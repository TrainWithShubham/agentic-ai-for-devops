# The agent harness


05 / Operate the system


## In everyday words

A harness is the machinery around the model: state, tools, limits, saved progress and failure handling.


## Picture it

The rider chooses a direction. The bicycle frame, brakes and controls make the ride manageable.

The picture explains supporting machinery. A harness still needs correctly designed permissions and recovery.



**State.** What the task knows so far.


**Limits.** How much work it may do.


**Recovery.** What happens after a failure.


## Put the model inside a controlled system

Treat the model as one part of a system you can inspect.


### Diagram reading order


1. **Context + state:** Messages, evidence and ownership.

2. **Tool dispatcher:** Check requests and save results.

3. **Budgets + recovery:** Deadlines, call limits and retries.

4. **Traces + outcomes:** Steps, decisions and verified state.



Timeout: stop waiting. Retry: try again. Idempotency: avoid duplicate effects for one logical operation. Choose one retry owner.


## The provider stops responding

You cannot tell whether a requested write finished.



1. **Classify:** Was this a model call, read or write?

2. **Inspect:** Check the saved execution record.

3. **Recover:** Retry suitable transient failures within limits.

4. **Report:** Show failure or partial results honestly.



Choose one retry owner. Retries at many layers can multiply work and cost.


## Failure and correction

Retrying an uncertain write and applying it twice.



Use an idempotency key, saved record and target-state checks.


## Engineering review


- Bound the work.

- Save progress.

- Classify failures.

- Show the stop reason.


## Further reading


- [Anthropic: long-running harnesses](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents)

- [Google SRE: handling overload](https://sre.google/sre-book/handling-overload/)

- [AWS: safe retries and idempotency](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
