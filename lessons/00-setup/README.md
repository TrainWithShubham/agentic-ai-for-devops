# Before the workshop

Complete this before November 14. No AWS account or paid model credits are required for the learner path.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), clone the standalone application, and run:

```bash
git clone https://github.com/TrainWithShubham/runbookops.git
cd runbookops
uv sync --frozen
cp .env.example .env
uv run runbookops preflight
uv run runbookops demo
```

The default is offline practice. The final lines should report that Bagha was denied approval and checkout recovered to HTTP 200 after Jethalal approved it. This checks the software and control flow without calling a model.

Create your own OpenRouter account and key. Put the key in `.env`, keep `RUNBOOKOPS_FREE_ONLY=true`, and use the named free model selected for the workshop. The key file is ignored by Git. Do not put keys in screenshots, issue reports, or commands you share.

```bash
uv run runbookops models
uv run runbookops --mode openrouter demo
```

A Claude Pro subscription can help you use Claude Code to edit files. It does not provide the API key used by this application. Coding assistants are optional; the completed examples and lab prompts work without one.

Before class, download the small local embedding model:

```bash
uv run runbookops --embedding semantic index
uv run runbookops --embedding semantic search "checkout payment connection refused"
```

Use a laptop with roughly 8 GB RAM or the supplied Codespaces devcontainer. The semantic model downloads once; local generative-model inference is not required. Windows learners can use PowerShell for the `uv` commands; use `Copy-Item .env.example .env` for the copy step.

If model access fails, keep working with `--mode offline`. Hash embeddings are a lexical fallback, explicitly separate from the downloaded semantic model. See [troubleshooting](https://github.com/TrainWithShubham/runbookops/blob/main/docs/TROUBLESHOOTING.md).

Run application commands in the `runbookops` checkout. Keep the course checkout open for lessons and exercises. The Codespaces devcontainer is in the application repository.
