# Tools with clear contracts


02 / Agents and tools


## How does a request become an action?

A model can return a tool name and structured arguments. Trusted application code decides whether to execute that request. The returned observation becomes input to a later model step.



**Name.** State the capability clearly: read_ci_log.


**Arguments.** Use a narrow schema with bounded identifiers.


**Result.** Return evidence, status and an intelligible error.


## Follow one tool request

The model is not the operating-system executor. The application validates the request before dispatching it, then records what the tool actually returned.


### Diagram reading order


1. **Model:** Requests read_ci_log(run_id=218).

2. **Application:** Checks tool name, argument schema and caller access.

3. **Tool:** Reads the allowed run and returns a bounded excerpt.

4. **Model:** Uses that observation or asks for another permitted step.



Tool descriptions and schemas help selection. They do not replace authorization or validation.


## A narrow CI tool

A read-only contract is easier to inspect than an unrestricted command runner.



1. **Input:** run_id identifies one known run; no arbitrary path or shell string.

2. **Validation:** Reject unknown IDs, unexpected fields and excessive excerpt sizes.

3. **Output:** Return run ID, source revision, log location and text.

4. **Error:** Return "run not found" rather than inventing a diagnosis.



Design results for both the agent and the engineer debugging it. Include enough provenance to revisit the observation.


## Failure and correction

A generic run_command tool turns a vague model request into broad operating-system authority.



Expose task-specific capabilities. Keep write tools separate and enforce their policy at the executor.


## Engineering review


- Describe when a tool is useful.

- Validate more than JSON syntax.

- Bound the returned evidence.

- Distinguish requested and completed actions.


## Further reading


- [Anthropic: writing tools](https://www.anthropic.com/research/writing-tools-for-agents)

- [Claude: tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
