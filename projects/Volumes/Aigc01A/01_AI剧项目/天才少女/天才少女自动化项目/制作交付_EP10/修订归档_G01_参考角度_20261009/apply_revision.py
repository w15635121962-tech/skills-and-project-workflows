from pathlib import Path
import json
root=Path(__file__).resolve().parent.parent
old=(Path(__file__).resolve().parent/'EP10_G01_修订前.txt').read_text()
head=old.split('【shot 3｜',1)[0]
fields={
'叙事任务':'Elena接管自己的终端，蓄势开口。',
'镜头':'机位B3桌右前通道，与Elena脸朝向约25度水平夹角，仍在蓝红席连线看台侧半空间；镜高1.30m、略高坐姿眼睛5cm、轻俯约3度，略偏正面三分之四。移手落键触发沿光轴缓推8cm约3cm/s，眼落本人屏即停，不环绕越轴穿桌。85mm定焦T1.8，焦点锁双眼；完整发顶至上胸，头高约45%、顶部留白5%，设计值。',
'画面':'@Elena.png Elena仍坐B3，黑衣透明眼镜、新版身份，身体朝本人终端；脸略朝画左，双眼鼻嘴完整。双手从桌沿落键、指腹按键打开比赛界面，手在下缘画外、肩臂前送可见；眼由公共屏降本人屏，唇闭，终态手留键区。透视构图描述：脸中心画宽50%，无前景人头，胸上清楚。@Madison的Northbridge比赛服.png Madison仍椅后左0.8m，@Silas的Northbridge战队比赛服.png Silas仍椅后右1m，相距约1.2m同平台；右前方取景仍分别在后方画左、画右，紧裁切只留虚焦蓝白肩胸局部，脸由上/侧缘自然裁出，尺度小于女主、不遮她、不复制肩。微推改裁切、二人原位。蓝LED墙低亮虚焦，电脑背壳下缘画外；耳麦仍桌右，Elena未佩戴。',
'视觉引导':'接Silas目光切，上中双眼为中心；女主瞳孔落画外左前下方本人B3屏，不看光轴。Madison仍看公共认证屏、Silas仍看Elena，闭口不抢焦；落幅保留两处后方蓝白肩胸和背景视差，无眼镜HUD。',
'微表演':'Elena唇闭、眼睑随眼线轻落，肩随落键前送后放松；2.5秒0—1次自然眨眼，无摆拍笑容。Madison抓衣摆未松，Silas肩仍僵，反应不同步。',
'对白反应':'认证后身后二人的停顿触发Elena转回操作；颈肩松、闭口，终态眼在屏、手在键区，接下一组抬眼宣告。三人不发言、不提前戴耳麦或起身。',
'人物背景融合':'臀压B3椅面、脚在平台，本人手落本人键盘；桌沿/背壳方向正确。后方二人同平台、原纵深、接触影连续；耳麦桌右不移动。',
'光影细节':'主光仍6500K桌前上方45度柔白，右前机位只改变亮暗投影；近颊亮、远颊保留，眼镜窄反光不盖眼；蓝光只勾发缘，微推无曝光跳变。',
'音频':'无对白、无旁白、无额外口型；只可有低电器环境底声，无音乐、无生理音效。',
'运动强度':'人物移手落键、眼线下降、肩臂低幅前送；相机单向8cm微推。无变焦、快速环绕、随机转头站起。',
'负面提示词':'换脸分身、旧版女主、服装互换、90度侧脸、遮远眼裁嘴贴边、直视镜头、与观众对视、瞳孔锁光轴、打破第四面墙、摆拍发呆、提前戴耳麦、颈挂耳机、人物消失、瞬移跳轴、背景大头复制肩、穿模漂浮多手、背壳显示内容、双面屏眼镜HUD、眼球发光、错口型额外台词、字幕水印音乐、蜡塑皮肤磨皮油光、纹理丢失肤色拼接、五官糊化皮肤灰白。'
}
newshot='【shot 3｜Elena｜景别：MCU｜视角：略偏正面三分之四/微俯｜运镜：落键触发微推｜焦段：85mm｜duration: 2.5s】\n'+'\n'.join(k+'：'+v for k,v in fields.items())
new=(head+newshot).replace('景别循环：MCU → CU → MCU；相邻机位按主体目光或说话权更换，反打改变镜高/裁切。','景别循环：Madison MCU近正面 → Silas CU近正面 → Elena胸上紧MCU略偏正面三分之四微俯；以人物眼线匹配切换。')
assert len(new)<=5000,len(new)
assert new.split('【shot 1｜')[1].split('【shot 3｜')[0]==old.split('【shot 1｜')[1].split('【shot 3｜')[0]
for k in fields:assert newshot.count('\n'+k+'：')==1,k
(root/'EP10_G01_参考角度修订.txt').write_text(new)
(root/'EP10_G01.txt').write_text(new)
data=json.loads((root/'EP10_平台填充.json').read_text());data[0]['prompt']=new
data[0]['revision']='20261009用户参考图：G01女主角度及邻接构图；其余镜头/时长/台词/站位/光色冻结'
data[0]['shots'][2].update(cam=fields['镜头'],view=fields['画面'].split('透视构图描述：')[1],gaze='画外左前下方本人B3屏')
(root/'EP10_平台填充.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
(root/'第10集完整提示词.md').write_text('# 第10集完整提示词\n\n'+'\n\n---\n\n'.join(g['prompt'] for g in data))
build=root/'build_ep10.py';b=build.read_text();b=b.replace(' return text\n\nif __name__'," override=ROOT/'EP10_G01_参考角度修订.txt'\n if n==1 and override.exists():return override.read_text()\n return text\n\nif __name__");build.write_text(b)
(Path(__file__).resolve().parent/'修订核验.md').write_text('EP10-G01 shot3及组头景别序列。源第10章：认证后移手到键盘打开比赛界面；G02起态手在键区。女主新版SHA256 2d0aab51f63c407e183ad9d4a6a6add942218c1d3821898bef4cb2b7894d7a99。参考图只取略偏正面三分之四视角、清楚双眼、紧近景；不提前第11组戴耳麦。3镜3/2.5/2.5秒共8秒无对白不变；第一二镜逐字冻结；后续已提交组不重做。平台回读及提交见补做记录。')
with (root.parent/'后续制作固定要求.md').open('a') as f:f.write('\n\n2026-10-09新增：Elena优先使用用户参考图的略偏正面三分之四角度、平视至轻微俯视、居中紧近景；双眼鼻嘴清楚，视线落戏内侧前目标，镜头有动机小幅运动。只继承机位构图，不复制与当前剧情不符的耳麦状态。对白期间优先完整正脸居中；保持道具站位轴线。第一组本次授权重新生成，其余已提交组保持。\n')
print(json.dumps({'chars':len(new),'shots':3,'duration':8,'frozen_shots':[1,2],'changed_shot':3},ensure_ascii=False))
