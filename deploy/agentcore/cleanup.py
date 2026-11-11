"""Remove only resources named in this workshop's deployment record."""

import json
import time
from pathlib import Path

import boto3

ROOT = Path(__file__).resolve().parents[2]


def main():
    path = ROOT / ".state/aws-deployment.json"
    data = json.loads(path.read_text())
    if data.get("project") != "runbookops-v2" or not data.get("prefix", "").startswith("runbookops_v2_"):
        raise ValueError("Deployment record does not belong to this project")
    if data["repository"] != data["prefix"] or data["role"] != data["prefix"] + "_runtime":
        raise ValueError("Unexpected resource names in deployment record")
    if data.get("runtime_id") and not data["runtime_id"].startswith(data["prefix"] + "-"):
        raise ValueError("Unexpected runtime in deployment record")
    session = boto3.Session(region_name=data["region"])
    if session.client("sts").get_caller_identity()["Account"] != data["account"]:
        raise ValueError("Current AWS account differs from the deployment record")
    control = session.client("bedrock-agentcore-control")
    if data.get("runtime_id"):
        try:
            current = control.get_agent_runtime(agentRuntimeId=data["runtime_id"])
        except control.exceptions.ResourceNotFoundException:
            current = None
        if current and current["status"] != "DELETING":
            endpoints = control.list_agent_runtime_endpoints(agentRuntimeId=data["runtime_id"])
            for endpoint in endpoints["runtimeEndpoints"]:
                if endpoint["name"] == "DEFAULT" or endpoint["status"] == "DELETING":
                    continue
                control.delete_agent_runtime_endpoint(
                    agentRuntimeId=data["runtime_id"], endpointName=endpoint["name"]
                )
            for _ in range(120):
                endpoints = control.list_agent_runtime_endpoints(agentRuntimeId=data["runtime_id"])
                if not any(e["name"] != "DEFAULT" for e in endpoints["runtimeEndpoints"]):
                    break
                time.sleep(3)
            else:
                raise RuntimeError("Endpoint deletion still pending; retry cleanup.")
            control.delete_agent_runtime(agentRuntimeId=data["runtime_id"])
        if current:
            for _ in range(120):
                try:
                    control.get_agent_runtime(agentRuntimeId=data["runtime_id"])
                except control.exceptions.ResourceNotFoundException:
                    break
                time.sleep(3)
            else:
                raise RuntimeError("Runtime deletion is still pending. Retry cleanup later.")
    ddb = session.client("dynamodb")
    for name in (data["operations_table"], data["checkpoint_table"]):
        if not name.startswith(data["prefix"]):
            raise ValueError("Unexpected table name")
        try:
            ddb.delete_table(TableName=name)
        except ddb.exceptions.ResourceNotFoundException:
            pass
    for name in (data["operations_table"], data["checkpoint_table"]):
        ddb.get_waiter("table_not_exists").wait(TableName=name)
    ecr = session.client("ecr")
    try:
        ecr.delete_repository(repositoryName=data["repository"], force=True)
    except ecr.exceptions.RepositoryNotFoundException:
        pass
    iam = session.client("iam")
    try:
        iam.delete_role_policy(RoleName=data["role"], PolicyName="runbookops-runtime")
        iam.delete_role(RoleName=data["role"])
    except iam.exceptions.NoSuchEntityException:
        pass
    # Log groups contain the instructor's incident evidence; list their names for explicit review.
    logs = session.client("logs")
    for page in logs.get_paginator("describe_log_groups").paginate(
        logGroupNamePrefix="/aws/bedrock-agentcore/runtimes/" + data["prefix"]
    ):
        for group in page["logGroups"]:
            logs.delete_log_group(logGroupName=group["logGroupName"])
    data["cleaned_up"] = True
    path.with_name("aws-deployment-cleaned.json").write_text(json.dumps(data, indent=2) + "\n")
    path.unlink()
    print("Removed the recorded workshop runtime, tables, repository, role, and log groups.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
