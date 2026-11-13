# Recovery checkpoints

Run these commands from the course root. Each concept example works without the final project checkout. Offline examples need no model key.

| Module | Working example | Completed learner edit |
|---|---|---|
| 1 | `uv run python -m course_labs.prompts` | Compare your prompt with `prompts/ci-system.txt` |
| 2 | `uv run python -m course_labs.agent` | `uv run python scripts/check_exercise.py ci --solution` |
| 2: MCP | `uv run python -m course_labs.mcp_client` | Inspect discovered tools and the actual log result |
| 2: graph | `uv run python -m course_labs.graph` | Identify the state and model/tools nodes |
| 3 | `uv run python -m course_labs.rag` | `uv run python scripts/check_exercise.py rag --solution` |
| 4 | `uv run python -m course_labs.security` | `uv run python scripts/check_exercise.py approval --solution` |
| 5 | `uv run python -m course_labs.operations` | `uv run python scripts/check_exercise.py evaluation --solution` |
| 5: evaluations | `uv run python -m course_labs.evaluations` | Explain the deliberately bad candidate's failures |

The [module-6 page](../module-6/README.md) owns the separate project and cloud-demo recovery instructions.

Save your work before comparing with `solutions`. There is no destructive reset command and no need to switch branches during class. To check the full course, run `uv run python scripts/check_course.py` and `uv run python scripts/verify_docs.py`.
