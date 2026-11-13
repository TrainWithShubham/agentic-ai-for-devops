# From AI to agents


01 / Foundations


## What should the model decide?

A fluent incident summary can be useful before any automation exists. An agent adds a model-directed choice of next steps. DevOps engineering supplies the evidence, permissions and reliable execution around that choice.



**AI.** A broad field of systems that perform tasks associated with intelligence.


**Generative AI.** Models produce content such as text, code or images.


**Agent.** A system lets a model select steps or tools toward a goal.


## Choose the simplest useful system

Predictable work often belongs in a script. Use a fixed workflow when the sequence is known. Add model-directed choices when the next step depends on what is discovered.


### Diagram reading order


1. **Known rule:** Rotate a log file on a schedule.

2. **Known sequence:** Fetch a report, summarize it, request review.

3. **Changing investigation:** Choose which evidence to inspect after each result.



An agent can contain deterministic steps. A workflow can contain model calls. The difference is who selects the path.


## A failed CI job

The job says "pytest: command not found". Several explanations are possible until the install step is inspected.



1. **Observe:** The test runner was unavailable when the test step started.

2. **Investigate:** Read the workflow and dependency declaration.

3. **Recommend:** Propose installing the declared test dependency group.

4. **Verify:** A new CI result, not the recommendation, proves the change worked.



The example is a fictional investigation. No workflow was changed and no CI job was executed.


## Failure and correction

Calling every chatbot an agent hides which decisions and actions the system can actually perform.



Describe the available tools, who chooses them and how the system stops. Use a plain answer when that is enough.


## Engineering review


- Identify the decision the model owns.

- Name the evidence available to it.

- Keep execution authority in software.

- Compare complexity with a fixed workflow.


## Further reading


- [Anthropic: building effective agents](https://www.anthropic.com/research/building-effective-agents)
