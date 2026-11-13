# Prompts and context


01 / Foundations


## What does the model see?

A model answers from its current input and learned patterns. It does not automatically see your private logs or current deployment. Context is the information actually supplied to this request.



**Instructions.** Define the task, evidence requirements and output shape.


**Context.** Supply relevant messages, source excerpts and tool results.


**Limits.** Tokens and context windows vary by model and API.


## Build a useful request

Tokens are units used to represent input and output; they are not a fixed number of words. A context window is finite. Keep the evidence needed for the present decision visible.


### Diagram reading order


1. **System instructions:** Explain CI failures from supplied evidence; propose only.

2. **User question:** Why did run 218 fail?

3. **Tool evidence:** Workflow revision, install log and error location.

4. **Response contract:** Facts, likely cause, proposed change, validation, unknowns.



Provider APIs differ in message roles, limits and structured-output support. Validate the returned data in the application.


## A prompt worth reviewing

For this fictional CI incident, the system asks for a proposal with explicit supporting evidence.



1. **Task:** Diagnose the failed test job using the supplied workflow and logs.

2. **Evidence:** Attach a source location to each observed fact.

3. **Uncertainty:** Separate a likely cause from something the logs establish.

4. **Boundary:** Prepare a change for review; do not claim it was applied.



Version the instructions and output schema together. A readable JSON object still needs semantic checks.


## Failure and correction

"You are a senior SRE. Fix everything." leaves the evidence, permitted tools and completion criteria undefined.



Specify the required observations and stop conditions. Reject malformed fields and unsupported claims outside the model.


## Engineering review


- Name the task and permitted actions.

- Keep critical evidence in context.

- Separate facts from hypotheses.

- Test changes against known questions.


## Further reading


- [Claude: prompt engineering](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)

- [Anthropic: context engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)
