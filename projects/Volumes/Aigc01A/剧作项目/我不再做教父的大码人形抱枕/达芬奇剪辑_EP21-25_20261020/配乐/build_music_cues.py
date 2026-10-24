#!/usr/bin/env python3
"""Create separate music assets; never open Resolve or rewrite the picture/audio plan."""
from pathlib import Path
import concurrent.futures
import datetime
import hashlib
import json
import math
import re
import subprocess
import numpy as np
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parent.parent
MUSIC = BASE / '配乐'
ANALYSIS = MUSIC / '分析'
CUES = MUSIC / 'Cues'
FFMPEG = '/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'
FFPROBE = str(Path(FFMPEG).with_name('ffprobe'))
RATE, FPS, SAMPLES_PER_FRAME = 48000, 24, 2000

# Boundary frames are existing editorial/story block boundaries, not new edits.
# Source preferences are seconds; a quiet 100 ms neighbourhood is selected below.
SPECS = {
    21: [(0, 1080, 1, 0, '病房陪坐、握手与保存愿望券：稀疏遗憾'),
         (1080, 1463, 3, 0, '十八岁赠券回忆：短钢琴记忆，不循环'),
         (1463, 2533, 1, 45, '回到现在、拒绝回庄园与请求拥抱')],
    22: [(0, 1681, 2, 0, '撕券、过期、醉夜告白与追问：低压氛围'),
         (1681, 2703, 2, 72, '低眼难言、东翼误会与日记复仇真相：继续低压，换原曲后段')],
    23: [(0, 1142, 2, 0, '病房质问、支票与邻居身份：克制张力'),
         (1142, 1672, 1, 134, '街头遇见、自由微笑与男主退缩：悔意')],
    24: [(0, 1254, 2, 0, '隔墙听见回家、公寓与未归：低声悬置'),
         (1254, 2255, 1, 47, '夜晚抵墙、等到天亮与不敢敲门：遗憾'),
         (2255, 3222, 2, 74, '梦、药、改变结局与道歉：压低后悔')],
    25: [(0, 1936, 2, 0, '界限对峙、不再等待与走出病房：克制压力'),
         (1936, 2586, 4, 0, '他停住之后、离院与纽约飞机：清醒而柔和的觉醒')],
}

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def db(v):
    return float(20 * math.log10(max(float(v), 1e-12)))

def run(args, data=None):
    p = subprocess.run(args, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors='replace')[-4000:])
    return p

