# -*- coding: utf-8 -*-
"""Post-blind recognition only. Relative0 SRT; no Resolve operations."""
from pathlib import Path
import collections,hashlib,json,math,re,textwrap
ROOT=Path(__file__).resolve().parent
RX=re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?|\d+")
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lex(t):return [x.group().lower().replace('’',"'")for x in RX.finditer(t)]
def normalized(t,ep):
 a={'mateo':'matteo',"mateo's":"matteo's",'belandi':'bellandi','volandia':'bellandi'}
 a.update({'18':'eighteen','19':'nineteen','10':'ten','balandas':'bellandis','bolandis':'bellandis','bellidi':'bellandi','bolandi':'bellandi','belundi':'bellandi','bellarini':'bellandi','waisted':'wasted','mep':'mph'})
 return [v for x in lex(t) for v in (['a','hundred','and','sixty'] if x=='160' else [a.get(x,x)])]
def wrap(t,width=28):
 words=t.split()
 if len(t)<=width:return [t]
 candidates=[]
 for i in range(1,len(words)):
  lines=[' '.join(words[:i]),' '.join(words[i:])]
  if max(map(len,lines))<=width:candidates.append((sum((len(l)-len(t)/2)**2 for l in lines),lines))
 if candidates:return min(candidates,key=lambda x:x[0])[1]
 for i in range(1,len(words)-1):
  for j in range(i+1,len(words)):
   lines=[' '.join(words[:i]),' '.join(words[i:j]),' '.join(words[j:])]
   if max(map(len,lines))<=width:
    score=sum((len(l)-len(t)/3)**2 for l in lines)+sum(50 for l in lines if len(l.split())==1)
    candidates.append((score,lines))
 assert candidates, (t,'cannot fit3lines')
 return min(candidates,key=lambda x:x[0])[1]
def tc(t):
 n=round(t*1000);h,n=divmod(n,3600000);m,n=divmod(n,60000);s,ms=divmod(n,1000);return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
