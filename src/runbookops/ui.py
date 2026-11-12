"""Same-origin workshop UI. Development persona issuance is explicit and loopback-only."""

import asyncio
import json
import os
from pathlib import Path
from typing import Literal

from fastapi import Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from .agent import INVESTIGATION_TIMEOUT, tool_client
from .models import SYSTEM
from .rag import CACHE_TTL, CHUNK_OVERLAP, CHUNK_SIZE, EMBEDDING_MODEL, Retriever, extract
from .security import Denied, redact, require
from .tools import MAX_TOOL_STEPS, SCHEMAS


class Persona(BaseModel):
    model_config = ConfigDict(extra="forbid")
    user: Literal["bagha", "nattu", "jethalal"]


class Investigation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=1200)


def install_ui(app, settings, engine, auth, caller):
    assets = Path(__file__).parent / "web"
    app.mount("/assets", StaticFiles(directory=assets), name="ui-assets")
    retriever = Retriever(settings)

    def demo_enabled():
        return settings.ui_demo_auth and not auth.external and os.getenv("RUNBOOKOPS_CLOUD") != "true"

    def sources(actor):
        require(actor, "read")
        _, manifest = retriever.fingerprint()
        return [s for s in manifest if s["current"] and s["access"] in ("public", actor.role)]

    def loopback(request):
        return (
            request.client is not None
            and request.client.host in ("127.0.0.1", "::1")
            and request.url.hostname in ("127.0.0.1", "localhost", "::1")
        )

    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(
            assets / "index.html",
            headers={
                "Cache-Control": "no-cache",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "no-referrer",
                "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; "
                "font-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; "
                "base-uri 'none'; form-action 'self'",
            },
        )

    @app.get("/ui/config", include_in_schema=False)
    def config(request: Request):
        return JSONResponse(
            {
                "mode": settings.mode,
                "embedding": settings.embedding,
                "model": engine.model.route("diagnose") or "Deterministic practice",
                "demo_auth": demo_enabled() and loopback(request),
                "max_calls": settings.max_calls,
            },
            headers={"Cache-Control": "no-store"},
        )

    @app.post("/ui/session", include_in_schema=False)
    def session(body: Persona, request: Request):
        if not demo_enabled():
            raise HTTPException(404, "Development persona login is disabled")
        # Reject proxies, remote clients, DNS rebinding hosts, and cross-origin browser requests.
        if not loopback(request) or request.headers.get("x-runbookops-demo") != "true":
            raise HTTPException(403, "Development login is available only on this computer")
        origin = request.headers.get("origin")
        if origin and origin != str(request.base_url).rstrip("/"):
            raise HTTPException(403, "Cross-origin development login is not allowed")
        token = auth.issue(body.user)
        actor = auth.verify(token)
        return JSONResponse(
            {
                "access_token": token,
                "expires_in": 600,
                "user": actor.user,
                "role": actor.role,
                "scopes": sorted(actor.scopes),
            },
            headers={"Cache-Control": "no-store"},
        )

    @app.get("/harness")
    async def harness(actor=Depends(caller)):
        require(actor, "read")
        async with engine.graph(actor) as graph:
            topology = graph.get_graph().to_json()
        return {
            "name": "RunbookOps",
            "framework": "LangGraph",
            "description": "Investigate the checkout simulator and prepare a correction for approval.",
            "system_prompt": SYSTEM,
            "routing": {
                task: engine.model.route(task) or "deterministic-fixture"
                for task in ("diagnose", "summarize")
            },
            "limits": {
                "model_calls": settings.max_calls,
                "tool_calls": MAX_TOOL_STEPS,
                "output_tokens": settings.max_tokens,
                "timeout_seconds": INVESTIGATION_TIMEOUT,
            },
            "tools": SCHEMAS,
            "graph": topology,
            "mcp": {"transport": "http" if settings.mcp_url else engine.transport},
            "rag": {
                "embedding": settings.embedding,
                "embedding_model": EMBEDDING_MODEL
                if settings.embedding == "semantic"
                else "lexical feature hashing",
                "chunk_characters": CHUNK_SIZE,
                "overlap_characters": CHUNK_OVERLAP,
                "cache_ttl_seconds": CACHE_TTL,
                "filters": ["current documents", "caller role", "read scope"],
                "cache_scope": ["user", "role", "scopes", "query", "corpus fingerprint", "result count"],
            },
            "checkpoint": "DynamoDB"
            if settings.checkpoint_table
            else "PostgreSQL"
            if settings.database_url
            else "SQLite",
            "free_only": settings.free_only,
            "permissions": {"user": actor.user, "role": actor.role, "scopes": sorted(actor.scopes)},
        }

    @app.get("/harness/mcp")
    async def mcp_discovery(actor=Depends(caller)):
        require(actor, "read")
        try:
            async with asyncio.timeout(15):
                async with tool_client(settings, actor, engine.transport) as client:
                    tools = await client.list_tools()
                    discovered = [
                        {"name": tool.name, "description": tool.description, "input_schema": tool.inputSchema}
                        for tool in tools
                    ]
        except Exception:
            raise HTTPException(
                503, "MCP discovery failed. Check the configured transport and identity."
            ) from None
        return {"transport": "http" if settings.mcp_url else engine.transport, "tools": discovered}

    @app.get("/knowledge")
    def knowledge(actor=Depends(caller)):
        return {"sources": sources(actor), "embedding": settings.embedding}

    @app.post("/knowledge/search")
    def search(body: Investigation, actor=Depends(caller)):
        return retriever.search(body.question, actor)

    @app.get("/knowledge/{source_id}")
    def source(source_id: str, actor=Depends(caller)):
        item = next((s for s in sources(actor) if s["id"] == source_id), None)
        if not item:
            raise Denied("Source not found or not accessible to this identity")
        return {
            **item,
            "sections": [
                {"location": location, "text": redact(text)}
                for location, text in extract(retriever.folder / item["file"])
            ],
        }

    @app.post("/investigations/stream")
    async def stream(body: Investigation, actor=Depends(caller)):
        require(actor, "investigate")

        async def events():
            incident = None
            offset = 0
            announced = False

            def created(value):
                nonlocal incident
                incident = value

            def line(kind, data):
                return json.dumps({"type": kind, "data": redact(data)}) + "\n"

            task = asyncio.create_task(engine.start(actor, body.question, on_created=created))
            try:
                yield line("connected", {"mode": settings.mode})
                while True:
                    await asyncio.wait({task}, timeout=0.4)
                    if incident:
                        if not announced:
                            yield line("incident", {"incident_id": incident})
                            announced = True
                        recorded = engine.store.events(incident, actor)
                        for item in recorded[offset:]:
                            yield line("event", item)
                        offset = len(recorded)
                    if task.done():
                        state = await task
                        yield line("complete", state)
                        break
            except Exception as error:
                yield line("error", {"message": str(error)})
            finally:
                if not task.done():
                    task.cancel()
                    await asyncio.gather(task, return_exceptions=True)
                    if incident:
                        engine.store.event(incident, "investigation_cancelled", actor=actor.user)

        return StreamingResponse(
            events(),
            media_type="application/x-ndjson",
            headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
        )
