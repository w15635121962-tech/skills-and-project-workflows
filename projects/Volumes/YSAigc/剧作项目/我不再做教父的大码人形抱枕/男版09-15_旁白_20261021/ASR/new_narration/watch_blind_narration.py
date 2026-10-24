"""Offline incremental narrator recognizer. Expected script is never read here."""
import argparse,importlib.util,json,re,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('blind_runtime',HERE.parent/'run_blind_asr.py')
runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
import mlx_whisper
from mlx_whisper.audio import load_audio,SAMPLE_RATE
TASK=HERE.parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--watch-seconds',type=int,default=0)
parser.add_argument('--wait-for-basename',action='append',default=[],help='Exact audio stem(s) that must be recognized before early completion, including a newly downloaded alternate')
args=parser.parse_args()
model_base=runtime.OLD_ASR/'models/large-v3-turbo';model=model_base/'weights'
provenance=json.loads((model_base/'provenance.json').read_text())
for x in provenance['files']:assert runtime.digest(model/x['path'])==x['sha256']
pattern=re.compile(r'大码男版枕头(09|1[0-5])-(\d{2})-(\d{2})\.mp3')
required_stems=set(args.wait_for_basename)
assert all(pattern.fullmatch(name+'.mp3') for name in required_stems),'Expected a male narration basename, not a path'
meta=dict(engine='mlx-whisper',model='large-v3-turbo',model_revision=provenance['revision'],decode_parameters=runtime.PARAMETERS,expected_text_given_to_recognizer=False,source_text_manifest_read_by_recognizer=False,audio_leaves_machine=False,human_audition=False,source_not_modified=True,generation_requested_speed_percent=100)
started=time.monotonic();stability={};last_status=None
while True:
 candidates=[]
 for ep in range(9,16):
  directory=TASK/'音频'/f'第{ep:02d}集'
  if not directory.exists():continue
  for p in directory.iterdir():
   m=pattern.fullmatch(p.name)
   if m and p.is_file():candidates.append((tuple(map(int,m.groups())),p))
 candidates.sort()
 records=[];errors=[];new=0
 for (ep,seq,take),p in candidates:
  target=HERE/'raw_large-v3-turbo'/f'EP{ep:02d}'/(p.stem+'.json')
  if target.exists():
   raw=json.loads(target.read_text());assert raw['source_sha256']==runtime.digest(p),'Downloaded source changed after ASR'
  else:
   stat=p.stat();key=(stat.st_size,stat.st_mtime_ns)
   if stat.st_size<=0:continue
   old=stability.get(str(p));stability[str(p)]=(key,time.monotonic())
   if old is None or old[0]!=key or time.monotonic()-old[1]<2:continue
   try:
    h=runtime.digest(p);audio=load_audio(str(p));dur=len(audio)/SAMPLE_RATE
    assert dur>0 and bool((abs(audio)>1e-7).any()),'No nonzero audio samples'
    t=time.monotonic();result=mlx_whisper.transcribe(audio,path_or_hf_repo=str(model),**runtime.PARAMETERS)
    assert runtime.digest(p)==h,'Source changed during recognition'
    segments=result.get('segments',[]);words=[w for s in segments for w in s.get('words',[])]
    flags=[]
    if not words:flags.append('no_recognized_words')
    if any(w.get('probability',1)<.6 for w in words):flags.append('low_confidence_word')
    if any(s.get('avg_logprob',0)<-.8 for s in segments):flags.append('low_segment_logprob')
    if any(w['start']<0 or w['end']<w['start'] or w['end']>dur+.1 for w in words):flags.append('word_time_out_of_source_bounds')
    raw=dict(**meta,source_path=str(p),source_sha256=h,episode=ep,narration_sequence=seq,take=take,kind='new_narration',decoded_duration_seconds=dur,decoded_sample_rate=SAMPLE_RATE,recognized_at_utc=runtime.stamp(),text=result.get('text',''),segments=segments,words=words,quality_flags=flags,raw_result=result,runtime_seconds=time.monotonic()-t)
    runtime.save(target,raw);runtime.sidecars(raw,target);new+=1
    print(json.dumps(dict(newly_recognized=p.name,duration=round(dur,3),text=raw['text'],quality_flags=flags),ensure_ascii=False),flush=True)
   except Exception as e:
    errors.append(dict(source_path=str(p),error=repr(e)));continue
  records.append(dict(source_path=str(p),source_sha256=raw['source_sha256'],episode=ep,narration_sequence=seq,take=take,json_path=str(target),word_tsv=str(target.with_suffix('.words.tsv')),segments_srt=str(target.with_suffix('.segments.srt')),decoded_duration_seconds=raw['decoded_duration_seconds'],text=raw['text'],quality_flags=raw['quality_flags']))
 recognized_stems={Path(x['source_path']).stem for x in records}
 requested_pending=sorted(required_stems-recognized_stems)
 index=dict(**meta,updated_at_utc=runtime.stamp(),completed=len(records),errors=errors,files=records,status='watching_downloads' if args.watch_seconds else 'current_files_checked',requested_basenames=sorted(required_stems),requested_pending_basenames=requested_pending)
 runtime.save(HERE/'转录索引.json',index)
 if new or (records and not (HERE/'旁白逐词原文核验.json').exists()):
  subprocess.run([sys.executable,str(HERE/'audit_new_narration.py')],check=True)
  subprocess.run([sys.executable,str(HERE/'measure_new_narration.py')],check=True)
 logical={(x['episode'],x['narration_sequence']) for x in records}
 status=(len(records),len(logical),len(errors))
 if status!=last_status:
  print(json.dumps(dict(recognized_files=len(records),logical_segments=len(logical),errors=errors,watch_seconds_elapsed=round(time.monotonic()-started)),ensure_ascii=False),flush=True);last_status=status
 # A new alternate still needs two stable scans even after all44 logical jobs
 # have an earlier candidate. Requested absent alternates also keep the watch on.
 if (len(logical)>=44 and len(records)==len(candidates) and not requested_pending) or not args.watch_seconds or time.monotonic()-started>=args.watch_seconds:break
 time.sleep(5)
