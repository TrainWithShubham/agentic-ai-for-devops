# Prepare your laptop

Modules 1–5 run from this course checkout. You need a terminal, Python 3.11–3.13 and [uv](https://docs.astral.sh/uv/getting-started/installation/). uv can install a compatible Python version. No AWS account, Docker, Kubernetes cluster or Node.js is needed for the concept labs.

```bash
git clone --branch v2 https://github.com/TrainWithShubham/agentic-ai-for-devops.git
cd agentic-ai-for-devops
uv sync --frozen
uv run python -m course_labs.prompts
uv run python scripts/check_course.py
```

Run all documented commands from this directory. The examples use synthetic CI and deployment documents. Offline output is labeled; it does not call a generative model. Start there before troubleshooting provider access.

## Optional live model

Create your own OpenRouter account and API key. Configure the ignored local file:

```bash
cp .env.example .env
uv run python -m course_labs.models
```

Copy one listed model ID into `OPENROUTER_MODEL` and put your own key in `OPENROUTER_API_KEY` using an editor. The catalog command does not invoke a model. Never paste the key into a chat, screen share, commit or command-line argument.

```bash
uv run python -m course_labs.prompts --live
uv run python -m course_labs.agent --live
```

The adapter requires a currently listed `:free` model with zero prompt/completion prices and tool support. It disables fallback and uses bounded requests. The request budget is 1,200 output tokens. Optional reasoning is disabled for models that advertise support; a reasoning-only/empty response is an explicit failure. Capacity, quotas, provider logging and availability can change. A failed live call remains a failed live call; select offline practice explicitly if needed. Free access is not a guarantee of class-wide concurrent capacity.

A paid ChatGPT/Claude subscription is separate from application API access. Claude Code/Codex can help with small edits, but you can run the supplied examples without a coding-assistant subscription. Review the code and its result yourself.

## Optional semantic retrieval

```bash
uv sync --frozen --extra semantic
uv run python -m course_labs.rag --backend semantic
```

The first run downloads a local embedding model into `.cache/models`. Prepare it before the session. Keyword retrieval works without the extra; it teaches extraction, chunks, metadata and citations while keeping the distinction from embeddings explicit. `uv sync --frozen` removes optional extras again; include `--extra semantic` when retaining that environment.

The supplied PDF, DOCX and PPTX files are ready to read. Rebuilding those fixtures is an authoring task: `uv sync --frozen --extra authoring` then `uv run python scripts/build_documents.py`. It is not learner setup.

## If setup fails

Use [recovery checkpoints](../checkpoints/README.md). Keep `.env` and downloaded files private. A Codespaces or local devcontainer is optional and subject to your account's quota; no free browser-lab allocation is promised. Follow along with the instructor if a download/provider issue would otherwise consume the class.

Prepare the separate Day 2 project only when following [module 6 setup](../module-6/README.md). The earlier examples do not require it.
