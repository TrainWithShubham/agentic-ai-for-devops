"""Incident state and approval transactions for the simulator."""

import hashlib
import json
import os
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager

from .security import Denied, InvalidChange, require

BAD_URL = "http://payments:9009"
GOOD_URL = "http://payments:9000"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class Store:
    def __init__(self, settings):
        self.lock = threading.RLock()
        self.postgres = bool(settings.database_url)
        if self.postgres:
            import psycopg
            from psycopg.rows import dict_row

            self.db = psycopg.connect(settings.database_url, row_factory=dict_row, autocommit=True)
        else:
            self.db = sqlite3.connect(
                settings.data / "operations.sqlite", check_same_thread=False, isolation_level=None
            )
            self.db.row_factory = sqlite3.Row
            self.db.execute("PRAGMA journal_mode=WAL")
            self.db.execute("PRAGMA busy_timeout=10000")
        for statement in (
            "CREATE TABLE IF NOT EXISTS incidents (id TEXT PRIMARY KEY, owner TEXT NOT NULL, config TEXT NOT NULL, revision INTEGER NOT NULL)",
            "CREATE TABLE IF NOT EXISTS proposals (id TEXT PRIMARY KEY, incident TEXT NOT NULL, owner TEXT NOT NULL, plan TEXT NOT NULL, hash TEXT NOT NULL, revision INTEGER NOT NULL, expires DOUBLE PRECISION NOT NULL, status TEXT NOT NULL, approver TEXT, approved_hash TEXT)",
            "CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, incident TEXT NOT NULL, at DOUBLE PRECISION NOT NULL, data TEXT NOT NULL)",
        ):
            self.execute(statement)

    def execute(self, sql, args=()):
        if self.postgres:
            sql = sql.replace("?", "%s")
        return self.db.execute(sql, args)

    @contextmanager
    def transaction(self):
        with self.lock:
            self.execute("BEGIN" if self.postgres else "BEGIN IMMEDIATE")
            try:
                yield
                self.execute("COMMIT")
            except BaseException:
                self.execute("ROLLBACK")
                raise

    def close(self):
        self.db.close()

    def create_incident(self, actor):
        require(actor, "investigate")
        incident = "gada-" + uuid.uuid4().hex[:12]
        with self.transaction():
            self.execute(
                "INSERT INTO incidents VALUES (?, ?, ?, ?)",
                (incident, actor.user, canonical({"PAYMENT_SERVICE_URL": BAD_URL}), 1),
            )
        self.event(incident, "incident_created", actor=actor.user)
        return self.incident(incident, actor)

    def incident(self, incident, actor):
        require(actor, "read")
        row = self.execute("SELECT * FROM incidents WHERE id=?", (incident,)).fetchone()
        if not row or (row["owner"] != actor.user and actor.role != "approver"):
            raise Denied("Incident not found or not accessible to this identity")
        result = dict(row)
        result["config"] = json.loads(result["config"])
        return result

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
        data = self.incident(incident, actor)
        if (service, key, value) != ("checkout", "PAYMENT_SERVICE_URL", GOOD_URL):
            raise InvalidChange("Only the documented checkout payment URL correction is allowed in this lab")
        if (
            not evidence
            or len(evidence) > 12
            or any(not isinstance(item, str) or len(item) > 180 for item in evidence)
        ):
            raise InvalidChange("Supply bounded source references for the proposal")
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
        proposal_id = "proposal-" + uuid.uuid4().hex[:12]
        with self.transaction():
            self.execute(
                "UPDATE proposals SET status='expired' WHERE incident=? AND expires<=? AND status IN ('pending','approved')",
                (incident, time.time()),
            )
            existing = self.execute(
                "SELECT id FROM proposals WHERE incident=? AND status IN ('pending','approved')", (incident,)
            ).fetchone()
            if existing:
                return self.proposal(existing["id"], actor)
            self.execute(
                "INSERT INTO proposals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    proposal_id,
                    incident,
                    actor.user,
                    canonical(plan),
                    digest(plan),
                    data["revision"],
                    time.time() + 900,
                    "pending",
                    None,
                    None,
                ),
            )
        self.event(incident, "proposal_prepared", proposal_id=proposal_id, hash=digest(plan))
        return self.proposal(proposal_id, actor)

    def proposal(self, proposal_id, actor):
        row = self.execute("SELECT * FROM proposals WHERE id=?", (proposal_id,)).fetchone()
        if not row:
            raise Denied("Proposal not found")
        self.incident(row["incident"], actor)
        result = dict(row)
        result["plan"] = json.loads(result["plan"])
        return result

    def decide(self, proposal_id, actor, expected_hash, approve):
        require(actor, "approve")
        with self.transaction():
            proposal = self.proposal(proposal_id, actor)
            if self.postgres:
                self.execute("SELECT id FROM proposals WHERE id=? FOR UPDATE", (proposal_id,)).fetchone()
                proposal = self.proposal(proposal_id, actor)
            if proposal["status"] != "pending":
                raise InvalidChange("This proposal already has a decision; replay rejected")
            self._validate(proposal, actor, expected_hash)
            status = "approved" if approve else "rejected"
            self.execute(
                "UPDATE proposals SET status=?, approver=?, approved_hash=? WHERE id=?",
                (status, actor.user, expected_hash, proposal_id),
            )
        self.event(
            proposal["incident"],
            "approval_decision",
            proposal_id=proposal_id,
            actor=actor.user,
            status=status,
        )
        return self.proposal(proposal_id, actor)

    def _validate(self, proposal, actor, expected_hash):
        if proposal["expires"] <= time.time():
            raise InvalidChange("Approval expired; prepare a new proposal")
        if digest(proposal["plan"]) != proposal["hash"] or expected_hash != proposal["hash"]:
            raise InvalidChange("Proposal changed; approval must match the exact hash")
        current = self.incident(proposal["incident"], actor)
        if (
            current["revision"] != proposal["revision"]
            or current["config"].get(proposal["plan"]["key"]) != proposal["plan"]["before"]
        ):
            raise InvalidChange("Service state changed; investigate and propose again")

    def apply(self, proposal_id, actor):
        # Executor identity is supplied by the application, not by model arguments.
        require(actor, "investigate")
        with self.transaction():
            proposal = self.proposal(proposal_id, actor)
            if self.postgres:
                self.execute("SELECT id FROM proposals WHERE id=? FOR UPDATE", (proposal_id,)).fetchone()
                proposal = self.proposal(proposal_id, actor)
            if proposal["status"] == "applied":
                return {
                    "applied": False,
                    "idempotent_replay": True,
                    "health": self.health(proposal["incident"], actor),
                }
            if proposal["status"] != "approved" or proposal["approver"] != "jethalal":
                raise Denied("An authorized approval is required before execution")
            self._validate(proposal, actor, proposal["approved_hash"])
            plan = proposal["plan"]
            if (plan["service"], plan["key"], plan["after"]) != ("checkout", "PAYMENT_SERVICE_URL", GOOD_URL):
                raise InvalidChange("Change outside executor allowlist")
            current = self.incident(proposal["incident"], actor)
            current["config"][plan["key"]] = plan["after"]
            updated = self.execute(
                "UPDATE incidents SET config=?, revision=revision+1 WHERE id=? AND revision=?",
                (canonical(current["config"]), proposal["incident"], proposal["revision"]),
            )
            if updated.rowcount != 1:
                raise InvalidChange("Concurrent configuration change; execution stopped")
            self.execute("UPDATE proposals SET status='applied' WHERE id=?", (proposal_id,))
        self.event(
            proposal["incident"], "change_applied", proposal_id=proposal_id, approver=proposal["approver"]
        )
        return {"applied": True, "health": self.health(proposal["incident"], actor)}

    def event(self, incident, kind, **data):
        from .security import redact

        event = redact({"kind": kind, **data})
        if os.getenv("RUNBOOKOPS_LOG_EVENTS") == "true":
            print(canonical({"incident_id": incident, **event}), flush=True)
        with self.lock:
            self.execute(
                "INSERT INTO events VALUES (?, ?, ?, ?)",
                (uuid.uuid4().hex, incident, time.time(), canonical(event)),
            )

    def events(self, incident, actor):
        self.incident(incident, actor)
        return [
            {"at": row["at"], **json.loads(row["data"])}
            for row in self.execute(
                "SELECT * FROM events WHERE incident=? ORDER BY at,id", (incident,)
            ).fetchall()
        ]


def open_store(settings):
    if settings.dynamodb_table:
        from .aws_store import DynamoStore

        return DynamoStore(settings)
    return Store(settings)
