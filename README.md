# Agentic AI for DevOps

A practical two-day workshop for freshers and working DevOps engineers. November 14–15, 2026: three hours each day, including breaks and questions.

Learn the concepts through CI failure analysis and deployment-document RAG. Run small examples, inspect their evidence and make a short code change. The integrated project is introduced in module 6 on Day 2.

## Syllabus

| Day | Module | Practical |
|---|---|---|
| 1 | [1. AI foundations and system prompts](module-1/README.md) | Explain a CI failure with evidence |
| 1 | [2. Agents, tool calling and MCP](module-2/README.md) | Follow a bounded tool loop, graph state and MCP exchange |
| 1 | [3. RAG pipelines](module-3/README.md) | Retrieve deployment guidance from five document formats |
| 2 | [4. Identity, guardrails and approval](module-4/README.md) | Reject unauthorized and changed proposals |
| 2 | [5. Agent harnesses and operations](module-5/README.md) | Inspect cache/routing/trace behavior and evaluation failures |
| 2 | [6. RunbookOps capstone and AgentCore demo](module-6/README.md) | Modify and verify the standalone project |

Read the [curriculum](CURRICULUM.md) for exact timing, outcomes and topic depth.

## Visual e-book

Read [Agentic AI for DevOps: a visual field guide](ebook/visual-edition/README.md): 24 beginner-friendly standalone chapters across the six modules, with Temporal and AgentCore bonuses. The 89-page [complete PDF](output/pdf/agentic-ai-for-devops-visual-ebook.pdf) pairs everyday illustrations with technical diagrams, short explanations and fictional DevOps examples, with beginner model guidance, prompt patterns and Claude Code practices. No setup is needed to read it.

## Start here

```bash
git clone --branch v2 https://github.com/TrainWithShubham/agentic-ai-for-devops.git
cd agentic-ai-for-devops
uv sync --frozen
uv run python -m course_labs.prompts
uv run python -m course_labs.agent
uv run python -m course_labs.rag
```

These are labeled offline demonstrations. No API key, AWS account or final-project checkout is needed for modules 1–5. See [setup](setup/README.md) for live inference and optional semantic retrieval.

```bash
uv run python scripts/check_course.py
uv run python scripts/verify_docs.py
```

## How the material works

`module-1` through `module-5` contain explanations, commands, bounded coding prompts and checks. `course_labs` contains their small independent examples. `data` contains synthetic CI evidence and deployment documents. Learner edits live in `exercises`; completed versions live in `solutions`.

Module 6 links to [RunbookOps](https://github.com/TrainWithShubham/runbookops), a separate application. Its source, UI, tests and AWS deployment stay there. The earlier modules do not import it or depend on its incident/story.

[Working context](CONTEXT.md) · [Recovery checkpoints](checkpoints/README.md) · [Instructor start page](instructor/START_HERE.md) · [Verification](instructor/VERIFICATION.md) · [Decisions](DECISIONS.md)

## Editions

`v1` preserves the previous course. `v2` contains the concept-first redesign and independent labs. `main` is unchanged by this work.
