---
name: restore-codex-browser-plugin
description: Recover a missing versioned Codex in-app Browser plugin from the installed ChatGPT app, then diagnose whether a remaining failure is site permission rather than runtime. Obtain authorization before copying plugin files.
allowed-tools: Read, Grep, Glob, Bash
---

# Restore Codex Browser Plugin

## When to use

Use when Codex desktop browser startup reports a missing versioned `browser-service.mjs`, or an in-app Browser tool cannot start because its cached `openai-bundled/browser/<version>` directory is incomplete. Do not use to bypass website permissions, cookies, or authentication.

## Inputs and first checks

1. Record the exact requested browser version and missing path from the runtime error.
2. Inspect `/Users/xuan/.codex/plugins/cache/openai-bundled/browser/` and confirm the requested version is missing or incomplete.
3. Confirm the local official source exists: `/Applications/ChatGPT.app/Contents/Resources/plugins/openai-bundled/plugins/browser`.
4. Obtain authorization before copying files into the Codex plugin cache.

## Procedure

1. Do not redirect configuration to an older cached browser version; such edits can be overwritten after restart.
2. Copy only the official application-bundled browser plugin into the exact cache version requested by the runtime.
3. Verify the copied tree is complete by comparing source and destination file inventory and content. The two observed recoveries each verified 383 files, but discover the actual count rather than assuming it.
4. Restart or reconnect the browser runtime and verify that it returns `Codex In-app Browser` or can enumerate the intended tab.
5. If the runtime works but a page reports `Browser Use could not request permission` or `saved browser permissions could not be verified`, stop treating this as a plugin issue. Check the application's Browser/site permission for the domain, restart if appropriate, and use `/feedback` if it remains blocked.

## Efficiency plan

- Use the exact error path as the version selector; inspect source and destination once before copying.
- Stop after a verified runtime recovery if the user did not request website operation.
- Do not retry project actions until accessibility tooling can read the actual page state (for example, `tab.ax.write()` succeeds).

## Pitfalls and fixes

- Temporary config path change disappears after restart -> restore the exact versioned cache from the official app bundle instead.
- Browser can enumerate a tab but cannot read its page -> runtime recovery succeeded; resolve the site-permission blocker separately.
- Permission error on a protected site -> never access cookies, tokens, permission databases, or non-authorized controls to bypass it.

## Verification checklist

- The exact requested `scripts/browser-service.mjs` exists under the expected cache version.
- Source and installed plugin inventories/content were compared successfully.
- Browser runtime reconnects successfully.
- If website access was the goal, the page is actually readable; otherwise explicitly report that runtime recovery does not establish page access.
