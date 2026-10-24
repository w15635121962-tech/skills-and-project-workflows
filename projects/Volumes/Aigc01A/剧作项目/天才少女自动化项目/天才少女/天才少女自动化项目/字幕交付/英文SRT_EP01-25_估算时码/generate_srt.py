# -*- coding: utf-8 -*-
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as E
import re, json, hashlib, textwrap, csv
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
SOURCE=ROOT/'完整剧本/被嘲笑我方无人，天才少女摘下耳机镇全场EN.docx'
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
original_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
with ZipFile(SOURCE) as z:
 root=E.fromstring(z.read('word/document.xml'))
paras=[''.join(t.text or '' for t in p.findall('.//w:t',ns)).strip() for p in root.findall('.//w:body/w:p',ns)]
episodes={}; excluded=[]; ep=None
for idx,p in enumerate(paras):
 if re.fullmatch(r'\d{1,2}',p):
  ep=int(p); assert ep not in episodes; episodes[ep]=[]; continue
 if ep is None or not p: continue
 if re.fullmatch(r'【.*】',p,flags=re.S):
  excluded.append({'paragraph':idx,'episode':ep,'text':p});continue
 assert not re.search(r'[\u4e00-\u9fff]',p),(idx,p)
 episodes[ep].append((idx,p))
assert list(episodes)==list(range(1,26))

def tc(ms):
 h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
 return f'{h:02}:{m:02}:{s:02},{ms:03}'

def wrap(words):
 lines=textwrap.wrap(' '.join(words),width=42,break_long_words=False,break_on_hyphens=False)
 return lines

def chunks(p):
 # Keep every source token and punctuation mark. Wrap only at existing spaces.
 words=p.split();start=0
 while start<len(words):
  limit=start
  while limit<len(words) and len(wrap(words[start:limit+1]))<=2 and limit-start<14:
   limit+=1
  assert limit>start
  # Prefer sentence/phrase boundary, without ending on a very short fragment.
  candidates=[j for j in range(start+3,limit+1) if re.search(r'[.!?;:,—][”\'\"’]*$',words[j-1]) and not re.fullmatch(r'(?:Mr|Mrs|Ms|Dr|Prof|St)\.',words[j-1])]
  end=candidates[-1] if candidates else limit
  yield words[start:end]
  start=end

def build(e):
 cues=[];now=0
 for para,p in episodes[e]:
  for words in chunks(p):
   duration=max(1200,round(len(words)/2.5*1000))
   text='\n'.join(wrap(words))
   cues.append({'index':len(cues)+1,'episode':e,'paragraph':para,'start_ms':now,'end_ms':now+duration,'text':text,'word_count':len(words)})
   now+=duration+80
 return cues,now-80

def write_srt(path,cues):
 path.write_text('\n\n'.join(f'{i}\n{tc(c["start_ms"])} --> {tc(c["end_ms"])}\n{c["text"]}' for i,c in enumerate(cues,1))+'\n',encoding='utf-8-sig')

def verify(path,expected):
 raw=path.read_text(encoding='utf-8-sig');blocks=raw.strip().split('\n\n');assert len(blocks)==len(expected)
 recovered=[];last=-1
 for i,(block,c) in enumerate(zip(blocks,expected),1):
  lines=block.splitlines();assert lines[0]==str(i)
  assert re.fullmatch(r'\d{2,}:\d{2}:\d{2},\d{3} --> \d{2,}:\d{2}:\d{2},\d{3}',lines[1])
  assert lines[1]==f'{tc(c["start_ms"])} --> {tc(c["end_ms"])}'
  assert c['start_ms']>=last and c['end_ms']>c['start_ms'];last=c['end_ms']
  assert len(lines[2:])<=2 and max(map(len,lines[2:]))<=42
  recovered.extend(' '.join(lines[2:]).split())
 assert recovered==' '.join(c['text'] for c in expected).split()
 return recovered

