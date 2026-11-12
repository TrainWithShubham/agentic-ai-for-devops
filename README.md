# Agentic AI for DevOps

A two-day live workshop on November 14 and 15, 2026. Three hours each day, including breaks and questions.

Learn how an agent uses system instructions, company knowledge, operational tools, identity checks, and human approval to investigate an incident. The capstone is RunbookOps: a fictional Gada Electronics checkout failure, diagnosed and repaired through a local simulator.

## Start here

1. Read the [curriculum and timing](CURRICULUM.md).
2. Complete [setup](lessons/00-setup/README.md).
3. Follow the [lessons](lessons/README.md).
4. Open [module 6 — RunbookOps capstone](module-6/README.md).

**The application now lives in [TrainWithShubham/runbookops](https://github.com/TrainWithShubham/runbookops).** Clone it separately to run the UI, CLI, examples, tests, and deployment tools. This repository contains the course material and learner exercises.

## The two days

| Day | Topics |
|---|---|
| Day 1 | AI foundations, system prompts, a simple agent, mixed-format RAG, and MCP |
| Day 2 | Identity, approval, guardrails, caching and routing, observability, evaluations, and an instructor AgentCore Runtime demo |

Learners use their own OpenRouter keys for live inference. Offline practice needs no API key or AWS account. AWS demonstrations use instructor credentials, which are never shared. A coding assistant subscription does not supply the application's model API access.

## Working with two repositories

Keep the course checkout open for reading. Run `uv`, application commands, and runnable examples from the **RunbookOps checkout**. Application paths such as `src/runbookops`, `resources`, and `examples` refer to that repository.

The health exercise stays here in `exercises`, with its completed version in `solutions`. From this course checkout:

```bash
python3 scripts/check_exercise.py health --solution
python3 scripts/verify_docs.py
```

| Here in the course | In RunbookOps |
|---|---|
| Curriculum and lessons | Application source and UI |
| Learner exercises and solutions | Runnable examples and synthetic knowledge |
| Instructor delivery notes | Tests, coverage gates, and app CI |
| Recovery instructions and historical course evidence | Run guide, API/security docs, and deployment tools |

See [recovery commands](checkpoints/README.md), [instructor start page](instructor/START_HERE.md), and [teaching notes](instructor/TEACHING_NOTES.md).

## Course editions

- `v1`: original course with KubeHealer, Temporal, and the CI analyzer.
- `v2`: updated lessons and exercises, with RunbookOps linked as a separate application.

`main` and `v1` remain unchanged. Application development continues on `main` in the new RunbookOps repository. [DECISIONS.md](DECISIONS.md) records the course's implementation history and repository split.
