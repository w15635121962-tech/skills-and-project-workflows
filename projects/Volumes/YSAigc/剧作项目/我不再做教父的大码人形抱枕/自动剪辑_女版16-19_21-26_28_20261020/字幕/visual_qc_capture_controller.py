"""Read-only Resolve SDK seek controller; screenshots are captured through CUA.

The file handshake prevents advancing the playhead before each screenshot finishes.
It does not change captions, track style, or any AV edit.
"""
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

BASE = Path(__file__).resolve().parent
OUT = BASE / '预设画面核验'
OUT.mkdir(exist_ok=True)
ROWS = json.loads((BASE / '11集字幕导入清单.json').read_text(encoding='utf-8'))
POINTS = json.loads((BASE / '11集预设后画面抽查点.json').read_text(encoding='utf-8'))['samples']
project = get_resolve().GetProjectManager().GetCurrentProject()
assert project.GetName() == '大码枕头'
timelines = {project.GetTimelineByIndex(i).GetUniqueId(): project.GetTimelineByIndex(i)
             for i in range(1, project.GetTimelineCount() + 1)}
plan = []
for row in ROWS:
    timeline = timelines[row['timeline_id']]
    assert timeline.GetName() == row['timeline']
    cues = timeline.GetItemListInTrack('subtitle', 1)
    assert len(cues) == row['cue_count']
    chosen = {0: ['first'], len(cues)//2: ['middle'], len(cues)-1: ['last']}
    for pt in POINTS:
        if pt['episode'] == row['ep']:
            chosen.setdefault(pt['cue_number']-1, []).append('long_or_wide')
    for index, reasons in sorted(chosen.items()):
        cue = cues[index]
        start, end = int(cue.GetStart()), int(cue.GetEnd())
        frame = start + min(12, max(0, (end-start)//2))
        seconds, ff = divmod(frame, 24)
        minutes, ss = divmod(seconds, 60)
        hh, mm = divmod(minutes, 60)
        plan.append({'id': f"EP{row['ep']}_cue{index+1:03d}_f{frame:05d}",
                     'episode': row['ep'], 'timeline_id': row['timeline_id'],
                     'timeline': row['timeline'], 'cue_number': index+1,
                     'frame': frame, 'timecode': f'{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}',
                     'text': cue.GetName(), 'reasons': reasons})
(OUT / 'capture_plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
last_timeline = None
for item in plan:
    timeline = timelines[item['timeline_id']]
    if last_timeline != item['timeline_id']:
        assert project.SetCurrentTimeline(timeline)
        time.sleep(.5)
        last_timeline = item['timeline_id']
    assert project.GetCurrentTimeline().GetUniqueId() == item['timeline_id']
    assert timeline.SetCurrentTimecode(item['timecode'])
    time.sleep(.15)
    if timeline.GetCurrentTimecode() != item['timecode']:
        assert timeline.SetCurrentTimecode(item['timecode'])
        time.sleep(.2)
    assert timeline.GetCurrentTimecode() == item['timecode']
    item['actual_timecode'] = timeline.GetCurrentTimecode()
    temp = OUT / 'next.tmp'
    temp.write_text(json.dumps(item, ensure_ascii=False), encoding='utf-8')
    temp.replace(OUT / 'next.json')
    print(json.dumps({'ready': item['id'], 'episode': item['episode']}, ensure_ascii=False), flush=True)
    deadline = time.monotonic()+300
    while not (OUT / (item['id'] + '.captured')).exists():
        if time.monotonic() > deadline:
            raise TimeoutError(item['id'])
        time.sleep(.05)
    assert project.GetCurrentTimeline().GetUniqueId() == item['timeline_id']
    assert timeline.GetCurrentTimecode() == item['timecode']
    item['captured'] = True
(OUT / 'capture_result.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'done.json').write_text(json.dumps({'complete': True, 'count': len(plan)}), encoding='utf-8')
print(json.dumps({'complete': True, 'count': len(plan)}), flush=True)
