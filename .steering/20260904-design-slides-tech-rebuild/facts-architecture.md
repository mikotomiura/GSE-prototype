# 一次資料メモ (3) アーキテクチャ・ワークフロー・各層のつながり

> 出典は `docs/architecture*` / ADR / `src-tauri/src/**` / CI の実測 (2026-09-04)。

## 前提: 「コード変更ゼロ」の ADR が多い

ADR-017 / 018 / 021 / 022 はいずれも本文末尾で **「コード変更ゼロ」** を明記
(ADR-017:330 / ADR-018:10, 184 / ADR-021:466 / ADR-022:556)。
→ **表現チャネルと Physical Anchor は設計文書だけが存在し、本体実装は 1 行もない**。

## 層 —— ⚠️ 番号体系が 6 系統併存している

### v2 の 7 層 = **処理の呼称の SSOT** (gse-v2-overview.md:75-91 / 対応表 :117-125)

| 層 | 内容 | 現行実装 |
|---|---|---|
| [0] Session Context | `task_kind` / `work_intent` / `support_consent` / `intervention_profile` | `session_meta` に `task_kind` を記録するのみ（記録/✗） |
| [1] Domain Event Adapter | Writing / Agentic Coding / Creative Editing | **なし**（`input/` が直接 `analysis/` へ）✗ |
| [2] Privacy Boundary + Event Envelope | 内容を除去し操作種別・量・時間・結果だけ保持 | 本文非保存は徹底。共通 `EventEnvelope` 外枠は**未実装** ○/✗ |
| [3] Domain-local Feature Extraction | タスク固有特徴量 | `features.rs` (F1/F3/F4/F5/F6) ◎ Writing 前提 |
| [4] Work-State Proxy | friction / stuck_likelihood / engagement / incubation_like_pause / flow_like_continuation | `engine.rs` (HMM) → `loop_step.rs` ◎ Writing 前提 |
| [5] Opportunity & Receptivity | breakpoint / receptivity / cooldown / daily_cap / recent_dismiss | `intervention.rs` ◎（receptivity は**分解形**） |
| [6] Intervention Decision Engine | none / defer / nudge（⚠️ zen / wall は ADR-015 D1 で削除） | `intervention.rs:16-20` ◎（Consent 軸は未実装） |
| [7] Outcome & Harm Evaluation | recovery / loop escape / helpfulness / annoyance / autonomy / reuse | `metrics.rs` + `intervention_eval.rs` △（harm は HIR のみ） |

⚠️ gse-v2-overview.md:95-105 逐語「repo には既に **L1/L2 を別の意味で使う体系が 3 系統**ある」。
`docs/glossary.md:249` は **「Mh-D 内部の `L1`〜`L4`（層番号の新設）」を禁止用語**とし、
代替を「既存の 7 層 `Layer 0`–`Layer 7`」としている。

### 併存する 6 系統
| # | 体系 | 出典 |
|---|---|---|
| 1 | 7 層 Layer 0–7（**SSOT**） | gse-v2-overview.md:75-91 |
| 2 | MhD(L1) → Need 層(L2) | glossary.md:14, 219 |
| 3 | 表現層の 層 0–3（**音**） | glossary.md:105-108 |
| 4 | 層 A / 層 B（曝露予算） | glossary.md:128 / expression-channel.md:132-157 |
| 5 | モデル成熟 M1–M4（★ **撤回済み**） | ADR-021:400-420 |
| 6 | スライドの L0/L1/L2/L2' | 現行スライド:112-117 |

### ⚠️ 「4 層パイプライン」は 2 通りあり、現行スライド版は内部矛盾している
| 出典 | 中身 |
|---|---|
| wbs-verification-halfyear.md:23-24 / research-positioning.md:892 | 行動シグナル層・作業状態推定層・介入機会判定層・介入ポリシー層 |
| 現行スライド:155-161 | 見出しは「**4 層**」だが本文は **5 項目**（Sensing / Inference / Decision / Physical Anchor / Expression） |

対応（本レポートの導出）:
```
【1】Sensing            ⟷ Layer 1–2（adapter/envelope 未実装なので実質「入力捕捉」）
【2】Inference          ⟷ Layer 3–4
【3】Decision           ⟷ Layer 5–6   （WBS はこれを 2 層に割る）
【4】Physical Anchor    ⟷ 7 層の外（出口・ADR-018）
【5】Expression Channel ⟷ 7 層の外（表現・ADR-017 D1）
                          Layer 7 (Outcome & Harm) はスライドに無い
```

## スレッドモデル

