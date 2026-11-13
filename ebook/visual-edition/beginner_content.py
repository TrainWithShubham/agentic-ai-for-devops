"""Beginner additions. Future-facing advice is a learning plan, not a forecast."""

from content import CHAPTERS, chapter

ORIGINAL = list(CHAPTERS)
CHAPTERS.clear()
CHAPTERS.append(ORIGINAL[0])

chapter(
    2,
    "Mistakes to avoid early",
    "01 / Foundations",
    "triangle-alert",
    "Which habits get in the way?",
    "DevOps experience gives you useful instincts about evidence, permissions and recovery. Bring those instincts into AI. Build confidence by explaining one result before adding another tool.",
    [
        ("Trust", "A confident explanation can contain an invented fact or command."),
        ("Complexity", "More agents, tools or frameworks create more behavior to inspect."),
        ("Learning", "Ask why a change works before accepting generated code."),
    ],
    "mistakes",
    "Turn familiar habits into better checks",
    "A model response can vary even when your script would be predictable. Keep the question small enough that you can compare the answer with real evidence.",
    [
        ("Tool collecting", "Start with one useful capability before connecting many servers."),
        ("Prompt guessing", "Add missing evidence and a success condition before adding adjectives."),
        ("Blind copy-paste", "Inspect flags, paths and effects before running a suggested command."),
        ("Demo equals proof", "Repeat with denied access, missing evidence and a failed provider call."),
    ],
    "Pasting secrets, accepting unreviewed changes and granting broad credentials are avoidable engineering errors. Use sanitized examples while learning.",
    "The first answer looks convincing",
    "A fictional assistant explains a CI failure by claiming that the network was unavailable. The only supplied log says the test runner was missing.",
    [
        ("Pause", "Underline the claim and find the evidence offered for it."),
        ("Separate", "The missing executable is observed; a network failure is a hypothesis."),
        ("Ask", "Request the install step and dependency declaration before a fix."),
        ("Learn", "Write down what confirmed the cause and what remains unknown."),
    ],
    "Resist changing the prompt, model and framework at the same time. One controlled change makes the result easier to explain.",
    "A beginner copies an entire generated pipeline, cannot explain it and treats a green-looking summary as a passed build.",
    "Review one change, inspect the actual CI outcome and explain the evidence in your own words before adding another feature.",
    [
        "Treat fluent text as a claim to check.",
        "Start with a small, observable task.",
        "Keep credentials out of learning examples.",
        "Save one failure and explain its cause.",
    ],
    ["agents", "evals", "agent-security"],
)

chapter(
    3,
    "Models, APIs and access",
    "01 / Foundations",
    "brain-circuit",
    "What are you actually using?",
    "A model is a trained system. Running it on an input is inference. Claude is a model family; Claude Code is a coding application that uses models and tools. An API lets your own code request a service.",
    [
        ("Training", "Learning model parameters from data; separate from asking a question."),
        ("Inference", "Using an existing model to produce an output for a request."),
        ("Access", "A chat login, coding-tool login and application API setup can differ."),
    ],
    "models",
    "Choose for the job",
    "Model names change. Compare the capability you need, acceptable delay, data handling and budget. Test on examples you understand before committing to a model.",
    [
        ("Text and code", "Generate explanations, structured fields or proposed patches."),
        ("Reasoning budget", "Some models can spend more computation on a difficult task."),
        ("Embeddings", "Represent content numerically for search; not a chat answer."),
        ("Local or hosted", "Local inference uses your hardware; hosted inference calls a service."),
    ],
    "Claude, GPT, Gemini, Qwen and Llama are examples of model families, not interchangeable products. Check current model IDs, licenses and capabilities at their official sources.",
    "Choose for one CI question",
    "Your first task is to explain a sanitized missing-dependency error. You do not need to train a model or deploy an agent platform to compare answers.",
    [
        ("Task", "Provide the failed step, install command and dependency declaration."),
        ("Capability", "Check the output format and tool-call support if your application needs tools."),
        ("Compare", "Use the same evidence; judge correctness, delay and actual usage."),
        ("Access", "Verify authentication, available credits, rate limits and data policy."),
    ],
    "Check API access and billing separately from your coding login. Some plans offer API credits with conditions; never assume an unlimited allowance. Free endpoints can have changing quotas.",
    "A learner chooses a model by a leaderboard alone, assumes their subscription covers every API call and adds tools without testing support.",
    "Choose using your task and account. Start with a small budget and a reviewed example; check current access rather than relying on a screenshot or an old tutorial.",
    [
        "Distinguish model, provider and application.",
        "Compare one task across candidates.",
        "Check tool and structured-output support.",
        "Verify credits, quotas and data handling.",
    ],
    ["models-overview", "embeddings-intro", "api-access", "local-models", "free-models", "model-families"],
)

# The original prompts chapter now follows the model foundations.
CHAPTERS.append(ORIGINAL[1])

