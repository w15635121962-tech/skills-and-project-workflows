# -*- coding: utf-8 -*-
"""Offline female EP10/11 narration QC, gated by an explicit batch whitelist.

--prepare validates text scope, runtime and cached model provenance only.
--execute requires --whitelist ABSOLUTE_JSON --whitelist-sha256 EXACT_SHA.
No directory audio discovery, browser, Resolve, network, audio rewrite or TTS.
Expected words are compared after blind recognition, never supplied to the model.
"""
from pathlib import Path
import argparse,csv,datetime as dt,difflib,hashlib,importlib.metadata,json,math,os,re,shutil,subprocess,sys,time,traceback
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
TASK=HERE.parent
PROJECT=TASK.parent
MANIFEST=TASK/'准备/manifest.json'
MANIFEST_SHA='bb46836fac7f1f325a431c4705dab336ccee79fa5a15dddf4ab5e1a972b4c6fe'
SKILL=Path('/Users/zc/.codex/skills/ffmpeg-skill')
FFBIN=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin')
BASE=PROJECT/'配音制作_前3集/制作资料/音频内容与顺序核验_20261018/ASR'
SITE=BASE/'.venv/lib/python3.12/site-packages'
COMPAT=PROJECT/'达芬奇剪辑_EP21-25_20261020/转录/runtime_compatible'
MODEL=BASE/'models/large-v3-turbo'
REVISION='a4aaeec0636e6fef84abdcbe3544cb2bf7e9f6fb'
VOICE='对标女旁白_测试A_1020'
COUNTS={10:6,11:7}
PARAMETERS=dict(language='en',task='transcribe',temperature=0.0,condition_on_previous_text=False,initial_prompt=None,word_timestamps=True,fp16=True,verbose=None)
PATTERN=re.compile(r'^大码女版枕头(10|11)-(\d{2})-(\d{2})\.mp3$')

def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def safe_output(p):
    p=Path(p)
    assert p.resolve().is_relative_to(HERE.resolve()) and not p.is_symlink(),'Output escapes task ASR or is a symlink'
    p.parent.mkdir(parents=True,exist_ok=True)
    assert p.parent.resolve().is_relative_to(HERE.resolve()),'Output parent escapes task ASR'
    return p
def text_output(p,text):
    p=safe_output(p);tmp=safe_output(p.with_name(p.name+'.tmp'))
    tmp.write_text(text,encoding='utf-8');tmp.replace(p)
def save(p,value):
    text_output(p,json.dumps(value,ensure_ascii=False,indent=2,default=lambda x:x.item()if hasattr(x,'item')else str(x))+'\n')
def scope():
    assert TASK.name=='新旁白_女版10-11_20261023' and HERE.name=='ASR'
    assert digest(MANIFEST)==MANIFEST_SHA,'Approved manifest changed; require explicit review'
    m=json.loads(MANIFEST.read_text(encoding='utf-8'))
    assert m['version']=='女版' and m['scope_episode_order']==[10,11]
    assert m['voice']==VOICE and m['model']=='Seed TTS' and m['mode']=='文本朗读' and m['speed_percent']==100
    assert digest(m['source_docx'])==m['source_docx_sha256'],'Original DOCX changed'
    rows={}
    for ep,count in COUNTS.items():
        gs=[g for g in m['groups'] if g['episode']==ep]
        assert len(gs)==count
        for seq,g in enumerate(gs,1):
            assert g['narration_sequence']==seq and g['take']==1
            assert g['basename']==f'大码女版枕头{ep:02d}-{seq:02d}-01'
            assert g['voice']==VOICE and g['speed_percent']==100 and g['characters']<=200
            tp=Path(g['text_file'])
            assert tp.resolve().is_relative_to((TASK/'准备/分段').resolve())
            assert tp.read_text(encoding='utf-8')==g['generation_text'] and digest(tp)==g['generation_text_sha256']
            rows[(ep,seq)]=g
    assert len(rows)==len(m['groups'])==13
    return m,rows
