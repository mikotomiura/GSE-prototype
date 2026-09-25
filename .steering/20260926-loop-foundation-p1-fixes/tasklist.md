# tasklist —— Loop 基盤の是正

## spawn 側（loop-spawn.sh ＋ loop-spawn-cleanup-test.sh）—— Sonnet subagent A
- [x] 回帰テスト先行: 起票 A（spawn 経路の不正 id / short）・P1-J（bare origin で 一致／先行／遅れ／分岐／fetch 失敗）・P1-K（同時 2 本・add 失敗で残骸なし）→ 現行で赤を確認
- [x] 起票 A: `validate_name` 括り出し・spawn の id / short に適用
- [x] P1-J: 祖先関係で start を選ぶ・分岐は die・`start-choice =` 行
- [x] P1-K: mkdir ロック（stale 検出・待ち上限・trap 解放）・add 失敗時の残骸ブランチ片づけ
- [x] 変異で赤になることを確認

## run 側（loop-run.sh ＋ loop-run-guard-test.sh）—— Sonnet subagent B
- [x] 回帰テスト先行: P1-I（dirty／コミット 0 → issue_done にならず uncommitted・同状態の継続で no_progress_stop）・P1-D（太字依存を拾う・拾えない数字で WARN）・P1-J の events WARN → 現行で赤を確認
- [x] P1-I: `check_committed` と失敗経路への合流
- [x] P1-D: 装飾剥がし・`issue_deps_unparsed` の WARN
- [x] P1-J: spawn の `start-choice = local-ahead` を attempt 1 の `attempt_start` detail WARN へ
- [x] 変異で赤になることを確認

## 文書（メイン）
- [x] `docs/loop-engineering.md`（語彙 12 種（acceptance_fail の記載漏れも補う）・P1-J / K / D / B の運用）
- [x] `.claude/commands/loop-status.md` / `loop-issue.md` / `.claude/agents/loop-worker.md`
- [x] `.steering/_template/loop-config.json` / `loop-config.README.md`（P1-B・境界ではない旨）

## 検証・レビュー・完了
- [x] 全ループ系テスト（guard / spawn-cleanup / worktree-deny / check-shell-portability / check-tests-are-wired）を正しい終了コードで緑
- [x] メインが diff を一次でレビュー（`* 001` 箇条書きの回帰を発見・是正 P1-D-c ／ ロックの決定論的検査 11d-11f を追加）
- [x] code-reviewer ＋ security-checker 並列・HIGH 対応（HIGH 0。MEDIUM 5 件＋安い LOW は研究者裁定で全対応 → 下）
- [x] レビュー対応: S-M1 文書訂正 ／ C-M1+M2 stale 除去の直列化 ／ C-M3+M4 check_committed を verify・watchdog の前へ ／ LOW 群（＋ メインが local-ahead の start を refs/heads で修飾・12g）
- [x] empirical-prompt-tuning（Lite・2 シナリオ: /loop-status の uncommitted 畳み込み ／ loop-issue・loop-worker の未コミット時の振る舞い）— 研究者依頼 2026-09-26
- [ ] /finish-task（/cross-review 必須・Codex gpt-6-astra）
- [ ] git コミット（明示ステージング・`Refs:`）
