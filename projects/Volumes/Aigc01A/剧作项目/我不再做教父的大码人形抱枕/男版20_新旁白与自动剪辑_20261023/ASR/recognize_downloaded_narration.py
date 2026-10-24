"""Incremental one-pass local blind ASR for already-downloaded male EP20 MP3s.

No generation/browser/Resolve/network action. Default validates names only.
Run again as new audio arrives; source SHA plus parameters protect the cache.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import re
import time

HERE=Path(__file__).resolve().parent
TASK=HERE.parent
spec=importlib.util.spec_from_file_location('ep20_helpers',HERE/'run_blind_ep20.py')
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--directory',default=str(TASK/'\u97f3\u9891/\u7b2c20\u96c6'))
    ap.add_argument('--execute',action='store_true')
    args=ap.parse_args()
    directory=Path(args.directory).resolve()
    assert directory==TASK/'\u97f3\u9891/\u7b2c20\u96c6', 'Use only this task male EP20 audio directory'
    paths=sorted(directory.glob('*.mp3')) if directory.exists() else []
    pattern=re.compile(r'\u5927\u7801\u7537\u7248\u6795\u593420-(\d{2})-(\d{2})\.mp3')
    assert all(pattern.fullmatch(p.name)for p in paths),'Unexpected audio naming/version in male EP20 directory'
    if not args.execute or not paths:
        print(json.dumps(dict(status='FILES_VALIDATED_NO_ASR'if not args.execute else 'NO_DOWNLOADED_AUDIO_YET',count=len(paths),directory=str(directory)),ensure_ascii=False));return
    old=TASK.parent/'\u7537\u724809-15_\u65c1\u767d_20261021/ASR/run_blind_asr.py'
    spec2=importlib.util.spec_from_file_location('runtime',old);runtime=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(runtime)
    import mlx_whisper
    from mlx_whisper.audio import load_audio,SAMPLE_RATE
    base=runtime.OLD_ASR/'models/large-v3-turbo'
    provenance=json.loads((base/'provenance.json').read_text(encoding='utf-8'))
    for item in provenance['files']:assert helpers.digest(base/'weights'/item['path'])==item['sha256']
    index=dict(episode=20,kind='new_male_narration',model='large-v3-turbo',decode_parameters=helpers.PARAMETERS,
               audio_leaves_machine=False,expected_script_supplied_to_model=False,human_listening_verified=False,files=[],errors=[])
    for path in paths:
        match=pattern.fullmatch(path.name);seq,take=map(int,match.groups())
        target=HERE/'raw_large-v3-turbo'/'narration'/(path.stem+'.json')
        try:
            assert path.stat().st_size>0 and time.time()-path.stat().st_mtime>1.5,'Audio download still empty/changing; retry after completion'
            sha=helpers.digest(path)
            if target.exists():
                rec=json.loads(target.read_text(encoding='utf-8'));assert rec['source_sha256']==sha and rec['decode_parameters']==helpers.PARAMETERS
            else:
                started=time.monotonic();audio=load_audio(str(path));result=mlx_whisper.transcribe(audio,path_or_hf_repo=str(base/'weights'),**helpers.PARAMETERS)
                assert helpers.digest(path)==sha,'Audio changed during recognition'
                segments=result.get('segments',[]);words=[w for s in segments for w in s.get('words',[])]
                flags=[]
                if not words:flags.append('no_recognized_words')
                if any(w.get('probability',1)<.6 for w in words):flags.append('low_confidence_word')
                if any(s.get('compression_ratio',0)>2.4 for s in segments):flags.append('possible_repetition_hallucination')
                rec=dict(episode=20,narration_sequence=seq,take=take,source_path=str(path),source_sha256=sha,
                    decoded_duration_seconds=len(audio)/SAMPLE_RATE,text=result.get('text',''),segments=segments,words=words,
                    quality_flags=flags,raw_result=result,decode_parameters=helpers.PARAMETERS,
                    model='large-v3-turbo',model_revision=provenance['revision'],expected_script_supplied_to_model=False,
                    human_listening_verified=False,runtime_seconds=time.monotonic()-started)
                helpers.save(target,rec)
            runtime.sidecars(rec,target)
            index['files'].append(dict(source_path=str(path),source_sha256=sha,sequence=seq,take=take,json_path=str(target),
                                       text=rec['text'],duration_seconds=rec['decoded_duration_seconds'],quality_flags=rec['quality_flags']))
            print(json.dumps(index['files'][-1],ensure_ascii=False),flush=True)
        except Exception as exc:
            index['errors'].append(dict(source_path=str(path),error=str(exc)))
        helpers.save(HERE/'narration_index.json',index)
    if index['errors']:raise SystemExit(1)

if __name__=='__main__':main()
