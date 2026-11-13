# Teaching notes

The audience includes freshers and working engineers. Start with a concrete CI failure, define one new term, then show it in code/output. Ask experienced attendees to explain a failure mode while beginners identify the boundary in the diagram. Keep the examples small enough to read on a shared screen.

## Practical rhythm

Use a short explanation, run the supplied example, inspect evidence, then ask for a small edit. Aim for most technical time to involve a demo, code inspection or learner exercise; do not spend the session implementing framework plumbing from scratch. The minute-by-minute allocation is in the curriculum.

Use CI failure analysis for instructions and tool use. Use deployment documents to explain RAG. Keep project/story details for the final module. Avoid using one large codebase as the explanation for every concept.

## Questions worth asking

- Did a test fail, or did the test runner fail to start?
- Where did the tool result actually come from?
- Is this an offline scripted tool decision or a live model decision?
- Which source supports this particular recommendation?
- What would change if this document were retired or restricted?
- Who may approve, and where did that identity come from?
- Did anything execute, and what verified the result?
- What data survives a restart?

A light tone is welcome. Keep jokes brief and avoid requiring familiarity with any television show in the concept modules. The practical mistake should be memorable without turning a safety boundary into a punchline.

## Provider use

One prompt call, one bounded agent investigation and one generated RAG answer are sufficient learner live runs for Day 1. The graph can stay offline after the plain live loop is understood. Reserve attempts for failures rather than promising a fixed free quota. Do not run hundreds of live evaluations in class.

Keep synthetic inputs only. Explain that a free endpoint is still an external provider with its own privacy terms. The local embedding model is a separate download and does not provide generative answers.

## If the clock slips

Preserve the visible tool boundary, RAG pipeline, role/approval failure and final project recovery. Shorten the LangGraph inspection and routing discussion, keeping their source and references for follow-up. Use prepared solutions for learners who are stuck. Preserve breaks and questions.

If a provider fails, identify the failure and explicitly switch to labeled offline practice. If the cloud demo fails, use historical evidence with its date and say the live invocation did not complete. Do not count a recording as a successful new run.
