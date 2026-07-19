import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const root = path.resolve(import.meta.dirname, "..");
const failures = [];

const requiredFiles = [
  "AGENTS.md",
  "CONTEXT.md",
  "docs/agents/issue-tracker.md",
  "docs/agents/triage-labels.md",
  "docs/agents/domain.md",
  "docs/adr/0001-codex-native-agentic-engineering.md",
  "docs/standards/review.md",
  ".codex/config.toml",
  ".codex/hooks.json",
  ".codex/rules/default.rules",
  ".codex/agents/researcher.toml",
  ".codex/agents/implementer.toml",
  ".codex/agents/standards_reviewer.toml",
  ".codex/agents/spec_reviewer.toml",
  ".codex/agents/rubber_duck.toml",
  ".sandcastle/main.ts",
  ".sandcastle/Dockerfile",
  ".sandcastle/plan-prompt.md",
  ".sandcastle/implement-prompt.md",
  ".sandcastle/review-prompt.md",
  ".sandcastle/spec-review-prompt.md",
  ".github/workflows/ci.yml",
  ".github/ISSUE_TEMPLATE/implementation.yml",
  ".husky/pre-commit",
];

const requiredSkills = [
  "ask-matt",
  "code-review",
  "codebase-design",
  "diagnosing-bugs",
  "domain-modeling",
  "grill-with-docs",
  "implement",
  "improve-codebase-architecture",
  "prototype",
  "research",
  "resolving-merge-conflicts",
  "setup-matt-pocock-skills",
  "tdd",
  "to-spec",
  "to-tickets",
  "triage",
  "wayfinder",
  "grill-me",
  "grilling",
  "handoff",
  "teach",
  "writing-great-skills",
  "setup-pre-commit",
  "loop-me",
  "setup-ts-deep-modules",
  "wizard",
  "rubber-duck-review",
  "workflow-retrospective",
];

for (const file of requiredFiles) {
  if (!fs.existsSync(path.join(root, file))) failures.push(`missing ${file}`);
}

for (const skill of requiredSkills) {
  const file = path.join(root, ".agents/skills", skill, "SKILL.md");
  if (!fs.existsSync(file)) {
    failures.push(`missing skill ${skill}`);
    continue;
  }
  const text = fs.readFileSync(file, "utf8");
  if (!text.startsWith("---\n") || !text.includes(`name: ${skill}`)) {
    failures.push(`invalid skill metadata for ${skill}`);
  }
}

const agents = fs.readFileSync(path.join(root, "AGENTS.md"));
if (agents.byteLength > 6000) {
  failures.push(
    `AGENTS.md is ${agents.byteLength} bytes; standing brief limit is 6000`
  );
}

const packageJson = JSON.parse(
  fs.readFileSync(path.join(root, "package.json"), "utf8")
);
if (
  packageJson.scripts?.["sandcastle:image"] !==
  "sandcastle docker build-image --image-name corvus-agentic"
) {
  failures.push("sandcastle:image must build the corvus-agentic image");
}
const sandcastleMain = fs.readFileSync(
  path.join(root, ".sandcastle/main.ts"),
  "utf8"
);
if (!sandcastleMain.includes('imageName: "corvus-agentic"')) {
  failures.push(".sandcastle/main.ts must run the corvus-agentic image");
}
if (sandcastleMain.includes("git config")) {
  failures.push("Sandcastle startup hooks must not mutate Git config");
}
const sandcastleDockerfile = fs.readFileSync(
  path.join(root, ".sandcastle/Dockerfile"),
  "utf8"
);
if (
  !sandcastleDockerfile.includes(
    'git config --system user.name "Corvus Agent"'
  ) ||
  !sandcastleDockerfile.includes(
    'git config --system user.email "agent@local.invalid"'
  )
) {
  failures.push("Sandcastle image must bake in system Git identity");
}
for (const [name, version] of Object.entries(
  packageJson.devDependencies ?? {}
)) {
  if (/^[~^*]/.test(version))
    failures.push(`${name} is not exactly pinned: ${version}`);
}

try {
  JSON.parse(fs.readFileSync(path.join(root, ".codex/hooks.json"), "utf8"));
} catch (error) {
  failures.push(`invalid .codex/hooks.json: ${error.message}`);
}

for (const secretPath of [
  ".sandcastle/.env",
  ".sandcastle/auth.json",
  ".env",
]) {
  try {
    execFileSync("git", ["check-ignore", "-q", secretPath], { cwd: root });
  } catch {
    failures.push(`${secretPath} is not ignored by git`);
  }
}

try {
  execFileSync("git", ["diff", "--check"], { cwd: root, stdio: "pipe" });
} catch (error) {
  failures.push(`git diff --check failed: ${error.stdout?.toString().trim()}`);
}

if (process.argv.includes("--github")) {
  const expected = [
    "needs-triage",
    "needs-info",
    "ready-for-agent",
    "ready-for-human",
    "wontfix",
    "wayfinder:map",
    "wayfinder:research",
    "wayfinder:prototype",
    "wayfinder:grilling",
    "wayfinder:task",
    "workflow:hitl",
    "workflow:afk",
  ];
  try {
    const output = execFileSync(
      "gh",
      ["label", "list", "--limit", "200", "--json", "name"],
      {
        cwd: root,
        encoding: "utf8",
      }
    );
    const actual = new Set(JSON.parse(output).map((label) => label.name));
    for (const label of expected) {
      if (!actual.has(label)) failures.push(`missing GitHub label ${label}`);
    }
  } catch (error) {
    failures.push(`unable to verify GitHub labels: ${error.message}`);
  }
}

if (failures.length > 0) {
  console.error("Workflow check failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log(
  `Workflow control plane OK: ${requiredSkills.length} skills, ` +
    `${requiredFiles.length} required artifacts, secrets ignored.`
);
