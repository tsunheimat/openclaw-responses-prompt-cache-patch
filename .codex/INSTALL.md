# Installing responses-third-party-prompt-cache-patch for OpenClaw

Install the skill files first, then run the patch. **Copying the skill into `~/.openclaw/workspace/skills/` does not enable the patch by itself.**

## Prerequisites

- Git or another way to copy this repo onto the target machine
- Python 3
- Node.js
- OpenClaw already installed on the target machine
- Permission to modify the installed OpenClaw `dist/` bundle

## Installation

1. **Get a local copy of this repo onto the target machine.**
   - If you are reading this on GitHub, use **Code → Download ZIP** and unpack it, or clone with the real URL shown on the repo page.
   - If you already have a checkout elsewhere, `scp` / `rsync` it onto the target machine.

2. **From the cloned or unpacked repo root, install the skill into the OpenClaw workspace:**
   ```bash
   mkdir -p ~/.openclaw/workspace/skills
   cp -R ./skill/responses-third-party-prompt-cache-patch ~/.openclaw/workspace/skills/
   ```

3. **Enter the installed skill directory:**
   ```bash
   cd ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch
   ```

4. **Verify the patch target with a dry run:**
   ```bash
   python3 scripts/patch_prompt_cache.py --dry-run
   ```

5. **Apply the patch for real:**
   ```bash
   python3 scripts/patch_prompt_cache.py
   ```

6. **Restart OpenClaw Gateway so the patched bundle is loaded:**
   ```bash
   openclaw gateway restart
   ```

## Rollback

Run from the installed skill directory:

```bash
cd ~/.openclaw/workspace/skills/responses-third-party-prompt-cache-patch
python3 scripts/revert_prompt_cache.py
openclaw gateway restart
```

## Common notes

- **Install skill != patch active.** The patch only takes effect after `patch_prompt_cache.py` runs successfully.
- **This modifies installed `dist/` files.** Treat it like a local hotfix, not a config toggle.
- **OpenClaw upgrades may replace the patched bundle.** Re-run the dry-run and reapply after upgrades when needed.
- **Restart is required after apply and rollback.** Without a restart, the running gateway may still use the previous bundle.
- **Use `--root /path/to/openclaw` if needed.** That is useful for testing against a copied fixture or a non-default installation.
- **Dry-run is the safe first step.** It confirms the target bundle is discoverable before any write happens.

## Optional packaging/distribution note

The skill content itself lives under `skill/responses-third-party-prompt-cache-patch/`. That layout keeps the skill clean for future packaging or alternative distribution channels such as ClawHub, without requiring you to publish there now.
