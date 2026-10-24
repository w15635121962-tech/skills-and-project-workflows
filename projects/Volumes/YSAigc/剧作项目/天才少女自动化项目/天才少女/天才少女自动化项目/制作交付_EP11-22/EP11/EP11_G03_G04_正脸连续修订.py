from pathlib import Path
import json,re,shutil,hashlib
root=Path(__file__).parent
p=root/'EP11_平台填充.json';groups=json.loads(p.read_text());ops=[]
backup=root/'G03_G04_正脸修订前';backup.mkdir(exist_ok=True)
for f in ['G03.txt','G04.txt','EP11_平台填充.json','EP11_完整FormatC_V2.6.md']:shutil.copy2(root/f,backup/f)
def change(g,old,new):
 assert g['prompt'].count(old)==1,(g['id'],old[:70],g['prompt'].count(old))
 g['prompt']=g['prompt'].replace(old,new)
 ops.append({'group':g['id'],'old':old,'new':new})
def field(g,i,k,new):
 s=g['shots'][i];old=s[k]
 # match section, disambiguate repeated generic field using local shot context for local update
 marker=f'【shot {i+1}｜';start=g['prompt'].index(marker);end=g['prompt'].find('【shot ',start+1);end=len(g['prompt']) if end<0 else end
 part=g['prompt'][start:end];assert old in part,(k,old)
 # UI repeated fields handled by prefix helper; order transforms earliest first
 g['prompt']=g['prompt'][:start]+part.replace(old,new,1)+g['prompt'][end:]
 ops.append({'group':g['id'],'old':old,'new':new});s[k]=new
cross='跨组位置：北桥Elena坐B3，Madison站椅后左0.8m、Silas站右1.0m，同平台、穿北桥比赛服，三人看B3屏；本组蓝队画外仍在原位。六名红队均坐原席，R4—R6裁出仍存在。'
g=groups[2]
change(g,'空间锁：','空间锁：'+cross)
change(g,'ECU 桌前上方略俯 → CU 屏前左斜角 → MS 桌前左侧略俯 → ECU R3左前侧平角 → MCU R3左前侧四分之三平角','ECU屏前推 → CU屏空间快速沿流 → MS三席横移 → ECU摘耳麦跟随 → MCU正脸居中缓推')
# preserve exact cast cards, change only text fragments after them
for i,move,path in [(0,'屏前短推','冻结触发屏前推进6cm，1.1秒推、0.4秒止；焦点箭头，桌沿仍可辨'),(1,'沿回流路径快速跟进','屏边引入同一终端立体拓扑，虚拟机位沿左→右数据流快速前掠，近节点视差与短冰青拖尾清楚，末0.2秒止红端；不是真实换场'),(2,'向R3右移','报警触发沿桌前右移12cm/1.2秒、0.3秒落定，跟焦R3手起；不越轴'),(3,'跟随耳麦上提','手上提触发升摄8cm/1.5秒、0.5秒跟停，焦点右手头梁接触；保留耳侧大特写')]:
 oldhead=re.search(r'【shot '+str(i+1)+r'[^\n]+',g['prompt']).group();newhead=oldhead.replace('固定机位',move).replace('轻手持',move);change(g,oldhead,newhead)
 oldcam=re.search(r'镜头：[^\n]+',g['prompt'][g['prompt'].index(newhead):]).group();newcam=f"镜头：9:16；高约{g['shots'][i]['height']:.2f}m；{g['shots'][i]['lens']}mm等效；T4.0；{path}。切点：{g['shots'][i]['cut']}";change(g,oldcam,newcam);g['shots'][i]['camera_movement']=move;g['shots'][i]['camera_path']=path
