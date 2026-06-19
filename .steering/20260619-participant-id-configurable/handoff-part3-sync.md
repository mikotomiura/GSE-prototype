# 次セッション開始プロンプト — Part 3: sync スクリプトを自動生成 ID に追従させる

> `feedback_handoff_prompt_in_steering` 方針に従い、CLAUDE.md 制約込みで固定。
> Part 1 (env 受け取り `4c9cd7b`) / Part 2 (自動生成+永続化 `6fa5bba`) は実装完了・全テスト緑・
> レビュー済み。ブランチ `feature/participant-id-configurable` にコミット済み。
> **Part 3 は scripts ドメイン (bash + PowerShell 5.1) のため別 PR・新規 `/start-task`。**

---

## 前提 (着手前に必ず)

1. **Part 1+2 を main へマージ**: `feature/participant-id-configurable` (commit `4c9cd7b`, `6fa5bba`)
   の PR を作成し main へマージする。Part 3 はマージ後の main から新ブランチを切る
   (`feature/sync-auto-participant-id`)。マージ前に着手しない。
2. `.steering/20260619-participant-id-configurable/` の **decisions.md (D4 + D4 addendum)** と
   本タスクの design.md を読む。Part 2 の解決順・永続化先 `~/.gse/participant_id`・ID 形式
   (`P`+12桁hex)・allowlist (`[A-Za-z0-9_-]`,1..=64) を把握してから着手する。

## 解決する問題 (背景)

Part 2 で logger は `raw/<auto-id>/` に自動生成 ID で記録するようになったが、sync スクリプトは
`GSE_PID` 単一前提のまま:
- `scripts/sync-session.sh:58` `PID="${GSE_PID:-P000}"` → `metrics/$PID/` (同 ps1 も同様)
- `scripts/sync-all.{sh,ps1}` は全 raw を 1 参加者前提で処理

このため自動生成 ID のセッションを sync すると **raw と metrics の ID が乖離**する
(`raw/Pabc.../` のデータが `metrics/P000/` に落ちる等)。これを構造的に一致させる。

## スコープ (候補設計 — 承認は次セッションでユーザーから取る)

- **`scripts/sync-session.{sh,ps1}`**: PID を **セッションパスの親ディレクトリ名**
  (`raw/<PID>/gse_*.ndjson` の `<PID>`) から導出する。導出不可時のみ
  `GSE_PID` → `~/.gse/participant_id` → `P000` の順でフォールバック。
  これで raw と metrics が構造的に同一 ID になる。
- **`scripts/sync-all.{sh,ps1}`**: 単一 `GSE_PID` 前提を廃し、**`raw/*/` を participant ごとに
  反復**して各 `metrics/<PID>/` へ振り分ける (現状は全 raw を 1 参加者前提で処理)。
- **ID バリデーション非対称の解消**: スクリプト側にも allowlist (`[A-Za-z0-9_-]`, 1..=64) を入れ、
  logger (`is_valid_participant_id`) と挙動を揃える (Part 1 code-reviewer MEDIUM の本対応)。
  不正なディレクトリ名は弾く。
- **docs**: `docs/development-guidelines.md §10.2` の手順を per-participant 反復に更新
  (Part 2 で「sync は未追従」と注記した箇所を「追従済み」に更新)。
- **スコープ外**: ID→被験者 対応表の運用、metrics JSON フォーマット変更、anonymize/package、
  logger 側 (`*.rs`) の変更 (Part 2 で完結済み)。

## 必須プロトコル (CLAUDE.md 準拠 — この順で)

1. **コマンド選定**: `/start-task` で新規タスク `.steering/20260619-sync-auto-participant-id/`
   を作成 → `/add-feature`。`git-workflow` Skill を参照。実装系は必ず `/start-task` が先。
2. **docs 先読み**: `@docs/agent-shared.md` リンクハブから §10 (Session データ管理) と
   §10.2.1 (PowerShell footgun) を先読み。
3. **Skill 参照**: `git-workflow` (コミット/ブランチ)。スクリプト変更のため Rust 系 Skill は不要。
4. **サブエージェント委譲**: 影響調査が要るなら `impact-analyzer` / `file-finder`
   (sync スクリプトの呼び出し元・docs 記述箇所)。
