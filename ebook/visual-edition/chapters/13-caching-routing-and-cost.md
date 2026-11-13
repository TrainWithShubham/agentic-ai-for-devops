# Caching, routing and cost


05 / Operate the system


## Where can you save time safely?

Measure where the request spends time before adding complexity. Retrieval, model generation and external tools have different costs. Reusing work is useful only when its identity, permissions and freshness still match.



**Prompt cache.** Provider feature that can reuse processing of eligible input prefixes.


**Result cache.** Application reuse of a retrieved result or generated answer.


**Model route.** Choose a model using task requirements and measured outcomes.


## A hit requires the right context

A result-cache key should reflect the actual authorization and resource context plus relevant source, prompt and model versions. Define invalidation for changes that matter.


### Diagram reading order


1. **Request context:** Caller permissions, resource and normalized question.

2. **Cache decision:** Version, freshness and access checks still match?

3. **Hit:** Return only an eligible, still-authorized result.

4. **Miss:** Retrieve or generate, then store under the correct scope.



Provider prompt caching is not a semantic answer cache. Requirements, pricing and retention depend on the provider and model.


## Two tasks, two candidate routes

Illustrative choices to evaluate; neither route is an endorsement of a particular model.



1. **Extract fields:** A small model may suffice for structured log classification.

2. **Investigate:** A harder multi-step comparison may justify a more capable model.

3. **Compare:** Measure task outcomes, tool errors, latency and actual usage.

4. **Constrain:** Keep the same permissions and approval rules on every route.



Do not silently switch to a paid model or another provider. Fallbacks must preserve budget, data-handling and tool requirements.


## Failure and correction

An answer cached only by question is returned to another caller after the document permissions change.



Scope cache access to trusted context, invalidate affected entries and revalidate permissions before serving.


## Engineering review


- Separate cache types.

- Record cache hit and scope.

- Measure cost per useful outcome.

- Treat fallback as a policy choice.


## Further reading


- [Claude: prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

- [OWASP: RAG security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html)

- [LangChain: model capabilities](https://docs.langchain.com/oss/python/langchain/models)
