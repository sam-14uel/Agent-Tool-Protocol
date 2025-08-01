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
    api_key="YOUR_ATP_API_KEY"
)
```

---

### get_toolkit_context

Retrieves the toolkit context and system instructions for a given toolkit and user prompt.

```python
context = llm_client.get_toolkit_context(
    toolkit_id="your_toolkit_id",
    user_prompt="What do you want to achieve?"
)
```

---

### call_tool

Executes a tool or workflow on the ATP server.

```python
response = llm_client.call_tool(
    toolkit_id="your_toolkit_id",
    json_response=json.dumps({
        "function": "hello_world",
        "parameters": {"name": "Alice"},
        "task_title": "Say hello",
        "execution_type": "remote"
    })
)
print(response)
```

---

## Example: Using LLMClient with OpenAI, Anthropic, and Mistral AI

You can use any LLM to generate the JSON workflow, then execute each step with `LLMClient`.

### 1. OpenAI (GPT-4o)

```python
import openai
from atp_sdk.clients import LLMClient

client = openai.OpenAI(api_key="YOUR_OPENAI_API_KEY")
llm_client = LLMClient(api_key="YOUR_ATP_API_KEY")

# Get toolkit context and system prompt
context = llm_client.get_toolkit_context(toolkit_id="your_toolkit_id", user_prompt="Create a company and then list contacts.")

# Use OpenAI to generate the workflow JSON
response = client.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": context},
        {"role": "user", "content": "Create a company and then list contacts."}
    ]
)
workflow_json = response.choices[0].message.content

# Parse and execute each workflow step
import json
workflow = json.loads(workflow_json)
if "workflows" in workflow:
    results = []
    for step in workflow["workflows"]:
        result = llm_client.call_tool(
            toolkit_id="your_toolkit_id",
            json_response=json.dumps(step)
        )
        results.append(result)
else:
    result = llm_client.call_tool(
        toolkit_id="your_toolkit_id",
        json_response=workflow_json
    )
```

### 2. Anthropic (Claude)

```python
import anthropic
from atp_sdk.clients import LLMClient

llm_client = LLMClient(api_key="YOUR_ATP_API_KEY")
context = llm_client.get_toolkit_context(toolkit_id="your_toolkit_id", user_prompt="...")

client = anthropic.Anthropic(api_key="YOUR_ANTHROPIC_API_KEY")
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": context}
    ]
)
workflow_json = response.content[0].text

# Execute as above
```

### 3. Mistral AI

```python
from mistralai.client import MistralClient
from atp_sdk.clients import LLMClient

llm_client = LLMClient(api_key="YOUR_ATP_API_KEY")
context = llm_client.get_toolkit_context(toolkit_id="your_toolkit_id", user_prompt="...")

client = MistralClient(api_key="YOUR_MISTRAL_API_KEY")
response = client.chat(
    model="mistral-large-latest",
    messages=[{"role": "user", "content": context}]
)
workflow_json = response.choices[0].message.content

# Execute as above
```

---

## Handling Multi-Step Workflows

When the LLM returns a workflow with multiple steps:

```python
import json

workflow = json.loads(workflow_json)
if "workflows" in workflow:
    results = []
    for step in workflow["workflows"]:
        result = llm_client.call_tool(
            toolkit_id="your_toolkit_id",
            json_response=json.dumps(step)
        )
        results.append(result)
else:
    result = llm_client.call_tool(
        toolkit_id="your_toolkit_id",
        json_response=workflow_json
    )
```

- For each step, call `llm_client.call_toolkit` with the step JSON.
- Collect and process results as needed.
- If a step has `"depends_on"`, you can pass outputs from previous steps as needed.

---

## Example: Full Workflow

```python
from atp_sdk.clients import LLMClient
import openai
import json

llm_client = LLMClient(api_key="YOUR_ATP_API_KEY")
context = llm_client.get_toolkit_context(toolkit_id="your_toolkit_id", user_prompt="...")

response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": context},
        {"role": "user", "content": "Do a multi-step task."}
    ]
)
workflow_json = response.choices[0].message.content
workflow = json.loads(workflow_json)

results = []
if "workflows" in workflow:
    for step in workflow["workflows"]:
        result = llm_client.call_tool(
            toolkit_id="your_toolkit_id",
            json_response=json.dumps(step)
        )
        results.append(result)
else:
    result = llm_client.call_tool(
        toolkit_id="your_toolkit_id",
        json_response=workflow_json
    )
    results.append(result)

print(results)
```

---

**Tip:**  
Always ensure the LLM returns valid JSON as described in the toolkit context instructions.

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

## License

MIT License.  
See LICENSE for details.

---

## Feedback & Issues

For bug reports or feature requests, please open an issue on [GitHub](https://github.com/sam-14uel/Agent-Tool-Protocol).

---

**Happy coding! 🚀**