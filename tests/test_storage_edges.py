import dataclasses
import sqlite3
import time
from types import SimpleNamespace

import boto3
import pytest
from moto import mock_aws

from runbookops.aws_store import DynamoStore
from runbookops.security import Denied, InvalidChange, principal
from runbookops.store import GOOD_URL, Store, canonical, digest

BAGHA, OWNER = principal("bagha"), principal("jethalal")


@pytest.fixture(params=["sqlite", "dynamodb"])
def backend(request, settings):
    if request.param == "sqlite":
        store = Store(settings)
        yield store
        store.close()
    else:
        with mock_aws():
            client = boto3.client("dynamodb", region_name="us-east-1")
            client.create_table(
                TableName="coverage-state",
                BillingMode="PAY_PER_REQUEST",
                AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
                KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            )
            store = DynamoStore(dataclasses.replace(settings, dynamodb_table="coverage-state"))
            yield store
            store.close()


def make(store):
    incident = store.create_incident(BAGHA)["id"]
    p = store.prepare(incident, BAGHA, "checkout", "PAYMENT_SERVICE_URL", GOOD_URL, ["checkout-runbook"])
    return incident, p


def change(store, incident, proposal, **fields):
    if isinstance(store, DynamoStore):
        store._mutate(incident, OWNER, lambda data: data["proposals"][proposal].update(fields))
    else:
        for key, value in fields.items():
            store.execute(
                f"UPDATE proposals SET {key}=? WHERE id=?",
                (canonical(value) if key == "plan" else value, proposal),
            )


@pytest.mark.parametrize("evidence", [[], ["x"] * 13, [1], ["x" * 181]])
def test_evidence_bounds_on_both_backends(backend, evidence):
    incident = backend.create_incident(BAGHA)["id"]
    with pytest.raises(InvalidChange):
        backend.prepare(incident, BAGHA, "checkout", "PAYMENT_SERVICE_URL", GOOD_URL, evidence)
    with pytest.raises(InvalidChange):
        backend.prepare(incident, BAGHA, "checkout", "PAYMENT_SERVICE_URL", "http://evil", ["source"])
    assert backend.health(incident, BAGHA)["http_status"] == 503


def test_proposal_dedup_expiry_rejection_and_already_healthy(backend):
    incident, p = make(backend)
    assert (
        backend.prepare(incident, BAGHA, "checkout", "PAYMENT_SERVICE_URL", GOOD_URL, ["checkout-runbook"])[
            "id"
        ]
        == p["id"]
    )
    backend.decide(p["id"], OWNER, p["hash"], True)
    assert (
        backend.prepare(incident, BAGHA, "checkout", "PAYMENT_SERVICE_URL", GOOD_URL, ["checkout-runbook"])[
            "id"
        ]
        == p["id"]
    )
    change(backend, incident, p["id"], expires=time.time() - 1)
    p = backend.prepare(incident, BAGHA, "checkout", "PAYMENT_SERVICE_URL", GOOD_URL, ["checkout-runbook"])
    backend.decide(p["id"], OWNER, p["hash"], False)
    p = backend.prepare(incident, BAGHA, "checkout", "PAYMENT_SERVICE_URL", GOOD_URL, ["checkout-runbook"])
    backend.decide(p["id"], OWNER, p["hash"], True)
    backend.apply(p["id"], BAGHA)
    assert backend.apply(p["id"], BAGHA)["idempotent_replay"]
    with pytest.raises(InvalidChange, match="already has"):
        backend.prepare(incident, BAGHA, "checkout", "PAYMENT_SERVICE_URL", GOOD_URL, ["checkout-runbook"])


def test_missing_and_cross_identity_records_are_denied(backend):
    incident, p = make(backend)
    for who in [principal("nattu")]:
        with pytest.raises(Denied):
            backend.incident(incident, who)
    with pytest.raises(Denied):
        backend.incident("gada-missing", BAGHA)
    ids = [
        "missing",
        "proposal:gada-missing:x",
        "proposal:" + incident + ":missing",
        "wrong:" + incident + ":x",
        "proposal:wrong:x",
    ]
    for pid in ids:
        with pytest.raises(Denied):
            backend.proposal(pid, BAGHA)
    if isinstance(backend, DynamoStore):
        with pytest.raises(Denied):
            backend.apply("proposal:" + incident + ":missing", BAGHA)
        with pytest.raises(InvalidChange):
            backend.decide("proposal:" + incident + ":missing", OWNER, "0" * 64, True)


