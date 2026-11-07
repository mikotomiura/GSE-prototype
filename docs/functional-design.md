# 機能設計書

## 1. プロジェクト概要

- **プロダクト名**: GSE (Generative Struggle Engine)
- **解決する課題**: 知識労働者がキーボード作業中に作業停滞へ入り、自覚なく長時間停滞し続ける問題。従来の生産性ツールは作業量の最大化を目指すが、GSE は PC 操作に現れる行動的シグナルから介入判断に必要な作業上の状態を推定し、適切なタイミングでの介入により「生産的苦闘（Productive Struggle）」を保護する。
- **ターゲットユーザー**: Windows 11 および macOS（13 Ventura 以降）上で日常的にキーボード作業を行う知識労働者（メール、企画書、ドキュメント作成、コーディング等）
- **コアバリュー**: **不便益を設計思想として引く** HCI フレームワーク — あえて不便を導入することで、ユーザー自身の作業再編・休止・**関与の再開**を促す。（⚠️ **2026-09-01: 禁止用語 2 件を是正** —— 「不便益**に基づく**」と「**回復**」は `docs/glossary.md` の禁止用語）GSE は脳内の認知状態を直接読むのではなく、行動的シグナルから Need と Opportunity を分離して介入判断を行う。

## 2. コア機能一覧

### 機能 1: キーストロークセンシング

- **概要**: OS レベルのキーボードフックにより、すべてのキー入力イベントをリアルタイム収集する
- **入力**: 物理キーボード入力（Windows: WH_KEYBOARD_LL / macOS: CGEventTap）
- **出力**: InputEvent ストリーム（vk_code, timestamp, is_press, is_repeat, is_backspace）
- **振る舞い**:
  - 専用スレッドでフックを実行し、メインスレッドをブロックしない
  - crossbeam チャネル経由で分析スレッドへイベントを送信
  - オートリピートキーを識別しフィルタリング可能にする
  - macOS: **Input Monitoring tap（ListenOnly tap）** を優先し、**3 回**連続失敗後に **Accessibility tap（Default tap）** へ自動フォールバック（⚠️ **2026-09-01 訂正: 旧文は「10 回」。実測は `hook_macos.rs:686` `consecutive_failures >= 3`**。★ API 定数名は `glossary.md` 禁止用語なので権限名で書く）
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

### 機能 4: Opportunity 判定 + 介入

- **概要**: Need（介入が必要そうか）と Opportunity（今介入してよいか）を分離し、`InterventionDecision` に従って段階的な介入を実施する。
- **MVP 入力**: `p_stuck`, `idle_ms`, F3/F4/F6, `cooldown`, `daily_cap`, `recent_dismiss`
  （⚠️ **2026-09-01 訂正: `Monk Mode` と `Wall 累積時間` を削除** — ADR-015 D1/D2。実体は `intervention.rs:152-159` の 6 フィールド）
- **MVP 出力**: `none` / `nudge` / `defer`（実測: `intervention.rs:16-20`。⚠️ **`wall` は ADR-015 D1 で削除**）
- **初期パラメータ**:
  - Nudge Need: `p_stuck >= 0.60`
  - Nudge cooldown: 10 分、daily cap: 6 回/日
  - recent dismiss 抑制: 20 分
  - away idle: 180 秒以上で**介入を出さない**（`none` 化・`suppressed_by:["away_idle"]`。`intervention.rs:249-251`）

- **発火/非発火の要点（期待ギャップ防止・実機 smoke フィードバック反映）**:
  - **Opportunity ゲート**: Need が高くても「今が好機か」を別途判定する。好機は **2〜30 秒の小休止**
    (短 2-8s が最良、中 8-30s が次点)。**能動タイプ中 (<2s) は減点され `defer`**（タイプを止めずに苦闘継続中は割り込まない）。
  - **席を離れたら黙る (不便益)**: `idle_ms ≥ 180s` で `away_idle` により介入を出さない。NDJSON では
    `suppressed_by:["away_idle"]` で識別する（`reason` は need 依存で、放置中は p_stuck 低下により
    `below_need_threshold` になることが多い）。
  - **idle ≠ Stuck**: キーボードを放置すると `p_stuck` はむしろ低下する（無打鍵は idle 観測でモデル上「停滞」ではない）。
    したがって「**長時間放置すれば介入が出る**」という挙動は**設計外**。介入は *作業に没入したまま苦闘している*
    （高 `p_stuck` × 小休止）状況を対象とする。
  - **2 つの介入制御の役割差**:
    - `session_meta.intervention_enabled`: セッション開始時の**マスタ ON/OFF**。`false` なら backend が
      全 `get_intervention_decision` を `none` で gate（較正の既定）。
    > ⚠️★★★ **2026-09-01 訂正 —— Monk Mode は 2026-08-23 に削除された**（ADR-015 D2）。
    > 旧文は「実行中トグルで **Lv2 Wall のみ**を無効化（Nudge は出る）」と書いていたが、
    > **`session_meta` の `monk_mode` フィールドごと外れている**（実測: `schema_dto.rs:317-337` に無い）。
    > ★ **介入制御は `session_meta.intervention_enabled` の 1 本だけである。**

