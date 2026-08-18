use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, AtomicU32, Ordering};
use std::sync::{Arc, Mutex};

use crate::analysis::features::Features;
use crate::analysis::heads::{DomainInferenceHead, WritingHead};

// ============================================================================
// TUNE: HMM チューニング定数
// ============================================================================
//
// 意図的な HMM チューニングでこれらを変更する際は、
//   1. `#[cfg(test)] mod tests` のスナップショットテストも更新する
//   2. 変更根拠を `.steering/` に記録する
// これら以外の α 値・閾値もソース内に散在する。
// 全チューニングポイントの列挙は `grep -rn "TUNE:" src-tauri/src/` で確認可能
// （`analysis/` 以外に `lib.rs` の TransitionPath 摩擦フロアも含む）。
//
// **EWMA α 系の定数化ポリシー**:
//   通常 update() の α=0.3、update_silence() の 0.15/0.18/0.25、
//   ヒステリシス層の 0.40/0.60 はモジュール定数として抽出しない。
//   理由: IEEE 754 において `(1.0 - α)` はリテラル相補値と bit-equal に
//   ならない（例: `1.0 - 0.3 ≠ 0.7`）。定数化すると compute 経路の
//   浮動小数点結果が ULP レベルで変わり、既存セッションログの再現性を
//   損なう。これらは `// TUNE:` マーカーコメントで列挙可能にするのみとする。

/// HMM エンジンの挙動バージョン。
///
/// **このファイル内の以下の変更では必ず bump すること**:
/// - `INITIAL_PROBS` / `INITIAL_AXES_EWMA` / `BACKSPACE_PENALTY_THRESHOLD`
/// - `transition_matrix` / `emission_matrix` / `initial_probabilities` の値
/// - `update()` / `update_silence()` の内部 α 値・ヒステリシス α
/// - `update_silence()` の silence_secs → α 閾値
/// また `analysis/features.rs` の `phi` / `make_silence_observation` /
/// `calculate_features` の数値挙動変更、`analysis/loop_step.rs` の摩擦フロア
/// 変更も bump 対象。
///
/// SemVer 運用:
///
/// - MAJOR: 既存セッションログの確率列が大幅に変わる（状態優勢の逆転等）
/// - MINOR: 確率列は動くが同じラベル付けになる範囲の調整
/// - PATCH: ログ形式のみの変更（数値挙動不変）
///
/// `logger.rs` の session_start meta エントリに書き出され、
/// `gse-replay` がゴールデンスナップショットと突き合わせる際に検証する。
pub const HMM_VERSION: &str = "0.3.0";

/// TUNE: 初期事前確率 [Flow, Incubation, Stuck]
///
/// Flow 優勢で開始することで、セッション開始直後のサイレンス観測（f1=2000）
/// による過渡的な Incubation 方向への引き込みを吸収する。
/// HMM は数秒以内に実データに収束する。
const INITIAL_PROBS: [f64; 3] = [0.80, 0.15, 0.05];

/// TUNE: 潜在軸 (X=Friction, Y=Engagement) の初期 EWMA 値
///
/// (0.1, 0.8) = Flow 領域 (obs=4 付近、Flow 優勢ビン)。
/// `INITIAL_PROBS` と整合的な開始位置。
const INITIAL_AXES_EWMA: (f64, f64) = (0.1, 0.8);

/// TUNE: Backspace 連打によるペナルティビン (obs=25) 発動閾値
///
/// IME の正常な変換修正操作（通常 8-12 連打）を超える値として 14 を設定。
/// この値以上で `has_pending_penalty` フラグが立ち、次回 `update()` で
/// observation を obs=25 に強制し、Stuck 方向へ強く引く。
const BACKSPACE_PENALTY_THRESHOLD: u32 = 14;

