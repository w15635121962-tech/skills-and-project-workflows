import av,json,subprocess,sys
import numpy as np
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent
rough=json.load(open(O/'rough_scan.json'))
notes=[('C0166_Proxy',230,300,'室内空镜_主推','班牌与教室门口前景，镜头侧移后露出明亮纵深走廊','真实横移与转向展开，前后景视差明显；末端进入完整透视','原片稍偏暗，温和抬中间调即可；比 C0150/C0151 走廊亮','优先，可在室外大景后接此镜，完成从校园到教室的空间进入'),('A001C214_260921LC_Proxy',20,65,'科学空间空镜_主推','机器人模型近景，后景为科技教室','镜头在机器人外壳与线路前轻横移，有前景与黑板视差，画面从清晰模型开始','此段在后续明显拉焦之前，模型清楚；不是宽幅空教室全景','优先，科学气息比单独奖牌墙更鲜活'),('A003C132_2609241J_Proxy',300,370,'真人动作_主推','隔书架看女生阅读，书架前景形成框中框','女生翻页，翻开后继续读；镜头微移，书脊和人物有细小视差','前景书架刻意虚化，女生脸部与眼神清楚','优先，可用 2.8 秒接书页或班牌，节拍在人手翻页处'),('A001C328_26092194_Proxy',140,200,'真人动作_主推','学生双手转动并拆开红黄拼搭模型的近景','模型从旋转观察到两手分开，动作明确；原生摄影机基本稳定','构图为有意手部细节，未误裁人物；无需再次大幅数字推近','优先，与科技模型空镜接成 科学空间到动手创造'),('A002C039_2609246R_Proxy',25,85,'真人动作_主推','男生向上提起滴管观察，身边同学露出笑容','抬手提起滴管并观察，摄影机轻微跟随；两个人表情自然','避免后续更靠后的原时间线已用区间 170–237','优先，手部动作提供节奏，科学实验也有青春温度'),('A003C139_260924UW_Proxy',60,115,'物件动态插镜_可选','低机位书页与圆形灯光散景','书页从低处掀起掠过镜头，圆灯光斑保持，页边清楚','浅景深为创作选择，文字不需要可读；不是镜头整体失焦','可选，做 2.2 秒运动桥，勿与上一女生翻书镜同时连续堆叠'),('C0151_Proxy',700,760,'室内空镜_备选','对称学校长廊与门框，远处窗口透光','前推形成门框与地面反光视差，运动真实非后期静图缩放','原片明显偏暗，画面肃静；不宜作为强开篇主打第一镜','仅需第二组宽幅室内空镜时用，主推 C0166，勿连放两条走廊')]
snap=json.load(open('/Volumes/YSAigc/2026-2027/自动剪辑/20261018_开篇三素材与强配乐_v20/工作文件/final_native_snapshot_v20.json'))
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
rows=[]
for n,st,en,cat,scene,mv,warning,rec in notes:
 r=next(x for x in rough if Path(x['path']).stem==n);p=Path(r['path']);c=av.open(str(p));s=c.streams.video[0];fps=float(s.average_rate);indices=np.rint(np.linspace(st,en-1,9)).astype(int).tolist();c.seek(int(st/fps/s.time_base),stream=s,backward=True)
 ims=[];g=[];actual=[]
 for f in c.decode(s):
  idx=round(f.time*fps)
  if idx<st:continue
  if idx>=en:break
  rgb=f.to_image();gray=np.asarray(rgb.resize((192,108)).convert('L'),dtype='float32');g.append(gray)
  if idx in indices:
   target=O/(n+'_selected');target.mkdir(exist_ok=True);rgb.save(target/f'{idx:05d}.jpg',quality=95);actual.append(idx);rgb.thumbnail((640,360));ims.append(rgb.copy())
 sheet=Image.new('RGB',(1920,1158),(12,12,12));d=ImageDraw.Draw(sheet)
 for i,(im,idx) in enumerate(zip(ims,actual)):
  x=(i%3)*640;y=(i//3)*386;sheet.paste(im,(x,y));d.text((x+7,y+362),f'{n}  source fr {idx}  {idx/fps:.2f}s',font=font,fill='white')
 dest=O/(n+'_精选连续9帧.jpg');sheet.save(dest,quality=92);c.close()
 used=[]
 for tr in snap['video']:
  for it in tr['items']:
   if it['path']==str(p):used.append({'track':tr['track'],'timeline_start':it['start'],'timeline_end':it['end'],'source_in':it['offset'],'source_out_exclusive':it['offset']+it['end']-it['start'],'enabled':it['enabled']})
 row={'path':str(p),'source_fps':fps,'source_in':st,'source_out_exclusive':en,'duration_seconds':(en-st)/fps,'category':cat,'scene':scene,'movement':mv,'caveat':warning,'editorial_recommendation':rec,'contact_9':str(dest),'actually_viewed_source_frames':actual,'all_frames_decoded':len(g),'consecutive_frame_motion_MAD_mean':float(np.mean([np.abs(a-b).mean() for a,b in zip(g,g[1:])])),'existing_v20_uses':used,'selected_range_overlap_existing':any(max(st,u['source_in'])<min(en,u['source_out_exclusive']) for u in used),'whole_source_unused':len(used)==0}
 # Official skill probe for each selected source.
 cmd=[sys.executable,'/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/probe.py',str(p),'--json']
 res=subprocess.run(cmd,capture_output=True,text=True);(O/(n+'_probe.json')).write_text(res.stdout);row['official_probe_exit_code']=res.returncode
 rows.append(row)
(O/'室内运镜与真人动作_最终选镜_v21.json').write_text(json.dumps({'scope':'003 004 006 全量既有缩略图重新视觉检索，并额外查 001 002；18 个新候选源文件重新9帧抽检；7 个精确区间全部逐帧解码验证。只离线源素材工作，未连接 Resolve。','preferred_order':['C0166_Proxy','A001C214_260921LC_Proxy','A003C132_2609241J_Proxy','A001C328_26092194_Proxy','A002C039_2609246R_Proxy'],'shots':rows},ensure_ascii=False,indent=2))
print(json.dumps([{'name':Path(r['path']).stem,'in':r['source_in'],'out':r['source_out_exclusive'],'decoded':r['all_frames_decoded'],'probe':r['official_probe_exit_code'],'overlap':r['selected_range_overlap_existing']} for r in rows],ensure_ascii=False))
