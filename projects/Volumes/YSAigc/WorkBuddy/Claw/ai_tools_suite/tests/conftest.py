"""
测试基础设施 / conftest
提供共享的 fixtures 和 mock 对象
"""
import os
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# 测试用提示词库（最小化版本）
TEST_PROMPT_LIBRARY = {
    "characters": {
        "TestCharacter": {
            "positive": "portrait of TestCharacter, {{ view }}, {{ expression }}, high quality",
            "negative": "low quality, blurry",
            "seed": 12345,
            "default_params": {
                "view": "front view",
                "expression": "neutral"
            },
            "variants": ["front view", "side profile"],
            "view_map": {
                "front view": "full face, looking at camera",
                "side profile": "side view, profile angle"
            },
            "expression_map": {
                "neutral": "neutral expression, calm",
                "smiling": "warm smile, happy"
            }
        }
    },
    "scenes": {
        "TestScene": {
            "positive": "{{ scene_name }}, {{ time }}, cinematic lighting",
            "negative": "low quality",
            "default_params": {
                "scene_name": "TestScene",
                "time": "day"
            }
        }
    },
    "props": {
        "TestProp": {
            "positive": "{{ prop_name }}, photorealistic",
            "negative": ""
        }
    },
    "negative_prompts": {
        "general": {
            "label": "通用负面提示词",
            "prompt": "low quality, blurry, deformed, ugly, disfigured"
        },
        "character": {
            "label": "角色负面提示词",
            "prompt": "bad anatomy, extra limbs, missing fingers"
        },
        "scene": {
            "label": "场景负面提示词",
            "prompt": "oversaturated, unnatural lighting"
        },
        "video": {
            "label": "视频负面提示词",
            "prompt": "flickering, inconsistent motion, warping"
        }
    },
    "video_prompts": {
        "shot_types": {
            "wide_shot": {"prompt": "wide shot, establishing view"},
            "close_up": {"prompt": "close-up shot, focus on face"}
        },
        "camera_movements": {
            "dolly_in": {"prompt": "camera dolly in slowly"},
            "pan": {"prompt": "camera pan across scene"}
        },
        "action_descriptions": {
            "walking": {"prompt": "character walking naturally"},
            "dialogue": {"prompt": "characters in conversation"}
        },
        "styles": {
            "cinematic": {"prompt": "cinematic lighting, film grain, anamorphic"},
            "photorealistic": {"prompt": "photorealistic, 8k, raw photo"}
        },
        "motion_intensity": {
            "low": {"prompt": "slow, subtle movement"},
            "high": {"prompt": "fast, dynamic movement"}
        },
        "audio_prompts": {
            "ambient": {"prompt": "ambient sound, room tone"},
            "music": {"prompt": "background music, emotional score"}
        },
        "tool_presets": {
            "runway_gen3": {
                "prompt_prefix": "[Runway Gen-3]",
                "prompt_suffix": " --motion-score 7"
            }
        },
        "examples": {
            "example1": {
                "prompt": "wide shot, character walking, cinematic style"
            }
        }
    },
    "_meta": {
        "version": "2.0",
        "last_updated": "2026-05-30T00:00:00",
        "total_prompts": 3
    }
}


@pytest.fixture
def temp_prompt_library(tmp_path):
    """创建一个临时提示词库文件"""
    lib_file = tmp_path / "test_prompt_library.json"
    with open(lib_file, 'w', encoding='utf-8') as f:
        json.dump(TEST_PROMPT_LIBRARY, f, ensure_ascii=False, indent=2)
    return str(lib_file)


@pytest.fixture
def prompt_manager(temp_prompt_library):
    """返回一个指向临时提示词库的 PromptManager 实例"""
    from modules.prompt_manager import PromptManager
    return PromptManager(library_path=str(temp_prompt_library))


@pytest.fixture
def mock_runninghub_api():
    """Mock RunningHubAPI 客户端"""
    mock = MagicMock()
    mock.text_to_image.return_value = ["/fake/path/generated_001.png"]
    mock.image_to_image.return_value = ["/fake/path/img2img_001.png"]
    mock.inpainting.return_value = ["/fake/path/inpaint_001.png"]
    mock.upscale.return_value = "/fake/path/upscaled_001.png"
    return mock


@pytest.fixture
def mock_requests_post():
    """Mock requests.post 方法"""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "images": [{"url": "https://example.com/fake_image.png"}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def sample_image_file(tmp_path):
    """创建一个假的图片文件用于测试"""
    img_file = tmp_path / "test_image.png"
    img_file.write_bytes(b"fake_png_data")
    return str(img_file)
