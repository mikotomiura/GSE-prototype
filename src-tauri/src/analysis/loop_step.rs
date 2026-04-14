//! 分析ループの純粋関数化 (P0-1: Phase 0 Replay & Guard)
//!
//! `lib.rs` の分析スレッド本体を `step()` 関数として切り出したもの。
//! プロダクションの分析スレッドと `gse-replay` CLI の両方から呼び出される。
//!
//! # 設計
//!
//! - 本関数は `crate::input` / `tauri` に依存しない（architecture-rules ルール 6）。
//! - 時刻は `u64` ミリ秒で統一（replay が NDJSON の `t` をそのまま渡せるように）。
//!   production 側は `SystemTime::now()` ベース、replay 側は NDJSON の `t` を渡す。
//! - 戻り値は `logger::LogEntry` ではなく中立記録型 (`KeyRecord` / `FeatSnapshot`)。
//!   ログ変換は呼び出し側 (`lib.rs`) で行う。
//! - `ime_open` は引数化。production は `input::hook::IME_OPEN` を、replay は
//!   直前の `ime_state.on` を渡す。
//!
//! # 挙動不変性
//!
//! 旧 `lib.rs` 分析スレッド本体と 1:1 マップされる:
//!
//! - イベント受信 → リピート検出 (Windows のみ) → Key ログ記録 → pause 判定
//! - pause 中: `was_paused=true` にセットして 1Hz ゲートを skip
//! - buffer 追加 → pause→復帰検出 → silence-break protection → register_keystroke
//! - 1Hz ゲート: `now_ms >= next_engine_update_ms` で発火
//! - 沈黙 3 状態機構 (TypingPath / TransitionPath / SilencePath) で分岐
//! - Feat 記録
//!
//! 関連ドキュメント: `docs/architecture.md` §4.7、
//! `.steering/20260414-improvement-roadmap/design.md` §0.1。

use std::collections::HashSet;

use crate::analysis::engine::{CognitiveState, CognitiveStateEngine};
use crate::analysis::features::{FeatureExtractor, InputEvent};

/// 分析ループのローカル状態。
///
/// `step()` をまたいで保持されるミュータブル状態をまとめたもの。
/// production では分析スレッドがこの構造体を 1 個所有し、
/// replay では CLI がセッション開始ごとに新規作成する。
pub struct AnalysisState {
    pub extractor: FeatureExtractor,
    /// 直近のキー入力時刻 (ms)。沈黙秒数の計算基準。
    pub last_event_time_ms: u64,
    /// 次の 1Hz ゲート発火時刻 (ms)。絶対時刻ベース増分で累積ドリフトを防止。
    pub next_engine_update_ms: u64,
    /// Silence-break protection: 10 秒沈黙後の連続打鍵カウント。
    pub presses_since_silence: u32,
    /// IME ポーズ→復帰遷移検出用。
    pub was_paused: bool,
    /// Windows リピートキー検出用 HashSet（判断 14 参照）。
    ///
    /// Windows の `WH_KEYBOARD_LL` にはリピートフラグがないため Press/Release
    /// ペアを追跡して検出する。macOS は CGEventTap の AUTOREPEAT フラグで
    /// フック層が判定するため本フィールドは空のまま使用されない。
    /// フィールド cfg 分岐は cfg 伝播の破綻リスクを避けるため適用しない。
    pub pressed_keys: HashSet<u32>,
}

impl AnalysisState {
    /// セッション開始時刻を基準に新規作成する。
    ///
    /// `now_ms` は `last_event_time_ms` と `next_engine_update_ms` の初期値。
    pub fn new(now_ms: u64, buffer_capacity: usize) -> Self {
        Self {
            extractor: FeatureExtractor::new(buffer_capacity),
            last_event_time_ms: now_ms,
            next_engine_update_ms: now_ms,
            presses_since_silence: 0,
            was_paused: false,
            pressed_keys: HashSet::new(),
        }
    }

    /// `start_session` からのリセット要求を処理する。
    pub fn reset(&mut self, now_ms: u64, buffer_capacity: usize) {
        self.extractor = FeatureExtractor::new(buffer_capacity);
        self.last_event_time_ms = now_ms;
        self.next_engine_update_ms = now_ms;
        self.presses_since_silence = 0;
        self.pressed_keys.clear();
        // was_paused はそのまま保持（セッション境界でも pause 状態は engine 側が管理）
    }
}

/// `step()` への入力イベント。
///
/// production 側の分析スレッドは `Key` のみを生成する。
/// replay 側の CLI は NDJSON の ime_state エントリから `ImeActivate` も生成する。
#[derive(Debug, Clone)]
pub enum LoopInput {
    /// キーストロークイベント。
    Key(InputEvent),
    /// IME 候補ウィンドウの active 状態変化。
    ///
    /// production 側の IME Monitor スレッドが直接 `engine.set_paused()` を呼ぶため、
    /// production の `step()` 呼び出しではこれを使わない。
    /// replay では NDJSON の ime_state エントリから再構成する。
    ImeActivate { active: bool },
}

