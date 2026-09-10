#!/usr/bin/env bash
# ⚠️★★★ **計測に使う .app が「思っている版」で「思っている診断を持つ」かを検査する。**
#
# ★ なぜ要るか（2026-09-10 の実害）:
#   ⚠️ 引き継ぎは「診断 `tap_enabled` を入れたので**次の Down のログで機序が決着する**」と
#   決めていたが、★ 走っていたバイナリは **v0.1.31（09-03 ビルド）**で、
#   診断が入ったのは **`cb1aa25`（09-05）**だった。→ ⚠️ **3 回の Down を無駄にした。**
#   ★ memory `gate-green-but-artifact-broken` の②「**版が新しい ≠ 機能が入っている**」と同型。
#
# ★ 使い方:
#   bash scripts/check-measurement-binary.sh [/path/to/gse-next.app]
#   （★ 既定は ~/Desktop/O1_計測用_macOS/gse-next.app）
#
# ★ 終了コード: 0=健全 / 3=版ずれ or 診断欠落 / 2=対象が無い・読めない
set -euo pipefail

APP="${1:-$HOME/Desktop/O1_計測用_macOS/gse-next.app}"
BIN="$APP/Contents/MacOS/gse-next"
PLIST="$APP/Contents/Info.plist"

fail=0
say() { printf '  %s\n' "$1"; }

echo "════════════════════════════════════════"
echo "★ 対象: $APP"

# ⚠️ 不在は「0 件」ではなく「測れない」。★ 黙って緑にしない。
if [ ! -x "$BIN" ]; then
  echo "⚠️★★★ 実行ファイルが無い / 実行できない: $BIN"
  echo "   → ★ **判定しない**（⚠️ 「診断が入っている」とは書かないこと）。"
  exit 2
fi

# ── ① 版 ─────────────────────────────────────────────
want="$(sed -n 's/^version[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' src-tauri/Cargo.toml | head -1)"
got="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$PLIST" 2>/dev/null || echo '')"
echo "── ① 版"
say "repo (src-tauri/Cargo.toml): ${want:-⚠️ 読めない}"
say "app  (CFBundleShortVersionString): ${got:-⚠️ 読めない}"
if [ -z "$want" ] || [ -z "$got" ]; then
  say "⚠️ どちらかが読めない → 判定しない"; fail=1
elif [ "$want" != "$got" ]; then
  say "⚠️★★★ **版がずれている**（★ repo の方が新しいなら、直したはずの修正が入っていない）"; fail=1
else
  say "★ 一致"
fi
say "★ ビルド時刻: $(stat -f '%Sm' -t '%Y-%m-%d %H:%M' "$BIN" 2>/dev/null || echo '?')"

# ── ② 診断の実在（⚠️ 陽性対照つき） ─────────────────────
# ⚠️★★ **`strings` で 0 件でも「無い」とは限らない**（★ release ビルドに関数名は残らない）。
#   → ★ **同じ経路でログに出ることが分かっている文字列**を陽性対照に置き、
#     ⚠️ **それらが出ることを先に確かめてから**、目的の文字列の不在を主張する。
CONTROLS="starved_ms rehook_requested tap_mode input_monitoring"
# ★ 探したい診断（★ 増やすならここ）。⚠️ 実行時に連結して作る ——
#   memory `gate-green-but-artifact-broken` の④「**対照文字列を検査対象に書くと自己参照で空回り**」。
WANTED="$(printf 'tap%s' '_enabled')"

echo "── ② 診断の実在（★ 陽性対照つき）"
ctl_ok=0; ctl_n=0
for s in $CONTROLS; do
  n="$(strings "$BIN" 2>/dev/null | grep -cF "$s" || true)"
  ctl_n=$((ctl_n + 1)); [ "${n:-0}" -gt 0 ] && ctl_ok=$((ctl_ok + 1))
  say "陽性対照 $(printf '%-18s' "$s") : ${n:-0}"
done
if [ "$ctl_ok" -lt "$ctl_n" ]; then
  say "⚠️★★★ **陽性対照が欠けている** → ★ この検査自体が信用できない。**判定しない**。"
  echo "════════════════════════════════════════"
  exit 2
fi
say "★ 陽性対照 $ctl_ok/$ctl_n → ★ strings は機能している"
for s in $WANTED; do
  n="$(strings "$BIN" 2>/dev/null | grep -cF "$s" || true)"
  if [ "${n:-0}" -gt 0 ]; then
    say "★ 診断 $s : ${n} 件 → ★ 入っている"
  else
    say "⚠️★★★ 診断 $s : **0 件** → ⚠️ **このバイナリでは機序を追えない**"
    fail=1
  fi
done

# ── ③ 稼働中のログとの照合（★ あれば） ───────────────────
echo "── ③ 稼働中の NDJSON との照合"
ND="$(ls -t "$HOME"/Documents/GSE-sessions/gse_o1_*.ndjson 2>/dev/null | head -1 || true)"
if [ -z "$ND" ]; then
  say "★ O1 の NDJSON が無い → ★ 照合は省略（⚠️ 「一致した」とは書かない）"
else
  # ⚠️ 中身は読まない。★ meta 行の app_version だけを取る。
  av="$(python3 -c "
import json,sys
for line in open(sys.argv[1], encoding='utf-8', errors='replace'):
    o = json.loads(line)
    if o.get('type') == 'meta':
        print(o.get('app_version','')); break
" "$ND" 2>/dev/null || echo '')"
  say "$(basename "$ND") の meta.app_version: ${av:-⚠️ 取れない}"
  if [ -n "$av" ] && [ -n "$got" ] && [ "$av" != "$got" ]; then
    say "⚠️★★ **走っているのは別の版**（★ .app を差し替えたのに GSE を再起動していない可能性）"
    fail=1
  elif [ -n "$av" ]; then
    say "★ 一致（★ **これが「その版が走っている」ことの一次資料**）"
  fi
fi

echo "════════════════════════════════════════"
if [ "$fail" -eq 0 ]; then
  echo "✅ ★ 計測用バイナリは健全"
else
  echo "⚠️★★★ **計測用バイナリに問題がある。上の ⚠️ を潰してから測ること。**"
  exit 3
fi
