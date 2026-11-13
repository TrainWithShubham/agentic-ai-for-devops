# Agentic AI for DevOps

Two live sessions on November 14 and 15, 2026. Each session is 180 minutes, including a ten-minute break and fifteen minutes for questions. The class has 50–100 learners with mixed experience: basic Python/Linux and some DevOps knowledge are enough.

The course has two professional outcomes: use agents to improve everyday DevOps work, and understand how to build and operate agent applications. Modules 1–5 teach the concepts through independent examples. Module 6 is the integrated project, introduced on Day 2.

## 1. What learners should be able to do

By the end, learners should be able to:

- Decide whether a task needs a script, a fixed workflow or an agent.
- Write system instructions that specify evidence, tools, output shape and limits.
- Follow a model's tool request through validation, execution and the returned result.
- Explain a RAG pipeline, including document preparation and query-time retrieval.
- Inspect source locations, missing evidence, document freshness and access filters.
- Distinguish tool calling, MCP, a framework, an agent harness and managed hosting.
- Explain RBAC, OAuth/OIDC, token scopes, tool credentials and human approval.
- Test an agent's behavior using traces, a small evaluation dataset and explicit failure cases.
- Recognize latency, token cost, caching, retries and deployment trade-offs.
- Demonstrate the final project and state which work they completed themselves.

These are workshop outcomes, not a claim that six hours confer production platform expertise. Existing Linux, CI/CD, IAM, networking and incident-response skills remain relevant.

## 2. Teaching approach and examples

Use a short explanation, an instructor demo and a small learner change for each main concept. Most of the technical session should be spent running, inspecting or modifying examples. Learners may use Claude Code or Codex to make bounded edits, then explain the diff and run the supplied check.

The two recurring examples are:

| Example | What it teaches |
|---|---|
| CI failure analysis | System prompts, structured output, tool calling, bounded loops, MCP, state and proposal review |
| Deployment-document RAG | Ingestion, extraction, chunks, embeddings, index/search, context assembly, citations, freshness and permissions |

The CI job excluded development dependencies before trying to run pytest. Learners inspect the evidence before proposing an installation change. The examples never run a shell command or modify a real workflow.

The document lab uses a deployment process, policy, rollback checklist, architecture slide and historical incident. The corpus also contains a retired procedure and a restricted operations note. All documents and CI runs are synthetic.

Use plain Python to make the loop visible, then show LangGraph's explicit state and conditional edges. The MCP demo runs an actual local server/client exchange. Explain the boundary between the direct Python-tool loop and the separate MCP transport example; the small course loop does not secretly call an MCP server.

## 3. Six modules

| Module | Main question | Practical output |
|---|---|---|
| [1. AI foundations and system prompts](module-1/README.md) | What can an LLM decide, and what must software check? | Evidence-based CI explanation with a reviewable response structure |
| [2. Agents, tool calling and MCP](module-2/README.md) | How does a model request become a controlled tool action? | Bounded CI agent, LangGraph trace and actual MCP tool discovery |
| [3. RAG pipelines for deployment knowledge](module-3/README.md) | How do company documents become useful context? | Local index, inspected chunks, retrieved excerpts and source locations |
| [4. Identity, guardrails and approval](module-4/README.md) | Who may read, propose and approve? | Denied permission/tamper/replay cases and one authorized review |
| [5. Agent harnesses and operations](module-5/README.md) | How do we debug, evaluate and control an agent? | Cache/routing observations, sanitized trace and outcome checks |
| [6. Integrated project and AgentCore demo](module-6/README.md) | How do these parts work together? | Guided project change, approval/recovery evidence and cloud architecture explanation |

### Core, demonstrated and follow-up depth

| Area | Live-session treatment | Follow-up |
|---|---|---|
| AI, tokens/context, system prompts | Explain and compare outputs | Prompt versioning and larger context experiments |
| Tool calling and agent loops | Run and edit a bounded example | More tools, robust error recovery |
| LangGraph | Inspect state, nodes, conditional edges | Durable checkpointers and graph testing |
| MCP | Actual stdio discovery/call; explain remote HTTP | Remote authorization and server hardening |
| RAG | Extract five formats, chunk, index, query and inspect evidence | OCR, reranking, hybrid search, vector database operations |
| Identity and guardrails | Real Python role/argument/hash checks; OAuth/OIDC diagram | Production IdP, consent, token revocation and delegated tool identity |
| Cache/routing/observability/evals | Small executable demonstrations and a dataset | Distributed caches, OpenTelemetry backend, production eval gates |
| AWS hosting | Prepared instructor AgentCore demonstration in module 6 | Independent deployment and teardown |

