import { execFileSync } from "node:child_process";

import { selectReadyIssues } from "./lib/ready-issues.mjs";

function gh(args) {
  return JSON.parse(
    execFileSync("gh", args, {
      cwd: process.cwd(),
      encoding: "utf8",
      maxBuffer: 64 * 1024 * 1024,
    })
  );
}

const candidates = gh([
  "issue",
  "list",
  "--state",
  "open",
  "--label",
  "ready-for-agent",
  "--limit",
  "1000",
  "--json",
  "number,title,body,labels,assignees,state,comments",
]);
const knownIssues = gh([
  "issue",
  "list",
  "--state",
  "all",
  "--limit",
  "1000",
  "--json",
  "number,state",
]);

const frontier = selectReadyIssues(candidates, knownIssues).map((issue) => ({
  number: issue.number,
  title: issue.title,
  body: issue.body,
  labels: issue.labels.map((label) =>
    typeof label === "string" ? label : label.name
  ),
  assignees: issue.assignees.map((assignee) =>
    typeof assignee === "string" ? assignee : assignee.login
  ),
  comments: issue.comments.map((comment) =>
    typeof comment === "string" ? comment : comment.body
  ),
}));

process.stdout.write(`${JSON.stringify(frontier)}\n`);
