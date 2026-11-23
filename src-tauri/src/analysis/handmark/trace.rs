//! 手跡のポインタの「跡の場」（design.md v2・ADR-050 D2〜D4・ADR-051 D3）。
//!
//! 画面を実寸に依らない正準の箱（横 1.6・縦 1.0・y は下向き）で表し、横 16 × 縦 10 の格子の
//! マスごとに「草を倒す量 `bend`」「粒を寄せる向きと量 `pull_x`・`pull_y`」を持つ。値は 16ms の
//! 固定刻みで 0 へ戻る。ライブも再生も同じ [`TraceField`] を通る。
//!
//! ## 守っていること
//!
//! - 持つのは固定長の配列・最後の一点・0 へ戻る値だけ。位置や押下の列を持たない（ADR-050 D4）。
//! - [`Point`]・[`Step`]・[`TraceState`]・[`TraceField`] は `Debug`・`Display`・`serde::Serialize` を持たない
//!   （ADR-050 D3。記録の型のフィールドに入れるとコンパイルが通らない）。
//! - 刻みの中で `pow`・`exp`・三角関数を呼ばない。係数は f32 のリテラル定数で、機械を跨いでもビット単位で
//!   同じになる（`sqrt` は IEEE で正しく丸められる）。テストが `powf` との差を確かめる。
//! - 刻みは絶対時刻の 16 の倍数にそろえる。`advance_to` を何回に分けても結果は同じ。

/// 刻み（ms）。
pub const STEP_MS: u64 = 16;
/// 正準の箱の横。
pub const BOX_W: f32 = 1.6;
/// 正準の箱の縦。
pub const BOX_H: f32 = 1.0;
/// 格子の横のマス数。
pub const GRID_W: usize = 16;
/// 格子の縦のマス数。
pub const GRID_H: usize = 10;
/// 格子のマス数。
pub const CELLS: usize = GRID_W * GRID_H;
/// 1 マスの辺（箱の単位）。
const CELL: f32 = 0.1;

/// `0.5^(16/700)`。
const DECAY_BEND: f32 = 0.984_281_5;
/// `0.5^(16/900)`。
const DECAY_PULL: f32 = 0.987_753;
/// 速さの平滑 `1 − 0.6^(16/16.7)`。
const SMOOTH_A: f32 = 0.387_014_36;
/// 粒の 1 刻みの寄せの上限の係数 `1 − 0.8^(16/16.7)`。
const PULL_RATE: f32 = 0.192_482_24;

/// 倒しの半径（箱の単位）。
const CURSOR_R: f32 = 0.16;
const CURSOR_PUSH: f32 = 6.0;
pub const BEND_MAX: f32 = 0.9;
/// この速さ（箱/秒）を超えると倒しは頭打ち（`BOX_W × 0.4`）。
const CURSOR_FULL: f32 = 0.64;
/// 平滑した速さがこれ未満なら止まっているとみなす（箱/秒）。
const CURSOR_STILL: f32 = 0.01;
/// 寄せの半径。
const MOTE_R: f32 = 0.18;
const MOTE_PULL: f32 = 0.0006;
pub const MOTE_MAX: f32 = 0.08;
/// 刻みの秒（0.016）。
const DT_S: f32 = 0.016;
/// 最後の入力からこの刻み数（8000ms）で、場と速さを正確に 0 にする。
const ZERO_AFTER_TICKS: u64 = 500;

/// 正準の箱の一点と、左の押下。
#[derive(Clone, Copy, PartialEq)]
pub struct Point {
    pub x: f32,
    pub y: f32,
    pub left_down: bool,
}

/// 1 刻みの入力。打鍵は入れない。
#[derive(Clone, Copy, PartialEq)]
pub struct Step {
    /// その刻みで読めた一点（読みなしは `None`）。
    pub sample: Option<Point>,
    /// カーソルの入力が入っているか。
    pub cursor_on: bool,
    /// クリックの入力が入っているか。
    pub click_on: bool,
    /// 読んだが、画面の外だった（副画面など・`to_point` が `None`）。`true` の刻みは最後の一点を捨て、
    /// 速さを 0 にし、前の押下を「押されている」とみなす（戻ったとき古い速さが効かず、押したまま戻って
    /// 波紋も出ない）。読まなかった刻み（呼び出しの遅れ）は `false` のまま `sample: None`（速さを保つ）。
    pub lost: bool,
}

