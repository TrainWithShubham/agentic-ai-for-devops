# Bonus: durable work with Temporal


Bonus / Temporal


## In everyday words

Temporal helps a process keep going across worker failures and long waits. It saves progress so the process can recover.


## Picture it

A saved order ticket survives a shift change. A new worker can continue from the recorded progress.

Durability preserves process progress. It does not make model answers correct.



**Workflow.** Deterministic process coordination.


**Activity.** External work, such as an API call.


**History.** Recorded events used during recovery.


## Durability around the investigation

Keep model and external tool calls in Activities. Workflow code coordinates them.


### Diagram reading order


1. **Investigate Activity:** Call the model and read evidence.

2. **Durable wait:** Wait for the reviewer decision.

3. **Apply Activity:** Apply the approved action safely.

4. **Verify Activity:** Read target state and save the result.



Replay reuses recorded results of completed Activities. Activity attempts can repeat; writes need idempotency. Signals and Updates do not prove reviewer authorization.


## Approval after a restart

The process waits for two hours while a worker restarts.



1. **Save:** Record the proposal identity.

2. **Recover:** Restore progress from recorded history.

3. **Receive:** Accept a validated reviewer message.

4. **Recheck:** Check expiry, permissions and current state.



Signals and Updates carry messages. They do not prove the reviewer is authorized.


## Failure and correction

Calling the model directly in replayed Workflow code.



Use Activities for external work and test replay compatibility.


## Engineering review


- Separate coordination and I/O.

- Bound retries and time.

- Authenticate decisions.

- Avoid duplicate effects.


## Further reading


- [Temporal: workflow execution](https://docs.temporal.io/workflow-execution)

- [Temporal: workflow determinism](https://docs.temporal.io/workflow-definition)

- [Temporal: Activities](https://docs.temporal.io/activities)

- [Temporal: retry policies](https://docs.temporal.io/encyclopedia/retry-policies)

- [Temporal: workflow messages](https://docs.temporal.io/encyclopedia/workflow-message-passing)

- [Temporal: Activity execution](https://docs.temporal.io/activity-execution)
