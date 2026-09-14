# Issue Plan — タスク 2（Mh-D 特徴量の Tier 別オフライン実装）

> 生成: 2026-09-14 / ★ `issue-slicing` skill（`docs/loop-engineering.md` の 7 基準）に従う。
> ⚠️★★★ **このファイルを一次資料にしない。**一次は `docs/adr/ADR-030` / `ADR-032` / `docs/loop-engineering.md`。

## 1. issue 一覧

| id | 中身 | verify_level | Allowed Files（新規は ★） |
|---|---|---|---|
| **001** | `--features` モード ＋ `T0`（activity） | **recheck** | `bin/replay.rs` / `analysis/mod.rs` / ★`feat_offline/mod.rs` / ★`feat_offline/activity.rs` |
| **002** | `T1b`（boundary） | parse | `feat_offline/mod.rs` / ★`feat_offline/boundary.rs` |
| **003** | `T1a`（dispersion） | parse | `feat_offline/mod.rs` / ★`feat_offline/dispersion.rs` |
| **004** | `T1c`（revision topology） | parse | `feat_offline/mod.rs` / ★`feat_offline/revision.rs` |
| **005** | `stall onset`（`t0`）検出器 | **recheck** | `feat_offline/mod.rs` / ★`feat_offline/stall_onset.rs` |
| **006** | `T1d`（restart） | parse | `feat_offline/mod.rs` / ★`feat_offline/restart.rs` |
| **007** | `Q`（evidence quality） | **recheck** | `feat_offline/mod.rs` / ★`feat_offline/quality.rs` |

★ 順序は **ADR-030 D10 の投資順序**に従う —— 逐語「⚠️★★★ **`T1` の内側では `T1b`（境界）を
`T1a`（分布）より先に置く。**」→ ★ `001 → 002(T1b) → 003(T1a) → 004 → 005 → 006 → 007`。

### ⚠️★★★ Loop に載せないもの

| 何 | なぜ |
|---|---|
| **`capability matrix`**（ADR-032 **M7**） | ★ 研究者判断 2026-09-14: 「**実装 issue だけ Loop、matrix は対話で行う**」（→ `decisions.md` 判断 4）。⚠️ 中身は一次資料の読み込みと裁定で、`acceptance.sh` は「行があること」しか検査できない（＝ 客観に見えて無意味な緑）。★ 範囲は `decisions.md` 判断 5 |
| ⚠️ `undo` / `redo`・`key.mod` の実装（ADR-032 **M5**） | ★ **ADR-032 が Accepted になり、同意 §3 の改訂（M4）が通ってから**。⚠️ 研究者承認待ち |
| ⚠️ `T2` / `T3` | ★ ADR-032 **D3** で `T2` は解かない / **D4** で `T3` は不採 |

## 2. 依存 DAG（★ 循環なし）

```text
001 → 002 → 003 → 004 → 005 → 006 → 007
```

- **最長 chain: 7 段**（＝ 直列時の総ウェーブ数）。
- **循環: なし**（★ 各 issue の `## Dependencies` は自分より小さい id を 1 つだけ持つ）。
- ★ `budget.parallel: 1`（引き継ぎ §6 の指示。★ 初回の無人実行なので最小で回す）。

### ⚠️ なぜ完全な直列なのか（★ `decisions.md` 判断 6）

★ 各 issue は自分の `tXX.rs` を作るが、**`feat_offline/mod.rs` に `pub mod` 1 行と
`FeatureRow` のフィールド 1 個を足す**ため、**Allowed Files が必ず交差する**。
→ ★ 基準 3 逐語「交差するなら `## Dependencies` で直列化する」に従う。

⚠️ **交差を消す案（001 が全 Tier の空プレースホルダを先に作る）は採らなかった** ——
★ 001 が 10 ファイルに膨らみ**基準 2（≤ 5 ファイル）を超える**うえ、
⚠️ 001 は「**最も安い issue 1 本を `parallel=1` で回して基盤を検証する**」の対象なので、
そこを一番大きくするのは目的に反する。

## 3. Allowed Files 交差表

