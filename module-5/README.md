# Module 5 -- KubeHealer

This is the flagship project. Everything from Day 1 comes together here -- LLM tool-calling, Kubernetes operations, and now Temporal for durable execution.

KubeHealer is an AI agent that finds broken Kubernetes pods, diagnoses them with Claude, and fixes them automatically. Every step runs inside Temporal workflows, so the agent is crash-proof, retryable, and fully observable.

**Repo:** https://github.com/TrainWithShubham/kubehealer

## What You'll Learn

- **Temporal workflows** -- durable execution that survives crashes. If the worker dies mid-diagnosis, it picks up exactly where it left off.
- **Claude tool-calling** -- the LLM doesn't just explain problems. It picks remediation actions (restart pod, fix image, adjust resources) and we execute them.
- **Crash recovery** -- kill the worker mid-workflow, restart it, watch it resume. This is the key demo.
- **Audit trail** -- every Claude call, every tool use, every fix is recorded in Temporal's event history. Open the UI and see exactly what the agent did.

## Architecture

```
CLI (you type here)
  |
  v
Temporal Workflow (ConversationWorkflow)
  |
  +-- activity: call_claude (sends your message to Claude)
  +-- activity: list_pods / get_pod_details / get_pod_logs (Claude's tool calls)
  +-- activity: call_claude (Claude sees tool results, responds)
  +-- activity: scan_cluster -> diagnose_pod -> execute_fix (healing flow)
  |
  v
Kubernetes API (applies the fix)
```

Every box above is a Temporal activity -- individually retryable, observable in the UI, with its own timeout.

## What Gets Fixed

| Broken App | Problem | AI Diagnosis | Auto-Fix |
|---|---|---|---|
| web-app | Image "nginx:latestt" (typo) | Detects typo in image name | Patches to nginx:latest |
| memory-hog | 10Mi memory limit + stress 100M | OOMKilled | Patches to 256Mi |
| config-app | Missing ConfigMap | Cannot auto-fix | Skips with explanation |

The agent knows its limits. config-app needs a ConfigMap created -- that's beyond what a pod patch can do, so the agent skips it and tells you why.

## Prerequisites

You need one new thing for this module:

**Temporal CLI** -- install it:

```bash
# macOS
brew install temporal

# Linux
curl -sSf https://temporal.download/cli.sh | sh
```

Verify:

```bash
temporal --version
```

You also need an **Anthropic API key**. Get one at https://console.anthropic.com/

## Setup

### Step 1: Clone KubeHealer

```bash
cd ~
git clone https://github.com/TrainWithShubham/kubehealer.git
cd kubehealer
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Set your API key

```bash
cp .env.example .env
```

Edit `.env` and paste your Anthropic API key.

### Step 4: Create the cluster and deploy broken apps

**Terminal 1:**

```bash
./setup.sh
```

This creates a Kind cluster called `kubehealer` and deploys 3 intentionally broken apps. You should see:

```
Pod status:
  web-app-xxx       0/1     ErrImagePull
  memory-hog-xxx    0/1     CrashLoopBackOff
  config-app-xxx    0/1     CreateContainerConfigError
```

### Step 5: Start Temporal

**Terminal 2:**

```bash
temporal server start-dev
```

Wait for "Temporal server is running". The UI will be at http://localhost:8233

### Step 6: Start the worker

**Terminal 3:**

```bash
python worker.py
```

You should see:

```
[OK] Anthropic API key
[OK] Kubernetes cluster

