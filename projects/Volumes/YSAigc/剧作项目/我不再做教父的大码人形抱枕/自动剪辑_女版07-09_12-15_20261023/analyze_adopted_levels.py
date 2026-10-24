from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess, json, math, hashlib, re
import numpy as np

W=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/自动剪辑_女版07-09_12-15_20261023')
READ=json.loads((W/'Resolve_组装实读.json').read_text())
INV=json.loads((W/'素材盘点.json').read_text())
FF=str(Path(INV['ffprobe_path']).with_name('ffmpeg'))
SR=48000;FPS=24;SPF=SR//FPS

def db(x):return round(20*math.log10(float(x)),3) if x>0 else -120.0
def stat(a):
    if not a.size:return {'peak_dbfs':-120,'rms_dbfs':-120,'active_rms_dbfs':-120,'over_full_scale_samples':0}
    peak=float(np.max(np.abs(a)));rms=float(np.sqrt(np.mean(a.astype(np.float64)**2)))
    blocks=a[:len(a)//4800*4800]
    if len(blocks):
        e=np.mean(blocks.reshape(-1,4800,2).astype(np.float64)**2,axis=(1,2))
        threshold=max(10**(-55/10),float(e.max())*10**(-22/10))
        active=e[e>=threshold]
        active_rms=float(np.sqrt(np.mean(active))) if len(active) else 0
    else:active_rms=rms
    return {'peak_dbfs':db(peak),'rms_dbfs':db(rms),'active_rms_dbfs':db(active_rms),
            'over_full_scale_samples':int(np.sum(np.abs(a)>=1)),
            'peak_linear':round(peak,8),'measurement':'decoded float PCM; active RMS uses 100 ms energy gates, not LUFS or true peak'}

cache={}
def decode(clip):
    key=(clip['path'],int(clip['source_start_frame']),int(clip['source_end_frame']))
    count=(key[2]-key[1])*SPF
    if key in cache:return cache[key]
    cmd=[FF,'-nostdin','-hide_banner','-loglevel','error','-ss',str(key[1]/FPS),
         '-i',key[0],'-t',str((key[2]-key[1])/FPS),'-map','0:a:0','-ac','2',
         '-ar',str(SR),'-f','f32le','pipe:1']
    p=subprocess.run(cmd,capture_output=True,timeout=40)
    if p.returncode:raise RuntimeError(p.stderr.decode('utf8','replace'))
    a=np.frombuffer(p.stdout,dtype='<f4').reshape(-1,2).copy()
    if len(a)<count:a=np.pad(a,((0,count-len(a)),(0,0)))
    a=a[:count]
    cache[key]=a
    return a

results=[];allrows=[]
for native in sorted(READ['episodes'],key=lambda x:x['episode']):
    path=Path(native['plan_path']);doc=json.loads(path.read_text())
    ep=next(e for e in doc['episodes'] if e['episode']==native['episode'])
    mixed=np.zeros((ep['duration_frames']*SPF,2),dtype=np.float32)
    rows=[]
    jobs=[]
    for track in ['video','narration']:
        for index,clip in enumerate(ep[track],1):jobs.append((track,index,clip))
    with ThreadPoolExecutor(max_workers=4) as pool:
        pcm=list(pool.map(lambda j:decode(j[2]),jobs))
    for (track,index,clip),a in zip(jobs,pcm):
        gain=float(clip.get('gain_db',0));g=10**(gain/20)
        start=clip['record_frame']*SPF;end=start+len(a)
        mixed[start:end]+=a*g
        r={'episode':ep['episode'],'track':'A1同期声' if track=='video' else 'A2旁白',
           'plan_clip_index':index,'source_path':clip['path'],
           'source_start_frame':clip['source_start_frame'],'source_end_frame':clip['source_end_frame'],
           'record_frame':clip['record_frame'],'record_end_frame':end//SPF,
           'duration_seconds':len(a)/SR,'current_gain_db':gain,'tag':clip.get('tag',''),
           'source_levels':stat(a),'post_gain_levels':stat(a*g),
           'proposed_gain_db':gain,'proposal_reason':'No automatic change recommended from sample-level analysis alone.'}
        rows.append(r)
    events=[]
    for e in ep.get('audio_events',[]):
        if e.get('kind') not in ['character_dialogue','dialogue']:continue
        clip={'path':e['source_path'],'source_start_frame':e['source_start_frame'],
              'source_end_frame':e['source_end_frame']}
        a=decode(clip)
        events.append({'kind':e['kind'],'speaker':e.get('speaker'),'canonical_text':e.get('canonical_text'),
                       'source_path':e['source_path'],'source_start_frame':e['source_start_frame'],
                       'source_end_frame':e['source_end_frame'],'record_frame':e['record_frame'],
                       'source_levels':stat(a)})
    vo_active=[r['source_levels']['active_rms_dbfs'] for r in rows if r['track']=='A2旁白']
    vo_median=float(np.median(vo_active)) if vo_active else None
    warnings=[]
    for r in rows:
        pk=r['post_gain_levels']['peak_dbfs'];src=r['source_levels'];gain=r['current_gain_db']
        if pk>=-0.3:
            r['proposed_gain_db']=round(gain+(-1.5-pk),2)
            r['proposal_reason']='Retain at least 1.5 dB sample headroom; no destructive source change.'
            warnings.append({'type':'clip_low_sample_headroom','source_path':r['source_path'],
                             'source_range_frames':[r['source_start_frame'],r['source_end_frame']],
                             'track':r['track'],'post_gain_peak_dbfs':pk,'suggested_clip_gain_db':r['proposed_gain_db']})
    for e in events:
        st=e['source_levels']
        if vo_median is not None and st['active_rms_dbfs']<vo_median-8:
            boost=min(3,vo_median-st['active_rms_dbfs']-5,-1.5-st['peak_dbfs'])
            e['suggested_gain_delta_db']=round(max(0,boost),2)
            warnings.append({'type':'dialogue_quieter_than_episode_vo','canonical_text':e['canonical_text'],
                             'source_path':e['source_path'],'source_range_frames':[e['source_start_frame'],e['source_end_frame']],
                             'active_rms_dbfs':st['active_rms_dbfs'],'episode_vo_median_active_rms_dbfs':round(vo_median,3),
                             'suggested_gain_delta_db':e['suggested_gain_delta_db'],
                             'severity':'listening suggestion, not a mandatory normalization; quiet delivery may be intentional'})
    mix=stat(mixed)
    peak_check=None
    if mix['peak_dbfs']>-1.5:
        check=subprocess.run([FF,'-nostdin','-hide_banner','-f','f32le','-ar',str(SR),'-ac','2',
                              '-i','pipe:0','-af','ebur128=peak=true','-f','null','-'],
                             input=mixed.astype('<f4').tobytes(),stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE,timeout=60)
        log=check.stderr.decode('utf8','replace')
        peaks=re.findall(r'True peak:\s+Peak:\s*([-\d.]+)\s*dBFS',log)
        integrated=re.findall(r'Integrated loudness:\s+I:\s*([-\d.]+)\s*LUFS',log)
        peak_check={'ffmpeg_returncode':check.returncode,
                    'true_peak_dbtp':float(peaks[-1]) if peaks else None,
                    'integrated_lufs':float(integrated[-1]) if integrated else None,
                    'scope':'Only current-gain offline mixed PCM; no native Fairlight effects/bus processing.'}
        if check.returncode:peak_check['error_tail']=log[-1000:]
    if mix['peak_dbfs']>=-0.3:
        warnings.append({'type':'summed_mix_headroom_risk','mix_peak_dbfs':mix['peak_dbfs'],
                         'samples_at_or_above_full_scale':mix['over_full_scale_samples'],
                         'suggested_timeline_or_master_trim_db':round(-1.5-mix['peak_dbfs'],2)})
    result={'episode':ep['episode'],'plan_path':str(path),'plan_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'duration_frames':ep['duration_frames'],'mix_pcm_levels_at_planned_clip_gains':mix,
            'tight_headroom_true_peak_check':peak_check,
            'median_vo_active_rms_dbfs':round(vo_median,3) if vo_median else None,
            'source_clips':rows,'canonical_dialogue_events':events,'warnings':warnings}
    results.append(result);allrows+=rows
    print(json.dumps({'episode':ep['episode'],'mix':mix,'vo_median':vo_median,'warning_count':len(warnings),'warnings':warnings},ensure_ascii=False),flush=True)
    cache.clear()

out={'analysis_only':True,'source_media_modified':False,'resolve_operated':False,'plans_modified':False,
     'method':'Decode only adopted source intervals to 48 kHz stereo float PCM, measure peaks/RMS/100 ms gated active RMS; sum at current planned gains and record frames. Not LUFS, true-peak, acoustic quality or native playback validation.',
     'limitations':['Sample peaks do not rule out intersample overs.','This is an offline plan sum, not a recorded native Fairlight bus output; native bus/effect/routing settings can change actual levels.','No unrecognized natural-sound interval is treated as canonical dialogue.','Suggested gains are advisory only. No clip, plan, source or Resolve gain was changed.'],
     'episodes':results,'warning_count':sum(len(e['warnings']) for e in results)}
(W/'source_levels_采用区间电平分析.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('REPORT',W/'source_levels_采用区间电平分析.json',flush=True)