#### Nudge（視覚的ヒント）— ★ **現行で稼働する唯一の介入**
- **トリガー**: `InterventionDecision.action == "nudge"`
- **振る舞い**: オーバーレイウィンドウ**右上**に小カード（幅 340px）を表示（`src/App.css:565-572`）。
  ★ カード以外は **OS レベルでクリック透過**（非ブロック）
- **解除条件**: 4 択（`not_stuck` / `want_to_struggle` / `just_close` / `silent`）のいずれかを押す、
  または **60 秒**無応答で `silent` として自動フェードアウト（`src/components/Overlay.tsx:40,340-365`）。
  いずれも `record_intervention_dismiss` を経て `recent_dismiss`（20 分）が立つ
  （★ `DismissReason` の実体は `schema_dto.rs:496-501` の 4 値）
> ⚠️★★★ **2026-09-01 訂正 —— 旧「#### Lv2: Wall（作業ブロック）」の節を全削除した。**
> ★ **Wall / Zen Timer / Early Unlock / `wall_server.rs` は 2026-08-23 に全削除された**（ADR-015 D1）。
> 旧節は全画面ロック・QR・Zen Timer・`POST /unlock`・Wall Server 起動失敗時のエラー条件まで
> **現行仕様として記述していた**が、**発火経路がコードに 1 つも無い**。
> ★ 段階呼称も外した（`#### Lv1:` → `#### Nudge`。ADR-018 D7）。
> 2026-11-03 更新: Physical Anchor の PC 側の招待は EH3 モードで実装済み（`analysis/invitation.rs`）。散歩の促進とその計測は行わない（2026-11-03 研究者の言。歩数・位置は ADR-017 D10 で本体から外してある）。身体回帰の後は、離席候補（打鍵の途絶 180 秒以上）明けの作業上の状態で見る。主は打鍵の再開と受領の有無（ADR-024 D1・D3）、副はウィンドウを離れずに再開したか（フォーカスの遷移・ADR-040・ADR-041 D3）。離席候補とフォーカスの遷移は別の腕として解析する（ADR-023 D4）。ポインタ（移動・ボタン・ホイール）は、打鍵の無い作業を離席と取り違えないために記録し（ADR-014・ADR-016）、停滞の型の手の様子（移動やクリック・フォーカスの離脱）にも使う（ADR-041 D2）。身体が動いたことは測らない（ADR-024 D5・ADR-018 D3）。

### 機能 5: セッション管理

- **概要**: 分析セッションのライフサイクルと Opportunity policy state を管理する
- **入力**: ユーザーの「開始する」ボタン押下
- **出力**: セッション開始/終了イベント、NDJSON セッションログ
- **振る舞い**:
  - セッション開始時: HMM エンジンリセット、ロガー初期化
  - セッション中: 1Hz で作業状態スコアを更新、500ms で UI が `InterventionDecision` をポーリング
  - セッション終了時: ログファイルの flush とクローズ（⚠️ **2026-09-01: 「Wall Server 停止」を削除** — ADR-015 D1）
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
> **較正モード blind dashboard (測定独立性)**: v0.3 較正セッションの既定メイン画面は **blind/minimal** にする (`App` の `calibrationMode` state、既定 ON・Start 画面のトグルで切替)。被験者にモデル出力 (推定状態 / Flow・Incubation・Stuck 確率 / p_stuck・X/Y / GT counter / 状態色) を**一切見せない**ことで、主観回答 (criterion label) のアンカリング汚染を防ぐ。較正中に表示してよいのはセッション経過時間 / Keyboard・Hook 状態 / 終了ボタン / 権限警告のみ。（⚠️ **2026-09-01: 「Monk Mode (介入状態)」を削除** — ADR-015 D2）`ProbeCard`/`VignetteTest` は overlay で従来どおり動作。frontend のみの分岐 (backend/schema 不変、`cognitiveState` は取得するが非表示)。`.steering/20260617-calibration-blind-dashboard/` 参照。

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

