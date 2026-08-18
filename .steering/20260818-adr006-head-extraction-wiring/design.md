# 設計 — ADR-006 Phase 2a/2b

## 0. 確定用語（揮発防止・`docs/glossary.md` へは各コミットで反映）

| 用語 | 定義 |
|---|---|
| **Writing head** | 論述・文章作成ドメインの推論ヘッド。β を 2 セット所有する: `β_writing`（IME on）と `β_writing_latin`（IME off）。`ime_open` は **within-writing 信号**として head 内部でのみ使う |
| **`β_writing_latin`** | IME off の日本語論述（英字引用・数式・URL）用の latin サブ baseline。**現 `β_coding` の値をそのまま改名して流用**（F1=150 / F3=0.06 / F4=5.0 / F5=2.0 / F6=0.08）。ADR-006 下位決定 #2 |
| **Coding head v0** | VibeCoding ドメインの推論ヘッド。現 `β_coding` の値を**初期シードとして所有**し、`ime_open` に関わらず適用する。coding イベント（accept/reject/test/revert/diff-review）は Epic 4 |
| **`DomainInferenceHead`** | head の trait。本タスクでは `head_id()` と潜在二軸の算出のみ。ADR-002 の `infer() -> WorkStateEstimate` 形は Decision Engine 境界（ADR-004・Epic 3）で導入する |
| **`head_id`** | どの head がそのセッションを採点したかの識別子。`writing` / `writing_fallback`（Creative）/ `coding_v0` |

---

## 1. 現状（実測）

```rust
// engine.rs:291-342  fn calculate_latent_axes(&self, features, ime_open) -> (f64, f64)
//   関数ローカル const で BETA_CODING_* / BETA_WRITING_* を定義
//   ime_open の三項で 5 個のタプルを選ぶ → phi() 5 回 → X/Y の重み付き和
// engine.rs:367      let apply_backspace_penalty = pending && !ime_open;
// engine.rs:45       pub const HMM_VERSION: &str = "0.3.0";
```

- `calculate_latent_axes` は **private**、呼び出しは `update()` (`:369`) と `update_silence()` (`:491`) のみ
- `BETA_*` / `calculate_latent_axes` を参照する**外部モジュールは 0 件** → 抽出は engine.rs 内で完結できる
- `analysis/` は `logger` に依存していない（依存方向の維持が必要）
- `task_kind` は `analysis/` に 0 件（dead_code）。`bin/replay.rs:173` の `SessionMeta` には
  **既に `task_kind: String` が存在する**が、`:257` で `None` を返して読み飛ばしている

---

## 2. 2a — 抽出（挙動不変・`HMM_VERSION` 不変）

### 2.1 新規モジュール

```
src-tauri/src/analysis/heads/
├── mod.rs        … DomainInferenceHead trait + head_id 定数
├── writing.rs    … WritingHead（β_writing / β_writing_latin）
└── (coding.rs は 2b で追加)
```

`analysis/mod.rs` に `pub mod heads;` を追加（`architecture-rules` Skill の mod.rs 更新規約に従う）。

### 2.2 trait

```rust
pub trait DomainInferenceHead: Send + Sync {
    fn head_id(&self) -> &'static str;

    /// 潜在二軸 (X = Friction, Y = Engagement) を算出する。
    /// `ime_open` は head 内部の within-writing 信号として渡す
    /// （どう使うか・使わないかは head が決める）。
    fn latent_axes(&self, features: &Features, ime_open: bool) -> (f64, f64);

    /// backspace ペナルティ（obs=25）を適用してよいか。
    /// Writing / Coding v0 とも現行どおり `!ime_open`（D-3）。
    fn applies_backspace_penalty(&self, ime_open: bool) -> bool { !ime_open }
}
```

⚠️ ADR-002 逐語の `infer(&mut self, &DomainFeatureSnapshot, &SessionContext) -> WorkStateEstimate`
とは形が違う。`WorkStateEstimate`（`uncertainty` / `evidence_quality` 必須）は Decision Engine 境界
（ADR-004）とセットで導入すべきで、本タスクの射程外。**この逸脱は ADR-002 に明記する**（D-8）。

