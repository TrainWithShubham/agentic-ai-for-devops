# MCP without the mystery


02 / Agents and tools


## In everyday words

MCP is a protocol for connecting an AI application to capability servers. It gives them a shared way to describe and call tools.


## Picture it

A common socket makes connections easier. You still decide which device to trust and switch on.

MCP does not decide the goal or make a connected tool safe.



**Host.** The AI application.


**Client.** The part that talks to a server.


**Server.** The part exposing tools or context.


## A connection is not an agent

The application discovers tools, checks a chosen request and calls the server.


### Diagram reading order


1. **AI application:** Model interaction and access rules.

2. **MCP client:** Lists and calls capabilities.

3. **MCP server:** Exposes a CI-log tool.

4. **DevOps system:** The underlying API or data store.



MCP also supports resources and prompts. Local stdio and remote Streamable HTTP have different authorization needs. Match protocol versions.


## Discover, then call

These method names show the idea, not a full wire transcript.



1. **Discover:** tools/list describes available tools.

2. **Choose:** The model requests one; the host checks it.

3. **Call:** tools/call sends its name and arguments.

4. **Return:** The server sends the observed result.



MCP also supports resources and prompts. A listed tool is not proof it ran.


## Failure and correction

Calling any Python function "MCP" without a protocol exchange.



Show the client, server, transport and real request/result.


## Engineering review


- Inspect tools.

- Scope credentials.

- Check transport.

- Match versions.


## Further reading


- [MCP: architecture](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)

- [MCP: authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)

- [MCP: security practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)
