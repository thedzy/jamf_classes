# Jamf API Classes (classic and Universal API)

## _class_ JamfClassic

### An interface to the classic API
------
JamfClassic interacts with the classic API of Jamf

Functions are pulled from the swagger documentation at initialisation Usage:

```python
api = jamf.JamfClassic(url, username, password, timeout=180, verify=True, disable_warnings=False)
# Accessing .../JSSResource/computers/id/100
api_data = api.computers_find_computers_by_id(id=100)
if api_data.success:
    print(api_data.json)
```

or

```python
with jamf.JamfClassic(url, username, password, timeout=180, verify=True, disable_warnings=False) as api:
    # Accessing .../JSSResource/computers/id/100
    api_data = api.computers_find_computers_by_id(id=100)
    if api_data.success:
        print(api_data.json)
```

_See: example.py_

Because methods are dynamically generated they will be current to your run time and cannot be listed here.

## _class_ JamfUAPI

### An interface to the universal API
------
JamfUAPI interacts with the universal API of Jamf

Usage:

```python
api = jamf.JamfUAPI(url, username, password, timeout=180, verify=True, disable_warnings=False)
# Accessing .../upai/v1/scripts/id/100
api_data = api.departments_get_v1_departments_by_id(id=100)
if api_data.success:
    print(api_data.json['results'])
```

or

```python
with jamf.JamfUAPI(url, username, password, timeout=180, verify=True, disable_warnings=False) as api:
    # Accessing .../upai/v1/scripts/id/100
    api_data = api.departments_get_v1_departments_by_id(id=100)
    if api_data.success:
        print(api_data.json['results'])
```

_See: example.py_

Because methods are dynamically generated they will be current to your run time and cannot be listed here.

## _class_ APIResponse

### The response returned from the JamfClassic and JamfUAPI Classes
------
APIResponse contains the url, response, http code and error of the request

_Interaction with this class is done with the data returned. See: example.py_

Usage:

```python
from api_response import APIResponse

response = APIResponse(success=True, url='https://example.com', response='{"key": "value"}', http_code=200)

print(response)  # Raw response string
print(response.json)  # Parsed JSON (if available)
print(response.success)  # True if HTTP code is 2xx
```

### Attributes

| Attribute   | Type                             | Description                             |
|-------------|----------------------------------|-----------------------------------------|
| `success`   | `bool`                            | Indicates if the request was successful. |
| `url`       | `Optional[str]`                   | The URL that was called.                |
| `response`  | `Optional[str, Dict[str, Any]]`   | Raw response data.                      |
| `http_code` | `int`                             | HTTP status code returned.              |
| `err`       | `Optional[str]`                   | Error message if an exception occurred. |
| `json`      | `Optional[Dict[str, Any]]`        | Parsed response as JSON or XML.         |
| `is_json`   | `bool`                            | Indicates if the response is valid JSON.|

## Why?

For easy interaction with the jamf api, abstracting the calls and data returned

## Improvements?

- Would like to remove v1, v2, etc and just use most recent, or have a generic call to the most recent.  Challenges, will be changes in the return data and unexpected results.  Don't think the juice is worth the squeeze.

## State?

No known bugs. But I no longer have access to a full Jamf instance to do thorough testing.

## New

### 1.0

- Used get_data, post_data, etc. to call the api and did very little to abstract the api urls

### 2.0

- Each api call now has its own function and pulled dynamically from teh swagger documentation from your instance of the
api.
- Removed things that were done inefficiently because I didn't know better at the time
- Better alignment with Classic and UAPI
- Which allows netter use of a parent class
