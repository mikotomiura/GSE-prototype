# 次セッション開始プロンプト — `task_kind` → β 配線 (ADR-006 / Epic 2)

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-18 に PR #104 (`fix/prereg1-scale-instructions`) がマージされた。
PreReg-1 の器の作り直しと回答分散メトリクスは完了している。

---

===

## §0 ⚠️★★★ 着手前に裁くこと（★ ここを飛ばして実装に入らない）

### ⚠️★★★ ADR-006 は「Phase1 完了後」を前提にしているが、Phase1 は完了していない

★ `docs/adr/ADR-006-task-kind-beta-wiring.md` の **Migration step 1 逐語**:

> 1. **Phase1 完了 + verdict 確定を待つ（凍結解除）。**

★ ところが Phase1 の verdict は **`inconclusive` / GATE3 は `DataInsufficient`** で、
`notes.md` §5① は「**収集継続**（コード変更不要・最優先）」と書いている。**＝ Phase1 は未完了。**

⚠️ さらに ADR-006 §制約の逐語:

> β 選択ロジックの変更は **HMM 挙動の変更** = `HMM_VERSION` bump = ゴールデン不一致 =
> **Phase1 の C-index 再現性を破壊**（migration-risk-register の凍結対象）

★ **ただし ADR 自身が 2 段階に分けており、前半は挙動不変である**（Migration step 3）:

| サブフェーズ | 内容 | acceptance | HMM_VERSION |
|---|---|---|---|
| **2a 抽出** | engine/features/β を Writing head へ**挙動を一切変えず**移送。`ime_open` gate は writing 固有として保持。**β 選択ロジックは変えない** | ★ **replay --snapshot byte-equal / calibration parity** | ★ **不変** |
| **2b 配線** | `task_kind` を head/baseline 選択へ効かせる | ゴールデン再生成 + 差分が意図通りか記録 | ⚠️ **bump** |

> ★ 逐語:「**両者を混ぜて 1 コミットにしない**」

★★★ **したがって最初の判断はこれ**:

> ⚠️ **2a（挙動不変・byte-equal が acceptance）は、Phase1 完了を待たずに着手してよいか?**
> ★ 技術的にはゴールデン 4 本の byte-equal が Phase1 の再現性を保証するので安全に見える。
> ⚠️ **だが ADR の手順書は step 1 で Phase1 完了を要求している。**
> → ★ **研究者に確認してから動く。**★ 決めたら **ADR-006 に追記**する（口頭で済ませない）。

### ⚠️ ADR-002 が Proposed のまま

★ `docs/adr/ADR-002-domain-local-inference.md` の逐語:

> - **ステータス**: Proposed（方向合意）。抽出の確定は Epic 2・Phase1 完了後。**ADR-006 と一体で確定**。

★ ADR-006 Migration step 2 も「ADR-002 と本 ADR を**同時に**確定する（研究者承認）」。
→ ⚠️ **ADR-002 を Accepted にする議論が、実装より先に要る。**

## §1 ★ 最初に読むもの（この順で）

1. `docs/adr/ADR-006-task-kind-beta-wiring.md` —— ★ **全文**。Decision / 下位決定 #2・#3 / Migration
2. `docs/adr/ADR-002-domain-local-inference.md` —— ★ Proposed の中身と、確定に何が要るか
3. `docs/architecture/domain-adapter-boundary.md` —— ★ Adapter 境界（ADR-002 の受け皿）
4. `docs/research-positioning.md` §8「課題種別による停滞の質の差」/ §9 の A-Q3 解除条件（`:689` 付近）
5. `experiments/20260731-phase1-calibration-analysis/notes.md` §5 —— ★ Phase1 の verdict と分岐

## §2 ★ 実装の中身（★ ADR-006 が既に具体化している。設計をゼロから起こさない）

### ★ 現状（実測・2026-08-18）

- ⚠️ `task_kind` は **`analysis/` 層で 1 件もヒットしない＝完全な dead_code**
  （`grep -rn "task_kind" src-tauri/src/analysis/` = 0 件）
- β は `src-tauri/src/analysis/engine.rs:311` で **`ime_open` だけ**を見て 2 択している

```rust
let (beta_f1, beta_f3, beta_f4, beta_f5, beta_f6) = if ime_open {
    (BETA_WRITING_F1, ...)   // F1=100 / F3=0.10 / F4=2.5 / F5=1.0 / F6=0.12
} else {
    (BETA_CODING_F1, ...)    // F1=150 / F3=0.06 / F4=5.0 / F5=2.0 / F6=0.08
};
```

### ★ 2a 抽出（挙動不変）でやること

