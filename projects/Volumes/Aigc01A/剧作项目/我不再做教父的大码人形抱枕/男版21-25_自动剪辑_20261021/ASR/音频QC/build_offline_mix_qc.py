from pathlib import Path
from collections import defaultdict
import datetime,hashlib,json,math,re,subprocess
import numpy as np

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
MANIFEST=OUT.parent.parent/'Resolve_组装实读.json'
FF=Path('/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg')
RATE=24000

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def db(v):return float(20*np.log10(max(float(v),1e-12)))
def metric(a):
    peak=float(np.max(np.abs(a))) if a.size else 0
    return dict(peak_linear=peak,peak_dbfs=db(peak),rms_dbfs=db(np.sqrt(np.mean(a**2))) if a.size else -240,
                samples_at_or_above_full_scale=int(np.count_nonzero(np.abs(a)>=1)),
                channel_peak_dbfs=[db(np.max(np.abs(a[:,n]))) for n in range(2)] if a.size else [-240,-240])
def wav(p,a):
    cp=subprocess.run([str(FF),'-nostdin','-v','error','-f','f32le','-ar',str(RATE),'-ac','2','-i','pipe:0','-c:a','pcm_f32le','-y',str(p)],input=a.astype('<f4').tobytes(),capture_output=True)
    if cp.returncode:raise RuntimeError(cp.stderr.decode()[-1000:])
