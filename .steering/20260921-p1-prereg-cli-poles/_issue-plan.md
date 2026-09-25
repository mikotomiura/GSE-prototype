# issue plan — P1 前: 事前宣言文書 ＋ CLI 注入 ＋ 両極

> ★ 分解は **Opus**（`issue-slicing` Skill・`docs/loop-engineering.md` のモデル割当）。
> ★ 前段の grill の裁定は `decisions.md` 判断 1〜16。
> ⚠️ **【1】事前宣言文書と凍結 JSON は本セッションの対話で作り済み**（commit `1cd25ce`）。
> 本計画が扱うのは **【2】以降**である。

## 1. issue 一覧

| id | 題 | verify_level | Dependencies | 変更の中心 |
|---|---|---|---|---|
| **001** | 凍結値の CLI 注入 ＋ θ の標本数 | `recheck` | （なし） | `bin/replay.rs` / `stall_onset.rs` |
| **002** | 削除の最小幅を入口で保証する | `recheck` | （なし） | `lib.rs` / `redaction.rs` / UI |
| **003** | `T1a` の 30 秒ローリング窓 | `recheck` | 001 | `dispersion.rs` / `features.rs` |
| **004** | 極の器（`--pole`） | `recheck` | 003 | `bin/replay.rs` / `stall_onset.rs` |
| **005** | 極 M+（修飾キー） | `recheck` | 004 | `bin/replay.rs` / `stall_onset.rs` |
| **006** | 極 B（ポインタ） | `recheck` | 005 | `bin/replay.rs` / `stall_onset.rs` |
| **007** | IME 変換中の onset 頻度カウンタ | `parse` | 006 | `stall_onset.rs` / `mod.rs` |
| **008** | 計算量の門 ＋ 3 極スクリプト | `parse` | 006 | `scripts/` / 前タスク acceptance |
| **009** | ADR-030 補訂 2 ＋ 起票の是正記録 | `parse` | 007, 008 | `docs/adr/` / 前タスク `blockers.md` |

### ⚠️ `verify_level` の選別根拠（★ 基準 5）

- **`recheck`**（001〜006）: **公開 API（CLI）**を変える ／ **criterion の定義**（条件 A の写像・
  観測区間・分位点）を変える ／ **被験者への約束**（削除）に触れる。
- **`parse`**（007〜009）: 出力フィールドの追加・検証スクリプト・文書。
  ⚠️ onset 集合を動かさないことが AC で固定されている。

## 2. 依存 DAG（⚠️ 循環なし）

```
  001 ──────┬──▶ 003 ──▶ 004 ──▶ 005 ──▶ 006 ──┬──▶ 007 ──┐
            │                                   │          ├──▶ 009
  002 ──────┘(独立)                             └──▶ 008 ──┘
```

- ★ **最長 chain = 7 段**（`001 → 003 → 004 → 005 → 006 → 007 → 009`
  ／ `… → 006 → 008 → 009` も 7 段）。
- ★ **直列時の総 attempt 見積り**: 7 段 × `max_attempts` 6 = **最大 42 attempt**。
  ⚠️ 実績（前タスク）は 1 issue あたり 1〜4 attempt。

### ★ ウェーブ（`parallel: 2` のとき）

| ウェーブ | issue | 根拠 |
|---|---|---|
| **W1** | **001 ‖ 002** | ★ Allowed Files が交差しない（下表）。⚠️ 001 は「pin 済み verify の前提を変える」ので、**002 以外とは並列にしない** |
| W2 | 003 | |
| W3 | 004 | |
| W4 | 005 | |
| W5 | 006 | |
| **W6** | **007 ‖ 008** | ★ 007 は `src-tauri/src/` のみ、008 は `scripts/` と前タスク acceptance のみ。交差しない |
| W7 | 009 | |

## 3. Allowed Files 交差表（★ 並列可能性の根拠）

### 3.1 各 issue の集合（⚠️ 自分の `00X-acceptance.sh` は必ず自分専用なので表から省く）

