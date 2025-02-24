#!/usr/bin/env python3

"""
Script:	jamf.py
Date:	2020-01-10
Platform: macOS/Linux
Description:
Jamf classes to manage and interact with the APIs
"""
__author__ = 'thedzy'
__copyright__ = 'Copyright 2020, thedzy'
__license__ = 'GPL'
__version__ = '2.0'
__maintainer__ = 'thedzy'
__email__ = 'thedzy@hotmail.com'
__status__ = 'Development'

import json
import re
import time
import warnings
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional, Union, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

import requests
import urllib3
import yaml


class AuthenticationError(Exception):
    """Raised when authentication to Jamf API fails."""
    pass


class SwaggerDocsError(Exception):
    """Raised when getting swagger data fails."""
    pass


class APIResponse:
    def __init__(self, success: bool = False, url: Optional[str] = None,
                 response: Optional[Union[str, Dict[str, Any]]] = None, http_code: int = 0,
                 err: Optional[str] = None, **kwargs: Any) -> None:
        """
        Initialisation
        """
        self.success: bool = kwargs.get('success', success)
        self.url: Optional[str] = kwargs.get('url', url)
        self.response: Optional[Union[str, Dict[str, Any]]] = kwargs.get('response', response)
        self.http_code: int = kwargs.get('http_code', http_code)
        self.err: Optional[str] = kwargs.get('err', err)
        self.data: Optional[Union[str, Dict[str, Any]]] = self.response
        self.json: dict
        self.is_json: bool
        self.json, self.is_json = self.get_json()

    def get_json(self) -> Tuple[Optional[Dict[str, Any]], bool]:
        """
        Convert json data to dict or return None
        :return: Dictionary values/None  and is converted successfully
        """
        is_json = False
        json_data = None
        try:
            json_data = json.loads(self.data)
            is_json = True
        except json.decoder.JSONDecodeError:
            try:
                root = ET.fromstring(self.data)
                json_data = {root.tag: {child.tag: child.text for child in root}}
                is_json = True
            except ET.ParseError as e:
                json_data = None

        return json_data, is_json

    def __str__(self) -> str:
        return str(self.data)

    def __repr__(self) -> str:
        return f'<APIResponse(success={self.success}, http_code={self.http_code}, url={self.url})>'


