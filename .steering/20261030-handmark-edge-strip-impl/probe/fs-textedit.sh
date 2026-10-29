#!/bin/bash
# テキストエディットを新しい書類で開いて全画面にし、$1 秒そのままにしてから全画面を解いて保存せずに終了する。
# 起動中なら中止する（既存の書類を失わないため）。印は $2 に時刻と状態だけを書く（打鍵しない）。
set -u
HOLD="$1"; MARKS="$2"
if pgrep -x TextEdit >/dev/null; then echo "TextEdit is already running; abort" >&2; exit 2; fi
mark() { echo "mark $(date +%s) $*" >> "$MARKS"; }
fs_state() { osascript -e 'tell application "System Events" to tell process "TextEdit" to get value of attribute "AXFullScreen" of window 1' 2>&1; }
mark start
osascript -e 'tell application "TextEdit" to make new document' >/dev/null 2>&1
osascript -e 'tell application "TextEdit" to activate' >/dev/null 2>&1
sleep 2
osascript -e 'tell application "System Events" to tell process "TextEdit" to set value of attribute "AXFullScreen" of window 1 to true' >/dev/null 2>&1
mark fs_on_sent
sleep 4
mark "fs_state=$(fs_state)"
sleep "$HOLD"
mark "fs_state_before_off=$(fs_state)"
osascript -e 'tell application "System Events" to tell process "TextEdit" to set value of attribute "AXFullScreen" of window 1 to false' >/dev/null 2>&1
mark fs_off_sent
sleep 3
osascript -e 'tell application "TextEdit" to quit saving no' >/dev/null 2>&1
mark textedit_quit
