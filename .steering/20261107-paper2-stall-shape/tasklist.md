# タスクリスト

## 準備
- [x] 引き継ぎ・判断 43・前の実験の notes を読む
- [x] 研究者に順番・読者・取り置き・OSF を確かめる（2026-11-07）
- [x] worktree を論文 1 の枝の先端から切る（references.md の採番を共有するため）
- [x] 文献の追いかけ（/literature-review・3 角度・V468〜V471・コミット 895b42b8）

## 条件
- [x] conditions.md・SEED・env.md をコミット（08010482・計算の前）

## 実装と確かめ
- [x] prep.py（D2・D3 の照合）
- [x] core.py と selftest（K2）・変異（K3: はじめ 12 個・レビュー後 20 個すべて赤・対照緑）
- [x] k1_match.py（K1: B0 全単位一致・変種も一致）
- [x] run_configs.py（90 通り・回し直しで 4,894 秒）
- [x] c3b.py
- [x] analyze.py を合成の入力で通す → 実データ（件数のモデルの最適化を L-BFGS-B に・ずれ 2）
- [x] notes.md（言える・言えない・逸脱）

## レビュー
- [x] code-reviewer と security-checker（並列）
- [x] /cross-review（Codex・統合レポートは判断 11）
- [x] 指摘への対応と回し直し（再開の修正で全部・その後は c3b と analyze だけ・長さは REML の最大へ）

## 判断
- [x] 研究者に単独にするかを聞く → 単独にする（判断 9）

## 完了処理
- [x] decisions.md・blockers.md
- [x] コミット（push と PR は研究者に確かめる）
- [x] 引き継ぎ（`.steering/_handoff/next-session-gse-paper2-outline.md`）
