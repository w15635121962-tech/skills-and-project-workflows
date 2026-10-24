from pathlib import Path
import json,re,zipfile,xml.etree.ElementTree as ET,hashlib,math,difflib,sys
R=Path.cwd();W=R/'自动剪辑_女版16-19_21-26_28_20261020';OUT=W/'字幕';ASR=W/'准备/EP16-19_ASR'
SNAP=W/'11集剪辑工作版_最终实读.json';MAN=R/'对标音色旁白制作_20261020/文本核验/manifest.json';DOC=R/'完整剧本/我不再做教父的大码人形抱枕EN.docx'
snapshot=json.loads(SNAP.read_text());manifest=json.loads(MAN.read_text());FPS=24;MAXCOL=28

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def source_quotes():
 with zipfile.ZipFile(DOC) as z:x=ET.fromstring(z.read('word/document.xml'))
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
 ps=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in x.findall('.//w:body/w:p',ns)]
 out={};ep=None
 for i,t in enumerate(ps):
  t=t.strip();m=re.match(r'^Episode\s+(\d+)',t,re.I)
  if m:ep=int(m.group(1));out[ep]=[]
  elif ep and t.startswith('"') and t.endswith('"'):out[ep].append({'text':t[1:-1],'original_quoted_text':t,'docx_paragraph_0based':i})
 return out
QUOTES=source_quotes()
DIALOGUE_QUOTE_INDICES={16:{'大码枕头16-01-02':[0],'大码枕头16-02-01':list(range(1,8)),'大码枕头16-03-01':[8,9],'大码枕头16-04-01':[10]},17:{'大码人形抱枕-第17集-分镜4-1':[0,1,2],'大码人形抱枕-第17集-分镜5-1':[3,4]},18:{},19:{'大码人形抱枕-第19集-分镜4-1':[0,1,2],'大码人形抱枕-第19集-分镜7-1':[3,4],'大码人形抱枕-第19集-分镜8-1':[5,6],'大码人形抱枕-第19集-分镜9-1':[7,8,9]}}
ALIASES={'alicia':'alessia','alaysia':'alessia','alicias':'alessias','alaysias':'alessias','mateo':'matteo','mateos':'matteos','elisa':'eliza','elisas':'elizas','belendi':'bellandi','belandi':'bellandi','bellandy':'bellandi','bellandyfamily':'bellandifamily','belundi':'bellandi','bellandys':'bellandis','10':'ten','10th':'tenth','40':'forty','18':'eighteen','wed':'wehad','hadnt':'hadnot','couldnt':'couldnot','cant':'cannot','didnt':'didnot','wasnt':'wasnot','wouldnt':'wouldnot','shouldve':'shouldhave','im':'iam','id':'ihad','ive':'ihave','weve':'wehave','weure':'were','theyre':'theyare','theyd':'theyhad','its':'itis','theres':'thereis','hehasnt':'hehasnot','hasnt':'hasnot','dont':'donot','youre':'youare','youve':'youhave','youd':'youhad','werenot':'werent','hed':'hehad'}
def norm(t):
 t=t.lower().replace('’',"'").replace('—','').replace('–','');t=re.sub(r'[^a-z0-9]','',t)
 return ALIASES.get(t,t)

def cost(a,b):
 a=norm(a);b=norm(b)
 if a==b:return 0.
 # 0000 is one original token and may be decoded as four zero digits.
 if a in ('0000','zerozerozerozero') and b in ('0000','zerozerozerozero'):return 0.
 ratio=difflib.SequenceMatcher(None,a,b).ratio()
 return min(1.35,1.5*(1-ratio)+.12)

