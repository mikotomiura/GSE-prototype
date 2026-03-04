use std::collections::HashMap;
use std::sync::atomic::{AtomicU32, Ordering};
use std::sync::{Arc, Mutex};

use crate::analysis::features::{phi, Features};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum CognitiveState {
    Flow,
    Incubation,
    Stuck,
}

#[derive(Clone)]
pub struct CognitiveStateEngine {
    // Manual HMM parameters
    transitions: Arc<[f64; 9]>,

    // 3 states × 26 observation bins
    //   obs = x_bin * 5 + y_bin  (0..24 natural bins)
    //   obs = 25                  (backspace streak penalty bin)
    //
    // X-axis (Friction):   0 = low friction  … 4 = high friction
    // Y-axis (Engagement): 0 = low engagement … 4 = high engagement
    emissions: Arc<[f64; 78]>,

    current_state_probs: Arc<Mutex<[f64; 3]>>,
    pub is_paused: Arc<Mutex<bool>>,
    pub backspace_streak: Arc<AtomicU32>,

    // 2-axis EWMA: (X = Friction, Y = Engagement)
    // α = 0.3: 新値30%、前値70%のブレンド
    axes_ewma: Arc<Mutex<(f64, f64)>>,

    // Hysteresis layer: slow EMA of reported probabilities.
    // Prevents instant state flips (e.g. Cold-Start after window reset).
    // α = 0.25 for normal updates (~4s time-constant).
    // α = 0.50 for backspace-penalty bin (faster Stuck response).
    display_probs: Arc<Mutex<[f64; 3]>>,
}

