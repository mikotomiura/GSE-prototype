#!/bin/bash
# 試し 3: テキストエディットの全画面の中でどける（判断 1）。
# 帯の試作を 40 秒動かし（12 秒目に隠す・27 秒目に戻す）、その間にテキストエディットを新しい書類で開いて全画面にする。
# 終わったら全画面を解き、保存せずに終了させる（もとは動いていなかったため）。
# 印には時刻と状態だけを書く。書類の中身は書かない（打鍵しない）。
set -u
STRIP="$1"; OUT="$2"; MARKS="$3"; shift 3
# 4 番目以降は帯の試作に渡す。無ければ run14・run15 と同じ引数。
ARGS=("$@"); [ ${#ARGS[@]} -eq 0 ] && ARGS=(--hide-at 12 --restore-at 27 --activate-first --restore-order)
mark() { echo "mark $(date +%s) $*" >> "$MARKS"; }
: > "$MARKS"
fs_state() { osascript -e 'tell application "System Events" to tell process "TextEdit" to get value of attribute "AXFullScreen" of window 1' 2>&1; }
hidden_state() { osascript -e 'tell application "System Events" to get visible of process "TextEdit"' 2>&1; }

mark start
"$STRIP" --duration 40 "${ARGS[@]}" > "$OUT" 2>&1 &
SP=$!
osascript -e 'tell application "TextEdit" to make new document' >/dev/null 2>&1
osascript -e 'tell application "TextEdit" to activate' >/dev/null 2>&1
sleep 2
mark "ax_windows=$(osascript -e 'tell application "System Events" to count windows of process "TextEdit"' 2>&1)"
osascript -e 'tell application "System Events" to tell process "TextEdit" to set value of attribute "AXFullScreen" of window 1 to true' >/dev/null 2>&1
mark fs_on_sent
sleep 4
mark "fs_state=$(fs_state)"
sleep 7   # 帯の試作の 12 秒目に隠す
mark "after_hide_textedit_visible=$(hidden_state)"
sleep 6
mark "mid_textedit_visible=$(hidden_state)"
sleep 6   # 27 秒目に戻す
mark "after_restore_textedit_visible=$(hidden_state) fs_state=$(fs_state)"
sleep 2
osascript -e 'tell application "System Events" to tell process "TextEdit" to set value of attribute "AXFullScreen" of window 1 to false' >/dev/null 2>&1
mark fs_off_sent
sleep 3
osascript -e 'tell application "TextEdit" to quit saving no' >/dev/null 2>&1
mark textedit_quit
wait $SP
mark end
