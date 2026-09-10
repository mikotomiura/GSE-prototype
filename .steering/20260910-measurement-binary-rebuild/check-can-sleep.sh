#!/usr/bin/env bash
# ★ 「この Mac はいま寝られるか」を寝かせる**前**に見るゲート。
#
# ⚠️★★★ なぜ要るか: 2026-09-10 に **蓋を 16 分閉じたのに寝なかった**（★ 実測）。
#   ★ feat が 13:15:00〜13:33:19 に 1,100 行・最大の穴 1 秒 ＝ 960 秒の閉蓋中も回り続けていた。
#   ⚠️ 閉蓋中ずっと coreaudiod / AirPlayXPCHelper が PreventUserIdleSystemSleep を握っていた。
#   → ★ **寝かせてから「寝なかった」と分かるのでは遅い**（★ 16 分と 1 回の検証機会を失う）。
set -uo pipefail
RC=0
echo "════════════════════════════════════════"
echo "★ いま sleep を止めているもの"
HOLD=$(pmset -g assertions 2>/dev/null | grep -E "^\s+pid [0-9]+\(" \
       | grep -E "PreventUserIdleSystemSleep|NoIdleSleepAssertion|PreventSystemSleep")

# ⚠️ powerd の「画面が点いている間」は蓋を閉じれば消えるので**除外する**（★ 誤検出になる）
REAL=$(printf '%s\n' "$HOLD" | grep -v "Powerd - Prevent sleep while display is on")

if [ -z "$(printf '%s' "$REAL" | tr -d '[:space:]')" ]; then
  echo "  ★ 何も握っていない → ★ 蓋を閉じれば寝るはず"
else
  printf '%s\n' "$REAL" | sed 's/^/  ⚠️ /' | cut -c1-150
  RC=3
fi

echo "── ★ 種類別の対処"
printf '%s\n' "$REAL" | grep -q "caffeinate" && {
  echo "  ⚠️ caffeinate: ★ **Claude Code が握っており、殺しても復活する**"
  echo "     → ★ **Claude Code を終了すること**（⚠️ 私からは外せない）"; }
printf '%s\n' "$REAL" | grep -qE "\(Claude\)|Electron" && {
  echo "  ⚠️ Claude デスクトップ (Electron NoIdleSleepAssertion) → ★ **アプリを終了すること**"; }
printf '%s\n' "$REAL" | grep -qE "coreaudiod|AirPlay|Media Playback|WebKit" && {
  echo "  ⚠️★★★ **音声 / メディア再生** —— ★ 2026-09-10 に**実際にこれで寝なかった**"
  echo "     → ★ Safari / 音楽 / 会議アプリの再生を止め、AirPlay 出力を切ること"; }

echo "── ★ 電源と設定（⚠️ AC 接続だと sleep=0 ＝ 自動では寝ない）"
pmset -g batt 2>/dev/null | head -1 | sed 's/^/  /'
SRC=$(pmset -g batt 2>/dev/null | head -1 | grep -q "AC Power" && echo "AC Power" || echo "Battery Power")
echo "  ★ 現在の電源: $SRC / sleep 設定: $(pmset -g custom 2>/dev/null | awk -v s="$SRC:" '$0 ~ s {f=1} f && $1=="sleep" {print $2; exit}') 分"

echo "── ★ 直前の GSE"
if pgrep -x gse-next > /dev/null; then
  echo "  ★ 生存 pid=$(pgrep -x gse-next)"
else
  echo "  ⚠️★★★ gse-next が居ない → ★ 寝かせても検証にならない"; RC=4
fi
echo "════════════════════════════════════════"
if [ "$RC" -eq 0 ]; then
  echo "✅ ★ 寝られる見込み。→ ★ 蓋を閉じて 5 分以上待つこと。"
else
  echo "⚠️★★★ **このまま寝かせても寝ない見込み (rc=$RC)。上の ⚠️ を潰してから閉じること。**"
fi
exit $RC
