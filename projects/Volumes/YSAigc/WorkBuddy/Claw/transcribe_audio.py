#!/usr/bin/env python3.14
"""
使用Whisper识别预告片中的台词
"""
import os
import sys
import ssl
import shutil

# 禁用SSL验证（仅用于下载模型）
ssl._create_default_https_context = ssl._create_unverified_context

import whisper
import json

def find_ffmpeg():
    """查找可用的ffmpeg路径"""
    # 检查imageio_ffmpeg（moviepy自带的）
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.exists(ffmpeg_path):
            print(f"找到imageio_ffmpeg: {ffmpeg_path}")
            return ffmpeg_path
    except:
        pass
    
    # 检查系统PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print(f"找到系统ffmpeg: {ffmpeg_path}")
        return ffmpeg_path
    
    # 常见路径
    common_paths = [
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/usr/bin/ffmpeg",
    ]
    for path in common_paths:
        if os.path.exists(path):
            print(f"找到ffmpeg: {path}")
            return path
    
    return None

def setup_ffmpeg():
    """设置ffmpeg路径"""
    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path:
        os.environ["PATH"] = os.path.dirname(ffmpeg_path) + os.pathsep + os.environ.get("PATH", "")
        # 也设置FFMPEG_BINARY环境变量
        os.environ["FFMPEG_BINARY"] = ffmpeg_path
        return True
    return False

def transcribe_audio(audio_path, output_path):
    """使用Whisper识别音频中的台词"""
    print(f"正在加载Whisper模型...")
    
    # 使用tiny模型（速度快，适合快速分析）
    model = whisper.load_model("tiny")
    
    print(f"正在识别音频: {audio_path}")
    print(f"这可能需要几分钟，请耐心等待...")
    
    # 识别音频
    result = model.transcribe(
        audio_path,
        language="en",  # 假设是英文
        verbose=True,
        fp16=False  # CPU运行
    )
    
    # 保存完整结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 识别结果已保存到: {output_path}")
    
    # 打印识别到的文本
    print("\n" + "="*60)
    print("识别到的台词内容")
    print("="*60)
    
    full_text = result.get("text", "").strip()
    if full_text:
        print(f"\n完整文本:\n{full_text}")
    else:
        print("\n未识别到明显台词（可能是纯音乐或背景音乐）")
    
    # 打印带时间戳的片段
    segments = result.get("segments", [])
    if segments:
        print(f"\n共识别到 {len(segments)} 个语音片段:")
        print("-" * 60)
        for seg in segments:
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            text = seg.get("text", "").strip()
            if text:
                print(f"[{start:>6.2f}s - {end:>6.2f}s] {text}")
    
    print("="*60)
    
    return result

if __name__ == "__main__":
    # 设置ffmpeg
    if not setup_ffmpeg():
        print("警告: 未找到ffmpeg，尝试继续...")
    
    audio_path = "/Users/xiazhi/WorkBuddy/Claw/preview-audio.m4a"
    output_path = "/Users/xiazhi/WorkBuddy/Claw/transcription.json"
    
    if not os.path.exists(audio_path):
        print(f"错误: 音频文件不存在: {audio_path}")
        sys.exit(1)
    
    result = transcribe_audio(audio_path, output_path)
