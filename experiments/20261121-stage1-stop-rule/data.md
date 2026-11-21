# 入力

- 自己検査: 合成の記録だけ（`scripts/selftest.py` が作る）。人の記録を使わない。
- 本人の段 1 の記録（探索・ADR-043 D3）: 記録は repo にも gse-dataset にも置かない。置き場は GSE の既定のセッションのディレクトリで、`prepare_records.py` が最初の `meta` の `s1_mode` で選ぶ。回したら、回した日と、使った記録の数だけをここに書く（ファイル名・SHA-256 の一覧は repo に入れない）。
