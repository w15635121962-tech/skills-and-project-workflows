# -*- coding: utf-8 -*-
"""Read-only, manifest-whitelisted acceptance of this task's 24 female VO MP3s.

Default: validate scope/mapping only. --prepare: validate local dependencies and
model provenance without decoding or recognizing any audio. --execute: process
only exact downloaded manifest paths from selected episodes; no waiting/polling.
No expected text, script, hotwords or initial_prompt enters the recognizer.
No browser/Resolve operation, network access, source rename or media rewrite.
"""
from pathlib import Path
import argparse,csv,datetime as dt,difflib,hashlib,importlib.metadata,json,math,os,re,shutil,subprocess,sys,time,traceback
sys.dont_write_bytecode=True
os.environ['PYTHONDONTWRITEBYTECODE']='1'
HERE=Path(__file__).resolve().parent
TASK=HERE.parent
PROJECT=TASK.parent
MANIFEST=TASK/'文本核验/manifest.json'
INDEPENDENT_AUDIT=TASK/'文本核验/独立复核_原文旁白与音频验收办法.json'
SKILL=Path('/Users/zc/.codex/skills/ffmpeg-skill')
FFBIN=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin')
RUNTIME=PROJECT/'配音制作_前3集/制作资料/音频内容与顺序核验_20261018/ASR'
COMPAT=PROJECT/'达芬奇剪辑_EP21-25_20261020/转录/runtime_compatible'
SITE=RUNTIME/'.venv/lib/python3.12/site-packages'
MODEL=RUNTIME/'models/large-v3-turbo'
PARAMETERS=dict(language='en',task='transcribe',temperature=0.0,condition_on_previous_text=False,initial_prompt=None,word_timestamps=True,fp16=True,verbose=None)
ALLOWED_EPISODES=(4,5,6)
EXPECTED_COUNTS={4:8,5:7,6:9}
EXPECTED_VOICE='对标女旁白_测试A_1020'
MANIFEST_SHA_PIN='a29e094ab15fae9da29e770c4c80586a8d4d8005e04084339503e3e153a32d38' # populated from independent audit at preparation
PATTERN=re.compile(r'^大码女版枕头(04|05|06)-(\d{2})-01$')

def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def safe_output(p):
 p=Path(p);assert p.resolve().is_relative_to(HERE),'All outputs must remain in this task ASR directory';return p
def default(x):
 if hasattr(x,'item'):return x.item()
 if hasattr(x,'tolist'):return x.tolist()
 return str(x)
def save(p,value):
 p=safe_output(p);p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=default)+'\n',encoding='utf-8');tmp.replace(p)
def norm(t,aliases=False):
 t=t.lower().replace('’',"'")
 words=re.findall(r"[a-z]+(?:'[a-z]+)?|\d+",t)
 if aliases:
  mapping={'mateo':'matteo','mattheo':'matteo','matelo':'matteo','mateel':'matteo','metello':'matteo','mattew':'matteo','matthew':'matteo','belandi':'bellandi','bellandis':'bellandi',"bellandi's":'bellandi','belandis':'bellandi','seraphina':'serafina'}
  words=[mapping.get(w,w)for w in words]
 return words

