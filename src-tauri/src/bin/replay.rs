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
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use gse_next_lib::analysis::calibration_eval::{
    compute_calibration_metrics, format_calibration_pretty, AggSpec, ProbeRecord, ProbeSourceKind,
    QuadrantKind, SessionData, SkipReasonKind, TrackKind, VignetteRecord,
    HOLDOUT_CALIBRATION_SESSIONS,
};
use gse_next_lib::analysis::engine::{CognitiveStateEngine, HMM_VERSION};
use gse_next_lib::analysis::features::InputEvent;
use gse_next_lib::analysis::intervention::InterventionThresholds;
use gse_next_lib::analysis::intervention_eval::{
    compute_correction_floor_report, compute_intervention_metrics, compute_intervention_sweep,
    compute_nudge_diagnostic, format_correction_floor_pretty, format_intervention_pretty,
    format_intervention_sweep_pretty, format_nudge_diagnostic_pretty, SweepInput,
    DEFAULT_DEFER_RECOVERY_WINDOW_MS, DEFAULT_SWEEP_NUDGE_NEED,
};
use gse_next_lib::analysis::loop_step::{
    step, AnalysisState, FeatSnapshot, LoopInput, ENGINE_TICK_MS,
};
use gse_next_lib::analysis::metrics::{
    compute_range_metrics, compute_session_metrics, format_pretty, LabelClass, RangeLabel,
    UserLabelEvent,
};

/// 入力 NDJSON のサイズ上限 (500 MB)。
///
/// `BufReader::lines()` + `Vec<ReplayEvent>` 蓄積で読むため、
/// 上限なしだとメモリ枯渇で OOM する可能性がある (security-checker MEDIUM 指摘)。
/// 10 分セッションの NDJSON は通常 数 MB なので 500 MB は十分広いバッファ。
const MAX_SESSION_BYTES: u64 = 500 * 1024 * 1024;

