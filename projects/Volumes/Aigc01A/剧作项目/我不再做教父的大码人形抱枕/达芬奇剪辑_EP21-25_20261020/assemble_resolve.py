import sys,json,subprocess,re,math
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

OUT=Path(__file__).resolve().parent
PLAN=json.loads((OUT/'剪辑执行计划.json').read_text(encoding='utf-8'))
FF='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'

def level(entry):
    ep,a=entry
    start=a['source_start_frame']/24;duration=(a['source_end_frame_exclusive']-a['source_start_frame'])/24
    cmd=[FF,'-hide_banner','-nostats','-ss',str(start),'-t',str(duration),'-i',a['source_path'],'-vn','-af','loudnorm=I=-18:TP=-1:LRA=11:print_format=json','-f','null','-']
    p=subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,encoding='utf-8',errors='replace')
    assert p.returncode==0,p.stderr[-1000:]
    matches=re.findall(r'\{\s*"input_i".*?\}',p.stderr,re.S);assert matches
    m=json.loads(matches[-1]);i=float(m['input_i']);tp=float(m['input_tp'])
    gain=round(max(-10,min(10,-18-i,-1-tp)),2) if math.isfinite(i) and math.isfinite(tp) else 0
    if 'gain_db' in a:
        gain=min(float(a['gain_db']),-1-tp) if math.isfinite(tp) else float(a['gain_db'])
    return dict(episode=ep,source_path=a['source_path'],source_start_frame=a['source_start_frame'],source_end_frame_exclusive=a['source_end_frame_exclusive'],record_frame=a['record_frame'],track=a['track'],integrated_lufs=i,true_peak_dbtp=tp,gain_db=gain)

level_path=OUT/'音量分析.json'
def audio_key(ep,a):
    return (ep,a['source_path'],a['source_start_frame'],a['source_end_frame_exclusive'],a['record_frame'],a['track'])
levels=json.loads(level_path.read_text(encoding='utf-8')) if level_path.exists() else []
known={audio_key(a['episode'],a) for a in levels}
missing_levels=[(e['episode'],a) for e in PLAN['episodes'] for a in e['audio'] if audio_key(e['episode'],a) not in known]
if missing_levels:
    with ThreadPoolExecutor(max_workers=4) as ex:
        levels+=list(ex.map(level,missing_levels))
    level_path.write_text(json.dumps(levels,ensure_ascii=False,indent=2),encoding='utf-8')

