from pathlib import Path
import json,re,hashlib

out=Path(__file__).parent/'EP11'
groups=json.loads((out/'EP11_平台填充.json').read_text())
ops=[]
before={g['id']:g['prompt'] for g in groups}
def change(g,old,new):
    assert old in g['prompt'],(g['id'],old)
    for _ in range(g['prompt'].count(old)): ops.append(dict(group=g['id'],old=old,new=new))
    g['prompt']=g['prompt'].replace(old,new)
def field(g,i,label,new):
    piece=g['prompt'].split(f'【shot {i}｜',1)[1]
    old=re.search(r'^'+re.escape(label)+r'：.*$',piece,re.M).group()
    change(g,old,label+'：'+new)
def cameras(g,specs):
    oldcycle=re.search(r'^景别循环：.*$',g['prompt'],re.M).group()
    cycle=[]
    for i,(move,path) in enumerate(specs,1):
        s=g['shots'][i-1]
        head=re.search(r'【shot '+str(i)+r'｜[^\n]+',g['prompt']).group()
        change(g,head,f"【shot {i}｜{s['name']}｜{s['size']}｜{s['angle']}｜{move}｜{s['lens']}mm等效｜duration: {s['duration']:.1f}s】")
        field(g,i,'镜头',f"9:16；机高建议{s['height']:.2f}m；{s['lens']}mm等效；T{s['t']:.1f}；{path}。切点：{s['cut']}")
        field(g,i,'运动强度','人物按具名起终态与道具接触执行；相机按本镜路径移动，背景产生真实视差，不以数码放大替代推轨。')
        s.update(camera_movement=move,camera_path=path)
        cycle.append(s['size']+' '+move)
    change(g,oldcycle,'景别循环：'+' → '.join(cycle))

for g in groups[4:]:
    caster='解说员仍坐C2' if g['id']=='G05' else ('解说员由C2坐姿撑桌起身' if g['id']=='G06' else '解说员已站C2')
    lock=f'跨组连续性：Elena始终坐B3，Madison站椅后左0.8m、Silas站椅后右1.0m，两人距1.2m，均看B3屏、不走离。红队左至右Xavier R1、副队长R2、队员01 R3、02 R4、03 R5、04 R6，各坐原椅；仅01耳麦已放R3桌右，其余戴耳麦。{caster}，裁判坐C3，两位相距1m；看台V1左V2中V3右均未起立。本组未取景的人仍在各自场地原位；近景裁出不等于离场，禁止跨场地召唤或克隆。'
    old=re.search(r'^空间锁：.*$',g['prompt'],re.M).group()
    change(g,old,old+'\n'+lock)

for idx in [4,9]:
    g=groups[idx]
    extra=['Madison的Northbridge比赛服.png','Silas的Northbridge战队比赛服.png']
    g['assets']+=extra
    old=re.search(r'^引用锁：.*$',g['prompt'],re.M).group()
    change(g,old,old+'\n角色补充引用：'+ '；'.join('@'+a for a in extra))

g=groups[4]
change(g,'Elena中部、腰上裁切占画高55%，B3屏上沿仅到胸下、键盘中下；机距2.5m轴前中性，左后Madison和右后Silas不入画；蓝山形屏垂线框住Elena不吞没她。','Elena坐B3画中，起幅胸上→落幅腰上占画高48%；B3屏胸下、键盘下中。Madison在椅后左0.8m画左后，Silas在椅后右1.0m画右后，两人站同平台、头高约Elena头高0.7倍，彼此距1.2m，均穿北桥比赛服。蓝山形屏与桌沿保持；屏不遮三人脸，不把两人挪到前景。')
s=g['shots'][3]
oldhead=re.search(r'【shot 4｜[^\n]+',g['prompt']).group()
change(g,oldhead,oldhead.replace('向下俯摇跟手回位','拉远揭示三人关系').replace('50mm','35mm'))
s.update(lens=35,t=4,camera_movement='拉远揭示三人关系',camera_path='桌前中性轨道后退0.6m，机距约1.9→2.5m，前2.5秒拉出两名椅后人物、末1秒读关系；三人的固定位置保持，焦点Elena、后景脸可辨')
field(g,4,'镜头','9:16；高约1.25m；35mm等效；T4.0；桌前轴上后退0.6m，建议机距1.9→2.5m，2.5秒拉出椅后两人，末1秒读取三人关系；跟焦Elena与手，后景人物可辨。切点：反击路径持续推进切中央席。')
change(g,'MS向下跟拍','MS拉远揭示三人')
field(g,4,'视觉引导','从中下回位右手拉回中上Elena眼睛；Madison画左后、Silas画右后均看B3屏右侧路径，视线不入镜头。')
field(g,4,'对白反应','右侧节点转红触发Elena右食指回键区；Madison原左后位抿唇、下颌后收，Silas原右后位握拳松半分、眉尾压低，反应错开半拍。三人闭口，终态站坐位置未变，单键操作不重复。')

