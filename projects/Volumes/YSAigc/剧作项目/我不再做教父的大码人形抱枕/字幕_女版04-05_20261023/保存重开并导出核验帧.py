import sys,json,re,hashlib,zipfile
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();b=Path(__file__).resolve().parent;out=b/'保存回读';out.mkdir(exist_ok=True);shots=b/'画面核验';shots.mkdir(exist_ok=True)
rows=json.loads((b/'字幕导入清单.json').read_text(encoding='utf-8'))
def stylehash(path):
 with zipfile.ZipFile(path)as z:
  s=z.read(next(n for n in z.namelist()if n.startswith('SeqContainer/')and n.endswith('.xml'))).decode('utf-8');v=re.search(r'<SubtitleTrackVec>\s*<Element>\s*<Sm2TiTrack\b[^>]*>\s*<FieldsBlob>(.*?)</FieldsBlob>',s,re.S).group(1);return hashlib.sha256(v.encode()).hexdigest()
def cues(t):return[(x.GetStart(),x.GetEnd(),x.GetName())for x in t.GetItemListInTrack('subtitle',1)or[]]
def timeline(uid):return next(p.GetTimelineByIndex(i)for i in range(1,p.GetTimelineCount()+1)if p.GetTimelineByIndex(i).GetUniqueId()==uid)
before={};reports=[]
for row in rows:
 t=timeline(row['timeline_id']);assert p.SetCurrentTimeline(t);fp=out/f'EP{row["ep"]}_预设保存前.drt';assert t.Export(str(fp),r.EXPORT_DRT);before[row['ep']]={'cues':cues(t),'style':stylehash(fp)}
assert pm.SaveProject();assert pm.CloseProject(p);p=pm.LoadProject('大码枕头');assert p
for row in rows:
 t=timeline(row['timeline_id']);assert p.SetCurrentTimeline(t);assert t.GetTrackName('subtitle',1)==str(row['ep']);assert cues(t)==before[row['ep']]['cues'];assert t.GetIsTrackEnabled('subtitle',1);fp=out/f'EP{row["ep"]}_预设重开后.drt';assert t.Export(str(fp),r.EXPORT_DRT);assert stylehash(fp)==before[row['ep']]['style']
 cs=t.GetItemListInTrack('subtitle',1);samples=[('first',cs[0]),('middle',cs[len(cs)//2]),('last',cs[-1]),('longest',max(cs,key=lambda c:len(c.GetName())))];rr=[]
 for label,c in samples:
  f=int((c.GetStart()+c.GetEnd())//2);tc=f'{f//108000:02d}:{f//1800%60:02d}:{f//30%60:02d}:{f%30:02d}';assert t.SetCurrentTimecode(tc);fn=shots/f'EP{row["ep"]}_{label}.png';ok=p.ExportCurrentFrameAsStill(str(fn));rr.append({'label':label,'tc':tc,'text':c.GetName(),'file':str(fn),'exported':ok})
 reports.append({'ep':row['ep'],'cue_count':len(cs),'track':t.GetTrackName('subtitle',1),'saved_reopened_cues_and_style_match':True,'style_hash':before[row['ep']]['style'],'frames':rr})
assert pm.SaveProject();(b/'保存重开回读.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps([{k:v for k,v in x.items()if k!='frames'}for x in reports],ensure_ascii=False))
