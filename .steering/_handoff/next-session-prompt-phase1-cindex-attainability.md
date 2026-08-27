# 次セッション開始プロンプト — **Phase1 C-index の到達可能性診断を実装する**

> ★ このファイルの「===」以下をコピペして開始する。
> ★ モデル: **Sonnet**（★ 実装タスク。★ ただし `§3` の論証だけは慎重に書くこと）。
> ⚠️ 前セッションから `/clear` して**新セッション**で始めること。
> ★ **コードのみ。凍結文書は 1 バイトも触らない。**

---

===

## §0 ⚠️★★★ 最初に固定すること

### 0-1. ★ これは「実装タスク」である

★ 出るべきものは:

1. `src-tauri/src/analysis/calibration_eval.rs` と `cohort.rs` への**コード変更**
2. **テスト**（★ 既存は `calibration_eval.rs` 34 本 / `cohort.rs` 20 本。ここに足す）
3. `.steering/[YYYYMMDD]-phase1-cindex-attainability/` の作業記録
4. ★ **凍結文書への影響の起票**（`§5`）——⚠️ **凍結文書そのものは書き換えない**

### 0-2. ⚠️★★★ **なぜこれをやるのか**（★ 2026-08-27 のサーヴェイ第 2 ラウンドの帰結）

★ G1（統制タスク実験）の判定が `MANIPULATION_CHECK_FAILED` で止まった件を文献で詰めた結果、
**「ゲートが到達不能な水準を要求していた」**ことが分かった
（`docs/literature/20260827-manipulation-check-attainability-and-task-complexity.md` カード 2）。

★ **G1 は `§5.2` で到達可能性をラベル非依存の診断値として必ず報告している**:
`attainable_min_p_for_this_subject` / `test_can_reject_at_all`。
⚠️ **Phase1 の C-index には、ゲート指標に対応する診断がまだ無い。**

### 0-3. ⚠️ 1 バイトも変えないもの

- ⚠️ **`docs/preregistration-v0.3.md`**（Phase1 の凍結された合否契約）—— ★ 影響は `.steering/` に記録
- ⚠️ **`experiments/20260731-phase1-calibration-analysis/`** の既存成果物（★ 再実行しない・`§9`）
- ⚠️ **G1 側**（`experiments/20260801-controlled-friction-task/`）—— ★ 別トラック
- ⚠️ **判定の閾値**（`>0.55` / `≥0.65` / `≥20件/人`）—— ★ **1 つも動かさない**

---

## §1 ⚠️★★★ **既に実装済みのものを二重に作らないこと**（★ 本節が最重要）

★ 前セッションが**コードを読んで確認済み**である。⚠️ **以下は既にある。作り直さない。**

| 既にあるもの | 場所 | 中身 |
|---|---|---|
| ★ `AxisDispersion` | `calibration_eval.rs:652` | `n` / `distinct_values` / `modal_value` / `modal_share` / **`comparable_pairs`** / **`degenerate`** |
| ★ `ResponseDispersion`（q1 / q2） | `calibration_eval.rs:677` | 上を 2 軸ぶん |
| ★ `CalibrationReport.dispersion` | `calibration_eval.rs:765` | ⚠️ **配線済み**（出力 JSON に出る） |
| ★ `axis_dispersion()` | `calibration_eval.rs:683` | `C(n,2) − Σ C(count_v, 2)` で比較可能ペアを数える実装 |
| ★ forking paths にならない論証 | `calibration_eval.rs:667-670` の doc コメント | ★ **これをそのまま踏襲する**（`§3`） |

⚠️★★ **`experiments/20260731-phase1-calibration-analysis/results/*.json` に `dispersion` が無いのは、
その JSON が 2026-07-31 生成でコード追加より前だからである**（`provenance.json` の `repo_commit=232d412`）。
★ **「未実装」と誤読しないこと。**

⚠️ かつ **`SubjectCindex` / `CalibrationReport` は `schema_dto.rs` の対象外**である
（★ あちらは NDJSON セッションスキーマ）。→ ★ **`emit_schema` の drift check は本タスクに無関係。**

---

