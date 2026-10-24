from scout_opening_v8 import *
from copy import deepcopy
P=json.load(open(OUT.parent/'base_plan_v7.json'));B={s['record_frame']:s for s in P['shots']}
choices=[(561,'003','A003C074',.6,'由坐姿凝视换为学生起身、抬头回应的真实动作；不额外给人物身份，不把不同课堂当同一连续回答。'),(614,'006','C0243',2.0,'由坐姿微笑换为手指固定展示卡片，按住到松手的动作完整可见；仅描述学习展示，不将卡片冒称梦想或许愿内容。'),(1204,'003','A003C123',2.0,'由固定机位低头阅读换为图书馆原生横移机位，书架、阅览者与纵深形成真实视差，不额外叠加运镜。')]
R=[]
for rec,g,t,ins,intent in choices:
 a=lookup(g,t);old=B[rec];s=deepcopy(old);l=s['length_frames'];out=round(ins+l/25,6)
 s.update(path=a['path'],name=a['name'],fps=float(a['fps']),**{'in':ins,'out':out},source_start_frame=round(ins*a['fps']),source_count_frames=round(l*a['fps']/25),source_out_exclusive=out,in_requested=ins,revision_v8=True,intent=intent,log=True,is_photo=False)
 s['replaces_v7']={'path':old['path'],'in':old['in'],'length_frames':l,'intent':old['intent']}
 ev=[]
 for lab,sec in zip(['首','中','尾'],[ins,ins+(l//2)/25,out-.04]):
  fp=OUT/f'最终_R{rec}_{lab}_{sec:.2f}s.jpg';frame(a['path'],sec).save(fp,quality=94);ev.append({'label':lab,'time':round(sec,4),'path':str(fp)})
 s['evidence_v8']={'first_middle_last_viewed':True,'frames':ev,'contact_sheet':str(OUT/'选定三处动态_源首中尾.jpg'),'source_overlap_with_full_v7':[]}
 other=[x for x in P['shots'] if x['record_frame']!=rec]
 for key in ['interview_overlays_v6','interview_overlays_v7']:
  overlays=P.get(key,[])
  if isinstance(overlays,list):other+=overlays
 for x in other:
  if x.get('path')==s['path']:
   z=min(out,x['in']+x['length_frames']/25)-max(ins,x['in'])
   if z>.001:s['evidence_v8']['source_overlap_with_full_v7'].append({'record_frame':x['record_frame'],'seconds':z})
 assert not s['evidence_v8']['source_overlap_with_full_v7']
 assert out<=a['duration']
 R.append(s)
json.dump(R,open(OUT/'source_replacements_v8.json','w'),ensure_ascii=False,indent=2)
M=[]
spec=[(0,'push',1,1.03,'红柱廊道有纵深和边缘余量；固定中心缓推强调进入校园，匹配根代理已验证的首镜1→1.03原型。'),(287,'push',1,1.025,'书架男生为稳定中景，主要脸与书本在画内，2.5%推进增加阅读专注；保留原翻阅动作。'),(396,'pull',1.025,1,'明亮教学楼无人脸与窄校牌，轻拉远让空间展开；只变主画面，不改变固定片名V2。'),(452,'pull',1.03,1,'树光与楼宇没有人物边缘风险，3%轻拉远作为片名末幅呼吸；保留原树叶和风的运动。'),(836,'push',1,1.025,'朗读女生头肩与书本位于画内并有余量，2.5%微推强调书声与专注，保留嘴部和手部自然动作。'),(1135,'push',1,1.025,'书架间女生与书本留有余量，2.5%固定中心缓推，接后镜图书馆真实横移形成变化。'),(1460,'pull',1.025,1,'女教师面部与学生关系是主体，轻拉远逐步显露交流空间，避免推进挤压手部和前景学生。'),(1645,'push',1,1.03,'树叶前景到红柱窗棂有层次，固定中心3%推进营造校园角落的可进入感；不加漂移。'),(1706,'push',1,1.025,'自然笑容与听课关系在安全区内，2.5%轻推收束开篇；保持真实微表情，不放大到面部特写。')]
for r,k,ss,es,why in spec:M.append({'record_frame':r,'kind':k,'start_size':ss,'end_size':es,'center_start':[.5,.5],'center_end':[.5,.5],'reason':why})
json.dump(M,open(OUT/'motion_suggestions_v8.json','w'),ensure_ascii=False,indent=2)
# A real-source framing reference; no generated or simulated replacement images.
font2=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',20)
im=Image.new('RGB',(1848,3*394+70),(244,241,235));d=ImageDraw.Draw(im)
d.text((16,10),'v8 开篇9镜轻运动建议｜真实源构图，未模拟效果',font=font2,fill=(35,32,28))
d.text((16,38),'全部固定中心（0.5,0.5），推进/拉远2.5%–3%，其余21镜不额外叠加运动',font=font2,fill=(100,92,80))
for i,m in enumerate(M):
 s=B[m['record_frame']];f=frame(s['path'],s['in']+(s['length_frames']//2)/25).resize((600,338));x=12+i%3*612;y=70+i//3*394;im.paste(f,(x,y));d.text((x,y+340),f"R{m['record_frame']}  {m['record_frame']/25:.2f}s  {m['kind']} {m['start_size']:.3f}→{m['end_size']:.3f}",font=font2,fill=(40,36,31));d.text((x,y+365),s['name'].split('_Proxy')[0],font=font2,fill=(110,100,85))
im.save(OUT/'九镜轻运动_真实源构图.jpg',quality=94)
report={'source_replacement_count':3,'motion_count':9,'scope_frames':[0,1767],'unchanged_total_shots':188,'unchanged_total_frames':11507,'unchanged_total_seconds':460.28,'narration_and_v2_untouched':True,'source_overlap_with_full_v7':0,'replacement_records':[s['record_frame'] for s in R],'motion_records':[m['record_frame'] for m in M],'rejected':['006/C0240源17–19.44在中间甩动模糊、右侧人物逼近边缘，弃用。','006/C0273源0.4–2.52从头到尾举手停住，不作为举手动作完成段。','003/C139/C140仍不使用虚焦翻页。','R782升旗队列源中点存在原生横移模糊，保持原样，不额外叠加推进。'],'verification_scope':'已实看三个精确替换区间首中尾；额外运动仅为建议，最终平滑性与裁切须由根代理原生时间线连续输出复核。未操作Resolve。'}
json.dump(report,open(OUT/'opening_v8_audit.json','w'),ensure_ascii=False,indent=2)
print(json.dumps({'replacements':str(OUT/'source_replacements_v8.json'),'motion':str(OUT/'motion_suggestions_v8.json'),'counts':[len(R),len(M)],'overlap':0},ensure_ascii=False))
