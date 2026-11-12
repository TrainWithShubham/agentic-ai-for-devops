import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { pathToFileURL } from "node:url";
import { JSDOM } from "jsdom";
const html = fs.readFileSync("src/runbookops/web/index.html", "utf8");
let instance = 0;
let current;
const harness = {
  system_prompt: "Use evidence. Never approve.",
  checkpoint: "SQLite",
  limits: {
    model_calls: 6,
    tool_calls: 16,
    output_tokens: 2048,
    timeout_seconds: 150,
  },
  routing: { diagnose: "test:free", summarize: "small:free" },
  mcp: { transport: "inprocess" },
  rag: {
    embedding: "hash",
    embedding_model: "test",
    chunk_characters: 900,
    overlap_characters: 120,
    cache_ttl_seconds: 120,
    filters: ["current", "role"],
    cache_scope: ["user"],
  },
  graph: {
    nodes: [
      { id: "__start__" },
      { id: "investigate" },
      { id: "review" },
      { id: "execute" },
    ],
  },
  tools: [
    {
      function: {
        name: "get_service_health",
        description: "Check health",
        parameters: { type: "object" },
      },
    },
    {
      function: {
        name: "search_runbooks",
        description: "Search notes",
        parameters: { type: "object" },
      },
    },
  ],
};
const plan = {
  key: "PAYMENT_SERVICE_URL",
  environment: "simulator",
  before: "http://payments:9009",
  after: "http://payments:9000",
  risk: "Reload may interrupt requests",
  validation: "Check HTTP 200",
  rollback: { value: "http://payments:9009" },
  evidence: ["checkout-runbook"],
};
const proposal = () => ({
  id: "p1",
  hash: "a".repeat(64),
  expires: Date.now() / 1000 + 900,
  status: "pending",
  plan,
});
const run = (extra = {}) => ({
  incident_id: "gada-test",
  user: "bagha",
  question: "Checkout is down",
  mode: "openrouter",
  health: { http_status: 503 },
  waiting_for_approval: true,
  proposal: proposal(),
  ...extra,
});
const events = () => [
  { kind: "incident_created", actor: "bagha", at: 1 },
  { kind: "node_started", node: "investigate", at: 2 },
  {
    kind: "mcp_connected",
    transport: "inprocess",
    tools: ["get_service_health"],
    at: 3,
  },
  { kind: "model_request", turn: 1, message_count: 2, tool_count: 5, at: 4 },
  {
    kind: "model",
    turn: 1,
    model: "test:free",
    content: "Checking checkout.",
    duration_ms: 50,
    usage: { prompt_tokens: 10, completion_tokens: 3, cost: 0 },
    requested_tools: [{ name: "get_service_health" }],
    at: 5,
  },
  {
    kind: "tool",
    tool: "get_service_health",
    duration_ms: 2,
    arguments: { service: "checkout" },
    result: { http_status: 503, revision: 1 },
    at: 6,
  },
  {
    kind: "tool",
    tool: "search_runbooks",
    arguments: { query: "checkout" },
    result: {
      results: [
        {
          source: "checkout-runbook",
          text: "Use port 9000",
          location: "Diagnosis",
          similarity: 0.8,
        },
      ],
      cache_hit: false,
    },
    at: 7,
  },
  { kind: "tool", tool: "prepare_change", result: { id: "p1" }, at: 8 },
  { kind: "proposal_prepared", proposal_id: "p1", at: 9 },
  { kind: "investigation_finished", model_calls: 1, proposal_id: "p1", at: 10 },
  { kind: "node_completed", node: "investigate", at: 11 },
];
function response(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json" },
  });
}
function ndjson(rows, { trailing = true, split = false } = {}) {
  const bytes = new TextEncoder().encode(
    rows.map((row) => JSON.stringify(row)).join("\n") + (trailing ? "\n" : ""),
  );
  return new Response(
    new ReadableStream({
      start(controller) {
        if (split) {
          controller.enqueue(bytes.slice(0, 13));
          controller.enqueue(bytes.slice(13));
        } else controller.enqueue(bytes);
        controller.close();
      },
    }),
  );
}
async function setup(options = {}) {
  current?.dom.window.close();
  const dom = new JSDOM(html, {
    url: "http://127.0.0.1:8004/",
    pretendToBeVisual: true,
  });
  const { window: w } = dom;
  const errors = [];
  w.addEventListener("error", (e) => {
    errors.push(e.error);
    e.preventDefault();
  });
  Object.assign(globalThis, {
    window: w,
    document: w.document,
    localStorage: w.localStorage,
    matchMedia: (q) => ({
      matches: options.mobile || (options.reduced && q.includes("reduced")),
    }),
    requestAnimationFrame: (fn) => fn(),
  });
  w.HTMLElement.prototype.scrollIntoView = function () {
    this.dataset.scrolled = "true";
  };
  w.HTMLDialogElement.prototype.showModal = function () {
    this.open = true;
  };
  w.HTMLDialogElement.prototype.close = function () {
    this.open = false;
  };
  w.HTMLAnchorElement.prototype.click = function () {
    this.dataset.clicked = "true";
  };
  w.HTMLFormElement.prototype.requestSubmit = function () {
    this.dispatchEvent(
      new w.Event("submit", { bubbles: true, cancelable: true }),
    );
  };
  const timers = [];
  globalThis.setInterval = () => 0;
  globalThis.setTimeout = (fn, ms) => {
    timers.push(fn);
    return 0;
  };
  globalThis.clearTimeout = () => {};
  const requests = [];
  const overrides = new Map();
  let actor = "bagha";
  let streamRows;
  globalThis.fetch = async (path, init = {}) => {
    requests.push({ path, init });
    if (overrides.has(path)) return await overrides.get(path)(init);
    if (path === "/ui/config")
      return response({
        mode: options.mode || "openrouter",
        demo_auth: options.demoAuth ?? true,
        model: "test:free",
      });
    if (path === "/ui/session") {
      actor = JSON.parse(init.body).user;
      return response({
        access_token: "test-" + actor,
        user: actor,
        role: actor === "jethalal" ? "approver" : "viewer",
        scopes:
          actor === "jethalal"
            ? ["read", "investigate", "approve"]
            : ["read", "investigate"],
        expires_in: 600,
      });
    }
    if (path === "/harness") return response(harness);
    if (path === "/knowledge")
      return response({
        sources: [
          {
            id: "checkout-runbook",
            file: "runbook.md",
            title: "Runbook",
            version: 2,
            access: "public",
          },
        ],
      });
    if (path === "/me")
      return response({
        user: actor,
        role: "viewer",
        scopes: ["read", "investigate"],
      });
    if (path === "/health") return response({ status: "Healthy" });
    if (path === "/harness/mcp")
      return response({
        tools: [
          {
            name: "get_service_health",
            description: "Check health",
            input_schema: { type: "object" },
          },
          { name: "prepare_change", description: "Propose", input_schema: {} },
          { name: "search_runbooks", description: "Search", input_schema: {} },
        ],
      });
    if (path === "/knowledge/search")
      return response({
        results: [
          {
            source: "checkout-runbook",
            text: "Use port 9000",
            location: "Diagnosis",
            similarity: 0.8,
          },
        ],
        cache_hit: false,
      });
    if (path.startsWith("/knowledge/"))
      return response({
        id: "checkout-runbook",
        title: "Runbook",
        file: "runbook.md",
        version: 2,
        updated: "today",
        access: "public",
        sections: [{ location: "Diagnosis", text: "Use port 9000" }],
      });
    if (path === "/investigations/stream")
      return ndjson(
        streamRows || [
          { type: "incident", data: { incident_id: "gada-test" } },
          ...events().map((data) => ({ type: "event", data })),
          {
            type: "complete",
            data: run({ diagnosis: "Payment address is wrong" }),
          },
        ],
        options.stream || {},
      );
    if (path.endsWith("/trace")) return response({ events: events() });
    if (path.endsWith("/decision")) {
      if (actor !== "jethalal")
        return response({ detail: "Approval permission required" }, 403);
      const approve = JSON.parse(init.body).approve;
      return response(
        run({
          health: { http_status: approve ? 200 : 503 },
          waiting_for_approval: false,
          proposal: { ...proposal(), status: approve ? "applied" : "rejected" },
          result: { applied: approve },
        }),
      );
    }
    if (path.endsWith("/resume"))
      return response(
        run({ health: { http_status: 200 }, waiting_for_approval: false }),
      );
    if (path.startsWith("/incidents/")) return response(run());
    throw new Error("Unexpected endpoint " + path);
  };
  if (options.storageFailure)
    Object.defineProperty(globalThis, "localStorage", {
      configurable: true,
      writable: true,
      value: {
        getItem() {
          throw new Error("blocked");
        },
        setItem() {
          throw new Error("blocked");
        },
      },
    });
  if (options.beforeBoot) options.beforeBoot({ overrides, requests, w });
  const app = await import(
    pathToFileURL(process.cwd() + "/src/runbookops/web/app.js").href +
      "?case=" +
      instance++
  );
  await app.ready;
  const tick = async () => {
    await new Promise((resolve) => setImmediate(resolve));
    await new Promise((resolve) => setImmediate(resolve));
  };
  const click = async (selector) => {
    const e = w.document.querySelector(selector);
    assert.ok(e, "Missing " + selector);
    e.dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
    await tick();
  };
  const submit = async (selector) => {
    w.document
      .querySelector(selector)
      .dispatchEvent(
        new w.Event("submit", { bubbles: true, cancelable: true }),
      );
    await tick();
  };
  const action = async (name, data = {}) => {
    const b = w.document.createElement("button");
    b.dataset.action = name;
    Object.assign(b.dataset, data);
    w.document.body.append(b);
    b.dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
    await tick();
    b.remove();
  };
  current = {
    errors,
    dom,
    app,
    requests,
    overrides,
    timers,
    tick,
    click,
    submit,
    action,
    setRows: (rows) => (streamRows = rows),
  };
  return current;
}
test.afterEach(() => assert.deepEqual(current?.errors, []));
test.after(() => current?.dom.window.close());

