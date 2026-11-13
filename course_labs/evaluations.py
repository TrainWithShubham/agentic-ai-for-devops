"""Deterministic outcome checks over fixed candidates; no live-model reliability estimate."""

import argparse

from .common import read_json, show

GOOD = {
    "answer": "pytest did not start because --no-dev excluded its development group. Propose removing that flag, request human review and rerun the test job.",
    "sources": ["ci-log", "ci-workflow"],
    "executed": False,
}
BAD = {
    "answer": "Fixed CI by deleting the tests. Everything is healthy.",
    "sources": ["ci-run"],
    "executed": True,
}


def evaluate(candidate):
    results = []
    for case in read_json("data/evaluations.json"):
        criterion, expected = case["criterion"], case["value"]
        text = candidate.get("answer", "").lower()
        if criterion == "contains":
            passed = expected.lower() in text
        elif criterion == "contains_all":
            passed = all(word.lower() in text for word in expected)
        elif criterion == "sources":
            passed = set(expected).issubset(candidate.get("sources", []))
        elif criterion == "executed":
            passed = candidate.get("executed") is expected
        else:
            raise ValueError("Unknown evaluation criterion")
        results.append({"id": case["id"], "passed": passed, "reason": case["reason"]})
    return {
        "mode": "offline fixed-candidate evaluation",
        "live_model_quality_measured": False,
        "results": results,
        "passed": sum(r["passed"] for r in results),
        "failed": sum(not r["passed"] for r in results),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bad-candidate", action="store_true")
    args = parser.parse_args()
    report = evaluate(BAD if args.bad_candidate else GOOD)
    show(report)
    raise SystemExit(1 if report["failed"] else 0)


if __name__ == "__main__":
    main()
