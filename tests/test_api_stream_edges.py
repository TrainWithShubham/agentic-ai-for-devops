import asyncio
import dataclasses
import json
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient

from runbookops import api
from runbookops.auth import Auth
from runbookops.security import principal
from runbookops.ui import Investigation


def test_api_invocations_resume_and_missing_identifiers(settings, monkeypatch):
    monkeypatch.setattr(api.Settings, "load", lambda: settings)
    app = api.create_app()
    with TestClient(app) as client:
        headers = {"Authorization": "Bearer " + app.state.auth.issue("jethalal")}
        assert client.get("/me", headers=headers).json()["role"] == "approver"
        monkeypatch.setenv("RUNBOOKOPS_CLOUD", "true")
        cloud = {"X-RunbookOps-Token": app.state.auth.issue("jethalal")}
        assert client.get("/me", headers=cloud).status_code == 200
        state = client.post(
            "/invocations", headers=headers, json={"operation": "investigate", "question": "Checkout down"}
        ).json()
        incident = state["incident_id"]
        p = state["proposal"]
        assert (
            client.post(
                "/invocations", headers=headers, json={"operation": "status", "incident_id": incident}
            ).json()["proposal_id"]
            == p["id"]
        )
        for op in ("status", "resume", "decide"):
            assert client.post("/invocations", headers=headers, json={"operation": op}).status_code == 422
        assert (
            client.post(
                "/invocations",
                headers=headers,
                json={
                    "operation": "decide",
                    "proposal_id": p["id"],
                    "expected_hash": p["hash"],
                    "approve": False,
                },
            ).json()["health"]["http_status"]
            == 503
        )
        assert (
            client.post(
                "/invocations", headers=headers, json={"operation": "resume", "incident_id": incident}
            ).status_code
            == 200
        )
        assert client.post("/incidents/" + incident + "/resume", headers=headers).status_code == 200


def test_external_issuer_metadata_is_not_republished(settings):
    auth = Auth(settings)
    app = api.create_app(dataclasses.replace(settings, oidc_issuer=auth.issuer, oidc_public_key=auth.public))
    with TestClient(app) as client:
        assert client.get("/oidc/.well-known/openid-configuration").status_code == 404
        assert client.get("/oidc/jwks.json").status_code == 404


def test_cloud_factory_guards_configuration(settings, monkeypatch):
    monkeypatch.delenv("RUNBOOKOPS_CLOUD", raising=False)
    sentinel = object()
    monkeypatch.setattr(api, "create_app", lambda: sentinel)
    assert api.app_factory() is sentinel
    monkeypatch.setenv("RUNBOOKOPS_CLOUD", "true")
    for name in (
        "RUNBOOKOPS_DATABASE_URL",
        "RUNBOOKOPS_OIDC_ISSUER",
        "RUNBOOKOPS_DYNAMODB_TABLE",
        "RUNBOOKOPS_CHECKPOINT_TABLE",
    ):
        monkeypatch.delenv(name, raising=False)
    import pytest

    with pytest.raises(RuntimeError):
        api.app_factory()
    monkeypatch.setenv("RUNBOOKOPS_DATABASE_URL", "postgresql://test")
    with pytest.raises(RuntimeError):
        api.app_factory()
    monkeypatch.setenv("RUNBOOKOPS_OIDC_ISSUER", "https://issuer.example")
    assert api.app_factory() is sentinel
    monkeypatch.delenv("RUNBOOKOPS_DATABASE_URL")
    monkeypatch.setenv("RUNBOOKOPS_DYNAMODB_TABLE", "state")
    with pytest.raises(RuntimeError):
        api.app_factory()
    monkeypatch.setenv("RUNBOOKOPS_CHECKPOINT_TABLE", "checkpoints")
    assert api.app_factory() is sentinel


def test_mcp_discovery_failure_is_clean(settings, monkeypatch):
    import runbookops.ui as ui

    @asynccontextmanager
    async def unavailable(*a):
        raise RuntimeError("private-password=secret")
        yield

    monkeypatch.setattr(ui, "tool_client", unavailable)
    app = api.create_app(settings)
    with TestClient(app) as client:
        headers = {"Authorization": "Bearer " + app.state.auth.issue("bagha")}
        response = client.get("/harness/mcp", headers=headers)
        assert response.status_code == 503 and "private-password" not in response.text


async def test_slow_stream_announces_incident_once_and_completes(settings):
    app = api.create_app(settings)
    engine = app.state.engine

    async def slow(*a, **kw):
        await asyncio.sleep(0.95)
        return {"role": "assistant", "content": "No fix requested"}, {"mode": "test"}

    engine.model.complete = slow
    endpoint = next(route.endpoint for route in app.routes if route.path == "/investigations/stream")
    response = await endpoint(Investigation(question="Check checkout"), principal("bagha"))
    rows = [json.loads(row) async for row in response.body_iterator]
    assert sum(r["type"] == "incident" for r in rows) == 1
    assert rows[-1]["type"] == "complete"
    engine.close()


async def test_stream_failure_before_incident_and_cancel_before_creation(settings):
    app = api.create_app(settings)
    engine = app.state.engine
    endpoint = next(route.endpoint for route in app.routes if route.path == "/investigations/stream")

    async def failing(*a, **kw):
        raise ValueError("Cannot start this investigation")

    engine.start = failing
    response = await endpoint(Investigation(question="Check"), principal("bagha"))
    rows = [json.loads(row) async for row in response.body_iterator]
    assert rows[-1]["type"] == "error" and "Cannot start" in rows[-1]["data"]["message"]

    async def unstarted(*a, **kw):
        await asyncio.sleep(60)

    engine.start = unstarted
    response = await endpoint(Investigation(question="Check"), principal("bagha"))
    iterator = response.body_iterator
    assert json.loads(await anext(iterator))["type"] == "connected"
    await iterator.aclose()
    engine.close()


def test_local_discovery_publishes_public_jwks(settings):
    app = api.create_app(settings)
    with TestClient(app) as client:
        discovery = client.get("/oidc/.well-known/openid-configuration").json()
        assert discovery["jwks_uri"].endswith("/jwks.json")
        keys = client.get("/oidc/jwks.json").json()["keys"]
        assert keys[0]["kty"] == "RSA" and "d" not in keys[0]
