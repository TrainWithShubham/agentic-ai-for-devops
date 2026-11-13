# Decisions and build notes

Work completed on 11 November 2026 for the November 14 and 15 workshop. This records the choices made while building the course and the failures that changed the implementation.

## Repository and scope

The initial build used `course-v2-runbookops` and preserved the previous modules in the same checkout. The instructor later requested separate editions: `v1` preserves the original course and `v2` contains only the new course. Do not push to GitHub, open a PR, merge, or invent a historical release tag. The root workspace holds the curriculum; the actual Git checkout is in `repository`.

Use one capstone across both days. Gada Electronics and the named characters provide a familiar fictional setting. Their online store, incident, and operational duties are course inventions. Technical names and error messages remain descriptive.

Use a completed application with small examples, bounded edits, one isolated starter exercise, a solution, and executable recovery points. This avoids maintaining many divergent copies or making beginners switch branches during class.

## Models and learner cost

Learners use individual OpenRouter keys. Instructor AWS credits are reserved for instructor Bedrock and AgentCore demonstrations. No sponsored learner gateway is built.

Claude Pro can provide Claude Code access, but it does not pay for the Python application's API calls. A paid coding subscription is optional. The course includes reviewed code and prompts so learners without one can participate.

Use an explicit free model and validate its current zero input/output pricing before inference. Do not silently select a paid model. Groq remains a supported alternative adapter, but no Groq key was available for a live test. Gemini is documented as another option, not an implemented core adapter.

The initial free candidate, `nvidia/nemotron-3.5-lightning:free`, passed a structured health-tool exchange and the full capstone. The account reported `is_free_tier=true` with a 50-request daily limit. Observed test calls reported zero model cost. This validates our tested runs, not guaranteed capacity for 100 simultaneous attendees.

Keep the full investigation at six model calls maximum and 16 tool calls maximum. Run regression checks offline. Target fewer than 30 model calls per learner per day, leaving space below the currently documented 50-request free cap.

## Framework and state

Use Python 3.12 and a committed uv lockfile. Python 3.11 through 3.13 are supported. The machine's default Python was newer; explicitly selecting 3.12 avoids unsupported native-library combinations in the class.

Use LangGraph directly with small provider adapters and a visible tool loop. FastMCP exposes the operational tools. This keeps the model/tool protocol readable while using the framework for state, approval, and resume.

Local operations and checkpoints use separate SQLite files. Incident investigations are bounded and can be retried; approval is a durable graph checkpoint. A crash inside the investigation can repeat read/model calls. The course does not claim every individual LLM turn has an exactly-once guarantee.

Cloud operations use one bounded DynamoDB aggregate per incident with conditional version writes. The maintained DynamoDB LangGraph saver holds checkpoints with consistent reads. This replaces the earlier planned PostgreSQL cloud setup and avoids a database server/VPC prerequisite. The optional PostgreSQL adapter is not the deployed or verified route.

The model has no apply tool. It can only prepare a proposal after current operational evidence and the current runbook were retrieved. The executor checks the exact hash, authorized approver, expiry, allowlist, current revision, and old value. Applying a proposal twice does not repeat the effect.

## Retrieval and documents

Supply eight synthetic documents in PDF, DOCX, PPTX, MD, and TXT. Preserve page, slide, paragraph/table, or heading locations. Keep editable source text and a manifest. Scanned PDFs, diagram interpretation, speaker-note extraction, and legacy PPT conversion are extensions, not silently simulated features.

Use local semantic embeddings with FastEmbed and Chroma. Include lexical feature hashing as a fully offline fallback and label it accurately. It is not a downloaded semantic model.

Filter access and superseded versions before returned chunks enter model context. Cache keys include identity/role/scopes and the corpus fingerprint. Hash content and metadata, not just the question. Operational reads and change execution bypass this retrieval cache.

The model validates evidence IDs against what was actually retrieved. Similarity is a retrieval signal, not a correctness probability. Model answer quality and claim support still require the manual rubric; deterministic policy tests are reported separately.

The available artifact runtime loader was not exposed in this environment. DOCX/PDF fixtures were generated locally and rendered for visual review. PPTX was converted from editable flat OpenDocument source using LibreOffice. The bundled DOCX renderer initially lacked `pdf2image`; installing that QA helper allowed its render-and-inspect check. No presentation-authoring Python API was used.

## Identity and the cloud deployment

CLI `--as` roles are explicit development shortcuts. The HTTP API verifies RS256 tokens, issuer, audience, expiry, subject, and scopes. Roles come from a known server-side subject mapping. A caller cannot gain Jethalal's role through a model message or request field.

The local issuer exposes discovery and JWKS for the lesson. It is not a complete production OAuth consent/authorization server. External issuer configuration is supported and separately documented.

AgentCore Runtime hosts the existing LangGraph code. Managed AgentCore Harness owns a separate managed loop, so it is compared rather than used to host the graph.

The instructor deployment uses IAM Runtime admission and an allowlisted signed application token header. It is not presented as production OAuth SSO. Only the public verification key enters the runtime configuration; the private signing key stays in ignored local state.

The cloud image includes the embedding model and uses the same in-process MCP tool implementation. An authenticated remote HTTP MCP exercise was also tested, but is not a dependency of the cloud capstone. No cloud component attempts to call a learner's localhost.

The execution role has project-scoped permissions. The tested trust policy follows AWS's documented source-account/region pattern. Runtime-ARN-only and runtime-ARN-plus-suffix conditions both produced role-assumption errors in this deployment. Account-and-region scoping worked. Do not claim a narrower condition was verified.

CloudWatch receives sanitized structured events. Full native AgentCore trace instrumentation, managed evaluations, Gateway, managed RAG, and Bedrock Guardrails are extensions. Local scenario evaluations and trace inspection are implemented.

## Failures and fixes

