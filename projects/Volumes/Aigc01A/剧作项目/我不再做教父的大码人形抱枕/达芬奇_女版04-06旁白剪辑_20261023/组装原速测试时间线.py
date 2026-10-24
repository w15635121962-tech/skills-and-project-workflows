from pathlib import Path
import json
import math
import hashlib
import sys

sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

ROOT = Path(__file__).resolve().parent
SELECT = ROOT.parent / '女版04-06_新旁白_20261023/最终采用清单.json'
selected = json.loads(SELECT.read_text(encoding='utf-8'))['files']
pcm = json.loads((ROOT / 'PCM_原速准备清单.json').read_text(encoding='utf-8'))
assert pcm['status'] == 'PASS_24_FULL_COVERAGE_PCM_READY'
by_name = {x['basename']: x for x in pcm['items']}
assert len(by_name) == 24
for row in selected:
    prepared = by_name[row['basename']]
    assert hashlib.sha256(Path(prepared['output_path']).read_bytes()).hexdigest() == prepared['output_sha256']

r = get_resolve()
pm = r.GetProjectManager()
p = pm.GetCurrentProject()
assert p.GetName() == '大码枕头'
pool = p.GetMediaPool()
prep = next(p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)
            if p.GetTimelineByIndex(i).GetName() == '女版04-06_原音频与音量准备_20261023')
assert p.SetCurrentTimeline(prep)
folder = next(f for f in pool.GetRootFolder().GetSubFolderList()
              if f.GetName() == '女版04-06_原速旁白剪辑_20261023')
assert pool.SetCurrentFolder(folder)
sources = {x.GetClipProperty('File Path'): x for x in folder.GetClipList() or []}
existing = prep.GetItemListInTrack('audio', 1) or []
assert len(existing) in (2, 24)
assert [x.GetMediaPoolItem().GetClipProperty('File Path') for x in existing] == [x['audio_file'] for x in selected[:len(existing)]]
cursor = existing[-1].GetEnd(True)
preparation_rows = []
for index, row in enumerate(selected):
    if index < len(existing):
        item = existing[index]
    else:
        result = pool.AppendToTimeline([{'mediaPoolItem': sources[row['audio_file']],
                                        'recordFrame': cursor, 'mediaType': 2, 'trackIndex': 1}])
        assert result and len(result) == 1
        item = result[0]
    gain = by_name[row['basename']]['gain_db']
    assert item.SetProperty('AudioVolume', gain)
    assert abs(item.GetProperty('AudioVolume') - gain) < .011
    assert abs(item.GetSourceStartTime()) < 1e-6
    assert abs(item.GetDuration(True) / 30 - row['duration_seconds']) < 1 / 48000
    cursor = item.GetEnd(True)
    preparation_rows.append({'basename': row['basename'], 'path': row['audio_file'],
                             'gain_db': gain, 'start': item.GetStart(True), 'end': cursor})
assert len(prep.GetItemListInTrack('audio', 1)) == 24

working = next((f for f in folder.GetSubFolderList() or [] if f.GetName() == '三集原速旁白测试'), None)
if working is None:
    working = pool.AddSubFolder(folder, '三集原速旁白测试')
assert working and pool.SetCurrentFolder(working)
existing_media = {x.GetClipProperty('File Path'): x for x in working.GetClipList() or []}
paths = [by_name[x['basename']]['output_path'] for x in selected]
if all(path in existing_media for path in paths):
    media = [existing_media[path] for path in paths]
else:
    assert not any(path in existing_media for path in paths)
    media = pool.ImportMedia(paths)
assert media and len(media) == 24
media_by_path = {x.GetClipProperty('File Path'): x for x in media}
result = {'project': p.GetName(), 'preparation_timeline': prep.GetName(),
          'preparation_rows': preparation_rows, 'timelines': [],
          'rate': 1.0, 'original_timelines_modified': False,
          'editing_policy': 'Full-source word-complete files in original narration order. Preserve natural pauses; no internal speech cuts.',
          'auditory_listening_verified': False}
