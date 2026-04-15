# Decisions — Phase 1 Task 2: Metrics 算出エンジン

## D1: `FeatSnapshot` の配置は現状維持（移動しない）

### 背景
design.md §Open 点: `FeatSnapshot` が `bin/replay.rs` 由来か `analysis/loop_step.rs` 由来か曖昧だった。

### 決着
実装時に確認した結果 `FeatSnapshot` は既に `src-tauri/src/analysis/loop_step.rs:126` で `pub struct` として定義済み。`analysis::metrics` から `use crate::analysis::loop_step::FeatSnapshot` で直接参照でき、型の追加移動は不要。`bin/replay.rs` も同じ型を import して使っている。

### 影響
- `analysis/snapshot.rs` 新設は却下（同じ型の二重定義を避ける）
- `analysis::metrics` は `analysis::loop_step::FeatSnapshot` に構造的依存を持つ（許容: loop_step も `analysis/` 内、レイヤー違反なし）

## D2: HMM argmax のタイブレークは Flow > Incubation > Stuck

### 背景
`[p_flow, p_inc, p_stuck]` の同率（稀だが境界値合成ケースで発生）での推定クラス決定が未定義だった。

### 決着
`argmax_class()` で Flow > Incubation > Stuck の固定順に決定。初期化直後 `[1/3, 1/3, 1/3]` を Flow に寄せることで「不明時はベストケース寄り」の直感と一致させる。テストは `f.p_flow >= f.p_inc && f.p_flow >= f.p_stuck` で Flow を優先する形で表現。

### 代替案
- ランダム化: 再現性を失うので却下
- Stuck 優先: 未発火時に介入レベルを上げる方向は望ましくない

## D3: リード/ラグ時間の定義は「同クラス argmax の最初の時刻」

### 背景
design.md §Open 点: 「同じクラスが出た最初の時刻」と「確率が 0.5 を超えた最初の時刻」のどちらを採るか未確定。

### 決着
初期実装は **argmax 方式**（±60 秒窓内で同クラスが argmax となる最初の FeatSnapshot）。理由: Incubation のように単独で 0.5 を超えにくいクラスでも評価できる。`p > 0.5` 方式は Incubation で測れないケースが多い。

### 符号の定義
`feat_ts < label_ts` のとき「HMM が先行」＝正の値。実装は `label_ts - feat_ts` で計算し、pretty-print で `{:+} ms  (positive = HMM leads user)` と明示する。

### 見直し条件
実データで中央値が常時 +60s 近傍に貼り付く等、窓の端に寄る現象が見えたら `p > 0.5` 方式に切替または両方を出すよう拡張。運用メモは `baseline_metrics.md` の「観察メモ」で収集。

## D4: NDJSON を 2 度読む（UserLabel 抽出を別経路化）

### 背景
`run_replay` は `FeatSnapshot` 列の生成専用で、UserLabel はゲート進行と無関係のため読み飛ばしていた。metrics 算出で UserLabel が必要になったが、`run_replay` のシグネチャ変更（戻り値を複合型に）は既存 `--snapshot` 経路への波及が大きい。

### 決着
`collect_user_labels(session_path)` を `main()` から `--metrics` 経路でのみ呼び出す。ファイルは 2 回開くが、`MAX_SESSION_BYTES = 500 MB` ガード既存 + 通常セッションは数 MB のため実害なし。逆に `run_replay` の変更影響が 0 行で済む利点が大きい。

### 代替案（却下）
- `run_replay` の戻り値を `(Vec<FeatSnapshot>, Vec<UserLabelEvent>)` に変更: 既存呼び出し箇所 + テスト 8 ファイルへ波及、`--snapshot` 経路に無駄な Vec 構築を強いる
- `ReplayEvent` をそのまま返す: 読み手責務の転嫁、API 境界が悪化

## D5: `--json` は `--metrics` 併用時のみ有効

