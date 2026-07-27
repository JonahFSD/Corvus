import assert from "node:assert/strict";
import test from "node:test";

import {
  boundedPositiveInteger,
  parseBlockingIssueNumbers,
  selectReadyIssues,
} from "../scripts/lib/ready-issues.mjs";

test("parseBlockingIssueNumbers accepts the canonical blocker header", () => {
  assert.deepEqual(parseBlockingIssueNumbers("Blocked by: None\n\n# Ready"), {
    valid: true,
    issueNumbers: [],
  });
  assert.deepEqual(parseBlockingIssueNumbers("Blocked by: #10, #13\n"), {
    valid: true,
    issueNumbers: [10, 13],
  });
});

test("parseBlockingIssueNumbers fails closed on ambiguous metadata", () => {
  for (const body of [
    "# Missing header",
    "Blocked by:",
    "Blocked by: issue 10",
    "Blocked by: #10 and #13",
    "Blocked by: #10, #10",
  ]) {
    assert.deepEqual(parseBlockingIssueNumbers(body), {
      valid: false,
      issueNumbers: [],
    });
  }
});

test("selectReadyIssues permits only open, unassigned AFK tickets", () => {
  const issues = [
    {
      number: 1,
      state: "OPEN",
      labels: [{ name: "ready-for-agent" }],
      assignees: [],
      body: "Blocked by: None",
    },
    {
      number: 2,
      state: "OPEN",
      labels: [{ name: "ready-for-human" }],
      assignees: [],
      body: "Blocked by: None",
    },
    {
      number: 3,
      state: "OPEN",
      labels: [{ name: "ready-for-agent" }, { name: "wayfinder:grilling" }],
      assignees: [],
      body: "Blocked by: None",
    },
    {
      number: 4,
      state: "OPEN",
      labels: [{ name: "ready-for-agent" }],
      assignees: [{ login: "owner" }],
      body: "Blocked by: None",
    },
    {
      number: 5,
      state: "CLOSED",
      labels: ["ready-for-agent"],
      assignees: [],
      body: "Blocked by: None",
    },
  ];

  assert.deepEqual(
    selectReadyIssues(issues).map((issue) => issue.number),
    [1]
  );
});

test("selectReadyIssues returns only the deterministic unblocked frontier", () => {
  const issues = [
    {
      number: 34,
      state: "OPEN",
      labels: ["ready-for-agent"],
      assignees: [],
      body: "Blocked by: #20, #32",
    },
    {
      number: 13,
      state: "OPEN",
      labels: ["ready-for-agent"],
      assignees: [],
      body: "Blocked by: #10",
    },
    {
      number: 10,
      state: "OPEN",
      labels: ["ready-for-agent"],
      assignees: [],
      body: "Blocked by: None",
    },
    {
      number: 12,
      state: "OPEN",
      labels: ["ready-for-agent"],
      assignees: [],
      body: "Blocked by: #9",
    },
  ];
  const knownIssues = [
    ...issues,
    { number: 9, state: "CLOSED" },
    { number: 20, state: "OPEN" },
    { number: 32, state: "OPEN" },
  ];

  assert.deepEqual(
    selectReadyIssues(issues, knownIssues).map((issue) => issue.number),
    [10, 12]
  );
});

test("selectReadyIssues rejects unknown blockers", () => {
  const issue = {
    number: 10,
    state: "OPEN",
    labels: ["ready-for-agent"],
    assignees: [],
    body: "Blocked by: #404",
  };

  assert.deepEqual(selectReadyIssues([issue], [issue]), []);
});

test("boundedPositiveInteger enforces an unattended iteration ceiling", () => {
  assert.equal(boundedPositiveInteger(undefined, 1, 20, "iterations"), 1);
  assert.equal(boundedPositiveInteger("20", 1, 20, "iterations"), 20);
  assert.throws(() => boundedPositiveInteger("0", 1, 20, "iterations"));
  assert.throws(() => boundedPositiveInteger("21", 1, 20, "iterations"));
});