## §2 ★★★ **実際の欠落 — ゲート指標の到達可能性**

### 2-1. ゲートに使われるのは `pooled` ではなく `session_median` である

★ `cohort.rs:17-19` の逐語:

> ゲート駆動は PreReg-4 文言「各人の C-index **中央値**」に従い `x_q1_session_median`。
> `x_q1_pooled` は頑健性参考値として併記するが**ゲートには使わない**（forking paths 排除）

### 2-2. ⚠️★★★ **その `session_median` は、各セッションの比較可能ペア数を捨てて作られている**

★ `calibration_eval.rs:949-969` の実装:

```rust
let per_session_x_q1: Vec<f64> = eval
    .iter()
    .filter_map(|s| { ...; concordance_index(&pairs_x_q1(&obs)) })
    .collect();
// → SubjectCindex { x_q1_session_median: median_f64(&per_session_x_q1), ... }
```

⚠️ `concordance_index()`（`calibration_eval.rs:320`）は**内部で `comparable` を数えているのに捨てている**:

```rust
pub fn concordance_index(pairs: &[(f64, u8)]) -> Option<f64> {
    let mut comparable: u64 = 0;
    ...
    if comparable == 0 { None } else { Some(concordant / comparable as f64) }
}
```

→ ★★★ **比較可能ペアが 1 件のセッションの C-index が、100 件のセッションと同じ重みで中央値に入る。**

### 2-3. ★ 実測でそれが起きている（★ 既存 `results/` から前セッションが復元した）

| 被験者・カット | 報告値 | = 既約分数 | **実際の比較可能ペア** |
|---|---|---|---|
| P013 感度 `x_q1_pooled` | **0.0** | 0/1 | **1** |
| P013 主 `y_q2_pooled` | 0.167 | 1/6 | **6** |
| P014 感度 `x_q1_pooled` | 0.381 | 8/21 | 21 |
| P011 主 `x_q1_pooled` | 0.365 | 19/52 | 52 |
| P010 主 `x_q1_pooled` | 0.512 | 362/707 | 707 |

★ かつ **P011 の `y_q2_session_median = 1.0`** —— ⚠️ **これはほぼ確実に極小ペアのセッション由来である。**
★ **本タスクの実装が入れば、それが数値で見えるようになる。**

### 2-4. ★★★ 作るもの

⚠️ **閾値は 1 つも新設しない。** ★ 出すのは**算術的事実**だけである。

1. ★ **`concordance_index()` が比較可能ペア数も返せるようにする。**
   ⚠️ **既存シグネチャを壊さない**（呼び出し元が複数ある）。
   → ★ `concordance_index_detailed(pairs) -> Option<(f64, u64)>` を新設し、
   既存 `concordance_index()` はその薄いラッパにするのが安全。
2. ★ **per-session の比較可能ペア数を `SubjectCindex` に載せる。** 案:
   - `x_q1_session_comparable_pairs: Vec<usize>`（★ セッション順・`None` のセッションは含めない）
   - `y_q2_session_comparable_pairs: Vec<usize>`
   - ★ **中央値に使ったセッションと同じ集合・同じ順序であること**（★ ここがずれると意味が消える）
3. ★ **ゲート閾値の *到達可能性* を算術的事実として出す。**
   ★ C-index は `(concordant + 0.5·tie) / comparable` なので、**取りうる値は `0.5/k` 刻み**である。
   → `x_q1_session_min_comparable_pairs: Option<usize>`（★ 中央値に寄与したセッションの最小ペア数）
   → `x_q1_session_median_comparable_pairs: Option<usize>`
   → `x_q1_gate_attainable: Option<bool>`（★ **`§3` で「出してよい」と解決済み**。
   ⚠️ **`CINDEX_GO_ALL_MIN` / `CINDEX_GO_MEDIAN` を参照し、数値を直書きしないこと**）。
4. ★ **`cohort.rs` の read-model に通す。**
   ⚠️ `SubjectCalibrationView`（**`cohort.rs:156`**）は**必要フィールドだけを宣言した部分ビュー**である。
   → ★ 足したフィールドを cohort 側でも使うなら、**この read-model にも宣言を足す**。
   ★ `cohort.rs:131` に「回答分散 (D 側の `ResponseDispersion` の部分ビュー)」の先例がある。**それに倣う。**
