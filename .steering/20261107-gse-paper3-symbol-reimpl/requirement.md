# 論文 3 の記号化の書き直し（公開 repo 用）

## 背景

論文 3（`.steering/20261107-gse-paper3-per-person-learning/`・判断 9）の記号の列は、GSE の replay が出す 26 記号の `obs`（2 つの平滑した特徴 x・y を 5×5 に割った 25 個＋ Backspace の連打の罰の記号 1 個・`src-tauri/src/analysis/engine.rs:402-406`）である。論文と公開 repo には GSE の名前を出さず、公開 repo は集計値と合成の検査だけを置く。読者が公開の生データ（CoAuthor・CS1 2021）から記号を作り直せるように、記号化を公開 repo 用に書き直す（研究者の選択・2026-11-07）。

## ゴール

生データから `obs` の列を作る独立の実装を `papers/per-person-learning/` の下に置き、手元で全セッション（CoAuthor）・全課題（CS1 2021）の記号が replay の `obs` と完全に一致することを確かめる。

## スコープ

### 含むもの
- 経路の洗い出し（生データ → 変換 → replay 2 回 → `obs`）と、書き直す範囲の決定
- 書き直しの実装（言語は設計で決める）・合成の selftest・変異で赤を見る
- 手元の照合（完全一致の件数だけを集計値として残す）

### 含まないもの
- 公開 repo の作成・push・書き出しの仕組み（論文 1 の `kit/export/` の使い回しは別に決める）
- 論文の本文（3.2・S2 は照合の後）
- GSE 本体（`src-tauri/`）の変更

## 受け入れ条件

- [ ] 書き直しの実装が GSE のコード・パス・名前を参照しない（`papers/README.md` の規約）
- [ ] 合成の selftest が通り、変異で名指しの検査が赤になる
- [ ] CoAuthor の全セッション・CS1 2021 の全課題で、記号の列が replay の `obs` と完全一致する（不一致 0）。不一致があれば原因を記録して止める
- [ ] 書き手ごとの値・記録を repo に入れない（一致の件数だけ）

## 関連ドキュメント

- `papers/README.md`（公開物の書き方）
- `experiments/20261103-coauthor-per-person/scripts/build_obs.py`・`experiments/20261104-coauthor-ml-improve/scripts/build_cs1_obs.py`

## 運用メモ
- /reimagine 適用: Yes（書き直しの言語と範囲〔変換から書くか・replay の 2 回の通りをどう再現するか〕に複数案がある。私の判断）
