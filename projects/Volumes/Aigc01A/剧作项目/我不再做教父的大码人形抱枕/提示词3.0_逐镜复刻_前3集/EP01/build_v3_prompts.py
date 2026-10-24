#!/usr/bin/env python3
"""Local EP01 V3 visual preparation. No browser/network/platform writes."""
from pathlib import Path
import hashlib
import json
import re
from decimal import Decimal

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = HERE / 'source_shots.json'
ASSETS = ROOT / '平台工作/飞书资产下载清单.json'
data = json.loads(SOURCE.read_text(encoding='utf-8'))
assets = {x['index']: x for x in json.loads(ASSETS.read_text(encoding='utf-8'))['assets']}

# Independent visual rewrite: identity/costume follows supplied cards; spatial action follows source.
# E/F/G below are visual-only, not substituted narration or invented dialogue.
ROWS = r'''
1|B|$B仰卧在床头，面部居中占满画幅，头部微微后仰，无明显位移。|$B双眼睁大向上凝视，眼下疲惫，嘴唇微抿，眉眼紧绷。|面部居中对称，微弱冷光划出面部轮廓，睡衣领边只在画幅下缘出现。
2|B|$B位于左上方，右臂斜伸向中央，右手攥住被角并向内收紧。|$B手指用力蜷曲，指节发紧，抓握中轻微颤抖，表现无法入睡的焦躁。|右手与被面褶皱形成对角线，袖口沿用童年睡衣参考，被面纹理随握紧下陷。
3|B|$B仰卧在中景偏左的层叠靠枕上，面向右上方天花板，身体静止。|$B睁眼呆望上方，眼睑疲惫，肩背沉在枕面上，保持无眠的僵滞。|左侧床头、暖光台灯和壁灯衬住人物；右侧保留窗景留白及破晓前冷色天光。
4|P|$P的左手与一名深色袖口成年送行者的手在中央相握，小手缓缓抽离；只见双方手部。|$P手指微蜷，抽手动作迟疑，成年手松开，不新增人物面孔。|中央两手交握后分离，$P袖口严格沿用童年参考；门框与暖色散景虚化在后。
5|P|$P的衣角与鞋尖从左下前景边缘闪入，向大厅纵深迈出一步。|$P步幅小而拘谨，局部入画一闪即过，巨大大厅压住人物存在感。|对称大厅全景先呈现环境，前景地面倒影清楚，左下只露参考服装下摆与鞋尖。
6|P|$P的下半身从左前景进入，右腿迈出，背向镜头朝大厅深处走。|$P小步迟疑，身体重心谨慎前移，衣物自然下垂。|人物下摆与小腿遮挡左前景，水晶灯、大厅家具与反光地面保留对称纵深。
7|P|$P双腿位于左前景，右脚在地面落定，继续向前。|$P落脚缓慢，膝部与脚踝轻微收紧，保持局促的小步态。|左侧清楚呈现下摆、小腿及参考鞋履，右侧与远景留给明亮厅堂。
8|P|$P在左前景迈步，双腿分开形成行进姿态，右脚跟抬起准备前迈。|$P身体重心继续向前，步伐克制，不增加停步回望。|双腿形成V形前景框，鞋影与吊灯光斑倒映在地面，远景对称纵深延续。
9|P|$P停在门缝左缘，侧脸靠近门框朝室内张望，随后轻轻推门。|$P先垂眼观察，再小幅抬眼，肩部收拢，谨慎而紧张。|左右深色门框形成窄缝，只露半张童年侧脸与衣角；门内台灯与护墙板虚化。
10|P|$P侧坐在大床右缘，朝左下方，双手放在膝上，微微前倾准备躺下。|$P低头，双手不安地蜷在膝前，呼吸轻而拘谨。|右三分侧坐人物与左侧床面呼应，靠枕、床头、暖灯作背景；童年参考服装完整延续。
11|B,P|$B从右侧伸出左臂，抓住床面与$P衣料交叠处，向自己一侧轻拉。|$B抓握急切，$P仍在床侧；表现失眠时寻求陪伴的依赖，不加入新动作。|左臂从右侧斜穿画幅，手掌、两人衣料与被面交叠处清楚；双方服装各锁童年参考。
12|B,P|$B侧身弯腰环抱$P，两人上身在被褥间靠拢。|$B环抱后肩膀逐渐放松，$P安静顺势靠近，呈儿童之间的安慰依靠。|以睡衣肩臂与另一人的衣料交叠形成对角线，只露$B少量发梢与下颌；无成人化表演。
13|B,P|$B在左上低头，双臂环住下方$P，下巴靠在肩头。|$B闭眼，呼吸渐稳，抓紧的手指松缓；$P保持安静。|左上侧脸与对角线手臂占主要画面，衣料层次清楚，动作落点是安慰性的肩头依靠。
14|B,P|$P侧卧在左下，$B从右上背后环抱，手臂横在$P身前。|$B眉头舒展睡去，$P睁眼望向暗处，小手停在$B手臂旁。|双人居中，暗部包围，头枕肩侧；只表现童年陪伴与安眠，保留原镜左右位置。
15|B,L|十年后，$B半靠在右侧床头；$L背向镜头坐在$B腿上并俯身贴近，$B单手扶住腰背。|$B垂眼，神情疏离，$L主动靠近；全程着各自指定睡衣。|双人在右三分，左侧床头台灯与花束留白，床尾家具可见；身份与服装替换为成年参考。
16|B,X|$B半躺在右侧，$X依在左侧，右手轻触$B胸前衣料。|$X闭眼靠着，右指轻动；$B偏头看向另一侧，嘴角绷紧，反应冷淡。|双人卧姿中心偏右，另一情人位于左侧；不将本镜人物冒认为主要情人，服装留待对应参考。
17||无人出场，镜头停留在空床、床单与孤立靠枕。|以静止的床面和空置位置表现离场后的冷清，不让人物返场。|焦点在左前景靠枕与床单褶皱，右后台灯、相框及白枕浅景深虚化。
18||无人出场，镜头俯看床面散落物。|所有物件保持静止，延续空床的余温与凌乱感。|一只香槟金细高跟鞋、揉皱丝绸衣物、金属烟灰缸与倒放透明高脚杯沿对角线散落；不添加人物。
19|B|$B居中靠床，抬左腕看表，随后放下手臂，抬眼看右侧门口。|$B先垂眼确认表面，随后眉头微蹙，视线由表转向门口，带习惯性的等待。|居中胸像，左腕动作和右前方视线清楚；睡衣领口、纹身及面容严格从成年参考读取。
20|Y|$Y赤脚背向镜头，从中央穿过卧室门口走向外侧走廊。|$Y背对镜头离开，步伐顺从，睡袍随步幅摆动，不回头露新正脸。|两侧门框形成纵深，背影与赤脚踩在地毯上；该背影身份和参考服装待明确，不冒认上一情人。
21|B,P|$B靠右侧床头，$P从左边缘步入，朝大床走。|$B目光追随$P入画，神情自然放松；$P安静走来。|起点先见右侧独坐的$B，随后$P从最左入画；床头灯留在左侧，双方成年睡衣参考不变。
22|B,P|$B靠左侧床头；$P从右前景背向镜头爬上床，侧身躺下，$B伸右手扶住腰背揽近。|$P垂眼熟练躺入，$B肩颈放松，右手自然承接体重。|右前景背影入怀与左中景接应者形成过肩层次；右后窗外深蓝夜色与暖灯对照。
23|B,P|$P仰卧在左下，$B从右上靠近脸侧，右臂横过肩头环住。|$B闭眼轻贴额角后平静入睡，$P睁眼望向左上，神情清醒疏离。|双人中心构图呼应14，肩头环抱与枕面清楚；保持$P成年大码体型与指定睡衣。
24|P,B|$P仰卧枕上，面部居中；右下前景是$B睡衣肩臂，$P由合眼缓缓睁眼。|$P先安静闭目，随后眼睑缓慢抬起，眼神由温顺转为清醒平静。|面部大特写与右下虚化肩部遮挡并存，发型肤色来自大码参考，不沿用源人物面容。
25|P,B|$P面部居中，承接睁眼落点凝视斜上方；$B肩部仍在右下。|$P目光稳定，嘴唇微抿，保持短暂的清醒停顿。|面部特写轻微提亮，构图与24保持一致，为下一镜白闪准备；不另加闭眼动作。
26|P|$P面部特写逐渐淡去，与后续合同桌面的画面开始叠化。|$P清醒目光在柔白光里隐去，不增加对白或新的表情转折。|保持面部中心构图，白光渐满，脸部轮廓透明化，转向会客厅桌面。
27||身份未明的一只手从左侧触及桌面纸张边缘，白光中只显出手与文件轮廓。|手指停在页边准备翻页，不补出手主人的身体或脸。|白闪尚未散尽，纸张与左下手部依稀显现；文件外观引用续约合同参考。
28||一只身份未明的左手从左伸入，拇指食指捏住合同左下角，缓慢翻页。|手指干净整齐，翻页动作轻缓克制，身份不作推断。|深色桌面上摆续约合同，手指翻起上层纸页，条款密集但不把微字可读作为剧情唯一线索。
29|M,P|$M端坐中央偏右扶手椅，双腿交叠，双手十指交叉放膝上；$P局部肩背在最左前景。|$M坐姿挺拔，手指交扣，保持审视的僵稳；参考帧头部受上沿裁切，不强行补全脸。|左前景肩背形成过肩遮挡，主体落在$M交握双手、坐姿与腿部；母亲服装改用指定浅粉套裙。
30|B|$B坐豪车后座左侧，低头朝右下看手机，右拇指滑动屏幕。|$B眉头微锁，注意力持续落在屏幕，侧脸冷峻专注。|透过半降车窗取景，真皮座椅包围侧脸，手机微光照面，窗外夜光掠过；服装用成年日常参考。
31|B|$B的手位于中央偏左，握紧方向盘左上方并微调方向。|手指有力扣紧方向盘，前臂绷紧，只有小幅校正动作。|方向盘与手形成对角线，仪表弱光在下；前挡雨滴、移动车灯散景在后，车内参考延续。
32|B|$B靠在车座中央，抬右手扶前额并揉按眉心。|$B闭眼，眉头紧蹙，手指按太阳穴与额头，嘴唇微张，疲惫烦躁。|面部居中，右手遮部分眼睛和前额，车厢冷暗侧光凸显疲劳，成年日常服装与身份不变。
33|P|$P端坐桌后居中，头微低，目光落向桌面。|$P安静垂眼，嘴唇轻合，肩背保持稳定，情绪不外露。|正面中近景，桌面在前，椅背承托人物，右后暖壁灯虚化；保持成年大码日常参考。
34|P|$P坐背景中央，画幅切至下巴以下；一份续约合同滑向$P并停在前景中央。|$P不动，双手不抢拿文件，合同滑停后保持短暂停顿。|前景合同由虚转清，背景胸像虚化；原要求可见标题“EMPLOYMENT RENEWAL AGREEMENT”保留，文件形制沿用参考。
35|M,P|$M居中，右手将碎花骨瓷茶杯凑唇轻抿，再放回左手托着的茶碟；$P局部头部虚影在最左。|$M从杯沿上方盯着$P，放杯后嘴角微抿，目光笃定轻蔑。|左缘虚化头部形成过肩层次，茶杯短暂遮嘴；母亲浅粉服装、盘发及首饰严格锁参考。
36|P|$P侧坐左侧扶手椅，面向右，双手交握放腿上，身体不动。|$P目光停在前方合同，垂眼长久沉默，手指交叠不松开。|左三分侧脸朝右，右侧保留木桌与暖灯背景；日常衣料沿用大码参考，不出现源百褶短裙。
37|P,M|$P正面居中，从垂眼缓缓抬眸直视前方，轻启双唇；$M肩头虚影在右下。|$P先抬眼，再轻微抬头，眼神平静坚定，双唇清楚开合；确切英文对白在独立槽位待统一回填。|正面过肩近景，右下虚化母亲参考服装肩部，注意力集中在$P抬眼与说出拒绝的嘴形。
38|M,P|$M坐右侧端茶杯茶碟；$P背影肩头占左前景。|$M表情由笃定僵住，双唇微张、眉头收起，端杯的手停在半空。|未签合同在桌面，左前景背影与右侧母亲构成过肩，保持源镜左移；拒绝句的说话者不改成母亲。
39|M,P|$M在右侧端茶凝视，$P背影仍在左前景，位置承接上一镜。|$M收起惊愕，抿唇看向前方，保持短促冷淡反应。|画面迅速压暗，母亲端茶身影隐入黑场，完成会客厅到酒店的转场，不删本0.1秒镜。
40|P|$P从走廊深处靠右墙向前走来。|$P神情平静，迈步克制，不新增停顿或视线回望。|冷暗酒店走廊全景由暗渐显，右侧门墙形成纵深；人物保持指定大码日常服装。
41|P|$P从左后走向右侧套房门，停步，伸左手握住门把。|$P先垂眼，走到门前才抬手，左手轻搭门锁，动作例行而从容。|由中全景落到中景，人物在右侧门前停住，门缝透暖光，走廊与门内冷暖对照。
42|L|右侧门扇遮住画面大部，左边缘只露$L的发际与少量发梢，轻轻移动。|只让发梢随房内小动作晃动，不提前展示完整脸。|门板占右侧约三分之二，左侧少量人物轮廓与纱帘见暖逆光；头发长度按情人参考卡适配。
43|L|$L位于中央偏左，微向右移，逐步从门框遮挡后露出面孔。|$L双目微闭，嘴唇轻抿，神态慵懒；先保持遮挡，再逐渐看清脸。|右前景门框持续虚化，左侧人物按参考睡衣入画，浅纱与暖光在后，不提前取消遮挡。
44|L,B|$L侧脸在中央偏右，朝右前方；$B头部与肩的虚影掠过左下边缘。|$L眼神轻转，嘴唇微张，呼吸稍促，动作幅度很小。|侧脸特写为主体，$B只作左下模糊遮挡；人物面容、发型与肤色均依各自参考。
45||无人出场，镜头停在刚换过的白色床品。|微皱床单保持静止，以空床与暖光承接室内余温。|白色床单、被套、层叠白枕形成对角留白；暖侧光在褶皱间留阴影，后方床头柜虚化。
46|L,B|$L侧脸居中朝右，眼睛微闭，胸口轻随呼吸起伏；$B肩头虚影留在左下。|$L低眼睫、微张双唇，呼吸由稍促趋缓，保留慵懒神态。|侧脸大特写，暖侧逆光落在面部，肩部覆盖与领口严格从参考睡衣，不复制源裸肩服装。
47||无人出场，镜头俯看床边地毯上一只侧翻的细高跟鞋。|鞋与床单垂角静止，不把鞋移动到床面。|鞋位于地毯中央，左后台阶状白床单角落入画，地毯花纹与鞋的侧翻姿态明确。
48|B|$B半靠床头居中，左手抬起轻搭额角，垂眼看向右下。|$B肩背松弛，眼神倦怠而疏离，嘴唇自然合拢，左手停在额侧。|从胸像缓缓上摇至脸，成年日常参考服装不变，床头与白床品衬住半躺姿态。
49|L,B|$L在中央偏右朝左上看$B；$B后脑与侧脸虚影占左下前景。|$L先小幅翻眼嗔怪，再抬眼注视$B，双唇微嘟，眼神转为期待。|过肩近景由左前景虚影引向右侧情人正侧脸，镜头缓推，背景维持暖光。
50|B,L|$B半靠左侧床头、左手支额；$L从右前倾，凑近$B面前。|$L仰脸靠近、双唇开合带央求，$B不移开支额手，冷眼看着，表情不松动。|双人侧面左右相对、鼻尖接近，视线相接；双方服装身份从参考，不更改动作与位置。
51|P|$P从半开的房门外缓步走入并停在左侧，目光先向床面，再垂下。|$P看一眼后避开视线，肩背稳定，双唇轻合，平静而疏离。|右侧门板与金属锁形成前景框，左后走廊冷蓝、室内暖光分割；大码日常体型不变。
52|L,B|$L位于中央偏右，越过左下$B肩头，转头看门口$P。|$L先皱眉上下打量，再夸张撇嘴，目光由疑惑转为嫌弃。|左下前景肩部虚影不动，焦点留在$L转头及撇嘴反应；门口$P不因此新增入画。
53|L|$L下半张脸和嘴唇居中，承接闭唇起点开口说话。|$L双唇由合至开，嘴角收紧，傲慢不耐；确切英文见对白槽位。|鼻唇下半脸极近特写，嘴部为唯一清晰主体，唇形与肤色沿用参考，不把源唇妆强套男版。
54|L|$L嘴唇居中，接上镜继续说完同一句，随后下巴微扬。|$L双唇完成后半句并合拢，下巴小幅抬起，神情轻蔑。|延续嘴部大特写和中心构图，连贯接上镜，不另生成一条新说话者。
55|B|$B面部居中，左手支额，听完后嘴角缓缓扬起，轻笑。|$B眼睛微眯，鼻翼轻动，嘴角由冷淡转为玩味；只作轻笑表演，不朗读括号舞台说明。|眼鼻唇大特写，左手指轻抵太阳穴，身份面容锁成年参考。
56|B|$B半靠床头居中偏右，左手支额，右手随意一挥，双唇开合。|$B先微闭眼轻笑，再小幅摇头，右手随口摆动，神态笃定散漫。|中近景侧胸像，床头与日常参考服装延续，右手动作清楚。
57|L,B|$L在中央偏右，左下$B肩部虚影不动，$L视线在$B与门口方向之间扫动。|$L瞳孔紧缩后瞪大，眉头微蹙，双唇张开，震惊中转向门口。|过肩近景清楚捕捉表情崩塌与眼神转移，$B肩部保持浅景深遮挡。
58|B,L|$B靠左床头支额，$L在右侧激动前倾逼近，面对面质问。|$L皱眉抬眼，嘴唇快速开合，肩部前压；$B不回避，脸色平静。|双人左右对称对峙，背景暖纱幔延续，服装不切换，保留近距离张力。
59|B,L|$B仍靠坐左侧，$L在右侧说完后紧盯$B。|$L胸口轻起伏，咬唇等待；$B保持平静，承接上一镜尾音而不新加台词。|保留58双人对称与鼻尖相对的位置，本0.2秒为质问后的短反应。
60|B|$B居中斜靠床头，左手握拳支额，从闭眼到睁眼，斜看左侧门口。|$B缓慢抬眼，把注意力从情人移到门口$P，目光收紧，嘴角微动。|半躺撑头胸像居中，镜头微仰，视线落在左侧；日常衣领、纹身形态仅用参考。
61|B|$B正脸居中占满画幅，始终注视画面左侧门口。|$B眼睛聚焦左侧，双唇微张后轻抿，嘴角带若有若无的笑，呼吸慢下来。|正面大特写突出目光和细微口部变化，面容发型不沿用源演员，背景压暗。
62|B,L|$B在中右侧斜靠床头朝左，前景左侧$L肩部轮廓虚化；$B微抬头开口。|$B先垂眸浅笑，再轻启双唇，眼神玩味，反问动作漫不经心。|左前景情人头肩柔焦，右侧老板侧脸清晰；耳后及领口细节以各版参考锁定。
63|B|$B半躺在左侧至中央，身体斜朝右下，一边说完话一边抬右手准备取支票。|$B眼睛微垂，嘴唇完成后半句，随后身体微动，右手进入取物动作。|中近景向下并向右摇，衔接胸像至取物区；床单和背景窗幔保持原空间关系。
64|B|$B半坐左侧，右手从下方抬起，向右伸去拿支票与钢笔。|$B动作熟练果断，不停顿寻找，肩臂随右手微向前。|切头中景，躯干与伸臂形成对角线，中景白床单清楚；手臂肤色和袖口从日常参考。
65|B,L|$B左手固定支票本，右手持黑色钢笔快速签字；$L少量头部边缘在画幅右侧。|左手稳定托纸，右腕连贯写动，笔尖不离开签名区，动作干脆。|双手签字中心偏左，浅蓝支票、黑银钢笔和白床单清楚，右缘只留情人参考轮廓。
66|B|$B双手位于左上，左手捏起签好支票边缘，右手握笔配合，准备撕下。|左手掀纸，右手微顿保持纸本稳定，表现熟练敷衍。|双手和两张支票沿对角线展开，白被角在下；腕表作为源动作道具保留，服装不变。
67|B|$B右手夹钢笔同时捏住撕下的支票，迅速向右上递出；左手向左后收回。|右手扯下后顺势递出，动作短促，手指保持对纸与笔的握持。|特写保留由左下到右上的动态模糊，下方黑裤与白被面构成底色。
68|B|$B右手从左下向右前甩出支票，纸张落向白床单，另一手持笔留在腿边。|右手一挥后松指，动作随意傲慢，不让钢笔随支票飞出。|前景手部挥动模糊，浅蓝支票向右下落在床单；黑裤腿在中景。
69|B,L|$B持笔手从左边缘收回；$L跪坐右侧床面；两张支票平摊在右下床单上。|$L低头看膝前两张支票，身体微僵，双手尚未拿钱。|两张浅蓝签字支票清晰交叠在白床单，左侧老板裤腿、右侧情人膝部仅作局部参照。
70|L,B|$L跪坐右上，左手搭膝侧；$B腿部在左后；两张支票静置前景中央。|$L迟迟不伸手，膝与肩保持僵硬，用停顿呈现不甘。|焦点落在两张支票，右后人物与左后裤腿虚化，支票数量不简化为一张。
71|B|$B靠中央偏右床头，抬左手朝侧方挥动示意离开，双唇开合。|$B斜眼看左侧情人，嘴角带淡笑，挥手轻慢而明确。|正面偏侧胸像居中，左手由身前上挥，左前景白枕角保留。
72|P|$P笔直站门边正中，双臂自然垂下，先看前方再缓缓垂眼。|$P眼神平静，垂睫后表情仍无波澜，不新增哭泣或争执。|正面中近景，门厅冷灰暗部与室内暖光交汇，大码日常参考身形、肩颈与衣装稳定。
73|P|$P站画面左侧，侧脸朝右看大床，身体静止。|$P稍抬下巴，目光平静略倦，双唇闭合，安静等待。|左三分四分之三侧脸，右侧留视线空间，门框与墙面浅景深虚化。
74|L,B|$L跪右后，右手从右上探下，五指按住前景床单上两张支票；$B裤腿在左后。|$L右手猛按纸面，指尖收拢准备抓起，动作带气性。|手抓两张支票位于中心，右后膝部和左后老板腿部维持原方位。
75|L,B|$L右手抓起两张支票向上猛提，仍跪坐在右后。|手指捏紧纸边，动作急促，支票随上扬弯曲。|手与两张浅蓝支票居中，向上的动态模糊清楚，背景膝部与老板裤腿不移位。
76|L|$L的右手在上方，把抓起的两张支票用力往下甩向床面。|右腕发力向下，手指不提前松开，表现受辱后的拒绝。|高举手与下甩支票形成对角线，纸张在半空弯曲模糊，白床单承接下落。
77|L|$L手掌带着两张支票迅速下落，拍向床面。|下拍动作干脆，承接76，不重新起一次抬手。|高速模糊残影沿对角线落向白床单，右侧保持情人膝部局部。
78|L,B|$L跪右侧，把支票拍在前景床单上后将右手迅速抽回右上；$B腿部在左。|手掌压平纸张后立刻离开，动作利落而倔强。|床单上两张支票留下，手向右上移开；左侧裤腿与搭腿的手、右侧膝部构成参照。
79|L|$L正脸居中，下巴高抬，眼睛先向上翻，再斜看左侧$B。|$L翻眼后紧抿双唇，鼻翼轻动，摆出高傲不屑姿态掩饰挫败。|低机位仰拍正脸，面部居中，发型、妆面及肩部覆盖严格用情人参考。
80|L,B|$L肩头与头部占左前景虚化；$B位于右侧朝左注视情人。|$B笑容收敛，眉头微蹙，带审视地听$L说话；说话者仍为前景情人，焦点人物不抢口型。|过肩特写左半被情人轮廓遮挡，右侧老板四分之三侧脸清晰，双方位置不互换。
81|B,L|$B斜靠左侧床头朝右；$L坐右侧床面前倾朝左，两人近距离相对。|$L抬眼逼视，双唇开合，故作潇洒；$B静看，脸色无明显改变。|双人中景左右对称，视线相接，中间与后方保留纱幔及暖灯。
82|L,B|$L正脸居中，说完后嘴角微扬准备转身；$B肩部虚影留左下。|$L直看左前方，双唇说动后闭眼，嘴角扬起带不甘的笑。|中心近景保持左下过肩暗示，情人发型与服装沿用同一参考，不在退场前换装。
83|L|$L在中央偏左，迅速由朝左转头向右，准备下床。|$L嘴角留倔强冷笑，转头果断，随转动带起发梢或衣领。|侧脸向右的动态近景，暖光勾边，发型长度按参考适配，不给短发人物生出长发。
84|L|$L继续向右大幅转过身体，承接83同一转身阶段。|$L不停顿，肩背跟随头部转动，离场态度决然。|中心动态快切，头部和右肩带运动模糊，不能退回上一镜起始姿态。
85|L|$L背向镜头，向右前方门口走去。|$L挺直背脊迈步，保持高傲离场，不回头。|右三分背影柔焦，左侧纱幔留白，逆光落在参考发型与肩线。
86|L|$L背影沿右侧向画外继续移动，承接上镜行进。|$L步伐快而果断，头肩随走动微起伏。|背影朝右下移动，左侧窗幔与深色窗框虚化，保持快切与离场动态。
87|L|$L从右侧迈入画面，走向中央偏左的房门开口。|$L走路急促，肩背挺直，动作直奔房门。|半开门框居中分割画面，人物自右入画，衣装与鞋履按同一睡衣参考，不凭空换成日常正装。
88|L|$L背向镜头从右快步穿门离开，左手顺势带门。|$L头也不回地出门，左手带门后放开，身影离开室内。|背影穿过居中门框，左手与门板关系清楚，走出后门扇缓慢合拢。
89||无人出现，镜头停在情人离开后的门扇与门框。|门扉承接88合拢后静止，室内恢复安静，不让情人再次入画。|门框垂直线居中，门锁和门缝细节可见，暖光落在门板凹凸线条上。
90|B|$B右手位于中央偏下，捏起拍回的支票，拇指缓缓摩挲纸面。|右手先拿纸再用拇指轻擦，动作比先前甩钱放慢，显出意外。|手与一张被拿起的支票呈对角线，黑裤与地面虚化；床面其余支票不凭此镜消失。
91|B|$B正脸居中，右手捏支票举在下前景，垂眼看纸。|$B眼神短暂怔住，双唇微张，眉眼出现罕见讶异。|脸部大特写，前景支票边缘虚化，右手指尖位置按本镜原表保留，不虚构换手过程。
92|B|$B靠中央偏右，左手捏支票后放下，抬头看左侧$P。|$B先看纸失神一瞬，再收敛表情，放纸并转眼向$P。|右三分中近景带轻微上摇，保留源表左手拿纸；91右手到92左手的切镜衔接不加新镜。
93|P|$P从左侧窗幔旁缓步朝中央大床走。|$P垂眼，步幅轻缓，表情平静无明显期待。|左前景窗幔与下前景床单引导，人物从左移向床边，远景窗帘、沙发与暖灯留在原侧。
94|P|$P位于左侧，继续朝右前方$B方向走近。|$P视线低垂，双唇轻合，保持平静，不增加质问动作。|左三分侧脸朝右，右侧台灯平衡画面；成年大码日常体型不因近景变瘦。
95|P,B|$P站左侧；$B从右下前景起身贴近，伸臂把$P拉向怀中。|$P顺势靠近，微微抬眼看$B，目光仍平静；$B动作熟练。|右下老板背侧轮廓虚化，左侧$P受光面部清晰，双方距离缩短但左右方位不变。
96|P,B|$B在左后方双臂环住右前景背向镜头的$P腰部，低头把脸靠向肩颈。|$B闭眼、肩膀松下，双臂收紧；$P保持平稳站姿，不推拒也不新增迎合动作。|右前景$P后背和参考发型遮挡部分画面，左后$B闭眼靠近，保留大码腰腹宽度。
97|P,B|右前景为$P头部与肩领；左中景$B闭眼将脸靠在肩颈处。|$B眼睫轻颤后稳定，呼吸渐缓，额部与鼻尖贴近肩颈；$P安静不动。|右侧参考发型和衣领形成前景，左侧仅见老板半张脸，保持左右分割与贴靠落点。
98|B|$B肩部暗影留在左下前景，中后景为床单与垂直纱帘。|人物只以模糊肩影出现，床单和纱帘保持静止，用余光视点承接前镜。|左下肩影浅景深，大片浅色床面与窗纱留白，只有肩部入画。
99|P,B|$P面向镜头位于左侧；$B背向镜头在右前景拥抱，后衣领上有一枚鲜红唇印。|$P垂眼看向近处后衣领，视线微凝，嘴唇轻合，表情由平静转冷。|过肩近景，右前景背影与衣料唇印引向左上$P眼神；唇印在衣领布料而非皮肤。
100|B|$B后颈与后衣领居中，衣领偏左的一枚鲜红唇印清楚可见。|人物不转身，镜头只强调静止的布料痕迹，不让唇印挪到颈部皮肤。|主观俯拍大特写，上方参考发尾及后颈，下方参考衬衫后领，左侧唇纹清楚的红色印记。
101|P,B|$P正脸居中，视线低落在右下方$B衣领；$B肩部虚影在右下。|$P看着印记，轻抿一次嘴唇，不哭、不争执，眼神沉静疏离。|面部大特写与右下肩影遮挡并存；大码参考面容和脸部轮廓保持稳定。
102|B,P|$B站中央，左手抱$P后背，右手托住大腿与臀部，把$P抱离地面；$P双臂环颈。|$B维持脸靠肩颈姿势、双臂发力；$P随抱起收拢手臂，保持全身衣物覆盖。|双人相拥抱起居中，左后台灯花束、后墙画框可见；被抱者的大码体型不缩小，支撑位置明确。
103|B,P|$B抱着$P朝右侧大床转身，左手按背、右手托大腿。|$B闭眼轻贴侧脸，抱持稳定；$P环颈手臂不松开，承接上一镜离地姿态。|双人抱姿居中，右下白床单接应转身方向，衣物随转身自然摆动，不凭空换装。
104|B,P|$B在左、$P在右，保持托抱面对面贴近，向右侧床沿移动。|$B微闭眼，$P垂眼，双方鼻尖接近；手臂支撑持续，不落地再抱起。|双人侧面对称抱姿居中，右侧白枕床单接应动作，完整保留大码躯体比例。
105|B,P|$B在左俯身，扶住$P腰背与腿，将$P放到右侧床沿坐下。|$B低眼看怀中人，托扶动作放慢；$P手臂仍搭肩，重心落到床沿。|左侧俯身、右侧坐床，坐下后的床面凹陷可见，背景画框与窗帘保持位置。
106|B,P|$B从左侧倾身，护住$P后背并扶腿，带$P向右侧枕头躺下。|$P从半坐顺势仰躺，手仍搭$B后颈；$B承接体重，动作连贯。|双人在中左，右侧枕头承接躺倒，白床面与双方参考日常衣料受暖光照明。
107|P,B|$P仰躺右下白枕；$B从左上俯身，先贴肩颈，再撑起一点观察$P。|$P先微阖眼后睁开，仍平静；$B从贴靠转为抬头，眉头微蹙、视线落在脸上。|双人呈左上与右下对角线，背景暖色圆形光斑，近距离对视承接贴颈动作。
108|B,P|$B俯身正脸居中，右下前景仅见$P虚化手部和脸缘。|$B低头凝视右下，眉心轻收，双唇微启，眼神由敷衍转为探询。|正脸大特写微仰，右下前景轻遮挡，面容与肤色锁成年参考。
109|B,P|$B俯身侧后影占左前景；$P仰躺中右白枕，抬眼并抬手指向$B衣领。|$P脸上无明显妒意，眼神平静，手指客观地指向衣料上的印记。|俯拍过肩中近景，左前景老板轮廓虚化，右侧仰躺者脸与指向衣领的手清楚。
110|P,B|$P仰躺中央偏右，目光从$B眼睛下移到衣领；$B额部鼻尖轮廓留左前景。|$P神情淡然，嘴唇轻启说话，指向落点仍是衣领，不将源视觉改成脖子吻痕。|俯拍面部大特写，左上轻微过肩，眼神方向和参考衣领在边缘可见。
111|B,P|$B在左中景俯身，低头看右下前景$P侧脸。|$B先怔一下，再舒眉、弯眼，嘴角扬起明显温和笑意。|右下$P鼻尖脸颊柔焦，主体是老板由严肃转笑的面部，暖背光勾勒参考发型。
112|B,P|$B在左上撑床俯身，$P仰躺右下白枕，两人保持近距离对视。|$B眼神温和，嘴唇开合，带耐心迁就；$P保持安静听着。|过肩中近景沿左上至右下对角线，右下是仰躺者脸和衣领，空间方位不改变。
113|P|$P仰躺正中，眼睛望向左上，双唇紧抿。|$P嘴唇向内轻抿，下巴微绷，保持沉默，不新增回答台词。|俯拍微侧面部大特写，暖光照脸、背景压暗，视线与上镜老板位置对应。
114|B,P|$B俯身面部居中，右下$P侧脸虚化。|$B先垂眸想一瞬，再带浅笑将目光重新落在$P脸上。|过肩大特写，右下虚化轮廓承接对视，暖背光与侧光保持温和。
115|B,P|$B从左侧双手撑床俯身，$P仰躺中右白枕、双手交叠身前，双方对视。|$B低眼轻启双唇，目光温和笃定；$P只静看，不先说出离开真相。|侧面中全景沿左上与右下呼应，前景白被、背景双灯与窗幔保留；双方全程参考日常衣装。
116|B,P|$B仍左侧撑床俯身，$P右侧仰躺，保持四目相对。|$B说完后等待，$P沉默，双方不开始新动作。|保持115构图，浅白柔光刚开始覆盖，短镜独立保留。
117|B,P|$B在左俯身、$P右侧仰躺，双人轮廓在白光中静止。|双人维持相对姿态，眼神不移开，用定格延续悬念。|约六成白闪覆盖，仍隐约可见左侧深色肩背与右侧仰躺轮廓及后台灯光晕。
118|B,P|$B和$P继续保持俯身与仰躺的对视姿态，隐在强白光中。|不添加动作，保持上镜落点，悬念停住。|白闪接近全白、约八成半覆盖，仅残留两人轮廓和背景双灯弱形，本0.2秒不删除。
119|B,P|$B左侧撑床，$P右侧白枕仰躺，白光消退后仍对视。|$B专注温和，$P平静淡然，动作保持不变。|白闪退去、暖调恢复清晰，台灯与窗幔重现，参考发型与服装回到同一位置。
120|B,P|$B在左俯身微靠近一点，$P在右仰躺，双方继续对视。|$B等待回答，$P安静看着，移动幅度仅分毫。|中心双人中全景，边缘轻微彩虹色散与发光，暖灯勾勒侧脸，不重新排姿势。
121|B,P|$B在左俯身、$P在右仰躺，双人定格对视。|$B表情温和笃定，$P目光清醒平静，维持悬念。|中心双人构图，白枕、深窗帘与右侧束起窗幔延续，边缘柔光色散保留。
122|B,P|$B左侧撑在床单上俯身，$P仰躺右侧白枕，最终定格对视。|$B温柔等待，$P平静不语，保持最终对视姿态。|结尾中全景保持122原构图，暖金双灯、白床品与窗幔作背景，所有大码体型与衣装锁到本镜结束。
'''.strip()

