import test from "node:test";
import assert from "node:assert/strict";
import { explainError } from "../src/runbookops/web/learning.js";

test("provider timeout gives a retry action without hiding raw diagnostics from the caller", () => {
  const raw =
    "openrouter timed out while waiting for a response. No fallback was used.";
  const [title, next] = explainError(raw);
  assert.match(title, /too long/);
  assert.match(next, /Run/);
  assert.equal(
    raw,
    "openrouter timed out while waiting for a response. No fallback was used.",
  );
});
test("AWS access problems do not tell learners that changing persona grants AWS permission", () => {
  const [title, next] = explainError(
    "AccessDeniedException: not authorized to perform bedrock:InvokeModel",
  );
  assert.match(title, /AWS model/);
  assert.doesNotMatch(next, /Jethalal/);
});
test("expired approval and quota failures have different next steps", () => {
  assert.match(explainError("Proposal expired")[1], /new task/);
  assert.match(explainError("HTTP 429 quota exceeded")[1], /Wait/);
});
test("an unknown failure does not claim the operation succeeded or changed nothing", () => {
  const result = explainError("Unexpected error").join(" ");
  assert.match(result, /Technical details/);
  assert.doesNotMatch(result, /succeeded|Nothing was changed|working again/);
});
