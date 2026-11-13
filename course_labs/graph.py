"""The same CI decision loop expressed as explicit LangGraph nodes."""

import argparse
import json
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from .agent import fixture_message
from .common import ROOT, show
from .provider import complete
from .tools import SCHEMAS, execute


class State(TypedDict):
    messages: list[dict]
    calls: int
    steps: int
    done: bool


def build(live=False):
    def model(state):
        if state["calls"] >= 4:
            raise RuntimeError("Four-model-call limit reached")
        message, _ = complete(state["messages"], SCHEMAS) if live else (fixture_message(state["calls"]), {})
        show(
            {
                "node": "model",
                "turn": state["calls"] + 1,
                "scripted": not live,
                "requested_tools": [c["function"]["name"] for c in message.get("tool_calls", [])],
            }
        )
        return {
            "messages": state["messages"] + [message],
            "calls": state["calls"] + 1,
            "done": not bool(message.get("tool_calls")),
        }

    def tools(state):
        messages = list(state["messages"])
        steps = state["steps"]
        for call in state["messages"][-1]["tool_calls"]:
            steps += 1
            if steps > 6:
                raise RuntimeError("Six-tool-step limit reached")
            result = execute(call["function"]["name"], json.loads(call["function"]["arguments"]))
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result)})
            show({"node": "tools", "source": result["source_id"]})
        return {"messages": messages, "steps": steps}

    graph = StateGraph(State)
    graph.add_node("model", model)
    graph.add_node("tools", tools)
    graph.add_edge(START, "model")
    graph.add_conditional_edges("model", lambda s: END if s["done"] else "tools")
    graph.add_edge("tools", "model")
    return graph.compile()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    result = build(args.live).invoke(
        {
            "messages": [
                {"role": "system", "content": (ROOT / "prompts/ci-system.txt").read_text()},
                {
                    "role": "user",
                    "content": "Investigate run 1042 with logs and workflow. Propose a fix with citations; do not apply it.",
                },
            ],
            "calls": 0,
            "steps": 0,
            "done": False,
        }
    )
    show(
        {
            "answer": result["messages"][-1]["content"],
            "state_scope": "in-memory only; persistence is a separate feature",
        }
    )


if __name__ == "__main__":
    main()