5. ★ **cohort のレポートに「ゲート母数の各被験者が、どれだけのペア数の上に立っているか」を出す。**
   ⚠️ ★ **母数から除外する規則は追加しない**（★ それは凍結された判定基準の変更になる）。**併記するだけ。**

---

## §3 ⚠️★★★ **forking paths にならないことの論証（★ 必ず書く）**

★ **先例がコード内にある。** `calibration_eval.rs:667-670` の doc コメント逐語:

> ⚠️ **順序 C-index が原理的に計算できない** (`distinct_values <= 1`)。
> これは判断を含む閾値ではなく**算術的事実**である
> (比較可能ペアが 0 なら concordance は定義されない)。
> **事前登録の閾値を新設していないので forking paths にあたらない。**

★ **同じ論法が本タスクにも使える。** ⚠️ **ただし成立させるには次を守ること**:

| 条件 | なぜ |
|---|---|
| ★ **閾値を 1 つも新設しない** | 新設した瞬間に「新しい合否経路」になる |
| ★ **判定母数を変えない** | 除外規則の追加は判定基準の変更である |
| ★ **合格経路を 1 本も増やさない** | ⚠️ G1 `§5.3` の「これが判定基準の変更でない理由」と同じ検査 |
| ★ **出すのは算術的事実のみ**（ペア数・粒度） | 解釈は人間がやる |

### ★★ 「到達可能性の bool を出してよいか」は **解決済み**（★ 前セッションがコードで確認した）

⚠️ 当初「閾値 `0.55` をコードに焼き込むことになるのでは」と懸念したが、
★ **`0.55` / `0.65` は既にコード内の定数である**。逐語（`calibration_eval.rs:474-476`）:

```rust
pub const CINDEX_GO_MEDIAN: f64 = 0.65;
pub const CINDEX_GO_ALL_MIN: f64 = 0.55;
pub const CINDEX_KILL_MEDIAN: f64 = 0.55;
```

→ ★ **これらを参照して到達可能性を出しても、新しい閾値の導入にはならない。**
★ **`x_q1_gate_attainable: Option<bool>` を出してよい**（★ 上の定数を参照すること。**数値を直書きしない**）。

⚠️ ★ **ただし `decisions.md` に「なぜ forking paths にならないか」を自分の言葉で必ず書くこと。**
★ 上の定数の存在は必要条件であって十分条件ではない —— **判定母数を変えず・合格経路を増やさない**ことも要る。

---

## §4 ★★ 検証

⚠️★★★ **`Cargo.toml` は repo 直下に無い（`src-tauri/` にある）。**

```bash
cd src-tauri     # ★ 以下は src-tauri/ から実行する

# 単体テスト（★ 既存 54 本が緑のままであること）
cargo test --workspace

# 回帰検証（★ FeatSnapshot の byte-equal。本タスクは触らないはずだが必ず走らせる）
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json
```

★ **足すテストの観点**（⚠️ 既存 34 本の流儀に合わせる）:

1. ★ **比較可能ペアが 1 件のセッション**で C-index が 0.0 / 1.0 になり、ペア数が **1** と報告されること
2. ★ **比較可能ペアが 0 件**（straight-lining）のセッションが `None` になり、**中央値の母数から外れる**こと
   —— ⚠️ **かつ `comparable_pairs` の `Vec` にも入らないこと**（★ 中央値の集合と一致させる）
3. ★ **既存の `x_q1_session_median` の値が 1 ビットも変わらないこと**（★ 回帰）
4. ★ `concordance_index()` と `concordance_index_detailed()` の**第 1 要素が常に一致**すること

⚠️ **`HMM_VERSION` は bump しない。** ★ 本タスクは **HMM の挙動を 1 つも変えない**（診断値を足すだけ）。
★ ただし **`cargo run --bin gse-replay -- ... --snapshot` が byte-equal で通ることを実測して確認**すること
（★ 「変えていないはず」で済ませない）。

