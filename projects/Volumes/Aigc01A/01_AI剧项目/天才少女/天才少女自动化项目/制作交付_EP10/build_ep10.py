from pathlib import Path
import json,re,collections
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
template=Path('/Users/zc/.codex/skills/write-format-c-video-prompts/references/format-c-template-v2.6.md').read_text()
Q=re.search(r'写实照片级、超写实质感、真人实拍电影剧照，采用 ARRI Alexa 65.*?丁达尔效果（Tyndall Effect）。',template).group()
SKIN=re.search(r'强制要求： 人物皮肤须保持.*?这一整段与固定画质词同等优先级，必须逐字出现在每一组的组头中，不允许省略、简写或用"皮肤真实"等笼统表述替代。',template).group()
AS={'E':'Elena.png','M':'Madison的Northbridge比赛服.png','S':'Silas的Northbridge战队比赛服.png','X':'Xavier.png','V':'ST.ALDWIN副队长.png','R':'裁判四视图人物.png','C':'解说员四视图人物.png'}
NAME={'E':'Elena','M':'Madison','S':'Silas','X':'Xavier','V':'副队长','R':'裁判','C':'解说员','a':'黑人男观众V1','b':'白人女观众V2','c':'拉丁裔男观众V3','d':'南亚裔女观众V4','e':'东亚裔男观众V5'}
PROFILES={'a':'二十岁黑人男生、短卷发、深蓝无字外套','b':'二十岁白人女生、棕色齐肩发、米色针织衫','c':'二十岁拉丁裔男生、黑短发、灰色连帽衫','d':'二十岁南亚裔女生、黑长发、墨绿无字上衣','e':'二十岁东亚裔男生、黑短发、白色无字衬衫'}
NB='北桥蓝席B1—B6按观众面向舞台由左至右编号。Elena黑衣透明眼镜坐B3；Madison在B3椅后左0.8m、Silas在椅后右1m，二人约距1.2m，穿各自蓝白比赛服、双脚同平台。B1/B2/B4—B6队员坐原椅画外。'
RED='红席R1 Xavier、R2副队长、R3队员01、R4队员02、R5队员03、R6队员04，六人各坐本人椅并戴本人耳麦，本集无人起身、摘摔耳麦。'
COURT='中立裁判台C2解说员与其右1m的C3裁判均坐椅。'
VIEW='北桥看台前排V1左、V2中、V3右，同排各距0.6m；V4在V2后排左，V5在V2后排右；五人均坐原椅，后排高一阶。其他白人、黑人、拉丁裔、南亚裔及东亚裔观众自然混坐。'
SC={'nb':('赛场Northbridge战队席位.png','蓝徽章柱在参考左、蓝桌前、蓝山形LED墙后、坡道右；桌前观察只能见终端不透明黑色背壳。','6500K桌前上方45度柔白主光，白桌反射补眼窝，蓝墙低脸一档只勾后肩；面部近侧亮、远侧保留纹理，投影落椅后及桌下。'),
'red':('赛场St.Aldwin战队席位.png','红柱参考右、红山形LED墙后、左台阶；摄于桌前，终端背壳朝镜头，屏正面朝选手。','3600K桌前上方45度暖白柔主光，红灯仅在后轮廓，中性桌反射补眼窝；近侧颊亮、远侧颊低半档，阴影落桌下及椅后。'),
'view':('赛场Northbridge代表观众席位.png','蓝横梁后、栏杆前、看台台阶后高；人物镜头只在各排前侧通道，不越座椅。','5600K看台顶前柔白主光，蓝横梁低一档作轮廓；近侧颊亮、远侧颊保留，阴影落栏杆与座位脚边，各族肤色保真。'),
'ref':('赛场中央裁判席位.png','中立桌正面低矮验证灯列、中央银白后墙，蓝席与红席分别在两侧画外，不能拼成一桌。','5600K中立桌前上方柔白主光，银白地台反射填下颌；面部近侧亮、远侧保留，后墙低脸一档，阴影落桌后及椅脚。')}
source=(BASE/'制作交付_EP11-22/源文提取/天才少女剧本台词分稿.txt').read_text().split('第10章\n')[1].split('第11章')[0]
quotes=re.findall('“([^”]+)”',source)
# English only, exact punctuation from the canonical dialogue draft.
EN=[x for x in quotes if re.search('[A-Za-z]',x) and not re.search('[\u4e00-\u9fff]',x)]
assert len(EN)==14,EN
DL={1:EN[0:2],2:[EN[2]],3:[EN[3]],4:[EN[4]],5:[EN[5]],6:[EN[6]],7:[EN[7]],8:[EN[8]],9:[EN[9]],10:[EN[10]],11:[EN[11]],12:[EN[12]],13:[EN[13]]}
groups=[]
def shot(p,size,t,task,act,gaze,react,dialogue=None,cam=None,view=None):
 return dict(p=p,size=size,duration=t,task=task,act=act,gaze=gaze,react=react,dialogue=dialogue,cam=cam,view=view)
