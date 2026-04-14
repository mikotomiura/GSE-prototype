use std::fs::{self, File};
use std::io::{BufWriter, Write};
use std::path::PathBuf;
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use crossbeam_channel::{bounded, Receiver, RecvTimeoutError, Sender};

/// ログエントリの種別
#[derive(Debug)]
pub enum LogEntry {
    /// キーストロークイベント (生データ)
    Key {
        vk_code: u32,
        timestamp: u64,
        is_press: bool,
    },
    /// 特徴量 + HMM状態確率 + 診断データ (分析スレッドから)
    Feat {
        timestamp: u64,
        f1: f64,
        f3: f64,
        f4: f64,
        f5: f64,
        f6: f64,
        p_flow: f64,
        p_inc: f64,
        p_stuck: f64,
        raw_x: f64,
        raw_y: f64,
        ewma_x: f64,
        ewma_y: f64,
        obs: usize,
        alpha: f64,
    },
    /// IME入力モードの切替イベント
    /// on=true  → 日本語入力モード (あ/カ) に移行 → β_writing を使用
    /// on=false → 英数直接入力モード (A) に移行   → β_coding を使用
    ImeState {
        timestamp: u64,
        on: bool,
        active: bool,
    },
    /// ユーザーが「開始する」を押した時刻 (セッション境界マーカー)
    SessionStart { timestamp: u64 },
    /// セッション終了マーカー
    End,
}

/// NDJSON形式でセッションデータを書き込むロガー。
/// バックグラウンドスレッドでファイルIOを行うため、
/// 送信側 (分析スレッド) は非ブロッキングで送信できる。
pub struct SessionLogger {
    pub log_path: PathBuf,
    _handle: thread::JoinHandle<()>,
}

impl SessionLogger {
    /// ロガーを開始し、ログエントリ送信用の `Sender` とシャットダウン通知用の `Receiver` を返す。
    /// `Sender` を Clone して複数スレッドから送信可能。
    /// `shutdown_rx` は `LogEntry::End` 処理完了後に値を受信する。
    pub fn start(log_path: PathBuf) -> (Self, Sender<LogEntry>, Receiver<()>) {
        let (tx, rx) = bounded::<LogEntry>(512);
        let (shutdown_tx, shutdown_rx) = bounded::<()>(1);
        let path_clone = log_path.clone();

        let handle = thread::spawn(move || {
            // 親ディレクトリを作成
            if let Some(parent) = path_clone.parent() {
                let _ = fs::create_dir_all(parent);
            }

            let file = match File::create(&path_clone) {
                Ok(f) => f,
                Err(e) => {
                    tracing::error!("SessionLogger: failed to create {:?}: {}", path_clone, e);
                    return;
                }
            };

            let mut writer = BufWriter::new(file);

            // セッション開始メタデータ
            // hmm_version は engine.rs の HMM_VERSION 定数。
            // gse-replay がゴールデンスナップショットと突き合わせる際に
            // 同一バージョンであることを検証する。
            let session_start = now_ms();
            let _ = writeln!(
                writer,
                r#"{{"type":"meta","session_start":{},"hmm_version":"{}"}}"#,
                session_start,
                crate::analysis::engine::HMM_VERSION,
            );

            tracing::info!("SessionLogger: writing to {:?}", path_clone);

            let flush_interval = Duration::from_secs(5);
            let mut last_flush = Instant::now();
            let mut dirty = false;

            loop {
                let timeout = flush_interval.saturating_sub(last_flush.elapsed());
                match rx.recv_timeout(timeout) {
                    Ok(entry) => match entry {
                        LogEntry::Key {
                            vk_code,
                            timestamp,
                            is_press,
                        } => {
                            let _ = writeln!(
                                writer,
                                r#"{{"type":"key","t":{},"vk":{},"press":{}}}"#,
                                timestamp, vk_code, is_press,
                            );
                            dirty = true;
                        }
                        LogEntry::Feat {
                            timestamp,
                            f1,
                            f3,
                            f4,
                            f5,
                            f6,
                            p_flow,
                            p_inc,
                            p_stuck,
                            raw_x,
                            raw_y,
                            ewma_x,
                            ewma_y,
                            obs,
                            alpha,
                        } => {
                            let _ = writeln!(
                                writer,
                                r#"{{"type":"feat","t":{},"f1":{:.2},"f3":{:.4},"f4":{:.2},"f5":{:.1},"f6":{:.4},"p_flow":{:.4},"p_inc":{:.4},"p_stuck":{:.4},"raw_x":{:.4},"raw_y":{:.4},"ewma_x":{:.4},"ewma_y":{:.4},"obs":{},"alpha":{:.2}}}"#,
                                timestamp,
                                f1,
                                f3,
                                f4,
                                f5,
                                f6,
                                p_flow,
                                p_inc,
                                p_stuck,
                                raw_x,
                                raw_y,
                                ewma_x,
                                ewma_y,
                                obs,
                                alpha,
                            );
                            dirty = true;
                        }
                        LogEntry::ImeState {
                            timestamp,
                            on,
                            active,
                        } => {
                            let _ = writeln!(
                                writer,
                                r#"{{"type":"ime_state","t":{},"on":{},"active":{}}}"#,
                                timestamp, on, active,
                            );
                            dirty = true;
                        }
                        LogEntry::SessionStart { timestamp } => {
                            let _ = writeln!(
                                writer,
                                r#"{{"type":"session_start","t":{}}}"#,
                                timestamp,
                            );
                            dirty = true;
                        }
                        LogEntry::End => {
                            let _ =
                                writeln!(writer, r#"{{"type":"meta","session_end":{}}}"#, now_ms());
                            break;
                        }
                    },
                    Err(RecvTimeoutError::Timeout) => {
                        // 5秒間アイドル → バッファフラッシュ
                    }
                    Err(RecvTimeoutError::Disconnected) => break,
                }

                // 5秒間隔でバッファフラッシュ (I/O負荷軽減)
                if dirty && last_flush.elapsed() >= flush_interval {
                    let _ = writer.flush();
                    last_flush = Instant::now();
                    dirty = false;
                }
            }

            let _ = writer.flush();
            // ファイルを閉じ終えたことを quit_app に通知する
            let _ = shutdown_tx.send(());
            tracing::info!("SessionLogger: session closed");
        });

        let logger = Self {
            log_path,
            _handle: handle,
        };

        (logger, tx, shutdown_rx)
    }
}

/// UNIX時刻をミリ秒で返す
fn now_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64
}