/// HMM 更新時の内部診断データ。
/// ログに書き出してセッション後分析・HMM チューニングに使用する。
#[derive(Debug, Clone)]
pub struct UpdateDiagnostics {
    pub raw_x: f64,
    pub raw_y: f64,
    pub ewma_x: f64,
    pub ewma_y: f64,
    pub obs: usize,
    pub alpha: f64,
}

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
    pub is_paused: Arc<AtomicBool>,
    pub backspace_streak: Arc<AtomicU32>,
    // ペナルティ保留フラグ: streak >= 14 に達した瞬間にtrueになり、
    // update() で消費されるまで保持される。
    // register_keystroke() で streak をリセットしてもペナルティは取りこぼさない。
    has_pending_penalty: Arc<AtomicBool>,

    // 2-axis EWMA: (X = Friction, Y = Engagement)
    // α = 0.3: 新値30%、前値70%のブレンド
    axes_ewma: Arc<Mutex<(f64, f64)>>,

    // Hysteresis layer: slow EMA of reported probabilities.
    // Prevents instant state flips (e.g. Cold-Start after window reset).
    // α = 0.40 for normal updates (~2.5s time-constant).
    // α = 0.60 for backspace-penalty bin (faster Stuck response).
    display_probs: Arc<Mutex<[f64; 3]>>,

    // ADR-006 Alternative C: β baseline は「1 関数内の 2 択 if」ではなく
    // **head の所有物**である。どの head を走らせるかは task_kind (宣言) が決め、
    // ime_open (観測) は Writing head 内部の within-writing 信号として使う。
    //
    // 2a (抽出) では常に WritingHead が入る = Phase1 と完全に同じ挙動。
    // task_kind → head 選択の配線は 2b。
    head: Arc<dyn DomainInferenceHead>,
}

impl CognitiveStateEngine {
    pub fn new() -> Self {
        // TUNE: 遷移確率行列 (row-major, 3×3)
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

        // TUNE: 放出確率行列 B (3 states × 26 bins)
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
        // Penalty bin (obs=25): backspace_streak ≥ 14 → near-certain Stuck.
        //
        // 全ビンに最小値 0.01 を設定し、確率の完全消滅を防止。
        // 旧実装の EMISSION_FLOOR (+0.05 一律加算) を廃止:
        //   - 旧: ペナルティビン Stuck:Flow 比 = 1.04/0.05 = 20.8x（鈍い応答）
        //   - 新: ペナルティビン Stuck:Flow 比 = 0.99/0.01 = 99x（鋭い応答）
        // EWMA (α=0.3) とヒステリシス層 (α=0.25/0.50) が安定性を維持する。
        #[rustfmt::skip]
        let emissions: [f64; 78] = [
            // ── Flow (State 0) ─────────────────────────── non-penalty sum ≈ 1.03
            //  x=0 (low F)    y: 0     1     2     3     4
                               0.01, 0.02, 0.08, 0.12, 0.14,
            //  x=1            y: 0     1     2     3     4
                               0.01, 0.02, 0.08, 0.12, 0.13,
            //  x=2            y: 0     1     2     3     4
                               0.01, 0.01, 0.02, 0.01, 0.08,
            //  x=3            y: 0     1     2     3     4
                               0.01, 0.01, 0.01, 0.01, 0.01,
            //  x=4 (high F)   y: 0     1     2     3     4
                               0.01, 0.01, 0.01, 0.01, 0.01,
            //  penalty bin
                               0.01,

            // ── Incubation (State 1) ──────────────────── non-penalty sum ≈ 1.12
            //  x=0 (low F)    y: 0     1     2     3     4
                               0.15, 0.10, 0.04, 0.03, 0.02,
            //  x=1            y: 0     1     2     3     4
                               0.14, 0.08, 0.04, 0.03, 0.02,
            //  x=2            y: 0     1     2     3     4
                               0.10, 0.08, 0.03, 0.02, 0.01,
            //  x=3            y: 0     1     2     3     4
                               0.05, 0.04, 0.01, 0.01, 0.01,
            //  x=4 (high F)   y: 0     1     2     3     4
                               0.04, 0.03, 0.01, 0.01, 0.01,
            //  penalty bin
                               0.01,

            // ── Stuck (State 2) ─────────────────────────
            //  x=0 (low F)    y: 0     1     2     3     4
                               0.01, 0.01, 0.01, 0.01, 0.01,
            //  x=1            y: 0     1     2     3     4
                               0.01, 0.01, 0.01, 0.01, 0.01,
            //  x=2            y: 0     1     2     3     4
                               0.02, 0.04, 0.04, 0.05, 0.01,
            //  x=3            y: 0     1     2     3     4
                               0.10, 0.16, 0.05, 0.07, 0.01,
            //  x=4 (high F)   y: 0     1     2     3     4
                               0.16, 0.22, 0.12, 0.05, 0.02,
            //  penalty bin  (backspace streak ≥14 → near-certain Stuck)
                               0.99,
        ];

        Self {
            transitions: Arc::new(transitions),
            emissions: Arc::new(emissions),
            current_state_probs: Arc::new(Mutex::new(INITIAL_PROBS)),
            is_paused: Arc::new(AtomicBool::new(false)),
            backspace_streak: Arc::new(AtomicU32::new(0)),
            has_pending_penalty: Arc::new(AtomicBool::new(false)),
            axes_ewma: Arc::new(Mutex::new(INITIAL_AXES_EWMA)),
            // display_probs は INITIAL_PROBS と同値で初期化
            display_probs: Arc::new(Mutex::new(INITIAL_PROBS)),
            // ADR-006 2a: 既定は Writing head (Phase1 と同一挙動)。
            head: Arc::new(WritingHead::new()),
        }
    }

