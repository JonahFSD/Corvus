import fs from "node:fs";
import path from "node:path";
import process from "node:process";

import { readRunRecord } from "./lib/run-record.mjs";

const root = process.env.CORVUS_AFK_ROOT
  ? path.resolve(process.env.CORVUS_AFK_ROOT)
  : path.resolve(import.meta.dirname, "..");
const runsRoot = path.join(root, ".agent-runs");
const selector = process.argv[2];
const showRaw = process.argv.slice(3).includes("--raw");

if (
  !selector ||
  process.argv
    .slice(2)
    .some((argument) => ![selector, "--raw"].includes(argument))
) {
  console.error("Usage: npm run runs -- last|<run-id> [--raw]");
  process.exit(2);
}

const available = fs.existsSync(runsRoot)
  ? fs
      .readdirSync(runsRoot, { withFileTypes: true })
      .filter(
        (entry) =>
          entry.isDirectory() &&
          fs.existsSync(path.join(runsRoot, entry.name, "manifest.json")) &&
          fs.existsSync(path.join(runsRoot, entry.name, "summary.json"))
      )
      .map((entry) => entry.name)
      .sort()
  : [];
const runId = selector === "last" ? available.at(-1) : selector;

if (!runId || !available.includes(runId)) {
  console.error(
    selector === "last"
      ? "No completed Run Records found."
      : `Run Record not found: ${selector}`
  );
  process.exit(1);
}

const runDirectory = path.join(runsRoot, runId);
const { manifest, summary } = readRunRecord(runDirectory);

function display(value) {
  return String(value).replace(/[\u0000-\u001f\u007f-\u009f]/g, " ");
}

function duration(value) {
  if (value === null) return "not recorded";
  if (value < 1000) return `${value}ms`;
  const seconds = Math.round(value / 1000);
  if (seconds < 60) return `${seconds}s`;
  return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
}

const lines = [
  `Issue #${manifest.issueNumber}: ${display(manifest.issueTitle)}`,
  `Run: ${runId}`,
  `Branch: ${manifest.branch}`,
  `Base: ${manifest.baseRevision}`,
  `Head: ${summary.git.headRevision}`,
  `Outcome: ${summary.outcome}`,
  "Agent",
  `  Duration: ${duration(summary.agent.durationMs)}`,
  `  Exit: ${summary.agent.exitCode ?? summary.agent.signal ?? "not started"}`,
  `  Report: ${summary.agent.reportedStatus ?? "invalid or unavailable"}`,
];

if (summary.verification) {
  lines.push(
    "Verification",
    `  Command: ${summary.verification.command}`,
    `  Duration: ${duration(summary.verification.durationMs)}`,
    `  Exit: ${summary.verification.exitCode ?? summary.verification.signal ?? "not started"}`
  );
}

lines.push(
  `Commits: ${summary.git.commits.length}`,
  `Worktree clean: ${summary.git.worktreeClean ? "yes" : "no"}`
);
if (summary.firstFailure) {
  lines.push(
    "First failure:",
    `  ${display(summary.firstFailure.stage)}: ${display(summary.firstFailure.message)}`
  );
}
lines.push(
  "Artifacts:",
  ...Object.values(summary.artifacts)
    .filter(Boolean)
    .map((artifact) => `  ${path.join(".agent-runs", runId, artifact)}`)
);
process.stdout.write(`${lines.join("\n")}\n`);

if (showRaw) {
  for (const [label, artifact] of [
    ["Codex JSONL", summary.artifacts.rawTrace],
    ["Codex stderr", summary.artifacts.stderr],
    ["Check log", summary.artifacts.checkLog],
  ]) {
    if (!artifact) continue;
    const artifactPath = path.join(runDirectory, artifact);
    if (!fs.existsSync(artifactPath)) continue;
    process.stdout.write(`\n--- ${label} ---\n`);
    process.stdout.write(fs.readFileSync(artifactPath, "utf8"));
  }
}
