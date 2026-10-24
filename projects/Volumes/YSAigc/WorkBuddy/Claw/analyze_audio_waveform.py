#!/usr/bin/env python3.14
"""
分析并可视化预告片的音频波形
识别对话、音乐、静音段
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
from moviepy import VideoFileClip
import os

def visualize_waveform(video_path, output_plot_path):
    """可视化音频波形"""
    print(f"正在读取视频用于波形分析: {video_path}")
    
    video = VideoFileClip(video_path)
    audio = video.audio
    
    if audio is None:
        print("错误: 没有音轨")
        return False
    
    duration = video.duration
    sample_rate = 44100
    
    print(f"正在提取音频数据进行可视化...")
    
    # 提取整个音频为数组
    # 为了性能，每秒取一个样本点
    audio_array = audio.to_soundarray()
    
    # 如果是立体声，转换为单声道
    if len(audio_array.shape) > 1:
        audio_mono = np.mean(audio_array, axis=1)
    else:
        audio_mono = audio_array
    
    # 计算RMS音量（每0.5秒）
    window_size = int(sample_rate * 0.5)  # 0.5秒的窗口
    num_windows = len(audio_mono) // window_size
    
    timestamps = []
    rms_volumes = []
    
    for i in range(num_windows):
        start = i * window_size
        end = (i + 1) * window_size
        segment = audio_mono[start:end]
        rms = np.sqrt(np.mean(segment**2))
        timestamps.append(i * 0.5)
        rms_volumes.append(float(rms))
    
    # 创建可视化图表
    print(f"正在生成波形图...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
    
    # 1. 波形图（采样部分）
    ax1.plot(audio_mono[::sample_rate//10], alpha=0.6, color='#534AB7')
    ax1.set_xlabel('样本点 (每0.1秒)')
    ax1.set_ylabel('振幅')
    ax1.set_title('音频波形 (完整)', fontsize=14, fontweight='500')
    ax1.grid(True, alpha=0.3)
    
    # 2. RMS音量包络线
    time_axis = np.array(timestamps)
    volume_array = np.array(rms_volumes)
    
    ax2.plot(time_axis, volume_array, linewidth=2, color='#1D9E75')
    ax2.fill_between(time_axis, volume_array, alpha=0.3, color='#1D9E75')
    ax2.set_xlabel('时间 (秒)')
    ax2.set_ylabel('RMS音量')
    ax2.set_title('音量包络线 (每0.5秒)', fontsize=14, fontweight='500')
    ax2.grid(True, alpha=0.3)
    
    # 标注关键时间点（基于之前的关键帧）
    key_frames = [
        (0, '开头 (悬念)'),
        (15, '25% (离别)'),
        (30, '50% (医院)'),
        (45, '75% (派对)')
    ]
    
    for t, label in key_frames:
        if t < duration:
            ax2.axvline(x=t, color='#D85A30', linestyle='--', alpha=0.7)
            ax2.text(t, ax2.get_ylim()[1]*0.9, label, rotation=90, fontsize=8)
    
    # 检测可能的对话段（音量在阈值以上且变化较大）
    threshold = np.mean(volume_array) + np.std(volume_array) * 0.5
    dialogue_segments = []
    in_dialogue = False
    dialogue_start = 0
    
    for i, (t, v) in enumerate(zip(time_axis, volume_array)):
        if v > threshold:
            if not in_dialogue:
                dialogue_start = t
                in_dialogue = True
        else:
            if in_dialogue:
                dialogue_segments.append((dialogue_start, t))
                in_dialogue = False
    
    if in_dialogue:
        dialogue_segments.append((dialogue_start, time_axis[-1]))
    
    # 标注可能的对话段
    for start, end in dialogue_segments[:10]:  # 最多标注10段
        ax2.axvspan(start, end, alpha=0.2, color='#D85A30')
    
    plt.tight_layout()
    plt.savefig(output_plot_path, dpi=150, bbox_inches='tight')
    print(f"✅ 波形图已保存到: {output_plot_path}")
    
    # 打印分析报告
    print("\n" + "="*60)
    print("音频分析报告")
    print("="*60)
    
    print(f"\n📊 基本统计:")
    print(f"  总时长: {duration:.2f} 秒")
    print(f"  平均音量: {np.mean(volume_array):.4f}")
    print(f"  最大音量: {np.max(volume_array):.4f}")
    print(f"  最小音量: {np.min(volume_array):.4f}")
    print(f"  音量变化: {np.std(volume_array):.4f}")
    
    print(f"\n🎤 可能的对话/高潮段 (音量 > {threshold:.4f}):")
    for i, (start, end) in enumerate(dialogue_segments[:5]):
        print(f"  {i+1}. {start:.1f}s - {end:.1f}s (持续 {end-start:.1f}s)")
    
    if len(dialogue_segments) > 5:
        print(f"  ... 还有 {len(dialogue_segments)-5} 段")
    
    # 检测静音段
    silence_threshold = 0.01
    silent_segments = []
    silent_start = None
    
    for t, v in zip(time_axis, volume_array):
        if v < silence_threshold:
            if silent_start is None:
                silent_start = t
        else:
            if silent_start is not None:
                silent_segments.append((silent_start, t))
                silent_start = None
    
    if silent_start is not None:
        silent_segments.append((silent_start, time_axis[-1]))
    
    if silent_segments:
        print(f"\n🔇 静音段 (音量 < {silence_threshold}):")
        for i, (start, end) in enumerate(silent_segments[:5]):
            print(f"  {i+1}. {start:.1f}s - {end:.1f}s (持续 {end-start:.1f}s)")
    
    print("\n" + "="*60)
    
    video.close()
    return True

if __name__ == "__main__":
    video_path = "/Users/xiazhi/WorkBuddy/Claw/preview-analysis.mp4"
    output_plot = "/Users/xiazhi/WorkBuddy/Claw/audio_waveform.png"
    
    if not os.path.exists(video_path):
        print(f"错误: 视频文件不存在: {video_path}")
        exit(1)
    
    success = visualize_waveform(video_path, output_plot)
    
    if success:
        print(f"\n下一步: 如需识别具体台词，需要语音识别工具 (如Whisper)")
