# Prompts you can adapt


01 / Foundations


## In everyday words

A useful prompt says what you need, gives evidence and asks for a result you can check. No prompt is best for every task.


## Picture it

"Two cups of chai, no sugar" is easier to follow than "make something good".

Clear instructions help. Software permissions still decide which actions are allowed.



**Goal.** The question or change you need.


**Evidence.** The material the answer should use.


**Result.** The output and check you expect.


## Give the request a clear shape

Replace vague praise such as "production ready" with concrete requirements.


### Diagram reading order


1. **Goal:** Explain the failed job.

2. **Evidence:** Use this log and workflow.

3. **Boundary:** Do not edit or run commands.

4. **Acceptance:** Cite facts and suggest validation.



Ask for a short explanation tied to sources. Check it against those sources.


## Four prompts to adapt

Supply the named evidence before using these examples.



1. **CI failure:** Use this log and workflow to explain the failed step. Cite lines. Separate facts from guesses. Propose the smallest fix and a check. Do not edit files.

2. **Document answer:** Use these deployment excerpts to say who approves rollback. Cite the section. Say if evidence is missing or conflicting. Do not grant approval.

3. **Terraform review:** Review this Terraform diff. Explain changed resources, possible replacement and access changes. State uncertainty and suggest checks. Do not apply it or invent a cost.

4. **Incident summary:** Summarize these sanitized events as facts, hypotheses and next read-only checks. Include time and sources. Claim recovery only with a confirming observation.



These are starting points, not measured guarantees.


## Failure and correction

Making the persona longer while leaving out the logs.



Improve the evidence and success criteria first.


## Engineering review


- Name the task.

- Supply evidence.

- Set boundaries.

- Check the answer.


## Further reading


- [Claude: prompt engineering](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)

- [Anthropic: context engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents)

- [Claude: tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
