# -*- coding: utf-8 -*-
from pathlib import Path
import json,re,itertools,zipfile,xml.etree.ElementTree as ET,hashlib,datetime
root=Path.cwd();base=root/'自动剪辑_女版16-19_21-26_28_20261020';out=base/'字幕/SRT';out.mkdir(parents=True,exist_ok=True)
source=root/'完整剧本/我不再做教父的大码人形抱枕EN.docx';ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};tag='{'+ns['w']+'}';tree=ET.fromstring(zipfile.ZipFile(source).read('word/document.xml'));episodes={};current=None
for ix,p in enumerate(tree.findall('.//w:body/w:p',ns),1):
 text=''.join((x.text or '') if x.tag==tag+'t' else '\n' if x.tag in [tag+'br',tag+'cr'] else '\t' if x.tag==tag+'tab' else '' for x in p.iter()).strip();m=re.fullmatch(r'Episode\s+(\d+)',text,re.I)
 if m:current=int(m[1]);episodes[current]=[];continue
 if current in (25,26) and text:episodes[current].append({'docx_paragraph':ix,'text':text})
actual=json.loads((base/'11集剪辑工作版_最终实读.json').read_text());real={e['episode']:e for e in actual['episodes']};r2=json.loads((base/'准备/EP26_EP28/剪辑候选_EP26_EP28_r2.json').read_text())
# Slot numbers below follow complete source paragraph order including the single omitted Chinese stage direction inEN26.
slots26={1:(0,88),2:(88,202),3:(202,286),4:(286,387),5:(390,446),6:(505,545),7:(545,595),8:(595,665),9:(665,800),10:(800,866),11:(866,980),12:(980,1147),13:None,14:(1220,1297),15:(1304,1332),16:(1395,1456),17:(1456,1535),18:(1535,1593),19:(1593,1660),20:(1660,1718),21:(1718,1762),22:(1762,1854),23:(1854,1992),24:(1992,2030),25:(2030,2075),26:(2075,2180),27:(2180,2283)}
slots28={1:(0,72),2:(72,150),3:(150,176),4:(176,212),5:(212,267),6:(267,337),7:(337,381),8:(381,410),9:(410,532),10:(532,568),11:(568,626),13:(626,742),14:(742,867),15:(867,1002),16:(1002,1064),17:(1064,1125),18:(1125,1180),19:(1180,1264),20:(1264,1344),21:(1344,1517),22:(1517,1563),23:(1563,1634),24:(1634,1852)}
splits={
 (26,2):["I didn't rush into a new relationship","or try to prove I'd completely forgotten Matteo."],
 (26,12):["When Evan finally told me how he felt,","I didn't say yes just because I was afraid of missing my chance."],
 (26,26):["The real transformation wasn't becoming","the kind of woman Matteo was willing to be seen with."],
 (28,9):["But whenever the lights went out,","he still instinctively reached for the empty space beside him."],
 (28,14):["He had mistaken dependence for power,","treating my love like a contract that would never expire."],
 (28,15):["One morning in New York, I walked out of my apartment","carrying flowers I had bought for myself."],
 (28,24):["It was the ten years I'd loved him","without holding anything back."]}

def norm(s):return ' '.join(s.split())
def layout(text):
 w=text.split();n=len(w)
 for count in range(1,4):
  options=[]
  for cut in itertools.combinations(range(1,n),count-1):
   stops=[0,*cut,n];ls=[' '.join(w[stops[i]:stops[i+1]]) for i in range(count)];lens=list(map(len,ls))
   if max(lens)>28:continue
   cost=sum((v-sum(lens)/count)**2 for v in lens)
   cost+=sum(7 for l in ls[:-1] if l.split()[-1].lower().strip('.,?!;:\"') in {'a','an','the','to','of','in','and','or','for','with','my','his','her','your','was','were','is','are','had','have','has'})
   cost-=sum(6 for l in ls[:-1] if l.endswith((',', '.', '?','!',';',':')))
   options.append((cost,ls))
  if options:return min(options,key=lambda x:x[0])[1]
 raise ValueError(('Cannot fit3x28',text))
