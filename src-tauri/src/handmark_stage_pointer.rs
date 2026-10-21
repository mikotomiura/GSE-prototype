//! 手跡の背景の層へカーソル・クリック・ホイールを渡す（spike・本線に入れない・ADR-040）。
//!
//! - 読みのスレッドは 16ms ごとにカーソルの一点を読み（判断 7）、位置か左の押下が変わったとき、
//!   またはホイールが回されたときだけ窓へ送る。
//! - ホイールは macOS の tap（`input/handmark_wheel_macos.rs`・判断 9）が数えた量を 16ms ごとに受け取る。
//! - 入れ切り（トレイ・判断 5）のたびに世代を進め、新しい世代の状態を送る。窓は古い世代を捨てる（D4）。
//!   カーソルとクリックを両方切っている間は OS の位置を読まず、ホイールを切っている間は tap を作らない。
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
    wheel: AtomicBool,
    epoch: AtomicU64,
}

/// ある時点の入れ切りと世代。
#[derive(Clone, Copy, PartialEq)]
struct State {
    epoch: u64,
    cursor: bool,
    click: bool,
    wheel: bool,
}

impl Switches {
    pub(crate) const fn new() -> Self {
        Self {
            cursor: AtomicBool::new(true),
            click: AtomicBool::new(true),
            wheel: AtomicBool::new(true),
            epoch: AtomicU64::new(0),
        }
    }

    fn set(&self, flag: &AtomicBool, on: bool) {
        if flag.swap(on, Ordering::SeqCst) != on {
            self.epoch.fetch_add(1, Ordering::SeqCst);
        }
    }

    pub(crate) fn set_cursor(&self, on: bool) {
        self.set(&self.cursor, on);
    }

    pub(crate) fn set_click(&self, on: bool) {
        self.set(&self.click, on);
    }

    pub(crate) fn set_wheel(&self, on: bool) {
        self.set(&self.wheel, on);
    }

    fn snapshot(&self) -> State {
        State {
            epoch: self.epoch.load(Ordering::SeqCst),
            cursor: self.cursor.load(Ordering::SeqCst),
            click: self.click.load(Ordering::SeqCst),
            wheel: self.wheel.load(Ordering::SeqCst),
        }
    }
}

static SWITCHES: Switches = Switches::new();

pub fn set_cursor_on(on: bool) {
    SWITCHES.set_cursor(on);
}

pub fn set_click_on(on: bool) {
    SWITCHES.set_click(on);
}

pub fn set_wheel_on(on: bool) {
    SWITCHES.set_wheel(on);
}

pub fn cursor_on() -> bool {
    SWITCHES.snapshot().cursor
}

pub fn click_on() -> bool {
    SWITCHES.snapshot().click
}

pub fn wheel_on() -> bool {
    SWITCHES.snapshot().wheel
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
    wheel_on: bool,
    x: f64,
    y: f64,
    moved: bool,
    clicked: bool,
    /// 前の送りから回した量（1 回ぶんを 1・画面を下へ送る向きを正）。
    wheel: f64,
}

/// 窓へ渡す値にする（ADR-040 D3 の「専用の関数」）。`u` が無ければ入れ切りの状態とホイールだけ。
fn payload(s: State, t_ms: f64, u: Option<&PointerUpdate>, wheel: f64) -> PointerPayload {
    PointerPayload {
        epoch: s.epoch,
        t_ms,
        cursor_on: s.cursor,
        click_on: s.click,
        wheel_on: s.wheel,
        x: u.map_or(0.0, |u| u.x()),
        y: u.map_or(0.0, |u| u.y()),
        moved: u.is_some_and(|u| u.moved()),
        clicked: u.is_some_and(|u| u.clicked()),
        wheel,
    }
}