impl CognitiveStateEngine {
    pub fn new() -> Self {
        // Transition probabilities
        // FLOW -> FLOW: 0.75  (escape time 1/(1-0.75)=4s; reduced from 0.80 to mitigate Flow Gravity)
        // FLOW -> INCUBATION: 0.17
        // FLOW -> STUCK: 0.08
        // INCUBATION -> FLOW: 0.12
        // INCUBATION -> INCUBATION: 0.80  (Sio & Ormerod 2009)
        // INCUBATION -> STUCK: 0.08
        // STUCK -> FLOW: 0.06
        // STUCK -> INCUBATION: 0.18
        // STUCK -> STUCK: 0.76  (Hall et al. 2024)
        let transitions = [0.75, 0.17, 0.08, 0.12, 0.80, 0.08, 0.06, 0.18, 0.76];

        // Emissions B: 3 states × 26 bins
        //
        // Grid layout: obs = x_bin * 5 + y_bin
        //
        //        x→  0(lo F)  1      2      3      4(hi F)
        //  y↓
        //  0(lo E)   [0]     [5]   [10]   [15]   [20]
        //  1         [1]     [6]   [11]   [16]   [21]
        //  2         [2]     [7]   [12]   [17]   [22]
        //  3         [3]     [8]   [13]   [18]   [23]
        //  4(hi E)   [4]     [9]   [14]   [19]   [24]
        //  penalty   [25]
        //
        // Flow:       peaks at low Friction (x=0,1) × high Engagement (y=3,4)
        // Incubation: peaks at low-mid Friction (x=0,1,2) × low Engagement (y=0,1)
        // Stuck:      peaks at high Friction (x=3,4) × low Engagement (y=0,1)
        //
        // Penalty bin (obs=25): backspace_streak ≥ 5 → near-certain Stuck.
        // Each state's non-penalty bins sum to ≈1.0; HMM normalizes anyway.
        // Emission Floor ポリシー変更 (advice.md §E):
        // 旧実装では全ビンに動的に EMISSION_FLOOR=0.05 を加算していたため、
        // ペナルティビン (Stuck=0.99) のシャープさが 0.99/0.05≈20x に薄まっていた。
        // 新実装では 0.00 を一律 0.001 に置き換えて静的テーブルに焼き込み、
        // 動的加算を廃止する。これにより ペナルティ比が 0.99/0.001≈990x に強化される。
        // HMM 正規化が行われるため合計値の厳密な 1.0 は不要。
        #[rustfmt::skip]
        let emissions: [f64; 78] = [
            // ── Flow (State 0) ─────────────────────────── non-penalty sum ≈ 0.86
            //  x=0 (low F)    y: 0      1      2      3      4
                               0.010, 0.020, 0.050, 0.120, 0.140,
            //  x=1            y: 0      1      2      3      4
                               0.010, 0.020, 0.050, 0.120, 0.130,
            //  x=2            y: 0      1      2      3      4
                               0.001, 0.010, 0.030, 0.060, 0.080,
            //  x=3            y: 0      1      2      3      4
                               0.001, 0.001, 0.001, 0.001, 0.001,
            //  x=4 (high F)   y: 0      1      2      3      4
                               0.001, 0.001, 0.001, 0.001, 0.001,
            //  penalty bin (BS streak ≥5 → near-zero Flow)
                               0.001,

            // ── Incubation (State 1) ──────────────────── non-penalty sum ≈ 1.07
            //  x=0 (low F)    y: 0      1      2      3      4
                               0.150, 0.100, 0.040, 0.030, 0.020,
            //  x=1            y: 0      1      2      3      4
                               0.140, 0.100, 0.040, 0.030, 0.020,
            //  x=2            y: 0      1      2      3      4
                               0.100, 0.080, 0.030, 0.010, 0.001,
            //  x=3            y: 0      1      2      3      4
                               0.050, 0.040, 0.010, 0.001, 0.001,
            //  x=4 (high F)   y: 0      1      2      3      4
                               0.040, 0.030, 0.010, 0.001, 0.001,
            //  penalty bin
                               0.010,

            // ── Stuck (State 2) ───────────────────────── non-penalty sum ≈ 1.01
            //  x=0 (low F)    y: 0      1      2      3      4
                               0.001, 0.001, 0.001, 0.001, 0.001,
            //  x=1            y: 0      1      2      3      4
                               0.001, 0.001, 0.001, 0.001, 0.001,
            //  x=2            y: 0      1      2      3      4
                               0.020, 0.040, 0.020, 0.001, 0.001,
            //  x=3            y: 0      1      2      3      4
                               0.100, 0.160, 0.070, 0.020, 0.001,
            //  x=4 (high F)   y: 0      1      2      3      4
                               0.160, 0.220, 0.120, 0.050, 0.020,
            //  penalty bin  (backspace streak ≥5 → near-certain Stuck)
                               0.990,
        ];

        // 初期事前確率: Flow 優先で開始。
        // セッション開始直後はほぼ全員 Flow 状態でタイピングを始めるため、
        // バランス型 [0.5, 0.3, 0.2] では Inc=30% が最初から表示され
        // コールドスタート時に誤ってIncubation状態が見えてしまう。
        // [0.80, 0.15, 0.05] にすることで初期 Inc=15% に抑え、
        // さらに display_probs α=0.40 の高速収束と組み合わせてノイズを低減する。
        let initial_probs = [0.80, 0.15, 0.05];

        Self {
            transitions: Arc::new(transitions),
            emissions: Arc::new(emissions),
            current_state_probs: Arc::new(Mutex::new(initial_probs)),
            is_paused: Arc::new(Mutex::new(false)),
            backspace_streak: Arc::new(AtomicU32::new(0)),
            // (0.1, 0.8) = Flow 方向で初期化 (obs=4; low Friction × high Engagement)
            // 旧 (0.3, 0.5) では obs=7 (中立) から始まり初回観測がやや Inc 寄りだった。
            // (0.0, 1.0) は最初の更新で p_flow=1.0 に固定されるため避ける。
            axes_ewma: Arc::new(Mutex::new((0.1, 0.8))),
            // display_probs は initial_probs と同値で初期化
            display_probs: Arc::new(Mutex::new(initial_probs)),
        }
    }

