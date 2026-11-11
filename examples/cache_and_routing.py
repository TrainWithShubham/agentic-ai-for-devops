"""Inspect application cache isolation and configured model routing without model calls."""

from runbookops.config import Settings
from runbookops.models import Model
from runbookops.rag import Retriever
from runbookops.security import principal

settings = Settings.load()
rag = Retriever(settings)
query = "checkout payment service URL recovery runbook"
for user in ("bagha", "bagha", "jethalal"):
    result = rag.search(query, principal(user))
    print(user, "cache_hit=", result["cache_hit"], "sources=", [r["source"] for r in result["results"]])
model = Model(Settings.load(mode="openrouter"))
print("Diagnosis route:", model.route("diagnose"))
print("Summarization route:", model.route("summarize"))
print("Routing display only; no model requests sent.")
