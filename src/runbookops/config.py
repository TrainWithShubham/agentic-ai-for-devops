"""Configuration shared by the CLI, API, and MCP server."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values


@dataclass
class Settings:
    root: Path = field(default_factory=lambda: Path(os.getenv("RUNBOOKOPS_ROOT", ".")).resolve())
    data: Path | None = None
    mode: str = "offline"
    embedding: str = "hash"
    model: str = ""
    api_key: str = field(default="", repr=False)
    max_calls: int = 6
    max_tokens: int = 2048
    mcp_url: str = ""
    mcp_token: str = field(default="", repr=False)
    database_url: str = field(default="", repr=False)
    free_only: bool = True
    dynamodb_table: str = ""
    checkpoint_table: str = ""
    oidc_issuer: str = ""
    oidc_audience: str = "runbookops"
    oidc_public_key: str = field(default="", repr=False)
    oidc_jwks: str = ""

    def __post_init__(self):
        self.root = self.root.resolve()
        data_path = Path(self.data or ".state")
        self.data = (data_path if data_path.is_absolute() else self.root / data_path).resolve()
        self.data.mkdir(parents=True, exist_ok=True)
        self.data.chmod(0o700)
        if self.mode not in ("offline", "openrouter", "groq", "bedrock"):
            raise ValueError("Mode must be offline, openrouter, groq, or bedrock")
        if not 1 <= self.max_calls <= 8 or not 128 <= self.max_tokens <= 4096:
            raise ValueError("Model budget outside workshop limits")

    @classmethod
    def load(cls, env_file=None, **overrides):
        values = dict(dotenv_values(".env"))
        if env_file:
            # Read only model configuration, never execute another project's env file.
            values.update(
                {
                    k: v
                    for k, v in dotenv_values(env_file).items()
                    if k.startswith(("OPENROUTER_", "GROQ_", "BEDROCK_"))
                }
            )
        values.update(os.environ)
        mode = overrides.get("mode") or values.get("RUNBOOKOPS_MODE", "offline")
        prefix = {"openrouter": "OPENROUTER", "groq": "GROQ", "bedrock": "BEDROCK"}.get(mode, "")
        config = dict(
            root=Path(values.get("RUNBOOKOPS_ROOT", ".")),
            data=values.get("RUNBOOKOPS_DATA") or None,
            mode=mode,
            embedding=values.get("RUNBOOKOPS_EMBEDDING", "hash"),
            model=values.get(prefix + "_MODEL")
            or (
                values.get("BEDROCK_MODEL_ID", "")
                if mode == "bedrock"
                else ("nvidia/nemotron-3.5-lightning:free" if mode == "openrouter" else "")
            ),
            api_key=values.get(prefix + "_API_KEY", "") or "",
            max_calls=int(values.get("RUNBOOKOPS_MAX_MODEL_CALLS", "6")),
            max_tokens=int(values.get("RUNBOOKOPS_MAX_OUTPUT_TOKENS", "2048")),
            mcp_url=values.get("RUNBOOKOPS_MCP_URL", "") or "",
            mcp_token=values.get("RUNBOOKOPS_MCP_TOKEN", "") or "",
            database_url=values.get("RUNBOOKOPS_DATABASE_URL", "") or "",
            free_only=values.get("RUNBOOKOPS_FREE_ONLY", "true").lower() == "true",
            dynamodb_table=values.get("RUNBOOKOPS_DYNAMODB_TABLE", "") or "",
            checkpoint_table=values.get("RUNBOOKOPS_CHECKPOINT_TABLE", "") or "",
            oidc_issuer=values.get("RUNBOOKOPS_OIDC_ISSUER", "") or "",
            oidc_audience=values.get("RUNBOOKOPS_OIDC_AUDIENCE", "runbookops") or "runbookops",
            oidc_public_key=values.get("RUNBOOKOPS_OIDC_PUBLIC_KEY", "") or "",
            oidc_jwks=values.get("RUNBOOKOPS_OIDC_JWKS", "") or "",
        )
        config.update({k: v for k, v in overrides.items() if v is not None})
        return cls(**config)
