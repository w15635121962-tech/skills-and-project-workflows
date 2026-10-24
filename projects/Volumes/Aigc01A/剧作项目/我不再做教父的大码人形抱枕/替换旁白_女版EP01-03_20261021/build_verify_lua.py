from pathlib import Path
import json
b=Path(__file__).resolve().parent
exec((b/'build_native_lua.py').read_text().split("(b/'apply_narration_replacement.lua').write_text")[0])
x=json.loads((b/'前三集_替换后原生回读.json').read_text())
helpers=(b/'native_template.lua').read_text().split("local report={status='STARTED_NATIVE'")[0]
code='local cfg='+lua({'base':str(b)})+'\nlocal expected='+lua(x)+'\n'+helpers+'''\nlocal pm=resolve:GetProjectManager();local p=pm:GetCurrentProject();assert(p:GetName()==expected.project)
assert(pm:SaveProject());assert(pm:CloseProject(p));p=assert(pm:LoadProject(expected.project));assert(p:GetName()==expected.project)
local out={status='REOPENED_VERIFIED',project=p:GetName(),timeline_count=p:GetTimelineCount(),episodes={},checked_at=os.date('%Y-%m-%dT%H:%M:%S')}
local first
for _,ep in ipairs(expected.episodes)do
 local t
 for i=1,p:GetTimelineCount()do local a=p:GetTimelineByIndex(i);if a:GetUniqueId()==ep.working_id then t=a end end
 assert(t and t:GetName()==ep.final_timeline);assert(p:SetCurrentTimeline(t));assert(p:GetCurrentTimeline():GetUniqueId()==ep.working_id)
 local live=snapshot(t);local ok,why=same(outside(live),outside(ep.after));assert(ok,'Outside changed on reopen '..tostring(why))
 ok,why=same(live.tracks.audio[4],ep.after.tracks.audio[4]);assert(ok,'VO changed on reopen '..tostring(why))
 local details={}
 for _,c in ipairs(t:GetItemListInTrack('audio',4))do details[#details+1]={start=c:GetStart(true),['end']=c:GetEnd(true),duration=c:GetDuration(true),path=c:GetMediaPoolItem():GetClipProperty('File Path'),online=c:GetMediaPoolItem():GetClipProperty('Offline')} end
 out.episodes[#out.episodes+1]={episode=ep.episode,name=t:GetName(),id=t:GetUniqueId(),all_other_editing_unchanged=true,narration_slots_unchanged=true,subtitle_count=#live.tracks.subtitle[1].items,narration_count=#details,narration=details,after=live}
 if not first then first=t end
end
assert(p:SetCurrentTimeline(first));assert(first:SetCurrentTimecode('00:00:01:00'));resolve:OpenPage('edit');out.saved_after_reopen=pm:SaveProject();assert(out.saved_after_reopen)
write('前三集_保存重开核验.json',out);print('REOPEN_VERIFIED_42_VO_117_SUBTITLES',out.saved_after_reopen)
'''
(b/'verify_saved_reopen.lua').write_text(code)
