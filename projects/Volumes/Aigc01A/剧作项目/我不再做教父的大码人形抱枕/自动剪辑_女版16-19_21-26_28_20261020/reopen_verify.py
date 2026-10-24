import json, sys
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
expected=json.loads((OUT/'11集剪辑工作版_最终实读.json').read_text(encoding='utf-8'))
assert Path(expected['saved_project_backup']).stat().st_size>0
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject()
assert p.GetName()==expected['project'];assert pm.SaveProject()
assert pm.CloseProject(p)
p=pm.LoadProject(expected['project']);assert p
ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
result=[]
for e in expected['episodes']:
    t=ts[e['timeline']];assert t.GetUniqueId()==e['id']
    assert p.SetCurrentTimeline(t)
    assert t.GetEndFrame()==e['end'] and t.GetStartFrame()==e['start']
    for kind,tracks in e['tracks'].items():
        assert t.GetTrackCount(kind)==len(tracks)
        for tr in tracks:
            assert t.GetTrackName(kind,tr['index'])==tr['name']
            assert t.GetIsTrackEnabled(kind,tr['index'])==tr['enabled']
            items=t.GetItemListInTrack(kind,tr['index']) or []
            assert len(items)==len(tr['items'])
            for x,a in zip(items,tr['items']):
                assert x.GetStart()==a['start'] and x.GetEnd()==a['end']
                m=x.GetMediaPoolItem();path=m.GetClipProperty('File Path') if m else None
                assert path==a['source_path']
                if m:assert abs(x.GetSourceStartTime()-a['source_start'])<.00001
                for prop in ['AudioVolume','ZoomX','ZoomY']:
                    if prop in a['properties']:assert abs(x.GetProperty(prop)-a['properties'][prop])<.0001
    if e['episode'] in [16,17,18,19]:
        assert p.SetCurrentTimeline(t)
        f=OUT/'原生时间线'/(t.GetName()+'_保存重开后.otio')
        assert t.Export(str(f),r.EXPORT_OTIO)
        otio=json.loads(f.read_text(encoding='utf-8'))
        atr=[tr for tr in otio['tracks']['children'] if tr['kind']=='Audio'][1]
        clips=[c for c in atr['children'] if c['OTIO_SCHEMA'].startswith('Clip')]
        assert len(clips)==len(e['tracks']['audio'][1]['items'])
        for c in clips:
            warp=[x['time_scalar'] for x in c['effects'] if x['OTIO_SCHEMA'].startswith('LinearTimeWarp')]
            assert len(warp)==1 and abs(warp[0]-1.1)<1e-8
    result.append({'episode':e['episode'],'timeline':t.GetName(),'id':t.GetUniqueId(),'duration_frames':t.GetEndFrame()-t.GetStartFrame(),'saved_reopened_matched':True})
assert p.SetCurrentTimeline(ts[expected['episodes'][0]['timeline']])
assert ts[expected['episodes'][0]['timeline']].SetCurrentTimecode('00:00:00:00')
assert pm.SaveProject()
(OUT/'保存重开_11集一致性核验.json').write_text(json.dumps({'project':p.GetName(),'episodes':result,'all_native110_voices_persisted':True,'auditory_acceptance':False},ensure_ascii=False,indent=2),encoding='utf-8')
print('SAVED_REOPENED_ALL_11_MATCH',len(result),flush=True)