class Jamf:
    """
    Parent class for shared Jamf API logic.
    """

    def __init__(self, api_url: str, username: str, password: str,
                 timeout: float = 240.0, verify: bool = True,
                 disable_warnings: bool = False, return_format: str = 'json',
                 **kwargs: Any) -> None:
        """
        Shared initialization logic for Jamf classes.
        """
        self._logger = logging.getLogger(__name__)

        self._api_url: str = self._format_api_url(api_url)
        self._username: str = username
        self._password: str = password
        self._token_expiry = 0

        self._timeout: float = timeout
        self._verify: bool = verify
        self._disable_warnings: bool = disable_warnings
        self._return_format: str = return_format
        self._hide_deprecated: bool = kwargs.get('hide_deprecated', False)

        self._headers: Dict[str, str] = {}

        if self._return_format not in ('json', 'xml'):
            raise ValueError('return_format must be "json" or "xml"')

        # Configure session with retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=25)
        self._session: requests.Session = requests.Session()
        self._session.mount("https://", adapter)

        if self._disable_warnings:
            urllib3.disable_warnings()

        # Child classes should define these
        self._auth_base = ''
        self._base_path = ''
        self._auth_path = ''

        self._post_init()

    def _post_init(self):
        """
        Hook for subclasses to add extra initialization after the parent constructor.
        """
        pass

    def __del__(self) -> None:
        """
        Destructor for the class.
        """
        self.logout()

    def __enter__(self) -> 'JamfClassic':
        """
        Enter method for context management.

        Enables the use of 'with' statements, returning the class instance
        :return: The current class instance.
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Exit method for context management.
        :param exc_type: Exception type (if any).
        :param exc_val: Exception value (if any).
        :param exc_tb: Traceback object (if any).
        """
        self.logout()

    @property
    def timeout(self) -> int:
        """
        Get the timeout
        :return: timeout value
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        """
        Set the timeout
        :param: timeout
        """
        if timeout < 0:
            raise ValueError('Value cannot be negative.')
        self._timeout = float(timeout)

    @property
    def verify_ssl(self) -> bool:
        """
        Get the ssl validation
        :return: setting
        """
        return self._verify

    @verify_ssl.setter
    def verify_ssl(self, verify: bool) -> None:
        """
        Set the ssl validation
        :param: validation
        """
        if not isinstance(verify, bool):
            raise ValueError('Bool value expected.')
        self._verify = verify

    @staticmethod
    def disable_warnings() -> None:
        """
        Disable ssl warnings
        :return: None
        """
        urllib3.disable_warnings()

    @staticmethod
    def _format_api_url(url: str) -> str:
        """
        Reformat the api url so that it can tolerate innocents with / and missing http
        :return: Consistent api url
        """
        if not url.startswith('http'):
            url = f'https://{url}'
        return url.rstrip('/')

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """
        Convert str from camelCase to snake_case
        :return: Reformatted string
        """
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    def _authenticate(self) -> None:
        """
        Authenticate to the api if pass the expiry time
        :return: None
        """
        if self._token_expiry == 0 or 'Authorization' not in self._headers:
            auth_url = f'{self._api_url}{self._auth_base}{self._auth_path}'
            self._logger.debug(f'Authenticating to {auth_url}')

            response = requests.post(
                auth_url,
                auth=(self._username, self._password),
                headers={'Accept': 'application/json'},
                timeout=self._timeout,
                verify=self._verify
            )
            if response.status_code == 200:
                token = response.json().get('token')
                self._headers['Authorization'] = f'Bearer {token}'
                self._session.headers.update(self._headers)
                self._token_expiry = time.time() + (30 * 60)
            else:
                raise AuthenticationError(f'Authentication failed: {response.status_code} {response.text}')
        elif time.time() >= self._token_expiry:
            auth_url = f'{self._api_url}{self._auth_base}{self._auth_path}'.replace('/token', '/keep-alive')
            self._logger.debug(f'Authenticating to {auth_url}')

            response = requests.post(
                auth_url,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify
            )
            if response.status_code == 200:
                token = response.json().get('token')
                self._headers['Authorization'] = f'Bearer {token}'
                self._session.headers.update(self._headers)
                self._token_expiry = time.time() + (30 * 60)
            else:
                raise AuthenticationError(f'Authentication failed: {response.status_code} {response.text}')

    def logout(self):
        """
         De-authenticate
         :return: None
         """
        if 'Authorization' in self._headers:
            de_auth_url = f'{self._api_url}{self._auth_base}{self._auth_path}'.replace('/token', '/invalidate-token')
            response = self._session.post(
                de_auth_url,
                headers={
                    'Authorization': self._headers['Authorization'],
                    'Accept': '*/*'
                },
                timeout=self._timeout,
                verify=self._verify
            )
            if response.status_code != 204:
                raise AuthenticationError(f'De-Authentication failed: {response.status_code} {response.text}')

            self._logger.debug(f'De-authenticating to {de_auth_url}')
            _ = self._headers.pop('Authorization', None)

        self._username = None
        self._password = None

    def _load_api_methods(self) -> None:
        """
        For each endpoint in the swagger docs, create a method
        :return: None
        """
        swagger_dict = self._fetch_swagger_yaml()
        for path, methods in swagger_dict.get('paths', {}).items():
            for method, details in methods.items():
                if method.lower() in ('get', 'put', 'post', 'patch', 'delete'):
                    self._generate_method(path, method, details)


class JamfClassic(Jamf):
    """
    Always up-to-date, by pulling the swagger.yaml and generating the functions
    """

    def _post_init(self):
        """
        Extra initialization
        """

        self._headers = {
            'Accept': f'application/{self._return_format}',
            'Content-Type': 'application/xml',
            'User-Agent': 'lynx',
        }

        self._load_api_methods()

        self._auth_base = '/api'
        self._auth_path = '/v1/auth/token'

        self._authenticate()

    def _fetch_swagger_yaml(self) -> Dict[str, Any]:
        """
        Fetch the swagger docs from teh api url
        :return: Swagger defination
        """
        swagger_url = f'{self._api_url}/classicapi/doc/swagger.yaml'
        response = self._session.get(swagger_url)
        if response.status_code == 200:
            swagger_data = yaml.safe_load(response.text)
            self._base_path = swagger_data['basePath'].rstrip('/')
            return swagger_data
        raise SwaggerDocsError(f'Failed to fetch Swagger YAML: {response.status_code} {response.text}')

    def _generate_method(self, path: str, method: str, details: Dict[str, Any]) -> None:
        """
        Generate a function for each url path
        Create a doc string with parameters
        :param path: Path to the api endpoint
        :param method: Method (get, etc)
        :param details: All details of the end point,
        :return: None
        """
        operation_id = details.get('operationId', f'{method}_{path.replace("/", "_")}').replace('-', '_')
        operation_id = self._to_snake_case(operation_id)
        tag = details.get('tags', ['jamf'])[0]

        def api_method(*args: Any, **kwargs: Any) -> APIResponse:
            self._authenticate()
            try:
                url = f'{self._api_url}{self._base_path}{path}'.format_map(kwargs)
            except KeyError as err:
                raise ValueError(f'Missing parameter for URL: {err}')
            response = self._session.request(
                method.upper(),
                url,
                headers=self._headers,
                data=kwargs.get('data'),
                timeout=self._timeout,
                verify=self._verify
            )
            success = 200 <= response.status_code < 300
            return APIResponse(success, response.url, response.text, response.status_code)

        api_method._name__ = f'{tag}_{operation_id}'
        api_method._doc__ = f'{details.get("summary", "No description available.")}\n{self._api_url}JSSResource{path}\n'
        for param in details.get('parameters', []):
            api_method._doc__ += f':param {param["name"]}: {param.get("description", "")}\n'
        api_method._doc__ += ':return: API response'

        setattr(self, f'{tag}_{operation_id}', api_method)


class JamfUAPI(Jamf):
    """
    Always up-to-date, by pulling the swagger.json and generating the functions
    """

    def _post_init(self):
        """
        Extra initialization specific to JamfUAPI.
        """
        self._headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'lynx',
        }
        self._load_api_methods()

        self._auth_base = self._base_path

        self._authenticate()

    def _fetch_swagger_yaml(self) -> Dict[str, Any]:
        """
        Fetch the swagger docs from teh api url
        :return: Swagger defination
        """
        swagger_url = f'{self._api_url}/api/schema/'
        response = self._session.get(swagger_url)
        if response.status_code == 200:
            swagger_data = json.loads(response.text)
            self._base_path = swagger_data['servers'][0]['url']
            self._auth_path = next((security[key][0] for security in swagger_data['security'] for key in security if len(security[key]) > 0), None)
            return swagger_data
        raise SwaggerDocsError(f'Failed to fetch Swagger YAML: {response.status_code} {response.text}')

    def _generate_method(self, path: str, method: str, details: Dict[str, Any]) -> None:
        """
        Generate a function for each url path
        Create a doc string with parameters
        :param path: Path to the api endpoint
        :param method: Method (get, etc)
        :param details: All details of the end point,
        :return: None
        """

        # Use friendly names
        methods = {
            'post': 'create',
            'put': 'update'
        }
        # Get path parameters
        keys = re.findall(r'{([A-z]+)}', path)

        function_name = f'{methods.get(method, method)}{path.replace("/", "_").replace("-", "_")}'
        function_name = re.sub(r'(_*\{[A-z]+\})', '', function_name)
        function_name = self._to_snake_case(function_name)
        if len(keys) > 0:
            function_name += '_by_' + '_'.join(keys)

        tag = details.get('tags', ['jamf'])[0].replace("-", "_")

        def api_method(*args: Any, **kwargs: Any) -> APIResponse:
            self._authenticate()
            if details.get('deprecated', False):
                deprecation_date = details.get('x-deprecation-date', 'Unknown date')
                warnings.warn(
                    f'⚠️ WARNING: The endpoint `{function_name}` is DEPRECATED as of {deprecation_date}.',
                    DeprecationWarning,
                    stacklevel=2
                )

            try:
                url = f'{self._api_url}{self._base_path}{path}'.format_map(kwargs)
            except KeyError as err:
                raise ValueError(f'Missing parameter for URL: {err}')

            # Get optional params, passed as keywords
            params = kwargs.copy()
            for key in keys:
                params.pop(key, None)
            params.pop('data', None)

            response = self._session.request(
                method.upper(),
                url,
                params=params,
                headers=self._headers,
                json=kwargs.get('data'),
                timeout=self._timeout,
                verify=self._verify
            )
            success = 200 <= response.status_code < 300
            return APIResponse(success, response.url, response.text, response.status_code)

        api_method._name__ = function_name
        api_method._doc__ = f'{details.get("summary", "No description available.")}\n'
        api_method._doc__ += f'{self._api_url}{self._base_path}{path}\n'
        api_method._doc__ += f'Requires permissions: {",".join(details.get("x-required-privileges", []))}\n'
        for param in details.get('parameters', []):
            if 'name' in param:
                api_method._doc__ += f':param {param["name"]}: {param.get("description", "")}\n'
        api_method._doc__ += ':return: API response'

        if not self._hide_deprecated or not details.get('deprecated', False):
            setattr(self, f'{tag}_{function_name}', api_method)