rows = {}
for line in ROWS.splitlines():
    n, roles, e, f, g = line.split('|')
    rows[int(n)] = {'visible_roles': roles.split(',') if roles else [], 'E': e, 'F': f, 'G': g}
assert list(rows) == list(range(1, 123))

VERSIONS = {
    '女版': {'P': ('大码Eliza', 1), 'B': ('Matteo Bellandi', 9), 'L': ('Alessia Varenna', 20),
             'young_P': ('童年Eliza', 7), 'young_B': ('童年Matteo', 16),
             'sleep_P': 3, 'sleep_B': 11, 'bed': 47, 'hall': 45, 'corridor': 46, 'reception': 48,
             'X': ('另一位红发成年女情人', None), 'Y': ('离场成年女情人', None)},
    '性转男版': {'P': ('大码性转男主', 2), 'B': ('Vittoria Blackwood', 12), 'L': ('性转男情人', 19),
                 'young_P': ('童年性转男主', 8), 'young_B': ('童年Vittoria', 17),
                 'sleep_P': 4, 'sleep_B': 13, 'bed': 53, 'hall': 51, 'corridor': 52, 'reception': 54,
                 'X': ('另一位红发成年男情人', None), 'Y': ('离场成年男情人', None)},
}

APPAREL = {
    1: '米白针织开衫、浅碎花连衣裙及配套鞋袜，成年大码体型与宽腰腹始终稳定',
    2: '白衬衫、米色短裤及配套鞋袜，成年大码体型与宽腰腹始终稳定',
    3: '米白宽松短袖睡裙及参考鞋袜，成年大码体型始终稳定',
    4: '藏蓝白滚边长袖长裤睡衣及参考拖鞋，成年大码体型始终稳定',
    7: '童年参考的米白开衫、浅碎花裙与鞋袜，保持童年身份',
    8: '童年参考的白衬衫、米色短裤与鞋袜，保持童年身份',
    9: '酒红衬衫、黑裤及参考鞋履；面容肤色、发型和纹身位置均取参考',
    11: '黑丝质白滚边睡衣及配套裤装，不沿用源金边睡袍',
    12: '黑衬衫、黑裤及参考高跟鞋；面容肤色、发型和纹身均取参考',
    13: '黑色蕾丝边睡袍，领口、袖口、下摆均锁参考',
    16: '童年深色纹样系带睡袍，保持童年身份与普通安慰性表演',
    17: '童年深色纹样系带睡袍，保持童年身份与普通安慰性表演',
    19: '黑金纹样系带睡袍、参考赤脚状态，短发及面容锁参考',
    20: '浅粉系带蕾丝睡袍与内搭、参考赤脚状态，金发及面容锁参考',
    22: '浅粉套裙、盘发、珍珠首饰及参考鞋履',
}

