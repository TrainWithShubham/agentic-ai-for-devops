# RAG pipelines


03 / Company knowledge


## How do private documents reach an answer?

Retrieval-augmented generation (RAG) supplies external evidence when a model answers. For a deployment question, useful evidence may be a current policy, a rollback checklist or an incident report.



**Prepare.** Extract useful content and preserve its provenance.


**Retrieve.** Find permitted passages relevant to the question.


**Generate.** Ask for an answer supported by those passages.


## Separate preparation from answering

Document changes drive ingestion. Questions drive retrieval. An index needs a refresh strategy; a model prompt cannot repair an ingestion failure.


### Diagram reading order


1. **Sources:** PDF, DOCX, PPTX, Markdown and text.

2. **Prepare index:** Extract, chunk, attach metadata and optionally embed.

3. **Search:** Filter and rank evidence for the current question.

4. **Answer:** Supply selected text and source locations to the model.



RAG does not require a model-directed agent loop. A fixed retrieve-then-answer workflow is a useful design in its own right.


## Who approves rollback?

A fictional release policy says production rollback needs incident-commander approval.



1. **Question:** Who must approve a production rollback?

2. **Evidence:** Current policy, section 4, contains the approval rule.

3. **Answer:** The incident commander must approve. Cite that section.

4. **Boundary:** Explaining the approval rule does not grant approval.



Keep policy knowledge distinct from live deployment state. A document alone cannot establish which release is running.


## Failure and correction

The ingestion job fails after the policy changes, but the assistant continues presenting the old rule as current.



Expose the last successful index refresh and source revision. Decide when stale evidence requires a warning or refusal.


## Engineering review


- Preserve source locations.

- Track document lifecycle.

- Review the selected evidence.

- Disclose missing or stale information.


## Further reading


- [LangChain: retrieval](https://docs.langchain.com/oss/python/deepagents/retrieval)

- [OWASP: RAG security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html)
