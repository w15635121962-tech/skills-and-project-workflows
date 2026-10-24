"""
批量生成模块
支持从提示词库批量生成角色/场景/道具资产
"""

import os
import json
import time
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio


class BatchGenerator:
    """批量生成器"""
    
    def __init__(self, api_client=None, prompt_manager=None, 
                  config_path: str = None, max_workers: int = 3):
        """
        初始化批量生成器
        
        Args:
            api_client: API客户端（RunningHubAPI/MidjourneyBot等）
            prompt_manager: 提示词管理器（PromptManager实例）
            config_path: 配置文件路径
            max_workers: 最大并行线程数
        """
        self.api_client = api_client
        self.prompt_manager = prompt_manager
        self.max_workers = max_workers
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 生成任务队列
        self.task_queue = []
        self.results = []
        
        # 统计信息
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "start_time": None,
            "end_time": None
        }
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), '../config/runninghub_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {}
    
    def generate_characters(self, characters: List[str] = None, 
                          views: List[str] = None, 
                          expressions: List[str] = None,
                          count_per_view: int = 4,
                          output_dir: str = None,
                          use_prompt_library: bool = True) -> Dict[str, List[str]]:
        """
        批量生成角色
        
        Args:
            characters: 角色名称列表（None表示全部）
            views: 视角列表（['front view', 'side profile', ...]）
            expressions: 表情列表（['smiling', 'crying', ...]）
            count_per_view: 每个视角/表情生成的数量
            output_dir: 输出目录
            use_prompt_library: 是否使用提示词库
        
        Returns:
            角色名称 -> 生成图片路径列表的字典
        """
        print(f"🎨 开始批量生成角色...")
        
        # 确定要生成的角色
        if not characters and self.prompt_manager:
            characters = list(self.prompt_manager.library.get('characters', {}).keys())
        
        if not characters:
            raise ValueError("未指定角色，且提示词库中没有角色数据！")
        
        print(f"   角色列表：{characters}")
        
        # 确定视角和表情
        if not views:
            views = ['front view', '3/4 view', 'side profile', 'full body']
        
        if not expressions:
            expressions = ['neutral', 'smiling', 'crying', 'surprised']
        
        # 创建任务列表
        tasks = []
        for character in characters:
            for view in views:
                for expr in expressions:
                    task = {
                        'type': 'character',
                        'character': character,
                        'view': view,
                        'expression': expr,
                        'count': count_per_view,
                        'output_dir': output_dir or f"../outputs/characters/{character}/"
                    }
                    tasks.append(task)
        
        self.stats['total'] = len(tasks)
        self.stats['start_time'] = time.time()
        
        print(f"   共 {len(tasks)} 个任务（{len(characters)} 角色 × {len(views)} 视角 × {len(expressions)} 表情）")
        print(f"   预计生成图片：{len(tasks) * count_per_view} 张")
        
        # 执行批量生成
        results = self._execute_tasks(tasks, use_prompt_library)
        
        self.stats['end_time'] = time.time()
        self._print_stats()
        
        return results
    
    def generate_scenes(self, scenes: List[str] = None,
                       variations: List[str] = None,
                       count_per_scene: int = 4,
                       output_dir: str = None,
                       use_prompt_library: bool = True) -> Dict[str, List[str]]:
        """
        批量生成场景
        
        Args:
            scenes: 场景名称列表（None表示全部）
            variations: 变化列表（['day', 'night', 'sunny', 'rainy']等）
            count_per_scene: 每个场景/变化生成的数量
            output_dir: 输出目录
            use_prompt_library: 是否使用提示词库
        
        Returns:
            场景名称 -> 生成图片路径列表的字典
        """
        print(f"🏞️ 开始批量生成场景...")
        
        # 确定要生成的场景
        if not scenes and self.prompt_manager:
            scenes = list(self.prompt_manager.library.get('scenes', {}).keys())
        
        if not scenes:
            raise ValueError("未指定场景，且提示词库中没有场景数据！")
        
        print(f"   场景列表：{scenes}")
        
        # 确定变化
        if not variations:
            variations = ['day', 'night']
        
        # 创建任务列表
        tasks = []
        for scene in scenes:
            for var in variations:
                task = {
                    'type': 'scene',
                    'scene': scene,
                    'variation': var,
                    'count': count_per_scene,
                    'output_dir': output_dir or f"../outputs/scenes/{scene}/"
                }
                tasks.append(task)
        
        self.stats['total'] = len(tasks)
        self.stats['start_time'] = time.time()
        
        print(f"   共 {len(tasks)} 个任务（{len(scenes)} 场景 × {len(variations)} 变化）")
        print(f"   预计生成图片：{len(tasks) * count_per_scene} 张")
        
        # 执行批量生成
        results = self._execute_tasks(tasks, use_prompt_library)
        
        self.stats['end_time'] = time.time()
        self._print_stats()
        
        return results
    
    def generate_from_prompt_list(self, prompts: List[str], 
                                  negative_prompts: List[str] = None,
                                  output_dir: str = None,
                                  batch_size: int = 4) -> List[List[str]]:
        """
        从提示词列表批量生成
        
        Args:
            prompts: 提示词列表
            negative_prompts: 负面提示词列表（可选，长度必须与prompts相同）
            output_dir: 输出目录
            batch_size: 每个提示词生成的数量
        
        Returns:
            每个提示词对应的图片路径列表
        """
        print(f"📝 开始从提示词列表批量生成...")
        print(f"   提示词数量：{len(prompts)}")
        print(f"   每个提示词生成：{batch_size} 张")
        print(f"   预计生成图片：{len(prompts) * batch_size} 张")
        
        if negative_prompts and len(negative_prompts) != len(prompts):
            raise ValueError("negative_prompts 长度必须与 prompts 相同！")
        
        self.stats['total'] = len(prompts)
        self.stats['start_time'] = time.time()
        
        # 创建任务列表
        tasks = []
        for i, prompt in enumerate(prompts):
            task = {
                'type': 'prompt',
                'prompt': prompt,
                'negative_prompt': negative_prompts[i] if negative_prompts else "",
                'count': batch_size,
                'output_dir': output_dir or "../outputs/characters/"
            }
            tasks.append(task)
        
        # 执行批量生成
        results = self._execute_tasks(tasks, use_prompt_library=False)
        
        self.stats['end_time'] = time.time()
        self._print_stats()
        
        return results
    
    def _execute_tasks(self, tasks: List[Dict], use_prompt_library: bool = True) -> Dict:
        """
        执行任务列表
        
        Args:
            tasks: 任务列表
            use_prompt_library: 是否使用提示词库
        
        Returns:
            结果字典（任务标识 -> 生成图片路径列表）
        """
        results = {}
        
        # 进度条
        with tqdm(total=len(tasks), desc="批量生成", unit="task") as pbar:
            # 单线程执行（避免触发API限流）
            for i, task in enumerate(tasks):
                try:
                    pbar.set_postfix_str(f"正在处理任务 {i+1}/{len(tasks)}...")
                    
                    # 执行任务
                    if task['type'] == 'character':
                        result = self._generate_character(task, use_prompt_library)
                        task_id = f"{task['character']}_{task['view']}_{task['expression']}"
                    
                    elif task['type'] == 'scene':
                        result = self._generate_scene(task, use_prompt_library)
                        task_id = f"{task['scene']}_{task['variation']}"
                    
                    elif task['type'] == 'prompt':
                        result = self._generate_from_prompt(task)
                        task_id = f"prompt_{i}"
                    
                    else:
                        raise ValueError(f"未知任务类型：{task['type']}")
                    
                    # 保存结果
                    results[task_id] = result
                    self.stats['success'] += 1
                    
                    # 避免触发限流
                    if i < len(tasks) - 1 and self.api_client:
                        wait_time = self.config.get('wait_between_tasks', 5)
                        time.sleep(wait_time)
                
                except Exception as e:
                    print(f"\n❌ 任务 {i+1} 失败：{str(e)}")
                    self.stats['failed'] += 1
                    results[f"task_{i}"] = []
                
                finally:
                    pbar.update(1)
        
        return results
    
    def _generate_character(self, task: Dict, use_prompt_library: bool = True) -> List[str]:
        """
        生成角色图片
        
        Args:
            task: 任务字典
            use_prompt_library: 是否使用提示词库
        
        Returns:
            生成的图片路径列表
        """
        character = task['character']
        view = task['view']
        expression = task['expression']
        count = task['count']
        output_dir = task['output_dir']
        
        # 使用提示词库
        if use_prompt_library and self.prompt_manager:
            prompt_data = self.prompt_manager.get_prompt('characters', character, view=view, expression=expression)
            prompt = prompt_data['positive']
            negative_prompt = prompt_data['negative']
            seed = prompt_data.get('seed')
        
        else:
            # 使用默认提示词模板
            prompt = f"{character}, {view}, {expression}, realistic texture, 8K resolution, photorealistic"
            negative_prompt = "cartoon, anime, low quality, blurry, deformed"
            seed = None
        
        # 调用API生成
        if not self.api_client:
            raise Exception("未配置API客户端！")
        
        # 判断API客户端类型
        if hasattr(self.api_client, 'text_to_image'):
            # RunningHub API
            return self.api_client.text_to_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                batch_size=count,
                output_dir=output_dir
            )
        
        elif hasattr(self.api_client, 'generate'):
            # Midjourney Bot
            return self.api_client.generate(
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                output_dir=output_dir
            )
        
        else:
            raise Exception(f"未知的API客户端类型：{type(self.api_client)}")
    
    def _generate_scene(self, task: Dict, use_prompt_library: bool = True) -> List[str]:
        """
        生成场景图片
        
        Args:
            task: 任务字典
            use_prompt_library: 是否使用提示词库
        
        Returns:
            生成的图片路径列表
        """
        scene = task['scene']
        variation = task['variation']
        count = task['count']
        output_dir = task['output_dir']
        
        # 使用提示词库
        if use_prompt_library and self.prompt_manager:
            prompt_data = self.prompt_manager.get_prompt('scenes', scene, time=variation)
            prompt = prompt_data['positive']
            negative_prompt = prompt_data['negative']
            seed = prompt_data.get('seed')
        
        else:
            # 使用默认提示词模板
            prompt = f"{scene}, {variation}, cinematic lighting, 8K resolution, photorealistic"
            negative_prompt = "cartoon, anime, low quality, blurry, deformed"
            seed = None
        
        # 调用API生成
        if not self.api_client:
            raise Exception("未配置API客户端！")
        
        # 判断API客户端类型
        if hasattr(self.api_client, 'text_to_image'):
            # RunningHub API
            return self.api_client.text_to_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                batch_size=count,
                output_dir=output_dir
            )
        
        elif hasattr(self.api_client, 'generate'):
            # Midjourney Bot
            return self.api_client.generate(
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                output_dir=output_dir
            )
        
        else:
            raise Exception(f"未知的API客户端类型：{type(self.api_client)}")
    
    def _generate_from_prompt(self, task: Dict) -> List[str]:
        """
        从提示词生成图片
        
        Args:
            task: 任务字典
        
        Returns:
            生成的图片路径列表
        """
        prompt = task['prompt']
        negative_prompt = task.get('negative_prompt', '')
        count = task['count']
        output_dir = task['output_dir']
        
        # 调用API生成
        if not self.api_client:
            raise Exception("未配置API客户端！")
        
        # 判断API客户端类型
        if hasattr(self.api_client, 'text_to_image'):
            # RunningHub API
            return self.api_client.text_to_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                batch_size=count,
                output_dir=output_dir
            )
        
        elif hasattr(self.api_client, 'generate'):
            # Midjourney Bot
            return self.api_client.generate(
                prompt=prompt,
                negative_prompt=negative_prompt,
                output_dir=output_dir
            )
        
        else:
            raise Exception(f"未知的API客户端类型：{type(self.api_client)}")
    
    def _print_stats(self):
        """打印统计信息"""
        print(f"\n📊 批量生成统计：")
        print(f"   总任务数：{self.stats['total']}")
        print(f"   成功：{self.stats['success']}")
        print(f"   失败：{self.stats['failed']}")
        print(f"   跳过：{self.stats['skipped']}")
        
        if self.stats['start_time'] and self.stats['end_time']:
            elapsed = self.stats['end_time'] - self.stats['start_time']
            print(f"   总耗时：{elapsed:.1f} 秒 ({elapsed/60:.1f} 分钟)")
            
            if self.stats['success'] > 0:
                avg_time = elapsed / self.stats['success']
                print(f"   平均每个任务：{avg_time:.1f} 秒")
    
    def save_results(self, results: Dict, output_path: str = None):
        """
        保存生成结果到JSON文件
        
        Args:
            results: 生成结果字典
            output_path: 输出文件路径（可选，默认为 outputs/batch_results_<timestamp>.json）
        """
        if not output_path:
            timestamp = int(time.time())
            output_path = f"../outputs/batch_results_{timestamp}.json"
        
        # 转换为可序列化的格式
        serializable_results = {}
        for key, value in results.items():
            if isinstance(value, list):
                serializable_results[key] = value
            else:
                serializable_results[key] = str(value)
        
        # 添加统计信息
        output_data = {
            "results": serializable_results,
            "stats": self.stats,
            "config": {
                "api_client": type(self.api_client).__name__ if self.api_client else None,
                "max_workers": self.max_workers,
                "timestamp": time.time()
            }
        }
        
        # 保存到文件
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 生成结果已保存：{output_path}")


