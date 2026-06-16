# 設計 v2 — Task D「オフライン解析 gse-replay 拡張」

> /reimagine で requirement.md のみから再生成した案。

## アプローチ

NDJSON を読む較正解析を `gse-replay` の新モード `--calibration` として足す。
解析の純ロジックは新規 `src-tauri/src/analysis/calibration_eval.rs`(OS 非依存)に閉じ、
replay.rs は「NDJSON から型付き列を抽出 → calibration_eval に渡す → 結果を JSON 出力」の配線に徹する。
v0.2 流の `metrics.rs`(confusion/precision/recall)は再利用せず、C-index 系の独立パスを新設する。

**設計原則: 既存 replay.rs の `collect_*` イディオムに完全に乗る。**
既存の `--metrics` 経路は `collect_user_labels()` + `collect_logged_feats()` を合成して
`compute_session_metrics()` に渡す形をとる。`--calibration` も同様に、
新しい型別コレクタ `collect_realtime_labels()` / `collect_probe_assignments()` /
`collect_session_meta()` / `collect_vignette_responses()` を足し、既存 `collect_logged_feats()`
(X/Y の源)と合成して `compute_calibration_metrics()` に渡す。
→ 合成型 (SessionData 等) を新たに発明せず、各コレクタが独立に単体テスト可能。NDJSON を
複数回走査するが、これは既存 `--metrics`/`--segment` 経路と同じ前提 (MAX_SESSION_BYTES ガード内)。

## 単一被験者・複数セッション CLI (重要な設計)

scope(3)「被験者内 C-index + 前向き holdout(最初の2で較正→残りで評価)」を
**CLI で実行可能にする**。`--calibration` は **1 被験者の複数セッション NDJSON を可変長で受ける**:

```
gse-replay --calibration s1.ndjson s2.ndjson s3.ndjson ... [--json]
```

ファイル順 = セッション時刻順(較正 2 + 評価 N)。これにより被験者内 C-index と holdout 分割を
合成 NDJSON 群で **end-to-end 決定論的に検証**できる(受け入れ条件の golden test を CLI で満たす)。
被験者**横断**のモデルゲート(中央値≥0.65 & 全員>0.55 等「全員/2人以上」判定)は複数被験者が必要で
単一 invocation では完結しないため、`model_gate()` を純関数として実装し合成多被験者データで unit test。
実データの多被験者オーケストレーション(P000/P001/... ディレクトリ走査)は Task E。

## 変更対象

### 新規作成
- `src-tauri/src/analysis/calibration_eval.rs` — 較正解析の純関数 + Serialize 結果型。
- `src-tauri/tests/fixtures/calib_subject_*.ndjson` — 1 被験者ぶんの合成セッション群
  (既知 X 系列 × realtime_label で C-index/holdout/MNAR/ビネットの数値を決定論固定)。

### 修正
- `src-tauri/src/analysis/mod.rs` — `pub mod calibration_eval;`。
- `src-tauri/src/bin/replay.rs`:
  - `ReplayEvent` に 4 variant 追加(SessionMeta / ProbeAssignment / RealtimeLabel / VignetteResponse)。
    `#[serde(tag="type")]` のフィールド名は NDJSON 実形式に一致(`ts`/`probe_id`/`q1_friction`/
    `q2_progress`/`answered`/`skip_reason`/`latency_ms`/`analysis_window_start_ms`/`_end_ms`/
    `source`/`scheduled_ts`/`session_elapsed_ms`/`expected_quadrant`/`vignette_id`/`track`/`task_kind`)。
  - 網羅 match 更新: `timestamp()` と `run_replay()` の `match ev`(snapshot 経路では読み飛ばし)。
  - 新コレクタ群 `collect_realtime_labels` / `collect_probe_assignments` / `collect_session_meta` /
    `collect_vignette_responses`(既存 collect_* と同形・silent skip 可視化・サイズガード踏襲)。
  - `Args` に `calibration: bool` + 可変長 positional 対応。`parse_args` の mode_count 排他配列に追加・
    `--json` 有効条件に追加。`--calibration` 時のみ複数 positional を許す(他モードは従来どおり 1 個)。
  - main に `--calibration` 分岐: 各ファイルを collect → `compute_calibration_metrics()` → pretty/JSON。