chapter(
    5,
    "Prompts you can adapt",
    "01 / Foundations",
    "file-text",
    "What makes a prompt useful?",
    "A useful DevOps prompt names the task, supplies relevant evidence, sets boundaries and asks for a checkable result. There is no single best prompt for every model or incident. Start with these patterns and assess the output.",
    [
        ("Task", "Say what decision or explanation you need."),
        ("Evidence", "Name the files, excerpts or observations available."),
        ("Result", "Ask for sources, uncertainty and a validation plan."),
    ],
    "prompt-pattern",
    "Give the request a clear shape",
    'Use ordinary language and concrete constraints. Replace vague instructions such as "make it production ready" with the changes and checks that would establish success.',
    [
        ("Goal", "Explain why the test job failed; prepare a proposal."),
        ("Evidence", "Use only this log, workflow and dependency file."),
        ("Boundary", "Do not execute commands or change the workflow."),
        ("Acceptance", "Return facts, cause, exact proposal, validation and unknowns."),
    ],
    "Ask for a short explanation tied to source locations. Inspect the evidence and observed actions when checking the result.",
    "Four DevOps prompt patterns",
    "Supply the named evidence before using a pattern. Replace the task details to fit your environment; these are examples, not tested guarantees.",
    [
        (
            "CI failure",
            "Using this log and workflow, explain the failed step. Cite lines. Separate facts from hypotheses. Propose the smallest fix and a validation check. Do not edit files.",
        ),
        (
            "Document answer",
            "Using these deployment excerpts, answer who approves rollback. Cite the supporting section. If the evidence is missing or conflicts, say so. Do not grant approval.",
        ),
        (
            "Terraform review",
            "Review this Terraform diff. Explain changed resources, possible replacement, access changes and uncertainty. Suggest validation. Do not apply it or assume a cost estimate.",
        ),
        (
            "Incident summary",
            "Summarize these sanitized events as observed facts, hypotheses and next read-only checks. Include time and source references. Do not claim recovery without a confirming observation.",
        ),
    ],
    "When an answer is weak, inspect the evidence and the requested result before adding a longer persona. Keep the prompt version with the reviewed example.",
    'The request says "act as a 10x engineer and fix the deployment" but supplies no target, logs or definition of success.',
    "Name the resource and evidence, ask for a proposal and state what would validate it. Prompt instructions still do not replace execution permissions.",
    [
        "Supply the evidence the model can use.",
        "Ask for sources and missing information.",
        "Bound actions and affected resources.",
        "Judge the result against the actual task.",
    ],
    ["prompting", "context", "tool-use"],
)

chapter(
    6,
    "Claude Code work habits",
    "01 / Foundations",
    "list-checks",
    "How do you learn while it writes code?",
    "Claude Code can inspect a codebase, edit files and run tools under its configured permissions. You remain responsible for understanding the change. Start with a small task you can inspect and verify.",
    [
        ("Explore", "Ask where the behavior lives before requesting a patch."),
        ("Plan", "Use Plan mode to understand a nontrivial change first."),
        ("Verify", "Read the diff and actual check output before accepting the work."),
    ],
    "claude-habits",
    "Give instructions, then enforce boundaries",
    "Keep CLAUDE.md short: project facts, conventions and real check commands. It is context for the model. Permissions, sandboxing and appropriate hooks serve different enforcement purposes.",
    [
        ("CLAUDE.md", "Record the relevant project structure and verification commands."),
        ("Plan + scope", "Choose one change and identify the files it should affect."),
        ("Permissions", "Grant only the tools, paths and environment access needed."),
        ("Review + check", "Inspect the patch, run the relevant checks and explain the result."),
    ],
    "Skills package reusable instructions. Hooks run at lifecycle events and can automate checks. Review their code and sources; both can add behavior you did not expect.",
    "One small, reviewable change",
    "A fictional Python CI job installs only runtime dependencies, then tries to run pytest. Work in an isolated branch or checkout without production credentials.",
    [
        (
            "Explore",
            "Find the install step and declared test dependency. Explain the mismatch; do not edit yet.",
        ),
        (
            "Plan",
            "Propose the smallest change that installs the declared test group. Keep the test step intact.",
        ),
        ("Implement", "Make only the agreed change. Summarize the diff and any assumption."),
        ("Verify", "Run the available relevant checks. Report exact results and anything you could not run."),
    ],
    "Watch the Hindi lesson, then explain one change without reading the generated answer. Menu names and permission behavior may change after this edition.",
    "A learner enables broad permission bypass, asks for a whole platform and accepts a large patch because Claude reports that tests passed.",
    "Use a small scope and normal permission checks. Read the actual diff and test result; reject test removal or fabricated verification. Keep secrets outside the accessible learning environment.",
    [
        "Keep project instructions concise.",
        "Explore and plan before broad edits.",
        "Review commands, permissions and the diff.",
        "Ask for exact checks and unresolved limits.",
    ],
    ["claude-best", "claude-memory", "claude-permissions", "claude-skills", "claude-hooks", "tws-video"],
)

CHAPTERS.extend(ORIGINAL[2:])
for number, item in enumerate(CHAPTERS, 1):
    item["number"] = number

# Beginner explanations at the point where new jargon first matters.
by_title = {item["title"]: item for item in CHAPTERS}
by_title["The agent harness"]["diagram_note"] = (
    "A timeout limits waiting. A retry is another attempt. Idempotency prevents repeated attempts for one logical operation from duplicating effects. Store important progress outside process memory."
)
by_title["Observability you can use"]["intro"] = (
    "Observability means understanding a system from the evidence it emits. A trace connects one request to retrieval, model calls, tools and review. It helps locate a bad source, a bad decision or a failed operation."
)
by_title["Identity, RBAC and OAuth"]["intro"] = (
    'Authentication establishes who the caller is. Authorization decides what that caller may do on a resource. Credentials help authenticate a request; a user prompt saying "I am the admin" establishes neither identity nor permission.'
)

PROMPT_CHAPTER = 5
CLAUDE_CHAPTER = 6
PROJECT_CHAPTER = next(c["number"] for c in CHAPTERS if c["title"] == "Case study: RunbookOps")
VIDEO_URL = "https://www.youtube.com/watch?v=14K2noGTJ1M"
