> ✅ **消化済み（2026-09-18）**。★ 002 / 003 / 005 / 007 は merge 済み、005 の是正として 008 を足して merge 済み、
> ⚠️ 004 / 006 は研究者の定義待ちで保留。★ 続きは **`next-session-mhd-tiers-researcher-decisions.md`**。
> ⚠️ 以下は当時の記述（履歴）。

# 次セッション — タスク 2 の issue 002〜007 を回す（★ 001 は完了済み）

> 作成: 2026-09-15 / ⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.steering/20260914-mhd-feature-offline-tiers/decisions.md`（**判断 7 / 判断 8**）／
> `issues/001.md` の Execution Result ／ `docs/adr/ADR-030-...md` ／ `docs/loop-engineering.md`。
> ★ 前段（001 の裁定）は `next-session-issue001-pause-const-arbitration.md`（**履歴**）。

---

## §1 いまの状態（★ 2026-09-15 実測）

- ブランチ `docs/adr-030-stall-onset-definition`、**tree クリーン**。
- **issue 001 = `done`**（commit `061e6fb` で merge 済み）。`gse-replay --features` が動く。
- pin 済み verify は **4 本とも exit 0**（`cargo test --workspace` **682 passed** /
  ゴールデン `OK: 15 snapshots match` / `cargo check --all-targets` / `clippy -D warnings`）。
  `001-acceptance.sh` も **OK**。
- worktree・`loop/*` ブランチは**残っていない**（cleanup 済み）。

## §2 ⚠️★★★ 回す前に必ず片付けること（★ 放置すると即死する）

1. ⚠️ **`events.jsonl` に issue 001 の `issue_done` が無い**（★ watchdog 空応答で `blocked` のまま終わったため。
   ⚠️ **手で `issue_done` を捏造しない** —— events を書くのは script だけという規約を破る）。
   → ★ **`issues/002.md` の `## Dependencies` から `001` を外す**。
   ⚠️ コード上の依存は **merge 済みで満たされている**（`feat_offline/mod.rs` は main 側に在る）。
   ⚠️ 外したら **`_issue-plan.md` §2 の DAG 図も同時に直す**（★ 片方だけ直さない）。
   ★ 外さないと `--issues 002,...` は `preflight_dag` が「依存 001 が issues/ に存在しません」で **die する**。
2. ⚠️ **`headless.max_turns: 30` を上げるか決める**（→ 判断 8 の未決 1）。
   ★ 実測: 001 の 2 回目は **attempt 1・2 とも `max_turns` 到達**で打ち切られた（実装は積み上がった）。
3. ⚠️ **`verify_level: recheck`（005 / 007）をどうするか決める**（→ 判断 8 の未決 2）。
   ★ 実測: watchdog が **2 回連続で空応答** → fail-closed で `blocked`。
   ⚠️ `loop-run.sh:243-246` 自身が逐語「**`recheck` の watchdog は現状まだ完全に信頼できる gate ではない**」
   「**AC を機械的に検査できるなら `<id>-acceptance.sh` を書くほうが確実**」と書いている。
   → ★ 現実的な線は **`parse` に落とし、`acceptance.sh` を厚くし、人がレビューで締める**。

## §3 ★ 001 から引き継ぐ実体（⚠️ 002〜007 はここに乗る）

- ★ 共有ヘルパ（`analysis/feat_offline/mod.rs`）: `extract_pause_resumptions` / `net_production` /
  `build_feature_rows(keys, paste_ts, max_ticks)`。
  ⚠️★★★ **独自の pause / net 定義を作らないこと**（Codex TASK-PRE 指摘 5）。
- ★ 定数は **`features::PAUSE_THRESHOLD_MS`** と **`loop_step::ENGINE_TICK_MS`** を `use` する。
  ⚠️ `feat_offline/` 配下に**数値定数を宣言しない**（★ acceptance が落とす。テスト用は `TEST_` 接頭辞）。
- ★ `t_ms` は **絶対 epoch ms**。
- ⚠️★★★ **issue 005（`stall onset`）への申し送り**: 共有ヘルパは **press ペアの間隔しか見ない**。
  **閉じない末尾の沈黙**（ADR-030 D3 逐語「沈黙こそ最長の停滞である」・評価時刻に `{t + W}` を含む）と
  **`feat` 行の穴**（D8 (b-2)）は**扱っていない**。★ 005 が補うこと。
  ⚠️ **原因ラベルを作る方向で直さない**（`redaction.rs` の約束・ADR-030 却下リスト 9）。

## §4 ★ acceptance を書くときの型（★ 001 で実証した）

⚠️★★★ **「新しい定数が無い」の否定形だけでは足りない。** ★ 001 では `>= 2000` の直書きも
`mod.rs` の `TICK_MS` 再宣言も**緑のまま通った**。→ ★ 3 点セットで書く:

1. **否定形**: `feat_offline/` 全体に数値定数の宣言が無い
2. **肯定形**: 既存 SSOT（`PAUSE_THRESHOLD_MS` / `ENGINE_TICK_MS`）を**実際に参照している**
3. **直書き禁止**: 比較の形（`>=`/`<` など）でリテラルが残っていない

★ 加えて **出力キー集合の完全一致**（⚠️ フィールドが増えたら落ちる＝privacy の門を両側にする）と、
**退化していないこと**（総和 > 0）を入れる。
⚠️★★★ **検査を書いたら、検査自体を 3 状態で試す**（正常 / 壊れている / 誤検出しうる正当な形）。

## §5 実行手順

```bash
# 0. 事前に §2 の 1〜3 を片付ける（★ Dependencies・max_turns・verify_level）
cd /c/GSE-prototype
git status --porcelain            # ★ クリーンであること（dirty だと worktree 生成に失敗する）

# 1. 002 から順に回す（★ DAG は直列なので 1 本ずつでもまとめてでもよい）
bash scripts/loop-run.sh .steering/20260914-mhd-feature-offline-tiers --issues 002

# 2. 監視
/loop-status

# 3. 各 issue が緑になったら（⚠️ 自己申告を信じない）
#    - pin 済み verify 4 本と <id>-acceptance.sh を**自分で走らせて** exit 0 を確認する
#    - code-reviewer と security-checker を**並列**で起動する（★ 001 では HIGH が 3 件出た）
#    - 直してから merge する
```

## §6 実行条件（★ 継続・変更なし）

- ブランチ `docs/adr-030-stall-onset-definition`（⚠️ **main へ switch しない** — ADR-030/031/032 はここにしかない）。
- ⚠️ `git add -A` / `git add <dir>` を使わない（★ 明示ファイル指定）。
- ⚠️ `_loop-config.json` の `allowed_tools` を `null` にしない。
- ⚠️ `.gitignore` の `_loop-events.jsonl` / `_loop-board.md` / `_loop-run-report.md` を外さない。
- ⚠️ `HMM_VERSION` を bump しない／ゴールデン snapshot を再生成しない。
- ⚠️ `schema_dto.rs` / `logger.rs` / `capabilities.rs` を触らない。
- ⚠️ `features.rs` / `engine.rs` / `loop_step.rs` は**読むだけ**（★ `use` は可。変更は判断 7 の 1 回きりの例外）。
- ★ 応答は日本語。設計裁定は Opus、実装は Sonnet。

## §7 ★ タスク完了時に残っている宿題

- ⚠️ `docs/repository-structure.md` の `analysis/` 一覧に **`feat_offline` が無い**（★ `/finish-task` で回収）。
- ⚠️ `/cross-review`（**2 巡**）は **タスク完了時に必須**（★ CLAUDE.md）。⚠️ 001 単体では未実施。
- ⚠️ `permission_denials` の中身は**依然未検証**（→ 判断 8 の未決 3）。
  ★ 検証するなら `loop-run.sh:342` の `res` を `WORK_TMP` に保存する改修が先。
