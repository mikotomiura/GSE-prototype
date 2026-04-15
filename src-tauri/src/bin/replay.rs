//! gse-replay — セッション NDJSON リプレイ CLI (Phase 0 P0-4)
//!
//! 既存の NDJSON セッションログを入力に、`analysis::loop_step::step()` を
//! 再実行して `FeatSnapshot` 列を生成する。
//!
//! # 使い方
//!
//! ```text
//! gse-replay <session.ndjson>                        # stdout に JSON 配列を出力
//! gse-replay <session.ndjson> --snapshot <file>      # 既存スナップショットと完全一致比較
//! ```
//!
//! # 設計
//!
//! - 仮想時刻は 1 秒刻みでゲートを発火させつつ、イベントは NDJSON の `t`
//!   タイムスタンプそのものを `step()` に渡す。
//! - `ReplayEvent` は `logger::LogEntry` とは独立した Deserialize 専用 enum。
//!   書き出しと読み込みの責務を分離し、NDJSON のフィールド名 (`t` / `vk` /
//!   `press` 等) に一致させる。
//! - ime_open は NDJSON の `ime_state.on` を追跡して `step()` 引数に渡す。
//! - 出力 JSON は `serde_json::to_string_pretty`（可読性重視、`diff` 容易）。
//!
//! # 関連
//!
//! - `docs/architecture.md` §4.7 沈黙 3 状態機構
//! - `.steering/20260414-improvement-roadmap/design.md` §0.2

use std::fs::File;
use std::io::{BufRead, BufReader, Write};
use std::path::PathBuf;
use std::process::ExitCode;

use gse_next_lib::analysis::engine::{CognitiveStateEngine, HMM_VERSION};
use gse_next_lib::analysis::features::InputEvent;
use gse_next_lib::analysis::loop_step::{
    step, AnalysisState, FeatSnapshot, LoopInput, ENGINE_TICK_MS,
};
use gse_next_lib::analysis::metrics::{
    compute_session_metrics, format_pretty, LabelClass, UserLabelEvent,
};

/// 入力 NDJSON のサイズ上限 (500 MB)。
///
/// `BufReader::lines()` + `Vec<ReplayEvent>` 蓄積で読むため、
/// 上限なしだとメモリ枯渇で OOM する可能性がある (security-checker MEDIUM 指摘)。
/// 10 分セッションの NDJSON は通常 数 MB なので 500 MB は十分広いバッファ。
const MAX_SESSION_BYTES: u64 = 500 * 1024 * 1024;

