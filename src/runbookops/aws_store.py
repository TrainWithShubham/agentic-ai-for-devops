"""DynamoDB simulator state for the instructor deployment.

Each incident is one bounded aggregate. Conditional writes serialize approvals and
configuration changes without placing a database server in the course setup.
"""

import copy
import json
import os
import time
import uuid

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.config import Config

from .security import Denied, InvalidChange, redact, require
from .store import BAD_URL, GOOD_URL, canonical, digest


class DynamoStore:
    def __init__(self, settings):
        session = boto3.Session(region_name=os.getenv("AWS_REGION", "us-east-1"))
        self.table = session.resource(
            "dynamodb",
            config=Config(
                retries={"total_max_attempts": 3, "mode": "adaptive"},
                connect_timeout=5,
                read_timeout=15,
            ),
        ).Table(settings.dynamodb_table)

    def close(self):
        self.table.meta.client.close()

    def _read(self, incident, actor):
        require(actor, "read")
        item = self.table.get_item(Key={"pk": incident}, ConsistentRead=True).get("Item")
        if not item:
            raise Denied("Incident not found or not accessible")
        data = json.loads(item["data"])
        if data["owner"] != actor.user and actor.role != "approver":
            raise Denied("Incident not found or not accessible")
        return data, int(item["version"])

    def _mutate(self, incident, actor, operation):
        for _ in range(8):
            data, version = self._read(incident, actor)
            result = operation(data)
            encoded = canonical(data)
            if len(encoded.encode()) > 300000:
                raise InvalidChange(
                    "Incident data limit reached; export evidence and start a new lab incident"
                )
            try:
                self.table.put_item(
                    Item={
                        "pk": incident,
                        "data": encoded,
                        "version": version + 1,
                        "ttl": int(time.time()) + 7 * 86400,
                    },
                    ConditionExpression=Attr("version").eq(version),
                )
                return copy.deepcopy(result)
            except self.table.meta.client.exceptions.ConditionalCheckFailedException:
                continue
        raise InvalidChange("Concurrent incident update; retry the request")

    def create_incident(self, actor):
        require(actor, "investigate")
        incident = "gada-" + uuid.uuid4().hex[:12]
        data = {
            "id": incident,
            "owner": actor.user,
            "config": {"PAYMENT_SERVICE_URL": BAD_URL},
            "revision": 1,
            "proposals": {},
            "events": [],
        }
        self.table.put_item(
            Item={"pk": incident, "data": canonical(data), "version": 1, "ttl": int(time.time()) + 7 * 86400},
            ConditionExpression=Attr("pk").not_exists(),
        )
        self.event(incident, "incident_created", actor=actor.user)
        return self.incident(incident, actor)

    def incident(self, incident, actor):
        data, _ = self._read(incident, actor)
        return {key: data[key] for key in ("id", "owner", "config", "revision")}

    def health(self, incident, actor):
        data = self.incident(incident, actor)
        healthy = data["config"]["PAYMENT_SERVICE_URL"] == GOOD_URL
        return {
            "service": "checkout",
            "status": "healthy" if healthy else "unhealthy",
            "http_status": 200 if healthy else 503,
            "revision": data["revision"],
        }

    def prepare(self, incident, actor, service, key, value, evidence):
        require(actor, "investigate")
        if (service, key, value) != ("checkout", "PAYMENT_SERVICE_URL", GOOD_URL):
            raise InvalidChange("Change outside simulator allowlist")
        if (
            not evidence
            or len(evidence) > 12
            or any(not isinstance(item, str) or len(item) > 180 for item in evidence)
        ):
            raise InvalidChange("Supply bounded evidence references")
        proposal_id = "proposal:" + incident + ":" + uuid.uuid4().hex[:10]

        def operation(data):
            for previous in data["proposals"].values():
                if previous["status"] in ("pending", "approved"):
                    if previous["expires"] < time.time():
                        previous["status"] = "expired"
                    else:
                        return previous
            if data["config"][key] == value:
                raise InvalidChange("The service already has this setting")
            plan = {
                "service": service,
                "environment": "simulator",
                "key": key,
                "before": data["config"][key],
                "after": value,
                "evidence": evidence,
                "risk": "Checkout requests may fail during the configuration reload.",
                "validation": "Check checkout returns HTTP 200 after the change.",
                "rollback": {"key": key, "value": data["config"][key]},
            }
            proposal = {
                "id": proposal_id,
                "incident": incident,
                "owner": actor.user,
                "plan": plan,
                "hash": digest(plan),
                "revision": data["revision"],
                "expires": time.time() + 900,
                "status": "pending",
                "approver": None,
                "approved_hash": None,
            }
            data["proposals"][proposal_id] = proposal
            return proposal

        result = self._mutate(incident, actor, operation)
        self.event(incident, "proposal_prepared", proposal_id=result["id"], hash=result["hash"])
        return result

    def _proposal_incident(self, proposal_id):
        parts = proposal_id.split(":")
        if len(parts) != 3 or parts[0] != "proposal" or not parts[1].startswith("gada-"):
            raise Denied("Proposal not found")
        return parts[1]

    def proposal(self, proposal_id, actor):
        data, _ = self._read(self._proposal_incident(proposal_id), actor)
        proposal = data["proposals"].get(proposal_id)
        if not proposal:
            raise Denied("Proposal not found")
        return proposal

    def _validate(self, proposal, data, expected_hash):
        if proposal["expires"] <= time.time():
            raise InvalidChange("Approval expired")
        if digest(proposal["plan"]) != proposal["hash"] or expected_hash != proposal["hash"]:
            raise InvalidChange("Proposal hash changed")
        if (
            data["revision"] != proposal["revision"]
            or data["config"][proposal["plan"]["key"]] != proposal["plan"]["before"]
        ):
            raise InvalidChange("Service changed; investigate again")

    def decide(self, proposal_id, actor, expected_hash, approve):
        require(actor, "approve")
        incident = self._proposal_incident(proposal_id)

        def operation(data):
            proposal = data["proposals"].get(proposal_id)
            if not proposal or proposal["status"] != "pending":
                raise InvalidChange("Proposal already decided or missing; replay rejected")
            self._validate(proposal, data, expected_hash)
            proposal.update(
                status="approved" if approve else "rejected", approver=actor.user, approved_hash=expected_hash
            )
            return proposal

        result = self._mutate(incident, actor, operation)
        self.event(
            incident, "approval_decision", proposal_id=proposal_id, actor=actor.user, status=result["status"]
        )
        return result

    def apply(self, proposal_id, actor):
        require(actor, "investigate")
        incident = self._proposal_incident(proposal_id)

        def operation(data):
            proposal = data["proposals"].get(proposal_id)
            if not proposal:
                raise Denied("Proposal not found")
            if proposal["status"] == "applied":
                return {"applied": False, "idempotent_replay": True}
            if proposal["status"] != "approved" or proposal["approver"] != "jethalal":
                raise Denied("Authorized stored approval required")
            self._validate(proposal, data, proposal["approved_hash"])
            plan = proposal["plan"]
            if (plan["service"], plan["key"], plan["after"]) != ("checkout", "PAYMENT_SERVICE_URL", GOOD_URL):
                raise InvalidChange("Change outside executor allowlist")
            data["config"][plan["key"]] = plan["after"]
            data["revision"] += 1
            proposal["status"] = "applied"
            return {"applied": True}

        result = self._mutate(incident, actor, operation)
        result["health"] = self.health(incident, actor)
        self.event(
            incident, "change_applied" if result["applied"] else "execution_replay", proposal_id=proposal_id
        )
        return result

    def event(self, incident, kind, **values):
        # The simulator has three fixed course identities. System events use its approver context.
        from .security import principal

        actor = principal("jethalal")
        event = {"at": time.time(), **redact({"kind": kind, **values})}
        if os.getenv("RUNBOOKOPS_LOG_EVENTS") == "true":
            print(canonical({"incident_id": incident, **event}), flush=True)

        def operation(data):
            data["events"].append(event)

        self._mutate(incident, actor, operation)

    def events(self, incident, actor):
        data, _ = self._read(incident, actor)
        return data["events"]