| | 001 | 002 | 003 | 004 | 005 | 006 | 007 |
|---|---|---|---|---|---|---|---|
| **001** | — | ✕ | ✕ | ✕ | ✕ | ✕ | ✕ |
| **002** | ✕ | — | ✕ | ✕ | ✕ | ✕ | ✕ |
| **003** | ✕ | ✕ | — | ✕ | ✕ | ✕ | ✕ |
| **004** | ✕ | ✕ | ✕ | — | ✕ | ✕ | ✕ |
| **005** | ✕ | ✕ | ✕ | ✕ | — | ✕ | ✕ |
| **006** | ✕ | ✕ | ✕ | ✕ | ✕ | — | ✕ |
| **007** | ✕ | ✕ | ✕ | ✕ | ✕ | ✕ | — |

★ ✕ = **交差する（並列不可）**。交差の実体は **すべて `feat_offline/mod.rs` 1 本**である。
→ ★ **並列可能な組は 1 つも無い。**`budget.parallel` を上げても意味がない。

## 4. 最初の単独ウェーブ

⚠️★★★ **pin 済み `verify` の前提を変えるのは 001 だけ**である
（★ `bin/replay.rs` を触るので、ゴールデン replay `--snapshot` の経路に隣接する）。
→ ★ 001 を**最初に単独で**回し、基盤（権限 / cwd 境界 / hook 発火 / 契約の二重定義）を検証する。
⚠️ SSOT 逐語「**`--dry-run` では権限・cwd 境界・hook 発火・契約の二重定義が観測できない**（実測で 2 回空振り）」。

## 5. ベースライン（★ 2026-09-14 実測・⚠️ 予測ではない）

| pin 済み verify | exit |
|---|---|
| `cargo test --manifest-path src-tauri/Cargo.toml --workspace` | **0**（670 passed / 0 failed） |
| `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` | **0**（`OK: 15 snapshots match`） |
| `cargo check --manifest-path src-tauri/Cargo.toml --workspace --all-targets` | **0** |
| `cargo clippy --manifest-path src-tauri/Cargo.toml --workspace --all-targets -- -D warnings` | **0** |

⚠️ ゴールデン replay は `session hmm_version = 0.2.0, current engine = 0.5.0` の**警告を出すが exit 0**。
★ **これが既存のベースラインである。**⚠️「無視してよい」と断定しない。

## 6. `verify_level` の選別（★ 基準 5）

| id | level | 理由 |
|---|---|---|
| 001 | **recheck** | ★ **公開 CLI（`--features`）を新設**し、⚠️ ゴールデン replay の経路に隣接する |
| 005 | **recheck** | ★ **AC 直結**（`t0` は本トラック全体の原点。⚠️ 誤ると後続の転帰がすべて歪む） |
| 007 | **recheck** | ⚠️★★★ **data-privacy に触れる**（★ 欠測理由に被験者由来が混ざると、端末内で完結すると約束した削除の事実が共有物に出る） |
| 002 / 003 / 004 / 006 | parse | ★ 純関数の追加で、AC は `acceptance.sh` と単体テストで機械的に取れる |

⚠️ **全部 parse にしていない**（基準 5 のアンチパターン）。

## 7. ⚠️ 実行前に効く前提（★ 忘れると空振りする）

1. ⚠️★★★ **`base_branch` は `docs/adr-030-stall-onset-definition`** に pin してある。
   ★ **ADR-030 / 031 / 032 はこのブランチにしか無い**（★ ADR-029 だけ main にマージ済み）。
   ⚠️ `main` から worktree が切られると **ADR が存在せず全 issue が即死する**。
2. ⚠️ `events_path` は **git-bash 形式の絶対パス**（`/c/GSE-prototype/...`）。
   ★ `loop-run.sh:53` は `/` 始まりを要求するので、`C:/...` にすると **起動時に die する**。
3. ⚠️★★★ **`acceptance_template` は `loop-run.sh` に読まれない。**
   ★ 実際の規約は **`$TASK_DIR/issues/<id>-acceptance.sh` のハードコード**（`loop-run.sh:235`）。
   → ★ 本タスクはその規約どおりに置いてある（⚠️ config の値を変えても効かない）。
