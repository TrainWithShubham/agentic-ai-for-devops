# Module 6: RunbookOps capstone

**Day 2 · 75 minutes** · [Previous](../module-5/README.md)

Bring the concepts together in a complete application. You will follow an investigation, inspect its sources, prepare a correction and see an authorized person approve it.

RunbookOps is in **[its own repository](https://github.com/TrainWithShubham/runbookops)**. Gada Electronics has a simulated checkout problem. Bagha investigates and Jethalal reviews the proposed correction. The story and incident are fictional; the application does not change a production service.

## 1. Open the application

Use a new terminal so it is clear which project you are running. Complete the download before Day 2 if you plan to follow along.

```bash
git clone https://github.com/TrainWithShubham/runbookops.git
cd runbookops
uv sync --frozen
uv run runbookops --mode offline --embedding hash preflight
uv run runbookops --mode offline --embedding hash serve --demo-auth --port 8002
```

Already have this checkout? Open its folder instead of cloning again. These commands run in `runbookops`, not in the course folder. Open **http://127.0.0.1:8002/** when the server starts. Keep that terminal running; press Ctrl+C when you want to stop it.

You need no AWS account or model key for this path. `offline` uses prepared model behavior. `hash` is a deterministic teaching representation, not a learned semantic embedding model. `--demo-auth` selects teaching identities; it is not a production login.

Use the application's [current run guide](https://github.com/TrainWithShubham/runbookops/blob/main/RUNBOOK.md) if commands differ from your checkout. For a terminal-only walkthrough, `uv run runbookops --mode offline --embedding hash demo` should show a denied approval, an accepted authorized approval and simulated health changing from HTTP 503 to HTTP 200. That is the documented expected result, not evidence that you have run it yet.

## 2. Follow an investigation

Try this request:

> Checkout is not working. Suggest a fix, but ask a person before changing anything.

Inspect the tool cards, company-note excerpts and pending proposal. The proposed correction should remain unapplied until an authorized review. Use Try approving as Bagha, then Review as Jethalal. Bagha's request should be denied; Jethalal can approve the exact correction. Check the resulting health observation instead of trusting the word “fixed”.

Ask yourself: which steps read evidence, which step prepared a proposal, and which step changed simulator state?

## 3. Make one small change

Choose either a clearer system response instruction or one synthetic sentence in `resources/company-knowledge/checkout-runbook.md`. Review the diff. Avoid changing authentication, dependencies or the frontend during this exercise.

For a document change, increment its `version` and `updated` values in the knowledge manifest. Stop the server with Ctrl+C, then run from the application folder:

```bash
uv run runbookops --mode offline --embedding hash index --rebuild
uv run runbookops --mode offline --embedding hash search "YOUR_NEW_SEARCH_PHRASE"
uv run runbookops --mode offline --embedding hash serve --demo-auth --port 8002
```

Replace the quoted phrase with words from your new sentence. Check that the search returns the edited passage and source location. Start a new investigation after restarting. Keep the CLI and UI on the same embedding backend; do not reuse an old approval after its supporting source changed.

Offline model text is prepared. A prompt change may not alter the generated-looking answer in this mode. You can still inspect the stored instructions; assess model behavior separately in an explicitly configured live run. Do not add credentials or edit restricted-source permissions.

## 4. Watch the instructor's cloud demonstration

The instructor may show this LangGraph agent hosted on **AgentCore Runtime**. You do not need to create AWS resources or copy the instructor's credentials. Observe which calls use the cloud and which actions still affect only the simulator. Managed AgentCore Harness is a different managed-loop option.

| Minutes | Your activity |
|---|---|
| 0–5 | Understand the incident and teaching roles |
| 5–20 | Investigate and inspect sources/tools |
| 20–35 | Make and check one learner change |
| 35–45 | Compare denied and authorized approval, then inspect health |
| 45–60 | Watch the instructor's AgentCore demonstration |
| 60–70 | Follow traces, saved state and evaluation results |
| 70–75 | Save your result and explain its limits |

Watching the cloud demonstration does not mean you deployed the application yourself. If it is unavailable, continue the local capstone; any recorded cloud example should be labeled historical.

## Finish your capstone

Save the diagnosis and sources, reviewed proposal, denied request, authorized simulator result and one sanitized trace. Record your own edit and its observed result. State whether model calls were prepared or live, and which cloud steps you only watched.

If the UI does not open, keep the server terminal visible and read its error. If port 8002 is occupied, choose `--port 8003` and open that port in the browser. Use the [application run guide](https://github.com/TrainWithShubham/runbookops/blob/main/RUNBOOK.md) for further recovery.

<details>
<summary>Instructor: cloud preparation and cleanup</summary>

Use the separate [AgentCore demonstration guide](../instructor/AGENTCORE_DEMO.md). Learners should not run those deployment or billed smoke-test commands.

</details>

**You have finished the course.** Explain one design decision, one failed/refused case and what would need to change before connecting real infrastructure.
