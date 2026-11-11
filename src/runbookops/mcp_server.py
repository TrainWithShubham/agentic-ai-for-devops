"""MCP transport for the same operational tools used by RunbookOps."""

from fastmcp import FastMCP

from .auth import Auth
from .config import Settings
from .rag import Retriever
from .security import principal
from .store import open_store
from .tools import Tools


def create_server(settings, local_actor=None):
    store = open_store(settings)
    retriever = Retriever(settings)
    sessions = {}
    auth = None
    if local_actor is None:
        from fastmcp.server.auth.providers.jwt import JWTVerifier

        issuer = Auth(settings)
        auth = JWTVerifier(
            public_key=issuer.public or None,
            jwks_uri=issuer.jwks if issuer.external and not issuer.public else None,
            issuer=issuer.issuer,
            audience=issuer.audience,
            algorithm="RS256",
            required_scopes=["read"],
        )
    server = FastMCP("Gada Electronics operations", auth=auth)

    def context(incident_id):
        if local_actor is not None:
            actor = local_actor
        else:
            from fastmcp.server.dependencies import get_access_token

            token = get_access_token()
            actor = principal(token.claims.get("sub", ""), token.scopes)
        store.incident(incident_id, actor)
        key = (actor.user, tuple(sorted(actor.scopes)), incident_id)
        if key not in sessions:
            sessions[key] = Tools(store, retriever, actor, incident_id)
        return sessions[key]

    @server.tool
    def get_service_health(incident_id: str, service: str) -> dict:
        """Read current checkout simulator health for an authorized incident."""
        return context(incident_id).call("get_service_health", {"service": service})

    @server.tool
    def get_recent_logs(incident_id: str, service: str) -> dict:
        """Read bounded and sanitized checkout logs."""
        return context(incident_id).call("get_recent_logs", {"service": service})

    @server.tool
    def get_recent_deployments(incident_id: str, service: str) -> dict:
        """Inspect the configuration change in the most recent deployment."""
        return context(incident_id).call("get_recent_deployments", {"service": service})

    @server.tool
    def search_runbooks(incident_id: str, query: str) -> dict:
        """Retrieve authorized current company documents with source locations."""
        return context(incident_id).call("search_runbooks", {"query": query})

    @server.tool
    def prepare_change(incident_id: str, service: str, key: str, value: str, evidence: list[str]) -> dict:
        """Prepare an evidenced change proposal without approving or executing it."""
        return context(incident_id).call(
            "prepare_change", {"service": service, "key": key, "value": value, "evidence": evidence}
        )

    return server, store


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--actor", choices=["bagha", "nattu", "jethalal"], default="bagha")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    settings = Settings.load()
    actor = principal(args.actor) if args.transport == "stdio" else None
    server, store = create_server(settings, actor)
    try:
        if args.transport == "stdio":
            server.run(transport="stdio", show_banner=False)
        else:
            server.run(transport="http", host="127.0.0.1", port=args.port, show_banner=False)
    finally:
        store.close()


if __name__ == "__main__":
    main()
