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

# ⚠️★★★ 2026-09-26 張り直し（P1-main-prep issue 008・`.steering/20260926-p1-main-prep/decisions.md` 判断 9）:
#   **`feat` 行が 1 本も無い入力では、`pause_*` は全行 null になった**（観測区間が確定しないので値で埋めない・
#   onset と同じ向き）。deep_silence / instrument_rich は **`feat` 行を 1 本も持たない**ので、
#   旧検査（`pause_max_ms` が全行 null でないこと・窓を 1 tick に戻す陽性対照）はそのままでは空振りでなく**赤**になる。
#   → ★ 値の検査は **fixture の一時コピーに 1Hz の `feat` 行を足した版**で行う（fixture 本体は変えない）。
#     穴の無い `feat` 行を敷き詰めるので、旧挙動（窓を切らない）と同じ値が出る = 検査の意図（沈黙を含む入力で
#     pause 分位点が退化していない）を保ったまま残せる。緩めてはいない。
#   ★ 0 本のままの入力は「**全行 null**」を新しい検査にする（下）。
#     ⚠️ 上の null が「入力に pause が無いから」ではないことは、`feat` 行を足した版の非 null が対照になる。
tmpd="$(mktemp -d)" || fail "一時ディレクトリを作れない"
trap 'rm -rf "$tmpd"' EXIT

# with_feat_copy <src> <dst>: <src> の全行の時刻（最小〜最大＋1 秒）を覆う 1Hz の feat 行を足した一時コピーを作る。
#   ⚠️ feat 行の値は読まれない（観測区間の判定に使うのは時刻だけ）ので 0 埋めでよい。
with_feat_copy() {
  local lo hi t
  lo="$(jq -s '[.[] | .t? | numbers] | min' "$1" | tr -d '\r')" || return 1
  hi="$(jq -s '[.[] | .t? | numbers] | max' "$1" | tr -d '\r')" || return 1
  case "$lo$hi" in ''|*null*) return 1 ;; esac
  cat "$1" > "$2" || return 1
  # 末尾に改行が無いと最初の feat 行が最終行に繋がる。
  [ -z "$(tail -c1 "$1")" ] || printf '\n' >> "$2"
  t="$lo"
  while [ "$t" -le "$((hi + 1000))" ]; do
    printf '{"type":"feat","t":%s,"f1":0.0,"f3":0.0,"f4":0.0,"f5":0.0,"f6":0.0,"p_flow":0.34,"p_inc":0.33,"p_stuck":0.33,"raw_x":0.0,"raw_y":0.0,"ewma_x":0.0,"ewma_y":0.0,"obs":0,"alpha":0.3}\n' "$t" >> "$2"
    t=$((t + 1000))
  done
}

DEEP="tests/fixtures/deep_silence.ndjson"
RICH="tests/fixtures/instrument_rich.ndjson"
for f in "$DEEP" "$RICH"; do
  [ "$(grep -c '"type":"feat"' "$f")" -eq 0 ] \
    || fail "前提が崩れた: $f に feat 行がある（★ 下の「feat 行 0 本 → 全行 null」の検査が別の入力を見ることになる）"
done
with_feat_copy "$DEEP" "$tmpd/deep_silence.ndjson" || fail "deep_silence の feat 行つきコピーを作れない"
with_feat_copy "$RICH" "$tmpd/instrument_rich.ndjson" || fail "instrument_rich の feat 行つきコピーを作れない"
[ "$(grep -c '"type":"feat"' "$tmpd/deep_silence.ndjson")" -ge 1 ] || fail "コピーに feat 行が入っていない（★ 値の検査が空振りする）"

# ★ feat 行 0 本の入力（fixture 本体）は pause_* が全行 null（判断 9）。
for f in "$DEEP" "$RICH"; do
  z="$(cargo run --quiet --bin gse-replay -- "$f" --features 2>/dev/null | jq -e '.rows | arrays')" \
    || fail "gse-replay --features が非 0 で終了した、または封筒の .rows を取り出せない ($f)"
  printf '%s' "$z" | jq -e '
    (length > 0) and all(.[] | .dispersion;
      .pause_p50_ms == null and .pause_p90_ms == null and .pause_max_ms == null)' >/dev/null 2>&1 \
    || fail "$f は feat 行 0 本なのに pause_* に値がある（★ 観測区間が確定しない入力は値で埋めない・判断 9）"
done

out="$(cargo run --quiet --bin gse-replay -- "$tmpd/deep_silence.ndjson" --features 2>/dev/null | jq -e '.rows | arrays')" \
  || fail "gse-replay --features が非 0 で終了した、または封筒の .rows を取り出せない（★ { provenance, config, rows } の形か確認）"
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
#     - ★ `feat` 行を持たない fixture（19 本中 7 本・2026-09-26 に JSON として数えた値）: `pause_*` が全行 null（判断 9）
#   ★ これらを「壊れている」と誤診して直しにいかないこと。
#   ★ instrument_rich も上のとおり `feat` 行つきの一時コピーで見る（fixture 本体は全行 null）。
out2="$(cargo run --quiet --bin gse-replay -- "$tmpd/instrument_rich.ndjson" --features 2>/dev/null | jq -e '.rows | arrays')" \
  || fail "gse-replay --features が非 0 で終了した、または封筒の .rows を取り出せない (instrument_rich)"
printf '%s' "$out2" | jq -e '[.[].dispersion.pause_max_ms | select(. != null)] | length > 0' >/dev/null 2>&1 \
  || fail "instrument_rich で pause_max_ms が全行 null（★ 同 fixture は pause を 2 本持つ）"

# ⚠️★★★ 2026-09-25 置き換え（issue 003・`.steering/20260921-p1-prereg-cli-poles/` 判断 4・起票 7 の裁定）:
#   旧: 「いま p50 == p90 == max であること」を固定していた（★ code-reviewer HIGH-1・構造的帰結:
#       PAUSE_THRESHOLD_MS(2000) > ENGINE_TICK_MS(1000) なので 1 tick に pause は高々 1 本）。
#   → 集約窓を 30 秒ローリング窓（既定 t1a_window_ms）に広げて退化は**解けた**ので、その固定は撤去した。
#   ★ 代わりに **窓を 1 tick に戻すと退化が再現する**（= 構造的帰結の証明が今も成り立つ）ことを固定する。
#   ⚠️ 窓が実際に効いていること（p50 != max の行が出る）は、新タスクの 003-acceptance.sh AC3 / AC4 が持つ。
narrow="$(cargo run --quiet --bin gse-replay -- "$tmpd/deep_silence.ndjson" --features --set t1a_window_ms=1000 2>/dev/null | jq -e '.rows | arrays')" \
  || fail "gse-replay --features --set t1a_window_ms=1000 が非 0 で終了した、または封筒の .rows を取り出せない"
printf '%s' "$narrow" | jq -e '
  [.[] | .dispersion | select(.pause_p50_ms != null)] | length > 0' >/dev/null 2>&1 \
  || fail "窓を 1 tick にしても pause 分位点が全行 null（★ 比較の母集団が空だと下の検査が空振りする）"
printf '%s' "$narrow" | jq -e '
  all(.[] | .dispersion | select(.pause_p50_ms != null);
    .pause_p50_ms == .pause_p90_ms and .pause_p90_ms == .pause_max_ms)' >/dev/null 2>&1 \
  || fail "窓を 1 tick に戻しても p50/p90/max が同値にならない（★ 構造的退化の証明が崩れたか、窓の実装が 1 tick と一致していない）"

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
