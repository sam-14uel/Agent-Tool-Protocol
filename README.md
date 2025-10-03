# Agent Tool Protocol(ATP)

<p align="center">
  <img src="https://github.com/sam-14uel/Agent-Tool-Protocol/raw/main/assets/atp.png" alt="ATP Logo" />
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
from atp_sdk.clients import ToolKitClient
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
- `auth_type`: Auth type (e.g., "OAuth2", "apiKey"), or `None`.
- `auth_with`: Name of the token parameter (e.g., "access_token", "api_key"), or `None`.

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
    params=[],
    required_params=[],
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

### Tool with API Key

```python
@client.register_tool(
    function_name="get_contacts",
    params=[],
    required_params=[],
    description="Fetches contacts from HubSpot.",
    auth_provider="hubspot", auth_type="apiKey", auth_with="api_key"
)
def get_contacts(**kwargs):
    access_token = kwargs.get('auth_token')
    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()
```


---

## Class: LLMClient
The `LLMClient` lets you connect to the ATP Agent Server, retrieve toolkit context, and execute tools or workflows using JSON payloads—perfect for LLM-based agents.

### Constructor
```python
from atp_sdk.clients import LLMClient

llm_client = LLMClient(
    api_key="YOUR_ATP_API_KEY",
    protocol="ws",  # or "http"
    base_url="https://chatatp-backend.onrender.com/ws/v1/atp/llm-client/"
)
```
**Parameters:**
- `api_key` (str): Your ATP API key.
- `protocol` (str, optional): Protocol to use ("ws" or "http"). Defaults to "ws".
- `base_url` (str, optional): ATP server URL. Defaults to `https://chatatp-backend.onrender.com/ws/v1/atp/llm-client/`.

---

### get_toolkit_context
Retrieves the toolkit context and system instructions for a given toolkit and user prompt.
```python
context = llm_client.get_toolkit_context(
    toolkit_id="your_toolkit_id",
    provider="openai",  # or "anthropic" or "mistralai"
    user_prompt="What do you want to achieve?"
)
```
**Returns:**
A dictionary containing the toolkit context, including provider-specific tool schemas.

---

### call_tool
Executes a tool or workflow on the ATP server.
```python
response = llm_client.call_tool(
    toolkit_id="your_toolkit_id",
    json_response='{"function": "hello_world", "parameters": {"name": "Alice"}}',
    provider="openai",  # or "anthropic" or "mistralai"
    user_prompt="Say hello to Alice."
)
print(response)
```
**Arguments:**
- `toolkit_id`: Unique ID of the toolkit.
- `json_response`: JSON payload from an LLM containing the tool call.
- `provider`: The LLM provider (e.g., "openai", "anthropic", "mistralai").
- `user_prompt`: Additional user input to include in the execution.

---

## OAuth2 Integration & Token Handling

The ATP SDK supports secure OAuth2 flows for tools that require third-party authentication (e.g., HubSpot, Google, Salesforce).

**How it works:**
- Use `LLMClient.initiate_oauth_connection()` to start the OAuth flow and get an authorization URL for the user.
- Use `LLMClient.wait_for_connection()` to poll for completion and retrieve the integration ID.
- Use `LLMClient.get_user_tokens()` to fetch the user's access and refresh tokens for use in tool calls.

**Example:**
```python
from atp_sdk.clients import LLMClient

llm_client = LLMClient(api_key="YOUR_ATP_API_KEY")

# Step 1: Initiate OAuth connection
connection = llm_client.initiate_oauth_connection(
    platform_id="PLATFORM_ID",
    external_user_id="user@example.com",
    developer_redirect_url="https://your-app.com/oauth/callback"
)
print("Authorize at:", connection["authorization_url"])

# Step 2: Wait for connection
account = llm_client.wait_for_connection(
    platform_id="PLATFORM_ID",
    external_user_id="user@example.com"
)
print("Integration ID:", account["integration_id"])

# Step 3: Fetch tokens
tokens = llm_client.get_user_tokens(
    platform_id="PLATFORM_ID",
    external_user_id="user@example.com"
)
print("Access token:", tokens["access_token"])
```