    /// HMM確率・EWMA・backspace_streakを初期値に戻す。
    /// セッション開始時に呼び出され、前回セッションの状態をリセットする。
    pub fn reset(&self) {
        match self.current_state_probs.lock() {
            Ok(mut p) => *p = INITIAL_PROBS,
            Err(poisoned) => *poisoned.into_inner() = INITIAL_PROBS,
        }
        match self.display_probs.lock() {
            Ok(mut p) => *p = INITIAL_PROBS,
            Err(poisoned) => *poisoned.into_inner() = INITIAL_PROBS,
        }
        match self.axes_ewma.lock() {
            Ok(mut e) => *e = INITIAL_AXES_EWMA,
            Err(poisoned) => *poisoned.into_inner() = INITIAL_AXES_EWMA,
        }
        self.backspace_streak.store(0, Ordering::Relaxed);
        self.has_pending_penalty.store(false, Ordering::Release);
        self.is_paused.store(false, Ordering::Release);
    }

    pub fn set_paused(&self, paused: bool) {
        self.is_paused.store(paused, Ordering::Release);
    }

    /// 全キー押下時に呼び出し、Backspaceストリークをリアルタイムでカウントする。
    /// 1Hz gate の外側（全打鍵）で呼ぶことで、高速Backspace連打を正確に検知する。
    ///
    /// streak >= 14 に達した時点で has_pending_penalty フラグを立てる。
    /// 閾値14はIMEの正常操作範囲（8-12連打）を超えた連打のみ検出する。
    /// 非BSキーで streak がリセットされても、フラグは update() で消費されるまで保持される。
    /// これにより「BS×12 → 即Enter」のようなケースでもペナルティを取りこぼさない。
    ///
    /// `is_backspace` の判定は呼び出し元（OS固有のフック処理）で行う。
    /// Windows: vk_code == 0x08 (VK_BACK), macOS: keycode == 0x33 (kVK_Delete)
    pub fn register_keystroke(&self, is_backspace: bool) {
        if is_backspace {
            let new_streak = self.backspace_streak.fetch_add(1, Ordering::Relaxed) + 1;
            if new_streak >= BACKSPACE_PENALTY_THRESHOLD {
                self.has_pending_penalty.store(true, Ordering::Release);
            }
        } else {
            self.backspace_streak.store(0, Ordering::Relaxed);
        }
    }

