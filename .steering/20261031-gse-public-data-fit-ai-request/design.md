# 設計

## アプローチ

1. 3 データの利用条件と出来事の種類をサブエージェント 3 本の並列で調べ、決め手の主張をメインが一次で照合する（`survey-datasets.md`）。
2. 研究者の判断（`decisions.md` 判断 1〜4）を受け、解析の条件を `experiments/20261031-coauthor-pre-request-signal/conditions.md` に書き、変換・解析のコードと一緒に計算の前にコミットする。
3. CoAuthor の jsonl を本文の無い GSE の NDJSON（時刻とキーの種類だけ）へ変換し、`gse-replay`（既定と `--features`）で 1 Hz の推定と停滞の始まりを出す。
4. 要求の時刻と対照の時刻で信号を比べ、書き手ごとの AUC を出す。
5. 感度（dwell 60/140 ms）。結果を notes.md に言える範囲を限って書く。

## 変更対象

- 新規: `experiments/20261031-coauthor-pre-request-signal/`（conditions.md・data.md・run.sh・SEED・scripts/・results/・notes.md）
- 新規: 本タスクの `.steering/`
- コード（`src-tauri/`）は変えない。

## テスト戦略

- 変換: 1 セッションで key 行が本文を含まないこと・押下の時刻を動かさないことを確かめる。
- 解析: 1 セッションで走ること（AUC は見ない）。
- 結果の検算: 標本の数（counts.json）を AUC より先に記録する。
