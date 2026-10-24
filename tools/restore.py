#!/usr/bin/env python3
"""Plan or restore verified workflow files into a new/empty sandbox directory.

Default is dry-run. No network, shell execution, account import, or automatic
workflow execution. Historical absolute paths in text remain unchanged.
"""

import argparse
import json
import os
import sys
from pathlib import Path, PurePosixPath
from migration_common import MigrationError, digest, inferred_repo, inside, load_list, relative_path, validate


INSTALL_ROOTS = {
    "active-codex": ".codex/skills",
    "active-agents": ".agents/skills",
    "active-cursor": ".cursor/skills",
    "bundled-cursor": ".cursor/skills-cursor",
}


def ensure_empty_destination(destination):
    raw = Path(destination).expanduser()
    # Do not follow an existing symbolic-link destination or parent component.
    absolute = Path(os.path.abspath(str(raw)))
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        if current.is_symlink():
            # macOS exposes these fixed system-directory aliases. Resolve them
            # after this check; arbitrary user-controlled links remain refused.
            system_aliases = {
                Path("/tmp"): Path("/private/tmp"),
                Path("/var"): Path("/private/var"),
                Path("/etc"): Path("/private/etc"),
            }
            if current in system_aliases and current.resolve() == system_aliases[current]:
                continue
            raise MigrationError("Symbolic-link destination rejected: {}".format(current))
    absolute = absolute.resolve()
    if absolute.exists():
        if not absolute.is_dir():
            raise MigrationError("Destination must be a new or empty directory")
        if next(absolute.iterdir(), None) is not None:
            raise MigrationError("Destination is not empty: {}".format(absolute))
    return absolute


def skill_suffix(item):
    source, root = item.get("source"), item.get("root")
    if not isinstance(source, str) or not isinstance(root, str):
        raise MigrationError("Current skill is missing source/root metadata")
    source_p, root_p = PurePosixPath(source), PurePosixPath(root)
    if not source_p.is_absolute() or not root_p.is_absolute():
        raise MigrationError("Current skill source/root must be absolute metadata paths")
    if ".." in source_p.parts or ".." in root_p.parts:
        raise MigrationError("Traversal in skill source metadata")
    try:
        suffix = source_p.relative_to(root_p)
    except ValueError:
        raise MigrationError("Skill source is outside its recorded root")
    return relative_path(str(suffix))


def plugin_suffix(unit):
    """Use original install metadata: payload may deduplicate into archive/."""
    source = unit.get("source")
    if not isinstance(source, str):
        raise MigrationError("Current plugin is missing source metadata")
    source_p = PurePosixPath(source)
    if not source_p.is_absolute() or ".." in source_p.parts:
        raise MigrationError("Invalid current plugin source metadata")
    parts = source_p.parts
    for index in range(len(parts) - 2):
        if parts[index:index + 3] == (".codex", "plugins", "cache"):
            return relative_path(str(PurePosixPath(*parts[index + 3:])))
    raise MigrationError("Current plugin source is outside recorded Codex plugin cache")


def build_plan(repo, files, skills, profile):
    plan = {}

    def add(source, destination):
        source = str(relative_path(source))
        destination = str(relative_path(destination))
        if source not in files:
            raise MigrationError("Unrecorded source requested: {}".format(source))
        old = plan.get(destination)
        if old and files[old]["sha256"] != files[source]["sha256"]:
            raise MigrationError("Conflicting restore files: {}".format(destination))
        plan[destination] = source

    def tree(source, destination):
        source_p, destination_p = relative_path(source), relative_path(destination)
        found = 0
        prefix = str(source_p) + "/"
        for name in files:
            if name.startswith(prefix):
                suffix = PurePosixPath(name).relative_to(source_p)
                add(name, str(destination_p / suffix))
                found += 1
        if found == 0:
            raise MigrationError("No recorded payload beneath {}".format(source))

    if profile in ("current", "all"):
        # Use skill aliases as well as physical units: identical active skills may
        # point at a single deduplicated payload but need distinct install paths.
        for item in skills:
            kind = item.get("kind")
            if kind in INSTALL_ROOTS:
                install = PurePosixPath(INSTALL_ROOTS[kind]) / skill_suffix(item)
                tree(item["target"], str(install))
        for unit in load_list(repo, "source-units.json"):
            if unit.get("kind") != "plugin-codex":
                continue
            target = relative_path(unit.get("target"))
            suffix = plugin_suffix(unit)
            tree(str(target), str(PurePosixPath(".codex/plugins/cache") / suffix))

    if profile in ("projects", "all"):
        for item in load_list(repo, "projects.json"):
            target = relative_path(item.get("target"))
            if target.parts[0] != "projects":
                raise MigrationError("Project target is outside projects/: {}".format(target))
            add(str(target), str(target))

    if profile == "all":
        covered = set(plan.values())
        for name in files:
            if name.startswith(("skills/archive/", "plugins/archive/")) or name not in covered:
                add(name, "archive/" + name)
    return plan


def restore(repo, destination, profile="current", apply=False):
    destination = ensure_empty_destination(destination)
    summary, files, skills = validate(repo)
    plan = build_plan(repo, files, skills, profile)
    # Fully validate source and destination paths before writing any file.
    for target, source in plan.items():
        inside(repo, source)
        inside(destination, target)
    result = {
        "status": "restored" if apply else "dry-run",
        "profile": profile,
        "destination": str(destination),
        "planned_files": len(plan),
        "planned_bytes": sum(files[s]["bytes"] for s in plan.values()),
        "verified_snapshot": summary,
    }
    if not apply:
        return result
    # Recheck empty immediately before mutation. Exclusive file creation also
    # prevents overwriting a file introduced between planning and application.
    ensure_empty_destination(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for target, source in sorted(plan.items()):
        source_path = inside(repo, source)
        destination_path = inside(destination, target)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        inside(destination, target)
        with source_path.open("rb") as reader, destination_path.open("xb") as writer:
            for chunk in iter(lambda: reader.read(1024 * 1024), b""):
                writer.write(chunk)
        if destination_path.stat().st_size != files[source]["bytes"] or digest(destination_path) != files[source]["sha256"]:
            raise MigrationError("Restored file failed verification: {}".format(target))
        destination_path.chmod(0o755 if files[source].get("executable") else 0o644)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=str(inferred_repo(__file__)), help="Snapshot repository directory")
    parser.add_argument("--destination", required=True, help="New or empty restore sandbox; never a live home directory")
    parser.add_argument("--profile", choices=("current", "projects", "all"), default="current")
    parser.add_argument("--apply", action="store_true", help="Write files after validation; default only prints plan counts")
    args = parser.parse_args()
    try:
        result = restore(args.repo, args.destination, args.profile, args.apply)
    except (MigrationError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
