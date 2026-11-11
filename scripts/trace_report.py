"""Create a local HTML view of a sanitized incident trace."""

import argparse
import html
import json
from pathlib import Path

from runbookops.security import redact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(".state/demo-latest.json"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/trace.html"))
    args = parser.parse_args()
    report = redact(json.loads(args.input.read_text()))
    state = report.get("state", {})
    rows = []
    for event in report.get("events", []):
        rows.append(
            "<tr><td>"
            + html.escape(event["kind"])
            + "</td><td><details><summary>Details</summary><pre>"
            + html.escape(json.dumps(event, indent=2))
            + "</pre></details></td></tr>"
        )
    page = """<!doctype html><html lang="en"><meta charset="utf-8"><title>RunbookOps incident trace</title>
<style>body{font:16px/1.6 system-ui;margin:40px auto;max-width:1100px;padding:0 20px;color:#182536}table{width:100%;border-collapse:collapse}td,th{padding:12px;text-align:left;border-bottom:1px solid #ccd3dd}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}summary{cursor:pointer}h1{font-size:30px}</style>
<h1>RunbookOps incident trace</h1>"""
    page += (
        "<p>Mode: "
        + html.escape(state.get("mode", "unknown"))
        + " | Incident: "
        + html.escape(state.get("incident_id", "unknown"))
        + "</p>"
    )
    page += (
        "<p>"
        + html.escape(state.get("diagnosis", ""))
        + "</p><table><thead><tr><th>Event</th><th>Evidence</th></tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></html>"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(page)
    print(args.output.resolve())


if __name__ == "__main__":
    main()