cameras(groups[5],[
 ('短距侧移','解说员识别拦截触发沿桌前左轴侧右移15cm/1秒，末0.5秒读闭口蓄力，胸上MCU不变；焦点解说员，裁判右后仍坐'),
 ('向眼睛推近','裁判核验支路触发桌前左轴侧推近25cm/2.5秒，末1秒读眼睑收紧；保持CU锁骨至面部，屏幕边缘左下不越轴'),
 ('贴掌同向跟移','左掌压桌触发滑轨沿桌沿右移4cm/0.7秒，0.3秒读指腹受力；85mm微距ECU保持左掌、袖口、台面接触'),
 ('升高跟起身再拉出关系','接离座剩余30%，轨道升高15cm/0.8秒跟胸口；随后沿轴前后退20cm/2.2秒，末1秒读站立解说员左、坐姿裁判右后；MS落幅不翻转')])
cameras(groups[6],[
 ('屏前推进追踪分流','沿R1屏前左轴侧前进8cm/3.5秒、末1秒读新入口；85mm微距读取ECU。屏内三维拓扑相机跟冰青数据流向右前掠进，近层节点掠过制造纵深，外框与红桌沿始终保留'),
 ('短促推近反应','新漏点触发桌前左轴侧前推10cm/0.7秒，0.3秒读Xavier第二方案落手；CU不越轴，不改变R1坐姿'),
 ('沿三席横移','桌前R4至R6方向向右横移35cm/2秒，末0.5秒落于04右近；保持35mm斜俯MS、02左远03中04右近、屏和椅距不变')])
field(groups[6],1,'起态—路线—终态','承接第一全防守：中央三道绿色规则栅格检查会话状态，违规红包在此停止、消隐；右侧破口补绿阻断原路径，冰青流立即沿另一条未覆盖的侧支路改道；可入支路亮绿、检测到异常后标红。只向第一目标推进，未获得第二分。屏内三维网络纵深是同一终端监控图，真人不进入虚拟空间。')
field(groups[6],1,'光影细节','同一R1屏的数字拓扑保留红桌接触反光；屏内深钢蓝底，冰青细线为数据流、月白节点为设备、绿色薄栅格为策略，边缘窄辉光和沿路径短拖尾；仅屏幕像素发光，不改变场馆光源，不使眼球发光；精细电影级合成。')
field(groups[6],1,'视觉引导','蓝区左红区右；镜头沿唯一冰青包流向右前推进，旧支路关闭→新侧支路通过，拒绝红包停止而非穿墙爆炸。前景细线掠过、纵深节点视差突出网络速度，不铺满乱码。')
cameras(groups[7],[
 ('贴屏向右追踪','R6屏前沿左轴侧右移5cm/0.7秒，末0.3秒读右下04的止住鼠标；屏内拓扑追冰青流穿过两节点的弯折连线，近节点向左掠过；85mm微距ECU不穿屏'),
 ('下降跟确认键','Xavier右手移向确认键触发桌前左轴侧下摇7度/2.5秒，末1秒保留脸和双手腰上MS；椅不横移，不越轴'),
 ('前推追到第一目标外圈','沿R1屏前推6cm/2.5秒、末1秒读第一目标外圈；屏内拓扑摄影机沿冰青弧线右进，到第一目标外圈减速；CU保留外框与红桌沿，未取得分数')])
field(groups[7],1,'起态—路线—终态','第二方案封闭旧会话路径；屏内冰青数据包从未覆盖的侧支路路由进入新开放节点，绿栅格只拦拒绝流，不被撞碎。队员04右手止在R6鼠标上，空入口只亮一处，未捕获第二得分点；所有人物仍在真实赛席。')
field(groups[7],3,'起态—路线—终态','第三策略下发后，中央状态检查栅格闭合；唯一冰青流沿旁侧未覆盖连线绕入第一目标外圈，前景细节点快速掠过、流线形成短弧形拖尾，到外圈减速停住；三种方案灰色失效标记出现，第一目标尚未完成，不添加现实漏洞名称或执行命令。')
field(groups[7],3,'光影细节','红队基础6500K曝光不变；同一显示屏内深钢蓝拓扑、绿色策略薄片、月白节点、冰青窄发光路径，层次与反射精细，不新增场景光源；电影级合成，细线短拖尾不遮节点逻辑。')
cameras(groups[8],[
 ('向播报者推近','第一防线越过触发桌前左轴侧推轨15cm/1.8秒，末0.7秒读取说话脸；65mm MCU保持右后坐姿裁判与C2椅出处'),
 ('裁判CU推至眼部ECU','读取27计时触发100mm微距推轨，建议距脸0.9→0.55m/2.5秒，末1秒读右眼；起幅锁骨CU、落幅右眉右眼鼻梁无完整脸，裁判仍坐C3，解说员仍站左画外'),
 ('拉远复位双人','从站姿解说员腰上MS沿轴前后退25cm/3秒，末1秒读左站右坐关系与时间句终态；眼神画右上巨幕，裁判不站')])
