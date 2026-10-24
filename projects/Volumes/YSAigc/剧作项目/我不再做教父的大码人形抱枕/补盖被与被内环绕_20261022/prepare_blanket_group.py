from pathlib import Path
import json
import re

OUT=Path(__file__).resolve().parent
BASE=OUT.parent/'复刻全集_FormatC_V25_20261022'
D=json.loads((BASE/'复刻全集_FormatC_V25_全部提示词.json').read_text())
source=Path('/Users/zc/.codex/skills/short-drama-prompts-v3/references/format-c-v2.5-source.md').read_text()
quality=next(x for x in source.splitlines() if x.startswith('写实照片级、'))
skin=next(x for x in source.splitlines() if x.startswith('强制要求： 人物皮肤须'))
lighting=next(x for x in D['groups'][6]['prompt'].splitlines() if x.startswith('光影基调（Lighting Tone）：'))
negative='换脸、融脸、比例失衡、漂浮、穿模、断手、多手、重复肢体、被子凭空出现或消失、被子穿过手臂、透明被子、透视被内手部、换枕换位、床头反转、穿墙机位、越轴、同向背抱、翻压、亲吻、意外说话口型、字幕、水印、BGM、眼球自发光；直视镜头（Looking at Camera / Looking into Lens）、与观众对视（Eye Contact with Viewer）、打破第四面墙（Breaking the Fourth Wall）、瞳孔锁定镜头（Pupils Locked on Lens）、望向镜头发呆（Blank Stare at Camera）、对镜头摆拍（Posing for Camera）、正视镜头说话（Talking to Camera）；女主Eliza微笑、女主Eliza嘴角上扬、女主Eliza露齿笑、女主Eliza甜笑。'
skin_negative='皮肤蜡感、塑料感、过度磨皮、毛孔消失、纹理丢失、大面积油光、浮油、高光过曝、脸部油亮色块、色调不均、多图融合色差、皮肤接缝、五官融合模糊、假面、发灰、死白。'
prompt=f'''第2集 EP02
EP02-S06B｜拉被圈抱——被内相拥
@场景1：Eliza公寓卧室（§ASSET:Eliza旧卧室§）；@人物1：大码Eliza（§ASSET:大码女主_Eliza_睡衣§）；@人物2：Matteo Bellandi（§ASSET:Matteo_成年_睡衣§）。
人物、空间和床上被子均取指定资产；Eliza保持28岁大码成年身份，Matteo保持成年。外观、服装与妆造只参考资产，不另写款色材质，衣物保持扣合与遮盖。女主嘴角自然平直、不微笑，心动只表现为手指与肩颈的细微紧张；不新增亲吻。画幅9:16。参考帧只取盖被动作和拥抱关系，不复制字幕或水印。
起始状态：两人已在原枕面对面侧卧，头同朝床头；男主床左里侧左侧承重，女主床右通道近侧右侧承重。男主下侧左前臂由床面承托、左掌从枕外托女主上背，上侧右臂原在腰外；女主左手在两人胸前，右手留自己枕旁。两人刚合眼安顿，尚未真正睡熟。现有被子的上沿在腰腿处、可由上侧右手取到，不从两人身下抽被，不凭空新增被子。房间床左贴墙，仅床右通道及床尾半区上空允许摄影。
【组头｜固定画质词与光影基调】
固定画质词（Fixed Quality Descriptor）：{quality}
{skin}
项目摄影覆盖：本组焦段按各shot所列85mm／35mm／50mm执行，覆盖固定词中的85mm缺省，其余固定词不变。正常速率拍摄；盖被动作连续，环绕依实际床尾可用空间执行。
{lighting}
节奏结构（Beat Structure）：组型：动作与情绪组｜3镜｜共12.0s；2.0 / 4.0 / 6.0秒。抓被起势→拉被落稳→被内圈抱环绕停留；动作最强拍在shot 2，情绪余韵与钩子落shot 3。保留无对白动作段，不新增旁白或说话口型。
景别循环（Shot Size Cycle）：CU 床尾右通道斜俯右手抓被 → MS 床尾右侧高斜双人盖被关系 → MCU 床尾同侧高斜双人环绕。
视觉动线（Visual Flow）：从腰腿处右手抓被沿上行，落到两人胸口下的被沿，再回到露在被沿上方的两张侧脸；床左男主、床右女主和原枕头向不互换，关系轴线始终从床尾侧观察。

【shot 1｜上侧右手抓住现有被沿｜景别（Shot Size）：CU｜视角（Angle）：床尾右通道斜俯手部｜运镜（Camera Movement）：手部短轨缓推｜焦段（Focal Length）：85mm｜duration: 2.0s】
叙事任务（Narrative Task）：上侧右手抓住现有被沿
镜头：从床尾右通道斜俯男主右手与腰腿处现有被沿，机身沿接点方向短轨缓推6厘米；焦点锁手指收拢和被沿的接触，切出时牵起刚启动。摄影机不跨到床头半区，原枕与两人头部在画外，不为手部镜改变床位。
画面：位置锁定：Matteo床左里侧左侧卧，Eliza床右近侧右侧卧，头同朝床头、腿向床尾、各在原枕承托区。男主下侧左前臂与左掌保持托背，上侧右臂暂松腰侧，右手向下取腰腿处现有被子上沿，拇指与其余四指合拢抓稳，沿床面向胸前拉起一点。女主左手仍在两人胸前、右手在自己枕旁；镜头只拍男主右手，不要求看见画外面部。
视觉引导（Visual Flow）：画面中下部的男主右手从腰侧移到被沿，抓点成为唯一重心；两人眼睛在画外，男主注意力转到这处被沿，女主仍合眼面向他，不注视摄影机。
微表演（Micro-Performance）：男主右手指腹先压住被沿再收指，手背只有短暂用力；女主画外保持原安顿状态，不因接近摄影机新增反应。
对白反应（Dialogue Reaction）：右臂离开腰侧时下侧左掌仍托住她上背，女主身体没有退开；抓稳后才启动拉被，不让手指穿透被面。
人物背景融合（Subject-Background Integration）：右手、被沿和床面保持真实遮挡与接触阴影；同一被子从腰腿处连续牵起，床面不扩大，被子不从躯干下方抽出。
光影细节（Lighting Detail）：右手与被沿的局部接触影随抓握收紧，背景仅保留原床面虚化，不改变台灯方向。
音频（Audio）：一次抓住被沿的轻微摩擦、自然呼吸和公寓深夜低底声；无对白、旁白、配乐或新增人声。
运动强度（Motion Intensity）：一次明确抓握，随后刚启动牵引；男主头肩不离原枕，不坐起、不猛扯女主。
负面提示词（Negative Prompt）：{negative}{skin_negative}

【shot 2｜被子拉起落到两人胸下｜景别（Shot Size）：MS｜视角（Angle）：床尾右侧高斜双人｜运镜（Camera Movement）：缓推配合小幅升高｜焦段（Focal Length）：35mm｜duration: 4.0s】
叙事任务（Narrative Task）：被子拉起落到两人胸下
镜头：床尾右侧高斜双人中景起幅，机身沿原斜俯方向缓推15厘米并升高10厘米，完整保留男主右手、被子展开路线与两人的头肩落点；被沿短暂掠过下前景后落稳，终点仍在关系轴线床尾同侧，不用遮挡切镜跳过盖被过程。
画面：位置锁定：Matteo仍床左里侧左侧卧、画面左后，Eliza仍床右近侧右侧卧、画面右前；头各落原枕，面对面、同一床头方向。男主左掌持续从枕外托住女主上背，左肘前臂由床垫承托；上侧右手承接抓稳的被沿，沿床面朝床头方向牵起并略向上扬，使现有被子在两人上方拱起一次，随即控制被沿落到两人胸口下，腰腿共同盖住。前胸被沿始终低于下巴，最终停在女主胸前左手下方，背侧被面自然覆盖左掌托背的接点，头颈、两张脸和枕旁右手保持露出。男主松开被沿，右臂开始回到被外腰侧；女主没有替他盖被或回抱，也不换枕。
视觉引导（Visual Flow）：被沿从画面中下部上行，带观众视线回到上三分之一的两张侧脸；男主短暂半睁眼看右手与被沿落点，女主仍合眼朝向男主，二人均不看镜头。
微表演（Micro-Performance）：女主肩线在被沿落下时轻轻收住，左手指尖在两人胸前微蜷后停住，嘴角保持平直，没有笑意；男主确认被沿落稳后眉间与下颌松下，手臂不突然加力。
对白反应（Dialogue Reaction）：被子落到胸下后女主原有的微紧张逐渐缓和，没有迎吻或主动抱紧；男主保持原躺姿，右臂归位时左掌始终承托她上背。
人物背景融合（Subject-Background Integration）：同一被子受右手牵引形成一次拱起和重力回落，覆盖双腿与躯干，头颈、女主胸前左手与枕旁右手、男主上侧右手露在被沿外，下侧左掌留在被下；被面真实遮住被下身体，不透明、不穿臂，不把两人卷成一团。
光影细节（Lighting Detail）：被面拱起时仅遮去部分床面反射，面部仍由原台灯明确照亮；被沿回落后两人脸部与枕面曝光恢复连续。
音频（Audio）：一次拉被、被面展开和落稳的细响，呼吸与深夜房间低底声；无人说话，无旁白或音乐。
运动强度（Motion Intensity）：单次连贯拉起、拱起、落稳；有可读的被面惯性，力度收在男主右手，不重复扬被，也不因盖被坐起。
负面提示词（Negative Prompt）：{negative}

【shot 3｜情绪型钩子：被内相拥环绕｜景别（Shot Size）：MCU｜视角（Angle）：床尾同侧高斜双人｜运镜（Camera Movement）：床尾同轴环绕25度｜焦段（Focal Length）：50mm｜duration: 6.0s】
叙事任务（Narrative Task）：情绪型钩子：被内相拥环绕
镜头：吊臂由床右通道支撑，起点在床尾偏右的高斜双人中近景；以两人原枕上的头肩为环绕中心，沿床尾可用扇区向床尾正中方向缓慢环绕约25度，弧长约45厘米，终点仍略偏右且停在关系轴线床尾侧。被沿在下前景形成连续视差，两张侧脸、被外右臂和被沿上方女主左手始终可辨；机位高度与俯角只作小幅补偿，不下钻被子、不去床头、不绕入床左贴墙侧。焦点留在两人露出的眼睑与侧脸，摄影机真实位移，不以转动演员或变焦假造环绕。
画面：位置锁定：Matteo固定床左里侧左侧承重、画面左后，Eliza固定床右近侧右侧承重、画面右前，头同朝床头、各在原枕；两人面对面。被沿停在双方胸口下，腰腿在同一被子里，女主左手在两人胸前被沿上方、右手在自己枕旁。男主上侧右臂回到被外，隔被稳稳环在女主腰侧；下侧左前臂仍受床面承托、左掌在被下托她上背，不要求透视看见被下手指。两人只是安顿已有圈抱，不再次拉人，不改变彼此距离；男主重新合眼，女主原本合着的眼睛不重复睁开。镜尾稳定为原床位、同被、面对面闭眼圈抱，接嗅发段。
视觉引导（Visual Flow）：被沿前景的轻微视差引向画面上三分之一的两张近侧脸；环绕中保持男主左后、女主右前，不出现左右翻转。两人眼睑合着，面朝彼此；无对镜头的眼球追视。
微表演（Micro-Performance）：Eliza嘴角自然平直、没有上扬，左手指尖的微蜷慢慢松开，肩颈仍留一点未尽的心动紧张，再随困意安顿；Matteo眉间放松，闭眼保持近距离而不追吻。两人的脸和身体都有轻微自然起伏，不作甜笑或摆拍。
对白反应（Dialogue Reaction）：右臂归到腰侧后她没有回抱，只顺着枕面与床垫留在怀里；男主双臂稳定，女主闭眼与微紧张的状态直接交给下一组，不新增对白反应动作。
人物背景融合（Subject-Background Integration）：环绕时台灯、原枕与被沿按真实深度产生视差，人物、床头、贴墙侧和桌柜不换位。腰腿被同一被面遮住，右掌在被外可见，左掌在被下由已知接触和被面受力交代，不画成透明被子。
光影细节（Lighting Detail）：绕行仅改变原台灯光在近侧脸与被沿上的可见角度，光源和色温不旋转；两人面部始终明亮、五官清晰可辨，暗侧保留皮肤纹理。
音频（Audio）：极轻的被面与枕面摩擦、两人逐渐平稳的自然呼吸、公寓深夜低底声；无对白、旁白、配乐、心跳音效或意外口型。
运动强度（Motion Intensity）：人物动作低幅稳定，运镜用完整6秒完成一次25度同轴环绕；不围床360度，不翻身压抱，不把女主转成背向男主，也不以摇晃镜头代替环绕。
负面提示词（Negative Prompt）：{negative}
'''
fields=['叙事任务（Narrative Task）','镜头','画面','视觉引导（Visual Flow）','微表演（Micro-Performance）','对白反应（Dialogue Reaction）','人物背景融合（Subject-Background Integration）','光影细节（Lighting Detail）','音频（Audio）','运动强度（Motion Intensity）','负面提示词（Negative Prompt）']
blocks=re.split(r'【shot\s+\d+[^】]*】',prompt)[1:]
assert len(blocks)==3
assert sum(map(float,re.findall(r'duration: ([\d.]+)s',prompt)))==12
assert prompt.count(quality)==prompt.count(skin)==1
for block in blocks:
    for f in fields:assert len(re.findall('^'+re.escape(f)+'：',block,re.M))==1,f