| What failed | What changed |
|---|---|
| Earlier sandbox requests could not resolve external hosts | Retried after the user enabled unrestricted access; distinguished DNS failures from later TLS failures |
| System Python could not validate the HTTPS certificate chain | Used the trusted system CA bundle; the smoke script now adds it when available. Certificate verification stays enabled |
| A live model supplied descriptive evidence names | Added exact source/tool enums and kept server-side checks against retrieved evidence |
| Waiting for an extra model summary wasted the free call budget | Stop once a validated proposal exists; generate a labeled application summary from that proposal |
| A test expected the evidence-state check before schema validation | Used valid schema arguments for that test, keeping the distinct schema and state checks intact |
| Runtime environment rejected literal PEM newlines | Escape newlines in configuration and decode them in the application |
| IAM trust update used the create-role parameter name | Use `PolicyDocument` for `UpdateAssumeRolePolicy` |
| Exact-runtime trust prevented execution-role assumption | Applied the documented account/region SourceArn condition while retaining project-scoped permissions |
| A committed effect could outlive an executor crash | Resume pending graph nodes with no new input; the idempotent executor returns the existing result |
| The first DOCX render retained a blue title rule | Removed inherited paragraph borders and set a plain black title, then rendered again |

## Verification and limits

Read `instructor/VERIFICATION.md` for the current test results and command evidence. Local API, stdio MCP, authenticated HTTP MCP, semantic retrieval, live free OpenRouter, Bedrock, and cross-session AgentCore recovery have each been exercised.

Do not equate a passing offline suite with live-model quality. Public free-provider capacity, every learner's network/account, Windows execution, and a real 100-attendee rehearsal cannot be guaranteed from this machine. Codespaces files and CI are supplied; GitHub has not been pushed or run for this build.

AWS workshop resources were initially kept available for the course; the instructor later requested their removal. See the cleanup record below. No real production service is modified. API credentials, private issuer keys, deployment records, local traces, and model caches stay out of Git.

## Final rehearsal notes

A separate directory with no state, keys, or environment installed the frozen learner dependencies and passed preflight, the offline capstone, evaluations, small examples, stdio MCP, identity checks, exercise solution, and trace export. The optional AWS saver test is skipped without the AWS extra; the full instructor suite ran 31 tests successfully with it.

The final OpenRouter semantic-RAG capstone used five model calls and recovered to HTTP 200 after authorized approval. Save the sanitized evidence in `instructor/evidence`; keep current working state ignored. The instructor cloud endpoint was updated to image version 2 and the cross-session capstone passed again. CloudWatch JSON events were read back rather than inferred from deployment readiness.

Fixed a lint issue in the documentation-check script. Made fixture regeneration find LibreOffice on PATH or its macOS location, use an isolated temporary profile, and create the incident-fixture directory. Learners use the supplied files and do not need LibreOffice.

Keep the tested in-process cloud MCP topology in the curriculum; remote HTTP MCP is a separately tested exercise. Removed planning-only and PostgreSQL claims from the delivered curriculum. Signed development JWTs teach validation and scope checks; a complete OAuth login server remains an extension.

The existing public free account was used only for a few instructor verification runs. No shared learner key or key copied into the repo was introduced. The final measured request budget supports a 27-call daily lesson allocation including retries, but is not a promise about public capacity or a substitute for a human teaching rehearsal.

Git treated the small generated PDF as text and reported whitespace inside its cross-reference table. Marked PDF, DOCX, and PPTX as binary in `.gitattributes`; their file content remains unchanged. The candidate-file secret check found no match for the actual provider key and no private PEM material. Temporary local HTTP servers were stopped after verification so teaching ports are available.

## AWS cleanup requested on November 12 (India time)

The instructor asked to delete the AWS resources after reviewing billing. Limit cleanup to the recorded RunbookOps deployment in us-east-1; leave unrelated account resources alone. Keep source code, synthetic documents, local practice, and sanitized historical evidence.

Removed the two DynamoDB tables, ECR repository with all images, dedicated IAM role and inline policy, and both Runtime CloudWatch log groups. AWS requires custom endpoints to finish asynchronous deletion before accepting runtime deletion; an immediate runtime delete returned ConflictException. Waited for the workshop endpoint to disappear, then requested runtime removal. Updated the cleanup script to wait for endpoints and table deletion and tolerate an already-removed runtime. Updated the teaching docs to require redeployment before a live cloud demo.

Final AWS read-back confirmed the runtime, custom/default endpoints, both tables, repository, role, and matching log groups were absent. Archived the ignored deployment record as `aws-deployment-cleaned.json` and saved a sanitized cleanup report. MCP verification initially exposed a missing advertised `ClientError` binding and blocked `getattr`; used the returned exception response fields directly and reran all checks successfully. Historical usage charges may still post after deletion.

## Separate course branches

At the instructor's request, created local `v1` at the original `main` commit (`5f328ff`) so its files match the previous course exactly. Renamed `course-v2-runbookops` to `v2` and removed the legacy modules, legacy requirements file, and duplicate V1 README from that branch. Updated the learner/instructor docs and CI branch filter. `main` remains unchanged; no GitHub push or history rewrite was performed. V1 files remain available by switching branches, and V2 keeps its normal development history.

Verified V1 and original main have identical Git trees. V2 has no tracked legacy modules, requirements file, or duplicate V1 README. The offline approval/recovery demo passed after separation, and all local links plus both 180-minute schedules passed validation.

## Publish course branches

The instructor explicitly authorized pushing the repository. Publish local `v1` and `v2` to the existing TrainWithShubham repository without force, changing `main`, opening a PR, or deploying AWS resources. The worktree was clean and neither version branch existed remotely before this push.

## Local run and operator guide

The instructor asked to start the project and document the steps. Port 8000 was occupied by an unrelated Docker service, so use localhost port 8002 and leave that service alone. Start the live OpenRouter adapter with the previously authorized external key file and semantic retrieval; do not recreate AWS resources or copy the key into the repository. Add a configurable base URL to the HTTP demo so it can exercise a nondefault port. Provide RUNBOOK.md for setup, offline and live operation, API tokens/approval, evidence, and shutdown.

