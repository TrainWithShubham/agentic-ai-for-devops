# Build a bounded agent loop


02 / Agents and tools


## What happens after the first result?

An investigation is a loop: ask the model for a next step, run a permitted tool, return its result, then decide again. The harness must also recognize a final answer, a failure or a limit.



**State.** Track messages, evidence, remaining budget and status.


**Dispatch.** Execute only recognized, validated requests.


**Stop.** End on completion, refusal, deadline or exhausted budget.


## The smallest inspectable agent

Keep the control loop explicit before introducing a framework. Model choices can vary; application rules remain deterministic.


### Diagram reading order


1. **Decide:** Model sees the goal and current evidence.

2. **Validate:** Check the requested capability and arguments.

3. **Observe:** Run the tool and record the actual result.

4. **Continue or stop:** Return evidence, final answer or a visible limit status.



A tool error is an observation. Repeating the same failed call forever is a control failure.


## Three calls, then a proposal

Illustrative budget: at most three tool calls for a small CI investigation. This is a teaching limit, not a universal default.



1. **Call 1:** Read the failed step: the test executable is missing.

2. **Call 2:** Read the install command: development dependencies were excluded.

3. **Call 3:** Read the dependency declaration: the test runner is in that group.

4. **Stop:** Return a reviewable installation proposal and validation plan.



If evidence remains incomplete at the limit, return the findings and missing information. Do not convert a limit into success.


## Failure and correction

The model keeps asking for the same unavailable log while the caller waits without a deadline.



Track repeated failures, impose a total deadline and return a clear partial-result status when the budget is exhausted.


## Engineering review


- Set call and time limits.

- Handle final answers and tool errors.

- Record what each call changed.

- Make incomplete outcomes visible.


## Further reading


- [Anthropic: building effective agents](https://www.anthropic.com/research/building-effective-agents)

- [Google SRE: handling overload](https://sre.google/sre-book/handling-overload/)
