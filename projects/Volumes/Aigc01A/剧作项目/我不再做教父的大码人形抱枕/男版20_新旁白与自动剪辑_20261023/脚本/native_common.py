"""Male EP20 only. Importing this module never connects to Resolve or clicks UI."""
import json,hashlib,sys,math,datetime
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
PROJECT='大码枕头'
EPISODES={20}
TIMELINE='大码_男版_EP20_新男版音色_原速旁白_自动剪辑_20261023_v1'
BASELINE_POINTER=BASE/'active_baseline.json'
DEFAULT_BASELINE_JSON=BASE/'剪辑前_项目与时间线实读.json'
DEFAULT_BACKUP=BASE/'大码枕头_男版EP20自动剪辑前_20261023.drp'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp')
    tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def baseline_paths():
    if not BASELINE_POINTER.exists():return DEFAULT_BASELINE_JSON,DEFAULT_BACKUP
    pointer=read(BASELINE_POINTER)
    assert pointer['project']==PROJECT and pointer['episode']==20
    baseline=Path(pointer['baseline_json']);backup=Path(pointer['backup_drp'])
    assert baseline.is_absolute() and backup.is_absolute()
    assert baseline.parent==BASE and backup.parent==BASE,'Active baseline must remain task-local.'
    return baseline,backup
BASELINE_JSON,BACKUP=baseline_paths()

def connect():
    sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
    from resolve_bootstrap import get_resolve
    r=get_resolve();m=r.GetProjectManager();p=m.GetCurrentProject()
    assert p and p.GetName()==PROJECT, 'Open the exact authorized project; no project switch is automatic.'
    return r,m,p,p.GetMediaPool()
def timelines(p):return [p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)]
def inventory(p):
    return [{'index':i,'name':t.GetName(),'id':t.GetUniqueId(),'fps':float(t.GetSetting('timelineFrameRate')),
             'start':t.GetStartFrame(),'end':t.GetEndFrame(),'vtracks':t.GetTrackCount('video'),
             'atracks':t.GetTrackCount('audio'),'stracks':t.GetTrackCount('subtitle')}
            for i,t in enumerate(timelines(p),1)]
def child(pool,parent,name):
    c=[x for x in parent.GetSubFolderList() or [] if x.GetName()==name];assert len(c)<=1
    f=c[0] if c else pool.AddSubFolder(parent,name);assert f;return f
def media(folder):
    out={}
    for x in folder.GetClipList() or []:
        path=x.GetClipProperty('File Path')
        if path:out.setdefault(path,x)
    for f in folder.GetSubFolderList() or []:out.update(media(f))
    return out
def item_state(x,track_kind):
    # Official API explicitly returns no MediaPoolItem for some native titles,
    # generators and compositions. They are real timeline items, never omissions.
    pool_item=x.GetMediaPoolItem()
    props=x.GetProperty() or {}
    media_props=pool_item.GetClipProperty() if pool_item else None
    return {'id':x.GetUniqueId(),'name':x.GetName(),'track_kind':track_kind,
            'path':pool_item.GetClipProperty('File Path') if pool_item else None,
            'source_binding_type':'media_pool_source' if pool_item else 'native_timeline_item_without_media_pool',
            'media_type':media_props.get('Type') if isinstance(media_props,dict) else None,
            'media_pool_properties':media_props,'timeline_item_properties':props,
            'fusion_composition_count':x.GetFusionCompCount(),
            'fusion_composition_names':x.GetFusionCompNameList() or [],
            'start':x.GetStart(),'end':x.GetEnd(),
            'source_start':x.GetSourceStartFrame(),'source_end':x.GetSourceEndFrame(),
            'enabled':x.GetClipEnabled(),'gain':props.get('AudioVolume'),
            'links':sorted(y.GetUniqueId() for y in x.GetLinkedItems() or [])}
