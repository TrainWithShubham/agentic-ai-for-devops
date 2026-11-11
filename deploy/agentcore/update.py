"""Publish a new image version to the existing recorded workshop runtime."""

import base64
import json
import os
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

import boto3

ROOT = Path(__file__).resolve().parents[2]


def main():
    path = ROOT / ".state/aws-deployment.json"
    data = json.loads(path.read_text())
    if data.get("project") != "runbookops-v2":
        raise ValueError("Not a workshop deployment record")
    session = boto3.Session(region_name=data["region"])
    if session.client("sts").get_caller_identity()["Account"] != data["account"]:
        raise ValueError("Wrong AWS account")
    ecr = session.client("ecr")
    auth = ecr.get_authorization_token()["authorizationData"][0]
    username, password = base64.b64decode(auth["authorizationToken"]).decode().split(":", 1)
    image = data["image_uri"].rsplit(":", 1)[0] + ":v2-" + uuid.uuid4().hex[:8]
    context = json.loads(subprocess.check_output(["docker", "context", "inspect"]))[0]
    with tempfile.TemporaryDirectory(prefix="runbookops-docker-auth-") as temp:
        env = {**os.environ, "DOCKER_CONFIG": temp, "DOCKER_HOST": context["Endpoints"]["docker"]["Host"]}
        subprocess.run(
            ["docker", "login", "--username", username, "--password-stdin", auth["proxyEndpoint"]],
            input=password.encode(),
            env=env,
            check=True,
            capture_output=True,
        )
        subprocess.run(["docker", "tag", "runbookops:v2", image], env=env, check=True)
        subprocess.run(["docker", "push", image], env=env, check=True)
    control = session.client("bedrock-agentcore-control")
    current = control.get_agent_runtime(agentRuntimeId=data["runtime_id"])
    response = control.update_agent_runtime(
        agentRuntimeId=data["runtime_id"],
        agentRuntimeArtifact={"containerConfiguration": {"containerUri": image}},
        roleArn=data["role_arn"],
        networkConfiguration=current["networkConfiguration"],
        protocolConfiguration={"serverProtocol": "HTTP"},
        environmentVariables=current["environmentVariables"],
        requestHeaderConfiguration={"requestHeaderAllowlist": ["X-RunbookOps-Token"]},
        lifecycleConfiguration={"idleRuntimeSessionTimeout": 300, "maxLifetime": 1800},
    )
    data["image_uri"] = image
    data["runtime_version"] = response["agentRuntimeVersion"]
    path.write_text(json.dumps(data, indent=2) + "\n")
    for _ in range(180):
        status = control.get_agent_runtime(agentRuntimeId=data["runtime_id"])
        if status["status"] == "READY":
            break
        if status["status"].endswith("FAILED"):
            raise RuntimeError("Runtime update failed")
        time.sleep(5)
    else:
        raise RuntimeError("Runtime readiness timeout")
    control.update_agent_runtime_endpoint(
        agentRuntimeId=data["runtime_id"],
        endpointName=data["qualifier"],
        agentRuntimeVersion=data["runtime_version"],
    )
    for _ in range(120):
        endpoint = control.get_agent_runtime_endpoint(
            agentRuntimeId=data["runtime_id"], endpointName=data["qualifier"]
        )
        if endpoint["status"] == "READY" and endpoint.get("liveVersion") == data["runtime_version"]:
            print("Updated workshop endpoint READY, version " + data["runtime_version"])
            return 0
        time.sleep(3)
    raise RuntimeError("Endpoint update timeout")


if __name__ == "__main__":
    raise SystemExit(main())
