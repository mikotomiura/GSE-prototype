# 合成入力での照合攻撃の試作（ADR-039 D6 の候補 1）

IME 論文の Windows のセルの記録（executor が送った合成入力・人の打鍵ではない）で、(1) 前のタスクの手順で本文から合成した長さの並びが実機の記録と一致するか、(2) 候補 N 本からの照合がどれだけ当たるか、(3) 加工でどこまで偶然の水準に近づくか、を測る。合否の判定ではない（ADR-039【決 6-a】）。

- 作業記録: `.steering/20261009-matching-attack-prototype/`（design.md に手順、decisions.md に判断）
- 結果の前に固定したこと: `preregistration.md`・`config.json`・`SEED`
- 結果: `notes.md`（読み方と限界）・`results/summary.md`（表）・`results/*.json`
- 入力の版: `data.md`（記録・計画・語句・手順の SHA-256）
- 環境: `env.md`・`requirements.txt`
- 前のタスク: `experiments/20261009-length-sequence-uniqueness/`

## 再現

```bash
cd experiments/20261009-matching-attack-prototype
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt   # Windows（macOS は .venv/bin/python）
bash run.sh            # 入力の照合 → 自己検査 → 割り当て → 照らし合わせ → 距離 → 再現の確認 → 照合 → 表
```

記録と計画は git に入っていない（`data.md` の手順で Zenodo から取る）。SHA-256 が違えば止まる。派生データは `raw/`（git に入らない）。全体で 1〜3 分（並列 4 と 2）。

## ファイル

| ファイル | 役割 |
|---|---|
| `scripts/kitload.py` | IME 論文と前のタスクのコードを SHA-256 を照らして読み込む・入力の照合 |
| `scripts/prepare.py` | 記録を計画の試行に割り当て、試行ごとの値を作る（`raw/trials.json`） |
| `scripts/crosscheck.py` | 照らし合わせ（記録 ↔ 本文から合成した並び） |
| `scripts/distances.py` | シミュレーション攻撃の試行ごとの距離（`raw/dist/`） |
| `scripts/data.py` | 攻撃の入力の読み込み |
| `scripts/reproduce_ime.py` | k = 1 で IME 論文の公開値を再現する確認（一致しなければ止まる） |
| `scripts/matching.py` | 441 セルの照合と診断（結果は並列の数によらない） |
| `scripts/explore_procedure_noise.py` | 事後の探索（事前の固定に無い） |
| `scripts/summarize.py` | 表 |
| `scripts/selftest.py` | 自己検査 |
