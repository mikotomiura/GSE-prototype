on run argv
	tell application "System Events" to tell process "gse-next"
		set w to (first window whose name is "gse-next")
		set allEls to entire contents of w
		repeat with e in allEls
			try
				if role of e is "AXButton" then
					set t to ""
					try
						set t to title of e
					end try
					try
						if t is "" or t is missing value then set t to description of e
					end try
					if t contains "開始" then
						if (count of argv) > 0 then click e
						return "found: " & t
					end if
				end if
			end try
		end repeat
	end tell
	return "not found"
end run
