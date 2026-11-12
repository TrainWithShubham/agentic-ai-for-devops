# Recover during a lab

Application commands and paths below refer to the standalone [`runbookops`](https://github.com/TrainWithShubham/runbookops) checkout. Course exercises are the exception where noted.

The repository contains a completed application and short isolated examples. You can return to a working flow without discarding your changes.

| Point in the course | Recovery command |
|---|---|
| First model call | `uv run python examples/first_call.py` |
| Read-only tool | `uv run python examples/simple_agent.py` |
| Knowledge extraction | `uv run python examples/rag_pipeline.py` |
| Retrieval | `uv run runbookops index` then `uv run runbookops search "checkout payment runbook"` |
| MCP connection | `uv run python examples/mcp_client.py` |
| Approval and full recovery | `uv run runbookops demo` |
| Identity checks | `uv run python scripts/demo_identity.py` |
| Outcome evaluation | `uv run runbookops evaluate` |
| Completed health exercise | `python3 scripts/check_exercise.py health --solution` (course checkout) |

Offline commands need no API key. For a live example, add its documented mode flag. Keep live requests limited; restarting a demo creates a new isolated simulator incident rather than deleting your previous evidence.

Save learner edits before comparing with `solutions`. There is no destructive reset script and no need to check out another branch mid-class. These are executable recovery points, not separate copies of the entire application.
