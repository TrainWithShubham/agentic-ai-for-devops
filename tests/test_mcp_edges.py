import os
import runpy
import socket
import subprocess
import sys
import time
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from fastmcp import Client

from runbookops import mcp_server
from runbookops.auth import Auth
from runbookops.security import principal
from runbookops.store import Store


async def test_verified_mcp_context_uses_token_identity(settings, monkeypatch):
    from fastmcp.server import dependencies

    store = Store(settings)
    incident = store.create_incident(principal("bagha"))["id"]
    server, server_store = mcp_server.create_server(settings)
    monkeypatch.setattr(
        dependencies,
        "get_access_token",
        lambda: SimpleNamespace(claims={"sub": "bagha"}, scopes=["read", "investigate"]),
    )
    async with Client(server) as client:
        health = await client.call_tool(
            "get_service_health", {"incident_id": incident, "service": "checkout"}
        )
        assert health.data["http_status"] == 503
    server_store.close()
    store.close()


@pytest.mark.parametrize("transport", ["stdio", "http"])
def test_mcp_entrypoint_transport_and_close(settings, monkeypatch, transport):
    runner = Mock()
    store = Mock()
    monkeypatch.setattr(mcp_server.Settings, "load", lambda: settings)
    monkeypatch.setattr(mcp_server, "create_server", lambda *a: (SimpleNamespace(run=runner), store))
    monkeypatch.setattr(sys, "argv", ["mcp", "--transport", transport, "--port", "8123"])
    mcp_server.main()
    assert runner.call_args.kwargs["transport"] == transport
    store.close.assert_called_once()


def test_mcp_module_entrypoint(settings, monkeypatch):
    # Executing the module is a real entrypoint check; replace only server.run so no blocking listener remains.
    from fastmcp import FastMCP

    monkeypatch.setattr(mcp_server.Settings, "load", lambda: settings)
    monkeypatch.setattr(FastMCP, "run", lambda *a, **kw: None)
    monkeypatch.setattr(sys, "argv", ["mcp", "--transport", "stdio"])
    monkeypatch.delitem(sys.modules, "runbookops.mcp_server", raising=False)
    runpy.run_module("runbookops.mcp_server", run_name="__main__")


async def test_actual_http_mcp_auth_and_tool_protocol(settings):
    # A separate process verifies HTTP transport and JWT admission rather than bypassing auth in memory.
    auth = Auth(settings)
    store = Store(settings)
    incident = store.create_incident(principal("bagha"))["id"]
    store.close()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = {
        **os.environ,
        "RUNBOOKOPS_ROOT": str(settings.root),
        "RUNBOOKOPS_DATA": str(settings.data),
        "RUNBOOKOPS_MODE": "offline",
        "RUNBOOKOPS_EMBEDDING": "hash",
    }
    for name in (
        "RUNBOOKOPS_OIDC_ISSUER",
        "RUNBOOKOPS_CLOUD",
        "RUNBOOKOPS_MCP_URL",
        "RUNBOOKOPS_DYNAMODB_TABLE",
        "RUNBOOKOPS_CHECKPOINT_TABLE",
    ):
        env.pop(name, None)
    log = (settings.data / "mcp-http.log").open("wb")
    process = subprocess.Popen(
        [sys.executable, "-m", "runbookops.mcp_server", "--transport", "http", "--port", str(port)],
        cwd=settings.root,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    try:
        url = f"http://127.0.0.1:{port}/mcp"
        for _ in range(100):
            try:
                httpx.get(url, timeout=0.2)
                break
            except httpx.TransportError:
                time.sleep(0.05)
        else:
            raise AssertionError("MCP server did not start")
        async with Client(url, auth=auth.issue("bagha")) as client:
            names = {tool.name for tool in await client.list_tools()}
            assert "get_service_health" in names
            result = await client.call_tool(
                "get_service_health", {"incident_id": incident, "service": "checkout"}
            )
            assert result.data["http_status"] == 503
        async with Client(url, auth=auth.issue("nattu")) as client:
            with pytest.raises(Exception):
                await client.call_tool("get_service_health", {"incident_id": incident, "service": "checkout"})
        with pytest.raises(Exception):
            async with Client(url, auth="invalid-access-token") as client:
                await client.list_tools()
    finally:
        process.terminate()
        process.wait(timeout=10)
        log.close()
