import av,json,sys,subprocess
import numpy as np
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码');O=Path(__file__).parent;V=O.parent
snap=json.load(open(V/'live_before_v22.json'))['snapshot'];font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',21)
plans=[('A003C200',508,544,'女生拍手互动','手臂起→拍到对方掌心→退回，36帧保留完整一轮拍掌。','拍掌接触点约源522–527帧，可落音乐短重拍。'),('A003C221',1090,1126,'女生抬眼露出笑容','低头带笑→抬头睁眼→看向前方微笑，动作完整。','留在阅读或同伴互动后，保持人文温度；不做连续无意义表情堆叠。'),('A001C338',125,161,'特色沙画手部创作','指尖沿沙画轮廓拨沙，右手抬离、左手完成局部细化，非静物。','只出现一条手作细节，避免与积木手部连放。'),('A003C139',60,96,'翻书页运动过门','纸页从平放到扬起，掠过圆形散景后落回，浅景深为有意创作。','1.44秒接阅读女生即可，不再人为快放。'),('C0125_Proxy',568,622,'群体向前走的低机位收束','多人自然迎面走来，衣摆、手臂与前后排持续运动，视野开阔。','2.16秒留完整脚步作为24.52–26.68秒段落收束；学生服装有便装与校服混合。')]
rows=[]
for n,st,en,scene,movement,edit in plans:
 p=next(R.rglob(n+'*mov'));c=av.open(str(p));s=c.streams.video[0];fps=float(s.average_rate);c.seek(int(st/fps/s.time_base),stream=s,backward=True);idxs=np.rint(np.linspace(st,en-1,9)).astype(int).tolist();ims=[];actual=[];gs=[]
 for f in c.decode(s):
  i=round(f.time*fps)
  if i<st:continue
  if i>=en:break
  im=f.to_image();gs.append(np.asarray(im.resize((192,108)).convert('L'),dtype='float32'))
  if i in idxs:
   q=O/(p.stem+'_selected');q.mkdir(exist_ok=True);im.save(q/f'{i:05d}.jpg',quality=94);im.thumbnail((640,360));ims.append(im);actual.append(i)
 sheet=Image.new('RGB',(1920,1158),(12,12,12));d=ImageDraw.Draw(sheet)
 for j,(im,idx) in enumerate(zip(ims,actual)):
  x=j%3*640;y=j//3*386;sheet.paste(im,(x,y));d.text((x+8,y+362),f'{p.stem} source fr {idx}',font=font,fill='white')
 contact=O/(p.stem+'_最终动作连续9帧.jpg');sheet.save(contact,quality=92);c.close();uses=[]
 for tr in snap['video']:
  for it in tr['items']:
   if it['path']==str(p):uses.append({'track':tr['track'],'timeline_in':it['start'],'timeline_out':it['end'],'source_in':it['offset'],'source_out_exclusive':it['offset']+it['end']-it['start'],'enabled':it['enabled']})
 overlap=[u for u in uses if max(st,u['source_in'])<min(en,u['source_out_exclusive'])];assert not overlap,(p,overlap)
 probe=subprocess.run([sys.executable,'/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/probe.py',str(p),'--json'],capture_output=True,text=True);(O/(p.stem+'_probe.json')).write_text(probe.stdout)
 rows.append({'path':str(p),'source_fps':fps,'source_in':st,'source_out_exclusive':en,'duration_frames':en-st,'duration_seconds':(en-st)/fps,'scene':scene,'movement_and_action':movement,'editing_note':edit,'decoded_frame_count':len(gs),'actual_review_frames':actual,'contact_9':str(contact),'consecutive_motion_MAD_min':float(min(np.abs(a-b).mean() for a,b in zip(gs,gs[1:]))),'existing_source_uses_in_fresh_v22_parent':uses,'overlap_with_entire_fresh_parent':False,'whole_source_unused':len(uses)==0,'official_probe_exit_code':probe.returncode})
x={'status':'all five source segments extracted, pending visual final check','baseline':str(V/'live_before_v22.json'),'shots':rows,'rhythm_advice':['首镜用开阔的人群动作或强透视运镜落音乐重拍，主镜保持1.35–1.85秒。','用一组完整拍掌、抬眼微笑和翻页做33–36帧短插镜，每次切换都落到可读动作。','文化素材三条保留原生摄影运动，避免照片墙连排。','书页接阅读，沙画与模型手作分开，避免同类细节连续堆叠。','最后C0125留2.16秒向前走作为收束，旁白与音乐保持原时钟。']}
p=O/'五条新增完整动作_选镜_v22.json';p.write_text(json.dumps(x,ensure_ascii=False,indent=2));print(str(p));print(json.dumps([{'name':Path(r['path']).stem,'in':r['source_in'],'out':r['source_out_exclusive'],'duration':r['duration_seconds']} for r in rows],ensure_ascii=False))