5. **PowerShell 5.1 footgun に注意** (`docs/development-guidelines.md §10.2.1`):
   `$PSHOME`/`$PSScriptRoot` が null、`Join-Path` 空返し、`LASTEXITCODE` 消費、`>` の UTF-16 BOM。
   bash は `set -euo pipefail` + `bash -n` 構文チェック必須。
6. **実装後 `code-reviewer` + `security-checker` を並列起動** (パス導出のインジェクション焦点 =
   ディレクトリ名由来の PID に allowlist が全経路でかかるか、`../` 等を弾けるか)。
7. **`/cross-review`**: jq 不在なら Codex 系統 skip → Claude 単独へ縮退し **skip 理由を完了報告に明記**
   (既知制約: 本機は jq 未導入)。
8. **検証ゲート**: bash `bash -n` 緑 + 実データ `--no-commit` dry-run 成功 / PowerShell 手動確認 /
   `sync-all` Step0 の schema parity check 緑 (`scripts/check_schema_parity.py`)。
9. `/finish-task`。`.steering/` 記録 (requirement/design/decisions/tasklist) を省略しない。

## 制約

- スクリプトのみ変更。`src-tauri/src/**/*.rs` は触らない (Part 2 で完結)。
- bash と PowerShell の **I/O 契約を対称に保つ** (位置引数 / `--output-dir` / `--no-commit` /
  exit code 0-3)。両者で PID 導出ロジックを揃える。
- 既存テスト・既存挙動 (`GSE_PID` 明示時の従来動作) を壊さない。後方互換を保つ。

## 受け入れ条件 (Part 3)

- `raw/Pabc.../gse_*.ndjson` を sync → `metrics/Pabc.../` に出力 (raw と同一 ID)。
- `sync-all` が複数 `raw/*/` を各々正しい `metrics/<PID>/` へ振り分ける。
- 不正なディレクトリ名は allowlist で弾く (logger と同基準)。
- `GSE_PID` 明示時の従来挙動が不変 (後方互換)。
- bash `bash -n` 緑 + dry-run 成功 / PowerShell 手動確認 / `sync-all` Step0 schema parity 緑。
- code-reviewer / security-checker の CRITICAL/HIGH 指摘なし (あれば対応)。

---

## 貼り付け用プロンプト (新セッションで /clear 後に投入)

```
.steering/20260619-participant-id-configurable/handoff-part3-sync.md に従い、Part 3
(sync スクリプトを Part 2 の自動生成参加者 ID に追従させる) を実装してください。

着手前に必ず: Part 1+2 の feature ブランチ feature/participant-id-configurable (4c9cd7b, 6fa5bba)
を main へ PR マージ → main から新ブランチ feature/sync-auto-participant-id を切る。
decisions.md (D4 + addendum) と §10.2.1 PowerShell footgun を読む。

問題: Part 2 で logger は raw/<auto-id>/ に自動生成 ID (P+12桁hex) で記録するが、sync は
GSE_PID 単一前提 (sync-session.sh:58 PID=${GSE_PID:-P000} → metrics/$PID/) のため raw と
metrics の ID が乖離する。

候補設計 (承認は会話で取る): sync-session.{sh,ps1} は PID を raw/<PID>/ パスの親ディレクトリ名
から導出 (不可時のみ GSE_PID→~/.gse/participant_id→P000)。sync-all.{sh,ps1} は raw/*/ を
participant ごとに反復し metrics/<PID>/ へ振り分け。スクリプト側にも allowlist
([A-Za-z0-9_-],1..=64) を入れ logger と挙動を揃える。docs §10.2 を per-participant 反復に更新。
スコープ外: 対応表運用・metrics フォーマット変更・*.rs の変更。

CLAUDE.md 準拠で: /start-task → /add-feature → git-workflow Skill 参照 → 実装 →
code-reviewer + security-checker 並列 (焦点=パス導出のインジェクション/allowlist) →
/cross-review (jq 不在なら Claude 単独へ縮退し skip 理由明記) → bash -n + dry-run /
PowerShell 手動確認 / schema parity 緑 → /finish-task。
制約: スクリプトのみ (src-tauri/*.rs は触らない)・bash と PowerShell の I/O 契約を対称に・
GSE_PID 明示時の後方互換を保つ・PowerShell 5.1 footgun (§10.2.1) に注意。
```
