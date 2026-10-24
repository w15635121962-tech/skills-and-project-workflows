#!/usr/bin/env python3
"""Read-only edit-plan audit. Writes only audit artifacts, never edits plan or Resolve."""
from pathlib import Path
from collections import defaultdict, Counter
from fractions import Fraction
import argparse,json,re,math,hashlib,datetime,difflib,subprocess

HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('plan',nargs='?',default=str(HERE/'剪辑执行计划.json'));ap.add_argument('--report',default=str(HERE/'剪辑执行计划_静态审核.json'));args=ap.parse_args()
planpath=Path(args.plan).resolve();outpath=Path(args.report).resolve()
if not planpath.exists():
 print(json.dumps({'status':'waiting_for_plan','path':str(planpath)},ensure_ascii=False));raise SystemExit(2)
planbytes=planpath.read_bytes();plan=json.loads(planbytes)
plot=json.loads((HERE/'剧情顺序.json').read_text());expected_ep={int(e['episode']):e for e in plot['episodes']}
inv=json.loads((HERE/'素材盘点.json').read_text());media={str(Path(r['path']).resolve()):r for r in inv['files']}
asr=json.loads((HERE/'转录/转录索引.json').read_text());asrby={str(Path(r['source_path']).resolve()):r for r in asr['files']};rawcache={}
errors=[];warnings=[];findings=[];bounds=[];speech=[];coverage=[];activewords={}
def issue(where,code,message,**kw):
 where.append({'code':code,'message':message,**kw})
def srcpath(v):
 p=Path(v);return str((p if p.is_absolute() else HERE.parent/p).resolve())
def meta(path):
 if path in media:return media[path]
 r=subprocess.run([inv['ffprobe_path'],'-v','error','-show_streams','-show_format','-of','json',path],capture_output=True,text=True,timeout=30)
 if r.returncode:raise ValueError(r.stderr.strip())
 d=json.loads(r.stdout);vs=[s for s in d.get('streams',[]) if s.get('codec_type')=='video' and not s.get('disposition',{}).get('attached_pic')];aa=[s for s in d.get('streams',[]) if s.get('codec_type')=='audio']
 f=d.get('format',{});m={'path':path,'duration_seconds':float(f.get('duration',0)),'video_streams':[],'audio_streams':[],'audio_stream_count':len(aa)}
 for v in vs:
  try:fps=float(Fraction(v.get('avg_frame_rate','0/1')))
  except:fps=0
  m['video_streams'].append({'fps':fps,'nb_frames':int(v['nb_frames']) if v.get('nb_frames') else None,'duration_seconds':float(v['duration']) if v.get('duration') else None})
 for a in aa:m['audio_streams'].append({'duration_seconds':float(a['duration']) if a.get('duration') else None})
 media[path]=m;return m
aliases={'mateo':'matteo','mattheo':'matteo','mattelio':'matteo','mattel':'matteo','matteau':'matteo','mateos':'matteos','matteaus':'matteos','mattew':'matteo','baletti':'bellandi','bolandi':'bellandi','belandi':'bellandi','bellandis':'bellandi','elisa':'eliza','alessiah':'alessia','alesia':'alessia','alicia':'alessia','10':'ten','18':'eighteen','28':'twentyeight'}
contractions={"can't":'can not',"cannot":'can not',"won't":'will not',"don't":'do not',"didn't":'did not',"doesn't":'does not',"wasn't":'was not',"weren't":'were not',"isn't":'is not',"aren't":'are not',"couldn't":'could not',"wouldn't":'would not',"shouldn't":'should not',"hadn't":'had not',"haven't":'have not',"hasn't":'has not',"i'm":'i am',"you're":'you are',"we're":'we are',"they're":'they are',"it's":'it is',"that's":'that is',"there's":'there is',"i've":'i have',"you've":'you have',"should've":'should have',"would've":'would have',"could've":'could have',"i'd":'i would',"you'd":'you would',"he'd":'he would',"we'd":'we would',"i'll":'i will',"you'll":'you will',"we'll":'we will',"he'll":'he will'}
def norm(s):
 s=s.lower().replace('’',"'").replace('‘',"'").replace('twenty-eight','twentyeight').replace('twenty eight','twentyeight')
 s=re.sub(r"[a-z]+(?:'[a-z]+)?",lambda m:contractions.get(m.group(),m.group()),s)
 return [aliases.get(x,x) for x in re.findall(r'[a-z0-9]+',s)]
