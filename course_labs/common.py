"""Shared paths and JSON printing, without application infrastructure."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def show(value):
    print(json.dumps(value, indent=2, ensure_ascii=False))


def read_json(relative):
    return json.loads((ROOT / relative).read_text())