4. ★ `verify` は **固定 3 種**（`test` → `typecheck` → `lint` の順）。
   ★ ゴールデン replay は `test` の後段に `&&` で繋いである（⚠️ 4 つ目のキーは読まれない）。
5. ⚠️ Loop の実行時生成物（`_loop-events.jsonl` / `_loop-board.md` / `_loop-run-report.md`）は
   **2026-09-14 に `.gitignore` へ追加済み**。★ 無視されていないと `loop-spawn.sh` の
   dirty-tree 判定に当たり、**1 issue 目から worktree 生成に失敗する**（★ 実測で再現した）。
6. ★ worktree には必須 `permissions.deny` 7 件が**自動注入され、attempt ごとに再検査される**
   （★ 2026-09-14 に実装）。⚠️ ただし **注入されていること ≠ 発効していること**は未検証である。

## 7b. ⚠️ TASK-PRE（Codex の第二意見）を反映した点

★ `docs/loop-engineering.md` の Codex ゲート **TASK-PRE** を 1 回実行した（→ `_codex-preplan.md` に全文と採否）。
★ **採用した 4 件**（⚠️ 不採用 2 件・部分採用 1 件は理由つきで preplan に記録した）:

| 反映先 | 内容 |
|---|---|
| **001** | ★ `pause` / `net` の抽出を **`mod.rs` の共有ヘルパ**として所有する（AC 8）。⚠️ Codex 指摘 5: 002〜004 が局所的な pause 定義を持つと **005 が別定義を要求して破壊的変更になる** |
| **001** | ★ **Tier ごとの causal / retrospective の区分**を明記する（AC 9）。⚠️ Codex 指摘 3: 「その時点で既知」と「後から付けたラベル」を tick 行で混ぜない |
| **001** | ⚠️ **境界入力で落ちない**（空ログ / 単一イベント / 同一 timestamp / 時刻逆行 / tick 境界ちょうど / 閉じない最終 pause）（AC 10）。★ Codex 指摘 4 |
| **002〜006** | ★ **共有ヘルパを使うこと**を AC ＋ `acceptance.sh` の grep で強制した |
| **006** | ⚠️★★★ `restart` は **retrospective** と明記し、**detection 側へ渡さない**（AC 7）。★ Codex 指摘 3 |

## 8. 分解の自己検査（★ `issue-slicing` skill の締め）

- [x] 各 issue を**単体 merge**しても main が壊れないか
  → ★ すべて **追加のみ**（新規モジュール ＋ `--features` モードの新設）。既存経路を変更しない。
- [x] 各 AC に対応する **test 名を「今」書けるか** → ★ 全 issue の AC 表に記載済み
- [x] **Allowed Files 交差表**を作り、並列可能な組を根拠付きで示したか → ★ §3（**並列可能な組は無い**）
- [x] **DAG に循環がないか。最長 chain は何段か** → ★ 循環なし / **7 段**
- [x] **recheck を基準 5 で選別したか**（全部 parse にしていないか） → ★ §6（3 本 recheck）
- [x] AC が書けない「リファクタするだけ」の issue を作っていないか → ★ 無し
- [x] **pin 済み verify の前提を変える issue を最初の単独ウェーブに置いたか** → ★ §4（001）
- [x] **test/lint が無条件に緑になる issue に `acceptance.sh` を書いたか**
  → ★ **全 7 本に書いた**（⚠️ `cargo test` は新特徴が出力に出ているかを見ないため）

## 9. ⚠️★★★ 実行の作法

1. ⚠️ **この分解セッションで実行を始めない。**★ `/clear` して**新セッション**で回す
   （★ CLAUDE.md 逐語「issue 分解と loop 実行は**別セッション**」）。
2. ★ 実行: `bash scripts/loop-run.sh .steering/20260914-mhd-feature-offline-tiers --issues 001`
   → ★ 001 が緑になったら残りを回す。
3. ★ 監視: `/loop-status`（★ board の単一書き手）。
4. ⚠️ **`issue_done` を自己申告で信じない** —— ★ `recheck` の 3 本は watchdog の客観再検証を通す。
5. ★ 全緑後: `/cross-review`（**2 巡**）＋ `code-reviewer` / `security-checker` → merge → retrospective。
