"""
视频生成工作流
完整的视频生成流程：从资产图到视频，支持首尾帧、参考图、延长等功能
"""

import os
import json
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from tqdm import tqdm


class VideoGenerationWorkflow:
    """视频生成工作流"""
    
    def __init__(self, api_client=None, output_dir: str = None):
        """
        初始化工作流
        
        Args:
            api_client: API客户端（RunwayAPI/PikaAPI等）
            output_dir: 输出目录
        """
        self.api_client = api_client
        self.output_dir = output_dir or "../outputs/videos/"
        
        # 视频生成参数
        self.default_duration = 5  # 秒
        self.default_resolution = "1280x720"
        self.default_motion_strength = 5  # 1-10
    
    def generate_from_image(self, image_path: str, prompt: str = "",
                          duration: int = None, output_path: str = None,
                          motion_strength: int = None) -> str:
        """
        从图片生成视频（动画化）
        
        Args:
            image_path: 输入图片路径
            prompt: 视频提示词（描述动作）
            duration: 视频时长（秒）
            output_path: 输出视频路径
            motion_strength: 运动强度（1-10）
        
        Returns:
            生成的视频文件路径
        """
        duration = duration or self.default_duration
        motion_strength = motion_strength or self.default_motion_strength
        
        print(f"🎬 从图片生成视频...")
        print(f"   输入图片：{image_path}")
        if prompt:
            print(f"   提示词：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"   时长：{duration}秒")
        print(f"   运动强度：{motion_strength}/10")
        
        # 检查API客户端
        if not self.api_client:
            raise Exception("未配置API客户端！")
        
        # 判断API客户端类型
        if hasattr(self.api_client, 'image_to_video'):
            # Runway API
            return self.api_client.image_to_video(
                image_path=image_path,
                prompt=prompt,
                duration=duration,
                output_dir=os.path.dirname(output_path) if output_path else self.output_dir
            )
        
        elif hasattr(self.api_client, 'generate'):
            # Pika API
            return self.api_client.image_to_video(
                image_path=image_path,
                prompt=prompt,
                duration=duration,
                motion_strength=motion_strength,
                output_dir=os.path.dirname(output_path) if output_path else self.output_dir
            )
        
        else:
            raise Exception(f"未知的API客户端类型：{type(self.api_client)}")
    
    def generate_from_prompt(self, prompt: str, negative_prompt: str = "",
                            duration: int = None, resolution: str = None,
                            image_url: str = None, output_path: str = None) -> str:
        """
        从提示词生成视频
        
        Args:
            prompt: 视频提示词
            negative_prompt: 负面提示词
            duration: 视频时长（秒）
            resolution: 分辨率
            image_url: 参考图片URL（可选）
            output_path: 输出视频路径
        
        Returns:
            生成的视频文件路径
        """
        duration = duration or self.default_duration
        resolution = resolution or self.default_resolution
        
        print(f"🎬 从提示词生成视频...")
        print(f"   提示词：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"   时长：{duration}秒")
        print(f"   分辨率：{resolution}")
        if image_url:
            print(f"   参考图片：{image_url}")
        
        # 检查API客户端
        if not self.api_client:
            raise Exception("未配置API客户端！")
        
        # 判断API客户端类型
        if hasattr(self.api_client, 'text_to_video'):
            # Runway API
            return self.api_client.text_to_video(
                prompt=prompt,
                negative_prompt=negative_prompt,
                duration=duration,
                resolution=resolution,
                image_url=image_url,
                output_dir=os.path.dirname(output_path) if output_path else self.output_dir
            )
        
        elif hasattr(self.api_client, 'generate'):
            # Pika API
            return self.api_client.text_to_video(
                prompt=prompt,
                negative_prompt=negative_prompt,
                duration=duration,
                resolution=resolution,
                motion_strength=self.default_motion_strength,
                output_dir=os.path.dirname(output_path) if output_path else self.output_dir
            )
        
        else:
            raise Exception(f"未知的API客户端类型：{type(self.api_client)}")
    
    def generate_with_start_end_frames(self, start_image: str, end_image: str,
                                     prompt: str = "", duration: int = None,
                                     output_path: str = None) -> str:
        """
        使用首尾帧生成视频（部分API支持）
        
        Args:
            start_image: 起始帧图片路径
            end_image: 结束帧图片路径
            prompt: 视频提示词（描述动作）
            duration: 视频时长（秒）
            output_path: 输出视频路径
        
        Returns:
            生成的视频文件路径
        """
        duration = duration or self.default_duration
        
        print(f"🎬 使用首尾帧生成视频...")
        print(f"   起始帧：{start_image}")
        print(f"   结束帧：{end_image}")
        if prompt:
            print(f"   提示词：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"   时长：{duration}秒")
        
        # 检查API客户端
        if not self.api_client:
            raise Exception("未配置API客户端！")
        
        # 注意：不是所有API都支持首尾帧
        # 这里提供一个通用实现，具体需要看API文档
        print(f"⚠️ 注意：不是所有API都支持首尾帧，请检查API文档")
        
        # 假设API支持 start_image 和 end_image 参数
        if hasattr(self.api_client, 'image_to_video'):
            # 扩展API客户端以支持首尾帧
            # 这里需要修改 core/runway_api.py 添加对应方法
            raise NotImplementedError("首尾帧功能尚未实现，需要API支持")
        else:
            raise Exception(f"API客户端不支持首尾帧：{type(self.api_client)}")
    
    def extend_video(self, video_path: str, prompt: str,
                     duration: int = None, output_path: str = None) -> str:
        """
        延长视频
        
        Args:
            video_path: 输入视频路径
            prompt: 延长部分的提示词
            duration: 延长的时长（秒）
            output_path: 输出视频路径
        
        Returns:
            延长后的视频文件路径
        """
        duration = duration or self.default_duration
        
        print(f"🎬 延长视频...")
        print(f"   输入视频：{video_path}")
        print(f"   延长提示词：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"   延长：{duration}秒")
        
        # 检查API客户端
        if not self.api_client:
            raise Exception("未配置API客户端！")
        
        # 判断API客户端类型
        if hasattr(self.api_client, 'extend_video'):
            # Runway API
            return self.api_client.extend_video(
                video_path=video_path,
                prompt=prompt,
                duration=duration,
                output_dir=os.path.dirname(output_path) if output_path else self.output_dir
            )
        
        elif hasattr(self.api_client, 'extend'):
            # Pika API
            return self.api_client.extend_video(
                video_path=video_path,
                prompt=prompt,
                duration=duration,
                output_dir=os.path.dirname(output_path) if output_path else self.output_dir
            )
        
        else:
            raise Exception(f"API客户端不支持延长视频：{type(self.api_client)}")
    
    def batch_generate_from_images(self, image_paths: List[str], 
                                 prompts: List[str] = None,
                                 durations: List[int] = None,
                                 output_dir: str = None) -> List[str]:
        """
        批量从图片生成视频
        
        Args:
            image_paths: 输入图片路径列表
            prompts: 视频提示词列表（可选，长度必须与image_paths相同）
            durations: 视频时长列表（可选）
            output_dir: 输出目录
        
        Returns:
            生成的视频文件路径列表
        """
        if prompts and len(prompts) != len(image_paths):
            raise ValueError("prompts 长度必须与 image_paths 相同！")
        
        if durations and len(durations) != len(image_paths):
            raise ValueError("durations 长度必须与 image_paths 相同！")
        
        output_dir = output_dir or self.output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🎬 批量从图片生成视频...")
        print(f"   图片数量：{len(image_paths)}")
        print(f"   输出目录：{output_dir}")
        
        results = []
        
        with tqdm(total=len(image_paths), desc="生成视频", unit="video") as pbar:
            for i, image_path in enumerate(image_paths):
                try:
                    pbar.set_postfix_str(f"正在处理 {i+1}/{len(image_paths)}...")
                    
                    # 获取提示词和时长
                    prompt = prompts[i] if prompts else ""
                    duration = durations[i] if durations else self.default_duration
                    
                    # 生成视频
                    output_path = os.path.join(output_dir, f"video_{i+1:03d}.mp4")
                    
                    video_path = self.generate_from_image(
                        image_path=image_path,
                        prompt=prompt,
                        duration=duration,
                        output_path=output_path
                    )
                    
                    results.append(video_path)
                    pbar.update(1)
                    
                    # 避免触发限流
                    if i < len(image_paths) - 1:
                        wait_time = 10
                        print(f"⏳ 等待 {wait_time} 秒（避免触发限流）...")
                        time.sleep(wait_time)
                
                except Exception as e:
                    print(f"\n❌ 处理图片 {i+1} 失败：{str(e)}")
                    results.append(None)
                    pbar.update(1)
        
        # 统计
        success_count = sum(1 for r in results if r is not None)
        print(f"\n✅ 批量生成完成！成功 {success_count}/{len(image_paths)}")
        
        return results
    
    def generate_scene_videos(self, scene_name: str, shot_configs: List[Dict],
                              output_dir: str = None) -> Dict[str, str]:
        """
        生成场景视频（用于分镜脚本）
        
        Args:
            scene_name: 场景名称
            shot_configs: 镜头配置列表，每个元素是一个字典：
                [
                    {
                        "shot": 1,
                        "image": "path/to/image.jpg",
                        "prompt": "Bella walks slowly toward camera",
                        "duration": 5
                    },
                    ...
                ]
            output_dir: 输出目录
        
        Returns:
            镜头编号 -> 视频文件路径的字典
        """
        output_dir = output_dir or os.path.join(self.output_dir, scene_name)
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🎬 生成场景视频：{scene_name}")
        print(f"   镜头数量：{len(shot_configs)}")
        print(f"   输出目录：{output_dir}")
        
        results = {}
        
        for config in tqdm(shot_configs, desc="生成镜头", unit="shot"):
            shot_num = config['shot']
            image_path = config.get('image')
            prompt = config.get('prompt', '')
            duration = config.get('duration', self.default_duration)
            
            try:
                print(f"\n   🎥 镜头 #{shot_num}")
                
                # 生成视频
                output_path = os.path.join(output_dir, f"shot_{shot_num:02d}.mp4")
                
                if image_path and os.path.exists(image_path):
                    # 从图片生成
                    video_path = self.generate_from_image(
                        image_path=image_path,
                        prompt=prompt,
                        duration=duration,
                        output_path=output_path
                    )
                else:
                    # 从提示词生成
                    video_path = self.generate_from_prompt(
                        prompt=prompt,
                        duration=duration,
                        output_dir=output_dir
                    )
                    # 重命名
                    import shutil
                    new_path = output_path
                    shutil.move(video_path, new_path)
                    video_path = new_path
                
                results[f"shot_{shot_num:02d}"] = video_path
                
                # 避免触发限流
                time.sleep(10)
            
            except Exception as e:
                print(f"   ❌ 镜头 #{shot_num} 生成失败：{str(e)}")
                results[f"shot_{shot_num:02d}"] = None
        
        # 保存结果
        report_path = os.path.join(output_dir, f"report_{int(time.time())}.json")
        report = {
            "scene_name": scene_name,
            "timestamp": time.time(),
            "shots": len(shot_configs),
            "results": {k: v for k, v in results.items()}
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 场景视频生成完成！")
        print(f"   报告已保存：{report_path}")
        
        return results


# 命令行测试
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='视频生成工作流')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 从图片生成视频
    img2vid = subparsers.add_parser('img2vid', help='从图片生成视频')
    img2vid.add_argument('--image', type=str, required=True, help='输入图片路径')
    img2vid.add_argument('--prompt', type=str, default='', help='视频提示词')
    img2vid.add_argument('--duration', type=int, default=5, help='视频时长（秒）')
    img2vid.add_argument('--output', type=str, help='输出视频路径')
    img2vid.add_argument('--motion', type=int, default=5, help='运动强度（1-10）')
    
    # 从提示词生成视频
    text2vid = subparsers.add_parser('text2vid', help='从提示词生成视频')
    text2vid.add_argument('--prompt', type=str, required=True, help='视频提示词')
    text2vid.add_argument('--negative', type=str, default='', help='负面提示词')
    text2vid.add_argument('--duration', type=int, default=5, help='视频时长（秒）')
    text2vid.add_argument('--resolution', type=str, default='1280x720', help='分辨率')
    text2vid.add_argument('--image', type=str, help='参考图片URL（可选）')
    text2vid.add_argument('--output', type=str, help='输出视频路径')
    
    # 延长视频
    extend = subparsers.add_parser('extend', help='延长视频')
    extend.add_argument('--video', type=str, required=True, help='输入视频路径')
    extend.add_argument('--prompt', type=str, required=True, help='延长部分的提示词')
    extend.add_argument('--duration', type=int, default=5, help='延长时长（秒）')
    extend.add_argument('--output', type=str, help='输出视频路径')
    
    # 批量从图片生成视频
    batch = subparsers.add_parser('batch', help='批量从图片生成视频')
    batch.add_argument('--input', type=str, required=True, help='输入图片目录')
    batch.add_argument('--prompts', type=str, help='提示词文件（每行一个）')
    batch.add_argument('--duration', type=int, default=5, help='视频时长（秒）')
    batch.add_argument('--output', type=str, help='输出目录')
    
    args = parser.parse_args()
    
    # 初始化工作流（这里只是示例，实际需要传入真实的API客户端）
    print("⚠️ 这只是命令行示例，实际需要配置真实的API客户端")
    print("   请先配置 config/.env 文件，然后运行对应的Python脚本")
    
    if args.command == 'img2vid':
        print(f"\n🎬 从图片生成视频")
        print(f"   输入图片：{args.image}")
        print(f"   提示词：{args.prompt}")
        print(f"   时长：{args.duration}秒")
        # workflow = VideoGenerationWorkflow(api_client=api)
        # workflow.generate_from_image(...)
    
    elif args.command == 'text2vid':
        print(f"\n🎬 从提示词生成视频")
        print(f"   提示词：{args.prompt}")
        print(f"   时长：{args.duration}秒")
        # workflow = VideoGenerationWorkflow(api_client=api)
        # workflow.generate_from_prompt(...)
    
    elif args.command == 'extend':
        print(f"\n🎬 延长视频")
        print(f"   输入视频：{args.video}")
        print(f"   延长提示词：{args.prompt}")
        # workflow = VideoGenerationWorkflow(api_client=api)
        # workflow.extend_video(...)
    
    elif args.command == 'batch':
        print(f"\n🎬 批量从图片生成视频")
        print(f"   输入目录：{args.input}")
        # workflow = VideoGenerationWorkflow(api_client=api)
        # workflow.batch_generate_from_images(...)
    
    else:
        parser.print_help()