def role_map(version, n):
    v = VERSIONS[version]
    out = {c: v[c] for c in ['P', 'B', 'L', 'X', 'Y']}
    out['M'] = ('Serafina', 22)
    if n <= 14:
        out['P'], out['B'] = v['young_P'], v['young_B']
    elif n <= 26:
        out['P'] = (v['P'][0], v['sleep_P'])
        out['B'] = (v['B'][0], v['sleep_B'])
    return out

def expand(text, mapping, refs=False):
    def one(m):
        name, idx = mapping[m.group(1)]
        if refs and idx is not None:
            return f"{name}（@{assets[idx]['local_asset_name']}）"
        return name
    return re.sub(r'\$([PBLMXY])', one, text)

def camera_adapt(text, version, n):
    m = role_map(version, n)
    # Replace identity and costume labels only; every spatial/camera instruction is retained.
    aliases = dict([
        ('男主情人', m['L'][0]), ('金发女伴', m['L'][0]), ('女伴', m['L'][0]),
        ('教父夫人', 'Serafina'), ('女主', m['P'][0]), ('男主', m['B'][0]),
    ])
    text = re.sub('|'.join(re.escape(x) for x in sorted(aliases,key=len,reverse=True)),lambda x:aliases[x.group()],text)
    changes = [
        ('左前景金发虚化', '左前景情人头部边缘虚化'),
        ('金发边缘', '情人头部边缘'), ('金发', '情人头部轮廓'),
        ('秀发', '参考发型'), ('甩动的情人头部轮廓', '转动的情人头部轮廓'),
        ('酒红肩部', '参考服装肩部'), ('酒红', '参考服装'),
    ]
    for a, b in changes:
        text = text.replace(a, b)
    return text