Verified `/health` and `/docs` returned HTTP 200 on port 8002 with mode `openrouter`. The real HTTP demo passed anonymous denial, viewer approval denial, and authorized recovery to HTTP 200. Lint, Markdown links, and schedule validation passed. Leave the local server running for the instructor; no AWS resources were recreated.

## Keep the local server available

The first interactive tool-hosted server was gone when the instructor opened it later. Restarted the existing OpenRouter configuration as a detached background process, with its PID and output under ignored `.state/server.pid` and `.state/server.log`. Verified health after separate tool calls and opened the actual Swagger page in Chrome. The app is an API/CLI project; the Swagger explorer is not a chat frontend. Foreground startup instructions remain valid when the instructor keeps that terminal open.

## Visual learning harness and TWS theme

The first UI direction was an operations dashboard. The instructor asked for a smaller harness console inspired by temporal-community/temporal-agent-harness, then supplied the TWS logo and requested less text, more graphics, and light/dark themes. Inspected the reference repository at commit 2a3dc3f; adopted the idea of conversation, component inspection, and observable events without copying its console or introducing Temporal into the LangGraph core.

Use two main boxes and a small Events strip. Sessions are a drawer. The visual component map opens the actual prompt, model settings, MCP schemas, retrieved documents, approval, and saved state. Keep verbose explanations and JSON behind disclosures. Use the supplied TWS PNG unchanged and derive purple/gold theme tokens from the brand; local fonts include their OFL licenses.

Serve static HTML/CSS/JavaScript from FastAPI so learners still use one Python command and need no Node setup. Add authenticated harness configuration and live MCP discovery, authorized knowledge inspection, and NDJSON investigation streaming. Export only public model text/tool requests and sanitized results; never hidden reasoning metadata. Centralize the existing execution/RAG constants so inspector settings reflect runtime values.

Persona issuance is an opt-in, loopback-only development helper with host/origin/header checks. It is disabled for cloud and external issuer configurations. Tokens stay in memory; changing identities clears UI content before access is rechecked. Added tests for these boundaries, document filtering, streaming and disconnect cancellation, actual harness/MCP schemas, and approval integrity.

Browser testing exposed excessive scrolling in the first design; replaced the dashboard with the component map. An initial faint-text colour failed contrast, so updated both theme palettes and measured the final foreground/background pairs above 4.5:1. Browser extension navigation was unreliable; verified the local UI through native Safari controls. A new live OpenRouter streamed run used five model calls, rejected viewer approval, and recovered to HTTP 200 after authorized approval. AWS resources were not recreated.

Final UI verification: 37 tests passed with one optional AWS test skipped, packaged wheel includes static assets/fonts/logo, and the actual-key/private-PEM candidate scan passed. Keep exact mobile-device testing listed as unverified. Both theme text palettes passed measured contrast checks; browser evidence and the fresh live harness trace are separate from offline regression results.

## Shared-screen teaching pass

- Enlarged the existing console rather than adding a second dashboard: 16px reading text, larger graph labels, tool rows, counters, controls, and event text. Kept the TWS purple/gold palette and added static, restrained glows to meaningful states. No blinking or decorative motion.
- Added a latest-operation card sourced from recorded events. Model highlighting now follows an outstanding model-request event instead of glowing for the entire investigation. The component map remains a teaching map; Events is the execution order.
- Added ten selectable teaching demos with per-demo observation cues. Agent tasks populate the composer and require Run; retrieval examples populate the RAG probe and require Search. Selection never approves changes. Inspector examples expose actual configuration and MCP discovery.
- Kept OAuth, AgentCore hosting, and automated evaluations as explicit accompanying exercises. Local development JWT personas are not described as an OAuth flow; configured routes are not described as executed calls; offline fixtures are not model prompt-following evidence.
- Safari retained some old control colours after toggling themes during visual QA. Disabled colour transitions during the toggle and force style resolution so the palette changes together; verify both directions before delivery.
- Verification: seven UI/API tests, Ruff, JavaScript syntax checks, and 33-file Markdown link checks passed. Safari confirmed the ten-card picker, task selection remaining Idle with zero events, retrieval Fresh → Cache hit, and consistent light/dark palettes after the fix. Desktop screenshots were inspected; phone-sized layouts and live adversarial prompt outcomes were not re-tested. Offline Prettier lookup missed the cache; formatting completed using pinned Prettier 3.6.2 without adding a project dependency.

## Free-provider timeout recovery — November 12

- The failed incident `gada-a184972d4483` received no first model response and stopped after approximately 60 seconds. The old error collapsed network failures and read timeouts into one message. A direct recheck returned HTTP 200 for the model catalog and key endpoint, but inference on `nvidia/nemotron-3.5-lightning:free` again timed out at 60 seconds. This supports an inference-path availability problem; it does not establish the provider's internal cause.
- Probed two explicitly named, catalog-listed free tool-capable alternatives. Liquid and Cohere returned the requested investigation tool calls in roughly two seconds. Cohere completed the full Engine capstone in 6.9 seconds with a valid proposal, denied viewer approval, and authorized HTTP 200 recovery. Selected `cohere/north-mini-code:free` explicitly as the current default and restarted only the local live server on port 8002 with that override. Did not edit the other project's env file or create AWS resources. No automatic model, paid, or offline fallback was added.
- Separated timeout, connection, and catalog HTTP errors. Messages name the configured route for timeouts and give a fresh-incident/restart action, without exposing raw exception details. Added an assertion that connection exceptions cannot leak proxy secrets.
- Verified the restarted server through authenticated NDJSON streaming: valid proposal after two model calls in 5.6 seconds, viewer decision HTTP 403, authorized decision and simulator verification HTTP 200. Sanitized evidence is in `instructor/evidence/provider-recovery.json`. Full suite: 38 passed, one optional test skipped. Ruff and links in 33 Markdown files passed. Free capacity remains variable; this is a verified recovery, not a guarantee of future availability.

## Live Bedrock verification — November 12

