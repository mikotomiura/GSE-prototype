# 研究者本人の G1 の書き写しでの照合の試し（ADR-039 D6・人のデータでの試作）

研究者本人が G1 で打った書き写しのブロック 4 本（P009・P010 の block01・block10・原文 `experiments/20260801-controlled-friction-task/materials/copy.md`）の記録で、(1) 原文から合成した区間の長さの並びが記録とどれだけずれるか、(2) 記録の連続した k 区間から原文を候補 N 本の中で当てられるか、(3) 加工でどこまで偶然の水準に近づくか、を測る。合否の判定ではない（ADR-039【決 6-a】）。

- 作業記録: `.steering/20261011-g1-copy-self-trial/`（decisions.md 判断 1 が研究者の選択）
- 結果の前に固定したこと: `preregistration.md`・`config.json`・`SEED`
- 結果: `notes.md`（読み方と限界）・`results/summary.md`（表）・`results/*.json`（集計だけ）
- 入力: `data.md`（記録は repo の外・SHA-256 で照らす）・環境: `env.md`・`requirements.txt`
- 前の実測: `experiments/20261009-length-sequence-uniqueness/`・`experiments/20261009-matching-attack-prototype/`

## 再現

```bash
cd experiments/20261011-g1-copy-self-trial
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt   # Windows（macOS は .venv/bin/python）
G1_RECORDS=<復号した NDJSON> G1_WORK=<repo の外> ZIPS=<前の実測の raw/zips> bash run.sh
```

記録は git に入らず、研究者の秘密鍵で `.age` を復号して得る（`data.md`）。SHA-256 が違えば止まる。おとりのコーパスは `raw/`（git に入らない）。全体で 1〜2 分。

## ファイル

| ファイル | 役割 |
|---|---|
| `scripts/common.py` | 入力の照合・前の実測のコードの読み込み（SHA-256 を照らす）・乱数 |
| `scripts/g1rule.py` | 本文 → G1 の規則の区間（`other` にまとまるキーを区切りにする） |
| `scripts/build_corpus.py` | 原文の区間（`results/copy_segments.json`）とおとりの 1,500 作品（`raw/corpus_g1.json`） |
| `scripts/records.py` | 記録 → 区間（plain・clean）。`G1_WORK` に書く |
| `scripts/align.py` | 記録と原文の区間の揃え（動的計画法） |
| `scripts/crosscheck.py` | 照らし合わせ（集計を `results/crosscheck.json`、揃えの詳細を `G1_WORK`） |
| `scripts/matching.py` | 照合・加工・診断 |
| `scripts/summarize.py` | 表 |
| `scripts/explore_align.py` | 事後の探索（区切りの乱れを許す攻撃者・notes.md 逸脱 3） |
| `scripts/selftest.py` | 自己検査（記録を読まない） |
