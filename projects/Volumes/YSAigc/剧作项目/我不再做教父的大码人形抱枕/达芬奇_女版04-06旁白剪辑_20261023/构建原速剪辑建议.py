# -*- coding: utf-8 -*-
"""Read-only selected24 narration analysis. No ASR call or Resolve connection.
Conservative units partition complete original audio; trim ranges are only
machine candidates pending source-context and processed-join audition.
"""
from pathlib import Path
import collections,datetime as dt,hashlib,json,math,os,re,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent.parent;OUT=Path(__file__).resolve().parent
TASK=ROOT/'女版04-06_新旁白_20261023';ASR=TASK/'ASR';FPS=30
sys.path[:0]=[str(ROOT/'达芬奇剪辑_EP21-25_20261020/转录/runtime_compatible'),str(ROOT/'配音制作_前3集/制作资料/音频内容与顺序核验_20261018/ASR/.venv/lib/python3.12/site-packages')]
os.environ['PATH']='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin'+os.pathsep+os.environ.get('PATH','')
os.environ['MPLCONFIGDIR']=str(OUT/'绘图缓存');os.environ['HF_HUB_OFFLINE']='1'
import numpy as np
from mlx_whisper.audio import load_audio,SAMPLE_RATE
from PIL import Image,ImageDraw,ImageFont
FONT=Path('/System/Library/Fonts/Supplemental/Arial.ttf')
def font(n):return ImageFont.truetype(str(FONT),n)if FONT.is_file()else ImageFont.load_default()
def draw_wave(canvas,rect,audio,words,left,right,cuts,title):
 draw=ImageDraw.Draw(canvas);x,y,w,h=rect;draw.rectangle((x,y,x+w,y+h),fill='white');draw.text((x+8,y+4),title,fill='#202020',font=font(17))
 xa=x+52;xb=x+w-15;ya=y+55;yb=y+h-28;mid=(ya+yb)/2;scale=(yb-ya)/2*.88
 def px(t):return xa+(t-left)/(right-left)*(xb-xa)
 vmax=max(float(np.max(np.abs(audio[round(left*SAMPLE_RATE):round(right*SAMPLE_RATE)]))),.02)
 draw.line((xa,mid,xb,mid),fill='#aaaaaa',width=1)
 for j in range(int(xb-xa)):
  sa=round((left+(right-left)*j/(xb-xa))*SAMPLE_RATE);sb=round((left+(right-left)*(j+1)/(xb-xa))*SAMPLE_RATE);v=audio[sa:max(sa+1,sb)]
  if len(v):draw.line((xa+j,mid-float(max(v))/vmax*scale,xa+j,mid-float(min(v))/vmax*scale),fill='#1d4b6a')
 for word in words:
  if word['end']>=left and word['start']<=right:
   xx=px(max(left,word['start']));draw.line((xx,ya,xx,yb),fill='#cfa76a');draw.text((xx,y+29),word['word'].strip(),fill='#835c1a',font=font(11))
 for c in cuts:
  if left<=c<=right:draw.line((px(c),ya,px(c),yb),fill='#b33b2d',width=2)
 for j in range(6):
  t=left+(right-left)*j/5;xx=px(t);draw.text((xx-13,yb+3),f'{t:.2f}',fill='#333333',font=font(12))
