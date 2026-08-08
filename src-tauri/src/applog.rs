//! アプリ本体の診断ログ (`tracing`) をファイルに残す。
//!
//! # なぜ要るか
//!
//! `lib.rs` の G1 自動提出は、⚠️ **画面には定型文だけを出し、参加者 ID とセッション日時を
//! 含む詳細は「ローカルのログにだけ」残す**設計になっている (`data-privacy`)。
//! ところが従来の `tracing_subscriber::fmt::init()` は **stdout に書くだけ**で、
//! Finder からダブルクリックで起動した `.app` の stdout はどこにも繋がっていない。
//! ★ 2026-08-08 に unified log 41,012 行を検索して **0 行**であることを実測した。
//! → 「ローカルのログにだけ残す」は**成立していなかった**。詳細はどこにも残っていない。
//!
//! ⚠️ ★ preregistration 第 13 版で研究者は**初回起動に同席したあと離れる**。
//! その後に起きた失敗の原因が追えないので、ここでファイルに落とす。
//!
//! # なぜ `impl MakeWriter for std::fs::File` を使わないか
//!
//! tracing-subscriber は `File` に直接書ける実装を持っている (`fmt/writer.rs:704`) が、
//! ⚠️ **それは同期 I/O** である。`hook_macos.rs` の CGEventTap コールバックの中に
//! `tracing::warn!("InputEvent dropped (channel full)")` があり、channel が詰まると
//! **打鍵ごとに発火しうる**。そこでファイル I/O をするのは `hook-constraints`
//! (コールバック内はブロッキング禁止) に反する。
//!
//! → `logger.rs` の `LogChannel` と同じ形にする: **bounded channel + 書き込みスレッド**。
//! 呼び出し側は `try_send` するだけで、待たないし、詰まったら捨てる。
//! ⚠️ 新しい crate は足していない (`crossbeam-channel` は既存依存)。

use std::fs::{File, OpenOptions};
use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

use crossbeam_channel::{bounded, Sender, TrySendError};
use tracing_subscriber::fmt::MakeWriter;

/// 1 ファイルの上限。超えたら `.1` へ 1 世代だけ回す (ディスク上限 ≒ 2 倍)。
///
/// ★ 10 ブロック × 数十分の実施で INFO 行は数百行 (数十 KB) にしかならない。
/// 2 MiB は「異常時にログが暴走しても端末を埋めない」ための天井であって、
/// 通常運用でここに触ることは無い。
const MAX_BYTES: u64 = 2 * 1024 * 1024;

/// channel の深さ。⚠️ ★ **溢れたら捨てる**ので、深さは「一瞬の突発を吸う」ぶんだけあればよい。
const QUEUE_DEPTH: usize = 256;

/// `tracing` の fmt レイヤに渡す `MakeWriter`。
///
/// イベント 1 件ごとに [`AppLogWriter`] を作り、その `Drop` で 1 回だけ送る。
#[derive(Clone)]
pub struct AppLogMaker {
    tx: Sender<Vec<u8>>,
    dropped: Arc<AtomicU64>,
}

/// 1 イベント分のバッファ。`Drop` で channel へ 1 回だけ送る。
///
/// ★ 1 イベントを 1 メッセージにまとめるのは、**行が途中で割れないようにする**ため。
/// fmt レイヤは 1 イベントを複数回の `write` に分けて渡してくる。
pub struct AppLogWriter {
    tx: Sender<Vec<u8>>,
    dropped: Arc<AtomicU64>,
    buf: Vec<u8>,
}

impl Write for AppLogWriter {
    fn write(&mut self, data: &[u8]) -> io::Result<usize> {
        self.buf.extend_from_slice(data);
        Ok(data.len())
    }

    /// ⚠️ ★ ここでは**何もしない**。実際に送るのは `Drop` (= イベント 1 件の完成時) である。
    fn flush(&mut self) -> io::Result<()> {
        Ok(())
    }
}

