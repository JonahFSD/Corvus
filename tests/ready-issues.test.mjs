import assert from "node:assert/strict";
import test from "node:test";

import { loadReadyFrontier } from "../scripts/lib/load-ready-frontier.mjs";
import {
  boundedPositiveInteger,
  parseBlockingIssueNumbers,
  selectReadyIssues,
} from "../scripts/lib/ready-issues.mjs";

const wayfinderParent = {
  number: 100,
  labels: [{ name: "wayfinder:map" }],
};

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
      labels: [{ name: "ready-for-agent" }, { name: "wayfinder:task" }],
      assignees: [],
      body: "Blocked by: None",
      parent: wayfinderParent,
    },
    {
      number: 2,
      state: "OPEN",
      labels: [{ name: "ready-for-human" }, { name: "wayfinder:task" }],
      assignees: [],
      body: "Blocked by: None",
      parent: wayfinderParent,
    },
    {
      number: 3,
      state: "OPEN",
      labels: [{ name: "ready-for-agent" }, { name: "wayfinder:grilling" }],
      assignees: [],
      body: "Blocked by: None",
      parent: wayfinderParent,
    },
    {
      number: 4,
      state: "OPEN",
      labels: [{ name: "ready-for-agent" }, { name: "wayfinder:task" }],
      assignees: [{ login: "owner" }],
      body: "Blocked by: None",
      parent: wayfinderParent,
    },
    {
      number: 5,
      state: "CLOSED",
      labels: ["ready-for-agent", "wayfinder:task"],
      assignees: [],
      body: "Blocked by: None",
      parent: wayfinderParent,
    },
  ];

  assert.deepEqual(
    selectReadyIssues(issues).map((issue) => issue.number),
    [1]
  );
});

test("selectReadyIssues requires both a Decision label and map parent", () => {
  const base = {
    state: "OPEN",
    assignees: [],
    body: "Blocked by: None",
  };
  const issues = [
    {
      ...base,
      number: 1,
      labels: ["ready-for-agent"],
      parent: wayfinderParent,
    },
    {
      ...base,
      number: 2,
      labels: ["ready-for-agent", "wayfinder:task"],
    },
    {
      ...base,
      number: 3,
      labels: ["ready-for-agent", "wayfinder:task"],
      parent: { number: 101, labels: [{ name: "not-a-map" }] },
    },
    {
      ...base,
      number: 4,
      labels: ["ready-for-agent", "wayfinder:task"],
      parent: wayfinderParent,
    },
  ];

  assert.deepEqual(
    selectReadyIssues(issues).map((issue) => issue.number),
    [4]
  );
});

test("selectReadyIssues returns only the deterministic unblocked frontier", () => {
  const issues = [
    {
      number: 34,
      state: "OPEN",
      labels: ["ready-for-agent", "wayfinder:task"],
      assignees: [],
      body: "Blocked by: #20, #32",
      parent: wayfinderParent,
    },
    {
      number: 13,
      state: "OPEN",
      labels: ["ready-for-agent", "wayfinder:task"],
      assignees: [],
      body: "Blocked by: #10",
      parent: wayfinderParent,
    },
    {
      number: 10,
      state: "OPEN",
      labels: ["ready-for-agent", "wayfinder:task"],
      assignees: [],
      body: "Blocked by: None",
      parent: wayfinderParent,
    },
    {
      number: 12,
      state: "OPEN",
      labels: ["ready-for-agent", "wayfinder:task"],
      assignees: [],
      body: "Blocked by: #9",
      parent: wayfinderParent,
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
    labels: ["ready-for-agent", "wayfinder:task"],
    assignees: [],
    body: "Blocked by: #404",
    parent: wayfinderParent,
  };

  assert.deepEqual(selectReadyIssues([issue], [issue]), []);
});

test("loadReadyFrontier maps native map parentage before selection", () => {
  const calls = [];
  const gh = (args, cwd) => {
    calls.push({ args, cwd });
    if (args[0] === "repo") {
      return { nameWithOwner: "owner/repository" };
    }
    if (args[0] === "api") {
      return {
        data: {
          repository: {
            i10: {
              parent: {
                number: 100,
                labels: { nodes: [{ name: "wayfinder:map" }] },
              },
            },
          },
        },
      };
    }
    if (args.includes("open")) {
      return [
        {
          number: 10,
          state: "OPEN",
          title: "Fixture slice",
          labels: ["ready-for-agent", "wayfinder:task"],
          assignees: [],
          body: "Blocked by: #4",
          comments: [],
        },
      ];
    }
    return [
      { number: 4, state: "CLOSED" },
      { number: 10, state: "OPEN" },
    ];
  };

  const frontier = loadReadyFrontier("/fixture/repository", gh);

  assert.equal(frontier.length, 1);
  assert.equal(frontier[0].number, 10);
  assert.deepEqual(frontier[0].parent, wayfinderParent);
  assert.equal(calls.length, 4);
  assert.ok(calls.every((call) => call.cwd === "/fixture/repository"));
});

test("boundedPositiveInteger enforces an unattended iteration ceiling", () => {
  assert.equal(boundedPositiveInteger(undefined, 1, 20, "iterations"), 1);
  assert.equal(boundedPositiveInteger("20", 1, 20, "iterations"), 20);
  assert.throws(() => boundedPositiveInteger("0", 1, 20, "iterations"));
  assert.throws(() => boundedPositiveInteger("21", 1, 20, "iterations"));
});
