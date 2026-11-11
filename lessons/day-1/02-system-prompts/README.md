# Give the assistant a clear job

Time: 20 minutes.

Start with `exercises/system_prompt.txt`. It contains a deliberately vague instruction. Compare it with `SYSTEM` in `src/runbookops/models.py`.

Ask Claude Code or Codex:

> Rewrite the exercise prompt for a read-only checkout investigator. Require observed evidence, exact source IDs, uncertainty when evidence is missing, and a proposed next step. Do not imply the model can approve changes. Keep it short enough to read aloud.

Run the first-call example before and after editing its exercise prompt:

```bash
uv run python examples/first_call.py --prompt-file exercises/system_prompt.txt
uv run python examples/first_call.py --mode openrouter --prompt-file exercises/system_prompt.txt
```

A useful answer says what is known and what must still be checked. It should not claim to have read logs or changed a configuration when it has done neither.

Classroom line: Jethalal asked for checkout help. That does not give the assistant permission to redesign the shop.

Inspect the Bedrock adapter in `models.py`. The instructor can demonstrate the equivalent provider call; learners continue using their own OpenRouter keys.

Check understanding: identify one instruction the prompt can express and one restriction the application must enforce. A prompt can request approval; code must prevent execution without it.
