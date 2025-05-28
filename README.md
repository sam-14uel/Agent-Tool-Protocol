ATPClient
A Python client for interacting with the ATP API, allowing registration and execution of tools via WebSocket and HTTP connections.
Installation
Install the package using pip:
pip install atpclient

Usage
from atpclient import ATPClient

# Initialize the client
client = ATPClient(api_key="your-api-key", app_name="your-app-name")

# Define a tool
@client.register_tool(
    function_name="example_tool",
    params={"param1": "string", "param2": "string"},
    required_params=["param1"],
    description="An example tool",
    auth_provider=None,
    auth_type=None,
    auth_with=None
)
def example_tool(param1, param2="default"):
    return {"result": f"Received {param1} and {param2}"}

# Start the WebSocket connection
client.start()

# Stop the client when done
client.stop()

Requirements

Python 3.8 or higher
Dependencies: requests, websocket-client, websockets, rel

License
This project is licensed under the MIT License - see the LICENSE file for details.
