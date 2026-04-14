use std::collections::VecDeque;

#[derive(Debug, Clone, Copy)]
pub struct InputEvent {
    pub vk_code: u32,
    pub timestamp: u64, // ms
    pub is_press: bool,
    pub is_repeat: bool,
    pub is_backspace: bool,
}

/// B-1: 5特徴量を格納する構造体
/// F2 (Flight Time 分散) は HMM の潜在軸計算で未使用のため除去済み。
#[derive(Debug, Clone)]
pub struct Features {
    /// F1: Flight Time 中央値 (ms)
    pub f1_flight_time_median: f64,
    /// F3: 修正率 = (BS + Del) / 全キー数
    pub f3_correction_rate: f64,
    /// F4: バースト長 = 連続FT<200ms の平均文字数
    pub f4_burst_length: f64,
    /// F5: ポーズ回数 = 2秒以上の無入力回数
    pub f5_pause_count: f64,
    /// F6: 削除後停止率 = BS/Del直後2秒以上停止する割合
    pub f6_pause_after_del_rate: f64,
}

impl Default for Features {
    fn default() -> Self {
        Self {
            f1_flight_time_median: 0.0,
            f3_correction_rate: 0.0,
            f4_burst_length: 0.0,
            f5_pause_count: 0.0,
            f6_pause_after_del_rate: 0.0,
        }
    }
}

/// B-2: 個人ベースライン正規化関数 φ(x, β) = clamp((x − β) / (κ · β), 0.0, 1.0)
///
/// TUNE: κ = 2.0 — 「β の 2 倍を上限」として正規化する感度パラメータ
pub fn phi(x: f64, beta: f64) -> f64 {
    const KAPPA: f64 = 2.0;
    if beta <= 0.0 {
        return 0.0;
    }
    ((x - beta) / (KAPPA * beta)).clamp(0.0, 1.0)
}

pub struct FeatureExtractor {
    buffer: VecDeque<InputEvent>,
    capacity: usize,
}

impl FeatureExtractor {
    pub fn new(capacity: usize) -> Self {
        Self {
            buffer: VecDeque::with_capacity(capacity),
            capacity,
        }
    }

    /// セッション開始時にバッファをクリアする。
    pub fn reset(&mut self) {
        self.buffer.clear();
    }

    pub fn process_event(&mut self, event: InputEvent) {
        if self.buffer.len() >= self.capacity {
            self.buffer.pop_front();
        }
        self.buffer.push_back(event);
    }