- docs(architecture / repository-structure / functional-design / glossary)に較正解析を追記。

### 不変
- `schema_dto.rs` / `schema/current.json`(A 凍結・parity guard 回避)・`metrics.rs`(流用禁止)・
  既存 `--snapshot`/`--metrics`/`--segment`/`--segments`/`--intervention` 経路。

## 中核アルゴリズム

### 窓集約 (scope 2)
realtime_label の `[analysis_window_start_ms, analysis_window_end_ms]`(= t−31s..t−1s。probe 後 t..t+60s は
使わない D-8)に入る FeatSnapshot を集め X/Y を集約。
集約は `AggSpec { source: AggSource, stat: AggStat }` で**差し替え可能**にし、将来の感度比較に備える。
`AggSource = { Ewma, Raw }`, `AggStat = { Median, Mean, Tail }`。
- **既定(ユーザー確定 2026-06-17): `AggSpec { source: Ewma, stat: Median }`**。
  理由: X 源 = ewma_x/ewma_y はデプロイ系が実際に表示・行動に使うモデル出力で、PreReg-4 の「モデル検証」対象
  として正当(系が使わない raw_x を検証しても運用妥当性に直結しない)。統計量 = 中央値は窓内の過渡スパイクに
  頑健。「モデル出力の正当性(ewma)」と「頑健性(median)」の折衷。
- 窓内 feat が 0 件(全沈黙でエンジン pause)の観測のみ C-index ペアから除外(回答率には算入)。
  MIN_WINDOW_FEATS の閾値ノブは置かない(1 件以上あれば集約)。C-index は probe 間の単調順序のみを使うため、
  集約法の違いは「probe 間 X 順位」を変えた時だけ効き影響は限定的(だからこそ AggSpec で切替可能にしておく)。

### 方向付き C-index (scope 3)
`concordance_index(pairs: &[(x: f64, q: u8)]) -> Option<f64>`: `q_i != q_j` の比較可能ペアのみを母数に、
`(x_i−x_j)` と `(q_i−q_j)` の符号一致 concordant=1.0 / 逆=0.0 / `x` タイ=0.5(AUC/Harrell C 流)。
0.5=偶然 / 1.0=完全 / <0.5=逆(方向を内包)。比較可能ペア 0 なら None。
**X↔Q1(摩擦)と Y↔Q2(前進)を両方算出して併報**。scope(3) が「X と Q1 の順位一致割合」と明示するため、
ゲート駆動はあくまで**軸別ランク concordance**(2D 象限 concordance は発明しない=スコープ厳守)。
**ゲート指標 = X↔Q1**(GSE 主構成概念=摩擦)、Y↔Q2 は secondary 併報。

### 前向き holdout (scope 3, §8)
`prospective_holdout(sessions)`: 時刻順先頭 2 = 較正(C-index から除外)・残り = 評価。
被験者内 C-index は評価セッションの観測のみで算出。<3 セッションは評価集合空 → C-index 算出不能。
※ X は記録済み値を使い再計算しない。「β 凍結」は評価設計上のセッション分割として実装(実 β 再較正なし=範囲外)。

### 2段ゲート (scope 4)
- 測定法ゲート: 回答率≥80%(全体)/2人以上<70%=Kill、latency 中央値≤10s、有効≥20件/人、
  ビネット PreReg-1 通過。失敗 → モデルゲートに進まない。
- モデルゲート(測定法通過時のみ・被験者横断): 各人 C-index 中央値集合に
  中央値≥0.65 & 全員>0.55=Go / 中央値≤0.55 or 2人以上≤0.50=Kill / 他=INCONCLUSIVE。

### MNAR 上下限 (scope 5)
未回答(skip/dont_remember/無応答)は窓 X を持つが q なし。q=5(全高)と q=1(全低)を代入して X↔Q1 C-index を
再計算 → `[lower, upper]` 併報。除外しない。無回答率 >20% 注意 / >30% 主分析不成立。中間値 3 代用しない。

