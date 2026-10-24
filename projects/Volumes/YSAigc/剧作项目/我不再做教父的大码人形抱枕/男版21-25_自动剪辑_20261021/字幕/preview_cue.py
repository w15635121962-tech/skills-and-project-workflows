import sys,json,re,time
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
out=Path(__file__).resolve().parent;ep=int(sys.argv[1]);cue=int(sys.argv[2])
row=next(x for x in json.loads((out/'五集字幕导入清单.json').read_text(encoding='utf-8')) if x['ep']==ep)
r=get_resolve();p=r.GetProjectManager().GetCurrentProject();assert p.GetName()=='大码枕头'
t=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetUniqueId()==row['timeline_id'])
if p.GetCurrentTimeline().GetUniqueId()!=row['timeline_id']:
 assert p.SetCurrentTimeline(t);time.sleep(.4)
x=t.GetItemListInTrack('subtitle',1)[cue-1];f=(int(x.GetStart())+int(x.GetEnd()))//2
h,f=divmod(f,86400);m,f=divmod(f,1440);s,f=divmod(f,24);tc=f'{h:02}:{m:02}:{s:02}:{f:02}'
assert t.SetCurrentTimecode(tc);print(ep,cue,tc,x.GetName(),flush=True)
