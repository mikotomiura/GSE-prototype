# 機能設計書

## 1. プロジェクト概要

- **プロダクト名**: GSE (Generative Struggle Engine)
- **解決する課題**: 知識労働者がキーボード作業中に作業停滞へ入り、自覚なく長時間停滞し続ける問題。従来の生産性ツールは作業量の最大化を目指すが、GSE は PC 操作に現れる行動的シグナルから介入判断に必要な作業上の状態を推定し、適切なタイミングでの介入により「生産的苦闘（Productive Struggle）」を保護する。
- **ターゲットユーザー**: Windows 11 および macOS（13 Ventura 以降）上で日常的にキーボード作業を行う知識労働者（メール、企画書、ドキュメント作成、コーディング等）
- **コアバリュー**: 不便益（Fubeneki）に基づく HCI フレームワーク — あえて不便を導入することで、ユーザー自身の作業再編・休止・回復を促進する。GSE は脳内の認知状態を直接読むのではなく、行動的シグナルから Need と Opportunity を分離して介入判断を行う。

## 2. コア機能一覧

### 機能 1: キーストロークセンシング

- **概要**: OS レベルのキーボードフックにより、すべてのキー入力イベントをリアルタイム収集する
- **入力**: 物理キーボード入力（Windows: WH_KEYBOARD_LL / macOS: CGEventTap）
- **出力**: InputEvent ストリーム（vk_code, timestamp, is_press, is_repeat, is_backspace）
- **振る舞い**:
  - 専用スレッドでフックを実行し、メインスレッドをブロックしない
  - crossbeam チャネル経由で分析スレッドへイベントを送信
  - オートリピートキーを識別しフィルタリング可能にする
  - macOS: Input Monitoring 権限（kCGEventTapOptionListenOnly）を優先し、10 回連続失敗後に Accessibility 権限（kCGEventTapOptionDefault）へ自動フォールバック
  - macOS: CGKeyCode を Windows VK コードにマッピングし、analysis 層のプラットフォーム非依存性を維持
- **エラー条件**:
  - Windows フック登録失敗時: tracing::error でログ出力、アプリは起動するが推定不能状態
  - macOS TCC 権限未付与時: システム設定ダイアログを表示し、ポーリングでタップ再作成を試行
  - macOS ad-hoc 署名時: TCC CDHash 不安定のため Input Monitoring が機能しない場合あり → Accessibility フォールバック
  - チャネル満杯時: try_send でイベントをドロップ、warn ログ出力

### 機能 2: IME 状態検出

- **概要**: 日本語 IME の ON/OFF 状態および変換候補ウィンドウの表示状態を検出する
- **入力**: Windows: IME API (ImmGetOpenStatus, VK_DBE_\*, WinEvent) / macOS: CGEventTap 状態機械 + TIS (Text Input Source) ポーリング
- **出力**: IME_OPEN（日本語/英数切替）、IME_ACTIVE（候補ウィンドウ表示）のアトミックフラグ。macOS では追加で IME_COMPOSING（ローマ字→かな変換中）
- **振る舞い**:
  - Windows: 多層検出戦略 — WinEvent フック（主）→ EnumWindows（副）→ UIAutomation（補助）
  - macOS: デュアルパス検出 — Path A: JIS キーボード物理キー検出（英数/かなキー、高速 \~5ms）→ Path B: ANSI キーボード TIS ポーリング（GCD メインキュー経由、100ms 間隔）
  - macOS: CGEventTap コールバック内の状態機械でインライン変換（下線テキスト）を追跡
  - IME 状態に応じてベースラインを動的切替（coding β vs writing β）
  - IME 変換中はバックスペースペナルティを抑制
- **エラー条件**:
  - Windows: ImmGetContext が NULL → VK_DBE_\* ダーティフラグへフォールバック
  - IME_ACTIVE の検出漏れ: 8 秒安全弁で自動リセット
  - IME ポーリングスレッド起動失敗: IME 状態検出なしで継続（ベースラインは coding β 固定）
  - macOS: TIS クエリは GCD メインキュー必須（dispatch_sync_f）。メインスレッド以外から直接呼ぶと不正な結果を返す

