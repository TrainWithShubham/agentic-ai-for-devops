"""Primary references reviewed on 2026-11-13; no vendor prose is reproduced."""

SOURCES = {
    "agents": (
        "Anthropic: building effective agents",
        "https://www.anthropic.com/research/building-effective-agents",
    ),
    "prompting": (
        "Claude: prompt engineering",
        "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview",
    ),
    "context": (
        "Anthropic: context engineering",
        "https://www.anthropic.com/research/effective-context-engineering-for-ai-agents",
    ),
    "tools": ("Anthropic: writing tools", "https://www.anthropic.com/research/writing-tools-for-agents"),
    "tool-use": (
        "Claude: tool use",
        "https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview",
    ),
    "reliability": ("Google SRE: handling overload", "https://sre.google/sre-book/handling-overload/"),
    "mcp": ("MCP: architecture", "https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture"),
    "mcp-auth": (
        "MCP: authorization",
        "https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization",
    ),
    "mcp-security": (
        "MCP: security practices",
        "https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices",
    ),
    "langgraph": ("LangGraph: overview", "https://docs.langchain.com/oss/python/langgraph/overview"),
    "persistence": ("LangGraph: persistence", "https://docs.langchain.com/oss/python/langgraph/persistence"),
    "interrupts": ("LangGraph: interrupts", "https://docs.langchain.com/oss/python/langgraph/interrupts"),
    "retrieval": ("LangChain: retrieval", "https://docs.langchain.com/oss/python/deepagents/retrieval"),
    "rag-security": (
        "OWASP: RAG security",
        "https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html",
    ),
    "extraction": ("pypdf: text extraction", "https://pypdf.readthedocs.io/en/stable/user/extract-text.html"),
    "search": ("Qdrant: hybrid search", "https://qdrant.tech/documentation/search-tuning/hybrid-search/"),
    "rerank": (
        "Qdrant: FastEmbed reranking",
        "https://qdrant.tech/documentation/fastembed/fastembed-rerankers/",
    ),
    "rag-evals": (
        "Microsoft: RAG evaluation",
        "https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/rag-evaluators",
    ),
    "oidc": ("OpenID Connect Core 1.0", "https://openid.net/specs/openid-connect-core-1_0.html"),
    "oauth": ("IETF: OAuth security / RFC 9700", "https://www.rfc-editor.org/rfc/rfc9700"),
    "authorization": (
        "OWASP: authorization",
        "https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html",
    ),
    "transaction": (
        "OWASP: transaction authorization",
        "https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html",
    ),
    "injection": (
        "OWASP: prompt injection",
        "https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html",
    ),
    "agent-security": (
        "OWASP: AI agent security",
        "https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html",
    ),
    "harness": (
        "Anthropic: long-running harnesses",
        "https://www.anthropic.com/research/effective-harnesses-for-long-running-agents",
    ),
    "idempotency": (
        "AWS: safe retries and idempotency",
        "https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/",
    ),
    "caching": (
        "Claude: prompt caching",
        "https://platform.claude.com/docs/en/build-with-claude/prompt-caching",
    ),
    "routing": ("LangChain: model capabilities", "https://docs.langchain.com/oss/python/langchain/models"),
    "traces": ("OpenTelemetry: traces", "https://opentelemetry.io/docs/concepts/signals/traces/"),
    "genai-otel": (
        "OpenTelemetry: GenAI conventions",
        "https://github.com/open-telemetry/semantic-conventions-genai",
    ),
    "sre-monitoring": (
        "Google SRE: monitoring",
        "https://sre.google/sre-book/monitoring-distributed-systems/",
    ),
    "evals": (
        "Anthropic: agent evaluations",
        "https://www.anthropic.com/research/demystifying-evals-for-ai-agents",
    ),
    "testing": ("LangGraph: testing", "https://docs.langchain.com/oss/python/langgraph/test"),
    "github-security": (
        "GitHub Actions: secure use",
        "https://docs.github.com/en/actions/reference/security/secure-use",
    ),
    "github-token": (
        "GitHub Actions: token permissions",
        "https://docs.github.com/en/actions/tutorials/authenticate-with-github_token",
    ),
    "runbookops": ("RunbookOps: application source", "https://github.com/TrainWithShubham/runbookops"),
    "temporal-workflow": ("Temporal: workflow execution", "https://docs.temporal.io/workflow-execution"),
    "temporal-definition": ("Temporal: workflow determinism", "https://docs.temporal.io/workflow-definition"),
    "temporal-activities": ("Temporal: Activities", "https://docs.temporal.io/activities"),
    "temporal-retry": ("Temporal: retry policies", "https://docs.temporal.io/encyclopedia/retry-policies"),
    "temporal-messages": (
        "Temporal: workflow messages",
        "https://docs.temporal.io/encyclopedia/workflow-message-passing",
    ),
    "temporal-execution": ("Temporal: Activity execution", "https://docs.temporal.io/activity-execution"),
    "agentcore-runtime": (
        "AgentCore: Runtime",
        "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agents-tools-runtime.html",
    ),
    "agentcore-compare": (
        "AgentCore: Harness vs Runtime",
        "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-vs-runtime.html",
    ),
    "agentcore-harness": (
        "AgentCore: managed Harness",
        "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness.html",
    ),
    "agentcore-gateway": (
        "AgentCore: Gateway",
        "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html",
    ),
    "agentcore-security": (
        "AgentCore: Harness security",
        "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-security.html",
    ),
    "agentcore-tools": (
        "AgentCore: Harness tools",
        "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/harness-tools.html",
    ),
}

