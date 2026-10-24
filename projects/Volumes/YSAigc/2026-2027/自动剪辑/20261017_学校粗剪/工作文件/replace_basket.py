import sys,json
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).parent;ROOT=OUT.parent;plan=json.loads((OUT/'edit_plan.json').read_text());r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==plan['name'];items=t.GetItemListInTrack('video',1)
assert len(items)==84
for i in [51,52]:
 s=plan['shots'][i];old=items[i];assert old.GetMediaPoolItem().GetClipProperty('File Path').endswith('/007/Proxies/C0118_Proxy.mov')
 assert t.DeleteClips([old],False)
 src=mp.ImportMedia([s['path']]);assert src and len(src)==1
 ret=mp.AppendToTimeline([{'mediaPoolItem':src[0],'startFrame':0,'endFrame':s['length_frames'],'mediaType':1,'trackIndex':1,'recordFrame':s['record_frame']}]);assert ret and len(ret)==1
 assert ret[0].GetStart()==s['record_frame'] and ret[0].GetDuration()==s['length_frames']
print('BASKET_REPLACED',flush=True)
assert pm.SaveProject()
prior=OUT/'初次核验导出';prior.mkdir(exist_ok=True)
for name in ['学校_自动粗剪_v1.drt','学校_自动粗剪_v1.drp']:
 f=ROOT/name
 if f.exists():f.rename(prior/name)
note=ROOT/'剪辑说明.txt';txt=note.read_text(encoding='utf-8');txt=txt.replace('当前拍摄输入为1280×720代理素材。','拍摄视频为1280×720代理素材，篮球段采用校内活动照片轻微推近。');txt=txt.replace('画面：84个原生时间线镜头','画面：84个时间线镜头（82个拍摄镜头和2张校内篮球照片的推近片段）');note.write_text(txt,encoding='utf-8')