test("console boots, investigates, inspects sources, requires approval and reports actual recovery", async () => {
  const t = await setup();
  const { app, click } = t;
  assert.match(
    document.querySelector("#inspector-body").textContent,
    /System prompt/,
  );
  await app.begin("Checkout down");
  assert.match(
    document.querySelector("#conversation").textContent,
    /Check checkout/,
  );
  assert.equal(app.state.run.health.http_status, 503);
  await click('[data-action="denial"]'); // A separate denial response is exercised in a failure test.
  await app.connect("jethalal");
  app.state.run = run();
  app.render();
  await app.decide(true);
  assert.equal(app.state.run.health.http_status, 200);
  assert.match(document.querySelector("#run-status").textContent, /Recovered/);
  app.inspect("rag");
  await t.action("source", { id: "checkout-runbook" });
  assert.match(
    document.querySelector("#dialog-content").textContent,
    /Use port 9000/,
  );
  app.inspect("tools");
  app.inspect("state");
  assert.match(
    document.querySelector("#inspector-body").textContent,
    /Saved work/,
  );
  await app.discover();
  app.inspect("mcp");
  assert.match(
    document.querySelector("#inspector-body").textContent,
    /Check checkout/,
  );
});

test("examples, inspector dialogs, tabs and keyboard controls are usable", async () => {
  const t = await setup({ mobile: true, reduced: true });
  await t.action("demo-library");
  assert.equal(document.querySelectorAll(".demo-card").length, 10);
  for (const i of [0, 1, 7, 8, 9])
    await t.action("demo-select", { index: String(i) });
  await t.action("demo-dismiss");
  await t.action("prompt");
  await t.action("model");
  await t.click("#dialog-close");
  await t.click("#detail-dialog");
  await t.action("inspect-section", { section: "mcp" });
  await t.action("mcp-schema", { index: "0" });
  await t.action("preset", { index: "0" });
  await t.action("approval-focus");
  t.app.state.run = run();
  t.app.render();
  await t.action("approval-focus");
  for (const selector of [
    "#theme-toggle",
    "#theme-toggle",
    "#sessions-toggle",
    "#sessions-toggle",
    "#dock-toggle",
    "#mobile-events",
    "#open-session",
    "#help-button",
    "#connect-button",
  ])
    await t.click(selector);
  await t.action("identity");
  await t.action("connect");
  for (const key of ["ArrowRight", "ArrowLeft", "Home", "End"])
    document
      .querySelector("[role=tab]")
      .dispatchEvent(
        new window.KeyboardEvent("keydown", { key, bubbles: true }),
      );
  await t.tick();
  document.dispatchEvent(
    new window.KeyboardEvent("keydown", { key: "Escape", bubbles: true }),
  );
  await t.click('[data-pane="inspect"]');
  await t.click('[data-pane="chat"]');
  await t.click("#new-task");
  await t.click("#stop-button");
  await t.click("#refresh-session");
});

