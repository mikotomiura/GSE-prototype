# タスクリスト

## 準備
- [x] 一次を読む: `blockers.md` 起票 23 / `loop-spawn.sh:53-72` / `loop-run.sh:436` / `ci.yml:651,658,760`
- [x] 受け皿の確認: `loop-spawn-cleanup-test.sh`（9 群 29 件・変異対照つき・jq 不要）
- [x] ⚠️ **他の呼び出し元を洗う** → `loop-worktree-deny-test.sh`（直接 2 か所＋loop-run 経由）/ `loop-run-guard-test.sh`（loop-run 経由）
- [x] ⚠️★★★ **罠の発見**: fake config は 1 行に 3 キー同居 → **行頭アンカー禁止**／fake の default が `main` なので **緑のまま穴が生きうる**
- [x] grill で 2 問を裁定（config 1 件でも止める / 承認は記録のみ）
- [x] `requirement.md` / `design.md` を書く

## 実装
- [ ] **I1** `loop-spawn.sh`: 先頭オプションの while ループ（`--no-exec` / `--task <v>` / `--task=<v>`）。⚠️ `--cleanup` の `$1` 判定を壊さない
- [ ] **I2** `loop-spawn.sh`: `json_top_value()` を新設（★ 行頭に依存しない・**n_key と n_val を別に数える** 4 状態）
- [ ] **I3** `loop-spawn.sh`: `valid_refname()` を新設（先頭 `-` / 文字集合 / `..` / `git check-ref-format --branch`）
- [ ] **I4** `loop-spawn.sh`: `find_task_config()` を新設（dir / 素名 / 日付付き名の 3 形・**0 件と複数件で die**）
- [ ] **I5** `loop-spawn.sh`: `resolve_base()` を書き換え（★ `RESOLVED_BASE` / `RESOLVED_FROM` に入れる・⚠️ `jq` を捨てる・**config 1 件でも die**）
- [ ] **I6** `loop-spawn.sh`: provenance ブロックを **stderr** へ（★ base / provenance / start / **default からの乖離**）
- [ ] **I7** `loop-run.sh`: `--task "$TASK_DIR"` を渡す ＋ ⚠️ `2>/dev/null` をやめて **stderr を run ログへ**

## テスト
- [ ] **T1** 群 7 を追加（7a–7t の 20 件）。⚠️ **7k は `base_branch` を `main` 以外の実在ブランチ**にする（★ でないと 8b が赤くならない）
- [ ] **T2** 群 8（変異）を追加: **8a** fail-closed を殺す / **8b** 抽出器を行頭アンカーに退行させる
- [ ] **T3** `bash scripts/loop-spawn-cleanup-test.sh` が exit 0（★ 既存 29 件も緑）
- [ ] **T4** `bash scripts/loop-worktree-deny-test.sh` が exit 0（⚠️ loop-run 経由の配線）
- [ ] **T5** `bash scripts/loop-run-guard-test.sh` が exit 0
- [ ] **T6** `bash scripts/check-tests-are-wired.sh` が exit 0
- [ ] **T7** ⚠️★★★ **実 repo で `--task` 無し実行が実際に止まるか**を手で 1 回確かめる（★ 現存 config 1 件が対象）

## レビュー
- [ ] **R1** `code-reviewer` ＋ `security-checker` を**並列**（★ 範囲 / 禁止事項 / 締切を明記）
- [ ] **R2** HIGH / MEDIUM 指摘を**一次で裏取り**してから反映
- [ ] **R3** `/cross-review`（Codex）**1 巡目** = 自文書・他文書の矛盾
- [ ] **R4** `/cross-review`（Codex）**2 巡目** = ★ **自分が足した規則の境界条件**
- [ ] **R5** ⚠️ 予算を **300000 へ戻す**（★ 3 本すべて終わったら）

## ドキュメント
- [ ] **D1** `.steering/_template/loop-config.README.md` の `base_branch` 節（★ `:97-100`）
- [ ] **D2** `docs/loop-engineering.md` `:113` の起動欄
- [ ] **D3** `.claude/commands/loop-issue.md` `:33`
- [ ] **D4** ⚠️ `blockers.md` の**起票 23 を「是正済み」に閉じる**（★ 一次の側に結果を書き戻す）

## 完了処理
- [ ] `design.md` の最終化（★ 実装後に実際の関数名・行番号へ）
- [ ] `decisions.md`（★ grill の 2 裁定 ＋ `jq` を捨てた判断 ＋ レビュー裁定）
- [ ] git commit（⚠️ `git add -A` 禁止・ファイル名を明示）
- [ ] PR → CI 緑 → merge（⚠️ `gh run view` で確かめる。`--watch` の終了コードを信じない）
