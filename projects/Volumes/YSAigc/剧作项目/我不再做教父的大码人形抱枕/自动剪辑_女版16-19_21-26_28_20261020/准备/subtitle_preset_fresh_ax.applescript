property resolveBundleID : "com.blackmagic-design.DaVinciResolve"
property presetName : "九州海外短剧 Preset 字幕 Preset"

-- Code delivery only. Compile does not execute these UI actions.
on pressFreshMenuItem(itemName, actionName, parentName)
	set bundleID to my resolveBundleID
	repeat 40 times
		tell application "System Events"
			tell (first application process whose bundle identifier is bundleID)
				set windowCount to count of windows
				repeat with wi from 1 to windowCount
					try
						if (name of window wi) is "" then
							if exists (menu item itemName of menu 1 of window wi) then
								perform action actionName of menu item itemName of menu 1 of window wi
								return true
							end if
							if parentName is not "" then
								if exists (menu item itemName of menu 1 of menu item parentName of menu 1 of window wi) then
									perform action actionName of menu item itemName of menu 1 of menu item parentName of menu 1 of window wi
									return true
								end if
							end if
						end if
					end try
				end repeat
			end tell
		end tell
		delay 0.05
	end repeat
	return false
end pressFreshMenuItem

-- Start with the options menu closed; the ST/Track Inspector must already be selected.
set bundleID to my resolveBundleID
tell application "System Events"
	tell (first application process whose bundle identifier is bundleID)
		set frontmost to true
	end tell
end tell
delay 0.1
tell application "System Events"
	tell (first application process whose bundle identifier is bundleID)
		-- Use the actual already-verified main window/group/button path if different.
		perform action "AXShowMenu" of first menu button of group 1 of window "大码枕头"
	end tell
end tell
if not my pressFreshMenuItem(my presetName, "AXShowMenu", "") then error "Preset parent menu item was not activated."
if not my pressFreshMenuItem("加载预设", "AXPress", my presetName) then error "Load Preset was not activated."
return "Load Preset action returned; independently verify the Track Inspector and saved timeline."

