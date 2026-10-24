import sys,json,time
from pathlib import Path
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v9 import connect,snap,tc
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件'
r,pm,p,mp,t=connect();assert t.GetName()=='学校_通透感与高光控制_v11_20261017',t.GetName()
s=snap(t);prior=json.loads((ROOT.parent/'20261017_通透感与高光控制_v11/工作文件/final_native_snapshot_v11.json').read_text());assert s==prior,'Manual timeline changes detected'
graphs=[]
for tr in range(1,t.GetTrackCount('video')+1):
 for it in t.GetItemListInTrack('video',tr):
  g=it.GetNodeGraph();graphs.append({'track':tr,'start':it.GetStart(),'version':it.GetCurrentVersion(),'nodes':g.GetNumNodes(),'luts':[g.GetLUT(i) for i in range(1,g.GetNumNodes()+1)],'tools':[g.GetToolsInNode(i) for i in range(1,g.GetNumNodes()+1)]})
(OUT/'live_before_v12.json').write_text(json.dumps({'snapshot':s,'timeline':t.GetName(),'graphs':graphs,'page':r.GetCurrentPage(),'timecode':t.GetCurrentTimecode()},ensure_ascii=False,indent=2))
assert pm.SaveProject();assert t.Export(str(ROOT/'学校_曲线二级精调前_v11备份.drt'),r.EXPORT_DRT)
n=t.DuplicateTimeline('学校_曲线与二级精调_v12_20261017');assert n and p.SetCurrentTimeline(n);assert snap(n)==s;assert r.OpenPage('color');assert n.SetCurrentTimecode(tc(146));time.sleep(1)
gal=p.GetGallery();album=gal.CreateGalleryStillAlbum();assert album and gal.SetAlbumName(album,'v12_曲线二级原生备份') and gal.SetCurrentStillAlbum(album)
still=n.GrabStill();print('STILL',bool(still),flush=True)
assert still;assert album.SetLabel(still,'v11_117_原生完整基准');ok=album.ExportStills([still],str(ROOT/'原生调色文件'),'baseline117','drx');print('EXPORT_DRX',ok,flush=True);print('FILES',[x.name for x in (ROOT/'原生调色文件').iterdir()],flush=True);assert ok;assert pm.SaveProject()
