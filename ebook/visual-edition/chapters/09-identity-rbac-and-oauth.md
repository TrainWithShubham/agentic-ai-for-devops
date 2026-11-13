# Identity, RBAC and OAuth


04 / Control and approval


## Who is allowed to do what?

Identity establishes the caller. Authorization decides the allowed action on a resource. A user prompt saying "I am the admin" establishes neither.



**OIDC.** An identity layer on OAuth 2.0 for authenticating users.


**OAuth.** A framework for delegated authorization using tokens.


**RBAC.** Roles map to application permissions; resource checks still apply.


## Separate the identities in the path

The browser login, API access token and downstream tool credential serve different purposes. Avoid treating a token accepted by one service as valid everywhere.


### Diagram reading order


1. **User + identity provider:** A login flow establishes the user identity.

2. **Application API:** Validates the access token and enforces resource policy.

3. **Agent execution:** Uses the established caller context; the model cannot invent it.

4. **Downstream tool:** Uses a scoped credential intended for that service.



For a browser-based authorization flow, follow current authorization-code and PKCE guidance. An ID token is not a general API access credential.


## Engineer versus approver

In this fictional policy, engineers may inspect a CI failure and propose a patch; release managers may approve it.



1. **Read:** Check that the engineer may access this project and run.

2. **Propose:** Allow a bounded proposal without granting write access.

3. **Approve:** Check the reviewer role and the specific target resource.

4. **Execute:** Use the service credential only after policy permits the action.



Validate issuer, audience, expiry and token integrity as appropriate to the token and provider. Keep secrets out of prompts and traces.


## Failure and correction

The client sends role=release-manager, and the API trusts it because the field looks well formed.



Derive roles and permissions from validated identity and trusted server policy. Deny access by default.


## Engineering review


- Separate authentication and authorization.

- Check each protected request.

- Scope audience and permissions.

- Avoid token passthrough to another service.


## Further reading


- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)

- [IETF: OAuth security / RFC 9700](https://www.rfc-editor.org/rfc/rfc9700)

- [OWASP: authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

- [MCP: security practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)
