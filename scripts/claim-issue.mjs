import { spawnSync } from "node:child_process";

const [issueNumber, ...unexpectedArguments] = process.argv.slice(2);

if (!/^\d+$/.test(issueNumber ?? "") || unexpectedArguments.length > 0) {
  console.error("Usage: node scripts/claim-issue.mjs <issue-number>");
  process.exit(2);
}

const claim = spawnSync(
  "gh",
  ["issue", "edit", issueNumber, "--add-assignee", "@me"],
  { stdio: "inherit" }
);

if (claim.error) {
  console.error(claim.error.message);
  process.exit(1);
}

process.exit(claim.status ?? 1);