for episode in (4, 5, 6):
    name = f'大码_女版_EP{episode:02d}_新旁白原速测试_20261023'
    timeline = next((p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)
                     if p.GetTimelineByIndex(i).GetName() == name), None)
    if timeline is None:
        timeline = pool.CreateEmptyTimeline(name)
    else:
        assert any(x.GetName() == name for x in working.GetClipList() or [])
        assert all(not timeline.GetItemListInTrack(k, n) for k in ('audio', 'video')
                   for n in range(1, timeline.GetTrackCount(k) + 1))
    assert timeline and p.SetCurrentTimeline(timeline)
    assert timeline.SetSetting('useCustomSettings', '1')
    assert timeline.SetSetting('timelineFrameRate', '30')
    assert timeline.SetStartTimecode('00:00:00:00')
    assert not timeline.GetItemListInTrack('audio', 1)
    assert timeline.AddTrack('audio', 'mono')
    assert timeline.DeleteTrack('audio', 1)
    assert timeline.GetTrackSubType('audio', 1) == 'mono'
    assert timeline.SetTrackName('audio', 1, f'第{episode}集_女主新旁白_原速')
    cursor = 0.0
    record = {'episode': episode, 'name': name, 'id': timeline.GetUniqueId(), 'fps': 30,
              'track_name': timeline.GetTrackName('audio', 1), 'clips': [], 'joins': []}
    for row in [x for x in selected if x['episode'] == episode]:
        source = by_name[row['basename']]
        clip = media_by_path[source['output_path']]
        added = pool.AppendToTimeline([{'mediaPoolItem': clip, 'mediaType': 2,
                                       'trackIndex': 1, 'recordFrame': cursor}])
        assert added and len(added) == 1
        item = added[0]
        assert abs(item.GetStart(True) - cursor) < 1e-5
        assert abs(item.GetSourceStartTime()) < 1e-6
        assert abs(item.GetDuration(True) / 30 - source['output_duration_seconds']) < 1 / 48000
        assert item.SetName(row['basename'] + '_新旁白_原速')
        assert item.SetClipColor('Green')
        assert abs(item.GetProperty('AudioVolume')) < .001
        assert not item.GetProperty('AudioDialogueLevelerEnabled')
        assert not item.GetProperty('AudioVoiceIsolationEnabled')
        assert timeline.AddMarker(round(cursor), 'Blue', f'{row["sequence"]:02d} | {row["basename"]}',
                                  row['generation_text'], 1, row['sha256'])
        out = {'basename': row['basename'], 'sequence': row['sequence'], 'take': row['take'],
               'timeline_item_name': item.GetName(), 'source_path': source['output_path'],
               'source_sha256': source['output_sha256'], 'original_mp3_sha256': row['sha256'],
               'source_fps': clip.GetClipProperty('FPS'), 'source_start_seconds': item.GetSourceStartTime(),
               'source_end_seconds': item.GetSourceEndTime(), 'start_frame': item.GetStart(True),
               'end_frame': item.GetEnd(True), 'duration_seconds': item.GetDuration(True) / 30,
               'clip_gain_db': item.GetProperty('AudioVolume'), 'text': row['generation_text']}
        if record['clips']:
            previous = record['clips'][-1]
            record['joins'].append({'outgoing': previous['basename'], 'incoming': row['basename'],
                                    'timeline_frame': cursor, 'gap_frames': out['start_frame'] - previous['end_frame'],
                                    'full_source_edges_preserved': True,
                                    'centered_crossfade': 'not applied: full-source clips have no source handles; no speech was trimmed for transitions',
                                    'normal_speed_audition': False})
        record['clips'].append(out)
        cursor = item.GetEnd(True)
    record['duration_seconds'] = cursor / 30
    assert len(record['clips']) == {4: 8, 5: 7, 6: 9}[episode]
    assert not timeline.GetItemListInTrack('video', 1)
    assert timeline.SetCurrentTimecode('00:00:00:00')
    record['drt_export'] = timeline.Export(str(ROOT / f'{name}.drt'), r.EXPORT_DRT)
    record['otio_export'] = timeline.Export(str(ROOT / f'{name}.otio'), r.EXPORT_OTIO)
    assert record['drt_export'] and record['otio_export']
    result['timelines'].append(record)
    (ROOT / 'Resolve_组装回读.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert prep.Export(str(ROOT / '备份/女版04-06_原音频与音量准备.drt'), r.EXPORT_DRT)
assert pm.SaveProject()
assert pm.ExportProject(p.GetName(), str(ROOT / '备份/大码枕头_三集新旁白原速测试完成.drp'), False)
first = next(p.GetTimelineByIndex(i) for i in range(1, p.GetTimelineCount() + 1)
             if p.GetTimelineByIndex(i).GetName() == result['timelines'][0]['name'])
assert p.SetCurrentTimeline(first)
assert first.SetCurrentTimecode('00:00:00:00')
assert r.OpenPage('edit')
assert pm.SaveProject()
result['status'] = 'SAVED_THREE_ORIGINAL_SPEED_NARRATION_TEST_TIMELINES'
(ROOT / 'Resolve_组装回读.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': result['status'], 'timelines': [{k: x[k] for k in ('name', 'duration_seconds')} for x in result['timelines']]}, ensure_ascii=False))
