# Bonus: Amazon Bedrock AgentCore


Bonus / AgentCore


## In everyday words

AgentCore Runtime hosts agent code you bring. Managed Harness supplies an agent loop you configure. Choose which layer you want managed.


## Picture it

Bring your own furniture to an empty office, or choose a furnished office. Both still need access rules.

The office picture compares responsibility; it is not a promise about pricing or service features.



**Runtime.** Host your LangGraph or custom agent.


**Managed Harness.** Use a supplied, Strands-powered loop.


**Other services.** Tools, identity, memory and observability.


## Hosting and orchestration are different

A custom LangGraph loop belongs on Runtime. Managed Harness is a separate approach.


### Diagram reading order


1. **Your loop:** Deploy custom code to Runtime.

2. **Managed loop:** Configure model, tools and limits.

3. **Tool connection:** Gateway can expose MCP-compatible tools.

4. **App boundary:** Your UI/API still needs approval and access rules.



Architecture only. Managed sessions do not replace approval records. Check tool defaults, invocation overrides, region, quotas and pricing before deployment.


## A private instructor demo

Keep AWS credentials on the trusted backend.



1. **Choose:** Custom Runtime code or managed Harness.

2. **Configure:** Scope roles, tools, models and limits.

3. **Observe:** Inspect real invocation events and saved state.

4. **Clean up:** Review dedicated runtime, logs and storage.



Managed sessions do not replace a durable approval record. Check allowed tool defaults and invocation overrides.


## Failure and correction

Forwarding arbitrary public inputs into a privileged Harness invocation.



Validate inputs, limit tools and protect credentials.


## Engineering review


- Runtime or Harness?

- Which tools?

- Which identity?

- Which costs and resources?


## Further reading


- [AgentCore: Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html)

- [AgentCore: Harness vs Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-vs-runtime.html)

- [AgentCore: managed Harness](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness.html)

- [AgentCore: Gateway](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)

- [AgentCore: Harness security](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-security.html)

- [AgentCore: Harness tools](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-tools.html)