| id | Allowed Files |
|---|---|
| 001 | `bin/replay.rs`, `feat_offline/stall_onset.rs`, `feat_offline/mod.rs`, `feat_offline/restart.rs`（★ テストのリテラルのみ・判断 17）, `prereg/p1-episode.json`, `docs/preregistration-p1-episode.md`, **前タスク** `005/006/008-acceptance.sh` |
| 002 | `lib.rs`, `redaction.rs`, `src/components/RecordingControls.tsx`, `docs/o1-deletion-ledger.md` |
| 003 | `analysis/features.rs`, `feat_offline/dispersion.rs`, `feat_offline/mod.rs`, `tests/fixtures/t1a_window.ndjson`, **前タスク** `003-acceptance.sh` |
| 004 | `bin/replay.rs`, `feat_offline/stall_onset.rs`, `feat_offline/mod.rs`, `feat_offline/restart.rs`（★ テストのリテラルのみ・判断 17） |
| 005 | `bin/replay.rs`, `feat_offline/stall_onset.rs`, `feat_offline/mod.rs`, `feat_offline/restart.rs`（★ テストのリテラルのみ・判断 17）, `tests/fixtures/modifier_pole.ndjson` |
| 006 | `bin/replay.rs`, `feat_offline/stall_onset.rs`, `feat_offline/mod.rs`, `feat_offline/restart.rs`（★ テストのリテラルのみ・判断 17）, `tests/fixtures/pointer_pole.ndjson` |
| 007 | `feat_offline/stall_onset.rs`, `feat_offline/mod.rs`, `feat_offline/restart.rs`（★ テストのリテラルのみ・判断 17）, `tests/fixtures/ime_overlap.ndjson` |
| 008 | **前タスク** `008-acceptance.sh`, `scripts/run-features-all-poles.sh`, `docs/verification-runbook.md` |
| 009 | `docs/adr/ADR-030-….md`, **前タスク** `blockers.md`, **前タスク** `tasklist.md` |

⚠️★★★ **2026-09-25 追記（判断 17）**: 001 / 004 / 005 / 006 / 007 に `restart.rs`（`#[cfg(test)]` 内のリテラルのみ）を足した。★ 5 本は元から直列で、並列相手の 002 / 008 は `restart.rs` を触らないので、下表の並列可否は変わらない。

### 3.2 交差（★ `∅` = 並列可能）

|  | 001 | 002 | 003 | 004 | 005 | 006 | 007 | 008 | 009 |
|---|---|---|---|---|---|---|---|---|---|
| **001** | — | **∅** | `mod.rs` | 3 本 | 3 本 | 3 本 | 2 本 | 前 `008-acc` | ∅ |
| **002** | **∅** | — | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ |
| **003** | `mod.rs` | ∅ | — | `mod.rs` | `mod.rs` | `mod.rs` | `mod.rs` | ∅ | ∅ |
| **004** | 3 本 | ∅ | `mod.rs` | — | 3 本 | 3 本 | 2 本 | ∅ | ∅ |
| **005** | 3 本 | ∅ | `mod.rs` | 3 本 | — | 3 本 | 2 本 | ∅ | ∅ |
| **006** | 3 本 | ∅ | `mod.rs` | 3 本 | 3 本 | — | 2 本 | ∅ | ∅ |
| **007** | 2 本 | ∅ | `mod.rs` | 2 本 | 2 本 | 2 本 | — | **∅** | ∅ |
| **008** | 前 `008-acc` | ∅ | ∅ | ∅ | ∅ | ∅ | **∅** | — | ∅ |
| **009** | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | ∅ | — |

★ 「3 本」= `bin/replay.rs` ＋ `feat_offline/stall_onset.rs` ＋ `feat_offline/mod.rs`。
★ 「2 本」= `feat_offline/stall_onset.rs` ＋ `feat_offline/mod.rs`。

→ ★★★ **並列にしてよいのは `001 ‖ 002` と `007 ‖ 008` だけ**である。
⚠️ **009 は交差が `∅` だが、内容の依存（007 / 008 の実装形を規範に書く）で最後に置く。**

### ⚠️ なぜ 004〜007 を 1 本にまとめないか

★ まとめると **変更 ≒ 800 行 / AC 20 項目超**になり、基準 2（≤ 5 ファイル / ≤ 300 行 / AC 3〜7）を
大きく超える。⚠️ 逆に、交差があるので**並列にはできない** —— **直列の 4 本**が最小の切り方である。

## 4. ⚠️ 分解の締めの自己検査（★ 全部 `[x]` になるまで終わらない）

