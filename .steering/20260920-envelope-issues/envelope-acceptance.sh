#!/usr/bin/env bash
# 封筒（起票 2 / 5）の AC 検査。
#
# ⚠️★★★ **既存 8 本の `issues/00N-acceptance.sh` は封筒を見ていない** ——
#   あちらは取得時に `jq '.rows'` で行だけを取り出す。★ 封筒 (`provenance` / `config`) を
#   見るのは**この 1 本だけ**である。
#
# ★ ACC_REPLAY_CMD を与えると gse-replay の代わりにそのコマンドを使う（★ 検査自体の 3 状態テスト用）。
#
# Usage: bash .steering/20260920-envelope-issues/envelope-acceptance.sh
# Exit:  0 = 緑 / 1 = 違反あり
#
# 関連: .steering/20260920-envelope-issues/decisions.md ／
#       .steering/20260914-mhd-feature-offline-tiers/blockers.md 起票 2 / 5
set -uo pipefail
fail() { echo "[acceptance envelope] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"

RICH="tests/fixtures/instrument_rich.ndjson"
OLD="tests/fixtures/minimal.ndjson"
[ -f "$RICH" ] || fail "$RICH が無い"
[ -f "$OLD" ] || fail "$OLD が無い"

replay() {
  if [ -n "${ACC_REPLAY_CMD:-}" ]; then $ACC_REPLAY_CMD "$@"
  else cargo run --quiet --bin gse-replay -- "$@"; fi
}

env_out="$(replay "$RICH" --features 2>/dev/null)" || fail "gse-replay --features が非 0 で終了した"
[ -n "$env_out" ] || fail "--features の出力が空"

# ---------- AC1: トップレベルが 3 キーの object（★ 完全一致。増えても減っても落とす） ----------
printf '%s' "$env_out" | jq -e '
  (type == "object") and ((keys_unsorted | sort) == ["config","provenance","rows"])' >/dev/null 2>&1 \
  || fail "AC1: トップレベルが { provenance, config, rows } でない。実際: $(printf '%s' "$env_out" | jq -c 'if type=="object" then (keys_unsorted|sort) else type end' 2>/dev/null)"

printf '%s' "$env_out" | jq -e '(.rows | type == "array") and (.rows | length > 0)' >/dev/null 2>&1 \
  || fail "AC1: rows が非空の配列でない"

# ---------- AC2: provenance のキー集合（★ 完全一致） ----------
#   ⚠️ `os` は**入っていない** —— `logger.rs::write_meta_start` が書いていないため（起票 1 / ADR-032 の領域）。
#     ★ ここへ `os` が現れたら、それは計器が変わったということなので、この検査が落ちてよい。
printf '%s' "$env_out" | jq -e '
  (.provenance | keys_unsorted | sort) == [
    "app_version","capabilities","g1_mode","hmm_version","keyboard_layout",
    "o1_mode","session_start","sharing","source_basename","source_sha256",
    "tool","tool_version"
  ]' >/dev/null 2>&1 \
  || fail "AC2: provenance のキー集合が規範と完全一致しない。実際: $(printf '%s' "$env_out" | jq -c '.provenance | keys_unsorted | sort' 2>/dev/null)"

# ---------- AC3: sharing マーカー（起票 5・判断 5） ----------
#   ★ 検査器 `scripts/check_no_feature_output.sh` がこの形を鍵に使う。⚠️ 形を変えるなら両方直す。
printf '%s' "$env_out" | jq -e '
  .provenance.sharing == {
    "gse_dataset": "prohibited",
    "anonymized": false,
    "absolute_epoch_ms": true,
    "rule": "docs/glossary.md 特徴行"
  }' >/dev/null 2>&1 \
  || fail "AC3: sharing マーカーが規範と一致しない（★ scripts/check_no_feature_output.sh の鍵）。実際: $(printf '%s' "$env_out" | jq -c '.provenance.sharing' 2>/dev/null)"

# ---------- AC4: meta 由来の事実が実際に読めている ----------
meta_line="$(jq -c 'select(.type=="meta" and has("session_start"))' "$RICH" | head -1)"
[ -n "$meta_line" ] || fail "前提: $RICH に meta(session_start) 行が無い"
for k in session_start hmm_version app_version; do
  want="$(printf '%s' "$meta_line" | jq -c ".$k")"
  got="$(printf '%s' "$env_out" | jq -c ".provenance.$k")"
  # ⚠️ `$got` の直後が全角括弧なので **`${got}` と括る**（★ macOS 既定の bash 3.2 は
  #   多バイト文字を変数名の一部として読み、`set -u` で落ちる・check-shell-portability.sh）。
  [ "$want" = "$got" ] || fail "AC4: provenance.${k} が meta の値と違う（meta=${want} / 封筒=${got}）"
done
# ⚠️ 宣言の無いキーは `null` になる（★ 空文字列・空配列で埋めない）。
printf '%s' "$env_out" | jq -e '
  (.provenance.g1_mode == null) and (.provenance.o1_mode == null)
  and (.provenance.keyboard_layout == null)' >/dev/null 2>&1 \
  || fail "AC4: 宣言の無い meta フィールドが null でない（★ 空文字列で埋めない）"

# ---------- AC5: capabilities は meta の値をそのまま、封筒に 1 回だけ ----------
meta_cap="$(jq -c 'select(.type=="meta" and has("capabilities")) | .capabilities' "$RICH" | head -1)"
[ -n "$meta_cap" ] || fail "前提: $RICH の meta に capabilities が無い"
printf '%s' "$env_out" | jq -e --argjson cap "$meta_cap" '.provenance.capabilities == $cap' >/dev/null 2>&1 \
  || fail "AC5: provenance.capabilities が meta の値と等価でない"
# ⚠️★★★ 行には 1 つも残っていないこと（判断 3）。
printf '%s' "$env_out" | jq -e '[.rows[] | select(.quality | has("capabilities"))] | length == 0' >/dev/null 2>&1 \
  || fail "AC5: rows[].quality に capabilities が残っている（★ 封筒へ移したはず）"

# ---------- AC6: 入力の同一性 ----------
printf '%s' "$env_out" | jq -e '.provenance.source_basename == "instrument_rich.ndjson"' >/dev/null 2>&1 \
  || fail "AC6: source_basename が入力のファイル名でない"
printf '%s' "$env_out" | jq -e '
  (.provenance.source_sha256 | test("^[0-9a-f]{16}$"))' >/dev/null 2>&1 \
  || fail "AC6: source_sha256 が 16 桁の 16 進でない。実際: $(printf '%s' "$env_out" | jq -c '.provenance.source_sha256' 2>/dev/null)"
# ★ 違う入力なら違うハッシュになる（★ 定数を返していないことの確認）。
old_env="$(replay "$OLD" --features 2>/dev/null)" || fail "AC6: $OLD で --features が非 0"
h1="$(printf '%s' "$env_out" | jq -r '.provenance.source_sha256')"
h2="$(printf '%s' "$old_env" | jq -r '.provenance.source_sha256')"
[ "$h1" != "$h2" ] || fail "AC6: 異なる入力で source_sha256 が同じ（★ 定数を返していないか）"
printf '%s' "$old_env" | jq -e '.provenance.source_basename == "minimal.ndjson"' >/dev/null 2>&1 \
  || fail "AC6: minimal の source_basename が違う"
# ⚠️ 宣言の無い入力では capabilities が null（★ 空配列・空オブジェクトで埋めない）。
printf '%s' "$old_env" | jq -e '.provenance.capabilities == null' >/dev/null 2>&1 \
  || fail "AC6: 宣言の無い入力で provenance.capabilities が null でない"

# ---------- AC7: config のキー集合と値 ----------
printf '%s' "$env_out" | jq -e '
  (.config | keys_unsorted | sort) == [
    "b_ms","engine_tick_ms","hmm_version","hole_gap_ms","max_feature_ticks",
    "net_diff_min","pause_threshold_ms","q","w_ms","warmup_count"
  ]' >/dev/null 2>&1 \
  || fail "AC7: config のキー集合が規範と完全一致しない。実際: $(printf '%s' "$env_out" | jq -c '.config | keys_unsorted | sort' 2>/dev/null)"
# ★ 既定値（事前宣言事項・判断 25 #13 が P1 前に凍結する対象）。
#   ⚠️ 値を変えたら**この行を先に書き換える**こと（★ 黙って変わらせない）。
printf '%s' "$env_out" | jq -e '
  (.config.w_ms == 30000) and (.config.q == 0.99) and (.config.b_ms == 30000)
  and (.config.hole_gap_ms == 2000) and (.config.warmup_count == null)
  and (.config.max_feature_ticks == 1000000)
  and (.config.engine_tick_ms == 1000) and (.config.pause_threshold_ms == 2000)' >/dev/null 2>&1 \
  || fail "AC7: config の既定値が想定と違う（★ 事前宣言事項。変えたなら検査を先に直す）。実際: $(printf '%s' "$env_out" | jq -c '.config' 2>/dev/null)"

# ---------- AC8: 収集時と解析時の hmm_version を**別フィールド**で持つ ----------
#   ★ `instrument_rich.ndjson` の meta は "0.2.0"、現行バイナリは "0.5.0"（2026-09-20 実測）。
#   ⚠️ 揃ってしまったら、この検査は「2 つ持つ意味」を見なくなる。→ そのときは fixture を足す。
printf '%s' "$env_out" | jq -e '.provenance.hmm_version != .config.hmm_version' >/dev/null 2>&1 \
  || fail "AC8: 収集時と解析時の hmm_version が同じ値になった（★ 食い違いを読める fixture へ差し替えること）"

# ---------- AC9: ⚠️★★★ 同じ入力から**バイト単位で同じ出力** ----------
#   ★ 生成時刻を載せない（判断 7）ことの検査。⚠️ 載せた瞬間にここが赤になる。
env_again="$(replay "$RICH" --features 2>/dev/null)" || fail "AC9: 2 回目の --features が非 0"
[ "$env_out" = "$env_again" ] \
  || fail "AC9: 同じ入力から 2 回実行してバイト単位で一致しない（★ 生成時刻など非決定な値を載せていないか）"

# ---------- AC10: 共有の門が、この出力を実際に赤にする ----------
#   ⚠️★★★ 「門がある」ではなく「**この出力で赤になる**」ことを確かめる
#     （★ 本プロジェクトは「検査があるつもりで検査していない」を 3 回踏んでいる）。
GATE="../scripts/check_no_feature_output.sh"
[ -f "$GATE" ] || fail "AC10: $GATE が無い"
gdir="$(mktemp -d)"; trap 'rm -rf "$gdir"' EXIT
printf '%s' "$env_out" > "$gdir/feat.json"
if bash "$GATE" --root "$gdir" >/dev/null 2>&1; then
  fail "AC10: 共有の門が封筒つきの出力を通した（★ マーカーで拾うはず）"
fi
# ★ 封筒を剥がした形でも赤になること（判断 6 の 2 本目）。
rm -f "$gdir/feat.json"
printf '%s' "$env_out" | jq '.rows' > "$gdir/rows.json"
if bash "$GATE" --root "$gdir" >/dev/null 2>&1; then
  fail "AC10: 共有の門が封筒を剥がした行の配列を通した（★ 行の形で拾うはず）"
fi
# ★ 偽陽性でないこと: metrics.json 形は通る。
rm -f "$gdir/rows.json"
echo '{"session_id":"x","f1":0.8,"median_ms":120}' > "$gdir/m.json"
bash "$GATE" --root "$gdir" >/dev/null 2>&1 \
  || fail "AC10: 共有の門が metrics.json 形を赤にした（★ 偽陽性。gse-dataset へ出す唯一の共有物）"

echo "[acceptance envelope] OK"
