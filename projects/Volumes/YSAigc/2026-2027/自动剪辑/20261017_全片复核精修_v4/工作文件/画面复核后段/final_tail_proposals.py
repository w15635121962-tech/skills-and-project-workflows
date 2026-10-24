from pathlib import Path
import concurrent.futures,json,subprocess
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent
B=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码')
P=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_旁白精修/工作文件/narrative_edit_plan.json')
old=json.loads(P.read_text())
specs=[
 (63,5901,116,'004/Proxies/A001C072_26092118_Proxy.mov',1.0,'小学课堂，学生举手，教师在讲台上讲解','去除236.04秒的同源小学楼重复空镜；保留明确小学阶段的课堂。',1),
 (75,7211,93,'004/Proxies/A001C318_260921YB_Proxy.mov',1.0,'特色手工课，学生动手、教师俯身指导','去除与276.36秒重复且源素材重叠的奖杯横移；用实际课程行动解释特色兴校。',2),
 (79,7610,118,'006/Proxies/C0252_Proxy.mov',1.0,'教师讲解，手势舒展，身后语文学科板书','师资段与81镜一起打破连续17.04秒资料照，保留78师徒结对和80专题研讨作证据。',3),
 (81,7840,95,'006/Proxies/C0288_Proxy.mov',1.0,'年轻教师在数学课堂讲解','去掉P11跨校培训合影的第二次重复；与79镜不同教师、不同学科视角。',3),
 (85,8220,64,'004/Proxies/A001C092_2609218H_Proxy.mov',3.4,'升旗手展旗动作','原2–4.56秒主要站立，动作刚开始即切；延后1.4秒让展旗展开。实际动作不是少先队敬礼。',4),
 (92,8768,102,'007/Proxies/C0067_Proxy.mov',4.0,'优秀集体表彰，学生持证书领奖','去除第44届科创获奖照片的二次重复，换另一类真实表彰成果。',5),
 (102,9627,125,'006/Proxies/C0174_Proxy.mov',1.0,'教师与全班学生互动的课堂全景','去掉P11跨校培训合影的第三次重复，用真实师生课堂呈现优质办学和教育生态。',6),
 (106,10056,106,'004/Proxies/A001C074_260921JH_Proxy.mov',1.0,'小学教师讲课，红色校服小学生听讲','去掉402.24秒与98.12/174.60/236.04同源重复的彩窗小学楼，用明确小学课堂体现贯通与融合。',7),
 (110,10492,130,'007/Proxies/C0103_Proxy.mov',5.0,'表彰典礼师生群像，学生持证书与教师同框','旧12–17.20秒为主席台前走人、空桌居中；换真实师生集体面孔回应贡献文汇力量。',8),
]

def one(spec):
 idx,record,frames,path,source_in,subject,reason,rec=spec
 source=B/path
 existing=next(s for s in old['shots'] if s['record_frame']==record)
 assert existing['length_frames']==frames
 used=[s for s in old['shots'] if s['path']==str(source) and s['record_frame']!=record]
 # Every fresh file is unused in the old full plan; the one same-file change is the flag action.
 assert not used,(source,used)
 duration=frames/25;times=[source_in+.04,source_in+duration/2,source_in+duration-.08]
 args=['python3','/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/look.py',str(source),'-o',str(O/f'最终建议_{record}.png'),'--no-timecode','--json']
 for t in times:args+=['--at',f'{t:.3f}']
 x=subprocess.run(args,capture_output=True,text=True);(O/f'最终建议_{record}.log.json').write_text(x.stdout)
 if x.returncode:raise RuntimeError(x.stdout+x.stderr)
 result=json.loads(x.stdout)
 return {'recommendation_id':rec,'original_v2_index':idx,'record_frame':record,'record_seconds':record/25,'length_frames':frames,'duration_seconds':duration,'path':str(source),'in':source_in,'out':source_in+duration,'subject':subject,'reason':reason,'source_frames':result['outputs'],'source_frame_times':times,'source_used_elsewhere_in_old_v2':False,'replace_path':existing['path'],'replace_in':existing['in'],'identity_caution':'小学课堂只能标为小学阶段/教学实景；不能据红校服独自证明它是文汇小学。' if idx in [63,106] else None}

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:results=list(ex.map(one,specs))
font=ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc',20)
for base in range(0,len(results),3):
 subset=results[base:base+3];im=Image.new('RGB',(1536,len(subset)*345),(22,25,28));dr=ImageDraw.Draw(im)
 for row,c in enumerate(subset):
  y=row*345;dr.text((6,y+2),f"记录帧{c['record_frame']}  {c['record_seconds']:.2f}s  {Path(c['path']).name}  源{c['in']:.2f}–{c['out']:.2f}",font=font,fill='white')
  for col,f in enumerate(c['source_frames']):
   pic=Image.open(f).convert('RGB');pic.thumbnail((508,286));im.paste(pic,(col*512,y+32));dr.text((col*512+6,y+317),f"源 {c['source_frame_times'][col]:.3f}s",font=font,fill='white')
 im.save(O/f'最终建议首中末_{base//3+1:02d}.jpg',quality=90)
(O/'tail_change_proposals.json').write_text(json.dumps({'scope_seconds':[236.04,460.28],'position_key':'record_frame','source_plan':str(P),'recommendation_count':8,'patch_count':len(results),'patches':results,'constraints':{'preserve_full_narration':True,'preserve_total_frames':11507,'fps':25,'audio_changes':False},'status':'review suggestions only; no changes applied'},ensure_ascii=False,indent=2))
print('ready',len(results))
