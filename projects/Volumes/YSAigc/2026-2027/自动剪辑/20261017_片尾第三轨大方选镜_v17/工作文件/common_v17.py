import sys,time,json,math,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_图片动态底板精修_v13/工作文件')
from common_v13 import get_resolve,snap,graphs,tc,cap
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精修预览'
PROJECT='学校_曲线二级精修_v12';TIMELINE='学校_片尾第三轨大方选镜_v17_20261017'
def connect():
 r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()==PROJECT
 t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE,t.GetName()
 return r,pm,p,p.GetMediaPool(),t

def named(c,typ,name):
 x=c.AddTool(typ);assert x,typ;x.SetAttrs({'TOOLS_Name':name});return x

def setv(x,d):
 for k,v in d.items():x.SetInput(k,v)

def solid(c,name,color,alpha=1):
 x=named(c,'Background',name);setv(x,{'UseFrameFormatSettings':0,'Width':1920,'Height':1080,'TopLeftRed':color[0],'TopLeftGreen':color[1],'TopLeftBlue':color[2],'TopLeftAlpha':alpha});return x

def merge(c,bg,fg,name,blend=1):
 m=named(c,'Merge',name);assert m.ConnectInput('Background',bg) and m.ConnectInput('Foreground',fg);m.SetInput('Blend',blend);return m

def active_comp(it):
 n=it.GetFusionCompNameList();name=next(iter(n.values())) if isinstance(n,dict) else n[0];c=it.LoadFusionCompByName(name);assert c;return c
