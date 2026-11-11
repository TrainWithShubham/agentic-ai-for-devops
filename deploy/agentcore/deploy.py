"""Create an isolated instructor runtime. No learner AWS credentials are needed."""

import argparse
import base64
import json
import os
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

import boto3
from botocore.config import Config

from runbookops.auth import Auth
from runbookops.config import Settings

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / ".state/aws-deployment.json"


def save(data):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--model", default="us.amazon.nova-lite-v1:0")
    parser.add_argument("--image", default="runbookops:v2")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Continue Runtime creation using already-created workshop resources",
    )
    args = parser.parse_args()
    if STATE.exists() and args.resume:
        return create_runtime(json.loads(STATE.read_text()), Auth(Settings(root=ROOT)))
    if STATE.exists():
        raise SystemExit(
            "A deployment record already exists. Use its runtime or clean it up before creating another."
        )
    config = Config(retries={"total_max_attempts": 3, "mode": "adaptive"}, connect_timeout=5, read_timeout=60)
    session = boto3.Session(region_name=args.region)
    identity = session.client("sts", config=config).get_caller_identity()
    account = identity["Account"]
    prefix = "runbookops_v2_" + uuid.uuid4().hex[:8]
    auth = Auth(Settings(root=ROOT))
    data = {
        "project": "runbookops-v2",
        "region": args.region,
        "account": account,
        "prefix": prefix,
        "model": args.model,
        "role": prefix + "_runtime",
        "operations_table": prefix + "_operations",
        "checkpoint_table": prefix + "_checkpoints",
        "repository": prefix,
        "created_resources": [],
    }
    save(data)
    tags = [{"Key": "Project", "Value": "runbookops-v2"}, {"Key": "Workshop", "Value": "2026-11-14"}]
    ddb = session.client("dynamodb", config=config)
    print("Creating two workshop-only DynamoDB tables.", flush=True)
    for name, keys in [(data["operations_table"], ["pk"]), (data["checkpoint_table"], ["PK", "SK"])]:
        ddb.create_table(
            TableName=name,
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[{"AttributeName": k, "AttributeType": "S"} for k in keys],
            KeySchema=[
                {"AttributeName": k, "KeyType": "HASH" if i == 0 else "RANGE"} for i, k in enumerate(keys)
            ],
            SSESpecification={"Enabled": True},
            Tags=tags,
        )
        data["created_resources"].append({"kind": "table", "name": name})
        save(data)
        ddb.get_waiter("table_exists").wait(TableName=name, WaiterConfig={"Delay": 2, "MaxAttempts": 60})
        ddb.update_time_to_live(
            TableName=name, TimeToLiveSpecification={"Enabled": True, "AttributeName": "ttl"}
        )
    print("Creating a scoped runtime role and image repository.", flush=True)
    ecr = session.client("ecr", config=config)
    repository = ecr.create_repository(
        repositoryName=prefix,
        imageScanningConfiguration={"scanOnPush": True},
        tags=[{"Key": "Project", "Value": "runbookops-v2"}],
    )["repository"]
    data["image_uri"] = repository["repositoryUri"] + ":v2"
    data["created_resources"].append({"kind": "ecr", "name": prefix})
    save(data)
    bedrock = session.client("bedrock", config=config)
    profile = bedrock.get_inference_profile(inferenceProfileIdentifier=args.model)
    model_arns = [profile["inferenceProfileArn"]] + [item["modelArn"] for item in profile["models"]]
    iam = session.client("iam", config=config)
    trust = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {"aws:SourceAccount": account},
                    "ArnLike": {"aws:SourceArn": f"arn:aws:bedrock-agentcore:{args.region}:{account}:*"},
                },
            }
        ],
    }
    role = iam.create_role(RoleName=data["role"], AssumeRolePolicyDocument=json.dumps(trust), Tags=tags)[
        "Role"
    ]
    data["role_arn"] = role["Arn"]
    data["created_resources"].append({"kind": "role", "name": data["role"]})
    save(data)
    log_arn = f"arn:aws:logs:{args.region}:{account}:log-group:/aws/bedrock-agentcore/runtimes/{prefix}*"
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Action": ["bedrock:InvokeModel"], "Resource": model_arns},
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:Query",
                    "dynamodb:BatchGetItem",
                    "dynamodb:BatchWriteItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:DescribeTable",
                ],
                "Resource": [
                    f"arn:aws:dynamodb:{args.region}:{account}:table/{name}"
                    for name in (data["operations_table"], data["checkpoint_table"])
                ],
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogStreams",
                ],
                "Resource": [log_arn, log_arn + ":*"],
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:BatchGetImage",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchCheckLayerAvailability",
                ],
                "Resource": repository["repositoryArn"],
            },
            {"Effect": "Allow", "Action": ["ecr:GetAuthorizationToken"], "Resource": "*"},
        ],
    }
    iam.put_role_policy(
        RoleName=data["role"], PolicyName="runbookops-runtime", PolicyDocument=json.dumps(policy)
    )
    (ROOT / "artifacts").mkdir(exist_ok=True)
    (ROOT / "artifacts/runtime-policy.json").write_text(json.dumps(policy, indent=2))
    authdata = ecr.get_authorization_token()["authorizationData"][0]
    username, password = base64.b64decode(authdata["authorizationToken"]).decode().split(":", 1)
    print("Pushing the ARM64 image with temporary Docker authentication.", flush=True)
    context = json.loads(subprocess.check_output(["docker", "context", "inspect"]))[0]
    with tempfile.TemporaryDirectory(prefix="runbookops-docker-auth-") as temp:
        env = {**os.environ, "DOCKER_CONFIG": temp, "DOCKER_HOST": context["Endpoints"]["docker"]["Host"]}
        subprocess.run(
            ["docker", "login", "--username", username, "--password-stdin", authdata["proxyEndpoint"]],
            input=password.encode(),
            env=env,
            check=True,
            capture_output=True,
        )
        subprocess.run(["docker", "tag", args.image, data["image_uri"]], env=env, check=True)
        subprocess.run(["docker", "push", data["image_uri"]], env=env, check=True)
    return create_runtime(data, auth)


