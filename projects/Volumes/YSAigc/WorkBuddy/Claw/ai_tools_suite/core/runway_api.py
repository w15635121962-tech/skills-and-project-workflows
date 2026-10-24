"""
Runway Gen-3 API 封装模块
用于AI视频生成
"""

import os
import json
import time
import requests
from typing import List, Dict, Optional, Union
from pathlib import Path
from tqdm import tqdm


class RunwayAPI:
    """Runway Gen-3 API 客户端"""
    
    def __init__(self, api_key: str = None, config_path: str = None):
        """
        初始化API客户端
        
        Args:
            api_key: Runway API密钥
            config_path: 配置文件路径
        """
        self.api_key = api_key or self._load_api_key_from_config(config_path)
        if not self.api_key:
            raise ValueError(
                "未找到Runway API密钥！\n"
                "请在 config/.env 中设置 RUNWAY_API_KEY，\n"
                "或在初始化时传入 api_key 参数。"
            )
        
        self.base_url = "https://api.runwayml.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 加载默认配置
        self.config = self._load_config(config_path)
    
    def _load_api_key_from_config(self, config_path: Optional[str]) -> Optional[str]:
        """从配置文件读取API密钥"""
        api_key = os.getenv("RUNWAY_API_KEY")
        if api_key:
            return api_key
        
        # 尝试从.env文件读取
        env_file = os.path.join(os.path.dirname(__file__), '../config/.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('RUNWAY_API_KEY='):
                        return line.strip().split('=', 1)[1].strip('"\'')
        
        return None
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        # Runway没有独立的配置文件，使用默认配置
        return {
            "model": "gen3-alpha",
            "duration": 5,  # 秒
            "resolution": "1280x768",
            "output_format": "mp4",
            "output_dir": "../outputs/videos/",
            "watermark": False,
            "expand_prompt": True
        }
    
    def _make_request(self, endpoint: str, method: str = "POST", 
                      data: Dict = None, max_retries: int = 3) -> Dict:
        """
        发送API请求（带重试机制）
        
        Args:
            endpoint: API端点
            method: HTTP方法
            data: 请求数据
            max_retries: 最大重试次数
        
        Returns:
            API响应的JSON数据
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                if method.upper() == "POST":
                    response = self.session.post(url, json=data, timeout=120)
                else:
                    response = self.session.get(url, params=data, timeout=120)
                
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⚠️ 请求失败（{type(e).__name__}），{wait_time}秒后重试... ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"API请求失败（已重试{max_retries}次）：{str(e)}")
    
    def text_to_video(self, prompt: str, negative_prompt: str = "",
                     duration: int = None, resolution: str = None,
                     image_url: str = None, output_dir: str = None) -> str:
        """
        文本生成视频（或图片+文本生成视频）
        
        Args:
            prompt: 视频提示词
            negative_prompt: 负面提示词（可选）
            duration: 视频时长（秒，默认5秒）
            resolution: 分辨率（默认1280x768）
            image_url: 参考图片URL（可选，用于图生视频）
            output_dir: 输出目录
        
        Returns:
            生成的视频文件路径
        """
        duration = duration or self.config.get('duration', 5)
        resolution = resolution or self.config.get('resolution', '1280x768')
        output_dir = output_dir or self.config.get('output_dir', '../outputs/videos/')
        
        # 构建请求数据
        data = {
            "model": self.config.get('model', 'gen3-alpha'),
            "prompt": prompt,
            "duration": duration,
            "resolution": resolution,
            "watermark": self.config.get('watermark', False),
            "expand_prompt": self.config.get('expand_prompt', True)
        }
        
        if negative_prompt:
            data['negative_prompt'] = negative_prompt
        
        if image_url:
            data['image_url'] = image_url
        
        print(f"🎬 正在生成视频...")
        print(f"   提示词：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"   时长：{duration}秒")
        print(f"   分辨率：{resolution}")
        if image_url:
            print(f"   参考图片：{image_url}")
        
        # 提交任务
        result = self._make_request('/videos', data=data)
        
        # 获取任务ID
        task_id = result.get('id')
        if not task_id:
            raise Exception(f"API响应格式错误：{result}")
        
        print(f"   任务ID：{task_id}")
        print(f"⏳ 等待视频生成完成（通常需要3-5分钟）...")
        
        # 轮询任务状态
        video_url = self._poll_task_status(task_id)
        
        # 下载视频
        output_path = self._download_video(video_url, output_dir)
        
        print(f"✅ 视频生成完成！")
        print(f"   📽️ {output_path}")
        
        return output_path
    
    def image_to_video(self, image_path: str, prompt: str = "",
                       duration: int = None, output_dir: str = None) -> str:
        """
        图片生成视频（动画化）
        
        Args:
            image_path: 输入图片路径
            prompt: 视频提示词（描述动作）
            duration: 视频时长（秒）
            output_dir: 输出目录
        
        Returns:
            生成的视频文件路径
        """
        duration = duration or self.config.get('duration', 5)
        output_dir = output_dir or self.config.get('output_dir', '../outputs/videos/')
        
        # 上传图片并获取URL
        print(f"📤 正在上传参考图片...")
        image_url = self._upload_image(image_path)
        print(f"   图片URL：{image_url}")
        
        # 生成视频
        return self.text_to_video(
            prompt=prompt,
            duration=duration,
            image_url=image_url,
            output_dir=output_dir
        )
    
    def extend_video(self, video_path: str, prompt: str,
                     duration: int = None, output_dir: str = None) -> str:
        """
        延长视频（在末尾添加内容）
        
        Args:
            video_path: 输入视频路径
            prompt: 延长部分的提示词
            duration: 延长的时长（秒）
            output_dir: 输出目录
        
        Returns:
            延长后的视频文件路径
        """
        duration = duration or self.config.get('duration', 5)
        output_dir = output_dir or self.config.get('output_dir', '../outputs/videos/')
        
        # 上传视频并获取URL
        print(f"📤 正在上传视频...")
        video_url = self._upload_video(video_path)
        print(f"   视频URL：{video_url}")
        
        # 构建请求数据
        data = {
            "model": self.config.get('model', 'gen3-alpha'),
            "video_url": video_url,
            "prompt": prompt,
            "duration": duration
        }
        
        print(f"🎬 正在延长视频...")
        print(f"   提示词：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"   延长：{duration}秒")
        
        # 提交任务
        result = self._make_request('/videos/extend', data=data)
        
        # 获取任务ID
        task_id = result.get('id')
        if not task_id:
            raise Exception(f"API响应格式错误：{result}")
        
        print(f"   任务ID：{task_id}")
        print(f"⏳ 等待视频生成完成...")
        
        # 轮询任务状态
        new_video_url = self._poll_task_status(task_id)
        
        # 下载视频
        output_path = self._download_video(new_video_url, output_dir)
        
        print(f"✅ 视频延长完成！")
        print(f"   📽️ {output_path}")
        
        return output_path
    
    def _poll_task_status(self, task_id: str, max_wait: int = 600) -> str:
        """
        轮询任务状态
        
        Args:
            task_id: 任务ID
            max_wait: 最大等待时间（秒）
        
        Returns:
            完成的视频URL
        """
        start_time = time.time()
        progress_bar = tqdm(total=100, desc="视频生成进度", unit="%")
        
        while time.time() - start_time < max_wait:
            response = self.session.get(f"{self.base_url}/videos/{task_id}", timeout=30)
            response.raise_for_status()
            result = response.json()
            
            status = result.get('status')
            progress = result.get('progress', 0)
            
            # 更新进度条
            progress_bar.update(progress - progress_bar.n)
            
            if status == 'completed':
                progress_bar.close()
                video_url = result.get('video_url')
                if not video_url:
                    raise Exception(f"任务完成但未返回视频URL：{result}")
                return video_url
            
            elif status == 'failed':
                progress_bar.close()
                error = result.get('error', '未知错误')
                raise Exception(f"视频生成失败：{error}")
            
            # 继续等待
            time.sleep(10)
        
        progress_bar.close()
        raise Exception(f"任务超时（已等待{max_wait}秒）")
    
    def _upload_image(self, image_path: str) -> str:
        """
        上传图片到Runway服务器
        
        Args:
            image_path: 图片路径
        
        Returns:
            图片URL
        """
        # 获取上传URL
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(f"{self.base_url}/upload", files=files, timeout=60)
            response.raise_for_status()
            result = response.json()
        
        upload_url = result.get('upload_url')
        if not upload_url:
            raise Exception(f"获取上传URL失败：{result}")
        
        # 上传文件
        with open(image_path, 'rb') as f:
            upload_response = requests.put(upload_url, data=f, timeout=120)
            upload_response.raise_for_status()
        
        # 返回文件URL
        file_url = result.get('file_url')
        if not file_url:
            raise Exception(f"上传成功但未返回文件URL：{result}")
        
        return file_url
    
    def _upload_video(self, video_path: str) -> str:
        """
        上传视频到Runway服务器
        
        Args:
            video_path: 视频路径
        
        Returns:
            视频URL
        """
        # 与_upload_image类似，复用逻辑
        return self._upload_image(video_path)
    
    def _download_video(self, video_url: str, output_dir: str) -> str:
        """
        下载视频到本地
        
        Args:
            video_url: 视频URL
            output_dir: 输出目录
        
        Returns:
            本地文件路径
        """
        # 创建输出目录
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = int(time.time())
        filename = f"runway_video_{timestamp}.mp4"
        output_path = os.path.join(output_dir, filename)
        
        # 下载视频
        print(f"📥 正在下载视频...")
        response = requests.get(video_url, timeout=300, stream=True)
        response.raise_for_status()
        
        # 保存文件
        total_size = int(response.headers.get('content-length', 0))
        with open(output_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                for chunk in tqdm(response.iter_content(chunk_size=8192), 
                                total=total_size//8192, 
                                desc="下载视频", 
                                unit='chunk'):
                    f.write(chunk)
        
        return output_path
    
    def __del__(self):
        """析构函数，关闭session"""
        if hasattr(self, 'session'):
            self.session.close()


# 命令行测试
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Runway Gen-3 API 测试')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 文本生成视频
    text2vid = subparsers.add_parser('text2vid', help='文本生成视频')
    text2vid.add_argument('--prompt', type=str, required=True, help='视频提示词')
    text2vid.add_argument('--negative', type=str, default='', help='负面提示词')
    text2vid.add_argument('--duration', type=int, default=5, help='视频时长（秒）')
    text2vid.add_argument('--resolution', type=str, default='1280x768', help='分辨率')
    text2vid.add_argument('--image', type=str, help='参考图片URL（可选）')
    text2vid.add_argument('--output', type=str, default='../outputs/videos/', help='输出目录')
    
    # 图片生成视频
    img2vid = subparsers.add_parser('img2vid', help='图片生成视频（动画化）')
    img2vid.add_argument('--image', type=str, required=True, help='输入图片路径')
    img2vid.add_argument('--prompt', type=str, default='', help='视频提示词')
    img2vid.add_argument('--duration', type=int, default=5, help='视频时长（秒）')
    img2vid.add_argument('--output', type=str, default='../outputs/videos/', help='输出目录')
    
    # 延长视频
    extend = subparsers.add_parser('extend', help='延长视频')
    extend.add_argument('--video', type=str, required=True, help='输入视频路径')
    extend.add_argument('--prompt', type=str, required=True, help='延长部分的提示词')
    extend.add_argument('--duration', type=int, default=5, help='延长时长（秒）')
    extend.add_argument('--output', type=str, default='../outputs/videos/', help='输出目录')
    
    args = parser.parse_args()
    
    try:
        api = RunwayAPI()
        
        if args.command == 'text2vid':
            api.text_to_video(
                prompt=args.prompt,
                negative_prompt=args.negative,
                duration=args.duration,
                resolution=args.resolution,
                image_url=args.image,
                output_dir=args.output
            )
        
        elif args.command == 'img2vid':
            api.image_to_video(
                image_path=args.image,
                prompt=args.prompt,
                duration=args.duration,
                output_dir=args.output
            )
        
        elif args.command == 'extend':
            api.extend_video(
                video_path=args.video,
                prompt=args.prompt,
                duration=args.duration,
                output_dir=args.output
            )
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
