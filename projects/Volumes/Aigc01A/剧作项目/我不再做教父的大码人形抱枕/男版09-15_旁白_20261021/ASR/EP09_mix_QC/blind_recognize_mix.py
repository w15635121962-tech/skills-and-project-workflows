"""Blind offline recognition of the rendered mix; no source text or plan read."""
import importlib.util,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('blind_runtime',HERE.parent/'run_blind_asr.py')
runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
import mlx_whisper
from mlx_whisper.audio import load_audio,SAMPLE_RATE
p=HERE/'EP09_按计划原始增益_通道幅度保持_完整音频mix.wav'
target=HERE/'EP09_完整mix_盲识别.json';assert not target.exists()
model_base=runtime.OLD_ASR/'models/large-v3-turbo';model=model_base/'weights'
provenance=json.loads((model_base/'provenance.json').read_text())
for x in provenance['files']:assert runtime.digest(model/x['path'])==x['sha256']
h=runtime.digest(p);audio=load_audio(str(p));started=time.monotonic()
raw=mlx_whisper.transcribe(audio,path_or_hf_repo=str(model),**runtime.PARAMETERS)
assert runtime.digest(p)==h
record=dict(source_path=str(p),source_sha256=h,decoded_duration_seconds=len(audio)/SAMPLE_RATE,model='large-v3-turbo',decode_parameters=runtime.PARAMETERS,expected_text_or_plan_supplied_to_recognizer=False,audio_leaves_machine=False,source_unchanged=True,text=raw.get('text',''),segments=raw.get('segments',[]),words=[w for s in raw.get('segments',[]) for w in s.get('words',[])],raw_result=raw,runtime_seconds=time.monotonic()-started)
runtime.save(target,record);runtime.sidecars(record,target)
print(json.dumps(dict(path=str(target),duration=record['decoded_duration_seconds'],text=record['text']),ensure_ascii=False),flush=True)