impl Drop for AppLogWriter {
    fn drop(&mut self) {
        if self.buf.is_empty() {
            return;
        }
        let chunk = std::mem::take(&mut self.buf);
        // ⚠️ ★ `send` ではなく `try_send`。**呼び出し側 (フックのコールバックを含む) を
        //   絶対に待たせない**。詰まったら捨て、捨てたことは数えておく。
        match self.tx.try_send(chunk) {
            Ok(()) => {}
            Err(TrySendError::Full(_)) | Err(TrySendError::Disconnected(_)) => {
                self.dropped.fetch_add(1, Ordering::Relaxed);
            }
        }
    }
}

impl<'a> MakeWriter<'a> for AppLogMaker {
    type Writer = AppLogWriter;

    fn make_writer(&'a self) -> Self::Writer {
        AppLogWriter {
            tx: self.tx.clone(),
            dropped: Arc::clone(&self.dropped),
            buf: Vec::new(),
        }
    }
}

/// `tracing` の購読者を **stdout + ファイル**の 2 本立てで設置する。
///
/// # ⚠️ ★ なぜ変えたか (2026-08-08)
///
/// 旧: `tracing_subscriber::fmt::init()` = **stdout だけ**。
/// Finder からダブルクリックした `.app` の stdout はどこにも繋がっておらず、
/// ★ unified log 41,012 行を検索して **0 行**であることを実測した。
/// つまり `submit_g1_reconcile` の「詳細はローカルのログにだけ残す」は成立していなかった。
///
/// # ⚠️ プライバシー (`data-privacy` ルール 1)
///
/// ファイル側には `.with_max_level(INFO)` を付ける。いま `env-filter` feature は
/// 入っていないので既定の閾値も INFO であり (`tracing-subscriber` の
/// `Subscriber::DEFAULT_MAX_LEVEL` を一次資料で確認済み)、`debug!` は 1 行も出ていない。
/// ★ それでも明示するのは、⚠️ **将来 `RUST_LOG` を効くようにした誰かが
/// `hook_macos.rs` のキーコード (`VK=0x..`) を `debug!` 経由でディスクに
/// 落とすのを構造で止める**ため (運用の注意に頼らない)。
///
/// # 落ち方
///
/// ファイルを開けなければ **stdout だけで続行する**。⚠️ ★ 起動は止めない
/// (ログが無いことより、アプリが起動しないほうが重い)。
pub fn init_tracing(path: &Path) {
    use tracing_subscriber::fmt::writer::MakeWriterExt;

    match spawn(path) {
        Ok(file_writer) => {
            tracing_subscriber::fmt()
                // ★ ANSI を切る。付いたままだとファイルがエスケープ列で読めなくなる。
                .with_ansi(false)
                .with_writer(std::io::stdout.and(file_writer.with_max_level(tracing::Level::INFO)))
                .init();
            tracing::info!(app_log = %path.display(), "app log file opened");
        }
        Err(e) => {
            tracing_subscriber::fmt().with_ansi(false).init();
            tracing::warn!(
                app_log = %path.display(),
                "could not open the app log file; continuing with stdout only: {}",
                e
            );
        }
    }
}

/// 書き込みスレッドを起こし、`MakeWriter` を返す。
///
/// ファイルを開けなければ `Err` を返す。⚠️ ★ 呼び出し側は**起動を止めず**、
/// stdout だけで動き続けること (ログが無いことよりアプリが起動しないことのほうが重い)。
pub fn spawn(path: &Path) -> io::Result<AppLogMaker> {
    let mut sink = Sink::open(path.to_path_buf())?;
    let (tx, rx) = bounded::<Vec<u8>>(QUEUE_DEPTH);
    let dropped = Arc::new(AtomicU64::new(0));
    let dropped_for_thread = Arc::clone(&dropped);

    std::thread::Builder::new()
        .name("gse-applog".to_string())
        .spawn(move || {
            let mut reported: u64 = 0;
            while let Ok(chunk) = rx.recv() {
                // ⚠️ ★ 捨てた件数を**黙って捨てない**。次に書けたときに 1 行残す
                //   (`silent-failure-in-guard-scripts` の教訓: 黙って落ちる経路を作らない)。
                let now = dropped_for_thread.load(Ordering::Relaxed);
                if now > reported {
                    let note = format!(
                        "[applog] {} log line(s) were dropped (writer queue full)\n",
                        now - reported
                    );
                    let _ = sink.write_all(note.as_bytes());
                    reported = now;
                }
                let _ = sink.write_all(&chunk);
            }
        })?;

    Ok(AppLogMaker { tx, dropped })
}

