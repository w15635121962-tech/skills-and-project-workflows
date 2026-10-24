"""第二轮只修订G03/04/05/07；保留其余已提交组与旧投递记录。"""
from pathlib import Path
import json,re,copy,ast
import build_prompts as b
root=Path(__file__).parent
allg=json.loads((root/'全部平台填充.json').read_text())
groups=[g for g in allg if g['episode']==12]
old=copy.deepcopy(groups)
backup=root/'EP12/第二轮屏幕修订前平台填充.json'
if not backup.exists():backup.write_text(json.dumps(old,ensure_ascii=False,indent=2))
old=json.loads(backup.read_text())
# 只读取上一轮已审核的规则字符串，不执行上一轮写文件脚本。
ns={}
tree=ast.parse((root/'EP12_screen_coverage_patch.py').read_text())
for node in tree.body:
 if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('rules','duel','backgrounds') for t in node.targets):
  exec(compile(ast.Module(body=[node],type_ignores=[]),'locked_rules','exec'),ns)
rules=ns['rules'];backgrounds=ns['backgrounds']
duel='对垒覆盖契约：蓝席在观众视向的左、红席在右，双方不共桌。摄影机保持蓝红连线的观众侧；G03队员01发令→队员02独立反应→大屏暴露左路集中；G04 Elena判断右路并开始输入→G05大屏右路转移、左路暴露→Elena反应；G06 Xavier收缩指令及副队长反应→G07 Elena确认空隙、按键、大屏确认第二分→G08观众接收结果。攻守在双方不同区域之间交替，不能把正反打拍成同一背景的两张肖像。'
g3=groups[2]
g3['shots'][1].update(action='反打队员02坐R4的眼眉大特写，承接画左R3队员01完整发令结束；02眼睛由画左01方向落回自己R4屏正面，下眼睑收紧，右指在画外本人键区开始左路防守，唇闭合。01仍坐R3、耳麦在自己桌右，其他队员R1—R6原位；本镜只拍02眼眉，绝不把光标叠在脸前或电脑背壳',gaze='队员02先看画左R3队员01，再低看本人R4屏正面，瞳孔不落镜头',face='02眉内侧收拢后下眼睑紧一下，承受队长命令频繁改变带来的迟疑，闭口接招',reaction='01短令收句触发02转眼并收眼睑，操作落回本人终端，反应晚于发令不重复说词',move='沿R3—R4连线的桌前半空间反打到R4；机高约1.35m平角、短推10cm在02眼眉中心落稳')
g4=groups[3]
g4['shots'][1].update(action='Elena自己的右食指贴键区，右腕受B3桌面承托，无暴力乱敲；摄影机从桌前左上方高于显示器顶沿的通视角俯拍，仅取她的手指、键帽和黑衣袖口，键盘真实位于显示器后方桌面。显示器只可露窄顶边与不透明侧背，不出现左路/右路网络图、代码或比分',gaze='Elena看朝向自己的B3屏右侧路径，摄影机只看手与键盘，不共享她的屏面视点',move='从B3桌前左上方俯拍右手与键区，机高建议2.0m按不遮挡键区调整，向指尖实推10cm，落幅不穿屏或手')
g4['shots'][2]['action']=g4['shots'][2]['action'].replace('镜头从屏边同轴微弧移至Elena完整正脸','切回桌前左侧Elena完整正脸居中，前景低位哑黑显示器背壳不遮眼嘴，镜头同轴短移20cm')
g5=groups[4]
g5['shots'][0].update(action='Elena坐B3的眼眉与透明眼镜大特写，承接她刚开始的短输入，眼睛从本人屏中左路封锁移向右侧入口；镜片仅有外部光源窄反射，不生成可读代码、比分、HUD或整张网络地图，眼睛本身不发光。Madison左后0.8m、Silas右后1m在画外原位',gaze='Elena视线从本人屏左侧转右侧入口，略向画右下偏光轴；本人眼睛不直视镜头',face='Elena下眼睑聚焦后轻收，判断右侧入口仍可通过；右手继续先前短输入，不重新开始操作',reaction='本人屏路由状态变化触发Elena转眼与收眼睑，后景二人仍在既定站位，没有台词',move='桌前左半空间平视眼眉，短推10cm，镜片与真实鼻梁有视差，不穿入眼球')
g7=groups[6]
g7['shots'][0]['action']='Elena坐B3正脸中心确认左翼开放，自己的右食指悬Enter上2cm；桌前镜头下部只见哑黑不透明显示器背壳，网络内容不出现在她脸前。Madison左后0.8m先向Silas抬内眉寻求认同，嘴角礼貌上扬但眼睑未松；Silas右后1m先回应Madison一眼，再被Elena准备按键的手牵住注意，嘴闭、不替她欢呼。两人各穿本人蓝白比赛服、脚位不变，不触碰Elena'
g7['shots'][0]['reaction']='Elena看红方追逐造成的左翼空隙而准备唯一一次按键；Madison借薄笑寻求Silas站自己一边，Silas先看她后看Elena的手，反应不同步且全员闭口'
g7['shots'][1]['action']+='；从桌前左上方高于屏顶的通视角只拍本人手、键区和黑衣袖口，显示器哑黑背壳不透，不在键盘上叠加UI'
g7['shots'][1]['move']='B3左前高位俯拍自己的右食指与Enter接触，沿指尖实推10cm，键帽触底与回弹时停稳，不穿屏背'

