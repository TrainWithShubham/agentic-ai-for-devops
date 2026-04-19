# Module 6 -- Build Your Own AIOps Agent

You've seen what AI agents can do for DevOps -- from explaining Docker errors to self-healing Kubernetes clusters. Now you build one yourself.

This module provides a **CI/CD Failure Analyzer** -- an agent that reads your GitHub Actions failures, fetches the logs, and tells you exactly what went wrong and how to fix it.

## What You'll Learn

- **Building your own agent from scratch** -- same patterns from Module 2/3, applied to a new domain
- **GitHub CLI as a tool source** -- the `gh` CLI gives you workflow runs, logs, and more. The agent calls it like any other tool.
- **Putting it all together** -- tools, LLM, agent loop. You've done this before. Now do it on your own problem.

## The Code

One file: [`ci_analyzer.py`](ci_analyzer.py)

Three tools, all using the `gh` CLI:

```python
@tool
def list_workflow_runs(status: str = "failure") -> str:
    """List recent GitHub Actions workflow runs."""
    result = subprocess.run(
        ["gh", "run", "list", "--status", status, "--limit", "5"],
        capture_output=True, text=True,
    )
    return result.stdout or result.stderr
```

Same pattern as every module -- subprocess call, capture output, return it. The agent decides which tools to use.

## Prerequisites

You need the **GitHub CLI** (`gh`) installed and authenticated:

```bash
# Install (if you don't have it)
# macOS
brew install gh

# Linux
sudo apt install gh
```

Then authenticate:

```bash
gh auth login
```

## Try It

### Option A: Use your own repo

`cd` into any repo that has GitHub Actions:

```bash
cd ~/your-project-with-github-actions
python3 /path/to/module-6/ci_analyzer.py
```

Ask it:

- "Show me recent failed runs"
- "What went wrong in the last failure?"
- "Read the workflow file and check for issues"

### Option B: Use a test workflow

If you don't have a repo with failures handy, create one:

1. Create a new repo (or use an existing one)
2. Add this broken workflow:

```bash
mkdir -p .github/workflows
```

Create `.github/workflows/ci.yml`:

```yaml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm install
      - run: npm test
```

3. Push it (it will fail because there's no package.json):

```bash
git add .github/workflows/ci.yml
git commit -m "add CI workflow"
git push
```

4. Wait for it to fail, then run the analyzer:

```bash
python3 module-6/ci_analyzer.py
```

```
> What failed in my last CI run?
```

The agent fetches the failure logs and explains: "npm install failed because there's no package.json in the repo."

## How It Works

Same architecture as Module 2/3:

```
You ask a question
  |
  v
LLM reads the question, picks a tool
  |
  v
Tool runs (gh CLI), returns output
  |
  v
LLM reads the output, picks another tool or gives final answer
  |
  v
You get a diagnosis with a fix
```

The three tools:

| Tool | What it does | gh command |
|------|-------------|------------|
| `list_workflow_runs` | Lists recent runs (failed, success, etc.) | `gh run list` |
| `get_failed_logs` | Gets logs from the failed steps | `gh run view <id> --log-failed` |
| `get_workflow_file` | Reads the workflow YAML | Reads `.github/workflows/<name>` |

## Extend It

This is your agent now. Some ideas:

- **Add a `rerun_workflow` tool** -- `gh run rerun <id>` to retry a failed run
- **Add a `list_workflow_files` tool** -- list all workflow files in `.github/workflows/`
- **Add a `get_pr_checks` tool** -- `gh pr checks` to see check statuses on a PR
- **Switch to Claude or GPT** -- swap `ChatOllama` for `ChatAnthropic` or `ChatOpenAI`
- **Add a system prompt** -- tell the LLM "You are a CI/CD expert. Always suggest specific fixes with code snippets."
- **Build a different agent entirely** -- AWS Cost Optimizer, Incident Responder, Log Analyzer -- the pattern is the same: tools + LLM + agent loop

## The Pattern

Every agent you've built in this course follows the same structure:

```python
# 1. Define tools (functions the LLM can call)
@tool
def my_tool(param: str) -> str:
    """Description the LLM reads to decide when to use this."""
    # call an API, run a command, read a file
    return result

# 2. Create the agent
llm = ChatOllama(model="gemma4", temperature=0)
agent = create_react_agent(llm, [my_tool, ...])

# 3. Run it
result = agent.invoke({"messages": [("user", question)]})
```

That's it. Change the tools, change the domain. Docker, Kubernetes, CI/CD, AWS, monitoring -- the pattern is always the same.

---

You made it. You went from zero LLM experience to building AI agents that automate real DevOps tasks. Go build something.