    /// セッション開始時に全内部状態を初期値にリセットする。
    /// start_session Tauri コマンドから呼ばれる。
    pub fn reset(&self) {
        let initial_probs = [0.80, 0.15, 0.05];
        match self.current_state_probs.lock() {
            Ok(mut p) => *p = initial_probs,
            Err(poisoned) => *poisoned.into_inner() = initial_probs,
        }
        match self.display_probs.lock() {
            Ok(mut p) => *p = initial_probs,
            Err(poisoned) => *poisoned.into_inner() = initial_probs,
        }
        match self.axes_ewma.lock() {
            Ok(mut e) => *e = (0.1, 0.8),
            Err(poisoned) => *poisoned.into_inner() = (0.1, 0.8),
        }
        self.backspace_streak.store(0, Ordering::Release);
        // is_paused もリセット: IME変換中に「開始する」が押された場合に
        // 停止状態が残留してキーストロークが全破棄されるのを防ぐ。
        // IMEモニタースレッドが100ms以内に正しい状態に戻すが、
        // その間のキーストロークが失われないよう先にリセットする。
        match self.is_paused.lock() {
            Ok(mut p) => *p = false,
            Err(poisoned) => *poisoned.into_inner() = false,
        }
    }

    pub fn set_paused(&self, paused: bool) {
        match self.is_paused.lock() {
            Ok(mut p) => *p = paused,
            Err(poisoned) => *poisoned.into_inner() = paused,
        }
    }

    /// IME active時に強制的にFlow状態にする (Stuck表示を消す)
    /// EWMA もリセットして誤った蓄積値が残らないようにする
    pub fn force_flow_state(&self) {
        let flow_probs = [0.98, 0.01, 0.01];
        match self.current_state_probs.lock() {
            Ok(mut p) => *p = flow_probs,
            Err(poisoned) => *poisoned.into_inner() = flow_probs,
        }
        // display_probs も即座にリセット (ヒステリシス層もクリア)
        match self.display_probs.lock() {
            Ok(mut p) => *p = flow_probs,
            Err(poisoned) => *poisoned.into_inner() = flow_probs,
        }
        // IME切り替え時にEWMAをリセット: (低Friction, 高Engagement) = Flow領域
        match self.axes_ewma.lock() {
            Ok(mut e) => *e = (0.0, 1.0),
            Err(poisoned) => *poisoned.into_inner() = (0.0, 1.0),
        }
    }

    /// 全キー押下時に呼び出し、Backspaceストリークをリアルタイムでカウントする。
    /// 1Hz gate の外側（全打鍵）で呼ぶことで、高速Backspace連打を正確に検知する。
    /// AtomicU32 を使用してロックなしに安全に更新する。
    pub fn register_keystroke(&self, vk_code: u32) {
        if vk_code == 0x08 {
            self.backspace_streak.fetch_add(1, Ordering::Relaxed);
        } else {
            self.backspace_streak.store(0, Ordering::Relaxed);
        }
    }

    /// IMEポーズ中かどうかを安全に取得する
    pub fn get_paused(&self) -> bool {
        match self.is_paused.lock() {
            Ok(g) => *g,
            Err(poisoned) => *poisoned.into_inner(),
        }
    }

    pub fn discretize_flight_time(&self, ft: f64) -> usize {
        match ft {
            t if t < 80.0 => 0,
            t if t < 120.0 => 1,
            t if t < 160.0 => 2,
            t if t < 200.0 => 3,
            t if t < 300.0 => 4,
            t if t < 400.0 => 5,
            t if t < 500.0 => 6,
            t if t < 700.0 => 7,
            t if t < 1000.0 => 8,
            t if t < 1500.0 => 9,
            _ => 10,
        }
    }

