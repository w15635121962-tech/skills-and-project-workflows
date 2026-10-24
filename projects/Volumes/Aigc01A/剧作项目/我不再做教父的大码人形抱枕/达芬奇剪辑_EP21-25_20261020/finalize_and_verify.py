import json,sys,hashlib
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
plan=json.loads((OUT/'剪辑执行计划.json').read_text(encoding='utf-8'))
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject()
assert p.GetName()=='大码枕头'
assert pm.SaveProject()
assert pm.CloseProject(p)
p=pm.LoadProject('大码枕头');assert p
assert p.GetName()=='大码枕头'
timelines={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
result={'project':p.GetName(),'saved_closed_and_reloaded':True,'episodes':[],'existing_timelines_unchanged':True,'source_audio_lip_sync_audition_claimed':False}

def get_item(a):
    m=a.GetMediaPoolItem()
    return {'name':a.GetName(),'start':a.GetStart(),'end':a.GetEnd(),'source_path':m.GetClipProperty('File Path') if m else None,'source_start':a.GetSourceStartFrame() if m else None,'source_end_raw':a.GetSourceEndFrame() if m else None,'properties':a.GetProperties(),'enabled':a.GetClipEnabled()}

for e in plan['episodes']:
    t=timelines[e['timeline_name']];assert p.SetCurrentTimeline(t)
    settings=t.GetSettings();assert float(settings['timelineFrameRate'])==24
    assert settings['timelineResolutionWidth']=='1080' and settings['timelineResolutionHeight']=='1920'
    actual={'episode':e['episode'],'name':t.GetName(),'start':t.GetStartFrame(),'end':t.GetEndFrame(),'tracks':{},'subtitle_count':0}
    for kind in ['video','audio','subtitle']:
        actual['tracks'][kind]=[]
        for tr in range(1,t.GetTrackCount(kind)+1):
            on=t.GetIsTrackEnabled(kind,tr)
            assert on,(e['episode'],kind,tr,'track not enabled')
            items=[get_item(a) for a in t.GetItemListInTrack(kind,tr) or []]
            actual['tracks'][kind].append({'track':tr,'name':t.GetTrackName(kind,tr),'enabled':on,'items':items})
            if kind=='subtitle':actual['subtitle_count']+=len(items)
    assert actual['end']==e['duration_frames']
    for key in ['video','audio']:
        expected=e[key]
        observed=[(tr['track'],a) for tr in actual['tracks'][key] for a in tr['items']]
        assert len(expected)==len(observed),(e['episode'],key,'item count',len(expected),len(observed))
        for a in expected:
            matches=[q for tr,q in observed if tr==a.get('track',1) and q['start']==a['record_frame'] and q['source_path']==a['source_path']]
            assert len(matches)==1,(e['episode'],key,a,'missing/duplicated')
            q=matches[0]
            assert q['source_start']==a['source_start_frame']
            assert q['end']-q['start']==a['source_end_frame_exclusive']-a['source_start_frame']
            assert q['enabled']
    for v in actual['tracks']['video'][0]['items']:
        if not v['source_path'].lower().endswith('.mp4'):continue
        covered=[]
        for tr in actual['tracks']['audio']:
            for a in tr['items']:
                if a['source_path']==v['source_path'] and a['source_start']-a['start']==v['source_start']-v['start']:
                    s=max(a['start'],v['start']);end=min(a['end'],v['end'])
                    if s<end:covered.append((s,end))
        cur=v['start']
        for s,end in sorted(covered):
            assert s==cur,(e['episode'],v['name'],'gap or duplicate audio',cur,s)
            cur=end
        assert cur==v['end'],(e['episode'],v['name'],'source audio missing tail')
    actual['all_mp4_picture_frames_have_matching_source_audio']=True
    drt=OUT/(e['timeline_name']+'_含同期声.drt')
    if drt.exists():drt.unlink()
    assert t.Export(str(drt),r.EXPORT_DRT)
    actual['drt']=str(drt)
    result['episodes'].append(actual)
    print(json.dumps({'episode':e['episode'],'duration_frames':actual['end'],'audio_tracks_enabled':[q['enabled'] for q in actual['tracks']['audio']],'sync_coverage':'100%','subtitles':actual['subtitle_count']},ensure_ascii=False),flush=True)

before=json.loads((OUT/'Resolve_操作前完整实读.json').read_text(encoding='utf-8'))
for old in before['timelines']:
    t=timelines[old['name']]
    assert t.GetEndFrame()==old['end']
    for kind in ['video','audio','subtitle']:
        assert t.GetTrackCount(kind)==len(old['tracks'][kind])
        for tr in old['tracks'][kind]:
            items=t.GetItemListInTrack(kind,tr['track']) or []
            assert len(items)==tr['count'],(old['name'],kind,'existing count changed')
            for a,b in zip(items,tr['items']):
                m=a.GetMediaPoolItem();path=m.GetClipProperty('File Path') if m else None
                assert a.GetStart()==b['start'] and a.GetEnd()==b['end'] and path==b['source_path'],(old['name'],kind,'existing item changed')

assert p.SetCurrentTimeline(timelines['大码_女版_EP21_剧情剪辑_v1'])
assert p.GetCurrentTimeline().SetCurrentTimecode('00:00:00:00')
assert pm.SaveProject()
drp=OUT/'大码枕头_EP21-25_剪辑与同期声完成.drp'
if drp.exists():drp.unlink()
assert pm.ExportProject(p.GetName(),str(drp),True)
assert drp.stat().st_size>0
result['final_project_backup']=str(drp)
result['srt_files']=[{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in sorted((OUT/'SRT').glob('EP*.srt'))]
(OUT/'Resolve_保存重开_同期声最终核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Final project saved, reloaded, verified and backed up.',flush=True)
