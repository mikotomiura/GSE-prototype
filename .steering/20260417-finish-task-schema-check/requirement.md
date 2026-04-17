# finish-task-schema-check

## 背景

2026-04-17 の schema drift 事故の根本原因は、Phase 2b IME Shadow 実装時に
`/finish-task` 時点で `docs/development-guidelines.md` §10.3 Step 3
(`src-tauri/schema/current.json` → `gse-dataset/schema/current.json` へのコピー)
が抜け落ちていたこと。

2026-04-17 の前タスク (`.steering/20260417-schema-drift-guard/`) で
`scripts/check_schema_parity.py` + `scripts/sync-all.{ps1,sh}` Step 0 呼出し
(tier-2 runtime guard) は導入済み (commit 0795fb6, v2.30)。

しかし runtime guard は **「次のバッチ同期まで drift を検出できない」** という
構造的欠陥を持つ:

- `/finish-task` → `git push` → 数時間〜数日後のバッチ同期 → ここで初めて検知
- drift は「クローズ済みタスク」に属するため、修復コミットは別タスク扱いとなり
  git history が分断される (今回の 0795fb6 自体がその症状)
- 「sync-all を今回走らせないワークフロー」(例: prototype 側のみの PR 切り出し)
  では drift が無期限に残留しうる

このためクローズ時点で catch する workflow-level guard (Option A) を入れる。

## ゴール

`.claude/commands/finish-task.md` に schema_dto.rs の diff 検出ステップを
追加し、変更がある場合のみ `python scripts/check_schema_parity.py --dataset
<path> --machine-readable` を走らせる。HELPER_EXITCODE != 0 なら finish を
停止し、修復手順を Claude Code 上で即時提示する。

## スコープ

### 含むもの
- `.claude/commands/finish-task.md` への Step 追加 (Step 2.5 または Step 3 内部)
- `schema_dto.rs` の変更有無を git diff で判定するロジック
- 変更ありの時のみ parity helper を起動する条件分岐
- HELPER_EXITCODE=0 以外の時に finish を停止し、修復コマンド例を提示する動線
- `.steering/20260417-finish-task-schema-check/` の記録

### 含まないもの
- 既存 runtime guard (`scripts/sync-all.*` Step 0) の変更
  (0795fb6 で完成済み・本タスクでは触らない)
- `/add-feature` / `/fix-bug` / `/refactor` / `/start-task` への guard 追加
  (finish の 1 点に集約する・複数点への分散は後続タスクで検討)
- CI (GitHub Actions) での drift guard 復活
  (memory「CI exhausted」により対象外)
- helper 本体 (`check_schema_parity.py`) の挙動変更
  (契約は 0795fb6 で確定・本タスクは呼出し側のみ変更)
- auto-copy による自動修復 (破壊的変更になりうるため明示停止を優先)

## 受け入れ条件

- [ ] `/finish-task` 実行時、`schema_dto.rs` に差分がある場合のみ helper が走る
- [ ] 差分が無いタスク (通常タスク) では helper を呼ばず、従来通り完了処理が進む
- [ ] drift 検出時は finish が停止し、修復手順 (cargo emit_schema + cp 手順) が
      Claude の応答に表示される
- [ ] drift なし (parity OK) の場合は helper 出力を短く報告して次 Step へ進む
- [ ] `$DATASET_ROOT` が未設定 / 不在時の挙動が明示される
      (skip with warning か hard-fail かを design.md で確定)
- [ ] 既存のタスク完了フロー (Step 1-5) が regression なく動作する

## 関連ドキュメント

- `.claude/commands/finish-task.md` (編集対象)
- `docs/development-guidelines.md` §10.3 / §10.3.1 (helper 契約と cross-repo 運用)
- `scripts/check_schema_parity.py` (再利用する helper)
- `.steering/20260417-schema-drift-guard/` (前タスク: runtime guard 側)
- `.steering/20260417-phase2b-ime-shadow-features/` (drift を引き起こした Phase 2b)

## 運用メモ
- /reimagine 適用: Yes (2026-04-17 再判定)
- 初回判断: No (前タスクで Option A は検討済みと判断)
- 再判定理由: 初稿 design.md 執筆後に以下が明らかになった:
  - 実装案は A (finish-task Step 2.5) / B (Stop hook) / C (pre-commit hook)
    / D (PreToolUse hook) の 4 層に分散しうる
  - A は Claude Code を介さない直 commit で素通りする弱点を持つ
  - 検出ロジック (git log --grep Refs:) がコミット規約依存で脆い
  - tier-2 と tier-3 の責務重複・layering 判断が残っている
  いずれも「複数の実装案が考えられ最良案が自明でない」に合致するため、
  v1 (Step 2.5 案) を退避して v2 案を再生成し比較する。