def group(scene,title,shots,state,props=()):
 g=dict(episode=10,group=len(groups)+1,title=title,scene=scene,shots=shots,state=state,props=list(props));groups.append(g)

group('nb','三人承受认证揭晓',[
shot('M','MCU',3,'Madison的优越感被打断','已在椅后左原位；视线锁向舞台前方公共认证屏，下颌轻落后收紧，原本微扬的唇角停住；左手抓紧自己衣摆，终态仍不肯看Elena。','公共认证屏的GHOST认证','承受第9集已有S+认证结果，闭口，原本抬高的下巴逐渐回平。'),
shot('S','CU',2.5,'Silas第一次无法解释她','仍在椅后右；从公共认证屏转看B3 Elena，再短看左侧Madison，下唇欲动后压住，右手收紧衣摆；终态停在Elena方向。','画外B3 Elena','认证打破Silas三年来的轻视；他先确认Madison，再关注Elena，始终未上前支持。'),
shot('E','MCU',2.5,'Elena接管自己的终端','坐B3，双手从桌沿移到本人键盘，指腹落键打开比赛界面，眼睛由公共屏降到自己屏；终态手留键区。','本人B3屏','承受身后两人的停顿而继续操作；上眼睑轻收、唇闭，不回应两人的视线。',view='Elena中央胸上清楚；Madison左后、Silas右后各为小且虚焦的胸上轮廓，二人头高小于Elena头高，均闭口，无人遮她。')],
'起态承接第9集GHOST/S+已经显示；不重复登录或重做揭晓。耳麦放B3桌右。终态Elena已打开比赛界面、双手在键区，Madison与Silas未移位。',('键盘参考图.png',))
group('nb','Elena完整宣告',[
shot('E','MCU',4.5,'Elena明确新的对手身份','坐B3由屏抬眼，身与脸朝红席Xavier方向；嘴唇从闭合到连续完整说两句，再闭合，双手留键区。','画外红席R1 Xavier','说话权由认证结果转到她；肩自然下沉，无夸张挑衅。',1),
shot('S','CU',1.5,'Silas被她的独立决定排除','椅后右站定；看Elena后颊，眉内侧抬起又收，右肩僵住，终态闭口未劝阻。','画外B3 Elena','接受Elena完整发言后的后果，手不伸向她。'),
shot('M','MCU',2,'Madison开始寻找反击理由','椅后左站定；目光由Elena转公共屏，再落她双手，拇指揉紧衣摆，唇角重新抬半分但眼睑不放松。','画外Elena键区','宣告剥夺Madison话语权，终态准备质疑而尚未开口。')],
'起态Elena双手已在键区；耳麦仍B3桌右。終态Elena闭口直坐；Silas右后、Madison左后原地，各不接触Elena。')
group('view','看台辨认身份',[
shot('a','MCU',2.5,'观众确认认证等级','V1坐原排，胸向舞台，双手停在膝盖；正脸连续说完整短问，句末下颌收回。','画外舞台公共认证屏','已有认证令他眉峰抬起；其他人闭口。',2),
shot('b','CU',3.5,'观众认出Ghost的作品','V2坐原椅前倾约5cm而不站，目光公共屏；完整发言后闭口，双手停膝。','画外公共认证屏','承受V1确认后的兴奋，唇角抬而肩不挥舞。',3),
shot('c','MCU',6,'C等成绩形成身份冲突','V3坐右侧原椅，眼从公共屏转舞台B3 Elena；完整发问，句末眉内侧轻收、唇闭。','画外蓝席B3 Elena','承受Ghost身份与自己所知成绩的矛盾，不额外加群喊。',4)],
'五位看台观众均坐原排；没有欢庆起立。末V3闭口仍注视Elena。蓝席三人、红席六人及裁判台均在原位画外。')
group('view','教授盲点与沉寂十年',[
shot('d','MCU',8,'观众质疑教学判断','V4坐V2后排左，上身微前倾，正脸完整说三句；句间自然换气不重新起句，末手掌压回膝。','画外蓝席B3 Elena','听见C成绩质疑后眉内侧抬、鼻翼轻收，句末闭口。',5),
shot('e','CU',5.5,'观众确认消失十年的账号','V5坐V2后排右，头向公共屏，完整说两句；末下唇轻收，下颌停住。','画外公共认证屏','账号重现令他停下原本揉衣袖的手，句末不补对白。',6),
shot('d','MCU',1.5,'怀疑没有立即消失','V4仍原椅，眼从认证屏降到自己膝上双手，眉峰慢落，闭口停在欲判断未判断。','自己膝上双手','V5发言已结束，V4不跟唱，沉默留下疑虑。')],
'所有观众坐定；身份惊叹尚未转为确定支持。蓝席三人、红席六人与裁判台仍原位画外。')
group('nb','三人的不同承受方式',[
shot('S','MCU',3.5,'Silas意识到自己从未了解她','椅后右；视线从公共认证屏落Elena手再到脸，自己的右手半抬后收回身侧，下颌收紧，未开口支持。','画外B3 Elena','看台的成绩质疑使他难堪；终态重新看左侧Madison，暴露习惯性依附。'),
shot('M','CU',2,'Madison借疑虑恢复姿态','椅后左；先捕捉Silas看向自己的目光，再转Elena；抬下巴半厘米，衣摆手松一下又收，唇闭。','画外B3 Elena','感到Silas仍寻求自己判断；眉外侧微抬，准备把攻击包装成维护学校。'),
shot('E','MCU',2.5,'Elena拒绝回应外部审判','坐B3，手指在自己的键区停住等待身份流程，颈肩放松，眼聚焦屏正面；末下眼睑轻收、唇闭。','本人B3屏','身后三人的三角关系未变，她不回头求认可。',view='Elena中央胸上；Madison左后与Silas右后胸上虚焦仍在原位，手不接触Elena。')],
'耳麦仍B3桌右；Elena坐定操作、Madison左后、Silas右后，三人无人离场。末Elena等身份流程。')
group('red','副队长提示认证',[
shot('V','MCU',3,'副队长无法忽略真实认证','副队长坐R2、耳麦在头，身体由靠背前倾5cm看自己的屏，继而头转R1 Xavier；完整说提示，句末唇闭。','画外左侧R1 Xavier','看到认证记录后下颌紧，右手停自己的鼠标。',7,cam='摄影机在R2左前方、红桌前外通道，朝副队长转向R1的脸；在R1—R2连线桌前半空间，镜高1.25m，调机位保持完整正脸中央；缓推8cm，无遮挡。'),
shot('X','CU',2,'Xavier复核认证记录','Xavier坐R1戴耳麦，身由靠背移到桌前5cm，目光自己屏，左手压桌沿，眼睑收紧；仍坐椅。','本人R1认证屏','副队长提示使他停止轻蔑，先真正检查记录。'),
shot('V','MCU',3,'副队长等待队长解释','副队长仍R2前倾，眼由Xavier落自己屏；拇指压鼠标却未点击，嘴闭，肩略向内收。','本人R2认证记录','察觉队长不能立即给出解释，终态等待其判断。')],
'六名红队员各在原椅前倾查看自己的认证屏；镜头仅清楚拍Xavier与副队长，01—04在原位画外，若出现任一队员须先绑定其本人图。所有耳麦在头，无摔摘。')
group('red','Xavier完整否认',[
shot('X','MCU',7,'Xavier用核验程序夺回权威','坐R1，检查屏后抬头看蓝席B3；脸完整朝对话方向连续说完两句，左手仍压桌沿，末闭口。','画外蓝席B3 Elena','把自己的迟疑压成笃定判断；句间气口自然、不加嘲笑新词。',8),
shot('V','CU',1.5,'副队长没有被说服','R2坐定看Xavier，眉内侧轻抬，嘴唇压住，右手不离鼠标。','画外左侧R1 Xavier','队长完整发言结束后，他仍见真实认证，闭口而不点头附和。'),
shot('X','MCU',1.5,'Xavier把压力交给裁判','R1坐定，眼从Elena方向移中央C3裁判，下巴抬半厘米，手掌压桌边更紧。','画外中央C3裁判','等联盟给自己支持；终态未起身，嘴闭。')],
'Xavier与副队长、01—04均坐R1—R6且戴耳麦；蓝席三人原位，解说员与裁判仍坐，比赛尚未开始。')
group('nb','质疑返回三人',[
shot('E','MCU',3.5,'Elena把质疑留在场外','坐B3承受Xavier的完整否认；右指停键，眼由自己的屏抬到中央裁判台，唇角不笑、颈肩放松，等待正式核验。','画外中央C3裁判','拒绝与Xavier争辩；后景M/S闭口维持原位。',view='Elena中央胸上，Madison左后、Silas右后胸上小轮廓虚焦，三人世界位置不变。'),
shot('M','CU',2,'Madison选择公开施压','椅后左，目光由观众方向落Elena，左手放开衣摆转为掌心向下停胸前，不迈步；鼻翼收紧。','画外B3 Elena','观众的迟疑被她抓住，末下巴抬起准备发言。'),
shot('S','MCU',2.5,'Silas再次优先确认Madison','椅后右；先看左侧Madison抬手，随后转Elena，自己的双手贴身，肩向Madison偏而双脚不换位。','先Madison，末B3 Elena','察觉Madison准备指控，他没有保护Elena或叫停Madison；末闭口。')],
'三人位置不变，Madison已掌心朝下举至胸前而未触碰Elena；耳麦B3桌右。终态她准备施压。')
group('nb','Madison完整指控',[
shot('M','MCU',12,'Madison把攻击包装成护校','椅后左对B3 Elena，开口前目光确认；连续正脸完整说完五句，掌心向下的左手在第一句轻压后留胸前，末缓落身侧，不推拉对方、不截断词尾。','画外右下B3 Elena','疑虑给她话语入口；语气越说越硬，眉内侧收、下颌前送，非真关怀；句后唇闭。',9,cam='Elena—Madison连线的B1侧外部机位，在Elena左前侧朝椅后Madison，镜高1.65m，近正脸，缓推15cm但保持胸上裁切与完整头顶嘴部。'),
shot('S','CU',1.5,'Silas默许她的指控','椅后右看Madison说完，随后垂目Elena，唇收紧、右肩缩半厘米，手贴自己衣缝。','画外B3 Elena','完整指控落下，他仍未出声保护Elena；闭口。'),
shot('E','MCU',1.5,'Elena不接受退场命令','坐B3，手留键区；对方说完才把眼从屏抬起，嘴闭，左肩开始朝后左Madison方向转5度，双脚与臀不动。','画外后左Madison','指控没有促使她起身；准备回应而未开口。')],
'耳麦桌右；M椅后左、S椅后右，不逼近不推拉；Elena坐B3、上身开始向左后转。Madison整段30词按约2.7词/秒急切自然语速预算，12秒含标点气口，属估算；无需倍速。')
group('nb','追问与拒绝',[
shot('M','MCU',2.3,'Madison要求服从','椅后左，脸朝Elena正脸居中，双眼睁大一点，完整问句后收下颌闭口，手仍身侧。','画外右下B3 Elena','见Elena未离座而再施压，不接触她。',10,cam='Elena—Madison连线B1侧外部机位，Elena左前侧向后拍Madison，镜高1.65m，轻推8cm。'),
shot('E','CU',1.3,'Elena切断Madison的话语权','坐B3，承接左肩转动，上身向后左转约35度、头再转向Madison，臀双脚留原位；朝她完整说短句后闭口。','画外左上Madison','回应其追问，眉内侧不扬，嘴角仅收紧一次，终态看Madison。',11,cam='摄影机在B3左后通道、Elena—Madison连线B1侧，面向Elena转来的正脸，镜高1.25m，微仰5cm；视线偏光轴5度。'),
shot('M','MCU',4.4,'Madison被公开拒绝','椅后左双脚不动，接Elena短句后嘴角停顿，左手欲抬又贴回衣缝，眼仍Elena方向。','画外右下B3 Elena','先眼睑短张、再下颌绷紧，不立刻退场或新增对白。Silas在椅后右画外仍闭口旁观，不移位。',cam='与前两镜同为Elena—Madison轴B1半空间，镜高1.65m，在Elena左前侧向后拍Madison。')],
'M椅后左、S椅后右；Elena仅转头上身而椅与脚未换位；耳麦桌右。正反打均在E—M连线B1侧，按机位重推背景，不把前方裁判台复制到女主后墙。')
group('nb','戴耳麦询问裁判',[
shot('E','MCU',2,'Elena把注意力移回比赛','坐B3，从望Madison的上身转回自己的终端；目光降桌右耳麦，双手离键区握住本人耳麦两侧并提离桌面至胸高。','B3桌右本人耳麦','刚拒绝指控，转向可以执行的比赛程序；嘴闭。',view='Elena中央胸上，双手和耳麦在下方可读；M左后、S右后小胸上虚焦原位。'),
shot('E','CU',2,'Elena戴稳本人耳麦','承接耳麦已经胸高，双手上抬到耳侧，头带跨过头顶落发上，软耳罩贴双耳，手指松开落桌沿；透明眼镜未被挤掉。','本人B3终端','耳麦从桌右转至头部，不穿耳、没有第三只手；唇闭。'),
shot('E','MCU',4,'Elena要求正式确认','已戴稳耳麦坐B3，双手落桌沿，抬眼向中央C3裁判；近正脸完整发问，句末闭口，眼仍裁判。','画外中央C3裁判','不再回应后方Madison；语气平稳，肩放松。',12,view='Elena中央胸上完整双眼鼻嘴；Madison左后与Silas右后小胸上轮廓虚焦闭口，各原位。')],
'初态Elena尚未戴耳麦、位于桌右；动作连续转回正面→握提→上抬贴耳→松手；末已戴稳，手落桌沿。M左后、S右后不移动。',('Elena耳机参考.png',))
group('ref','身份核验通过',[
shot('R','ECU',1.5,'裁判台验证灯依次确认','只拍C3前桌边的实体小验证灯列；绿灯由左至右逐个亮，灯不映成文字、台面接触影真实；裁判本人袖口只出现一小片且归属明确。','C3实体灯列','承接Elena询问，呈现联盟核验结果，任何人不发声。'),
shot('R','MCU',2.5,'裁判确认身份','裁判仍坐C3，在灯亮完后由灯列抬头到B3 Elena；正脸完整说短句，末闭口，手停自己桌沿。','画外蓝席B3 Elena','核验确认打断Xavier与Madison的质疑，眉间放松半分。',13),
shot('C','CU',4,'解说员接受新的比赛主体','解说员仍坐C2、与裁判距1m；眼由灯列转B3 Elena，右手停自己的提示卡，唇角轻收、下颌略抬；不站起。','画外蓝席B3 Elena','裁判确认后无声承受结果，终态等待第11集比赛开始。')],
'裁判与解说员均坐原椅；末灯列绿、身份通过，比赛尚未开始。Elena已戴耳麦坐B3，Madison左后、Silas右后；红队六人仍坐且戴耳麦，看台仍坐。')

