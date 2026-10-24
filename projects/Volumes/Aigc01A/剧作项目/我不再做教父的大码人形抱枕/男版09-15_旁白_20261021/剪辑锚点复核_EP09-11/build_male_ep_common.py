from pathlib import Path
import json,re,math,subprocess,functools
import numpy as np
from PIL import Image,ImageDraw,ImageFont
B=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/男版09-15_旁白_20261021');F=24;O=B/'剪辑锚点复核_EP09-11';O.mkdir(exist_ok=True)
M=json.loads((B/'准备/narration_manifest.json').read_text());A=json.loads((B/'ASR/同期对白与原带音轨核查.json').read_text());I=json.loads((B/'剪辑脚本准备/media_inventory_native.json').read_text());ff=json.loads((B/'剪辑素材只读核查_20261022.json').read_text())['tools']['ffmpeg'];vs={v['filename']:v for e in I['episodes'] for v in e['videos']}
normalize=lambda x:re.sub(r'[^a-z0-9]+','',x.lower())
def align_words(cw,ww):
 @functools.lru_cache(None)
 def dp(i,j):
  if i==len(cw):return (0,[]) if j==len(ww) else (999,[])
  if j==len(ww):return 999,[]
  opts=[]
  for k in range(1,min(3,len(ww)-j)+1):
   ob=''.join(normalize(w['word']) for w in ww[j:j+k]);co=normalize(cw[i]);cost=0 if ob==co else (1 if k==1 else 3)
   rem,rows=dp(i+1,j+k);opts.append((cost+rem,[(i,j,j+k)]+rows))
  return min(opts,key=lambda x:x[0])
 cost,rows=dp(0,0);assert len(rows)==len(cw)
 return [(cw[i],dict(word=' '.join(w['word'] for w in ww[j:k]),start=ww[j]['start'],end=ww[k-1]['end'],probability=min(w.get('probability',0) for w in ww[j:k]),asr_indices=list(range(j,k)))) for i,j,k in rows],cost

