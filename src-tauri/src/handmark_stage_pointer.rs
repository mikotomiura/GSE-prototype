//! 手跡の背景の層へカーソルとクリックを渡す（spike・本線に入れない・ADR-040）。
//!
//! - 読みのスレッドは 16ms ごとに一点を読み（判断 7）、位置か左の押下が変わったときだけ窓へ送る。
//! - 入れ切り（トレイ・判断 5）のたびに世代を進め、新しい世代の状態を送る。窓は古い世代を捨てる（D4）。
//!   両方を切っている間は OS を読まない。
//! - 送る先は背景の窓だけ（`emit_to`）。イベント名はこの窓専用（D3 の他の窓への配送）。
//! - このファイルは記録・ファイル・ネットワーク・推定の道具を使わない。検査は `crate::handmark_stage_guard`。
//!   `.steering/20261021-handmark-stage-pointer/design.md` §1・§3。

use crate::input::handmark_pointer::{PointerReader, PointerSample, PointerUpdate};
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};

/// 背景の窓へポインタを知らせるイベント名。背景の窓のコードだけが受ける。
pub const POINTER_EVENT: &str = "handmark-stage-pointer";

/// 入れ切りと世代。
pub(crate) struct Switches {
    cursor: AtomicBool,
    click: AtomicBool,
    epoch: AtomicU64,
}

impl Switches {
    pub(crate) const fn new() -> Self {
        Self {
            cursor: AtomicBool::new(true),
            click: AtomicBool::new(true),
            epoch: AtomicU64::new(0),
        }
    }

    pub(crate) fn set_cursor(&self, on: bool) {
        if self.cursor.swap(on, Ordering::SeqCst) != on {
            self.epoch.fetch_add(1, Ordering::SeqCst);
        }
    }

    pub(crate) fn set_click(&self, on: bool) {
        if self.click.swap(on, Ordering::SeqCst) != on {
            self.epoch.fetch_add(1, Ordering::SeqCst);
        }
    }

    fn snapshot(&self) -> (u64, bool, bool) {
        (
            self.epoch.load(Ordering::SeqCst),
            self.cursor.load(Ordering::SeqCst),
            self.click.load(Ordering::SeqCst),
        )
    }
}

static SWITCHES: Switches = Switches::new();

pub fn set_cursor_on(on: bool) {
    SWITCHES.set_cursor(on);
}

pub fn set_click_on(on: bool) {
    SWITCHES.set_click(on);
}

pub fn cursor_on() -> bool {
    SWITCHES.snapshot().1
}

pub fn click_on() -> bool {
    SWITCHES.snapshot().2
}

/// 窓へ送る数だけの値。この型はこのファイルの外へ出さない。
#[derive(Clone, Copy, serde::Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct PointerPayload {
    epoch: u64,
    /// 読みのスレッドが始まってからのミリ秒（窓は遅れて届いたものを捨てるのに使う）。
    t_ms: f64,
    cursor_on: bool,
    click_on: bool,
    x: f64,
    y: f64,
    moved: bool,
    clicked: bool,
}

/// 入れ切りの状態だけを知らせる（位置を持たない）。
fn state_payload(epoch: u64, t_ms: f64, cursor_on: bool, click_on: bool) -> PointerPayload {
    PointerPayload {
        epoch,
        t_ms,
        cursor_on,
        click_on,
        x: 0.0,
        y: 0.0,
        moved: false,
        clicked: false,
    }
}

/// 変化を窓へ渡す値にする（ADR-040 D3 の「専用の関数」）。
fn update_payload(
    u: &PointerUpdate,
    epoch: u64,
    t_ms: f64,
    cursor_on: bool,
    click_on: bool,
) -> PointerPayload {
    PointerPayload {
        epoch,
        t_ms,
        cursor_on,
        click_on,
        x: u.x(),
        y: u.y(),
        moved: u.moved(),
        clicked: u.clicked(),
    }
}

/// 読みの 1 回分の処理。読む関数と送る関数を外から受ける（テストで偽物に替える）。
pub(crate) struct Forwarder {
    reader: PointerReader,
    epoch: Option<u64>,
}

impl Forwarder {
    pub(crate) const fn new() -> Self {
        Self {
            reader: PointerReader::new(),
            epoch: None,
        }
    }

    pub(crate) fn tick(
        &mut self,
        switches: &Switches,
        t_ms: f64,
        read: &mut dyn FnMut() -> PointerSample,
        send: &mut dyn FnMut(PointerPayload),
    ) {
        let (epoch, cursor_on, click_on) = switches.snapshot();
        if self.epoch != Some(epoch) {
            // 入れ切りが変わった: 前の点と押下を捨て、新しい世代の状態を先に送る。
            self.epoch = Some(epoch);
            self.reader.reset();
            send(state_payload(epoch, t_ms, cursor_on, click_on));
        }
        if !cursor_on && !click_on {
            // 両方を切っている間は取得しない。
            return;
        }
        if let Some(u) = self.reader.step(read(), cursor_on, click_on) {
            send(update_payload(&u, epoch, t_ms, cursor_on, click_on));
        }
    }
}

