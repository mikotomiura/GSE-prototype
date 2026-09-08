#!/usr/bin/env bash
# scripts/secrets-filter-test.sh
# scripts/secrets-filter.sh が **本当に止めるか** をローカルで実測する。
#
# ⚠️★ 測るのは「フィルタを書いた」ではなく **「フィルタが機密を伏せる」** である。
#   ★ 陰性対照 (ふつうのコードは素通りする) を必ず含める。含めないと、
#     全部 [REDACTED] にする実装でも緑になる。
#
# 使い方: bash scripts/secrets-filter-test.sh   (rc=0 なら全ケース期待どおり)

set -uo pipefail
cd "$(dirname "$0")/.."
FILTER=scripts/secrets-filter.sh

ng=0
total=0

# 機密を含む行: rc=2 で、⚠️ **値が出力に残っていない**こと。
expect_blocked() {
  local label="$1" input="$2" leak="$3"
  local out rc
  out=$(printf '%s\n' "$input" | "$FILTER"); rc=$?
  total=$((total + 1))
  if [ "$rc" -ne 2 ]; then
    echo "NG   $label → rc=$rc (2 を期待)  out=$out"
    ng=$((ng + 1))
  elif [ -n "$leak" ] && printf '%s' "$out" | grep -qF -- "$leak"; then
    echo "NG   $label → rc=2 だが値が残っている: $out"
    ng=$((ng + 1))
  else
    echo "OK   $label → rc=2 / 値は残っていない"
  fi
}

# ふつうのコード: rc=0 で、★ **1 バイトも変わらない**こと (陰性対照)。
expect_clean() {
  local label="$1" input="$2"
  local out rc
  out=$(printf '%s\n' "$input" | "$FILTER"); rc=$?
  total=$((total + 1))
  if [ "$rc" -ne 0 ]; then
    echo "NG   $label → rc=$rc (0 を期待)"
    ng=$((ng + 1))
  elif [ "$out" != "$input" ]; then
    echo "NG   $label → 中身が変わった: $out"
    ng=$((ng + 1))
  else
    echo "OK   $label → 素通り"
  fi
}

echo "--- 1. 機密の形 (★ 大文字・JSON 形・短い値も止まること) ---"
# ⚠️ 下の 4 つは 2026-08-07 まで **rc=0 で素通り**していた (security-checker の実測指摘)。
expect_blocked "小文字 secret = 短い値"        'const secret = "abc123"'            'abc123'
expect_blocked "★ 大文字 SHARED_SECRET"        'var SHARED_SECRET = "hunter2xx"'    'hunter2xx'
expect_blocked "★ 大文字 API_KEY = 短い値"     'API_KEY = "shortval"'               'shortval'
expect_blocked "★ JSON 形 \"secret\": 値"       '  "secret": "s3cr3t"'               's3cr3t'
expect_blocked "★ g1-submit.json の形"          '{"endpoint":"https://x/exec","secret":"REALSECRET1"}' 'REALSECRET1'
expect_blocked "長いトークン (従来から止まる)"  'api_key = "AKIAIOSFODNN7EXAMPLE"'   'AKIAIOSFODNN7EXAMPLE'
expect_blocked "Bearer トークン"                'Authorization: Bearer abcdefghijklmnop' 'abcdefghijklmnop'
expect_blocked "password= 素の値"               'password=hunter22'                  'hunter22'

echo "--- 2. ファイル単位の除去 (hunk ごと落とす) ---"
expect_blocked "NDJSON セッションログ"          'diff --git a/s.ndjson b/s.ndjson'   ''
expect_blocked ".env"                           'diff --git a/x.env b/x.env'         ''
expect_blocked "★ 大文字の proprietary 拡張子"  'diff --git a/R.PDF b/R.PDF'         ''
expect_blocked "credentials を含む名前"         'diff --git a/my_credentials b/my_credentials' ''

