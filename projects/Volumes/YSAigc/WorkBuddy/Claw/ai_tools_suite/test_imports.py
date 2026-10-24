#!/usr/bin/env python3
"""
测试AI工具套件的模块导入
"""
import sys
import traceback
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("🧪 测试AI工具套件模块导入")
print("=" * 60)

# 测试核心模块
print("\n📦 测试核心模块 (core/)...")
core_modules = [
    'core.runninghub_api',
    'core.midjourney_bot',
    'core.runway_api',
    'core.pika_api',
]

for module in core_modules:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except Exception as e:
        print(f"  ❌ {module}: {e}")
        traceback.print_exc()

# 测试功能模块
print("\n🔧 测试功能模块 (modules/)...")
module_modules = [
    'modules.prompt_manager',
    'modules.batch_generator',
    'modules.asset_organizer',
    'modules.quality_checker',
]

for module in module_modules:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except Exception as e:
        print(f"  ❌ {module}: {e}")
        traceback.print_exc()

# 测试工作流模块
print("\n🔄 测试工作流模块 (workflows/)...")
workflow_modules = [
    'workflows.character_generation',
    'workflows.scene_generation',
    'workflows.video_generation',
]

for module in workflow_modules:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except Exception as e:
        print(f"  ❌ {module}: {e}")
        traceback.print_exc()

# 测试脚本
print("\n📜 测试命令行脚本 (scripts/)...")

scripts = [
    'scripts.generate_character',
    'scripts.generate_scene',
    'scripts.batch_process',
    'scripts.oragnize_assets',
]

for script in scripts:
    try:
        __import__(script)
        print(f"  ✅ {script}")
    except Exception as e:
        print(f"  ❌ {script}: {e}")
        traceback.print_exc()

print("\n" + "=" * 60)
print("🎉 模块导入测试完成！")
print("=" * 60)

# 尝试导入主要类
print("\n🔍 测试主要类导入...")

try:
    from core.runninghub_api import RunningHubAPI
    print("  ✅ RunningHubAPI")
except Exception as e:
    print(f"  ❌ RunningHubAPI: {e}")

try:
    from modules.prompt_manager import PromptManager
    print("  ✅ PromptManager")
except Exception as e:
    print(f"  ❌ PromptManager: {e}")

try:
    from modules.batch_generator import BatchGenerator
    print("  ✅ BatchGenerator")
except Exception as e:
    print(f"  ❌ BatchGenerator: {e}")

try:
    from modules.asset_organizer import AssetOrganizer
    print("  ✅ AssetOrganizer")
except Exception as e:
    print(f"  ❌ AssetOrganizer: {e}")

try:
    from modules.quality_checker import QualityChecker
    print("  ✅ QualityChecker")
except Exception as e:
    print(f"  ❌ QualityChecker: {e}")

try:
    from workflows.character_generation import CharacterGenerationWorkflow
    print("  ✅ CharacterGenerationWorkflow")
except Exception as e:
    print(f"  ❌ CharacterGenerationWorkflow: {e}")

try:
    from workflows.scene_generation import SceneGenerationWorkflow
    print("  ✅ SceneGenerationWorkflow")
except Exception as e:
    print(f"  ❌ SceneGenerationWorkflow: {e}")

try:
    from workflows.video_generation import VideoGenerationWorkflow
    print("  ✅ VideoGenerationWorkflow")
except Exception as e:
    print(f"  ❌ VideoGenerationWorkflow: {e}")

print("\n" + "=" * 60)
print("✅ 测试完成！")
print("\n如果有模块导入失败，请检查:")
print("  1. 依赖是否安装: pip install -r requirements.txt")
print("  2. Python版本是否 >= 3.8")
print("  3. 模块文件是否有语法错误")
print("=" * 60)