/// 押下が始まった刻みの正準の位置（波紋の種）。
#[derive(Clone, Copy, PartialEq)]
pub struct RipplePoint {
    pub x: f32,
    pub y: f32,
    /// 押下が始まった刻みの場の世代（窓が、切る前に送られた波紋を捨てるのに使う）。
    pub epoch: u32,
}

/// 窓へ渡す場の写し。`cells[i][0..3]` は `bend`・`pull_x`・`pull_y`、`i = j * GRID_W + col`。
#[derive(Clone, Copy, PartialEq)]
pub struct TraceState {
    pub epoch: u32,
    pub cells: [[f32; 3]; CELLS],
}

impl TraceState {
    /// 全部が 0（窓へ「止まった」と 1 回だけ知らせる判定）。
    pub fn is_zero(&self) -> bool {
        self.cells.iter().all(|c| c.iter().all(|v| *v == 0.0))
    }

    /// 各 f32 のビット列まで比べるための写し（先頭は世代）。
    pub fn bits(&self) -> Vec<u32> {
        let mut out = Vec::with_capacity(1 + CELLS * 3);
        out.push(self.epoch);
        for c in &self.cells {
            out.extend(c.iter().map(|v| v.to_bits()));
        }
        out
    }
}

/// 跡の場の積分器。
#[derive(Clone)]
pub struct TraceField {
    cells: [[f32; 3]; CELLS],
    vx: f32,
    vy: f32,
    /// 最後の一点と、それを読んだ刻みの番号。
    last: Option<(f32, f32, u64)>,
    prev_down: bool,
    /// 最後の入力（動きか押下）の刻みの番号。
    last_input: Option<u64>,
    /// 最後に処理した刻みの時刻（16 の倍数）。
    grid_t: u64,
    epoch: u32,
}

impl TraceField {
    /// `t0` はその走行でポインタを読み始めた時刻（UTC の ms）。格子（16 の倍数）に丸める。
    pub fn new(t0: u64) -> Self {
        Self {
            cells: [[0.0; 3]; CELLS],
            vx: 0.0,
            vy: 0.0,
            last: None,
            // 最初の一点までは押されているとみなす（開いたとき押しっぱなしで波紋を出さない）。
            prev_down: true,
            last_input: None,
            grid_t: t0 / STEP_MS * STEP_MS,
            epoch: 0,
        }
    }

    /// 8 秒以内に入力（動きか押下）があった（場が 0 へ戻りきっていない）。
    pub fn is_active(&self) -> bool {
        self.last_input.is_some()
    }

    /// 最後に処理した刻みの時刻。
    pub fn grid_t(&self) -> u64 {
        self.grid_t
    }

    /// 入れ切りや門が変わったとき。場・速さ・最後の一点を 0 に戻し、世代を進める。
    /// 前の押下は「押されている」とみなす（離すまで波紋を出さない）。
    pub fn reset(&mut self) {
        self.cells = [[0.0; 3]; CELLS];
        self.vx = 0.0;
        self.vy = 0.0;
        self.last = None;
        self.prev_down = true;
        self.last_input = None;
        self.epoch = self.epoch.wrapping_add(1);
    }

    /// 以後の読みなしの刻みが何も変えない（場も速さも 0 で、最後の入力も無い）。
    fn is_idle(&self) -> bool {
        self.last_input.is_none()
            && self.vx == 0.0
            && self.vy == 0.0
            && self.cells.iter().all(|c| c.iter().all(|v| *v == 0.0))
    }

    /// 時計が戻ったとき。場・速さ・最後の一点を 0 に戻し（世代を進め）、格子を `t0`（UTC の ms ではなく
    /// 呼び手の時計）から取り直す。
    pub fn rebase(&mut self, t0: u64) {
        self.reset();
        self.grid_t = t0 / STEP_MS * STEP_MS;
    }

