import json,sys,re,hashlib
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
rows=json.loads((OUT/'五集字幕导入清单.json').read_text(encoding='utf-8'))
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='大码枕头'
mp=p.GetMediaPool();root=mp.GetRootFolder()
parent=next(f for f in root.GetSubFolderList() if f.GetName()=='男版21-25_自动剪辑_20261021')
found=[f for f in parent.GetSubFolderList() or [] if f.GetName()=='男版SRT_EP21-25']
folder=found[0] if found else mp.AddSubFolder(parent,'男版SRT_EP21-25');assert folder
ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
def fr(tc):
    h,m,s,ms=map(int,re.split('[:,]',tc));return round((h*3600+m*60+s+ms/1000)*24)
def parse(path):
    cues=[]
    for block in re.split(r'\n\s*\n',Path(path).read_text(encoding='utf-8-sig').replace('\r\n','\n').strip()):
        lines=block.splitlines();a,b=lines[1].split(' --> ')
        cues.append((fr(a),fr(b),'\n'.join(lines[2:])))
    return cues
def clean(s):return s.replace('\u2028','\n').replace('\r\n','\n').strip()
def native(t):return [(int(x.GetStart()),int(x.GetEnd()),clean(x.GetName())) for x in t.GetItemListInTrack('subtitle',1) or []]
def av(t):
    return {kind:[(t.GetTrackName(kind,j),t.GetIsTrackEnabled(kind,j),[(x.GetUniqueId(),x.GetStart(),x.GetEnd(),x.GetSourceStartFrame(),x.GetSourceEndFrame(),x.GetProperties(),x.GetClipEnabled(),x.GetMediaPoolItem().GetClipProperty('File Path')) for x in t.GetItemListInTrack(kind,j) or []]) for j in range(1,t.GetTrackCount(kind)+1)] for kind in ['video','audio']}
report=[]
for row in rows:
    t=ts[row['timeline']];assert t.GetUniqueId()==row['timeline_id'];assert p.SetCurrentTimeline(t)
    assert t.GetStartFrame()==0 and float(t.GetSetting('timelineFrameRate'))==24
    assert t.GetTrackCount('subtitle')==1
    before=av(t);expected=parse(row['srt']);old=native(t)
    assert len(expected)==row['cue_count']
    assert all(a>=0 and a<b<=t.GetEndFrame() and len(s.splitlines())<=3 for a,b,s in expected)
    if old:
        assert old==expected,'Existing subtitles conflict; do not overwrite'
        action='reused_exact'
    else:
        sub=mp.AddSubFolder(folder,str(row['ep']));assert sub and mp.SetCurrentFolder(sub)
        imported=mp.ImportMedia([row['srt']]);assert imported and len(imported)==1
        clip=imported[0];assert clip.GetClipProperty('Type')=='字幕'
        assert t.SetCurrentTimecode('00:00:00:00')
        made=mp.AppendToTimeline([clip])
        observed=native(t)
        assert made and observed==expected,(row['ep'],'insert mismatch',len(observed),len(expected),observed[:2],expected[:2])
        action='inserted_native_srt'
    assert t.GetTrackCount('subtitle')==1 and av(t)==before,'AV changed'
    assert t.SetTrackName('subtitle',1,str(row['ep']))
    t.SetTrackEnable('subtitle',1,True);assert t.GetIsTrackEnabled('subtitle',1)
    assert pm.SaveProject()
    report.append({'ep':row['ep'],'timeline':t.GetName(),'id':t.GetUniqueId(),'action':action,'cue_count':len(expected),
                   'track':t.GetTrackName('subtitle',1),'text_and_frame_times_exact':True,'av_unchanged':True,
                   'max_explicit_lines':max(len(c.splitlines()) for _,_,c in expected),'srt':row['srt'],
                   'srt_sha256':hashlib.sha256(Path(row['srt']).read_bytes()).hexdigest()})
    (OUT/'SRT_原生入轨回读.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report[-1],ensure_ascii=False),flush=True)
assert len(report)==5 and sum(x['cue_count'] for x in report)==197
first=ts[rows[0]['timeline']];assert p.SetCurrentTimeline(first)
assert pm.SaveProject()
