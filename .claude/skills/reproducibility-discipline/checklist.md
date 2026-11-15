# 再現性チェックリスト（詳細）

SSOT: `docs/experiment-tracking.md`。実験のたびに本リストを `notes.md` に貼って埋める。

## 実験開始前 (pre-flight)

- [ ] `experiments/<YYYYMMDD>-<exp-name>/` を作成した（`.steering/` ではない）
- [ ] **仮説を先に書いた**: 検証する `research-positioning.md` §4.1 の H?（または事前登録の項目番号）と、該当 `preregistration-v0.3.md` の PreReg 番号
- [ ] `config.(yaml|json)` に全ハイパーパラメータを列挙した（HMM 閾値 / α / β / ゲート定数 / merge-gap 等）
- [ ] ランダム要素（プローブ時点抽選など）があれば `SEED` を固定した
- [ ] `data.md` に入力 NDJSON の出所を固定した（gse-dataset の commit hash、被験者 ID、OS）
- [ ] `env.md` に環境を固定した（Cargo.lock の hash / rustc version / OS、Python 使用時は requirements.txt）
- [ ] `HMM_VERSION` を config に明記した（現行 engine と一致するか確認）

## 実行 (run)

- [ ] `run.sh` に再現コマンドを 1 つ書いた（`gse-replay --calibration` / `gse-cohort` / `run-calibration-cohort.sh`）
- [ ] 出力を `results/` に保存した（calib.json / cohort.json / segments.txt 等）
- [ ] 主要指標を `metrics.json` に抽出した（gse-dataset の `metrics/P*/<os>/` 共有値と同一）

## 実験終了後 (post)

- [ ] `notes.md` に所感・**設計からの逸脱**・気づきを書いた
- [ ] 結果を仮説に対応づけた（H? が支持/棄却/inconclusive のいずれか）
- [ ] `scripts/repro.sh`（または run-calibration-cohort.sh）で**他端末/後日に 1 コマンド再現**できることを確認した
- [ ] 共有するのは**集計 JSON のみ**で、キーストローク内容・生 NDJSON を含めていないことを確認した（data-privacy）
- [ ] HMM 挙動を変えた実験なら、`HMM_VERSION` bump とゴールデン再生成を `.steering/` に記録した

## よくある違反

- ❌ 実験ログを `.steering/` に置く → `experiments/` に置く
- ❌ 「だいたい同じ設定で回した」→ config を残さず再現不能
- ❌ 生 NDJSON を実験ディレクトリにコミット → gse-dataset commit hash 参照に置換
- ❌ 仮説リンクなしで結果だけ残す → 何を検証したか後で不明