def ref(p):return '@'+AS[p]+' '+NAME[p] if p in AS else NAME[p]+'（'+PROFILES[p]+'）'
def render(g):
 n=g['group'];sc=g['scene'];scene,anchors,light=SC[sc]; ss=g['shots']; total=sum(s['duration'] for s in ss)
 cast=list(dict.fromkeys(s['p'] for s in ss))
 if sc=='nb':cast=['E','M','S']
 if sc=='red':cast=['X','V']
 if sc=='ref':cast=['R','C']
 refs='；'.join(ref(p) for p in cast)+'；场景 @'+scene+'；'+'；'.join('@'+p for p in g['props'])
 state=NB+RED+COURT+VIEW+g['state']
 if n in (3,4,6,7):state+='Elena耳麦仍在B3桌右尚未戴，双手留本人键区。'
 out=[f'【EP10-G{n:02d}｜{g["title"]}｜九梦2.0 Pro｜720P｜{total:.1f}s】',
 '【组头｜固定画质词与光影基调】',f'固定画质词（Fixed Quality Descriptor）：{Q}',SKIN,
 f'引用锁：{refs}。角色图只取身份、脸型、发型与指定服装；参考板文字不入画，Madison蓝白服属于北桥，Silas的参考标语不替代本集行为。',
 f'空间与状态链：{state}',
 f'光影基调（Lighting Tone）：后现代科技赛事写实质感，钢蓝/月白与红席局部暗红连续，不改变现实场馆几何。{light}人物脸部明亮、五官清晰可辨。皮肤哑光，玻璃眼镜只窄小真实反光不遮眼，衣料吸光、金属小反光、塑料壳低反射，地面接触影稳定。',
 f'节奏结构（Beat Structure）：组型：反应/对白组｜{len(ss)}镜｜共{total:.1f}s；最强拍落在shot {max(range(len(ss)),key=lambda i:ss[i]["duration"])+1}，完整发言收句后才交反应；时长序列'+ '/'.join(f'{s["duration"]:.1f}' for s in ss)+'。本集按用户要求以中近景反应为主、特写辅助，取消默认全景收尾和机械三级景别；完整说话镜覆盖快切默认。',
 '景别循环（Shot Size Cycle）：'+' → '.join(s['size'] for s in ss)+'；相邻机位按主体目光或说话权更换，反打改变镜高/裁切。',
 '视觉动线（Visual Flow）：人物面部始终居中央安全区，视觉从上中眼线至下方归属手部；桌、椅、灯为位置锚。不得让人物贴边，镜头移动服务真实关注变化。',
 f'背景几何：{anchors}可裁出屏正面，不透明背壳不显示任何内容；不得有双面透明屏、眼镜HUD、脸上叠UI。公共S+认证在第9集已出现，本组不另造台词或提前比赛。']
 t=0
 for i,s in enumerate(ss,1):
  p=s['p'];size=s['size'];du=s['duration'];end=t+du
  defaultcam={'nb':'机位在蓝桌前至左前可行通道，同属蓝红席连线看台侧半空间，朝主体近正脸；按坐站镜高Elena1.25m、M/S1.65m','red':'机位在红桌前看台側半空间，R1—R2对话轴桌前侧，镜高1.25m；副队长看画左Xavier，Xavier查屏后看画右蓝席','view':'机位在该观众所在排前侧通道，舞台—观众轴看台通道侧，镜高与坐姿眼高1.25m','ref':'机位在裁判桌前舞台侧，C2—C3轴桌前半空间，镜高1.25m'}[sc]
  camera=s['cam'] or defaultcam+'；触发目光/信息变化后缓推10cm，约4cm/s，读清反应即停，不换焦、不穿桌。'
  crop={'MCU':'胸上裁切，可见身体纵向占画高约80%，头高约35%，顶部留白8%','CU':'头顶至肩锁骨，头高约58%，顶部留白6%','ECU':'只裁归属道具局部，占画高70%，不使用人物巨大脸部'}[size]
  visual=s['view'] or f'仅{NAME[p]}为清楚主体居画宽50%，其他在场者按组头原位裁出画外；前景无人肩、无分身。'
  if sc=='nb' and s['view']:
   visual=visual.replace('Madison',ref('M')).replace('Silas',ref('S'))
  if size=='ECU':visual='只见裁判本人右袖边与C3桌边灯列；解说员在C2画外。'
  audio=f'无对白、无旁白、无额外口型；只可有低电器环境底声，无音乐、无生理音效。'
  if s['dialogue']:
   d=s['dialogue'];ll=DL[d]
   audio=f'唯一发言单元D{d:02d}，只属于G{n:02d}，组内{t:.1f}—{end:.1f}s，{NAME[p]}画内连续原声原口型；完整英文：'+ ' '.join('“'+line+'”' for line in ll)+'。自然语速和标点气口，先说完再切；不重启不倍速，其余角色闭口。无旁白、字幕或音乐。'
  out.extend([f'【shot {i}｜{NAME[p]}｜景别（Shot Size）：{size}｜视角（Angle）：近正脸/细节客观｜运镜（Camera Movement）：有动机缓推｜焦段（Focal Length）：85mm｜duration: {du:.1f}s】',
  f'叙事任务（Narrative Task）：{s["task"]}。'+('组尾留下下一事件的情绪钩子。' if i==len(ss) else ''),
  f'镜头：{camera}。85mm不变，T1.8浅景深；全程焦点锁主体眼睛/指定道具；{crop}。',
  f'画面：{ref(p)}：{s["act"]}透视构图描述：{visual}距相机2—3m；起落幅保持裁切，支撑与原位不变。',
  f'视觉引导（Visual Flow）：重心上中，{NAME[p]}视线落至{s["gaze"]}，偏光轴5—10度；信息/视线切点接，虚化无关背景。',
  '微表演（Micro-Performance）：按画面中的具体部位动作执行，眨眼0—1次且不同步；说话全程双眼鼻嘴完整居中无遮挡，反应人物闭口。',
  f'对白反应（Dialogue Reaction）：{s["react"]}非当前说话人嘴唇闭合；未写路线者原位，反应落下再承下一刺激。',
  '人物背景融合（Subject-Background Integration）：臀/椅或脚/地台真实支撑，手和道具归本人，桌沿与背壳前后正确，接触影连续。',
  '光影细节（Lighting Detail）：推进不改变曝光，转头明暗随主光，眼球仅真实环境反射。',
  f'音频（Audio）：{audio}',
  '运动强度（Motion Intensity）：人物低幅主动作及因果反应，相机单一路径；无随机走位、剧烈环绕。',
  '负面提示词（Negative Prompt）：换脸分身、服装互换、人物消失、瞬移跳轴、穿模、漂浮、第三只手、错口型、非说话者张口、断句吞词重复、贴边遮嘴、直视镜头、眼球发光、字幕水印音乐、背壳显示内容、双面屏、眼镜HUD、蜡塑皮肤、磨皮油光、纹理丢失、肤色拼接、五官糊化、皮肤灰白。'])
  t=end
 g.update(duration=total,model='九梦 2.0 Pro',resolution='720P',cast=cast)
 text='\n'.join(out)
 for label in ['Narrative Task','Visual Flow','Micro-Performance','Dialogue Reaction','Subject-Background Integration','Lighting Detail','Audio','Motion Intensity','Negative Prompt','Fixed Quality Descriptor','Lighting Tone','Beat Structure','Shot Size Cycle','Shot Size','Angle','Camera Movement','Focal Length']:
  text=text.replace('（'+label+'）','')
 override=ROOT/'EP10_G01_参考角度修订.txt'
 if n==1 and override.exists():return override.read_text()
 return text

