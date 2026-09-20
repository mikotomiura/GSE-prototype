# 次セッション — タスク 2（Mh-D 特徴量の Tier 別オフライン実装）の残り：研究者判断と完了処理

> 作成: 2026-09-18 / ⚠️★★★ **このメモを一次資料にしない。**
> ★ 一次は `.steering/20260914-mhd-feature-offline-tiers/decisions.md`（**判断 18〜25**）／`blockers.md`（**起票 1〜17**）／
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
  > ★★★ **2026-09-19 更新（判断 26）**: 算出式と名前は理論レビューで**確定**し、issue 004 / 006 の Background・AC1・受け入れスクリプトへ**転記済み**である（`.steering/20260918-theory-critical-review/decisions.md` 判断 2）。
  > ⚠️★★★ ただし両 issue とも **`blocked` のまま**である。004 は **U1〜U4**、006 は **V1〜V5** の実装設計を、**実装フェーズの設計議論で先に裁定する**（★ 研究者の指示: 「E1の箇所は具体的に設計議論などが実行後での実装フェーズにて実装する形にしましょう」）。
  > ⚠️ 最初に扱う発見は 3 つある（詳細は判断 26）:
  > - E1 を検出列に入れると、`recovery` が未実装のあいだは、同じ観測区間で onset が 1 回しか立たない。
  > - 条件 A が `stall_onset.rs` の非公開関数にある。
  > - 006 の fixture では AC6 が原理的に通らない。
  > ⚠️ 改訂した受け入れスクリプトは `bash -n` とダミー行での jq 検算しか通していない（★ 実装が出たら通しで回す）。
  > ⚠️★★★ **Loop 基盤の修正で扱う**: `loop-run.sh` の `issue_ids()` は `## Status` を読まないので、`--issues` なしで回すと `blocked` の 004 / 006 も走る（判断 26・`/cross-review` 2 巡目）。★ 006 の未決は V5（窓そのものが無いとき）を足して **V1〜V5** になった。
- worktree・`loop/*` ブランチは**残っていない**（`.worktrees/codex-rescue-20260916-theory-review` は**別トラックのもの。触らない**）。

## §2 ★★★ 研究者判断は 2026-09-18 に仰いだ（★ `decisions.md` **判断 25**・16 問）

★ **タスク 2 はここで中断し、理論の批判的レビュー（`next-session-theory-critical-review.md`）へ移った**（判断 25 #1）。
★ 各起票の結論（⚠️ 詳細は判断 25 と `blockers.md` の各起票の冒頭の注記）:

| 起票 | ★ 研究者の回答 | 次に何が起きるか |
|---|---|---|
| **9** `T1c`（004） | 理論レビューで扱い、保留を続ける | 理論レビューで算出式が決まる |
| **17** `T1d`（006） | 理論レビューで EVAL-NCC の「再停止」と一体に決める | 同上 |
| **7** `T1a` の窓 | 事前宣言と一緒に決める | P1 前の事前宣言文書 |
| **11** 修飾キー規則 | ★ **規則あり・なしの両極で挟む**／実装はポインタ極と同じ時期 | ADR-030 補訂案は理論レビューで・実装は P1 の解析設計 |
| **12** IME 抑制 | P1 で頻度を見てから | P1 |
| **13** ポインタ両極 | P1 まで極 A のみ | P1 の解析設計 |
| **14 / 16** 事前宣言値・CLI | P1 前に 1 本の宣言文書で（CLI 注入も同時に） | 事前宣言文書 |
| **15** `hole_gap_ms` | 仮の値のまま ＋ **削除 UI の最小幅 > `hole_gap_ms` を redaction 側で固定** | 小タスク（redaction の制約とテスト） |
| **2 / 5** 封筒・共有の門 | 封筒を足す小 issue | Loop 基盤の修正の後 |
| **3 / 10** Loop 基盤 | 次に Loop を回す前に直す | 小タスク |
| — ADR-030 への反映 | 理論レビューの中で補訂案 → 人の採否 → 反映 | 理論レビュー |
| — `capability matrix` | 理論レビューの後 | — |

★ **再開順**（判断 25）: 理論レビュー → Loop 基盤の修正 → 封筒 issue → 004 / 006 → `capability matrix` → P1 前の事前宣言文書 ＋ CLI ＋ 両極。

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

- ⚠️ `git add -A` / `git add <dir>` を使わない（★ 明示ファイル指定）。★ 別トラックの未コミット変更（`.steering/20260916-*` /
  `docs/references.md` の [P361]〜[P367] / 引き継ぎメモ 2 本 / 索引の行）は **2026-09-18 に研究者の指示ですべてコミットした**（判断 25 #3）。
  ⚠️ 今後また別トラックの未コミット変更が出たら、**触らない・stage しない**。
  ★ Loop を回すときは `LOOP_FORCE=1` が要る（dirty tree のため。worktree は index を共有しないので安全）。
- ⚠️ `_loop-config.json` の `allowed_tools` を `null` にしない。⚠️ `HMM_VERSION` を bump しない／ゴールデン snapshot を再生成しない。
- ⚠️ `schema_dto.rs` / `logger.rs` / `capabilities.rs` を触らない。`features.rs` / `engine.rs` / `loop_step.rs` は読むだけ。
- ★ 応答は日本語。設計裁定は Opus、実装は Sonnet（★ 今回はレビュー是正を Sonnet のサブエージェントへ委譲した）。
- ⚠️ **利用上限**: 2026-09-18 に Opus のサブエージェントが HTTP 429（月次上限）で途中終了した。★ レビューの回数と範囲を計画的に。
  ★ 008 の Loop は $13.80（1 回目の run は MSYS の不具合で空回り）。