**Note:**  
- You only need to handle OAuth and fetch tokens; the SDK will automatically inject tokens into tool calls as needed.
- See the [LLMClient](#class-llmclient) section for more details.

---

## Request/Response Flow

### **1. LLM Requests Toolkit Context**
- The LLM (OpenAI, Anthropic, or Mistral) sends a request to the ATP server to get the toolkit context.
- The ATP server responds with a list of available tools and their schemas.

**Request:**
```json
{
  "type": "get_toolkit_context",
  "toolkit_id": "your_toolkit_id",
  "request_id": "uuid",
  "provider": "openai",
  "user_prompt": "What do you want to achieve?"
}
```

**Response:**
```json
{
  "type": "toolkit_context",
  "request_id": "uuid",
  "payload": {
    "toolkit_id": "your_toolkit_id",
    "toolkit_name": "Example Toolkit",
    "caption": "Example Caption",
    "provider": "openai",
    "tools": [
      {
        "type": "function",
        "name": "hello_world",
        "description": "Returns a greeting.",
        "parameters": {
          "type": "object",
          "properties": {
            "name": {"type": "string", "description": "Name to greet"}
          },
          "required": ["name"]
        }
      }
    ],
    "user_prompt": "What do you want to achieve?"
  }
}
```

---

### **2. LLM Generates Tool Calls**
- The LLM uses the toolkit context to generate tool calls.
- The LLM sends the tool calls to the ATP server for execution.

**Request:**
```json
{
  "type": "task_request",
  "toolkit_id": "your_toolkit_id",
  "request_id": "uuid",
  "payload": {
    "function": "hello_world",
    "parameters": {"name": "Alice"}
  },
  "provider": "openai",
  "user_prompt": "Say hello to Alice."
}
```

---

### **3. ATP Server Executes Tool**
- The ATP server receives the tool call and executes the corresponding tool.
- The ATP server sends the tool's response back to the LLM.

**Response:**
```json
{
  "type": "task_response",
  "request_id": "uuid",
  "payload": {
    "result": {"message": "Hello, Alice!"}
  }
}
```

---

## Using LLMClient with OpenAI, Anthropic, and Mistral AI

### OpenAI
```python
import openai
from atp_sdk.clients import LLMClient

openai_client = openai.OpenAI(api_key="YOUR_OPENAI_API_KEY")
llm_client = LLMClient(api_key="YOUR_ATP_API_KEY")

# Get toolkit context
context = llm_client.get_toolkit_context(
    toolkit_id="your_toolkit_id",
    provider="openai",
    user_prompt="Create a company and then list contacts."
)

# Use OpenAI to generate tool calls
response = openai_client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Create a company and then list contacts."}
    ],
    tools=context["tools"],
    tool_choice="auto"
)

# Extract tool calls
tool_calls = response.choices[0].message.tool_calls

# Loop through tool calls and execute each one
for tool_call in tool_calls:
    tool_call_json = {
        "function": tool_call.function.name,
        "parameters": tool_call.function.arguments
    }

    result = llm_client.call_tool(
        toolkit_id="your_toolkit_id",
        json_response=tool_call_json,
        provider="openai",
        user_prompt="Create a company and then list contacts."
    )

    print(f"Tool call result: {result}")
```

---

### Anthropic
```python
import anthropic
from atp_sdk.clients import LLMClient

anthropic_client = anthropic.Anthropic(api_key="YOUR_ANTHROPIC_API_KEY")
llm_client = LLMClient(api_key="YOUR_ATP_API_KEY")

# Get toolkit context
context = llm_client.get_toolkit_context(
    toolkit_id="your_toolkit_id",
    provider="anthropic",
    user_prompt="Create a company and then list contacts."
)

# Use Anthropic to generate tool calls
response = anthropic_client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Create a company and then list contacts."}
    ],
    tools=context["tools"]
)

# Extract tool calls
tool_calls = response.content

# Loop through tool calls and execute each one
for tool_call in tool_calls:
    tool_call_json = {
        "function": tool_call.name,
        "parameters": tool_call.input
    }

    result = llm_client.call_tool(
        toolkit_id="your_toolkit_id",
        json_response=tool_call_json,
        provider="anthropic",
        user_prompt="Create a company and then list contacts."
    )

    print(f"Tool call result: {result}")
```

---

### Mistral AI
```python
from mistralai.client import MistralClient
from atp_sdk.clients import LLMClient

mistral_client = MistralClient(api_key="YOUR_MISTRAL_API_KEY")
llm_client = LLMClient(api_key="YOUR_ATP_API_KEY")

# Get toolkit context
context = llm_client.get_toolkit_context(
    toolkit_id="your_toolkit_id",
    provider="mistralai",
    user_prompt="Create a company and then list contacts."
)

# Use Mistral to generate tool calls
response = mistral_client.chat(
    model="mistral-large-latest",
    messages=[{"role": "user", "content": "Create a company and then list contacts."}],
    tools=context["tools"]
)

# Extract tool calls
tool_calls = response.choices[0].message.tool_calls

# Loop through tool calls and execute each one
for tool_call in tool_calls:
    tool_call_json = {
        "function": tool_call.function.name,
        "parameters": tool_call.function.arguments
    }

    result = llm_client.call_tool(
        toolkit_id="your_toolkit_id",
        json_response=tool_call_json,
        provider="mistralai",
        user_prompt="Create a company and then list contacts."
    )

    print(f"Tool call result: {result}")
```

---

## Handling Multi-Step Tool Calls
When the LLM generates multiple tool calls, loop through them and execute each one sequentially:

```python
# Loop through tool calls and execute each one
for tool_call in tool_calls:
    tool_call_json = {
        "function": tool_call.function.name,
        "parameters": tool_call.function.arguments
    }

    result = llm_client.call_tool(
        toolkit_id="your_toolkit_id",
        json_response=tool_call_json,
        provider="openai",  # or "anthropic" or "mistralai"
        user_prompt="Create a company and then list contacts."
    )

    print(f"Tool call result: {result}")
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

---

## Framework Integration: Django, FastAPI, and Flask

### Django

**How to use:**
1. Install:  
   `pip install AgentToolProtocol django`
2. Add `"django_atp"` to `INSTALLED_APPS` in your `settings.py`.
3. Include `path("", include("django_atp.urls"))` in your project `urls.py`.
4. Register your toolkits and tools in a module in your app (e.g. `myapp/atp_tools.py`), and import this module in your app’s `apps.py` `ready()` method to ensure registration at startup:
   ```python
   # myapp/apps.py
   from django.apps import AppConfig
   class MyAppConfig(AppConfig):
       name = "myapp"
       def ready(self):
           import myapp.atp_tools
   ```
5. Each registered tool is exposed at `/atp/<toolkit_name>/<tool_name>/` (GET for context, POST payload of parameters for execution).
6. Visit `/atp/<toolkit_name>/` for toolkit details and a list of tools.

---

### FastAPI

**How to use:**
1. Install:  
   `pip install AgentToolProtocol fastapi uvicorn`
2. Register your toolkits and tools in a module (e.g. `atp_tools.py`), and import it in your FastAPI app before starting.
3. Example endpoints:
   ```python
   from fastapi import FastAPI, Request
   from fastapi.responses import JSONResponse
   from fastapi_atp.registry import get_client
   import atp_tools  # Ensure toolkit registration

   app = FastAPI()

   @app.get("/atp/{toolkit_name}/{tool_name}/")
   async def get_tool(toolkit_name: str, tool_name: str):
       client = get_client(toolkit_name)
       if not client:
           return JSONResponse({"error": "Toolkit not found"}, status_code=404)
       tool = client.registered_tools.get(tool_name)
       if not tool:
           return JSONResponse({"error": "Tool not found"}, status_code=404)
       return JSONResponse(tool)

   @app.post("/atp/{toolkit_name}/{tool_name}/")
   async def post_tool(toolkit_name: str, tool_name: str, request: Request):
       client = get_client(toolkit_name)
       if not client:
           return JSONResponse({"error": "Toolkit not found"}, status_code=404)
       tool = client.registered_tools.get(tool_name)
       if not tool:
           return JSONResponse({"error": "Tool not found"}, status_code=404)
       params = await request.json()
       result = tool["function"](**params)
       return JSONResponse({"result": result})

   @app.get("/atp/{toolkit_name}/")
   async def get_toolkit(toolkit_name: str):
       client = get_client(toolkit_name)
       if not client:
           return JSONResponse({"error": "Toolkit not found"}, status_code=404)
       tools = list(client.registered_tools.keys())
       return JSONResponse({"toolkit": toolkit_name, "tools": tools})
   ```
4. Run your fastAPI app with:  
   `uvicorn your_app_module:app --reload`

5. Visit `/atp/<toolkit_name>/` for toolkit details and a list of tools.

6. Visit `/atp/<toolkit_name>/<tool_name>/` for tool details.

---

### Flask

**How to use:**
1. Install:  
   `pip install AgentToolProtocol flask`
2. Register your toolkits and tools in a module (e.g. `atp_tools.py`), and import it in your Flask app before starting.
3. Example endpoints:
   ```python
   from flask import Flask, request, jsonify
   from django_atp.registry import get_client
   import atp_tools  # Ensure toolkit registration

   app = Flask(__name__)

   @app.route("/atp/<toolkit_name>/<tool_name>/", methods=["GET", "POST"])
   def tool_endpoint(toolkit_name, tool_name):
       client = get_client(toolkit_name)
       if not client:
           return jsonify({"error": "Toolkit not found"}), 404
       tool = client.registered_tools.get(tool_name)
       if not tool:
           return jsonify({"error": "Tool not found"}), 404
       if request.method == "GET":
           return jsonify(tool)
       params = request.json if request.is_json else request.form.to_dict()
       result = tool["function"](**params)
       return jsonify({"result": result})

   @app.route("/atp/<toolkit_name>/", methods=["GET"])
   def toolkit_endpoint(toolkit_name):
       client = get_client(toolkit_name)
       if not client:
           return jsonify({"error": "Toolkit not found"}), 404
       tools = list(client.registered_tools.keys())
       return jsonify({"toolkit": toolkit_name, "tools": tools})

   if __name__ == "__main__":
       app.run(debug=True)
   ```

4. Run your Flask app with:  
   `python your_flask_app.py`

5. Visit `/atp/<toolkit_name>/` for toolkit details and a list of tools.

6. Visit `/atp/<toolkit_name>/<tool_name>/` for tool details.


# Example atp_tools.py for Flask/FastAPI/Django

```python
from atp_sdk.clients import ToolKitClient
from django_atp.registry import register_client  # For Django
from fastapi_atp.registry import register_client  # For FastAPI
from flask_atp.registry import register_client  # For Flask

# Initialize the client
client = ToolKitClient(
    api_key="YOUR_ATP_API_KEY",
    app_name="<your_toolkit_name>"
)

# Register the client (Django/FastAPI/Flask)
register_client("<your_toolkit_name>", client)

# Define and register tools the usual way but this time no need to call start() at the end of the file
@client.register_tool(
    function_name="hello_world",
    params=['name'],
    required_params=['name'],
    description="Returns a greeting.",
    auth_provider=None, auth_type=None, auth_with=None
)
def hello_world(name):
    return f"Hello, {name}!"
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