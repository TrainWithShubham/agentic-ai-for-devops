# What makes it an agent?

Time: 25 minutes, after the opening incident demo.

Bagha reports that checkout fails while the catalogue still works. Ask the class what they would check. Then compare pasting the error into a chatbot, running a fixed script, and letting an agent choose among operational tools.

Explain AI, generative AI, LLMs, tokens, context limits, and hallucinations using this incident. Keep examples concrete: an explanation of HTTP 503 is general knowledge; the current payment URL is company-specific evidence.

Open the short example:

```bash
uv run python examples/first_call.py
```

Offline mode prints an explicit practice response. With a key configured:

```bash
uv run python examples/first_call.py --mode openrouter
```

Read `src/runbookops/models.py`. Find the system message, user message, provider call, and model output. An agent also needs a bounded loop and tools. LangGraph organizes the state and control flow; it does not make evidence correct by itself.

Class exercise: classify a health-check script, a document chatbot, an incident investigator, and a deployment pipeline. Discuss where fixed steps are easier to test.

Check understanding: the learner can explain why a model cannot know whether our checkout service is healthy without current evidence.

Optional: sketch where company knowledge, live service data, and saved workflow state belong. Those are different forms of context.
