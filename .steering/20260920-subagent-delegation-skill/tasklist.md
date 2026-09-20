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

## 検証（`empirical-prompt-tuning` Lite・詳細は `verification.md`）
- [x] **Iteration 0**: description と body の乖離を修正（★ 入れ子 / 渡すかの判断 / brief が
      description に無かった）
- [x] **Iteration 1**: 要件 **7/7（100%）**だが ⚠️ **詰まりが 5 件**（★ 実行者は推測で埋めて満点を取った）
- [x] **Iteration 2**: 5 点中 **4 点が「Skill に答えあり」**へ。残る 1 点は
      ⚠️ **シナリオ側の欠陥**（git 操作を禁じたため Skill と矛盾した）。新たな穴 1 件を一般形で反映
- [x] ⚠️ 改行コードが LF（★ `SKILL.md` / `literature-review.md` / `verification.md` とも CR=0）

## レビュー
- [x] `code-reviewer`（opus・★ 範囲と禁止事項と締切を明記）
      → ⚠️ **HIGH 5 / MEDIUM 6 / LOW 3。一次で裏取りして偽陽性 0。全件反映**（`110c41f`）
- [x] `security-checker` → ⚠️★ **skip。理由: 本タスクは `.md` のみ 8 ファイル**で、
      rust/ts **0 件**・schema **0 件**。★ 外部入力・認証・データ保存に触れていない
      （`.claude/agents/security-checker.md` の起動条件に該当しない）
- [x] `test-runner` → ⚠️★ **skip。理由: 同上（コード変更 0 件）**
- [x] schema parity check → ⚠️★ **skip。理由: `schema_dto.rs` / `schema/current.json` 未変更**
- [x] `/cross-review`（Codex） → ⚠️★★★ **skip。理由: 研究者の指示**（2026-09-20・
      「finish-task へ進めよう」）。★ 予算は残 **78,542 / per_inv 30,000** で通せたが、
      **本タスクは文書のみ**であり、⚠️ Codex は repo を読めないので
      （memory「Codex は repo を読めない」）**プロンプトに全文を貼る必要があり割に合わない**と判断
- [x] `/finish-task`

## ⚠️ マージ時にやること（★ 本ブランチでは触らない）
- [ ] `.steering/_handoff/README.md` に本タスクの行を足す
      —— ⚠️ **本ブランチでは編集しない**。★ 同ファイルは `feature/g1-collection-readiness-gate`
      が既に書き換えており、**両方で触ると衝突する**。→ マージの後に 1 行足す。

## ⚠️ 起票（★ 本タスクでは直さない）
1. **`cross-reviewer` の文書と実体の食い違い** —— `/cross-review` Step 5 は
   「cross-reviewer 内部で code-reviewer を Task で並列起動」と書くが、
   `cross-reviewer` は `Task` を持たない。⚠️ 直し方が 2 通りあり**裁定が要る**（判断 6）。
