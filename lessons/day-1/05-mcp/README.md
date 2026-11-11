# Connect the operational tools

Time: 30 minutes, followed by the 20-minute integration and Q&A block.

MCP defines how clients discover and call capabilities. The model's tool request is a separate part of the loop. Our client adapts discovered MCP tools to model-visible schemas and validates requests before forwarding them.

```bash
uv run python examples/mcp_client.py
uv run runbookops --transport stdio investigate
```

The first command discovers tools and reads service health through a real stdio subprocess. The second runs the complete investigation using that transport. Save its incident and proposal IDs for Day 2.

Open `src/runbookops/mcp_server.py` and `scripts/mcp_entry.py`. Inspect how the trusted local identity is assigned to the server process. The model cannot supply a different user. HTTP deployment uses signed tokens rather than a user field in tool arguments.

Coding prompt:

> Explain how `get_recent_logs` is exposed through FastMCP. Add a read-only deployment-summary tool by adapting the existing deployment tool. Validate the service ID, keep results bounded, and show a client call. Do not expose arbitrary command execution.

Run the invalid-target test:

```bash
uv run pytest -q tests/test_rag_and_mcp.py
```

The server advertises read and proposal tools. Execution is handled separately after approval. Let the class inspect the discovery response rather than taking a diagram on trust.

For the final 10-minute investigation, combine health, logs, deployment history, and cited documents. Spend the remaining 10 minutes on questions. Keep the service broken until the approval exercise tomorrow.
