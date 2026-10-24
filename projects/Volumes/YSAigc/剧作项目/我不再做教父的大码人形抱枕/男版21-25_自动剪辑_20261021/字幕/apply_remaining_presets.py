"""Task-local native UI driver for the already imported male captions.

Uses the user's authorized AppleScript and real mouse events. The timeline
canvas geometry is checked against the current observed layout every episode.
No caption text or audiovisual edit is changed.
"""
import json,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
CLICK=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/自动剪辑_女版16-19_21-26_28_20261020/准备/native_left_click.js')
rows=json.loads((OUT/'五集字幕导入清单.json').read_text(encoding='utf-8'))
scope=set(map(int,sys.argv[1:])) if len(sys.argv)>1 else {22,23,24,25}
done=json.loads((OUT/'SRT_原生入轨回读.json').read_text(encoding='utf-8'));assert len(done)==5
r=get_resolve();p=r.GetProjectManager().GetCurrentProject();assert p.GetName()=='大码枕头'
ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
APP='tell application "System Events"\ntell (first application process whose bundle identifier is "com.blackmagic-design.DaVinciResolve")\n'
END='\nend tell\nend tell'
def osa(s):return subprocess.check_output(['osascript','-e',s],text=True,encoding='utf-8',stderr=subprocess.PIPE).strip()
for row in rows:
    if row['ep'] not in scope:continue
    t=ts[row['timeline']];assert t.GetUniqueId()==row['timeline_id']
    assert len(t.GetItemListInTrack('subtitle',1) or [])==row['cue_count']
    assert p.SetCurrentTimeline(t)
    osa('tell application id "com.blackmagic-design.DaVinciResolve" to activate')
    # Current native AX bounds, matching the screenshot-observed ST1 row.
    raw=osa(APP+'''set w to window "大码枕头"
set g to splitter group 1 of group 1 of w
set xy to position of g
set wh to size of g
if item 1 of wh < 1200 or item 1 of wh > 1500 then error "Timeline layout changed"
if item 2 of wh < 650 or item 2 of wh > 800 then error "Timeline layout changed"
set b to first checkbox of group 1 of w whose description is "选择模式"
if value of b is not 1 then click b
return {(item 1 of xy)+300, (item 2 of xy)+88}'''+END)
    vals=[float(x.strip()) for x in raw.split(',')];assert len(vals)==2
    subprocess.run(['osascript','-l','JavaScript',str(CLICK),*map(str,vals)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    time.sleep(.15)
    context=osa(APP+'''tell group 1 of window "大码枕头"
set selectedName to name of static text 1
if selectedName does not contain "字幕" and selectedName is not "'''+str(row['ep'])+'''" then error "Subtitle was not selected"
if value of checkbox 2 is not 1 then click checkbox 2
end tell
return name of static text 1 of group 1 of window "大码枕头"'''+END)
    assert context==str(row['ep']),(row['ep'],context)
    inner=osa(APP+'''tell group 2 of group 1 of window "大码枕头"
if value of checkbox 2 is not 1 then click checkbox 2
end tell
return value of checkbox 2 of group 2 of group 1 of window "大码枕头"'''+END)
    assert inner=='1'
    subprocess.run([sys.executable,str(OUT/'apply_track_preset.py'),str(row['ep'])],check=True)
    print('PRESET_DONE',row['ep'],flush=True)
