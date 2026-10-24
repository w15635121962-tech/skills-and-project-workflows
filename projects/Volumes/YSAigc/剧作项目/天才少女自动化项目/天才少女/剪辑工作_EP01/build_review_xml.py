from pathlib import Path
import xml.etree.ElementTree as E
import av,json
ROOT=Path.cwd(); OUT=ROOT/'剪辑工作_EP01'; FPS=24
name='天才少女EP01_粗剪待复核_20261009'
root=E.Element('xmeml',version='5'); seq=E.SubElement(root,'sequence',id='seq-ep01')
def put(p,k,v): E.SubElement(p,k).text=str(v)
def rate(p): r=E.SubElement(p,'rate');put(r,'timebase',24);put(r,'ntsc','FALSE')
put(seq,'name',name);rate(seq)
media=E.SubElement(seq,'media');vid=E.SubElement(media,'video');fmt=E.SubElement(vid,'format');sc=E.SubElement(fmt,'samplecharacteristics');rate(sc)
for k,v in [('width',720),('height',1280),('anamorphic','FALSE'),('pixelaspectratio','square'),('fielddominance','none')]:put(sc,k,v)
vt=E.SubElement(vid,'track');aud=E.SubElement(media,'audio');put(aud,'numOutputChannels',2);at=E.SubElement(aud,'track');vo=E.SubElement(aud,'track')
meta={};counter=0;defined=set();cursor=0;manifest=[]
def path(code):return ROOT/'天才少女01集'/f'天才少女-01-{code}.mp4'
def info(p):
 if p not in meta:
  c=av.open(str(p));meta[p]=(round(c.duration/av.time_base*24),len(c.streams.video)>0);c.close()
 return meta[p]
def fnode(parent,p):
 fid='file'+str(list(meta).index(p)+1); f=E.SubElement(parent,'file',id=fid)
 if fid in defined:return
 defined.add(fid);put(f,'name',p.name);put(f,'pathurl',p.as_uri());rate(f);put(f,'duration',info(p)[0]); m=E.SubElement(f,'media')
 if info(p)[1]:
  v=E.SubElement(m,'video');s=E.SubElement(v,'samplecharacteristics');rate(s)
  for k,val in [('width',720),('height',1280),('anamorphic','FALSE'),('pixelaspectratio','square'),('fielddominance','none')]:put(s,k,val)
 a=E.SubElement(m,'audio');s=E.SubElement(a,'samplecharacteristics');put(s,'depth',16);put(s,'samplerate',48000);put(a,'channelcount',2)
def clip(track,p,start,inf,dur,typ):
 global counter
 info(p);counter+=1;c=E.SubElement(track,'clipitem',id=f'clip-{counter}');put(c,'name',p.stem);put(c,'duration',info(p)[0]);rate(c)
 for k,v in [('start',start),('end',start+dur),('in',inf),('out',inf+dur)]:put(c,k,v)
 fnode(c,p);s=E.SubElement(c,'sourcetrack');put(s,'mediatype',typ);put(s,'trackindex',1)
 if typ=='audio':
  fil=E.SubElement(c,'filter');ef=E.SubElement(fil,'effect')
  for k,v in [('name','Audio Levels'),('effectid','audiolevels'),('effectcategory','audiolevels'),('effecttype','audio'),('mediatype','audio')]:put(ef,k,v)
  par=E.SubElement(ef,'parameter');put(par,'parameterid','level');put(par,'name','Level');put(par,'value',1)
def video(code,ins,outs,dialog=False):
 global cursor
 p=path(code);i=round(ins*24);d=round((outs-ins)*24);clip(vt,p,cursor,i,d,'video')
 if dialog:clip(at,p,cursor,i,d,'audio')
 manifest.append({'file':p.name,'timeline_in':cursor/24,'source_in':i/24,'duration':d/24,'original_audio':dialog});cursor+=d;return cursor-d
def narration(n,start,ins=0,outs=None):
 p=ROOT/'天才少女自动化项目/旁白配音/天才少女EP01'/f'天才01-{n}.mp3';total=info(p)[0];i=round(ins*24);d=total-i if outs is None else round((outs-ins)*24);clip(vo,p,round(start*24),i,d,'audio')
def marker(title,note,frame=None):
 m=E.SubElement(seq,'marker');put(m,'name',title);put(m,'comment',note);put(m,'in',cursor if frame is None else frame);put(m,'out',-1)
# Approved nine opening shots. Imported lab/title suffixes follow actual picture.
for c,i,o in [('00-01',0,2.5),('00-03',0,2.5),('00-03',2.5,5),('00-01',2.5,5),('00-02',0,2.5),('00-04',0,2.5),('00-04',2.5,5),('00-04',5,7.5),('00-04',7.5,10)]:video(c,i,o)
for t,i,o in [(2.5,0,2.9),(5.5,3.0,5.95),(10,6.05,8.3),(17.5,8.7,10.8),(20,11,13.512)]:narration(1,t,i,o)
marker('开场字版待跟踪','Cyber Twins校报标题及ELENA/C手机文字需跟踪合成；现有底片不代表字版已完成。',240)
marker('Madison发言断组待复核','第一句在05号，后两句在06-02；保留原声拼接，尚未达到单镜完整发言要求。')
video('05-01',6.7,9,True);video('06-02',0,8.7,True);video('06-03',0,4.7,True)
start=cursor/24;narration(2,start);video('07-01',0,10.125)
start=cursor/24;narration(3,start);video('00-01',0,5);video('07-01',10.125,13.0833333)
start=cursor/24;narration(4,start);video('07-01',7,14);video('08-01',0,7.2083333)
marker('闪回画面待补','现有数字镜头重组覆盖旁白；8岁Elena及全球团队追踪画面未找到，非最终画面验收。',round(start*24))
start=cursor/24;narration(5,start);video('09-01',0,3.5);video('10-01',0,1.5);video('11-01',0,3);video('12-01',6.6666667,10.7083333)
start=cursor/24;narration(6,start);video('14-01',2,6.5);video('14-01',11.1666667,12.2083333);video('13-01',0,1.5)
marker('缺Xavier第一句对白','未找到 This is Northbridge’s prized Cyber Twins? Pure trash. 对应完整音画。此处不造声、不插假台词。')
video('13-01',0,14.6666667,True)
start=cursor/24;narration(7,start);video('14-01',0,6.5);video('15-01',0,1.2083333)
video('14-01',6.5,12.6666667,True);video('15-01',5.5,12)
marker('结尾动作待补','抽查15号仍以坐姿反应为主，16号画面黑；Elena摘耳机站起终态待确认或补镜。',cursor-156)
put(seq,'duration',cursor);tc=E.SubElement(seq,'timecode');rate(tc);put(tc,'string','00:00:00:00');put(tc,'frame',0);put(tc,'displayformat','NDF')
for t in [vt,at,vo]:put(t,'enabled','TRUE');put(t,'locked','FALSE')
E.indent(root);E.ElementTree(root).write(OUT/'EP01_粗剪待复核.xml',encoding='utf-8',xml_declaration=True)
(OUT/'剪辑清单.json').write_text(json.dumps({'timeline':name,'fps':24,'duration':cursor/24,'clips':manifest},ensure_ascii=False,indent=2))
print(name,'duration',cursor/24,'clips',len(manifest))