- The user explicitly requested real Bedrock verification and running the app. Used the existing shared AWS credential configuration in `us-east-1`; no Bedrock bearer key was configured or created. Read-only AWS discovery confirmed the active Nova Lite inference profile. All operational changes remained in the local simulator; no deleted AWS hosting resources were recreated.
- `us.amazon.nova-lite-v1:0` passed the full CLI capstone in 4.43 seconds with two model calls and all five required tools, including the new-Engine persisted approval/resume exercise. Viewer approval was denied; Jethalal approval verified HTTP 200. The permission-claim prompt prepared a valid proposal but did not apply it (5.89 seconds, four calls). The unsafe-command prompt returned without tools, proposal, or change (2.19 seconds, one call).
- Started a separate detached local Bedrock UI on port 8004 with explicitly billed inference enabled. Left the learner OpenRouter default intact. The browser test exercised actual tool calls, RAG retrieval, the server's 403 viewer denial, the review checkbox, authorized approval, and observed HTTP 200.
- Nova sometimes emits `<thinking>` blocks in its text channel, including a truncated/unclosed block. Added a provider-independent filter before public response/event persistence for `thinking`, `think`, and `analysis` tags; preserved native provider-required metadata handling. Three regression cases cover closed, unclosed, and uppercase blocks. Earlier private local traces retain their original content; the verification summary excludes reasoning content.
- Reran the browser flow after the formatting fix: five model calls, five tools, authorized recovery, and no tagged reasoning in the persisted public model events. Tool call order/count varied across successful runs; this is a small scenario verification, not a model reliability benchmark. Haiku was not invoked because Nova Lite passed the requested checks.
- Full regression suite: 41 passed, one optional test skipped; Ruff and local links in 34 Markdown files passed. Evidence: `instructor/evidence/bedrock-local-verification.json`. Run/authentication instructions: `docs/BEDROCK_DEMO.md`. API-key authentication is documented but not live-tested; the actual successful runs used existing AWS credentials.

## Beginner learning flow — November 12

- Kept one small app and the existing safety boundaries. Simplified the language learners see first: Find the problem, Check checkout, Read error logs, Search company notes, and Suggest a fix. The diagram shows Rules, AI, Tools, Company notes, Approval, and Apply fix. RAG and MCP each get a one-sentence explanation beside the real inspector.
- Show four starter examples first. The remaining six topics are available in a collapsed More topics section. Short natural-language questions replace technical multi-clause prompts. Each still submits the actual question to the configured model; no canned live result or fake tool event was introduced.
- Put model replies/metadata, schemas, saved JSON, and the approval hash behind disclosures. Exact before/after values, risk, how to undo, expiry, and the approval checkbox remain reviewable. The server still checks the same permissions, evidence, hashes, expiry, and revision. Added a short beginner-language instruction to the real system prompt.
- Added friendly error explanations and next actions while preserving the original diagnostic text in a Technical details disclosure. Unknown failures do not claim success or that nothing changed. AWS permission errors specifically refer to instructor setup rather than suggesting that selecting Jethalal grants AWS access. Four Node tests cover those distinctions.
- Live Nova Lite check: the first short question found the payment connection problem using health, logs, and deployment tools without preparing a fix. The separate short fix request called all five tools, retrieved notes, and prepared a pending proposal in 3.34 seconds with two model calls; checkout remained HTTP 503 and no change was applied. Documented that asking only what is wrong need not call every tool or prepare a fix.
- Safari desktop confirmed the simplified labels, collapsed model metadata, four visible starter cards, and collapsed advanced topics. Python suite: 41 passed, one optional test skipped. Node error tests: four passed. Ruff, JavaScript syntax, and links in 35 Markdown files passed. The current Bedrock server was restarted for the updated system prompt. No new AWS hosting resources were created.

## Complete application coverage and end-to-end checks — November 12

- Restored technical names in the harness: System prompt, Model, MCP tools, RAG, Approval, and Execute. Kept beginner-facing prompts, tool descriptions, and error guidance simple.
- Measured the baseline with Python branch coverage: 42 tests passed, but combined statement/branch coverage was 68%. Added tests for the uncovered CLI commands, provider contracts, error paths, auth/JWKS races, RAG formats/cache failures, exact approval integrity, SQL rollback, DynamoDB conditional-write retries/size limits, and checkpoint recovery. Added actual HTTP MCP subprocess/JWT testing alongside the existing stdio protocol tests.
- Added Node/JSDOM tests for the actual ES modules with a controlled HTTP boundary, plus coverage of theme startup and friendly errors. Exported named console entrypoints and an awaitable startup result so asynchronous operations can be observed without a test-only runtime mode. Browser tokens remain in memory and all authorization stays on the server. No application source files or lines were excluded from either coverage scope.
- Fixed two issues found by the tests: offline evaluation now clears DynamoDB/checkpoint-table settings as well as the database URL; keyboard handling tolerates a document event target without calling a missing matches method. The evaluator mutation-style tests verify it actually reports failures when audience, approval, hash, or replay enforcement is deliberately broken in a test double.
- Repeated live Nova runs exposed behaviour the original spot checks missed: one stopped without preparing a requested fix; another attempted preparation without retrieving the required current runbook, which validation correctly blocked. Added one bounded completion reminder after partial evidence, explicit guidance that preparation is not execution, verification that retrieved results contain the current runbook, and safe tool-validation next steps. The instructor Bedrock configuration uses the already-supported eight-call budget to allow a bounded repair attempt; the learner default stays six. Tool-step and 150-second limits remain active.
- A destructive request is judged by enforced safety, not by requiring a specific refusal sentence: it may be refused or produce a valid pending alternative suggestion, but cannot run arbitrary commands or apply an unapproved fix. Recorded the earlier live failures rather than claiming all sampled attempts succeeded. Final four-scenario live suite passed: approval/restart/replay, rejection, permission claim, and unsafe request. Live tests require explicit paid opt-in and are outside normal discovery; their output files are reset before each case and record failure if a case does not complete.
- Final deterministic gates: 144 Python tests, 1,432 statements and 382 branches at 100%; 32 JavaScript tests, all four application modules at 100% lines/statements/functions/branches. There are no skips with AWS test extras installed. The offline evaluator passed all 13 outcomes. Ruff, 36-file Markdown checks, wheel asset inclusion, and npm audit (zero findings) passed. npm test dependencies are development-only; the web app still starts with one Python command and needs no Node runtime.
- Dependency choice: current c8 introduced moderate transitive audit findings; pinned the compatible c8 9.1 series with zero audit findings and verified it against Node 26. The lockfile records the complete test dependency graph. JSDOM is for logic tests, not evidence of rendering correctness.
- Final native Safari desktop check: the simple fix prompt paused for approval after the completion reminder obtained the missing runbook. Viewer approval returned 403; Jethalal reviewed and applied the exact saved fix; checkout returned HTTP 200. Also observed five discovered MCP tools and a real semantic RAG cache hit, with light/dark palettes checked. Kept the app running locally on port 8004. No new AWS hosting resources were created.
- Scope limits remain explicit: PostgreSQL was checked through adapter/checkpointer contracts, DynamoDB through Moto, model HTTP contracts through mocks/Stubber plus separate real Bedrock scenarios. Other browsers, phone layouts, production AWS deployment, and every possible model response are not covered by a 100% application-code metric. See docs/TESTING.md and instructor/evidence/test-coverage.json. CI now enforces both 100% gates and uploads reports; remote CI status will be reported only after it runs.

