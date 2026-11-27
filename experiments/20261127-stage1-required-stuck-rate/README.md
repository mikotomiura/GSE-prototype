# 要る詰まりの率の模擬（段 1・2026-11-27）

段 1 の確認の参加者 1 人について、詰まりの率 π ごとに、H1〜H3・S1-E4・S1-G2 が「判定不能でない」確率を合成で出し、0.8 以上になる最小の π を表にする（A-1 の判断 62 の後・研究者が「表にする」を選んだ）。

- 条件: `conditions.md`（回す前にコミット）・環境: `env.md`・再現: `bash run.sh`（H3 の内訳は `python3 -I scripts/h3_breakdown.py 20261127 results/h3_breakdown.json`）
- 結果: `results/required_rate.md`・`results/required_rate.json`・`results/h3_breakdown.json`・読み方と限り: `notes.md`
- 本人の記録の生データは読まない。値は事前登録の本文の集計だけ。

## 第 2 版（3 名を合わせた判定と下限・2026-11-27）

- 研究者が H2・H3 を「3 名を合わせて判定・人ごとは記述」とし、「詰まり 10 件未満は判定不能」の下限を選んだ後に、判定が出る見込みを確かめた。
- 条件: `conditions.md` の第 2 版（回す前にコミット 0217d973）・script: `scripts/pooled.py`・再現: `bash run.sh` の後半
- 結果: `results/pooled.md`・`results/pooled.json`・読み方と限り: `notes.md` の第 2 版
