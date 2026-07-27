import { execFileSync } from "node:child_process";

import { selectReadyIssues } from "./ready-issues.mjs";

function ghIssueList(args, cwd) {
  return JSON.parse(
    execFileSync("gh", ["issue", "list", ...args], {
      cwd,
      encoding: "utf8",
      maxBuffer: 64 * 1024 * 1024,
    })
  );
}

export function loadReadyFrontier(cwd) {
  const candidates = ghIssueList(
    [
      "--state",
      "open",
      "--label",
      "ready-for-agent",
      "--limit",
      "1000",
      "--json",
      "number,title,body,labels,assignees,state,comments",
    ],
    cwd
  );
  const knownIssues = ghIssueList(
    ["--state", "all", "--limit", "1000", "--json", "number,state"],
    cwd
  );

  return selectReadyIssues(candidates, knownIssues);
}
