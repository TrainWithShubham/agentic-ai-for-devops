# Local HTTP API

Start the API from the repository directory:

```bash
uv run runbookops serve
```

Open `http://127.0.0.1:8000/docs` for the schema. Health and public issuer metadata are unauthenticated. Incident data requires a signed token.

Run the complete HTTP exercise without displaying tokens:

```bash
uv run python scripts/demo_api.py
```

It verifies anonymous access is denied, starts an investigation as Bagha, attempts approval as Bagha, then approves as Jethalal and checks HTTP 200.

| Method and route | Purpose |
|---|---|
| `GET /health` or `/ping` | Process health and mode |
| `GET /me` | Verified caller identity and scopes |
| `POST /investigations` | Start a new isolated incident |
| `GET /incidents/{id}` | Read authorized incident and graph status |
| `GET /incidents/{id}/trace` | Read sanitized incident events |
| `POST /proposals/{id}/decision` | Approve or reject the exact reviewed hash |
| `POST /incidents/{id}/resume` | Resume a stored decision after an interrupted execution |
| `POST /invocations` | AgentCore-compatible operation envelope |
| `GET /oidc/.well-known/openid-configuration` | Local development issuer description |
| `GET /oidc/jwks.json` | Public verification key |

`uv run runbookops --as bagha token` intentionally prints a short-lived development token for manual Swagger testing. It is not an OpenRouter key. Avoid recording tokens on screen.

The server rejects extra request fields. Sending `role=approver` or saying that Jethalal approved a change cannot grant authorization. A signed token's subject is mapped to the server's known users, and scope restrictions are enforced at the operation boundary.

## Optional remote MCP exercise

In one terminal:

```bash
uv run python -m runbookops.mcp_server --transport http --port 8001
```

In another:

```bash
uv run python examples/remote_mcp.py
```

The client obtains a local development JWT without displaying it, and the HTTP MCP server verifies it before serving the incident's health. Both processes use the same `.state` directory. For a separate machine, configure the external issuer/key and a reachable HTTPS endpoint; do not expose the local development setup directly to the internet.