## Separate application repository — November 12, 2026

RunbookOps moves from course v2 to TrainWithShubham/runbookops, with a new main branch and independent application history. Its initial source comes from course commit 9e251fb2517d7d5158c9da93f7e23948c3498329. Module 6 links to the app. The course retains its lessons, exercises, solutions, instructor delivery plans, and historical sanitized evidence. Course main and v1 are unchanged.

Application source, dependencies, tests, CI, examples, knowledge fixtures, devcontainer, and deployment tooling move together. Course links point to app documentation; setup clones the app and states which checkout each command needs. The health exercise remains a standard-library course task. Course CI validates links, both 180-minute schedules, and the exercise solution; app CI retains the coverage gates and offline evaluations.

No private environment, state, credentials, or caches enter the new Git history. No cloud resources are created. The original implementation commits remain available in course history.

The prompt-editing lab copies its course prompt into the app's ignored .state/system_prompt.txt; the health exercise checker runs from the course checkout. This avoids adding course exercise files to the application or relying on a particular sibling-folder name. Standalone regression checks passed: 144 Python tests and 32 JavaScript tests, both at 100% application coverage, plus 13/13 offline outcomes and package builds. Course link/schedule checks and the exercise solution passed.

## November 13 — concepts before the integrated application

The owner asked to redesign v2 so the first five modules teach concepts independently, with the final application introduced only in module 6 on Day 2. They chose both everyday DevOps use and agent engineering, centered the examples on CI failure analysis and deployment-document RAG, requested a demo/practical-heavy mix, retained the 75-minute guided capstone and kept AgentCore in the Day 2 demonstration.

Replaced the application-dependent day/lesson pages with six module pages and a new timed curriculum. Modules 1–5 use a new small course package, their own uv lockfile and synthetic fixtures; no final-application imports, character names, data or checkout are required. Root navigation and instructor history may still identify the final project. A documentation gate checks this separation as well as both 180-minute schedules and the 75-minute capstone. Main and v1 refs are preserved.

The CI example diagnoses a dev dependency group excluded before pytest starts. It exposes three bounded read-only tools and never edits a real pipeline. A plain Python loop comes before the LangGraph representation. The real stdio MCP example demonstrates discovery/calling separately from model selection; it is not mislabeled as an integrated model-to-MCP agent. Reference Inspector discovery was checked in addition to the course client. Ten stable MCP evaluation questions are supplied for follow-up; ordinary course CI does not claim to run a live-model evaluation over them.

The RAG example reads an independent deployment process, rollback PDF, incident DOCX, architecture PPTX and text policy. The preparation path extracts/chunks/indexes; semantic mode embeds corpus chunks at indexing time and the query at retrieval time. The tiny local JSON index makes vectors visible without a managed vector database. Keyword retrieval remains a no-download alternative and is labeled as such. Offline output shows extracted evidence, not a fabricated LLM answer. Real document extraction, metadata filtering, source locations and semantic retrieval were checked.

Identity examples use explicit development principals, actual Python policy/hash/expiry/replay checks and an OAuth/OIDC architecture explanation. They do not claim to implement a production identity provider. Approval changes only in-memory proposal status. The cache/routing/trace examples also state their small scope. The evaluation dataset checks supplied fixed candidates; that result is not a live-model reliability score.

Live OpenRouter checks exposed an empty reasoning-only response at the original token limit and a verbose answer that was cut off. The adapter now checks for empty and truncated answers, disables optional reasoning when the model advertises support, retains free-only catalog validation and disables provider fallback. Compact response instructions were added. A separate RAG answer invented retry guidance and lost precise source references; its visible excerpt is retained as a classroom source-review case. Subsequent sampled prompt, two-call tool investigation and RAG checks passed. Failures remain part of the verification record; rerunning until a pass is not represented as a success-rate benchmark. No key or private model reasoning was saved in course evidence.

Fourteen course regression checks pass on Python 3.11, 3.12 and 3.13. A clean environment without the final application also passes. This is separate from the application coverage suite. Timed teaching rehearsal, Windows/attendee machines, class-wide provider capacity and a fresh AgentCore demonstration remain instructor preparation. No AWS resources were recreated during this redesign. Earlier instructor verification remains marked as history.

The outer workspace curriculum/README were updated to point at the canonical v2 material, with the previous untracked workspace curriculum backed up under ignored artifacts. This avoids opening a stale project-centered syllabus from the workspace landing directory.

## November 13 — e-book sample chapter

Created a standalone sample, RAG Pipelines for DevOps, rather than expanding the whole book before the author reviews its teaching style. The 23-page PDF uses TWS purple/gold, an unchanged TWS logo, licensed embedded fonts, five vector diagrams, a linked contents page, narrow code listings, exercises and answer notes. The editable manuscript and portable ReportLab renderer are retained. Technical claims have a primary-source ledger dated November 13; pinned versions were tested rather than described as universally latest.

