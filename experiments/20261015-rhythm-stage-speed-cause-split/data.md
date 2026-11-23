# data —— 揺れの world の `res=sub` の赤の原因の切り分け

- 入力は合成の列だけ（実在の人の打鍵は使わない）。揺れの world の c100・c200 の本番の P の列（seed 20261020・P 240）を、揺れの world の計器（`../20261014-rhythm-stage-speed-confound-world/` の `config.json`・`scripts/gen_sessions.py`・`scripts/replay_all.py`）で作り直す（design §1.1）。スモークは seed 20261022・P 12。
- 生成した NDJSON・ラベル・秒ごとの特徴は `work-<段>-<mode>/`（git の外）に置き、回し終えたら消す。コミットするのは `results/<段>/main/` の集計した JSON（`split.json`・`reproduce.json`・`provenance.json`・`capabilities.json`）だけ。スモークの結果は git の外。
- 照合の門（design §1.5）は、揺れの world の `results/<段>/main/e13.json`（SHA-256 を `config.json` で固定）と比べる。
- NDJSON の生ログ（合成も）・キーストロークの内容を外部の LLM（Codex を含む）に送らない。
