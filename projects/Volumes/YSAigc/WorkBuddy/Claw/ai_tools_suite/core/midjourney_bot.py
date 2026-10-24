"""
Midjourney Discord Bot 自动化模块
通过Discord Bot API调用Midjourney生成图片
"""

import os
import json
import time
import asyncio
import logging
from typing import List, Dict, Optional, Callable
from pathlib import Path
import discord
from discord.ext import commands
from tqdm import tqdm


class MidjourneyBot:
    """Midjourney Discord Bot 客户端"""
    
    def __init__(self, bot_token: str = None, channel_id: str = None, 
                 config_path: str = None):
        """
        初始化Bot客户端
        
        Args:
            bot_token: Discord Bot Token
            channel_id: Midjourney频道ID
            config_path: 配置文件路径
        """
        self.bot_token = bot_token or self._load_token_from_config(config_path)
        self.channel_id = channel_id or self._load_channel_from_config(config_path)
        
        if not self.bot_token:
            raise ValueError(
                "未找到Discord Bot Token！\n"
                "请在 config/.env 中设置 DISCORD_BOT_TOKEN，\n"
                "或在初始化时传入 bot_token 参数。"
            )
        
        if not self.channel_id:
            raise ValueError(
                "未找到Midjourney频道ID！\n"
                "请在 config/.env 中设置 MIDJOURNEY_CHANNEL_ID，\n"
                "或在初始化时传入 channel_id 参数。"
            )
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化Discord Bot
        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        # 消息监听
        self.generated_images = []
        self.current_task_id = None
        
        @self.bot.event
        async def on_ready():
            print(f"✅ Discord Bot 已登录：{self.bot.user}")
        
        @self.bot.event
        async def on_message(message):
            # 只处理Midjourney的消息
            if message.author.id == self.config.get('midjourney_bot_id', 936929561302675456):
                # 检测是否是我们触发的任务
                if self.current_task_id and self.current_task_id in message.content:
                    # 提取图片URL
                    if message.attachments:
                        for attachment in message.attachments:
                            if attachment.url.endswith(('.png', '.jpg', '.jpeg', '.webp')):
                                self.generated_images.append(attachment.url)
                                print(f"📥 收到生成图片：{attachment.url}")
                    
                    # 检测完成（Midjourney会发送完成消息）
                    if "✅" in message.content or "done" in message.content.lower():
                        print(f"✅ 任务完成！共生成{len(self.generated_images)}张图片")
            
            await self.bot.process_commands(message)
    
    def _load_token_from_config(self, config_path: Optional[str]) -> Optional[str]:
        """从配置文件读取Bot Token"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('discord_bot_token')
        
        # 尝试从环境变量读取
        return os.getenv("DISCORD_BOT_TOKEN")
    
    def _load_channel_from_config(self, config_path: Optional[str]) -> Optional[str]:
        """从配置文件读取频道ID"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('midjourney_channel_id')
        
        # 尝试从环境变量读取
        return os.getenv("MIDJOURNEY_CHANNEL_ID")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), '../config/midjourney_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 返回默认配置
        return {
            "model": "v6",
            "aspect_ratio": "2:3",
            "style": "raw",
            "quality": "hd",
            "output_format": "PNG",
            "default_negative_prompt": "cartoon, anime, low quality, blurry, deformed",
            "output_dir": "../outputs/scenes/",
            "midjourney_bot_id": 936929561302675456  # Midjourney官方Bot ID
        }
    
    def _build_midjourney_prompt(self, prompt: str, negative_prompt: str = "",
                                  aspect_ratio: str = None, style: str = None,
                                  quality: str = None, seed: int = None) -> str:
        """
        构建Midjourney提示词
        
        Midjourney提示词格式：
        /imagine prompt: {prompt} --ar {aspect_ratio} --style {style} --quality {quality} --seed {seed} --no {negative_prompt}
        """
        # 基础提示词
        mj_prompt = f"/imagine prompt: {prompt}"
        
        # 宽高比
        if aspect_ratio:
            mj_prompt += f" --ar {aspect_ratio}"
        elif self.config.get('aspect_ratio'):
            mj_prompt += f" --ar {self.config.get('aspect_ratio')}"
        
        # 风格
        if style:
            mj_prompt += f" --style {style}"
        elif self.config.get('style'):
            mj_prompt += f" --style {self.config.get('style')}"
        
        # 质量
        if quality:
            mj_prompt += f" --quality {quality}"
        elif self.config.get('quality'):
            mj_prompt += f" --quality {self.config.get('quality')}"
        
        # 种子（用于复现）
        if seed:
            mj_prompt += f" --seed {seed}"
        elif self.config.get('seed'):
            mj_prompt += f" --seed {self.config.get('seed')}"
        
        # 负面提示词（--no参数）
        if negative_prompt:
            mj_prompt += f" --no {negative_prompt}"
        elif self.config.get('default_negative_prompt'):
            mj_prompt += f" --no {self.config.get('default_negative_prompt')}"
        
        return mj_prompt
    
    async def _send_command(self, prompt: str):
        """发送Midjourney命令到Discord频道"""
        channel = self.bot.get_channel(int(self.channel_id))
        if not channel:
            raise Exception(f"无法找到频道（ID: {self.channel_id}）")
        
        # 生成任务ID（用于后续匹配消息）
        import uuid
        self.current_task_id = str(uuid.uuid4())[:8]
        
        # 发送命令
        print(f"📤 发送Midjourney命令到频道...")
        await channel.send(prompt)
        
        # 等待生成完成（Midjourney通常需要1-2分钟）
        print(f"⏳ 等待Midjourney生成（通常需要60-120秒）...")
        await asyncio.sleep(60)  # 基础等待时间
        
        # 继续等待，直到检测到完成消息
        max_wait = 120  # 最多再等2分钟
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.current_task_id and len(self.generated_images) > 0:
                # 检测到图片，再等一会儿确保全部生成完成
                await asyncio.sleep(10)
                break
            await asyncio.sleep(5)
        
        return self.generated_images
    
    def generate(self, prompt: str, negative_prompt: str = "",
                 aspect_ratio: str = None, style: str = None,
                 quality: str = None, seed: int = None,
                 output_dir: str = None) -> List[str]:
        """
        生成图片（同步接口）
        
        Args:
            prompt: 正面提示词
            negative_prompt: 负面提示词
            aspect_ratio: 宽高比（如 "16:9"）
            style: 风格（如 "raw", "cute"）
            quality: 质量（如 "hd"）
            seed: 随机种子
            output_dir: 输出目录
        
        Returns:
            生成的图片文件路径列表
        """
        # 构建Midjourney提示词
        mj_prompt = self._build_midjourney_prompt(
            prompt=prompt,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio,
            style=style,
            quality=quality,
            seed=seed
        )
        
        print(f"🎨 正在使用Midjourney生成图片...")
        print(f"   提示词：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"   Midjourney命令：{mj_prompt[:100]}{'...' if len(mj_prompt) > 100 else ''}")
        
        # 清空之前的图片
        self.generated_images = []
        
        # 启动Bot并发送命令
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果已有事件循环，使用create_task
            task = loop.create_task(self._send_command(mj_prompt))
            loop.run_until_complete(task)
            image_urls = task.result()
        else:
            # 否则直接运行
            image_urls = loop.run_until_complete(self._send_command(mj_prompt))
        
        # 下载图片
        output_dir = output_dir or self.config.get('output_dir', '../outputs/scenes/')
        output_paths = self._download_images(image_urls, output_dir)
        
        print(f"✅ 生成完成！共{len(output_paths)}张图片")
        for path in output_paths:
            print(f"   📁 {path}")
        
        return output_paths
    
    def _download_images(self, image_urls: List[str], output_dir: str) -> List[str]:
        """下载多张图片"""
        # 创建输出目录
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        output_paths = []
        for i, url in enumerate(image_urls):
            suffix = f'_{i+1:03d}'
            path = self._download_image(url, output_dir, suffix)
            output_paths.append(path)
        
        return output_paths
    
    def _download_image(self, image_url: str, output_dir: str, suffix: str = "") -> str:
        """下载单张图片"""
        import requests
        
        # 获取文件扩展名
        ext = self.config.get('output_format', 'PNG').lower()
        if not ext.startswith('.'):
            ext = f'.{ext}'
        
        # 生成文件名
        timestamp = int(time.time())
        filename = f"midjourney_{timestamp}{suffix}{ext}"
        output_path = os.path.join(output_dir, filename)
        
        # 下载图片
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return output_path
    
    def batch_generate(self, prompts: List[str], negative_prompt: str = "",
                       output_dir: str = None) -> List[List[str]]:
        """
        批量生成图片（逐个生成，避免触发限流）
        
        Args:
            prompts: 提示词列表
            negative_prompt: 负面提示词
            output_dir: 输出目录
        
        Returns:
            每个提示词对应的图片文件路径列表的列表
        """
        output_dir = output_dir or self.config.get('output_dir', '../outputs/scenes/')
        
        results = []
        for i, prompt in enumerate(tqdm(prompts, desc="批量生成（Midjourney）", unit="prompt")):
            try:
                print(f"\n🔄 进度：{i+1}/{len(prompts)}")
                paths = self.generate(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    output_dir=output_dir
                )
                results.append(paths)
                
                # 避免触发限流，等待一段时间
                if i < len(prompts) - 1:
                    wait_time = 60  # Midjourney通常需要1分钟生成一张
                    print(f"⏳ 等待{wait_time}秒（避免触发限流）...")
                    time.sleep(wait_time)
                
            except Exception as e:
                print(f"⚠️ 提示词 {i+1} 生成失败：{str(e)}")
                results.append([])
        
        return results
    
    def __del__(self):
        """析构函数，关闭Bot"""
        if hasattr(self, 'bot'):
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.bot.close())
            else:
                loop.run_until_complete(self.bot.close())


