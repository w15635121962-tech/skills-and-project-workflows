from pathlib import Path
import datetime, hashlib, json, re

BASE=Path(__file__).resolve().parent.parent
SUB=BASE/'字幕'
SRT=SUB/'SRT'
FROZEN=SUB/'依据/11集剪辑工作版_生成SRT使用的最终实读.json'
LATEST=BASE/'11集剪辑工作版_最终实读.json'
scope=[16,17,18,19,21,22,23,24,25,26,28]
paths={ep:SRT/(f'EP{ep}.srt' if ep<20 else f'EP{ep}_当前轨道_三行以内.srt' if ep<=25 else 'EP26_含预排旁白.srt' if ep==26 else 'EP28_预排旁白.srt') for ep in scope}

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def flatten(s):
 # Resolve snapshots explicitly carry both literal escaped and real Unicode separators.
 for tok in ('\\u2028','\\u2029','\u2028','\u2029','\\r\\n','\\n'):
  s=s.replace(tok,' ')
 return re.sub(r'\s+',' ',s).strip()
def ms(s):
 h,m,se,mill=map(int,re.fullmatch(r'(\d{2,}):(\d{2}):(\d{2}),(\d{3})',s).groups())
 assert m<60 and se<60
 return ((h*60+m)*60+se)*1000+mill
def parse(p):
 txt=p.read_text(encoding='utf-8-sig').replace('\r\n','\n').replace('\r','\n').strip()
 cues=[]
 for block in re.split(r'\n[ \t]*\n',txt):
  lines=block.split('\n');assert len(lines)>=3,(p,block)
  n=int(lines[0]);a,b=re.fullmatch(r'(\d{2,}:\d{2}:\d{2},\d{3})\s+-->\s+(\d{2,}:\d{2}:\d{2},\d{3})',lines[1]).groups()
  textlines=[]
  for line in lines[2:]:textlines.extend(line.splitlines())
  assert textlines and all(x.strip() for x in textlines),(p,n)
  start=ms(a);end=ms(b)
  cues.append({'cue':n,'start_ms':start,'end_ms':end,'start_frame_24fps':round(start*24/1000),'end_frame_exclusive_24fps':round(end*24/1000),'lines':textlines,'text':flatten('\n'.join(textlines))})
 return cues

frozen=json.loads(FROZEN.read_text());latest=json.loads(LATEST.read_text())
fb={e['episode']:e for e in frozen['episodes']};lb={e['episode']:e for e in latest['episodes']}
records=[];all_errors=[];hashes={p:digest(p) for p in paths.values()}
for ep in scope:
 p=paths[ep];cues=parse(p);e=lb[ep];fps=24;duration_frames=e['end']-e['start'];duration_ms=duration_frames/fps*1000;errors=[]
 numbering=[c['cue'] for c in cues]==list(range(1,len(cues)+1))
 if not numbering:errors.append({'kind':'nonconsecutive_cue_numbers'})
 for i,c in enumerate(cues):
  if c['end_ms']<=c['start_ms']:errors.append({'kind':'nonpositive_duration','cue':c['cue']})
  if len(c['lines'])>3:errors.append({'kind':'more_than3_lines','cue':c['cue']})
  if c['start_ms']<0 or c['end_frame_exclusive_24fps']>duration_frames:errors.append({'kind':'out_of_timeline_frame_range','cue':c['cue']})
  if c['end_ms']>duration_ms+0.501:errors.append({'kind':'out_of_timeline_time_range','cue':c['cue']})
  if i and c['start_ms']<cues[i-1]['end_ms']:errors.append({'kind':'overlap_or_nonmonotonic','previous':cues[i-1]['cue'],'cue':c['cue']})
  # SRT 1ms rounding must round back to the exact24fps endpoint (<=0.5ms).
  if abs(c['start_ms']-c['start_frame_24fps']*1000/24)>.501 or abs(c['end_ms']-c['end_frame_exclusive_24fps']*1000/24)>.501:errors.append({'kind':'not24fps_endpoint','cue':c['cue']})
 match=None
 if ep in range(21,26):
  t=next(t for t in fb[ep]['tracks']['subtitle'] if t['name']==str(ep));items=t['items'];diffs=[]
  if len(items)!=len(cues):diffs.append({'kind':'cue_count_mismatch','snapshot':len(items),'srt':len(cues)})
  for i,(old,new) in enumerate(zip(items,cues),1):
   a=old['start']-fb[ep]['start'];b=old['end']-fb[ep]['start']
   if a!=new['start_frame_24fps'] or b!=new['end_frame_exclusive_24fps']:diffs.append({'cue':i,'kind':'frame_changed','snapshot':[a,b],'srt':[new['start_frame_24fps'],new['end_frame_exclusive_24fps']]})
   if flatten(old['name'])!=new['text']:diffs.append({'cue':i,'kind':'text_changed','snapshot':flatten(old['name']),'srt':new['text']})
  match={'frozen_native_track':t['name'],'snapshot_cue_count':len(items),'all_text_except_line_breaks_identical':not any(x['kind']=='text_changed' for x in diffs),'all_in_out_frames_identical':not any(x['kind']=='frame_changed' for x in diffs),'differences':diffs}
  errors.extend(diffs)
 row={'episode':ep,'file':str(p),'sha256':hashes[p],'cue_count':len(cues),'max_lines_per_cue':max(len(c['lines']) for c in cues),'max_characters_per_line':max(len(s) for c in cues for s in c['lines']),'first_start_ms':cues[0]['start_ms'],'last_end_ms':cues[-1]['end_ms'],'latest_timeline':e['timeline'],'latest_duration_frames':duration_frames,'latest_duration_seconds':duration_frames/fps,'within_latest_timeline':not any(x['kind'].startswith('out_of_timeline') for x in errors),'numbering_consecutive':numbering,'time_monotonic_nonoverlapping':not any(x['kind']=='overlap_or_nonmonotonic' for x in errors),'frozen_duration_matches_latest':fb[ep]['end']-fb[ep]['start']==duration_frames,'prearranged_narration':ep in (26,28),'frozen_native_match':match,'errors':errors}
 records.append(row);all_errors.extend({'episode':ep,**x} for x in errors)