field(g,1,'action','箭头完成方向翻转，冰青回流沿既定路径左→右掠过月白节点，弯折网络线快速通过，红端由路径返回触发警示；蓝左红右不镜像，不出现实体弹道或随机爆炸。')
oldhead=re.search(r'【shot 5[^\n]+',g['prompt']).group();change(g,oldhead,oldhead.replace('R3左前侧四分之三平角｜轻手持','R3桌前正面平角｜居中缓推'))
field(g,4,'angle','R3桌前正面平角') if False else None
g['shots'][4]['angle']='R3桌前正面平角'
oldcam=re.search(r'镜头：[^\n]+',g['prompt'][g['prompt'].index('【shot 5'):]).group();change(g,oldcam,'镜头：9:16；高约1.35m；65mm等效；T2.8；机位在桌前原轴侧面向R3，随耳麦下降缓推8cm/3秒、最后1秒稳住胸上。连续4秒不切，脸与嘴始终清楚居中，收句闭口后才切Xavier。')
field(g,4,'frame','透视构图描述：队员01正脸居中、胸上裁切占画高58%，双眼鼻嘴完整，脸中心画宽50%、双侧留余量；耳麦从头顶右侧降右胸，由右手持有；副队长在R2左画外、Xavier在R1更左画外，均未换座；桌前轴侧不变，屏边不遮嘴。')
field(g,4,'action','右手持耳麦降到右胸前，左掌压台面；头部保持正脸，眼睛向左画外Xavier偏移，嘴清楚地说完整一句；结束闭口，耳麦仍留右手，R3坐姿不变。')
field(g,4,'flow','视觉重心从摘耳麦细节回到画面中央正脸，机位调向R3而非让人物换席；队员01眼睛看左画外Xavier，不盯光轴。')
field(g,4,'audio','D11-02，队员01画内，组内6.2—9.6秒自然语速一次说完整："Why the hell is our attack hitting us?!" 6.0—6.2秒准备，9.6—10.0秒闭口反应；整句保持一个连续正脸镜头，不切声、不重启、不删词，只队员01口型。无旁白、字幕、BGM，警示底声压低。时长为文本预算。')
g['shots'][4]['camera_movement']='居中缓推';g['shots'][4]['camera_path']='前推8cm/3秒，1秒保持居中'
# G04 put all speech into first continuous speaker shot
h=groups[3];change(h,'空间锁：','空间锁：'+cross)
change(h,'时长分配：1.5 / 1.0 / 3.0 / 3.5 / 3.0s；最强拍shot 3','时长分配：6.0 / 1.0 / 1.0 / 1.0 / 3.0s；最强拍shot 1，完整命令连续镜修复断接，覆盖原短镜时长')
change(h,'MCU前跟 → CU短摇 → MS侧移 → CU推至眼部ECU → CU屏幕右移','MCU正脸居中连续前跟 → CU听者居中 → MS三席侧移 → ECU眼部短推 → CU屏幕右移')
change(h,'视觉动线：左中Xavier→中右听者→左中命令→下部防线。','视觉动线：中央Xavier完整命令→中央副队长执行→三席关系→中央眼部→下部防线。')
h['durations']=[6,1,1,1,3];h['strong']=1
for i,d in enumerate(h['durations']):
 oldhead=re.search(r'【shot '+str(i+1)+r'[^\n]+',h['prompt']).group();newhead=re.sub(r'duration: [\d.]+s',f'duration: {d:.1f}s',oldhead)
 if i==0:newhead=newhead.replace('R1左前侧略低｜前移跟随坐直｜50mm','R1桌前正面平角｜居中前跟｜65mm')
 if i==3:newhead=newhead.replace('CU→ECU','ECU').replace('推近右眼大特写','眼部短推')
 if oldhead!=newhead:change(h,oldhead,newhead)
 h['shots'][i]['duration']=d
