import sys,time,json
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();print('CONNECTED',p.GetName() if p else None,flush=True)
if p and p.GetName()!='Untitled Project':assert pm.SaveProject()
print('CREATE_BEGIN',flush=True);p=pm.CreateProject('_v12曲线二级兼容性测试_20261017');assert p;print('PROJECT_CREATED',flush=True)
p.SetSetting('timelineFrameRate','25');p.SetSetting('timelineResolutionWidth','1920');p.SetSetting('timelineResolutionHeight','1080');mp=p.GetMediaPool();t=mp.CreateEmptyTimeline('曲线二级隔离验证');assert t;p.SetCurrentTimeline(t)
old=next(x for x in json.loads((OUT/'original_grade_bodies_v11.json').read_text()) if x['track']==1 and x['start']==117);items=mp.ImportMedia([old['source']]);assert items
base=json.loads((OUT/'live_before_v12.json').read_text());st=next(x for x in base['snapshot']['video'][0]['items'] if x['start']==117);offset=st['offset']
it=mp.AppendToTimeline([{'mediaPoolItem':items[0],'startFrame':offset,'endFrame':offset+58,'mediaType':1,'trackIndex':1,'recordFrame':0}])[0];assert it;assert t.SetStartTimecode('00:00:00:00');assert t.SetCurrentTimecode('00:00:01:04');assert pm.SaveProject()
records=[];specs=json.loads((OUT/'probe_specs.json').read_text());specs.sort(key=lambda x:0 if x['name']=='qualifier_sat' else 1);specs=[x for x in specs if len(sys.argv)<2 or x['name']==sys.argv[1]]
for s in specs:
 print('APPLY_BEGIN',s['name'],flush=True);(OUT/'probe_current_feature.txt').write_text(s['name']);assert it.GetNodeGraph().ApplyGradeFromDRX(s['path'],0);print('APPLY_RETURNED',s['name'],flush=True);g=it.GetNodeGraph();assert g.GetNumNodes()==2;assert r.OpenPage('edit');time.sleep(.7)
 dest=ROOT/'调色预览'/f"隔离验证_{s['name']}.jpg";assert p.ExportCurrentFrameAsStill(str(dest));print('FRAME_EXPORTED',s['name'],flush=True);records.append({'name':s['name'],'nodes':g.GetNumNodes(),'tools':[g.GetToolsInNode(i) for i in [1,2]],'path':str(dest)});(OUT/'native_feature_probe_v12.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));assert pm.SaveProject()
print('ALL_ISOLATED_NATIVE_FEATURES_PASSED',flush=True)
