# 実行環境

`reproducibility-discipline` ルール 2・3。

## GSE 側のアンカー

| 項目 | 値 | 出所 |
|---|---|---|
| repo commit（実験の開始時） | `6e2e349b`（引き継ぎのコミット・`15251993` の main の上） | `git rev-parse --short HEAD` |
| ブランチ | `docs/matching-attack-prototype` | 実測 |
| `HMM_VERSION` | 使わない | 本実験は GSE のコード（`src-tauri/`）を 1 行も実行しない |

## ツール

| ツール | 版 | 用途 |
|---|---|---|
| Python | 3.11.9（Windows 11 Home 10.0.26300・G-GEAR） | 全計算 |
| SudachiPy | 0.7.0（Apache-2.0） | 照らし合わせの読み（`.venv`） |
| SudachiDict-core | 20260723.1（Apache-2.0） | 同上 |
| シェル | git-bash（`run.sh`） | 1 コマンド再現 |

`.venv/Scripts/python -m pip freeze` の出力（2026-10-09）:

```text
sudachidict-core==20260723.1
SudachiPy==0.7.0
```

ほかは Python の標準ライブラリだけ（numpy は使わない）。

## 読み込んで呼ぶコード（写さない・書き換えない）

`scripts/kitload.py` が、読み込む前に下の SHA-256 を照らし、違えば止まる（値は `config.json` の `code` と同じ）。

| ファイル | SHA-256 |
|---|---|
| `papers/ime-observation/kit/e2/closed_set.py` | `364cc833b48a73aeb15b9416bff203ec21a71296e26534f914e3a2bb9bd067c3` |
| `papers/ime-observation/kit/e2/simulate_obs.py` | `ab989955e7273e9290595318a96087c384d40e19565f351be17bf3f8d4733123` |
| `papers/ime-observation/kit/gen/generate_plan.py` | `822538a52fd40ddc04e7ef406373f8d6cf5b0e7e22763b695fe61cef5fd5cb15` |
| `papers/ime-observation/kit/gen/romaji.py` | `79db4d4ef74fb3e354aff769f0fe5c350cf57410c0adb2e7543d5594afd9f4b1` |
| `papers/ime-observation/kit/analysis/stats.py` | `ead0ccaa50bb86b088b66899ef5b1e04fb9b995a582e520679e04d09cbbf5c07` |
| `experiments/20261009-length-sequence-uniqueness/scripts/romaji_table.py` | `d2101efb9f36201b7fb51ea7c4283c114854cf13bba8fae379b6f85ae381fbd2` |
| `experiments/20261009-length-sequence-uniqueness/scripts/build_segments.py` | `7b84a46bdc9ff6f6d44b3635f4f84533aea7a4f189d8d84ce5f0113c24f1cd8f` |

IME 論文のコードは Apache-2.0（`papers/ime-observation/LICENSE-CODE`・同じ研究者）。
