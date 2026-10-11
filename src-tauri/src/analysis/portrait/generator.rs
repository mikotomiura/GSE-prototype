//! 肖像の生成器（`raw` / `lattice` × drift `none` / `diffuse`・OS API 非依存）。
//!
//! EH1 第 5 回の試作 `portrait.py` の `Generator`（`_draw`・`_draw_lattice`・中立の規則・drift）の移植。
//! 値は同じ `config.json` の `generator` に揃える。
//!
//! ⚠️ 材料は F 系列（f1・f3・f4・f6）の 1 秒ごとの値と、その秒に打鍵があったかだけ（R-P1・E1-1）。
//! 推定（`p_stuck`・`level`・X / Y）と招待を受け取る口は**型として存在しない**（[`Second`] の欄がそれだけ）。

use super::canvas::{hsv, Canvas, H, W};
use crate::eh3::{Drift, Grammar};

/// 1 秒ぶんの材料。F 系列の値が無い秒は NaN。
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Second {
    pub f1: f64,
    pub f3: f64,
    pub f4: f64,
    pub f6: f64,
    /// その秒に打鍵（押下）が 1 回以上あった。
    pub active: bool,
}

/// 中立の規則: 累積の打鍵の秒がこれに届くまでは地のまま（EH1 `neutral_active_s`）。
pub const NEUTRAL_ACTIVE_S: u32 = 60;
const ACTIVE_PER_MARK: u32 = 10;
const ALPHA: f32 = 0.35;
const DIFFUSE_SIGMA: f32 = 0.6;
const DIFFUSE_MIX: f32 = 0.1;
/// 水準の正規化の範囲（EH1 `raw_ranges`）: f1・f3・f4・f6。
const RAW_RANGES: [(f64, f64); 4] = [(50.0, 600.0), (0.0, 0.5), (0.0, 20.0), (0.0, 1.0)];
const LAT_BOUNDS: [f64; 2] = [1.0 / 3.0, 2.0 / 3.0];
const LAT_DELTA: f64 = 0.05;
const LAT_CELL_PX: usize = 20;
const LAT_OFFSET_PX: f32 = 5.0;
const LAT_HUE: [f32; 3] = [0.08, 0.45, 0.75];
const LAT_LIGHT: [f32; 3] = [0.35, 0.55, 0.75];
const LAT_SIGMA: [f32; 3] = [3.0, 5.0, 7.0];
const TAU: f32 = std::f32::consts::TAU;

/// 小さな決定的な乱数（splitmix64）。初期位置と向きだけに使う（材料には使わない）。
#[derive(Debug, Clone)]
pub struct SplitMix(u64);

impl SplitMix {
    pub fn new(seed: u64) -> Self {
        Self(seed)
    }

    pub fn next_u64(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }

    /// [0, 1)
    pub fn unit(&mut self) -> f32 {
        (self.next_u64() >> 40) as f32 / (1u64 << 24) as f32
    }
}

/// 1 回のセッションの肖像を描き続ける生成器。セッションの始まりで作り直す（地から始める）。
#[derive(Debug, Clone)]
pub struct Generator {
    grammar: Grammar,
    drift: Drift,
    base: Canvas,
    total_active: u32,
    neutral: bool,
    buffer: Vec<Vec<Second>>,
    x: f32,
    y: f32,
    theta: f32,
    phase: f32,
    lat_cls: [Option<usize>; 4],
    lat_k: usize,
    cells: Vec<(f32, f32)>,
}

/// Python の `round`（偶数への丸め）。
fn round_half_even(v: f64) -> i64 {
    let r = v.round();
    if (v - v.trunc()).abs() == 0.5 {
        let t = v.trunc() as i64;
        if t % 2 == 0 {
            t
        } else {
            t + v.signum() as i64
        }
    } else {
        r as i64
    }
}

