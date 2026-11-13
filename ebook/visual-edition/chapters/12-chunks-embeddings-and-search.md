# Chunks, embeddings and search


03 / Company knowledge


## In everyday words

Chunks are small pieces of source text. Embeddings turn content into numbers so search can compare related meanings.


## Picture it

Use tabs to find a useful passage. Keep the whole instruction on the tabbed section.

Similarity is a search signal, not proof that a passage is true or sufficient.



**Extract.** Read usable text from a file.


**Chunk.** Split text without losing its meaning.


**Rank.** Order candidate passages by usefulness.


## Preserve meaning across boundaries

Keep a condition and its required action together.


### Diagram reading order


1. **Source:** If validation fails, stop promotion and contact the service owner.

2. **Bad split:** Only: "If validation fails..."

3. **Useful chunk:** The condition, action and source location.

4. **Metadata:** Version, location, access and current status.



No chunk size fits every source. Scanned PDFs need OCR. Tables and slide diagrams may need more processing and review.


## Different ways to search

Compare results on questions you can review.



1. **Keyword:** Useful for exact names and error codes.

2. **Semantic:** Uses compatible document and query embeddings.

3. **Hybrid:** Combines word-based and semantic candidates.

4. **Rerank:** Optionally scores the candidates again.



No single chunk size or number of results is right for every source.


## Failure and correction

A related old incident replaces the current policy in the answer.



Inspect source eligibility and the ranked text first.


## Engineering review


- Read extracted text.

- Keep access metadata.

- Test retrieval.

- Check source support.


## Further reading


- [pypdf: text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)

- [Qdrant: hybrid search](https://qdrant.tech/documentation/search-tuning/hybrid-search/)

- [Qdrant: FastEmbed reranking](https://qdrant.tech/documentation/fastembed/fastembed-rerankers/)

- [Microsoft: RAG evaluation](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)
