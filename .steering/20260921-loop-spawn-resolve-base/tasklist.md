# タスクリスト

## 準備
- [x] 一次を読む: `blockers.md` 起票 23 / `loop-spawn.sh:53-72` / `loop-run.sh:436` / `ci.yml:651,658,760`
- [x] 受け皿の確認: `loop-spawn-cleanup-test.sh`（9 群 29 件・変異対照つき・jq 不要）
- [x] ⚠️ **他の呼び出し元を洗う** → `loop-worktree-deny-test.sh`（直接 2 か所＋loop-run 経由）/ `loop-run-guard-test.sh`（loop-run 経由）
- [x] ⚠️★★★ **罠の発見**: fake config は 1 行に 3 キー同居 → **行頭アンカー禁止**／fake の default が `main` なので **緑のまま穴が生きうる**
- [x] grill で 2 問を裁定（config 1 件でも止める / 承認は記録のみ）
- [x] `requirement.md` / `design.md` を書く

## 実装
- [x] **I1** `loop-spawn.sh`: 先頭オプションの while ループ（`--no-exec` / `--task <v>` / `--task=<v>`）。⚠️ `--cleanup` の `$1` 判定を壊さない
- [x] **I2** `loop-spawn.sh`: `json_top_value()` を新設（★ 行頭に依存しない・**n_key と n_val を別に数える** 4 状態）
- [x] **I3** `loop-spawn.sh`: `valid_refname()` を新設（先頭 `-` / 文字集合 / `..` / `git check-ref-format --branch`）
- [x] **I4** `loop-spawn.sh`: `find_task_config()` を新設（dir / 素名 / 日付付き名の 3 形・**0 件と複数件で die**）
- [x] **I5** `loop-spawn.sh`: `resolve_base()` を書き換え（★ `RESOLVED_BASE` / `RESOLVED_FROM` に入れる・⚠️ `jq` を捨てる・**config 1 件でも die**）
- [x] **I6** `loop-spawn.sh`: provenance ブロックを **stderr** へ（★ base / provenance / start / **default からの乖離**）
- [x] **I7** `loop-run.sh`: `--task "$TASK_DIR"` を渡す ＋ ⚠️ `2>/dev/null` をやめて **stderr を run ログへ**

## テスト
- [x] **T1** 群 7 を追加（★ 最終的に **34 件**。レビュー後に 7u・7v・7w・7x・7y・7z・7aa・7ab・7ac・7x2 を追加）。⚠️ **7k は `base_branch` を `main` 以外の実在ブランチ**にする
- [x] **T2** 群 8（変異）を追加: **8a** fail-closed を殺す / **8b** ★ **深さ 1 だけ規則**を殺す / **8c** ★ `valid_refname` を殺す（⚠️ 行アンカーの変異は書き直しで作れなくなった）
- [x] **T3** `bash scripts/loop-spawn-cleanup-test.sh` が exit 0（★ **PASS=64 / FAIL=0**。既存 29 件も緑）
- [x] **T4** `bash scripts/loop-worktree-deny-test.sh` が exit 0（⚠️ loop-run 経由の配線）
- [x] **T5** `bash scripts/loop-run-guard-test.sh` が exit 0
- [x] **T6** `bash scripts/check-tests-are-wired.sh` が exit 0
- [x] **T7** ⚠️★★★ **実 repo で `--task` 無し実行が実際に止まるか**を手で 1 回確かめる（★ 現存 config 1 件が対象）

## レビュー後の追加実装（★ 判断 6）
- [x] **I8** 抽出器を JSON の文字ステートマシンへ書き直す（⚠️★★★ **入れ子の `base_branch` を拾う**穴・両系統 HIGH）
- [x] **I9** `sanitize_disp()` を新設（⚠️★★★ **端末エスケープで乖離警告を隠せる**）
- [x] **I10** `valid_refname` に `refs/` / 予約名 / hex の拒否を追加（⚠️ `FETCH_HEAD` と 40 桁 hex は `worktree add` が成功する）
- [x] **I11** `cfg_rel()` で `.steering/<task>/_loop-config.json` に閉じる（⚠️ 任意のファイルを config として受けていた）
- [x] **I12** `n_cfg` の 「|| true」 を取る（⚠️★ **起票 23 と同型の形を自分で書いていた**）
- [x] **I13** `default_branch` を remote-tracking 優先に（⚠️ 片側だけ remote で乖離が過小に出た）
- [x] **I14** 日付接頭辞を数字 8 桁に限る / `FOUND_CFG` の bash 限定表現をやめる / `loop-run.sh` の空行復帰値
- [x] **D5** `CLAUDE.md:149` と `git-workflow` Skill（⚠️★★★ **旧記述のままでは必ず die する**）
- [x] **D6** `docs/loop-engineering.md` の表の分断を直す（⚠️ 自分で壊した・A/B/C 比較は SSOT）
## レビュー
- [x] **R1** `code-reviewer` ＋ `security-checker` を**並列**（★ 範囲 / 禁止事項 / 締切を明記）
- [x] **R2** HIGH / MEDIUM 指摘を**一次で裏取り**してから反映
- [x] **R3** `/cross-review`（Codex）**1 巡目**（★ 5 件 / 採用 3・却下 1・記録 1。実消費 41012）
- [x] **R4** `/cross-review`（Codex）**2 巡目**（★★★ **偏陽性を検証した過程で自分のテスト 2 件が空振りと判明**。実消費 36274）
- [x] **R5** 予算を **300000 へ戻した**（★ 3 本の実消費合計 118844。見込み 115000 と誤差 +3.3%）

## ドキュメント
- [x] **D1** `.steering/_template/loop-config.README.md` の `base_branch` 節（★ `:97-100`）
- [x] **D2** `docs/loop-engineering.md` `:113` の起動欄
- [x] **D3** `.claude/commands/loop-issue.md` `:33`
- [x] **D4** ⚠️ `blockers.md` の**起票 23 を「是正済み」に閉じる**（★ 一次の側に結果を書き戻す）

## 完了処理
- [x] `design.md` の最終化（★ 実装後に実際の関数名・行番号へ）
- [x] `decisions.md`（★ grill の 2 裁定 ＋ `jq` を捨てた判断 ＋ レビュー裁定）
- [x] git commit（★ 4 コミット）（⚠️ `git add -A` 禁止・ファイル名を明示）
- [ ] PR → CI 緑 → merge（⚠️ `gh run view` で確かめる。`--watch` の終了コードを信じない）