def load_scope():
 assert TASK.name=='女版04-06_新旁白_20261023'and HERE.name=='ASR','This script is task-local only'
 data=MANIFEST.read_bytes();m=json.loads(data)
 audit=json.loads(INDEPENDENT_AUDIT.read_text(encoding='utf-8'))
 actual=hashlib.sha256(data).hexdigest()
 assert audit['status']=='PASS_TEXT_ONLY_READY_FOR_GENERATION_REVIEW','Require independently audited text'
 assert actual==audit['manifest_sha256']==MANIFEST_SHA_PIN,'Audited manifest changed; no implicit new scope'
 assert m['version']=='女版'and m['scope_episode_order']==list(ALLOWED_EPISODES)
 assert m['model']=='Seed TTS'and m['mode']=='文本朗读'and m['speed_percent']==100 and m['voice']==EXPECTED_VOICE
 assert digest(m['source_docx'])==m['source_docx_sha256']==audit['source_docx_sha256'],'Source DOCX changed'
 assert len(m['groups'])==24
 rows=[]
 for ep in ALLOWED_EPISODES:
  groups=[g for g in m['groups']if g['episode']==ep];assert len(groups)==EXPECTED_COUNTS[ep]
  for i,g in enumerate(groups,1):
   expected=f'大码女版枕头{ep:02d}-{i:02d}-01';assert PATTERN.fullmatch(g['basename'])and g['basename']==expected
   assert g['narration_sequence']==i and g['take']==1
   assert g['voice']==EXPECTED_VOICE and g['speed_percent']==100
   assert len(g['generation_text'])==g['characters']<=200
   txt=Path(g['text_file']);assert txt.resolve().is_relative_to(TASK/'文本核验/分段')
   assert txt.read_text(encoding='utf-8')==g['generation_text']and digest(txt)==g['generation_text_sha256']
   p=TASK/'音频'/f'第{ep:02d}集'/(expected+'.mp3')
   assert str(p)==g['planned_audio_path']and g['planned_audio_filename']==p.name,'Exact manifest audio path required'
   # Resolve path even if not yet present; existing directory symlinks may not escape task.
   assert p.resolve().is_relative_to(TASK.resolve()),'Audio symlink escapes this task'
   rows.append(dict(episode=ep,sequence=i,take=1,basename=expected,source_path=str(p),canonical_text=g['generation_text'],text_sha256=g['generation_text_sha256'],text_path=str(txt),docx_paragraphs=g['source_docx_paragraphs'],expected_voice=EXPECTED_VOICE,speed_percent=100))
 assert len({r['source_path']for r in rows})==len(rows)==24
 mapping=dict(created_at_utc=stamp(),scope='female_EP04_EP05_EP06_only',manifest_path=str(MANIFEST),manifest_sha256=actual,independent_text_audit=str(INDEPENDENT_AUDIT),independent_text_audit_sha256=digest(INDEPENDENT_AUDIT),source_docx=m['source_docx'],source_docx_sha256=m['source_docx_sha256'],count=24,files=rows,no_directory_glob_used=True,reference_or_other_task_audio_excluded=True)
 save(HERE/'源24段白名单.json',mapping)
 return m,rows,mapping

def configure_runtime():
 assert sys.version_info[:2]==(3,12),'Use the verified existing Python3.12 runtime'
 assert COMPAT.is_dir()and SITE.is_dir()
 sys.path[:0]=[str(COMPAT),str(SITE)]
 os.environ['PATH']=str(FFBIN)+os.pathsep+os.environ.get('PATH','')
 os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1';os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN']='1'
 os.environ['PYTHONDONTWRITEBYTECODE']='1'
 assert Path(shutil.which('ffmpeg')).resolve()==(FFBIN/'ffmpeg').resolve()
 assert Path(shutil.which('ffprobe')).resolve()==(FFBIN/'ffprobe').resolve()
 import mlx.core as mx
 import mlx_whisper
 from mlx_whisper.audio import load_audio,SAMPLE_RATE
 import numpy as np
 assert SAMPLE_RATE==16000
 prov=json.loads((MODEL/'provenance.json').read_text(encoding='utf-8'))
 checked=[]
 for item in prov['files']:
  p=MODEL/'weights'/item['path'];assert p.is_file()and p.stat().st_size==item['bytes']
  assert digest(p)==item['sha256'],'Model provenance checksum mismatch'
  checked.append(dict(path=str(p),size_bytes=p.stat().st_size,sha256=item['sha256']))
 def version(name):
  try:return importlib.metadata.version(name)
  except importlib.metadata.PackageNotFoundError:return 'metadata unavailable; imported module path verified'
 deps=dict(validated_at_utc=stamp(),python_executable=sys.executable,python_version=sys.version,mlx_device=str(mx.default_device()),engine='mlx-whisper',engine_version=version('mlx-whisper'),mlx_version=version('mlx'),engine_module_path=mlx_whisper.__file__,numpy_version=np.__version__,audio_decode_sample_rate=SAMPLE_RATE,ffmpeg_path=shutil.which('ffmpeg'),ffprobe_path=shutil.which('ffprobe'),model='large-v3-turbo',model_revision=prov['revision'],model_path=str(MODEL/'weights'),model_files_sha256_checked=checked,decode_parameters=PARAMETERS,offline=True,no_model_transcription_invoked=True)
 return mlx_whisper,load_audio,SAMPLE_RATE,np,prov,deps

