# OpenClaw install/apply playbook for `responses-third-party-prompt-cache-patch`

This file is for an **OpenClaw agent running on the target machine**.

Do the work on the machine. Do **not** only restate these instructions.

## Mission

Install this skill from:

- Repo: `https://github.com/tsunheimat/openclaw-responses-prompt-cache-patch.git`
- Skill subdirectory: `skill/responses-third-party-prompt-cache-patch`

Then apply the patch so the local OpenClaw installation keeps these Responses fields for supported third-party OpenAI-compatible endpoints:

- `prompt_cache_key`
- `prompt_cache_retention`

## Operator intent

When this file is fetched via a prompt like:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/tsunheimat/openclaw-responses-prompt-cache-patch/refs/heads/main/.openclaw/INSTALL.md
```

interpret that as permission to perform the install/apply workflow on the current machine.

## Rules

- Act on the current machine.
- Execute the workflow; do not stop at explanation only.
- Run a dry-run before the real patch.
- Stop on the first hard failure and report it clearly.
- Prefer backup/replace over destructive deletion.
- Restart OpenClaw Gateway after apply or rollback.
- If a dependency or permission is missing, report the blocker precisely.

## Success criteria

The task is successful only if all of the following are true:

1. The skill is installed at `~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch`
2. `python3 scripts/patch_prompt_cache.py --dry-run` succeeds
3. `python3 scripts/patch_prompt_cache.py` succeeds
4. `openclaw gateway restart` succeeds
5. The result is reported back with status and any warnings

## Step 1 — Preflight checks

Confirm these commands exist before modifying anything:

```bash
command -v git
command -v python3
command -v node
command -v openclaw
```

If any command is missing, stop and report exactly which dependency is missing.

## Step 2 — Fetch or update the repo in a temporary working path

Use `/tmp/openclaw-responses-prompt-cache-patch` as the working checkout.

If it already contains a git checkout, update it:

```bash
cd /tmp/openclaw-responses-prompt-cache-patch && git pull --ff-only
```

Otherwise, create a fresh checkout:

```bash
git clone https://github.com/tsunheimat/openclaw-responses-prompt-cache-patch.git /tmp/openclaw-responses-prompt-cache-patch
```

If `/tmp/openclaw-responses-prompt-cache-patch` exists but is not a usable git checkout, move it aside with a timestamp suffix and then clone fresh.

## Step 3 — Install or update the skill in the OpenClaw workspace

Create the local skills directory if needed:

```bash
mkdir -p ~/.openclaw/workspace/skills
```

If an older installed skill already exists, move it aside as a backup:

```bash
if [ -d ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch ]; then
  mv ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch.backup-$(date +%Y%m%d-%H%M%S)
fi
```

Copy the skill into place:

```bash
cp -R /tmp/openclaw-responses-prompt-cache-patch/skill/responses-third-party-prompt-cache-patch ~/.openclaw/workspace/skills/
```

## Step 4 — Enter the installed skill directory

```bash
cd ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch
```

## Step 5 — Dry-run the patch

Run:

```bash
python3 scripts/patch_prompt_cache.py --dry-run
```

If the dry-run fails, stop here and report the failure. Do not continue to the real apply step.

## Step 6 — Apply the patch for real

Run:

```bash
python3 scripts/patch_prompt_cache.py
```

## Step 7 — Restart OpenClaw Gateway

Run:

```bash
openclaw gateway restart
```

## Step 8 — Basic post-apply verification

Confirm the gateway is up:

```bash
openclaw gateway status
```

If the patch script reported specific patched bundle paths, include them in the final report.

## Final report format

Report back in a concise status block like this:

```text
install: success|failed
dry_run: success|failed
apply: success|failed
gateway_restart: success|failed
gateway_status: success|failed
patched_bundles:
- <path>
warnings:
- <warning or none>
blockers:
- <blocker or none>
```

## Rollback

If the user asks to revert the patch, run:

```bash
cd ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch
python3 scripts/revert_prompt_cache.py
openclaw gateway restart
openclaw gateway status
```

Then report the rollback result clearly.

## Notes

- This is a **local hotfix**, not an upstream OpenClaw change.
- Copying the skill into `~/.openclaw/workspace/skills/` does **not** activate the patch by itself.
- OpenClaw upgrades or reinstalls may replace the patched bundle; if that happens, repeat the dry-run and apply workflow.
- Use `--root /path/to/openclaw` only when the user explicitly wants to target a non-default installation or a copied fixture.