    /// B-1: 直近30秒のバッファから5特徴量を算出する
    pub fn calculate_features(&self) -> Features {
        if self.buffer.is_empty() {
            return Features::default();
        }

        let last_ts = self.buffer.back().unwrap().timestamp;
        // TUNE: 特徴量計算ウィンドウ = 30 秒 (30,000 ms)
        let cutoff = last_ts.saturating_sub(30_000);

        // 直近30秒のイベントを収集
        let events: Vec<&InputEvent> = self
            .buffer
            .iter()
            .filter(|e| e.timestamp >= cutoff)
            .collect();

        if events.is_empty() {
            return Features::default();
        }

        // --- ウィンドウ内のフライトタイムを計算 (F1) ---
        // キーリピートを除外して正確なタイピングリズムを測定する。
        // リピート判定はフック層の is_repeat フラグを使用する。
        // 注: 非タイピングキーはフック層 (hook.rs) で既にフィルタ済み。
        let mut window_fts: Vec<f64> = Vec::new();
        let mut last_release: Option<u64> = None;

        for event in &events {
            if event.is_repeat {
                continue;
            }
            if event.is_press {
                if let Some(rel) = last_release {
                    if event.timestamp >= rel {
                        let ft = (event.timestamp - rel) as f64;
                        // TUNE: Flight Time の上限キャップ 2000 ms (これ以上は外れ値として除外)
                        if ft < 2000.0 {
                            window_fts.push(ft);
                        }
                    }
                }
            } else {
                last_release = Some(event.timestamp);
            }
        }

        // --- F1: Flight Time 中央値 (30秒ウィンドウ内) ---
        // F2 除去済みのため in-place ソート (clone不要)
        let f1 = if window_fts.is_empty() {
            0.0
        } else {
            window_fts
                .sort_unstable_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
            let len = window_fts.len();
            if len % 2 == 0 {
                (window_fts[len / 2 - 1] + window_fts[len / 2]) / 2.0
            } else {
                window_fts[len / 2]
            }
        };

        // --- キー押下イベントのみ抽出 ---
        let press_events: Vec<&&InputEvent> = events.iter().filter(|e| e.is_press).collect();

        let total_keys = press_events.len();

        // --- F3: 修正率 = (BS + Del) / 全キー押下数 ---
        let correction_keys = press_events.iter().filter(|e| e.is_backspace).count();

        let f3 = if total_keys > 0 {
            correction_keys as f64 / total_keys as f64
        } else {
            0.0
        };

        // --- F4: バースト長 = 連続FT<200ms のチャンクの平均文字数 ---
        // リピートイベントを除外して真のタイピングバーストを測定する。
        let mut burst_lengths: Vec<usize> = Vec::new();
        let mut current_burst: usize = 0;
        let mut last_rel_for_burst: Option<u64> = None;

        for event in &events {
            if event.is_repeat {
                continue;
            }
            if event.is_press {
                if let Some(rel) = last_rel_for_burst {
                    let ft = event.timestamp.saturating_sub(rel);
                    // TUNE: バースト判定閾値 200 ms (これ未満の連続打鍵をバーストとみなす)
                    if ft < 200 {
                        current_burst += 1;
                    } else {
                        if current_burst > 0 {
                            burst_lengths.push(current_burst);
                        }
                        current_burst = 1;
                    }
                } else {
                    current_burst = 1;
                }
            } else {
                last_rel_for_burst = Some(event.timestamp);
            }
        }
        if current_burst > 0 {
            burst_lengths.push(current_burst);
        }

        let f4 = if !burst_lengths.is_empty() {
            burst_lengths.iter().sum::<usize>() as f64 / burst_lengths.len() as f64
        } else {
            0.0
        };

        // --- F5: ポーズ回数 = 連続キー押下間で2秒以上の間隔の数 ---
        let press_ts: Vec<u64> = events
            .iter()
            .filter(|e| e.is_press)
            .map(|e| e.timestamp)
            .collect();

        // TUNE: ポーズ判定閾値 2000 ms (F5, F6 共通)
        let f5 = press_ts
            .windows(2)
            .filter(|w| w[1].saturating_sub(w[0]) >= 2000)
            .count() as f64;

        // --- F6: 削除後停止率 = BS/Del直後に2秒以上停止する割合 ---
        let del_count = press_events.iter().filter(|e| e.is_backspace).count();

        // 連続するキー押下ペアで、先頭がBS/Del かつ間隔>=2sのものを数える
        let del_followed_by_pause = press_ts
            .windows(2)
            .zip(press_events.windows(2))
            .filter(|(ts_win, ev_win)| {
                let is_del = ev_win[0].is_backspace;
                let long_pause = ts_win[1].saturating_sub(ts_win[0]) >= 2000;
                is_del && long_pause
            })
            .count();

        let f6 = if del_count > 0 {
            del_followed_by_pause as f64 / del_count as f64
        } else {
            0.0
        };

        Features {
            f1_flight_time_median: f1,
            f3_correction_rate: f3,
            f4_burst_length: f4,
            f5_pause_count: f5,
            f6_pause_after_del_rate: f6,
        }
    }

    /// 沈黙 3 状態機構の **SilencePath** 用合成観測値を生成する（バッファ空時に使用）。
    ///
    /// 呼び出し元: `lib.rs` 分析スレッドの SilencePath ブランチ（バッファ空時）。
    /// TransitionPath（バッファあり + 沈黙）は独自の摩擦フロアを持ち、
    /// 本関数を呼ばない — 閾値の不一致は設計上の分離（詳細は lib.rs のコメント参照）。
    ///
    /// `silence_secs < 2.0` の場合は None を返す（ポーズとして認識しない）。
    pub fn make_silence_observation(&self, silence_secs: f64) -> Option<Features> {
        if silence_secs < 2.0 {
            return None;
        }

        // TUNE: F1 = 2000 ms — 「現在タイピングしていない = Flight Time が事実上無限大」の意味付け
        let f1 = 2000.0_f64;

        // TUNE: Synthetic Friction — SilencePath 用合成摩擦値ランプ
        // 早期オンセット + フロア値で、沈黙開始後の Stuck 到達を高速化する。
        //   F6: onset 10s / ramp 40s / floor 0.15 (≥ 10s 時)  → ~50s で 1.0 到達
        //   F3: onset 15s / ramp 50s / floor 0.20 (≥ 10s 時)  → ~65s で 1.0 到達
        // 注: `lib.rs` の TransitionPath ブランチ（分析スレッド内）にも類似ロジックがあり、
        //     閾値 (F6 onset 8s / F3 onset 10s) が本関数と異なる。統合せず 3 状態機構として
        //     共存させる判断の詳細は `docs/architecture.md §4.7` および
        //     `.steering/20260414-improvement-roadmap/decisions.md` 判断 3 を参照。
        let f6_synthetic = if silence_secs >= 10.0 {
            (((silence_secs - 10.0) / 40.0).clamp(0.0, 1.0)).max(0.15)
        } else {
            ((silence_secs - 10.0) / 40.0).clamp(0.0, 1.0)
        };

        let f3_synthetic = if silence_secs >= 10.0 {
            (((silence_secs - 15.0) / 50.0).clamp(0.0, 1.0)).max(0.20)
        } else {
            ((silence_secs - 15.0) / 50.0).clamp(0.0, 1.0)
        };

        Some(Features {
            f1_flight_time_median: f1,
            f3_correction_rate: f3_synthetic,
            f4_burst_length: 0.0,
            f5_pause_count: silence_secs / 2.0,
            f6_pause_after_del_rate: f6_synthetic,
        })
    }
}