    /// IMEポーズ中かどうかを安全に取得する
    pub fn get_paused(&self) -> bool {
        self.is_paused.load(Ordering::Acquire)
    }

    /// B-5: HMM Update (2軸 Friction × Engagement、25+1ビン モデル)
    ///
    /// `ime_open`: true = Japanese IME is in Japanese-input mode (あ/カ).
    /// Head 内部で context-appropriate な β の選択に使われる
    /// (Writing head: β_writing / β_writing_latin の切替)。
    pub fn update(&self, features: &Features, ime_open: bool) -> Option<UpdateDiagnostics> {
        if self.get_paused() {
            return None;
        }

        // F1がゼロ（データ不足）の場合はスキップ。
        // ただし保留中のペナルティがある場合は処理を続行し、ペナルティビンを適用する。
        if features.f1_flight_time_median <= 0.0
            && !self.has_pending_penalty.load(Ordering::Acquire)
        {
            return None;
        }

        // --- Backspace Streak Logic ---
        // register_keystroke() が streak >= 14 到達時に has_pending_penalty を true に設定済み。
        // ここではフラグを消費（swap false）し、ペナルティビン（obs=25）を適用する。
        // IMEガード: ime_open=true 時はペナルティを無効化。IME変換修正のBS連打は
        // 認知的Stuckではなく正常操作のため。
        let pending = self.has_pending_penalty.swap(false, Ordering::AcqRel);
        let apply_backspace_penalty = pending && self.head.applies_backspace_penalty(ime_open);

        let (raw_x, raw_y) = self.head.latent_axes(features, ime_open);

        // TUNE: EWMA 平滑化 α = 0.3 (通常 update)
        // s_t = 0.3 * raw_t + 0.7 * s_{t-1}
        // 注: IEEE 754 の (1.0 - 0.3) ≠ 0.7 のため、定数抽出せずリテラル維持。
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
        // 放射確率は emission テーブルに最小値 0.01 を組み込み済み。
        // 旧 EMISSION_FLOOR (+0.05 一律加算) は廃止。
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
        drop(current); // MutexGuard 早期解放 — display_probs ロック前にデッドロックリスクを排除

        // ── Hysteresis Layer ──────────────────────────────────────────────
        // display_probs に EMA を適用し、ウィンドウリセット時の
        // Cold-Start 瞬間遷移 (Stuck→Flow in 1ms) を防ぐ。
        //
        // TUNE: ヒステリシス α
        //   α=0.40 (通常): 時定数 ≈ 2.5 更新 ≈ 2.5 秒
        //     emission floor 削除 (0.05→0.01) で HMM 応答が鋭くなったため、
        //     旧 α=0.25 (4秒) から引き上げて表示の追従速度を改善。
        //   α=0.60 (ペナルティ): Backspace 連続時は素早く Stuck に収束
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

        Some(UpdateDiagnostics {
            raw_x,
            raw_y,
            ewma_x: x,
            ewma_y: y,
            obs,
            alpha: 0.3,
        })
    }

