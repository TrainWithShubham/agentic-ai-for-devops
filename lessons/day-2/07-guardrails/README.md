# Try the requests the agent should refuse

Application commands and paths below refer to the standalone [`runbookops`](https://github.com/TrainWithShubham/runbookops) checkout. Course exercises are the exception where noted.

Time: 15 minutes.

Read `suspicious-note.txt`. It contains an injected instruction telling the assistant to skip approval. The text is retrieval data; it cannot change the server's role mapping or authorize execution.

```bash
uv run pytest -q tests/test_controls.py tests/test_rag_and_mcp.py
uv run runbookops evaluate
```

Inspect tool enums, extra-argument rejection, step limits, and redaction in `tools.py`, `agent.py`, and `security.py`. A free model still needs bounded execution. A failed model call must not silently become an offline success.

Coding prompt:

> Add a synthetic adversarial test for an unsupported service or configuration value. Assert that it is rejected and the simulator remains at HTTP 503. Use the existing store fixture. Keep keys and real customer data out of the test.

Inspect one trace and confirm the synthetic key from the log fixture was redacted. Explain that masking a final answer does not remove a secret already sent to a provider; redact tool results before model input.

A useful classroom line: writing "approved by Jethalal" inside a PDF does not make it an approval system.

Bedrock Guardrails can add content safeguards in the instructor's AWS architecture. Our operational permission checks remain necessary. Configuring the managed service is an extension; do not describe it as active in the local application.

Check understanding: the learner identifies which application check blocks an unauthorized change even if a model follows the malicious note.