### 2.3 `WritingHead`

```rust
pub struct WritingHead { id: &'static str }   // "writing" / "writing_fallback"

// TUNE: β_writing — IME on（日本語 composition）
const BETA_WRITING_F1: f64 = 100.0; F3 = 0.10; F4 = 2.5; F5 = 1.0; F6 = 0.12;
// TUNE: β_writing_latin — IME off（英字引用・数式・URL）
//   ★ 旧 BETA_CODING_* の値をそのまま改名。数値変更なし（ADR-006 下位決定 #2）
const BETA_WRITING_LATIN_F1: f64 = 150.0; F3 = 0.06; F4 = 5.0; F5 = 2.0; F6 = 0.08;
```

`latent_axes` の中身は現行 `calculate_latent_axes` の **式・演算順序をそのまま**移す。

> ⚠️ **浮動小数の演算順序を変えない。** `phi()` の呼び出し順、`0.30*phi3 + 0.25*phi6 + ...` の
> 項の順序、`clamp` の位置を一切いじらない。定数を関数ローカル const から
> モジュール const へ移すこと自体は f64 の値を変えないが、**式を「整理」すると byte-equal が壊れる**。

### 2.4 engine への接続

`CognitiveStateEngine` に `head: Arc<dyn DomainInferenceHead>` を持たせ、
`new()` は `WritingHead::new("writing")` を入れる（= 2a では常に現行と同じ経路）。

- `update()` / `update_silence()` の `self.calculate_latent_axes(features, ime_open)` を
  `self.head.latent_axes(features, ime_open)` に置換
- `let apply_backspace_penalty = pending && !ime_open;` を
  `pending && self.head.applies_backspace_penalty(ime_open)` に置換（既定実装が `!ime_open` なので等価）

`CognitiveStateEngine` の外部シグネチャ（`new()` / `update()` / `update_silence()`）は変えない
→ `lib.rs` / `bin/replay.rs` / `analysis/loop_step.rs` / `logger.rs` は **2a では無変更**。

### 2.5 2a の acceptance（＝ Done）

| 検査 | コマンド / テスト名 |
|---|---|
| ゴールデン 4 本 byte-equal | `cargo test --workspace` → `replay_snapshot_goldens_byte_equal` |
| `HMM_VERSION` 不変 | 新規テスト `hmm_version_is_unchanged_by_extraction`（`== "0.3.0"` を assert） |
| 全 10 fixture の差分ゼロ | 下記 2.6 の差分スクリプト（exit code 0） |
| schema drift なし | `cargo run --bin emit_schema` → `schema/current.json` と byte-equal |
| clippy 新規ゼロ | `cargo clippy --workspace` の警告数が変更前と同数 |

### 2.6 差分検証（ゴールデン 4 本では足りない部分を埋める）

ゴールデンは 4 本だが fixture は 10 本ある（`calib_subject_s1/s2/s3_eval` / `minimal.anon` /
`outcome_metrics` の 6 本は snapshot 未整備）。抽出リファクタが**ゴールデンで覆われていない経路**で
挙動を変えていないことを確かめるため、旧 HEAD のバイナリと比較する:

```bash
# scripts/verify-extraction-parity.sh (本タスクで新規追加)
git worktree add /tmp/gse-base HEAD          # 変更前
(cd /tmp/gse-base/src-tauri && cargo build --bin gse-replay --release)
(cd src-tauri && cargo build --bin gse-replay --release)
# 10 fixture × 適用可能な全モード (--snapshot / --metrics --json / --calibration / --intervention)
# の出力を両バイナリで生成し diff。1 バイトでも差があれば exit 1
```

---

## 3. 2b — 配線（挙動変更・`HMM_VERSION` `0.3.0` → `0.4.0`）

### 3.1 ルーティング型（`analysis/` は `logger` に依存しない）

```rust
// analysis/heads/mod.rs
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TaskDomain { Writing, WritingFallback, Coding }

pub fn head_for(domain: TaskDomain) -> Arc<dyn DomainInferenceHead> { … }
```

`logger::TaskKind` → `TaskDomain` の変換は **`lib.rs` 境界**で行う（依存方向を維持）:

