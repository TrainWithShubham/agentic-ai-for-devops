"""A bounded investigation followed by a persistent, externally authorized approval."""

import asyncio
import json
import os
import sys
from contextlib import asynccontextmanager
from typing import TypedDict

from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .mcp_server import create_server
from .models import SYSTEM, Model, ModelError
from .security import Denied, InvalidChange, redact, require
from .store import open_store
from .tools import MAX_TOOL_STEPS, SCHEMAS

INVESTIGATION_TIMEOUT = 150


class IncidentState(TypedDict, total=False):
    incident_id: str
    user: str
    question: str
    mode: str
    diagnosis: str
    proposal_id: str | None
    model_calls: int
    error: str | None
    result: dict


@asynccontextmanager
async def tool_client(settings, actor, transport):
    server_store = None
    if settings.mcp_url:
        if not settings.mcp_token:
            raise Denied("Remote MCP requires a caller access token")
        client = Client(settings.mcp_url, auth=settings.mcp_token)
    elif transport == "stdio":
        client = Client(
            PythonStdioTransport(
                settings.root / "scripts/mcp_entry.py",
                args=["--actor", actor.user],
                python_cmd=sys.executable,
                cwd=str(settings.root),
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "RUNBOOKOPS_ROOT": str(settings.root),
                    "RUNBOOKOPS_DATA": str(settings.data),
                    "RUNBOOKOPS_EMBEDDING": settings.embedding,
                    "RUNBOOKOPS_MODE": "offline",
                },
            )
        )
    else:
        server, server_store = create_server(settings, actor)
        client = Client(server)
    try:
        async with client:
            yield client
    finally:
        if server_store:
            server_store.close()


