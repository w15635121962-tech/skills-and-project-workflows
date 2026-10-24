from pathlib import Path
import concurrent.futures
import json
import math
import subprocess
import sys

import numpy as np
import soundfile as sf

WORK = Path(__file__).parent
RUN = WORK.parent.parent
OLD = RUN.parent / '20261017_学校粗剪' / '工作文件'
SKILL = Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts')
FPS = 25
SR = 48000
TOTAL_FRAMES = 11507
PAD_SAMPLES = 12000
LOGS = WORK / 'logs'
LOGS.mkdir(exist_ok=True)


def call(script, args, tag, dry=False):
    log = LOGS / (tag + ('.dry.json' if dry else '.json'))
    command = [sys.executable, str(SKILL / script), *map(str, args), '--json']
    if dry:
        command.append('--dry-run')
    p = subprocess.run(command, capture_output=True, text=True)
    log.write_text(p.stdout, encoding='utf-8')
    (LOGS / (tag + ('.dry.stderr.txt' if dry else '.stderr.txt'))).write_text(p.stderr)
    if p.returncode:
        raise RuntimeError(tag + ': ' + p.stdout[-1800:] + p.stderr[-600:])
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return {'raw_output': p.stdout}


def normalize(source, out, target, tag):
    args = [source, '-o', out, '-I', target, '--tp', -2, '--sample-rate', SR]
    if not out.exists():
        call('loudness.py', args, tag, dry=True)
        call('loudness.py', args, tag)
    return out


def wav_data(path):
    data, sr = sf.read(path, always_2d=True, dtype='float32')
    if sr != SR:
        raise ValueError(f'Unexpected sample rate {sr}: {path}')
    if data.shape[1] == 1:
        data = np.repeat(data, 2, axis=1)
    assert data.shape[1] == 2
    return data


def write_padded(path, data, length_frames):
    n = round(length_frames / FPS * SR)
    result = np.zeros((n + PAD_SAMPLES, 2), dtype=np.float32)
    result[:min(n, len(data))] = data[:n]
    assert not np.any(result[n:]), 'Padding must remain silent'
    sf.write(path, result, SR, subtype='PCM_24')


def build_speech():
    plan = json.loads((WORK.parent / 'narrative_edit_plan.json').read_text())
    narration_source = Path(plan['narration_source'])
    decoded = WORK / 'narration_decoded_48000.wav'
    if not decoded.exists():
        args = [narration_source, '-o', decoded, '--stereo']
        call('audio.py', args, 'narration_decode', dry=True)
        call('audio.py', args, 'narration_decode')
    narration_norm = normalize(decoded, WORK / 'narration_normalized.wav', -17.5, 'narration_normalize')
    path = WORK / '01_完整旁白_归一_余量.wav'
    data = wav_data(narration_norm)
    assert len(data) >= round(433.633 * SR), 'Narration last word would be lost'
    write_padded(path, data, 10842)
    speech = [{
        'path': str(path), 'record_frame': 0, 'duration_frames': 10842,
        'track': 1, 'kind': 'narration', 'source': str(narration_source),
        'source_in': 0.0, 'target_lufs': -17.5, 'fade_out_seconds': 0.0,
        'preserves_all_words': True, 'padding_seconds': 0.25,
    }]
    old_plan = json.loads((OLD / 'audio_plan.json').read_text())
    locations = [
        (76, 'C0043', 2.8, 6.2, 10850, 85, -17.8, '02_教师现场口号'),
        (81, 'C0160', 3.32, 7.60, 10935, 107, -18.5, '03_群体现场口号'),
        (84, 'C0163', 47.88, 62.48, 11042, 365, -17.8, '04_校长完整讲话'),
    ]
    for number, clip, start, end, record, frames, target, title in locations:
        # The old clean WAV contains its entire original camera audio, not only the old cut.
        old_item = next(v for v in old_plan['speech'] if Path(v['path']).name.startswith(f'{number:03d}_'))
        assert clip in old_item['source'], (number, old_item)
        clean = OLD / f'voice-{number}-clean.wav'
        call('probe.py', [clean], f'location_{number}_source_probe')
        data = wav_data(clean)
        data = data[round(start * SR):round(end * SR)].copy()
        assert len(data) == round(frames / FPS * SR)
        fade = round(0.008 * SR)
        data[:fade] *= np.linspace(0, 1, fade)[:, None]
        data[-fade:] *= np.linspace(1, 0, fade)[:, None]
        trimmed = WORK / f'{title}_trim.wav'
        sf.write(trimmed, data, SR, subtype='PCM_24')
        normalized = normalize(trimmed, WORK / f'{title}_normal.wav', target, f'location_{number}_normalize')
        dest = WORK / f'{title}_余量.wav'
        write_padded(dest, wav_data(normalized), frames)
        speech.append({
            'path': str(dest), 'record_frame': record, 'duration_frames': frames,
            'track': 2, 'kind': 'location', 'source': old_item['source'],
            'source_in': start, 'source_out': end, 'target_lufs': target,
            'reused_light_voice_file': str(clean), 'padding_seconds': 0.25,
        })
    return speech


