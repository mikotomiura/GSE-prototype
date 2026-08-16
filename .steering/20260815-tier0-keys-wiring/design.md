# 設計 — Tier 0 配線（`keys` / `bs_keys`）

> ★ 原本は `.steering/20260801-recovery-axis-grounding/tier0-wiring-design.md`（181 行）。本書はその**差分と補正**を書く。
>
> ★★★ **2026-08-16 に実装完了。** 以下は計画として書かれたものだが、
> **§「実装で計画から外れたこと」（末尾）に実測との差分を追記してある**。
> ★ 実装中に出た判断は `decisions.md` の判断 5/6/7 ＋ 実測 3、
> ★ ゴールデン再生成の検証は `golden-regeneration.md` を参照。

## 実装アプローチ

★ **案 B を採る**（原本 §1 の推奨どおり）: **`keys` と `bs_keys` を「ともに整数（`u64`）」で追加する。**

| 案 | 追加 | 判定 |
|---|---|---|
| A | `keys` のみ | ❌ ⚠️ 丸め済み `f3`（`{:.4}`）から `correction_keys` を復元すると**整数に戻らない** |
| ★ **B** | `keys` ＋ `bs_keys` | ★ **採用**。★ 純産出 `= keys − bs_keys` が**丸め誤差なしで**得られる。`f3` との冗長性は許容（`f3` は既存の本番経路が使用中・**削除も変更もしない**） |
| C | ＋ `ime_dwell_med` | ⚠️ **今は採らない**。★ 被験者の 4 割で `ime_shadow` がゼロで **`null` が「欠測」か「IME 不使用」か区別できない**／`ime_nav`・`ime_abandon` の macOS 常時ゼロが**実装バグか仕様か未確定**（§11-5）。★ 確定前に schema へ入れると**誤った値が golden に焼き付く** |

### ★ 核心の契約（★ これが破れたら止める）

> **Tier 0 配線は `feat` 行に値を書くだけであり、HMM にも X/Y 合成式にも 1 バイトも流さない。**

| 対象 | Tier 0 配線で変わるか |
|---|---|
| `engine.rs` の遷移行列 / 放出行列 / 量子化 | **変わらない** |
| `X = 0.30φ(F3)+0.25φ(F6)+0.25φ(F1)+0.20φ(F5)` / `Y` | **変わらない** |
| `p_flow` / `p_inc` / `p_stuck` | **変わらない**（同じ入力・同じ定数） |
| `intervention.rs` の発火 | **変わらない** |
| `HMM_VERSION` | ★ **bump しない** |

★ これは **ADR-009 Migration P1「現行 X を置換せず並走」の実装形**である。

## 変更対象

### 修正するファイル（★ 本セッションで行番号を実測済み）

| ファイル | 何を変えるか | ★ 実測 |
|---|---|---|
| `src-tauri/src/analysis/features.rs` | `total_keys` / `correction_keys` を `FeatSnapshot` まで持ち回す | ★ **`:146` `let total_keys = press_events.len();` ／ `:149` `correction_keys` ／ `:151-152` `f3 = correction_keys as f64 / total_keys as f64`** — ★ **両方ローカル変数として既に計算済み＝新規計算ゼロ** |
| `src-tauri/src/analysis/loop_step.rs` | `FeatSnapshot` に `keys` / `bs_keys` を追加 | ★ **`:134` `pub struct FeatSnapshot`**（★ `Serialize`/`Deserialize`/`PartialEq` 付き） |
| `src-tauri/src/logger.rs` | `feat` 行のフォーマット文字列に 2 フィールド追加 | ⚠️ ★ **`:1214` の手書き `writeln!` フォーマット文字列**（原本 memo の `:974` は**古い**。★ 行番号がずれている） |
| `src-tauri/src/schema_dto.rs` | `Feat` DTO に `Option<u64>` ＋ `#[serde(default)]` | ⚠️ **凍結対象だったファイル**（★ 研究者承認済・D1） |
| `src-tauri/schema/current.json` | `emit_schema` で再生成 | ★ **同じコミットに含める**（★ 片方だけだと byte-equal drift 検知が必ず落ちる） |
| `src-tauri/tests/snapshots/*.json` | ★ **golden 4 本を再生成** | ★ `minimal` / `phase1_ime_heavy` / `category_coverage` / **`deep_silence`** |
| `C:\gse-dataset/schema/current.json` | additive 変更を反映 | ★ D2（研究者判断） |
| `docs/architecture/personalization-and-online-learning.md` §10 | 順序記述を改訂 | ★ D1（研究者判断） |

### 新規作成するファイル
- ★ **なし**（★ 既存ファイルへの additive 変更のみ）

### 削除するファイル
- ★ **なし**

## 影響範囲

### ⚠️★★★ B-1: 既存の schema parity drift を先に解消する（★ 原本 memo に無い項目）

★ 本セッションの実測:

