# Teaching notes

Run application commands from the standalone [`runbookops`](https://github.com/TrainWithShubham/runbookops) checkout; this repository contains the teaching material.

Use the [timed curriculum](../CURRICULUM.md) and [lesson index](../lessons/README.md). Keep the Gada Electronics story in the incident messages and permission examples. Keep the code, runbooks, and results professional. Every technical explanation should work for someone who has not watched the show.

## Rehearse before the event

```bash
uv sync --frozen --extra aws
uv run runbookops preflight
uv run runbookops --embedding semantic index
uv run runbookops demo
uv run runbookops evaluate
uv run pytest -q
uv run python examples/mcp_client.py
uv run python scripts/demo_identity.py
uv run python scripts/trace_report.py
```

Run one live OpenRouter capstone with your own ignored key file and the model selected for the class. Do not use that one account for all learners. The tested candidate is in `.env.example`; recheck the free catalog before the session.

The instructor cloud demo has its own scripts and recorded resource information. Invoke the existing deployment once before Day 2; do not provision while teaching.

## Day 1

Open with the checkout failure and two learner suggestions about evidence. Show the completed project briefly, then return to the first-call example. Explain the agent loop before showing the larger graph.

Use one small coding-assistant request at a time. Read the diff and run a check after each change. A learner without a coding subscription can inspect the completed example or solution.

Before the break, everyone should understand where a model-requested tool actually executes. After the break, open the extracted document text before the generated answer. A citation is useful only if the source supports the claim.

Leave 10 minutes to combine sources and tools, and 10 minutes for questions. Save an incident awaiting approval. If a learner is behind, use the command in `checkpoints/README.md`; do not spend the whole class repairing one environment.

## Day 2

Start with the saved investigation. Ask who can authorize a change. Show Bagha denied approval before Jethalal succeeds. For expiry/replay, use the tests and inspect state, rather than changing the computer clock.

Use the local token demo to explain signature, audience, expiry, scope, and role mapping. Distinguish OAuth delegated access from a local development issuer; do not imply a complete production consent flow was built.

Run an injected-document and invalid-tool case. Explain why code still blocks execution if a model follows a bad instruction. Bedrock Guardrails is an additional managed safeguard discussed as an extension.

Show the retrieval cache and configured model route. If both tasks select the same model because no second one is configured, say so. Do not spend live calls trying many public free models during class.

Run the evaluation set and inspect a denied case. Use the cloud segment to show the same graph with durable external state. Keep the final learner acceptance run and Q&A even if a cloud outage forces the saved-evidence fallback.

## Live-call budget

A complete investigation has at most six model calls; the supplied offline checks use none. Plan two capstone investigations per learner per day at most, a first-call exercise, a simple tool exchange, a few RAG questions, and one provider preflight. The design target is below 30 live model calls per learner per day, including reasonable retries, against the currently documented 50-request OpenRouter free cap.

The final verified OpenRouter capstone used five calls and 7,980 total tokens; approval used no extra inference. Check the measured count in actual traces. Tool calls are not model requests; several tool requests can fit in one model response. A failed inference can still consume provider quota. No public free tier guarantees class-wide capacity.

## What learners should be able to explain

- Why the current logs and deployment matter even when a similar old incident exists.
- Which company sources were retrieved and how access was filtered.
- How MCP connects the tools and where the arguments are checked.
- Why a model-generated approval cannot execute a change.
- Where the pending proposal survives a restart.
- Which checks demonstrate safety, and which results require manual quality review.
- What they ran themselves and what they only saw in the instructor AWS demonstration.

A useful interview explanation is in the curriculum. Encourage each learner to add one small extension and describe its evidence rather than claiming production experience from a six-hour workshop.
