"""List current zero-priced tool models; the catalog request does not invoke a model."""

from .common import show
from .provider import catalog, is_free_tool_model

if __name__ == "__main__":
    show({"free_tool_models": [m["id"] for m in catalog() if is_free_tool_model(m)]})