### 2.x+2 P1 の特徴行 (`gse-replay --features`) — オフライン

O1 の自然作業のセッション NDJSON から、1 Hz の特徴行（stall onset・`T0`〜`T1d`・品質）を作る解析専用の経路
（ADR-030 D1「検出器はオフライン側に置く」）。出力は封筒 `{ provenance, config, rows }`。
仕様の SSOT はこの節ではなく、`docs/adr/ADR-030-stall-onset-and-decision-episode.md`（補訂 1〜5）と
`docs/preregistration-p1-episode.md`（値・探索・読み方）、値は `src-tauri/prereg/p1-episode.json`。

- **設定**: 既定は凍結 JSON。`--set <key>=<value>` / `--feature-config` で外れた値は封筒 `config.overrides` に残る。極は `--pole`。
- **観測区間の前処理**（2026-10-08・事前宣言 v1.2 §6・issue #330）: 観測区間を作る前に、長い穴（`idle_trim_min_gap_ms` 以上）の直前と
  ファイルの最後で、最後の入力（`key` 行と `pointer_bin` 行）を含む秒の `feat` 行より後を、最大 `idle_trim_max_ms` さかのぼって落とす。
  Windows のモダンスタンバイで、寝た後も `feat` 行が続く（電源につないだ試験で 16 分）ことへの対処。
  落とした量は `provenance.idle_trim`。前処理なしの実行（`--set idle_trim_max_ms=0`）を必ず並べて報告する（2 本は真の値を挟む上下界ではない）。
- **長い無入力の前処理**（2026-10-11・事前宣言 v1.3 §7）: 続けて、入力と入力の間（ファイルの最初と最後を含む）が `idle_trim_input_gap_ms`（30 分）以上
  空いた区間の `feat` 行を落とす（前後の入力を含む秒の行は残す）。O1 のアプリは宣言を自分では外さず、PC が起きていれば `feat` 行が途切れないことへの対処。
  落とした量は `provenance.input_gap_trim`。この前処理なし（`--set idle_trim_input_gap_ms=0`）、無入力の末尾の前処理なし（`idle_trim_max_ms=0`・v1.3 では長い無入力の前処理は掛かったまま）、両方なしの 3 本を並べて報告する（v1.3 §7.4）。
- **振る舞い上の制約**: 出力は `gse-dataset` へ共有しない（`scripts/check_no_feature_output.sh`）。`features.rs` / `engine.rs` は変えない。

### 2.x+3 段 1 のモードと問いの調停器（ADR-043・ADR-031 M5）— 駆動役・画面・再生まで（配布の門は 3 本目の PR 2）

段 1（本人の試しと確認の段）は、O1 の収集の器の上に載る層である（EH3 と同じ作り方）。O1 の提出・自動起動・導入 ID・区間の削除をそのまま共有し、問いだけを足す。
問いは C4 のプローブ（無作為の枠が主・層化は補い・6 択の申告）と日の終わりの問い（ADR-048 D3）。計画は `.steering/20261105-gse-m5-probe-wiring-plan/`。

- **2026-11-06 時点（M5 の 1 本目・`.steering/20261106-gse-m5-s1-core/`）**: モードの判定（`s1.rs`・印 `s1.mode`・env `GSE_S1_MODE=1`・O1 のときだけ・EH3 の印と同時なら両方を落とす）、純粋な調停器（`analysis/probe_arbiter.rs`）、行種 `probe_frame`・`probe_suppressed`・`day_question` と `meta.s1_mode`・`skip_reason` の `superseded` がある。
- **2026-11-07 時点（M5 の 2 本目・`.steering/20261107-gse-m5-s1-driver-ui/`）**: 段 1 の駆動役（`s1_driver.rs` の純粋な部分と `lib.rs` の駆動スレッド）が 1 秒ごとに調停器を回し（時刻は 2 秒遅らせ、押下が届き切ってから判定する）、問いを overlay のカードに出す。
  - 本人が登録の画面で「問いに同意する」を押すまで問いは出ず、行も 0。押すと O1 のローテートを 1 回起こし、新しいファイルの起点で枠を作る。「問いへの同意を取り消す」で開いているカードを行なしで下ろし、以後の行は 0。
  - プローブのカードは 3 問を 1 枚（摩擦・前進・固定の 6 択・自由記述なし）。`realtime_label` と `activity_label` を同じ `probe_id` で 2 行書く。層化のカードを無作為が差し替えたときは `superseded` の 2 行。
  - 日の終わりの問いは「今日の作業にどのくらい熱意を持てましたか」1〜5（仮の文 `dq-draft-1`・拾い直しは「昨日の作業に」）。無作為の問いが出ている間は伏せ、閉じたら出し直す。トレイの「GSE を終了」は、時間帯の中で当日まだ尋ねていなければ「答えて終了／答えずに終了」で尋ね、60 秒で終わる。どの終了の経路でも、開いている日の問いの行を `End` の前に書く。
  - 一時停止の間はカードを出さない（開いているプローブは行なしで下ろす）。段 1 の overlay は画面共有・録画から外す。capabilities は 4 行種（`activity_label`・`probe_frame`・`probe_suppressed`・`day_question`）を段 1 のときだけ `config_gated` に宣言する。
  - O1 の配布の門は、6 択の送出元が段 1 の門だけを通るなら O1 の同意の ESM 追補を求めず、O1 の配布物に `s1.mode` を書かないことを確かめる。
