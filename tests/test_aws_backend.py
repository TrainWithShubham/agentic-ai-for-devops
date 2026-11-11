import dataclasses

import boto3
import pytest
from moto import mock_aws

pytest.importorskip("langgraph_checkpoint_aws")

from runbookops.agent import Engine
from runbookops.security import Denied, principal


@pytest.mark.asyncio
async def test_dynamodb_checkpoint_and_approval_across_engines(settings, monkeypatch):
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    with mock_aws():
        ddb = boto3.client("dynamodb", region_name="us-east-1")
        ddb.create_table(
            TableName="gada-operations-test",
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        )
        ddb.create_table(
            TableName="gada-checkpoints-test",
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
        )
        cloud = dataclasses.replace(
            settings, dynamodb_table="gada-operations-test", checkpoint_table="gada-checkpoints-test"
        )
        engine = Engine(cloud)
        state = await engine.start(principal("bagha"), "Investigate checkout and prepare the correction.")
        assert state["waiting_for_approval"]
        p = state["proposal"]
        with pytest.raises(Denied):
            engine.store.apply(p["id"], principal("bagha"))
        engine.close()
        engine = Engine(cloud)
        done = await engine.decide(p["id"], principal("jethalal"), p["hash"], True)
        assert done["health"]["http_status"] == 200
        assert done["health"]["revision"] == 2
        assert engine.store.apply(p["id"], principal("bagha"))["idempotent_replay"]
        assert any(
            e["kind"] == "verification" for e in engine.store.events(state["incident_id"], principal("bagha"))
        )
        engine.close()