`docs/architecture.md:89` 逐語「GSE は **8 つのスレッド/タスク**で構成される
（★ G1 モード時のみ 2 つ増える。⚠️ Cloak Resolver は Windows のみ）」。

`lib.rs` 内の `thread::spawn` は **11 箇所**（実測）:
| path:line | スレッド | 起動条件 |
|---|---|---|
| lib.rs:3339 | ★ **Analysis スレッド（1Hz）** | 常時（`setup()` の**外**） |
| lib.rs:3466 | IME Monitor | 常時（`setup()` の**外**） |
| lib.rs:4055 | liveness（フック生存監視）TICK_MS=1000 | 常時 |
| lib.rs:4557 | Probe Scheduler（1000ms） | `!probes_disabled` |
| lib.rs:3051 | 終了処理 | 常時 |
| lib.rs:1970 | 提出収束器 reconcile | `auto_submit_enabled()` |
| lib.rs:2670 / 4345 | G1 二重起動チェック / ブロック自動終了 | G1 |
| lib.rs:3780 / 3873 / 3978 | O1 日次ローテート / 非打鍵ドレイン / 孤児 sweep | O1 |

`lib.rs` 外:
logger.rs:1479 (Logger) / hook_windows.rs:377 / hook_macos.rs:613 (KB Hook) /
ime_windows.rs:253 (IME Polling) / ime_windows.rs:405 (**Cloak Resolver・Windows 限定**) /
observe_windows.rs:320・observe_macos.rs:448 (O1 非打鍵観測)

★ Analysis と IME Monitor だけ `setup()` の外で起動する（lib.rs:3563-3566。
Tauri 初期化がフックを無効化する問題の回避）。

## 1 秒ループの起点 = lib.rs:3339

```
lib.rs:3366  o1::analysis_gate_open() ── 閉なら空読み + ANALYSIS_IDLE=true + 50ms sleep
lib.rs:3382  should_reset.swap(false) → state.reset(now_ms(), 600)
lib.rs:3387  timeout = state.next_engine_update_ms - current   ← 「次の 1Hz マークまでの残り」
lib.rs:3392  rx.recv_timeout(timeout)
lib.rs:3405  is_paste なら clipboard_char_count() → LogEntry::Paste
lib.rs:3423  tick_now = now_ms();  ime_open = input::hook::IME_OPEN.load(Relaxed)
lib.rs:3426  step(&mut state, &engine, input, tick_now, ime_open)   ← 本体は analysis/loop_step.rs
lib.rs:3431  out.key  → LogEntry::Key を try_send
lib.rs:3438  out.feat → LatestFeatState に格納 → LogEntry::Feat を try_send
```
⚠️ **`lib.rs` は `features` / `engine` を直接呼ばない**。すべて `step()` の内側
（lib.rs:3428-3430 が architecture-rules ルール 6 を根拠に明記）。

## チャネル (crossbeam)

| path:line | 型・容量 | 送信 → 受信 |
|---|---|---|
| lib.rs:3283 | `bounded::<InputEvent>(64)` | KB Hook → Analysis |
| lib.rs:3837 | `bounded::<()>(1)` | フックコールバック → IME Polling（wake-on-keystroke） |
| lib.rs:3863/3865/3868 | `bounded(256)/(256)/(16)` | observe → ドレイン（フォーカス遷移 / ポインタ 1 秒ビン / secure_input） |
| logger.rs:1389 | `bounded::<LogEntry>(512)` | 全スレッド → Logger |
| ime_windows.rs:402 | `bounded::<CloakEvent>(256)` | フックコールバック → Cloak Resolver |

Atomic: `input/hook.rs` の `pub static` は **19 本**
（IME_ACTIVE:28 / IME_OPEN:37 / LAST_KEY_MS:51 / HOOK_ACTIVE:170 / EVENTS_DROPPED:211 ほか）。
Ordering 方針 (architecture.md:161): 「Relaxed for LAST_KEY_MS（近似で十分）、Acquire/Release for IME 状態」。

## ⚠️★ IME_ACTIVE は推論を止めない（2026-08-23）

architecture.md:104-111 逐語: 旧設計は「IME 候補ウィンドウ表示中は HMM 推論を一時停止」だったが、
実測でこの信号は**変換セッション全体**を覆うと判明。pause すると日本語論述の推定窓が
**約 56〜60%**（実データ fixture `phase1_ime_heavy` では **94%**）消える。
→ `lib.rs` と `loop_step.rs` の両方から `set_paused` を外し、**`HMM_VERSION` 0.4.0 → 0.5.0**。

## モジュール境界の不変条件