- **2026-11-07 時点（M5 の 3 本目の PR 1・`.steering/20261107-gse-m5-s1-replay-gate/`）**: 再生 `gse-replay <s1.ndjson> [s2.ndjson ...] --probes [--utc-offset-secs <N>] [--day-state <s1_day_state.json>]` が、記録の `key`（押下）・`focus_transition`・`recording_pause`・`probe_frame` から同じ調停器を回し直し、`probe_assignment`・`probe_suppressed`・差し替えのラベル・`day_question` と照合した結果を JSON で出す（`s1_replay.rs`）。
  - 開いているカードは再生の発火からでなく記録から渡す（1 件の食い違いを後ろへ波及させない）。照合の鍵は候補の時刻（tick の位相に依らない）で、位相を 4 通りに振って割れたものは境目に分ける。
  - 分類: `match`・`differ`・`missing`（再生にあり記録に無い）・`extra`（記録にあり再生に無い）と、一時停止の行の前 2 秒（`boundary_pause`）・枠の動き出し・記録に無い情報（時差・前日の状態・スリープの復帰・起動・同意の取り消し）で照合できないもの（`unverified`）。回答率は差し替え・一時停止や終了で下ろしたカードを分母から外して出す。
  - `--day-questions --utc-offset-secs <N>` は、答えた日の問いごとに次の現地 4:00 までの押下の数を出す。
  - 確かめ用のボタン（`GSE_DEBUG=1` の下だけ）で出したカードの行には `"debug":true` を付け（本物の行は変わらない）、再生は照合の外で数える。
  - 限界: 区間の削除は NDJSON に印を残さないので、削除をまたぐ記録は一致しない。一時停止の間に閉じた日の問いと同意の取り消しは行が無い。
- **調停の順**: 無作為の枠 → 層化 → 日の問い。無作為の候補の時刻の列は `frame_seed` と起点だけで決まり、層化と日の問いは枠を読むだけ（記録から再現できる）。推定器の出力を入力に持たない（ADR-031 D2）。頻度と閾値は探索用の仮の定数（確定は R6′）。
- **6 択の門**: `o1::activity_label_allowed(段 1, 本人の同意の印)`。素の O1 では同意があっても通さない（ADR-043 D8）。同意の印は `~/.gse/s1_probe_consent`（時刻と版だけ）。
- **プライバシー**: 新しい行は数値・真偽・固定の文字列だけ。`day_question` は現地の分を書かず、時間帯の中かの真偽だけ（時差を出さない）。区間の削除で `probe_frame` は残し（系の設定だけ）、他の 2 行種は 2 つの時刻を両端とする区間で消える。

## 3. ユースケース

### UC-1: 通常の作業セッション

- **アクター**: 知識労働者
- **前提条件**: GSE アプリケーションが起動済み
- **トリガー**: 「開始する」ボタンをクリック
- **基本フロー**:
  1. ユーザーがセッションを開始する
  2. GSE がキーストロークの収集を開始する
  3. ユーザーが通常通りキーボード作業を行う
  4. GSE が 1Hz でユーザーの作業上の状態を推定する
  5. ダッシュボードに推定の 3 つの確率（列 `p_flow`・`p_inc`・`p_stuck`）が表示される（2026-11-05: 3 状態の名前は主張と画面で使わない・ADR-046 D1。列名は識別子。2026-11-05 時点の実装の `src/components/Dashboard.tsx` は Incubation・Stuck の名前を表示している。研究者向けの表示かは要確認で、直すのは別タスク）
  6. ユーザーが作業を完了し、アプリを終了する
