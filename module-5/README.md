# Module 5 — agent harnesses and operations

Day 2, 40 minutes. Learn to inspect and control the agent as a system you operate.

## What is an agent harness?

A harness is the surrounding software that runs the loop: constructs context, calls the model, dispatches tools, carries state and handles limits, failures, review and telemetry. Different products include different responsibilities under that name.

| Term | Responsibility |
|---|---|
| Model | Produces text or structured requests from context |
| Agent loop | Chooses/executes permitted steps using observations |
| Framework | Libraries for expressing state and control flow |
| Harness | The surrounding execution and control machinery |
| Runtime/hosting | The environment running that code |
| External state store | Data needed beyond one process/session |

Map these terms onto the small CI loop. Its counters bound work, tool handlers validate calls and model/provider errors stop the run. Its state is volatile. A production harness also needs cancellation, authentication, persistence and safe handling of retries around side effects. A framework name alone does not supply those policies.

## Cache, route and trace

```bash
uv run python -m course_labs.operations
```

Inspect [operations.py](../course_labs/operations.py) and `.state/operations-trace.jsonl`.

The first cache read hits. Changing role or corpus version misses. The key also includes question, model and prompt version. This small exact-match cache has a TTL. It is not a distributed cache or semantic cache, and its printed routing labels do not invoke different models.

| Technique | Useful for | Failure to consider |
|---|---|---|
| Exact response cache | Repeated authorized questions | Stale context or a key that omits user/resource scope |
| Retrieval/embedding cache | Avoiding repeated preparation | Document/model changes require invalidation |
| Prompt/provider cache | Repeated model-input prefixes | Provider-specific eligibility and pricing |
| Task/model routing | Different quality, cost and latency needs | A smaller model may fail the actual tool/schema/evidence task |

Measure before deciding a route is cheaper or faster. Include failed requests, repeated context, tool time, retries and human waiting. A rate limit is not a spending cap.

Traces should let you locate the failing stage: retrieval, model output, argument validation, tool result, review or verification. Record IDs, duration, model/usage metadata and sanitized outcomes. Use correlation IDs across logs. OpenTelemetry and trace backends are production extensions; this lab writes actual local JSONL events.

## Reliability decisions

Set deadlines and step budgets. Retry transient read failures with a limit and backoff; classify permanent authorization/schema failures separately. A timeout after a write request may leave an unknown result, so a blind retry can duplicate a change. Use an idempotency key and verify actual external state before calling an action successful. Include cancellation and partial failure in reviews.

Deployment needs an immutable artifact, dependency lock, appropriate runtime identity, health/readiness checks, durable state, logs, release checks, rollback and teardown. Separate local process memory from durable checkpoints. Discuss CI gates for prompts, tools and evaluation datasets as well as Python tests.

## Evaluations: test an outcome, not a sentence's confidence

```bash
uv run python -m course_labs.evaluations
# Deliberate failing candidate: exits nonzero and displays which outcomes failed.
uv run python -m course_labs.evaluations --bad-candidate
```

The dataset in [data/evaluations.json](../data/evaluations.json) checks whether the CI answer cites required evidence, identifies the missing test runner and avoids claiming an applied fix. These checks run against supplied fixed candidates; they do not measure live model reliability. The course regression checks separately test actual role, RAG and tool boundaries.

For a live evaluation, save the actual input, model/version, tool results and answer, then evaluate that run. Avoid a judge that only checks wording. Human review is still needed to assess source support and the quality of a proposed change.

Read [the recorded RAG answer for review](../data/rag-answer-for-review.md). Compare the added recovery step with the PDF checklist. A citation-presence check alone would not prove that the source supports that step.

## Practical: add a case that catches a real mistake

Edit [exercises/extra_evaluation.json](../exercises/extra_evaluation.json) with one denied or missing-evidence case. Explain the input, expected outcome and why it matters.

```bash
uv run python scripts/check_exercise.py evaluation
```

Then change the corpus version or role in the cache demo and predict the result before running it. Name which fields you would add for multi-tenant resource permissions.

AI coding prompt:

> Help me add one evaluation for a model claiming it fixed CI without an execution result. Use a concrete expected outcome. Keep live-model quality claims separate from deterministic regression results.

Check understanding: show which event you would inspect for a wrong tool argument, a stale answer and an unauthorized change. Explain why an offline test pass is not a live-model success rate.

After the break, open [module 6](../module-6/README.md).