def align(tokens,words):
 n=len(tokens);m=len(words);dp=[[float('inf')]*(m+1) for _ in range(n+1)];back={};dp[0][0]=0
 def put(i,j,v,prev):
  if v<dp[i][j]-1e-9:dp[i][j]=v;back[(i,j)]=prev
 for i in range(n+1):
  for j in range(m+1):
   v=dp[i][j]
   if not math.isfinite(v):continue
   if i<n:put(i+1,j,v+.92,(i,j,'delete',1,0,.92))
   if j<m:put(i,j+1,v+.45,(i,j,'insert',0,1,.45))
   if i<n and j<m:
    c=cost(tokens[i],words[j]['word']);put(i+1,j+1,v+c,(i,j,'match',1,1,c))
   if i<n and j+1<m:
    joined=''.join(w['word'].strip() for w in words[j:j+2]);c=cost(tokens[i],joined)+.12
    if c<.85:put(i+1,j+2,v+c,(i,j,'merge_asr',1,2,c))
   if i+1<n and j<m:
    joined=''.join(tokens[i:i+2]);c=cost(joined,words[j]['word'])+.12
    if c<.85:put(i+2,j+1,v+c,(i,j,'split_asr',2,1,c))
 i,j=n,m;ops=[]
 while i or j:
  prev=back[(i,j)];ops.append(prev);i,j=prev[:2]
 ops.reverse();mapped=[None]*n;insertions=[]
 for i,j,kind,ci,aj,c in ops:
  if kind=='insert':insertions.append({'asr_index':j,'asr_word':words[j]});continue
  if kind=='delete':continue
  st=float(words[j]['start']);en=float(words[j+aj-1]['end']);totalchars=sum(max(1,len(norm(t))) for t in tokens[i:i+ci]);cursor=st
  for k in range(ci):
   end=en if k==ci-1 else cursor+(en-st)*max(1,len(norm(tokens[i+k])))/totalchars
   mapped[i+k]={'canonical_word':tokens[i+k],'source_start_seconds':cursor,'source_end_seconds':max(cursor,end),'asr_words':[words[z]['word'] for z in range(j,j+aj)],'asr_word_indices':list(range(j,j+aj)),'alignment_kind':kind,'alignment_cost':c};cursor=end
 missing=[i for i,v in enumerate(mapped) if v is None]
 for i in missing:
  left=next((mapped[k] for k in range(i-1,-1,-1) if mapped[k]),None);right=next((mapped[k] for k in range(i+1,n) if mapped[k]),None)
  st=left['source_end_seconds'] if left else 0.;en=right['source_start_seconds'] if right else words[-1]['end'];en=max(st,en)
  mapped[i]={'canonical_word':tokens[i],'source_start_seconds':st,'source_end_seconds':en,'asr_words':[],'asr_word_indices':[],'alignment_kind':'interpolated_unmatched','alignment_cost':.92}
 return mapped,{'alignment_total_cost':dp[n][m],'unmatched_canonical_indices':missing,'asr_insertions':insertions,'canonical_word_count':n,'asr_word_count':m}

def canonical(ep,path,track):
 stem=Path(path).stem
 if track==2:
  g=next(g for g in manifest['groups'] if g['basename']==stem);return re.sub(r'\s+',' ',g['generation_text']).strip(),{'kind':'manifest_new_narration','manifest_group':stem,'source_docx_paragraphs':g['source_docx_paragraphs']}
 qs=[QUOTES[ep][i] for i in DIALOGUE_QUOTE_INDICES[ep][stem]]
 return ' '.join(q['text'] for q in qs),{'kind':'original_english_dialogue','quotes':qs}

ABBREV={'mr.','mrs.','ms.','dr.','st.','jr.','sr.'}
def sent_end(word):return bool(re.search(r'[.!?][\"\u201d\u2019\)\]]*$',word)) and word.lower().strip('"') not in ABBREV and not word.endswith('...')

def wrap(tokens):
 text=' '.join(tokens)
 if len(text)<=MAXCOL:return [text]
 choices=[]
 for k in range(1,len(tokens)):
  a=' '.join(tokens[:k]);b=' '.join(tokens[k:])
  if len(a)<=MAXCOL and len(b)<=MAXCOL:
   penalty=abs(len(a)-len(b))-(4 if re.search(r'[,;:\u2014]$',a) else 0)
   if (norm(tokens[k-1]),norm(tokens[k])) in {('mr','bellandi'),('matteo','bellandi'),('alessia','varenna'),('eliza','mercer'),('hudson','medical'),('medical','institute')}:penalty+=22
   choices.append((penalty,[a,b]))
 if choices:return min(choices,key=lambda x:x[0])[1]
 return None

