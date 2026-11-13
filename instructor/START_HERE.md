# Instructor start page

Teach from `v2`. Modules 1–5 now use independent course examples, not a completed application. See the [timed curriculum](../CURRICULUM.md).

## Before opening the class

```bash
uv sync --frozen --extra semantic
uv run python scripts/check_course.py
uv run python scripts/verify_docs.py
uv run python -m course_labs.models
uv run python -m course_labs.prompts --live
uv run python -m course_labs.agent --live
uv run python -m course_labs.rag --backend semantic
```

The live commands need your private ignored configuration and current free capacity. They must not silently become paid/offline calls. The semantic run prepares the local model cache. Keep the corresponding keyword/offline commands ready.

Use a clean course terminal and a large font. Have three artifacts visible during teaching: the short source file, its terminal output and the input evidence. Do not open a large application during the first five modules. Reveal one boundary at a time.

## Day 1 tabs

- Module pages 1–3 and their synthetic CI/deployment fixtures.
- `prompts/ci-system.txt`, `course_labs/agent.py`, `course_labs/tools.py`.
- `course_labs/mcp_server.py`, client output and `course_labs/graph.py`.
- `course_labs/rag.py`, the manifest and `.state/deployment-index.json`.
- The completed exercise solutions for catch-up.

## Day 2 tabs

Start with modules 4–5 and the small security/operations/evaluation examples. After the break, introduce [module 6](../module-6/README.md), switch explicitly to its separate checkout and open its UI.

AgentCore is part of the Day 2 demonstration. The previous AWS resources were deleted; [module 6](../module-6/README.md#instructor-agentcore-demo) has the current rebuild, probe, paid smoke and presenter commands. A fresh successful invocation is required before describing the demo as ready. Do not use old deployment scripts from historical course notes.

Never share AWS credentials, private signing keys or model keys. The instructor owns cloud usage and cleanup. The browser/API bridge stays local. Prepare the cloud deployment before class, not during the fifteen-minute demo.

## Remaining rehearsal

Confirm class start times and a support channel with attendees. Run a timed rehearsal, verify one learner laptop and send [setup](../setup/README.md). Technical checks cannot establish that 50–100 attendees will finish every edit on time.
