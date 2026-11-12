import { demos } from "./demos.js";
import { toolNames, eventNames, explainError } from "./learning.js";
// The console renders public events and configuration. It never runs tools or stores model keys.
const $ = (q, root = document) => root.querySelector(q);
const $$ = (q, root = document) => [...root.querySelectorAll(q)];
const esc = (value = "") =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (ch) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        ch
      ],
  );
const icon = (name) =>
  `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;
const json = (value) => JSON.stringify(value, null, 2);
const badge = (text, tone = "") =>
  `<span class="badge ${tone}">${esc(text)}</span>`;
const names = { bagha: "Bagha", nattu: "Nattu Kaka", jethalal: "Jethalal" };
const presets = [
  [
    "Find the problem",
    "Customers cannot pay at Gada Electronics. Can you check what is wrong?",
  ],
  [
    "Suggest a fix",
    "Checkout is not working. Suggest a fix, but ask a person before changing anything.",
  ],
];
const S = {
  demo: null,
  config: null,
  harness: null,
  mcp: null,
  actor: null,
  token: "",
  expires: 0,
  epoch: 0,
  run: null,
  events: [],
  sources: [],
  busy: false,
  deciding: false,
  tab: "harness",
  ragTab: "corpus",
  ragProbe: null,
  ragQuery: "",
  selectedTool: null,
  error: "",
  controller: null,
  filter: "all",
};
class StaleSession extends Error {}
let toastTimer;
function read(key, fallback) {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? fallback;
  } catch {
    return fallback;
  }
}
function write(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* Storage is optional. */
  }
}
function notice(message, error = false) {
  const node = $("#toast");
  node.textContent = error ? explainError(message).join(" ") : message;
  node.classList.toggle("error", error);
  node.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (node.hidden = true), 6500);
}
function history() {
  return read("runbookops-runs:" + (S.actor?.user || "bagha"), []);
}
function runStatus() {
  if (S.busy) return ["Running", "model"];
  if (S.run?.health?.http_status === 200) return ["Recovered", "success"];
  const status = S.run?.proposal?.status;
  if (status === "pending") return ["Approval pending", "warn"];
  if (status === "approved") return ["Resume execution", "warn"];
  if (status === "rejected") return ["Rejected", ""];
  if (S.error || S.run?.error) return ["Stopped", "error"];
  return [S.run ? "Completed" : "Idle", ""];
}
function remember() {
  if (!S.actor || !S.run?.incident_id) return;
  const record = {
    id: S.run.incident_id,
    at: Date.now(),
    status: runStatus()[0],
  };
  write(
    "runbookops-runs:" + S.actor.user,
    [record, ...history().filter((row) => row.id !== record.id)].slice(0, 20),
  );
}
async function renew() {
  if (!S.config.demo_auth)
    throw new Error("Connect again with a fresh application access token.");
  const epoch = S.epoch;
  const response = await fetch("/ui/session", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-RunbookOps-Demo": "true",
    },
    body: JSON.stringify({ user: S.actor?.user || $("#persona").value }),
  });
  const data = await response.json();
  if (epoch !== S.epoch) throw new StaleSession();
  if (!response.ok) throw new Error(data.detail || "Development login failed.");
  S.token = data.access_token;
  S.expires = Date.now() + data.expires_in * 1000;
  return data;
}
async function authorized() {
  if (!S.token) throw new Error("Connect an application identity first.");
  if (S.expires && S.expires < Date.now() + 15000) await renew();
  return S.token;
}
async function api(path, method = "GET", body, retry = true) {
  const epoch = S.epoch;
  const token = await authorized();
  const response = await fetch(path, {
    method,
    headers: {
      Authorization: "Bearer " + token,
      ...(body === undefined ? {} : { "Content-Type": "application/json" }),
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const data = await response.json();
  if (epoch !== S.epoch) throw new StaleSession();
  if (response.status === 401 && retry && S.config.demo_auth) {
    await renew();
    return api(path, method, body, false);
  }
  if (!response.ok) {
    const message = Array.isArray(data.detail)
      ? data.detail.map((row) => row.msg).join("; ")
      : data.detail;
    const error = new Error(message || "HTTP " + response.status);
    error.status = response.status;
    throw error;
  }
  return data;
}
function resetRun() {
  S.run = null;
  S.events = [];
  S.selectedTool = null;
  S.ragProbe = null;
  S.error = "";
}
async function connect(user) {
  if (S.busy || S.deciding) {
    $("#persona").value = S.actor.user;
    notice("Stop or finish the active operation before switching.");
    return;
  }
  if (!S.config.demo_auth) {
    $("#persona").value = S.actor?.user || "bagha";
    connectionDialog();
    return;
  }
  const id = S.run?.incident_id;
  S.epoch++;
  const epoch = S.epoch;
  S.actor = null;
  S.token = "";
  S.sources = [];
  S.harness = null;
  S.mcp = null;
  resetRun();
  $("#detail-dialog").close();
  $("#dialog-content").textContent = "";
  $("#persona").value = user;
  $("#persona").disabled = true;
  render();
  try {
    const identity = await renew();
    if (epoch !== S.epoch) return;
    S.actor = {
      user: identity.user,
      role: identity.role,
      scopes: identity.scopes,
    };
    write("runbookops-persona", user);
    const [harness, knowledge] = await Promise.all([
      api("/harness"),
      api("/knowledge"),
    ]);
    S.harness = harness;
    S.sources = knowledge.sources;
    if (id) {
      try {
        await loadRun(id);
      } catch (error) {
        if (!(error instanceof StaleSession))
          notice("The previous incident is not accessible to this persona.");
      }
    }
    render();
  } catch (error) {
    if (!(error instanceof StaleSession)) {
      S.error = error.message;
      render();
      notice(error.message, true);
    }
  } finally {
    $("#persona").disabled = false;
  }
}
function drawSessions() {
  const records = history();
  $("#session-list").innerHTML = records.length
    ? records
        .map(
          (row) =>
            `<button class="session-item ${S.run?.incident_id === row.id ? "current" : ""}" data-action="load" data-id="${esc(row.id)}"><strong>Checkout</strong><small>${esc(row.id.replace("gada-", ""))}</small><small>${esc(row.status)} · ${esc(new Date(row.at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }))}</small></button>`,
        )
        .join("")
    : '<p class="small muted">No sessions in this browser yet.</p>';
}
function messageHeader(name, avatar, detail = "") {
  return `<div class="message-header"><span class="message-avatar">${esc(avatar)}</span>${esc(name)}<small>${esc(detail)}</small></div>`;
}
function errorCard(raw) {
  const [title, next] = explainError(raw);
  return `<section class="friendly-error" role="alert"><strong>${esc(title)}</strong><p>${esc(next)}</p><details><summary>Technical details</summary><pre>${esc(raw)}</pre></details></section>`;
}
function turnContent(event, index) {
  const calls = event.requested_tools || [];
  const action = calls.length
    ? "Next: " + calls.map((c) => toolNames[c.name] || c.name).join(" · ")
    : "AI reply received";
  return `<article class="message model">${messageHeader(event.mode === "offline" ? "Practice agent" : "AI", "A", "step " + (event.turn || "—"))}<p class="ai-choice">${esc(action)}</p><details class="response-details" data-key="response-${index}"><summary>Read reply & technical details</summary>${event.content ? `<div class="message-body">${esc(event.content)}</div>` : '<p class="small muted">This reply requested tools without a written answer.</p>'}<div class="turn-meta">${badge(event.model || event.mode, "model")}<span>${event.duration_ms !== undefined ? (event.duration_ms / 1000).toFixed(1) + "s" : ""}</span>${event.usage ? `<span>${esc(event.usage.total_tokens ?? (event.usage.prompt_tokens || 0) + (event.usage.completion_tokens || 0))} tokens</span>` : ""}<button class="link-button" data-action="event" data-index="${index}">Full response</button></div></details></article>`;
}
function toolContent(event, index) {
  const r = event.result || {};
  const summary =
    event.tool === "get_service_health"
      ? r.http_status === 200
        ? "Checkout is working (HTTP 200)."
        : `Checkout is not working (HTTP ${r.http_status ?? "unknown"}).`
      : event.tool === "search_runbooks"
        ? `${r.results?.length || 0} matching notes · ${r.cache_hit ? "reused saved results" : "new search"}`
        : event.tool === "prepare_change"
          ? r.id
            ? "Fix suggested. Nothing changed yet."
            : "No fix was saved."
          : event.tool === "get_recent_deployments"
            ? "Read the latest deployment record."
            : event.tool === "get_recent_logs"
              ? "Read the service's recent error messages."
              : "Result received.";
  return `<details class="tool-call" data-key="tool-${index}"><summary>${icon(event.tool === "search_runbooks" ? "book" : "terminal")}<span class="tool-label"><strong>${esc(toolNames[event.tool] || event.tool)}</strong><small>${esc(r.error ? explainError(r.error)[0] : summary)}</small></span><span class="tool-time">${event.duration_ms ?? "—"} ms ${icon("chevron")}</span></summary><div class="tool-content"><div class="section-kicker">TECHNICAL DETAILS · ${esc(event.tool)}</div><p class="small muted">What the tool received</p><pre>${esc(json(event.arguments))}</pre><p class="small muted">What the tool returned</p><pre>${esc(json(r))}</pre><button class="quiet-button" data-action="inspect-tool" data-index="${index}">Open ${event.tool === "search_runbooks" ? "company notes" : "tool details"} ${icon("up-right")}</button></div></details>`;
}
function approval() {
  const p = S.run?.proposal;
  if (!p) return "";
  const plan = p.plan;
  const expired = Date.now() / 1000 >= p.expires;
  const pending = p.status === "pending" && !expired;
  const approver = S.actor?.scopes.includes("approve");
  return `<section class="approval-card" aria-label="Review the suggested fix"><div class="approval-top"><span>${icon("shield")} Review the suggested fix</span>${badge(expired && p.status === "pending" ? "Expired" : p.status, p.status === "applied" ? "success" : "warn")}</div><div class="approval-body"><span class="eyebrow">Payment service address · ${esc(plan.environment)}</span><p class="fix-explanation">The suggested change replaces the payment address below. This only affects the practice checkout.</p><div class="diff"><div class="removed">− ${esc(plan.before)}</div><div class="added">+ ${esc(plan.after)}</div></div><div class="plan-details"><p><strong>Risk:</strong> ${esc(plan.risk)}</p><p><strong>Check it worked:</strong> ${esc(plan.validation)}</p><p><strong>Undo if needed:</strong> <code>${esc(plan.rollback?.value)}</code></p><p><strong>Evidence:</strong> ${esc(plan.evidence.join(", "))}</p><p><strong>Expires:</strong> ${esc(new Date(p.expires * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }))}</p></div>${pending && approver ? `<label class="review-check"><input id="review-check" type="checkbox">I have checked the change, risk, and how to undo it.</label><div class="button-row"><button data-action="approve" class="primary-button" disabled>Approve & run ${icon("check")}</button><button data-action="reject" class="quiet-button danger">Reject</button></div>` : pending ? `<p class="inline-notice warn">${esc(names[S.actor?.user] || "This persona")} can prepare a proposal, but cannot approve it.</p><div class="button-row"><button class="quiet-button" data-action="review-persona">Review as Jethalal ${icon("arrow")}</button><button class="link-button" data-action="denial">Try approving as Bagha</button></div>` : p.status === "approved" && approver ? `<p class="small muted">The decision is stored. Resume the saved execution to finish verification.</p><button class="primary-button" data-action="resume">Resume execution</button>` : `<p class="small muted">${p.status === "applied" ? "Applied after approval. Checkout was checked again." : p.status === "rejected" ? "Rejected. The simulator configuration remains unchanged." : "This proposal cannot execute. Start a fresh incident."}</p>`}</div><details class="approval-identity" data-key="approval-hash"><summary>Technical details · approval ID</summary><div class="hash-label">SHA-256 ${esc(p.hash)}</div></details></section>`;
}
function drawConversation() {
  const node = $("#conversation");
  const follow = node.scrollHeight - node.scrollTop - node.clientHeight < 70;
  const top = node.scrollTop;
  const open = new Set(
    $$("details[open]", node).map((item) => item.dataset.key),
  );
  if (!S.run) {
    node.innerHTML = `<div class="opening"><div class="empty-graphic" aria-hidden="true"><span>${icon("terminal")}</span><i></i><span>${icon("cpu")}</span><i></i><span>${icon("network")}</span></div><h1>Let’s check checkout.</h1><p class="opening-note">The payment step at Gada Electronics is not working.</p><div class="task-presets">${presets.map((p, i) => `<button class="task-preset" data-action="preset" data-index="${i}">${icon(i ? "shield" : "activity")}${esc(p[0])}</button>`).join("")}</div><span class="empty-mode">${badge(S.config?.mode === "offline" ? "Offline practice" : "Live model", "model")}${badge("Local simulator")}</span>${S.error ? errorCard(S.error) : ""}</div>`;
  } else {
    let content = `<article class="message user">${messageHeader(names[S.run.user || S.actor?.user] || "You", "U", "task")}<div class="message-body">${esc(S.run.question || "Investigate checkout.")}</div></article>`;
    for (let index = 0; index < S.events.length; index++) {
      const event = S.events[index];
      if (event.kind === "model") content += turnContent(event, index);
      if (event.kind === "tool") content += toolContent(event, index);
    }
    if (S.busy)
      content += `<div class="pending-indicator"><span class="spinner"></span>Checking the problem…</div>`;
    if (!S.busy && S.run.diagnosis)
      content += `<article class="message app">${messageHeader("What we found", "H", "before approval")}<div class="message-body">${S.run.proposal ? "The tool results support changing the payment address. A fix is ready for a person to review." : "No fix was prepared. Open the findings to see what the AI checked."}</div><details class="response-details" data-key="diagnosis"><summary>Read the findings</summary><div class="message-body">${esc(S.run.diagnosis)}</div></details></article>`;
    if (S.error || S.run.error) content += errorCard(S.error || S.run.error);
    if (!S.busy) content += approval();
    if (S.run.result)
      content += `<article class="message app">${messageHeader("Executor", "E", "application result")}<div class="message-body">${S.run.health?.http_status === 200 ? "Checkout is working again (HTTP 200). The approved fix was applied." : S.run.proposal?.status === "rejected" ? "Proposal rejected. No change was applied." : "Execution returned a result. Inspect saved state for details."}</div><div class="turn-meta"><button class="link-button" data-action="state">Inspect state & verification</button></div></article>`;
    node.innerHTML = content;
  }
  $$("details[data-key]", node).forEach((item) => {
    if (open.has(item.dataset.key)) item.open = true;
  });
  if (follow) node.scrollTop = node.scrollHeight;
  else node.scrollTop = top;
}
function values(rows) {
  return `<div class="key-values">${rows.map(([key, value]) => `<div class="kv"><span>${esc(key)}</span><strong>${esc(value)}</strong></div>`).join("")}</div>`;
}
function modelUsage() {
  const models = S.events.filter((event) => event.kind === "model");
  const usage = models.filter((event) => event.usage);
  const tokens = usage.reduce(
    (sum, event) =>
      sum +
      (event.usage.total_tokens ??
        (event.usage.prompt_tokens || 0) +
          (event.usage.completion_tokens || 0)),
    0,
  );
  const costs = usage
    .map((event) => event.usage.cost)
    .filter((value) => value !== undefined && value !== null);
  return {
    calls: models.length,
    tokens: usage.length ? tokens.toLocaleString() : "—",
    cost:
      models.length && costs.length === models.length
        ? "$" + costs.reduce((a, b) => a + Number(b), 0).toFixed(4)
        : "Not reported",
  };
}
function demoLibrary() {
  const starters = [0, 1, 6, 4];
  const card = (i, n) => {
    const d = demos[i];
    return `<button class="demo-card" data-action="demo-select" data-index="${i}"><span class="demo-number">${String(n).padStart(2, "0")} ${icon(d.icon)}</span><strong>${esc(d.title)}</strong><span>${esc(d.topic)}</span><small>${d.kind === "task" ? "Fill in a task" : d.kind === "rag" ? "Open a search" : "Take a look"}</small></button>`;
  };
  dialog(
    "Try an example",
    "START HERE",
    `<p class="dialog-lead">Choose one, then press Run or Search. Start with the first example.</p><div class="demo-grid">${starters.map((i, n) => card(i, n + 1)).join("")}</div><details class="more-demos"><summary>More topics · caching, permissions, MCP, and saved work</summary><div class="demo-grid">${demos
      .map((_, i) => i)
      .filter((i) => !starters.includes(i))
      .map((i, n) => card(i, n + 5))
      .join(
        "",
      )}</div></details><p class="small muted">Offline practice follows a fixed example. Use a live model to try different instructions. All fixes affect the practice checkout only.</p>`,
  );
}
function drawDemo() {
  const d = S.demo;
  const panel = $("#demo-cue");
  panel.hidden = !d;
  if (!d) return;
  panel.innerHTML = `<div><span class="demo-topic">${esc(d.topic)}</span><strong>${esc(d.title)}</strong><p>${esc(d.observe)}</p></div><button class="icon-button" data-action="demo-dismiss" aria-label="Hide demo guidance">${icon("close")}</button>`;
}
function operationView() {
  const e = S.events.at(-1);
  let title = "Ready to help",
    detail = "Choose an example, then press Run.",
    symbol = "terminal";
  if (e) {
    title =
      {
        model_request: "The AI is choosing the next check",
        model: "The AI replied",
        tool: toolNames[e.tool] || "A check finished",
        mcp_connected: "The tools are connected",
        proposal_prepared: "A fix is ready to review",
        approval_denied: "Approval denied",
        approval_decision: "Human decision recorded",
        change_applied: "Change applied",
        verification: "Verification recorded",
        node_started: "Workflow node started",
        node_completed: "Workflow node completed",
        investigation_finished: "Investigation finished",
      }[e.kind] || e.kind.replaceAll("_", " ");
    detail = describe(e);
    symbol =
      group(e) === "model"
        ? "cpu"
        : group(e) === "approval"
          ? "shield"
          : "terminal";
  }
  if (S.run && !S.busy && !S.run.proposal) {
    title = "Checks finished";
    detail = "Read the findings, or ask for a suggested fix.";
  }
  if (S.run?.waiting_for_approval && !S.busy) {
    title = "Waiting for human approval";
    detail = "Review the exact change before execution.";
    symbol = "shield";
  }
  if (S.run?.health?.http_status === 200) {
    title = "Checkout is working again";
    detail = "Approved change applied and verified.";
    symbol = "check";
  }
  if (S.error || S.run?.error) {
    title = "Operation stopped";
    [title, detail] = explainError(S.error || S.run.error);
    symbol = "stop";
  }
  if (S.deciding) {
    title = "Submitting human decision";
    detail = "Waiting for the saved execution result.";
    symbol = "shield";
  }
  return `<div class="operation-banner ${S.busy || S.deciding ? "running" : ""}"><span class="operation-icon">${icon(symbol)}</span><div><small>${S.busy ? "RUNNING · LATEST EVENT" : "LATEST OPERATION"}</small><strong>${esc(title)}</strong><span>${esc(detail)}</span></div></div>`;
}
function graphView(harness) {
  const connected = S.events.some((e) => e.kind === "mcp_connected");
  const retrievedCount = retrieved()?.results?.length;
  const pending = S.run?.waiting_for_approval;
  const done = S.run?.health?.http_status === 200;
  function node(css, title, symbol, meta, action, section = "") {
    return `<button class="map-node ${css}" data-action="${action}" ${section ? `data-section="${section}"` : ""}><span class="map-icon">${icon(symbol)}</span><strong>${title}</strong><small>${esc(meta)}</small></button>`;
  }
  return `<div class="harness-map" aria-label="Agent components and execution connections"><svg class="map-lines" viewBox="0 0 600 300" preserveAspectRatio="none" aria-hidden="true"><defs><marker id="flow-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto-start-reverse"><path d="M0 0 6 3 0 6"/></marker></defs><path class="path-prompt" d="M174 73H225" marker-end="url(#flow-arrow)"/><path class="path-tools" d="M374 64H425" marker-end="url(#flow-arrow)"/><path class="path-result" d="M425 91H374" marker-end="url(#flow-arrow)"/><path class="path-rag" d="M500 122V176" marker-end="url(#flow-arrow)"/><path class="path-review" d="M300 122V176" marker-end="url(#flow-arrow)"/><path class="path-execute" d="M225 225H174" marker-end="url(#flow-arrow)"/></svg>${node("map-prompt", "System prompt", "file", "Rules", "prompt")}${node("map-model " + (S.busy && S.events.at(-1)?.kind === "model_request" ? "active" : ""), "Model", "cpu", S.config.mode === "offline" ? "Fixture" : S.config.mode, "model")}${node("map-tools " + (connected ? "visited" : ""), "MCP tools", "network", connected ? "MCP · connected" : "MCP connection", "inspect-section", "mcp")}${node("map-rag " + (retrievedCount ? "visited" : ""), "RAG", "database", retrievedCount !== undefined ? retrievedCount + " notes · RAG" : S.sources.length + " files · RAG", "inspect-section", "rag")}${node("map-review " + (pending ? "waiting" : "") + (done ? " visited" : ""), "Approval", "shield", pending ? "Waiting" : S.run?.proposal?.status || "A person decides", "approval-focus")}${node("map-execute " + (done ? "visited" : ""), "Execute", "terminal", done ? "HTTP 200" : S.run?.result ? "Verified" : "Idle", "inspect-section", "state")}</div>`;
}
function harnessView() {
  const h = S.harness;
  if (!h) return '<p class="small muted">Connect to inspect.</p>';
  return `${operationView()}${graphView(h)}<div class="harness-metrics"><span>${icon("cpu")}<strong>${modelUsage().calls}/${h.limits.model_calls}</strong><small>${S.config.mode === "offline" ? "Model steps" : "Model calls"}</small></span><span>${icon("terminal")}<strong>${S.events.filter((e) => e.kind === "tool").length}/${h.limits.tool_calls}</strong><small>Tool calls</small></span><span>${icon("clock")}<strong>${h.limits.timeout_seconds}s</strong><small>Time limit</small></span></div><details class="inspect-details" data-key="system-prompt"><summary>${icon("file")} System prompt</summary><div><p class="prompt-text">${esc(h.system_prompt)}</p></div></details><details class="inspect-details" data-key="execution"><summary>${icon("cpu")} Model & limits</summary><div>${values(
    [
      ["Model", h.routing.diagnose],
      ["Summary", h.routing.summarize],
      ["Output tokens", h.limits.output_tokens],
      ["Checkpoint", h.checkpoint],
    ],
  )}</div></details><details class="inspect-details" data-key="graph-json"><summary>${icon("code")} LangGraph</summary><div><div class="flow-nodes">${h.graph.nodes
    .filter((n) => !n.id.startsWith("__"))
    .map(
      (n, i) =>
        `${i ? icon("chevron") : ""}<span class="flow-node">${esc(n.id)}</span>`,
    )
    .join(
      "",
    )}</div><pre class="graph-json">${esc(json(h.graph))}</pre></div></details>`;
}
function retrieved() {
  return S.events
    .filter(
      (event) => event.kind === "tool" && event.tool === "search_runbooks",
    )
    .at(-1)?.result;
}
function ragView() {
  const rag = S.harness?.rag;
  if (!rag) return '<p class="small muted">Connect to inspect.</p>';
  const result = S.ragProbe || retrieved();
  return `<div class="component-strip">${icon("database")}<strong>Company notes</strong>${badge(rag.embedding)}<span>${S.sources.length} sources</span></div><form id="rag-form" class="search-form"><label class="sr-only" for="rag-query">Retrieval probe query</label><input id="rag-query" required maxlength="1200" placeholder="Ask about the company notes…" value="${esc(S.ragQuery)}"><button class="quiet-button" type="submit" aria-label="Retrieve chunks">${icon("search")}</button></form><div class="inspector-subtabs"><button data-action="rag-results" class="${S.ragTab === "results" ? "active" : ""}">Chunks ${result?.results?.length ?? 0}</button><button data-action="rag-corpus" class="${S.ragTab === "corpus" ? "active" : ""}">Files ${S.sources.length}</button></div>${S.ragTab === "results" ? (result ? `<div class="result-tags">${badge(S.ragProbe ? "Probe" : "Agent context")}${badge(result.cache_hit ? "Saved result · cache hit" : "New search · fresh")}</div>${result.results.length ? result.results.map((item) => `<article class="rag-excerpt"><button class="text-button" data-action="source" data-id="${esc(item.source)}">${icon("file")}${esc(item.source)} ${icon("up-right")}</button><p>${esc(item.text)}</p><small>${esc(item.location)} · ${esc(item.similarity)} similarity</small></article>`).join("") : '<p class="small muted">No matches.</p>'}` : '<div class="visual-empty">' + icon("search") + "<span>Ask a question above, then press Search.</span></div>") : S.sources.map((item) => `<button class="source-row" data-action="source" data-id="${esc(item.id)}"><span class="file-format">${esc(item.file.split(".").at(-1).toUpperCase())}</span><div><strong>${esc(item.title)}</strong><small>v${esc(item.version)}${item.access === "approver" ? " · Approver" : ""}</small></div>${icon("chevron")}</button>`).join("")}<details class="inspect-details" data-key="rag-config"><summary>${icon("code")} Retrieval config</summary><div>${values(
    [
      ["Embedding", rag.embedding_model],
      [
        "Chunk / overlap",
        rag.chunk_characters + " / " + rag.overlap_characters + " chars",
      ],
      ["Cache TTL", rag.cache_ttl_seconds + "s"],
      ["Filters", rag.filters.join(", ")],
    ],
  )}<p class="source-file">Cache: ${esc(rag.cache_scope.join(", "))}. Similarity is not confidence.</p></div></details>`;
}
function mcpView() {
  const discovery = S.mcp;
  return `<div class="component-strip">${icon("network")}<strong>Tool connections · MCP</strong>${badge(S.harness?.mcp.transport || "—")}<button class="icon-button" data-action="discover" aria-label="Discover MCP tools" title="Discover tools">${icon("refresh")}</button></div>${discovery?.loading ? '<div class="visual-empty"><span class="spinner"></span><span>Discovering…</span></div>' : discovery?.error ? errorCard(discovery.error) : discovery?.tools ? `<div class="result-tags">${badge(discovery.tools.length + " discovered", "success")}</div><div class="mcp-tool-grid">${discovery.tools.map((tool, i) => `<button class="mcp-tool-node" data-action="mcp-schema" data-index="${i}">${icon(tool.name === "search_runbooks" ? "database" : tool.name === "prepare_change" ? "shield" : "terminal")}<strong>${esc(toolNames[tool.name] || tool.name)}</strong>${icon("up-right")}</button>`).join("")}</div>` : '<div class="visual-empty">' + icon("network") + '<button class="quiet-button" data-action="discover">Find available tools</button></div>'}`;
}
function toolsView() {
  const event = S.selectedTool;
  return `<div class="component-strip">${icon("terminal")}<strong>Tools</strong>${badge((S.harness?.tools || []).length + " schemas")}</div>${event ? `<div class="tool-selected"><div class="section-kicker">${esc(event.tool)} · ${esc(event.duration_ms)} ms</div><details class="inspect-details" open><summary>Input</summary><pre>${esc(json(event.arguments))}</pre></details><details class="inspect-details"><summary>Output</summary><pre>${esc(json(event.result))}</pre></details></div>` : ""}<div class="tool-catalog">${(S.harness?.tools || []).map((tool) => `<details class="inspect-details schema-tool" data-key="schema-${tool.function.name}"><summary>${icon(tool.function.name === "search_runbooks" ? "database" : tool.function.name === "prepare_change" ? "shield" : "terminal")}<span>${esc(tool.function.name)}</span></summary><div><p class="schema-description">${esc(tool.function.description)}</p><pre>${esc(json(tool.function.parameters))}</pre></div></details>`).join("")}</div>`;
}
function stateView() {
  const run = S.run;
  return `<div class="component-strip">${icon("grid")}<strong>Saved work</strong>${badge(S.harness?.checkpoint || "SQLite")}<button class="icon-button" data-action="refresh" aria-label="Refresh saved state">${icon("refresh")}</button></div>${
    run
      ? `<div class="state-tiles"><span>${icon("activity")}<strong>${esc(run.health?.http_status || "—")}</strong><small>Checkout HTTP</small></span><span>${icon("shield")}<strong>${run.waiting_for_approval ? "Paused" : S.busy ? "Running" : "Settled"}</strong><small>Checkpoint</small></span></div><div class="inspect-section">${values(
          [
            ["Incident", run.incident_id || "Opening"],
            [
              "Next",
              run.pending_nodes?.join(", ") ||
                (S.busy ? "investigate" : "none"),
            ],
          ],
        )}</div><details class="inspect-details" data-key="state-json"><summary>${icon("code")} Technical details · saved state</summary><pre>${esc(json(run))}</pre></details>`
      : '<div class="visual-empty">' +
        icon("grid") +
        "<span>No active session.</span></div>"
  }`;
}
function drawInspector() {
  const node = $("#inspector-body");
  const top = node.scrollTop;
  const open = new Set(
    $$("details[open]", node).map((item) => item.dataset.key),
  );
  const functions = {
    harness: harnessView,
    rag: ragView,
    mcp: mcpView,
    tools: toolsView,
    state: stateView,
  };
  const introductions = {
    harness:
      "An agent checks tools and company notes to help with a task. A person approves any change.",
    rag: "RAG: find useful passages in company documents for the AI to read.",
    mcp: "MCP: a standard way for the app to discover and connect tools.",
    tools:
      "A tool is a function the AI can ask the app to run. Click one to see its inputs.",
    state:
      "Saved work keeps the task and approval record so you can open them again.",
  };
  node.innerHTML =
    `<p class="concept-intro">${esc(introductions[S.tab])}</p>` +
    functions[S.tab]();
  node.setAttribute("aria-labelledby", "tab-" + S.tab);
  $$("details[data-key]", node).forEach((item) => {
    if (open.has(item.dataset.key)) item.open = true;
  });
  node.scrollTop = top;
  $$("[data-tab]").forEach((tab) => {
    const selected = tab.dataset.tab === S.tab;
    tab.setAttribute("aria-selected", String(selected));
    tab.tabIndex = selected ? 0 : -1;
  });
}
function group(event) {
  if (["model", "model_request"].includes(event.kind)) return "model";
  if (["tool", "tool_error", "mcp_connected"].includes(event.kind))
    return "tool";
  if (
    [
      "approval_decision",
      "approval_denied",
      "proposal_prepared",
      "change_applied",
      "verification",
    ].includes(event.kind)
  )
    return "approval";
  return "state";
}
function describe(event) {
  if (event.kind === "model_request")
    return `Step ${event.turn} · choosing from ${event.tool_count} tools`;
  if (event.kind === "model")
    return `${event.model || event.mode} · ${event.requested_tools?.length ?? "—"} requested tools`;
  if (event.kind === "tool")
    return `${toolNames[event.tool] || event.tool} · ${event.duration_ms ?? "—"} ms`;
  if (event.kind === "mcp_connected")
    return `${event.transport} · ${event.tools?.length ?? 0} tools discovered`;
  if (event.kind === "approval_denied")
    return `${event.actor} lacks approval permission`;
  if (event.kind === "approval_decision")
    return `${event.actor || event.approver || "approver"} · ${event.status}`;
  if (event.kind === "verification")
    return `HTTP ${event.result?.health?.http_status || "—"} · applied=${event.result?.applied}`;
  if (event.kind === "node_started" || event.kind === "node_completed")
    return event.node;
  if (event.kind === "investigation_finished")
    return (
      event.error ||
      `${event.model_calls} model calls · ${event.proposal_id ? "proposal prepared" : "no proposal"}`
    );
  return event.proposal_id || event.actor || "";
}
function drawEvents() {
  const node = $("#event-list");
  const follow = node.scrollHeight - node.scrollTop - node.clientHeight < 40;
  const top = node.scrollTop;
  const filtered = S.events
    .map((event, index) => ({ event, index }))
    .filter(({ event }) => S.filter === "all" || group(event) === S.filter);
  node.innerHTML = filtered.length
    ? filtered
        .map(
          ({ event, index }) =>
            `<button class="event-row ${group(event)}" data-action="event" data-index="${index}"><time>${event.at ? esc(new Date(event.at * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })) : "—"}</time><span class="event-kind">${esc(eventNames[event.kind] || event.kind)}</span><span class="event-description">${esc(describe(event))}</span></button>`,
        )
        .join("")
    : '<p class="event-empty">' +
      (S.events.length ? "No matching events." : "Waiting for a task.") +
      "</p>";
  $("#event-count").textContent = S.events.length;
  if (follow) node.scrollTop = node.scrollHeight;
  else node.scrollTop = top;
}
function drawHeader() {
  const [label, tone] = runStatus();
  $("#run-status").className = "badge " + tone;
  $("#run-status").textContent = label;
  $("#session-id").textContent = "/ " + (S.run?.incident_id || "new task");
  $("#persona").disabled = S.busy || S.deciding;
  $("#send-button").hidden = S.busy;
  $("#stop-button").hidden = !S.busy;
  $("#task-input").disabled = S.busy;
  $("#new-session").disabled = S.busy || S.deciding;
  $("#new-task").disabled = S.busy || S.deciding;
  $("#runtime-status").textContent =
    `${S.config?.mode || "connecting"} / ${S.actor ? names[S.actor.user] + " · " + S.actor.role : "identity not connected"}`;
  const m = modelUsage();
  $("#usage-status").textContent = S.events.length
    ? `${m.calls} model ${S.config.mode === "offline" ? "steps" : "calls"} · ${m.tokens} tokens${S.config.mode === "offline" ? " · no inference" : m.cost === "Not reported" ? "" : " · " + m.cost}`
    : "Model keys stay on the server.";
  $("#composer-hint").textContent = S.busy
    ? "Running…"
    : "A person must approve any fix.";
}
function render() {
  drawHeader();
  drawDemo();
  drawSessions();
  drawConversation();
  drawInspector();
  drawEvents();
}
function inspect(tab) {
  S.tab = tab;
  drawInspector();
  if (matchMedia("(max-width:960px)").matches) setPane("inspect");
}
async function discover() {
  S.mcp = { loading: true };
  drawInspector();
  try {
    S.mcp = await api("/harness/mcp");
  } catch (error) {
    if (error instanceof StaleSession) return;
    S.mcp = { error: error.message };
  }
  if (S.tab === "mcp") drawInspector();
}
async function begin(question) {
  if (S.busy) return;
  if (!S.token) {
    connectionDialog();
    return;
  }
  question = question.trim();
  if (!question || question.length > 1200) return;
  resetRun();
  S.run = { question, user: S.actor.user, mode: S.config.mode };
  S.busy = true;
  S.controller = new AbortController();
  S.ragTab = "results";
  render();
  $("#conversation").scrollTop = 0;
  let complete = false;
  try {
    const token = await authorized();
    const response = await fetch("/investigations/stream", {
      method: "POST",
      headers: {
        Authorization: "Bearer " + token,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
      signal: S.controller.signal,
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "HTTP " + response.status);
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let pending = "";
    function entry(line) {
      if (!line.trim()) return;
      const row = JSON.parse(line);
      if (row.type === "incident") {
        S.run.incident_id = row.data.incident_id;
        remember();
      }
      if (row.type === "event") S.events.push(row.data);
      if (row.type === "complete") {
        S.run = row.data;
        complete = true;
      }
      if (row.type === "error")
        throw new Error(row.data.message || "Investigation failed.");
      render();
    }
    while (true) {
      const chunk = await reader.read();
      if (chunk.done) break;
      pending += decoder.decode(chunk.value, { stream: true });
      const lines = pending.split("\n");
      pending = lines.pop();
      for (const line of lines) entry(line);
    }
    pending += decoder.decode();
    if (pending.trim()) entry(pending);
    if (!complete)
      throw new Error(
        "The stream ended before completion. Open this incident again to inspect saved state.",
      );
  } catch (error) {
    S.error =
      error.name === "AbortError"
        ? "Investigation stopped. No unapproved change was executed."
        : error.message;
  } finally {
    S.busy = false;
    S.controller = null;
    remember();
    render();
    if (S.run?.proposal) notice("A fix is ready. A person needs to review it.");
  }
}
async function loadRun(id) {
  const run = await api("/incidents/" + encodeURIComponent(id));
  const trace = await api("/incidents/" + encodeURIComponent(id) + "/trace");
  S.run = { ...run, incident_id: id };
  S.events = trace.events;
  S.error = "";
  S.selectedTool = null;
  S.ragProbe = null;
  remember();
  render();
}
async function decide(approve, denial = false) {
  if (S.deciding || !S.run?.proposal) return;
  const p = S.run.proposal;
  S.deciding = true;
  drawHeader();
  $$(".approval-card button").forEach((button) => (button.disabled = true));
  try {
    const result = await api(
      "/proposals/" + encodeURIComponent(p.id) + "/decision",
      "POST",
      { expected_hash: p.hash, approve },
    );
    S.run = result;
    S.events = (
      await api(
        "/incidents/" + encodeURIComponent(result.incident_id) + "/trace",
      )
    ).events;
    S.error = "";
    remember();
    notice(
      approve
        ? "Approved change executed; health verified."
        : "Proposal rejected. No change applied.",
    );
  } catch (error) {
    if (denial && error.status === 403) {
      S.events = (
        await api(
          "/incidents/" + encodeURIComponent(S.run.incident_id) + "/trace",
        )
      ).events;
      notice("Bagha cannot approve this fix (403). Nothing was changed.");
    } else {
      S.error = error.message;
      notice(error.message, true);
    }
  } finally {
    S.deciding = false;
    render();
  }
}
function dialog(title, eyebrow, content) {
  $("#dialog-eyebrow").textContent = eyebrow;
  $("#dialog-content").innerHTML =
    `<h2 id="dialog-title">${esc(title)}</h2>${content}`;
  if (!$("#detail-dialog").open) $("#detail-dialog").showModal();
}
function connectionDialog() {
  dialog(
    "Connect an identity",
    "LOCAL HARNESS",
    `<p class="dialog-lead">Mode: <code>${esc(S.config?.mode)}</code>. Model: <code>${esc(S.config?.model)}</code>. Model API keys stay on the server.</p>${S.config?.demo_auth ? `<p class="dialog-lead">Local persona login is enabled with <code>--demo-auth</code>. Each selection issues a short-lived development JWT. API authorization still runs.</p><button class="primary-button" data-action="connect">Connect as ${esc(names[$("#persona").value])}</button>` : `<p class="dialog-lead">Start the local server with <code>serve --demo-auth</code>, or paste a valid application JWT. This is not your OpenRouter key. Tokens remain in memory only.</p><code class="code-line">uv run runbookops --as bagha token</code><form id="token-form"><label class="field-label" for="access-token">Application access token</label><textarea id="access-token" class="token-field" required spellcheck="false" autocomplete="off"></textarea><button type="submit" class="primary-button">Connect token</button></form>`}`,
  );
}
function help() {
  dialog(
    "Use the learning harness",
    "WORKSHOP GUIDE",
    `<p class="dialog-lead">The console is deliberately small: a task, its visible execution, and an inspector for the components you are learning.</p><ol class="help-list"><li><strong>Run as Bagha.</strong> Send a checkout incident. Expand tool calls to see their arguments and results.</li><li><strong>Inspect the harness.</strong> Read the exact system prompt and graph. Compare model-facing Tools schemas with actual MCP discovery.</li><li><strong>Follow the context.</strong> Open RAG for returned chunks, source locations, access filters, embeddings, and a retrieval-only probe.</li><li><strong>Review as Jethalal.</strong> The agent can prepare a change; an authorized person approves the exact stored proposal.</li><li><strong>Check State and Events.</strong> Inspect the saved checkpoint, verification, and sanitized trace. This is one task per incident, not a general multi-turn chatbot.</li></ol><p class="small muted">The personas are development shortcuts for a local synthetic simulator. They are not production login accounts.</p><button class="quiet-button" data-action="identity">Connection & identity</button>`,
  );
}
async function source(id) {
  const item = await api("/knowledge/" + encodeURIComponent(id));
  dialog(
    item.title,
    `${item.file} / v${item.version}`,
    `<p class="dialog-lead">Source <code>${esc(item.id)}</code> · updated ${esc(item.updated)} · ${esc(item.access)} access.</p>${item.sections.map((section) => `<section class="document-section"><h3>${esc(section.location)}</h3><p>${esc(section.text)}</p></section>`).join("")}`,
  );
}
function exportTrace() {
  if (!S.run) {
    notice("Run or open an incident first.");
    return;
  }
  const url = URL.createObjectURL(
    new Blob([json({ state: S.run, events: S.events })], {
      type: "application/json",
    }),
  );
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = (S.run.incident_id || "runbookops") + "-trace.json";
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function theme() {
  const dark = document.documentElement.dataset.theme === "dark";
  $("#theme-toggle").innerHTML = icon(dark ? "sun" : "moon");
  $("#theme-toggle").setAttribute(
    "aria-label",
    `Switch to ${dark ? "light" : "dark"} theme`,
  );
}
function setPane(pane) {
  document.body.classList.toggle("inspect-mode", pane === "inspect");
  $$("[data-pane]").forEach((button) =>
    button.setAttribute("aria-pressed", String(button.dataset.pane === pane)),
  );
}
$("#theme-toggle").addEventListener("click", () => {
  const value =
    document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  // Finish colour changes together; Safari can retain old transition colours on controls.
  document.documentElement.classList.add("theme-changing");
  void document.documentElement.offsetWidth;
  document.documentElement.dataset.theme = value;
  void document.documentElement.offsetWidth;
  requestAnimationFrame(() =>
    document.documentElement.classList.remove("theme-changing"),
  );
  try {
    localStorage.setItem("runbookops-theme", value);
  } catch {}
  theme();
});
$("#persona").addEventListener("change", (event) =>
  connect(event.target.value),
);
$("#connect-button").addEventListener("click", connectionDialog);
$("#help-button").addEventListener("click", help);
$("#dialog-close").addEventListener("click", () => $("#detail-dialog").close());
$("#detail-dialog").addEventListener("click", (event) => {
  if (event.target === $("#detail-dialog")) $("#detail-dialog").close();
});
$("#new-task").addEventListener("click", () => {
  document.body.classList.remove("sessions-open");
  $("#sessions-toggle").setAttribute("aria-expanded", "false");
  $("#new-session").click();
});
$("#new-session").addEventListener("click", () => {
  if (S.busy || S.deciding) return;
  resetRun();
  $("#task-input").value = "";
  render();
  setPane("chat");
  $("#task-input").focus();
});
$("#stop-button").addEventListener("click", () => S.controller?.abort());
$("#refresh-session").addEventListener("click", async () => {
  if (S.busy) {
    notice("The task is still streaming.");
    return;
  }
  if (S.run?.incident_id) {
    try {
      await loadRun(S.run.incident_id);
    } catch (error) {
      notice(error.message, true);
    }
  }
});
$("#export-button").addEventListener("click", exportTrace);
$("#open-session").addEventListener("click", () =>
  dialog(
    "Open saved incident",
    "PERSISTED STATE",
    '<p class="dialog-lead">The server rechecks access for the selected persona.</p><form id="open-form"><label class="field-label" for="saved-id">Incident ID</label><input id="saved-id" class="token-field" required maxlength="100" placeholder="gada-…"><button class="primary-button" type="submit">Open incident</button></form>',
  ),
);
$("#event-filter").addEventListener("change", (event) => {
  S.filter = event.target.value;
  drawEvents();
});
function toggleDock() {
  const collapsed = $(".console-layout").classList.toggle("dock-collapsed");
  $("#dock-toggle").setAttribute("aria-expanded", String(!collapsed));
  $("#dock-toggle").setAttribute(
    "aria-label",
    collapsed ? "Expand event stream" : "Collapse event stream",
  );
}
$("#dock-toggle").addEventListener("click", toggleDock);
$("#mobile-events").addEventListener("click", toggleDock);
$("#sessions-toggle").addEventListener("click", () => {
  const open = document.body.classList.toggle("sessions-open");
  $("#sessions-toggle").setAttribute("aria-expanded", String(open));
});
document.addEventListener("click", async (event) => {
  const pane = event.target.closest("[data-pane]");
  if (pane) {
    setPane(pane.dataset.pane);
    return;
  }
  const tab = event.target.closest("[data-tab]");
  if (tab) {
    inspect(tab.dataset.tab);
    tab.focus();
    if (tab.dataset.tab === "mcp" && !S.mcp) await discover();
    return;
  }
  const target = event.target.closest("[data-action]");
  if (!target || target.disabled) return;
  try {
    switch (target.dataset.action) {
      case "demo-library":
        demoLibrary();
        break;
      case "demo-dismiss":
        S.demo = null;
        drawDemo();
        break;
      case "demo-select": {
        if (S.busy || S.deciding) {
          notice("Finish or stop the active operation first.");
          break;
        }
        const d = demos[Number(target.dataset.index)];
        if (!d) break;
        S.demo = d;
        $("#detail-dialog").close();
        drawDemo();
        if (d.kind === "task") {
          $("#task-input").value = d.prompt;
          setPane("chat");
          $("#task-input").focus();
        } else if (d.kind === "rag") {
          S.ragQuery = d.prompt;
          S.ragProbe = null;
          inspect("rag");
          $("#rag-query").focus();
        } else {
          inspect(d.tab || "harness");
          if (d.tab === "mcp" && !S.mcp) await discover();
        }
        break;
      }
      case "prompt":
        dialog(
          "System prompt",
          "HARNESS",
          `<div class="prompt-text">${esc(S.harness.system_prompt)}</div>`,
        );
        break;
      case "model":
        dialog(
          "Model",
          "HARNESS",
          values([
            ["Mode", S.config.mode],
            ["Model", S.harness.routing.diagnose],
            ["Max calls", S.harness.limits.model_calls],
            ["Output tokens", S.harness.limits.output_tokens],
          ]),
        );
        break;
      case "inspect-section":
        inspect(target.dataset.section);
        if (target.dataset.section === "mcp" && !S.mcp) await discover();
        break;
      case "approval-focus":
        if ($(".approval-card")) {
          setPane("chat");
          $(".approval-card").scrollIntoView({
            block: "center",
            behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
              ? "auto"
              : "smooth",
          });
          setPane("chat");
        } else notice("No approval is waiting.");
        break;
      case "mcp-schema": {
        const tool = S.mcp.tools[Number(target.dataset.index)];
        dialog(
          tool.name,
          "MCP SCHEMA",
          `<p class="schema-description">${esc(tool.description)}</p><div class="json-box"><pre>${esc(json(tool.input_schema))}</pre></div>`,
        );
        break;
      }
      case "preset":
        $("#task-input").value = presets[Number(target.dataset.index)][1];
        $("#task-input").focus();
        break;
      case "load":
        if (S.busy) notice("Finish or stop the current task first.");
        else {
          await loadRun(target.dataset.id);
          document.body.classList.remove("sessions-open");
          setPane("chat");
        }
        break;
      case "event": {
        const item = S.events[Number(target.dataset.index)];
        dialog(
          item.kind,
          "RECORDED EVENT",
          `<div class="json-box"><pre>${esc(json(item))}</pre></div>`,
        );
        break;
      }
      case "inspect-tool":
        S.selectedTool = S.events[Number(target.dataset.index)];
        S.ragProbe = null;
        S.ragTab = "results";
        inspect(S.selectedTool.tool === "search_runbooks" ? "rag" : "tools");
        break;
      case "discover":
        await discover();
        break;
      case "source":
        await source(target.dataset.id);
        break;
      case "rag-results":
        S.ragTab = "results";
        drawInspector();
        break;
      case "rag-corpus":
        S.ragTab = "corpus";
        drawInspector();
        break;
      case "state":
        inspect("state");
        break;
      case "refresh":
        if (S.run?.incident_id && !S.busy) await loadRun(S.run.incident_id);
        else notice("Select a completed or paused incident first.");
        break;
      case "review-persona":
        if (S.config.demo_auth) await connect("jethalal");
        else connectionDialog();
        break;
      case "denial":
        await decide(true, true);
        break;
      case "approve":
        if ($("#review-check")?.checked) await decide(true);
        break;
      case "reject":
        await decide(false);
        break;
      case "resume":
        S.run = await api(
          "/incidents/" + encodeURIComponent(S.run.incident_id) + "/resume",
          "POST",
        );
        await loadRun(S.run.incident_id);
        break;
      case "identity":
        connectionDialog();
        break;
      case "connect":
        $("#detail-dialog").close();
        await connect($("#persona").value);
        break;
    }
  } catch (error) {
    if (!(error instanceof StaleSession)) notice(error.message, true);
  }
});
document.addEventListener("change", (event) => {
  if (event.target.id === "review-check")
    $('[data-action="approve"]').disabled = !event.target.checked;
});
document.addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.target;
  if (form.id === "task-form") {
    await begin($("#task-input").value);
    return;
  }
  if (form.id === "rag-form") {
    S.ragQuery = $("#rag-query").value;
    const button = $("button", form);
    button.disabled = true;
    button.textContent = "Retrieving…";
    try {
      S.ragProbe = await api("/knowledge/search", "POST", {
        question: S.ragQuery,
      });
      S.ragTab = "results";
      drawInspector();
    } catch (error) {
      if (!(error instanceof StaleSession)) notice(error.message, true);
      button.disabled = false;
      button.textContent = "Retrieve";
    }
  }
  if (form.id === "open-form") {
    try {
      await loadRun($("#saved-id").value.trim());
      $("#detail-dialog").close();
    } catch (error) {
      notice(error.message, true);
    }
  }
  if (form.id === "token-form") {
    const token = $("#access-token")
      .value.trim()
      .replace(/^Bearer\s+/i, "");
    S.epoch++;
    resetRun();
    S.actor = null;
    S.sources = [];
    S.harness = null;
    S.mcp = null;
    S.token = token;
    S.expires = 0;
    render();
    try {
      S.actor = await api("/me");
      $("#persona").value = S.actor.user;
      const [h, k] = await Promise.all([api("/harness"), api("/knowledge")]);
      S.harness = h;
      S.sources = k.sources;
      $("#detail-dialog").close();
      render();
      notice("Application identity connected.");
    } catch (error) {
      S.token = "";
      S.actor = null;
      notice(error.message, true);
    }
  }
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !$("#detail-dialog").open) {
    document.body.classList.remove("sessions-open");
    $("#sessions-toggle").setAttribute("aria-expanded", "false");
  }
  if (
    (event.metaKey || event.ctrlKey) &&
    event.key === "Enter" &&
    event.target.id === "task-input"
  ) {
    event.preventDefault();
    $("#task-form").requestSubmit();
  }
  if (
    event.target.matches?.("[role=tab]") &&
    ["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)
  ) {
    event.preventDefault();
    const tabs = $$("[role=tab]");
    let index = tabs.indexOf(event.target);
    index =
      event.key === "Home"
        ? 0
        : event.key === "End"
          ? tabs.length - 1
          : (index + (event.key === "ArrowRight" ? 1 : tabs.length - 1)) %
            tabs.length;
    tabs[index].click();
  }
});
async function health() {
  if (document.hidden) return;
  try {
    const r = await fetch("/health");
    if (!r.ok) throw new Error();
    $("#server-dot").classList.remove("offline");
    $("#server-status").textContent = "Server connected";
  } catch {
    $("#server-dot").classList.add("offline");
    $("#server-status").textContent = "Server unavailable";
  }
}
async function boot() {
  theme();
  try {
    const response = await fetch("/ui/config");
    if (!response.ok)
      throw new Error("Start the local RunbookOps server and reload.");
    S.config = await response.json();
    $("#mode-pill").textContent =
      S.config.mode === "offline"
        ? "OFFLINE PRACTICE"
        : S.config.mode.toUpperCase();
    if (S.config.demo_auth) {
      const saved = read("runbookops-persona", "bagha");
      await connect(names[saved] ? saved : "bagha");
    } else {
      render();
      connectionDialog();
    }
    await health();
    setInterval(health, 30000);
    document.addEventListener("visibilitychange", health);
  } catch (error) {
    S.error = error.message;
    $("#server-status").textContent = "Connection failed";
    $("#server-dot").classList.add("offline");
    notice(error.message, true);
    if (S.config) render();
  }
}
// Named entrypoints keep startup and the console's asynchronous operations observable.
const ready = boot();
export {
  S as state,
  ready,
  boot,
  connect,
  begin,
  loadRun,
  decide,
  inspect,
  discover,
  health,
  render,
  api,
};
