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
    /// `run_replay` (snapshot 検証経路) では step() 再実行で自前生成するため、
    /// 本 variant は読み飛ばし専用 (`timestamp()` も `None` を返し時刻順ソート
    /// から除外)。metrics 経路では `collect_logged_feats()` 側で `LoggedFeatDto`
    /// を使って別途構造化パースする (clock semantic mismatch 対策、
    /// `.steering/20260416-replay-feat-alignment-bug/decisions.md` D1 参照)。
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

/// NDJSON の `{"type":"feat", ...}` 行を `FeatSnapshot` に変換する DTO。
///
/// metrics 経路 (`--metrics`) で production が wall-clock で書いた feat 行を
/// そのまま source of truth として使うための変換型。`run_replay` の step()
/// 再生成は virtual-clock grid のため label と時刻軸が一致せず、metrics の
/// nearest_feat 判定で大量に取りこぼす bug (decisions.md D1) の fix 用。
///
/// ## 同期対象
///
/// フィールド一式は `src-tauri/src/schema_dto.rs` の `LogEntryDto::Feat`
/// (L63-79) と一致させる必要がある。`logger::LogEntry::Feat` に新フィールド
/// が追加されたら schema_dto.rs と本 DTO の両方を更新する。同期漏れは:
/// - schema drift check (emit_schema vs `schema/current.json`) で schema_dto 側は検知可能
/// - 本 DTO 側は serde のデフォルト挙動で「未知フィールドは無視」する
///   (`#[serde(deny_unknown_fields)]` は forward-compat のため **付けない**)
/// - 必要ならテスト層1 (`logged_feat_dto_parses_schema_dto_feat_shape`) で
///   schema_dto::LogEntryDto::Feat が生成するサンプル文字列を本 DTO で
///   受けて round-trip すること。
#[derive(Debug, serde::Deserialize)]
struct LoggedFeatDto {
    #[serde(rename = "t")]
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
}

impl From<LoggedFeatDto> for FeatSnapshot {
    fn from(d: LoggedFeatDto) -> Self {
        FeatSnapshot {
            timestamp: d.timestamp,
            f1: d.f1,
            f3: d.f3,
            f4: d.f4,
            f5: d.f5,
            f6: d.f6,
            p_flow: d.p_flow,
            p_inc: d.p_inc,
            p_stuck: d.p_stuck,
            raw_x: d.raw_x,
            raw_y: d.raw_y,
            ewma_x: d.ewma_x,
            ewma_y: d.ewma_y,
            obs: d.obs,
            alpha: d.alpha,
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

    // metrics 経路は logged feat (production wall-clock) + user_label を使う。
    // run_replay の step() 再生成 (virtual clock) は clock semantic が label と
    // 揃わず label 取りこぼしを起こすため、snapshot 検証以外には使わない
    // (decisions.md D1)。
    if args.metrics {
        let labels = match collect_user_labels(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect user labels: {}", msg);
                return ExitCode::from(1);
            }
        };
        let feats = match collect_logged_feats(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect logged feats: {}", msg);
                return ExitCode::from(1);
            }
        };
        let metrics = compute_session_metrics(&labels, &feats);
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

    // snapshot 経路 (デフォルト JSON 出力 / --snapshot 比較) は run_replay で
    // step() 再実行し決定論を検証する。こちらは従来通り。
    let snapshots = match run_replay(&args.session_path) {
        Ok(s) => s,
        Err(msg) => {
            tracing::error!("replay failed: {}", msg);
            return ExitCode::from(1);
        }
    };

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
    // silent skip の可視化 (security-checker MEDIUM 指摘、collect_logged_feats と同方針)
    let mut parse_failed_lines: u64 = 0;
    let mut unknown_label_count: u64 = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::UserLabel { t, label, .. } = ev {
            if let Some(lc) = LabelClass::parse(&label) {
                out.push(UserLabelEvent {
                    timestamp: t,
                    label: lc,
                });
            } else {
                unknown_label_count += 1;
            }
        }
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            skipped = parse_failed_lines,
            "collect_user_labels: NDJSON lines failed to parse as ReplayEvent"
        );
    }
    if unknown_label_count > 0 {
        tracing::warn!(
            skipped = unknown_label_count,
            "collect_user_labels: user_label entries with unknown label class (forward-compat skip)"
        );
    }
    out.sort_by_key(|l| l.timestamp);
    Ok(out)
}