1. ★ **`β_coding` → `β_writing_latin` に改名**（下位決定 #2・**値はそのまま**・数値変更なし）
   —— ⚠️ 「IME off の日本語論述（英字引用・数式・URL）」は Writing head 内の latin サブ baseline であって、
   Coding の baseline ではない、という概念的分離。**改名だけなので byte-equal は保たれる**
2. ★ β を **Writing head の所有物**へ移送（「1 関数内の 2 択 if」から外す）
3. ★ `ime_open` は **Writing head 内部の within-writing 信号**として維持
   （β 切替 + 日本語 composition + **backspace ペナルティ（obs=25・streak≥14）の `!ime_open` 紐付けは現行どおり**）
4. ⚠️ **β 選択ロジックそのものは変えない**（変えたら 2a ではない）

★ acceptance: **ゴールデン 4 本 byte-equal**（`minimal` 15 / `phase1_ime_heavy` 6 /
`category_coverage` 2 / `deep_silence` 51）＋ `HMM_VERSION` **不変** ＋ `cargo test --workspace` 緑

### ⚠️ 2b 配線（挙動変更）は別コミット

★ `task_kind` → head 選択。⚠️ **`HMM_VERSION` bump → ゴールデン 4 本再生成 → 差分が意図通りか `.steering/` に記録。**
⚠️ ★ ADR-006 の逐語「**task_kind が初めて推論に効くのは Coding head 追加時（Phase2）**」なので、
★ **2b を今やる意味があるかも含めて研究者に確認する**（Phase1 は argumentative 固定＝Writing head しか走らない）。

## §3 ★ ついでにやること — Wall 廃止を docs とコードへ反映する

⚠️★★★ **研究者は Wall を廃止したが、リポジトリが追随していない**（2026-08-18 実測）。
★ 放置すると「文書の記述と実態がずれていて、次のセッションが古い前提で走る」という、
**2026-08-17 の事故とまったく同じ型**になる。

### ★ 影響範囲（実測・`grep -ci wall` の件数）

| 層 | ファイル | 件数 |
|---|---|---|
| **Rust** | `analysis/intervention.rs` | **112** |
| | `wall_server.rs` | **45** |
| | `lib.rs` | 39 |
| | `logger.rs` | 24 |
| | `analysis/intervention_eval.rs` | 13 |
| | `bin/replay.rs` | 10 |
| | `schema_dto.rs` | 6 / `overlay_panel.rs` 4 / `sensors_macos.rs` 2 / 他 3 ファイル 各 1 |
| **Frontend** | `components/Overlay.tsx` | **61** |
| | `App.tsx` | 28 / `App.css` 18 / `components/Dashboard.tsx` 13 |
| **docs** | `design-history.md` / `.ja.md` | 各 39 |
| | `architecture.md` 21 / `functional-design.md` 18 / `glossary.md` 13 / `research-positioning.md` 7 / `repository-structure.md` 6 / `verification-runbook.md` 5 |

★ 特に `research-positioning.md:661` は **§9 スコープの「やる」側**に
「Lv1 Nudge / **Lv2 Wall** / Lv3・Lv4 Physical Anchor」と書いてある。

### ⚠️ 着手前に決めること（★ 研究者に聞く）

1. ⚠️★★★ **「廃止」の意味は「コードごと削除」か「設計の主軸から外す（コードは残す）」か。**
   ★ `intervention.rs` に 112 件・`Overlay.tsx` に 61 件あるので、**削除なら大手術**になる。
   ★ かつ `logger.rs` / `schema_dto.rs` に出るということは **NDJSON schema に載っている** ＝
   ⚠️ **削ると Phase1 の既存ログが読めなくなる可能性がある**（要確認）
2. ⚠️ **`design-history.md`（39 件）は「歴史の記録」なので書き換えない**のが筋ではないか。
   ★ 履歴は残し、**現行仕様を語る文書（`functional-design` / `architecture` / `research-positioning` §9 /
   `glossary`）だけを直す**、という切り分けが要る
3. ★ **ADR を切るか**。⚠️ Lv2 を落とすのは介入レパートリーの根幹変更なので、
   ★ `intervention-design` Skill と ADR に根拠を残さないと、また同じ質問が起きる

> ⚠️ **`docs/` を機械的に一括置換しない。** 履歴・引用・過去の実測記述まで書き換わる。

## §4 ★ 直前セッション（2026-08-17〜18）で確定したこと

