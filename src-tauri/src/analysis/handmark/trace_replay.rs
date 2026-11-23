//! 手跡のポインタの再生（判断 2・ADR-051 D3）。
//!
//! `pointer_bin` の行（1 秒ごとの移動量のバケットと押下回数）から、描画の種で決めた起点を動く
//! **合成の一点の列**を作り、ライブと同じ [`TraceField`] に 16ms ごとに入れる。
//!
//! ## 限界（記録の限界であって実装の欠陥ではない）
//!
//! - 位置と向きは記録に無い。向きは描画の種と行の時刻から決めた疑似乱数で、**位置は再現できない**。
//!   再現するのは「いつ・どれだけ動いたか」の粗い量だけ。
//! - `pointer_bin` の押下は **どのボタンも数える**。ここでは全部を左の押下とみなすので、ライブ（左だけ）より
//!   押下が多めに出うる（判断 2 の限界）。ホイールは使わない。
//!
//! ## 規則（テストで縛る）
//!
//! - 行 `timestamp` はビンの終端で、区間は `[timestamp − 1000, timestamp)`。
//! - 区間が重なる・逆順の行は **前の行を優先**する。行は、直前に採った行の終端（最初は `t0`）より
//!   後ろの終端のものだけを採り、区間の始めを「直前の終端」に切り詰める（動く速さは変えず、動く長さだけ
//!   短くなる）。押下は元の区間で置き、切り詰めで外れたものは捨てる。`t0` 以前の行は使わない。
//! - 行の無い区間は止まっている。
//! - 距離は代表値（[`REP_PT`]）÷ 900（縦 900 point を箱の 1 とみなす）。向きは 16 方向の表から選ぶ。
//!   箱の縁では跳ね返る（三角波の折り返しで解析的に・決定的に）。
//! - 押下は区間の中の `(k + 0.5) × 1000 / n` に置き、その時刻を含む 16ms の刻み（`(T − 16, T]`）だけで
//!   `left_down` を立てる。同じ刻みに 2 つ落ちたら 1 つにまとめる。
//!
//! 時計・pow・三角関数を実行時に呼ばない（表はリテラル）。

use super::state::SplitMix64;
use super::trace::{Point, Step, TraceField, TraceState, BOX_H, BOX_W, STEP_MS};
use crate::analysis::pointer_bin::PointerBin;

/// `moved` のバケットの代表の移動量（point）。バケットの閾値（1..=8, 9..=32, 33..=128, 129..=512,
/// 513..=2048, 2049..=8192, 8193..）の幾何平均。
pub const REP_PT: [f64; 8] = [0.0, 2.83, 16.97, 65.0, 257.0, 1025.0, 4097.0, 11586.0];
/// 縦 900 point を箱の 1 とみなす。
const PT_PER_BOX: f64 = 900.0;
const BIN_MS: u64 = 1_000;
/// 16 方向の単位ベクトル（`(cos, sin)`・22.5 度おき）。
/// `cos 45°`。
const R: f64 = std::f64::consts::FRAC_1_SQRT_2;
const DIRS: [(f64, f64); 16] = [
    (1.0, 0.0),
    (0.9238795325112867, 0.3826834323650898),
    (R, R),
    (0.38268343236508984, 0.9238795325112867),
    (0.0, 1.0),
    (-0.3826834323650897, 0.9238795325112867),
    (-R, R),
    (-0.9238795325112867, 0.3826834323650899),
    (-1.0, 0.0),
    (-0.9238795325112868, -0.38268343236508967),
    (-R, -R),
    (-0.38268343236509034, -0.9238795325112865),
    (0.0, -1.0),
    (0.38268343236509, -0.9238795325112866),
    (R, -R),
    (0.9238795325112865, -0.3826834323650904),
];

/// 長さ `l` の箱での折り返し（`v` は展開した位置・結果は `[0, l]`）。
fn fold(v: f64, l: f64) -> f64 {
    let m = v.rem_euclid(2.0 * l);
    if m > l {
        2.0 * l - m
    } else {
        m
    }
}

