import json, math, subprocess
from pathlib import Path

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
FPS=24
FF='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'
IDX=json.loads((OUT/'转录/转录索引.json').read_text(encoding='utf-8'))
SOURCES={Path(x['source_path']).stem:x for x in IDX['files']}
STILLS=OUT/'剪辑静帧'; STILLS.mkdir(exist_ok=True)

def src(name):
    if name.endswith('.png'): return str(STILLS/name)
    return SOURCES[name]['source_path']

for name,source,t in [('EP21_开场反应.png','女版21-01-01',0),('EP21_回忆愿望券.png','女版21-05-02',6.5)]:
    path=STILLS/name
    if not path.exists():
        subprocess.run([FF,'-v','error','-ss',str(t),'-i',src(source),'-frames:v','1','-update','1',str(path)],check=True)

def f(t):return round(t*FPS)

class Episode:
    def __init__(self,n):
        self.n=n;self.cursor=0;self.v=[];self.a=[];self.blocks=[]
    def picture(self,name,s,e,tag,properties=None,record=None):
        row=dict(source_path=src(name),source_start_frame=f(s),source_end_frame_exclusive=f(e),record_frame=self.cursor if record is None else record,track=1,tag=tag)
        if properties:row['properties']=properties
        assert row['source_end_frame_exclusive']>row['source_start_frame']
        self.v.append(row)
        return row
    def audio(self,name,s,e,tag,record=None,subtitle=True,track=None):
        self.a.append(dict(source_path=src(name),source_start_frame=f(s),source_end_frame_exclusive=f(e),record_frame=self.cursor if record is None else record,track=track or (2 if SOURCES[name]['kind']=='narration' else 1),subtitle=subtitle,tag=tag))
    def block(self,tag,pictures,audio=None):
        start=self.cursor
        for pic in pictures:
            name,s,e,*props=pic
            self.picture(name,s,e,tag,props[0] if props else None)
            self.cursor+=f(e)-f(s)
        if audio:
            name,s,e,*offset=audio
            self.audio(name,s,e,tag,record=start+(f(offset[0]) if offset else 0))
            assert (f(e)-f(s))+(f(offset[0]) if offset else 0)<=self.cursor-start, (tag,'audio exceeds picture')
        self.blocks.append(dict(tag=tag,start_frame=start,end_frame_exclusive=self.cursor))
    def av(self,name,s,e,tag):self.block(tag,[(name,s,e)],(name,s,e))
    def vo(self,name,s,e,pics,tag):self.block(tag,pics,(name,s,e))
    def result(self):return dict(episode=self.n,english_episode=self.n-1,fps=FPS,timeline_name=f'大码_女版_EP{self.n:02d}_剧情剪辑_v1',duration_frames=self.cursor,video=self.v,audio=self.a,blocks=self.blocks)

E=[]
x=Episode(21)
x.vo('女版21-1',0,7.375,[('EP21_开场反应.png',0,1.375),('女版21-01-01',0,6)],'不回应、建议治疗')
x.av('女版21-01-01',6,8.05,'请求陪坐')
x.vo('女版21-2',0,13.5,[('女版21-01-01',10.5,12.041666667),('女版21-02-01',0,9),('女版21-03-01',0,2.958333333)],'坐下握腕、睡着、抽手惊醒')
x.av('女版21-03-01',2.958333333,5.6,'别走')
x.vo('女版21-3',0,11.375,[('女版21-04-01',0,11.375)],'枕下取出十年愿望券')
x.vo('女版21-4',0,8.083333333,[('女版21-04-01',11.375,19.458333333)],'保存廉价纸券')
x.vo('女版21-5',0,10.708333333,[('女版21-05-02',0,3,{'TransformEnabled':True,'ZoomX':2.0,'ZoomY':2.0,'Pan':-495.0,'Tilt':-151.0}),('女版21-05-02',3,7.0),('EP21_回忆愿望券.png',0,2.166666667),('女版21-05-02',12.5,14.041666667)],'十八岁回忆：避开儿童正脸、保留画券')
x.vo('女版21-05-02',7.125,12.375,[('EP21_回忆愿望券.png',0,3.25),('女版21-04-01',15.0,17.0)],'回忆赠券对白：以纸券及成年听者覆盖儿童说话画面')
x.vo('女版21-6',0,14.083333333,[('女版21-06-01',0,14.083333333)],'回到现在、递券与被撕碎的心意')
x.av('女版21-07-01',0,1.6,'你想换什么')
x.vo('女版21-7',0,14.291666667,[('女版21-07-01',1.6,15.891666667)],'准备拒绝回庄园和放弃纽约')
x.vo('女版21-8',0,10.708333333,[('女版21-07-01',15.891666667,17.516666667),('女版21-08-01',0,9.083333333)],'攥床单、红眼请求')
x.av('女版21-08-01',9.083333333,13.0,'只请求再拥抱一次、落点')
E.append(x.result())

