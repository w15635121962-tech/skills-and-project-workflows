"""
测试 RunningHub API 模块
使用 mock 避免真实 API 调用
"""
import os
import json
import pytest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path


# —— 辅助函数 ——
def _make_pm_with_lib(tmp_path, lib_data=None):
    """创建带测试数据的 PromptManager"""
    from modules.prompt_manager import PromptManager
    if lib_data is None:
        lib_data = {"characters": {}, "scenes": {}, "props": {}, "_meta": {}}
    lib_file = tmp_path / "prompt_library.json"
    with open(lib_file, 'w', encoding='utf-8') as f:
        json.dump(lib_data, f, ensure_ascii=False, indent=2)
    return PromptManager(library_path=str(lib_file))


def _make_config(tmp_path, config_data=None):
    """创建测试用配置文件"""
    if config_data is None:
        config_data = {
            "model": "SDXL",
            "sampler": "DPM++ 2M Karras",
            "steps": 30,
            "cfg_scale": 7.5,
            "resolution": "1024x1024",
            "batch_size": 4,
            "output_format": "PNG",
            "default_negative_prompt": "low quality",
            "output_dir": str(tmp_path / "outputs"),
            "wait_between_tasks": 2
        }
    config_file = tmp_path / "runninghub_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    return str(config_file)


def _mock_api_response(images_count=1):
    """创建模拟的 API 响应"""
    return {
        "images": [{"url": f"https://example.com/img_{i}.png"} for i in range(images_count)]
    }


# ===================================================================
# 初始化测试
# ===================================================================
class TestRunningHubInit:
    def test_init_with_api_key(self):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key_123")
        assert api.api_key == "test_key_123"
        assert "Bearer test_key_123" in api.headers["Authorization"]

    def test_init_without_api_key_raises(self):
        from core.runninghub_api import RunningHubAPI
        # 确保环境变量也没设置
        with patch.dict(os.environ, {}, clear=True):
            # 删除可能存在的配置文件
            with pytest.raises(ValueError, match="未找到"):
                RunningHubAPI(config_path="/nonexistent/path.json")

    def test_init_loads_config(self, tmp_path):
        from core.runninghub_api import RunningHubAPI
        config_path = _make_config(tmp_path)
        api = RunningHubAPI(api_key="test_key", config_path=config_path)
        assert api.config["model"] == "SDXL"
        assert api.config["steps"] == 30

    def test_init_creates_session(self):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key")
        assert api.session is not None
        api.session.close()