### 機能 3: 作業状態推定（HMM ベースライン）

- **概要**: キーストローク特徴量から、介入判断に必要な作業上の停滞・摩擦・継続の兆候をリアルタイム推定する。現行 HMM の Flow / Incubation / Stuck 確率は、脳内状態の直接分類ではなく、行動シグナル由来の参考スコアとして扱う。
- **入力**: 5 つのキーストローク特徴量（F1: Flight Time, F3: Correction Rate, F4: Burst Length, F5: Pause Count, F6: Pause-After-Delete Rate）
- **出力**: {p_flow, p_incubation, p_stuck}（1Hz 更新）。MVP では `p_stuck` を Need 層の `stuck_likelihood` として利用する。
- **振る舞い**:
  - 30 秒ローリングウィンドウで特徴量を算出
  - 特徴量 → 潜在軸（X: Cognitive Friction, Y: Engagement）→ 26 観測ビンへ量子化
  - HMM Forward Algorithm で状態確率を更新
  - EWMA 平滑化 + ヒステリシス EMA で表示確率を安定化
  - サイレンス時: 合成特徴量を生成し、摩擦フロアで Stuck 侵食を防止
  - バックスペース 14 連続以上でペナルティビン（obs=25）を発火
- **エラー条件**:
  - コールドスタート: Flow 寄りの初期確率 [0.80, 0.15, 0.05] で安定起動
  - 長時間無入力: 段階的 α 調整（0.15 → 0.18 → 0.25）で緩やかに遷移

### 機能 4: Opportunity 判定 + 段階的介入

- **概要**: Need（介入が必要そうか）と Opportunity（今介入してよいか）を分離し、`InterventionDecision` に従って段階的な介入を実施する。
- **MVP 入力**: `p_stuck`, `idle_ms`, F3/F4/F6, `cooldown`, `daily_cap`, `recent_dismiss`, `Monk Mode`, Wall 累積時間
- **MVP 出力**: `none` / `nudge` / `wall` / `defer`
- **初期パラメータ**:
  - Nudge Need: `p_stuck >= 0.60`
  - Wall Need: `p_stuck >= 0.70` が累積 30 秒
  - Nudge cooldown: 10 分、daily cap: 6 回/日
  - Wall cooldown: 60 分、daily cap: 1 回/日
  - recent dismiss 抑制: 20 分
  - away idle: 180 秒以上で Wall 抑制

#### Lv1: Nudge（視覚的ヒント）
- **トリガー**: `InterventionDecision.action == "nudge"`
- **振る舞い**: オーバーレイウィンドウ右端に小さなサイドカードを表示
- **解除条件**: `InterventionDecision.action != "nudge"` で自動消失

#### Lv2: Wall（作業ブロック）
- **トリガー**: `InterventionDecision.action == "wall"`
- **振る舞い**:
  - メインウィンドウを全画面ロック
  - QR コードを表示し、スマートフォンでスキャンを促す
  - スマートフォン上で Zen Timer（2 分カウントダウン）を起動
  - タイマー完了後に手動アンロックボタンを表示
  - Early Unlock ボタンも提供（緊急時）
- **解除条件**: スマートフォンからの POST /unlock、またはキーボード長時間アイドル
- **エラー条件**:
  - Wall Server 起動失敗: ログ出力、Wall なしで継続
  - スマートフォン未接続: QR コード再表示で対応
  - 画面オートロック: navigator.wakeLock API で防止

### 機能 5: セッション管理

- **概要**: 分析セッションのライフサイクルと Opportunity policy state を管理する
- **入力**: ユーザーの「開始する」ボタン押下
- **出力**: セッション開始/終了イベント、NDJSON セッションログ
- **振る舞い**:
  - セッション開始時: HMM エンジンリセット、ロガー初期化
  - セッション中: 1Hz で作業状態スコアを更新、500ms で UI が `InterventionDecision` をポーリング
  - セッション終了時: ログファイルクローズ、Wall Server 停止