    /// X軸 (Friction / 摩擦) と Y軸 (Engagement / 没入度) を算出する。
    /// 返値はそれぞれ [0.0, 1.0] にクランプ済み。
    ///
    /// X (Friction) — 高いほど「つまずき」を表す。重み合計 = 1.0
    ///   0.30 × φ(F3: 修正率)
    ///   0.25 × φ(F6: 削除後停止率)
    ///   0.25 × φ(F1: Flight Time)
    ///   0.20 × φ(F5: ポーズ回数)
    ///
    /// Y (Engagement) — 高いほど「滑らかな出力」を表す。重み合計 = 1.0
    ///   0.40 × φ(F4: バースト長)
    ///   0.35 × (1 − φ(F1))   … 短いFT = 高エンゲージ
    ///   0.25 × (1 − φ(F5))   … 少ないポーズ = 高エンゲージ
    ///
    /// # Context-specific β (dual baseline)
    ///
    /// `ime_open = true`  → β_writing: Japanese typing baseline.
    ///   Slower flight times and shorter bursts are normal during Japanese composition.
    ///   Normalizing against a tighter baseline prevents systematic Flow over-detection
    ///   when the user is simply typing romaji at their natural Japanese pace.
    ///
    /// `ime_open = false` → β_coding: Alphanumeric/coding baseline.
    ///   Faster flight times and longer bursts are the reference for fluent coding.
    ///   A coder who is "slow" relative to their coding norm signals friction correctly.
    ///
    /// Both sets are population-level estimates; future work can adapt them per-session
    /// using EWMA updates (update only the matching β when IME state is known).
    fn calculate_latent_axes(&self, features: &Features, ime_open: bool) -> (f64, f64) {
        // β_coding: reference values for alphanumeric / coding input
        // Source: Dhakal et al. (2018) general population medians, coding-adjusted.
        const BETA_CODING_F1: f64 = 150.0; // Flight Time median (ms)
        const BETA_CODING_F3: f64 = 0.06;  // Correction rate (6%)
        const BETA_CODING_F4: f64 = 5.0;   // Burst length (chars)
        const BETA_CODING_F5: f64 = 2.0;   // Pause count (per 30 s)
        const BETA_CODING_F6: f64 = 0.08;  // Pause-after-delete rate

        // β_writing: reference values for Japanese IME writing input
        // Japanese romaji→kana composition is slower than direct ASCII entry.
        // Correction pattern differs: kanji selection uses arrow keys, not Backspace.
        const BETA_WRITING_F1: f64 = 220.0; // Flight Time median (ms) — slower
        const BETA_WRITING_F3: f64 = 0.08;  // Correction rate — slightly lower (IME handles errors)
        const BETA_WRITING_F4: f64 = 2.0;   // Burst length — shorter (composition in segments)
        const BETA_WRITING_F5: f64 = 4.0;   // Pause count — more pauses for thinking/selection
        const BETA_WRITING_F6: f64 = 0.12;  // Pause-after-delete rate

        let (beta_f1, beta_f3, beta_f4, beta_f5, beta_f6) = if ime_open {
            (BETA_WRITING_F1, BETA_WRITING_F3, BETA_WRITING_F4, BETA_WRITING_F5, BETA_WRITING_F6)
        } else {
            (BETA_CODING_F1, BETA_CODING_F3, BETA_CODING_F4, BETA_CODING_F5, BETA_CODING_F6)
        };

        let phi1 = phi(features.f1_flight_time_median, beta_f1);
        let phi3 = phi(features.f3_correction_rate, beta_f3);
        let phi4 = phi(features.f4_burst_length, beta_f4);
        let phi5 = phi(features.f5_pause_count, beta_f5);
        let phi6 = phi(features.f6_pause_after_del_rate, beta_f6);

        // X: Friction (高いほど「つまずき」)  重み合計 = 1.0
        let x = (0.30 * phi3 + 0.25 * phi6 + 0.25 * phi1 + 0.20 * phi5).clamp(0.0, 1.0);

        // Y: Engagement (高いほど「滑らかな出力」)  重み合計 = 1.0
        let y = (0.40 * phi4 + 0.35 * (1.0 - phi1) + 0.25 * (1.0 - phi5)).clamp(0.0, 1.0);

        (x, y)
    }

