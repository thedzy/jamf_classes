
# Jamf API Classes
## _class_ JamfClassic
### An interface to the classic API
------
JamfClassic interacts with the classic API of Jamf

Usage:
```python
api = jamf.JamfClassic(url, username, password, timeout=180, verify=True, disable_warnings=False)
# Accessing .../JSSResource/computers/id/100
api_data = api.get_data('computers', 'id', 100)
if api_data.success:
    print(api_data.data)
```
or
```python
jamf.JamfClassic(url, username, password, timeout=180, verify=True, disable_warnings=False) as api:
    # Accessing .../JSSResource/computers/id/100
    api_data = api.get_data('computers', 'id', 100)
    if api_data.success:
        print(api_data.data)
```
_See: example.py_



```python

class JamfClassic:
    """
    JamfClassic interacts with the classic API of Jamf
    """

    def __init__(self, api_url, username, password, *args, **kwargs):
        """
        Initialisation method
        :param api_url: (str) url of the api
        :param username: (str) username
        :param password: (str) password
        :param kwargs: (dict) timeout, verify, disable_warnings
        """

    def timeout(self, timeout=None):
        """
        Set or retrieve the timeout
        :param timeout: (int) new value or (None) to remain
        :return: (int) Current/new setting
        """

    def verify_ssl(self, verify=None):
        """
        Set or retrieve whether to verify teh SSL certificate
        :param verify: (bool) new value or (None) to remain
        :return: (bool) Current/new setting
        """

    @staticmethod
    def disable_warnings():
        """
        Disable warnings for ssl verify
        Making unverified HTTPS requests is strongly discouraged, however,
        if you understand the risks and wish to disable these warnings, you can use disable_warnings()
        :return: (void)
        """

    def get_data(self, *objects, **kwargs):
        """
        GET from the api
        :param objects: (list) of objects ex. /JSSResource/computer/id/0 = ['computer', 'id', 0]
        :param kwargs: None
        :return:
        """

    def del_data(self, *objects, **kwargs):
        """
        DELETE to the api
        :param objects: (list) of objects ex. /JSSResource/computer/id/0 = ['computer', 'id', 0]
        :param kwargs: None
        :return:
        """

    def put_data(self, data, *objects, **kwargs):
        """
        PUT to the api
        :param data: (dict) data to post
        :param objects: (list) of objects ex. /JSSResource/computer/id/0 = ['computer', 'id', 0]
        :param kwargs: None
        :return:
        """

    def post_data(self, data, *objects, **kwargs):
        """
        POST to the api
        :param data: (dict) data to post
        :param objects: (list) of objects ex. /JSSResource/computer/id/0 = ['computer', 'id', 0]
        :param kwargs: None
        :return:
        """
```

## _class_ JamfUAPI
### An interface to the universal API
------
JamfUAPI interacts with the universal API of Jamf

Usage:
```python
api = jamf.JamfUAPI(url, username, password, timeout=180, verify=True, disable_warnings=False)
# Accessing .../upai/v1/scripts/id/100
api_data = api.get_data('v', 'scripts', 'id', 100)
if api_data.success:
    print(api_data.data['results'])
```
or
```python
with jamf.JamfUAPI(url, username, password, timeout=180, verify=True, disable_warnings=False) as api:
    # Accessing .../upai/v1/scripts/id/100
    api_data = api.get_data('v', 'scripts', 'id', 100)
    if api_data.success:
        print(api_data.data['results'])
```
_See: example.py_

```python
class JamfUAPI:
    """
    JAMFUAPI interacts with the universal API of Jamf
    """

    def __init__(self, api_url, username, password, *args, **kwargs):
        """
        Initialisation method
        :param api_url: (str) url of the api
        :param username: (str) username
        :param password: (str) password
        :param args: (list)
        :param kwargs: (dict) timeout, verify, disable_warnings
        """

    def renew_token(self):
        """
        Renew the login token
        :return: (APIResponse)
        """

    def timeout(self, timeout=None):
        """
        Set or retrieve the timeout
        :param timeout: (int) new value or (None) to remain
        :return: (int) Current/new setting
        """

    def verify_ssl(self, verify=None):
        """
        Set or retrieve whether to verify teh SSL certificate
        :param verify: (bool) new value or (None) to remain
        :return: (bool) Current/new setting
        """

    @staticmethod
    def disable_warnings():
        """
        Disable warnings for ssl verify
        Making unverified HTTPS requests is strongly discouraged, however,
        if you understand the risks and wish to disable these warnings, you can use disable_warnings()
        :return: (bool) Current/new setting
        """

    def get_login(self):
        """
        Get login information
        :return: (APIResponse)
        """

    def get_data(self, *objects, **kwargs):
        """
        GET from the api
        :param objects: (list) of objects ex. /uapi/computer/id/0 = ['computer', 'id', 0]
        :param kwargs: (dict) options ex: sort=asc
        :return: (APIResponse)
        """

    def del_data(self, *objects, **kwargs):
        """
        DELETE from the api
        :param objects: (list) of objects ex. /uapi/computer/id/0 = ['computer', 'id', 0]
        :param kwargs: (dict) options ex: sort=asc
        :return: (APIResponse)
        """

    def put_data(self, data, *objects, **kwargs):
        """
        PUT to the api
        :param data: (dict) data to post
        :param objects: (list) of objects ex. /uapi/computer/id/0 = ['computer', 'id', 0]
        :param kwargs: (dict) options ex: sort=asc
        :return: (APIResponse)
        """

    def post_data(self, data, *objects, **kwargs):
        """
        POST to the api
        :param data: (dict) data to post
        :param objects: (list) of objects ex. /uapi/computer/id/0 = ['computer', 'id', 0]
        :param kwargs: (dict) options ex: sort=asc
        :return: (APIResponse)
        """

```

## _class_ APIResponse
### The response returned from the JamfClassic and JamfUAPI Classes
------
APIResponse contains the url, response, http code and error of the request

_Interaction with this class is done with the data returned.  See: example.py_

```python
class APIResponse:
    """
    Data object containing data of the query
    :property success: (bool) success of the call
    :property url: (str) url that was called
    :property response: (str, json) depending on the success
    :property http_code: (int) http code returned
    :property err: (str) Error if exception
    """

    def success(self, success=None):
        """
        :param success: Set or retrieve property success
        :return: (bool) Current/new setting
        """

    def response(self, response=None):
        """
        :param response: Set or retrieve property response
        :return: (int) Current/new setting
        """

    def http_code(self, http_code=None):
        """
        :param http_code: Set or retrieve property http_code
        :return: (int) Current/new setting
        """

    def err(self, err=None):
        """
        :param err: Set or retrieve property err
        :return: (int) Current/new setting
        """
```
