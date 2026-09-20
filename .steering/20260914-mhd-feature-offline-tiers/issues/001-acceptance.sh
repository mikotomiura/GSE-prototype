#!/usr/bin/env bash
# issue 001 の AC 検査 — ⚠️ cargo test が無条件に緑になる部分を補う。
#   ★ 「新特徴が **実際に出力に出ている**」ことだけをここで見る（★ 正しさは単体テストの担当）。
#   ★ worktree の中で実行される (loop-run.sh の acceptance 段)。
# ⚠️★★★ 2026-09-20（封筒・起票 2）: `--features` の出力は
#   **`{ provenance, config, rows }` の封筒**になった（判断 25 #14）。
#   ★ 本検査は取得時に `jq '.rows'` で**行だけを取り出して**おり、
#     以降の `.[]` / `all(.[]; ...)` は封筒を剥がした後の配列を指す。
#   ⚠️★★★ **この検査は `provenance` と `config` を 1 つも見ていない。**
#     ★ 封筒自体の検査は `.steering/20260920-envelope-issues/envelope-acceptance.sh` が持つ。
#   ★ 封筒が無い（配列のままの）出力では `jq '.rows'` が失敗し、
#     `set -o pipefail` によりその場で赤になる（fail-closed）。
set -uo pipefail
fail() { echo "[acceptance 001] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"

cd src-tauri || fail "src-tauri が無い"
out="$(cargo run --quiet --bin gse-replay -- tests/fixtures/minimal.ndjson --features 2>/dev/null | jq -e '.rows | arrays')" \
  || fail "gse-replay --features が非 0 で終了した、または封筒の .rows を取り出せない（★ { provenance, config, rows } の形か確認）"
[ -n "$out" ] || fail "--features の出力が空"

printf '%s' "$out" | jq -e 'type == "array" and length > 0' >/dev/null 2>&1 \
  || fail "出力が非空の JSON 配列でない"

# AC2: 全行が t_ms と activity の 6 フィールドを持つ
printf '%s' "$out" | jq -e '
  all(.[];
    has("t_ms")
    and (.activity | type == "object")
    and (.activity | has("keys") and has("deletes") and has("pastes")
         and has("mean_iki_ms") and has("pauses") and has("net_production")))' >/dev/null 2>&1 \
  || fail "全行に t_ms / activity の 6 フィールドが揃っていない"

# AC3: ⚠️ 退化していないこと（★ 全部 0 の出力を緑にしない）
printf '%s' "$out" | jq -e '[.[].activity.keys] | add > 0' >/dev/null 2>&1 \
  || fail "activity.keys の総和が 0（★ 出力が退化している）"

# AC3b: ⚠️★★★ paste も退化していないこと（★ 2026-09-15 追加・レビュー MEDIUM）
#   ★ minimal.ndjson:22 は `{"type":"paste","t":...}` で external_paste_chars を持たない。
#   ⚠️ `collect_paste_events`（--metrics 用）はこれを落とすので、そのまま使うと
#     全 tick が pastes: 0 になる ＝「paste が無かった」と「文字数が取れなかった」が潰れる。
printf '%s' "$out" | jq -e '[.[].activity.pastes] | add > 0' >/dev/null 2>&1 \
  || fail "activity.pastes の総和が 0（★ 文字数欠落の paste 行を落としていないか確認すること）"

# AC2b: ⚠️★★★ 出力のキー集合が**完全一致**すること（★ privacy の門を両側にする）
#   ⚠️ has() の存在確認だけだと、将来 vk / app / window_title を足しても緑のまま通る。
#   ⚠️★★★ 2026-09-18（decisions.md 判断 18）: 最上位の集合は **002 で boundary が加わった時点から
#     この行で NG になっていた**（★ 各 issue の裁定が自分の acceptance しか回していなかったので見逃した）。
#     ★ Tier を足す issue を merge したら、裁定セッションがここへ 1 語足す（★ 最上位の門はここ 1 か所）。
#   ★ 2026-09-20: issue 004（`revision`）/ 006（`restart`）の実装と**同じコミットで** 2 語足した。
printf '%s' "$out" | jq -e '
  all(.[];
    (keys_unsorted | sort) == ["activity","boundary","dispersion","quality","restart","revision","stall_onset","t_ms"]
    and (.activity | keys_unsorted | sort)
        == ["deletes","keys","mean_iki_ms","net_production","pastes","pauses"])' >/dev/null 2>&1 \
  || fail "出力のキー集合が想定と完全一致しない（★ フィールドの増減を検査している）"

# AC10b: ⚠️★★★ 巨大な時刻ギャップで暴走しないこと（★ 2026-09-15 追加・レビュー HIGH）
#   ★ 実測: 251 バイト・2 行の入力に t=0 と t=1e8 を並べると 100,001 行出た。
#   ⚠️ tick 数は**入力サイズではなく時刻スパン**に比例するので MAX_SESSION_BYTES で防げない。
gapfile="$(mktemp)"; trap 'rm -f "$gapfile"' EXIT
{
  echo '{"type":"meta","session_start":1700000000000,"hmm_version":"0.2.0"}'
  echo '{"type":"session_start","t":1700000000000}'
  echo '{"type":"key","t":1700000000000,"category":"alphabetic","press":true}'
  echo '{"type":"key","t":1900000000000,"category":"alphabetic","press":true}'
} > "$gapfile"
if cargo run --quiet --bin gse-replay -- "$gapfile" --features >/dev/null 2>&1; then
  fail "巨大な時刻ギャップ（2e11 ms）の入力が exit 0 になった（★ 上限で止めること・ADR-030 D9）"
fi

# AC6: ⚠️ 新しい数値定数を導入していないこと ＋ ★ SSOT を実際に参照していること
#   ★ ADR-030 D3 逐語「新しい定数を作らず、既存パラメータを対称に再利用する」。
#   ⚠️★★★ 2026-09-15 に 3 本へ強化した（`decisions.md` 判断 7）——
#     初版は `const NAME: ... = <数値>` の**宣言**しか見ておらず、
#     ★ `>= 2000` と**直書き**されたら緑のまま通る穴があった。
FEATDIR="src/analysis/feat_offline"

# (1) 否定形: 数値定数の宣言が feat_offline/ 配下に無いこと
#   ⚠️★★★ 2026-09-15: 範囲を activity.rs から**ディレクトリ全体**へ広げた。
#   ★ 理由（実測）: 初版は activity.rs しか見ておらず、worker が mod.rs に
#     `pub const TICK_MS: u64 = 1000;`（= `loop_step::ENGINE_TICK_MS` の再宣言）を
#     置いたのを**緑のまま通した**。AC 6 が禁じた事象そのものだった。
#   ★ テストコードの定数は許す（`#[cfg(test)]` 配下は実装の judgment quantity ではない）。
if grep -rnE '^[[:space:]]*(pub )?const [A-Z_]+[[:space:]]*:[^=]*=[[:space:]]*[0-9]' \
     "$FEATDIR" | grep -v 'TEST_' >/dev/null 2>&1; then
  fail "$FEATDIR に新しい数値定数が宣言されている（★ 既存定数を use すること。テスト用は TEST_ 接頭辞）"
fi

# (2) 肯定形: 既存 SSOT を実際に参照していること
#   ⚠️ 「新しい定数が無い」だけでは「閾値を直書きした」と区別できない。
grep -rq 'PAUSE_THRESHOLD_MS' "$FEATDIR" \
  || fail "$FEATDIR が features.rs::PAUSE_THRESHOLD_MS を参照していない（★ pause 閾値の SSOT）"
grep -rq 'ENGINE_TICK_MS' "$FEATDIR" \
  || fail "$FEATDIR が loop_step::ENGINE_TICK_MS を参照していない（★ 1 Hz グリッドの SSOT）"

# (3) 直書きの禁止: 閾値としての 2000 リテラルが残っていないこと
#   ★ 比較の形だけを見る（⚠️ テストの合成タイムスタンプ `key_at(2000)` を誤検出しないため）。
#   ⚠️ 2026-09-18（判断 18）: **コメント行を除外する段**を足した。★ 判断 16 は 002〜006 には入れたが
#     001 に入れ漏れており、`dispersion.rs` の doc コメント「`< 1000 < 2000`」（判断 16 自身が足した証明）で落ちていた。
#     ★ `grep -rn` の出力は `path:line:content` なので、除外の形も 002〜006 と違う。
if grep -rnE '(>=|<=|<|>|==|!=)[[:space:]]*2_?000([^0-9]|$)' "$FEATDIR" \
     | grep -vE '^[^:]+:[0-9]+:[[:space:]]*//' | grep -q .; then
  fail "$FEATDIR に閾値として直書きされた 2000 がある（★ PAUSE_THRESHOLD_MS を使うこと）"
fi

# AC8: ★ pause / net の抽出が mod.rs の共有ヘルパとして公開されていること
#   ⚠️ Codex TASK-PRE 指摘 5: 後続 issue が局所的な pause 定義を持つと、
#     issue 005 (stall onset) が別定義を要求して破壊的変更になる。
MODRS="src/analysis/feat_offline/mod.rs"
grep -qE '^[[:space:]]*pub fn [a-z_]*pause' "$MODRS"   || fail "$MODRS に pause 抽出の pub 関数が無い（★ 共有ヘルパとして公開すること）"
grep -qE '^[[:space:]]*pub fn [a-z_]*net' "$MODRS"   || fail "$MODRS に net 計算の pub 関数が無い（★ 共有ヘルパとして公開すること）"

# AC9: ★ Tier ごとの causal / retrospective の区分が書かれていること
#   ⚠️ Codex TASK-PRE 指摘 3: 「その時点で既知」と「後から付けたラベル」を tick 行で混ぜない。
grep -qEi '(causal|retrospective)' "$MODRS"   || fail "$MODRS に Tier ごとの causal / retrospective の区分が書かれていない"

echo "[acceptance 001] OK"