/// NDJSON の 1 行を表す Deserialize 専用 enum。
///
/// `logger::LogEntry` とは意図的に別型。`logger` は書き出し専用・`ReplayEvent`
/// は読み込み専用として責務を分離する。JSON のフィールド名は NDJSON 実形式に
/// 完全一致させる（例: `timestamp` ではなく `t`、`vk_code` ではなく `vk`）。
#[derive(Debug, serde::Deserialize)]
#[serde(tag = "type")]
enum ReplayEvent {
    /// `{"type":"meta","session_start":...,"hmm_version":"..."}` または
    /// `{"type":"meta","session_end":...}` のいずれか。
    #[serde(rename = "meta")]
    Meta {
        session_start: Option<u64>,
        #[allow(dead_code)]
        session_end: Option<u64>,
        hmm_version: Option<String>,
    },
    /// `start_session` コマンド発火時刻マーカー。replay では extractor を
    /// リセットして「session 境界」を再現するために使う。
    #[serde(rename = "session_start")]
    SessionStart { t: u64 },
    /// キーストローク。vk_code は Windows 規約 (macOS 側はフック層で変換済み)。
    #[serde(rename = "key")]
    Key { t: u64, vk: u32, press: bool },
    /// IME 状態変化。`on` は IME モード（β 切替用）、`active` は候補ウィンドウ
    /// の開閉（engine pause 用）。
    #[serde(rename = "ime_state")]
    ImeState { t: u64, on: bool, active: bool },
    /// 既存セッションの Feat エントリ。
    ///
    /// replay は FeatSnapshot 列を step() 再実行で自前生成するため、本
    /// variant は入力からの読み飛ばし専用（`timestamp()` も `None` を返し
    /// 時刻順ソートから除外される）。内容検証はしない (`serde_json::Value`)。
    #[serde(rename = "feat")]
    Feat(#[allow(dead_code)] serde_json::Value),
    /// Phase 1 Ground Truth ラベル。`--metrics` で評価対象として突き合わせる。
    /// `--snapshot` / デフォルト (snapshot 出力) の経路では読み飛ばす。
    #[serde(rename = "user_label")]
    UserLabel {
        t: u64,
        label: String,
        #[allow(dead_code)]
        recovered_at: Option<u64>,
    },
}

impl ReplayEvent {
    /// タイムスタンプを取り出す（Meta は `session_start` フィールドから）。
    /// `None` は時刻順ソートから除外する（既存 Feat など）。
    fn timestamp(&self) -> Option<u64> {
        match self {
            ReplayEvent::Meta { session_start, .. } => *session_start,
            ReplayEvent::SessionStart { t } => Some(*t),
            ReplayEvent::Key { t, .. } => Some(*t),
            ReplayEvent::ImeState { t, .. } => Some(*t),
            ReplayEvent::Feat(_) => None,
            // UserLabel は再実行対象ではない (ゲート進行を動かさない)。
            // timestamp() から None を返して時刻順ソートから除外し、
            // metrics 算出経路で別途抽出する。
            ReplayEvent::UserLabel { .. } => None,
        }
    }
}

/// vk_code から is_backspace を再計算。
///
/// 既存の hook_windows.rs:304 と hook_macos.rs:340 の判定を複製:
/// Windows 規約 0x08 (VK_BACK) / 0x2E (VK_DELETE) が true。
fn is_backspace(vk: u32) -> bool {
    vk == 0x08 || vk == 0x2E
}

/// コマンドライン引数をパース。
struct Args {
    session_path: PathBuf,
    snapshot_path: Option<PathBuf>,
    metrics: bool,
    json: bool,
}

fn parse_args() -> Result<Args, String> {
    let mut args: Vec<String> = std::env::args().skip(1).collect();
    if args.is_empty() || args.iter().any(|a| a == "-h" || a == "--help") {
        return Err(usage());
    }

    let mut snapshot_path = None;
    // --snapshot <path> フラグを検出・除去
    if let Some(pos) = args.iter().position(|a| a == "--snapshot") {
        if pos + 1 >= args.len() {
            return Err("--snapshot requires a path argument".to_string());
        }
        let path = args.remove(pos + 1);
        args.remove(pos);
        snapshot_path = Some(PathBuf::from(path));
    }

    // --metrics / --json フラグを検出・除去（Phase 1 Task 2）
    // --snapshot と同じ position+remove パターンで揃え、位置引数が偶然
    // --metrics と一致するパスを持っても誤って食わないようにする。
    let metrics = if let Some(pos) = args.iter().position(|a| a == "--metrics") {
        args.remove(pos);
        true
    } else {
        false
    };
    let json = if let Some(pos) = args.iter().position(|a| a == "--json") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --metrics と --snapshot は排他（役割が完全に異なる）
    if metrics && snapshot_path.is_some() {
        return Err("--metrics and --snapshot are mutually exclusive".to_string());
    }
    // --json は --metrics 併用時のみ意味を持つ
    if json && !metrics {
        return Err("--json requires --metrics".to_string());
    }

    if args.len() != 1 {
        return Err(format!(
            "expected 1 positional argument (session.ndjson), got {}",
            args.len()
        ));
    }

    Ok(Args {
        session_path: PathBuf::from(args.into_iter().next().unwrap()),
        snapshot_path,
        metrics,
        json,
    })
}

fn usage() -> String {
    String::from(
        "gse-replay — NDJSON セッションを再実行し FeatSnapshot 列を生成\n\n\
         USAGE:\n    \
         gse-replay <session.ndjson> [--snapshot <golden.json>]\n    \
         gse-replay <session.ndjson> --metrics [--json]\n\n\
         OPTIONS:\n    \
         --snapshot <path>   既存 JSON スナップショットと完全一致比較\n    \
         --metrics           UserLabel との混同行列・F1・中央値を算出\n    \
         --json              --metrics の出力を JSON で標準出力へ\n    \
         -h, --help          このヘルプを表示\n",
    )
}

fn main() -> ExitCode {
    // 最小 tracing subscriber (stderr 出力、INFO 以上)。
    // rust-standards ルール 3 準拠: 警告・エラー系は tracing 経由で出す。
    // ただし CLI の「人向け結果メッセージ」(usage / OK 一致 / MISMATCH 差分) は
    // ログではなくコマンド出力として writeln!(stderr, ...) に残す。
    // `try_init` は既に subscriber が登録済みでもエラーにならない。
    let _ = tracing_subscriber::fmt()
        .with_writer(std::io::stderr)
        .with_target(false)
        .without_time()
        .try_init();

    let args = match parse_args() {
        Ok(a) => a,
        Err(msg) => {
            let _ = writeln!(std::io::stderr(), "{}", msg);
            return ExitCode::from(2);
        }
    };

    let snapshots = match run_replay(&args.session_path) {
        Ok(s) => s,
        Err(msg) => {
            tracing::error!("replay failed: {}", msg);
            return ExitCode::from(1);
        }
    };

    if args.metrics {
        // Phase 1 Task 2: GT ラベル × 推定確率の突き合わせメトリクス算出。
        // UserLabel は run_replay では使わないため、セッション NDJSON を再度開いて抽出する
        // (ファイルサイズは MAX_SESSION_BYTES でガード済み)。
        let labels = match collect_user_labels(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect user labels: {}", msg);
                return ExitCode::from(1);
            }
        };
        let metrics = compute_session_metrics(&labels, &snapshots);
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&metrics) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize metrics: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_pretty(&metrics));
        }
        return ExitCode::SUCCESS;
    }

    match args.snapshot_path {
        None => {
            // stdout に JSON 配列を出力（データ出力、ログではない）
            let json = match serde_json::to_string_pretty(&snapshots) {
                Ok(s) => s,
                Err(e) => {
                    tracing::error!("failed to serialize snapshots: {}", e);
                    return ExitCode::from(1);
                }
            };
            let stdout = std::io::stdout();
            let mut lock = stdout.lock();
            let _ = writeln!(lock, "{}", json);
            ExitCode::SUCCESS
        }
        Some(path) => {
            // 既存スナップショットと比較
            match compare_snapshots(&snapshots, &path) {
                Ok(()) => {
                    let _ = writeln!(
                        std::io::stderr(),
                        "OK: {} snapshots match {}",
                        snapshots.len(),
                        path.display()
                    );
                    ExitCode::SUCCESS
                }
                Err(msg) => {
                    let _ = writeln!(std::io::stderr(), "MISMATCH: {}", msg);
                    ExitCode::from(1)
                }
            }
        }
    }
}

