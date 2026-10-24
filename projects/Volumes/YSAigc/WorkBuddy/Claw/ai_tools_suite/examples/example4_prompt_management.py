#!/usr/bin/env python3
"""
示例4: 提示词管理
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.prompt_manager import PromptManager


def main():
    print("📝 示例4: 提示词管理")
    print("=" * 60)
    
    # 初始化提示词管理器
    pm = PromptManager()
    
    # 1. 渲染角色提示词
    print("\n1. 渲染角色提示词:")
    prompt = pm.render_character_prompt(
        character_name='Bella',
        variant='elegant blue dress, pearl necklace',
        view='front',
        expression='smile'
    )
    print(f"   提示词: {prompt[:150]}...")
    
    # 2. 渲染场景提示词
    print("\n2. 渲染场景提示词:")
    prompt = pm.render_scene_prompt(
        scene_name='Hospital_Corridor',
        variant='morning sunlight, empty',
        lighting='morning',
        atmosphere='peaceful'
    )
    print(f"   提示词: {prompt[:150]}...")
    
    # 3. 获取负面提示词
    print("\n3. 获取负面提示词:")
    negative = pm.get_negative_prompt('character')
    print(f"   角色负面: {negative[:100]}...")
    
    negative = pm.get_negative_prompt('scene')
    print(f"   场景负面: {negative[:100]}...")
    
    # 4. 添加角色变体
    print("\n4. 添加角色变体:")
    pm.add_character_variant(
        character_name='Bella',
        variant_name='party',
        variant_prompt='golden gown, diamond crown, elegant updo'
    )
    print("   ✅ 已添加变体: party")
    
    # 5. 搜索提示词
    print("\n5. 搜索提示词:")
    results = pm.search_prompts('elegant', category='characters')
    print(f"   搜索结果: {len(results)} 个")
    
    # 6. 导出提示词库
    print("\n6. 导出提示词库:")
    pm.export_library('outputs/prompt_library_backup.json')
    print("   ✅ 已导出到 outputs/prompt_library_backup.json")
    
    print("\n✅ 提示词管理示例完成!")


if __name__ == '__main__':
    main()
