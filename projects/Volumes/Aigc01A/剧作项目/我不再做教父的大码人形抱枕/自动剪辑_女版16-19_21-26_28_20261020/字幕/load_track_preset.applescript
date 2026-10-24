-- Native menu workflow. Run only after verifying the active timeline and ST track.
tell application id "com.blackmagic-design.DaVinciResolve" to activate
tell application "System Events"
 set resolveProcess to first process whose bundle identifier is "com.blackmagic-design.DaVinciResolve"
 set projectWindow to first window of resolveProcess whose name is "大码枕头"
 set inspectorGroup to first UI element of projectWindow whose role is "AXGroup"
 set presetButton to first UI element of inspectorGroup whose role is "AXMenuButton"
 perform action "AXShowMenu" of presetButton
 set presetEntry to missing value
 repeat with popupWindow in windows of resolveProcess
  if name of popupWindow is "" then
   repeat with popupChild in UI elements of popupWindow
    if role of popupChild is "AXMenu" then
     repeat with candidateEntry in UI elements of popupChild
      if name of candidateEntry is "九州海外短剧 Preset 字幕 Preset" then set presetEntry to contents of candidateEntry
     end repeat
    end if
   end repeat
  end if
 end repeat
 if presetEntry is missing value then error "Exact subtitle preset menu entry not found."
 try
  perform action "AXShowMenu" of presetEntry
 end try
 set loadEntry to missing value
 repeat with popupWindow in windows of resolveProcess
  if name of popupWindow is "" then
   set popupContents to entire contents of popupWindow
   repeat with candidateEntry in popupContents
    try
     if name of candidateEntry is "加载预设" then set loadEntry to contents of candidateEntry
    end try
   end repeat
  end if
 end repeat
 if loadEntry is missing value then error "Load Preset submenu entry not found."
 perform action "AXPress" of loadEntry
 return "Loaded: 九州海外短剧 Preset 字幕 Preset"
end tell
