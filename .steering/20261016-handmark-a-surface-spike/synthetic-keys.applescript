-- 合成の打鍵を流す（手跡の小面の試作の遅れの計測用）。
-- 使い方: osascript synthetic-keys.applescript <回数> <間隔の秒>
-- 前面のアプリ（TextEdit の新しい書類）に、a〜z を 1 文字ずつ間を空けて打つ。
on run argv
	set n to (item 1 of argv) as integer
	set gap to (item 2 of argv) as real
	set letters to "abcdefghijklmnopqrstuvwxyz"
	tell application "System Events"
		repeat with i from 1 to n
			keystroke (character (((i - 1) mod 26) + 1) of letters)
			delay gap
		end repeat
	end tell
end run
