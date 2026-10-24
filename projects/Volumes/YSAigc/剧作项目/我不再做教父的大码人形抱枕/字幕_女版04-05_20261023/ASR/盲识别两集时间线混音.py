# -*- coding: utf-8 -*-
"""Two explicitfemale timeline-analysis exports only; offlineblindASR.
Default/--prepare validatesexistingdependencies/model butneverdecodesaudio.
--execute requires分析音频白名单.json withexact paths/SHA suppliedbyRoot.
No canonical text, reference script, browser, Resolveor networkcalls.
"""
from pathlib import Path
import argparse,datetime as dt,hashlib,importlib.metadata,json,os,re,shutil,subprocess,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;TASK=HERE.parent;PROJECT=TASK.parent
WHITELIST=HERE/'分析音频白名单.json'
COMPAT=PROJECT/'达芬奇剪辑_EP21-25_20261020/转录/runtime_compatible'
BASE=PROJECT/'配音制作_前3集/制作资料/音频内容与顺序核验_20261018/ASR'
SITE=BASE/'.venv/lib/python3.12/site-packages';MODEL=BASE/'models/large-v3-turbo'
FFBIN=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin')
SKILL=Path('/Users/zc/.codex/skills/ffmpeg-skill')
PARAMETERS=dict(language='en',task='transcribe',temperature=0.0,condition_on_previous_text=False,initial_prompt=None,word_timestamps=True,fp16=True,verbose=None)
REVISION='a4aaeec0636e6fef84abdcbe3544cb2bf7e9f6fb'
EXPECTED_EPISODES={4,5}

def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def safe_output(p):
 p=Path(p);assert p.resolve().is_relative_to(HERE.resolve())and not p.is_symlink(),'Output must be a real task-local file'
 p.parent.mkdir(parents=True,exist_ok=True);return p
def save_text(p,text):
 p=safe_output(p);tmp=safe_output(p.with_name(p.name+'.tmp'));tmp.write_text(text,encoding='utf-8');tmp.replace(p)
def save(p,x):
 save_text(p,json.dumps(x,ensure_ascii=False,indent=2,default=lambda y:y.item()if hasattr(y,'item')else str(y))+'\n')