- agent-shared.md 制約 11: `analysis/` 内で OS API を直接呼ばない
  （OS 依存は `input/` + `sensors*.rs` + `overlay_panel.rs` + `lib.rs` の `#[cfg]` に限る）
- repository-structure.md:167: `analysis/` に置くべきでないもの =
  OS API 呼び出し / 入力イベント捕捉 / **タイムスタンプ生成**（`SystemTime` は `lib.rs` で付与）
- **依存方向**（2026-09-01 訂正）: **input → analysis の片方向のみ**。
  ⚠️ 旧文の括弧「features.rs の型を hook.rs が利用するケースなし」は**事実と正反対**。
  実測: `input/hook.rs:6` が `use crate::analysis::features::InputEvent;`、
  `hook_windows.rs:116` が `crate::analysis::key_gate::is_feature_key(vk_code)` を呼ぶ（計 6 箇所）。
  ★ 逆方向（analysis → input）は 0 件なので「片方向のみ」という結論自体は正しい。

### 破ると何が壊れるか
1. **`analysis/` に OS API を入れると両 OS 共通テストが崩れる**
   (development-guidelines.md:132「単体テスト｜`analysis::features`/`engine`/`metrics`/`logger`｜高｜**両 OS 共通**」)
2. **`#[cfg]` の付け忘れは相手側 OS の CI で赤になる**。2026-08-10 に
   `liveness::macos_tick_tests` が macOS の許容幅前提のまま Windows CI で落ちた。
   規約は「**両 OS に対のテストを置く**」（実例 `input/liveness.rs::tick_indicates_input`:
   Windows=等値 / macOS=250ms 許容幅）
3. **フックコールバックのブロッキング禁止**（Atomic + channel send のみ）。分離の実例が
   **Cloak Resolver スレッド** —— architecture.md:98 逐語
   「⚠️ フックコールバックでは `GetClassNameW` を呼べない（`hook-constraints` Win-1）ための分離」
4. `input/ime_cloak.rs` は**意図的に `#[cfg]` を付けない**（mod.rs:4-7「★ そうすると macOS の CI でも
   `CloakFold` のテストが走る」）
5. **本番とリプレイが同じ変換経路を通ることが回帰保護の前提**（architecture.md:201-202）

### ⚠️ Windows TSF 制約の理由が 2026-08-22 に訂正されている
旧文「グローバル TSF フック禁止: **UIPI でブロックされる**」は**誤り**。
UIPI の禁止 5 項目に TSF も COM も含まれず、同一整合性レベルでは発動すらしない。
**真の障壁はアーキテクチャ**（`ITfThreadMgr::Activate` は "Activates TSF for **the calling thread**"、
`AdviseSink` にリモート対象の引数が構文上存在しない）。
採る手段は **WinEvent (`WINEVENT_OUTOFCONTEXT`)** —— DLL 注入不要・プロセス跨ぎ可・
**コールバック引数に文字列が 1 つも無く content-free が構造的に保証される**。
⚠️ **未追随**: architecture.md:624 と `.claude/skills/architecture-rules/SKILL.md:96` が旧説のまま。

## 介入決定エンジン (analysis/intervention.rs・609 行)

```rust
// intervention.rs:16-20
pub enum InterventionAction { None, Nudge, Defer }     // ★ 3 値のみ
```
⚠️ `intervention.rs:50-59` に**もう 1 つ enum `OpportunityReason`（8 値）**がある。
これは加点**理由**であって action ではない。**「8 種類の介入」と読ませない。**
`#[serde(skip)]`（:132）で NDJSON にも IPC にも出ず in-memory のみ。

### 定数（実測・全件）
| 定数 | 値 | 位置 |
|---|---|---|
| `NUDGE_NEED_THRESHOLD` | **0.60** | :3 |
| `NUDGE_OPPORTUNITY_THRESHOLD` | **0.35** | :4 |
| `NUDGE_COOLDOWN_MS` | **10 分** | :5 |
| `RECENT_DISMISS_MS` | **20 分** | :6 |
| `SHORT_PAUSE_MIN_MS` / `MAX_MS` | **2,000** / **8,000** | :7-8 |
| `MEDIUM_PAUSE_MAX_MS` | **30,000** | :9 |
| `AWAY_IDLE_MS` | **180,000**（idle≥180s で介入全停止） | :10 |
| `NUDGE_DAILY_CAP` | **6** | :11 |

⚠️ intervention-decision-engine.md:120-122 逐語:「旧文の『Phase1 完了まで定数変更禁止』は前提が失効した。
… **定数は現在も未変更**だが、それは『変更禁止だから』ではなく『まだ触っていない』からである。」

