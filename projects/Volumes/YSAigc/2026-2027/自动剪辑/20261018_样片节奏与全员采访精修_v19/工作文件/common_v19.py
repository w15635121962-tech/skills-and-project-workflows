import sys,time,json,math,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_片尾第三轨大方选镜_v17/工作文件')
from common_v17 import get_resolve,snap,graphs,tc,cap,named,setv,solid,merge,active_comp
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精修预览'
PROJECT='学校_曲线二级精修_v12';TIMELINE='学校_样片节奏与全员采访精修_v19_20261018'
def connect(require_timeline=True):
 r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()==PROJECT
 t=p.GetCurrentTimeline();assert t
 if require_timeline:assert t.GetName()==TIMELINE,t.GetName()
 return r,pm,p,p.GetMediaPool(),t
