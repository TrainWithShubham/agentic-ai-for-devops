"""Read this deployment's structured CloudWatch incident events."""

import argparse
import json
from pathlib import Path

import boto3

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--incident", help="Filter to one incident ID")
    args = parser.parse_args()
    deployment = json.loads((ROOT / ".state/aws-deployment.json").read_text())
    logs = boto3.client("logs", region_name=deployment["region"])
    prefix = "/aws/bedrock-agentcore/runtimes/" + deployment["prefix"]
    count = 0
    for page in logs.get_paginator("describe_log_groups").paginate(logGroupNamePrefix=prefix):
        for group in page["logGroups"]:
            params = {"logGroupName": group["logGroupName"], "limit": 100}
            if args.incident:
                params["filterPattern"] = '"' + args.incident + '"'
            for events in logs.get_paginator("filter_log_events").paginate(**params):
                for event in events["events"]:
                    text = event["message"].strip()
                    try:
                        item = json.loads(text)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(item, dict) and "incident_id" in item and "kind" in item:
                        print(json.dumps(item))
                        count += 1
    print(f"Structured incident events: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
