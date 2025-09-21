from django.urls import path
from .views import ToolView, ToolkitView
from .registry import clients

urlpatterns = [
    path(
        "atp/<str:toolkit_name>/<str:tool_name>/",
        ToolView.as_view(),
        name="atp_tool"
    ),
    path("atp/<str:toolkit_name>/", ToolkitView.as_view(), name="atp_toolkit"),
]