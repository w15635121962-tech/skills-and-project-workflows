"""
场景生成工作流
完整的场景概念图生成流程：多时间/多天气/多角度
"""

import os
import json
import time
from typing import List, Dict, Optional
from pathlib import Path
from tqdm import tqdm


class SceneGenerationWorkflow:
    """场景生成工作流"""
    
    def __init__(self, api_client=None, prompt_manager=None, 
                  output_dir: str = None):
        """
        初始化工作流
        
        Args:
            api_client: API客户端（RunningHubAPI/MidjourneyBot等）
            prompt_manager: 提示词管理器
            output_dir: 输出目录
        """
        self.api_client = api_client
        self.prompt_manager = prompt_manager
        self.output_dir = output_dir or "../outputs/scenes/"
        
        # 场景变化参数
        self.time_of_day = ['dawn', 'morning', 'noon', 'afternoon', 'dusk', 'night']
        self.weather = ['clear', 'cloudy', 'rainy', 'snowy', 'foggy']
        self.angles = ['wide_shot', 'medium_shot', 'close_up', 'top_down', 'low_angle']
        self.moods = ['cheerful', 'melancholic', 'tense', 'romantic', 'mysterious']
    
    def generate_scene_complete(self, scene_name: str, 
                               variations: List[str] = None,
                               count_per_variation: int = 4,
                               use_prompt_library: bool = True) -> Dict:
        """
        完整场景生成流程
        
        Args:
            scene_name: 场景名称（在提示词库中的名称）
            variations: 变化列表（如 ['day', 'night', 'rainy']）
            count_per_variation: 每个变化生成的数量
            use_prompt_library: 是否使用提示词库
        
        Returns:
            生成结果字典
        """
        print(f"🏞️ 开始生成场景：{scene_name}")
        
        # 确定变化列表
        if not variations:
            variations = ['day', 'night', 'rainy', 'foggy']
        
        print(f"   变化列表：{variations}")
        print(f"   每个变化生成：{count_per_variation} 张")
        
        # 创建输出目录
        scene_output_dir = os.path.join(self.output_dir, scene_name)
        os.makedirs(scene_output_dir, exist_ok=True)
        
        # 生成每个变化
        results = {}
        total_tasks = len(variations)
        
        with tqdm(total=total_tasks, desc="生成场景变化", unit="variation") as pbar:
            for i, variation in enumerate(variations):
                try:
                    pbar.set_postfix_str(f"正在生成 {variation}...")
                    
                    # 生成这个变化的场景图
                    result = self._generate_scene_variation(
                        scene_name=scene_name,
                        variation=variation,
                        count=count_per_variation,
                        output_dir=scene_output_dir,
                        use_prompt_library=use_prompt_library
                    )
                    
                    results[variation] = result
                    pbar.update(1)
                    
                    # 避免触发限流
                    if i < total_tasks - 1 and self.api_client:
                        wait_time = 10
                        print(f"⏳ 等待 {wait_time} 秒（避免触发限流）...")
                        time.sleep(wait_time)
                
                except Exception as e:
                    print(f"\n❌ 生成变化 '{variation}' 失败：{str(e)}")
                    results[variation] = []
                    pbar.update(1)
        
        # 生成总结报告
        report = self._generate_report(scene_name, variations, results)
        
        # 保存报告
        report_path = os.path.join(scene_output_dir, f"report_{int(time.time())}.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 场景生成完成！")
        print(f"   输出目录：{scene_output_dir}")
        print(f"   报告已保存：{report_path}")
        
        return results
    
    def _generate_scene_variation(self, scene_name: str, variation: str,
                                   count: int, output_dir: str,
                                   use_prompt_library: bool = True) -> List[str]:
        """
        生成场景的某个变化
        
        Args:
            scene_name: 场景名称
            variation: 变化（day/night/rainy等）
            count: 生成数量
            output_dir: 输出目录
            use_prompt_library: 是否使用提示词库
        
        Returns:
            生成的图片路径列表
        """
        # 创建变化子目录
        variation_dir = os.path.join(output_dir, variation)
        os.makedirs(variation_dir, exist_ok=True)
        
        # 获取提示词
        if use_prompt_library and self.prompt_manager:
            # 从提示词库获取
            prompt_data = self.prompt_manager.get_prompt(
                category='scenes',
                name=scene_name,
                time=variation
            )
            prompt = prompt_data['positive']
            negative_prompt = prompt_data['negative']
            seed = prompt_data.get('seed')
        else:
            # 使用默认提示词
            prompt = f"{scene_name}, {variation}, cinematic lighting, 8K resolution, photorealistic"
            negative_prompt = "cartoon, anime, low quality, blurry, deformed"
            seed = None
        
        # 调用API生成
        if not self.api_client:
            raise Exception("未配置API客户端！")
        
        print(f"\n   🎨 生成变化：{variation}")
        print(f"      提示词：{prompt[:60]}{'...' if len(prompt) > 60 else ''}")
        
        # 判断API客户端类型
        if hasattr(self.api_client, 'text_to_image'):
            # RunningHub API
            return self.api_client.text_to_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                batch_size=count,
                output_dir=variation_dir
            )
        
        elif hasattr(self.api_client, 'generate'):
            # Midjourney Bot
            return self.api_client.generate(
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                output_dir=variation_dir
            )
        
        else:
            raise Exception(f"未知的API客户端类型：{type(self.api_client)}")
    
    def generate_multiple_angles(self, scene_name: str, 
                                 time_of_day: str = 'noon',
                                 weather: str = 'clear',
                                 count_per_angle: int = 3,
                                 use_prompt_library: bool = True) -> Dict:
        """
        生成同一场景的多个角度
        
        Args:
            scene_name: 场景名称
            time_of_day: 时间（dawn/morning/noon/afternoon/dusk/night）
            weather: 天气（clear/cloudy/rainy/snowy/foggy）
            count_per_angle: 每个角度生成的数量
            use_prompt_library: 是否使用提示词库
        
        Returns:
            角度 -> 生成图片路径列表的字典
        """
        print(f"📷 开始生成多角度场景：{scene_name}")
        print(f"   时间：{time_of_day}")
        print(f"   天气：{weather}")
        print(f"   角度：{self.angles}")
        
        # 创建输出目录
        scene_output_dir = os.path.join(self.output_dir, scene_name, f"{time_of_day}_{weather}")
        os.makedirs(scene_output_dir, exist_ok=True)
        
        # 生成每个角度
        results = {}
        
        for angle in self.angles:
            try:
                print(f"\n   📷 生成角度：{angle}")
                
                # 构建提示词（添加角度描述）
                if use_prompt_library and self.prompt_manager:
                    prompt_data = self.prompt_manager.get_prompt(
                        category='scenes',
                        name=scene_name,
                        time=time_of_day,
                        lighting=weather
                    )
                    prompt = prompt_data['positive'] + f", {angle}"
                    negative_prompt = prompt_data['negative']
                else:
                    prompt = f"{scene_name}, {time_of_day}, {weather}, {angle}, cinematic lighting, 8K resolution"
                    negative_prompt = "cartoon, anime, low quality, blurry"
                
                # 调用API生成
                if hasattr(self.api_client, 'text_to_image'):
                    paths = self.api_client.text_to_image(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        batch_size=count_per_angle,
                        output_dir=os.path.join(scene_output_dir, angle)
                    )
                elif hasattr(self.api_client, 'generate'):
                    paths = self.api_client.generate(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        output_dir=os.path.join(scene_output_dir, angle)
                    )
                else:
                    raise Exception(f"未知的API客户端类型")
                
                results[angle] = paths
                
                # 避免触发限流
                time.sleep(5)
            
            except Exception as e:
                print(f"   ❌ 生成角度 '{angle}' 失败：{str(e)}")
                results[angle] = []
        
        print(f"\n✅ 多角度场景生成完成！")
        print(f"   输出目录：{scene_output_dir}")
        
        return results
    
    def generate_scene_series(self, scene_name: str,
                              series_config: List[Dict] = None,
                              count_per_shot: int = 3,
                              use_prompt_library: bool = True) -> Dict:
        """
        生成场景系列（用于分镜脚本）
        
        Args:
            scene_name: 场景名称
            series_config: 系列配置（列表，每个元素是一个镜头的配置）
            count_per_shot: 每个镜头生成的数量
            use_prompt_library: 是否使用提示词库
        
        Returns:
            镜头编号 -> 生成图片路径列表的字典
        
        Example:
            series_config = [
                {"shot": 1, "time": "night", "angle": "wide_shot", "mood": "tense"},
                {"shot": 2, "time": "night", "angle": "close_up", "mood": "tense"},
                ...
            ]
        """
        if not series_config:
            # 使用默认配置（5个镜头）
            series_config = [
                {"shot": 1, "time": "night", "angle": "wide_shot", "mood": "tense"},
                {"shot": 2, "time": "night", "angle": "medium_shot", "mood": "tense"},
                {"shot": 3, "time": "night", "angle": "close_up", "mood": "emotional"},
                {"shot": 4, "time": "night", "angle": "over_the_shoulder", "mood": "dramatic"},
                {"shot": 5, "time": "night", "angle": "low_angle", "mood": "mysterious"}
            ]
        
        print(f"🎬 开始生成场景系列：{scene_name}")
        print(f"   镜头数量：{len(series_config)}")
        
        # 创建输出目录
        scene_output_dir = os.path.join(self.output_dir, scene_name, "series")
        os.makedirs(scene_output_dir, exist_ok=True)
        
        # 生成每个镜头
        results = {}
        
        for config in tqdm(series_config, desc="生成镜头", unit="shot"):
            shot_num = config['shot']
            time_of_day = config.get('time', 'noon')
            angle = config.get('angle', 'medium_shot')
            mood = config.get('mood', 'neutral')
            
            try:
                # 构建提示词
                if use_prompt_library and self.prompt_manager:
                    prompt_data = self.prompt_manager.get_prompt(
                        category='scenes',
                        name=scene_name,
                        time=time_of_day
                    )
                    prompt = f"{prompt_data['positive']}, {angle}, {mood} mood"
                    negative_prompt = prompt_data['negative']
                else:
                    prompt = f"{scene_name}, {time_of_day}, {angle}, {mood} mood, cinematic lighting"
                    negative_prompt = "cartoon, anime, low quality, blurry"
                
                # 调用API生成
                shot_dir = os.path.join(scene_output_dir, f"shot_{shot_num:02d}")
                os.makedirs(shot_dir, exist_ok=True)
                
                if hasattr(self.api_client, 'text_to_image'):
                    paths = self.api_client.text_to_image(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        batch_size=count_per_shot,
                        output_dir=shot_dir
                    )
                elif hasattr(self.api_client, 'generate'):
                    paths = self.api_client.generate(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        output_dir=shot_dir
                    )
                else:
                    raise Exception(f"未知的API客户端类型")
                
                results[f"shot_{shot_num:02d}"] = {
                    "config": config,
                    "paths": paths
                }
                
                # 避免触发限流
                time.sleep(5)
            
            except Exception as e:
                print(f"\n❌ 生成镜头 {shot_num} 失败：{str(e)}")
                results[f"shot_{shot_num:02d}"] = {
                    "config": config,
                    "paths": []
                }
        
        print(f"\n✅ 场景系列生成完成！")
        print(f"   输出目录：{scene_output_dir}")
        
        return results
    
    def _generate_report(self, scene_name: str, variations: List[str], 
                         results: Dict) -> Dict:
        """
        生成总结报告
        
        Args:
            scene_name: 场景名称
            variations: 变化列表
            results: 生成结果
        
        Returns:
            报告字典
        """
        report = {
            "scene_name": scene_name,
            "timestamp": time.time(),
            "variations": variations,
            "total_generated": 0,
            "by_variation": {},
            "output_dir": self.output_dir
        }
        
        for variation, paths in results.items():
            count = len(paths) if isinstance(paths, list) else 0
            report["by_variation"][variation] = {
                "count": count,
                "paths": paths if count > 0 else []
            }
            report["total_generated"] += count
        
        return report


