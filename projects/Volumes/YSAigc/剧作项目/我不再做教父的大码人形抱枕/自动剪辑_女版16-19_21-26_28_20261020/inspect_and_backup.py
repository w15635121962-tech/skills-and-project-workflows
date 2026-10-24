import json, re, sys
from pathlib import Path

sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

OUT = Path(__file__).resolve().parent
BACK = OUT / '备份'
BACK.mkdir(exist_ok=True)
r = get_resolve()
pm = r.GetProjectManager()
p = pm.GetCurrentProject()
assert p and p.GetName() == '大码枕头'
original = p.GetCurrentTimeline()
tc = original.GetCurrentTimecode()
backup = BACK / '大码枕头_女版11集自动剪辑前完整备份.drp'
if not backup.exists():
    assert pm.SaveProject()
    assert pm.ExportProject(p.GetName(), str(backup))
else:
    assert backup.stat().st_size > 0
report = {'project': p.GetName(), 'current': original.GetName(), 'timecode': tc,
          'backup': str(backup), 'all_timelines': [], 'targets': [], 'media': []}
for idx in range(1, p.GetTimelineCount() + 1):
    t = p.GetTimelineByIndex(idx)
    name = t.GetName()
    report['all_timelines'].append({'index': idx, 'name': name, 'id': t.GetUniqueId()})
    if not re.fullmatch(r'大码_女版_EP(?:1[6-9]|2[1-6]|28)(?:_.*)?', name):
        continue
    assert p.SetCurrentTimeline(t)
    row = {'name': name, 'id': t.GetUniqueId(), 'start': t.GetStartFrame(),
           'end': t.GetEndFrame(), 'settings': t.GetSettings(), 'tracks': {}}
    for kind in ['video', 'audio', 'subtitle']:
        row['tracks'][kind] = []
        for j in range(1, t.GetTrackCount(kind) + 1):
            track = {'index': j, 'name': t.GetTrackName(kind, j),
                     'enabled': t.GetIsTrackEnabled(kind, j), 'locked': t.GetIsTrackLocked(kind, j), 'items': []}
            for item in t.GetItemListInTrack(kind, j) or []:
                m = item.GetMediaPoolItem()
                track['items'].append({'id': item.GetUniqueId(), 'name': item.GetName(),
                    'start': item.GetStart(), 'end': item.GetEnd(), 'duration': item.GetDuration(),
                    'source_start': item.GetSourceStartFrame() if m else None,
                    'source_end': item.GetSourceEndFrame() if m else None,
                    'source_path': m.GetClipProperty('File Path') if m else None,
                    'media_properties': m.GetClipProperty() if m else None,
                    'properties': item.GetProperties(), 'enabled': item.GetClipEnabled()})
            row['tracks'][kind].append(track)
    row['drt'] = str(BACK / (name + '_操作前.drt'))
    if not Path(row['drt']).exists():
        assert t.Export(row['drt'], r.EXPORT_DRT)
    otio = BACK / (name + '_操作前.otio')
    row['otio_exported'] = otio.exists() or t.Export(str(otio), r.EXPORT_OTIO)
    report['targets'].append(row)
    print(json.dumps({'name': name, 'duration_frames': row['end'] - row['start'],
          'tracks': {k: [{'name': x['name'], 'items': len(x['items'])} for x in v] for k, v in row['tracks'].items()}}, ensure_ascii=False), flush=True)

def walk(folder, parent=''):
    path = parent + '/' + folder.GetName()
    for m in folder.GetClipList() or []:
        props = m.GetClipProperty()
        report['media'].append({'folder': path, 'id': m.GetUniqueId(), 'name': m.GetName(), 'properties': props})
    for sub in folder.GetSubFolderList() or []:
        walk(sub, path)

walk(p.GetMediaPool().GetRootFolder())
assert p.SetCurrentTimeline(original)
assert original.SetCurrentTimecode(tc)
(OUT / 'Resolve_操作前实时实读.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('BACKUP_AND_SNAPSHOT_COMPLETE', len(report['targets']), len(report['media']), backup.stat().st_size, flush=True)
