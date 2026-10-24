from pathlib import Path
import re,json,hashlib,html,math
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
SPEC=Path('/Users/zc/.codex/skills/write-format-c-video-prompts/references/format-c-template-v2.6.md').read_text()
QUALITY=re.search(r'写实照片级、超写实质感.*?丁达尔效果（Tyndall Effect）。',SPEC,re.S).group()
SKIN=re.search(r'强制要求： 人物皮肤须保持细腻.*?不允许省略、简写或用"皮肤真实"等笼统表述替代。',SPEC,re.S).group()
TEARS=re.search(r'真实人类眼泪从内眼角缓慢溢出.*?整体情绪克制。',SPEC,re.S).group()
GROUPS=[]
# Each row: focus|task|physical action and stable endpoint|trigger and embodied reaction|English line, if any.
def group(ep,title,scene,cast,props,block,rows,time='夜',notes=''):
    parsed=[]
    for line in rows.strip().splitlines():
        v=line.split('|'); assert len(v) in [4,5],line
        parsed.append(dict(focus=v[0],task=v[1],action=v[2],reaction=v[3],dialogue=v[4] if len(v)>4 else ''))
    GROUPS.append(dict(episode=ep,title=title,scene=scene,cast=cast.split(','),props=props.split(',') if props else [],blocking=block,shots=parsed,time=time,notes=notes))
BED='Blackwood别墅卧室.png'; LIVING='Blackwood别墅客厅.png'; TERRACE='Blackwood别墅顶层露台.png'
CAR='豪车.png'; RING='丝绒礼盒+钻戒.png'; WHEEL='轮椅.png'
ARIA_GALA='Aria深蓝色星空长裙.png'; HADES_SUIT='Hades黑色西装.png'; ARIA_ROBE='Aria象牙白睡袍_EP16-17.png'; ARIA='Aria.png'; HADES='Hades.png'; HEALER='秘术医师.png'; LEO='Leo.png'
CAR_BLOCK='轴线为后排两人连线；摄影机始终在隔板侧拍向后排，Aria画左、Hades画右。两人坐在同一后排坐垫，臀部承重，脚落车内地板；相距0.2米。隔板在镜头后方，车头方向不变。'
BED_BLOCK='房间坐标以卧室主图为准：床位西侧，沙发东侧，窗在北墙、门在南墙。仅借反打图识别南门，不照搬其左右。Aria画左、Hades画右；机位在两人轴线南侧。床边拥抱时两脚落木地板，接近后距离0.15米；不改变房间位置。'
BED_REST='床头为西、床尾为东；两人着完整衣物，背部靠同一床头软枕，Aria画左、Hades画右、间距0.15米。摄影机在床南侧，镜头不绕到北侧；床面承担躯干重量，不出现悬空肢体。'
TERRACE_BLOCK='花拱为左后景、石栏为后景、湖面远景；两人在中央圆形石台同一平面。Aria画左、Hades画右、相距0.8米，摄影机保持两人连线南侧；所有近景保留此左右与眼线。'
WHEEL_BLOCK='卧室西床、东沙发、北窗、南门。Aria坐锁刹轮椅位于画左，面朝画右；双脚落脚踏、臀背受座垫与椅背支撑。医师在画右面向Aria，间距0.9米。摄影机在二人轴线南侧，门位右后方；轮椅不自行移动。'
exec((OUT/'plans.py').read_text())

# Preserve the measured episode audio envelope. Mapping is editorial, not phoneme alignment.
REC={x['episode']:x['seconds'] for x in json.loads((OUT/'recorded_timing.json').read_text())}
for ep in range(15,23):
    gs=[g for g in GROUPS if g['episode']==ep]
    minimum=[]
    for g in gs:
        ds=[]
        for i,sh in enumerate(g['shots']):
            w=len(re.findall(r"[A-Za-z]+(?:[’'][A-Za-z]+)?",sh['dialogue']))
            ds.append(max([3.5,2.0,4.0,2.5,4.5][i%5],math.ceil((w/2.5+0.5)*10)/10 if w else 0))
        minimum.append(sum(ds))
    target=max(math.ceil(REC[ep]),math.ceil(sum(minimum)))
    scale=target/sum(minimum)
    for g,m in zip(gs,minimum):g['target_seconds']=math.ceil(m*scale)

