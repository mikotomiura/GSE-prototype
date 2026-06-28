# タスクリスト

## 準備
- [x] next-session-prompt.md 精読
- [x] 並列先読み: probe_scheduler.rs / lib.rs プローブ駆動 / package.rs / unpack.rs / prereg / research-positioning / setup-guide / runbook / experiment-tracking
- [x] 既存 probe-timing サーベイ [V18]-[V23] 確認

## T0 落合サーベイ（実装前の前提）
- [x] Q1 ESM/EMA サンプリング密度 vs compliance/負担 → [V24][V25][V26]
- [x] Q2 within-person 較正に必要なラベル数（GATE2 ≥20 妥当性）→ [V27][V28]
- [x] Q3 event-contingent (self-report) compliance → [V24]（率不可測）
- [x] Q4 データ収集 UX と retention → [V29]
- [x] 落合カード 5 本作成（docs/literature/20260628-calibration-sampling-density.md）
- [x] _index.md 追記・references.md(V24–V29) append-only
- [x] WebSearch で実在確認（provisional は明示）

## §2 数値確定（T0 を根拠に）→ decisions.md D1–D5
- [x] D1 較正 probe レート（λ=1/6分・gap_min=3分・max_gap=10分・cap=4）
- [x] D2 GATE2 ≥20 件/人＝floor として妥当（閾値不変）
- [x] D3 提出方式 A（自動検出ダブルクリック・ラッパー）
- [x] D4 self-marker 導線（既存活用＋教示）
- [x] D5 バージョンカット（release=shakedown / M0=confirmatory）

## T1 較正 ProbeConfig（Rust）
- [x] probe_scheduler.rs に ProbeConfig::calibration() 追加
- [x] lib.rs で condition に応じ選択（SESSION_IS_CALIBRATION + SESSION_META_READY gate で race 排除）
- [x] seed 決定性・引数注入・31s 窓と非重複の gap_min
- [x] cargo test ＋模擬で収量/分散検証（5 テスト追加・実測 min10/max15/mean12）
- [x] gse-replay --snapshot byte-equal（default 不変・OK 15 snapshots match）

## T2 提出ラッパー
- [x] packaging module 抽出（匿名化+crypto SSOT・gse-package と共有）
- [x] gse-submit bin（最新 NDJSON 自動検出→.age・P-ID 自動）
- [x] mac/Win ダブルクリックランチャ（scripts/submit/）
- [x] 匿名化保証不変確認（E2E round-trip: VK→category・本文非保存）

## T3 ファイル名 実名漏れ対策
- [x] participant-setup-guide（提出時 P-ID 入力・実名禁止）
- [x] pilot-runbook §4.1（受領時 P### リネーム手順）data-privacy SSOT

## T4 self-marker 導線
- [x] participant-setup-guide §3 に教示（ボタン＋D ホットキー・主観でよい・本文非保存）

## T5 docs バージョンカット
- [x] preregistration-v0.3.md 前向き宣言（基準不変・来歴境界のみ）
- [x] experiment-tracking.md 来歴台帳（P006=researcher test・P007=shakedown）
- [x] research-positioning §6/§8 更新（M0 内容・ラベル収量前提・≥20 floor）

## M0 凍結 & 再走準備
- [x] T1〜T5 を 1 本に束ね（CI 本番バイナリ＝単一真実源・debug 既定 OFF 不変）
- [x] P007 confirmatory 再走手順を docs に明記

## テスト
- [x] cargo test --workspace（242 + 22 passed）
- [x] gse-replay --snapshot（byte-equal）
- [x] clippy（新規コードに警告なし）

## レビュー
- [x] code-reviewer + security-checker（並列）→ HIGH 1件・MEDIUM/LOW 対応
- [x] /cross-review（Codex・絞った Rust diff 935行・secrets-filter 経由 exit0）→ HIGH 1件対応
- [x] HIGH 指摘対応（meta-ready fallback + 世代タグ SESSION_META_FOR_START_MS + decide_probe_init 純化）
- [x] レビュー後再検証: 249 tests pass・clippy clean・snapshot byte-equal・--help exit0

## 完了処理
- [x] design.md / decisions.md 作成（D6 レビュー対応含む）
- [ ] 列挙 add でコミット（-A 禁止・budget.json 混ぜない）
- [ ] /finish-task
