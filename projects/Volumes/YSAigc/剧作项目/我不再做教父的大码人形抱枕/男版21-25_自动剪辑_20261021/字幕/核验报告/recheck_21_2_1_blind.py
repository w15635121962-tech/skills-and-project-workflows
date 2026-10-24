import os,sys,pathlib,json,subprocess,datetime
B=pathlib.Path(__file__).resolve().parents[2];P=B.parent;old=P/'配音制作_前3集/制作资料/音频内容与顺序核验_20261018/ASR';sys.path[:0]=[str(P/'达芬奇剪辑_EP21-25_20261020/转录/runtime_compatible'),str(old/'.venv/lib/python3.12/site-packages')];ff='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin';os.environ['PATH']=ff+os.pathsep+os.environ.get('PATH','');os.environ['HF_HUB_OFFLINE']='1'
import mlx_whisper
D=json.loads((B/'男版素材盘点.json').read_text());src=next(v['path'] for e in D['episodes'] for v in e['videos'] if v['filename']=='男版21-2-1.mp4');out=B/'字幕/核验报告';rows=[]
for s,e in [(0,4),(1.5,4),(0,14.041667)]:
 dest=out/f'21_2_1_src_{s}_{e}_TEMP.wav';subprocess.run([ff+'/ffmpeg','-v','error','-ss',str(s),'-i',src,'-t',str(e-s),'-ar','16000','-ac','1','-y',str(dest)],check=True)
 raw=mlx_whisper.transcribe(str(dest),path_or_hf_repo=str(old/'models/large-v3-turbo/weights'),language='en',task='transcribe',temperature=0.0,condition_on_previous_text=False,initial_prompt=None,word_timestamps=True,fp16=True,verbose=None)
 rows.append({'source_start':s,'source_end':e,'text':raw.get('text'),'segments':raw.get('segments'),'blind':True,'script_supplied':False,'manual_listening':False});print(s,e,raw.get('text'),flush=True)
 dest.unlink()
(out/'21_2_1_非原稿呼名_独立盲复核.json').write_text(json.dumps({'source':src,'cropped_rechecks':rows,'basis':'Independent unprompted local ASR crops; no manual listening claim'},ensure_ascii=False,indent=2,default=str))
