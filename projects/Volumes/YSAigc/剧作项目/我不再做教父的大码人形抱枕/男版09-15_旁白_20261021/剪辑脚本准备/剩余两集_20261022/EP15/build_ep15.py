"""Build male EP15 only after all four actual narration source observations exist.
No Resolve, browser, generation state or existing five-episode outputs are touched.
"""
from pathlib import Path
import sys,json,re,math,hashlib,datetime,itertools
O=Path(__file__).resolve().parent;B=O.parents[2];S=B/'剪辑脚本准备'
sys.path.insert(0,str(S))
from subtitle_tools import write_srt,parse_srt,wrap_original
J=lambda p:json.loads(Path(p).read_text())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
M=J(B/'准备/narration_manifest.json');A=J(S/'剪辑计划_EP12-15_锚点.json');anchor=next(e for e in A['episodes']if e['episode']==15)
I=J(S/'media_inventory_native.json');V={v['filename']:v for e in I['episodes']if e['episode']==15 for v in e['videos']}
raws={i:B/f'ASR/new_narration/raw_large-v3-turbo/EP15/大码男版枕头15-{i:02}-01.json'for i in range(1,5)}
missing=[str(p)for p in raws.values()if not p.exists()]
if missing:
    (O/'等待真实音频与时码.json').write_text(json.dumps({'status':'WAITING_ACTUAL_SOURCE_OBSERVATIONS','missing':missing,'no_final_duration_invented':True,'next_action':'Run build_ep15.py after source ASR/mapping/levels are all available.'},ensure_ascii=False,indent=2)+'\n')
    print('PENDING',missing);raise SystemExit(2)
mapping=J(O.parent/'新旁白实际源词时码_EP12-15_候选待采用.json')
files={int(re.search(r'15-(\d+)-',r['logical_basename'])[1]):r for r in mapping['files']if r['episode']==15}
assert set(files)=={1,2,3,4},'Refresh actual source mapping for all four EP15 files first'
levels={r['source_path']:r for r in J(B/'ASR/new_narration/source_levels.json')['files']}
R={i:J(p)for i,p in raws.items()}
# Secondary's actual observed The=1.58s agrees with the PCM pause;
# primary wrongly glued snapped./The at1.2s. Preserve raw models unchanged.
secondary2_path=B/'ASR/new_narration/secondary_small.en/EP15/大码男版枕头15-02-01.json'
secondary2=J(secondary2_path);assert len(secondary2['words'])==24
for para in files[2]['paragraphs']:
    for wi,w in zip(para['expected_token_indices'],para['canonical_word_events_source_seconds']):
        observed=secondary2['words'][wi]
        w['primary_observed_span_preserved']=[w['start'],w['end']]
        w['start']=observed['start'];w['end']=observed['end']
        w['timing_source_model']='small.en';w['timing_source_json']=str(secondary2_path)
        w['observed_source_tokens']=[observed['word']]
    para['source_first_observed_word_start_seconds']=para['canonical_word_events_source_seconds'][0]['start']
    para['source_last_observed_word_end_seconds']=para['canonical_word_events_source_seconds'][-1]['end']
for i,r in files.items():
    assert r['all_expected_tokens_have_actual_observed_span'] and not r['missing_token_indices']
    assert Path(r['source_path']).is_file() and H(r['source_path'])==r['source_sha256']==R[i]['source_sha256']
    assert r['source_path']in levels
video=[];narration=[];events=[];blocks=[];role=[];pos=0
norm=lambda s:re.sub(r'[^a-z0-9]+','',s.lower())
def add_picture(fn,a,z,tag,gain=-12,dialogue_id=None):
    global pos
    assert 0<=a<z<=int(V[fn]['video_streams'][0]['nb_frames'])
    x=dict(path=V[fn]['path'],source_start_frame=a,source_end_frame=z,record_frame=pos,speed_percent=100,gain_db=gain,tag=tag,same_source_linked_sync_audio=True,contains_protected_original_dialogue=bool(dialogue_id))
    if dialogue_id:x['dialogue_unit_id']=dialogue_id
    video.append(x);pos+=z-a;return x

