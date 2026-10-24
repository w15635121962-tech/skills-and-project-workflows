"""Read-only offline validation of the frozen five-episode assembly plan."""
from pathlib import Path
import json, hashlib, re, datetime, collections, math
B=Path(__file__).resolve().parent.parent; OUT=Path(__file__).resolve().parent
P=OUT/'final_native_plan.json'; plan=json.loads(P.read_text()); scope=[9,10,11,13,14]
assert plan['scope']==scope and [e['episode']for e in plan['episodes']]==scope
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=json.loads((B/'准备/narration_manifest.json').read_text())
picks=json.loads((OUT/'五集采用清单.json').read_text()); chosen={r['selected_audio_path']:r for r in picks['selections']}
assert len(chosen)==32
inventory=json.loads((B/'剪辑脚本准备/media_inventory_native.json').read_text())
vids={r['path']:r for e in inventory['episodes'] for r in e['videos']}
units=json.loads((B/'ASR/同期对白与原带音轨核查.json').read_text())['dialogue_units']
check_paths=[P,OUT/'五集采用清单.json']+[Path(e['subtitle_srt']) for e in plan['episodes']]+[Path(x['path'])for x in plan['source_plan_provenance']]
before={str(p):sha(p)for p in check_paths}
norm=lambda s:re.sub(r'[^a-z0-9]+','',s.lower())
def tokens(s):return [norm(x)for x in s.split()if norm(x)]
def end(c):return c['record_frame']+c['source_end_frame']-c['source_start_frame']
def cover(cs,path,lo,hi,tol=0):
    parts=sorted((c['record_frame'],end(c))for c in cs if c['path']==path);pos=lo
    for a,z in parts:
        if a>pos+tol:continue
        if z>=pos-tol:pos=max(pos,z)
        if pos>=hi-tol:return True
    return False

def parse_srt(path):
    rows=[]
    def ms(s):
        a,b,c,d=map(int,re.split(r'[:,]',s));return ((a*60+b)*60+c)*1000+d
    for block in re.split(r'\n\s*\n',Path(path).read_text(encoding='utf-8-sig').strip()):
        ln=block.splitlines();m=re.fullmatch(r'(\d\d:\d\d:\d\d,\d{3}) --> (\d\d:\d\d:\d\d,\d{3})',ln[1]);assert m
        rows.append({'number':int(ln[0]),'start_ms':ms(m[1]),'end_ms':ms(m[2]),'lines':ln[2:]})
    return rows
