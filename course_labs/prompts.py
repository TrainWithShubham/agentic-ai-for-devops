"""Compare vague instructions with an evidence-based CI prompt."""

import argparse

from .common import ROOT, run_cli, show
from .provider import complete


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    system = (ROOT / "prompts/ci-system.txt").read_text()
    log = (ROOT / "data/ci/test-output.txt").read_text()
    workflow = (ROOT / "data/ci/workflow.txt").read_text()
    print("Vague prompt: Fix my pipeline.\n\nSystem instructions:\n" + system)
    if args.live:
        message, usage = complete(
            [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": f"Explain run 1042 using [ci-log] {log}\n[ci-workflow] {workflow}",
                },
            ]
        )
        show({"mode": "live", "answer": message.get("content"), "usage": usage})
    else:
        show(
            {
                "mode": "offline fixture, no LLM call",
                "observed": "pytest cannot start; the installation excluded development dependencies",
                "likely_cause": "pytest is in the dev group, which --no-dev excluded",
                "proposal": "Install the locked dev group for the test job by removing --no-dev",
                "validation": "Have a person review the diff and rerun the test job; no rerun has happened",
                "sources": ["ci-log", "ci-workflow"],
            }
        )


if __name__ == "__main__":
    run_cli(main, "See module-1/README.md or checkpoints/README.md for the next step.")
