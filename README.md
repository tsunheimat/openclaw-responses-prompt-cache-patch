# responses-third-party-prompt-cache-patch

A GitHub-ready wrapper repo for the `responses-third-party-prompt-cache-patch` OpenClaw skill.

This skill applies a **local patch** to an **installed OpenClaw dist bundle** so third-party OpenAI-compatible Responses endpoints keep `prompt_cache_key` and `prompt_cache_retention` instead of having them stripped.

中文版本：[README.zh-TW.md](README.zh-TW.md)

ClawHub: [responses-third-party-prompt-cache-patch](https://clawhub.ai/tsunheimat/responses-third-party-prompt-cache-patch)

## Quick install for OpenClaw

Install the skill into the default OpenClaw workspace:

```bash
clawhub install responses-third-party-prompt-cache-patch --workdir ~/.openclaw/workspace
```

After install, follow the apply workflow below or use the OpenClaw paste-in instruction.

## Paste this into OpenClaw

Use this one-liner if you want OpenClaw to fetch the install guide and carry out the install/apply workflow on the target machine:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/tsunheimat/openclaw-responses-prompt-cache-patch/refs/heads/main/.openclaw/INSTALL.md
```

Use the **raw** URL, not the GitHub `blob/...` page. The `.openclaw/INSTALL.md` file is written as an OpenClaw-specific execution guide: install the skill, run dry-run, apply the patch, restart the gateway, and report the result.

## Who this is for

Use this if you:

- run OpenClaw on your own machine or server,
- use a third-party OpenAI-compatible Responses endpoint,
- need prompt-cache hints to survive the OpenClaw bundle layer,
- are okay applying a local patch to the installed OpenClaw `dist/` files.

Do **not** use this if you want an upstream OpenClaw code change, a config-only fix, or a published marketplace install flow.

## What this repo contains

```text
.
├── .openclaw/INSTALL.md
├── .gitignore
├── README.md
└── skill/
    └── responses-third-party-prompt-cache-patch/
        ├── SKILL.md
        └── scripts/
            ├── _bundle_patch_common.py
            ├── patch_prompt_cache.py
            └── revert_prompt_cache.py
```

The public-facing repo docs live at the repo root. The installable skill stays clean under `skill/responses-third-party-prompt-cache-patch/` so it can still be packaged or distributed separately.

## Additional docs

- Technical walkthrough: [docs/TECHNICAL-OVERVIEW.md](docs/TECHNICAL-OVERVIEW.md)
- Disclaimer: [docs/DISCLAIMER.md](docs/DISCLAIMER.md)

## Important risks

- The apply script writes directly into the installed OpenClaw `dist/` directory.
- The patch is **local**, not upstream. OpenClaw upgrades or reinstalls may require you to apply it again.
- You must restart the gateway after apply or rollback:
  ```bash
  openclaw gateway restart
  ```
- Installing the skill folder alone does **not** activate the patch. You must run the apply script.

## Install onto another OpenClaw machine

1. Get a local copy of this repo onto the target machine. If you are viewing it on GitHub, use **Code → Download ZIP**, clone with the real URL shown on the page, or copy an existing checkout with `scp` / `rsync`.
2. From the cloned or unpacked repo root, copy the skill into the OpenClaw workspace skills directory:
   ```bash
   mkdir -p ~/.openclaw/workspace/skills
   cp -R ./skill/responses-third-party-prompt-cache-patch ~/.openclaw/workspace/skills/
   ```
3. Move into the installed skill directory:
   ```bash
   cd ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch
   ```
4. Dry-run first:
   ```bash
   python3 scripts/patch_prompt_cache.py --dry-run
   ```
5. Apply the patch:
   ```bash
   python3 scripts/patch_prompt_cache.py
   ```
6. Restart OpenClaw Gateway:
   ```bash
   openclaw gateway restart
   ```

For the OpenClaw-specific install/apply playbook, see [.openclaw/INSTALL.md](.openclaw/INSTALL.md).

Direct raw URL:
`https://raw.githubusercontent.com/tsunheimat/openclaw-responses-prompt-cache-patch/refs/heads/main/.openclaw/INSTALL.md`

## Apply / rollback commands

Run these from the installed skill directory:

```bash
cd ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch
python3 scripts/patch_prompt_cache.py --dry-run
python3 scripts/patch_prompt_cache.py
openclaw gateway restart
```

Rollback:

```bash
cd ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch
python3 scripts/revert_prompt_cache.py
openclaw gateway restart
```

## Notes for distribution

- This repo is meant to be a clean GitHub distribution wrapper.
- If the skill is later published to ClawHub, that can become an additional install path, but this repo remains a manual fallback and source-of-truth-friendly distribution channel.
- The patch and rollback logic are intentionally kept in the skill scripts; this repo does not change their behavior.
