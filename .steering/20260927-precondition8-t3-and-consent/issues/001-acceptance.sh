#!/usr/bin/env bash
# issue 001 acceptance — validate_blocks.py の未完了マーカー（前提条件 8 / A-1）
# ⚠️ cwd は **worktree のルート**である（loop-run.sh が `cd "$wt"` してから実行する）。
#    → 相対パスで書く。`dirname "$0"` から cd すると main チェックアウトを測ってしまう。
# ⚠️ macOS の bash 3.2 / BSD grep で動く書き方に限る（`grep -F` の固定文字列で数える）。
set -u

VB="experiments/20260801-controlled-friction-task/validate_blocks.py"
PROTO="experiments/20260801-controlled-friction-task/protocol.md"
FAILS=0
ok () { printf '  ✅ %s\n' "$1"; }
ng () { printf '  ❌ %s\n' "$1"; FAILS=$((FAILS + 1)); }

# $1=file $2=固定文字列 $3=表示名
need () {
  if [ ! -f "$1" ]; then ng "$3: ファイルが無い ($1)"; return; fi
  if grep -qF -- "$2" "$1"; then ok "$3"; else ng "$3 (見つからない: $2)"; fi
}
# 在ってはいけない語
forbid () {
  if [ ! -f "$1" ]; then ng "$3: ファイルが無い ($1)"; return; fi
  if grep -qF -- "$2" "$1"; then ng "$3 (⚠️ 在ってはいけない語がある: $2)"; else ok "$3"; fi
}

echo "[001] validate_blocks.py の未完了マーカー"

# AC 1: selftest が緑
if python3 "$VB" --selftest >/dev/null 2>&1; then
  ok "AC1 validate_blocks.py --selftest が exit 0"
else
  ng "AC1 validate_blocks.py --selftest が赤"
fi

# AC 2/4/5: 3 値を読んでいる
need "$VB" "participation_status" "AC2 participation_status を読んでいる"
need "$VB" "started_incomplete"   "AC2 started_incomplete を扱う"
need "$VB" "not_started"          "AC5 not_started を扱う"
need "$VB" "completed"            "AC2 completed を扱う"

# AC 3: negative control —— status 無しの部分記入は FAIL のまま
#   ★ 既存 selftest のケース名（validate_blocks.py:681「★ 一部だけ記入は記入漏れとして赤」）が
#     残っていることを要求する。⚠️ 消したら「緩めた」ので赤にする。
need "$VB" "一部だけ記入は記入漏れとして赤" "AC3 negative control のケースが残っている"

# AC 4: 未知の値を弾いている（新ケースの存在）
if grep -qF "未知の participation_status" "$VB" || grep -qF "未知の status" "$VB"; then
  ok "AC4 未知の status を赤にするケースがある"
else
  ng "AC4 未知の status を赤にするケースが無い"
fi

# AC 6: 実験者向け手順に記入方法がある
need "$PROTO" "participation_status" "AC6 protocol.md に記入手順がある"

# AC 7: ⚠️ 除外・判定を足していない（§3.6 不触）
for w in "exclude_subject" "drop_subject" "skip_subject" "除外する"; do
  forbid "$VB" "$w" "AC7 除外語を導入していない ($w)"
done

echo "  ---- 失敗 ${FAILS} 件 ----"
[ "$FAILS" -eq 0 ] || exit 1
exit 0
