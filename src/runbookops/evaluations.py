"""Small task-outcome evaluation. It reports what was actually exercised."""

import dataclasses
import tempfile

from .agent import Engine
from .auth import Auth
from .rag import Retriever
from .security import Denied, InvalidChange, principal, redact


async def evaluate(settings):
    cases = []

    def record(name, passed):
        cases.append({"scenario": name, "passed": bool(passed)})

    with tempfile.TemporaryDirectory(prefix="runbookops-eval-") as folder:
        config = dataclasses.replace(settings, data=folder, mode="offline", database_url="", mcp_url="")
        bagha, jethalal = principal("bagha"), principal("jethalal")
        retriever = Retriever(config)
        hits = retriever.search("checkout runbook payment URL connection refused", bagha)
        record("current_runbook_retrieved", any(r["source"] == "checkout-runbook" for r in hits["results"]))
        restricted = retriever.search("INTERNAL_APPROVER_MARKER_GADA_27 restricted operations", bagha)
        record("viewer_document_isolation", all(r["access"] == "public" for r in restricted["results"]))
        privileged = retriever.search("INTERNAL_APPROVER_MARKER_GADA_27 restricted operations", jethalal)
        record(
            "approver_document_visible",
            any(r["source"] == "restricted-operations" for r in privileged["results"]),
        )
        cached = retriever.search("INTERNAL_APPROVER_MARKER_GADA_27 restricted operations", bagha)
        record("cache_does_not_cross_roles", all(r["access"] == "public" for r in cached["results"]))
        record("logs_redact_keys", "sk-test" not in redact("API_KEY=sk-test-workshop-secret-only"))
        auth = Auth(config)
        try:
            auth.verify(auth.issue("bagha", audience="wrong-service"))
            record("wrong_audience_rejected", False)
        except Denied:
            record("wrong_audience_rejected", True)
        engine = Engine(config)
        state = await engine.start(
            bagha, "Investigate checkout 503 and prepare a proposal, but wait for approval."
        )
        record(
            "proposal_without_execution",
            state.get("waiting_for_approval") and state["health"]["http_status"] == 503,
        )
        proposal = state["proposal"]
        try:
            await engine.decide(proposal["id"], bagha, proposal["hash"], True)
            record("viewer_approval_denied", False)
        except Denied:
            record("viewer_approval_denied", True)
        try:
            engine.store.decide(proposal["id"], jethalal, "0" * 64, True)
            record("changed_proposal_denied", False)
        except InvalidChange:
            record("changed_proposal_denied", True)
        engine.close()
        engine = Engine(config)
        result = await engine.decide(proposal["id"], jethalal, proposal["hash"], True)
        record("restart_resume_and_recovery", result["health"]["http_status"] == 200)
        replay = engine.store.apply(proposal["id"], bagha)
        record("executor_idempotency", replay["idempotent_replay"] and replay["health"]["revision"] == 2)
        try:
            await engine.decide(proposal["id"], jethalal, proposal["hash"], True)
            record("approval_replay_denied", False)
        except InvalidChange:
            record("approval_replay_denied", True)
        rejected = await engine.start(bagha, "Investigate checkout and prepare a correction for review.")
        rp = rejected["proposal"]
        result = await engine.decide(rp["id"], jethalal, rp["hash"], False)
        record(
            "rejection_preserves_service",
            result["health"]["http_status"] == 503 and not result["result"]["applied"],
        )
        engine.close()
    return {
        "mode": "offline",
        "live_model_quality_tested": False,
        "cases": cases,
        "passed": sum(case["passed"] for case in cases),
        "failed": sum(not case["passed"] for case in cases),
    }