report=[]
for ep in plan['episodes']:
    n=ep['episode']
    eventpath=B/(f'EP{n:02}_原文词事件.json'if n<12 else f'剪辑脚本准备/EP{n:02}_原文词事件.json')
    events=json.loads(eventpath.read_text())['episodes'][0]['events']
    me=next(e for e in manifest['episodes']if e['episode']==n)
    orig_tokens=tokens(' '.join(r['raw_source_text']for r in me['original_paragraphs_and_retained_narration']))
    assert orig_tokens==tokens(' '.join(w['word']for w in events)),('original words',n)
    assert len(events)==len(orig_tokens)
    for kind in ['video','narration']:
        bypath=collections.defaultdict(list);prev=0
        for c in ep[kind]:
            assert c.get('speed_percent',100)==100
            assert all(isinstance(c[x],int)for x in ['source_start_frame','source_end_frame','record_frame'])
            assert 0<=c['source_start_frame']<c['source_end_frame']
            assert 0<=c['record_frame']<end(c)<=ep['duration_frames']
            bypath[c['path']].append((c['source_start_frame'],c['source_end_frame']))
            if kind=='video':
                v=vids[c['path']]
                assert v['episode_group_segment'][0]==n and v['has_embedded_audio']
                assert c['source_end_frame']<=int(v['video_streams'][0]['nb_frames'])
                assert c['record_frame']==prev;prev=end(c)
            else:
                r=chosen[c['path']]
                assert r['episode']==n and r['generation_speed_percent_requested']==100 and not r['retime_applied']
                assert c['source_end_frame']<=math.ceil(r['duration_seconds']*24)
                assert sha(c['path'])==r['source_sha256']==r['selected_audio_sha256']==c.get('audio_sha256',c.get('source_sha256'))
                assert c['gain_db']==r['suggested_gain_db']
        if kind=='video':assert prev==ep['duration_frames']
        for path,spans in bypath.items():
            spans.sort();assert all(a[1]<=b[0]for a,b in zip(spans,spans[1:])),('source frame reuse',n,kind,path)
    kinds=[];timingerrs=[]
    for w in events:
        k='narration'if w.get('source_kind',w.get('type'))in ['new_narration','original_new_narration']else 'video'
        kinds.append(k)
        assert 0<=w['start_frame']<=w['end_frame']<=ep['duration_frames']
        assert cover(ep[k],w['source_path'],w['start_frame'],w['end_frame'],1),('uncovered word',n,w)
        if 'source_start_seconds'in w:
            cs=[c for c in ep[k]if c['path']==w['source_path']and w['start_frame']>=c['record_frame']-1 and w['end_frame']<=end(c)+1]
            if cs:
                err=min(max(abs(w['start_frame']-(c['record_frame']+w['source_start_seconds']*24-c['source_start_frame'])),abs(w['end_frame']-(c['record_frame']+w['source_end_seconds']*24-c['source_start_frame'])))for c in cs)
                assert err<=1.000001,('word source clock',n,w,err);timingerrs.append(err)
    role_checks=[]
    for u in [u for u in units if u['episode']==n]:
        if n<12:
            ds=[r for r in ep['role_dialogue']if r['id']==u['id']];assert len(ds)==1
            path=ds[0]['source_path']
        else:
            ds=[r for r in ep['story_blocks']if r.get('dialogue_unit_id')==u['id']];assert len(ds)==1
            wes=[w for w in events if w.get('dialogue_unit_id')==u['id']]
            assert tokens(' '.join(w['word']for w in wes))==tokens(u['original_text']);path=wes[0]['source_path']
        can=next(r for r in u['source_candidates']if r['source_path']==path and r['complete_original_words_observed'])
        lo=can['word_start_seconds']*24;hi=can['word_end_seconds']*24
        spans=sorted((c['source_start_frame'],c['source_end_frame'],c['record_frame']-c['source_start_frame'],c['gain_db'])for c in ep['video']if c['path']==path)
        active=[x for x in spans if x[1]>lo and x[0]<hi];assert active
        assert active[0][0]<=lo+1 and active[-1][1]>=hi-1
        assert len(set(x[2]for x in active))==1
        assert all(a[1]==b[0]for a,b in zip(active,active[1:]))
        assert all(x[3]==0 for x in active)
        role_checks.append({'id':u['id'],'source_path':path,'complete_once':True,'same_source_contiguous_record_mapping':True,'source_gain_db':0})
    cues=parse_srt(ep['subtitle_srt'])
    assert [c['number']for c in cues]==list(range(1,len(cues)+1))
    assert all(c['start_ms']<c['end_ms']for c in cues)
    assert all(a['end_ms']<=b['start_ms']for a,b in zip(cues,cues[1:]))
    assert max(len(c['lines'])for c in cues)<=3
    assert max(len(s)for c in cues for s in c['lines'])<=26
    assert cues[-1]['end_ms']<=ep['duration_frames']/24*1000+1
    assert orig_tokens==tokens(' '.join(' '.join(c['lines'])for c in cues))
    cursor=0;caption_checks=[]
    for c in cues:
        ct=tokens(' '.join(c['lines']));ws=events[cursor:cursor+len(ct)];ks=kinds[cursor:cursor+len(ct)]
        assert len(set(ks))==1,('mixed caption streams',n,c['number'])
        assert ct==[norm(w['word'])for w in ws]
        start=c['start_ms']*24/1000;finish=c['end_ms']*24/1000
        # Existing approved captions intentionally hold3–4frames after last word for legibility.
        assert abs(start-ws[0]['start_frame'])<=1.02
        assert -1.02<=finish-ws[-1]['end_frame']<=5.02
        cursor+=len(ct)
        if cursor<len(events):assert finish<=events[cursor]['start_frame']+1.02,('caption overruns next word',n,c['number'])
        caption_checks.append({'cue':c['number'],'original_tokens':len(ct),'kind':ks[0],'all_words_once_in_order':True,'last_word_readability_handle_frames':round(finish-ws[-1]['end_frame'],3)})
    assert cursor==len(events)
    report.append({'episode':n,'duration_frames':ep['duration_frames'],'duration_seconds':ep['duration_frames']/24,'video_and_identical_sync_segments':len(ep['video']),'narration_segments':len(ep['narration']),'logical_narration_sources':len(set(c['path']for c in ep['narration'])),'original_tokens':len(events),'srt_cues':len(cues),'srt_sha256':sha(ep['subtitle_srt']),'word_events':str(eventpath),'word_events_sha256':sha(eventpath),'original_script_and_srt_word_order_verified':True,'srt_max_lines':max(len(c['lines'])for c in cues),'srt_max_line_chars':max(len(s)for c in cues for s in c['lines']),'srt_overlaps':0,'srt_clock':'24fps relative elapsed from timeline head zero','source_reuse_overlap_count':0,'all_retained_sync_dialogue_source_spans':role_checks,'source_word_clock_max_rounding_error_frames':max(timingerrs,default=0),'narration_paths_hashes_speed_and_gain_match_adopted_manifest':True,'existing_plan_and_srt_not_changed':True,'caption_checks':caption_checks,'remaining_live_review_limits':ep.get('limitations',[])})
assert before=={str(p):sha(p)for p in check_paths},'Frozen inputs changed during read-only validation'
result={'created_at_local':datetime.datetime.now().isoformat(timespec='seconds'),'scope':scope,'status':'READ_ONLY_OFFLINE_VALIDATION_PASSED','final_native_plan':str(P),'final_native_plan_sha256':sha(P),'source_docx_sha256_verified':sha(manifest['source_docx'])==manifest['source_docx_sha256'],'selected_manifest':str(OUT/'五集采用清单.json'),'selected_manifest_sha256':sha(OUT/'五集采用清单.json'),'logical_narration_source_count':sum(r['logical_narration_sources']for r in report),'total_video_and_identical_sync_segments':sum(r['video_and_identical_sync_segments']for r in report),'total_narration_segments':sum(r['narration_segments']for r in report),'total_frames':sum(r['duration_frames']for r in report),'total_srt_cues':sum(r['srt_cues']for r in report),'total_original_tokens':sum(r['original_tokens']for r in report),'episodes':report,'protected_input_hashes':before,'resolve_connected_by_this_validator':False,'native_assembly_verified_by_this_validator':False,'normal_speed_listening_or_full_picture_playback_claimed':False,'notes':['Only the five completed episodes are included. Global44 narration manifest, generation progress and three missing logical segments remain untouched.','Existing SRT readability tail handles preserved; no cue crosses the next original word.','Native assembly and actual playback require parent verification. Subtitle preset only after native SRT insertion.']}
p=OUT/'五集合并只读核验.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k]for k in ['status','logical_narration_source_count','total_video_and_identical_sync_segments','total_narration_segments','total_frames','total_srt_cues','total_original_tokens']},ensure_ascii=False))
