# Technical and editorial review

Edition date: 13 November 2026. Scope: the visual book and its chapter exports. This is a source-grounded editorial review, not independent certification or verification of a deployed system.

## Review boundaries

The 48 primary references in `sources.py` were consulted for the relevant topics. The PDF links each chapter to its sources and includes a complete reference section. Most illustrations are original teaching designs; their concrete policies, CI run identifiers, errors, role assignments and incident scenarios are synthetic. No vendor diagrams or prose passages were copied.

| Chapters | Claims checked | Primary reference families | Important qualification |
|---|---|---|---|
| 1-2 | Workflow versus agent, model context, token limits, system instructions | Anthropic agent/context guidance and Claude prompt documentation | The distinctions are an engineering vocabulary, not a universal taxonomy. Prompts do not confer authority. |
| 3-4 | Model tool requests, application execution, bounded loops | Anthropic tools, Claude tool-use documentation, Google SRE overload guidance | The CI narratives are invented worked examples, not captured executions. |
| 5 | Host/client/server, capability discovery, tool calls and transports | MCP architecture, authorization and security documents | Architecture/authorization links identify the 2026-07-28 specification. SDKs may support different versions; no complete wire transcript is claimed. |
| 6 | State, nodes, edges, checkpointers, stores and interrupts | LangGraph overview, persistence and interrupts | In-memory storage is not restart-durable. The graph is conceptual; deployment and side-effect policy are application responsibilities. |
| 7-8 | Preparation/query paths, source extraction, chunking, search and grounding | LangChain retrieval, pypdf extraction, Qdrant hybrid search/reranking, Microsoft RAG evaluation | No universal chunk size, vector dimension, top-k or retrieval success rate is asserted. OCR and diagram interpretation need suitable processing. |
| 9 | OIDC authentication, OAuth delegated authorization, resource policy | OpenID Connect Core, RFC 9700, OWASP authorization and MCP security | Token validation depends on token/provider. An ID token is not a general API access credential. Browser flows should follow current code/PKCE guidance. |
| 10-11 | Review binding, stale/replayed proposals and injection defenses | OWASP transaction authorization, authorization, prompt injection and AI-agent security | Hashes do not authenticate people. Rejected decisions stop; changed/expired proposals need review. Layering controls is not complete injection resistance. |
| 12-13 | Harness responsibilities, retries, idempotency, cache types and routing | Anthropic harnesses, AWS Builders' Library, Google SRE, Claude caching, OWASP RAG security, LangChain models | Result-cache design and model routes are proposed engineering choices. Prompt caching behavior is provider-specific. No paid fallback, cost saving or reliability figure is claimed. |
| 14-16 | Traces/spans, evaluation layers, release boundaries and CI credentials | OpenTelemetry, Anthropic evaluations, LangGraph tests, GitHub Actions security, Google SRE | GenAI conventions now have a dedicated upstream repository. No private reasoning capture is required. Coverage does not establish model quality. |
| 17 | Application responsibilities and simulator/production distinction | Local module-6 material and the public RunbookOps repository | Fictional conceptual case study, not new verification of a live app, AWS deployment or operational remediation. |
| 18 | Workflow determinism, Activities, history/replay, messages and retries | Temporal workflow/Activity/retry/message documentation | Activities can be attempted more than once; external effects need idempotency. Signal/Update delivery does not authenticate a business approver. |
| 19 | Runtime versus managed Harness, Gateway, tools and invocation boundaries | AWS AgentCore Runtime, comparison, Harness, tools, Gateway and security documentation | Custom LangGraph belongs on Runtime; managed Harness supplies a Strands loop. No claim that Harness runs a custom LangGraph loop unchanged. Regions, quotas and price must be checked at deployment time. |

## Sources that needed correction

Some older Qdrant search/tutorial URLs redirected without usable content. The book uses the current hybrid-search guide at `https://qdrant.tech/documentation/search-tuning/hybrid-search/`, read successfully. Temporal message-passing documentation was located through the official workflow page and uses the canonical encyclopedia URL. OpenTelemetry's former GenAI conventions page points to a dedicated repository; the book uses that current destination. These corrections avoid treating an obsolete link as technical evidence.

## Illustration review

The source comparison, sequence arrows, proposal transitions, cache decisions, graph routes and shared cloud responsibilities were reviewed for meaning as well as alignment. A preliminary approval diagram could imply that rejection leads to execution; it now labels the continuation "approved only" and states that rejection stops. The LangGraph write route is labeled a proposal rather than implying prior approval.

## Publication scope

All reader pages are rendered and inspected. Automated checks cover text fit, PDF links/bookmarks, page counts, standalone extraction and absence of exercise/setup dependencies. These are publication checks, not operational integration tests. No infrastructure, credentials or model responses were needed. Asset notices are retained with the sources and attached to every exported PDF. Tagged-PDF accessibility is not certified.
