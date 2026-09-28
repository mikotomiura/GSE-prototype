//! ime-observation-logger — IME 観測の単体ロガー（核）。
//!
//! GSE の変換セッション状態機械（`input/ime_compose.rs` / `ime_cloak.rs` / `ime_mode.rs`）を**逐語コピー**で
//! 使い、Atomic を読んで `ime_shadow` 行を、ドライバが送る打鍵から `key` 行を、`obs/1` で書き出す。
//! ⚠️ content-free: `key` は 14 種の category だけ・`ime_shadow` は数（`dwell_ms` / `nav` / `abandon`）だけ。
//!
//! 使い方: `ime-observation-logger --out <path> [--duration-s <n>]` / `ime-observation-logger --selftest [--out <path>]`
//! OS ドライバ（打鍵の取得）は `driver_macos.rs` / `driver_windows.rs`（後続の issue）。

// ★ GSE の Windows の `is_observed_key`（`hook_windows.rs`）は本体の先頭で `crate::analysis::key_gate` を呼ぶ。
//   `key_gate.rs` を**ファイルごとの逐語コピー**で置き、ドライバ（issue 013 / 014）がそれを逐語の抜粋から呼べるようにする
//   （011 の追補）。macOS のドライバは使わないので `dead_code` を許す。
#[allow(dead_code)]
mod analysis;
mod driver_api;
#[cfg(target_os = "macos")]
mod driver_macos;
#[cfg(windows)]
mod driver_windows;
mod input;
#[allow(dead_code)]
mod key_category;

use std::fs::OpenOptions;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering};
use std::sync::mpsc::{self, RecvTimeoutError};
use std::sync::Arc;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use sha2::{Digest, Sha256};

use driver_api::DriverCtx;
use input::hook::{
    IME_ACTIVE, IME_CANDIDATE_NAV_COUNT, IME_COMPOSITION_START_MS, IME_SHADOW_ABANDON,
    IME_SHADOW_DWELL_MS, IME_SHADOW_READY,
};
use input::ime_cloak::MONITOR_SAFETY_VALVE_MS;
use input::ime_compose::{self, Chord};
use key_category::KeyCategory;

const LOGGER_VERSION: &str = env!("CARGO_PKG_VERSION");
/// `obs/1` の `os` は macos / windows の 2 値。この 2 つ以外では核は動かない（`start_driver` が
/// エラーで止まる）。⚠️ Linux 等で誤って "windows" を名乗らない（issue 011 merge ゲートレビュー item 9）。
const OS_NAME: &str = if cfg!(target_os = "macos") {
    "macos"
} else if cfg!(windows) {
    "windows"
} else {
    "unsupported"
};
/// `meta` 行の `manifest_sha256` の元。核の manifest（ドライバの manifest は含まない）。
const MANIFEST: &[u8] = include_bytes!("../manifest.json");
/// GSE の IME Monitor スレッドのポーリング間隔（`lib.rs` の `thread::sleep(100ms)`）。
const POLL_MS: u64 = 100;

// ---------------------------------------------------------------------------
// 行の書き出し（obs/1）。区切りに空白を入れない・エスケープを使わない（FORMATS.md）。
// ---------------------------------------------------------------------------

fn meta_line() -> String {
    let mut hex = String::with_capacity(64);
    for b in Sha256::digest(MANIFEST) {
        hex.push_str(&format!("{b:02x}"));
    }
    // ⚠️ capabilities は GSE の `capabilities.rs` の宣言と同じ群: `key` = unconditional / `ime_shadow` = config_gated。
    format!(
        r#"{{"type":"meta","format":"obs/1","os":"{OS_NAME}","logger_version":"{LOGGER_VERSION}","manifest_sha256":"{hex}","capabilities":{{"unconditional":["key"],"threshold_gated":[],"config_gated":["ime_shadow"]}}}}"#
    )
}

fn key_line(t: u64, category: KeyCategory, press: bool) -> String {
    format!(
        r#"{{"type":"key","t":{t},"category":"{}","press":{press}}}"#,
        category.as_str()
    )
}

fn shadow_line(t: u64, dwell_ms: u64, nav: u32, abandon: bool) -> String {
    format!(
        r#"{{"type":"ime_shadow","t":{t},"dwell_ms":{dwell_ms},"nav":{nav},"abandon":{abandon}}}"#
    )
}

