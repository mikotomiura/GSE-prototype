#!/usr/bin/env bash
# scripts/secrets-filter.sh
# Codex CLI に渡す入力から機密情報と proprietary plugin 出力を除去する。
#
# 使い方:
#   git diff | scripts/secrets-filter.sh > /tmp/codex-input.txt
#   cat some-text | scripts/secrets-filter.sh
#   SECRETS_FILTER_REPORT=/tmp/report.txt git diff | scripts/secrets-filter.sh > out
#
# exit code:
#   0: マッチなし、安全に Codex に渡してよい
#   2: secret / proprietary 検出、置換済みだが Codex 呼び出しは呼び出し側で中止すべき
#   その他: スクリプトエラー
#
# SECRETS_FILTER_REPORT にパスを与えると、★ **どの行がなぜマッチしたか** (行番号と理由) を
# そこへ書く。⚠️ 値そのものは書かない。呼び出し側 (run-codex-review.sh --ack-filtered) が
# 「人が目で確かめる」ために使う。
#
# Phase 5 で生成、Phase 8 hook と Codex 関連 Skill から参照される。
# 注意: 第一段フィルタのみ。複数行 secret / base64 断片 / URL query 内の値を取り逃がす可能性あり。
#
# ## ⚠️★★ 2026-08-07 の修正 (security-checker の実測指摘)
#
# ★ 「大文字小文字無視」と書いてあったが **実装は区別していた** (awk の match() には
#   IGNORECASE が無い)。実測で以下が **rc=0 = 素通り**していた:
#     var SHARED_SECRET = "hunter2xx"   ← ★ このプロジェクトの実際の秘密の名前
#     API_KEY = "shortval"
#     "secret": "s3cr3t"                ← ★ g1-submit.json そのものの形
# ★ さらに、行内の置換は **16 文字以上の連続トークンしか**伏せないため、
#   短い値は「検出されたが伏せられない」まま出力に残っていた。
#   → ⚠️ 「置換済みだが中止すべき」という exit 2 の説明が半分しか本当でなかった。
# ★ 検査は `scripts/secrets-filter-test.sh` で実測する (陽性対照・陰性対照つき)。

set -euo pipefail

# 機密パターン。★ **すべて小文字で書く** (行を tolower してから照合するため)。
# ⚠️ 大文字で書くと一致しない (2026-08-07 まで実際にそうなっていた)。
SECRET_PATTERNS=(
  'openai_api_key'
  'anthropic_api_key'
  'aws_(access|secret)_key'
  'github_token'
  'gh_token'
  'begin[[:space:]]+(rsa[[:space:]]+|ec[[:space:]]+|dsa[[:space:]]+|openssh[[:space:]]+)?private[[:space:]]+key'
  # ★ 区切りは `=` だけでなく `:` も見る (JSON の `"secret": "…"` を捕まえるため)。
  #   間に `"` `'` 空白が挟まる形を許すので `[^[:alnum:]]{0,3}` を挟む。
  '(password|passwd|secret|api[_-]?key|access[_-]?token)[^[:alnum:]]{0,3}[:=]'
  'bearer[[:space:]]+[a-z0-9_-]+'
)
SECRET_REGEX=$(IFS='|'; echo "${SECRET_PATTERNS[*]}")

# Proprietary 拡張子 (docs/external-skills.md の「外部 LLM 送信禁止」と整合)
PROPRIETARY_EXTS_REGEX='\.(pdf|docx|xlsx|pptx)$'

REPORT="${SECRETS_FILTER_REPORT:-}"
[ -n "$REPORT" ] && : > "$REPORT"

awk -v secret_re="${SECRET_REGEX}" -v prop_re="${PROPRIETARY_EXTS_REGEX}" -v report="${REPORT}" '
BEGIN { skip_hunk = 0; in_pem = 0; matched = 0 }

function note(reason) {
  if (report != "") print NR ": " reason > report
}

# 複数行 PEM key の範囲スキップ
/-----BEGIN[[:space:]]+([A-Z]+[[:space:]]+)?PRIVATE[[:space:]]+KEY-----/ { in_pem = 1; matched = 1; note("PEM ブロック開始 (以降を除去)") }
in_pem {
  if ($0 ~ /-----END[[:space:]]+([A-Z]+[[:space:]]+)?PRIVATE[[:space:]]+KEY-----/) in_pem = 0
  print "[secrets-filter] SKIPPED PEM block line"; next
}

/^diff --git/ {
  skip_hunk = 0
  lower_head = tolower($0)
  if (lower_head ~ /\.(env|pem|key)([[:space:]]|$)/) skip_hunk = 1
  if (lower_head ~ /credentials|secret/) skip_hunk = 1
  # NDJSON セッションログ (キーストローク動態) は外部 LLM 送信禁止。
  # 参加者の実データは gitignore で追跡外だが、追跡下の fixture
  # (src-tauri/tests/fixtures/*.ndjson) は vk コード列を含み diff に乗る。
  # 規約の単一真実源は docs/agent-shared.md / data-privacy Skill。
  if (lower_head ~ /\.ndjson([^a-z0-9_]|$)/) skip_hunk = 1
  if (lower_head ~ prop_re) skip_hunk = 1
  if (skip_hunk) {
    print "[secrets-filter] SKIPPED hunk: " $0
    matched = 1
    note("hunk まるごと除去: " $0)
    next
  }
}
skip_hunk { next }

# 行内マッチング — 機密値を [REDACTED] に置換
# ⚠️★ **3 本とも要る。** 旧実装は 1 本目だけで、`secret=short1` のような
#   16 文字未満の値が伏せられないまま出ていた (security-checker の実測指摘)。
{
  line = $0
  if (match(tolower(line), secret_re)) {
    gsub(/[A-Za-z0-9_+\/=.-]{16,}/, "[REDACTED]", line)          # 長いトークン
    gsub(/"[^"]{4,}"/, "\"[REDACTED]\"", line)                   # 引用符つきの値
    gsub(/=[[:space:]]*[A-Za-z0-9_+\/.-]{4,}/, "=[REDACTED]", line) # 素の値 (= の右)
    gsub(/:[[:space:]]*[A-Za-z0-9_+\/.-]{4,}/, ":[REDACTED]", line) # 素の値 (: の右)
    matched = 1
    note("行内マッチ (値は [REDACTED] に置換済み)")
  }
  print line
}

END {
  if (matched) exit 2
}
'