⚠️ **`emit_schema` の drift check は本タスクに無関係**（`§1` 末尾）。★ 走らせても構わないが、
差分が出たら **それは別の原因**なので調べること。

---

## §5 ★★ 起票するもの（⚠️ **凍結文書は書き換えない**）

★ `.steering/[YYYYMMDD]-phase1-cindex-attainability/decisions.md` に、**次の改訂の議題**として書く:

| # | 議題 | 出所 |
|---|---|---|
| **1** | ⚠️★★★ **`PreReg-4` の「十分なデータがある全員で >0.55」は `all()` 型のコホートゲートである** | 2026-08-27 カード 2 |
| | ★ 被験者 5 名・1 人あたり通過率 0.8 なら **コホート通過率 0.328**、0.7 なら **0.168**。 | |
| | ★ **コード上でも見える**（`calibration_eval.rs:521` 逐語）: `let all_above = subject_cindices.iter().all(|&c| c > CINDEX_GO_ALL_MIN);` | |
| | ⚠️ **被験者を増やすほど通りにくくなる**（G1 の `analyze.py` の `all(m["passed"])` と同じ構造）。 | |
| **2** | ★ **Kill 条件に *計器側の枝* を足す**——比較可能ペアが極小の被験者を `Kill` でなく `InstrumentInsufficient` として扱えるか | [V90] Fayant 逐語「a failed MC could be attributed to **measurement problems**」 |
| **3** | ★ `notes.md` の「X→Q1 は 5 名全員で 0.52 以下」に**ペア数を併記**する（★ P013 感度は **1 ペア**由来） | 2026-08-28 の実測 |

⚠️ ★ **1 と 2 は研究者判断である。** ★ **こちらで決めない。議題として書くだけ。**

---

## §6 ★ 読むもの（★ ゼロから考えない）

| 何 | なぜ |
|---|---|
| ⚠️★★★ `src-tauri/src/analysis/calibration_eval.rs` の **313-340 / 470-530 / 565-580 / 650-720 / 940-985** | ★ **既にある物と、無い物の境界**。`§1` `§2` `§3` の根拠 |
| ⚠️★★ `src-tauri/src/analysis/cohort.rs` の **8-30 / 125-200** | ★ ゲートが `session_median` を使うことの逐語と、read-model（`156`）の作り |
| `docs/literature/20260827-manipulation-check-attainability-and-task-complexity.md` **カード 2 / カード 7** | ★ **なぜ到達可能性を出すのか**の一次的な理由 |
| `experiments/20260801-controlled-friction-task/preregistration.md` **§5.2** | ★ **G1 側の先例**（到達可能性の報告義務・「事後の自由度にならない」論証） |
| `experiments/20260731-phase1-calibration-analysis/notes.md` **§3 / §4** | ★ 実測の straight-lining と C-index 算出不能の記録 |
| `docs/preregistration-v0.3.md` **PreReg-2 / PreReg-4 / PreReg-5** | ★ 触ってはいけない閾値の確認 |
| Skill: `rust-standards` / `architecture-rules` / `verify-before-claiming` | ⚠️ `analysis/` は **OS 非依存**（OS API を呼ばない）・`anyhow` / `tracing` |

---

## §7 ⚠️ 落とし穴

1. ⚠️★★★ **既にある物を作り直す。** ★ `AxisDispersion` の `comparable_pairs` は
   **生の Q1/Q2 分布に対するもの**で、本タスクが要るのは **評価セッションごとの C-index に対するもの**である。
   ★ **似ているが別物。** ⚠️ **`dispersion` を拡張して済ませようとしないこと**（母数が違う: `main` 全体 vs 評価セッション）。
2. ⚠️★★ **`x_q1_pooled` を触ってしまう。** ★ **ゲートは `session_median`** である（`§2-1`）。
   ★ pooled にも足してよいが、**優先は session 側**。
3. ⚠️★★ **中央値の母数とペア数の `Vec` がずれる。** ★ `filter_map` で `None` を落としているので、
   **同じ `filter_map` の中で両方を集める**こと。⚠️ 2 回ループを回すと順序と件数がずれる。