/// 読みの 1 回分の処理に渡す口（テストで偽物に替える）。
pub(crate) struct Io<'a> {
    pub(crate) read: &'a mut dyn FnMut() -> PointerSample,
    /// 前に呼ばれてから回した量を返し、0 に戻す。
    pub(crate) take_wheel: &'a mut dyn FnMut() -> f64,
    /// 溜まった量を捨てる（ホイールを切ったとき）。
    pub(crate) discard_wheel: &'a mut dyn FnMut(),
    pub(crate) send: &'a mut dyn FnMut(PointerPayload),
}

/// 読みの 1 回分の処理。
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

    pub(crate) fn tick(&mut self, switches: &Switches, t_ms: f64, io: &mut Io<'_>) {
        let s = switches.snapshot();
        if self.epoch != Some(s.epoch) {
            // 入れ切りが変わった: 前の点と押下と溜まった回した量を捨て、新しい世代の状態を先に送る。
            self.epoch = Some(s.epoch);
            self.reader.reset();
            (io.discard_wheel)();
            (io.send)(payload(s, t_ms, None, 0.0));
        }
        let update = if s.cursor || s.click {
            self.reader.step((io.read)(), s.cursor, s.click)
        } else {
            // 両方を切っている間は取得しない。
            None
        };
        let wheel = if s.wheel { (io.take_wheel)() } else { 0.0 };
        if update.is_some() || wheel != 0.0 {
            (io.send)(payload(s, t_ms, update.as_ref(), wheel));
        }
    }
}

#[cfg(target_os = "macos")]
mod imp {
    use super::*;
    use crate::input::handmark_wheel_macos as wheel;
    use std::time::{Duration, Instant};
    use tauri::{AppHandle, Emitter, Wry};

    /// 読む間隔（1 秒に約 60 回・判断 7）。
    const READ_EVERY: Duration = Duration::from_millis(16);

    /// 背景の窓が出ているか（`start` が受けた旗）。ホイールの tap のスレッドが見る。
    static STAGE_ACTIVE: std::sync::OnceLock<&'static AtomicBool> = std::sync::OnceLock::new();

    /// ホイールの tap を動かしておくか（背景の窓が出ていて、ホイールを入れている間）。
    fn wheel_wanted() -> bool {
        STAGE_ACTIVE
            .get()
            .is_some_and(|a| a.load(Ordering::Acquire))
            && wheel_on()
    }