### Need と Opportunity の分離
- **Need** = `p_stuck` そのもの（:245 `let need_score = p_stuck;`）
- **Opportunity** = `calculate_opportunity()`（:398-439）。入力は
  `idle_ms` / `f3` / `f4` / `f6`:

| 条件 | 加点 | reason |
|---|---|---|
| 2,000 ≤ idle ≤ 8,000 | **+0.45** | ShortPause |
| 8,000 < idle ≤ 30,000 | **+0.35** | MediumPause |
| idle < 2,000 | **−0.20** | ActiveTyping |
| 30,000 < idle < 180,000 | **+0.15** | LongPause |
| ShortPause かつ f4≥4.0 かつ f3<0.20 かつ f6<0.30 | **+0.25** | PostBurstPause |
| (f3≥0.20 or f6≥0.30) かつ 2,000≤idle≤30,000 | **+0.15** | CorrectionAfterPause |
| (f3≥0.20 or f6≥0.30) かつ idle<2,000 | **−0.20** | ActiveCorrectionLoop |

最後に `clamp(0.0, 1.0)`。

### decide() の決定過程 (:239-317)
```
:249  idle_ms >= AWAY_IDLE_MS(180s)  → suppressed_by "away_idle" ; None
:252  need_score < 0.60              → None
:254  opportunity_score >= 0.35      → Nudge
:257  それ以外                        → Defer
:260  Nudge なら apply_nudge_suppressions(); 非空なら → Defer
:273  correction_floor veto（既定 off・評価専用）→ Defer
:297  record_activation(candidate, now_ms)
```
suppression (:334-346) —— ⚠️ **`current_action != Nudge` のときだけ** cap/cooldown を見る
（表示継続中の Nudge を自分で消さないため）: `daily_cap` / `cooldown` / `recent_dismiss`。

★ **veto の不変条件** (:271-272 逐語):「この veto は `record_activation` より**前**に置くこと。
さもないと veto で defer に落とした nudge が nudge_count を増やし cooldown/cap を誤って消費する。」

cap のカウント (:355-366): `action == current_action` なら何もしない（**遷移時のみ加算**）。

ログ間引き (:368-395): `action != None || suppressed_by 非空 || need_score >= 閾値` のときだけ
「面白い」とみなし、キーが変わったか **5 秒経過**したときだけ書く。

### 二重進行の防止
architecture.md:219 逐語:「Main Window の `get_intervention_decision` 呼び出し**だけ**が policy state を
進める。Overlay Window は `last_decision` を読み取るだけにし、2 つの WebView による
cooldown / cap の二重進行を防ぐ」。

`INTERVENTION_ENABLED`（lib.rs:111・**既定 true**）。★ **O1 では起動時に強制 false**（lib.rs:3245。
理由「O1 は `record_session_meta` を通らないので何もしなければ Nudge が出る」）。

### 未実装 (Layer 5–7)
- **Consent 軸 (`SupportConsent`) は未実装** (ADR-004:15)。決定は `ObserveOnly → none` の硬いゲート。
  ⚠️ **倫理・自律性の正当化であって効果エビデンスではない**。
- decision reason code のログ化・`policy_version` 刻印は未実装
- **統合 `receptivity` スコアは作らない**（分解維持・ADR-007）
- `DismissReason` の現行は 4 値のみ: `NotStuck / WantToStruggle / JustClose / Silent`
  （⚠️ 旧文の `Completed` / `IdleTimeout` は存在しない）
- ⚠️ **ADR-004:14 本文は「`InterventionAction{None,Nudge,Wall,Defer}`」のまま**（ADR-015 で Wall 削除済み）。
  ADR 本文は書き換えない規約なので**後発 ADR で読み替える**。

## 表現チャネル —— ⚠️ ADR-017 単独では古い。現行裁定は ADR-021 + ADR-022

### 実装状況: **本体アプリ未配線のプロトタイプ段階**
本体 grep（`src-tauri/src` + `src`）: `expression` / `physical_anchor` / `EXPR_VERSION` は **0 件**。
★ ただし **repo 内にプロトタイプが実在する**:
| 実体 | パス |
|---|---|
| 平滑化器 (`EXPR_VERSION = "0.3.0-step4"`) | `.steering/20260811-expression-prototype-step0/scripts/expr_smooth.py:59` |
| 層 0 ドローン (config + player + selftest) | `experiments/20260812-expression-layer0-drone/` |
| 層 2 グレイン + **ABX 結果 15 件** | `experiments/20260812-expression-step4-grain/` |
| 検出力計算 | `experiments/20260815-expression-power/` |
| **層 A 視覚プレイヤー** | `experiments/20260902-expression-layerA-visual/player/layerA.html` |

