# Technical Overview

This document explains how the patch works for readers who:

- have basic programming experience,
- do not know Node.js or TypeScript well,
- have not read the OpenClaw source code,
- but want to understand the rough mechanism and where the change happens.

## What problem this patch solves

OpenClaw can send requests to OpenAI-style Responses endpoints.

In the installed OpenClaw bundle, there is logic that may remove these request fields before the request is sent out:

- `prompt_cache_key`
- `prompt_cache_retention`

For official OpenAI this may be acceptable, but for some third-party OpenAI-compatible Responses endpoints, those fields are still useful and should be preserved.

This patch changes OpenClaw so those fields are no longer stripped out just because the endpoint is third-party.

## The big idea

This is a **local hotfix**.

It does **not**:

- change OpenClaw config,
- change the provider server,
- change model behavior,
- or patch upstream OpenClaw source code in a development repository.

Instead, it directly patches the **already installed OpenClaw runtime bundle** on a machine.

In practice, that means it edits JavaScript files under OpenClaw's installed `dist/` directory.

## Why patch `dist/` instead of source code?

OpenClaw is developed in source form, but the installed application actually runs the compiled and bundled files in `dist/`.

So if the goal is:

- fix one machine quickly,
- avoid rebuilding OpenClaw from source,
- and keep the workflow simple,

then patching the installed bundle is the most direct route.

The tradeoff is that this is not a permanent upstream fix. If OpenClaw is upgraded or reinstalled, the bundle may change and the patch may need to be applied again.

## Where in the request lifecycle the change happens

The patch affects the **outbound request preparation stage**.

A simplified flow looks like this:

```text
Caller / agent
  -> OpenClaw builds a Responses request
  -> OpenClaw decides which fields to keep or strip
  -> OpenClaw sends the request to the provider
  -> Provider returns a response
```

This patch changes the middle step:

```text
OpenClaw decides which fields to keep or strip
```

So the patch is applied **before the HTTP request leaves OpenClaw**, not after the response comes back.

## The exact logic being changed

The patch scripts look for this function inside the installed bundle:

```js
function shouldStripResponsesPromptCache(model) {
  ...
}
```

Inside that function, the original bundle is expected to contain this line:

```js
return !isDirectOpenAIBaseUrl(model.baseUrl);
```

That means, roughly:

- if the `baseUrl` is not the direct official OpenAI base URL,
- OpenClaw decides prompt-cache hints should be stripped.

The patch replaces that return line with:

```js
return false;
```

That means:

- do not strip prompt-cache fields based on that check,
- let `prompt_cache_key` and `prompt_cache_retention` continue through the outbound request path.

## What this patch does and does not guarantee

What it does:

- stops OpenClaw from removing those two fields at this bundle layer,
- allows third-party OpenAI-compatible Responses endpoints to receive them.

What it does not do:

- guarantee the downstream provider supports those fields,
- guarantee the provider will actually use them,
- implement a cache system by itself.

So this patch fixes the **field preservation path**, not the cache behavior of the provider.

## How the scripts work

The main scripts live under:

- `skill/responses-third-party-prompt-cache-patch/scripts/patch_prompt_cache.py`
- `skill/responses-third-party-prompt-cache-patch/scripts/revert_prompt_cache.py`
- `skill/responses-third-party-prompt-cache-patch/scripts/_bundle_patch_common.py`

### `patch_prompt_cache.py`

This script:

1. finds the installed OpenClaw root,
2. locates the `dist/` directory,
3. scans bundle files for `shouldStripResponsesPromptCache(model)`,
4. verifies the function still has the expected shape,
5. creates a timestamped backup,
6. writes the narrow patch,
7. runs `node --check` on the modified bundle,
8. restores the backup automatically if syntax validation fails.

### `revert_prompt_cache.py`

This script:

1. finds currently patched bundles,
2. locates the latest matching backup,
3. restores the original file,
4. validates the restored bundle with `node --check`.

## Why this is relatively safe for a hotfix

The scripts do not do a blind global search-and-replace.

They only patch when all of these are true:

- the target function exists,
- the expected original return line is present,
- the file shape still matches the known patch point.

If the bundle no longer matches the expected shape, the script refuses to continue instead of guessing.

That matters because installed bundles can change across OpenClaw versions.

## Why a restart is required

The scripts modify files on disk, but a running OpenClaw gateway may already have the old bundle loaded in memory.

So after apply or rollback, you must restart the gateway so the process reloads the modified bundle.

In short:

- file changed on disk != running process already using it
- restart makes the running gateway load the new code

## Upgrade behavior

Because this patch targets installed bundle files, OpenClaw upgrades can replace the patched file with a new bundle.

The scripts are written to recognize this situation:

- they can detect historical backups,
- they can detect that a new current bundle is unpatched,
- and they can reapply the patch to the new target bundle when the function is still identifiable.

That is why the repo describes the workflow as **upgrade-aware reapply**, not as a one-time permanent fix.

## One-sentence summary

This repo applies a narrow local patch to OpenClaw's installed outbound Responses request logic so `prompt_cache_key` and `prompt_cache_retention` survive the bundle layer and can reach third-party OpenAI-compatible endpoints.
