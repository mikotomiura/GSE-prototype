-- 合成の打鍵のバーストを流す（手跡の小面の波紋の試作の計測用）。
-- 使い方: osascript synthetic-burst.applescript <バーストの数> <1 バーストの打鍵数> <間隔の秒> <止まる秒>
-- 前面のアプリ（TextEdit の新しい書類）に、a〜z を 1 文字ずつ打つ。
on run argv
	set nb to (item 1 of argv) as integer
	set per to (item 2 of argv) as integer
	set gap to (item 3 of argv) as real
	set pause to (item 4 of argv) as real
	set letters to "abcdefghijklmnopqrstuvwxyz"
	tell application "System Events"
		repeat with b from 1 to nb
			repeat with i from 1 to per
				keystroke (character (((i - 1) mod 26) + 1) of letters)
				delay gap
			end repeat
			delay pause
		end repeat
	end tell
end run
