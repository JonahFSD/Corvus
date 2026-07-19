import fs from "node:fs";
import os from "node:os";
import path from "node:path";

import * as sandcastle from "@ai-hero/sandcastle";
import { docker } from "@ai-hero/sandcastle/sandboxes/docker";
import { z } from "zod";

const planSchema = z.object({
  issues: z.array(
    z.object({ id: z.string(), title: z.string(), branch: z.string() })
  ),
});

type PlannedIssue = z.infer<typeof planSchema>["issues"][number];

function boundedInteger(
  name: string,
  fallback: number,
  maximum: number
): number {
  const parsed = Number.parseInt(process.env[name] ?? String(fallback), 10);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > maximum) {
    throw new Error(`${name} must be an integer between 1 and ${maximum}`);
  }
  return parsed;
}

const maxCycles = boundedInteger("SANDCASTLE_MAX_CYCLES", 1, 10);
const maxParallel = boundedInteger("SANDCASTLE_MAX_PARALLEL", 2, 4);
const autoMerge = process.env.SANDCASTLE_AUTO_MERGE === "1";
const runRubberDuck = process.env.SANDCASTLE_RUBBER_DUCK === "1";

const authPath = path.resolve(".sandcastle/auth.json");
const mounts = fs.existsSync(authPath)
  ? [
      {
        hostPath: authPath,
        sandboxPath: "/home/agent/.codex/auth.json",
        readonly: false,
      },
    ]
  : [];

if (mounts.length === 0 && !process.env.CODEX_API_KEY) {
  throw new Error(
    "Codex sandbox auth is missing. Copy a disposable auth.json to " +
      ".sandcastle/auth.json or set CODEX_API_KEY in .sandcastle/.env."
  );
}

const sandboxProvider = () =>
  docker({
    imageName: "corvus-agentic",
    mounts,
    cpus: 4,
  });

const hooks = {
  sandbox: {
    onSandboxReady: [
      { command: "npm ci", timeoutMs: 300_000 },
      { command: "git config user.name 'Corvus Agent'" },
      { command: "git config user.email 'agent@local.invalid'" },
    ],
  },
};

for (let cycle = 1; cycle <= maxCycles; cycle += 1) {
  console.log(`\n=== Sandcastle cycle ${cycle}/${maxCycles} ===\n`);

  const plan = await sandcastle.run({
    hooks,
    sandbox: sandboxProvider(),
    name: "planner",
    maxIterations: 1,
    agent: sandcastle.codex("gpt-5.5", { effort: "high" }),
    promptFile: ".sandcastle/plan-prompt.md",
    output: sandcastle.Output.object({ tag: "plan", schema: planSchema }),
    idleTimeoutSeconds: 600,
    completionTimeoutSeconds: 60,
    branchStrategy: {
      type: "branch",
      branch: `sandcastle/planner-${Date.now()}`,
    },
  });

  const issues: PlannedIssue[] = plan.output.issues.slice(0, maxParallel);
  if (issues.length === 0) {
    console.log("No eligible unblocked AFK issues. Exiting.");
    break;
  }

  const settled = await Promise.allSettled(
    issues.map(async (issue: PlannedIssue) => {
      const sandbox = await sandcastle.createSandbox({
        branch: issue.branch,
        sandbox: sandboxProvider(),
        hooks,
        copyToWorktree: ["node_modules"],
      });

      try {
        const implement = await sandbox.run({
          name: `implement-${issue.id}`,
          maxIterations: 1,
          agent: sandcastle.codex("gpt-5.5", { effort: "high" }),
          promptFile: ".sandcastle/implement-prompt.md",
          promptArgs: {
            TASK_ID: issue.id,
            ISSUE_TITLE: issue.title,
            BRANCH: issue.branch,
          },
          idleTimeoutSeconds: 1800,
        });

        if (implement.commits.length === 0) return implement;

        const standards = await sandbox.run({
          name: `standards-${issue.id}`,
          maxIterations: 1,
          agent: sandcastle.codex("gpt-5.5", { effort: "high" }),
          promptFile: ".sandcastle/review-prompt.md",
          promptArgs: { BRANCH: issue.branch },
          idleTimeoutSeconds: 900,
        });

        const spec = await sandbox.run({
          name: `spec-${issue.id}`,
          maxIterations: 1,
          agent: sandcastle.codex("gpt-5.5", { effort: "high" }),
          promptFile: ".sandcastle/spec-review-prompt.md",
          promptArgs: { BRANCH: issue.branch, TASK_ID: issue.id },
          idleTimeoutSeconds: 900,
        });

        const duck = runRubberDuck
          ? await sandbox.run({
              name: `rubber-duck-${issue.id}`,
              maxIterations: 1,
              agent: sandcastle.codex("gpt-5.4", { effort: "xhigh" }),
              prompt:
                `Independently critique branch ${issue.branch} for hidden ` +
                `correctness, security, and design failures. Fix only ` +
                `decision-free defects, run npm run check, commit fixes, and ` +
                `stop at diminishing returns. Output <promise>COMPLETE</promise>.`,
              idleTimeoutSeconds: 900,
            })
          : undefined;

        return {
          ...spec,
          commits: [
            ...implement.commits,
            ...standards.commits,
            ...spec.commits,
            ...(duck?.commits ?? []),
          ],
        };
      } finally {
        await sandbox.close();
      }
    })
  );

  const completed: PlannedIssue[] = settled.flatMap(
    (outcome, index): PlannedIssue[] => {
      if (outcome.status === "rejected") {
        console.error(
          `${issues[index]?.id ?? "unknown"} failed:`,
          outcome.reason
        );
        return [];
      }
      return outcome.value.commits.length > 0 ? [issues[index]!] : [];
    }
  );

  if (completed.length === 0) {
    console.log("No reviewed branches produced commits.");
    continue;
  }

  console.log("Reviewed branches ready for human diff review:");
  for (const issue of completed)
    console.log(`- ${issue.branch}: ${issue.title}`);

  if (!autoMerge) {
    console.log(
      "Automatic local merge is disabled. Read every diff, then rerun with " +
        "SANDCASTLE_AUTO_MERGE=1 if the branches are approved."
    );
    break;
  }

  await sandcastle.run({
    hooks,
    sandbox: sandboxProvider(),
    name: "merger",
    maxIterations: 1,
    agent: sandcastle.codex("gpt-5.5", { effort: "high" }),
    promptFile: ".sandcastle/merge-prompt.md",
    promptArgs: {
      BRANCHES: completed
        .map((issue: PlannedIssue) => `- ${issue.branch}`)
        .join("\n"),
      ISSUES: completed
        .map((issue: PlannedIssue) => `- ${issue.id}: ${issue.title}`)
        .join("\n"),
    },
    idleTimeoutSeconds: 1200,
    branchStrategy: { type: "head" },
    logging: {
      type: "file",
      path: path.join(
        ".sandcastle/logs",
        `merge-${Date.now()}-${os.hostname()}.log`
      ),
    },
  });
}
