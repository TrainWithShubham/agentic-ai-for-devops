# November delivery plan

Course dates: 14 and 15 November 2026. Expected attendance: 50 to 100. Each day is 180 minutes including breaks and questions. Exact start times are not yet specified.

## Before the first session

| Date | Work | Evidence needed |
|---|---|---|
| November 11 | Preserve existing modules, prepare the V2 branch and docs, choose model-access approach | Separate branch and explicit build status |
| November 12 | Build the local checkout simulator, knowledge loaders/retrieval, agent, and MCP tools; implement approval and role checks | One incident runs from failure to approved recovery, with denial checks |
| November 13 | Finish model gateway, validate provider tool calling, deploy the instructor Runtime demo, rehearse both days, freeze learner setup | Clean-machine install, live-provider run, 100-attendee load check, recorded fallback, timed rehearsal |
| November 14 | Deliver Day 1 | Learners save the working investigation checkpoint |
| November 15 | Deliver Day 2 | Learners save capstone evidence and actual evaluation results |

This is a tight schedule. Freeze the core when it works. Move optional integrations to follow-up material rather than rushing untested setup into class.

## Build order

1. Seeded checkout incident and read-only operational tools.
2. Company knowledge in PDF, DOCX, PPTX, MD, and TXT; tested extraction and local embeddings.
3. Bounded LangGraph investigation using retrieved evidence and MCP tools.
4. Proposal, role-authorized approval, persistence, expiry, and replay protection.
5. Scenario runner and structured traces, including denied and failed cases.
6. Sponsored Bedrock model gateway and independently revocable learner access.
7. Same application on AgentCore Runtime, with reachable remote tools and external checkpoint/approval storage.
8. Lesson prompts, starter/completed checkpoints, devcontainer, troubleshooting, and rehearsal recording.

Keep the previous course's modules in place. Reuse small patterns after reviewing them; do not bring the old Kubernetes/Ollama prerequisites into the learner path.

## What must be real before class

- A complete local incident recovery, including rejection and unauthorized-approval cases.
- A live model capable of the exact structured tool exchange used by the application.
- A tested no-purchase learner path. Do not assume Claude Pro supplies API credits.
- A setup check that a learner can run without AWS credentials.
- A working checkpoint for each lab and a trace that makes failures visible.
- A clear record of which AWS features are live and which are recorded demonstrations.

## Class operations

For 50 to 100 attendees, avoid live account creation and package/model downloads. Send setup instructions before class and reserve a small number of live model runs per module. Run most validation cases without provider calls.

The exact support channel or helper arrangement is not yet confirmed. Provide written recovery steps so setup debugging does not stop the main session. A helper is useful if available, but do not design the labs around one being present.

Keep a stable incident seed and learner-specific namespaces. One attendee must not alter another attendee's simulator state. Publish endpoint shutdown and cleanup instructions.

## Scope cuts if rehearsal fails

Preserve foundations, RAG inspection, MCP tools, authorized approval, and recovery verification. Keep caching/routing to a prepared configuration exercise. Use the Runtime recording if cloud provisioning or service limits interfere. Managed Knowledge Bases, full OAuth provider setup, Gateway/Identity integration, and Temporal remain extensions.

Do not call the gateway, cloud demo, or learner labs ready until their checks pass. The documents on this branch currently describe planned implementation.

## Git policy

Work on `course-v2-runbookops`. Use short commit messages. Do not add co-author trailers, create a PR, change the default branch, or merge into `main` for this delivery. Do not tag an assumed historical teaching commit; identify it with the instructor first.