The companion ZIP contains a small independent lab and the synthetic mixed-format deployment documents. It has no capstone dependency. Keyword retrieval runs without downloading an embedding model; optional semantic mode was exercised with FastEmbed and 384-value vectors. Six regression checks passed both in the authoring checkout and after extracting the archive into a fresh environment. A privately configured live OpenRouter sample returned source IDs with provider-reported cost zero and no fallback. Credentials and private configuration are excluded. One successful model call does not establish answer reliability or future free capacity.

Layout review found an overflowing contents-page callout and a stranded troubleshooting heading; both were fixed. The final PDF has 23 pages and 39 link annotations; all pages were rendered and visually reviewed, code listings parse, and body text stays within the page boundaries. An apparent small-header issue during image inspection was checked against the PDF content and raster pixels; header pixels are identical across the sampled pages, so no font change was needed. Documentation checks and Ruff pass. VERIFICATION.json records the final artifact hashes and tested scope.

This is a sample, not the completed e-book. It does not implement OCR, production identity, a general model-quality benchmark, tagged-PDF accessibility or cloud deployment. Temporal and AgentCore remain proposed bonus chapters. No AWS resource was created and no changes were pushed.

## November 13 — shorter, standalone visual edition

The author's feedback replaces the long instructional sample with an independent visual chapter. Rebuilt the reader PDF from 23 pages to 10 and 870 extracted words, including headings and running furniture. Removed setup commands, code listings, exercises and all companion/repository dependencies from the reader content. Removed the edition's separate exercise package and archive; the course examples are unchanged. The earlier edition remains in Git history.

Used the PDF, frontend design, UI/UX and humanizer guidance. The design search supplied general minimal-layout/icon guidance; web conversion/CTA recommendations were irrelevant to a book and were not applied. Chose a single consistent Lucide vector set with pinned upstream revision and retained license, embedded in the PDF. Two renamed upstream icons initially returned 404; resolved their canonical names and recorded the filename mappings. A first render attempted before all assets arrived failed; only the successful complete render is published.

The chapter follows one fictional deployment-policy question through preparation, extraction, chunking, retrieval, trust boundaries and answer review, then distinguishes fixed RAG from an agent loop. Technical sources were rechecked; four compact further-reading links preserve fact-checkability without interrupting the diagrams. No provider/model/version claims are needed in the reader edition.

Reviewed all ten rendered pages. The final PDF, after embedding the icon license, renders pixel-identically to that reviewed revision. Text boundary checks, four external link annotations, attachment presence, absence of exercise/implementation references, Ruff and course documentation/isolation checks pass. VERIFICATION.json records the edition-specific results and final hash, replacing the older implementation-test record. This is a conceptual book sample; no model call, AWS resource or production-system test was required.

## November 13 — complete visual e-book

The owner approved the shorter standalone sample and authorized the full book with the same visual direction. Created Agentic AI for DevOps: A Visual Field Guide, first edition dated November 13, 2026: 86 pages, 19 chapters, 28 glossary terms and 48 primary references. The first 16 chapters follow modules 1–5 independently; chapter 17 is the module-6 application case study. Temporal and AgentCore are separate bonus chapters. The book is an independent conceptual read, with no setup commands, exercise files or runnable-project dependency.

Kept the approved TWS purple/gold, original logo, licensed fonts and pinned Lucide symbols. Authored different vector explanations for tool sequences, loops, graph routes, MCP participants, RAG preparation/query paths, chunk boundaries, identity, approvals, guardrails, harness machinery, caches, trace spans, evaluation layers, release flow, durable work and cloud responsibilities. Each four-page chapter includes a concept opener, diagram, worked synthetic scenario and failure review. The Markdown manuscript includes diagram reading order. Source copy/data and geometry are editable separately; the reading transcripts regenerate from them. Exported the complete PDF and a ZIP of 19 independent chapter PDFs, preserving printed page numbers.

Reviewed current primary documentation, including MCP 2026-07-28, LangGraph persistence/interrupts, Temporal history/replay/Activities/messages and the AgentCore managed Harness versus Runtime distinction. Clarified that Runtime hosts the custom LangGraph loop and managed Harness provides a Strands-powered loop. Replaced obsolete Qdrant and Temporal documentation paths and followed OpenTelemetry's moved GenAI conventions to the current repository. No market ranking, stable free-model availability, unverified pricing, live deployment readiness or broad model-reliability claim is made.

Publication review caught and fixed a compact-node text-fit assertion, a trace-heading collision, redundant sequence labels hidden behind a note, ambiguous script/workflow/agent labels, an approval continuation that could imply rejection executes, and a cloud diagram that needed an explicit shared-responsibility connection. Changed the graph write route to say proposal. Adjusted the illustrative trace bars so child operations progress in sequence and the request spans the whole task. An initial verifier assumed named destinations, whereas ReportLab writes outline/direct destinations; the check now inspects the actual outline and contents-link targets.

All 86 pages were rendered and visually reviewed; revised pages were inspected again and unchanged pages compared at pixel level. Automated publication checks pass: zero page-safe-area text overflow, zero significant authoring text-box overlap candidates, all 19 chapter bookmark destinations, 125 PDF link annotations, four embedded asset notices, all 76 standalone pages matching book text/content streams, and concept/application isolation. First and last chapter raster exports also match the reviewed book pages. Ruff, course local-link/schedule/isolation checks and staged secret scanning pass. VERIFICATION.json records the artifact hashes and limits. No application code, AWS resources, model inference or remote push was needed.

The result is a complete first visual edition for author review, not an independently certified production reference or tagged-PDF accessibility certification. Cases are fictional and architecture diagrams are conceptual. Source-grounded technical review and publication QA do not establish that a deployment or agent implementation was executed. Main, v1 and the earlier approved sample are preserved.

## November 13 — beginner learning edition for 2027

