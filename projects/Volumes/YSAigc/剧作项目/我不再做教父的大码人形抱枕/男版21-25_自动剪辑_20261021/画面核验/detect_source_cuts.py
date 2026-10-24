import json,pathlib,subprocess,concurrent.futures,re
B=pathlib.Path(__file__).resolve().parent;D=json.loads((B.parent/'男版素材盘点.json').read_text());ff='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'
def one(v):
 p=subprocess.run([ff,'-hide_banner','-i',v['path'],'-vf',"scale=120:-2,blackdetect=d=0.15:pix_th=0.10,select='gt(scene,0.22)',showinfo",'-an','-f','null','-'],text=True,capture_output=True,check=True)
 return {'filename':v['filename'],'source_path':v['path'],'scene_change_candidate_seconds':[float(x) for x in re.findall(r'pts_time:([0-9.]+)',p.stderr)],'black_intervals':[{'start':float(a),'end':float(b),'duration':float(c)} for a,b,c in re.findall(r'black_start:([0-9.]+) black_end:([0-9.]+) black_duration:([0-9.]+)',p.stderr)],'method':'ffmpeg scene>0.22 candidates only; blackdetect >=.15s'}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:r=list(ex.map(one,[v for e in D['episodes'] for v in e['videos']]))
(B/'source_cut_and_black_candidates.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps([x for x in r if x['black_intervals']],ensure_ascii=False,indent=2));print('54 finished')