def render(ep,mapping,qc):
 rawp=ROOT/'ASR/raw_large-v3-turbo'/f'EP{ep:02d}_timeline_analysis.json';raw=read(rawp);cp=ROOT/'准备'/f'episode{ep}_canonical.json';can=read(cp)
 def source_text(spec):
  parts=[]
  for pn,kind in spec:
   matches=[s for s in can['segments']if s['source_docx_paragraph']==pn and s['kind']==kind];assert len(matches)==1,(pn,kind);parts.append(matches[0]['text'])
  return ' '.join(parts)
 key=lambda w:(w['word'],w['start'],w['end']);wordidx={key(w):i for i,w in enumerate(raw['words'])};used=[];events=[];cues=[]
 for i,(segids,spec,options)in enumerate(mapping,1):
  ws=[dict(w,primary_word_index=wordidx[key(w)])for sid in segids for w in raw['segments'][sid]['words']]
  if options.get('word_select') is not None: ws=ws[options['word_select'][0]:options['word_select'][1]]
  if options.get('window_prefix') is not None:
   win=read(ROOT/'ASR/blind_windows/EP05_APPENDED_HEAD.json');lo,hi=options['window_prefix'];extra=[dict(w,start=w['export_start_seconds'],end=w['export_end_seconds'],primary_word_index=None,timing_source='blind_window_APPENDED_HEAD') for w in win['words'][lo:hi]];ws=extra+ws
  used.extend(w['primary_word_index'] for w in ws if w['primary_word_index'] is not None)
  text=source_text(spec)
  if options.get('actual_extra_to'):text=text.replace('dared mistake','dared to mistake')
  if options.get('override_text')is not None:text=options['override_text']
  if options.get('q1_secondary'):
   sec=read(ROOT/'ASR/secondary_small.en/EP11_Q1_blind.json');where=next(j for j,w in enumerate(sec['words'])if w['word'].strip()=='Where');picked=sec['words'][where:where+6];assert lex(' '.join(w['word']for w in picked))==lex(text)
   head=ws[0]['start'];ws=[dict(w,word=w['word'],start=w['export_start_seconds'],end=w['export_end_seconds'],primary_word_index=None,timing_source='secondary_small.en')for w in picked];ws[0]['start']=head
  exp=[(normalized(m.group(),ep)[0],m.start(),m.end())for m in RX.finditer(text)];obs=[]
  for w in ws:
   for t in normalized(w['word'],ep):
    t=options.get('phonetic_aliases',{}).get(t,t);obs.append(dict(w,token=t))
  assert [e[0]for e in exp]==[o['token']for o in obs],(ep,i,text,[e[0]for e in exp],[o['token']for o in obs])
  timed=[]
  for m in re.finditer(r'\S+',text):
   ids=[j for j,e in enumerate(exp)if e[1]>=m.start()and e[2]<=m.end()];assert ids
   timed.append(dict(text=m.group(),start=min(obs[j]['start']for j in ids),end=max(obs[j]['end']for j in ids)))
  event=dict(event_id=f'EP{ep:02d}-E{i:02d}',primary_segment_ids=segids,source_paragraph_kinds=spec,canonical_or_approved_actual_text=text,options=options,source_word_times=timed,start_seconds=timed[0]['start'],end_seconds=timed[-1]['end']);events.append(event)
  # Prefer complete thought groups. Explicit Root phrase fixes take priority.
  forced=options.get('forced_chunks')
  if forced:
   assert ' '.join(forced)==' '.join(text.split()),(text,forced)
   groups=[];cursor=0
   for chunk in forced:
    count=len(chunk.split());part=timed[cursor:cursor+count];assert ' '.join(w['text']for w in part)==chunk;groups.append(part);cursor+=count
   assert cursor==len(timed)
  else:
   try:wrap(text);groups=[timed]
   except AssertionError:
    groups=[];part=[]
    for w in timed:
     candidate=' '.join(x['text']for x in part+[w])
     if part and len(candidate)>70:groups.append(part);part=[]
     part.append(w)
    if part:groups.append(part)
  for group in groups:
   cue_text=' '.join(w['text']for w in group);lines=wrap(cue_text)
   cues.append(dict(event_id=event['event_id'],source_paragraph_kinds=spec,text=cue_text,lines=lines,start_seconds=group[0]['start'],speech_end_seconds=group[-1]['end'],end_seconds=group[-1]['end'],word_times=list(group)))
 for i,c in enumerate(cues):
  nxt=cues[i+1]['start_seconds']if i+1<len(cues)else raw['decoded_duration_seconds']
  end=min(max(c['speech_end_seconds']+.08,c['start_seconds']+.65),nxt-.001)
  c['end_seconds']=max(c['speech_end_seconds'],end)
  if c['end_seconds']>nxt and i+1<len(cues):c['end_seconds']=nxt
  assert c['end_seconds']>c['start_seconds'],c
  assert len(c['lines'])<=3 and max(map(len,c['lines']))<=28,c
  c['cue_number']=i+1
 out=ROOT/'候选字幕';out.mkdir(exist_ok=True);srt=out/f'EP{ep:02d}_候选_相对0.srt'
 srt.write_text('\n\n'.join(f"{i}\n{tc(c['start_seconds'])} --> {tc(c['end_seconds'])}\n"+'\n'.join(c['lines'])for i,c in enumerate(cues,1))+'\n',encoding='utf-8-sig')
 ignored=sorted(set(range(len(raw['words'])))-set(used));assert len(used)==len(set(used)),'Primarywords duplicated across events'
 qc.update(episode=ep,status='FRONT_PROGRAM_ONLY_RELATIVE0_READY_FOR_INDEPENDENT_QC',raw_asr_file=str(rawp),raw_asr_sha256=sha(rawp),actual_source_path=raw['source_path'],actual_source_sha256=raw['source_sha256'],source_clock='relative0seconds from nativeisolatedanalysisexport',export_duration_seconds=raw['decoded_duration_seconds'],canonical_file=str(cp),canonical_sha256=sha(cp),cue_count=len(cues),maximum_lines=max(len(c['lines'])for c in cues),maximum_line_characters=max(len(l)for c in cues for l in c['lines']),first_cue_seconds=cues[0]['start_seconds'],last_cue_end_seconds=cues[-1]['end_seconds'],primary_asr_word_count=len(raw['words']),covered_primary_word_count=len(set(used)),excluded_primary_word_indices=ignored,excluded_primary_words=[raw['words'][j]for j in ignored],all_word_times_and_readability_machine_checked=True,human_listening_performed=False,normal_speed_audio_visual_audition=False,ui_or_Resolve_operation=False,srt_path=str(srt),srt_sha256=sha(srt),no_unheard_script_paragraphs_added=True)
 qc['latest_user_scope']='Front original picture program only; appended newVO tests explicitly excluded.'
 qc['append_new_vo_start_seconds']={4:97.4666667,5:139.8333333}[ep]
 qc['front_program_audio_word_indices']=list(range({4:267,5:316}[ep]))
 qc['intentional_front_hallucination_excluded_indices']=[] if ep==4 else [314,315]
 qc['front_valid_primary_word_coverage_missing']=sorted(set(qc['front_program_audio_word_indices'])-set(used)-set(qc['intentional_front_hallucination_excluded_indices']))
 qc['appended_test_primary_word_indices']=list(range({4:267,5:316}[ep],len(raw['words'])))
 assert not qc['front_valid_primary_word_coverage_missing']
 assert cues[-1]['end_seconds']<qc['append_new_vo_start_seconds']
 align=ROOT/'对齐';align.mkdir(exist_ok=True);ap=align/f'EP{ep:02d}_候选词码与原文.json';ap.write_text(json.dumps(dict(status=qc['status'],episode=ep,raw_asr_file=str(rawp),raw_asr_sha256=sha(rawp),canonical_file=str(cp),events=events,cues=cues,qc_file=str(ROOT/'复核'/f'EP{ep:02d}_实际混音与原文差异.json')),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 qdir=ROOT/'复核';qdir.mkdir(exist_ok=True);qp=qdir/f'EP{ep:02d}_实际混音与原文差异.json';qp.write_text(json.dumps(qc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 md=[f'# 女版EP{ep:02d} SRT候选差异','','- 时间为隔离原生混音导出的相对0秒，字幕英文，逐条最多3行/每行最多28字符。','- 只根据实际识别词制作，未读原句不补入；原文名字/标点与Root明确批准的音近词修正单列。','- 未人工核听，不把机器候选冒充成片或音画试听通过。',f'- SRT：`{srt}`；{len(cues)}条；最后cue结束{cues[-1]["end_seconds"]:.3f}秒。','']
 for issue in qc.get('issues',[]):md.append('- '+issue['description'])
 (qdir/f'EP{ep:02d}_实际混音与原文差异.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
 print(json.dumps(dict(episode=ep,srt=str(srt),srt_sha256=sha(srt),cues=len(cues),maxlines=qc['maximum_lines'],maxchars=qc['maximum_line_characters'],last_end=qc['last_cue_end_seconds'],alignment=str(ap),qc=str(qp),unmapped_primary_word_indices=ignored),ensure_ascii=False),flush=True)
 return qc

N='narration';D='character_dialogue'
def ep4():
 mp=[([0],[(113,N)],{}),([1,2],[(114,N)],{'forced_chunks':['The Bellandis covered my college tuition;','my job was putting their heir to sleep.']}),([3],[(116,N)],{}),([4],[(117,N)],{}),([5],[(118,D)],{}),([6],[(119,N)],{}),([7],[(120,N)],{'forced_chunks':['The difference was, they showed him a good time','while I killed the mood.']}),([8,9],[(121,N),(122,N)],{'forced_chunks':['Annoyed by my presence, he once tried sending me away,','forcing himself to sleep alone.']}),([10,11],[(123,N)],{'forced_chunks':['But every time, within two hours,','his bodyguards would bring me back to the estate.']}),([12],[(124,N)],{'forced_chunks':['For ten years, I humored every mood','just to give him peace before the nightmares.']}),([13],[(125,N)],{}),([14],[(126,D)],{}),([15],[(127,D)],{}),([16],[(128,N),(129,N)],{'forced_chunks':['Sensing something, his mother, Serafina Bellandi,','repeatedly warned me against getting unrealistic ideas.']}),([17],[(130,N)],{}),([18],[(131,D)],{}),([19],[(132,N)],{'forced_chunks':['At nineteen, Matteo chased off the loan sharks',"collecting my mother’s old debt."]}),([20,21],[(133,N)],{'forced_chunks':['That night, unable to hold back my feelings any longer,','I wrote his name in my diary for the first time.']}),([22],[(134,N)],{'forced_chunks':['But when I woke up the next morning,','Matteo was sitting silently at my desk.']}),([23,24],[(135,N),(136,N),(137,N)],{'forced_chunks':['My drawer was open.','The combination lock was on the floor.','My diary lay open in his hands.','Matteo slowly ran his thumb over the page covered in writing.']}),([25],[(138,N)],{}),([26],[(139,N)],{'forced_chunks':['I stood there,','feeling stripped naked and tossed under a spotlight.']})]
 qc=dict(issues=[dict(type='LATEST_USER_SCOPE_FRONT_PROGRAM_ONLY',description='只给前面的正片加字幕；97.4667秒起追加的新旁白测试段全部不纳入SRT，完整盲ASR仅留证据缓存。',excluded_interval_seconds=[97.4666667,192.3666875]),dict(type='PROPER_NAMES_NUMERALS_SOURCE_NORMALIZED',description='Balandas/Bolandis→Bellandis；Bellidi/Bolandi/Belundi→Bellandi；Mateo→Matteo；18/19/10→eighteen/nineteen/ten。只改字幕表记，不改音频。'),dict(type='DIARY_WRITTEN_WORDS_VOICED',source_paragraphs=[138],description='日记中的Matteo、I love you由正片叙述真实读出，保留在旁白字幕，不当现场人物对白。')])
 return render(4,mp,qc)
def ep5():
 mp=[([0],[(142,D)],{'override_text':'How did you open it?','actual_omitted_source_stutter':True}),([1],[(143,D)],{}),([2],[(144,N)],{}),([3],[(145,D)],{}),([4],[(146,D)],{}),([5],[(147,N)],{'phonetic_aliases':{'and':'on'},'forced_chunks':['I lowered my head,','waiting for his verdict on my pathetic little crush.']}),([6],[(148,N)],{}),([7],[(149,N)],{}),([8],[(151,D)],{}),([9,10],[(152,D)],{'forced_chunks':['That sleeping beside me for ten years','would somehow make you Mrs. Bellandi?']}),([11],[(153,N)],{}),([12],[(154,D)],{}),([13],[(155,N)],{}),([14],[(156,D)],{}),([15,16],[(157,D)],{'forced_chunks':['Your fat helps me sleep.','But it will never get you anywhere beyond my bed.']}),([17],[(158,N)],{}),([18],[(159,D)],{}),([19],[(160,N)],{}),([20],[(161,N)],{'phonetic_aliases':{'the':'that'}}),([21],[(162,N)],{'forced_chunks':['On the fourth night, his second-in-command, Vincent,','dragged a stumbling, wasted Matteo to my door.']}),([22],[(163,D),(164,D),(165,D)],{'forced_chunks':["Boss hasn't slept in three nights.",'He was doing a hundred and sixty mph at the underground track.','He would only come here.']}),([23],[(166,N),(167,N)],{'forced_chunks':['Taking care of him when he was drunk or feverish','was part of my job.','But he could really hold his liquor.']}),([24],[(168,N),(169,N)],{'forced_chunks':['I had never seen him this drunk before.','His knuckles were scraped,','his expensive coat covered in track dust.']}),([25],[(170,N)],{'forced_chunks':['While I cleaned his wounds,','he refused to let go of my hand.']}),([26],[(171,N)],{'forced_chunks':['I helped Matteo into the kitchen','to prepare honey-lemon tea.']}),([27],[(172,N)],{}),([28,29],[(173,N)],{'phonetic_aliases':{'trilling':'trailing'},'forced_chunks':['Matteo trapped me against the counter,','trailing kisses from behind my ear down to my neck.']}),([30],[(174,D)],{'phonetic_aliases':{'lisa':'ellie'}}),([31],[(175,N)],{}),([32],[(176,N),(177,N)],{}),([33],[(181,N)],{}),([34],[(180,D)],{'actual_repeat':'first occurrence before Feeling awful'}),([35],[(179,D)],{}),([36],[(180,D)],{'actual_repeat':'second occurrence after Feeling awful'})]
 qc=dict(issues=[dict(type='LATEST_USER_SCOPE_FRONT_PROGRAM_ONLY',description='只给前面的正片加字幕；139.8333秒起追加的新旁白测试段全部不纳入SRT，完整盲ASR与补窗仅留缓存证据。',excluded_interval_seconds=[139.8333333,222.9]),dict(type='SOURCE_STUTTER_NOT_ACTUALLY_READ',source_paragraphs=[142],actual_text='How did you open it?',source_text='How... how did you open it?',relative_intervals_seconds=[[0,1]],description='源文双How，正片首句只识别到一次How；字幕按实际单How，不补未读重复词。'),dict(type='ROOT_APPROVED_PHONETIC_SOURCE_NORMALIZATION',source_paragraphs=[147,161,173,174],raw_observed=['and','the','trilling','Lisa'],subtitle_source_spellings=['on','that','trailing','Ellie'],relative_intervals_seconds=[[14.90,15.14],[52,52.16],[92.88,93.14],[95.58,95.82]],description='Root明确准许on/that/trailing/Ellie按源文校音近转录，原始差异在此保留；未改源音频。'),dict(type='PROPER_NAMES_NUMERALS_SOURCE_NORMALIZED',description='Mateo→Matteo；Bellarini→Bellandi；waisted→wasted同音表记；10→ten；160 MEP→a hundred and sixty mph，与原文对应。'),dict(type='ACTUAL_DIALOGUE_REPEAT_AND_SEQUENCE',source_paragraphs=[179,180,181],relative_intervals_seconds=[[101.18,103.04],[104.80,106.50],[108.98,109.86],[113.14,114.88]],description='当前正片顺序是His answer...、It’s almost ready...、Feeling awful?、再一次It’s almost ready...；两次原对白均字幕，未按原文顺序擅自重排声音。'),dict(type='ZERO_DURATION_LOW_CONFIDENCE_HALLUCINATION_EXCLUDED',primary_segment_ids=[37],relative_intervals_seconds=[[114.88,114.92]],raw_words=["I'm",'not.'],description='主识别末I’m起止同为114.88，not只0.04s；103–118.067无提示补窗仅复现真实前面3句，不复现I’m not，无源支持，字幕排除。',secondary_evidence_file=str(ROOT/'ASR/blind_windows/EP05_ACTOR_TAIL.json'))])
 return render(5,mp,qc)
if __name__=='__main__':ep4();ep5()