def runtime():
 assert TASK.name=='字幕_女版04-05_20261023'and HERE.name=='ASR'
 assert sys.version_info[:2]==(3,12)
 sys.path[:0]=[str(COMPAT),str(SITE)]
 for p in(COMPAT,SITE,MODEL):assert p.is_dir(),str(p)
 os.environ['PATH']=str(FFBIN)+os.pathsep+os.environ.get('PATH','')
 os.environ.update(HF_HUB_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',HF_HUB_DISABLE_IMPLICIT_TOKEN='1',PYTHONDONTWRITEBYTECODE='1')
 assert Path(shutil.which('ffmpeg')).resolve()==(FFBIN/'ffmpeg').resolve()
 import mlx.core as mx
 import mlx_whisper
 from mlx_whisper.audio import load_audio,SAMPLE_RATE
 import numpy as np
 assert SAMPLE_RATE==16000
 prov=json.loads((MODEL/'provenance.json').read_text(encoding='utf-8'));assert prov['revision']==REVISION
 checked=[]
 for f in prov['files']:
  p=MODEL/'weights'/f['path'];assert p.is_file()and p.stat().st_size==f['bytes']and digest(p)==f['sha256'];checked.append(dict(path=str(p),bytes=p.stat().st_size,sha256=f['sha256']))
 def version(n):
  try:return importlib.metadata.version(n)
  except importlib.metadata.PackageNotFoundError:return 'imported existingmodule; package metadataunavailable'
 deps=dict(created_at_utc=stamp(),python_executable=sys.executable,python_version=sys.version,mlx_device=str(mx.default_device()),engine='mlx-whisper',engine_version=version('mlx-whisper'),model='large-v3-turbo',model_revision=REVISION,model_files=checked,model_path=str(MODEL/'weights'),offline=True,word_timestamp_clock='Actual exported audio secondsfrom0; timeline absolute mappingis separate.',parameters=PARAMETERS,canonical_or_expected_text_loaded=False,source_audio_modified=False,audio_decode_started=False,ASR_started=False)
 return mlx_whisper,load_audio,SAMPLE_RATE,np,deps

def load_whitelist():
 assert WHITELIST.is_file(),'Root exact exportpath/SHA whitelist hasnotbeen supplied; noaudio scanning isallowed.'
 data=WHITELIST.read_bytes();d=json.loads(data)
 assert d['version']=='female_original'and d['authorization']=='Root supplied actual isolatedtimeline exportpath andSHA'
 assert 1<=len(d['files'])<=2 and {f['episode']for f in d['files']}.issubset(EXPECTED_EPISODES)
 assert len({f['source_path']for f in d['files']})==len(d['files'])
 assert len({f['sha256']for f in d['files']})==len(d['files'])
 for f in d['files']:
  p=Path(f['source_path']);assert p.is_absolute()and p.suffix.lower()in('.wav','.flac','.m4a','.mp3','.mov')
  assert not re.search('男版|性转',str(p))and not re.search('男版|性转',str(p.resolve())),'Never acceptmale/gender-swappedmedia includingresolvedsymlinktarget'
  assert re.fullmatch('[a-f0-9]{64}',f['sha256'])and f['bytes']>0
  assert f['timeline_fps']==30 and f['timeline_start_frame']==0
  assert f['timeline_version']=='isolatedanalysiscopy preserves existingedit/retimes/VO/dialogue'
  assert f['version']=='female_original'
 return d,data

def probe_source(p,ep):
 argv=[sys.executable,str(SKILL/'scripts/probe.py'),str(p),'--json']
 proc=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',timeout=180)
 save(HERE/'measurements'/f'EP{ep:02d}_probe.json',dict(argv=argv,returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr))
 assert proc.returncode==0,f'Probe failed{proc.stderr[-1000:]}'
 return json.loads(proc.stdout)

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--prepare',action='store_true');ap.add_argument('--execute',action='store_true');ap.add_argument('--episodes',nargs='+',type=int,choices=[4,5],default=[4,5]);args=ap.parse_args()
 mlx_whisper,load_audio,sr,np,deps=runtime()
 save(HERE/'准备完成报告.json',dict(status='READY_FOR_EXACT_TWOFILE_WHITELIST_NO_ASR_YET',dependencies=deps,whitelist_expected=str(WHITELIST),no_files_globbed=True,canonical_text_never_loaded=True))
 if not args.execute:
  print(json.dumps(dict(status='PREPARED_NO_AUDIO_OR_ASR',report=str(HERE/'准备完成报告.json'),whitelist_exists=WHITELIST.exists(),model_revision=REVISION),ensure_ascii=False),flush=True);return
 whitelist,data=load_whitelist();outputs=[]
 for f in whitelist['files']:
  if f['episode']not in args.episodes:continue
  ep=f['episode'];source=Path(f['source_path']);assert source.is_file()and source.stat().st_size==f['bytes']and digest(source)==f['sha256'],'Exportmissing/unstable/SHA mismatch'
  before=source.stat();assert before.st_size==f['bytes']
  target=safe_output(HERE/'raw_large-v3-turbo'/f'EP{ep:02d}_timeline_analysis.json')
  if target.exists():
   old=json.loads(target.read_text(encoding='utf-8'))
   assert old['source_sha256']==f['sha256']and old['parameters']==PARAMETERS and old['model_revision']==REVISION and old['blind_transcription']is True,'Cacheidentity differs; do not overwriteor reuse implicitnewsource'
   outputs.append(dict(episode=ep,status='EXACT_SHA_CACHE_REUSED_NO_REPEAT_ASR',path=str(target),sha256=digest(target),text=old['text']));continue
  t0=time.monotonic();probe=probe_source(source,ep)
  audio=load_audio(str(source));a=np.asarray(audio,dtype=np.float32);assert len(a)>0 and  bool(np.isfinite(a).all())
  result=mlx_whisper.transcribe(audio,path_or_hf_repo=str(MODEL/'weights'),**PARAMETERS)
  words=[w for s in result.get('segments',[])for w in s.get('words',[])];dur=len(a)/sr
  flags=[]
  if not words:flags.append('NO_WORD_TIMES')
  if any(float(w.get('probability',1))<.35 for  w in words):flags.append('LOW_WORD_CONFIDENCE_NAVIGATION_ONLY')
  expected=f.get('original_timeline_duration_seconds')
  if expected is not None and abs(dur-expected)>1/30+.001:flags.append('EXPORT_DURATION_DIFFERS_FROM_ORIGINAL_TIMELINE_MORE_THAN1FRAME_VERIFY_MAPPING')
  raw=dict(status='BLIND_ASR_COMPLETE_NO_CANONICAL_ALIGNMENT_YET',episode=ep,version='female_original',source_path=str(source),source_sha256=f['sha256'],source_bytes=f['bytes'],export_metadata=f,recognized_at_utc=stamp(),model='large-v3-turbo',model_revision=REVISION,parameters=PARAMETERS,source_relative_clock='secondsfromactualexportfilestart0',timeline_absolute_word_mapping='unassigned pendingparent exportstart/durationconfirmation; donotapply rawwordtimeas absoluteTC',text=result.get('text',''),segments=result.get('segments',[]),words=words,raw_result=result,decode_completed=True,decoded_mono_sample_rate=sr,decoded_sample_count=len(a),decoded_duration_seconds=dur,pcm_peak_dbfs=float(20*np.log10(max(float(np.max(np.abs(a))),1e-9))),original_timeline_duration_seconds=expected,probe=probe,quality_flags=flags,blind_transcription=True,expected_script_supplied_to_model=False,initial_prompt=None,hotwords=None,canonical_text_loaded=False,canonical_names_punctuation_corrected=False,source_audio_modified=False,human_listening_verified=False,normal_speed_audition_performed=False,network_or_audio_upload=False,ASR_runtime_seconds=time.monotonic()-t0)
  assert source.stat().st_size==before.st_size and source.stat().st_mtime_ns==before.st_mtime_ns and digest(source)==f['sha256'],'Exportchanged duringread'
  assert WHITELIST.read_bytes()==data
  save(target,raw)
  save_text(target.with_suffix('.txt'),raw['text'].strip()+'\n')
  save_text(target.with_suffix('.words.tsv'),'start\tend\tprobability\tword\n'+''.join(f"{w['start']}\t{w['end']}\t{w.get('probability','')}\t{w['word'].strip()}\n"for w in words))
  outputs.append(dict(episode=ep,status=raw['status'],path=str(target),sha256=digest(target),decoded_duration_seconds=dur,words=len(words),quality_flags=flags,text=raw['text']))
  print(json.dumps(outputs[-1],ensure_ascii=False),flush=True)
 save(HERE/'盲识别索引.json',dict(status='REQUESTED_AVAILABLE_EXACT_EXPORTS_COMPLETE',created_at_utc=stamp(),whitelist_file=str(WHITELIST),whitelist_sha256=hashlib.sha256(data).hexdigest(),requested_episodes=args.episodes,outputs=outputs,no_canonical_prompt=True,source_files_modified=False,resolve_or_browser_operated=False))
if __name__=='__main__':main()
