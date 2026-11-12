import test from "node:test";
import assert from "node:assert/strict";
let instance = 0;
for (const value of [null, "light", "dark", "throws"])
  test("theme startup " + value, async () => {
    globalThis.document = { documentElement: { dataset: { theme: "dark" } } };
    globalThis.localStorage = {
      getItem() {
        if (value === "throws") throw new Error("blocked");
        return value;
      },
    };
    await import("../src/runbookops/web/theme.js?test=" + instance++);
    assert.equal(
      document.documentElement.dataset.theme,
      value === "light" ? "light" : "dark",
    );
  });