# ===================================================================
# _make_request 测试（通过 mock 测试重试逻辑）
# ===================================================================
class TestMakeRequest:
    def test_successful_request(self, tmp_path):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        with patch.object(api.session, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            result = api._make_request('/test', data={"prompt": "test"})

            assert result == {"ok": True}
            mock_post.assert_called_once()

    def test_retry_on_failure(self, tmp_path):
        from core.runninghub_api import RunningHubAPI
        import requests
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        with patch.object(api.session, 'post') as mock_post:
            # 前两次失败，第三次成功
            mock_response_ok = Mock()
            mock_response_ok.status_code = 200
            mock_response_ok.json.return_value = {"ok": True}
            mock_response_ok.raise_for_status = Mock()

            mock_post.side_effect = [
                requests.exceptions.ConnectionError("network error"),
                requests.exceptions.Timeout("timeout"),
                mock_response_ok
            ]

            with patch('time.sleep'):  # 跳过等待
                result = api._make_request('/test', data={"prompt": "test"}, max_retries=3)

            assert result == {"ok": True}
            assert mock_post.call_count == 3

    def test_max_retries_exhausted(self, tmp_path):
        from core.runninghub_api import RunningHubAPI
        import requests
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        with patch.object(api.session, 'post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("persistent error")

            with patch('time.sleep'):  # 跳过等待
                with pytest.raises(Exception, match="API请求失败"):
                    api._make_request('/test', data={"prompt": "test"}, max_retries=2)

            assert mock_post.call_count == 2


# ===================================================================
# text_to_image 测试
# ===================================================================
class TestTextToImage:
    def test_text_to_image_success(self, tmp_path):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        # Mock _make_request
        with patch.object(api, '_make_request') as mock_request:
            mock_request.return_value = _mock_api_response(1)

            # Mock _download_images
            with patch.object(api, '_download_images') as mock_download:
                mock_download.return_value = ["/fake/output/img_001.png"]

                result = api.text_to_image(prompt="a beautiful woman")

                assert len(result) == 1
                assert result[0] == "/fake/output/img_001.png"
                mock_request.assert_called_once()

    def test_text_to_image_with_all_params(self, tmp_path):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        with patch.object(api, '_make_request') as mock_request:
            mock_request.return_value = _mock_api_response(2)

            with patch.object(api, '_download_images') as mock_download:
                mock_download.return_value = ["/fake/1.png", "/fake/2.png"]

                result = api.text_to_image(
                    prompt="test prompt",
                    negative_prompt="low quality",
                    width=768,
                    height=768,
                    steps=50,
                    cfg_scale=12.0,
                    seed=42,
                    batch_size=2
                )

                assert len(result) == 2
                # 检查传给 _make_request 的数据
                call_args = mock_request.call_args
                data = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('data', {})
                assert data["width"] == 768
                assert data["seed"] == 42

    def test_text_to_image_uses_config_defaults(self, tmp_path):
        from core.runninghub_api import RunningHubAPI
        config_path = _make_config(tmp_path)
        api = RunningHubAPI(api_key="test_key", config_path=config_path)

        with patch.object(api, '_make_request') as mock_request:
            mock_request.return_value = _mock_api_response(1)

            with patch.object(api, '_download_images') as mock_download:
                mock_download.return_value = ["/fake/img.png"]

                api.text_to_image(prompt="test")

                call_args = mock_request.call_args
                data = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('data', {})
                assert data["steps"] == 30  # 来自 config
                assert data["cfg_scale"] == 7.5


# ===================================================================
# image_to_image 测试
# ===================================================================
class TestImageToImage:
    def test_image_to_image_success(self, tmp_path, sample_image_file):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        with patch.object(api, '_make_request') as mock_request:
            mock_request.return_value = _mock_api_response(1)

            with patch.object(api, '_download_images') as mock_download:
                mock_download.return_value = ["/fake/img2img.png"]

                result = api.image_to_image(
                    input_image=sample_image_file,
                    prompt="convert to oil painting"
                )

                assert len(result) == 1
                mock_request.assert_called_once()

    def test_image_to_image_reads_file(self, tmp_path, sample_image_file):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        with patch.object(api, '_make_request') as mock_request:
            mock_request.return_value = _mock_api_response(1)

            with patch.object(api, '_download_images') as mock_download:
                mock_download.return_value = ["/fake/img.png"]

                api.image_to_image(
                    input_image=sample_image_file,
                    prompt="test",
                    strength=0.8
                )

                # 验证请求中包含 image 字段（base64）
                call_args = mock_request.call_args
                data = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('data', {})
                assert "image" in data
                assert data["strength"] == 0.8


# ===================================================================
# upscale 测试
# ===================================================================
class TestUpscale:
    def test_upscale_success(self, tmp_path, sample_image_file):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        with patch.object(api, '_make_request') as mock_request:
            mock_request.return_value = {"image": {"url": "https://example.com/upscaled.png"}}

            with patch.object(api, '_download_image') as mock_download:
                mock_download.return_value = "/fake/upscaled.png"

                result = api.upscale(input_image=sample_image_file, scale=2)

                assert result == "/fake/upscaled.png"
                mock_request.assert_called_once()

    def test_upscale_scale_4(self, tmp_path, sample_image_file):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        with patch.object(api, '_make_request') as mock_request:
            mock_request.return_value = {"image": {"url": "https://example.com/upscaled.png"}}

            with patch.object(api, '_download_image') as mock_download:
                mock_download.return_value = "/fake/upscaled.png"

                api.upscale(input_image=sample_image_file, scale=4)

                call_args = mock_request.call_args
                data = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('data', {})
                assert data["scale"] == 4


# ===================================================================
# 批量生成测试
# ===================================================================
class TestBatchGenerate:
    def test_batch_generate_multiple_prompts(self, tmp_path):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        with patch.object(api, 'text_to_image') as mock_t2i:
            mock_t2i.return_value = ["/fake/img.png"]

            prompts = ["prompt 1", "prompt 2", "prompt 3"]
            results = api.batch_generate(prompts=prompts, output_dir=str(tmp_path))

            assert len(results) == 3
            assert all(len(r) == 1 for r in results)
            assert mock_t2i.call_count == 3

    def test_batch_generate_handles_errors(self, tmp_path):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        with patch.object(api, 'text_to_image') as mock_t2i:
            # 第二个 prompt 失败
            mock_t2i.side_effect = [
                ["/fake/img1.png"],
                Exception("API error"),
                ["/fake/img3.png"]
            ]

            prompts = ["p1", "p2", "p3"]
            results = api.batch_generate(prompts=prompts, output_dir=str(tmp_path))

            assert len(results) == 3
            assert len(results[0]) == 1
            assert len(results[1]) == 0  # 失败返回空列表
            assert len(results[2]) == 1


# ===================================================================
# 下载功能测试
# ===================================================================
class TestDownload:
    def test_download_image(self, tmp_path):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        # Mock requests.get
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b"fake_image_data"
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            output_dir = str(tmp_path / "downloads")
            os.makedirs(output_dir, exist_ok=True)  # 确保目录存在
            url = "https://example.com/test.png"

            result = api._download_image(url, output_dir, suffix="_test")

            assert result.startswith(output_dir)
            assert os.path.exists(result)
            with open(result, 'rb') as f:
                assert f.read() == b"fake_image_data"

    def test_download_images_multiple(self, tmp_path):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key", config_path=_make_config(tmp_path))

        with patch.object(api, '_download_image') as mock_download:
            mock_download.side_effect = [
                "/fake/img_001.png",
                "/fake/img_002.png"
            ]

            urls = ["url1", "url2"]
            output_dir = str(tmp_path)

            results = api._download_images(urls, output_dir)

            assert len(results) == 2
            assert mock_download.call_count == 2


# ===================================================================
# 析构函数测试
# ===================================================================
class TestCleanup:
    def test_session_closed_on_del(self):
        from core.runninghub_api import RunningHubAPI
        api = RunningHubAPI(api_key="test_key")
        mock_session = MagicMock()
        api.session = mock_session

        api.__del__()

        mock_session.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
