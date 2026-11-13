# Course material

Read [CONTEXT.md](CONTEXT.md) for the completed e-book handoff, reusable technical decisions and the current v2 course-work boundary. The book is finished; change it only when requested.

Work on `v2`. Preserve `main` and `v1`. Keep commits short and omit co-author trailers. Do not push, merge, create a PR, or provision AWS resources unless requested.

Modules 1–5 teach concepts through independent CI and deployment-document examples in this repository. They must not mention or depend on the module-6 application, its characters, its package, its data or its checkout. Module 6 introduces the separate application and owns its capstone/AWS demo instructions. Root navigation and instructor records may link to module 6.

Run course examples with uv and this repository's lockfile. Use clearly labeled deterministic offline examples by default. Live inference requires --live and the learner's own currently zero-priced OpenRouter model. Never silently fall back to paid inference. Never share instructor keys. No Kubernetes or AWS account is required for modules 1–5.

Use plain professional explanations, short scripts and synthetic DevOps data. Keep prompt instructions separate from trusted authorization and execution checks. Explain what each example actually implements; development principals are not an OAuth login implementation, keyword matching is not semantic embedding, and an offline fixture is not a live model decision.

Keep V1 code on `v1`; do not restore legacy application modules. New concept modules and course examples are authorized by the November 13 redesign. Application changes/tests remain in the separate application repository. Course checks cover executable examples, exercise solutions, both 180-minute schedules, local links and module isolation.

Never commit .env, .state, model caches, tokens or private signing material. Record decisions, failures and verification limits in DECISIONS.md. Describe AWS demonstrations as live only after a fresh invocation; previously deleted resources and historical traces do not establish current readiness.
