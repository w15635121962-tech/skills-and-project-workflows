import json,copy,importlib.util
from pathlib import Path
root=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('builder',root/'build_prompts.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
allg=json.loads((root/'全部平台填充.json').read_text());old=copy.deepcopy(allg)
backup=root/'EP12/人物强化前平台填充.json'
if not backup.exists():backup.write_text(json.dumps([g for g in old if g['episode']==12],ensure_ascii=False,indent=2))
gg=[g for g in allg if g['episode']==12]
# 已批准事件、台词、镜数、时长、席位、灯光不变；只修订行为表现。
mods={
(4,1):('承接第一节点已绿，Elena先看左路密集光标再看右侧第二节点，右腕固定桌面；Madison站椅后左0.8m，先斜看Silas寻求认同，嘴角礼貌扬起而眼睑不跟随，肩线仅朝他转15度；Silas在右后1m先回她一个短促关注，再看Elena手指，不向Elena点头或赞许；三人双脚/坐姿不换位','Elena看B3右侧第二节点；Madison看Silas眼睛；Silas先看Madison再看Elena的键区','Elena判断不受身后二人影响；Madison笑意只在唇角，像在确认盟友；Silas对Madison的目光先软后收，对Elena只作技术审视'),
(4,3):('镜头从屏边同轴微弧移至Elena完整正脸，她开始一次短输入；Madison左后收住对Silas的礼貌笑，视线落女主操作，自己右指捏比赛服下摆，嫉妒被压在闭口里；Silas右后盯屏，却把肩线留向Madison一侧，没有回应Elena的成绩；脚仍原位，双方不触碰','Elena看B3右路入点；Madison看Elena右手；Silas看B3屏而肩仍偏Madison','Elena嘴闭目光稳定；Madison唇角先收、指节后紧；Silas下颌轻抬的优越感未完全退去，眨眼慢于Madison'),
(5,3):('回到B3正脸，Elena手停而目光锁左侧开放支路；Madison在左后把绷紧的唇角松出一个小幅礼貌笑，眼睛却先斜看Silas判断他是否仍站自己；Silas右后先回看Madison，随后看屏，没有看Elena的脸；两人仍隔既定1.2m，不跨到椅前','Elena看B3左侧开放支路；Madison看Silas眼睛；Silas先看Madison再看B3屏','Madison笑容快于眼神恢复，是装作镇定地试探站队；Silas先接她目光的习惯清楚可见，Elena不寻求他认可'),
(7,3):('B3第二节点从未捕获变绿，实时比分1–3变2–3，小型历史轨迹仅保留0–3、1–3；镜头缓拉到Elena正脸和后景二人。Madison左后先看比分，再朝Silas抬内眉并露半拍薄笑，自己的手仍捏下摆；Silas右后下意识转眼确认Madison，嘴闭，随即僵住看Elena手，不替女主欢呼；原席与支撑不变','Elena看已绿第二节点；Madison先看比分再看Silas；Silas先看Madison再落Elena右手','Elena收指停稳；Madison先整理礼貌面具、眼神仍带排斥；Silas原本朝Madison的注意被事实打断，唇角不形成自豪微笑'),
(11,1):('Silas站B3右后1m，先被Madison从左后0.8m投来的求确认目光牵住，肩线仅转15度作条件反射回应；随即看Elena已停的手和2–3比分，原本略抬的下颌沉下，手指松开垂腰侧，双脚不动、不碰Elena；Madison迅速收回柔笑压唇，仍留左后','Silas先看Madison眼睛、再看Elena右手与比分；Madison看Silas后转屏；Elena看最后两节点','Silas先顾Madison的习惯暴露后才被事实压住，表现自尊受挫与心虚；Madison笑容像开关一样收起，Elena闭口等防线调整'),
(11,2):('Silas自己的眼睛从Elena屏边移到B3桌沿，下眼睑收、下颌绷紧，视线不敢抬向Elena；自己的右拇指搓一下食指侧边后停，站位不变，不把崩塌演成关心女友的深情；画外Madison左后仍压唇捏自己的下摆，Elena仍坐B3','Silas看B3桌沿，回避Elena的眼睛；Madison留左后看屏；Elena看最后两节点','Silas想维持体面却抬不起下颌，短眨后垂眼，是过去轻视被揭穿的心虚；不流泪、不加内心旁白'),
(11,3):('Elena始终坐B3安静等待最后两节点防守调整，右手停止输入。Madison左后0.8m先借Silas的回避停一拍，再把脸朝场馆公开视域摆回礼貌中性，自己下摆仍有被捏的褶；Silas右后1m垂目，肩线朝Madison的角度逐渐收回原面屏方向，仍不给Elena道歉、祝贺或触碰；三人完整带回原位置','Elena看最后两节点；Madison看舞台上方评分后回B3屏；Silas看桌沿，不与Elena对视','Madison管理公开形象与私下嫉妒的差异可见；Silas从习惯性护Madison到被事实压住，最后闭口垂目；Elena不回头处理两人'),
(13,3):('屏中第三节点变绿，比分2–3到3–3；Elena仍坐B3，镜头短拉保持她居中并带回Madison左后0.8m与Silas右后1m。Madison看3–3后试着牵唇成礼貌笑，眼眉未松、右手从捏下摆改为压平褶痕后停；Silas先瞥Madison求体面的表情，随后立即落桌沿，仍不敢面对Elena，不借成绩把自己摆成支持者','Elena看第三节点与3–3；Madison看比分再看Silas；Silas短看Madison后落B3桌沿','Elena胜在判断并不寻求二人认可；Madison笑意没到眼睛，整理衣褶是在掩饰失控；Silas没有庆祝或拥抱，闭口回避落稳')
}
for (n,i),(act,gaze,face) in mods.items():
 s=gg[n-1]['shots'][i-1];s.update(action=act,gaze=gaze,face=face,reaction=act)
anchor='人物行为锁：Madison是善于伪装关心、争夺注意并操纵站队的坏女孩，以对Silas柔笑、对Elena冷眼、私下捏衣褶等行为显露嫉妒，不演无辜朋友；Silas长期轻视和忽视Elena、优先回应Madison，此处事实揭穿后先保体面再回避，不能演成温柔支持者。第12集已分手，Silas是Elena前男友；不补亲吻、拥抱、身体接触、对白或既定席位之外的走位。两人各用本人比赛服资产，只取外貌与服装，不继承资产板上的温柔守护标签、错误阵营标题或板内台词。'
for g in gg:
 g['prompt']=b.render(g).replace('，本次不提交视频。','。')
 if g['scene']=='nb':g['prompt']=g['prompt'].replace('空间锁：',anchor+'\n空间锁：',1)
 g['generation_authorized']=True
 # 动作修改有具名二人，渲染器需把两人各自资产卡带入各镜，而非只组头。
 (root/f'EP12/G{g["group"]:02d}.txt').write_text(g['prompt'])
actual=[l for g in gg for s in g['shots'] for l in s.get('lines',[])]
ledger=json.loads((root/'英文原台词核对底稿.json').read_text())
assert actual==[l for r in ledger['12'] for l in r['lines']]
for g,prev in zip(gg,[g for g in old if g['episode']==12]):
 assert len(g['shots'])==len(prev['shots']) and g['duration']==prev['duration']
 assert all(a['lines']==p['lines'] and a['duration']==p['duration'] for a,p in zip(g['shots'],prev['shots']))
 assert '强制要求： 人物皮肤须保持细腻' in g['prompt']
 assert not g['blocked']
(root/'全部平台填充.json').write_text(json.dumps(allg,ensure_ascii=False,indent=2))
(root/'EP12/EP12_平台填充.json').write_text(json.dumps(gg,ensure_ascii=False,indent=2))
(root/'EP12/EP12_完整FormatC_V2.6.md').write_text('\n\n---\n\n'.join(g['prompt'] for g in gg))
(root/'EP12-25_全部提示词.md').write_text('\n\n---\n\n'.join(g['prompt'] for g in allg))
(root/'人物行为锚点_用户20261009.md').write_text('# 用户角色定位与行为锚点\n\n'+anchor+'\n\n本次第12集修改范围：G04、G05、G07、G11、G13无声表演。继承14组42镜、原英文台词顺序、时长、灯光、B3三人席位、R1—R6独立人物和比分推进。\n\n素材图文字只作外貌资料，角色行为以用户最新要求与剧本时间线为准。后续各集按其事件进度强化伪装、挑拨、偏袒和自我中心；第24集的最终接受边界仍按原作，不把人物改成永不变化。\n')
print(json.dumps({'groups':len(gg),'shots':sum(len(g['shots']) for g in gg),'duration_s':sum(g['duration'] for g in gg),'dialogue_verbatim':True,'modified_groups':sorted({n for n,i in mods}),'max_chars':max(len(g['prompt']) for g in gg)},ensure_ascii=False))
