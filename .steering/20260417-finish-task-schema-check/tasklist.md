# タスクリスト (v2 ベース)

## 準備
- [x] requirement.md / design.md 記入 + /reimagine 実施 (v2 採用)
- [x] file-finder / impact-analyzer 並列調査
- [x] 調査結果を design.md に反映 (sentinel 不要化・shallow fallback 強化・
      downstream ファイル追記)

## 実装
- [x] `.claude/commands/finish-task.md` frontmatter 更新
      (allowed-tools に `Bash(python *)` と `Bash(python3 *)` を追加)
- [x] `.claude/commands/finish-task.md` Step 3 本文を書き換え
      - 「以下を並列で起動する」パターンに統一 (review-changes.md:22-29 風)
      - `/review-changes` + `test-runner` + **schema parity check** の 3 並列
      - parity check のサブブロック (検出ロジック + helper 呼出し + exit code
        判定 + 失敗時の停止宣言)
- [x] `.claude/commands/finish-task.md` 制約に「parity check 失敗で Step 4
      に進まない」を追加
- [x] `.claude/commands/add-feature.md` 末尾に 1 行注記追加
- [x] `.claude/commands/fix-bug.md` 末尾に 1 行注記追加
- [x] `.claude/commands/refactor.md` 末尾に 1 行注記追加

## ドキュメント
- [x] `docs/development-guidelines.md` §10.3.1 「呼出し」欄を更新
      (tier-2: sync-all Step 0 + tier-3: finish-task Step 3 の 2 段表記)
- [ ] 必要なら §10.3 の tier 対応表を明示 (既に tier-1/2/3 で記述済みのため
      追加不要と判断・§10.3.1 の更新で十分カバー)

## 動作確認 (手動回帰・dry-run で実施)
- [x] **dogfood (skip)**: 本タスクでの dry-run 実行で BASE=e05cb19 resolve・
      CHANGED 空・skip メッセージ出力を確認
- [x] **positive (green)**: CHANGED を手動で "schema_dto.rs" に setup した
      dry-run で helper 起動・parity OK (7369 bytes)・parity_rc=0 を確認
- [x] **negative (stop)**: DATASET=/tmp/nonexistent-dataset-for-test で
      dry-run し helper exit 3 + 修復コマンド (cp) 出力を確認
- [x] **shallow clone fallback**: `git merge-base HEAD
      refs/heads/nonexistent-branch` で merge-base 失敗時 CHANGED を
      `__fallback__` に set する経路が動作することを確認
- [ ] **本番実行**: Step 8 (/finish-task 本実走) で上記 4 ケースの Bash
      ブロックが Claude Code 経由で動くことを dogfood 確認

## レビュー (並列実行)
- [x] code-reviewer 起動: HIGH 3 件 + MEDIUM 4 件 + LOW 3 件検出
- [x] security-checker 起動: 問題なし (LOW 1 件のみ)
- [x] HIGH #1 対応: unstaged 取りこぼしバグを修正
      (`git diff "$BASE"` + `git diff` + `git diff --cached` の 3 者 union)
- [x] HIGH #2 対応: early exit を撤廃し rc 変数一本化・末尾 exit 1 箇所化
- [x] HIGH #3 対応: frontmatter `Bash(python *)` を
      `Bash(python scripts/check_schema_parity.py*)` に絞り込み
- [x] MEDIUM #1 対応: add-feature / fix-bug / refactor の 4 行注記を
      2 行短縮 + §10.3.1 へのリンク (SSOT 化)
- [x] MEDIUM #2 対応: DATASET 既定不在時の WARN 出力追加
- [x] MEDIUM #3 対応: `__fallback__` sentinel を SKIP boolean 変数に分離
      (HIGH #1 と同時解決)
- [x] MEDIUM #4 対応: docs §10.3.1 の Windows/macOS 行を tier-2/tier-3
      の親レベルへ移動 (共通前提として明示)

## 完了処理
- [ ] design.md に実装時判明事項を追記 (該当あれば)
- [ ] decisions.md の作成 (設計判断が増えた場合のみ)
- [ ] /finish-task Step 1-5 を自己適用 (= dogfood)
- [ ] git commit (`chore(commands): add schema parity check to /finish-task Step 3`)

## スコープ外 (本タスクで扱わない)
- `/add-feature` / `/fix-bug` / `/refactor` の末尾注記 **以外** の大幅改修
  (注記は 1 行・影響は軽微)
- auto-copy 機能
- CI による drift 検知復活 (CI exhausted)
- helper 本体 (`check_schema_parity.py`) の挙動変更
