#!/usr/bin/env bash
# issue 007 (IME 変換中の onset 頻度カウンタ) の AC 検査
# ⚠️ 実行は repo 直下から。
set -uo pipefail
fail() { echo "[acceptance 007i] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"

# ⚠️★★★ loop-run.sh は `( cd "$wt" && bash "$acc" )` で **worktree を cwd にして**呼ぶ
#   (scripts/loop-run.sh:369)。★ よって repo root は **cwd** であって、
#   ${BASH_SOURCE[0]} の位置 (= main checkout) ではない。
#   ⚠️ BASH_SOURCE から導くと **worktree ではなく main checkout を検査**してしまう。
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない（src-tauri/Cargo.toml が無い）: $REPO_ROOT"
cd "$REPO_ROOT/src-tauri" || fail "src-tauri が無い"

FIX="tests/fixtures/ime_overlap.ndjson"
[ -f "$FIX" ] || fail "AC2: 新 fixture が無い: $FIX"

run() { cargo run --quiet --bin gse-replay -- "$1" --features 2>/dev/null; }

out="$(run "$FIX")" || fail "AC1: --features が非 0"

# ── AC1: onset 行だけが ime_overlap を持つ ──────────────────────────────
printf '%s' "$out" | jq -e '
  (.rows | arrays)
  and (.rows | all(.stall_onset;
        if .is_onset then (.ime_overlap | type == "boolean")
        else (.ime_overlap == null) end))' >/dev/null 2>&1 \
  || fail "AC1: ime_overlap が onset 行だけに bool で載っていない"

# ── AC2 / AC3: true と false の両方が出る ───────────────────────────────
n_true="$(printf '%s' "$out" | jq '[.rows[].stall_onset | select(.is_onset and .ime_overlap == true)] | length')" \
  || fail "AC2: 数えられない"
n_false="$(printf '%s' "$out" | jq '[.rows[].stall_onset | select(.is_onset and .ime_overlap == false)] | length')" \
  || fail "AC3: 数えられない"
[ "${n_true:-0}" -ge 1 ] \
  || fail "AC2: ime_overlap == true の onset が 0 件（★ fixture が IME 区間に重なる onset を持っていないか、判定が効いていない）"
[ "${n_false:-0}" -ge 1 ] \
  || fail "AC3: ime_overlap == false の onset が 0 件（★ 常に true を返している疑い ＝ 判定が空振り）"

# ── AC6: 抑制していない（ime_shadow 行を削っても onset 集合が同じ） ──────
#   ⚠️★★★ 「数えるだけで抑制しない」を出力の同一性で固定する。
tmpd="$(mktemp -d)" || fail "AC6: 一時ディレクトリを作れない"
trap 'rm -rf "$tmpd"' EXIT
grep -v '"type":"ime_shadow"' "$FIX" > "$tmpd/no_ime.ndjson" || fail "AC6: ime_shadow を落とせない"

# ⚠️ 変異が実際に起きたことを確かめる (検査の検査 ルール 3: src に 1 件 / mut に 0 件)
src_ime="$(grep -c '"type":"ime_shadow"' "$FIX")"
[ "${src_ime:-0}" -ge 1 ] || fail "AC6: 元 fixture に ime_shadow 行が無い（★ 検査の前提が崩れている）"
mut_ime="$(grep -c '"type":"ime_shadow"' "$tmpd/no_ime.ndjson" || true)"
[ "${mut_ime:-1}" -eq 0 ] || fail "AC6: 変異後にも ime_shadow 行が残っている"

out_no_ime="$(run "$tmpd/no_ime.ndjson")" || fail "AC6: ime 無し版で --features が非 0"
o_with="$(printf '%s' "$out"        | jq -c '[.rows[] | select(.stall_onset.is_onset) | .stall_onset.t0_ms] | sort')"
o_none="$(printf '%s' "$out_no_ime" | jq -c '[.rows[] | select(.stall_onset.is_onset) | .stall_onset.t0_ms] | sort')"
[ "$o_with" = "$o_none" ] \
  || fail "AC6: ime_shadow の有無で onset 集合が変わった（★ 抑制してしまっている）。with=$o_with none=$o_none"

# ⚠️ かつ ime 無し版では overlap が全部 false であること (AC5 の CLI 側の裏取り)
printf '%s' "$out_no_ime" | jq -e '
  .rows | all(.stall_onset | select(.is_onset); .ime_overlap == false)' >/dev/null 2>&1 \
  || fail "AC5: ime_shadow が無い入力で ime_overlap が false になっていない（★ null で埋めていないか）"

# ── AC4 / AC5: 対応する単体テストが 1 件ずつ走って緑 ─────────────────────
for t in \
  ime_overlap_is_closed_interval_intersection \
  no_ime_rows_means_overlap_false_not_null
do
  o="$(cargo test --workspace "$t" -- --exact --nocapture 2>&1)" || fail "test $t が赤"
  printf '%s' "$o" | grep -qE '1 passed' \
    || fail "test $t が 1 件も走っていない（★ cargo test は 0 件マッチでも exit 0 になる）"
done

# ── AC7: abandon を「迷い」と解釈する語が無い ───────────────────────────
if grep -rniE '(迷い|hesitat)' src/analysis/feat_offline/ >/dev/null 2>&1; then
  fail "AC7: feat_offline/ に abandon を「迷い」と解釈する語がある"
fi

echo "[acceptance 007i] OK"
