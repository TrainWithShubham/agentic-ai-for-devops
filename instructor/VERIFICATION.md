# Verification on 11 November 2026

The learner capstone and instructor cloud demonstration were run successfully. These results apply to this branch and the tested environment: macOS ARM64, uv 0.10.2, Python 3.12.12, and the committed lockfile. The cloud image is Linux ARM64.

## Results

| Check | Observed result |
|---|---|
| Full regression suite, including mocked AWS persistence | 31 passed; one upstream Authlib deprecation warning |
| Outcome evaluation runner | 13 passed, 0 failed; explicitly offline |
| Ruff | Passed for new source, examples, scripts, tests, and deployment code |
| Separate clean-directory install | Frozen lockfile installed with no `.env`, `.state`, or previous virtual environment |
| Clean learner flow | Preflight, demo, evaluations, all local examples, identity checks, exercise solution, and trace export passed |
| Semantic retrieval | Real local FastEmbed model and Chroma; current runbook retrieved with source locations |
| Mixed-format documents | PDF, DOCX, PPTX, MD, and TXT extracted; policy, Word report, and all three architecture slides rendered and visually checked |
| MCP | Real in-process and stdio client/server exchanges; signed-token HTTP MCP call on localhost passed |
| HTTP API | Anonymous request denied, viewer approval denied, approver recovery verified; separate API tests cover scope/audience/ownership |
| OpenRouter | Free account and structured tool exchange verified; final semantic-RAG capstone completed in five model calls |
| Bedrock | Nova Lite Converse and full application flow passed using instructor credentials |
| AgentCore Runtime | Updated endpoint version 2 invoked successfully; Bagha investigated, Bagha approval was denied, Jethalal approved in another Runtime session, checkout returned HTTP 200 |
| Cloud logs | Sanitized JSON incident events retrieved from CloudWatch; no claim of automatic native graph traces |

The clean learner suite skips the optional AWS saver test when the AWS extra is absent. The instructor suite installs that extra and runs it against Moto, not a paid live database. Live cloud behavior was checked separately through the deployed endpoint.

## Reviewable evidence

- [Live OpenRouter capstone](evidence/openrouter-capstone.json): actual source/tool events, five model responses, denied approval, authorized execution, and verification.
- [Live AgentCore capstone](evidence/agentcore-capstone.json): investigation and recovered states, viewer denial, and separate Runtime-session approval.
- [Offline evaluation results](evidence/offline-evaluation.json): thirteen actual application checks; `live_model_quality_tested` is false.
- [CloudWatch events](evidence/agentcore-events.json): sanitized events from the final cloud incident.

These are saved results from November 11. They are useful fallback evidence when the network fails; they are not a fresh live run. Approval IDs in these records are historical and should not be reused.

Generate an interactive local trace from the saved OpenRouter evidence:

```bash
uv run python scripts/trace_report.py --input instructor/evidence/openrouter-capstone.json
```

Open `artifacts/trace.html`. The viewer expands each event so learners can inspect evidence and policy transitions without exposing private model reasoning.

## Measured learner request budget

The final live OpenRouter investigation used five model calls and 7,980 total tokens summed across requests. The provider reported cost zero for each call. Repeated context counts again in those token totals. Approval and resume made no additional inference calls. An earlier bounded run reached six calls; the implementation now stops as soon as a validated proposal exists.

| Activity per learner per day | Reserved model calls |
|---|---:|
| Provider tool smoke check | 2 |
| First-call prompt comparison | 2 |
| Simple health-tool exchange | 2 |
| Three RAG questions | 3 |
| Two complete investigations at the enforced maximum | 12 |
| Retry allowance | 6 |
| Total planned maximum | 27 |

This is a teaching allocation, not a measured timed delivery of every activity. The documented free allowance is currently 50 requests/day, but public provider capacity, account limits, failed attempts, and synchronized demand can affect class. Each learner needs an independent account. Recheck the catalog and tool exchange on November 13.

## Repeat the checks

```bash
uv sync --frozen --extra aws
uv run ruff check src examples scripts tests deploy
uv run pytest -q
uv run runbookops demo
uv run runbookops evaluate
uv run python scripts/verify_docs.py
uv run python examples/mcp_client.py
uv run python scripts/demo_identity.py
```

For live free inference, configure your own ignored `.env`, then run:

```bash
uv run runbookops --mode openrouter --embedding semantic demo
```

For the existing instructor deployment:

```bash
uv run --extra aws python deploy/agentcore/invoke.py
uv run --extra aws python deploy/agentcore/logs.py
```

## Limits and remaining instructor preparation

A timed teaching rehearsal and a volunteer group rehearsal still need the instructor and real attendees. Windows execution, Codespaces provisioning, and GitHub Actions have not been run from this environment. The devcontainer and workflow are supplied. These results describe the original local verification; subsequent CI results appear in GitHub Actions.

Groq is implemented and documented but has no live test because no Groq key was supplied. The optional PostgreSQL store, production OAuth login/consent, managed AgentCore Harness creation, Gateway/Identity, Managed Knowledge Bases, Bedrock Guardrails, full managed trace export, and Temporal are extensions. They are not presented as completed live integrations.

The simulator proves an approved configuration transition and recovery within this teaching system. It is not evidence of production incident remediation or a complete AIOps platform. Live model answers still need source-support review; passing deterministic controls does not prove hallucination or prompt injection is impossible.

The tested AWS deployment was subsequently deleted on November 12 (India time) at the instructor's request. Historical evidence remains in this repository. Recreate the deployment before another live cloud demonstration; the learner capstone still works locally.

[Cleanup verification](evidence/aws-cleanup.json) confirms every recorded workshop resource is absent. The local capstone and historical live evidence remain available.

