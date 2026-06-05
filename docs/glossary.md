# ユビキタス言語定義

このプロジェクトで使用する用語を統一する。同じ概念を異なる言葉で呼ばないこと。
新しい概念を導入する際は必ずここに追加する。

## ドメイン用語

| 用語 (日本語) | 用語 (英語) | 定義 | 使用例 |
|---|---|---|---|
| 作業状態 | Work State | PC 操作に現れる行動的シグナルから推定する作業上の状態。脳内状態の直接分類ではなく、介入判断に必要な状態表現 | 「作業状態スコアを 1Hz で更新する」 |
| 認知状態 | Cognitive State | ユーザーの知的作業における内的状態。GSE では直接読める対象として扱わず、UserLabel や説明概念として限定的に使う | 「認知状態を直接読むとは主張しない」 |
| フロー | Flow | 滑らかにアウトプットが出ている行動パターンの説明語。現行 HMM の `p_flow` は flow-like continuation の参考スコア | 「p_flow は Flow 断定ではなく参考スコア」 |
| インキュベーション | Incubation | 生産的な沈黙・熟考に近い行動パターンの説明語。現行 HMM の `p_incubation` は incubation-like pause の参考スコア | 「長い休止は Incubation と断定せず介入を defer する」 |
| スタック | Stuck | 作業停滞・摩擦が強い可能性を表す説明語。現行 HMM の `p_stuck` は Need 層の `stuck_likelihood` として使う | 「p_stuck が高くても Opportunity が低ければ介入しない」 |
| 生産的苦闘 | Productive Struggle | 困難に取り組むプロセス自体に学習・成長の価値がある状態。GSE が保護する対象 | 「生産的苦闘を阻害しない介入設計」 |
| 不便益 | Fubeneki | あえて不便を導入することで得られる便益。GSE の理論的基盤 | 「Wall は不便益に基づく介入」 |
| ナッジ | Nudge (Lv1) | `InterventionDecision.action == "nudge"` で発動する軽度介入。右端から小さく現れるサイドカードとして表示 | 「Nudge が表示されたがユーザーは作業を継続した」 |
| ウォール | Wall (Lv2) | `InterventionDecision.action == "wall"` で発動する強制介入。全画面ロック + スマートフォンアンロック | 「Wall が発動し Zen Timer が開始された」 |
| ゼンタイマー | Zen Timer | Wall 発動時にスマートフォン上で起動する 2 分カウントダウン。身体的休息を促す | 「Zen Timer 完了後に手動アンロック」 |
| モンクモード | Monk Mode | Wall 介入を無効化するトグル。Nudge のみ有効になる | 「Monk Mode 有効時は Wall が発動しない」 |
| フィジカルアンカー | Physical Anchor | 将来の Lv3/Lv4 介入。身体的活動（散歩等）を促す Flutter アプリ連携 | 「Physical Anchor は stretch goal」 |
| グラウンドトゥルース | Ground Truth (GT) | ユーザー自身が主観的に付与する認知状態ラベル。HMM 推定の正解データとして機能 (Phase 1) | 「Phase 1 で GT 付きセッションを収集」 |
| ユーザーラベル | UserLabel | GT の実体。`{Flow, Incubation, Stuck}` の 3 値 enum + timestamp として NDJSON に記録 | 「`⌘⇧⌥F` を押すと UserLabel が記録される」 |
| Need | Need | 介入が必要そうかを表す層。MVP では主に `p_stuck` を `stuck_likelihood` として利用する | 「Need は高いが Opportunity が低い」 |
| Opportunity | Opportunity | 今介入してよいかを表す層。idle、post-burst pause、cooldown、daily cap、recent dismiss、Monk Mode で判定する | 「Opportunity が低いため defer する」 |
| 介入判断 | InterventionDecision | `analysis::intervention` が返す介入ポリシー出力。`none` / `nudge` / `wall` / `defer` と説明スコアを含む | 「InterventionDecision を NDJSON に記録する」 |
| defer | defer | Need はあるが、今は介入機会ではないため先送りする判断 | 「active typing 中なので defer」 |
| daily cap | daily cap | 1日あたりの介入回数上限。通知疲れと過介入を防ぐ | 「Wall daily cap により defer」 |
| cooldown | cooldown | 介入後の再介入禁止時間。Nudge は 10 分、Wall は 60 分を MVP 初期値とする | 「cooldown 中なので Nudge を抑制」 |
| recent dismiss | recent dismiss | 直近で介入が拒否された事実。MVP 初期値では 20 分間、同種介入を抑制する | 「recent dismiss により defer」 |

