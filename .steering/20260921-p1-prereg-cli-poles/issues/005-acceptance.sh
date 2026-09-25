#!/usr/bin/env bash
# issue 005 (極 M+) の AC 検査
# ⚠️ 実行は repo 直下から。
set -uo pipefail
fail() { echo "[acceptance 005m] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"

# ⚠️★★★ loop-run.sh は `( cd "$wt" && bash "$acc" )` で **worktree を cwd にして**呼ぶ
#   (scripts/loop-run.sh:369)。★ よって repo root は **cwd** であって、
#   ${BASH_SOURCE[0]} の位置 (= main checkout) ではない。
#   ⚠️ BASH_SOURCE から導くと **worktree ではなく main checkout を検査**してしまう。
REPO_ROOT="$(pwd)"
[ -f "$REPO_ROOT/src-tauri/Cargo.toml" ] || fail "cwd が repo root ではない（src-tauri/Cargo.toml が無い）: $REPO_ROOT"
cd "$REPO_ROOT/src-tauri" || fail "src-tauri が無い"

MFIX="tests/fixtures/modifier_pole.ndjson"
NOMOD="tests/fixtures/stall_onset_observed.ndjson"
[ -f "$MFIX" ]  || fail "AC1: 新 fixture が無い: $MFIX"
[ -f "$NOMOD" ] || fail "AC6: fixture が無い: $NOMOD"

run() { local f="$1"; shift; cargo run --quiet --bin gse-replay -- "$f" --features "$@" 2>/dev/null; }
onsets() { printf '%s' "$1" | jq -c '[.rows[] | select(.stall_onset.is_onset) | .stall_onset.t0_ms] | sort'; }

# ── AC1: 極 M+ が開通している ───────────────────────────────────────────
mplus="$(run "$MFIX" --pole modifier_m_plus)" || fail "AC1: --pole modifier_m_plus が非 0"
printf '%s' "$mplus" | jq -e '.config.pole == "modifier_m_plus"' >/dev/null 2>&1 \
  || fail "AC1: config.pole が modifier_m_plus でない"
printf '%s' "$mplus" | jq -e '.config.pole_applicable == true' >/dev/null 2>&1 \
  || fail "AC1: 修飾キー行を持つ fixture なのに pole_applicable が true でない"

base="$(run "$MFIX" --pole baseline)" || fail "AC2: --pole baseline が非 0"

# ── AC2: 極 M+ の onset 集合が baseline と異なる（≠） ────────────────────
#   ⚠️★★★ 判断 28: 「M+ は baseline の真の上位集合」は**保証されない**
#   （挿入系の press を除くと条件 A の成立期間がつながり、baseline にあった後ろの立ち上がりが
#   消えうる。`stall_onset.rs::m_plus_can_drop_a_baseline_onset_by_merging_condition_a` が
#   反例を固定している）。★ ここで検査できるのは「規則が効いていて集合が変わること」だけで、
#   向き（広い/狭い/一部交換）までは決め打ちしない。⚠️「異なる」の検査そのものは残す。
o_base="$(onsets "$base")"  || fail "AC2: baseline の onset を取り出せない"
o_plus="$(onsets "$mplus")" || fail "AC2: M+ の onset を取り出せない"
[ "$o_base" != "$o_plus" ] \
  || fail "AC2: M+ と baseline の onset が同一（★ 規則が効いていない）。onset=$o_base"

# ── AC6: 修飾キー行が 0 本の入力で not_applicable かつ baseline と恒等 ──
nm_plus="$(run "$NOMOD" --pole modifier_m_plus)" || fail "AC6: --pole modifier_m_plus が非 0（修飾キー無し fixture）"
printf '%s' "$nm_plus" | jq -e '
  (.config.pole_applicable == false)
  and (.config.pole_not_applicable_reason == "no_modifier_rows")' >/dev/null 2>&1 \
  || fail "AC6: pole_applicable / pole_not_applicable_reason が期待と違う"

nm_base="$(run "$NOMOD" --pole baseline)" || fail "AC6: baseline が非 0"
so_plus="$(printf '%s' "$nm_plus" | jq -cS '[.rows[].stall_onset]')" || fail "AC6: stall_onset を取り出せない"
so_base="$(printf '%s' "$nm_base" | jq -cS '[.rows[].stall_onset]')" || fail "AC6: stall_onset を取り出せない"
[ "$so_plus" = "$so_base" ] \
  || fail "AC6: not_applicable と称しながら stall_onset が baseline と違う（★ 値で埋めている）"

# ── AC3〜5: 対応する単体テストが 1 件ずつ走って緑 ────────────────────────
for t in \
  m_plus_does_not_drop_deletions \
  modifier_depth_merges_nested_presses \
  unmatched_modifier_release_and_open_press
do
  # ⚠️★★★ `--exact` は**完全パス**（`mod::tests::<name>`）にしか一致せず、裸の名前では 0 件＝**実装が正しくても必ず赤**
  #   （2026-09-25 実測・issue 002 / 003 の worker が発見）。→ 部分一致で走らせ、
  #   `test <任意のパス>::<name> ... ok` の行が**ちょうど 1 行**あることを数える（★ 部分名・0 件・同名 2 件をすべて落とす）。
  out="$(cargo test --workspace "$t" -- --nocapture 2>&1)" || fail "test $t が赤"
  n_ok="$(printf '%s\n' "$out" | tr -d '\r' | grep -cE "^test ([A-Za-z0-9_]+::)*${t} \.\.\. ok$")"
  [ "${n_ok}" -eq 1 ] \
    || fail "test $t がちょうど 1 件緑で走っていない（${n_ok} 件）（★ cargo test は 0 件マッチでも exit 0 になる）"
done

# ── AC8: collector が --features 経路にしか配線されていない ──────────────
#   ⚠️ 呼び出し箇所を数える。1 か所を超えたら他経路へ漏れている疑い。
calls="$(grep -cE 'collect_modifier_intervals\(' src/bin/replay.rs)" || calls=0
[ "$calls" -ge 1 ] || fail "AC8: collect_modifier_intervals の呼び出しが無い"
[ "$calls" -le 2 ] || fail "AC8: collect_modifier_intervals の呼び出しが $calls 箇所ある（★ --features 以外へ漏れていないか確認）"
if grep -nE 'collect_modifier_intervals' src/analysis/metrics.rs >/dev/null 2>&1; then
  fail "AC8: metrics.rs が collect_modifier_intervals を参照している"
fi

# ── AC7: baseline の出力が本 issue の前後で変わっていない ────────────────
PREV="$REPO_ROOT/.steering/20260914-mhd-feature-offline-tiers/issues"
for prev in 005 008; do
  ( cd "$REPO_ROOT" && bash "$PREV/$prev-acceptance.sh" ) >/dev/null 2>&1 \
    || fail "AC7: 前タスクの $prev-acceptance.sh が非 0（★ baseline の行が動いた）"
done

echo "[acceptance 005m] OK"
