import sys,json,re,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
# Use only the documented Resolve MediaPool and Timeline APIs.
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
BASE=Path(__file__).resolve().parent
rows=json.loads((BASE/'11集字幕导入清单.json').read_text(encoding='utf-8'))
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='大码枕头';mp=p.GetMediaPool();original=p.GetCurrentTimeline()
ts={t.GetName():t for t in [p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)]}
binroot=next(x for x in mp.GetRootFolder().GetSubFolderList() if x.GetName()=='本次11集_SRT字幕')
def fr(tc):
 h,m,s,ms=map(int,re.split(r'[:,]',tc));return round((h*3600+m*60+s+ms/1000)*24)
def parse(row):
 result=[]
 for b in re.split(r'\n\s*\n',Path(row['srt']).read_text(encoding='utf-8-sig').strip()):
  a=b.splitlines();start,end=a[1].split(' --> ');result.append((fr(start),fr(end),'\n'.join(a[2:])))
 return result
def clean(s):return s.replace('\u2028','\n').replace('\r\n','\n').strip()
def native(t):return [(int(x.GetStart()),int(x.GetEnd()),clean(x.GetName())) for x in (t.GetItemListInTrack('subtitle',1) or [])]
def av(t):
 return {'start':t.GetStartFrame(),'end':t.GetEndFrame(),'tracks':[(k,i,t.GetTrackName(k,i),t.GetIsTrackEnabled(k,i),[(x.GetStart(),x.GetEnd(),x.GetSourceStartFrame(),x.GetSourceEndFrame(),x.GetMediaPoolItem().GetClipProperty('File Path') if x.GetMediaPoolItem() else None,x.GetProperty('AudioVolume'),x.GetProperty('ZoomX'),x.GetProperty('ZoomY')) for x in (t.GetItemListInTrack(k,i) or [])]) for k in ['video','audio'] for i in range(1,t.GetTrackCount(k)+1)]}
reports=[]
for row in rows:
 t=ts[row['timeline']];assert t.GetUniqueId()==row['timeline_id'];assert p.SetCurrentTimeline(t);assert t.GetTrackCount('subtitle')==1
 beforeav=av(t);expected=parse(row);old=native(t)
 if old!=expected:
  if old:
   assert row['ep'] in [21,22,23,24,25]
   assert [(a,b,' '.join(c.split())) for a,b,c in old]==[(a,b,' '.join(c.split())) for a,b,c in expected]
   backup=BASE.parent/'备份'/f'EP{row["ep"]}_字幕三行排版前.drt'
   if not backup.exists():assert t.Export(str(backup),r.EXPORT_DRT)
  folder=next(f for f in binroot.GetSubFolderList() if f.GetName()==str(row['ep']));assert mp.SetCurrentFolder(folder)
  existing=next((x for x in folder.GetClipList() if x.GetClipProperty('File Path')==row['srt']),None)
  if not existing:
   imported=mp.ImportMedia([row['srt']]);assert imported and imported[0]
   existing=imported[0]
  assert existing.GetClipProperty('Type')=='字幕'
  if old:assert t.DeleteClips(t.GetItemListInTrack('subtitle',1),False)
  assert t.SetCurrentTimecode('00:00:00:00')
  result=mp.AppendToTimeline([existing]);assert result and result[0],(row['ep'],result)
  assert native(t)==expected,(row['ep'],native(t),expected)
  action='reflowed_existing' if old else 'inserted'
 else:action='reused_matching'
 assert av(t)==beforeav,(row['ep'],'AV changed')
 assert t.SetTrackName('subtitle',1,str(row['ep']));assert t.SetTrackEnable('subtitle',1,True)
 assert pm.SaveProject()
 report={'ep':row['ep'],'timeline':t.GetName(),'cue_count':len(expected),'track':t.GetTrackName('subtitle',1),'action':action,'av_unchanged':True,'exact_text_timecode_match':True,'max_explicit_lines':max(len(c.splitlines()) for _,_,c in expected),'preset_loaded':False}
 reports.append(report);print(json.dumps(report,ensure_ascii=False),flush=True)
 (BASE/'11集SRT_原生插入与实读.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
assert p.SetCurrentTimeline(original);assert pm.SaveProject()
