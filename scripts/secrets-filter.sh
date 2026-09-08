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
  # ⚠️★★★ 2026-08-14 追加（`/cross-review` の HIGH が**実際に外へ出た**あとの是正）——
  #   ★ 実セッション名（`Pnnn_gse_<年月日>_<時分秒>` ＝ 擬似 ID ＋ **打鍵開始日時**）が
  #     experiments/ の検査コードに残っており、★ **本フィルタは 1 バイトも反応しなかった。**
  #   ⚠️★★★ **この注意書き自体に実名を書かないこと。** ★ 2026-08-14 に
  #     (1) 検査コードの説明コメント (2) 本フィルタの試験の陽性対照 (3) ★ **このコメント**
  #     の 3 箇所で同じ誤りを踏んだ。★ **「漏洩について書く」と「漏洩を再導入する」は同じ動作である。**
  #   ★ 2 本要る:
  #     (a) 組み立て済みの形。
  #     (b) ★★ **連結で分割された形**（`"P010" + "_gse_" + "20260721_085908"`）——
  #         ⚠️ 実際に事故ったのは (b) の形であり、(a) だけでは**また素通りする**。
  #   ⚠️★ 年は `202x` に限る。★ 架空名の約束（`_00000000_` / 年 2000）を**素通りさせる**ため
  #     ——ここで架空名まで止めると、検査の見本を持つ diff が毎回 exit 2 になり、
  #     ★ **人がフィルタを迂回する動機を作ってしまう**（それが最悪の結果）。
  'p[0-9]{3}_gse_202[0-9]{5}_[0-9]{6}'
  '_gse_[^0-9]{0,20}202[0-9]{5}'
  # ⚠️★★★ 2026-08-14 `/cross-review`（HIGH）が実測した **既知の副作用（over-block）**:
  #   ★ 既存の**合成テストフィクスチャ**が同じ形をしており、下記が実際に当たる（実測）——
  #     src-tauri/src/reconcile.rs (9) / submission.rs (6) / docs/pilot-runbook.md (7) /
  #     Form_G1/*.cjs / Form_O1/*.cjs / Form_Phase1/*.gs / docs/participant-setup-guide.md
  #   → ⚠️ **これらに触れる将来の diff は `/cross-review` でほぼ確実に rc=2 になる。**
  #   ⚠️★★ S5C-D8 が明記した設計哲学（「架空名まで止めると人がフィルタを迂回する動機を作る」）と
  #     **正面から衝突するリスク**である。
  #   ★ **弱めない**（fail-closed を先に壊さない）。★ 正しい解き方は
  #     **フィクスチャ側を `_00000000_` 形式へ寄せること**であり、S5C-D11 の独立タスクで行う。
  #   ★ それまでは `--ack-filtered`（★ 人が [REDACTED] の中身を確かめてから通す）で運用する。
  # ⚠️★★ **awk は行単位**なので、`"a"` と `"b"` を**改行で分けた連結**は見えない（実測で素通り）。
  #   ★ Python 側（step4_selftest.py の畳み込み検査）が第 2 層として塞いでいる。
)
SECRET_REGEX=$(IFS='|'; echo "${SECRET_PATTERNS[*]}")

# Proprietary 拡張子 (docs/external-skills.md の「外部 LLM 送信禁止」と整合)
# ⚠️★★★ 2026-09-08 修正: 終端を `$` にしない。
#   ★ git は **非 ASCII を含むパスを C-quote して引用符で囲む** (`core.quotepath` の既定 true)。
#     → 行末が `"` になるので `$` 終端はすべて空振りしていた (★ 下の正規化と対で直す)。
#   ⚠️ **`([^a-z0-9]|$)` には広げない** —— ★ それだと `.pptx.md` まで止まり、
#     現行仕様 (`docs/external-skills.md` は拡張子 4 種のみを禁止) を**勝手に拡大**することになる。
#     ★ `.pptx.md` を送信禁止に含めるかは **別の判断**であり、研究者に委ねる。
#   ★ **2026-09-08 追加: `.pptx.md` / `.docx.md` も止める**（★ 研究者判断）——
#     ⚠️ 実測: `[提案…]GSE設計スライド.pptx.md` は **中身が pptx の本文そのもの**（md2pptx の入力）で、
#     ★ `.pptx` バイナリを止めても **Markdown 版から本文 257 行が外へ出ていた**。
#     ⚠️ 拡張子が `.md` なのは *変換の都合* にすぎず、守るべき中身は同じである。
#   ⚠️ **副作用を承知で入れている**: 未踏提出物に触る diff は毎回 rc=2 になる。
#     → ★ そのときは `--ack-filtered`（★ 人が [REDACTED] の中身を確かめてから通す）で運用する。
PROPRIETARY_EXTS_REGEX='\.(pdf|docx|xlsx|pptx)(\.md)?([[:space:]]|$)'

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
  # ⚠️★★★ 2026-09-08 追加 —— **fail-closed が引用符つきファイル名に対して開いていた。**
  #   ★ git のヘッダは非 ASCII 名でこうなる (★ 実測):
  #       diff --git "a/docs/[æ...]GSEè¨­...pptx" "b/..."
  #   ⚠️ 末尾が `"` なので `$` 終端の判定が当たらず、
  #     ★ **実物の diff が rc=0 で素通りし、本文 257 行がそのまま出力に残っていた**
  #     (★ 陽性対照: 同じ内容でも ASCII 名なら rc=2 で止まる ＝ **違いは引用符だけ**)。
  #   → ★ 判定の前に **引用符を空白へ置き換えて正規化する** (★ 区切りとして働かせる)。
  #   ⚠️ 既存テストが `a/R.PDF` のような **引用符なしの形しか試していなかった**ため見逃していた。
  gsub(/"/, " ", lower_head)
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
