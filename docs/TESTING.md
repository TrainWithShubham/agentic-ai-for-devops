# Test the course application

Run these commands from the repository directory. Coverage is a measure of executed code, not a promise that an AI provider will always answer correctly.

## Offline regression tests and coverage

```bash
uv sync --frozen --extra aws
uv run --extra aws pytest --cov=runbookops --cov-branch \
  --cov-report=term-missing \
  --cov-report=json:artifacts/coverage/python.json \
  --cov-report=html -q
npm ci
npm run test:coverage
uv run --extra aws runbookops evaluate
uv run python scripts/verify_docs.py
```

The JavaScript test tooling needs Node.js 26 or newer. Node.js is not required to run the Python web app or attend the learner labs.

The gates require:

- **Python:** 100% statement and branch coverage of every module under `src/runbookops`, including the CLI, providers, auth, API, RAG, MCP, and optional storage adapters.
- **JavaScript:** 100% statement, branch, function, and line coverage of every `.js` file under `src/runbookops/web`.

No application files or lines are omitted from those scopes. Templates, CSS, fonts, binary assets, instructor deployment scripts, dependencies, and test code are not executable application coverage. Reports stay in the ignored `artifacts/coverage` folder; the recorded verification summary is in `instructor/evidence/test-coverage.json`.

The Python tests exercise real SQLite transactions, graph checkpoints, mixed-format extraction, Chroma retrieval, stdio MCP, a separate HTTP MCP process with JWT admission, and the HTTP/NDJSON API. DynamoDB uses Moto. PostgreSQL connection and query paths use a local adapter contract test; the PostgreSQL checkpoint path uses a saver contract test. HTTP model providers and Bedrock response conversion use mock transports and SDK Stubber. Semantic embedding vectors use a test double in the deterministic coverage suite.

The JavaScript suite runs the actual application modules in JSDOM with a controlled HTTP boundary. It checks rendering, errors, partial NDJSON chunks, token refresh, stale identities, approval controls, source inspection, keyboard navigation, theme startup, storage failure, and trace export. JSDOM tests do not establish real CSS layout or screen-reader behaviour. Native Safari visual checks and live Bedrock results are separate evidence.

To run a focused Python test while developing, use `uv run --extra aws pytest tests/NAME.py --no-cov -q`. A partial suite is not expected to meet the full-application coverage gate.

## Explicit live Bedrock checks

These make billed inference requests using the local AWS SDK credential configuration or a configured Bedrock bearer token. They never create cloud hosting resources. The simulator stays local.

```bash
RUNBOOKOPS_ENABLE_PAID_TESTS=true uv run --extra aws pytest -q tests/live_bedrock.py
```

The file is deliberately outside normal `test_*.py` discovery, so CI does not need AWS credentials or spend inference credits. There are four live scenarios: approved recovery, rejection, permission claim, and an unsupported destructive request. The full recovery checks approval denial, process restart/resume, HTTP 200, and idempotent replay. Live tests use a bounded eight-call budget for the instructor model; the learner default remains six calls.

A model may refuse an unsafe request or offer a valid, pending alternative suggestion. The enforced safety requirement is that it cannot execute arbitrary commands, change permissions, or apply an unapproved fix. A valid alternative proposal must still satisfy the same evidence and approval checks.

Successful scenario summaries are saved to `artifacts/live-bedrock`. Test failures remain failures: do not turn them into offline fallbacks or count a rerun as a reliability benchmark. Model output, quotas, and service availability vary. The application now gives one bounded completion reminder after partial checks, and tool-validation errors provide a safe next action for retrieving the required runbook.

## Browser end-to-end check

Open the instructor Bedrock app on port 8004. Use the four starter examples, then inspect the technical System prompt, Model, MCP tools, RAG, Approval, and Execute components. Verify a viewer's denial and an authorized approval or rejection. Check RAG retrieval/cache, saved work, theme switching, keyboard tabs, and the original diagnostic disclosure on errors. Follow [the beginner walkthrough](BEGINNER_DEMO.md).

The GitHub workflow runs the deterministic coverage gates and offline evaluations on `v2`. It uploads reports even when a check fails. Live inference is opt-in and is not part of CI.
