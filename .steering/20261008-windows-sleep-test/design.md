# 設計

- 機: Surface Pro 8（モダンスタンバイ S0 のみ・S3 なし）。
- 配布物: Drive の `O1_実施用_Windows.zip`（v0.1.40）。SHA-256 と展開後のバイト一致を確かめてから使う。
- 判定: `win_sleep_check.py` の snapshot / check。読むのは NDJSON の行の種類と時刻、アプリのログ、イベントログ、プロセスだけで、記録の中身は読まない。復帰後の行の種類ごとの数と `hook_health` の数値は、check の後に別に数えた（どちらも打鍵の内容を含まない）。
- 結果: `result.md`。
