# RAG Pipelines for DevOps: companion lab

Read the sample PDF chapter alongside this directory. All sources are synthetic. No deployment or shell-execution tool is exposed.

```bash
uv sync --frozen
uv run python -m course_labs.rag
uv run python check_lab.py
```

The default mode shows real keyword retrieval and extracted evidence without a generated answer. Optional semantic mode:

```bash
uv sync --frozen --extra semantic
uv run python -m course_labs.rag --backend semantic
```

The first semantic run downloads local embedding weights. For optional live answer generation, copy `.env.example` to `.env`, configure your own key and currently listed zero-priced model, then use `--live`. Never commit that file. `--role` is a teaching identity selector, not production authentication.

The code and lockfile are a snapshot for the sample chapter. The provider does not silently fall back to a paid route or replace a failed live response with offline output. The index is rebuilt on each CLI run for this small lab.
