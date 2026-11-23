//! 手跡のポインタのスレッドの純粋な部分（design.md §3）。
//!
//! 時計・読む口・一時停止を引数で受け、出来事 [`PointerOut`] を返す。OS の API・ファイル・通信・ログを
//! 呼ばない（スレッドの起動と窓への送りは `lib.rs` の側）。`TraceField` はこの駆動役だけが持ち、
//! 打鍵の駆動役（`handmark_driver`）とはロックを共有しない（入れ切りは [`Gate`] の値で受ける）。
//!
//! - 出来事の行き先は窓だけ。記録へ向かう腕を持たない（ADR-050 D2）。
//! - ポインタの値・座標・場の値をログやエラー文に入れない（このファイルは `tracing` も使わない）。
//! - 持つのは [`TraceField`]（固定長の場・最後の一点）と時刻・真偽値だけで、位置や押下の列を持たない（D4）。

use crate::analysis::handmark::trace::{Point, RipplePoint, Step, TraceField, TraceState, STEP_MS};

/// 窓へ場を送る間隔（ms）。刻み（16ms）の 2 つぶん。窓の `TRACE_TICK_MS`（handmarkStageTrace.ts）と同じ。
const TRACE_SEND_MS: u64 = 2 * STEP_MS;
/// 動いている間の待ち（ms）。
const WAIT_ACTIVE_MS: u64 = STEP_MS;
/// 止まっている間の待ち（ms）。
const WAIT_IDLE_MS: u64 = 250;

/// 帯の縦の幅（点）。試作と同じ。
const STRIP_HEIGHT_PT: f64 = 14.0;
/// 帯からこの距離（点）で近さが 0 になる。
const STRIP_NEAR_RANGE_PT: f64 = 80.0;

/// 帯（下の縁）の置き場。帯の窓の層が決める（今は口だけで、層は実装 B）。値は座標の点で、記録しない。
#[derive(Clone, Copy)]
pub struct StripSpot {
    /// 帯の下端の高さ（点・主画面の左下が原点）。
    pub bottom_pt: f64,
    /// 主画面の高さ（点）。読んだ一点（正準の箱）から点へ戻すのに使う。
    pub screen_h_pt: f64,
}

/// 下の縁の帯へのカーソルの近さを 0〜10（0.1 刻み）にする。`y_pt`・`bottom_pt` は主画面の左下が原点の点。
/// カーソルを切っている間・値が壊れているとき（非有限）は 0。帯の上にいれば 10、帯の下端より下は下端からの距離、
/// 上は帯の上端からの距離で 80 点まで薄れて 0 になる。
pub fn strip_near(cursor_on: bool, y_pt: f64, bottom_pt: f64) -> u8 {
    if !cursor_on || !y_pt.is_finite() || !bottom_pt.is_finite() {
        return 0;
    }
    let d = if y_pt < bottom_pt {
        bottom_pt - y_pt
    } else {
        (y_pt - bottom_pt - STRIP_HEIGHT_PT).max(0.0)
    };
    let near = (1.0 - d / STRIP_NEAR_RANGE_PT).clamp(0.0, 1.0);
    (near * 10.0).round() as u8
}

/// 駆動役（打鍵側）が決める入れ切り。
#[derive(Clone, Copy, PartialEq, Eq)]
pub struct Gate {
    /// 手跡の窓が開いている。
    pub open: bool,
    /// カーソルの入力が入っている。
    pub cursor: bool,
    /// クリックの入力が入っている。
    pub click: bool,
}

impl Gate {
    /// 駆動役が書く門の Atomic のビット（0 = 窓が開いている・1 = カーソルが入っている・2 = クリックが入っている）。
    pub fn from_bits(bits: u8) -> Self {
        Self {
            open: bits & 1 != 0,
            cursor: bits & 2 != 0,
            click: bits & 4 != 0,
        }
    }
}

/// ポインタの駆動役の出来事。行き先は窓だけ。
#[derive(Clone, PartialEq)]
pub enum PointerOut {
    /// 場の写し（`TraceState::is_zero` なら「止まった」の知らせ）。
    Trace(Box<TraceState>),
    /// 押下が始まった位置（波紋の種）。
    Ripple(RipplePoint),
    /// 帯へのカーソルの近さ（0〜10）。行き先は帯の窓だけで、場（`TraceField`）には入れない。変わったときだけ出る。
    StripNear(u8),
}

/// ポインタのスレッドの駆動役。
pub struct PointerDriver {
    field: Option<TraceField>,
    /// 前回の `(open, cursor, click, paused)`。
    key: (bool, bool, bool, bool),
    last_trace_ms: u64,
    /// 前回の `tick` の時刻。戻った（前より小さい）ときに読みが止まり続けないよう、場を取り直す。
    last_now_ms: u64,
    /// 最後に出した写しが全部 0 だった。
    sent_zero: bool,
    /// 実効の入れ切りがある（読んでいる）。
    hot: bool,
    /// 最後に出した近さ（初めは 0）。
    near_sent: u8,
}

impl Default for PointerDriver {
    fn default() -> Self {
        Self::new()
    }
}