- [x] **各 issue を単体 merge しても main が壊れないか**
  - 001: 行に `theta_sample_n` が増え、`warmup_count` で onset が 1 本減る。
    ⚠️ **影響する既存 acceptance 3 本を同じ issue で更新する**（AC9 が緑を確かめる）
  - 002: 新しい定数と入口の広げ処理。⚠️ 既存 UI からは到達しない経路なので振る舞いは不変
  - 003: `pub const` 化は**振る舞い不変**（AC2 がゴールデンで固定）／ 窓は `T1a` の 3 値だけ
  - 004: 新フラグ。既定（無指定）の出力は不変（AC1）。未実装の極は exit 1
  - 005 / 006: 新しい極を 1 つずつ開通。⚠️ baseline の出力は不変（各 AC7 / AC9）
  - 007: フィールド追加のみ。⚠️ onset 集合は不変（AC6）
  - 008: 検証スクリプトと文書のみ
  - 009: 文書のみ
- [x] **各 AC に対応する test 名を「今」書けるか** —— ★ 全 AC に
  `00X-acceptance.sh` か `module::tests::<name>` を明記した
- [x] **Allowed Files 交差表を作り、並列可能な組を根拠付きで示したか** —— §3
- [x] **DAG に循環がないか。最長 chain は何段か** —— ★ 循環なし・**7 段**
- [x] **`recheck` を基準 5 で選別したか（全部 `parse` になっていないか）** ——
  ★ `recheck` **6 件** / `parse` **3 件**。選別根拠は §1
- [x] **AC が書けない「リファクタするだけ」の issue を作っていないか** ——
  ⚠️ 003 は命名リファクタを含むが、**窓の導入という振る舞いの変更**が本体であり、
  リファクタ自体も AC1 / AC2（ゴールデン byte-equal）で検証できる
- [x] **pin 済み verify の前提を変える issue を最初の単独ウェーブに置いたか** ——
  ★ 001 を W1 に置いた。⚠️ 同時に走るのは **`--features` に一切触らない 002 だけ**
- [x] **test/lint が無条件に緑になる issue に `acceptance.sh` を書いたか** ——
  ★ 008（`scripts/` と文書のみ）と 009（文書のみ）に専用 acceptance を置いた

## 5. ⚠️★★★ 実行前に読むこと（★ 前セッションの教訓）

1. ⚠️ **`--task` を落とすと fail-closed で止まる**（2026-09-21・起票 23）:
   `bash scripts/loop-spawn.sh --task <task> <id> [short]`
2. ⚠️ **解決した base の provenance を読む** —— 「既定ブランチからの乖離コミット数」が 0 でないときは
   **意図した pin か確かめる**（★ 38 コミット前から切られた実測がある）
3. ⚠️★★★ **「検査の検査」5 点**（★ `design.md` §テスト戦略）—— 前セッションは
   **8 件の欠陥を自分で作って自分で見つけ、うち 3 件はテストが緑のまま潜んでいた**
4. ⚠️ **`.codex/budget.json` の上限は 300000**。`today.tokens_used` が 432937 のままなので
   **日付が変わるまで予算ガードで止まる**（★ 意図どおり）。⚠️ **上限を勝手に引き上げない**
5. ⚠️ **`git add -A` / `git add <dir>` を使わない**（★ 作業ツリーに別ブランチの未コミット作業がありうる）

## 6. ★ 実測しておいた前提（⚠️ 推測ではない・2026-09-21）

| 事実 | 効く先 |
|---|---|
| `collect_key_events` は **press しか残さない**（`KeyPress` に `press` が無い） | ★ 005 が新しい collector を要する理由 |
| `meta` 行に **`os` が無い** ／ `capabilities` に**修飾キーの項目が無い** ／ **`key.mod` は未実装** | ★ 005 の `not_applicable` 判定がファイル単位・行数になる理由 |
| `stall_onset_observed.ndjson`: press **353**、第 1 onset 時点で press **12**（＝ 対 11） | ★ 001 で **第 1 onset が消える**（`warmup_count=100`） |
| 既存 fixture は**すべて旧形式（`vk`）**で `category` を持たない。`pointer_bin` 行は **0 本**、`capabilities` 行は `instrument_rich` の **1 本だけ** | ★ 005 / 006 / 007 が**新 fixture を要する**理由 |
| `delete_time_range` の検査は **`from_ms > to_ms` だけ** | ★ 002 の穴 |
| `features.rs:129` の `30_000` は**名前の無い生リテラル** | ★ 003 の命名リファクタ |