    /// B-5: HMM Update (2軸 Friction × Engagement、25+1ビン モデル)
    ///
    /// `ime_open`: true = Japanese IME is in Japanese-input mode (あ/カ).
    /// Used to select context-appropriate β values in `calculate_latent_axes`.
    pub fn update(&self, features: &Features, ime_open: bool) {
        if self.get_paused() {
            return;
        }

        // F1がゼロの場合はデータ不足のためスキップ
        if features.f1_flight_time_median <= 0.0 {
            return;
        }

        // --- Backspace Streak Logic ---
        // register_keystroke() が全打鍵でカウントを更新済み。
        // ストリークはここでリセットしない。リセットは register_keystroke() で
        // 非BSキーが押されたときのみ行う。こうすることで、5回以上のBackspace連打後
        // に停止した場合でも次の silence observation で再びペナルティビンが適用され、
        // p_stuck が 0.52 → 0.68 → 0.76 と段階的に上昇して閾値(0.6)を超えられる。
        // 閾値 8: 通常編集の BS 5回程度では誤発動しないよう引き上げ
        let streak = self.backspace_streak.load(Ordering::Relaxed);
        let apply_backspace_penalty = streak >= 8;

        let (raw_x, raw_y) = self.calculate_latent_axes(features, ime_open);

        // EWMA平滑化 (α = 0.3): 各軸を独立に平滑化
        // s_t = 0.3 * raw_t + 0.7 * s_{t-1}
        let (x, y) = match self.axes_ewma.lock() {
            Ok(mut ewma) => {
                ewma.0 = 0.3 * raw_x + 0.7 * ewma.0;
                ewma.1 = 0.3 * raw_y + 0.7 * ewma.1;
                (ewma.0, ewma.1)
            }
            Err(poisoned) => {
                let mut ewma = poisoned.into_inner();
                ewma.0 = 0.3 * raw_x + 0.7 * ewma.0;
                ewma.1 = 0.3 * raw_y + 0.7 * ewma.1;
                (ewma.0, ewma.1)
            }
        };

        // (X, Y) → 5×5 グリッド → 観測インデックス [0..24]
        let x_bin = (x * 5.0).floor().min(4.0) as usize;
        let y_bin = (y * 5.0).floor().min(4.0) as usize;
        let mut obs = x_bin * 5 + y_bin;

        // Backspace Streak Override → ペナルティビン (obs=25)
        // 高Friction・低Engagementの極端ケースとして強制マップ
        if apply_backspace_penalty {
            obs = 25;
        }

        // A-3: Mutex ポイズニング対策
        let mut current = match self.current_state_probs.lock() {
            Ok(g) => g,
            Err(poisoned) => poisoned.into_inner(),
        };

        let old_probs = *current;
        let mut new_probs = [0.0; 3];
        let n_states = 3;

        // Forward Algorithm Step
        // ε-floor は静的テーブルに焼き込み済み (全ビン最小値 = 0.001)。
        // 動的加算は廃止: ペナルティビンの比率が 20x → 990x に向上。
        let mut sum_prob = 0.0;

        for j in 0..n_states {
            let mut trans_sum = 0.0;
            for i in 0..n_states {
                let t_prob = self.transitions[i * n_states + j];
                trans_sum += old_probs[i] * t_prob;
            }

            // 3 states × 26 bins: index = j * 26 + obs
            let e_prob = self.emissions[j * 26 + obs];
            new_probs[j] = trans_sum * e_prob;
            sum_prob += new_probs[j];
        }

        // Normalize
        if sum_prob > 0.0 {
            for j in 0..n_states {
                new_probs[j] /= sum_prob;
            }
        }
        // 合計が0になった場合は以前の確率を維持する (フォールバック)

        *current = new_probs;

        // ── Hysteresis Layer ──────────────────────────────────────────────
        // display_probs に EMA を適用し、ウィンドウリセット時の
        // Cold-Start 瞬間遷移 (Stuck→Flow in 1ms) を防ぐ。
        //
        // α=0.40 (通常): 時定数 ≈ 2.5 更新 ≈ 2.5 秒 (旧 α=0.25 → 4秒 より高速)
        // α=0.60 (ペナルティ): Backspace 連続時は素早く Stuck に収束 (旧 0.50)
        let display_alpha = if apply_backspace_penalty { 0.60 } else { 0.40 };

        let mut display = match self.display_probs.lock() {
            Ok(g) => g,
            Err(poisoned) => poisoned.into_inner(),
        };
        let mut disp_sum = 0.0;
        for i in 0..n_states {
            display[i] = display_alpha * new_probs[i] + (1.0 - display_alpha) * display[i];
            disp_sum += display[i];
        }
        if disp_sum > 0.0 {
            for v in display.iter_mut() {
                *v /= disp_sum;
            }
        }
    }

