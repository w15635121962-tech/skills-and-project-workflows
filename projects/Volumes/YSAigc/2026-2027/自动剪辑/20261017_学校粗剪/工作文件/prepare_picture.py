import sys,json,math,concurrent.futures
from pathlib import Path
from fractions import Fraction
import av
from PIL import Image,ImageDraw
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts')
from _common.timeline import to_fcpxml
OUT=Path(__file__).parent
plan=json.loads((OUT/'edit_plan.json').read_text());rows={r['key']:r for r in json.loads((OUT/'footage.json').read_text())}
clips=[]
for i,s in enumerate(plan['shots']):
 r=rows[s['key']]
 clips.append({'index':i,'src':s['path'],'name':s['name'],'src_in':round(s['in']*25),'src_out':round(s['out']*25),'speed':s['speed'],'length':s['length_frames'],'media_frames':round(r['duration']*25),'has_video':True,'has_audio':False,'picture':(1280,720),'fps':r['fps'],'reframed':False,'trim_head':0,'trim_tail':0,'visible':s['length_frames'],'record_in':s['record_frame']})
tl={'rate':Fraction(25),'width':1920,'height':1080,'name':plan['name'],'total':plan['duration_frames'],'transition_frames':0,'markers':[],'music':None,'clips':clips,'fit':'pad'}
(OUT.parent/'学校_自动粗剪.fcpxml').write_text(to_fcpxml(tl),encoding='utf-8')
def frame(s):
 tm=(s['in']+s['out'])/2
 with av.open(s['path']) as c:
  v=c.streams.video[0];c.seek(int(tm/v.time_base),stream=v)
  for fr in c.decode(v):
   if (fr.time or 0)>=tm:
    im=fr.to_image();im.thumbnail((320,180));return s,im
 raise RuntimeError(s['name'])
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:rs=list(ex.map(frame,plan['shots']))
for start in range(0,len(rs),28):
 part=rs[start:start+28];sheet=Image.new('RGB',(1280,math.ceil(len(part)/4)*210),'white');draw=ImageDraw.Draw(sheet)
 for k,(s,im) in enumerate(part):
  x=k%4*320;y=k//4*210;sheet.paste(im,(x,y));draw.text((x+2,y+182),f"#{start+k+1} "+s['section']+' '+s['name'],fill='black');draw.text((x+2,y+196),f"{s['in']:.2f}-{s['out']:.2f}s  speed {s['speed']}",fill='black')
 dest=OUT/f'picture-selects-{start//28+1}.jpg';sheet.save(dest);print(dest)
