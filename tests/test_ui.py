import dataclasses
import json

from fastapi.testclient import TestClient

from runbookops.api import create_app
from runbookops.auth import Auth


def test_ui_assets_and_no_implicit_persona_issuance(settings):
    app = create_app(settings)
    with TestClient(app) as client:
        page = client.get("/")
        assert page.status_code == 200
        assert "Agent harness" in page.text
        assert "frame-ancestors 'none'" in page.headers["Content-Security-Policy"]
        assert client.get("/assets/app.js").status_code == 200
        assert client.get("/assets/fonts/manrope-0.woff2").status_code == 200
        assert client.get("/ui/config").json()["demo_auth"] is False
        assert client.post("/ui/session", json={"user": "jethalal"}).status_code == 404
        assert client.get("/knowledge").status_code == 401


def test_persona_login_is_explicit_loopback_and_same_origin(settings):
    app = create_app(dataclasses.replace(settings, ui_demo_auth=True))
    headers = {"X-RunbookOps-Demo": "true", "Origin": "http://127.0.0.1"}
    with TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        assert client.get("/ui/config").json()["demo_auth"] is True
        assert client.post("/ui/session", json={"user": "bagha"}).status_code == 403
        assert (
            client.post(
                "/ui/session", headers={**headers, "Origin": "https://example.org"}, json={"user": "jethalal"}
            ).status_code
            == 403
        )
        result = client.post("/ui/session", headers=headers, json={"user": "bagha"})
        assert result.status_code == 200
        assert result.headers["cache-control"] == "no-store"
        body = result.json()
        actor = app.state.auth.verify(body["access_token"])
        assert actor.role == "viewer"
        assert "approve" not in actor.scopes
        assert (
            client.post(
                "/ui/session", headers=headers, json={"user": "bagha", "role": "approver"}
            ).status_code
            == 422
        )
    with TestClient(app, base_url="http://evil.example", client=("127.0.0.1", 50000)) as client:
        assert client.get("/ui/config").json()["demo_auth"] is False
        assert (
            client.post(
                "/ui/session", headers={"X-RunbookOps-Demo": "true"}, json={"user": "jethalal"}
            ).status_code
            == 403
        )
    with TestClient(app, base_url="http://127.0.0.1", client=("10.0.0.5", 50000)) as client:
        assert client.post("/ui/session", headers=headers, json={"user": "bagha"}).status_code == 403


def test_cloud_and_external_issuer_cannot_enable_persona_issuance(settings, monkeypatch):
    local = Auth(settings)
    external = dataclasses.replace(
        settings, ui_demo_auth=True, oidc_issuer=local.issuer, oidc_public_key=local.public
    )
    with TestClient(create_app(external)) as client:
        assert client.get("/ui/config").json()["demo_auth"] is False
        assert client.post("/ui/session", json={"user": "jethalal"}).status_code == 404
    monkeypatch.setenv("RUNBOOKOPS_CLOUD", "true")
    with TestClient(create_app(dataclasses.replace(settings, ui_demo_auth=True))) as client:
        assert client.get("/ui/config").json()["demo_auth"] is False
        assert client.post("/ui/session", json={"user": "jethalal"}).status_code == 404


def test_knowledge_content_and_search_enforce_roles(settings):
    app = create_app(settings)
    bagha = {"Authorization": "Bearer " + app.state.auth.issue("bagha")}
    approver = {"Authorization": "Bearer " + app.state.auth.issue("jethalal")}
    with TestClient(app) as client:
        sources = client.get("/knowledge", headers=bagha).json()["sources"]
        assert all(s["current"] and s["access"] == "public" for s in sources)
        restricted = "/knowledge/restricted-operations"
        assert client.get(restricted, headers=approver).status_code == 200
        assert client.get(restricted, headers=bagha).status_code == 403
        assert client.get("/knowledge/checkout-runbook-old", headers=approver).status_code == 403
        assert client.get("/knowledge/not-a-source", headers=bagha).status_code == 403
        doc = client.get("/knowledge/architecture", headers=bagha).json()
        assert any("payments:9000" in section["text"] for section in doc["sections"])
        answer = client.post(
            "/knowledge/search", headers=bagha, json={"question": "payment checkout connection endpoint"}
        ).json()
        assert answer["results"]
        assert "INTERNAL_APPROVER_MARKER" not in json.dumps(answer)