#[cfg(target_os = "macos")]
mod imp {
    use super::*;
    use std::time::{Duration, Instant};
    use tauri::{AppHandle, Emitter, Wry};

    /// 読む間隔（1 秒に約 60 回・判断 7）。
    const READ_EVERY: Duration = Duration::from_millis(16);

    /// 背景の窓が出ている間（`active` が true の間）だけ読み続けるスレッドを起こす。
    /// `synthetic` のときは OS を読まず、合成のポインタを使う（負荷の計測・人の手の入力を読まない）。
    pub fn start(
        app: AppHandle<Wry>,
        label: &'static str,
        active: &'static AtomicBool,
        synthetic: bool,
    ) -> std::io::Result<()> {
        std::thread::Builder::new()
            .name("gse-handmark-pointer".to_string())
            .spawn(move || {
                let t0 = Instant::now();
                let mut forwarder = Forwarder::new();
                let mut read = move || {
                    if synthetic {
                        crate::input::handmark_pointer::synthetic_sample(
                            t0.elapsed().as_millis() as u64
                        )
                    } else {
                        crate::input::handmark_pointer_macos::read()
                    }
                };
                let mut send = |p: PointerPayload| {
                    // 送れなくても背景が動かないだけ（値をどこにも残さない）。
                    let _ = app.emit_to(label, POINTER_EVENT, p);
                };
                while active.load(Ordering::Acquire) {
                    let t_ms = t0.elapsed().as_secs_f64() * 1_000.0;
                    forwarder.tick(&SWITCHES, t_ms, &mut read, &mut send);
                    std::thread::sleep(READ_EVERY);
                }
            })
            .map(|_| ())
    }
}

#[cfg(target_os = "macos")]
pub use imp::start;

/// 検査が型の名前を実行時に得るための口（検査のファイルに名前を書かない）。
#[cfg(test)]
pub(crate) fn payload_type_name() -> &'static str {
    std::any::type_name::<PointerPayload>()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::handmark_pointer::synthetic_sample;

    fn run(
        fw: &mut Forwarder,
        sw: &Switches,
        from: u64,
        ticks: u64,
        reads: &mut u32,
        out: &mut Vec<PointerPayload>,
    ) {
        for k in from..from + ticks {
            let mut read = || {
                *reads += 1;
                synthetic_sample(k * 16)
            };
            let mut send = |p: PointerPayload| out.push(p);
            fw.tick(sw, (k * 16) as f64, &mut read, &mut send);
        }
    }

    #[test]
    fn the_first_tick_sends_the_state_and_then_only_changes() {
        let sw = Switches::new();
        let mut fw = Forwarder::new();
        let (mut reads, mut out) = (0, Vec::new());
        run(&mut fw, &sw, 0, 260, &mut reads, &mut out);
        assert_eq!(reads, 260);
        assert!(!out[0].moved && !out[0].clicked && out[0].epoch == 0);
        assert_eq!(out.iter().filter(|p| p.clicked).count(), 2);
    }

    #[test]
    fn nothing_is_read_while_both_inputs_are_off() {
        let sw = Switches::new();
        let mut fw = Forwarder::new();
        let (mut reads, mut out) = (0, Vec::new());
        run(&mut fw, &sw, 0, 10, &mut reads, &mut out);
        sw.set_cursor(false);
        sw.set_click(false);
        let (before_reads, before_out) = (reads, out.len());
        run(&mut fw, &sw, 10, 300, &mut reads, &mut out);
        // 取得を止める（読まない）。切った状態を 1 回だけ知らせ、位置は送らない。
        assert_eq!(reads, before_reads);
        assert_eq!(out.len(), before_out + 1);
        let last = out[out.len() - 1];
        assert!(!last.cursor_on && !last.click_on && last.x == 0.0 && last.y == 0.0);
        assert_eq!(last.epoch, 2);
    }

    #[test]
    fn switching_resets_the_reader_and_advances_the_epoch() {
        let sw = Switches::new();
        let mut fw = Forwarder::new();
        let (mut reads, mut out) = (0, Vec::new());
        run(&mut fw, &sw, 0, 5, &mut reads, &mut out);
        sw.set_cursor(false);
        sw.set_cursor(true);
        // 同じ値を入れても世代は進まない
        sw.set_click(true);
        out.clear();
        run(&mut fw, &sw, 5, 1, &mut reads, &mut out);
        // 状態だけを送り、入れ直した最初の一点では動いたことにしない
        assert_eq!(out.len(), 1);
        assert_eq!(out[0].epoch, 2);
        assert!(!out[0].moved && out[0].cursor_on);
        run(&mut fw, &sw, 6, 1, &mut reads, &mut out);
        assert!(out[1].moved && out[1].epoch == 2);
    }
}
