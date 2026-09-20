#!/usr/bin/env bash
# issue 003 (T1a 分布・個人相対) の AC 検査
# ⚠️★★★ 2026-09-20（封筒・起票 2）: `--features` の出力は
#   **`{ provenance, config, rows }` の封筒**になった（判断 25 #14）。
#   ★ 本検査は取得時に `jq '.rows'` で**行だけを取り出して**おり、
#     以降の `.[]` / `all(.[]; ...)` は封筒を剥がした後の配列を指す。
#   ⚠️★★★ **この検査は `provenance` と `config` を 1 つも見ていない。**
#     ★ 封筒自体の検査は `.steering/20260920-envelope-issues/envelope-acceptance.sh` が持つ。
#   ★ 封筒が無い（配列のままの）出力では `jq '.rows'` が失敗し、
#     `set -o pipefail` によりその場で赤になる（fail-closed）。
set -uo pipefail
fail() { echo "[acceptance 003] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"

out="$(cargo run --quiet --bin gse-replay -- tests/fixtures/deep_silence.ndjson --features 2>/dev/null | jq '.rows')" \
  || fail "gse-replay --features が非 0 で終了した"
[ -n "$out" ] || fail "--features の出力が空"

# AC1
printf '%s' "$out" | jq -e '
  all(.[];
    (.dispersion | type == "object")
    and (.dispersion | has("pause_p50_ms") and has("pause_p90_ms") and has("pause_max_ms")
         and has("iki_cv") and has("surprise")))' >/dev/null 2>&1 \
  || fail "全行に dispersion の必須フィールドが揃っていない"

# AC3: 不変式 p50 <= p90 <= max（⚠️ null は検査対象外 = 0 埋めしていない行）
printf '%s' "$out" | jq -e '
  all(.[] | .dispersion;
    (.pause_p50_ms == null or .pause_p90_ms == null or .pause_max_ms == null)
    or (.pause_p50_ms <= .pause_p90_ms and .pause_p90_ms <= .pause_max_ms))' >/dev/null 2>&1 \
  || fail "p50 <= p90 <= max が成り立たない行がある"

# AC7: ⚠️ 退化していないこと（deep_silence は長い沈黙を含む fixture）
printf '%s' "$out" | jq -e '[.[].dispersion.pause_max_ms | select(. != null)] | (length > 0) and (max > 0)' >/dev/null 2>&1 \
  || fail "pause_max_ms が全行 null か 0（★ 沈黙を含む fixture なのに出力が退化している）"

# ⚠️★★★ 2026-09-15 追加（`code-reviewer` MEDIUM）——
#   ★ 非退化検査を fixture 1 本に賭けない。★ instrument_rich も pause を 2 本持つ。
#   ⚠️ **全行 null が「正しい」fixture が実在する**ので、それを既知として書いておく:
#     - outcome_metrics.ndjson   : セッション IKI が {1000, 1000} のみ → 分散 0 → baseline なし
#     - resumption_outcomes.ndjson: iki_cv が全行 null
#   ★ これらを「壊れている」と誤診して直しにいかないこと。
out2="$(cargo run --quiet --bin gse-replay -- tests/fixtures/instrument_rich.ndjson --features 2>/dev/null | jq '.rows')" \
  || fail "gse-replay --features が非 0 で終了した (instrument_rich)"
printf '%s' "$out2" | jq -e '[.[].dispersion.pause_max_ms | select(. != null)] | length > 0' >/dev/null 2>&1 \
  || fail "instrument_rich で pause_max_ms が全行 null（★ 同 fixture は pause を 2 本持つ）"

# ⚠️★★★ 現状 p50 == p90 == max である（★ code-reviewer HIGH-1・構造的帰結）。
#   ★ PAUSE_THRESHOLD_MS(2000) > ENGINE_TICK_MS(1000) なので 1 tick に pause は高々 1 本。
#   → ★ **この検査は「いま 3 値が同値であること」を固定する**。⚠️ 集約窓を広げる裁定
#     （blockers.md 起票 7）が通ったら、**本検査を先に書き換えること**。
printf '%s' "$out" | jq -e '
  all(.[] | .dispersion | select(.pause_p50_ms != null);
    .pause_p50_ms == .pause_p90_ms and .pause_p90_ms == .pause_max_ms)' >/dev/null 2>&1 \
  || fail "p50/p90/max が同値でない（★ 起票 7 の裁定が入ったなら本検査を更新すること）"

# AC6: ⚠️ 帯域分割を入れていないこと（★ [P121] が否定した形）
if grep -nEi '(band|bucket|short_pause|medium_pause|long_pause|帯域)' \
     src/analysis/feat_offline/dispersion.rs >/dev/null 2>&1; then
  fail "dispersion.rs に帯域分割がある（★ [P121] は 4 帯域すべてが成績と負相関と示した）"
fi

# ★ pause / net は issue 001 の共有ヘルパを使うこと（⚠️ 局所定義を作らない）
#   ⚠️ Codex TASK-PRE 指摘 5: 局所定義は issue 005 (stall onset) との破壊的な食い違いを生む。
SRCF="src/analysis/feat_offline/dispersion.rs"
if grep -nE '^[[:space:]]*(pub )?fn [a-z_]*(extract_pauses|compute_net|pause_list)' "$SRCF" >/dev/null 2>&1; then
  fail "$SRCF が pause / net を独自に定義している（★ mod.rs の共有ヘルパを使うこと）"
fi
grep -qE 'super::|crate::analysis::feat_offline::' "$SRCF"   || fail "$SRCF が mod.rs の共有ヘルパを参照していない"

# ⚠️★★★ 2026-09-15 追加（★ 引き継ぎ §4 の型 / decisions.md 判断 8）——
#   ★ 「否定形だけでは抜ける」ことを issue 001 で実測した（`TICK_MS` の再宣言が緑のまま通った）。
#   ⚠️ 出力キー集合の**完全一致**。フィールドを足したくなったら AC1 と本検査を先に直すこと。
printf '%s' "$out" | jq -e '
  [.[].dispersion | keys_unsorted[]] | unique
  == ["iki_cv","pause_max_ms","pause_p50_ms","pause_p90_ms","surprise"]' >/dev/null 2>&1 \
  || fail "dispersion のキー集合が AC1 の 5 個と完全一致しない（★ 増えても減っても落とす）"

# ⚠️ 新しい数値定数を宣言しない（ADR-030 D3 逐語「新しい定数を作らず、既存パラメータを対称に再利用する」）
if grep -nE '^[[:space:]]*(pub )?const +[A-Z_]+ *: *(u8|u16|u32|u64|usize|i8|i16|i32|i64|isize|f32|f64) *=' \
     "$SRCF" | grep -vE '^[0-9]+:[[:space:]]*//' | grep -vE 'const +TEST_' >/dev/null 2>&1; then
  fail "$SRCF が数値定数を宣言している（★ 既存 SSOT を use する。テスト専用は TEST_ 接頭辞）"
fi
# ⚠️ 直書き禁止: pause / tick の閾値をリテラルで比較しない
if grep -nE '[<>=!]=?[[:space:]]*(2000|2_000|1000|1_000)\b' "$SRCF" \
     | grep -vE '^[0-9]+:[[:space:]]*//' >/dev/null 2>&1; then
  fail "$SRCF が pause / tick の閾値をリテラルで直書き比較している（★ PAUSE_THRESHOLD_MS / ENGINE_TICK_MS を使う）"
fi

echo "[acceptance 003] OK"
