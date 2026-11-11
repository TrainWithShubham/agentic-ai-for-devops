"""Discover and call a tool through a local stdio MCP server."""

import asyncio

from runbookops.agent import tool_client
from runbookops.config import Settings
from runbookops.security import principal
from runbookops.store import open_store


async def main():
    settings = Settings.load()
    actor = principal("bagha")
    store = open_store(settings)
    case = store.create_incident(actor)
    async with tool_client(settings, actor, "stdio") as client:
        print("Discovered tools:", [tool.name for tool in await client.list_tools()])
        result = await client.call_tool(
            "get_service_health", {"incident_id": case["id"], "service": "checkout"}
        )
        print("MCP result:", result.data)
    store.close()


if __name__ == "__main__":
    asyncio.run(main())
