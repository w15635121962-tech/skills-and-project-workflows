#!/usr/bin/env python3
"""
示例1: 生成单个角色
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.runninghub_api import RunningHubAPI
from modules.prompt_manager import PromptManager
from workflows.character_generation import CharacterGenerationWorkflow


def main():
    print("🎨 示例1: 生成单个角色")
    print("=" * 60)
    
    # 初始化
    api = RunningHubAPI()  # 从 .env 读取 API Key
    prompt_manager = PromptManager()
    
    # 创建角色生成工作流
    workflow = CharacterGenerationWorkflow(api, prompt_manager)
    
    # 生成角色
    result = workflow.generate_character(
        character_name='Bella',
        prompt_variant='elegant blue dress, pearl necklace',
        views=['front', 'side'],
        expressions=['neutral', 'smile'],
        output_dir='outputs/characters',
        width=512,
        height=768,
        steps=30,
        cfg_scale=7.5,
        upscale=True,
        quality_check=True
    )
    
    print(f"\n✅ 完成! 生成了 {len(result['files'])} 个文件")
    print(f"   文件: {result['files']}")


if __name__ == '__main__':
    main()
