#!/usr/bin/env python3
"""
PromptManager 交互式演示
展示如何使用 PromptManager 管理提示词库
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 切换工作目录到项目根目录
os.chdir(project_root)

print("📝 PromptManager 交互式演示")
print("=" * 70)
print()

# 导入 PromptManager
try:
    from modules.prompt_manager import PromptManager
    
    # 初始化 PromptManager (会自动加载 config/prompt_library.json)
    pm = PromptManager()
    print("✅ PromptManager 初始化成功")
    print(f"   提示词库路径: {pm.library_path}")
    print()
    
except Exception as e:
    print(f"❌ 导入 PromptManager 失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ===========================================================
# 功能演示
# ===========================================================

print("=" * 70)
print()

# 1. 列出所有提示词
print("📚 1. 列出所有提示词")
print("-" * 70)

all_prompts = pm.list_prompts()
print(f"角色提示词 (characters): {len(all_prompts['characters'])} 个")
for name in all_prompts['characters']:
    print(f"   - {name}")

print(f"\n场景提示词 (scenes): {len(all_prompts['scenes'])} 个")
for name in all_prompts['scenes']:
    print(f"   - {name}")

print(f"\n道具提示词 (props): {len(all_prompts['props'])} 个")
for name in all_prompts['props']:
    print(f"   - {name}")

total = len(all_prompts['characters']) + len(all_prompts['scenes']) + len(all_prompts['props'])
print(f"\n总计: {total} 个")
print()

# 2. 获取并显示角色提示词
print("👤 2. 获取角色提示词")
print("-" * 70)

result = pm.get_prompt('characters', 'Bella')
if result:
    print(f"✅ 找到角色 'Bella':")
    print(f"   正面提示词 (前200字符):")
    print(f"   {result['positive'][:200]}...")
    print(f"\n   负面提示词 (前100字符):")
    print(f"   {result['negative'][:100]}...")
    if result.get('seed'):
        print(f"\n   种子值: {result['seed']}")
    print()

# 获取 Luca 的提示词
result = pm.get_prompt('characters', 'Luca')
if result:
    print(f"✅ 找到角色 'Luca':")
    print(f"   正面提示词 (前200字符):")
    print(f"   {result['positive'][:200]}...")
    print()

# 3. 获取场景提示词
print("🏥 3. 获取场景提示词")
print("-" * 70)

result = pm.get_prompt('scenes', 'Hospital_Corridor')
if result:
    print(f"✅ 找到场景 'Hospital_Corridor':")
    print(f"   正面提示词 (前200字符):")
    print(f"   {result['positive'][:200]}...")
    print()

# 4. 搜索提示词
print("🔍 4. 搜索提示词")
print("-" * 70)

keywords = ['beautiful', 'hospital', 'elegant', 'party']

for keyword in keywords:
    results = pm.search_prompts(keyword)
    if results:
        print(f"✅ 搜索 '{keyword}': 找到 {len(results)} 个结果")
        for r in results[:2]:  # 只显示前2个
            print(f"   - [{r['category']}] {r['name']}")
    else:
        print(f"⚠️  搜索 '{keyword}': 未找到结果")
print()

# 5. 查看提示词库的原始结构
print("📋 5. 查看提示词库的原始结构")
print("-" * 70)

print("提示词库包含以下类别:")
for category in ['characters', 'scenes', 'props', 'negative_prompts']:
    if category in pm.library:
        if category == 'negative_prompts':
            print(f"   - {category}: {len(pm.library[category])} 个类型")
        else:
            print(f"   - {category}: {len(pm.library[category])} 个")

print()

# 6. 显示某个角色的完整提示词
print("📄 6. 显示 'Bella' 的完整提示词")
print("-" * 70)

if 'Bella' in pm.library.get('characters', {}):
    bella_data = pm.library['characters']['Bella']
    print(f"角色: Bella")
    print(f"正面提示词 (完整):")
    print(f"  {bella_data.get('positive', '')}")
    print(f"\n负面提示词:")
    print(f"  {bella_data.get('negative', '')}")
    if 'seed' in bella_data:
        print(f"\n种子值: {bella_data['seed']}")
    print()

# 7. 演示搜索功能（更详细的输出）
print("🔎 7. 详细搜索演示")
print("-" * 70)

search_term = 'hospital'
print(f"搜索关键词: '{search_term}'")
results = pm.search_prompts(search_term)
if results:
    print(f"找到 {len(results)} 个匹配结果:\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. 类别: {r['category']}")
        print(f"   名称: {r['name']}")
        # 显示匹配的提示词内容（前100字符）
        prompt_result = pm.get_prompt(r['category'], r['name'])
        if prompt_result:
            content = prompt_result['positive']
            print(f"   匹配内容: {content[:100]}...")
        print()

# 8. 显示配置文件路径
print("📁 8. 配置文件信息")
print("-" * 70)

print(f"提示词库文件路径:")
print(f"  {pm.library_path}")
print()
print(f"文件是否存在: {os.path.exists(pm.library_path)}")
if os.path.exists(pm.library_path):
    size_kb = os.path.getsize(pm.library_path) / 1024
    print(f"文件大小: {size_kb:.2f} KB")
print()

# 9. 显示如何使用提示词（实际使用示例）
print("💡 9. 实际使用提示词示例")
print("-" * 70)

print("示例1: 为角色 Bella 生成图像提示词")
print("   positive = pm.get_prompt('characters', 'Bella')")
print("   print(positive['positive'])  # 用于 RunningHub/Midjourney")
print("   print(positive['negative'])  # 作为负面提示词")
print()

print("示例2: 为场景 Hospital_Corridor 生成视频提示词")
print("   scene = pm.get_prompt('scenes', 'Hospital_Corridor')")
print("   print(scene['positive'])  # 用于 Runway/Pika")
print()

print("示例3: 搜索包含 'elegant' 的所有提示词")
print("   results = pm.search_prompts('elegant')")
print("   for r in results:")
print("       print(f\"{r['category']}/{r['name']}\")")
print()

# 10. 总结
print("=" * 70)
print()
print("🎉 PromptManager 演示完成！")
print()
print("💡 接下来您可以:")
print("   1. 编辑提示词库: nano config/prompt_library.json")
print("   2. 运行其他示例: python examples/example4_prompt_management.py")
print("   3. 使用命令行工具: python scripts/generate_character.py --help")
print("   4. 查看完整文档: open docs/USER_GUIDE.md")
print()
print("=" * 70)
