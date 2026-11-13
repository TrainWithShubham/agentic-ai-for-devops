# See what the agent did


05 / Operate the system


## In everyday words

Observability means understanding what happened from the evidence a system records. A trace follows one request through its steps.


## Picture it

A journey record shows each stop and delay. An agent trace shows searches, model calls, tools and review.

A trace records operations. It does not by itself prove the final claim is correct.



**Trace.** The connected path of one request.


**Span.** One timed operation on that path.


**Outcome.** The result actually reached.


## Trace one investigation

Follow the evidence from the request to the result.


### Diagram reading order


1. **Request:** Task ID and caller/resource context.

2. **Retrieve:** Source IDs and index revision.

3. **Model + tool:** Model, usage, inputs, status and duration.

4. **Review + verify:** Proposal, decision and target-state check.



Record observable steps, versions and stop reasons. Protect trace data. Private model reasoning is not needed to prove which tool ran.


## The answer says "fixed"

The trace contains only read-only calls.



1. **Inspect:** There is no execution record.

2. **Compare:** The answer claims more than the evidence.

3. **Classify:** Recovery is not established.

4. **Improve:** Add a check for unsupported completion claims.



Record observable steps and decisions. Private model reasoning is not needed to prove which tool ran.


## Failure and correction

Saving credentials and private documents in a broadly readable trace.



Minimize content, redact secrets and restrict access.


## Engineering review


- Connected events.

- Versions and stop reasons.

- Delay and errors.

- Protected trace data.


## Further reading


- [OpenTelemetry: traces](https://opentelemetry.io/docs/concepts/signals/traces/)

- [OpenTelemetry: GenAI conventions](https://github.com/open-telemetry/semantic-conventions-genai)

- [Google SRE: monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