## 技術用語

| 用語 | 英語表記 | 定義 | 関連用語 |
|---|---|---|---|
| HMM | Hidden Markov Model | 3 隠れ状態 × 26 観測ビンの確率モデル。Forward Algorithm で状態確率を逐次更新 | Emission Matrix, Transition Matrix |
| 遷移行列 | Transition Matrix | 3×3 の状態遷移確率行列。現在の認知状態から次の状態への遷移確率を定義 | HMM |
| 発射行列 | Emission Matrix | 3×26 の観測確率行列。各認知状態から各観測ビンが生成される確率を定義 | HMM, 観測ビン |
| 観測ビン | Observation Bin | 潜在軸 (X, Y) を 5×5 グリッド + 1 ペナルティビンに量子化した 26 離散値 (obs=0..25) | HMM |
| EWMA | Exponentially Weighted Moving Average | 指数加重移動平均。潜在軸の平滑化に使用。α が大きいほど最新値への追従が速い | 潜在軸 |
| ヒステリシス EMA | Hysteresis EMA | display_probs に適用する追加の平滑化層。状態確率の急激な変動を抑制 | EWMA |
| 潜在軸 | Latent Axes | 5 特徴量から算出する 2 次元空間。X 軸 = Cognitive Friction、Y 軸 = Engagement | 特徴量, 観測ビン |
| 認知的摩擦 | Cognitive Friction (X 軸) | 修正率・削除後休止・打鍵間隔・休止回数の加重合成。高いほど「つまずき」を示す | 潜在軸 |
| エンゲージメント | Engagement (Y 軸) | バースト長・打鍵速度・休止少なさの加重合成。高いほど「滑らかな出力」を示す | 潜在軸 |
| F1: 打鍵間隔 | Flight Time | 連続するキー押下間の中央値時間 (ms) | 特徴量 |
| F3: 修正率 | Correction Rate | (Backspace + Delete 回数) / 総キー数 | 特徴量 |
| F4: バースト長 | Burst Length | 打鍵間隔 < 200ms の連続入力の平均文字数 | 特徴量 |
| F5: 休止回数 | Pause Count | 2 秒以上の沈黙の回数 (30 秒ウィンドウ内) | 特徴量 |
| F6: 削除後休止率 | Pause-After-Delete Rate | (削除の後に 2 秒以上の沈黙) / 総削除数 | 特徴量 |
| ベースライン (β) | Baseline | 特徴量の正規化基準値。IME 状態に応じて coding β と writing β を切替 | IME, 正規化関数 φ |
| 正規化関数 φ | Normalization Function φ | φ(x, β) = clamp((x − β) / (κ · β), 0, 1)。κ=2.0 | ベースライン |
| バックスペースペナルティ | Backspace Penalty | 連続 14 回以上のバックスペースで obs=25（ペナルティビン）を強制発火。IME 変換中は抑制 | HMM, 観測ビン |
| 摩擦フロア | Friction Floor | サイレンス時に合成される最小摩擦値。Stuck 状態の侵食を防止 | サイレンス検出 |
| サイレンス検出 | Silence Detection | 2 秒以上のキー入力なし状態。段階的 α 調整 (0.15 → 0.18 → 0.25) で遷移 | EWMA |
| 1Hz ゲート | 1Hz Gate | Analysis スレッドが 1 秒ごとに HMM 推論を実行する時間制御機構 | Analysis Thread |
| IME_OPEN | — | 日本語 IME の ON/OFF 状態を示すアトミックフラグ。ON = 日本語入力モード | IME, ベースライン |
| IME_ACTIVE | — | IME 変換候補ウィンドウの表示状態を示すアトミックフラグ | IME |
| CGEventTap | — | macOS のキーボードイベント傍受機構。ListenOnly (Input Monitoring) と Default (Accessibility) の 2 モード | WH_KEYBOARD_LL (Windows 対応物) |
| Input Monitoring | — | macOS TCC 権限カテゴリ。kCGEventTapOptionListenOnly でキーイベントを受動的に傍受するために必要 | TCC, CGEventTap |
| Accessibility 権限 | Accessibility Permission | macOS TCC 権限カテゴリ。kCGEventTapOptionDefault でタップを作成するために必要。Input Monitoring のフォールバック先 | TCC, CGEventTap |
| CGKeyCode | — | macOS 固有の仮想キーコード (HIToolbox/Events.h)。hook_macos.rs 内で Windows VK コードにマッピング | VK |
| TIS | Text Input Source | macOS の入力ソース API。TISCopyCurrentKeyboardInputSource() で日本語 IME の ON/OFF を検出。GCD メインキュー経由で呼び出し必須 | IME_OPEN |
| dispatch_sync_f | — | GCD のメインキュー同期ディスパッチ関数。TIS クエリと AXIsProcessTrustedWithOptions に使用。フックスレッドから呼ぶ（メインスレッドからはデッドロック） | GCD |
| IME_COMPOSING | — | macOS 固有のアトミックフラグ。ローマ字→かな変換中（インライン下線テキスト）を示す。CGEventTap 内の状態機械で更新 | IME_ACTIVE |
| JIS_KEYBOARD_SEEN | — | macOS 固有のアトミックフラグ。JIS 物理 IME キーが検出された時点で true になり、TIS ポーリングを無効化する | TIS |
| USING_ACCESSIBILITY_FALLBACK | — | macOS 固有のアトミックフラグ。Input Monitoring から Accessibility へフォールバックしたことを示す | CGEventTap, TCC |
| FeatSnapshot | — | 1Hz ゲートで生成される特徴量 + HMM 状態確率のスナップショット (`analysis::loop_step::FeatSnapshot`)。NDJSON `feat` レコード + gse-replay 回帰比較の基本単位 | 1Hz ゲート, snapshot |
| LatestFeatState | — | 直近の FeatSnapshot を Tauri state として保持する構造。`get_intervention_decision` が F3/F4/F6 を読む | InterventionDecision |
| InterventionPolicyState | — | cooldown / daily cap / recent dismiss / Wall 累積時間 / last decision を保持する Rust 側ポリシー状態 | InterventionDecision |
| 混同行列 | Confusion Matrix | `[正解×推定]` の 3×3 行列 (`analysis::metrics::ConfusionMatrix`)。正解ラベルクラス × HMM argmax クラスの件数を格納 | UserLabel, F1 |
| Macro F1 | — | 各クラスの F1 を単純平均した値。固定分母 3 (scikit-learn 互換)。クラス不均衡に強くない代わりに minority class を重視 | 混同行列 |
| Micro F1 | — | 総 TP / 総 labels。多クラスでは accuracy と一致。GSE では分母は matched labels のみ (警告行きは除外) | 混同行列 |
| detection_lead_ms | — | UserLabel 時刻 - 最近傍同クラス argmax feat の時刻。正 = HMM 先行、負 = 遅延 (±60 秒窓内の最近傍を採用) | UserLabel, FeatSnapshot |
| recovered_at | — | Stuck ラベル後に p_flow > 0.5 に達する最初の FeatSnapshot 時刻。ログ記録時は null、`gse-replay --metrics` 実行時にオフラインで純粋関数算出 | compute_recovered_at |
| hmm_version | — | `analysis::engine::HMM_VERSION` の SemVer 値 (現行 `0.2.0`)。meta NDJSON エントリに埋まる、gse-replay が版不一致を WARN | HMM, schema |
| schema_dto | — | `logger::LogEntry` の `schemars::JsonSchema` 派生専用ミラー型 (`schema_dto::LogEntryDto`)。production path に影響させず JSON Schema を機械生成するための DTO | emit_schema, current.json |
| intervention_decision | — | MVP Opportunity の NDJSON ログ種別。action, need_score, opportunity_score, p_stuck, idle_ms, wall_accum_ms, reason, suppressed_by を含む | InterventionDecision, schema |
| metrics.json | — | `gse-replay --metrics --json` の出力 (1 KB/session)。gse-dataset repo の `metrics/P*/<os>/` に配置する共有アーティファクト | aggregate_metrics, UC-GT3 |
| gse-dataset | — | セッションメトリクスの集約データ repo (`mikotomiura/gse-dataset`, private)。生 NDJSON は絶対に置かず、`metrics/` と機械生成 schema のみ tracked | metrics.json, schema sync |
| 被験者 ID | Participant ID | データ repo での匿名化識別子。`P000` (開発者自身) / `P001-P005` (Phase 2+ 外部被験者) | IRB, consent |
| Phase 2a Go/No-Go | — | `aggregate_metrics.py` が出力する判定。Stuck precision 平均 ≥ 0.6 かつ n ≥ 5 で GO、未満は INCONCLUSIVE | metrics.json, baseline_metrics.md |

