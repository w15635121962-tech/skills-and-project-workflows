#!/usr/bin/env python3
"""Measure a local recording's estimated beats and energy; never edits media."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

import librosa
import numpy as np


def analyze(path):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is not on PATH")
    path = Path(path).expanduser().resolve(strict=True)
    decoded = subprocess.run(
        [ffmpeg, "-v", "error", "-i", str(path), "-map", "0:a:0",
         "-ac", "1", "-ar", "22050", "-f", "f32le", "pipe:1"],
        capture_output=True, check=True, timeout=300,
    )
    audio = np.frombuffer(decoded.stdout, dtype="<f4").copy()
    if len(audio) < 22050 or not np.isfinite(audio).all():
        raise ValueError("Need at least one second of valid audio")
    sr = 22050
    tempo, frames = librosa.beat.beat_track(y=audio, sr=sr, hop_length=512)
    beats = librosa.frames_to_time(frames, sr=sr, hop_length=512)
    energy = []
    for start in range(0, len(audio), sr):
        chunk = audio[start:start + sr]
        rms = float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2)))
        energy.append({"time_seconds": round(start / sr, 3),
                       "rms_dbfs": round(20 * np.log10(max(rms, 1e-8)), 2)})
    return {
        "input": str(path), "duration_seconds": round(len(audio) / sr, 3),
        "estimated_bpm": round(float(np.asarray(tempo).ravel()[0]), 2),
        "beat_seconds": [round(float(t), 3) for t in beats],
        "energy_per_second": energy,
        "limits": ["Tempo and beats are estimates; check half/double tempo by listening.",
                   "Downbeats and musical phrase boundaries are not detected.",
                   "RMS measures level, not emotion, quality, or integrated LUFS."],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("--output", help="New JSON output path; existing files refused")
    args = parser.parse_args()
    result = analyze(args.input)
    payload = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)
    if args.output:
        with Path(args.output).open("x", encoding="utf-8") as handle:
            handle.write(payload + "\n")
        print(json.dumps({"output": str(Path(args.output).resolve()),
                          "estimated_bpm": result["estimated_bpm"],
                          "duration_seconds": result["duration_seconds"],
                          "beat_count": len(result["beat_seconds"])}, ensure_ascii=False))
    else:
        print(payload)


if __name__ == "__main__":
    main()