- **エラー条件**:
  - IPC 失敗時: 認知状態を安全なデフォルト値にリセット（flow=1.0, stuck=0.0）

### 機能 6: セッションログ記録

- **概要**: キーストロークイベント、作業状態スコア、介入判断を NDJSON 形式で永続化する
- **入力**: InputEvent、特徴量、IME 状態、`InterventionDecision`、セッションイベント、UserLabel (Phase 1)
- **出力**: セッションログの保存先は環境変数 `GSE_DATASET` で制御する (logger.rs `default_log_path` の 2 段優先):
  1. `GSE_DATASET` 設定時: `$GSE_DATASET/raw/P000/gse_YYYYMMDD_HHMMSS.ndjson` (開発者マシンでは `gse-dataset` リポジトリに直接書き込む運用)
  2. 未設定時 (fallback): `~/Documents/GSE-sessions/gse_YYYYMMDD_HHMMSS.ndjson`
  - どちらに解決されたかは `tracing::info!` で起動時に出力 (`resolved_log_dir`, `source`)
- **振る舞い**:
  - バウンドチャネル（512 エントリ）でバッファリング
  - バックグラウンドスレッドが 5 秒間隔でディスクにフラッシュ
  - セッション開始/終了のメタレコードで囲む
  - meta 行に `hmm_version` (SemVer) を埋め込み、gse-replay で検証
  - `intervention_decision` 行に action / need_score / opportunity_score / suppressed_by を記録し、介入しすぎ・defer・dismiss の事後分析に使う
- **将来拡張**: セッション終了後にオプトインでログを匿名化・外部送信する学習データ収集パス
- **エラー条件**:
  - ディスク書き込み失敗: ログをドロップし warn 出力、推定は継続

### 機能 7: Ground Truth (GT) ラベリング + 集計 (Phase 1)

> **v0.3 較正での位置づけ (重要・優先順位の逆転)**: v0.3 較正スモーク (D-13 以降) では、**主データ源は「ランダム時点プローブ」** (モデル出力非依存に一様ランダムな時点で Q1 摩擦 / Q2 前進を 1–5 で問う `realtime_label`) であり、本節で説明する**ホットキー方式の自覚ラベル (3 値 `user_label`) は補助データに降格**する (希少な深い Stuck を拾う self-marker 用途、Recall 分母には混ぜない)。この段階のラベルは "GT" ではなく **criterion label** と呼ぶ。詳細・preregistration は `docs/preregistration-v0.3.md` と `docs/glossary.md` を参照。
>
> **尺度理解テスト (ビネット) は現行スコープでは延期**: schema (`vignette_response`) と format 関数は実装済みだが、初回スモークの最小核スコープからは外され、比較条件を実装した段で発効する (PreReg-1/3 の扱い、`.steering/20260612-retro-labeling-and-corner-intervention/design.md` 参照)。
>
> **較正モード blind dashboard (測定独立性)**: v0.3 較正セッションの既定メイン画面は **blind/minimal** にする (`App` の `calibrationMode` state、既定 ON・Start 画面のトグルで切替)。被験者にモデル出力 (推定状態 / Flow・Incubation・Stuck 確率 / p_stuck・X/Y / GT counter / 状態色) を**一切見せない**ことで、主観回答 (criterion label) のアンカリング汚染を防ぐ。較正中に表示してよいのはセッション経過時間 / Keyboard・Hook 状態 / Monk Mode (介入状態) / 終了ボタン / 権限警告のみ。`ProbeCard`/`VignetteTest` は overlay で従来どおり動作。frontend のみの分岐 (backend/schema 不変、`cognitiveState` は取得するが非表示)。`.steering/20260617-calibration-blind-dashboard/` 参照。

- **概要**: HMM の自動推定とユーザーの主観的認知状態のズレを定量化するため、作業中にリアルタイムで「自覚しているクラス」をラベル付けし、オフラインで混同行列・F1・中央値を算出する (下記はホットキー方式の仕様。v0.3 較正の主データはプローブ方式 — 上記注記参照)
- **入力経路**:
  - **ホットキー**: macOS `⌘⇧⌥ F/I/S`、Windows/Linux `Ctrl+Shift+Alt+F/I/S`
  - **Tauri コマンド**: `record_user_label(label: "flow" | "incubation" | "stuck")`
  - 両経路とも `record_label_internal` を経由し、**`AtomicU64::compare_exchange` による race-free な 2 秒デバウンス** を適用