def create_runtime(data, auth):
    from types import SimpleNamespace

    args = SimpleNamespace(region=data["region"], model=data["model"])
    prefix = data["prefix"]
    config = Config(retries={"total_max_attempts": 3, "mode": "adaptive"}, connect_timeout=5, read_timeout=60)
    session = boto3.Session(region_name=args.region)
    iam = session.client("iam", config=config)
    trust = iam.get_role(RoleName=data["role"])["Role"]["AssumeRolePolicyDocument"]
    print("Creating AgentCore Runtime with IAM admission and a signed application identity.", flush=True)
    control = session.client("bedrock-agentcore-control", config=config)
    environment = {
        "RUNBOOKOPS_CLOUD": "true",
        "RUNBOOKOPS_MODE": "bedrock",
        "RUNBOOKOPS_FREE_ONLY": "false",
        "BEDROCK_MODEL_ID": args.model,
        "AWS_REGION": args.region,
        "RUNBOOKOPS_EMBEDDING": "semantic",
        "RUNBOOKOPS_DYNAMODB_TABLE": data["operations_table"],
        "RUNBOOKOPS_CHECKPOINT_TABLE": data["checkpoint_table"],
        "RUNBOOKOPS_OIDC_ISSUER": auth.issuer,
        "RUNBOOKOPS_OIDC_PUBLIC_KEY": auth.public.replace("\n", "\\n"),
        "RUNBOOKOPS_OIDC_AUDIENCE": auth.audience,
        "RUNBOOKOPS_LOG_EVENTS": "true",
    }
    kwargs = dict(
        agentRuntimeName=prefix,
        agentRuntimeArtifact={"containerConfiguration": {"containerUri": data["image_uri"]}},
        roleArn=data["role_arn"],
        networkConfiguration={"networkMode": "PUBLIC"},
        protocolConfiguration={"serverProtocol": "HTTP"},
        environmentVariables=environment,
        requestHeaderConfiguration={"requestHeaderAllowlist": ["X-RunbookOps-Token"]},
        tags={"Project": "runbookops-v2", "Workshop": "2026-11-14"},
        lifecycleConfiguration={"idleRuntimeSessionTimeout": 300, "maxLifetime": 1800},
        description="Gada Electronics course simulator. Instructor demo only.",
    )
    if not data.get("runtime_id"):
        for attempt in range(8):
            try:
                response = control.create_agent_runtime(**kwargs)
                break
            except control.exceptions.ValidationException as error:
                if attempt == 7 or "role" not in str(error).lower():
                    raise
                time.sleep(5)
        data.update(runtime_id=response["agentRuntimeId"], runtime_arn=response["agentRuntimeArn"])
        data["created_resources"].append({"kind": "runtime", "name": data["runtime_id"]})
        save(data)
    # Use the documented account/region trust scope. Exact runtime ARN matching failed in this deployment.
    trust["Statement"][0]["Condition"]["ArnLike"]["aws:SourceArn"] = (
        f"arn:aws:bedrock-agentcore:{args.region}:{data['account']}:*"
    )
    iam.update_assume_role_policy(RoleName=data["role"], PolicyDocument=json.dumps(trust))
    for _ in range(180):
        status = control.get_agent_runtime(agentRuntimeId=data["runtime_id"])
        if status["status"] == "READY":
            break
        if status["status"].endswith("FAILED"):
            raise RuntimeError("Runtime provisioning failed: " + status.get("failureReason", "unknown"))
        time.sleep(5)
    else:
        raise RuntimeError("Runtime did not become READY within 15 minutes")
    if not data.get("qualifier"):
        endpoint = control.create_agent_runtime_endpoint(
            agentRuntimeId=data["runtime_id"],
            name="workshop",
            agentRuntimeVersion=status["agentRuntimeVersion"],
        )
        data["endpoint_id"] = endpoint["id"] if "id" in endpoint else endpoint.get("agentRuntimeEndpointId")
        data["qualifier"] = "workshop"
        save(data)
    for _ in range(120):
        ep = control.get_agent_runtime_endpoint(agentRuntimeId=data["runtime_id"], endpointName="workshop")
        if ep["status"] == "READY":
            print("Runtime and workshop endpoint READY. Run deploy/agentcore/invoke.py.", flush=True)
            return 0
        if ep["status"].endswith("FAILED"):
            raise RuntimeError("Endpoint provisioning failed")
        time.sleep(3)
    raise RuntimeError("Endpoint readiness timeout")


if __name__ == "__main__":
    raise SystemExit(main())