Every original topic remains covered. We limit the amount learners must implement from scratch so the practical sections fit the clock.

## 4. Day 1 — understand, build, retrieve

| Time | Minutes | Activity | Learners should see or do |
|---|---:|---|---|
| 00:00 to 00:10 | 10 | Module 1: AI, generative AI and LLMs | Separate a fluent answer from verified operational evidence |
| 00:10 to 00:25 | 15 | Module 1: context, tokens, workflow vs agent, system prompts | Draw the model/application/tool boundary and compare two CI prompts |
| 00:25 to 00:45 | 20 | Module 1: prompt demo and learner edit | Ask for facts, cause, proposal, validation and source IDs; review a live or labeled offline answer |
| 00:45 to 01:05 | 20 | Module 2: a bounded agent loop | Follow tool requests, JSON arguments and actual read-only tool results |
| 01:05 to 01:20 | 15 | Module 2: MCP discovery and calls | Inspect discovered schemas and a real stdio request/result |
| 01:20 to 01:35 | 15 | Module 2: LangGraph and a small edit | Identify state, conditional edges and stop limits; reject an unknown run ID |
| 01:35 to 01:45 | 10 | Break | Stop the clock for teaching |
| 01:45 to 02:00 | 15 | Module 3: what RAG pipelines are | Trace separate preparation and query paths; open the mixed-format corpus |
| 02:00 to 02:20 | 20 | Module 3: extraction, chunks and search | Inspect page/slide/paragraph locations; compare keyword and real semantic retrieval |
| 02:20 to 02:35 | 15 | Module 3: learner experiment | Change chunk settings or a deployment document and inspect the new evidence |
| 02:35 to 02:45 | 10 | Module 3: grounded answers and failure cases | Inspect citations, retired documents and a question with missing evidence |
| 02:45 to 03:00 | 15 | Q&A and checkpoint | Explain the agent loop and both RAG paths using the executed examples |

Day 1 exit artifact: one CI recommendation and one retrieved deployment answer/evidence set, each with sources and an honest description of whether a live model was used.

## 5. Day 2 — control, operate, integrate

| Time | Minutes | Activity | Learners should see or do |
|---|---:|---|---|
| 00:00 to 00:10 | 10 | Module 4: identity and OAuth/OIDC | Identify user identity, token audience/scopes, app role and downstream credentials |
| 00:10 to 00:25 | 15 | Module 4: review boundary demo | Deny an engineer's approval, a changed proposal and a replay; approve with the trusted demo role |
| 00:25 to 00:40 | 15 | Module 4: guardrails and learner attack | Try extra tool arguments, an injected log instruction and a restricted RAG query |
| 00:40 to 00:50 | 10 | Module 5: harness and failure handling | Map state, tool dispatch, budgets, timeouts, retries and human review |
| 00:50 to 01:05 | 15 | Module 5: cache, routing and traces | Observe cache hit/miss boundaries and a task route; open the saved trace |
| 01:05 to 01:20 | 15 | Module 5: evaluation practical | Run outcomes, inspect a deliberately bad candidate and add one useful case |
| 01:20 to 01:30 | 10 | Break | Prepare the separately documented project checkout |
| 01:30 to 01:35 | 5 | Module 6: introduce the project | Explain the scenario, roles and repository boundary |
| 01:35 to 01:50 | 15 | Module 6: local harness walkthrough | Follow an investigation, sources, tools and pending approval |
| 01:50 to 02:05 | 15 | Module 6: guided learner modification | Make one bounded change, review its diff and run a relevant check |
| 02:05 to 02:15 | 10 | Module 6: denial and approved recovery | Demonstrate the viewer boundary and verify the approved simulator correction |
| 02:15 to 02:30 | 15 | Module 6: AgentCore instructor demo | Observe actual cloud invocation/stream, managed hosting and durable state |
| 02:30 to 02:40 | 10 | Module 6: inspect traces and evaluations | Compare claimed success with saved evidence and actual outcomes |
| 02:40 to 02:45 | 5 | Module 6: save learner artifacts | Record what ran, one improvement and limitations |
| 02:45 to 03:00 | 15 | Q&A and interview explanation | Explain design choices and discuss a safe next integration |