/// `lattice_cells`: 中心から外へ渦巻く升の中心（距離（升で丸め）→角度の順）。
fn lattice_cells() -> Vec<(f32, f32)> {
    let nx = W / LAT_CELL_PX;
    let ny = H / LAT_CELL_PX;
    let cx = (nx as f64 - 1.0) / 2.0;
    let cy = (ny as f64 - 1.0) / 2.0;
    let mut cells: Vec<(i64, f64, f32, f32)> = Vec::with_capacity(nx * ny);
    for j in 0..ny {
        for i in 0..nx {
            let d = (i as f64 - cx).hypot(j as f64 - cy);
            let a = (j as f64 - cy)
                .atan2(i as f64 - cx)
                .rem_euclid(std::f64::consts::TAU);
            cells.push((
                round_half_even(d),
                a,
                ((i as f32) + 0.5) * LAT_CELL_PX as f32,
                ((j as f32) + 0.5) * LAT_CELL_PX as f32,
            ));
        }
    }
    cells.sort_by(|p, q| p.0.cmp(&q.0).then(p.1.total_cmp(&q.1)));
    cells.into_iter().map(|c| (c.2, c.3)).collect()
}

fn lattice_class(v: f64, prev: Option<usize>) -> usize {
    match prev {
        None => LAT_BOUNDS.iter().filter(|b| v >= **b).count(),
        Some(mut c) => {
            while c < 2 && v >= LAT_BOUNDS[c] + LAT_DELTA {
                c += 1;
            }
            while c > 0 && v < LAT_BOUNDS[c - 1] - LAT_DELTA {
                c -= 1;
            }
            c
        }
    }
}

impl Generator {
    pub fn new(grammar: Grammar, drift: Drift, seed: u64) -> Self {
        let mut r = SplitMix::new(seed);
        let x = (0.3 + 0.4 * r.unit()) * W as f32;
        let y = (0.3 + 0.4 * r.unit()) * H as f32;
        let theta = r.unit() * TAU;
        let phase = r.unit() * TAU;
        Self {
            grammar,
            drift,
            base: Canvas::ground(),
            total_active: 0,
            neutral: true,
            buffer: Vec::new(),
            x,
            y,
            theta,
            phase,
            lat_cls: [None; 4],
            lat_k: 0,
            cells: lattice_cells(),
        }
    }

    /// 移植の検算用: Python の試作と同じ歩みの出発点から始める。
    #[cfg(test)]
    pub(crate) fn with_walk_start(
        grammar: Grammar,
        drift: Drift,
        x: f32,
        y: f32,
        theta: f32,
        phase: f32,
    ) -> Self {
        let mut g = Self::new(grammar, drift, 0);
        g.x = x;
        g.y = y;
        g.theta = theta;
        g.phase = phase;
        g
    }

    /// いまの画（中立の間は地）。
    pub fn image(&self) -> &Canvas {
        &self.base
    }

    /// 1 回の更新。`mat` は前の更新からこの更新までの秒の材料。
    pub fn update(&mut self, mat: &[Second]) -> &Canvas {
        let a_u = mat.iter().filter(|s| s.active).count() as u32;
        self.total_active += a_u;
        if self.neutral {
            self.buffer.push(mat.to_vec());
            if self.total_active < NEUTRAL_ACTIVE_S {
                return &self.base;
            }
            self.neutral = false;
            for b in std::mem::take(&mut self.buffer) {
                self.draw(&b);
            }
        } else {
            self.draw(mat);
        }
        if self.drift == Drift::Diffuse {
            self.base.diffuse(DIFFUSE_SIGMA, DIFFUSE_MIX);
        }
        &self.base
    }

    /// 水準（打鍵のあった秒の平均を範囲で正規化）。値が無ければ `None`。
    fn level(mat: &[Second], k: usize) -> Option<f64> {
        let (lo, hi) = RAW_RANGES[k];
        let vals: Vec<f64> = mat
            .iter()
            .filter(|s| s.active)
            .map(|s| [s.f1, s.f3, s.f4, s.f6][k])
            .filter(|v| v.is_finite())
            .collect();
        if vals.is_empty() {
            return None;
        }
        let mean = vals.iter().sum::<f64>() / vals.len() as f64;
        Some(((mean - lo) / (hi - lo)).clamp(0.0, 1.0))
    }

