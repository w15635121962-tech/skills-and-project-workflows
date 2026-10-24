"""Pitch-preserving voice replacement to frozen edit/subtitle timing.

Render continuous islands with small overlaps at tempo changes, then split the
same PCM at original frame boundaries. Original MP3s and Resolve stay untouched.
"""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import wave

import numpy as np

BASE = Path(__file__).resolve().parent
FF = '/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'
SR = 48000
PLAN = BASE/'EP01-03_42切新旁白槽位计划.json'
data = json.loads(PLAN.read_text(encoding='utf-8'))
assert data['ready_for_parent_whole_island_render']
anchors = json.loads((BASE/'字幕与新旁白_词锚点.json').read_text(encoding='utf-8'))['anchors']
levels = {x['new_source']:x for x in json.loads((BASE/'新旧旁白响度匹配分析.json').read_text(encoding='utf-8'))}
snap = json.loads((BASE/'替换前_完整时间线实读.json').read_text(encoding='utf-8'))
OUT=BASE/'对齐音频';OUT.mkdir(exist_ok=True)
Q=BASE/'音频核验';Q.mkdir(exist_ok=True)

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def decode(path):
    return np.frombuffer(subprocess.check_output([FF,'-v','error','-i',str(path),'-ac','1','-ar',str(SR),'-f','f32le','-']),dtype='<f4').copy()

def write24(path, pcm):
    q=np.round(np.clip(pcm,-1,1)*(2**23-1)).astype('<i4')
    packed=q.view(np.uint8).reshape(-1,4)[:,:3].tobytes()
    with wave.open(str(path),'wb') as f:
        f.setnchannels(1);f.setsampwidth(3);f.setframerate(SR);f.writeframes(packed)
    return packed

def closest_times(src, desired, duration, low=.85, high=1.60):
    """Project cue boundaries onto bounded tempo intervals (Dykstra)."""
    deltas=np.diff(src);lower=deltas/high;upper=deltas/low
    assert lower.sum()<=duration+1e-7 and upper.sum()>=duration-1e-7
    n=len(src)-2
    if not n:return np.array([0.,duration])
    rows=[]
    for i in range(len(deltas)):
        v=np.zeros(n);constant=0.
        if i>0:v[i-1]-=1
        if i+1<len(src)-1:v[i]+=1
        else:constant+=duration
        rows.extend([(v,lower[i]-constant),(-v,constant-upper[i])])
    x=np.array(desired[1:-1],float);corrections=[np.zeros(n) for _ in rows]
    for _ in range(1500):
        old=x.copy()
        for j,(a,b) in enumerate(rows):
            y=x+corrections[j];z=y.copy();v=b-float(a@y)
            if v>0:z+=a*v/float(a@a)
            corrections[j]=y-z;x=z
        if max(abs(x-old))<1e-10:break
    result=np.r_[0.,x,duration]
    assert all(np.diff(result)>=lower-1e-5) and all(np.diff(result)<=upper+1e-5)
    return result

