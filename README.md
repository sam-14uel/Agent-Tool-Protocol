# Agent Tool Protocol(ATP)

<p align="center">
  <img src="assets/atp.png" alt="ATP Logo" />
</p>

<p align="center">
  <strong>
  A Python SDK for registering, exposing, and serving your own Python functions as tools via the ATP platform.
  Supports secure OAuth2 flows, dynamic tool registration, and real-time tool invocation via WebSocket.
  </strong>
</p>


---

## Table of Contents

- Installation
- Quick Start
- Class: ToolKitClient
  - Constructor
  - register_tool
  - start
  - stop
- Tool Function Requirements
- WebSocket Events
- Error Handling
- Examples
- Advanced Usage
- License

---

## Installation

```sh
pip install AgentToolProtocol
```

---

## Quick Start

```python
from atp_sdk.atp_sdk.clients import ToolKitClient
import requests

client = ToolKitClient(
    api_key="YOUR_ATP_API_KEY",
    app_name="my_app"
)

@client.register_tool(
    function_name="hello_world",
    params=['name'],
    required_params=['name'],
    description="Returns a greeting.",
    auth_provider=None, auth_type=None, auth_with=None
)
def hello_world(**kwargs):
    return {"message": f"Hello, {kwargs.get('name', 'World')}!"}

client.start()
```

---

## Class: ToolKitClient

### Constructor

```python
ToolKitClient(
    api_key: str,
    app_name: str,
    base_url: str = "https://chatatp-backend.onrender.com"
)
```

**Parameters:**
- `api_key` (str): Your ATP API key.
- `app_name` (str): Name of your application.
- `base_url` (str, optional): ATP Server backend URL. Defaults to chatatp-backend.onrender.com.

---

### register_tool

Registers a Python function as a tool with the ATP platform.

```python
@client.register_tool(
    function_name: str,
    params: list[str],
    required_params: list[str],
    description: str,
    auth_provider: Optional[str],
    auth_type: Optional[str],
    auth_with: Optional[str]
)
def my_tool(**kwargs):
    ...
```

**Arguments:**
- `function_name`: Unique name for the tool.
- `params`: List of all parameter names.
- `required_params`: List of required parameter names.
- `description`: Human-readable description.
- `auth_provider`: Name of OAuth2 provider (e.g., "hubspot", "google"), or `None`.
- `auth_type`: Auth type (e.g., "OAuth2"), or `None`.
- `auth_with`: Name of the token parameter (e.g., "access_token"), or `None`.

**Returns:**  
A decorator to wrap your function.

**Example:**

```python
@client.register_tool(
    function_name="create_company",
    params=['name', 'domain', 'industry'],
    required_params=['name', 'domain', 'industry'],
    description="Creates a company in HubSpot.",
    auth_provider="hubspot", auth_type="OAuth2", auth_with="access_token"
)
def create_company(**kwargs):
    access_token = kwargs.get('auth_token')
    url = "https://api.hubapi.com/crm/v3/objects/companies"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    data = {"properties": {
        "name": kwargs.get('name'),
        "domain": kwargs.get('domain'),
        "industry": kwargs.get('industry')
    }}
    response = requests.post(url, json=data, headers=headers)
    return response.json()
```

---

### start

Starts the WebSocket client and begins listening for tool requests.

```python
client.start()
```

- Keeps the main thread alive.
- Handles reconnections automatically.

---

### stop

Stops the WebSocket client and closes the connection.

```python
client.stop()
```

---

## Tool Function Requirements

- Must accept all parameters as `**kwargs`.
- If your tool requires authentication, expect `auth_token` in `kwargs`.
- Return a serializable object (dict, str, etc).

---

## WebSocket Events

### Tool Registration

Upon registration, your tool is announced to the ATP backend and available for invocation.

### Tool Invocation

When a tool request is received, your function is called with the provided parameters and (if needed) `auth_token`.

**Example incoming message:**
```json
{
  "message_type": "atp_tool_request",
  "payload": {
    "request_id": "uuid",
    "tool_name": "create_company",
    "params": {"name": "Acme", "domain": "acme.com", "industry": "Tech"},
    "auth_token": "ACCESS_TOKEN"
  }
}
```

---

## Error Handling

- If your function raises an exception, the error is caught and returned as:
  ```json
  {"error": "Error message"}
  ```
- If required parameters are missing, an error is returned.
- If `auth_token` is required but missing, an error is returned.

---

## Examples

### Minimal Tool

```python
@client.register_tool(
    function_name="echo",
    params=['text'],
    required_params=['text'],
    description="Echoes the input text.",
    auth_provider=None, auth_type=None, auth_with=None
)
def echo(**kwargs):
    return {"echo": kwargs.get('text')}
```

### Tool with OAuth2

```python
@client.register_tool(
    function_name="get_contacts",
    params=['auth_token'],
    required_params=['auth_token'],
    description="Fetches contacts from HubSpot.",
    auth_provider="hubspot", auth_type="OAuth2", auth_with="access_token"
)
def get_contacts(**kwargs):
    access_token = kwargs.get('auth_token')
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()
```

---

## Advanced Usage

### Custom Backend

```python
client = ToolKitClient(
    api_key="YOUR_API_KEY",
    app_name="my_app",
    base_url="https://your-backend.example.com"
)
```

### Multiple Tools

```python
@client.register_tool(...)
def tool1(**kwargs): ...

@client.register_tool(...)
def tool2(**kwargs): ...
```

### Keeping the Main Thread Alive

```python
client.start()
try:
    while True:
        import time; time.sleep(1)
except KeyboardInterrupt:
    client.stop()
```

---

## License

MIT License.  
See LICENSE for details.

---

## Feedback & Issues

For bug reports or feature requests, please open an issue on [GitHub](https://github.com/sam-14uel/Agent-Tool-Protocol).

---

**Happy coding! 🚀**