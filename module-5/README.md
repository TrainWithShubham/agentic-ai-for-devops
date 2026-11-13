# Module 5: agent harnesses and operations

**Day 2 · 40 minutes** · [Previous](../module-4/README.md) · [Glossary](../GLOSSARY.md)

You will inspect a cache result, follow a trace and run checks that catch a misleading answer. The question is familiar to DevOps: how do we know what the system actually did?

## Understand the harness

A harness is the software around the model: it builds context, runs tools, carries state and handles limits, failures and telemetry. Products use the name for different combinations of these responsibilities.

| Part | Responsibility |
|---|---|
| Model | Produce text or a tool request |
| Agent loop | Choose permitted next steps using tool observations |
| Framework | Express state and routes in code |
| Harness | Coordinate execution and its controls |
| Runtime | Run the application code |
| Persistent state | Keep needed information after a process exits |

The small CI agent has counters, validated tools and volatile state. Production also needs suitable identity, persistence, cancellation and safe recovery. Adding a framework does not automatically implement these policies.

## Run cache, routing and trace examples

```bash
uv run python -m course_labs.operations
```

Look for these results:

```json
{
  "kind": "cache",
  "same_role_hit": true,
  "other_role_hit": false,
  "changed_corpus_hit": false
}
```

A **hit** reuses a saved answer. A **miss** means it was not found under that key. The key includes the question, role, document version, model and prompt version. TTL, or time to live, limits how long an entry can be reused. Read `cache_key` and `Cache` in [operations.py](../course_labs/operations.py).

Next, inspect `kind: routing` and `live_models_selected: false`. Routing means choosing who handles a task. These labels demonstrate that choice; they do not call different models. Finally, find `result: recommendation_only` in the trace event. A trace records what happened. The example writes actual local events to `.state/operations-trace.jsonl`; it is not an OpenTelemetry deployment.

| Technique | Useful for | What to check |
|---|---|---|
| Saved answer | Repeated authorized questions | Is the caller still allowed? Is the source current? |
| Retrieval/embedding cache | Avoiding repeated preparation | Did the document or embedding model change? |
| Provider prompt cache | Reusing eligible model-input processing | Does this provider/model support it, and what does it cost? |
| Model routing | Matching a task to cost, delay and capability | Does the chosen model pass the actual task checks? |

## Change one thing

In `operations.py`, change the document version or role used for the lookup. Predict whether it will hit, then rerun. Explain why a production system may also need user, tenant and resource scope. A role-only example is not a complete multi-tenant cache.

Trace records should connect sources, tool results, review decisions and the final result through an ID. Keep secrets and unnecessary private content out of traces. OpenTelemetry and a trace backend are follow-up choices, not requirements for this exercise.

## Run the evaluations

An evaluation is a task with an expected result and a way to check it. A **candidate** is the answer being checked.

```bash
uv run python -m course_labs.evaluations
uv run python -m course_labs.evaluations --bad-candidate
```

The first reports `passed: 5`, `failed: 0`. The deliberate bad answer reports `passed: 0`, `failed: 5` and exits with code 1. That failure is the expected result: the checks caught an answer that claimed a fix by deleting tests and lacked supporting sources.

Read [the cases](../data/evaluations.json) and `evaluate` in [evaluations.py](../course_labs/evaluations.py). These small text/field checks run against fixed answers; they do not measure live-model quality. A citation-presence check cannot establish source support. Use [the saved answer-review exercise](../data/rag-answer-for-review.md) to find a recovery instruction that the cited checklist did not authorize.

Complete [exercises/extra_evaluation.json](../exercises/extra_evaluation.json) with one concrete case. Fill in its name, input, expected outcome and why the case matters.

```bash
uv run python scripts/check_exercise.py evaluation
```

Success prints `Passed: evaluation`. This checks that your case has the required non-placeholder fields, not that a model passes it. Run `--solution` or read [the completed case](../solutions/extra_evaluation.json) if stuck. For a live evaluation, save actual model inputs, outputs, tool results and configuration; check supported answers and observed outcomes, not just wording.

Optional coding-assistant prompt:

> Help me write one evaluation for an assistant claiming CI is fixed when it only read evidence. Use an observable expected outcome. Keep the case small and explain its limits.

## Apply your DevOps judgment

Set call limits and deadlines. A timeout means the caller stopped waiting; a remote write may still finish. Check operation status or target state before retrying, use an idempotency contract to prevent duplicate effects, and bound retries with backoff. A rate limit is not a spending cap. Measure failed requests, tool time and retries as well as model usage.

Releases need versioned code, prompts, tool definitions and evaluation cases, with health checks, rollback and cleanup. Do not claim an operation succeeded until its observed result supports that claim.

Before the break, explain which event you would inspect for a wrong tool argument, stale answer or unauthorized change. Use [recovery checkpoints](../checkpoints/README.md) if a command fails unexpectedly.

**Next:** [Module 6: the integrated capstone](../module-6/README.md), after the break.