def cue_chunks(words):
 # Respect original sentence boundaries, then find balanced readable chunks
 # globally so a greedy break never strands "bed." or "remember?" alone.
 sentences=[];cur=[]
 for w in words:
  cur.append(w)
  if sent_end(w['canonical_word']):sentences.append(cur);cur=[]
 if cur:sentences.append(cur)
 out=[]
 for sentence in sentences:
  n=len(sentence);dp=[float('inf')]*(n+1);path={};dp[0]=0
  for i in range(n):
   if not math.isfinite(dp[i]):continue
   for j in range(i+1,min(n,i+14)+1):
    ws=sentence[i:j];lines=wrap([w['canonical_word'] for w in ws])
    if lines is None:break
    duration=(ws[-1]['timeline_end_frame']-ws[0]['timeline_start_frame'])/24
    if duration>4.5 and j>i+1:break
    chars=sum(len(l) for l in lines)
    penalty=100+4*((chars-40)/30)**2
    if duration<.8:penalty+=100*(.8-duration)**2
    if len(ws)<3 and n>=4:penalty+=20*(3-len(ws))
    if j<n and re.search(r'[,;:]$',ws[-1]['canonical_word']):penalty-=5
    if len(lines)==2:penalty+=abs(len(lines[0])-len(lines[1]))*.03
    value=dp[i]+penalty
    if value<dp[j]:dp[j]=value;path[j]=(i,lines)
  if n not in path:raise ValueError(('cannot wrap sentence',sentence))
  parts=[];j=n
  while j:
   i,lines=path[j];parts.append((sentence[i:j],lines));j=i
  out.extend(reversed(parts))
 return out

def tc(frame):
 ms=round(frame*1000/24);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
 return f'{h:02}:{m:02}:{s:02},{ms:03}'

