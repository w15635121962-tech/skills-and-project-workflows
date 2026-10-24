import sys,time,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v12 import connect,snap,tc
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'调色预览';
from resolve_bootstrap import get_resolve
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();
if p.GetName()!='学校_曲线二级精修_v12':p=pm.LoadProject('学校_曲线二级精修_v12');assert p
mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()=='学校_曲线与二级精调_v12_20261017';assert r.OpenPage('edit')
def cap(frame,path):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);check=path.with_name(path.stem+'_check.jpg');assert t.SetCurrentTimecode(tc(frame-1));time.sleep(.05);assert t.SetCurrentTimecode(tc(frame));time.sleep(.6);assert p.ExportCurrentFrameAsStill(str(path));prev=np.array(Image.open(path).convert('RGB'),float)
 for attempt in range(4):
  time.sleep(.3);assert p.ExportCurrentFrameAsStill(str(check));now=np.array(Image.open(check).convert('RGB'),float);d=float(abs(prev-now).mean())
  if d<.1:
   if attempt:path.write_bytes(check.read_bytes())
   return Image.open(path).convert('RGB')
  prev=now;path.write_bytes(check.read_bytes())
 raise AssertionError(('Unstable frame',frame,d))
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',22);records=[]
for s in json.loads((OUT/'sample_specs_v12.json').read_text()):
 it=next(x for x in t.GetItemListInTrack('video',s['track']) if x.GetStart()==s['start']);v=it.GetCurrentVersion();before=cap(s['frame'],PRE/'样板前'/f"{s['start']}.jpg");lut=it.GetNodeGraph().GetLUT(1)
 assert ('v12_曲线与精细二级' in it.GetVersionNameList(0) or it.AddVersion('v12_曲线与精细二级',0)) and it.LoadVersionByName('v12_曲线与精细二级',0)
 try:
  assert it.GetNodeGraph().ApplyGradeFromDRX(s['path'],0);g=it.GetNodeGraph();assert g.GetNumNodes()==len(s['nodes']) and g.GetLUT(1)==lut
  after=cap(s['frame'],PRE/'样板后'/f"{s['start']}.jpg");d=np.abs(np.array(before,float)-np.array(after,float));mean=float(d.mean());assert .02<mean<15,(s['start'],mean)
  # Bypass only added nodes to check the original grade survives the new graph.
  for n in range(2,g.GetNumNodes()+1):assert g.SetNodeEnabled(n,False)
  base=cap(s['frame'],PRE/'基础保留复核'/f"{s['start']}.jpg");base_delta=float(abs(np.array(before,float)-np.array(base,float)).mean());assert base_delta<.15,(s['start'],base_delta)
  for n in range(2,g.GetNumNodes()+1):assert g.SetNodeEnabled(n,True)
  # Isolate native qualifier contribution; store actual image proof rather than only metadata.
  assert g.SetNodeEnabled(2,False)
  secondary=cap(s['frame'],PRE/'仅二级复核'/f"{s['start']}.jpg")
  assert g.SetNodeEnabled(2,True)
  sd=np.abs(np.array(before,float)-np.array(secondary,float));sel_delta=float(sd.mean());affected=float(np.mean(np.max(sd,axis=2)>1));assert sel_delta>.005,(s['start'],'Secondary no-op')
  pair=Image.new('RGB',(1920,588),(242,239,230));dr=ImageDraw.Draw(pair)
  for j,(pic,label) in enumerate([(before,'v11 当前'),(after,'v12 原生曲线与二级')]):
   pic=pic.copy();pic.thumbnail((960,540));pair.paste(pic,(j*960,0));dr.text((j*960+18,548),label+' · '+str(round(s['start']/25,2))+'s',font=font,fill=(22,38,30))
  pair.save(PRE/f"样板前后_{s['start']}.jpg",quality=96)
  records.append(dict(s,prior_version=v,lut=lut,actual_nodes=g.GetNumNodes(),actual_tools=[g.GetToolsInNode(i) for i in range(1,g.GetNumNodes()+1)],mean_delta=mean,base_preserved_delta=base_delta,secondary_mean_delta=sel_delta,secondary_affected_above_1=affected,before=str(PRE/'样板前'/f"{s['start']}.jpg"),after=str(PRE/'样板后'/f"{s['start']}.jpg")))
  print('SAMPLE',s['start'],'MEAN',mean,'BASE',base_delta,'SECONDARY',sel_delta,'AREA',affected,flush=True)
 except:
  assert it.LoadVersionByName(v['versionName'],v['versionType']);raise
(OUT/'native_samples_qa_v12.json').write_text(json.dumps({'records':records},ensure_ascii=False,indent=2));assert pm.SaveProject()