def getraw(path):
 if path not in asrby:return None
 if path not in rawcache:rawcache[path]=json.loads(Path(asrby[path]['json_path']).read_text())
 return rawcache[path]
def duration(item):return item['source_end_frame_exclusive']-item['source_start_frame']
def bestmatch(expected,words):
 e=norm(expected);t=[w['token'] for w in words];n=len(e)
 if not n or not t:return {'score':0,'coverage':0,'matched_text':'','occurrences':[]}
 exact=[]
 for i in range(len(t)-n+1):
  if t[i:i+n]==e:exact.append((i,i+n))
 if exact:
  i,j=exact[0];return {'score':1,'coverage':1,'matched_text':' '.join(t[i:j]),'start_seconds':words[i]['start'],'end_seconds':words[j-1]['end'],'word_indices':[i,j],'occurrences':[{'start_seconds':words[a]['start'],'end_seconds':words[b-1]['end'],'word_indices':[a,b]} for a,b in exact]}
 freq=Counter(t);starts=set()
 for k,x in enumerate(e):
  if freq[x] and (freq[x]<=12 or len(e)<=4):
   for j,z in enumerate(t):
    if z==x:
     for delta in (-1,0,1):
      i=j-k+delta
      if 0<=i<len(t):starts.add(i)
 if not starts:starts=set(range(len(t)))
 best=(0,0,0,0);delta=max(2,round(n*.17))
 for i in starts:
  for length in range(max(1,n-delta),n+delta+1):
   j=min(len(t),i+length)
   sm=difflib.SequenceMatcher(None,e,t[i:j],autojunk=False);matches=sum(b.size for b in sm.get_matching_blocks());sc=sm.ratio();cv=matches/n
   if (sc,cv)>(best[0],best[1]):best=(sc,cv,i,j)
 sc,cv,i,j=best
 return {'score':round(sc,4),'coverage':round(cv,4),'matched_text':' '.join(t[i:j]),'start_seconds':words[i]['start'] if j>i else None,'end_seconds':words[j-1]['end'] if j>i else None,'word_indices':[i,j],'occurrences':[]}