echo "--- 2c. ★★★ 引用符つきのファイル名 (2026-09-08: fail-closed が開いていた形) ---"
# ⚠️★★★ git は **非 ASCII を含むファイル名を C-quote して引用符で囲む**
#   (`core.quotepath` の既定は true。★ 本 repo は未設定＝既定なので **常にこの形**)。
#   ★ ところが判定は行末 `$` に依存しており、末尾が `"` になる引用符つきでは当たらなかった。
#   ⚠️★★★ **実測 (2026-09-08)**: 作業ツリーの実 diff (日本語名の .pptx / .pptx.md) は
#     **rc=0 で素通りし、追加行 257 行がそのまま出力に残った**。
#   ⚠️ 既存ケース (`a/R.PDF` / `a/x.env`) が **引用符なしの形しか試していなかった**ため見逃していた。
#     → ★ **検査の「入力の形」を実物に合わせる。**
expect_blocked "★★★ 引用符つき .pptx (日本語名)"   'diff --git "a/docs/æ¥.pptx" "b/docs/æ¥.pptx"' ''
expect_blocked "★★★ 引用符つき .env"   'diff --git "a/æ¥.env" "b/æ¥.env"' ''
expect_blocked "★★★ 引用符つき .pem"   'diff --git "a/æ¥.pem" "b/æ¥.pem"' ''
expect_blocked "★★★ 引用符つき .key"   'diff --git "a/æ¥.key" "b/æ¥.key"' ''
expect_blocked "★★★ 引用符つき大文字 .PDF"   'diff --git "a/æ¥.PDF" "b/æ¥.PDF"' ''
# ★ 2026-09-08 (研究者判断): proprietary 資料の **Markdown 版**も止める。
#   ⚠️ 実測で `.pptx` を止めても `.pptx.md` から本文 257 行が出ていた。
#   ★ 拡張子が .md なのは変換の都合にすぎず、守るべき中身は同じである。
#   ⚠️ 副作用を承知で入れている: 未踏提出物に触る diff は毎回 rc=2 になる
#     → そのときは --ack-filtered (人が中身を確かめてから通す) で運用する。
expect_blocked "★★★ .pptx.md (proprietary の Markdown 版)" 'diff --git a/docs/deck.pptx.md b/docs/deck.pptx.md' ''
expect_blocked "★★★ .docx.md (同上)" 'diff --git a/docs/spec.docx.md b/docs/spec.docx.md' ''
expect_blocked "★★★ 引用符つき .pptx.md (★ 実物の形)" 'diff --git "a/docs/x.pptx.md" "b/docs/x.pptx.md"' ''
expect_blocked "★★★ 引用符つき .ndjson (★ 元から塞がっていた側の回帰)"   'diff --git "a/æ¥.ndjson" "b/æ¥.ndjson"' ''
# ⚠️★ **本文が実際に落ちるか**まで見る (★ rc だけ見ると「検出したが出力に残る」を見逃す)。
{
  total=$((total + 1))
  out=$(printf 'diff --git "a/æ¥.pptx" "b/æ¥.pptx"
@@ -1 +1 @@
+PROPRIETARY_BODY_TEXT
' | "$FILTER"); rc=$?
  if [ "$rc" -ne 2 ]; then
    echo "NG   ★ 引用符つき .pptx の本文除去 → rc=$rc (2 を期待)"
    ng=$((ng + 1))
  elif printf '%s' "$out" | grep -qF 'PROPRIETARY_BODY_TEXT'; then
    echo "NG   ★ 引用符つき .pptx の本文除去 → rc=2 だが **本文が残っている**"
    ng=$((ng + 1))
  else
    echo "OK   ★ 引用符つき .pptx → rc=2 / 本文は残っていない"
  fi
}

echo "--- 2b. ★★★ 実セッション名 (2026-08-14: 実際に外部 LLM へ出た形) ---"
# ⚠️★★★ 下の 2 つは 2026-08-14 まで **rc=0 で素通り**していた。
#   ★ (b) の連結形が**実際に事故った形**であり、(a) だけ足しても再発を止められない。
# ⚠️★★★ **見本は必ず架空値にする。** 陽性対照は「パターンに当たる」ことだけが要件であり、
#   実在の識別子である必要は 1 ミリも無い。★ 2026-08-14 に**ここへ実名を書いて自分で踏んだ**
#   (★ そして**このフィルタ自身が送信前に捕まえた**)。★ 架空値の条件は「年が 202x であること」だけ。
expect_blocked "★ 組み立て済みのセッション名の形" \
  '  "$D/P123_gse_20260101_000000.ndjson"' 'P123_gse_20260101_000000'
expect_blocked "★★ 連結で分割された形 (実際の事故の形)" \
  '         mut_file("run.sh", "", "# 例: P123" + "_gse_" + "20260101_000000")' '20260101_000000'

echo "--- 3. ★ 陰性対照 (ふつうのコードは 1 バイトも変えない) ---"
# ⚠️★★ 架空名は**素通りさせる** —— ここで止めると検査の見本を含む diff が毎回 exit 2 になり、
#   ★ 人がフィルタを迂回する動機を作る。★ 架空名の約束は「年が 202x でない」こと。
expect_clean "★ 架空名 (_00000000_ 形式)"  '  "$D/P000_gse_00000000_000000.ndjson"'
expect_clean "★ 架空名 (年 2000 の見本)"   'FAKE_SESSION = "P999" + "_gse_" + "20000101_000000"'
expect_clean "★ ふつうの gse 語 (誤検出しない)" 'cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson'
expect_clean "ふつうの Rust"      'pub fn next_block_number(dir: &Path) -> u32 {'
expect_clean "ふつうのコメント"   '// 送信先は配布フォルダの設定ファイルから読む'
expect_clean "ふつうの diff 見出し" 'diff --git a/src-tauri/src/reconcile.rs b/src-tauri/src/reconcile.rs'
expect_clean "型注釈のコロン"     'let block: u32 = 3;'
# ⚠️★★★ 2026-09-08 追加の陰性対照 —— ★ **引用符つきでも「ふつうのファイル」は素通りすること。**
#   ★ これが無いと「引用符が付いていたら全部止める」実装でも緑になってしまう。
expect_clean "★ 引用符つきだが普通の .rs"   'diff --git "a/src/æ¥.rs" "b/src/æ¥.rs"'
expect_clean "★ 引用符つきだが普通の .md"   'diff --git "a/docs/æ¥.md" "b/docs/æ¥.md"'
# ⚠️ 拡張子の途中一致で誤爆しないこと (★ .key と .keyboard を混同しない)
expect_clean "★ .keyboard.rs は .key ではない"   'diff --git a/src/keyboard.rs b/src/keyboard.rs'

echo "--- 4. ★ レポート (SECRETS_FILTER_REPORT) に値そのものを書かない ---"
# ⚠️ レポートは `--ack-filtered` のときに **端末へ出す**。値を書くと
#   スクロールバックとログに秘密が残る (cross-review 指摘)。
{
  rep=$(mktemp)
  printf 'ok\nconst secret = "TOPSECRETVALUE9"\n' \
    | SECRETS_FILTER_REPORT="$rep" "$FILTER" > /dev/null
  total=$((total + 1))
  if [ ! -s "$rep" ]; then
    echo "NG   レポートが空 (どの行がマッチしたか分からない)"
    ng=$((ng + 1))
  elif grep -qF 'TOPSECRETVALUE9' "$rep"; then
    echo "NG   レポートに値が書かれている: $(cat "$rep")"
    ng=$((ng + 1))
  else
    echo "OK   レポートは行番号と理由だけ → $(tr '\n' ' ' < "$rep")"
  fi
  rm -f "$rep"
}

echo
if [ "$ng" -eq 0 ]; then
  echo "全 $total ケース期待どおり"
else
  echo "$ng 件が期待と違う（全 $total ケース）"
fi
exit $((ng == 0 ? 0 : 1))