def scene_indices(version, n):
    v = VERSIONS[version]
    if n == 4:
        return [v['corridor']]
    if 5 <= n <= 8:
        return [v['hall']]
    if n <= 25:
        return [v['bed']]
    if n == 26:
        return [v['bed'], v['reception']]
    if 27 <= n <= 29 or 33 <= n <= 39:
        return [v['reception']]
    if 30 <= n <= 32:
        return [82]
    return [37]

def environment(version, n):
    v = VERSIONS[version]
    scenes = '至'.join(f"{assets[i]['local_asset_name']}（@{assets[i]['local_asset_name']}）" for i in scene_indices(version, n))
    if n == 1:
        mood = '十年前深夜，极暗冷蓝月光斜照脸部，四周深暗，孤寂压抑。'
    elif n == 2:
        mood = '十年前深夜，微暖床灯照被面，强烈明暗对比，焦躁压抑。'
    elif n == 3:
        mood = '十年前破晓前，室内暖金暗调与右侧窗外冷蓝微橙天光对照，空旷孤寂。'
    elif n == 4:
        mood = '十年前夜晚，卧室门外，暖黄背景光在暗木色空间里虚化。'
    elif 5 <= n <= 8:
        mood = '十年前傍晚，暖金吊灯与窗外冷青暮光交织，厅堂纵深庞大、地面反光。'
    elif 9 <= n <= 14:
        mood = '十年前夜晚，卧室及门口低照度暖光，前景阴影包围，安静且局促。'
    elif 15 <= n <= 18:
        mood = '十年后夜晚，暖金卧室灯光照床面与衣料，静默中留有疏离感。'
    elif n == 19:
        mood = '十年后深夜，暖暗侧光勾面，冷峻而安静。'
    elif n == 20:
        mood = '十年后深夜，卧室通向走廊，门内暖光与门外暗部交接，离场冷清。'
    elif 21 <= n <= 24:
        mood = '十年后深夜，柔和暖金台灯与窗外深蓝夜色对照，转为安眠的静谧。'
    elif n == 25:
        mood = '暖调柔光开始泛白提亮，保持上一镜安眠空间。'
    elif n == 26:
        mood = '由卧室转向会客厅，柔白高调光覆盖，脸部与桌面叠化。'
    elif n == 27:
        mood = '会客厅桌面白闪收束，纯白过曝渐退，日间室内纸张逐渐显露。'
    elif n == 28:
        mood = '日间柔侧光照桌面与白纸，沉稳冷清，具有契约的冰冷感。'
    elif n == 30:
        mood = '夜晚车厢冷暗，手机弱光与窗外城市冷光掠过，后座侧拍。'
    elif n == 31:
        mood = '雨夜驾驶室，前挡雨滴、冷白暖黄车灯散景，仪表微光。'
    elif n == 32:
        mood = '夜晚车厢冷蓝暗调，微弱侧光照疲倦面部，压抑焦灼。'
    elif n == 39:
        mood = '傍晚会客厅光线快速压暗，淡出到下一场酒店。'
    elif n <= 38:
        mood = '傍晚会客厅暖壁灯与窗外深蓝暮光相对，桌面深沉，严肃压抑。'
    elif n in [40, 41]:
        mood = '深夜套房门外走廊冷灰蓝暗调，右侧门缝透一线暖光；门位与纵深沿用源镜。'
    elif n in [42, 43, 44, 46, 49, 50, 52, 53, 54, 57, 58, 59, 79, 80, 81, 82, 83, 84, 85, 86]:
        mood = '深夜套房暖金侧逆光，人物轮廓与表情清楚，门框、纱帘及床头位置承接源镜。'
    elif n == 45:
        mood = '深夜暖侧灯照洁白床品，细小褶皱形成柔和阴影，环境安静。'
    elif n == 47:
        mood = '床边地面暖暗，柔光照鞋与地毯纹理，床单垂角在侧。'
    elif n == 51:
        mood = '套房门口冷暖分区，门内暖黄、门外深蓝，人物入画与门框关系沿源镜。'
    elif 64 <= n <= 78:
        mood = '深夜暖色灯聚焦手、支票和白床单，冷淡的交易感逐渐变为突发冲突。'
    elif n in [87, 88, 89]:
        mood = '套房门口暖暗光交替，门扇与门框受光，离场后归于静谧。'
    elif n in [99, 100]:
        mood = '暖光照参考衬衫后领，衣料上的红色唇印醒目，保持源位置。'
    elif n == 116:
        mood = '床头暖光开始被浅白柔光覆盖，结尾定格转场起始。'
    elif n == 117:
        mood = '约六成白闪叠化，保持双人暖灯空间的微弱轮廓。'
    elif n == 118:
        mood = '白闪达峰值，约八成半高亮覆盖，接近全白。'
    elif n == 119:
        mood = '白闪迅速消退，床头暖黄与室内暖调重新出现。'
    elif n in [120, 121]:
        mood = '暖黄床灯，画面边缘轻微色散及柔光，延续悬念余韵。'
    else:
        mood = '深夜套房暖暗侧光，床灯与白床品柔和，保持源镜局部环境与视线关系。'
    return scenes + '。' + mood + ' 空间材质和家具取场景参考，机位与人物落点按本镜。'

