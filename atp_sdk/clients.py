import threading
import inspect
import hashlib
# import rel
import requests
import websocket # websocket client package(websocket-client)
# import websockets # websocket client and server package(websockets)
# from websockets.exceptions import ConnectionClosed
import json
import logging
import time
# import asyncio

# websocket.enableTrace(True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolKitClient:
    """
    ToolKitClient manages registration and execution of remote tools via WebSocket for the ATP Toolkit platform.

    Attributes:
        api_key (str): Your ATP Toolkit API key.
        app_name (str): Name of your application.
        base_url (str): Backend server URL.
        registered_tools (dict): Registered tool metadata.
    """
    def __init__(self, api_key, app_name, base_url="https://chatatp-backend.onrender.com"):
        """
        Initialize the ToolKitClient.

        Args:
            api_key (str): Your ATP Toolkit API key.
            app_name (str): Name of your application.
            base_url (str, optional): Backend server URL of the ATP Server. Defaults to chatatp-backend.onrender.com.
        """
        self.api_key = api_key
        self.app_name = app_name
        self.base_url = base_url.rstrip("/")
        self.registered_tools = {}
        self.exchange_tokens = {}
        self.lock = threading.Lock()
        self.ws = None
        self.ws_thread = None

        self.programming_language = "Python"

        self.loop = None
        self.running = False

    def register_tool(self, function_name, params, required_params, description, auth_provider, auth_type, auth_with):
        """
        Register a Python function as a remote tool.

        Args:
            function_name (str): Unique name for the tool based on the function.
            params (list): List of parameter names.
            required_params (list): List of required parameter names.
            description (str): Description of the tool.
            auth_provider (str): Name of the auth provider.
            auth_type (str): Type of authentication.
            auth_with (str): How authentication is performed.

        Returns:
            decorator: A decorator to wrap the tool function.
        """
        def decorator(func):
            # Ensure 'access_token' is NOT in user function signature
            #sig = inspect.signature(func)
            # if "access_token" in sig.parameters:
            #     raise ValueError(
            #         f"In tool '{function_name}': 'access_token' must not be declared in your function signature.\n"
            #         "ChatATP handles this securely and automatically."
            #     )

            # Get source code and hash it
            source_code = inspect.getsource(func)
            code_hash = hashlib.sha256(source_code.encode("utf-8")).hexdigest()

            # Register tool metadata
            self.registered_tools[function_name] = {
                "function": func,
                "params": params,
                "required_params": required_params,
                "description": description,
                "auth_provider": auth_provider,
                "auth_type": auth_type,
                "auth_with": auth_with,
                "source_code": source_code,
                "code_hash": code_hash,
                "function_id": function_name
            }

            # Register with server
            self._register_with_server(function_name)
            return func
        return decorator

    def _register_with_server(self, function_name):
        """
        Register the tool with the backend server.

        Args:
            function_name (str): Name of the tool to register.
        """
        tool_data = self.registered_tools[function_name]
        func = tool_data["function"]
        source_code = tool_data["source_code"]
        code_hash = tool_data["code_hash"]

        # Generate a sample response for registration
        sample_params = self._generate_sample_params(tool_data["params"])
        sig = inspect.signature(func)
        if "auth_token" in sig.parameters:
            sample_params["auth_token"] = "sample_token"
        try:
            response = func(**sample_params)
        except Exception as e:
            logger.warning(f"Sample invocation for '{function_name}' failed: {e}")
            response = {"error": "Sample response unavailable"}

        payload = {
            "function_id": function_name,
            "api_key": self.api_key,
            "app_name": self.app_name,
            "programming_language": self.programming_language,
            "code_hash": code_hash,
            "metadata": {
                "params": tool_data["params"],
                "required_params": tool_data["required_params"],
                "description": tool_data["description"],
                "auth_provider": tool_data["auth_provider"],
                "auth_type": tool_data["auth_type"],
                "auth_with": tool_data["auth_with"],
                "sample_response": response,
                "source_code": source_code  # <-- Include full source code here
            }
        }

        url = f"{self.base_url}/api/v1/register_tool"
        headers = {
            "Content-Type": "application/json",
            # "Authorization": f"Bearer {self.api_key}"
        }

        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            exchange_token = resp.json().get("exchange_token")
            with self.lock:
                self.exchange_tokens[function_name] = exchange_token
            logger.info(f" Tool '{function_name}' registered successfully. ✔️")
        else:
            # logger.error(f"Failed to register tool '{function_name}': {resp.status_code} - {resp.text}")
            logger.info(f"⚠️ Failed to register tool '{function_name}' ❌: {resp.status_code} - {resp.text}")

    def _generate_sample_params(self, param_defs):
        """
        Generate sample parameters for tool registration.

        Args:
            param_defs (list): List of parameter names.

        Returns:
            dict: Dictionary of sample parameters.
        """
        # Generate dummy sample parameters based on param definitions
        sample = {}
        # Always add a dummy auth_token for sample invocation
        sample["auth_token"] = "sample_token"
        for key in param_defs:
            # Use dummy values for now, you can refine per type
            sample[key] = "sample_value"
        return sample

    def _report_execution(self, function_id, result):
        """
        Report the result of a tool execution to the backend.

        Args:
            function_id (str): Name of the executed tool.
            result (dict): Result of the execution.
        """
        with self.lock:
            exchange_token = self.exchange_tokens.pop(function_id, None)

        if not exchange_token:
            logger.warning(f"No valid exchange token for '{function_id}'. Skipping report.")
            return

        payload = {
            "exchange_token": exchange_token,
            "result": result,
            "function_id": function_id
        }

        url = f"{self.base_url}/api/v1/execute_function"
        headers = {
            "Content-Type": "application/json",
            # "Authorization": f"Bearer {self.api_key}"
        }

        try:
            resp = requests.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                logger.info(f"Execution of '{function_id}' reported successfully.")
            else:
                logger.error(f"Failed to report execution for '{function_id}': {resp.status_code} - {resp.text}")
        except Exception as e:
            logger.exception(f"Error reporting execution for '{function_id}': {e}")

    def on_message(self, ws, message):
        """
        Handle incoming WebSocket messages.

        Args:
            ws: WebSocket connection.
            message (str): Incoming message as JSON string.
        """
        try:
            data = json.loads(message)
            message_type = data["message_type"]
            if message_type == "atp_client_connected":
                logger.info(f"Server message: {data['payload']['message']}")
            elif message_type == "atp_tool_request":
                payload = data["payload"]
                request_id = payload.get("request_id")
                tool_name = payload.get("tool_name")
                params = payload.get("params", {})
                auth_token = payload.get("auth_token")  # optional, if needed
                logger.info(f"Received tool request for '{tool_name}' with params: {params}")

                if tool_name in self.registered_tools:
                    tool_data = self.registered_tools[tool_name]
                    func = tool_data["function"]
                    sig = inspect.signature(func)
                    try:
                        if auth_token:
                            # Prepare arguments based on function signature
                            call_params = params.copy()
                            if "auth_token" in sig.parameters and auth_token:
                                call_params["auth_token"] = auth_token
                            elif any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()) and auth_token:
                                call_params["auth_token"] = auth_token
                            elif "auth_token" in sig.parameters and not auth_token:
                                error_result = {"error": f"Function '{tool_name}' requires 'auth_token', but none was provided."}
                                ws.send(json.dumps({
                                    "type": "tool_response",
                                    "request_id": request_id,
                                    "result": error_result
                                }))
                            # Call function with auth_token if not in signature
                            result = func(**call_params)
                            # Send response
                            ws.send(json.dumps({
                                "type": "tool_response",
                                "request_id": request_id,
                                "result": result
                            }))
                            # self._report_execution(tool_name, result)
                        else:
                            # Call function without auth_token if not in signature
                            result = func(**params)
                            # Send response
                            ws.send(json.dumps({
                                "type": "tool_response",
                                "request_id": request_id,
                                "result": result
                            }))
                            # self._report_execution(tool_name, result)
                    except Exception as e:
                        error_result = {"error": str(e)}
                        ws.send(json.dumps({
                            "type": "tool_response",
                            "request_id": request_id,
                            "result": error_result
                        }))
                        # self._report_execution(tool_name, error_result)
                else:
                    logger.info(f"Unknown tool requested: {tool_name}")

            else:
                logger.info(f"Unknown message type: {message_type}")
        except Exception as e:
            logger.info(f"Error handling WebSocket message: {e}")

    def start(self):
        """
        Start the WebSocket client and listen for tool requests.
        """
        self.running = True

        def run_ws():
            if self.base_url.startswith("https://"):
                ws_url = self.base_url.replace("https://", "wss://")
            elif self.base_url.startswith("http://"):
                ws_url = self.base_url.replace("http://", "ws://")
            url = f"{ws_url}/ws/v1/atp/{self.api_key}/"
            while True:
                try:
                    logger.info(f"Connecting to: {url}")
                    self.ws = websocket.WebSocketApp(
                        url,
                        on_open=lambda ws: logger.info("WebSocket connection established."),
                        on_message=self.on_message,
                        on_error=on_error,
                        on_close=on_close
                    )
                    self.ws.run_forever(ping_interval=30)
                    # self.ws.run_forever(dispatcher=rel, ping_interval=30, reconnect=5)

                    # rel.signal(2, rel.abort)
                    # rel.dispatch()

                    logger.warning("WebSocket disconnected. Reconnecting in 5 seconds...")
                except Exception as e:
                    logger.exception("Exception in WebSocket thread")

                    time.sleep(5)  # delay before trying again

        thread = threading.Thread(target=run_ws)
        thread.daemon = True
        thread.start()

        self.run_forever()

        logger.info("WebSocket thread started.")


    def run_forever(self):
        """
        Keep the main thread alive until stopped.
        """
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()


    def stop(self):
        """
        Stop the WebSocket client and close the connection.
        """
        if self.ws:
            self.ws.close()
        if self.ws_thread:
            self.ws_thread.join()
        logger.info("WebSocket connection stopped.")


def on_error(ws, error):
    logger.exception(f"WebSocket error: {error}")

def on_close(ws, code, reason):
    logger.error(f"WebSocket closed with code {code} and reason: {reason}")