screen_base=re.search(r'【shot 3.*?(?=\n皮肤专项负面词：)',groups[12]['prompt'],re.S).group()
screen_info={
 3:('展示左路防守集中和右路空隙','比分保持1–3，第二点尚未捕获；红色防守光标集中画左路径，右侧第二节点入口的检查覆盖稀薄。左右是网络拓扑固定方向，蓝起点在左、红目标在右，红队响应左路指令，右侧空隙由防守重新配置产生，不凭空新增漏洞或命令代码','承接队员01完整短令和02转眼接招，展示防守迁移的可见结果，留右侧入口给Elena下一组判断'),
 5:('展示右路诱导造成左路暴露','比分保持1–3、第二节点仍未捕获；蓝色请求沿右侧支路高速前进，在红色规则检查点短暂停顿后进入允许通行的侧支；红防守光标因请求向右汇集，左路未覆盖支路逐渐显出空隙。细长冰青数据线左到右流动、近节点掠过、远节点有视差，方向拖尾随路径弯折，不用爆炸或万能反弹','承接Elena此前短输入，防守被右路牵动使左路暴露；下一镜她停手确认空隙，真实队员不进入数字世界'),
 7:('确认第二节点与二比三结果','比分由1–3开始；承接Elena刚才唯一一次Enter输入，蓝请求从已开放左路进入第二得分节点，规则/状态检查通过后该节点一次变绿，实时比分一次变为2–3。0–3、1–3仅作为小型历史轨迹，不能重复捕获第一节点；不出现第三节点变绿或3–3','Elena按键引出第二节点结果，本镜独立给观众看证据，下一组观众因2–3起立；不把画面投射到队员电脑背壳')
}
def display_shot(n,duration):
 task,content,reaction=screen_info[n]
 p=re.sub(r'duration: [\d.]+s',f'duration: {duration:.1f}s',screen_base,count=1)
 replacements={
  '叙事任务':task,
  '画面':'【透视构图】@比赛积分参考图.png 只借独立公共大屏载体、蓝左红右与比分视觉层级；不照抄参考图4–3终局、兜帽人物、错误队名或后续得分。摄影机→舞台前空的通视区→舞台上方实体LED大屏发光正面→窄边框、支架与环形舞台结构。'+content+'。本镜不出真人或桌上电脑；画外Elena坐B3，Madison左后0.8m、Silas右后1m；Xavier站R1、副队长与01—04坐R2—R6；耳麦与椅位继承，各人物没有搬进大屏。',
  '视觉引导':'上一镜主体的目光或按键接到大屏网络状态，蓝起点左、红目标右保持；注意中心从当前路径收在'+('2–3结果' if n==7 else '未覆盖支路')+'，每条线只沿所写路径运动，屏面边框与光线共面，摄影机实移产生支架视差。',
  '对白反应':reaction+'。无真人、无新口型、无新增台词，屏内状态稳定后不重启。',
  '运动强度':'摄影机中低强度实推；仅屏内数据线高速移动，方向拖尾和节点视差提供速度证据；当前策略或节点状态变化后稳定落幅，不引入本组之外的节点捕获。',
  '负面提示词':'禁止背壳显示图像、透明双面电脑、镜片HUD、屏内容穿墙、悬浮UI、廉价贴图、随机爆炸、额外得分、提前3–3或4–3、重复计第一分、角色进入网络世界、头像克隆、随机字幕、水印、旁白和口型。'
 }
 for key,val in replacements.items():p=re.sub(r'^'+key+r'：[^\n]*',key+'：'+val,p,flags=re.M)
 return p