def make(ep):
 e=next(e for e in snapshot['episodes'] if e['episode']==ep);tracks=[t for t in e['tracks']['audio'] if t['index'] in (1,2)];sources={};clips=[];word_events=[];pending=[]
 for t in tracks:
  for ix,c in enumerate(t['items']):
   if not c.get('enabled',True):continue
   path=c['source_path'];stem=Path(path).stem;key=(path,t['index'])
   if key not in sources:
    asrp=ASR/(stem+'.json');raw=json.loads(asrp.read_text());aw=[w for s in raw['segments'] for w in s.get('words',[]) if w['word'].strip()]
    text,prov=canonical(ep,path,t['index']);tokens=text.split();aligned,stats=align(tokens,aw)
    sources[key]={'source_path':path,'track':t['index'],'canonical_text':text,'canonical_provenance':prov,'blind_asr_json':str(asrp),'blind_asr_sha256':sha(asrp),'source_sha256':raw['source_sha256'],'alignment':stats,'words':aligned}
   src=sources[key];rate=1.1 if t['index']==2 else 1.;clip_id=f'A{t["index"]}_{ix+1:02d}';events=[]
   for wi,w in enumerate(src['words']):
    mid=(w['source_start_seconds']+w['source_end_seconds'])/2
    if not (c['source_start']-1e-4<=mid<c['source_end']+1e-4):continue
    st=c['start']+(w['source_start_seconds']-c['source_start'])/rate*24;en=c['start']+(w['source_end_seconds']-c['source_start'])/rate*24
    st=max(c['start'],min(c['end']-1,math.floor(st+1e-7)));en=max(st+1,min(c['end'],math.ceil(en-1e-7)))
    ev={**w,'canonical_source_word_index':wi,'clip_id':clip_id,'track':t['index'],'speed_percent':rate*100,'timeline_start_frame':st,'timeline_end_frame':en,'timeline_start_seconds':st/24,'timeline_end_seconds':en/24,'source_path':path}
    events.append(ev);word_events.append(ev)
   clips.append({'id':clip_id,'source_path':path,'track':t['index'],'record_start_frame':c['start'],'record_end_frame_exclusive':c['end'],'source_start_seconds_actual':c['source_start'],'source_end_seconds_actual':c['source_end'],'speed_percent':rate*100,'word_indices':[w['canonical_source_word_index'] for w in events]})
   for ws,lines in cue_chunks(events):
    pending.append({'clip_id':clip_id,'track':t['index'],'source_path':path,'start_frame':ws[0]['timeline_start_frame'],'end_frame_exclusive':min(c['end'],max(ws[-1]['timeline_end_frame']+2,ws[0]['timeline_start_frame']+4)),'clip_end_frame':c['end'],'lines':lines,'words':ws,'canonical_text':' '.join(w['canonical_word'] for w in ws)})
 pending.sort(key=lambda c:(c['start_frame'],c['track']))
 for i,c in enumerate(pending):
  if i+1<len(pending):c['end_frame_exclusive']=min(c['end_frame_exclusive'],pending[i+1]['start_frame'])
  if c['end_frame_exclusive']<=c['start_frame']:raise ValueError(('zero cue',ep,c))
  c['index']=i+1;c['start_srt']=tc(c['start_frame']);c['end_srt']=tc(c['end_frame_exclusive']);c['text']='\n'.join(c['lines'])
  assert len(c['lines'])<=3 and all(len(l)<=MAXCOL for l in c['lines'])
 # Every canonical word included exactly once for every actual unique source.
 source_checks=[]
 for key,src in sources.items():
  observed=[w['canonical_source_word_index'] for w in word_events if w['source_path']==src['source_path'] and w['track']==src['track']];counts={i:observed.count(i) for i in range(len(src['words']))};missing=[i for i,n in counts.items() if n==0];double=[i for i,n in counts.items() if n>1]
  if missing or double:raise ValueError(('coverage',ep,Path(src['source_path']).name,missing,double))
  source_checks.append({'source_path':src['source_path'],'track':src['track'],'canonical_word_count':len(src['words']),'words_mapped_exactly_once':True,'unmatched_canonical_words':src['alignment']['unmatched_canonical_indices'],'asr_insertions_not_added_to_canonical':src['alignment']['asr_insertions']})
 srt='\n\n'.join(f'{c["index"]}\n{c["start_srt"]} --> {c["end_srt"]}\n{c["text"]}' for c in pending)+'\n'
 out=OUT/'SRT'/f'EP{ep}.srt';out.write_text(srt,encoding='utf-8-sig')
 v=3 if ep==19 else 2;otio=W/f'原生时间线/大码_女版_EP{ep}_新旁白110_自动剪辑_v{v}_保存重开后.otio'
 report={'episode':ep,'timeline':e['timeline'],'frame_rate':24,'relative_timeline_start_timecode':'00:00:00:00','timeline_end_frame_exclusive':e['end'],'srt_path':str(out),'srt_sha256':sha(out),'time_mapping':'record_frame + (blind_ASR_source_word_seconds - actual_snapshot_source_start_seconds) / native_speed_scalar *24; floor start, ceil end; native A2 speed confirmed1.1 in saved/reopenedOTIO. Cue ends exclusive, quantized24fps.','canonical_text_policy':'English source dialogue and generation manifest narration retained; ASR only supplies word times. ASR names/digits/contractions normalized for alignment, never substituted into subtitle text. Outer dialogue quotation marks omitted for display, inner quotes retained.','line_policy':{'max_lines':3,'preferred_max_lines':2,'max_characters_per_line':MAXCOL,'split_words':False},'inputs':{'final_snapshot':str(SNAP),'final_snapshot_sha256':sha(SNAP),'saved_reopened_otio':str(otio),'saved_reopened_otio_sha256':sha(otio),'manifest':str(MAN),'manifest_sha256':sha(MAN),'english_docx':str(DOC),'english_docx_sha256':sha(DOC)},'clips':clips,'sources':list(sources.values()),'cues':pending,'source_coverage_checks':source_checks,'validation':{'cue_count':len(pending),'all_cues_max3_lines':True,'all_cues_max2_lines':all(len(c['lines'])<=2 for c in pending),'all_lines_max28_characters':True,'no_cue_time_overlaps':all(a['end_frame_exclusive']<=b['start_frame'] for a,b in zip(pending,pending[1:])),'all_canonical_words_mapped_once':True,'interpolated_unmatched_canonical_word_count':sum(len(s['alignment']['unmatched_canonical_indices']) for s in sources.values()),'human_listening_or_playback_verified':False},'known_limit':'Word times are blind ASR plus actual native source/record mapping; final on-screen font preset and complete listening/playback remain root UI work. A3 ambience/hallucination candidates not subtitled.'}
 jp=OUT/'词时码'/f'EP{ep}_cue与词时码映射.json';jp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'episode':ep,'cues':len(pending),'lines_max':max(len(c['lines']) for c in pending),'canonical_sources':len(sources),'words':len(word_events),'unmatched':report['validation']['interpolated_unmatched_canonical_word_count'],'srt':str(out)},ensure_ascii=False))
 for src in sources.values():
  if src['alignment']['unmatched_canonical_indices']:print('UNMATCHED',Path(src['source_path']).name,src['alignment']['unmatched_canonical_indices'])
 return report
if __name__=='__main__':
 for ep in ([int(a) for a in sys.argv[1:]] or [16,17,18,19]):make(ep)
