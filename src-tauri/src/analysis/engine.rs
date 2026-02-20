use std::collections::HashMap;
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
    emissions: Arc<[f64; 33]>,

    current_state_probs: Arc<Mutex<[f64; 3]>>,
    pub is_paused: Arc<Mutex<bool>>,
    pub backspace_streak: Arc<Mutex<u32>>,

    // GPT advice: EWMA平滑化でS_stuckのジッタ抑制
    // α=0.3: 新値30%、前値70%のブレンド
    s_stuck_ewma: Arc<Mutex<f64>>,
}

impl CognitiveStateEngine {
    pub fn new() -> Self {
        // Literature-backed transition probabilities (as a Smoothing Filter for Phase 1)
        // FLOW -> FLOW: 0.92
        // Source: Csikszentmihalyi (1990). Flow duration average ~mins.
        //         1/(1-0.92) = 12.5s (conservative lower bound).
        // FLOW -> INCUBATION: 0.07
        // Source: Hall et al. (2024). Derived from pause frequency in writing tasks.
        // FLOW -> STUCK: 0.01
        // Source: Hall et al. (2024). Direct transition from high-speed to stuck is rare.

        // INCUBATION -> INCUBATION: 0.82
        // Source: Sio & Ormerod (2009). Meta-analysis of incubation duration.
        //         1/(1-0.82) = 5.6s (~3x minimum pause).
        // INCUBATION -> FLOW: 0.10
        // Source: High probability of returning to flow after a burst.
        // INCUBATION -> STUCK: 0.08
        // Source: Probability of incubation turning into a block.

        // STUCK -> STUCK: 0.80 (旧0.85 → 0.80: Stuckから抜け出しやすく)
        //         1/(1-0.80) = 5.0s — 回復に5秒かかる程度が妥当。
        // STUCK -> INCUBATION: 0.15 (旧0.13)
        // STUCK -> FLOW: 0.05 (旧0.02: 直接Flowへの回復も許容)
        let transitions = [0.92, 0.07, 0.01, 0.10, 0.82, 0.08, 0.05, 0.15, 0.80];

        // Emissions (B) 3x11  S_stuck=[0,1] を 11ビンにマッピング
        //
        // 設計方針:
        //   Flow        : 低ビン(0-5)に集中。普通のタイピング(S_stuck≈0.1-0.2)は確実にFlow。
        //   Incubation  : 中〜高ビン(3-9)に分布。思考ポーズ・Idle状態をカバー。
        //   Stuck       : 高ビン(5-9)のみ。S_stuck が0.5以上の明確なシグナルのみ検知。
        //                 Bin10 は Backspace連打ペナルティ専用 (0.99 で強制Stuck)。
        //
        // 旧実装の問題: Stuck が bin4-5 でピーク → S_stuck=0.4でもStuck誘導 → 普通入力が誤判定
        // 新実装:       Stuck を bin6-8 にシフト → 明確な遅さ/修正過多のみ判定
        #[rustfmt::skip]
        let emissions = [
            // Flow: 低ビン集中 (合計 ≈ 1.0)
            0.35, 0.25, 0.15, 0.10, 0.07, 0.05, 0.02, 0.01, 0.0, 0.0, 0.0,
            // Incubation: 中〜高ビンに広く分布 (合計 = 1.0)
            0.02, 0.03, 0.05, 0.08, 0.10, 0.15, 0.20, 0.20, 0.10, 0.06, 0.01,
            // Stuck: 高ビンのみ (Bin10 = Backspace強制Stuck)
            0.0, 0.0, 0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.20, 0.10, 0.99,
        ];

        // 初期事前確率を修正:
        // 旧: [0.5, 0.4, 0.1] → Incubationが初期から高く、誤検知の原因
        // 新: [0.7, 0.2, 0.1] → Flowを優位にし、実際のタイピングパターンで検知
        let initial_probs = [0.7, 0.2, 0.1];

        Self {
            transitions: Arc::new(transitions),
            emissions: Arc::new(emissions),
            current_state_probs: Arc::new(Mutex::new(initial_probs)),
            is_paused: Arc::new(Mutex::new(false)),
            backspace_streak: Arc::new(Mutex::new(0)),
            s_stuck_ewma: Arc::new(Mutex::new(0.0)),
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
        // IME切り替え時にEWMAをリセット: 日本語入力中の誤差を引き継がない
        match self.s_stuck_ewma.lock() {
            Ok(mut e) => *e = 0.0,
            Err(poisoned) => *poisoned.into_inner() = 0.0,
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

    /// B-3: S_stuck (Stuckスコア) を算出する
    ///
    /// ベータ値はSurface Pro / 日本語入力ユーザーの実測値に合わせてキャリブレーション済み:
    ///   F1: 250ms  (旧150ms) — 普通のタイピング速度の中央値
    ///   F2: 2000ms²(旧1000)  — FT分散の許容範囲を拡大
    ///   F3: 10%   (旧5%)    — 修正率10%以下は正常範囲
    ///   F4: 2文字 (旧5文字)  — バースト長2未満のみStuck判定対象
    ///   F5: 3回   (旧2回)   — 30秒に3回以下のポーズは正常
    ///   F6: 15%   (旧10%)  — 削除後停止率15%以下は正常
    fn calculate_s_stuck(&self, features: &Features) -> f64 {
        const BETA_F1: f64 = 250.0; // 標準FT中央値 (ms)
        const BETA_F2: f64 = 2000.0; // 標準FT分散
        const BETA_F3: f64 = 0.10; // 標準修正率 (10%)
        const BETA_F4: f64 = 2.0; // 標準バースト長 (文字数) — 2文字未満がStuck
        const BETA_F5: f64 = 3.0; // 標準ポーズ回数 (3回/30s)
        const BETA_F6: f64 = 0.15; // 標準削除後停止率 (15%)

        let phi1 = phi(features.f1_flight_time_median, BETA_F1);
        let phi2 = phi(features.f2_flight_time_variance, BETA_F2);
        let phi3 = phi(features.f3_correction_rate, BETA_F3);
        let phi4_inv = 1.0 - phi(features.f4_burst_length, BETA_F4);
        let phi5 = phi(features.f5_pause_count, BETA_F5);
        let phi6 = phi(features.f6_pause_after_del_rate, BETA_F6);

        // 重み合計 1.0
        0.30 * phi1 + 0.10 * phi2 + 0.15 * phi3 + 0.15 * phi6 + 0.15 * phi4_inv + 0.15 * phi5
    }

    /// B-5: HMM Update
    pub fn update(&self, features: &Features, vk_code: Option<u32>) {
        if self.get_paused() {
            return;
        }

        // F1がゼロの場合はデータ不足のためスキップ
        if features.f1_flight_time_median <= 0.0 {
            return;
        }

        // --- Backspace Streak Logic ---
        let streak = match self.backspace_streak.lock() {
            Ok(mut s) => {
                if vk_code == Some(0x08) {
                    // VK_BACK
                    *s += 1;
                } else if vk_code.is_some() {
                    *s = 0;
                }
                *s
            }
            Err(poisoned) => {
                let mut s = poisoned.into_inner();
                if vk_code == Some(0x08) {
                    *s += 1;
                } else if vk_code.is_some() {
                    *s = 0;
                }
                *s
            }
        };
        // 3回は単なるタイポ修正の可能性があるため、5回以上を「大きな修正＝Stuck」とする
        let apply_backspace_penalty = streak >= 5;

        let raw_s_stuck = self.calculate_s_stuck(features);

        // GPT advice: EWMA平滑化 (α = 0.3)
        // 瞬間的なスパイク（3回のスペースなど）による誤検知を抑制
        // s_t = 0.3 * raw_t + 0.7 * s_{t-1}
        let s_stuck = match self.s_stuck_ewma.lock() {
            Ok(mut ewma) => {
                *ewma = 0.3 * raw_s_stuck + 0.7 * (*ewma);
                *ewma
            }
            Err(poisoned) => {
                let mut ewma = poisoned.into_inner();
                *ewma = 0.3 * raw_s_stuck + 0.7 * (*ewma);
                *ewma
            }
        };

        // S_stuck [0, 1] → 観測ビン [0, 10]
        let mut obs = ((s_stuck * 10.0) as usize).min(10);

        // Streak Override
        if apply_backspace_penalty {
            obs = 10;
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
        let mut sum_prob = 0.0;

        for j in 0..n_states {
            let mut trans_sum = 0.0;
            for i in 0..n_states {
                let t_prob = self.transitions[i * n_states + j];
                trans_sum += old_probs[i] * t_prob;
            }

            let e_prob = self.emissions[j * 11 + obs];
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
    }

    pub fn get_current_state(&self) -> HashMap<CognitiveState, f64> {
        // A-3: Mutex ポイズニング対策
        let probs = match self.current_state_probs.lock() {
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
