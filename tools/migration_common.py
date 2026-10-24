#!/usr/bin/env python3
"""Offline, standard-library helpers for this migration snapshot."""

import hashlib
import json
import re
from pathlib import Path, PurePosixPath, PureWindowsPath


class MigrationError(Exception):
    pass


def relative_path(value):
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise MigrationError("Invalid relative path: {!r}".format(value))
    p = PurePosixPath(value)
    if p.is_absolute() or PureWindowsPath(value).drive or str(p) != value:
        raise MigrationError("Noncanonical or absolute path: {!r}".format(value))
    if any(part in ("", ".", "..") for part in p.parts):
        raise MigrationError("Path traversal rejected: {!r}".format(value))
    return p


def inside(root, value):
    """Reject traversal and symlinks, including symlinked parent components."""
    relative = relative_path(value)
    root = Path(root).resolve()
    candidate = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise MigrationError("Symbolic link rejected: {}".format(current))
    try:
        candidate.resolve().relative_to(root)
    except ValueError:
        raise MigrationError("Path escapes root: {!r}".format(value))
    return candidate


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_list(repo, name):
    p = inside(repo, "catalog/" + name)
    try:
        value = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise MigrationError("Cannot read {}: {}".format(p, error))
    if not isinstance(value, list) or not all(isinstance(x, dict) for x in value):
        raise MigrationError("{} must contain a JSON list of objects".format(name))
    return value


def validate(repo):
    """Validate all recorded payload bytes and every catalogued skill entry."""
    repo = Path(repo).resolve()
    files = load_list(repo, "files.json")
    skills = load_list(repo, "skills.json")
    index, hashes, errors = {}, {}, []
    total = 0
    for item in files:
        try:
            name = str(relative_path(item.get("path")))
            if name in index:
                raise MigrationError("Duplicate file entry: {}".format(name))
            index[name] = item
            size = item.get("bytes")
            sha = item.get("sha256")
            if isinstance(size, bool) or not isinstance(size, int) or size < 0:
                raise MigrationError("Invalid byte count: {}".format(name))
            if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{64}", sha):
                raise MigrationError("Invalid SHA-256: {}".format(name))
            path = inside(repo, name)
            if not path.is_file():
                raise MigrationError("Missing payload file: {}".format(name))
            if path.stat().st_size != size:
                raise MigrationError("Byte count mismatch: {}".format(name))
            actual = digest(path)
            if actual != sha:
                raise MigrationError("SHA-256 mismatch: {}".format(name))
            hashes[name] = actual
            total += size
        except (MigrationError, OSError) as error:
            errors.append(str(error))
    for item in skills:
        try:
            target = relative_path(item.get("target"))
            name = str(target / "SKILL.md")
            path = inside(repo, name)
            if not path.is_file() or name not in index:
                raise MigrationError("Skill entry missing recorded SKILL.md: {}".format(name))
            expected = item.get("migrated_skill_md_sha256")
            if expected and hashes.get(name) and hashes[name] != expected:
                raise MigrationError("Skill SHA-256 mismatch: {}".format(name))
        except (MigrationError, OSError) as error:
            errors.append(str(error))
    if errors:
        preview = "\n".join("- " + error for error in errors[:25])
        if len(errors) > 25:
            preview += "\n- ... {} additional errors".format(len(errors) - 25)
        raise MigrationError("Snapshot verification failed ({} errors):\n{}".format(len(errors), preview))
    return {"files": len(files), "skills": len(skills), "bytes": total}, index, skills


def inferred_repo(script):
    """Support tools/verify.py or a script placed directly at repository root."""
    folder = Path(script).resolve().parent
    for candidate in (folder.parent, folder):
        if (candidate / "catalog" / "files.json").is_file():
            return candidate
    return folder.parent
