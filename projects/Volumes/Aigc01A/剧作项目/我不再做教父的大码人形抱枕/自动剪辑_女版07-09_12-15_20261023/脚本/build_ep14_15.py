import json
import re
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
FPS=24
P=json.loads((BASE/'原文逐段.json').read_text(encoding='utf-8'))
def para(*indices):
    values=[]
    for i in indices:
        text=P[i-1].strip()
        values.append(re.match(r'^"([^"]+)"',text).group(1) if text.startswith('"') else text)
    return ' '.join(values)
def fr(s): return round(s*FPS)

class Edit:
    def __init__(self,episode,chapter):
        self.ep=episode; self.pos=0
        self.files=json.loads((BASE/f'ASR/EP{episode:02}_complete.json').read_text(encoding='utf-8'))['files']
        self.data={'episode':episode,'source_script_episode':chapter,'timeline_name':f'大码_女版_EP{episode:02}_原速旁白_自动剪辑_20261023_v1',
                   'video':[],'narration':[],'audio_events':[],'limitations':[],
                   'editorial_basis':'原文逐段与实际女版素材对应；原片24fps，旁白100%，同期声同源同剪并链接。'}
    def src(self,kind,name):
        return next(x for x in self.files if x['kind']==kind and Path(x['source_path']).name==name)
    def video(self,g,n,a,b,gain=-17,tag='剧情画面'):
        s=self.src('video',f'女版{self.ep}-{g}-{n}.mp4')
        c={'path':s['source_path'],'source_start_frame':fr(a),'source_end_frame':fr(b),
           'record_frame':self.pos,'gain_db':gain,'tag':tag,'speed_percent':100}
        c['duration_frames']=c['source_end_frame']-c['source_start_frame']
        self.data['video'].append(c); self.pos+=c['duration_frames']
        return c
    def event(self,kind,c,text,speaker,source_a=None,source_b=None):
        self.data['audio_events'].append({'kind':kind,'speaker':speaker,'canonical_text':text,
          'source_path':c['path'],'source_start_frame':c['source_start_frame'] if source_a is None else fr(source_a),
          'source_end_frame':c['source_end_frame'] if source_b is None else fr(source_b),'record_frame':c['record_frame'],
          'clip_source_start_frame':c['source_start_frame']})
    def vo(self,n,a,b,text,start=None):
        s=self.src('narration',f'女版{self.ep}-{n}.mp3')
        c={'path':s['source_path'],'source_start_frame':fr(a),'source_end_frame':fr(b),
           'record_frame':self.pos if start is None else start,'gain_db':0,'tag':'女版新旁白_原速','speed_percent':100}
        c['duration_frames']=c['source_end_frame']-c['source_start_frame']
        self.data['narration'].append(c);self.event('narration',c,text,'Eliza Mercer')
        return c
    def dialogue(self,g,n,a,b,text,speaker,tag='原文同期对白'):
        c=self.video(g,n,a,b,0,tag);self.event('dialogue',c,text,speaker);return c
    def save(self):
        self.data['duration_frames']=self.pos
        self.data['narration'].sort(key=lambda x:x['record_frame'])
        self.data['audio_events'].sort(key=lambda x:x['record_frame'])
        return self.data

