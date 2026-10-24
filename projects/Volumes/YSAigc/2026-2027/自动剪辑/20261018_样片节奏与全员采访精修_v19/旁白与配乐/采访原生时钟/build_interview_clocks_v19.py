"""Offline only: exact full-source PCM, carried by a 25fps audio-only import MOV."""
from pathlib import Path
from fractions import Fraction
from concurrent.futures import ThreadPoolExecutor
import av, wave, hashlib, json, math, subprocess, sys
import numpy as np, soundfile as sf

OUT=Path(__file__).resolve().parent
BASE=OUT.parents[1]
PRE=OUT.parent/'采访准备'
PLAN=json.loads((PRE/'four_speaker_audio_ready_v19.json').read_text())
SRCPLAN=json.loads((BASE/'工作文件/采访最终方案/four_speaker_plan_final.json').read_text())
SR=48000;FPS=25;SPF=1920

def encode24(z):
    z=z.reshape(-1).astype(np.int32)
    raw=np.empty((len(z),3),dtype=np.uint8)
    for i in range(3):raw[:,i]=(z>>(8*i))&255
    return raw.tobytes()

def decode24(raw):
    u=np.frombuffer(raw,np.uint8).reshape(-1,3).astype(np.int32)
    z=u[:,0]|(u[:,1]<<8)|(u[:,2]<<16)
    z=(z^0x800000)-0x800000
    return z.reshape(-1,2)

def write24(path,z):
    assert not path.exists(),path
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(3);f.setframerate(SR);f.writeframes(encode24(z))

def pcm_hash(path):
    sha=hashlib.sha256()
    with wave.open(str(path)) as f:
        assert (f.getnchannels(),f.getsampwidth(),f.getframerate())==(2,3,SR)
        count=f.getnframes()
        while True:
            raw=f.readframes(65536)
            if not raw:break
            sha.update(raw)
    return sha.hexdigest(),count

def clock_container(wav_path,mov_path):
    assert not mov_path.exists(),mov_path
    with wave.open(str(wav_path)) as h,av.open(str(mov_path),'w') as o:
        count=h.getnframes();frames=math.ceil(count/SPF)
        assert (h.getnchannels(),h.getsampwidth(),h.getframerate())==(2,3,SR)
        v=o.add_stream('libx264',rate=FPS);v.width=16;v.height=16;v.pix_fmt='yuv420p'
        v.options={'preset':'ultrafast','tune':'zerolatency','crf':'51','bf':'0'};v.codec_context.thread_count=1
        a=o.add_stream('pcm_s24le',rate=SR);a.layout='stereo';a.time_base=Fraction(1,SR)
        o.metadata['comment']='Full-source PCM clock carrier. Native append AUDIO ONLY, mediaType=2. Black video must never be used.'
        black=np.zeros((16,16,3),np.uint8)
        for f in range(frames):
            vf=av.VideoFrame.from_ndarray(black,format='rgb24');vf.pts=f;vf.time_base=Fraction(1,FPS)
            for p in v.encode(vf):o.mux(p)
            raw=h.readframes(SPF);expected=min(SPF,count-f*SPF)
            assert len(raw)==expected*6
            z=decode24(raw)
            af=av.AudioFrame.from_ndarray((z<<8).reshape(1,-1),format='s32',layout='stereo')
            af.sample_rate=SR;af.pts=f*SPF;af.time_base=Fraction(1,SR)
            for p in a.encode(af):o.mux(p)
        for p in v.encode():o.mux(p)
        for p in a.encode():o.mux(p)
    sha=hashlib.sha256();ns=0;pts=[]
    with av.open(str(mov_path)) as c:
        vs=c.streams.video[0];st=c.streams.audio[0]
        assert vs.average_rate==25 and vs.frames==frames
        assert (vs.codec_context.width,vs.codec_context.height)==(16,16)
        assert st.codec_context.name=='pcm_s24le' and st.codec_context.sample_rate==SR
        assert st.start_time==0 and st.duration==count and st.time_base==Fraction(1,SR)
        for af in c.decode(st):
            assert af.format.name=='s32' and len(af.layout.channels)==2 and af.sample_rate==SR
            assert af.pts==ns
            if len(pts)<3:pts.append({'pts':af.pts,'samples':af.samples,'time_base':str(af.time_base)})
            z=af.to_ndarray().reshape(-1,2)>>8;sha.update(encode24(z));ns+=len(z)
    expected,nwav=pcm_hash(wav_path)
    assert ns==nwav==count and sha.hexdigest()==expected
    return {'video_fps':25,'video_size':[16,16],'video_codec':'h264','video_frames':frames,
            'video_duration_sec':frames/FPS,'audio_codec':'pcm_s24le','audio_sample_rate':SR,
            'audio_samples':count,'audio_duration_sec':count/SR,'audio_channels':2,
            'audio_pts_start':0,'audio_time_base':'1/48000','wav_pcm_sha256':expected,
            'mov_decoded_pcm_sha256':sha.hexdigest(),'decoded_PCM_bit_identical_to_WAV':True,
            'first_audio_packets':pts,'tail_audio_padding_samples':0,
            'black_video_tail_extra_sec':frames/FPS-count/SR}

