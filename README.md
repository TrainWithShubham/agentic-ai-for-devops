# Agentic AI for DevOps, V2

Build RunbookOps, an assistant that investigates Gada Electronics' checkout failure using company documents and operational tools. It prepares a fix, waits for an authorized human, and checks whether recovery worked.

Two live sessions on 14 and 15 November 2026, three hours each including breaks and questions. The course starts with AI fundamentals. Basic Python and Linux help; previous agent experience is not required.

## Start here

- [Curriculum and timed exercises](CURRICULUM.md)
- [Model access: what is free and what needs a key](docs/MODEL_ACCESS.md)
- [Build and rehearsal plan](instructor/DELIVERY_PLAN.md)
- [Previous course: Docker, MCP, and KubeHealer](README-v1.md)

## What we build

Day 1 covers LLMs, system prompts, a simple agent, retrieval from company documents, and operational tools through MCP.

Day 2 adds permissions, human approval, guardrails, caching, model routing, traces, and evaluations. The instructor demonstrates the same LangGraph project on Amazon Bedrock AgentCore Runtime. Managed AgentCore Harness is a separate architecture and receives a brief comparison.

The company knowledge pack will include PDF, DOCX, PPTX, Markdown, and text files. The incident runs against a small simulator, so learners do not need Kubernetes.

## Development status

This branch currently contains the revised curriculum, model-access decision, and delivery plan. The V2 application, starter checkpoints, document pack, provider adapters, and AWS deployment still need implementation and rehearsal. The existing `module-0` through `module-6` files belong to the previous course and remain unchanged.

Do not follow the old installation instructions expecting the V2 capstone. Publish the V2 setup command here once its clean-machine check passes.

## Cost and access

A Claude Pro subscription can be used for Claude Code, but does not pay for API calls from the Python application. A paid coding subscription is optional; learners will receive prepared code patches.

Learners use their own OpenRouter keys with a tested free model. Groq is the first backup provider to test, and a labeled offline practice mode covers provider failures or exhausted quotas. The instructor uses a separate AWS account for Bedrock and AgentCore demonstrations. Provider compatibility still needs live testing. Read the [model-access plan](docs/MODEL_ACCESS.md) before buying anything.

## Branch policy

V2 work stays on `course-v2-runbookops`. No pull request or changes to `main` are planned for this delivery. The old course remains available on `main`.