```
$ python scripts/check_schema_parity.py --dataset C:/gse-dataset
[check_schema_parity] DRIFT detected
Missing variants in B: hook_health
（＋ meta variant の g1_mode プロパティが B 側に無い）
REAL EXIT=1
```

★ `check_schema_parity.py` は**意味的比較**（★ 改行コードとキー順は無視する）なので、
⚠️ **これは CRLF 起因ではなく本物の drift である。**

**★ 作業順序（★ 原本 §5 を B-1 で補正した版）**:

1. ★★★ **先に `hook_health` variant と `meta.g1_mode` を gse-dataset 側へ反映し、`exit 0` に戻す**
   （★ **本タスクの変更を入れる前に**。⚠️ **そうしないと「今回壊したのか元から壊れていたのか」が分離できない**）
2. gse-dataset 側に **本タスクの** additive 変更を用意する（マージはまだ）
3. 本 repo 側で `schema_dto.rs` / `logger.rs` / `loop_step.rs` / `features.rs` / `schema/current.json` を変更
4. `check_schema_parity.py` をローカルで走らせて意味同値を確認
5. 両方を近接したタイミングでマージする

⚠️ **`external_paste_chars` は既に両側の schema にあるため paste については parity 影響ゼロ。**

### B-2: 後方互換（★ 旧フィクスチャを壊さない）

- ★ **DTO 側は `Option<u64>` ＋ `#[serde(default)]`**（★ `Paste.external_paste_chars` の前例と同じ扱い）
- ★ **書き出し側は常に値を書く**（新規セッションでは `null` にしない）
- → ★ 「**読むときは省略可・書くときは必須**」という非対称を**意図的に**採る

### B-3: `FeatSnapshot` に含めるか（★ 原本 §8-2 の未決を本セッションで閉じた）

★ **含める。** 根拠:

- ★ 一次（`loop_step.rs:133` doc コメント逐語）: **「ゴールデンスナップショット (P0-10) の byte-equal 比較対象」**
- ★ 含めないと **replay から `progress_proxy`（= `keys − bs_keys`）を再構成できない**
  → ⚠️★★★ **Replay-as-Truth が切れる**（★ NDJSON にしかない値ができてしまう）
- **代償**: ★ **golden 4 本の再生成が必要**（★ 受け入れ条件で「差分が新フィールドの追加のみ」を強制する）

## 既存パターンとの整合性

| 規約 | 従い方 |
|---|---|
| **ADR-005**（additive versioning） | ★ 追加のみ・型変更なし・`required` に入れない |
| **Replay-as-Truth** | ★ golden 再生成の差分を目視 ＋ 差分レビューし `.steering/` に記録 |
| `Paste.external_paste_chars` の前例 | ★ `Option` ＋ `#[serde(default)]` で旧フィクスチャ互換 |
| `data-privacy` | ★ **`keys` / `bs_keys` は打鍵の「数」のみ**。★ 文字内容・VK 生値を含まない |
| `rust-standards` | ★ `tracing` のみ・`anyhow::Result`・`winapi` 不使用（★ 本変更は OS API に触れない） |
| `architecture-rules` | ★ `analysis/` に OS API を持ち込まない（★ 本変更は `analysis/` 内で完結し OS 非依存） |

## テスト戦略

| 層 | 何をテストするか |
|---|---|
| **単体** | ★ `logger.rs` のフォーマット文字列テスト（`format_paste_line` と同型）に **新フィールドの位置と精度を固定**した期待文字列を追加 |
| **単体** | ★ `features.rs` で `keys` / `bs_keys` が `total_keys` / `correction_keys` と一致すること（★ `f3 × keys ≈ bs_keys` の整合） |
| **後方互換** | ★ **新フィールドを持たない旧 NDJSON** を `gse-replay` が読めること |
| **回帰（背骨）** | ★★★ `gse-replay --snapshot` を golden 4 本で走らせ、**差分が新フィールドの追加のみ**であること |
| **schema** | ★ `emit_schema` の出力が `schema/current.json` と byte-equal ／ `check_schema_parity.py` が exit 0 |
| E2E | ★ **不要**（★ UI・介入経路に触れない） |

> ★★★ **最重要の受け入れ条件**: golden 再生成の差分に `p_*` / `raw_*` / `ewma_*` / `obs` が現れたら、
> **どこかで推論に混入している**。★ 契約が破れた証拠なので**その場で止めて原因を突き止める**。

## ロールバック計画

- ★ **1 コミットに閉じる**（`schema_dto.rs` ＋ `logger.rs` ＋ `loop_step.rs` ＋ `features.rs` ＋ `schema/current.json` ＋ golden 4 本）。
  → ★ `git revert` 1 回で戻る。
- ★ **`HMM_VERSION` を bump しないので、revert 後に golden の再々生成が要らない。**
- ⚠️ **gse-dataset 側は別 repo なので、revert する場合は両側を戻す**（★ 片側だけ戻すと parity が落ちる）。
- ⚠️ **既に配布済みのビルドで収集された NDJSON には新フィールドが入る**が、
  ★ DTO が `Option` なので**古いビルドの `gse-replay` でも読める**（★ 前方互換も成り立つ）。

