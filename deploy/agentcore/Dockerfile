FROM ghcr.io/astral-sh/uv:0.10.2 AS uv
FROM python:3.12-slim
COPY --from=uv /uv /uvx /usr/local/bin/
WORKDIR /app
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 RUNBOOKOPS_ROOT=/app RUNBOOKOPS_DATA=/tmp/runbookops \
    RUNBOOKOPS_MODEL_CACHE=/opt/models HF_HUB_DISABLE_XET=1 PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra aws --no-install-project &&     /app/.venv/bin/python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5', cache_dir='/opt/models')"
COPY src ./src
COPY resources ./resources
COPY scripts/mcp_entry.py ./scripts/mcp_entry.py
RUN uv sync --frozen --no-dev --extra aws && \
    useradd --uid 1000 --create-home workshop && chmod -R a+rX /app /opt/models
USER workshop
EXPOSE 8080
CMD ["/app/.venv/bin/uvicorn", "runbookops.api:app_factory", "--factory", "--host", "0.0.0.0", "--port", "8080"]
