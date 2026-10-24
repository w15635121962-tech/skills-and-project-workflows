"""Build native editable timelines from an explicit reviewed source-frame plan.

The OTIO media/effect templates come from this running Resolve project's own
exports. Only new task-owned timelines are created; existing edits are retained.
"""
import copy, json, math, os, sys
from pathlib import Path

sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
PLAN=Path(sys.argv[1]).resolve()
data=json.loads(PLAN.read_text(encoding='utf-8'))
requested=set(map(int,sys.argv[2:])) if len(sys.argv)>2 else {16,17,18,19}
raw=json.loads((OUT/'准备/新旁白29条_原生110_音量校准.otio').read_text(encoding='utf-8'))
templates={'video':{},'audio':{},'vo':{}}
track_templates={}
def path_of(c):
    return c['media_references'][c['active_media_reference_key']]['target_url']
for tr in raw['tracks']['children']:
    if tr['kind']=='Audio':
        track_templates['vo']=tr
        for c in tr['children']:
            if c['OTIO_SCHEMA'].startswith('Clip'):templates['vo'][path_of(c)]=c
for f in (OUT/'原生时间线').glob('*画面同期声粗排_v1.otio'):
    d=json.loads(f.read_text(encoding='utf-8'))
    for tr in d['tracks']['children']:
        kind=tr['kind'].lower()
        track_templates.setdefault(kind,tr)
        for c in tr['children']:
            if c['OTIO_SCHEMA'].startswith('Clip'):templates[kind][path_of(c)]=c

gains={x['source']:x['suggested_native_AudioVolume_db'] for x in json.loads((OUT/'准备/音频QC/29条新旁白响度与原生增益建议.json').read_text(encoding='utf-8'))['records']}
def rational(value):return {'OTIO_SCHEMA':'RationalTime.1','rate':24.0,'value':float(value)}
def gap(n):
    assert n>0
    return {'OTIO_SCHEMA':'Gap.1','metadata':{},'name':'','source_range':{'OTIO_SCHEMA':'TimeRange.1','duration':rational(n),'start_time':rational(0)},'effects':[],'markers':[],'enabled':True}
def clip(entry,kind):
    src=entry['source_path'];start=entry['source_start_frame'];end=entry['source_end_frame_exclusive']
    speed=entry.get('speed_percent',100)
    assert end>start>=0
    if kind=='video':assert speed==100
    category='vo' if speed==110 else kind
    if src in templates[category]:
        c=copy.deepcopy(templates[category][src])
    else:
        assert category in ['video','audio'], ('Missing narration template',src)
        c=copy.deepcopy(next(iter(templates[category].values())))
        c['name']=Path(src).name
        ref=c['media_references'][c['active_media_reference_key']]
        ref['name']=Path(src).name
        ref['target_url']=src
        ref['available_range']=None
    duration=int(entry.get('duration_frames',round((end-start)/(speed/100))))
    assert duration>0
    c['source_range']['start_time']=rational(start)
    c['source_range']['duration']=rational(duration)
    c['enabled']=True
    c['metadata'].setdefault('Resolve_OTIO',{}).pop('Link Group ID',None)
    if speed==110:
        warp=[f for f in c['effects'] if f['OTIO_SCHEMA'].startswith('LinearTimeWarp')]
        assert len(warp)==1
        warp[0]['time_scalar']=1.1
    else:
        c['effects']=[f for f in c['effects'] if not f['OTIO_SCHEMA'].startswith('LinearTimeWarp')]
    return c,duration
def make_track(entries,kind,name):
    t=copy.deepcopy(track_templates['vo' if kind=='vo' else kind])
    t['name']=name;t['children']=[];t['enabled']=True
    cursor=0
    for entry in sorted(entries,key=lambda a:a['record_frame']):
        rec=int(entry['record_frame'])
        assert rec>=cursor,(name,'overlap',rec,cursor)
        if rec>cursor:t['children'].append(gap(rec-cursor))
        c,n=clip(entry,'audio' if kind=='vo' else kind)
        t['children'].append(c);cursor=rec+n
    return t

