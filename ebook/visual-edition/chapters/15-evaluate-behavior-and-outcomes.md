# Evaluate behavior and outcomes


05 / Operate the system


## What would count as a good result?

An evaluation is a repeatable task with a way to assess the outcome. Agent behavior needs more than checking for a friendly answer: inspect sources, tool actions, denied cases and final state.



**Dataset.** Representative questions, caller context and expected evidence.


**Grader.** A deterministic check, reviewed rubric or calibrated model judge.


**Outcome.** Success, partial completion, refusal or failure against the task.


## Use more than one kind of check

Different questions need different graders. Code coverage and model quality measure different things. A branch-complete test suite can still miss a bad operational recommendation.


### Diagram reading order


1. **Unit checks:** Schemas, permission rules and proposal integrity.

2. **Trajectory checks:** Required evidence, forbidden tools and budget use.

3. **Answer review:** Supported claims, relevance and missing steps.

4. **Outcome checks:** Actual approved target state and no duplicate effects.



Run stochastic cases multiple times where practical and record model/configuration. One successful run is not a reliability estimate.


## A useful CI evaluation case

Fictional expected behavior: identify the missing test dependency without disabling the test step.



1. **Input:** Workflow, dependency declaration, failed log and engineer identity.

2. **Expected:** Proposal adds the declared test dependency group.

3. **Forbidden:** No workflow write, secret read or test bypass.

4. **Assessment:** Check evidence and proposal; review whether the explanation follows.



Add denied-permission, stale-source, malformed-tool and provider-failure cases. Keep failed runs rather than replacing them with fixed answers.


## Failure and correction

A release gate passes because the response contains "approved" and a citation-shaped string.



Validate the approval record and source support separately. Calibrate subjective graders against reviewed examples.


## Engineering review


- Define success before running.

- Retain negative cases.

- Separate retrieval and answer quality.

- Record failures and version changes.


## Further reading


- [Anthropic: agent evaluations](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)

- [Microsoft: RAG evaluation](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)

- [LangGraph: testing](https://docs.langchain.com/oss/python/langgraph/test)
