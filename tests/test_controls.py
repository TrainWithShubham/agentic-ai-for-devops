import json
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from runbookops.agent import Engine
from runbookops.auth import Auth
from runbookops.security import Denied, InvalidChange, principal, redact
from runbookops.store import GOOD_URL, Store


def proposal(store):
    actor = principal("bagha")
    incident = store.create_incident(actor)["id"]
    return store.prepare(incident, actor, "checkout", "PAYMENT_SERVICE_URL", GOOD_URL, ["checkout-runbook"])


def test_permissions_expiry_integrity_and_replay(settings):
    store = Store(settings)
    p = proposal(store)
    with pytest.raises(Denied):
        store.decide(p["id"], principal("bagha"), p["hash"], True)
    with pytest.raises(Denied):
        store.apply(p["id"], principal("bagha"))
    with pytest.raises(InvalidChange):
        store.decide(p["id"], principal("jethalal"), "0" * 64, True)
    store.execute("UPDATE proposals SET expires=? WHERE id=?", (time.time() - 1, p["id"]))
    with pytest.raises(InvalidChange):
        store.decide(p["id"], principal("jethalal"), p["hash"], True)
    assert store.health(p["incident"], principal("bagha"))["http_status"] == 503
    store.close()


def test_tampered_payload_and_changed_service_rejected(settings):
    store = Store(settings)
    p = proposal(store)
    changed = dict(p["plan"], after="http://attacker.invalid")
    store.execute("UPDATE proposals SET plan=? WHERE id=?", (json.dumps(changed), p["id"]))
    with pytest.raises(InvalidChange):
        store.decide(p["id"], principal("jethalal"), p["hash"], True)
    p = proposal(store)
    store.execute("UPDATE incidents SET revision=revision+1 WHERE id=?", (p["incident"],))
    with pytest.raises(InvalidChange):
        store.decide(p["id"], principal("jethalal"), p["hash"], True)
    store.close()


def test_incident_isolation_and_allowlist(settings):
    store = Store(settings)
    p = proposal(store)
    with pytest.raises(Denied):
        store.incident(p["incident"], principal("nattu"))
    with pytest.raises(InvalidChange):
        store.prepare(
            p["incident"], principal("bagha"), "checkout", "PAYMENT_SERVICE_URL", "http://other", ["source"]
        )
    store.close()


def test_concurrent_execution_applies_once(settings):
    store = Store(settings)
    p = proposal(store)
    store.decide(p["id"], principal("jethalal"), p["hash"], True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: store.apply(p["id"], principal("bagha")), range(4)))
    assert sum(r["applied"] for r in results) == 1
    assert store.health(p["incident"], principal("bagha"))["revision"] == 2
    store.close()


def test_jwt_claims_do_not_override_roles(settings):
    auth = Auth(settings)
    token = auth.issue("bagha")
    assert auth.verify(token).role == "viewer"
    with pytest.raises(Denied):
        auth.issue("bagha", ["approve"])
    with pytest.raises(Denied):
        auth.verify(auth.issue("bagha", expires=-1))
    with pytest.raises(Denied):
        auth.verify(auth.issue("jethalal", audience="another-service"))
    assert "read" not in auth.verify(auth.issue("bagha", scopes=[])).scopes
    damaged = token[:-10] + "invalidsig"
    with pytest.raises(Denied):
        auth.verify(damaged)


def test_redaction_preserves_usage_not_secrets():
    data = redact(
        {
            "api_key": "example",
            "authorization": "Bearer abc",
            "total_tokens": 24,
            "message": "API_KEY=sk-or-v1-secret-should-not-leak Bearer other",
        }
    )
    assert data["total_tokens"] == 24
    assert "should-not-leak" not in json.dumps(data)
    assert data["api_key"] == "[redacted]"


async def test_process_restart_rejection_and_complete_flow(settings):
    app = Engine(settings)
    state = await app.start(principal("bagha"), "Investigate checkout and prepare a fix for approval.")
    assert state["waiting_for_approval"] and state["health"]["http_status"] == 503
    p = state["proposal"]
    app.close()
    app = Engine(settings)
    state = await app.decide(p["id"], principal("jethalal"), p["hash"], True)
    assert state["health"]["http_status"] == 200
    assert state["result"]["applied"]
    with pytest.raises(InvalidChange):
        await app.decide(p["id"], principal("jethalal"), p["hash"], True)
    assert app.store.apply(p["id"], principal("bagha"))["idempotent_replay"]
    events = app.store.events(state["incident_id"], principal("bagha"))
    assert any(event["kind"] == "mcp_connected" for event in events)
    assert any(event["kind"] == "verification" for event in events)
    assert "sk-test" not in json.dumps(events)
    app.close()


async def test_model_cannot_resume_without_a_stored_decision(settings):
    from langgraph.types import Command

    app = Engine(settings)
    state = await app.start(principal("bagha"), "Investigate checkout and prepare a fix.")
    with pytest.raises(Denied):
        async with app.graph(principal("bagha")) as graph:
            await graph.ainvoke(
                Command(resume={"approved": True, "actor": "jethalal"}), app.config(state["incident_id"])
            )
    assert app.store.health(state["incident_id"], principal("bagha"))["http_status"] == 503
    app.close()


async def test_bounded_model_loop(settings):
    from runbookops.models import tool_call

    app = Engine(settings)

    async def repeated(*args, **kwargs):
        return {
            "role": "assistant",
            "tool_calls": [tool_call("get_service_health", {"service": "checkout"}, 1)],
        }, {"mode": "test"}

    app.model.complete = repeated
    state = await app.start(principal("bagha"), "Investigate checkout.")
    assert state["model_calls"] == settings.max_calls
    assert "budget" in state["error"]
    assert state["health"]["http_status"] == 503
    app.close()


async def test_resume_after_executor_crashes_after_applying(settings):
    app = Engine(settings)
    state = await app.start(principal("bagha"), "Investigate checkout and prepare a correction.")
    proposal = state["proposal"]
    app.store.decide(proposal["id"], principal("jethalal"), proposal["hash"], True)
    original = app.store.apply

    def crash_after_apply(*args):
        original(*args)
        raise RuntimeError("Simulated process death after committed effect")

    app.store.apply = crash_after_apply
    with pytest.raises(RuntimeError, match="Simulated process death"):
        await app.resume(state["incident_id"], principal("jethalal"))
    app.close()
    app = Engine(settings)
    recovered = await app.resume(state["incident_id"], principal("jethalal"))
    assert recovered["health"]["revision"] == 2
    assert recovered["health"]["http_status"] == 200
    assert recovered["result"]["idempotent_replay"]
    assert not recovered["pending_nodes"]
    app.close()


def test_external_issuer_from_env_file_uses_public_key_only(settings, tmp_path, monkeypatch):
    from runbookops.config import Settings

    local = Auth(settings)
    env = tmp_path / ".env"
    escaped_public = local.public.replace("\n", "\\n")
    env.write_text(
        f'RUNBOOKOPS_OIDC_ISSUER="{local.issuer}"\n'
        'RUNBOOKOPS_OIDC_AUDIENCE="runbookops"\n'
        f'RUNBOOKOPS_OIDC_PUBLIC_KEY="{escaped_public}"\n'
    )
    # Project .env must configure trust; --env-file imports model settings only.
    monkeypatch.chdir(tmp_path)
    configured = Settings.load(root=settings.root, data=tmp_path / "external")
    external = Auth(configured)
    assert external.external
    assert external.verify(local.issue("bagha")).role == "viewer"
    assert not external.key_path.exists()
    with pytest.raises(Denied, match="external issuer"):
        external.issue("jethalal")
