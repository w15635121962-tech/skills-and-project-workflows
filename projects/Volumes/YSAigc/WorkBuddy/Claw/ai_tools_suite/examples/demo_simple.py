#!/usr/bin/env python3
"""
AI工具套件 - 简化演示
只演示确定能工作的功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

print("🎬 AI工具套件 - 简化演示")
print("=" * 70)
print()

# ============================================================
# 1. 测试 PromptManager (提示词管理)
# ============================================================
print("📝 1. 测试 PromptManager (提示词管理)")
print("-" * 70)

try:
    from modules.prompt_manager import PromptManager
    
    # 创建提示词管理器
    pm = PromptManager()
    
    # 列出所有提示词
    prompts = pm.list_prompts()
    print(f"✅ 提示词库统计:")
    print(f"   角色: {prompts['characters']} 个")
    print(f"   场景: {prompts['scenes']} 个")
    print(f"   道具: {prompts['props']} 个")
    
    # 搜索提示词
    results = pm.search_prompts('Bella')
    print(f"✅ 搜索 'Bella': 找到 {len(results)} 个结果")
    
    print("✅ PromptManager 测试通过!")
    
except Exception as e:
    print(f"❌ PromptManager 测试失败: {e}")

print()
print("=" * 70)
print()

# ============================================================
# 2. 测试 AssetOrganizer (资产整理)
# ============================================================
print("📁 2. 测试 AssetOrganizer (资产整理)")
print("-" * 70)

try:
    from modules.asset_organizer import AssetOrganizer
    
    # 创建资产整理器
    output_dir = project_root / 'outputs' / 'organized'
    organizer = AssetOrganizer(str(output_dir))
    
    print(f"✅ AssetOrganizer 初始化成功")
    print(f"   输出目录: {output_dir}")
    print(f"   支持的扩展名: {list(organizer.extensions.keys())}")
    
    print("✅ AssetOrganizer 测试通过!")
    
except Exception as e:
    print(f"❌ AssetOrganizer 测试失败: {e}")

print()
print("=" * 70)
print()

# ============================================================
# 3. 查看文件结构
# ============================================================
print("📂 3. 查看项目结构")
print("-" * 70)

def count_files(directory):
    """统计目录中的文件数"""
    count = 0
    for root, dirs, files in os.walk(directory):
        count += len(files)
    return count

# 统计各目录
dirs_to_check = [
    'core',
    'modules',
    'workflows',
    'scripts',
    'config',
    'templates',
    'docs',
    'examples'
]

print(f"✅ 项目文件统计:")
total_files = 0
for dir_name in dirs_to_check:
    dir_path = project_root / dir_name
    if dir_path.exists():
        file_count = count_files(str(dir_path))
        total_files += file_count
        print(f"   {dir_name}/: {file_count} 个文件")

print(f"   总计: {total_files} 个文件")

print()
print("=" * 70)
print()

# ============================================================
# 4. 显示使用建议
# ============================================================
print("📊 使用建议")
print("=" * 70)
print()

print("✅ 可以立即使用的功能 (无需API Key):")
print("   1. PromptManager - 管理提示词库")
print("      - 查看: pm = PromptManager()")
print("      - 列出: pm.list_prompts()")
print("      - 搜索: pm.search_prompts('Bella')")
print("      - 获取: pm.get_prompt('characters', 'Bella')")
print()
print("   2. AssetOrganizer - 整理生成的资产")
print("      - 整理: organizer.organize(input_dir, output_dir)")
print("      - 分析: organizer.analyze_directory(dir)")
print()

print("⚠️  需要API Key的功能:")
print("   1. RunningHubAPI - 生成图像 (需要 RUNNINGHUB_API_KEY)")
print("   2. RunwayAPI - 生成视频 (需要 RUNWAY_API_KEY)")
print("   3. PikaAPI - 生成视频 (需要 PIKA_API_KEY)")
print("   4. QualityChecker - 质量检查 (需要安装numpy/opencv)")
print()

print("📝 下一步建议:")
print("   1. 阅读快速开始指南: docs/QUICKSTART.md")
print("   2. 阅读详细使用指南: docs/USER_GUIDE.md")
print("   3. 配置API Key: cp config/.env.example config/.env")
print("   4. 查看示例脚本: examples/ 目录")
print()

print("=" * 70)
print()
print("🎉 演示完成！")
print()
print("💡 提示:")
print("   - 即使没有API Key，您也可以用PromptManager准备好提示词")
print("   - 所有模块的源代码都已创建，可以根据需要修改")
print("   - 查看各模块的docstring了解详细用法")
print()
