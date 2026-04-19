"""
CI/CD Failure Analyzer -- diagnoses GitHub Actions failures.
Run: python3 module-6/ci_analyzer.py
Requires: gh CLI authenticated (gh auth login)
"""

import subprocess
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import create_agent as create_react_agent


@tool
def list_workflow_runs(status: str = "failure") -> str:
    """List recent GitHub Actions workflow runs. Use status='failure' for failed runs."""
    result = subprocess.run(
        ["gh", "run", "list", "--status", status, "--limit", "5"],
        capture_output=True, text=True,
    )
    return result.stdout or result.stderr


@tool
def get_failed_logs(run_id: str) -> str:
    """Get the failed step logs from a GitHub Actions run. Pass the run ID."""
    result = subprocess.run(
        ["gh", "run", "view", run_id, "--log-failed"],
        capture_output=True, text=True,
    )
    output = result.stdout + result.stderr
    # Truncate if too long (LLMs have token limits)
    if len(output) > 5000:
        output = output[:5000] + "\n\n[...truncated, showing first 5000 chars]"
    return output


@tool
def get_workflow_file(workflow_name: str) -> str:
    """Read a GitHub Actions workflow YAML file. Pass the filename like 'ci.yml'."""
    import pathlib
    path = pathlib.Path(f".github/workflows/{workflow_name}")
    if path.exists():
        return path.read_text()
    return f"File not found: {path}"


llm = ChatOllama(model="gemma4", temperature=0)
tools = [list_workflow_runs, get_failed_logs, get_workflow_file]
agent = create_react_agent(llm, tools)

print("\nCI/CD Failure Analyzer")
print("-" * 40)
print("I analyze GitHub Actions failures.")
print("Run this inside a git repo with GitHub Actions.")
print("Type 'quit' to exit.\n")

while True:
    question = input("> ").strip()
    if question.lower() in ("quit", "exit", "q"):
        break
    if not question:
        continue

    print("\nThinking...\n")
    result = agent.invoke({"messages": [("user", question)]})
    print(result["messages"][-1].content)
    print()
