# Chunks, embeddings and search


03 / Company knowledge


## Which passage should the model receive?

Search quality depends on what was extracted and how it was split. Embeddings represent content numerically for similarity search; a related vector is not proof of a correct operational answer.



**Extract.** Inspect the text before choosing a search database.


**Chunk.** Keep a condition and its required action together.


**Rank.** Compare search strategies on reviewed questions.


## Preserve meaning across boundaries

A rollback instruction can become misleading if its condition and action land in separate excerpts. Overlap may preserve context, at the cost of repetition.


### Diagram reading order


1. **Source:** If validation fails, stop promotion and escalate to the service owner.

2. **Bad split:** A fragment says only: "If validation fails..."

3. **Useful chunk:** Includes the condition, required action and location.

4. **Metadata:** Source ID, version, location, permissions and current status.



Scanned PDFs need OCR. Slide diagrams and complex tables may require additional parsing and human inspection.


## A search strategy comparison

The examples are qualitative; they are not retrieval benchmark results.



1. **Keyword:** Exact names and error codes can be strong lexical signals.

2. **Semantic:** Compatible document/query embeddings help find related meanings.

3. **Hybrid:** Combine lexical and semantic candidates when useful.

4. **Rerank:** Optionally score candidates again before context assembly.



Use a labeled question set to compare evidence quality, latency and context size. There is no universal chunk size or top-k value.


## Failure and correction

A semantically related incident report displaces the current approval policy, and the answer borrows an outdated procedure.



Check eligibility, source freshness and ranked passages before changing the generation prompt. Add the failure to the question set.


## Engineering review


- Inspect extracted text.

- Keep access metadata attached.

- Measure search separately.

- Review incomplete excerpts.


## Further reading


- [pypdf: text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)

- [Qdrant: hybrid search](https://qdrant.tech/documentation/search-tuning/hybrid-search/)

- [Qdrant: FastEmbed reranking](https://qdrant.tech/documentation/fastembed/fastembed-rerankers/)

- [Microsoft: RAG evaluation](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)
