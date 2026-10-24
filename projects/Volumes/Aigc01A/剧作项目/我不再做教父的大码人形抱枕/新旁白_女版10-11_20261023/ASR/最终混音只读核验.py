# -*- coding: utf-8 -*-
"""Read-only blind ASR/QC of explicitly whitelisted Resolve EP10/11 renders.

No Resolve/browser/UI, network, source edits, source audio processing or discovery.
Expected script is compared only AFTER recognition; never passed to ASR.
"""
from pathlib import Path
import argparse, datetime as dt, difflib, hashlib, importlib.util, json, math, os, re, subprocess, sys, time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
TASK = HERE.parent
OUT = HERE / '最终混音验收'
RELEASE = TASK / '剪辑准备/冻结发布清单.json'
RELEASE_SHA = '34a4dc24510780ec5d6ed45a746b667958b33b75d292926087f275096ea54a69'
PLAN_SHA = '40cbc08b8e244d122500a048537899757710aff26af8a6e6951a82614d1a23de'
SKILL = Path('/Users/zc/.codex/skills/ffmpeg-skill')
PARAMS = dict(language='en', task='transcribe', temperature=0.0,
              condition_on_previous_text=False, initial_prompt=None,
              word_timestamps=True, fp16=True, verbose=None)

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def save(p, d):
    p = Path(p)
    assert p.resolve().is_relative_to(OUT.resolve())
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + '.tmp')
    tmp.write_text(json.dumps(d, ensure_ascii=False, indent=2,
                            default=lambda x:x.item() if hasattr(x,'item') else str(x)) + '\n', encoding='utf-8')
    tmp.replace(p)

def norm(t):
    aliases = {'mateo':'matteo','mattheo':'matteo','mathew':'matteo','matthew':'matteo',
               'belandi':'bellandi','belandis':'bellandi','seraphina':'serafina',
               'serafina':'serafina'}
    return [aliases.get(x,x) for x in re.findall(r"[a-z]+(?:'[a-z]+)?|\d+", t.lower().replace('’',"'"))]

def scope():
    assert sha(RELEASE) == RELEASE_SHA, 'Frozen release manifest changed'
    r = json.loads(RELEASE.read_text(encoding='utf-8'))
    assert r['plan_sha256'] == PLAN_SHA and sha(r['frozen_plan_path']) == PLAN_SHA
    assert sha(r['adopted_audio_manifest']) == r['adopted_audio_manifest_sha256']
    adopted = json.loads(Path(r['adopted_audio_manifest']).read_text(encoding='utf-8'))
    assert len(adopted['files']) == 13 and all(f['speed_percent'] == 100 for f in adopted['files'])
    maps = {}
    for ep in (10,11):
        art = next(a for a in r['artifacts'] if a['episode'] == ep and a['path'].endswith('词码与原文.json'))
        assert sha(art['path']) == art['sha256']
        m = json.loads(Path(art['path']).read_text(encoding='utf-8'))
        assert m['plan_sha256'] == PLAN_SHA and m['episode'] == ep
        assert sha(m['srt_path']) == m['srt_sha256']
        maps[ep] = m
    return r, maps

def expected_words(m):
    rows = []
    for e in sorted(m['events'], key=lambda e:(e['record_clip_start_seconds'],e['event_id'])):
        for w in e['words']:
            for tok in norm(w['text']):
                rows.append(dict(token=tok, start=w['record_start_seconds'], end=w['record_end_seconds'],
                                 event_id=e['event_id'], kind=e['kind'], speaker=e['speaker'],
                                 canonical_event_text=e['canonical_text']))
    return rows

def measurement(tool, p, dest):
    argv = [sys.executable, str(SKILL/'scripts'/(tool+'.py')), str(p)]
    argv += ['--json'] if tool == 'probe' else ['--measure-only','-I','-18','--tp','-2','--json']
    s = subprocess.run(argv, capture_output=True, text=True, encoding='utf-8', timeout=180)
    assert s.returncode == 0, s.stderr + s.stdout
    d = json.loads(s.stdout); save(dest, dict(argv=argv, result=d, source_modified=False))
    return d