def params(g):
    out=[]
    for i,sh in enumerate(g['shots']):
        focus=sh['focus'];task=sh['task'];act=sh['action']
        if any(w in task for w in ['跪','起身','步','走','逃离','退出','重心','牵手','支撑','相拥','拥抱']):
            p=('全景FS',28,'斜侧平视','固定',1.2,75) if i%2==0 else ('中全景MLS',35,'四分之三侧微俯','轻微下摇跟随主体高度',1.35,68)
        elif focus in ['礼盒与钻戒','卧室门'] or any(w in task for w in ['戒圈','佩戴','取出戒指','打开礼盒','揭示唯一','检查已签署','捧脸']):
            p=('动作特写CU',85,'侧前方微俯','固定',1.1,75)
        elif sh['dialogue'] and i==0 and len(g['cast'])>1:
            p=('越肩中近景OTS-MCU',65,'同轴南侧过肩平视','固定',1.35,52)
        elif '与' in focus:p=('双人中景MS',35,'双侧平视','固定',1.3,55)
        else:p=PARAMS[i%5]
        if out and p[0]==out[-1][0]:
            p=('中近景MCU',50,'四分之三侧平视','固定',1.4,52) if '特写' in p[0] else ('中景MS',35,'斜侧微俯','固定',1.35,45)
        out.append(p)
    return out

def refs(g):return list(dict.fromkeys(g['cast']+([g['scene']] if g['scene'] else [])+g['props']))

def light(g):
    if g['scene']==CAR:
        return '参考《夜行动物》的车窗冷暖分层。主光为车顶前左侧高于眼线0.35米的暖白漫射灯，3800K，经白色内饰反射；车窗外5600K路灯仅作移动边缘光，基准面光保持稳定。脸左侧亮、右侧柔暗，面光比1:1.5，背景低1档；影落右后侧坐垫，皮革局部柔反射、胡桃木高光不过曝。人物脸部明亮、五官清晰可辨。'
    if g['scene']==TERRACE:
        return '参考《时空恋旅人》的夜间暖色人像。左前上方高于头部0.6米的露台暖白柔光为4000K主光，右后蓝色魔晶6500K仅作轮廓，烛灯2800K作低位点光。面光比1:1.5，脸左亮右柔暗；影落右后石台，白花与石面反射柔光，金属与钻石仅局部高光，背景低1档。人物脸部明亮、五官清晰可辨。'
    day=g['time']!='夜'
    return ('参考《傲慢与偏见》的窗侧柔光层次。北窗'+('5600K日光经薄帘漫射' if day else '6500K冷月色作弱轮廓')+'；主光为画左前45度、高于眼线0.5米的'+('窗侧反射日光5000K' if day else '床头/室内灯经浅色墙反射的3800K暖白柔光')+'。面光比1:1.5，人物左颊亮、右颊保留纹理；影落右后木地板或坐垫，金属仅细线反光，布料哑光褶皱、石墙漫反射，背景低1档。人物脸部明亮、五官清晰可辨。')

