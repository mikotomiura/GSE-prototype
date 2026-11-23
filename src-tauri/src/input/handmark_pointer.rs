//! 手跡のポインタの読みの型（OS 非依存・ADR-050 D2〜D4）。
//!
//! OS の API を呼ぶのは別のファイル（macOS 用は後の段）で、ここは読んだ値の型と、正準の箱への写しだけを持つ。
//! 表現に使うが記録しない・溜めない:
//! - [`PointerSample`] は `Debug`・`Display`・`Serialize` を持たない（記録の型のフィールドに入れるとコンパイルが
//!   通らない）。
//! - 画面の大きさは [`to_point`] の引数としてだけ使い、保持しない。
//! - 向き（`analysis` が `input` を参照しない）に合わせ、写しの先の [`Point`] は `analysis` 側の型。

use crate::analysis::handmark::trace::{Point, BOX_W};

/// OS から読んだ一点。座標は主画面の左下が原点（macOS は Cocoa の座標の point、Windows は物理ピクセルを
/// [`from_top_left`] で直したもの）。
#[derive(Clone, Copy)]
pub struct PointerSample {
    x: f64,
    y: f64,
    left_down: bool,
}

impl PointerSample {
    pub fn new(x: f64, y: f64, left_down: bool) -> Self {
        Self { x, y, left_down }
    }

    pub fn x(&self) -> f64 {
        self.x
    }

    pub fn y(&self) -> f64 {
        self.y
    }

    pub fn left_down(&self) -> bool {
        self.left_down
    }
}

/// 左上が原点で y が下向きの座標（Windows の `GetCursorPos`・物理ピクセル）を、[`PointerSample`] の約束
/// （左下が原点・y は上向き）へ直す。`screen_h` は主画面の高さ（同じ単位）。画面の外の値もそのまま直し、
/// 外かどうかは [`to_point`] が決める。
pub fn from_top_left(x: f64, y_down: f64, screen_h: f64, left_down: bool) -> PointerSample {
    PointerSample::new(x, screen_h - y_down, left_down)
}

/// 一点を正準の箱（横 1.6・縦 1.0・y は下向き）へ写す。
///
/// `screen_w_pt`・`screen_h_pt` は主画面の大きさ（point）。0 以下、または一点が画面の外（NaN を含む）なら `None`。
pub fn to_point(sample: PointerSample, screen_w_pt: f64, screen_h_pt: f64) -> Option<Point> {
    if !(screen_w_pt > 0.0 && screen_h_pt > 0.0) {
        return None;
    }
    let inside = (0.0..=screen_w_pt).contains(&sample.x) && (0.0..=screen_h_pt).contains(&sample.y);
    if !inside {
        return None;
    }
    Some(Point {
        x: (sample.x / screen_w_pt * f64::from(BOX_W)) as f32,
        y: (1.0 - sample.y / screen_h_pt) as f32,
        left_down: sample.left_down,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn maps_to_the_canonical_box_with_y_flipped() {
        // 1440 x 900 の画面の左下・右上・中央。
        let p = to_point(PointerSample::new(0.0, 0.0, false), 1440.0, 900.0).expect("in");
        assert!(p.x == 0.0 && p.y == 1.0 && !p.left_down);
        let p = to_point(PointerSample::new(1440.0, 900.0, true), 1440.0, 900.0).expect("in");
        assert!(p.x == BOX_W && p.y == 0.0 && p.left_down);
        let p = to_point(PointerSample::new(720.0, 450.0, false), 1440.0, 900.0).expect("in");
        assert!((p.x - 0.8).abs() < 1e-6 && (p.y - 0.5).abs() < 1e-6);
    }

    /// Windows の向き（左上が原点）から直した一点は、Mac の向き（左下が原点）と同じ箱の位置に写る。
    /// 両 OS で走る（OS ごとに規則が違う写しの対のテスト）。
    #[test]
    fn top_left_origin_maps_to_the_same_box_as_bottom_left_origin() {
        // 1920 x 1080 の画面の左上（Windows の (0,0)）は、Mac の向きでは (0,1080)。
        let w = to_point(from_top_left(0.0, 0.0, 1080.0, false), 1920.0, 1080.0).expect("in");
        let m = to_point(PointerSample::new(0.0, 1080.0, false), 1920.0, 1080.0).expect("in");
        assert!(w.x == m.x && w.y == m.y && w.y == 0.0);
        // 右下（Windows の (1920,1080)）は箱の (1.6, 1.0)。
        let p = to_point(from_top_left(1920.0, 1080.0, 1080.0, true), 1920.0, 1080.0).expect("in");
        assert!(p.x == BOX_W && p.y == 1.0 && p.left_down);
        // 上から 270 の点は箱の y = 0.25（y は下向き）。
        let p = to_point(from_top_left(960.0, 270.0, 1080.0, false), 1920.0, 1080.0).expect("in");
        assert!((p.x - 0.8).abs() < 1e-6 && (p.y - 0.25).abs() < 1e-6);
        // 画面の下より下（多画面の別の画面）は外。
        assert!(to_point(from_top_left(10.0, 1081.0, 1080.0, false), 1920.0, 1080.0).is_none());
    }

    #[test]
    fn outside_the_screen_is_none() {
        for (x, y) in [(-1.0, 10.0), (10.0, -0.5), (1441.0, 10.0), (10.0, 901.0)] {
            assert!(to_point(PointerSample::new(x, y, false), 1440.0, 900.0).is_none());
        }
        assert!(to_point(PointerSample::new(f64::NAN, 1.0, false), 1440.0, 900.0).is_none());
    }

    #[test]
    fn a_zero_or_negative_screen_is_none() {
        for (w, h) in [
            (0.0, 900.0),
            (1440.0, 0.0),
            (-1.0, 900.0),
            (1440.0, -3.0),
            (f64::NAN, 900.0),
        ] {
            assert!(to_point(PointerSample::new(1.0, 1.0, false), w, h).is_none());
        }
    }
}
