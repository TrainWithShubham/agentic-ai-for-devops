# Module 4 -- AIOps Demystified

Day 1 was about building agents. Day 2 is about making them production-ready. Before we write more code, let's understand the landscape -- what AIOps is, who's doing it, what can go wrong, and why durability matters.

## What You'll Learn

- **Why AIOps exists** -- the alert fatigue problem that makes manual ops unsustainable at scale.
- **Who's building what** -- real companies shipping AIOps products right now.
- **What can go wrong** -- the AWS Kiro incident and why unbounded agents are dangerous.
- **Why durability matters** -- agents crash, LLMs timeout, networks fail. How Temporal solves this.

## The Problem: Alert Fatigue

A mid-sized engineering team gets **thousands of alerts per day**. Vectra's 2023 State of Threat Detection report measured an average of 4,484 alerts/day across SOC teams. Most are noise. Engineers learn to ignore them.

The result:

- Teams respond to less than 5% of alerts
- Real incidents get buried in the noise
- MTTR (Mean Time to Recovery) goes up because the signal is lost in the flood
- On-call engineers burn out

This is why AIOps exists. The idea: use AI to triage, correlate, and act on alerts so humans only deal with what actually matters.

## The Landscape: Who's Building AIOps

Three examples at very different scales:

### NeuBird -- Startup ($19.3M raised, April 2026)

Autonomous AI agents for Site Reliability Engineering. They scan alerts, correlate them across services, and suggest (or take) remediation actions.

Their numbers: 1M+ alerts resolved, up to 90% reduction in MTTR, $2M+ saved in engineering hours.

Backed by Xora Innovation, Mayfield, and Microsoft's M12.

### Komodor -- Enterprise (Cisco case study)

Kubernetes troubleshooting platform. Their AI agent "Klaudia" provides multi-cluster visibility and autonomous self-healing.

Cisco case study: 80% faster MTTR, 40% reduction in tickets. Investigation that took hours now takes seconds because Klaudia synthesizes data across the entire Kubernetes stack.

Lacework case study: 70% MTTR reduction across 30+ clusters and 3,700+ services. They expanded their on-call pool from fewer than 10 to 40+ responders because the tool made K8s accessible to non-experts.

### k8sgpt -- Open Source (CNCF Sandbox)

CLI tool that scans your Kubernetes cluster and explains problems in plain English. Think of it as Module 1's error explainer, but for your entire cluster.

```bash
k8sgpt analyze
```

It runs built-in analyzers that examine Kubernetes objects, identifies issues, and sends them to an LLM (OpenAI, Gemini, Bedrock, etc.) for human-readable explanations.

Open source, Apache-2.0 license, CNCF sandbox project. This is the closest thing to what we're building in this course.

## The Risk: Agents Without Guardrails

### The AWS Kiro Incident (December 2025)

Amazon's AI coding agent "Kiro" caused a **13-hour AWS outage** in their Cost Explorer service. Here's what happened:

1. A human operator granted Kiro elevated permissions -- their own access level
2. This bypassed the normal requirement of two human sign-offs before production changes
3. Kiro autonomously decided to "delete and recreate" a production environment
4. 13 hours of downtime

The root cause wasn't the AI being "dumb." The AI did what it thought was correct. The failure was **no guardrails**:

- No permission boundaries -- the agent had the same access as its operator
- No mandatory peer review for destructive actions
- No blocklist for dangerous operations (delete, drop, destroy)
- No human-in-the-loop checkpoint before irreversible changes

### Lessons for Our Agents

When we build KubeHealer in Module 5, we'll follow these rules:

1. **Explicit tool list** -- the agent can only call functions we define. No shell access, no arbitrary commands.
2. **Safe actions only** -- restart pod, scale deployment, adjust resources, rollback. No delete, no destroy.
3. **Scoped permissions** -- the agent operates in specific namespaces, not cluster-wide.
4. **Audit trail** -- every action is logged in Temporal's workflow history. You can see exactly what the agent did and why.

The goal is an agent that's useful enough to fix real problems but constrained enough that it can't cause an incident.

## The Durability Problem

Here's a scenario. Your agent detects a crashing pod, asks the LLM for a diagnosis, and gets back "increase memory limits to 512Mi." The agent is about to apply the fix when:

- The worker process crashes (OOM, segfault, deployment)
- The network drops between your agent and the Kubernetes API
- The LLM provider has a timeout or rate limit error

What happens? In a naive Python script:

```python
# This is what most tutorials teach
diagnosis = call_llm("Why is this pod crashing?")  # LLM returns "increase memory"
apply_fix(diagnosis)  # <-- crash happens here. Fix never applied.
# Script restarts. No memory of what happened. Starts from scratch.
# Maybe the LLM gives a different answer this time. Maybe it retries the same work.
```

The diagnosis is lost. The fix was never applied. When the script restarts, it has no memory of what already happened. It might re-diagnose, get a different answer, or retry work that partially completed.

### How Temporal Fixes This

Temporal is a **durable execution** platform. It guarantees that your code runs to completion, even if workers crash, networks fail, or services timeout.

The key idea: Temporal records every step of your workflow. If a worker crashes after the LLM returns a diagnosis but before the fix is applied, Temporal knows:

- The LLM call already completed (don't redo it)
- The fix hasn't been applied yet (resume from here)

When a new worker picks up the workflow, it **replays** the history, skips completed steps, and continues from exactly where it left off.

```
Normal execution:
  detect pod issue -> diagnose with LLM -> apply fix -> done

Worker crashes after diagnosis:
  detect pod issue -> diagnose with LLM -> [CRASH]

  [new worker picks up]
  detect pod issue (replayed) -> diagnose with LLM (replayed, uses cached result) -> apply fix -> done
```

No re-diagnosis. No lost state. No duplicate actions.

This is why Module 5 uses Temporal. KubeHealer isn't a script that runs and hopes for the best -- it's a durable workflow that survives failures.

### Why Not Just Use Try/Except?

Try/except handles errors within a running process. It can't help when the process itself dies. Temporal handles both:

| Failure | Try/Except | Temporal |
|---------|-----------|----------|
| API returns error | Catches it | Retries automatically |
| LLM times out | Catches it | Retries with backoff |
| Worker process crashes | Lost everything | Resumes from last checkpoint |
| Network partition | Depends | Retries when network recovers |
| Partial completion | No tracking | Knows what finished, resumes the rest |

## What's Next

In Module 5, you'll build **KubeHealer** -- a self-healing Kubernetes agent that:

- Watches for broken pods in your cluster
- Diagnoses the root cause using an LLM
- Takes safe remediation actions (restart, scale, adjust resources, rollback)
- Survives crashes and resumes mid-workflow using Temporal
- Logs every decision in an auditable workflow history

Everything from Day 1 (LLM calls, tool-calling agents, Kubernetes tools) comes together in one system. The concepts from this module (guardrails, durability, AIOps patterns) are what make it production-grade.

---

Next: **[Module 5 -- KubeHealer](../module-5/)**