/// 1 行 = 1 回の書き込み＋flush（強制終了されても書いた行は残る）。
fn write_line<W: Write>(out: &mut W, line: &str) -> Result<(), String> {
    writeln!(out, "{line}")
        .and_then(|()| out.flush())
        .map_err(|e| format!("書き出しに失敗: {e}"))
}

fn wall_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}

// ---------------------------------------------------------------------------
// 監視ループが読み書きする Atomic（issue 011 merge ゲートレビュー item 7）。
//
// 生産では実体はシム `input::hook` の Atomic そのもの（[`ShadowAtomics::real`]）。テストでは
// `Box::leak` で作った独立の Atomic（[`ShadowAtomics::fresh_for_test`]）を使い、コピーした
// 状態機械の単体テスト（同じ実 Atomic を並列に読み書きする）と競合しない。
// ---------------------------------------------------------------------------

#[derive(Clone, Copy)]
struct ShadowAtomics {
    /// 候補窓（変換セッション）の生死。safety valve が下ろす対象は**これ**（GSE と同じ `IME_ACTIVE`）。
    active: &'static AtomicBool,
    ready: &'static AtomicBool,
    dwell_ms: &'static AtomicU64,
    nav: &'static AtomicU32,
    abandon: &'static AtomicBool,
    composition_start_ms: &'static AtomicU64,
}

impl ShadowAtomics {
    /// 生産で使う実体（シム `input::hook` の Atomic そのもの）。
    fn real() -> Self {
        Self {
            active: &IME_ACTIVE,
            ready: &IME_SHADOW_READY,
            dwell_ms: &IME_SHADOW_DWELL_MS,
            nav: &IME_CANDIDATE_NAV_COUNT,
            abandon: &IME_SHADOW_ABANDON,
            composition_start_ms: &IME_COMPOSITION_START_MS,
        }
    }

    /// テスト用: 実 static とは無関係な Atomic（`Box::leak` するだけで `'static` になる・
    /// シムの `IME_ACTIVE` 等とは別のメモリ）。並列に走る他のテストと値を共有しない。
    #[cfg(test)]
    fn fresh_for_test() -> Self {
        Self {
            active: Box::leak(Box::new(AtomicBool::new(false))),
            ready: Box::leak(Box::new(AtomicBool::new(false))),
            dwell_ms: Box::leak(Box::new(AtomicU64::new(0))),
            nav: Box::leak(Box::new(AtomicU32::new(0))),
            abandon: Box::leak(Box::new(AtomicBool::new(false))),
            composition_start_ms: Box::leak(Box::new(AtomicU64::new(0))),
        }
    }
}

fn default_candidate_observer() -> Box<dyn FnMut() -> bool + Send> {
    // ⚠️ 既定 = `IME_ACTIVE` を直接読む（旧実装と同じ）。ドライバが観測関数を返さない場合や、
    // selftest（ドライバを使わない）はこれを使う。Windows ドライバ（013 / 014）は
    // `ImeMonitor::is_candidate_window_open()` 相当（WinEvent・EnumWindows・UIA の OR ＋
    // stale リセット）をここに差し込める（`driver_api.rs` の契約）。
    Box::new(|| IME_ACTIVE.load(Ordering::Acquire))
}

// ---------------------------------------------------------------------------
// 監視ループ（ime_shadow 行）。
// 一次: GSE `src-tauri/src/lib.rs` の `emit_ime_shadow` と IME Monitor スレッド（`should_drain_ready` を使う判断の順序）の
// **G1（`g1_mode()`）を除いた写し**。⚠️ `t` は drain した時刻。⚠️ Stale 経路 / active→false 遷移経路は Windows 限定。
// 差分: 「候補窓が開いているか」の判定は既定で `IME_ACTIVE` を直接読むが、ドライバは
// `DriverHandle.candidate_window_observer` でより強い判定（GSE の `is_candidate_window_open()` 相当）を
// 差し込める（issue 011 merge ゲートレビュー item 1・`driver_api.rs` の契約）。
// ---------------------------------------------------------------------------

