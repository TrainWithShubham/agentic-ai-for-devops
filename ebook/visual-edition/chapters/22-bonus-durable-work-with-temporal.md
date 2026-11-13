# Bonus: durable work with Temporal


Bonus / Temporal


## What should survive a worker crash?

Temporal provides durable execution for processes that must continue across failures and long waits. It complements agent decisions with recorded progress; it does not make a model answer correct.



**Workflow.** Deterministic orchestration of the process.


**Activity.** External or nondeterministic work, such as an API or model call.


**History.** Recorded events used to reconstruct workflow progress.


## Durability around the investigation

Keep model and external tool calls in Activities. Workflow logic coordinates results, timers and messages. Worker processes execute the code; the Temporal service records progress.


### Diagram reading order


1. **Investigate Activity:** Call the model and read permitted evidence.

2. **Durable wait:** Persist the process while a human reviews.

3. **Apply Activity:** Execute the approved action with idempotency.

4. **Verify Activity:** Read target state and record the outcome.



Replay uses recorded Activity results for completed work. An Activity can still run more than once after ambiguous failures; external writes need idempotency.


## Approval arrives after a restart

A fictional release review waits for two hours while the worker is restarted.



1. **Persist:** Record the proposed action identity before waiting.

2. **Recover:** Replay restores orchestration from recorded history.

3. **Receive:** A validated application sends the reviewer decision through a suitable message handler.

4. **Recheck:** Check expiry, permissions and current target state before applying.



A Signal or Update is a message mechanism, not proof of reviewer identity. The application must validate who is allowed to send the decision.


## Failure and correction

The Workflow calls the model directly during replay, or retrying an Activity applies the same release action twice.



Move external work into Activities, set bounded timeouts/retries and make writes idempotent. Test replay compatibility before changing running workflow code.


## Engineering review


- Separate orchestration and I/O.

- Set explicit retry and time policy.

- Authenticate review messages.

- Plan for duplicate Activity attempts.


## Further reading


- [Temporal: workflow execution](https://docs.temporal.io/workflow-execution)

- [Temporal: workflow determinism](https://docs.temporal.io/workflow-definition)

- [Temporal: Activities](https://docs.temporal.io/activities)

- [Temporal: retry policies](https://docs.temporal.io/encyclopedia/retry-policies)

- [Temporal: workflow messages](https://docs.temporal.io/encyclopedia/workflow-message-passing)

- [Temporal: Activity execution](https://docs.temporal.io/activity-execution)