## 略語

| 略語 | 正式名称 | 意味 |
|---|---|---|
| GSE | Generative Struggle Engine | 本プロダクトの名称 |
| HMM | Hidden Markov Model | 隠れマルコフモデル |
| EWMA | Exponentially Weighted Moving Average | 指数加重移動平均 |
| IME | Input Method Editor | 日本語入力メソッドエディタ |
| IPC | Inter-Process Communication | プロセス間通信（Tauri のフロントエンド↔バックエンド通信） |
| NDJSON | Newline Delimited JSON | 改行区切り JSON（セッションログ形式） |
| VK | Virtual Key | 仮想キーコード（Windows API 由来。macOS では CGKeyCode からマッピング） |
| TCC | Transparency, Consent, and Control | macOS のプライバシー権限管理フレームワーク。Input Monitoring, Accessibility 等のカテゴリを管理 |
| GCD | Grand Central Dispatch | macOS のスレッドディスパッチ機構。dispatch_sync_f でメインキュー実行に使用 |
| CDHash | Code Directory Hash | macOS コード署名のハッシュ値。TCC データベースでアプリを識別。ad-hoc 署名では不安定 |
| CSP | Content Security Policy | コンテンツセキュリティポリシー |
| UIPI | User Interface Privilege Isolation | UI 特権分離（Windows セキュリティ機構） |
| TSF | Text Services Framework | テキストサービスフレームワーク（Windows IME 基盤） |