- **事後条件**: セッションログが NDJSON ファイルとして保存される

### UC-2: Stuck 検出と介入

- **アクター**: 知識労働者
- **前提条件**: セッションが進行中
- **トリガー**: ユーザーが行き詰まり状態に陥る（長時間の修正・削除の繰り返し、長い休止）
- **基本フロー**:
  1. キーストローク特徴量が Stuck 領域に移行する
  2. Need と Opportunity が閾値を満たし、Nudge（右上の小カード）が表示される
  3. ユーザーが 4 択（`not_stuck` / `want_to_struggle` / `just_close` / `silent`）で応答するか、
     **60 秒**無応答で `silent` として自動フェードアウトする
  4. `record_intervention_dismiss` が `intervention_response` 行を記録し、`recent_dismiss`（20 分）が立つ
- **代替フロー**:
  - 2a. Nudge 表示前に自然回復 → `below_need_threshold` で `none`（`intervention.rs:449-451`）
  - 2b. Opportunity が低い（打鍵中など） → `defer`（★ 見逃しではなく **Opportunity を守る判断**）
  - 2c. idle 180 秒以上 → `suppressed_by:["away_idle"]` で `none`
> ⚠️★★★ **2026-09-01 訂正 —— 旧フローは Wall 起動 → QR → Zen Timer → 手動アンロックの
> 5 ステップを「基本フロー」として書いていたが、その経路は ADR-015 D1 で全削除された。**
> ★ 代替フローの「Monk Mode が有効 → Wall は発動せず」「Early Unlock ボタンで即時解除」も同様に失効。
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
  4. CGEventTap が **Input Monitoring tap（ListenOnly tap）** で作成される
  5. フックがアクティブになり、キーストローク収集が開始される
- **代替フロー**:
  - 3a. Input Monitoring を拒否 → Accessibility 権限チェックへ移行
  - 3b. ad-hoc 署名で CDHash 不安定 → ListenOnly tap が **3 回**連続失敗
  - 4a. ListenOnly 失敗 → AXIsProcessTrustedWithOptions ダイアログ（GCD メインキュー経由）を表示
  - 4b. ユーザーが Accessibility 権限を付与 → **Accessibility tap（Default tap）** でタップ作成
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
- **事後条件**: `SessionMetrics` を人間または機械 (**`gse-cohort`**) が消費できる形で標準出力に得る（⚠️★★★ **2026-09-01 訂正 —— `scripts/aggregate_metrics.py` は存在しない。** 実測で `scripts/` に該当ファイルは 0 件。★ **被験者横断の集計は `gse-cohort`（`src-tauri/src/bin/cohort.rs`）と `scripts/run-calibration-cohort.sh` が担う**。v0.2 期の計画名がそのまま残っていた）

### UC-GT3: 端末間で metrics を共有し Phase 2a 判定する (Phase 1)

- **アクター**: 開発者 (macOS 端末 + Windows 端末を跨ぐ)
- **前提条件**: UC-GT2 の `--metrics --json` 出力が手元にある、`gse-dataset` repo を clone 済み
- **トリガー**: 複数セッションが溜まり、Phase 2a 着手の Go/No-Go を判定したい
- **基本フロー**:
  1. 各端末で `--metrics --json` 出力を `gse-dataset/metrics/P000/<macos|windows>/*.metrics.json` に配置
  2. `gse-dataset` で `git commit && git push`
  3. 他端末で `git pull`
  4. **`bash scripts/run-calibration-cohort.sh`**（内部で `gse-cohort` を呼ぶ）で全体集計: セッション数 / Macro F1 平均 / per-class 平均 / Stuck precision 平均（⚠️★★★ **2026-09-01 訂正 —— `scripts/aggregate_metrics.py` は存在しない。** 実測で `scripts/` に該当ファイルは 0 件。★ **被験者横断の集計は `gse-cohort`（`src-tauri/src/bin/cohort.rs`）と `scripts/run-calibration-cohort.sh` が担う**。v0.2 期の計画名がそのまま残っていた）
  5. `Phase 2a Go/No-Go (Stuck precision >= 0.6, n >= 5)` の判定行を確認
- **代替フロー**:
  - 4a. `n < 5`: `INCONCLUSIVE` が出力される → セッション収集を継続
  - 4b. 破損 metrics.json がある: `gse-cohort` が stderr に警告を出しスキップする
