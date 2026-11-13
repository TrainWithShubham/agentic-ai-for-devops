# Technical review ledger

Reviewed: 13 November 2026. This ledger covers the sample chapter and its standalone lab. It is a technical review record, not a claim that all future dependency versions or live model runs will behave identically.

| Claim | Evidence | Scope / limitation |
|---|---|---|
| Retrieval supplies external evidence; fixed and agentic RAG designs exist | [LangChain retrieval documentation](https://docs.langchain.com/oss/python/deepagents/retrieval), reviewed on the date above | The supplied lab is a fixed workflow, not a model-controlled agent loop |
| Index preparation and query-time retrieval are separate functions | `lab/course_labs/rag.py`: `build_index` and `retrieve` | The CLI rebuilds its tiny index per run for teaching |
| Scanned page images need OCR beyond pypdf's text extraction | [pypdf extraction documentation](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) | No OCR is implemented or claimed |
| PDF/DOCX/PPTX/MD/TXT are actually read | Standalone `check_lab.py` format test | Word tables, slide diagrams/notes and arbitrary complex layouts are not covered |
| Seven document IDs and eighteen initial chunks | Actual standalone preparation run with the included files and 450/80 character splitter | Counts change with files, settings or extraction behavior |
| FastEmbed query/passage methods are used at the appropriate stages | [Qdrant FastEmbed example](https://qdrant.tech/documentation/fastembed/fastembed-rerankers/) and actual semantic run | The referenced reranking feature is not implemented in this lab |
| Selected embedding configuration emits 384-value vectors | Measured from the standalone semantic index using FastEmbed 0.9.1 and BAAI/bge-small-en-v1.5 | Not a claim about all embedding models |
| 450/80 yields two PDF chunks; 600/80 yields one in this fixture | Executed exercise-A snippet against the supplied PDF | Character counts, not token counts; not an optimality result |
| Current/role filters are applied before similarity ranking | Source inspection and actual allowed/restricted/retired retrieval checks | CLI role is a teaching fixture, not validated identity; the local index is not a production access boundary |
| Unauthorized/untrusted sources are security concerns | [OWASP RAG Security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html) | The checklist is engineering guidance, not a comprehensive security audit |
| Empty retrieval skips generation even with --live | `check_lab.py` patches the model boundary and asserts zero calls | Nonempty irrelevant results still need relevance/support assessment |
| Corpus fingerprint changes after source/manifest edits | Temporary-copy source-change regression | Fingerprint does not version the full loader/model configuration |
| Source IDs alone do not establish supported/complete answers | [Microsoft RAG evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators) plus the recorded synthetic rehearsal failure | The sample does not call Microsoft's evaluators or measure a general model success rate |
| Free model entries are catalog-specific and can change | [OpenRouter free-variant documentation](https://openrouter.ai/docs/guides/routing/model-variants/free) and catalog validation in the adapter | No promise of perpetual free capacity or provider privacy terms |
| Standalone live generation completed with source IDs | Actual `course_labs.rag --live` from the companion folder, using a privately loaded instructor key | One sample; provider reported cost 0; no paid/offline fallback; no source-support guarantee for every future answer |

The sample retains pinned tested versions rather than installing unbounded latest packages. API documentation was reviewed at publication time; examples were exercised against the lockfile. The core checks make no generative API calls. Actual semantic testing uses local model weights. No AWS resource was created.

## Typography and branding

The source includes the license notices for Manrope, Source Serif 4 and IBM Plex Mono. Static TTF instances are included for portable PDF rendering. Source Serif 4 was obtained from [Google Fonts](https://github.com/google/fonts/tree/main/ofl/sourceserif4). TWS artwork was copied unchanged from the instructor-provided project asset.

## Publication limits

This is a sample chapter with a tested lab, not the complete e-book. Temporal and AgentCore remain proposed bonus chapters. No production integration, cloud deployment, broad load test, OCR, model-quality benchmark or tagged-PDF accessibility certification is claimed. Code listings in the PDF are explanatory excerpts; the companion contains the complete executable source.