    fn draw(&mut self, mat: &[Second]) {
        let a_u = mat.iter().filter(|s| s.active).count() as u32;
        if a_u == 0 {
            return;
        }
        let m = a_u.div_ceil(ACTIVE_PER_MARK) as usize;
        let levels = [0, 1, 2, 3].map(|k| Self::level(mat, k));
        match self.grammar {
            Grammar::Raw => self.draw_raw(levels, m),
            Grammar::Lattice => self.draw_lattice(levels, m),
        }
    }

    fn step(&mut self, dtheta: f32, step: f32) {
        self.theta += dtheta;
        self.x += step * self.theta.cos();
        self.y += step * self.theta.sin();
        let margin = 10.0;
        if self.x < margin || self.x > W as f32 - margin {
            self.theta = std::f32::consts::PI - self.theta;
            self.x = self.x.clamp(margin, W as f32 - margin);
        }
        if self.y < margin || self.y > H as f32 - margin {
            self.theta = -self.theta;
            self.y = self.y.clamp(margin, H as f32 - margin);
        }
    }

    fn draw_raw(&mut self, levels: [Option<f64>; 4], m: usize) {
        let [n1, n3, n4, n6] = levels.map(|v| v.unwrap_or(0.5) as f32);
        for i in 0..m {
            let fi = i as f32;
            let hue = 0.55 - 0.5 * n3 + 0.03 * (fi * 1.7).sin();
            let sigma = 2.0 + 6.0 * n4;
            let col = hsv(hue, 0.55, 0.35 + 0.4 * n1);
            let heading = TAU * n6 + self.phase + 0.25 * (fi * 2.3).sin();
            self.step(heading - self.theta, 4.0 + 6.0 * n4);
            self.base.blob(self.x, self.y, sigma, col, ALPHA);
        }
    }

