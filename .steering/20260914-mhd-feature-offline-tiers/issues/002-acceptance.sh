#!/usr/bin/env bash
# issue 002 (T1b 境界) の AC 検査
#
# ⚠️★★★ 2026-09-15 改訂 (decisions.md 判断 12):
#   ★ fixture を argumentative_ime_mixed.ndjson → instrument_rich.ndjson へ差し替えた。
#     理由: **既存 fixture には ime_shadow 行が 1 本も無い**ので、旧 AC5 は原理的に充たせなかった。
#   ★ 併せて引き継ぎ §4 の「3 点セット + キー集合の完全一致 + 非退化」の型に揃えた。
set -uo pipefail
fail() { echo "[acceptance 002] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"
cd src-tauri || fail "src-tauri が無い"
SRCF="src/analysis/feat_offline/boundary.rs"
FIXTURE="tests/fixtures/instrument_rich.ndjson"

[ -f "$FIXTURE" ] || fail "$FIXTURE が無い（★ 裁定セッションが用意した fixture。自分で作らない）"
[ -f "$SRCF" ]    || fail "$SRCF が無い"

out="$(cargo run --quiet --bin gse-replay -- "$FIXTURE" --features 2>/dev/null)" \
  || fail "gse-replay --features が非 0 で終了した"
[ -n "$out" ] || fail "--features の出力が空"

# AC1 / AC2: boundary の必須フィールド（★ sentence_punctuation が分離していること）
printf '%s' "$out" | jq -e '
  all(.[];
    (.boundary | type == "object")
    and (.boundary | has("prev_cat_counts") and has("next_cat_counts")
         and has("space") and has("enter") and has("sentence_punctuation")
         and has("ime_dwell_ms") and has("ime_nav") and has("ime_abandon")))' >/dev/null 2>&1 \
  || fail "全行に boundary の必須フィールドが揃っていない"

# ⚠️★★★ 出力キー集合の**完全一致**（★ 引き継ぎ §4）。
#   フィールドが増えたら落とす = privacy の門を両側にする。増やすときは本検査を先に直すこと。
printf '%s' "$out" | jq -e '
  [.[].boundary | keys_unsorted[]] | unique
  == ["enter","ime_abandon","ime_dwell_ms","ime_nav","next_cat_counts",
      "prev_cat_counts","sentence_punctuation","space"]' >/dev/null 2>&1 \
  || fail "boundary のキー集合が AC1 の 8 個と完全一致しない（★ 増えても減っても落とす）"

# AC2: ⚠️ sentence_punctuation が punctuation に畳まれていないこと。
#   ★ 検査は 2 段にする（⚠️ 2026-09-15 改訂・decisions.md 判断 13）:
#   (a) **行レベルの計数**が立つこと —— ★ fixture は vk=188 (,) と vk=190 (.) を 1 個ずつ持つ。
#       ⚠️ ここは pause と無関係に必ず立つので、**畳み込みを最も確実に検出する**。
printf '%s' "$out" | jq -e '[.[].boundary.sentence_punctuation] | add > 0' >/dev/null 2>&1 \
  || fail "sentence_punctuation の総和が 0（★ fixture は vk=188 と vk=190 を持つ。punctuation に畳まれている疑い）"
#   (b) **pause 境界のカテゴリ**にも現れること —— ★ fixture の 2 本目の pause は
#       直前が vk=190 (.) である（⚠️ この前提が崩れたら本検査は落ちる。fixture 側を直すこと）。
printf '%s' "$out" | jq -e '
  [.[].boundary.prev_cat_counts | keys[]] + [.[].boundary.next_cat_counts | keys[]] | unique
  | index("sentence_punctuation") != null' >/dev/null 2>&1 \
  || fail "prev/next_cat_counts に sentence_punctuation が 1 度も現れない（★ fixture の 2 本目の pause は直前が vk=190）"

# AC3: prev_cat_counts のキーは KeyCategory の 14 種のうちのものだけ
printf '%s' "$out" | jq -e --argjson cats '
  ["alphabetic","numeric","punctuation","sentence_punctuation","tab","backspace","delete",
   "space","enter","navigation","modifier","function","escape","other"]' '
  ([.[].boundary.prev_cat_counts, .[].boundary.next_cat_counts | keys[]] | unique) - $cats | length == 0' \
  >/dev/null 2>&1 \
  || fail "prev/next_cat_counts に KeyCategory 14 種以外のキーがある（★ anonymize.rs::KeyCategory が SSOT）"

# AC5: ⚠️ 退化していないこと（★ instrument_rich は ime_shadow を 2 行持つ:
#   dwell_ms 650 / 920・nav 2 / 3・abandon false / true）
printf '%s' "$out" | jq -e '[.[].boundary.ime_dwell_ms] | add > 0' >/dev/null 2>&1 \
  || fail "ime_dwell_ms の総和が 0（★ ime_shadow を含む fixture なのに出力が退化している）"
printf '%s' "$out" | jq -e '[.[].boundary.ime_nav] | add > 0' >/dev/null 2>&1 \
  || fail "ime_nav の総和が 0（★ fixture の nav は 2 と 3）"
printf '%s' "$out" | jq -e '[.[].boundary.ime_abandon] | add > 0' >/dev/null 2>&1 \
  || fail "ime_abandon の総和が 0（★ fixture の abandon は false / true。true が 1 件ある）"
printf '%s' "$out" | jq -e '([.[].boundary.space] | add > 0) and ([.[].boundary.enter] | add > 0)' >/dev/null 2>&1 \
  || fail "space / enter が全行 0（★ fixture は vk=32 を 3 回・vk=13 を 1 回持つ）"

# AC6: ⚠️ abandon を「迷い」と解釈する語を置かない（★ 起票 6: ライブ変換 ON で偽陽性が立つ）
if grep -nEi '(迷い|hesitat|ためらい)' "$SRCF" >/dev/null 2>&1; then
  fail "$SRCF が abandon を迷いと解釈している（★ 起票 6 より、行数は変換回数の代理にならない）"
fi

# AC7: ★ pause / net は issue 001 の共有ヘルパを使うこと（⚠️ 局所定義を作らない）
#   ⚠️ Codex TASK-PRE 指摘 5: 局所定義は issue 005 (stall onset) との破壊的な食い違いを生む。
#   ★ 引き継ぎ §4 の 3 点セット: 否定形 / 肯定形 / 直書き禁止。
#   ⚠️ 「関数名が違うだけ」で抜けないよう、**数値定数の宣言**と**リテラル直書き**の両方を見る。
if grep -nE '^[[:space:]]*(pub )?fn [a-z_]*(extract_pauses|compute_net|pause_list)' "$SRCF" >/dev/null 2>&1; then
  fail "$SRCF が pause / net を独自に定義している（★ mod.rs の共有ヘルパを使うこと）"
fi
if grep -nE '^[[:space:]]*(pub )?const +[A-Z_]+ *: *(u8|u16|u32|u64|usize|i8|i16|i32|i64|isize|f32|f64) *=' \
     "$SRCF" | grep -vE 'const +TEST_' >/dev/null 2>&1; then
  fail "$SRCF が数値定数を宣言している（★ 既存 SSOT を use する。テスト専用は TEST_ 接頭辞）"
fi
if grep -nE '[<>=!]=?[[:space:]]*(2000|2_000|1000|1_000)\b' "$SRCF" >/dev/null 2>&1; then
  fail "$SRCF が pause / tick の閾値をリテラルで直書き比較している（★ PAUSE_THRESHOLD_MS / ENGINE_TICK_MS を使う）"
fi
grep -qE 'super::|crate::analysis::feat_offline::' "$SRCF" \
  || fail "$SRCF が mod.rs の共有ヘルパを参照していない"

# ★ 肯定形: 共有ヘルパを**実際に呼んでいる**こと（⚠️ 否定形だけでは 001 で抜けた）
grep -qE 'extract_pause_resumptions' "$SRCF" \
  || fail "$SRCF が extract_pause_resumptions を呼んでいない（★ pause の定義は 001 の共有ヘルパが SSOT）"

echo "[acceptance 002] OK"