    /// `t` 以下の格子の点まで、読みなしの刻みで進める（`t` が格子の手前なら何もしない）。
    /// 止まっている区間（`is_idle`）は刻みで何も変わらないので、まとめて進める。
    /// 埋める刻みは `cursor_on: false`（速さを 0 に戻す）。
    pub fn advance_to(&mut self, t: u64) {
        self.advance_held(t, false);
    }

    /// `advance_to` と同じだが、埋める刻みの `cursor_on` を指定する。`true`（カーソルが入っていて、
    /// その刻みは読めなかった）なら速さを保つ（場へは足さない）。ライブの `tick` が呼び出しの間の刻みを
    /// 埋めるのに使う。
    pub fn advance_held(&mut self, t: u64, cursor_on: bool) {
        let idle_step = Step {
            sample: None,
            cursor_on,
            click_on: false,
            lost: false,
        };
        while self.grid_t.saturating_add(STEP_MS) <= t {
            if self.is_idle() {
                self.grid_t += (t - self.grid_t) / STEP_MS * STEP_MS;
                return;
            }
            self.step(idle_step);
        }
    }

    /// 次の 1 刻み（`grid_t + 16`）を進める。押下が始まったらその位置を返す。
    pub fn step(&mut self, input: Step) -> Option<RipplePoint> {
        self.grid_t += STEP_MS;
        let tick = self.grid_t / STEP_MS;

        // 1. 減衰
        for c in &mut self.cells {
            c[0] *= DECAY_BEND;
            c[1] *= DECAY_PULL;
            c[2] *= DECAY_PULL;
        }

        // 1b. 読んだが画面の外だった: 最後の一点・速さ・前の押下を捨てる（戻った最初の一点を古い値で扱わない）
        if input.lost {
            self.last = None;
            self.vx = 0.0;
            self.vy = 0.0;
            self.prev_down = true;
        }

        // 2. 速さ
        let mut cursor_at: Option<(f32, f32)> = None;
        match (input.cursor_on, input.sample) {
            (true, Some(p)) => {
                if let Some((px, py, pt)) = self.last {
                    let dt = (tick - pt) as f32 * DT_S;
                    let vx = (p.x - px) / dt;
                    let vy = (p.y - py) / dt;
                    self.vx += (vx - self.vx) * SMOOTH_A;
                    self.vy += (vy - self.vy) * SMOOTH_A;
                    if (self.vx * self.vx + self.vy * self.vy).sqrt() < CURSOR_STILL {
                        self.vx = 0.0;
                        self.vy = 0.0;
                    }
                    if p.x != px || p.y != py {
                        self.last_input = Some(tick);
                    }
                } else {
                    self.vx = 0.0;
                    self.vy = 0.0;
                }
                self.last = Some((p.x, p.y, tick));
                cursor_at = Some((p.x, p.y));
            }
            // 入っているが読めなかった刻み: 速さは保つ（場へは足さない）。0 に戻すと、呼び出しの間隔が
            // 揺れて飛ばした刻みのたびに倒しが弱まる。
            (true, None) => {}
            (false, _) => {
                self.vx = 0.0;
                self.vy = 0.0;
            }
        }

        if let Some((cx, cy)) = cursor_at {
            // 3. 倒し
            let cv = (self.vx / CURSOR_FULL).clamp(-1.0, 1.0);
            if cv != 0.0 {
                for j in 0..GRID_H {
                    for i in 0..GRID_W {
                        let (dx, dy) = (cx - center(i), cy - center(j));
                        let d = (dx * dx + dy * dy).sqrt();
                        if d < CURSOR_R {
                            let k = 1.0 - d / CURSOR_R;
                            let f = k * k;
                            let b = &mut self.cells[j * GRID_W + i][0];
                            *b = (*b + cv * f * CURSOR_PUSH * DT_S).clamp(-BEND_MAX, BEND_MAX);
                        }
                    }
                }
            }
            // 4. 寄せ
            let s = (self.vx * self.vx + self.vy * self.vy).sqrt();
            if s != 0.0 {
                for j in 0..GRID_H {
                    for i in 0..GRID_W {
                        let (dx, dy) = (cx - center(i), cy - center(j));
                        let d = (dx * dx + dy * dy).sqrt();
                        if d < MOTE_R && d > 1e-4 {
                            let f = 1.0 - d / MOTE_R;
                            let amount = (d * PULL_RATE).min(s * f * MOTE_PULL * 16.0);
                            let c = &mut self.cells[j * GRID_W + i];
                            c[1] += dx / d * amount;
                            c[2] += dy / d * amount;
                            let m = (c[1] * c[1] + c[2] * c[2]).sqrt();
                            if m > MOTE_MAX {
                                let r = MOTE_MAX / m;
                                c[1] *= r;
                                c[2] *= r;
                            }
                        }
                    }
                }
            }
        }

        // 5. 押下
        let mut ripple = None;
        if let Some(p) = input.sample {
            if input.click_on && p.left_down && !self.prev_down {
                ripple = Some(RipplePoint {
                    x: p.x,
                    y: p.y,
                    epoch: self.epoch,
                });
                self.last_input = Some(tick);
            }
            // 入れていないときも更新する（入れ直した瞬間に押しっぱなしで波紋を出さない）。
            self.prev_down = p.left_down;
        }

        // 6. 最後の入力から 8 秒で、場と速さを正確に 0 にする。
        if let Some(li) = self.last_input {
            if tick - li >= ZERO_AFTER_TICKS {
                self.cells = [[0.0; 3]; CELLS];
                self.vx = 0.0;
                self.vy = 0.0;
                self.last_input = None;
            }
        }
        ripple
    }

