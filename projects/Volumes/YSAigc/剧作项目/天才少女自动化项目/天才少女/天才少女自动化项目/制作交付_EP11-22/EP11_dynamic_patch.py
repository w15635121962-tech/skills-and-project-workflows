from pathlib import Path
import json,re,hashlib

out=Path(__file__).parent/'EP11'
groups=json.loads((out/'EP11_平台填充.json').read_text())
ops=[]
def change(g,old,new):
    assert old in g['prompt'],(g['id'],old)
    n=g['prompt'].count(old)
    for _ in range(n): ops.append({'group':g['id'],'old':old,'new':new})
    g['prompt']=g['prompt'].replace(old,new)

g=groups[3]
change(g,'景别循环：MCU R1左前侧略低 → CU R2左前侧平角 → MS 桌前左侧斜俯 → CU 桌前R1四分之三平角 → ECU 桌前中性俯角','景别循环：MCU前跟 → CU短摇 → MS侧移 → CU推至眼部ECU → CU屏幕右移')
cams=[
('前移跟随坐直',50,1.20,2.8,'Xavier前收触发前跟15cm，1秒到位、0.5秒稳胸上；左轴侧跟焦脸','首句中切听者，连续声轨不断'),
('向下短摇',85,1.40,2.8,'回看终端触发下摇6度，0.7秒停于锁骨近景；焦点副队长眼睛','听者落手切队长'),
('桌前向右横移',35,1.65,4.0,'沿桌前左轴侧右移30cm/3秒，匀速跟三人操作层；不越屏后','命令结束切无声压力'),
('推近右眼大特写',100,1.35,2.8,'微距；命令结束触发推轨0.95m至0.55m，2.8秒推、0.7秒落定；CU收为右眼ECU；跟焦，不越轴','眼睑压紧切封堵证据'),
('屏前向右横移',65,1.65,4.0,'屏距0.8m，右移12cm/2.4秒、0.6秒止于弱支路；屏面清楚','弱支路切Elena选择')]
for i,(move,lens,h,t,camera,cut) in enumerate(cams):
 s=g['shots'][i]
 oldhead=re.search(r'【shot '+str(i+1)+r'｜[^\n]+',g['prompt']).group()
 size='CU→ECU' if i==3 else ('CU' if i==4 else s['size'])
 change(g,oldhead,f"【shot {i+1}｜{s['name']}｜{size}｜{s['angle']}｜{move}｜{lens}mm等效｜duration: {s['duration']:.1f}s】")
 oldcam=g['prompt'].split(oldhead if oldhead in g['prompt'] else f'【shot {i+1}｜')[1].split('镜头：')[1].split('\n')[0]
 change(g,'镜头：'+oldcam,f'镜头：9:16；高约{h:.2f}m；{lens}mm等效；T{t:.1f}；{camera}。切点：{cut}。')
 s.update(size=size,lens=lens,height=h,t=t,camera_movement=move,camera_path=camera,cut=cut)
change(g,'Xavier脸在左中占画高50%，远右边仅','起幅Xavier锁骨CU在左中；落幅裁右眉、右眼、鼻梁和耳麦边。起幅右边仅')
change(g,'副队长虚焦肩宽不超过画宽10%，属于R2本人；R3与R4—R6画外。主屏边缘在下部，桌前半空间不跨轴。','副队长虚肩占宽不到10%，推近后出画，不换座；R3—R6画外。单眼清楚，不遮瞳孔、不越轴。')
change(g,'主体左中，Xavier看主屏，副队长与队员01看各自屏，均避开镜头。','横移保持Xavier左、副队长中、队员01右，均看本人屏；R3落耳麦接切点，桌沿产生视差。')
change(g,'重心左中脸，Xavier眼神落右下主屏，听者看自己的屏。','重心脸→右眼；Xavier看右下主屏，副队长起幅看R2屏，瞳孔避光轴。')
change(g,'从Xavier视線接屏下部再向右支路，下一组Elena选择承接。','视线接屏，三层绿墙向左滑、弱支路落右中；左蓝右红固定，接Elena选择。')
change(g,'低：固定观察；人物动作按所写触发发生。','人物执行起终态；相机按逐镜路径移动。')
change(g,'中：上身前收，椅子不横移。','人物上身前收15cm；相机同向跟15cm，椅子不横移。')

