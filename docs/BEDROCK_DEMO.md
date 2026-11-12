# Run the local harness with Amazon Bedrock

The app uses the Bedrock Converse API for model inference. RAG extraction, Chroma, MCP tools, LangGraph checkpoints, and the synthetic checkout simulator still run locally. Starting this server does not deploy AgentCore or provision AWS hosting.

## Verified model

`us.amazon.nova-lite-v1:0` in `us-east-1` passed the full capstone on November 12, 2026:

- Called health, logs, deployments, and runbook retrieval tools, then prepared the documented correction.
- Paused before applying a change; Bagha's approval was denied.
- Continued after Jethalal's approval and verified checkout HTTP 200, including the CLI's new-Engine restart/resume path.
- A prompt claiming to be the owner could prepare a legitimate proposal but could not bypass approval.
- An unsafe-command prompt produced no proposal or applied change.

These are observed runs with a small scenario set, not a reliability benchmark. Tool ordering and call counts can vary. The app also removes tagged reasoning text from public model responses and traces; native provider metadata is not exported as reasoning.

## Start the server

From the repository directory:

```bash
uv sync --frozen --extra aws
export AWS_REGION=us-east-1
export BEDROCK_MODEL_ID=us.amazon.nova-lite-v1:0
export RUNBOOKOPS_FREE_ONLY=false
uv run runbookops --mode bedrock --embedding semantic serve --demo-auth --port 8004
```

Open <http://127.0.0.1:8004/>. Confirm the header says **BEDROCK**, then check Harness → Model & limits for the exact model ID. Select Bagha for investigation and Jethalal for the approval exercise. See [HARNESS_DEMOS.md](HARNESS_DEMOS.md) for the teaching sequence.

`RUNBOOKOPS_FREE_ONLY=false` explicitly allows billed inference. Keep the existing six-call, 16-tool-step, and 150-second investigation limits. A Bedrock invocation can still fail due to model access, IAM, quotas, or service availability.

## Authentication

The verified runs used the existing local AWS shared-credentials configuration. The app does not embed AWS credentials in browser code or MCP subprocesses.

For a Bedrock API key instead, set it in the server process environment before starting:

```bash
export AWS_BEARER_TOKEN_BEDROCK="your-bedrock-api-key"
```

Use a key valid for the chosen region and model access. The locked AWS SDK supports Bedrock bearer authentication. The API-key path was not live-tested in this verification because no Bedrock bearer key was configured. A key read only as a string from a dotenv file is not automatically exported into the AWS SDK's environment: export it in the terminal or use your secret manager's process environment integration.

AWS documentation: [use a Bedrock API key](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys-use.html), [Nova Converse and tool use](https://docs.aws.amazon.com/nova/latest/userguide/using-converse-api.html).

## CLI capstone check

With the same environment:

```bash
uv run runbookops --mode bedrock --embedding semantic demo
```

This makes real billed calls, exercises denied and authorized approval, and saves a trace under the ignored `.state/demo-latest.json`. Offline tests remain available without a provider:

```bash
uv run pytest -q
```

The instructor's verification summary is in `instructor/evidence/bedrock-local-verification.json`. The running instructor server uses port 8004; the OpenRouter server on port 8002 remains separate.
