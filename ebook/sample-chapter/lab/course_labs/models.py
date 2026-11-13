"""List currently zero-priced tool-capable catalog entries; no model invocation."""

from .common import show
from .provider import catalog, is_free_tool_model

if __name__ == "__main__":
    show({"free_tool_models": [m["id"] for m in catalog() if is_free_tool_model(m)]})
