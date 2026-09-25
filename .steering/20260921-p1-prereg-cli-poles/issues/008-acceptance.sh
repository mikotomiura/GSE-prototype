#!/usr/bin/env bash
# issue 008 (計算量の門の張り直し ＋ 3 極スクリプト) の AC 検査
# ⚠️ 実行は repo 直下から。
set -uo pipefail
fail() { echo "[acceptance 008g] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"

# ⚠️★★★ loop-run.sh は `( cd "$wt" && bash "$acc" )` で **worktree を cwd にして**呼ぶ
#   (scripts/loop-run.sh:369)。★ よって repo root は **cwd** であって、
#   ${BASH_SOURCE[0]} の位置 (= main checkout) ではない。
#   ⚠️ BASH_SOURCE から導くと **worktree ではなく main checkout を検査**してしまう。
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない（src-tauri/Cargo.toml が無い）: $REPO_ROOT"
PREV_AC="$REPO_ROOT/.steering/20260914-mhd-feature-offline-tiers/issues/008-acceptance.sh"
ALLPOLES="$REPO_ROOT/scripts/run-features-all-poles.sh"
RUNBOOK="$REPO_ROOT/docs/verification-runbook.md"
[ -f "$PREV_AC" ]   || fail "前タスクの 008-acceptance.sh が無い"
[ -f "$ALLPOLES" ]  || fail "AC4: $ALLPOLES が無い"
[ -f "$RUNBOOK" ]   || fail "AC7: $RUNBOOK が無い"

# ⚠️ trap は後から書くと前のを上書きする。後始末は 1 か所に集約する。
CLEANUP=()
cleanup() { [ "${#CLEANUP[@]}" -gt 0 ] && rm -rf "${CLEANUP[@]}"; return 0; }
trap cleanup EXIT

# ── AC1 / AC2: 門が多 onset で張られている ─────────────────────────────
#   ⚠️★★★ 「20 秒以内に終わった」だけでは足りない。
#     ★ 門の入力で onset が実際に何本立つかを **独立に数える**。
#     ★ 前タスクの検査は入力を awk で生成するので、生成部の打鍵数だけを見ても
#       onset 本数は分からない。→ 検査が出力する onset 本数を拾う契約にする。
#   ⚠️ 門は 20 秒級なので **1 回だけ**回し、その出力から両方の本数を読む。
prev_log="$(mktemp)" || fail "AC1: 一時ファイルを作れない"
CLEANUP+=("$prev_log")
( cd "$REPO_ROOT" && bash "$PREV_AC" ) > "$prev_log" 2>&1 \
  || { echo "--- 前タスク 008-acceptance.sh の出力（末尾） ---" >&2; tail -20 "$prev_log" >&2; \
       fail "AC1: 前タスクの 008-acceptance.sh が非 0"; }

for tag in AC18 AC18b; do
  # ★ 前タスクの検査は「<tag>: onsets=<n>」を 1 行出す契約にする（本 issue が足す）。
  n="$(grep -oE "${tag}: *onsets=[0-9]+" "$prev_log" | grep -oE '[0-9]+$' | head -1)"
  [ -n "${n:-}" ] \
    || fail "AC1/AC2($tag): 検査が「$tag: onsets=<n>」を出していない（★ 本数を数えられないと門が空振りか判別できない）"
  [ "$n" -ge 50 ] \
    || fail "AC1/AC2($tag): onset が $n 本しか立っていない（★ 50 本以上でないと R に比例する経路を踏めない）"
done

# ── AC3: 門が 1 極あたりで測られている ──────────────────────────────────
grep -qE '\-\-pole ' "$PREV_AC" \
  || fail "AC3: 前タスクの門が --pole を渡していない（★ 1 極あたりで測る契約）"
multi="$(grep -cE '\-\-pole +(baseline|pointer_b|modifier_m_plus)' "$PREV_AC")"
[ "${multi:-0}" -le 2 ] \
  || fail "AC3: 門が複数極を回している疑い（--pole の出現が $multi 箇所）。★ 3 極の合計を測らない"

# ── AC4: 3 極スクリプトが 3 ファイルを出す ──────────────────────────────
cd "$REPO_ROOT/src-tauri" || fail "src-tauri が無い"
FIX="tests/fixtures/pointer_pole.ndjson"
[ -f "$FIX" ] || fail "AC4: fixture が無い: $FIX"
outdir="$(mktemp -d)" || fail "AC4: 一時ディレクトリを作れない"
CLEANUP+=("$outdir")

( cd "$REPO_ROOT" && bash "$ALLPOLES" "src-tauri/$FIX" "$outdir" ) >/dev/null 2>&1 \
  || fail "AC4: run-features-all-poles.sh が非 0"

for pole in baseline pointer_b modifier_m_plus; do
  f="$outdir/$pole.json"
  [ -f "$f" ] || fail "AC4: $pole.json が出ていない"
  got="$(jq -r '.config.pole' "$f")" || fail "AC4: $f を読めない"
  [ "$got" = "$pole" ] || fail "AC4: $f の config.pole が '$got'（ファイル名は '$pole'）"
done

# ── AC6: applicable == false でも exit 0 で 3 ファイル出る ──────────────
#   ★ stall_onset_observed は修飾キー行もポインタ宣言も持たない (実測)。
outdir2="$(mktemp -d)" || fail "AC6: 一時ディレクトリを作れない"
CLEANUP+=("$outdir2")
( cd "$REPO_ROOT" && bash "$ALLPOLES" "src-tauri/tests/fixtures/stall_onset_observed.ndjson" "$outdir2" ) >/dev/null 2>&1 \
  || fail "AC6: pole_applicable == false を失敗扱いにしている（★ 正しい報告であって失敗ではない）"
[ "$(ls -1 "$outdir2"/*.json 2>/dev/null | wc -l)" -eq 3 ] \
  || fail "AC6: 3 ファイル出ていない"
jq -e '.config.pole_applicable == false' "$outdir2/modifier_m_plus.json" >/dev/null 2>&1 \
  || fail "AC6: modifier_m_plus が applicable == false になっていない（★ 検査の前提が崩れている）"

# ── AC5: fail-closed ────────────────────────────────────────────────────
outdir3="$(mktemp -d)" || fail "AC5: 一時ディレクトリを作れない"
CLEANUP+=("$outdir3")
if ( cd "$REPO_ROOT" && bash "$ALLPOLES" "src-tauri/tests/fixtures/__does_not_exist__.ndjson" "$outdir3" ) >/dev/null 2>&1; then
  fail "AC5: 存在しない入力でも exit 0 になった（fail-closed でない）"
fi

# ── AC7: runbook に手順と Cartesian 禁止が書かれている ──────────────────
grep -qE 'run-features-all-poles' "$RUNBOOK" \
  || fail "AC7: runbook に 3 極を回す手順が無い"
grep -qE '(Cartesian|直積|組まない)' "$RUNBOOK" \
  || fail "AC7: runbook に「極を Cartesian に組まない」旨が無い"

echo "[acceptance 008g] OK"
