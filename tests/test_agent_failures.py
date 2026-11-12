import dataclasses
from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest

from runbookops import agent
from runbookops.agent import Engine, tool_client
from runbookops.models import tool_call
from runbookops.rag import Retriever
from runbookops.security import Denied, InvalidChange, principal
from runbookops.store import Store
from runbookops.tools import MAX_TOOL_STEPS, Tools


@pytest.mark.parametrize(
    "fault",
    [
        "no-tools",
        "unknown-tool",
        "invalid-input",
        "wrong-result",
        "too-many-tools",
        "timeout",
        "empty-response",
    ],
)
async def test_agent_failures_stop_without_change(settings, monkeypatch, fault):
    engine = Engine(settings)

    class Client:
        async def list_tools(self):
            return (
                []
                if fault == "no-tools"
                else [SimpleNamespace(name=t["function"]["name"]) for t in agent.SCHEMAS]
            )

        async def call_tool(self, *a, **kw):
            return SimpleNamespace(data=["wrong-shape"])

    @asynccontextmanager
    async def transport(*a):
        yield Client()

    monkeypatch.setattr(agent, "tool_client", transport)
    count = 0

    async def reply(*a, **kw):
        nonlocal count
        count += 1
        if fault == "timeout":
            raise TimeoutError
        calls = []
        if count == 1 and fault != "empty-response":
            name = "not_allowed" if fault == "unknown-tool" else "get_service_health"
            args = {"service": "billing"} if fault == "invalid-input" else {"service": "checkout"}
            calls = [tool_call(name, args, i) for i in range(17 if fault == "too-many-tools" else 1)]
        return {"role": "assistant", "content": None, "tool_calls": calls}, {"mode": "test"}

    engine.model.complete = reply
    state = await engine.start(principal("bagha"), "Check checkout")
    assert state["health"]["http_status"] == 503 and not state.get("proposal_id")
    if fault in ("no-tools", "too-many-tools", "timeout"):
        assert state["error"]
    if fault == "empty-response":
        assert state["diagnosis"] == "No diagnosis returned."
    if fault in ("invalid-input", "wrong-result"):
        assert any(
            e["kind"] == "tool_error" for e in engine.store.events(state["incident_id"], principal("bagha"))
        )
    engine.close()


async def test_remote_mcp_token_required_and_client_wiring(settings, monkeypatch):
    remote = dataclasses.replace(settings, mcp_url="http://127.0.0.1:8888/mcp")
    with pytest.raises(Denied):
        async with tool_client(remote, principal("bagha"), "inprocess"):
            pass
    seen = []

    class Remote:
        def __init__(self, url, auth):
            seen.append((url, auth))

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            pass

    monkeypatch.setattr(agent, "Client", Remote)
    async with tool_client(
        dataclasses.replace(remote, mcp_token="test-token"), principal("bagha"), "inprocess"
    ) as client:
        assert isinstance(client, Remote)
    assert seen == [(remote.mcp_url, "test-token")]


async def test_resume_guards_and_missing_proposal_denial(settings, monkeypatch):
    engine = Engine(settings)
    for question in ("", "x" * 1201):
        with pytest.raises(ValueError):
            await engine.start(principal("bagha"), question)
    with pytest.raises(Denied):
        await engine.decide("does-not-exist", principal("bagha"), "0" * 64, True)

    async def no_tools(*a, **kw):
        return {"role": "assistant", "content": "No fix"}, {"mode": "test"}

    engine.model.complete = no_tools
    state = await engine.start(principal("bagha"), "Check")
    with pytest.raises(InvalidChange):
        await engine.resume(state["incident_id"], principal("jethalal"))
    engine = Engine(settings)
    state = await engine.start(principal("bagha"), "Check")
    with pytest.raises(Denied):
        await engine.resume(state["incident_id"], principal("jethalal"))
    engine.store.decide(state["proposal"]["id"], principal("jethalal"), state["proposal"]["hash"], False)
    done = await engine.resume(state["incident_id"], principal("jethalal"))
    assert not done["result"]["applied"] and done["health"]["http_status"] == 503
    assert not (await engine.resume(state["incident_id"], principal("jethalal")))["pending_nodes"]
    engine.close()


async def test_postgres_checkpoint_adapter_setup(settings, monkeypatch):
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

    engine = Engine(settings)
    engine.settings = dataclasses.replace(settings, database_url="postgresql://contract")
    saver = InMemorySaver()
    calls = []

    async def setup():
        calls.append("setup")

    saver.setup = setup

    @asynccontextmanager
    async def factory(dsn):
        assert dsn == "postgresql://contract"
        yield saver

    monkeypatch.setattr(AsyncPostgresSaver, "from_conn_string", factory)
    async with engine.graph(principal("bagha")) as graph:
        assert graph.get_graph().nodes and calls == ["setup"]
    engine.close()


