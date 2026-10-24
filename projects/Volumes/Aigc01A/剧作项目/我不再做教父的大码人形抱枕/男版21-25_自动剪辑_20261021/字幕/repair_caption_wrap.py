import json,sys,re,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
# Importing the insertion script would run it; keep read-only helpers local.
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
rows=json.loads((OUT/'五集字幕导入清单.json').read_text(encoding='utf-8'))
log=json.loads((OUT/'SRT_原生入轨回读.json').read_text(encoding='utf-8'))
def fr(tc):
    h,m,s,ms=map(int,re.split('[:,]',tc));return round((h*3600+m*60+s+ms/1000)*24)
def parse(path):
    ans=[]
    for b in re.split(r'\n\s*\n',path.read_text(encoding='utf-8-sig').strip()):
        ls=b.splitlines();a,e=ls[1].split(' --> ');ans.append((fr(a),fr(e),'\n'.join(ls[2:])))
    return ans
def native(t):return [(int(x.GetStart()),int(x.GetEnd()),x.GetName().replace('\u2028','\n').strip()) for x in t.GetItemListInTrack('subtitle',1) or []]
def content(cues):return [(a,b,' '.join(s.split())) for a,b,s in cues]
def av(t):
    return {kind:[(t.GetTrackName(kind,j),t.GetIsTrackEnabled(kind,j),[(x.GetUniqueId(),x.GetStart(),x.GetEnd(),x.GetSourceStartFrame(),x.GetSourceEndFrame(),x.GetProperties(),x.GetClipEnabled(),x.GetMediaPoolItem().GetClipProperty('File Path')) for x in t.GetItemListInTrack(kind,j) or []]) for j in range(1,t.GetTrackCount(kind)+1)] for kind in ['video','audio']}
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='大码枕头'
mp=p.GetMediaPool();parent=next(f for f in mp.GetRootFolder().GetSubFolderList() if f.GetName()=='男版21-25_自动剪辑_20261021')
folder=mp.AddSubFolder(parent,'男版字幕_三行换行修正');assert folder and mp.SetCurrentFolder(folder)
ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
for row in rows:
    ep=row['ep']
    if ep not in [24,25]:continue
    path=OUT/'修正导入'/f'EP{ep}_三行.srt';assert path.exists()
    assert path.read_bytes()==Path(row['srt']).read_bytes()
    expected=parse(path);t=ts[row['timeline']];assert p.SetCurrentTimeline(t) and t.GetUniqueId()==row['timeline_id']
    assert len(expected)==row['cue_count'] and t.GetTrackCount('subtitle')==1
    old=native(t);assert content(old)==content(expected),'Only line breaks may change'
    before=av(t)
    backup=OUT/'备份'/f'EP{ep}_六条长字幕换行前.drt'
    if not backup.exists():assert t.Export(str(backup),r.EXPORT_DRT)
    if old!=expected:
        added=mp.ImportMedia([str(path)]);assert added and len(added)==1
        assert added[0].GetClipProperty('Type')=='字幕'
        assert t.DeleteClips(t.GetItemListInTrack('subtitle',1),False)
        assert not (t.GetItemListInTrack('subtitle',1) or [])
        assert t.SetCurrentTimecode('00:00:00:00')
        made=mp.AppendToTimeline([added[0]]);assert made and native(t)==expected
    assert av(t)==before and t.GetTrackName('subtitle',1)==str(ep)
    assert max(len(s.splitlines()) for _,_,s in expected)<=3
    assert pm.SaveProject()
    entry=next(x for x in log if x['ep']==ep)
    entry.update(action='native_srt_line_break_repair',max_explicit_lines=3,srt_sha256=hashlib.sha256(Path(row['srt']).read_bytes()).hexdigest(),
                 source_for_cache_safe_import=str(path),text_and_frame_times_exact=True,av_unchanged=True)
    (OUT/'SRT_原生入轨回读.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    print(ep,len(expected),'line breaks repaired; AV frozen',flush=True)