groups[8]['shots'][1].update(size='CU→ECU',lens=100)
# 摄影参数按新的ECU设计同步。
change(groups[8],'｜CU｜C3左前侧四分之三平角｜裁判CU推至眼部ECU｜85mm','｜CU→ECU｜C3左前侧四分之三平角｜裁判CU推至眼部ECU｜100mm')
change(groups[8],'CU 裁判CU推至眼部ECU','CU→ECU 裁判CU推至眼部ECU')
change(groups[8],'85mm等效；T2.8；读取27计时','100mm等效；T2.8；读取27计时')
change(groups[8],'裁判画中右锁骨裁切占画高52%，C3屏低于下颌，解说员左画外站着距1m；前景无新演员，机位同桌前半空间。','裁判起幅中右锁骨CU，推轨落幅裁右眉、右眼和鼻梁，单眼约占画宽35%，无完整脸；裁判坐C3不移位，解说员仍站左画外相距1m；C3屏从左下因收幅退出，桌前左轴侧不变。')
cameras(groups[9],[
 ('沿计时区短移','27.00冻结读数触发B3屏前右移5cm/3.5秒，末1秒读数字与蓝桌沿；85mm微距ECU，屏内文字不滚动不变更'),
 ('短推确认眼神','从计时区落眼触发左轴側前推8cm/0.7秒，末0.3秒读Elena压低视线；CU眼镜耳麦不变，二人仍在椅后裁出'),
 ('拉遠恢复三人结果关系','第一节点转绿触发桌前中性后退0.5m/3.5秒，末1秒读三人和第一绿点；35mm、T4，建议机距2.3→2.8m；Elena中、Madison左后、Silas右后，台面HUD不遮脸')])
change(groups[9],'Elena画中、腰上裁切占画高48%，台面透明HUD位上中27.00、眼睛位中部、键盘与第一绿色得分点位下部，三层不遮脸；机距2.8m轴前中性，无其他演员肩；后山形屏和蓝桌沿形成稳定纵深。','Elena固定坐B3画中、腰上占画高48%；Madison站椅后左0.8m画左后，Silas站椅后右1.0m画右后，二人相距1.2m，头高约Elena头高0.7倍，北桥比赛服不换。计时27.00在屏内上部，键盘与首个绿点下部，无遮挡任何人脸；后山形屏、蓝桌沿和同平台支撑保持，不生成多余肩膀。')
field(groups[9],3,'对白反应','第一绿点触发Elena右肩放松而不追加输入；Madison在左后抿唇加紧，目光从27.00落第一绿点；Silas在右后指节松开、下颌短收，仍看B3屏。反应错开、三人闭口，均不移位、不庆祝第二分。')
groups[9]['shots'][2]['lens']=35
change(groups[9],'｜拉遠恢复三人结果关系｜50mm','｜拉遠恢复三人结果关系｜35mm')
change(groups[9],'50mm等效；T4.0；第一节点转绿','35mm等效；T4.0；第一节点转绿')

