#!/usr/bin/env python3
"""
Video Analyzer - AI视频解析流水线
完整流程：视频解码 → 帧采样 → 视觉分析 → 音频转录 → 时序分析 → 结构化输出

依赖：
  pip install openai requests opencv-python pillow
  whisper: pip install openai-whisper

用法：
  python video_analyzer.py --video input.mp4 [--api-key YOUR_KEY] [--model gpt-4o] [--fps 1] [--whisper-model tiny] [--output result.json]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ── 配置 ──────────────────────────────────────────────────────────────

DEFAULT_WHISPER_MODEL = "tiny"  # tiny/base/small/medium/large
DEFAULT_SAMPLE_FPS = 1          # 每秒采样帧数
DEFAULT_MAX_FRAMES = 30         # 最大分析帧数
DEFAULT_VISION_MODEL = "gpt-4o"
DEFAULT_LANGUAGE = "zh"        # zh / en / auto


# ── Step 1: 视频信息提取 ─────────────────────────────────────────────

@dataclass
class VideoInfo:
    path: str = ""
    duration: float = 0.0
    width: int = 0
    height: int = 0
    fps: float = 0.0
    codec: str = ""
    audio_codec: str = ""
    size_mb: float = 0.0
    has_audio: bool = False

    def to_dict(self):
        return asdict(self)


def probe_video(video_path: str) -> VideoInfo:
    """使用 ffprobe 获取视频元数据"""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")

    data = json.loads(result.stdout)
    info = VideoInfo(path=video_path)

    # Format info
    fmt = data.get("format", {})
    info.duration = float(fmt.get("duration", 0))
    info.size_mb = int(fmt.get("size", 0)) / (1024 * 1024)

    # Stream info
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            info.width = int(stream.get("width", 0))
            info.height = int(stream.get("height", 0))
            # 优先从 r_frame_rate 取
            r = stream.get("r_frame_rate", "0/1")
            try:
                num, den = r.split("/")
                info.fps = float(num) / float(den) if float(den) > 0 else float(stream.get("avg_frame_rate", 0))
            except (ValueError, ZeroDivisionError):
                info.fps = float(stream.get("avg_frame_rate", 0))
            info.codec = stream.get("codec_name", "unknown")
        elif stream.get("codec_type") == "audio":
            info.audio_codec = stream.get("codec_name", "unknown")
            info.has_audio = True

    return info


# ── Step 2: 帧采样 ──────────────────────────────────────────────────

@dataclass
class Frame:
    index: int = 0
    timestamp_sec: float = 0.0
    path: str = ""
    description: str = ""


def sample_frames(
    video_path: str,
    output_dir: str,
    fps: float = DEFAULT_SAMPLE_FPS,
    max_frames: int = DEFAULT_MAX_FRAMES,
    strategy: str = "uniform"
) -> list[Frame]:
    """
    从视频中采样帧
    strategy:
      - uniform: 均匀间隔采样
      - keyframe: 仅提取关键帧（I帧）
      - scene: 基于场景变化检测（需 OpenCV）
    """
    os.makedirs(output_dir, exist_ok=True)
    info = probe_video(video_path)

    frames: list[Frame] = []

    if strategy == "uniform":
        frames = _sample_uniform(video_path, output_dir, fps, max_frames, info)
    elif strategy == "keyframe":
        frames = _sample_keyframes(video_path, output_dir, max_frames)
    elif strategy == "scene":
        frames = _sample_scene_change(video_path, output_dir, max_frames, info)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    print(f"  ✓ 采样完成：{len(frames)} 帧")
    return frames


def _sample_uniform(
    video_path: str, output_dir: str, fps: float, max_frames: int, info: VideoInfo
) -> list[Frame]:
    """均匀间隔采样"""
    # 计算间隔
    total_possible = int(info.duration * fps)
    actual_fps = min(fps, max_frames / max(info.duration, 0.01))

    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", f"fps={actual_fps:.4f}",
        "-q:v", "2",
        "-y",
        os.path.join(output_dir, "frame_%04d.jpg")
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    frames = []
    for f in sorted(Path(output_dir).glob("frame_*.jpg")):
        idx = int(f.stem.split("_")[1])
        ts = idx / actual_fps
        frames.append(Frame(index=idx, timestamp_sec=round(ts, 2), path=str(f)))

    return frames[:max_frames]


def _sample_keyframes(
    video_path: str, output_dir: str, max_frames: int
) -> list[Frame]:
    """提取 I 帧（关键帧）"""
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vf", "select='eq(pict_type\\,I)'",
        "-vsync", "vfr",
        "-q:v", "2",
        "-y",
        os.path.join(output_dir, "keyframe_%04d.jpg")
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    frames = []
    info = probe_video(video_path)
    for f in sorted(Path(output_dir).glob("keyframe_*.jpg")):
        idx = int(f.stem.split("_")[1])
        # I帧时间戳近似：按比例分配
        all_frames = sorted(Path(output_dir).glob("keyframe_*.jpg"))
        pos = all_frames.index(f)
        ts = (pos / max(len(all_frames), 1)) * info.duration
        frames.append(Frame(index=idx, timestamp_sec=round(ts, 2), path=str(f)))

    return frames[:max_frames]


def _sample_scene_change(
    video_path: str, output_dir: str, max_frames: int, info: VideoInfo
) -> list[Frame]:
    """基于场景变化的智能采样（使用 OpenCV）"""
    import cv2

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    prev_frame = None
    threshold = 30.0  # 像素差异阈值
    min_interval = 1.0  # 最小帧间隔（秒）
    last_saved_time = -min_interval

    frames: list[Frame] = []
    frame_idx = 0
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    while cap.isOpened() and len(frames) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = frame_idx / fps
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_frame is not None:
            diff = cv2.absdiff(prev_frame, gray)
            mean_diff = diff.mean()

            if mean_diff > threshold and (current_time - last_saved_time) >= min_interval:
                path = os.path.join(output_dir, f"scene_{len(frames):04d}.jpg")
                cv2.imwrite(path, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                frames.append(Frame(
                    index=len(frames),
                    timestamp_sec=round(current_time, 2),
                    path=path
                ))
                last_saved_time = current_time

        prev_frame = gray
        frame_idx += 1

    cap.release()
    return frames


# ── Step 3: 视觉分析（Vision API）─────────────────────────────────────

def analyze_frame_with_vision(
    frame_path: str,
    api_key: str,
    model: str = DEFAULT_VISION_MODEL,
    language: str = DEFAULT_LANGUAGE,
    prompt: str = ""
) -> str:
    """
    使用 OpenAI Vision API 分析单帧图像
    """
    import base64
    from openai import OpenAI

    if not prompt:
        lang_hint = "请用中文" if language == "zh" else "Please respond in English"
        prompt = (
            f"你是一个专业的视频分析师。请详细描述这张视频帧中的内容，包括：\n"
            f"1. 场景描述（环境、光线、构图）\n"
            f"2. 人物/物体（位置、动作、表情、衣着）\n"
            f"3. 视觉风格（色调、质感、特效）\n"
            f"4. 关键细节（文字、道具、特殊元素）\n"
            f"{lang_hint}，简洁但信息密度高，不超过200字。"
        )

    with open(frame_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                    }
                ]
            }],
            max_tokens=500,
            temperature=0.3
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[分析失败: {e}]"


def analyze_frames_batch(
    frames: list[Frame],
    api_key: str,
    model: str = DEFAULT_VISION_MODEL,
    language: str = DEFAULT_LANGUAGE,
    prompt: str = "",
    delay: float = 0.5
) -> list[Frame]:
    """
    批量分析所有帧
    """
    total = len(frames)
    for i, frame in enumerate(frames):
        print(f"  分析帧 {i+1}/{total} ({frame.timestamp_sec}s)...", end=" ", flush=True)
        frame.description = analyze_frame_with_vision(
            frame.path, api_key, model, language, prompt
        )
        print(f"✓")
        if i < total - 1:
            time.sleep(delay)
    return frames


# ── Step 4: 音频转录（Whisper）───────────────────────────────────────

def transcribe_audio(
    video_path: str,
    model_name: str = DEFAULT_WHISPER_MODEL,
    language: str = DEFAULT_LANGUAGE,
    temp_dir: str = None
) -> dict:
    """
    提取视频音频并用 Whisper 转录
    返回: {"text": "...", "segments": [{"start": 0.0, "end": 2.5, "text": "..."}], ...}
    """
    import whisper

    # 提取音频
    audio_path = os.path.join(temp_dir or tempfile.mkdtemp(), "audio.wav")
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        "-y", audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        return {"text": "", "segments": [], "error": f"音频提取失败: {result.stderr}"}

    # 加载 Whisper
    print(f"  加载 Whisper {model_name} 模型...", flush=True)
    model = whisper.load_model(model_name)

    # 转录
    lang = language if language != "auto" else None
    options = {
        "language": lang,
        "verbose": False,
    }

    result_data = model.transcribe(audio_path, **options)

    # 清理临时音频
    try:
        os.remove(audio_path)
    except OSError:
        pass

    segments = [
        {
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip()
        }
        for seg in result_data.get("segments", [])
    ]

    print(f"  ✓ 转录完成：{len(segments)} 段")
    return {
        "text": result_data.get("text", "").strip(),
        "language": result_data.get("language", "unknown"),
        "segments": segments
    }


# ── Step 5: 时序分析与结构化输出 ──────────────────────────────────────

def generate_report(
    video_info: VideoInfo,
    frames: list[Frame],
    transcription: dict,
    api_key: str,
    model: str = DEFAULT_VISION_MODEL,
    language: str = DEFAULT_LANGUAGE
) -> dict:
    """
    将帧描述和音频文字结合，生成结构化分析报告
    """
    from openai import OpenAI

    # 构建帧时间线
    timeline = []
    for f in frames:
        timeline.append({
            "timestamp": f.timestamp_sec,
            "frame_path": f.path,
            "description": f.description
        })

    # 构建音频段落
    audio_segments = transcription.get("segments", [])

    lang = "中文" if language == "zh" else "English"
    prompt = (
        f"你是一个专业的视频内容分析师。请根据以下视频帧描述和音频转录内容，"
        f"生成一份结构化的视频分析报告。\n\n"
        f"## 视频基本信息\n"
        f"- 时长: {video_info.duration:.1f}秒\n"
        f"- 分辨率: {video_info.width}x{video_info.height}\n"
        f"- 编码: {video_info.codec}\n\n"
        f"## 采样帧描述（按时间顺序）\n"
    )
    for t in timeline:
        prompt += f"- [{t['timestamp']:.1f}s] {t['description']}\n"

    if audio_segments:
        prompt += f"\n## 音频转录\n"
        for seg in audio_segments:
            prompt += f"- [{seg['start']:.1f}s-{seg['end']:.1f}s] {seg['text']}\n"

    prompt += (
        f"\n请用{lang}输出以下格式的JSON（不要包含markdown代码块标记）：\n"
        f"{{\n"
        f'  "title": "视频标题或主题",\n'
        f'  "summary": "100字以内的内容摘要",\n'
        f'  "key_scenes": [\n'
        f'    {{"time": "00:05", "description": "场景描述", "type": "动作/对话/转场/特效"}}\n'
        f'  ],\n'
        f'  "visual_style": "视觉风格分析",\n'
        f'  "techniques": ["使用的AI技术或制作技巧"],\n'
        f'  "prompts": ["可复用的提示词或参数"],\n'
        f'  "audio_transcription": "音频完整转录文本",\n'
        f'  "tags": ["标签"]\n'
        f"}}"
    )

    client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )
        raw = resp.choices[0].message.content.strip()

        # 清理 markdown 代码块标记
        if raw.startswith("```"):
            lines = raw.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            raw = "\n".join(lines)

        report = json.loads(raw)
    except json.JSONDecodeError as e:
        report = {"raw_response": raw, "parse_error": str(e)}
    except Exception as e:
        report = {"error": str(e)}

    return report


def build_final_output(
    video_info: VideoInfo,
    frames: list[Frame],
    transcription: dict,
    report: dict,
    output_path: str
):
    """构建最终 JSON 输出"""
    output = {
        "video_info": video_info.to_dict(),
        "frames": [
            {
                "index": f.index,
                "timestamp_sec": f.timestamp_sec,
                "path": f.path,
                "description": f.description
            }
            for f in frames
        ],
        "transcription": transcription,
        "analysis_report": report,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"  ✓ 报告已保存: {output_path}")
    return output


# ── 主入口 ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI视频解析流水线")
    parser.add_argument("--video", "-v", required=True, help="视频文件路径")
    parser.add_argument("--api-key", "-k", default=os.environ.get("OPENAI_API_KEY", ""),
                        help="OpenAI API Key（或设置 OPENAI_API_KEY 环境变量）")
    parser.add_argument("--model", "-m", default=DEFAULT_VISION_MODEL,
                        help=f"Vision 模型 (默认: {DEFAULT_VISION_MODEL})")
    parser.add_argument("--fps", type=float, default=DEFAULT_SAMPLE_FPS,
                        help=f"采样帧率 (默认: {DEFAULT_SAMPLE_FPS} fps)")
    parser.add_argument("--max-frames", type=int, default=DEFAULT_MAX_FRAMES,
                        help=f"最大采样帧数 (默认: {DEFAULT_MAX_FRAMES})")
    parser.add_argument("--whisper-model", default=DEFAULT_WHISPER_MODEL,
                        help=f"Whisper 模型 (默认: {DEFAULT_WHISPER_MODEL})")
    parser.add_argument("--strategy", default="uniform",
                        choices=["uniform", "keyframe", "scene"],
                        help="帧采样策略")
    parser.add_argument("--language", default=DEFAULT_LANGUAGE,
                        help="语言 (zh/en/auto)")
    parser.add_argument("--output", "-o", default=None,
                        help="输出 JSON 路径")
    parser.add_argument("--skip-vision", action="store_true",
                        help="跳过 Vision API 分析（仅帧采样+音频转录）")
    parser.add_argument("--skip-audio", action="store_true",
                        help="跳过音频转录")
    parser.add_argument("--temp-dir", default=None,
                        help="临时目录（帧文件存储）")

    args = parser.parse_args()

    # 验证输入
    if not os.path.isfile(args.video):
        print(f"✗ 视频文件不存在: {args.video}")
        sys.exit(1)

    if not args.skip_vision and not args.api_key:
        print("✗ 需要提供 OpenAI API Key（--api-key 或 OPENAI_API_KEY 环境变量）")
        print("  或使用 --skip-vision 跳过视觉分析")
        sys.exit(1)

    # 临时目录
    temp_dir = args.temp_dir or tempfile.mkdtemp(prefix="video_analysis_")
    os.makedirs(temp_dir, exist_ok=True)

    # 输出路径
    if args.output:
        output_path = args.output
    else:
        base = Path(args.video).stem
        output_path = str(Path(temp_dir) / f"{base}_analysis.json")

    print("=" * 60)
    print("  AI 视频解析流水线")
    print("=" * 60)

    # Step 1: 视频信息
    print("\n[1/5] 视频信息提取...")
    info = probe_video(args.video)
    print(f"  时长: {info.duration:.1f}s | 分辨率: {info.width}x{info.height}"
          f" | 编码: {info.codec} | 音频: {'有' if info.has_audio else '无'}")

    # Step 2: 帧采样
    print(f"\n[2/5] 帧采样 (策略: {args.strategy}, fps: {args.fps})...")
    frames_dir = os.path.join(temp_dir, "frames")
    frames = sample_frames(args.video, frames_dir, fps=args.fps,
                           max_frames=args.max_frames, strategy=args.strategy)

    # Step 3: 视觉分析
    if not args.skip_vision:
        print(f"\n[3/5] 视觉分析 (模型: {args.model})...")
        frames = analyze_frames_batch(
            frames, api_key=args.api_key, model=args.model,
            language=args.language
        )
    else:
        print(f"\n[3/5] 跳过视觉分析 (--skip-vision)")

    # Step 4: 音频转录
    transcription = {"text": "", "segments": [], "language": "none"}
    if not args.skip_audio and info.has_audio:
        print(f"\n[4/5] 音频转录 (Whisper {args.whisper_model})...")
        transcription = transcribe_audio(
            args.video, model_name=args.whisper_model,
            language=args.language, temp_dir=temp_dir
        )
    else:
        print(f"\n[4/5] 跳过音频转录")

    # Step 5: 生成报告
    if not args.skip_vision:
        print(f"\n[5/5] 时序分析与报告生成...")
        report = generate_report(
            info, frames, transcription,
            api_key=args.api_key, model=args.model, language=args.language
        )
    else:
        report = {"note": "视觉分析已跳过，仅输出帧采样和音频数据"}

    # 输出
    result = build_final_output(info, frames, transcription, report, output_path)

    print("\n" + "=" * 60)
    print("  解析完成!")
    print("=" * 60)

    # 打印摘要
    if "summary" in report:
        print(f"\n摘要: {report['summary']}")
    if transcription.get("text"):
        print(f"\n音频转录: {transcription['text'][:200]}...")

    print(f"\n完整报告: {output_path}")
    print(f"临时文件: {temp_dir}")


if __name__ == "__main__":
    main()
