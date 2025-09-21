from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .registry import get_client

def get_tool_context(client, tool_name):
    tool = client.registered_tools.get(tool_name)
    if not tool:
        return None
    return {
        "function": tool_name,
        "params": tool["params"],
        "required_params": tool["required_params"],
        "description": tool["description"],
        "auth_provider": tool["auth_provider"],
        "auth_type": tool["auth_type"],
        "auth_with": tool["auth_with"],
    }

@method_decorator(csrf_exempt, name="dispatch")
class ToolView(View):
    def get(self, request, toolkit_name, tool_name):
        client = get_client(toolkit_name)
        if not client:
            return JsonResponse({"error": "Toolkit not found"}, status=404)
        context = get_tool_context(client, tool_name)
        if not context:
            return JsonResponse({"error": "Tool not found"}, status=404)
        return JsonResponse(context)

    def post(self, request, toolkit_name, tool_name):
        client = get_client(toolkit_name)
        if not client:
            return JsonResponse({"error": "Toolkit not found"}, status=404)
        tool = client.registered_tools.get(tool_name)
        if not tool:
            return JsonResponse({"error": "Tool not found"}, status=404)
        try:
            params = request.POST.dict()
            if request.content_type == "application/json":
                import json
                params = json.loads(request.body.decode())
            func = tool["function"]
            result = func(**params)
            return JsonResponse({"result": result})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def http_method_not_allowed(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["GET", "POST"])


from django.http import JsonResponse
from django.views import View
from .registry import get_client

class ToolkitView(View):
    def get(self, request, toolkit_name):
        client = get_client(toolkit_name)
        if not client:
            return JsonResponse({"error": "Toolkit not found"}, status=404)
        tools = [
            {
                "function": name,
                "description": tool["description"],
                "params": tool["params"],
                "required_params": tool["required_params"],
                "auth_provider": tool["auth_provider"],
                "auth_type": tool["auth_type"],
                "auth_with": tool["auth_with"],
            }
            for name, tool in client.registered_tools.items()
        ]
        return JsonResponse({
            "toolkit": toolkit_name,
            "app_name": getattr(client, "app_name", toolkit_name),
            "tools": tools,
        })