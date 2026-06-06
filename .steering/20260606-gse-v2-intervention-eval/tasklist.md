# タスクリスト

## 準備（docs 先読み → Skill → 調査の順、CLAUDE.md 準拠）
- [x] docs/baseline 確認: baseline_metrics.md（既存指標の形式・range/point GT 運用）を精読
- [x] 必須 Skill 参照: rust-standards / architecture-rules
      （hmm-analysis / ml-workflow は engine 非変更のため対象外と判断）
- [x] file-finder で replay.rs・metrics.rs の既存構造を調査（並列 2 本）
- [x] 影響範囲分析（インラインで実施）: schema_dto 非変更・既存フラグ排他のみ・CI 影響なし
- [x] GT 可用性の実地調査: dataset に segments 不在（labeled/ 空）→ point label のみ判明

## 実装
- [x] replay.rs に `--intervention` フラグ追加（既存フラグと相互排他、--json 依存チェック、usage）
- [x] 既存ログから `InterventionInput` を再構成（p_stuck/f3/f4/f6 は logged feat、idle_ms は press 間隔）
- [x] decide() を feat timestamp 順にステップ（cooldown/daily_cap/wall 累積が実時刻で進行）
- [x] GT 二値化（PROTECT/STALL）と join（point label を forward-fill で区間化、D2）
- [x] HIR / Precision / DC / Burden の算出（新規 analysis/intervention_eval.rs、D6）
- [x] pretty-print + `--json` 出力

## テスト
- [x] 単体テスト追加（HIR=1.0/0.0、DC=1.0/0.0、forward-fill カバレッジ、idle_ms 境界、空入力ほか 15 本）
- [x] `cargo fmt` / `cargo test --lib` が通ることを確認（82 passed）

## レビュー
- [x] code-reviewer + security-checker を並列起動
- [x] HIGH/MEDIUM 指摘への対応（DC 起点不変条件の明文化、カバレッジ docstring、wall_active 限界、
      empty ヘルパ、テスト 2 本追加。security は実害指摘なし）

## 実データ検証
- [x] P000 13 セッションに `--intervention` を実行
- [x] HIR/DC/Precision/Burden を steering（results.md）に記録
- [x] 結論報告: Wall=0（重度害は完全抑制）、PROTECT suppression 99.4%、条件付き HIR 0.647（軽度 nudge 残存）、
      DC 0.933。→ 「部分的に Yes」（results.md）

## ドキュメント
- [x] development-guidelines §10 に `--intervention` 経路を追記
- [x] glossary に HIR / DC / PROTECT-STALL（介入評価）を追加

## 完了処理
- [x] design.md の最終化（p_stuck=logged feat、GT=forward-fill を反映）
- [x] decisions.md 作成（D1〜D6）
- [ ] /finish-task（tier-3 schema parity guard。schema_dto 非変更のため drift 無しの想定）
