# Tier 0 配線 — `feat` 行に `keys` / `bs_keys` を additive に追加する（記録のみ）

> ⚠️★★★ **本セッションでコードは 1 行も変更していない。** 調査と判断の確定までで止めた（研究者判断・コンテキスト都合）。
> ★ 実装は次セッション。引き継ぎ: `.steering/_handoff/next-session-prompt-tier0-keys-wiring.md`

## 背景

`docs/architecture/personalization-and-online-learning.md §5.2` の **Tier 0**
（★ **新規収集ゼロで効く層**）は、Phase1 の実測でこう言われている:

| 信号 | 実測 | 状態 |
|---|---|---|
| `keys`（窓内打鍵数）→ Q2 | ★ **個人内 C-index 0.60–0.68**（P014 のみ 0.368） | ⚠️★★★ **現行 5 特徴量のどれよりも高いのに、推論に 1 バイトも使われていない** |
| `external_paste_chars` → Q1 | 0.571（P010） | ★ 既に別レコードで記録済み・未配線 |

★ そして `progress_proxy`（純産出 = 挿入 − 削除）は **ADR-009 D2 の目的変数の構成要素**である。
★ その材料は **`keys` を 1 つ足すだけで揃う**（`f3 = correction_keys / total_keys` が既にあるため）。

### ★ 2026-08-15 の文献ラウンドが、この投資順序を独立に支持した

- ★★★ **12 か国・449 名の実配備**（FlowLight）が使っている中断可能性の測度は、
  **打鍵＋マウスの率を個人の過去分位で閾値化するだけ**で、アプリ識別子を 1 つも使わない [P119]。
  → ★ **Tier 0 ＋ 個人正規化（§4.4 Phase A）は実配備の実績がある。**
- ⚠️ 一方 **Tier 1–2 を足したときの利得を測った ablation は 1 本も存在しない（判定不能）**。
- 詳細: `docs/literature/20260815-desk-behavior-stagnation-inference.md`

## ゴール

★ **`feat` 行と `FeatSnapshot` に `keys` / `bs_keys`（ともに整数）を additive に追加し、
記録だけする。HMM にも X/Y 合成式にも 1 バイトも流さない。**

★ Done は exit code で言える:

```bash
cd src-tauri
cargo test --workspace                                     # 緑
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json
cargo run --bin emit_schema                                # additive-only diff
cd .. && python scripts/check_schema_parity.py --dataset C:/gse-dataset   # exit 0
```

## スコープ

### 含むもの
- `src-tauri/src/schema_dto.rs` — `Feat` DTO に `keys` / `bs_keys` を `Option<u64>` ＋ `#[serde(default)]` で追加
- `src-tauri/src/logger.rs:1214` — `feat` 行のフォーマット文字列に 2 フィールド追加（★ 書き出しは常に値を書く）
- `src-tauri/src/analysis/loop_step.rs:134` — `FeatSnapshot` に 2 フィールド追加
- `src-tauri/src/analysis/features.rs` — `total_keys` / `correction_keys` を持ち回す（★ 新規計算ゼロ）
- `src-tauri/schema/current.json` — `emit_schema` で再生成（★ 同じコミットに含める）
- `src-tauri/tests/snapshots/*.json` — ★ **golden 4 本を再生成**
- ★ **`C:\gse-dataset` 側の `schema/current.json`** — 同時更新（★ 研究者判断・下記 D2）
- `docs/architecture/personalization-and-online-learning.md §10` — ★ 順序記述の改訂（下記 D1）

### 含まないもの
- ⚠️ **`keys` / `bs_keys` を読む本番コード**（★ 記録のみ。消費者は将来の recovery 推定器）
- ⚠️ **`HMM_VERSION` の bump**（★ HMM 挙動が変わらないため）
- ⚠️ **`ime_dwell_med` の追加**（★ 案 C。`§11-5` の macOS 常時ゼロ調査が先）
- ⚠️ **Tier 1（沈黙長・burst 長の分布）**（★ 別タスク。`feat` に足すか別レコードかが未決・memo §8-3）
- ⚠️ **`engine.rs` / `intervention.rs` / `probe_scheduler.rs`**（★ 一切触れない）