| `task_kind` | `TaskDomain` | head_id | 挙動 |
|---|---|---|---|
| `Argumentative` | `Writing` | `writing` | **現行と同一** |
| `Correspondence` | `Writing` | `writing` | **現行と同一** |
| `Creative` | `WritingFallback` | `writing_fallback` | **数値挙動は現行と同一**（D-6）。印だけ付ける |
| `VibeCoding` | `Coding` | `coding_v0` | ⚠️ **変更**: `ime_open` に関わらず β_coding シード |

`bin/replay.rs` も `SessionMeta.task_kind`（`:173` に既存）を読んで `CognitiveStateEngine` に
渡す。⚠️ **これをやらないとリプレイが 2b の挙動を再現できない**（現在 `:257` で読み飛ばしている）。
`task_kind` 欠落 / 未知文字列のときは `Argumentative` 相当（`Writing`）にフォールバックし、
`tracing::warn!` を出す（既存 Phase1 ログとの互換）。

### 3.2 `CodingHeadV0`

```rust
pub struct CodingHeadV0;
// TUNE: β_coding — Coding head の初期シード（ADR-006 下位決定 #3）
//   値は β_writing_latin と同一から出発するが、所有者が別で以後独立に再チューニングする
const BETA_CODING_F1: f64 = 150.0; F3 = 0.06; F4 = 5.0; F5 = 2.0; F6 = 0.08;

impl DomainInferenceHead for CodingHeadV0 {
    fn head_id(&self) -> &'static str { "coding_v0" }
    fn latent_axes(&self, f: &Features, _ime_open: bool) -> (f64, f64) { /* β 固定 */ }
    // applies_backspace_penalty は既定実装（!ime_open）のまま = D-3
}
```

> ⚠️ **β_writing_latin と CodingHeadV0 の β は「同じ数値の別定数」として二重に持つ。**
> ADR-006 の帰結「両者は同じ数値から出発するが概念的・進化的に別物」を型で表現するため、
> **共有定数にしない**（共有すると Epic 4 の再チューニングで Writing 側が巻き添えになる）。
> 二重定義であることをコメントに明記する。

### 3.3 `head_id` の記録先 — ⚠️ ゴールデンを壊さない置き場所

`head_id` を **`FeatSnapshot` に入れてはいけない**。ゴールデン snapshot は `FeatSnapshot` 列なので、
フィールドを 1 つ足すだけで**既存 4 本すべてが byte-equal でなくなり、2b の acceptance が消滅する**。

→ **`session_meta` NDJSON 行に additive に追加する**（セッション単位の属性なので意味的にも正しい）。
`replay.rs` は `session_meta` を読み飛ばすため、ゴールデンは byte-equal のまま。

schema 変更を伴うので（引き継ぎ §5-7 の手順）:
```bash
cd src-tauri && cargo run --bin emit_schema > schema/current.json
python scripts/check_schema_parity.py --dataset /c/gse-dataset   # PYTHONUTF8=1
cp src-tauri/schema/current.json /c/gse-dataset/…                # gse-dataset 側もコミット
```

### 3.4 `HMM_VERSION` と SemVer 定義の補修（D-4）

`engine.rs:45` を `"0.4.0"` に。加えて `engine.rs:36-40` の SemVer 運用コメントに 1 行足す:

```
/// - 既存ログの確率列は変わらないが、新しい入力クラス（task_kind 等）に対して
///   挙動の分岐条件が増える場合: MINOR
```

**追随が要る箇所**: `docs/glossary.md:157`（「現行 `0.3.0`」）/
`docs/wbs-verification-halfyear.md:232`（`HMM_VERSION=0.3.0`）。

### 3.4b ⚠️ fixture の `task_kind` 実態（2026-08-18 実測・2b の前提）

| fixture | `session_meta` | `task_kind` | 2b での挙動 |
|---|---|---|---|
| `minimal` / `phase1_ime_heavy` / `category_coverage` / `deep_silence`（**ゴールデン 4 本**） | **無し** | — | フォールバック = Writing head → **byte-equal 維持** ✅ |
| `calib_subject_s1` / `s2` / `s3_eval` | 有り | **`vibe_coding`** | ⚠️ ルーティングが効く |
| `minimal.anon` / `outcome_metrics` / `phase1_minimal` | 無し | — | Writing head |

