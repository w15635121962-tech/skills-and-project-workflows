from pathlib import Path
import json,re
R=Path(__file__).resolve().parent
D=json.loads((R/'修改前_复刻全集_FormatC_V25_全部提示词.json').read_text())
patches=[]
def put(pos,shot,field,old,new,reason):
 assert D['groups'][pos-1]['prompt'].count(old)==1,(pos,shot,field)
 patches.append(dict(timeline_position=pos,shot=shot,field=field,old=old,new=new,reason=reason))
def lines(pos,shot):
 blocks=re.split(r'(?=【shot\s+\d+)',D['groups'][pos-1]['prompt'])[1:]
 return blocks[shot-1].splitlines()
lock=' 身体轴向与承托锁定：两人躯干长轴沿床长方向、近于平行床面，Matteo左侧头部始终落在原枕左承托区，左肩和左髋由床垫承重；Eliza右侧头部落在原枕右承托区，右肩与右髋压床。两张脸留在枕区近似同一高度，男主不能在女主上方竖起上身、倚床头半坐或用手肘撑高自己。局部镜头不包含头髋时，这些支撑在画外保持，不要求把全身塞入特写。'
for pos in [14,15,16]:
 for i,block in enumerate(re.split(r'(?=【shot\s+\d+)',D['groups'][pos-1]['prompt'])[1:],1):
  old=next(x for x in block.splitlines() if x.startswith('画面：'))
  put(pos,i,'画面',old,old+lock,'第14组成片已出现男主坐起的偏差，逐镜以床面和原枕明确现实承托，不改变原侧卧动作。')
# Preserve the existing single-person cameras while leaving a visible pillow contact cue.
for pos,shot in [(14,2),(14,4),(15,2),(16,1)]:
 old=next(x for x in lines(pos,shot) if x.startswith('镜头：'))
 put(pos,shot,'镜头',old,old+' 头肩构图保留男主左侧头部与原枕接触的一小段边缘，明确他横卧在床面；不以竖直上身的构图代替落枕侧卧。','给可见枕面接触证据，防止只凭脸部近景误生成为坐姿；原机位、运镜幅度、景别不改。')
# Local CU cannot show the distant chest hand.
for field in ['微表演（Micro-Performance）','对白反应（Dialogue Reaction）']:
 old=next(x for x in lines(14,1) if x.startswith(field+'：'))
 new=(field+'：本腰侧局部只见被外右掌的一次短促收拢和被面受力，随后恢复稳定；女主左手在胸前画外停住，不另把胸前手指塞进腰侧特写。男主不反复揉捏。')
 if field.startswith('对白'):new+=' 双方在画外均不新增说话口型。'
 put(14,1,field,old,new,'腰侧局部与胸前左手不在同一局部视野，澄清手部归属，不改停指事件。')
# Eyes lower here; the later group still owns the deliberate eyes-closing event.
for shot in [3,4]:
 old=next(x for x in lines(14,shot) if x.startswith('微表演（Micro-Performance）：'))
 new=old+' 末态是目光下垂、眼睑仍微开；正常眨眼后回到微开，不提前进入下一组的闭眼装睡。'
 put(14,shot,'微表演（Micro-Performance）',old,new,'第14组成片后段已变成闭眼，明确当前只是垂眼，保持14→15的表演顺序。')
(R/'root_14_16_patches.json').write_text(json.dumps(patches,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'root_patches':len(patches),'groups':[14,15,16]},ensure_ascii=False))
