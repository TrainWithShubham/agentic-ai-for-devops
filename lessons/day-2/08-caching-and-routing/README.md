# Avoid repeating work

Application commands and paths below refer to the standalone [`runbookops`](https://github.com/TrainWithShubham/runbookops) checkout. Course exercises are the exception where noted.

Time: 15 minutes.

Run the cache example:

```bash
uv run python examples/cache_and_routing.py
```

The first retrieval is cold, the second is a hit, and a different role has its own cache entry. The key includes user, role, scopes, query, corpus version, embedding configuration, and result count. Document or metadata changes produce a new corpus fingerprint. Live operational reads and mutations do not use this cache.

Read `Retriever.search` and `Model.route`. A configured `OPENROUTER_SMALL_MODEL` is selected for summarization; the main model handles diagnosis. If no second model is configured, both tasks use the main model. The example prints the actual routing choice without claiming two live providers were tested.

Coding prompt:

> Change the retrieval-cache TTL, explain the freshness tradeoff, and run the cache isolation test. Then configure a second explicitly free model for summarization only after checking its current availability. Do not remove the free-model guard or change approval requirements.

```bash
uv run runbookops --mode openrouter ask "Summarize the checkout recovery procedure" --task summarize
```

Use a small request budget. Provider prompt caching is different from our retrieval cache and depends on model/API support and minimum prefix lengths. Do not infer a provider cache hit from a faster response.

Check understanding: explain what must invalidate the retrieval cache and why an old health response must not decide whether recovery succeeded.
