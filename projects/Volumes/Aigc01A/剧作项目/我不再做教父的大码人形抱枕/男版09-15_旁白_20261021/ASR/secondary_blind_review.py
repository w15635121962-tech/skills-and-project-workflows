"""Independent small.en blind pass for ambiguous/non-script and variant sources."""
import importlib.util,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('blind_runtime',HERE/'run_blind_asr.py')
runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
import mlx_whisper
from mlx_whisper.audio import load_audio,SAMPLE_RATE
model_base=runtime.OLD_ASR/'models/small.en';model=model_base/'weights'
provenance=json.loads((model_base/'provenance.json').read_text())
for x in provenance['files']:assert runtime.digest(model/x['path'])==x['sha256']
index=json.loads((HERE/'转录索引.json').read_text())
names={'男版9-7-2.mp4','男版10-9-2.mp4','男版11-5-1.mp4','男版12-1-1.mp4','男版12-1-2.mp4','男版13-4-1.mp4','男版13-4-2.mp4','男版14-1-1.mp4','男版14-1-2.mp4','男版14-8-1.mp4','男版14-8-2.mp4','男版15-3-1.mp4','男版15-3-2.mp4'}
results=[]
for row in index['files']:
 p=Path(row['source_path'])
 if p.name not in names:continue
 target=HERE/'secondary_small.en'/f"EP{row['episode']}"/(p.stem+'.json')
 h=runtime.digest(p);started=time.monotonic()
 if target.exists():
  rec=json.loads(target.read_text());assert rec['source_sha256']==h
 else:
  audio=load_audio(str(p));raw=mlx_whisper.transcribe(audio,path_or_hf_repo=str(model),**runtime.PARAMETERS)
  assert runtime.digest(p)==h
  rec=dict(source_path=str(p),source_sha256=h,episode=row['episode'],kind='video',model='small.en',model_revision=provenance['revision'],decode_parameters=runtime.PARAMETERS,blind_transcription=True,expected_script_supplied_to_model=False,hotwords_supplied=False,source_files_modified=False,text=raw.get('text',''),words=[w for s in raw.get('segments',[]) for w in s.get('words',[])],raw_result=raw,runtime_seconds=time.monotonic()-started)
  runtime.save(target,rec)
 results.append(dict(source_path=str(p),episode=row['episode'],model='small.en',primary_text=row['text'],secondary_text=rec['text'],json_path=str(target)))
 print(json.dumps(results[-1],ensure_ascii=False),flush=True)
runtime.save(HERE/'第二次盲识别索引.json',dict(files=results,source_files_modified=False,human_listening_performed=False,expected_text_supplied=False))
assert len(results)==len(names)
