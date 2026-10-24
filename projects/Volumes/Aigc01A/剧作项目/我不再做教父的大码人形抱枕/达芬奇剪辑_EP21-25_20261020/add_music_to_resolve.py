import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

BASE = Path(__file__).resolve().parent
PLAN = json.loads((BASE / '配乐/配乐执行计划.json').read_text(encoding='utf-8'))
BEFORE = json.loads((BASE / 'Resolve_保存重开_同期声最终核验.json').read_text(encoding='utf-8'))


def clip_state(item):
    media = item.GetMediaPoolItem()
    return {
        'start': item.GetStart(),
        'end': item.GetEnd(),
        'source_path': media.GetClipProperty('File Path') if media else None,
        'source_start': item.GetSourceStartFrame() if media else None,
    }


def ensure_preserved(timeline, reference):
    assert timeline.GetEndFrame() == reference['end']
    for kind in ['video', 'audio']:
        tracks = reference['tracks'][kind]
        assert timeline.GetTrackCount(kind) >= len(tracks)
        for track in tracks:
            actual = [clip_state(a) for a in timeline.GetItemListInTrack(kind, track['track']) or []]
            keys = ('start', 'end', 'source_path', 'source_start')
            expected = [{k: a[k] for k in keys} for a in track['items']]
            assert actual == expected, (timeline.GetName(), kind, track['track'], 'original edit changed')


r = get_resolve()
pm = r.GetProjectManager()
p = pm.GetCurrentProject()
assert p.GetName() == '大码枕头'
mp = p.GetMediaPool()
timelines = {p.GetTimelineByIndex(i).GetName(): p.GetTimelineByIndex(i)
             for i in range(1, p.GetTimelineCount() + 1)}
root = mp.GetRootFolder()
parent = next((f for f in root.GetSubFolderList() if f.GetName() == 'EP21-25_配乐_CC0'), None)
if not parent:
    parent = mp.AddSubFolder(root, 'EP21-25_配乐_CC0')
assert parent
assert mp.SetCurrentFolder(parent)
known_media = {c.GetClipProperty('File Path'): c for c in parent.GetClipList()}
all_cues = [cue for ep in PLAN['episodes'] for cue in ep['cues']]
for cue in all_cues:
    f = Path(cue['path'])
    assert hashlib.sha256(f.read_bytes()).hexdigest() == cue['sha256'], f
missing = [cue['path'] for cue in all_cues if cue['path'] not in known_media]
if missing:
    imported = mp.ImportMedia(missing)
    assert imported and len(imported) == len(missing)
    known_media.update({m.GetClipProperty('File Path'): m for m in imported})

result = {'project': p.GetName(), 'original_edit_preserved': True, 'episodes': [],
          'license_manifest': str(BASE / '配乐/配乐来源与授权.json'),
          'full_subjective_playback_claimed': False}
for episode in PLAN['episodes']:
    t = timelines[episode['timeline_name']]
    assert p.SetCurrentTimeline(t)
    reference = next(q for q in BEFORE['episodes'] if q['episode'] == episode['episode'])
    ensure_preserved(t, reference)
    if t.GetTrackCount('audio') == 3:
        assert t.AddTrack('audio', 'stereo')
    assert t.GetTrackCount('audio') == 4
    assert t.SetTrackName('audio', 4, '配乐_CC0_对白避让')
    assert t.SetTrackEnable('audio', 4, True)
    existing = t.GetItemListInTrack('audio', 4) or []
    if existing:
        expected = [{'start': c['record_frame'], 'end': c['record_frame'] + c['duration_frames'],
                     'source_path': c['path'], 'source_start': 0} for c in episode['cues']]
        assert [clip_state(a) for a in existing] == expected, 'Existing A4 does not match this plan'
    else:
        added = mp.AppendToTimeline([
            {'mediaPoolItem': known_media[c['path']], 'startFrame': 0,
             'endFrame': c['duration_frames'], 'recordFrame': c['record_frame'],
             'trackIndex': 4, 'mediaType': 2} for c in episode['cues']])
        assert added and len(added) == len(episode['cues'])
        for item, cue in zip(added, episode['cues']):
            assert item
            assert item.GetStart() == cue['record_frame']
            assert item.GetDuration() == cue['duration_frames']
            assert item.GetSourceStartFrame() == 0
            assert item.SetProperties({'AudioVolumeEnabled': True, 'AudioVolume': 0.0})
    ensure_preserved(t, reference)
    actual = t.GetItemListInTrack('audio', 4) or []
    for item in actual:
        assert item.GetClipEnabled()
        assert abs(item.GetProperties()['AudioVolume']) < 0.001
    q = {'episode': episode['episode'], 'timeline_name': t.GetName(),
         'track': 4, 'enabled': t.GetIsTrackEnabled('audio', 4),
         'music_clips': [dict(clip_state(a), properties=a.GetProperties()) for a in actual]}
    result['episodes'].append(q)
    assert pm.SaveProject()
    print(json.dumps({'episode': episode['episode'], 'music_cues': len(actual),
                      'original_edit_preserved': True}, ensure_ascii=False), flush=True)
(BASE / 'Resolve_配乐加入回读.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
assert pm.SaveProject()
print('Music imported and saved.', flush=True)
