# Instructor: AgentCore demonstration

Learners follow [module 6](../module-6/README.md) locally. This page is for the presenter; it is not learner setup.

The previous AWS deployment was deleted on November 12 at the owner's request. These instructions do not establish a currently running deployment and do not authorize creating one. When deployment is requested, use the current standalone application's [Terraform AWS guide](https://github.com/TrainWithShubham/runbookops/blob/main/docs/AWS.md). The earlier GitHub deployment workflow was disabled and its environment configuration removed; restore those only if CI deployment is chosen.

## Prepare before class

Recreate, rehearse and verify the deployment outside the fifteen-minute demonstration. Run these commands from the **application checkout**, after deployment:

```bash
uv sync --frozen --extra aws
uv run --extra aws python deploy/manage.py probe
uv run --extra aws python deploy/manage.py smoke
uv run runbookops present --runtime-arn YOUR_RUNTIME_ARN
```

Open http://127.0.0.1:8005/. `smoke` makes billed Bedrock calls. Keep AWS credentials and the private signing key on the instructor laptop. Learners need no AWS account or access to the instructor's credits.

A fresh successful invocation is required before calling the cloud demonstration ready. Do not infer readiness from a saved trace.

## Show these boundaries

- LangGraph owns the loop; AgentCore Runtime hosts the custom code. Managed AgentCore Harness provides a separate managed loop.
- IAM authorizes the cloud invocation; application identities enforce viewer/approver permissions.
- The UI/API bridge remains local. Durable cloud state is separate from process memory.
- The correction changes a simulator, not production. An optional read-only CloudWatch source is not a remediation integration.

Show a streamed investigation, discovered MCP tools, retrieved sources and a pending proposal. Deny viewer approval, then approve through a fresh authorized session and inspect verified health. Use [the harness guide](https://github.com/TrainWithShubham/runbookops/blob/main/docs/HARNESS_DEMOS.md) and [the testing guide](https://github.com/TrainWithShubham/runbookops/blob/main/docs/TESTING.md) for current application procedures.

If the live demonstration fails, continue locally. Label any [saved release verification](https://github.com/TrainWithShubham/runbookops/blob/main/docs/VERIFICATION.md) as historical and state that a fresh invocation did not complete.

## Finish and clean up

Follow [costs and shutdown](https://github.com/TrainWithShubham/runbookops/blob/main/docs/COSTS.md). Review and delete the dedicated cloud resources after the demonstration, then verify absence. Stopping a local server does not delete cloud storage or runtime configuration.