/// 書き込み先のファイルと、いま何バイト書いたか。★ 世代交代もここだけで完結する
/// (このスレッド以外は触らないので、ロックも競合も要らない)。
struct Sink {
    path: PathBuf,
    file: File,
    written: u64,
}

impl Sink {
    fn open(path: PathBuf) -> io::Result<Self> {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        let file = append_file(&path)?;
        let written = file.metadata().map(|m| m.len()).unwrap_or(0);
        Ok(Self {
            path,
            file,
            written,
        })
    }

    fn write_all(&mut self, data: &[u8]) -> io::Result<()> {
        if self.written + data.len() as u64 > MAX_BYTES {
            self.rotate()?;
        }
        self.file.write_all(data)?;
        // ★ 毎回 flush する。⚠️ 診断ログは「落ちる直前の 1 行」がいちばん要る。
        //   バッファに抱えたまま異常終了すると、**いちばん読みたい行だけが消える**。
        self.file.flush()?;
        self.written += data.len() as u64;
        Ok(())
    }

    /// `gse-app.log` → `gse-app.log.1` へ 1 世代だけ回す (旧 `.1` は捨てる)。
    fn rotate(&mut self) -> io::Result<()> {
        let mut backup = self.path.clone().into_os_string();
        backup.push(".1");
        let backup = PathBuf::from(backup);
        // rename が失敗しても**書き続ける**ほうが安全 (ログが伸びるだけで実施は止まらない)。
        if std::fs::rename(&self.path, &backup).is_ok() {
            self.file = append_file(&self.path)?;
            self.written = 0;
        }
        Ok(())
    }
}