seen_eps=[]
for ep in plan.get('episodes',[]):
 eno=ep.get('episode');seen_eps.append(eno);fps=ep.get('fps');D=ep.get('duration_frames');origin=ep.get('record_start_frame',0)
 if eno not in range(21,26):issue(errors,'unexpected_episode','Expected only local folder EP21–25.',episode=eno)
 if fps!=24:issue(errors,'fps_not_24','Plan fps must be 24 for these CFR sources.',episode=eno,value=fps)
 if not isinstance(D,int) or D<1:issue(errors,'invalid_duration','duration_frames must be positive integer.',episode=eno,value=D);continue
 fps=float(fps or 24)
 videos=ep.get('video',[]);audios=ep.get('audio',[])
 if not videos:issue(errors,'empty_video_track','V1 is empty.',episode=eno)
 validvideo=[];validaudio=[]
 for kind,items in [('video',videos),('audio',audios)]:
  for ix,x in enumerate(items):
   ident={'episode':eno,'kind':kind,'item_index':ix,'tag':x.get('tag')}
   try:
    path=srcpath(x['source_path']);ss=x['source_start_frame'];se=x['source_end_frame_exclusive'];rf=x['record_frame']
    if not all(isinstance(z,int) and not isinstance(z,bool) for z in (ss,se,rf)):raise ValueError('Source and record frame bounds must be integers.')
    if ss<0 or se<=ss or rf<origin:raise ValueError('Negative/reversed source range or record frame before origin.')
    if not Path(path).is_file():raise FileNotFoundError(path)
    still=kind=='video' and Path(path).suffix.lower() in {'.png','.jpg','.jpeg','.webp','.bmp','.tiff','.tif'}
    m=None if still else meta(path);properties=x.get('properties') or {}
    speed=[(k,v) for k,v in properties.items() if 'speed' in k.lower() and float(v or 100)!=100]
    if speed:issue(errors,'unhandled_retime','Plan retime properties require explicit record duration; current schema supplies only source duration.',**ident,properties=speed)
    if still:
     # Original extracted stills are intentional holds on the plan frame grid.
     # Their hold duration is not bounded by ffprobe's nominal single frame.
     lim=None
    elif kind=='video':
     vv=m.get('video_streams') or []
     if not vv:raise ValueError('No video stream.')
     sfps=vv[0].get('fps') or 0
     if abs(sfps-fps)>.0001:issue(errors,'source_fps_mismatch','Source frame indices are not on plan 24fps grid.',**ident,source_path=path,source_fps=sfps)
     lim=vv[0].get('nb_frames') or round((vv[0].get('duration_seconds') or m['duration_seconds'])*sfps)
     if se>lim:raise ValueError(f'Video exclusive end {se} exceeds true source frame count {lim}.')
    else:
     if not m.get('audio_streams'):raise ValueError('No audio stream.')
     secs=max([m.get('duration_seconds') or 0]+[a.get('duration_seconds') or 0 for a in m['audio_streams']])
     lim=math.ceil(secs*fps-1e-6)
     if se>lim:raise ValueError(f'Audio exclusive end {se} exceeds ceil(duration*24) {lim}.')
    end=rf+se-ss
    if end>origin+D:issue(errors,'past_episode_end','Item extends past declared episode duration.',**ident,record_end=end,episode_end=origin+D)
    row={**ident,'source_path':path,'source_start_frame':ss,'source_end_frame_exclusive':se,'record_frame':rf,'record_end_frame':end,'duration_frames':se-ss,'source_limit_frames':lim,'track':x.get('track',1),'subtitle':x.get('subtitle')}
    bounds.append(row)
    (validvideo if kind=='video' else validaudio).append(row)
   except Exception as exc:issue(errors,'source_or_bounds_error',str(exc),**ident,source_path=x.get('source_path'))
 if validvideo:
  cursor=origin
  for x in sorted(validvideo,key=lambda a:a['record_frame']):
   if x['record_frame']!=cursor:issue(errors,'video_gap' if x['record_frame']>cursor else 'video_overlap','V1 must be contiguous without holes or overlap.',episode=eno,expected_record_frame=cursor,actual_record_frame=x['record_frame'],difference_frames=x['record_frame']-cursor,tag=x['tag'])
   cursor=max(cursor,x['record_end_frame'])
  if cursor!=origin+D:issue(errors,'video_duration_mismatch','V1 end differs from declared episode end.',episode=eno,video_end=cursor,episode_end=origin+D)
 bytrack=defaultdict(list)
 for x in validaudio:bytrack[x['track']].append(x)
 for tr,items in bytrack.items():
  if tr not in (1,2):issue(errors,'unexpected_audio_track','Only tracks 1/2 are in declared schema.',episode=eno,track=tr)
  ordered=sorted(items,key=lambda a:a['record_frame'])
  for a,b in zip(ordered,ordered[1:]):
   if b['record_frame']<a['record_end_frame']:issue(errors,'same_track_audio_overlap','Two audio items overlap on the same track.',episode=eno,track=tr,overlap_frames=a['record_end_frame']-b['record_frame'],first_tag=a['tag'],second_tag=b['tag'])
 heard=[];sp=[]
 for x in validaudio:
  path=x['source_path'];raw=getraw(path)
  if raw is None:
   issue(warnings,'no_existing_asr','No existing ASR for this audio source; speech/content audit cannot certify it.',episode=eno,source_path=path,tag=x['tag']);continue
  index=asrby[path];unreliable='low_segment_logprob' in index.get('quality_flags',[]);isvo=index.get('kind')=='narration'
  ss=x['source_start_frame']/fps;se=x['source_end_frame_exclusive']/fps;rf=(x['record_frame']-origin)/fps
  srcwords=raw.get('words') or [w for s in raw.get('segments',[]) for w in s.get('words',[])]
  if unreliable:issue(warnings,'unreliable_asr_source_used','Low-segment-confidence source is scheduled; text is not certified speech.',episode=eno,source_path=path,tag=x['tag'],asr_text=index['text'])
  for side,cut in [('start',ss),('end',se)]:
   connected=any(y is not x and y['track']==x['track'] and y['source_path']==path and ((side=='start' and y['source_end_frame_exclusive']==x['source_start_frame'] and y['record_end_frame']==x['record_frame']) or (side=='end' and y['source_start_frame']==x['source_end_frame_exclusive'] and y['record_frame']==x['record_end_frame'])) for y in validaudio)
   if connected or unreliable:continue
   for w in srcwords:
    st=float(w.get('start',0));en=float(w.get('end',st));prob=float(w.get('probability',1))
    if st+0.03<cut<en-0.03 and prob>=.25:issue(warnings,'possible_word_truncation_from_asr','Cut falls inside a recognized source word; waveform/listening required.',episode=eno,tag=x['tag'],source_path=path,side=side,cut_source_seconds=cut,word=w.get('word'),word_source_start=st,word_source_end=en,probability=prob)
  for w in srcwords:
   st=float(w.get('start',0));en=float(w.get('end',st));overlap=max(0,min(en,se)-max(st,ss))
   if en<=st or overlap/(en-st)<.5:continue
   if unreliable:continue
   tokens=norm(w.get('word',''))
   for token in tokens:
    word={'token':token,'raw_word':w.get('word'),'start':rf+max(st,ss)-ss,'end':rf+min(en,se)-ss,'source_start':st,'source_end':en,'source_path':path,'tag':x['tag'],'track':x['track'],'subtitle':x['subtitle'],'is_vo':isvo,'probability':w.get('probability')}
    heard.append(word)
   if tokens:sp.append({'start':rf+max(st,ss)-ss,'end':rf+min(en,se)-ss,'source_path':path,'tag':x['tag'],'track':x['track'],'is_vo':isvo,'word':w.get('word')})
  # Use recognized segment extents to avoid treating whole source handles as active speech.
  for seg in raw.get('segments',[]):
   st=max(ss,float(seg.get('start',0)));en=min(se,float(seg.get('end',0)))
   if en>st and not unreliable and seg.get('no_speech_prob',0)<.8:speech.append({'episode':eno,'track':x['track'],'tag':x['tag'],'source_path':path,'timeline_start_seconds':rf+st-ss,'timeline_end_seconds':rf+en-ss,'text':seg.get('text'),'is_vo':isvo})
 heard.sort(key=lambda w:(w['start'],w['end']));activewords[eno]=heard
 # Cross-track overlap is measured from word intervals, so silent handles do not cause false alarms.
 overlaps=[]
 for i,a in enumerate(sp):
  for b in sp[i+1:]:
   if a['track']==b['track']:continue
   amount=min(a['end'],b['end'])-max(a['start'],b['start'])
   if amount>.045:overlaps.append({'in_seconds':max(a['start'],b['start']),'out_seconds':min(a['end'],b['end']),'first_tag':a['tag'],'second_tag':b['tag'],'first_word':a['word'],'second_word':b['word'],'first_track':a['track'],'second_track':b['track']})
 if overlaps:issue(errors,'simultaneous_recognized_speech','ASR word intervals show simultaneous speech across A1/A2 (not a subjective listening judgment).',episode=eno,count=len(overlaps),examples=overlaps[:30])
 expected=expected_ep.get(eno,{}).get('source_en_items',[]);matches=[]
 for item in expected:
  kind=item.get('kind');texts=item.get('direct_dialogue_texts_verbatim') or []
  if kind=='dialogue' and not texts:texts=[item['text_verbatim'].strip('"')]
  if kind=='source_narration':texts=[item['text_verbatim']]
  if kind not in ('dialogue','source_narration'):continue
  words=[w for w in heard if w['is_vo']==(kind=='source_narration')]
  for text in texts:
   m=bestmatch(text,words);status='matched_normalized_asr' if m['score']>=.94 and m['coverage']>=.94 else 'manual_check_asr_variant' if m['score']>=.74 and m['coverage']>=.74 else 'not_covered_by_scheduled_reliable_asr'
   row={'episode':eno,'english_episode':eno-1,'source_order':item['order'],'kind':kind,'source_text':text,'status':status,**m}
   matches.append(row)
   if kind=='dialogue' and status!='matched_normalized_asr':issue(findings,'dialogue_not_fully_verified','Original line is missing from or differs in selected reliable ASR; inspect actual source audio before deciding it is missing.',**row)
   if kind=='source_narration' and status=='not_covered_by_scheduled_reliable_asr':issue(findings,'narration_not_audio_covered','No scheduled reliable ASR match; may be visually represented, must be reviewed against intended VO coverage.',**row)
   if kind=='dialogue':
    allowed=sum(1 for it in expected for q in it.get('direct_dialogue_texts_verbatim',[]) if norm(q)==norm(text))
    if len(m['occurrences'])>max(1,allowed):issue(errors,'repeated_original_line','The same original dialogue occurs more times than in the original episode, across chosen audio items.',episode=eno,source_order=item['order'],source_text=text,allowed_count=max(1,allowed),actual_count=len(m['occurrences']),occurrences=m['occurrences'])
 # Script-ordered matched dialogue and VO reveal misplaced anchoring (not merely file ordering).
 reliable=[m for m in matches if m['score']>=.82 and m['coverage']>=.82 and m.get('start_seconds') is not None]
 last=None
 for m in reliable:
  if last and m['start_seconds']+0.08<last['start_seconds']:
   issue(findings,'script_order_or_vo_anchor_inversion','Later original script item occurs earlier on the planned timeline.',episode=eno,earlier_script_item={'order':last['source_order'],'kind':last['kind'],'text':last['source_text'],'timeline_start':last['start_seconds']},later_script_item={'order':m['source_order'],'kind':m['kind'],'text':m['source_text'],'timeline_start':m['start_seconds']})
  last=m
 dialogues=[m for m in reliable if m['kind']=='dialogue']
 for m in reliable:
  if m['kind']!='source_narration':continue
  before=[d for d in dialogues if d['source_order']<m['source_order']];after=[d for d in dialogues if d['source_order']>m['source_order']]
  prev=before[-1] if before else None;nxt=after[0] if after else None
  if prev and m['start_seconds']<prev['end_seconds']-.08:issue(findings,'vo_before_preceding_dialogue_finished','VO script item is placed before its preceding original dialogue has finished.',episode=eno,vo_order=m['source_order'],vo_text=m['source_text'],vo_start=m['start_seconds'],preceding_dialogue=prev['source_text'],preceding_dialogue_end=prev['end_seconds'])
  if nxt and m['end_seconds']>nxt['start_seconds']+.08:issue(findings,'vo_after_following_dialogue_started','VO script item is placed after its following original dialogue has started.',episode=eno,vo_order=m['source_order'],vo_text=m['source_text'],vo_end=m['end_seconds'],following_dialogue=nxt['source_text'],following_dialogue_start=nxt['start_seconds'])
 coverage.append({'episode':eno,'english_episode':eno-1,'duration_frames':D,'duration_seconds':D/fps,'video_items':len(videos),'audio_items':len(audios),'audio_tracks':{str(k):len(v) for k,v in bytrack.items()},'matches':matches,'original_dialogue_count':sum(m['kind']=='dialogue' for m in matches),'dialogue_matched_normalized_asr':sum(m['kind']=='dialogue' and m['status']=='matched_normalized_asr' for m in matches)})