- **事後条件**: 複数端末のデータが単一の集計値に統合され、`baseline_metrics.md` への転記元になる

### UC-OM1: 捕捉済み NDJSON から v0.4 アウトカム指標を算出する (Phase B / WBS 0.10)

- **アクター**: 開発者 / 研究者
- **前提条件**: capture-schema-freeze 以降の NDJSON (`external_paste_chars` / `key` / `feat` を含む) が手元にある
- **トリガー**: M3 Y 価値検証の (a) AI依存度・(b) 自力解決率を `metrics.json` に載せたい
- **基本フロー**:
  1. `gse-replay --metrics --json` が `collect_logged_feats` / `collect_paste_events` / `collect_key_events`
     で content-free な時系列 (p_stuck feat / paste 文字数 / **key category**) を収集
  2. `segment_stuck_episodes` が `p_stuck >= 0.60` の連続区間を merge-gap で統合し **Stuck エピソード**化
  3. `compute_outcome_metrics` が各エピソードについて回復 (p_flow>0.5)・paste 有無・net_diff 正進行を判定し、
     (b) `manual_contribution_ratio` / `pflow_exit_manual_gain_rate`、
     (a) `external_paste_count` / `large_paste_rate` / `paste_after_stuck_rate` /
     `pflow_exit_without_receipt` / `paste_count_per_hour` (補助) を算出
  4. `SessionMetrics.outcome` (additive・後方互換) として既存メトリクスと同じ `metrics.json` に出力
- **代替フロー**:
  - 1a. 旧 NDJSON で `external_paste_chars` 欠落の paste: outcome から除外し `excluded_paste_count` に件数を残す
  - 3a. paste/key/エピソードが 0 件: 各比率は `None` (NaN を出さない)
- **事後条件**: `metrics.json` に**数値のみ** (キーストローク/クリップボード内容を一切含まない) で
  (a)(b) 指標が載り、後から閾値を変えて再処理・再計算できる
- **備考**: Stuck 候補トリガは `StuckTrigger` enum で将来 `UserLabel` / `InterventionFired` へ拡張する
  設計だが、**現状は `PStuckThreshold` (既定) のみ実装**。予約バリアントを指定した場合は p_stuck の
  結果を返さず空エピソードになる。詳細・根拠は `.steering/20260623-outcome-metrics/decisions.md`

### UC-EH3: EH3 の参加者が、肖像と招待のある PC で自分の作業をする

- **前提**: 研究者が配布フォルダに `o1.mode` と、その参加者の割り当てを書いた `eh3.mode` を置いた（`docs/eh3-distribution-tag.md`）。
- **流れ**:
  1. 参加者はふだんどおり作業する（O1 と同じく「開始する」を押さずに記録が続く）。
  2. その日に初めて打鍵すると、その日が稼働日として数えられ、条件（空 / D / A-none / A-seed）が決まる。
  3. 空の日は元の壁紙のまま。D の日は日替わりの地模様。A の日は打鍵の時間関係から描いた形が 5 分ごとの予定で育つ（60 秒以上の不在の中では更新しない）。終了・スリープの直前・4:00 に、A-seed の日は形を小さな印へ畳む。
  4. 推定の停滞が 30 秒続くと、画面の右上に文字の無い小さな図像が 60 秒出る（1 区間 1 回・閉じた後 30 分・1 日の上限は本人が選ぶ）。押すと説明と設定の窓が開く。
  5. 参加者はトレイからいつでも「壁紙を元に戻す」「印の説明と設定」を選べる。どちらも記録しない。
  6. 15 稼働日を超えた日になった時点（その日の最初の起動、または起動中なら 4:00）で、元の壁紙に戻る（seed の印を残さない）。期間の後は招待も出ない。
- **記録**: `meta` の `eh3_mode`・`invitation_enabled`、`eh3_day`、`invitation_present`。壁紙を書いた時刻・本人の操作・設定の値は記録しない。
- **要件の SSOT**: `.steering/20261011-portrait-eh3-prereg/implementation-requirements.md`。実装の判断は `.steering/20261011-portrait-eh3-impl/decisions.md`。

## 4. 機能要件

### 必須機能

