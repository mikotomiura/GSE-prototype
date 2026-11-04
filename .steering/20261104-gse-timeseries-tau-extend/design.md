# 設計

## 実装アプローチ

- 前回の実験のディレクトリ（`experiments/20261104-coauthor-ml-improve/`）は変えない。新しい `experiments/20261104-timeseries-tau-extend/` に、前回の `scripts/`・`run.sh`・`mutate.sh` を写してから変える（写した版の SHA-256 を provenance に残す）。
- 条件は前回の `conditions.md` を下敷きにし、変える所だけを書く（`conditions.md`）。
- 重なる行を前回と一致させる（P-REPRO）ために、SEED・全員の共通の乱数の通し番号・書き手ごとの乱数の並べを前回のままにする。外した構造の番では、乱数の開始点だけを引いて捨てる。

## 変更対象（コードの段・このセッションでは書かない）

### 新規作成するファイル
- `experiments/20261104-timeseries-tau-extend/conditions.md`・`SEED`（このセッション）
- `scripts/`（前回から写す）: `ml.py`（TAUS・STRUCTS・τ = ∞・2 段の行・共通 − r1・P-REPRO 用の照合）、`selftest.py`（P-INF・P-TAU・P-JOINT・P-PR1・P-SUBSET・ロジスティックの対照を外す）、`report.py`（新しい行）、`check_mutations.py`（m11〜m15）、`repro_check.py`（新しい・前回の summary と照らす）
- `run.sh`・`mutate.sh`（ロジスティックの段を外す・P-REPRO を足す・書き手ごとの値の置き場所の名前）

## 影響範囲

- 前回の結果・条件には触れない。
- repo には集計値だけ。書き手ごとの値は `~/gse-public-data/landscape/timeseries_tau_extend_writer_values.*.json`。

## テスト戦略

- 合成の selftest（引き継ぐ 12 対照＋新しい 5 対照）と変異（引き継ぐ 6 個＋新しい 5 個）を Mac で通してから HP Z2 へ渡す。
- HP Z2 で P-D1・P-REPRO を本計算の頭と後に回す。

## ロールバック計画

- 枝 `exp/gse-timeseries-tau-extend` を捨てれば前回の状態に戻る（前回の枝には触れない）。