fn emit_ime_shadow<W: Write>(
    atomics: &ShadowAtomics,
    out: &mut W,
    t: u64,
    is_windows: bool,
) -> Result<(), String> {
    if atomics.ready.swap(false, Ordering::AcqRel) {
        // 正常経路: 要約は書き込み側が計算済み。
        let dwell_ms = atomics.dwell_ms.swap(0, Ordering::Relaxed);
        let nav = atomics.nav.swap(0, Ordering::Relaxed);
        let abandon = atomics.abandon.swap(false, Ordering::Relaxed);
        return write_line(out, &shadow_line(t, dwell_ms, nav, abandon));
    }
    // ⚠️ Stale 経路は Windows 限定（macOS では途中の偽の行が出てセッションが壊れる）。
    if is_windows {
        let start = atomics.composition_start_ms.swap(0, Ordering::Relaxed);
        if start > 0 {
            let dwell_ms = t.saturating_sub(start);
            let nav = atomics.nav.swap(0, Ordering::Relaxed);
            let abandon = atomics.abandon.swap(false, Ordering::Relaxed);
            return write_line(out, &shadow_line(t, dwell_ms, nav, abandon));
        }
    }
    Ok(())
}

struct Monitor {
    is_windows: bool,
    last_active: Option<bool>,
    active_since: Option<Instant>,
    next_poll: Instant,
    /// 「候補窓が開いているか」の観測関数（既定 = `IME_ACTIVE` の読み取り。`driver_api.rs` 参照）。
    observe_candidate: Box<dyn FnMut() -> bool + Send>,
    atomics: ShadowAtomics,
}

impl Monitor {
    fn new(
        now: Instant,
        is_windows: bool,
        observe_candidate: Box<dyn FnMut() -> bool + Send>,
    ) -> Self {
        Self {
            is_windows,
            last_active: None,
            active_since: None,
            next_poll: now,
            observe_candidate,
            atomics: ShadowAtomics::real(),
        }
    }

    /// テスト用: Atomic も注入する（実 static と競合しない・issue 011 merge ゲートレビュー item 7）。
    #[cfg(test)]
    fn new_for_test(
        now: Instant,
        is_windows: bool,
        observe_candidate: Box<dyn FnMut() -> bool + Send>,
        atomics: ShadowAtomics,
    ) -> Self {
        Self {
            is_windows,
            last_active: None,
            active_since: None,
            next_poll: now,
            observe_candidate,
            atomics,
        }
    }

    /// GSE の IME Monitor スレッドの 1 周（同じ判断・同じ順序）。`POLL_MS` に 1 回だけ動く。
    /// `now` は経過の測定用・`ts_ms` は drain の壁時計（`ime_shadow` の `t`）。
    fn poll<W: Write>(&mut self, now: Instant, ts_ms: u64, out: &mut W) -> Result<(), String> {
        if now < self.next_poll {
            return Ok(());
        }
        self.next_poll = now + Duration::from_millis(POLL_MS);
        self.run_cycle(now, ts_ms, out)
    }

    /// スケジュールを無視して 1 周だけ強制的に回す。★ ループの終了直前に呼び、直近の `poll` 以降に
    /// 届いた `IME_SHADOW_READY` の取りこぼしを防ぐ（issue 011 merge ゲートレビュー item 4）。
    fn force_poll<W: Write>(
        &mut self,
        now: Instant,
        ts_ms: u64,
        out: &mut W,
    ) -> Result<(), String> {
        self.run_cycle(now, ts_ms, out)
    }

    fn run_cycle<W: Write>(&mut self, now: Instant, ts_ms: u64, out: &mut W) -> Result<(), String> {
        let active = (self.observe_candidate)();

        // Safety valve: 窓の閉じを取りこぼして候補窓が開きっぱなしなら stale とみなして下ろす。
        if active {
            let since = *self.active_since.get_or_insert(now);
            if now.duration_since(since) > Duration::from_millis(MONITOR_SAFETY_VALVE_MS) {
                tracing::warn!(
                    valve_ms = MONITOR_SAFETY_VALVE_MS,
                    "candidate window stale — auto-resetting"
                );
                self.atomics.active.store(false, Ordering::Release);
                self.active_since = None;
                self.last_active = Some(false);
                if self.is_windows {
                    emit_ime_shadow(&self.atomics, out, ts_ms, true)?;
                }
                return Ok(());
            }
        } else {
            self.active_since = None;
        }

        // active → false の遷移（Windows 限定）。
        if self.last_active.is_none_or(|prev| prev != active) {
            let was_active = self.last_active.unwrap_or(false);
            self.last_active = Some(active);
            if self.is_windows && was_active && !active {
                emit_ime_shadow(&self.atomics, out, ts_ms, true)?;
            }
        }

        // `IME_SHADOW_READY` の直接ポーリング（macOS で ime_shadow が出るのはこの経路だけ）。
        let ready = self.atomics.ready.load(Ordering::Acquire);
        if ime_compose::should_drain_ready(ready, active, self.is_windows) {
            emit_ime_shadow(&self.atomics, out, ts_ms, self.is_windows)?;
        }
        Ok(())
    }
}

