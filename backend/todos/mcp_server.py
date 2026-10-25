"""Le serveur MCP.

Une MCP App = 2 primitives MCP classiques reliées entre elles :

  1. une RESSOURCE  `ui://todos/app.html`  -> le HTML (notre app React buildée)
  2. un TOOL        `show_todos`           -> déclare dans ses _meta :
                                               {"ui": {"resourceUri": "ui://todos/app.html"}}

Quand le LLM appelle `show_todos`, l'hôte (Claude, VS Code...) voit ce lien,
télécharge la ressource, l'affiche dans une iframe, puis envoie le résultat
du tool à l'iframe. L'iframe peut ensuite rappeler d'autres tools du serveur.
"""

from django.conf import settings
from fastmcp import FastMCP
from fastmcp.apps import AppConfig

from .models import Todo
from .serializers import TodoSerializer

APP_URI = "ui://todos/app.html"

mcp = FastMCP("Todos")


def _all_todos() -> dict:
    """Format renvoyé par tous les tools : {"todos": [...]}.

    FastMCP le transmet en `structuredContent`, que l'app React lit directement.
    """
    return {"todos": TodoSerializer(Todo.objects.order_by("id"), many=True).data}


# --- 1. La ressource UI ------------------------------------------------------
# Les URI `ui://` sont servies automatiquement avec le MIME
# `text/html;profile=mcp-app`, celui qu'attendent les hôtes MCP Apps.
@mcp.resource(APP_URI)
def todo_app() -> str:
    return settings.MCP_APP_HTML.read_text()


# --- 2. Le tool qui ouvre l'UI -------------------------------------------------
# app=AppConfig(resource_uri=...) ajoute `_meta.ui.resourceUri` au tool.
@mcp.tool(app=AppConfig(resource_uri=APP_URI))
def show_todos() -> dict:
    """Affiche la liste de tâches dans une interface interactive."""
    return _all_todos()


# --- 3. Des tools "normaux", appelables par le LLM ET par l'UI ---------------
# (Les fonctions sync sont exécutées dans un thread par FastMCP,
#  donc l'ORM Django fonctionne sans sync_to_async.)
@mcp.tool
def add_todo(title: str) -> dict:
    """Ajoute une tâche."""
    serializer = TodoSerializer(data={"title": title})
    serializer.is_valid(raise_exception=True)  # même validation que l'API REST
    serializer.save()
    return _all_todos()


# visibility=["app"] : réservé à l'UI, le LLM ne le voit pas dans sa liste de tools.
@mcp.tool(app=AppConfig(visibility=["app"]))
def toggle_todo(todo_id: int) -> dict:
    """Coche / décoche une tâche."""
    todo = Todo.objects.get(pk=todo_id)
    todo.done = not todo.done
    todo.save()
    return _all_todos()
