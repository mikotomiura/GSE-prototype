//! 肖像の画布（320×180・f32 の RGB）と、その上の描画の部品（OS API 非依存）。
//!
//! EH1 第 5 回の試作 `experiments/20261010-portrait-eh1-round5/scripts/portrait.py` の
//! `Generator._blob` / `_diffuse` と `hsv` の移植である。値は同じ `config.json` の `canvas` に揃える。
//! ⚠️ 浮動小数の計算の順序が違うので、Python と bit 単位では一致しない（移植の検算は `decisions.md`）。

/// 画布の幅（EH1 の `canvas.w`）。
pub const W: usize = 320;
/// 画布の高さ（EH1 の `canvas.h`）。
pub const H: usize = 180;
/// 地の色（EH1 の `canvas.ground`）。
pub const GROUND: [f32; 3] = [0.92, 0.91, 0.88];
/// 「地から離れた」とみなす差（EH1 の `canvas.coverage_eps`）。
pub const COVERAGE_EPS: f32 = 0.05;

/// RGB の画布。
#[derive(Debug, Clone, PartialEq)]
pub struct Canvas {
    pub px: Vec<[f32; 3]>,
}

impl Default for Canvas {
    fn default() -> Self {
        Self::ground()
    }
}

impl Canvas {
    /// 地だけの画布。
    pub fn ground() -> Self {
        Self {
            px: vec![GROUND; W * H],
        }
    }

    /// 地のままか。
    pub fn is_ground(&self) -> bool {
        self.px.iter().all(|p| *p == GROUND)
    }

    /// ガウスの印を 1 つ重ねる（`_blob`: 半径 3σ+1 の窓の中だけ）。
    pub fn blob(&mut self, x: f32, y: f32, sigma: f32, col: [f32; 3], alpha: f32) {
        let r = (3.0 * sigma) as i64 + 1;
        let x0 = ((x as i64) - r).max(0);
        let x1 = ((x as i64) + r + 1).min(W as i64);
        let y0 = ((y as i64) - r).max(0);
        let y1 = ((y as i64) + r + 1).min(H as i64);
        if x0 >= x1 || y0 >= y1 {
            return;
        }
        let two_s2 = 2.0 * sigma * sigma;
        for yy in y0..y1 {
            for xx in x0..x1 {
                let gx = xx as f32 - x;
                let gy = yy as f32 - y;
                let w = alpha * (-(gx * gx + gy * gy) / two_s2).exp();
                let p = &mut self.px[yy as usize * W + xx as usize];
                for c in 0..3 {
                    p[c] = p[c] * (1.0 - w) + w * col[c];
                }
            }
        }
    }

    /// 拡散（`_diffuse`: ガウスでぼかした画を `mix` だけ混ぜる。scipy `gaussian_filter` の
    /// `mode="nearest"`・`truncate=4.0` と同じ核）。
    pub fn diffuse(&mut self, sigma: f32, mix: f32) {
        let blurred = gaussian_blur(&self.px, sigma);
        for (p, b) in self.px.iter_mut().zip(blurred) {
            for c in 0..3 {
                p[c] = p[c] * (1.0 - mix) + mix * b[c];
            }
        }
    }

    /// 地からの差（チャネルの最大）。
    pub fn deviation(&self, i: usize) -> f32 {
        let p = self.px[i];
        (0..3)
            .map(|c| (p[c] - GROUND[c]).abs())
            .fold(0.0_f32, f32::max)
    }
}

/// scipy の `gaussian_filter` と同じ 1 次元の核（半径 `int(4σ + 0.5)`）。
fn kernel(sigma: f32) -> Vec<f32> {
    let radius = (4.0 * sigma + 0.5) as i64;
    let mut k: Vec<f32> = (-radius..=radius)
        .map(|i| (-0.5 * (i as f32 / sigma).powi(2)).exp())
        .collect();
    let s: f32 = k.iter().sum();
    for v in &mut k {
        *v /= s;
    }
    k
}

/// 分離可能なガウスのぼかし（端は最も近い画素で延ばす = `mode="nearest"`）。
fn gaussian_blur(src: &[[f32; 3]], sigma: f32) -> Vec<[f32; 3]> {
    let k = kernel(sigma);
    let r = (k.len() / 2) as i64;
    let mut tmp = vec![[0.0_f32; 3]; W * H];
    for y in 0..H {
        for x in 0..W {
            let mut acc = [0.0_f32; 3];
            for (j, kv) in k.iter().enumerate() {
                let xx = (x as i64 + j as i64 - r).clamp(0, W as i64 - 1) as usize;
                let p = src[y * W + xx];
                for c in 0..3 {
                    acc[c] += kv * p[c];
                }
            }
            tmp[y * W + x] = acc;
        }
    }
    let mut out = vec![[0.0_f32; 3]; W * H];
    for y in 0..H {
        for x in 0..W {
            let mut acc = [0.0_f32; 3];
            for (j, kv) in k.iter().enumerate() {
                let yy = (y as i64 + j as i64 - r).clamp(0, H as i64 - 1) as usize;
                let p = tmp[yy * W + x];
                for c in 0..3 {
                    acc[c] += kv * p[c];
                }
            }
            out[y * W + x] = acc;
        }
    }
    out
}