def vo(seq,a,z,paras,start=None):
    r=files[seq];start=pos if start is None else start
    assert 0<=a<z<=math.ceil(r['decoded_duration_seconds']*24)
    narration.append(dict(path=r['source_path'],source_start_frame=a,source_end_frame=z,record_frame=start,speed_percent=100,gain_db=levels[r['source_path']]['suggested_speech_gain_db'],tag=f'Original prose P{paras}; actual source word spans, 100% speed',logical_basename=r['logical_basename'],source_sha256=r['source_sha256'],original_docx_paragraphs=paras))
    for p in r['paragraphs']:
        if p['docx_paragraph']not in paras:continue
        for wi,w in enumerate(p['canonical_word_events_source_seconds']):
            sf=round(w['start']*24);ef=max(sf+1,round(w['end']*24))
            assert a<=sf<ef<=z,('VO word outside selected source slice',seq,p['docx_paragraph'],w,a,z)
            events.append(dict(word=w['original_word'],start_frame=sf-a+start,end_frame=ef-a+start,source_path=r['source_path'],source_start_seconds=w['start'],source_end_seconds=w['end'],observed_source_word_indices=w.get('observed_source_word_indices',[]),docx_paragraph=p['docx_paragraph'],source_kind='new_narration',type='original_new_narration',boundary_before=wi==0,mapping=w.get('mapping'),timing_source_model=w.get('timing_source_model','large-v3-turbo'),timing_source_json=w.get('timing_source_json',r['source_asr_json'])))
    return z-a

def picture_for_vo(seq,a,z,paras,parts,note):
    start=pos;duration=vo(seq,a,z,paras,start)
    assert sum(y-x for _,x,y in parts)==duration,(paras,duration,parts)
    for fn,x,y in parts:add_picture(fn,x,y,note)
    blocks.append(dict(paragraphs=paras,start_frame=start,end_frame=pos,note=note))

def dialogue(uid,a=None,z=None):
    x=next(x for x in anchor['story_blocks']if x.get('dialogue_unit_id')==uid);c=x['source_ranges'][0]
    a=c['source_start_frame']if a is None else a;z=c['source_end_frame']if z is None else z
    start=pos;fn=Path(c['path']).name;add_picture(fn,a,z,'Complete original synchronous line '+uid,c['gain_db'],uid)
    for wi,w in enumerate(x['observed_word_events']):
        sf=round(w['start']*24);ef=max(sf+1,round(w['end']*24));assert a<=sf<ef<=z,(uid,w,a,z)
        events.append(dict(word=w['original_word'],start_frame=start+sf-a,end_frame=start+ef-a,source_path=c['path'],source_start_seconds=w['start'],source_end_seconds=w['end'],observed_source_word_indices=w.get('observed_source_word_indices',[]),docx_paragraph=x['original_docx_paragraphs'][0],source_kind='sync_dialogue',type='original_sync_dialogue',boundary_before=wi==0,dialogue_unit_id=uid))
    role.append(dict(id=uid,original_text=x['original_text'],source_path=c['path'],source_start_seconds=x['observed_word_events'][0]['start'],source_end_seconds=x['observed_word_events'][-1]['end'],record_start_frame=start+round(x['observed_word_events'][0]['start']*24)-a,record_end_frame=start+round(x['observed_word_events'][-1]['end']*24)-a,docx_paragraph=x['original_docx_paragraphs'][0]))
    blocks.append(dict(paragraphs=x['original_docx_paragraphs'],start_frame=start,end_frame=pos,dialogue_unit_id=uid,original_text=x['original_text'],note='Complete single original delivery; phone consigliere is offscreen; same-source audio follows picture cuts.'))