oldcam=re.search(r'镜头：[^\n]+',h['prompt'][h['prompt'].index('【shot 1'):]).group();change(h,oldcam,'镜头：9:16；高约1.35m；65mm等效；T2.8；R1桌前原轴侧正面，坐直触发前跟10cm/1秒，随后缓推5cm到第5秒、第6秒收句留稳；全程同一镜不切，Xavier正脸居中、双眼鼻嘴清楚，禁止在话中切听者或大特写。')
field(h,0,'frame','透视构图描述：Xavier正脸居中、胸上裁切占画高62%，脸中心画宽50%，左右留余量，双眼鼻嘴完整；R1屏边仅右下不遮嘴。机距建议1.9m、机位桌前原轴侧，副队长R2右画外、队员01R3更右画外，其他三席仍在原位；无前景肩膀。')
field(h,0,'action','接队员01求援，Xavier从后靠前收上身15cm坐直，脚踩地、臀部留座；头部保持正脸、目光略向右画外副队长，连续完成整段命令；末词说完才闭口回看本人主屏，双手落键鼠，不站起。')
field(h,0,'flow','重心保持画面中央正脸，脸随前跟不贴边；眼睛略偏向右画外R2副队长，身体仍朝本人终端，视线不锁光轴。')
field(h,0,'audio','D11-03，Xavier画内，组内0.4—5.7秒同一声音自然急促地一次说完整："Sever the link! Lock down the main gate! Everyone on defense, stop her!" 0.0—0.4秒坐直准备，5.7—6.0秒收句闭口；全句一个连续正脸居中镜头，不剪断、不重启、不换音色、不重复开头，只Xavier口型。无旁白、字幕、BGM，底声低于人声；时长为文本预算。')
h['shots'][0].update(angle='R1桌前正面平角',lens=65,height=1.35,camera_movement='居中前跟',camera_path='先前跟10cm/1秒，再缓推5cm至5秒，6秒收句留稳')
field(h,1,'frame','透视构图描述：副队长居中、锁骨裁切占画高52%，R2屏左下；Xavier仍R1左画外约0.8m、队员01R3右画外；桌前左轴侧不变，无裁判蓝队或新人物，完整脸不贴边。')
field(h,1,'audio','组内6.0—7.0秒，D11-03已经完整结束，本镜无对白；副队长闭口执行，Xavier不复读。仅低键响，无旁白或BGM。')
oldcam=re.search(r'镜头：[^\n]+',h['prompt'][h['prompt'].index('【shot 3'):]).group();change(h,oldcam,'镜头：9:16；高约1.65m；35mm等效；T4.0；完整命令后沿桌前左轴侧右移10cm/0.8秒、0.2秒落定，三人操作层可读；不越屏后。切点：R3耳麦接触台面后切队长压力。')
field(h,2,'action','完整命令已结束，三人按各自终端防守；副队长先键入，队员01把右手耳麦从右胸降至本人R3桌右放稳，左手不离键区；Xavier目光回主入口，三人均闭口坐定。')
field(h,2,'audio','组内7.0—8.0秒无对白，D11-03不在此续句或重播；三人闭口，耳麦轻触桌面与低键响，禁止新命令和旁白。')
oldcam=re.search(r'镜头：[^\n]+',h['prompt'][h['prompt'].index('【shot 4'):]).group();change(h,oldcam,'镜头：9:16；高约1.35m；100mm等效；T2.8；右眼微距，眼睑收紧触发短推3cm/0.7秒、0.3秒落定；始终ECU不承载台词，原轴侧跟焦。切点：闭口眼部压力切封堵证据。')
# keep card fragments around Xavier and deputy intact
change(h,'起幅Xavier锁骨CU在左中；落幅裁右眉、右眼、鼻梁和耳麦边。起幅右边仅','Xavier右眼居中大特写，裁右眉、右眼、鼻梁和耳麦边；只眼部无嘴。画右边原有')
change(h,'副队长虚肩占宽不到10%，推近后出画，不换座；R3—R6画外。单眼清楚，不遮瞳孔、不越轴。','副队长虚肩占宽不到10%，两人仍在R1/R2，不换座；R3—R6画外。单眼清楚，不遮瞳孔、不越轴。')
field(h,3,'audio','组内8.0—9.0秒无对白，D11-03已结束；Xavier闭口不再说话，眼部反应无额外音效，只极低通风底声。')
field(h,3,'reaction','Elena持续进攻构成隐含压力；完整命令后Xavier下颌绷紧、眼睑微收，副队长肩线微沉且闭口；终态指尖悬在方案切换位置，接主入口防线结果。')
h['shots'][3].update(size='ECU',camera_movement='眼部短推',camera_path='前推3cm/0.7秒、0.3秒落定')
# reflect partial framing replacement into structured field
h['shots'][3]['frame']=re.search(r'画面：([^\n]+)',h['prompt'][h['prompt'].index('【shot 4'):]).group(1)
for g in [g,h]:
 assert sum(g['durations'])==(10 if g['id']=='G03' else 12)
 for label in ['叙事任务：','镜头：','画面：','视觉引导：','微表演：','对白反应：','人物背景融合：','光影细节：','音频：','运动强度：','负面提示词：']:assert g['prompt'].count(label)==5,(g['id'],label)
 assert '正视镜头说话' in g['prompt'] # existing negative refers to gaze, not face orientation
 (root/(g['id']+'.txt')).write_text(g['prompt'])
p.write_text(json.dumps(groups,ensure_ascii=False,indent=2))
md=root/'EP11_完整FormatC_V2.6.md';s=md.read_text()
for gid in ['G03','G04']:
 old=(backup/(gid+'.txt')).read_text();new=next(g['prompt'] for g in groups if g['id']==gid);assert old in s;s=s.replace(old,new)
md.write_text(s)
(root/'G03_G04_正脸连续修订操作.json').write_text(json.dumps(ops,ensure_ascii=False,indent=2))
print('操作数',len(ops))
for g in groups[2:4]:print(g['id'],'字符',len(g['prompt']),'原台词次数',g['prompt'].count('Why the hell')+g['prompt'].count('Sever the link'))