→ ★ 「未実装」の一語で書くと**過小評価**。正確には「**本体未配線のプロトタイプ段階**」。

### ⚠️★★★ 現行の境界契約 (ADR-021 D4 が ADR-017 D2 を改訂・:186-192)
| フィールド | 値域 | 備考 |
|---|---|---|
| **`level`** | **`stable` / `friction_rising` / `stuck`** ← **3 値**（旧 4 値から `intervention_active` を除去） | 作業状態（MhD の出力）。⚠️ `p_stuck` 等の**連続値を載せない** |
| **`invitation`** | **`none` / `present`** ← **新設・二値のみ** | Need/Opportunity（決定）の出力。⚠️ **理由・強度・残り時間を載せない** |
| `seq` | 単調増加整数 | 欠落検出 |
| `emitted_at` | **秒粒度** | ⚠️ ミリ秒粒度にしない |
| `epoch` | 不透明な識別子 | PC 再起動 / 再ペアリングで新しくなる。⚠️ 本人の識別子を流用しない |

**発火条件**: `level` が変わったときだけ。⚠️ **1Hz を流さない**。

4 値を 3 値 + 二値に割った根拠 (ADR-021:194-208): ① **4 値は相互排他ではない**（介入中も下の作業状態は
3 値のいずれか。1 enum に畳むと介入中は状態が消える）② `level` は MhD（推定）、招待は
Need/Opportunity（決定）で **ADR-004 の境界では別層** ③ set size 3 は周辺視のみでの同定率が最も高い
（90%・set size 7 では 76%）[P250]。

**再接続の意味論 4 項**: ① `epoch` が変わったら `seq` 比較を打ち切り初期同期からやり直す
② 同一 `epoch` で `seq` が戻ったら捨てる ③ 再接続直後は現在の `level` を 1 発だけ送る
（⚠️ 履歴を再送しない）④ 一定時間 `epoch` が更新されなければ失効させ**層 0 へ縮退**。

### 方向・運搬路
- **PC → スマホの一方向** (ADR-017 D3)。⚠️ **inbound の「歩いた」二値経路を第 1 版で作らない**。
  根拠は ADR-018 D4 で書き換え: 旧「完了条件が時間＋復帰なのでセンサの量が寄与しない」→
  新「**完了判定を置かない ＝ センサが寄与しうる判定が存在しない**」。→ **再燃しなくなる**。
- 運搬路の 4 制約: ① PC 側に**常設の LAN リスナを置かない** ② on-demand 起動＋停止時ティアダウン
  ③ チャネル不在でも表現が成立（層 0 へ縮退）④ チャネルが無い間のフレームを捏造しない。
  ⚠️ **Wall Server 型の LAN HTTP を無審査で復活させない**。
- セキュリティ最小要件 S1–S6。⚠️ **wire protocol は未決 (W-1)** —— 実装着手時の別 ADR。

### ADR-022 が確定した媒体実装制約 —— ★ 2 つの OS は正反対
| | **iOS** | **Android** |
|---|---|---|
| ロック画面ウィジェット | 使える | ❌ 実質使えない（AOSP 既定 OFF・**BFU で例外なく閉じる**） |
| ライブ壁紙 | ❌ 存在しない | 使える（キーガード窓に `FLAG_SHOW_WALLPAPER`） |
| 持続アニメーション | ❌ 不可（最大 2 秒・AOD では 1 フレームも出ない） | 可（画面点灯中のみ） |
| 色 | ❌ **OS が強制的に desaturate** | 自由 |

**決定**: **iOS = ロック画面ウィジェット / Android = ライブ壁紙** (ADR-022:214)。
- ⚠️ **iOS で Live Activities を採らない** —— 8 時間上限＋ push-to-start の alert が "requirement" で、
  **技術的理由だけで 1 日 2–3 回の「画面点灯 + 提示」が発生**し、Need/Opportunity を通らない介入になる。
- ⚠️ **A-7（振幅 ~1°・1–3 Hz の持続振動）を第 1 版の符号から外す** (ADR-022 D1)。
  決定的な理由は「**非対称そのもの**」—— 符号が OS で違うと **OS が表現と交絡し評価が壊れる**。
  代替は **「面の縁が開く/閉じる」（開口＝招待）** という静的符号。
- ⚠️ **「1°」を絶対値で使わない** —— iOS `accessoryCircular` は 76×76pt = **2.26°** しかない。
- ⚠️ **iOS は APNs を経由せざるを得ず、`level`/`invitation`/`seq` の値と状態遷移の時刻列が
  Apple 側のメタデータになる**。逐語「content-free の原則は『文字列を送らない』までは守れるが、
  **iOS では『タイミングを漏らさない』は守れない**」。**Android ではこれが起きない**。

