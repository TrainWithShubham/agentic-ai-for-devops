import json

import pytest
from fastmcp import Client

from runbookops.agent import Engine
from runbookops.mcp_server import create_server
from runbookops.rag import Retriever, extract
from runbookops.security import principal
from runbookops.store import Store
from runbookops.tools import Tools


@pytest.mark.parametrize(
    "filename,term",
    [
        ("change-policy.pdf", "Jethalal"),
        ("incident-042.docx", "9009"),
        ("architecture.pptx", "9000"),
        ("checkout-runbook.md", "PAYMENT_SERVICE_URL"),
        ("support-notes.txt", "Bagha"),
    ],
)
def test_format_extraction(settings, filename, term):
    sections = extract(settings.root / "resources/company-knowledge" / filename)
    assert term in "\n".join(text for _, text in sections)
    assert all(location for location, _ in sections)


def test_retrieval_filters_before_model_context_and_cache(settings):
    retriever = Retriever(settings)
    query = "INTERNAL_APPROVER_MARKER_GADA_27 restricted operations"
    privileged = retriever.search(query, principal("jethalal"))
    assert any(r["source"] == "restricted-operations" for r in privileged["results"])
    viewer = retriever.search(query, principal("bagha"))
    assert "INTERNAL_APPROVER_MARKER_GADA_27" not in json.dumps(viewer)
    cached = retriever.search(query, principal("bagha"))
    assert cached["cache_hit"]
    assert "INTERNAL_APPROVER_MARKER_GADA_27" not in json.dumps(cached)
    current = retriever.search("old checkout payment port 8080", principal("bagha"))
    assert all(r["current"] for r in current["results"])


def test_tool_cannot_prepare_without_current_evidence(settings):
    store = Store(settings)
    actor = principal("bagha")
    case = store.create_incident(actor)
    tools = Tools(store, Retriever(settings), actor, case["id"])
    with pytest.raises(Exception, match="Inspect health"):
        tools.call(
            "prepare_change",
            {
                "service": "checkout",
                "key": "PAYMENT_SERVICE_URL",
                "value": "http://payments:9000",
                "evidence": ["checkout-runbook"],
            },
        )
    with pytest.raises(Exception, match="allowlist"):
        tools.call("apply_approved_change", {})
    store.close()


async def test_actual_mcp_protocol_discovery_and_invalid_target(settings):
    store = Store(settings)
    actor = principal("bagha")
    case = store.create_incident(actor)
    server, server_store = create_server(settings, actor)
    async with Client(server) as client:
        names = {item.name for item in await client.list_tools()}
        assert "search_runbooks" in names and "apply_approved_change" not in names
        result = await client.call_tool(
            "get_service_health", {"incident_id": case["id"], "service": "checkout"}
        )
        assert result.data["http_status"] == 503
        with pytest.raises(Exception):
            await client.call_tool("get_service_health", {"incident_id": case["id"], "service": "billing"})
    server_store.close()
    store.close()


async def test_stdio_mcp_subprocess(settings):
    app = Engine(settings, "stdio")
    try:
        state = await app.start(
            principal("bagha"), "Investigate checkout and prepare the documented correction."
        )
        assert state["proposal_id"]
        assert state["health"]["http_status"] == 503
    finally:
        app.close()
