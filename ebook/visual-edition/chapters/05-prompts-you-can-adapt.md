# Prompts you can adapt


01 / Foundations


## What makes a prompt useful?

A useful DevOps prompt names the task, supplies relevant evidence, sets boundaries and asks for a checkable result. There is no single best prompt for every model or incident. Start with these patterns and assess the output.



**Task.** Say what decision or explanation you need.


**Evidence.** Name the files, excerpts or observations available.


**Result.** Ask for sources, uncertainty and a validation plan.


## Give the request a clear shape

Use ordinary language and concrete constraints. Replace vague instructions such as "make it production ready" with the changes and checks that would establish success.


### Diagram reading order


1. **Goal:** Explain why the test job failed; prepare a proposal.

2. **Evidence:** Use only this log, workflow and dependency file.

3. **Boundary:** Do not execute commands or change the workflow.

4. **Acceptance:** Return facts, cause, exact proposal, validation and unknowns.



Ask for a short explanation tied to source locations. Inspect the evidence and observed actions when checking the result.


## Four DevOps prompt patterns

Supply the named evidence before using a pattern. Replace the task details to fit your environment; these are examples, not tested guarantees.



1. **CI failure:** Using this log and workflow, explain the failed step. Cite lines. Separate facts from hypotheses. Propose the smallest fix and a validation check. Do not edit files.

2. **Document answer:** Using these deployment excerpts, answer who approves rollback. Cite the supporting section. If the evidence is missing or conflicts, say so. Do not grant approval.

3. **Terraform review:** Review this Terraform diff. Explain changed resources, possible replacement, access changes and uncertainty. Suggest validation. Do not apply it or assume a cost estimate.

4. **Incident summary:** Summarize these sanitized events as observed facts, hypotheses and next read-only checks. Include time and source references. Do not claim recovery without a confirming observation.



When an answer is weak, inspect the evidence and the requested result before adding a longer persona. Keep the prompt version with the reviewed example.


## Failure and correction

The request says "act as a 10x engineer and fix the deployment" but supplies no target, logs or definition of success.



Name the resource and evidence, ask for a proposal and state what would validate it. Prompt instructions still do not replace execution permissions.


## Engineering review


- Supply the evidence the model can use.

- Ask for sources and missing information.

- Bound actions and affected resources.

- Judge the result against the actual task.


## Further reading


- [Claude: prompt engineering](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)

- [Anthropic: context engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)

- [Claude: tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
