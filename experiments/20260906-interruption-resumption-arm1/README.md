# 20260906-interruption-resumption-arm1

★ ADR-023 §Migration **M1** —— 「中断 → 再開」の観測設計（★ 第 1 弾 = **離席候補アームのみ**）。

⚠️★★★ **設計 ＋ 実行可能性プローブまで。アウトカムの本解析 (run.sh Step 2b) は未実装。**

- 設計と限界: **`notes.md`**（★ 先にこれを読む）
- 前段の実測: `experiments/20260906-p321-resumption-baseline/`（**B1**）
- 実行: `GSE_DATASET=C:/gse-dataset bash run.sh`

⚠️★★★ **`run.sh` Step 0（`capabilities_gate.py`）を消さないこと。**
★ 本実験は GSE が収集した信号を読むので、ADR-013 のゲートは **適用される**。