- キーストロークのリアルタイム収集（Windows: WH_KEYBOARD_LL / macOS: CGEventTap）
- macOS TCC 権限管理（Input Monitoring / Accessibility の自動検出・フォールバック・リセット）
- 3 状態の HMM の推定（列 `p_flow`・`p_inc`・`p_stuck`）の 1Hz 更新（2026-11-05: 名前は識別子で、状態の主張ではない・ADR-046 D1。推定は契機を作らない・ADR-047 D2）
- 日本語 IME 対応（文脈依存ベースライン切替）
- Nudge 介入（視覚フィードバック）
- セッションログの NDJSON 永続化
- 介入のマスタ ON/OFF（`session_meta.intervention_enabled`。⚠️ **2026-09-01: 旧「Monk Mode（Wall 無効化トグル）」を差し替え** — ADR-015 D2 で削除）

### オプション機能


### 将来的な拡張

- **ML モデル推論**: データ蓄積に応じて HMM → ONNX Runtime 経由の学習済みモデルへ段階的移行。学習データはオプトイン同意のもとセッションログを匿名化・集約して収集
- **Physical Anchor**: **身体的回帰への方向づけ**（★ **系は開始も完了も判定しない** — ADR-018 D1/D2。
  ⚠️ タイマー・カウントダウン・残り時間表示を実装しない）— Flutter アプリとの連携。
  ⚠️★★★ **身体活動のセンシング（歩数・距離・速度・位置情報）は本体から恒久的に外れている**（ADR-017 D10）。
  ★ 境界（PC → スマホの一方向）の形は ADR-017 D3 で確定済み。
  （⚠️ **2026-09-01 訂正: 旧文「Lv3/Lv4 介入: Physical Anchor（身体的活動の促進）」は
  段階呼称・完了条件・センシングの 3 点で現行の決定と食い違っていた**）
- **マルチデバイス対応**: タッチパッド、ペン入力の特徴量追加

## 5. 非機能要件

### パフォーマンス

- **推定レイテンシ**: 1Hz（1 秒ごとに状態確率を更新）
- **フック遅延**: フックコールバック内での処理は最小限（アトミック操作 + チャネル送信のみ）
- **UI 更新**: 500ms ポーリング間隔

### セキュリティ・プライバシー

- **キーストロークデータ**: NDJSON にはキーの**種類**（`KeyCategory` 14 種）と押下/離上のみを記録する。
  ⚠️★★★ **2026-09-01 訂正 —— 実装は旧文より厳しい。生 VK コードも書かない**
  （ADR-014 判断 6 で `vk` → `category` へ変更・`logger.rs:1541`。回帰テスト `key_line_records_category_and_never_raw_vk` が固定）
- **セッションログ（運用時）**: ローカルファイルシステムに保存。リアルタイム推定中の外部送信なし
- **セッションログ（学習データ収集）**: ML モデル学習目的の外部送信はオプトイン + 匿名化 + セッション終了後バッチのみ許可
> ⚠️★★★ **2026-09-01 訂正 —— GSE は現在いかなるローカル HTTP ポートも開かない。**
> 旧文はここに「**Wall Server**: ローカルネットワーク内のみ（Windows: Defender ファイアウォールルール動的管理…）」
> 「**Wall Server トークン**: ランダム生成トークンによるアクセス制御」の 2 行を置いていたが、
> **`wall_server.rs` は ADR-015 D1 で削除**され、依存 `tiny_http` / `qrcode` も除去済みである。
> ★ **存在しない攻撃面をセキュリティ節に書き続けると、実在する経路から目が逸れる。**
- **提出パス（★ 現行で唯一の外部送信経路）**: セッションが閉じた後にのみ、匿名化（`analysis::anonymize`）
  → age 暗号化（`packaging.rs`）→ `.age` を生成する。★ **被験者の確認（`.ok`）が無ければ送信経路が開かない**
  （`submission.rs`）。送信済みは `.age.sent` で表す。O1 では 48 時間の猶予後に自動提出する（`o1.rs`）
  - ★ **O1 の送信見送り（G-5・2026-09-28）**: 受け口の上限（32 MiB・`Form_O1/GSE_O1_Submit.gs` の `MAX_BYTES`）を
    **超える** `.age` は送らず、提出物フォルダの `oversize/` へ移す（送る前の大きさ検査と、受け口の `too large` 応答の両方）。
    ⚠️ **消さない**（研究者が手で回収する・`docs/o1-deletion-ledger.md` B-4b）。日番号は台帳も見て決まるので再利用されず、
    受領台帳の欠番検知が研究者に知らせる。⚠️ **G1 は対象外**（凍結）
- ⚠️ **PC ↔ スマホの境界を将来作るときは ADR-017 D4 の S1–S6 を満たすこと**
  （S1 明示的ペアリング / S2 送信元認証 / S3 偽造・リプレイ対策 / S4 端末紐付けと失効 / S5 LAN 露出の明示 /
  S6 ペイロードに本人性を載せない）。★ **常設の LAN リスナを置かない**（ADR-017 D4）

