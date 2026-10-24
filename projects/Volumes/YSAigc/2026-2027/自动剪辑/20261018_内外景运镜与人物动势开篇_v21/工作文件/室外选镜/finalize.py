import json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
M=json.load(open(ROOT/'detail_manifest.json'))+json.load(open(ROOT/'detail_more_manifest.json'))
D=json.load(open('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_学校粗剪/工作文件/footage.json'))
S=json.load(open(ROOT.parent/'live_before_v21.json'))
U={}
for t in S['snapshot']['video']:
 for i in t['items']:
  if i.get('enabled',True):U.setdefault(i['path'],[]).append({'track':t['track'],'start':i['start'],'end':i['end'],'source_in_frame':i['offset'],'source_out_exclusive':i['offset']+i['end']-i['start']})
P=[('004','A001C070',100,160,'室外空镜','红柱长廊平稳横摇','机位完整展示红柱与木格窗；镜头从右侧近柱向左侧廊尽头缓摇，前中后连续清晰，横向运动明确；可直接接室内门框。底部边角偶见红色消防箱，主构图不受影响。','A'),('004','A001C048',75,135,'室外空镜','古建庭院与树冠广角缓摇','前景粗树干、上部树冠、远处院落形成纵深；镜头轻向上及横向缓摇，有视差。广角有桶形变形、地平线略倾，建议只用2.4秒而非大幅数字再运动；人物很小，不作为主体动作。','A-'),('006','C0327',300,360,'室外空镜','教学楼庭院全景轻升摇','完整楼宇包围校园庭院，大景别、微升摇，人物在底部远处走动；无遮挡或失焦，广角自然透视明显。可承担现代校区转场，与古建形成变化。','B+'),('007','C0002',375,435,'真人行动','学生队列正面行进','多列学生从远处向近处行走，手臂和步伐自然，画面连续清晰，人物出入左右边缘属正常场面运动，没有遮挡全画面；可用于迈向未来／青春人文。','A'),('007','C0007',525,575,'真人行动细节','脚步和晨光长影','横向成组脚步与长影明确移动，镜头轻下摇，从裤腿转向长影；身体上半部不在构图内是脚步细节景别，可卡在鼓点上作为1.6–2秒动作插镜，不作为完整人物群像。','A'),('007','C0125',125,185,'真人行动','低机位学生群体迎面走来','多位学生从远到近前行，完整身体和上方蓝天保留，构图宽；近景人物行进穿出画边，不遮挡中后排；校园纪实感较强，便装与校服混合。','A-')]
R=[]
for g,n,a,b,k,desc,qa,rank in P:
 x=next(x for x in M if x['group']==g and x['name'].startswith(n+'_'));p=next(x for x in D if x['group']==g and x['name'].startswith(n+'_'))
 probe_file=ROOT/(g+'_'+n+'_probe.json')
 if not probe_file.exists():
  z=subprocess.run(['/Users/xuan/.local/share/promo-audio/venv/bin/python','/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/probe.py',x['path'],'--json'],capture_output=True,text=True,check=True);probe_file.write_text(z.stdout)
 r={**x,'source_in_frame':a,'source_out_frame_exclusive':b,'duration_frames':b-a,'duration_seconds':(b-a)/x['fps'],'kind':k,'description':desc,'actual_visual_qa':qa,'rank':rank,'fresh_before_v21_usage':U.get(x['path'],[]),'source_unused_in_fresh_timeline':x['path'] not in U,'probe':str(probe_file),'reviewed_frame_times_sec':[x['source_in_frame']/x['fps']+v*.36 for v in range(9)]};R.append(r)
(Root:=ROOT/'最优六镜_室外空镜与人物行动_v21.json').write_text(json.dumps({'baseline':str(ROOT.parent/'live_before_v21.json'),'total_newly_scanned_source_thumbnails':len(json.load(open(ROOT/'scan_manifest.json'))),'continuous_checks_count':19,'selection':R,'rejected':[{'source':'007/C0116_Proxy.mov','reason':'5–8秒连续失焦；12–15秒连续接近且软焦，不用于开篇'},{'source':'007/C0003_Proxy.mov','reason':'5–8秒人物明显软焦，虽逆光好看但不是本轮清晰动势最优'},{'source':'004/A001C049_260921K6_Proxy.mov','reason':'已用且与A001C048景别内容接近'},{'source':'002/A002C018_260924AP_Proxy.mov','reason':'灰天广角变形明显，空场缺乏人物，优先级低于古建长廊'}]},ensure_ascii=False,indent=2))
F=ImageFont.load_default(size=16);sheet=Image.new('RGB',(1440,2*310),(12,16,20));d=ImageDraw.Draw(sheet)
for j,r in enumerate(R):
 im=Image.open(r['contact_sheet']);im=im.crop((480,298,960,568));xx=(j%3)*480;yy=(j//3)*310;sheet.paste(im,(xx,yy));d.text((xx+4,yy+271),r['group']+'_'+r['name'].split('_')[0]+f" [{r['source_in_frame']},{r['source_out_frame_exclusive']})",font=F,fill='white');d.text((xx+4,yy+291),'25fps / NEW SOURCE / '+r['rank'],font=F,fill='yellow')
sheet.save(ROOT/'最优六镜_画面概览.jpg',quality=94)
print(Root);print([(r['name'],r['source_unused_in_fresh_timeline']) for r in R])