    /// いまの場の写し。
    pub fn state(&self) -> TraceState {
        TraceState {
            epoch: self.epoch,
            cells: self.cells,
        }
    }
}

/// 場の値 `v / max` を −127〜127 に丸める（窓へ送る形。机上のコマも同じ関数で作る・手跡の PR 4）。
pub fn quantize_cell(v: f32, max: f32) -> i8 {
    ((v / max) * 127.0).round().clamp(-127.0, 127.0) as i8
}

/// 場を窓へ送る形にする（`i * GRID_W + col` の順に `bend`・`pull_x`・`pull_y`、各 −127〜127）。
pub fn encode_cells(cells: &[[f32; 3]; CELLS]) -> Vec<i8> {
    let mut out = Vec::with_capacity(CELLS * 3);
    for c in cells {
        out.push(quantize_cell(c[0], BEND_MAX));
        out.push(quantize_cell(c[1], MOTE_MAX));
        out.push(quantize_cell(c[2], MOTE_MAX));
    }
    out
}

/// マス `i`（横でも縦でも）の中心（箱の単位）。
fn center(i: usize) -> f32 {
    (i as f32 + 0.5) * CELL
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn quantize_rounds_and_clips() {
        assert_eq!(quantize_cell(0.0, BEND_MAX), 0);
        assert_eq!(quantize_cell(BEND_MAX, BEND_MAX), 127);
        assert_eq!(quantize_cell(-BEND_MAX, BEND_MAX), -127);
        assert_eq!(quantize_cell(BEND_MAX * 3.0, BEND_MAX), 127);
        assert_eq!(quantize_cell(-BEND_MAX * 3.0, BEND_MAX), -127);
        assert_eq!(quantize_cell(f32::NAN, BEND_MAX), 0);
        assert_eq!(quantize_cell(MOTE_MAX / 2.0, MOTE_MAX), 64);
    }

    #[test]
    fn encoded_cells_are_cell_major_bend_pull_x_pull_y() {
        let mut cells = [[0.0; 3]; CELLS];
        cells[0] = [BEND_MAX, 0.0, 0.0];
        cells[1] = [0.0, MOTE_MAX, -MOTE_MAX];
        cells[CELLS - 1] = [-BEND_MAX, 0.0, MOTE_MAX];
        let e = encode_cells(&cells);
        assert_eq!(e.len(), CELLS * 3);
        assert_eq!(&e[0..6], &[127, 0, 0, 0, 127, -127]);
        assert_eq!(&e[(CELLS - 1) * 3..], &[-127, 0, 127]);
    }

    fn pt(x: f32, y: f32) -> Point {
        Point {
            x,
            y,
            left_down: false,
        }
    }

    fn on(p: Point) -> Step {
        Step {
            sample: Some(p),
            cursor_on: true,
            click_on: true,
            lost: false,
        }
    }

    /// 円を描く一点の列（テストの入力。実行時の三角関数はテストだけ）。
    fn circle(n: usize) -> Vec<Point> {
        (0..n)
            .map(|k| {
                let a = k as f32 * 0.07;
                pt(0.8 + 0.5 * a.cos(), 0.5 + 0.3 * a.sin())
            })
            .collect()
    }

    fn run(points: &[Point]) -> TraceField {
        let mut f = TraceField::new(1_600);
        for p in points {
            f.step(on(*p));
        }
        f
    }

    #[test]
    fn same_input_gives_bit_identical_state() {
        let pts = circle(120);
        assert!(run(&pts).state().bits() == run(&pts).state().bits());
        assert!(!run(&pts).state().is_zero());
    }

    #[test]
    fn changing_one_point_changes_the_state() {
        let pts = circle(120);
        let mut other = pts.clone();
        other[60].x += 0.01;
        assert!(run(&pts).state().bits() != run(&other).state().bits());
    }

    #[test]
    fn advance_to_in_pieces_equals_at_once() {
        let pts = circle(40);
        let mut a = run(&pts);
        let mut b = a.clone();
        let t_end = a.grid_t() + 3_000;
        a.advance_to(t_end);
        let mut t = b.grid_t();
        while t < t_end {
            t += 7;
            b.advance_to(t.min(t_end));
        }
        // 刻みを 1 つずつ（読みなし）でも同じ。
        let mut c = run(&pts);
        while c.grid_t() + STEP_MS <= t_end {
            c.step(Step {
                sample: None,
                cursor_on: true,
                click_on: true,
                lost: false,
            });
        }
        assert!(a.grid_t() == b.grid_t() && a.grid_t() == c.grid_t());
        assert!(a.state().bits() == b.state().bits());
        assert!(a.state().bits() == c.state().bits());
    }

    #[test]
    fn grid_is_absolute() {
        let mut f = TraceField::new(1_605);
        assert!(f.grid_t() == 1_600);
        f.advance_to(1_615);
        assert!(f.grid_t() == 1_600);
        f.advance_to(1_616);
        assert!(f.grid_t() == 1_616);
    }

    #[test]
    fn decays_and_is_exactly_zero_after_eight_seconds() {
        let mut f = run(&circle(60));
        let before = f.state();
        assert!(!before.is_zero());
        f.advance_to(f.grid_t() + 700);
        let mid = f.state();
        let max = |s: &TraceState| s.cells.iter().map(|c| c[0].abs()).fold(0.0f32, f32::max);
        assert!(max(&mid) < max(&before));
        f.advance_to(f.grid_t() + 7_400);
        assert!(f.state().is_zero());
    }

    #[test]
    fn values_stay_bounded_when_moving_for_long() {
        let mut f = TraceField::new(0);
        for k in 0..6_000 {
            let a = k as f32 * 0.35;
            f.step(on(pt(0.8 + 0.7 * a.cos(), 0.5 + 0.45 * a.sin())));
            let s = f.state();
            for c in &s.cells {
                assert!(c[0].abs() <= BEND_MAX);
                assert!((c[1] * c[1] + c[2] * c[2]).sqrt() <= MOTE_MAX * 1.000_01);
            }
        }
        assert!(!f.state().is_zero());
    }

    #[test]
    fn cursor_off_leaves_the_field_alone() {
        let mut f = TraceField::new(0);
        for p in circle(100) {
            f.step(Step {
                sample: Some(p),
                cursor_on: false,
                click_on: true,
                lost: false,
            });
        }
        assert!(f.state().is_zero());
    }

    #[test]
    fn click_off_gives_no_ripple_and_click_on_does() {
        let down = |x| Point {
            x,
            y: 0.5,
            left_down: true,
        };
        let mut f = TraceField::new(0);
        f.step(Step {
            sample: Some(pt(0.4, 0.5)),
            cursor_on: true,
            click_on: false,
            lost: false,
        });
        let r = f.step(Step {
            sample: Some(down(0.4)),
            cursor_on: true,
            click_on: false,
            lost: false,
        });
        assert!(r.is_none());
        // 押しっぱなしのまま入れても出ない。
        let r = f.step(on(down(0.4)));
        assert!(r.is_none());
        // 離してから押すと出る。
        f.step(on(pt(0.4, 0.5)));
        let r = f.step(on(down(0.45))).expect("ripple");
        assert!(r.x == 0.45 && r.y == 0.5);
        // 押し続けても 2 度目は出ない。
        assert!(f.step(on(down(0.45))).is_none());
    }

    #[test]
    fn reset_zeroes_advances_epoch_and_hides_a_held_button() {
        let mut f = run(&circle(80));
        let e = f.state().epoch;
        f.reset();
        let s = f.state();
        assert!(s.is_zero());
        assert!(s.epoch == e + 1);
        let down = Point {
            x: 0.3,
            y: 0.3,
            left_down: true,
        };
        assert!(f.step(on(down)).is_none());
        assert!(f.step(on(down)).is_none());
        f.step(on(pt(0.3, 0.3)));
        assert!(f.step(on(down)).is_some());
    }

    fn max_bend(f: &TraceField) -> f32 {
        f.state()
            .cells
            .iter()
            .map(|c| c[0].abs())
            .fold(0.0, f32::max)
    }

    #[test]
    fn a_still_cursor_far_apart_in_ticks_does_not_jump() {
        // 読めなかった刻み（カーソルは入っている）を挟んでも、刻みの差で割る（速さが跳ね上がらない）。
        let mut f = TraceField::new(0);
        f.step(on(pt(0.2, 0.5)));
        f.advance_held(f.grid_t() + 160, true);
        f.step(on(pt(0.3, 0.5)));
        let held = max_bend(&f);
        // 0.1 箱 / (11 刻み × 0.016) = 約 0.57 箱/秒 → cv ≈ 0.89 以下。
        assert!(held > 0.0 && held <= 0.9);
        // 同じ 0.1 を 1 刻みで動いたとみなす（跳ねる）場合より、倒しは小さい。
        let mut j = TraceField::new(0);
        j.step(on(pt(0.2, 0.5)));
        j.step(on(pt(0.3, 0.5)));
        assert!(held < max_bend(&j));
        // 読みなしを `cursor_on: false` で埋めても（速さは 0 へ戻るが）跳ねない。
        let mut f = TraceField::new(0);
        f.step(on(pt(0.2, 0.5)));
        f.advance_to(f.grid_t() + 160);
        f.step(on(pt(0.3, 0.5)));
        let b = max_bend(&f);
        assert!(b > 0.0 && b <= 0.9);
    }

    #[test]
    fn a_missed_read_with_the_cursor_on_keeps_the_speed_and_adds_nothing() {
        let mut f = TraceField::new(0);
        for p in circle(30) {
            f.step(on(p));
        }
        let (vx, vy) = (f.vx, f.vy);
        assert!(vx != 0.0 || vy != 0.0);
        let cells = f.cells;
        let miss = Step {
            sample: None,
            cursor_on: true,
            click_on: true,
            lost: false,
        };
        f.step(miss);
        assert!((f.vx, f.vy) == (vx, vy), "the speed is kept");
        // 場は減衰するだけで、足し込まれない（絶対値が増えるマスが無い）。
        for (a, b) in cells.iter().zip(f.cells.iter()) {
            assert!(b[0].abs() <= a[0].abs() && b[1].abs() <= a[1].abs());
        }
        // 入っていない刻み（`cursor_on: false`）は今までどおり 0 に戻す。
        f.step(Step {
            sample: None,
            cursor_on: false,
            click_on: true,
            lost: false,
        });
        assert!(f.vx == 0.0 && f.vy == 0.0);
    }

    fn lost_step() -> Step {
        Step {
            sample: None,
            cursor_on: true,
            click_on: true,
            lost: true,
        }
    }

    fn max_abs_bend(f: &TraceField) -> f32 {
        f.cells.iter().fold(0.0f32, |m, c| m.max(c[0].abs()))
    }

    #[test]
    fn a_return_from_off_screen_does_not_use_the_old_speed() {
        // 動く → 画面の外（読んだが None）→ 遠くへ戻る。戻った最初の一点に古い速さが効かず、場が跳ねない。
        let far = pt(0.2, 0.9);
        let mut lost = run(&circle(30));
        assert!(lost.vx != 0.0 || lost.vy != 0.0);
        for _ in 0..3 {
            lost.step(lost_step());
        }
        assert!(lost.last.is_none() && lost.vx == 0.0 && lost.vy == 0.0);
        let before = max_abs_bend(&lost);
        lost.step(on(far));
        assert!(
            lost.vx == 0.0 && lost.vy == 0.0,
            "no speed from a stale point"
        );
        assert!(max_abs_bend(&lost) <= before, "the field does not jump");

        // 陰性の対照: 読まなかった刻み（lost でない・呼び出しの遅れ）では、最後の一点が残るので同じ戻りで跳ねる。
        let mut held = run(&circle(30));
        for _ in 0..3 {
            held.step(Step {
                lost: false,
                ..lost_step()
            });
        }
        held.step(on(far));
        assert!(
            held.vx != 0.0 || held.vy != 0.0,
            "the control sees the stale point"
        );
    }

    #[test]
    fn a_press_held_across_an_off_screen_stretch_gives_no_ripple_but_release_and_press_does() {
        let down = |x| Point {
            x,
            y: 0.5,
            left_down: true,
        };
        let mut f = TraceField::new(0);
        f.step(on(pt(0.4, 0.5)));
        // 押したまま画面の外へ出て、押したまま戻る: 波紋は出ない。
        assert!(f.step(on(down(0.4))).is_some());
        f.step(lost_step());
        f.step(lost_step());
        assert!(f.step(on(down(0.9))).is_none());
        assert!(f.step(on(down(0.9))).is_none());
        // 離して画面の外へ出て、戻って押す: 波紋が出る。
        f.step(on(pt(0.9, 0.5)));
        f.step(lost_step());
        // 離している間に外へ出たので、戻った最初の一点までは「押されている」とみなす（その一点が離している）。
        assert!(f.step(on(pt(0.5, 0.5))).is_none());
        let r = f.step(on(down(0.5)));
        assert!(r.is_some_and(|r| r.x == 0.5));
    }

    #[test]
    fn rebase_zeroes_advances_epoch_and_retakes_the_grid() {
        let mut f = run(&circle(40));
        let e = f.state().epoch;
        f.rebase(2_005);
        assert!(f.state().is_zero() && f.state().epoch == e + 1);
        assert!(f.grid_t() == 2_000);
    }

    #[test]
    fn literal_constants_match_powf() {
        let close = |lit: f32, exact: f32| (lit - exact).abs() < 1e-6;
        assert!(close(DECAY_BEND, 0.5f32.powf(16.0 / 700.0)));
        assert!(close(DECAY_PULL, 0.5f32.powf(16.0 / 900.0)));
        assert!(close(SMOOTH_A, 1.0 - 0.6f32.powf(16.0 / 16.7)));
        assert!(close(PULL_RATE, 1.0 - 0.8f32.powf(16.0 / 16.7)));
        assert!(close(CURSOR_FULL, BOX_W * 0.4));
        assert!(GRID_W as f32 * CELL == BOX_W && GRID_H as f32 * CELL == BOX_H);
    }

    #[test]
    fn center_of_cells() {
        assert!(center(0) == 0.05);
        assert!((center(GRID_W - 1) - 1.55).abs() < 1e-6);
    }
}