→ **ゴールデン 4 本に `session_meta` が 1 件も無い**ことが、2b で byte-equal が保てる根拠（実測）。

⚠️ ただし `calib_subject_*` の 3 本は `task_kind=vibe_coding` を持つ。これらは **`feat` 行を直接読む**
（`key` イベントを持たず engine を再実行しない）ため `--calibration` の結果は変わらない見込みだが、
**既定モード（snapshot 出力）の出力は変わり得る**。
→ ⚠️ **`verify-extraction-parity.sh` は 2a 専用のツールである。**
2b で流すと `calib_subject_*` の差分は「意図した変更」であり FAIL ではない。
2b では「ゴールデン 5 本 + 単体テスト」を acceptance とし、parity スクリプトは使わない。

### 3.5 新規ゴールデン `vibe_coding_ime_mixed`（D-5）

`tests/fixtures/vibe_coding_ime_mixed.ndjson`:
- `session_meta` に `task_kind: "vibe_coding"`
- IME on 区間と IME off 区間を**両方**含む打鍵列（β が切り替わらないことを見るため）
- backspace streak ≥14 を IME on 区間で 1 回起こす（D-3 の gate が効くことを固定）

`bin/replay.rs:2916` の `cases` 配列に追加（4 → 5 本）。

### 3.6 2b の acceptance（＝ Done）

| 検査 | テスト名 / コマンド |
|---|---|
| 既存 4 本が byte-equal のまま | `replay_snapshot_goldens_byte_equal` |
| 新規ゴールデンが緑 | 同上（`cases` に追加した 5 本目） |
| vibe_coding は IME に関わらず coding β | `vibe_coding_uses_coding_beta_regardless_of_ime` |
| creative / correspondence は Writing head | `creative_and_correspondence_route_to_writing_head` |
| Creative は挙動が現行と同一 | `creative_latent_axes_match_writing_head` |
| 未知 / 欠落 task_kind は Writing へ | `unknown_task_kind_falls_back_to_writing` |
| バージョン | `hmm_version_is_0_4_0` |
| schema | `emit_schema` → `check_schema_parity.py` 緑 |

---

## 4. テスト戦略

- `analysis/` は OS 非依存なので `cargo test --workspace` で両 OS 共通に検証できる
  （`docs/development-guidelines.md` §3）。**OS ごとに規則が違うロジックは無い**ので
  `#[cfg(target_os)]` 付きのテストは追加しない
- ゴールデン再生成は 2b でのみ行い、**5 本すべて**を再生成する
  （★ 3 本だけ再生成して `deep_silence` が落ちる事故が過去にある）
- 2a では**ゴールデンを再生成しない**（再生成した時点で 2a の意味が消える）

## 5. リスク

| リスク | 対策 |
|---|---|
| ⚠️ 抽出時に式を「整理」して byte-equal が壊れる | 演算順序・項順・clamp 位置を触らない。2.6 の全 fixture 差分検証 |
| ⚠️ `head_id` を `FeatSnapshot` に入れてゴールデンが全滅 | `session_meta` に置く（3.3） |
| ⚠️ replay が `task_kind` を読まず 2b を再現できない | `replay.rs:257` の読み飛ばしを修正（3.1） |
| ⚠️ 既存 Phase1 ログに `head_id` が無い | additive・欠落時は `writing` 相当として扱う |
| `Arc<dyn Trait>` の動的ディスパッチで数値が変わる | 変わらない（同じ f64 演算）。差分検証で確認 |
| clippy が新規警告を出す | 変更前後で警告数を比較（新規ゼロが acceptance） |

## 6. コミット計画

1. `refactor(engine): β を Writing head へ移送し β_coding を β_writing_latin に改名する` — 2a
2. `feat(engine): task_kind を head 選択へ配線し Coding head v0 を追加する (v0.4.0)` — 2b
3. `docs(adr): ADR-002 を Accepted に昇格し ADR-006 に実施記録を追記する`
