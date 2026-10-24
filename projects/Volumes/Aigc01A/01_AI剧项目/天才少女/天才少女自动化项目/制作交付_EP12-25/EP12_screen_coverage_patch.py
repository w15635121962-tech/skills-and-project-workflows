"""局部修订背景、屏幕正反与反应覆盖；不重跑全剧构建器。"""
from pathlib import Path
import copy,json,re
import build_prompts as b

root=Path(__file__).parent
allg=json.loads((root/'全部平台填充.json').read_text())
old=copy.deepcopy(allg)
groups=[g for g in allg if g['episode']==12]
backup=root/'EP12/屏幕反打修订前平台填充.json'
if not backup.exists():backup.write_text(json.dumps(groups,ensure_ascii=False,indent=2))
original=json.loads(backup.read_text())
rules='背景与屏幕正反契约：拍人物正脸的桌前机位，显示器发光正面朝队员，摄影机只能看到哑黑不透明背壳、支架和窄边框；背壳绝不出现比分、代码、节点、图像或透明穿透效果。屏内内容需要给观众看时，另切场馆实体LED大屏的发光正面，交代边框、屏面和舞台位置；电脑背壳、桌前广告面与场馆大屏不是同一物体。人物镜背景保留可见结构锚点，不能把各方向都复制成同一面墙。'
duel='对垒覆盖契约：全局以观众面向舞台为参照，北桥蓝席左、红席右、裁判台中；两个终端不拼成相邻双人桌。Elena向右侧红席的确认目光与Xavier向左侧蓝席的确认目光互为反打，摄影机均在蓝红连线的观众侧半空间；各人随后落回自己屏幕的视线不是两人直接对视。G11蓝席等待与判断→G12红席被迫收缩防守→G13蓝席行动和大屏结果→G14裁判及解说员接收结果。反应由实际可见比分、对手姿态或公开播报触发，不靠随机皱眉；对白完整说完后才切独立听者反应。'
backgrounds={
 'nb':'背景落位：桌前摄影机→低位哑黑显示器背壳与蓝长桌桌沿→B3的Elena→椅后左0.8m Madison、右1m Silas→后方蓝色山形LED墙；左侧蓝徽章柱、右侧斜坡结构和地面蓝灯线保持位置。蓝席LED墙正面朝赛席前方与观众，属于独立墙屏，不能借此把终端背壳变成显示面。后排二人比Elena小且站在同一平台，近景裁出者留原位。',
 'red':'背景落位：桌前摄影机→红长桌和各终端哑黑背壳→R1站立Xavier，R2副队长及R3—R6队员01—04原椅→后方红山城LED墙；右近端红徽章柱、左侧台阶保持。六席以已批准R1—R6编号存在，未被参考图裁到的席位在画外延伸，不复制已有椅/角色。主显示面朝队员，桌前镜头只看到背面与真实边框。',
 'view':'背景落位：前排蓝栏杆在下部，V1黑人男居本排左、V2白人女中、V3拉丁裔男右，各已站稳本人排地面；后排座席沿画右上方升高、左侧阶梯和蓝横梁保持。白人、黑人、拉丁裔、南亚裔与东亚裔自然混坐，保留各自脸型、发型与服装。正打面对说话者，反打按同一V1—V2或V2—V3连线的舞台侧半空间取景；反打背景为对应方向的栏杆与座席，不能原封复制正打背景。',
 'ref':'背景落位：前景中立桌和裁定终端哑黑背壳；C2解说员站左、C3裁判坐右，相距1m；后方银白舞台、白阶梯、远左蓝席与远右红席保持身份。裁判看朝向自己的裁定屏发光正面，桌前正脸摄影机看不到其屏内信息。独立结果镜改拍舞台上方公共LED大屏发光正面。'
}