x=Episode(22)
x.vo('女版22-1',0,9.333333333,[('女版22-01-01',0,9.333333333)],'病房静默、想起被撕毁的日记')
x.vo('女版22-2',0,6.583333333,[('女版22-02-01',0,6.583333333)],'撕愿望券、碎片落垃圾桶')
x.vo('女版22-2',7.041666667,9.958333333,[('女版22-01-01',9.333333333,10.25),('女版22-02-01',7.041666667,9.041666667)],'男主伸手僵住；排除多读音节')
x.av('女版22-02-01',9.041666667,12.1,'愿望券已过期')
x.vo('女版22-2',10.166666667,14.75,[('女版22-02-01',12.1,14.041666667),('女版22-03-01',5.8,8.441666667)],'男主苍白、女主起身整理衣服')
x.av('女版22-03-01',1.875,5.875,'接受治疗、不要把人当药')
x.vo('女版22-3',0,2.916666667,[('女版22-03-01',8.4,11.316666667)],'走到门口被叫住')
x.av('女版22-04-01',0,2.75,'醉夜知道是她')
x.vo('女版22-3',3.125,10.791666667,[('女版22-04-01',2.75,10.416666667)],'停步、答案迟来一年')
x.av('女版22-04-01',10.416666667,16.041666667,'Vincent欲联系Alessia、被阻止')
x.av('女版22-05-02',0,12.5,'车内回忆：拦手机、去找Eliza')
x.av('女版22-06-01',0,8.1,'从头到尾要她、为何羞辱追问')
x.vo('女版22-3',11.125,14.875,[('女版22-06-01',8.1,11.85)],'低眼、难言')
x.av('女版22-07-01',0,19.6,'东翼钥匙、研究中心和金钱误会')
x.av('女版22-08-01',0.75,20,'日记真相、报复、雇员伪装')
E.append(x.result())

x=Episode(23)
x.vo('女版23-1',0,2.083333333,[('女版23-1-1',0,2.083333333)],'荒唐的真相')
x.av('女版23-1-1',2.083333333,13.1,'知道爱他仍扔支票、更残忍')
x.av('女版23-2-1',0,10.5,'慌乱下床、愿去纽约等原谅')
x.vo('女版23-1',2.166666667,7.25,[('女版23-3-1',0,5.083333333)],'想起隔壁每日鲜花')
x.av('女版23-3-1',7.458333333,9.875,'拆穿隔壁邻居')
x.vo('女版23-1',7.416666667,12.5,[('女版23-3-1',9.875,14.375),('女版23-4-2',0,0.583333333)],'僵住、沉默后承认')
x.av('女版23-3-1',14.416666667,15.8,'是')
x.av('女版23-4-1',0.416666667,6.916666667,'第三个月找到、Vincent搜索项目医院实验室')
x.av('女版23-4-2',2.916666667,6.458333333,'不知以什么身份靠近')
x.block('街头回忆建立：女主抱花与朋友', [('女版23-5-1',0,2)])
x.vo('女版23-6-1',0,10.583333333,[('女版23-5-1',2,12.583333333)],'原想带回芝加哥、首次自由微笑、没有家族')
x.vo('女版23-6-1',13.5,20.791666667,[('女版23-5-1',12.583333333,15.041666667),('女版23-5-2',0,4.833333333)],'离开才开始生活、想呼喊却退回阴影')
x.block('回病房、忏悔落点', [('女版23-6-1',20.791666667,23.0)])
E.append(x.result())