    /// 背景の窓が出ている間（`active` が true の間）だけ読み続けるスレッドを起こす。
    /// `synthetic` のときは OS を読まず（tap も作らず）、合成のポインタと 3 秒ごとの 1 回ぶんのホイールを使う
    /// （負荷の計測・人の手の入力を読まない）。
    pub fn start(
        app: AppHandle<Wry>,
        label: &'static str,
        active: &'static AtomicBool,
        synthetic: bool,
    ) -> std::io::Result<()> {
        let _ = STAGE_ACTIVE.set(active);
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
                let mut take_wheel = move || {
                    if synthetic {
                        let t = t0.elapsed().as_millis() as u64 % 3_000;
                        if t < 16 {
                            1.0
                        } else {
                            0.0
                        }
                    } else {
                        wheel::take()
                    }
                };
                let mut discard_wheel = wheel::discard;
                let mut send = |p: PointerPayload| {
                    // 送れなくても背景が動かないだけ（値をどこにも残さない）。
                    let _ = app.emit_to(label, POINTER_EVENT, p);
                };
                while active.load(Ordering::Acquire) {
                    if !synthetic && wheel_wanted() {
                        wheel::ensure_running(wheel_wanted);
                    }
                    let t_ms = t0.elapsed().as_secs_f64() * 1_000.0;
                    let mut io = Io {
                        read: &mut read,
                        take_wheel: &mut take_wheel,
                        discard_wheel: &mut discard_wheel,
                        send: &mut send,
                    };
                    forwarder.tick(&SWITCHES, t_ms, &mut io);
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

    #[derive(Default)]
    struct Counts {
        reads: u32,
        wheel_takes: u32,
        discards: u32,
        out: Vec<PointerPayload>,
    }

    /// `wheel_every` 回に 1 回、1 回ぶん回したことにする。
    fn run(
        fw: &mut Forwarder,
        sw: &Switches,
        from: u64,
        ticks: u64,
        wheel_every: u64,
        c: &mut Counts,
    ) {
        for k in from..from + ticks {
            let Counts {
                reads,
                wheel_takes,
                discards,
                out,
            } = c;
            let mut read = || {
                *reads += 1;
                synthetic_sample(k * 16)
            };
            let mut take_wheel = || {
                *wheel_takes += 1;
                if wheel_every > 0 && k % wheel_every == 0 {
                    1.0
                } else {
                    0.0
                }
            };
            let mut discard_wheel = || *discards += 1;
            let mut send = |p: PointerPayload| out.push(p);
            let mut io = Io {
                read: &mut read,
                take_wheel: &mut take_wheel,
                discard_wheel: &mut discard_wheel,
                send: &mut send,
            };
            fw.tick(sw, (k * 16) as f64, &mut io);
        }
    }

    #[test]
    fn the_first_tick_sends_the_state_and_then_only_changes() {
        let sw = Switches::new();
        let mut fw = Forwarder::new();
        let mut c = Counts::default();
        run(&mut fw, &sw, 0, 260, 0, &mut c);
        assert_eq!(c.reads, 260);
        assert!(!c.out[0].moved && !c.out[0].clicked && c.out[0].epoch == 0);
        assert_eq!(c.out.iter().filter(|p| p.clicked).count(), 2);
    }

    #[test]
    fn nothing_is_read_while_the_inputs_are_off() {
        let sw = Switches::new();
        let mut fw = Forwarder::new();
        let mut c = Counts::default();
        run(&mut fw, &sw, 0, 10, 5, &mut c);
        sw.set_cursor(false);
        sw.set_click(false);
        sw.set_wheel(false);
        let (reads, takes, sent) = (c.reads, c.wheel_takes, c.out.len());
        run(&mut fw, &sw, 10, 300, 5, &mut c);
        // 取得を止める（読まない・回した量も受け取らない）。切った状態を 1 回だけ知らせ、位置は送らない。
        assert_eq!(c.reads, reads);
        assert_eq!(c.wheel_takes, takes);
        assert_eq!(c.out.len(), sent + 1);
        let last = c.out[c.out.len() - 1];
        assert!(!last.cursor_on && !last.click_on && !last.wheel_on);
        assert!(last.x == 0.0 && last.y == 0.0 && last.wheel == 0.0);
        assert_eq!(last.epoch, 3);
    }

    #[test]
    fn the_wheel_is_sent_only_when_turned() {
        let sw = Switches::new();
        sw.set_cursor(false);
        sw.set_click(false);
        let mut fw = Forwarder::new();
        let mut c = Counts::default();
        run(&mut fw, &sw, 1, 100, 10, &mut c);
        // 最初の状態 1 回と、10 回に 1 回の回した量
        assert_eq!(c.out.len(), 1 + 10);
        assert!(c.out[1..].iter().all(|p| p.wheel == 1.0 && !p.moved));
        assert_eq!(c.reads, 0);
    }

    #[test]
    fn switching_discards_and_advances_the_epoch() {
        let sw = Switches::new();
        let mut fw = Forwarder::new();
        let mut c = Counts::default();
        run(&mut fw, &sw, 0, 5, 0, &mut c);
        assert_eq!(c.discards, 1);
        sw.set_cursor(false);
        sw.set_cursor(true);
        // 同じ値を入れても世代は進まない
        sw.set_click(true);
        sw.set_wheel(true);
        c.out.clear();
        run(&mut fw, &sw, 5, 1, 0, &mut c);
        // 状態だけを送り、入れ直した最初の一点では動いたことにしない。溜まった回した量は捨てる
        assert_eq!(c.discards, 2);
        assert_eq!(c.out.len(), 1);
        assert_eq!(c.out[0].epoch, 2);
        assert!(!c.out[0].moved && c.out[0].cursor_on);
        run(&mut fw, &sw, 6, 1, 0, &mut c);
        assert!(c.out[1].moved && c.out[1].epoch == 2);
    }
}
