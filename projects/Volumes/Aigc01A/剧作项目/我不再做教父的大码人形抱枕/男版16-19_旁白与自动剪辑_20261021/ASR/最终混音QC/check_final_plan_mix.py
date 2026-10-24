#!/usr/bin/env python3
"""Read-only, frame/sample-accurate offline mix QA; no Resolve connection.

Reconstruct A1 from every V1 source trim and gain, and A2 from narration edits.
Mono is duplicated to L/R without attenuation for a conservative upper-peak
model. The report is not a Resolve bus render, listening or lip-sync validation.
No normalization, limiter, retiming or unplanned fade is introduced.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import time

try:
    import numpy as np
except ModuleNotFoundError:
    project = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(project / '配音制作_前3集/制作资料/音频内容与顺序核验_20261018/ASR/.venv/lib/python3.12/site-packages'))
    import numpy as np

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
FF = Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg')
FP = FF.with_name('ffprobe')
RATE = 48000
OVERSAMPLE_RATE = 192000
FPS = 24
THRESHOLD_DBTP = -1.0
TARGET_DBTP = -2.0


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def db(value):
    return float(20 * np.log10(max(float(value), 1e-12)))


def metrics(audio):
    flat_index = int(np.argmax(np.abs(audio)))
    sample_index, channel = np.unravel_index(flat_index, audio.shape)
    peak = abs(float(audio[sample_index, channel]))
    return {'peak_dbfs': db(peak), 'peak_linear': peak,
            'peak_time_seconds': float(sample_index / RATE), 'peak_channel': int(channel + 1),
            'rms_dbfs': db(np.sqrt(np.mean(audio ** 2))),
            'samples_at_or_above_full_scale': int(np.count_nonzero(np.abs(audio) >= 1)),
            'channel_peak_dbfs': [db(np.max(np.abs(audio[:, c]))) for c in range(2)]}


def probe(path):
    cp = subprocess.run([str(FP), '-v', 'error', '-select_streams', 'a:0', '-show_streams', '-of', 'json', str(path)],
                        capture_output=True, text=True, encoding='utf-8', check=True)
    streams = json.loads(cp.stdout)['streams']
    assert len(streams) == 1, 'Missing or ambiguous first audio stream: ' + str(path)
    channels = int(streams[0]['channels'])
    assert channels in [1, 2], 'Only native mono/stereo sources are in this task'
    return channels, streams[0]


def decode(path, expected_sha):
    source_sha = sha(path)
    assert source_sha == expected_sha, 'Source changed since measurement: ' + str(path)
    channels, stream = probe(path)
    cp = subprocess.run([str(FF), '-nostdin', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-vn',
                         '-ac', str(channels), '-ar', str(RATE), '-f', 'f32le', 'pipe:1'],
                        capture_output=True, check=True)
    audio = np.frombuffer(cp.stdout, dtype='<f4').reshape((-1, channels)).copy()
    assert audio.size and np.isfinite(audio).all()
    if channels == 1:
        audio = np.repeat(audio, 2, axis=1)
    assert sha(path) == source_sha
    return audio, channels, stream


def write_float_wav(path, audio):
    cp = subprocess.run([str(FF), '-nostdin', '-v', 'error', '-f', 'f32le', '-ar', str(RATE), '-ac', '2',
                         '-i', 'pipe:0', '-c:a', 'pcm_f32le', '-y', str(path)],
                        input=audio.astype('<f4').tobytes(), capture_output=True)
    if cp.returncode:
        raise RuntimeError(cp.stderr.decode('utf-8', errors='replace')[-2000:])


def ebur128(path):
    cp = subprocess.run([str(FF), '-nostdin', '-hide_banner', '-nostats', '-i', str(path),
                         '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                        capture_output=True, text=True, encoding='utf-8', check=True)
    path.with_suffix('.ebur128.log').write_text(cp.stderr, encoding='utf-8')
    def last(pattern):
        values = re.findall(pattern, cp.stderr, re.M)
        return float(values[-1]) if values and values[-1] not in ['-inf', 'inf', 'nan'] else None
    return {'integrated_loudness_lufs': last(r'^\s*I:\s*([-+\d.inf]+)\s*LUFS'),
            'loudness_range_lu': last(r'^\s*LRA:\s*([-+\d.inf]+)\s*LU'),
            'true_peak_dbtp': last(r'^\s*Peak:\s*([-+\d.inf]+)\s*dBFS')}


def active_clips(clips, seconds):
    output = []
    for clip in clips:
        start = clip['record_frame'] / FPS
        end = start + (clip['source_end_frame'] - clip['source_start_frame']) / FPS
        if start <= seconds < end:
            output.append({'kind': clip['kind'], 'path': clip['path'], 'tag': clip.get('tag'),
                           'gain_db': clip['gain_db'], 'record_start_frame': clip['record_frame'],
                           'source_time_at_peak_seconds': clip['source_start_frame'] / FPS + seconds - start})
    return output


def locate_true_peaks(path, clips):
    # Independent 4x interpolation provides useful source/timeline positions;
    # EBU R128 above remains the stated standards-based TP measurement.
    cp = subprocess.run([str(FF), '-nostdin', '-v', 'error', '-i', str(path), '-af', f'aresample={OVERSAMPLE_RATE}',
                         '-ac', '2', '-f', 'f32le', 'pipe:1'], capture_output=True, check=True)
    audio = np.frombuffer(cp.stdout, dtype='<f4').reshape((-1, 2))
    maximum = np.max(np.abs(audio), axis=1)
    index = int(np.argmax(maximum))
    seconds = index / OVERSAMPLE_RATE
    threshold = 10 ** (THRESHOLD_DBTP / 20)
    above = np.flatnonzero(maximum > threshold)
    groups = []
    if len(above):
        starts = np.r_[0, np.where(np.diff(above) > OVERSAMPLE_RATE * .1)[0] + 1]
        ends = np.r_[starts[1:], len(above)]
        for a, z in zip(starts, ends):
            positions = above[a:z]
            local = int(positions[np.argmax(maximum[positions])])
            at = local / OVERSAMPLE_RATE
            groups.append({'timeline_start_seconds': float(positions[0] / OVERSAMPLE_RATE),
                           'timeline_end_seconds': float((positions[-1] + 1) / OVERSAMPLE_RATE),
                           'peak_time_seconds': at, 'peak_estimate_dbtp': db(maximum[local]),
                           'active_sources_at_peak': active_clips(clips, at)})
    groups.sort(key=lambda g: g['peak_estimate_dbtp'], reverse=True)
    return {'method': '4x ffmpeg interpolation, independent diagnostic location; EBU R128 TP log is authoritative',
            'oversample_rate': OVERSAMPLE_RATE, 'maximum_estimate_dbtp': db(maximum[index]),
            'maximum_time_seconds': seconds, 'active_sources_at_maximum': active_clips(clips, seconds),
            'regions_above_minus1_dbtp': groups[:20], 'total_regions_above_minus1_dbtp': len(groups)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=BASE / 'final_native_plan.json')
    parser.add_argument('--episodes', type=int, nargs='+', default=[16, 17, 18, 19])
    parser.add_argument('--output', type=Path, default=HERE)
    parser.add_argument('--keep-analysis-wav', action='store_true', help='Keep float analysis WAV; otherwise remove after logged measurements.')
    parser.add_argument('--expected-plan-sha256', help='Require the root-approved frozen plan hash.')
    args = parser.parse_args()
    assert args.plan.is_file(), 'Final plan has not appeared yet; no waiting or mutation performed'
    raw_plan = args.plan.read_bytes()
    plan_hash = hashlib.sha256(raw_plan).hexdigest()
    if args.expected_plan_sha256:
        assert plan_hash == args.expected_plan_sha256, 'Frozen final plan hash differs from root-approved hash'
    plan = json.loads(raw_plan)
    assert plan.get('status') == 'READY_FOR_NATIVE_ASSEMBLY'
    assert plan.get('fps', FPS) == FPS
    episodes = [e for e in plan['episodes'] if e['episode'] in args.episodes]
    assert {e['episode'] for e in episodes} == set(args.episodes)
    level_file = BASE / 'ASR/source_levels.json'
    source_levels = json.loads(level_file.read_text(encoding='utf-8'))
    source_hashes = {r['path']: r['source_sha256'] for r in source_levels['files']}
    args.output.mkdir(parents=True, exist_ok=True)
    report = {'created_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'plan_path': str(args.plan.resolve()),
              'plan_sha256': plan_hash, 'source_levels_path': str(level_file), 'sample_rate': RATE,
              'channels': 2, 'frame_samples': RATE // FPS, 'all_source_speed_percent': 100,
              'mono_routing': 'Equal amplitude duplicate to both channels, no pan-law attenuation; conservative peak reconstruction',
              'plan_audio_gains_applied_exactly': True, 'normalizer_limiter_fades_added': False,
              'audio_sources_modified': False, 'resolve_or_UI_used': False,
              'human_listening_performed': False, 'episodes': [],
              'limits': ['Offline plan reconstruction, not a rendered Resolve bus or actual listening.',
                         'Native pan law, track/bus effects and hardware monitoring are not inferred.',
                         'Mono VO is duplicated equally for a conservative upper-peak estimate; center pan attenuation may lower Resolve output.',
                         'Original AAC/MP3 decoding follows FFmpeg edit-list/priming metadata; no artificial speed or sample drift is applied.']}
    for ep in episodes:
        started = time.monotonic()
        duration_frames = ep['duration_frames']
        length = duration_frames * RATE // FPS
        tracks = {k: np.zeros((length, 2), dtype=np.float64) for k in ['A1', 'A2']}
        cache, clip_rows, shortages = {}, [], []
        for key, track in [('video', 'A1'), ('narration', 'A2')]:
            for clip in ep[key]:
                path = clip['path']
                assert path in source_hashes, 'Unmeasured source: ' + path
                if path not in cache:
                    cache[path] = decode(path, source_hashes[path])
                audio, channels, stream = cache[path]
                s0, s1, record = clip['source_start_frame'], clip['source_end_frame'], clip['record_frame']
                assert all(isinstance(x, int) for x in [s0, s1, record])
                assert clip.get('speed_percent', clip.get('native_speed_percent', clip.get('source_speed_percent', 100))) == 100
                start, count, at = s0 * RATE // FPS, (s1 - s0) * RATE // FPS, record * RATE // FPS
                assert count > 0 and 0 <= at < length and at + count <= length
                part = audio[start:start + count]
                missing = count - len(part)
                if missing:
                    shortages.append({'kind': track, 'path': path, 'missing_samples': missing, 'missing_seconds': missing / RATE})
                    assert missing <= RATE // FPS, 'Source shortage exceeds one frame; inspect plan: ' + path
                    part = np.pad(part, ((0, missing), (0, 0)))
                gain = float(clip.get('gain_db', 0))
                assert -60 <= gain <= 0
                tracks[track][at:at + count] += part.astype(np.float64) * 10 ** (gain / 20)
                clip_rows.append({**clip, 'kind': track, 'source_channels': channels, 'source_sha256': source_hashes[path],
                                  'rendered_samples': count, 'source_shortage_samples': missing})
        mix = tracks['A1'] + tracks['A2']
        wav_path = args.output / f"EP{ep['episode']}_offline_plan_mix_48k_float.wav"
        write_float_wav(wav_path, mix)
        loudness = ebur128(wav_path)
        peak = loudness['true_peak_dbtp']
        assert peak is not None
        mix_metric = metrics(mix)
        if peak >= THRESHOLD_DBTP:
            location = locate_true_peaks(wav_path, clip_rows)
        else:
            location = {'method': 'EBU R128 true peak is below threshold; no extra oversampling/localization pass needed',
                        'maximum_estimate_dbtp': peak, 'maximum_time_seconds': mix_metric['peak_time_seconds'],
                        'time_is_sample_peak_not_true_peak': True,
                        'regions_above_minus1_dbtp': [], 'total_regions_above_minus1_dbtp': 0}
        triggered = peak > THRESHOLD_DBTP or location['maximum_estimate_dbtp'] > THRESHOLD_DBTP
        reduction = math.ceil(max(0, max(peak, location['maximum_estimate_dbtp']) - TARGET_DBTP) * 10) / 10 if triggered else 0
        output = {'episode': ep['episode'], 'timeline': ep.get('timeline_name'),
                  'duration_frames': duration_frames, 'duration_seconds': duration_frames / FPS,
                  'A1_clips': len(ep['video']), 'A2_clips': len(ep['narration']),
                  'metrics': {'A1': metrics(tracks['A1']), 'A2': metrics(tracks['A2']), 'mix': mix_metric},
                  'ebu_r128': loudness, 'true_peak_location': location,
                  'peak_above_minus1_dbtp': triggered, 'source_end_zero_padding': shortages,
                  'attenuation_recommendation_only': None if not triggered else {
                      'safe_uniform_audio_reduction_db': reduction, 'target_dbtp': TARGET_DBTP,
                      'meaning': 'Reducing A1 and A2 together by this amount would preserve their balance and lower offline peak to at most target. Apply only after root decision, with a new plan revision/hash.',
                      'alternative': 'If the peak overlaps VO and ambience, root may instead lower only A1 ambience after simulating that specific proposal; never lower original spoken dialogue without checking its context.'},
                  'analysis_wav': str(wav_path), 'analysis_wav_retained': args.keep_analysis_wav,
                  'clip_rows': clip_rows, 'runtime_seconds': time.monotonic() - started}
        if not args.keep_analysis_wav:
            wav_path.unlink()
        report['episodes'].append(output)
        report['plan_unchanged_after_analysis'] = sha(args.plan) == plan_hash
        assert report['plan_unchanged_after_analysis']
        save(args.output / 'offline_final_mix_qc.json', report)
        print(json.dumps({'episode': ep['episode'], 'seconds': output['duration_seconds'],
                          'integrated_lufs': loudness['integrated_loudness_lufs'],
                          'true_peak_dbtp': peak, 'sample_peak_dbfs': output['metrics']['mix']['peak_dbfs'],
                          'peak_time_seconds': location['maximum_time_seconds'], 'above_minus1_dbtp': triggered,
                          'suggested_uniform_reduction_db_only': reduction}, ensure_ascii=False), flush=True)
        del mix, tracks, cache
    report['finished_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    report['all_four_completed'] = len(report['episodes']) == 4
    report['plan_unchanged_after_analysis'] = sha(args.plan) == plan_hash
    assert report['plan_unchanged_after_analysis']
    save(args.output / 'offline_final_mix_qc.json', report)
    print(json.dumps({'report': str(args.output / 'offline_final_mix_qc.json'),
                      'plan_sha256': plan_hash, 'plan_unchanged': True,
                      'attention_episodes': [e['episode'] for e in report['episodes'] if e['peak_above_minus1_dbtp']]}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