### 層 A の設計要件 (ADR-021:380-391)
A-1 設計上限は 4 秒でなく **2 秒** / A-2 争点は意味写像 / A-3 **未学習の抽象表現は 3 値でも
チャンスと区別がつかない**（30–39% vs チャンス 33%）/ A-4 段数は視線コストで切る /
A-5 1 目盛りの段数は安全域 5・上限 7 / A-6 **色を主符号にしない** / A-8 状態遷移の検知可能性を別に試験。

⚠️★★★ **必ず併記する留保** (:393-395):「**上記のどの研究も『内的な認知状態』を抽象表現で
弁別させていない。**弁別対象はすべて外的な量である。→ 層 A の弁別は
『文献で許可されているが、実証されてはいない』」。

### ⚠️ D9 の前提が未実装
ADR-021:44 (B1) は「推論層は `WorkStateEstimate` に `uncertainty` / `evidence_quality` を必須で持つ」と
書いているが、根拠の `heads/mod.rs:20` は **doc コメント**で、同 :16-23 が
「本モジュールは現行 engine の形に合わせ、**潜在二軸の算出だけ**を trait 化する。
`infer -> WorkStateEstimate` への移行は **Epic 3**」と明記。
実測: **`WorkStateEstimate` / `uncertainty` / `evidence_quality` / `scope_fit` は
`src-tauri/src/` に 0 ヒット**。

## Physical Anchor (ADR-018) —— **未実装**

ADR-018:10 逐語「**コード変更ゼロ**（Physical Anchor は未実装であり、本 ADR は設計語彙と
評価設計のみを動かす）」。architecture.md:665-666「⚠️ 本フェーズでは未実装
（★ Phase1 の実体は **WoZ ＋ 自己申告**）」。

| 決定 | 内容 |
|---|---|
| D1 | 「完了条件を持つ介入」→「**身体的回帰への方向づけ (invitation)**」。**系はその開始も完了も判定しない** |
| D2 | **時間長・往復回数・再開のタイミングに系の側の閾値を置かない**。⚠️ **タイマー・カウントダウン・残り時間表示を実装しない** |
| D3 | 「離席候補区間があり、復帰した」は**観測として残すが完了判定に使わない**。UI・表現層・ログのいずれにも `completed` / `達成` に相当する語を置かない |
| D5 | 評価量を実行率/完了率 → **招待の受容 ＋ 機会保存の行動指標**（`paste_after_stuck_rate` / `self_recovery_without_paste` / `manual_contribution_ratio`）へ |
| D7 | **段階呼称 Lv1〜Lv4 を廃止方向**、実体名で呼ぶ。★ コード側の出現は **0 箇所** |

**センシングの恒久除外**: 歩数 / 距離 / 速度 / 位置情報は
**GSE 本体（介入の判定・完了・表現・主評価）から恒久的に外れた** (ADR-017 D10)。

**構造的必須性** (ADR-017:195-198 D7 逐語):
「**不便益の認定条件 1（益は不便だからこそ＝労力）を満たすのは Physical Anchor だけである** [P170]。
⚠️ **Lv1 Nudge は非ブロック・自動消失＝労力を課さない**」
→ expression-channel.md:498-499「表現層と Physical Anchor は『あれば良い』関係ではなく、
**片方だけだと表現層が『装飾』に落ちるという構造的な関係**にある」。

**招待を差し出す面は PC 側** (ADR-021 D6)。⚠️ **文献では決められない**。根拠は
① 段階をまたがせるな（`read → act` 同一面継続希望 95.6%）② PC 側に dismiss 記録機構が既に実在
（intervention.rs:229）③ 境界の一方向性を保てる ④ 本人は既に PC の前にいる。

**代償を隠さない** (ADR-018:163-172): ⚠️「不便が実際に担われたか」を系が確認する手段が無くなる／
閾値が無いため「介入が発火したのに何も起きなかった」を失敗と切り分けにくい。

## 回帰保護

development-guidelines.md:83-91 逐語:「ゴールデンセッション NDJSON を入力に `gse-replay` CLI で
`analysis::loop_step::step()` を再実行し、`FeatSnapshot` 列の **byte-equal 一致** をもって
回帰保護する。リプレイ CLI 1 本で ① 単体 ② 統合 ③ 回帰 ④ Ground Truth 評価
⑤ パラメータチューニング の 5 役を兼ねる」。

⚠️★★★ **`Cargo.toml` は repo 直下に無く `src-tauri/` にある**。