test("rag search, saved sessions, trace dialogs and export preserve real data", async () => {
  const t = await setup();
  await t.app.begin("Check");
  t.app.inspect("rag");
  document.querySelector("#rag-query").value = "payment address";
  await t.submit("#rag-form");
  assert.match(
    document.querySelector("#inspector-body").textContent,
    /Use port 9000/,
  );
  await t.action("rag-corpus");
  await t.action("rag-results");
  await t.action("inspect-tool", { index: "6" });
  await t.action("inspect-tool", { index: "5" });
  await t.action("event", { index: "4" });
  await t.action("state");
  await t.action("refresh");
  await t.action("load", { id: "gada-test" });
  await t.click("#refresh-session");
  const filter = document.querySelector("#event-filter");
  filter.value = "approval";
  filter.dispatchEvent(new window.Event("change", { bubbles: true }));
  assert.match(
    document.querySelector("#event-list").textContent,
    /Fix suggested/,
  );
  await t.click("#export-button");
  t.timers.forEach((fn) => fn());
  await t.click("#open-session");
  document.querySelector("#saved-id").value = "gada-test";
  await t.submit("#open-form");
  await t.action("review-persona");
  t.app.state.run = run();
  t.app.render();
  await t.action("reject");
  assert.match(document.querySelector("#run-status").textContent, /Rejected/);
  t.app.state.run = run();
  t.app.render();
  await t.action("resume");
});