# 命令行测试
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='批量生成工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 批量生成角色
    char_parser = subparsers.add_parser('characters', help='批量生成角色')
    char_parser.add_argument('--characters', type=str, nargs='+', help='角色名称列表')
    char_parser.add_argument('--views', type=str, nargs='+', help='视角列表')
    char_parser.add_argument('--expressions', type=str, nargs='+', help='表情列表')
    char_parser.add_argument('--count', type=int, default=4, help='每个任务生成的数量')
    char_parser.add_argument('--output', type=str, help='输出目录')
    char_parser.add_argument('--api', type=str, choices=['runninghub', 'midjourney'], default='runninghub', help='API客户端')
    
    # 批量生成场景
    scene_parser = subparsers.add_parser('scenes', help='批量生成场景')
    scene_parser.add_argument('--scenes', type=str, nargs='+', help='场景名称列表')
    scene_parser.add_argument('--variations', type=str, nargs='+', help='变化列表')
    scene_parser.add_argument('--count', type=int, default=4, help='每个任务生成的数量')
    scene_parser.add_argument('--output', type=str, help='输出目录')
    scene_parser.add_argument('--api', type=str, choices=['runninghub', 'midjourney'], default='runninghub', help='API客户端')
    
    # 从提示词列表生成
    prompt_parser = subparsers.add_parser('prompts', help='从提示词列表批量生成')
    prompt_parser.add_argument('--input', type=str, required=True, help='提示词列表文件（每行一个提示词）')
    prompt_parser.add_argument('--count', type=int, default=4, help='每个提示词生成的数量')
    prompt_parser.add_argument('--output', type=str, help='输出目录')
    prompt_parser.add_argument('--api', type=str, choices=['runninghub', 'midjourney'], default='runninghub', help='API客户端')
    
    args = parser.parse_args()
    
    # 初始化API客户端（这里只是示例，实际需要传入真实的API密钥）
    print("⚠️ 这只是命令行示例，实际需要配置真实的API密钥")
    print("   请先配置 config/.env 文件，然后运行对应的Python脚本")
    
    # 示例：初始化PromptManager
    from modules.prompt_manager import PromptManager
    pm = PromptManager()
    
    # 示例：初始化BatchGenerator
    # from core.runninghub_api import RunningHubAPI
    # api = RunningHubAPI()
    # bg = BatchGenerator(api_client=api, prompt_manager=pm)
    
    if args.command == 'characters':
        print(f"\n🎨 批量生成角色：{args.characters}")
        print(f"   视角：{args.views}")
        print(f"   表情：{args.expressions}")
        print(f"   每个任务生成：{args.count} 张")
        # bg.generate_characters(...)
    
    elif args.command == 'scenes':
        print(f"\n🏞️ 批量生成场景：{args.scenes}")
        print(f"   变化：{args.variations}")
        print(f"   每个任务生成：{args.count} 张")
        # bg.generate_scenes(...)
    
    elif args.command == 'prompts':
        print(f"\n📝 从提示词列表批量生成")
        print(f"   输入文件：{args.input}")
        print(f"   每个提示词生成：{args.count} 张")
        # 读取提示词列表
        # with open(args.input, 'r', encoding='utf-8') as f:
        #     prompts = [line.strip() for line in f if line.strip()]
        # bg.generate_from_prompt_list(...)
    
    else:
        parser.print_help()
