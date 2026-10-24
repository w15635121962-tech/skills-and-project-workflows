import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
inventory=json.loads((OUT/'男版素材盘点.json').read_text(encoding='utf-8'))
video_sources={Path(x['path']).stem:x for ep in inventory['episodes'] for x in ep['videos']}
audio_sources={Path(x['path']).stem:x for ep in inventory['episodes'] for x in ep['narration_audio']}
FPS=24
def f(s):return round(s*FPS)
class Episode:
    def __init__(self,ep):self.ep=ep;self.cursor=0;self.video=[];self.narration=[]
    def block(self,tag,pics,vo=None):
        start=self.cursor
        for name,s,e in pics:
            row=video_sources[name];last=f(e);first=f(s)
            if row.get('video_streams'):assert last<=int(row['video_streams'][0]['nb_frames']),(name,last)
            assert last>first
            self.video.append({'path':row['path'],'src0':first/24,'src1':last/24,'record':self.cursor/24,
                               'tag':tag,'gain_db':-14 if vo else 0})
            self.cursor+=last-first
        if vo:
            name,s,e=vo;assert f(e)-f(s)<=self.cursor-start,(tag,f(e)-f(s),self.cursor-start)
            self.narration.append({'path':audio_sources[name]['path'],'src0':f(s)/24,'src1':f(e)/24,
                                   'record':start/24,'tag':tag,'gain_db':0})
    def result(self):return {'episode':self.ep,'fps':24,'video':self.video,'narration':self.narration,'duration_seconds':self.cursor/24}
episodes=[]
x=Episode(21)
x.block('病房陪坐、伸展、握腕',[('男版21-1-1',0,14.25)],('男版21-1',0,14.088))
x.block('闭眼不安到傍晚醒来、轻抽手',[('男版21-2-1',0,4),('男版21-2-1',6.75,14.041667)],('男版21-2',0,11.112))
x.block('Oliver提出离开',[('男版21-3-1',0,2.5)])
x.block('Vittoria叫住他',[('男版21-3-1',5.9,7.1)])
x.block('抓衣角、从枕下抽旧愿望卡',[('男版21-3-1',7.1,15.041667),('男版21-4-1',4.8,7.1),('男版21-4-2',2.8,4.5),('男版21-4-2',4.6,7.041667),('男版21-4-1',0,1.5)],('男版21-3',0,15.552))
x.block('看卡引出童年制作的回忆',[('男版21-4-1',0,1.7),('男版21-4-2',4.6,7.041667),('男版21-5-1',0,7.75),('男版21-4-1',5,7.75)],('男版21-4',0,14.544))
x.block('少年Oliver安慰她',[('男版21-5-1',7.75,10.041667)])
x.block('回病房从她手中接过卡',[('男版21-6-1',0,2.25),('男版21-6-2',11,12)],('男版21-5-1',0,3.072))
x.block('询问愿望',[('男版21-6-2',0.25,1.95)])
x.block('猜想是否继续充当抱枕',[('男版21-6-2',2,3.5)],('男版21-5-3',0,1.368))
x.block('猜想收住、等待真正的愿望',[('男版21-6-2',3.5,7.2),('男版21-6-2',10.85,13.85)],('男版21-5-4',0,6.528))
x.block('只请求最后一次拥抱',[('男版21-6-2',8.25,10.85)])
x.block('迟疑后撕卡、对应过去被撕的日记',[('男版21-6-2',11,14.041667),('男版21-7-1',0,9.65)],('男版21-6',0,12.504))
x.block('愿望已经过期',[('男版21-7-1',9.65,12.05)])
x.block('她的绝望落点',[('男版21-7-1',12.05,15.041667)])
e=x.result();e['limitations']=['原文Did she want me back in Veriston?未找到对应男版21-5-2录音，未合成人声。','原片愿望卡仅ONE WISH，与源稿One Free Wish文字不同；童年形象显小于13岁；部分成年镜头外衬连续性来自原片。'];episodes.append(e)

