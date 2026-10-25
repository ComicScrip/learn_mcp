"""Petit client MCP pour voir ce que voit un hôte (Claude, VS Code...).

    python try_client.py      (avec le serveur lancé sur :8765)
"""

import asyncio
import json

from fastmcp import Client


async def main():
    async with Client("http://localhost:8765/mcp") as client:
        print("== Tools ==")
        for tool in await client.list_tools():
            print(f"- {tool.name}  _meta={json.dumps(tool.meta)}")

        print("\n== Ressources ==")
        for res in await client.list_resources():
            print(f"- {res.uri}  ({res.mime_type})")

        print("\n== Appel add_todo ==")
        result = await client.call_tool("add_todo", {"title": "Apprendre MCP Apps"})
        print(result.structured_content)


asyncio.run(main())
