# 次セッション開始プロンプト（Phase1 較正データ分析 / experiments トラック）

このタスクは **データ収集後に新しいセッションで実行**する。下の「===」以下をそのままコピペして開始する。
これは実装(.steering)ではなく **experiments / 再現性トラック**の作業。コード変更が要る結論
（HMM 再チューニング / UX 改修）が出た時だけ、別途 `/start-task` で `.steering` 実装タスクに切る。

---

GSE の Phase1 較正データ分析を行う。被験者から収集した提出物(.age)を復号し、較正評価パイプラインで
GATE2(測定)/GATE3(モデル)を判定し、再現可能な形で記録する。コード変更が要る結論(HMM 再チューニング/
UX 改修)が出た時だけ、別途 /start-task で .steering 実装タスクに切る。

## まず読む（着手前・順守）
1. Skill: `reproducibility-discipline`(必須・実験規約SSOT) / `data-privacy`(復号・PII・外部送信禁止/必須) /
   `hmm-analysis`・`ml-workflow`(model_gate が Kill/Inconclusive で再チューニング判断する時)。
2. docs: `docs/experiment-tracking.md`(再現性SSOT) / `docs/development-guidelines.md` §3(Replay-as-Truth)・§10(データ) /
   `docs/calibration-smoke-runbook.md`(あれば) / `scripts/run-calibration-cohort.sh` のヘッダ。
3. メモリ: 提出/配布(`build-ci-and-pilot-distribution`) と 較正収量(`pilot-calibration-label-yield-gap`)。

## ゴール
収集済み `.age` を全件復号 → gse-dataset の `raw/P###/` レイアウトへ被験者別に配置 →
`scripts/run-calibration-cohort.sh` で per-被験者 `*.calib.json`(C-index・回答率・latency・有効件数) と
コホート判定(Go/Kill/INCONCLUSIVE/DataInsufficient) を生成 → 判定と次アクションを
`experiments/<YYYYMMDD>-phase1-calibration-analysis/` に再現可能な形で記録する。

## 凍結ゲート閾値（calibration_eval.rs。実装と一致させる・再実装しない）
- 測定(GATE2): 全体回答率 ≥0.80、被験者<0.70 が2人以上で Kill。有効プローブ ≥20件/人(VALID_PROBES_MIN)、
  回答中央 latency ≤10s は被験者ごと要件。20件は1人の累積(複数セッションを同一IDで束ねる)。
- モデル(GATE3): C-index 中央 ≥0.65 かつ全員 >0.55 = Go / 中央 ≤0.55 または ≤0.50 が2人以上 = Kill / 他 = INCONCLUSIVE。
- 有効<20/人 や 人数不足は Kill ではなく DataInsufficient（=収集継続。確証データにならない）。

## 手順
1. まず1-2人ぶんで**ドライラン**: `.age` を `gse-unpack --input <f> --identity ~/.gse/age-identity.txt --out <dir>` で
   復号(復号鍵は repo 外・秘密)、匿名化健全性(vk生値0・本文/題名漏れ0・時刻相対化)を確認。
   `run-calibration-cohort.sh --dry-run` → `--no-cohort` でパイプラインが匿名化済 NDJSON で通るか確認。
   - **task_kind フィルタ（必須）**: 各セッションの `session_meta.task_kind` を確認し、**論述 (argumentative) 以外を
     較正評価から除外**する。task_kind ロック (`.steering/20260629-lock-task-kind-argumentative`) 以前に収集された
     データには非論述セッションが混入し得るため (混ぜると C-index がタスク種別で交絡)。除外件数を experiments に記録。
     例: `grep -L '"task_kind":"argumentative"' <decrypted>/*.ndjson` で非論述ファイルを特定し配置対象から外す。
2. 全件で `GSE_DATASET=<root> scripts/run-calibration-cohort.sh`(--os 明示)を実行し cohort 判定 JSON を得る。
3. 結果を experiments/ に記録: HMM_VERSION・Cargo.lock・入力NDJSONの件数/hash・gse-dataset commit・OS・seed を刻印し、
   1コマンド再現(repro)を残す。per-被験者の C-index/回答率/有効件数の表と、コホート verdict、収量(20件到達状況)を要約。

## 判定後の分岐（結論を experiments に明記）
- DataInsufficient → 収集継続（self-marker 教示・セッション追加で有効≥20/人を満たす。コード変更不要）。
- measurement_gate Kill → 回答率/latency 改善（教示/プローブUX）。コード変更なら /start-task で .steering 実装タスク。
- model_gate Kill/INCONCLUSIVE → HMM が当たっていない/不足。`hmm-analysis`/`ml-workflow` で再チューニング検討
  （HMM_VERSION bump → ゴールデン再生成 → 差分記録）。これは /start-task で .steering 実装タスクに切る。
- model_gate Go → confirmatory 成立。次フェーズ（介入効果検証等）の設計へ。

## 死守
- 復号鍵 `~/.gse/age-identity.txt` は秘密・repo 外。**生 NDJSON / .age を repo・gse-dataset に commit しない・外部 LLM に送らない**。
  共有してよいのは metrics/ と cohort/ の集計 JSON のみ（development-guidelines §10）。
- 被験者は**同一 ID**でセッションを束ねる（ID がブレると1人ぶんに集約されず ≥20 に届かない）。
- shakedown(リリース版pilot) と confirmatory(M0) のカットを prereg と突合し、混ぜない。