def test_tool_budget_and_evidence_guards(settings):
    store = Store(settings)
    actor = principal("bagha")
    incident = store.create_incident(actor)["id"]
    tools = Tools(store, Retriever(settings), actor, incident)
    args = {
        "service": "checkout",
        "key": "PAYMENT_SERVICE_URL",
        "value": "http://payments:9000",
        "evidence": ["checkout-runbook"],
    }
    tools.observed = {"get_service_health", "get_recent_logs", "get_recent_deployments"}
    with pytest.raises(InvalidChange, match="Retrieve the current"):
        tools.call("prepare_change", args)
    tools.sources = {"checkout-runbook"}
    with pytest.raises(InvalidChange, match="not retrieved"):
        tools.call("prepare_change", {**args, "evidence": ["architecture"]})
    tools.steps = MAX_TOOL_STEPS
    with pytest.raises(InvalidChange, match="budget"):
        tools.call("get_service_health", {"service": "checkout"})
    store.close()


@pytest.mark.parametrize("request_fix", [False, True])
async def test_completion_reminder_for_missing_checks_is_bounded(settings, request_fix):
    engine = Engine(settings)
    calls = []

    async def reply(messages, *args, **kwargs):
        calls.append(messages.copy())
        if len(calls) == 1:
            return {
                "role": "assistant",
                "tool_calls": [tool_call("get_service_health", {"service": "checkout"}, 1)],
            }, {"mode": "test"}
        return {"role": "assistant", "content": "Partial diagnosis"}, {"mode": "test"}

    engine.model.complete = reply
    state = await engine.start(principal("bagha"), "Suggest a fix" if request_fix else "Check checkout")
    assert state["model_calls"] == 3 and not state.get("proposal_id")
    assert sum("Check completion" in str(m) for m in calls[-1]) == 1
    assert state["health"]["http_status"] == 503
    engine.close()


@pytest.mark.parametrize("request_fix", [False, True])
async def test_completion_checks_distinguish_finding_from_requested_fix(settings, request_fix):
    engine = Engine(settings)
    calls = []

    async def reply(messages, *args, **kwargs):
        calls.append(messages.copy())
        if len(calls) == 1:
            tools = [
                tool_call(name, {"service": "checkout"}, i)
                for i, name in enumerate(["get_service_health", "get_recent_logs", "get_recent_deployments"])
            ]
            tools.append(
                tool_call("search_runbooks", {"query": "checkout runbook payment URL correction"}, 3)
            )
            return {"role": "assistant", "tool_calls": tools}, {"mode": "test"}
        if len(calls) == 3:
            return {
                "role": "assistant",
                "tool_calls": [
                    tool_call(
                        "prepare_change",
                        {
                            "service": "checkout",
                            "key": "PAYMENT_SERVICE_URL",
                            "value": "http://payments:9000",
                            "evidence": [
                                "checkout-runbook",
                                "get_service_health",
                                "get_recent_logs",
                                "get_recent_deployments",
                            ],
                        },
                        4,
                    )
                ],
            }, {"mode": "test"}
        return {"role": "assistant", "content": "Checkout cannot connect to payments."}, {"mode": "test"}

    engine.model.complete = reply
    state = await engine.start(principal("bagha"), "Suggest a fix" if request_fix else "Check checkout")
    assert bool(state.get("proposal_id")) == request_fix
    assert state["model_calls"] == (3 if request_fix else 2)
    assert state["health"]["http_status"] == 503
    engine.close()


async def test_missing_runbook_can_be_retrieved_after_blocked_proposal(settings, monkeypatch):
    engine = Engine(settings)
    search = Retriever.search
    attempts = []

    def first_missing(self, query, actor, limit=5):
        attempts.append(query)
        if len(attempts) == 1:
            return {
                "results": [{"source": "architecture", "text": "The payment service uses port 9000"}],
                "cache_hit": False,
            }
        return search(self, query, actor, limit)

    monkeypatch.setattr(Retriever, "search", first_missing)
    turn = 0
    arguments = {
        "service": "checkout",
        "key": "PAYMENT_SERVICE_URL",
        "value": "http://payments:9000",
        "evidence": ["checkout-runbook", "get_service_health", "get_recent_logs", "get_recent_deployments"],
    }

    async def reply(messages, *args, **kwargs):
        nonlocal turn
        turn += 1
        if turn == 1:
            reads = [
                tool_call(name, {"service": "checkout"}, i)
                for i, name in enumerate(["get_service_health", "get_recent_logs", "get_recent_deployments"])
            ]
            reads.append(tool_call("search_runbooks", {"query": "company architecture"}, 3))
            return {"role": "assistant", "tool_calls": reads}, {"mode": "test"}
        if turn == 3:
            assert "next_step" in messages[-1]["content"]
            assert "current checkout-runbook" in messages[-1]["content"]
            return {
                "role": "assistant",
                "tool_calls": [
                    tool_call(
                        "search_runbooks", {"query": "checkout runbook payment URL correction approval"}, 5
                    )
                ],
            }, {"mode": "test"}
        return {"role": "assistant", "tool_calls": [tool_call("prepare_change", arguments, 6)]}, {
            "mode": "test"
        }

    engine.model.complete = reply
    state = await engine.start(principal("bagha"), "Suggest a fix")
    assert state["proposal"]["status"] == "pending" and state["health"]["http_status"] == 503
    assert len(attempts) == 2 and state["model_calls"] == 4
    assert any(
        e["kind"] == "tool_error" for e in engine.store.events(state["incident_id"], principal("bagha"))
    )
    engine.close()
