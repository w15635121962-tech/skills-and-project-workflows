import hashlib, json, re, sys
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool()
assert p.GetName()=='大码枕头'
ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
gain_rows=json.loads((OUT/'准备/音频QC/实际r2_A1同期对白响度与增益建议.json').read_text(encoding='utf-8'))['records']
names={ep:f'大码_女版_EP{ep}_新旁白110_自动剪辑_'+('v3' if ep==19 else 'v2') for ep in [16,17,18,19]}
names.update({ep:f'大码_女版_EP{ep}_画面同期声_待新旁白_v3' for ep in range(21,26)})
names.update({ep:f'大码_女版_EP{ep}_画面同期声粗排_v1' for ep in [26,28]})
task_folder=next(f for f in mp.GetRootFolder().GetSubFolderList() if f.GetName()=='女版11集自动剪辑_20261020')
delivery=next((f for f in task_folder.GetSubFolderList() or [] if f.GetName()=='本次剪辑_11集'),None) or mp.AddSubFolder(task_folder,'本次剪辑_11集')
assert delivery
report={'project':p.GetName(),'scope':[16,17,18,19,21,22,23,24,25,26,28],
        'jumeng_generation':'No further generation submitted; earlier server job had no cancellation control.',
        'user_direction':'New benchmark female VO for16–19. Other seven episodes picture and synchronized source sound first; no new VO generation.',
        'delivery_bin':'Master/女版11集自动剪辑_20261020/本次剪辑_11集',
        'rendered_video':False,'full_playback_and_auditory_acceptance':False,
        'limits':['Native timeline assembly, source/record mapping, word-timed and waveform boundary inspection verified.',
                  'Native two-frame fade/crossfade pass and full listening acceptance are not claimed.',
                  'EP21 preserves the existing five-frame L-cut and complete dialogue tail.'],
        'episodes':[]}
vo_paths=set()
def source_exists(path):
    if Path(path).exists():return True
    match=re.search(r'\[(\d+)-(\d+)\]',path)
    if not match:return False
    start,end=map(int,match.groups());width=len(match.group(1))
    return all(Path(path[:match.start()]+str(i).zfill(width)+path[match.end():]).exists() for i in range(start,end+1))
