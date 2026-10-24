from pathlib import Path
from datetime import datetime
import json
import re

BASE = Path(__file__).resolve().parent.parent / '复刻全集_FormatC_V25_20261022'
OUT = Path(__file__).resolve().parent
data = json.loads((BASE / '复刻全集_FormatC_V25_全部提示词.json').read_text())
group = data['groups'][5]
old = group['prompt']
lines = old.splitlines()
changes = []

def replace_line(prefix, new, shot=None):
    start, end = 0, len(lines)
    if shot is not None:
        start = next(i for i, line in enumerate(lines) if line.startswith(f'【shot {shot}｜')) + 1
        end = next((i for i in range(start, len(lines)) if lines[i].startswith('【shot ')), len(lines))
    hits = [i for i in range(start, end) if lines[i].startswith(prefix)]
    assert len(hits) == 1, (prefix, shot, hits)
    i = hits[0]
    changes.append({'shot': shot, 'old': lines[i], 'new': new})
    lines[i] = new

replace_line('节奏结构（Beat Structure）：', '节奏结构（Beat Structure）：组型：动作与情绪组｜5镜｜共15.0s；3.0 / 2.0 / 4.0 / 2.0 / 4.0秒，非均匀分配；动作最强拍在shot 3，暧昧余韵落shot 5。先递手停顿，握牢后一次短促有力地拉近；落枕后用女主垂眼、藏住唇角又看回他的反应放慢节奏，最后安顿为面对面闭眼圈抱。不增加动作次数与对白。')
replace_line('视觉动线（Visual Flow）：', '视觉动线（Visual Flow）：左里男主伸手→右边握牢牵拉→女主沿右近侧床面承重落原枕→两人近距离对视、羞怯垂眼再看回；最终左后男主/右前女主面对面不换位。')
replace_line('微表演（Micro-Performance）：', '微表演（Micro-Performance）：Matteo躺着看向床右的Eliza，目光停在她脸上，嘴角只有很浅的松动；Eliza先看他的手，再与他短暂相视，唇角轻抿，站姿仍稳，停半拍才靠近。', 1)
replace_line('画面：', '画面：位置锁定：Matteo左侧卧在床左里位、画面左后；Eliza站床右通道、画面右前，脚仍落地，头朝床头方向。男主下侧左前臂已经在原枕外床面。上侧右手伸向她递来的左手，手掌完整握牢、拇指扣住掌背，腕部保持自然直线；牵握接点在床右边缘上方。镜末他的右肘开始迅速收向自身腰侧，启动一次朝床左里侧的有力牵拉，在拉动尚未完成时切出。', 2)
replace_line('微表演（Micro-Performance）：', '微表演（Micro-Performance）：男主握牢后指节与前臂短暂绷紧；女主左手原先放松的手指因突来的牵力收拢在他的手上。只拍手部，不在局部特写中要求看见画外脸部反应。', 2)
replace_line('对白反应（Dialogue Reaction）：', '对白反应（Dialogue Reaction）：她递出的左手被他稳稳接住，接点先牢固后发力；她的前臂随牵力朝床里移动，另一只右手尚未接床。', 2)
replace_line('音频（Audio）：', '音频（Audio）：握紧手掌与衣料被带动的短促摩擦；无对白、旁白或配乐。', 2)
replace_line('运动强度（Motion Intensity）：', '运动强度（Motion Intensity）：先握稳，镜末短促加速发力，力度明显强于轻牵；不拧腕，不将她整个人悬吊，下一镜继续同一次牵拉。', 2)
replace_line('镜头：', '镜头：固定在床尾右通道高斜俯位，完整保留男主右肘、两人牵握接点、女主膝部与右掌落床区，不跨到床头半区。焦点落在受力链上；女主前臂和发梢在朝左里侧的加速中有短幅方向性运动模糊，床面与支撑点清楚，不用切近景遮掉落点。', 3)
replace_line('画面：', '画面：位置锁定：Matteo仍在床左里侧左侧承重、画面左后，头肩不离原枕；下侧左前臂已在枕外床面，左掌留在她上背的落点旁。Eliza从床右通道、画面右前进入自己近侧原枕区。承接上镜正在进行的同一次牵拉，男主右肘迅速收向腰侧，把她左手与上身明显带近；她被带得前倾，近侧膝迅速触到床沿、空闲右掌随即撑住自己枕旁床面，床垫在这两处受力点下陷回弹。膝与右掌承重后她顺势收上双腿，屈右肘降低肩背，Matteo的左掌从枕外接住她上背，头向近侧原枕落去。牵引只发生这一次，身体下落由床面与托背共同接住。', 3)
replace_line('视觉引导（Visual Flow）：', '视觉引导（Visual Flow）：男主左后、女主右前，受力从左后收拢的右肘经过牵握接点传到她前倾的肩背，再落到画右的膝与右掌支撑点。Matteo视线追随她的落身区域，Eliza先看接床位置，落稳前目光开始抬向近处男主；均不看镜头。背景书桌压成虚焦色块，注意力只留在牵拉与落床。', 3)
replace_line('微表演（Micro-Performance）：', '微表演（Micro-Performance）：被拉动的一瞬，Eliza肩线短暂提起、眼睛睁大，发丝随前倾扬起后落下；右掌接稳床面后她肩颈仍带一点紧张，察觉自己被带到他近前才抬眼。Matteo下颌短暂绷紧，托住她后下颌放松、左掌仍稳在她上背，目光由落点回到她脸上。', 3)
replace_line('对白反应（Dialogue Reaction）：', '对白反应（Dialogue Reaction）：女主前倾的反馈让男主在她接床后立即减速、左掌承住上背；她确认被稳稳接住后不后退，抬眼寻找他的目光，惊讶开始转成害羞。', 3)
replace_line('音频（Audio）：', '音频（Audio）：一次短促衣料摩擦、膝与手掌接床、床垫受力回弹的轻闷响；女主自然吸气一瞬，无惊叫、对白、旁白或配乐。', 3)
replace_line('运动强度（Motion Intensity）：', '运动强度（Motion Intensity）：一次短促有力的牵拉，前段加速明显，女主接床后立即减速并托住；用前臂张力、前倾速度与床垫下陷体现重量。男主不坐起，女主不被抛起、不翻过男主、不悬空横飞。', 3)
replace_line('画面：', '画面：位置锁定：Matteo仍床左里侧左侧卧、头在原枕，Eliza头肩落到床右原枕承托区，右侧身体压枕、面朝床左Matteo；本镜女主上侧左脸位于画面右上、男主近处轮廓在左下画边，床头方向不变。她下侧右臂屈肘完成降身，右手留自己枕旁，上侧左手仍被男主右手握住；双腿已收床。男主左掌从枕外托住她肩胛上背，落枕时停住牵力，两人的脸因这次落身突然近在咫尺。', 4)
replace_line('视觉引导（Visual Flow）：', '视觉引导（Visual Flow）：女主落枕动线停在画面右上，她先看左下近处Matteo的眼睛，随后把视线垂到两人仍握着的手；男主画外视线留在她脸上。焦点始终锁女主眼睑与唇角，不因她垂眼改动实际床位。', 4)
replace_line('微表演（Micro-Performance）：', '微表演（Micro-Performance）：Eliza落稳后先睁大眼，和他近距离对上视线；下一瞬眼睑垂下、下巴轻收，唇角想扬起又被她抿住，肩颈短暂绷住后只放松一小点，藏不住被突然拉近的羞意。不开怀大笑，不哭、不叹气。', 4)
replace_line('对白反应（Dialogue Reaction）：', '对白反应（Dialogue Reaction）：男主托住上背给她稳定支撑，她因对上他的目光而垂眼；牵握保持到本镜末，停在她羞怯而没有躲开的状态，下一镜才松开换成圈腰。', 4)
replace_line('音频（Audio）：', '音频（Audio）：一次落枕轻响、女主尚未完全平复的自然呼吸；无对白、旁白或配乐。', 4)
replace_line('运动强度（Motion Intensity）：', '运动强度（Motion Intensity）：牵拉后的减速落枕，女主只有小幅垂眼与收下巴；右侧承重，不重复倒床、不转为仰面压抱。', 4)
replace_line('画面：', '画面：位置锁定：Matteo固定床左靠墙里侧、画面左后，左侧身体压床；Eliza固定床右靠通道近侧、画面右前，右侧身体压枕、面向男主；两人头同朝床头、各在原枕承托区。Matteo松开牵握的右手，上侧右臂沿她腰外侧圈住；下侧左掌托肩胛上背、肘前臂由床面承托，稳稳合臂把她沿床面收近一点，随即停住，鼻尖仍留一掌左右距离。Eliza左手停在两人胸前、右手留自己枕旁，身体在他的圈抱里先绷一瞬再缓缓放松，没有回抱。她先垂眼停在他胸前，又忍不住抬眼看他；男主一直躺着等她看回。近距离停留后，两人肩线慢慢落下、眼睑先后合拢，末态为原床位面对面闭眼圈抱，直接接下一组。', 5)
replace_line('视觉引导（Visual Flow）：', '视觉引导（Visual Flow）：重心从男主收稳的腰侧右臂回到上三分之一的两张侧脸；Eliza视线先落两人胸前再抬到Matteo眼睛，男主目光停在她眼睛与垂下的眼睑上，均不对镜头。镜尾眼睑合拢、没有眼球追视，机位始终在床尾右通道一侧。', 5)
replace_line('微表演（Micro-Performance）：', '微表演（Micro-Performance）：Eliza被收近时左手指尖轻轻蜷起，先垂眼抿唇，再偷偷看回，唇角最后松出一点压不住的羞怯笑意；Matteo看见她抬眼后目光软下来、唇角微微牵动，不追吻、不抬身。短暂对视留住半拍后，她先缓缓合眼、唇角归于安静，他随后合眼，双方肩颈逐渐放松。', 5)
replace_line('对白反应（Dialogue Reaction）：', '对白反应（Dialogue Reaction）：她因他稳稳圈住而垂眼，他没有立刻移开目光，等到她重新看回；两人的目光接住后停留，才一起从羞怯与试探中安顿下来。稳定终态对接下一组闭眼嗅发的起态。', 5)
replace_line('音频（Audio）：', '音频（Audio）：衣料与床单轻摩擦、两人距离很近的自然呼吸由稍乱变平稳；无对白、旁白、夸张喘息、心跳配乐或音乐。', 5)
replace_line('运动强度（Motion Intensity）：', '运动强度（Motion Intensity）：稳而明确地圈紧一次，随后保持、不再猛拉；前段有收拢力度，后段以近距离停顿和微表情保留暧昧。男主不坐起、不翻压到她上方，女主不移到他身上，不换枕、不改同向背抱。', 5)

