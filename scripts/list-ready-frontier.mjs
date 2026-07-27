import { loadReadyFrontier } from "./lib/load-ready-frontier.mjs";

const frontier = loadReadyFrontier(process.cwd()).map((issue) => ({
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
