# Prompts and context


01 / Foundations


## In everyday words

A prompt is your request. Context is the information available with it: instructions, messages, files and tool results.


## Picture it

Packing for a journey: take the ticket and map you need. Extra luggage can get in the way.

Only supplied or retrieved information is available; the model cannot see your private systems automatically.



**Prompt.** What you ask the model to do.


**Context.** Information it can use now.


**Token.** A unit used to represent input or output.


## Build a useful request

Give the task and the evidence. Say what a useful result should contain.


### Diagram reading order


1. **Instructions:** Explain the error; propose only.

2. **Question:** Why did this test job fail?

3. **Evidence:** Install log, workflow and dependency file.

4. **Output:** Facts, cause, proposal, checks, unknowns.

- **Context:** For this request.

- **RAG:** Retrieved sources.

- **Memory:** Saved for later.



RAG and saved conversation context do not by themselves retrain the model. Scope memory to the right user. Keep important evidence visible and validate structured responses.


## A useful CI request

Ask for a result you can inspect.



1. **Task:** Diagnose this failed test job.

2. **Evidence:** Cite the supplied log lines.

3. **Uncertainty:** Separate facts from likely causes.

4. **Boundary:** Propose a change; do not apply it.



A readable JSON response still needs application checks.


## Failure and correction

"Act like an expert and fix everything."



Name the task, evidence, allowed actions and output.


## Engineering review


- Clear task.

- Relevant evidence.

- Visible unknowns.

- A checkable result.


## Further reading


- [Claude: prompt engineering](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)

- [Anthropic: context engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)