e=Edit(14,13)
t=e.pos;e.video(1,1,.125,10.875,tag='合约最后一夜与清空公寓');e.vo(1,0,10.50,para(391,392,393),t+3)
t=e.pos;e.video(2,1,.15,7.30,tag='接管家电话');e.video(2,2,.25,1.25,tag='女主听电话近景');e.vo(2,0,7.875,para(394,395),t+3)
e.dialogue(2,1,7.30,13.95,para(396,397),'Eliza Mercer')
t=e.pos;e.video(3,2,.10,2.10,tag='凌晨时钟');e.video(3,1,2.1,8.6,tag='独自等候并拨电话');e.vo(3,0,8.35,para(398,399,400),t+2)
e.dialogue(3,1,11.10,14.0,para(401),'Eliza Mercer')
t=e.pos;e.video(4,1,4.15,5.95,tag='电话另一头烟花');e.video(4,1,9.15,11.95,tag='烟花与酒杯');e.video(3,1,16.20,16.95,tag='女主听见烟花');e.vo(3,8.35,13.42,para(402,403),t+2)
e.dialogue(4,1,1.15,4.15,para(404),'Alessia Varenna')
t=e.pos;e.video(3,1,14.0,16.20,tag='女主听男主轻笑');e.video(5,2,.10,1.10,tag='握电话的手');e.vo(4,0,3.10,para(405),t+1)
e.dialogue(4,1,5.95,9.15,para(406),'Matteo Bellandi')
t=e.pos;e.video(5,2,1.10,3.40,tag='听见情人撒娇前停顿');e.vo(4,3.10,5.20,para(407),t+1)
e.dialogue(4,1,11.95,16.25,para(408,409),'Alessia Varenna / Matteo Bellandi')
t=e.pos;e.video(5,1,6.05,11.30,tag='最后一丝留恋消退');e.vo(4,5.20,10.18,para(410),t+2)
e.dialogue(5,1,3.50,5.95,para(411),'Eliza Mercer')
t=e.pos;e.video(6,1,4.45,8.90,tag='更换手机卡');e.video(6,2,.10,3.55,tag='留下钥匙支票');e.video(7,1,.15,5.50,tag='飞机与云层');e.vo(5,0,11.70,para(413,414,415),t+2)
e.dialogue(7,1,5.70,9.95,para(416),'Eliza Mercer')
e.data['limitations'].append('文件EP14对应源剧本Episode13，按用户素材集号保留14；人物名称以原文校正ASR。未将自然声识别幻觉写入字幕。')
ep14=e.save()

e=Edit(15,14)
t=e.pos;e.video(1,1,.10,5.45,tag='Alessia坐近男主');e.video(1,1,9.90,12.50,tag='男主出神的反应');e.vo(1,0,7.50,para(419,420),t+3)
e.dialogue(1,1,5.45,9.90,para(421),'Alessia Varenna')
t=e.pos;e.video(2,1,0,14.00,tag='男主想起女主抱他入睡');e.vo(2,0,14.00,para(422,423,424,425),t)
t=e.pos;e.video(3,1,.10,5.10,tag='手机未读消息');e.video(3,2,3.25,6.95,tag='拉情人躺下');e.video(3,1,8.05,12.85,tag='男主彻夜失眠');e.vo(3,0,12.16,para(426,427,428,429),t+3)
t=e.pos;e.video(4,1,.25,12.25,tag='次日来到空公寓');e.vo(4,0,11.60,para(430,431,432),t+3)
t=e.pos;e.video(4,1,12.25,18.80,tag='空床与男主失落');e.video(4,2,.15,.95,tag='空房间视线');e.vo(5,0,6.88,para(433),t+3)
e.dialogue(5,1,0,1.65,para(435),'Matteo Bellandi')
t=e.pos;e.video(5,1,1.65,5.60,tag='无人回应后拨号');e.vo(6,0,3.65,para(436,437),t+1)
e.dialogue(5,1,9.20,10.95,para(438),'Matteo Bellandi')
t=e.pos;e.video(5,1,6.05,7.90,tag='等待Vincent回答');e.vo(6,3.65,5.20,para(439),t+1)
e.dialogue(5,1,11.55,16.95,para(440,441),'Vincent')
t=e.pos;e.video(6,1,.10,3.00,tag='捏紧玩偶');e.vo(6,5.20,7.82,para(442),t+2)
e.dialogue(6,1,4.30,8.00,para(443),'Matteo Bellandi')
e.data['limitations'].append('文件EP15对应源剧本Episode14；同期对白Eliza在片头已经发声，保留0帧开头不截字头。素材内回忆女主与情人位置沿片保留。')
ep15=e.save()
out={'project':'大码枕头','fps':24,'status':'READY_FOR_NATIVE_ASSEMBLY','episodes':[ep14,ep15]}
(BASE/'female_edit_plan_EP14-15.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
for ep in out['episodes']:
    print(ep['episode'],ep['duration_frames']/24,len(ep['video']),len(ep['narration']),len(ep['audio_events']))
