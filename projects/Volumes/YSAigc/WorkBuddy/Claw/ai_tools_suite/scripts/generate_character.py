"""
命令行工具：生成角色设定图
使用方法：
    python3.14 scripts/generate_character.py --name "Bella" --count 4
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
    parser = argparse.ArgumentParser(description='生成角色设定图')
    
    parser.add_argument('--name', type=str, required=True, help='角色名称（在提示词库中的名称）')
    parser.add_argument('--age', type=int, help='年龄（可选，用于覆盖默认参数）')
    parser.add_argument('--gender', type=str, help='性别（可选）')
    parser.add_argument('--features', type=str, help='外貌特征（可选，用于覆盖默认参数）')
    parser.add_argument('--outfit', type=str, help='服装（可选，用于覆盖默认参数）')
    parser.add_argument('--view', type=str, default='front', help='视角（front/side/3-4_view/full_body）')
    parser.add_argument('--expression', type=str, help='表情（可选，用于覆盖默认参数）')
    parser.add_argument('--count', type=int, default=4, help='生成数量')
    parser.add_argument('--output', type=str, help='输出目录（可选，默认 outputs/characters/<name>/）')
    parser.add_argument('--seed', type=int, help='随机种子（可选，用于复现）')
    parser.add_argument('--no-prompt-library', action='store_true', help='不使用提示词库，使用默认提示词')
    
    args = parser.parse_args()
    
    print(f"🎨 开始生成角色设定图：{args.name}")
    
    # 初始化API客户端
    try:
        api = RunningHubAPI(config_path='../config/runninghub_config.json')
    except ValueError as e:
        print(f"❌ 错误：{str(e)}")
        print(f"   请先配置 config/.env 文件，设置 RUNNINGHUB_API_KEY")
        sys.exit(1)
    
    # 初始化提示词管理器
    prompt_manager = None if args.no_prompt_library else PromptManager()
    
    # 构建参数字典
    params = {}
    if args.age:
        params['age'] = args.age
    if args.gender:
        params['gender'] = args.gender
    if args.features:
        params['features'] = args.features
    if args.outfit:
        params['outfit'] = args.outfit
    if args.view:
        params['view'] = args.view
    if args.expression:
        params['expression'] = args.expression
    
    # 获取提示词
    if not args.no_prompt_library and prompt_manager:
        try:
            prompt_data = prompt_manager.get_prompt(
                category='characters',
                name=args.name,
                **params
            )
            prompt = prompt_data['positive']
            negative_prompt = prompt_data['negative']
            seed = prompt_data.get('seed') or args.seed
            print(f"✅ 已从提示词库获取提示词")
        except ValueError as e:
            print(f"⚠️ 提示词库中没有角色 '{args.name}'，将使用默认提示词")
            prompt = f"{args.name}, {params.get('view', 'front view')}, realistic texture, 8K resolution, photorealistic"
            negative_prompt = "cartoon, anime, low quality, blurry, deformed"
            seed = args.seed
    else:
        prompt = f"{args.name}, {params.get('view', 'front view')}, realistic texture, 8K resolution, photorealistic"
        negative_prompt = "cartoon, anime, low quality, blurry, deformed"
        seed = args.seed
    
    print(f"   提示词：{prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    print(f"   负面提示词：{negative_prompt[:80]}{'...' if len(negative_prompt) > 80 else ''}")
    if seed:
        print(f"   随机种子：{seed}")
    print(f"   生成数量：{args.count}")
    
    # 确定输出目录
    if args.output:
        output_dir = args.output
    else:
        output_dir = f"../outputs/characters/{args.name}/"
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成图片
    try:
        print(f"\n🎨 正在生成图片...")
        paths = api.text_to_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            batch_size=args.count,
            output_dir=output_dir
        )
        
        print(f"\n✅ 生成完成！共 {len(paths)} 张图片")
        print(f"   输出目录：{os.path.abspath(output_dir)}")
        for i, path in enumerate(paths):
            print(f"   {i+1}. {path}")
        
        # 保存生成信息
        info = {
            "name": args.name,
            "params": params,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "count": args.count,
            "output_dir": output_dir,
            "paths": paths,
            "timestamp": __import__('time').time()
        }
        
        info_path = os.path.join(output_dir, f"info_{int(__import__('time').time())}.json")
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        print(f"\n📋 生成信息已保存：{info_path}")
        
    except Exception as e:
        print(f"\n❌ 生成失败：{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
