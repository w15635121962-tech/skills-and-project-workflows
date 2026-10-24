"""Read-only timeline baseline; the only Resolve mutations are SaveProject/ExportProject."""
import datetime
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
OUT.mkdir(exist_ok=True)
(OUT / '备份').mkdir(exist_ok=True)
stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
manifest = json.loads((BASE / 'Resolve_组装实读.json').read_text(encoding='utf-8'))


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def read_item(item, kind):
    media = item.GetMediaPoolItem()
    row = {
        'id': item.GetUniqueId(), 'name': item.GetName(),
        'start': item.GetStart(True), 'end': item.GetEnd(True),
        'duration': item.GetDuration(True),
        'source_start': item.GetSourceStartFrame(),
        'source_end': item.GetSourceEndFrame(),
        'source_start_seconds': item.GetSourceStartTime(),
        'source_end_seconds': item.GetSourceEndTime(),
        'left_offset': item.GetLeftOffset(True),
        'right_offset': item.GetRightOffset(True),
        'enabled': item.GetClipEnabled(),
        'properties': item.GetProperties(),
        'speed': item.GetSpeed(),
        'linked_ids': sorted(x.GetUniqueId() for x in item.GetLinkedItems() or []),
        'markers': item.GetMarkers(),
        'media_pool_id': media.GetUniqueId() if media else None,
        'source_path': media.GetClipProperty('File Path') if media else None,
        'source_properties': media.GetClipProperty() if media else None,
    }
    if kind == 'subtitle':
        # Documented GetName returns native subtitle text (20.2.1 fix).
        row['text'] = item.GetName()
    return row


def read_timeline(timeline, episode):
    row = {'episode': episode, 'id': timeline.GetUniqueId(),
           'name': timeline.GetName(), 'start': timeline.GetStartFrame(),
           'end': timeline.GetEndFrame(), 'start_timecode': timeline.GetStartTimecode(),
           'settings': timeline.GetSettings(), 'markers': timeline.GetMarkers(), 'tracks': {}}
    for kind in ('video', 'audio', 'subtitle'):
        row['tracks'][kind] = []
        for index in range(1, timeline.GetTrackCount(kind) + 1):
            track = {'index': index, 'name': timeline.GetTrackName(kind, index),
                     'enabled': timeline.GetIsTrackEnabled(kind, index),
                     'locked': timeline.GetIsTrackLocked(kind, index),
                     'items': [read_item(x, kind) for x in timeline.GetItemListInTrack(kind, index) or []]}
            if kind == 'audio':
                track['subtype'] = timeline.GetTrackSubType(kind, index)
            row['tracks'][kind].append(track)
    av = {'start': row['start'], 'end': row['end'], 'settings': row['settings'],
          'tracks': {k: row['tracks'][k] for k in ('video', 'audio')}}
    row['av_sha256'] = digest(av)
    row['subtitle_sha256'] = digest(row['tracks']['subtitle'])
    row['counts'] = {k: sum(len(t['items']) for t in row['tracks'][k]) for k in row['tracks']}
    return row


resolve = get_resolve()
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
assert project and project.GetName() == '大码枕头', 'Wrong project: do not save/export'
current = project.GetCurrentTimeline()
original = {'project': project.GetName(), 'timeline_id': current.GetUniqueId() if current else None,
            'timeline_name': current.GetName() if current else None,
            'timecode': current.GetCurrentTimecode() if current else None,
            'page': resolve.GetCurrentPage()}
timelines = {project.GetTimelineByIndex(i).GetUniqueId(): project.GetTimelineByIndex(i)
             for i in range(1, project.GetTimelineCount() + 1)}
report = {'recorded_at': datetime.datetime.now().isoformat(), 'project': project.GetName(),
          'version': resolve.GetVersionString(), 'original_context': original,
          'all_timeline_names': {key: t.GetName() for key, t in timelines.items()},
          'project_settings': project.GetSettings(), 'episodes': [],
          'scope': 'No UI/page/timeline switch; no track/media/subtitle/style changes; SaveProject/ExportProject only.'}
for expected in sorted(manifest['episodes'], key=lambda x: x['episode']):
    t = timelines[expected['id']]
    assert t.GetName() == expected['timeline']
    report['episodes'].append(read_timeline(t, expected['episode']))

# Save/export is explicitly authorized. Confirm project immediately before saving.
assert pm.GetCurrentProject().GetName() == '大码枕头'
assert pm.SaveProject(), 'SaveProject failed'
backup = OUT / '备份' / f'大码枕头_男版21-25_添加字幕前_{stamp}.drp'
assert not backup.exists()
assert pm.ExportProject(project.GetName(), str(backup), True), 'ExportProject failed'
assert backup.is_file() and backup.stat().st_size > 0
report['backup'] = {'path': str(backup), 'bytes': backup.stat().st_size,
                    'sha256': hashlib.sha256(backup.read_bytes()).hexdigest(),
                    'with_stills_and_luts': True,
                    'note': 'Complete project DRP, not media archive; external source media remains referenced.'}

# Re-read without changing current timeline; prove this operation changed no target AV/subtitle rows.
report['post_backup_checks'] = []
for expected, before in zip(sorted(manifest['episodes'], key=lambda x: x['episode']), report['episodes']):
    after = read_timeline(timelines[expected['id']], expected['episode'])
    same_av = before['av_sha256'] == after['av_sha256']
    same_st = before['subtitle_sha256'] == after['subtitle_sha256']
    assert same_av and same_st
    report['post_backup_checks'].append({'episode': expected['episode'],
                                         'av_unchanged': same_av, 'subtitle_unchanged': same_st})
now = project.GetCurrentTimeline()
report['current_context_after'] = {'project': pm.GetCurrentProject().GetName(),
                                  'timeline_id': now.GetUniqueId() if now else None,
                                  'timeline_name': now.GetName() if now else None,
                                  'timecode': now.GetCurrentTimecode() if now else None,
                                  'page': resolve.GetCurrentPage()}
assert report['current_context_after'] == original
path = OUT / 'Resolve_字幕操作前完整基线.json'
path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'baseline': str(path), 'backup': report['backup'],
                  'original_context_unchanged': True,
                  'episodes': [{'episode': e['episode'], 'name': e['name'],
                                'counts': e['counts'], 'subtitle_tracks': len(e['tracks']['subtitle']),
                                'av_sha256': e['av_sha256']} for e in report['episodes']]},
                 ensure_ascii=False, indent=2), flush=True)