assert len(prompt)<15000
group={'index':'06B','episode':2,'title':'EP02-S06B｜拉被圈抱——被内相拥','duration':12,'prompt':prompt,'dialogue_lines':[],'shots':[{'n':1,'duration':2.0,'size':'CU','angle':'床尾右通道斜俯手部','camera_movement':'手部短轨缓推'},{'n':2,'duration':4.0,'size':'MS','angle':'床尾右侧高斜双人','camera_movement':'缓推配合小幅升高'},{'n':3,'duration':6.0,'size':'MCU','angle':'床尾同侧高斜双人','camera_movement':'床尾同轴环绕25度'}],'is_supplement':True,'insertion_after_original_position':6,'timeline_position':7,'native_asset_status':'pending_platform_bind','revision':'format-c-v2.5_blanket_orbit_supplement','source_paragraphs':['用户补充盖被与被内拥抱环绕要求','EP02对标本地28–30秒帧盖被、34–35秒拥抱关系；文本母版未载此动作'],'reference_frames':['frame_28s.jpg','frame_29s.jpg','frame_30s.jpg','frame_34s.jpg','frame_35s.jpg'],'audio_timing_basis':'无对白，动作计划12秒；未提交生成'}
(OUT/'新增盖被环绕组_提示词.md').write_text(prompt)
(OUT/'新增盖被环绕组_待绑定.json').write_text(json.dumps(group,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'shots':3,'seconds':12,'chars':len(prompt),'insert_after':6,'assets':3},ensure_ascii=False))
