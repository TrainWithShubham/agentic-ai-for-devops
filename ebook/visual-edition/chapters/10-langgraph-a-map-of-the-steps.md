# LangGraph: a map of the steps


02 / Agents and tools


## In everyday words

LangGraph helps describe an agent as a map: state holds information, nodes do work and edges choose where to go next.


## Picture it

A route map shows stations and connections. Your agent map shows steps and possible next steps.

A graph shows control flow; it does not grant permission for a write.



**State.** Information carried between steps.


**Node.** A step that reads or updates state.


**Edge.** A route to the next step.


## Draw the actual control flow

Make tool use, answers and review visible as separate routes.


### Diagram reading order


1. **Model:** Choose a tool or an answer.

2. **Tools:** Check inputs and return results.

3. **Review:** Pause; this node restarts on resume.

4. **End:** Record the final or incomplete result.



On resume, code before interrupt() runs again. Use a persistent checkpointer and protect side effects from repeating. Recheck approval before any write.


## Pause, then continue

A release proposal waits for human review.



1. **Save:** Keep thread progress in a suitable checkpointer.

2. **Pause:** Show the exact proposal for review.

3. **Resume:** The node starts again. Use the correct thread and trusted decision.

4. **Recheck:** Check identity, proposal and current target state.



In-memory checkpoints disappear on restart. Durable storage is a separate choice.


## Failure and correction

Calling a run resumable when its only copy is in one process.



Use persistent storage and check thread ownership.


## Engineering review


- Visible state.

- Clear routes.

- Owned threads.

- Restart test.


## Further reading


- [LangGraph: overview](https://docs.langchain.com/oss/python/langgraph/overview)

- [LangGraph: persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

- [LangGraph: interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
