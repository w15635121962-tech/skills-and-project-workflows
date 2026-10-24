#!/usr/bin/env python3
"""Read-only media QC. Writes reports only; never edits audio or production progress."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
DEFAULT_MANIFEST = TASK / '文本核验' / 'manifest.json'
BUNDLED_BIN = Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin')

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def tool_path(explicit: str | None, name: str) -> str:
    candidates = [explicit, shutil.which(name), str(BUNDLED_BIN / name)]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(Path(candidate).resolve())
    raise FileNotFoundError(f'{name} unavailable; provide --{name}')

def command(argv: list[str], timeout: float):
    p = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True, encoding='utf-8',
                       errors='replace', timeout=timeout, check=False)
    return {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}

def positive_float(value):
    try:
        f = float(value)
        return f if math.isfinite(f) and f > 0 else None
    except (TypeError, ValueError):
        return None

def progress_provenance(path: Path | None):
    if path is None or not path.is_file():
        return {'status': 'not_available', 'reason': 'No current production progress supplied/read.'}
    d = read_json(path)
    summary = {k: d[k] for k in ['voice', 'model', 'mode', 'speed', 'speed_percent', 'status']
               if isinstance(d, dict) and k in d and isinstance(d[k], (str, int, float, bool, type(None)))}
    return {'status': 'source_record_read_only', 'path': str(path.resolve()),
            'sha256': sha256(path), 'recorded_settings': summary,
            'note': 'Provenance/config record only; not acoustic proof of voice identity or 100% speed.'}

def verify(args):
    manifest_path = Path(args.manifest).resolve()
    manifest_hash = sha256(manifest_path)
    manifest = read_json(manifest_path)
    groups = manifest['groups']
    expected_counts = {4: 8, 5: 7, 6: 9}
    if len(groups) != 24 or Counter(g['episode'] for g in groups) != Counter(expected_counts):
        raise ValueError('Expected the approved 24 inputs: EP04=8, EP05=7, EP06=9.')
    expected_names = [f'大码女版枕头{ep:02d}-{seq:02d}-01' for ep in [4, 5, 6]
                      for seq in range(1, expected_counts[ep] + 1)]
    if [g['basename'] for g in groups] != expected_names:
        raise ValueError('Manifest order/naming differs from the approved episode-sequence-take plan.')
    ffmpeg, ffprobe = tool_path(args.ffmpeg, 'ffmpeg'), tool_path(args.ffprobe, 'ffprobe')
    report = {
        'status': 'RUNNING', 'created_at': datetime.now(timezone.utc).isoformat(),
        'scope': '24 downloaded female EP04-06 narration files; technical checks only',
        'manifest': str(manifest_path), 'manifest_sha256': manifest_hash,
        'tools': {'ffmpeg': ffmpeg, 'ffprobe': ffprobe},
        'requested_voice': manifest.get('voice'), 'requested_speed_percent': manifest.get('speed_percent'),
        'provenance': progress_provenance(Path(args.progress).resolve() if args.progress else None),
        'speed_verification_boundary': '100% is the requested/source-recorded generation setting. File duration, sample rate and codec cannot prove unprocessed/original speed; no retiming, resampling or media writes are performed by this script.',
        'content_verification': 'Not performed: no ASR, listening, dialogue/narration comparison or voice-identity verification.',
        'source_audio_mutations': False, 'production_progress_mutations': False, 'items': []}
    for g in groups:
        path = Path(g['planned_audio_path']).resolve()
        row = {'basename': g['basename'], 'episode': g['episode'],
               'narration_sequence': g['narration_sequence'], 'take': g['take'],
               'expected_filename': g['planned_audio_filename'], 'path': str(path),
               'status': 'NOT_CHECKED', 'errors': [], 'warnings': []}
        report['items'].append(row)
        expected_filename = g['basename'] + '.mp3'
        row['name_exact'] = path.name == expected_filename == g['planned_audio_filename']
        row['name_pattern_valid'] = bool(re.fullmatch(r'大码女版枕头(04|05|06)-\d{2}-01\.mp3', path.name))
        if not row['name_exact'] or not row['name_pattern_valid']:
            row['errors'].append('INVALID_EXPECTED_NAME')
        if not path.is_file():
            row['status'] = 'MISSING'
            row['exists'] = False
            continue
        row['exists'] = True
        before = path.stat()
        row['bytes'] = before.st_size
        row['mtime_ns_before'] = before.st_mtime_ns
        if not before.st_size:
            row['status'] = 'FAIL'
            row['errors'].append('EMPTY_FILE')
            continue
        row['sha256'] = sha256(path)
        try:
            probe = command([ffprobe, '-v', 'error', '-show_format', '-show_streams',
                             '-of', 'json', str(path)], args.timeout)
            row['ffprobe_returncode'] = probe['returncode']
            row['ffprobe_stderr'] = probe['stderr']
            if probe['returncode']:
                row['errors'].append('FFPROBE_FAILED')
            else:
                info = json.loads(probe['stdout'])
                streams = info.get('streams', [])
                audio = [s for s in streams if s.get('codec_type') == 'audio']
                row['audio_stream_count'] = len(audio)
                row['non_audio_streams'] = [{'index': s.get('index'), 'codec_type': s.get('codec_type'),
                                            'attached_pic': s.get('disposition', {}).get('attached_pic')}
                                           for s in streams if s.get('codec_type') != 'audio']
                row['audio_streams'] = [{k: s.get(k) for k in ['index', 'codec_name', 'sample_fmt',
                                         'sample_rate', 'channels', 'channel_layout', 'duration', 'bit_rate']}
                                        for s in audio]
                row['format'] = {k: info.get('format', {}).get(k) for k in
                                 ['format_name', 'duration', 'size', 'bit_rate', 'start_time']}
                row['duration_seconds'] = positive_float(info.get('format', {}).get('duration'))
                if row['duration_seconds'] is None and audio:
                    row['duration_seconds'] = positive_float(audio[0].get('duration'))
                if not audio:
                    row['errors'].append('NO_AUDIO_STREAM')
                if row['duration_seconds'] is None:
                    row['errors'].append('INVALID_AUDIO_DURATION')
                if any(positive_float(s.get('sample_rate')) is None or not s.get('channels') for s in audio):
                    row['errors'].append('INVALID_SAMPLE_RATE_OR_CHANNEL_COUNT')
                if len(audio) > 1:
                    row['warnings'].append('MULTIPLE_AUDIO_STREAMS_REVIEW')
            # Decode all audio streams completely to the null muxer; no output audio is written.
            decoded = command([ffmpeg, '-hide_banner', '-nostdin', '-v', 'error', '-xerror',
                               '-i', str(path), '-map', '0:a', '-vn', '-sn', '-dn',
                               '-f', 'null', '-'], args.timeout)
            row['full_decode'] = {'returncode': decoded['returncode'], 'stderr': decoded['stderr'],
                                  'destination': 'null muxer only; no media file written',
                                  'complete_decode_success': decoded['returncode'] == 0 and not decoded['stderr'].strip()}
            if not row['full_decode']['complete_decode_success']:
                row['errors'].append('FULL_AUDIO_DECODE_FAILED_OR_ERROR_LOG')
        except (subprocess.TimeoutExpired, OSError, ValueError) as exc:
            row['errors'].append('TOOL_ERROR_OR_TIMEOUT')
            row['exception'] = str(exc)
        after = path.stat()
        row['mtime_ns_after'] = after.st_mtime_ns
        row['file_content_stable_during_verification'] = (
            before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns and
            row['sha256'] == sha256(path))
        if not row['file_content_stable_during_verification']:
            row['errors'].append('FILE_CHANGED_DURING_VERIFICATION')
        row['status'] = 'FAIL' if row['errors'] else 'PASS_TECHNICAL_ONLY'
    hashes = defaultdict(list)
    for row in report['items']:
        if row.get('sha256'):
            hashes[row['sha256']].append(row['basename'])
    duplicates = [{'sha256': h, 'basenames': names} for h, names in hashes.items() if len(names) > 1]
    for dup in duplicates:
        for row in report['items']:
            if row.get('sha256') == dup['sha256']:
                row['errors'].append('DUPLICATE_SHA256_DIFFERENT_EXPECTED_TEXTS')
                row['status'] = 'FAIL'
    report['duplicate_sha256_groups'] = duplicates
    unchanged = sha256(manifest_path) == manifest_hash
    report['manifest_unchanged'] = unchanged
    counts = Counter(row['status'] for row in report['items'])
    report['summary'] = {'expected_files': 24, 'existing_files': sum(row.get('exists', False) for row in report['items']),
                         'status_counts': dict(counts), 'duplicate_sha256_group_count': len(duplicates),
                         'total_duration_seconds': round(sum(row.get('duration_seconds') or 0 for row in report['items']), 6)}
    report['status'] = ('FAIL' if counts['FAIL'] or not unchanged else
                        'INCOMPLETE_MISSING_FILES' if counts['MISSING'] else 'PASS_TECHNICAL_ONLY')
    output = Path(args.report).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# 女版04—06新旁白技术核验', '', f'状态：{report["status"]}', '',
             '只核文件技术完整性，不证明朗读内容、音色身份或实际100%语速；本脚本未改动音频、源清单或制作进度。', '',
             '| 文件 | 状态 | 秒 | 采样率 | 音轨数 |', '|---|---|---:|---|---:|']
    for row in report['items']:
        rates = '/'.join(str(s.get('sample_rate')) for s in row.get('audio_streams', []))
        seconds = row.get('duration_seconds')
        lines.append(f'| {row["basename"]}.mp3 | {row["status"]} | {seconds if seconds is not None else "—"} | {rates or "—"} | {row.get("audio_stream_count", "—")} |')
    output.with_suffix('.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'status': report['status'], 'report': str(output), 'summary': report['summary']}, ensure_ascii=False))
    return 0 if report['status'] == 'PASS_TECHNICAL_ONLY' else 2

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', default=str(DEFAULT_MANIFEST))
    p.add_argument('--report', default=str(HERE / '24段音频技术验收.json'))
    p.add_argument('--progress', help='Optional read-only current production provenance JSON.')
    p.add_argument('--ffmpeg')
    p.add_argument('--ffprobe')
    p.add_argument('--timeout', type=float, default=180)
    args = p.parse_args()
    try:
        return verify(args)
    except Exception as exc:
        print(json.dumps({'status': 'PRECHECK_OR_TOOL_ERROR', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3

if __name__ == '__main__':
    raise SystemExit(main())
