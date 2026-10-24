from pathlib import Path
import json,numpy as np,soundfile as sf,math,zlib,struct,binascii
from scipy.signal import resample_poly,spectrogram
from faster_whisper import WhisperModel
import pymupdf,sys
O=Path(__file__).parent
src=O/'原始旁白_仅解码.wav';a,sr=sf.read(src,dtype='float32');mono=a.mean(axis=1)
model=None if '--render-only' in sys.argv else WhisperModel('small',device='cpu',compute_type='int8',download_root='/Users/xuan/.local/share/promo-audio/models',cpu_threads=4,local_files_only=True)
specs=[('01_原声_绚丽待辨_03分50至04分00',230,240,235.24,235.60,'Script: xuan4 li4 | ASR: shun4 li4 - unconfirmed'),('02_原声_青年精进待辨_05分02至05分12',302,312,306.74,307.18,'Script: jing1 jin4 | ASR: jing1 ji4 - unconfirmed')]
results=[]
def png_rgb(arr):
 h,w,c=arr.shape
 def chunk(name,data):return struct.pack('!I',len(data))+name+data+struct.pack('!I',binascii.crc32(name+data)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\x00'+row.tobytes() for row in arr),6))+chunk(b'IEND',b'')
for name,start,end,lo,hi,label in specs:
 y=a[round(start*sr):round(end*sr)];wav=O/(name+'.wav');sf.write(wav,y,sr,subtype='PCM_16');x=y.mean(axis=1);g=math.gcd(sr,16000);x16=resample_poly(x,16000//g,sr//g).astype('float32');runs=[]
 for beam in (() if '--render-only' in sys.argv else (1,5)):
  ss,_=model.transcribe(x16,language='zh',beam_size=beam,word_timestamps=True,vad_filter=False,condition_on_previous_text=False)
  segs=[{'start':round(s.start+start,3),'end':round(s.end+start,3),'text':s.text,'avg_logprob':s.avg_logprob,'words':[{'word':w.word,'start':round(w.start+start,3),'end':round(w.end+start,3),'p':w.probability} for w in (s.words or [])]} for s in ss]
  runs.append({'beam_size':beam,'no_initial_prompt':True,'vad_filter':False,'condition_on_previous_text':False,'segments':segs});print(name,beam,json.dumps(segs,ensure_ascii=False),flush=True)
 f,t,P=spectrogram(x16,fs=16000,nperseg=256,noverlap=192,mode='psd');S=10*np.log10(np.maximum(P,1e-15));S=S-np.percentile(S,99.8);norm=np.clip((S+75)/75,0,1);anchors=np.array([[15,8,40],[49,68,130],[35,145,140],[253,231,37]],dtype=float);u=norm*3;j=np.minimum(u.astype(int),2);frac=u-j;rgb=(anchors[j]*(1-frac[...,None])+anchors[j+1]*frac[...,None]).astype('uint8');rgb=rgb[::-1,:,:]
 doc=pymupdf.open();pg=doc.new_page(width=1400,height=700);pg.draw_rect(pg.rect,color=None,fill=(1,1,1));pg.insert_text((65,30),'Original narration - waveform and spectrogram',fontsize=22,fontname='helv');pg.insert_text((65,56),f'{start:.2f}-{end:.2f} s | 44.1 kHz stereo source | no gain / no denoise / no time stretch',fontsize=13,fontname='helv');pg.insert_text((65,80),label,fontsize=14,fontname='helv')
 x0,x1=80,1340;y0,y1=120,300;pg.draw_line((x0,(y0+y1)/2),(x1,(y0+y1)/2),color=(.75,.75,.75));N=1260;chunks=np.array_split(x,N);points=[]
 for k,v in enumerate(chunks):
  xx=x0+(x1-x0)*k/(N-1);q=float(v[np.argmax(np.abs(v))]);points.append((xx,(y0+y1)/2-q*(y1-y0)*.46))
 pg.draw_polyline(points,color=(.08,.32,.56),width=.65);pg.insert_text((x0,y0-8),'Waveform, original amplitude',fontsize=12,fontname='helv');pg.insert_image(pymupdf.Rect(x0,350,x1,630),stream=png_rgb(rgb),keep_proportion=False);pg.insert_text((x0,340),'Spectrogram, 0-8 kHz (brightness = relative power)',fontsize=12,fontname='helv')
 for sec in range(start,end+1):
  xx=x0+(sec-start)/(end-start)*(x1-x0);pg.draw_line((xx,350),(xx,630),color=(.4,.4,.4),width=.2);pg.insert_text((xx-14,652),f'{sec:.0f}',fontsize=10,fontname='helv')
 for marker in (lo,hi):
  xx=x0+(marker-start)/(end-start)*(x1-x0);pg.draw_line((xx,110),(xx,635),color=(.85,.15,.1),width=1)
 pg.insert_text((80,678),'Red lines mark approximate ASR word interval; spectra do not prove spelling or a pronunciation error.',fontsize=12,fontname='helv')
 png=O/(name+'_波形声谱.png');pg.get_pixmap(matrix=pymupdf.Matrix(1,1),alpha=False).save(png)
 results.append({'name':name,'source':str(src),'original_source':'/Volumes/YSAigc/2026-2027/文汇中学/配音/文汇学校配音.mp3','start':start,'end':end,'clip':str(wav),'waveform_spectrogram':str(png),'runs':runs,'conclusion':'Unconfirmed. Same local small model with different context/beam is not independent human listening or a second acoustic model.'})
if '--render-only' not in sys.argv:(O/'疑点短窗再识别与声谱.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