### 可用性

- **想定稼働率**: デスクトップアプリケーションのため、OS 起動中は常時利用可能
- **障害復旧**: フック登録失敗やチャネル溢れは graceful degradation（推定精度低下はあるがクラッシュしない）
- ⚠️★ **O1 の稼働継続（2026-09-28・`.steering/20260928-o1-resilience-g1-g2-g5/`）**:
  - **自動起動（G-1）**: O1 の配布形（`o1.mode` 由来）で**初めて起動したときに 1 回だけ**、ログイン時起動に登録する
    （macOS = `~/Library/LaunchAgents/com.johnd.gse-next.o1.plist`・Windows = HKCU `Run` の `GSE-O1`（引用符つき））。
    ★ **O1 の同意確認の後**だけ。新しく作るのは端末で 1 回だけ（`~/.gse/o1_autostart_registered`）で、新しい版のフォルダでは
    **OS に登録が残っているときだけ**付け替える（被験者が切った・消したら作り直さない）。配布フォルダの印 `o1.autostart` は処理済みの印。
    ⚠️ 環境変数 `GSE_O1_MODE=1`・G1・通常運用では登録しない（`autostart.rs`）
  - **定期再送（G-2）**: O1 では起動時・日次ローテート時に加えて **6 時間ごと**に収束器を回す
    （`ReconcileReason::O1Periodic`・`o1::PERIODIC_RECONCILE_MS`）。排他は既存のロックに任せる
- ⚠️★★ **フック生存監視 (hook liveness・2026-08-09 追加)**:
  「フックの**設置**に成功した」と「イベントが**届いている**」は別概念として扱う。
  OS が低レベルフックを黙って外した場合、従来はどこにも痕跡が残らず
  **打鍵ゼロのブロックが「正常」として提出された**
  （`experiments/20260801-controlled-friction-task/windows-verification.md` §5-7 に実測記録）。
  - **検知**: OS が持つ「最後の入力時刻」（フックとは独立な情報源）の**変化**と、
    自前フックのコールバック回数の**変化**を 1 Hz で突き合わせ、
    「システムには入力があるのに自前のフックは呼ばれない」時間を累積する（`input/liveness.rs`）。
    ⚠️ ★ **キーの内容も種別も読まない**（`data-privacy`）。
  - **通知**: 30 秒でアプリログに `ERROR`、120 秒でトレイを `⚠ 計測できていません` にする。
    ⚠️ ★ **被験者向けの文言・通知は増やさない**（盲検と介入規制。トレイ表示までに留める）。
  - **復旧**: 既存の再設置経路を **1 エピソードにつき 1 回**だけ起こす。
    ⚠️ ★ 繰り返すと、誤検知時に**生きているフックを壊し続ける**。
  - **記録**: NDJSON に `hook_health` 行（`alive` / `starved_ms` / `rehook`）を残す。
    ★ **判断ではなく測った量**を載せるので、後から閾値を変えて再解釈できる。
  - ⚠️ **既知の限界**: 情報源にマウス入力が含まれるため、
    「読んでスクロールしているだけ」の時間を誤検知しうる（単体テストで仕様として固定）。

### ユーザビリティ

- **対応デバイス**: Windows 11（Surface Pro 8 + Type Cover）/ macOS 13 Ventura 以降（MacBook Pro/Air — JIS / ANSI 両キーボード対応）
- **UI**: ダッシュボードウィンドウ + オーバーレイウィンドウの 2 ウィンドウ構成
- **操作**: 通常運用は**セッション開始/終了**のみ。加えて **記録の一時停止・再開**（`set_recording_paused`）、
  **区間指定削除**（`delete_time_range`）、**作業の種類の宣言**（`declare_task_kind`・O1 のみ。5 択 = 論述 / 通信文 / デザイン・映像・制作作業 / vibe coding / その他・細切れの作業 —— ADR-016 判断 4b-2・ADR-037）、
  **参加者 ID 入力と提出**（`submit_latest_session` / `approve_pending_submissions`）、
  **自己マーカー**（`record_self_marker`）、macOS の**権限リセット / システム設定を開く**を持つ
  （★ モードごとに表示を出し分ける）。
  ⚠️ **2026-09-01 訂正 —— 旧文「セッション開始/終了と Monk Mode 切替のみ」は
  Monk Mode 削除（ADR-015 D2）と、その後に増えた操作面の両方で古い。**
