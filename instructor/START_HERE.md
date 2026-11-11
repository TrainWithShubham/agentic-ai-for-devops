# Open this before teaching

The implementation is on `v2` in this `repository` directory. The previous course is preserved separately on `v1`. No GitHub push or PR was made.

## First five minutes

```bash
uv sync --frozen --extra aws
uv run runbookops preflight
uv run runbookops demo
uv run runbookops evaluate
```

The offline demo must show HTTP 503, Bagha denied approval, and HTTP 200 after Jethalal approves. This checks the full application without consuming free API quota. Run one live check after configuring your own ignored key file:

```bash
uv run runbookops --mode openrouter --embedding semantic demo
```

Learners bring individual OpenRouter keys. Your AWS account is only used for the instructor deployment. Claude Pro and the application's model API are separate.

## Teaching tabs

1. [Curriculum](../CURRICULUM.md): exact 180-minute schedules, activities, explanations, and hiring evidence.
2. [Lesson index](../lessons/README.md): commands, coding prompts, and checks for each topic.
3. [Recovery commands](../checkpoints/README.md): catch-up points without changing branches.
4. [Teaching notes](TEACHING_NOTES.md): pacing, questions, and live-call allocation.
5. [Verification](VERIFICATION.md): tests and saved live evidence, with limits stated.
6. [Decisions](../DECISIONS.md): choices, errors, and corrections made during the build.

## Day 2 cloud demo

The verified deployment was deleted on November 12 (India time) at your request. Use the deployment guide to recreate it before the cloud segment; the commands below require a fresh deployment:

```bash
uv run --extra aws python deploy/agentcore/invoke.py
uv run --extra aws python deploy/agentcore/logs.py
```

The endpoint hosts LangGraph on AgentCore Runtime and persists state in DynamoDB. Managed AgentCore Harness is a separate architecture. Cloud provisioning is not a learner task.

If network or provider access fails, identify [the saved results](VERIFICATION.md#reviewable-evidence) as historical evidence, then continue the local learner exercise. The trace viewer works with the supplied saved OpenRouter run:

```bash
uv run python scripts/trace_report.py --input instructor/evidence/openrouter-capstone.json
```

## Before November 14

Recheck the named free model on November 13, rehearse the lesson timing, and send the [setup instructions](../lessons/00-setup/README.md). A small volunteer rehearsal is still useful for finding laptop and network issues. The technical checks do not substitute for that rehearsal.

After the workshop, use the project [cleanup instructions](../deploy/agentcore/README.md#cleanup). The AWS resources remain available until you run cleanup.