The owner asked to treat the reader as new to AI, explain learning mistakes/models/useful prompts, add Claude Code practices and link the Hindi-channel one-shot video. Expanded the visual book to 107 pages and 23 chapters while keeping short standalone chapters. New foundations cover learning traps, model/training/inference/API distinctions, local/hosted access, model/task selection, four original DevOps prompt patterns and Claude Code work habits. Added a first-month learning path, a 2027 skills compass and 14 glossary entries. The six-module structure remains; the application case is now chapter 21, and Temporal/AgentCore are chapters 22/23. Concept material still has no application dependency.

The 2027 framing is a recommended learning direction based on documentation reviewed November 13, 2026, not a forecast of future product capabilities, prices or job requirements. Learning mistakes are editorial guidance, not a survey ranking. Prompt templates are examples for adaptation, not empirically best prompts. Claude Code guidance distinguishes model instructions in CLAUDE.md from tool permissions and other enforcement, recommends bounded changes and actual diff/check review, and explains skills/hooks without requiring broad permission bypass.

Located the requested video at https://www.youtube.com/watch?v=14K2noGTJ1M. Direct web retrieval was throttled; YouTube oEmbed successfully confirmed the exact title, TrainWithShubham author and channel URL. Kept public identity metadata in VIDEO.json. The owner identifies the Hindi language; no unseen transcript, timestamp or complete-video review is claimed. Added a clickable PDF link and original vector QR, explicitly labeled as the 2026 video. Decoded the rendered final QR with zxing-cpp 3.1.1 and matched its destination to the verified URL; recorded the PDF hash with this evidence.

Current documentation revealed that some Claude plans now include API credits with eligibility conditions. Avoided repeating the blanket claim that subscriptions never include API credits. The beginner chapter instead asks readers to check Console/API setup, eligibility, available credits, quotas and data policy independently of a coding login. No volatile dollar amounts or model-version recommendations are printed. Added current official Claude Code/model/access references and an OpenRouter catalog reference; there are 60 linked sources in this edition.

Rebuilt three contents pages, chapter bookmarks, 23 standalone exports, glossary/reference sections and the editable reading transcripts. Removed stale generated chapter filenames during renumbering. Rendered and visually reviewed all 107 pages; final five changed pages were inspected again and all other rasters matched their reviewed versions. The QR decodes correctly. Publication gates pass for zero safe-area text overflow, zero significant authoring text-box overlap candidates, 23 contents/bookmark targets, 160 link annotations, all 92 standalone page text/content streams and embedded asset licenses. Ruff, local-link/schedule/isolation checks and staged secret scanning pass. No inference, AWS resources or push was required; main, v1 and the approved sample remain unchanged.

## November 13 — shorter illustrated rewrite

The owner asked for simpler human language, fewer words, stronger everyday illustrations and TWS branding throughout. Applied the humanizer, PDF and design guidance to the book. Rewrote all 23 chapters as three-page standalone explanations: a picture and short definition, a technical diagram, and a small DevOps example with mistakes and checks. Reduced the book from 107 to 84 pages and from roughly 10,988 to 8,567 extracted words including navigation and references. Added 23 original vector scenes beside the 23 technical diagrams. Kept the original logo unchanged and matched the cover background to its black background; purple/gold and a small TWS footer carry through the pages. The approved earlier sample is unchanged.

Used everyday comparisons such as a librarian finding a page for RAG, an office badge for identity, a delivery label for exact approval, a bicycle for harness machinery and a labeled food container for caching. Each comparison has an explicit limit. The examples are fictional teaching devices. Retained the source ledger and dated technical review rather than claiming a new verification of all 60 external references during this editorial pass. The 2027 framing remains a learning direction. No dedicated skill named “ultra max editorial” was available; used the available humanizer, design and PDF review workflows.

Review caught several issues and corrected them: paper details escaping small illustration bounds, an analogy illustration that did not match its caption, a tool-result arrow implying every success becomes an error, and arrows suggesting that search options/model choices were mandatory sequences. Options now use normal reading order without arrows. The application example labels its execution branch as approved only. Shortened text still explains enforced permissions, conditional API credits, source freshness and access, approval integrity, retries/idempotency, protected traces, and the Runtime/managed Harness distinction. Removed residual course-dependent wording from the reader pages.

Rendered and visually reviewed all 84 pages. Inspected changed pages again and compared all other rasters with reviewed versions; the last revision changed only pages 41, 56 and 68. Publication checks pass with zero safe-area text overflow, zero significant recorded text-box overlaps, 23 contents/bookmark destinations, 155 link annotations, four embedded asset notices and all 69 standalone page text/content streams matching the full book. Decoded the rendered video QR and tied the evidence to the final PDF hash. Ruff and local-link/schedule/module-isolation checks pass. Final publication evidence is in ebook/visual-edition/VERIFICATION.json. These checks do not establish model reliability, deployment readiness, complete security or tagged-PDF accessibility. No AWS resources, inference calls or remote push were needed.


## November 13 — rocket-only footer

The owner requested the existing TWS rocket monogram instead of footer lettering. Found the original transparent purple/gold asset in Downloads/Images/2026-11/TWS Monogram 3 (1).png and copied it unchanged into the shared book assets as tws-monogram.png. Replaced the footer's TWS letters and Train With Shubham text with this image; page numbers remain. Rebuilt the full book and all 23 standalone exports. Rendered all 84 pages and confirmed every pixel above the footer matches the previously reviewed book. Inspected the cover, light pages, video page, final page and enlarged footer. Refreshed the rendered QR evidence against the new PDF hash. Publication and local-link/schedule/isolation checks pass. This is a branding-only change; no content, infrastructure or model behavior was changed.

## November 13 — final AI engineering and DevOps review

