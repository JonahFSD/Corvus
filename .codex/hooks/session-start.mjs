import fs from "node:fs";
import path from "node:path";

let event = {};
try {
  event = JSON.parse(fs.readFileSync(0, "utf8") || "{}");
} catch {
  // A malformed hook payload should warn, never prevent a session from starting.
}

const root = event.cwd || process.cwd();
const required = [
  "AGENTS.md",
  "CONTEXT.md",
  ".codex/config.toml",
  "docs/agents/issue-tracker.md",
];
const missing = required.filter(
  (file) => !fs.existsSync(path.join(root, file))
);

if (missing.length > 0) {
  process.stdout.write(
    JSON.stringify({
      systemMessage: `Workflow control plane is incomplete: missing ${missing.join(", ")}.`,
    })
  );
}
