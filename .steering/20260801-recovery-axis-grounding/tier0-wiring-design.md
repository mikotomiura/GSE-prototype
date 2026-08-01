# T2-b: Tier 0 配線の additive schema 設計メモ（★ 設計のみ・コードは書かない）

> ⚠️ **`schema_dto.rs` / `schema/current.json` は凍結対象**（Phase1 完了まで）。
> **本メモはコードを 1 行も変更していない。** 凍結解除後の実装計画である。
> 対象: `docs/architecture/personalization-and-online-learning.md §5.2` の **Tier 0**（新規収集ゼロで効く層）。

---

## 0. 前提の確認（コードを読んで判明した事実）

| 事実 | 出典 | 意味 |
|---|---|---|
| `paste` は `{"type":"paste","t":..,"external_paste_chars":N}` として**別レコードで記録済み** | `logger.rs:406-410` / `schema_dto.rs` `Paste` | **収集は既に動いている**。推論に使われていないだけ |
| `feat` 行は **serde ではなく手書きの `writeln!` フォーマット文字列**で組まれる | `logger.rs:974` | フィールド追加は**フォーマット文字列と DTO の 2 箇所**を同時に触る。精度指定も手で決める必要がある |
| ★ **`f3` は `correction_keys / total_keys` ＝ そのものが `bs_rate`** | `features.rs:146-152` | ★ **`bs_rate` は既に `feat` 行にある**（`f3` として）。§5.2 の Tier 0 表は `bs_rate` を「未配線」としているが**これは誤り** |
| ★ `total_keys` は `features.rs` 内の**ローカル変数として既に計算済み** | `features.rs:146` | `keys` の追加は**新規計算ゼロ**。値を持ち回すだけ |
| `ime_dwell_med` の原資 `ime_shadow` は **Windows のみ・macOS は常時ゼロ** | `schema_dto.rs` `ImeShadow` / `§5.2` / `§11-5` | 欠測が構造的。**Option 必須** |

### ★ 最重要の帰結: Tier 0 の実質的な追加は **`keys` 1 フィールド**である

`f3 = correction_keys / total_keys` である以上、`keys`（= `total_keys`）を 1 つ足せば
**削除打鍵数 = `f3 × keys`**、**挿入打鍵数 = `keys − f3 × keys`** が復元できる。
すなわち `§3.2` の `progress_proxy`（純産出 = 挿入 − 削除）の材料は **`keys` の追加だけで揃う**。

> **schema 変更を最小にできる**。追加フィールドが少ないほど、golden 再生成・parity 検証・
> gse-dataset 側の追随の全てが軽くなる。
>
> ⚠️ **実装時に確認すること**: `f3` の定義が本当に `correction/total` のままか（1 経路しか読んでいない）。
> 丸め（`{:.4}`）済みの `f3` から `correction_keys` を復元すると誤差が乗るため、
> **打鍵数が必要な用途では `keys` と別に `bs_keys`（整数）を持つほうが安全**かもしれない。
> → 下記 案 B を参照。

---

## 1. 追加案

### 案 A（最小）: `keys` のみ追加

```jsonc
{"type":"feat","t":..., "f1":..., "f3":..., ..., "alpha":..., "keys":123}
```

- 追加 1 フィールド（`u64`）。整数なので**精度指定が不要＝ byte-equal の риск が最小**。
- `bs_rate` は `f3` で代用、削除打鍵数は `f3 × keys` で復元。
- ❌ 弱点: 丸め済み `f3` からの復元は整数に戻らない（誤差）。

### 案 B（推奨）: `keys` ＋ `bs_keys` を整数で追加

```jsonc
{"type":"feat", ..., "alpha":..., "keys":123, "bs_keys":7}
```

- 追加 2 フィールド（ともに `u64`）。**両方とも整数**なので浮動小数の再現性問題が無い。
- 純産出 = `keys − bs_keys` が**丸め誤差なしで**得られる。`f3` との冗長性は許容する
  （`f3` は既存の本番経路が使っており、削除も変更もしない）。
- ★ **推奨**。`progress_proxy` は目的変数の材料であり、**そこに丸め誤差を持ち込みたくない**。

### 案 C: `ime_dwell_med` も同時に追加

```jsonc
{"type":"feat", ..., "keys":123, "bs_keys":7, "ime_dwell_med":null}
```

- ⚠️ **今は採らない**。理由:
  - 被験者の 4 割で `ime_shadow` 自体がゼロ（`§5.2`）＝ **`null` の意味が「欠測」か「IME 不使用」か
    区別できない**まま schema に入る。
  - `ime_nav` / `ime_abandon` が macOS で常時ゼロなのが**実装バグか仕様か未確定**（`§11-5`）。
    先に原因を確定させるべきで、確定前に schema へ入れると誤った値が golden に焼き付く。
  - → **`§11-5` の調査を先に済ませてから、別の additive 変更として入れる。**

---

## 2. ★ 「記録する」と「推論に使う」を分離する（凍結契約の核心）

> **Tier 0 配線は `feat` 行に値を書くだけであり、HMM にも X/Y 合成式にも 1 バイトも流さない。**

| 対象 | Tier 0 配線で変わるか |
|---|---|
| `engine.rs` の遷移行列 / 放出行列 / 量子化 | **変わらない** |
| `X = 0.30φ(F3)+0.25φ(F6)+0.25φ(F1)+0.20φ(F5)` / `Y` の合成式 | **変わらない** |
| `p_flow` / `p_inc` / `p_stuck` | **変わらない**（同じ入力・同じ定数） |
| `intervention.rs` の発火 | **変わらない** |
| `HMM_VERSION` | ★ **bump しない**（HMM 挙動が変わらないため） |