class Engine:
    def __init__(self, settings, transport="inprocess"):
        self.settings = settings
        self.store = open_store(settings)
        self.model = Model(settings)
        self.transport = transport

    def close(self):
        self.store.close()

    @asynccontextmanager
    async def graph(self, actor):
        async def investigate(state):
            self.store.event(state["incident_id"], "node_started", node="investigate")
            messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": state["question"]}]
            proposal_id = None
            calls = 0
            tool_steps = 0
            diagnosis = ""
            verified_reads = set()
            completion_reminded = False
            failure = None
            try:
                async with asyncio.timeout(INVESTIGATION_TIMEOUT):
                    async with tool_client(self.settings, actor, self.transport) as client:
                        discovered = {tool.name for tool in await client.list_tools()}
                        if not {t["function"]["name"] for t in SCHEMAS}.issubset(discovered):
                            raise ModelError("MCP server is missing a required workshop tool")
                        self.store.event(
                            state["incident_id"],
                            "mcp_connected",
                            transport="http" if self.settings.mcp_url else self.transport,
                            tools=sorted(discovered),
                        )
                        for _ in range(self.settings.max_calls):
                            self.store.event(
                                state["incident_id"],
                                "model_request",
                                turn=calls + 1,
                                message_count=len(messages),
                                tool_count=len(SCHEMAS),
                            )
                            message, metadata = await self.model.complete(messages, SCHEMAS)
                            calls += 1
                            self.store.event(
                                state["incident_id"],
                                "model",
                                **metadata,
                                turn=calls,
                                content=message.get("content") or "",
                                requested_tools=[
                                    {
                                        "name": call.get("function", {}).get("name", ""),
                                        "arguments": call.get("function", {}).get("arguments", ""),
                                    }
                                    for call in message.get("tool_calls") or []
                                ],
                            )
                            messages.append(message)
                            requests = message.get("tool_calls") or []
                            if not requests:
                                diagnosis = message.get("content") or "No diagnosis returned."
                                required_reads = {
                                    "get_service_health",
                                    "get_recent_logs",
                                    "get_recent_deployments",
                                    "search_runbooks",
                                }
                                if (
                                    verified_reads
                                    and not completion_reminded
                                    and (
                                        verified_reads != required_reads or "fix" in state["question"].lower()
                                    )
                                ):
                                    completion_reminded = True
                                    messages.append(
                                        {
                                            "role": "user",
                                            "content": (
                                                "Check completion against the original task. Finish any missing health, logs, "
                                                "deployment, and current-runbook checks using the provided tools. If the user "
                                                "requested a fix and the evidence supports it, call prepare_change to save the "
                                                "suggestion. That tool does not apply a change. If the current checkout-runbook "
                                                "source was not retrieved, search_runbooks with query: checkout runbook "
                                                "payment URL correction approval. Never invent source IDs. Otherwise explain the findings."
                                            ),
                                        }
                                    )
                                    continue
                                break
                            for call in requests:
                                tool_steps += 1
                                if tool_steps > MAX_TOOL_STEPS:
                                    raise ModelError("Tool step limit reached")
                                name = call.get("function", {}).get("name", "")
                                if name not in {t["function"]["name"] for t in SCHEMAS}:
                                    result = {"error": "Tool outside the investigation allowlist"}
                                else:
                                    try:
                                        arguments = json.loads(call["function"]["arguments"])
                                        import jsonschema

                                        spec = next(
                                            t["function"]["parameters"]
                                            for t in SCHEMAS
                                            if t["function"]["name"] == name
                                        )
                                        jsonschema.validate(arguments, spec)
                                        response = await client.call_tool(
                                            name,
                                            {**arguments, "incident_id": state["incident_id"]},
                                            timeout=20,
                                        )
                                        result = response.data
                                        if not isinstance(result, dict):
                                            raise ValueError("Tool returned an unexpected data shape")
                                        if name in {
                                            "get_service_health",
                                            "get_recent_logs",
                                            "get_recent_deployments",
                                            "search_runbooks",
                                        } and not result.get("error"):
                                            if name != "search_runbooks" or any(
                                                item.get("source") == "checkout-runbook"
                                                for item in result.get("results", [])
                                            ):
                                                verified_reads.add(name)
                                        if name == "prepare_change" and result.get("id"):
                                            proposal_id = result["id"]
                                    except Exception:
                                        result = {
                                            "error": f"{name} failed validation or execution; no unauthorized action was performed",
                                            "next_step": (
                                                "Verify health, logs and deployments; retrieve the current checkout-runbook "
                                                "using search_runbooks query 'checkout runbook payment URL correction approval'. "
                                                "Use only exact source IDs returned by the tools."
                                                if name == "prepare_change"
                                                else "Check the tool input schema and use only permitted arguments."
                                            ),
                                        }
                                        self.store.event(state["incident_id"], "tool_error", tool=name)
                                messages.append(
                                    {
                                        "role": "tool",
                                        "tool_call_id": call["id"],
                                        "content": json.dumps(redact(result)),
                                    }
                                )
                            if proposal_id:
                                proposal = self.store.proposal(proposal_id, actor)
                                plan = proposal["plan"]
                                diagnosis = (
                                    f"Validated tool evidence and the current checkout-runbook support restoring {plan['key']} "
                                    f"from {plan['before']} to {plan['after']}. Proposal {proposal_id} awaits Jethalal. "
                                    "This application summary is based on the validated proposal; no change has been applied."
                                )
                                break
                        else:
                            failure = "Model call budget reached; investigation stopped."
            except (TimeoutError, ModelError, OSError) as error:
                failure = (
                    str(error)
                    if isinstance(error, ModelError)
                    else "Investigation timed out or the provider connection failed."
                )
            self.store.event(
                state["incident_id"],
                "investigation_finished",
                mode=self.settings.mode,
                model_calls=calls,
                proposal_id=proposal_id,
                error=failure,
            )
            self.store.event(state["incident_id"], "node_completed", node="investigate")
            return {
                "diagnosis": redact(diagnosis),
                "proposal_id": proposal_id,
                "model_calls": calls,
                "error": failure,
            }

        def review(state):
            proposal = self.store.proposal(state["proposal_id"], actor)
            interrupt(
                {"message": "An authorized human must review this exact proposal.", "proposal": proposal}
            )
            # The resume payload cannot grant approval. Only a stored decision can.
            proposal = self.store.proposal(state["proposal_id"], actor)
            if proposal["status"] not in ("approved", "applied", "rejected"):
                raise Denied("Resume requires an authorized stored approval decision")
            return {"result": {"decision": proposal["status"]}}

        def execute(state):
            self.store.event(state["incident_id"], "node_started", node="execute")
            if state["result"]["decision"] == "rejected":
                result = {
                    "applied": False,
                    "status": "rejected",
                    "health": self.store.health(state["incident_id"], actor),
                }
            else:
                result = self.store.apply(state["proposal_id"], actor)
            self.store.event(state["incident_id"], "verification", result=result)
            self.store.event(state["incident_id"], "node_completed", node="execute")
            return {"result": result}

        builder = StateGraph(IncidentState)
        builder.add_node("investigate", investigate)
        builder.add_node("review", review)
        builder.add_node("execute", execute)
        builder.add_edge(START, "investigate")
        builder.add_conditional_edges(
            "investigate", lambda state: "review" if state.get("proposal_id") else END
        )
        builder.add_edge("review", "execute")
        builder.add_edge("execute", END)
        if self.settings.checkpoint_table:
            from botocore.config import Config
            from langgraph_checkpoint_aws import DynamoDBSaver

            saver = DynamoDBSaver(
                table_name=self.settings.checkpoint_table,
                region_name=os.getenv("AWS_REGION", "us-east-1"),
                ttl_seconds=7 * 86400,
                enable_checkpoint_compression=True,
                consistent_read=True,
                boto_config=Config(
                    retries={"total_max_attempts": 3, "mode": "adaptive"}, connect_timeout=5, read_timeout=20
                ),
            )
            yield builder.compile(checkpointer=saver)
        elif self.settings.database_url:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

            async with AsyncPostgresSaver.from_conn_string(self.settings.database_url) as saver:
                await saver.setup()
                yield builder.compile(checkpointer=saver)
        else:
            async with AsyncSqliteSaver.from_conn_string(
                str(self.settings.data / "checkpoints.sqlite")
            ) as saver:
                yield builder.compile(checkpointer=saver)

    def config(self, incident):
        return {"configurable": {"thread_id": incident}, "recursion_limit": 25}

    async def start(self, actor, question, on_created=None):
        require(actor, "investigate")
        if not 1 <= len(question) <= 1200:
            raise ValueError("Question must contain 1 to 1200 characters")
        question = redact(question)
        incident = self.store.create_incident(actor)["id"]
        if on_created:
            on_created(incident)
        async with self.graph(actor) as graph:
            await graph.ainvoke(
                {
                    "incident_id": incident,
                    "user": actor.user,
                    "question": question,
                    "mode": self.settings.mode,
                    "proposal_id": None,
                },
                self.config(incident),
            )
        return await self.status(incident, actor)

    async def status(self, incident, actor):
        self.store.incident(incident, actor)
        async with self.graph(actor) as graph:
            snapshot = await graph.aget_state(self.config(incident))
        values = dict(snapshot.values)
        values["waiting_for_approval"] = "review" in snapshot.next
        values["pending_nodes"] = list(snapshot.next)
        values["health"] = self.store.health(incident, actor)
        if values.get("proposal_id"):
            values["proposal"] = self.store.proposal(values["proposal_id"], actor)
        return redact(values)

    async def decide(self, proposal_id, actor, expected_hash, approve):
        try:
            proposal = self.store.decide(proposal_id, actor, expected_hash, approve)
        except Denied:
            try:
                visible = self.store.proposal(proposal_id, actor)
                self.store.event(visible["incident"], "approval_denied", actor=actor.user)
            except Denied:
                pass
            raise
        return await self.resume(proposal["incident"], actor)

    async def resume(self, incident, actor):
        require(actor, "approve")
        state = await self.status(incident, actor)
        if not state.get("proposal_id"):
            raise InvalidChange("This incident has no proposal")
        if state["proposal"]["status"] not in ("approved", "rejected", "applied"):
            raise Denied("A stored approval decision is required")
        if state["pending_nodes"]:
            async with self.graph(actor) as graph:
                input_value = (
                    Command(resume={"proposal_id": state["proposal_id"]})
                    if state["waiting_for_approval"]
                    else None
                )
                await graph.ainvoke(input_value, self.config(incident))
        return await self.status(incident, actor)
