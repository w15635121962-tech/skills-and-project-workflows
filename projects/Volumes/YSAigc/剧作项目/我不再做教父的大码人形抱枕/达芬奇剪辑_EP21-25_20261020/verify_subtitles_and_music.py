import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

BASE = Path(__file__).resolve().parent
MUSIC = json.loads((BASE / '配乐/配乐执行计划.json').read_text(encoding='utf-8'))
BEFORE = json.loads((BASE / 'Resolve_保存重开_同期声最终核验.json').read_text(encoding='utf-8'))
ORIGINAL = json.loads((BASE / 'Resolve_操作前完整实读.json').read_text(encoding='utf-8'))


def read_srt(ep):
    def frame(tc):
        h, m, s, ms = map(int, re.split('[:,]', tc))
        return round((((h * 60 + m) * 60 + s) + ms / 1000) * 24)
    path = BASE / 'SRT' / f'EP{ep}.srt'
    result = []
    for block in path.read_text(encoding='utf-8-sig').strip().split('\n\n'):
        lines = block.splitlines()
        start, end = lines[1].split(' --> ')
        result.append({'start': frame(start), 'end': frame(end), 'text': '\n'.join(lines[2:])})
    return result


def normalized(text):
    return text.replace('\u2028', '\n').replace('\r\n', '\n').strip()


def state(item):
    m = item.GetMediaPoolItem()
    return {'name': item.GetName(), 'start': item.GetStart(), 'end': item.GetEnd(),
            'source_path': m.GetClipProperty('File Path') if m else None,
            'source_start': item.GetSourceStartFrame() if m else None,
            'properties': item.GetProperties(), 'enabled': item.GetClipEnabled()}


r = get_resolve()
pm = r.GetProjectManager()
p = pm.GetCurrentProject()
assert p.GetName() == '大码枕头'
assert pm.SaveProject()
assert pm.CloseProject(p)
p = pm.LoadProject('大码枕头')
assert p
timelines = {p.GetTimelineByIndex(i).GetName(): p.GetTimelineByIndex(i)
             for i in range(1, p.GetTimelineCount() + 1)}
report = {'project': p.GetName(), 'saved_closed_and_reloaded': True,
          'original_picture_and_audio_preserved': True, 'original_seven_timelines_preserved': True,
          'all_mp4_source_audio_coverage': '100%', 'episodes': [],
          'full_normal_speed_audiovisual_audition_claimed': False}

for ep in MUSIC['episodes']:
    t = timelines[ep['timeline_name']]
    assert p.SetCurrentTimeline(t)
    reference = next(q for q in BEFORE['episodes'] if q['episode'] == ep['episode'])
    assert t.GetEndFrame() == reference['end']
    assert t.GetTrackCount('video') == 1, 'An unintended overlay track remains'
    assert t.GetTrackCount('audio') == 4
    q = {'episode': ep['episode'], 'timeline_name': t.GetName(), 'end': t.GetEndFrame(), 'tracks': {}}
    for kind in ['video', 'audio', 'subtitle']:
        q['tracks'][kind] = []
        for i in range(1, t.GetTrackCount(kind) + 1):
            if kind == 'subtitle':
                assert t.SetTrackEnable(kind, i, True)
            enabled = t.GetIsTrackEnabled(kind, i)
            assert enabled, (ep['episode'], kind, i, 'disabled track')
            items = [state(a) for a in t.GetItemListInTrack(kind, i) or []]
            assert all(a['enabled'] for a in items)
            q['tracks'][kind].append({'track': i, 'name': t.GetTrackName(kind, i),
                                      'enabled': enabled, 'items': items})
    for kind in ['video', 'audio']:
        for old in reference['tracks'][kind]:
            actual = q['tracks'][kind][old['track'] - 1]['items']
            assert len(actual) == len(old['items'])
            for a, b in zip(actual, old['items']):
                for key in ['start', 'end', 'source_path', 'source_start']:
                    assert a[key] == b[key], (ep['episode'], kind, key, 'original clip changed')
                if kind == 'audio':
                    assert a['properties']['AudioVolume'] == b['properties']['AudioVolume']
    expected_cues = read_srt(ep['episode'])
    actual_cues = sorted([a for tr in q['tracks']['subtitle'] for a in tr['items']], key=lambda a: a['start'])
    assert len(actual_cues) == len(expected_cues), (ep['episode'], len(actual_cues), 'subtitle count')
    for a, b in zip(actual_cues, expected_cues):
        assert a['start'] == b['start'] and a['end'] == b['end'], (ep['episode'], b, 'subtitle time mismatch')
        assert normalized(a['name']) == normalized(b['text']), (ep['episode'], b, 'subtitle text mismatch')
    q['native_srt_cues'] = len(actual_cues)
    actual_music = q['tracks']['audio'][3]['items']
    assert len(actual_music) == len(ep['cues'])
    for a, b in zip(actual_music, ep['cues']):
        assert a['source_path'] == b['path'] and a['source_start'] == 0
        assert a['start'] == b['record_frame'] and a['end'] == b['record_frame'] + b['duration_frames']
        assert abs(a['properties']['AudioVolume']) < 0.001
    for v in q['tracks']['video'][0]['items']:
        if not v['source_path'].lower().endswith('.mp4'):
            continue
        spans = []
        for tr in q['tracks']['audio'][:3]:
            for a in tr['items']:
                if a['source_path'] == v['source_path'] and a['source_start'] - a['start'] == v['source_start'] - v['start']:
                    left, right = max(a['start'], v['start']), min(a['end'], v['end'])
                    if left < right:
                        spans.append((left, right))
        cursor = v['start']
        for left, right in sorted(spans):
            assert left == cursor
            cursor = right
        assert cursor == v['end']
    report['episodes'].append(q)
    print(json.dumps({'episode': ep['episode'], 'native_srt': len(actual_cues),
                      'music_cues': len(actual_music), 'audio_tracks_enabled': 4,
                      'source_audio_coverage': '100%'}, ensure_ascii=False), flush=True)