new = '\n'.join(lines) + ('\n' if old.endswith('\n') else '')
assert re.findall(r'§ASSET:([^§]+)§', new) == re.findall(r'§ASSET:([^§]+)§', old)
assert re.findall(r'duration: ([\d.]+)s', new) == ['3.0', '2.0', '4.0', '2.0', '4.0']
assert new.count('【shot ') == 5
for phrase in ['握力只够引导', '牵手只指方向', '不猛拽', '双方放松；不新增笑', '两臂轻合']:
    assert phrase not in new, phrase
(OUT / '第6组_修订前提示词.md').write_text(old)
(OUT / '第6组_加强牵拉与羞意_提示词.md').write_text(new)
(OUT / '逐段替换清单.json').write_text(json.dumps(changes, ensure_ascii=False, indent=2))
(OUT / '第6组_待保存.json').write_text(json.dumps({**group, 'prompt': new, 'revision': 'format-c-v2.5_s06_stronger_pull_shy_response', 'native_asset_status': 'pending_platform_save', 'action_preservation_note': '用户2026-10-22明确要求本组加大牵拉力度、女主更害羞、加强暧昧；保留5镜15秒、原床位枕位、一次牵拉落床及面对面终态、原资产与无对白设置。'}, ensure_ascii=False, indent=2))
print(json.dumps({'patches': len(changes), 'chars': len(new), 'group': 6, 'planned_seconds': 15, 'shots': 5}, ensure_ascii=False))
