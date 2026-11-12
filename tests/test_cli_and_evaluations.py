import dataclasses
import json
import runpy
import sys
from unittest.mock import Mock

import httpx
import pytest

from runbookops import cli
from runbookops.agent import Engine
from runbookops.auth import Auth
from runbookops.evaluations import evaluate
from runbookops.models import ModelError
from runbookops.security import principal
from runbookops.store import Store


@pytest.fixture
def command(settings, monkeypatch):
    monkeypatch.setattr(cli.Settings, "load", lambda *a, **kw: settings)

    def parse(*args):
        return cli.parser().parse_args(args)

    return parse


async def test_cli_demo_and_incident_lifecycle(command, settings, capsys):
    report = await cli.demo(settings, "inprocess")
    assert report["state"]["health"]["http_status"] == 200
    assert (settings.data / "demo-latest.json").exists()
    await cli.execute(command("investigate", "Check checkout"))
    # Read IDs from the local store, not formatted console output.
    store = Store(settings)
    row = store.execute("SELECT id FROM incidents ORDER BY rowid DESC LIMIT 1").fetchone()
    incident = row["id"]
    p = dict(store.execute("SELECT id, hash FROM proposals WHERE incident=?", (incident,)).fetchone())
    store.close()
    await cli.execute(command("status", incident))
    await cli.execute(command("trace", incident))
    await cli.execute(command("--as", "jethalal", "reject", p["id"], "--hash", p["hash"]))
    await cli.execute(command("--as", "jethalal", "resume", incident))
    # Exercise approve command independently; rejection cannot be undone by replay.
    engine = Engine(settings)
    state = await engine.start(principal("bagha"), "Check checkout")
    engine.close()
    await cli.execute(
        command("--as", "jethalal", "approve", state["proposal"]["id"], "--hash", state["proposal"]["hash"])
    )
    assert "HTTP 200" in capsys.readouterr().out


@pytest.mark.parametrize(
    "args",
    [
        ("index", "--rebuild"),
        ("search", "checkout payment URL"),
        ("ask", "checkout payment URL"),
        ("preflight",),
        ("token", "--scopes", "read"),
        ("demo",),
    ],
)
async def test_cli_commands(command, args, capsys):
    await cli.execute(command(*args))
    output = capsys.readouterr().out
    assert output.strip()
    if args[0] == "token":
        assert len(output.split(".")) == 3
    if args[0] == "ask":
        assert "Offline practice" in output
    if args[0] == "preflight":
        assert "false" in output


async def test_unknown_rag_answer_does_not_call_model(command, monkeypatch, capsys):
    monkeypatch.setattr(cli.Retriever, "search", lambda *a: {"results": []})
    await cli.execute(command("ask", "question with no authorized sources"))
    assert "unknown" in capsys.readouterr().out


async def test_cli_catalog_filters_nonfree_and_non_tool_models(command, monkeypatch, capsys):
    data = [
        {
            "id": "good:free",
            "pricing": {"prompt": 0, "completion": 0},
            "supported_parameters": ["tools", "tool_choice"],
        },
        {"id": "paid", "pricing": {"prompt": 1, "completion": 1}},
        {"id": "charged:free", "pricing": {"prompt": 1, "completion": 0}},
        {"id": "no-tools:free", "pricing": {"prompt": 0, "completion": 0}},
    ]
    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kw: original(
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"data": data})), **kw
        ),
    )
    await cli.execute(command("models"))
    output = capsys.readouterr().out
    assert "good:free" in output and "charged:free" not in output and "no-tools:free" not in output


async def test_evaluator_runs_real_outcomes_and_writes_report(command, tmp_path):
    output = tmp_path / "eval.json"
    await cli.execute(command("evaluate", "--output", str(output)))
    result = json.loads(output.read_text())
    assert result["failed"] == 0 and result["passed"] == 13
    assert not result["live_model_quality_tested"]


