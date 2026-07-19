import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const sandboxDir = path.join(root, ".sandcastle");
const sourceAuth = path.join(os.homedir(), ".codex", "auth.json");
const targetAuth = path.join(sandboxDir, "auth.json");

if (!fs.existsSync(sourceAuth)) {
  throw new Error(
    "No ~/.codex/auth.json found. Run codex login or provide CODEX_API_KEY."
  );
}

fs.copyFileSync(sourceAuth, targetAuth);
fs.chmodSync(targetAuth, 0o600);

const ghToken = execFileSync("gh", ["auth", "token"], {
  cwd: root,
  encoding: "utf8",
}).trim();
const codexApiKey = process.env.CODEX_API_KEY ?? "";
const envBody = `CODEX_API_KEY=${codexApiKey}\nGH_TOKEN=${ghToken}\n`;
fs.writeFileSync(path.join(sandboxDir, ".env"), envBody, { mode: 0o600 });

console.log(
  "Created ignored, mode-0600 Sandcastle auth files without printing secrets."
);