def analyse_array(x):
    if len(x) < RATE // 2:
        return None
    p = run([FFMPEG, '-hide_banner', '-nostats', '-f', 'f32le', '-ar', str(RATE), '-ac', '2',
             '-i', 'pipe:0', '-af', 'loudnorm=I=-29:TP=-2:LRA=11:print_format=json',
             '-f', 'null', '-'], np.asarray(x, dtype='<f4').tobytes())
    raw = p.stderr.decode(errors='replace')
    m = re.findall(r'\{\s*"input_i".*?\}', raw, re.S)
    if not m:
        raise RuntimeError(raw[-1500:])
    v = json.loads(m[-1])
    return {k: float(v[k]) for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh')}

def analyse_wav(path):
    p = run([FFMPEG, '-hide_banner', '-nostats', '-i', str(path),
             '-af', 'loudnorm=I=-29:TP=-2:LRA=11:print_format=json', '-f', 'null', '-'])
    raw = p.stderr.decode(errors='replace')
    v = json.loads(re.findall(r'\{\s*"input_i".*?\}', raw, re.S)[-1])
    return {k: float(v[k]) for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh')}

def parse_srt(path):
    text = path.read_text(encoding='utf-8-sig')
    def sec(t):
        h, m, s, ms = map(int, re.split('[:,]', t))
        return h * 3600 + m * 60 + s + ms / 1000
    matches = re.findall(r'(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})', text)
    return [(sec(a), sec(b)) for a, b in matches]

def decode(track):
    p = run([FFMPEG, '-v', 'error', '-i', track['local_path'], '-vn', '-ar', str(RATE),
             '-ac', '2', '-f', 'f32le', 'pipe:1'])
    x = np.frombuffer(p.stdout, dtype='<f4').reshape(-1, 2).copy()
    win = RATE // 10
    padded = np.pad(x, ((0, (-len(x)) % win), (0, 0)))
    blocks = padded.reshape(-1, win, 2)
    rms = np.sqrt(np.mean(blocks.astype(np.float64) ** 2, axis=(1, 2)))
    peaks = np.max(np.abs(blocks), axis=(1, 2))
    energy = []
    for s in range(0, len(x), 5 * RATE):
        y = x[s:s + 5 * RATE]
        energy.append({'start_seconds': s / RATE, 'end_seconds': min(s + 5 * RATE, len(x)) / RATE,
                       'rms_dbfs': round(db(np.sqrt(np.mean(y.astype(np.float64) ** 2))), 3),
                       'sample_peak_dbfs': round(db(np.max(np.abs(y))), 3)})
    original = json.loads((ANALYSIS / (track['id'] + '_source_r128_silence.json')).read_text())
    report = {'source_path': track['local_path'], 'sha256': sha(track['local_path']),
              'decoded_samples_48000': len(x), 'decoded_duration_seconds': len(x) / RATE,
              'sample_peak_dbfs': db(np.max(np.abs(x))), 'energy_blocks_5_seconds': energy,
              'r128': original['loudnorm_analysis'],
              'silence_threshold_db': original['silence_threshold_db'],
              'silence_starts': original['silence_starts'], 'silence_ends': original['silence_ends'],
              'entry_method_limit': '100ms RMS/peak locates low-energy entries; it does not verify musical bars or subjective phrasing.'}
    plot_source(track, rms, peaks, len(x) / RATE)
    print('Decoded/analysed:', track['id'], round(len(x) / RATE, 3), flush=True)
    return track['id'], x, rms, report

def plot_source(track, rms, peak, duration):
    w, h = 1500, 480
    im = Image.new('RGB', (w, h), '#101821')
    d = ImageDraw.Draw(im)
    d.text((32, 15), track['id'] + ' | 100ms RMS cyan / sample peak amber | dBFS', fill='white')
    left, top, pw, ph = 60, 60, w - 100, 350
    for value in (-60, -45, -30, -15, 0):
        yy = top + ph * (-value / 60)
        d.line((left, yy, left + pw, yy), fill='#34404b')
        d.text((12, yy - 6), str(value), fill='#aeb8c1')
    for series, color in ((peak, '#e5b850'), (rms, '#61dbdf')):
        points = [(left + i / max(1, len(series) - 1) * pw,
                   top + ph * (1 - (max(-60, db(v)) + 60) / 60)) for i, v in enumerate(series)]
        d.line(points, fill=color, width=1)
    for t in range(0, int(duration) + 1, 15):
        xx = left + t / duration * pw
        d.text((xx - 10, top + ph + 10), str(t) + 's', fill='#aeb8c1')
    im.save(ANALYSIS / (track['id'] + '_energy.png'))

def select_entry(x, rms, preferred, length, minimum=0):
    if preferred == 0:
        return 0, {'method': 'original beginning, with 3-second fade-in', 'preferred_seconds': 0}
    lo = max(minimum, preferred - 2.5)
    hi = min(len(x) / RATE - length, preferred + 2.5)
    if hi < lo:
        raise ValueError('Source is shorter than the proposed non-looping excerpt')
    idx = np.arange(math.ceil(lo * 10), math.floor(hi * 10) + 1)
    # Avoid favouring a single isolated zero crossing: average the next 0.5 seconds.
    scores = [float(np.mean(rms[i:i + 5])) for i in idx]
    chosen = int(idx[int(np.argmin(scores))])
    return chosen * (RATE // 10), {
        'method': 'minimum mean RMS over the next 0.5s, sampled at 100ms; no musical-bar assertion',
        'preferred_seconds': preferred, 'search_seconds': [round(lo, 6), round(hi, 6)],
        'selected_seconds': chosen / 10, 'selected_entry_rms_dbfs': db(scores[int(np.argmin(scores))])}

def envelopes(length, global_start, intervals):
    time = np.arange(length, dtype=np.float64) / RATE + global_start
    speech = np.zeros(length, dtype=bool)
    protect = np.zeros(length, dtype=np.float32)
    # Hold extends the protection beyond SRT word edges. Close gaps merge naturally.
    attack, hold_pre, hold_post, release = 0.20, 0.12, 0.18, 0.75
    clipped = []
    for a, b in intervals:
        if b + hold_post + release < global_start or a - hold_pre - attack > time[-1]:
            continue
        speech |= (time >= a) & (time < b)
        onset, offset = a - hold_pre, b + hold_post
        loc = np.minimum(np.clip((time - (onset - attack)) / attack, 0, 1),
                         np.clip((offset + release - time) / release, 0, 1))
        protect = np.maximum(protect, loc.astype(np.float32))
        local_a, local_b = max(0, a - global_start), min(length / RATE, b - global_start)
        if local_b > local_a:
            clipped.append([local_a, local_b])
    edges = np.ones(length, dtype=np.float32)
    ni, no = min(3 * RATE, length // 2), min(2 * RATE, length // 2)
    edges[:ni] = np.sin(np.linspace(0, np.pi / 2, ni, dtype=np.float32)) ** 2
    edges[-no:] = np.cos(np.linspace(0, np.pi / 2, no, dtype=np.float32)) ** 2
    edges[0] = edges[-1] = 0
    return speech, protect, edges, clipped, {
        'source': 'current episode SRT speech intervals', 'attack_seconds': attack,
        'speech_pre_hold_seconds': hold_pre, 'speech_post_hold_seconds': hold_post,
        'release_seconds': release, 'fade_in_seconds': ni / RATE, 'fade_out_seconds': no / RATE,
        'speech_region_target_lufs': -32, 'gap_target_lufs': -29, 'max_gap_boost_db': 3}

def plot_cue(path, x, protect, edges, title):
    w, h = 1450, 420
    im = Image.new('RGB', (w, h), '#101821')
    d = ImageDraw.Draw(im)
    d.text((25, 12), title + ' | peak cyan / speech protection amber / edge fade green', fill='white')
    left, top, pw, ph = 60, 55, 1340, 300
    win = RATE // 20
    count = math.ceil(len(x) / win)
    peak = np.array([np.max(np.abs(x[i * win:(i + 1) * win])) for i in range(count)])
    for value in (-60, -40, -20, 0):
        yy = top + ph * (-value / 60)
        d.line((left, yy, left + pw, yy), fill='#34404b')
        d.text((15, yy - 5), str(value), fill='#aeb8c1')
    points = [(left + i / max(1, len(peak) - 1) * pw,
               top + ph * (1 - (max(-60, db(v)) + 60) / 60)) for i, v in enumerate(peak)]
    d.line(points, fill='#61dbdf', width=1)
    for values, color in ((protect[::win], '#e5b850'), (edges[::win], '#65ce7b')):
        pts = [(left + i / max(1, len(values) - 1) * pw, top + ph - float(v) * 45) for i, v in enumerate(values)]
        d.line(pts, fill=color, width=1)
    duration = len(x) / RATE
    for t in range(0, math.ceil(duration) + 1, 5):
        if t <= duration:
            d.text((left + t / duration * pw - 8, top + ph + 10), str(t) + 's', fill='#aeb8c1')
    im.save(path)

def make_cue(ep, spec, n, source_data, intervals, tracks):
    start, end, source_num, preferred, purpose = spec
    track = tracks[source_num - 1]
    _, original, rms, source_report = source_data[track['id']]
    frames, length = end - start, (end - start) * SAMPLES_PER_FRAME
    minimum = 1681 / FPS if ep['episode'] == 22 and n == 2 else 0
    source_start, selection = select_entry(original, rms, preferred, length / RATE, minimum)
    x = original[source_start:source_start + length].copy()
    if len(x) != length:
        raise ValueError('Excerpt requires a loop or padding, which is not permitted')
    speech, protect, edges, clipped, env_info = envelopes(length, start / FPS, intervals)
    x *= edges[:, None]
    raw_speech = analyse_array(x[speech])
    if not raw_speech or not math.isfinite(raw_speech['input_i']):
        raise ValueError('No measurable current-SRT speech region for cue')
    base_gain = -32 - raw_speech['input_i']
    x *= np.float32(10 ** (base_gain / 20))
    gap_mask = (~speech) & (protect < 0.05) & (edges > 0.95)
    gap_before = analyse_array(x[gap_mask])
    boost = 3.0 if not gap_before or not math.isfinite(gap_before['input_i']) else min(3.0, max(0.0, -29 - gap_before['input_i']))
    gain_db = boost * (1 - protect)
    x *= np.power(10, gain_db / 20).astype(np.float32)[:, None]
    # Native PCM precision conversion below. No dynamics compression or limiter.
    out_dir = CUES / ('EP' + str(ep['episode']))
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / f"EP{ep['episode']}_M{n:02d}_{start:05d}-{end:05d}_{track['id'][3:]}.wav"
    run([FFMPEG, '-v', 'error', '-y', '-f', 'f32le', '-ar', str(RATE), '-ac', '2',
         '-i', 'pipe:0', '-c:a', 'pcm_s24le', '-ar', str(RATE), '-ac', '2', str(output)],
        np.asarray(x, dtype='<f4').tobytes())
    probe = json.loads(run([FFPROBE, '-v', 'error', '-select_streams', 'a:0', '-show_streams',
                            '-show_format', '-of', 'json', str(output)]).stdout)
    stream = probe['streams'][0]
    assert stream['codec_name'] == 'pcm_s24le' and int(stream['sample_rate']) == RATE
    assert stream['channels'] == 2 and int(stream['bits_per_raw_sample']) == 24
    assert stream['time_base'] == '1/48000' and int(stream['duration_ts']) == length
    overall = analyse_array(x)
    actual_pcm24 = analyse_wav(output)
    speech_actual = analyse_array(x[speech])
    gap_actual = analyse_array(x[gap_mask])
    if actual_pcm24['input_tp'] >= -12:
        raise ValueError('Unexpectedly high music peak; inspect before import')
    assert abs(speech_actual['input_i'] - (-32)) <= 0.2
    assert np.all(x[0] == 0) and np.all(x[-1] == 0)
    plot_cue(ANALYSIS / (output.stem + '_envelope.png'), x, protect, edges, output.stem)
    metrics = {'overall': overall, 'actual_pcm24_wav_r128': actual_pcm24, 'speech_regions_concatenated': speech_actual,
               'unprotected_gap_regions_concatenated': gap_actual,
               'sample_peak_dbfs': db(np.max(np.abs(x))),
               'speech_seconds': int(np.count_nonzero(speech)) / RATE,
               'unprotected_gap_seconds': int(np.count_nonzero(gap_mask)) / RATE,
               'metric_note': 'Speech/gap subsets are concatenated solely for aggregate loudness measurement. They are not separate playback edits. Sparse short gaps may not provide a measurable LUFS value.'}
    dump(ANALYSIS / (output.stem + '_analysis.json'), {'ffprobe': probe, 'loudness': metrics})
    item = {'id': f"EP{ep['episode']}_M{n:02d}", 'path': str(output), 'record_frame': start,
            'duration_frames': frames, 'source_start_frame': 0, 'source_end_frame_exclusive': frames,
            'track': 4, 'resolve_item_gain_db': 0, 'gain_already_baked_into_asset': True,
            'purpose': purpose, 'sample_rate': RATE, 'channels': 2, 'pcm_bit_depth': 24,
            'sample_count': length, 'duration_seconds': length / RATE, 'loop_count': 0,
            'source_info': {'path': track['local_path'], 'title': track['title'], 'author': track['author'],
                            'sha256': source_report['sha256'], 'source_start_sample_48000': source_start,
                            'source_start_seconds': source_start / RATE,
                            'source_end_seconds_exclusive': (source_start + length) / RATE,
                            'entry_selection': selection, 'original_r128': source_report['r128']},
            'processing': {**env_info, 'base_gain_relative_to_decoded_original_db': round(base_gain, 6),
                           'gap_boost_db': round(boost, 6), 'edge_curve': 'squared sine/cosine',
                           'duck_curve': 'continuous linear dB gain with union of SRT protection envelopes',
                           'compressor_or_limiter': False, 'speech_intervals_relative_seconds': clipped,
                           'transition': 'non-overlapping consecutive A4 cues; 2s outgoing fade and 3s incoming fade create a soft dip'},
            'loudness_analysis': metrics,
            'license': {'name': track['license'], 'source_page_url': track['page_url'],
                        'license_url': track['license_url'], 'license_legalcode_url': track['license_legalcode_url'],
                        'attribution_required': track['attribution_required'],
                        'source_html_evidence': track['source_html_evidence'],
                        'source_text_evidence': track['source_text_evidence'],
                        'download_date_utc': track['download_date_utc'],
                        'content_id_status': track['content_id_status']},
            'sha256': sha(output), 'analysis_path': str(ANALYSIS / (output.stem + '_analysis.json'))}
    print(item['id'], 'frames', frames, 'source', round(source_start / RATE, 2),
          'gain', round(base_gain, 2), 'speech I', speech_actual['input_i'], 'TP', overall['input_tp'], flush=True)
    return item

def main():
    ANALYSIS.mkdir(parents=True, exist_ok=True)
    plan_path, license_path = BASE / '剪辑执行计划.json', MUSIC / '配乐来源与授权.json'
    plan = json.loads(plan_path.read_text())
    tracks = json.loads(license_path.read_text())['tracks']
    frozen = [plan_path, license_path] + [BASE / 'SRT' / f'EP{n}.srt' for n in range(21, 26)] + [Path(t['local_path']) for t in tracks]
    before = {str(p): sha(p) for p in frozen}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        decoded = list(pool.map(decode, tracks))
    source_data = {row[0]: row for row in decoded}
    dump(ANALYSIS / '原曲能量分析.json', [row[3] for row in decoded])
    report = {'created_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'Separate music WAV assets only; no Resolve access, picture render, or existing A1/A2/A3 modification.',
              'fps': FPS, 'sample_rate': RATE, 'samples_per_frame': SAMPLES_PER_FRAME,
              'import_policy': 'Native A4. Use each asset path with source_start_frame=0 and source_end_frame_exclusive=duration_frames, record_frame as supplied. Asset gain is preprocessed; set clip gain 0 dB. Do not add another attenuation.',
              'audition_status': 'No subjective whole-track listening or completed audiovisual mix audition performed. Author descriptions, decoded waveform/energy, EBU R128 loudness, fades, SRT protection and exact sample/frame checks were used.',
              'license_manifest': str(license_path), 'episodes': [], 'validation': {}}
    for ep in plan['episodes']:
        episode = ep['episode']
        if episode not in SPECS:
            continue
        intervals = parse_srt(BASE / 'SRT' / f'EP{episode}.srt')
        cues = [make_cue(ep, spec, i + 1, source_data, intervals, tracks) for i, spec in enumerate(SPECS[episode])]
        assert cues[0]['record_frame'] == 0
        for a, b in zip(cues, cues[1:]):
            assert a['record_frame'] + a['duration_frames'] == b['record_frame']
        assert cues[-1]['record_frame'] + cues[-1]['duration_frames'] == ep['duration_frames']
        report['episodes'].append({'episode': episode, 'timeline_name': ep['timeline_name'], 'fps': FPS,
                                   'duration_frames': ep['duration_frames'], 'audio_track': 4, 'cues': cues})
    after = {str(p): sha(p) for p in frozen}
    assert before == after
    report['validation'] = {'cue_count': sum(len(e['cues']) for e in report['episodes']),
                            'episode_count': len(report['episodes']), 'all_outputs_pcm_24bit_stereo_48000': True,
                            'all_sample_counts_equal_duration_frames_times_2000': True,
                            'all_cues_nonoverlapping_and_within_episode': True,
                            'all_episode_a4_music_spans_exact_timeline_bounds': True,
                            'all_speech_subset_loudness_within_0_2_lu_of_minus_32': True,
                            'all_output_true_peaks_below_minus_12_dbtp': True,
                            'all_cues_nonlooping': True, 'immutable_input_hashes_unchanged': before}
    report['validation']['actual_pcm24_output_wavs_r128_verified'] = True
    dump(MUSIC / '配乐执行计划.json', report)
    print('COMPLETE', report['validation']['cue_count'], 'cues; no existing plan/media/SRT rewritten.', flush=True)

if __name__ == '__main__':
    main()