def run_skill(tool,path):
 assert tool in {'probe','loudness'}
 args=[sys.executable,str(SKILL/'scripts'/(tool+'.py')),str(path)]
 if tool=='probe':args+=['--json']
 else:args+=['--measure-only','-I','-18','--tp','-2','--json']
 proc=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',timeout=180,env=dict(os.environ))
 log=HERE/'measurements'/(path.stem+'_'+tool+'.log');safe_output(log).parent.mkdir(parents=True,exist_ok=True)
 log.write_text(proc.stderr,encoding='utf-8')
 assert proc.returncode==0,f'{tool} wrapper failed: {proc.stdout[-1200:]} {proc.stderr[-1200:]}'
 value=json.loads(proc.stdout)
 save(HERE/'measurements'/(path.stem+'_'+tool+'.json'),dict(tool=tool,argv=args,source_path=str(path),result=value,stderr_log=str(log),source_modified=False))
 return value,proc.stderr

def pcm_measures(audio,sr,np):
 a=np.asarray(audio,dtype=np.float32)
 assert len(a)>0 and bool(np.isfinite(a).all()),'Empty/nonfinite decoded PCM'
 window=round(sr*.01);count=len(a)//window
 rms=np.sqrt(np.mean(np.square(a[:count*window].reshape(count,window)),axis=1))if count else np.array([])
 active=np.flatnonzero(rms>10**(-45/20))
 leading=float(active[0])*.01 if len(active)else len(a)/sr
 trailing=(count-1-float(active[-1]))*.01 if len(active)else len(a)/sr
 peak=float(np.max(np.abs(a)));full=int(np.count_nonzero(np.abs(a)>=.9999))
 return dict(decoded_sample_count=len(a),decoded_sample_rate=sr,decoded_duration_seconds=len(a)/sr,decoded_mono=True,peak_pcm_dbfs=20*math.log10(max(peak,1e-12)),near_full_scale_sample_count=full,leading_below_minus45db_rms_seconds=round(leading,4),trailing_below_minus45db_rms_seconds=round(trailing,4),quiet_window_seconds=.01,quiet_threshold_dbfs=-45,all_quiet=not len(active),silence_diagnostic_only_no_trim=True)

def comparison(expected,observed):
 a=norm(expected);b=norm(observed);aa=norm(expected,True);bb=norm(observed,True)
 opcodes=[]
 for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
  if tag!='equal':opcodes.append(dict(kind=tag,expected_token_range=[i,j],observed_token_range=[k,l],expected_tokens=a[i:j],observed_tokens=b[k:l]))
 return dict(expected_tokens=a,observed_tokens=b,strict_word_sequence_equal=a==b,word_sequence_equal_with_documented_name_aliases=aa==bb,strict_differences=opcodes,expected_first_tokens=a[:6],observed_first_tokens=b[:6],expected_last_tokens=a[-6:],observed_last_tokens=b[-6:],source_words_unchanged=True,alignment_is_post_recognition_only=True,aliases_are_diagnostic_not_proof_of_pronunciation=True)

def sidecars(rec,target):
 target=safe_output(target)
 text=target.with_suffix('.txt');text.write_text(rec['text'].strip()+'\n',encoding='utf-8')
 with target.with_suffix('.words.tsv').open('w',encoding='utf-8-sig',newline='')as f:
  writer=csv.writer(f,delimiter='\t');writer.writerow(['word_index','source_start_seconds','source_end_seconds','word','probability'])
  for i,w in enumerate(rec['words']):writer.writerow([i,w['start'],w['end'],w['word'],w.get('probability')])