gains=[0,-.2,.2,-.7]
starts=[11042,11229,11489,11806];ends=[11229,11489,11806,12055]
rows=[]
for i,(p,s,gain,start,end) in enumerate(zip(PLAN,SRCPLAN,gains,starts,ends),1):
    source=Path(p['prepared_wav']);mono,sr=sf.read(source,dtype='int32',always_2d=True)
    assert sr==SR and mono.shape[1]==1
    mono24=mono[:,0]>>8
    scalar=10**(gain/20)/math.sqrt(2)
    z=np.rint(mono24.astype(np.float64)*scalar).astype(np.int32)
    assert z.min()>=-8388608 and z.max()<=8388607
    stereo=np.repeat(z[:,None],2,axis=1)
    wav=OUT/f'{i:02d}_{p["speaker_key"]}_完整源时钟_双单声道_48k24bit_v19.wav'
    write24(wav,stereo)
    verify,vsr=sf.read(wav,dtype='int32',always_2d=True)
    assert vsr==SR and len(verify)==len(mono) and np.array_equal(verify>>8,stereo)
    mov=OUT/f'{i:02d}_{p["speaker_key"]}_25fps_完整PCM时钟_v19.mov'
    rows.append({'speaker_key':p['speaker_key'],'source_video':s['source'],'prepared_mono_wav':str(source),
                 'full_source_stereo_wav':str(wav),'container_path':str(mov),
                 'source_n_samples':len(mono),'output_n_samples':len(stereo),
                 'per_channel_mono_scale':scalar,'dual_mono_power_compensation':'1/sqrt(2)',
                 'selected_phrase_gain_baked_db':gain,'native_clip_gain_db':0,
                 'source_in_frame':s['source_in_frame'],'source_out_frame_exclusive':s['source_out_frame_exclusive'],
                 'source_fps':25,'record_start_frame':start,'record_end_frame_exclusive':end,
                 'duration_frames':end-start,'native_media_type':2,'fade':'none','gate':'none'})

principal=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_旁白精修/工作文件/audio_v2/04_校长完整讲话_余量.wav')
orig_sha,ns=pcm_hash(principal)
rows.append({'speaker_key':'总校长','source_video':'/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码/001/Proxies/20260924_C0163_Proxy.mp4',
             'source_video_in_frame':1197,'source_video_out_frame_exclusive':1562,
             'source_video_offset_seconds':47.88,
             'prepared_mono_wav':None,'full_source_stereo_wav':str(principal),
             'container_path':str(OUT/'05_总校长_25fps_原声完整PCM时钟_v19.mov'),
             'source_n_samples':ns,'output_n_samples':ns,'original_pcm_sha256':orig_sha,
             'per_channel_mono_scale':None,'dual_mono_power_compensation':'not applied: original stereo unchanged',
             'selected_phrase_gain_baked_db':0,'native_clip_gain_db':0,
             'source_in_frame':0,'source_out_frame_exclusive':365,'source_fps':25,
             'record_start_frame':12055,'record_end_frame_exclusive':12420,'duration_frames':365,
             'native_media_type':2,'fade':'none','gate':'none'})

def process(row):
    row['clock_container_verification']=clock_container(Path(row['full_source_stereo_wav']),Path(row['container_path']))
    stem=Path(row['container_path']).stem
    # Native endpoints consume 1920 PCM samples per 25fps source frame.
    wav,sr=sf.read(row['full_source_stereo_wav'],dtype='int32',always_2d=True)
    lo=row['source_in_frame']*SPF;hi=row['source_out_frame_exclusive']*SPF
    assert 0<=lo<hi<=len(wav)
    row['native_selected_source_samples']=[lo,hi]
    row['native_expected_duration_seconds']=(hi-lo)/SR
    excerpt=OUT/f'测量_{row["speaker_key"]}_原帧切口选句.wav';write24(excerpt,wav[lo:hi]>>8)
    for label,args in [('full_measure',['loudness.py',row['full_source_stereo_wav'],'--measure-only','-I','-16','--tp','-2']),
                       ('selected_measure',['loudness.py',str(excerpt),'--measure-only','-I','-16','--tp','-2'])]:
        cmd=[sys.executable,str(PRE/'run_skill_pcm24.py'),*args,'--json']
        r=subprocess.run(cmd,capture_output=True,text=True,check=True)
        (OUT/f'{stem}_{label}.json').write_text(r.stdout);(OUT/f'{stem}_{label}.log').write_text(r.stderr)
        row[label]=json.loads(r.stdout)
    probe=subprocess.run([sys.executable,'/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/probe.py',row['container_path'],'--json'],capture_output=True,text=True,check=True)
    row['actual_container_probe']=json.loads(probe.stdout)
    (OUT/f'{stem}_probe.json').write_text(probe.stdout)
    assert row['actual_container_probe']['video']['fps']==25
    assert row['actual_container_probe']['audio']['codec']=='pcm_s24le'
    print(json.dumps({'speaker':row['speaker_key'],'container':row['container_path'],
                      'PCM_exact':True,'range':[row['record_start_frame'],row['record_end_frame_exclusive']],
                      'selected':row['selected_measure']},ensure_ascii=False),flush=True)
    return row

with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(process,rows))
manifest={'status':'passed_offline_ready_for_native_audio_only_import','fps':FPS,'sample_rate':SR,'pcm_bits':24,
          'channels':2,'native_media_type':2,'native_clip_gain_db':0,'no_additional_fades_or_gate':True,
          'source_clock_full_coverage_preserved':True,'all_five_decoded_PCM_bit_exact':True,
          'record_range_frames':[11042,12420],'interviews':rows,
          'principal_original_PCM_unchanged':True,'resolve_connection':'not used',
          'audition':'unavailable: no listening tool; actual measurement, frame-clock, and PCM verification only',
          'import_contract':'Append audio only (mediaType=2) to A2, exact source frame ranges at 25fps. Black 16x16 video never on video tracks. Gain already baked; native clip volume 0 dB, no additional fade/gate.'}
(OUT/'五人采访_25fps原生回装清单_v19.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('FIVE_INTERVIEW_CLOCKS_READY',OUT/'五人采访_25fps原生回装清单_v19.json',flush=True)