def runtime():
    assert sys.version_info[:2]==(3,12),'Use the existing verified Python 3.12 runtime'
    for p in [COMPAT,SITE,MODEL]:assert p.is_dir(),str(p)
    sys.path[:0]=[str(COMPAT),str(SITE)]
    os.environ['PATH']=str(FFBIN)+os.pathsep+os.environ.get('PATH','')
    os.environ.update(HF_HUB_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',HF_HUB_DISABLE_IMPLICIT_TOKEN='1',PYTHONDONTWRITEBYTECODE='1')
    assert Path(shutil.which('ffmpeg')).resolve()==(FFBIN/'ffmpeg').resolve()
    assert Path(shutil.which('ffprobe')).resolve()==(FFBIN/'ffprobe').resolve()
    import mlx.core as mx
    import mlx_whisper
    from mlx_whisper.audio import load_audio,SAMPLE_RATE
    import numpy as np
    assert SAMPLE_RATE==16000
    prov=json.loads((MODEL/'provenance.json').read_text(encoding='utf-8'));assert prov['revision']==REVISION
    checked=[]
    for f in prov['files']:
        p=MODEL/'weights'/f['path']
        assert p.is_file() and p.stat().st_size==f['bytes'] and digest(p)==f['sha256'],'Cached model provenance mismatch'
        checked.append(dict(path=str(p),bytes=p.stat().st_size,sha256=f['sha256']))
    deps=dict(validated_at_utc=stamp(),python_executable=sys.executable,python_version=sys.version,mlx_device=str(mx.default_device()),engine='mlx-whisper',engine_module=mlx_whisper.__file__,model='large-v3-turbo',model_revision=REVISION,model_files=checked,model_path=str(MODEL/'weights'),offline=True,decode_parameters=PARAMETERS,audio_decoded=False,ASR_started=False)
    return mlx_whisper,load_audio,SAMPLE_RATE,np,deps
def whitelist(path,expected_sha,rows):
    path=Path(path)
    assert path.is_absolute() and path.resolve().is_relative_to(TASK.resolve()),'Whitelist must be an explicit task-local absolute path'
    assert re.fullmatch(r'[a-f0-9]{64}',expected_sha or ''),'Exact batch whitelist SHA is required'
    data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==expected_sha,'Whitelist SHA differs from supplied authorization'
    d=json.loads(data)
    assert d['version']=='female_new_narration'
    assert Path(d['manifest_path']).resolve()==MANIFEST.resolve() and d['manifest_sha256']==MANIFEST_SHA
    assert isinstance(d['files'],list) and 1<=len(d['files'])<=26
    selected=[];keys=set();paths=set();hashes=set()
    for f in d['files']:
        ep=int(f['episode']);seq=int(f.get('narration_sequence',f.get('sequence',0)));take=int(f['take']);key=(ep,seq,take)
        assert (ep,seq) in rows and take>=1 and key not in keys,'Unexpected or duplicate episode/sequence/take'
        p=Path(f['source_path']);mat=PATTERN.fullmatch(p.name)
        assert mat and (int(mat[1]),int(mat[2]),int(mat[3]))==key
        assert p.is_absolute() and not p.is_symlink() and p.resolve().is_relative_to(TASK.resolve())
        assert any(p.resolve().is_relative_to((TASK/x).resolve()) for x in ['音频','备选版本','交付音频']),'Audio must be inside this new female task'
        assert not re.search(r'男版|性转',str(p)) and not re.search(r'男版|性转',str(p.resolve()))
        assert re.fullmatch(r'[a-f0-9]{64}',f['sha256']) and int(f['bytes'])>0
        assert str(p) not in paths and f['sha256'] not in hashes,'Duplicate path or audio SHA in batch'
        g=rows[(ep,seq)]
        selected.append(dict(episode=ep,sequence=seq,take=take,source_path=str(p),source_sha256=f['sha256'],expected_bytes=int(f['bytes']),canonical_text=g['generation_text'],canonical_text_sha256=g['generation_text_sha256'],source_docx_paragraphs=g['source_docx_paragraphs']))
        keys.add(key);paths.add(str(p));hashes.add(f['sha256'])
    return d,data,selected
def run_skill(tool,path):
    assert tool in ['probe','loudness']
    argv=[sys.executable,str(SKILL/'scripts'/(tool+'.py')),str(path)]
    argv+=['--json'] if tool=='probe' else ['--measure-only','-I','-18','--tp','-2','--json']
    r=subprocess.run(argv,capture_output=True,text=True,encoding='utf-8',timeout=180,env=dict(os.environ))
    save(HERE/'measurements'/(path.stem+'_'+tool+'.json'),dict(argv=argv,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,source_audio_modified=False))
    assert r.returncode==0,f'{tool} measurement failed: {r.stderr[-1000:]} {r.stdout[-1000:]}'
    return json.loads(r.stdout)
def normalize(text,aliases=False):
    tokens=re.findall(r"[a-z]+(?:'[a-z]+)?|\d+",text.lower().replace('’',"'"))
    aliases_map={'mateo':'matteo','mattheo':'matteo','mattew':'matteo','matthew':'matteo','belandi':'bellandi','belandis':'bellandi','seraphina':'serafina'}
    return [aliases_map.get(t,t) for t in tokens] if aliases else tokens
def compare(expected,observed,words):
    exp=normalize(expected);obs=normalize(observed);expanded=[]
    for w in words:
        expanded += [dict(token=t,start=w['start'],end=w['end']) for t in normalize(w['word'])]
    differences=[]
    for tag,i,j,k,l in difflib.SequenceMatcher(None,exp,obs,autojunk=False).get_opcodes():
        if tag=='equal':continue
        differences.append(dict(kind=tag,expected_token_range=[i,j],observed_token_range=[k,l],expected_tokens=exp[i:j],observed_tokens=obs[k:l],observed_times=expanded[k:l],ordinary_word_review_required=normalize(' '.join(exp[i:j]),True)!=normalize(' '.join(obs[k:l]),True)))
    return dict(strict_word_sequence_equal=exp==obs,word_sequence_equal_with_documented_name_aliases=normalize(expected,True)==normalize(observed,True),differences=differences,expected_word_count=len(exp),observed_word_count=len(obs),first_expected_tokens=exp[:6],first_observed_tokens=obs[:6],last_expected_tokens=exp[-6:],last_observed_tokens=obs[-6:],post_recognition_only=True,proper_name_aliases_are_diagnostic_not_voice_or_pronunciation_proof=True)
def pcm_stats(audio,sr,np):
    a=np.asarray(audio,dtype=np.float32);assert len(a)>0 and bool(np.isfinite(a).all()),'Empty/nonfinite PCM'
    win=round(sr*.01);n=len(a)//win
    rms=np.sqrt(np.mean(a[:n*win].reshape(n,win)**2,axis=1)) if n else np.array([])
    act=np.flatnonzero(rms>10**(-45/20));peak=float(np.max(np.abs(a)))
    return dict(decoded_sample_count=len(a),decoded_sample_rate=sr,decoded_duration_seconds=len(a)/sr,decoded_mono=True,pcm_peak_dbfs=20*math.log10(max(peak,1e-12)),near_full_scale_samples=int(np.count_nonzero(np.abs(a)>=.9999)),leading_below_minus45db_rms_seconds=round(float(act[0])*.01,4)if len(act)else len(a)/sr,trailing_below_minus45db_rms_seconds=round((n-1-float(act[-1]))*.01,4)if len(act)else len(a)/sr,all_quiet=not len(act),quiet_threshold_dbfs=-45,quiet_window_seconds=.01,pcm_note='Mono16k decoder PCM for speech/tail diagnostics; source true peak measured separately with loudness.py; no trimming or source processing.')
def process(row,rt,batch_path,batch_bytes,batch_sha):
    engine,load_audio,sr,np,deps=rt;p=Path(row['source_path'])
    assert p.is_file() and p.stat().st_size==row['expected_bytes'] and digest(p)==row['source_sha256'],'Source missing, different, incomplete or not the authorized exact SHA'
    before=p.stat();assert time.time()-before.st_mtime>1.5,'File too recent; wait for stable download'
    target=safe_output(HERE/'raw_large-v3-turbo/narration'/(p.stem+'.json'))
    if target.exists():
        old=json.loads(target.read_text(encoding='utf-8'))
        assert old['source_sha256']==row['source_sha256'] and old['canonical_text_sha256']==row['canonical_text_sha256'] and old['parameters']==PARAMETERS and old['model_revision']==REVISION,'Existing cache differs; never overwrite/reuse another take or source'
        return old,True
    t0=time.monotonic();probe=run_skill('probe',p);loudness=run_skill('loudness',p)
    # Existing offline speech library fully decodes the single audio stream to memory.
    # No intermediate audio file, normalisation, speed or pitch processing is applied.
    assert len(probe.get('audio_streams',[]))==1 and probe.get('video') is None,'Require narration-only, single-audio-stream source'
    audio=load_audio(str(p));pcm=pcm_stats(audio,sr,np);assert not pcm['all_quiet'],'Entirely quiet source'
    result=engine.transcribe(audio,path_or_hf_repo=str(MODEL/'weights'),**PARAMETERS)
    segs=result.get('segments',[]);words=[w for s in segs for w in s.get('words',[])]
    cmp=compare(row['canonical_text'],result.get('text',''),words);flags=[]
    measured=loudness.get('measured',{})
    source_tp=float(measured['input_tp'])
    source_lufs=float(measured['input_i'])
    if not words:flags.append('NO_WORDS')
    if not cmp['strict_word_sequence_equal']:flags.append('TEXT_DIFFERENCE_REVIEW_REQUIRED')
    if any(x['ordinary_word_review_required'] for x in cmp['differences']):flags.append('ORDINARY_WORD_OMISSION_REPEAT_OR_PRONUNCIATION_SUSPECT_NOT_AUTO_CORRECTED')
    if any(w.get('probability',1)<.6 for w in words):flags.append('LOW_WORD_CONFIDENCE')
    if any(s.get('compression_ratio',0)>2.4 or s.get('no_speech_prob',0)>.5 for s in segs):flags.append('POSSIBLE_ASR_HALLUCINATION_OR_REPETITION')
    if any(w['end']<=w['start'] or w['start']<0 or w['end']>pcm['decoded_duration_seconds']+.1 for w in words):flags.append('WORD_TIMING_ANOMALY')
    if pcm['near_full_scale_samples']:flags.append('NEAR_FULL_SCALE_PCM_REVIEW_SOURCE_TRUE_PEAK')
    if source_tp>=0:flags.append('SOURCE_TRUE_PEAK_AT_OR_ABOVE_ZERO_DBTP_REVIEW')
    elif source_tp>-.3:flags.append('SOURCE_TRUE_PEAK_LESS_THAN_0_3DB_HEADROOM')
    if pcm['leading_below_minus45db_rms_seconds']>.8:flags.append('LONG_LEADING_QUIET_DIAGNOSTIC_ONLY')
    if pcm['trailing_below_minus45db_rms_seconds']>1.2:flags.append('LONG_TRAILING_QUIET_DIAGNOSTIC_ONLY')
    if words and pcm['decoded_duration_seconds']-words[-1]['end']<.025:flags.append('LAST_WORD_NEAR_FILE_EDGE_REVIEW_TAIL_NOT_PROOF_OF_CUTOFF')
    assert p.stat().st_size==before.st_size and p.stat().st_mtime_ns==before.st_mtime_ns and digest(p)==row['source_sha256'],'Source changed during analysis'
    assert Path(batch_path).read_bytes()==batch_bytes,'Authorized whitelist changed during batch'
    rec=dict(row,status='AUTOMATED_DECODE_TEXT_PASS_PENDING_VOICE_LISTEN'if not flags else'REVIEW_REQUIRED',recognized_at_utc=stamp(),batch_whitelist=str(batch_path),batch_whitelist_sha256=batch_sha,manifest_sha256=MANIFEST_SHA,model='large-v3-turbo',model_revision=REVISION,parameters=PARAMETERS,expected_script_supplied_to_model=False,initial_prompt=None,hotwords=None,blind_transcription=True,text=result.get('text',''),segments=segs,words=words,raw_result=result,comparison=cmp,quality_flags=flags,probe=probe,loudness_measurement=loudness,source_true_peak_dbtp=source_tp,source_integrated_lufs=source_lufs,pcm_measurements=pcm,decode_completed=True,source_audio_modified=False,network_or_audio_upload=False,browser_or_Resolve_operated=False,speed_processing_applied=False,voice_identity_provable_by_asr=False,human_listening_verified=False,ASR_runtime_seconds=time.monotonic()-t0)
    save(target,rec);text_output(target.with_suffix('.txt'),rec['text'].strip()+'\n')
    lines=['word_index\tstart\tend\tprobability\tword']+[f"{i}\t{w['start']}\t{w['end']}\t{w.get('probability','')}\t{w['word'].strip()}" for i,w in enumerate(words)]
    text_output(target.with_suffix('.words.tsv'),'\n'.join(lines)+'\n')
    return rec,False
def main():
    ap=argparse.ArgumentParser(description=__doc__);modes=ap.add_mutually_exclusive_group();modes.add_argument('--prepare',action='store_true');modes.add_argument('--execute',action='store_true')
    ap.add_argument('--whitelist');ap.add_argument('--whitelist-sha256');args=ap.parse_args();manifest,rows=scope()
    if not args.prepare and not args.execute:
        print(json.dumps(dict(status='TEXT_SCOPE_ONLY_NO_AUDIO',segments=len(rows),manifest_sha256=MANIFEST_SHA),ensure_ascii=False));return
    rt=runtime()
    if args.prepare:
        report=dict(status='PREPARED_WAITING_EXPLICIT_FILE_SHA_WHITELIST',manifest_path=str(MANIFEST),manifest_sha256=MANIFEST_SHA,expected_segments=len(rows),scope_episodes=[10,11],dependencies=rt[-1],source_audio_opened=False,ASR_started=False)
        save(HERE/'准备完成报告.json',report);print(json.dumps(report,ensure_ascii=False));return
    assert args.whitelist and args.whitelist_sha256,'No recognition without an explicitly supplied batch path and SHA'
    d,data,selected=whitelist(args.whitelist,args.whitelist_sha256,rows);done=[];errors=[]
    for row in selected:
        try:
            rec,cached=process(row,rt,args.whitelist,data,args.whitelist_sha256)
            item=dict(episode=row['episode'],sequence=row['sequence'],take=row['take'],source_path=row['source_path'],source_sha256=row['source_sha256'],status=rec['status'],flags=rec['quality_flags'],cache_reused=cached,json_path=str(HERE/'raw_large-v3-turbo/narration'/(Path(row['source_path']).stem+'.json')),duration_seconds=rec['pcm_measurements']['decoded_duration_seconds'],comparison=rec['comparison'])
            done.append(item);print(json.dumps(item,ensure_ascii=False),flush=True)
        except Exception as exc:
            err=dict(source_path=row['source_path'],error=str(exc),traceback=traceback.format_exc());errors.append(err);save(HERE/'errors'/(Path(row['source_path']).stem+'.json'),err);print(json.dumps(err,ensure_ascii=False),flush=True)
    report=dict(status='BATCH_COMPLETE'if not errors else'BATCH_HAS_ERRORS',created_at_utc=stamp(),batch_whitelist=args.whitelist,batch_whitelist_sha256=args.whitelist_sha256,manifest_sha256=MANIFEST_SHA,completed=done,errors=errors,files_modified=False,blind_transcription=True,expected_script_supplied_to_model=False,human_listening_verified=False)
    out=HERE/'批次验收'/(args.whitelist_sha256[:16]+'.json');save(out,report)
    print(json.dumps(dict(status=report['status'],completed=len(done),errors=len(errors),report=str(out)),ensure_ascii=False),flush=True)
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
