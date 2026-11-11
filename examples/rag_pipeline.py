"""Inspect the text extracted from each public format before indexing."""

import json

from runbookops.config import Settings
from runbookops.rag import chunks, extract

settings = Settings.load()
folder = settings.root / "resources/company-knowledge"
for item in json.loads((folder / "manifest.json").read_text()):
    if item["access"] != "public" or not item["current"]:
        continue
    parts = extract(folder / item["file"])
    pieces = list(chunks(parts))
    print(item["file"], "| sections:", len(parts), "| chunks:", len(pieces))
    for location, text in pieces[:1]:
        print(" ", location, ":", text[:160])
