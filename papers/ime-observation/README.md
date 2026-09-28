# Observing Japanese IME conversion without recording text: Observability limits, a cross-platform logger, and a synthetic-input validation

日本語 IME の変換を、本文を記録せずに観測する。観測の限界・クロスプラットフォームの単体ロガー・
合成入力による検証を 1 本の論文にまとめるための作成物の置き場。境界の規則（GSE 本体から参照しない・
生ログを git に入れない・公開時に書き出せない語を書かない）は [`../README.md`](../README.md) にある。

## 構成

| ディレクトリ | 役割 |
|---|---|
| `kit/` | 再現できる道具一式（ログ形式・生成器・実行器・参照入力欄・単体ロガー・解析・書き出し）。 |
| `experiment/` | 実験の記録（SEED / env.md / data.md / run.sh / notes.md）。生ログは置かず（`experiment/raw/` は無視される）、寄託先と SHA-256 を `data.md` に書く。 |
| `manuscript/` | 原稿。 |

## ライセンス

- コード（`kit/`）: Apache-2.0
- データ・文書（`experiment/` の記録・`manuscript/`）: CC BY 4.0

## 部品の置き場

後続の部品はこの場所に作る。

| ディレクトリ | 中身 | issue |
|---|---|---|
| `kit/formats/` | ログ形式の契約と検査器 | 001 |
| `kit/corpus/` | 青空文庫の句と読み | 002 / 027 |
| `kit/gen/` | シナリオ生成器 | 003 |
| `kit/emit/` | 実行器（合成キーの送出と oracle） | 004 / 005 |
| `kit/run/` | 1 セルの段取り | 006 |
| `kit/refinput-macos/` / `kit/refinput-windows/` | 参照入力欄 | 007 / 008 / 009 |
| `kit/logger/` | 単体ロガー | 011–014 |
| `kit/pilot/` | 較正パイロットの道具 | 015 |
| `kit/analysis/` | 正解の組み立て・照合・L1・L2・パイプライン | 010 / 016–020 |
| `kit/e2/` / `kit/e3/` | 漏洩の評価 / 実行コスト | 021 / 022 / 023 |
| `kit/export/` | 公開 repo への書き出し | 024 |

## 検証

```bash
bash papers/ime-observation/kit/check.sh              # kit/ の selftest を全部回す（空振りは赤）
bash papers/ime-observation/kit/check.sh --compile    # kit/ の全 .py を py_compile
bash papers/ime-observation/kit/check.sh --self-test  # この入口自身の陰性対照
```

- `kit/` 配下で、`# kit: selftest` という目印のコメントを持つ `.py` だけが `--selftest` で回される
  （目印の無い補助モジュールは compile だけ）。
- 入口は verify で毎回・各 acceptance でも回るので、**selftest は速い既定で書く**（1 本 30 秒以内。超えると
  警告が出る）。重い検査は `--selftest --full` などに分け、既定では回さない。
- ログ形式の契約は [`kit/formats/FORMATS.md`](kit/formats/FORMATS.md)。`gt` と `obs` の行に本文が入らないことは
  `kit/formats/validate_logs.py` が機械で保証する。
