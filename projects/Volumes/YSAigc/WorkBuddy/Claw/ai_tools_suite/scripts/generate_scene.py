"""
命令行工具：生成场景概念图
使用方法：
    python3.14 scripts/generate_scene.py --name "Hospital_Corridor" --variations day night
"""

import os
import sys
import json
import argparse
from pathlib import Path

# 添加父目录到sys.path，以便导入模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.runninghub_api import RunningHubAPI
from modules.prompt_manager import PromptManager


def main():
    parser = argparse.ArgumentParser(description='生成场景概念图')
    
    parser.add_argument('--name', type=str, required=True, help='场景名称（在提示词库中的名称）')
    parser.add_argument('--variations', type=str, nargs='+', help='变化列表（day/night/rainy等）')
    parser.add_argument('--count', type=int, default=4, help='每个变化生成的数量')
    parser.add_argument('--output', type=str, help='输出目录（可选，默认 outputs/scenes/<name>/）')
    parser.add_argument('--seed', type=int, help='随机种子（可选，用于复现）')
    parser.add_argument('--no-prompt-library', action='store_true', help='不使用提示词库，使用默认提示词')
    
    args = parser.parse_args()
    
    print(f"🏞️ 开始生成场景概念图：{args.name}")
    
    # 初始化API客户端
    try:
        api = RunningHubAPI(config_path='../config/runninghub_config.json')
    except ValueError as e:
        print(f"❌ 错误：{str(e)}")
        print(f"   请先配置 config/.env 文件，设置 RUNNINGHUB_API_KEY")
        sys.exit(1)
    
    # 初始化提示词管理器
    prompt_manager = None if args.no_prompt_library else PromptManager()
    
    # 确定变化列表
    variations = args.variations or ['day', 'night', 'rainy', 'foggy']
    
    print(f"   变化列表：{variations}")
    print(f"   每个变化生成：{args.count} 张")
    
    # 创建输出目录
    if args.output:
        output_dir = args.output
    else:
        output_dir = f"../outputs/scenes/{args.name}/"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成每个变化
    results = {}
    
    for variation in variations:
        try:
            print(f"\n   🎨 生成变化：{variation}")
            
            # 创建变化子目录
            variation_dir = os.path.join(output_dir, variation)
            os.makedirs(variation_dir, exist_ok=True)
            
            # 获取提示词
            if not args.no_prompt_library and prompt_manager:
                try:
                    prompt_data = prompt_manager.get_prompt(
                        category='scenes',
                        name=args.name,
                        time=variation
                    )
                    prompt = prompt_data['positive']
                    negative_prompt = prompt_data['negative']
                    seed = prompt_data.get('seed') or args.seed
                    print(f"       ✅ 已从提示词库获取提示词")
                except ValueError as e:
                    print(f"       ⚠️ 提示词库中没有场景 '{args.name}'，将使用默认提示词")
                    prompt = f"{args.name}, {variation}, cinematic lighting, 8K resolution, photorealistic"
                    negative_prompt = "cartoon, anime, low quality, blurry, deformed"
                    seed = args.seed
            else:
                prompt = f"{args.name}, {variation}, cinematic lighting, 8K resolution, photorealistic"
                negative_prompt = "cartoon, anime, low quality, blurry, deformed"
                seed = args.seed
            
            print(f"       提示词：{prompt[:60]}{'...' if len(prompt) > 60 else ''}")
            
            # 调用API生成
            paths = api.text_to_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                seed=seed,
                batch_size=args.count,
                output_dir=variation_dir
            )
            
            results[variation] = paths
            
            # 避免触发限流
            if variation != variations[-1]:
                wait_time = 10
                print(f"       ⏳ 等待 {wait_time} 秒（避免触发限流）...")
                import time
                time.sleep(wait_time)
        
        except Exception as e:
            print(f"   ❌ 生成变化 '{variation}' 失败：{str(e)}")
            results[variation] = []
    
    # 生成总结报告
    print(f"\n✅ 场景生成完成！")
    
    total_generated = sum(len(paths) for paths in results.values())
    print(f"   总生成图片：{total_generated} 张")
    print(f"   输出目录：{os.path.abspath(output_dir)}")
    
    # 保存报告
    report = {
        "scene_name": args.name,
        "variations": variations,
        "count_per_variation": args.count,
        "results": {k: v for k, v in results.items()},
        "output_dir": output_dir,
        "timestamp": __import__('time').time()
    }
    
    report_path = os.path.join(output_dir, f"report_{int(__import__('time').time())}.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"   报告已保存：{report_path}")


if __name__ == "__main__":
    main()