| 決定 | 内容 |
|---|---|
| **D-20** | ★ **ビネットテストは施行せず、事前説明で代える**。⚠️ 事前登録とは矛盾しない（GATE1 は今も「延期」で発効は比較条件実装段） |
| **D-21** | ★ 失う検出能力を **回答分散メトリクス**（`ResponseDispersion`）で代替。⚠️ **閾値は新設していない** |
| **D-10** | ⚠️ 完了ガード（8 問そろわないと不合格）を新設。★ **研究者の採否確認が未了**。外すなら 1 行 |
| ★ 器の扱い | ★ 8 ビネットと `VignetteTest` 画面は **残す**（使わないが削らない）。教示文は **アプリ内のまま** |

★ ⚠️ **教示文の文言を変えたら必ず測り直す**（`tuning-log.md` の手順）。
★ 特に「合否条件を教示文に書く」と被験者が出題構成を推測し始める（D-11・実測済み）。

## §5 ⚠️ 落とし穴（★ 実測）

1. ⚠️★★ **`Cargo.toml` は repo 直下に無い**（`src-tauri/`）。`cd src-tauri` してから叩く
2. ★ ゴールデンは **4 本**。⚠️ 3 本だけ再生成すると `deep_silence` が取り残されて落ちる
3. ⚠️★★ **Windows コンソールは cp932** → Python は `PYTHONUTF8=1` を必ず付ける
4. ⚠️★★ **bash の heredoc は長い日本語で壊れる** → ★ `Write` でファイルにしてから実行する（2026-08-18 に実際に壊れた）
5. ⚠️★★★ **`git push` / `gh pr merge` は deny** —— ★ 研究者に `! <command>` で叩いてもらう
6. ★ CI は **`push: [main, "feature/*"]`** なので、⚠️ **`fix/*` ブランチへの push では CI が走らない**。
   ★ PR を開いて初めて走る
7. ★ schema を変えたら `cd src-tauri && cargo run --bin emit_schema > schema/current.json` →
   `python scripts/check_schema_parity.py --dataset /c/gse-dataset` → ★ **gse-dataset 側にも cp してコミット**

## §6 ★ 直前セッション終了時点の状態（実測）

| 項目 | 値 |
|---|---|
| PR | ★ **#104 マージ済み**（`fix/prereg1-scale-instructions` → `main`・19 ファイル / +3089 −108） |
| CI | ★ **全ジョブ緑**（`check` win-selfhosted 7m35s / mac-selfhosted 7m35s / `frontend-check` 24s / `decide-win-runner` 4s） |
| テスト | ★ `cargo test --workspace` **373 passed / 0 failed** |
| clippy | ★ 警告 **49 件 = 変更前と同数**（新規ゼロ） |
| ゴールデン | ★ 4 本すべて byte-equal（`HMM_VERSION` **bump していない**） |
| `gse-dataset` | ★ `ceb6f03` で schema 同期・push 済み |
| 新設 CI | ★ `frontend-check` に `check_vignettes.py --self-test` → 本検査の 2 ステップ（ubuntu で緑を実測） |
| 凍結値 | ★ `VIGNETTE_PASS_MIN = 6` / `VIGNETTE_COHORT_PASS_FRACTION = 0.80` **不変** |

## §7 ⚠️ 他に残っているもの（★ 本セッションの射程外）

| # | 項目 | 状態 |
|---|---|---|
| 1 | ⚠️ `check_citations.py` が **CI にもフックにも未接続** | ★ `check_vignettes.py` は接続済み。同型の負債が残る |
| 2 | ⚠️ `inferQuadrant` が **Rust / TypeScript で二重実装**・一致を守るテストが無い | ★ 定数は TS 側にも置いたが関数は人力頼み |
| 3 | ⚠️ `npm audit` の既存 HIGH 4 件（vite / postcss / nanoid 他） | ★ **本変更が導入したものではない**（`package.json` 未変更）。ビルド時 dev 依存 |
| 4 | ⚠️ `cargo audit` **未インストール**で Rust 側の依存監査が未実施 | ★ `cargo install cargo-audit` が要る |
| 5 | ⚠️ **プローブ負荷の個人適応** | ★★★ `notes.md` §7 が「次の一手」と名指し。⚠️ `probe_scheduler` は **Phase1 凍結対象**＝完了後 |
| 6 | ⚠️ **PM-Q1〜Q7（表現層）が 700 行の議論のまま承認待ち** | ★ 最も長く塩漬け |
| 7 | ⚠️ **B-a プール倍率の実数**（A-Q3 解除条件①） | ★ 研究者「現時点では分からない」→ 小規模な募集テストが要る |
| 8 | ⚠️ Codex 監査 pass1 / pass2 #3・#4 | ⚠️ **資料はプロンプトに貼る。シェルは起動しない**（`--sandbox read-only` は Windows 1312 で死ぬ） |
