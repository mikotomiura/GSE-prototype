//! 手跡の状態の純関数（ADR-051 D5 のライブの契約と再生の契約）。
//!
//! 入力は「打鍵の時刻の列」「種」「起点 `t0`」「時刻 `t`」だけで、キーの種類を受ける口が型に無い。
//! 式と定数は試作 `handmark_wind.rs`（`Wind::tick`）をそのまま移した。ライブも再生も同じ [`Stage`] を通す。
//!
//! ## 呼び出しの契約
//!
//! 打鍵 `p` は `advance_to(p)` の後に `press(p)` で入れる（時刻順）。`advance_to` は 250ms の格子の点
//! （絶対時刻の 250 の倍数）まで刻みを進める。格子を過ぎてから届いた打鍵は、その時刻のまま輪に入るが
//! すでに進んだ刻みには効かない（ライブで遅れて届くとき、再生と差が出うる。1b で受信の時刻を渡す側が
//! 守る）。描画の回数は状態に影響しない（`advance_to` を何回に分けても同じ）。

/// 風の目標を決める間隔。
pub const TICK_MS: u64 = 250;
const COUNT_MS: u64 = 1_000;
const STOP_MS: u64 = 2_000;
const SPEED_PER_KEY: f64 = 0.05;
const MAX_KEYS_PER_SEC: usize = 14;
const WIND_DECAY: f64 = 0.88;
const MIN_SPEED: f64 = 0.002;
const IRREG_MS: u64 = 10_000;
const IRREG_MIN_GAPS: usize = 4;
const IRREG_DECAY: f64 = 0.96;
const MIN_IRREG: f64 = 0.002;
/// 打鍵の時刻を持つ輪の大きさ。
const CAP: usize = 256;
/// 漂いの種からのずれの幅（秒）。
const DRIFT_SPAN_S: f64 = 1_000.0;

/// splitmix64 の状態を持つ擬似乱数（依存を増やさない・表の生成と種の導出で共有する）。
#[derive(Debug, Clone)]
pub struct SplitMix64 {
    state: u64,
}

impl SplitMix64 {
    pub fn new(seed: u64) -> Self {
        Self { state: seed }
    }

    pub fn next_u64(&mut self) -> u64 {
        self.state = self.state.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.state;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }

    /// `[0, n)` の一様な整数（`n == 0` は 0）。
    pub fn below(&mut self, n: u64) -> u64 {
        if n == 0 {
            return 0;
        }
        ((u128::from(self.next_u64()) * u128::from(n)) >> 64) as u64
    }
}

/// 1 回分の splitmix64（`x` から 1 つ出す）。
pub fn splitmix64(x: u64) -> u64 {
    SplitMix64::new(x).next_u64()
}

/// 窓へ渡す状態。
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct StageState {
    pub speed: f64,
    pub irreg: f64,
    pub phase: f64,
    pub drift: f64,
    pub layout_seed: u32,
}

impl StageState {
    /// 各 f64 のビット列まで比べるための写し。
    pub fn bits(&self) -> [u64; 5] {
        [
            self.speed.to_bits(),
            self.irreg.to_bits(),
            self.phase.to_bits(),
            self.drift.to_bits(),
            u64::from(self.layout_seed),
        ]
    }
}

/// 状態の積分器。
#[derive(Debug, Clone)]
pub struct Stage {
    ring: [u64; CAP],
    len: usize,
    next: usize,
    speed: f64,
    irreg: f64,
    phase: f64,
    /// 最後に処理した格子の点。
    grid_t: u64,
    grid_start: u64,
    drift_offset: f64,
    layout_seed: u32,
}

impl Stage {
    /// `seed` は描画の種、`t0` はその走行で手跡を出し始めた時刻（UTC の ms）。
    pub fn new(seed: u64, t0: u64) -> Self {
        let g0 = t0 / TICK_MS * TICK_MS;
        let a = splitmix64(seed);
        let b = splitmix64(a ^ 0xA5A5_A5A5_5A5A_5A5A);
        Self {
            ring: [0; CAP],
            len: 0,
            next: 0,
            speed: 0.0,
            irreg: 0.0,
            phase: 0.0,
            grid_t: g0,
            grid_start: g0,
            drift_offset: (a >> 11) as f64 / (1u64 << 53) as f64 * DRIFT_SPAN_S,
            layout_seed: (b >> 32) as u32,
        }
    }

    /// 打鍵の時刻（UTC の ms）を入れる。
    pub fn press(&mut self, t_ms: u64) {
        self.ring[self.next] = t_ms;
        self.next = (self.next + 1) % CAP;
        self.len = (self.len + 1).min(CAP);
    }