4. ⚠️★ **閾値を新設してしまう。** `§3` を読んでから決める。★ **迷ったら出さない。**
5. ⚠️★ **既存 `results/*.json` を再生成しようとする。** ★ **本タスクの範囲外**（`§9`）。
   ⚠️ 再生成には `~/gse-dataset` の実データが要り、`provenance.json` の来歴が変わる。
6. ⚠️★ **`HMM_VERSION` を bump してしまう。** ★ 挙動を変えていないので **bump 不要**。
   ⚠️ ただし **replay の byte-equal を実測で確認する**こと（`§4`）。
7. ⚠️ **`cargo test` を repo 直下で叩く** → `could not find 'Cargo.toml'` で空振りする。★ `cd src-tauri`。

---

## §8 ★ 進め方

1. ★ **`/start-task`** で `.steering/[YYYYMMDD]-phase1-cindex-attainability/` を作る
2. ★ `§6` の**コードを先に読む**（⚠️ 特に `§1` の「既にある物」）
3. ★ `§3` の論証（**なぜ forking paths にならないか**）を**自分の言葉で** `decisions.md` に書く
   （⚠️ bool を出してよいことは解決済み。★ 論証だけは省略しない）
4. ★ **テストを先に書く**（`§4` の 4 観点）→ 実装 → 緑
5. ★ `cargo test --workspace` ＋ **replay の byte-equal** を実測
6. ★ `§5` の議題を `decisions.md` に起票
7. ★ `/finish-task`（⚠️ **Step 3 の `/cross-review` を飛ばさない**。
   ★ `main` へマージしないなら **Step 5 の CI 発火確認は N/A** と明記する）

---

## §9 ⚠️ 本セッションで扱わないもの

- ⚠️ **`docs/preregistration-v0.3.md` の改訂**（★ 研究者の行為・`§5` で起票するだけ）
- ⚠️ **`experiments/20260731-phase1-calibration-analysis/` の再実行**（★ 別タスク・実データが要る）
- ⚠️ **G1 側の `§2.6` / `analyze.py` の修正**（★ 別トラック。
  `experiments/20260801-controlled-friction-task/notes.md §15-5` に起票済み）
- ⚠️ **`analyze.py --unseal`**（★ G1 側・絶対に押さない）
- ⚠️ **`replay.rs` の flaky test**（★ `.steering/20260825-replay-flaky-test/`）
- ⚠️ **判定閾値の変更**（`>0.55` / `≥0.65` / `≥20件/人` を 1 つも動かさない）

---

## §10 ⚠️ git の前提

★ **2026-08-28 時点で `docs/g1-verdict-and-friction-survey` ブランチが `origin` に未 push** であり、
`origin/main` より **28 コミット遅れ / 6 先行**である。
⚠️ ★ **研究者がまだ push / rebase していない可能性が高い。** ★ 着手前に `git rev-list --left-right --count origin/main...HEAD` で実測すること。

⚠️★★★ **ブランチを切る前に必ず `git fetch`**（★ 古い `main` から切らない）。
★ 本タスクのブランチは `feat/phase1-cindex-attainability` を使う。

⚠️★★ **`origin/main` は急速に進んでいる**（★ 2026-08-28 の 1 セッション中に 14 → 28 へ増えた＝
G-GEAR 側の O1 トラックが push している）。★ 2026-08-28 時点の実測では:

- ✅ `docs/references.md` / `docs/literature/` は **origin/main 側が 1 行も触っていない**（採番の衝突なし）
- ⚠️ **交差するのは `.codex/budget.json` のみ**（★ `/cross-review` の使用量記録）——
  ★ rebase で衝突したら**両方の `history` を残してマージする**（★ どちらかを捨てない）

★ 本タスクが触るのは `src-tauri/src/analysis/` なので、⚠️ **O1 トラックが `src-tauri/` を触っていないか**を
着手前に確認すること: `git diff --name-only $(git merge-base HEAD origin/main) origin/main -- src-tauri/`

⚠️ **`git push` / `git rebase` は dev から環境ゲートで拒否される。** ★ 研究者に渡す形で出すこと:

```bash
! git fetch origin && git rebase origin/main && git push -u origin feat/phase1-cindex-attainability
```
