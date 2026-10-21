//! 手跡の背景の層の表現の入力（カーソルの位置と左の押下）。OS に依らない部分（spike）。
//!
//! ADR-040（枝 `docs/tangibility-design`・Proposed）: 表現に使うが記録しない・溜めない。
//! - `PointerSample`・`PointerUpdate` は `Debug`・`Display`・`Serialize` を持たない（D3 の型の層）。
//!   記録の型（`Debug` を derive している）のフィールドに入れるとコンパイルが通らない。
//! - 持つのは最後の一点と左の押下の前の値だけ（D4）。列を作らない。
//! - OS の API は `handmark_pointer_macos.rs` だけが呼ぶ。O1 の `observe*.rs` とは別のファイル。
//! - 検査は `crate::handmark_stage_guard`（テストだけのモジュール）。

/// OS から読んだ一点。座標は主画面の左下が原点の Cocoa の座標（point）。
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
}

/// 前の一点からの変化。窓へは `crate::handmark_stage_pointer` の専用の関数で数にして渡す。
#[derive(Clone, Copy)]
pub struct PointerUpdate {
    x: f64,
    y: f64,
    moved: bool,
    clicked: bool,
}

impl PointerUpdate {
    pub fn x(&self) -> f64 {
        self.x
    }
    pub fn y(&self) -> f64 {
        self.y
    }
    /// カーソルが動いた（カーソルの入力を入れているときだけ立つ）。
    pub fn moved(&self) -> bool {
        self.moved
    }
    /// 左のボタンが押された瞬間（クリックの入力を入れているときだけ立つ）。
    pub fn clicked(&self) -> bool {
        self.clicked
    }
}

/// 最後の一点と左の押下の前の値だけを持つ。
pub struct PointerReader {
    last: Option<(f64, f64)>,
    left_was_down: bool,
}

impl PointerReader {
    pub const fn new() -> Self {
        Self {
            last: None,
            left_was_down: false,
        }
    }

    /// 一点を受け、変わったときだけ返す。前の点が無い最初の一点では何も返さない
    /// （入れ直した直後に、切る前の押下や位置から跡が出ないように）。
    pub fn step(
        &mut self,
        s: PointerSample,
        cursor_on: bool,
        click_on: bool,
    ) -> Option<PointerUpdate> {
        let first = self.last.is_none();
        let moved = cursor_on && !first && self.last != Some((s.x, s.y));
        let clicked = click_on && !first && s.left_down && !self.left_was_down;
        self.last = Some((s.x, s.y));
        self.left_was_down = s.left_down;
        (moved || clicked).then_some(PointerUpdate {
            x: s.x,
            y: s.y,
            moved,
            clicked,
        })
    }

    /// 入力を切ったときに呼ぶ。前の点と押下を捨てる。
    pub fn reset(&mut self) {
        self.last = None;
        self.left_was_down = false;
    }
}

impl Default for PointerReader {
    fn default() -> Self {
        Self::new()
    }
}

/// 負荷の計測に使う合成のポインタ（人の手の入力を読まない・ADR-040 判断 7）。
/// 半径 150 の円を 4 秒で 1 周し、2 秒ごとに 80ms だけ左を押す。
pub fn synthetic_sample(t_ms: u64) -> PointerSample {
    let a = (t_ms % 4_000) as f64 / 4_000.0 * std::f64::consts::TAU;
    PointerSample::new(
        600.0 + 150.0 * a.cos(),
        500.0 + 150.0 * a.sin(),
        t_ms % 2_000 < 80,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    fn at(x: f64, y: f64, left: bool) -> PointerSample {
        PointerSample::new(x, y, left)
    }

    #[test]
    fn the_first_point_after_a_reset_yields_nothing() {
        let mut r = PointerReader::new();
        assert!(r.step(at(1.0, 2.0, true), true, true).is_none());
        let u = r.step(at(3.0, 2.0, true), true, true).unwrap();
        assert!(u.moved() && !u.clicked());
        r.reset();
        // 押したまま入れ直しても、最初の一点ではクリックにしない
        assert!(r.step(at(3.0, 2.0, true), true, true).is_none());
        assert!(r.step(at(3.0, 2.0, true), true, true).is_none());
    }

    #[test]
    fn only_the_left_press_edge_is_a_click() {
        let mut r = PointerReader::new();
        r.step(at(5.0, 5.0, false), true, true);
        let u = r.step(at(5.0, 5.0, true), true, true).unwrap();
        assert!(u.clicked() && !u.moved());
        assert_eq!((u.x(), u.y()), (5.0, 5.0));
        // 押したままは 1 回だけ
        assert!(r.step(at(5.0, 5.0, true), true, true).is_none());
        assert!(r.step(at(5.0, 5.0, false), true, true).is_none());
        assert!(r.step(at(5.0, 5.0, true), true, true).unwrap().clicked());
    }

    #[test]
    fn a_switched_off_input_does_not_appear() {
        let mut r = PointerReader::new();
        r.step(at(0.0, 0.0, false), false, true);
        assert!(r.step(at(9.0, 9.0, false), false, true).is_none());
        let u = r.step(at(8.0, 9.0, true), false, true).unwrap();
        assert!(u.clicked() && !u.moved());
        let mut r = PointerReader::new();
        r.step(at(0.0, 0.0, false), true, false);
        let u = r.step(at(1.0, 0.0, true), true, false).unwrap();
        assert!(u.moved() && !u.clicked());
    }

    #[test]
    fn the_synthetic_pointer_moves_and_clicks() {
        let mut r = PointerReader::new();
        let (mut moved, mut clicked) = (0, 0);
        for k in 0..260u64 {
            if let Some(u) = r.step(synthetic_sample(k * 16), true, true) {
                moved += u32::from(u.moved());
                clicked += u32::from(u.clicked());
            }
        }
        // 0〜4.16 秒: 0 秒の押下は最初の一点なので数えず、2 秒と 4 秒の 2 回
        assert_eq!(clicked, 2);
        assert!(moved > 200);
    }
}