KubeHealer worker started. Waiting for tasks...
```

### Step 7: Start the CLI

**Terminal 4:**

```bash
python cli.py
```

You're in.

## Demo 1: Diagnose and Fix

In the CLI, start by exploring:

```
you> how many pods are running?
```

The agent calls `list_pods` and shows you the cluster status.

```
you> what's wrong with web-app?
```

The agent calls `get_pod_details`, reads the events, and spots the image typo.

```
you> show me the logs for memory-hog
```

The agent calls `get_pod_logs` and shows the OOMKill.

Now heal everything:

```
you> heal my cluster
```

The agent scans all pods, diagnoses each one, and presents its findings with severity, root cause, and proposed fix.

```
you> approve all fixes
```

The agent patches web-app's image and memory-hog's resource limits. config-app gets skipped (needs a ConfigMap that doesn't exist).

Verify:

```bash
kubectl get pods
```

web-app and memory-hog should be Running. config-app is still broken (expected).

### Fix config-app manually

The agent told you config-app needs a ConfigMap. Create it:

```bash
kubectl create configmap app-config --from-literal=APP_ENV=production --from-literal=APP_DEBUG=false
kubectl rollout restart deployment config-app
```

Now all 3 pods should be healthy.

## Demo 2: Crash Recovery

This is the key Temporal demo. We'll prove the agent survives crashes.

### Step 1: Redeploy broken apps

```bash
./setup.sh
```

### Step 2: Start healing

In the CLI:

```
you> heal my cluster
```

Watch the agent start scanning and diagnosing.

### Step 3: Kill the worker

While the agent is mid-diagnosis, go to Terminal 3 (worker) and press **Ctrl+C**.

The workflow is now stuck. Open http://localhost:8233 -- you'll see the workflow in "Running" state with some activities completed and the current one pending.

### Step 4: Restart the worker

```bash
python worker.py
```

Go back to the Temporal UI. The workflow resumes immediately. Activities that already completed (scan, some diagnoses) are NOT re-executed -- Temporal replays them from cached results. Only the remaining work runs.

The CLI gets the response as if nothing happened.

This is durable execution. The agent's state lives in Temporal, not in the Python process.

### Bonus: Kill the CLI

You can also kill the CLI (Ctrl+C) and restart it:

```bash
python cli.py
```

It reconnects to the same conversation. Your chat history is preserved.

## Demo 3: Temporal UI

Open http://localhost:8233 in your browser.

Click on any completed workflow. Go to the History tab. You'll see every event:

- `WorkflowExecutionStarted`
- `ActivityTaskScheduled` (call_claude)
- `ActivityTaskCompleted` (Claude's response)
- `ActivityTaskScheduled` (list_pods -- Claude called a tool)
- `ActivityTaskCompleted` (pod list returned)
- `ActivityTaskScheduled` (call_claude -- with tool result)
- `ActivityTaskCompleted` (Claude's final answer)
- ...and so on for every interaction

This is your audit trail. Every Claude call, every tool invocation, every fix -- all recorded with zero custom logging code. If someone asks "what did the AI agent do to our cluster?", the answer is in the workflow history.

## How It Connects to Module 4

Remember the concepts from Module 4:

**Guardrails (Kiro incident):** KubeHealer has a constrained action space -- only 4 possible actions (restart_pod, fix_image, patch_resources, skip). No arbitrary kubectl commands. The agent asks for approval before executing. Compare this to AWS Kiro, which had unbounded production access and deleted an environment.

**Durability (Temporal):** Module 4 showed the problem: naive agents lose state on crash. KubeHealer proves the solution: every step is a Temporal activity, every result is persisted, crashes are invisible to the workflow.

**Alert fatigue:** Module 4 talked about thousands of alerts per day. KubeHealer doesn't just alert -- it diagnoses and fixes. The human only needs to approve.

## Tech Stack

| Component | Role |
|-----------|------|
| Temporal | Durable workflow orchestration |
| Claude (Sonnet 4) | LLM diagnosis + conversational agent |
| Kubernetes | Target environment |
| Kind | Local K8s cluster |
| Python 3.11+ | Everything glued together |

## Cleanup

```bash
kind delete cluster --name kubehealer
```

Stop Temporal (Ctrl+C in Terminal 2), worker (Ctrl+C in Terminal 3).

## Experiment

- Change the broken apps in `chaos/` to create different failures
- Add a new remediation action (e.g., scale a deployment)
- Try `python starter.py` for auto-heal mode (no interaction needed)
- Modify the system prompt in the chat activities to make the agent more/less conservative
- Run `kubectl get pods -w` in a separate terminal to watch pods heal in real time

---

Next: **[Module 6 -- Build Your Own AIOps Agent](../module-6/)**