def compare(m, rec):
    exp = expected_words(m)
    obs = [dict(token=t, start=w['start'], end=w['end'], probability=w.get('probability'))
           for w in rec['words'] for t in norm(w['word'])]
    et, ot = [x['token'] for x in exp], [x['token'] for x in obs]
    diffs, matched = [], []
    for op,i,j,k,l in difflib.SequenceMatcher(None, et, ot, autojunk=False).get_opcodes():
        if op == 'equal':
            matched += [dict(expected=exp[a], observed=obs[b], start_delta=obs[b]['start']-exp[a]['start'],
                             end_delta=obs[b]['end']-exp[a]['end']) for a,b in zip(range(i,j),range(k,l))]
        else:
            diffs.append(dict(operation=op, expected=exp[i:j], observed=obs[k:l],
                              expected_context=et[max(0,i-3):min(len(et),j+3)],
                              observed_context=ot[max(0,k-3):min(len(ot),l+3)]))
    ds = sorted(abs(x['start_delta']) for x in matched)
    percentile = lambda f: ds[min(len(ds)-1,round((len(ds)-1)*f))] if ds else None
    cue_checks = []
    for c in m['cues']:
        subset = [x for x in matched if x['expected']['event_id'] == c['event_id']
                  and any(abs(x['expected']['start']-w['record_start_seconds']) < 1e-5
                          and x['expected']['token'] in norm(w['text']) for w in c['word_times'])]
        if subset:
            a,b = min(x['observed']['start'] for x in subset), max(x['observed']['end'] for x in subset)
            cue_checks.append(dict(cue=c['cue_number'], text=c['text'], start=c['start_seconds'],end=c['end_seconds'],
                                  actual_matched_speech_start=a, actual_matched_speech_end=b,
                                  start_difference=a-c['start_seconds'], speech_over_end=b-c['end_seconds'],
                                  boundary_review= a < c['start_seconds']-.25 or b > c['end_seconds']+.25))
        else: cue_checks.append(dict(cue=c['cue_number'],text=c['text'],no_matched_words=True,boundary_review=True))
    event_checks=[]
    for e in m['events']:
        ew = [x for x in exp if x['event_id']==e['event_id']]
        em = [x for x in matched if x['expected']['event_id']==e['event_id']]
        event_checks.append(dict(event_id=e['event_id'],kind=e['kind'],canonical_text=e['canonical_text'],
                                 expected_words=len(ew),matched_words=len(em),all_words_matched=len(ew)==len(em),
                                 max_abs_start_delta=max([abs(x['start_delta']) for x in em]or[0]),
                                 expected_range=[e['record_clip_start_seconds'],e['record_clip_end_seconds']]))
    return dict(expected_count=len(exp),observed_count=len(obs),all_words_exact_after_documented_name_aliases=et==ot,
                difference_count=len(diffs),differences=diffs,matched_word_count=len(matched),
                matched_start_abs_median_seconds=percentile(.5),matched_start_abs_p90_seconds=percentile(.9),
                matched_start_abs_max_seconds=max(ds) if ds else None,
                event_checks=event_checks,cue_checks=cue_checks,
                cue_boundary_review_count=sum(x['boundary_review'] for x in cue_checks),
                expected_text_not_supplied_to_model=True)

