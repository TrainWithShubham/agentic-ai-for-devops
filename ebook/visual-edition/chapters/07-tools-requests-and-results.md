# Tools: requests and results


02 / Agents and tools


## In everyday words

A tool is a capability your application can run. The model requests it; trusted code checks the request and returns the result.


## Picture it

A waiter passes an order to the kitchen. The order is a request; the kitchen decides what it can serve.

The model request itself does not run the action or grant permission.



**Name.** What the tool can do.


**Arguments.** The values the tool needs.


**Result.** What actually happened or failed.


## Follow one tool request

Follow the request through the application before trusting a completion claim.


### Diagram reading order


1. **Model:** Requests a CI log.

2. **Application:** Checks tool, input and caller access.

3. **Tool:** Returns a bounded log excerpt.

4. **Model:** Uses the observed result.



Tool descriptions help selection. The executor must still validate and authorize the call.


## Read one CI log

A narrow reader is easier to control than a general shell.



1. **Input:** One known run ID.

2. **Check:** Reject unknown IDs and extra fields.

3. **Return:** Run ID, source location and log text.

4. **Error:** Say "not found" if the run is missing.



A requested action and a completed action are different events.


## Failure and correction

Giving the model an unrestricted shell for a simple log question.



Expose a narrow log reader with access checks.


## Engineering review


- Clear tool name.

- Checked inputs.

- Limited output.

- Recorded result.


## Further reading


- [Anthropic: writing tools](https://www.anthropic.com/research/writing-tools-for-agents)

- [Claude: tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
