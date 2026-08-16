import { randomBytes, createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";

import { z } from "zod";

export const runOutcomes = new Set([
  "candidate_ready",
  "stopped_for_human",
  "agent_failed",
  "verification_failed",
  "timed_out",
  "no_change",
  "invalid_agent_result",
  "orchestration_failed",
  "interrupted",
]);

const runnerSchema = z
  .object({
    name: z.string().min(1),
    version: z.string().min(1).nullable(),
    model: z.string().nullable(),
    sandbox: z.string().min(1),
    approvalPolicy: z.string().min(1),
    ephemeral: z.boolean(),
  })
  .strict();

export const manifestSchema = z
  .object({
    schemaVersion: z.literal(1),
    runId: z.string().min(1),
    workflow: z.literal("afk"),
    issueNumber: z.number().int().positive(),
    issueTitle: z.string().min(1),
    repository: z
      .object({ nameWithOwner: z.string().regex(/^[^/]+\/[^/]+$/) })
      .strict(),
    baseRevision: z.string().min(1),
    branch: z.string().min(1),
    worktree: z.string().min(1),
    startedAt: z.iso.datetime(),
    runner: runnerSchema,
    prompt: z
      .object({
        source: z.string().min(1),
        templateVersion: z.number().int().positive(),
        digest: z.string().regex(/^sha256:[a-f0-9]{64}$/),
      })
      .strict(),
  })
  .strict();

const firstFailureSchema = z
  .object({
    stage: z.string().min(1),
    kind: z.string().min(1),
    message: z.string().min(1),
  })
  .strict();

const processResultSchema = z
  .object({
    exitCode: z.number().int().nullable(),
    signal: z.string().nullable(),
    timedOut: z.boolean(),
    durationMs: z.number().int().nonnegative().nullable(),
  })
  .strict();

const externalStageSchema = processResultSchema
  .extend({
    status: z.enum(["not_run", "not_needed", "succeeded", "failed"]),
  })
  .strict();

export const summarySchema = z
  .object({
    schemaVersion: z.literal(1),
    runId: z.string().min(1),
    outcome: z.enum([...runOutcomes]),
    startedAt: z.iso.datetime(),
    finishedAt: z.iso.datetime(),
    durationMs: z.number().int().nonnegative(),
    agent: processResultSchema
      .extend({
        reportedStatus: z
          .enum(["complete", "blocked", "needs_human", "failed"])
          .nullable(),
        resultValid: z.boolean(),
      })
      .strict(),
    verification: processResultSchema
      .extend({ command: z.literal("npm run check") })
      .strict()
      .nullable(),
    externalStages: z
      .object({
        issueClaim: externalStageSchema,
        worktreeSetup: externalStageSchema,
        completionComment: externalStageSchema,
      })
      .strict(),
    git: z
      .object({
        baseRevision: z.string().min(1),
        headRevision: z.string().min(1),
        commits: z.array(z.string().min(1)),
        worktreePresent: z.boolean(),
        inspectionSucceeded: z.boolean(),
        worktreeClean: z.boolean(),
      })
      .strict(),
    artifacts: z
      .object({
        manifest: z.literal("manifest.json"),
        rawTrace: z.literal("raw/codex.jsonl"),
        stderr: z.literal("raw/codex.stderr.log"),
        agentResult: z.literal("agent-result.json"),
        checkLog: z.literal("check.log").nullable(),
      })
      .strict(),
    firstFailure: firstFailureSchema.nullable(),
  })
  .strict();

export function digestText(value) {
  return `sha256:${createHash("sha256").update(value).digest("hex")}`;
}

export function createRunId(issueNumber, now = new Date()) {
  const timestamp = now.toISOString().replaceAll(":", "-").replace(".", "-");
  return `${timestamp}-issue-${issueNumber}-${randomBytes(3).toString("hex")}`;
}

function atomicWrite(filePath, contents, mode = 0o600) {
  const temporaryPath = `${filePath}.${process.pid}.${randomBytes(3).toString("hex")}.tmp`;
  fs.writeFileSync(temporaryPath, contents, { mode });
  fs.renameSync(temporaryPath, filePath);
}

export function writeJson(filePath, value) {
  atomicWrite(filePath, `${JSON.stringify(value, null, 2)}\n`);
}

export function createRunRecord({ root, issue, manifest }) {
  const runId = manifest.runId;
  const runDirectory = path.join(root, ".agent-runs", runId);
  const rawDirectory = path.join(runDirectory, "raw");
  fs.mkdirSync(rawDirectory, { recursive: true, mode: 0o700 });
  fs.chmodSync(runDirectory, 0o700);
  fs.chmodSync(rawDirectory, 0o700);

  const paths = {
    runDirectory,
    manifest: path.join(runDirectory, "manifest.json"),
    stdout: path.join(rawDirectory, "codex.jsonl"),
    stderr: path.join(rawDirectory, "codex.stderr.log"),
    agentResult: path.join(runDirectory, "agent-result.json"),
    checkLog: path.join(runDirectory, "check.log"),
    summary: path.join(runDirectory, "summary.json"),
  };
  writeJson(
    paths.manifest,
    manifestSchema.parse({ schemaVersion: 1, ...manifest })
  );
  fs.writeFileSync(paths.stdout, "", { mode: 0o600 });
  fs.writeFileSync(paths.stderr, "", { mode: 0o600 });
  fs.writeFileSync(paths.agentResult, "", { mode: 0o600 });
  return { runId, issue, paths };
}

export function readAgentResult(filePath, schemaPath) {
  try {
    const checkedInSchema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
    const agentResultSchema = z.fromJSONSchema(checkedInSchema);
    const parsed = JSON.parse(fs.readFileSync(filePath, "utf8"));
    const validation = agentResultSchema.safeParse(parsed);
    if (!validation.success) {
      return { valid: false, value: null, error: validation.error.message };
    }
    return { valid: true, value: validation.data, error: null };
  } catch (error) {
    return {
      valid: false,
      value: null,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}

export function finalizeRun(record, summary) {
  if (!runOutcomes.has(summary.outcome)) {
    throw new Error(`Unknown Run Record outcome: ${summary.outcome}`);
  }
  writeJson(
    record.paths.summary,
    summarySchema.parse({ schemaVersion: 1, ...summary })
  );
}

export function readRunRecord(runDirectory) {
  const manifest = manifestSchema.parse(
    JSON.parse(
      fs.readFileSync(path.join(runDirectory, "manifest.json"), "utf8")
    )
  );
  const summary = summarySchema.parse(
    JSON.parse(fs.readFileSync(path.join(runDirectory, "summary.json"), "utf8"))
  );
  if (manifest.runId !== summary.runId) {
    throw new Error(`Run Record identity mismatch in ${runDirectory}`);
  }
  return { manifest, summary };
}