    /// 無入力期間（サイレンス）用のHMM更新。
    /// 通常の `update()` (α=0.3) より低い α=0.15 で EWMA を緩やかに更新する。
    /// 深い沈黙 (≥15s) では α=0.25 に引き上げ、Stuck領域への到達を加速する。
    ///
    /// EWMA を完全凍結すると observation bin が固定され、HMM が遷移確率のみに依存して
    /// Stuck に到達できない（均衡点固着問題）。摩擦フロア付きの特徴量で緩やかに
    /// EWMA を更新することで、沈黙の深刻度を observation bin に反映する。
    pub fn update_silence(
        &self,
        features: &Features,
        ime_open: bool,
        silence_secs: f64,
    ) -> Option<UpdateDiagnostics> {
        if self.get_paused() {
            return None;
        }

        let (raw_x, raw_y) = self.head.latent_axes(features, ime_open);

        // TUNE: サイレンス時の動的 EWMA α — 沈黙深さに応じて段階的加速
        //   α=0.15: silence < 15s   (初期サイレンス、緩やかに推移)
        //   α=0.18: 15s ≤ silence < 25s  (中間ギア、Nudge 領域)
        //   α=0.25: silence ≥ 25s   (完全に固まった状態、Stuck 領域へ加速)
        let alpha = if silence_secs >= 25.0 {
            0.25
        } else if silence_secs >= 15.0 {
            0.18
        } else {
            0.15
        };

        // EWMA を緩やかに更新
        let (x, y) = match self.axes_ewma.lock() {
            Ok(mut ewma) => {
                ewma.0 = alpha * raw_x + (1.0 - alpha) * ewma.0;
                ewma.1 = alpha * raw_y + (1.0 - alpha) * ewma.1;
                (ewma.0, ewma.1)
            }
            Err(poisoned) => {
                let mut ewma = poisoned.into_inner();
                ewma.0 = alpha * raw_x + (1.0 - alpha) * ewma.0;
                ewma.1 = alpha * raw_y + (1.0 - alpha) * ewma.1;
                (ewma.0, ewma.1)
            }
        };

        let x_bin = (x * 5.0).floor().min(4.0) as usize;
        let y_bin = (y * 5.0).floor().min(4.0) as usize;
        let obs = x_bin * 5 + y_bin;

        // サイレンス中はペナルティビンを適用しない

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
                let t_prob = self.transitions[i * n_states + j];
                trans_sum += old_probs[i] * t_prob;
            }
            let e_prob = self.emissions[j * 26 + obs];
            new_probs[j] = trans_sum * e_prob;
            sum_prob += new_probs[j];
        }

        if sum_prob > 0.0 {
            for j in 0..n_states {
                new_probs[j] /= sum_prob;
            }
        }

        *current = new_probs;
        drop(current); // MutexGuard 早期解放

        // TUNE: ヒステリシス α=0.40 (update_silence は常に通常値)
        let mut display = match self.display_probs.lock() {
            Ok(g) => g,
            Err(poisoned) => poisoned.into_inner(),
        };
        let mut disp_sum = 0.0;
        for i in 0..n_states {
            display[i] = 0.40 * new_probs[i] + 0.60 * display[i];
            disp_sum += display[i];
        }
        if disp_sum > 0.0 {
            for v in display.iter_mut() {
                *v /= disp_sum;
            }
        }

        Some(UpdateDiagnostics {
            raw_x,
            raw_y,
            ewma_x: x,
            ewma_y: y,
            obs,
            alpha,
        })
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

