from scout_v7 import *
S=json.load(open(OUT/'segments_pending_view.json'))
for s in S:s['evidence_v7']['viewed']=True
ranges=[([0,117,234,340,508,587],0,667),([667,727],667,169),([836],836,106),([942,1022],942,193),([1135],1135,138),([1273],1273,67),([1340],1340,57),([1397],1397,126),([1523,1593,1693],1523,244)]
G=[]
for olds,r,l in ranges:
 seg=[s for s in S if r<=s['record_frame']<r+l]
 assert sum(s['length_frames'] for s in seg)==l
 G.append({'old_record_frames':olds,'record_frame':r,'length_frames':l,'segments':seg,'preserve_audio_absolute_positions':True,'preserve_title_v2_absolute_range':[340,508] if r==0 else None})
assert sum(g['length_frames'] for g in G)==1767
json.dump(G,open(OUT/'groups_v7.json','w'),ensure_ascii=False,indent=2)
fontsmall=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',18)
fonttitle=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',26)
labels=['廊檐入境','笔尖书香','师者迎接','青春入校','师生共读','少年阅读','校名与文脉','朝阳校园','树影光亮','同伴互动','专注目光','自然回应','展旗启程','国旗下敬礼','意气风发','琅琅书声','书页细节','现代教学楼','明亮课堂','抬头求知','书架阅读','墨香阅览','化学探索','飞身扑救','同伴求知','师者温度','人文自然','艺术实践','校园角落','笑容收束']
def overview(sub,cols,cellw,header,name):
 cw=cellw;ch=round(cw*9/16);gap=14;labelh=51;head=70;rows=(len(sub)+cols-1)//cols
 im=Image.new('RGB',(cols*cw+(cols+1)*gap,head+rows*(ch+labelh+gap)+gap),(243,241,235));d=ImageDraw.Draw(im)
 d.text((gap,12),header,font=fonttitle,fill=(38,36,31));d.text((gap,43),'真实源画面 · 尚未套用项目调色 · 旁白与片名绝对位置保留',font=fontsmall,fill=(96,91,82))
 for j,s in enumerate(sub):
  i=S.index(s);x=gap+(j%cols)*(cw+gap);y=head+(j//cols)*(ch+labelh+gap)
  mid=Path(s['evidence_v7']['first_middle_last'][1]['path']);fr=Image.open(mid).resize((cw,ch));im.paste(fr,(x,y))
  d.text((x,y+ch+3),f"{i+1:02d}  {s['record_frame']/25:.2f}–{(s['record_frame']+s['length_frames'])/25:.2f}s  {labels[i]}",font=fontsmall,fill=(40,38,33))
  token=s['name'].split('_Proxy')[0].split('_260')[0].replace('20260924_','').replace('20260921_','')
  d.text((x,y+ch+27),f"{s['path'].split('/')[-3]}/{token}  源{s['in']:.2f}–{s['out']:.2f}s",font=fontsmall,fill=(100,93,80))
 path=OUT/name;im.save(path,quality=94);return str(path)
pre=overview(S[:12],3,600,'v7 开篇重编 · 前26.68秒 · 12镜','前26.68秒_12镜选镜拼图.jpg')
allp=overview(S,5,440,'v7 前70.68秒 · 30镜节奏方案','开篇70秒_30镜选镜总览.jpg')
report={'scope_frames':[0,1767],'fps':25,'old_shots':18,'new_shots':30,'total_seconds':70.68,'duration_range_seconds':[min(s['length_frames'] for s in S)/25,max(s['length_frames'] for s in S)/25],'mean_seconds':1767/25/30,'all_first_middle_last_viewed':True,'retained_v6_source_overlap_count':0,'title_v2_unchanged':[340,508],'contact_sheets':[pre,allp]+[str(OUT/f'选定首中尾_{i:02d}.jpg') for i in range(1,7)],'notes':['第二镜改006/C0206独立源6–8.28秒，笔尖、手指及课本文字清楚；与中段C0206源1–3秒无重叠。第一镜C070为金台书院廊道环境，不含校名；未在此覆盖集团身份标签，17.04秒集团旁白期间为真实文汇校园。','全片原C1336–11.2秒与开篇新C1331–3.12秒不重叠；C211片尾15–18.68秒与开篇1.4–3.52秒不重叠。','自然入校C0001有真实口罩学生，不是无人口罩的摆拍美化；老师C0011已后移到16.08秒避开经过书包完全遮挡。','笔尖与所有人物镜均为真实视频；未生成替代画面。未操作Resolve，未修改音轨。','本次为源素材首中尾视觉审阅，最终调色、片名跨画面可读性与动感请以原生时间线实际输出复核。']}
json.dump(report,open(OUT/'opening_v7_audit.json','w'),ensure_ascii=False,indent=2)
lines=['v7开篇30镜方案：0–1767帧，时长精确70.68秒。常规镜长2.12–2.76秒，平均2.356秒。','12镜构成前26.68秒；片名13.60–20.32秒固定不动，跨C077/C0017/C307三镜。','30个选段全部实看首中尾；已后移迎接老师避开书包遮挡、前移书架男生避开突然看镜头、前移C211避开末尾看镜头，队列改C086避开前景人身遮挡。','基于当前v6全片保留段及两处采访V2补画逐段查重，源区间重叠0；其他v7工作组新源由根代理统一交叉核查。','首镜无小学门匾，不把金台单校冒作集团；集团名旁白期间使用明确文汇中学校园底图。','此文件不含听审或全片播放结论；未操作Resolve。','']
for s in S:lines.append(f"{s['record_frame']:4d} | {s['length_frames']:2d}帧 | {s['path'].split('/')[-3]}/{s['name']} | {s['in']:.2f}–{s['out']:.2f} | {s['intent']}")
(OUT/'开篇重编说明.txt').write_text('\n'.join(lines))
print(json.dumps({'groups':str(OUT/'groups_v7.json'),'overview':allp,'opening':pre,'metrics':report['duration_range_seconds']},ensure_ascii=False))
