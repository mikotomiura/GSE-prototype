# 段 1 の区間の再標本化の手順（S1-E5）を模擬の被覆で選ぶ

- 何を: 較正の切片と傾きの区間の作り方とブロックの長さの 9 通りを、段 1 に近い日の揺れの模擬（36 点・各 400 回）の被覆で比べ、`conditions.md` K3 の規則で 1 つを選ぶ。
- データ: すべて合成。O1 と段 1 の記録は使わない。HMM_VERSION・gse-dataset は当たらない。
- 再現: `bash run.sh`（`OUT` で出力先を変えられる）。
- 出力: `results/coverage.json`・`results/provenance.json`。
- 結果と読み: `notes.md`。作業記録: `.steering/20261121-stage1-prereg-values-and-stop-rule/` 判断 32。
