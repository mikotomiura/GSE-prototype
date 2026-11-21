# data.md — 入力の固定（auto-context-segmentation）

入力 NDJSON はリポジトリにコミットしない。ファイル名は書かず、人ごとの本数・合計バイト数と、
各ファイルの SHA-256 を昇順に並べて改行でつないだ列の SHA-256（要約値）で固定する。

| 人 | 置き場 | 本数 | 合計バイト | 要約値（SHA-256） |
|---|---|---|---|---|
| self | 本人の記録（`~/Documents/GSE-sessions/`・2026-10-09〜11-20・O1 の時期と段 1 の時期） | 57 | 566277106 | `c025dd8164c977d529fe90c32a3377392b3acf8c6a187d88d6786704e451582f` |
| P006 | O1 の被験者（`~/gse-o1-derived/20261116-o1-conduct-record/plain/`・11-16 の復号） | 46 | 673334537 | `1015fd2aac2a035fa29693d50e8631e6ba66f8d4114d64b4092d9c7bfb572f12` |
| P009 | O1 の被験者（`~/gse-o1-derived/20261116-o1-conduct-record/plain/`・11-16 の復号） | 48 | 447068953 | `5b7d06b2cb54e217542aeaabe0bb34eda18bd7741c85be504fd9e4ee8b17bb0e` |
| P011 | O1 の被験者（`~/gse-o1-derived/20261116-o1-conduct-record/plain/`・11-16 の復号） | 14 | 588608 | `a95acd0b6d7d7d7ffffe6ce7332f4751914c7c0ac1a0b0e7f69674904e82db3b` |
| P013 | O1 の被験者（`~/gse-o1-derived/20261116-o1-conduct-record/plain/`・11-16 の復号） | 32 | 88629554 | `df26bfd7d25897f162f2c98aa74cc58e08be80a9d8893a23ae804b73aea45b8d` |

全体の要約値: `4df3928d125d2d704a36c334c417e3a0fd590cdaa68f1b06656d213f4ebbe9dd`

- 選び方は研究者が決めた（2026-11-21・decisions.md 判断 16）。O1 の削除の求めは 0 件（`docs/o1-deletion-ledger.md`）。
- 人ごとのファイルの一覧（実パス）は `work/people.json` にあり、コミットしない。
- 合成の記録は `gen_synth.py` と `SEED` から作り直せる（コミットしない）。