def av(t):
    return {k:[{'index':i,'name':t.GetTrackName(k,i),
                'items':[item_state(x,k) for x in t.GetItemListInTrack(k,i) or []]}
               for i in range(1,t.GetTrackCount(k)+1)] for k in ['video','audio']}
def timeline_state(t):
    return {'id':t.GetUniqueId(),'name':t.GetName(),'av':av(t),
            'settings':{k:t.GetSetting(k) for k in ['timelineFrameRate','timelineResolutionWidth','timelineResolutionHeight']},
            'markers':t.GetMarkers() or {},
            'av_track_controls':[{'kind':k,'index':i,'enabled':t.GetIsTrackEnabled(k,i)}
                                 for k in ['video','audio'] for i in range(1,t.GetTrackCount(k)+1)],
            'subtitles':[{'index':i,'name':t.GetTrackName('subtitle',i),
                          'enabled':t.GetIsTrackEnabled('subtitle',i),
                          'cues':[[x.GetStart(),x.GetEnd(),x.GetName(),x.GetClipEnabled()]
                                  for x in t.GetItemListInTrack('subtitle',i) or []]}
                         for i in range(1,t.GetTrackCount('subtitle')+1)]}
def baseline_semantic_state(state):
    # Clone through the JSON representation used by the saved baseline. This
    # also makes marker/frame keys consistent between live API ints and JSON str.
    value=json.loads(json.dumps(state,ensure_ascii=False))
    for tracks in value.get('av',{}).values():
        for track in tracks:
            for item in track.get('items',[]):
                media_props=item.get('media_pool_properties')
                if isinstance(media_props,dict):
                    # Usage is a derived media-pool occurrence count. Appending
                    # the same source to a NEW timeline changes this count even
                    # when every old timeline item remains byte-for-byte intact.
                    # Exclude only this one exact field, never other metadata.
                    media_props.pop('Usage',None)
                    if item.get('media_type') in ('音频','Audio') or media_props.get('Type') in ('音频','Audio'):
                        # Pure-audio media-pool TC strings follow the ACTIVE
                        # timeline display rate, not the audio sample duration.
                        # Evidence: 原时间线完整状态差异_20261023T063017_774377Z.json
                        # has only these 104 display-field deltas on EP01;
                        # e.g. 00:00:06:20 at 30fps -> 00:00:06:16 at 24fps.
                        # Preserve raw snapshots and all real timeline/source
                        # boundaries, gain, links and every other metadata field.
                        # Video media-pool Duration/End TC remain frozen.
                        media_props.pop('Duration',None)
                        media_props.pop('End TC',None)
    return value
def state_differences(before,after,path='$'):
    """Complete JSON differences, including int/float/null type changes."""
    if type(before) is not type(after):
        return [{'path':path,'change':'type_or_value','before_type':type(before).__name__,
                 'after_type':type(after).__name__,'before':before,'after':after}]
    if isinstance(before,dict):
        result=[]
        for key in sorted(set(before)|set(after)):
            where=path+'['+json.dumps(key,ensure_ascii=False)+']'
            if key not in before:result.append({'path':where,'change':'added','after':after[key]})
            elif key not in after:result.append({'path':where,'change':'removed','before':before[key]})
            else:result.extend(state_differences(before[key],after[key],where))
        return result
    if isinstance(before,list):
        result=[]
        for i in range(max(len(before),len(after))):
            where=f'{path}[{i}]'
            if i>=len(before):result.append({'path':where,'change':'added','after':after[i]})
            elif i>=len(after):result.append({'path':where,'change':'removed','before':before[i]})
            else:result.extend(state_differences(before[i],after[i],where))
        return result
    if json.dumps(before,ensure_ascii=False)!=json.dumps(after,ensure_ascii=False):
        return [{'path':path,'change':'value','before':before,'after':after}]
    return []
def diagnostic_path(kind):
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S_%fZ')
    return BASE/'诊断'/f'{kind}_{stamp}.json'