NEG='禁止换脸、服装互换、左右互换、跳轴、焦点导致换位、手指穿模、肢体悬空、道具复制；禁止粗糙颗粒皮肤、蜡感、塑料感、浮油、过度磨皮、皮肤色块与融合接缝；禁止眼球自发光、直视镜头、与观众对视、打破第四面墙、瞳孔锁定镜头、对镜头摆拍；禁止字幕、水印、旁白、音乐、非说话者口型。'
PARAMS=[('中景MS',35,'四分之三侧平视','固定',1.35,40),('特写CU',85,'正面偏轴20度微俯','缓推0.1米',1.5,70),('中近景MCU',50,'侧面平视','固定',1.4,52),('大特写ECU',100,'三分之二侧微俯','固定',1.45,85),('中全景MLS',35,'斜侧微仰','横移0.15米',1.25,70)]
assets={}; result=[]
for g in GROUPS:
    ep=g['episode']; idx=sum(x['episode']==ep for x in result)+1
    gid=f'EP{ep}-G{idx:02d}'; g['id']=gid
    shots=g['shots']; count=len(shots); shotparams=params(g)
    durations=[]
    for i,s in enumerate(shots):
        words=len(re.findall(r"[A-Za-z]+(?:[’'][A-Za-z]+)?",s['dialogue']))
        d=max([3.5,2.0,4.0,2.5,4.5][i%5],math.ceil((words/2.5+0.5)*10)/10 if words else 0)
        durations.append(d)
    # User source dialogue and recorded narration determine output; length overrides default caps where necessary.
    target=g['target_seconds']
    extra=round(target-sum(durations),1)
    # Extend meaningful action and reaction beats, with the last beat carrying the largest share.
    weights=[1.0 if sh['dialogue'] else (2.0 if j==count-1 else 1.5) for j,sh in enumerate(shots)]
    den=sum(weights)
    additions=[round(extra*w/den,1) for w in weights]
    additions[-1]=round(extra-sum(additions[:-1]),1)
    durations=[round(d+a,1) for d,a in zip(durations,additions)]
    total=round(sum(durations),1); g['duration']=total
    if total>30: raise ValueError((gid,total,'exceeds observed platform max'))
    intro=f'【{gid}｜{g["title"]}】\n【组头｜固定画质词与光影基调】\n固定画质词（Fixed Quality Descriptor）：{QUALITY}\n{SKIN}\n'
    intro+='本项目镜头参数覆盖：保留ARRI Alexa 65质感、竖版9:16、180度快门；上文85mm为人像基线，实际各镜采用下列全画幅等效焦段及T2.8，双人共焦镜T4；不得把多焦段误解为画内变焦。\n'
    intro+=f'光影基调（Lighting Tone）：{light(g)}\n'
    intro+=f'节奏结构（Beat Structure）：组型：'+('对白组' if any(s['dialogue'] for s in shots) else '情绪/动作组')+f'｜{count}镜｜共{total:.1f}s。时长'+ '/'.join(f'{x:.1f}' for x in durations)+'秒；铺垫→触发→承受→终态，最强情绪落在末镜，组尾以末镜所述新状态承接后续。按本地录音总时长分配画面承载，长对白按原文自然语速预留；本项目单镜可为完整长句超过6秒，组时长不超过平台30秒。精确音画对齐在剪辑阶段处理，禁止凭此声称已逐句同步。\n'
    intro+='景别循环（Shot Size Cycle）：'+'→'.join(shotparams[i][0]+' '+shotparams[i][2] for i in range(count))+'。\n'
    intro+=f'视觉动线（Visual Flow）：{g["blocking"]} 人物占主要视觉信息约80%，背景20%；道具单独特写按画面所述保留手部归属。\n'
    
    if ep>=21 or (ep==20 and g['scene']==BED):g['notes']+='戒指卡只提取戒指，佩戴于Aria左无名指；本组禁止出现礼盒。'
    if g['scene']==BED:g['notes']+='当前时间线不复活完整恒温箱；构图取床侧或南门区域，遮出主图中央旧箱区域。'
    intro+='引用锁：'+ '、'.join('@'+x for x in refs(g))+'。角色参考只提取对应单人身份与服饰，禁止把卡片文字、分格和多视图复制进视频。'+g['notes']+'\n'
    text= intro
    for i,s in enumerate(shots):
        size,focal,angle,movement,height,occupancy=shotparams[i]
        focus=s['focus']; dia=s['dialogue']; names=[x for x in ['Aria','Hades','Leo','秘术医师','落魄Mia','落魄Foster先生','落魄Foster夫人'] if any(x in c for c in g['cast'])]
        gaze=[]
        for name in names:
            if name=='Aria': target='画右Hades面部' if 'Hades' in names else ('画右Leo递来的文件' if 'Leo' in names else ('画右秘术医师面部' if '秘术医师' in names else '画外电视或手中手机'))
            elif name=='Hades':target='画右中景秘术医师面部' if (g['title']=='让医师离开' and i<3) or (g['title']=='卧室门被力量撞开' and i==3) else '画左Aria面部'
            elif name in ['Leo','秘术医师']:target=('右后卧室出口' if g['title']=='让医师离开' and i in [1,2] else '画左Aria手部，再短暂抬至她面部')
            else:target='自己手中或面前的物体'
            gaze.append(name+'在可见时看'+target)
        audio=(f'{focus}英文原台词：“{dia}”；仅{focus}生成说话口型，其余可见人物闭口。' if dia else '无台词；所有人闭口，禁止生成口型。')+'无旁白、无音乐、无生理音效。仅保留与本镜可见动作对应的轻微衣料/接触环境声。'
        text+=f'\n【shot {i+1}｜{focus}｜{size}｜{angle}｜{movement}｜{focal}mm｜duration: {durations[i]:.1f}s】\n'
        text+=f'叙事任务（Narrative Task）：{s["task"]}'+('；情绪/行动钩子' if i==count-1 else '')+'。\n'
        fg=(('前景'+('Hades' if focus=='Aria' and 'Hades' in names else ('Leo' if focus=='Aria' and 'Leo' in names else ('秘术医师' if focus=='Aria' else 'Aria')))+'近镜头侧肩背占'+('画右' if focus=='Aria' else '画左')+'20%宽度，虚焦；') if 'OTS' in size else '无前景肩膀遮挡；')
        text+=f'镜头：{focal}mm等效，{movement}，T'+('4' if i%5 in [0,4] else '2.8')+f'，常规坐姿机位高{height}米；站姿改至主体眼高减0.1米、跪姿改为0.9米，按{angle}；同一轴线南侧。{focus}为焦点，主体可见部分占画高{occupancy}%，头部留白'+('3%' if i%5==3 else '8%')+'；'+fg+'其他人物仅留画缘虚焦轮廓，背景中度虚化；禁止无因拉焦。\n'
        text+=f'画面：{s["action"]}\n'
        text+='视觉引导（Visual Flow）：主体重心沿画面上1/3的既定左右位置承接；'+ '；'.join(gaze)+'。具体动作涉及戒指、文件或门时，眼线先沿画面动作落到该具名目标，再回到上述对手；只让画面明确出镜的人出现，引用卡不增加可见人数。视线偏离镜头光轴15–25度。仅放大本镜任务对应部位，压暗背景装饰。\n'
        text+=f'微表演（Micro-Performance）：{s["reaction"]} 可见人物按本镜反应错开眨眼时机；不得因通用反应规则添加未出镜人物。\n'
        text+=f'对白反应（Dialogue Reaction）：{s["reaction"]} '+(f'{focus}察觉对方反应后停半拍再继续原句；听者闭口，眼线保持对手方向。' if dia else '所有在场者沉默；手部或肩颈的收紧/松开应由本镜事件触发，终态保持画面所述姿势。')+'\n'
        text+='人物背景融合（Subject-Background Integration）：保持本组支撑面与接触链；臀背/脚掌/膝部按画面状态接触坐垫、地板或脚踏，受压面产生衣料压痕与连续接触阴影；身体、道具和背景共享同一光源，玻璃/金属只反射环境；人物焦平面真实，无贴片边缘。\n'
        text+='光影细节（Lighting Detail）：机位靠近后保留同侧面部高光，眼眸仅反射既有光源；手部和衣料随动作改变反光面积，不改变主光方向。\n'
        if '眼泪' in s['action'] or '流泪' in s['action']:
            text+=TEARS+' 泪水不得自发光、漂浮或对称；仅哭泣角色应用此段，其他人不自动流泪。\n'
        text+=f'音频（Audio）：{audio}\n'
        text+='运动强度（Motion Intensity）：'+('中高，主体动作同向跟随，前景衣角沿运动方向短暂掠过，背景轻微方向性模糊；碰撞后立刻给受力结果。' if any(k in s['action'] for k in ['撞开','冲开','猛地','失衡']) else '低至中；前半拍准备，动作主体平稳完成，末拍保留结果，禁止机械重复；发生连续动作时在70%处切出，下镜接剩余30%。')+'\n'
        text+='负面提示词（Negative Prompt）：'+NEG+'\n'
    g['prompt']=text;g['refs']=refs(g);g['shot_durations']=durations
    (OUT/'prompts'/f'{gid}.txt').write_text(text)
    result.append(g)