def dialogue_slots(version):
    # Exact candidates; never automatically choose, splice, rewrite, translate, or force cross-scene lines.
    female = {
        (37, 38, 39): ['No. My job ends here.'],
        (50,): ["You really won't let me stay the night?"],
        (53, 54): ["Sorry. I didn't order room service."],
        (56,): ["She's not room service.", "She's my human pillow."],
        (58, 59): ["One woman isn't enough?", "You're moving straight on to the next one?"],
        (62, 63): ["I'm just sleeping with my little pillow. Problem?"],
        (71,): ["We're done for tonight. You can go."],
        (80, 81, 82): ['Keep it. I had a good time too. We both got what we wanted.'],
        (108,): [], (110,): [], (112,): [], (115, 116): [],
    }
    male = {
        (37, 38, 39): ['No. This ends here.'],
        (50,): ["You're really not letting me spend the night?"],
        (53, 54): ["Sorry, we didn't ask for turndown service."],
        (56,): ["Service? He's mine."],
        (58, 59): ["Wasn't I enough for you? You're already bringing in the next guy?"],
        (62, 63): ["What's wrong with sleeping with my pillow?"],
        (71,): ['Alright, you can go now.'],
        (80, 81, 82): ["Keep your damn money. I got what I wanted out of this, too. We're even. We're done."],
        (108,): ["What's wrong?"],
        (110,): ["There's a mark on your neck."],
        (112,): ["Jealous? Want me to wash his scent off first?"],
        (115, 116): ["Let's go somewhere else, then. We're staying at your place tonight, okay?"],
    }
    source = {
        (37, 38, 39): ['No.', 'This is where it ends.'],
        (50,): ["You really won't let me stay the night?"],
        (53, 54): ["Sorry, we don't need", 'housekeeping.'],
        (56,): ["Housekeeping? She's mine."],
        (58, 59): ["Having me isn't enough? You're moving on already?"],
        (62, 63): ["What's wrong with sleeping...", '...with my little pillow?'],
        (71,): ['All right, you can go.'],
        (80, 81, 82): ["I don't want your damn money.", 'I enjoyed it too.', "We both got what we wanted. That's all."],
        (108,): ["Hmm? What's wrong?"],
        (110,): ["There's lipstick on your shirt."],
        (112,): ['If it bothers you, should I change?'],
        (115, 116): ["Then let's sleep somewhere else. Your place tonight, okay?"],
    }
    who = {(37,38,39):'P',(50,):'L',(53,54):'L',(56,):'B',(58,59):'L',(62,63):'B',
           (71,):'B',(80,81,82):'L',(108,):'B',(110,):'P',(112,):'B',(115,116):'B'}
    candidates = female if version == '女版' else male
    slots = []
    for shot_nums, source_lines in source.items():
        duration = sum(Decimal(str(data['shots'][n-1]['timecode']['duration_seconds'])) for n in shot_nums)
        candidate = candidates[shot_nums]
        notes = []
        if shot_nums == (37,38,39):
            notes.append('38/39是母亲反应镜，源表把同句标台词/VO，不能指定母亲开口；拒绝者应由37确立，尾音承接。')
        if not candidate:
            notes.append('该版EP01英文未覆盖此后段对白，不从其他场景强套；画面仍保留源镜。')
        if version == '性转男版' and shot_nums in [(110,), (112,)]:
            notes.append('项目原句为脖子mark/洗掉气味，但源镜明确衣领唇印/换衣，存在视觉语义冲突，待根线程处理，不静默改台词。')
        if shot_nums in [(53,54),(80,81,82),(115,116)]:
            notes.append('固定源时长与英文长度可能冲突；尚无实测对白音频，不声称准确匹配，不加时或删词。')
        slots.append({
            'slot_id': f"EP01_{shot_nums[0]:03d}_{shot_nums[-1]:03d}", 'source_shots': list(shot_nums),
            'source_excel_rows': [n+3 for n in shot_nums], 'speaker_role': who[shot_nums],
            'speaker': role_map(version,shot_nums[0])[who[shot_nums]][0],
            'source_XLSX_english_verbatim': source_lines,
            'project_version_english_verbatim_candidates': candidate,
            'source_F_verbatim': {str(n):data['shots'][n-1]['source_fields_by_column']['F'] for n in shot_nums},
            'duration_seconds': float(duration), 'status':'awaiting_user_dialogue_source_policy',
            'selected_text':None, 'prompt_audio_inserted':False, 'notes':notes,
        })
    slots.append({'slot_id':'EP01_055_laugh','source_shots':[55],'speaker_role':'B',
                  'source_XLSX_english_verbatim':['Hmph','(Chuckles)'],
                  'project_version_english_verbatim_candidates':[], 'status':'nonverbal_laugh_visual_only',
                  'selected_text':None,'prompt_audio_inserted':False,
                  'notes':['轻笑/舞台说明不当作角色朗读词，源视觉表演保留。']})
    return slots

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def resolved_dialogue_events(version):
    female = [
        ('refusal',[37,38,39],1,'P',['No. My job ends here.'],{37:['No. My job ends here.']}),
        ('stay',[50],1,'L',["You really won't let me stay the night?"],{50:["You really won't let me stay the night?"]}),
        ('service',[53,54],1,'L',["Sorry. I didn't order room service."],{53:["Sorry. I didn't order room service."]}),
        ('ownership',[56,57],1,'B',["She's not room service.","She's my human pillow."],{56:["She's not room service.","She's my human pillow."]}),
        ('complaint',[58,59],1,'L',["One woman isn't enough?","You're moving straight on to the next one?"],{58:["One woman isn't enough?","You're moving straight on to the next one?"]}),
        ('pillow',[62,63],1,'B',["I'm just sleeping with my little pillow. Problem?"],{62:["I'm just sleeping with my little pillow. Problem?"]}),
        ('dismiss',[71,72],1,'B',["We're done for tonight. You can go."],{71:["We're done for tonight. You can go."]}),
        ('rejectmoney',[80,81,82],1,'L',['Keep it. I had a good time too. We both got what we wanted.'],{80:['Keep it.'],81:['I had a good time too.'],82:['We both got what we wanted.']}),
        ('wrong',[108],2,'B',["What's wrong?"],{108:["What's wrong?"]}),
        ('mark',[110,111],2,'P',["There's lipstick on your neck."],{110:["There's lipstick on your neck."]}),
        ('change',[112,113],2,'B',['If it bothers you, I can take a shower.'],{112:['If it bothers you, I can take a shower.']}),
        ('elsewhere',list(range(115,123)),2,'B',["Then let's sleep somewhere else.","How about your place tonight?"],{115:["Then let's sleep somewhere else.","How about your place tonight?"]}),
    ]
    male = [
        ('refusal',[37,38,39],1,'P',['No. This ends here.'],{37:['No. This ends here.']}),
        ('stay',[50],1,'L',["You're really not letting me spend the night?"],{50:["You're really not letting me spend the night?"]}),
        ('service',[53,54],1,'L',["Sorry, we didn't ask for turndown service."],{53:["Sorry, we didn't ask for turndown service."]}),
        ('ownership',[56,57],1,'B',["Service? He's mine."],{56:["Service? He's mine."]}),
        ('complaint',[58,59],1,'L',["Wasn't I enough for you? You're already bringing in the next guy?"],{58:["Wasn't I enough for you? You're already bringing in the next guy?"]}),
        ('pillow',[62,63],1,'B',["What's wrong with sleeping with my pillow?"],{62:["What's wrong with sleeping with my pillow?"]}),
        ('dismiss',[71,72],1,'B',['Alright, you can go now.'],{71:['Alright, you can go now.']}),
        ('rejectmoney',[80,81,82],1,'L',["Keep your damn money. I got what I wanted out of this, too. We're even. We're done."],{80:['Keep your damn money.'],81:["I got what I wanted out of this, too. We're even. We're done."]}),
        ('wrong',[108],1,'B',["What's wrong?"],{108:["What's wrong?"]}),
        ('mark',[110,111],1,'P',["There's a mark on your neck."],{110:["There's a mark on your neck."]}),
        ('change',[112,113],1,'B',["Jealous? Want me to wash his scent off first?"],{112:["Jealous? Want me to wash his scent off first?"]}),
        ('elsewhere',list(range(115,123)),1,'B',["Let's go somewhere else, then. We're staying at your place tonight, okay?"],{115:["Let's go somewhere else, then. We're staying at your place tonight, okay?"]}),
    ]
    result=[]
    project=HERE.parent.parent
    source_version='女版' if version=='女版' else '性转版'
    for event_id, support, ep, speaker, originals, parts in (female if version=='女版' else male):
        p=project/'配音制作_前3集/英文剧本'/source_version/f'{source_version}_第{ep:02d}集_纯英文全文.txt'
        raw=p.read_text(encoding='utf-8')
        quotes=re.findall(r'["“]([^"”]+)["”]',raw,re.S)
        assert all(x in quotes for x in originals),(version,event_id,originals)
        reconstruction=' '.join(t for shot in sorted(parts) for t in parts[shot])
        assert reconstruction==' '.join(originals),(version,event_id,reconstruction)
        dur=sum(Decimal(data['shots'][n-1]['timecode']['duration_seconds_exact']) for n in support)
        words=len(re.findall(r"\b[\w]+(?:['’][\w]+)*\b",' '.join(originals)))
        notes=[]
        if event_id=='mark':notes.append('项目原台词neck与源镜后衣领布料唇印位置有语义差异；不改台词、不改源镜，待用户核对。')
        if event_id=='change':notes.append('项目原台词shower/洗气味与源镜询问换衣语义不同；同场互动对应但不改原词或增添洗澡镜头。')
        if event_id=='refusal':notes.append('38/39为母亲反应镜，承接拒绝者37的声音，母亲不作说话口型。')
        if words/float(dur)>3:notes.append('按整个连续支持镜段计算超过3词/秒；仅为时长风险提示，未实测声音，不删词或加时。')
        result.append({
            'event_id':f'EP01_{event_id}','version':version,'speaker_role':speaker,
            'speaker':role_map(version,support[0])[speaker][0],
            'source_file':str(p),'source_sha256':sha(p),'source_episode':ep,
            'original_quoted_units_verbatim':originals,
            'source_quote_indices_1based':[quotes.index(x)+1 for x in originals],
            'source_shots':support,'parts':[{'source_shot':k,'texts_verbatim':v} for k,v in sorted(parts.items())],
            'continuation_only_source_shots':[n for n in support if n not in parts],
            'support_duration_seconds':float(dur),'english_word_count':words,
            'words_per_second_for_risk_only':round(words/float(dur),3),
            'exact_source_quote_match':True,'all_parts_reconstruct_original':True,
            'inserted_exactly_once':True,'status':'project_original_selected_verbatim','notes':notes,
        })
    return result

