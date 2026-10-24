#!/usr/bin/env python3.14
"""
从预告片视频中提取音频并分析
"""
import os
import sys
import numpy as np

try:
    from moviepy import VideoFileClip
except ImportError:
    print("错误: 无法导入 moviepy，尝试使用 opencv")
    sys.exit(1)

def extract_audio(video_path, output_audio_path):
    """提取视频中的音频"""
    print(f"正在读取视频: {video_path}")
    
    try:
        video = VideoFileClip(video_path)
    except Exception as e:
        print(f"读取视频失败: {e}")
        return False
    
    print(f"视频时长: {video.duration:.2f} 秒")
    print(f"视频尺寸: {video.size}")
    print(f"FPS: {video.fps}")
    
    # 提取音频
    audio = video.audio
    if audio is None:
        print("警告: 该视频没有音轨!")
        return False
    
    print(f"音频采样率: {audio.fps} Hz")
    
    # 保存音频
    print(f"正在导出音频到: {output_audio_path}")
    try:
        audio.write_audiofile(
            output_audio_path,
            fps=44100,
            codec='aac' if output_audio_path.endswith('.m4a') else None,
            logger=None  # 禁用进度条
        )
        print("音频提取完成!")
    except Exception as e:
        print(f"导出音频失败: {e}")
        return False
    
    # 分析音频特征
    print("\n正在分析音频特征...")
    output_npy = output_audio_path.replace('.m4a', '_waveform.npy')
    timestamps, volumes = analyze_audio_waveform(audio, video.duration)
    
    # 保存结果
    np.save(output_npy, {'timestamps': timestamps, 'volumes': volumes})
    print(f"波形数据已保存到: {output_npy}")
    
    video.close()
    return True

def analyze_audio_waveform(audio_clip, duration):
    """分析音频波形特征，返回时间戳和音量列表"""
    sample_rate = 44100
    
    # 每秒采样一次分析音量
    num_samples = int(duration)
    volumes = []
    timestamps = []
    
    print(f"  分析 {num_samples} 秒的音频数据...")
    
    for i in range(num_samples):
        t_start = float(i)
        t_end = float(i + 1)
        if t_end > duration:
            t_end = duration
            if t_end - t_start < 0.1:
                break
        
        # 获取这一秒的音频片段
        try:
            segment = audio_clip.subclipped(t_start, t_end)
            # 转换为numpy数组
            audio_array = segment.to_soundarray()
            
            # 计算RMS音量
            if len(audio_array.shape) > 1:
                # 立体声，取平均值
                rms = float(np.sqrt(np.mean(audio_array**2)))
            else:
                rms = float(np.sqrt(np.mean(audio_array**2)))
            
            volumes.append(rms)
            timestamps.append(t_start)
            
            # 进度提示
            if (i + 1) % 10 == 0:
                print(f"  已分析 {i+1}/{num_samples} 秒...")
                
        except Exception as e:
            print(f"  分析 {t_start:.1f}s 时出错: {e}")
            volumes.append(0.0)
            timestamps.append(t_start)
    
    # 打印统计信息
    if len(volumes) > 0:
        volumes_arr = np.array(volumes)
        print(f"\n  平均音量: {np.mean(volumes_arr):.4f}")
        print(f"  最大音量: {np.max(volumes_arr):.4f} (at {timestamps[np.argmax(volumes_arr)]:.1f}s)")
        print(f"  最小音量: {np.min(volumes_arr):.4f} (at {timestamps[np.argmin(volumes_arr)]:.1f}s)")
        print(f"  音量标准差: {np.std(volumes_arr):.4f}")
        
        # 检测静音段
        silent_threshold = 0.01
        silent_segments = []
        silent_start = None
        
        for i, (ts, vol) in enumerate(zip(timestamps, volumes)):
            if vol < silent_threshold:
                if silent_start is None:
                    silent_start = ts
            else:
                if silent_start is not None:
                    silent_segments.append((silent_start, ts))
                    silent_start = None
        
        # 处理最后一个静音段
        if silent_start is not None:
            silent_segments.append((silent_start, timestamps[-1]))
        
        if silent_segments:
            print(f"\n  检测到 {len(silent_segments)} 处静音段:")
            for start, end in silent_segments[:5]:  # 只显示前5个
                print(f"    {start:.1f}s - {end:.1f}s (持续 {end-start:.1f}s)")
    
    return timestamps, volumes

if __name__ == "__main__":
    video_path = "/Users/xiazhi/WorkBuddy/Claw/preview-analysis.mp4"
    audio_path = "/Users/xiazhi/WorkBuddy/Claw/preview-audio.m4a"
    
    if not os.path.exists(video_path):
        print(f"错误: 视频文件不存在: {video_path}")
        sys.exit(1)
    
    success = extract_audio(video_path, audio_path)
    
    if success:
        print(f"\n✅ 音频已保存到: {audio_path}")
        waveform_path = audio_path.replace('.m4a', '_waveform.npy')
        print(f"   波形数据已保存到: {waveform_path}")
        print("\n下一步: 使用语音识别工具分析台词内容")
