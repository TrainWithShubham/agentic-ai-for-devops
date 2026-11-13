# MCP without the mystery


02 / Agents and tools


## How do applications connect to tools?

Model Context Protocol (MCP) standardizes exchanges between an AI application and capability servers. A host owns the user experience; its clients communicate with servers that expose tools and other context.



**Host.** The application coordinates model use and connections.


**Client.** A protocol participant communicates with an MCP server.


**Server.** Publishes capabilities such as tools, resources and prompts.


## A connection is not an agent

The host can obtain tool descriptions, present suitable schemas to the model, validate a chosen request and call the server. The protocol does not decide the investigation goal.


### Diagram reading order


1. **AI application:** Host + model interaction + policy checks.

2. **MCP client:** Lists capabilities and issues protocol calls.

3. **MCP server:** Exposes a bounded CI-log capability.

4. **DevOps system:** The underlying run store or API.



Local stdio uses process input/output. Remote Streamable HTTP has a different deployment and authorization surface. Match SDK and protocol versions.


## Discover, then request a tool

These method names illustrate the tool exchange; they are not a complete version-specific wire transcript.



1. **Discover:** tools/list returns names, descriptions and input schemas.

2. **Select:** The model requests one capability; the host checks the request.

3. **Call:** tools/call sends the name and arguments to the server.

4. **Return:** The server result is available to the host and subsequent model step.



MCP also supports resources and prompts. A tool catalog alone does not prove that a model used any tool.


## Failure and correction

A demo labels a direct Python function call "MCP" without a client/server exchange.



Show the actual transport and request/result boundary. Use separate names for the agent loop, protocol and server.


## Engineering review


- Identify host, client and server.

- Inspect schemas before granting use.

- Keep server credentials scoped.

- Verify supported protocol versions.


## Further reading


- [MCP: architecture](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)

- [MCP: authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)

- [MCP: security practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)
