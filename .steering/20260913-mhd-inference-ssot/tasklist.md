# タスクリスト

## 調査
- [x] `.steering/_handoff/next-session-mhd-feature-redesign-ssot.md` を読む
- [x] §0 の前提確認（⚠️ **ADR-029 は main に無い** → ブランチに在ることを確認）
- [x] `verify-before-claiming` Skill を参照
- [x] 一次資料（`.idea` 2 本 / ADR-008/009/010/013/014/016/029 / personalization / task-adaptation）
- [x] サブエージェントで横断調査（NDJSON 観測空間 ／ 個人基準の実装有無）

## 設計
- [x] `/start-task` で `.steering/20260913-mhd-inference-ssot/` を作成
- [x] `requirement.md` を記入
- [x] 初回案 `design-v1.md`
- [x] ⚠️★★★ `/reimagine` で v2 を再生成 → `design.md` / `design-comparison.md`
- [x] 研究者判断 3 件（v2 採用 ／ ADR-029 ブランチから分岐 ／ `phase` は §3.6 を確定）

## 停止条件の判定
- [x] Δ 依存 → ★ **発火しない**（`personalization:1273` 逐語で確認）
- [x] `task_kind` 依存 → ★ **発火しない**（⚠️ 引き継ぎの前提が実測で覆った）

## 執筆
- [x] `docs/adr/ADR-030-stall-onset-and-decision-episode.md`
- [x] `docs/adr/README.md` に 1 行

## レビュー（★ AC10 = 3 系統すべて）
- [x] `/cross-review`（Codex）**1 巡目** → HIGH 1 / MEDIUM 2 / LOW 1 → 全件反映
- [x] `security-checker` → HIGH 1 / MEDIUM 4 / LOW 2 → 全件反映
- [x] `code-reviewer` → HIGH 8 / MEDIUM 8 / LOW 4 → 全件反映（★ D2/D3/D4 を全面改訂）
- [x] `/cross-review`（Codex）**2 巡目** → HIGH 2 / MEDIUM 2 / LOW 1 → 全件反映

## 機械 AC（★ 衛生条件）
- [x] AC6 `check_doc_lexicon.py` exit 0（⚠️ **ADR は検査対象外**なので緑を「検査された」と読まない）
- [x] AC7 `check_citations.py` exit 0（★ 2 回実行して安定）
- [x] AC8 `docs/adr/README.md` に行あり ＋ ファイル実在
- [x] AC9 ヘッダに `昇格元:`
- [x] ★ 禁止用語の手 grep（★ 機械が ADR を見ないため）

## 人が承認する AC（⚠️ 未了）
- [ ] AC1 `stall onset` の操作的定義がコードに落ちる形
- [ ] AC2 `Decision Episode` が新設でなく既存の受け皿
- [ ] AC3 Tier 枠 ＋ 投資順序 ＋ ablation 規律
- [ ] AC4 計器を変えない範囲 / 変える範囲の仕切り
- [ ] AC5 却下案が Alternatives に理由付きで残っている

## 残件（★ 本セッションの射程外）
- [ ] ⚠️★★★ **ADR-029 の AC 1〜3 の研究者承認**（★ マージ順序の律速）
- [ ] タスク 2（T0/T1a/T1b/T1d/Q を `gse-replay` へ）→ ⚠️ `issue-slicing` で別セッション
- [ ] §8c の Loop 基盤整備（worktree へ deny リストを入れる経路）
