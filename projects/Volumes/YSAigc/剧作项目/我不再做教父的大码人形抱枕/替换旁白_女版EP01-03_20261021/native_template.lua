local function esc(s) return '"'..s:gsub('[%z\1-\31\\"]',function(c) if c=='"' then return '\\"' elseif c=='\\' then return '\\\\' else return string.format('\\u%04x',string.byte(c)) end end)..'"' end
local function json(v)
 local t=type(v)
 if t=='nil' then return 'null' elseif t=='boolean' or t=='number' then return tostring(v) elseif t=='string' then return esc(v) end
 if t~='table' then return esc(tostring(v)) end
 local n=0; local arr=true; for k,_ in pairs(v) do n=n+1; if type(k)~='number' then arr=false end end
 if arr and #v==n then local a={};for i=1,n do a[i]=json(v[i]) end;return '['..table.concat(a,',')..']' end
 local keys={};for k,_ in pairs(v) do keys[#keys+1]=k end;table.sort(keys,function(a,b)return tostring(a)<tostring(b) end)
 local a={};for _,k in ipairs(keys)do a[#a+1]=esc(tostring(k))..':'..json(v[k]) end;return '{'..table.concat(a,',')..'}'
end
local function write(name,v) local f=assert(io.open(cfg.base..'/'..name,'w'));f:write(json(v));f:close() end
local function same(a,b,path)
 path=path or ''
 if type(a)~=type(b) then return false,path..' type' end
 if type(a)=='number' then return math.abs(a-b)<0.000001,path end
 if type(a)~='table' then return a==b,path end
 for k,v in pairs(a)do local ok,why=same(v,b[k],path..'.'..tostring(k));if not ok then return false,why end end
 for k,_ in pairs(b)do if a[k]==nil then return false,path..'.extra '..tostring(k) end end
 return true
end
local function item(c)
 local m=c:GetMediaPoolItem()
 return {name=c:GetName(),start=c:GetStart(),['end']=c:GetEnd(),left=c:GetLeftOffset(),right=c:GetRightOffset(),enabled=c:GetClipEnabled(),source_start=c:GetSourceStartTime(),source_end=c:GetSourceEndTime(),media_id=m and m:GetMediaId(),properties=c:GetProperty()}
end
local function snapshot(t)
 local s={name=t:GetName(),id=t:GetUniqueId(),start=t:GetStartFrame(),['end']=t:GetEndFrame(),fps=t:GetSetting('timelineFrameRate'),tracks={}}
 for _,kind in ipairs({'video','audio','subtitle'})do
  s.tracks[kind]={}
  for i=1,t:GetTrackCount(kind)do
   local tr={index=i,name=t:GetTrackName(kind,i),enabled=t:GetIsTrackEnabled(kind,i),locked=t:GetIsTrackLocked(kind,i),items={}}
   for _,c in ipairs(t:GetItemListInTrack(kind,i) or {})do tr.items[#tr.items+1]=item(c) end
   s.tracks[kind][i]=tr
  end
 end
 return s
end
local function outside(s)
 local o={start=s.start,['end']=s['end'],fps=s.fps,tracks={}}
 for kind,trs in pairs(s.tracks)do
  o.tracks[kind]={}
  for i,tr in ipairs(trs)do
   local t={index=tr.index,name=tr.name,enabled=tr.enabled,locked=tr.locked,items=tr.items}
   if kind=='audio' and i==4 then t.items={} end
   o.tracks[kind][i]=t
  end
 end
 return o
end
local report={status='STARTED_NATIVE',episodes={},events={}}
local function main()
 local pm=assert(resolve:GetProjectManager());local p=assert(pm:GetCurrentProject());assert(p:GetName()=='大码枕头');local mp=p:GetMediaPool()
 report.project=p:GetName();report.timeline_count_before=p:GetTimelineCount()
 local existing={};local names={}
 for i=1,p:GetTimelineCount()do local t=p:GetTimelineByIndex(i);existing[t:GetUniqueId()]=t;names[t:GetName()]=t end
 local folder
 for _,f in ipairs(mp:GetRootFolder():GetSubFolderList() or {})do if f:GetName()=='前3集_新对标旁白_20261021' then folder=f end end
 folder=folder or assert(mp:AddSubFolder(mp:GetRootFolder(),'前3集_新对标旁白_20261021'));assert(mp:SetCurrentFolder(folder))
 local lookup={};for _,c in ipairs(folder:GetClipList() or {})do lookup[c:GetClipProperty('File Path')]=c end
 local paths={};for _,c in ipairs(cfg.clips)do if not lookup[c.path] then paths[#paths+1]=c.path end end
 if #paths>0 then local imported=assert(mp:ImportMedia(paths));assert(#imported==#paths,'import count');for _,c in ipairs(imported)do lookup[c:GetClipProperty('File Path')]=c end end
 report.imported_media_count=#paths
 local working={}
 for _,old in ipairs(cfg.timelines)do
  local orig=assert(existing[old.id]);assert(orig:GetName()==old.name,'original name changed');assert(orig:GetStartFrame()==old.start and orig:GetEndFrame()==old['end'],'original duration changed')
  local clips=orig:GetItemListInTrack('audio',4) or {};assert(#clips==#old.old_clips,'old clip count')
  for i,c in ipairs(clips)do local oc=old.old_clips[i];assert(c:GetUniqueId()==oc.id and c:GetStart()==oc.start and c:GetEnd()==oc['end'],'old clip changed') end
  assert(p:SetCurrentTimeline(orig));assert(p:GetCurrentTimeline():GetUniqueId()==orig:GetUniqueId());local before=snapshot(orig)
  local workname=old.name..'_新旁白对齐_20261021';local work=names[workname] or assert(orig:DuplicateTimeline(workname));assert(p:SetCurrentTimeline(work));assert(p:GetCurrentTimeline():GetUniqueId()==work:GetUniqueId())
  local ok,why=same(outside(before),outside(snapshot(work)));assert(ok,'duplicate changed '..tostring(why))
  local locked=work:GetIsTrackLocked('audio',4);if locked then assert(work:SetTrackLock('audio',4,false)) end
  assert(work:DeleteClips(work:GetItemListInTrack('audio',4),false),'delete work A4 failed')
  local rows={};for _,c in ipairs(cfg.clips)do if c.episode==old.ep then rows[#rows+1]=c end end;table.sort(rows,function(a,b)return a.record_start_frame<b.record_start_frame end)
  local addeditems={}
  for i,e in ipairs(rows)do
   local media=assert(lookup[e.path],'missing WAV');local result=mp:AppendToTimeline({{mediaPoolItem=media,recordFrame=e.record_start_frame,trackIndex=4,mediaType=2}})
   assert(result and result[1],'append returned no clip '..i)
   local c=result[1];assert(c:GetStart()==e.record_start_frame and c:GetEnd()==e.record_end_frame_exclusive,'append slot mismatch '..i..' '..tostring(c:GetStart())..' '..tostring(c:GetEnd()))
   local oldclip=old.old_clips[i];local props=c:GetProperty()
   for k,v in pairs(oldclip.properties)do if props[k]~=v then assert(c:SetProperty(k,v),'set property '..k) end end
   if c:GetClipEnabled()~=oldclip.enabled then assert(c:SetClipEnabled(oldclip.enabled)) end
   local propsok,pwhy=same(c:GetProperty(),oldclip.properties);assert(propsok,'clip props '..tostring(pwhy))
   assert(c:GetMediaPoolItem():GetClipProperty('File Path')==e.path)
   addeditems[#addeditems+1]=item(c)
  end
  if locked then assert(work:SetTrackLock('audio',4,true)) end
  local after=snapshot(work);ok,why=same(outside(before),outside(after));assert(ok,'outside narration changed '..tostring(why))
  assert(#after.tracks.audio[4].items==#rows)
  local row={episode=old.ep,old_id=orig:GetUniqueId(),working_id=work:GetUniqueId(),original_name=old.name,working_name=workname,new_clips=addeditems,after=after,picture_subtitles_other_audio_unchanged=true,all_record_slots_unchanged=true}
  report.episodes[#report.episodes+1]=row;working[#working+1]={orig=orig,work=work,name=old.name,row=row}
  write('原生Lua_执行回读.json',report);print('NARRATION_READY_EP',old.ep,#addeditems)
 end
 for _,v in ipairs(working)do
  local backup=v.name..'_旧旁白备份_20261021';assert(not names[backup]);assert(v.orig:SetName(backup));assert(v.work:SetName(v.name))
  assert(v.work:Export(cfg.base..'/备份/'..v.name..'_新旁白已替换.drt',resolve.EXPORT_DRT))
  v.row.backup_timeline=backup;v.row.final_timeline=v.name
 end
 assert(p:SetCurrentTimeline(working[1].work));assert(working[1].work:SetCurrentTimecode('00:00:00:00'))
 report.save_returned=pm:SaveProject();assert(report.save_returned,'native save false')
 report.backup=cfg.base..'/备份/大码枕头_前3集新旁白已替换.drp';assert(pm:ExportProject(p:GetName(),report.backup))
 report.status='REPLACED_NATIVE_PENDING_REOPEN_QC';report.timeline_count_after=p:GetTimelineCount();report.source_files=24;report.timeline_clips=42;report.completed_at=os.date('%Y-%m-%dT%H:%M:%S')
 write('前三集_替换后原生回读.json',report);print('NARRATION_REPLACEMENT_COMPLETE',report.save_returned)
end
local ok,err=xpcall(main,debug.traceback)
if not ok then report.status='FAILED_NATIVE_INSPECT';report.error=err;write('原生Lua_执行错误.json',report);print(err) end
