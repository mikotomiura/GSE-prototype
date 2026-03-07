use std::collections::VecDeque;

#[derive(Debug, Clone, Copy)]
pub struct InputEvent {
    pub vk_code: u32,
    pub timestamp: u64, // ms
    pub is_press: bool,
    pub is_repeat: bool,
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
/// κ = 2.0
pub fn phi(x: f64, beta: f64) -> f64 {
    const KAPPA: f64 = 2.0;
    if beta <= 0.0 {
        return 0.0;
    }
    ((x - beta) / (KAPPA * beta)).clamp(0.0, 1.0)
}

// Virtual key codes
const VK_BACK: u32 = 0x08;
const VK_DELETE: u32 = 0x2E;

/// タイピングリズムに関連するキーかどうかを判定する。
/// Flight Time 計算の対象を限定し、矢印キー・ファンクションキー・IMEモードキー等の
/// ノイズを除外する。
pub fn is_typing_key(vk_code: u32) -> bool {
    matches!(
        vk_code,
        // Letters A-Z
        0x41..=0x5A
        // Digits 0-9
        | 0x30..=0x39
        // Numpad keys (0-9, multiply, add, separator, subtract, decimal, divide)
        | 0x60..=0x6F
        // Symbol / punctuation keys (OEM)
        | 0xBA..=0xC0
        | 0xDB..=0xDF
        // Editing keys
        | 0x08  // Backspace
        | 0x0D  // Enter
        | 0x20  // Space
        | 0x09  // Tab
        | 0x2E  // Delete
    )
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
        let cutoff = last_ts.saturating_sub(30_000);

        // 直近30秒のイベントを収集
        let events: Vec<&InputEvent> = self.buffer.iter()
            .filter(|e| e.timestamp >= cutoff)
            .collect();

        if events.is_empty() {
            return Features::default();
        }

        // --- ウィンドウ内のフライトタイムを計算 (F1) ---
        // キーリピートと非タイピングキーを除外して正確なタイピングリズムを測定する。
        // リピート判定はフック層の is_repeat フラグを使用する。
        let mut window_fts: Vec<f64> = Vec::new();
        let mut last_release: Option<u64> = None;

        for event in &events {
            if event.is_repeat {
                continue;
            }
            if event.is_press {
                // Flight time: only non-repeat, typing keys
                if is_typing_key(event.vk_code) {
                    if let Some(rel) = last_release {
                        if event.timestamp >= rel {
                            let ft = (event.timestamp - rel) as f64;
                            if ft < 2000.0 {
                                window_fts.push(ft);
                            }
                        }
                    }
                }
            } else if is_typing_key(event.vk_code) {
                last_release = Some(event.timestamp);
            }
        }

        // --- F1: Flight Time 中央値 (30秒ウィンドウ内) ---
        // F2 除去済みのため in-place ソート (clone不要)
        let f1 = if window_fts.is_empty() {
            0.0
        } else {
            window_fts.sort_unstable_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
            let len = window_fts.len();
            if len % 2 == 0 {
                (window_fts[len / 2 - 1] + window_fts[len / 2]) / 2.0
            } else {
                window_fts[len / 2]
            }
        };

        // --- キー押下イベントのみ抽出 ---
        let press_events: Vec<&&InputEvent> = events.iter()
            .filter(|e| e.is_press)
            .collect();

        let total_keys = press_events.len();

        // --- F3: 修正率 = (BS + Del) / 全キー押下数 ---
        let correction_keys = press_events.iter()
            .filter(|e| e.vk_code == VK_BACK || e.vk_code == VK_DELETE)
            .count();

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
        let press_ts: Vec<u64> = events.iter()
            .filter(|e| e.is_press)
            .map(|e| e.timestamp)
            .collect();

        let f5 = press_ts.windows(2)
            .filter(|w| w[1].saturating_sub(w[0]) >= 2000)
            .count() as f64;

        // --- F6: 削除後停止率 = BS/Del直後に2秒以上停止する割合 ---
        let del_count = press_events.iter()
            .filter(|e| e.vk_code == VK_BACK || e.vk_code == VK_DELETE)
            .count();

        // 連続するキー押下ペアで、先頭がBS/Del かつ間隔>=2sのものを数える
        let del_followed_by_pause = press_ts.windows(2).zip(press_events.windows(2))
            .filter(|(ts_win, ev_win)| {
                let is_del = ev_win[0].vk_code == VK_BACK || ev_win[0].vk_code == VK_DELETE;
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

    /// サイレンス期間（無入力）の合成観測値を生成する。
    /// silence_secs < 2.0 の場合は None を返す（ポーズとして認識しない）。
    pub fn make_silence_observation(&self, silence_secs: f64) -> Option<Features> {
        if silence_secs < 2.0 {
            return None;
        }

        // F1=2000ms: 「現在タイピングしていない = Flight Time が事実上無限大」
        let f1 = 2000.0_f64;

        // Synthetic Friction（合成摩擦値）:
        // 早期オンセット + フロア値で、沈黙開始後のStuck到達を高速化。
        // f6: 8秒から開始、10秒以上でフロア0.15を保証、33秒で0.50到達
        // f3: 15秒から開始、10秒以上でフロア0.20を保証、47秒で0.40到達
        let f6_synthetic = if silence_secs >= 10.0 {
            (((silence_secs - 8.0) / 50.0).clamp(0.0, 0.50)).max(0.15)
        } else {
            ((silence_secs - 8.0) / 50.0).clamp(0.0, 0.50)
        };

        let f3_synthetic = if silence_secs >= 10.0 {
            (((silence_secs - 15.0) / 80.0).clamp(0.0, 0.40)).max(0.20)
        } else {
            ((silence_secs - 15.0) / 80.0).clamp(0.0, 0.40)
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