/// 採った行 1 本ぶんの動き。
struct Seg {
    start: u64,
    end: u64,
    /// 区間の始めの位置。
    x0: f64,
    y0: f64,
    /// 1ms あたりの展開した移動量。
    dx: f64,
    dy: f64,
    /// 区間の終わりの位置。
    x1: f64,
    y1: f64,
}

/// 合成の一点の列（刻み 1, 2, … の順。刻み `k` の時刻は `g0 + 16 k`）。
pub struct Synth {
    segs: Vec<Seg>,
    /// 押下のある刻みの番号（昇順・重複なし）。
    presses: Vec<u64>,
    origin: (f64, f64),
    g0: u64,
    k: u64,
    k_end: u64,
    si: usize,
    pi: usize,
    cur: (f64, f64),
}

impl Synth {
    /// `bins` は時刻の昇順（逆順・重なりの扱いは module doc）。`t` までの刻みを出す。
    pub fn new(bins: &[PointerBin], seed: u64, t0: u64, t: u64) -> Self {
        let g0 = t0 / STEP_MS * STEP_MS;
        let mut rng = SplitMix64::new(seed);
        let ox = (rng.next_u64() >> 40) as f64 / (1u64 << 24) as f64 * f64::from(BOX_W);
        let oy = (rng.next_u64() >> 40) as f64 / (1u64 << 24) as f64 * f64::from(BOX_H);
        let (lw, lh) = (f64::from(BOX_W), f64::from(BOX_H));

        let mut segs: Vec<Seg> = Vec::new();
        let mut presses: Vec<u64> = Vec::new();
        let mut prev_end = t0;
        let mut pos = (ox, oy);
        for b in bins {
            let ts = b.timestamp;
            if ts <= prev_end {
                continue;
            }
            let orig_start = ts.saturating_sub(BIN_MS);
            if orig_start > t {
                continue;
            }
            let start = orig_start.max(prev_end);
            let (ux, uy) = DIRS[SplitMix64::new(seed ^ ts).below(16) as usize];
            let rep = REP_PT[usize::from(b.moved).min(REP_PT.len() - 1)] / PT_PER_BOX;
            let (dx, dy) = (ux * rep / BIN_MS as f64, uy * rep / BIN_MS as f64);
            let span = (ts - start) as f64;
            let x1 = fold(pos.0 + dx * span, lw);
            let y1 = fold(pos.1 + dy * span, lh);
            segs.push(Seg {
                start,
                end: ts,
                x0: pos.0,
                y0: pos.1,
                dx,
                dy,
                x1,
                y1,
            });
            pos = (x1, y1);
            prev_end = ts;

            let n = i64::from(b.buttons.min(15));
            for k in 0..n {
                // 時刻 = orig_start + (2k+1)*500/n。分母 n の有理数のまま比べる。
                let off = (2 * k + 1) * 500;
                if n * (orig_start as i64 - start as i64) + off < 0 {
                    continue; // 切り詰めで外れた
                }
                let num = n * (orig_start as i64 - g0 as i64) + off;
                let den = 16 * n;
                let tick = (num + den - 1).div_euclid(den);
                if tick >= 1 {
                    presses.push(tick as u64);
                }
            }
        }
        presses.sort_unstable();
        presses.dedup();
        Self {
            segs,
            presses,
            origin: (ox, oy),
            g0,
            k: 0,
            k_end: t.saturating_sub(g0) / STEP_MS,
            si: 0,
            pi: 0,
            cur: (ox, oy),
        }
    }

    /// 描画の種で決めた起点（テスト用）。
    pub fn origin(&self) -> (f64, f64) {
        self.origin
    }
}

impl Iterator for Synth {
    type Item = Point;