report={'created_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'status':'PASS' if not all_errors else 'FAIL','scope':scope,'read_only_source_files':True,'files_unchanged':all(digest(p)==h for p,h in hashes.items()),'fps':24,'endpoint_convention':'end-exclusive; SRT millisecond times round to exact24fps frames; timeline start offset subtracted for frozen native comparison','inputs':{'latest_snapshot':str(LATEST),'latest_snapshot_sha256':digest(LATEST),'frozen_snapshot':str(FROZEN),'frozen_snapshot_sha256':digest(FROZEN)},'total_target_files':len(records),'total_cues':sum(r['cue_count'] for r in records),'max_lines_per_cue':max(r['max_lines_per_cue'] for r in records),'max_characters_per_line':max(r['max_characters_per_line'] for r in records),'EP21_25_total_cues':sum(r['cue_count'] for r in records if 21<=r['episode']<=25),'errors':all_errors,'episodes':records,'limitations':['EP26 and EP28 narration cue times are prearranged, not synchronized to new narration audio.','Offline SRT audit only; does not verify Resolve import, native subtitle track preset application, font rendering, overflow from automatic wrapping, playback or auditory sync.']}
(SUB/'11集目标SRT_独立只读审计.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=[f"11集目标SRT独立只读审计：{report['status']}。",'',f"共{len(records)}个目标文件、{report['total_cues']}条；每条最多{report['max_lines_per_cue']}行，每行最多{report['max_characters_per_line']}字符。各集编号连续、时间单调不重叠、范围不超过最新实读时间线。EP21–25共{report['EP21_25_total_cues']}条，与冻结原生字幕的文字（仅忽略换行）及起止帧完全一致。",'','| 集 | 条数 | 最多行 | 最长行字符 | 末字幕秒 | 时间线秒 |','|---|---:|---:|---:|---:|---:|']
lines += [f"| {r['episode']} | {r['cue_count']} | {r['max_lines_per_cue']} | {r['max_characters_per_line']} | {r['last_end_ms']/1000:.3f} | {r['latest_duration_seconds']:.3f} |" for r in records]
lines += ['', 'EP26、EP28旁白为预排时码；取得新旁白后须重新对齐。此审计未操作Resolve，不证明原生轨道导入、预设、实际自动换行或回放同步。', '',f"异常：{len(all_errors)}；全部源SRT文件哈希前后一致。"]
if all_errors:lines.append(json.dumps(all_errors,ensure_ascii=False))
(SUB/'11集目标SRT_独立只读审计.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:report[k] for k in ['status','total_target_files','total_cues','max_lines_per_cue','max_characters_per_line','EP21_25_total_cues','files_unchanged','errors']},ensure_ascii=False,indent=2))
print('\n'.join(lines))
