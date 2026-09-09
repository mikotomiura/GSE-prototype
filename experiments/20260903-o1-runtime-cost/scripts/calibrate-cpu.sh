#!/usr/bin/env bash
# ⚠️★★★ **CPU% の測定器そのものを校正する。**
#
# ★ なぜ要るか: 2026-09-10 に、macOS サンプラが使っていた `top -l 2` が
#   **1 コアを飽和させたプロセスを 47.6 % と報告する**ことを実測した
#   （★ 地上真実は 99.7 %）。⚠️ 8 時間 × 2 本の macOS 実測が**すべて約 2.08 倍
#   過小報告**されていたことになる。→ ★ 測定器は使う前に陽性対照で校正する。
#
# ★ 使い方:  bash scripts/calibrate-cpu.sh
#   ⚠️ 15 秒ほど 1 コアを 100 % 使う（★ 終わったら必ず止める）。
set -euo pipefail

echo "★ 論理プロセッサ数: $(sysctl -n hw.logicalcpu 2>/dev/null || nproc 2>/dev/null || echo '?')"

# ★ 陽性対照: 単一スレッドで 1 コアを飽和させる（⚠️ GIL があるので 1 コアぶんちょうど）
python3 -c 'while True: pass' &
SPIN=$!
trap 'kill "$SPIN" 2>/dev/null || true' EXIT
sleep 5

# ★ 地上真実: CPU 時間の増分 / 実時間（⚠️ top にも ps %cpu にも依存しない）
c0=$(ps -o cputime= -p "$SPIN" | tr -d ' '); t0=$(date +%s)
sleep 8
c1=$(ps -o cputime= -p "$SPIN" | tr -d ' '); t1=$(date +%s)
truth=$(python3 - "$c0" "$c1" "$((t1 - t0))" <<'PY'
import sys
def sec(s):
    p = s.split(':')
    return int(p[0]) * 60 + float(p[1]) if len(p) == 2 else float(p[0])
print(f"{100 * (sec(sys.argv[2]) - sec(sys.argv[1])) / float(sys.argv[3]):.1f}")
PY
)
echo "★ 地上真実 (cputime 増分 / 実時間): ${truth} %   ← ★ 1 コア = 100 % 基準"

echo "★ 各 measurement の読み値:"
printf '  %-28s %s\n' "ps -o %cpu (起動以降の平均)" "$(ps -o %cpu= -p "$SPIN" | tr -d ' ')"
for L in 2 3 4; do
  printf '  %-28s %s\n' "top -l $L -n 1 (最終フレーム)" \
    "$(top -l "$L" -pid "$SPIN" -stats cpu -n 1 2>/dev/null | tail -1)"
done

cat <<'NOTE'

⚠️★★★ 判定:
  ★ `top -l 3` が地上真実と一致すること。
  ⚠️ `top -l 2` は **約 0.48 倍**になる（★ 2 フレーム目の分母に top 自身の
     起動時間 ≈ 1.1 s が混ざるため。-s を伸ばすと 100 % に漸近することで確かめた）。
  ⚠️ `ps -o %cpu` は「起動以降の平均」なので、★ 定常なら一致するが**山は消える**。

★ 陰性対照 (プロセス不在): 下で 0 が出ること。
NOTE
kill "$SPIN" 2>/dev/null || true
sleep 1
echo "  不在時の top: [$(top -l 3 -pid "$SPIN" -stats cpu -n 1 2>/dev/null | tail -1)]  ← ★ 空 or 0 が正しい"