test("rendering covers approval states and incomplete provider metadata without claiming success", async () => {
  const t = await setup();
  const s = t.app.state;
  const states = [
    run({ proposal: { ...proposal(), status: "approved" } }),
    run({
      proposal: { ...proposal(), status: "rejected" },
      result: { applied: false },
    }),
    run({ proposal: { ...proposal(), status: "pending", expires: 1 } }),
    run({
      proposal: { ...proposal(), status: "applied" },
      result: { applied: true },
      health: { http_status: 200 },
    }),
    run({
      proposal: null,
      result: { applied: false },
      diagnosis: "No proposal",
      waiting_for_approval: false,
    }),
    run({ error: "Provider timed out" }),
    run({
      error: null,
      proposal: null,
      health: {},
      pending_nodes: ["execute"],
    }),
  ];
  for (const mode of ["offline", "openrouter"]) {
    s.config.mode = mode;
    for (const entry of states) {
      s.run = entry;
      s.events = [
        ...events(),
        {
          kind: "model",
          mode,
          content: "",
          usage: { total_tokens: 2, cost: 0 },
          requested_tools: [],
        },
        {
          kind: "model",
          mode,
          content: "Reply",
          requested_tools: [{ name: "unfamiliar_tool" }],
        },
        { kind: "tool", tool: "get_recent_logs", result: {} },
        { kind: "tool", tool: "get_recent_deployments", result: {} },
        {
          kind: "tool",
          tool: "prepare_change",
          result: { error: "validation failed" },
        },
        { kind: "tool", tool: "unfamiliar_tool", result: {} },
        { kind: "approval_denied", actor: "bagha" },
        { kind: "approval_decision", approver: "jethalal", status: "approved" },
        {
          kind: "verification",
          result: { health: { http_status: 200 }, applied: true },
        },
        { kind: "investigation_finished", model_calls: 2 },
        { kind: "investigation_finished", error: "timed out" },
        { kind: "other", actor: "test" },
        { kind: "other" },
      ];
      t.app.render();
      assert.ok(document.querySelector(".conversation").textContent.length > 0);
      s.actor = {
        user: "jethalal",
        role: "approver",
        scopes: ["approve", "read"],
      };
      t.app.render();
      s.actor = {
        user: "bagha",
        role: "viewer",
        scopes: ["read", "investigate"],
      };
    }
  }
  s.events = [
    {
      kind: "model",
      mode: "test",
      usage: { prompt_tokens: 2, completion_tokens: 1, cost: 0 },
    },
  ];
  s.run = run();
  s.busy = true;
  t.app.render();
  s.events.push({ kind: "model_request", turn: 2, tool_count: 5 });
  t.app.render();
  s.busy = false;
  s.deciding = true;
  t.app.render();
  s.deciding = false;
  s.error = "Unknown error";
  s.run = null;
  t.app.render();
  assert.match(
    document.querySelector("#conversation").textContent,
    /Technical details/,
  );
  s.error = "";
  s.events = [];
  t.app.inspect("state");
  s.selectedTool = events()[5];
  t.app.inspect("tools");
  s.selectedTool = null;
  t.app.inspect("tools");
  s.harness = null;
  t.app.inspect("harness");
  t.app.inspect("rag");
});