/// 追記モードで開く。⚠️ ★ `truncate` しない (前回の起動のログを消さない)。
fn append_file(path: &Path) -> io::Result<File> {
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        OpenOptions::new()
            .create(true)
            .append(true)
            .mode(0o600)
            .open(path)
    }
    #[cfg(not(unix))]
    {
        OpenOptions::new().create(true).append(true).open(path)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::{Duration, Instant};

    /// 書き込みスレッドは非同期なので、条件が満たされるまで待つ。
    /// ⚠️ ★ 固定 sleep にしない (遅いマシンで falsely 赤くなる／速いマシンで無駄に待つ)。
    fn wait_until<F: Fn() -> bool>(cond: F) -> bool {
        let deadline = Instant::now() + Duration::from_secs(5);
        while Instant::now() < deadline {
            if cond() {
                return true;
            }
            std::thread::sleep(Duration::from_millis(10));
        }
        cond()
    }

    fn tmpdir(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!(
            "gse-applog-test-{}-{}-{:?}",
            tag,
            std::process::id(),
            std::thread::current().id()
        ));
        let _ = std::fs::remove_dir_all(&d);
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    fn send(maker: &AppLogMaker, line: &str) {
        let mut w = maker.make_writer();
        w.write_all(line.as_bytes()).unwrap();
        drop(w);
    }

    /// T1: 送った行が**実ファイルに現れる**。
    #[test]
    fn writes_lines_to_the_real_file() {
        let dir = tmpdir("t1");
        let path = dir.join("gse-app.log");
        let maker = spawn(&path).unwrap();
        send(&maker, "hello applog\n");

        assert!(
            wait_until(|| std::fs::read_to_string(&path)
                .map(|s| s.contains("hello applog"))
                .unwrap_or(false)),
            "書いた行がファイルに現れない: {}",
            std::fs::read_to_string(&path).unwrap_or_default()
        );
    }

    /// T1b: 親ディレクトリが無くても作る (初回起動は `Documents/GSE-sessions` が無い)。
    #[test]
    fn creates_parent_directory() {
        let dir = tmpdir("t1b");
        let path = dir.join("not-yet").join("gse-app.log");
        let maker = spawn(&path).unwrap();
        send(&maker, "created\n");
        assert!(
            wait_until(|| path.exists()),
            "親ディレクトリが作られていない"
        );
    }

    /// T2: 追記である (前回の起動のログを消さない)。
    #[test]
    fn appends_instead_of_truncating() {
        let dir = tmpdir("t2");
        let path = dir.join("gse-app.log");
        std::fs::write(&path, "previous run\n").unwrap();

        let maker = spawn(&path).unwrap();
        send(&maker, "this run\n");

        assert!(wait_until(|| std::fs::read_to_string(&path)
            .map(|s| s.contains("this run"))
            .unwrap_or(false)));
        let body = std::fs::read_to_string(&path).unwrap();
        assert!(
            body.contains("previous run"),
            "前回のログが消えている (truncate されている): {body:?}"
        );
    }

    /// T3: 上限を超えたら `.1` へ回り、現ファイルが小さくなる。
    #[test]
    fn rotates_when_over_limit() {
        let dir = tmpdir("t3");
        let path = dir.join("gse-app.log");
        let backup = dir.join("gse-app.log.1");
        // 先に上限ぎりぎりまで太らせておく (テストで 2 MiB 書かないため)。
        std::fs::write(&path, vec![b'x'; MAX_BYTES as usize - 8]).unwrap();

        let maker = spawn(&path).unwrap();
        send(&maker, "line that tips it over the limit\n");

        assert!(
            wait_until(|| backup.exists()),
            "上限を超えたのに世代交代していない"
        );
        assert!(wait_until(|| std::fs::metadata(&path)
            .map(|m| m.len() < MAX_BYTES)
            .unwrap_or(false)));
        let fresh = std::fs::read_to_string(&path).unwrap();
        assert!(
            fresh.contains("tips it over"),
            "世代交代した後の新しいファイルに行が入っていない: {fresh:?}"
        );
        assert_eq!(
            std::fs::metadata(&backup).unwrap().len(),
            MAX_BYTES - 8,
            "旧世代の中身が変わっている"
        );
    }

    /// T4: channel が満杯でも**呼び出し側は待たない**。
    ///
    /// ⚠️ ★ これは `hook-constraints` の要求そのものである。`send` に変えると
    /// この test は `deadline` を超えて赤くなる。
    #[test]
    fn never_blocks_the_caller_when_full() {
        // ★ ファイルは要らない。**書き込みスレッドを起こさず** channel を満杯にする
        //   (`_rx` を握ったまま誰も受け取らない = 詰まった状態そのもの)。
        let (tx, _rx) = bounded::<Vec<u8>>(1);
        let dropped = Arc::new(AtomicU64::new(0));
        let maker = AppLogMaker {
            tx,
            dropped: Arc::clone(&dropped),
        };

        let started = Instant::now();
        for i in 0..1000 {
            send(&maker, &format!("line {i}\n"));
        }
        let elapsed = started.elapsed();

        assert!(
            elapsed < Duration::from_secs(2),
            "満杯の channel で呼び出し側が待っている ({elapsed:?})"
        );
        assert!(
            dropped.load(Ordering::Relaxed) > 0,
            "捨てたのに件数が数えられていない"
        );
    }

    /// T5: 捨てた件数を**黙って捨てない** (次に書けたときに 1 行残す)。
    #[test]
    fn reports_dropped_lines() {
        let dir = tmpdir("t5");
        let path = dir.join("gse-app.log");
        let maker = spawn(&path).unwrap();
        // 実際に溢れさせるのは不安定なので、カウンタを直接立てて「報告するか」を見る。
        maker.dropped.fetch_add(7, Ordering::Relaxed);
        send(&maker, "after the drop\n");

        assert!(
            wait_until(|| std::fs::read_to_string(&path)
                .map(|s| s.contains("7 log line(s) were dropped"))
                .unwrap_or(false)),
            "捨てた件数がファイルに出ていない: {}",
            std::fs::read_to_string(&path).unwrap_or_default()
        );
    }
}
