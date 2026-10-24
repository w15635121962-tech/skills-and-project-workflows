"""Coordinate UI wrap-only adaptation with the official Resolve SDK.

The user requests preset styling and at most three displayed lines. The loaded
preset's 26-character auto-wrap rewraps existing hard lines. Only this limit is
adapted to 30; all cue content, timing, and all other style fields are checked.
"""
import datetime
import json
from pathlib import Path
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
OUT = BASE / '换行适配'
OUT.mkdir(exist_ok=True)
ROWS = json.loads((BASE/'11集字幕导入清单.json').read_text(encoding='utf-8'))
POINTS = json.loads((BASE/'11集预设后画面抽查点.json').read_text(encoding='utf-8'))['samples']
sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
resolve = get_resolve()
pm = resolve.GetProjectManager()
project = pm.GetCurrentProject()
assert project.GetName() == '大码枕头'
timelines = {project.GetTimelineByIndex(i).GetUniqueId(): project.GetTimelineByIndex(i)
             for i in range(1, project.GetTimelineCount()+1)}

def signature(t):
    return {kind: [[t.GetTrackName(kind, n), [[c.GetName(), c.GetStart(), c.GetEnd(),
               c.GetLeftOffset(), c.GetRightOffset()] for c in (t.GetItemListInTrack(kind, n) or [])]]
            for n in range(1, t.GetTrackCount(kind)+1)] for kind in ('video','audio','subtitle')}

def read_style():
    code='''tell application "System Events"
tell (first application process whose bundle identifier is "com.blackmagic-design.DaVinciResolve")
set episodeHeader to name of static text 1 of group 1 of window "大码枕头"
if value of checkbox 2 of group 1 of window "大码枕头" is not 1 then error "Not Track context"
if value of checkbox 2 of group 2 of group 1 of window "大码枕头" is not 1 then error "Not subtitle Track style"
tell group 1 of group 2 of group 1 of window "大码枕头"
set outText to episodeHeader & linefeed & (name of combo box 1) & linefeed & (name of combo box 2) & linefeed
set fieldNames to get name of every static text
repeat with v in fieldNames
if contents of v is not missing value then set outText to outText & (contents of v as text) & tab
end repeat
set outText to outText & linefeed
set checkValues to get value of every checkbox
repeat with v in checkValues
if contents of v is not missing value then set outText to outText & (contents of v as text) & tab
end repeat
return outText
end tell
end tell
end tell'''
    raw=subprocess.check_output(['osascript','-e',code],text=True,encoding='utf-8').strip()
    lines=raw.splitlines()
    return dict(episode_header=lines[0], font=lines[1], weight=lines[2],
                text_fields=lines[3].split('\t'), checkbox_values=lines[4].split('\t'))

reports=[]
for row in ROWS:
    ep=row['ep'];t=timelines[row['timeline_id']]
    assert t.GetName()==row['timeline']
    assert project.SetCurrentTimeline(t)
    time.sleep(.5)
    point=next(x for x in POINTS if x['episode']==ep)
    frame=point['sample_frame'];sec,ff=divmod(frame,24);mins,ss=divmod(sec,60);hh,mm=divmod(mins,60)
    tc=f'{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}'
    assert t.SetCurrentTimecode(tc)
    before=signature(t)
    data={'episode':ep, 'timeline':t.GetName(),'timeline_id':t.GetUniqueId(),'sample_timecode':tc}
    (OUT/'next.json').write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'ready':ep}),flush=True)
    deadline=time.monotonic()+300
    while not (OUT/f'EP{ep}.adapted').exists():
        if time.monotonic()>deadline:raise TimeoutError(ep)
        time.sleep(.05)
    assert project.GetCurrentTimeline().GetUniqueId()==t.GetUniqueId()
    actual=read_style()
    original=json.loads((BASE/'预设操作记录'/f'EP{ep}.json').read_text(encoding='utf-8'))['after_style']
    expected=json.loads(json.dumps(original))
    i=expected['text_fields'].index('每行字符最大值')-1
    assert expected['text_fields'][i]=='26'
    expected['text_fields'][i]='30'
    assert actual==expected,(ep,actual,expected)
    assert signature(t)==before
    assert pm.SaveProject()
    reports.append({**data,'after_style':actual,'only_wrap_changed':True,'cues_and_av_unchanged':True,
                    'saved':True,'time':datetime.datetime.now().isoformat()})
    (OUT/f'EP{ep}.json').write_text(json.dumps(reports[-1],ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'next.json').unlink()
(OUT/'result.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'done.json').write_text(json.dumps({'complete':True,'episodes':len(reports)}),encoding='utf-8')
print(json.dumps({'complete':True,'episodes':len(reports)}),flush=True)