    /// サイレンス（完全無入力）時の HMM 更新 (advice.md §F)。
    ///
    /// 通常の update() と異なり、axes_ewma を更新しない。
    /// サイレンス特徴量 (f1=2000ms 等の合成値) で EWMA を更新すると、
    /// ユーザーが次にタイピング再開したときに EWMA が高Friction側に偏ったまま
    /// となり、最初の数回の更新が不正確になる（EWMA汚染）。
    ///
    /// HMM は silence 特徴量 (raw X/Y) で正常に更新する。
    /// これにより Incubation = 「手を止めて考えている状態」が正しく上昇する。
    /// Backspace ペナルティ (streak ≥ 8) は obs=25 に上書きする。
    pub fn update_silence(&self, features: &Features, ime_open: bool) {
        if self.get_paused() {
            return;
        }

        if features.f1_flight_time_median <= 0.0 {
            return;
        }

        // Backspace ペナルティ判定 (閾値 8: 通常編集の5回BS誤検知を防ぐ)
        let apply_backspace_penalty = self.backspace_streak.load(Ordering::Relaxed) >= 8;

        // サイレンス特徴量から観測ビンを計算 (EWMA は更新しない)
        // axes_ewma を読まず raw_x/raw_y をそのままビン変換する。
        // Incubation 上昇 (pause中の自然な状態遷移) は維持しつつ EWMA 汚染を防ぐ。
        let obs = if apply_backspace_penalty {
            25
        } else {
            let (raw_x, raw_y) = self.calculate_latent_axes(features, ime_open);
            let x_bin = (raw_x * 5.0).floor().min(4.0) as usize;
            let y_bin = (raw_y * 5.0).floor().min(4.0) as usize;
            x_bin * 5 + y_bin
        };

        let mut current = match self.current_state_probs.lock() {
            Ok(g) => g,
            Err(poisoned) => poisoned.into_inner(),
        };

        let old_probs = *current;
        let mut new_probs = [0.0; 3];
        let n_states = 3;
        let mut sum_prob = 0.0;

        for j in 0..n_states {
            let mut trans_sum = 0.0;
            for i in 0..n_states {
                trans_sum += old_probs[i] * self.transitions[i * n_states + j];
            }
            new_probs[j] = trans_sum * self.emissions[j * 26 + obs];
            sum_prob += new_probs[j];
        }

        if sum_prob > 0.0 {
            for j in 0..n_states {
                new_probs[j] /= sum_prob;
            }
        }

        *current = new_probs;

        // display_probs EMA
        // ペナルティ α=0.50: nudge 閾値到達に 2 更新 (2s) 必要 (α=0.60 の即発動を緩和)
        // 通常 α=0.40: silence での Incubation 上昇を自然なペースで反映
        let display_alpha = if apply_backspace_penalty { 0.50 } else { 0.40 };
        let mut display = match self.display_probs.lock() {
            Ok(g) => g,
            Err(poisoned) => poisoned.into_inner(),
        };
        let mut disp_sum = 0.0;
        for i in 0..n_states {
            display[i] = display_alpha * new_probs[i] + (1.0 - display_alpha) * display[i];
            disp_sum += display[i];
        }
        if disp_sum > 0.0 {
            for v in display.iter_mut() {
                *v /= disp_sum;
            }
        }
    }

    pub fn get_current_state(&self) -> HashMap<CognitiveState, f64> {
        // display_probs (ヒステリシス層) を返す。
        // 生の current_state_probs は瞬間値; display_probs は遅い EMA により
        // 短期スパイクを平滑化した値。UI・ログはこちらを使用する。
        let probs = match self.display_probs.lock() {
            Ok(g) => g,
            Err(poisoned) => poisoned.into_inner(),
        };
        let mut map = HashMap::new();
        map.insert(CognitiveState::Flow, probs[0]);
        map.insert(CognitiveState::Incubation, probs[1]);
        map.insert(CognitiveState::Stuck, probs[2]);
        map
    }
}