    fn times(&self) -> impl Iterator<Item = u64> + '_ {
        let start = (self.next + CAP - self.len) % CAP;
        (0..self.len).map(move |i| self.ring[(start + i) % CAP])
    }

    fn irregularity(&self, now: u64) -> Option<f64> {
        let (mut n, mut sum, mut sum_sq) = (0usize, 0.0f64, 0.0f64);
        let mut prev: Option<u64> = None;
        for t in self.times() {
            if let Some(p) = prev {
                if now.saturating_sub(t) <= IRREG_MS {
                    let g = t.saturating_sub(p);
                    if g < STOP_MS {
                        n += 1;
                        sum += g as f64;
                        sum_sq += (g * g) as f64;
                    }
                }
            }
            prev = Some(t);
        }
        if n < IRREG_MIN_GAPS {
            return None;
        }
        let mean = sum / n as f64;
        if mean <= 0.0 {
            return None;
        }
        let sd = (sum_sq / n as f64 - mean * mean).max(0.0).sqrt();
        Some(((sd / mean - 0.1) / 0.9).clamp(0.0, 1.0))
    }

    /// 1 刻み（250ms）。`now` は格子の点。
    fn tick(&mut self, now: u64) {
        let prev_speed = self.speed;
        let last_sec = self
            .times()
            .filter(|t| now.saturating_sub(*t) <= COUNT_MS)
            .count();
        let rate = last_sec.min(MAX_KEYS_PER_SEC) as f64 * SPEED_PER_KEY;
        let next = if last_sec > 0 {
            0.5 * self.speed + 0.5 * rate
        } else {
            self.speed * WIND_DECAY
        };
        self.speed = if next < MIN_SPEED { 0.0 } else { next };
        let irreg = match self.irregularity(now) {
            None => self.irreg * IRREG_DECAY,
            Some(ir) => 0.5 * self.irreg + 0.5 * ir,
        };
        self.irreg = if irreg < MIN_IRREG { 0.0 } else { irreg };
        // 試作の窓が 250ms かけて線形に寄せていた積分（台形）と同じ。
        self.phase += (prev_speed + self.speed) / 2.0 * (TICK_MS as f64 / 1000.0);
    }

    /// `t` 以下の格子の点まで刻みを進める（`t` が格子の手前なら何もしない）。
    pub fn advance_to(&mut self, t: u64) {
        while self.grid_t + TICK_MS <= t {
            self.grid_t += TICK_MS;
            let g = self.grid_t;
            self.tick(g);
        }
    }

    /// いまの状態。
    pub fn state(&self) -> StageState {
        StageState {
            speed: self.speed,
            irreg: self.irreg,
            phase: self.phase,
            drift: (self.grid_t - self.grid_start) as f64 / 1000.0 + self.drift_offset,
            layout_seed: self.layout_seed,
        }
    }
}

/// 打鍵の時刻の列（昇順）から、時刻 `t` の状態を出す。ライブも再生もこの順で `Stage` に流す。
pub fn replay(presses: &[u64], seed: u64, t0: u64, t: u64) -> StageState {
    let mut s = Stage::new(seed, t0);
    for &p in presses {
        if p > t {
            break;
        }
        s.advance_to(p);
        s.press(p);
    }
    s.advance_to(t);
    s.state()
}

#[cfg(test)]
mod tests {
    use super::*;

    /// 試作の `Wind::tick` と同じ式で `speed`・`irreg` を出す（式の写しの対照）。
    fn run(presses: &[u64], until: u64) -> Stage {
        let mut s = Stage::new(1, 0);
        for &p in presses {
            s.advance_to(p);
            s.press(p);
        }
        s.advance_to(until);
        s
    }

    #[test]
    fn no_presses_means_no_wind() {
        let s = run(&[], 10_000);
        let st = s.state();
        assert_eq!((st.speed, st.irreg, st.phase), (0.0, 0.0, 0.0));
    }

    #[test]
    fn steady_typing_matches_the_window_formula() {
        // 毎秒 10 打を 2 秒（100ms おき）。格子の点 2750 で: rate = 0.5、speed = 0.5 * 前 + 0.5 * 0.5。
        let presses: Vec<u64> = (0..20u64).map(|i| 1_000 + i * 100).collect();
        let mut s = Stage::new(1, 0);
        for &p in &presses {
            s.advance_to(p);
            s.press(p);
        }
        // 最後の打鍵は 2900。速さは 0.25 に向かう途中で、定常（0.5）を超えない。
        s.advance_to(2_950);
        let st = s.state();
        assert!(st.speed > 0.0 && st.speed <= 0.5, "{st:?}");
        assert_eq!(st.irreg, 0.0);
        assert!(st.phase > 0.0);
    }

    #[test]
    fn the_rate_is_capped_and_the_wind_decays_to_zero() {
        let presses: Vec<u64> = (0..40u64).map(|i| 1_000 + i * 25).collect();
        let s = run(&presses, 2_000);
        assert!(s.state().speed <= 14.0 * SPEED_PER_KEY);
        let mut s = s;
        let mut last = s.state().speed;
        let mut now = 3_000;
        s.advance_to(now);
        last = last.max(s.state().speed);
        for _ in 0..200 {
            now += TICK_MS;
            s.advance_to(now);
            let v = s.state().speed;
            assert!(v <= last, "{v} > {last}");
            last = v;
        }
        assert_eq!(last, 0.0);
    }