r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool()
assert p.GetName()=='大码枕头'
existing={p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)}
logpath=OUT/'Resolve_新旁白4集剪辑回读.json'
log=json.loads(logpath.read_text(encoding='utf-8')) if logpath.exists() else []
for e in data['episodes']:
    ep=e['episode']
    if ep not in requested:continue
    assert e.get('final_narration_mix_ready',True),f'EP{ep} timing is not ready'
    revision=os.environ.get('ELIZA_EDIT_VERSION','v2')
    assert revision in ['v2','v3']
    name=f'大码_女版_EP{ep}_新旁白110_自动剪辑_{revision}'
    assert name not in existing,'Preserve existing timeline: '+name
    videos=e['video'];audios=e['audio'];assert videos and audios
    for a in audios:
        assert a['track'] in [1,2,3]
        assert a.get('speed_percent',100)==(110 if a['track']==2 else 100)
    d=copy.deepcopy(raw);d['name']=name;d['tracks']['children']=[]
    d['tracks']['children'].append(make_track(videos,'video','画面_剧情顺序'))
    for idx,label in [(1,'原片对白_100'),(2,'新对标女旁白_110'),(3,'同期声_动作与环境_100')]:
        d['tracks']['children'].append(make_track([a for a in audios if a['track']==idx],'vo' if idx==2 else 'audio',label))
    f=OUT/'原生时间线'/(name+'.otio');f.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    t=mp.ImportTimelineFromFile(str(f),{'timelineName':name,'importSourceClips':True});assert t
    assert p.SetCurrentTimeline(t)
    assert t.SetStartTimecode('00:00:00:00')
    assert float(t.GetSetting('timelineFrameRate'))==24
    actual={'episode':ep,'timeline':name,'id':t.GetUniqueId(),'settings':t.GetSettings(),'plan':str(PLAN),'tracks':{}}
    for kind,entries in [('video',videos),('audio',audios)]:
        actual['tracks'][kind]=[]
        for track in range(1,t.GetTrackCount(kind)+1):
            items=t.GetItemListInTrack(kind,track) or []
            expected=sorted([a for a in entries if (a.get('track',1) if kind=='audio' else 1)==track],key=lambda a:a['record_frame'])
            assert len(items)==len(expected),(ep,kind,track,len(items),len(expected))
            for x,a in zip(items,expected):
                m=x.GetMediaPoolItem();assert m,(ep,'offline clip',x.GetName())
                assert m.GetClipProperty('File Path')==a['source_path']
                assert x.GetStart()==a['record_frame'],(ep,x.GetName(),'record mismatch')
                expected_duration=int(a.get('duration_frames',round((a['source_end_frame_exclusive']-a['source_start_frame'])/(a.get('speed_percent',100)/100))))
                assert x.GetDuration()==expected_duration,(ep,x.GetName(),x.GetDuration(),expected_duration)
                src_time=x.GetSourceStartTime()
                assert abs(src_time-a['source_start_frame']/24)<.055,(ep,x.GetName(),'source offset',src_time,a['source_start_frame']/24)
                if kind=='audio':
                    gain=gains[a['source_path']] if track==2 else a.get('gain_db',0)
                    assert x.SetProperties({'AudioVolumeEnabled':True,'AudioVolume':gain})
                actual['tracks'][kind].append({'track':track,'name':x.GetName(),'start':x.GetStart(),'end':x.GetEnd(),'source_path':m.GetClipProperty('File Path'),'source_start_frame':x.GetSourceStartFrame(),'source_end_frame':x.GetSourceEndFrame(),'source_start_seconds':src_time,'source_end_seconds':x.GetSourceEndTime(),'properties':x.GetProperties()})
    # Restore native links between picture and every overlapping sound segment
    # with the same source-to-record mapping. VO stays independently editable.
    for v in t.GetItemListInTrack('video',1) or []:
        linked=[v];vp=v.GetMediaPoolItem().GetClipProperty('File Path')
        for track in [1,3]:
            for a in t.GetItemListInTrack('audio',track) or []:
                if (a.GetMediaPoolItem().GetClipProperty('File Path')==vp and
                    abs((a.GetSourceStartTime()*24-a.GetStart())-(v.GetSourceStartTime()*24-v.GetStart()))<.1 and
                    max(a.GetStart(),v.GetStart())<min(a.GetEnd(),v.GetEnd())):linked.append(a)
        if len(linked)>1:assert t.SetClipsLinked(linked,True)
    actual['duration_frames']=t.GetEndFrame()
    assert actual['duration_frames']==e['duration_frames'],(ep,'timeline duration',actual['duration_frames'],e['duration_frames'])
    assert pm.SaveProject()
    assert t.Export(str(OUT/'原生时间线'/(name+'.drt')),r.EXPORT_DRT)
    assert t.Export(str(OUT/'原生时间线'/(name+'_回读.otio')),r.EXPORT_OTIO)
    log.append(actual);logpath.write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'episode':ep,'timeline':name,'seconds':actual['duration_frames']/24,'video':len(videos),'audio':len(audios)},ensure_ascii=False),flush=True)