test("retrieval and discovery render empty, cached, loading, and failed outcomes", async () => {
  const t = await setup();
  const s = t.app.state;
  t.app.inspect("rag");
  s.ragTab = "results";
  t.app.render();
  s.ragProbe = { results: [], cache_hit: true };
  t.app.render();
  assert.match(
    document.querySelector("#inspector-body").textContent,
    /No matches/,
  );
  s.ragProbe = {
    results: [
      {
        source: "restricted",
        text: "Authorized note",
        location: "page 1",
        similarity: 0.8,
      },
    ],
    cache_hit: true,
  };
  t.app.render();
  s.ragTab = "corpus";
  s.sources.push({
    id: "restricted",
    title: "Restricted",
    access: "approver",
    version: 2,
    file: "private.pdf",
  });
  t.app.render();
  s.ragTab = "results";
  s.ragProbe = null;
  s.run = run();
  s.events = [
    {
      kind: "tool",
      tool: "search_runbooks",
      result: { results: [], cache_hit: true },
    },
  ];
  t.app.render();
  s.mcp = null;
  t.app.inspect("mcp");
  s.mcp = { loading: true };
  t.app.render();
  s.mcp = { error: "unavailable" };
  t.app.render();
  t.overrides.set("/harness/mcp", () =>
    response({ detail: "Unavailable" }, 503),
  );
  await t.app.discover();
  assert.match(
    document.querySelector("#inspector-body").textContent,
    /could not reach/,
  );
  t.overrides.delete("/harness/mcp");
  await t.app.discover();
  s.mcp = { tools: [] };
  t.app.render();
  t.app.inspect("rag");
  t.overrides.set("/knowledge/search", () =>
    response({ detail: "timeout" }, 503),
  );
  await t.submit("#rag-form");
  assert.equal(document.querySelector("#rag-form button").disabled, false);
});

test("API renewal, validation errors and stale responses are explicit", async () => {
  const t = await setup();
  const s = t.app.state;
  s.expires = Date.now() + 1;
  assert.equal((await t.app.api("/me")).user, "bagha");
  let count = 0;
  t.overrides.set("/me", () =>
    ++count === 1 ? response({}, 401) : response({ user: "bagha" }),
  );
  assert.equal((await t.app.api("/me")).user, "bagha");
  assert.equal(count, 2);
  t.overrides.set("/me", () =>
    response({ detail: [{ msg: "invalid input" }] }, 422),
  );
  await assert.rejects(t.app.api("/me"), /invalid input/);
  t.overrides.set("/me", () => response({}, 500));
  await assert.rejects(t.app.api("/me"), /HTTP 500/);
  t.overrides.set("/me", () => {
    s.epoch++;
    return response({ user: "old" });
  });
  await assert.rejects(t.app.api("/me"));
  t.overrides.set("/ui/session", () =>
    response({ detail: "login refused" }, 403),
  );
  s.expires = Date.now() + 1;
  await assert.rejects(t.app.api("/me"), /login refused/);
  t.overrides.set("/ui/session", () => {
    s.epoch++;
    return response({});
  });
  await assert.rejects(t.app.api("/me"));
  s.config.demo_auth = false;
  await assert.rejects(t.app.api("/me"), /Connect again/);
  s.token = "";
  await assert.rejects(t.app.api("/me"), /Connect an application/);
});

test("stream parser handles chunks, missing newline, errors, HTTP failures and cancellation", async () => {
  const t = await setup({ stream: { trailing: false, split: true } });
  await t.app.begin("check");
  assert.equal(t.app.state.run.incident_id, "gada-test");
  const s = t.app.state;
  for (const rows of [
    [{ type: "error", data: { message: "timeout" } }],
    [{ type: "error", data: {} }],
    [{ type: "connected", data: {} }],
  ]) {
    t.setRows(rows);
    await t.app.begin("check");
    assert.ok(s.error);
  }
  t.overrides.set("/investigations/stream", () =>
    response({ detail: "access denied" }, 403),
  );
  await t.app.begin("check");
  assert.match(s.error, /access denied/);
  t.overrides.set("/investigations/stream", () => response({}, 503));
  await t.app.begin("check");
  assert.match(s.error, /HTTP 503/);
  t.overrides.set("/investigations/stream", () => {
    throw new DOMException("aborted", "AbortError");
  });
  await t.app.begin("check");
  assert.match(s.error, /stopped/);
  t.overrides.set(
    "/investigations/stream",
    () =>
      new Response(
        "\n" +
          JSON.stringify({ type: "complete", data: run({ proposal: null }) }) +
          "\n",
      ),
  );
  await t.app.begin("check");
  assert.equal(s.error, "");
  const oldCount = t.requests.length;
  await t.app.begin("");
  await t.app.begin("x".repeat(1201));
  assert.equal(t.requests.length, oldCount);
  s.busy = true;
  await t.app.begin("check");
  s.busy = false;
  s.token = "";
  await t.app.begin("check");
  assert.ok(document.querySelector("#detail-dialog").open);
});

