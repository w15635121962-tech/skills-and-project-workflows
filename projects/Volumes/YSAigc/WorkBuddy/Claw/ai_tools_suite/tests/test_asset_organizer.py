"""
测试 AssetOrganizer 模块
使用真实文件系统进行集成测试（tmp_path）
"""
import os
import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
from collections import defaultdict

from modules.asset_organizer import AssetOrganizer


def _create_test_outputs(tmp_path):
    """创建测试用的 outputs/ 目录结构"""
    outputs = tmp_path / "outputs"

    bella_dir = outputs / "characters" / "Bella"
    bella_dir.mkdir(parents=True)
    (bella_dir / "Bella_front_001.png").write_bytes(b"fake_png")
    (bella_dir / "Bella_side_002.png").write_bytes(b"fake_png")
    (bella_dir / "Bella_front_003.png").write_bytes(b"fake_png")
    (bella_dir / "metadata.json").write_text('{"seed": 12345}')

    luca_dir = outputs / "characters" / "Luca"
    luca_dir.mkdir(parents=True)
    (luca_dir / "Luca_001.png").write_bytes(b"fake_png")

    scenes_dir = outputs / "scenes"
    scenes_dir.mkdir(parents=True)
    (scenes_dir / "Hospital_001.png").write_bytes(b"fake_png")

    (outputs / "unsorted_001.png").write_bytes(b"fake_png")
    (outputs / "unsorted_002.jpg").write_bytes(b"fake_jpg")
    (outputs / "readme.txt").write_text("not an image")

    return outputs


def _make_organizer(tmp_path, outputs_dir=None):
    outputs = outputs_dir or _create_test_outputs(tmp_path)
    return AssetOrganizer(input_dir=str(outputs), output_dir=str(tmp_path / "organized"))


# ===================================================================
# 初始化测试
# ===================================================================
class TestAssetOrganizerInit:
    def test_init_with_dirs(self, tmp_path):
        outputs = _create_test_outputs(tmp_path)
        organizer = AssetOrganizer(input_dir=str(outputs), output_dir=str(tmp_path / "organized"))
        assert organizer.input_dir == str(outputs)
        assert organizer.output_dir == str(tmp_path / "organized")

    def test_init_creates_defaults(self):
        organizer = AssetOrganizer()
        assert organizer.input_dir == "../outputs/"
        assert organizer.output_dir == "../outputs/organized/"

    def test_scan_directory(self, tmp_path):
        organizer = _make_organizer(tmp_path)
        files = organizer._scan_directory(str(tmp_path / "outputs"))
        image_files = [f for f in files if f.endswith(('.png', '.jpg'))]
        assert len(image_files) >= 5

    def test_extensions_mapping(self, tmp_path):
        organizer = _make_organizer(tmp_path)
        assert '.png' in organizer.extensions['image']
        assert '.mp4' in organizer.extensions['video']
        assert '.obj' in organizer.extensions['3d']


# ===================================================================
# 分类测试
# ===================================================================
class TestCategorize:
    def test_categorize_files_by_name(self, tmp_path):
        organizer = _make_organizer(tmp_path)
        files = organizer._scan_directory(str(tmp_path / "outputs"))
        categories = organizer._categorize_files(files)

        assert 'character' in categories
        char_files = categories['character']
        assert any('Bella' in f for f in char_files)

    def test_categorize_scene_files(self, tmp_path):
        organizer = _make_organizer(tmp_path)
        files = organizer._scan_directory(str(tmp_path / "outputs"))
        categories = organizer._categorize_files(files)

        if 'scene' in categories:
            scene_files = categories['scene']
            assert any('Hospital' in f for f in scene_files)


# ===================================================================
# 整理测试
# ===================================================================
class TestOrganize:
    def test_organize_dry_run(self, tmp_path):
        organizer = _make_organizer(tmp_path)
        stats = organizer.organize(dry_run=True)

        assert "total" in stats
        assert stats["total"] > 0
        # 验证至少有 by_category 统计
        assert len(stats.get("by_category", {})) > 0

    def test_organize_with_copy(self, tmp_path):
        organizer = _make_organizer(tmp_path)
        stats = organizer.organize(copy_mode=True, dry_run=False)

        assert stats["total"] > 0
        assert stats["copied"] > 0
        # 原文件应该还在
        assert (tmp_path / "outputs" / "characters" / "Bella" / "Bella_front_001.png").exists()

    def test_organize_creates_output_structure(self, tmp_path):
        organizer = _make_organizer(tmp_path)
        organizer.organize(dry_run=False)

        organized_dir = tmp_path / "organized"
        assert organized_dir.exists()


# ===================================================================
# 分析测试
# ===================================================================
class TestAnalyze:
    def test_analyze_directory(self, tmp_path):
        organizer = _make_organizer(tmp_path)
        analysis = organizer.analyze()

        assert "total_files" in analysis
        assert analysis["total_files"] > 0
        assert "by_type" in analysis
        assert "by_category" in analysis

    def test_analyze_finds_duplicates(self, tmp_path):
        outputs = _create_test_outputs(tmp_path)
        dup_file = outputs / "characters" / "Bella" / "Bella_front_copy.png"
        shutil.copy(
            outputs / "characters" / "Bella" / "Bella_front_001.png",
            dup_file
        )

        organizer = AssetOrganizer(input_dir=str(outputs))
        analysis = organizer.analyze()

        assert len(analysis["duplicates"]) >= 1


# ===================================================================
# 清理测试
# ===================================================================
class TestCleanup:
    def test_clean_empty_dirs(self, tmp_path):
        empty_dir = tmp_path / "outputs" / "empty_subdir"
        empty_dir.mkdir(parents=True, exist_ok=True)

        organizer = _make_organizer(tmp_path)
        organizer.clean_empty_dirs(directory=str(tmp_path / "outputs"), dry_run=False)

        # 验证空目录被删除了
        assert not empty_dir.exists()

    def test_clean_empty_dirs_dry_run(self, tmp_path):
        empty_dir = tmp_path / "outputs" / "empty_subdir"
        empty_dir.mkdir(parents=True, exist_ok=True)

        organizer = _make_organizer(tmp_path)
        organizer.clean_empty_dirs(directory=str(tmp_path / "outputs"), dry_run=True)

        assert empty_dir.exists()


# ===================================================================
# 输出结构创建测试
# ===================================================================
class TestOutputStructure:
    def test_create_output_structure(self, tmp_path):
        organizer = _make_organizer(tmp_path)
        output_dir = str(tmp_path / "organized")
        categories = {"character": [], "scene": [], "uncategorized": []}

        organizer._create_output_structure(output_dir, categories)

        assert os.path.exists(os.path.join(output_dir, "character", "front"))
        assert os.path.exists(os.path.join(output_dir, "character", "side"))
        assert os.path.exists(os.path.join(output_dir, "scene", "day"))
        assert os.path.exists(os.path.join(output_dir, "scene", "night"))


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
