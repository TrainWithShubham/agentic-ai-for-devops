# RAG pipelines


03 / Company knowledge


## In everyday words

RAG finds useful source material before the model answers. It can bring current company knowledge into a response.


## Picture it

A librarian finds the right page. You read that page to answer the question.

Finding a page does not guarantee the answer uses it correctly.



**Retrieve.** Find relevant source passages.


**Context.** Give those passages to the model.


**Generate.** Write an answer from that evidence.


## Separate preparation from answering

Prepare knowledge when documents change. Search it when someone asks a question.


### Diagram reading order


1. **Sources:** PDF, DOCX, PPTX, Markdown and text.

2. **Prepare index:** Extract, chunk and attach metadata.

3. **Search:** Find allowed, current passages.

4. **Answer:** Use their text and cite the location.



A runbook describes policy; live tools show current state. Some search designs need no embeddings. Fixed RAG does not require an agent loop.


## Who approves rollback?

The fictional current policy names the incident commander.



1. **Ask:** Who approves production rollback?

2. **Find:** Read the current approval policy.

3. **Answer:** Name the approver and cite the section.

4. **Limit:** Explaining the rule does not grant approval.



A runbook describes policy. Live tools tell you what is running now.


## Failure and correction

Answering with a retired policy after a failed document refresh.



Track source versions and show when knowledge is stale.


## Engineering review


- Source location.

- Current version.

- Allowed access.

- Missing evidence.


## Further reading


- [LangChain: retrieval](https://docs.langchain.com/oss/python/deepagents/retrieval)

- [OWASP: RAG security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html)