g11=groups[10]
g11['shots'][0]['action']=g11['shots'][0]['action'].replace('Elena已停的手和2–3比分','Elena已停的手与舞台上方公共大屏的2–3比分；本镜只拍Silas反应，不把比分印在前景电脑背壳')
g11['shots'][1].update(subject='Mb',action='反打Madison左后0.8m的眼眉大特写：她承接Silas先回应自己、随后垂目回避的变化，向画右Silas短看一眼；右嘴角刚扬起又压平，下眼睑收紧，眼睛回落Elena所在画左下方，自己的右手仍捏下摆，双脚原位。Silas右后1m、Elena坐B3都在画外原位，不新增人或手',gaze='Madison先看画右Silas眼睛，再落画左下Elena的工作位，不看镜头',face='礼貌笑在嘴角停止而眼眉未松，窥探同盟后遮掩嫉妒；反应只属于Madison',reaction='Silas收回目光触发Madison压嘴角与收眼睑，握下摆的手保持，没有台词、意外口型或离开原位',move='沿Madison—Silas连线的桌前半空间从右前正打切到Madison左前反打；镜内短推10cm，眼眉在中心停稳')
g11['shots'][2]['action']='Elena始终坐B3，承接Silas垂目与Madison压唇，先向画右红席Xavier站立位置确认一眼，再回到朝向自己的B3显示面，右手停止输入等待最后两节点防线调整；本镜不展示终端UI。Madison左后0.8m把脸摆回公开礼貌状态，自己的下摆仍有捏痕；Silas右后1m肩线收回面屏方向，回避Elena、不道歉、不触碰。短拉带回三人和蓝柱、山形LED墙的真实纵深，三人脚与椅支撑不变'
g11['shots'][2]['gaze']='Elena先落画右Xavier所在红席，再落自己屏幕；Madison看画右Silas后看公开大屏；Silas看B3桌沿'
g11['shots'][2]['reaction']='Elena看红席收缩态势后仍不出手，停手是等待防线调整的策略；Madison压笑、Silas垂目各自承接前镜，不同步眨眼、不说话'
g12=groups[11]
g12['shots'][0].update(size='CU',action='反打Xavier站R1的完整正脸居中：接到第二节点失守与Elena停止追逐的信号，眼睛先向画左蓝席B3确认，再回自己的R1显示面，下颌绷紧，嘴角压下，双手扶本人桌沿、重心前压但脚不移动。副队长R2及队员01—04在R3—R6原椅画外；他被迫守住最后两节点，不新增进攻、台词或得分',gaze='先看画左蓝席B3的Elena，再落本人R1屏幕下部，瞳孔避开镜头光轴',face='Xavier下颌绷紧、眉内侧收拢后维持，急躁转成受压防守；反应晚于比分变成2–3',reaction='Elena第二次得分与停手触发Xavier先抬眼确认再压回屏幕，手指扶桌发紧；双方以跨席位反打表现对垒，不把他们放在一张桌',move='位于蓝红连线观众侧、红桌前靠内侧，机高约1.6m正面微低角，缓推12cm在完整正脸居中落稳')
g12['shots'][2]['action']='同轴横移露回六席：Xavier站R1双手扶桌，副队长坐R2、队员01坐R3、02坐R4、03坐R5、04坐R6。副队长压键后停；01肩线内收，02指节停键面，03先瞥队长再回屏，04眼睑收紧后定在本人屏面，各自承接第二节点失守而守住最后两节点。屏幕发光正面朝六人，摄影机只见哑黑背壳，不能在背壳绘制防守地图；防线内容留给后续独立公共大屏镜。X耳麦在R1桌、01耳麦R3桌右，其他仍戴，没人离椅或复制成第七人'
g12['shots'][2]['reaction']='Elena停手使六人谨慎收缩；Xavier绷下颌、副队长停按键、01收肩、02停指、03回屏、04收眼睑按不同先后落稳，形成应战的群体反应，全部闭口'
g13=groups[12]
g13['shots'][0]['action']+='；显示器背壳只出现在画面下方，屏内防线不在背壳上可见，脸完整居中'

