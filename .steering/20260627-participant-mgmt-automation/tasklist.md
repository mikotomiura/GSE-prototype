# タスクリスト

## 準備
- [x] 関連 docs を読む（設問草案 / pilot-runbook / 既存 .gs）
- [x] ユーザー決定確認（メール=下書き / condition=baseline 固定）

## 実装（Task 1: F1 トリガ）
- [x] `recordFormUrl` に form ID 保存を追加
- [x] 設問タイトル照合ヘルパ `f1Answers_` / `findResp_`
- [x] 適格性判定 `isEligibleF1_`
- [x] メール本文テンプレ `f1EmailBody_` ＋ 定数（AUTO_SEND / 配布情報）
- [x] ロスター行追加ヘルパ `appendRosterRow_`（冪等チェック含む）
- [x] `onF1Submit(e)` 本体
- [x] `installF1Trigger()` / `removeF1Triggers()`

## 実装（Task 2: 管理シート）
- [x] `refreshRosterStatus()`（F2/F4/F5 を P-ID で集計しロスター更新）
- [x] `buildDashboardTab_`（完了率・未提出者・無回答フラグ）
- [x] `applyRosterValidation_`（ドロップダウン・条件付き書式）
- [x] `validateRoster()`（P-ID 形式・重複チェック）
- [x] `buildRosterTab_` に対応表注意行追加
- [x] `buildManagementSheet` から新ヘルパ呼び出し

## テスト
- [x] `node --check` で構文確認
- [x] 純粋ロジックの単体確認（scratchpad）

## レビュー
- [x] code-reviewer + security-checker を並列起動
- [x] /cross-review（Codex 独立レビュー・全ゲート通過）
- [x] HIGH/MED 指摘への対応（ヘッダ動的探索統一・LockService 排他・メールマスク・
      ダッシュボード実名除去・通知失敗の備考可視化・email@検証・forForm 明示・各種コメント）

## ドキュメント
- [x] decisions.md 作成（D1〜D7）
- [ ] 実機検証チェックリストを完了報告に提示

## 完了処理
- [x] design.md / decisions.md 最終化
- [ ] git commit + PR
