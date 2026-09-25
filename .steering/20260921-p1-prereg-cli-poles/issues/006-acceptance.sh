#!/usr/bin/env bash
# issue 006 (極 B ポインタ) の AC 検査
# ⚠️ 実行は repo 直下から。
set -uo pipefail
fail() { echo "[acceptance 006p] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"

# ⚠️★★★ loop-run.sh は `( cd "$wt" && bash "$acc" )` で **worktree を cwd にして**呼ぶ
#   (scripts/loop-run.sh:369)。★ よって repo root は **cwd** であって、
#   ${BASH_SOURCE[0]} の位置 (= main checkout) ではない。
#   ⚠️ BASH_SOURCE から導くと **worktree ではなく main checkout を検査**してしまう。
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない（src-tauri/Cargo.toml が無い）: $REPO_ROOT"
cd "$REPO_ROOT/src-tauri" || fail "src-tauri が無い"

PFIX="tests/fixtures/pointer_pole.ndjson"
NOCAP="tests/fixtures/stall_onset_observed.ndjson"
[ -f "$PFIX" ]  || fail "AC1: 新 fixture が無い: $PFIX"
[ -f "$NOCAP" ] || fail "AC7: fixture が無い: $NOCAP"

run() { local f="$1"; shift; cargo run --quiet --bin gse-replay -- "$f" --features "$@" 2>/dev/null; }
onsets() { printf '%s' "$1" | jq -c '[.rows[] | select(.stall_onset.is_onset) | .stall_onset.t0_ms] | sort'; }

# ── AC1: 極 B が開通している ────────────────────────────────────────────
pb="$(run "$PFIX" --pole pointer_b)" || fail "AC1: --pole pointer_b が非 0"
printf '%s' "$pb" | jq -e '
  (.config.pole == "pointer_b") and (.config.pole_applicable == true)' >/dev/null 2>&1 \
  || fail "AC1: config.pole / pole_applicable が期待と違う（★ fixture は capabilities に pointer_bin を宣言している）"

base="$(run "$PFIX" --pole baseline)" || fail "AC2: --pole baseline が非 0"

# ── AC2: 極 B の onset が baseline の真の部分集合 ───────────────────────
o_base="$(onsets "$base")" || fail "AC2: baseline の onset を取り出せない"
o_pb="$(onsets "$pb")"     || fail "AC2: pointer_b の onset を取り出せない"
[ "$o_base" != "$o_pb" ] \
  || fail "AC2: pointer_b と baseline の onset が同一（★ 抑制が効いていない）。onset=$o_base"

subset="$(jq -n --argjson a "$o_base" --argjson b "$o_pb" \
  '($b - ($b - $a)) == $b and (($b | length) < ($a | length))')" \
  || fail "AC2: 包含関係を判定できない"
[ "$subset" = "true" ] \
  || fail "AC2: pointer_b の onset が baseline の真の部分集合でない（baseline=$o_base pointer_b=${o_pb}）。★ 逆向きなら抑制が反転している"

# ── AC3: observed_intervals が極 B で狭くなる ───────────────────────────
iv_base="$(printf '%s' "$base" | jq -c '.provenance.observed_intervals')" || fail "AC3: observed_intervals が無い"
iv_pb="$(printf '%s' "$pb"   | jq -c '.provenance.observed_intervals')" || fail "AC3: observed_intervals が無い"
[ "$iv_base" != "$iv_pb" ] \
  || fail "AC3: observed_intervals が baseline と同じまま（★ 抑制が配線されていない）"

span() { printf '%s' "$1" | jq '[.[] | (.b_ms - .a_ms)] | add // 0'; }
s_base="$(span "$iv_base")" || fail "AC3: 区間長を集計できない"
s_pb="$(span "$iv_pb")"     || fail "AC3: 区間長を集計できない"
[ "$s_pb" -lt "$s_base" ] \
  || fail "AC3: 極 B の評価区間の総長 ($s_pb) が baseline ($s_base) 以上（★ 抑制で狭くなるはず）"

# ── AC7: capabilities 宣言が無い入力 ────────────────────────────────────
nc_pb="$(run "$NOCAP" --pole pointer_b)" || fail "AC7: --pole pointer_b が非 0（capabilities 無し fixture）"
printf '%s' "$nc_pb" | jq -e '
  (.config.pole_applicable == false)
  and (.config.pole_not_applicable_reason == "no_pointer_capability")' >/dev/null 2>&1 \
  || fail "AC7: pole_applicable / pole_not_applicable_reason が期待と違う"

nc_base="$(run "$NOCAP" --pole baseline)" || fail "AC7: baseline が非 0"
so_pb="$(printf '%s'   "$nc_pb"   | jq -cS '[.rows[].stall_onset]')" || fail "AC7: stall_onset を取り出せない"
so_base="$(printf '%s' "$nc_base" | jq -cS '[.rows[].stall_onset]')" || fail "AC7: stall_onset を取り出せない"
[ "$so_pb" = "$so_base" ] \
  || fail "AC7: not_applicable と称しながら stall_onset が baseline と違う（★ 値で埋めている）"

# ⚠️ 理由コードが極 M+ と別の語であること（★ 根拠が違うので混同させない）
[ "$(printf '%s' "$nc_pb" | jq -r '.config.pole_not_applicable_reason')" != "no_modifier_rows" ] \
  || fail "AC7: ポインタの理由コードが修飾キーのものと同じ語になっている"

# ── AC4〜6: 対応する単体テストが 1 件ずつ走って緑 ────────────────────────
for t in \
  pointer_bins_merge_into_maximal_intervals \
  theta_sample_excludes_pairs_across_pointer_suppression \
  pointer_suppression_skips_the_leading_w
do
  # ⚠️★★★ `--exact` は**完全パス**（`mod::tests::<name>`）にしか一致せず、裸の名前では 0 件＝**実装が正しくても必ず赤**
  #   （2026-09-25 実測・issue 002 / 003 の worker が発見）。→ 部分一致で走らせ、
  #   `test <任意のパス>::<name> ... ok` の行が**ちょうど 1 行**あることを数える（★ 部分名・0 件・同名 2 件をすべて落とす）。
  out="$(cargo test --workspace "$t" -- --nocapture 2>&1)" || fail "test $t が赤"
  n_ok="$(printf '%s\n' "$out" | tr -d '\r' | grep -cE "^test ([A-Za-z0-9_]+::)*${t} \.\.\. ok$")"
  [ "${n_ok}" -eq 1 ] \
    || fail "test $t がちょうど 1 件緑で走っていない（${n_ok} 件）（★ cargo test は 0 件マッチでも exit 0 になる）"
done

# ── AC8: pointer_bin の値を読んでいない ─────────────────────────────────
if grep -rnE '\b(moved|buttons|wheel)\b' src/analysis/feat_offline/ >/dev/null 2>&1; then
  fail "AC8: feat_offline/ が pointer_bin の値 (moved/buttons/wheel) を参照している（★ 存在だけを使う）"
fi

# ── AC9: 他の極の出力が変わっていない ───────────────────────────────────
PREV="$REPO_ROOT/.steering/20260914-mhd-feature-offline-tiers/issues"
HERE="$REPO_ROOT/.steering/20260921-p1-prereg-cli-poles/issues"
for s in "$PREV/005-acceptance.sh" "$PREV/008-acceptance.sh" "$HERE/005-acceptance.sh"; do
  ( cd "$REPO_ROOT" && bash "$s" ) >/dev/null 2>&1 \
    || fail "AC9: $(basename "$s") が非 0（★ 極 B の導入が他の極を動かした）"
done

echo "[acceptance 006p] OK"
