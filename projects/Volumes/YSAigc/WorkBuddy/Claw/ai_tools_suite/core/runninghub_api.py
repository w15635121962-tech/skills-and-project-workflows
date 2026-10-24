"""
RunningHub API 封装模块
支持文本生成图片、图生图、局部重绘、放大等功能
"""

import os
import json
import time
import requests
from typing import List, Dict, Optional, Union
from pathlib import Path
from tqdm import tqdm


class RunningHubAPI:
    """RunningHub API 客户端"""
    
    def __init__(self, api_key: str = None, config_path: str = None):
        """
        初始化API客户端
        
        Args:
            api_key: RunningHub API密钥（优先级高）
            config_path: 配置文件路径（优先级低，用于读取api_key）
        """
        self.api_key = api_key or self._load_api_key_from_config(config_path)
        if not self.api_key:
            raise ValueError(
                "未找到RunningHub API密钥！\n"
                "请在 config/.env 中设置 RUNNINGHUB_API_KEY，\n"
                "或在初始化时传入 api_key 参数。"
            )
        
        self.base_url = "https://api.runninghub.ai/v1"
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
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('api_key')
        
        # 尝试从环境变量读取
        return os.getenv("RUNNINGHUB_API_KEY")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), '../config/runninghub_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 返回默认配置
        return {
            "model": "SDXL 1.0",
            "sampler": "DPM++ 2M Karras",
            "steps": 30,
            "cfg_scale": 7.5,
            "resolution": "1024x1024",
            "batch_size": 4,
            "output_format": "PNG",
            "default_negative_prompt": "cartoon, anime, low quality, blurry, deformed",
            "output_dir": "../outputs/characters/",
            "seed": None
        }
    
    def _make_request(self, endpoint: str, method: str = "POST", data: Dict = None, 
                      max_retries: int = 3, timeout: int = 120) -> Dict:
        """
        发送API请求（带重试机制）
        
        Args:
            endpoint: API端点（如 '/text2img'）
            method: HTTP方法（GET/POST）
            data: 请求数据
            max_retries: 最大重试次数
            timeout: 超时时间（秒）
        
        Returns:
            API响应的JSON数据
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(max_retries):
            try:
                if method.upper() == "POST":
                    response = self.session.post(url, json=data, timeout=timeout)
                else:
                    response = self.session.get(url, params=data, timeout=timeout)
                
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"⚠️ 请求失败（{type(e).__name__}），{wait_time}秒后重试... ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"API请求失败（已重试{max_retries}次）：{str(e)}")
    
    def text_to_image(self, prompt: str, negative_prompt: str = "", 
                      width: int = 1024, height: int = 1024, 
                      steps: int = None, cfg_scale: float = None, 
                      seed: int = None, batch_size: int = None,
                      output_dir: str = None) -> List[str]:
        """
        文本生成图片
        
        Args:
            prompt: 正面提示词
            negative_prompt: 负面提示词（可选）
            width: 图片宽度
            height: 图片高度
            steps: 采样步数（默认从配置读取）
            cfg_scale: CFG权重（默认从配置读取）
            seed: 随机种子（None表示随机）
            batch_size: 批量生成数量（默认从配置读取）
            output_dir: 输出目录（默认从配置读取）
        
        Returns:
            生成的图片文件路径列表
        """
        # 使用默认配置
        steps = steps or self.config.get('steps', 30)
        cfg_scale = cfg_scale or self.config.get('cfg_scale', 7.5)
        seed = seed if seed is not None else self.config.get('seed')
        batch_size = batch_size or self.config.get('batch_size', 4)
        negative_prompt = negative_prompt or self.config.get('default_negative_prompt', '')
        output_dir = output_dir or self.config.get('output_dir', '../outputs/characters/')
        
        # 构建请求数据
        data = {
            "model": self.config.get('model', 'SDXL 1.0'),
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "sampler": self.config.get('sampler', 'DPM++ 2M Karras'),
            "batch_size": batch_size,
            "output_format": self.config.get('output_format', 'PNG')
        }
        
        if seed is not None:
            data['seed'] = seed
        
        print(f"🎨 正在生成图片...")
        print(f"   提示词：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"   尺寸：{width}x{height}，步数：{steps}，CFG：{cfg_scale}")
        print(f"   批量：{batch_size}张")
        
        # 发送请求
        result = self._make_request('/text2img', data=data)
        
        # 解析响应（假设返回 {'images': [{'url': '...'}, ...]}）
        image_urls = []
        if 'images' in result:
            image_urls = [img['url'] for img in result['images']]
        elif 'data' in result and 'images' in result['data']:
            image_urls = [img['url'] for img in result['data']['images']]
        else:
            raise Exception(f"API响应格式错误：{result}")
        
        # 下载图片
        output_paths = self._download_images(image_urls, output_dir)
        
        print(f"✅ 生成完成！共{len(output_paths)}张图片")
        for path in output_paths:
            print(f"   📁 {path}")
        
        return output_paths
    
    def image_to_image(self, input_image: str, prompt: str, 
                       negative_prompt: str = "", strength: float = 0.7,
                       steps: int = None, cfg_scale: float = None,
                       output_dir: str = None) -> List[str]:
        """
        图生图（Image-to-Image）
        
        Args:
            input_image: 输入图片路径
            prompt: 正面提示词
            negative_prompt: 负面提示词
            strength: 重绘强度（0.0-1.0，越大越偏离原图）
            steps: 采样步数
            cfg_scale: CFG权重
            output_dir: 输出目录
        
        Returns:
            生成的图片文件路径列表
        """
        steps = steps or self.config.get('steps', 30)
        cfg_scale = cfg_scale or self.config.get('cfg_scale', 7.5)
        negative_prompt = negative_prompt or self.config.get('default_negative_prompt', '')
        output_dir = output_dir or self.config.get('output_dir', '../outputs/characters/')
        
        # 读取输入图片并转换为base64
        import base64
        with open(input_image, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        data = {
            "model": self.config.get('model', 'SDXL 1.0'),
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image": image_data,
            "strength": strength,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "sampler": self.config.get('sampler', 'DPM++ 2M Karras'),
            "output_format": self.config.get('output_format', 'PNG')
        }
        
        print(f"🎨 正在图生图...")
        print(f"   输入图片：{input_image}")
        print(f"   提示词：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"   重绘强度：{strength}")
        
        result = self._make_request('/img2img', data=data)
        
        # 解析响应并下载图片
        image_urls = []
        if 'images' in result:
            image_urls = [img['url'] for img in result['images']]
        
        output_paths = self._download_images(image_urls, output_dir)
        
        print(f"✅ 图生图完成！共{len(output_paths)}张图片")
        for path in output_paths:
            print(f"   📁 {path}")
        
        return output_paths
    
    def inpainting(self, input_image: str, mask_image: str, prompt: str,
                   negative_prompt: str = "", steps: int = None,
                   cfg_scale: float = None, output_dir: str = None) -> List[str]:
        """
        局部重绘（Inpainting）
        
        Args:
            input_image: 输入图片路径
            mask_image: 蒙版图片路径（白色区域将被重绘）
            prompt: 正面提示词
            negative_prompt: 负面提示词
            steps: 采样步数
            cfg_scale: CFG权重
            output_dir: 输出目录
        
        Returns:
            生成的图片文件路径列表
        """
        steps = steps or self.config.get('steps', 30)
        cfg_scale = cfg_scale or self.config.get('cfg_scale', 7.5)
        negative_prompt = negative_prompt or self.config.get('default_negative_prompt', '')
        output_dir = output_dir or self.config.get('output_dir', '../outputs/characters/')
        
        # 读取输入图片和蒙版并转换为base64
        import base64
        with open(input_image, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        with open(mask_image, 'rb') as f:
            mask_data = base64.b64encode(f.read()).decode('utf-8')
        
        data = {
            "model": self.config.get('model', 'SDXL 1.0'),
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "image": image_data,
            "mask": mask_data,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "sampler": self.config.get('sampler', 'DPM++ 2M Karras'),
            "output_format": self.config.get('output_format', 'PNG')
        }
        
        print(f"🎨 正在局部重绘...")
        print(f"   输入图片：{input_image}")
        print(f"   蒙版图片：{mask_image}")
        print(f"   提示词：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        
        result = self._make_request('/inpaint', data=data)
        
        # 解析响应并下载图片
        image_urls = []
        if 'images' in result:
            image_urls = [img['url'] for img in result['images']]
        
        output_paths = self._download_images(image_urls, output_dir)
        
        print(f"✅ 局部重绘完成！共{len(output_paths)}张图片")
        for path in output_paths:
            print(f"   📁 {path}")
        
        return output_paths
    
    def upscale(self, input_image: str, scale: int = 2, 
                output_dir: str = None) -> str:
        """
        放大图片（Upscale）
        
        Args:
            input_image: 输入图片路径
            scale: 放大倍数（2或4）
            output_dir: 输出目录
        
        Returns:
            放大后的图片文件路径
        """
        output_dir = output_dir or self.config.get('output_dir', '../outputs/characters/')
        
        # 读取输入图片并转换为base64
        import base64
        with open(input_image, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        data = {
            "image": image_data,
            "scale": scale
        }
        
        print(f"🔍 正在放大图片（{scale}×）...")
        print(f"   输入图片：{input_image}")
        
        result = self._make_request('/upscale', data=data)
        
        # 解析响应并下载图片
        image_url = None
        if 'image' in result:
            image_url = result['image']['url']
        elif 'data' in result and 'image' in result['data']:
            image_url = result['data']['image']['url']
        
        if not image_url:
            raise Exception(f"API响应格式错误：{result}")
        
        # 下载图片
        output_path = self._download_image(image_url, output_dir, suffix=f'_upscale{scale}x')
        
        print(f"✅ 放大完成！")
        print(f"   📁 {output_path}")
        
        return output_path
    
    def batch_generate(self, prompts: List[str], negative_prompt: str = "",
                      width: int = 1024, height: int = 1024,
                      output_dir: str = None) -> List[List[str]]:
        """
        批量生成图片
        
        Args:
            prompts: 提示词列表
            negative_prompt: 负面提示词
            width: 图片宽度
            height: 图片高度
            output_dir: 输出目录
        
        Returns:
            每个提示词对应的图片文件路径列表的列表
        """
        output_dir = output_dir or self.config.get('output_dir', '../outputs/characters/')
        
        results = []
        for i, prompt in enumerate(tqdm(prompts, desc="批量生成", unit="prompt")):
            try:
                paths = self.text_to_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    output_dir=output_dir
                )
                results.append(paths)
            except Exception as e:
                print(f"⚠️ 提示词 {i+1} 生成失败：{str(e)}")
                results.append([])
        
        return results
    
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
        # 获取文件扩展名
        import re
        ext = self.config.get('output_format', 'PNG').lower()
        if not ext.startswith('.'):
            ext = f'.{ext}'
        
        # 生成文件名
        timestamp = int(time.time())
        filename = f"generated_{timestamp}{suffix}{ext}"
        output_path = os.path.join(output_dir, filename)
        
        # 下载图片
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return output_path
    
    def __del__(self):
        """析构函数，关闭session"""
        if hasattr(self, 'session'):
            self.session.close()


# 命令行测试
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='RunningHub API 测试')
    parser.add_argument('--prompt', type=str, required=True, help='提示词')
    parser.add_argument('--negative', type=str, default='', help='负面提示词')
    parser.add_argument('--width', type=int, default=1024, help='宽度')
    parser.add_argument('--height', type=int, default=1024, help='高度')
    parser.add_argument('--steps', type=int, default=30, help='采样步数')
    parser.add_argument('--cfg', type=float, default=7.5, help='CFG权重')
    parser.add_argument('--seed', type=int, default=None, help='随机种子')
    parser.add_argument('--batch', type=int, default=1, help='批量生成数量')
    parser.add_argument('--output', type=str, default='../outputs/characters/', help='输出目录')
    
    args = parser.parse_args()
    
    try:
        api = RunningHubAPI(config_path='../config/runninghub_config.json')
        api.text_to_image(
            prompt=args.prompt,
            negative_prompt=args.negative,
            width=args.width,
            height=args.height,
            steps=args.steps,
            cfg_scale=args.cfg,
            seed=args.seed,
            batch_size=args.batch,
            output_dir=args.output
        )
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