/// Phase 1 Task 2: NDJSON から `{"type":"user_label", ...}` 行のみを抽出する。
///
/// `run_replay` は step() 再実行に関係するイベントのみ処理するため、UserLabel は
/// 読み飛ばされる。metrics 経路では別途抽出する (ファイルを 2 回読むがサイズ上限
/// 500MB + 通常セッション数 MB のため実害なし)。未知 label は警告にせず黙ってスキップ
/// する (将来の互換性のため)。
fn collect_user_labels(session_path: &PathBuf) -> Result<Vec<UserLabelEvent>, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);
    let mut out: Vec<UserLabelEvent> = Vec::new();
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            // collect_user_labels は run_replay の後に呼ばれる。同じ NDJSON を
            // run_replay が通過しているので parse error はここでは起きない前提。
            Err(_) => continue,
        };
        if let ReplayEvent::UserLabel { t, label, .. } = ev {
            if let Some(lc) = LabelClass::parse(&label) {
                out.push(UserLabelEvent {
                    timestamp: t,
                    label: lc,
                });
            }
        }
    }
    out.sort_by_key(|l| l.timestamp);
    Ok(out)
}

/// NDJSON を読み込み、step() を再実行して FeatSnapshot 列を返す。
fn run_replay(session_path: &PathBuf) -> Result<Vec<FeatSnapshot>, String> {
    // ファイルサイズガード (OOM 防止、security-checker MEDIUM)
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }

    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);

    let mut events: Vec<ReplayEvent> = Vec::new();
    let mut meta_hmm_version: Option<String> = None;

    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = serde_json::from_str(&line)
            .map_err(|e| format!("parse error at line {}: {}", lineno + 1, e))?;
        if let ReplayEvent::Meta { hmm_version, .. } = &ev {
            if let Some(v) = hmm_version {
                meta_hmm_version = Some(v.clone());
            }
        }
        events.push(ev);
    }

    // hmm_version 検証（不一致は WARN のみ、exit はしない）
    if let Some(v) = &meta_hmm_version {
        if v != HMM_VERSION {
            tracing::warn!(
                "session hmm_version = {}, current engine = {}. snapshots may not be comparable.",
                v,
                HMM_VERSION
            );
        }
    }

    // session_start を決定: Meta.session_start → SessionStart.t → 最初のイベントの t
    let session_start_ms = events
        .iter()
        .find_map(|e| match e {
            ReplayEvent::Meta {
                session_start: Some(t),
                ..
            } => Some(*t),
            _ => None,
        })
        .or_else(|| {
            events.iter().find_map(|e| match e {
                ReplayEvent::SessionStart { t } => Some(*t),
                _ => None,
            })
        })
        .or_else(|| events.iter().find_map(|e| e.timestamp()))
        .ok_or_else(|| "no events with timestamps found".to_string())?;

    // 時刻順にソート（既存 Feat は timestamp() == None で除外）
    let mut ordered: Vec<ReplayEvent> = events
        .into_iter()
        .filter(|e| e.timestamp().is_some())
        .collect();
    ordered.sort_by_key(|e| e.timestamp().unwrap_or(0));

    // state + engine を初期化
    let mut state = AnalysisState::new(session_start_ms, 600);
    let engine = CognitiveStateEngine::new();
    let mut ime_open = false;
    let mut snapshots: Vec<FeatSnapshot> = Vec::new();

    // 各イベントの前に、そのイベントの時刻までゲートを進める
    for ev in ordered {
        let ev_ms = ev.timestamp().unwrap();

        // イベント時刻に達するまでゲートを進める (1Hz 推論を仮想時刻で駆動)
        while state.next_engine_update_ms <= ev_ms {
            let tick_ms = state.next_engine_update_ms;
            let out = step(&mut state, &engine, None, tick_ms, ime_open);
            if let Some(f) = out.feat {
                snapshots.push(f);
            }
            // 無限ループ防止セーフティガード: step() が next_engine_update_ms を
            // 進めなかった場合（通常は engine pause で gate スキップ時）。
            // 通常運用では発生しないが、step() の実装に回帰があった際は
            // tracing::error + debug_assert でバグとして可視化する。
            if state.next_engine_update_ms == tick_ms {
                tracing::error!(
                    tick_ms = tick_ms,
                    "step() did not advance next_engine_update_ms — forcing +ENGINE_TICK_MS"
                );
                debug_assert!(
                    false,
                    "step() must advance next_engine_update_ms on each gate tick"
                );
                state.next_engine_update_ms = tick_ms + ENGINE_TICK_MS;
            }
        }

        // イベント処理
        match ev {
            ReplayEvent::Meta { .. } | ReplayEvent::Feat(_) | ReplayEvent::UserLabel { .. } => {
                // Meta / Feat / UserLabel はゲート進行済み、追加処理不要
                // (UserLabel は metrics 経路で collect_user_labels 側で抽出)
            }
            ReplayEvent::SessionStart { t } => {
                // 本番の start_session リセットを再現
                state.reset(t, 600);
            }
            ReplayEvent::Key { t, vk, press } => {
                let event = InputEvent {
                    vk_code: vk,
                    timestamp: t,
                    is_press: press,
                    is_repeat: false, // step() が pressed_keys で検出する
                    is_backspace: is_backspace(vk),
                };
                let out = step(
                    &mut state,
                    &engine,
                    Some(LoopInput::Key(event)),
                    t,
                    ime_open,
                );
                if let Some(f) = out.feat {
                    snapshots.push(f);
                }
            }
            ReplayEvent::ImeState { t, on, active } => {
                ime_open = on;
                let out = step(
                    &mut state,
                    &engine,
                    Some(LoopInput::ImeActivate { active }),
                    t,
                    ime_open,
                );
                if let Some(f) = out.feat {
                    snapshots.push(f);
                }
            }
        }
    }

    Ok(snapshots)
}

/// 既存スナップショットと比較。byte-equal (JSON 正規化後) を期待する。
fn compare_snapshots(actual: &[FeatSnapshot], expected_path: &PathBuf) -> Result<(), String> {
    let expected_str = std::fs::read_to_string(expected_path)
        .map_err(|e| format!("cannot read {}: {}", expected_path.display(), e))?;
    let expected: Vec<FeatSnapshot> = serde_json::from_str(&expected_str)
        .map_err(|e| format!("parse error in {}: {}", expected_path.display(), e))?;

    if actual.len() != expected.len() {
        return Err(format!(
            "length mismatch: actual={}, expected={}",
            actual.len(),
            expected.len()
        ));
    }

    for (i, (a, e)) in actual.iter().zip(expected.iter()).enumerate() {
        if a != e {
            return Err(format!(
                "snapshot[{}] differs:\n  actual   = {}\n  expected = {}",
                i,
                serde_json::to_string(a).unwrap_or_default(),
                serde_json::to_string(e).unwrap_or_default(),
            ));
        }
    }

    Ok(())
}