def process(row,runtime):
 mlx_whisper,load_audio,sr,np,prov,deps=runtime
 source=Path(row['source_path']);assert source.is_file()and not source.is_symlink(),'Missing audio or source symlink'
 stat1=source.stat();assert stat1.st_size>0 and time.time()-stat1.st_mtime>1.5,'Download empty or too recent; retry after stable completion'
 time.sleep(.2);stat2=source.stat();assert(stat1.st_size,stat1.st_mtime_ns)==(stat2.st_size,stat2.st_mtime_ns),'Download still changing'
 source_sha=digest(source);target=HERE/'raw_large-v3-turbo/narration'/(source.stem+'.json')
 if target.exists():
  old=json.loads(target.read_text(encoding='utf-8'))
  assert old['source_sha256']==source_sha,'Source replaced under an already-recognized filename: do not overwrite existing ASR; review take naming'
  assert old['decode_parameters']==PARAMETERS and old['canonical_text_sha256']==row['text_sha256']and old['model_revision']==prov['revision'],'Cached ASR parameter/text/model mismatch'
  return old,True
 started=time.monotonic()
 probe,probe_log=run_skill('probe',source)
 loudness,loudness_log=run_skill('loudness',source)
 # Existing mlx_whisper.audio.load_audio performs complete ffmpeg decode,
 # mono downmix and16kHz s16PCM conversion; no file is written or rewritten.
 audio=load_audio(str(source));pcm=pcm_measures(audio,sr,np)
 assert not pcm['all_quiet'],'Audio is entirely quiet at diagnostic threshold'
 result=mlx_whisper.transcribe(audio,path_or_hf_repo=str(MODEL/'weights'),**PARAMETERS)
 assert digest(source)==source_sha,'Source modified during acceptance'
 segs=result.get('segments',[]);words=[w for s in segs for w in s.get('words',[])]
 flags=[]
 if not words:flags.append('no_recognized_words')
 if any(w.get('probability',1)<.6 for w in words):flags.append('low_word_confidence')
 if any(s.get('avg_logprob',0)<-.8 for s in segs):flags.append('low_segment_logprob')
 if any(s.get('no_speech_prob',0)>.5 for s in segs):flags.append('high_no_speech_probability')
 if any(s.get('compression_ratio',0)>2.4 for s in segs):flags.append('possible_repetition_hallucination')
 if any(w['end']<=w['start']for w in words):flags.append('zero_or_negative_word_duration')
 if any(w['start']<0 or w['end']>pcm['decoded_duration_seconds']+.1 for w in words):flags.append('word_time_out_of_source_bounds')
 cmp=comparison(row['canonical_text'],result.get('text',''))
 if not cmp['strict_word_sequence_equal']:flags.append('transcript_differs_from_original_listen_review')
 if pcm['leading_below_minus45db_rms_seconds']>.8:flags.append('long_leading_quiet_diagnostic_only')
 if pcm['trailing_below_minus45db_rms_seconds']>1.2:flags.append('long_trailing_quiet_diagnostic_only')
 if pcm['near_full_scale_sample_count']>0:flags.append('near_full_scale_pcm_samples_review_true_peak')
 # Do not classify names, numbers or diary terms as actual speech corrections.
 rec=dict(row,source_sha256=source_sha,canonical_text_sha256=row['text_sha256'],recognized_at_utc=stamp(),text=result.get('text',''),segments=segs,words=words,raw_result=result,decode_parameters=PARAMETERS,model='large-v3-turbo',model_revision=prov['revision'],quality_flags=flags,comparison=cmp,pcm_measurements=pcm,probe=probe,loudness_measurement=loudness,decode_completed=True,expected_script_supplied_to_model=False,hotwords_supplied=False,blind_transcription=True,audio_leaves_machine=False,source_files_modified=False,speed_percent=100,voice_identity_human_verified=False,human_listening_verified=False,voice_identity_not_provable_from_asr=True,runtime_seconds=time.monotonic()-started,status='AUTOMATED_TEXT_AND_DECODE_PASS_PENDING_VOICE_LISTEN'if not flags else'REVIEW_REQUIRED')
 save(target,rec);sidecars(rec,target)
 return rec,False