### ビネット採点 (scope 6) / 二軸性 / Recall / track
- ビネット: `infer_quadrant(q1,q2)`(端 1-2/4-5 のみ採用・3 は不一致。flow=低摩擦高前進 / stuck=高摩擦低前進 /
  incubation=高摩擦高前進 / idle=低摩擦低前進)→ expected 一致数。6/8 で個人通過・被験者 80% で PreReg-1 合格。
  frontend `inferQuadrant` と同一規則(権威採点は Task D)。
- 二軸性(報告併走): realtime_label の (q1,q2) 象限分布。非対角(incubation 中心)<10% で「検証不能」。
- Recall: 点推定を出さない。`recall:{reported:false, positive_episode_count, reason}` のみ。分母=一様ランダムプローブ。
- track: `session_meta.track==exploratory` はゲートに混ぜない(main のみ)。

## 出力 (scope 7)
`compute_calibration_metrics(sessions) -> CalibrationReport`(Serialize)を `--calibration --json` で出力。
被験者内 C-index(X↔Q1/Y↔Q2)・holdout 内訳・測定法ゲート統計・MNAR 上下限・ビネット採点・二軸性・
Recall(withheld)を含む。集計値と中央値のみ・個人情報なし(§10)。
`gse-dataset/metrics/P000/<os>/*.metrics.json` に置く。

## 既存パターンとの整合
- replay.rs の `collect_*` 多パス + `compute_*` + `format_*_pretty` を完全踏襲(--metrics と対称)。
- ReplayEvent variant 追加・読み飛ばしは ImeShadow/InterventionDecision と同型。
- サイズガード・silent skip warn・mode 排他チェックを踏襲。新 crate 不要(std + serde)。

## テスト戦略
- 単体(calibration_eval): concordance(完全/逆/偶然/タイ)・2段ゲート境界・MNAR 上下限・ビネット・
  象限推論・holdout 分割・track 隔離・被験者横断モデルゲート(合成多被験者 in-code)。
- 統合(replay): 合成 `calib_subject_*.ndjson` 群を `--calibration s1 s2 s3` で通し、抽出→窓集約→
  被験者内 C-index→holdout→MNAR→ビネット→JSON を end-to-end 決定論検証。
- 回帰: `--snapshot tests/snapshots/minimal.json` 緑(variant 追加は FeatSnapshot 列に無影響)。
  `cargo test --workspace`/`cargo clippy` 緑。emit_schema 差分なし。

## ロールバック計画
新規モジュール + 新モード + 新 fixture。既存への影響は ReplayEvent match 2 箇所 + parse_args の可変長対応のみ。
問題時は calibration_eval.rs 削除 + replay.rs 追加分 revert で完全復帰。

## テスト戦略 / 実装アプローチの理由
可変長 CLI により被験者内 C-index/holdout を「合成 fixture で決定論検証」する受け入れ条件を unit test 依存に
せず CLI 経路で満たせる。`collect_*` 踏襲でコードベース一貫性とコレクタ単体テスト容易性を確保する。

## 設計判断の履歴
- 実行回数: 1 回目
- 採用: **ハイブリッド(v2 ベース)**
- 根拠(ユーザー判断 2026-06-17):
  - 設計案 = v2 ベース ハイブリッド。v2 の `collect_*` 多パス踏襲(コードベース一貫性・コレクタ単体テスト容易)と
    可変長 CLI(被験者内 C-index/holdout を CLI 経路の合成 fixture で決定論検証=受け入れ条件を直接充足)を採用。
    集約は AggSpec で差し替え可能化し、既定値のみ確定。
  - 設計判断 A(窓集約)= **ewma の中央値**を既定に確定(モデル出力の運用妥当性 + 中央値の頑健性の折衷)。
  - 設計判断 B(C-index ペアリング)= scope(3) で実質確定・両案一致(軸別 concordance、ゲート=X↔Q1、Y↔Q2 併報)。
