import assert from "node:assert/strict";
import { chmod, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";

const claimScript = path.resolve("scripts/claim-issue.mjs");

test("claim-issue permits only one numeric issue and assigns @me", async (t) => {
  const fakeBin = await mkdtemp(path.join(tmpdir(), "corvus-claim-issue-"));
  const capturePath = path.join(fakeBin, "gh-arguments.json");
  const fakeGhPath = path.join(fakeBin, "gh");

  await writeFile(
    fakeGhPath,
    `#!/usr/bin/env node
import { writeFileSync } from "node:fs";
writeFileSync(process.env.CLAIM_CAPTURE_PATH, JSON.stringify(process.argv.slice(2)));
`
  );
  await chmod(fakeGhPath, 0o755);
  t.after(() => rm(fakeBin, { recursive: true, force: true }));

  const environment = {
    ...process.env,
    CLAIM_CAPTURE_PATH: capturePath,
    PATH: `${fakeBin}:${process.env.PATH}`,
  };

  const valid = spawnSync(process.execPath, [claimScript, "42"], {
    encoding: "utf8",
    env: environment,
  });

  assert.equal(valid.status, 0, valid.stderr);
  assert.deepEqual(JSON.parse(await readFile(capturePath, "utf8")), [
    "issue",
    "edit",
    "42",
    "--add-assignee",
    "@me",
  ]);
  await rm(capturePath);

  const invalid = spawnSync(
    process.execPath,
    [claimScript, "42", "--add-label", "ready-for-agent"],
    { encoding: "utf8", env: environment }
  );

  assert.equal(invalid.status, 2);
  assert.match(invalid.stderr, /Usage:/);
  await assert.rejects(readFile(capturePath, "utf8"), { code: "ENOENT" });
});