```bash
cd src-tauri
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json
cargo test --workspace
cargo run --bin emit_schema      # 出力を src-tauri/schema/current.json と byte-equal 比較
```

Fixture 11 本 / **Snapshot 6 本**（minimal / argumentative_ime_mixed / vibe_coding_ime_mixed /
deep_silence / category_coverage / phase1_ime_heavy）。
`serde_json` は `features = ["float_roundtrip"]`（Cargo.toml:86。逐語「無効だとデシリアル時に
数 ULP のドリフトが入り snapshot 比較が落ちる」）。

**Schema drift 検知**: `schema_dto::LogEntryDto` は `logger::LogEntry` の schemars 派生専用ミラー。
理由 (schema_dto.rs:9-14 逐語):「`logger::LogEntry` は `f64` の小数桁数固定フォーマット (`{:.4}`) を
`writeln!` で直接指定しており、`serde::Serialize` 経由で出すと形式が崩れて
gse-replay の**ゴールデン byte-equal が落ちる**。したがって `LogEntry` 本体には `Serialize` を派生させない」。

CI (`.github/workflows/ci.yml`) の `check` ジョブ: build → `cargo test --features package --workspace`
→ gse-replay スナップショット照合 → `emit_schema` の diff。
runner は **self-hosted 実機**（macOS = `[self-hosted, gse-mac]`、Windows は probe して 30 秒で
hosted へ fallback）。`frontend-check` は ubuntu で `tsc --noEmit` / `npm run build` /
`check_vignettes.py` / `capabilities_gate.py` / `check-shell-portability.sh` /
**`md2docx.py --selftest`** / **`check_doc_lexicon.py`** / **`check_citations.py`**。

## 各アーキのつながり（契約 = 型・イベント）

```
[OS]  Win: WH_KEYBOARD_LL + WinEvent  /  mac: CGEventTap + CFRunLoop
        hook_windows.rs:377                 hook_macos.rs:613
   │ ★契約① InputEvent (features.rs:4-15)
   │   { vk_code, timestamp, is_press, is_repeat, is_backspace, is_paste }
   │   ⚠️ 文字内容なし。macOS は CGKeyCode→VK 変換済み
   │ crossbeam bounded(64) ＋ Atomic (IME_OPEN / LAST_KEY_MS ほか)
   ▼
[Analysis 1Hz]  lib.rs:3339 → step()  loop_step.rs:221
   ★契約② LoopInput = Key(InputEvent) | ImeActivate{active}(replay 専用)
   FeatureExtractor(600) → Features (F1/F3/F4/F5/F6)
   ★契約③ DomainInferenceHead::latent_axes(&Features, ime_open) -> (X, Y)   heads/mod.rs:145
        head 選択は task_kind（宣言）/ β は head の所有物 / ime_open は Writing head 内部の信号
   量子化 obs = x_bin*5 + y_bin (0..24) / obs=25 = BS ペナルティビン
   HMM Forward (3 states × 26 bins) → EWMA → ヒステリシス EMA
   ★契約④ FeatSnapshot (loop_step.rs:134-194)  ⚠️ head_id は入れない（ゴールデンが壊れる）
   ├─ LatestFeatState(Arc<Mutex<Option<..>>>) ─┐
   └─ LogEntry::Feat → bounded(512) ───────────┼─→ [Logger] 5 秒フラッシュ → NDJSON
                                               │     ★契約⑦ LogEntry 27 variant
   ▼                                           │       = NDJSON の "type" タグ付き封筒
[決定層] get_intervention_decision  lib.rs:612  │
   ★契約⑤ InterventionInput { now_ms, p_stuck, f3, f4, f6, idle_ms }
   ★契約⑥ InterventionDecision { action, need_score, opportunity_score, p_stuck,
                                  idle_ms, reason, suppressed_by, #[serde(skip)] opportunity_reason }
   ▼ Tauri IPC (500ms poll)
[Frontend] App.tsx:282-300 → Overlay.tsx (Nudge 非ブロック)
   dismiss → invoke("record_intervention_dismiss") → intervention.rs:229
   ▼  ⚠️★ ここから先は 本体未実装（設計のみ）
[表現チャネル] ★契約⑧ { level: stable|friction_rising|stuck, invitation: none|present,
                        seq, emitted_at(秒粒度), epoch }
   PC → スマホ 一方向 / level 変化時のみ / 1Hz を流さない
   iOS=ロック画面ウィジェット(APNs 経由) / Android=ライブ壁紙
   ▼
[Physical Anchor] 完了条件なし・センシングなし。出口として構造的に必須 (ADR-017 D7)
```

