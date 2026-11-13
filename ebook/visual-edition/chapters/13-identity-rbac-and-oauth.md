# Identity, RBAC and OAuth


04 / Control and approval


## In everyday words

Authentication checks who is asking. Authorization checks what that person or service may do.


## Picture it

An office badge identifies you. It does not open every room in the building.

A role written in a chat message is not a trusted identity.



**OIDC.** An identity layer built on OAuth 2.0.


**OAuth.** A framework for delegated access.


**RBAC.** Permissions assigned through roles.


## Separate the identities in the path

Keep user identity, application rules and tool credentials separate.


### Diagram reading order


1. **User + identity provider:** Login establishes the user identity.

2. **Application API:** Checks the access token and resource policy.

3. **Agent execution:** Uses trusted caller context.

4. **Downstream tool:** Uses a credential meant for that service.



Validate token issuer, audience, expiry and integrity. An ID token is not a general API credential. Browser flows need current authorization-code/PKCE guidance.


## Read, propose or approve?

In this fictional policy, an engineer can propose; a release manager can approve.



1. **Read:** Check access to this project and run.

2. **Propose:** Prepare the patch without write permission.

3. **Approve:** Check the reviewer and target resource.

4. **Execute:** Use a scoped credential only when permitted.



Browser authorization flows should follow current authorization-code and PKCE guidance.


## Failure and correction

Trusting role=admin because the client sent it.



Use validated identity and server-side policy.


## Engineering review


- Deny by default.

- Check every protected request.

- Scope tokens.

- Do not pass tokens to unrelated services.


## Further reading


- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)

- [IETF: OAuth security / RFC 9700](https://www.rfc-editor.org/rfc/rfc9700)

- [OWASP: authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

- [MCP: security practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)