def waveform_checks(m, mix, load_audio, sr, np):
    """Correlate each approved new-voice source at original rate with actual mix.

    This is independent of ASR text. A high correlation proves the actual source
    waveform at its original rate survives the native conform, allowing only
    constant volume and up to 180ms of timestamp quantization/decoder priming.
    """
    from scipy.signal import resample_poly
    caches={};checks=[];stride=8;search=.18;work_sr=sr/stride
    mix=resample_poly(mix,1,stride)
    for e in m['events']:
        if e['kind']!='new_narration':continue
        p=Path(e['source_path']);assert sha(p)==e['source_sha256']
        if str(p) not in caches:caches[str(p)]=resample_poly(load_audio(str(p)),1,stride)
        source=caches[str(p)]
        # Avoid judging a rounded edge as a rate mismatch; full word/tail
        # coverage is checked separately against the recognized actual mix.
        sa=e['source_clip_start_seconds'];sb=e['source_clip_end_seconds']
        trim=min(.06,(sb-sa)/10)
        a=round((sa+trim)*work_sr);b=round((sb-trim)*work_sr)
        ref=np.asarray(source[a:b],dtype=np.float64)
        if len(ref)<100:continue
        ref-=ref.mean();ref_energy=float(np.dot(ref,ref))
        target=e['record_clip_start_seconds']+trim
        left=max(0,round((target-search)*work_sr));right=min(len(mix),round((target+(b-a)/work_sr+search)*work_sr))
        window=np.asarray(mix[left:right],dtype=np.float64)
        if len(window)<len(ref) or ref_energy<1e-10:
            checks.append(dict(event_id=e['event_id'],insufficient_signal=True,review_required=True));continue
        dot=np.correlate(window,ref,mode='valid')
        csum=np.r_[0.,np.cumsum(window)];sq=np.r_[0.,np.cumsum(window*window)]
        n=len(ref);energy=sq[n:]-sq[:-n]-(csum[n:]-csum[:-n])**2/n
        corr=dot/np.sqrt(np.maximum(energy*ref_energy,1e-24))
        k=int(np.argmax(corr));coef=float(corr[k]);actual=left/work_sr+k/work_sr
        checks.append(dict(event_id=e['event_id'],source=p.name,source_rate_percent=100,
                           normalized_waveform_correlation=coef,
                           actual_minus_planned_seconds=actual-target,
                           source_comparison_seconds=(b-a)/work_sr,
                           review_required=coef<.72,
                           note='Original-rate waveform correlation, diagnostic not perceptual listening.'))
    return checks

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--prepare',action='store_true');ap.add_argument('--whitelist');ap.add_argument('--whitelist-sha256')
    a=ap.parse_args();release,maps=scope()
    spec=importlib.util.spec_from_file_location('source_qc', HERE/'验收精确白名单.py')
    q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
    rt=q.runtime();engine,load_audio,sr,np,deps=rt
    if a.prepare:
        result=dict(status='PREPARED_WAITING_EXACT_RENDER_FILE_WHITELIST',release_sha256=RELEASE_SHA,
                    plan_sha256=PLAN_SHA,episodes={str(ep):dict(duration=m['proposed_program_duration_seconds'],
                    cues=m['cue_count'],words=len(expected_words(m))) for ep,m in maps.items()},runtime=deps,
                    source_audio_opened=False,ASR_started=False)
        save(OUT/'准备报告.json',result);print(json.dumps(result,ensure_ascii=False));return
    assert a.whitelist and a.whitelist_sha256, 'Require exact explicit whitelist and SHA'
    wp=Path(a.whitelist);assert wp.is_absolute() and wp.resolve().is_relative_to(TASK.resolve())
    assert sha(wp)==a.whitelist_sha256
    blob=wp.read_bytes();wl=json.loads(blob)
    assert wl['plan_sha256']==PLAN_SHA and wl['purpose']=='female_ep10_11_native_final_mix_qc'
    assert 1<=len(wl['files'])<=2 and len({int(x['episode']) for x in wl['files']})==len(wl['files'])
    results=[]
    for row in wl['files']:
        ep=int(row['episode']);assert ep in maps
        p=Path(row['path']);assert p.is_absolute() and not p.is_symlink() and p.resolve().is_relative_to(TASK.resolve())
        assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
        before=p.stat(); assert time.time()-before.st_mtime>1
        d=OUT/f'EP{ep}_{row["sha256"][:12]}';dest=d/'blind_asr.json'
        probe=measurement('probe',p,d/'probe.json');loud=measurement('loudness',p,d/'loudness.json')
        audio=load_audio(str(p));assert np.isfinite(audio).all() and len(audio)>0
        if dest.exists():
            rec=json.loads(dest.read_text(encoding='utf-8'));assert rec['source_sha256']==row['sha256'] and rec['parameters']==PARAMS
        else:
            raw=engine.transcribe(audio,path_or_hf_repo=str(q.MODEL/'weights'),**PARAMS)
            words=[w for s in raw.get('segments',[]) for w in s.get('words',[])]
            rec=dict(source_path=str(p),source_sha256=row['sha256'],source_bytes=row['bytes'],episode=ep,
                     text=raw.get('text',''),words=words,raw_result=raw,parameters=PARAMS,
                     model_revision=q.REVISION,blind_transcription=True,expected_script_supplied_to_model=False,
                     duration=len(audio)/sr,decoded_to_memory_only=True)
            save(dest,rec)
        c=compare(maps[ep],rec);waveforms=waveform_checks(maps[ep],audio,load_audio,sr,np)
        measure=loud.get('measured',{});flags=[]
        if not c['all_words_exact_after_documented_name_aliases']:flags.append('ASR_WORD_DIFFERENCE_REQUIRES_REVIEW')
        if c['matched_start_abs_p90_seconds'] is None or c['matched_start_abs_p90_seconds']>.5:flags.append('ASR_TIMING_DRIFT_REQUIRES_REVIEW')
        if c['cue_boundary_review_count']:flags.append('SUBTITLE_SPEECH_BOUNDARY_REVIEW')
        if abs(rec['duration']-maps[ep]['proposed_program_duration_seconds'])>1/24+.01:flags.append('DURATION_DIFFERS_FROM_NATIVE_PLAN')
        if float(measure.get('input_tp','0'))>=0:flags.append('TRUE_PEAK_AT_OR_ABOVE_ZERO')
        if not (-26<=float(measure.get('input_i','-99'))<=-12):flags.append('MIX_LOUDNESS_REVIEW')
        if any(x['review_required'] for x in waveforms):flags.append('NEW_VOICE_SOURCE_WAVEFORM_RATE_OR_OFFSET_REVIEW')
        assert p.stat().st_size==before.st_size and p.stat().st_mtime_ns==before.st_mtime_ns and sha(p)==row['sha256']
        assert wp.read_bytes()==blob
        result=dict(episode=ep,status='AUTOMATED_MIX_QC_PASS' if not flags else 'REVIEW_REQUIRED',flags=flags,
                    source_path=str(p),source_sha256=row['sha256'],plan_sha256=PLAN_SHA,
                    source_modified=False,resolve_or_ui_operated=False,network_or_audio_upload=False,
                    human_listening_verified=False,lipsync_visual_verified=False,
                    integrated_lufs=measure.get('input_i'),true_peak_dbtp=measure.get('input_tp'),
                    probe=probe,comparison=c,new_narration_waveform_checks=waveforms,blind_asr_path=str(dest))
        save(d/'结果.json',result);results.append(result)
        print(json.dumps({k:result[k] for k in ['episode','status','flags','integrated_lufs','true_peak_dbtp']},ensure_ascii=False),flush=True)
    report=dict(status='BATCH_COMPLETE',plan_sha256=PLAN_SHA,whitelist_sha256=a.whitelist_sha256,
                created_utc=dt.datetime.now(dt.timezone.utc).isoformat(),episodes=results)
    save(OUT/(a.whitelist_sha256[:16]+'_批次报告.json'),report)

if __name__=='__main__':main()