/// Phase 1: NDJSON の `{"type":"feat", ...}` 行を `FeatSnapshot` 列として抽出する。
///
/// `run_replay` が step() 再実行で生成する virtual-clock feat と異なり、production
/// が wall-clock で書いた feat 行をそのまま source of truth として使う。user_label
/// との時刻軸を揃えるのが目的 (`decisions.md` D1)。未知 type / parse error は
/// silent skip (`collect_user_labels` と同方針)。
fn collect_logged_feats(session_path: &PathBuf) -> Result<Vec<FeatSnapshot>, String> {
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
    let mut out: Vec<FeatSnapshot> = Vec::new();
    // silent skip を可視化する: parse 失敗行数をカウントし件数のみ warn で出す
    // (内容はプライバシーのため出さない)。security-checker MEDIUM 指摘対応。
    let mut parse_failed_lines: u64 = 0;
    let mut feat_decode_failed: u64 = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::Feat(val) = ev {
            match serde_json::from_value::<LoggedFeatDto>(val) {
                Ok(dto) => out.push(dto.into()),
                Err(_) => {
                    feat_decode_failed += 1;
                    continue;
                }
            }
        }
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            skipped = parse_failed_lines,
            "collect_logged_feats: NDJSON lines failed to parse as ReplayEvent"
        );
    }
    if feat_decode_failed > 0 {
        tracing::warn!(
            skipped = feat_decode_failed,
            "collect_logged_feats: feat entries failed to decode as LoggedFeatDto \
             (possible schema drift vs schema_dto::LogEntryDto::Feat)"
        );
    }
    if out.is_empty() {
        tracing::warn!(
            "collect_logged_feats: no feat entries found — metrics will have zero support. \
             Verify session NDJSON was generated by hmm_version >= 0.2.0 with Phase 1 feat logging."
        );
    }
    out.sort_by_key(|f| f.timestamp);
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

