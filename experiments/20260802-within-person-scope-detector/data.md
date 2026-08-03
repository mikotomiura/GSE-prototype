# 入力データの固定

## 出所

[mikotomiura/gse-dataset](https://github.com/mikotomiura/gse-dataset)（private）の `raw/P0{10..14}/*.ndjson`。
**前ラウンド `experiments/20260802-task-scope-detector/` と完全に同一の入力**である。

| 項目 | 値 |
|---|---|
| gse-dataset commit | `c2f960c0b9a04778e616dbd212517c65a76f132c` |
| 参照パス | `raw/P010` `raw/P011` `raw/P012` `raw/P013` `raw/P014` |
| 除外 | `raw/P000`（開発者の動作確認用・較正コホート外。`analyze.py` で明示的に除外） |
| セッション数 | P010=12 / P011=5 / P012=7 / P013=10 / P014=6（計 40） |
| 解析対象 | 38（`press < 200` の事前基準で 2 セッション除外・前ラウンドと同一基準） |
| `session_meta.task_kind` | 全セッション `argumentative`（分散ゼロ。**教師に使えない**） |
| `session_meta.condition` | 全セッション `blind_calibration` |

## ★ 同一データの再利用について（本実験の最大の弱点）

本実験は前ラウンドと**同じ 38 セッション**を使う。新規収集はゼロである。
したがって「導出集合 = 検定集合」の問題が構造的に存在する。

- 判別特徴 `bs_rate` は **P013 の探索的分析から選ばれた**。
- そのため **主検定 T-1 は P013 を除外して行う**（`preregistration.md` §T-1）。
- P013 を含む数値（T-2 / P-1）は**サニティチェックであり証拠に数えない**。
- ⚠️ 厳密には P010/P011/P012/P014 も「前ラウンドで被験者別中央値を見た」母集団であり、
  完全な hold-out ではない。**セッション単位の `bs_rate` が未見**という限定的な hold-out である。
  この限界は `preregistration.md` の凍結宣言に明記した。

## プライバシー

- ⚠️ **raw NDJSON は本リポジトリに一切コミットしない**（`docs/development-guidelines.md` §10 / `data-privacy`）。
- NDJSON には**本文が含まれない**（content-free）。`key` レコードは `{t, press, category}` のみ。
- 本実験の出力（`metrics.json`）は**集計値のみ**。
- ⚠️ **NDJSON も打鍵内容も外部 LLM に送信していない**（解析はすべてローカル）。

## 匿名化

⚠️ 本 repo は **ビルドのため一時的に public にする運用がある**。
そのため成果物には **セッション名の日時を出力しない**。`analyze.py` はファイル名順の安定した
連番（`P013-s03` 等）へ置き換える。**対応表は repo に残さない**（gse-dataset 側から再構成可能）。
連番規則は前ラウンドと同一なので、両ラウンドのセッション ID は相互に対応する。