    fn next(&mut self) -> Option<Point> {
        if self.k >= self.k_end {
            return None;
        }
        self.k += 1;
        let t = self.g0 + STEP_MS * self.k;
        while self.si < self.segs.len() && self.segs[self.si].end <= t {
            self.cur = (self.segs[self.si].x1, self.segs[self.si].y1);
            self.si += 1;
        }
        let (x, y) = match self.segs.get(self.si) {
            Some(s) if s.start <= t => {
                let e = (t - s.start) as f64;
                (
                    fold(s.x0 + s.dx * e, f64::from(BOX_W)),
                    fold(s.y0 + s.dy * e, f64::from(BOX_H)),
                )
            }
            _ => self.cur,
        };
        while self.pi < self.presses.len() && self.presses[self.pi] < self.k {
            self.pi += 1;
        }
        let left_down = self.presses.get(self.pi) == Some(&self.k);
        Some(Point {
            x: x as f32,
            y: y as f32,
            left_down,
        })
    }
}

/// 合成の一点の列（刻み 1, 2, …。刻み `k` の時刻は `t0` を 16 に丸めた点 + 16 k）。
pub fn synth_points(bins: &[PointerBin], seed: u64, t0: u64, t: u64) -> Vec<Point> {
    Synth::new(bins, seed, t0, t).collect()
}

