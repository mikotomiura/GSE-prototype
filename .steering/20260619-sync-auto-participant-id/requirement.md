# sync-auto-participant-id — sync スクリプトを自動生成参加者 ID に追従させる

## 背景

Part 2 (`6fa5bba`, main マージ済 PR #14) で logger は `raw/<auto-id>/` に自動生成 ID
(`P` + 12桁hex) で記録するようになった。しかし sync スクリプトは `GSE_PID` 単一前提のまま:

- `scripts/sync-session.sh` / `.ps1`: `PID="${GSE_PID:-P000}"` → `metrics/$PID/`
- `scripts/sync-all.sh` / `.ps1`: 全 raw を 1 参加者前提で処理

このため自動生成 ID のセッションを sync すると **raw と metrics の ID が乖離**する
(`raw/Pabc.../` のデータが `metrics/P000/` に落ちる)。実データ収集で ID 不一致は静かな
データ汚染になり、本プロジェクトの重視品質「正確性」に直結する。これを構造的に一致させる。

関連: `.steering/20260619-participant-id-configurable/decisions.md` D4 + addendum
(自動生成 ID 形式・永続化先・allowlist 基準) / 同 handoff-part3-sync.md。

## ゴール

raw と metrics の参加者 ID が構造的に一致し、複数被験者の raw を各々正しい metrics へ
振り分けられる。スクリプト側 ID バリデーションを logger (`is_valid_participant_id`) と揃える。

## スコープ

### 含むもの
- `scripts/sync-session.{sh,ps1}`: PID を `raw/<PID>/gse_*.ndjson` の親ディレクトリ名から導出。
  導出不可時のみ `GSE_PID` → `~/.gse/participant_id` → `P000` の順でフォールバック。
- `scripts/sync-all.{sh,ps1}`: 単一 `GSE_PID` 前提を廃し、`raw/*/` を participant ごとに
  反復して各 `metrics/<PID>/` へ振り分け。
- スクリプト側 allowlist (`[A-Za-z0-9_-]`, 1..=64) を全 PID 経路に適用 (logger と同基準、
  Part 1 code-reviewer MEDIUM の本対応)。不正ディレクトリ名・`../` 等は弾く。
- `docs/development-guidelines.md §10.2` を per-participant 反復に更新
  (Part 2 で「sync は未追従」と注記した箇所を「追従済み」に)。

### 含まないもの
- ID→被験者 対応表の運用
- metrics JSON フォーマット変更、anonymize/package
- logger 側 (`src-tauri/src/**/*.rs`) の変更 (Part 2 で完結済)

## 受け入れ条件

- [ ] `raw/Pabc.../gse_*.ndjson` を sync → `metrics/Pabc.../` に出力 (raw と同一 ID)
- [ ] `sync-all` が複数 `raw/*/` を各々正しい `metrics/<PID>/` へ振り分ける
- [ ] 不正なディレクトリ名は allowlist で弾く (logger と同基準)
- [ ] `GSE_PID` 明示時の従来挙動が不変 (後方互換)
- [ ] bash `bash -n` 緑 + dry-run (`--no-commit`) 成功 / PowerShell 手動確認 /
      `sync-all` Step0 schema parity 緑
- [ ] code-reviewer / security-checker の CRITICAL/HIGH 指摘なし
- [ ] bash と PowerShell の I/O 契約が対称 (位置引数 / `--output-dir` / `--no-commit` / exit 0-3)

## 関連ドキュメント

- docs/development-guidelines.md §10 (Session データ管理) / §10.2 / §10.2.1 (PowerShell footgun)
- .steering/20260619-participant-id-configurable/decisions.md (D4 + addendum)
- .steering/20260619-participant-id-configurable/handoff-part3-sync.md

## 運用メモ
- /reimagine 適用: No
- 理由: handoff に承認候補設計 (パス親ディレクトリ名から PID 導出 + per-participant 反復 +
  allowlist 対称化) が明示され、最良案がほぼ自明。スクリプトのみの局所変更で破壊的でなく、
  複数案の比較で得るものが少ない。設計の対称性 (bash↔ps1 I/O 契約) は design.md で詰める。