/// キーストローク 1 件の中立記録型。
///
/// `lib.rs` は `LogEntry::Key` へ変換してロガーに送信、
/// `gse-replay` は NDJSON 再出力に使用する。
#[derive(Debug, Clone)]
pub struct KeyRecord {
    pub vk_code: u32,
    pub timestamp: u64,
    pub is_press: bool,
}

/// 1Hz 推論 1 サイクルの中立記録型。
///
/// ゴールデンスナップショット (P0-10) の byte-equal 比較対象。
#[derive(Debug, Clone, PartialEq)]
pub struct FeatSnapshot {
    pub timestamp: u64,
    pub f1: f64,
    pub f3: f64,
    pub f4: f64,
    pub f5: f64,
    pub f6: f64,
    pub p_flow: f64,
    pub p_inc: f64,
    pub p_stuck: f64,
    pub raw_x: f64,
    pub raw_y: f64,
    pub ewma_x: f64,
    pub ewma_y: f64,
    pub obs: usize,
    pub alpha: f64,
}

/// `step()` の出力。
#[derive(Debug, Default)]
pub struct StepOutput {
    /// イベント処理で生成された Key レコード（最大 1 件）。
    pub key: Option<KeyRecord>,
    /// 1Hz ゲート発火時の Feat レコード（最大 1 件）。
    pub feat: Option<FeatSnapshot>,
}

