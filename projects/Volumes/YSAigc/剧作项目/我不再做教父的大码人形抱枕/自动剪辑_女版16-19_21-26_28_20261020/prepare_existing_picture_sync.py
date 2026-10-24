import json, sys
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool()
assert p.GetName()=='大码枕头'
assert (OUT/'备份/大码枕头_女版11集自动剪辑前完整备份.drp').stat().st_size>0
ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
log=[]
def rows(t,kind,tr):
    return [{'name':x.GetName(),'start':x.GetStart(),'end':x.GetEnd(),'src0':x.GetSourceStartTime(),'src1':x.GetSourceEndTime(),'path':x.GetMediaPoolItem().GetClipProperty('File Path') if x.GetMediaPoolItem() else None,'props':x.GetProperties()} for x in t.GetItemListInTrack(kind,tr) or []]
def same(a,b):
    if len(a)!=len(b):return False
    for x,y in zip(a,b):
        if any(x[k]!=y[k] for k in x if k!='props'):return False
        if any(x['props'][k]!=y['props'][k] for k in set(x['props'])&set(y['props'])):return False
        # Resolve materializes disabled effect defaults on duplication.
        for k in set(x['props'])^set(y['props']):
            if x['props'].get(k,y['props'].get(k)) not in [False,0,0.0,None]:return False
    return True
for ep in range(21,26):
    original=ts[f'大码_女版_EP{ep}_精修_旁白110_v2']
    name=f'大码_女版_EP{ep}_画面同期声_待新旁白_v3'
    t=ts.get(name) or original.DuplicateTimeline(name);assert t and p.SetCurrentTimeline(t)
    assert t.SetTrackEnable('audio',2,False)
    assert t.SetTrackName('audio',2,'旧旁白_暂静音待新音色')
    assert not t.GetIsTrackEnabled('audio',2)
    for kind in ['video','audio','subtitle']:
        assert t.GetTrackCount(kind)==original.GetTrackCount(kind)
        for tr in range(1,t.GetTrackCount(kind)+1):
            assert same(rows(t,kind,tr),rows(original,kind,tr)),(ep,kind,tr,'copy mismatch')
    assert t.GetEndFrame()==original.GetEndFrame()
    assert t.GetTrackName('subtitle',1)==str(ep)
    assert pm.SaveProject()
    assert t.Export(str(OUT/'原生时间线'/(name+'.drt')),r.EXPORT_DRT)
    log.append({'episode':ep,'original_timeline':original.GetName(),'working_timeline':name,'id':t.GetUniqueId(),'duration_frames':t.GetEndFrame(),'old_narration_track_enabled':False,'picture_sync_music_subtitle_content_preserved':True,'subtitle_track':str(ep),'new_narration_status':'deferred by user; picture and source audio first'})
    (OUT/'Resolve_21-25画面同期声版本回读.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(log[-1],ensure_ascii=False),flush=True)
assert pm.SaveProject()
