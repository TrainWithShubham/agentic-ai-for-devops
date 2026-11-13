"""Check a course exercise or its completed solution without making model calls."""

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(folder, filename):
    spec = importlib.util.spec_from_file_location("learner_exercise", ROOT / folder / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def must_reject(function, *args):
    try:
        function(*args)
    except ValueError:
        return
    raise AssertionError("Invalid input was accepted")


def check(name, solution=False):
    folder = "solutions" if solution else "exercises"
    if name == "ci":
        fn = load(folder, "ci_summary.py").ci_summary
        answer = fn({"run_id": 1042, "conclusion": "failure", "failed_step": "Test"})
        assert all(word in answer for word in ("1042", "failure", "Test"))
        for bad in (
            {},
            {"run_id": 99},
            {"run_id": 1042, "conclusion": "unknown", "failed_step": "Test"},
            {"run_id": 1042, "conclusion": "failure"},
        ):
            must_reject(fn, bad)
    elif name == "rag":
        fn = load(folder, "source_filter.py").allowed_sources
        docs = [
            {"id": "current", "current": True, "roles": ["engineer"]},
            {"id": "retired", "current": False, "roles": ["engineer"]},
            {"id": "restricted", "current": True, "roles": ["release-manager"]},
        ]
        assert [d["id"] for d in fn(docs, "engineer")] == ["current"]
        assert [d["id"] for d in fn(docs, "release-manager")] == ["restricted"]
        must_reject(fn, docs, "administrator-by-prompt")
        assert len(docs) == 3, "Do not mutate the input collection"
    elif name == "approval":
        fn = load(folder, "approval_policy.py").may_approve
        assert fn("release-manager", 20, 10, False) is True
        for inputs in (
            ("engineer", 20, 10, False),
            ("release-manager", 10, 10, False),
            ("release-manager", 20, 10, True),
        ):
            assert fn(*inputs) is False
    else:
        case = json.loads((ROOT / folder / "extra_evaluation.json").read_text())
        assert all(
            isinstance(case.get(k), str) and case[k].strip()
            for k in ("name", "input", "expected_outcome", "reason")
        )
        assert case["name"] != "replace-with-your-case", (
            "Replace the example placeholders with a concrete case"
        )
    return name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exercise", choices=["ci", "rag", "approval", "evaluation", "all"])
    parser.add_argument("--solution", action="store_true")
    args = parser.parse_args()
    try:
        for name in ("ci", "rag", "approval", "evaluation") if args.exercise == "all" else (args.exercise,):
            print("Passed:", check(name, args.solution))
    except (NotImplementedError, AssertionError) as error:
        print(str(error))
        print("Complete the learner file or use --solution to check the supplied completed version.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
