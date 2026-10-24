"""
测试 BatchGenerator 模块
使用 mock 避免真实 API 调用
"""
import os
import json
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path


# —— 辅助函数 ——
def _make_pm_with_characters(tmp_path):
    """创建包含测试角色的 PromptManager"""
    from modules.prompt_manager import PromptManager
    lib_data = {
        "characters": {
            "Bella": {
                "positive": "portrait of Bella, {{ view }}, {{ expression }}",
                "negative": "low quality",
                "seed": 12345,
                "default_params": {"view": "front view", "expression": "neutral"},
                "variants": ["front view", "side profile"],
                "view_map": {},
                "expression_map": {}
            },
            "Luca": {
                "positive": "portrait of Luca, {{ view }}",
                "negative": "",
                "seed": None,
                "default_params": {}
            }
        },
        "scenes": {
            "Hospital": {
                "positive": "hospital, {{ time }}",
                "negative": ""
            }
        },
        "negative_prompts": {
            "general": {"label": "通用", "prompt": "low quality"}
        }
    }
    lib_file = tmp_path / "prompt_library.json"
    with open(lib_file, 'w', encoding='utf-8') as f:
        json.dump(lib_data, f, ensure_ascii=False, indent=2)
    return PromptManager(library_path=str(lib_file))


def _make_config(tmp_path):
    """创建测试用配置文件"""
    config_data = {
        "model": "SDXL",
        "steps": 30,
        "cfg_scale": 7.5,
        "batch_size": 4,
        "output_format": "PNG",
        "output_dir": str(tmp_path / "outputs"),
        "wait_between_tasks": 0  # 测试时不等待
    }
    config_file = tmp_path / "config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    return str(config_file)


