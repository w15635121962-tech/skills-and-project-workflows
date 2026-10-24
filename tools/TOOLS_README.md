These tools use Python 3.9+ and only the standard library. Put these four Python
files together in the repository's `tools/` directory.

    python3 tools/verify.py
    python3 tools/restore.py --destination /absolute/new/restore-folder
    python3 tools/restore.py --destination /absolute/new/restore-folder --apply
    python3 tools/restore.py --destination /absolute/new/project-folder --profile projects --apply
    python3 tools/restore.py --destination /absolute/new/full-folder --profile all --apply
    python3 tools/selftest.py

Use `--repo /absolute/repository` if automatic root detection does not apply.
Default restoration is a dry run and creates no destination directory. Every
profile verifies the complete recorded payload before planning a restore.

`current` restores active Codex, Agents, Cursor and bundled Cursor skills under
the destination's `.codex/skills`, `.agents/skills`, `.cursor/skills` and
`.cursor/skills-cursor`; it restores current plugin packages under
`.codex/plugins/cache`. Deduplicated active aliases are restored separately.
`projects` mirrors catalogued project workflows under `destination/projects/`,
preserving the archived absolute-source hierarchy as relative paths.
`all` combines both profiles and mirrors `skills/archive` and `plugins/archive`
beneath `destination/archive/`.

The destination must be new or completely empty. Existing files and symlinked
paths are refused. Files are copied, hash-checked, and assigned normal read or
executable permissions from the catalog. No source path is written, no workflow
is executed, no network connection is made, and no account state is imported.
Absolute old-machine paths inside text are retained as historical facts; review
and adjust them when manually installing on another machine. A successful file
restore does not establish platform login, runtime dependencies, or media output.

Self-tests use disposable temporary fixtures, including same-length corrupted
bytes, path escape attempts, deduplicated active aliases, pre-existing files,
and symbolic links. No live skill/project directory is used by these tests.
