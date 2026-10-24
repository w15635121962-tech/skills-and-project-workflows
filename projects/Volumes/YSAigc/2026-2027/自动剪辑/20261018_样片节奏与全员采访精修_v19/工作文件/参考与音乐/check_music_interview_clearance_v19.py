from pathlib import Path
import json,wave,hashlib
import numpy as np
R=Path(__file__).resolve().parents[2]
O=R/'旁白与配乐/配乐每40秒'
plan=json.loads((R/'工作文件/采访最终方案/four_speaker_plan_final.json').read_text())

def read24(p):
 with wave.open(str(p)) as h:
  ch=h.getnchannels();assert h.getsampwidth()==3 and h.getframerate()==48000
  b=np.frombuffer(h.readframes(h.getnframes()),np.uint8).reshape(-1,3).astype(np.int32)
  z=b[:,0]|b[:,1]<<8|b[:,2]<<16;z=np.where(z&0x800000,z-0x1000000,z).reshape(-1,ch)
 return z.astype(np.float64)/8388608
music=read24(O/'00_全片每40秒换曲_音乐总线_v19_48k24.wav')
start=round(441.68*48000);rows=[]
for c in plan:
 rec=json.loads((R/'旁白与配乐/采访准备'/(Path(c['source']).stem+'_最终校准记录.json')).read_text())
 p=Path(rec['prepared_wav']);voice=read24(p)
 a=round(c['source_in_sec']*48000);n=c['timeline_duration_frames_25fps']*1920
 v=voice[a:a+n];m=music[start:start+n];assert len(v)==len(m)==n
 sr,ms=np.mean(v*v),np.mean(m*m)
 rms_ratio=10*np.log10(sr/ms)
 win=[]
 for i in range(0,n-48000+1,24000):
  vr=float(np.mean(v[i:i+48000]**2));mr=float(np.mean(m[i:i+48000]**2))
  vd=10*np.log10(max(vr,1e-30));md=10*np.log10(max(mr,1e-30))
  if vd>-35:win.append(vd-md)
 mono=np.mean(v,axis=1,keepdims=True);mix_nominal=m+mono/(2**.5);mix_conservative=m+mono
 q={'speaker':c['speaker_key'],'prepared_voice':str(p),'record_start_sec':start/48000,'record_end_sec':(start+n)/48000,'duration':n/48000,'prepared_source_in_sec':a/48000,'voice_rms_dbfs':float(10*np.log10(sr)),'music_rms_dbfs':float(10*np.log10(ms)),'voice_above_music_rms_db':float(rms_ratio),'one_second_speech_window_margin_db_p10':float(np.percentile(win,10)),'one_second_speech_window_margin_db_median':float(np.median(win)),'conservative_mix_sample_peak_dbfs':float(20*np.log10(np.max(np.abs(mix_conservative)))),'nominal_minus3db_center_mix_sample_peak_dbfs':float(20*np.log10(np.max(np.abs(mix_nominal)))),'voice_pcm_modified':False,'native_clip_gain_db':0,'reference_final_measurement':rec.get('final_measurement')}
 assert rms_ratio>10,(c['speaker_key'],rms_ratio)
 assert np.max(np.abs(mix_conservative))<1,('possible clip',c['speaker_key'])
 rows.append(q);start+=n
assert start==round(482.2*48000),(start,start/48000)
a={'status':'passed','four_prepared_voice_sources_read_only':True,'interview_range_seconds':[441.68,482.2],'reference':'measured sample RMS ratio; this is not an intelligibility or subjective listening certification','all_four_voice_music_rms_margin_at_least_10db':True,'conservative_unattenuated_mono_mix_no_sample_clipping':True,'rows':rows}
(O/'采访与音乐余量核验_v19.json').write_text(json.dumps(a,ensure_ascii=False,indent=2));print(json.dumps(a,ensure_ascii=False,indent=2))
