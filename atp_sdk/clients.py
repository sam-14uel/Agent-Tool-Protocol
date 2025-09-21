"""
ToolKitClient and LLMClient
"""

import threading
import inspect
import hashlib
import uuid
# import rel
import requests
import websocket
import json
import logging
import time
# import asyncio
from websocket import WebSocketException, WebSocketConnectionClosedException
import os
import hashlib
from pathlib import Path
from typing import Dict, Set, Optional, Union
# websocket.enableTrace(True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileWatcher:
    """
    Monitors Python files for changes and triggers callbacks when code is modified.
    """
    def __init__(self, callback):
        self.callback = callback
        self.file_hashes: Dict[str, str] = {}
        self.watched_files: Set[str] = set()
        self.running = False
        self.watcher_thread = None
        
    def add_file(self, file_path: str):
        """Add a file to watch for changes."""
        if os.path.exists(file_path):
            self.watched_files.add(file_path)
            self.file_hashes[file_path] = self._get_file_hash(file_path)
            
    def _get_file_hash(self, file_path: str) -> str:
        """Get the hash of a file's contents."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return hashlib.sha256(content.encode('utf-8')).hexdigest()
        except Exception:
            return ""
            
    def start(self):
        """Start the file watcher thread."""
        self.running = True
        self.watcher_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watcher_thread.start()
        
    def stop(self):
        """Stop the file watcher."""
        self.running = False
        if self.watcher_thread:
            self.watcher_thread.join()
            
    def _watch_loop(self):
        """Main watching loop that checks for file changes."""
        while self.running:
            try:
                for file_path in list(self.watched_files):
                    if not os.path.exists(file_path):
                        continue
                        
                    current_hash = self._get_file_hash(file_path)
                    if current_hash != self.file_hashes.get(file_path):
                        logger.info(f"Code change detected in {file_path}")
                        self.file_hashes[file_path] = current_hash
                        self.callback(file_path)
                        
                time.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Error in file watcher: {e}")
                time.sleep(5)  # Wait longer on error

class ToolKitClient:
    """
    ToolKitClient manages registration and execution of remote tools via WebSocket for the ATP Toolkit platform.

    Attributes:
        api_key (str): Your ATP Toolkit API key.
        app_name (str): Name of your application.
        base_url (str): Backend server URL.
        registered_tools (dict): Registered tool metadata.
    """
    def __init__(self, api_key, app_name, base_url="https://chatatp-backend.onrender.com", endpoint_url=None, auto_restart=True, protocol="http", idle_timeout=300):
        """
        Initialize the ToolKitClient.

        Args:
            api_key (str): Your ATP Toolkit API key.
            app_name (str): Name of your application.
            base_url (str, optional): Backend server URL of the ATP Server. Defaults to chatatp-backend.onrender.com.
            endpoint_url (str, optional): Endpoint URL where the toolkit is deployed and ready to get requests.
            auto_restart (bool, optional): Whether to auto-restart on code changes. Defaults to True.
            protocol (str, optional): Connection protocol, either "ws(s)" or "http(s)". Defaults to "https" use wss for development and http for production.
            idle_timeout (int, optional): Idle timeout in seconds before disconnecting. Defaults to 300 seconds (5 minutes).
        """
        self.idle_timeout = idle_timeout  # Default: 300 seconds (5 minutes)
        self.last_activity_time = time.time()
        self.protocol = protocol  # "ws" or "http"
        self.api_key = api_key
        self.app_name = app_name
        self.base_url = base_url.rstrip("/")
        self.endpoint_url = endpoint_url  # <-- Add this
        self.registered_tools = {}
        self.exchange_tokens = {}
        self.lock = threading.Lock()
        self.ws = None
        self.ws_thread = None
        self.auto_restart = auto_restart

        self.programming_language = "Python"

        self.loop = None
        self.running = False
        
        # File watching for auto-restart
        if self.auto_restart:
            self.file_watcher = FileWatcher(self._on_code_change)
            self._setup_file_watching()
        else:
            self.file_watcher = None

    def _setup_file_watching(self):
        """Setup file watching for all registered tool files."""
        if not self.file_watcher:
            return
            
        # Get the main script file
        main_file = inspect.stack()[-1].filename
        if main_file and main_file != '<string>':
            self.file_watcher.add_file(main_file)
            
        # Watch current working directory for Python files
        current_dir = Path.cwd()
        for py_file in current_dir.rglob("*.py"):
            if py_file.is_file():
                self.file_watcher.add_file(str(py_file))
                
        logger.info(f"Watching {len(self.file_watcher.watched_files)} Python files for changes")
        
    def _on_code_change(self, file_path: str):
        """Handle code changes by restarting the toolkit client."""
        logger.info(f"Code change detected in {file_path}. Restarting toolkit client...")
        
        # Stop current connection
        self.stop()
        
        # Wait a moment for cleanup
        time.sleep(2)
        
        # Re-register all tools
        self._re_register_tools()
        
        # Restart the client
        self.start()
        
        logger.info("Toolkit client restarted successfully after code change")
        
    def _re_register_tools(self):
        """Re-register all tools after code changes."""
        logger.info("Re-registering tools after code change...")
        
        # Clear existing exchange tokens
        with self.lock:
            self.exchange_tokens.clear()
            
        # Re-register each tool
        for function_name in list(self.registered_tools.keys()):
            self._register_with_server(function_name)
            
        logger.info(f"Re-registered {len(self.registered_tools)} tools")

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
        self.last_activity_time = time.time()  # Reset timer on activity
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

    def _watch_idle(self):
        """Monitor for inactivity and close the connection if idle for too long."""
        while self.running:
            if time.time() - self.last_activity_time > self.idle_timeout:
                logger.info("WebSocket idle timeout reached. Closing connection...")
                self.stop()
                break
            time.sleep(10)  # Check every 10 seconds

    import requests

    def _send_tool_result_http(self, request_id, result):
        """
        Send tool execution result to toolkit's endpoint_url.
        """
        if not self.endpoint_url:
            raise ValueError("No endpoint_url configured for HTTP mode.")
        payload = {
            "request_id": request_id,
            "result": result
        }
        resp = requests.post(self.endpoint_url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _send_tool_result_inbox(self, request_id, result):
        """
        Send tool execution result to ATP server inbox endpoint.
        """
        url = f"{self.base_url}/api/v1/toolkit/{self.api_key}/inbox/respond"
        payload = {
            "request_id": request_id,
            "response": result
        }
        logger.info(f"Sending result to inbox: request_id={request_id}, result={result}")
        try:
            resp = requests.post(url, json=payload, timeout=30)
            logger.info(f"Inbox response: status={resp.status_code}, content={resp.text}")
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"Error sending result to inbox: {e}")
            raise

    def poll_inbox_for_requests(self):
        """
        Poll the ATP server for pending tool requests.
        """
        url = f"{self.base_url}/api/v1/toolkit/{self.api_key}/inbox"
        logger.info(f"Polling inbox at {url}")
        try:
            resp = requests.get(url, timeout=30)
            logger.info(f"Inbox poll response: status={resp.status_code}, content={resp.text}")
            if resp.status_code == 200:
                try:
                    response_data = resp.json()
                    if response_data:
                        logger.info(f"Received inbox request: {json.dumps(response_data, indent=2)}")
                        return response_data
                    else:
                        logger.debug("Inbox is empty")
                        return None
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse inbox response JSON: {e}, response={resp.text}")
                    return None
            else:
                logger.warning(f"Inbox poll failed: status={resp.status_code}, response={resp.text}")
                return None
        except requests.RequestException as e:
            logger.error(f"Error polling inbox: {e}")
            return None

    def _poll_inbox_loop(self):
        """
        Poll the ATP server for pending tool requests (Inbox Mode).
        """
        logger.info("Starting inbox polling loop")
        while self.running:
            try:
                req = self.poll_inbox_for_requests()
                if req:
                    request_id = req.get("request_id")
                    tool_name = req.get("tool_name")
                    params = req.get("params", {})
                    auth_token = req.get("auth_token")
                    logger.info(f"Processing inbox request: request_id={request_id}, tool_name={tool_name}, params={params}, auth_token={'<hidden>' if auth_token else None}")

                    if tool_name in self.registered_tools:
                        logger.info(f"Found registered tool: {tool_name}")
                        func = self.registered_tools[tool_name]["function"]
                        sig = inspect.signature(func)
                        try:
                            call_params = params.copy()
                            if auth_token and ("auth_token" in sig.parameters or any(
                                    p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())):
                                call_params["auth_token"] = auth_token
                                logger.debug(f"Added auth_token to call parameters for {tool_name}")
                            logger.info(f"Executing tool {tool_name} with params: {call_params}")
                            result = func(**call_params)
                            logger.info(f"Tool {tool_name} executed successfully, result: {result}")
                            self._send_tool_result_inbox(request_id, result)
                            logger.info(f"Sent result for request_id={request_id} to inbox")
                        except Exception as e:
                            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
                            error_result = {"error": str(e)}
                            self._send_tool_result_inbox(request_id, error_result)
                    else:
                        logger.warning(f"Tool {tool_name} not found in registered tools")
                else:
                    logger.debug("No pending requests in inbox")
                time.sleep(30)  # Poll every 30 seconds
            except Exception as e:
                logger.error(f"Inbox polling loop error: {e}", exc_info=True)
                time.sleep(30)  # Wait 30 seconds after an error

    def start(self):
        """
        Start the WebSocket client and listen for tool requests.
        """
        # Start idle watcher thread
        idle_thread = threading.Thread(target=self._watch_idle, daemon=True)
        idle_thread.start()
        self.running = True

        # Start file watcher if auto-restart is enabled
        if self.file_watcher:
            self.file_watcher.start()

        if self.protocol.startswith("http"):
            # thread = threading.Thread(target=self._run_http_loop, daemon=True)
            thread = threading.Thread(target=self._poll_inbox_loop, daemon=True)
        else:
            thread = threading.Thread(target=self._run_ws_loop, daemon=True)

        thread.start()
        self.ws_thread = thread
        self.run_forever()


    def _run_ws_loop(self):
        if self.base_url.startswith("https://"):
            ws_url = self.base_url.replace("https://", "wss://")
        elif self.base_url.startswith("http://"):
            ws_url = self.base_url.replace("http://", "ws://")
        url = f"{ws_url}/ws/v1/atp/toolkit-client/{self.api_key}/"
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
                logger.warning("WebSocket disconnected. Reconnecting in 5 seconds...")
            except Exception as e:
                logger.exception("Exception in WebSocket thread")

                time.sleep(5)  # delay before trying again

    def _run_http_loop(self):
        """Poll the ATP server for incoming tool requests over HTTP."""
        url = f"{self.base_url}/api/v1/atp/toolkit-client/{self.api_key}/messages/"
        logger.info(f"Starting HTTP polling loop: {url}")

        while self.running:
            try:
                resp = requests.get(url, timeout=60)  # long-poll up to 60s
                if resp.status_code == 200:
                    data = resp.json()
                    if data:
                        # simulate on_message handling
                        self._handle_http_message(data)
                else:
                    logger.warning(f"Polling failed: {resp.status_code} - {resp.text}")
                    time.sleep(5)
            except Exception as e:
                logger.error(f"HTTP polling error: {e}")
                time.sleep(5)

    def _handle_http_message(self, data):
        """Handle a message payload from HTTP polling."""
        try:
            message_type = data.get("message_type")
            if message_type == "atp_tool_request":
                payload = data["payload"]
                request_id = payload.get("request_id")
                tool_name = payload.get("tool_name")
                params = payload.get("params", {})
                auth_token = payload.get("auth_token")

                if tool_name in self.registered_tools:
                    tool_data = self.registered_tools[tool_name]
                    func = tool_data["function"]
                    sig = inspect.signature(func)

                    try:
                        call_params = params.copy()
                        if auth_token and ("auth_token" in sig.parameters or any(
                                p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())):
                            call_params["auth_token"] = auth_token

                        result = func(**call_params)
                        self._report_execution(tool_name, result)

                    except Exception as e:
                        error_result = {"error": str(e)}
                        self._report_execution(tool_name, error_result)
                else:
                    logger.warning(f"Unknown tool requested: {tool_name}")
            else:
                logger.info(f"Unknown HTTP message type: {message_type}")
        except Exception as e:
            logger.error(f"Error handling HTTP message: {e}")



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
        self.running = False
        
        # Stop file watcher
        if self.file_watcher:
            self.file_watcher.stop()

        if self.ws:
            self.ws.close()
        if self.ws_thread:
            self.ws_thread.join()
        logger.info("WebSocket connection stopped.")


def on_error(ws, error):
    logger.exception(f"WebSocket error: {error}")

def on_close(ws, code, reason):
    logger.error(f"WebSocket closed with code {code} and reason: {reason}")


class WebSocketException(Exception):
    pass

class HTTPException(Exception):
    pass

class LLMClient:
    """
    LLMClient manages connections to the ATP Agent Server for toolkit context retrieval
    and remote tool execution. Supports both WebSocket and HTTP protocols.
    
    This client is designed to work seamlessly with popular LLM providers like OpenAI,
    Anthropic, and Mistral by handling tool call formatting automatically.
    """
    def __init__(
        self,
        api_key: str,
        protocol: str = "https",
        base_url: str = "https://chatatp-backend.onrender.com",
        idle_timeout: int = 300,
    ):
        """
        Initialize the LLMClient.
        
        Args:
            api_key (str): ATP API key for authentication.
            protocol (str): Connection protocol. Options: "ws", "wss", "http", "https". 
                          Defaults to "https".
            base_url (str): Server URL. Defaults to "https://chatatp-backend.onrender.com".
            idle_timeout (int): Idle timeout in seconds. Defaults to 300.
        """
        self.api_key = api_key
        self.protocol = protocol.lower()
        self.base_url = base_url.rstrip("/")
        self.idle_timeout = idle_timeout
        self.last_activity_time = time.time()
        
        # Connection management
        self.ws = None
        self.lock = threading.Lock()
        self.response_data = {}
        self.authenticated = False
        
        # Initialize based on protocol
        if self.protocol in ["ws", "wss"]:
            self._init_websocket()
        elif self.protocol in ["http", "https"]:
            self._init_http()
        else:
            raise ValueError("Unsupported protocol. Use 'ws', 'wss', 'http', or 'https'.")

    def _init_websocket(self):
        """Initialize WebSocket-specific attributes."""
        if self.base_url.startswith("https://"):
            ws_url = self.base_url.replace("https://", "wss://")
        elif self.base_url.startswith("http://"):
            ws_url = self.base_url.replace("http://", "ws://")
        else:
            raise ValueError("Invalid base URL for WebSocket.")
        self.ws_url = f"{ws_url}/{self.api_key}/"
        self._connect()

    def _init_http(self):
        """Initialize HTTP-specific attributes."""
        self.http_url = f"{self.base_url}/api/v1/atp/llm-client/"

    def _connect(self):
        """Establish a WebSocket connection with authentication."""
        with self.lock:
            if self.ws and self.ws.sock and self.ws.sock.connected and self.authenticated:
                return
            try:
                self.ws = websocket.WebSocketApp(
                    self.ws_url,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                )
                ws_thread = threading.Thread(target=self.ws.run_forever, kwargs={"ping_interval": 30})
                ws_thread.daemon = True
                ws_thread.start()
                # Wait for authentication
                start_time = time.time()
                while not self.authenticated and time.time() - start_time < 10:
                    time.sleep(0.1)
                if not self.authenticated:
                    raise WebSocketException("Authentication timed out.")
            except Exception as e:
                print(f"Failed to initiate WebSocket connection: {e}")
                raise WebSocketException(f"Failed to initiate WebSocket connection: {e}")

    def _on_open(self, ws: websocket.WebSocketApp):
        """Handle WebSocket connection opening by sending authentication."""
        try:
            auth_message = json.dumps({"type": "auth", "api_key": self.api_key})
            ws.send(auth_message)
            print("WebSocket connection established and authentication sent.")
        except Exception as e:
            print(f"Error during WebSocket authentication: {e}")
            raise WebSocketException(f"Authentication failed: {e}")

    def _on_message(self, ws: websocket.WebSocketApp, message: str):
        """Handle incoming WebSocket messages."""
        self.last_activity_time = time.time()
        try:
            data = json.loads(message)
            message_type = data.get("type")
            request_id = data.get("request_id")
            if message_type == "auth_response":
                if not data.get("success"):
                    print(f"Authentication failed: {data.get('error', 'Unknown error')}")
                    ws.close()
                else:
                    print("Authentication successful.")
                    self.authenticated = True
            elif message_type in ["toolkit_context", "task_response"]:
                self.response_data[request_id] = data.get("payload", {})
            else:
                print(f"Received unknown message type: {message_type}")
        except json.JSONDecodeError:
            print("Failed to parse WebSocket message as JSON.")
        except Exception as e:
            print(f"Error processing WebSocket message: {e}")

    def _on_error(self, ws: websocket.WebSocketApp, error: Exception):
        """Handle WebSocket errors."""
        print(f"WebSocket error: {error}, type: {type(error).__name__}")
        with self.lock:
            self.ws = None
            self.authenticated = False

    def _on_close(self, ws: websocket.WebSocketApp, close_status_code: int, close_msg: str):
        """Handle WebSocket connection closure."""
        print(f"WebSocket closed with code {close_status_code}: {close_msg}")
        with self.lock:
            self.ws = None
            self.authenticated = False

    def _http_request(self, endpoint: str, payload: dict, method: str = "POST", stream: bool = False):
        """Make an HTTP request to the server."""
        url = f"https://chatatp-backend.onrender.com/api/v1/atp/llm-client/process/"
        # if not stream:
        # resp = requests.post(url, json=payload, headers=headers)
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_toolkit_context(self, toolkit_id: str, user_prompt: str, provider: str = "openai") -> dict:
        """
        Retrieve the execution context for a toolkit from the server.

        The context combines provider-specific schema details (e.g., OpenAI, Anthropic, Mistral) 
        with the given user prompt, ensuring the request aligns with the provider's 
        tool/function call format.

        Args:
            toolkit_id (str): Unique ID/name of the toolkit to retrieve context for.
            user_prompt (str): The user's input to append to the toolkit context.
            provider (str): The LLM provider whose tool/function call schema should be used.
                          Options: "openai", "anthropic", "mistralai", "mistral". Defaults to "openai".

        Returns:
            dict: Toolkit context containing tools and system instructions ready for the provider.

        Raises:
            WebSocketException: If the connection fails or authentication is invalid.
            ValueError: If the server returns an invalid response.
        """
        if self.protocol in ["ws", "wss"]:
            return self._get_toolkit_context_ws(toolkit_id, user_prompt, provider)
        elif self.protocol in ["http", "https"]:
            return self._get_toolkit_context_http(toolkit_id, user_prompt, provider)

    def _get_toolkit_context_ws(self, toolkit_id: str, user_prompt: str, provider: str) -> dict:
        """Retrieve toolkit context using WebSocket."""
        self._connect()
        if not self.authenticated:
            raise WebSocketException("WebSocket not authenticated.")
        request_id = f"context_{toolkit_id}_{str(uuid.uuid4())}"
        message = json.dumps({
            "type": "get_toolkit_context",
            "toolkit_id": toolkit_id,
            "request_id": request_id,
            "provider": provider,
            "user_prompt": user_prompt,
        })
        try:
            with self.lock:
                if not self.ws or not self.ws.sock or not self.ws.sock.connected:
                    raise WebSocketException("WebSocket connection is closed.")
                self.ws.send(message)
        except Exception as e:
            logger.error(f"Error sending get_toolkit_context message: {e}")
            raise WebSocketException(f"Failed to send request: {e}")
        # Wait for response
        timeout = 30
        start_time = time.time()
        while request_id not in self.response_data:
            if time.time() - start_time > timeout:
                raise TimeoutError("Timed out waiting for toolkit context response.")
            time.sleep(0.1)
        return self.response_data.pop(request_id)

    def _get_toolkit_context_http(self, toolkit_id: str, user_prompt: str, provider: str) -> dict:
        """Retrieve toolkit context using HTTP."""
        payload = {
            "type": "get_toolkit_context",
            "toolkit_id": toolkit_id,
            "request_id": str(uuid.uuid4()),
            "provider": provider,
            "user_prompt": user_prompt,
        }
        response = self._http_request("process", payload, stream=False)
        return response.get("payload", {})

    def call_tool(self, toolkit_id: str, tool_calls: list, provider: str = "openai", auth_token: str = None, user_prompt: str = None, timeout: int = 120, sequential: bool = False) -> list:
        """
        Execute tool calls from LLM providers on the server.

        This method accepts tool call objects directly from LLM providers (OpenAI, Anthropic, Mistral)
        and executes them remotely. The tool calls are automatically formatted for the backend server.

        Args:
            toolkit_id (str): Unique ID/name/identifier of the toolkit instance to execute.
            tool_calls (list): List of tool call objects from LLM response.
            provider (str): The LLM provider. Options: "openai", "anthropic", "mistralai", "mistral". 
                          Defaults to "openai".
            auth_token (str, optional): Authentication token for the request.
            user_prompt (str, optional): Additional user input to include in the execution.
            timeout (int, optional): Timeout in seconds. Default is 120.
            sequential (bool, optional): If True, execute tool calls one by one. If False, execute in parallel. Default is False.

        Returns:
            list: List of tool execution results with tool_call_id and result.

        Raises:
            WebSocketException: If the connection fails or authentication is invalid.
            ValueError: If the server returns an invalid response type.
        """
        if not tool_calls:
            logger.warning("No tool calls provided")
            return []
            
        # Format tool calls for the backend
        formatted_calls = self._format_tool_calls(tool_calls, provider)
        
        if sequential:
            # Execute tool calls one by one
            return self._call_tool_sequential(toolkit_id, formatted_calls, provider, auth_token, user_prompt, timeout)
        else:
            # Execute tool calls in parallel (default behavior)
            if self.protocol in ["ws", "wss"]:
                return self._call_tool_ws(toolkit_id, formatted_calls, provider, auth_token, user_prompt, timeout)
            elif self.protocol in ["http", "https"]:
                return self._call_tool_http(toolkit_id, formatted_calls, provider, auth_token, user_prompt, timeout)

    def _format_tool_calls(self, tool_calls: list, provider: str) -> list:
        """
        Format tool calls from different providers to a consistent format for the backend.
        
        Args:
            tool_calls (list): Raw tool calls from LLM provider
            provider (str): Provider name
            
        Returns:
            list: Formatted tool calls for backend
        """
        formatted_calls = []
        
        for tool_call in tool_calls:
            try:
                if provider in ["openai"]:
                    # OpenAI format: {id, function: {name, arguments}}
                    if hasattr(tool_call, 'get'):
                        # Dictionary format
                        formatted_call = {
                            "id": tool_call.get("id", ""),
                            "function": tool_call.get("function", {}).get("name", ""),
                            "arguments": tool_call.get("function", {}).get("arguments", {}),
                            "type": "function"
                        }
                    else:
                        # Object format
                        formatted_call = {
                            "id": getattr(tool_call, "id", ""),
                            "function": getattr(tool_call.function, "name", "") if hasattr(tool_call, "function") else "",
                            "arguments": getattr(tool_call.function, "arguments", {}) if hasattr(tool_call, "function") else {},
                            "type": "function"
                        }
                        
                elif provider in ["anthropic"]:
                    # Anthropic format: {id, name, input}
                    if hasattr(tool_call, 'get'):
                        # Dictionary format
                        formatted_call = {
                            "id": tool_call.get("id", ""),
                            "function": tool_call.get("name", ""),
                            "arguments": tool_call.get("input", {}),
                            "type": "function"
                        }
                    else:
                        # Object format
                        formatted_call = {
                            "id": getattr(tool_call, "id", ""),
                            "function": getattr(tool_call, "name", ""),
                            "arguments": getattr(tool_call, "input", {}),
                            "type": "function"
                        }
                        
                elif provider in ["mistralai", "mistral"]:
                    # Mistral format: ToolCall object with function, id, type, index
                    if hasattr(tool_call, 'get'):
                        # Dictionary format
                        formatted_call = {
                            "id": tool_call.get("id", ""),
                            "function": tool_call.get("name", ""),
                            "arguments": tool_call.get("arguments", {}),
                            "type": "function"
                        }
                    else:
                        # Mistral ToolCall object format
                        function_name = ""
                        arguments = {}
                        
                        if hasattr(tool_call, "function"):
                            function_name = getattr(tool_call.function, "name", "")
                            # Parse arguments if it's a string
                            args_str = getattr(tool_call.function, "arguments", "{}")
                            if isinstance(args_str, str):
                                try:
                                    arguments = json.loads(args_str)
                                except json.JSONDecodeError as e:
                                    logger.warning(f"Failed to parse Mistral arguments '{args_str}': {e}")
                                    arguments = {}
                            else:
                                arguments = args_str
                        
                        formatted_call = {
                            "id": getattr(tool_call, "id", ""),
                            "function": function_name,
                            "arguments": arguments,
                            "type": "function"
                        }
                        
                else:
                    # Generic format - try to extract common fields
                    if hasattr(tool_call, 'get'):
                        # Dictionary format
                        formatted_call = {
                            "id": tool_call.get("id", ""),
                            "function": tool_call.get("function", tool_call.get("name", "")),
                            "arguments": tool_call.get("arguments", tool_call.get("input", {})),
                            "type": "function"
                        }
                    else:
                        # Object format
                        formatted_call = {
                            "id": getattr(tool_call, "id", ""),
                            "function": getattr(tool_call, "function", getattr(tool_call, "name", "")),
                            "arguments": getattr(tool_call, "arguments", getattr(tool_call, "input", {})),
                            "type": "function"
                        }
                
                formatted_calls.append(formatted_call)
                
            except Exception as e:
                logger.error(f"Error formatting tool call: {e}")
                # Add a fallback formatted call
                formatted_calls.append({
                    "id": f"error_{len(formatted_calls)}",
                    "function": "unknown",
                    "arguments": {},
                    "type": "function",
                    "error": str(e)
                })
        
        return formatted_calls

    def _call_tool_sequential(self, toolkit_id: str, formatted_calls: list, provider: str, auth_token: str, user_prompt: str, timeout: int) -> list:
        """Execute tool calls one by one sequentially."""
        results = []
        
        for i, tool_call in enumerate(formatted_calls):
            logger.info(f"Executing tool call {i+1}/{len(formatted_calls)}: {tool_call.get('function', 'unknown')}")
            
            try:
                if self.protocol in ["ws", "wss"]:
                    result = self._call_tool_ws(toolkit_id, [tool_call], provider, auth_token, user_prompt, timeout)
                elif self.protocol in ["http", "https"]:
                    result = self._call_tool_http(toolkit_id, [tool_call], provider, auth_token, user_prompt, timeout)
                
                if result and isinstance(result, list):
                    results.extend(result)
                    logger.info(f"Tool call {i+1} completed successfully")
                elif result:
                    # Handle single result
                    results.append(result)
                    logger.info(f"Tool call {i+1} completed successfully")
                else:
                    results.append({
                        "tool_call_id": tool_call.get("id", f"call_{i}"),
                        "result": {"error": "No result returned"}
                    })
                    
            except Exception as e:
                logger.error(f"Error executing tool call {i+1}: {e}")
                results.append({
                    "tool_call_id": tool_call.get("id", f"call_{i}"),
                    "result": {"error": str(e)}
                })
        
        return results

    def _call_tool_ws(self, toolkit_id: str, formatted_calls: list, provider: str, auth_token: str, user_prompt: str, timeout: int) -> list:
        """Execute tool calls using WebSocket."""
        self._connect()
        if not self.authenticated:
            raise WebSocketException("WebSocket not authenticated.")
        
        results = []
        
        for i, tool_call in enumerate(formatted_calls):
            request_id = f"task_{toolkit_id}_{i}_{str(uuid.uuid4())}"
            message = json.dumps({
                "type": "task_request",
                "toolkit_id": toolkit_id,
                "request_id": request_id,
                "payload": tool_call,
                "provider": provider,
                "auth_token": auth_token,
                "user_prompt": user_prompt,
            })
            
            try:
                with self.lock:
                    if not self.ws or not self.ws.sock or not self.ws.sock.connected:
                        raise WebSocketException("WebSocket connection is closed.")
                    self.ws.send(message)
            except Exception as e:
                logger.error(f"Error sending task_request message: {e}")
                raise WebSocketException(f"Failed to send request: {e}")
            
            # Wait for response
            start_time = time.time()
            while request_id not in self.response_data:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Timed out waiting for task response {i+1}.")
                time.sleep(0.1)
            
            response = self.response_data.pop(request_id)
            results.append({
                "tool_call_id": tool_call.get("id", f"call_{i}"),
                "result": response
            })
        
        return results

    def _call_tool_http(self, toolkit_id: str, formatted_calls: list, provider: str, auth_token: str, user_prompt: str, timeout: int) -> list:
        """Execute tool calls using HTTP."""
        results = []
        
        for i, tool_call in enumerate(formatted_calls):
            payload = {
                "type": "task_request",
                "toolkit_id": toolkit_id,
                "request_id": f"task_{toolkit_id}_{i}_{str(uuid.uuid4())}",
                "payload": tool_call,
                "provider": provider,
                "auth_token": auth_token,
                "user_prompt": user_prompt,
            }
            
            try:
                response = self._http_request("process", payload)
                results.append({
                    "tool_call_id": tool_call.get("id", f"call_{i}"),
                    "result": response
                })
            except Exception as e:
                logger.error(f"Error executing tool call {i+1}: {e}")
                results.append({
                    "tool_call_id": tool_call.get("id", f"call_{i}"),
                    "result": {"error": str(e)}
                })
        
        return results
    

    def call_tool_streaming(self, toolkit_id: str, tool_calls: list, provider: str = "openai", auth_token: str = None, user_prompt: str = None, timeout: int = 120):
        """
        Execute tool calls and stream the response from the backend (SSE).
        Returns a generator yielding each SSE event as a dict.
        """
        if not tool_calls:
            logger.warning("No tool calls provided")
            return

        formatted_calls = self._format_tool_calls(tool_calls, provider)
        # Only support HTTP streaming for now
        if self.protocol not in ["http", "https"]:
            raise ValueError("Streaming only supported for HTTP protocol")

        # Only support one tool call per streaming request
        tool_call = formatted_calls[0]
        payload = {
            "type": "task_request",
            "toolkit_id": toolkit_id,
            "request_id": f"task_{toolkit_id}_{str(uuid.uuid4())}",
            "payload": tool_call,
            "provider": provider,
            "auth_token": auth_token,
            "user_prompt": user_prompt,
        }
        url = f"{self.base_url}/api/v1/atp/llm-client/process/"
        headers = {
            "Accept": "application/json",
            "Cache-Control": "no-cache",
        }

        return self._http_stream_request(url, payload, headers, timeout)

    def _http_stream_request(self, url, payload, headers, timeout):
        """
        Internal: Make an HTTP POST request and yield SSE events as dicts.
        """
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=timeout) as resp:
            if resp.status_code != 200:
                raise Exception(f"Streaming request failed: {resp.status_code} {resp.text}")

            # Parse SSE events
            for line in resp.iter_lines():
                if line:
                    try:
                        # SSE lines start with "data: "
                        if line.startswith(b"data: "):
                            data = line[len(b"data: "):]
                            event = json.loads(data.decode("utf-8"))
                            yield event
                    except Exception as e:
                        logger.warning(f"Failed to parse SSE event: {e}")