- **出力**:
  - NDJSON エントリ: `{"type":"user_label","t":<ms>,"label":"flow|incubation|stuck","recovered_at":null}`
  - Tauri イベント: `user_label_recorded` (payload: `{label, timestamp}`) — Dashboard counter widget が購読
- **集計 CLI (`gse-replay --metrics`)**:
  - 入力: GT 付きセッション NDJSON
  - 出力: `SessionMetrics` (混同行列 / per-class precision/recall/F1 / macro F1 / micro F1 / detection_lead_ms 中央値 / Stuck recovery 中央値)
  - `--json` フラグで構造化 JSON (gse-dataset repo の `metrics/` へ配置する共有アーティファクト)
- **振る舞い上の制約**:
  - **Production path (engine / features / hook / ime / loop_step) 無変更**: /reimagine v2 で「汚染源を発生させない」方針を採用。Task 1-3 は既存の HMM 挙動・snapshot を 1 bit も動かさない
  - `recovered_at` はログ記録時は常に `null` で、`--metrics` 実行時にオフラインで純粋関数により後付け算出 (閾値変更で過去ログを再解析可能)
- **UI**: Dashboard に読み取り専用 counter widget (`Flow N / Inc N / Stuck N` + ショートカット hint)。
  ただし **v0.3 較正モード (`calibrationMode`、既定 ON) ではこの counter・推定状態・確率バー・状態説明を非表示**にする (下記「較正モード blind dashboard」)。
- **事後レビュー方式 (Phase 1 GT 改善)**:
  - **レビューマーカー**: `⌘⇧⌥R` (macOS) / `Ctrl+Shift+Alt+R` で「後で見返したい」ブックマークを記録 (1 秒デバウンス)。NDJSON: `{"type":"review_marker","t":<ms>}`
  - **`gse-replay --segment`**: セッションをキーストローク沈黙 (≥ 5s) で自動分割し `.segments.txt` を生成。各セグメントの活動指標 (feat 数, silence, correction rate, avg FT) を表示
  - **`.segments.txt` 編集**: ユーザーがテキストエディタで各セグメントに F/I/S ラベルを記入。`*` マーカーでレビューマーカー所属セグメントをハイライト
  - **`gse-replay --segments <file>`**: 範囲マッチングで confusion matrix を構築。1 セグメント内の全 feat を評価するため、点ラベルの約 30 倍の統計検出力
  - **設計意図**: リアルタイム hotkey 方式の観察者効果 (Flow 阻害) と Stuck 自覚遅延を解消する。事後レビューにより「ここで詰まっていた」を振り返り認識で正確にラベル付けできる
- **エラー条件**:
  - デバウンス違反 (2 秒以内の再押下): `tracing::warn!("shortcut label recording failed: debounced")` で記録、ユーザーへの通知なし (意図的)
  - `record_user_label` が未知ラベル受信: `Err("invalid label: ...")` を返す (whitelist 3 値のみ許可)

### 2.x v0.3 較正解析 (`gse-replay --calibration`) — オフライン

v0.3 較正スモークで収集した criterion label (`realtime_label`) と記録済み `feat` を突き合わせ、
測定法とモデルの妥当性を**オフラインで**評価する。frontend は起動しない (NDJSON 解析のみ)。
methodology は `docs/preregistration-v0.3.md` (PreReg-1..8) と設計書 v0.3 §4.2/§6.4/§7/§8/§9/§10 に凍結。

> **実行手順 (自己ドッグフード→3-5名スモーク)**: 収集→解析→cohort 判定の運用は
> `docs/calibration-smoke-runbook.md` を参照。`scripts/run-calibration-cohort.sh` が
> `raw/P*/` → `gse-replay --calibration` → `metrics/Pxxx/<os>/*.calib.json` → `gse-cohort` を 1 コマンドで回す。