def rollup(rows,selected,completed,errors,missing,scope):
 all_records=[]
 for row in rows:
  p=HERE/'raw_large-v3-turbo/narration'/(row['basename']+'.json')
  if p.exists():
   r=json.loads(p.read_text(encoding='utf-8'))
   all_records.append(dict(episode=r['episode'],sequence=r['sequence'],source_path=r['source_path'],source_sha256=r['source_sha256'],json_path=str(p),text=r['text'],quality_flags=r['quality_flags'],status=r['status'],duration_seconds=r['pcm_measurements']['decoded_duration_seconds']))
 index=dict(updated_at_utc=stamp(),scope='female_EP04_EP05_EP06_only',manifest_sha256=scope['manifest_sha256'],selected_episodes=selected,expected_count=24,recognized_count=len(all_records),current_run_completed=completed,current_run_errors=errors,current_run_pending_missing=missing,files=all_records,blind_transcription=True,expected_script_supplied_to_model=False,source_files_modified=False,browser_operated=False,resolve_connected=False,human_listening_verified=False)
 save(HERE/'index.json',index)
 return index

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--episodes',type=int,nargs='+',choices=ALLOWED_EPISODES,default=list(ALLOWED_EPISODES))
 modes=ap.add_mutually_exclusive_group();modes.add_argument('--prepare',action='store_true');modes.add_argument('--execute',action='store_true')
 args=ap.parse_args();selected=sorted(set(args.episodes))
 m,rows,scope=load_scope()
 if not args.prepare and not args.execute:
  present=[r['basename']for r in rows if Path(r['source_path']).is_file()]
  result=dict(status='SCOPE_VALIDATED_NO_AUDIO_DECODE_NO_ASR',count=24,selected_episodes=selected,currently_present_whitelisted_files=present,source_mapping=str(HERE/'源24段白名单.json'),outputs_only_under=str(HERE))
  save(HERE/'作用域验证.json',result);print(json.dumps(result,ensure_ascii=False));return
 runtime=configure_runtime()
 deps=runtime[-1]
 if args.prepare:
  deps.update(status='DEPENDENCIES_AND_MODEL_HASHES_VERIFIED_NO_ASR',manifest_sha256=scope['manifest_sha256'],whitelisted_files=24,scope_mapping=str(HERE/'源24段白名单.json'),audio_decoded=False,asr_started=False)
  save(HERE/'依赖与作用域验证.json',deps);print(json.dumps(deps,ensure_ascii=False,default=default));return
 deps.update(status='RUNTIME_VALIDATED_FOR_EXECUTION',asr_started=False);save(HERE/'执行环境.json',deps)
 completed=[];errors=[];missing=[]
 for row in rows:
  if row['episode']not in selected:continue
  path=Path(row['source_path'])
  if not path.is_file():missing.append(dict(basename=row['basename'],source_path=str(path)));continue
  try:
   rec,cached=process(row,runtime)
   done=dict(basename=row['basename'],cache_reused_without_asr=cached,status=rec['status'],quality_flags=rec['quality_flags'],json_path=str(HERE/'raw_large-v3-turbo/narration'/(path.stem+'.json')))
   completed.append(done);print(json.dumps(done,ensure_ascii=False),flush=True)
  except Exception as exc:
   err=dict(basename=row['basename'],error=str(exc),traceback=traceback.format_exc());errors.append(err);save(HERE/'errors'/(row['basename']+'.json'),err);print(json.dumps(err,ensure_ascii=False),flush=True)
  rollup(rows,selected,completed,errors,missing,scope)
 result=rollup(rows,selected,completed,errors,missing,scope)
 print(json.dumps(dict(status='EXECUTION_COMPLETE'if not errors else'EXECUTION_HAS_ERRORS',selected_episodes=selected,current_run_completed=len(completed),cache_reused=sum(r['cache_reused_without_asr']for r in completed),current_run_pending_missing=len(missing),current_run_errors=len(errors),recognized_count=result['recognized_count'],index=str(HERE/'index.json')),ensure_ascii=False),flush=True)
 if errors:raise SystemExit(1)

if __name__=='__main__':main()
