# Give it a health-check tool

Application commands and paths below refer to the standalone [`runbookops`](https://github.com/TrainWithShubham/runbookops) checkout. Course exercises are the exception where noted.

Time: 25 minutes.

Run the small tool-loop example before opening the full capstone:

```bash
uv run python examples/simple_agent.py
uv run python examples/simple_agent.py --mode openrouter
```

Follow the printed exchange: the model requests `get_service_health`, the application validates the arguments, the tool returns a result, and that result reaches the model. The example never exposes a write tool.

Read the tool schema in `src/runbookops/tools.py`. Notice the service enum and the ban on extra properties. Then open `examples/simple_agent.py` and find the local execution boundary.

Coding exercise:

> In the course checkout, implement `health_summary` in `exercises/health_tool.py`. Accept a health dictionary and return a short summary containing the service, status, and HTTP status. Reject unknown services and missing fields. Do not call a model or run a shell command.

Run the exercise checker from the **course** checkout (standard Python; no application install required):

```bash
python3 scripts/check_exercise.py health
```

Use `solutions/health_tool.py` if you need to catch up. Check the output against the actual tool dictionary; a plausible sentence alone is not a successful test.

Discuss tool timeouts, maximum model calls, and what an assistant should say when a tool fails. The full agent has both a model-call budget and a tool-step budget.

Check understanding: the learner can point to the code that executes a model-requested tool and explain why an unknown service is rejected.