# 命令行测试
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='场景生成工作流')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 完整场景生成
    complete_parser = subparsers.add_parser('complete', help='完整场景生成（多变化）')
    complete_parser.add_argument('--scene', type=str, required=True, help='场景名称')
    complete_parser.add_argument('--variations', type=str, nargs='+', help='变化列表')
    complete_parser.add_argument('--count', type=int, default=4, help='每个变化生成的数量')
    complete_parser.add_argument('--output', type=str, help='输出目录')
    
    # 多角度生成
    angles_parser = subparsers.add_parser('angles', help='生成多角度场景')
    angles_parser.add_argument('--scene', type=str, required=True, help='场景名称')
    angles_parser.add_argument('--time', type=str, default='noon', help='时间')
    angles_parser.add_argument('--weather', type=str, default='clear', help='天气')
    angles_parser.add_argument('--count', type=int, default=3, help='每个角度生成的数量')
    
    # 场景系列生成（分镜）
    series_parser = subparsers.add_parser('series', help='生成场景系列（分镜）')
    series_parser.add_argument('--scene', type=str, required=True, help='场景名称')
    series_parser.add_argument('--shots', type=int, default=5, help='镜头数量')
    series_parser.add_argument('--count', type=int, default=3, help='每个镜头生成的数量')
    
    args = parser.parse_args()
    
    # 初始化工作流（这里只是示例，实际需要传入真实的API客户端）
    print("⚠️ 这只是命令行示例，实际需要配置真实的API客户端")
    print("   请先配置 config/.env 文件，然后运行对应的Python脚本")
    
    if args.command == 'complete':
        print(f"\n🏞️ 完整场景生成：{args.scene}")
        print(f"   变化：{args.variations}")
        print(f"   每个变化生成：{args.count} 张")
        # workflow = SceneGenerationWorkflow(api_client=api, prompt_manager=pm)
        # workflow.generate_scene_complete(...)
    
    elif args.command == 'angles':
        print(f"\n📷 多角度场景生成：{args.scene}")
        print(f"   时间：{args.time}")
        print(f"   天气：{args.weather}")
        # workflow = SceneGenerationWorkflow(api_client=api, prompt_manager=pm)
        # workflow.generate_multiple_angles(...)
    
    elif args.command == 'series':
        print(f"\n🎬 场景系列生成：{args.scene}")
        print(f"   镜头数量：{args.shots}")
        # workflow = SceneGenerationWorkflow(api_client=api, prompt_manager=pm)
        # workflow.generate_scene_series(...)
    
    else:
        parser.print_help()