/// 分析ループ 1 サイクル。
///
/// # 引数
/// - `state`: ループローカル状態（mut 借用）
/// - `engine`: HMM エンジン（内部状態は `Arc<Mutex<_>>` 経由で更新される）
/// - `input`: 今回のティックで受信したイベント（なければ `None`）
/// - `now_ms`: 現在時刻 (ms)。production は `SystemTime::now()` ベース、
///   replay は NDJSON の `t` を渡す。
/// - `ime_open`: IME モード（true: 日本語モード → β_writing、false: 英数 → β_coding）
///
/// # 戻り値
/// - `StepOutput.key`: イベントがあれば Key レコード
/// - `StepOutput.feat`: 1Hz ゲート発火時の Feat レコード
///
/// # 挙動
/// 現行 `lib.rs:510-742` と 1:1。詳細は関数内部のコメントを参照。
pub fn step(
    state: &mut AnalysisState,
    engine: &CognitiveStateEngine,
    input: Option<LoopInput>,
    now_ms: u64,
    ime_open: bool,
) -> StepOutput {
    let mut out = StepOutput::default();

    // ── イベント処理 ───────────────────────────────────────────────
    match input {
        Some(LoopInput::Key(mut event)) => {
            // Windows: 分析スレッド側でリピート検出。
            // フックコールバックは is_repeat=false 固定で送信されるため、
            // HashSet で Press/Release ペアを追跡する。
            // CLAUDE.md 制約 (3) 準拠（フックコールバック内 Mutex 排除）。
            #[cfg(target_os = "windows")]
            {
                if event.is_press {
                    if !state.pressed_keys.insert(event.vk_code) {
                        event.is_repeat = true;
                    }
                } else {
                    state.pressed_keys.remove(&event.vk_code);
                }
            }

            out.key = Some(KeyRecord {
                vk_code: event.vk_code,
                timestamp: event.timestamp,
                is_press: event.is_press,
            });

            // IME ポーズ中はバッファ蓄積を含め全処理をスキップ。
            // unpause 時に extractor.reset() で再開するため蓄積しても無駄。
            if engine.get_paused() {
                state.was_paused = true;
                return out;
            }

            state.extractor.process_event(event);

            // ポーズ→復帰遷移: バッファをクリアして stale なフライトタイムを排除。
            if state.was_paused {
                state.was_paused = false;
                state.extractor.reset();
                state.last_event_time_ms = now_ms;
                state.presses_since_silence = 0;
                tracing::debug!("IME pause ended — buffer cleared for clean restart");
            }

            if event.is_press {
                // Silence-break protection (non-repeat only):
                // 10 秒以上の沈黙後、3 打鍵以上の連続入力で初めて
                // last_event_time をリセットし「タイピング復帰」と判定する。
                if !event.is_repeat {
                    let elapsed_ms = now_ms.saturating_sub(state.last_event_time_ms);
                    if elapsed_ms > 10_000 {
                        state.presses_since_silence += 1;
                        if state.presses_since_silence >= 3 {
                            state.last_event_time_ms = now_ms;
                            state.presses_since_silence = 0;
                        }
                    } else {
                        state.last_event_time_ms = now_ms;
                        state.presses_since_silence = 0;
                    }
                }

                // Backspace ストリークカウント（1Hz gate の外側で全打鍵）
                // リピートイベントも含める: BS 長押しによる一気消しでペナルティを発動させる
                engine.register_keystroke(event.is_backspace);
            }
        }
        Some(LoopInput::ImeActivate { active }) => {
            // replay 用: NDJSON の ime_state から pause 状態を再構成する。
            // production は IME Monitor スレッドが直接 set_paused するため、
            // production の `step()` 呼び出しではこのバリアントを生成しない。
            engine.set_paused(active);
        }
        None => {}
    }

    // ── 独立 1Hz ゲート ──────────────────────────────────────────────
    if now_ms < state.next_engine_update_ms {
        return out;
    }

    // 絶対時刻ベースインクリメント (累積ドリフト防止)。
    // スレッドスタール後のキャッチアップ: 大幅に遅れた場合は現在時刻にリセット。
    state.next_engine_update_ms += 1000;
    if state.next_engine_update_ms < now_ms {
        state.next_engine_update_ms = now_ms + 1000;
    }

    if engine.get_paused() {
        state.was_paused = true;
        return out;
    }

    // 1Hz ゲートでのポーズ→復帰遷移検出（タイムアウトパス）
    if state.was_paused {
        state.was_paused = false;
        state.extractor.reset();
        state.last_event_time_ms = now_ms;
        state.presses_since_silence = 0;
        tracing::debug!("IME pause ended (1Hz gate) — buffer cleared for clean restart");
    }

    let silence_secs = (now_ms.saturating_sub(state.last_event_time_ms)) as f64 / 1000.0;
    let mut features = state.extractor.calculate_features();

    // ── 沈黙 3 状態機構 ──────────────────────────────────────────────
    // 詳細は docs/architecture.md §4.7。
    let (log_features, diag_opt) = if features.f1_flight_time_median > 0.0 && silence_secs < 2.0 {
        // === TypingPath: バッファ実データあり + 直近タイピング中 ===
        let d = engine.update(&features, ime_open);
        (features, d)
    } else if features.f1_flight_time_median > 0.0 {
        // === TransitionPath: バッファ実データあり + 2 秒以上沈黙中 ===
        // α=0.3 で古いウィンドウデータを連続入力すると Incubation にロックインするため、
        // α=0.15 の update_silence を使用する。
        if silence_secs >= 2.0 {
            features.f5_pause_count += silence_secs / 2.0;
        }
        // TUNE: TransitionPath 用摩擦フロア
        //   F6: onset 8s / ramp 30s / floor 0.15 (≥ 10s)
        //   F3: onset 10s / ramp 40s / floor 0.20 (≥ 10s)
        if silence_secs >= 8.0 {
            let mut f6_floor = ((silence_secs - 8.0) / 30.0).clamp(0.0, 1.0);
            let mut f3_floor = ((silence_secs - 10.0) / 40.0).clamp(0.0, 1.0);
            if silence_secs >= 10.0 {
                f6_floor = f6_floor.max(0.15);
                f3_floor = f3_floor.max(0.20);
            }
            features.f6_pause_after_del_rate = features.f6_pause_after_del_rate.max(f6_floor);
            features.f3_correction_rate = features.f3_correction_rate.max(f3_floor);
        }
        let d = engine.update_silence(&features, ime_open, silence_secs);
        (features, d)
    } else if let Some(sf) = state.extractor.make_silence_observation(silence_secs) {
        // === SilencePath: バッファ空 → 合成特徴量で update_silence ===
        let d = engine.update_silence(&sf, ime_open, silence_secs);
        (sf, d)
    } else {
        // silence < 2s かつ f1=0 (データ不足) → スキップ
        return out;
    };

    // ── Feat 記録 ────────────────────────────────────────────────────
    let state_probs = engine.get_current_state();
    let p_flow = state_probs
        .get(&CognitiveState::Flow)
        .copied()
        .unwrap_or(0.0);
    let p_inc = state_probs
        .get(&CognitiveState::Incubation)
        .copied()
        .unwrap_or(0.0);
    let p_stuck = state_probs
        .get(&CognitiveState::Stuck)
        .copied()
        .unwrap_or(0.0);

    let (raw_x, raw_y, ewma_x, ewma_y, obs, alpha) = match &diag_opt {
        Some(d) => (d.raw_x, d.raw_y, d.ewma_x, d.ewma_y, d.obs, d.alpha),
        None => (0.0, 0.0, 0.0, 0.0, 0, 0.0),
    };

    out.feat = Some(FeatSnapshot {
        timestamp: now_ms,
        f1: log_features.f1_flight_time_median,
        f3: log_features.f3_correction_rate,
        f4: log_features.f4_burst_length,
        f5: log_features.f5_pause_count,
        f6: log_features.f6_pause_after_del_rate,
        p_flow,
        p_inc,
        p_stuck,
        raw_x,
        raw_y,
        ewma_x,
        ewma_y,
        obs,
        alpha,
    });

    out
}