def build(version):
    target = HERE / version
    target.mkdir(exist_ok=True)
    shots = []
    slots = dialogue_slots(version)
    events=resolved_dialogue_events(version)
    prefix='大码女版' if version=='女版' else '性转版男版'
    for s in data['shots']:
        n = s['source_shot']
        r = rows[n]
        m = role_map(version,n)
        group_no, local_no = divmod(n-1,5)
        shot_id=f'01-{group_no+1:02d}-{local_no+1:02d}'
        full_shot_id=prefix+shot_id
        fields = {
            '时长': f"{s['timecode']['duration_seconds_exact']}秒（{full_shot_id}；原镜{n:02d}）",
            '环境氛围': environment(version,n),
            '景别': s['source_fields_by_column']['H'],
            '拍摄角度': s['source_fields_by_column']['J']+'；'+camera_adapt(s['source_fields_by_column']['I'],version,n),
            '摄像机运动': s['source_fields_by_column']['K'],
            '人物角色和运动': expand(r['E'],m,True),
            '人物表演': expand(r['F'],m),
            '画面内容': expand(r['G'],m),
        }
        # Production prompts contain only visible performance; workflow notes stay in JSON.
        fields['人物表演'] = fields['人物表演'].replace('；确切英文对白在独立槽位待统一回填','').replace('；确切英文见对白槽位','')
        for event in events:
            part=next((p for p in event['parts'] if p['source_shot']==n),None)
            if part:
                fields['人物表演']+=' '+event['speaker']+'英文原台词：'+' '.join('“'+t+'”' for t in part['texts_verbatim'])+'。'
                if n==80:
                    fields['人物表演']+=' 声音来自左前景情人，清晰受焦的老板只作听者反应。'
            elif n in event['continuation_only_source_shots']:
                first=event['source_shots'][0]
                fields['人物表演']+=f' 承接原镜{first:02d}已开始的同一段英文对白尾音，不重新说一遍；画中人物维持本镜反应。'
        indices = list(dict.fromkeys([m[c][1] for c in r['visible_roles'] if m[c][1] is not None]+scene_indices(version,n)))
        prop_indices=[]
        if n in [27,28,34,38]:prop_indices.append(71)
        if n == 30:prop_indices.append(78)
        if 71 in prop_indices:
            fields['画面内容'] += ' 文件形制锁定续约合同（@续约合同）。'
        if 78 in prop_indices:
            fields['人物角色和运动'] = fields['人物角色和运动'].replace('手机','手机（@手机）')
        indices += prop_indices
        requirements=[]
        if n in [4]: requirements.append('送行成年人仅手部，源表管家/送行者未确定，未擅自指定Vincent。')
        if n in [16,20]:requirements.append('本镜情人无已确认对应参考，不冒认主要情人或虚构绑定。')
        if n in [27,28]:requirements.append('合同手身份未确定，未指定Eliza/性转男主或Serafina。')
        if n in [40,41]:requirements.append('酒店参考图仅套房，不含该走廊的完整位置；门位构图按源截图。')
        shot = {
            'episode':1,'source_shot':n,'source_excel_row':s['source_excel_row'],
            'shot_id':shot_id,'full_shot_id':full_shot_id, 'group_number':group_no+1, 'group_local_shot':local_no+1,
            'source_TC':s['timecode']['raw'], 'duration_seconds':s['timecode']['duration_seconds'],
            'duration_seconds_exact':s['timecode']['duration_seconds_exact'],
            'screenshot':s['screenshot']['path'],'screenshot_sha256':s['screenshot']['sha256'],
            'source_fields_verbatim':s['source_fields_by_column'],
            'visual_review':s['visual_review'], 'fields':fields,
            'visible_roles':[{'role_code':c,'name':m[c][0],
                 'asset_name':assets[m[c][1]]['local_asset_name'] if m[c][1] is not None else None,
                 'reference_status':'provided_not_bound' if m[c][1] is not None else 'reference_pending'} for c in r['visible_roles']],
            'asset_names':[assets[i]['local_asset_name'] for i in dict.fromkeys(indices)],
            'asset_indices':list(dict.fromkeys(indices)),
            'dialogue_slot_ids':[x['slot_id'] for x in slots if n in x['source_shots']],
            'dialogue_event_ids':[x['event_id'] for x in events if n in x['source_shots']],
            'platform_binding_verified':False, 'unresolved_reference_notes':requirements,
        }
        shots.append(shot)
    groups=[]
    for i in range(0,122,5):
        sub=shots[i:i+5]
        gn=i//5+1
        # Cast may span childhood/adulthood and scenes; do not flatten across the source cut.
        cast={}
        for s in sub:
            for r in s['visible_roles']:
                cast[(r['name'],r['asset_name'])]=r
        cast_text=[]
        for (name,asset_name),r in cast.items():
            if asset_name is None:
                cast_text.append(name+'（参考图待指定）')
            else:
                idx=next(x for x in sub if any(q['asset_name']==asset_name for q in x['visible_roles']))
                ai=next(k for k,a in assets.items() if a['local_asset_name']==asset_name)
                cast_text.append(name+f"（@{asset_name}；{APPAREL.get(ai,'外形服装锁对应参考')}）")
        if not cast_text:cast_text=['无完整人物出场，局部手部仅按源镜显示，不臆定身份']
        scene_ids=list(dict.fromkeys(j for s in sub for j in scene_indices(version,s['source_shot'])))
        scene_text=' → '.join(f"{assets[j]['local_asset_name']}（@{assets[j]['local_asset_name']}）" for j in scene_ids)
        pending=[r['name'] for r in cast.values() if r['asset_name'] is None]
        lock='以下所有Shot出场的角色和场景统一锁定参考图。'
        if pending:
            lock='已提供参考图的角色和场景锁定对应参考图；'+ '、'.join(pending)+'的参考图待指定。'
        header='\n'.join([
            '出场角色：'+'；'.join(cast_text)+'。',
            '场景：'+scene_text+'。跨场切换按各Shot原顺序；参考卡仅取人物、服装、空间，不出现多视图拼贴或标签。',
            lock,
            '画幅：竖屏9:16。',
        ])
        blocks=[]
        for s in sub:
            blocks.append('Shot'+s['shot_id']+':\n'+'\n'.join(f'{k}：{v}' for k,v in s['fields'].items()))
        prompt=header+'\n\n'+'\n\n'.join(blocks)+'\n'
        assert len(prompt)<5000, (version,gn,len(prompt))
        out=target/f'01-{gn:02d}.txt'
        out.write_text(prompt,encoding='utf-8')
        group_indices=list(dict.fromkeys(j for s in sub for j in s['asset_indices']))
        groups.append({
            'version':version,'episode':1,'group_number':gn, 'group_id':f'01-{gn:02d}',
            'naming_status':'confirmed_episode_group_localshot_with_version_prefix',
            'card_name':sub[0]['full_shot_id'],'planned_platform_card_name':sub[0]['full_shot_id'],
            'source_shots':[s['source_shot'] for s in sub],
            'source_excel_rows':[s['source_excel_row'] for s in sub],
            'shot_ids':[s['shot_id'] for s in sub],
            'shot_count':len(sub),
            'total_duration':float(sum(Decimal(s['duration_seconds_exact']) for s in sub)),
            'total_duration_exact':str(sum(Decimal(s['duration_seconds_exact']) for s in sub)),
            'prompt':prompt,'prompt_character_count':len(prompt),
            'prompt_path':str(out),'prompt_sha256':sha(out),
            'asset_names':[assets[j]['local_asset_name'] for j in group_indices],
            'asset_sources':[{'name':assets[j]['local_asset_name'],'path':assets[j]['local_path'],
                             'sha256':assets[j]['sha256']} for j in group_indices],
            'platform_binding_verified':False,
            'reference_pending':pending,
            'dialogue_slot_ids':list(dict.fromkeys(q for s in sub for q in s['dialogue_slot_ids'])),
            'status':'text_prepared_reference_pending' if pending else 'text_prepared_not_bound_or_submitted',
            'shots':sub,
        })
    result = {
        'schema_version':'EP01-v3-local-project-dialogue-2.0', 'version':version,'episode':1,
        'status':'text_prepared_not_submitted_reference_resolution_pending',
        'authority':'Source XLSX + 122 matching stills; assigned Feishu identities and costumes replace only those visual identity details.',
        'source_shots_path':str(SOURCE),'source_shots_sha256':sha(SOURCE),
        'source_workbook':data['source_workbook'],
        'grouping':{'shots_per_full_group':5,'group_count':25,'last_group_shot_count':2,
                    'shot_count':122,'duration_seconds':142.2,'naming_provisional':False,'version_prefix':prefix},
        'verification_limits':[
            '122 supplied single stills individually reviewed; not a verification of entire clip motion or actual actor performance.',
            'Textual @ names represent provided local cards, not verified platform bindings.',
            'Original fixed durations preserved, including 57 sub-one-second shots. Dialogue timing not audio-measured.',
            'No narration English inserted into mouth speech. User selected project English originals; exact quoted units are inserted once, reaction shots only continue the sound.',
        ],
        'auxiliary_script_differences':[
            'Female source108–122 dialogue maps semantically to project EP02 opening; source shot order remains EP01, with no inserted scene.',
            'Project scripts do not control source montage, car chase, actions, or shot order.',
            'Both versions source99/100 keeps lipstick on back collar cloth; male project hickey-on-neck line is a separately flagged semantic conflict.',
            'Source69–70 contains two checks; later90–92 shows one held; no global simplification.',
        ],
        'dialogue_policy':'User selected corresponding project English original dialogue verbatim, including same-scene material across project episode boundary.',
        'dialogue_events':events,'dialogue_slots':events,
        'source_dialogue_slots_before_policy_resolution':slots,'groups':groups,
    }
    project_source_version='女版' if version=='女版' else '性转版'
    ep1file=HERE.parent.parent/'配音制作_前3集/英文剧本'/project_source_version/f'{project_source_version}_第01集_纯英文全文.txt'
    project_quotes=re.findall(r'["“]([^"”]+)["”]',ep1file.read_text(encoding='utf-8'),re.S)
    used=[text for ev in events if ev['source_episode']==1 for text in ev['original_quoted_units_verbatim']]
    result['project_EP01_dialogue_coverage']={
        'source_file':str(ep1file),'source_sha256':sha(ep1file),'original_quote_count':len(project_quotes),
        'source_corresponding_quote_count':len(used),
        'not_forced_into_source_shots':[
            {'text_verbatim':q,'source_quote_index_1based':i+1,
             'reason':'源表无对应说话镜段，不为覆盖旧项目原稿增镜、移入别处或改动源镜表演。'}
            for i,q in enumerate(project_quotes) if q not in used],
    }
    out=target/'groups.json'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result