/// `pointer_bin` の行の列（昇順）から、時刻 `t` のポインタの場を出す。ライブと同じ [`TraceField`] を通す。
pub fn replay_trace(bins: &[PointerBin], seed: u64, t0: u64, t: u64) -> TraceState {
    let mut field = TraceField::new(t0);
    for p in Synth::new(bins, seed, t0, t) {
        field.step(Step {
            sample: Some(p),
            cursor_on: true,
            click_on: true,
            lost: false,
        });
    }
    field.state()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn bin(timestamp: u64, moved: u8, buttons: u8) -> PointerBin {
        PointerBin {
            timestamp,
            moved,
            buttons,
            wheel: 0,
        }
    }

    fn bits(ps: &[Point]) -> Vec<(u32, u32, bool)> {
        ps.iter()
            .map(|p| (p.x.to_bits(), p.y.to_bits(), p.left_down))
            .collect()
    }

    fn sample_bins() -> Vec<PointerBin> {
        vec![
            bin(2_000, 4, 1),
            bin(3_000, 5, 0),
            bin(4_000, 6, 2),
            bin(7_000, 3, 0),
            bin(8_000, 7, 3),
        ]
    }

    #[test]
    fn same_input_gives_bit_identical_state() {
        let b = sample_bins();
        let a = replay_trace(&b, 7, 1_000, 9_000);
        let c = replay_trace(&b, 7, 1_000, 9_000);
        assert!(a.bits() == c.bits());
        assert!(!a.is_zero());
    }

    #[test]
    fn a_different_seed_changes_the_result() {
        let b = sample_bins();
        let a = replay_trace(&b, 7, 1_000, 9_000);
        let c = replay_trace(&b, 8, 1_000, 9_000);
        assert!(a.bits() != c.bits());
        assert!(
            bits(&synth_points(&b, 7, 1_000, 9_000)) != bits(&synth_points(&b, 8, 1_000, 9_000))
        );
    }

    #[test]
    fn replay_trace_is_the_field_fed_with_the_synth_points() {
        let b = sample_bins();
        let mut f = TraceField::new(1_000);
        for p in synth_points(&b, 3, 1_000, 9_000) {
            f.step(Step {
                sample: Some(p),
                cursor_on: true,
                click_on: true,
                lost: false,
            });
        }
        assert!(f.state().bits() == replay_trace(&b, 3, 1_000, 9_000).bits());
    }

    #[test]
    fn no_rows_means_the_point_does_not_move_and_the_field_is_zero() {
        let pts = synth_points(&[], 5, 1_000, 6_000);
        assert!(pts.len() == (6_000 / 16 - 1_000 / 16) as usize);
        assert!(pts
            .iter()
            .all(|p| p.x == pts[0].x && p.y == pts[0].y && !p.left_down));
        assert!(replay_trace(&[], 5, 1_000, 6_000).is_zero());
    }

    #[test]
    fn a_gap_without_rows_stands_still() {
        // 2000 の行の後、7000 の行が始まる 6000 まで止まる。
        let b = vec![bin(2_000, 5, 0), bin(7_000, 5, 0)];
        let pts = synth_points(&b, 9, 0, 8_000);
        let at = |t: u64| pts[(t / 16 - 1) as usize];
        let end_of_first = at(2_000);
        for t in (2_016..=6_000).step_by(16) {
            assert!(at(t).x == end_of_first.x && at(t).y == end_of_first.y);
        }
        assert!(at(6_992).x != end_of_first.x || at(6_992).y != end_of_first.y);
    }

    #[test]
    fn rows_before_t0_do_not_move_the_point() {
        let b = vec![bin(500, 7, 5), bin(900, 7, 5)];
        let pts = synth_points(&b, 2, 1_000, 3_000);
        assert!(pts.iter().all(|p| !p.left_down));
        assert!(pts.iter().all(|p| p.x == pts[0].x && p.y == pts[0].y));
    }

    #[test]
    fn buttons_are_evenly_placed_and_never_share_a_tick() {
        for n in 1..=15u8 {
            let b = vec![bin(11_000, 0, n)];
            let pts = synth_points(&b, 1, 0, 12_000);
            let ticks: Vec<usize> = pts
                .iter()
                .enumerate()
                .filter(|(_, p)| p.left_down)
                .map(|(i, _)| i + 1)
                .collect();
            assert!(ticks.len() == usize::from(n), "n={n} got {}", ticks.len());
            let step = 1_000.0 / f64::from(n);
            for (k, tick) in ticks.iter().enumerate() {
                let want = 10_000.0 + (k as f64 + 0.5) * step;
                let t = *tick as f64 * 16.0;
                assert!(
                    t >= want && t - want < 16.0,
                    "n={n} k={k} t={t} want={want}"
                );
            }
            for w in ticks.windows(2) {
                assert!(w[1] > w[0] + 1, "adjacent ticks for n={n}");
            }
        }
    }

    #[test]
    fn presses_in_the_same_tick_merge() {
        // 15 回でも刻みの数は押下の回数以下で、重複が無い（dedup）。
        let b = vec![bin(1_000, 0, 15), bin(2_000, 0, 15)];
        let pts = synth_points(&b, 1, 0, 3_000);
        assert!(pts.iter().filter(|p| p.left_down).count() == 30);
    }

    #[test]
    fn the_point_never_leaves_the_box() {
        let b: Vec<PointerBin> = (1..=60).map(|i| bin(i * 1_000, 7, 0)).collect();
        for seed in 0..8 {
            for p in synth_points(&b, seed, 0, 61_000) {
                assert!(p.x >= 0.0 && p.x <= BOX_W, "x={}", p.x);
                assert!(p.y >= 0.0 && p.y <= BOX_H, "y={}", p.y);
            }
        }
    }

    #[test]
    fn overlapping_rows_keep_the_earlier_and_reverse_rows_are_dropped() {
        let first = vec![bin(2_000, 5, 1)];
        let base = synth_points(&first, 4, 0, 4_000);
        // 逆順の行（終端が前の行以前）は捨てる。
        let reversed = vec![bin(2_000, 5, 1), bin(1_500, 7, 5), bin(2_000, 7, 5)];
        assert!(bits(&synth_points(&reversed, 4, 0, 4_000)) == bits(&base));
        // 重なる行は、前の行の終端から先だけを使う（2000 までは前の行だけで決まる）。
        let overlap = vec![bin(2_000, 5, 1), bin(2_500, 5, 0)];
        let o = synth_points(&overlap, 4, 0, 4_000);
        for k in 0..(2_000 / 16) {
            assert!(bits(&o[k..=k]) == bits(&base[k..=k]));
        }
        // 2000 から 2500 までは動き、2500 の後は止まる。
        let at = |t: u64| o[(t / 16 - 1) as usize];
        assert!(at(2_400).x != at(2_000).x || at(2_400).y != at(2_000).y);
        assert!(at(2_512).x == at(3_984).x && at(2_512).y == at(3_984).y);
    }

    #[test]
    fn table_constants() {
        for (x, y) in DIRS {
            assert!((x * x + y * y - 1.0).abs() < 1e-12);
        }
        assert!(REP_PT.len() == 8 && REP_PT[0] == 0.0);
        assert!(REP_PT.windows(2).all(|w| w[0] < w[1]));
    }
}
