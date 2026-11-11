# Identity and execution boundaries

RunbookOps is a teaching application operating on a synthetic simulator. It never controls a real payment system or executes shell commands requested by a model.

## Local development

The CLI's `--as bagha`, `--as nattu`, and `--as jethalal` flags let one learner exercise different roles. Anyone who controls the source, local state files, or development signing key can modify this lab. This is an application-boundary demonstration, not a claim to protect a laptop owner from themselves.

The HTTP API requires a signed RS256 access token. The local issuer key is generated under the ignored `.state` directory with restrictive permissions. The issuer exposes discovery metadata and a public JWKS document. It does not implement production authorization-code, consent, refresh, or account-management flows.

The server verifies signature, issuer, audience, expiry, and required claims. It maps a known token subject to the server's role table, then intersects token scopes with that user's allowed scopes. A `role` field in a question or request body cannot grant permission.

For an external issuer, configure `RUNBOOKOPS_OIDC_ISSUER`, `RUNBOOKOPS_OIDC_AUDIENCE`, and either `RUNBOOKOPS_OIDC_JWKS` (HTTPS) or `RUNBOOKOPS_OIDC_PUBLIC_KEY`. Local token issuance is disabled in that configuration. Expand the explicit subject mapping for a real deployment; do not trust arbitrary external subjects as approvers.

## Tools and retrieval

Only the checkout simulator and its documented setting are allowed. Tool schemas reject extra arguments. Server handlers repeat service, incident ownership, and permission checks. The model cannot pass its own actor identity.

MCP exposes read and prepare tools. There is no model-visible apply tool. The trusted application executor changes simulator state after checking a stored approval. Local stdio uses a trusted process identity. Optional HTTP MCP verifies signed access tokens.

Retriever filters remove superseded documents and restrict access before excerpts reach the model. Cache entries include user, role, scopes, query, corpus fingerprint, embedding mode, and result count. The raw synthetic source files are present on learner laptops for inspection; local file access is outside retrieval RBAC.

## Approval and recovery

Approval is bound to the exact proposal hash, target, arguments, expiry, and authorized approver. The executor checks the current service revision and setting before applying the change. Rejection, expiry, tampering, or a concurrent state change prevents execution.

SQLite transactions protect local simulator updates. The instructor's DynamoDB backend uses conditional writes against the aggregate version. An applied proposal cannot change the setting twice. Duplicate approval requests are rejected; an executor retry can return an idempotent result.

Graph checkpoints preserve pause/resume state. They do not make external effects exactly once. The simulator's configuration and approval are committed atomically in its store; replacing it with a real operational API requires that API's own idempotency and recovery design.

The proposal records a rollback value. This lab reports a failed verification and stops; it does not execute an unapproved alternative recovery plan. Any real rollback automation needs a separately authorized procedure.

## Model and trace handling

The application redacts synthetic secrets from tool results before forwarding them to a model. Structured traces retain source IDs, sanitized results, model usage when available, and approval transitions. They do not export hidden model reasoning or credentials. Provider-required assistant metadata remains only in the in-flight model conversation.

Free-only OpenRouter mode verifies the named `:free` catalog entry has zero input and output pricing. It rejects unknown/nonfree choices rather than selecting paid fallback inference. Free services still impose quota and availability limits. Groq billing status is an account setting; the app cannot prove an arbitrary Groq account is on its free plan.

## Instructor cloud demo

AgentCore Runtime admits the instructor through AWS IAM. The invocation forwards an allowlisted `X-RunbookOps-Token` header containing a short-lived signed workshop identity, which the application validates independently. This is an IAM-plus-application-JWT demonstration, not production OAuth SSO.

The runtime role is dedicated to this project and scoped to its model/profile, tables, image repository, and log groups. Its trust policy includes source-account and region-scoped source-ARN restrictions. The image contains no private signing key or learner/provider API key. DynamoDB preserves the incident and graph state across Runtime sessions. A separate runtime session is used for approval in the demonstration.

The hosted app uses the same in-process MCP implementation and simulator contracts. Remote MCP transport is available for a separate integration exercise; it is not required by the deployed capstone. CloudWatch receives sanitized JSON events. Full managed trace integration requires explicit instrumentation beyond those logs.