def build_music():
    music_root = RUN / '配乐'
    files = {
        'piano': music_root / '01_温暖校园_AtlasAudio_511864.mp3',
        'science': music_root / '05_科学探索_LexinMusic_169621.mp3',
        'guitar': music_root / '04_木吉他人文_Universfield_232912.mp3',
        'cinema': music_root / '03_昂扬未来_Tunetank_409347.mp3',
    }
    normal = {}
    for key, source in files.items():
        # Source normalization is quiet enough for speech and doesn't introduce compression.
        target = -31.0 if key == 'science' else -32.0
        normal[key] = normalize(source, WORK / f'music_{key}_normal.wav', target, f'music_{key}_normalize')
    cues = [
        ('piano', 0, 2861, 0.0, 2.0, 2.0, 3, '书香与文脉'),
        ('science', 2811, 2002, 3.0, 2.0, 2.0, 4, '青春与探索'),
        ('guitar', 4763, 2171, 2.0, 2.0, 2.0, 3, '师者与成长'),
        ('science', 6884, 1909, 44.0, 2.0, 2.0, 4, '课程与收获'),
        ('cinema', 8743, 2124, 47.088969, 2.0, 2.0, 3, '共生与未来'),
        ('piano', 10817, 690, 15.0, 2.0, 4.0, 4, '现场声音与温暖回归'),
    ]
    stems = []
    for i, (key, record, frames, source_in, fade_in, fade_out, track, section) in enumerate(cues, 1):
        data = wav_data(normal[key])
        a = round(source_in * SR)
        n = round(frames / FPS * SR)
        data = data[a:a+n].copy()
        # MP3 duration fields include encoder delay; a tiny decoded-end shortfall is silence.
        if len(data) < n:
            assert n - len(data) < round(0.05 * SR), (key, n, len(data))
            data = np.pad(data, ((0, n-len(data)), (0, 0)))
        t = np.arange(n, dtype=np.float64) / SR
        env = np.minimum(1.0, t / fade_in)
        env *= np.minimum(1.0, np.maximum(0.0, (n - 1 - np.arange(n)) / (fade_out * SR)))
        # The quiet closing piano continues beneath real speech; only the end card rises slightly.
        if i == 6:
            absolute = t + record / FPS
            db = np.interp(absolute, [432.68, 434, 456.28, 457.4, 460.28], [-1, -2, -2, 1, 1])
            env *= 10 ** (db / 20)
        data *= env[:, None].astype(np.float32)
        dest = WORK / f'BGM_{i:02d}_{section}_余量.wav'
        write_padded(dest, data, frames)
        stems.append({
            'path': str(dest), 'record_frame': record, 'duration_frames': frames,
            'track': track, 'kind': 'music', 'source': str(files[key]),
            'source_in': source_in, 'source_out': source_in + frames / FPS,
            'section': section, 'target_source_lufs': -31 if key == 'science' else -32,
            'fade_in_seconds': fade_in, 'fade_out_seconds': fade_out,
            'padding_seconds': 0.25,
        })
    return stems


def main():
    # These are independent audio branches; only write within this task's audio_v2 directory.
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        speech_future = pool.submit(build_speech)
        music_future = pool.submit(build_music)
        speech = speech_future.result()
        music = music_future.result()
    n_total = round(TOTAL_FRAMES / FPS * SR)
    mix = np.zeros((n_total, 2), dtype=np.float32)
    for item in speech + music:
        data = wav_data(item['path'])
        a = round(item['record_frame'] / FPS * SR)
        length = round(item['duration_frames'] / FPS * SR)
        end = min(n_total, a + length)
        mix[a:end] += data[:end-a]
    peak = float(np.max(np.abs(mix)))
    assert peak < 1.0, f'Mix clips: {peak}'
    # The whole preview also carries the requested silent safety handle after the edit ends.
    dest = WORK / '完整混音试听.wav'
    write_padded(dest, mix, TOTAL_FRAMES)
    measured = call('loudness.py', [dest, '--measure-only'], 'complete_mix_measure')
    probe = call('probe.py', [dest], 'complete_mix_probe')
    output = {
        'fps': FPS, 'duration_frames': TOTAL_FRAMES, 'duration_seconds': TOTAL_FRAMES / FPS,
        'wav_silent_safety_handle_seconds': 0.25,
        'speech': speech, 'music': music,
        'mix_path': str(dest), 'mix_peak_dbfs': 20 * math.log10(peak),
        'mix_loudness_measurement': measured, 'mix_probe': probe,
        'notes': [
            '旁白保留完整词句，仅提取与音量归一；无降噪、无语速变化、无淡出末字。',
            '三段现场声根据旧计划核对了原视频身份，复用整段轻处理音轨后按原源时间精确提取。',
            '每个可导入WAV在标称有效时长后保留0.25秒静音，导入长度按duration_frames指定。',
            '5段音乐加1段尾声钢琴，双轨交叠2秒；原硬摇滚运动音乐未使用。',
            '完整混音文件实体长度460.53秒，其中末0.25秒是静音余量；有效剪辑长460.28秒。',
        ],
    }
    (WORK.parent / 'audio_plan_v2.json').write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(json.dumps({'audio_ready': True, 'speech': len(speech), 'music': len(music), 'mix_peak_dbfs': output['mix_peak_dbfs'], 'mix_measurement': measured, 'mix_path': str(dest)}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
