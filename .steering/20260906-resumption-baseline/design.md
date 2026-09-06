# 設計

## 実装アプローチ

★ **コード（`src-tauri/`, `src/`）は 1 行も変えない。**★ 追加するのは `experiments/` 配下の
2 ディレクトリだけである。

### B1 — [P321] の公開データを集計する

1. ★ **到達性を先に確かめる（fail fast）**。⚠️ 粘らず、駄目なら代替へ。
2. ★ **検算 A を先に通す**。⚠️★★★ 通らなければ R₀ / R₁ を出しても意味がない。
3. ★ **検算そのものが空回りしていないか**を 3 状態で試す（`verify-before-claiming` 5b）。
4. ★ R₀ / R₁ を出し、**定義の揺れ 2 軸で感度分析**する。

### M1 — 「中断 → 再開」の観測を設計する

★ **設計を `experiments/` の形（config / data / env / SEED / run.sh / notes）で書く。**
★ 実行可能性だけプローブで確かめ、⚠️ **アウトカムの本解析は回さない**。

## 変更対象

### 新規作成するファイル

**`experiments/20260906-p321-resumption-baseline/`（B1・実行済み）**

| ファイル | 役割 |
|---|---|
| `analyze_p321.py` | 検算 A ＋ R₀/R₁/R₀′ の算出。`--selftest` で検査自体を 3 状態検査 |
| `run.sh` | ★ **Step 0′ = 入力の SHA-256 照合**（⚠️ capabilities gate は**適用外**） |
| `config.yaml` / `SEED` / `data.md` / `env.md` / `requirements.txt` | 規約の読み替えを明記 |
| `notes.md` | ★ 結論・限界・読み替え表・引き継ぎメモの誤り 3 件 |
| `results/` | `metrics.json` / `report.txt` / `provenance.txt`（★ 集計値のみ） |
| `raw/` | ⚠️ `.gitignore` 済み（`experiments/**/raw/`）。生データはコミットしない |

**`experiments/20260906-interruption-resumption-arm1/`（M1・設計のみ）**

| ファイル | 役割 |
|---|---|
| `notes.md` | ★ 設計本体（観測単位 / アーム分離の機械的根拠 / 制約 8 件 / 限界） |
| `feasibility_probe.py` | ★ N があるかの数え上げ（⚠️ アウトカムではない） |
| `run.sh` | ★ **Step 0 = `capabilities_gate.py`**（⚠️★★★ こちらは**適用される**）/ Step 2b は未実装 |
| `config.yaml` / `SEED` / `data.md` / `env.md` / `README.md` | — |
| `results/` | `capabilities.json` / `feasibility.json` / `provenance.txt` |

### 修正するファイル
- ★ **なし**（⚠️ `src-tauri/` も `src/` も `docs/adr/` も触らない）

## 影響範囲

- ★ **コード影響ゼロ。** `cargo test` / `gse-replay` のゴールデンに触れない。
- ★ `HMM_VERSION` は **bump しない**（★ HMM の挙動を変えていない）。
- ⚠️ `schema_dto.rs` / `schema/current.json` を触らないので **schema drift check は関係しない**。

## 既存パターンとの整合性

- ★ `experiments/_template/` の構造（config / SEED / data.md / env.md / run.sh / results / notes.md）に従う。
- ⚠️★★★ **`run.sh` Step 0 の扱いが 2 実験で違う** —— ★ これは意図であり、両方 `notes.md` に明記した:

| 実験 | Step 0 | 理由 |
|---|---|---|
| B1（P321） | ⚠️ **適用外** → **Step 0′ = SHA-256 照合**に置換 | ★ GSE が収集した信号を 1 行も読まない |
| M1（arm1） | ★ **適用される**（消さない） | ★ GSE の NDJSON を読む |

## テスト戦略

- ★ **`--selftest`（3 状態）**: 正常 / 不在（参照活動を全削除）/ 壊れている（DF7 畳み込み無効）
- ★ **`run.sh` を実際に走らせて exit code を見る**（⚠️ `| tail` にパイプしない）
- ★ **検算 A の 12 項目**が論文の一次記述と一致すること
- ★ **漏洩検査**: `results/*.json` に URL / 動画 ID / ファイル名が入っていないこと
- ⚠️ 単体テスト（`cargo test`）は **対象外**（★ Rust を 1 行も変えない）
