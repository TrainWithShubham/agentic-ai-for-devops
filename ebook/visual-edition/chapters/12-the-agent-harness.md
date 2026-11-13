# The agent harness


05 / Operate the system


## What makes an agent runnable?

A harness is the execution machinery around the model: context, tool dispatch, state, limits and recovery. Frameworks can supply parts of it; the application still needs a coherent operational design.



**Control.** Track state, routes, deadlines and stop reasons.


**Execution.** Validate requests and handle tool results and errors.


**Operations.** Persist progress, observe outcomes and enforce budgets.


## Put the model inside a controlled system

The model is one component. Connect the surrounding machinery deliberately so a restart, timeout or repeated tool request has a defined outcome.


### Diagram reading order


1. **Context + state:** Messages, evidence, proposal and ownership.

2. **Tool dispatcher:** Validation, permissions, execution and results.

3. **Budgets + recovery:** Call limits, deadlines and retry policy.

4. **Traces + outcomes:** Observed steps, human decisions and verified state.



Session state, durable task progress and long-term knowledge are different storage needs. Do not assume process memory satisfies all three.


## The provider times out

A model request times out while an investigation is active. The system needs to distinguish a lost response from a completed side effect.



1. **Classify:** Was this a read, model call or write action?

2. **Inspect:** Check the saved execution record before issuing a duplicate write.

3. **Retry safely:** Use bounded backoff for suitable transient failures.

4. **Report:** Return a partial result or explicit failure if recovery is exhausted.



Choose one owner for retries across layers. Multiplying SDK, application and workflow retries can amplify cost and load.


## Failure and correction

A timeout triggers an automatic retry of a write whose outcome is unknown, applying the change twice.



Design an idempotency key and durable execution record. Reconcile actual target state when the result is ambiguous.


## Engineering review


- Bound total work.

- Persist important transitions.

- Classify failures before retry.

- Expose final and partial status.


## Further reading


- [Anthropic: long-running harnesses](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)

- [Google SRE: handling overload](https://sre.google/sre-book/handling-overload/)

- [AWS: safe retries and idempotency](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