@pytest.mark.parametrize("fault", ["expired", "hash", "plan", "revision", "config"])
def test_invalid_stored_approval_does_not_apply(backend, fault):
    incident, p = make(backend)
    backend.decide(p["id"], OWNER, p["hash"], True)
    if fault == "expired":
        change(backend, incident, p["id"], expires=time.time() - 1)
    if fault == "hash":
        change(backend, incident, p["id"], approved_hash="0" * 64)
    if fault == "plan":
        change(backend, incident, p["id"], plan={**p["plan"], "after": "http://evil"})
    if fault in ("revision", "config"):
        if isinstance(backend, DynamoStore):
            backend._mutate(
                incident,
                OWNER,
                lambda d: (
                    d.update(revision=2)
                    if fault == "revision"
                    else d["config"].update(PAYMENT_SERVICE_URL="http://other")
                ),
            )
        else:
            if fault == "revision":
                backend.execute("UPDATE incidents SET revision=revision+1 WHERE id=?", (incident,))
            else:
                backend.execute(
                    "UPDATE incidents SET config=? WHERE id=?",
                    (canonical({"PAYMENT_SERVICE_URL": "http://other"}), incident),
                )
    with pytest.raises(InvalidChange):
        backend.apply(p["id"], BAGHA)
    assert backend.health(incident, BAGHA)["http_status"] == 503


def test_executor_validates_allowlist_and_approver_separately(backend):
    incident, p = make(backend)
    backend.decide(p["id"], OWNER, p["hash"], True)
    change(backend, incident, p["id"], approver="bagha")
    with pytest.raises(Denied):
        backend.apply(p["id"], BAGHA)
    plan = {**p["plan"], "after": "http://evil"}
    changed = digest(plan)
    change(backend, incident, p["id"], approver="jethalal", plan=plan, hash=changed, approved_hash=changed)
    with pytest.raises(InvalidChange, match="executor allowlist"):
        backend.apply(p["id"], BAGHA)
    assert backend.health(incident, BAGHA)["http_status"] == 503


def test_event_logging_redacts_secrets(backend, monkeypatch, capsys):
    incident = backend.create_incident(BAGHA)["id"]
    monkeypatch.setenv("RUNBOOKOPS_LOG_EVENTS", "true")
    backend.event(incident, "test", api_key="private-secret", note="safe")
    output = capsys.readouterr().out
    assert "private-secret" not in output and "safe" in output


@pytest.mark.parametrize("backend", ["dynamodb"], indirect=True)
def test_dynamo_conflicts_retry_and_bound_size(backend, monkeypatch):
    incident = backend.create_incident(BAGHA)["id"]
    original = backend.table.put_item
    error = backend.table.meta.client.exceptions.ConditionalCheckFailedException(
        {"Error": {"Code": "ConditionalCheckFailedException"}}, "PutItem"
    )
    calls = []

    def once(**kw):
        calls.append(kw)
        if len(calls) == 1:
            raise error
        return original(**kw)

    monkeypatch.setattr(backend.table, "put_item", once)
    backend.event(incident, "retry")
    assert len(calls) == 2 and backend.events(incident, BAGHA)[-1]["kind"] == "retry"

    def always(**kw):
        raise error

    monkeypatch.setattr(backend.table, "put_item", always)
    with pytest.raises(InvalidChange, match="Concurrent"):
        backend.event(incident, "blocked")
    with pytest.raises(InvalidChange, match="data limit"):
        backend._mutate(incident, OWNER, lambda d: d.update(oversize="x" * 300001))
    assert backend.events(incident, BAGHA)[-1]["kind"] == "retry"


def test_sql_concurrent_revision_rollback(settings, monkeypatch):
    store = Store(settings)
    incident, p = make(store)
    store.decide(p["id"], OWNER, p["hash"], True)
    execute = store.execute

    def conflict(sql, args=()):
        return (
            SimpleNamespace(rowcount=0)
            if sql.startswith("UPDATE incidents SET config")
            else execute(sql, args)
        )

    monkeypatch.setattr(store, "execute", conflict)
    with pytest.raises(InvalidChange, match="Concurrent"):
        store.apply(p["id"], BAGHA)
    assert store.health(incident, BAGHA)["revision"] == 1
    store.close()


def test_postgres_sql_adapter_and_lock_contract(settings, monkeypatch):
    import psycopg

    statements = []

    class Adapter:
        def __init__(self):
            self.db = sqlite3.connect(":memory:", isolation_level=None)
            self.db.row_factory = sqlite3.Row

        def execute(self, sql, args=()):
            statements.append(sql)
            return self.db.execute(sql.replace("%s", "?").replace(" FOR UPDATE", ""), args)

        def close(self):
            self.db.close()

    monkeypatch.setattr(psycopg, "connect", lambda dsn, **kw: Adapter())
    store = Store(dataclasses.replace(settings, database_url="postgresql://test-contract"))
    incident, p = make(store)
    store.decide(p["id"], OWNER, p["hash"], True)
    assert store.apply(p["id"], BAGHA)["health"]["http_status"] == 200
    assert any("FOR UPDATE" in sql for sql in statements)
    assert any("%s" in sql for sql in statements)
    store.close()