test("manual token login and development login failures keep credentials out of local storage", async () => {
  const t = await setup({ demoAuth: false });
  const s = t.app.state;
  await t.app.connect("jethalal");
  assert.ok(document.querySelector("#token-form"));
  document.querySelector("#access-token").value = "Bearer manual-token";
  await t.submit("#token-form");
  assert.equal(s.token, "manual-token");
  assert.equal(localStorage.getItem("access_token"), null);
  await t.action("identity");
  t.overrides.set("/me", () => response({ detail: "bad token" }, 401));
  document.querySelector("#access-token").value = "bad-token";
  await t.submit("#token-form");
  assert.equal(s.token, "");
  await t.action("review-persona");
  s.config.demo_auth = true;
  t.overrides.set("/ui/session", () => response({}, 403));
  await t.app.connect("bagha");
  assert.ok(s.error);
  t.overrides.set("/ui/session", () =>
    response({ detail: "login denied" }, 403),
  );
  await t.app.connect("bagha");
  assert.match(s.error, /login denied/);
});

test("persona switching clears inaccessible incidents and rejects changes while busy", async () => {
  const t = await setup();
  const s = t.app.state;
  s.run = run();
  t.overrides.set("/incidents/gada-test", () =>
    response({ detail: "not accessible" }, 403),
  );
  await t.app.connect("nattu");
  assert.equal(s.run, null);
  assert.match(document.querySelector("#toast").textContent, /not accessible/);
  s.busy = true;
  await t.app.connect("bagha");
  assert.equal(s.actor.user, "nattu");
  await t.click("#new-session");
  await t.click("#refresh-session");
  await t.action("load", { id: "gada-test" });
  await t.action("demo-select", { index: "0" });
  s.busy = false;
  s.deciding = true;
  await t.click("#new-session");
  await t.action("demo-select", { index: "0" });
  s.deciding = false;
  await t.action("demo-select", { index: "999" });
  s.run = run();
  s.deciding = true;
  await t.app.decide(true);
  s.deciding = false;
  s.run = null;
  await t.app.decide(true);
});

test("denial, rejected decisions, resumed work and error feedback retain the approval boundary", async () => {
  const t = await setup();
  const s = t.app.state;
  s.run = run();
  t.app.render();
  t.overrides.set("/proposals/p1/decision", () =>
    response({ detail: "no approve scope" }, 403),
  );
  await t.app.decide(true, true);
  assert.match(
    document.querySelector("#toast").textContent,
    /Bagha cannot approve/,
  );
  await t.app.decide(true);
  assert.match(s.error, /no approve/);
  s.actor = { user: "jethalal", role: "approver", scopes: ["read", "approve"] };
  s.run = run({ proposal: { ...proposal(), status: "approved" } });
  s.error = "";
  t.app.render();
  assert.match(
    document.querySelector("#conversation").textContent,
    /Resume execution/,
  );
  await t.action("resume");
  s.run = run();
  s.actor = { user: "jethalal", role: "approver", scopes: ["read", "approve"] };
  t.app.render();
  const box = document.querySelector("#review-check");
  box.checked = true;
  box.dispatchEvent(new window.Event("change", { bubbles: true }));
  assert.equal(
    document.querySelector('[data-action="approve"]').disabled,
    false,
  );
  await t.action("approve");
  box.checked = false;
  box.dispatchEvent(new window.Event("change", { bubbles: true }));
});