anchor=(root/'人物行为锚点_用户20261009.md').read_text().split('\n\n')[1]
changed=[3,4,5,7]
for g in groups:
 if g['group'] not in changed:continue
 n=g['group'];screen_index=2 if n==5 else 3 if n in (3,7) else None
 if screen_index:
  g['shots'][screen_index-1]['size']='MS'
  if n==3:g['shots'][0]['size']='MCU' # MCU→ECU→MS
  if n==7:g['shots'][0]['size']='MCU' # MCU→ECU→MS
  if '比赛积分参考图.png' not in g['props']:g['props'].append('比赛积分参考图.png')
 p=b.render(g).replace('，本次不提交视频。','。')
 if g['scene']=='nb':p=p.replace('空间锁：',anchor+'\n空间锁：',1)
 p=p.replace('空间锁：',rules+'\n'+backgrounds[g['scene']]+'\n'+duel+'\n空间锁：',1)
 p=p.replace('屏中影像是屏中不跑到现实前景。','屏内容只在面向人物的发光正面，桌前背壳不显示图像；本镜人物机位不展示UI。')
 p=p.replace('负面提示词：','负面提示词：禁止透明双面电脑、背壳显示代码/比分/网络图、镜片可读HUD、错误屏面朝向、无因反应；')
 if screen_index:
  pattern=rf'【shot {screen_index}.*?(?=\n【shot|\n皮肤专项负面词：)'
  block=display_shot(n,g['shots'][screen_index-1]['duration']).replace('【shot 3','【shot '+str(screen_index),1)
  p=re.sub(pattern,block,p,flags=re.S)
  g['shots'][screen_index-1].update(subject='screen',action=screen_info[n][1],gaze='无真人',face='无真人',reaction=screen_info[n][2],move='公共屏正面实推20cm')
 g['prompt']=p;g['generation_authorized']=True
 (root/f'EP12/G{n:02d}.txt').write_text(p)

ledger=json.loads((root/'英文原台词核对底稿.json').read_text())
assert [l for g in groups for s in g['shots'] for l in s['lines']]==[l for x in ledger['12'] for l in x['lines']]
for g,prev in zip(groups,old):
 assert g['duration']==prev['duration'] and g['cast']==prev['cast']
 assert [s['duration'] for s in g['shots']]==[s['duration'] for s in prev['shots']]
 if g['group'] not in changed:assert g['prompt']==prev['prompt']
 assert '强制要求： 人物皮肤须保持细腻' in g['prompt']
(root/'全部平台填充.json').write_text(json.dumps(allg,ensure_ascii=False,indent=2))
(root/'EP12/EP12_平台填充.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2))
(root/'EP12/EP12_完整FormatC_V2.6.md').write_text('\n\n---\n\n'.join(g['prompt'] for g in groups))
(root/'EP12-25_全部提示词.md').write_text('\n\n---\n\n'.join(g['prompt'] for g in allg))
(root/'EP12/第二轮修订核验_20261009.json').write_text(json.dumps({'modified_groups':changed,'unchanged_groups':[g['group'] for g in groups if g['group'] not in changed],'dialogue_verbatim':True,'groups':14,'shots':42,'duration_s':131,'source':'源文提取第12章257—284行，英文底稿12章','screen_shots':['G03-S03','G05-S02','G07-S03'],'visual_evidence':'G07旧视频首帧有透明背面网络图，当前稿消除此结构','generation_authorized_by':'用户：调整完继续制作12集','new_generation_pending':True},ensure_ascii=False,indent=2))
print('只改G03/04/05/07，14组42镜131秒与英文原文保持。')
