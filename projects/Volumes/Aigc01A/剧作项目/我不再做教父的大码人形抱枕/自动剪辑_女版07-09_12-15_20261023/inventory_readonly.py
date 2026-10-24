from pathlib import Path
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor
import subprocess, json, re, hashlib, datetime

root = Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕')
base = root / '剧梦生成视频片段/女版/《人形抱枕》女版'
out = root / '自动剪辑_女版07-09_12-15_20261023'
probe = Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffprobe')
eps = [7, 8, 9, 12, 13, 14, 15]
paths = [p for kind in ['视频', '旁白'] for ep in eps
         for p in (base / kind / f'EP{ep:02d}').iterdir()
         if p.is_file() and p.suffix.lower() in ['.mp4', '.mp3', '.wav', '.mov', '.m4a']]

def natural_key(p):
    return [int(s) if s.isdigit() else s for s in re.split('(\\d+)', str(p))]

def read(p):
    r = subprocess.run([str(probe), '-v', 'error', '-show_format', '-show_streams',
                        '-of', 'json', str(p)], capture_output=True, text=True, timeout=40)
    raw = json.loads(r.stdout) if r.returncode == 0 else {}
    s = raw.get('streams', [])
    video = [x for x in s if x.get('codec_type') == 'video'
             and not x.get('disposition', {}).get('attached_pic')]
    audio = [x for x in s if x.get('codec_type') == 'audio']
    ep = int(p.parent.name[2:])
    kind = 'video' if p.parent.parent.name == '视频' else 'narration'
    match = re.search(r'(\d+)-(\d+)(?:-(\d+))?$', p.stem)
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(8*1024*1024), b''):
            h.update(chunk)
    def num(x):
        try: return float(x)
        except (ValueError, TypeError): return None
    def fps(x):
        try:
            n, d = x.split('/')
            return float(n) / float(d) if float(d) else None
        except (ValueError, TypeError): return None
    return {
        'episode': ep, 'kind': kind, 'filename': p.name,
        'path': str(p), 'resolved_path': str(p.resolve()),
        'size_bytes': p.stat().st_size, 'sha256': h.hexdigest(),
        'group_or_segment': int(match[2]) if match else None,
        'version_number': int(match[3]) if match and match[3] else None,
        'episode_in_filename': int(match[1]) if match else None,
        'probe_returncode': r.returncode, 'probe_error': r.stderr.strip() or None,
        'duration_seconds': num(raw.get('format', {}).get('duration')),
        'video_stream_count': len(video), 'audio_stream_count': len(audio),
        'subtitle_stream_count': sum(x.get('codec_type') == 'subtitle' for x in s),
        'video_streams': [dict(index=x.get('index'), codec=x.get('codec_name'),
                               width=x.get('width'), height=x.get('height'),
                               avg_frame_rate=x.get('avg_frame_rate'),
                               fps=fps(x.get('avg_frame_rate')),
                               duration_seconds=num(x.get('duration')),
                               nb_frames=x.get('nb_frames'),
                               pixel_format=x.get('pix_fmt')) for x in video],
        'audio_streams': [dict(index=x.get('index'), codec=x.get('codec_name'),
                               channels=x.get('channels'),
                               sample_rate=x.get('sample_rate'),
                               duration_seconds=num(x.get('duration')),
                               start_time=num(x.get('start_time')),
                               channel_layout=x.get('channel_layout')) for x in audio],
    }

with ThreadPoolExecutor(max_workers=4) as pool:
    rows = list(pool.map(read, sorted(paths, key=natural_key)))
by_hash = defaultdict(list)
for r in rows: by_hash[r['sha256']].append(r['path'])
episodes = []
for ep in eps:
    videos = [r for r in rows if r['episode'] == ep and r['kind'] == 'video']
    narr = [r for r in rows if r['episode'] == ep and r['kind'] == 'narration']
    grouped = defaultdict(list)
    for r in videos: grouped[r['group_or_segment']].append(r)
    groups = []
    for group in sorted(grouped):
        vr = sorted(grouped[group], key=lambda x: x['version_number'] or 0)
        groups.append({'group': group, 'versions': [x['version_number'] for x in vr],
                       'paths_in_version_order': [x['path'] for x in vr],
                       'durations_seconds': [x['duration_seconds'] for x in vr],
                       'identical_hash': len(set(x['sha256'] for x in vr)) == 1})
    nums = sorted(grouped)
    ns = sorted(r['group_or_segment'] for r in narr)
    episodes.append({
        'episode': ep, 'video_directory': str(base/'视频'/f'EP{ep:02d}'),
        'narration_directory': str(base/'旁白'/f'EP{ep:02d}'),
        'video_count': len(videos), 'video_group_count': len(groups),
        'video_group_numbers': nums,
        'video_number_gaps_within_observed_range': [x for x in range(1, max(nums)+1) if x not in nums],
        'video_groups': groups, 'narration_count': len(narr), 'narration_numbers': ns,
        'narration_number_gaps_within_observed_range': [x for x in range(1, max(ns)+1) if x not in ns],
        'narration_paths_in_order': [r['path'] for r in sorted(narr, key=lambda x:x['group_or_segment'])],
        'narration_durations_in_order': [r['duration_seconds'] for r in sorted(narr, key=lambda x:x['group_or_segment'])],
        'narration_total_seconds': round(sum(r['duration_seconds'] or 0 for r in narr), 6),
        'video_total_all_versions_seconds': round(sum(r['duration_seconds'] or 0 for r in videos), 6),
        'video_total_first_version_seconds': round(sum(g['durations_seconds'][0] or 0 for g in groups), 6),
        'video_without_audio': [r['path'] for r in videos if not r['audio_stream_count']],
        'filename_episode_mismatches': [r['path'] for r in videos+narr if r['episode_in_filename'] != ep],
    })
result = {
    'created_at': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
    'scope': 'Read-only inventory of the exact user-supplied female EP07,08,09,12,13,14,15 video/narration folder. Source files not modified. No Resolve or browser operation.',
    'project_root': str(root), 'source_root': str(base), 'ffprobe_path': str(probe),
    'episodes': episodes, 'files': rows,
    'total': {'video_files': sum(r['kind']=='video' for r in rows),
              'video_groups': sum(e['video_group_count'] for e in episodes),
              'narration_files': sum(r['kind']=='narration' for r in rows),
              'narration_seconds': round(sum(e['narration_total_seconds'] for e in episodes),6)},
    'exact_duplicate_groups': [{'sha256': h, 'paths': paths} for h, paths in by_hash.items() if len(paths)>1],
    'probe_failures': [r for r in rows if r['probe_returncode']],
    'limits': ['Filename order and stream presence do not validate script coverage, speech completeness, lip sync or best version.',
               'Alternative versions are recorded, not automatically selected by highest filename number.',
               'Narration and video group counts may differ because dialogue-only groups may have no narration.']
}
out.mkdir(exist_ok=True)
(out/'素材盘点.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({'total': result['total'], 'episodes': [{k:e[k] for k in ['episode','video_count','video_group_count','narration_count','narration_total_seconds','video_without_audio','video_number_gaps_within_observed_range','narration_number_gaps_within_observed_range']} for e in episodes], 'duplicates':len(result['exact_duplicate_groups']), 'probe_failures':len(result['probe_failures'])},ensure_ascii=False,indent=2))