/// `--calibration` で受け付ける 1 被験者あたりのセッションファイル数の上限。
///
/// 各ファイルは `MAX_SESSION_BYTES` で保護されるが、ファイル**数**が無制限だと
/// `500MB × 数 × 2 パス` のリソースを消費しうる (security-checker MEDIUM 指摘)。
/// 実運用では 1 被験者 10 セッション程度なので 64 は十分広い。
const MAX_CALIBRATION_FILES: usize = 64;

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
    /// ペーストイベント (Ctrl+V / Cmd+V) の発生時刻マーカー。
    /// features/HMM には未使用のため replay では読み飛ばす (`timestamp()==None`)。
    /// 本 variant が無いと NDJSON に paste 行があるとき deserialize でエラーになる。
    #[serde(rename = "paste")]
    Paste {
        #[allow(dead_code)]
        t: u64,
    },
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
    /// 事後レビュー用ブックマークマーカー。`--segment` でハイライト表示に使う。
    /// `--snapshot` / `--metrics` の経路では読み飛ばす。
    #[serde(rename = "review_marker")]
    ReviewMarker {
        #[allow(dead_code)]
        t: u64,
    },
    /// Phase 2b IME Shadow Features。replay では読み飛ばす。
    #[serde(rename = "ime_shadow")]
    ImeShadow(#[allow(dead_code)] serde_json::Value),
    /// MVP Opportunity 判定ログ。replay では読み飛ばす。
    #[serde(rename = "intervention_decision")]
    InterventionDecision(#[allow(dead_code)] serde_json::Value),
    /// v0.3 較正スモーク: セッション宣言。`--calibration` 経路で track を抽出する。
    /// snapshot/run_replay 経路では `timestamp()==None` で読み飛ばす。
    #[serde(rename = "session_meta")]
    SessionMeta {
        track: String,
        #[allow(dead_code)]
        task_kind: String,
        #[allow(dead_code)]
        monk_mode: bool,
        #[allow(dead_code)]
        intervention_enabled: bool,
        #[allow(dead_code)]
        ts: u64,
    },
    /// v0.3 較正スモーク: ランダムプローブ割当の監査記録。`--calibration` で件数を数える。
    #[serde(rename = "probe_assignment")]
    ProbeAssignment {
        #[allow(dead_code)]
        probe_id: String,
        #[allow(dead_code)]
        scheduled_ts: u64,
        #[allow(dead_code)]
        session_elapsed_ms: u64,
    },
    /// v0.3 較正スモーク: 主データ (リアルタイム/自己マーカー回答)。`--calibration` で ProbeRecord 化する。
    #[serde(rename = "realtime_label")]
    RealtimeLabel {
        #[allow(dead_code)]
        probe_id: Option<String>,
        source: String,
        q1_friction: Option<u8>,
        q2_progress: Option<u8>,
        answered: bool,
        skip_reason: String,
        latency_ms: u64,
        analysis_window_start_ms: u64,
        analysis_window_end_ms: u64,
        #[allow(dead_code)]
        ts: u64,
    },
    /// v0.3 較正スモーク: 尺度理解テスト回答。`--calibration` で VignetteRecord 化する。
    #[serde(rename = "vignette_response")]
    VignetteResponse {
        #[allow(dead_code)]
        vignette_id: String,
        expected_quadrant: String,
        q1_friction: u8,
        q2_progress: u8,
        #[allow(dead_code)]
        ts: u64,
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
            // Paste は記録専用 (回数集計用)。step() 再実行に影響しないため除外する。
            ReplayEvent::Paste { .. } => None,
            ReplayEvent::ImeState { t, .. } => Some(*t),
            ReplayEvent::Feat(_) => None,
            // UserLabel は再実行対象ではない (ゲート進行を動かさない)。
            // timestamp() から None を返して時刻順ソートから除外し、
            // metrics 算出経路で別途抽出する。
            ReplayEvent::UserLabel { .. } => None,
            ReplayEvent::ReviewMarker { .. } => None,
            ReplayEvent::ImeShadow(_) => None,
            ReplayEvent::InterventionDecision(_) => None,
            // v0.3 較正 variant は --calibration 専用コレクタで別途抽出する。
            // run_replay (snapshot 経路) の時刻順ソートからは除外する (UserLabel と同方針)。
            ReplayEvent::SessionMeta { .. } => None,
            ReplayEvent::ProbeAssignment { .. } => None,
            ReplayEvent::RealtimeLabel { .. } => None,
            ReplayEvent::VignetteResponse { .. } => None,
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

/// `LoggedFeatDto` → `FeatSnapshot` の安全な変換。
///
/// rust-standards Skill: `anyhow::Result` ではなく `Result<_, String>` を使う
/// (既存 `collect_user_labels` / `collect_logged_feats` と対称、bin crate 層での
/// 軽量エラー通知)。
///
/// 検証ルール (security-checker M3 対応、`decisions.md` D8 で詳細化):
/// - `p_flow`, `p_inc`, `p_stuck`: `is_finite()` かつ `[0.0, 1.0]`
/// - 確率和 `p_flow + p_inc + p_stuck`: `[0.98, 1.02]` (logger `{:.4}` 丸め誤差許容)
/// - `alpha`: `is_finite()` かつ `[0.0, 1.0]`
/// - `f1, f3, f4, f5, f6, raw_x, raw_y, ewma_x, ewma_y`: `is_finite()` かつ非負
///
/// NaN が `argmax_class` の `>=` 比較を全て false にして silent に Stuck 誤分類を
/// 招いていた問題 (`metrics.rs:270-277`) を入力側で止める。
impl TryFrom<LoggedFeatDto> for FeatSnapshot {
    type Error = String;

    fn try_from(d: LoggedFeatDto) -> Result<Self, Self::Error> {
        // 確率の範囲検証
        for (name, p) in [
            ("p_flow", d.p_flow),
            ("p_inc", d.p_inc),
            ("p_stuck", d.p_stuck),
        ] {
            if !p.is_finite() {
                return Err(format!("{} is not finite (NaN/Inf): {}", name, p));
            }
            if !(0.0..=1.0).contains(&p) {
                return Err(format!("{} out of range [0.0, 1.0]: {}", name, p));
            }
        }

        // 確率和検証 (4 桁丸め誤差許容)
        let sum = d.p_flow + d.p_inc + d.p_stuck;
        if !sum.is_finite() || !(0.98..=1.02).contains(&sum) {
            return Err(format!(
                "probability sum out of range [0.98, 1.02]: p_flow={} p_inc={} p_stuck={} sum={}",
                d.p_flow, d.p_inc, d.p_stuck, sum
            ));
        }

        // alpha
        if !d.alpha.is_finite() || !(0.0..=1.0).contains(&d.alpha) {
            return Err(format!("alpha out of range [0.0, 1.0]: {}", d.alpha));
        }

        // 特徴量: is_finite + 非負
        for (name, v) in [
            ("f1", d.f1),
            ("f3", d.f3),
            ("f4", d.f4),
            ("f5", d.f5),
            ("f6", d.f6),
            ("raw_x", d.raw_x),
            ("raw_y", d.raw_y),
            ("ewma_x", d.ewma_x),
            ("ewma_y", d.ewma_y),
        ] {
            if !v.is_finite() {
                return Err(format!("{} is not finite (NaN/Inf): {}", name, v));
            }
            if v < 0.0 {
                return Err(format!("{} is negative: {}", name, v));
            }
        }

        Ok(FeatSnapshot {
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
        })
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
    /// --segment: セッションを活動境界で分割し .segments.txt を生成
    segment: bool,
    /// --segments <path>: .segments.txt を読み込み範囲マッチングでメトリクス算出
    segments_path: Option<PathBuf>,
    /// --intervention: v2 介入ポリシーをオフライン反実仮想リプレイし HIR/DC 等を算出
    intervention: bool,
    /// --calibration: v0.3 較正解析 (時間隔離窓 C-index / 2段ゲート / MNAR / ビネット)。
    /// 1 被験者の複数セッションを受けるため、追加の positional を `extra_sessions` に積む。
    calibration: bool,
    /// --sweep: nudge_need を 0.50–0.90 で振り reason 別 HIR / 閾値別指標をプール出力 (Phase 0)。
    /// `--calibration` と同様に 1 被験者の複数セッションを受ける。
    sweep: bool,
    /// --nudge-diag: ACT decision を reason×GT で層別し特徴量分布を出す (FP/TP 分離診断)。
    /// `--sweep` と同様に複数セッションを受ける。
    nudge_diag: bool,
    /// --corr-floor: correction_after_pause veto floor (f4/f6) の counterfactual 候補比較 (Step 2)。
    /// `--sweep` と同様に複数セッションを受ける。
    corr_floor: bool,
    /// `--calibration` / `--sweep` / `--nudge-diag` / `--corr-floor` の 2 個目以降の positional。
    extra_sessions: Vec<PathBuf>,
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
    // --segment フラグ
    let segment = if let Some(pos) = args.iter().position(|a| a == "--segment") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --segments <path> フラグ
    let segments_path = if let Some(pos) = args.iter().position(|a| a == "--segments") {
        if pos + 1 >= args.len() {
            return Err("--segments requires a path argument".to_string());
        }
        let path = args.remove(pos + 1);
        args.remove(pos);
        Some(PathBuf::from(path))
    } else {
        None
    };

    // --intervention フラグ
    let intervention = if let Some(pos) = args.iter().position(|a| a == "--intervention") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --calibration フラグ (v0.3 較正解析)
    let calibration = if let Some(pos) = args.iter().position(|a| a == "--calibration") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --sweep フラグ (Phase 0 nudge_need threshold sweep)
    let sweep = if let Some(pos) = args.iter().position(|a| a == "--sweep") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --nudge-diag フラグ (ACT を reason×GT で層別した特徴量診断)
    let nudge_diag = if let Some(pos) = args.iter().position(|a| a == "--nudge-diag") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --corr-floor フラグ (correction_after_pause veto floor の counterfactual)
    let corr_floor = if let Some(pos) = args.iter().position(|a| a == "--corr-floor") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --json は集計系モード併用時のみ意味を持つ
    if json
        && !metrics
        && segments_path.is_none()
        && !intervention
        && !calibration
        && !sweep
        && !nudge_diag
        && !corr_floor
    {
        return Err(
            "--json requires --metrics, --segments, --intervention, --calibration, --sweep, --nudge-diag, or --corr-floor"
                .to_string(),
        );
    }

    // 排他チェック: 全モードは相互排他
    let mode_count = [
        metrics,
        segment,
        segments_path.is_some(),
        snapshot_path.is_some(),
        intervention,
        calibration,
        sweep,
        nudge_diag,
        corr_floor,
    ]
    .iter()
    .filter(|&&v| v)
    .count();
    if mode_count > 1 {
        return Err(
            "--metrics, --segment, --segments, --snapshot, --intervention, --calibration, --sweep, --nudge-diag, --corr-floor are mutually exclusive"
                .to_string(),
        );
    }

    // positional 引数の検証。--calibration / --sweep / --nudge-diag / --corr-floor は複数セッションを
    // 受けるため ≥1 個、それ以外のモードは従来どおり厳密に 1 個。
    if args.is_empty() {
        return Err("expected at least 1 positional argument (session.ndjson)".to_string());
    }
    if !calibration && !sweep && !nudge_diag && !corr_floor && args.len() != 1 {
        return Err(format!(
            "expected 1 positional argument (session.ndjson), got {}",
            args.len()
        ));
    }
    let mut positional_iter = args.into_iter();
    let session_path = PathBuf::from(positional_iter.next().unwrap());
    let extra_sessions: Vec<PathBuf> = positional_iter.map(PathBuf::from).collect();

    Ok(Args {
        session_path,
        snapshot_path,
        metrics,
        json,
        segment,
        segments_path,
        intervention,
        calibration,
        sweep,
        nudge_diag,
        corr_floor,
        extra_sessions,
    })
}

fn usage() -> String {
    String::from(
        "gse-replay — NDJSON セッションを再実行し FeatSnapshot 列を生成\n\n\
         USAGE:\n    \
         gse-replay <session.ndjson> [--snapshot <golden.json>]\n    \
         gse-replay <session.ndjson> --metrics [--json]\n    \
         gse-replay <session.ndjson> --segment\n    \
         gse-replay <session.ndjson> --segments <segments.txt> [--json]\n    \
         gse-replay <session.ndjson> --intervention [--json]\n    \
         gse-replay <s1.ndjson> [s2.ndjson ...] --calibration [--json]\n    \
         gse-replay <s1.ndjson> [s2.ndjson ...] --sweep [--json]\n    \
         gse-replay <s1.ndjson> [s2.ndjson ...] --nudge-diag [--json]\n    \
         gse-replay <s1.ndjson> [s2.ndjson ...] --corr-floor [--json]\n\n\
         OPTIONS:\n    \
         --snapshot <path>   既存 JSON スナップショットと完全一致比較\n    \
         --metrics           UserLabel との混同行列・F1・中央値を算出\n    \
         --segment           活動境界で分割した .segments.txt を生成\n    \
         --segments <path>   .segments.txt を読み込み範囲マッチングでメトリクス算出\n    \
         --intervention      v2 介入ポリシーを反実仮想リプレイし HIR/Precision/Recall/DC/Burden + reason 別分解を算出\n    \
         --calibration       v0.3 較正解析 (時間隔離窓 C-index/2段ゲート/MNAR/ビネット)。1 被験者の複数セッションを時刻順に渡す\n    \
         --sweep             nudge_need を 0.50–0.90 で振り reason 別 HIR / 閾値別指標を複数セッションでプール出力 (production 不変)\n    \
         --nudge-diag        ACT decision を reason×GT で層別し決定時の特徴量分布 (min/med/max) を出力 (FP/TP 分離診断)\n    \
         --corr-floor        correction_after_pause veto floor (f4/f6) の counterfactual 候補比較 (production 不変)\n    \
         --json              集計系モード (--metrics/--segments/--intervention/--calibration/--sweep/--nudge-diag/--corr-floor) の出力を JSON へ\n    \
         -h, --help          このヘルプを表示\n",
    )
}

/// `--sweep` / `--nudge-diag` 共通: positional セッション群を `SweepInput` 列に読み込む。
/// ファイル数が `MAX_CALIBRATION_FILES` を超えたら `Err(ExitCode::from(2))`、
/// 各セッションの読み込み失敗は `Err(ExitCode::from(1))` を返す (stderr / tracing へ出力済み)。
fn collect_sweep_inputs(
    session_path: &Path,
    extra_sessions: &[PathBuf],
) -> Result<Vec<SweepInput>, ExitCode> {
    let mut paths: Vec<PathBuf> = Vec::with_capacity(1 + extra_sessions.len());
    paths.push(session_path.to_path_buf());
    paths.extend(extra_sessions.iter().cloned());

    // ファイル数の上限 (calibration と同じ安全キャップを流用)。
    if paths.len() > MAX_CALIBRATION_FILES {
        let _ = writeln!(
            std::io::stderr(),
            "too many sessions: {} exceeds limit {}",
            paths.len(),
            MAX_CALIBRATION_FILES
        );
        return Err(ExitCode::from(2));
    }

    let mut sessions: Vec<SweepInput> = Vec::with_capacity(paths.len());
    for p in &paths {
        let feats = collect_logged_feats(p).map_err(|msg| {
            tracing::error!("failed to collect logged feats {}: {}", p.display(), msg);
            ExitCode::from(1)
        })?;
        let point_labels = collect_user_labels(p).map_err(|msg| {
            tracing::error!("failed to collect user labels {}: {}", p.display(), msg);
            ExitCode::from(1)
        })?;
        let key_press_ts = collect_key_timestamps(p);
        sessions.push(SweepInput {
            feats,
            point_labels,
            key_press_ts,
        });
    }
    Ok(sessions)
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

    // --segment 経路: セッションを活動境界で分割し .segments.txt を stdout に出力
    if args.segment {
        let feats = match collect_logged_feats(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect logged feats: {}", msg);
                return ExitCode::from(1);
            }
        };
        let markers = collect_review_markers(&args.session_path);
        let key_timestamps = collect_key_timestamps(&args.session_path);
        let segments = build_segments(&feats, &key_timestamps, &markers);
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        let _ = write!(
            lock,
            "{}",
            format_segments_txt(&args.session_path, &segments)
        );
        return ExitCode::SUCCESS;
    }

    // --segments 経路: .segments.txt を読み込み範囲マッチングでメトリクス算出
    if let Some(ref seg_path) = args.segments_path {
        let feats = match collect_logged_feats(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect logged feats: {}", msg);
                return ExitCode::from(1);
            }
        };
        let range_labels = match parse_segments_file(seg_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to parse segments file: {}", msg);
                return ExitCode::from(1);
            }
        };
        let metrics = compute_range_metrics(&range_labels, &feats);
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

    // --intervention 経路: v2 介入ポリシーをオフライン反実仮想リプレイ。
    // metrics 経路と同じく logged feat (wall-clock) を使い、decide() を時刻順に
    // ステップして HIR/Precision/DC/Burden を算出する (decisions.md D1)。
    if args.intervention {
        let feats = match collect_logged_feats(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect logged feats: {}", msg);
                return ExitCode::from(1);
            }
        };
        let labels = match collect_user_labels(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect user labels: {}", msg);
                return ExitCode::from(1);
            }
        };
        let key_press_ts = collect_key_timestamps(&args.session_path);
        let metrics = compute_intervention_metrics(
            &feats,
            &labels,
            &key_press_ts,
            DEFAULT_DEFER_RECOVERY_WINDOW_MS,
            &InterventionThresholds::default(),
        );
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&metrics) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize intervention metrics: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_intervention_pretty(&metrics));
        }
        return ExitCode::SUCCESS;
    }

    // --sweep 経路: nudge_need を 0.50–0.90 (0.05 刻み) で振り、reason 別 HIR / 閾値別の
    // HIR/Precision/Recall/DC/Burden を全セッションでプール出力する (Phase 0、production 不変)。
    // --calibration と同じく複数セッションを受け、各セッションを独立評価してプールする。
    if args.sweep {
        let sessions = match collect_sweep_inputs(&args.session_path, &args.extra_sessions) {
            Ok(s) => s,
            Err(code) => return code,
        };
        let report = compute_intervention_sweep(
            &sessions,
            &DEFAULT_SWEEP_NUDGE_NEED,
            DEFAULT_DEFER_RECOVERY_WINDOW_MS,
        );
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&report) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize sweep report: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_intervention_sweep_pretty(&report));
        }
        return ExitCode::SUCCESS;
    }

    // --nudge-diag 経路: ACT decision を reason×GT で層別し決定時の特徴量分布 (min/median/max) を
    // プール出力する (Phase 0、production 不変)。FP(GT=PROTECT) と TP(GT=STALL) の分離可能性を診断する。
    if args.nudge_diag {
        let sessions = match collect_sweep_inputs(&args.session_path, &args.extra_sessions) {
            Ok(s) => s,
            Err(code) => return code,
        };
        let diag = compute_nudge_diagnostic(&sessions, &InterventionThresholds::default());
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&diag) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize nudge diagnostic: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_nudge_diagnostic_pretty(&diag));
        }
        return ExitCode::SUCCESS;
    }

    // --corr-floor 経路: correction_after_pause veto floor (f4/f6) の counterfactual 候補
    // (baseline / f4 / f6 / both) を全セッションでプール評価し HIR/recall を比較する (production 不変)。
    if args.corr_floor {
        let sessions = match collect_sweep_inputs(&args.session_path, &args.extra_sessions) {
            Ok(s) => s,
            Err(code) => return code,
        };
        let report = compute_correction_floor_report(&sessions, DEFAULT_DEFER_RECOVERY_WINDOW_MS);
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&report) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize correction floor report: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_correction_floor_pretty(&report));
        }
        return ExitCode::SUCCESS;
    }

    // --calibration 経路: v0.3 較正解析 (Task D)。1 被験者の複数セッション NDJSON を時刻順に受け、
    // 時間隔離窓で X/Y を集約 → 被験者内 C-index → holdout → MNAR → ビネット → 二軸性を算出する。
    // frontend を起動せず NDJSON のみを読む。被験者横断の最終ゲートは Task E。
    if args.calibration {
        let mut paths: Vec<PathBuf> = Vec::with_capacity(1 + args.extra_sessions.len());
        paths.push(args.session_path.clone());
        paths.extend(args.extra_sessions.iter().cloned());

        // ファイル数の上限 (各ファイルは MAX_SESSION_BYTES でも保護されるが、数の暴走を防ぐ)。
        if paths.len() > MAX_CALIBRATION_FILES {
            let _ = writeln!(
                std::io::stderr(),
                "too many calibration sessions: {} exceeds limit {}",
                paths.len(),
                MAX_CALIBRATION_FILES
            );
            return ExitCode::from(2);
        }
        // 前向き holdout には main セッション 3 本以上が要る (先頭 2 = 較正)。
        if paths.len() < HOLDOUT_CALIBRATION_SESSIONS + 1 {
            tracing::warn!(
                sessions = paths.len(),
                "calibration: prospective-holdout C-index requires ≥{} sessions (first {} are calibration); \
                 eval set will be empty",
                HOLDOUT_CALIBRATION_SESSIONS + 1,
                HOLDOUT_CALIBRATION_SESSIONS
            );
        }

        let mut sessions: Vec<SessionData> = Vec::with_capacity(paths.len());
        for p in &paths {
            match load_calibration_session(p) {
                Ok(s) => sessions.push(s),
                Err(msg) => {
                    tracing::error!(
                        "failed to load calibration session {}: {}",
                        p.display(),
                        msg
                    );
                    return ExitCode::from(1);
                }
            }
        }
        // 既定の窓集約スペック (ewma の中央値, 設計判断 A)。
        let report = compute_calibration_metrics(&sessions, AggSpec::default());
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&report) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize calibration report: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_calibration_pretty(&report));
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
    let mut feat_validation_failed: u64 = 0;
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
            let dto: LoggedFeatDto = match serde_json::from_value(val) {
                Ok(d) => d,
                Err(_) => {
                    feat_decode_failed += 1;
                    continue;
                }
            };
            // M3: TryFrom で NaN/Inf/範囲外を reject、汚染を metrics 前段で止める
            match FeatSnapshot::try_from(dto) {
                Ok(f) => out.push(f),
                Err(_) => {
                    feat_validation_failed += 1;
                    continue;
                }
            }
        }
    }
    if feat_validation_failed > 0 {
        tracing::warn!(
            skipped = feat_validation_failed,
            "collect_logged_feats: feat entries failed NaN/Inf/range validation \
             (see FeatSnapshot::try_from rules — prevents silent argmax corruption)"
        );
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

/// Task D: 1 セッション NDJSON から較正解析の入力 `SessionData` を構築する。
///
/// 1 パスで session_meta(track) / probe_assignment(件数) / realtime_label(ProbeRecord) /
/// vignette_response(VignetteRecord) を抽出し、X/Y の源となる FeatSnapshot は既存
/// `collect_logged_feats` を再利用する (計 2 パス、`--metrics` 経路と同じ前提)。
/// 未知 source / quadrant / parse 失敗は silent skip (件数のみ warn、内容はプライバシーのため出さない)。
fn load_calibration_session(session_path: &PathBuf) -> Result<SessionData, String> {
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

    let mut track = TrackKind::Main; // session_meta がなければ main 既定
    let mut session_meta_seen = false;
    let mut session_start_ms: Option<u64> = None; // session_meta.ts (時刻単調性検証用)
    let mut probes: Vec<ProbeRecord> = Vec::new();
    let mut vignettes: Vec<VignetteRecord> = Vec::new();
    let mut random_probe_assignment_count: usize = 0;

    let mut parse_failed_lines: u64 = 0;
    let mut unknown_enum_lines: u64 = 0;
    // producer は q を 1..=5 に clamp するが reader は信頼せず再検証する (security-checker MEDIUM)。
    // 手編集/破損 NDJSON で範囲外 q が集計値を静かに歪めるのを防ぐ。
    let mut out_of_range_lines: u64 = 0;

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
        match ev {
            ReplayEvent::SessionMeta { track: t, ts, .. } => {
                // 複数あれば最初の宣言を採用 (通常はセッション先頭に 1 件)。
                if !session_meta_seen {
                    match TrackKind::parse(&t) {
                        Some(tk) => track = tk,
                        None => unknown_enum_lines += 1,
                    }
                    session_start_ms = Some(ts);
                    session_meta_seen = true;
                }
            }
            ReplayEvent::ProbeAssignment { .. } => {
                // probe_assignment は一様ランダムプローブの監査記録 (Recall 分母の定義)。
                random_probe_assignment_count += 1;
            }
            ReplayEvent::RealtimeLabel {
                source,
                q1_friction,
                q2_progress,
                answered,
                skip_reason,
                latency_ms,
                analysis_window_start_ms,
                analysis_window_end_ms,
                ..
            } => {
                let Some(source) = ProbeSourceKind::parse(&source) else {
                    unknown_enum_lines += 1;
                    continue;
                };
                let Some(skip_reason) = SkipReasonKind::parse(&skip_reason) else {
                    unknown_enum_lines += 1;
                    continue;
                };
                // 回答済みは q1/q2 が 1..=5 必須 (producer 不変条件)。範囲外/欠落は破損とみなし skip。
                // skip 回答 (answered=false) は q=None が正常なので検証しない。
                if answered {
                    let q_valid = matches!(q1_friction, Some(q) if (1..=5).contains(&q))
                        && matches!(q2_progress, Some(q) if (1..=5).contains(&q));
                    if !q_valid {
                        out_of_range_lines += 1;
                        continue;
                    }
                }
                probes.push(ProbeRecord {
                    source,
                    answered,
                    q1_friction,
                    q2_progress,
                    skip_reason,
                    latency_ms,
                    window_start_ms: analysis_window_start_ms,
                    window_end_ms: analysis_window_end_ms,
                });
            }
            ReplayEvent::VignetteResponse {
                expected_quadrant,
                q1_friction,
                q2_progress,
                ..
            } => {
                let Some(expected) = QuadrantKind::parse(&expected_quadrant) else {
                    unknown_enum_lines += 1;
                    continue;
                };
                // ビネット q1/q2 も 1..=5 を再検証 (破損 NDJSON で象限推論が歪むのを防ぐ)。
                if !(1..=5).contains(&q1_friction) || !(1..=5).contains(&q2_progress) {
                    out_of_range_lines += 1;
                    continue;
                }
                vignettes.push(VignetteRecord {
                    expected,
                    q1_friction,
                    q2_progress,
                });
            }
            // 較正に無関係な type は読み飛ばす。
            _ => {}
        }
    }

    if parse_failed_lines > 0 {
        tracing::warn!(
            skipped = parse_failed_lines,
            "load_calibration_session: NDJSON lines failed to parse as ReplayEvent"
        );
    }
    if unknown_enum_lines > 0 {
        tracing::warn!(
            skipped = unknown_enum_lines,
            "load_calibration_session: entries with unknown enum value (forward-compat skip)"
        );
    }
    if out_of_range_lines > 0 {
        tracing::warn!(
            skipped = out_of_range_lines,
            "load_calibration_session: entries with q1/q2 out of 1..=5 (corrupt/hand-edited NDJSON skip)"
        );
    }
    if !session_meta_seen {
        tracing::warn!(
            session = %session_path.display(),
            "load_calibration_session: no session_meta found — assuming track=main"
        );
    }

    // X/Y の源 = 記録済み feat (wall-clock)。既存コレクタを再利用する。
    let feats = collect_logged_feats(session_path)?;

    Ok(SessionData {
        track,
        probes,
        vignettes,
        feats,
        random_probe_assignment_count,
        session_start_ms,
        skipped_parse: parse_failed_lines,
        skipped_unknown_enum: unknown_enum_lines,
        skipped_out_of_range: out_of_range_lines,
    })
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
            ReplayEvent::Meta { .. }
            | ReplayEvent::Feat(_)
            | ReplayEvent::Paste { .. }
            | ReplayEvent::UserLabel { .. }
            | ReplayEvent::ReviewMarker { .. }
            | ReplayEvent::ImeShadow(_)
            | ReplayEvent::InterventionDecision(_)
            | ReplayEvent::SessionMeta { .. }
            | ReplayEvent::ProbeAssignment { .. }
            | ReplayEvent::RealtimeLabel { .. }
            | ReplayEvent::VignetteResponse { .. } => {
                // Paste は回数記録専用で features/HMM に未使用 → 追加処理なし。
                // Meta / Feat / UserLabel / ReviewMarker はゲート進行済み、追加処理不要
                // (UserLabel は metrics 経路で collect_user_labels 側で抽出)
                // (ReviewMarker は --segment 経路でセグメントハイライトに使用)
                // (v0.3 較正 variant は --calibration 経路の collect_calibration_session で抽出)
                // これらは timestamp()==None で ordered から除外されるが、match の網羅性のため列挙する。
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
                    is_paste: false, // replay は key 行から再構成。paste は別 variant で記録済み
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
// ── Segment 関連関数 (Phase 1 GT 改善) ────────────────────────────────

/// セグメント: 活動境界 (沈黙 ≥ SILENCE_BOUNDARY_SEC) で分割された区間。
struct Segment {
    start_ms: u64,
    end_ms: u64,
    feat_count: u32,
    silence_sec: f64,
    correction_rate: f64,
    avg_flight_time_ms: f64,
    has_marker: bool,
}

/// 沈黙がこの秒数以上続いたらセグメント境界とみなす。
const SILENCE_BOUNDARY_SEC: f64 = 5.0;

/// NDJSON から review_marker の timestamp 一覧を抽出する。
fn collect_review_markers(path: &PathBuf) -> Vec<u64> {
    // MAX_SESSION_BYTES ガード (collect_logged_feats と同じ NDJSON を読むため同一上限)
    if let Ok(meta) = std::fs::metadata(path) {
        if meta.len() > MAX_SESSION_BYTES {
            tracing::warn!("session file too large for review marker scan, skipping");
            return Vec::new();
        }
    }
    let file = match File::open(path) {
        Ok(f) => f,
        Err(_) => return Vec::new(),
    };
    let reader = BufReader::new(file);
    let mut markers = Vec::new();
    for line in reader.lines() {
        let line = match line {
            Ok(l) => l,
            Err(_) => continue,
        };
        if line.contains("\"review_marker\"") {
            if let Ok(ev) = serde_json::from_str::<ReplayEvent>(&line) {
                if let ReplayEvent::ReviewMarker { t } = ev {
                    markers.push(t);
                }
            }
        }
    }
    markers
}

/// NDJSON から key press イベントのタイムスタンプ一覧を抽出する。
/// セグメント境界検出に使用 (feat は 1Hz 固定なので沈黙検出に使えない)。
fn collect_key_timestamps(path: &PathBuf) -> Vec<u64> {
    // MAX_SESSION_BYTES ガード
    if let Ok(meta) = std::fs::metadata(path) {
        if meta.len() > MAX_SESSION_BYTES {
            tracing::warn!("session file too large for key timestamp scan, skipping");
            return Vec::new();
        }
    }
    let file = match File::open(path) {
        Ok(f) => f,
        Err(_) => return Vec::new(),
    };
    let reader = BufReader::new(file);
    let mut timestamps = Vec::new();
    for line in reader.lines() {
        let line = match line {
            Ok(l) => l,
            Err(_) => continue,
        };
        if line.contains("\"key\"") {
            if let Ok(ev) = serde_json::from_str::<ReplayEvent>(&line) {
                if let ReplayEvent::Key { t, press, .. } = ev {
                    if press {
                        timestamps.push(t);
                    }
                }
            }
        }
    }
    timestamps.sort_unstable();
    timestamps
}

/// キーストロークの沈黙 (≥ SILENCE_BOUNDARY_SEC) で区間を分割し、
/// 各区間に含まれる FeatSnapshot の統計をセグメントとして返す。
fn build_segments(feats: &[FeatSnapshot], key_timestamps: &[u64], markers: &[u64]) -> Vec<Segment> {
    if feats.is_empty() || key_timestamps.is_empty() {
        return Vec::new();
    }

    // キーストローク沈黙で区間境界を検出
    let boundary_ms = (SILENCE_BOUNDARY_SEC * 1000.0) as u64;
    let mut boundaries: Vec<(u64, u64)> = Vec::new(); // (start, end) of each active interval
    let mut seg_start = key_timestamps[0];

    for i in 1..key_timestamps.len() {
        let gap = key_timestamps[i].saturating_sub(key_timestamps[i - 1]);
        if gap >= boundary_ms {
            // 前セグメントを閉じる
            boundaries.push((seg_start, key_timestamps[i - 1]));
            seg_start = key_timestamps[i];
        }
    }
    // 最後のセグメント
    boundaries.push((seg_start, *key_timestamps.last().unwrap()));

    // 各区間に feat を割り当て
    let mut segments = Vec::new();
    for (start, end) in &boundaries {
        let seg_feats: Vec<&FeatSnapshot> = feats
            .iter()
            .filter(|f| f.timestamp >= *start && f.timestamp <= *end)
            .collect();
        segments.push(make_segment(*start, *end, &seg_feats, markers));
    }

    segments
}

fn make_segment(start_ms: u64, end_ms: u64, feats: &[&FeatSnapshot], markers: &[u64]) -> Segment {
    let feat_count = feats.len() as u32; // feat snapshots in range (1Hz → ≈ active seconds)
    let duration_sec = (end_ms.saturating_sub(start_ms)) as f64 / 1000.0;
    let silence_sec = duration_sec - feat_count as f64; // approx
    let silence_sec = if silence_sec < 0.0 { 0.0 } else { silence_sec };

    // Correction rate: average f3 across feats
    let correction_rate = if feats.is_empty() {
        0.0
    } else {
        feats.iter().map(|f| f.f3).sum::<f64>() / feats.len() as f64
    };

    // Average flight time
    let avg_flight_time_ms = if feats.is_empty() {
        0.0
    } else {
        feats.iter().map(|f| f.f1).sum::<f64>() / feats.len() as f64
    };

    let has_marker = markers.iter().any(|&m| m >= start_ms && m <= end_ms);

    Segment {
        start_ms,
        end_ms,
        feat_count,
        silence_sec,
        correction_rate,
        avg_flight_time_ms,
        has_marker,
    }
}

/// .segments.txt 形式の文字列を生成する。
fn format_segments_txt(session_path: &PathBuf, segments: &[Segment]) -> String {
    let mut out = String::new();
    let session_name = session_path
        .file_name()
        .map(|n| n.to_string_lossy().to_string())
        .unwrap_or_else(|| "unknown".to_string());

    let total_keys: u32 = segments.iter().map(|s| s.feat_count).sum();

    out.push_str(&format!("# Session: {}\n", session_name));
    out.push_str(&format!(
        "# Segments: {}  |  Total feat snapshots: {}\n",
        segments.len(),
        total_keys,
    ));
    out.push_str("#\n");
    out.push_str("# Label: F=Flow  I=Incubation  S=Stuck  ?=Unknown  -=Skip\n");
    out.push_str("# Edit the Label column, then save.\n");
    out.push_str("# Timestamps are absolute epoch ms (used by --segments parser).\n");
    out.push_str("#\n");
    out.push_str(
        "# Seg  Start_ms         End_ms           Feats  Silence  CorrRate  AvgFT    Label\n",
    );

    for (i, seg) in segments.iter().enumerate() {
        let marker = if seg.has_marker { "*" } else { " " };
        out.push_str(&format!(
            "{}{:>3}  {:>16}  {:>16}  {:>5}  {:>6.1}s  {:>7.1}%  {:>5.0}ms   ?\n",
            marker,
            i + 1,
            seg.start_ms,
            seg.end_ms,
            seg.feat_count,
            seg.silence_sec,
            seg.correction_rate * 100.0,
            seg.avg_flight_time_ms,
        ));
    }

    out
}

/// .segments.txt をパースし RangeLabel 列を返す。
fn parse_segments_file(path: &PathBuf) -> Result<Vec<RangeLabel>, String> {
    // サイズガード: segments ファイルは通常数 KB、10 MB を上限とする
    const MAX_SEGMENTS_BYTES: u64 = 10 * 1024 * 1024;
    let meta =
        std::fs::metadata(path).map_err(|e| format!("cannot stat {}: {}", path.display(), e))?;
    if meta.len() > MAX_SEGMENTS_BYTES {
        return Err(format!(
            "{} is {} bytes, exceeds limit {} bytes",
            path.display(),
            meta.len(),
            MAX_SEGMENTS_BYTES,
        ));
    }

    let content = std::fs::read_to_string(path)
        .map_err(|e| format!("cannot read {}: {}", path.display(), e))?;

    let mut labels = Vec::new();

    for line in content.lines() {
        let trimmed = line.trim();
        // コメント行・空行をスキップ
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }

        // マーカー `*` をスキップ
        let trimmed = trimmed.trim_start_matches('*').trim();

        // フィールド分割: Seg Start_ms End_ms Feats Silence CorrRate AvgFT Label
        let fields: Vec<&str> = trimmed.split_whitespace().collect();
        if fields.len() < 8 {
            continue; // ヘッダー行やフィールド不足行をスキップ
        }

        let label_str = fields[7];
        let label = match label_str {
            "F" => LabelClass::Flow,
            "I" => LabelClass::Incubation,
            "S" => LabelClass::Stuck,
            "?" | "-" => continue, // Unknown/Skip
            _ => continue,
        };

        // start_ms / end_ms のパース — 非数値行 (ヘッダー等) は continue でスキップ
        let start_ms: u64 = match fields[1].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };
        let end_ms: u64 = match fields[2].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };

        if start_ms > end_ms {
            tracing::warn!(
                "segment has start_ms ({}) > end_ms ({}), skipping",
                start_ms,
                end_ms
            );
            continue;
        }

        labels.push(RangeLabel {
            start_ms,
            end_ms,
            label,
        });
    }

    Ok(labels)
}

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
        let feat: FeatSnapshot = dto.try_into().expect("valid dto converts to FeatSnapshot");
        assert_eq!(feat.timestamp, 1_700_000_001_000);
        assert!((feat.f1 - 140.0).abs() < 1e-9);
        assert!((feat.p_flow - 0.85).abs() < 1e-9);
        assert!((feat.p_inc - 0.10).abs() < 1e-9);
        assert!((feat.p_stuck - 0.05).abs() < 1e-9);
        assert_eq!(feat.obs, 3);
        assert!((feat.alpha - 0.3).abs() < 1e-9);
    }

    /// ペーストイベント行 (`{"type":"paste","t":...}`) が deserialize でき、
    /// `timestamp()==None` で snapshot 再実行の時刻順ソートから除外されることを確認する。
    /// 本 variant が無いと paste 行を含む NDJSON で gse-replay が parse エラーになる。
    #[test]
    fn paste_event_parses_and_is_skipped_from_replay() {
        let line = r#"{"type":"paste","t":1700000005000}"#;
        let ev: ReplayEvent = serde_json::from_str(line).expect("parse ReplayEvent::Paste");
        assert!(
            matches!(
                ev,
                ReplayEvent::Paste {
                    t: 1_700_000_005_000
                }
            ),
            "expected ReplayEvent::Paste, got {ev:?}"
        );
        assert_eq!(
            ev.timestamp(),
            None,
            "paste は再実行に使わないため timestamp()==None で除外する"
        );
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
        let feat: FeatSnapshot = dto.try_into().expect("valid schema_dto converts");
        assert_eq!(feat.timestamp, 1_700_000_042_000);
        assert!((feat.f1 - 120.5).abs() < 1e-9);
        assert!((feat.p_flow - 0.6).abs() < 1e-9);
        assert_eq!(feat.obs, 11);
        assert!((feat.alpha - 0.2).abs() < 1e-9);
    }

    // =========================================================================
    // M3: TryFrom validation tests (security-checker MEDIUM)
    // =========================================================================

    /// Helper: 合法な LoggedFeatDto を返す。各テストで異常値だけ差し替える。
    fn valid_dto() -> LoggedFeatDto {
        LoggedFeatDto {
            timestamp: 1_700_000_000_000,
            f1: 140.0,
            f3: 0.0,
            f4: 4.0,
            f5: 0.0,
            f6: 0.0,
            p_flow: 0.85,
            p_inc: 0.10,
            p_stuck: 0.05,
            raw_x: 0.0,
            raw_y: 0.6,
            ewma_x: 0.07,
            ewma_y: 0.74,
            obs: 3,
            alpha: 0.3,
        }
    }

    /// M3: NaN が確率フィールドに入った場合は Err で reject。
    /// `argmax_class` が NaN で silent に Stuck を選ぶ問題を入力側で止める。
    #[test]
    fn nan_probability_rejected() {
        let mut dto = valid_dto();
        dto.p_flow = f64::NAN;
        let err = FeatSnapshot::try_from(dto).expect_err("NaN must be rejected");
        assert!(
            err.contains("p_flow") && err.contains("not finite"),
            "error should mention field + not finite: {}",
            err
        );
    }

    /// M3: Inf が特徴量に入った場合は Err で reject。
    #[test]
    fn inf_feature_rejected() {
        let mut dto = valid_dto();
        dto.f4 = f64::INFINITY;
        let err = FeatSnapshot::try_from(dto).expect_err("Inf must be rejected");
        assert!(
            err.contains("f4") && err.contains("not finite"),
            "error should mention f4 + not finite: {}",
            err
        );
    }

    /// M3: 確率和が許容範囲 [0.98, 1.02] を外れた場合は Err。
    /// 4 桁丸め誤差 (logger の {:.4}) は許容、本質的な壊れ値のみ reject。
    #[test]
    fn prob_sum_out_of_range_rejected() {
        let mut dto = valid_dto();
        // 和が 1.5 になる壊れ値 (明確に範囲外)
        dto.p_flow = 0.5;
        dto.p_inc = 0.5;
        dto.p_stuck = 0.5;
        let err = FeatSnapshot::try_from(dto).expect_err("sum=1.5 must be rejected");
        assert!(
            err.contains("probability sum") && err.contains("1.5"),
            "error should mention probability sum: {}",
            err
        );
    }

    /// M3: alpha が `[0, 1]` を外れた場合は Err。
    #[test]
    fn alpha_out_of_range_rejected() {
        let mut dto = valid_dto();
        dto.alpha = 1.5;
        let err = FeatSnapshot::try_from(dto).expect_err("alpha=1.5 must be rejected");
        assert!(
            err.contains("alpha") && err.contains("1.5"),
            "error should mention alpha out of range: {}",
            err
        );
    }

    /// M3: 丸め誤差レベル (sum=0.99 等) は許容される (回帰保護)。
    #[test]
    fn rounding_error_tolerated() {
        let mut dto = valid_dto();
        // logger の {:.4} で端数が 0.9999 や 1.0001 になるケースを許容
        dto.p_flow = 0.8499;
        dto.p_inc = 0.1000;
        dto.p_stuck = 0.0500;
        // sum = 0.9999 → [0.98, 1.02] 内、通るべき
        let feat = FeatSnapshot::try_from(dto).expect("rounding-level sum must be tolerated");
        assert!((feat.p_flow - 0.8499).abs() < 1e-9);
    }

    // =========================================================================
    // Task D: --calibration 抽出経路の統合テスト (合成 NDJSON fixture)
    // =========================================================================

    /// `load_calibration_session` が新 4 type を正しく抽出することを確認する。
    #[test]
    fn load_calibration_session_extracts_new_variants() {
        let s3 = load_calibration_session(&fixture_path("calib_subject_s3_eval.ndjson"))
            .expect("load s3");
        assert_eq!(s3.track, TrackKind::Main);
        assert_eq!(s3.probes.len(), 3, "s3 has 3 realtime_label probes");
        assert_eq!(
            s3.random_probe_assignment_count, 3,
            "s3 has 3 probe_assignment audit records"
        );
        assert!(s3.vignettes.is_empty(), "s3 has no vignettes");
        assert_eq!(s3.feats.len(), 6, "s3 has 6 feat lines");
        // 全 probe が random_probe・回答済み。
        assert!(s3
            .probes
            .iter()
            .all(|p| p.source == ProbeSourceKind::RandomProbe && p.answered));

        let s1 =
            load_calibration_session(&fixture_path("calib_subject_s1.ndjson")).expect("load s1");
        assert_eq!(s1.vignettes.len(), 8, "s1 carries the 8 vignettes");
        assert_eq!(s1.probes.len(), 1);
    }

    /// 3 セッション (s1/s2 = 較正・s3 = 評価) を `--calibration` 相当で通し、
    /// 抽出 → 窓集約 → 被験者内 C-index → holdout → ビネット採点を end-to-end 検証する。
    /// s3 は X(ewma) を q1 に単調対応させてあり C-index = 1.0 になる (決定論)。
    #[test]
    fn calibration_pipeline_end_to_end_strong_concordance() {
        let sessions = vec![
            load_calibration_session(&fixture_path("calib_subject_s1.ndjson")).unwrap(),
            load_calibration_session(&fixture_path("calib_subject_s2.ndjson")).unwrap(),
            load_calibration_session(&fixture_path("calib_subject_s3_eval.ndjson")).unwrap(),
        ];
        let report = compute_calibration_metrics(&sessions, AggSpec::default());

        // holdout: 先頭 2 (s1/s2) = 較正、s3 = 評価。
        assert_eq!(report.main_session_count, 3);
        assert_eq!(report.calibration_session_count, 2);
        assert_eq!(report.evaluation_session_count, 1);

        // 評価セッション s3 の X↔Q1: ewma_x=(0.1,0.5,0.9) ↔ q1=(1,3,5) → 完全一致。
        assert_eq!(report.cindex.x_q1_pooled, Some(1.0));
        // Y↔Q2: ewma_y=(0.9,0.5,0.1) ↔ q2=(5,3,1) → 完全一致。
        assert_eq!(report.cindex.y_q2_pooled, Some(1.0));

        // 測定法: 全 5 random probe (s1:1 + s2:1 + s3:3) が回答済み。
        assert_eq!(report.measurement.random_probe_total, 5);
        assert_eq!(report.measurement.random_probe_answered, 5);
        assert!((report.measurement.answer_rate - 1.0).abs() < 1e-9);

        // ビネット (s1 の 8 問) はすべて想定象限。
        assert_eq!(report.vignette.total, 8);
        assert_eq!(report.vignette.matched, 8);
        assert!(report.vignette.passed);

        // 無回答なし → MNAR 上下限は点推定と一致。
        assert_eq!(report.mnar.point, Some(1.0));
        assert_eq!(report.mnar.lower, Some(1.0));
        assert_eq!(report.mnar.upper, Some(1.0));

        // Recall は withheld。
        assert!(!report.recall.reported);

        // JSON シリアライズが通る (metrics.json 出力経路)。
        let json = serde_json::to_string(&report).expect("serialize CalibrationReport");
        assert!(json.contains("\"schema\":\"calibration/v0.3\""));
    }

    /// exploratory セッションは主指標から除外される (§1.3)。
    #[test]
    fn calibration_excludes_exploratory_track() {
        // s3 を exploratory 扱いにするため、track を書き換えた SessionData を直接合成する。
        let mut s3 =
            load_calibration_session(&fixture_path("calib_subject_s3_eval.ndjson")).unwrap();
        s3.track = TrackKind::Exploratory;
        let sessions = vec![
            load_calibration_session(&fixture_path("calib_subject_s1.ndjson")).unwrap(),
            load_calibration_session(&fixture_path("calib_subject_s2.ndjson")).unwrap(),
            s3,
        ];
        let report = compute_calibration_metrics(&sessions, AggSpec::default());
        assert_eq!(report.exploratory_session_count, 1);
        assert_eq!(report.main_session_count, 2);
        // main は s1/s2 のみ → 両方較正に取られ評価集合は空。
        assert_eq!(report.evaluation_session_count, 0);
        assert_eq!(report.cindex.x_q1_pooled, None);
    }
}
