"""Blind local recognition of EP10/11 rendered audio; no script/plan input."""
import importlib.util,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('blind_runtime',HERE/'run_blind_asr.py')
runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
import mlx_whisper
from mlx_whisper.audio import load_audio,SAMPLE_RATE
model_base=runtime.OLD_ASR/'models/large-v3-turbo';model=model_base/'weights'
provenance=json.loads((model_base/'provenance.json').read_text())
for x in provenance['files']:assert runtime.digest(model/x['path'])==x['sha256']
results=[]
for ep in [10,11]:
 folder=HERE/f'EP{ep:02d}_mix_QC';p=folder/f'EP{ep:02d}_按计划原始增益_通道幅度保持_完整音频mix.wav'
 target=folder/f'EP{ep:02d}_完整mix_盲识别.json';h=runtime.digest(p)
 if target.exists():
  record=json.loads(target.read_text());assert record['source_sha256']==h
 else:
  audio=load_audio(str(p));started=time.monotonic();raw=mlx_whisper.transcribe(audio,path_or_hf_repo=str(model),**runtime.PARAMETERS)
  assert runtime.digest(p)==h
  record=dict(source_path=str(p),source_sha256=h,episode=ep,decoded_duration_seconds=len(audio)/SAMPLE_RATE,model='large-v3-turbo',decode_parameters=runtime.PARAMETERS,expected_text_or_plan_supplied_to_recognizer=False,audio_leaves_machine=False,source_unchanged=True,text=raw.get('text',''),segments=raw.get('segments',[]),words=[w for s in raw.get('segments',[]) for w in s.get('words',[])],raw_result=raw,runtime_seconds=time.monotonic()-started)
  runtime.save(target,record);runtime.sidecars(record,target)
 results.append(dict(episode=ep,path=str(target),text=record['text'],duration=record['decoded_duration_seconds']))
 print(json.dumps(results[-1],ensure_ascii=False),flush=True)
runtime.save(HERE/'EP10-11_mix_QC_盲识别索引.json',dict(results=results,expected_text_supplied=False,source_files_modified=False,human_audition=False))