test("boot failures, disabled storage, server checks and cancellation controls degrade safely", async () => {
  let t = await setup({ storageFailure: true });
  await t.click("#theme-toggle");
  await t.click("#export-button");
  t.timers.forEach((fn) => fn());
  Object.defineProperty(document, "hidden", {
    configurable: true,
    value: true,
  });
  await t.app.health();
  Object.defineProperty(document, "hidden", {
    configurable: true,
    value: false,
  });
  t.overrides.set("/health", () => response({}, 503));
  await t.app.health();
  assert.match(
    document.querySelector("#server-status").textContent,
    /unavailable/,
  );
  t.overrides.set("/health", () => {
    throw new Error("network");
  });
  await t.app.health();
  t = await setup({
    beforeBoot: ({ overrides }) =>
      overrides.set("/ui/config", () => response({}, 500)),
  });
  assert.match(document.querySelector("#server-status").textContent, /failed/);
  t = await setup({
    beforeBoot: ({ overrides }) =>
      overrides.set("/ui/session", () => {
        throw new Error("network");
      }),
  });
  assert.ok(t.app.state.error);
  t = await setup();
  t.app.state.run = run();
  t.overrides.set("/incidents/gada-test", () =>
    response({ detail: "unavailable" }, 503),
  );
  await t.click("#refresh-session");
  await t.click("#open-session");
  document.querySelector("#saved-id").value = "gada-test";
  await t.submit("#open-form");
  await t.action("refresh");
  t.app.state.run = null;
  await t.action("refresh");
  t.app.state.controller = new AbortController();
  await t.click("#stop-button");
  assert.ok(t.app.state.controller.signal.aborted);
});

test("partial records and scroll positions preserve readable details and safe fallbacks", async () => {
  const t = await setup();
  const s = t.app.state;
  s.run = run({ user: "unmapped-user", question: "" });
  s.actor = { user: "unmapped-user", scopes: [], role: "viewer" };
  s.events = [
    {
      kind: "model",
      mode: "test",
      content: "Public reply",
      usage: {},
      requested_tools: [{ name: "unknown-tool" }],
    },
    { kind: "tool", tool: "get_service_health", result: { http_status: 200 } },
    { kind: "tool", tool: "get_service_health" },
    { kind: "tool", tool: "unfamiliar" },
    { kind: "mcp_connected" },
    { kind: "approval_decision", status: "pending" },
    { kind: "verification" },
  ];
  t.app.render();
  assert.match(
    document.querySelector("#conversation").textContent,
    /Checkout is working/,
  );
  assert.match(document.querySelector("#conversation").textContent, /unknown/);
  const detail = document.querySelector("details[data-key]");
  detail.open = true;
  const conversation = document.querySelector("#conversation");
  Object.defineProperties(conversation, {
    scrollHeight: { configurable: true, value: 1000 },
    clientHeight: { configurable: true, value: 100 },
  });
  conversation.scrollTop = 12;
  const list = document.querySelector("#event-list");
  Object.defineProperties(list, {
    scrollHeight: { configurable: true, value: 1000 },
    clientHeight: { configurable: true, value: 100 },
  });
  list.scrollTop = 12;
  t.app.render();
  assert.equal(conversation.scrollTop, 12);
  assert.ok(document.querySelector("details[data-key]").open);
  s.filter = "model";
  s.events = [{ kind: "other" }];
  t.app.render();
  assert.match(list.textContent, /No matching events/);
  s.run = { health: {}, waiting_for_approval: false };
  s.busy = true;
  t.app.inspect("state");
  assert.match(
    document.querySelector("#inspector-body").textContent,
    /Opening/,
  );
  s.busy = false;
  s.run.pending_nodes = ["review"];
  t.app.render();
  s.harness = null;
  t.app.inspect("mcp");
  t.app.inspect("tools");
  s.selectedTool = { tool: "get_recent_logs" };
  t.app.render();
  s.harness = {
    ...harness,
    tools: [
      {
        function: {
          name: "prepare_change",
          description: "Propose",
          parameters: {},
        },
      },
    ],
  };
  s.selectedTool = null;
  t.app.render();
  s.config = null;
  s.harness = null;
  s.run = null;
  s.events = [];
  s.actor = null;
  t.app.render();
  assert.match(
    document.querySelector("#runtime-status").textContent,
    /connecting/,
  );
});

