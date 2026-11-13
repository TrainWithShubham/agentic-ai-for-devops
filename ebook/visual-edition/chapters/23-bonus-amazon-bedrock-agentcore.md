# Bonus: Amazon Bedrock AgentCore


Bonus / AgentCore


## Which layer do you want managed?

AgentCore includes services for running and connecting agents. The key choice is whether you bring an existing agent loop to Runtime or use the managed Harness loop configured for you.



**Runtime.** Host your code, including a LangGraph application.


**Managed Harness.** Configure an agent whose orchestration loop is supplied.


**Supporting services.** Use Gateway, Identity, Memory and observability as appropriate.


## Hosting and orchestration are different

For the course LangGraph design, Runtime hosts the custom loop. Managed Harness is a separate approach powered by Strands; it is not a wrapper that hosts a LangGraph graph unchanged.


### Diagram reading order


1. **Your loop:** LangGraph or custom code deployed to AgentCore Runtime.

2. **Managed loop:** Harness configuration selects model, tools and limits.

3. **Tool connection:** Gateway can expose APIs and services as MCP-compatible tools.

4. **App boundary:** Your UI/API, user authorization and approval rules remain explicit.



This is an architecture guide, not a deployment transcript. Verify current service support, quotas, regional availability and pricing before using AWS.


## An instructor-only hosted investigation

The browser talks to an authenticated application boundary. AWS credentials stay on the trusted backend.



1. **Choose:** Keep the LangGraph loop and use Runtime, or adopt managed Harness deliberately.

2. **Configure:** Scope execution roles, tool access, model permissions and request limits.

3. **Observe:** Inspect actual invocation events and durable application state.

4. **Clean up:** Review dedicated resources, logs and storage after the demonstration.



Managed sessions and memory do not replace a transactional approval record. Runtime isolation does not define who may approve an application action.


## Failure and correction

A public client forwards arbitrary Harness overrides or exposes broad tools under a shared privileged role.



Validate and allowlist invocation inputs, restrict tools and credentials, and keep sensitive overrides behind the application boundary.


## Engineering review


- Distinguish Runtime and Harness.

- Review allowed tool defaults.

- Separate inbound and tool identity.

- Check cost and resource lifecycle.


## Further reading


- [AgentCore: Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html)

- [AgentCore: Harness vs Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-vs-runtime.html)

- [AgentCore: managed Harness](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness.html)

- [AgentCore: Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)

- [AgentCore: Harness security](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-security.html)

- [AgentCore: Harness tools](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-tools.html)
