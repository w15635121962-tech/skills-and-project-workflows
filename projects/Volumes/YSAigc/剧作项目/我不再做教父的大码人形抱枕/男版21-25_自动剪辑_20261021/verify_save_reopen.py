import json,sys,datetime
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
out=Path(__file__).resolve().parent
manifest=json.loads((out/'Resolve_组装实读.json').read_text(encoding='utf-8'))
assert sorted(x['episode'] for x in manifest['episodes'])==[21,22,23,24,25]
before=json.loads((out/'Resolve_操作前实读.json').read_text(encoding='utf-8'))
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='大码枕头'
mp=p.GetMediaPool();root=mp.GetRootFolder()
partial=next((p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)
              if p.GetTimelineByIndex(i).GetName()=='男版EP24_接口中断草稿_不使用'),None)
if partial:
    folders=[f for f in root.GetSubFolderList() or [] if f.GetName()=='备份_男版剪辑中断草稿']
    dest=folders[0] if folders else mp.AddSubFolder(root,'备份_男版剪辑中断草稿')
    assert dest and mp.MoveClips([partial.GetMediaPoolItem()],dest)
assert pm.SaveProject()
assert pm.CloseProject(p)
p=pm.LoadProject('大码枕头');assert p and p.GetName()=='大码枕头'
timelines={p.GetTimelineByIndex(i).GetUniqueId():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
report={'checked_at':datetime.datetime.now().isoformat(),'project':p.GetName(),
        'saved_and_reopened':True,'previous_timelines_preserved':[],'episodes':[],
        'playback_scope':'EP21已试播并观察到播放时间码推进；五集未完成逐句正常速度实听，不能据结构核验声称完整听验。',
        'source_issue':'EP21源稿Did she want me back in Veriston?未找到21-5-2音频；已在EP21时间线黄标中记录，不合成替代。'}
for old in before['timelines']:
    t=timelines[old['id']];assert t.GetName()==old['name']
    assert t.GetStartFrame()==old['start'] and t.GetEndFrame()==old['end']
    for kind,tracks in old['tracks'].items():
        assert t.GetTrackCount(kind)==len(tracks)
        for a in tracks:
            assert len(t.GetItemListInTrack(kind,a['index']) or [])==a['count']
    report['previous_timelines_preserved'].append({'name':old['name'],'id':old['id'],'duration_and_track_counts_unchanged':True})
for ep in sorted(manifest['episodes'],key=lambda x:x['episode']):
    t=timelines[ep['id']];assert p.SetCurrentTimeline(t)
    assert t.GetEndFrame()==ep['duration_frames'] and t.GetStartFrame()==0
    v=t.GetItemListInTrack('video',1) or [];a=t.GetItemListInTrack('audio',1) or [];vo=t.GetItemListInTrack('audio',2) or []
    assert len(v)==len(ep['video']) and len(a)==len(ep['sync_audio']) and len(vo)==len(ep['narration'])
    assert len(a)==len(v),'Every motion picture must carry synchronous audio'
    cursor=0;checks=[]
    for vi,ai,expected in zip(v,a,ep['video']):
        assert vi.GetStart()==cursor;cursor=vi.GetEnd()
        assert vi.GetStart()==ai.GetStart() and vi.GetEnd()==ai.GetEnd()
        assert vi.GetSourceStartFrame()==ai.GetSourceStartFrame()
        assert vi.GetSourceEndFrame()==ai.GetSourceEndFrame()
        assert vi.GetMediaPoolItem().GetClipProperty('File Path')==ai.GetMediaPoolItem().GetClipProperty('File Path')==expected['path']
        assert '/男版/' in expected['path']
        assert vi.GetClipEnabled() and ai.GetClipEnabled()
        assert ai.GetUniqueId() in [x.GetUniqueId() for x in vi.GetLinkedItems() or []]
        assert vi.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
        assert abs(ai.GetProperties()['AudioVolume']-expected['gain_db'])<.01
        checks.append({'video':vi.GetUniqueId(),'sync_audio':ai.GetUniqueId(),'start':vi.GetStart(),'end':vi.GetEnd(),
                       'source_start':vi.GetSourceStartFrame(),'source_end':vi.GetSourceEndFrame(),'same_source_and_cuts':True,'linked':True,'enabled':True})
    assert cursor==t.GetEndFrame()
    for x,expected in zip(vo,ep['narration']):
        assert x.GetStart()==expected['start'] and x.GetEnd()==expected['end']
        assert x.GetSourceStartFrame()==expected['source_start'] and x.GetSourceEndFrame()==expected['source_end']
        assert x.GetClipEnabled() and x.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
        assert abs(x.GetProperties()['AudioVolume']-expected['gain_db'])<.01
    assert t.GetIsTrackEnabled('video',1) and t.GetIsTrackEnabled('audio',1) and t.GetIsTrackEnabled('audio',2)
    if ep['episode']==21:
        # Marker 0 is occupied by a narrative marker; warnings live at frames 1,2.
        markers=t.GetMarkers() or {}
        for i,note in enumerate(ep.get('limitations',[]),1):
            if i not in markers:assert t.AddMarker(i,'Yellow','源素材待补',note,1)
    assert t.Export(ep['drt'],r.EXPORT_DRT)
    assert t.Export(ep['otio'],r.EXPORT_OTIO)
    report['episodes'].append({'episode':ep['episode'],'timeline':t.GetName(),'id':t.GetUniqueId(),
        'duration_frames':t.GetEndFrame(),'seconds':t.GetEndFrame()/24,'video_clips':len(v),'linked_sync_clips':len(a),
        'original_speed_narration_clips':len(vo),'no_video_gaps':True,'media_online':True,'av_checks':checks})
first=timelines[next(x['id'] for x in manifest['episodes'] if x['episode']==21)]
assert p.SetCurrentTimeline(first) and first.SetCurrentTimecode('00:00:00:00')
parent=next(f for f in p.GetMediaPool().GetRootFolder().GetSubFolderList() if f.GetName()=='男版21-25_自动剪辑_20261021')
assert p.GetMediaPool().SetCurrentFolder(parent)
assert pm.SaveProject()
backup=out/'大码枕头_男版21-25原速旁白自动剪辑_v1.drp'
assert pm.ExportProject(p.GetName(),str(backup)) and backup.stat().st_size>0
report['project_export']=str(backup);report['project_export_bytes']=backup.stat().st_size
(out/'Resolve_保存重开最终核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'saved_and_reopened':True,'original_timelines_preserved':len(report['previous_timelines_preserved']),
                  'episodes':[{k:v for k,v in x.items() if k!='av_checks'} for x in report['episodes']],
                  'backup_bytes':backup.stat().st_size},ensure_ascii=False),flush=True)