test("form and keyboard submission, discovery buttons, and export work without internal calls", async () => {
  const t = await setup();
  document.querySelector("#task-input").value = "Check checkout";
  await t.submit("#task-form");
  assert.ok(t.app.state.run);
  const input = document.querySelector("#task-input");
  input.dispatchEvent(
    new window.KeyboardEvent("keydown", {
      key: "x",
      ctrlKey: true,
      bubbles: true,
    }),
  );
  document
    .querySelector("#persona")
    .dispatchEvent(
      new window.KeyboardEvent("keydown", {
        key: "Enter",
        metaKey: true,
        bubbles: true,
      }),
    );
  input.dispatchEvent(
    new window.KeyboardEvent("keydown", {
      key: "Enter",
      ctrlKey: true,
      bubbles: true,
    }),
  );
  await t.tick();
  assert.ok(
    t.requests.filter((r) => r.path === "/investigations/stream").length >= 2,
  );
  t.app.state.mcp = null;
  await t.click("#tab-mcp");
  t.app.state.mcp = null;
  await t.action("inspect-section", { section: "mcp" });
  await t.action("discover");
  t.app.state.run = run();
  t.app.render();
  await t.action("approval-focus");
  t.app.state.run = { question: "not saved yet" };
  t.app.render();
  await t.click("#export-button");
  t.app.state.run = run({ user: "", question: "" });
  t.app.render();
  t.app.state.actor = null;
  t.app.render();
});

test("in-flight persona and discovery responses cannot restore a stale identity", async () => {
  const t = await setup();
  const s = t.app.state;
  t.overrides.set("/harness/mcp", () => {
    s.epoch++;
    return response({ tools: [] });
  });
  await t.app.discover();
  assert.ok(s.mcp.loading);
  t.overrides.set("/ui/session", () => ({
    ok: true,
    json() {
      queueMicrotask(() => queueMicrotask(() => s.epoch++));
      return Promise.resolve({
        access_token: "new-token",
        expires_in: 600,
        user: "bagha",
        role: "viewer",
        scopes: ["read"],
      });
    },
  }));
  await t.app.connect("bagha");
  assert.equal(s.actor, null);
  s.config.demo_auth = false;
  await t.app.connect("bagha");
  assert.equal(document.querySelector("#persona").value, "bagha");
});

test("boot chooses a safe persona, handles offline startup, and reports post-config failure", async () => {
  let t = await setup({
    mode: "offline",
    beforeBoot: ({ w }) =>
      w.localStorage.setItem(
        "runbookops-persona",
        JSON.stringify("unknown-user"),
      ),
  });
  assert.equal(t.app.state.actor.user, "bagha");
  assert.match(document.querySelector("#mode-pill").textContent, /OFFLINE/);
  const interval = globalThis.setInterval;
  globalThis.setInterval = () => {
    throw new Error("timers unavailable");
  };
  await t.app.boot();
  assert.match(document.querySelector("#server-status").textContent, /failed/);
  globalThis.setInterval = interval;
  t.app.state.run = run();
  t.app.state.actor = { user: "jethalal", scopes: ["approve"] };
  t.app.render();
  const box = document.querySelector("#review-check");
  box.checked = false;
  await t.action("approve");
  assert.equal(t.app.state.run.health.http_status, 503);
  const submit = document.createElement("form");
  document.body.append(submit);
  await t.submit("form:not([id])");
  submit.remove();
});

test("nullable metadata, configured personas and inspector disclosures have safe defaults", async () => {
  const t = await setup({
    beforeBoot: ({ w }) =>
      w.localStorage.setItem("runbookops-persona", JSON.stringify("nattu")),
  });
  const s = t.app.state;
  assert.equal(s.actor.user, "nattu");
  s.config.demo_auth = false;
  await t.app.connect("bagha");
  assert.equal(document.querySelector("#persona").value, "nattu");
  s.ragTab = "results";
  s.ragProbe = {
    results: [{ source: null, text: null, location: null, similarity: null }],
  };
  t.app.inspect("rag");
  const details = document.querySelector("#inspector-body details");
  details.open = true;
  t.app.render();
  assert.ok(document.querySelector("#inspector-body details").open);
  s.harness = { ...harness, mcp: { transport: "" } };
  t.app.inspect("mcp");
  assert.match(document.querySelector("#inspector-body").textContent, /—/);
  const { demos } = await import("../src/runbookops/web/demos.js");
  demos.push({ title: "Default inspector", topic: "Harness", kind: "inspect" });
  try {
    await t.action("demo-select", { index: String(demos.length - 1) });
    assert.equal(s.tab, "harness");
  } finally {
    demos.pop();
  }
});

test("newly discovered MCP tools retain their exact protocol names", async () => {
  const t = await setup();
  t.app.state.mcp = {
    tools: [
      {
        name: "future_readonly_tool",
        description: "Extension",
        input_schema: {},
      },
    ],
  };
  t.app.inspect("mcp");
  assert.match(
    document.querySelector("#inspector-body").textContent,
    /future_readonly_tool/,
  );
});
