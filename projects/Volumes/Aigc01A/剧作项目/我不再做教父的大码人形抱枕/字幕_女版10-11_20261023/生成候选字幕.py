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
 if ep==11:a['winking']='wincing' # Explicit Root source-spelling decision; QC retains both ASR variants.
 return [a.get(x,x)for x in lex(t)]
def wrap(t,width=28):
 words=t.split();best=None
 for i in range(1,len(words)):
  l=[' '.join(words[:i]),' '.join(words[i:])]
  if max(map(len,l))<=width:
   score=abs(len(l[0])-len(l[1]));best=l if best is None or score<abs(len(best[0])-len(best[1]))else best
 if len(t)<=width:return [t]
 if best:return best
 lines=textwrap.wrap(t,width=width,break_long_words=False,break_on_hyphens=False);assert len(lines)<=3,(t,lines);return lines
def tc(t):
 n=round(t*1000);h,n=divmod(n,3600000);m,n=divmod(n,60000);s,ms=divmod(n,1000);return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
def render(ep,mapping,qc):
 rawp=ROOT/'ASR/raw_large-v3-turbo'/f'EP{ep:02d}_timeline_analysis.json';raw=read(rawp);cp=ROOT/'原文'/f'episode{ep}_canonical.json';can=read(cp)
 def source_text(spec):
  parts=[]
  for pn,kind in spec:
   matches=[s for s in can['segments']if s['source_docx_paragraph']==pn and s['kind']==kind];assert len(matches)==1,(pn,kind);parts.append(matches[0]['text'])
  return ' '.join(parts)
 key=lambda w:(w['word'],w['start'],w['end']);wordidx={key(w):i for i,w in enumerate(raw['words'])};used=[];events=[];cues=[]
 for i,(segids,spec,options)in enumerate(mapping,1):
  ws=[dict(w,primary_word_index=wordidx[key(w)])for sid in segids for w in raw['segments'][sid]['words']];used.extend(w['primary_word_index']for w in ws)
  text=source_text(spec)
  if options.get('actual_extra_to'):text=text.replace('dared mistake','dared to mistake')
  if options.get('override_text')is not None:text=options['override_text']
  if options.get('q1_secondary'):
   sec=read(ROOT/'ASR/secondary_small.en/EP11_Q1_blind.json');where=next(j for j,w in enumerate(sec['words'])if w['word'].strip()=='Where');picked=sec['words'][where:where+6];assert lex(' '.join(w['word']for w in picked))==lex(text)
   head=ws[0]['start'];ws=[dict(w,word=w['word'],start=w['export_start_seconds'],end=w['export_end_seconds'],primary_word_index=None,timing_source='secondary_small.en')for w in picked];ws[0]['start']=head
  exp=[(normalized(m.group(),ep)[0],m.start(),m.end())for m in RX.finditer(text)];obs=[]
  for w in ws:
   for t in normalized(w['word'],ep):obs.append(dict(w,token=t))
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
  end=min(c['speech_end_seconds']+.08,nxt-.001)
  c['end_seconds']=max(c['speech_end_seconds'],end)
  if c['end_seconds']>nxt and i+1<len(cues):c['end_seconds']=nxt
  assert c['end_seconds']>c['start_seconds'],c
  assert len(c['lines'])<=3 and max(map(len,c['lines']))<=28,c
  c['cue_number']=i+1
 out=ROOT/'候选字幕';out.mkdir(exist_ok=True);srt=out/f'EP{ep:02d}_候选_相对0.srt'
 srt.write_text('\n\n'.join(f"{i}\n{tc(c['start_seconds'])} --> {tc(c['end_seconds'])}\n"+'\n'.join(c['lines'])for i,c in enumerate(cues,1))+'\n',encoding='utf-8-sig')
 ignored=sorted(set(range(len(raw['words'])))-set(used));assert len(used)==len(set(used)),'Primarywords duplicated across events'
 qc.update(episode=ep,status='DRAFT_RELATIVE0_ACTUAL_MIX_WITH_ROOT_APPROVED_CORRECTIONS',raw_asr_file=str(rawp),raw_asr_sha256=sha(rawp),actual_source_path=raw['source_path'],actual_source_sha256=raw['source_sha256'],source_clock='relative0seconds from nativeisolatedanalysisexport',export_duration_seconds=raw['decoded_duration_seconds'],canonical_file=str(cp),canonical_sha256=sha(cp),cue_count=len(cues),maximum_lines=max(len(c['lines'])for c in cues),maximum_line_characters=max(len(l)for c in cues for l in c['lines']),first_cue_seconds=cues[0]['start_seconds'],last_cue_end_seconds=cues[-1]['end_seconds'],primary_asr_word_count=len(raw['words']),covered_primary_word_count=len(set(used)),excluded_primary_word_indices=ignored,excluded_primary_words=[raw['words'][j]for j in ignored],all_word_times_and_readability_machine_checked=True,human_listening_performed=False,normal_speed_audio_visual_audition=False,ui_or_Resolve_operation=False,srt_path=str(srt),srt_sha256=sha(srt),no_unheard_script_paragraphs_added=True)
 align=ROOT/'对齐';align.mkdir(exist_ok=True);ap=align/f'EP{ep:02d}_候选词码与原文.json';ap.write_text(json.dumps(dict(status=qc['status'],episode=ep,raw_asr_file=str(rawp),raw_asr_sha256=sha(rawp),canonical_file=str(cp),events=events,cues=cues,qc_file=str(ROOT/'复核'/f'EP{ep:02d}_实际混音与原文差异.json')),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 qdir=ROOT/'复核';qdir.mkdir(exist_ok=True);qp=qdir/f'EP{ep:02d}_实际混音与原文差异.json';qp.write_text(json.dumps(qc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 md=[f'# 女版EP{ep:02d} SRT候选差异','','- 时间为隔离原生混音导出的相对0秒，字幕英文，逐条最多3行/每行最多28字符。','- 只根据实际识别词制作，未读原句不补入；原文名字/标点与Root明确批准的音近词修正单列。','- 未人工核听，不把机器候选冒充成片或音画试听通过。',f'- SRT：`{srt}`；{len(cues)}条；最后cue结束{cues[-1]["end_seconds"]:.3f}秒。','']
 for issue in qc.get('issues',[]):md.append('- '+issue['description'])
 (qdir/f'EP{ep:02d}_实际混音与原文差异.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
 print(json.dumps(dict(episode=ep,srt=str(srt),srt_sha256=sha(srt),cues=len(cues),maxlines=qc['maximum_lines'],maxchars=qc['maximum_line_characters'],last_end=qc['last_cue_end_seconds'],alignment=str(ap),qc=str(qp),unmapped_primary_word_indices=ignored),ensure_ascii=False),flush=True)
 return qc

def ep11():
 N='narration';D='character_dialogue'
 mp=[([0],[(330,N)],{}),([1],[(331,N)],{}),([2],[(332,N)],{'forced_chunks':['On the second night,','Matteo came to my apartment as usual.']}),([3],[(333,N)],{'forced_chunks':['He opened the closet','and immediately noticed two of my pajama tops were missing.']}),([4],[(334,D)],{'q1_secondary':True}),([5],[(335,D)],{}),([6],[(336,N)],{}),([7],[(337,N)],{}),([8],[(338,N)],{}),([9],[(339,N)],{'forced_chunks':['The finger-shaped bruises from that night','still marked the soft skin around my waist.']}),([10],[(340,N)],{}),([11],[(341,D)],{}),([12],[(342,D)],{}),([13],[(348,N)],{'audible_repeat':'firstoccurrence_rootconfirmed','forced_chunks':['He bought ointment downstairs,','gently working it into my bruises with his own hands.']}),([14],[(349,N)],{'audible_repeat':'firstoccurrence_rootconfirmed'}),([15,16],[(347,D)],{'root_approved_wincing_from_win_ing':True}),([17],[(348,N)],{'audible_repeat':'secondoccurrence_rootconfirmed','forced_chunks':['He bought ointment downstairs,','gently working it into my bruises with his own hands.']}),([18],[(349,N)],{'audible_repeat':'secondoccurrence_rootconfirmed'}),([19],[(350,N)],{'actual_extra_to':True,'root_approved_actual_to':True,'forced_chunks':['His belated concern still made my eyes sting,','but I no longer dared to mistake habit for love.']}),([20],[(351,N)],{}),([21],[(352,D),(353,D)],{}),([22],[(354,D)],{}),([23],[(355,N)],{}),([24],[(356,D),(357,D)],{'forced_chunks':['Matteo, I cut my hand packing our camping gear.','I always mess things up…']}),([25],[(359,D),(360,D)],{}),([26],[(361,N)],{}),([27],[(362,N)],{}),([28],[(362,D)],{}),([29],[(363,N)],{}),([30],[(364,D)],{})]
 qc=dict(issues=[dict(type='UNHEARD_SOURCE_PARAGRAPHS',source_paragraphs=[343,344,345,346],description='原文P343–346未在当前混音读出，候选字幕不补入。'),dict(type='AUDIBLE_REPEAT',relative_intervals_seconds=[[40.84,48.32],[52.62,59.68]],source_paragraphs=[348,349],description='P348/349在40.84–48.32和52.62–59.68各出现一次；Root明确两次均加字幕。'),dict(type='SOURCE_SPELLING_PHONETIC_AMBIGUITY_ROOT_APPROVED',relative_intervals_seconds=[[50.34,51.20]],source_paragraphs=[347],asr_both_models='You\'re winking',subtitle_root_approved="You're wincing—",description='两盲模型winking与源wincing音近；Root明确按原文wincing保留整句，疑点保留本报告。'),dict(type='ACTUAL_ADDED_WORD_ROOT_APPROVED',relative_intervals_seconds=[[63.44,63.62]],source_paragraphs=[350],actual_word='to',description='原文dared mistake；实际混音识别为dared to mistake，Root明确加入实际to。'),dict(type='QUESTION_FUSION_RECOGNITION',relative_intervals_seconds=[[16.14,17.30]],source_paragraphs=[334],description='主模型Were，独立small.en明确Where are the two I like；采用原文，句首覆盖主模型更早16.14s。'),dict(type='LIKELY_TAIL_HALLUCINATION_EXCLUDED',relative_intervals_seconds=[[128.0,137.2916875]],primary_interval_seconds=[135.86,137.26],primary_word='You',primary_probability=.119384765625,secondary_text='',description='尾128.0–137.292秒独立small.en空；主模型末You低置信度且无源支持，候选SRT排除。稳定对白最后词96.16s。')])
 return render(11,mp,qc)


def ep10():
 N='narration';D='character_dialogue';M='written_message'
 mp=[([0],[(302,N)],{}),([1],[(303,N)],{}),([2],[(304,D)],{}),([3],[(305,D)],{}),([4,5],[(306,D)],{}),([6],[(307,D)],{}),([7],[(308,N)],{}),([8],[(309,N)],{}),([9],[(310,N)],{}),([10],[(311,D)],{}),([11,12],[(312,N)],{'forced_chunks':['Her tone was cold,',"as if she were afraid I'd use my ten years with Matteo",'as an excuse to cling to the Bellandi family.']}),([13],[(313,N)],{}),([14],[(314,D)],{}),([15],[(315,D)],{'forced_chunks':["I won't cling to him,","and I won't use this job to get anything for myself."]}),([16],[(316,N)],{}),([17],[(317,N)],{'forced_chunks':['After leaving the estate,',"for the first time, I didn't know where to go."]}),([18],[(318,N)],{}),([19],[(319,N)],{'forced_chunks':['My professor once recommended me','for a visiting medical research program in New York.']}),([20],[(320,N)],{}),([21],[(321,N)],{}),([22],[(322,M)],{'written_source_but_actual_mix_spoken':True}),([23],[(323,N)],{}),([24],[(324,M)],{'written_source_but_actual_mix_spoken':True}),([25],[(325,N)],{}),([26],[(326,N)],{}),([27],[(327,N)],{})]
 qc=dict(issues=[dict(type='PROPER_NAME_SPELLING_CORRECTION',source_paragraphs=[306,310,312,318,326],description='Matteo、Bellandi按原文拼写，主模型Mateo/Belandi/Volandia为专名音近转录差异；未增加原文未读句。'),dict(type='WRITTEN_MESSAGES_ACTUALLY_VOICED',relative_intervals_seconds=[[58.68,62.04],[64.22,67.10]],source_paragraphs=[322,324],description='原文是教授短信问答，但当前混音真实读出，按原文两句纳入字幕。'),dict(type='TAIL_NONSOURCE_LOW_CONFIDENCE_EXCLUDED',relative_intervals_seconds=[[93.08,94.50],[120.36,122.52]],raw_words=['Thank you.',"I'm sorry."],description='两尾语均非本集原文，识别词置信约0.10，独立时间线轨道审查确认均不在启用语音片段覆盖内；Root明确不再追加模型测试，候选SRT排除。稳定正文结束78.18s。')])
 return render(10,mp,qc)
if __name__=='__main__':ep11();ep10()