## ⚠️ 実装時に確認すること（★ 原本 §8 ＋ 本セッションの追加）

1. ★ **`f3` の定義**が `correction_keys / total_keys` のままか
   → ★ **本セッションで一次確認済み**（`features.rs:146-152`）。⚠️ ただし**読んだのは 1 経路のみ**。
2. ★ `FeatSnapshot` に含めるか → ★ **本セッションで決着（B-3・含める）**。
3. ⚠️ Tier 1（沈黙長・burst 長の分布）を `feat` に足すか別レコードか → ★ **本タスクのスコープ外**。
   ⚠️ **ただし G1 の FS-B には必要**（原本 §8-3）なので、★ **G1 の残り 2 名を回す前に決める必要がある**。
4. ⚠️ 期の幅 Δ（§11-7）が決まると Tier 1 の窓が決まる → ★ **順序としては Δ が先**。
5. ★ **`logger.rs` の行番号がずれている**（memo `:974` → 実測 `:1214`）。★ 他の参照も同様にずれている前提で読むこと。

---

## ★★★ 実装で計画から外れたこと（2026-08-16・実測）

| # | 計画 | ★ 実際 | 記録 |
|---|---|---|---|
| 1 | 変更対象は 8 ファイル | ⚠️ **11 ファイル**。★ 計画に無かった 3 つ: **`src/bin/replay.rs`**（`LoggedFeatDto` の同期。★ 当該ファイル自身の doc コメントが「`LogEntry::Feat` に新フィールドが追加されたら schema_dto.rs と本 DTO の両方を更新する」と要求していた）／**`src/lib.rs`**（`FeatSnapshot` → `LogEntry::Feat` の変換）／**テストヘルパ 3 か所**（`calibration_eval.rs` / `intervention_eval.rs` / `metrics.rs` の `FeatSnapshot` リテラル） | — |
| 2 | `logger.rs` は「フォーマット文字列に 2 フィールド追加」 | ★ **`format_feat_line()` を純粋関数として抽出**した。★ 理由: テスト戦略が要求する「フォーマット文字列テスト（`format_paste_line` と同型）」は、**インラインの `writeln!` のままでは書けない**。★ 抽出は振る舞いを変えない（★ ゴールデン 4 本と `cargo test` で担保） | — |
| 3 | 「`features.rs` から `FeatSnapshot` まで持ち回す」 | ⚠️ ★ **SilencePath では持ち回せない**（★ 合成観測が打鍵を数えていないため）。→ ★ **実測値を退避して経路に依らず書く**方式に変えた | `decisions.md` 判断 5 |
| 4 | `FeatSnapshot` にも `#[serde(default)]` を付ける想定（原本 §3 の読み方） | ★ **付けない**ことにした（★ golden を全部再生成するので互換不要／欠けた golden を 0 で黙って受けるほうが危険） | `decisions.md` 判断 6 |
| 5 | 旧 NDJSON 互換は「DTO を `Option`」で足りる | ⚠️ ★ **`--metrics` 経路の `LoggedFeatDto` という第 3 の DTO があった**。★ 欠測を `0` に倒したが、**「旧ログの欠測」と「実測 0 打」が区別できない**という妥協が残る | `decisions.md` 判断 7（★ **T0-Q5 として次に渡す**） |

### ★ 実測した検証結果（★ 受け入れ条件との対応）

| 受け入れ条件 | ★ 実測 |
|---|---|
| `emit_schema` の diff が additive-only | ★ **feat variant に 2 プロパティ追加のみ**。`required` 変更なし・既存プロパティの型変更なし・variant の増減なし（★ JSON 意味比較で機械判定） |
| 旧フィクスチャを `gse-replay` が読める | ★ golden 4 本の fixture がそのまま通る ＋ 旧 `feat` 行の後方互換テストを追加 |
| ★★★ golden の差分が新フィールドの追加のみ | ★ **4 本 155 行すべてで「追加キー = {keys, bs_keys} ちょうど・削除ゼロ・既存値は `repr()` 一致」** |
| `HMM_VERSION` が変わっていない | ★ `0.3.0` のまま（★ `engine.rs` は 1 行も変更なし） |
| `check_schema_parity.py` が exit 0 | ★ exit 0（20750 bytes canonical） |
| `cargo test --workspace` が緑 | ★ **354 + 25 + 1 passed / 0 failed** |
| 新フィールドを読む本番コードが無い | ★ grep 実測: 読み取りは**テストと `loop_step.rs` の記録用退避のみ** |
| `.age` / NDJSON / 実セッション名が repo に入っていない | ★ `security-checker` で確認 |
| `code-reviewer` + `security-checker` 並列レビュー | ★ 実施 |
