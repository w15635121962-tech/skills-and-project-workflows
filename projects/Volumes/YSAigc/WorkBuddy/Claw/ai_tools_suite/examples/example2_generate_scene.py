#!/usr/bin/env python3
"""
示例2: 生成单个场景
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.runninghub_api import RunningHubAPI
from modules.prompt_manager import PromptManager
from workflows.scene_generation import SceneGenerationWorkflow


def main():
    print("🏞️  示例2: 生成单个场景")
    print("=" * 60)
    
    # 初始化
    api = RunningHubAPI()
    prompt_manager = PromptManager()
    
    # 创建场景生成工作流
    workflow = SceneGenerationWorkflow(api, prompt_manager)
    
    # 生成场景
    result = workflow.generate_scene(
        scene_name='Hospital_Corridor',
        prompt_variant='morning sunlight, empty',
        variations=3,
        output_dir='outputs/scenes',
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
