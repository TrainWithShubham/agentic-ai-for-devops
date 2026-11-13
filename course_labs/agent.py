"""A visible, bounded tool loop. Offline tool requests are scripted, not AI decisions."""

import argparse
import json
import time

from .common import ROOT, run_cli, show
from .provider import complete
from .tools import SCHEMAS, execute


def fixture_message(turn):
    """Return a prepared model message so the loop can be learned without an API key."""
    if turn < 3:
        name = ["ci_get_run", "ci_read_log", "ci_read_workflow"][turn]
        return {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": f"call-{turn}",
                    "type": "function",
                    "function": {"name": name, "arguments": '{"run_id":1042}'},
                }
            ],
        }
    return {
        "role": "assistant",
        "content": "pytest was excluded by --no-dev [ci-log, ci-workflow]. Propose removing --no-dev for this test job. Ask a person to review and rerun; the pipeline has not been changed.",
    }


def run(live=False, emit=show):
    messages = [
        {"role": "system", "content": (ROOT / "prompts/ci-system.txt").read_text()},
        {
            "role": "user",
            "content": "Investigate CI run 1042. Read the logs and workflow, cite evidence and propose a minimal fix for review.",
        },
    ]
    events, steps = [], 0
    for turn in range(4):
        started = time.monotonic()
        message, usage = complete(messages, SCHEMAS) if live else (fixture_message(turn), {})
        messages.append(message)
        event = {
            "kind": "model",
            "turn": turn + 1,
            "mode": "live" if live else "offline scripted fixture",
            "duration_ms": round((time.monotonic() - started) * 1000),
            "usage": usage,
        }
        events.append(event)
        emit(event)
        calls = message.get("tool_calls", [])
        if not calls:
            final = {
                "kind": "answer",
                "content": message.get("content"),
                "status": "read-only recommendation; no CI change applied",
            }
            emit(final)
            return {"events": events, "answer": final["content"], "messages": messages}
        for call in calls:
            steps += 1
            if steps > 6:
                raise RuntimeError("Tool-step budget reached; investigation stopped")
            name = call["function"]["name"]
            try:
                arguments = json.loads(call["function"]["arguments"])
                result = execute(name, arguments)
            except (ValueError, TypeError):
                result = {
                    "error": "Invalid tool or arguments; use a discovered read-only tool and run_id 1042"
                }
            event = {"kind": "tool", "tool": name, "result": result}
            events.append(event)
            emit(event)
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)})
    raise RuntimeError("Four-model-call budget reached without a final answer; no change was applied")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    run(args.live)


if __name__ == "__main__":
    run_cli(main, "See module-2/README.md or checkpoints/README.md for the next step.")
