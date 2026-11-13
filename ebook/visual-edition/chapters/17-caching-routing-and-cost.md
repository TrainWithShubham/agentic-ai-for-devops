# Caching, routing and cost


05 / Operate the system


## In everyday words

Caching reuses eligible earlier work. Model routing chooses which model handles a task. Both need checks on cost, quality and access.


## Picture it

A labeled food container saves cooking time. Check who it belongs to and whether it is still fresh.

A fresh-looking label alone is not enough; cache access and invalidation need application rules.



**Prompt cache.** Provider reuse of eligible input processing.


**Result cache.** Application reuse of a previous result.


**Route.** Choose a model for a task.


## A hit requires the right context

Reuse a result only when permissions, resource, versions and freshness still match.


### Diagram reading order


1. **Request context:** Caller permissions, resource and question.

2. **Cache decision:** Are access and versions still valid?

3. **Hit:** Return an eligible result.

4. **Miss:** Do the work and store it with the right scope.



Prompt caching is not an answer cache. Provider rules vary. Fallbacks must preserve budget and data rules; do not silently switch to paid inference.


## Choose a route, then measure

These are candidates to test, not model endorsements.



1. **Simple task:** Try field extraction with a suitable small model.

2. **Harder task:** Compare a more capable model for a difficult investigation.

3. **Measure:** Check outcomes, tool errors, delay and usage.

4. **Constrain:** Keep the same access and approval rules.



Fallbacks must respect budget and data rules. Do not silently switch to a paid model.


## Failure and correction

Returning a cached answer after the reader loses document access.



Scope cache entries and recheck permission before serving.


## Engineering review


- Which cache?

- Whose result?

- Still current?

- What did it cost?


## Further reading


- [Claude: prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

- [OWASP: RAG security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html)

- [LangChain: model capabilities](https://docs.langchain.com/oss/python/langchain/models)
