"""Behavioral checks for the teaching boundaries; no generative API calls."""

import asyncio
import contextlib
import io
import os
import sys
import unittest
from unittest.mock import patch

from course_labs.agent import run
from course_labs.common import run_cli
from course_labs.evaluations import BAD, GOOD, evaluate
from course_labs.graph import build
from course_labs.mcp_client import inspect
from course_labs.operations import Cache, cache_key, route
from course_labs.provider import catalog, complete, is_free_tool_model
from course_labs.rag import DOCS, build_index, embedding_model, extract, retrieve, split
from course_labs.security import ALLOWED_PATCH, Principal, Review
from course_labs.tools import execute
from scripts.check_exercise import check


class CourseChecks(unittest.TestCase):
    def test_ci_tool_validation(self):
        self.assertEqual(execute("ci_get_run", {"run_id": 1042})["failed_step"], "Test")
        for name, args in (
            ("shell", {"run_id": 1042}),
            ("ci_read_log", {"run_id": 99}),
            ("ci_read_log", {"run_id": "1042"}),
            ("ci_read_log", {"run_id": 1042, "command": "rm -rf /"}),
        ):
            with self.assertRaises(ValueError):
                execute(name, args)

    def test_plain_loop_uses_actual_tools(self):
        result = run(emit=lambda _: None)
        self.assertEqual(
            [e["result"]["source_id"] for e in result["events"] if e["kind"] == "tool"],
            ["ci-run", "ci-log", "ci-workflow"],
        )
        self.assertIn("--no-dev", result["answer"])
        self.assertIn("not been changed", result["answer"])

    def test_loop_stops_at_model_budget(self):
        from course_labs.agent import fixture_message

        with patch("course_labs.agent.fixture_message", side_effect=lambda _: fixture_message(0)):
            with self.assertRaisesRegex(RuntimeError, "budget"):
                run(emit=lambda _: None)

    def test_langgraph_runs_real_nodes(self):
        with contextlib.redirect_stdout(io.StringIO()):
            state = build().invoke(
                {
                    "messages": [{"role": "user", "content": "Investigate"}],
                    "calls": 0,
                    "steps": 0,
                    "done": False,
                }
            )
        self.assertEqual((state["calls"], state["steps"], state["done"]), (4, 3, True))
        self.assertIn("pytest", state["messages"][-1]["content"])

    def test_real_mcp_stdio(self):
        with contextlib.redirect_stdout(io.StringIO()):
            result = asyncio.run(inspect())
        self.assertEqual(result["names"], ["ci_get_run", "ci_read_log", "ci_read_workflow"])
        self.assertEqual(result["log"]["source_id"], "ci-log")
        self.assertIn("Failed to spawn", result["log"]["text"])

    def test_five_document_formats(self):
        for name, location in (
            ("release-process.md", "paragraph"),
            ("deployment-policy.txt", "paragraph"),
            ("rollback-checklist.pdf", "page"),
            ("release-incident.docx", "paragraph"),
            ("deployment-architecture.pptx", "slide"),
        ):
            sections = extract(DOCS / name)
            self.assertTrue(sections)
            self.assertTrue(sections[0][0].startswith(location))
            self.assertTrue(any("Catalog" in text or "Document ID" in text for _, text in sections))

    def test_chunk_bounds(self):
        chunks = split("0123456789abcdefghij", size=8, overlap=2)
        self.assertEqual(chunks[0][-2:], chunks[1][:2])
        self.assertTrue(all(len(c) <= 8 for c in chunks))
        for values in ((0, 0), (8, 8), (8, -1)):
            with self.assertRaises(ValueError):
                split("text", *values)

    def test_retrieval_filters_and_locations(self):
        index = build_index()
        results = retrieve(index, "approval checks production rollback", limit=20)
        self.assertIn("rollback-checklist", {r["id"] for r in results})
        self.assertTrue(all(r["current"] and "location" in r for r in results))
        self.assertNotIn("deploy-old", {r["id"] for r in results})
        restricted = retrieve(index, "signing rotation", limit=20)
        self.assertNotIn("restricted-operations", {r["id"] for r in restricted})
        manager = retrieve(index, "signing rotation", role="release-manager", limit=20)
        self.assertIn("restricted-operations", {r["id"] for r in manager})
        self.assertEqual(retrieve(index, "zebras astrophysics xyzzy"), [])
        with self.assertRaises(PermissionError):
            retrieve(index, "rollback", role="admin-by-prompt")

    def test_proposal_permission_tamper_expiry_and_replay(self):
        manager, engineer = Principal("owner", "release-manager"), Principal("dev", "engineer")
        review = Review()
        proposal = review.prepare(engineer, ALLOWED_PATCH)
        with self.assertRaises(PermissionError):
            review.approve(engineer, proposal["hash"])
        with self.assertRaises(ValueError):
            review.approve(manager, "0" * 64)
        review.proposal["change"]["after"] = "delete all tests"
        with self.assertRaises(ValueError):
            review.approve(manager, proposal["hash"])
        proposal = review.prepare(engineer, ALLOWED_PATCH)
        review.proposal["expires_at"] = 0
        with self.assertRaises(ValueError):
            review.approve(manager, proposal["hash"])
        proposal = review.prepare(engineer, ALLOWED_PATCH)
        self.assertIs(review.approve(manager, proposal["hash"])["ci_modified"], False)
        with self.assertRaises(ValueError):
            review.approve(manager, proposal["hash"])
        with self.assertRaises(ValueError):
            review.prepare(engineer, {"command": "delete"})

    def test_cache_scope_invalidation_and_expiry(self):
        cache = Cache()
        values = ["question", "engineer", "docs-v1", "model-v1", "prompt-v1"]
        key = cache_key(*values)
        cache.put(key, "answer")
        self.assertEqual(cache.get(key), "answer")
        for i in range(len(values)):
            changed = list(values)
            changed[i] += "-changed"
            self.assertIsNone(cache.get(cache_key(*changed)))
        cache.put(key, "answer", ttl=-1)
        self.assertIsNone(cache.get(key))
        self.assertEqual(route("approve_change"), "human-review")
        with self.assertRaises(ValueError):
            route("arbitrary task")

    def test_evaluation_catches_bad_candidate(self):
        self.assertEqual(evaluate(GOOD)["failed"], 0)
        self.assertEqual(evaluate(BAD)["passed"], 0)

    def test_completed_exercises(self):
        for name in ("ci", "rag", "approval", "evaluation"):
            self.assertEqual(check(name, solution=True), name)

    def test_empty_and_failed_live_requests_do_not_become_success(self):
        import httpx

        model = {
            "id": "fake/model:free",
            "pricing": {"prompt": "0", "completion": "0"},
            "supported_parameters": ["tools", "tool_choice"],
        }
        with (
            patch.dict(
                os.environ, {"OPENROUTER_MODEL": model["id"], "OPENROUTER_API_KEY": "course-test-not-a-key"}
            ),
            patch("course_labs.provider.catalog", return_value=[model]),
            patch("course_labs.provider.httpx.Client") as factory,
        ):
            response = factory.return_value.__enter__.return_value.post.return_value
            response.json.return_value = {
                "choices": [{"message": {"content": ""}, "finish_reason": "length"}]
            }
            with self.assertRaisesRegex(RuntimeError, "no usable answer"):
                complete([{"role": "user", "content": "hello"}])
            response.json.return_value = {
                "choices": [{"message": {"content": "partial diagnosis"}, "finish_reason": "length"}]
            }
            with self.assertRaisesRegex(RuntimeError, "truncated"):
                complete([{"role": "user", "content": "hello"}])
            factory.return_value.__enter__.return_value.post.side_effect = httpx.ReadTimeout("test")
            with self.assertRaisesRegex(RuntimeError, "No offline or paid fallback"):
                complete([{"role": "user", "content": "hello"}])

    def test_missing_live_configuration_gives_recovery_without_a_request(self):
        errors = io.StringIO()
        with (
            patch.dict(os.environ, {"OPENROUTER_API_KEY": "", "OPENROUTER_MODEL": ""}),
            patch("course_labs.provider.load_dotenv"),
            patch("course_labs.provider.catalog") as model_list,
            contextlib.redirect_stderr(errors),
            self.assertRaises(SystemExit) as stopped,
        ):
            run_cli(lambda: complete([]), "Use setup/README.md or rerun without --live.")
        self.assertEqual(stopped.exception.code, 1)
        self.assertIn("Live mode needs", errors.getvalue())
        self.assertIn("without --live", errors.getvalue())
        self.assertNotIn("Traceback", errors.getvalue())
        model_list.assert_not_called()

    def test_catalog_failure_is_actionable_and_does_not_echo_network_details(self):
        import httpx

        catalog.cache_clear()
        with patch("course_labs.provider.httpx.Client") as factory:
            factory.return_value.__enter__.return_value.get.side_effect = httpx.ReadTimeout(
                "private-network-detail"
            )
            with self.assertRaises(RuntimeError) as failure:
                catalog()
        self.assertIn("course_labs.models", str(failure.exception))
        self.assertIn("No model was called", str(failure.exception))
        self.assertNotIn("private-network-detail", str(failure.exception))
        catalog.cache_clear()

    def test_missing_semantic_package_explains_install_and_keyword_option(self):
        embedding_model.cache_clear()
        with patch.dict(sys.modules, {"fastembed": None}):
            with self.assertRaises(RuntimeError) as failure:
                embedding_model()
        self.assertIn("uv sync --frozen --extra semantic", str(failure.exception))
        self.assertIn("keyword search works without it", str(failure.exception))
        embedding_model.cache_clear()

    def test_paid_and_non_tool_routes_are_rejected(self):
        model = {
            "id": "fake/model:free",
            "pricing": {"prompt": "0", "completion": "0"},
            "supported_parameters": ["tools", "tool_choice"],
        }
        self.assertTrue(is_free_tool_model(model))
        self.assertFalse(is_free_tool_model({**model, "pricing": {"prompt": ".01", "completion": "0"}}))
        self.assertFalse(is_free_tool_model({**model, "supported_parameters": []}))
        with (
            patch.dict(
                os.environ, {"OPENROUTER_MODEL": "fake/paid", "OPENROUTER_API_KEY": "course-test-not-a-key"}
            ),
            patch("course_labs.provider.catalog", return_value=[model]),
            patch("course_labs.provider.httpx.Client") as client,
        ):
            with self.assertRaisesRegex(ValueError, "zero-priced"):
                complete([{"role": "user", "content": "hello"}])
            client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
