"""Offline fresh-range track sum, unchanged levels, and audition MP3s."""
from pathlib import Path
from fractions import Fraction
import json
import math
import wave
import av
import numpy as np

ROOT=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_画面缓推与旁白气口精修_v14')
WORK=ROOT/'工作文件';OUT=ROOT/'旁白与混音';PRE=ROOT/'气口试听'
SR,SPF=48000,1920
live=json.loads((WORK/'live_before_v14.json').read_text())
edit=json.loads((WORK/'audio_edit_map_v14.json').read_text())
new_voice=Path(edit['output'])

def decode(raw):
    b=np.frombuffer(raw,np.uint8).reshape(-1,3).astype(np.int32)
    v=b[:,0]|b[:,1]<<8|b[:,2]<<16
    return np.where(v&0x800000,v-0x1000000,v).reshape(-1,2)

def encode(a):
    a=np.asarray(a,np.int32).reshape(-1)
    return np.column_stack((a&255,(a>>8)&255,(a>>16)&255)).astype(np.uint8).tobytes()

def open_new_wav(p):
    assert not p.exists(),p
    f=wave.open(str(p),'wb');f.setnchannels(2);f.setsampwidth(3);f.setframerate(SR)
    return f

items=[];handles={}
for track in live['snapshot']['audio']:
    if not track['enabled']:continue
    for i in track['items']:
        if not i.get('enabled',True):continue
        p=Path(i['path']);h=wave.open(str(p),'rb')
        assert h.getparams()[:3]==(2,3,SR),(p,h.getparams())
        handles[str(p)]=h
        assert i['offset']*SPF+(i['end']-i['start'])*SPF<=h.getnframes(),i
        items.append({**i,'track':track['track'],
                      'source_frame_units':'25fps timeline units from fresh snapshot',
                      'source_start_sample':i['offset']*SPF,
                      'duration_samples':(i['end']-i['start'])*SPF})
new_h=wave.open(str(new_voice),'rb')
old_mix=OUT/'02_原轨范围重建_调整前混音_v14.wav'
new_mix=OUT/'03_完整混音_气口精修_v14.wav'
old_out,new_out=open_new_wav(old_mix),open_new_wav(new_mix)
total=11507*SPF;peak_old=peak_new=clips_old=clips_new=0
for pos in range(0,total,SR*10):
    end=min(total,pos+SR*10);n=end-pos
    before=np.zeros((n,2),np.int64);after=np.zeros((n,2),np.int64)
    for i in items:
        a=max(pos,i['start']*SPF);b=min(end,i['end']*SPF)
        if b<=a:continue
        off=i['source_start_sample']+a-i['start']*SPF
        h=handles[i['path']];h.setpos(off);z=decode(h.readframes(b-a)).astype(np.int64)
        before[a-pos:b-pos]+=z
        if i['track']==1:
            new_h.setpos(off);z=decode(new_h.readframes(b-a)).astype(np.int64)
        after[a-pos:b-pos]+=z
    peak_old=max(peak_old,int(np.max(abs(before))));peak_new=max(peak_new,int(np.max(abs(after))))
    clips_old+=int(np.count_nonzero(np.abs(before)>=8388607))
    clips_new+=int(np.count_nonzero(np.abs(after)>=8388607))
    assert not np.any(before>8388607) and not np.any(before<-8388608),'Original fresh mix would clip'
    assert not np.any(after>8388607) and not np.any(after<-8388608),'New fresh mix would clip'
    old_out.writeframesraw(encode(before));new_out.writeframesraw(encode(after))
old_out.close();new_out.close()
for h in handles.values():h.close()
new_h.close()
assert peak_new<=peak_old,('New sample peak increased',peak_old,peak_new)
for p in (old_mix,new_mix):
    with wave.open(str(p),'rb') as h:assert h.getnframes()==total
for p,name in [(old_mix,'配乐与气口_调整前_206至222秒.wav'),(new_mix,'配乐与气口_调整后_206至222秒.wav')]:
    with wave.open(str(p),'rb') as h:
        h.setpos(206*SR);raw=h.readframes(16*SR)
    with open_new_wav(PRE/name) as h:h.writeframes(raw)

def mp3(src,dest):
    assert not dest.exists(),dest
    samples=0
    with wave.open(str(src),'rb') as h, av.open(str(dest),'w') as out:
        st=out.add_stream('libmp3lame',rate=SR);st.layout='stereo';st.bit_rate=256000
        out.metadata['title']=dest.stem
        while True:
            raw=h.readframes(1152*10)
            if not raw:break
            z=(decode(raw).astype(np.float32)/8388608).T.copy()
            frame=av.AudioFrame.from_ndarray(z,format='fltp',layout='stereo')
            frame.sample_rate=SR;frame.time_base=Fraction(1,SR);frame.pts=samples
            samples+=frame.samples
            for pkt in st.encode(frame):out.mux(pkt)
        for pkt in st.encode():out.mux(pkt)
    decoded=0
    with av.open(str(dest)) as c:
        stream=c.streams.audio[0]
        assert stream.codec_context.name=='mp3float' or stream.codec_context.name=='mp3'
        for frame in c.decode(stream):
            assert frame.sample_rate==SR and len(frame.layout.channels)==2
            decoded+=frame.samples
    assert decoded==samples,(dest,decoded,samples)
    return {'source':str(src),'path':str(dest),'decoded_samples_per_channel':decoded,
            'sample_rate':SR,'channels':2,'seconds':decoded/SR,'bitrate':256000}

auditions=[]
for src,name in [(PRE/'旁白气口_调整前_206至222秒.wav','旁白气口_调整前_206至222秒.mp3'),
                 (PRE/'旁白气口_调整后_206至222秒.wav','旁白气口_调整后_206至222秒.mp3'),
                 (new_voice,'新完整旁白_气口精修_v14.mp3'),
                 (PRE/'配乐与气口_调整前_206至222秒.wav','配乐与气口_调整前_206至222秒.mp3'),
                 (PRE/'配乐与气口_调整后_206至222秒.wav','配乐与气口_调整后_206至222秒.mp3')]:
    auditions.append(mp3(src,PRE/name))
    print('AUDITION_READY',str(PRE/name),flush=True)
result={'status':'passed_sample_peak_no_clipping_loudness_measurement_pending',
        'old_fresh_range_mix':str(old_mix),'new_full_mix':str(new_mix),
        'duration_seconds':total/SR,'sample_rate':SR,'sample_width_bits':24,'channels':2,
        'actual_clip_ranges_from':str(WORK/'live_before_v14.json'),'clips':items,
        'BGM05_actual_duration_frames':next(i['end']-i['start'] for i in items if 'BGM_05_' in i['name']),
        'before_sample_peak_dbfs':20*math.log10(peak_old/8388608),
        'after_sample_peak_dbfs':20*math.log10(peak_new/8388608),
        'sample_peak_not_increased':peak_new<=peak_old,
        'before_clipped_channel_samples':clips_old,'after_clipped_channel_samples':clips_new,
        'auditions':auditions,'audition_available':False,
        'mix_limit':'Offline sample sum uses fresh clip source ranges at existing baked source-file levels. No unexposed Resolve bus/plugin/automation is modeled; this is not a native final rendered soundtrack.',
        'source_media_modified':False,'resolve_connected_or_modified':False,
        'gain_denoise_compression_speed_changes':False}
(WORK/'offline_mix_auditions_v14.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False)[:800],flush=True)