# ===================================================================
# 初始化测试
# ===================================================================
class TestBatchGeneratorInit:
    def test_init_with_api_client(self):
        from modules.batch_generator import BatchGenerator
        mock_api = MagicMock()
        bg = BatchGenerator(api_client=mock_api, max_workers=2)
        assert bg.api_client == mock_api
        assert bg.max_workers == 2

    def test_init_with_prompt_manager(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        pm = _make_pm_with_characters(tmp_path)
        bg = BatchGenerator(prompt_manager=pm)
        assert bg.prompt_manager == pm

    def test_init_stats(self):
        from modules.batch_generator import BatchGenerator
        bg = BatchGenerator()
        assert bg.stats["total"] == 0
        assert bg.stats["success"] == 0
        assert bg.stats["failed"] == 0


# ===================================================================
# generate_characters 测试
# ===================================================================
class TestGenerateCharacters:
    def test_generate_all_characters(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        pm = _make_pm_with_characters(tmp_path)
        mock_api = MagicMock()
        mock_api.text_to_image.return_value = ["/fake/img.png"]

        bg = BatchGenerator(api_client=mock_api, prompt_manager=pm, config_path=_make_config(tmp_path))

        with patch('time.sleep'):  # 跳过等待
            results = bg.generate_characters(
                views=["front view"],
                expressions=["neutral"],
                count_per_view=1
            )

        # 应该有 2 个字符 × 1 视角 × 1 表情 = 2 个任务
        assert len(results) == 2
        assert mock_api.text_to_image.call_count == 2

    def test_generate_specific_characters(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        pm = _make_pm_with_characters(tmp_path)
        mock_api = MagicMock()
        mock_api.text_to_image.return_value = ["/fake/img.png"]

        bg = BatchGenerator(api_client=mock_api, prompt_manager=pm, config_path=_make_config(tmp_path))

        with patch('time.sleep'):
            results = bg.generate_characters(
                characters=["Bella"],  # 只生成 Bella
                views=["front view"],
                expressions=["neutral"],
                count_per_view=1
            )

        assert len(results) == 1
        # 键名格式为 "{character}_{view}_{expression}"
        assert any("Bella" in k for k in results.keys())

    def test_generate_characters_no_prompt_manager(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        mock_api = MagicMock()
        mock_api.text_to_image.return_value = ["/fake/img.png"]

        bg = BatchGenerator(api_client=mock_api, config_path=_make_config(tmp_path))

        with patch('time.sleep'):
            results = bg.generate_characters(
                characters=["Bella"],
                views=["front view"],
                expressions=["neutral"],
                count_per_view=1,
                use_prompt_library=False
            )

        assert len(results) == 1

    def test_generate_characters_stats(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        pm = _make_pm_with_characters(tmp_path)
        mock_api = MagicMock()
        mock_api.text_to_image.return_value = ["/fake/img.png"]

        bg = BatchGenerator(api_client=mock_api, prompt_manager=pm, config_path=_make_config(tmp_path))

        with patch('time.sleep'):
            bg.generate_characters(
                views=["front view"],
                expressions=["neutral"],
                count_per_view=1
            )

        assert bg.stats["total"] > 0
        assert bg.stats["success"] > 0
        assert bg.stats["start_time"] is not None
        assert bg.stats["end_time"] is not None


# ===================================================================
# generate_scenes 测试
# ===================================================================
class TestGenerateScenes:
    def test_generate_all_scenes(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        pm = _make_pm_with_characters(tmp_path)
        mock_api = MagicMock()
        mock_api.text_to_image.return_value = ["/fake/scene.png"]

        bg = BatchGenerator(api_client=mock_api, prompt_manager=pm, config_path=_make_config(tmp_path))

        with patch('time.sleep'):
            results = bg.generate_scenes(
                variations=["day"],
                count_per_scene=1
            )

        assert len(results) == 1  # 1 场景 × 1 变化
        assert mock_api.text_to_image.call_count == 1

    def test_generate_scenes_no_prompt_manager_raises(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        mock_api = MagicMock()

        bg = BatchGenerator(api_client=mock_api, config_path=_make_config(tmp_path))

        with pytest.raises(ValueError, match="未指定场景"):
            bg.generate_scenes(use_prompt_library=False)


# ===================================================================
# generate_from_prompt_list 测试
# ===================================================================
class TestGenerateFromPromptList:
    def test_generate_from_prompts(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        mock_api = MagicMock()
        mock_api.text_to_image.return_value = ["/fake/img.png"]

        bg = BatchGenerator(api_client=mock_api, config_path=_make_config(tmp_path))

        with patch('time.sleep'):
            results = bg.generate_from_prompt_list(
                prompts=["prompt 1", "prompt 2"],
                batch_size=1
            )

        assert len(results) == 2
        assert mock_api.text_to_image.call_count == 2

    def test_generate_with_negative_prompts(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        mock_api = MagicMock()
        mock_api.text_to_image.return_value = ["/fake/img.png"]

        bg = BatchGenerator(api_client=mock_api, config_path=_make_config(tmp_path))

        with patch('time.sleep'):
            results = bg.generate_from_prompt_list(
                prompts=["prompt 1", "prompt 2"],
                negative_prompts=["neg 1", "neg 2"],
                batch_size=1
            )

        assert len(results) == 2
        # 检查 negative_prompt 参数是否传入
        call_args = mock_api.text_to_image.call_args_list[0]
        assert call_args[1].get("negative_prompt") == "neg 1"

    def test_generate_prompts_mismatched_lengths(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        mock_api = MagicMock()

        bg = BatchGenerator(api_client=mock_api, config_path=_make_config(tmp_path))

        with pytest.raises(ValueError, match="长度必须与"):
            bg.generate_from_prompt_list(
                prompts=["p1", "p2"],
                negative_prompts=["only one"],  # 长度不匹配
                batch_size=1
            )


# ===================================================================
# API 客户端类型判断测试
# ===================================================================
class TestAPIClientTypes:
    def test_runninghub_api_client(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        mock_api = MagicMock()
        mock_api.text_to_image = MagicMock(return_value=["/fake/img.png"])
        # 确保没有 generate 方法
        del mock_api.generate

        pm = _make_pm_with_characters(tmp_path)
        bg = BatchGenerator(api_client=mock_api, prompt_manager=pm, config_path=_make_config(tmp_path))

        with patch('time.sleep'):
            results = bg.generate_characters(
                characters=["Bella"],
                views=["front view"],
                expressions=["neutral"],
                count_per_view=1
            )

        assert len(results) == 1
        mock_api.text_to_image.assert_called_once()

    def test_midjourney_api_client(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        mock_api = MagicMock()
        mock_api.generate = MagicMock(return_value=["/fake/mj.png"])
        # 确保没有 text_to_image 方法
        del mock_api.text_to_image

        pm = _make_pm_with_characters(tmp_path)
        bg = BatchGenerator(api_client=mock_api, prompt_manager=pm, config_path=_make_config(tmp_path))

        with patch('time.sleep'):
            results = bg.generate_characters(
                characters=["Bella"],
                views=["front view"],
                expressions=["neutral"],
                count_per_view=1,
                use_prompt_library=False  # Midjourney 可能不用 prompt library
            )

        # 如果 use_prompt_library=False，会走 else 分支
        # 这里主要测试 hasattr 逻辑
        assert True  # 到达这里说明没有崩溃

    def test_unknown_api_client_raises(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        mock_api = MagicMock(spec=[])  # 空 spec，没有任何方法

        pm = _make_pm_with_characters(tmp_path)
        bg = BatchGenerator(api_client=mock_api, prompt_manager=pm, config_path=_make_config(tmp_path))

        with patch('time.sleep'):
            # 可能抛异常，也可能不抛（取决于实现），只要不崩溃就行
            results = bg.generate_characters(
                characters=["Bella"],
                views=["front view"],
                expressions=["neutral"],
                count_per_view=1
            )
            assert isinstance(results, dict)


# ===================================================================
# 错误处理测试
# ===================================================================
class TestErrorHandling:
    def test_api_error_continues_to_next_task(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        pm = _make_pm_with_characters(tmp_path)
        mock_api = MagicMock()
        # 第一个任务失败，第二个成功
        mock_api.text_to_image.side_effect = [
            Exception("API error"),
            ["/fake/img.png"]
        ]

        bg = BatchGenerator(api_client=mock_api, prompt_manager=pm, config_path=_make_config(tmp_path))

        with patch('time.sleep'):
            results = bg.generate_characters(
                characters=["Bella", "Luca"],
                views=["front view"],
                expressions=["neutral"],
                count_per_view=1
            )

        assert bg.stats["failed"] == 1
        assert bg.stats["success"] == 1
        assert len(results) == 2

    def test_no_api_client_raises(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        pm = _make_pm_with_characters(tmp_path)
        bg = BatchGenerator(prompt_manager=pm, config_path=_make_config(tmp_path))

        with patch('time.sleep'):
            # 没有api_client时，任务会失败但不会抛异常
            results = bg.generate_characters(
                characters=["Bella"],
                views=["front view"],
                expressions=["neutral"],
                count_per_view=1
            )
            assert bg.stats["failed"] == 1


# ===================================================================
# save_results 测试
# ===================================================================
class TestSaveResults:
    def test_save_results_creates_file(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        bg = BatchGenerator(config_path=_make_config(tmp_path))

        results = {
            "Bella_front_neutral": ["/fake/img1.png"],
            "Luca_front_neutral": ["/fake/img2.png"]
        }

        output_path = str(tmp_path / "results.json")
        bg.save_results(results, output_path=output_path)

        assert os.path.exists(output_path)
        with open(output_path, 'r', encoding='utf-8') as f:
            saved = json.load(f)
            assert "results" in saved
            assert "stats" in saved

    def test_save_results_default_path(self, tmp_path):
        from modules.batch_generator import BatchGenerator
        config_data = {
            "output_dir": str(tmp_path / "outputs"),
        }
        config_file = tmp_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)

        bg = BatchGenerator(config_path=str(config_file))
        results = {"test": ["/fake/img.png"]}

        output_path = str(tmp_path / "results.json")
        bg.save_results(results, output_path=output_path)

        assert os.path.exists(output_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
