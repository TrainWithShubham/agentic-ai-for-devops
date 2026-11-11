<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-Local_LLM-000000?style=for-the-badge&logo=ollama&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" />
  <img src="https://img.shields.io/badge/Temporal-000000?style=for-the-badge&logo=temporal&logoColor=white" />
</p>

# Agentic AI for DevOps

> Build AI agents that automate real DevOps infrastructure tasks — from kubectl error explanations to a self-healing Kubernetes system.

A 2-day hands-on course by [Shubham Londhe](https://github.com/LondheShubham153) / [TrainWithShubham](https://www.youtube.com/@TrainWithShubham)

---

## The Journey

You start with zero LLM experience and end up building **KubeHealer** — an AI agent that detects broken Kubernetes pods, diagnoses the root cause, and fixes them automatically.

### Day 1 — Foundations

| Module | What You'll Build |
|--------|-------------------|
| [Module 0 — Know Before You Go](module-0/) | Set up your environment and verify everything works |
| [Module 1 — Docker Error Explainer](module-1/) | Paste a Docker error, get a human-readable fix (your first LLM tool) |
| [Module 2 — Docker Troubleshooter Agent](module-2/) | An AI agent that inspects containers and diagnoses crashes on its own |
| [Module 3 — Multi-Tool DevOps Agent + MCP](module-3/) | Combine Docker + K8s tools, intro to LangChain and MCP |

### Day 2 — Production-Grade Agents

| Module | What You'll Build |
|--------|-------------------|
| [Module 4 — AIOps Demystified](module-4/) | The AIOps landscape, guardrails, and why durability matters |
| [Module 5 — KubeHealer](module-5/) | Self-healing K8s agent with Temporal and Claude ([separate repo](https://github.com/TrainWithShubham/kubehealer)) |
| [Module 6 — Build Your Own AIOps Agent](module-6/) | CI/CD Failure Analyzer — diagnose GitHub Actions failures with an AI agent |

---

## Prerequisites

| Tool | Why |
|------|-----|
| **Docker** | We build and troubleshoot containers |
| **kubectl** | We talk to Kubernetes clusters |
| **Kind** | Local K8s clusters for testing |
| **Python 3.10+** | All code is Python |
| **Ollama** | Run LLMs locally, no API keys needed |
| **Temporal CLI** | Durable workflow execution (Module 5) |
| **gh CLI** | GitHub CLI for CI/CD analysis (Module 6) |
| **Anthropic API key** | Claude AI for KubeHealer (Module 5) |

Already have Docker, kubectl, and Kind? Head to **[Module 0](module-0/)** to set up the rest.

---

## Quick Start

```bash
git clone https://github.com/trainwithshubham/agentic-ai-for-devops.git
cd agentic-ai-for-devops

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 module-0/verify_setup.py
```

See **[Module 0](module-0/)** for the full step-by-step setup.

---

## Tech Stack

| Category | Tools |
|----------|-------|
| Language | Python 3.10+ |
| LLM (Day 1) | Ollama + Gemma 4 (local, free) |
| LLM (Day 2) | Anthropic Claude (KubeHealer) |
| Containers | Docker |
| Orchestration | Kubernetes (Kind) |
| Agent Framework | LangChain |
| Durable Execution | Temporal |
| MCP | FastMCP |

---

<p align="center">
  Built by <a href="https://github.com/LondheShubham153">Shubham Londhe</a> for the <a href="https://www.youtube.com/@TrainWithShubham">TrainWithShubham</a> community
</p>
