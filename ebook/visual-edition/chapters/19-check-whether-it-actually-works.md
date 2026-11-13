# Check whether it actually works


05 / Operate the system


## In everyday words

An evaluation is a repeatable task with a way to judge its result. Check behavior and outcomes, not just polished wording.


## Picture it

A teacher compares an answer with evidence and a marking guide. A neat page can still contain the wrong answer.

Human and model judges can make mistakes too. Review the grading rules.



**Case.** An input and expected behavior.


**Grader.** A check or reviewed scoring rule.


**Outcome.** Success, partial result, refusal or failure.


## Use more than one kind of check

Use different checks for different questions.


### Diagram reading order


1. **Unit checks:** Schemas, access rules and proposal integrity.

2. **Path checks:** Evidence used, tools called and limits.

3. **Answer review:** Supported, relevant and complete claims.

4. **Outcome checks:** Approved target state; no duplicate effect.



Grade outcomes and constraints, not one exact tool sequence. Repeat variable cases and record configuration. Code coverage is not a model-quality score.


## Five cases worth checking

Expected results and forbidden actions make failures easier to spot.



| Case | Expected | Forbidden |

|---|---|---|

| CI error | Propose the missing dependency. | Disable tests. |

| Missing policy | Say evidence is missing. | Invent an approver. |

| No access | Deny the protected request. | Reveal private data. |

| Injected log | Treat the instruction as log data. | Upload a secret. |

| Repeated write | Check status; avoid another effect. | Apply the change twice. |

Score retrieval, answer support and action safety separately. Compare delay and cost with a script or manual baseline. Repeat variable cases and record configuration.



Keep failed runs. Repeat variable cases and record model/configuration.


## Failure and correction

Passing because the answer contains a citation and the word "approved".



Check source support and the actual approval record.


## Engineering review


- Define success.

- Keep negative cases.

- Check retrieval separately.

- Record failures.


## Further reading


- [Anthropic: agent evaluations](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)

- [Microsoft: RAG evaluation](https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators)

- [LangGraph: testing](https://docs.langchain.com/oss/python/langgraph/test)
