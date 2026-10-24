#!/usr/bin/env python3
"""
示例3: 批量生成角色和场景
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.runninghub_api import RunningHubAPI
from modules.prompt_manager import PromptManager
from workflows.character_generation import CharacterGenerationWorkflow
from workflows.scene_generation import SceneGenerationWorkflow


def main():
    print("🚀 示例3: 批量生成角色和场景")
    print("=" * 60)
    
    # 初始化
    api = RunningHubAPI()
    prompt_manager = PromptManager()
    
    # 创建角色生成工作流
    char_workflow = CharacterGenerationWorkflow(api, prompt_manager)
    
    # 批量生成角色
    characters_config = [
        {
            'name': 'Bella',
            'prompt_variant': 'elegant blue dress, pearl necklace',
            'views': ['front', 'side'],
            'expressions': ['neutral', 'smile']
        },
        {
            'name': 'Luca',
            'prompt_variant': 'black suit, gold watch',
            'views': ['front', 'side'],
            'expressions': ['neutral', 'smile']
        }
    ]
    
    print("\n👤 批量生成角色...")
    char_results = char_workflow.batch_generate_characters(
        character_configs=characters_config,
        output_dir='outputs/characters'
    )
    
    # 创建场景生成工作流
    scene_workflow = SceneGenerationWorkflow(api, prompt_manager)
    
    # 批量生成场景
    scenes_config = [
        {
            'name': 'Hospital_Corridor',
            'prompt_variant': 'morning sunlight, empty',
            'variations': 2
        },
        {
            'name': 'Party_Venue',
            'prompt_variant': 'warm lighting, romantic',
            'variations': 2
        }
    ]
    
    print("\n🏞️  批量生成场景...")
    scene_results = scene_workflow.batch_generate_scenes(
        scene_configs=scenes_config,
        output_dir='outputs/scenes'
    )
    
    # 统计
    total_char = sum(r['generated'] for r in char_results)
    total_scene = sum(r['generated'] for r in scene_results)
    
    print(f"\n✅ 完成! 生成了 {total_char} 个角色文件, {total_scene} 个场景文件")


if __name__ == '__main__':
    main()
