"""Read-only FFmpeg whole-stream loudness/true-peak measurement, never rewrites audio."""
import datetime
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from native_common import BASE, read_json, selected_narration, sha256, write_json

FF = Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg')
assert FF.is_file()
selected, pending = selected_narration(require_all=True)
inventory = read_json(BASE / '准备/media_inventory.json')
selection_hash = sha256(BASE / 'ASR/旁白采用清单.json')
rows = [{'path': x['path'], 'episode': ep['episode'], 'kind': 'video'}
        for ep in inventory['episodes'] for x in ep['videos']]
rows.extend({'path': path, 'episode': int(logical.split('枕头')[1].split('-')[0]), 'kind': 'narration'}
            for logical, path in selected.items())
log_root = BASE / 'ASR/source_levels'


def last(pattern, text):
    matches = re.findall(pattern, text, re.MULTILINE)
    if not matches or matches[-1] in ['-inf', 'inf', 'nan']:
        return None
    return float(matches[-1])


def one(row):
    path = Path(row['path'])
    started = time.monotonic()
    original_hash = sha256(path)
    # EBU measurement precedes volumedetect's required signed-16 conversion so
    # decoded AAC/MP3 samples above full scale are not clipped before true-peak QC.
    command = [str(FF), '-nostdin', '-hide_banner', '-nostats', '-i', str(path), '-vn',
               '-af', 'ebur128=peak=true,volumedetect', '-f', 'null', '-']
    process = subprocess.run(command, capture_output=True, text=True, timeout=180)
    assert process.returncode == 0, process.stderr[-2000:]
    assert original_hash == sha256(path), 'Source changed while measuring'
    folder = log_root / ('EP%d' % row['episode']) / row['kind']
    folder.mkdir(parents=True, exist_ok=True)
    logfile = folder / (path.stem + '.log')
    logfile.write_text(process.stderr, encoding='utf-8')
    item = dict(row, source_path=str(path), source_sha256=original_hash,
                integrated_loudness_lufs=last(r'^\s*I:\s*([-+\d.inf]+)\s*LUFS', process.stderr),
                true_peak_dbfs=last(r'^\s*Peak:\s*([-+\d.inf]+)\s*dBFS', process.stderr),
                loudness_range_lu=last(r'^\s*LRA:\s*([-+\d.inf]+)\s*LU', process.stderr),
                mean_volume_dbfs=last(r'mean_volume:\s*([-+\d.inf]+)\s*dB', process.stderr),
                max_volume_dbfs=last(r'max_volume:\s*([-+\d.inf]+)\s*dB', process.stderr),
                analysis_log=str(logfile), runtime_seconds=round(time.monotonic() - started, 3),
                source_unchanged=True, gain_applied=False)
    loudness = item['integrated_loudness_lufs']
    peak = item['true_peak_dbfs']
    candidates = [0]
    if peak is not None:
        candidates.append(-2 - peak)
    if loudness is not None:
        candidates.append((-17 if row['kind'] == 'narration' else -18) - loudness)
    speech = round(min(candidates), 2)
    item.update(suggested_speech_gain_db=speech,
                suggested_ambience_under_vo_gain_db=min(speech, -12),
                suggested_gain_never_boosts=True)
    return item


def main():
    completed = []
    errors = []
    output = BASE / 'ASR/source_levels.json'
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(one, row): row for row in rows}
        for future in as_completed(futures):
            row = futures[future]
            try:
                completed.append(future.result())
            except Exception as error:
                errors.append(dict(row, error=repr(error)))
            if (len(completed) + len(errors)) % 10 == 0 or len(completed) + len(errors) == len(rows):
                print(json.dumps({'completed': len(completed), 'errors': len(errors), 'total': len(rows)}), flush=True)
    result = {'created_at': datetime.datetime.now().isoformat(), 'source_count': len(rows),
              'completed': len(completed), 'errors': errors, 'selection_sha256': selection_hash,
              'selection_unchanged': sha256(BASE / 'ASR/旁白采用清单.json') == selection_hash,
              'method': 'FFmpeg EBU R128 integrated loudness and true peak before volumedetect signed-16 conversion; entire original audio stream.',
              'source_files_not_modified': True, 'gain_not_applied': True,
              'cautions': ['全源文件响度含静默、环境或原背景声，不等同独立对白响度。',
                           '建议对白增益仅衰减至-18LUFS及-2dBTP上限，不自动额外压低；VO目标-17LUFS/-2dBTP。',
                           'VO期间环境同期声建议至少衰减12dB；真实对白期间使用对白建议值并留出VO间隙。',
                           '测量不证明口型同步、台词完整、说话人身份或最终混音听感。'],
              'files': sorted(completed, key=lambda x: (x['episode'], x['kind'], x['path']))}
    write_json(output, result)
    assert len(completed) == 75 and not errors
    print(json.dumps({'output': str(output), 'completed': len(completed),
                      'positive_true_peak_sources': sum(x['true_peak_dbfs'] is not None and x['true_peak_dbfs'] > 0 for x in completed),
                      'gain_applied': False, 'selection_unchanged': result['selection_unchanged']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