// ============================================================================
// Unit tests (diagnostic — snapshot tests for tuning parameters)
// ============================================================================
//
// これらのテストは「意図しないパラメータドリフト」を検出するために存在する。
// 意図的な HMM チューニングでパラメータを変更した際は、テストも合わせて更新する。
// テスト更新を伴うチューニングは `.steering/` に根拠を残すこと。

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::atomic::Ordering;

    // ---------- Transition / Emission / Initial Probs Snapshots ----------

    #[test]
    fn transition_matrix_snapshot() {
        // 9 要素 (行優先): Flow/Incubation/Stuck からの遷移確率。
        // 各行の合計 = 1.0 であることも同時に検証する。
        let e = CognitiveStateEngine::new();
        let t = e.transitions.as_ref();
        let expected: [f64; 9] = [
            0.75, 0.17, 0.08, // Flow →
            0.12, 0.80, 0.08, // Incubation →
            0.06, 0.18, 0.76, // Stuck →
        ];
        for (i, (a, b)) in t.iter().zip(expected.iter()).enumerate() {
            assert!(
                (a - b).abs() < 1e-9,
                "transitions[{}] drift: got {}, expected {}",
                i,
                a,
                b
            );
        }
        // 行和 = 1.0 の確認
        for row in 0..3 {
            let sum: f64 = t[row * 3..(row + 1) * 3].iter().sum();
            assert!(
                (sum - 1.0).abs() < 1e-9,
                "transition row {} does not sum to 1.0: {}",
                row,
                sum
            );
        }
    }

    #[test]
    fn emission_matrix_snapshot() {
        // 3 states × 26 bins = 78 要素。
        // ドリフト検出のため全値を固定比較する。
        // 意図的チューニング時はここも更新。
        let e = CognitiveStateEngine::new();
        let em = e.emissions.as_ref();
        #[rustfmt::skip]
        let expected: [f64; 78] = [
            // Flow (state 0), bins 0..25
            0.01, 0.02, 0.08, 0.12, 0.14,
            0.01, 0.02, 0.08, 0.12, 0.13,
            0.01, 0.01, 0.02, 0.01, 0.08,
            0.01, 0.01, 0.01, 0.01, 0.01,
            0.01, 0.01, 0.01, 0.01, 0.01,
            0.01, // penalty bin
            // Incubation (state 1)
            0.15, 0.10, 0.04, 0.03, 0.02,
            0.14, 0.08, 0.04, 0.03, 0.02,
            0.10, 0.08, 0.03, 0.02, 0.01,
            0.05, 0.04, 0.01, 0.01, 0.01,
            0.04, 0.03, 0.01, 0.01, 0.01,
            0.01, // penalty bin
            // Stuck (state 2)
            0.01, 0.01, 0.01, 0.01, 0.01,
            0.01, 0.01, 0.01, 0.01, 0.01,
            0.02, 0.04, 0.04, 0.05, 0.01,
            0.10, 0.16, 0.05, 0.07, 0.01,
            0.16, 0.22, 0.12, 0.05, 0.02,
            0.99, // penalty bin: near-certain Stuck
        ];
        for (i, (a, b)) in em.iter().zip(expected.iter()).enumerate() {
            assert!(
                (a - b).abs() < 1e-9,
                "emissions[{}] drift: got {}, expected {}",
                i,
                a,
                b
            );
        }
    }

    #[test]
    fn initial_probabilities_snapshot() {
        // 初期事前確率 [Flow, Incubation, Stuck] = [0.80, 0.15, 0.05]
        // Flow 優勢で開始することでセッション開始直後のフリッカーを防止する。
        let e = CognitiveStateEngine::new();
        let probs = e.current_state_probs.lock().unwrap();
        assert!((probs[0] - 0.80).abs() < 1e-9, "Flow prior drifted");
        assert!((probs[1] - 0.15).abs() < 1e-9, "Incubation prior drifted");
        assert!((probs[2] - 0.05).abs() < 1e-9, "Stuck prior drifted");
        // 確率の合計 = 1.0
        let sum: f64 = probs.iter().sum();
        assert!((sum - 1.0).abs() < 1e-9, "initial probs do not sum to 1.0");
    }

    #[test]
    fn emission_penalty_bin_near_certain_stuck() {
        // ペナルティビン (obs=25) は Stuck:Flow 比 ≈ 99× の鋭い応答を維持する。
        // EMISSION_FLOOR (+0.05) 廃止後の設計意図を確認。
        let e = CognitiveStateEngine::new();
        let em = e.emissions.as_ref();
        // 各 state の penalty bin index = state * 26 + 25
        let flow_penalty = em[25];
        let inc_penalty = em[26 + 25];
        let stuck_penalty = em[52 + 25];
        assert!((flow_penalty - 0.01).abs() < 1e-9);
        assert!((inc_penalty - 0.01).abs() < 1e-9);
        assert!((stuck_penalty - 0.99).abs() < 1e-9);
        // Stuck:Flow 比 ≈ 99
        assert!((stuck_penalty / flow_penalty - 99.0).abs() < 1e-6);
    }

    // ---------- register_keystroke() ----------

    #[test]
    fn register_keystroke_non_backspace_resets_streak() {
        let e = CognitiveStateEngine::new();
        e.register_keystroke(true); // BS
        e.register_keystroke(true); // BS
        e.register_keystroke(true); // BS
        assert_eq!(e.backspace_streak.load(Ordering::Relaxed), 3);
        e.register_keystroke(false); // non-BS
        assert_eq!(e.backspace_streak.load(Ordering::Relaxed), 0);
    }

    #[test]
    fn register_keystroke_streak_at_13_does_not_trigger_penalty() {
        // 境界値: 13 連打ではフラグが立たない
        let e = CognitiveStateEngine::new();
        for _ in 0..13 {
            e.register_keystroke(true);
        }
        assert_eq!(e.backspace_streak.load(Ordering::Relaxed), 13);
        assert!(!e.has_pending_penalty.load(Ordering::Acquire));
    }

    #[test]
    fn register_keystroke_streak_at_14_triggers_pending_penalty() {
        // 閾値: 14 連打到達でフラグが立つ
        let e = CognitiveStateEngine::new();
        for _ in 0..14 {
            e.register_keystroke(true);
        }
        assert_eq!(e.backspace_streak.load(Ordering::Relaxed), 14);
        assert!(e.has_pending_penalty.load(Ordering::Acquire));
    }

    #[test]
    fn register_keystroke_penalty_flag_persists_through_non_bs() {
        // BS×14 で立ったフラグは、非 BS キーでストリークがリセットされても保持される
        // （次の update() で消費されるまで）。
        let e = CognitiveStateEngine::new();
        for _ in 0..14 {
            e.register_keystroke(true);
        }
        assert!(e.has_pending_penalty.load(Ordering::Acquire));
        e.register_keystroke(false); // non-BS → streak リセット
        assert_eq!(e.backspace_streak.load(Ordering::Relaxed), 0);
        // フラグは依然立っている
        assert!(e.has_pending_penalty.load(Ordering::Acquire));
    }

    #[test]
    fn reset_clears_all_state() {
        // reset() は全ての可変状態を初期値に戻す
        let e = CognitiveStateEngine::new();
        for _ in 0..14 {
            e.register_keystroke(true);
        }
        e.set_paused(true);
        assert!(e.has_pending_penalty.load(Ordering::Acquire));
        assert!(e.get_paused());

        e.reset();

        assert_eq!(e.backspace_streak.load(Ordering::Relaxed), 0);
        assert!(!e.has_pending_penalty.load(Ordering::Acquire));
        assert!(!e.get_paused());
        let probs = e.current_state_probs.lock().unwrap();
        assert!((probs[0] - 0.80).abs() < 1e-9);
        assert!((probs[1] - 0.15).abs() < 1e-9);
        assert!((probs[2] - 0.05).abs() < 1e-9);
    }

    // ---------- ADR-006 Phase 2a: 抽出が挙動を変えていないことのガード ----------

    /// 抽出 (Writing head への β 移送) は **挙動不変**でなければならない。
    /// `HMM_VERSION` が動いていたら、それは抽出ではなく配線 (2b) を混ぜている。
    ///
    /// 根拠: ADR-006 Migration step 3 / ADR-002 Consequences
    /// (acceptance = replay --snapshot byte-equal / calibration parity / HMM_VERSION 不変)
    #[test]
    fn hmm_version_is_unchanged_by_extraction() {
        assert_eq!(
            HMM_VERSION, "0.3.0",
            "2a (抽出) で HMM_VERSION を bump してはならない。bump が要るのは 2b (task_kind → head 配線) であり、別コミットに分ける。"
        );
    }

    /// 既定の engine は Writing head を積む = Phase1 と同一経路。
    #[test]
    fn default_engine_uses_writing_head() {
        let e = CognitiveStateEngine::new();
        assert_eq!(e.head.head_id(), "writing");
    }

    /// backspace ペナルティ gate は head 経由になっても `!ime_open` のままである。
    #[test]
    fn backspace_penalty_gate_is_delegated_to_head() {
        let e = CognitiveStateEngine::new();
        assert!(e.head.applies_backspace_penalty(false));
        assert!(!e.head.applies_backspace_penalty(true));
    }
}
