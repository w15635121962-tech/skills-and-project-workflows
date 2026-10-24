from pathlib import Path
import json,hashlib
b=Path(__file__).resolve().parent
x=json.loads((b/'原始MP3来源顺序核验.json').read_text(encoding='utf8'))
for c in x['files']:
 assert hashlib.sha256(Path(c['path']).read_bytes()).hexdigest()==c['sha256']
def lua(x):
 if x is None:return 'nil'
 if isinstance(x,bool):return str(x).lower()
 if isinstance(x,(int,float)):return repr(x)
 if isinstance(x,str):return json.dumps(x,ensure_ascii=False)
 if isinstance(x,list):return '{'+','.join(lua(v)for v in x)+'}'
 return '{'+','.join('['+lua(str(k))+']='+lua(v)for k,v in x.items())+'}'
helpers=Path('替换旁白_女版EP01-03_20261021/native_template.lua').read_text(encoding='utf8').split("local report={status='STARTED_NATIVE'")[0]
config={'base':str(b),'files':x['files'],'episodes':x['episodes']}
script='''
local report={status='STARTED',source_speed_percent=100,tempo_processing=false,episodes={}}
local function main()
 local pm=resolve:GetProjectManager();local p=assert(pm:GetCurrentProject());assert(p:GetName()=='大码枕头');local mp=p:GetMediaPool()
 assert(pm:SaveProject(),'save before backup');report.project=p:GetName();report.before_backup=cfg.base..'/备份/大码枕头_创建原速测试前.drp';assert(pm:ExportProject(p:GetName(),report.before_backup))
 local byname={};for i=1,p:GetTimelineCount()do local t=p:GetTimelineByIndex(i);byname[t:GetName()]=t end
 local protected={}
 for n=1,3 do local name=string.format('大码_女版_EP%02d',n);local t=assert(byname[name]);assert(p:SetCurrentTimeline(t));protected[#protected+1]={timeline=t,before=snapshot(t)} end
 report.protected_before={};for _,v in ipairs(protected)do report.protected_before[#report.protected_before+1]=v.before end
 write('创建前正式时间线快照.json',report.protected_before)
 local foldername='女版前3集_新旁白原速测试_20261021';local folder
 for _,f in ipairs(mp:GetRootFolder():GetSubFolderList() or {})do if f:GetName()==foldername then folder=f end end
 folder=folder or assert(mp:AddSubFolder(mp:GetRootFolder(),foldername));assert(mp:SetCurrentFolder(folder))
 local lookup={};for _,m in ipairs(folder:GetClipList()or{})do lookup[m:GetClipProperty('File Path')]=m end
 local paths={};for _,f in ipairs(cfg.files)do if not lookup[f.path]then paths[#paths+1]=f.path end end
 if #paths>0 then local imported=assert(mp:ImportMedia(paths));assert(#imported==#paths);for _,m in ipairs(imported)do lookup[m:GetClipProperty('File Path')]=m end end
 local first
 for _,ep in ipairs(cfg.episodes)do
  local name=string.format('大码_女版_EP%02d_新旁白原速测试_20261021',ep.episode)
  local t=byname[name] or assert(mp:CreateEmptyTimeline(name));assert(#(t:GetItemListInTrack('audio',1)or{})==0,'Existing test is not empty');assert(p:SetCurrentTimeline(t));assert(t:SetStartTimecode('00:00:00:00'))
  local fps=assert(tonumber(t:GetSetting('timelineFrameRate')),'Missing frame rate')
  assert(t:SetTrackName('audio',1,'新旁白100%原速_按原文顺序'))
  local cursor=0;local clips={}
  for seq,path in ipairs(ep.ordered_paths)do
   local m=assert(lookup[path]);local result=mp:AppendToTimeline({{mediaPoolItem=m,mediaType=2,trackIndex=1,recordFrame=cursor}})
   assert(result and #result==1 and result[1],'Append missing clip')
   local c=result[1];assert(c:GetMediaPoolItem():GetClipProperty('File Path')==path)
   local a=c:GetStart(true);local z=c:GetEnd(true);local d=c:GetDuration(true);local source_a=c:GetSourceStartTime();local source_z=c:GetSourceEndTime()
   assert(math.abs(a-cursor)<1,'Timeline order discontinuity')
   assert(c:GetLeftOffset()==0 and c:GetRightOffset()==0,'Unexpected source trimming')
   assert(math.abs(d/fps-(source_z-source_a))<0.04,'Unexpected speed change')
   assert(c:GetClipEnabled(),'Clip disabled')
   local row={sequence=seq,path=path,name=c:GetName(),start=a,['end']=z,duration_frames=d,source_start_seconds=source_a,source_end_seconds=source_z,source_speed_ratio=(source_z-source_a)/(d/fps),left=c:GetLeftOffset(),right=c:GetRightOffset(),properties=c:GetProperty()}
   clips[#clips+1]=row;cursor=z
  end
  assert(#(t:GetItemListInTrack('audio',1)or{})==ep.count)
  for i=1,t:GetTrackCount('video')do assert(#(t:GetItemListInTrack('video',i)or{})==0)end
  assert(t:GetTrackCount('subtitle')==0)
  report.episodes[#report.episodes+1]={episode=ep.episode,name=name,id=t:GetUniqueId(),count=#clips,fps=fps,duration_seconds=cursor/fps,clips=clips}
  assert(t:Export(cfg.base..'/备份/'..name..'.drt',resolve.EXPORT_DRT))
  if not first then first=t end
  write('原速测试_执行中.json',report);print('ORIGINAL_SPEED_TEST_EP',ep.episode,#clips,cursor/fps)
 end
 for _,v in ipairs(protected)do assert(p:SetCurrentTimeline(v.timeline));local ok,why=same(v.before,snapshot(v.timeline));assert(ok,'Formal timeline changed '..tostring(why))end
 report.formal_timelines_unchanged=true
 assert(p:SetCurrentTimeline(first));assert(first:SetCurrentTimecode('00:00:00:00'));resolve:OpenPage('edit')
 report.save_returned=pm:SaveProject();assert(report.save_returned)
 report.after_backup=cfg.base..'/备份/大码枕头_前三集新旁白原速测试已排好.drp';assert(pm:ExportProject(p:GetName(),report.after_backup))
 report.status='SAVED_PENDING_REOPEN';report.total_files=24;report.completed_at=os.date('%Y-%m-%dT%H:%M:%S')
 write('原速测试_创建结果.json',report);print('ORIGINAL_SPEED_TESTS_SAVED',report.save_returned)
end
local ok,err=xpcall(main,debug.traceback);if not ok then report.status='ERROR_INSPECT';report.error=err;write('原速测试_错误.json',report);print(err)end
'''
(b/'create_original_speed_test.lua').write_text('local cfg='+lua(config)+'\n'+helpers+script,encoding='utf8')
