from pathlib import Path
import json
import re
from decimal import Decimal

OUT = Path(__file__).resolve().parent
BASE = OUT.parent / '复刻全集_FormatC_V25_20261022'
original = json.loads((BASE / '复刻全集_FormatC_V25_全部提示词.json').read_text())
patches = []
for name in ['patch_07_11.json', 'patch_12_16.json', 'patch_17_21.json']:
    patches.extend(json.loads((OUT / name).read_text()))

def extra(position, shot, prefix, new, reason):
    p = original['groups'][position-1]['prompt']
    section = re.split(r'【shot\s+\d+[^】]*】', p)[shot]
    old = next(line for line in section.splitlines() if line.startswith(prefix))
    patches.append(dict(position=position, shot=shot, old=old, new=new, reason=reason))

extra(13, 2, '对白反应（Dialogue Reaction）：',
      '对白反应（Dialogue Reaction）：Matteo用原句中的比较维持表面轻松，手臂却留在腰背；Eliza虚化肩线短促绷紧，嘴唇合拢，完整眼部反应留到下一镜。只有男主按原句生成口型。',
      '同步当前表演分寸，区分表面轻佻与身体留人。')
extra(13, 3, '对白反应（Dialogue Reaction）：',
      '对白反应（Dialogue Reaction）：名字与比较使Eliza把尚存的期待收住，目光降到他胸前、唇角抿平；男主原圈抱未撤，她没有争辩或回应口型。',
      '明确垂眼由比较触发，延续受伤而非困倦。')
extra(13, 4, '对白反应（Dialogue Reaction）：',
      '对白反应（Dialogue Reaction）：Eliza垂眼、唇线收紧后不再把目光交回，Matteo看着她的反应，轻佻唇角逐渐收住，双臂仍不放开；双方闭口，停在她克制受伤、他未撤拥抱的矛盾里。',
      '删除不追加新表情的重置指令，与新版残留情绪一致。')
p = original['groups'][14]['prompt']
section = re.split(r'【shot\s+\d+[^】]*】', p)[4]
old = next(line for line in section.splitlines() if line.startswith('画面：'))
extra(15, 4, '画面：', old.replace('Eliza闭眼装睡、唇线平静', 'Eliza闭眼装睡、唇线保留轻紧').replace('女主尚未真正睡着', '女主意识一直清醒、只是装睡'),
      '画面字段同步装睡定义，避免与表演字段冲突。')

data = json.loads(json.dumps(original, ensure_ascii=False))
for patch in patches:
    g = data['groups'][patch['position']-1]
    assert g['prompt'].count(patch['old']) == 1, (patch['position'], patch['shot'], patch['old'])
    assert patch['old'].split('：',1)[0] == patch['new'].split('：',1)[0]
    g['prompt'] = g['prompt'].replace(patch['old'], patch['new'])
changed = sorted({x['position'] for x in patches})
fields = ['叙事任务（Narrative Task）','镜头','画面','视觉引导（Visual Flow）','微表演（Micro-Performance）','对白反应（Dialogue Reaction）','人物背景融合（Subject-Background Integration）','光影细节（Lighting Detail）','音频（Audio）','运动强度（Motion Intensity）','负面提示词（Negative Prompt）']
source = Path('/Users/zc/.codex/skills/short-drama-prompts-v3/references/format-c-v2.5-source.md').read_text()
quality = next(s for s in source.splitlines() if s.startswith('写实照片级、'))
skin = next(s for s in source.splitlines() if s.startswith('强制要求： 人物皮肤须'))
for p in range(7,22):
    g = data['groups'][p-1]; oldg = original['groups'][p-1]
    a, b = g['prompt'], oldg['prompt']
    assert re.findall(r'§ASSET:([^§]+)§', a) == re.findall(r'§ASSET:([^§]+)§', b)
    assert re.findall(r'^音频（Audio）：.*$', a, re.M) == re.findall(r'^音频（Audio）：.*$', b, re.M)
    assert re.findall(r'【shot[^】]*】', a) == re.findall(r'【shot[^】]*】', b)
    assert a.count(quality) == a.count(skin) == a.count('固定画质词（Fixed Quality Descriptor）')
    assert sum(Decimal(x) for x in re.findall(r'duration:\s*([\d.]+)s', a)) == Decimal(str(g['duration']))
    for section in re.split(r'【shot\s+\d+[^】]*】', a)[1:]:
        for field in fields:
            assert len(re.findall('^'+re.escape(field)+'：',section,re.M)) == 1, (p,field)
    assert len(a) < 15000
    if p in changed:
        g['revision'] = 'format-c-v2.5_actor_state_continuity_verified'
        g['native_asset_status'] = 'pending_platform_save'
        g['actor_state_revision_note'] = '用户要求承接新S06核验后续演员状态；只修羞意、困意、意外触碰、受伤克制与装睡/真睡的因果连续性，不改原动作事件、对白、时长、资产和镜头结构。'
(OUT / '全部待替换段落.json').write_text(json.dumps(patches,ensure_ascii=False,indent=2)+'\n')
(OUT / '后续15组_核验后提示词.json').write_text(json.dumps({'groups':data['groups'][6:], 'changed_positions':changed},ensure_ascii=False,indent=2)+'\n')
(OUT / '后续15组_核验后提示词.md').write_text('\n\n---\n\n'.join(g['prompt'] for g in data['groups'][6:]))
(OUT / '本地结构与演员状态核验.json').write_text(json.dumps({'reviewed_positions':list(range(7,22)), 'changed_positions':changed, 'unchanged_positions':[p for p in range(7,22) if p not in changed], 'patches':len(patches), 'dialogue_unchanged':True,'audio_unchanged':True,'shots_duration_assets_unchanged':True,'passed':True},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'reviewed':15,'changed_positions':changed,'patches':len(patches),'passed':True},ensure_ascii=False))
