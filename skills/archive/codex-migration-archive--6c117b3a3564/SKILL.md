---
name: codex-migration-archive
description: Build a portable migration archive when the user says to move machines, pack all files and memories, or back up a project together with Codex memory/state.
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
2. Check whether the scope is:
   - lightweight: project files + `~/.codex/memories`
   - fuller migration: project files + selected `~/.codex` state such as `memories`, `skills`, `sessions`, `session_index.jsonl`, `config.toml`, `AGENTS.md`, sqlite state files
   - external-drive backup: project files + broader `~/.codex` copy and a separately listed database subset
3. Inspect hidden project directories and relevant `~/.codex` paths before copying so nothing important is missed.
4. If the request names a disk label such as `YS`, resolve the real mount path under `/Volumes` before copying.
5. Note whether the user needs restore notes, a manifest, database file inventory, and checksum output.

## Procedure

1. Inventory the source paths.
   - Check the project root contents, including hidden `.codex_*` folders when present.
   - Check candidate Codex paths under `~/.codex`.
2. Build a staging directory instead of relying on archive-time path rewriting.
   - Lightweight mode: create `project_files/` and `codex_memories/`.
   - Fuller migration mode: create `Projects/<project_name>/` and `CodexHome/`.
   - External-drive backup mode: create a named backup root with `项目资料/`, `Codex本地数据/`, `数据库单独备份/`, and `迁移说明/`.
3. Copy only the chosen sources into staging.
   - Always exclude `auth.json`.
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
3. If the target is an external drive, resolve the mount path first so you do not copy to a guessed location.
4. Stop expanding CodexHome scope once the user goal is met; do not add rebuildable caches by default.
5. Prefer one archive plus checksum over multiple ad hoc copies.

## Pitfalls and fixes

- Symptom: `tar --transform` fails.
  Likely cause: system `tar` does not support `--transform`.
  Fix: create the desired folder layout inside staging first, then archive the staging root.
- Symptom: important memory or hidden project folders are missing.
  Likely cause: only visible workspace files were scanned.
  Fix: inspect hidden directories and `~/.codex/memories` before packaging.
- Symptom: disk label was mentioned but copy target is missing or wrong.
  Likely cause: the path was guessed from the label instead of checking the real mount point.
  Fix: search `/Volumes` first and use the resolved mount path in all copy/archive paths.
- Symptom: sensitive login state is bundled.
  Likely cause: `~/.codex` was copied wholesale.
  Fix: explicitly exclude `auth.json` and tell the user to log in again on the new machine.
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
4. If a disk label was named, the report states the resolved mount path actually used.
5. Report explicitly states whether the package contains only `memories`, a broader `CodexHome` subset, or an external-drive backup with separate database inventory.
6. Report explicitly states that `auth.json` was excluded and re-login is required on the new machine.
7. Report explicitly states whether the work was copy-only or a true relocation.

## Minimal example

- Lightweight pattern: stage `project_files/` + `codex_memories/`, archive once, verify with listing + SHA256.
- Fuller migration pattern: stage `Projects/<project_name>/` + `CodexHome/`, add README and manifest, archive once, verify with listing + SHA256.
- External-drive pattern: resolve `/Volumes/<disk>`, stage `项目资料/` + `Codex本地数据/` + `数据库单独备份/` + `迁移说明/`, archive if useful, then spot-check key copied paths and record checksum/inventory files.
