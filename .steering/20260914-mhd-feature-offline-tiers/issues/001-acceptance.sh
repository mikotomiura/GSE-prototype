#!/usr/bin/env bash
# issue 001 の AC 検査 — ⚠️ cargo test が無条件に緑になる部分を補う。
#   ★ 「新特徴が **実際に出力に出ている**」ことだけをここで見る（★ 正しさは単体テストの担当）。
#   ★ worktree の中で実行される (loop-run.sh の acceptance 段)。
set -uo pipefail
fail() { echo "[acceptance 001] NG: $*" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || fail "jq が無い"

cd src-tauri || fail "src-tauri が無い"
out="$(cargo run --quiet --bin gse-replay -- tests/fixtures/minimal.ndjson --features 2>/dev/null)" \
  || fail "gse-replay --features が非 0 で終了した"
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

# AC6: ⚠️ 新しい数値定数を導入していないこと ＋ ★ SSOT を実際に参照していること
#   ★ ADR-030 D3 逐語「新しい定数を作らず、既存パラメータを対称に再利用する」。
#   ⚠️★★★ 2026-09-15 に 3 本へ強化した（`decisions.md` 判断 7）——
#     初版は `const NAME: ... = <数値>` の**宣言**しか見ておらず、
#     ★ `>= 2000` と**直書き**されたら緑のまま通る穴があった。
FEATDIR="src/analysis/feat_offline"

# (1) 否定形: 数値定数の宣言が activity.rs に無いこと（★ 初版どおりの範囲）
if grep -nE '^[[:space:]]*(pub )?const [A-Z_]+[[:space:]]*:[^=]*=[[:space:]]*[0-9]' \
     "$FEATDIR/activity.rs" >/dev/null 2>&1; then
  fail "activity.rs に新しい数値定数が宣言されている（★ features.rs の既存定数を use すること）"
fi

# (2) 肯定形: pause 閾値の SSOT を実際に参照していること
#   ⚠️ 「新しい定数が無い」だけでは「閾値を直書きした」と区別できない。
grep -rq 'PAUSE_THRESHOLD_MS' "$FEATDIR" \
  || fail "$FEATDIR が features.rs::PAUSE_THRESHOLD_MS を参照していない（★ pause 閾値の SSOT）"

# (3) 直書きの禁止: 閾値としての 2000 リテラルが残っていないこと
#   ★ 比較の形だけを見る（⚠️ テストの合成タイムスタンプ `key_at(2000)` を誤検出しないため）。
if grep -rnE '(>=|<=|<|>|==|!=)[[:space:]]*2_?000([^0-9]|$)' "$FEATDIR" >/dev/null 2>&1; then
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
