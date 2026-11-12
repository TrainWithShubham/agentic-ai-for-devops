# Agentic AI for DevOps

A two-day live workshop on November 14 and 15, 2026. Three hours each day, including breaks and questions.

Build RunbookOps, an assistant for Gada Electronics' online store. Checkout is returning HTTP 503. The assistant reads company documents, checks operational evidence, and prepares a correction. Bagha can investigate; Jethalal must approve the exact change before it runs.

The store's online system and incident are fictional. The code operates on a simulator, so learners need no Kubernetes cluster or AWS account.

## Run it

For installation, CLI use, the browser API explorer, live models, and shutdown, follow the [step-by-step run guide](RUNBOOK.md).

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run these commands from this repository:

```bash
uv sync --frozen
uv run runbookops preflight
uv run runbookops demo
```

The default is clearly labeled offline practice. The demo checks Bagha cannot approve, reloads persisted graph state, approves as Jethalal, and verifies checkout returns HTTP 200. It saves evidence under `.state/demo-latest.json`.

For semantic retrieval, download the small embedding model before class:

```bash
uv run runbookops --embedding semantic index
uv run runbookops --embedding semantic search "checkout payment connection refused"
```

Hash mode is an offline lexical fallback. Semantic mode uses local embeddings and Chroma; it needs no paid embedding API.

## Open the visual harness

```bash
uv run runbookops --mode offline serve --demo-auth --port 8002
```

Open [localhost:8002](http://127.0.0.1:8002/). The TWS-themed console has an agent pane, a visual harness inspector, and an event strip. Inspect the prompt, RAG context, actual MCP discovery, tool schemas, saved state, and human approval. Light and dark themes are included. The same UI works with live OpenRouter mode.

The persona picker is an opt-in local learning shortcut. Model keys stay on the server, and the existing API authorization and approval checks still run. See [the run guide](RUNBOOK.md).

## Use a live free model

Create your own OpenRouter account and API key. Copy `.env.example` to `.env` and add your key there. Keep `RUNBOOKOPS_FREE_ONLY=true`.

```bash
cp .env.example .env
uv run runbookops models
uv run runbookops --mode openrouter --embedding semantic demo
```

The initial tested model is `nvidia/nemotron-3.5-lightning:free`. Check the current catalog before the workshop. Free capacity and quotas can change. The application rejects nonfree OpenRouter choices in free-only mode and never silently switches to paid inference.

Claude Code or Codex can help with edits. A Claude Pro subscription does not provide this application's API access. Paid coding tools are optional; examples, an exercise solution, and recovery commands are included. See [model access](docs/MODEL_ACCESS.md).

## The two days

| Day | What learners build |
|---|---|
| Day 1 | A bounded investigator using system instructions, a health tool, company RAG, and MCP |
| Day 2 | Role checks, saved human approval, guardrails, caching/routing configuration, traces, and evaluations |

The instructor demonstrates the same LangGraph application on AgentCore Runtime. Managed AgentCore Harness is a separate architecture, explained briefly. Instructor AWS credits are not shared with learners.

- [Full curriculum and timing](CURRICULUM.md)
- [All lessons and coding prompts](lessons/README.md)
- [Setup](lessons/00-setup/README.md)
- [Recovery checkpoints](checkpoints/README.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security and identity boundaries](docs/SECURITY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Instructor start page](instructor/START_HERE.md)
- [Instructor teaching notes](instructor/TEACHING_NOTES.md)

## Check the result

```bash
uv run runbookops evaluate
uv run pytest -q
uv run python scripts/trace_report.py
```

The evaluation report records actual pass/fail outcomes. Offline tests check application behavior; they do not claim live model quality. The HTML trace is written to `artifacts/trace.html`.

For the optional AWS backend tests and deployment tools:

```bash
uv sync --frozen --extra aws
uv run pytest -q
```

Live OpenRouter, Bedrock, local HTTP/stdio MCP, and AgentCore Runtime have been exercised separately. Read [verification results](instructor/VERIFICATION.md) for the exact scope and remaining limits.

## Inspect the HTTP API

```bash
uv run runbookops serve
```

Open `http://127.0.0.1:8000/docs`. In another terminal, `uv run python scripts/demo_api.py` demonstrates the authenticated flow without displaying tokens. See [API instructions](docs/API.md).

## Code and resources

| Path | Contents |
|---|---|
| `src/runbookops` | Graph, providers, retrieval, tools, permissions, stores, API, and CLI |
| `examples` | Small runnable examples used before the full project |
| `exercises` and `solutions` | Isolated learner exercise and completed version |
| `resources/company-knowledge` | PDF, DOCX, PPTX, MD, and TXT documents with source/access metadata |
| `resources/sources` | Editable text and slide source for the synthetic documents |
| `tests` | Meaningful application, transport, approval, and provider-boundary checks |
| `deploy/agentcore` | Instructor build, deployment, invocation, update, log, and cleanup tools |
| `.devcontainer` | Browser development environment for Codespaces |

Run from the `v2` checkout and use the locked uv environment.

## Instructor AWS demo

The tested cloud deployment was deleted on November 12 (India time) at the instructor's request to avoid further resource charges. Recreate it using the deployment guide before running:

```bash
uv run --extra aws python deploy/agentcore/invoke.py
```

The [deployment guide](deploy/agentcore/README.md) covers recreation and cleanup. It uses DynamoDB to preserve approval and graph state across Runtime sessions. Keep the local development signing key while using that deployment. Credentials and state are ignored by Git.

## Course branches

- `v1`: the original course, including Docker tools, KubeHealer/Temporal material, and the CI/CD analyzer.
- `v2`: this RunbookOps course, its lessons, resources, and tests.

The editions live on separate local branches. Switch editions with `git switch v1` or `git switch v2` after saving your work. V1 setup instructions are in its own README.

The course editions are published on separate `v1` and `v2` branches; `main` remains unchanged. [DECISIONS.md](DECISIONS.md) records the implementation choices, failures, and fixes.

For screen sharing, open **Demo prompts** in the console. [The teaching walkthrough](docs/HARNESS_DEMOS.md) maps ten examples to harness features and includes a 15-minute demo order.
