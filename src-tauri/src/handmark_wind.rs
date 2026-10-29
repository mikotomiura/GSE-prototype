//! 手跡の風（背景の層と下の縁の帯が共有する・spike・本線に入れない）。
//!
//! `.steering/20261030-handmark-edge-strip-impl/` の判断 1: 風は 1 か所（Rust）で 250ms ごとに計算し、
//! 背景と帯の両方の窓へ配る。式と定数は `src/components/HandmarkStage.tsx` が持っていた `tick()` と
//! `irregularity()` をそのまま移した（窓の側は受け取った目標へ 250ms かけて寄せる）。
//!
//! 材料は打鍵の時刻だけ（キーの種類は持たない）。OS の API を呼ばない純粋な計算。
//! 打鍵の時刻は固定長の輪に入れ、古いものから上書きする（不規則さは直近 10 秒しか見ないので、
//! 輪が溢れるのは 10 秒に `CAP` 打を超える速さのときだけ）。

/// 風の目標を決める間隔（`WIND_TICK_MS`）。
pub const TICK_MS: u64 = 250;
/// 打鍵の数を数える窓（直近 1 秒）。
const COUNT_MS: u64 = 1_000;
/// 打鍵の間合いをこれ以上空いたら途切れとみなす。
const STOP_MS: u64 = 2_000;
const SPEED_PER_KEY: f64 = 0.05;
/// 1 秒の打鍵の数の頭打ち。
const MAX_KEYS_PER_SEC: usize = 14;
/// 打鍵が無い 0.25 秒ごとの減り。
const WIND_DECAY: f64 = 0.88;
const MIN_SPEED: f64 = 0.002;
const IRREG_MS: u64 = 10_000;
const IRREG_MIN_GAPS: usize = 4;
/// 打鍵の間合いが足りない間の不規則さの減り（0.25 秒ごと）。
const IRREG_DECAY: f64 = 0.96;
const MIN_IRREG: f64 = 0.002;
/// 打鍵の時刻を持つ輪の大きさ。
const CAP: usize = 256;

/// 窓へ配る風の目標。
#[derive(Clone, Copy, Debug, PartialEq, serde::Serialize)]
pub struct WindTarget {
    /// 風の速さの目標（0 以上）。
    pub speed: f64,
    /// 打鍵の間合いの不規則さの目標（0〜1）。
    pub irreg: f64,
}

/// 風の状態。打鍵の時刻（ミリ秒・単調）を `press` で入れ、`tick` で目標を出す。
pub struct Wind {
    ring: [u64; CAP],
    /// 入っている数（`CAP` まで）。
    len: usize,
    /// 次に書く位置。
    next: usize,
    speed: f64,
    irreg: f64,
}

impl Default for Wind {
    fn default() -> Self {
        Self::new()
    }
}

impl Wind {
    pub const fn new() -> Self {
        Self {
            ring: [0; CAP],
            len: 0,
            next: 0,
            speed: 0.0,
            irreg: 0.0,
        }
    }

    /// 打鍵の時刻を入れる。古いものから上書きする。
    pub fn press(&mut self, t_ms: u64) {
        self.ring[self.next] = t_ms;
        self.next = (self.next + 1) % CAP;
        self.len = (self.len + 1).min(CAP);
    }

    /// 古い順の打鍵の時刻。
    fn times(&self) -> impl Iterator<Item = u64> + '_ {
        let start = (self.next + CAP - self.len) % CAP;
        (0..self.len).map(move |i| self.ring[(start + i) % CAP])
    }

    /// 直近 10 秒の、途切れでない間合いの変動係数から出す不規則さ。間合いが足りなければ None。
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

    /// 250ms ごとに呼び、次の目標を出す。
    pub fn tick(&mut self, now: u64) -> WindTarget {
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
        WindTarget {
            speed: self.speed,
            irreg: self.irreg,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn no_presses_means_no_wind() {
        let mut w = Wind::new();
        assert_eq!(
            w.tick(10_000),
            WindTarget {
                speed: 0.0,
                irreg: 0.0
            }
        );
    }

    #[test]
    fn steady_typing_matches_the_window_formula() {
        // 毎秒 10 打を 2 秒（100ms おき）。TS の式: rate = 10 * 0.05 = 0.5、speed = 0.5 * 0 + 0.5 * 0.5。
        let mut w = Wind::new();
        for i in 0..20u64 {
            w.press(1_000 + i * 100);
        }
        let t = w.tick(2_950);
        assert!((t.speed - 0.25).abs() < 1e-12, "{t:?}");
        // 間合いが全部同じなので変動係数 0 → (0 - 0.1) / 0.9 を 0 に切る → 0.5 * 0 + 0.5 * 0 = 0。
        assert_eq!(t.irreg, 0.0);
    }

    #[test]
    fn the_rate_is_capped_and_the_wind_decays_to_zero() {
        let mut w = Wind::new();
        for i in 0..40u64 {
            w.press(1_000 + i * 25); // 毎秒 40 打（頭打ち 14 を超える）
        }
        let t = w.tick(2_000);
        assert!(
            (t.speed - 0.5 * 14.0 * SPEED_PER_KEY).abs() < 1e-12,
            "{t:?}"
        );
        // 最後の打鍵（1975ms）から 1 秒を過ぎるまでは、まだ打鍵が数えられて風は上がりうる。
        // それより後は打鍵が無いので、0.25 秒ごとに減って 0 になる。
        let mut now = 3_000;
        let mut last = w.tick(now).speed;
        for _ in 0..200 {
            now += TICK_MS;
            let s = w.tick(now).speed;
            assert!(s <= last, "{s} > {last}");
            last = s;
        }
        assert_eq!(last, 0.0);
    }

    #[test]
    fn irregular_gaps_raise_irregularity() {
        let mut w = Wind::new();
        let mut t = 1_000u64;
        for g in [100u64, 600, 120, 900, 80, 700, 150, 1_200] {
            t += g;
            w.press(t);
        }
        let out = w.tick(t + 10);
        assert!(out.irreg > 0.0, "{out:?}");
        assert!(out.irreg <= 1.0);
    }

    #[test]
    fn the_ring_keeps_only_the_newest_presses() {
        let mut w = Wind::new();
        for i in 0..(CAP as u64 + 10) {
            w.press(i);
        }
        assert_eq!(w.len, CAP);
        let times: Vec<u64> = w.times().collect();
        assert_eq!(times.first().copied(), Some(10));
        assert_eq!(times.last().copied(), Some(CAP as u64 + 9));
    }
}
