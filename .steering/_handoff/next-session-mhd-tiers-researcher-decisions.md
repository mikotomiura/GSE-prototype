# 次セッション — タスク 2（Mh-D 特徴量の Tier 別オフライン実装）の残り：研究者判断と完了処理

> 作成: 2026-09-18 / ⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.steering/20260914-mhd-feature-offline-tiers/decisions.md`（**判断 18〜24**）／`blockers.md`（**起票 1〜17**）／
> 各 `issues/*.md` の Status と Execution Result ／ `docs/adr/ADR-030-...md` ／ `docs/loop-engineering.md`。
> ★ 前段は `next-session-loop-issues-002-007.md`（**消化済み・履歴**）。

---

## §1 いまの状態（★ 2026-09-18 実測）

- ブランチ `docs/adr-030-stall-onset-definition`、HEAD は `6b7daef` 以降。⚠️ **main へ switch しない**（ADR-030 / 031 / 032 はここにしか無い）。
- ★ **実装済み・merge 済み**（`gse-replay --features` の Tier）:

  | issue | 中身 | merge | 備考 |
  |---|---|---|---|
  | 001 | `T0` activity | `061e6fb` | |
  | 002 | `T1b` boundary | `a4400b9` | |
  | 003 | `T1a` dispersion | `46f98ff` | ⚠️ 起票 7（分位点が構造的に退化）が開いたまま |
  | 005 | `stall onset`（`t0`） | `da1b8b2` | ⚠️ レビュー未通過で merge されていた → 008 で是正 |
  | **008** | ★ `stall onset` の是正（観測区間 = ADR-030 D8 (b-2)・末尾の沈黙・`task_kind`・O(N log N)） | **`2b417c1`** | 判断 18 / 22 |
  | **007** | ★ `Q` evidence quality | **`08423b2`** | 判断 21 / 23 / 24 |

- ★ **merge 後の客観検証（`08423b2`・裁定セッションが直接実行）**: `cargo test --workspace` **745 passed** /
  ゴールデン `OK: 15 snapshots match` / check・clippy・fmt **exit 0** / acceptance **001・002・003・005・007・008 すべて OK**。
- ⚠️ **保留（研究者の定義待ち）**: **004 `T1c`**（判断 17 / 起票 9）・**006 `T1d`**（判断 20 / 起票 17）。
- worktree・`loop/*` ブランチは**残っていない**（`.worktrees/codex-rescue-20260916-theory-review` は**別トラックのもの。触らない**）。

## §2 ★★★ 最初にやること：研究者判断を仰ぐ（⚠️ 推測で埋めない）

★ **以下はすべて「定義を作る」か「事前宣言の値を決める」案件**であり、裁定セッションが代わりに決めない（判断 16 / 17 / 20 の規律）。
★ 候補と代償は各起票に書いてある。**AskUserQuestion で研究者に選んでもらう**のが最初の仕事。

| 起票 | 何を決めるか | 解けると進むもの |
|---|---|---|
| **9** | `T1c` の `rewrite` / `redelete` / `loop_depth` / `local_recurrence` の算出式（★ 3 候補ずつ表あり） | issue 004 |
| **17** | `T1d` の集計窓・`restop_ms`・`stable_generation_ms`・分類（★ ⚠️「再停止」は ADR-031 の**転帰**側の語。二重定義にしない） | issue 006 |
| **7** | `T1a` の集約窓（(a) 窓を広げる / (b) p50・p90 を落とす / (c) 判断 2 を見直す） | 003 の是正 |
| **11** | ⚠️★★★ ADR-030 D3 の修飾キー規則 —— `KeyCategory::Modifier` は **Shift を含む**（逐語どおりだと大文字・記号が産出から外れる。匿名化データでは Shift と Ctrl を区別できない） | ADR-030 の改訂 |
| **12** | IME 変換中の抑制（区間の形・「抑制」の意味。⚠️ 20 秒超の変換は行が出ない） | 検出器 |
| **13** | ポインタ活動の両極（出力の形：列を 2 本か別モードか） | 検出器 |
| **14** | `warmup_count` の値・`cold_start` の集団 prior（★ 部品が存在しない）・刻印（`feature_schema_version` 等） | 検出器・起票 2 |
| **15** | `hole_gap_ms` の値 ＋ ⚠️ **削除 UI の最小幅 > `hole_gap_ms`** を redaction 側で同時に固定 | 検出器・redaction |
| **16** | 事前宣言した値を `--features` へ渡す経路（★ 値が決まってから作る） | CLI |
| **2 / 5** | `--features` 出力の「由来の封筒」と、共有しないことの機械的な門 | 出力形状 |

## §3 研究者判断が要らない残り

1. ★ **`capability matrix`**（ADR-032 **M7**）—— ⚠️ **Loop に載せない**（判断 4）。範囲は判断 5。結果で ADR-032 の未決 ④ / ⑤ と起票 21 を閉じる。
2. ★ 起票 8（pause の「対の突き合わせ」の一本化・`boundary.rs` / `dispersion.rs`）—— 小さなリファクタ issue として切れる。
3. ★ Loop 基盤（⚠️ 本タスクの範囲外だが、次に Loop を回す前に効く）:
   - 起票 10: worker が `git checkout` で worktree 隔離を外せる（`allow: Bash(git *)`）／ attempt 後にブランチを検査していない。
   - 起票 3: `permission_denials` の中身が未検証（★ **worker の transcript は `~/.claude/projects/C--wt-GSE-prototype-<id>-issue/*.jsonl` に残る**。一次資料はそこ）。
   - 起票 4: `preflight_dag` の文言。
   - ⚠️ worker の sandbox は `bash <script>` を承認ゲートで拒否する（★ worker は acceptance を自分で通しで回せない。loop-run 側の verify は回る）。
4. ★ **タスク完了時の宿題**（★ 004 / 006 が残るので、完了処理はそれらの後）: `docs/repository-structure.md` の `analysis/` 一覧に `feat_offline`／
   `/cross-review` **2 巡**（★ CLAUDE.md 必須）／`_loop-retrospective.md`／`/finish-task`。

## §4 ★ 今回の教訓（★ 次に acceptance や issue を書くとき効く）

- ⚠️★★★ **Loop の worker は 003〜008 のあいだ `/loop-issue` の指示を一度も受け取っていなかった**（git-bash の MSYS パス変換）。
  → ★ `446fa3b` で修正済み（判断 19）。★ **worker の最初のメッセージが `<command-name>/loop-issue</command-name>` であることを transcript で確かめてから待つ。**
- ⚠️★★★ **acceptance の自己矛盾・前提の欠落が 4 件目まで続いた**（判断 13 / 16 / 21 / 23）。★ 規律:
  1. 実 fixture で正常系の前提が成り立つかを**回す前に**確かめる（★ 参照実装を別言語で書くと早い）。
  2. 検査の 3 状態テストは **`ACC_SKIP_*` で省いた部分を未検証と明記し、実装が出たら必ず通しで回す**（判断 23）。
  3. **merge ゲートでは 001〜最新の acceptance を全部回す**（★ 001 の最上位キー集合が 002 以降ずっと NG だった・判断 18）。
     ★ Tier を足す issue を merge したら `001-acceptance.sh` の最上位キー集合に 1 語足す。
- ⚠️ **「テストが名前どおりの検出力を持たない」は mutation でしか分からない**（判断 14 / 16 / 22 / 24）。★ レビューには mutation を必ず頼む。
- ★ `security-checker` の削除の再現（`redaction.rs::retain_outside_range` の忠実移植）は強力だった —— 資材はジョブ一時領域にあったので消えている。★ 必要なら再作成。

## §5 実行条件（★ 継続）

- ⚠️ `git add -A` / `git add <dir>` を使わない（★ 明示ファイル指定）。⚠️ 作業ツリーには**別トラックの未コミット変更**
  （`.steering/_handoff/README.md` / `docs/references.md` / `.steering/20260916-*` ほか）がある —— **触らない・stage しない**。
  ★ Loop を回すときは `LOOP_FORCE=1` が要る（dirty tree のため。worktree は index を共有しないので安全）。
- ⚠️ `_loop-config.json` の `allowed_tools` を `null` にしない。⚠️ `HMM_VERSION` を bump しない／ゴールデン snapshot を再生成しない。
- ⚠️ `schema_dto.rs` / `logger.rs` / `capabilities.rs` を触らない。`features.rs` / `engine.rs` / `loop_step.rs` は読むだけ。
- ★ 応答は日本語。設計裁定は Opus、実装は Sonnet（★ 今回はレビュー是正を Sonnet のサブエージェントへ委譲した）。
- ⚠️ **利用上限**: 2026-09-18 に Opus のサブエージェントが HTTP 429（月次上限）で途中終了した。★ レビューの回数と範囲を計画的に。
  ★ 008 の Loop は $13.80（1 回目の run は MSYS の不具合で空回り）。