for old in ORIGINAL['timelines']:
    t = timelines[old['name']]
    assert p.SetCurrentTimeline(t)
    assert t.GetEndFrame() == old['end']
    for kind in ['video', 'audio', 'subtitle']:
        assert t.GetTrackCount(kind) == len(old['tracks'][kind])
        for track in old['tracks'][kind]:
            actual = t.GetItemListInTrack(kind, track['track']) or []
            assert len(actual) == track['count']
            for a, b in zip(actual, track['items']):
                now = state(a)
                for key in ['start', 'end', 'source_path']:
                    assert now[key] == b[key], (old['name'], kind, 'original timeline changed')

for episode in report['episodes']:
    t = timelines[episode['timeline_name']]
    assert p.SetCurrentTimeline(t)
    path = BASE / (t.GetName() + '_SRT与配乐完成.drt')
    assert not path.exists(), path
    assert t.Export(str(path), r.EXPORT_DRT)
    episode['drt'] = str(path)

assert p.SetCurrentTimeline(timelines[MUSIC['episodes'][0]['timeline_name']])
assert p.GetCurrentTimeline().SetCurrentTimecode('00:00:01:12')
assert r.OpenPage('edit')
assert pm.SaveProject()
drp = BASE / '大码枕头_EP21-25_SRT与配乐完成.drp'
assert not drp.exists(), drp
assert pm.ExportProject(p.GetName(), str(drp), True)
report['project_backup'] = str(drp)
report['native_srt_total'] = sum(x['native_srt_cues'] for x in report['episodes'])
assert report['native_srt_total'] == 152
report['music_cues_total'] = 12
report['srt_files'] = [{'path': str(f), 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()}
                       for f in sorted((BASE / 'SRT').glob('EP*.srt'))]
(BASE / 'Resolve_字幕配乐最终核验.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
(BASE / '待解锁恢复状态.json').write_text(json.dumps({
    'status': 'native_edit_full_sync_native_srt_and_cc0_music_completed',
    'project': p.GetName(), 'episodes': [21, 22, 23, 24, 25],
    'native_srt_cues': 152, 'music_cues_on_a4': 12, 'music_tracks_cc0': 4,
    'verified_native_mp4_segments': 89, 'matching_source_audio_coverage': '100%',
    'saved_closed_and_reloaded': True, 'all_audio_tracks_enabled': True,
    'original_seven_timelines_unchanged': True, 'final_project_backup': str(drp),
    'verification': 'Resolve_字幕配乐最终核验.json',
    'full_normal_speed_audiovisual_mix_and_source_lip_sync_review_completed': False,
    'final_render_started': False}, ensure_ascii=False, indent=2), encoding='utf-8')
print('Native SRT and music saved, reloaded, verified, and backed up.', flush=True)