assert SAMPLE_RATE==16000
RX=re.compile(r"[a-z]+(?:'[a-z]+)?|\d+",re.I)
ALIASES={'mateo':'matteo',"mateo's":"matteo's",'bolandis':'bellandis','belundi':'bellandi','bolandi':'bellandi','bolondi':'bellandi','18':'eighteen','19':'nineteen','waisted':'wasted','overhoored':'overheard'}
def normal(x):return ALIASES.get(x.lower().replace('’',"'"),x.lower().replace('’',"'"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def float6(x):return round(float(x),6)
def rms_db(a):return float(20*np.log10(max(float(np.sqrt(np.mean(a*a))),1e-9)))if len(a)else -180.0
selection=TASK/'最终采用清单.json';sb=selection.read_bytes();sel=json.loads(sb);assert len(sel['files'])==24
manifest=TASK/'文本核验/manifest.json';mb=manifest.read_bytes();assert sha(manifest)=='a29e094ab15fae9da29e770c4c80586a8d4d8005e04084339503e3e153a32d38'
slotp=OUT/'原文对白占位.json';slots=read(slotp);assert slots['summary']['dialogue_count']==32
canonical_files_sha=hashlib.sha256(json.dumps(sel['files'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
files=[];allunits=[];pauses=[];joinviews=[];audits=[];snapshot={}
for sf in sel['files']:
 source=Path(sf['audio_file']);assert source.is_relative_to(TASK/'交付音频')and sha(source)==sf['sha256'];snapshot[str(source)]=sha(source)
 rp=ASR/'raw_large-v3-turbo/narration'/f"{sf['basename']}.json";raw=read(rp);snapshot[str(rp)]=sha(rp)
 assert raw['source_sha256']==sf['sha256']and raw['canonical_text']==sf['generation_text']
 text=sf['generation_text'];expected=[(normal(m.group()),m.start(),m.end())for m in RX.finditer(text.replace('’',"'"))]
 observed=[]
 for wi,w in enumerate(raw['words']):
  for m in RX.finditer(w['word'].replace('’',"'")):observed.append(dict(token=normal(m.group()),word_index=wi,start=float(w['start']),end=float(w['end']),word=w['word']))
 assert [t[0]for t in expected]==[t['token']for t in observed],sf['basename']
 audio=np.asarray(load_audio(str(source)),dtype=np.float32);duration=len(audio)/SAMPLE_RATE
 assert abs(duration-sf['duration_seconds'])<.001 and len(audio)>0 and np.isfinite(audio).all()
 # Same-clock PCM support, not a phoneme/silence classifier.
 win=80;nb=len(audio)//win;frames=audio[:nb*win].reshape(nb,win)
 energy=np.sqrt(np.mean(frames*frames,axis=1));db=20*np.log10(np.maximum(energy,1e-9));times=(np.arange(nb)+.5)*win/SAMPLE_RATE
 quiet_floor=float(np.percentile(db,10));speech_level=float(np.percentile(db,85))
 def edge(t):
  a=max(0,int((t-.005)*SAMPLE_RATE));b=min(len(audio),int((t+.005)*SAMPLE_RATE));return rms_db(audio[a:b])
 # Blank paragraphs mark removed actor speech; grammar-only sentence edges alone
 # would incorrectly read the following narration continuously over that speech.
 bounds={len(text)}
 for m in re.finditer(r'[.!?](?:["\u201d\u2019])?(?=\s|$)',text):
  if re.search(r'\b(?:Mr|Mrs|Ms|Dr|Sr|Jr|St)\.$',text[:m.end()]):continue
  bounds.add(m.end())
 for m in re.finditer(r'\n\s*\n',text):bounds.add(m.start())
 relevant=[]
 for b in slots['insertion_blocks']:
  if b['insertion_kind']=='within_narration_audio'and b['before_narration']['selected_basename']==sf['basename']:
   relevant.append(b);bounds.add(b['before_narration']['boundary_char_offset_0_based'])
 spans=[];start=0
 for stop in sorted(bounds):
  a=start;b=stop
  while a<b and text[a].isspace():a+=1
  while b>a and text[b-1].isspace():b-=1
  if a<b:spans.append((a,b))
  start=stop
 # Map each canonical word to actual selected-file word clock; aliases only
 # explain prior ASR spellings and do not alter canonical/source/ASR records.
 phrase=[]
 for i,(a,b)in enumerate(spans):
  ix=[k for k,t in enumerate(expected)if t[1]>=a and t[2]<=b];assert ix
  phrase.append(dict(unit_id=f"EP{sf['episode']:02d}-N{sf['sequence']:02d}-S{i+1:02d}",episode=sf['episode'],sequence=sf['sequence'],take=sf['take'],basename=sf['basename'],source_path=str(source),source_sha256=sf['sha256'],canonical_text=text[a:b],text_char_start=a,text_char_end_exclusive=b,source_token_start=ix[0],source_token_end_exclusive=ix[-1]+1,first_word=observed[ix[0]],last_word=observed[ix[-1]],asr_speech_start=observed[ix[0]]['start'],asr_speech_end=observed[ix[-1]]['end'],source_docx_paragraphs=sf['source_docx_paragraphs'],rate=1.0,audition_status='NOT_AUDITIONED',safe_phoneme_edge_status='REQUIRES_SOURCE_SIGNAL_AND_NORMAL_SPEED_AUDITION'))
 assert [k for p in phrase for k in range(p['source_token_start'],p['source_token_end_exclusive'])]==list(range(len(expected)))
 cuts=[]
 for i in range(len(phrase)-1):
  prev=phrase[i];nxt=phrase[i+1];end=prev['asr_speech_end'];beg=nxt['asr_speech_start'];gap=beg-end
  lo=math.ceil(end*FPS);hi=math.floor(beg*FPS);allowed=list(range(lo,hi+1))
  candidates=[(edge(f/FPS),f)for f in allowed]
  midpoint=(end+beg)/2
  if candidates:
   lowest=min(x[0]for x in candidates);near=[x for x in candidates if x[0]<=lowest+3]
   chosen=min(near,key=lambda x:abs(x[1]/FPS-midpoint));cut=chosen[1]/FPS
  else:cut=round(midpoint*FPS)/FPS;lowest=edge(cut)
  cut=max(cuts[-1]+1/FPS if cuts else 0, min(cut,duration));cuts.append(cut)
  block_ids=[b['block_id']for b in relevant if prev['text_char_end_exclusive']<=b['before_narration']['boundary_char_offset_0_based']<nxt['text_char_start']+1]
  # Explicit low-energy core proposal: only inside the ASR inter-word interval.
  # Local adaptive level is evidence, never an automatic speech/no-speech proof.
  mask=(times>=end)&(times<=beg);lidx=np.flatnonzero(mask);quiet_core=None
  local_threshold=quiet_floor+max(3,min(12,(speech_level-quiet_floor)/4))
  if gap>=.35 and len(lidx):
   good=lidx[db[lidx]<=local_threshold];runs=[]
   for k in good:
    if runs and k==runs[-1][-1]+1:runs[-1].append(k)
    else:runs.append([k])
   if runs:
    longest=max(runs,key=len);qa=longest[0]*win/SAMPLE_RATE;qb=(longest[-1]+1)*win/SAMPLE_RATE
    if qb-qa>=.12:quiet_core=dict(start_seconds=float6(qa),end_seconds=float6(qb),duration_seconds=float6(qb-qa),max_rms_dbfs=float6(max(db[longest])),local_threshold_dbfs=float6(local_threshold),classification='LOW_ENERGY_CANDIDATE_NOT_PROVEN_SILENCE')
  thought_sensitive=any(z in (prev['canonical_text']+' '+nxt['canonical_text']).lower()for z in ['my drawer was open','my diary','first time','love you','nightmares','future too','the first time','my love show','foul moods'])
  decision='RESERVE_ORIGINAL_DIALOGUE_INSERTION_NO_VO_OVERLAP'if block_ids else'KEEP_EMOTIONAL_OR_THOUGHT_PAUSE'if thought_sensitive else'KEEP_NATURAL_PUNCTUATION_PAUSE'if not quiet_core else'OPTIONAL_QUIET_CORE_REDUCTION_AFTER_AUDITION_ONLY'
  p=dict(join_id=f"{prev['unit_id']}__{nxt['unit_id']}",episode=sf['episode'],basename=sf['basename'],source_path=str(source),source_sha256=sf['sha256'],outgoing_unit=prev['unit_id'],incoming_unit=nxt['unit_id'],outgoing_final_word=prev['last_word'],incoming_first_word=nxt['first_word'],asr_interword_gap_seconds=float6(gap),conservative_shared_split_seconds=float6(cut),conservative_shared_split_frame30=round(cut*FPS),split_rms_10ms_dbfs=float6(edge(cut)),file_quiet_floor_p10_dbfs=float6(quiet_floor),speech_energy_p85_dbfs=float6(speech_level),candidate_frame_count_between_word_marks=len(allowed),cut_inside_asr_word=not(bool(candidates)),dialogue_block_ids=block_ids,policy=decision,optional_low_energy_core=quiet_core,remove_interval_seconds=None,retained_pause_seconds=float6(max(gap,0)),no_samples_removed_in_conservative_partition=True,signal_only_not_phoneme_proof=True,outgoing_phoneme_complete_audition='PENDING',incoming_phoneme_and_immediacy_audition='PENDING',assembled_processed_join='NOT_CREATED',fade='NOT_APPLIED; if later adjacent editorial seam: centered Cross Fade 0dB two timeline frames after handle/phoneme check; no fade across dialogue gaps')
  pauses.append(p);joinviews.append((sf['basename'],audio,raw['words'],p))
 endpoints=[0]+cuts+[duration]
 for i,p in enumerate(phrase):
  p.update(source_start_seconds=float6(endpoints[i]),source_end_seconds_exclusive=float6(endpoints[i+1]),source_start_frame30_float=float6(endpoints[i]*FPS),source_end_frame30_float=float6(endpoints[i+1]*FPS),source_start_sample16k=round(endpoints[i]*SAMPLE_RATE),source_end_sample16k_exclusive=round(endpoints[i+1]*SAMPLE_RATE),retain_head_or_breath=True,retain_tail_or_word_release=True,all_samples_partitioned_without_trim=True,frame_note='Reference30fps from Root live timeline; fractional file tail must be clamped using actual imported clip length before native edit.')
  assert p['source_start_seconds']<=p['asr_speech_start']+.035 and p['source_end_seconds_exclusive']>=p['asr_speech_end']-.035,(p['unit_id'],p)
 allunits.extend(phrase)
 head=float(raw['words'][0]['start']);tail=duration-float(raw['words'][-1]['end'])
 edge_audit=dict(basename=sf['basename'],episode=sf['episode'],source_path=str(source),source_duration_seconds=duration,leading_to_first_asr_word_seconds=float6(head),last_asr_word_to_file_end_seconds=float6(tail),head_candidate_remove_seconds=None,tail_candidate_remove_seconds=None,policy='Do not blanket-trim: inspect forward head and quiet consonants, preserve outgoing final phoneme/release. These ASR marks are navigation only.',normal_speed_audition='NOT_PERFORMED',processed_or_faded_audio='NOT_CREATED',first_word=raw['words'][0],last_word=raw['words'][-1],source_decode_clock='16kHz mono complete decode; original compressed audio unchanged')
 audits.append(edge_audit)
 # Same-clock selected-file overview; original PCM is only read.
 wp=OUT/'波形词时码'/f"{sf['basename']}_全段.png"
 canvas=Image.new('RGB',(1700,420),'white');draw_wave(canvas,(0,0,1700,420),audio,raw['words'],0,duration,cuts,sf['basename']+' | complete selected source | red=phrase split | orange=ASR word heads');canvas.save(wp)
 files.append(dict(episode=sf['episode'],sequence=sf['sequence'],take=sf['take'],basename=sf['basename'],source_path=str(source),source_sha256=sf['sha256'],raw_asr_file=str(rp),raw_asr_sha256=sha(rp),duration_seconds=duration,generation_text=text,generation_text_sha256=sf['generation_text_sha256'],source_docx_paragraphs=sf['source_docx_paragraphs'],unit_ids=[p['unit_id']for p in phrase],word_count=len(expected),waveform_image=str(wp),head_tail=edge_audit,dialogue_internal_blocks=[b['block_id']for b in relevant],runtime_ASR_invoked=False,source_audio_modified=False))
for page in range(math.ceil(len(joinviews)/6)):
 subset=joinviews[page*6:page*6+6];canvas=Image.new('RGB',(1700,250*len(subset)),'white')
 for row,(name,audio,words,p)in enumerate(subset):
  c=p['conservative_shared_split_seconds'];left=max(0,c-1.1);right=min(len(audio)/SAMPLE_RATE,c+1.1)
  draw_wave(canvas,(0,row*250,1700,250),audio,words,left,right,[c],name+' | '+p['join_id']+' | '+p['policy'])
 path=OUT/'波形词时码'/f'内部接点_第{page+1:02d}页.png';canvas.save(path)
 for _,_,_,p in subset:p['waveform_context_page']=str(path)
for p,h in snapshot.items():assert sha(p)==h
assert manifest.read_bytes()==mb
assert hashlib.sha256(json.dumps(read(selection)['files'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()==canonical_files_sha
out=dict(status='SOURCE_WORD_WAVEFORM_PROPOSAL_ONLY_NO_EDIT_OR_AUDITION',created_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),reference_timeline_fps=FPS,reference_fps_source='Root live Resolve inspection reported30fps; source times are actual chosen-file clock, not record positions.',selection_file=str(selection),selection_snapshot_sha256=hashlib.sha256(sb).hexdigest(),selection_files_canonical_sha256=canonical_files_sha,original_manifest=str(manifest),original_manifest_sha256=sha(manifest),dialogue_slot_file=str(slotp),dialogue_slot_file_sha256=sha(slotp),method=dict(actual_decoded_sample_rate=16000,asr='Reuse existing blind large-v3-turbo word JSON; no inference call',word_alias_mapping_diagnostic=ALIASES,raw_asr_unmodified=True,waveform='Actual same-clock16k mono PCM plus5ms RMS; local quantile levels diagnostic only',boundary_policy='Complete-source conservative partition at lowest-energy available30fps gap frame; does not remove samples. Every edge remains pending phoneme/context audition.',optional_pause_policy='Only identify low-energy core inside marked inter-word gaps; no fixed-threshold ripple, no automatic removals.',speed=1.0,source_audio_mutation=False,resolve_or_ui_operation=False),summary=dict(selected_files=24,total_selected_source_duration_seconds=round(sum(x['duration_seconds']for x in files),3),conservative_units=len(allunits),internal_candidate_joins=len(pauses),internal_word_overlap_candidates=sum(x['cut_inside_asr_word']for x in pauses),optional_low_energy_core_count=sum(x['optional_low_energy_core']is not None for x in pauses),original_dialogue_utterances=32,original_dialogue_blocks=20,internal_dialogue_blocks=13,files_with_internal_dialogue=11,source_canonical_words=sum(x['word_count']for x in files),all_canonical_word_positions_covered_once=True,total_audio_samples_removed=0,audio_speed_changes=0,normal_speed_audition_performed=False,processed_join_or_fade_created=False),files=files,units=allunits,pause_and_join_candidates=pauses,outer_edge_audits=audits,limitations=['This is not a native edit plan or a report of safe phoneme trims.','Word times, low RMS valleys and multirecognizer agreement do not prove clean phoneme edges; every proposed new edit needs source-context and assembled normal-speed audition.','No reference-time or duration invented for synchronous actor dialogue; insert actual dialogue using original sequence and do not layer narration over audible speech.','No retiming, source modifications, narration readout of actor dialogue, picture reorder or target-timeline placement performed.'])
save(OUT/'旁白原速逐句_机器建议.json',out)
md=['# 女版04–06旁白原速逐句剪辑建议','','- 仅源文件时码与机器候选，尚未剪辑；未试听、不声称字尾或接点听感已通过。',f'- 采用24段共{out["summary"]["total_selected_source_duration_seconds"]:.3f}秒；按英文句子及对白插入点分成{len(allunits)}个保守片段。','- 30fps来自主线程实际时间线检查；源秒/16k采样是准确源时钟，record时钟暂空。','- 保守切点保留全部源采样，没有删词/变速。低能量区仅供后续试听后决定，不能静音阈值自动删。','- 32句人物对白（20区块）只作独立占位；11个旁白文件需13次段内让位，不能将对白读入旁白。','','|源文件|实际时长秒|保守句段数|段内对白区块|','|---|---:|---:|---|']
for f in files:md.append(f'|{f["basename"]}|{f["duration_seconds"]:.3f}|{len(f["unit_ids"])}|{", ".join(f["dialogue_internal_blocks"])or"无"}|')
md+=['','逐句源范围（秒，尾点排他；不是已批准最终剪口）：','']
for u in allunits:md.append(f'- {u["unit_id"]}：{u["source_start_seconds"]:.6f}–{u["source_end_seconds_exclusive"]:.6f}；{u["canonical_text"]}')
md+=['','对白占位及每个接点的词、波形、呼吸/停顿政策均在JSON。尚未创建处理链、交叉淡化或实际音轨，正式接点需正常速度核听，不能据机器清单承诺没有截字。','']
(OUT/'旁白原速逐句_机器建议.md').write_text('\n'.join(md),encoding='utf-8')
print(json.dumps(dict(status=out['status'],summary=out['summary'],json_path=str(OUT/'旁白原速逐句_机器建议.json'),sha256=sha(OUT/'旁白原速逐句_机器建议.json'),waveform_context_pages=math.ceil(len(joinviews)/6)),ensure_ascii=False),flush=True)
