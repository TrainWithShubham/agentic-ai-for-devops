# Make state visible with LangGraph


02 / Agents and tools


## Where is the investigation now?

LangGraph represents application flow using state, nodes and edges. It is useful when the next step, saved progress and review boundary should be visible in the design.



**State.** Shared data such as messages and retrieved evidence.


**Node.** An operation that reads state and returns an update.


**Edge.** A fixed or conditional route to the next operation.


## Draw the actual control flow

A model node may request a tool. A conditional route selects the tool node or the final path. Keep validation and authorization inside the relevant application operations.


### Diagram reading order


1. **Model:** Choose a tool or produce a response.

2. **Tools:** Validate, execute and return observations.

3. **Review:** Pause before an authorized write.

4. **End:** Record final, refused or incomplete status.



A graph does not make a side effect safe. Re-executed work still needs an idempotency design.


## An investigation survives a pause

A graph-based release assistant needs to remember which proposal is waiting for review.



1. **Save:** Persist the thread state with a suitable checkpointer.

2. **Pause:** Interrupt with the exact proposal details required by the reviewer.

3. **Resume:** Use the correct thread and a validated approval result.

4. **Recheck:** Confirm identity, proposal integrity and current preconditions.



In-memory checkpoints disappear with the process. Durable storage and authenticated thread ownership need explicit choices.


## Failure and correction

The UI says "resumable", but progress exists only in a Python object in one worker.



Choose persistent checkpoint storage and test restart behavior. Keep cross-thread knowledge separate from thread state.


## Engineering review


- Name the state fields.

- Label conditional edges.

- Scope thread ownership.

- Test the pause and resume boundary.


## Further reading


- [LangGraph: overview](https://docs.langchain.com/oss/python/langgraph/overview)

- [LangGraph: persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

- [LangGraph: interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