g=groups[4]
change(g,'景别循环：CU 左前侧平角 → ECU 中性桌前高俯 → CU 屏前左侧略俯 → MS 桌前正面略低','景别循环：CU推至眼部ECU → ECU贴键横移 → CU沿屏右移 → MS向下跟拍')
cams=[
('推近右眼大特写',100,1.30,2.8,'100mm微距等效；识别弱支路触发推轨，距脸0.95m至0.55m；前3秒匀速推进、末1秒读取右眼偏移；CU收为单眼ECU，跟焦右眼与镜框，不变焦','支路锁定切右食指触键'),
('贴键向右跟移',85,1.70,4.0,'键盘上方短滑轨跟食指向右移4cm，前0.6秒同向跟随、后0.4秒停在确认键受压位置；微距持续跟焦指腹，机位不穿手','触底动作切节点结果，下一镜不是再按一次'),
('沿屏向右横移',65,1.50,4.0,'B3屏前向右横移6cm，1.1秒到右节点、末0.4秒读取绿转红；屏距约0.8m、屏面保持清楚，左蓝右红不翻转','绿转红结果切Elena与手回位'),
('向下俯摇跟手回位',50,1.25,4.0,'桌前正面略低，机距建议2.5m；右手回弹触发俯摇8度，前2.5秒从脸与屏移向手和键盘、末1秒稳住腰上MS；焦平面涵盖脸和手，蓝桌沿始终可辨','路径持续推进切中央解说员识别反击')]
for i,(move,lens,h,t,camera,cut) in enumerate(cams):
 s=g['shots'][i]
 oldhead=re.search(r'【shot '+str(i+1)+r'｜[^\n]+',g['prompt']).group()
 size='CU→ECU' if i==0 else s['size']
 oldcam=g['prompt'].split(oldhead)[1].split('镜头：')[1].split('\n')[0]
 change(g,oldhead,f"【shot {i+1}｜{s['name']}｜{size}｜{s['angle']}｜{move}｜{lens}mm等效｜duration: {s['duration']:.1f}s】")
 change(g,'镜头：'+oldcam,f'镜头：9:16；机高建议{h:.2f}m；{lens}mm等效；T{t:.1f}；{camera}。切点：{cut}。')
 s.update(size=size,lens=lens,height=h,t=t,camera_movement=move,camera_path=camera,cut=cut)
change(g,'Elena脸中上、锁骨裁切占画高55%，屏的虚化边框在左下；B3固定座位、比赛耳麦和眼镜不变，Madison左后与Silas右后均画外；机距1.6m在桌前左半空间。','起幅Elena锁骨近景在中上，落幅只裁右眉、右眼、鼻梁与透明镜框，单眼约占画宽35%；耳麦边仍可辨，无完整头脸。B3坐姿不变，Madison左后、Silas右后画外；屏边因收幅退出，桌前左轴侧不变。')
change(g,'右腕受桌面支撑、食指从键区移约4cm，悬停半拍后下压单键到触底；键帽下降约2mm，切在触底约70%动作，不多键乱敲。','接上镜已锁定支路；右腕压桌、食指向确认键移4cm，相机同向跟；只下压此键一次至约2mm，切在触底70%阶段，不多键乱敲。')
change(g,'眼睛接力到画中下指尖，动作向下，归属Elena清楚。','右眼接力到下中指尖；食指向右抵确认键后下压，横移制造邻键视差；仅Elena黑袖右手操作。')
change(g,'重心中上眼睛→中下屏，路径与右侧破口相连；眼神无镜头对视。','俯摇由中上眼睛落中下右手回位，屏中唯一路径仍向右侧破口推进；Elena看B3屏路径，不抬眼看镜头。')
change(g,'低：固定观察；人物动作按所写触发发生。','人物按起终态执行；相机按本镜路径移动，禁止全组锁定机位。')
change(g,'低：单键一次受力。','手指右移后只按一次；相机贴键同向跟移4cm。')

for g in groups[3:5]:
 original=(out/(g['id']+'.txt')).read_text()
 archive=out/(g['id']+'_动态修订前.txt')
 if not archive.exists(): archive.write_text(original)
 assert re.findall(r'音频：([^\n]+)',original)==re.findall(r'音频：([^\n]+)',g['prompt'])
 assert g['durations']==([1.5,1,3,3.5,3] if g['id']=='G04' else [4,1,1.5,3.5])
 assert len(g['prompt'])<4900,(g['id'],len(g['prompt']))
 (out/(g['id']+'.txt')).write_text(g['prompt'])
 # 回填镜头数据，避免结构化稿与提示词失配。
 pieces=re.split(r'【shot \d+｜[^\n]+\n',g['prompt'])[1:]
 for s,p in zip(g['shots'],pieces):
  for key,label,nextlabel in [('frame','画面','起态—路线—终态'),('action','起态—路线—终态','视觉引导'),('flow','视觉引导','微表演'),('motion','运动强度','负面提示词')]:
   s[key]=p.split(label+'：',1)[1].split('\n'+nextlabel+'：',1)[0]
 (out/(g['id']+'_动态修订记录.json')).write_text(json.dumps({'source':'英文原剧本行294—300、台词分稿第11章、已批准G04/G05','scope':'运镜、景别及相应构图与动线','frozen':'人物、世界站位、台词及连续声轨、时长、镜数、灯光、道具动作链','shots':g['shots'],'dialogue_unchanged':True,'platform':'待回读','generation':'待提交'},ensure_ascii=False,indent=2))
(out/'G04-G05_动态修订操作.json').write_text(json.dumps(ops,ensure_ascii=False,indent=2))
(out/'EP11_平台填充.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2))
md=out/'EP11_完整FormatC_V2.6.md'
text=md.read_text()
for g in groups[3:5]: text=text.replace((out/(g['id']+'_动态修订前.txt')).read_text(),g['prompt'])
md.write_text(text)
print(json.dumps({'groups':{g['id']:len(g['prompt']) for g in groups[3:5]},'operations':len(ops),'dialogue_unchanged':True},ensure_ascii=False))
