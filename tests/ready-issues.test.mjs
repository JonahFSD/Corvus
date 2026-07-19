import assert from "node:assert/strict";
import test from "node:test";

import {
  boundedPositiveInteger,
  selectReadyIssues,
} from "../scripts/lib/ready-issues.mjs";

test("selectReadyIssues permits only open, unassigned AFK tickets", () => {
  const issues = [
    {
      number: 1,
      state: "OPEN",
      labels: [{ name: "ready-for-agent" }],
      assignees: [],
    },
    {
      number: 2,
      state: "OPEN",
      labels: [{ name: "ready-for-human" }],
      assignees: [],
    },
    {
      number: 3,
      state: "OPEN",
      labels: [{ name: "ready-for-agent" }, { name: "wayfinder:grilling" }],
      assignees: [],
    },
    {
      number: 4,
      state: "OPEN",
      labels: [{ name: "ready-for-agent" }],
      assignees: [{ login: "owner" }],
    },
    { number: 5, state: "CLOSED", labels: ["ready-for-agent"], assignees: [] },
  ];

  assert.deepEqual(
    selectReadyIssues(issues).map((issue) => issue.number),
    [1]
  );
});

test("boundedPositiveInteger enforces an unattended iteration ceiling", () => {
  assert.equal(boundedPositiveInteger(undefined, 1, 20, "iterations"), 1);
  assert.equal(boundedPositiveInteger("20", 1, 20, "iterations"), 20);
  assert.throws(() => boundedPositiveInteger("0", 1, 20, "iterations"));
  assert.throws(() => boundedPositiveInteger("21", 1, 20, "iterations"));
});