# Panic -> call. End at the real214f source scene cut, excluding a two-frame flash.
picture_for_vo(1,0,214,[426,427],[('男版15-1-1.mp4',0,214)],'Panic face -> tight hand -> phone -> calling; original source scene chronology')
dialogue('EP15_P0428_Q1')
picture_for_vo(1,214,271,[429],[('男版15-3-2.mp4',0,57)],'Vittoria waits; consigliere is at the other end, not a second visible speaker')
dialogue('EP15_P0430_Q1');dialogue('EP15_P0431_Q1')
picture_for_vo(1,271,353,[432],[('男版15-3-1.mp4',48,130)],'Consigliere hesitates while Vittoria tightens her grip; trim only silent breath handles')
dialogue('EP15_P0433_Q1')
# Preserve full original signed? and Why source handles, then insert a real
# unused same-scene33frame reverse reaction instead of the original26frame gap.
#33f retains snapped's actual terminal/t/release; the next The begins1.58s.
dialogue('EP15_P0434_Q1',0,69)
start=pos;vo(2,0,33,[434],start);add_picture('男版15-3-2.mp4',57,90,'Unused same-scene phone-profile reaction;33f preserves full reporting-phrase release')
blocks.append(dict(paragraphs=[434],start_frame=start,end_frame=pos,note='Original26f silent gap replaced by33f real unique reaction;7f total extension, no retime/freeze or word-tail trimming.'))
dialogue('EP15_P0434_Q2',95,157)
add_picture('男版15-4-1.mp4',157,175,'Original18f breath and listening reaction before offscreen response')
dialogue('EP15_P0435_Q1')
# Apartment -> estate -> walk into garden -> mother trimming; no apartment exit substituted for arrival.
picture_for_vo(2,33,204,[437,438],[('男版15-5-1.mp4',101,157),('男版15-6-1.mp4',0,60),('男版15-5-1.mp4',204,259)],'Estate establishing -> Vittoria enters -> mother continues tending flowers')
dialogue('EP15_P0439_Q1')
picture_for_vo(2,204,260,[440],[('男版15-6-3.mp4',0,56)],'Vittoria maintains unblinking stare before speaking')
dialogue('EP15_P0441_Q1')
picture_for_vo(3,0,134,[442],[('男版15-6-1.mp4',170,241),('男版15-7-1.mp4',0,63)],'Mother lowers hands, dusts and reacts with amused disdain before full reply')
dialogue('EP15_P0443_Q1')
picture_for_vo(3,134,209,[444],[('男版15-8-2.mp4',0,75)],'Vittoria brow tightens before the brief question; real source remains consecutive into line')
dialogue('EP15_P0445_Q1',75,100);dialogue('EP15_P0446_Q1')
# Final source observations decide tail length; no EP15-04 placeholder or invented duration.
z3=min(math.floor(R[3]['decoded_duration_seconds']*24),math.ceil(files[3]['paragraphs'][-1]['source_last_observed_word_end_seconds']*24)+4)
d3=z3-209;assert 1<d3<=187
picture_for_vo(3,209,z3,[447],[('男版15-9-1.mp4',0,d3)],'Mother returns attention to flowers without concern; no daughter walking away added')
z4=min(math.floor(R[4]['decoded_duration_seconds']*24),math.ceil(R[4]['words'][-1]['end']*24)+4)
# Maximize true flower continuation and a brief mother reaction, end on existing garden space.
# Extra frame capacity can come only from a unique silent Vittoria reaction, never repeating15-9walking.
total=z4+12;pool=187-d3
parts=[]
if pool>0:parts.append(('男版15-9-1.mp4',d3,187))
remaining=total-pool-40
assert remaining>=0 and remaining<=64+49,('Tail exceeds reviewed unused still-action pool',total,pool,remaining)
if remaining>64:
    parts.append(('男版15-6-2.mp4',105,169));parts.append(('男版15-8-1.mp4',192,192+remaining-64))
elif remaining>0:parts.append(('男版15-6-2.mp4',169-remaining,169))
parts.append(('男版15-9-1.mp4',273,313))
start=pos;vo(4,0,z4,[448],start)
for fn,a,z in parts:add_picture(fn,a,z,'Indifferent mother and garden ending; omit added walking-away187–273')
blocks.append(dict(paragraphs=[448],start_frame=start,end_frame=pos,note='Original inner narration with12frames final environment; only unique retained source actions; no added departure.'))

# Verify canonical order, complete role quotes, same-source uniqueness, 100% speeds and matching clocks.
events.sort(key=lambda w:(w['start_frame'],w['end_frame']))
source_ep=next(e for e in M['episodes']if e['episode']==15)
expected=' '.join(p['raw_source_text'].replace('"','')for p in source_ep['original_paragraphs_and_retained_narration']).split()
assert [norm(w['word'])for w in events]==[norm(w)for w in expected],('Canonical prose/role order mismatch')
for arr in [video,narration]:
    by={}
    for c in arr:by.setdefault(c['path'],[]).append(c)
    for path,cs in by.items():
        cs.sort(key=lambda c:c['source_start_frame'])
        assert all(x['source_end_frame']<=y['source_start_frame']for x,y in zip(cs,cs[1:])),('Source frames reused',path)
for n in narration:
    ns=n['record_frame'];ne=ns+n['source_end_frame']-n['source_start_frame']
    for d in role:assert max(ns,d['record_start_frame'])>=min(ne,d['record_end_frame']),('VO overlaps role',n,d)
assert len(role)==12 and len({d['id']for d in role})==12
assert not any(Path(v['path']).name=='男版15-9-1.mp4'and max(v['source_start_frame'],187)<min(v['source_end_frame'],273)for v in video)
# Caption phrases preserve each original token and only split at source/speaker boundaries or meaningful clauses.
phrases={435:["Madam Blackwood said she'd handle it","and told me to back off.","I assumed she'd already told you..."],438:['When Vittoria arrived,','Madam Blackwood was trimming her prize flowers, not looking up.'],443:['Your man?','He was just some broke kid from the gutter','who got lucky being your pillow.',"Don't tell me he actually cast a spell on you."],447:["Madam Blackwood wasn't surprised by Vittoria's reaction,",'nor did she care.'],448:["Vittoria's interest never lasted long;",'she figured Vittoria would soon forget and look for new fun.']}
def balanced(words):
    minimum=len(wrap_original(words));assert minimum<=3,(words,minimum)
    if minimum==1:return [' '.join(words)]
    opts=[]
    for bs in itertools.combinations(range(1,len(words)),minimum-1):
        pts=(0,)+bs+(len(words),);ls=[' '.join(words[pts[i]:pts[i+1]])for i in range(minimum)]
        if max(map(len,ls))>26:continue
        target=sum(map(len,ls))/minimum;score=sum((len(x)-target)**2for x in ls)
        if len(words[pts[-2]:])==1:score+=200
        opts.append((score,ls))
    assert opts;return min(opts,key=lambda x:x[0])[1]
