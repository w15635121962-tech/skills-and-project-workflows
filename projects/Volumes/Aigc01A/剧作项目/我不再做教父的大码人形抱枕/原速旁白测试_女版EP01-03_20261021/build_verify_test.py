from pathlib import Path
import json
b=Path(__file__).resolve().parent
x=json.loads((b/'原速测试_创建结果.json').read_text(encoding='utf8'))
def lua(x):
 if x is None:return 'nil'
 if isinstance(x,bool):return str(x).lower()
 if isinstance(x,(int,float)):return repr(x)
 if isinstance(x,str):return json.dumps(x,ensure_ascii=False)
 if isinstance(x,list):return '{'+','.join(lua(v)for v in x)+'}'
 return '{'+','.join('['+lua(str(k))+']='+lua(v)for k,v in x.items())+'}'
helpers=Path('替换旁白_女版EP01-03_20261021/native_template.lua').read_text(encoding='utf8').split("local report={status='STARTED_NATIVE'")[0]
script='''
local pm=resolve:GetProjectManager();local p=pm:GetCurrentProject();assert(p:GetName()==expected.project);assert(pm:SaveProject());assert(pm:CloseProject(p));p=assert(pm:LoadProject(expected.project))
local ids={};for i=1,p:GetTimelineCount()do local t=p:GetTimelineByIndex(i);ids[t:GetUniqueId()]=t end
local out={status='REOPENED_VERIFIED',project=p:GetName(),speed_percent=100,tempo_processing=false,episodes={},formal_timelines_unchanged=true,checked_at=os.date('%Y-%m-%dT%H:%M:%S')}
local first
for _,e in ipairs(expected.episodes)do
 local t=assert(ids[e.id]);assert(t:GetName()==e.name);assert(p:SetCurrentTimeline(t));local cs=t:GetItemListInTrack('audio',1);assert(#cs==e.count)
 local cursor=0;local rows={}
 for i,c in ipairs(cs)do
  local want=e.clips[i];local a=c:GetStart(true);local z=c:GetEnd(true);local d=c:GetDuration(true);local source_a=c:GetSourceStartTime();local source_z=c:GetSourceEndTime();local props=c:GetProperty()
  assert(c:GetMediaPoolItem():GetClipProperty('File Path')==want.path,'wrong source/order');assert(want.path:sub(-4)=='.mp3','not original MP3');assert(math.abs(a-cursor)<0.001,'gap or overlap');assert(math.abs(d-want.duration_frames)<0.001)
  assert(c:GetLeftOffset()==0 and c:GetRightOffset()==0,'trimmed clip');assert(math.abs((source_z-source_a)/(d/e.fps)-1)<0.00001,'not original speed')
  local ok,why=same(props,want.properties);assert(ok,'property change '..tostring(why));rows[#rows+1]={sequence=i,path=want.path,start=a,['end']=z,duration_seconds=d/e.fps,source_duration_seconds=source_z-source_a,source_speed_ratio=(source_z-source_a)/(d/e.fps),full_untrimmed_source=true}
  cursor=z
 end
 out.episodes[#out.episodes+1]={episode=e.episode,name=e.name,id=e.id,count=#rows,fps=e.fps,duration_seconds=cursor/e.fps,clips=rows}
 if not first then first=t end
end
for _,old in ipairs(expected.protected_before)do local t=assert(ids[old.id]);assert(p:SetCurrentTimeline(t));local ok,why=same(old,snapshot(t));assert(ok,'Formal timeline changed '..tostring(why))end
assert(p:SetCurrentTimeline(first));assert(first:SetCurrentTimecode('00:00:00:00'));resolve:OpenPage('edit');out.save_returned=pm:SaveProject();assert(out.save_returned)
write('原速测试_保存重开核验.json',out);print('ORIGINAL_SPEED_REOPEN_VERIFIED',#out.episodes,24,out.save_returned)
'''
(b/'verify_original_speed_tests.lua').write_text('local cfg='+lua({'base':str(b)})+'\nlocal expected='+lua(x)+'\n'+helpers+script,encoding='utf8')
print('source speed ratios',min(c['source_speed_ratio']for e in x['episodes']for c in e['clips']),max(c['source_speed_ratio']for e in x['episodes']for c in e['clips']))