impl PointerDriver {
    pub fn new() -> Self {
        Self {
            field: None,
            key: (false, false, false, false),
            last_trace_ms: 0,
            last_now_ms: 0,
            sent_zero: true,
            hot: false,
            near_sent: 0,
        }
    }

    /// 次の `tick` までの待ちの目安（ms）。`now_ms` は今の時刻（`tick` に渡す時計と同じもの）。
    /// 実効の入れ切りがある（窓が開いていて・一時停止でなく・カーソルかクリックが入っている）間は
    /// 止まっていても、次の 16ms の格子の境目までの残り（1〜16）。250 は読まない間だけ。
    /// 止まっている間に延ばすと、次の短いクリックを取りこぼす（補訂 1 の項目 1 は 16ms ごとの読み）。
    /// 固定の 16 だと、読みと睡眠の費用で刻みを飛ばす呼び出しが出る。格子の境目へ合わせる。
    pub fn next_wait_ms(&self, now_ms: u64) -> u64 {
        if self.hot {
            (now_ms / WAIT_ACTIVE_MS + 1) * WAIT_ACTIVE_MS - now_ms
        } else {
            WAIT_IDLE_MS
        }
    }

    /// いまの場（まだ開いていなければ `None`）。
    pub fn trace_state(&self) -> Option<TraceState> {
        self.field.as_ref().map(TraceField::state)
    }

    /// 1 回の呼び出し。`now_ms` はこのスレッドの単調な ms（起動からの経過）、`read` は一点を 1 回読む口。
    /// `now_ms` が前回より小さくなったときは、場を 0 に戻して世代を進め、格子を取り直す（読みが止まり続けない）。
    ///
    /// 開いていない・一時停止・カーソルもクリックも切れている間は `read` を呼ばない。
    pub fn tick(
        &mut self,
        now_ms: u64,
        gate: Gate,
        paused: bool,
        read: &mut dyn FnMut() -> Option<Point>,
    ) -> Vec<PointerOut> {
        self.tick_with_strip(now_ms, gate, paused, None, read)
    }

    /// [`Self::tick`] に帯の置き場 `strip` を足したもの。`None`（帯が無い）なら近さは 0。
    /// 近さは読んだ一点から作るだけで、場には触れない（場の値・波紋は `strip` の有無で変わらない）。
    /// 出すのは値が変わったときだけ。カーソルが切れている・一時停止・窓が閉じている・帯が無い・
    /// 一点が画面の外のときは 0 に戻り、0 を 1 回出してそれ以上は出さない。
    pub fn tick_with_strip(
        &mut self,
        now_ms: u64,
        gate: Gate,
        paused: bool,
        strip: Option<StripSpot>,
        read: &mut dyn FnMut() -> Option<Point>,
    ) -> Vec<PointerOut> {
        let mut out = Vec::new();
        let eff_open = gate.open && !paused;
        let reading = eff_open && (gate.cursor || gate.click);

        let went_back = now_ms < self.last_now_ms;
        self.last_now_ms = now_ms;

        let mut fresh = false;
        if eff_open && self.field.is_none() {
            self.field = Some(TraceField::new(now_ms));
            fresh = true;
        }
        let key = (gate.open, gate.cursor, gate.click, paused);
        let changed = key != self.key || (went_back && !fresh);
        self.key = key;

        let Some(field) = self.field.as_mut() else {
            self.hot = false;
            return out;
        };

        if changed {
            if !fresh {
                if went_back {
                    field.rebase(now_ms);
                } else {
                    field.reset();
                }
            }
            out.push(PointerOut::Trace(Box::new(field.state())));
            self.last_trace_ms = now_ms;
            self.sent_zero = true;
        }

        // 読んでいない間・入れ切りが変わった刻みは近さを 0 に戻す。読んだ刻みでは下で作り直す。
        let mut near: Option<u8> = if reading && !changed { None } else { Some(0) };

        if reading {
            let target = now_ms / STEP_MS * STEP_MS;
            if target.saturating_sub(field.grid_t()) >= STEP_MS {
                // 飛ばした刻み。カーソルが入っていれば速さを保つ（読めなかった刻み）。
                field.advance_held(target - STEP_MS, gate.cursor);
                // 読んで画面の外だった（`None`）刻みは `lost`。読まなかった刻み（上の `advance_held`）とは別。
                let sample = read();
                let lost = sample.is_none();
                near = Some(match (sample, strip) {
                    (Some(p), Some(spot)) => strip_near(
                        gate.cursor,
                        (1.0 - f64::from(p.y)) * spot.screen_h_pt,
                        spot.bottom_pt,
                    ),
                    _ => 0,
                });
                let ripple = field.step(Step {
                    sample,
                    cursor_on: gate.cursor,
                    click_on: gate.click,
                    lost,
                });
                if let Some(r) = ripple {
                    out.push(PointerOut::Ripple(r));
                }
                if now_ms.saturating_sub(self.last_trace_ms) >= TRACE_SEND_MS {
                    let st = field.state();
                    let zero = st.is_zero();
                    if !zero || !self.sent_zero {
                        out.push(PointerOut::Trace(Box::new(st)));
                        self.sent_zero = zero;
                    }
                    self.last_trace_ms = now_ms;
                }
            }
        }
        self.hot = reading;
        if let Some(n) = near {
            if n != self.near_sent {
                self.near_sent = n;
                out.push(PointerOut::StripNear(n));
            }
        }
        out
    }
}