def screen_block(index,duration,final=False):
 content=('大屏已稳定3–3，仅保留第三节点归属北桥的绿色结果；不再重复捕获动画，不出现4–3、获胜字样或后续得分' if final else '大屏从2–3开始：最后两个得分节点的红色策略检查层收缩，蓝色数据流沿未覆盖的侧支路高速前进、在检查点短暂停顿后获准进入第三节点；第三节点由待捕获变绿，比分一次变为3–3。冰青线条沿路径有方向拖尾和节点视差，不用随机爆炸、透明电脑背壳或无因万能墙反弹')
 return '\n'.join([
 f'【shot {index}｜场馆公共大屏｜MS｜观众侧正面略仰｜沿屏面法线实推20cm，末0.7秒停稳｜50mm等效｜duration: {duration:.1f}s】',
 '叙事任务：'+('确认第三节点与三比三结果' if final else '展示第三节点捕获的因果结果'),
 '镜头：竖屏9:16，50mm全画幅等效/T4；摄影机在舞台前观众侧公共大屏法线附近，机高约1.6m略仰，向屏面推20cm；公共大屏在舞台上方的真实墙架中，保留四边框与下方舞台结构，不把整镜伪装成没有载体的HUD。屏面占画高约75%，四周留真实结构边距；同一场馆、同一时间和已有舞台照明，没有换地点或光源。',
 '画面：【透视构图】@比赛积分参考图.png 仅借公共显示面、蓝左红右布局和比分视觉层级；严禁照抄参考图终局4–3、错误队名、兜帽人物或后续节点。镜头→空的舞台前通视区→独立大屏发光正面→实体支架与上方环形舞台结构；不出队员电脑、不出人物。'+content+'。画外Elena仍坐B3，Madison左后0.8m、Silas右后1m；Xavier站R1，副队长及01—04坐R2—R6；裁判坐C3、解说员站C2、观众原排站立，均没有搬进大屏或离场。',
 '视觉引导：由上一镜的输入接点引向屏面中心第三节点，蓝流左到右、红防守右侧聚集；随后注意力收在比分3–3，不显示其他可读长文本。边框与屏面始终共面，摄影机移动产生支架与墙面的真实视差。',
 '微表演：本镜无真人、无头像和手；不生成任何人脸或嘴。数据速度依状态变化，结果稳定后不再循环重启。',
 '对白反应：'+('承接裁判完整播报和解说员已完成的眼睑反应，大屏只确认既有结果；画外队员继续各自原位' if final else '承接Elena唯一一次按键的结果，第三节点状态改变触发得分；不把尚未发生的第四分写入画面')+'。本镜没有新增对白或表演者。',
 '人物背景融合：无真人；LED屏面在实体框架内，后壳不透明，像素与光线受屏面边界约束，不透墙、不穿框、不悬浮到前景；既有赛席仍位于舞台两侧。',
 '光影细节：LED亮区保留纹理且不过曝，窄框仅反射本场舞台光；屏亮度变化局限显示面，场馆主光方向、色温与曝光不改变。',
 '音频：无台词、无旁白、无字幕朗读、无音乐、无新增提示声；只留既有场馆环境底声，不重播裁判句子。',
 '运动强度：摄影机中低强度实推；仅屏内数据高速运动，路径方向拖尾与前后节点视差提供速度证据，第三点捕获后稳定落幅。',
 '负面提示词：禁止电脑背壳显示图像、透明双面显示器、屏内容穿墙、浮空HUD、错误屏面朝向、重复捕获、比分4–3、提前获胜、未绑定人物、头像克隆、字幕、水印、随机长文字、旁白、口型；禁止跳轴、屏幕反转、廉价贴图和随机爆炸。'])