// ============================================================================
// Unit tests (diagnostic — capture current behavior to prevent regressions)
// ============================================================================
//
// Phase 0 リファクタの一環として既存挙動を捕獲する。
// 将来のチューニングで意図的にパラメータを変更した際は、テスト側も一緒に更新する。
// - phi(): 境界値・ゼロ除算ガード
// - make_silence_observation(): 閾値前後のフロア/ランプ挙動
// - calculate_features(): 既知入力列 → 期待特徴量

#[cfg(test)]
mod tests {
    use super::*;

    const EPS: f64 = 1e-9;

    fn approx_eq(a: f64, b: f64) -> bool {
        (a - b).abs() < EPS
    }

    // ---------- phi() ----------

    #[test]
    fn phi_at_baseline_returns_zero() {
        assert!(approx_eq(phi(0.06, 0.06), 0.0));
    }

    #[test]
    fn phi_below_baseline_clamps_to_zero() {
        // x < β は下限クランプで 0.0
        assert!(approx_eq(phi(0.03, 0.06), 0.0));
    }

    #[test]
    fn phi_midpoint_returns_half() {
        // φ(x=2β, β) = (2β − β) / (2β) = 0.5
        assert!(approx_eq(phi(0.12, 0.06), 0.5));
    }

    #[test]
    fn phi_at_triple_baseline_clamps_to_one() {
        // φ(x=3β, β) = (3β − β) / (2β) = 1.0（上限クランプ境界）
        assert!(approx_eq(phi(0.18, 0.06), 1.0));
    }

    #[test]
    fn phi_way_above_baseline_clamps_to_one() {
        assert!(approx_eq(phi(10.0, 0.06), 1.0));
    }

    #[test]
    fn phi_with_zero_beta_returns_zero() {
        // β=0 ゼロ除算ガード
        assert!(approx_eq(phi(1.0, 0.0), 0.0));
    }

    #[test]
    fn phi_with_negative_beta_returns_zero() {
        assert!(approx_eq(phi(1.0, -0.1), 0.0));
    }

    // ---------- make_silence_observation() ----------

    fn extractor() -> FeatureExtractor {
        FeatureExtractor::new(600)
    }

    #[test]
    fn silence_below_2s_returns_none() {
        assert!(extractor().make_silence_observation(1.9).is_none());
        assert!(extractor().make_silence_observation(0.0).is_none());
    }

    #[test]
    fn silence_at_2s_has_no_friction_floors() {
        // 2s 時点では F3/F6 ともフロアなし、F5 は累積（2/2=1.0）
        let f = extractor().make_silence_observation(2.0).unwrap();
        assert!(approx_eq(f.f1_flight_time_median, 2000.0));
        assert!(approx_eq(f.f3_correction_rate, 0.0));
        assert!(approx_eq(f.f4_burst_length, 0.0));
        assert!(approx_eq(f.f5_pause_count, 1.0));
        assert!(approx_eq(f.f6_pause_after_del_rate, 0.0));
    }

    #[test]
    fn silence_just_before_10s_has_no_floors() {
        // 10s 直前では floor が効かない（閾値境界確認）
        let f = extractor().make_silence_observation(9.99).unwrap();
        assert!(approx_eq(f.f6_pause_after_del_rate, 0.0));
        assert!(approx_eq(f.f3_correction_rate, 0.0));
    }

    #[test]
    fn silence_at_10s_applies_both_floors() {
        // 10s 到達で F6 フロア 0.15 / F3 フロア 0.20 が適用される。
        // ランプ自体は F6=10s/ F3=15s から立ち上がるため、
        // 10s 時点では「フロアのみ」が効いている状態。
        let f = extractor().make_silence_observation(10.0).unwrap();
        assert!(approx_eq(f.f6_pause_after_del_rate, 0.15));
        assert!(approx_eq(f.f3_correction_rate, 0.20));
        assert!(approx_eq(f.f5_pause_count, 5.0));
        assert!(approx_eq(f.f1_flight_time_median, 2000.0));
    }

