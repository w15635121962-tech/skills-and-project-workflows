# -*- coding: utf-8 -*-
import json,sys,shutil
from pathlib import Path
root=Path(__file__).resolve().parent
out=root/'最终交付'
d=json.loads((out/'最终核验_最终重开核验.json').read_text())
old=json.loads((out/'最终核验_重开后.json').read_text())
assert d['passed'] and d['totals']=={'A1':44,'A2':31,'S1':152,'A4':12}
for a,b in zip(d['episodes'],old['episodes']):
 assert a['tracks']['video']==b['tracks']['video']
 assert a['tracks']['audio']==b['tracks']['audio']
 for x,y in zip(a['tracks']['subtitle'][0]['items'],b['tracks']['subtitle'][0]['items']):
  assert (x['name'],x['start'],x['end'])==(y['name'],y['start'],y['end'])
folder=out/'可导入时间线与字幕';folder.mkdir(exist_ok=True)
for e in d['episodes']:
 ep=e['episode']
 shutil.copy2(e['exports'][0],folder/f'EP{ep}_旁白110精修.drt')
 shutil.copy2(root/f'SRT_110精修/EP{ep}.srt',folder/f'EP{ep}.srt')
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject()
t=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()=='大码_女版_EP21_精修_旁白110_v2')
assert p.SetCurrentTimeline(t)
assert t.SetCurrentTimecode('00:00:00:00')
assert pm.SaveProject()
backup=out/'大码枕头_EP21-25_旁白110_精修完成.drp'
assert pm.ExportProject('大码枕头',str(backup))
report='''# EP21–25 旁白110精修交付

Resolve工程：大码枕头。工作时间线为“大码_女版_EP21…25_精修_旁白110_v2”；原五集v1保持不变。

已将31段旁白统一为原生可编辑110%，原生操作启用音调校正；按新节奏回调画面、44段原片对白及动作环境同期声。所有MP4画面有对应同源、同偏移的100%同期声。

删减旁白静音与重复画面，修正撕纸、起身、街道转病房和机舱重复动作；五集共缩短467帧（24fps，19.458秒）。12段CC0配乐重新处理淡入淡出和人声避让，两处对白及两处环境声做最终余量调整。

152条原生字幕保持可编辑，正文及新时码逐条核验，字幕轨名为21–25。统一继承轨道样式、修复单条字号覆盖导致的越界。五集SRT附在“可导入时间线与字幕”。

最终时长：EP21 01:36:06；EP22 01:48:13；EP23 01:08:13；EP24 02:13:21；EP25 01:43:04（24fps）。

保存并关闭重开项目后，全部五集轨道、源范围、原生变速、同期声覆盖、字幕正文/时码核验通过；完成关键画面全屏抽查。尚未完成五集逐秒听审，也未渲染交付成片。离线叠加音频QC不等同于原生Fairlight总线的最终听审。

完整工程备份：大码枕头_EP21-25_旁白110_精修完成.drp。中间准备时间线移入“精修准备_保留恢复_旁白110”媒体夹，保留恢复及精确接句源依赖。
'''
(out/'交付说明.md').write_text(report,encoding='utf-8')
print('FINAL_BACKUP',str(backup),backup.stat().st_size,flush=True)
print('ALL_152_CUES_AND_AV_PERSISTED_WITH_STYLE_REPAIR',flush=True)