### 背景
既定の `gse-replay <session.ndjson>` は `FeatSnapshot` 列を JSON で stdout に出すので、`--json` が「metrics JSON」か「snapshot JSON」かあいまいになる。

### 決着
`--json` は `--metrics` 専用フラグ扱い。`--json` 単独指定は Usage エラーで exit 2。既定経路は従来どおり pretty JSON を吐く（互換性維持）。

## D6: macro F1 は固定分母 3 (scikit-learn 互換)

### 背景
初版は `support > 0` のクラスのみで平均していた。code-reviewer MEDIUM 指摘: scikit-learn 標準の macro F1 は欠損クラスも 0 として固定分母で平均する。セッション間比較時に分母が変動すると `baseline_metrics.md` 集計での傾向解釈が困難。

### 決着
`macro_f1 = sum(per_class[i].f1 for i in 0..3) / 3.0` に統一。support=0 のクラスは `per_class_metrics()` が `precision=recall=f1=0.0` を返すのでそのまま加算される。

### 影響
- 支配的クラスのみが現れるセッションでは macro F1 が低めに出る（sklearn と同じ挙動）
- ドキュメント: decisions.md (本項) + コード doc コメント

## D7: micro F1 の分母はマッチしたラベル数のみ

### 背景
`nearest_feat` が None を返した (±1s 窓に FeatSnapshot が無かった) ラベルは混同行列に計上されず warnings 行き。結果 micro F1 = accuracy の分母が `total_labels` と乖離する。

### 決着
実装は変更せず、`compute_micro_f1` の doc コメントに明記:
- 分母 = 混同行列合計 = matched labels のみ
- warnings で未マッチ件数を可視化、`baseline_metrics.md` で併記して判断

## D8: median の偶数件数時はオーバーフロー回避パターン

### 背景
`(a + b) / 2` は i64/u64 で理論上オーバーフロー可能（code-reviewer MEDIUM）。

### 決着
- u64 版: `a + (b - a) / 2`（sort 後 a<=b 保証、(b-a) も a+... も u64 範囲内）
- i64 版: `i128` 経由で `(a + b) / 2` を計算してから i64 キャスト（両端 i64::MIN / i64::MAX 両立時も安全）

## D9: detection_lead_ms を「最近傍の同クラス feat」に再定義

### 背景
初版は `find()` で窓内の先頭ヒット (最小 timestamp) を拾っていた。2026-04-15 の初回実機セッション (`gse_20260415_080214.ndjson`) で metrics 算出したところ lead 中央値が +50,174 ms と窓端 (±60 秒) 付近に貼り付き、code-reviewer M1 で指摘。

### 症状
ラベル時刻から遠い偶発的な同クラス出現を拾うため、ラベル付近の真の lead/lag を反映しない。Phase 2a の baseline 比較で歪んだ基準値を使う危険あり。

### 決着
`min_by_key(abs_diff(f.timestamp, label.timestamp))` に変更。ラベル時刻に最も近い同クラス feat を選ぶ。回帰テスト `detection_lead_picks_nearest_not_first` を追加し、窓内 3 点のうち最近傍 (abs_diff=200) を選ぶことを担保。

### 影響
- 初回実機データの lead 中央値は再算出で大きく改善する見込み (baseline_metrics.md で記録)
- M1 指摘解消、Phase 2a の Go/No-Go 判断基準が信頼できる数値になる

## D6: タスクリスト項目のうち実装規模に照らして省略したもの

- **D-M1 / D-M2 (docs/README 更新)**: 実施済み（development-guidelines.md §3、README.md / README.ja.md のリプレイ CLI セクションに `--metrics` サンプル追加）
- **ClassMetrics の ordering in per_class**: [Flow, Incubation, Stuck] の順で `per_class[0..2]` に並べる固定配列。`LabelClass::index()` と整合。

## レビューサマリ

運用フローの順序:
1. 本文書で設計確定 → 2. `code-reviewer` 並列実行 → 3. HIGH 対応 → 4. commit
