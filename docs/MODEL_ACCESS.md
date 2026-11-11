# Model access for the workshop

Checked 11 November 2026. Recheck the selected provider and model on 13 November.

## Two different uses of a model

Learners may use Claude Code or Codex to edit code. RunbookOps separately calls a model API while investigating an incident. Paying for a coding assistant does not automatically fund those application calls.

[Claude Pro](https://support.claude.com/en/articles/8325606-what-is-the-pro-plan) includes Claude Code access and excludes Claude Console API usage. [Claude Code's subscription setup](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-max-or-ultra-plan) explains how to sign in with a subscription. An existing Anthropic API-key environment variable can cause Claude Code to use separately billed API access. Do not turn subscription login tokens into credentials for our Python agent.

A paid coding subscription is optional. Provide the lab prompt and a reviewed patch for each exercise, so someone without Claude Code can still finish.

## Recommended class setup

Use a workshop model gateway funded by the instructor's AWS credits. Learners receive an expiring workshop token and endpoint URL, not AWS credentials. Their local LangGraph agent runs retrieval and simulator tools locally, and calls the gateway only for model responses and tool-call decisions.

The instructor pays through AWS credits, subject to actual credit eligibility. This is free to the attendee, not universally free infrastructure. The endpoint still needs to be built, deployed, and load-tested.

Required gateway behavior:

- One independently revocable token per learner; store hashes server-side and transmit tokens over HTTPS.
- An allowlist of preflighted Bedrock models. Ignore or reject arbitrary upstream URLs and unauthorized model choices.
- Limits on input size, output tokens, requests per learner, and simultaneous requests. Reject excess work with a useful retry response.
- Preserve structured tool calls and tool results. A successful text response alone is not a provider compatibility test.
- Bound retries and timeouts. Make failures visible to the learner instead of silently switching to fixtures.
- Keep credentials server-side and out of logs. Track learner token ID, selected model, usage, errors, and latency without recording secrets.
- Expire access after the workshop. Include a revocation procedure and delete credentials from local example files.

Workshop tokens authorize model access only. They do not authorize simulator changes or grant Jethalal's approver role.

## OpenRouter: optional free API access

OpenRouter offers models with a `:free` variant and the `openrouter/free` router. Its [official free-model page](https://openrouter.ai/collections/free-models/) currently lists 20 requests per minute and 50 requests per day for free variants without a credit purchase. Failed attempts count. The higher daily allowance requires a credit purchase and is not a zero-purchase recommendation.

One agent investigation may require several model calls. For example, six calls per investigation would use 48 requests after eight investigations, before setup checks and retries. This is an illustration, not a measured budget for the unfinished application.

For a class of 50 to 100:

- Each learner uses their own account and key. Never share one free account across the class.
- Choose a named free model only after checking its current availability and structured tool support.
- The free router is useful for exploration, but it can select different models. Do not make an untested changing model the sole classroom dependency.
- Bound agent steps and reserve live calls for a few complete exercises. Run policy and state-transition checks offline.
- Do not silently fall back to a paid model when free capacity is exhausted.

Use only the synthetic course documents with these public endpoints. Provider data policies differ.

## Gemini free tier: secondary option

Some Gemini models have a free API tier. Actual limits depend on the project, model, and account and must be checked in AI Studio. Availability and stated limits are not guaranteed. See [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) and [pricing](https://ai.google.dev/gemini-api/docs/pricing).

Keep this as another candidate, not a promise that every attendee can create an eligible project in the live session. Do not add a third provider integration before the main route works.

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
7. The 100-attendee concurrency test stays within discovered AWS request/token quotas and the configured queue limits.

Credit balance does not establish service capacity. Check quotas and model access in the instructor's actual region before rehearsal.

## Learner message to publish after validation

> You do not need to buy model API credits for the core exercises. We will provide workshop model access. If you already use Claude Code, you can use it to edit the project; it is optional. Bring a laptop and complete the setup check before November 14. An offline practice mode is included if your network or model access fails.

This message is a draft. Publish it only when sponsored access passes the checks above.