GLOSSARY = [
    ("Agent", "Model-directed choices of steps or tools toward a goal."),
    ("Workflow", "A process whose routes and sequencing are defined in application logic."),
    ("LLM", "Large language model; generates or interprets content from its input and learned patterns."),
    ("Token", "A unit used to represent model input or output; not a fixed number of words."),
    ("Context window", "The finite input/output capacity supported by a particular model interface."),
    ("System instructions", "Application-supplied behavioral guidance; not an authorization mechanism."),
    ("Tool call", "A structured request for a capability, subject to trusted validation and execution."),
    ("MCP", "Model Context Protocol; exchanges between applications and capability servers."),
    ("State", "The data representing current progress, evidence, decisions and status."),
    ("Checkpointer", "Persists graph state for a thread; durability depends on the storage implementation."),
    ("RAG", "Retrieval-augmented generation; supplies external evidence for an answer."),
    ("Chunk", "A bounded source segment with enough context and metadata for retrieval."),
    ("Embedding", "A numeric representation used for tasks such as similarity search."),
    ("Groundedness", "The degree to which answer claims are supported by the supplied evidence."),
    ("RBAC", "Role-based access control; roles map to allowed operations."),
    ("OAuth 2.0", "Delegated authorization framework; token meaning depends on the issuer and resource."),
    ("OIDC", "OpenID Connect; an identity layer built on OAuth 2.0."),
    ("HITL", "Human-in-the-loop; a human decision is part of the system process."),
    ("Guardrail", "A control that constrains some input, behavior or output; scope must be explicit."),
    ("Prompt injection", "Untrusted content attempts to redirect model behavior or tool use."),
    ("Idempotency", "Designing repeated attempts for one logical operation to avoid duplicate effects."),
    ("Trace / span", "A connected operation history / one timed operation within it."),
    ("Evaluation", "A repeatable task and assessment method for behavior or outcome."),
    ("Harness", "Execution machinery around a model: state, tools, limits and recovery."),
    ("Temporal Activity", "External or nondeterministic work that can be retried; writes need idempotency."),
    ("Temporal Workflow", "Deterministic orchestration reconstructed using recorded event history."),
    ("AgentCore Runtime", "AWS hosting for an agent or tool implementation that you supply."),
    ("Managed Harness", "AgentCore configuration-based loop, powered by Strands."),
]