def tc(frame):
 ms=round(frame/24*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def pieces_for(ep,n,text):
 pieces=splits.get((ep,n),[text]);assert norm(' '.join(pieces))==norm(text);return pieces

def add_piece(result,ep,n,source_record,text,a,z,kind,slotrole):
 ps=pieces_for(ep,n,text);weights=[len(x) for x in ps];weight=sum(weights);cursor=a
 for j,(p,cw) in enumerate(zip(ps,weights),1):
  w=len(re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?",p))
  end=z if j==len(ps) else a+round((z-a)*sum(weights[:j])/weight);ls=layout(p);assert norm('\n'.join(ls))==norm(p);assert end>cursor
  overlaps=[]
  for v in real[ep]['tracks']['video'][0]['items']:
   lo=max(cursor,v['start']);hi=min(end,v['end'])
   if hi>lo:overlaps.append({'source_path':v['source_path'],'timeline_overlap_frames':[lo,hi],'source_overlap_seconds':[v['source_start']+(lo-v['start'])/24,v['source_start']+(hi-v['start'])/24]})
  result.append({'source_unit':n,'docx_paragraph':source_record['docx_paragraph'],'source_paragraph_text':source_record['text'],'part':j,'text':p,'lines':ls,'kind':kind,'timeline_start_frame':cursor,'timeline_end_frame_exclusive':end,'time':tc(cursor)+' --> '+tc(end),'characters':len(p),'words':w,'words_per_second':w/((end-cursor)/24),'reading_cps':len(p)/((end-cursor)/24),'timing_status':'source_ASR_word_mapped_outward24fps' if kind=='synchronized_dialogue' else 'prearranged_to_current_picture_pending_new_VO','narrative_picture_role':slotrole,'actual_picture_sources':overlaps})
  cursor=end

reports=[]
for ep,en in [(26,25),(28,26)]:
 records=episodes[en];slots=slots26 if ep==26 else slots28;result=[];omitted=[]
 for n,record in enumerate(records,1):
  text=record['text']
  if re.search(r'[\u3400-\u9fff]',text):omitted.append(record);continue
  if ep==26 and n==13:
   # Preserve report and exact quoted dialogue while keeping the existing true speech timing.
   lead,spoken=text.split('"',1);spoken='"'+spoken;assert lead.strip()=='I told him,'
   add_piece(result,ep,n,record,lead.strip(),1147,1172,'prearranged_narration','女主提出慢一点前的原叙述提示，接同期对白')
   add_piece(result,ep,n,record,spoken,1175,1212,'synchronized_dialogue','女主现有同期声：I need to take things slowly.')
   continue
  a,z=slots[n];kind='synchronized_dialogue' if ep==26 and n in (5,15) else 'prearranged_narration'
  roles={26:{1:'回到纽约研究所',2:'不急于新感情或证明忘记男主',3:'不向人表演新生活',4:'导师递正式聘用合同',5:'导师同期原句',6:'签字',7:'没有Bellandi信托',8:'没有陪睡条件',9:'与Evan逗猫',10:'一起晚餐',11:'无需证明值得被喜欢',12:'Evan告白与不急答应',14:'Evan微笑反应',15:'Evan接受慢一点同期原句',16:'隔壁售出换邻居',17:'不再每日换花',18:'不再隔墙听动静',19:'安稳独睡',20:'未拆道歉信',21:'退回未拆信的决定',22:'不必原谅的认识',23:'一年后进入花店看自己',24:'健康体型与镜中自己',25:'笑容放开',26:'真正转变不是满足男主选择',27:'不再依靠男人证明价值'},28:{1:'独睡治疗进展开场',2:'从十分钟开始',3:'睡眠逐步延长',4:'终于独睡整夜',5:'员工离开及关门',6:'收起酒药',7:'不再跟踪',8:'不再电话',9:'摸空床',10:'身旁体温已无',11:'旧书与无人轻读',13:'独坐顿悟失眠之外',14:'承认依赖被当作权力',15:'晨光抱自购花出门',16:'Evan街角挥手',17:'朋友催促',18:'女主笑着跑去',19:'十年人形抱枕回顾',20:'男主以为无法独睡',21:'女主真正走出噩梦',22:'男主终于明白',23:'床头愿望券与男主',24:'十年之爱过期，与朋友走向自己的生活'}}
  add_piece(result,ep,n,record,text,a,z,kind,roles[ep][n])
 result.sort(key=lambda r:r['timeline_start_frame']);blocks=[]
 for i,r in enumerate(result,1):
  r['cue']=i;blocks.append(f"{i}\n{r['time']}\n"+'\n'.join(r['lines']))
  assert r['timeline_start_frame']>=0 and r['timeline_end_frame_exclusive']<=real[ep]['end'];assert len(r['lines'])<=3 and max(map(len,r['lines']))<=28
  if i>1:assert result[i-2]['timeline_end_frame_exclusive']<=r['timeline_start_frame'],('overlap',ep,i)
 source_text='\n'.join(r['text'] for r in records if not re.search(r'[\u3400-\u9fff]',r['text']))
 assert norm(' '.join(r['text'] for r in result))==norm(source_text),('source mismatch',ep)
 target=out/('EP26_含预排旁白.srt' if ep==26 else 'EP28_预排旁白.srt');target.write_text('\n\n'.join(blocks)+'\n',encoding='utf-8-sig')
 reports.append({'episode_local_chinese':ep,'english_source_episode':en,'timeline_name':real[ep]['timeline'],'timeline_id':real[ep]['id'],'timeline_duration_frames':real[ep]['end'],'timeline_duration_seconds':real[ep]['end']/24,'output':str(target),'cue_count':len(result),'narration_cues':sum(r['kind']=='prearranged_narration' for r in result),'synchronized_dialogue_cues':sum(r['kind']=='synchronized_dialogue' for r in result),'maximum_lines':max(len(r['lines']) for r in result),'maximum_row_characters':max(len(l) for r in result for l in r['lines']),'source_english_whitespace_normalized_exact_match':True,'original_quotation_delimiters_retained':True,'omitted_unspoken_chinese_visual_direction':omitted,'all_cues_inside_actual_timeline':True,'no_cue_overlap':True,'narration_does_not_overlap_synchronized_dialogue':True,'reading_speed_over22cps':[{'cue':r['cue'],'time':r['time'],'text':r['text'],'cps':r['reading_cps']} for r in result if r['reading_cps']>22],'cues':result})
report={'created_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'status':'Complete originalEnglish SRT prepared, not imported. Narration timing is prearranged to picture, not audio-aligned.','source_docx':str(source),'source_docx_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'actual_timeline_snapshot':str(base/'11集剪辑工作版_最终实读.json'),'actual_timeline_snapshot_sha256':hashlib.sha256((base/'11集剪辑工作版_最终实读.json').read_bytes()).hexdigest(),'source_mapping':{'26':'EnglishEpisode25','28':'EnglishEpisode26'},'wording_policy':'All original English words, punctuation, capitalization and quotation marks retained in source order. Only whitespace/line breaks and cue splitting changed. Chinese visual directions and chapter headers excluded.','timing_policy':'Known EP26 three synchronized dialogue ranges preserved from word-ASR mapping; narrative slots prearranged by visible story sequence and current actual clip ranges. All24fps endpoints exclusive. Must recalibrate narration cue timing after new VO exists, potentially adjusting picture length/reading speed.','episodes':reports,'limitations':['New narration audio does not exist for these episodes in this workflow; no narration sync or speech-speed claim.','Source actual3 dialogue timing derives from blind ASR words and saved timeline mapping, not subjective listening acceptance.','Visual/source alignment is a planned semantic association, not final rendered acceptance.','Explicit3-line/28-character checks still require preset appearance verification in Resolve.','No Resolve/browser/UI changes, no generation, no upload performed.']}
q=base/'字幕/EP26_EP28_原文旁白预排明细映射.json';q.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(q)
for e in reports:print(e['episode_local_chinese'],e['cue_count'],e['narration_cues'],e['synchronized_dialogue_cues'],e['maximum_lines'],e['maximum_row_characters'],'cps>22',e['reading_speed_over22cps'])
