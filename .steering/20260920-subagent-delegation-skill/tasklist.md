# タスクリスト — サブエージェント委譲の Skill 化

## 調査（完了・★ すべて一次で実測）
- [x] 既存 Skill 23 本 / コマンド 13 本 / `docs/external-skills.md` に**該当 0 件**を確認
- [x] `/literature-review` に `commit` / `check_citations` / `pypdf` / `並列` が**各 0 件**
- [x] モデル割当の SSOT を特定（`docs/loop-engineering.md:60-76`）
- [x] `Task` を持つ agent は **`loop-worker` の 1 本だけ**（12 本中）
- [x] ⚠️ **`cross-reviewer` の文書と実体の食い違い**を発見（→ 起票・判断 6）
- [x] 入れ子起動で**利用上限に 2 回当たった**一次記録を特定

## 設計（完了）
- [x] grill で判断分岐 4 件を閉じた（判断 1〜4）
- [x] 実装段階の判断を記録（判断 5: 出所の格 ／ 判断 6: 矛盾は起票のみ）

## 実装（完了）
- [x] `.claude/skills/subagent-delegation/SKILL.md`（ルール 1〜7 ＋ チェックリスト ＋ 抜け穴表）
- [x] `/literature-review` に「★ 回し方」「★ ラウンドを閉じる」＋ アンチパターン 4 行
- [x] `CLAUDE.md` の Skill 表 ＋ §4 に入口
- [x] memory 4 件をポインタへ縮小 ＋ `MEMORY.md` の 4 行を更新

## 検証（`empirical-prompt-tuning` Lite）
- [x] **Iteration 0**: description と body の乖離を修正（★ 入れ子 / 渡すかの判断 / brief が
      description に無かった）
- [ ] **Iteration 1**: 別エージェントに 1 シナリオを渡し、要件 7 項目で採点 ＋ 「詰まった点」を回収
- [ ] **Iteration 2**: 詰まった点を Skill へ反映 → 再実行して改善を確認
- [ ] ⚠️ 改行コードが LF であることを確認（`tr -cd '\r' | wc -c` が 0）

## レビュー
- [ ] `code-reviewer`（opus・★ 範囲と禁止事項と締切を明記）
- [ ] `/cross-review`（⚠️ 予算残と相談。★ 本タスクは文書のみなので 1 巡でも可）
- [ ] `/finish-task`

## ⚠️ 起票（★ 本タスクでは直さない）
1. **`cross-reviewer` の文書と実体の食い違い** —— `/cross-review` Step 5 は
   「cross-reviewer 内部で code-reviewer を Task で並列起動」と書くが、
   `cross-reviewer` は `Task` を持たない。⚠️ 直し方が 2 通りあり**裁定が要る**（判断 6）。
