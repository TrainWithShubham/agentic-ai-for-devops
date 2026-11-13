# v2 working context

Updated 13 November 2026. Read this with [AGENTS.md](AGENTS.md) before continuing repository work. This is a handoff, not a replacement for the curriculum or current documentation.

## Current task boundary

The owner considers the e-book and cover artwork finished. Preserve them unless the owner requests another book change. Work has returned to the concept-first `v2` course branch. Carry forward its explanations and verified engineering distinctions; do not turn the workshop into a book-production project.

Repository: TrainWithShubham/agentic-ai-for-devops, branch `v2`. Preserve `v1` and `main`. Do not push, merge, open a PR or provision AWS resources without a new request. Do not add co-author trailers. Use short local commit messages.

## Course decisions that still apply

- Two live online sessions, November 14–15, 2026; 180 minutes each, including a ten-minute break and fifteen-minute Q&A. Audience: 50–100 freshers and working engineers with basic Linux/Python/DevOps familiarity.
- Teach from scratch. Favor demonstrations and small learner edits, with evidence and a check. Learners can use Claude Code or Codex to help write code, but must inspect and explain the result.
- Modules 1–5 use independent synthetic CI-failure and deployment-document examples. They must not mention or depend on the final application's name, characters, package, data or checkout.
- Module 6 alone introduces the separate [RunbookOps repository](https://github.com/TrainWithShubham/runbookops) and owns the capstone/AgentCore demo. Application code, UI, infrastructure and application tests remain there.
- Modules 1–5 need no Kubernetes cluster or AWS account. Preserve their small scripts rather than rebuilding a full application here.
- Use deterministic, clearly labeled offline demonstrations by default. Live inference is explicit, uses the learner's own key and a currently zero-priced OpenRouter model, and has no silent paid/offline fallback. Free capacity is not guaranteed for a class.
- AWS is instructor-only. Earlier resources were deleted. Historical traces and book diagrams do not establish a currently running deployment. This handoff authorizes no cloud provisioning.
- Curriculum time is fixed. New explanations must replace or improve existing material rather than silently adding teaching time. Temporal is a book bonus, not a required extra workshop module.

## Reusable teaching and engineering knowledge

| Topic | Keep this distinction clear |
|---|---|
| System prompts | Instructions guide the model; trusted application code enforces access and execution. |
| Models and access | A model, coding application and API account are different things. Some Claude plans have conditional API credits; verify current eligibility instead of repeating a blanket subscription claim. |
| Tool calls | The model requests an action. The executor validates its name, arguments, caller and resource before running it. A request is not an execution result. |
| MCP | A real protocol exchange has a client, server and transport. A local server runs code on the laptop. Review startup commands, source and permissions; scope credentials appropriately. |
| LangGraph | The small course graph has volatile state. A production interrupt needs appropriate persistence and thread ownership. A resumed interrupted node starts from its beginning; earlier side effects can repeat. Do not imply this example implements durable interrupts. |
| RAG | Separate preparation from query-time retrieval. PDF/DOCX/PPTX/MD/TXT need suitable extraction; scanned PDFs need OCR and complex layouts need review. Keyword retrieval is not semantic embedding. |
| RAG failures | Distinguish missing supporting evidence, a retrieval failure and an authorization failure. Do not silently invent company policy from model memory. Apply access controls before private content reaches the model. Propagate deletion/access changes to chunks and cached results. |
| Approval | Review one exact action, target and parameters. Authenticate the reviewer, bind the decision to the proposal, recheck state/expiry and prevent replay. A hash does not authenticate a person. |
| Reliability | A timeout stops waiting; it does not prove a remote operation stopped. Check status/target state before retrying writes. Bound retries, avoid amplification and use a meaningful idempotency contract. |
| Caching and routing | Prompt caching differs from cached answers. Recheck permission, freshness and relevant versions. Demonstrated route labels are not live model routing unless an actual call occurs. |
| Observability and evaluation | Record observable actions, sources, versions, stop reasons and outcomes. Protect traces. Grade evidence use and results, with denied/missing/injected/duplicate cases. Code coverage and deterministic passes are not live-model reliability scores. |
| AgentCore | Runtime hosts custom code such as LangGraph; managed Harness provides a Strands loop on Runtime infrastructure. For managed Harness, allowedTools does not govern the separate direct-command API; IAM must control that separately. |
| Career scope | AIOps uses AI for IT operations. MLOps operates ML models/data pipelines. LLMOps operates language-model apps; GenAIOps may cover other generative models. These overlap. “Agent operations” is descriptive here, not a universal job taxonomy. |

The learning direction is to strengthen DevOps foundations, use one agent well, operate a bounded AI application and choose a specialization. It is not a 2027 hiring forecast or a promise that every engineer must become a model trainer. Avoid framework popularity claims without an appropriately scoped current study.

These claims were reviewed on 13 November 2026. Recheck version-sensitive service capabilities, API-credit eligibility, model availability, protocol versions, prices and third-party installation guidance before changing the runnable examples.

## Writing and visual conventions

Use short, human sentences, concrete definitions and familiar examples. Prefer a diagram that explains a decision or failure over a paragraph of framework names. Keep technical names visible, then explain them. About 80% professional and 20% approachable/fun was the requested tone; the application story belongs only in module 6.

The e-book uses TWS purple/gold, warm ivory and dark aubergine; original vector scenes and licensed Lucide icons; and an original rocket-only footer. Its illustrations are analogies with explicit limits. Do not copy marketing claims such as “most proven” or describe a community directory as security-verified. Keep source links near the claims they support.

## Finished book and artwork

- [Final e-book](output/pdf/agentic-ai-for-devops-visual-ebook.pdf): 89 pages, 24 chapters. Chapter 24, DevOps in the agentic AI era, is pages 75–77. The 12-resource QR page is page 89.
- [Standalone chapter archive](output/pdf/agentic-ai-for-devops-chapters.zip): 24 three-page chapters, preserving book page numbers.
- [Source/build guide](ebook/visual-edition/README.md), [manuscript](ebook/visual-edition/MANUSCRIPT.md), [technical review](ebook/visual-edition/FINAL_REVIEW.md), [claim-review scope](ebook/visual-edition/FACT_CHECK.md) and [publication evidence](ebook/visual-edition/VERIFICATION.json).
- Canonical chapter copy: `ebook/visual-edition/plain_content.py`, applied over the earlier content sources. Renderer: `build_book.py`; everyday scenes: `scenes.py`; technical diagrams: `illustrations.py`; 64 technical references: `sources.py`.
- [Resource list](ebook/visual-edition/RESOURCES.md) contains the owner's YouTube channel and all 11 requested repositories. QR evidence and source-identity checks are in `RESOURCE_QR.json` and `RESOURCE_REVIEW.json`.
- [Portrait cover poster](output/imagegen/agentic-ai-for-devops-cover-poster.png) and [1024 × 556 banner](output/imagegen/agentic-ai-for-devops-banner-1024x556.png), with generation prompts alongside them. These are generated promotional images; they do not replace the book cover or its original logo assets.
- Latest book content commit: `36c722a`. Poster/banner commits: `e9937ab` and `944cff8`. PDF SHA-256: `813e31e5f1422fc93868ce6717f6d2dfb11bf41a8f9fde5adb433b13487f62e5`.

Final book checks: 24 contents/bookmark targets, 176 link annotations, zero detected safe-area text overflow/significant recorded text-box overlap, 72 matching standalone pages and all 13 QR destinations decoded. Those are publication checks, not model, deployment or complete accessibility certification. The earlier approved sample remains separate.

## Back on repository work

Entry points: [curriculum](CURRICULUM.md), [instructor start page](instructor/START_HERE.md), [delivery plan](instructor/DELIVERY_PLAN.md), [setup](setup/README.md) and [course verification](instructor/VERIFICATION.md).

The return-to-branch check on 13 November passed all 14 deterministic course tests, including the real local MCP exchange. Local Markdown links, two 180-minute schedules, the 75-minute module-6 block and concept/module isolation also passed. This run did not repeat live model, semantic-model download, AWS, remote CI or cross-platform checks. Earlier evidence for those activities is dated historical evidence, not a fresh run.

Initial alignment inspection found these points already present in the course:

- Module 2 explains local MCP trust, in-memory graph state and the direct-tool/MCP boundary.
- Module 3 covers five-format extraction, missing evidence without a model call, source permissions and deletion/freshness questions.
- Module 5 discusses uncertain writes, cache scope, protected traces and outcome-based evaluation.

Next repository pass: compare those explanations with the code they demonstrate; tighten gaps in failure behavior and learner instructions without overstating implementation. Preserve the six-hour scope. A short AIOps/MLOps/LLMOps discussion can replace existing wrap-up material if requested; it does not automatically become another practical or module.

Use the existing checks after relevant course changes:

```bash
uv run python scripts/check_course.py
uv run python scripts/verify_docs.py
uv run ruff check .
```

Run exercise-specific checks when changing exercises. Reserve book publication checks for actual book edits. Do not read/copy credential files, run paid inference or recreate AWS resources merely to resume this branch.


## Learner-facing pass completed

The owner approved the beginner-focused cleanup after the handoff above. README/setup/modules now explain prerequisites, expected results, one learner change and recovery. Main navigation is learner-facing; maintainer links are collapsed. Cloud preparation moved to instructor/AGENTCORE_DEMO.md. The course still has six modules and two 180-minute sessions.

Added a small shared CLI error boundary, actionable catalog/configuration/optional-semantic messages and clearer exercise failures. No dependency or application architecture was added. Current course tests: 17 passing, including three new failure-path checks; fresh Python 3.12 installation and 16 documented offline/check commands also pass. Public catalog access worked; no inference, cloud deployment or standalone-app run was performed. Latest scope and limits are recorded in instructor/evidence/learner-experience-review.json. Book content and assets remain finished and unchanged.