def assert_task_current(p,t,stage,appended_items=None):
    """Observe only; never switch back when user/application changes context."""
    current=p.GetCurrentTimeline()
    expected={'id':t.GetUniqueId(),'name':t.GetName()}
    actual={'id':current.GetUniqueId(),'name':current.GetName()} if current else None
    if actual and actual['id']==expected['id']:return
    path=diagnostic_path('活动时间线发生变化')
    write(path,{'stage':stage,'expected':expected,'actual':actual,
                'returned_append_items':[{'id':x.GetUniqueId(),'name':x.GetName(),
                                          'start':x.GetStart(),'end':x.GetEnd()} for x in appended_items or []],
                'expected_timeline_state':timeline_state(t),
                'actual_timeline_state':timeline_state(current) if current else None,
                'action':'Stopped immediately; no automatic timeline switch, deletion or rollback was attempted.',
                'atomicity_limit':'The official append call depends on global current timeline. Pre/post guards detect a switch but are not an atomic application lock.'})
    raise AssertionError(('Active timeline changed; inspect diagnostics before continuing',str(path),expected,actual))
def assert_baseline(p):
    assert baseline_paths()==(BASELINE_JSON,BACKUP),'Active baseline changed during this process; restart with the new pointer.'
    baseline=read(BASELINE_JSON)
    assert baseline['project']==PROJECT and baseline['backup_drp']==str(BACKUP)
    assert BACKUP.is_file() and BACKUP.stat().st_size>100000
    assert sha(BACKUP)==baseline['backup_sha256'],'Baseline DRP changed'
    if BASELINE_POINTER.exists():
        pointer=read(BASELINE_POINTER)
        assert sha(BASELINE_JSON)==pointer['baseline_sha256'],'Active raw baseline changed'
        assert sha(BACKUP)==pointer['backup_sha256'],'Active DRP changed'
    ids={x['id'] for x in baseline['timelines']}
    now_inventory=[x for x in inventory(p) if x['id'] in ids]
    if now_inventory!=baseline['timelines']:
        path=diagnostic_path('原时间线清单差异')
        write(path,{'before':baseline['timelines'],'after':now_inventory,
                    'differences':state_differences(baseline['timelines'],now_inventory),
                    'baseline_path':str(BASELINE_JSON),'baseline_file_sha256':sha(BASELINE_JSON),
                    'action':'Read-only diagnostic; unknown differences remain blocking.'})
        raise AssertionError(('Existing timeline inventory changed',str(path)))
    live={x.GetUniqueId():x for x in timelines(p)}
    entrance=p.GetCurrentTimeline();assert entrance,'Baseline context needs an entrance timeline to restore.'
    entrance_id=entrance.GetUniqueId()
    # Resolve returns inactive-track flags as false and omits these eight AI
    # properties until that timeline is active. Reproduce the saved context;
    # never discard these real fields. Evidence: 活动与非活动时间线上下文回读差异.json.
    ai_keys={'AudioVoiceIsolationEnabled','AudioVoiceIsolationAmount',
             'AudioDialogueLevelerEnabled','AudioDialogueLevelerMode',
             'AudioDialogueLevelerReduceLoudDialogue','AudioDialogueLevelerLiftSoftDialogue',
             'AudioDialogueLevelerBackgroundReduction','AudioDialogueLevelerOutputGain'}
    def active_evidence(state):
        evidence=[]
        if any(x.get('enabled') is True for x in state.get('av_track_controls',[])):
            evidence.append('saved_av_track_enabled')
        if any(x.get('enabled') is True for x in state.get('subtitles',[])):
            evidence.append('saved_subtitle_track_enabled')
        found=set()
        for tracks in state.get('av',{}).values():
            for track in tracks:
                for item in track.get('items',[]):
                    found.update(ai_keys.intersection(item.get('timeline_item_properties') or {}))
        if found:evidence.append({'saved_ai_property_keys':sorted(found)})
        return evidence
    contexts={old['id']:active_evidence(old['state']) for old in baseline['timeline_states']}
    active_ids=[uid for uid,evidence in contexts.items() if evidence]
    context_path=diagnostic_path('原时间线按基线上下文回读')
    context_log={'entrance_id':entrance_id,'entrance_name':entrance.GetName(),
                 'baseline_path':str(BASELINE_JSON),'reads':[],'switches':[],
                 'all_context_fields_strictly_compared':True}
    def current_id():
        current=p.GetCurrentTimeline()
        return current.GetUniqueId() if current else None
    def select_context(t,reason):
        uid=t.GetUniqueId();previous=current_id()
        if previous!=uid:
            result=p.SetCurrentTimeline(t)
            observed=current_id()
            context_log['switches'].append({'reason':reason,'from_id':previous,'to_id':uid,
                                            'api_result':result,'observed_id':observed})
            assert result and observed==uid,('Unable to select baseline read context',reason,uid,observed)
    try:
        for old in baseline['timeline_states']:
            assert old['id'] in live,('Existing timeline missing',old['name'])
            evidence=contexts[old['id']]
            row={'id':old['id'],'name':old['name'],'saved_context':'active' if evidence else 'inactive',
                 'inference_evidence':evidence}
            context_log['reads'].append(row)
            try:
                if evidence:
                    select_context(live[old['id']],'match_saved_active_context')
                elif current_id()==old['id']:
                    # Normally entrance is the new EP20 task. This fallback
                    # also preserves an inactive saved context if an old
                    # timeline happens to be the caller's entrance timeline.
                    parking=next((live[uid] for uid in active_ids if uid!=old['id'] and uid in live),None)
                    assert parking,'No alternate context available for saved-inactive read.'
                    select_context(parking,'keep_saved_inactive_timeline_inactive')
                row['current_id_at_read']=current_id()
                assert (row['current_id_at_read']==old['id'])==bool(evidence)
                raw_after=timeline_state(live[old['id']])
            finally:
                select_context(entrance,'restore_caller_after_baseline_read')
                row['restored_entrance_id']=current_id()
                assert row['restored_entrance_id']==entrance_id
            before=baseline_semantic_state(old['state'])
            after=baseline_semantic_state(raw_after)
            if digest(before)!=digest(after):
                path=diagnostic_path('原时间线完整状态差异')
                current=p.GetCurrentTimeline()
                write(path,{'timeline_id':old['id'],'timeline_name':old['name'],
                            'current_timeline_at_failure':{'id':current.GetUniqueId(),'name':current.GetName()} if current else None,
                            'baseline_context_log':str(context_path),
                            'baseline_path':str(BASELINE_JSON),'baseline_file_sha256':sha(BASELINE_JSON),
                            'archived_original_state_sha256':old['state_sha256'],
                            'raw_before':old['state'],'raw_after':raw_after,
                            'semantic_before':before,'semantic_after':after,
                            'semantic_before_sha256':digest(before),'semantic_after_sha256':digest(after),
                            'differences':state_differences(before,after),
                            'ignored_exact_fields':['media_pool_properties.Usage',
                                                    'media_pool_properties.Duration only for Type/media_type Audio or 音频',
                                                    'media_pool_properties.End TC only for Type/media_type Audio or 音频'],
                            'action':'Read-only complete failure capture in the saved active/inactive context. No AI/track field was excluded and no original state was changed.'})
                raise AssertionError(('Existing timeline media/captions/markers changed',old['name'],str(path)))
        context_log['all_original_states_match']=True
    finally:
        try:
            select_context(entrance,'final_restore_caller')
            context_log['final_current_id']=current_id()
            context_log['entrance_restored']=context_log['final_current_id']==entrance_id
            assert context_log['entrance_restored'],'Caller timeline was not restored.'
        finally:
            write(context_path,context_log)
    return baseline

