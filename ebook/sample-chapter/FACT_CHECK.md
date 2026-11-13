# Technical review ledger

Reviewed 13 November 2026. This edition explains concepts independently of any implementation. All operational policies, questions and answer snippets are fictional illustrations.

| Topic | Primary source | Editorial limit |
|---|---|---|
| External evidence, indexing and query-time retrieval; fixed versus agentic retrieval | [LangChain retrieval](https://docs.langchain.com/oss/python/deepagents/retrieval) | RAG supplies context; it does not guarantee correct answers. The diagrams are conceptual, not executable architectures. |
| Source extraction and OCR limitations | [pypdf extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) | Not every format or layout is equally extractable. Additional processing may be needed for images, tables and diagrams. |
| Source trust, access control and cache/trace disclosure | [OWASP RAG security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html) | The illustrated controls do not constitute a complete security design. Authorization must be enforced by trusted application infrastructure. |
| Retrieval quality versus groundedness, relevance and completeness | [Microsoft RAG evaluators](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators) | The sample does not report an evaluation score or model-quality benchmark. |

Chunk boundaries and overlap are shown qualitatively. No universal chunk size, model, database, threshold or provider is recommended. Similarity is a ranking signal. Source locations aid review; they do not establish that a claim follows from the source. Write actions require their own authorization and verification design.

Lucide icons are pinned to the revision in `assets/icons/SOURCE.json`. Their original license is retained, including upstream attribution, and embedded in the PDF. [Lucide licensing](https://lucide.dev/license). Fonts retain their supplied license notices. TWS artwork is copied unchanged.

The publication check covers page rendering, visible text boundaries, links, PDF attachments and absence of implementation/setup references. It does not certify tagged-PDF accessibility or a production system. No AWS resources or live inference are used to build this edition.
