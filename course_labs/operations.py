"""Show a cache boundary, task routing and sanitized trace events without model calls."""

import hashlib
import json
import time
from dataclasses import dataclass, field

from .common import ROOT, run_cli, show


def route(task):
    routes = {
        "classify_ci": "small-tool-model",
        "explain_deployment": "stronger-grounded-model",
        "approve_change": "human-review",
    }
    if task not in routes:
        raise ValueError("No approved route for that task")
    return routes[task]


def cache_key(question, role, corpus_version, model, prompt_version):
    return hashlib.sha256(
        json.dumps([question, role, corpus_version, model, prompt_version]).encode()
    ).hexdigest()


@dataclass
class Cache:
    values: dict = field(default_factory=dict)

    def put(self, key, value, ttl=60):
        self.values[key] = (time.monotonic() + ttl, value)

    def get(self, key):
        saved = self.values.get(key)
        return saved[1] if saved and saved[0] > time.monotonic() else None


def main():
    question = "Who approves production rollback?"
    cache = Cache()
    key = cache_key(question, "engineer", "docs-v3", "demo-model", "prompt-v1")
    cache.put(key, {"answer": "Release-manager", "source": "deploy-policy"})
    restricted = cache_key(question, "release-manager", "docs-v3", "demo-model", "prompt-v1")
    refreshed = cache_key(question, "engineer", "docs-v4", "demo-model", "prompt-v1")
    events = [
        {
            "kind": "cache",
            "same_role_hit": cache.get(key) is not None,
            "other_role_hit": cache.get(restricted) is not None,
            "changed_corpus_hit": cache.get(refreshed) is not None,
        },
        {
            "kind": "routing",
            "classify_ci": route("classify_ci"),
            "approve_change": route("approve_change"),
            "live_models_selected": False,
        },
        {
            "kind": "trace",
            "trace_id": "demo-ci-1042",
            "task": "classify_ci",
            "source_ids": ["ci-run", "ci-log"],
            "result": "recommendation_only",
            "model_calls": 0,
            "model_tokens": 0,
            "mode": "offline demonstration",
        },
    ]
    target = ROOT / ".state/operations-trace.jsonl"
    target.parent.mkdir(exist_ok=True)
    target.write_text("\n".join(json.dumps(e) for e in events) + "\n")
    for event in events:
        show(event)
    print("Trace: .state/operations-trace.jsonl. No secrets or private model reasoning recorded.")


if __name__ == "__main__":
    run_cli(main, "See module-5/README.md or checkpoints/README.md for the next step.")