Module 6 has 75 minutes. Keep cloud provisioning, package/model downloads and account creation outside the live teaching window.

## 6. What a DevOps engineer should recognize at work

| Existing engineering skill | Agent-system application | Interview or review question |
|---|---|---|
| CI/CD and release review | Prompt/tool changes need behavioral checks before release | What would prevent a prompt change from breaking tool selection? |
| IAM and secrets | Separate model requests from caller permissions and tool credentials | Can a retrieved document grant write access? |
| Incident response | Separate observed evidence, hypotheses and verified recovery | What proves the recommendation actually restored service? |
| Reliability engineering | Bound calls, handle timeouts and make side effects idempotent | What happens if a provider times out after a tool was called? |
| Observability | Trace model calls, tool results, retrieval sources and human decisions | Which event explains the wrong answer? |
| Cost management | Measure usage/latency; scope caches and model routes | Could a cache leak another user's context? |
| Infrastructure operations | Understand hosting, state, logs, runtime identity and teardown | Which data survives process restart? |

These are transferable engineering capabilities. We do not claim that every top company requires a particular framework, or that a small job sample establishes a market-wide ranking. LangGraph is retained for continuity and visible state; the course teaches the loop before its framework representation.

## 7. Learner access and preparation

Start with [setup](setup/README.md). Course commands run in this repository through module 5. Python 3.11–3.13 and uv are sufficient; no Node.js, Docker, Kubernetes cluster or AWS account is required for those modules.

Offline examples use deterministic fixtures and make no generative API calls. A live run requires an explicit flag and each learner's own OpenRouter key/model. The provider adapter verifies a currently listed zero-priced `:free` model and disables fallback. Availability, quotas, privacy terms and service quality remain provider-controlled. A Claude or ChatGPT subscription is separate from application API access.

The optional semantic extra downloads an embedding model once and runs it locally. Have the instructor prepare this before class. Every learner can run keyword retrieval without that download; label the distinction clearly. PDF/DOCX/PPTX extraction is real; OCR and interpreting diagrams are follow-up work.

Modules 1–5 share only small course utilities and synthetic fixtures. Their commands, checks and solutions work without the final project repository.

## 8. Checks and completion

Run the [course checks](checkpoints/README.md). They validate tool boundaries, actual MCP transport, retrieval sources/filters, approval integrity, cache isolation and the example evaluation outcomes. Passing these deterministic checks does not prove live model quality or resistance to every prompt injection.

For each practical, save the input, observed result, source IDs and one explanation of the boundary being tested. Learners should be able to explain a failure as well as a successful run. Use the module-6 checklist for the final integrated demonstration.

## 9. Instructor preparation

- Rehearse with this lockfile in a clean course checkout and confirm free-model access on November 13.
- Prepare the semantic model cache before class; inspect all five source formats and source locations.
- Keep a working solution for each learner edit. A learner can watch the demonstrated run when local setup fails.
- Prepare module 6 separately, including the live AgentCore deployment, role-boundary checks and cleanup. Previously deleted resources are not a ready demonstration.
- Keep historical evidence clearly labeled. Recorded evidence is the recovery option when a live provider/cloud demonstration fails.
- Rehearse the stated clock. Timed rehearsal and attendee laptop checks are instructor tasks, not outcomes established by code tests.

## 10. Further reading

Primary references reviewed for this redesign:

- [Anthropic: building effective agents](https://www.anthropic.com/research/building-effective-agents): agent/workflow selection and simple, inspectable designs.
- [Anthropic: writing tools for agents](https://www.anthropic.com/research/writing-tools-for-agents): tool contracts and evaluation.
- [LangGraph quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart): explicit state and the tool loop.
- [MCP architecture](https://modelcontextprotocol.io/docs/learn/architecture) and [security practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices).
- [FastMCP client transports](https://gofastmcp.com/docs/clients/transports): actual local stdio exchanges.
- [OpenRouter free variants](https://openrouter.ai/docs/guides/routing/model-variants/free): catalog entries and model access.

Frameworks and service capabilities change. Recheck the official references before changing a pinned example or advertising a specific hiring claim.