- **CLI (`gse-replay <s1.ndjson> [s2.ndjson ...] --calibration [--json]`)**:
  - 入力: **1 被験者**の複数セッション NDJSON を**時刻順**に渡す (先頭 2 = 較正・残り = 評価 = 前向き holdout §8)。
  - 出力: `CalibrationReport` (測定法統計 / 被験者内 C-index / MNAR 上下限 / ビネット採点 / 二軸性 / Recall)。
    `--json` で構造化出力 (gse-dataset の `metrics/P*/<os>/` へ置く共有アーティファクト・集計値のみ §10)。
- **算出内容**:
  - **時間隔離窓** (t−31s..t−1s): 各 `realtime_label` の `analysis_window_[start/end]_ms` 内の `feat` を集め
    X (認知摩擦) / Y (エンゲージメント) を集約 (既定: `ewma` の中央値・`AggSpec` で差替可)。probe 後窓は使わない (D-8)。
  - **方向付き 順序 C-index**: 集約 X ↔ Q1 摩擦 / Y ↔ Q2 前進 の順位一致割合 (0.5=偶然/1.0=完全/<0.5=逆)。
    評価セッションの回答済みランダムプローブのみ (§7・`|r|≥0.30` は廃止)。
  - **2段ゲート**: 測定法ゲート (回答率≥80% / latency 中央値≤10s / 有効≥20件) → モデルゲート
    (C-index 中央値≥0.65 & 全員>0.55=Go / ≤0.55 or 2人以上≤0.50=Kill / 他=INCONCLUSIVE)。被験者横断の最終判定は別途。
  - **MNAR 上下限**: 未回答を全高摩擦(5)/全低摩擦(1) と置いた C-index 範囲を併報。被験者除外しない (無回答率 >20%注意/>30%不成立)。
  - **ビネット採点** (PreReg-1): `(q1,q2)→象限推論` で expected_quadrant との一致率 (6/8 で個人通過)。
  - **Recall は点推定を出さない** (PreReg-6: 独立陽性<30件で検出力なし)。
- **振る舞い上の制約**:
  - 既存 `metrics.rs` の confusion/precision/recall は v0.2 流のため**流用しない** (D-14)。C-index 系は独立パス (`calibration_eval`)。
  - `track=exploratory` のセッションは主指標 (ゲート/C-index) に混ぜない (確証/探索の隔離 §1.3)。
  - 解析は `analysis/` に閉じ OS API を呼ばない。`schema_dto.rs` は不変 (A 凍結)。
  - 被験者**横断**の最終 Go/Kill 判定 (コホート全体) は下記 `gse-cohort` (Task E)。

### 2.x+1 v0.3 被験者横断判定 (`gse-cohort`) — オフライン (Task E)

`gse-replay --calibration` が**被験者ごと**に出力した `CalibrationReport` (per-被験者 metrics.json) を
**複数被験者ぶん集約**し、PreReg ゲートでコホート全体の Go/Kill/INCONCLUSIVE を判定する。

- **CLI (`gse-cohort <dataset-root> [--suffix <s>] [--compact]`)**:
  - 入力: `<root>/metrics/P*/<os>/*.calib.json` (既定 suffix `.calib.json`) を走査。被験者 ID = `P*` ディレクトリ名。
    **NDJSON 生ログは走査しない** (プライバシー §10)。入力は集計済み calibration レポート JSON のみ。
  - 出力: `CohortReport` (JSON) — コホート vignette/測定法/モデルゲート結果 + 最終判定 + 被験者別サマリ + notes。
