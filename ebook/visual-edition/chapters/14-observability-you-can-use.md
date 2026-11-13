# Observability you can use


05 / Operate the system


## Which step explains the outcome?

A useful trace connects the user request with retrieval, model calls, tool results and approval events. It lets an engineer distinguish a bad source from a bad decision or a failed executor.



**Trace.** A connected view of operations for one request or task.


**Span.** A timed operation such as retrieval or a model call.


**Outcome.** The result the system actually reached, including failure.


## Trace one investigation

Record enough identifiers and versions to reconstruct a run. Redact sensitive content and restrict who can inspect it.


### Diagram reading order


1. **Request:** Caller/resource context and task ID.

2. **Retrieve:** Index revision and returned source IDs.

3. **Model + tool:** Model ID, usage, tool arguments/status and duration.

4. **Review + verify:** Proposal identity, decision and observed target state.



Use stable trace/span correlation across services. Check the maturity and version of any GenAI semantic conventions you adopt.


## The agent says "fixed"

The visible answer claims recovery, but the fictional trace contains only read-only tool calls.



1. **Inspect:** No executor span or execution record exists.

2. **Compare:** The response wording exceeds what the observations support.

3. **Classify:** This is an unsupported completion claim, not a verified recovery.

4. **Improve:** Add an outcome check and an evaluation case for the claim.



Record decisions and observable evidence. Raw private model reasoning is not required to explain which tool ran or whether the target changed.


## Failure and correction

The trace stores complete prompts, customer documents and tokens in a widely accessible log group.



Minimize captured content, redact secrets and apply retention and access policies. Source IDs can also be sensitive.


## Engineering review


- Correlate model and tool events.

- Capture versions and stop reasons.

- Track latency and errors.

- Protect trace data.


## Further reading


- [OpenTelemetry: traces](https://opentelemetry.io/docs/concepts/signals/traces/)

- [OpenTelemetry: GenAI conventions](https://github.com/open-telemetry/semantic-conventions-genai)

- [Google SRE: monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
