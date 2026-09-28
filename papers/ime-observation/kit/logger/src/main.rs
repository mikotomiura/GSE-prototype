//! ime-observation-logger — IME 観測の単体ロガー（核）。
//!
//! GSE の変換セッション状態機械（`input/ime_compose.rs` / `ime_cloak.rs` / `ime_mode.rs`）を**逐語コピー**で
//! 使い、Atomic を読んで `ime_shadow` 行を、ドライバが送る打鍵から `key` 行を、`obs/1` で書き出す。
//! ⚠️ content-free: `key` は 14 種の category だけ・`ime_shadow` は数（`dwell_ms` / `nav` / `abandon`）だけ。
//!
//! 使い方: `ime-observation-logger --out <path> [--duration-s <n>]` / `ime-observation-logger --selftest [--out <path>]`
//! OS ドライバ（打鍵の取得）は `driver_macos.rs` / `driver_windows.rs`（後続の issue）。

mod driver_api;
#[cfg(target_os = "macos")]
mod driver_macos;
#[cfg(windows)]
mod driver_windows;
mod input;
#[allow(dead_code)]
mod key_category;

use std::fs::File;
use std::io::Write;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, Ordering};
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
/// `obs/1` の `os` は macos / windows の 2 値。（ドライバの無い OS ではドライバの起動で止まる。）
const OS_NAME: &str = if cfg!(target_os = "macos") { "macos" } else { "windows" };
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
    format!(r#"{{"type":"key","t":{t},"category":"{}","press":{press}}}"#, category.as_str())
}