x=Episode(22)
x.block('扔碎片、走到门口',[('男版22-1-1',0,6.25),('男版22-1-1',8.05,9.7)],('男版22-1',0,7.8))
x.block('门口被叫住',[('男版22-1-1',6.25,8.15)])
x.block('她看着背影',[('男版22-1-1',9.2,11.041667)],('男版22-1',8.25,10.056))
x.block('醉酒那晚始终知道是他：选完整单次表演',[('男版22-2-2',0,6.65)])
x.block('迟到的答案没有改变现状',[('男版22-2-1',8,16.041667),('男版22-3-1',12,16.041667)],('男版22-2',0,11.976))
x.block('淡淡伤感、准备轻声打断',[('男版22-2-1',10,16.041667),('男版22-4-1',10.5,12.041667)],('男版22-3',0,7.55))
x.block('已经不再重要',[('男版22-3-1',0.3,2.55)])
x.block('她急忙继续',[('男版22-3-1',2.7,4.8)],('男版22-3',8,10.0))
x.block('可以搬去等待、请求别走',[('男版22-3-1',5.9,11.1)])
x.block('他转回看她',[('男版22-3-1',13.4,16.041667)],('男版22-3',10.15,12.7))
x.block('问隔壁公寓归属',[('男版22-4-1',0,2.9)])
x.block('被看穿后的慌张',[('男版22-4-1',3.7,6.45)],('男版22-3',13.3,16.032))
x.block('只想靠近',[('男版22-4-1',6.9,10.5)])
x.block('最后一次看着她',[('男版22-4-1',10.5,12.041667),('男版22-3-1',14.1,16.041667)],('男版22-4',0,3.48))
x.block('劝治疗、不能一生等待别人',[('男版22-5-1',0.5,8.35)])
x.block('开门离开不回头',[('男版22-5-1',8.35,13.6)],('男版22-4',3.75,8.95))
x.block('飞机晨光',[('男版22-6-2',0,5.041667)],('男版22-4',9,13.992))
x.block('深蓝与琥珀、飞向新生活',[('男版22-6-1',4.75,12.041667)],('男版22-5',0,7.2))
episodes.append(x.result())

x=Episode(23)
x.block('转Vittoria视角：选大学、听见保证',[('男版23-1-1',0,13.041667),('男版23-2-2',0,1.85)],('男版23-1',0,14.736))
x.block('Oliver只为钱的保证',[('男版23-2-1',2.3,5.95)])
x.block('懵懂感情变成恨',[('男版23-2-1',6,9.9)],('男版23-2',0,3.85))
x.block('当晚愤怒抓住他',[('男版23-3-1',0,3.75)],('男版23-2',4,7.75))
x.block('付钱就会陪睡的质问',[('男版23-3-1',3.65,6.8)])
x.block('男主被抓疼、她认出他的表情',[('男版23-3-3',0,7.041667),('男版23-3-1',6.9,8.05)],('男版23-2',8,15.96))
x.block('她否定他的委屈',[('男版23-3-1',8.05,13)],('男版23-3',0,4.95))
x.block('日记、三天回避',[('男版23-3-1',13,15.041667),('男版23-4-1',0,9.041667)],('男版23-3',5.1,16.15))
x.block('醉酒后顾问扶她',[('男版23-5-1',0,3.6),('男版23-5-1',8.65,9.85)],('男版23-4',0,4.75))
x.block('顾问问去哪',[('男版23-5-1',3.6,5.2)])
x.block('酒精让愤怒迟钝',[('男版23-5-1',5.2,6.55),('男版23-5-1',1,2.15)],('男版23-4',5,7.45))
x.block('带我去睡觉',[('男版23-5-1',6.55,8.65)])
x.block('准备打给Evan、她按住手机',[('男版23-5-1',8.65,11.041667),('男版23-6-2',0,4.041667)],('男版23-4',7.5,13.8))
x.block('明确指定Oliver',[('男版23-6-1',3.9,5.85)])
x.block('顾问收住、车驶离',[('男版23-6-1',5.85,10.041667)])
e=x.result();e['limitations']=['避开23-3-2红眼异常片，改用同组3-3自然眼神补镜。'];episodes.append(e)

for e in episodes:
    cursor=0
    for v in e['video']:
        assert f(v['record'])==cursor
        cursor+=f(v['src1'])-f(v['src0'])
    assert cursor==f(e['duration_seconds'])
    for a in e['narration']:
        assert f(a['record'])+f(a['src1'])-f(a['src0'])<=cursor
(OUT/'EP21-23_剪辑计划.json').write_text(json.dumps({'episodes':episodes},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'ep':e['episode'],'seconds':e['duration_seconds'],'v':len(e['video']),'vo':len(e['narration'])} for e in episodes],ensure_ascii=False))
