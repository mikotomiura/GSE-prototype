# ユビキタス言語定義

このプロジェクトで使用する用語を統一する。同じ概念を異なる言葉で呼ばないこと。
新しい概念を導入する際は必ずここに追加する。

## ドメイン用語

| 用語 (日本語) | 用語 (英語) | 定義 | 使用例 |
|---|---|---|---|
| 認知状態 | Cognitive State | ユーザーの知的作業における内的状態。GSE では Flow / Incubation / Stuck の 3 状態を定義 | 「認知状態を 1Hz で推定する」 |
| フロー | Flow | 集中し滑らかにアウトプットが出ている状態。短い打鍵間隔、長いバースト、低い修正率が特徴 (Csikszentmihalyi 1990) | 「p_flow > 0.8 のとき Flow と判定」 |
| インキュベーション | Incubation | 意識的思考を離れ、無意識的に問題を処理している休止状態。生産的な沈黙 (Sio & Ormerod 2009) | 「長い休止でも Incubation なら介入しない」 |
| スタック | Stuck | 問題解決が行き詰まり、同じアプローチを繰り返している状態。高い修正率、削除後の長い休止が特徴 (Ohlsson 1992) | 「p_stuck > 0.6 で Nudge を発動」 |
| 生産的苦闘 | Productive Struggle | 困難に取り組むプロセス自体に学習・成長の価値がある状態。GSE が保護する対象 | 「生産的苦闘を阻害しない介入設計」 |
| 不便益 | Fubeneki | あえて不便を導入することで得られる便益。GSE の理論的基盤 | 「Wall は不便益に基づく介入」 |
| ナッジ | Nudge (Lv1) | p_stuck > 0.60 で発動する軽度介入。赤いビネット効果をオーバーレイ表示 | 「Nudge が表示されたがユーザーは作業を継続した」 |
| ウォール | Wall (Lv2) | p_stuck > 0.70 が累積 30 秒で発動する強制介入。全画面ロック + スマートフォンアンロック | 「Wall が発動し Zen Timer が開始された」 |
| ゼンタイマー | Zen Timer | Wall 発動時にスマートフォン上で起動する 2 分カウントダウン。身体的休息を促す | 「Zen Timer 完了後に手動アンロック」 |
| モンクモード | Monk Mode | Wall 介入を無効化するトグル。Nudge のみ有効になる | 「Monk Mode 有効時は Wall が発動しない」 |
| フィジカルアンカー | Physical Anchor | 将来の Lv3/Lv4 介入。身体的活動（散歩等）を促す Flutter アプリ連携 | 「Physical Anchor は stretch goal」 |

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