fn shadow_line(t: u64, dwell_ms: u64, nav: u32, abandon: bool) -> String {
    format!(r#"{{"type":"ime_shadow","t":{t},"dwell_ms":{dwell_ms},"nav":{nav},"abandon":{abandon}}}"#)
}

/// 1 行 = 1 回の書き込み＋flush（強制終了されても書いた行は残る）。
fn write_line<W: Write>(out: &mut W, line: &str) -> Result<(), String> {
    writeln!(out, "{line}").and_then(|()| out.flush()).map_err(|e| format!("書き出しに失敗: {e}"))
}

fn wall_ms() -> u64 {
    SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_millis() as u64
}

// ---------------------------------------------------------------------------
// 監視ループ（ime_shadow 行）。
// 一次: GSE `src-tauri/src/lib.rs` の `emit_ime_shadow` と IME Monitor スレッド（`should_drain_ready` を使う判断の順序）の
// **G1（`g1_mode()`）を除いた写し**。⚠️ `t` は drain した時刻。⚠️ Stale 経路 / active→false 遷移経路は Windows 限定。
// 差分: `is_candidate_window_open()`（Windows の遷移の観測）の代わりに `IME_ACTIVE` を直接読む。
// ---------------------------------------------------------------------------

fn emit_ime_shadow<W: Write>(out: &mut W, t: u64, is_windows: bool) -> Result<(), String> {
    if IME_SHADOW_READY.swap(false, Ordering::AcqRel) {
        // 正常経路: 要約は書き込み側が計算済み。
        let dwell_ms = IME_SHADOW_DWELL_MS.swap(0, Ordering::Relaxed);
        let nav = IME_CANDIDATE_NAV_COUNT.swap(0, Ordering::Relaxed);
        let abandon = IME_SHADOW_ABANDON.swap(false, Ordering::Relaxed);
        return write_line(out, &shadow_line(t, dwell_ms, nav, abandon));
    }
    // ⚠️ Stale 経路は Windows 限定（macOS では途中の偽の行が出てセッションが壊れる）。
    if is_windows {
        let start = IME_COMPOSITION_START_MS.swap(0, Ordering::Relaxed);
        if start > 0 {
            let dwell_ms = t.saturating_sub(start);
            let nav = IME_CANDIDATE_NAV_COUNT.swap(0, Ordering::Relaxed);
            let abandon = IME_SHADOW_ABANDON.swap(false, Ordering::Relaxed);
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
}

impl Monitor {
    fn new(now: Instant, is_windows: bool) -> Self {
        Self { is_windows, last_active: None, active_since: None, next_poll: now }
    }

    /// GSE の IME Monitor スレッドの 1 周（同じ判断・同じ順序）。`POLL_MS` に 1 回だけ動く。
    /// `now` は経過の測定用・`ts_ms` は drain の壁時計（`ime_shadow` の `t`）。
    fn poll<W: Write>(&mut self, now: Instant, ts_ms: u64, out: &mut W) -> Result<(), String> {
        if now < self.next_poll {
            return Ok(());
        }
        self.next_poll = now + Duration::from_millis(POLL_MS);
        let active = IME_ACTIVE.load(Ordering::Acquire);

        // Safety valve: 窓の閉じを取りこぼして `IME_ACTIVE` が立ちっぱなしなら stale とみなして下ろす。
        if active {
            let since = *self.active_since.get_or_insert(now);
            if now.duration_since(since) > Duration::from_millis(MONITOR_SAFETY_VALVE_MS) {
                tracing::warn!(valve_ms = MONITOR_SAFETY_VALVE_MS, "IME_ACTIVE stale — auto-resetting");
                IME_ACTIVE.store(false, Ordering::Release);
                self.active_since = None;
                self.last_active = Some(false);
                if self.is_windows {
                    emit_ime_shadow(out, ts_ms, true)?;
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
                emit_ime_shadow(out, ts_ms, true)?;
            }
        }

        // `IME_SHADOW_READY` の直接ポーリング（macOS で ime_shadow が出るのはこの経路だけ）。
        let ready = IME_SHADOW_READY.load(Ordering::Acquire);
        if ime_compose::should_drain_ready(ready, active, self.is_windows) {
            emit_ime_shadow(out, ts_ms, self.is_windows)?;
        }
        Ok(())
    }
}

// ---------------------------------------------------------------------------
// ドライバの差し込み（各 OS の中身は後続の issue）。
// ---------------------------------------------------------------------------

#[cfg(target_os = "macos")]
fn start_driver(ctx: DriverCtx) -> Result<std::thread::JoinHandle<()>, String> {
    driver_macos::start(ctx)
}
#[cfg(windows)]
fn start_driver(ctx: DriverCtx) -> Result<std::thread::JoinHandle<()>, String> {
    driver_windows::start(ctx)
}
#[cfg(not(any(target_os = "macos", windows)))]
fn start_driver(_ctx: DriverCtx) -> Result<std::thread::JoinHandle<()>, String> {
    Err("この OS にはドライバが無い（macOS / Windows のみ）".to_string())
}

fn run(out_path: &Path, duration: Option<Duration>) -> Result<(), String> {
    let mut out = File::create(out_path).map_err(|e| format!("出力先を開けない: {e}"))?;
    write_line(&mut out, &meta_line())?;
    let (tx, rx) = mpsc::channel();
    let stop = Arc::new(AtomicBool::new(false));
    let handle = start_driver(DriverCtx { keys: tx, stop: Arc::clone(&stop) })?;
    let started = Instant::now();
    let mut monitor = Monitor::new(started, cfg!(windows));
    tracing::info!(out = %out_path.display(), "logging started");
    let mut result = Ok(());
    while duration.is_none_or(|d| started.elapsed() < d) {
        match rx.recv_timeout(Duration::from_millis(POLL_MS)) {
            Ok(k) => {
                // ⚠️ VK は種別（14 種）に畳んでから書く。VK そのものは書かない。
                result = write_line(&mut out, &key_line(k.t, KeyCategory::from_vk(k.vk), k.press));
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
    stop.store(true, Ordering::Release);
    let _ = handle.join();
    result
}

// ---------------------------------------------------------------------------
// --selftest（OS 非依存）: ドライバを使わず、状態機械に打鍵列を直接入れて監視ループを回し、読み戻して確かめる。
// ---------------------------------------------------------------------------

fn selftest(path: &Path) -> Result<(), String> {
    const T0: u64 = 1_700_000_000_000;
    // (T0 からの ms, VK): `k a` → Space → Enter（確定・1500ms）／ `k` → Esc（放棄・200ms）。
    let sessions: [&[(u64, u32)]; 2] =
        [&[(0, 0x4B), (120, 0x41), (400, 0x20), (1500, 0x0D)], &[(3000, 0x4B), (3200, 0x1B)]];
    let drained_at = [T0 + 2000, T0 + 3500];

    let mut out = File::create(path).map_err(|e| format!("selftest の出力先を開けない: {e}"))?;
    write_line(&mut out, &meta_line())?;
    let base = Instant::now();
    let mut monitor = Monitor::new(base, cfg!(windows));
    for (i, keys) in sessions.iter().enumerate() {
        for &(dt, vk) in keys.iter() {
            write_line(&mut out, &key_line(T0 + dt, KeyCategory::from_vk(vk), true))?;
            ime_compose::drive(vk, true, Chord::Plain, T0 + dt);
        }
        let now = base + Duration::from_millis(POLL_MS * 2 * (i as u64 + 1));
        monitor.poll(now, drained_at[i], &mut out)?;
    }
    drop(out);

    let text = std::fs::read_to_string(path).map_err(|e| format!("読み戻せない: {e}"))?;
    let lines: Vec<&str> = text.lines().collect();
    let count = |needle: &str| lines.iter().filter(|l| l.contains(needle)).count();
    let expect = [
        (lines.len() == 9, "行数が 9（meta 1 + key 6 + ime_shadow 2）でない"),
        (lines.first().is_some_and(|l| l.starts_with(r#"{"type":"meta","format":"obs/1""#)), "1 行目が obs/1 の meta でない"),
        (count(r#""type":"key""#) == 6, "key 行が 6 行でない"),
        (count(r#""category":"alphabetic""#) == 3, "alphabetic の key 行が 3 行でない"),
        (lines.contains(&shadow_line(drained_at[0], 1500, 0, false).as_str()), "確定の ime_shadow 行が無い"),
        (lines.contains(&shadow_line(drained_at[1], 200, 0, true).as_str()), "放棄の ime_shadow 行が無い"),
        (lines.iter().all(|l| !l.contains(' ') && !l.contains('\\')), "行に空白かエスケープがある"),
        (!IME_SHADOW_READY.load(Ordering::Acquire), "IME_SHADOW_READY が残っている"),
    ];
    let failed: Vec<&str> = expect.iter().filter(|(ok, _)| !ok).map(|(_, why)| *why).collect();
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
    let mut parsed = Args { out: None, duration_s: None, selftest: false };
    let mut it = args.iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "--selftest" => parsed.selftest = true,
            "--out" => parsed.out = Some(PathBuf::from(it.next().ok_or("--out にはパスが要る")?)),
            "--duration-s" => {
                let n = it.next().ok_or("--duration-s には秒数が要る")?;
                parsed.duration_s = Some(n.parse().map_err(|_| "--duration-s は 0 以上の整数")?);
            }
            other => return Err(format!("未知の引数: {other}（--out <path> / --duration-s <n> / --selftest）")),
        }
    }
    if !parsed.selftest && parsed.out.is_none() {
        return Err("--out <path> が要る".to_string());
    }
    Ok(parsed)
}

fn main() {
    tracing_subscriber::fmt().with_writer(std::io::stderr).init();
    let args: Vec<String> = std::env::args().skip(1).collect();
    let parsed = match parse_args(&args) {
        Ok(p) => p,
        Err(e) => {
            tracing::error!("{e}");
            std::process::exit(2);
        }
    };
    let result = if parsed.selftest {
        let path = parsed.out.unwrap_or_else(|| std::env::temp_dir().join("ime-observation-selftest.jsonl"));
        selftest(&path)
    } else {
        let path = parsed.out.unwrap_or_default();
        run(&path, parsed.duration_s.map(Duration::from_secs))
    };
    if let Err(e) = result {
        tracing::error!("{e}");
        std::process::exit(1);
    }
}

// ⚠️ ここのテストは Atomic に触れない（コピーした状態機械のテストが同じ Atomic を並列で使うため）。
//    状態機械を通す検査は `--selftest`（別プロセス）が持つ。
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lines_have_no_spaces_or_escapes() {
        for l in [meta_line(), key_line(1, KeyCategory::Other, false), shadow_line(1, 2, 3, true)] {
            assert!(!l.contains(' ') && !l.contains('\\'), "{l}");
        }
    }

    #[test]
    fn meta_line_carries_the_two_line_kinds_and_a_64_hex_manifest_hash() {
        let l = meta_line();
        assert!(l.contains(r#""unconditional":["key"]"#) && l.contains(r#""config_gated":["ime_shadow"]"#));
        let hex = l.split(r#""manifest_sha256":""#).nth(1).and_then(|s| s.split('"').next()).unwrap_or("");
        assert!(hex.len() == 64 && hex.bytes().all(|b| b.is_ascii_hexdigit()), "{hex}");
    }

    #[test]
    fn key_line_writes_a_category_never_the_vk() {
        assert_eq!(key_line(5, KeyCategory::from_vk(0x41), true), r#"{"type":"key","t":5,"category":"alphabetic","press":true}"#);
    }

    #[test]
    fn args_need_out_unless_selftest() {
        let s = |v: &[&str]| v.iter().map(|x| x.to_string()).collect::<Vec<_>>();
        assert!(parse_args(&s(&[])).is_err());
        assert!(parse_args(&s(&["--selftest"])).is_ok());
        assert_eq!(parse_args(&s(&["--out", "a", "--duration-s", "3"])).unwrap().duration_s, Some(3));
        assert!(parse_args(&s(&["--out", "a", "--nope"])).is_err());
    }
}
