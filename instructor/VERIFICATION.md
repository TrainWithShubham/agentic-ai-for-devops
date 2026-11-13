# Concept-first course verification — November 13, 2026

This record covers the redesigned `v2` course, not the standalone application. The [machine-readable summary](evidence/concept-course-verification.json) records counts and scope. [Earlier verification](VERIFICATION_HISTORY.md) is historical material from the previous course layout.

## Learner experience update

The [learner-review evidence](evidence/learner-experience-review.json) records the latest pass on November 13. All 17 current checks pass on Python 3.12.12 on macOS, including a fresh locked environment. Sixteen documented offline/check commands returned their expected results, including deliberately failing evaluations and incomplete starters. The public model-list command also succeeded without inference. Expected configuration/catalog/optional-dependency failures now provide a next step and retain a nonzero exit code.

Rewrote the root README, setup and all six modules from the learner's perspective using the humanizer guidance. Added expected-output explanations and recovery steps, defined jargon where introduced, and moved cloud commands to the [instructor guide](AGENTCORE_DEMO.md). This was an editorial/code review, not an observed beginner usability study. No new dependency, live generative request, semantic download, AWS deployment or application execution was needed. The finished book is unchanged.

## Earlier redesign checks

The table and sampled live evidence below describe the earlier 14-check baseline, not a new run of every Python version or live endpoint.



| Check | Observed result |
|---|---|
| Course regression checks | 14 checks pass on Python 3.11, 3.12 and 3.13 |
| Independent installation | Clean Python 3.12 environment has no final application package installed; course checks pass |
| MCP | Actual local stdio process discovery/call passes; reference Inspector 2.15.0 lists the three tools |
| LangGraph | Actual model/tools nodes complete the offline CI loop with bounded counters |
| Documents | PDF, DOCX, PPTX, MD and TXT extraction preserves tested page/slide/paragraph locations |
| Keyword retrieval | Current authorized sources returned; retired/restricted sources excluded; unmatched query returns no evidence |
| Semantic retrieval | Real local FastEmbed model downloaded; corpus vectors indexed; query retrieves deployment guidance and the PDF checklist |
| Approval | Engineer approval, wrong hash, changed proposal, expiry and replay denied; authorized in-memory review passes |
| Cache/routing | Exact-match cache respects its demonstrated role/version/model/prompt boundary and TTL; approval routes to human review |
| Evaluation exercise | Five checks pass for the fixed good candidate; all five reject the supplied bad candidate with the expected nonzero exit |
| Exercise solutions | CI summary, source filter, approval predicate and evaluation case checks pass |
| Docs and source | Local links, two continuous 180-minute schedules, 75-minute capstone, module independence, Ruff and workflow lint pass |

The tests run actual course functions, document loaders and local MCP processes. They do not make generative model requests. The semantic-model run and live-provider checks below were separate.

## Sampled live model checks

The preflight used `cohere/north-mini-code:free` through OpenRouter with an existing authorized instructor key. The key was read privately into the process environment and was not copied into this course or saved in evidence.

The final preflight passed a CI prompt response, a two-model-call CI investigation using actual course tool results, and a deployment answer containing retrieved source IDs. The actual RAG CLI with `--live` also completed. [Sanitized sampled evidence](evidence/concept-labs-live.json) includes visible answers and provider-reported metadata, without keys or private model reasoning. These are sampled observations, not a success-rate benchmark.

Earlier attempts exposed real problems:

- The original 700-token budget was consumed by reasoning and returned no visible answer.
- A verbose response reached a later output limit. Optional reasoning is now disabled where supported, answer length is instructed, and empty/truncated responses fail explicitly.
- A RAG response used imprecise references and added a recovery step the source did not authorize. That answer is preserved as a [source-review exercise](../data/rag-answer-for-review.md). Better formatting alone does not establish source support.

No paid/offline model fallback was used. The free catalog and provider access can change before class. Recheck them; do not assume that a successful individual call establishes capacity for 50–100 simultaneous attendees.

## Cloud and classroom readiness

AgentCore remains in the Day 2 module-6 demonstration. The previous AWS deployment was deleted; this redesign did not recreate it or run a fresh cloud invocation. Follow [the instructor preflight](AGENTCORE_DEMO.md) before class. Old successful cloud evidence is historical, not a currently running deployment.

The redesigned course was checked locally on macOS with managed Python environments. Windows laptops, a new browser-lab allocation, the new GitHub workflow on a remote runner, a timed instructor rehearsal and a 50–100-person session were not tested in this pass. The original application retains its own separate verification records.
