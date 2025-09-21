# Registry for all ToolKitClient instances
clients = {}

def init_registry():
    global clients
    if clients is None or not isinstance(clients, dict):
        clients = {}

def register_client(toolkit_name, client):
    clients[toolkit_name] = client

def get_client(toolkit_name):
    return clients.get(toolkit_name)