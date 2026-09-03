# タスクリスト

## 準備
- [x] 引き継ぎメモの主張 5 件を **実コードで検算**（★ #3 は実体と違ったので訂正した）
- [x] `verify-before-claiming` Skill を読む
- [x] 現状を測る（`check-o1-release-readiness.sh` = 18 / 1、PR #148 は CLEAN）
- [x] `/start-task` → `.steering/20260903-o1-remaining-highs/`
- [x] `/reimagine`（#5 のみ）→ v2（予約トークン方式）を採用

## PR #148
- [x] マージ（★ MERGED 2026-09-03T03:56:54Z・`7f4bf75`）
- [x] ローカル main を更新し、変更された `o1FindInPhase1Roster_` を読み直す

## 実装
- [x] #1 `O1_MGMT_SHEET_ID` を `o1Config_()` に追加
- [x] #1 `o1MgmtConfigProblem_` / `o1OpenMgmtLog_` / `o1LogMgmt_` / `o1MgmtSafeCell_`
- [x] #1 `buildO1MgmtSheet()` / `checkO1MgmtSheet()`（研究者の入口）
- [x] #1 `o1ConfigProblems_` に構築時 fail-closed の検査を追加
- [x] #1 `o1OpenRoster_` に逆向きガード（採番元 = 登録ログ を拒否）
- [x] #1 `onO1ConsentSubmit` の全分岐にログ追記を配線（8 経路）
- [x] #3 `O1_MGMT_MAX_ROWS = 5000`（★ 超えたら追記しない・消さない）
- [x] #4 `o1FindInPhase1Roster_` のメール重複検知（★ 全行走査）
- [x] #4 `o1ConflictMessage_`（★ 理由別の文面）
- [x] #5 `o1AllocatePidRow_`（予約トークン → 採番 → 読み返し → 有界リトライ）
- [x] #5 `assignO1ParticipantId` も同じ経路へ通す
- [x] `scripts/check-o1-release-readiness.sh` に管理シートの実装検査を追加

## テスト
- [x] §13（管理シート）/ §14（メール重複）/ §15（予約トークン）を追加 — 185 ケース緑
- [x] ⚠️ **陰性対照**: 既存 §1〜§12（134 件）が緑のまま
- [x] ⚠️ **3 状態**: 正常 / 不在（プロパティ空・タブ無し）/ 壊れ（同一 ID・ロスタータブ）
- [x] 変異注入 11 件を追加 → **52 / 52 が赤**（★ 全変異が適用されたことも harness が確認）
- [x] 関連する他の guard test 7 本が緑
- [x] ⚠️ 新しい検査自体を 5 状態で手実測 → ★ **偽陰性を 1 件発見して直した**
      （メッセージ文字列を「実コード」と数えて `comment-only` を見逃していた）
- [x] `check-o1-release-readiness.sh --selftest`

## レビュー
- [x] code-reviewer / security-checker を並列起動
- [x] HIGH 指摘への対応
- [x] `/cross-review`（Codex）— HIGH 1 / MEDIUM 2 / LOW 1 に対応、Codex の 2 件は反証して却下

## 配備（外界）— ★ 完了（詳細は decisions.md「配備記録」）
- [x] `GSE_O1_Form_Builder` へ貼り付け（★ `a837c284317d1539` / 2558 行・⚠️ リロード後も一致）
- [x] スクリプト プロパティ `O1_MGMT_SHEET_ID` を設定（★ 7 件目・既存 6 件は無傷）
- [x] `buildO1MgmtSheet()` を 1 回実行（★ 2 タブ作成）
- [x] `checkO1FormConfig()` / `checkO1MgmtSheet()` / `checkO1RosterShape()` すべて ✅
- [x] クリップボードを復元（★ バイト一致を確認）／自分が開いたタブを閉じた

## 完了処理
- [x] design.md の最終化（v2 採用の根拠つき）
- [x] decisions.md
- [x] git commit / PR #150（★ CI 全緑 → MERGED・main = `ea0eb70`）

## ⚠️ 今回やらないこと（★ 完了報告に明記する）
- #2 G1 側へのロスター形検査の移植（★ 研究者判断でスコープ外）
- 送信 timeout の実測（★ 研究者の実機操作。readiness の残 1 件はこれ）
- 引き継ぎメモ §5 の持ち越し 6 件
