"""Run the instructor cloud capstone using IAM and short-lived signed workshop identities."""

import argparse
import json
import uuid
from pathlib import Path

import boto3
from botocore.config import Config

from runbookops.auth import Auth
from runbookops.config import Settings

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", default=str(ROOT / ".state/aws-deployment.json"))
    args = parser.parse_args()
    deployment = json.loads(Path(args.record).read_text())
    auth = Auth(Settings(root=ROOT))
    client = boto3.client(
        "bedrock-agentcore",
        region_name=deployment["region"],
        config=Config(
            retries={"total_max_attempts": 1, "mode": "standard"}, connect_timeout=10, read_timeout=240
        ),
    )

    def invoke(payload, user):
        token = auth.issue(user)

        def add_token(request, **kwargs):
            request.headers["X-RunbookOps-Token"] = token

        event = "before-sign.bedrock-agentcore.InvokeAgentRuntime"
        client.meta.events.register_first(event, add_token, unique_id="workshop-identity")
        try:
            response = client.invoke_agent_runtime(
                agentRuntimeArn=deployment["runtime_arn"],
                qualifier=deployment.get("qualifier", "DEFAULT"),
                runtimeSessionId=str(uuid.uuid4()),
                contentType="application/json",
                accept="application/json",
                payload=json.dumps(payload).encode(),
            )
            stream = response["response"]
            raw = stream.read() if hasattr(stream, "read") else b"".join(stream)
            result = json.loads(raw)
            if "detail" in result:
                return result
            return result
        finally:
            client.meta.events.unregister(event, unique_id="workshop-identity")

    print("Starting a cloud investigation as Bagha.", flush=True)
    state = invoke(
        {
            "operation": "investigate",
            "question": "Investigate checkout HTTP 503. Check health, logs, deployments and the current runbook, then prepare the documented correction for approval.",
        },
        "bagha",
    )
    if not state.get("proposal"):
        print(json.dumps(state, indent=2))
        raise RuntimeError("Cloud agent did not prepare a proposal")
    proposal = state["proposal"]
    decision = {
        "operation": "decide",
        "proposal_id": proposal["id"],
        "expected_hash": proposal["hash"],
        "approve": True,
    }
    print("Checking viewer approval is denied.", flush=True)
    denied = False
    try:
        response = invoke(decision, "bagha")
        denied = "detail" in response
    except client.exceptions.RuntimeClientError:
        denied = True
    if not denied:
        raise RuntimeError("Viewer approval was not denied")
    print("Approving as Jethalal in a new Runtime session.", flush=True)
    recovered = invoke(decision, "jethalal")
    if recovered.get("health", {}).get("http_status") != 200:
        print(json.dumps(recovered, indent=2))
        raise RuntimeError("Cloud recovery verification failed")
    report = {
        "mode": "live-bedrock-agentcore",
        "viewer_approval_denied": denied,
        "separate_runtime_sessions": True,
        "initial": state,
        "recovered": recovered,
    }
    path = ROOT / "artifacts/cloud-capstone.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print("Cloud capstone passed: HTTP 503 -> approval -> HTTP 200. Evidence: " + str(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
