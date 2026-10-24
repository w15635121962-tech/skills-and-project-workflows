from pathlib import Path
import json,re,difflib
OUT=Path(__file__).parent
raw=json.loads((OUT/'narration_raw.json').read_text())
keep=lambda x: bool(re.match(r'[\u3400-\u9fffA-Za-z0-9]',x))
rawchars=[]
for si,s in enumerate(raw['segments']):
 for wi,w in enumerate(s['words']):
  cs=[c for c in w['word'] if keep(c)]
  for j,c in enumerate(cs):
   a=w['start']+(w['end']-w['start'])*j/max(1,len(cs));b=w['start']+(w['end']-w['start'])*(j+1)/max(1,len(cs))
   rawchars.append({'c':c,'start':a,'end':b,'p':w['p'],'raw_word':w['word'],'raw_segment':si})
chapters=[];refchars=[];sentence_specs=[];phrase_specs=[]
for ln in (OUT/'narration_reference.txt').read_text().splitlines():
 if not ln.strip():continue
 if ln.startswith('# '):
  chapters.append({'id':len(chapters)+1,'name':ln[2:],'offset':len(refchars)});continue
 start=len(refchars)
 for c in ln:
  if keep(c):refchars.append(c)
 # sentences split on strong punctuation; commas remain inside
 cursor=start
 for p in re.findall(r'[^。；！!]+[。；！!]?|[。；！!]',ln):
  length=sum(keep(c) for c in p)
  if length:
   sentence_specs.append({'chapter_id':len(chapters),'text':p,'a':cursor,'b':cursor+length});cursor+=length
 cursor=start
 for p in re.findall(r'[^，。、；！!]+[，。、；！!]?|[，。、；！!]',ln):
  length=sum(keep(c) for c in p)
  if length:
   phrase_specs.append({'chapter_id':len(chapters),'text':p,'a':cursor,'b':cursor+length});cursor+=length
A=''.join(x['c'] for x in rawchars);B=''.join(refchars)
sm=difflib.SequenceMatcher(None,A,B,autojunk=False)
aligned=[None]*len(B);audit=[]
for tag,a,b,c,d in sm.get_opcodes():
 if tag=='equal':
  for j,i in enumerate(range(c,d)):
   x=rawchars[a+j];aligned[i]={'start':x['start'],'end':x['end'],'word':B[i],'p':x['p'],'alignment':'asr_match','raw_word':x['raw_word']}
 else:
  audit.append({'kind':tag,'asr':A[a:b],'reference':B[c:d],'raw_start':rawchars[min(a,len(rawchars)-1)]['start'],'raw_end':rawchars[max(a,b-1)]['end']})
  if c==d:continue
  if a<b:
   left=rawchars[a]['start'];right=rawchars[b-1]['end'];prob=min(x['p'] for x in rawchars[a:b])
  else:
   left=rawchars[a-1]['end'] if a else rawchars[0]['start'];right=rawchars[a]['start'] if a<len(rawchars) else rawchars[-1]['end'];prob=None
  right=max(left,right)
  for j,i in enumerate(range(c,d)):
   aligned[i]={'start':left+(right-left)*j/(d-c),'end':left+(right-left)*(j+1)/(d-c),'word':B[i],'p':prob,'alignment':'source_assisted_interpolation','asr_span':A[a:b]}
assert all(x is not None for x in aligned)
for x in aligned:
 x['start']=round(x['start'],3);x['end']=round(x['end'],3)
def build(specs):
 result=[]
 for sp in specs:
  ws=aligned[sp['a']:sp['b']]
  result.append({'id':len(result)+1,'chapter_id':sp['chapter_id'],'start':ws[0]['start'],'end':ws[-1]['end'],'text':sp['text'],'words':ws})
 return result
sentences=build(sentence_specs);phrases=build(phrase_specs)
for i,ch in enumerate(chapters):
 end=chapters[i+1]['offset'] if i+1<len(chapters) else len(B)
 ch['start']=aligned[ch['offset']]['start'];ch['end']=aligned[end-1]['end'];ch['sentence_ids']=[s['id'] for s in sentences if s['chapter_id']==ch['id']];ch.pop('offset')
notes=[
 {'type':'recording_order','time':[0.37,26.69],'detail':'录音开篇顺序为“这里”→“深耕这方沃土/汇启新章/集团名”→“青春筑梦”。策划第15页汇总稿将“青春筑梦”列在“深耕”之前；已按录音顺序定位。'},
 {'type':'script_variant','time':[26.69,36.93],'detail':'录音识别为“看少年意气风发”“琅琅书声中，看青春最美底色”，与第18页分镜文案一致；第23页汇总版措辞不同。'},
 {'type':'script_variant','time':[100.23,105.65],'detail':'录音为“从学段独立到九年贯通，文汇中学教育集团”，与第25页版本一致；第29页汇总稿为“学段割裂”“文汇教育集团”。'},
 {'type':'script_variant','time':[424.89,433.53],'detail':'录音为“满怀激情，激活智慧，不断创新，创造文汇更美好的未来”，与第42页一致；第43页汇总稿的“热忱/创新不断/蒸蒸日上”未出现在本次识别中。'},
 {'type':'source_corrected_uncertainty','time':[9.37,11.5],'detail':'ASR为“生根这方沃土”，依据策划纠正为“深耕这方沃土”；未作人工听写核验。'},
 {'type':'orthography_uncertainty','time':[338.93,341],'detail':'“同科异构”为策划第37/38页原文，ASR为同音“同科意购”；该术语应由校方审字，未擅改为其他教育术语。'},
 {'type':'method','detail':'全文由实际录音ASR定位，按策划校正学校名/同音错字。标点为阅读添加。词时间为模型估计；纠错字时间由邻近ASR字插值，不是逐音素人工强制对齐。未改动音频。'}
]
data={'source':raw['source'],'duration':raw['duration'],'script_source':'/Volumes/YSAigc/2026-2027/文汇中学/文汇中学集团宣传策划.pdf','method':'faster-whisper small word timestamps + source-assisted character alignment','review_status':'source_assisted_asr_not_human_listening_verified','chapters':chapters,'sentences':sentences,'phrases':phrases,'notes':notes,'alignment_corrections':audit}
(OUT/'narration_aligned.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
def tc(x):return f'{int(x)//60:02d}:{x%60:06.3f}'
lines=['旁白逐句时间表（录音优先；策划辅助校字；词时间为自动估计）','音频总长 '+tc(raw['duration']),'']
for ch in chapters:
 lines.append(f"[{tc(ch['start'])} - {tc(ch['end'])}] {ch['name']}")
 for s in sentences:
  if s['chapter_id']==ch['id']:lines.append(f"{s['id']:03d}  {tc(s['start'])} - {tc(s['end'])}  {s['text']}")
 lines.append('')
lines.append('差异和不确定项：')
for n in notes:lines.append('- '+n['detail'])
(OUT/'narration_aligned.txt').write_text('\n'.join(lines))
print('\n'.join(lines))
print('CHAR_MATCH_RATIO',sm.ratio(),'SENTENCES',len(sentences),'PHRASES',len(phrases),'CORRECTION_SPANS',len(audit))
print('LONG_ALIGNMENT_EDITS',json.dumps([a for a in audit if max(len(a['asr']),len(a['reference']))>7],ensure_ascii=False))
