import sys,json,base64,time,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).parent;ROOT=OUT.parent
plan=json.loads((OUT/'edit_plan.json').read_text());audio=json.loads((OUT/'audio_plan.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==plan['name'];items=t.GetItemListInTrack('video',1)
assert len(items)==len(plan['shots'])
root=mp.GetRootFolder();bin=next(f for f in root.GetSubFolderList() if f.GetName()=='自动剪辑_20261017')
ab=next((f for f in bin.GetSubFolderList() if f.GetName()=='声音与配乐'),None) or mp.AddSubFolder(bin,'声音与配乐');assert ab;assert mp.SetCurrentFolder(ab)
old_audio=[it for n in range(1,t.GetTrackCount('audio')+1) for it in t.GetItemListInTrack('audio',n)]
if old_audio:
 assert all(it.GetMediaPoolItem().GetClipProperty('File Path').startswith(str(ROOT/'声音')) for it in old_audio),'Existing audio changed, inspect before replacing'
 assert t.SetClipsLinked(old_audio,False)
 assert t.DeleteClips(old_audio,False)
 assert len(t.GetItemListInTrack('video',1))==len(items)
while t.GetTrackCount('audio')<3:assert t.AddTrack('audio','stereo')
for n,name in enumerate(['现场口号与校长讲话','配乐_校园与仪式','配乐_运动与采访'],1):
 assert t.SetTrackName('audio',n,name);assert t.SetTrackEnable('audio',n,True)
assert t.SetTrackName('video',1,'画面_按指定顺序')
placed=[]
for a in audio['speech']+audio['music']:
 imported=mp.ImportMedia([a['path']]);assert imported and len(imported)==1,a['path'];src=imported[0]
 fps=float(src.GetClipProperty('FPS') or 25);count=math.ceil(a['duration_frames']/25*fps-1e-8)
 ret=mp.AppendToTimeline([{'mediaPoolItem':src,'startFrame':0,'endFrame':count,'mediaType':2,'trackIndex':1 if a['kind']=='speech' else a['track'],'recordFrame':a['record_frame']}])
 assert ret and len(ret)==1,a['path'];it=ret[0]
 assert it.GetStart()==a['record_frame'],(a,it.GetStart())
 if it.GetDuration()>a['duration_frames']:
  assert t.DeleteClips([it],False)
  ret=mp.AppendToTimeline([{'mediaPoolItem':src,'startFrame':0,'endFrame':count-1,'mediaType':2,'trackIndex':1 if a['kind']=='speech' else a['track'],'recordFrame':a['record_frame']}]);assert ret;it=ret[0]
 # The project audio source clock is 24 fps; picture is 25 fps. Rounding may
 # shorten the trailing silent handle by one frame, never the spoken words.
 assert 0<=a['duration_frames']-it.GetDuration()<=1,(a,it.GetDuration(),fps)
 if a['kind']=='speech':assert t.SetClipsLinked([items[a['shot_index']],it],True)
 placed.append({'kind':a['kind'],'path':a['path'],'start':it.GetStart(),'end':it.GetEnd(),'fps':fps})
 print('AUDIO',a['kind'],it.GetStart(),it.GetDuration(),flush=True)
assert r.OpenPage('color')
lut='Sony/SLog3SGamut3.CineToLC-709TypeA.cube'
grades=[]
for i,(it,s) in enumerate(zip(items,plan['shots'])):
 assert it.GetStart()==s['record_frame'] and it.GetDuration()==s['length_frames'],i
 assert it.GetMediaPoolItem().GetClipProperty('Online Status')=='Online',s['name']
 graph=it.GetNodeGraph();assert graph and graph.GetNumNodes()>=1
 assert graph.SetLUT(1,lut),s['name'];grades.append({'index':i,'lut':lut})
 if s['speed']!=1:
  comp=it.GetFusionCompByIndex(1);assert comp
  ts=next(z for z in comp.GetToolList(False).values() if z.GetAttrs().get('TOOLS_RegID')=='TimeSpeed')
  assert abs(ts.GetInput('Speed')-s['speed'])<.001
 # Timeline section markers carry the organization; clip colors are optional.
 it.SetClipColor('Orange' if s['voice'] else ('Cyan' if 11<=int(s['section'][:2])<=18 else 'Blue'))
print('GRADED',len(grades),flush=True)
# Editable fade from black and fade to black, with voice timing untouched.
assert r.OpenPage('edit')
for idx,fadein in [(0,True),(len(items)-1,False)]:
 it=items[idx];comp=it.AddFusionComp();assert comp
 tools=list(comp.GetToolList(False).values());mi=next(z for z in tools if z.GetAttrs().get('TOOLS_RegID')=='MediaIn');mo=next(z for z in tools if z.GetAttrs().get('TOOLS_RegID')=='MediaOut')
 bc=comp.AddTool('BrightnessContrast');assert bc;assert bc.ConnectInput('Input',mi);assert mo.ConnectInput('Input',bc)
 bc.Gain=comp.BezierSpline();last=it.GetDuration()-1
 if fadein:bc.Gain[0]=0;bc.Gain[15]=1
 else:bc.Gain[last-30]=1;bc.Gain[last]=0
 assert abs(bc.GetInput('Gain',0)-(0 if fadein else 1))<.001
 assert it.ExportFusionComp(str(OUT/f'fade-{idx+1}.comp'),it.GetFusionCompCount())
sections=list(dict.fromkeys(s['section'] for s in plan['shots']))
colors=['Blue','Cyan','Green','Yellow','Purple']
for i,sec in enumerate(sections):
 ss=[s for s in plan['shots'] if s['section']==sec];start=ss[0]['record_frame'];duration=sum(s['length_frames'] for s in ss)
 assert t.AddMarker(start,colors[min(i//5,4)],sec,'用户指定顺序；现场原声保留' if ss[0]['voice'] else '按画面内容精选',duration,'school-autoedit-20261017')
rope_end=next(s['record_frame'] for s in plan['shots'] if s['section'].startswith('20'))
assert t.AddMarker(rope_end-1,'Red','19 仰卧起坐待补','尚未找到可确认的仰卧起坐；没有用拉伸或平板支撑代替，无黑场占位。',1,'school-autoedit-missing')
assert pm.SaveProject()
(OUT/'finalize_result.json').write_text(json.dumps({'timeline':t.GetName(),'audio_items':placed,'grades':grades,'markers':t.GetMarkers()},ensure_ascii=False,indent=2),encoding='utf-8')
print('FINALIZED',t.GetName(),flush=True)
