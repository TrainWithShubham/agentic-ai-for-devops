"""Local HTTP API and AgentCore-compatible HTTP entrypoint."""

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field

from .agent import Engine
from .auth import Auth
from .config import Settings
from .security import Denied, InvalidChange, require


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=1200)


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    approve: bool


class Invocation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: str = Field(pattern="^(investigate|status|decide|resume)$")
    question: str = Field(
        default="Investigate checkout HTTP 503 and prepare the documented correction.", max_length=1200
    )
    incident_id: str | None = None
    proposal_id: str | None = None
    expected_hash: str | None = None
    approve: bool = False


def create_app(settings=None):
    settings = settings or Settings.load()
    engine = Engine(settings)
    auth = Auth(settings)

    @asynccontextmanager
    async def lifespan(app):
        yield
        engine.close()

    app = FastAPI(title="RunbookOps", version="2.0.0", lifespan=lifespan)
    app.state.engine = engine
    app.state.auth = auth
    bearer = HTTPBearer(auto_error=False)

    def caller(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
        workshop_token: str | None = Header(default=None, alias="X-RunbookOps-Token"),
    ):
        token = credentials.credentials if credentials else None
        if os.getenv("RUNBOOKOPS_CLOUD") == "true" and not token:
            token = workshop_token
        if not token:
            raise HTTPException(401, "Bearer access token required", headers={"WWW-Authenticate": "Bearer"})
        try:
            return auth.verify(token)
        except Denied:
            raise HTTPException(
                401, "Invalid or expired access token", headers={"WWW-Authenticate": "Bearer"}
            ) from None

    @app.exception_handler(Denied)
    async def denied(request, error):
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=403, content={"detail": str(error)})

    @app.exception_handler(InvalidChange)
    async def invalid(request, error):
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=409, content={"detail": str(error)})

    @app.get("/ping")
    @app.get("/health")
    def health():
        return {"status": "Healthy", "mode": settings.mode}

    @app.get("/oidc/.well-known/openid-configuration")
    def discovery():
        if auth.external:
            raise HTTPException(404, "Use the configured external issuer")
        return {
            "issuer": auth.issuer,
            "jwks_uri": auth.issuer + "/jwks.json",
            "id_token_signing_alg_values_supported": ["RS256"],
            "description": "Development token issuer. No production authorization or consent flow.",
        }

    @app.get("/oidc/jwks.json")
    def jwks():
        if auth.external:
            raise HTTPException(404, "Use the configured external issuer")
        return auth.jwks_document()

    @app.get("/me")
    def me(actor=Depends(caller)):
        return {"user": actor.user, "role": actor.role, "scopes": sorted(actor.scopes)}

    @app.post("/investigations")
    async def start(body: Question, actor=Depends(caller)):
        return await engine.start(actor, body.question)

    @app.get("/incidents/{incident_id}")
    async def status(incident_id: str, actor=Depends(caller)):
        return await engine.status(incident_id, actor)

    @app.get("/incidents/{incident_id}/trace")
    def trace(incident_id: str, actor=Depends(caller)):
        return {"incident_id": incident_id, "events": engine.store.events(incident_id, actor)}

    @app.post("/proposals/{proposal_id}/decision")
    async def decide(proposal_id: str, body: Decision, actor=Depends(caller)):
        return await engine.decide(proposal_id, actor, body.expected_hash, body.approve)

    @app.post("/incidents/{incident_id}/resume")
    async def resume(incident_id: str, actor=Depends(caller)):
        return await engine.resume(incident_id, actor)

    @app.post("/invocations")
    async def invoke(body: Invocation, actor=Depends(caller)):
        # App JWT validation remains active behind Runtime admission authentication.
        if body.operation == "investigate":
            return await engine.start(actor, body.question)
        if body.operation == "status" and body.incident_id:
            return await engine.status(body.incident_id, actor)
        if body.operation == "resume" and body.incident_id:
            return await engine.resume(body.incident_id, actor)
        if body.operation == "decide" and body.proposal_id and body.expected_hash:
            require(actor, "approve")
            return await engine.decide(body.proposal_id, actor, body.expected_hash, body.approve)
        raise HTTPException(422, "Operation is missing its required identifiers or hash")

    from .ui import install_ui

    install_ui(app, settings, engine, auth, caller)
    return app


def app_factory():
    if os.getenv("RUNBOOKOPS_CLOUD") == "true":
        if not (
            os.getenv("RUNBOOKOPS_DATABASE_URL")
            or (os.getenv("RUNBOOKOPS_DYNAMODB_TABLE") and os.getenv("RUNBOOKOPS_CHECKPOINT_TABLE"))
        ) or not os.getenv("RUNBOOKOPS_OIDC_ISSUER"):
            raise RuntimeError("Cloud mode requires external database and issuer configuration")
    return create_app()
