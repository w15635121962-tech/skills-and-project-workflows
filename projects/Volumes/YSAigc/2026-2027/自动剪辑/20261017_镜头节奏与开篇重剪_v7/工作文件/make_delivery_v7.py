import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精剪预览'
plan=json.loads((OUT/'edit_plan_v7.json').read_text());qa=json.loads((OUT/'native_verification_v7.json').read_text());delivery=json.loads((OUT/'final_delivery_v7.json').read_text());rev=plan['revision_v7'];before=rev['before'];after=rev['after']
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',23)
head=ImageFont.truetype('/System/Library/Fonts/Supplemental/Songti.ttc',43)
small=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',20)
W=1680;tilew=540;tileh=304;gap=15;top=112;rowh=350
sheet=Image.new('RGB',(W,top+rowh*4+15),(244,242,235));d=ImageDraw.Draw(sheet)
d.text((18,15),'汇启新章 · 共育未来',font=head,fill=(42,44,37))
d.text((20,73),'人文开篇重选  ·  前26.68秒 / 12镜  ·  v7',font=small,fill=(83,83,71))
d.line((20,102,W-20,102),fill=(171,151,106),width=1)
labels=['红柱长廊','笔尖与书页','入校问候','迎着晨光入校','师生共读','书架前阅读','文汇校名','教学楼与阳光','光影里的校园','同伴互动','专注的目光','自然笑容']
by={x['start']:x for x in qa['main_frames']}
for i,s in enumerate(plan['shots'][:12]):
    assert s['record_frame']<667
    im=Image.open(by[s['record_frame']]['path']).convert('RGB');im=im.resize((tilew,tileh),Image.Resampling.LANCZOS)
    x=15+(i%3)*(tilew+gap);y=top+(i//3)*rowh;sheet.paste(im,(x,y))
    sec=s['record_frame']/25;mm=int(sec)//60;ss=sec-mm*60
    d.text((x+2,y+tileh+7),f'{mm:02d}:{ss:05.2f}  {s["length_frames"]/25:.2f}秒  {labels[i]}',font=font,fill=(42,44,37))
preview=PRE/'开篇重剪_12镜实际画面预览.jpg';sheet.save(preview,quality=95)

text=f'''文汇中学教育集团宣传片｜镜头节奏与开篇重剪 v7

已在达芬奇工程“学校”中完成“{plan['name']}”。总长保持7分40秒7帧（25fps，460.28秒），完整旁白、教师口号、群体口号、校长原声和现有配乐全部保留。

本轮主画面从{before['total_v1_items']}镜增至{after['total_v1_items']}镜，净增{after['total_v1_items']-before['total_v1_items']}镜。解说段镜头平均时长由{before['mean_narration_shot_seconds']:.2f}秒降到{after['mean_narration_shot_seconds']:.2f}秒，中位时长由{before['median_narration_shot_seconds']:.2f}秒降到{after['median_narration_shot_seconds']:.2f}秒；超过3.15秒的解说段画面由{before['shots_over_3_15_seconds']}镜减至{after['shots_over_3_15_seconds']}镜。片名、校名、正式揭牌和同期口号保留必要的阅读与呼吸时间。

前70.68秒从18镜重编为30镜，前26.68秒为12镜。旧空操场和随意横穿入校的画面已换成红柱窗棂廊道、清楚的笔尖批注、老师自然问候、学生迎面入校、师生共读与专注阅读。片名保持原位置，跨校名立面、教学楼光线与校园树影展开；虚焦翻页候选已剔除。

全片以真实不同角度交替：师生关系接表情与操作，课堂全景接书写细节，体育保留可辨动作，手工由作品转入指尖，史料与校方成果保留证据后接真实校园活动。照片累计时长从{before['photo_seconds']:.2f}秒降至{after['photo_seconds']:.2f}秒。不以切开同一连续画面或放大裁切凑镜数，新增实拍源区间已查重。

校长讲话的连续正面主镜由8秒压至4.44秒，之后用学生板书、教师温和讲解、英语课堂和工程实践对应品格、视野与创新。完整的同步原视频和全部原声仍保留在下层。片尾保留学生并肩走向光亮与可编辑片名。

本轮核验覆盖{qa['unique_actual_stills']}张独立的达芬奇实际输出静帧，包含全片逐镜、开篇首中尾、采访补画与片名字标；主画面连续、素材在线，音频与v6逐项一致。v6及此前版本保留，v7原生DRP与DRT已导出并通过压缩包完整性检查。

此处交付可继续调整的原生工程与实际画面预览，尚未输出MP4，未进行全片连续完整试听。原有约3分55秒“绚丽／顺利”的词音疑问保留原声和复核标记。
'''
report=ROOT/'本轮精剪说明.txt';report.write_text(text)
print(str(preview));print(str(report))