### ADR-005 の「イベント封筒」は 2 つの別物がある
| | 実装状況 |
|---|---|
| ① `schema_dto::LogEntryDto`（現行の NDJSON 封筒） | ✅ **実装済み**。`#[serde(tag="type", rename_all="snake_case")]` の tagged union。**27 variant**。`emit_schema` → `schema/current.json` → CI diff |
| ② ADR-005 の `EventEnvelope` / `EventFamily` | ❌ **未実装**（新規追加）。定義案は domain-adapter-boundary.md:116-135。**additive にのみ導入**する決定。着手は Epic 2 |

★ `EventFamily` の設計判断: 「`EventFamily` は**分析上の同一性を保証しない**。あくまでデータ配管と
監査の共通分類である（**Writing の Backspace と動画編集の Undo を同じ重みにしない**）」。

### ADR-006 の配線経路（実測・2 経路のみ）
- **経路 A（G1 / Phase1）**: `record_session_meta` — lib.rs:2362 → :2366 `TaskDomain::from(task_kind)`
  → :2409 `engine.set_domain(domain)`（★ **ログ送信に成功した後**）
- **経路 B（O1）**: `declare_task_kind`（lib.rs:1291）/ 日次ローテート。契約コメント lib.rs:1162-1169
  （「**`engine.reset()` は `set_domain` より前**」「**`set_domain` はログ送信に成功した後**」）
- ★ `record_session_meta` は **O1 では拒否**（lib.rs:2350-2356）
- 実際に走った head は `session_meta.head_id` に残す。⚠️ `FeatSnapshot` には入れない

## ⚠️ 一次資料側の陳腐化・不整合（スライド執筆時に踏まない）

| # | 箇所 | 問題 |
|---|---|---|
| 1 | 現行スライド:161 | ★★★ **「4 値の抽象イベントを PC → スマホへ一方向送信」は陳腐化**。ADR-021 D4 が `level` を 3 値にし `invitation` 二値を新設。**スライドの最重要修正点** |
| 2 | 現行スライド:155-161 | 見出し「**4 層**」に対し本文は **5 項目**。WBS の 4 層とも中身が違う |
| 3 | repository-structure.md:106 / gse-v2-overview.md:255 | 「ADR-001〜018」と書いてあるが実際は **ADR-001〜022** |
| 4 | architecture.md:624 | 「ITfThreadMgr グローバルフック: UIPI によりブロックされる」は 2026-08-22 の訂正に未追随 |
| 5 | `.claude/skills/architecture-rules/SKILL.md:47,96,103` | 依存図に **`wall_server`（削除済み）** が残る。UIPI 説も残る |
| 6 | ADR-004:14 | `InterventionAction{None,Nudge,Wall,Defer}`（Wall は削除済み） |
| 7 | ADR-021:44 (B1) | 根拠の `heads/mod.rs:20` は doc コメント。`WorkStateEstimate` 等はコード 0 ヒット |
| 8 | repository-structure.md ツリー | `src-tauri/src/ndjson_scan.rs` が列挙されていない（実在する） |
| 9 | Cargo.toml:92 | コメント「Wall Server: QR コードによるスマートフォン連携 Wall 解除」が残る |
| 10 | glossary.md:105-108 vs expression-channel.md:256-257 | glossary の**層 0–3 は「音」の定義**。視覚側の層 0 は ADR-021 D10 が別に定義。**同じ「層 0」が 2 つの媒体で別物** |
| 11 | sensors_macos.rs:12, :30 | 存在しない `wall_server.rs` を指す死んだコメント参照 |

## セキュア入力（⚠️ 現行スライドの記述が不正確）

| 事実 | path:line |
|---|---|
| macOS は**計器あり** | observe_macos.rs:56 `SECURE_INPUT_AVAILABLE = true` / :480 `IsSecureEventInputEnabled()` / :411-419 1Hz ポーリングで**変化時のみ送出** |
| Windows は**計器なし** | observe_windows.rs:39 `SECURE_INPUT_AVAILABLE = false` / :445 テスト |
| ★ `GUITHREADINFO` はリポジトリに **0 件** | Windows 側の代替検出は着手すらしていない |
| 記録されるのは区間の on/off フラグのみ | observe.rs:9,44,48 |

→ ★ 安全な書き方:「**検出は macOS のみ実装済み。Windows は計器が無い。抑止の配線はどちらの OS にもない**」
⚠️ 現行スライドの「スキーマ項目はあるが送出元が無い」は **macOS には送出元があるので不正確**。

## Flutter —— 不在の確証
`find . \( -name "pubspec*" -o -name "*.dart" \)` → **0 件**。
ヒット 21 件はすべて Markdown 文書内のコード例。