def asr_path(source,kind):
    return BASE/'ASR/raw_large-v3-turbo'/kind/(Path(source).stem+'.json')
def expected_narration():
    return {str(BASE/'音频/第20集'/f'大码男版枕头20-{i:02d}-01.mp3') for i in range(1,10)}
def event_record_range(ev):
    offset=ev['record_frame']-ev.get('clip_source_start_frame',ev['source_start_frame'])
    return (ev.get('event_record_start_frame',ev['source_start_frame']+offset),
            ev.get('event_record_end_frame',ev['source_end_frame']+offset))
def load_plan(path,allow_pending=False):
    p=read(path)
    assert p['project']==PROJECT and p['fps']==24
    allowed_status={'READY_FOR_NATIVE_ASSEMBLY'}
    if allow_pending:allowed_status.add('READY_FOR_NATIVE_ASSEMBLY_WAITING_INDEPENDENT_REVIEW')
    assert p['status'] in allowed_status,'Independent review must finish before --execute.'
    assert len(p['episodes'])==1 and p['episodes'][0]['episode']==20
    inv=read(BASE/'准备/素材盘点.json')
    sources={r['path']:r for r in inv['files'] if r['kind']=='video' and r['episode']==20}
    narr=expected_narration()
    # No stale voice or female media fallback: all nine current-task MP3s and
    # their independent ASR hashes must exist before any native assembly.
    for source in narr:
        assert Path(source).is_file(),('Missing new male narration',source)
        raw=read(asr_path(source,'narration'))
        assert raw['source_path']==source and raw['source_sha256']==sha(source),('Narration ASR/source hash mismatch',source)
    for e in p['episodes']:
        assert e['timeline_name']==TIMELINE
        for kind in ['video','narration']:
            last=0;ranges={};assert e[kind]
            for c in e[kind]:
                source=c['path'];assert source in (sources if kind=='video' else narr),('Wrong version/source',source)
                assert Path(source).is_file()
                s,z,r=[c[k] for k in ['source_start_frame','source_end_frame','record_frame']]
                assert all(isinstance(v,int) for v in [s,z,r]) and 0<=s<z and r>=last
                if kind=='video':
                    assert r==last,('Picture gap',last,r)
                    row=sources[source]
                    assert row['sha256']==sha(source),'Source video changed after inventory'
                    assert row['audio_stream_count']>=1 and row['video_streams'][0]['fps']==24
                    assert z<=row['video_streams'][0]['nb_frames'],'Source end outside real picture frames'
                else:
                    raw=read(asr_path(source,'narration'))
                    duration=raw.get('decoded_duration_seconds') or raw.get('source_duration_seconds')
                    assert duration and z<=math.ceil(float(duration)*24),('VO range outside source',source)
                assert c.get('speed_percent',100)==100
                c['duration_frames']=z-s
                last=r+z-s;assert last<=e['duration_frames']
                for a,b in ranges.setdefault(source,[]):assert z<=a or s>=b,('Repeated source frames',c)
                ranges[source].append((s,z))
            if kind=='video':assert last==e['duration_frames']
        assert {c['path'] for c in e['narration']}==narr,'Every approved new narration segment must be accounted for'
        for ev in e['audio_events']:
            assert ev['canonical_text'].strip() and ev['source_path'] in set(sources)|narr
            a,z=event_record_range(ev);assert 0<=a<z<=e['duration_frames']
            if ev['kind'] in ['dialogue','sync_dialogue','character_dialogue']:
                for c in e['narration']:
                    ns=c['record_frame'];ne=ns+c['duration_frames']
                    assert max(a,ns)>=min(z,ne),('VO and dialogue overlap',ev,c)
    return p
def assert_clip(item,c):
    assert item.GetStart()==c['record_frame']
    assert item.GetEnd()==c['record_frame']+c['duration_frames']
    assert item.GetSourceStartFrame()==c['source_start_frame']
    assert item.GetMediaPoolItem().GetClipProperty('File Path')==c['path']
    assert item.GetClipEnabled()
