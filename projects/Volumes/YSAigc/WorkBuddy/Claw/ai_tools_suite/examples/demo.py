#!/usr/bin/env python3
"""
AI工具套件 - 演示脚本
展示如何使用各个模块 (不依赖discord.py)
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径 - 修复导入问题
project_root = Path(__file__).parent.parent  # examples/的上一级是项目根目录
sys.path.insert(0, str(project_root))

# 切换工作目录到项目根目录 (修复相对路径问题)
os.chdir(project_root)

print("🎬 AI工具套件 - 功能演示")
print("=" * 70)
print(f"项目根目录: {project_root}")
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
    
    # 获取角色提示词
    result = pm.get_prompt('characters', 'Bella')
    if result:
        prompt_template = result['base']
        print(f"✅ 获取角色提示词模板 (前100字符):")
        print(f"   {prompt_template[:100]}...")
        
        # 获取场景提示词
        result = pm.get_prompt('scenes', 'Hospital_Corridor')
        if result:
            prompt_template = result['base']
            print(f"✅ 获取场景提示词模板 (前100字符):")
            print(f"   {prompt_template[:100]}...")
    
    # 获取负面提示词
    negative = pm.generate_negative_prompt('character')
    print(f"✅ 生成负面提示词 (前80字符):")
    print(f"   {negative[:80]}...")
    
    # 列出所有提示词
    prompts = pm.list_prompts()
    print(f"✅ 提示词库统计:")
    print(f"   角色: {prompts['characters']} 个")
    print(f"   场景: {prompts['scenes']} 个")
    print(f"   道具: {prompts['props']} 个")
    
    print("✅ PromptManager 测试通过!")
    
except Exception as e:
    print(f"❌ PromptManager 测试失败: {e}")
    import traceback
    traceback.print_exc()

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
    
    # 创建测试目录和文件
    test_dir = project_root / 'outputs' / 'test_demo'
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建一些测试文件
    (test_dir / 'character_Bella.png').write_text('test')
    (test_dir / 'scene_Hospital.jpg').write_text('test')
    (test_dir / 'video_clip.mp4').write_text('test')
    
    print(f"✅ 创建测试文件:")
    print(f"   {test_dir / 'character_Bella.png'}")
    print(f"   {test_dir / 'scene_Hospital.jpg'}")
    print(f"   {test_dir / 'video_clip.mp4'}")
    
    # 整理资产 (干运行模式)
    print(f"✅ 整理资产 (复制模式):")
    result = organizer.organize(
        input_dir=str(test_dir),
        output_dir=str(output_dir),
        copy_mode=True,
        dry_run=True  # 干运行，不实际复制
    )
    
    print(f"   计划复制 {result['total']} 个文件")
    print(f"   分类: {result['categorized']}")
    print(f"   跳过: {result['skipped']}")
    
    print("✅ AssetOrganizer 测试通过!")
    
except Exception as e:
    print(f"❌ AssetOrganizer 测试失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print()

# ============================================================
# 3. 测试 QualityChecker (质量检查) - 需要 numpy/opencv
# ============================================================
print("🔍 3. 测试 QualityChecker (质量检查)")
print("-" * 70)

try:
    from modules.quality_checker import QualityChecker
    
    checker = QualityChecker()
    print(f"✅ QualityChecker 初始化成功")
    print(f"   面部检测可用: {checker.face_cascade is not None}")
    print(f"   手部检测可用: {checker.hand_cascade is not None}")
    
    print("✅ QualityChecker 测试通过!")
    
except ImportError as e:
    print(f"⚠️  QualityChecker 导入失败 (缺少依赖): {e}")
    print(f"   请运行: pip install numpy opencv-python-headless")
    
except Exception as e:
    print(f"❌ QualityChecker 测试失败: {e}")

print()
print("=" * 70)
print()

# ============================================================
# 4. 演示 RunningHubAPI (需要API Key)
# ============================================================
print("🎨 4. 演示 RunningHubAPI (需要API Key)")
print("-" * 70)

try:
    from core.runninghub_api import RunningHubAPI
    
    # 检查是否有API Key
    api_key = os.getenv('RUNNINGHUB_API_KEY')
    
    if api_key:
        print(f"✅ 找到 API Key (前10字符): {api_key[:10]}...")
        
        # 创建API客户端
        api = RunningHubAPI(api_key=api_key)
        print(f"✅ RunningHubAPI 初始化成功")
        
        # 注意: 实际调用API需要网络连接和有效的API Key
        print(f"   (实际生成需要调用API，这里只演示初始化)")
        
    else:
        print(f"⚠️  未找到 RUNNINGHUB_API_KEY 环境变量")
        print(f"   请在 config/.env 中配置，或设置环境变量")
        print(f"   演示模式: 只测试导入，不实际调用API")
        
        # 演示类的结构
        print(f"✅ RunningHubAPI 类可以导入")
        print(f"   主要方法:")
        print(f"     - text_to_image()  # 文本生成图片")
        print(f"     - image_to_image()  # 图生图")
        print(f"     - inpaint_image()  # 局部重绘")
        print(f"     - upscale_image()  # 放大图片")
    
    print("✅ RunningHubAPI 测试通过!")
    
except Exception as e:
    print(f"❌ RunningHubAPI 测试失败: {e}")

print()
print("=" * 70)
print()

# ============================================================
# 5. 演示工作流 (需要API Key)
# ============================================================
print("🔄 5. 演示工作流 (需要API Key)")
print("-" * 70)

try:
    # 只测试导入，不实际运行
    from workflows.character_generation import CharacterGenerationWorkflow
    from workflows.scene_generation import SceneGenerationWorkflow
    
    print(f"✅ CharacterGenerationWorkflow 可以导入")
    print(f"✅ SceneGenerationWorkflow 可以导入")
    
    print(f"   主要工作流:")
    print(f"     - generate_character()  # 生成角色 (多视角、多表情)")
    print(f"     - generate_scene()  # 生成场景 (多变化)")
    print(f"     - batch_generate_characters()  # 批量生成角色")
    print(f"     - batch_generate_scenes()  # 批量生成场景")
    
    print(f"")
    print(f"   ⚠️  实际运行需要:")
    print(f"     1. 配置 RUNNINGHUB_API_KEY")
    print(f"     2. 可选: 安装 numpy/opencv 用于质量检查")
    
    print("✅ 工作流模块测试通过!")
    
except Exception as e:
    print(f"❌ 工作流模块测试失败: {e}")

print()
print("=" * 70)
print()

# ============================================================
# 总结
# ============================================================
print("📊 演示总结")
print("=" * 70)
print()
print("✅ 可以使用的模块 (无需API Key):")
print("   1. PromptManager - 提示词管理")
print("   2. AssetOrganizer - 资产整理")
print("   3. QualityChecker - 质量检查 (需要安装numpy/opencv)")
print()
print("⚠️  需要API Key的模块:")
print("   1. RunningHubAPI - RunningHub API客户端")
print("   2. MidjourneyBot - Midjourney Bot (需要discord.py)")
print("   3. RunwayAPI - Runway API客户端")
print("   4. PikaAPI - Pika API客户端")
print("   5. 工作流模块 - 需要上述API客户端")
print()
print("📝 下一步:")
print("   1. 配置API Key: cp config/.env.example config/.env")
print("   2. 编辑 config/.env 填入您的API Key")
print("   3. 运行示例: python examples/example1_generate_character.py")
print("   4. 阅读文档: docs/QUICKSTART.md")
print()
print("=" * 70)
print()
print("🎉 演示完成！")
print()
print("💡 提示:")
print("   - 即使没有API Key，您也可以使用PromptManager管理提示词")
print("   - 您可以先准备好提示词库，等API Key配置好后再生成")
print("   - 查看 examples/ 目录下的示例脚本学习使用方法")
print()
