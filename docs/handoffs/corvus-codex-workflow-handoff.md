# Corvus Codex workflow handoff

## Objective

Finish and verify the greenfield, Codex-native recreation of the agentic-engineering workflow, then report back to the user. The active goal is paused for a computer restart; do not mark it complete until the container verification below succeeds or a real blocker is established.

Repository: the current `Corvus` workspace (`/Users/<redacted>/ARCHIPELIGO/Corvus`). Treat the pre-existing Obsidian/vault material as unrelated carryover. Do not modify, reformat, or incorporate it.

## Canonical artifacts

Do not reconstruct the workflow from this handoff. Read these committed artifacts instead:

- `docs/workflow/README.md` — operating runbook
- `docs/adr/0001-codex-native-agentic-engineering.md` — design and Codex translation
- `AGENTS.md` and `CONTEXT.md` — steering and vocabulary
- `.codex/config.toml`, `.codex/agents/`, `.codex/rules/`, `.codex/hooks.json` — Codex control plane
- `.sandcastle/main.ts` and `.sandcastle/Dockerfile` — isolated AFK factory
- `package.json` — supported commands
- Commit `bc61d04` — complete implementation diff

The source PDF has already been read exhaustively and translated into those artifacts; rereading it should not be necessary unless auditing fidelity.

## Completed and verified

- Commit `bc61d04` (`Set up Codex-native agentic engineering workflow`) is pushed to `origin/main`.
- GitHub CI run `29669761709` completed successfully for that commit.
- `main` branch protection is active: strict `verify` check, one approving review, resolved conversations, linear history, no force pushes, and no deletions. Admin enforcement is intentionally off.
- Workflow labels and GitHub issue/PR templates are installed remotely.
- Twenty-six pinned upstream workflow skills plus two local skills (`rubber-duck-review`, `workflow-retrospective`) are committed under `.agents/skills/`.
- Six Codex custom agents, hooks, execution policy, pre-commit checks, two-axis review, native AFK runner, and Sandcastle orchestration are implemented.
- `npm run check` passes: workflow integrity, Prettier, TypeScript, and tests.
- GitHub YAML parses successfully.
- Codex project discovery was smoke-tested: steering, project config, skills, and custom agents load. `git push` is forbidden by project policy and issue mutation requires approval.
- `.sandcastle/auth.json` and `.sandcastle/.env` were generated with mode `0600`, are ignored, and must never be printed or committed.
- Working tree was clean except for a pre-existing user-owned `.DS_Store` modification. Leave it alone.

## Interruption state

The only unfinished item is the isolated Sandcastle image/runtime verification.

Docker Desktop had failed while installing Rosetta. During diagnosis it updated from 4.68 to 4.82. The host setting `UseVirtualizationFrameworkRosetta` was explicitly set to `false` in Docker Desktop's `settings-store.json` so its ARM-native engine could start. At handoff time `docker desktop status` reported `running`, but the user is restarting the computer so Rosetta can finish installing.

The `corvus-agentic` image has not yet been successfully built. The previous build attempt failed solely because the Docker daemon socket was unavailable.

## Resume checklist after restart

1. Confirm repository and remote state without touching `.DS_Store`:

   ```bash
   cd /Users/<redacted>/ARCHIPELIGO/Corvus
   git status --short
   git rev-parse --short HEAD
   git status -sb
   ```

   Expected history includes workflow commit `bc61d04`; expected branch: `main...origin/main`; expected only dirty path: `.DS_Store`.

2. Confirm Docker is genuinely usable, not merely reporting a UI state:

   ```bash
   docker desktop status
   docker info --format '{{.ServerVersion}} {{.Architecture}}'
   ```

   The workflow image is ARM-native and does not require Rosetta. If the user wants Rosetta acceleration, inspect the Docker Desktop setting after reboot and re-enable it only after the OS installation succeeds. Do not factory-reset Docker or delete Docker data while troubleshooting.

3. Build and inspect the pinned sandbox image:

   ```bash
   npx sandcastle docker build-image
   docker image inspect corvus-agentic --format '{{.Id}} {{.Architecture}}'
   docker run --rm --entrypoint codex corvus-agentic --version
   docker run --rm --entrypoint gh corvus-agentic --version
   ```

   Expected Codex CLI: `0.144.6`. The image must run as the non-root `agent` user; verify if needed:

   ```bash
   docker run --rm --entrypoint id corvus-agentic
   ```

4. Re-run repository and remote checks:

   ```bash
   npm run check
   node scripts/workflow-check.mjs --github
   gh run view 29669761709 --json status,conclusion,headSha
   ```

5. Optional Sandcastle end-to-end smoke: first run

   ```bash
   gh issue list --state open --label ready-for-agent
   ```

   Only run `npm run sandcastle` if the result is empty; otherwise it will intentionally begin real ticket work. With no eligible ticket it should plan an empty frontier and exit cleanly using the ignored auth files.

6. If all checks pass, make no further commit unless verification reveals a required repository fix. Report the delivered workflow, commit, CI/branch protection, safety boundaries, and the commands to start HITL (`Codex` + skills), native AFK (`npm run afk -- --max-iterations 1 --timeout-seconds 1800`), and Sandcastle (`npm run sandbox:auth && npm run sandcastle`). Explicitly mention that `.DS_Store` was preserved and excluded.

## Suggested skills

- `diagnosing-bugs` — only if Docker or the sandbox image still fails after reboot.
- `code-review` — for a final focused audit if any repository fix is needed.
- `workflow-retrospective` — after verification, to capture any reusable correction uncovered by the setup.
- `openai-docs` — only if a Codex CLI/config behavior must be revalidated against current official documentation.

## Safety notes

- Never print `.sandcastle/auth.json`, `.sandcastle/.env`, API keys, or GitHub tokens.
- Do not stage or commit `.DS_Store` or any unrelated vault content.
- Do not run a live Sandcastle ticket when merely smoke-testing.
- Do not weaken branch protection, Codex execution rules, iteration caps, or the human review boundary to make a test pass.