for ep,name in names.items():
    t=ts[name];assert p.SetCurrentTimeline(t)
    assert float(t.GetSetting('timelineFrameRate'))==24
    assert str(t.GetSetting('timelineResolutionWidth'))=='1080'
    assert str(t.GetSetting('timelineResolutionHeight'))=='1920'
    plan=None
    if ep in [16,17,18,19]:
        pf=OUT/f'准备/EP{ep}_可执行r2.json';text=pf.read_text(encoding='utf-8');plan=json.loads(text)['episodes'][0]
        assert t.GetEndFrame()==plan['duration_frames']
        v=t.GetItemListInTrack('video',1);assert len(v)==len(plan['video'])
        for x,a in zip(v,plan['video']):
            assert x.GetStart()==a['record_frame'] and x.GetDuration()==a['duration_frames']
            assert x.GetMediaPoolItem().GetClipProperty('File Path')==a['source_path']
            assert abs(x.GetSourceStartTime()-a['source_start_frame']/24)<.001
            if a.get('native_reframe'):
                q=a['native_reframe'];assert x.SetProperties({'ZoomX':q['zoom_x'],'ZoomY':q['zoom_y']})
        # Match gain measurements by source range, not record frame, because
        # EP19's final breath-safe split moved the question one record frame.
        for x in t.GetItemListInTrack('audio',1) or []:
            path=x.GetMediaPoolItem().GetClipProperty('File Path')
            g=next(a for a in gain_rows if a['episode']==ep and a['source_path']==path and abs(a['source_in_s']-x.GetSourceStartTime())<.001 and a['duration_frames']==x.GetDuration())
            gain=min(g['suggested_native_AudioVolume_db'],3.5)
            assert x.SetProperties({'AudioVolumeEnabled':True,'AudioVolume':gain})
        for tr in [1,2,3]:
            actual=t.GetItemListInTrack('audio',tr) or []
            exp=sorted([a for a in plan['audio'] if a['track']==tr],key=lambda a:a['record_frame'])
            assert len(actual)==len(exp),(ep,tr,len(actual),len(exp))
            for x,a in zip(actual,exp):
                assert x.GetStart()==a['record_frame'] and x.GetDuration()==a['duration_frames'],(ep,tr,'record/duration mismatch')
                assert x.GetMediaPoolItem().GetClipProperty('File Path')==a['source_path']
                assert abs(x.GetSourceStartTime()-a['source_start_frame']/24)<.055
                if tr==2:vo_paths.add(a['source_path'])
        assert not [(x.GetStart(),y.GetStart()) for x in t.GetItemListInTrack('audio',1) or [] for y in t.GetItemListInTrack('audio',2) or [] if max(x.GetStart(),y.GetStart())<min(x.GetEnd(),y.GetEnd())]
    elif ep in range(21,26):
        assert not t.GetIsTrackEnabled('audio',2)
        assert t.GetTrackName('subtitle',1)==str(ep)
    else:
        assert not t.GetItemListInTrack('audio',2)
    row={'episode':ep,'timeline':name,'id':t.GetUniqueId(),'start':t.GetStartFrame(),'end':t.GetEndFrame(),'seconds':(t.GetEndFrame()-t.GetStartFrame())/24,'tracks':{},
         'narration':'new benchmark voice, native110%' if ep<20 else 'deferred; old narration muted in working copy' if ep<26 else 'deferred; no new narration',
         'plan_sha256':hashlib.sha256(text.encode('utf-8')).hexdigest() if plan else None}
    for kind in ['video','audio','subtitle']:
        row['tracks'][kind]=[]
        for tr in range(1,t.GetTrackCount(kind)+1):
            track={'index':tr,'name':t.GetTrackName(kind,tr),'enabled':t.GetIsTrackEnabled(kind,tr),'items':[]}
            for x in t.GetItemListInTrack(kind,tr) or []:
                m=x.GetMediaPoolItem();path=m.GetClipProperty('File Path') if m else None
                if path:assert source_exists(path),('Offline path',path)
                track['items'].append({'name':x.GetName(),'start':x.GetStart(),'end':x.GetEnd(),'duration':x.GetDuration(),'source_path':path,'source_start':x.GetSourceStartTime() if m else None,'source_end':x.GetSourceEndTime() if m else None,'properties':x.GetProperties(),'enabled':x.GetClipEnabled()})
            row['tracks'][kind].append(track)
    if ep in [16,17,18,19,26,28]:
        video=row['tracks']['video'][0]['items']
        audio=[a for tr in row['tracks']['audio'] if tr['index'] in [1,3] for a in tr['items']]
        for v in video:
            covers=[a for a in audio if a['source_path']==v['source_path'] and abs((a['source_start']*24-a['start'])-(v['source_start']*24-v['start']))<.1 and a['start']==v['start'] and a['end']==v['end']]
            assert len(covers)==1,(ep,'missing matched source sound',v)
    assert t.Export(str(OUT/'原生时间线'/(name+'.drt')),r.EXPORT_DRT)
    assert t.Export(str(OUT/'原生时间线'/(name+'_最终实读.otio')),r.EXPORT_OTIO)
    mi=t.GetMediaPoolItem()
    if mi.GetUniqueId() not in {m.GetUniqueId() for m in delivery.GetClipList() or []}:
        assert mp.MoveClips([mi],delivery)
    report['episodes'].append(row)
    print(json.dumps({'episode':ep,'timeline':name,'seconds':row['seconds'],'counts':{k:[len(a['items']) for a in v] for k,v in row['tracks'].items()}},ensure_ascii=False),flush=True)
assert len(vo_paths)==29
report['new_narration_unique_sources']=29
assert mp.SetCurrentFolder(delivery)
assert p.SetCurrentTimeline(ts[names[16]])
assert ts[names[16]].SetCurrentTimecode('00:00:00:00')
assert pm.SaveProject()
backup=OUT/'备份/大码枕头_女版11集_剪辑工作版完成.drp'
assert not backup.exists()
assert pm.ExportProject(p.GetName(),str(backup))
report['saved_project_backup']=str(backup)
(OUT/'11集剪辑工作版_最终实读.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('ELEVEN_NATIVE_WORKING_TIMELINES_SAVED',len(report['episodes']),backup.stat().st_size,flush=True)
