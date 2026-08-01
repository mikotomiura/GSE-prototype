#!/usr/bin/env bash
# scripts/secrets-filter.sh
# Codex CLI に渡す入力から機密情報と proprietary plugin 出力を除去する。
#
# 使い方:
#   git diff | scripts/secrets-filter.sh > /tmp/codex-input.txt
#   cat some-text | scripts/secrets-filter.sh
#
# exit code:
#   0: マッチなし、安全に Codex に渡してよい
#   2: secret / proprietary 検出、置換済みだが Codex 呼び出しは呼び出し側で中止すべき
#   その他: スクリプトエラー
#
# Phase 5 で生成、Phase 8 hook と Codex 関連 Skill から参照される。
# 注意: 第一段フィルタのみ。複数行 secret / base64 断片 / URL query 内の値を取り逃がす可能性あり。

set -euo pipefail

# 機密パターン (大文字小文字無視) — マッチした行は [REDACTED] に置換
SECRET_PATTERNS=(
  'OPENAI_API_KEY'
  'ANTHROPIC_API_KEY'
  'AWS_(ACCESS|SECRET)_KEY'
  'GITHUB_TOKEN'
  'GH_TOKEN'
  'BEGIN[[:space:]]+(RSA[[:space:]]+|EC[[:space:]]+|DSA[[:space:]]+|OPENSSH[[:space:]]+)?PRIVATE[[:space:]]+KEY'
  '(password|passwd|secret|api[_-]?key|access[_-]?token)[[:space:]]*='
  'Bearer[[:space:]]+[A-Za-z0-9_-]+'
)
SECRET_REGEX=$(IFS='|'; echo "${SECRET_PATTERNS[*]}")

# Proprietary 拡張子 (docs/external-skills.md の「外部 LLM 送信禁止」と整合)
PROPRIETARY_EXTS_REGEX='\.(pdf|docx|xlsx|pptx)$'

awk -v secret_re="${SECRET_REGEX}" -v prop_re="${PROPRIETARY_EXTS_REGEX}" '
BEGIN { skip_hunk = 0; in_pem = 0; matched = 0 }

# 複数行 PEM key の範囲スキップ
/-----BEGIN[[:space:]]+([A-Z]+[[:space:]]+)?PRIVATE[[:space:]]+KEY-----/ { in_pem = 1; matched = 1 }
in_pem {
  if ($0 ~ /-----END[[:space:]]+([A-Z]+[[:space:]]+)?PRIVATE[[:space:]]+KEY-----/) in_pem = 0
  print "[secrets-filter] SKIPPED PEM block line"; next
}

/^diff --git/ {
  skip_hunk = 0
  if ($0 ~ /\.(env|pem|key)([[:space:]]|$)/) skip_hunk = 1
  if ($0 ~ /credentials|secret/) skip_hunk = 1
  # NDJSON セッションログ (キーストローク動態) は外部 LLM 送信禁止。
  # 参加者の実データは gitignore で追跡外だが、追跡下の fixture
  # (src-tauri/tests/fixtures/*.ndjson) は vk コード列を含み diff に乗る。
  # 規約の単一真実源は docs/agent-shared.md / data-privacy Skill。
  if ($0 ~ /\.ndjson([^A-Za-z0-9_]|$)/) skip_hunk = 1
  if ($0 ~ prop_re) skip_hunk = 1
  if (skip_hunk) {
    print "[secrets-filter] SKIPPED hunk: " $0
    matched = 1
    next
  }
}
skip_hunk { next }

# 行内マッチング — 機密値を [REDACTED] に置換
{
  line = $0
  if (match(line, secret_re)) {
    gsub(/[A-Za-z0-9_+\/=.-]{16,}/, "[REDACTED]", line)
    matched = 1
  }
  print line
}

END {
  if (matched) exit 2
}
'