if sorted(seen_eps)!=[21,22,23,24,25]:issue(errors,'episode_set_mismatch','Plan must contain each local episode 21–25 exactly once.',episodes=seen_eps)
report={'created_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'plan_path':str(planpath),'plan_sha256':hashlib.sha256(planbytes).hexdigest(),'review_kind':'Static timeline/source-bounds/ASR-anchoring audit; no subjective listening or playback.','numbering':'Local folder/Chinese EP21–25 corresponds English DOCX EP20–24.','normalization_for_search_only':'Punctuation, contractions, spoken numbers and common ASR spellings of character names canonicalized only for matching. No transcript, subtitle, script or plan changed.','status':'static_errors_found' if errors else 'static_geometry_pass_content_findings_remain' if findings or warnings else 'static_checks_pass_not_playback_or_listening_acceptance','counts':{'errors':len(errors),'warnings':len(warnings),'content_findings':len(findings),'source_ranges_checked':len(bounds)},'errors':errors,'warnings':warnings,'content_findings':findings,'episode_coverage':coverage,'source_ranges':bounds,'scheduled_asr_speech_segments':speech,'limitations':['ASR segment/word timing may be imperfect; truncation and content findings require actual waveform/listening before final audio edits.','A missing ASR match does not prove absent audio, especially low-confidence sources or character names.','Source-narration lines may legitimately be shown visually; unmatched narration is a review finding, not proof of a missing scene.','This audit does not inspect subjective acting, fine lip-sync, final subtitle appearance or Resolve persistence.']}
outpath.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=[f'Status: {report["status"]}',f'Errors: {len(errors)}; warnings: {len(warnings)}; content findings: {len(findings)}',f'Plan SHA256: {report["plan_sha256"]}']
for group,name in ((errors,'ERROR'),(warnings,'WARN'),(findings,'CONTENT')):
 for f in group:lines.append(f'{name} EP{f.get("episode","?")} {f["code"]}: '+json.dumps(f,ensure_ascii=False))
outpath.with_suffix('.txt').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines[:3]));print(str(outpath));raise SystemExit(1 if errors else 0)
