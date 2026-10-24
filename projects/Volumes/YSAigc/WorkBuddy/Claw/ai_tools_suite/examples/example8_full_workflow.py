"""
示例8：完整工作流 - 从剧本到生成资产
模拟一个完整的 AI 真人剧制作流程
"""
import os
import sys
import json
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.prompt_manager import PromptManager


def print_section(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def step1_init_prompt_manager():
    print_section("步骤 1：初始化提示词管理器")
    
    pm = PromptManager()
    print(f"已加载提示词库")
    
    # 列出所有可用角色
    prompts = pm.list_prompts(category="characters")
    if "characters" in prompts:
        print(f"   可用角色：{list(prompts['characters'])}")
    
    return pm


def step2_generate_characters(pm, api_client=None):
    print_section("步骤 2：生成角色资产")
    
    # 获取角色提示词
    characters = ["Bella", "Luca"]
    for char_name in characters:
        try:
            prompt_data = pm.get_prompt("characters", char_name, view="front view", expression="neutral")
            print(f"\n🎨 角色：{char_name}")
            print(f"   正面提示词：{prompt_data['positive'][:80]}...")
            print(f"   负面提示词：{prompt_data['negative'][:60]}...")
            if prompt_data['seed']:
                print(f"   推荐种子：{prompt_data['seed']}")
            
            # 如果有 API 客户端，实际生成
            if api_client:
                print(f"   ⚠️  API 客户端未配置，跳过实际生成")
                # output = api_client.text_to_image(
                #     prompt=prompt_data['positive'],
                #     negative_prompt=prompt_data['negative'],
                #     seed=prompt_data['seed'],
                #     batch_size=4,
                #     output_dir=f"../outputs/characters/{char_name}/"
                # )
                # print(f"   已生成 {len(output)} 张图片")
            else:
                print(f"   （模拟）将生成 4 张图片")
        
        except ValueError as e:
            print(f"   ⚠️  角色 {char_name} 不存在于提示词库中")
    
    return characters


def step3_generate_scenes(pm, api_client=None):
    print_section("步骤 3：生成场景资产")
    
    scenes = ["Hospital_Corridor", "Party_Venue"]
    for scene_name in scenes:
        try:
            prompt_data = pm.get_prompt("scenes", scene_name, time="night")
            print(f"\n🏞️  场景：{scene_name}")
            print(f"   提示词：{prompt_data['positive'][:80]}...")
            
            if api_client:
                print(f"   ⚠️  API 客户端未配置，跳过实际生成")
            else:
                print(f"   （模拟）将生成 4 张图片（day/night 各 2 张）")
        
        except ValueError as e:
            print(f"   ⚠️  场景 {scene_name} 不存在于提示词库中")
    
    return scenes


def step4_assemble_video_prompt(pm):
    print_section("步骤 4：组装视频生成提示词")
    
    # 示例：组装一个完整的视频提示词
    video_prompt = pm.get_video_prompt(
        shot_type="close_up",
        camera_movement="dolly_in",
        action="dialogue",
        style="cinematic",
        motion_intensity="medium",
        audio="music",
        tool="runway_gen3"
    )
    
    print(f"🎬 视频提示词：")
    print(f"   {video_prompt}")
    
    return video_prompt


def step5_validate_all_prompts(pm):
    print_section("步骤 5：验证所有提示词")
    
    categories = ["characters", "scenes", "props"]
    all_valid = True
    
    for category in categories:
        prompts = pm.list_prompts(category=category)
        if category not in prompts:
            continue
        
        for name in prompts[category]:
            result = pm.validate_prompt(category, name)
            status = "✅" if result["valid"] else "❌"
            print(f"   {status} {category}/{name}")
            
            if result["errors"]:
                for err in result["errors"]:
                    print(f"      ⚠️  {err}")
            
            if result["warnings"]:
                for warn in result["warnings"]:
                    print(f"      ⚠️  {warn}")
            
            if not result["valid"]:
                all_valid = False
    
    return all_valid


def step6_export_for_production(pm, output_dir: str = "../outputs/production/"):
    print_section("步骤 6：导出生产用提示词")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 导出角色提示词
    pm.export_prompts(
        output_path=os.path.join(output_dir, "characters_prompts.json"),
        category="characters"
    )
    
    # 导出场景提示词
    pm.export_prompts(
        output_path=os.path.join(output_dir, "scenes_prompts.json"),
        category="scenes"
    )
    
    # 导出视频提示词配置
    video_config = {
        "video_prompt_templates": pm.library.get("video_prompts", {}),
        "negative_prompts": pm.library.get("negative_prompts", {})
    }
    with open(os.path.join(output_dir, "video_config.json"), 'w', encoding='utf-8') as f:
        json.dump(video_config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 生产用提示词已导出到：{output_dir}")
    print(f"   文件：")
    print(f"   - characters_prompts.json")
    print(f"   - scenes_prompts.json")
    print(f"   - video_config.json")


def main():
    print("\n" + "=" * 60)
    print("  AI 工具套件 - 完整工作流示例")
    print("  从剧本到生成资产")
    print("=" * 60)
    
    # 检查配置文件
    env_file = Path(__file__).parent.parent / "config" / ".env"
    if not env_file.exists():
        print(f"\n⚠️  未找到配置文件：{env_file}")
        print(f"   请复制 config/.env.example 到 config/.env 并填写 API 密钥")
        print(f"   当前以模拟模式运行\n")
    
    # 执行工作流
    pm = step1_init_prompt_manager()
    characters = step2_generate_characters(pm, api_client=None)
    scenes = step3_generate_scenes(pm, api_client=None)
    video_prompt = step4_assemble_video_prompt(pm)
    all_valid = step5_validate_all_prompts(pm)
    step6_export_for_production(pm)
    
    # 总结
    print_section("工作流执行完毕")
    print(f"✅ 已处理 {len(characters)} 个角色")
    print(f"✅ 已处理 {len(scenes)} 个场景")
    print(f"✅ 已生成视频提示词模板")
    print(f"✅ 提示词验证：{'全部通过' if all_valid else '存在警告'}")
    print(f"\n💡 下一步：")
    print(f"   1. 在 config/.env 中配置 API 密钥")
    print(f"   2. 运行 python scripts/generate_character.py --name Bella")
    print(f"   3. 查看输出目录：outputs/")


if __name__ == "__main__":
    main()
