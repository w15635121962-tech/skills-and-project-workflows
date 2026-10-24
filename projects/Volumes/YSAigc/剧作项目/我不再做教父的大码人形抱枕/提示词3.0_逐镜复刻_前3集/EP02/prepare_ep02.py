"""Local text preparation only. Never connects to a browser or Resolve."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
SOURCE = OUT / 'source_shots.json'
data = json.loads(SOURCE.read_text())
assets = json.loads((ROOT / '平台工作/飞书资产下载清单.json').read_text())['assets']
assets_by_name = {a['local_asset_name']: a for a in assets}

# Each row was checked against its contact-sheet tile. Movement remains the XLS instruction;
# a single screenshot cannot prove the full camera move or action completion.
VISUAL = '''
白枕上仰卧面部大特写，视线朝画外右上，暖暗侧光。
白枕头肩俯拍，双眼向左下方垂落，浅色衣领可见。
右侧枕卧正侧脸，左后方暖灯与窗帘虚化。
回到头肩俯拍，仰卧视线重新抬向右上。
面部较紧特写，点头阶段的下巴轻收，曝光开始暗。
同面部暗过渡帧，五官与眼部高光仍隐约可见。
极暗白门框空镜，右侧圆形深色把手，门底细光。
白门正面平视，黑圆把手在右，门扇初开。
同门机位，门缝暖光加宽投在木地板上。
黑袍人物出白门，转背身朝卧室小床，源帧可见房间纵深。
腰下腿脚与床沿局部，人物由左靠床，源人物赤足。
斜构图床面，黑衣人物后仰躺倒，枕头和玩偶在床头。
俯拍黑丝衣领与上胸局部，粉枕为背景。
与13同胸口局部连续帧，衣料和纹身位置一致。
胸口局部压暗的过渡帧，无新人物。
房间全景由暗渐亮，左侧睡衣人物床边站立，右侧黑衣人物床上伸手。
同全景床边拉人上床，睡衣人物在左、黑衣人物在右。
垂直俯拍双人面对面侧卧，睡衣人物在左、黑衣人物在右。
环腰背交叠手臂近特写，黑衣人物纹身手可见。
侧卧双人近景，睡衣人物左下、黑衣人物右上，额头相贴。
睡衣人物面部近景，黑衣人物下颌在右前景，手蜷在胸前。
卧室全景，小床中央被褥盖住两人，只露头部；左有窗。
俯拍倾斜手臂局部，被子边缘和睡衣肩背入画，脸不在主体内。
双人闭眼贴额近景，与20的左右关系一致。
黑衣人物闭眼侧脸大特写，另一人发顶在左下前景。
过睡衣人物肩拍黑衣人物，后者右上近景贴额发问。
睡衣人物面部大特写，睫毛眼部及唇部困倦反应。
睡衣人物左侧近景答话，右侧是黑衣人物鼻尖和下颌。
黑衣人物右上清醒侧脸，视线落向左下的头发与颈部。
黑衣人物眼鼻极近特写，前景虚化，仍维持右侧向左下关系。
左侧睡衣领口和颈部，右侧鼻尖进入并靠近颈侧。
黑衣人物埋颈侧脸特写，嘴角可见微笑；单张不能证明景别跳切过程。
黑衣人物右上贴颈低语近景，另一人头发和肩在左下。
颈侧、耳垂与睡衣领口微距，颈部绷起。
睡衣人物面部大特写，眼睛睁大、唇启，头部准备抬起。
左下嘴唇擦到右上黑衣人物下巴底部，非嘴对嘴亲吻。
同嘴唇与下巴微距，嘴唇稍退，双方停住。
双人正侧面近景，睡衣人物左、黑衣人物右，鼻尖相对，前者手在对方胸前。
同侧面对视的短连续帧，睡衣人物眼神躲闪准备后撤。
睡衣人物向画面左侧抽身的模糊运动阶段。
睡衣人物半坐在左床头，垂眸向右，肩胸紧张。
下颌、颈部和衣领局部特写，人物呼吸绷紧。
睡衣人物左侧半坐，黑衣人物右侧伸左臂揽腰背。
双人中近景回抱，黑衣人物左掌扣左肩臂、右手扶脑后。
过左下睡衣肩拍右上黑衣人物，后者低头凝视。
黑衣人物脸部大特写，另一人鼻尖和侧脸边缘位于左下。
黑衣人物左手扣住睡衣人物左肩，大拇指和手指轻捏。
黑衣人物嘴唇、下颌、衣领和上胸局部大特写，左下前景虚肩。
与45同过肩右上主体机位，黑衣人物嘴角微扬低头说话。
同过肩机位开始白色柔光，人物姿态延续49。
白闪峰值，人物只余高调轮廓，机位未变。
白闪回落、面部边缘轻微红蓝色散。
白雾更淡、边缘仍有色差，双人仍对视。
恢复暖色对比度，少量边缘色散趋退。
同过肩片尾定格，左下睡衣肩脸、右上黑衣人物。
同过肩定格连续帧，无新增动作。
同过肩末帧，双方相拥对视，片尾悬念定格。
'''.strip().splitlines()
assert len(VISUAL) == 57

# P = pillow protagonist; B = mafia boss. No voice-over is emitted as dialogue.
# The identity and wardrobe come from the supplied Feishu assets, not the reference actors.
SPECS = {
1: ('{P}仰躺白枕中央，脸朝上微偏左，双眼看向画外右上方的{B}；肩背保持陷在枕中。', '【{P}】双眼微睁大，微张的嘴唇轻合，目光短暂停住，把突然听见去自己公寓的要求表现为错愕。', '白枕托住脸部，{p_hair}沿枕面自然散开；镜尾仍看右上，不让画外的{B}突然入镜。'),
2: ('{P}保持仰卧，头肩居中偏下，视线由右上慢慢垂向左下；没有坐起。', '【{P}】睫毛轻颤，唇角逐渐放松，先垂眼再停顿；呼吸让{p_day_detail}轻微起伏。', '以白床枕衬出头肩，{p_day_detail}在画面下缘；右上至左下的视线变化是视觉重心，承接上一镜思索。'),
3: ('{P}头肩靠在画面右侧白枕，呈朝左上方的正侧脸；身体维持卧姿。', '【{P}】半垂的眼帘缓缓合上，嘴角和肩颈放松，呼吸平稳，呈现对长期相伴的习惯。', '右三分侧脸与白枕在近处，左后景保留酒店暖灯、窗帘层次；轻微左摇落在闭眼的侧脸。'),
4: ('{P}回到02的仰卧头肩机位，眼睛由低垂缓慢抬起，重新望向右上方画外{B}。', '【{P}】先轻颤眼睫，再抬眼停住，眉间的疑惑松开，以安静目光表达接纳，不做口播。', '白枕和{p_day_detail}保持前镜状态，头部不换枕位；视线终点与01的右上画外位置相同。'),
5: ('{P}仰卧面部居中，继续看右上；下巴只轻收一次，完成小幅点头。', '【{P}】双唇轻抿，点头后立刻安静，眼神柔和；不追加起身或开口动作。', '缓推贴近点头后的脸，暖光开始变暗，为下一镜暗切留落点。'),
6: ('{P}维持05点头后的仰卧姿势，目光仍在右上，身体不再新增动作。', '【{P}】保留安静凝视，面部表情不突变；这是点头后的0.1秒过渡，不再点第二次头。', '同一面部构图迅速压暗，五官和眼中高光最后消退，接下一镜的暗门空镜。'),
7: ('无人入画；公寓内门处于关闭状态，只见门扇与地面。', '空镜，无人物表演；暗场中先辨出门底细窄光线，不凭空增加开门的人。', '黑场渐显，按{entrance}资产的木色门扇与金属把手，保留源门框位置及门底暖光；门的位置保持到09。'),
8: ('人物留在门后画外；门把转动，木色门向内开启一道窄缝。', '仅用门把转动与门扇的平稳运动表现{B}换好衣服准备走出，尚不露人脸或手。', '平视木色门，门扇材质和金属把手依{entrance}资产，暗走道前景与门内暖光形成层次；光缝在地板上拉长，接09同机位。'),
9: ('木色门沿08的方向继续向内开启，门缝扩大；{B}仍未完整进入画面。', '无可见人物表演；开门运动连续，不能反向关门或换到另一扇门。', '扩大后的垂直暖光缝、金属门把手和地面反光为主体；保留门框位置，让10的人物从此门走出。'),
10: ('{B}穿{b_sleep_detail}从门框中央正面走出，向镜头左侧经过，再转背身直走卧室小床；{P}不抢入前景。', '【{B}】先略扫卧室，再以沉稳熟悉的步子直奔床边，肩背松弛，毫不客套；不在本镜提前完成躺床。', '起幅门框中见{B}，左摇跟住经过的身体，随后跟背影前推进入{room_detail}，末尾落在床边方向，空间关系接11。'),
11: ('仅拍{B}腰部以下，赤脚从画面左侧走到床沿，转身屈膝坐下，并开始抬腿上床。', '【{B}】赤足脚步自然、转身不迟疑；重心从脚移到床垫，动作延续10，脸不进入局部镜头。', '{b_lower_detail}与床边软毯、{bed}形成前中后层；低机位保留赤足接触地面和床沿下陷，接12后仰。'),
12: ('{B}接11坐姿向后躺倒，头落左侧枕头，双腿向右前方伸展，手臂自然舒开。', '【{B}】后背落床时枕垫下陷，神态放松，视线看床边画外{P}，保持等待的姿态。', '由床尾侧前方看斜躺的{B}，带出资产卧室床头枕、玩偶与照片墙；微幅左移跟住落枕，不加入新人物动作。'),
13: ('{B}仰卧不动，画面只取睡衣领口、锁骨与上胸可见部分，身体随一次深呼吸缓慢起伏。', '【{B}】肩胸放松，丝质衣料随呼吸抬落；保持资产衣领开合程度，纹身只展示参考图已有且衣料未遮住的部分。', '对角线俯拍{b_sleep_detail}的领口与衣料高光，背景是{bed}枕面；保持身体局部构图，长相体态与衣服锁定资产。'),
14: ('{B}维持13的仰卧位置和衣领状态，胸口延续轻微呼吸。', '【{B}】只有连续呼吸，没有第二个明显动作，0.1秒保留原镜尾帧节奏。', '同一领口和上胸局部，保持对角线及枕面位置，亮度开始转向下一暗切。'),
15: ('{B}仰卧局部不变，无人新进入画面。', '转场帧，呼吸姿态保持；不新增开衣、抬手或坐起。', '13的胸口衣料构图渐暗，衣料高光与已有纹身轮廓隐去，用0.1秒衔接16的全景渐显。'),
16: ('{P}穿{p_sleep_detail}与拖鞋站在画面左侧床边；{B}穿{b_sleep_detail}仰卧右侧，右手伸向{P}手腕并握住。', '【{B}】手臂已伸出，准备发力；【{P}】重心仍在床边双脚，身体开始朝床内倾，0.2秒不重复完成整段拉人。', '全景从暗渐亮，先交代左站右躺、右手与手腕连接点，再由17完成拉拽；床铺和两人衣服连续。'),
17: ('{B}保持右侧卧床位置，右手握{P}手腕向怀中一拉；{P}从左侧床边失衡扑向床面，{B}顺势张臂接住。', '【{P}】先重心前倾，再本能收手护在胸前，眼睛短暂睁大；【{B}】目光跟住{P}，动作熟练，接住后不继续甩动。', '固定全景完整容纳床边、手腕连接与扑入怀中的动作路径；末尾{P}落到床上左侧，{B}仍在右侧，接18俯拍。'),
18: ('{P}在左侧右侧卧、面向右边的{B}，手蜷胸前、右腿自然弯曲；{B}在右侧左侧卧面向{P}，双臂一上一下环抱腰背。', '【{P}】闭眼安静依偎；【{B}】低头把鼻梁贴近{P}额头发丝，眼睛闭合，环抱的手指轻收，肩背松下来。', '垂直俯拍完整交代两人面对面侧卧与腿部相接，{P}左、{B}右的位置不换；{bed}围住两人的身体轮廓。'),
19: ('只取{P}侧卧腰背和{B}交叠双臂；{B}右前臂从下环腰，左手从上覆在右前臂与{P}背上。', '【{B}】左手五指轻收，把{P}向怀中按紧一点；手势连贯，不把左右手交换。', '对角线手臂与{p_sleep_detail}腰背衣料为主体，已有纹身依资产呈现；避开脸，用接触细节承接18的拥抱。'),
20: ('{P}侧卧在左下，{B}侧卧在右上，双臂保持环背，鼻梁贴近{P}额头，双方仍闭眼。', '【{B}】背后手指稍收，把{P}上身贴近，呼吸稳定；【{P}】放松肩颈、闭眼依偎，不翻成俯卧。', '平视侧卧双人近景，左下和右上形成依偎的中心构图，注意力落在额头与鼻尖近距接触；沿用18建立的拥抱关系。'),
21: ('{P}脸在中央偏左，左手蜷胸前抓着{B}黑色睡衣衣襟；{B}下颌与鼻尖留在右侧近前景。', '【{P}】原本闭合的眼睛缓慢睁开，视线稍向上看{B}睡颜，眼睫轻颤；其余身体仍留在环抱中。', '过右侧下颌看{P}面部，抓衣襟的手在下缘可见；用清醒的目光对照右前景的闭目静止，不让手自行换到别处。'),
22: ('两人仍在床中央相贴侧卧，被子已盖到肩边，只露相邻头部与发顶，人物位置沿用前镜。', '被面随{B}环抱手臂轻收小幅起伏，除此保持安静；不插入重新铺床的动作。', '固定全景交代{room_detail}，左侧窗、床铺和床头生活摆件保持资产布局；{bed}中央的双人鼓起轮廓成为视觉重心。'),
23: ('局部俯拍被外交叠的双臂，{B}仍环住{P}肩背；左手轻搭自己右前臂及{P}肩头。', '【{B}】左手轻拍抚一次并收紧拥抱，{P}肩背顺着手掌略贴近；不把局部镜头的画面左侧误作人物换边。', '倾斜对角线截取被褥边缘、黑色袖口和{p_sleep_detail}肩背，面部不作为主体，连到24的同一次拥抱。'),
24: ('{P}继续左下侧卧，{B}右上侧卧环抱，额头和鼻尖贴近{P}额发。', '【{B}】闭眼抱住片刻，背后的手指微动，鼻翼轻翕，眉间出现一点好奇；【{P}】仍安静闭眼。', '回到20的平视双人近景，保持衣领和被边高度；用{B}鼻翼的小变化引出25嗅闻。'),
25: ('{B}闭眼侧脸在右上，脸埋近左下{P}额发，嘴唇微启准备发问。', '【{B}】先深吸一口气，鼻翼轻动，眉头舒展；动作轻而慢，停在准备说话的状态。', '右三分的脸部大特写，{P}头顶和肩作左下前景；近距离暖光落在眼鼻，接26同轴发问。'),
26: ('{B}位于右上，贴着左下{P}额头，维持环抱姿态；说话后才缓缓睁眼向下看。', '【{B}】从闭眼放松到睁眼探究，嘴唇自然开合提出床铺气味的疑问。', '过{P}肩拍{B}侧脸，右三分机位保持两人距离，眼睛睁开的终点落向怀中{P}。'),
27: ('{P}侧卧脸占画面中心，仍靠{B}胸前，身体不抬起。', '【{P}】听见问题后睫毛轻动，缓缓睁眼，嘴唇微动，呈现半睡半醒的回应。', '固定面部大特写保留困倦反应，延续26被唤醒的时刻；没有旁白口型。'),
28: ('{P}侧卧在左，左手轻搭胸前，{B}鼻尖与下颌位于右侧极近处；回答后{P}又合眼。', '【{P}】半垂眼帘，嘴唇轻启自然回答，尾句后闭眼，肩颈继续放松。', '过右侧下颌看左侧脸部，近景同时保留胸前手的位置；以答完闭眼的落点接29中{B}反而清醒的反应。'),
29: ('{B}右上睁眼低看左下{P}发顶和颈部，头部缓缓往下埋近，拥抱未松。', '【{B}】眼神由困倦变清明，视线先落发旋，再下移到颈侧，鼻翼轻动。', '右三分过肩近景强调清醒的眼睛与向下的视线，左下头发肩部作连续前景，为30嗅闻路线定向。'),
30: ('{B}眼鼻位于右侧至中央，低头贴近左下{P}发丝与领口之间，头部缓缓向下嗅探。', '【{B}】双眼清醒专注，鼻翼轻翕，一边移动头部一边吸气，视线不离开近处的颈侧方向。', '固定机位的极近眼鼻构图，前景从虚到实以显出靠近路线；不把源表由虚转实描述改成摄影机平移。'),
31: ('{P}领口和颈部占左侧至中央，{B}鼻尖与前额从右侧进入，轻轻擦到{P}颈侧。', '【{B}】沿着前镜方向慢慢探近，鼻尖落在颈侧；【{P}】颈部产生很小的绷紧反应，身体仍侧卧。', '平视微距保持左颈右鼻的对峙关系，{p_collar_detail}标明接触位置；只拍鼻尖擦颈，不改成口唇亲吻。'),
32: ('{B}面部在右上，鼻尖仍埋近左下{P}颈侧，吸气后微眯眼，嘴角渐起。', '【{B}】先专注嗅闻，再短暂停顿，随后出现发现气味来源的满足微笑；手臂持续环抱。', '源内从极近侧脸跳切至近景，保持固定机位轴线与右三分关系；同一源镜号内交代景别变化，不另造镜号或连续拉远。'),
33: ('{B}保持右上贴颈的侧卧姿势，嘴唇在左下{P}发间颈边说话，环肩的手轻摩挲。', '【{B}】眼睛略眯，笑意先起，随后低头说话，呼吸近贴颈侧；【{P}】仍在环抱内。', '右三分近景集中在{B}侧脸与{P}颈肩，维持32的贴颈落点；不新增另一段吻颈动作。'),
34: ('{P}右侧颈部、耳垂与领口占满局部画面，因吸气微微绷紧，头部开始抬起一点。', '【{P}】一次轻微倒吸气使颈线短暂收紧，肩颈随之小抬，表现猝然紧张；不夸张扭动。', '微距对角线突出耳垂至{p_collar_detail}之间的细小反应，光线仍沿前镜侧光，接35抬头。'),
35: ('{P}侧卧面部居中，眼睛睁大、嘴唇微张，头部缓缓向上抬准备开口。', '【{P}】先呼吸变快，目光慌乱一停，再抬下巴；嘴唇欲言却未说出新句，脸颊泛起紧张红晕。', '固定面部大特写用4.4秒呈现呼吸、停顿、抬头的次序；头部上抬方向必须接36左下嘴唇碰右上下巴。'),
36: ('{P}嘴唇鼻尖在左下，{B}下巴与颈部在右上；{P}抬头时嘴唇向上轻擦{B}下巴底部。', '【{P}】唇瓣刚触下巴就停顿；【{B}】下颌突然静住，保持意外擦碰的瞬间，不主动转成嘴对嘴接吻。', '侧面微距沿对角线看清唇与下巴的接触点，{b_chin_detail}依身份资产；领口可见部分连续，接37微退。'),
37: ('延续36的左下嘴唇、右上下巴；{P}意识到擦碰后只向后缩开很小距离。', '【{P}】嘴唇一顿后微退，呼吸短暂停住；【{B}】下颌保持原位，双方同时僵住。', '相同侧面微距呈现从接触到分开毫厘，不换人物左右或追加第二次擦碰。'),
38: ('{P}在左正侧面朝右，右手蜷在{B}胸前；{B}在右正侧面朝左，两人鼻尖相对，身体仍在拥抱中。', '【{P}】眼睛睁大，手指微蜷，嘴唇微张却说不出话；【{B}】目光定在{P}眼睛上，嘴唇也微启，双方屏住呼吸。', '双人对称近景清楚保留左{P}右{B}的轴线，胸前蜷手仍在画面下部；静止对视是本镜任务。'),
39: ('保持38左右和姿势，{P}眼神一闪，肩背出现准备抽身的小变化，尚未坐起。', '【{P}】先避开直视，收紧胸前手指；【{B}】仍看{P}，0.2秒只作退开的起点。', '双人正侧近景保留鼻尖之间距离，末尾以{P}微移接40，不能在此跳完后退。'),
40: ('{P}从画面中央偏左急促撑起上身，向左侧床头后退，离开{B}胸前；{B}留在原床位。', '【{P}】目光低垂，肩背紧绷，动作短促而慌乱；不额外站到地面。', '中近景左摇起幅追{P}向左抽身，允许原镜短暂运动模糊，0.2秒保留起身动作阶段，接41落幅。'),
41: ('{P}半坐在左床头，侧脸朝右但垂眸避开{B}，上身已与怀抱拉开距离。', '【{P}】双唇紧抿，视线下落，胸口呼吸明显，肩背短暂僵住，表现担心心跳被听见。', '左摇落幅在偏左的半坐侧脸，保持前镜后退方向，床头与{p_sleep_detail}肩部可见，接42呼吸局部。'),
42: ('只拍{P}下颌、脖颈与衣领局部，人物仍半坐，不换回枕卧位置。', '【{P}】轻吞咽一次，颈部随急促呼吸上下微动，唇线收紧，紧张以身体细节显出。', '固定中心微距取颈侧与{p_collar_detail}，保留布料随呼吸起伏的细节；不让锁骨或衣领造型变成源演员服装。'),
43: ('{P}半坐在左侧，{B}半卧右侧，{B}伸出左臂揽到{P}腰背并开始拉回。', '【{B}】不迟疑地伸臂，视线跟住{P}；【{P}】被拉时肩部一惊，身体由左向右前倾。', '固定双人中近景交代左侧退开的{P}和右侧伸臂的{B}，连接点是腰背；动作末尾接44怀中回抱。'),
44: ('{P}由左侧前倾回到{B}怀中；{B}左掌扣{P}左肩大臂，右手扶{P}后脑与颈侧，拉回到胸前。', '【{B}】低头看{P}，手掌在回抱落点稳住而非继续甩拉；【{P}】惊愕停住，抬脸与{B}近距相对。', '中心中近景看清左掌扣肩、右手护脑两个位置，双方鼻尖重新靠近；保持衣服和接触点到45。'),
45: ('{B}脸在右上，低头看左下{P}；{P}肩与略抬的侧脸作虚化前景，仍被抱在胸前。', '【{B}】眉梢微压、目光仔细打量{P}慌乱的脸，唇线轻抿；【{P}】仰看而不再退。', '过{P}左下肩头看右上{B}，微仰视强调审视关系；睡衣领口与已有纹身依各自资产，视线接46发问。'),
46: ('{B}低头面部占大特写，{P}鼻尖与侧脸边缘留在左下，两人距离不变。', '【{B}】先挑眉审视，再开口带一点疑问和调侃；眼睛始终落在{P}脸上。', '由45切紧脸部固定机位，保留左下前景和微仰角，不改为另一侧反打。'),
47: ('{P}左肩在画面中央，{B}左手仍扣着该肩，拇指与其余手指轻收捏一下。', '【{B}】手掌力道从拉回的稳固转为安抚式轻捏，随后停住；不把左手换到右肩。', '微俯肩头特写，看清黑色袖口、手与{p_sleep_detail}肩部衣料受压的细节；纹身只保留资产已有图案。'),
48: ('{B}嘴唇、下巴与领口上胸局部居中，{P}肩头仍在左下虚前景，双方继续贴近。', '【{B}】嘴角轻轻扬起，嘴唇开合说出安抚词，表面松弛，手臂仍维持回抱。', '对角线大特写集中嘴唇和{b_sleep_detail}领口，以{b_chin_detail}区别人物；不额外暴露被衣料遮住的身体。'),
49: ('回45机位，{B}右上低头看左下{P}，{P}保持在怀中仰视；{B}目光从脸扫过身体后回到眼睛。', '【{B}】嘴角似笑非笑，慢慢说出调侃；环抱没有松开，以言语和仍紧抱的姿态形成反差；【{P}】静静抬眼听。', '过肩近景保留左下{P}肩脸和右上{B}主体，衣服与体型依大码/教父或教母资产；不为台词中的体型词改瘦人物。'),
50: ('两人保持49的相拥对视，{B}说完后嘴角轻勾，等待{P}反应，位置不变。', '【{B}】保留上一句的口型收尾，不重复完整台词；【{P}】仍仰看，0.1秒不新增情绪动作。', '同过肩构图叠起暖白柔光，白光从轻雾开始，接51峰值；不是另一个场景。'),
51: ('维持50的右上{B}、左下{P}对视定格，拥抱接触点不变。', '两人保持停住的表情与身体，闪白过程不另开口、不另做动作。', '柔白闪光覆盖全幅达到峰值，人物面部与衣领只余半透明高调轮廓，沿用同一过肩机位。'),
52: ('两人延续定格，{B}低头、{P}抬脸，人物左右与拥抱保持。', '【{B}】嘴角残留轻抿弧度；【{P}】眼神仍在对方脸上，0.1秒无新动作。', '白闪开始回落，原过肩人物轮廓恢复；发丝与面部边缘出现轻微红蓝色差，不改变真实人物位置。'),
53: ('两人近距离四目相对，保持52的同一身体姿态。', '双方把上一句后的反应停在眼神内，不新增笑、哭或抽身动作。', '白光进一步消退，面部和领口重新清晰，画缘保留细微色散与震动余韵；固定机位不跟人物移动。'),
54: ('{B}右上低头凝视，{P}左下仰看，延续同一对角线视线。', '【{B}】嘴唇微抿，眼神留住{P}；【{P}】保持短暂停顿，身体依旧被抱住。', '暖色对比度恢复饱满，白闪基本退出、边缘余效收敛，回到原近景的脸部与肩部关系。'),
55: ('两人维持极近距离相拥，{P}左下肩脸、{B}右上主体，不挪动。', '片尾定格：{B}嘴角微勾而目光不移，{P}仰视停住；不增加第二句对白。', '同过肩近景定格，衣服、光线和背景与54相同，本镜0.2秒独立保留原表节奏。'),
56: ('完整延续55的相拥与对视位置，左下{P}、右上{B}。', '保持片尾定格，无新增动作或表情变化，0.1秒仍为独立源镜。', '同过肩近景连续定格帧，保持对角线眼神、肩部遮挡及领口位置。'),
57: ('{B}仍把{P}抱在胸前，低头凝视；{P}仍在左下仰脸，身体不退开。', '片尾末帧延续嘴角微勾与双方停住的眼神，怀抱依然收紧，动作不重新开始。', '同过肩构图结束本集，左下{P}肩脸和右上{B}的对视定格延续至74.9秒，保留源表最后0.2秒，不另补转场。'),
}
assert set(SPECS) == set(range(1, 58))

VERSIONS = {
 '女版': dict(P='Eliza', B='Matteo Bellandi', p_day='大码女主_Eliza_日常', p_sleep='大码女主_Eliza_睡衣', b_sleep='Matteo_成年_睡衣', room='Eliza旧卧室', entrance='客厅与入口', p_hair='棕色微卷长发', p_day_detail='米白针织开衫与浅色碎花连衣裙领口', p_sleep_detail='米白宽松短袖睡裙', p_collar_detail='米白短袖睡裙的圆形蕾丝边领口', b_sleep_detail='白滚边黑色丝质两件睡衣', b_lower_detail='黑色丝质睡裤裤脚与脚部', b_chin_detail='Matteo资产中的下巴与浅胡茬', bed='粉米白床铺', room_detail='粉米白暖调旧卧室的窄床、窗、照片墙与木质梳妆桌'),
 '性转男版': dict(P='Oliver', B='Vittoria Blackwood', p_day='大码男主_性转_日常', p_sleep='大码男主_性转_睡衣', b_sleep='Vittoria_成年_黑色睡衣', room='性转卧室', entrance='性转客厅入户', p_hair='棕色短卷发', p_day_detail='白色衬衫衣领', p_sleep_detail='藏蓝白滚边长袖长裤睡衣', p_collar_detail='藏蓝睡衣的白滚边翻领', b_sleep_detail='黑色蕾丝边系带丝质睡袍', b_lower_detail='黑色长睡袍下摆与脚部', b_chin_detail='Vittoria资产中的光洁下巴与颈部', bed='蓝灰床铺', room_detail='蓝灰卧室的窄床、窗、照片墙与木质书桌'),
}

SLOTS = {
 26: dict(speaker='B', kind='dialogue', xls='Elena, why does your bed smell so good?', female='Why does your bed smell so good?', male='Oliver, why does your bed smell so good?'),
 27: dict(speaker='P', kind='nonverbal_vocalization', xls='Hmm...', female=None, male=None),
 28: dict(speaker='P', kind='dialogue', xls='Everything was just freshly washed.', female='I just washed the bedding today.', male="Everything's fresh out of the wash."),
 33: dict(speaker='B', kind='dialogue', xls='So this is where the best smell is.', female='So this is where you smell the best.', male='Turns out the sweetest scent is over here.'),
 34: dict(speaker='P', kind='nonverbal_breath', xls='Ah...', female=None, male=None),
 46: dict(speaker='B', kind='dialogue', xls='What are you hiding from?', female='Why are you pulling away?', male="Why pull away? Relax, I'm not into chubby boys.", project_utterance_id='male_EP02_combined_46_48_49'),
 48: dict(speaker='B', kind='dialogue', xls='Relax.', female="Relax. I'm into bodies like Alessia's. Hot and sexy.", male="Why pull away? Relax, I'm not into chubby boys.", project_utterance_id='male_EP02_combined_46_48_49'),
 49: dict(speaker='B', kind='dialogue', xls="I'm not interested in a skinny body like yours.", female="Relax. I'm into bodies like Alessia's. Hot and sexy.", male="Why pull away? Relax, I'm not into chubby boys.", project_utterance_id='male_EP02_combined_46_48_49'),
 50: dict(speaker='B', kind='continuation_only_not_new_line', xls='...like yours.', female=None, male=None, continuation_of_source_shot=49),
}

SELECTED = {
 '女版':{26:'Why does your bed smell so good?',28:'I just washed the bedding today.',33:'So this is where you smell the best.',46:'Why are you pulling away?',48:'Relax.',49:"I'm into bodies like Alessia's. Hot and sexy."},
 '性转男版':{26:'Oliver, why does your bed smell so good?',28:"Everything's fresh out of the wash.",33:'Turns out the sweetest scent is over here.',46:'Why pull away?',48:'Relax,',49:"I'm not into chubby boys."},
}
PREFIX={'女版':'大码女版','性转男版':'性转版男版'}

def mirror_full_id(n,version):
 return f'{PREFIX[version]}02-{(n-1)//5+1:02d}-{(n-1)%5+1:02d}'

def sha(p):
 return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def fields_for(n, v, version):
 s=data['shots'][n-1]; f=s['source_fields']; t=SPECS[n]
 perf=t[1].format(**v)
 if n in SELECTED[version]:
  perf += f'【{v[SLOTS[n]["speaker"]]}原台词】"{SELECTED[version][n]}"'
 elif n in (27,34):
  perf += '本镜仅保留上述可见困倦/吸气反应，项目原稿没有对应引号台词，不另添英文气声台词。'
 elif n==50:
  perf += '仅承49已经说出的原句尾音，保持口型收尾，不再次完整说句或添加新词。'
 env = ('奢华酒店套房，夜晚，白床枕与暖金低照度侧光。' if n<=6 else ('公寓室内门口，夜晚，门外暗、门内暖光；整体墙地与引用场景一致。' if n<=9 else f'{v["room"]}，夜晚，资产床品和空间色调不变，柔暖床头侧光。'))
 if n==6: env+='整体迅速压暗。'
 if n==7: env+='黑场渐显。'
 if n==15: env+='画面渐暗。'
 if n==16: env+='暗室全景渐亮。'
 if n==50:env+='暖白柔光闪起。'
 if n==51:env+='全屏柔白闪光达到峰值。'
 if n in (52,53):env+='白闪回落并有轻微红蓝色散余效。'
 if n==54:env+='暖色恢复。'
 if n>=55:env+='片尾安静定格。'
 angle=f['拍摄角度']
 if n==20: angle='平视（两人侧卧的面部高度，保持源截图卧姿）'
 movement=f['摄像机运动 (运镜指令)']
 if n==30: movement='固定镜头；保留源表由虚转实的焦点过渡，不新增机身移动。'
 if n==32: movement='固定镜头（原镜内由大特写跳切近景，不新增源镜号）。'
 return {'时长':f'{s["timecode"]["duration_seconds"]:g}秒（{mirror_full_id(n,version)}；原TC {s["timecode"]["start_tc"]}–{s["timecode"]["end_tc"]}）',
  '环境氛围':env,'景别':f['景别变化'],'拍摄角度':angle,'摄像机运动':movement,
  '人物角色和运动':t[0].format(**v),'人物表演':perf,'画面内容':t[2].format(**v)}

def total_settings(n, v):
 if n<=6: return f'出场角色：{v["P"]}（@{v["p_day"]}；大码体态、身份长相及日常服装统一锁定资产）；{v["B"]}仅在右上画外，不强行入镜。\n场景：@酒店；夜晚白床枕机位。\n以下所有Shot出场的角色和场景统一锁定参考图。\n画幅：竖屏9:16。'
 if n<=9: return f'出场角色：空镜；{v["B"]}仅为门后画外动作归属。\n场景：@{v["entrance"]}（公寓内门/走道）；门扇颜色、材质、把手依真实资产，源门框位置、开合调度与机位保持；不把它认定为外部入户开门。\n以下所有Shot出场的角色和场景统一锁定参考图。\n画幅：竖屏9:16。'
 return f'出场角色：{v["P"]}（@{v["p_sleep"]}；{v["p_sleep_detail"]}，大码体态不改瘦）；{v["B"]}（@{v["b_sleep"]}；{v["b_sleep_detail"]}）。\n场景：@{v["room"]}；'+(f'与@{v["entrance"]}（门口通道）连通，按源镜走到床边。' if n==10 else '保持原床边、床面与床头的机位关系。')+'\n以下所有Shot出场的角色和场景统一锁定参考图。\n画幅：竖屏9:16。'

def region(n): return 0 if n<=6 else (1 if n<=9 else 2)
allgroups=[]
for version,v in VERSIONS.items():
 directory=OUT/version; directory.mkdir(exist_ok=True)
 groups=[]
 for g in range(1,13):
  nums=list(range((g-1)*5+1,min(g*5,57)+1)); parts=[]; oldregion=None; shotrecords=[]
  for i,n in enumerate(nums,1):
   if region(n)!=oldregion:
    parts.append(total_settings(n,v)); oldregion=region(n)
   fields=fields_for(n,v,version)
   parts.append(f'Shot{n:02d}:\n'+'\n'.join(f'{k}：{value.rstrip("。；")}'+('。' if k=='画面内容' else '；') for k,value in fields.items()))
   rec={'episode':2,'source_shot':n,'source_excel_row':n+3,'shot_id':f'02-{g:02d}-{i:02d}','full_id':mirror_full_id(n,version),'prompt_label':f'Shot{n:02d}', 'fields':fields,'source_timecode':data['shots'][n-1]['timecode']}
   if n in SLOTS:
    slot=dict(SLOTS[n]); slot['speaker_name']=v[slot['speaker']]; slot['selected_source']='project_version_english_original_user_confirmed'; slot['selection_status']='project_original_selected' if n in SELECTED[version] else 'visual_only_no_corresponding_quoted_line' if n in (27,34) else 'continuation_only_no_repetition';slot['selected_text']=SELECTED[version].get(n);slot['source_xls_excel_cell']=f'F{n+3}';slot['source_raw_full']=data['shots'][n-1]['source_fields']['人物表演 (动作/表情/心理)'];slot['project_candidate']=slot['female' if version=='女版' else 'male'];slot['project_candidate_scope']='Female46/48/49 mapped to adjacent original EP03, all others original EP02; null means no exact quoted counterpart, not permission to invent or omit a source shot.'
    slot['project_candidate_episode']=3 if version=='女版' and n in (46,48,49) else 2
    if version=='女版' and n in (48,49):slot['project_utterance_id']='female_EP03_combined_48_49'
    if version=='女版' and n==46:slot['project_utterance_id']='female_EP03_46'
    rec['dialogue_slot']=slot
   shotrecords.append(rec)
  prompt='\n\n'.join(parts)+'\n'
  assert len(prompt)<5000,(version,g,len(prompt))
  path=directory/f'02-{g:02d}.txt';path.write_text(prompt)
  refs=[v['p_day']] if nums[0]<=5 else []
  if any(n in (7,8,9,10) for n in nums): refs += [v['entrance']]
  if any(n>=10 for n in nums): refs += [v['p_sleep'],v['b_sleep'],v['room']]
  if any(n<=6 for n in nums): refs += ['酒店',v['p_day']]
  refs=list(dict.fromkeys(refs))
  group={'episode':2,'version':version,'group':g,'group_id':f'02-{g:02d}','card_name':mirror_full_id(nums[0],version),'source_shots':nums,'shot_ids':[s['shot_id'] for s in shotrecords],'full_shot_ids':[s['full_id'] for s in shotrecords],'source_tcs':[s['source_timecode']['raw'] for s in shotrecords], 'total_duration':round(sum(data['shots'][n-1]['timecode']['duration_seconds'] for n in nums),1),'asset_names':refs,'prompt_path':str(path),'prompt':prompt,'character_count':len(prompt),'shots':shotrecords,'status':'visual_draft_project_original_dialogue_selected', 'platform_binding_status':'not_bound; text @names only'}
  groups.append(group);allgroups.append(group)
 (directory/'groups.json').write_text(json.dumps({'episode':2,'version':version,'source_shot_count':57,'group_count':12,'last_group_source_shots':[56,57], 'last_group_status':'preserved_two_shots_per_root_instruction','total_duration':74.9,'dialogue_source_status':'project_version_english_original_selected_user_confirmed','naming':'prefix + episode-group-intragroupShot, each card named by its first shot full ID', 'source_priority':'XLS + screenshots for visual/order/timing; actual Feishu identity/wardrobe/room; user confirms corresponding project English original for dialogue only. Narration never becomes spoken dialogue.','spoken_duration_verification':'not measured; keep strict source TC and exact dialogue, no timing guarantee','groups':groups},ensure_ascii=False,indent=2)+'\n')

for n,s in enumerate(data['shots'],1):
 first=((n-1)//6)*6+1;last=min(first+5,57)
 contact=ROOT/f'核对联系表/EP02/contact_{first:03d}_{last:03d}.png'
 s['screenshot']['visual_review_status']='reviewed_contact_sheet_tile'
 s['screenshot']['visual_review']={'contact_sheet':str(contact),'tile_index_one_based':n-first+1,'observed_static_frame':VISUAL[n-1], 'method':'model visually inspected contact sheet, each tile linked to the source shot; not OCR-only', 'limits':'Static frame verifies visible identity class, costume, framing, props and pose at captured instant. Full movement/action duration remains XLS instruction, not claimed proven by a still.'}
 s['requirements']['role_visibility_status']='visually_reviewed_static_frame'
 s['requirements']['actual_asset_binding']={version:{'role_names':{'pillow_protagonist':v['P'],'mafia_boss':v['B']},'asset_names':([v['p_day'],'酒店'] if n<=6 else [v['entrance']] if n<=9 else [v['b_sleep'],v['room']]+([v['p_sleep']] if n>=16 else [])),'binding_status':'text references prepared only; no platform binding performed'} for version,v in VERSIONS.items()}
 s['requirements']['asset_status']='actual_downloaded_asset_names_matched_locally'
data['validation']['visual_inspection_completed']=True
data['validation']['visual_inspection_pending']=None
data['validation']['visually_reviewed_shot_count']=57
data['validation']['visual_contact_sheet_count']=10
data['grouping'].update({'remainder_source_shots':[56,57],'final_tail_group_and_naming_status':'root instructed each consecutive5 source shots/group; last2 preserved without merge or padding','groups_per_version':12})
data['phase']='source_parse_visual_review_and_two_version_local_prompt_draft'
data['source_priority']='Source XLS and screenshots govern all57 shots, their timing/order/blocking/camera. User-confirmed corresponding project English original governs actual spoken dialogue; real Feishu assets govern identity/body/clothes/scene appearance. No narration is converted into character speech.'
data['grouping']['no_generation_names_assigned']=False
data['grouping']['planned_full_shot_names_assigned']=True
data['grouping']['actual_platform_cards_created']=False
data['asset_requirements']['binding_status']='actual Feishu filenames verified; no platform @binding claimed'
data['asset_requirements']['matched_assets']=[{k:a[k] for k in ('local_asset_name','local_path','sha256','nodeId')} for a in assets if a['local_asset_name'] in {v[x] for v in VERSIONS.values() for x in ('p_day','p_sleep','b_sleep','room','entrance')}|{'酒店'}]
for role in data['asset_requirements']['role_catalog']:
 for version,v in VERSIONS.items():
  is_p=role['id']=='pillow_protagonist'; role['versions'][version]['canonical_name']=v['P' if is_p else 'B'];role['versions'][version]['actual_asset_names']=([v['p_day'],v['p_sleep']] if is_p else [v['b_sleep']])
 role['asset_status']='matched_actual_downloaded_assets'
for scene in data['asset_requirements']['scene_catalog']:
 key={'hotel_suite_bed':None,'apartment_door_passage':'entrance','apartment_pink_bedroom':'room'}[scene['id']]
 scene['actual_asset_names_by_version']={ver:('酒店' if key is None else v[key]) for ver,v in VERSIONS.items()}
 scene['status']='actual_asset_matched_locally'
 if scene['id']=='apartment_pink_bedroom':scene['gender_swap_note']='Root confirms assigned room38 pink/ivory for female, room41 blue/gray for male. Change set dressing to actual asset while preserving source blocking and camera.'
 if scene['id']=='apartment_door_passage':scene['ambiguity']='Source room function is internally inconsistent; static frames confirm one interior door, not its full floor plan. Use corresponding actual asset door material; keep source framing/opening and avoid claiming exterior arrival.'
for wardrobe in data['asset_requirements']['wardrobe_catalog']:
 wardrobe['actual_asset_names_by_version']={ver:([v['p_day']] if 'hotel' in wardrobe['id'] else [v['b_sleep']] if wardrobe.get('role_id')=='mafia_boss' else [v['p_sleep']]) for ver,v in VERSIONS.items()}
 wardrobe['status']='clothes_and_identity_follow_real_asset; footwear_follow_source_action_per_root'
for issue in data['conflicts_and_pending_checks']:
 if issue['id'] in ('SOURCE_NAMES_ARE_NOT_FINAL','SOURCE_APPEARANCE_VS_ASSIGNED_ASSET'):
  issue['resolution_status']='resolved_by_actual_Feishu_names_and_visual_review'
  issue['resolution']='Eliza/Matteo Bellandi female; Oliver/Vittoria Blackwood male. Actual body, identity, outfit and scene palette replace source actor appearance; source framing and blocking preserved.'
 elif issue['id']=='APARTMENT_DOOR_FUNCTION_AMBIGUOUS':
  issue['resolution_status']='static_frame_checked_function_remains_unproven'
  issue['resolution']='One interior door, material follows corresponding real scene asset; no invented exterior arrival or extra white door. Keep source opening sequence/camera.'
 elif issue['id'] in ('CAMERA_WORDING_FOCUS_ZOOM','WITHIN_SHOT_PULLBACK_VS_JUMPCUT'):
  issue['resolution_status']='source_ambiguity_preserved_and_conservative_prompt_selected'
 elif issue['id'] in ('SOURCE_DIALOGUE_BODY_TYPE','EXACT_DIALOGUE_DIFFERS_FROM_EXISTING_ENGLISH'):
  issue['resolution_status']='resolved_by_user_selected_corresponding_project_english_original'
  issue['resolution']='Use exact project lines only at existing source slots; no new spoken Hmm/Ah where not quoted in project, source50continuation not repeated; preserve original XLS wording here as provenance.'
data['auxiliary_english_sources']['女版_相邻原稿EP03_对白候选补充']={
 'path':str((ROOT.parent/'配音制作_前3集/英文剧本/女版/女版_第03集_纯英文全文.txt').resolve()),
 'sha256':sha(ROOT.parent/'配音制作_前3集/英文剧本/女版/女版_第03集_纯英文全文.txt'),
 'text':(ROOT.parent/'配音制作_前3集/英文剧本/女版/女版_第03集_纯英文全文.txt').read_text(),
 'usage':'User confirmed project English dialogue. Original EP03 lines used only at XLS46/48/49, no addition/reorder/change to57 source shots.'}
data['execution_status']={'local_source_and_visual_review':'complete57','local_prompt_groups':'12perversion24total','dialogue_selection':'project_original_selected_per_latest_user_confirmation','browser':'not_operated','generation':'not_submitted','platform_binding':'not_performed'}
data['asset_requirement_resolution_notes']=[
 '01–06女版米白开衫/碎花连衣裙、男版白衬衫/米色短裤；16+女版米白短袖睡裙、男版藏蓝白滚边长袖长裤；10+Matteo白滚边黑丝两件睡衣，Vittoria黑蕾丝边系带睡袍。身份服装以真实资产为准，源演员粉碎花睡衣和金滚边黑袍不混入。',
 '女卧室38粉米白、男卧室41蓝灰，依实际资产替换美术色调；源镜左右位置、场内动作与机位保留，不把资产多视图拼贴或文字标签当成画面。',
 '源门白色黑圆把手，资产40/43为木门金属把手：按根线程确认，门颜色材质随真实场景，源门位置、开合与机位保留，不额外构造白门。',
 '根线程确认鞋履按场景动作：源11赤脚、16起床边拖鞋动作保留；睡衣卡只提取身份衣服，不把卡面米色鞋或黑鞋强行穿上床。',
 '用户已确认对白用两版项目对应英文原句。26/28/33/46/48/49逐字回填；27/34无对应引号台词仅可见反应，50仅承49尾音。男版46/48/49合起来只说一次原句，Relax,保留原逗号；女版46/48/49用原稿EP03对应原句且不更改本轮镜头集界。',
 '源30由虚转实与变焦表述有歧义：按静止机位保留焦点过渡；源32保留一源镜内固定机位景别跳切，不加镜号。',
]
SOURCE.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
assert sha(data['source_xlsx']['path'])==data['source_xlsx']['sha256'],'source XLS changed'
qc={'episode':2,'source_shots_per_version':57,'versions':list(VERSIONS),'groups_per_version':12,'total_prompt_groups':24,'tail_group_shots':[56,57], 'total_duration_per_version':74.9,'group_characters':{v:[g['character_count'] for g in allgroups if g['version']==v] for v in VERSIONS},'each_group_under5000':all(g['character_count']<5000 for g in allgroups),'all_source_shots_exactly_once_per_version':all([n for g in allgroups if g['version']==v for n in g['source_shots']]==list(range(1,58)) for v in VERSIONS),'dialogue_status':'project_original_selected_per_user; six spoken entries/version, absent quote at27/34 visual-only,50continuation_only','source_xlsx_sha_verified_unchanged':True,'visual_review':{'shots':57,'contact_sheets':10,'static_frame_limits_recorded':True},'binding_status':'local named refs only','open_issues':[],'exact_spoken_duration_verified':False,'naming':'episode-group-intragroupShot; full ID included in every duration field'}
(OUT/'本地正文检查.json').write_text(json.dumps(qc,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(qc,ensure_ascii=False))