def ebur(p):
    cp=subprocess.run([str(FF),'-nostdin','-hide_banner','-nostats','-i',str(p),'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True)
    log=cp.stderr;p.with_suffix('.ebur128.log').write_text(log)
    def last(pattern):
        a=re.findall(pattern,log,re.M)
        return float(a[-1]) if a and a[-1] not in ('-inf','inf','nan') else None
    return dict(integrated_loudness_lufs=last(r'^\s*I:\s*([-+\d.inf]+)\s*LUFS'),loudness_range_lu=last(r'^\s*LRA:\s*([-+\d.inf]+)\s*LU'),true_peak_dbfs=last(r'^\s*Peak:\s*([-+\d.inf]+)\s*dBFS'))

raw=MANIFEST.read_bytes();manifest_sha=hashlib.sha256(raw).hexdigest();j=json.loads(raw)
all_sources=json.loads((BASE/'转录索引.json').read_text())['files']
source_meta={r['source_path']:r for r in all_sources}
inventory=json.loads((BASE.parent/'男版素材盘点.json').read_text())
channels={r['path']:int(r['audio_streams'][0]['channels']) for ep in inventory['episodes'] for k in ('videos','narration_audio') for r in ep[k]}
cache={}
def decode(p):
    if p in cache:return cache[p]
    meta=source_meta[p]
    if sha(p)!=meta['source_sha256']:raise RuntimeError('Source hash differs from ASR inventory '+p)
    ch=channels[p]
    cp=subprocess.run([str(FF),'-nostdin','-v','error','-i',p,'-vn','-ac',str(ch),'-ar',str(RATE),'-f','f32le','pipe:1'],capture_output=True,check=True)
    a=np.frombuffer(cp.stdout,dtype='<f4').reshape((-1,ch)).copy()
    if ch==1:a=np.repeat(a,2,axis=1)
    if ch!=1 and ch!=2:raise RuntimeError('Unsupported channel layout')
    cache[p]=a
    return a

history_path=OUT/'offline_mix_qc.json'
history=json.loads(history_path.read_text()) if history_path.exists() else dict(episodes=[])
history_by={e['episode']:e for e in history['episodes']}
reports=[]
for ep in j['episodes']:
    e=ep['episode'];fps=float(ep['fps']);frames=int(ep['duration_frames']);n=round(frames*RATE/fps)
    # Parent requested episodes as soon as they appear in the native readback.
    track={k:np.zeros((n,2),np.float64) for k in ('sync_audio','narration')}
    clip_rows=[];shortages=[];sync_offsets=[]
    for kind in ('sync_audio','narration'):
        for r in ep[kind]:
            if not r.get('enabled',True):continue
            dur_frames=int(r['end'])-int(r['start'])
            assert dur_frames>=0
            take_n=round(dur_frames*RATE/fps)
            source_seconds=float(r['source_start'])/fps
            at=round(float(r['start'])*RATE/fps)
            src_at=round(source_seconds*RATE)
            a=decode(r['path'])
            part=a[src_at:src_at+take_n]
            missing=take_n-len(part)
            if missing:
                part=np.pad(part,((0,missing),(0,0)))
                shortages.append(dict(kind=kind,id=r['id'],source=r['path'],missing_samples=missing,missing_seconds=missing/RATE,note='native clip length exceeds decoded available source; zero pad after actual source end, no speech removed'))
            gain=float(r['gain_db']);amp=10**(gain/20)
            if at+take_n>n:raise RuntimeError(f'EP{e} clip extends beyond native duration')
            track[kind][at:at+take_n]+=part.astype(np.float64)*amp
            clip_rows.append(dict(kind=kind,id=r['id'],path=r['path'],source_start_frame=r['source_start'],source_start_seconds=source_seconds,
                                  native_record_start_frame=r['start'],native_record_end_frame_exclusive=r['end'],native_length_frames=dur_frames,
                                  rendered_samples=take_n,gain_db=gain,enabled=True,source_shortage_samples=missing))
    # No normalization/limiting/fades are added. Float WAV keeps any overs intact.
    mix=track['sync_audio']+track['narration']
    paths={}
    for k,a in [('sync_audio',track['sync_audio']),('narration',track['narration']),('mix',mix)]:
        p=OUT/f'EP{e}_{k}_24k_stereo_float.wav';wav(p,a);paths[k]=str(p)
    native_sync=ep['sync_audio'];native_video=ep['video']
    av_pairs=[]
    for a,v in zip(native_sync,native_video):
        okay=(a['path']==v['path'] and a['start']==v['start'] and a['end']==v['end'] and a['source_start']==v['source_start'])
        av_pairs.append(okay)
        if not okay:sync_offsets.append(dict(audio=a,video=v))
    report=dict(episode=e,timeline=ep['timeline'],timeline_id=ep['id'],input_manifest_sha256=manifest_sha,
                native_duration_frames=frames,fps=fps,duration_seconds=frames/fps,output_sample_rate=RATE,channels=2,total_samples=n,
                enabled_sync_clips=sum(r.get('enabled',True) for r in ep['sync_audio']),enabled_narration_clips=sum(r.get('enabled',True) for r in ep['narration']),
                mono_to_stereo_model='mono duplicated equally to L/R with no extra pan-law attenuation; conservative peak model',
                no_track_or_bus_effects_simulated=True,no_automatic_gain_or_limiter=True,native_gain_values_applied=True,
                length_basis='exact (row.end-row.start)/fps; GetSourceEndFrame ignored for length',
                source_start_basis='row.source_start/fps, never planned src0 or source_end-derived length',
                paths=paths,metrics={k:metric(a) for k,a in [('sync_audio',track['sync_audio']),('narration',track['narration']),('mix',mix)]},
                ebur128=ebur(Path(paths['mix'])),native_audio_video_rows_one_to_one_equal=(len(native_sync)==len(native_video) and all(av_pairs)),
                av_mismatch_details=sync_offsets,source_end_padding=shortages,clip_rows=clip_rows,
                human_listening_validated=False,quality_status='offline automatic reconstruction and level QC only; not a Resolve bus render or actual audition')
    history_by[e]=report;reports.append(report)
    print(json.dumps(dict(episode=e,duration_seconds=report['duration_seconds'],mix_peak_dbfs=report['metrics']['mix']['peak_dbfs'],clipping_samples=report['metrics']['mix']['samples_at_or_above_full_scale'],integrated_loudness_lufs=report['ebur128']['integrated_loudness_lufs'],source_pad_clips=len(shortages),native_av_match=report['native_audio_video_rows_one_to_one_equal']),ensure_ascii=False),flush=True)

result=dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),input_manifest=str(MANIFEST),input_manifest_sha256=manifest_sha,
            episodes=[history_by[e] for e in sorted(history_by)],sample_rate=RATE,channels=2,pcm_encoding='IEEE float32 WAV',
            source_files_modified=False,resolve_or_UI_used=False,human_listening_validated=False,
            limits=['This is not a Resolve render; track/bus processing, pan law, codec timing differences are not modelled.','Mono VO is equal-amplitude dual-mono for a conservative upper peak estimate; Resolve may attenuate a center-panned mono source.','No gain beyond row.gain_db is added, no limiting/normalization/fades are introduced.','Stereo float WAV preserves peak overs for diagnosis, unlike integer clipping.','Clip lengths use native row.end-row.start; source_end is intentionally ignored.'])
history_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(report=str(history_path),completed_episodes=[e['episode'] for e in reports]),ensure_ascii=False),flush=True)
