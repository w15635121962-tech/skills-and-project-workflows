import sys,time,json,math,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261018_样片节奏与全员采访精修_v19/工作文件')
from common_v19 import get_resolve,snap,graphs,tc,cap,active_comp,named,setv,solid,merge
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'开篇预览'
PROJECT='学校_曲线二级精修_v12'
PARENT='学校_开篇三素材与强配乐_v20_20261018'
TIMELINE='学校_内外景运镜与人物动势开篇_v21_20261018'
def connect():
 r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()==PROJECT
 t=p.GetCurrentTimeline();assert t and t.GetName()==TIMELINE,t.GetName() if t else None
 return r,pm,p,p.GetMediaPool(),t
