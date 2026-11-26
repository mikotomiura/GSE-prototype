//! 手跡の状態の純関数（ADR-051 D5 のライブの契約と再生の契約）。
//!
//! 入力は「打鍵の時刻の列」「種」「起点 `t0`」「時刻 `t`」だけで、キーの種類を受ける口が型に無い。
//! 式と定数は試作 `handmark_wind.rs`（`Wind::tick`）をそのまま移した。ライブも再生も同じ [`Stage`] を通す。
//!
//! ## 呼び出しの契約
//!
//! 打鍵 `p` は `press(p)` で入れる（時刻順。中で先に `advance_to(p)` を呼ぶ）。`advance_to` は 250ms の格子の点
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
#[derive(Debug, Clone, Copy, PartialEq, serde::Serialize)]
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
    /// `is_idle` が初めて真になった格子の刻み（ADR-056 D1）。止まっていなければ `None`。
    /// 止まりの層（`stopped.rs`）の立ち上がりにだけ使う。風・位相・漂いの計算には効かない。
    idle_since: Option<u64>,
    #[cfg(test)]
    ticks_run: u64,
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
            // 打鍵の列が空で風も無いので、作った時点で止まっている（返すかは止まりの層の門が決める）。
            idle_since: Some(g0),
            #[cfg(test)]
            ticks_run: 0,
        }
    }

    /// 打鍵の時刻（UTC の ms）を入れる。先に `advance_to(t_ms)` を呼ぶので、呼び出し側が進め忘れても
    /// （未来の時刻が入っても）再生と食い違わない。
    pub fn press(&mut self, t_ms: u64) {
        self.advance_to(t_ms);
        self.push(t_ms);
    }

    fn push(&mut self, t_ms: u64) {
        self.ring[self.next] = t_ms;
        self.next = (self.next + 1) % CAP;
        self.len = (self.len + 1).min(CAP);
        self.note_idle();
    }

    /// 格子の時刻か打鍵の列が変わった後に呼ぶ。止まりが始まった刻みを 1 つだけ覚え、止まっていなければ忘れる。
    fn note_idle(&mut self) {
        if !self.is_idle() {
            self.idle_since = None;
        } else if self.idle_since.is_none() {
            self.idle_since = Some(self.grid_t);
        }
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
        #[cfg(test)]
        {
            self.ticks_run += 1;
        }
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
    ///
    /// 止まっている区間（速さも不規則さも 0 で、最後の打鍵から `IRREG_MS` より長い）は、刻みで状態が
    /// 変わらない（`drift` は格子から計算する）ので、まとめて進める。
    pub fn advance_to(&mut self, t: u64) {
        while let Some(g) = self.grid_t.checked_add(TICK_MS).filter(|g| *g <= t) {
            if self.is_idle() {
                // 止まっている間は状態が変わらず、`idle_since` も既に決まっている（`note_idle` を刻みごとに呼ぶ）。
                self.grid_t += (t - self.grid_t) / TICK_MS * TICK_MS;
                return;
            }
            self.grid_t = g;
            self.tick(g);
            self.note_idle();
        }
    }

    /// `is_idle` が初めて真になった格子の刻み（止まっていなければ `None`・ADR-056 D1）。
    pub fn idle_since(&self) -> Option<u64> {
        self.idle_since
    }

    /// 最後に処理した格子の点。
    pub fn grid_t(&self) -> u64 {
        self.grid_t
    }

    /// 以後の刻みが状態を変えない（打鍵が無いまま）。
    fn is_idle(&self) -> bool {
        self.speed == 0.0
            && self.irreg == 0.0
            && self.times().last().is_none_or(|last| {
                self.grid_t.saturating_sub(last) > IRREG_MS && last <= self.grid_t
            })
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
///
/// 入力の契約: ライブは `t0`（手跡を出し始めた時刻）より前の打鍵を受けないので、`p < t0` の打鍵は
/// 入れない（記録に開始前の打鍵が混ざっていても、ライブと同じ状態になる）。
pub fn replay(presses: &[u64], seed: u64, t0: u64, t: u64) -> StageState {
    let mut s = Stage::new(seed, t0);
    for &p in presses {
        if p > t {
            break;
        }
        if p < t0 {
            continue;
        }
        s.advance_to(p);
        s.press(p);
    }
    s.advance_to(t);
    s.state()
}

/// ライブが状態を進める遅れ（ms）。ライブは「今 − この値」までしか進めない（遅れて届く打鍵を
/// 時刻の順に入れるため・判断 7-3）。
pub const LIVE_LAG_MS: u64 = 500;

/// ライブの規則（時刻 `now` には「`now − LIVE_LAG_MS` まで」の状態を出す）を、記録の打鍵の時刻から再現する。
/// 500 ms 以内の遅れで届いた打鍵なら、ライブの `tick` の列と `to_bits` で一致する。
pub fn replay_live(presses: &[u64], seed: u64, t0: u64, now: u64) -> StageState {
    replay(presses, seed, t0, now.saturating_sub(LIVE_LAG_MS))
}

#[cfg(test)]
mod tests {
    use super::*;

    /// 試作 `handmark_wind.rs` のテストと同じく、打鍵を輪に直接入れて 1 刻みだけ `tick` する。
    fn raw(presses: &[u64]) -> Stage {
        let mut s = Stage::new(1, 0);
        for &p in presses {
            s.push(p);
        }
        s
    }

    #[test]
    fn no_presses_means_no_wind() {
        let mut s = raw(&[]);
        s.tick(10_000);
        let st = s.state();
        assert_eq!((st.speed, st.irreg), (0.0, 0.0));
    }

    #[test]
    fn steady_typing_matches_the_window_formula() {
        // 毎秒 10 打を 2 秒（100ms おき）。rate = 10 * 0.05 = 0.5、speed = 0.5 * 0 + 0.5 * 0.5。
        let presses: Vec<u64> = (0..20u64).map(|i| 1_000 + i * 100).collect();
        let mut s = raw(&presses);
        s.tick(2_950);
        let st = s.state();
        assert!((st.speed - 0.25).abs() < 1e-12, "{st:?}");
        assert_eq!(st.irreg, 0.0);
    }

    #[test]
    fn the_rate_is_capped_and_the_wind_decays_to_zero() {
        let presses: Vec<u64> = (0..40u64).map(|i| 1_000 + i * 25).collect();
        let mut s = raw(&presses);
        s.tick(2_000);
        assert!(
            (s.state().speed - 0.5 * 14.0 * SPEED_PER_KEY).abs() < 1e-12,
            "{:?}",
            s.state()
        );
        // 最後の打鍵（1975ms）から 1 秒を過ぎると 0.25 秒ごとに減って 0 になる。
        let mut now = 3_000;
        s.tick(now);
        let mut last = s.state().speed;
        for _ in 0..200 {
            now += TICK_MS;
            s.tick(now);
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
        let mut s = raw(&presses);
        s.tick(t + 10);
        let st = s.state();
        assert!(st.irreg > 0.0 && st.irreg <= 1.0, "{st:?}");
    }

    #[test]
    fn the_ring_keeps_only_the_newest_presses() {
        let mut s = Stage::new(1, 0);
        for i in 0..(CAP as u64 + 10) {
            s.push(i);
        }
        assert_eq!(s.len, CAP);
        let times: Vec<u64> = s.times().collect();
        assert_eq!(times.first().copied(), Some(10));
        assert_eq!(times.last().copied(), Some(CAP as u64 + 9));
    }

    /// `press` が先に進めるので、`advance_to` を呼ばずに（未来の時刻を直接）入れても再生と一致する。
    #[test]
    fn press_alone_matches_replay_even_with_future_times() {
        for i in 0..200u64 {
            let presses = random_presses(i);
            let t = presses.last().copied().unwrap_or(1_000_000) + 3_000;
            let mut s = Stage::new(9, 999_000);
            for &p in &presses {
                s.press(p); // advance_to を呼ばない
            }
            s.advance_to(t);
            assert_eq!(
                s.state().bits(),
                replay(&presses, 9, 999_000, t).bits(),
                "case {i}"
            );
        }
    }

    #[test]
    fn replay_ignores_presses_before_t0() {
        let a = replay(&[900], 5, 1_000, 1_250);
        let b = replay(&[], 5, 1_000, 1_250);
        assert_eq!(a.bits(), b.bits());
        // t0 ちょうどは入る
        let c = replay(&[1_000], 5, 1_000, 1_250);
        assert_ne!(c.bits(), b.bits());
    }

    /// 素朴に 1 刻みずつ回す参照の実装。
    fn naive_advance(s: &mut Stage, t: u64) {
        while let Some(g) = s.grid_t.checked_add(TICK_MS).filter(|g| *g <= t) {
            s.grid_t = g;
            s.tick(g);
        }
    }

    #[test]
    fn fast_forward_matches_the_naive_step_loop_including_long_gaps() {
        for i in 0..200u64 {
            let mut r = SplitMix64::new(i + 77);
            let mut fast = Stage::new(3, 500_000);
            let mut slow = Stage::new(3, 500_000);
            let mut t = 500_000u64;
            for _ in 0..r.below(40) {
                // ときどき長い空白（数分〜数時間）
                t += 1 + match r.below(4) {
                    0 => 600_000 + r.below(3_600_000),
                    1 => 9_000 + r.below(30_000),
                    _ => r.below(400),
                };
                fast.advance_to(t);
                naive_advance(&mut slow, t);
                fast.push(t);
                slow.push(t);
                assert_eq!(fast.state().bits(), slow.state().bits(), "case {i} t {t}");
            }
            let end = t + 7_200_000;
            fast.advance_to(end);
            naive_advance(&mut slow, end);
            assert_eq!(fast.state().bits(), slow.state().bits(), "case {i} end");
        }
    }

    /// 素朴な進め方で、刻みごとに止まりの始まりを数え直す参照（`note_idle` を毎刻み呼ぶ）。
    fn naive_advance_with_idle(s: &mut Stage, t: u64) {
        while let Some(g) = s.grid_t.checked_add(TICK_MS).filter(|g| *g <= t) {
            s.grid_t = g;
            s.tick(g);
            s.note_idle();
        }
    }

    /// 早送りでも、止まりの始まりの刻みは素朴な 1 刻みずつと同じ（ADR-056・設計案 §4.4 の論理の時刻）。
    #[test]
    fn idle_since_matches_the_naive_step_loop_including_long_gaps() {
        for i in 0..200u64 {
            let mut r = SplitMix64::new(i + 991);
            let mut fast = Stage::new(3, 500_000);
            let mut slow = Stage::new(3, 500_000);
            let mut t = 500_000u64;
            for _ in 0..r.below(40) {
                let prev = t;
                t += 1 + match r.below(4) {
                    0 => 600_000 + r.below(3_600_000),
                    1 => 9_000 + r.below(60_000),
                    _ => r.below(400),
                };
                // 打鍵の前に、描画のつもりの途中の時刻（前の打鍵と次の打鍵の間）でも比べる
                let mid = prev + r.below(t - prev);
                fast.advance_to(mid);
                naive_advance_with_idle(&mut slow, mid);
                assert_eq!(fast.idle_since(), slow.idle_since(), "case {i} mid {mid}");
                fast.advance_to(t);
                naive_advance_with_idle(&mut slow, t);
                assert_eq!(fast.idle_since(), slow.idle_since(), "case {i} t {t}");
                fast.push(t);
                slow.push(t);
                assert_eq!(fast.idle_since(), None, "case {i}");
            }
            let end = t + 7_200_000;
            fast.advance_to(end);
            naive_advance_with_idle(&mut slow, end);
            assert_eq!(fast.idle_since(), slow.idle_since(), "case {i} end");
            assert!(fast.idle_since().is_some(), "case {i}");
        }
    }

    /// 止まりの始まりは、止まった区間の中で動かない（長さが伸びても同じ刻み）。
    #[test]
    fn idle_since_stays_put_while_stopped() {
        let mut s = Stage::new(1, 1_000_000);
        for k in 0..30u64 {
            s.press(1_000_000 + 1_000 + k * 120);
        }
        s.advance_to(1_000_000 + 120_000);
        let start = s.idle_since().expect("stopped after two minutes");
        // 最後の打鍵は 1_004_480。止まりの始まりは、そこから `IRREG_MS` を過ぎた後の格子の点
        assert!(start > 1_000_000 + 4_480 + IRREG_MS, "{start}");
        assert_eq!(start % TICK_MS, 0);
        for later in [3_600_000u64, 86_400_000, 30 * 86_400_000] {
            s.advance_to(1_000_000 + later);
            assert_eq!(s.idle_since(), Some(start));
        }
        // 打鍵で忘れ、次の止まりは新しい刻みから
        s.press(1_000_000 + 30 * 86_400_000 + 7);
        assert_eq!(s.idle_since(), None);
    }

    #[test]
    fn a_year_of_silence_takes_few_iterations() {
        let t0 = 1_000_000u64;
        let mut s = Stage::new(1, t0);
        s.press(t0 + 1_000);
        s.advance_to(t0 + 365 * 86_400_000);
        assert!(s.ticks_run < 1_000, "{}", s.ticks_run);
        assert_eq!(s.state().speed, 0.0);
    }

    #[test]
    fn the_grid_does_not_overflow_near_u64_max() {
        let mut s = Stage::new(1, u64::MAX);
        s.advance_to(u64::MAX);
        s.press(u64::MAX);
        assert!(s.state().drift.is_finite());
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
