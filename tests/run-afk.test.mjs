import assert from "node:assert/strict";
import {
  chmod,
  cp,
  mkdir,
  mkdtemp,
  readFile,
  readdir,
  rm,
  stat,
  writeFile,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";
import { once } from "node:events";
import test from "node:test";

const runAfkScript = path.resolve("scripts/run-afk.mjs");
const showRunsScript = path.resolve("scripts/show-runs.mjs");

async function writeExecutable(filePath, source) {
  await writeFile(filePath, `#!/usr/bin/env node\n${source}`);
  await chmod(filePath, 0o755);
}

async function createFixture(t, scenario = {}) {
  const fixtureRoot = await mkdtemp(path.join(tmpdir(), "corvus-run-afk-"));
  const fakeBin = path.join(fixtureRoot, "bin");
  const statePath = path.join(fixtureRoot, "state.json");
  const ghCallsPath = path.join(fixtureRoot, "gh-calls.jsonl");
  await mkdir(fakeBin, { recursive: true });
  await mkdir(path.join(fixtureRoot, ".codex", "schemas"), {
    recursive: true,
  });
  await cp(
    path.resolve(".codex/schemas/afk-result.schema.json"),
    path.join(fixtureRoot, ".codex", "schemas", "afk-result.schema.json")
  );
  await writeFile(
    statePath,
    JSON.stringify({ base: "a".repeat(40), head: "b".repeat(40) })
  );
  t.after(() => rm(fixtureRoot, { recursive: true, force: true }));

  await writeExecutable(
    path.join(fakeBin, "gh"),
    `
import { appendFileSync } from "node:fs";
appendFileSync(process.env.AFK_TEST_GH_CALLS, JSON.stringify(process.argv.slice(2)) + "\\n");
const args = process.argv.slice(2);
if (args[0] === "issue" && args[1] === "edit" && process.env.AFK_TEST_CLAIM_EXIT !== "0") {
  process.exit(Number(process.env.AFK_TEST_CLAIM_EXIT));
} else if (args[0] === "issue" && args[1] === "comment" && process.env.AFK_TEST_COMMENT_EXIT !== "0") {
  process.exit(Number(process.env.AFK_TEST_COMMENT_EXIT));
} else if (args[0] === "issue" && args[1] === "list" && args.includes("open")) {
  process.stdout.write(JSON.stringify([{
    number: 50,
    state: "OPEN",
    title: process.env.AFK_TEST_ISSUE_TITLE ?? "Fixture Run Record",
    body: "Blocked by: None",
    labels: [{ name: "ready-for-agent" }, { name: "wayfinder:task" }],
    assignees: [],
    comments: []
  }]));
} else if (args[0] === "issue" && args[1] === "list") {
  process.stdout.write(JSON.stringify([{ number: 50, state: "OPEN" }]));
} else if (args[0] === "repo") {
  process.stdout.write(JSON.stringify({ nameWithOwner: "owner/repository" }));
} else if (args[0] === "api") {
  process.stdout.write(JSON.stringify({ data: { repository: {
    i50: { parent: { number: 36, labels: { nodes: [{ name: "wayfinder:map" }] } } }
  } } }));
}
`
  );

  await writeExecutable(
    path.join(fakeBin, "git"),
    `
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import path from "node:path";
const args = process.argv.slice(2);
const state = JSON.parse(readFileSync(process.env.AFK_TEST_STATE, "utf8"));
const inWorktree = process.cwd().includes(path.join(".agent-runs", "worktrees"));
if (args[0] === "status") {
  if (inWorktree && existsSync(path.join(process.cwd(), ".fake-dirty"))) process.stdout.write(" M dirty.txt\\n");
} else if (args[0] === "show-ref") {
  process.exit(1);
} else if (args[0] === "worktree" && args[1] === "add") {
  if (process.env.AFK_TEST_WORKTREE_EXIT !== "0") process.exit(Number(process.env.AFK_TEST_WORKTREE_EXIT));
  const target = args[2] === "-b" ? args[4] : args[2];
  mkdirSync(target, { recursive: true });
} else if (args[0] === "rev-parse") {
  const committed = inWorktree && existsSync(path.join(process.cwd(), ".fake-commit"));
  process.stdout.write((committed ? state.head : state.base) + "\\n");
} else if (args[0] === "rev-list") {
  const committed = inWorktree && existsSync(path.join(process.cwd(), ".fake-commit"));
  if (committed && args.at(-1) === state.base + ".." + state.head) process.stdout.write(state.head + "\\n");
}
`
  );

  await writeExecutable(
    path.join(fakeBin, "codex"),
    `
import { writeFileSync } from "node:fs";
import path from "node:path";
const args = process.argv.slice(2);
if (args[0] === "--version") {
  process.stdout.write("codex-cli 9.9.9\\n");
  process.exit(0);
}
process.stdout.write('{"type":"agent_event","safe":true}\\n');
process.stderr.write("diagnostic stderr\\n");
if (process.env.AFK_TEST_MODE === "timeout") {
  setInterval(() => {}, 1000);
} else {
const finalIndex = args.indexOf("--output-last-message");
const finalPath = args[finalIndex + 1];
if (process.env.AFK_TEST_MODE === "invalid") {
  writeFileSync(finalPath, "not json");
} else if (process.env.AFK_TEST_MODE !== "missing") {
  writeFileSync(finalPath, JSON.stringify({
    reportedStatus: process.env.AFK_TEST_REPORTED_STATUS ?? "complete",
    summary: "Fixture result",
    humanDecisionRequired: process.env.AFK_TEST_REPORTED_STATUS === "needs_human",
    claimedChecks: ["npm run check"],
    handoff: "Human diff review is required."
  }));
}
if (process.env.AFK_TEST_NEW_COMMIT === "1") writeFileSync(path.join(process.cwd(), ".fake-commit"), "yes");
process.exit(Number(process.env.AFK_TEST_AGENT_EXIT ?? "0"));
}
`
  );

  await writeExecutable(
    path.join(fakeBin, "npm"),
    `
if (process.env.AFK_TEST_CHECK_MODE === "timeout") {
  setInterval(() => {}, 1000);
} else {
process.stdout.write("fixture check stdout\\n");
process.stderr.write("fixture check stderr\\n");
process.exit(Number(process.env.AFK_TEST_CHECK_EXIT ?? "0"));
}
`
  );

  return {
    fixtureRoot,
    fakeBin,
    ghCallsPath,
    environment: {
      ...process.env,
      PATH: `${fakeBin}:${process.env.PATH}`,
      CORVUS_AFK_ROOT: fixtureRoot,
      AFK_TEST_STATE: statePath,
      AFK_TEST_GH_CALLS: ghCallsPath,
      AFK_TEST_NEW_COMMIT: scenario.newCommit === false ? "0" : "1",
      AFK_TEST_AGENT_EXIT: String(scenario.agentExit ?? 0),
      AFK_TEST_CHECK_EXIT: String(scenario.checkExit ?? 0),
      AFK_TEST_CHECK_MODE: scenario.checkMode ?? "normal",
      AFK_TEST_REPORTED_STATUS: scenario.reportedStatus ?? "complete",
      AFK_TEST_CLAIM_EXIT: String(scenario.claimExit ?? 0),
      AFK_TEST_WORKTREE_EXIT: String(scenario.worktreeExit ?? 0),
      AFK_TEST_COMMENT_EXIT: String(scenario.commentExit ?? 0),
      AFK_TEST_MODE: scenario.mode ?? "normal",
      AFK_TEST_ISSUE_TITLE: scenario.issueTitle ?? "Fixture Run Record",
      AFK_TEST_SECRET: "must-not-enter-normalized-records",
    },
  };
}

async function readOnlyRun(fixtureRoot) {
  const entries = await readdir(path.join(fixtureRoot, ".agent-runs"), {
    withFileTypes: true,
  });
  const runDirectories = entries
    .filter((entry) => entry.isDirectory() && entry.name !== "worktrees")
    .map((entry) => entry.name);
  assert.equal(runDirectories.length, 1);
  const runDirectory = path.join(fixtureRoot, ".agent-runs", runDirectories[0]);
  return {
    runDirectory,
    manifest: JSON.parse(
      await readFile(path.join(runDirectory, "manifest.json"))
    ),
    summary: JSON.parse(
      await readFile(path.join(runDirectory, "summary.json"))
    ),
  };
}

test("run-afk records a verified candidate and preserves native stdout", async (t) => {
  const fixture = await createFixture(t);
  const result = spawnSync(
    process.execPath,
    [runAfkScript, "--max-iterations", "1", "--timeout-seconds", "5"],
    { encoding: "utf8", env: fixture.environment }
  );

  assert.equal(result.status, 0, result.stderr);
  const { runDirectory, manifest, summary } = await readOnlyRun(
    fixture.fixtureRoot
  );
  assert.equal(manifest.issueNumber, 50);
  assert.equal(manifest.repository.nameWithOwner, "owner/repository");
  assert.equal(manifest.runner.version, "codex-cli 9.9.9");
  assert.equal(summary.outcome, "candidate_ready");
  assert.equal(summary.agent.resultValid, true);
  assert.equal(summary.verification.exitCode, 0);
  assert.deepEqual(summary.git.commits, ["b".repeat(40)]);
  assert.equal(summary.git.inspectionSucceeded, true);
  assert.equal(summary.git.worktreeClean, true);
  assert.equal(summary.externalStages.issueClaim.status, "succeeded");
  assert.equal(summary.externalStages.worktreeSetup.status, "succeeded");
  assert.equal(summary.externalStages.completionComment.status, "succeeded");
  assert.equal(summary.firstFailure, null);
  assert.match(
    await readFile(path.join(runDirectory, "raw", "codex.jsonl"), "utf8"),
    /agent_event/
  );
  assert.doesNotMatch(
    await readFile(path.join(runDirectory, "raw", "codex.jsonl"), "utf8"),
    /diagnostic stderr/
  );
  assert.match(
    await readFile(path.join(runDirectory, "raw", "codex.stderr.log"), "utf8"),
    /diagnostic stderr/
  );
  assert.match(
    await readFile(path.join(runDirectory, "check.log"), "utf8"),
    /fixture check stdout/
  );
  assert.match(
    await readFile(path.join(runDirectory, "check.log"), "utf8"),
    /fixture check stderr/
  );
  const ghCalls = await readFile(fixture.ghCallsPath, "utf8");
  assert.match(ghCalls, /"issue","comment","50"/);
  assert.equal(
    (await stat(path.join(runDirectory, "manifest.json"))).mode & 0o777,
    0o600
  );
  assert.equal(
    (await stat(path.join(runDirectory, "summary.json"))).mode & 0o777,
    0o600
  );
  assert.equal(
    (await stat(path.join(runDirectory, "agent-result.json"))).mode & 0o777,
    0o600
  );
  assert.doesNotMatch(
    `${JSON.stringify(manifest)}${JSON.stringify(summary)}`,
    /must-not-enter-normalized-records/
  );
});

for (const scenario of [
  {
    name: "agent failure",
    options: { agentExit: 7 },
    outcome: "agent_failed",
    failureStage: "agent",
  },
  {
    name: "agent-reported failure",
    options: { reportedStatus: "failed" },
    outcome: "agent_failed",
    failureStage: "agent",
  },
  {
    name: "verification failure",
    options: { checkExit: 9 },
    outcome: "verification_failed",
    failureStage: "verification",
  },
  {
    name: "invalid final result",
    options: { mode: "invalid" },
    outcome: "invalid_agent_result",
    failureStage: "agent",
  },
  {
    name: "missing final result",
    options: { mode: "missing" },
    outcome: "invalid_agent_result",
    failureStage: "agent",
  },
  {
    name: "no commit",
    options: { newCommit: false },
    outcome: "no_change",
    failureStage: "git_inspection",
  },
]) {
  test(`run-afk classifies ${scenario.name}`, async (t) => {
    const fixture = await createFixture(t, scenario.options);
    const result = spawnSync(
      process.execPath,
      [runAfkScript, "--max-iterations", "1", "--timeout-seconds", "5"],
      { encoding: "utf8", env: fixture.environment }
    );

    assert.equal(result.status, 1);
    const { summary } = await readOnlyRun(fixture.fixtureRoot);
    assert.equal(summary.outcome, scenario.outcome);
    assert.equal(summary.firstFailure.stage, scenario.failureStage);
    assert.equal(summary.git.inspectionSucceeded, true);
    if (scenario.name === "verification failure") {
      assert.deepEqual(summary.git.commits, ["b".repeat(40)]);
      assert.equal(summary.git.headRevision, "b".repeat(40));
    }
    const ghCalls = await readFile(fixture.ghCallsPath, "utf8");
    assert.doesNotMatch(ghCalls, /"issue","comment","50"/);
  });
}

test("run-afk validates the final result against the checked-in JSON Schema", async (t) => {
  const fixture = await createFixture(t);
  const schemaPath = path.join(
    fixture.fixtureRoot,
    ".codex",
    "schemas",
    "afk-result.schema.json"
  );
  const schema = JSON.parse(await readFile(schemaPath, "utf8"));
  schema.required.push("reviewToken");
  schema.properties.reviewToken = { type: "string", minLength: 1 };
  await writeFile(schemaPath, JSON.stringify(schema));

  const result = spawnSync(
    process.execPath,
    [runAfkScript, "--max-iterations", "1", "--timeout-seconds", "5"],
    { encoding: "utf8", env: fixture.environment }
  );

  assert.equal(result.status, 1);
  const { summary } = await readOnlyRun(fixture.fixtureRoot);
  assert.equal(summary.outcome, "invalid_agent_result");
  assert.equal(summary.firstFailure.kind, "invalid_result");
});

for (const scenario of [
  {
    name: "issue claim failure",
    options: { claimExit: 8 },
    stage: "issueClaim",
    failureStage: "issue_claim",
  },
  {
    name: "worktree setup failure",
    options: { worktreeExit: 9 },
    stage: "worktreeSetup",
    failureStage: "worktree_setup",
  },
  {
    name: "completion comment failure",
    options: { commentExit: 10 },
    stage: "completionComment",
    failureStage: "completion_comment",
  },
]) {
  test(`run-afk records ${scenario.name}`, async (t) => {
    const fixture = await createFixture(t, scenario.options);
    const result = spawnSync(
      process.execPath,
      [runAfkScript, "--max-iterations", "1", "--timeout-seconds", "5"],
      { encoding: "utf8", env: fixture.environment }
    );

    assert.equal(result.status, 1);
    const { summary } = await readOnlyRun(fixture.fixtureRoot);
    assert.equal(summary.outcome, "orchestration_failed");
    assert.equal(summary.firstFailure.stage, scenario.failureStage);
    assert.equal(summary.externalStages[scenario.stage].status, "failed");
  });
}

test("run-afk does not mutate an issue when Run Record storage is unavailable", async (t) => {
  const fixture = await createFixture(t);
  await writeFile(
    path.join(fixture.fixtureRoot, ".agent-runs"),
    "not a directory"
  );

  const result = spawnSync(
    process.execPath,
    [runAfkScript, "--max-iterations", "1", "--timeout-seconds", "5"],
    { encoding: "utf8", env: fixture.environment }
  );

  assert.equal(result.status, 1);
  const ghCalls = await readFile(fixture.ghCallsPath, "utf8");
  assert.doesNotMatch(ghCalls, /"issue","edit","50"/);
});

test("run-afk stops cleanly for a human decision without claiming completion", async (t) => {
  const fixture = await createFixture(t, {
    reportedStatus: "needs_human",
    newCommit: false,
  });
  const result = spawnSync(
    process.execPath,
    [runAfkScript, "--max-iterations", "1", "--timeout-seconds", "5"],
    { encoding: "utf8", env: fixture.environment }
  );

  assert.equal(result.status, 0, result.stderr);
  const { summary } = await readOnlyRun(fixture.fixtureRoot);
  assert.equal(summary.outcome, "stopped_for_human");
  assert.equal(summary.verification, null);
  const ghCalls = await readFile(fixture.ghCallsPath, "utf8");
  assert.doesNotMatch(ghCalls, /"issue","comment","50"/);
});

test("run-afk terminates and records an agent timeout", async (t) => {
  const fixture = await createFixture(t, { mode: "timeout", newCommit: false });
  const result = spawnSync(
    process.execPath,
    [runAfkScript, "--max-iterations", "1", "--timeout-seconds", "1"],
    { encoding: "utf8", env: fixture.environment, timeout: 5000 }
  );

  assert.equal(result.status, 1, result.stderr);
  const { summary } = await readOnlyRun(fixture.fixtureRoot);
  assert.equal(summary.outcome, "timed_out");
  assert.equal(summary.agent.timedOut, true);
  assert.equal(summary.firstFailure.stage, "agent");
});

test("run-afk terminates and records a verification timeout", async (t) => {
  const fixture = await createFixture(t, { checkMode: "timeout" });
  const result = spawnSync(
    process.execPath,
    [runAfkScript, "--max-iterations", "1", "--timeout-seconds", "1"],
    { encoding: "utf8", env: fixture.environment, timeout: 5000 }
  );

  assert.equal(result.status, 1, result.stderr);
  const { summary } = await readOnlyRun(fixture.fixtureRoot);
  assert.equal(summary.outcome, "timed_out");
  assert.equal(summary.verification.timedOut, true);
  assert.equal(summary.firstFailure.stage, "verification");
});

test("run-afk records a process launch failure as orchestration failure", async (t) => {
  const fixture = await createFixture(t);
  fixture.environment.CORVUS_AFK_CODEX_COMMAND = path.join(
    fixture.fakeBin,
    "missing-codex"
  );
  const result = spawnSync(
    process.execPath,
    [runAfkScript, "--max-iterations", "1", "--timeout-seconds", "5"],
    { encoding: "utf8", env: fixture.environment }
  );

  assert.equal(result.status, 1);
  const { summary } = await readOnlyRun(fixture.fixtureRoot);
  assert.equal(summary.outcome, "orchestration_failed");
  assert.equal(summary.firstFailure.kind, "process_launch");
});

test("run-afk finalizes an interrupted Run Record", async (t) => {
  const fixture = await createFixture(t, { mode: "timeout", newCommit: false });
  const child = spawn(
    process.execPath,
    [runAfkScript, "--max-iterations", "1", "--timeout-seconds", "5"],
    { env: fixture.environment, stdio: "ignore" }
  );

  const deadline = Date.now() + 3000;
  while (Date.now() < deadline) {
    try {
      await readOnlyRun(fixture.fixtureRoot);
      break;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 25));
    }
  }
  child.kill("SIGINT");
  const [exitCode] = await once(child, "close");

  assert.equal(exitCode, 1);
  const { summary } = await readOnlyRun(fixture.fixtureRoot);
  assert.equal(summary.outcome, "interrupted");
  assert.equal(summary.firstFailure.kind, "interrupted");
});