- **判定 (凍結純関数 `model_gate`/`measurement_gate` を再利用・再実装しない)**:
  - **ゲート駆動 = 各被験者の C-index 中央値** (`x_q1_session_median`・PreReg-4 文言準拠)。`pooled` は参考併記。
  - モデルゲート母数 = 主指標対象 & session_median 有 & PreReg-5 充足 (eval≥6 & probe≥16/人) & PreReg-2 被験者要件充足。
  - 最終判定の優先順位 (PreReg §2): 主指標0名/提示プローブ0件→`DataInsufficient` → PreReg-1 尺度理解未達→`Inconclusive`
    → PreReg-2 測定法 Kill→`Kill` → PreReg-5 充足者0→`DataInsufficient` → モデルゲート結果。
  - **無理に Go と言わない**: PreReg-5 充足が一部被験者のみなら model Go でも `Inconclusive` (データ拡充) に留める (§11)。
  - MNAR (PreReg-7)・二軸性 (PreReg-8) は notes + 機械可読カウントで報告併走。
- **振る舞い上の制約**: D (`calibration_eval.rs`)・`replay.rs`・`schema_dto.rs` は不変。`analysis/cohort.rs` (純関数) と
  `bin/cohort.rs` (I/O) に分離。閾値定数は `calibration_eval` を唯一の真実源とする。

## 3. ユースケース

### UC-1: 通常の作業セッション

- **アクター**: 知識労働者
- **前提条件**: GSE アプリケーションが起動済み
- **トリガー**: 「開始する」ボタンをクリック
- **基本フロー**:
  1. ユーザーがセッションを開始する
  2. GSE がキーストロークの収集を開始する
  3. ユーザーが通常通りキーボード作業を行う
  4. GSE が 1Hz でユーザーの認知状態を推定する
  5. ダッシュボードに Flow/Incubation/Stuck の確率が表示される
  6. ユーザーが作業を完了し、アプリを終了する
- **事後条件**: セッションログが NDJSON ファイルとして保存される

### UC-2: Stuck 検出と段階的介入

- **アクター**: 知識労働者
- **前提条件**: セッションが進行中
- **トリガー**: ユーザーが行き詰まり状態に陥る（長時間の修正・削除の繰り返し、長い休止）
- **基本フロー**:
  1. キーストローク特徴量が Stuck 領域に移行する
  2. Need と Opportunity が閾値を満たし、Nudge（右端サイドカード）が表示される
  3. ユーザーが作業を継続し、p_stuck が 0.70 を超える
  4. 累積 30 秒経過後、Wall が起動する
  5. ユーザーがスマートフォンで QR コードをスキャンする
  6. Zen Timer（2 分）が開始される
  7. タイマー完了後、ユーザーが手動でアンロックする
  8. ユーザーがリフレッシュされた状態で作業に戻る
- **代替フロー**:
  - 3a. Nudge 表示後に自然回復 → Nudge が消失し基本フローに戻る
  - 5a. Monk Mode が有効 → Wall は発動せず Nudge のみ
  - 7a. 緊急時 → Early Unlock ボタンで即時解除
- **事後条件**: 介入イベントがセッションログに記録される

### UC-3: 日本語入力での作業

- **アクター**: 日本語で文章を書く知識労働者
- **前提条件**: セッションが進行中、IME が ON
- **トリガー**: ユーザーが日本語入力を開始する
- **基本フロー**:
  1. IME ON が検出され、ベースラインが writing β に切り替わる
  2. 変換候補選択中は IME_ACTIVE がセットされる
  3. IME 変換中のバックスペースはペナルティから除外される
  4. 変換確定後、通常の特徴量計算が再開される
- **代替フロー（macOS）**:
  - 1a. JIS キーボード: 英数/かな物理キーで即座にモード切替を検出（\~5ms）
  - 1b. ANSI キーボード: TIS ポーリングによるメニューバー入力ソース切替の検出にフォールバック（100ms 間隔）
  - 2a. macOS: CGEventTap 内の状態機械でインライン変換（IME_COMPOSING）を追跡
- **事後条件**: IME 状態遷移がセッションログに記録される

### UC-4: macOS TCC 権限セットアップ

- **アクター**: macOS ユーザー（初回起動）
- **前提条件**: GSE アプリケーションを初めて起動する。TCC 権限は未付与
- **トリガー**: アプリケーション起動時のフック初期化
- **基本フロー**:
  1. CGPreflightListenEventAccess() が false を返す
  2. CGRequestListenEventAccess() がシステム設定を開く（Input Monitoring）
  3. ユーザーがシステム設定で GSE に Input Monitoring 権限を付与する
  4. CGEventTap が kCGEventTapOptionListenOnly で作成される
  5. フックがアクティブになり、キーストローク収集が開始される