/// ポインタのスレッドの本体。OS・Tauri に触る部分（門の Atomic・一時停止・時計・読み・窓への送り・待ち・終了の
/// 判定）は閉包で受ける。`lib.rs` はスレッドを立てて閉包を渡すだけにして、ループの本体を `handmark_guard.rs` の
/// 本文検査（記録・ログ・ファイル・推定の語を持たない）の下に置く。`should_stop` が `true` を返したら戻る。
///
/// - `gate_bits`: 駆動役が書く門の値（[`Gate::from_bits`] の並び）。
/// - `read`: 一点を 1 回読む口（画面の外は `None`）。開いていて入っている間だけ呼ばれる。
/// - `send_trace` / `send_ripple`: 窓へ送る（`lib.rs` が `handmark_stage` の送りを渡す）（第 2 引数は今の時刻）。
/// - `strip_spot`: 帯の置き場（帯が無ければ `None`・近さは 0）。
/// - `send_near`: 帯の窓へ近さを送る（変わったときだけ呼ばれる・第 2 引数は今の時刻）。
/// - `sleep_ms`: 待つ。
#[allow(clippy::too_many_arguments)]
pub fn run_loop(
    mut gate_bits: impl FnMut() -> u8,
    mut paused: impl FnMut() -> bool,
    mut now_ms: impl FnMut() -> u64,
    mut read: impl FnMut() -> Option<Point>,
    mut send_trace: impl FnMut(&TraceState, u64),
    mut send_ripple: impl FnMut(&RipplePoint, u64),
    mut strip_spot: impl FnMut() -> Option<StripSpot>,
    mut send_near: impl FnMut(u8, u64),
    mut sleep_ms: impl FnMut(u64),
    mut should_stop: impl FnMut() -> bool,
) {
    let mut driver = PointerDriver::new();
    loop {
        if should_stop() {
            return;
        }
        let gate = Gate::from_bits(gate_bits());
        let now = now_ms();
        let out = driver.tick_with_strip(now, gate, paused(), strip_spot(), &mut read);
        for o in out {
            match o {
                PointerOut::Trace(s) => send_trace(&s, now),
                PointerOut::Ripple(r) => send_ripple(&r, now),
                PointerOut::StripNear(n) => send_near(n, now),
            }
        }
        sleep_ms(driver.next_wait_ms(now_ms()));
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analysis::handmark::trace_replay::{replay_trace, synth_points};
    use crate::analysis::pointer_bin::PointerBin;

    const ON: Gate = Gate {
        open: true,
        cursor: true,
        click: true,
    };

    fn pt(x: f32, y: f32, down: bool) -> Point {
        Point {
            x,
            y,
            left_down: down,
        }
    }

    fn traces(out: &[PointerOut]) -> Vec<TraceState> {
        out.iter()
            .filter_map(|o| match o {
                PointerOut::Trace(s) => Some(**s),
                PointerOut::Ripple(_) | PointerOut::StripNear(_) => None,
            })
            .collect()
    }

    fn ripples(out: &[PointerOut]) -> usize {
        out.iter()
            .filter(|o| matches!(o, PointerOut::Ripple(_)))
            .count()
    }

    #[test]
    fn read_is_never_called_while_closed_paused_or_both_off() {
        let mut calls = 0u32;
        let mut d = PointerDriver::new();
        let cases = [
            (Gate { open: false, ..ON }, false),
            (ON, true),
            (
                Gate {
                    cursor: false,
                    click: false,
                    ..ON
                },
                false,
            ),
        ];
        for (gate, paused) in cases {
            for k in 0..200u64 {
                let mut read = || {
                    calls += 1;
                    Some(pt(0.5, 0.5, false))
                };
                d.tick(1_600 + k * 16, gate, paused, &mut read);
                assert!(d.next_wait_ms(1_600 + k * 16) == 250);
            }
        }
        assert!(calls == 0);
    }

    #[test]
    fn read_is_called_while_open_and_on() {
        let mut calls = 0u32;
        let mut d = PointerDriver::new();
        for k in 0..10u64 {
            let mut read = || {
                calls += 1;
                Some(pt(0.5, 0.5, false))
            };
            d.tick(1_600 + k * 16, ON, false, &mut read);
        }
        // 開いた最初の tick は刻みが無いので読まない。
        assert!(calls == 9);
        let mut d = PointerDriver::new();
        let mut c2 = 0u32;
        for k in 0..10u64 {
            let mut read = || {
                c2 += 1;
                None
            };
            d.tick(
                1_600 + k * 16,
                Gate {
                    cursor: false,
                    ..ON
                },
                false,
                &mut read,
            );
        }
        assert!(c2 == 9, "click only still reads");
    }

    /// 円を描かせて場を立てる。
    fn drive_circle(d: &mut PointerDriver, from_k: u64, n: u64, gate: Gate) -> Vec<PointerOut> {
        let mut all = Vec::new();
        for k in from_k..from_k + n {
            let a = k as f32 * 0.07;
            let mut read = || Some(pt(0.8 + 0.5 * a.cos(), 0.5 + 0.3 * a.sin(), false));
            all.extend(d.tick(1_600 + k * 16, gate, false, &mut read));
        }
        all
    }

    #[test]
    fn a_change_of_gate_advances_epoch_and_sends_an_all_zero_trace() {
        let mut d = PointerDriver::new();
        let out = drive_circle(&mut d, 0, 60, ON);
        let first = traces(&out);
        assert!(first.first().is_some_and(|s| s.is_zero() && s.epoch == 0));
        assert!(first.iter().any(|s| !s.is_zero()), "the field rises");
        let e0 = first.last().map(|s| s.epoch).unwrap_or(0);

        // カーソルを切る。
        let mut read = || -> Option<Point> { panic!("must not read after both off") };
        let gate = Gate {
            cursor: false,
            click: false,
            ..ON
        };
        let out = d.tick(1_600 + 60 * 16, gate, false, &mut read);
        let t = traces(&out);
        assert!(t.len() == 1 && t[0].is_zero() && t[0].epoch == e0 + 1);

        // 戻す・一時停止・窓を閉じる、でもそれぞれ世代が進む。
        let mut epochs = vec![t[0].epoch];
        let mut now = 1_600 + 61 * 16;
        for (gate, paused) in [
            (ON, false),
            (ON, true),
            (ON, false),
            (Gate { open: false, ..ON }, false),
        ] {
            let mut r = || Some(pt(0.5, 0.5, false));
            let out = d.tick(now, gate, paused, &mut r);
            let t = traces(&out);
            assert!(!t.is_empty() && t[0].is_zero());
            epochs.push(t[0].epoch);
            now += 16;
        }
        assert!(epochs.windows(2).all(|w| w[1] == w[0] + 1), "{epochs:?}");
        // 閉じた後は何も出ない。
        let mut r = || Some(pt(0.5, 0.5, false));
        assert!(d
            .tick(now, Gate { open: false, ..ON }, false, &mut r)
            .is_empty());
    }

    #[test]
    fn no_ripple_for_a_button_held_across_a_toggle_or_the_opening() {
        let mut d = PointerDriver::new();
        let mut all = Vec::new();
        let mut now = 1_600u64;
        // 押しっぱなしのまま開く・走る。
        for _ in 0..20 {
            let mut r = || Some(pt(0.5, 0.5, true));
            all.extend(d.tick(now, ON, false, &mut r));
            now += 16;
        }
        // クリックを切って戻す（押しっぱなし）。
        for gate in [Gate { click: false, ..ON }, ON, ON, ON] {
            let mut r = || Some(pt(0.5, 0.5, true));
            all.extend(d.tick(now, gate, false, &mut r));
            now += 16;
        }
        // 一時停止の前後も。
        for paused in [true, false, false, false] {
            let mut r = || Some(pt(0.5, 0.5, true));
            all.extend(d.tick(now, ON, paused, &mut r));
            now += 16;
        }
        assert!(ripples(&all) == 0);
        // 離して押すと出る。
        let mut r = || Some(pt(0.5, 0.5, false));
        d.tick(now, ON, false, &mut r);
        now += 16;
        let mut r = || Some(pt(0.5, 0.5, true));
        let out = d.tick(now, ON, false, &mut r);
        assert!(ripples(&out) == 1);
    }

    #[test]
    fn trace_goes_out_every_32ms_while_nonzero_and_stops_after_one_zero() {
        let mut d = PointerDriver::new();
        let out = drive_circle(&mut d, 0, 90, ON);
        let moving = traces(&out).len();
        // 90 刻み（約 1.4 秒）で 32ms ごと（16ms の刻みでは 2 刻みに 1 回）。最初の 0 の知らせを含む。
        assert!((43..=47).contains(&moving), "{moving}");
        // 止まる（同じ一点を返し続ける）。8 秒を過ぎると 0 が 1 回だけ出て、あとは出ない。
        let mut all = Vec::new();
        for k in 90..90 + 800u64 {
            let mut r = || {
                Some(pt(
                    0.8 + 0.5 * (89.0f32 * 0.07).cos(),
                    0.5 + 0.3 * (89.0f32 * 0.07).sin(),
                    false,
                ))
            };
            all.extend(d.tick(1_600 + k * 16, ON, false, &mut r));
        }
        let t = traces(&all);
        let zeros = t.iter().filter(|s| s.is_zero()).count();
        assert!(zeros == 1, "zeros={zeros}");
        assert!(t.last().is_some_and(|s| s.is_zero()));
        // 止まって場が 0 でも、読んでいる間は 16（短いクリックを取りこぼさない）。
        assert!(d.next_wait_ms(1_600 + 889 * 16) == 16);
    }

    #[test]
    fn wait_is_16_while_reading_even_when_still_and_250_only_when_not_reading() {
        let mut d = PointerDriver::new();
        drive_circle(&mut d, 0, 30, ON);
        assert!(d.next_wait_ms(1_600 + 29 * 16) == 16);
        // 止まって 8 秒を過ぎ、場が 0 になっても、入っている間は 16。
        let mut now = 1_600 + 30 * 16;
        for _ in 0..1_000 {
            let mut r = || Some(pt(0.5, 0.5, false));
            d.tick(now, ON, false, &mut r);
            assert!(d.next_wait_ms(now) == 16, "now={now}");
            now += 16;
        }
        // クリックだけ・カーソルだけでも読むので 16。
        for gate in [
            Gate {
                cursor: false,
                ..ON
            },
            Gate { click: false, ..ON },
        ] {
            let mut r = || Some(pt(0.5, 0.5, false));
            d.tick(now, gate, false, &mut r);
            assert!(d.next_wait_ms(now) == 16);
            now += 16;
        }
        // 読まない間（一時停止・両方切る・閉じる）は 250。
        for (gate, paused) in [
            (ON, true),
            (
                Gate {
                    cursor: false,
                    click: false,
                    ..ON
                },
                false,
            ),
            (Gate { open: false, ..ON }, false),
        ] {
            let mut r = || Some(pt(0.5, 0.5, false));
            d.tick(now, gate, paused, &mut r);
            assert!(d.next_wait_ms(now) == 250);
            now += 16;
        }
    }

    #[test]
    fn a_return_from_off_screen_through_tick_does_not_jump_the_field() {
        // 画面の外（read が None）を数刻み挟んで、遠くへ戻る。戻った刻みで場が大きく増えない。
        let mut d = PointerDriver::new();
        let out = drive_circle(&mut d, 0, 60, ON);
        assert!(!traces(&out).is_empty());
        let mut now = 1_600 + 60 * 16;
        for _ in 0..4 {
            let mut r = || None;
            d.tick(now, ON, false, &mut r);
            now += 16;
        }
        let before = d.trace_state().expect("opened");
        let mut r = || Some(pt(0.05, 0.95, false));
        d.tick(now, ON, false, &mut r);
        let after = d.trace_state().expect("opened");
        let bend = |s: &TraceState| s.cells.iter().fold(0.0f32, |m, c| m.max(c[0].abs()));
        assert!(bend(&after) <= bend(&before), "no jump on return");
    }

    /// `run_loop` を偽の時計・門・読みで回す（OS に触らない）。時計は待ちの分だけ進める。
    #[test]
    fn run_loop_reads_only_while_open_and_emits_to_the_window_only() {
        use std::cell::{Cell, RefCell};
        let clock = Cell::new(1_600u64);
        let bits = Cell::new(0u8);
        let paused = Cell::new(false);
        let reads = Cell::new(0u32);
        let iterations = Cell::new(0u32);
        let traces_out = RefCell::new(0u32);
        let ripples_out = RefCell::new(0u32);
        let slept = RefCell::new(Vec::new());
        // 閉じている 5 周 → 開く（カーソル + クリック）120 周 → 一時停止 5 周 → 閉じる。
        let mut read_at = 0u32;
        run_loop(
            || bits.get(),
            || paused.get(),
            || clock.get(),
            || {
                reads.set(reads.get() + 1);
                read_at += 1;
                let a = read_at as f32 * 0.07;
                Some(pt(
                    0.8 + 0.5 * a.cos(),
                    0.5 + 0.3 * a.sin(),
                    read_at % 40 > 20,
                ))
            },
            |_, _| *traces_out.borrow_mut() += 1,
            |_, _| *ripples_out.borrow_mut() += 1,
            || None,
            |_, _| {},
            |ms| {
                slept.borrow_mut().push(ms);
                clock.set(clock.get() + ms);
            },
            || {
                let n = iterations.get();
                iterations.set(n + 1);
                match n {
                    0 => {}
                    5 => bits.set(0b111),
                    125 => paused.set(true),
                    130 => {
                        paused.set(false);
                        bits.set(0);
                    }
                    _ => {}
                }
                if n == 140 {
                    return true;
                }
                false
            },
        );
        assert!(reads.get() > 100, "reads={}", reads.get());
        assert!(
            reads.get() < 125,
            "no read while closed or paused: {}",
            reads.get()
        );
        assert!(*traces_out.borrow() > 10);
        assert!(*ripples_out.borrow() > 0);
        // 閉じている間は 250、読んでいる間は 16 以下。
        let s = slept.borrow();
        assert!(s[..5].iter().all(|m| *m == 250));
        assert!(s[10..100].iter().all(|m| (1..=16).contains(m)));
    }

    #[test]
    fn gate_bits_decode() {
        let g = Gate::from_bits(0b101);
        assert!(g.open && !g.cursor && g.click);
        let g = Gate::from_bits(0);
        assert!(!g.open && !g.cursor && !g.click);
        assert!(
            Gate::from_bits(0b110)
                == Gate {
                    open: false,
                    cursor: true,
                    click: true
                }
        );
    }

    /// ライブの一致: A2 の合成の一点を、偽の読みで同じ刻みの時刻に返して `tick` を回した結果が
    /// `replay_trace` とビット単位で一致する（`tick` を 16ms ちょうどごとに呼ぶ条件）。
    #[test]
    fn live_matches_replay_bit_for_bit() {
        let bins = vec![
            PointerBin {
                timestamp: 2_000,
                moved: 4,
                buttons: 2,
                wheel: 0,
            },
            PointerBin {
                timestamp: 3_000,
                moved: 6,
                buttons: 0,
                wheel: 0,
            },
            PointerBin {
                timestamp: 4_000,
                moved: 5,
                buttons: 3,
                wheel: 0,
            },
            PointerBin {
                timestamp: 6_000,
                moved: 7,
                buttons: 1,
                wheel: 0,
            },
        ];
        let (seed, t0, t_end) = (11u64, 1_600u64, 9_600u64);
        let mut pts = synth_points(&bins, seed, t0, t_end).into_iter();
        let presses = synth_points(&bins, seed, t0, t_end)
            .iter()
            .filter(|p| p.left_down)
            .count();
        assert!(presses > 0);

        let mut d = PointerDriver::new();
        let mut checked = 0;
        let mut rip = 0;
        let mut now = t0;
        while now <= t_end {
            let mut read = || pts.next();
            let out = d.tick(now, ON, false, &mut read);
            rip += ripples(&out);
            for s in traces(&out) {
                let want = replay_trace(&bins, seed, t0, now);
                assert!(s.bits() == want.bits(), "differs at now={now}");
                checked += 1;
            }
            now += 16;
        }
        assert!(checked > 100, "checked={checked}");
        assert!(rip == presses, "ripples={rip} presses={presses}");
        let live = d.trace_state().expect("opened");
        assert!(live.bits() == replay_trace(&bins, seed, t0, t_end).bits());
        // 終わりの時点（最後の入力は 6 秒の行で、その後 8 秒は経っていない）で場は 0 でない。
        assert!(!live.is_zero());
    }

    /// 時刻 `t`（ms）のカーソルの位置（なめらかな円。呼び出しの時刻で読む）。
    fn circle_at(t: u64) -> Point {
        let a = t as f32 / 16.0 * 0.07;
        pt(0.8 + 0.5 * a.cos(), 0.5 + 0.3 * a.sin(), false)
    }

    /// 呼び出しの時刻の列に沿って走らせ、場の `bend` の最大値（全刻み・全マス）を返す。
    fn max_bend_over(times: &[u64]) -> f32 {
        let mut d = PointerDriver::new();
        let mut best = 0.0f32;
        for &now in times {
            let mut read = || Some(circle_at(now));
            d.tick(now, ON, false, &mut read);
            if let Some(st) = d.trace_state() {
                for c in &st.cells {
                    best = best.max(c[0].abs());
                }
            }
        }
        best
    }

    #[test]
    fn jittered_call_intervals_do_not_weaken_the_bend() {
        // 16ms ちょうどの呼び出しと、17・16・33ms を繰り返す（刻みを飛ばす呼び出しが混じる）呼び出しで、
        // 同じ動きに対する草を倒す量の最大値が大きく落ちない（飛ばした刻みで速さが 0 に戻らない）。
        let exact: Vec<u64> = (0..400u64).map(|k| 1_600 + k * 16).collect();
        let mut jittered = Vec::new();
        let mut t = 1_600u64;
        let pattern = [17u64, 16, 33];
        let mut i = 0;
        while t < 1_600 + 400 * 16 {
            jittered.push(t);
            t += pattern[i % 3];
            i += 1;
        }
        let a = max_bend_over(&exact);
        let b = max_bend_over(&jittered);
        assert!(a > 0.0);
        assert!(b >= a * 0.7, "exact={a} jittered={b}");
        // 17・16 の交互（刻みを飛ばさない・ときどき 2 回呼ぶ）でも同じ。
        let mut alt = Vec::new();
        let mut t = 1_600u64;
        let mut i = 0;
        while t < 1_600 + 400 * 16 {
            alt.push(t);
            t += if i % 2 == 0 { 17 } else { 16 };
            i += 1;
        }
        assert!(max_bend_over(&alt) >= a * 0.7);
    }

    #[test]
    fn the_wait_aims_at_the_next_grid_boundary() {
        let mut d = PointerDriver::new();
        let mut r = || Some(pt(0.5, 0.5, false));
        d.tick(1_600, ON, false, &mut r);
        // 読んでいる間は、次の 16ms の格子の境目までの残り（最低 1・最大 16）。
        for now in 1_600u64..1_700 {
            let w = d.next_wait_ms(now);
            assert!((1..=16).contains(&w));
            assert!((now + w).is_multiple_of(16), "now={now} w={w}");
        }
        assert!(d.next_wait_ms(1_615) == 1);
        assert!(d.next_wait_ms(1_616) == 16);
    }

    #[test]
    fn reading_resumes_when_the_clock_goes_back() {
        // 時刻が前より小さくなっても（格子が先に進んだままで読みが止まり続けない）、場を取り直して読み続ける。
        let mut calls = 0u32;
        let mut d = PointerDriver::new();
        let mut now = 50_000u64;
        let mut epoch_before = 0;
        for _ in 0..60 {
            let mut read = || {
                calls += 1;
                Some(circle_at(now))
            };
            d.tick(now, ON, false, &mut read);
            epoch_before = d.trace_state().map_or(0, |s| s.epoch);
            now += 16;
        }
        let calls_before = calls;
        // 時計が 40 秒戻る。
        let mut now = 10_000u64;
        let mut out_all = Vec::new();
        for _ in 0..60 {
            let mut read = || {
                calls += 1;
                Some(circle_at(now))
            };
            out_all.extend(d.tick(now, ON, false, &mut read));
            now += 16;
        }
        assert!(calls - calls_before >= 58, "reads={}", calls - calls_before);
        let st = d.trace_state().expect("opened");
        assert!(
            !st.is_zero(),
            "the field rises again after the clock went back"
        );
        assert!(
            st.epoch == epoch_before + 1,
            "a new epoch tells the window to clear"
        );
        // 戻った刻みで 0 の写しが 1 回出る（窓が前の場を消す）。
        let zeros: Vec<_> = traces(&out_all)
            .into_iter()
            .filter(|s| s.is_zero())
            .collect();
        assert!(zeros.len() == 1 && zeros[0].epoch == epoch_before + 1);
        // 押しっぱなしで時計が戻っても、波紋は出ない。
        assert!(ripples(&out_all) == 0);
    }

    #[test]
    fn a_perturbed_live_run_differs_from_replay() {
        // 陰性の対照: 読みを 1 点だけずらすと一致しない（一致のテストが空回りしていない）。
        let bins = vec![PointerBin {
            timestamp: 3_000,
            moved: 6,
            buttons: 0,
            wheel: 0,
        }];
        let (seed, t0, t_end) = (5u64, 1_600u64, 4_000u64);
        let mut pts: Vec<Point> = synth_points(&bins, seed, t0, t_end);
        pts[40].x += 0.05;
        let mut it = pts.into_iter();
        let mut d = PointerDriver::new();
        let mut now = t0;
        while now <= t_end {
            let mut read = || it.next();
            d.tick(now, ON, false, &mut read);
            now += 16;
        }
        let live = d.trace_state().expect("opened");
        assert!(live.bits() != replay_trace(&bins, seed, t0, t_end).bits());
    }

    // ---- 帯の近さ ----

    #[test]
    fn strip_near_boundaries() {
        // 帯（下端 0・高さ 14）の上は 10、80 点で 0
        assert_eq!(strip_near(true, 0.0, 0.0), 10);
        assert_eq!(strip_near(true, 14.0, 0.0), 10);
        assert_eq!(strip_near(true, 54.0, 0.0), 5);
        assert_eq!(strip_near(true, 94.0, 0.0), 0);
        assert_eq!(strip_near(true, 900.0, 0.0), 0);
        // 帯が Dock の上（下端 48）にあるとき: 帯の下端より下は下端からの距離
        assert_eq!(strip_near(true, 48.0, 48.0), 10);
        assert_eq!(strip_near(true, 55.0, 48.0), 10);
        assert_eq!(strip_near(true, 8.0, 48.0), 5);
        assert_eq!(strip_near(true, -32.0, 48.0), 0);
        assert_eq!(strip_near(true, 102.0, 48.0), 5);
        // 上端から 80 点ちょうどで 0、1 点手前は 1
        assert_eq!(strip_near(true, 48.0 + 14.0 + 80.0, 48.0), 0);
        assert_eq!(strip_near(true, 48.0 + 14.0 + 72.0, 48.0), 1);
        // カーソルを切っている・非有限は 0
        assert_eq!(strip_near(false, 0.0, 0.0), 0);
        assert_eq!(strip_near(true, f64::NAN, 0.0), 0);
        assert_eq!(strip_near(true, f64::INFINITY, 0.0), 0);
        assert_eq!(strip_near(true, 10.0, f64::NAN), 0);
        assert_eq!(strip_near(true, 10.0, f64::NEG_INFINITY), 0);
    }

    const SPOT: StripSpot = StripSpot {
        bottom_pt: 0.0,
        screen_h_pt: 900.0,
    };

    /// 主画面の高さ 900 点で、下端から `y_pt` 点の高さの一点（正準の箱の縦は下向き）。
    fn at_pt(y_pt: f32) -> Point {
        pt(0.8, 1.0 - y_pt / 900.0, false)
    }

    fn nears(out: &[PointerOut]) -> Vec<u8> {
        out.iter()
            .filter_map(|o| match o {
                PointerOut::StripNear(n) => Some(*n),
                _ => None,
            })
            .collect()
    }

    #[test]
    fn near_is_sent_only_when_it_changes_and_zero_once_when_cut() {
        let mut d = PointerDriver::new();
        let mut now = 1_600u64;
        let mut all = Vec::new();
        let mut run = |d: &mut PointerDriver, n: usize, y: f32, gate: Gate, paused: bool| {
            let mut v = Vec::new();
            for _ in 0..n {
                let mut r = || Some(at_pt(y));
                v.extend(nears(&d.tick_with_strip(
                    now,
                    gate,
                    paused,
                    Some(SPOT),
                    &mut r,
                )));
                now += 16;
            }
            v
        };
        // 開いた直後（最初の刻みは読まない）は 0 のまま何も出ない。帯の上で 10 が 1 回。
        all.push(run(&mut d, 20, 5.0, ON, false));
        assert_eq!(all[0], vec![10], "変わったときだけ");
        // 動かさなければ出ない。離れると変わるたびに出る。
        assert!(run(&mut d, 20, 5.0, ON, false).is_empty());
        assert_eq!(run(&mut d, 5, 54.0, ON, false), vec![5]);
        // カーソルを切ると 0 が 1 回だけ。
        let off = Gate {
            cursor: false,
            ..ON
        };
        assert_eq!(run(&mut d, 30, 54.0, off, false), vec![0]);
        // 戻すと再び出て、一時停止で 0 が 1 回、窓を閉じても出ない（すでに 0）。
        assert_eq!(run(&mut d, 20, 5.0, ON, false), vec![10]);
        assert_eq!(run(&mut d, 30, 5.0, ON, true), vec![0]);
        assert!(run(&mut d, 30, 5.0, Gate { open: false, ..ON }, false).is_empty());
        // 開いたまま 10 のときに窓を閉じると 0 が 1 回。
        assert_eq!(run(&mut d, 20, 5.0, ON, false), vec![10]);
        assert_eq!(
            run(&mut d, 30, 5.0, Gate { open: false, ..ON }, false),
            vec![0]
        );
    }

    #[test]
    fn near_is_zero_without_a_strip_or_when_the_point_is_lost() {
        let mut d = PointerDriver::new();
        let mut now = 1_600u64;
        let mut got = Vec::new();
        for _ in 0..40 {
            let mut r = || Some(at_pt(5.0));
            got.extend(nears(&d.tick_with_strip(now, ON, false, None, &mut r)));
            now += 16;
        }
        assert!(got.is_empty(), "帯が無ければ近さは 0 のまま");
        // 帯があって 10 → 一点が画面の外（読めない）で 0
        for _ in 0..10 {
            let mut r = || Some(at_pt(5.0));
            got.extend(nears(&d.tick_with_strip(
                now,
                ON,
                false,
                Some(SPOT),
                &mut r,
            )));
            now += 16;
        }
        for _ in 0..10 {
            let mut r = || None;
            got.extend(nears(&d.tick_with_strip(
                now,
                ON,
                false,
                Some(SPOT),
                &mut r,
            )));
            now += 16;
        }
        assert_eq!(got, vec![10, 0]);
    }

    /// 近さは場に触れない: 帯の口が有り・無しで、場と波紋の出来事がビット単位で同じ。
    #[test]
    fn near_never_changes_the_field_or_the_ripples() {
        let run = |strip: Option<StripSpot>| {
            let mut d = PointerDriver::new();
            let mut others = Vec::new();
            let mut states = Vec::new();
            for k in 0..400u64 {
                let a = k as f32 * 0.07;
                // 下の縁を行き来する（帯の有無で近さは大きく変わる）。押下もある。
                let mut r = || Some(pt(0.8 + 0.5 * a.cos(), 0.97 + 0.03 * a.sin(), k % 50 > 25));
                let gate = if k == 200 {
                    Gate {
                        cursor: false,
                        ..ON
                    }
                } else {
                    ON
                };
                for o in d.tick_with_strip(1_600 + k * 16, gate, k == 300, strip, &mut r) {
                    if !matches!(o, PointerOut::StripNear(_)) {
                        others.push(o);
                    }
                }
                states.push(d.trace_state());
            }
            (others, states)
        };
        let with = run(Some(SPOT));
        let without = run(None);
        assert!(with.0 == without.0, "出来事（場の写し・波紋）が同じ");
        assert!(with.0.iter().any(|o| matches!(o, PointerOut::Ripple(_))));
        assert_eq!(with.1.len(), without.1.len());
        for (a, b) in with.1.iter().zip(without.1.iter()) {
            match (a, b) {
                (Some(a), Some(b)) => assert_eq!(a.bits(), b.bits(), "場の値がビット単位で同じ"),
                (None, None) => {}
                _ => panic!("開き方が違う"),
            }
        }
    }

    /// `run_loop` の近さの送り口: 帯の置き場が有れば変わったときだけ呼ばれ、無ければ呼ばれない。
    #[test]
    fn run_loop_sends_near_only_with_a_strip() {
        use std::cell::{Cell, RefCell};
        let go = |with_strip: bool| {
            let clock = Cell::new(1_600u64);
            let n = Cell::new(0u32);
            let sent = RefCell::new(Vec::new());
            run_loop(
                || 0b111,
                || false,
                || clock.get(),
                || Some(at_pt(5.0)),
                |_, _| {},
                |_, _| {},
                || with_strip.then_some(SPOT),
                |v, _| sent.borrow_mut().push(v),
                |ms| clock.set(clock.get() + ms),
                || {
                    n.set(n.get() + 1);
                    n.get() > 60
                },
            );
            sent.into_inner()
        };
        assert_eq!(go(true), vec![10]);
        assert!(go(false).is_empty());
    }
}
