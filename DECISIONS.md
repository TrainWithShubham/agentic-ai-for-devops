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
