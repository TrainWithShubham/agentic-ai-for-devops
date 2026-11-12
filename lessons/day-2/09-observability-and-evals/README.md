# Show what happened and check the result

Application commands and paths below refer to the standalone [`runbookops`](https://github.com/TrainWithShubham/runbookops) checkout. Course exercises are the exception where noted.

Time: 20 minutes.

```bash
uv run runbookops demo
uv run runbookops evaluate
uv run pytest -q
uv run python scripts/trace_report.py
```

The demo saves `.state/demo-latest.json`. The evaluation command saves actual scenario results to `artifacts/evaluation.json`. The trace report creates an HTML file from the latest demo, with source IDs, tool calls, model metadata, decisions, and health checks. Open it in a browser.

Read `evaluations.py`. Its deterministic checks validate policy and simulator outcomes. They do not measure a real model's quality. A live provider run is recorded separately, including the model name, observed request count, tokens when available, and provider-reported cost. Missing usage stays unknown.

Coding prompt:

> Add one outcome-based evaluation for a rejected or expired proposal. Check the simulator state and approval result rather than matching the exact wording of an answer. Then make one prompt or retrieval change and compare the evaluation results.

Inspect a denied case as well as a successful one. Check that a viewer cannot retrieve restricted content even after an approver warmed the cache. Explain the limits of similarity scores and LLM-as-judge scoring.

Cloud deployment emits sanitized structured incident events to CloudWatch. OpenTelemetry export is optional; do not claim every LangGraph step appears in AgentCore's managed trace view unless instrumentation was configured and verified.

Check understanding: explain the difference between model quality, application-policy correctness, and service recovery.
