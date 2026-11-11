# Instructor deployment on AgentCore Runtime

This deploys the same LangGraph project used locally. AgentCore Runtime hosts the code; managed AgentCore Harness is a different orchestration choice.

The instructor account pays for Bedrock and hosting. Learners keep their own OpenRouter keys and need no AWS account.

## Architecture

- Linux ARM64 container exposing `/ping` and `/invocations` on port 8080.
- Bedrock Nova Lite inference through a discovered cross-region profile.
- A dedicated role scoped to the selected model/profile, project tables, image, and log groups.
- IAM authentication at Runtime admission, plus a short-lived signed workshop JWT forwarded through the allowlisted `X-RunbookOps-Token` header.
- The same in-process MCP tools, with identity bound by the application.
- DynamoDB incident/proposal state and `DynamoDBSaver` graph checkpoints.
- Semantic embedding model included in the image; the small knowledge index is built from the packaged documents.
- Sanitized JSON incident events in CloudWatch.

This is a workshop identity setup, not a production OAuth identity provider. The public verification key goes into Runtime configuration with escaped newlines. The private signing key remains in the instructor's local ignored `.state` directory and never enters the image.

The tested service trust policy uses the AWS-documented source-account and region-scoped SourceArn pattern. Exact runtime ARN matching failed during this deployment. Resource permissions remain scoped to this project. See [Runtime permissions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html) and [the decision record](../../DECISIONS.md).

## Build and deploy

Use an AWS login/profile with permission to create the project's ECR repository, two tables, dedicated role, and runtime, and to pass that role. The application uses the standard AWS credential chain; do not place credentials in files tracked by Git.

```bash
uv sync --frozen --extra aws
docker build --platform linux/arm64 -f deploy/agentcore/Dockerfile -t runbookops:v2 .
uv run --extra aws python deploy/agentcore/deploy.py
```

The script records every created resource under `.state/aws-deployment.json`. It generates a fresh project prefix to avoid changing existing infrastructure. Docker push authentication uses a temporary configuration directory.

Do not create another stack if a step fails. Once the tables, role, and image exist, continue Runtime provisioning with:

```bash
uv run --extra aws python deploy/agentcore/deploy.py --resume
```

The original verified deployment was deleted on November 12 (India time) at the instructor's request. Run the build/deploy steps above to recreate it before the live workshop. Saved evidence remains available for an offline walkthrough.

## Update the existing deployment

After a source change, rebuild the image and publish a new immutable tag to the same recorded runtime:

```bash
docker build --platform linux/arm64 -f deploy/agentcore/Dockerfile -t runbookops:v2 .
uv run --extra aws python deploy/agentcore/update.py
uv run --extra aws python deploy/agentcore/invoke.py
```

The updater preserves the role, tables, identity configuration, and workshop endpoint name. It waits for the new version to become ready. Version 2 was built and invoked during verification.

## Demonstrate the incident

```bash
uv run --extra aws python deploy/agentcore/invoke.py
```

The client signs AWS requests and supplies a short-lived Bagha or Jethalal JWT without printing it. It investigates as Bagha, checks viewer approval is denied, and approves as Jethalal in a separate Runtime session. It verifies HTTP 200 and saves `artifacts/cloud-capstone.json`.

A new session is intentional: the demonstration relies on durable DynamoDB state, not a microVM's local SQLite file. Keep the local issuer key while using this deployment; replacing it requires updating the deployed public key.

Read structured events for the cloud incident:

```bash
uv run --extra aws python deploy/agentcore/logs.py
```

The JSON logs support the course's observability exercise. Full AgentCore managed trace instrumentation is not automatically claimed. The current image contains no generic shell tool or browser tool.

## Thirty-minute teaching sequence

| Minutes | Demonstration |
|---|---|
| 0 to 4 | Runtime vs. Harness, code ownership, and architecture |
| 4 to 10 | Entrypoint, image, role, and completed provisioning output |
| 10 to 18 | Authenticated investigation and source/tool evidence |
| 18 to 25 | Denied approval, authorized approval from another session, health verification |
| 25 to 30 | CloudWatch events, failure handling, and cleanup |

Build and provisioning run before class. Use the saved evidence if the service is unavailable, and identify it as recorded evidence. Learners complete the local capstone either way.

## Cleanup

After the workshop, remove only the recorded project resources:

```bash
uv run --extra aws python deploy/agentcore/cleanup.py
```

Cleanup checks the account and project names before deleting the runtime, tables, ECR repository, dedicated role, and matching log groups. Export the trace first if you want to retain it. The tables have seven-day TTL for rows, which does not delete the tables or the image repository by itself.

## Optional extensions

Use a production OIDC issuer with JWT admission and forward `Authorization`; connect an authenticated remote MCP server; replace the packaged index with a Managed Knowledge Base; or add verified OpenTelemetry instrumentation. These are separate exercises, not prerequisites for this workshop.