    fn draw_lattice(&mut self, levels: [Option<f64>; 4], m: usize) {
        for (k, v) in levels.iter().enumerate() {
            if let Some(v) = v {
                self.lat_cls[k] = Some(lattice_class(*v, self.lat_cls[k]));
            }
        }
        let [k1, k3, k4, k6] = self.lat_cls.map(|c| c.unwrap_or(1));
        let (cx, cy) = self.cells[self.lat_k % self.cells.len()];
        self.lat_k += 1;
        let col = hsv(LAT_HUE[k3], 0.55, LAT_LIGHT[k1]);
        let sigma = LAT_SIGMA[k4];
        let rot = TAU * k6 as f32 / 3.0;
        for i in 0..m {
            let j = i % 7;
            let (x, y) = if j == 0 {
                (cx, cy)
            } else {
                let a = rot + TAU * (j as f32 - 1.0) / 6.0;
                (cx + LAT_OFFSET_PX * a.cos(), cy + LAT_OFFSET_PX * a.sin())
            };
            self.base.blob(x, y, sigma, col, ALPHA);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sec(active: bool) -> Second {
        Second {
            f1: 150.0,
            f3: 0.1,
            f4: 6.0,
            f6: 0.3,
            active,
        }
    }

    #[test]
    fn stays_neutral_until_sixty_active_seconds() {
        for g in [Grammar::Raw, Grammar::Lattice] {
            let mut gen = Generator::new(g, Drift::None, 7);
            let mat: Vec<Second> = (0..300).map(|i| sec(i < 59)).collect();
            assert!(gen.update(&mat).is_ground(), "{g:?}: 59 秒では地のまま");
            let mat: Vec<Second> = (0..300).map(|i| sec(i < 1)).collect();
            assert!(
                !gen.update(&mat).is_ground(),
                "{g:?}: 60 秒に届いたら貯めた分を描く"
            );
        }
    }

    #[test]
    fn an_update_with_no_typing_draws_nothing_without_drift() {
        let mut gen = Generator::new(Grammar::Raw, Drift::None, 7);
        let busy: Vec<Second> = (0..300).map(|_| sec(true)).collect();
        let before = gen.update(&busy).clone();
        let idle: Vec<Second> = (0..300).map(|_| sec(false)).collect();
        assert_eq!(
            gen.update(&idle),
            &before,
            "不在を減り・暗さに写さない（E1-4）"
        );
    }

    #[test]
    fn lattice_cells_start_at_the_centre() {
        let cells = lattice_cells();
        assert_eq!(cells.len(), (W / LAT_CELL_PX) * (H / LAT_CELL_PX));
        let (x, y) = cells[0];
        assert!((x - W as f32 / 2.0).abs() <= LAT_CELL_PX as f32);
        assert!((y - H as f32 / 2.0).abs() <= LAT_CELL_PX as f32);
    }

    #[test]
    fn lattice_class_has_hysteresis() {
        assert_eq!(lattice_class(0.2, None), 0);
        assert_eq!(
            lattice_class(0.34, Some(0)),
            0,
            "境界を δ だけ越えないと上がらない"
        );
        assert_eq!(lattice_class(0.39, Some(0)), 1);
        assert_eq!(lattice_class(0.30, Some(1)), 1);
        assert_eq!(lattice_class(0.27, Some(1)), 0);
    }

    #[test]
    fn round_half_even_matches_python() {
        assert_eq!(round_half_even(2.5), 2);
        assert_eq!(round_half_even(3.5), 4);
        assert_eq!(round_half_even(2.4), 2);
        assert_eq!(round_half_even(2.6), 3);
    }

    /// 移植の検算（手で回す）: `GSE_PORT_CHECK=<json>` に Python の試作の出力を、
    /// `GSE_PORT_CHECK_OUT=<txt>` に結果の書き出し先を置いて
    /// `cargo test --lib port_check -- --ignored`。結果は decisions.md に書く。
    #[test]
    #[ignore]
    fn port_check_against_python() {
        let (Ok(path), Ok(out_path)) = (
            std::env::var("GSE_PORT_CHECK"),
            std::env::var("GSE_PORT_CHECK_OUT"),
        ) else {
            return;
        };
        let v: serde_json::Value =
            serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
        let num = |x: &serde_json::Value| x.as_f64().unwrap_or(f64::NAN);
        let updates: Vec<Vec<Second>> = v["updates"]
            .as_array()
            .unwrap()
            .iter()
            .map(|u| {
                let n = u["active"].as_array().unwrap().len();
                (0..n)
                    .map(|i| Second {
                        f1: num(&u["f1"][i]),
                        f3: num(&u["f3"][i]),
                        f4: num(&u["f4"][i]),
                        f6: num(&u["f6"][i]),
                        active: u["active"][i].as_bool().unwrap(),
                    })
                    .collect()
            })
            .collect();
        let mut report = String::new();
        for run in v["runs"].as_array().unwrap() {
            let grammar = if run["mapping"] == "raw" {
                Grammar::Raw
            } else {
                Grammar::Lattice
            };
            let drift = if run["drift"] == "none" {
                Drift::None
            } else {
                Drift::Diffuse
            };
            let st = &run["start"];
            let mut g = Generator::with_walk_start(
                grammar,
                drift,
                num(&st["x"]) as f32,
                num(&st["y"]) as f32,
                num(&st["theta"]) as f32,
                num(&st["phase"]) as f32,
            );
            for u in &updates {
                g.update(u);
            }
            let py: Vec<f64> = run["final"].as_array().unwrap().iter().map(num).collect();
            let mut max = 0.0_f64;
            let mut sum = 0.0_f64;
            for (i, p) in g.image().px.iter().enumerate() {
                for c in 0..3 {
                    let d = (p[c] as f64 - py[i * 3 + c]).abs();
                    max = max.max(d);
                    sum += d;
                }
            }
            report.push_str(&format!(
                "{:?} {:?}: max |diff| = {:.6}, mean |diff| = {:.8}\n",
                grammar,
                drift,
                max,
                sum / py.len() as f64
            ));
        }
        std::fs::write(out_path, report).unwrap();
    }

    #[test]
    fn the_same_material_and_seed_draw_the_same_image() {
        let mat: Vec<Second> = (0..300).map(|i| sec(i % 3 == 0)).collect();
        for g in [Grammar::Raw, Grammar::Lattice] {
            for d in [Drift::None, Drift::Diffuse] {
                let mut a = Generator::new(g, d, 42);
                let mut b = Generator::new(g, d, 42);
                assert_eq!(a.update(&mat), b.update(&mat), "{g:?} {d:?}");
            }
        }
    }
}
