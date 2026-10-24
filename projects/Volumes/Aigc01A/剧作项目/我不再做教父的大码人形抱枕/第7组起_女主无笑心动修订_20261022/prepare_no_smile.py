from pathlib import Path
import json
import re

OUT = Path(__file__).resolve().parent
BASE = OUT.parent / '复刻全集_FormatC_V25_20261022'
data = json.loads((BASE / '复刻全集_FormatC_V25_全部提示词.json').read_text())
original = json.loads(json.dumps(data, ensure_ascii=False))
changes = {}

def change(position, shot, prefix, new=None, edits=None):
    g = data['groups'][position-1]
    lines = g['prompt'].splitlines()
    start, end = 0, len(lines)
    if shot is not None:
        start = next(i for i,s in enumerate(lines) if s.startswith(f'【shot {shot}｜'))+1
        end = next((i for i in range(start,len(lines)) if lines[i].startswith('【shot ')),len(lines))
    hits = [i for i in range(start,end) if lines[i].startswith(prefix)]
    assert len(hits)==1,(position,shot,prefix)
    i=hits[0]; old=lines[i]
    if edits:
        new=old
        for a,b in edits:
            assert a in new,(position,shot,a)
            new=new.replace(a,b)
    assert new and new!=old
    key=(position,i)
    if key not in changes:
        changes[key]={'position':position,'shot':shot,'old':old,'new':new}
    else:
        changes[key]['new']=new
    lines[i]=new
    g['prompt']='\n'.join(lines)+ ('\n' if g['prompt'].endswith('\n') else '')

for p in range(7,17):
    old = data['groups'][p-1]['prompt'].splitlines()[3]
    if p<=12:
        lock=' 女主表演锁定：Eliza全组不微笑、嘴角不上扬，嘴角保持自然平直；一点心动只在各镜已有的眼神停留、垂眼、手指与肩颈轻微紧张中流露，不新增动作或主动亲吻。资产只锁定身份与外形，不复制资产图中的笑容。'
    else:
        lock=' 女主表演锁定：Eliza全组不微笑、嘴角不上扬；按当前剧情保留受伤、克制和装睡的状态，未退的心动不转为愉悦表情。资产只锁定身份与外形，不复制资产图中的笑容。'
    change(p,None,old,new=old+lock)

change(7,1,'微表演（Micro-Performance）：',edits=[('先前羞怯的微蜷','先前心动后留下的微蜷'),('唇角回到安静','嘴角自然平直，没有上扬')])
change(7,3,'视觉引导（Visual Flow）：',edits=[('收稳的唇角','自然平直的唇线')])
change(7,3,'微表演（Micro-Performance）：',new='微表演（Micro-Performance）：Eliza眼睑仍合着，嘴角自然平直、不上扬；先前心动留下的细微紧张随困意渐缓，肩颈慢慢放松，尚未因发间停留重新睁眼。')
change(8,1,'微表演（Micro-Performance）：',new='微表演（Micro-Performance）：Eliza眼睑只抬起一线，嘴角自然平直、没有上扬，双唇只完成原句口型；一点心动留在短暂抬起的眼睑和指尖轻紧中，句后左手指节渐松，困意重新占上来。Matteo安静看她，不突然摸索。')
change(9,4,'微表演（Micro-Performance）：',new='微表演（Micro-Performance）：Eliza眼睑由困意慢慢抬开，目光停在近处男主下颌，嘴唇微分但嘴角自然平直、不上扬；眼神多停一瞬，指尖仍紧，像还没准备好与他对上眼。一点心动和突然清醒并存，不叹气、不夸张扭捏。')
change(10,3,'微表演（Micro-Performance）：',new='微表演（Micro-Performance）：Eliza把目光从近处下颌抬向Matteo眼睛方向，睫毛有一瞬轻颤，嘴唇仍微分、嘴角自然平直；左手松开自己衣料后落到他胸前，指尖因心动略收着。她想拉开颈侧那一点过近的距离，抬头幅度小而急，不微笑、不叹气。')
change(11,2,'微表演（Micro-Performance）：',new='微表演（Micro-Performance）：Eliza眼睑短促张开后停在他的眼睛上，嘴唇微分、嘴角自然平直，没有上扬；意外触碰带来的一点心动让她一时怔住，目光没有立即移开。Matteo下颌仍轻绷，眼神失去惯常从容。两人均没有低头、微笑或继续靠近。')
change(11,3,'微表演（Micro-Performance）：',new='微表演（Micro-Performance）：误触后的静止仍在，两人胸廓起伏恢复得不一样：Eliza浅而略快，嘴角自然平直、没有笑意，目光带着未掩住的心动停在他眼睛；Matteo下颌只松开一丝，眼睛仍没移开。两人没有追近，也没有提前演退开。')
change(12,1,'微表演（Micro-Performance）：',edits=[('唇角收住','嘴角保持自然平直')])
change(12,2,'微表演（Micro-Performance）：',edits=[('唇角压住','嘴角自然平直、没有上扬')])
change(13,3,'微表演（Micro-Performance）：',edits=[('嘴角慢慢抿平','原本平直的唇线轻轻收紧')])
change(13,3,'对白反应（Dialogue Reaction）：',edits=[('唇角抿平','唇线轻紧')])

face_shots={7:[1,3],8:[1,2],9:[1,4],10:[3],11:[1,2,3],12:[1,2],13:[3],14:[1,3],15:[3,4],16:[1,2,3]}
for p,shots in face_shots.items():
    for n in shots:
        prefix='负面提示词（Negative Prompt）：'
        sections=re.split(r'【shot\s+\d+[^】]*】',data['groups'][p-1]['prompt'])
        old=next(s for s in sections[n].splitlines() if s.startswith(prefix))
        change(p,n,prefix,new=old.rstrip('；。')+'；女主Eliza微笑、女主Eliza嘴角上扬、女主Eliza露齿笑、女主Eliza甜笑。')

for p in range(7,22):
    a=data['groups'][p-1]['prompt']; b=original['groups'][p-1]['prompt']
    assert re.findall(r'^音频（Audio）：.*$',a,re.M)==re.findall(r'^音频（Audio）：.*$',b,re.M)
    assert re.findall(r'【shot[^】]*】',a)==re.findall(r'【shot[^】]*】',b)
    assert re.findall(r'§ASSET:([^§]+)§',a)==re.findall(r'§ASSET:([^§]+)§',b)
    assert len(a)<15000
    if p<=16:
        data['groups'][p-1]['revision']='format-c-v2.5_eliza_no_smile_subtle_attraction'
        data['groups'][p-1]['native_asset_status']='pending_platform_save'
        data['groups'][p-1]['no_smile_revision_note']='2026-10-22用户要求第7组起女主不笑，仅一点心动；保持Matteo原有浅笑、原动作事件及后续受伤装睡状态。'
patches=list(changes.values())
(OUT/'逐段替换清单.json').write_text(json.dumps(patches,ensure_ascii=False,indent=2)+'\n')
(OUT/'第7-21组_无笑心动修正版.json').write_text(json.dumps({'groups':data['groups'][6:],'changed_positions':list(range(7,17))},ensure_ascii=False,indent=2)+'\n')
(OUT/'第7-21组_无笑心动修正版.md').write_text('\n\n---\n\n'.join(g['prompt'] for g in data['groups'][6:]))
print(json.dumps({'reviewed_groups':15,'changed_groups':10,'patches':len(patches),'female_face_negative_shots':sum(map(len,face_shots.values())),'audio_and_actions_preserved':True},ensure_ascii=False))