g=groups[10]
extras=['ST.ALDWIN副队长.png','ST. ALDWIN队员01.png'];g['assets']+=extras
old=re.search(r'^引用锁：.*$',g['prompt'],re.M).group();change(g,old,old+'\n角色补充引用：'+'；'.join('@'+a for a in extras))
change(g,'Xavier固定坐R1画左中、裁至腰上占画高58%，R1屏画右下；副队长与其他队员均画外，R3耳麦留桌面不在Xavier手里，臀与双脚支撑不变。','Xavier坐R1画左远、副队长坐R2画中、队员01坐R3画右近；三人腰上MS，各椅距0.8m、屏在本人前0.6m，近者头高约远者1.2倍。01耳麦在本人R3桌右，Xavier和副队长耳麦仍戴。R4队员02、R5队员03、R6队员04在右画外原座不离席；三人臀与双脚同平台支撑，红桌沿及后柱位置不变。')
field(g,1,'对白反应','第一节点失守触发Xavier下颌锁紧、胸口收回2cm；副队长在R2眉间收紧、左掌压住桌缘；队员01在R3嘴角下压、右手停在已放桌右的耳麦旁，不再次取耳麦。三人错开反应、闭口，各看本人屏，终态仍坐原位。')
cameras(g,[
 ('沿R1至R3侧移揭示关系','第一分失守触发桌前左轴侧右移30cm/3秒，末1秒读Xavier左远、副队长中、01右近三席腰上MS；不跨屏后、不得换脸换座'),
 ('贴鼠标横移','右食指卸力触发微距沿R1桌面右移3cm/0.7秒，末0.3秒读停住指腹和支撑阴影；ECU只为Xavier双手'),
 ('脸部推至单眼ECU','未亮下一目标触发100mm微距，距脸约0.9→0.55m/2秒，末1秒读右眼偏移；CU起幅→右眉右眼鼻梁落幅，副队长仍R2、01仍R3画外')])
change(g,'Xavier画左中锁骨裁切占画高55%，眼睛在上三分区，主屏边缘画右下，副队长画外；机距1.7m仍桌前左半空间，红后柱柔虚。','起幅Xavier锁骨CU在左中，落幅右眉右眼鼻梁ECU、单眼约占画宽35%，耳麦边可辨；R1坐姿不变，副队长R2与01 R3因收幅裁出仍原位，主屏边右下退出，桌前左轴侧不变。')
g['shots'][2].update(size='CU→ECU',lens=100)
change(g,'｜CU｜R1左前侧平角｜脸部推至单眼ECU｜85mm','｜CU→ECU｜R1左前侧平角｜脸部推至单眼ECU｜100mm')
change(g,'CU 脸部推至单眼ECU','CU→ECU 脸部推至单眼ECU')
change(g,'85mm等效；T2.8；未亮下一目标','100mm等效；T2.8；未亮下一目标')
cameras(groups[11],[
 ('沿前排横移','V2前倾触发下方通道右移25cm/3秒，末1秒读V1左V2中V3右同排原座和落掌70%；35mm略仰MS不越观众—巨幕轴'),
 ('同向下跟落掌','V1掌继续下降触发微距轨道下降3cm/0.7秒，末0.3秒读取指节与本人右扶手接触；85mmECU只拍V1右手'),
 ('推近吸气后的眼神','V2闭嘴等待触发通道同轴侧推近15cm/2秒，末1秒读CU锁骨脸部；V1左与V3右只因紧裁出画，三座不换，不变成后排人')])

for g in groups[4:]:
    assert re.findall(r'^音频：.*$',before[g['id']],re.M)==re.findall(r'^音频：.*$',g['prompt'],re.M),g['id']
    assert sum(g['durations'])==sum(s['duration'] for s in g['shots'])
    assert len(g['prompt'])<5000,(g['id'],len(g['prompt']))
    (out/(g['id']+'_连续性修订前.txt')).write_text(before[g['id']])
    (out/(g['id']+'.txt')).write_text(g['prompt'])
    parts=re.split(r'【shot \d+｜[^\n]+\n',g['prompt'])[1:]
    for s,p in zip(g['shots'],parts):
        for k,label in [('frame','画面'),('action','起态—路线—终态'),('flow','视觉引导'),('reaction','对白反应'),('motion','运动强度')]:
            s[k]=re.search(r'^'+label+r'：(.*)$',p,re.M).group(1)
(out/'EP11_平台填充.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2))
(out/'G05-G12_连续性极客修订操作.json').write_text(json.dumps(ops,ensure_ascii=False,indent=2))
md=out/'EP11_完整FormatC_V2.6.md';body=md.read_text()
for g in groups[4:]:body=body.replace(before[g['id']],g['prompt'])
md.write_text(body)
(out/'G05-G12_连续性极客修订校验.json').write_text(json.dumps({'dialogue_unchanged':True,'durations_unchanged':True,'groups':[{ 'id':g['id'],'chars':len(g['prompt']),'sha256':hashlib.sha256(g['prompt'].encode()).hexdigest(),'assets':g['assets']} for g in groups[4:]],'platform':'待回读','generation_authorized':['G06'],'G05_existing_video':'旧成片位置漏人，修订稿尚未重生成'},ensure_ascii=False,indent=2))
print(json.dumps({'operations':len(ops),'chars':{g['id']:len(g['prompt']) for g in groups[4:]},'dialogue_unchanged':True},ensure_ascii=False))
