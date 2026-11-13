# Module 1 — AI foundations and system prompts

Day 1, 45 minutes. Run commands from the course repository root. Start with [setup](../setup/README.md).

## What you should understand

| Term | First explanation |
|---|---|
| AI | Software techniques for tasks such as prediction, perception and decision-making |
| Machine learning | Systems learn patterns from examples/data |
| Generative AI | Systems produce content such as text, code or images |
| LLM | A language model that produces responses from context |
| Chat application | An interface around models, tools and stored conversation context |
| Agent | A controlled loop where a model can choose permitted next steps |

An LLM predicts a response from its input context. Generative AI describes systems that produce content; an LLM is one kind of model. A chat interface is a product around a model. An agent adds a loop in which model output can request tools and the application supplies the resulting observations.

A fixed workflow chooses the order in code. An agent can choose a next step from observations. Use a normal script when the inputs, checks and steps are already known. Use an agent when interpreting varied evidence and choosing among permitted steps adds value. A CI dependency installer should stay deterministic even if a model helps investigate its failure.

Tokens are the units a model processes. The context window limits what fits in a request; it is not permanent memory. Repeating an entire log on each turn can increase latency and usage. Give the model the relevant step output and source IDs. Discuss model knowledge cutoffs, outdated answers and plausible unsupported explanations.

| Input | Purpose | Trust boundary |
|---|---|---|
| System instructions | Define the assistant's task, limits and response contract | Application-owned instructions |
| User request | State the task | Cannot grant new permissions |
| Logs and documents | Supply evidence | Untrusted data, including any embedded instructions |
| Tool schema/result | Describe permitted calls and actual observations | Application validates and executes calls |

Context engineering means selecting and maintaining the instructions, evidence, messages and tool results that fit the task. Use the [glossary](../GLOSSARY.md) when a term is unfamiliar.

## Demo: a failed CI job

```bash
uv run python -m course_labs.prompts
```

Open [the log](../data/ci/test-output.txt), [workflow excerpt](../data/ci/workflow.txt) and [system prompt](../prompts/ci-system.txt). The test job excluded the dev dependency group, which contains pytest. The process fails before any tests run. Removing `--no-dev` is a proposed correction to the fixture; the demo has not changed or rerun a real pipeline.

The default response is a fixed offline example. For an actual model response, configure your own free model as described in setup and run:

```bash
uv run python -m course_labs.prompts --live
```

Ask learners to find an observed fact, an inference and a proposed action. If the model claims it fixed the pipeline, compare that claim with the tools actually available.

## Practical: make the answer reviewable

Edit [exercises/system_prompt.txt](../exercises/system_prompt.txt). Require:

- Observed failure and supporting source IDs.
- Likely cause, with uncertainty if evidence is missing.
- Minimal proposed change for human review.
- A validation step and a statement of what was actually executed.

Try the prompt in ChatGPT/Claude with the synthetic fixture, or temporarily copy it to `prompts/ci-system.txt` for the CLI demo. Review the diff before retaining a change. The CLI reads only that documented prompt file.

AI coding prompt:

> Help me improve the response contract for this CI investigator. Keep the existing read-only boundary. Explain each instruction you add. Do not invent a successful rerun or change the tool permissions.

A structured format makes an answer easier to inspect. Valid JSON alone does not make a diagnosis correct. Application validation and observed results still matter.

## Check understanding

Explain why a fixed dependency-install step does not need an agent. Identify why `pytest` failing to start differs from a failing test assertion. Name one limit a system prompt can describe but only application code can enforce.

Continue with [module 2](../module-2/README.md).