// ---------------------------------------------------------------------------
// ドライバの差し込み（各 OS の中身は後続の issue）。
// ---------------------------------------------------------------------------

#[cfg(target_os = "macos")]
fn start_driver(ctx: DriverCtx) -> Result<driver_api::DriverHandle, String> {
    driver_macos::start(ctx)
}
#[cfg(windows)]
fn start_driver(ctx: DriverCtx) -> Result<driver_api::DriverHandle, String> {
    driver_windows::start(ctx)
}
#[cfg(not(any(target_os = "macos", windows)))]
fn start_driver(_ctx: DriverCtx) -> Result<driver_api::DriverHandle, String> {
    Err("この OS にはドライバが無い（macOS / Windows のみ）".to_string())
}

fn run(out_path: &Path, duration: Option<Duration>) -> Result<(), String> {
    let (tx, rx) = mpsc::channel();
    let stop = Arc::new(AtomicBool::new(false));
    let handle = start_driver(DriverCtx {
        keys: tx,
        stop: Arc::clone(&stop),
    })
    .map_err(|e| format!("ドライバを起動できない: {e}"))?;

    // ⚠️★ 出力は「ドライバの起動が成功した後」に、既存のファイルを上書きしない形で開く
    //   （issue 011 merge ゲートレビュー item 3）。開けなければドライバを止めて終わる。
    let mut out = match OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(out_path)
    {
        Ok(f) => f,
        Err(e) => {
            stop.store(true, Ordering::Release);
            let _ = handle.thread.join();
            return Err(format!(
                "出力先を開けない（既存の観測ログは上書きしない）: {e}"
            ));
        }
    };
    write_line(&mut out, &meta_line())?;

    let started = Instant::now();
    let observe = handle
        .candidate_window_observer
        .unwrap_or_else(default_candidate_observer);
    let mut monitor = Monitor::new(started, cfg!(windows), observe);
    tracing::info!(out = %out_path.display(), "logging started");
    let mut result = Ok(());
    while duration.is_none_or(|d| started.elapsed() < d) {
        // ⚠️★ ドライバのスレッドが想定外に終わっていたらエラーで終わる
        //   （issue 011 merge ゲートレビュー item 4・`driver_api.rs` の停止の契約）。
        if handle.thread.is_finished() {
            result = Err("ドライバのスレッドが終了している（想定外の終了）".to_string());
            break;
        }
        match rx.recv_timeout(Duration::from_millis(POLL_MS)) {
            Ok(k) => {
                // ⚠️ VK は種別（14 種）に畳んでから書く。VK そのものは書かない。
                result = write_line(
                    &mut out,
                    &key_line(k.t, KeyCategory::from_vk(k.vk), k.press),
                );
            }
            Err(RecvTimeoutError::Timeout) => {}
            Err(RecvTimeoutError::Disconnected) => {
                result = Err("ドライバが終了した（打鍵の送信側が閉じた）".to_string());
            }
        }
        if result.is_ok() {
            result = monitor.poll(Instant::now(), wall_ms(), &mut out);
        }
        if result.is_err() {
            break;
        }
    }
    // ⚠️★ 終了直前にもう一度だけスケジュール抜きで回し、直近の poll 以降に届いた READY の
    //   取りこぼしを防ぐ（issue 011 merge ゲートレビュー item 4）。
    if result.is_ok() {
        result = monitor.force_poll(Instant::now(), wall_ms(), &mut out);
    }
    stop.store(true, Ordering::Release);
    let _ = handle.thread.join();
    result
}

// ---------------------------------------------------------------------------
// --selftest（OS 非依存）: ドライバを使わず、状態機械に打鍵列を直接入れて監視ループを回し、読み戻して確かめる。
// ---------------------------------------------------------------------------