# 简化版（不使用Discord Bot，直接调用Midjourney网页版API）
class MidjourneyWebAPI:
    """Midjourney 网页版API客户端（逆向工程接口，可能随时失效）"""
    
    def __init__(self, api_key: str = None, config_path: str = None):
        """
        初始化网页版API客户端
        
        注意：Midjourney没有官方API，这里使用的是第三方逆向接口
        稳定性无法保证，建议优先使用Discord Bot方案
        """
        print("⚠️ 警告：MidjourneyWebAPI 使用的是非官方接口，稳定性无法保证！")
        print("   建议优先使用 MidjourneyBot（Discord Bot方案）")
        
        self.api_key = api_key or os.getenv("MIDJOURNEY_API_KEY")
        if not self.api_key:
            raise ValueError("未找到Midjourney API密钥！请在 config/.env 中设置 MIDJOURNEY_API_KEY")
        
        self.base_url = "https://api.midjourney.com/v1"  # 示例URL，实际可能不同
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), '../config/midjourney_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {}
    
    def generate(self, prompt: str, negative_prompt: str = "",
                 aspect_ratio: str = None, style: str = None,
                 quality: str = None, seed: int = None,
                 output_dir: str = None) -> List[str]:
        """
        生成图片（网页版API）
        
        注意：这个实现是基于假设的API接口，实际使用时需要根据具体API文档调整
        """
        # 构建请求数据（示例格式，实际可能不同）
        data = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio": aspect_ratio or self.config.get('aspect_ratio', '2:3'),
            "style": style or self.config.get('style', 'raw'),
            "quality": quality or self.config.get('quality', 'hd'),
            "seed": seed or self.config.get('seed')
        }
        
        print(f"🎨 正在使用Midjourney网页版API生成图片...")
        print(f"   提示词：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        
        # 发送请求（假设接口是 /generate）
        response = self.session.post(f"{self.base_url}/generate", json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        # 解析响应（假设返回 {'task_id': '...'}）
        task_id = result.get('task_id')
        if not task_id:
            raise Exception(f"API响应格式错误：{result}")
        
        # 轮询任务状态
        print(f"⏳ 任务已提交（ID: {task_id}），等待生成完成...")
        image_urls = self._poll_task_status(task_id)
        
        # 下载图片
        output_dir = output_dir or self.config.get('output_dir', '../outputs/scenes/')
        output_paths = self._download_images(image_urls, output_dir)
        
        print(f"✅ 生成完成！共{len(output_paths)}张图片")
        for path in output_paths:
            print(f"   📁 {path}")
        
        return output_paths
    
    def _poll_task_status(self, task_id: str, max_wait: int = 300) -> List[str]:
        """
        轮询任务状态
        
        Args:
            task_id: 任务ID
            max_wait: 最大等待时间（秒）
        
        Returns:
            生成的图片URL列表
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            response = self.session.get(f"{self.base_url}/tasks/{task_id}", timeout=30)
            response.raise_for_status()
            result = response.json()
            
            status = result.get('status')
            if status == 'completed':
                # 任务完成，返回图片URL
                image_urls = [img['url'] for img in result.get('images', [])]
                return image_urls
            elif status == 'failed':
                raise Exception(f"任务失败：{result.get('error', '未知错误')}")
            
            # 继续等待
            print(f"   ⏳ 任务状态：{status}，已等待{int(time.time() - start_time)}秒...")
            time.sleep(10)
        
        raise Exception(f"任务超时（已等待{max_wait}秒）")
    
    def _download_images(self, image_urls: List[str], output_dir: str) -> List[str]:
        """下载多张图片"""
        # 创建输出目录
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        output_paths = []
        for i, url in enumerate(image_urls):
            suffix = f'_{i+1:03d}'
            path = self._download_image(url, output_dir, suffix)
            output_paths.append(path)
        
        return output_paths
    
    def _download_image(self, image_url: str, output_dir: str, suffix: str = "") -> str:
        """下载单张图片"""
        import requests
        
        # 获取文件扩展名
        ext = self.config.get('output_format', 'PNG').lower()
        if not ext.startswith('.'):
            ext = f'.{ext}'
        
        # 生成文件名
        timestamp = int(time.time())
        filename = f"midjourney_web_{timestamp}{suffix}{ext}"
        output_path = os.path.join(output_dir, filename)
        
        # 下载图片
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return output_path


# 命令行测试
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Midjourney Bot 测试')
    parser.add_argument('--prompt', type=str, required=True, help='提示词')
    parser.add_argument('--negative', type=str, default='', help='负面提示词')
    parser.add_argument('--ar', type=str, default='2:3', help='宽高比（如 16:9）')
    parser.add_argument('--style', type=str, default='raw', help='风格（raw/cute等）')
    parser.add_argument('--quality', type=str, default='hd', help='质量（hd等）')
    parser.add_argument('--seed', type=int, default=None, help='随机种子')
    parser.add_argument('--output', type=str, default='../outputs/scenes/', help='输出目录')
    parser.add_argument('--use-web-api', action='store_true', help='使用网页版API（非官方）')
    
    args = parser.parse_args()
    
    try:
        if args.use_web_api:
            # 使用网页版API
            api = MidjourneyWebAPI(config_path='../config/midjourney_config.json')
            api.generate(
                prompt=args.prompt,
                negative_prompt=args.negative,
                aspect_ratio=args.ar,
                style=args.style,
                quality=args.quality,
                seed=args.seed,
                output_dir=args.output
            )
        else:
            # 使用Discord Bot
            bot = MidjourneyBot(config_path='../config/midjourney_config.json')
            bot.generate(
                prompt=args.prompt,
                negative_prompt=args.negative,
                aspect_ratio=args.ar,
                style=args.style,
                quality=args.quality,
                seed=args.seed,
                output_dir=args.output
            )
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