def stage(label,**extra):
    data=dict(stage=label,time=datetime.now().isoformat(),**extra)
    (OUT/'Resolve_组装进度.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(data,ensure_ascii=False),flush=True)
stage('connect')
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject()
assert p and p.GetName()==PLAN['project'],'Unexpected live project'
stage('project_connected',project=p.GetName())
assert r.OpenPage('edit')
mp=p.GetMediaPool();root=mp.GetRootFolder()
assert (OUT/'大码枕头_剪辑前原工程备份.drp').stat().st_size>0
existing_timelines={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
existing_names=set(existing_timelines)

def walk(f):
    d={c.GetClipProperty('File Path'):c for c in f.GetClipList() or [] if c.GetClipProperty('File Path')}
    for child in f.GetSubFolderList() or []:d.update(walk(child))
    return d
media=walk(root)
top=next((f for f in root.GetSubFolderList() or [] if f.GetName()=='EP21-25_剪辑素材'),None)
assert top
working=next((f for f in top.GetSubFolderList() or [] if f.GetName()=='已剪辑时间线与字幕'),None)
if not working:working=mp.AddSubFolder(top,'已剪辑时间线与字幕')
assert working
assert mp.SetCurrentFolder(working)
needed={a['source_path'] for e in PLAN['episodes'] for a in e['video']+e['audio']}
missing=sorted(needed-set(media))
if missing:
    imported=mp.ImportMedia(missing);assert imported and len(imported)==len(missing)
    for a in imported:media[a.GetClipProperty('File Path')]=a

log={'project':p.GetName(),'existing_timelines_preserved':sorted(existing_names),'episodes':[]}
for ep in PLAN['episodes']:
    stage('create_or_recover_timeline',episode=ep['episode'])
    t=existing_timelines.get(ep['timeline_name'])
    if t:
        assert all(not t.GetItemListInTrack(k,i) for k in ['video','audio','subtitle'] for i in range(1,t.GetTrackCount(k)+1)),'Existing work timeline contains edits; inspect before resuming'
    else:t=mp.CreateEmptyTimeline(ep['timeline_name'])
    assert t
    assert p.SetCurrentTimeline(t)
    # Project already has 24fps, 1080x1920. Avoid broad SetSettings, which
    # stalled the running Fusion render lock in the previous attempt.
    settings=t.GetSettings()
    assert str(settings['timelineFrameRate']) in ['24','24.0'],settings
    assert str(settings['timelineResolutionWidth'])=='1080' and str(settings['timelineResolutionHeight'])=='1920',settings
    assert t.SetStartTimecode('00:00:00:00')
    while t.GetTrackCount('audio')<3:assert t.AddTrack('audio','stereo' if t.GetTrackCount('audio')==2 else 'mono')
    assert t.SetTrackName('video',1,'画面_剧情顺序')
    assert t.SetTrackName('audio',1,'原片对白')
    assert t.SetTrackName('audio',2,'Eliza独白')
    assert t.SetTrackName('audio',3,'画面同期声_动作与环境')
    result=dict(episode=ep['episode'],timeline=t.GetName(),timeline_id=t.GetUniqueId(),expected_duration_frames=ep['duration_frames'],video=[],audio=[])
    handles={}
    for kind,key,mt in [('video','video',1),('audio','audio',2)]:
        for a in ep[key]:
            stage('append',episode=ep['episode'],kind=kind,track=a.get('track',1),record_frame=a['record_frame'],source=Path(a['source_path']).name)
            # Resolve 21.1 measured in a disposable timeline: endFrame is
            # exclusive (source 0..144 creates exactly 144 timeline frames).
            infos={'mediaPoolItem':media[a['source_path']],'startFrame':a['source_start_frame'],'endFrame':a['source_end_frame_exclusive'],'recordFrame':a['record_frame'],'trackIndex':a.get('track',1),'mediaType':mt}
            made=mp.AppendToTimeline([infos]);assert made and len(made)==1 and made[0],(ep['episode'],a,'append failed')
            item=made[0]
            assert item.GetStart()==a['record_frame'],(kind,a,'record mismatch',item.GetStart())
            expected_end=a['record_frame']+a['source_end_frame_exclusive']-a['source_start_frame']
            assert item.GetEnd()==expected_end,(kind,a,'end mismatch',item.GetEnd(),expected_end)
            if a.get('properties'):assert item.SetProperties(a['properties']),a
            if kind=='audio':
                lev=next(q for q in levels if audio_key(q['episode'],q)==audio_key(ep['episode'],a))
                assert item.SetProperties({'AudioVolumeEnabled':True,'AudioVolume':lev['gain_db']}),'gain failed'
            result[key].append(dict(a,actual_start=item.GetStart(),actual_end=item.GetEnd(),actual_source_start=item.GetSourceStartFrame(),actual_source_end=item.GetSourceEndFrame(),actual_properties=item.GetProperties()))
            hkey=(a['source_path'],a['source_start_frame'],a['source_end_frame_exclusive'],a['record_frame'])
            handles.setdefault(hkey,[]).append(item)
    for items in handles.values():
        if len(items)==2:assert t.SetClipsLinked(items,True)
    # Also link split ambient clips to the picture whose source mapping
    # they share. Narration and deliberately different picture/dialogue
    # combinations stay independently editable.
    for vi,v in enumerate(ep['video']):
        if not v['source_path'].lower().endswith('.mp4'):continue
        linked=[next(iter(handles[(v['source_path'],v['source_start_frame'],v['source_end_frame_exclusive'],v['record_frame'])]))]
        ve=v['record_frame']+v['source_end_frame_exclusive']-v['source_start_frame']
        for ai,a in enumerate(ep['audio']):
            ae=a['record_frame']+a['source_end_frame_exclusive']-a['source_start_frame']
            if a['source_path']==v['source_path'] and a['source_start_frame']-a['record_frame']==v['source_start_frame']-v['record_frame'] and max(v['record_frame'],a['record_frame'])<min(ve,ae):
                key=(a['source_path'],a['source_start_frame'],a['source_end_frame_exclusive'],a['record_frame'])
                linked.extend(x for x in handles[key] if x not in linked)
        if len(linked)>1:assert t.SetClipsLinked(linked,True)
    for b in ep['blocks']:
        assert t.AddMarker(b['start_frame'],'Blue',b['tag'],'按中文第%d集 / 英文第%d集原稿顺序剪辑。'%(ep['episode'],ep['english_episode']),1)
    assert t.GetStartFrame()==0
    assert t.GetEndFrame()==ep['duration_frames'],(t.GetName(),'timeline end',t.GetEndFrame(),ep['duration_frames'])
    result['actual_duration_frames']=t.GetEndFrame()
    result['settings']=t.GetSettings()
    stage('save',episode=ep['episode'])
    assert pm.SaveProject(),'Save failed'
    drt=OUT/(ep['timeline_name']+'.drt')
    assert t.Export(str(drt),r.EXPORT_DRT),'DRT export failed'
    result['drt']=str(drt)
    log['episodes'].append(result)
    (OUT/'Resolve_组装回读.json').write_text(json.dumps(log,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'episode':ep['episode'],'timeline':t.GetName(),'frames':t.GetEndFrame(),'video':len(result['video']),'audio':len(result['audio'])},ensure_ascii=False),flush=True)
assert pm.SaveProject()
print('All five native timelines created and saved.',flush=True)