- **代替フロー**:
  - 3a. Input Monitoring を拒否 → Accessibility 権限チェックへ移行
  - 3b. ad-hoc 署名で CDHash 不安定 → ListenOnly タップが 10 回連続失敗
  - 4a. ListenOnly 失敗 → AXIsProcessTrustedWithOptions ダイアログ（GCD メインキュー経由）を表示
  - 4b. ユーザーが Accessibility 権限を付与 → kCGEventTapOptionDefault でタップ作成
  - 5a. Dashboard の「システム設定を開く」ボタンから手動で Accessibility を付与
  - 5b. Dashboard の TCC リセットボタンで権限状態をリセットし再試行
  - 5c. ad-hoc 署名ビルドでは CDHash 不安定のため、システム設定で**権限を一度オフにしてから再度オンに戻す**手動操作が必要になる場合がある (Dashboard が再トグル手順を案内)。自動回復はシームレスではない点に注意
- **事後条件**: 権限状態（Input Monitoring / Accessibility / フォールバック使用中）が Dashboard に表示される

### UC-GT1: 開発者が自身の作業セッションにラベルを付ける (Phase 1)

- **アクター**: 開発者自身 (被験者 ID P000)
- **前提条件**: GSE アプリが起動中、Input Monitoring 権限付与済み、セッション開始済み
- **トリガー**: 作業しながら自覚的な認知状態の切替を感じた瞬間 (例: Flow に入った / Stuck に陥った)
- **基本フロー**:
  1. ユーザーが `⌘⇧⌥ F` (macOS) / `Ctrl+Shift+Alt+F` (Windows) を押す (Flow を自覚した場合)
  2. global-shortcut プラグインが `record_label_internal` を呼び、`compare_exchange` デバウンスを通過
  3. `log_tx.try_send(LogEntry::UserLabel { label: Flow, timestamp, recovered_at: None })`
  4. `user_label_recorded` Tauri イベントが emit され、Dashboard counter が `Flow N → N+1` に更新
  5. 2 秒以上空けて異なる状態を自覚したら `⌘⇧⌥ I` (Inc) / `⌘⇧⌥ S` (Stuck) を押す
  6. セッション終了で NDJSON に全ラベルが確定保存される
- **代替フロー**:
  - 2a. 2 秒以内に再押下: `compare_exchange` が失敗 → `tracing::warn!("debounced")` で破棄、Counter 不変
- **事後条件**: NDJSON ファイルに `{"type":"user_label",...}` 行が 1 つ以上記録される

### UC-GT2: オフラインで GT 付きセッションの精度を評価する (Phase 1)

- **アクター**: 開発者
- **前提条件**: UserLabel を含む NDJSON が `$GSE_DATASET/raw/P000/` (env 設定時) または `~/Documents/GSE-sessions/` (fallback) に存在
- **トリガー**: Phase 2a Go/No-Go 判定前の集計、またはパラメータ調整後の再評価
- **基本フロー**:
  1. `cargo run --bin gse-replay -- <session.ndjson> --metrics` を実行
  2. `collect_logged_feats` が NDJSON の `{"type":"feat",...}` 行を `FeatSnapshot` 列として抽出 (production wall-clock の真値を使用)
  3. `collect_user_labels` が NDJSON を 2 度目に読み UserLabel を抽出
  4. `compute_session_metrics` が混同行列 / F1 / 検出リード / Stuck 回復を算出
  5. pretty-print または `--json` で出力
- **代替フロー**:
  - 1a. `--metrics --snapshot` を同時指定 → Usage エラーで exit 2
  - 5a. `--json` 指定時: 構造化 JSON を stdout に出力
- **事後条件**: `SessionMetrics` を人間または機械 (`aggregate_metrics.py`) が消費できる形で標準出力に得る

### UC-GT3: 端末間で metrics を共有し Phase 2a 判定する (Phase 1)

