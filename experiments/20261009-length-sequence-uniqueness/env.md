# 実行環境

`reproducibility-discipline` ルール 2・3。

## GSE 側のアンカー

| 項目 | 値 | 出所 |
|---|---|---|
| repo commit（実験の開始時） | `f0ac66a0`（main） | `git rev-parse --short HEAD` |
| ブランチ | `docs/length-sequence-uniqueness` | 実測 |
| `HMM_VERSION` | 使わない | 本実験は GSE のコード（`src-tauri/`）を 1 行も実行しない。記録の形式（`KeyCategory`・key 行）は読んで写しただけ（`.steering/20261009-length-sequence-uniqueness/design.md` §1・§2） |

## ツール

| ツール | 版 | 用途 |
|---|---|---|
| Python | 3.11.9（Windows 11 Home 10.0.26300・G-GEAR） | 全計算 |
| SudachiPy | 0.7.0（Apache-2.0） | 読み（`.venv`） |
| SudachiDict-core | 20260723.1（Apache-2.0） | 読み（`.venv`） |
| シェル | git-bash（`run.sh`） | 1 コマンド再現 |

`.venv/Scripts/python -m pip freeze` の出力（2026-10-09）:

```text
sudachidict-core==20260723.1
SudachiPy==0.7.0
```

ほかは Python の標準ライブラリだけ（numpy は使わない）。

## 写したコード

| 写した先 | 元 | 元の SHA-256 |
|---|---|---|
| `scripts/romaji_table.py` の表 | `papers/ime-observation/kit/gen/romaji.py`（Apache-2.0・同じ研究者） | `79db4d4ef74fb3e354aff769f0fe5c350cf57410c0adb2e7543d5594afd9f4b1` |
| `scripts/build_segments.py` の `body_lines` の規則 | `papers/ime-observation/kit/corpus/build_corpus.py` | `e44477302a8a4aa209eda6fffee791d70e0d6eb3f4a68f77dc00c04958db3132` |

`scripts/selftest.py` は、写した表の打鍵数が元の `romaji.py` の `to_keys` と一致することを確かめる（元のファイルを repo から読む）。
