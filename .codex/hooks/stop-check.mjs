import { spawnSync } from "node:child_process";

// Consume the hook event even though this check currently needs no fields.
process.stdin.resume();

const result = spawnSync("npm", ["run", "--silent", "workflow:check"], {
  cwd: process.cwd(),
  encoding: "utf8",
  timeout: 55_000,
});

if (result.status !== 0) {
  const detail = `${result.stdout || ""}\n${result.stderr || ""}`
    .trim()
    .slice(-3000);
  process.stdout.write(
    JSON.stringify({
      systemMessage: `Workflow integrity check failed before handoff. Run npm run workflow:check.\n${detail}`,
    })
  );
}