groups=[];cursor=0
for p in source_ep['original_paragraphs_and_retained_narration']:
    para=p['docx_paragraph'];ww=p['raw_source_text'].replace('"','').split();ee=events[cursor:cursor+len(ww)];cursor+=len(ww)
    assert [norm(w['word'])for w in ee]==[norm(w)for w in ww]
    if para in phrases:
        assert [norm(w)for ph in phrases[para]for w in ph.split()]==[norm(w)for w in ww]
        k=0
        for ph in phrases[para]:
            ct=len(ph.split());groups.append(ee[k:k+ct]);k+=ct
    else:
        current=[]
        for e in ee:
            if current and e['source_kind']!=current[-1]['source_kind']:groups.append(current);current=[]
            current.append(e)
        if current:groups.append(current)
assert cursor==len(events)
cues=[]
for i,g in enumerate(groups):
    nxt=groups[i+1][0]['start_frame']if i+1<len(groups)else pos
    st=g[0]['start_frame'];en=min(pos,nxt,g[-1]['end_frame']+4)
    assert st<en<=nxt
    lines=balanced([w['word']for w in g]);cues.append(dict(start_frame=st,end_frame=en,text='\n'.join(lines)))
assert [w['word']for w in events]==' '.join(c['text'].replace('\n',' ')for c in cues).split()
srt=O/'EP15.srt';write_srt(srt,cues);assert len(parse_srt(srt))==len(cues)
limitations=['No Resolve connection, normal-speed human listening, or full-motion picture/lip-sync review performed by this plan author.','Exact original spellings preserved for Vitoria/Victoria/Vittoria and Madame/Madam recognition variants; they remain listening limitations.','All timing is observed actual source speech rounded to nearest24fps.15-02 primary snapped./The boundary1.2s is contradicted by actual PCM release; use observed secondary The1.58s and cut33f=1.375s in real pause, preserving snapped terminal release. Raw source models remain unchanged.','Low-confidence non-script hallucinations in ambient sources are not turned into words or subtitles; same-source ambience is retained under narrator.']
ep=dict(episode=15,timeline_name=anchor['timeline_name'],duration_frames=pos,video=video,narration=narration,subtitle_srt=str(srt),story_blocks=blocks,role_dialogue=role,original_word_events=events,limitations=limitations)
plan=dict(status='READY_FOR_NATIVE_ASSEMBLY',project='大码枕头',fps=24,scope=[15],episodes=[ep],offline_verified=True)
(O/'EP15_真实帧剪辑计划.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
(O/'EP15_原文词事件.json').write_text(json.dumps(dict(fps=24,canonical_original_words_verified=True,original_text_source=M['source_docx'],episodes=[dict(episode=15,duration_frames=pos,events=events)]),ensure_ascii=False,indent=2)+'\n')
audit=dict(episode=15,created_at_local=datetime.datetime.now().isoformat(timespec='seconds'),duration_frames=pos,duration_seconds=pos/24,video_and_identical_sync_segments=len(video),narration_segments=len(narration),narration_logical_sources=4,complete_original_role_quotes_once=12,original_tokens=len(events),srt_cues=len(cues),max_lines=max(len(c['text'].splitlines())for c in cues),max_line_characters=max(len(l)for c in cues for l in c['text'].splitlines()),srt_sha256=H(srt),source_speed_percent=100,source_overlap=False,vo_role_overlap=False,source_walking187_273_excluded=True,snapped_gap=dict(original_source='男版15-4-1.mp4',original_gap_range=[69,95],original_gap_frames=26,reaction_insert_source='男版15-3-2.mp4',reaction_insert_range=[57,90],picture_frames=33,narration_frames=33,extra_frames=7,narration_cut_seconds=1.375,observed_secondary_next_The_start_seconds=1.58,previous_word_end=63.84,next_word_start=99.36,pcm_evidence='EP15_VO2_snapped_The_实际波形.jpg'),original_word_order_verified=True,selected_sources=[dict(path=r['source_path'],sha256=r['source_sha256'],speed_percent=100,gain_db=levels[r['source_path']]['suggested_speech_gain_db'],post_asr_differences=r['differences'])for r in files.values()],limitations=limitations,resolve_used=False,normal_speed_audition_claimed=False)
(O/'EP15_离线核验.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');print(json.dumps(audit,ensure_ascii=False,indent=2))
if (O/'等待真实音频与时码.json').exists():(O/'等待真实音频与时码.json').unlink()
