# Run RunbookOps locally

Use the `v2` branch. You need Git and [uv](https://docs.astral.sh/uv/getting-started/installation/). No AWS account, Kubernetes cluster, Docker, or paid model credits are required for the learner application.

The application has a CLI and an HTTP API with a browser API explorer. The explorer is at `/docs`; there is no separate chat frontend.

## 1. Open the project

For a new checkout:

```bash
git clone --branch v2 https://github.com/TrainWithShubham/agentic-ai-for-devops.git runbookops-course
cd runbookops-course
```

In the instructor's existing workspace, use the `repository` directory instead. Run every command below from the folder containing `pyproject.toml`.

## 2. Install and check setup

```bash
uv sync --frozen
uv run runbookops --mode offline --embedding hash preflight
```

uv installs the selected Python version and locked dependencies. Preflight indexes the supplied documents and checks the local components. It does not test a live model.

## 3. Run the complete offline demo

```bash
uv run runbookops --mode offline --embedding hash demo
```

Expected result:

```text
Checkout before approval: HTTP 503
Bagha approval: denied as expected.
Jethalal approval: accepted. Checkout after verification: HTTP 200.
```

This is explicitly offline practice. It exercises retrieval, tools, saved approval, and the simulator without calling a generative model. Each demo creates a new isolated incident. The report is saved to `.state/demo-latest.json`.

## 4. Start the HTTP application

In one terminal:

```bash
uv run runbookops --mode offline --embedding hash serve --port 8002
```

Keep that terminal open. Visit:

- API explorer: <http://127.0.0.1:8002/docs>
- Health: <http://127.0.0.1:8002/health>

Port 8002 is used here because another local service may already occupy 8000. You can choose another free port; use the same port in the client commands.

In another terminal, from the same project directory:

```bash
uv run python scripts/demo_api.py --base-url http://127.0.0.1:8002
```

The script verifies anonymous access is denied, starts an investigation as Bagha, checks Bagha cannot approve, approves as Jethalal, and verifies HTTP 200. It handles the development tokens without displaying them.

## 5. Run with a real free model

Create your own OpenRouter account and key. If `.env` does not exist, copy the supplied template:

```bash
cp .env.example .env
```

In PowerShell use `Copy-Item .env.example .env`. If `.env` already exists, edit it instead of replacing it.

Set `OPENROUTER_API_KEY` in that ignored file. Keep `RUNBOOKOPS_FREE_ONLY=true` and select a named free tool-capable model. The initial tested model is `nvidia/nemotron-3.5-lightning:free`; check current availability:

```bash
uv run runbookops models
uv run runbookops --embedding semantic index
uv run runbookops --mode openrouter --embedding semantic demo
```

Semantic indexing downloads a small local embedding model once. It needs no paid embedding API. Model availability and free quotas can change; an agent investigation can consume up to six model requests.

To run the API with live inference, stop the offline server with Ctrl+C, then start:

```bash
uv run runbookops --mode openrouter --embedding semantic serve --port 8002
```

Open `/health` and check that `mode` is `openrouter`. Run the HTTP demo from step 4 against it. Stop any server you started before launching a replacement on the same port.

If your key is already in another ignored file, you can read its model settings without copying it:

```bash
uv run runbookops --env-file /path/to/your/.env --mode openrouter --embedding semantic serve --port 8002
```

Never put the key itself in a command, screenshot, or Git commit. Claude Pro does not provide the application API key. See [model access](docs/MODEL_ACCESS.md) for limits and alternatives.

## 6. Try the API manually

Use the API explorer's **Authorize** button. Generate a short-lived development access token:

```bash
uv run runbookops --as bagha token
```

Paste the token into Authorize. This is a local development JWT, separate from your OpenRouter key.

1. Call `GET /me` to inspect Bagha's identity.
2. Call `POST /investigations` with a question such as `Investigate checkout HTTP 503 and prepare a correction for approval.`
3. Review the response's `proposal`, its `id`, exact `hash`, and planned configuration change. Health should still be HTTP 503.
4. Call `POST /proposals/{proposal_id}/decision` as Bagha with the reviewed hash. It must return HTTP 403.
5. Generate an approver token with `uv run runbookops --as jethalal token`, then replace the token in Authorize.
6. Submit the same decision using Jethalal's token:

```json
{
  "expected_hash": "PASTE_THE_EXACT_REVIEWED_HASH",
  "approve": true
}
```

The response should show HTTP 200 health and an applied proposal. Approval expires after 15 minutes; development tokens normally expire after 10 minutes. Generate a new token if needed. Restart the exercise with a new incident if its proposal expired.

The role flags and token issuer are development conveniences for learning on your own machine. They are not a production login system.

## 7. Inspect the evidence

```bash
uv run runbookops evaluate
uv run python scripts/trace_report.py
```

Open `artifacts/trace.html` to inspect the most recent CLI demo. The HTTP demo checks its own incident; it does not overwrite the CLI's `.state/demo-latest.json`. For API incident events, use `GET /incidents/{incident_id}/trace` with an authorized token.

The evaluator saves actual offline results to `artifacts/evaluation.json`. It does not score live model quality. To run regression tests:

```bash
uv run pytest -q
```

The optional AWS saver test is skipped without the AWS extra. Learner operation needs no AWS packages or resources.

## 8. Stop and restart

Press Ctrl+C in the server terminal. Local state stays under `.state`, so pending approvals can survive a restart. Restart with the same project directory, state location, model mode, and embedding configuration.

Serving locally does not deploy to AWS. The earlier instructor AWS deployment was deleted. Recreating it is a separate, billable instructor activity described in [the deployment guide](deploy/agentcore/README.md).

For missing dependencies, model limits, occupied ports, token errors, and embedding-download failures, see [troubleshooting](docs/TROUBLESHOOTING.md).
