"""Shared paths and JSON printing, without application infrastructure."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def show(value):
    print(json.dumps(value, indent=2, ensure_ascii=False))


def read_json(relative):
    return json.loads((ROOT / relative).read_text())


def run_cli(main, recovery):
    """Show an actionable message for expected setup/input errors; keep a failing exit code."""
    try:
        main()
    except (ValueError, RuntimeError, OSError, ImportError) as error:
        print(f"Could not finish: {error}", file=sys.stderr)
        print(f"Next: {recovery}", file=sys.stderr)
        raise SystemExit(1) from None