x=Episode(24)
x.av('女版24-1-1',0,19,'买隔壁公寓、鲜花、床品和推床')
x.av('女版24-2-1',1.8,17.2,'隔墙假装陪伴、听回家才关灯')
x.block('公寓回忆：交钥匙、入屋、推床', [('女版24-3-1',0,5.083333333),('女版24-3-1',8.75,12.708333333)])
x.av('女版24-4-1',0.5,4.6,'听到隔壁走动才能闭眼')
x.vo('女版24-1',0,1.6,[('女版24-4-1',4.6,6.2)],'声音渐低')
x.vo('女版24-4-1',8.875,11.958333333,[('女版24-4-2',0,3.083333333)],'她一夜未归；用听者覆盖低处姿态')
x.block('公寓深夜、手抵墙等待', [('女版24-5-1',0,7)])
x.av('女版24-6-1',0,6.2,'等到天亮、猜她爱上别人')
x.av('女版24-6-2',2.041666667,4.416666667,'会吻他吗')
x.av('女版24-6-3',0.375,2.958333333,'会像从前那样拥抱吗')
x.av('女版24-7-1',0.458333333,24,'酒店等待、想敲门、知道无资格')
x.av('女版24-8-1',0,5.958333333,'回芝加哥、重复旧梦')
x.av('女版24-8-2',2.416666667,6.041666667,'梦里不再沉默、靠近说')
x.av('女版24-8-1',13.0,15.208333333,'梦中Matteo it hurts')
x.block('梦醒、药瓶', [('女版24-8-3',0,3.041666667)])
x.av('女版24-9-1',0,8,'醒来服药、想改变结局')
x.av('女版24-9-1',10.5,15.833333333,'酒精忘记剂量、入院')
x.av('女版24-9-1',19.5,23.041666667,'一夜已接近崩溃')
x.av('女版24-10-2',0.5,2.875,'她却承受十年')
x.vo('女版24-2',0,2.333333333,[('女版24-10-2',2.875,5.208333333)],'红眼看她')
x.av('女版24-10-2',9.125,13,'道歉和听者反应')
E.append(x.result())

x=Episode(25)
x.vo('女版25-1',0,11.958333333,[('女版25-1-1',0,11.958333333)],'听完、迟到真相与窒息')
x.av('女版25-2-1',2.958333333,18.125,'跟踪不是尊重、不曾问愿意')
x.av('女版25-2-3',0,2.666666667,'不曾问需要鲜花')
x.av('女版25-3-2',0.5,6.125,'依旧把她生活当家产')
x.av('女版25-3-1',8.166666667,10.708333333,'秘密住隔壁不是保护')
x.av('女版25-3-1',13.25,16.875,'拒不接受失去她')
x.vo('女版25-2',0,1.583333333,[('女版25-3-1',16.875,18.458333333)],'男主哑声问')
x.av('女版25-4-2',0,7.375,'是否爱上别人、已经与你无关')
x.vo('女版25-2',1.416666667,10.958333333,[('女版25-4-2',7.375,16.916666667)],'话击中他、手垂下、最后望向十年所爱')
x.av('女版25-5-1',0.458333333,21.041666667,'不原地等待、早已离开、推门出病房')
x.block('男主站起停住', [('女版25-6-1',0,2.458333333)])
x.vo('女版25-3',0,2.666666667,[('女版25-6-1',2.458333333,5.125)],'这次真的没有追出')
x.vo('女版25-3',2.666666667,6.208333333,[('女版25-6-1',7.666666667,11.208333333)],'飞机穿云返纽约')
x.vo('女版25-3',6.208333333,14.958333333,[('女版25-6-1',9.75,11.833333333),('女版25-6-1',11.833333333,15.041666667),('女版25-7-2',0,3.458333333)],'十八岁把他放在自己人生之前')
x.vo('女版25-4',0,9.666666667,[('女版25-7-1',0,9.666666667)],'二十八岁先自己、蓝橙天际、不回头')
E.append(x.result())

result={'project':'大码枕头','timeline_policy':'新增五条可编辑时间线，保留既有时间线；仅剪辑及字幕，不启动视频渲染','numbering':'中文21–25 / 英文20–24','episodes':E,'limitations':['EP21回忆原生女主年龄错误，避开儿童正脸，少年局部采用原生变换，纸券局部使用原帧短暂停留。','ASR时码及波形作剪点依据；不把静态抽帧审核冒充完整正常速度听看验收。']}
for ep in E:
    for v in ep['video']:
        assert v['source_end_frame_exclusive']>v['source_start_frame']
    end=0
    for v in ep['video']:
        assert v['record_frame']==end,(ep['episode'],v['tag'],end,v['record_frame'])
        end+=v['source_end_frame_exclusive']-v['source_start_frame']
    assert end==ep['duration_frames']
    for a in ep['audio']:
        assert a['record_frame']+a['source_end_frame_exclusive']-a['source_start_frame']<=end
(OUT/'剪辑执行计划.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{ 'episode':e['episode'],'duration':e['duration_frames']/FPS,'video':len(e['video']),'audio':len(e['audio'])} for e in E],ensure_ascii=False))
