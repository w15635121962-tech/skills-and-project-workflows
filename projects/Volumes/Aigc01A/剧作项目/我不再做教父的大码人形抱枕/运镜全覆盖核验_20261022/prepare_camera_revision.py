from pathlib import Path
from decimal import Decimal
import json
import re

OUT=Path(__file__).resolve().parent
BASE=OUT.parent/'复刻全集_FormatC_V25_20261022'
original=json.loads((BASE/'复刻全集_FormatC_V25_全部提示词.json').read_text())
data=json.loads(json.dumps(original,ensure_ascii=False))
patches=[]
for name in ['patch_09_14.json','patch_15_18.json','patch_19_21.json']:
    patches.extend(json.loads((OUT/name).read_text()))
for x in patches:
    if x['position']==17 and x['unit']=='S06-B' and x['shot']==1 and x['new'].startswith('镜头：'):
        x['new']=x['new'].replace('把构图重心沿可见前臂带到肩线轮廓','把构图重心由交握处带向手腕与前臂局部，交握指尖仍留在画幅下缘')
        x['reason']='保持原交握动作的局部可见，真实升高配合原上抬，不扩出新肩部构图。'
for x in patches:
    p=x['position']; g=data['groups'][p-1]
    assert g['prompt'].count(x['old'])==1,(p,x['unit'],x['shot'],x['old'])
    if x['old'].startswith('【shot '):
        a=x['old'].split('｜');b=x['new'].split('｜')
        assert len(a)==len(b)==7
        assert a[:4]+a[5:]==b[:4]+b[5:]
        assert '固定' not in b[4]
    else:
        assert x['old'].startswith('镜头：') and x['new'].startswith('镜头：')
        assert '位置与轴线不变' not in x['new']
    g['prompt']=g['prompt'].replace(x['old'],x['new'])
results=[]
for p in range(9,22):
    g=data['groups'][p-1];o=original['groups'][p-1]
    # Everything outside shot headers and camera fields is frozen.
    strip=lambda s:[l for l in s.splitlines() if not l.startswith(('【shot ','镜头：'))]
    assert strip(g['prompt'])==strip(o['prompt']),p
    heads=re.findall(r'【shot[^】]*】',g['prompt'])
    cameras=re.findall(r'^镜头：(.*)$',g['prompt'],re.M)
    assert len(heads)==len(cameras)==len(g['shots'])
    assert sum(Decimal(x) for x in re.findall(r'duration:\s*([\d.]+)s',g['prompt']))==Decimal(str(g['duration']))
    for i,(head,camera) in enumerate(zip(heads,cameras)):
        movement=head.split('｜')[4].replace('运镜（Camera Movement）：','')
        assert '固定' not in movement
        assert re.search('推|移|升|降|拉|退',movement)
        assert re.search(r'\d+(?:cm|厘米|°|度)',camera), (p,head)
        g['shots'][i]['camera_movement']=movement
    assert len(g['prompt'])<15000
    g['revision']='format-c-v2.5_all_shots_camera_movement'
    g['native_asset_status']='pending_platform_save'
    g['camera_revision_note']='用户要求第9组起所有镜头运镜；仅更新各镜标题中的运镜与镜头字段，锁定真实路线与幅度，保留画面、人物状态、动作、视线、声音、时长、焦段及资产。'
    results.append({'position':p,'shots':len(heads),'moving_shots':len(heads),'chars':len(g['prompt'])})
assert len(patches)==92
assert sum(x['shots'] for x in results)==46
(OUT/'全部运镜替换清单.json').write_text(json.dumps(patches,ensure_ascii=False,indent=2)+'\n')
(OUT/'第9-21组_全镜运镜修正版.json').write_text(json.dumps({'groups':data['groups'][8:],'changed_positions':list(range(9,22))},ensure_ascii=False,indent=2)+'\n')
(OUT/'第9-21组_全镜运镜修正版.md').write_text('\n\n---\n\n'.join(g['prompt'] for g in data['groups'][8:]))
(OUT/'运镜本地核验.json').write_text(json.dumps({'groups':13,'shots':46,'moving_shots':46,'fixed_shots':0,'patches':92,'frozen_actor_action_audio_fields_unchanged':True,'results':results,'passed':True},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'groups':13,'shots':46,'moving_shots':46,'patches':92,'passed':True},ensure_ascii=False))