def build(ep,rows,vo_specs,extra_limits=None):
 gs={g['narration_sequence']:g for g in M['groups'] if g['episode']==ep};D=[u for u in A['dialogue_units'] if u['episode']==ep];block=[];pos=0
 for fn,s,e,tag in rows:
  assert 0<=s<e<=int(vs[fn]['video_streams'][0]['nb_frames'])
  block.append(dict(filename=fn,source_start_frame=s,source_end_frame=e,record_frame=pos,duration_frames=e-s,tag=tag));pos+=e-s
 levels={x['source_path']:x for x in json.loads((B/'ASR/new_narration/source_levels.json').read_text())['files']}
 narration=[];events=[];cuts=[];alignment=[]
 for seq,s,e,blockidx,add,paras in vo_specs:
  r=block[blockidx]['record_frame']+add;g=gs[seq];p=Path(g['planned_audio_path']);raw=json.loads((B/f'ASR/new_narration/raw_large-v3-turbo/EP{ep:02d}/{p.stem}.json').read_text());assert e/F<=raw['decoded_duration_seconds']+.04,(seq,e,raw['decoded_duration_seconds'])
  narration.append(dict(path=str(p),source_start_frame=s,source_end_frame=e,record_frame=r,gain_db=levels.get(str(p),{}).get('suggested_speech_gain_db',0),speed_percent=100,tag=f'P{paras} original narration; sentence-safe edit',source_docx_paragraphs=paras,audio_sha256=raw['source_sha256']))
  mapped,cost=align_words(g['generation_text'].split(),raw['words']);alignment.append(dict(logical_basename=p.stem,alignment_cost=cost,expected_words=len(mapped),observed_words=len(raw['words'])))
  for wi,(c,w) in enumerate(mapped):
   st,et=w['start']*F,w['end']*F
   if st>=s-.001 and et<=e+.001:events.append(dict(word=c,start_frame=max(r,int(math.floor(st-s+r))),end_frame=max(r+1,int(math.ceil(et-s+r))),source_path=str(p),source_word_index=wi,canonical_original_token_index=wi,observed_source_word_indices=w['asr_indices'],source_start_seconds=w['start'],source_end_seconds=w['end'],speaker='Oliver narration',source_kind='new_narration',boundary_before=wi==0))
   elif st<e and et>s:raise AssertionError(('word crosses VO trim',seq,wi,c,s,e,st,et))
 # Each role original quote gets exactly one source delivery from selected, fully containing blocks.
 role=[]
 for u in D:
  choices=[]
  for c in u['source_candidates']:
   for b in block:
    if b['filename']==Path(c['source_path']).name and b['source_start_frame']<=c['word_start_seconds']*F+.001 and b['source_end_frame']>=c['word_end_seconds']*F-.001:choices.append((c,b))
  assert len(choices)==1,(u['id'],[(Path(c['source_path']).name,b) for c,b in choices]);c,b=choices[0];offset=b['record_frame']-b['source_start_frame'];role.append(dict(id=u['id'],docx_paragraph=u['docx_paragraph'],original_text=u['original_text'],source_path=c['source_path'],source_start_seconds=c['word_start_seconds'],source_end_seconds=c['word_end_seconds'],record_start_frame=math.floor(c['word_start_seconds']*F)+offset,record_end_frame=math.ceil(c['word_end_seconds']*F)+offset))
  for wi,w in enumerate(c['word_events']):events.append(dict(word=w['original_word'],start_frame=math.floor(w['start']*F)+offset,end_frame=max(math.floor(w['start']*F)+offset+1,math.ceil(w['end']*F)+offset),source_path=c['source_path'],source_start_seconds=w['start'],source_end_seconds=w['end'],speaker='original role dialogue',source_kind='sync_dialogue',boundary_before=wi==0))
 video=[]
 for b in block:
  fn=b['filename'];s=b['source_start_frame'];e=b['source_end_frame'];bound={s,e};sp=[]
  for d in role:
   if Path(d['source_path']).name!=fn:continue
   a=max(s,math.floor(d['source_start_seconds']*F)-6);z=min(e,math.ceil(d['source_end_seconds']*F)+6)
   if a<z:sp.append((a,z));bound.update([a,z])
  xx=sorted(bound)
  for a,z in zip(xx,xx[1:]):
   speech=any(a>=x and z<=y for x,y in sp);video.append(dict(path=vs[fn]['path'],source_start_frame=a,source_end_frame=z,record_frame=b['record_frame']+a-s,gain_db=0 if speech else -12,speed_percent=100,tag=b['tag']+(' | dialogue unity' if speech else ' | linked environment under VO')))
 events.sort(key=lambda x:(x['start_frame'],x['end_frame']));assert len(events)==sum(len(g['generation_text'].split()) for g in gs.values())+sum(len(x['original_text'].split()) for x in D)
 for x,y in zip(events,events[1:]):
  if x['source_path']!=y['source_path'] or y['start_frame']-x['end_frame']>=12:y['boundary_before']=True
 source_ep=next(x for x in M['episodes'] if x['episode']==ep);canonical=[]
 for p in source_ep['original_paragraphs_and_retained_narration']:canonical.extend(p['raw_source_text'].strip().replace('"','').split())
 actual=[normalize(x['word']) for x in events];expected=[normalize(x) for x in canonical];assert actual==expected,('canonical order mismatch',ep,[(i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b][:8])
 for n in narration:
  ns=n['record_frame'];ne=ns+n['source_end_frame']-n['source_start_frame']
  for d in role:assert max(ns,d['record_start_frame'])>=min(ne,d['record_end_frame']),('VO role overlap',n,d)
 # Verify source uniqueness in picture and narration independently.
 for arr in [video,narration]:
  for i,x in enumerate(arr):
   for y in arr[i+1:]:
    if x['path']==y['path']:assert max(x['source_start_frame'],y['source_start_frame'])>=min(x['source_end_frame'],y['source_end_frame']),('source reused',x,y)
 plan=dict(status=f'READY_EP{ep:02d}_STRUCTURAL_REVIEW_AUDIO_AUDITION_PENDING',project='大码枕头',fps=24,scope=f'male EP{ep:02d} only; parent merge reviewed episode',episodes=[dict(episode=ep,timeline_name=f'大码_男版_EP{ep:02d}_新男版音色_原速旁白_自动剪辑_v1',duration_frames=pos,video=video,narration=narration,subtitle_srt=str(B/f'字幕/EP{ep:02d}.srt'),picture_blocks=block,role_dialogue=role,limitations=['No Resolve edits or normal-speed human listening performed by plan author.','Actual contact sheets inspected; not full motion/lip-sync playback.','Role and VO trims checked against observed words; waveform plots cover VO internal splits.','Original spelling kept for recognition-only proper-name differences.']+(extra_limits or []))],proof=dict(contact_sheets=[str(x) for x in O.glob(f'EP{ep:02d}*.jpg')],original_words_on_timeline=len(events),role_quotes_once=len(role),narration_logical_segments=len(gs),narration_pieces=len(narration),vo_role_overlap=False,source_interval_overlap=False,video_sync_audio_same_bounds=True,source_speed_percent=100,canonical_word_alignment=alignment))
 (B/f'剪辑计划_EP{ep:02d}_可落地帧计划.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2));(B/f'EP{ep:02d}_原文词事件.json').write_text(json.dumps(dict(fps=24,canonical_original_words_verified=True,episodes=[dict(episode=ep,duration_frames=pos,events=events)]),ensure_ascii=False,indent=2))
 # All unique internal source cuts, including removed long between-sentence gaps.
 for seq,s,e,_,_,_ in vo_specs:
  for cf in [s,e]:
   rawp=B/f'ASR/new_narration/raw_large-v3-turbo/EP{ep:02d}/{Path(gs[seq]["planned_audio_path"]).stem}.json';raw=json.loads(rawp.read_text());c=cf/F
   if cf==0 or c>raw['words'][-1]['end']:continue
   prev=[w for w in raw['words'] if w['end']<=c];nex=[w for w in raw['words'] if w['start']>=c]
   if prev and nex and not any(x['seq']==seq and x['cut_frame']==cf for x in cuts):cuts.append(dict(seq=seq,source_path=gs[seq]['planned_audio_path'],cut_frame=cf,cut_seconds=c,observed_prior_word=prev[-1],observed_next_word=nex[0],human_audition=False))
 if cuts:
  font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14);im=Image.new('RGB',(1200,230*len(cuts)),(24,24,24));draw=ImageDraw.Draw(im);cache={}
  for row,z in enumerate(cuts):
   p=z['source_path'];cache.setdefault(p,np.frombuffer(subprocess.check_output([ff,'-v','error','-i',p,'-f','f32le','-ac','1','-ar','16000','-']),dtype='<f4'));a=cache[p];c=z['cut_seconds'];lo=max(0,c-.7);hi=min(len(a)/16000,c+.7);x=a[int(lo*16000):int(hi*16000)];top=row*230;mid=top+130;draw.text((10,top+5),f'EP{ep:02d} VO{z["seq"]} split {z["cut_frame"]}f / {c:.6f}s | source waveform; not human audition',fill='white',font=font)
   for j in range(1180):
    v=x[int(j*len(x)/1180):int((j+1)*len(x)/1180)];val=float(np.max(np.abs(v))) if len(v) else 0;yy=min(80,round(val*130));draw.line((10+j,mid-yy,10+j,mid+yy),fill=(90,210,230))
   px=10+int((c-lo)/(hi-lo)*1180);draw.line((px,top+32,px,top+218),fill=(255,100,80),width=2);pr=z['observed_prior_word'];nx=z['observed_next_word'];draw.text((10,top+25),f'Observed prior {pr["word"]!r} ends {pr["end"]:.3f}s; next {nx["word"]!r} starts {nx["start"]:.3f}s',fill=(220,220,220),font=font)
   z['actual_pcm_cut_window_peak_dbfs']=float(20*np.log10(max(1e-9,float(np.max(np.abs(a[max(0,int((c-.02)*16000)):int((c+.02)*16000)]))))))
  im.save(O/f'EP{ep:02d}_VO_internal_split_waveforms.jpg',quality=90);(O/f'EP{ep:02d}_VO_internal_split_waveforms.json').write_text(json.dumps(cuts,ensure_ascii=False,indent=2))
 print('EP',ep,'frames',pos,'sec',pos/24,'V',len(video),'VO',len(narration),'words',len(events),flush=True)
 return plan,events