## TWS visual harness follow-up

The UI addition passed 37 local tests, with the optional AWS saver test skipped without the AWS extra. Checks cover explicit loopback persona issuance, host/origin restrictions, disabled cloud/external-issuer issuance, source permissions, actual MCP discovery/schema exposure, streamed events, disconnect cancellation, and the approval boundary. Ruff, JavaScript syntax, local links, and the wheel asset check passed.

The final TWS palettes were measured for normal foreground text against their associated surfaces; tested pairs exceeded 4.5:1 in light and dark mode. Both themes and an offline approval/recovery were observed in Safari. Exact small-device viewport testing was not completed; responsive styles are supplied without claiming a full device audit.

A fresh live streamed OpenRouter capstone used five model calls, rejected Bagha's approval, and recovered to HTTP 200 after Jethalal's approval. [Sanitized harness evidence](evidence/harness-live.json) includes public model responses/requested tools and actual tool/node events. Hidden reasoning and provider credentials are excluded. AWS resources remain deleted.

### Shared-screen UI pass

The follow-up changed frontend presentation and demo guidance. Seven existing UI/API tests passed; Ruff, both JavaScript syntax checks, and links in 33 Markdown files passed. Safari desktop checks confirmed ten demo cards, task selection without execution (Idle and zero events), RAG probe selection, and a real Fresh → Cache hit transition. Both theme directions were visually checked after the Safari palette fix. The live server on port 8002 remained healthy and served the new demo module. This pass did not rerun adversarial prompts against a live model, deploy AWS resources, or validate phone-sized layouts. The larger dark screenshot is saved locally at `artifacts/ui/shared-screen-dark.png`.

### Provider recovery — November 12

The earlier NVIDIA route timed out at 60 seconds on both the user run and a direct inference probe; catalog and key requests returned HTTP 200. Explicitly switched the current free default and the local port-8002 server to `cohere/north-mini-code:free`. The restarted server completed a real streamed investigation in 5.6 seconds with two model calls and a valid proposal. Viewer approval returned 403; authorized approval recovered the simulator to HTTP 200. Sanitized evidence: `instructor/evidence/provider-recovery.json`. Full suite: 38 passed, one optional test skipped; Ruff and 33-file documentation checks passed. No AWS resources were created.

### Local Bedrock app — November 12

Nova Lite (`us.amazon.nova-lite-v1:0`, `us-east-1`) passed a real CLI capstone, including restart/resume and denied/authorized approval. It also passed permission-claim and unsafe-command checks without an unauthorized simulator change. A separate local server runs on port 8004. In Safari, the updated app called all five tools, retrieved runbook evidence, denied Bagha's approval, and recovered checkout to HTTP 200 after Jethalal approved. The browser investigation used five model calls in about seven seconds. The CLI baseline used two calls in 4.43 seconds; order and counts vary.

Filtered Nova's tagged reasoning text before public persistence and verified the new browser trace contains none. Full suite: 41 passed, one optional test skipped; Ruff and 34-file local-link checks passed. No cloud hosting resources were created. Existing local AWS credentials authenticated the real calls; a Bedrock bearer API key was not configured or tested. Evidence: `instructor/evidence/bedrock-local-verification.json`. Setup: [Bedrock demo](../docs/BEDROCK_DEMO.md).

### Beginner prompts and UI — November 12

The short question “Customers cannot pay at Gada Electronics. Can you check what is wrong?” returned a diagnosis after health, logs, and deployment checks. The separate prompt “Checkout is not working. Suggest a fix, but ask a person before changing anything.” invoked all five tools and prepared a pending proposal in 3.34 seconds on Nova Lite, with two model calls. No fix was applied. Evidence: `instructor/evidence/beginner-prompt.json`.

Safari desktop showed friendly tool labels, collapsed replies/metadata, and four starter cards with six more under a disclosure. Regression results: 41 Python tests passed, one optional skip; four Node error-guidance tests passed (`node --test tests/ui_learning.test.mjs`). Ruff, syntax checks, and local links in 35 Markdown files passed. Phone-sized layouts were not rechecked in this pass. Start with [the beginner walkthrough](../docs/BEGINNER_DEMO.md).

### Complete application coverage — November 12

Final local results: **144 Python tests passed**, **32 JavaScript tests passed**, and **four explicit live Bedrock scenarios passed**. With AWS test extras installed there are no skipped deterministic tests. Python application coverage is 100% for 1,432 statements and 382 branches across all `src/runbookops` modules. JavaScript application coverage is 100% for lines, statements, functions, and branches across all four `web/*.js` modules. No application source exclusions were used. Coverage gates fail below 100%. The offline evaluator passed 13/13 outcomes; Ruff, links in 36 Markdown files, wheel asset checks, and npm audit passed.

The final Safari desktop flow used Nova Lite on port 8004: simple prompt → required checks and runbook → pending proposal → viewer denial → authorized review/approval → HTTP 200. The completion reminder was exercised in this real browser run. Five MCP tools were discovered, semantic RAG results were inspected, the repeated query showed a cache hit, and both themes were checked.

Earlier repeated live attempts did reveal missing proposal/completion and runbook retrieval failures. The app now gives bounded corrective guidance; the final four-scenario live suite passed. This is sampled live verification, not a guarantee of deterministic model quality. Contract tests cover PostgreSQL/checkpointer wiring; Moto covers DynamoDB; JSDOM covers UI logic; provider contracts use mock transports/Stubber. Real production infrastructure, other browsers, and phone-sized layouts were not tested in this pass. No AWS hosting resources were created. Follow [Testing](../docs/TESTING.md); summary: `instructor/evidence/test-coverage.json`.
