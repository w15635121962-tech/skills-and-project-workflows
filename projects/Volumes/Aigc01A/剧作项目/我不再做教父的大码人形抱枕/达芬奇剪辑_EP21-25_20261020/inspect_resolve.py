import json
import re
import sys
from pathlib import Path

sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

out = Path(__file__).parent
resolve = get_resolve()
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
assert project, 'No project'
pool = project.GetMediaPool()
selected = project.GetCurrentTimeline()
settings = project.GetSettings()
result = {'project': project.GetName(), 'version': resolve.GetVersionString(),
          'current_timeline': selected.GetName() if selected else None,
          'settings': {k: v for k, v in settings.items() if any(x in k.lower() for x in ['resolution', 'framerate', 'audio', 'dropframe'])},
          'timelines': [], 'media': [], 'folders': []}

for i in range(1, project.GetTimelineCount() + 1):
    timeline = project.GetTimelineByIndex(i)
    data = {'index': i, 'name': timeline.GetName(), 'id': timeline.GetUniqueId(),
            'start': timeline.GetStartFrame(), 'end': timeline.GetEndFrame(),
            'settings': timeline.GetSettings(), 'tracks': {}}
    for kind in ['video', 'audio', 'subtitle']:
        data['tracks'][kind] = []
        for track in range(1, timeline.GetTrackCount(kind) + 1):
            items = timeline.GetItemListInTrack(kind, track) or []
            row = {'track': track, 'name': timeline.GetTrackName(kind, track), 'count': len(items), 'items': []}
            for item in items:
                source = item.GetMediaPoolItem()
                row['items'].append({'name': item.GetName(), 'start': item.GetStart(), 'end': item.GetEnd(),
                                     'left': item.GetLeftOffset(), 'right': item.GetRightOffset(),
                                     'source_path': source.GetClipProperty('File Path') if source else None,
                                     'source_start': item.GetSourceStartFrame() if source else None,
                                     'source_end': item.GetSourceEndFrame() if source else None})
            data['tracks'][kind].append(row)
    result['timelines'].append(data)

def walk(folder, parent=''):
    name = parent + '/' + folder.GetName()
    clips = folder.GetClipList() or []
    result['folders'].append({'name': name, 'count': len(clips)})
    for clip in clips:
        props = clip.GetClipProperty()
        result['media'].append({'folder': name, 'id': clip.GetUniqueId(), 'name': clip.GetName(), 'properties': props})
    for child in folder.GetSubFolderList() or []:
        walk(child, name)

walk(pool.GetRootFolder())
(out / 'Resolve_操作前完整实读.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps({'project': result['project'], 'current': result['current_timeline'],
                  'timelines': [{'name': x['name'], 'start': x['start'], 'end': x['end'],
                                 'tracks': {k: sum(t['count'] for t in v) for k, v in x['tracks'].items()}}
                                for x in result['timelines']],
                  'media_count': len(result['media']), 'folders': result['folders']}, ensure_ascii=False))
