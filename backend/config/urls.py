from django.urls import include, path
from rest_framework.routers import DefaultRouter

from todos.views import TodoViewSet

router = DefaultRouter()
router.register("todos", TodoViewSet)

# L'API REST classique : /api/todos/
# (le serveur MCP, lui, est monté sur /mcp dans config/asgi.py)
urlpatterns = [
    path("api/", include(router.urls)),
]