if __name__=='__main__':
 ROOT.mkdir(exist_ok=True)
 old_file=ROOT/'EP10_平台填充.json'
 old_groups={g['group']:g for g in json.loads(old_file.read_text())} if old_file.exists() else {}
 for g in groups:
  if old_groups.get(g['group'],{}).get('url'):g['url']=old_groups[g['group']]['url']
  g['prompt']=render(g)
  assert len(g['prompt'])<=5000,(g['group'],len(g['prompt']))
  assert 4<=g['duration']<=15
  assert not any(s['size'] in ('MS','MFS','LS','ELS','FS','EWS') for s in g['shots'])
  (ROOT/f'EP10_G{g["group"]:02d}.txt').write_text(g['prompt'])
 all_lines=[line for g in groups for s in g['shots'] if s['dialogue'] for line in DL[s['dialogue']]]
 assert all_lines==EN,(all_lines,EN)
 assert len(set(s['dialogue'] for g in groups for s in g['shots'] if s['dialogue']))==13
 for g in groups:
  assert Q in g['prompt'] and SKIN in g['prompt']
  assert '第三点捕获' not in g['prompt'] and '比分3—3' not in g['prompt']
 ledger=[dict(id=f'D{i:02d}',lines=ll,words=sum(len(x.split()) for x in ll)) for i,ll in DL.items()]
 (ROOT/'EP10_平台填充.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2))
 (ROOT/'英文原台词核对.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2))
 count=collections.Counter(s['size'] for g in groups for s in g['shots'])
 qa=dict(groups=len(groups),shots=sum(len(g['shots']) for g in groups),duration=sum(g['duration'] for g in groups),shot_sizes=dict(count),english_exact=True,maximum_chars=max(len(g['prompt']) for g in groups),audio_timing='文本预算估算；未回放成片，不宣称口型/音轨通过',model='九梦2.0 Pro',resolution='720P',generation_submitted=False)
 (ROOT/'本地核验.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
 (ROOT/'第10集完整提示词.md').write_text('# 第10集完整提示词\n\n'+'\n\n---\n\n'.join(g['prompt'] for g in groups))
 print(json.dumps(qa,ensure_ascii=False));print('Madison long turn',ledger[8])