/// セッションログの保存先パスを生成する。
/// 優先順位:
///   1. 環境変数 GSE_DATASET → $GSE_DATASET/raw/P000/
///   2. 実行ファイルの兄弟ディレクトリ ../gse-dataset/raw/P000/
///   3. フォールバック: ~/Documents/GSE-sessions/
pub fn default_log_path() -> PathBuf {
    let dir = if let Ok(dataset) = std::env::var("GSE_DATASET") {
        PathBuf::from(dataset).join("raw").join("P000")
    } else if let Ok(exe) = std::env::current_exe() {
        // 開発時: target/debug/gse-prototype.exe → ../../.. = src-tauri → ../../../.. の兄弟
        // Tauri 開発ビルド: src-tauri/target/debug/ から 3 つ上が src-tauri、さらに 1 つ上がプロジェクトルート
        let mut candidate = None;
        let mut dir = exe.parent().map(|p| p.to_path_buf());
        // 最大 5 階層上まで gse-dataset を探す
        for _ in 0..5 {
            if let Some(ref d) = dir {
                let sibling = d.join("gse-dataset").join("raw").join("P000");
                if sibling.exists() {
                    candidate = Some(sibling);
                    break;
                }
                dir = d.parent().map(|p| p.to_path_buf());
            }
        }
        candidate.unwrap_or_else(|| fallback_log_dir())
    } else {
        fallback_log_dir()
    };

    let ts = chrono_like_filename();
    dir.join(format!("gse_{}.ndjson", ts))
}

/// フォールバック: ~/Documents/GSE-sessions/
fn fallback_log_dir() -> PathBuf {
    let base = std::env::var("USERPROFILE")
        .or_else(|_| std::env::var("HOME"))
        .unwrap_or_else(|_| ".".to_string());
    PathBuf::from(base).join("Documents").join("GSE-sessions")
}

/// chrono 非依存のタイムスタンプ文字列生成 (標準ライブラリのみ)
fn chrono_like_filename() -> String {
    // UNIX時刻から YYYYMMDD_HHMMSS を近似生成
    // 完全な精度は不要 (セッション識別に使うだけ)
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

    // 2000-01-01 00:00:00 UTC からの秒数ベースで日時を概算
    // 注: 簡易実装のためタイムゾーンはUTC
    let days_since_epoch = secs / 86400;
    let time_of_day = secs % 86400;
    let h = time_of_day / 3600;
    let m = (time_of_day % 3600) / 60;
    let s = time_of_day % 60;

    // グレゴリオ暦変換 (ユリウス通算日から)
    let jd = days_since_epoch + 2440588; // UNIX epoch = JD 2440588
    let a = jd + 32044;
    let b = (4 * a + 3) / 146097;
    let c = a - (146097 * b) / 4;
    let d = (4 * c + 3) / 1461;
    let e = c - (1461 * d) / 4;
    let m_cal = (5 * e + 2) / 153;
    let day = e - (153 * m_cal + 2) / 5 + 1;
    let month = m_cal + 3 - 12 * (m_cal / 10);
    let year = 100 * b + d - 4800 + m_cal / 10;

    format!("{:04}{:02}{:02}_{:02}{:02}{:02}", year, month, day, h, m, s)
}
