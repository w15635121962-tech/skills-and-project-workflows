#!/usr/bin/env python3
"""
批量处理脚本 - 批量生成角色和场景
"""
import argparse
import json
import sys
import os
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflows.character_generation import CharacterGenerationWorkflow
from workflows.scene_generation import SceneGenerationWorkflow
from modules.prompt_manager import PromptManager
from core.runninghub_api import RunningHubAPI


def load_batch_config(config_path: str) -> dict:
    """加载批量生成配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_batch_config(config: dict, config_path: str):
    """保存批量生成配置文件"""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def batch_generate_characters(api: RunningHubAPI, prompt_manager: PromptManager, 
                             characters: list, output_dir: str, **kwargs):
    """批量生成角色"""
    print(f"\n👤 批量生成角色 ({len(characters)} 个)")
    print("=" * 60)
    
    workflow = CharacterGenerationWorkflow(api, prompt_manager)
    
    results = []
    for i, char_config in enumerate(characters, 1):
        print(f"\n[{i}/{len(characters)}] 生成角色: {char_config.get('name', 'unknown')}")
        
        try:
            result = workflow.generate_character(
                character_name=char_config['name'],
                prompt_variant=char_config.get('prompt_variant'),
                negative_prompt=char_config.get('negative_prompt'),
                output_dir=output_dir,
                views=char_config.get('views', ['front', 'side', 'back']),
                expressions=char_config.get('expressions', ['neutral', 'smile']),
                **kwargs
            )
            
            results.append({
                'character': char_config['name'],
                'status': 'success',
                'result': result
            })
            print(f"✅ 角色 {char_config['name']} 生成完成")
            
        except Exception as e:
            print(f"❌ 角色 {char_config['name']} 生成失败: {e}")
            results.append({
                'character': char_config['name'],
                'status': 'failed',
                'error': str(e)
            })
        
        # 避免API限流
        if i < len(characters):
            time.sleep(2)
    
    return results


def batch_generate_scenes(api: RunningHubAPI, prompt_manager: PromptManager,
                         scenes: list, output_dir: str, **kwargs):
    """批量生成场景"""
    print(f"\n🏞️  批量生成场景 ({len(scenes)} 个)")
    print("=" * 60)
    
    workflow = SceneGenerationWorkflow(api, prompt_manager)
    
    results = []
    for i, scene_config in enumerate(scenes, 1):
        print(f"\n[{i}/{len(scenes)}] 生成场景: {scene_config.get('name', 'unknown')}")
        
        try:
            result = workflow.generate_scene(
                scene_name=scene_config['name'],
                prompt_variant=scene_config.get('prompt_variant'),
                negative_prompt=scene_config.get('negative_prompt'),
                output_dir=output_dir,
                variations=scene_config.get('variations', 3),
                **kwargs
            )
            
            results.append({
                'scene': scene_config['name'],
                'status': 'success',
                'result': result
            })
            print(f"✅ 场景 {scene_config['name']} 生成完成")
            
        except Exception as e:
            print(f"❌ 场景 {scene_config['name']} 生成失败: {e}")
            results.append({
                'scene': scene_config['name'],
                'status': 'failed',
                'error': str(e)
            })
        
        # 避免API限流
        if i < len(scenes):
            time.sleep(2)
    
    return results


def generate_batch_config_template(output_path: str):
    """生成批量配置模板"""
    template = {
        "characters": [
            {
                "name": "Character1",
                "prompt_variant": "elegant blue dress, pearl necklace",
                "negative_prompt": "ugly, deformed",
                "views": ["front", "side", "back"],
                "expressions": ["neutral", "smile", "serious"]
            },
            {
                "name": "Character2",
                "prompt_variant": "black suit, gold watch",
                "negative_prompt": "ugly, deformed",
                "views": ["front", "side"],
                "expressions": ["neutral", "smile"]
            }
        ],
        "scenes": [
            {
                "name": "Scene1",
                "prompt_variant": "morning sunlight, empty",
                "negative_prompt": "crowded, noisy",
                "variations": 3
            },
            {
                "name": "Scene2",
                "prompt_variant": "warm lighting, romantic",
                "negative_prompt": "cold, dark",
                "variations": 3
            }
        ],
        "output_dir": "outputs",
        "global_settings": {
            "width": 512,
            "height": 768,
            "steps": 30,
            "cfg_scale": 7.5,
            "batch_size": 1,
            "upscale": True,
            "quality_check": True
        }
    }
    
    save_batch_config(template, output_path)
    print(f"✅ 批量配置模板已生成: {output_path}")
    print("\n请编辑此文件，配置您要生成的角色和场景，然后运行:")
    print(f"  python scripts/batch_process.py --config {output_path}")


def main():
    parser = argparse.ArgumentParser(description='批量生成角色和场景')
    
    parser.add_argument('--config', type=str, help='批量生成配置文件路径 (JSON)')
    parser.add_argument('--characters', nargs='+', help='要生成的角色名称列表')
    parser.add_argument('--scenes', nargs='+', help='要生成的场景名称列表')
    parser.add_argument('--output-dir', type=str, default='outputs', help='输出目录')
    
    parser.add_argument('--width', type=int, default=512, help='图片宽度')
    parser.add_argument('--height', type=int, default=768, help='图片高度')
    parser.add_argument('--steps', type=int, default=30, help='生成步数')
    parser.add_argument('--cfg-scale', type=float, default=7.5, help='CFG缩放')
    parser.add_argument('--batch-size', type=int, default=1, help='批次大小')
    parser.add_argument('--upscale', action='store_true', help='是否放大')
    parser.add_argument('--no-upscale', dest='upscale', action='store_false', help='不放大')
    parser.set_defaults(upscale=True)
    parser.add_argument('--quality-check', action='store_true', help='是否质量检查')
    parser.add_argument('--no-quality-check', dest='quality_check', action='store_false', help='不检查质量')
    parser.set_defaults(quality_check=True)
    
    parser.add_argument('--generate-template', type=str, help='生成批量配置模板文件')
    parser.add_argument('--api-key', type=str, help='RunningHub API Key')
    parser.add_argument('--api-secret', type=str, help='RunningHub API Secret')
    
    args = parser.parse_args()
    
    # 生成配置模板
    if args.generate_template:
        generate_batch_config_template(args.generate_template)
        return
    
    # 加载配置
    if args.config:
        if not os.path.exists(args.config):
            print(f"❌ 配置文件不存在: {args.config}")
            return
        
        config = load_batch_config(args.config)
        characters = config.get('characters', [])
        scenes = config.get('scenes', [])
        output_dir = config.get('output_dir', args.output_dir)
        global_settings = config.get('global_settings', {})
        
        # 合并全局设置
        width = global_settings.get('width', args.width)
        height = global_settings.get('height', args.height)
        steps = global_settings.get('steps', args.steps)
        cfg_scale = global_settings.get('cfg_scale', args.cfg_scale)
        batch_size = global_settings.get('batch_size', args.batch_size)
        upscale = global_settings.get('upscale', args.upscale)
        quality_check = global_settings.get('quality_check', args.quality_check)
        
    else:
        if not args.characters and not args.scenes:
            print("❌ 错误: 必须指定 --config 或 --characters/--scenes")
            parser.print_help()
            return
        
        characters = [{'name': name} for name in args.characters] if args.characters else []
        scenes = [{'name': name} for name in args.scenes] if args.scenes else []
        output_dir = args.output_dir
        width = args.width
        height = args.height
        steps = args.steps
        cfg_scale = args.cfg_scale
        batch_size = args.batch_size
        upscale = args.upscale
        quality_check = args.quality_check
    
    # 初始化API和提示词管理器
    api_key = args.api_key or os.getenv('RUNNINGHUB_API_KEY')
    api_secret = args.api_secret or os.getenv('RUNNINGHUB_API_SECRET')
    
    if not api_key:
        print("❌ 错误: 必须提供 RunningHub API Key")
        print("   方法1: --api-key <key>")
        print("   方法2: 设置环境变量 RUNNINGHUB_API_KEY")
        print("   方法3: 在 config/.env 文件中配置")
        return
    
    api = RunningHubAPI(api_key=api_key, api_secret=api_secret)
    prompt_manager = PromptManager()
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("🚀 开始批量生成")
    print("=" * 60)
    print(f"角色数量: {len(characters)}")
    print(f"场景数量: {len(scenes)}")
    print(f"输出目录: {output_dir}")
    print(f"图片尺寸: {width}x{height}")
    print(f"生成步数: {steps}")
    print(f"CFG缩放: {cfg_scale}")
    print(f"批次大小: {batch_size}")
    print(f"放大: {'是' if upscale else '否'}")
    print(f"质量检查: {'是' if quality_check else '否'}")
    print("=" * 60)
    
    # 批量生成角色
    character_results = []
    if characters:
        character_results = batch_generate_characters(
            api, prompt_manager, characters, output_dir,
            width=width, height=height, steps=steps, cfg_scale=cfg_scale,
            batch_size=batch_size, upscale=upscale, quality_check=quality_check
        )
    
    # 批量生成场景
    scene_results = []
    if scenes:
        scene_results = batch_generate_scenes(
            api, prompt_manager, scenes, output_dir,
            width=width, height=height, steps=steps, cfg_scale=cfg_scale,
            batch_size=batch_size, upscale=upscale, quality_check=quality_check
        )
    
    # 统计结果
    print("\n" + "=" * 60)
    print("📊 生成统计")
    print("=" * 60)
    
    if character_results:
        char_success = sum(1 for r in character_results if r['status'] == 'success')
        char_failed = sum(1 for r in character_results if r['status'] == 'failed')
        print(f"\n角色生成:")
        print(f"  成功: {char_success}")
        print(f"  失败: {char_failed}")
    
    if scene_results:
        scene_success = sum(1 for r in scene_results if r['status'] == 'success')
        scene_failed = sum(1 for r in scene_results if r['status'] == 'failed')
        print(f"\n场景生成:")
        print(f"  成功: {scene_success}")
        print(f"  失败: {scene_failed}")
    
    # 保存结果
    all_results = {
        'characters': character_results,
        'scenes': scene_results
    }
    
    result_file = output_path / 'batch_results.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存: {result_file}")
    print("\n🎉 批量生成完成！")


if __name__ == '__main__':
    main()
