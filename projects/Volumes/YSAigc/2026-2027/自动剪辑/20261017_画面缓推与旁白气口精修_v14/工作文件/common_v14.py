import sys,time,json,math,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_图片动态底板精修_v13/工作文件')
from common_v13 import get_resolve,snap,graphs,tc,cap
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精修预览';PRE.mkdir(exist_ok=True);PROJECT='学校_曲线二级精修_v12';TIMELINE='学校_画面缓推与旁白气口精修_v14_20261017'
def connect():
 r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()==PROJECT;t=p.GetCurrentTimeline();assert t and t.GetName()==TIMELINE
 return r,pm,p,p.GetMediaPool(),t
def video_unchanged(t,before,allow_fusion=None):
 current=snap(t)['video'];original=json.loads(json.dumps(before['snapshot']['video']));allow_fusion=allow_fusion or set()
 for track in current:
  for it in track['items']:
   if (track['track'],it['start']) in allow_fusion:
    other=next(x for x in original[track['track']-1]['items'] if x['start']==it['start']);it['fusion_count']=other['fusion_count']
 assert current==original
