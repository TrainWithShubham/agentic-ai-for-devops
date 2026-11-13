# Case study: RunbookOps


06 / Integrated application


## How do the parts work together?

RunbookOps is the course application case study. Gada Electronics has a fictional checkout failure: Bagha investigates, Jethalal reviews a proposed correction and the application checks the simulator afterward.



**Investigate.** Read operational evidence and current runbook knowledge.


**Prepare.** Produce a specific proposal with supporting observations.


**Review.** An authorized human decides before a simulator write.


## Trace one incident through the system

This conceptual map explains responsibilities. It is not a claim that a fresh cloud deployment or model run was verified while producing the book.


### Diagram reading order


1. **Browser + API:** Show the request, evidence and review decision.

2. **LangGraph agent:** Manage investigation state and tool choices.

3. **Knowledge + tools:** Retrieve sources and inspect permitted simulator state.

4. **Approval + executor:** Bind review to the exact fix and verify the result.



The case is fictional and independent of any real company infrastructure. Observing a demo is different from implementing or deploying it.


## The approval is part of the story

Bagha may diagnose and propose. Jethalal must inspect the exact correction; a role claim in chat is insufficient.



1. **Observe:** Read the simulated checkout failure and current runbook.

2. **Prepare:** Save the bounded correction and the relevant evidence.

3. **Review:** Deny an unauthorized reviewer; validate the authorized decision.

4. **Verify:** Apply only the approved simulator action, then inspect health.



A local deterministic demonstration must be labeled as such. A live model run, cloud hosting and real remediation are separate claims.


## Failure and correction

A simulator recovery is described as an autonomous production incident fix, without explaining the approval or environment.



State which observations and actions actually ran. Keep the boundary between simulated operations, read-only integrations and production writes explicit.


## Engineering review


- Show the source and tool result.

- Inspect a denied case.

- Review the exact proposal.

- Verify rather than narrate recovery.


## Further reading


- [RunbookOps: application source](https://github.com/TrainWithShubham/runbookops)

- [LangGraph: overview](https://docs.langchain.com/oss/python/langgraph/overview)

- [OWASP: authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
