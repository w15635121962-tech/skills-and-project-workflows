#!/usr/bin/env python3
"""Temporary-fixture tests: byte integrity, safe paths, and guarded restoration."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from migration_common import MigrationError, validate
from restore import restore


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repository"
        self.catalog = self.repo / "catalog"
        self.catalog.mkdir(parents=True)
        self.data = b"# Example skill\n"
        self.sha = hashlib.sha256(self.data).hexdigest()
        self.skill_path = "skills/codex/example/SKILL.md"
        payload = self.repo / self.skill_path
        payload.parent.mkdir(parents=True)
        payload.write_bytes(self.data)
        self.record = {"path": self.skill_path, "sha256": self.sha, "bytes": len(self.data)}
        self.write("files.json", [self.record])
        self.write("skills.json", [
            {"source": "/Users/old/.codex/skills/example", "root": "/Users/old/.codex/skills", "target": "skills/codex/example", "kind": "active-codex"},
            {"source": "/Users/old/.cursor/skills/example", "root": "/Users/old/.cursor/skills", "target": "skills/codex/example", "kind": "active-cursor"},
        ])
        self.write("source-units.json", [])
        self.write("projects.json", [])

    def write(self, name, value):
        (self.catalog / name).write_text(json.dumps(value), encoding="utf-8")

    def test_success_dry_run_and_distinct_active_alias_restore(self):
        destination = self.root / "restore"
        result = restore(self.repo, destination)
        self.assertEqual(result["planned_files"], 2)
        self.assertFalse(destination.exists())
        restore(self.repo, destination, apply=True)
        for install in (".codex/skills", ".cursor/skills"):
            self.assertEqual((destination / install / "example/SKILL.md").read_bytes(), self.data)

    def test_same_length_corruption_fails_hash_check(self):
        (self.repo / self.skill_path).write_bytes(b"x" * len(self.data))
        with self.assertRaisesRegex(MigrationError, "SHA-256 mismatch"):
            validate(self.repo)

    def test_current_plugin_restores_from_deduplicated_archive_payload(self):
        self.write("source-units.json", [{
            "kind": "plugin-codex",
            "source": "/Users/old/.codex/plugins/cache/market/package/1.0",
            "target": "skills/codex/example",
        }])
        destination = self.root / "restore"
        restore(self.repo, destination, apply=True)
        self.assertEqual((destination / ".codex/plugins/cache/market/package/1.0/SKILL.md").read_bytes(), self.data)

    def test_catalog_path_escape_is_rejected(self):
        self.write("files.json", [dict(self.record, path="../outside")])
        with self.assertRaises(MigrationError):
            validate(self.repo)

    def test_skill_metadata_escape_is_rejected_without_writes(self):
        self.write("skills.json", [{"source": "/Users/old/.codex/skills/../outside", "root": "/Users/old/.codex/skills", "target": "skills/codex/example", "kind": "active-codex"}])
        destination = self.root / "restore"
        with self.assertRaises(MigrationError):
            restore(self.repo, destination, apply=True)
        self.assertFalse(destination.exists())

    def test_nonempty_destination_refuses_overwrite(self):
        destination = self.root / "restore"
        destination.mkdir()
        sentinel = destination / "existing.txt"
        sentinel.write_text("keep")
        with self.assertRaisesRegex(MigrationError, "not empty"):
            restore(self.repo, destination, apply=True)
        self.assertEqual(sentinel.read_text(), "keep")

    def test_symlinked_payload_and_destination_are_rejected(self):
        outside = self.root / "outside.txt"
        outside.write_bytes(self.data)
        payload = self.repo / self.skill_path
        payload.unlink()
        payload.symlink_to(outside)
        with self.assertRaisesRegex(MigrationError, "Symbolic link"):
            validate(self.repo)
        target = self.root / "empty"
        target.mkdir()
        link = self.root / "linked"
        link.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(MigrationError, "Symbolic-link destination"):
            restore(self.repo, link)


if __name__ == "__main__":
    unittest.main()
