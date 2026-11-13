# Set up your laptop

Start without a model key. You will run a prepared CI example and check that your laptop is ready.

Modules 1–5 need Git, a terminal and uv. uv manages Python and packages for you. Docker, Node.js, Kubernetes and AWS are not required.

## 1. Install the tools

Install [Git](https://git-scm.com/downloads) and [uv](https://docs.astral.sh/uv/getting-started/installation/) using their official instructions. On Windows, use PowerShell; on macOS or Linux, use Terminal.

Open a new terminal after installation, then check:

```bash
git --version
uv --version
```

Both commands should print a version. If either command is missing, finish its installation and reopen the terminal before continuing.

## 2. Download and prepare the course

```bash
git clone --branch v2 https://github.com/TrainWithShubham/agentic-ai-for-devops.git
cd agentic-ai-for-devops
uv sync --frozen --python 3.12
```

Already cloned it? Open that folder instead of cloning again. Run the remaining commands from the folder containing `pyproject.toml`. `--frozen` installs the versions recorded in `uv.lock`. The first run may download Python 3.12 and packages; you do not need to activate a virtual environment yourself.

## 3. Run your first example

```bash
uv run python -m course_labs.prompts
```

You should see these fields among the printed instructions and answer:

```json
{
  "mode": "offline fixture, no LLM call",
  "observed": "pytest cannot start; the installation excluded development dependencies",
  "sources": ["ci-log", "ci-workflow"]
}
```

This is an excerpt, not the whole output. A fixture is prepared sample data. The program explains a made-up CI failure; it does not call an AI model or change a pipeline.

```bash
uv run python scripts/check_course.py
```

Successful output ends with `OK`. Now open [module 1](../module-1/README.md).

## Optional live model

Do this after the offline example works. Create your own [OpenRouter account](https://openrouter.ai/) and API key, then create a local configuration file. If `.env` already exists, edit it and skip the copy command:

```bash
cp .env.example .env
uv run python -m course_labs.models
```

`cp` also works in PowerShell. The second command reads the public model list, not a model response. It prints `free_tool_models`. Choose one listed ID. Open `.env` in an editor and fill in `OPENROUTER_MODEL` and `OPENROUTER_API_KEY`.

If the list is empty or unavailable, continue offline and try again later. Do not put the key in a prompt, command-line argument, screenshot or commit.

```bash
uv run python -m course_labs.prompts --live
uv run python -m course_labs.agent --live
```

`--live` sends the synthetic input to an external model. Look for `mode: live` and inspect the answer's sources. The answer may differ from the prepared example. A live failure stays a failure; no paid or offline fallback is used. Omit `--live` yourself when returning to offline practice.

The adapter requires a currently listed `:free` model with zero input/output prices and tool support. It allows up to 1,200 output tokens per request. Availability, quotas and provider privacy terms vary; free access does not promise capacity for the whole class.

Claude Code or Codex is optional help for small edits. A coding-assistant login is different from application API configuration. Some Claude plans include conditional API credits; check [current eligibility](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers). This course's live examples still use your own OpenRouter configuration.

## Optional semantic retrieval

Module 3 starts with keyword search. To compare it with meaning-based search:

```bash
uv sync --frozen --extra semantic
uv run python -m course_labs.rag --backend semantic
```

The first semantic run downloads an embedding model into `.cache/models`. An embedding represents text as numbers for comparison; it does not write an answer. Prepare the download before class or stay with keyword search. `uv sync --frozen` removes optional extras again, so retain `--extra semantic` when you need them.

## If something goes wrong

| What you see | What to do |
|---|---|
| `uv` or `git` is not recognized | Reopen your terminal after installing the tool. Check its official installation guide. |
| No `pyproject.toml` found | Change into the downloaded `agentic-ai-for-devops` folder. |
| A download fails | Check your connection, then rerun the same setup command. The first install needs internet. |
| Live mode needs a key/model | Edit your local `.env`, or rerun without `--live`. |
| Model unavailable, rate-limited or truncated | Read the error. Check the model list, try later or explicitly use offline practice. |
| Semantic package is missing | Rerun `uv sync --frozen --extra semantic`, or omit `--backend semantic`. |
| Exercise says `Not passed yet` | The starter is meant to be incomplete. Read its contract and use [recovery checkpoints](../checkpoints/README.md). |

If you are still stuck, save the command and error text, hide credentials and ask for help. An instructor demonstration is a useful way to follow along while fixing laptop setup. Browser environments such as Codespaces depend on your account and quota; no free lab allocation is promised.

The supplied PDF, DOCX and PPTX files are ready to use. Learners do not need to rebuild them. Prepare the separate Day 2 application using [module 6](../module-6/README.md) when you reach it.