## 禁止用語

| 禁止 | 代替 | 理由 |
|---|---|---|
| winapi | windows crate | winapi crate はメンテナンス停止。公式の windows crate (v0.58+) を使用 |
| allowlist | capabilities | Tauri 2.0 では v1 の allowlist を廃止し capabilities に移行 |
| 集中度 / 集中状態 | Flow | 「集中」は曖昧。Csikszentmihalyi の Flow 概念を正確に使用する |
| 行き詰まり度 | p_stuck / Stuck 確率 | 「度」は曖昧。確率値で語る |
| タイマー | Zen Timer | 「タイマー」単体では Wall の Zen Timer か他のタイマーか不明 |
| ロック / ブロック | Wall (Lv2) | 介入レベルを明示する |
| kCGEventTapOptionListenOnly | Input Monitoring tap / ListenOnly tap | API 定数名をそのまま使わず、権限名で説明する |
| kCGEventTapOptionDefault | Accessibility tap / Default tap | 同上 |

## 用語の追加・変更ルール

1. 新しい概念を導入する際は、まずここに追加してから実装する
2. 既存用語の意味を変える場合は、変更履歴を残す
3. ドメイン用語は日本語・英語の両方を定義する
4. 学術的な裏付けがある場合は参考文献を括弧内に記載する
