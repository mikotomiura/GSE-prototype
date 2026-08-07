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

echo "--- 3. ★ 陰性対照 (ふつうのコードは 1 バイトも変えない) ---"
expect_clean "ふつうの Rust"      'pub fn next_block_number(dir: &Path) -> u32 {'
expect_clean "ふつうのコメント"   '// 送信先は配布フォルダの設定ファイルから読む'
expect_clean "ふつうの diff 見出し" 'diff --git a/src-tauri/src/reconcile.rs b/src-tauri/src/reconcile.rs'
expect_clean "型注釈のコロン"     'let block: u32 = 3;'

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