sources={};report=[];slices=[]
episode_pcm={x['ep']:np.zeros(int(x['end'])*1600,dtype=np.float32) for x in snap['timelines']}
for isl in data['merged_islands']:
    path=isl['new_source_path'];assert digest(path)==isl['new_source_sha256']
    if path not in sources:sources[path]=decode(path)
    raw=sources[path];start=isl['new_source_in_seconds'];end=isl['new_source_out_seconds_exclusive']
    # Trim only truly quiet exterior material. Preserve 50 ms and never trim an
    # internal island boundary chosen by the waveform/word correspondence pass.
    if start==0 or isl.get('uses_entire_new_source_file'):
        active=np.flatnonzero(abs(raw)>10**(-65/20))
        if len(active):
            if start==0:start=max(0.,active[0]/SR-.05)
            if end>=len(raw)/SR-.001:end=min(end,(active[-1]+1)/SR+.05)
    duration=isl['record_duration_seconds'];num=isl['output_samples_exact']
    aa=sorted([x for x in anchors if x['episode']==isl['episode'] and x['new_source_path']==path
               and x['new_source_word_start_seconds']>=start-.35
               and x['new_source_word_end_seconds']<=end+.35],key=lambda x:x['new_source_word_start_seconds'])
    points=[(start,0.)]
    for a,b in zip(aa,aa[1:]):
        s=(a['new_source_word_end_seconds']+b['new_source_word_start_seconds'])/2
        t=(a['target_record_end_frame_exclusive']+b['target_record_start_frame'])/60-isl['record_start_frame']/30
        if s>points[-1][0]+.05 and t>points[-1][1]+.05 and s<end-.05 and t<duration-.05:
            points.append((s,t))
    points.append((end,duration))
    src=np.array([x[0] for x in points]);desired=np.array([x[1] for x in points])
    # Preserve deliberate clip preroll before its first subtitle phrase. The
    # original clip edge is sometimes half a second ahead of its spoken text.
    lead=0.
    if aa:
        target_first=max(0.,aa[0]['target_record_start_frame']/30-isl['record_start_frame']/30)
        source_preroll=max(0.,aa[0]['new_source_word_start_seconds']-start)
        lead=max(0.,target_first-source_preroll/isl['tempo_needed'])
        lead=min(lead,duration*.25,duration-(end-start)/1.60-.005)
        lead=max(0.,lead)
    desired[0]=lead
    dst=closest_times(src,desired-lead,duration-lead)+lead
    canvas=np.zeros(num,dtype=np.float64);weight=np.zeros(num,dtype=np.float64);segments=[]
    for i,((s,e),(t,u)) in enumerate(zip(zip(src,src[1:]),zip(dst,dst[1:]))):
        tempo=(e-s)/(u-t);margin=.025
        a=max(start,s-(margin if i else 0));b=min(end,e+(margin if i<len(src)-2 else 0))
        inp=raw[round(a*SR):round(b*SR)].astype('<f4')
        result=subprocess.check_output([FF,'-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','pipe:0',
                    '-af',f'atempo={tempo:.12f}','-f','f32le','pipe:1'],input=inp.tobytes())
        pcm=np.frombuffer(result,dtype='<f4').copy()
        expected=round((b-a)/tempo*SR)
        discarded=pcm[expected:]
        # atempo's last window length varies; last-chunk material is silence or
        # is retained below. Allocate one extra window rather than cutting words.
        pcm=np.pad(pcm,(0,max(0,expected-len(pcm))))[:expected]
        pos=round((t-(s-a)/tempo)*SR)
        w=np.ones(len(pcm),dtype=np.float64)
        fade=max(1,round(margin/tempo*SR))
        if i:w[:min(2*fade,len(w))]=np.linspace(0,1,min(2*fade,len(w)))
        if i<len(src)-2:w[-min(2*fade,len(w)):]=np.linspace(1,0,min(2*fade,len(w)))
        left=max(pos,0);right=min(pos+len(pcm),num)
        canvas[left:right]+=pcm[left-pos:right-pos]*w[left-pos:right-pos]
        weight[left:right]+=w[left-pos:right-pos]
        segments.append({'new_source_in':float(s),'new_source_out':float(e),
                         'output_in':float(t),'output_out':float(u),'tempo_percent':tempo*100,
                         'discarded_filter_tail_samples':len(discarded),
                         'discarded_filter_tail_peak':float(max(abs(discarded),default=0))})
    canvas=np.divide(canvas,weight,out=np.zeros_like(canvas),where=weight>1e-9)
    lev=levels[path];gain=lev['old_level']['active_rms_dbfs']-lev['new_level']['active_rms_dbfs']
    gain=max(-12,min(6,gain));peak=max(abs(canvas),default=0)
    if peak>0:gain=min(gain,-1-20*math.log10(peak))
    canvas*=10**(gain/20)
    fade=min(round(.002*SR),len(canvas)//2)
    canvas[:fade]*=np.linspace(0,1,fade);canvas[-fade:]*=np.linspace(1,0,fade)
    island_path=Q/(isl['island_id']+'_连续适配.wav')
    packed=write24(island_path,canvas)
    rebuilt=b''
    for c in isl['original_items']:
        s=(c['record_start_frame']-isl['record_start_frame'])*1600
        e=(c['record_end_frame_exclusive']-isl['record_start_frame'])*1600
        folder=OUT/f"第{isl['episode']:02d}集";folder.mkdir(exist_ok=True)
        name=Path(path).stem+f"_对齐切{c['clip_index_zero_based']+1:02d}.wav"
        target=folder/name
        body=write24(target,canvas[s:e]);rebuilt+=body
        assert len(body)==(e-s)*3
        slices.append({**c,'episode':isl['episode'],'island_id':isl['island_id'],
                       'path':str(target),'sha256':digest(target),'samples':e-s,
                       'source_new_mp3':path,'gain_db_baked':gain,'speed_baked_into_wav':True,
                       'native_clip_speed_percent':100,'pitch_preserved':True})
    assert rebuilt==packed,'Continuous output slices differ from island PCM'
    ep=isl['episode'];a=isl['record_start_frame']*1600;b=isl['record_end_frame_exclusive']*1600
    episode_pcm[ep][a:b]=canvas
    report.append({'island_id':isl['island_id'],'episode':ep,'source':path,'source_hash':digest(path),
                   'source_in':start,'source_out':end,'target_samples':num,'segments':segments,
                   'gain_db':gain,'preserved_leading_subtitle_preroll_s':lead,
                   'max_cue_boundary_shift_s':float(max(abs(dst-desired))),
                   'internal_slices_reconstruct_exact_pcm':True,'pitch_preserved':True,
                   'output':str(island_path),'peak_dbfs':20*math.log10(max(max(abs(canvas)),1e-12))})
    print(isl['island_id'],len(segments),round(min(x['tempo_percent'] for x in segments),1),round(max(x['tempo_percent'] for x in segments),1),flush=True)
for ep,pcm in episode_pcm.items():write24(Q/f'EP{ep:02d}_替换后旁白监听.wav',pcm)
final={'status':'AUDIO_PREPARED_NOT_YET_IMPORTED','source_plan':str(PLAN),'source_plan_sha256':digest(PLAN),
       'source_mp3s_unchanged':True,'format':{'sample_rate':SR,'channels':1,'bit_depth':24},
       'user_policy':'Preserve existing picture, subtitles and sync-sound timing; adapt narration tempo',
       'islands':report,'clips':sorted(slices,key=lambda x:(x['episode'],x['clip_index_zero_based']))}
assert len(final['clips'])==42 and len(final['islands'])==30
(BASE/'42段对齐WAV_制作结果.json').write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding='utf-8')
print('COMPLETE',len(slices),len(report),flush=True)
