"""Discover and call tools through a real MCP subprocess, with no model involved."""

import asyncio
import sys

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from .common import ROOT, show


async def inspect():
    transport = StdioTransport(command=sys.executable, args=["-m", "course_labs.mcp_server"], cwd=str(ROOT))
    async with Client(transport, timeout=15) as client:
        tools = await client.list_tools()
        show(
            {
                "transport": "stdio",
                "model_called": False,
                "tools": [{"name": t.name, "input_schema": t.inputSchema} for t in tools],
            }
        )
        result = await client.call_tool("ci_read_log", {"run_id": 1042})
        show({"tool": "ci_read_log", "result": result.data})
        return {"names": sorted(t.name for t in tools), "log": result.data}


if __name__ == "__main__":
    asyncio.run(inspect())