async def test_evaluator_detects_deliberately_broken_security(settings, monkeypatch):
    # Mutation-style check: the evaluator must report failures if these controls regress.
    monkeypatch.setattr(Auth, "verify", lambda *a: principal("bagha"))
    decide = Engine.decide

    async def faulty_decide(self, proposal_id, actor, expected_hash, approve):
        if actor.user == "bagha" or self.store.proposal(proposal_id, actor)["status"] == "applied":
            return {}
        return await decide(self, proposal_id, actor, expected_hash, approve)

    monkeypatch.setattr(Engine, "decide", faulty_decide)
    store_decide = Store.decide

    def faulty_hash(self, pid, actor, expected, approve):
        return {} if expected == "0" * 64 else store_decide(self, pid, actor, expected, approve)

    monkeypatch.setattr(Store, "decide", faulty_hash)
    result = await evaluate(settings)
    failed = {case["scenario"] for case in result["cases"] if not case["passed"]}
    assert failed == {
        "wrong_audience_rejected",
        "viewer_approval_denied",
        "changed_proposal_denied",
        "approval_replay_denied",
    }


async def test_failed_evaluation_fails_cli(command, monkeypatch, tmp_path):
    import runbookops.evaluations

    async def failed(settings):
        return {"failed": 1, "cases": []}

    monkeypatch.setattr(runbookops.evaluations, "evaluate", failed)
    with pytest.raises(ModelError, match="Evaluation failures"):
        await cli.execute(command("evaluate", "--output", str(tmp_path / "failed.json")))


@pytest.mark.parametrize("failure", ["missing-proposal", "viewer-allowed", "recovery-failed"])
async def test_demo_smoke_check_rejects_broken_workflow(settings, monkeypatch, failure):
    class BrokenEngine:
        def __init__(self, *a):
            self.closed = False

        async def start(self, *a):
            return {
                "incident_id": "test",
                "mode": "test",
                "diagnosis": "test",
                "health": {"http_status": 503},
                "proposal": None if failure == "missing-proposal" else {"id": "p", "hash": "h"},
            }

        async def decide(self, pid, actor, *a):
            if actor.user == "bagha" and failure != "viewer-allowed":
                from runbookops.security import Denied

                raise Denied("no approval")
            return {"health": {"http_status": 503}}

        def close(self):
            self.closed = True

    monkeypatch.setattr(cli, "Engine", BrokenEngine)
    with pytest.raises((ModelError, AssertionError)):
        await cli.demo(settings, "inprocess")


def test_cli_entrypoint_serve_errors_interrupt_and_module(command, settings, monkeypatch):
    import uvicorn

    runner = Mock()
    monkeypatch.setattr(uvicorn, "run", runner)
    monkeypatch.setattr(sys, "argv", ["runbookops", "serve", "--demo-auth", "--port", "8123"])
    assert cli.main() == 0
    assert runner.call_args.kwargs["host"] == "127.0.0.1" and runner.call_args.kwargs["port"] == 8123
    runner.call_args.args[0].state.engine.close()
    monkeypatch.setattr(sys, "argv", ["runbookops", "index"])
    real = cli.asyncio.run

    def fail(coro):
        coro.close()
        raise ValueError("invalid setting")

    monkeypatch.setattr(cli.asyncio, "run", fail)
    assert cli.main() == 1

    def interrupt(coro):
        coro.close()
        raise KeyboardInterrupt

    monkeypatch.setattr(cli.asyncio, "run", interrupt)
    assert cli.main() == 130
    monkeypatch.setattr(cli.asyncio, "run", lambda coro: coro.close())
    assert cli.main() == 0
    monkeypatch.delitem(sys.modules, "runbookops.cli", raising=False)
    with pytest.raises(SystemExit) as status:
        runpy.run_module("runbookops.cli", run_name="__main__")
    assert status.value.code == 0
    monkeypatch.setattr(cli.asyncio, "run", real)


async def test_offline_evaluation_clears_cloud_storage(settings, monkeypatch):
    import runbookops.evaluations as module

    original = module.Engine
    configurations = []

    def local_engine(config):
        configurations.append(config)
        assert not config.dynamodb_table and not config.checkpoint_table and not config.database_url
        return original(config)

    monkeypatch.setattr(module, "Engine", local_engine)
    report = await module.evaluate(
        dataclasses.replace(
            settings,
            dynamodb_table="must-not-touch",
            checkpoint_table="must-not-touch",
            database_url="postgresql://must-not-touch",
        )
    )
    assert report["failed"] == 0 and configurations
