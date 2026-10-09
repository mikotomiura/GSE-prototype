# 長さの並びの一意性（ADR-039 D6 の関門の最初の実測）

公開テキスト（青空文庫）を理想の書き手が打ったと仮定し、打鍵の記録に残る「句読点（、。）と改行の間の打鍵の個数」の並びが、どれだけ一意か、候補の文章との照合でどれだけ当たるかを見積もる。人のデータは使わない。

- 作業記録: `.steering/20261009-length-sequence-uniqueness/`（design.md に手順と換算表）
- 結果の前に固定したこと: `preregistration.md`・`config.json`・`SEED`
- 結果: `notes.md`（読み方と限界）・`results/summary.md`（表）・`results/*.json`
- 入力の版: `data.md`・`results/corpus_manifest.json`（zip ごとの SHA-256）
- 環境: `env.md`・`requirements.txt`

## 再現

```bash
cd experiments/20261009-length-sequence-uniqueness
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt   # Windows（macOS は .venv/bin/python）
bash run.sh            # 自己検査 → 選定 → 取得と照合 → 前処理 → 指標 1 → 指標 2 → 表
```

取得は 1 秒に 1 件（約 27 分）。zip と派生データは `raw/`（git に入らない）に置く。zip の SHA-256 が `results/corpus_manifest.json` と違えば止まる（青空文庫の側でファイルが更新された場合）。

## ファイル

| ファイル | 役割 |
|---|---|
| `scripts/romaji_table.py` | かな → ローマ字の打鍵数（IME 論文の表の写し）と書き手の癖 |
| `scripts/select_works.py` | 作品の一覧から作品を選ぶ |
| `scripts/fetch_works.py` | zip の取得と SHA-256 |
| `scripts/build_segments.py` | 本文の切り出し・ルビ・SudachiPy の読み・区切り B0〜B3 |
| `scripts/uniqueness.py` | 指標 1 |
| `scripts/matching.py` | 指標 2（並列は `PROCESSES` で変える。結果は並列の数によらない） |
| `scripts/selftest.py` | 自己検査（採点・正解の選ばれ方・換算・BS の較正・前処理） |
| `scripts/summarize.py` | 表 |