def test_stream_records_real_events_and_keeps_approval_boundary(settings):
    app = create_app(settings)
    auth = app.state.auth
    bagha = {"Authorization": "Bearer " + auth.issue("bagha")}
    nattu = {"Authorization": "Bearer " + auth.issue("nattu")}
    approver = {"Authorization": "Bearer " + auth.issue("jethalal")}
    with TestClient(app) as client:
        assert client.post("/investigations/stream", json={"question": "Investigate."}).status_code == 401
        result = client.post(
            "/investigations/stream",
            headers=bagha,
            json={"question": "Investigate checkout 503 and prepare a fix."},
        )
        assert result.status_code == 200
        rows = [json.loads(line) for line in result.text.splitlines()]
        assert rows[0]["type"] == "connected"
        assert any(row["type"] == "event" and row["data"]["kind"] == "tool" for row in rows)
        state = rows[-1]["data"]
        assert rows[-1]["type"] == "complete" and state["health"]["http_status"] == 503
        assert state["waiting_for_approval"]
        proposal = state["proposal"]
        request = {"expected_hash": proposal["hash"], "approve": True}
        path = f"/proposals/{proposal['id']}/decision"
        assert client.post(path, headers=bagha, json=request).status_code == 403
        assert client.get(f"/incidents/{state['incident_id']}", headers=nattu).status_code == 403
        done = client.post(path, headers=approver, json=request)
        assert done.status_code == 200 and done.json()["health"]["http_status"] == 200
        assert "sk-test" not in result.text


async def test_disconnecting_stream_cancels_readonly_investigation(settings):
    import asyncio

    from runbookops.security import principal
    from runbookops.ui import Investigation

    app = create_app(settings)
    engine = app.state.engine

    async def slow(*args, **kwargs):
        await asyncio.sleep(60)

    engine.model.complete = slow
    endpoint = next(route.endpoint for route in app.routes if route.path == "/investigations/stream")
    response = await endpoint(Investigation(question="Investigate checkout."), principal("bagha"))
    iterator = response.body_iterator
    assert json.loads(await anext(iterator))["type"] == "connected"
    entry = json.loads(await anext(iterator))
    assert entry["type"] == "incident"
    incident = entry["data"]["incident_id"]
    await iterator.aclose()
    assert engine.store.health(incident, principal("bagha"))["http_status"] == 503
    assert any(
        event["kind"] == "investigation_cancelled"
        for event in engine.store.events(incident, principal("bagha"))
    )
    engine.close()


def test_harness_exposes_real_configuration_and_mcp_schemas(settings):
    from runbookops.models import SYSTEM
    from runbookops.tools import SCHEMAS

    app = create_app(settings)
    headers = {"Authorization": "Bearer " + app.state.auth.issue("bagha")}
    with TestClient(app) as client:
        assert client.get("/harness").status_code == 401
        assert client.get("/harness/mcp").status_code == 401
        harness = client.get("/harness", headers=headers).json()
        assert harness["system_prompt"] == SYSTEM
        assert harness["tools"] == SCHEMAS
        assert {node["id"] for node in harness["graph"]["nodes"]} >= {"investigate", "review", "execute"}
        assert harness["limits"]["model_calls"] == settings.max_calls
        assert harness["rag"]["chunk_characters"] == 900
        assert "api_key" not in json.dumps(harness).lower()
        discovered = client.get("/harness/mcp", headers=headers)
        assert discovered.status_code == 200
        tools = discovered.json()["tools"]
        assert {tool["name"] for tool in tools} == {tool["function"]["name"] for tool in SCHEMAS}
        assert all("incident_id" in tool["input_schema"]["properties"] for tool in tools)
        state = client.post(
            "/investigations", headers=headers, json={"question": "Investigate checkout 503."}
        ).json()
        events = client.get(f"/incidents/{state['incident_id']}/trace", headers=headers).json()["events"]
        model = next(event for event in events if event["kind"] == "model")
        assert model["requested_tools"]
        assert "reasoning" not in model
        assert any(event["kind"] == "model_request" for event in events)
        assert any(event["kind"] == "node_started" and event["node"] == "investigate" for event in events)
