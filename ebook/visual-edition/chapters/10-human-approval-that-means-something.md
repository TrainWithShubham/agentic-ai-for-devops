# Human approval that means something


04 / Control and approval


## What exactly did the reviewer approve?

Human-in-the-loop (HITL) review should authorize a specific proposal. The application must bind that decision to the target, parameters and relevant evidence, then recheck before execution.



**Proposal.** Immutable action details, target and expected preconditions.


**Decision.** Authenticated reviewer accepts or rejects that proposal.


**Execution.** Apply only the approved action under current policy.


## A proposal has a lifecycle

Use explicit states. A pending proposal is not a queued side effect that should execute automatically after any message containing "yes".


### Diagram reading order


1. **Prepared:** Action, target, evidence and expiry are recorded.

2. **Pending review:** Reviewer sees the exact diff and impact.

3. **Decision recorded:** Approval or rejection is tied to this proposal identity.

4. **Applied + verified:** Execution and post-change evidence are stored separately.



A hash helps detect a changed proposal when compared with trusted stored data. It does not authenticate the reviewer.


## A CI patch changes after review

The reviewer approved adding a test dependency group. The pending patch is later edited to disable tests.



1. **Prepare:** Store the exact patch and a server-side proposal digest.

2. **Review:** Show the installation change, validation and expected impact.

3. **Detect change:** The digest or version differs: invalidate approval.

4. **Re-review:** Require a fresh decision on the changed action.



Use expiry and one-time consumption. Recheck target state to reduce the gap between review and execution.


## Failure and correction

One approval can be replayed, or a mutable proposal is silently replaced before the executor reads it.



Persist the reviewed proposal, validate current preconditions and consume approval atomically with the execution claim where possible.


## Engineering review


- Bind decision to exact parameters.

- Reject changed or expired proposals.

- Prevent approval replay.

- Verify the resulting state.


## Further reading


- [OWASP: authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

- [LangGraph: interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)

- [OWASP: transaction authorization](https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html)
