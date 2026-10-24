"""Read-only official Resolve SDK audit; no current-timeline, UI, or setter calls."""
import datetime
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

ROOT = Path(__file__).resolve().parents[1]
BASES = [ROOT / '11集剪辑工作版_最终实读.json', ROOT / '字幕/依据/11集剪辑工作版_生成SRT使用的最终实读.json']
baselines = [json.loads(p.read_text(encoding='utf-8')) for p in BASES]
r = get_resolve()
p = r.GetProjectManager().GetCurrentProject()
assert p and p.GetName() == baselines[0]['project']
timelines = {}
for i in range(1, p.GetTimelineCount() + 1):
    t = p.GetTimelineByIndex(i)
    timelines[t.GetUniqueId()] = t

snapshot = {'project': p.GetName(), 'read_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'read_only': True, 'episodes': []}
for e in baselines[0]['episodes']:
    t = timelines.get(e['id'])
    if not t:
        snapshot['episodes'].append({'episode': e['episode'], 'missing_timeline': True, 'id': e['id']})
        continue
    a = {'episode': e['episode'], 'timeline': t.GetName(), 'id': t.GetUniqueId(), 'start': t.GetStartFrame(), 'end': t.GetEndFrame(), 'fps': t.GetSetting('timelineFrameRate'), 'tracks': {}}
    fps = float(a['fps'])
    for kind in ('video', 'audio'):
        a['tracks'][kind] = []
        for index in range(1, t.GetTrackCount(kind) + 1):
            track = {'index': index, 'name': t.GetTrackName(kind, index), 'enabled': t.GetIsTrackEnabled(kind, index), 'items': []}
            for x in t.GetItemListInTrack(kind, index) or []:
                m = x.GetMediaPoolItem()
                item = {'name': x.GetName(), 'start': x.GetStart(), 'end': x.GetEnd(), 'duration': x.GetDuration(), 'source_path': m.GetClipProperty('File Path') if m else None, 'source_start': x.GetSourceStartTime(), 'source_end': x.GetSourceEndTime(), 'properties': x.GetProperty(), 'enabled': x.GetClipEnabled()}
                duration_seconds = item['duration'] / fps
                if duration_seconds and item['source_start'] is not None and item['source_end'] is not None:
                    item['derived_average_speed_percent'] = (item['source_end'] - item['source_start']) / duration_seconds * 100
                track['items'].append(item)
            a['tracks'][kind].append(track)
    snapshot['episodes'].append(a)

def equal(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-7, abs_tol=1e-5)
    return a == b

reports = []
for basepath, base in zip(BASES, baselines):
    report = {'baseline': str(basepath), 'episode_results': [], 'differences': []}
    for old, cur in zip(base['episodes'], snapshot['episodes']):
        before = len(report['differences'])
        ep = old['episode']
        def difference(where, was, now):
            report['differences'].append({'episode': ep, 'location': where, 'baseline': was, 'current': now})
        if cur.get('missing_timeline'):
            difference('timeline', old['id'], 'missing')
            continue
        for key in ('timeline', 'id', 'start', 'end'):
            if not equal(old[key], cur[key]):
                difference(key, old[key], cur[key])
        for kind in ('video', 'audio'):
            oldtracks = old['tracks'][kind]
            newtracks = cur['tracks'][kind]
            if len(oldtracks) != len(newtracks):
                difference(kind + '.track_count', len(oldtracks), len(newtracks))
            for ot, nt in zip(oldtracks, newtracks):
                label = f'{kind}.track{ot["index"]}'
                for key in ('name', 'enabled'):
                    if not equal(ot[key], nt[key]):
                        difference(label + '.' + key, ot[key], nt[key])
                if len(ot['items']) != len(nt['items']):
                    difference(label + '.item_count', len(ot['items']), len(nt['items']))
                for num, (oi, ni) in enumerate(zip(ot['items'], nt['items']), 1):
                    ilabel = f'{label}.item{num}[{oi["name"]}@{oi["start"]}]'
                    for key in ('name', 'start', 'end', 'duration', 'source_path', 'source_start', 'source_end', 'enabled'):
                        if not equal(oi.get(key), ni.get(key)):
                            difference(ilabel + '.' + key, oi.get(key), ni.get(key))
                    for key in sorted(set(oi['properties']) | set(ni['properties'])):
                        if not equal(oi['properties'].get(key), ni['properties'].get(key)):
                            difference(ilabel + '.properties.' + key, oi['properties'].get(key), ni['properties'].get(key))
        report['episode_results'].append({'episode': ep, 'difference_count': len(report['differences']) - before, 'video_items': sum(len(t['items']) for t in cur['tracks']['video']), 'audio_items': sum(len(t['items']) for t in cur['tracks']['audio'])})
    reports.append(report)

focus = []
for e in snapshot['episodes']:
    if e['episode'] == 22:
        for tr in e.get('tracks', {}).get('video', []):
            for item in tr['items']:
                if '22-07-01' in item['name']:
                    focus.append(item)

for report in reports:
    report['confirmed_av_differences'] = []
    report['unverified_track_enabled_values'] = []
    report['unavailable_advanced_audio_properties'] = []
    for d in report['differences']:
        key = d['location'].rsplit('.', 1)[-1]
        if d['current'] is None and key.startswith(('AudioDialogue', 'AudioVoice')):
            report['unavailable_advanced_audio_properties'].append(d)
        elif d['location'].endswith('.enabled') and '.item' not in d['location']:
            report['unverified_track_enabled_values'].append(d)
        else:
            report['confirmed_av_differences'].append(d)
result = {'read_at': snapshot['read_at'], 'read_only': True, 'baselines_identical': baselines[0] == baselines[1], 'reports': reports, 'ep22_07_01_current': focus, 'limits': ['Subtitle track changes intentionally excluded.', 'Speed is derived average from source range / record duration; SDK does not expose a separate native speed or retime-curve getter.', 'Track enabled is false on every non-current-timeline track, and eight advanced audio properties are absent on every non-current-timeline audio clip. This consistent context pattern is not classified as proven mute/style changes; actual non-current track enable and advanced audio settings remain unconfirmed without activating those timelines.', 'Audio mixer bus/track faders are not exposed by this read.']}
snapfile = ROOT / '字幕排查_当前AV只读实读_20261021.json'
reportfile = ROOT / '字幕排查_只读AV差异_20261021.json'
snapfile.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding='utf-8')
reportfile.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'report': str(reportfile), 'baseline_identical': result['baselines_identical'], 'confirmed_av_differences': reports[0]['confirmed_av_differences'], 'unverified_track_enabled_count': len(reports[0]['unverified_track_enabled_values']), 'unavailable_advanced_audio_property_count': len(reports[0]['unavailable_advanced_audio_properties']), 'ep22_07_01_current': focus}, ensure_ascii=False, indent=2), flush=True)