    #[test]
    fn irregular_gaps_raise_irregularity() {
        let mut t = 1_000u64;
        let mut presses = Vec::new();
        for g in [100u64, 600, 120, 900, 80, 700, 150, 1_200] {
            t += g;
            presses.push(t);
        }
        let s = run(&presses, t + 10);
        let st = s.state();
        assert!(st.irreg > 0.0 && st.irreg <= 1.0, "{st:?}");
    }

    #[test]
    fn the_ring_keeps_only_the_newest_presses() {
        let mut s = Stage::new(1, 0);
        for i in 0..(CAP as u64 + 10) {
            s.press(i);
        }
        assert_eq!(s.len, CAP);
        let times: Vec<u64> = s.times().collect();
        assert_eq!(times.first().copied(), Some(10));
        assert_eq!(times.last().copied(), Some(CAP as u64 + 9));
    }

    #[test]
    fn phase_is_the_trapezoid_integral_of_speed() {
        let mut s = Stage::new(1, 0);
        s.press(100);
        s.advance_to(250); // 0 -> 0.5*0 + 0.5*0.05 = 0.025
        let st = s.state();
        assert!((st.speed - 0.025).abs() < 1e-12);
        assert!((st.phase - 0.025 / 2.0 * 0.25).abs() < 1e-12);
    }

    /// 固定の種の小さな擬似乱数で、入力の列を作る。
    fn random_presses(seed: u64) -> Vec<u64> {
        let mut r = SplitMix64::new(seed);
        let n = r.below(120);
        let mut t = 1_000_000 + r.below(10_000);
        (0..n)
            .map(|_| {
                let span = if r.below(4) == 0 { 4_000 } else { 300 };
                t += 1 + r.below(span);
                t
            })
            .collect()
    }

    #[test]
    fn same_input_gives_bit_identical_state() {
        for i in 0..200u64 {
            let presses = random_presses(i);
            let t = presses.last().copied().unwrap_or(1_000_000) + 3_000;
            let a = replay(&presses, i, 999_000, t);
            let b = replay(&presses, i, 999_000, t);
            assert_eq!(a.bits(), b.bits(), "case {i}");
        }
    }

    #[test]
    fn changing_only_the_seed_changes_drift_or_layout() {
        for i in 0..200u64 {
            let presses = random_presses(i);
            let t = presses.last().copied().unwrap_or(1_000_000) + 3_000;
            let a = replay(&presses, i, 999_000, t);
            let b = replay(&presses, i + 1_000, 999_000, t);
            assert!(
                a.drift.to_bits() != b.drift.to_bits() || a.layout_seed != b.layout_seed,
                "case {i}"
            );
            // 種は風に影響しない
            assert_eq!(a.speed.to_bits(), b.speed.to_bits());
            assert_eq!(a.phase.to_bits(), b.phase.to_bits());
        }
    }

    #[test]
    fn the_number_of_advance_calls_does_not_change_the_state() {
        for i in 0..200u64 {
            let presses = random_presses(i);
            let t = presses.last().copied().unwrap_or(1_000_000) + 5_000;
            let once = replay(&presses, 7, 999_000, t);
            // 打鍵の間に、描画のつもりで余分に advance_to を呼ぶ（時刻は打鍵より前）
            let mut s = Stage::new(7, 999_000);
            let mut r = SplitMix64::new(i);
            let mut last = 999_000u64;
            for &p in &presses {
                let mid = last + r.below(p.saturating_sub(last) + 1);
                s.advance_to(mid.min(p));
                s.advance_to(p);
                s.press(p);
                last = p;
            }
            s.advance_to(t - 1_000);
            s.advance_to(t);
            assert_eq!(once.bits(), s.state().bits(), "case {i}");
        }
    }

    #[test]
    fn the_grid_is_aligned_to_absolute_time() {
        // t0 が 250 の倍数でなくても、格子は 250 の倍数に切り下げた点から。
        let mut s = Stage::new(3, 1_000_130);
        s.advance_to(1_000_249);
        assert_eq!(s.state().drift, Stage::new(3, 1_000_130).state().drift);
        s.advance_to(1_000_250);
        assert!(s.state().drift > Stage::new(3, 1_000_130).state().drift);
    }

    #[test]
    fn splitmix64_below_stays_in_range_and_covers_it() {
        let mut r = SplitMix64::new(9);
        let mut seen = [false; 5];
        for _ in 0..200 {
            let v = r.below(5) as usize;
            assert!(v < 5);
            seen[v] = true;
        }
        assert!(seen.iter().all(|s| *s));
        assert_eq!(r.below(0), 0);
    }
}
