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

/// 窓へ場を送る間隔（ms）。
const TRACE_SEND_MS: u64 = 33;
/// 動いている間の待ち（ms）。
const WAIT_ACTIVE_MS: u64 = STEP_MS;
/// 止まっている間の待ち（ms）。
const WAIT_IDLE_MS: u64 = 250;

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

/// ポインタの駆動役の出来事。行き先は窓だけ。
#[derive(Clone, PartialEq)]
pub enum PointerOut {
    /// 場の写し（`TraceState::is_zero` なら「止まった」の知らせ）。
    Trace(Box<TraceState>),
    /// 押下が始まった位置（波紋の種）。
    Ripple(RipplePoint),
}

/// ポインタのスレッドの駆動役。
pub struct PointerDriver {
    field: Option<TraceField>,
    /// 前回の `(open, cursor, click, paused)`。
    key: (bool, bool, bool, bool),
    last_trace_ms: u64,
    /// 最後に出した写しが全部 0 だった。
    sent_zero: bool,
    /// 実効の入れ切りがある（読んでいる）。
    hot: bool,
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
            sent_zero: true,
            hot: false,
        }
    }

    /// 次の `tick` までの待ちの目安（ms）。実効の入れ切りがある（窓が開いていて・一時停止でなく・
    /// カーソルかクリックが入っている）間は止まっていても常に 16。250 は読まない間だけ。
    /// 止まっている間に延ばすと、次の短いクリックを取りこぼす（補訂 1 の項目 1 は 16ms ごとの読み）。
    pub fn next_wait_ms(&self) -> u64 {
        if self.hot {
            WAIT_ACTIVE_MS
        } else {
            WAIT_IDLE_MS
        }
    }

    /// いまの場（まだ開いていなければ `None`）。
    pub fn trace_state(&self) -> Option<TraceState> {
        self.field.as_ref().map(TraceField::state)
    }

    /// 1 回の呼び出し。`now_ms` は UTC の ms、`read` は一点を 1 回読む口。
    ///
    /// 開いていない・一時停止・カーソルもクリックも切れている間は `read` を呼ばない。
    pub fn tick(
        &mut self,
        now_ms: u64,
        gate: Gate,
        paused: bool,
        read: &mut dyn FnMut() -> Option<Point>,
    ) -> Vec<PointerOut> {
        let mut out = Vec::new();
        let eff_open = gate.open && !paused;
        let reading = eff_open && (gate.cursor || gate.click);

        let mut fresh = false;
        if eff_open && self.field.is_none() {
            self.field = Some(TraceField::new(now_ms));
            fresh = true;
        }
        let key = (gate.open, gate.cursor, gate.click, paused);
        let changed = key != self.key;
        self.key = key;

        let Some(field) = self.field.as_mut() else {
            self.hot = false;
            return out;
        };

        if changed {
            if !fresh {
                field.reset();
            }
            out.push(PointerOut::Trace(Box::new(field.state())));
            self.last_trace_ms = now_ms;
            self.sent_zero = true;
        }

        if reading {
            let target = now_ms / STEP_MS * STEP_MS;
            if target.saturating_sub(field.grid_t()) >= STEP_MS {
                field.advance_to(target - STEP_MS);
                let sample = read();
                let ripple = field.step(Step {
                    sample,
                    cursor_on: gate.cursor,
                    click_on: gate.click,
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
        out
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
                PointerOut::Ripple(_) => None,
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
                assert!(d.next_wait_ms() == 250);
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
    fn trace_goes_out_every_33ms_while_nonzero_and_stops_after_one_zero() {
        let mut d = PointerDriver::new();
        let out = drive_circle(&mut d, 0, 90, ON);
        let moving = traces(&out).len();
        // 90 刻み（約 1.4 秒）で 33ms ごと（16ms の刻みでは 3 刻みに 1 回）。
        assert!((25..=35).contains(&moving), "{moving}");
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
        assert!(d.next_wait_ms() == 16);
    }

    #[test]
    fn wait_is_16_while_reading_even_when_still_and_250_only_when_not_reading() {
        let mut d = PointerDriver::new();
        drive_circle(&mut d, 0, 30, ON);
        assert!(d.next_wait_ms() == 16);
        // 止まって 8 秒を過ぎ、場が 0 になっても、入っている間は 16。
        let mut now = 1_600 + 30 * 16;
        for _ in 0..1_000 {
            let mut r = || Some(pt(0.5, 0.5, false));
            d.tick(now, ON, false, &mut r);
            assert!(d.next_wait_ms() == 16, "now={now}");
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
            assert!(d.next_wait_ms() == 16);
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
            assert!(d.next_wait_ms() == 250);
            now += 16;
        }
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
        assert!(!live.is_zero() || t_end > 6_000);
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
}
