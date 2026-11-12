# Run the same graph on AgentCore Runtime

Application commands and paths below refer to the standalone [`runbookops`](https://github.com/TrainWithShubham/runbookops) checkout. Course exercises are the exception where noted.

Time: 30-minute instructor demonstration.

Learners inspect the adapter and cloud evidence. They do not need AWS credentials or a cloud deployment to finish the local capstone.

Read [the instructor deployment guide](https://github.com/TrainWithShubham/runbookops/blob/main/deploy/agentcore/README.md). AgentCore Runtime hosts our LangGraph application. AgentCore Harness provides a separate managed loop; it is not the host for this custom graph.

The instructor shows the ARM64 image, `/ping` and `/invocations`, Runtime IAM admission, and the forwarded signed application identity. The local development issuer is kept separate from production identity-provider guidance.

The cloud demo uses the same operational tool schemas and simulator behavior. MCP runs in process inside the hosted app, with the authenticated principal bound in application code. Incident, proposal, and approval state use DynamoDB, and the graph uses a DynamoDB checkpointer. Starting another Runtime session does not lose the pending proposal.

Demonstrate: investigate as Bagha, deny Bagha's approval, approve as Jethalal in another Runtime session, and verify HTTP 200. Inspect the saved report and structured CloudWatch logs. The image contains the small semantic embedding model so it does not need a live model download during the session.

Check understanding: explain which component hosts the agent, which component owns its decision loop, and where approval survives a runtime replacement.

The final 15-minute capstone block is a learner acceptance run. Reserve the last 20 minutes for questions, interview explanation, and a chosen extension. Do not count the instructor's AWS deployment as a learner's personal deployment.
