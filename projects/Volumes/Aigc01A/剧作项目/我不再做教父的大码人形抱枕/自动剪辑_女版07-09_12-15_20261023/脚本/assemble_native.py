import argparse,json,datetime
from pathlib import Path
from native_common import *

def main():
    a=argparse.ArgumentParser();a.add_argument('--plan',required=True);a.add_argument('--execute',action='store_true');a.add_argument('--repair-task-episode',type=int);args=a.parse_args()
    plan=load_plan(args.plan)
    if not args.execute:print('Offline plan validation passed');return
    backup=BASE/'大码枕头_女版7集自动剪辑前_20261023.drp';assert backup.is_file() and backup.stat().st_size>100000
    r,m,p,pool=connect();baseline=read(BASE/'剪辑前_项目与时间线实读.json')['timelines']
    ids={x['id'] for x in baseline};assert [x for x in inventory(p) if x['id'] in ids]==baseline
    journalpath=BASE/'Resolve_组装实读.json'
    j=read(journalpath) if journalpath.exists() else {'project':PROJECT,'episodes':[],'baseline_drp':str(backup),'created_at':datetime.datetime.now().isoformat()}
    own={x['id'] for x in j['episodes']};existing={t.GetName():t for t in timelines(p)}
    root=child(pool,pool.GetRootFolder(),BASE.name);allmedia=media(pool.GetRootFolder())
    for e in plan['episodes']:
        folder=child(pool,root,'女版EP%02d'%e['episode'])
        for kind,label in [('video','画面与同期声'),('narration','女版新旁白_100%')]:
            dest=child(pool,folder,label);assert pool.SetCurrentFolder(dest)
            paths=sorted({c['path'] for c in e[kind]});needed=[x for x in paths if x not in allmedia]
            if needed:
                made=pool.ImportMedia(needed);assert made and len(made)==len(needed)
                for x in made:allmedia[x.GetClipProperty('File Path')]=x
            for path in paths:
                x=allmedia[path];assert x.GetClipProperty('Online Status')=='Online'
                if kind=='video':assert float(x.GetClipProperty('FPS'))==24
        t=existing.get(e['timeline_name']);row=next((x for x in j['episodes'] if x['episode']==e['episode']),None)
        digest=sha(args.plan)
        if t:
            assert row and row['id']==t.GetUniqueId() and t.GetUniqueId() in own
            if row['plan_sha256']!=digest and args.repair_task_episode==e['episode']:
                assert t.GetTrackCount('subtitle')==0, 'Repair is limited to owned AV before subtitle insertion'
                assert p.SetCurrentTimeline(t)
                archive=BASE/'修订前可恢复备份';archive.mkdir(exist_ok=True)
                olddrt=archive/(t.GetName()+'_before_source_edge_repair.drt')
                assert not olddrt.exists()
                assert t.Export(str(olddrt),r.EXPORT_DRT)
                write(archive/('EP%02d_修订前轨道快照.json'%e['episode']),dict(row,av_before_repair=av(t)))
                clips=[x for k in ['video','audio'] for i in range(1,t.GetTrackCount(k)+1) for x in t.GetItemListInTrack(k,i) or []]
                assert clips and t.DeleteClips(clips,False)
                assert not any(t.GetItemListInTrack(k,i) for k in ['video','audio'] for i in range(1,t.GetTrackCount(k)+1))
                row.update(plan_sha256=digest,plan_path=str(Path(args.plan).resolve()),status='REBUILDING_OWNED_EPISODE_FROM_REPAIRED_WORD_EDGES',previous_drt=str(olddrt))
                write(journalpath,j);assert m.SaveProject()
            assert row['plan_sha256']==digest, 'Do not resume altered plan on existing edits'
        else:
            assert row is None
            assert pool.SetCurrentFolder(folder)
            t=pool.CreateEmptyTimeline(e['timeline_name']);assert t
            row={'episode':e['episode'],'id':t.GetUniqueId(),'timeline':t.GetName(),'plan_path':str(Path(args.plan).resolve()),'plan_sha256':digest,'status':'CREATED'}
            j['episodes'].append(row);write(journalpath,j);assert m.SaveProject()
        assert p.SetCurrentTimeline(t)
        if not t.GetItemListInTrack('video',1):
            assert t.SetSetting('useCustomSettings','1')
            for key,value in [('timelineFrameRate','24'),('timelineResolutionWidth','1080'),('timelineResolutionHeight','1920')]:
                if str(t.GetSetting(key))!=value:assert t.SetSetting(key,value)
            assert t.SetStartTimecode('00:00:00:00')
            if not any(t.GetItemListInTrack('audio',i) for i in range(1,t.GetTrackCount('audio')+1)):
                if any(t.GetTrackSubType('audio',i).lower()!='stereo' for i in range(1,t.GetTrackCount('audio')+1)):
                    assert t.AddTrack('audio','stereo')
                    for i in range(t.GetTrackCount('audio')-1,0,-1):assert t.DeleteTrack('audio',i)
                while t.GetTrackCount('audio')<2:assert t.AddTrack('audio','stereo')
        assert float(t.GetSetting('timelineFrameRate'))==24 and t.GetStartFrame()==0
        assert t.GetTrackCount('video')==1 and t.GetTrackCount('audio')==2
        for k,i,name in [('video',1,'女版%d_剧情画面'%e['episode']),('audio',1,'同期声_与画面链接'),('audio',2,'女版新旁白_100%')]:
            assert t.SetTrackName(k,i,name);assert t.SetTrackEnable(k,i,True)
        def append(c,k,i,mt):
            matches=[x for x in t.GetItemListInTrack(k,i) or [] if x.GetStart()==c['record_frame']]
            assert len(matches)<=1
            if matches:x=matches[0]
            else:
                made=pool.AppendToTimeline([{'mediaPoolItem':allmedia[c['path']],'startFrame':c['source_start_frame'],
                      'endFrame':c['source_end_frame'],'recordFrame':c['record_frame'],'trackIndex':i,'mediaType':mt}])
                assert made and len(made)==1;x=made[0]
            assert_clip(x,c)
            if k=='audio':
                assert x.SetProperties({'AudioVolumeEnabled':True,'AudioVolume':float(c.get('gain_db',0))})
                assert abs(x.GetProperties()['AudioVolume']-c.get('gain_db',0))<.01
            return x
        for c in e['video']:
            v=append(c,'video',1,1);au=append(c,'audio',1,2)
            assert v.GetSourceEndFrame()==au.GetSourceEndFrame()
            assert t.SetClipsLinked([v,au],True)
            assert au.GetUniqueId() in [x.GetUniqueId() for x in v.GetLinkedItems() or []]
        for c in e['narration']:append(c,'audio',2,2)
        assert len(t.GetItemListInTrack('video',1))==len(e['video'])
        assert len(t.GetItemListInTrack('audio',1))==len(e['video'])
        assert len(t.GetItemListInTrack('audio',2))==len(e['narration'])
        assert t.GetEndFrame()==e['duration_frames']
        row.update(status='NATIVE_AV_ASSEMBLED_SUBTITLES_PENDING',duration_frames=t.GetEndFrame(),fps=24,av_readback=av(t),limitations=e.get('limitations',[]))
        for n,note in enumerate(e.get('limitations',[]),1):
            if n not in (t.GetMarkers() or {}):assert t.AddMarker(n,'Yellow','素材与复核说明',str(note),1)
        assert m.SaveProject();out=BASE/'原生时间线';out.mkdir(exist_ok=True)
        row['drt']=str(out/(t.GetName()+'.drt'));assert t.Export(row['drt'],r.EXPORT_DRT)
        write(journalpath,j)
        print(json.dumps({'episode':e['episode'],'timeline':t.GetName(),'seconds':t.GetEndFrame()/24,'linked_av_clips':len(e['video']),'narration_segments':len(e['narration'])},ensure_ascii=False),flush=True)
    assert [x for x in inventory(p) if x['id'] in ids]==baseline
    write(BASE/'Resolve_组装后时间线清单.json',inventory(p));assert m.SaveProject()
if __name__=='__main__':main()