// =============================================================================
// Tests — `.steering/20260416-replay-feat-alignment-bug/` Phase A 回帰テスト
// =============================================================================
// 層 1 (unit):       `LoggedFeatDto` の serde デシリアライズ + FeatSnapshot 変換
// 層 2 (integration): 合成 NDJSON (tests/fixtures/phase1_minimal.ndjson) で
//                     `collect_logged_feats` + `compute_session_metrics` を通して
//                     warnings 空 + support=1 を確認
// 層 3 (回帰):         実データから key を除去した fixture
//                     (tests/fixtures/phase1_ime_heavy.ndjson) で warnings < 2
//                     かつ confusion matrix 合計 ≥ 4 を確認。将来 metrics 経路を
//                     regen に戻す変更が入ったら CI で落とす役割。
#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    fn fixture_path(name: &str) -> PathBuf {
        let mut p = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        p.push("tests");
        p.push("fixtures");
        p.push(name);
        p
    }

    /// 層 1: NDJSON の 1 行文字列を `LoggedFeatDto` にデシリアライズし、
    /// `FeatSnapshot` への変換でフィールドが一致することを確認する。
    /// schema_dto.rs の LogEntryDto::Feat と本 DTO が乖離したら落ちる。
    #[test]
    fn logged_feat_dto_deserialize_matches_ndjson() {
        let line = r#"{"type":"feat","t":1700000001000,"f1":140.0,"f3":0.0,"f4":4.0,"f5":0.0,"f6":0.0,"p_flow":0.85,"p_inc":0.10,"p_stuck":0.05,"raw_x":0.0,"raw_y":0.6,"ewma_x":0.07,"ewma_y":0.74,"obs":3,"alpha":0.3}"#;
        let ev: ReplayEvent = serde_json::from_str(line).expect("parse ReplayEvent");
        let val = match ev {
            ReplayEvent::Feat(v) => v,
            _ => panic!("expected ReplayEvent::Feat variant"),
        };
        let dto: LoggedFeatDto = serde_json::from_value(val).expect("parse LoggedFeatDto");
        let feat: FeatSnapshot = dto.into();
        assert_eq!(feat.timestamp, 1_700_000_001_000);
        assert!((feat.f1 - 140.0).abs() < 1e-9);
        assert!((feat.p_flow - 0.85).abs() < 1e-9);
        assert!((feat.p_inc - 0.10).abs() < 1e-9);
        assert!((feat.p_stuck - 0.05).abs() < 1e-9);
        assert_eq!(feat.obs, 3);
        assert!((feat.alpha - 0.3).abs() < 1e-9);
    }

    /// 層 2: 合成 NDJSON fixture で `collect_logged_feats` +
    /// `compute_session_metrics` のパスを通す。warnings 空 + flow support=1 を
    /// 期待する (label と feat が ±100ms で揃っている設計)。
    #[test]
    fn collect_logged_feats_plus_metrics_matches_minimal_fixture() {
        let path = fixture_path("phase1_minimal.ndjson");
        let labels = collect_user_labels(&path).expect("collect_user_labels");
        let feats = collect_logged_feats(&path).expect("collect_logged_feats");
        assert_eq!(feats.len(), 3, "minimal fixture has 3 feat lines");
        assert_eq!(labels.len(), 1, "minimal fixture has 1 user_label line");
        let m = compute_session_metrics(&labels, &feats);
        assert_eq!(m.total_labels, 1);
        assert!(
            m.warnings.is_empty(),
            "warnings should be empty on aligned fixture, got {:?}",
            m.warnings
        );
        // Flow label @t=2100 の最近傍 feat @t=2000 で p_flow=0.88 → argmax flow → tp=1
        let flow_metrics = m
            .per_class
            .iter()
            .find(|c| c.class == LabelClass::Flow)
            .expect("flow per_class");
        assert_eq!(flow_metrics.support, 1);
    }

    /// 層 3 (実データ回帰): key 行を除去した real fixture で alignment を確認する。
    /// 元 `gse_20260415_144120.ndjson` は 6 labels × 96 feat (wall-clock 1Hz)。
    /// 全ラベルが ±500ms 以内に feat を持つため warnings は **0 (第一 assert)** が
    /// 期待。将来 regen 経路に戻る / IME auto-reset semantics が再度ずれる regression
    /// があれば warnings > 0 で落ちる。
    /// - fix 前 (regen): warnings=6 / matched=0
    /// - fix 後 (logged): warnings=0 / matched=6 (Phase D-2 実測、2026-04-16)
    /// matched 閾値は 6 件全マッチを要件に格上げ (code-reviewer M5 対応)。
    #[test]
    fn real_ime_heavy_fixture_warnings_minimal_and_matches_most_labels() {
        const EXPECTED_LABELS: usize = 6;
        const EXPECTED_MIN_FEATS: usize = 90; // 元 96 件、fixture 切り出しで微減許容
        const EXPECTED_MATCHED_LABELS: u32 = 6; // 全 label が ±1000ms 内に logged feat を持つ

        let path = fixture_path("phase1_ime_heavy.ndjson");
        let labels = collect_user_labels(&path).expect("collect_user_labels");
        let feats = collect_logged_feats(&path).expect("collect_logged_feats");
        assert_eq!(labels.len(), EXPECTED_LABELS);
        assert!(
            feats.len() >= EXPECTED_MIN_FEATS,
            "expected ~96 logged feats, got {}",
            feats.len()
        );
        let m = compute_session_metrics(&labels, &feats);
        assert_eq!(m.total_labels, EXPECTED_LABELS as u32);
        // 第一 assert: warnings 0 (alignment 完全成立が要件)
        assert!(
            m.warnings.is_empty(),
            "expected warnings == 0 on aligned real fixture (regression would indicate \
             regen feat path re-introduced or IME pause semantics changed), got {}: {:?}",
            m.warnings.len(),
            m.warnings
        );
        let matched: u32 = m.confusion.matrix.iter().flatten().sum();
        assert_eq!(
            matched, EXPECTED_MATCHED_LABELS,
            "expected all {} labels matched into confusion matrix, got {}",
            EXPECTED_MATCHED_LABELS, matched
        );
    }

    /// 層 1 拡張 (M2 対応): `schema_dto::LogEntryDto::Feat` が生成する JSON を
    /// `LoggedFeatDto` で受けて round-trip する。両者のフィールド定義が drift
    /// したら serde が落とす or 無視で値が 0 になるため CI で検知できる。
    /// (obs: schema_dto は u64 / LoggedFeatDto は usize で型差あり。serde_json は
    /// u64 → usize の範囲内変換を許すため実用上問題ない点も同時に担保)。
    #[test]
    fn logged_feat_dto_round_trips_schema_dto_feat_shape() {
        use gse_next_lib::schema_dto::LogEntryDto;
        let src = LogEntryDto::Feat {
            t: 1_700_000_042_000,
            f1: 120.5,
            f3: 0.125,
            f4: 7.0,
            f5: 2.5,
            f6: 0.333,
            p_flow: 0.6,
            p_inc: 0.25,
            p_stuck: 0.15,
            raw_x: 0.1,
            raw_y: 0.8,
            ewma_x: 0.05,
            ewma_y: 0.7,
            obs: 11,
            alpha: 0.2,
        };
        let json = serde_json::to_string(&src).expect("serialize LogEntryDto::Feat");
        let ev: ReplayEvent =
            serde_json::from_str(&json).expect("parse as ReplayEvent (type=feat)");
        let val = match ev {
            ReplayEvent::Feat(v) => v,
            _ => panic!(
                "expected ReplayEvent::Feat from schema_dto::LogEntryDto::Feat, json = {}",
                json
            ),
        };
        let dto: LoggedFeatDto = serde_json::from_value(val).expect("LoggedFeatDto from_value");
        let feat: FeatSnapshot = dto.into();
        assert_eq!(feat.timestamp, 1_700_000_042_000);
        assert!((feat.f1 - 120.5).abs() < 1e-9);
        assert!((feat.p_flow - 0.6).abs() < 1e-9);
        assert_eq!(feat.obs, 11);
        assert!((feat.alpha - 0.2).abs() < 1e-9);
    }
}