/// `colorsys.hsv_to_rgb`（色相は 1 周で折り返す）。
pub fn hsv(h: f32, s: f32, v: f32) -> [f32; 3] {
    let h = h.rem_euclid(1.0);
    if s == 0.0 {
        return [v, v, v];
    }
    let i = (h * 6.0).floor();
    let f = h * 6.0 - i;
    let p = v * (1.0 - s);
    let q = v * (1.0 - s * f);
    let t = v * (1.0 - s * (1.0 - f));
    match (i as i64).rem_euclid(6) {
        0 => [v, t, p],
        1 => [q, v, p],
        2 => [p, v, t],
        3 => [p, q, v],
        4 => [t, p, v],
        _ => [v, p, q],
    }
}

/// 画布を `out_w × out_h` へ双線形で拡げ、8bit の RGB の列にする（壁紙の書き出し用）。
pub fn upscale_rgb8(c: &Canvas, out_w: usize, out_h: usize) -> Vec<u8> {
    let mut out = Vec::with_capacity(out_w * out_h * 3);
    let sx = W as f32 / out_w as f32;
    let sy = H as f32 / out_h as f32;
    for oy in 0..out_h {
        let fy = ((oy as f32 + 0.5) * sy - 0.5).clamp(0.0, (H - 1) as f32);
        let y0 = fy.floor() as usize;
        let y1 = (y0 + 1).min(H - 1);
        let ty = fy - y0 as f32;
        for ox in 0..out_w {
            let fx = ((ox as f32 + 0.5) * sx - 0.5).clamp(0.0, (W - 1) as f32);
            let x0 = fx.floor() as usize;
            let x1 = (x0 + 1).min(W - 1);
            let tx = fx - x0 as f32;
            for ch in 0..3 {
                let a = c.px[y0 * W + x0][ch] * (1.0 - tx) + c.px[y0 * W + x1][ch] * tx;
                let b = c.px[y1 * W + x0][ch] * (1.0 - tx) + c.px[y1 * W + x1][ch] * tx;
                let v = (a * (1.0 - ty) + b * ty).clamp(0.0, 1.0);
                out.push((v * 255.0).round() as u8);
            }
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn hsv_matches_colorsys_on_known_points() {
        assert_eq!(hsv(0.0, 1.0, 1.0), [1.0, 0.0, 0.0]);
        let g = hsv(1.0 / 3.0, 1.0, 1.0);
        assert!((g[1] - 1.0).abs() < 1e-6 && g[0].abs() < 1e-6);
        assert_eq!(hsv(0.5, 0.0, 0.4), [0.4, 0.4, 0.4]);
        // 1 周で折り返す
        let a = hsv(1.25, 0.5, 0.5);
        let b = hsv(0.25, 0.5, 0.5);
        for c in 0..3 {
            assert!((a[c] - b[c]).abs() < 1e-6);
        }
    }

    #[test]
    fn kernel_matches_scipy_radius_and_sums_to_one() {
        let k = kernel(0.6);
        assert_eq!(k.len(), 2 * 2 + 1, "int(4*0.6+0.5) = 2");
        assert!((k.iter().sum::<f32>() - 1.0).abs() < 1e-6);
    }

    #[test]
    fn blob_changes_only_its_neighbourhood_and_diffuse_keeps_a_flat_canvas() {
        let mut c = Canvas::ground();
        c.blob(100.0, 50.0, 4.0, [0.2, 0.3, 0.4], 0.35);
        assert!(!c.is_ground());
        assert_eq!(c.px[10 * W + 10], GROUND, "遠い画素は地のまま");
        let mut flat = Canvas::ground();
        flat.diffuse(0.6, 0.1);
        for p in &flat.px {
            for ch in 0..3 {
                assert!((p[ch] - GROUND[ch]).abs() < 1e-5);
            }
        }
    }

    #[test]
    fn upscale_keeps_a_flat_colour() {
        let c = Canvas::ground();
        let img = upscale_rgb8(&c, 64, 36);
        assert_eq!(img.len(), 64 * 36 * 3);
        let g = [
            (GROUND[0] * 255.0).round() as u8,
            (GROUND[1] * 255.0).round() as u8,
            (GROUND[2] * 255.0).round() as u8,
        ];
        assert!(img.chunks(3).all(|p| p == g));
    }
}
