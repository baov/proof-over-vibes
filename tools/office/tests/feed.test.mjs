import assert from "node:assert/strict";
import test from "node:test";

import { diffEvents } from "../web/feed.js";
import { roleShort, roleTitle, verdictTone } from "../web/roles.js";

const run = (qa) => ({ slug: "s", iteration: 0, limit: 5, roles: { qa } });

test("qa reads as an acronym", () => {
  assert.equal(roleTitle("qa"), "QA");
  assert.equal(roleShort("qa"), "QA");
  assert.equal(roleTitle("failure-analyst"), "Failure Analyst");
});

test("a QA proof is good, bad, or neither", () => {
  assert.equal(verdictTone("GO"), "good");
  assert.equal(verdictTone("NO-GO"), "bad");
  assert.equal(verdictTone("not-applicable"), "info");
});

test("the feed reports QA's proof with its tone", () => {
  const before = run({ state: "working", verdict: null });
  const noGo = diffEvents(before, run({ state: "done", verdict: "NO-GO" }));
  assert.deepEqual(noGo.at(-1), { text: "QA: NO-GO", tone: "bad" });
  const notApplicable = diffEvents(before, run({ state: "done", verdict: "not-applicable" }));
  assert.deepEqual(notApplicable.at(-1), { text: "QA: not-applicable", tone: "info" });
});