(OUT/'storyboard.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(OUT/'format_c_prompts.md').write_text('\n\n'.join(g['prompt'] for g in result))
report={'groups':len(result),'shots':sum(len(g['shots']) for g in result),'duration':round(sum(g['duration'] for g in result),1),'max_chars':max(len(g['prompt']) for g in result),'platform_written':False,'generation_submitted':False,'warnings':['原始全剧分镜表标称镜数与实际行数不一致，以实际动作与英文原文为准。','每镜参数覆盖固定块85mm基线。','EP22使用卧室，纠正原文件夹客厅图。','卧室图含早期恒温箱：当前时间线不复制已破碎的恒温箱。','EP17非露骨改编。','已核验九梦2.5Pro支持4至30秒；本次采用整数秒分组。录音只做集级承载时长核验，尚未完成逐句声画对齐。']}
(OUT/'qa_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
review=['<!doctype html><meta charset="utf-8"><title>EP15–22 Format C 2.6 审阅与投递</title><style>body{font:16px system-ui;max-width:1100px;margin:auto;background:#faf7f2;color:#222}textarea{width:100%;height:320px}section{margin:32px 0;padding:20px;background:white}pre{white-space:pre-wrap}</style><h1>《玻璃箱里的神明》15–22集</h1><p>Format C 2.6 分组稿；未提交生成。每组在下方展示引用与全文。</p>']
for g in result:
 review.append(f'<section id="{g["id"]}"><h2>{g["id"]} {html.escape(g["title"])}</h2><p class="refs">{html.escape(json.dumps(g["refs"],ensure_ascii=False))}</p><p class="duration">{g["duration"]}</p><textarea readonly aria-label="{g["id"]}">{html.escape(g["prompt"])}</textarea></section>')
(OUT/'review.html').write_text('\n'.join(review))
print(json.dumps(report,ensure_ascii=False,indent=2))
