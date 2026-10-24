from pathlib import Path
import json, os, subprocess, concurrent.futures, math, re
from PIL import Image,ImageDraw,ImageFont
BASE=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕')
OUT=BASE/'达芬奇剪辑_EP21-25_20261020/画面核验'
OUT.mkdir(exist_ok=True)
FFDIR='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin'
os.environ['PATH']=FFDIR+os.pathsep+os.environ['PATH']
PY='/Users/zc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
LOOK='/Users/zc/.codex/skills/ffmpeg-skill/scripts/look.py'
probes=json.loads((BASE/'达芬奇剪辑_EP21-25_20261020/ffmpeg_skill_probe_EP21-25.json').read_text())
rows=[p for p in probes if p.get('video') and any('/EP'+str(e)+'/' in p['file'] for e in [21,22,23])]
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
def work(p):
    src=Path(p['file']);ep=re.search(r'/EP(\d+)/',str(src))[1]
    folder=OUT/('EP'+ep)/src.stem;folder.mkdir(parents=True,exist_ok=True)
    last=(int(p['video']['nb_frames'])-1)/float(p['video']['fps'])
    mid=math.floor(last)/2
    ts=sorted(set([0.0,mid,last]+[float(t) for t in range(2,math.floor(last)+1,2)]))
    cmd=[PY,LOOK,str(src),'-o',str(folder/'frame.png'),'--width','320','--no-timecode','--json','--timeout','120']
    for t in ts:cmd.extend(['--at',f'{t:.3f}'])
    res=subprocess.run(cmd,capture_output=True,text=True)
    (folder/'look_result.json').write_text(res.stdout)
    (folder/'look_stderr.txt').write_text(res.stderr)
    if res.returncode:raise RuntimeError(src.name+res.stderr[-500:]+res.stdout[-500:])
    pics=[folder/f'frame_{t:.3f}s.png' for t in ts]
    assert all(x.exists() for x in pics),[str(x) for x in pics if not x.exists()]
    cols=4;cw=240;ih=427;ch=457;head=48;nr=math.ceil(len(ts)/cols)
    sheet=Image.new('RGB',(cols*cw,nr*ch+head),(22,22,22));draw=ImageDraw.Draw(sheet)
    label=src.name.replace('女版','NV')
    draw.text((10,6),label+' | '+f'24 fps | last video frame {last:.3f}s',font=font,fill='white')
    for i,(t,fp) in enumerate(zip(ts,pics)):
        im=Image.open(fp).convert('RGB');im.thumbnail((cw,ih));xx=(i%cols)*cw;yy=head+(i//cols)*ch
        sheet.paste(im,(xx+(cw-im.width)//2,yy))
        draw.text((xx+4,yy+ih+3),f'{label}  TC {t:06.3f}s',font=small,fill='white')
    sheet_path=folder/'contact_sheet.png';sheet.save(sheet_path)
    record={'source':str(src),'source_basename':src.name,'fps':p['video']['fps'],'video_frame_count':int(p['video']['nb_frames']),'last_video_frame_seconds':last,'container_duration_seconds':p['duration'],'sample_times_seconds':ts,'frames':[str(x) for x in pics],'contact_sheet':str(sheet_path),'sampling':'start, exact half-integer midpoint, last video frame, every 2 seconds; FFmpeg look.py seek timestamps','visual_review_status':'pending_actual_view'}
    (folder/'sample_manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
    print('DONE',src.name,'frames',len(ts),flush=True)
    return record
records=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    futures=[pool.submit(work,p) for p in rows]
    for f in concurrent.futures.as_completed(futures):records.append(f.result())
records.sort(key=lambda r:r['source'])
(OUT/'EP21-23_抽帧索引.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print('TOTAL',len(records),'files',sum(len(x['frames']) for x in records),'frames',flush=True)

