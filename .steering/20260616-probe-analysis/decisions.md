# decisions.md — Task D「オフライン解析 gse-replay 拡張」

## DD-1 ブランチは main でなく feature/probe-collect から分岐 (2026-06-17 ユーザー承認)
- **判断**: handoff は「main から feature/probe-analysis を分岐」を指示していたが、現作業ツリーに
  39 個の uncommitted infra 変更 (Codex bridge・hooks・/cross-review 等、workflow 実行に必要) があり、
  うち docs/architecture.md・glossary.md が main と衝突して clean switch がブロックされた。
  → `feature/probe-collect` (A+B+C) から `feature/probe-analysis` を分岐。
- **根拠**: D は NDJSON 解析のみで B/C ランタイム非依存・schema は A 凍結で足りるため correctness は不変。
  D を C にスタックするのは A→(B∥C)→D→E のマージ順と一致 (B/C 先行マージ後に D の対 main diff はクリーン)。
  handoff の「main から」はクリーンツリー前提で書かれ infra 状態を想定していなかった (AskUserQuestion で確認)。

## DD-2 設計は v2 ハイブリッド (collect_* 多パス + 可変長 CLI)・集約は AggSpec で差替可能
- **判断**: /reimagine で v1(単一パス合成型・単一セッション CLI) と v2(既存 collect_* 踏襲・1被験者可変長 CLI)
  を比較し、**v2 ベース ハイブリッド**を採用 (2026-06-17 ユーザー判断)。
- **根拠**: (a) `collect_*` 踏襲はコードベース一貫性 (--metrics と対称)・コレクタ単体テスト容易。
  (b) 可変長 CLI (`--calibration s1 s2 s3`) で被験者内 C-index/holdout を CLI 経路の合成 fixture で
  決定論検証でき、受け入れ条件を unit test 依存にしない。実装は単一パス collector + 既存
  `collect_logged_feats` 再利用 (計2パス) に落とした (型別 4 コレクタは小レコードなので 1 パスに統合)。

## DD-3 設計判断 A (窓集約) = ewma の中央値 (差替可能・既定確定)
- **判断**: `AggSpec { source, stat }` で差替可能化し、既定を `{ Ewma, Median }` に確定 (2026-06-17 ユーザー判断)。
- **根拠**: X 源 = ewma_x はデプロイ系が実際に表示・行動に使うモデル出力で PreReg-4「モデル検証」の対象として
  正当 (raw_x は系が使わない)。中央値は窓内過渡スパイクに頑健。C-index は probe 間順序のみ使うため集約法の
  影響は限定的だが、将来の感度比較のため AggSource{Ewma,Raw}/AggStat{Median,Mean,Tail} を残す。
- 窓内 feat 0 件 (全沈黙) の観測のみ C-index ペアから除外 (回答率には算入)。MIN_WINDOW_FEATS 閾値は置かない。

## DD-4 設計判断 B (C-index ペアリング) = X↔Q1 主・Y↔Q2 secondary (scope 確定)
- **判断**: scope(3)「X と Q1 の順位一致割合」に従い**軸別ランク concordance**を採用 (2D 象限 concordance は発明しない)。
  ゲート駆動 = X↔Q1 (GSE 主構成概念=摩擦)、Y↔Q2 は併報。両案一致のためスコープで確定。

## DD-5 CLI は 1 被験者・被験者横断ゲートは純関数 + unit test (実データ評価は Task E)
- **判断**: `--calibration` は 1 被験者の複数セッションを受け被験者内 C-index/holdout/測定法統計/MNAR/
  ビネット/二軸性を算出。被験者**横断**の最終ゲート (`model_gate`/`measurement_gate`) は複数被験者が必要なため
  純関数として実装し合成多被験者データで golden test。実データ多被験者オーケストレーション (P000/.. 走査) は E。
- **根拠**: handoff「holdout の β 凍結ロジックまで実装・実データ multi-session 評価は E」。
  NDJSON 1 ファイル = 1 セッションで subject/session 番号は gse-dataset のディレクトリ構造が持つ。
- **β 再較正は行わない**: 記録済み feat の X をそのまま使い、「β 凍結」は評価設計上のセッション分割として実装。

## DD-6 MNAR の母数は「窓 X を持つ random_probe」に統一 (cross-review/code-reviewer HIGH 対応)
- **判断**: `compute_mnar_bounds` の no_answer_rate/caution/invalid と上下限計算の母数を、ともに
  `x_friction.is_some()` の random_probe に統一。
- **根拠**: 上下限の感度分析は窓 X がある probe でしか計算できない。母数が「X 無しを含む」のに上下限だけ
  「X 有り」だと、バウンドに寄与しない probe で欠測フラグが立つ非対称が生じる。PreReg-7 の無回答率は
  感度分析の対象母集団で定義する。

## DD-7 二軸性は holdout 評価集合でなく main 全体で集計 (記述統計・報告併走)
- **判断**: PreReg-8 二軸性 (象限分布・非対角<10% で検証不能) は「自然データ」の分布なので、較正/評価の
  holdout 分割とは独立に main 全セッションで集計する。モデルゲートの判定には用いない (記述統計)。
- **根拠**: PreReg-8 は「自然データで非対角象限の出現が<10%」と定義し holdout 限定ではない。コメントで明示。

## DD-8 Recall の positive_episode_count = Stuck 象限の主観陽性数 (code-reviewer MEDIUM 対応)
- **判断**: 点推定は出さない (PreReg-6) が、withhold の根拠となる「独立陽性エピソード数」を
  「一様ランダムプローブのうち (q1,q2) が Stuck 象限 (高摩擦・低前進) の回答数」と定義。
- **根拠**: 旧実装 `min(assignment 件数, answered)` は意味が曖昧で `.max(0)` が死にコードだった。
  分母=一様ランダムプローブ・陽性=主観 Stuck の honest な定義に置換。

## DD-9 reader 側 q1/q2 範囲再検証 + 較正ファイル数上限 (security-checker MEDIUM 対応)
- **判断**: `load_calibration_session` で回答済み realtime_label / vignette の q1/q2 を `1..=5` 再検証し
  範囲外は件数のみ warn で skip (producer は clamp するが reader は信頼しない)。
  `--calibration` のファイル数は `MAX_CALIBRATION_FILES=64` で上限を設ける (500MB×数×2パスの暴走防止)。
  `median_u64` の偶数ケースを overflow-safe 計算に変更。

## 受容 (根拠付き)
- **N×2 パス**: load_calibration_session が 4 type 抽出で 1 パス + collect_logged_feats で feat に 1 パス。
  --metrics 経路と同じ前提・MAX_SESSION_BYTES 内で実害小。将来 1 パス化は Task E で検討。
- **median 系ヘルパの局所重複** (metrics.rs と): analysis 内局所重複は許容。共通 stats 切り出しは Task E 検討。
- **プライバシー (security-checker クリーン)**: CalibrationReport/pretty/metrics.json は集計値・中央値・カウント・
  象限分布・真偽フラグのみ。probe_id/vignette_id/task_kind は parse のみで破棄し出力・ログに ID/本文は到達しない (§10)。
