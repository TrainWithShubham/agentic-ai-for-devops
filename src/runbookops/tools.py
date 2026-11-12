"""The agent sees only these bounded operational capabilities."""

import time

from .security import InvalidChange, redact, require
from .store import BAD_URL


def schema(name, description, properties, required):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
                "additionalProperties": False,
            },
        },
    }


MAX_TOOL_STEPS = 16

SERVICE = {"type": "string", "enum": ["checkout"]}
SCHEMAS = [
    schema(
        "get_service_health",
        "Read checkout HTTP health. Never changes state.",
        {"service": SERVICE},
        ["service"],
    ),
    schema("get_recent_logs", "Read bounded recent checkout logs.", {"service": SERVICE}, ["service"]),
    schema(
        "get_recent_deployments",
        "Read the latest checkout deployment and configuration change.",
        {"service": SERVICE},
        ["service"],
    ),
    schema(
        "search_runbooks",
        "Retrieve authorized current company documents. Cite the returned source IDs.",
        {"query": {"type": "string", "minLength": 1, "maxLength": 1200}},
        ["query"],
    ),
    schema(
        "prepare_change",
        "Prepare the documented simulator correction. Does not execute or approve anything.",
        {
            "service": SERVICE,
            "key": {"type": "string", "enum": ["PAYMENT_SERVICE_URL"]},
            "value": {"type": "string", "enum": ["http://payments:9000"]},
            "evidence": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "checkout-runbook",
                        "architecture",
                        "incident-042",
                        "change-policy",
                        "support-notes",
                        "get_service_health",
                        "get_recent_logs",
                        "get_recent_deployments",
                    ],
                },
                "minItems": 1,
                "maxItems": 12,
            },
        },
        ["service", "key", "value", "evidence"],
    ),
]


class Tools:
    def __init__(self, store, retriever, actor, incident):
        self.store, self.retriever, self.actor, self.incident = store, retriever, actor, incident
        self.sources = set()
        self.observed = set()
        self.proposal_id = None
        self.steps = 0

    def call(self, name, arguments):
        require(self.actor, "read")
        self.steps += 1
        if self.steps > MAX_TOOL_STEPS:
            raise InvalidChange("Tool step budget exceeded")
        definition = next((s["function"] for s in SCHEMAS if s["function"]["name"] == name), None)
        if definition is None:
            raise InvalidChange("Tool is not in the read/propose allowlist")
        import jsonschema

        jsonschema.validate(arguments, definition["parameters"])
        start = time.monotonic()
        self.store.incident(self.incident, self.actor)
        if name == "get_service_health":
            result = self.store.health(self.incident, self.actor)
            self.observed.add(name)
        elif name == "get_recent_logs":
            health = self.store.health(self.incident, self.actor)
            result = {
                "lines": ["checkout request succeeded HTTP 200"]
                if health["http_status"] == 200
                else [
                    "checkout HTTP 503: payment connection refused",
                    f"upstream={BAD_URL} connection refused; began after deployment deploy-108",
                    "synthetic API_KEY=sk-test-workshop-secret-only never forward secrets",
                ]
            }
            self.observed.add(name)
        elif name == "get_recent_deployments":
            result = {
                "deployment": "deploy-108",
                "service": "checkout",
                "change": {"key": "PAYMENT_SERVICE_URL", "before": "http://payments:9000", "after": BAD_URL},
            }
            self.observed.add(name)
        elif name == "search_runbooks":
            result = self.retriever.search(arguments["query"], self.actor)
            self.sources.update(item["source"] for item in result["results"])
        else:
            require(self.actor, "investigate")
            if not {"get_service_health", "get_recent_logs", "get_recent_deployments"}.issubset(
                self.observed
            ):
                raise InvalidChange("Inspect health, logs, and deployment evidence before proposing a fix")
            if "checkout-runbook" not in self.sources:
                raise InvalidChange("Retrieve the current checkout runbook before proposing a fix")
            if not set(arguments["evidence"]).issubset(self.sources | self.observed):
                raise InvalidChange("Proposal references evidence not retrieved in this investigation")
            result = self.store.prepare(self.incident, self.actor, **arguments)
            self.proposal_id = result["id"]
        result = redact(result)
        self.store.event(
            self.incident,
            "tool",
            tool=name,
            arguments=arguments,
            result=result,
            duration_ms=round((time.monotonic() - start) * 1000),
        )
        return result
