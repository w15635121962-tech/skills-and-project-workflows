#!/usr/bin/env python3
"""
示例7: 视频生成 (需要配置 Runway/Pika API)
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# 注意: 需要先配置 Runway 或 Pika API Key
# 编辑 config/.env 文件，填入 RUNWAY_API_KEY 或 PIKA_API_KEY


def main():
    print("🎬 示例7: 视频生成")
    print("=" * 60)
    
    # 检查 API Key 是否配置
    runway_key = os.getenv('RUNWAY_API_KEY')
    pika_key = os.getenv('PIKA_API_KEY')
    
    if not runway_key and not pika_key:
        print("\n⚠️  错误: 未配置 Runway 或 Pika API Key")
        print("   请编辑 config/.env 文件，填入以下其中一个:")
        print("      RUNWAY_API_KEY=your_key_here")
        print("      PIKA_API_KEY=your_key_here")
        print("\n   参考文档: docs/USER_GUIDE.md")
        return
    
    # 初始化 API
    from core.runninghub_api import RunningHubAPI
    from modules.prompt_manager import PromptManager
    
    prompt_manager = PromptManager()
    
    # 初始化视频生成 API
    if runway_key:
        print("\n🎥 使用 Runway Gen-3 API")
        from core.runway_api import RunwayAPI
        video_api = RunwayAPI(api_key=runway_key)
        api_name = 'Runway'
    else:
        print("\n🎥 使用 Pika 2.0 API")
        from core.pika_api import PikaAPI
        video_api = PikaAPI(api_key=pika_key)
        api_name = 'Pika'
    
    # 示例1: 文本生成视频
    print(f"\n1. 文本生成视频 (使用 {api_name})")
    print("   " + "=" * 56)
    
    prompt = "medium shot, Bella walking in hospital corridor, natural gait, cinematic lighting"
    print(f"   提示词: {prompt[:80]}...")
    
    try:
        # 注意: 这是示例代码，实际使用时需要有效的 API Key
        # result = video_api.text_to_video(
        #     prompt=prompt,
        #     duration=5,
        #     aspect_ratio='16:9'
        # )
        # print(f"   ✅ 视频已保存: {result['video_path']}")
        print("   ⚠️  示例代码 - 需要有效的 API Key 才能实际生成视频")
    except Exception as e:
        print(f"   ❌ 生成失败: {e}")
    
    # 示例2: 图片生成视频
    print(f"\n2. 图片生成视频 (使用 {api_name})")
    print("   " + "=" * 56)
    
    image_path = 'outputs/characters/Bella/front_neutral.png'
    if not Path(image_path).exists():
        print(f"   ⚠️  图片不存在: {image_path}")
        print("   请先运行 example1_generate_character.py 生成测试图像")
    else:
        prompt = "character blinking, subtle smile"
        print(f"   图片: {image_path}")
        print(f"   提示词: {prompt}")
        
        try:
            # result = video_api.image_to_video(
            #     image_path=image_path,
            #     prompt=prompt,
            #     duration=5
            # )
            # print(f"   ✅ 视频已保存: {result['video_path']}")
            print("   ⚠️  示例代码 - 需要有效的 API Key 才能实际生成视频")
        except Exception as e:
            print(f"   ❌ 生成失败: {e}")
    
    # 示例3: 使用视频生成工作流
    print(f"\n3. 使用视频生成工作流 (使用 {api_name})")
    print("   " + "=" * 56)
    
    try:
        from workflows.video_generation import VideoGenerationWorkflow
        
        workflow = VideoGenerationWorkflow(
            runway_api=video_api if runway_key else None,
            pika_api=video_api if pika_key else None,
            prompt_manager=prompt_manager
        )
        
        # result = workflow.generate_video_from_text(
        #     prompt='medium shot, Bella walking in hospital corridor',
        #     output_dir='outputs/videos',
        #     duration=5
        # )
        # print(f"   ✅ 视频已保存: {result['video_path']}")
        print("   ⚠️  示例代码 - 需要有效的 API Key 才能实际生成视频")
    except Exception as e:
        print(f"   ❌ 初始化失败: {e}")
    
    print("\n✅ 视频生成示例完成 (需要有效 API Key 才能实际运行)")


if __name__ == '__main__':
    main()
