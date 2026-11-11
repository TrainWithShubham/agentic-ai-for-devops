# Model access for the workshop

Checked 11 November 2026. Recheck the selected provider and model on 13 November.

## Two different uses of a model

Learners may use Claude Code or Codex to edit code. RunbookOps separately calls a model API while investigating an incident. Paying for a coding assistant does not automatically fund those application calls.

[Claude Pro](https://support.claude.com/en/articles/8325606-what-is-the-pro-plan) includes Claude Code access and excludes Claude Console API usage. [Claude Code's subscription setup](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-max-or-ultra-plan) explains how to sign in with a subscription. An existing Anthropic API-key environment variable can cause Claude Code to use separately billed API access. Do not turn subscription login tokens into credentials for our Python agent.

A paid coding subscription is optional. Provide the lab prompt and a reviewed patch for each exercise, so someone without Claude Code can still finish.

## Selected class setup

Each learner uses an individual OpenRouter account and API key with a preflighted free model. The instructor's AWS credits are reserved for instructor Bedrock and AgentCore demonstrations. We will not build a sponsored learner gateway or distribute workshop model tokens.

OpenRouter is the chosen course default because one interface gives learners access to several model options. This is a course-design choice, not evidence that it has the largest free allowance or guaranteed capacity. Keep a Groq adapter as the first alternative to test, and offline practice for exhausted quotas or network failures.

Use a single provider configuration layer so switching provider, base URL, and model does not require rewriting RAG, tools, or approval. The app must reject paid model choices in its free-only mode and must never switch to a paid endpoint automatically. Store keys in ignored environment files and redact them from logs.

## OpenRouter: primary learner route

OpenRouter offers models with a `:free` variant and the `openrouter/free` router. Its [official free-model page](https://openrouter.ai/collections/free-models/) currently lists 20 requests per minute and 50 requests per day for free variants without a credit purchase. Failed attempts count. The higher daily allowance requires a credit purchase and is not a zero-purchase recommendation.

One agent investigation may require several model calls. For example, six calls per investigation would use 48 requests after eight investigations, before setup checks and retries. This is an illustration, not a measured budget for the unfinished application.

For a class of 50 to 100:

- Each learner uses their own account and key. Never share one free account across the class.
- Choose a named free model only after checking its current availability and structured tool support.
- The free router is useful for exploration, but it can select different models. Do not make an untested changing model the sole classroom dependency.
- Bound agent steps and reserve live calls for a few complete exercises. Run policy and state-transition checks offline.
- Do not silently fall back to a paid model when free capacity is exhausted.

Use only the synthetic course documents with these public endpoints. Provider data policies differ.

## Groq: first alternative to test

Groq has a [Free tier](https://console.groq.com/docs/billing-faqs), an [OpenAI-compatible API](https://console.groq.com/docs/openai), and [local tool calling](https://console.groq.com/docs/tool-use/overview). Our app can run operational tools and MCP locally, then return their results to the model.

Its [rate limits](https://console.groq.com/docs/rate-limits) apply at organization level and include requests and tokens. Check the learner's actual account and the Free Plan view; do not copy numbers from the Developer plan table into learner instructions. A large daily request allowance would still be constrained by per-minute or daily token limits.

Test a free account with the full RAG context and multi-step tool flow before choosing the backup model. Switching providers must be explicit, and a different model's behavior needs a fresh compatibility check. No live Groq account/model test has been completed for this course yet.

## Gemini free tier: additional option

Some Gemini models have a free API tier. Actual limits depend on the project, model, and account and must be checked in AI Studio. Availability and stated limits are not guaranteed. See [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) and [pricing](https://ai.google.dev/gemini-api/docs/pricing). Gemini supports [function calling](https://ai.google.dev/gemini-api/docs/function-calling); India is listed among [supported regions](https://ai.google.dev/gemini-api/docs/available-regions).

Keep this as a documented alternative. Implement and verify OpenRouter first, then Groq, before adding another provider adapter. Account setup belongs in prework.

## Offline practice

Provide a mode that replays documented responses or uses a deterministic policy for the seeded incident. Label it in the terminal, trace, and evaluation report. Learners can exercise RAG indexing, access checks, simulator behavior, approval, and replay protection without consuming API requests.

Offline mode does not test a real model's tool choice, factual support, latency, token usage, or resilience to prompt injection. Report those separately. There must be no fabricated live-model pass result.

## Provider acceptance check

Before publishing learner instructions, verify:

1. A plain model response succeeds.
2. A structured read-only tool request is returned and executed locally.
3. The tool result reaches the model in the correct format.
4. A retrieved document answer cites a source supplied in the context.
5. A bounded failure produces a useful error; no secrets appear in output.
6. An investigation reaches the proposal checkpoint without executing the proposed fix.
7. Measure requests and tokens per lab on a fresh free account. Target at most 30 model requests per learner per day, including preflight and retries, to leave room below the currently documented 50-request OpenRouter cap. This is a design target until the completed labs are measured.
8. Verify a second provider configuration and label offline results separately. Rehearse synchronized requests with a small volunteer group; this cannot establish guaranteed public free-tier capacity for 100 people.

The 50 to 100 attendees use independent accounts. More API keys under the same account do not create extra quota. Keep documents small, bound model steps, and run policy regression checks without provider calls. Check Bedrock access and quotas separately for the instructor's AWS demonstration.

## Learner message to publish after validation

> Create your own OpenRouter account and API key before November 14. We will use a tested free model; no API credit purchase or AWS account is required for the learner labs. Free models have usage limits. Complete the setup check in advance. Claude Code is optional, and offline practice is included if live model access fails.

This message is a draft. Publish it with the exact model and setup instructions only after the free-account checks pass.
