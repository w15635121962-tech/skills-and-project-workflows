import pathlib,json,re,hashlib,datetime
S=pathlib.Path(__file__).resolve().parents[1];backup=S/'备份/20261021_185912_26字预设换行前';changes=[];errors=[]
def parse(p):
 txt=p.read_text(encoding='utf-8-sig');out=[]
 for b in re.split(r'\r?\n\s*\r?\n',txt.strip()):
  ls=b.splitlines();assert len(ls)>=3,(p,b);out.append({'number':int(ls[0]),'number_raw':ls[0],'time_raw':ls[1],'lines':ls[2:]})
 return out
flat=lambda ls:re.sub(r'\s+',' ',' '.join(ls)).strip()
def wrap_line(line,limit=26):
 # Independent greedy word wrapping for one already explicit line, retaining existing hard breaks.
 ws=line.split();lines=[];cur=''
 for word in ws:
  if not cur:cur=word
  elif len(cur)+1+len(word)<=limit:cur+=' '+word
  else:lines.append(cur);cur=word
  while len(cur)>limit:
   lines.append(cur[:limit]);cur=cur[limit:]
 if cur:lines.append(cur)
 return lines
files=[]
for ep in [24,25]:
 oldp=backup/f'EP{ep}.srt';newp=S/f'修正导入/EP{ep}_三行.srt';old=parse(oldp);new=parse(newp)
 if len(old)!=len(new):errors.append({'episode':ep,'type':'cue_count_changed'})
 for a,b in zip(old,new):
  if a['number_raw']!=b['number_raw']:errors.append({'episode':ep,'cue':a['number'],'type':'number_changed'})
  if a['time_raw']!=b['time_raw']:errors.append({'episode':ep,'cue':a['number'],'type':'timecode_changed','old':a['time_raw'],'new':b['time_raw']})
  if flat(a['lines'])!=flat(b['lines']):errors.append({'episode':ep,'cue':a['number'],'type':'body_words_punctuation_changed','old':flat(a['lines']),'new':flat(b['lines'])})
  if a['lines']!=b['lines']:
   changes.append({'episode':ep,'cue':a['number'],'old_lines':a['lines'],'new_lines':b['lines'],'timecode_unchanged':a['time_raw']==b['time_raw'],'text_without_linebreaks_unchanged':flat(a['lines'])==flat(b['lines']),'timecode':b['time_raw'],'old_rendered_lines_at26':[y for x in a['lines'] for y in wrap_line(x)],'new_rendered_lines_at26':[y for x in b['lines'] for y in wrap_line(x)]})
 files.append({'episode':ep,'backup':str(oldp),'corrected':str(newp),'backup_sha256':hashlib.sha256(oldp.read_bytes()).hexdigest(),'corrected_sha256':hashlib.sha256(newp.read_bytes()).hexdigest(),'cue_count':len(new),'main_srt_matches_corrected':(S/f'EP{ep}.srt').read_bytes()==newp.read_bytes()})
actual_set={(x['episode'],x['cue']) for x in changes};expected_set={(24,5),(24,14),(24,30),(25,4),(25,16),(25,20)}
if actual_set!=expected_set:errors.append({'type':'changed_cues_not_exact_expected6','actual':sorted(actual_set),'expected':sorted(expected_set)})
all5=[]
for ep in range(21,26):
 p=S/f'EP{ep}.srt' if ep<=23 else S/f'修正导入/EP{ep}_三行.srt';rows=parse(p);rendered=[{'cue':c['number'],'hard_lines':len(c['lines']),'rendered_lines_at26':sum(len(wrap_line(x)) for x in c['lines']),'original_lines':c['lines'],'rendered_lines':[y for x in c['lines'] for y in wrap_line(x)]} for c in rows];bad=[x for x in rendered if x['rendered_lines_at26']>3]
 if bad:errors.append({'episode':ep,'type':'more_than3_rendered_lines_at26','cues':bad})
 all5.append({'episode':ep,'path':str(p),'cue_count':len(rows),'max_hard_lines':max(x['hard_lines'] for x in rendered),'max_rendered_lines_at26':max(x['rendered_lines_at26'] for x in rendered),'more_than3_count':len(bad),'three_line_cues':[x['cue'] for x in rendered if x['rendered_lines_at26']==3],'all_cues':rendered})
if sum(x['cue_count'] for x in all5)!=197:errors.append({'type':'total_cues_not197'})
report={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'task':'Independent read-only check of exactly six hard-line-break changes against185912 backup and197cue26-character automatic wrap model','independent':True,'srt_files_modified':False,'native_ui_or_resolve_operated':False,'file_comparisons':files,'changed_cue_count':len(changes),'changes':changes,'all5_episodes':all5,'text_timecodes_numbers_counts_unchanged':not any(e['type'] in ['cue_count_changed','number_changed','timecode_changed','body_words_punctuation_changed'] for e in errors),'exactly_expected_six_linebreak_changes':actual_set==expected_set,'total_cues':sum(x['cue_count'] for x in all5),'all197_rendered_model_le3_lines_at26':not any(x['more_than3_count'] for x in all5),'wrap_model':'Greedy English word wrapping at26 Unicode characters per line, preserving each existing explicit newline independently; long words split only if>26characters. This is static worst-case hard-break + width counting, not a new native screenshot or playback check.','errors':errors,'pass':not errors}
(S/'核验报告/六条换行独立复核.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['all5_episodes','changes','file_comparisons']},ensure_ascii=False,indent=2));print('episodes',[(x['episode'],x['cue_count'],x['max_rendered_lines_at26']) for x in all5]);print('changes',[(x['episode'],x['cue'],len(x['old_rendered_lines_at26']),len(x['new_rendered_lines_at26'])) for x in changes])
