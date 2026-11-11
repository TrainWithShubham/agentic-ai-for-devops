"""Call the optional HTTP MCP server using a development JWT, without displaying it."""

import asyncio

from fastmcp import Client

from runbookops.auth import Auth
from runbookops.config import Settings
from runbookops.security import principal
from runbookops.store import open_store


async def main():
    settings = Settings.load()
    actor = principal("bagha")
    store = open_store(settings)
    incident = store.create_incident(actor)
    token = Auth(settings).issue("bagha")
    async with Client("http://127.0.0.1:8001/mcp", auth=token) as client:
        result = await client.call_tool(
            "get_service_health", {"incident_id": incident["id"], "service": "checkout"}
        )
        assert result.data["http_status"] == 503
        print("Signed Bagha token accepted by remote MCP. Checkout HTTP 503 verified. Token not displayed.")
    store.close()


if __name__ == "__main__":
    asyncio.run(main())
