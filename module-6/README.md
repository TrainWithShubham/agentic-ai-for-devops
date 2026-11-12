# Module 6 — RunbookOps capstone

The application has its own repository: **[TrainWithShubham/runbookops](https://github.com/TrainWithShubham/runbookops)**.

```bash
git clone https://github.com/TrainWithShubham/runbookops.git
cd runbookops
uv sync --frozen
uv run runbookops demo
uv run runbookops --mode offline serve --demo-auth --port 8002
```

Open http://127.0.0.1:8002/. Start offline, then configure your own model key for live inference using the application's [run guide](https://github.com/TrainWithShubham/runbookops/blob/main/RUNBOOK.md).

Show the incident checks, runbook citations, MCP tools, saved agent state, viewer approval denial, and authorized recovery. Keep the technical harness visible as each step runs. Use the [beginner walkthrough](https://github.com/TrainWithShubham/runbookops/blob/main/docs/BEGINNER_DEMO.md) for short prompts and the [harness demos](https://github.com/TrainWithShubham/runbookops/blob/main/docs/HARNESS_DEMOS.md) for the wider feature tour.

Lessons and exercises remain here in the course repository. Continue with [Day 2 identity and approval](../lessons/day-2/06-identity-and-approval/README.md) and [the full lesson index](../lessons/README.md). Module 6 is the capstone entry point; it does not replace the individual Day 2 lessons.

Application fixes, tests, releases, issues, and deployment tools belong in the standalone repository. The course no longer includes a copy of the application source.