merged=[];offset=0;summary=[];mapping=[]
for e in episodes:
 cues,duration=build(e)
 filename=f'天才少女_EP{e:02d}_EN_估算时码.srt'
 write_srt(OUT/filename,cues)
 tokens=verify(OUT/filename,cues)
 source_tokens=' '.join(p for _,p in episodes[e]).split()
 assert tokens==source_tokens
 start_index=len(merged)+1
 for c in cues:
  full=dict(c,start_ms=c['start_ms']+offset,end_ms=c['end_ms']+offset,index=len(merged)+1)
  merged.append(full)
  mapping.append({'episode':e,'episode_cue':c['index'],'merged_cue':full['index'],'source_paragraph':c['paragraph'],'episode_start':tc(c['start_ms']),'episode_end':tc(c['end_ms']),'merged_start':tc(full['start_ms']),'merged_end':tc(full['end_ms']),'text':c['text'].replace('\n',' ')})
 summary.append({'episode':e,'file':filename,'cues':len(cues),'words':len(tokens),'estimated_duration':tc(duration),'merged_start':tc(offset),'merged_end':tc(offset+duration),'merged_first_cue':start_index,'merged_last_cue':len(merged)})
 offset+=duration+1000
write_srt(OUT/'天才少女_EP01-25_EN_全集合并_估算时码.srt',merged)
full_tokens=verify(OUT/'天才少女_EP01-25_EN_全集合并_估算时码.srt',merged)
assert full_tokens==' '.join(p for e in episodes for _,p in episodes[e]).split()
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==original_hash
with (OUT/'逐集与全集字幕映射.csv').open('w',encoding='utf-8-sig',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(mapping[0]));writer.writeheader();writer.writerows(mapping)
qa={'source':str(SOURCE),'source_sha256':original_hash,'source_unmodified':True,'episodes':25,'cues':len(merged),'words':len(full_tokens),'max_lines':max(len(c['text'].splitlines()) for c in merged),'max_line_characters':max(len(l) for c in merged for l in c['text'].splitlines()),'verbatim_source_token_sequence':True,'srt_readback_validation':True,'encoding':'UTF-8 BOM','timing':'ESTIMATED. 2.5 whitespace-separated words/sec, minimum 1.2 sec/cue, 80 ms cue gaps, 1 sec gaps between episodes in merged version. NOT audio-aligned or final-edit-synced.','estimated_total':tc(merged[-1]['end_ms']),'excluded_stage_directions':excluded,'episode_summary':summary}
(OUT/'校验统计.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'制作说明.txt').write_text('天才少女第1—25集英文 SRT 文稿版\n\n来源：完整剧本/被嘲笑我方无人，天才少女摘下耳机镇全场EN.docx。\n保留英文旁白、对白及英文叙述顺序与标点；排除文档开头人员信息、数字章节标题、中文画面备注与卡点说明。未修改源稿，不以分镜生成提示词代替剧本。\n\n时码是估算，不是音频或成片对齐。项目内音频为分段旁白，缺少第8、9集，且没有全剧完整对白与最终剪辑时间轴；不得把分段旁白累计时长当作完整剧集时码。字幕按2.5词/秒、最短1.2秒、条间80毫秒计算。逐集文件从00:00:00,000开始；合并版按集顺序接续，集间留1秒。\n\n每条最多两行，每行最多42字符，优先在已有句末或分句标点处分条。英文词与标点不改写，仅调整空白与换行。UTF-8 BOM。\n\n交付：25个逐集SRT、1个全集合并SRT、映射CSV、校验JSON与本说明。请逐集导入对应剪辑，按照实际英文配音及最终成片校准时间码；新增无对白补镜的时长尚未作为成片时间轴加入本稿。\n',encoding='utf-8-sig')
archive=OUT.parent/'天才少女_EP01-25_英文SRT_估算时码.zip'
with ZipFile(archive,'w',ZIP_DEFLATED) as z:
 for p in sorted(OUT.iterdir()):
  if p.is_file():z.write(p,arcname=OUT.name+'/'+p.name)
with ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({k:qa[k] for k in ['episodes','cues','words','max_lines','max_line_characters','estimated_total','verbatim_source_token_sequence','srt_readback_validation']},ensure_ascii=False,indent=2))
print(archive)