    #[test]
    fn silence_at_30s_f6_ramps_past_floor() {
        // 30s: F6 = max((30-10)/40, 0.15) = 0.5
        //      F3 = max((30-15)/50, 0.20) = 0.3
        let f = extractor().make_silence_observation(30.0).unwrap();
        assert!(approx_eq(f.f6_pause_after_del_rate, 0.5));
        assert!(approx_eq(f.f3_correction_rate, 0.3));
        assert!(approx_eq(f.f5_pause_count, 15.0));
    }

    #[test]
    fn silence_at_50s_f6_saturates_f3_near_saturation() {
        // 50s: F6 = max((50-10)/40, 0.15) = 1.0（飽和）
        //      F3 = max((50-15)/50, 0.20) = 0.7
        let f = extractor().make_silence_observation(50.0).unwrap();
        assert!(approx_eq(f.f6_pause_after_del_rate, 1.0));
        assert!(approx_eq(f.f3_correction_rate, 0.7));
    }

    #[test]
    fn silence_at_100s_both_saturate() {
        let f = extractor().make_silence_observation(100.0).unwrap();
        assert!(approx_eq(f.f6_pause_after_del_rate, 1.0));
        assert!(approx_eq(f.f3_correction_rate, 1.0));
    }

    // ---------- calculate_features() ----------

    fn key_press(vk: u32, t: u64) -> InputEvent {
        InputEvent {
            vk_code: vk,
            timestamp: t,
            is_press: true,
            is_repeat: false,
            is_backspace: false,
        }
    }

    fn key_release(vk: u32, t: u64) -> InputEvent {
        InputEvent {
            vk_code: vk,
            timestamp: t,
            is_press: false,
            is_repeat: false,
            is_backspace: false,
        }
    }

    fn backspace_press(t: u64) -> InputEvent {
        InputEvent {
            vk_code: 0x08, // VK_BACK
            timestamp: t,
            is_press: true,
            is_repeat: false,
            is_backspace: true,
        }
    }

    #[test]
    fn calculate_features_empty_buffer_returns_defaults() {
        let e = extractor();
        let f = e.calculate_features();
        assert!(approx_eq(f.f1_flight_time_median, 0.0));
        assert!(approx_eq(f.f3_correction_rate, 0.0));
        assert!(approx_eq(f.f4_burst_length, 0.0));
        assert!(approx_eq(f.f5_pause_count, 0.0));
        assert!(approx_eq(f.f6_pause_after_del_rate, 0.0));
    }

    #[test]
    fn calculate_features_flight_time_median_from_press_release_pairs() {
        // press/release シーケンス:
        //   A press@0    release@50
        //   B press@150  release@200  → FT = 150 − 50 = 100
        //   C press@350  release@400  → FT = 350 − 200 = 150
        //   D press@500  release@550  → FT = 500 − 400 = 100
        // fts = [100, 150, 100] sorted = [100, 100, 150], len=3, median = index 1 = 100
        let mut e = extractor();
        e.process_event(key_press(0x41, 0));
        e.process_event(key_release(0x41, 50));
        e.process_event(key_press(0x42, 150));
        e.process_event(key_release(0x42, 200));
        e.process_event(key_press(0x43, 350));
        e.process_event(key_release(0x43, 400));
        e.process_event(key_press(0x44, 500));
        e.process_event(key_release(0x44, 550));
        let f = e.calculate_features();
        assert!(approx_eq(f.f1_flight_time_median, 100.0));
    }

    #[test]
    fn calculate_features_correction_rate_counts_backspace_ratio() {
        // Press 3 keys: A, BS, B → F3 = 1/3
        let mut e = extractor();
        e.process_event(key_press(0x41, 0));
        e.process_event(backspace_press(100));
        e.process_event(key_press(0x42, 200));
        let f = e.calculate_features();
        assert!(approx_eq(f.f3_correction_rate, 1.0 / 3.0));
    }

    #[test]
    fn calculate_features_pause_count_counts_2s_gaps() {
        // 3 presses at t=0, 2500, 5100 → 2 pauses (>= 2000 ms gap)
        let mut e = extractor();
        e.process_event(key_press(0x41, 0));
        e.process_event(key_press(0x42, 2500));
        e.process_event(key_press(0x43, 5100));
        let f = e.calculate_features();
        assert!(approx_eq(f.f5_pause_count, 2.0));
    }

    #[test]
    fn calculate_features_ignores_repeats_in_flight_time() {
        // is_repeat=true のイベントは FT 計算から除外される
        let mut e = extractor();
        e.process_event(key_press(0x41, 0));
        e.process_event(key_release(0x41, 50));
        let mut repeat = key_press(0x41, 100);
        repeat.is_repeat = true;
        e.process_event(repeat);
        e.process_event(key_press(0x42, 200));
        e.process_event(key_release(0x42, 250));
        // リピート除外により FT は 200 − 50 = 150 の 1 本のみ → median = 150
        let f = e.calculate_features();
        assert!(approx_eq(f.f1_flight_time_median, 150.0));
    }
}
