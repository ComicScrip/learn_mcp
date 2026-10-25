"""Point d'entrée ASGI : Django ET le serveur MCP dans le même process.

    /mcp   -> FastMCP (protocole MCP en "Streamable HTTP")
    /...   -> Django (API REST DRF)

Lancer avec :  uvicorn config.asgi:application --port 8765
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Django doit être initialisé AVANT d'importer du code qui touche aux modèles.
django_app = get_asgi_application()

from starlette.middleware import Middleware  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402

from todos.mcp_server import mcp  # noqa: E402

# App ASGI (Starlette) générée par FastMCP, qui répond sur /mcp.
mcp_app = mcp.http_app(
    path="/mcp",
    # CORS : nécessaire pour les hôtes de test qui tournent dans le navigateur
    # (ex. basic-host sur localhost:8080). Inutile pour Claude.
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:8080"],
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id"],
        )
    ],
)


async def application(scope, receive, send):
    # "lifespan" = démarrage/arrêt du serveur : FastMCP en a besoin
    # pour son gestionnaire de sessions (Django, lui, ne le gère pas).
    if scope["type"] == "lifespan" or scope["path"].startswith("/mcp"):
        await mcp_app(scope, receive, send)
    else:
        await django_app(scope, receive, send)