The owner requested a current factual review, including official resources and Reddit. Reviewed the 84-page rocket-footer edition without changing its PDF, chapter exports or manuscript. Saved the findings in ebook/visual-edition/FINAL_REVIEW.md, tied to the PDF hash, and the public-link HTTP results in REFERENCE_AUDIT.json. All 60 existing reference URLs return HTTP 200 after redirects; inspected suspicious page titles against article content rather than treating HTTP status as proof. Current official documentation supports the core LangGraph, MCP, RAG, Claude Code, subscription-credit, caching, Temporal and AgentCore distinctions examined.

Recommended four pre-publication clarifications: RAG no-evidence/error branches and derived-data access/deletion; LangGraph restarting an interrupted node; a timeout not proving a remote operation stopped; and AgentCore allowedTools not governing the separate direct-command API. Suggested local MCP server trust and a small evaluation scorecard as useful additions, with a context/RAG/memory picture optional. These are scoped omissions/clarifications, not a claim that the foundations are broadly wrong. The existing book was not silently patched during a review-only request.

Consulted recent practitioner discussions about root access, RAG parsing/freshness, evidence use and Claude Code context. Treated Reddit as anecdotal and self-reported, with no generalization of accuracy/cost percentages or incident claims. Indexed and rendered Reddit timestamps differed, so exact thread publication dates were not independently certified. Linked a current October 22, 2026 primary monitor-red-teaming study as an optional guardrails reference. No live model call, cloud provisioning, application test or independent benchmark reproduction was done; URL checks and documentation review do not establish operational reliability.

## November 13 — apply final review and add QR resources

The owner approved the technical follow-up and requested a last page linking the TWS YouTube channel and 11 named projects. Applied all seven review recommendations within the existing three-page chapters: context/RAG/memory tiles; local MCP server code/permission awareness; an explicit LangGraph node-restart arrow and note; RAG evidence/no-evidence/error branches plus derived-data removal/access handling; uncertain-write status checks and bounded retries; a five-case evaluation scorecard; and separate model-tool and caller-IAM boundaries for AgentCore. Named the timeout example around a write request. Kept prompts, authorization, evidence and actual execution distinct. The primary-reference count remains 60. The new resources page makes the book 85 pages without extending any chapter.

Verified the requested canonical repositories against their current project pages. ECC is affaan-m/ECC and REA is morluto/rea. Linked the existing verified TrainWithShubham channel. Used short descriptions and direct URLs, with no tracking redirect, star ranking, universal enforcement guarantee, free-service promise or blanket security certification. The Awesome list is a community directory; Graphiti is a graph-building framework; n8n is described as self-hostable without treating every project's license as identical. No third-party skills, MCP servers or packages from this list were installed or executed. Recorded source identities and HTTP checks in RESOURCE_REVIEW.json; all 12 destinations resolve.

The first render exposed the resource cards overlapping the heading's introduction. Moved the grid below the introduction and used six rows of two cards with 64-point vector QR codes. Review also caught a shared AgentCore caption that could imply allowedTools applies to custom Runtime code; changed the shared caption to code/configuration tool selection and made the allowedTools exception explicitly about managed Harness. Reviewed all 12 revised original-book pages and the new resource page. Re-rendered final fixes, reviewed them again, and pixel-matched all other pages to their reviewed versions. The last wording pass changed only page 37.

Publication checks pass: 85 rendered pages, zero safe-area text overflow, zero significant recorded text-box overlaps, 23 chapter destinations, 167 link annotations, four embedded asset notices and all 69 standalone page text/content streams matching the book. Decoded all 12 final-page QR codes at a 1000-pixel page render and the existing video QR; every destination matches its clickable link and evidence is tied to the final PDF hash. Ruff, local links/schedules/module isolation and staged secret scanning pass. VERIFICATION.json records the final hashes. Updated the earlier review with implementation status while preserving its original 84-page snapshot. No AWS resources, inference, remote push or application changes were involved.

## November 13 — DevOps learning directions chapter

The owner asked to turn the discussion of AIOps, MLOps, LLMOps and DevOps's next steps into a chapter matching the existing visual style. Added chapter 24, DevOps in the agentic AI era, on pages 75–77. Kept the three-page pattern: an original crossroads illustration and short explanation, a four-card scope comparison with a shared platform-engineering strip, then a CI-helper learning path with mistakes and checks. Existing chapters retain their numbers and page positions. Appended rather than renumbered the Temporal/AgentCore bonuses. Updated contents, guide, sources, manuscripts and the 24-chapter archive. The resource page stays last.

Checked the IBM AIOps, Google Cloud MLOps, Microsoft LLMOps and CNCF platform-engineering sources. Added their four links to the technical reference ledger, bringing it to 64. The extra source page plus the three chapter pages brings the book from 85 to 89 pages. Described Agent operations as a descriptive label and noted overlapping terminology. Clarified that GenAIOps can include non-language models, AIOps need not use an LLM/agent, and the learning paths are choices rather than a hiring guarantee. The CNCF article is practitioner guidance, not a job-market forecast. Recommendations do not require every DevOps engineer to become a model trainer.

Rendered all 89 pages. Reviewed the new chapter, contents, guide, changed source pages and final resource page. Compared existing content at pixel level after accounting for shifted footer numbers: only contents, guide and the old final source page changed above the footer, with credits moving to the added source page. Reviewed the last changes on pages 75–76 again; all other final rasters match their reviewed versions. Publication checks pass with zero safe-area text overflow, zero significant recorded text-box overlaps, 24 chapter destinations, 176 PDF link annotations and all 72 standalone page text/content streams matching the full book. All 13 QR codes decode correctly, with the 12-resource page now at 89. Ruff and local-link/schedule/module-isolation checks pass. Recorded current hashes and source checks. No application, AWS, inference or remote push was required.

## November 13 — cover poster

Created a portrait promotional cover image with the built-in image generator, using the existing TWS rocket monogram as a branding reference. Kept the established dark purple/gold palette and a short title/subtitle/author hierarchy. The illustration connects documents, a terminal, tools and an approval shield around an agent hub. Inspected the generated image for readable title, author, branding and the current 24-chapter/89-page metadata. Saved the PNG and exact generation prompt under output/imagegen. This is generated promotional artwork; the e-book PDF and its original logo assets were not replaced.
