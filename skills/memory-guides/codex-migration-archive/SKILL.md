---
name: codex-migration-archive
description: Build a portable project-and-Codex migration archive when the user says to move machines or pack project files together with Codex memory/state.
argument-hint: "[project_path] [mode]"
disable-model-invocation: true
user-invocable: false
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Codex Migration Archive

## When to use

Use this when the user asks for phrases like "移机", "打包所有文件和记忆", "pack all files and memories", or wants one archive containing both project files and Codex memory/state.

Do not use this when the user only wants a code export, a git bundle, or a backup of one narrow subfolder.

## Inputs / context to gather

1. Confirm the project root from `$0` or the current working directory.
2. Confirm the requested scope: project files plus selected `~/.codex` state such as `memories`, `skills`, `sessions`, `session_index.jsonl`, `config.toml`, `AGENTS.md`, and sqlite state files.
3. Inspect hidden project directories and relevant `~/.codex` paths before copying so nothing important is missed.
4. Note whether the user needs restore notes, a manifest, database file inventory, and checksum output.

## Procedure

1. Inventory the source paths.
   - Check the project root contents, including hidden `.codex_*` folders when present.
   - Check candidate Codex paths under `~/.codex`.
2. Build a staging directory instead of relying on archive-time path rewriting: create `Projects/<project_name>/` and `CodexHome/`.
3. Copy only the chosen sources into staging.
   - Exclude `auth.json` and other sensitive login state by default. Include them only when the user gives explicit, scope-specific authorization; identify the backup as sensitive in the handoff.
   - Treat `plugins`, `cache`, `logs`, `computer-use`, and other bulky rebuildable directories as optional, not default.
   - If the user explicitly asks for local databases or training/session traces, inventory and copy the relevant sqlite/jsonl files from `~/.codex` as a first-class part of the bundle.
4. If the package is meant for handoff or a fresh machine, add:
   - a restore/readme file
   - a manifest or file list
   - a database inventory when sqlite/jsonl files were a requested deliverable
5. Unless the user explicitly authorizes deletion, treat "移机/转移" as copy-and-package work, not destructive relocation.
6. Create one `.tar.gz` from the staging root when an archive is useful.
7. Verify the package.
   - List contents from the archive.
   - Generate a SHA256 checksum.
   - For directory-style external-drive backups, also spot-check the key copied paths.
8. Report the final archive path or backup root, checksum, top-level structure, and any intentionally excluded items.

## Efficiency plan

1. Start with path inventory and scope confirmation before copying large trees.
2. Reuse the same staging layout pattern rather than redesigning archive structure each time.
3. Stop expanding CodexHome scope once the user goal is met; do not add rebuildable caches by default.
4. Prefer one archive plus checksum over multiple ad hoc copies.

## Pitfalls and fixes

- Symptom: important memory or hidden project folders are missing.
  Likely cause: only visible workspace files were scanned.
  Fix: inspect hidden directories and `~/.codex/memories` before packaging.
- Symptom: sensitive login state is bundled without a clear request.
  Likely cause: `~/.codex` was copied wholesale.
  Fix: explicitly exclude `auth.json` by default and tell the user to log in again on the new machine. If they explicitly authorize its inclusion, preserve that authorization in the handoff and treat the resulting backup as sensitive.
- Symptom: bundle misses sqlite/jsonl state even though the user asked for databases or training content.
  Likely cause: only `memories/` was copied.
  Fix: inventory `~/.codex` for `*.db`, `*.sqlite`, `*.sqlite3`, and key `*.jsonl` files, then include or separately list them.
- Symptom: shell cleanup/listing command errors with `sed: bad flag in substitute command: '#'`.
  Likely cause: malformed `sed` expression in a piped inventory command.
  Fix: use the raw listing output or validate the expression separately before chaining it.
- Symptom: source data was removed even though the user only wanted a backup.
  Likely cause: "move/transfer" wording was interpreted as permission to delete.
  Fix: default to copy-only and explicitly confirm before any deletion.

## Verification checklist

1. Archive exists and is readable.
2. `tar -tzf` lists the expected top-level directories.
3. SHA256 checksum was generated and recorded.
4. Report explicitly states whether the package contains only `memories` or a broader `CodexHome` subset.
5. Report explicitly states whether `auth.json` was excluded (and re-login is required) or included under explicit user authorization (and the backup is sensitive).
6. Report explicitly states whether the work was copy-only or a true relocation.

## Minimal example

- Project archive pattern: stage `Projects/<project_name>/` + `CodexHome/`, add README and manifest, archive once, verify with listing + SHA256.
