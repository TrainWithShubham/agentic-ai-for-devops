# Module 6 — RunbookOps capstone and AgentCore demo

Day 2, 75 minutes. This is where we introduce the integrated application. Modules 1–5 have their own examples and do not require this repository.

RunbookOps lives in **[TrainWithShubham/runbookops](https://github.com/TrainWithShubham/runbookops)**. Gada Electronics has a simulated checkout failure. Bagha investigates, Jethalal reviews the exact proposed correction and the application verifies the resulting health state. The technical incident and responsibilities are fictional.

## Prepare the separate checkout

Complete the dependency download before the Day 2 session if you plan to follow the whole project. The concept labs remain runnable without it.

```bash
git clone https://github.com/TrainWithShubham/runbookops.git
cd runbookops
uv sync --frozen
uv run runbookops --mode offline serve --demo-auth --port 8002
```

Open http://127.0.0.1:8002/. The offline model path is deterministic and labeled. Follow the [beginner demo](https://github.com/TrainWithShubham/runbookops/blob/main/docs/BEGINNER_DEMO.md). Live model access uses your own key and the application guide; a subscription to a coding assistant does not supply an application API key.

## Guided session

| Minutes | Work |
|---|---|
| 0–5 | Introduce the scenario, separate repository and viewer/approver roles |
| 5–20 | Investigate from the UI; inspect prompts, tool results, RAG excerpts and a pending proposal |
| 20–35 | Make one bounded learner change and verify its effect |
| 35–45 | Deny viewer approval, review as an approver and verify recovery to HTTP 200 |
| 45–60 | Instructor demonstrates the same LangGraph agent on AgentCore Runtime |
| 60–70 | Inspect traces, saved state and evaluation outcomes |
| 70–75 | Save evidence and explain one improvement and limitation |

### Learner change

Choose one edit: improve the system response contract or add a synthetic knowledge sentence with source metadata. Review the diff. Reindex when changing documents. Run the application's documented relevant check and inspect the effect in the UI. Avoid redesigning authentication, swapping dependencies or modifying the frontend during this short exercise.

For the knowledge edit, use `resources/company-knowledge/checkout-runbook.md` in the application checkout. Add a short synthetic validation note, increment that entry's `version` and `updated` metadata in the manifest, then stop the local server and run:

```bash
uv run runbookops --mode offline --embedding hash index --rebuild
uv run runbookops --mode offline --embedding hash search "YOUR_NEW_SEARCH_PHRASE"
uv run runbookops --mode offline --embedding hash serve --demo-auth --port 8002
```

Start a new investigation after restarting, then inspect the new excerpt and citation. Do not reuse an old pending approval after changing its source. Keep the CLI and UI on the same embedding backend; changing only one would make the comparison misleading. Do not edit restricted-source permissions or add real credentials.

Use the [run guide](https://github.com/TrainWithShubham/runbookops/blob/main/RUNBOOK.md), [harness walkthrough](https://github.com/TrainWithShubham/runbookops/blob/main/docs/HARNESS_DEMOS.md) and [testing guide](https://github.com/TrainWithShubham/runbookops/blob/main/docs/TESTING.md). Do not claim a change worked until its observed result supports that claim.

## Instructor AgentCore demo

The previous deployment was deleted on November 12 at the owner's request. This course revision does not provision AWS resources. Recreate, rehearse and verify the deployment before class using the current [Terraform AWS guide](https://github.com/TrainWithShubham/runbookops/blob/main/docs/AWS.md). The previous GitHub deployment workflow is disabled and its environment configuration was removed; restore that setup only if using CI deployment.

Run the following from the **application** checkout after deployment:

```bash
uv sync --frozen --extra aws
uv run --extra aws python deploy/manage.py probe
uv run --extra aws python deploy/manage.py smoke
uv run runbookops present --runtime-arn YOUR_RUNTIME_ARN
```

Open http://127.0.0.1:8005/. `smoke` makes billed Bedrock calls. Keep AWS credentials and the demo private signing key on the instructor laptop. Learners do not need AWS accounts or access to the instructor's credits.

Show the actual streamed investigation, discovered MCP tools, retrieved sources, pending proposal and durable approval state. Deny a viewer's approval, then approve through a fresh session and inspect the verified health result. Explain the boundaries:

- LangGraph owns the agent loop; AgentCore Runtime hosts it.
- Managed AgentCore Harness is a separate managed loop, not the hosting wrapper for this LangGraph project.
- IAM admits the cloud invocation; application identities still enforce the viewer/approver boundary.
- The browser/API bridge stays local; durable cloud state is stored separately from runtime memory.
- The operational correction is a simulator action. An optional read-only CloudWatch source is not a production remediation integration.

Use [costs and shutdown](https://github.com/TrainWithShubham/runbookops/blob/main/docs/COSTS.md). Stop/review/delete the dedicated AWS resources after the demonstration. A local server shutdown does not remove cloud storage or the runtime configuration.

If the live demo fails, label the saved [release verification](https://github.com/TrainWithShubham/runbookops/blob/main/docs/VERIFICATION.md) as historical evidence and continue the local capstone. Do not present saved traces as a new invocation.

## Completion evidence

Save the diagnosis and sources, reviewed proposal, viewer denial, authorized recovery result and a sanitized trace. Explain which operations ran locally, which used a live model and which were an instructor cloud demonstration. Record one failed/refused case and the result of the learner's edit.

An interview explanation should describe actual participation. Watching the cloud demonstration does not mean the learner independently deployed the application.
