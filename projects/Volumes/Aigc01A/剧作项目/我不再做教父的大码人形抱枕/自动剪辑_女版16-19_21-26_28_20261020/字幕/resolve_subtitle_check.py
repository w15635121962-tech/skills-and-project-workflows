import sys,json,re,argparse
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
BASE=Path(__file__).resolve().parent
ROWS=json.loads((BASE/'11集字幕导入清单.json').read_text(encoding='utf-8'))
parser=argparse.ArgumentParser();parser.add_argument('action',choices=['status','prepare','verify','switch']);parser.add_argument('ep',type=int,nargs='?');parser.add_argument('--frame',type=int);args=parser.parse_args()
r=get_resolve();p=r.GetProjectManager().GetCurrentProject();mp=p.GetMediaPool();assert p.GetName()=='大码枕头'
original=p.GetCurrentTimeline()
ts={t.GetName():t for t in [p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)]}
def parse(row):
 def fr(tc):
  h,m,s,ms=map(int,re.split(r'[:,]',tc));return round((h*3600+m*60+s+ms/1000)*24)
 data=[]
 for block in re.split(r'\n\s*\n',Path(row['srt']).read_text(encoding='utf-8-sig').strip()):
  lines=block.splitlines();a,b=lines[1].split(' --> ');data.append({'text':'\n'.join(lines[2:]),'start':fr(a),'end':fr(b)})
 return data
def norm(text):return ' '.join(text.split())
selected=ROWS if args.ep is None else [x for x in ROWS if x['ep']==args.ep]
reports=[]
for row in selected:
 t=ts[row['timeline']];assert t.GetUniqueId()==row['timeline_id'];assert p.SetCurrentTimeline(t)
 if args.action=='switch':
  frame=args.frame if args.frame is not None else 1
  assert 0 <= frame < int(t.GetEndFrame())
  seconds,ff=divmod(frame,24);minutes,ss=divmod(seconds,60);hh,mm=divmod(minutes,60)
  assert t.SetCurrentTimecode(f'{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}')
 if args.action=='prepare':
  b=next(x for x in mp.GetRootFolder().GetSubFolderList() if x.GetName()=='本次11集_SRT字幕');f=next(x for x in b.GetSubFolderList() if x.GetName()==str(row['ep']));assert mp.SetCurrentFolder(f)
  existing=f.GetClipList() or []
  if len(existing)==1:assert mp.SetSelectedClip(existing[0])
  assert t.SetCurrentTimecode('00:00:00:00')
 items=t.GetItemListInTrack('subtitle',1) or [] if t.GetTrackCount('subtitle') else []
 expected=parse(row);diffs=[]
 if len(items)!=len(expected):diffs.append({'kind':'count','actual':len(items),'expected':len(expected)})
 for n,(a,e) in enumerate(zip(items,expected),1):
  if (int(a.GetStart()),int(a.GetEnd()),norm(a.GetName()))!=(e['start'],e['end'],norm(e['text'])):diffs.append({'cue':n,'actual':[a.GetStart(),a.GetEnd(),a.GetName()],'expected':e})
 if args.action=='verify' and not diffs:
  assert t.SetTrackName('subtitle',1,str(row['ep']));assert t.GetTrackName('subtitle',1)==str(row['ep']);assert r.GetProjectManager().SaveProject()
 report={'ep':row['ep'],'timeline':t.GetName(),'track_count':t.GetTrackCount('subtitle'),'cue_count':len(items),'expected':len(expected),'diffs':diffs,'track_names':[t.GetTrackName('subtitle',j) for j in range(1,t.GetTrackCount('subtitle')+1)]}
 reports.append(report);print(json.dumps(report,ensure_ascii=False),flush=True)
if args.action=='status':(BASE/'11集原生字幕_当前状态.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')

if args.action=='status':p.SetCurrentTimeline(original)
