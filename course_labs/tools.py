"""Three bounded, read-only CI tools shared by the plain loop and MCP example."""

from .common import ROOT, read_json


def read_tool(name, run_id):
    if type(run_id) is not int or run_id != 1042:
        raise ValueError("Only synthetic run 1042 is available; use that run ID")
    if name == "ci_get_run":
        return {"source_id": "ci-run", **read_json("data/ci/run.json")}
    files = {"ci_read_log": "test-output.txt", "ci_read_workflow": "workflow.txt"}
    if name not in files:
        raise ValueError("Unknown tool; discover the available read-only CI tools")
    return {
        "source_id": "ci-log" if name == "ci_read_log" else "ci-workflow",
        "text": (ROOT / "data/ci" / files[name]).read_text(),
    }


def execute(name, arguments):
    if not isinstance(arguments, dict) or set(arguments) != {"run_id"}:
        raise ValueError("Tool arguments must contain only the integer run_id")
    return read_tool(name, arguments["run_id"])


SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {"run_id": {"type": "integer", "enum": [1042]}},
                "required": ["run_id"],
                "additionalProperties": False,
            },
        },
    }
    for name, description in (
        ("ci_get_run", "Read the status and failed step for synthetic CI run 1042."),
        ("ci_read_log", "Read the bounded failed-step output for synthetic CI run 1042."),
        ("ci_read_workflow", "Read the workflow and dependency-group excerpts for synthetic CI run 1042."),
    )
]