def main():
    results={v:build(v) for v in VERSIONS}
    qc={'schema_version':'EP01-v3-project-dialogue-QC-2.0','source_shots_path':str(SOURCE),
        'source_shots_sha256':sha(SOURCE),'browser_or_platform_actions':False,'versions':{}}
    for version,r in results.items():
        flattened=[s for g in r['groups'] for s in g['shots']]
        expected=list(range(1,123))
        assert [s['source_shot'] for s in flattened]==expected
        assert all(s['duration_seconds_exact']==data['shots'][s['source_shot']-1]['timecode']['duration_seconds_exact'] for s in flattened)
        assert all(list(s['fields'])==['时长','环境氛围','景别','拍摄角度','摄像机运动','人物角色和运动','人物表演','画面内容'] for s in flattened)
        assert all(s['fields']['景别']==data['shots'][s['source_shot']-1]['source_fields_by_column']['H'] and
                   s['fields']['摄像机运动']==data['shots'][s['source_shot']-1]['source_fields_by_column']['K'] for s in flattened)
        assert all('Dante' not in g['prompt'] and 'DeLuca' not in g['prompt'] for g in r['groups'])
        assert all('瘦身' not in a for g in r['groups'] for a in g['asset_names'])
        assert not any(re.search(r'旁白|\bVO\b',g['prompt']) for g in r['groups'])
        qc['versions'][version]={
            'groups':25,'source_shots':122,'last_group_shots':2,'duration_seconds':142.2,
            'exact_source_order_coverage':True,'all_durations_preserved':True,
            'all_8_fields_ordered':True,'source_shot_size_and_camera_motion_preserved':True,
            'all_txt_match_JSON':all(Path(g['prompt_path']).read_text(encoding='utf-8')==g['prompt'] for g in r['groups']),
            'max_prompt_chars':max(g['prompt_character_count'] for g in r['groups']),
            'groups_ge_5000_chars':[], 'platform_bindings_verified':0,
            'reference_pending_source_shots':[s['source_shot'] for s in flattened if any(x['asset_name'] is None for x in s['visible_roles'])],
            'dialogue_status':'project_original_verbatim_inserted_once',
            'dialogue_events':len(r['dialogue_events']),
            'all_dialogue_parts_reconstruct_original':all(x['all_parts_reconstruct_original'] for x in r['dialogue_events']),
            'all_dialogue_exact_source_quote_match':all(x['exact_source_quote_match'] for x in r['dialogue_events']),
            'groups_json_path':str(HERE/version/'groups.json'),
            'groups_json_sha256':sha(HERE/version/'groups.json'),
        }
    (HERE/'prompt_preparation_qc.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(qc,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
