#!/usr/bin/env python3
"""Offline in-memory PCM proxy QC; no Resolve/ASR or original-media writes."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import math
import re
import subprocess
import numpy as np

HERE = Path(__file__).resolve().parent
FF = '/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'
RATE, FPS, SPF = 48000, 24, 2000


def db(x):
    return float(20 * np.log10(max(float(x), 1e-12)))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def run(args, raw=None):
    p = subprocess.run(args, input=raw, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError(p.stderr.decode('utf-8', 'replace')[-3000:])
    return p


def r128(x):
    p = run([FF, '-hide_banner', '-nostats', '-threads', '2', '-f', 'f32le', '-ar', str(RATE),
             '-ac', '2', '-i', 'pipe:0', '-af', 'loudnorm=I=-18:TP=-1:LRA=11:print_format=json',
             '-f', 'null', '-'], x.astype('<f4', copy=False).tobytes())
    raw = p.stderr.decode('utf-8', 'replace')
    v = json.loads(re.findall(r'\{\s*"input_i".*?\}', raw, re.S)[-1])
    return {k: float(v[k]) for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh')}


def trim_or_pad(x, count):
    actual = len(x)
    return (x[:count] if actual >= count else np.pad(x, ((0, count - actual), (0, 0)))), count - actual


def window_levels(x, window):
    frames = math.ceil(len(x) / window)
    padded = np.pad(x, ((0, frames * window - len(x)), (0, 0)))
    return np.sqrt(np.mean(padded.reshape(frames, window, 2).astype(np.float64) ** 2, axis=(1, 2)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--episodes', default='21,22,23,24,25')
    parser.add_argument('--output', default=str(HERE / '离线音频叠加QC'))
    parser.add_argument('--proxy-gain-overrides', help='Optional offline-only candidate gain changes JSON; never affects sources or Resolve.')
    args = parser.parse_args()
    selected = {int(x) for x in args.episodes.split(',')}
    overrides = read(args.proxy_gain_overrides) if args.proxy_gain_overrides else []
    paths = {'safe_mapping': HERE / '原生110_安全画面与A1A3执行映射.json',
             'native_A2': HERE / '原生110分组实测.json',
             'new_A4': HERE / 'A4配乐导入计划.json'}
    hashes = {str(p): sha(p) for p in paths.values()}
    safe = read(paths['safe_mapping'])
    native = {e['episode']: e for e in read(paths['native_A2'])['episodes']}
    music = {e['episode']: e for e in read(paths['new_A4'])['episodes']}
    report = {'created_at': datetime.datetime.now().astimezone().isoformat(),
              'scope': 'Offline in-memory48k stereo float PCM proxy; no Resolve connection, final video render, ASR, listening or original-source adjustment.',
              'input_hashes': hashes, 'proxy_assumptions': [
                  'A1/A3 use supplied100% source ranges and native clip gains. A2 uses native getter integer source bounds, atempo1.1, then pad/trim to measured native timeline duration. A4 uses new processed WAV at0dB.',
                  'ffmpeg default mono-to-stereo center upmix is used. Resolve track/bus pan law, fader/automation, plug-ins, routing and native pitch-correction engine are not emulated.',
                  'Native retime source getters quantize to whole frames; proxy endpoints may differ from actual subframe native playback by roughly one source frame. Native speed/pitch processing is not bit-identical to ffmpeg atempo.',
                  'A3/A2 energy closeness flags masking risk only. It does not prove intelligible speech or a subjective bad mix.',
                  'True peak/loudness is measured on unclipped floating-point sum, with no normalization, limiting or change applied.'],
              'episodes': [], 'overall_gain_changes_applied': False,
              'proxy_only_gain_candidates': overrides}
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    for ep in safe['episodes']:
        eno, duration = ep['episode'], ep['duration_frames']
        if eno not in selected:
            continue
        count = duration * SPF
        stems = {t: np.zeros((count, 2), dtype=np.float32) for t in range(1, 5)}
        cache, clips, ranges = {}, [], []

        def decoded(path):
            if path not in cache:
                p = run([FF, '-v', 'error', '-threads', '2', '-i', path, '-vn', '-ac', '2', '-ar', str(RATE),
                         '-f', 'f32le', 'pipe:1'])
                cache[path] = np.frombuffer(p.stdout, dtype='<f4').reshape(-1, 2).copy()
            return cache[path]

        def place(path, ss, se, rs, duration_frames, track, gain, item, speed=1.0):
            native_gain = gain
            matches = [o for o in overrides if o['episode'] == eno and o['track'] == track
                       and o['source_path'] == path and o['source_start_frame'] == ss
                       and o['source_end_frame_exclusive'] == se and o['record_frame'] == rs]
            if len(matches) > 1:
                raise ValueError('Duplicate proxy gain override.')
            if matches:
                gain = float(matches[0]['candidate_gain_db'])
            src = decoded(path)
            x = src[ss * SPF:se * SPF].copy()
            decoded_count = len(x)
            if speed != 1:
                p = run([FF, '-v', 'error', '-threads', '2', '-f', 'f32le', '-ar', str(RATE), '-ac', '2',
                         '-i', 'pipe:0', '-af', f'atempo={speed}', '-f', 'f32le', 'pipe:1'], x.astype('<f4').tobytes())
                x = np.frombuffer(p.stdout, dtype='<f4').reshape(-1, 2).copy()
            x, correction = trim_or_pad(x, duration_frames * SPF)
            x *= np.float32(10 ** (gain / 20))
            begin, end = rs * SPF, (rs + duration_frames) * SPF
            if begin < 0 or end > count:
                raise ValueError(f'EP{eno} A{track}: clip outside episode.')
            stems[track][begin:end] += x
            row = {'track': track, 'source_path': path, 'source_start_frame': ss,
                   'source_end_frame_exclusive_raw': se, 'record_frame': rs, 'duration_frames': duration_frames,
                   'record_start_seconds': rs / FPS, 'record_end_seconds': (rs + duration_frames) / FPS,
                   'native_gain_db': native_gain, 'proxy_gain_db': gain, 'speed_ratio_in_proxy': speed,
                   'original_item_id': item.get('original_item_id', item.get('id')),
                   'tag_or_name': item.get('tag', item.get('name', item.get('id'))),
                   'source_samples_decoded_in_range': decoded_count,
                   'post_atempo_alignment_padding_samples': max(0, correction),
                   'post_atempo_alignment_trimming_samples': max(0, -correction),
                   'sample_peak_dbfs_after_gain': db(np.max(np.abs(x)))}
            clips.append(row)
            if track == 2:
                ranges.append((begin, end))

        for tr, key in ((1, 'audio_A1'), (3, 'audio_A3')):
            for a in ep[key]:
                gain = float(a.get('properties', {}).get('AudioVolume', a.get('gain_db', 0)))
                place(a['source_path'], a['source_start_frame'], a['source_end_frame_exclusive'],
                      a['record_frame'], a['duration_frames'], tr, gain, a)
        for group in native[eno]['groups']:
            for a in group['native_110']:
                gain = float(a.get('properties', {}).get('AudioVolume', 0))
                place(a['path'], a['source_start'], a['source_end'], a['start'], a['end'] - a['start'],
                      2, gain, a, 1.1)
        for a in music[eno]['cues']:
            if sha(a['path']) != a['sha256']:
                raise ValueError('New music asset hash mismatch.')
            place(a['path'], 0, a['duration_frames'], a['record_frame'], a['duration_frames'], 4, 0, a)
        mixed = sum(stems.values())
        # No PCM files are exported: only temporary arrays/stdin buffers exist.
        measurement = r128(mixed)
        stem_measurements = {}
        for tr in (1, 2):
            stem_measurements[f'A{tr}'] = r128(stems[tr])
        for tr in (3, 4):
            stem_measurements[f'A{tr}'] = {'sample_peak_dbfs': db(np.max(np.abs(stems[tr]))),
                                           'whole_episode_rms_dbfs': db(np.sqrt(np.mean(stems[tr].astype(np.float64) ** 2)))}
        maximum_flat = int(np.argmax(np.abs(mixed)))
        sample, channel = divmod(maximum_flat, 2)
        peak_time = sample / RATE
        peak_frame = int(peak_time * FPS)
        active_peak = [dict(c, channel_sample_at_mix_sample_peak=float(stems[c['track']][sample, channel]))
                       for c in clips if c['record_frame'] <= peak_frame < c['record_frame'] + c['duration_frames']]
        levels2, levels3 = window_levels(stems[2], 4800), window_levels(stems[3], 4800)
        db2 = 20 * np.log10(np.maximum(levels2, 1e-12))
        db3 = 20 * np.log10(np.maximum(levels3, 1e-12))
        voiced = db2 > -42
        close = voiced & (db3 > -35) & (db3 - db2 > -6)
        events, begin = [], None
        for k in range(len(close) + 1):
            flag = bool(close[k]) if k < len(close) else False
            if flag and begin is None:
                begin = k
            if not flag and begin is not None:
                stop = k
                if stop - begin >= 2:
                    winner = int(begin + np.argmax(db3[begin:stop] - db2[begin:stop]))
                    time = winner * .1
                    contributors = [c for c in clips if c['track'] == 3 and c['record_start_seconds'] <= time < c['record_end_seconds']]
                    events.append({'timeline_start_seconds': round(begin * .1, 3),
                                   'timeline_end_seconds': round(min(stop * .1, duration / FPS), 3),
                                   'max_A3_minus_A2_RMS_db': round(float(np.max(db3[begin:stop] - db2[begin:stop])), 2),
                                   'worst_100ms_start_seconds': round(time, 3),
                                   'A2_100ms_RMS_dbfs': round(float(db2[winner]), 2),
                                   'A3_100ms_RMS_dbfs': round(float(db3[winner]), 2),
                                   'A3_source_contributors': contributors,
                                   'meaning': 'Energy masking risk only; not intelligible-speech or subjective audition judgment.'})
                begin = None
        # Exact clip-start PCM step, retaining only nontrivial jumps near VO.
        boundary_steps = []
        for a in clips:
            if a['track'] != 3:
                continue
            pos = a['record_frame'] * SPF
            if pos <= 0 or pos >= count or not any(lo <= pos < hi for lo, hi in ranges):
                continue
            step = db(np.max(np.abs(stems[3][pos] - stems[3][pos - 1])))
            if step > -30:
                boundary_steps.append({'timeline_seconds': pos / RATE, 'timeline_frame': a['record_frame'],
                                       'A3_sample_step_dbfs': step, 'source_path': a['source_path'],
                                       'source_start_frame': a['source_start_frame'], 'native_gain_db': a['native_gain_db'],
                                       'suggestion_only': 'At this native clip edge, audition for click/sudden entry; a2–5ms amplitude fade can soften without shifting source mapping. Not applied.'})
        recommendations = []
        if measurement['input_tp'] > -1:
            delta = round(-1 - measurement['input_tp'] - .3, 2)
            recommendations.append({'kind': 'peak_headroom_candidate_not_applied',
                                    'proxy_true_peak_dbtp': measurement['input_tp'],
                                    'additional_gain_db_to_all_active_clips_or_bus_at_least': delta,
                                    'scope': 'Only proxy-derived headroom floor. To change individual clips, use listed active-at-sample-peak items and remeasure after choice.',
                                    'active_at_sample_peak': active_peak})
        ep_report = {'episode': eno, 'duration_frames': duration, 'duration_seconds': duration / FPS,
                     'mix_r128': measurement, 'sample_peak_dbfs': db(np.max(np.abs(mixed))),
                     'sample_peak_timeline_seconds': peak_time, 'sample_peak_channel': channel,
                     'samples_above_unity_per_channel_total': int(np.count_nonzero(np.abs(mixed) > 1)),
                     'stems': stem_measurements, 'active_at_sample_peak': active_peak,
                     'A3_close_to_VO_events': events, 'A3_nontrivial_start_steps_during_VO': boundary_steps,
                     'gain_recommendations_not_applied': recommendations, 'source_clip_placements': clips}
        report['episodes'].append(ep_report)
        print(json.dumps({'episode': eno, 'mix_I': measurement['input_i'], 'mix_TP': measurement['input_tp'],
                          'A3_near_VO_events': len(events), 'A3_edges': len(boundary_steps)}, ensure_ascii=False), flush=True)
        (output / '新版四轨离线代理QC.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    report['all_input_JSON_hashes_unchanged'] = {str(p): sha(p) for p in paths.values()} == hashes
    peak_episode = max(report['episodes'], key=lambda e: e['mix_r128']['input_tp'])
    report['summary'] = {'episodes': len(report['episodes']), 'max_mix_true_peak_dbtp': peak_episode['mix_r128']['input_tp'],
                         'max_peak_episode': peak_episode['episode'],
                         'all_mix_true_peaks_below_zero': all(e['mix_r128']['input_tp'] < 0 for e in report['episodes']),
                         'all_mix_true_peaks_at_or_below_minus1': all(e['mix_r128']['input_tp'] <= -1 for e in report['episodes']),
                         'A3_VO_energy_events_total': sum(len(e['A3_close_to_VO_events']) for e in report['episodes']),
                         'A3_edge_steps_during_VO_total': sum(len(e['A3_nontrivial_start_steps_during_VO']) for e in report['episodes']),
                         'final_DaVinci_bus_mix_acceptance': False, 'temporary_PCM_files_written': False}
    destination = output / '新版四轨离线代理QC.json'
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# 新版四轨离线音频代理QC', '', '只做离线PCM代理测量，未连接Resolve、未改源或增益，不能代替原生母线听音验收。', '',
             '| 集数 | 代理响度LUFS | 真峰值dBTP | A3贴近VO事件 | A3硬边缘 |', '|---|---:|---:|---:|---:|']
    for ep in report['episodes']:
        lines.append(f'| EP{ep["episode"]} | {ep["mix_r128"]["input_i"]:.2f} | {ep["mix_r128"]["input_tp"]:.2f} | {len(ep["A3_close_to_VO_events"])} | {len(ep["A3_nontrivial_start_steps_during_VO"])} |')
    lines += ['', 'A3贴近VO：连续至少200ms，VO RMS高于-42dBFS，A3高于-35dBFS且与VO相差不足6dB。仅为遮蔽风险，未判断实际内容。', '', '代理限制：']
    lines += ['- ' + s for s in report['proxy_assumptions']]
    destination.with_suffix('.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(report['summary'], ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
