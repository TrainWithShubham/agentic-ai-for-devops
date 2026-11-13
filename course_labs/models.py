"""List current zero-priced tool models; the catalog request does not invoke a model."""

from .common import run_cli, show
from .provider import catalog, is_free_tool_model


def main():
    show({"free_tool_models": [m["id"] for m in catalog() if is_free_tool_model(m)]})


if __name__ == "__main__":
    run_cli(main, "Check your internet connection and retry this command; see setup/README.md.")