test("run-afk derives paths from safe identifiers, not hostile issue text", async (t) => {
  const fixture = await createFixture(t, {
    issueTitle: "../../escape\nTOKEN=must-not-enter-path",
  });
  const result = spawnSync(
    process.execPath,
    [runAfkScript, "--max-iterations", "1", "--timeout-seconds", "5"],
    { encoding: "utf8", env: fixture.environment }
  );

  assert.equal(result.status, 0, result.stderr);
  const { runDirectory, manifest } = await readOnlyRun(fixture.fixtureRoot);
  assert.doesNotMatch(path.basename(runDirectory), /escape|TOKEN|\.\./);
  assert.equal(manifest.issueTitle, "../../escape\nTOKEN=must-not-enter-path");
});

test("show-runs renders the latest normalized record and explicit raw output", async (t) => {
  const fixture = await createFixture(t);
  const execution = spawnSync(
    process.execPath,
    [runAfkScript, "--max-iterations", "1", "--timeout-seconds", "5"],
    { encoding: "utf8", env: fixture.environment }
  );
  assert.equal(execution.status, 0, execution.stderr);

  const normal = spawnSync(process.execPath, [showRunsScript, "last"], {
    encoding: "utf8",
    env: fixture.environment,
  });
  assert.equal(normal.status, 0, normal.stderr);
  assert.match(normal.stdout, /Issue #50: Fixture Run Record/);
  assert.match(normal.stdout, /Outcome: candidate_ready/);
  assert.match(normal.stdout, /Verification/);
  assert.doesNotMatch(normal.stdout, /agent_event/);

  const raw = spawnSync(process.execPath, [showRunsScript, "last", "--raw"], {
    encoding: "utf8",
    env: fixture.environment,
  });
  assert.equal(raw.status, 0, raw.stderr);
  assert.match(raw.stdout, /agent_event/);
  assert.match(raw.stdout, /diagnostic stderr/);
});
