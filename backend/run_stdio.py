"""Lance le serveur MCP en "stdio" pour Claude Desktop (serveur local).

Claude Desktop démarre lui-même ce script et lui parle via stdin/stdout :
pas besoin d'uvicorn, de port ni de tunnel.
"""

import os
import sys
from pathlib import Path

# Claude Desktop lance le script depuis un autre dossier : on se place dans backend/.
BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from todos.mcp_server import mcp  # noqa: E402

if __name__ == "__main__":
    mcp.run()  # transport stdio par défaut