- **アクター**: 開発者 (macOS 端末 + Windows 端末を跨ぐ)
- **前提条件**: UC-GT2 の `--metrics --json` 出力が手元にある、`gse-dataset` repo を clone 済み
- **トリガー**: 複数セッションが溜まり、Phase 2a 着手の Go/No-Go を判定したい
- **基本フロー**:
  1. 各端末で `--metrics --json` 出力を `gse-dataset/metrics/P000/<macos|windows>/*.metrics.json` に配置
  2. `gse-dataset` で `git commit && git push`
  3. 他端末で `git pull`
  4. `python scripts/aggregate_metrics.py` で全体集計: セッション数 / Macro F1 平均 / per-class 平均 / Stuck precision 平均
  5. `Phase 2a Go/No-Go (Stuck precision >= 0.6, n >= 5)` の判定行を確認
- **代替フロー**:
  - 4a. `n < 5`: `INCONCLUSIVE` が出力される → セッション収集を継続
  - 4b. 破損 metrics.json がある: `aggregate_metrics.py` が `sys.stderr` に WARN を出しスキップ、`skipped` リストに記録
- **事後条件**: 複数端末のデータが単一の集計値に統合され、`baseline_metrics.md` への転記元になる

## 4. 機能要件

### 必須機能

- キーストロークのリアルタイム収集（Windows: WH_KEYBOARD_LL / macOS: CGEventTap）
- macOS TCC 権限管理（Input Monitoring / Accessibility の自動検出・フォールバック・リセット）
- 3 状態認知推定（Flow / Incubation / Stuck）の 1Hz 更新
- 日本語 IME 対応（文脈依存ベースライン切替）
- Lv1 Nudge 介入（視覚フィードバック）
- Lv2 Wall 介入（全画面ロック + スマートフォンアンロック + Zen Timer）
- セッションログの NDJSON 永続化
- Monk Mode（Wall 無効化トグル）

### オプション機能

- セッションログの事後分析スクリプト（behavioral_gt.py）
- キーボードアイドル検出による Wall 自動解除

### 将来的な拡張

- **ML モデル推論**: データ蓄積に応じて HMM → ONNX Runtime 経由の学習済みモデルへ段階的移行。学習データはオプトイン同意のもとセッションログを匿名化・集約して収集
- **Lv3/Lv4 介入**: Physical Anchor（身体的活動の促進）— Flutter アプリとの連携
- **マルチデバイス対応**: タッチパッド、ペン入力の特徴量追加

## 5. 非機能要件

### パフォーマンス

- **推定レイテンシ**: 1Hz（1 秒ごとに状態確率を更新）
- **フック遅延**: フックコールバック内での処理は最小限（アトミック操作 + チャネル送信のみ）
- **UI 更新**: 500ms ポーリング間隔

### セキュリティ・プライバシー

- **キーストロークデータ**: VK コードのみ記録（文字内容は記録しない）
- **セッションログ（運用時）**: ローカルファイルシステムに保存。リアルタイム推定中の外部送信なし
- **セッションログ（学習データ収集）**: ML モデル学習目的の外部送信はオプトイン + 匿名化 + セッション終了後バッチのみ許可
- **Wall Server**: ローカルネットワーク内のみ（Windows: Defender ファイアウォールルール動的管理 / macOS: ユーザースコープポートバインドのため追加のファイアウォール管理不要）
- **Wall Server トークン**: ランダム生成トークンによるアクセス制御

### 可用性

- **想定稼働率**: デスクトップアプリケーションのため、OS 起動中は常時利用可能
- **障害復旧**: フック登録失敗やチャネル溢れは graceful degradation（推定精度低下はあるがクラッシュしない）

### ユーザビリティ

- **対応デバイス**: Windows 11（Surface Pro 8 + Type Cover）/ macOS 13 Ventura 以降（MacBook Pro/Air — JIS / ANSI 両キーボード対応）
- **UI**: ダッシュボードウィンドウ + オーバーレイウィンドウの 2 ウィンドウ構成
- **操作**: セッション開始/終了とMonk Mode 切替のみ（設定項目を最小化）