fn selftest(path: &Path) -> Result<(), String> {
    const T0: u64 = 1_700_000_000_000;
    // (T0 からの ms, VK): `k a` → Space → Enter（確定・1500ms）／ `k` → Esc（放棄・200ms）。
    let sessions: [&[(u64, u32)]; 2] = [
        &[(0, 0x4B), (120, 0x41), (400, 0x20), (1500, 0x0D)],
        &[(3000, 0x4B), (3200, 0x1B)],
    ];
    let drained_at = [T0 + 2000, T0 + 3500];

    let mut out = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .open(path)
        .map_err(|e| format!("selftest の出力先を開けない: {e}"))?;
    write_line(&mut out, &meta_line())?;
    let base = Instant::now();
    let mut monitor = Monitor::new(base, cfg!(windows), default_candidate_observer());
    for (i, keys) in sessions.iter().enumerate() {
        for &(dt, vk) in keys.iter() {
            write_line(&mut out, &key_line(T0 + dt, KeyCategory::from_vk(vk), true))?;
            ime_compose::drive(vk, true, Chord::Plain, T0 + dt);
        }
        let now = base + Duration::from_millis(POLL_MS * 2 * (i as u64 + 1));
        monitor.poll(now, drained_at[i], &mut out)?;
    }

    // ⚠️★★★ Windows 限定の safety valve 経路（issue 011 merge ゲートレビュー item 7）。
    // `K` → `Space` で候補窓を開いた状態（`active == true`）にし、Enter も Esc も Escape も
    // 送らず候補窓が開いたまま `MONITOR_SAFETY_VALVE_MS` を超えたことにする（`K` だけでは
    // `step()` の遷移表どおり `active` は立たない —— 立つのは Space で候補が表示されてから）。
    // cfg!(windows) が false（macOS ビルド）では `Monitor.is_windows` が false になり、
    // リセットだけ起きて行は出ない（GSE と同じ: valve のリセット自体は両 OS 共通・
    // shadow の emit は Windows 限定 —— `lib.rs` の safety valve 節と `emit_ime_shadow` の doc を参照）。
    let k3_at = T0 + 4000;
    write_line(&mut out, &key_line(k3_at, KeyCategory::from_vk(0x4B), true))?;
    ime_compose::drive(0x4B, true, Chord::Plain, k3_at); // セッション開始（まだ active ではない）
    write_line(
        &mut out,
        &key_line(k3_at + 50, KeyCategory::from_vk(0x20), true),
    )?;
    ime_compose::drive(0x20, true, Chord::Plain, k3_at + 50); // Space → 候補表示（active = true）
    let compose_poll = base + Duration::from_millis(POLL_MS * 6);
    monitor.poll(compose_poll, k3_at + 50, &mut out)?; // active_since を刻むだけ（valve 未発火）
    let valve_ts = k3_at + MONITOR_SAFETY_VALVE_MS + 1_000;
    let valve_poll = compose_poll + Duration::from_millis(MONITOR_SAFETY_VALVE_MS + 1_000);
    monitor.poll(valve_poll, valve_ts, &mut out)?; // ★ ここで valve が発火する（Windows のみ 1 行）

    drop(out);

    let text = std::fs::read_to_string(path).map_err(|e| format!("読み戻せない: {e}"))?;
    let lines: Vec<&str> = text.lines().collect();
    let count = |needle: &str| lines.iter().filter(|l| l.contains(needle)).count();
    let expect_shadow_lines: usize = if cfg!(windows) { 3 } else { 2 };
    let expect_key_lines: usize = 8;
    let expect_alphabetic: usize = 4;
    let expect: Vec<(bool, String)> = vec![
        (
            lines.len() == 1 + expect_key_lines + expect_shadow_lines,
            format!(
                "行数が {}（meta 1 + key {expect_key_lines} + ime_shadow {expect_shadow_lines}）でない",
                1 + expect_key_lines + expect_shadow_lines
            ),
        ),
        (
            lines.first().is_some_and(|l| l.starts_with(r#"{"type":"meta","format":"obs/1""#)),
            "1 行目が obs/1 の meta でない".to_string(),
        ),
        (count(r#""type":"key""#) == expect_key_lines, format!("key 行が {expect_key_lines} 行でない")),
        (
            count(r#""category":"alphabetic""#) == expect_alphabetic,
            format!("alphabetic の key 行が {expect_alphabetic} 行でない"),
        ),
        (lines.contains(&shadow_line(drained_at[0], 1500, 0, false).as_str()), "確定の ime_shadow 行が無い".to_string()),
        (lines.contains(&shadow_line(drained_at[1], 200, 0, true).as_str()), "放棄の ime_shadow 行が無い".to_string()),
        (
            !cfg!(windows) || lines.contains(&shadow_line(valve_ts, MONITOR_SAFETY_VALVE_MS + 1_000, 0, false).as_str()),
            "safety valve の stale ime_shadow 行が無い（Windows 限定）".to_string(),
        ),
        (lines.iter().all(|l| !l.contains(' ') && !l.contains('\\')), "行に空白かエスケープがある".to_string()),
        (!IME_SHADOW_READY.load(Ordering::Acquire), "IME_SHADOW_READY が残っている".to_string()),
    ];
    let failed: Vec<&str> = expect
        .iter()
        .filter(|(ok, _)| !ok)
        .map(|(_, why)| why.as_str())
        .collect();
    if failed.is_empty() {
        tracing::info!(lines = lines.len(), "selftest ok");
        Ok(())
    } else {
        Err(format!("selftest 失敗: {}", failed.join(" / ")))
    }
}

// ---------------------------------------------------------------------------
// 引数
// ---------------------------------------------------------------------------

#[derive(Debug, PartialEq)]
struct Args {
    out: Option<PathBuf>,
    duration_s: Option<u64>,
    selftest: bool,
}

fn parse_args(args: &[String]) -> Result<Args, String> {
    let mut parsed = Args {
        out: None,
        duration_s: None,
        selftest: false,
    };
    let mut it = args.iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "--selftest" => parsed.selftest = true,
            "--out" => {
                // ⚠️ 2 回渡したら使い方の誤り（issue 011 merge ゲートレビュー item 9）。
                if parsed.out.is_some() {
                    return Err("--out は 2 回渡せない".to_string());
                }
                parsed.out = Some(PathBuf::from(it.next().ok_or("--out にはパスが要る")?));
            }
            "--duration-s" => {
                let n = it.next().ok_or("--duration-s には秒数が要る")?;
                parsed.duration_s = Some(n.parse().map_err(|_| "--duration-s は 0 以上の整数")?);
            }
            other => {
                return Err(format!(
                    "未知の引数: {other}（--out <path> / --duration-s <n> / --selftest）"
                ))
            }
        }
    }
    if !parsed.selftest && parsed.out.is_none() {
        return Err("--out <path> が要る".to_string());
    }
    Ok(parsed)
}

fn main() {
    tracing_subscriber::fmt()
        .with_writer(std::io::stderr)
        .init();
    let args: Vec<String> = std::env::args().skip(1).collect();
    let parsed = match parse_args(&args) {
        Ok(p) => p,
        Err(e) => {
            tracing::error!("{e}");
            std::process::exit(2);
        }
    };
    let result = if parsed.selftest {
        // ⚠️ 既定の出力先（`--out` を渡さなかった場合）は実行後に消す
        //   （issue 011 merge ゲートレビュー item 9）。
        let used_default = parsed.out.is_none();
        let path = parsed
            .out
            .unwrap_or_else(|| std::env::temp_dir().join("ime-observation-selftest.jsonl"));
        let r = selftest(&path);
        if used_default {
            let _ = std::fs::remove_file(&path);
        }
        r
    } else {
        let path = parsed.out.unwrap_or_default();
        run(&path, parsed.duration_s.map(Duration::from_secs))
    };
    if let Err(e) = result {
        tracing::error!("{e}");
        std::process::exit(1);
    }
}

// ⚠️ ここのテストは実 Atomic（`input::hook` の static）に触れない（コピーした状態機械のテストが
//    同じ Atomic を並列で使うため）。`Monitor` を使うテストは `ShadowAtomics::fresh_for_test()`
//    （`Box::leak` した独立の Atomic）を使う。状態機械を通す検査は `--selftest`（別プロセス）が持つ。
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lines_have_no_spaces_or_escapes() {
        for l in [
            meta_line(),
            key_line(1, KeyCategory::Other, false),
            shadow_line(1, 2, 3, true),
        ] {
            assert!(!l.contains(' ') && !l.contains('\\'), "{l}");
        }
    }

    #[test]
    fn meta_line_carries_the_two_line_kinds_and_a_64_hex_manifest_hash() {
        let l = meta_line();
        assert!(
            l.contains(r#""unconditional":["key"]"#)
                && l.contains(r#""config_gated":["ime_shadow"]"#)
        );
        let hex = l
            .split(r#""manifest_sha256":""#)
            .nth(1)
            .and_then(|s| s.split('"').next())
            .unwrap_or("");
        assert!(
            hex.len() == 64 && hex.bytes().all(|b| b.is_ascii_hexdigit()),
            "{hex}"
        );
    }

    #[test]
    fn key_line_writes_a_category_never_the_vk() {
        assert_eq!(
            key_line(5, KeyCategory::from_vk(0x41), true),
            r#"{"type":"key","t":5,"category":"alphabetic","press":true}"#
        );
    }

    #[test]
    fn args_need_out_unless_selftest() {
        let s = |v: &[&str]| v.iter().map(|x| x.to_string()).collect::<Vec<_>>();
        assert!(parse_args(&s(&[])).is_err());
        assert!(parse_args(&s(&["--selftest"])).is_ok());
        assert_eq!(
            parse_args(&s(&["--out", "a", "--duration-s", "3"]))
                .unwrap()
                .duration_s,
            Some(3)
        );
        assert!(parse_args(&s(&["--out", "a", "--nope"])).is_err());
    }

    #[test]
    fn args_reject_out_given_twice() {
        // issue 011 merge ゲートレビュー item 9。
        let s = |v: &[&str]| v.iter().map(|x| x.to_string()).collect::<Vec<_>>();
        let e = parse_args(&s(&["--out", "a", "--out", "b"])).unwrap_err();
        assert!(e.contains("2 回"), "{e}");
    }

    // -----------------------------------------------------------------
    // `Monitor`: 独立の Atomic（`ShadowAtomics::fresh_for_test`）を使い、コピーした状態機械の
    // 単体テストが並列に読み書きする実 Atomic とは競合しない。
    // -----------------------------------------------------------------

    #[test]
    fn poll_uses_injected_candidate_observer_not_the_real_ime_active_atomic() {
        // issue 011 merge ゲートレビュー item 1: 観測関数を注入すれば poll はそれに従う
        // （実 IME_ACTIVE の値には一切触れない・依存しない）。
        let atomics = ShadowAtomics::fresh_for_test();
        let now = Instant::now();
        let mut monitor = Monitor::new_for_test(now, false, Box::new(|| true), atomics);
        let mut out: Vec<u8> = Vec::new();
        monitor.poll(now, 1, &mut out).expect("poll");
        assert_eq!(
            monitor.last_active,
            Some(true),
            "poll は注入した観測関数の戻り値に従うべき"
        );
    }

    #[test]
    fn poll_before_next_poll_time_is_a_no_op() {
        let atomics = ShadowAtomics::fresh_for_test();
        let now = Instant::now();
        let mut monitor = Monitor::new_for_test(now, false, Box::new(|| false), atomics);
        let mut out: Vec<u8> = Vec::new();
        monitor.poll(now, 1, &mut out).unwrap();
        assert_eq!(monitor.last_active, Some(false));
        // POLL_MS 未満なら次の poll は素通り（last_active は変わらない）。
        monitor
            .poll(now + Duration::from_millis(1), 2, &mut out)
            .unwrap();
        assert_eq!(monitor.last_active, Some(false));
    }

    #[test]
    fn windows_active_to_false_transition_emits_ime_shadow_from_ready() {
        // issue 011 merge ゲートレビュー item 7 の経路 2: active→false 遷移（READY あり）。
        let atomics = ShadowAtomics::fresh_for_test();
        atomics.ready.store(true, Ordering::Release);
        atomics.dwell_ms.store(777, Ordering::Relaxed);
        atomics.nav.store(2, Ordering::Relaxed);
        atomics.abandon.store(false, Ordering::Relaxed);
        let now = Instant::now();
        let mut calls = vec![true, false].into_iter();
        let mut monitor = Monitor::new_for_test(
            now,
            true,
            Box::new(move || calls.next().unwrap_or(false)),
            atomics,
        );
        let mut out: Vec<u8> = Vec::new();
        monitor.poll(now, 100, &mut out).unwrap();
        monitor
            .poll(now + Duration::from_millis(200), 200, &mut out)
            .unwrap();
        let text = String::from_utf8(out).unwrap();
        assert_eq!(
            text.lines().collect::<Vec<_>>(),
            vec![shadow_line(200, 777, 2, false)]
        );
    }

    #[test]
    fn windows_stale_path_uses_composition_start_ms_when_ready_is_absent() {
        // issue 011 merge ゲートレビュー item 7 の経路 3: stale（READY 無し・START_MS から dwell）。
        let atomics = ShadowAtomics::fresh_for_test();
        atomics.composition_start_ms.store(1_000, Ordering::Relaxed);
        let now = Instant::now();
        let mut calls = vec![true, false].into_iter();
        let mut monitor = Monitor::new_for_test(
            now,
            true,
            Box::new(move || calls.next().unwrap_or(false)),
            atomics,
        );
        let mut out: Vec<u8> = Vec::new();
        monitor.poll(now, 100, &mut out).unwrap();
        monitor
            .poll(now + Duration::from_millis(200), 5_100, &mut out)
            .unwrap();
        let text = String::from_utf8(out).unwrap();
        assert_eq!(
            text.lines().collect::<Vec<_>>(),
            vec![shadow_line(5_100, 4_100, 0, false)]
        );
    }

    #[test]
    fn windows_safety_valve_resets_active_and_emits_stale_line() {
        // issue 011 merge ゲートレビュー item 7 の経路 1: safety valve。
        let atomics = ShadowAtomics::fresh_for_test();
        atomics.active.store(true, Ordering::Release);
        atomics.composition_start_ms.store(2_000, Ordering::Relaxed);
        let now = Instant::now();
        let mut monitor = Monitor::new_for_test(now, true, Box::new(|| true), atomics);
        let mut out: Vec<u8> = Vec::new();
        monitor.poll(now, 100, &mut out).unwrap(); // active_since を刻む（valve 未発火）
        assert!(out.is_empty(), "valve が発火する前に行が出た");
        let after = now + Duration::from_millis(MONITOR_SAFETY_VALVE_MS + 1_000);
        monitor.poll(after, 30_100, &mut out).unwrap(); // valve 発火
        assert!(
            !atomics.active.load(Ordering::Acquire),
            "valve は候補窓の Atomic を下ろすべき"
        );
        let text = String::from_utf8(out).unwrap();
        assert_eq!(
            text.lines().collect::<Vec<_>>(),
            vec![shadow_line(30_100, 28_100, 0, false)]
        );
    }

    #[test]
    fn mac_ready_drains_regardless_of_active_transition() {
        // macOS では active→false 遷移経路そのものが無い（GSE と同じ）。ime_shadow が出るのは
        // READY の直接ポーリングだけで、`active` の値とは無関係に drain される
        // （`ime_compose::should_drain_ready` は mac 側で `ready` だけを見る）。
        let atomics = ShadowAtomics::fresh_for_test();
        atomics.ready.store(true, Ordering::Release);
        atomics.dwell_ms.store(50, Ordering::Relaxed);
        let now = Instant::now();
        let mut calls = vec![true, false].into_iter();
        let mut monitor = Monitor::new_for_test(
            now,
            false,
            Box::new(move || calls.next().unwrap_or(false)),
            atomics,
        );
        let mut out: Vec<u8> = Vec::new();
        // 1 回目（active=true）で即 drain される。
        monitor.poll(now, 100, &mut out).unwrap();
        // 2 回目（active=false）は READY が既に消費済みなので何も出ない。
        monitor
            .poll(now + Duration::from_millis(200), 200, &mut out)
            .unwrap();
        let text = String::from_utf8(out).unwrap();
        assert_eq!(
            text.lines().collect::<Vec<_>>(),
            vec![shadow_line(100, 50, 0, false)]
        );
    }

    #[test]
    fn force_poll_ignores_the_poll_schedule() {
        // issue 011 merge ゲートレビュー item 4: 終了直前の force_poll は next_poll を待たない。
        let atomics = ShadowAtomics::fresh_for_test();
        atomics.ready.store(true, Ordering::Release);
        atomics.dwell_ms.store(9, Ordering::Relaxed);
        let now = Instant::now();
        let mut monitor = Monitor::new_for_test(now, false, Box::new(|| false), atomics);
        let mut out: Vec<u8> = Vec::new();
        // 通常の poll は next_poll（= now）未満では動かないが、ここでは同時刻を渡す force_poll が
        // 確実に 1 周してくれることを確かめる（duration ゼロの実行でも最後の 1 周が保証される）。
        monitor.force_poll(now, 100, &mut out).unwrap();
        let text = String::from_utf8(out).unwrap();
        assert_eq!(
            text.lines().collect::<Vec<_>>(),
            vec![shadow_line(100, 9, 0, false)]
        );
    }
}