## 受け入れ条件（★ `tier0-wiring-design.md §7` を継承し 2 件追加）

- [ ] `emit_schema` の diff が **additive-only**（追加のみ・型変更なし・required 追加なし）
- [ ] 旧フィクスチャ（新フィールドなし）を `gse-replay` が読める
- [ ] ★★★ golden 再生成の差分が **新フィールドの追加のみ**（`p_*` / `raw_*` / `ewma_*` / `obs` が動いていない）
      —— ⚠️ **これが最重要。動いていたら §2 の「記録と推論の分離」が破れている証拠なので、その場で止める**
- [ ] `HMM_VERSION` が変わっていない
- [ ] `check_schema_parity.py` が **exit 0**（★ 下記 ⚠️ 既存 drift を先に解消する必要がある）
- [ ] `cargo test --workspace` が緑
- [ ] 新フィールドを読む本番コードが **まだ存在しない**こと
- [ ] ★ **追加 1**: `.age` / NDJSON / 実セッション名が repo に入っていないこと（`data-privacy`）
- [ ] ★ **追加 2**: `code-reviewer` + `security-checker` の並列レビュー（★ CLAUDE.md 必須・前セッションでは動作条件で禁止されていた）

## ⚠️★★★ 着手前に解消が要るブロッカー（★ 本セッションの実測）

### B-1: **既存の schema parity drift がある**（★ 本タスクの変更以前の問題）

```
$ python scripts/check_schema_parity.py --dataset C:/gse-dataset
[check_schema_parity] DRIFT detected
Missing variants in B: hook_health
（加えて meta variant の g1_mode プロパティが B 側に無い）
REAL EXIT=1
```

⚠️★★★ **`C:\gse-dataset` の schema は本 repo より古い。** 本タスクの additive 変更は**この drift の上に載る**。
→ ★ **先に `hook_health` / `meta.g1_mode` を dataset 側へ反映して exit 0 に戻してから、本タスクの差分を足す。**
⚠️ **そうしないと「今回の変更で壊れたのか、元から壊れていたのか」が分離できない。**

### B-2: **`FeatSnapshot` は golden の byte-equal 比較対象そのもの**

★ 一次（`loop_step.rs:133` doc コメント逐語）: **「ゴールデンスナップショット (P0-10) の byte-equal 比較対象」**
★ golden は **4 本**: `minimal.json` / `phase1_ime_heavy.json` / `category_coverage.json` / **`deep_silence.json`**
⚠️★★★ **`experiments/20260731-phase1-calibration-analysis/notes.md §5③` の「golden 3 本」は古い**（★ `deep_silence.json` が増えている）。

## 関連ドキュメント

- ★ **設計の原本**: `.steering/20260801-recovery-axis-grounding/tier0-wiring-design.md`（★ 181 行・受け入れ条件つき）
- `docs/architecture/personalization-and-online-learning.md` §5.2（Tier 表）/ §10（実装計画）
- `docs/adr/ADR-009-recovery-risk-axis-and-latent-state.md` Migration P1
- `docs/adr/ADR-008-online-learning-boundary.md` D5（pinning）
- `docs/adr/ADR-005`（additive versioning）
- `docs/literature/20260815-desk-behavior-stagnation-inference.md`（★ 投資順序の文献裏づけ）

## 運用メモ

- **/reimagine 適用: No**
- **理由**: ★ 設計は `tier0-wiring-design.md` に既に確定しており（案 A/B/C を比較し **案 B を推奨**まで済んでいる）、
  ★ 本タスクはその実装である。複数案の再生成は不要。
  ⚠️ ただし **B-1（既存 drift）は設計時に想定されていなかった**ため、その扱いだけは design.md で決める。
