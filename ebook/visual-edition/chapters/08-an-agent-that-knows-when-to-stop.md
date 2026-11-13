# An agent that knows when to stop


02 / Agents and tools


## In everyday words

An agent loop repeats a simple process: choose a step, check the request, run a tool and inspect the result.


## Picture it

A detective checks one clue, then decides where to look next. A deadline stops the search from running forever.

The model may choose poorly. Software must enforce limits.



**State.** What the investigation knows so far.


**Budget.** How much work it may do.


**Stop reason.** Why the run ended.


## The smallest inspectable agent

Keep the loop visible. Each tool result should help the next decision.


### Diagram reading order


1. **Decide:** Choose a tool or an answer.

2. **Validate:** Check the request.

3. **Observe:** Save the actual tool result.

4. **Continue or stop:** Respect the remaining budget.



Return partial findings when time or calls run out. Do not label a limit as success.


## Three calls, then stop

Three is an example limit for this small investigation.



1. **Call 1:** Read the missing-command error.

2. **Call 2:** Read the dependency install step.

3. **Call 3:** Find the declared test dependency.

4. **Stop:** Propose a fix and a validation check.



A tool error is useful evidence, not a reason to repeat forever.


## Failure and correction

Calling the same unavailable tool again and again.



Limit calls, detect repeated failures and return partial results.


## Engineering review


- Call limit.

- Total deadline.

- Error handling.

- Clear final status.


## Further reading


- [Anthropic: building effective agents](https://www.anthropic.com/research/building-effective-agents)

- [Google SRE: handling overload](https://sre.google/sre-book/handling-overload/)
