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

# ⚠️★★★ **最初にこれを見る。** ★ 2026-09-10 に 2 回スリープ検証を潰した真因である。
#   ★ `SleepDisabled 1` は `sudo pmset disablesleep 1` の設定で、
#   ⚠️ **assertion と無関係に、蓋を閉じても含めてスリープを全面的に無効化する**。
#   ★ 実測: この Mac は `kern.waketime = 0`（★ 2026-07-26 の起動以来 **46 日間 1 度も寝ていない**）、
#     閉蓋 16 分 / 5 分でも NDJSON の穴は最大 1 秒だった。
#   ⚠️★★ **私は 2 回とも「音声が妨害している」と書いた。** ★ 妨害者は列挙できていたのに、
#     **その上位にある system 設定を 1 度も見なかった** —— ⚠️ 順序を間違えると、
#     潰しても潰しても寝ない理由が分からないまま時間だけ溶ける。
echo "★ system 設定 (⚠️ assertion より先に効く)"
SD=$(pmset -g 2>/dev/null | awk '/SleepDisabled/ {print $2}')
case "${SD:-}" in
  1)
    echo "  ⚠️★★★ **SleepDisabled = 1** ＝ ★ **この Mac はそもそも寝ない設定である**"
    echo "     → ★ 解除 (⚠️ sudo が要る。私からは実行できない):"
    echo "          sudo pmset -a disablesleep 0"
    echo "     ★ 解除できたか:  pmset -g | grep SleepDisabled   → 0 になること"
    RC=3 ;;
  0)
    echo "  ★ SleepDisabled = 0（★ 寝られる設定）" ;;
  *)
    echo "  ⚠️ SleepDisabled を読めない (値=[${SD:-空}]) → ★ **判定しない**"
    [ "$RC" -eq 0 ] && RC=1 ;;
esac

echo "★ いま sleep を止めているもの"
HOLD=$(pmset -g assertions 2>/dev/null | grep -E "^\s+pid [0-9]+\(" \
       | grep -E "PreventUserIdleSystemSleep|NoIdleSleepAssertion|PreventSystemSleep")

# ⚠️ powerd の「画面が点いている間」は蓋を閉じれば消えるので**除外する**（★ 誤検出になる）
REAL=$(printf '%s\n' "$HOLD" | grep -v "Powerd - Prevent sleep while display is on")

# ⚠️★★★ 2026-09-10 改訂 —— ★ 一律に赤くすると **永久に rc=0 にならない**。
#   ★ 実際、`sharingd (Handoff)` だけで赤になり進めなくなった。
#   ⚠️ だが「Handoff は無害」を**私は実証していない**。→ ★ **緑にもしない。**
#   → ★ 3 段に分ける:
#      ① 何も握っていない            → rc=0（★ 寝るはず）
#      ② **実測で寝させなかったもの** → rc=3（⚠️ 潰してから閉じる）
#      ③ それ以外（効果が未知）      → rc=1（★ **試してよい**が、寝なかったらこれを疑う）
#   ⚠️ ②の根拠は 2026-09-10 の実測のみ:
#      閉蓋 16 分のあいだ coreaudiod / AirPlayXPCHelper / Safari の HTMLMediaElement が
#      握り続け、★ feat は 1 Hz で回り続けた（＝ 一度も寝ていない）。
#      ★ caffeinate / Claude(Electron) は **pkill しても復活する**ので同格に置く。
KNOWN_BLOCKERS='caffeinate|\(Claude\)|Electron|coreaudiod|AirPlay|Media Playback|WebKit'

if [ -z "$(printf '%s' "$REAL" | tr -d '[:space:]')" ]; then
  echo "  ★ 何も握っていない → ★ 蓋を閉じれば寝るはず"
else
  BLOCK=$(printf '%s\n' "$REAL" | grep -E "$KNOWN_BLOCKERS")
  OTHER=$(printf '%s\n' "$REAL" | grep -vE "$KNOWN_BLOCKERS")
  if [ -n "$(printf '%s' "$BLOCK" | tr -d '[:space:]')" ]; then
    echo "  ⚠️★★★ **実測で寝させなかったもの**:"
    printf '%s\n' "$BLOCK" | sed 's/^/    ⚠️ /' | cut -c1-150
    RC=3
  fi
  if [ -n "$(printf '%s' "$OTHER" | tr -d '[:space:]')" ]; then
    echo "  ⚠️ 効果が**未知**のもの（★ 実証していない）:"
    printf '%s\n' "$OTHER" | sed 's/^/    ・/' | cut -c1-150
    [ "$RC" -eq 0 ] && RC=1
  fi
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
case "$RC" in
  0) echo "✅ ★ 寝られる見込み。→ ★ 蓋を閉じて 5 分以上待つこと。" ;;
  1) echo "⚠️ ★ **試してよい (rc=1)。** ★ 既知の妨害は無い。"
     echo "   ⚠️ ただし上の「効果が未知のもの」が握っている。→ ★ 蓋を閉じて 5 分以上待ち、"
     echo "   ★ 寝ていなければ (post-wake-check.sh の項目 4 で穴が開いていなければ) それを疑う。" ;;
  *) echo "⚠️★★★ **このまま寝かせても寝ない見込み (rc=$RC)。上の ⚠️ を潰してから閉じること。**" ;;
esac
exit $RC
