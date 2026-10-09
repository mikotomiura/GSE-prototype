# 入力データ

人のデータ（O1・G1・Phase1 の NDJSON）は使わない。入力は青空文庫（https://www.aozora.gr.jp/）の公開テキストだけ。

## 作品の一覧

| 項目 | 値 |
|---|---|
| URL | `https://www.aozora.gr.jp/index_pages/list_person_all_extended_utf8.zip` |
| 取得日 | 2026-10-09 |
| SHA-256 | `a615fa6ddb6ef3e0ad598337f5d08f1570c3d2aa51cc5d43a62998ca904905be` |
| 置き場所 | `raw/index/`（git に入らない。`run.sh` が SHA-256 を照らす） |
| ライセンス | 図書カードと一覧は CC BY 4.0（青空文庫） |

一覧は青空文庫の側で更新される。SHA-256 が違えば `run.sh` は止まる（同じ選定を再現するには、この版の一覧が要る）。

## 作品

- 選定: `scripts/select_works.py`（`results/selection.json` に、条件を満たす作品の全順序と参照の 12 作品）。
- 取得した zip: `results/corpus_manifest.json`（作品 ID・URL・SHA-256・バイト数）。zip は `raw/zips/`（git に入らない）。
- 使った作品: `results/corpus_stats.json` の `corpus_work_ids`（1,500）と `reference_work_ids`（12）。落とした作品と理由は `dropped`。
- 著作権の切れた作品で、複製・再配布・改変は自由（青空文庫「収録ファイルの取り扱い規準」・memory「青空文庫の取得元」に一次の確認の記録）。底本・入力者・校正者の情報は各 zip に残っている。
- 参照の 12 作品の zip が IME 論文の記録（`papers/ime-observation/experiment/data.md`）と同じかは、`corpus_manifest.json` の `matches_ime_paper` に書く。