- これは ADR-009 Migration P1「**現行 X を置換せず並走**」の実装形である。
- 新フィールドの消費者は**将来の recovery 推定器のみ**。Phase 2b までは誰も読まない。

> ⚠️ **もし Tier 0 の値を X の合成式に入れたくなったら、それは Tier 0 ではなく HMM 変更**である。
> `HMM_VERSION` bump ＋ golden 再生成 ＋ PreReg への影響評価が必要になる。**混ぜないこと。**

---

## 3. 後方互換 — 旧フィクスチャを壊さないための必須条件

`tests/fixtures/*.ndjson` の既存ゴールデンには新フィールドが**存在しない**。
`gse-replay` がそれを読めなくなると回帰テストの背骨が折れる。

- ★ **DTO 側は `Option<u64>` ＋ `#[serde(default)]` にする**（`Paste.external_paste_chars` が
  「旧フィクスチャ互換のため省略可」としている前例と同じ扱い・`schema_dto.rs` のコメント参照）。
- 逆に**書き出し側は常に値を書く**（新規セッションでは `null` にしない）。
- → 「読むときは省略可・書くときは必須」という非対称を**意図的に**採る。

---

## 4. `emit_schema` diff の想定

```bash
cargo run --bin emit_schema   # 出力を src-tauri/schema/current.json と byte-equal 比較
```

**想定される diff（案 B の場合）**:

- `Feat` の `properties` に `keys` / `bs_keys`（`type: ["integer","null"]` 相当）が**追加される**のみ。
- `required` には**入れない**（省略可のため）。
- 既存プロパティの型・順序は**不変**。

→ **additive-only の diff**（ADR-005 の additive 原則に適合）。
**削除・改名・型変更が diff に現れたら設計ミス**なので、その場で止める。

⚠️ **`schema/current.json` の再生成を同じコミットに含める**こと。CI（ローカル代替）の drift 検知は
byte-equal 比較なので、片方だけ更新すると必ず落ちる。

---

## 5. gse-dataset 側の schema parity への影響

- 検証は `scripts/check_schema_parity.py`（`/finish-task` Step 3 の tier-3 workflow guard）。
  `schema_dto.rs` または `schema/current.json` に変更があると**必ず走る**。
- 本変更は両方に触れるため、**parity check が必ず発火する**。
- → **gse-dataset 側の schema を同時に更新する必要がある**。片側だけ進めると
  `/finish-task` が Step 4 へ進まず停止する（それが正しい挙動）。

**作業順序（凍結解除後）**:

1. gse-dataset 側に additive 変更を入れる PR を先に用意する（マージはまだ）
2. 本 repo 側で `schema_dto.rs` / `logger.rs` / `schema/current.json` を変更
3. `check_schema_parity.py` をローカルで走らせて JSON 意味同値を確認
4. 両方を近接したタイミングでマージする

⚠️ **`external_paste_chars` は既に両側の schema にある**ため、paste については parity 影響ゼロ。
今回追加で影響するのは `feat` の新フィールドのみ。

---

## 6. 回帰テストへの影響

| 対象 | 影響 | 対応 |
|---|---|---|
| `gse-replay --snapshot` の byte-equal 比較 | ★ **`FeatSnapshot` 列に新フィールドが出るなら golden 再生成が必要** | 再生成し、**差分が新フィールドの追加のみである**ことを目視 ＋ 差分レビューで確認して `.steering/` に記録 |
| `cargo test --workspace` | `logger.rs` のフォーマット文字列テスト（`format_paste_line` 等と同型のもの）が落ちる | 期待文字列を更新。**新フィールドの位置と精度を固定する** |
| `HMM_VERSION` | **bump しない**（§2） | — |

> ★ **golden 再生成の差分が「新フィールドの追加のみ」でないなら、どこかで推論に混入している。**
> §2 の分離が破れている証拠なので、その場で止めて原因を突き止めること。
> **これが Tier 0 配線の最重要の受け入れ条件である。**

---

## 7. 受け入れ条件（凍結解除後の実装タスクへ引き渡す）

- [ ] `emit_schema` の diff が **additive-only**（追加のみ・型変更なし・required 追加なし）
- [ ] 旧フィクスチャ（新フィールドなし）を `gse-replay` が読める
- [ ] golden 再生成の差分が **新フィールドの追加のみ**（`p_*` / `raw_*` / `ewma_*` / `obs` が動いていない）
- [ ] `HMM_VERSION` が変わっていない
- [ ] `check_schema_parity.py` が pass（gse-dataset 側と同時更新済み）
- [ ] `cargo test --workspace` が緑
- [ ] 新フィールドを読む本番コードが**まだ存在しない**こと（記録のみ・§2）

---

## 8. 未解決 / 実装時に判断すること

1. ★ `f3` の定義が `correction_keys / total_keys` のままか（**1 経路しか読んでいない**）。
   異なれば案 A/B の前提が崩れる。
2. `FeatSnapshot`（`gse-replay --snapshot` の出力列）に新フィールドを**含めるか**。
   含めなければ golden 再生成が不要になるが、**リプレイから recovery ラベルを作れなくなる**。
   → おそらく含める必要があるが、`gse-replay` の出力仕様を読んでから決める。
3. Tier 1（沈黙長の分布 p50/p90/max・burst 長の分布）は **`feat` 行に足すか、別レコードにするか**。
   `feat` は 1Hz で出るため、分布統計を毎秒書くと**ログ量が増える**。別レコード（低頻度）が妥当かもしれない。
   → 本メモの範囲外（Tier 1）。G1 の FS-B には必要なので、G1 実施前に決める必要がある。
4. 期の幅 Δ（`§11-7`）が決まると、Tier 1 の分布統計を**どの窓で取るか**が決まる。順序としては Δ が先。