anchor=(root/'人物行为锚点_用户20261009.md').read_text().split('\n\n')[1]
for g in groups:
 # 已提交1—8保留原投递正文；修订只针对尚未提交组9—14。
 if g['group']<9:continue
 p=b.render(g).replace('，本次不提交视频。','。')
 if g['scene']=='nb':p=p.replace('空间锁：',anchor+'\n空间锁：',1)
 p=p.replace('空间锁：',rules+'\n'+backgrounds.get(g['scene'],'')+'\n'+duel+'\n空间锁：',1)
 p=p.replace('屏中影像是屏中不跑到现实前景。','屏内影像只在面向人物的发光正面，桌前背壳不显示内容；本镜人物机位不展示UI。')
 p=p.replace('负面提示词：','负面提示词：禁止背壳出现代码/比分/画面、透明双面屏、屏面正反混淆、正反打视线同向、对手无因反应；')
 if g['group'] in (13,14):
  if '比赛积分参考图.png' not in g['assets']:
   g['assets'].append('比赛积分参考图.png');g['props'].append('比赛积分参考图.png')
   p=p.replace('引用锁：','引用锁：@比赛积分参考图.png；',1)
  p=re.sub(r'【shot 3.*?(?=\n皮肤专项负面词：)',screen_block(3,g['shots'][2]['duration'],g['group']==14),p,flags=re.S)
  g['shots'][2].update(subject='screen',action='独立公共LED大屏正面：第三节点归北桥，比分3–3；不展示电脑背壳UI',gaze='无真人',face='无真人',reaction='既有按键/播报的结果确认',move='屏法线实推20cm')
  p=re.sub(r'景别循环：[^\n]+','景别循环：'+'→'.join(s['size'] for s in g['shots'])+'；各镜角度按正文，完整发言在首镜说完才切反应。',p)
 g['prompt']=p;g['generation_authorized']=True
 (root/f'EP12/G{g["group"]:02d}.txt').write_text(p)

ledger=json.loads((root/'英文原台词核对底稿.json').read_text())
assert [l for g in groups for s in g['shots'] for l in s['lines']]==[l for x in ledger['12'] for l in x['lines']]
for g,prev in zip(groups,original):
 assert len(g['shots'])==len(prev['shots']) and g['duration']==prev['duration']
 assert [s['duration'] for s in g['shots']]==[s['duration'] for s in prev['shots']]
 assert g['cast']==prev['cast']
 assert '强制要求： 人物皮肤须保持细腻' in g['prompt']
(root/'全部平台填充.json').write_text(json.dumps(allg,ensure_ascii=False,indent=2))
(root/'EP12/EP12_平台填充.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2))
(root/'EP12/EP12_完整FormatC_V2.6.md').write_text('\n\n---\n\n'.join(g['prompt'] for g in groups))
(root/'EP12-25_全部提示词.md').write_text('\n\n---\n\n'.join(g['prompt'] for g in allg))
(root/'背景屏幕正反与对垒反应_用户20261009.md').write_text('# 后续制作执行契约\n\n'+rules+'\n\n'+duel+'\n\n镜头覆盖应按具体事件落实：建立双方位置→动作发出→对方独立反应→接招/反击→结果→相关人物反应。反应不能截断英文原台词，不能用未绑定主要人物补镜。后续12—25集按本条检查对应场次，不凭检查新增原稿没有的攻防、得分或人物。\n\n本次实际修订EP12 G09—14；G01—08已提交，正文与投递记录保留，未自动重新生成。\n')
(root/'EP12/屏幕反打核验_20261009.json').write_text(json.dumps({'modified_groups':list(range(9,15)),'frozen_submitted_groups':list(range(1,9)),'dialogue_verbatim':True,'groups':14,'shots':42,'duration_s':sum(g['duration'] for g in groups),'screen_shots':['G13-S03','G14-S03'],'reaction_coverage':['G09-S02','G10-S02','G11-S01/S02','G11-S03→G12-S01','G12-S03','G14-S02'],'asset_analysis':'资产空间与全剧连续性底稿.md + 本轮实际查看蓝席/红席/比分图','pending_video_qa':True},ensure_ascii=False,indent=2))
print('EP12 G09—14已修订；14组42镜131秒、英文原文和席位保持。')
