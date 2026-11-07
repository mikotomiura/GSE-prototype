//! 段 1 の再生（`gse-replay --probes`・`--day-questions`）の純粋な部分。
//!
//! 記録の行から段 1 の調停器 [`Arbiter`] を回し直し、記録の `probe_assignment`・`probe_suppressed`・
//! 差し替えのラベル・`day_question` の行と照合する（M5 の 3 本目・`.steering/20261107-gse-m5-s1-replay-gate/`
//! の design.md と判断 2〜4）。
//!
//! ## 方針
//!
//! - 回すのは調停器だけ。開いているカード（`TickInput.open_card`）は再生の発火から作らず、**記録から作って渡す**。
//!   カードを閉じるのは本人の操作で、その情報は記録にしかない。記録から渡すと、1 件の食い違いが後ろへ波及しない。
//! - 記録に tick の時刻が無いので、照合の鍵は tick の位相に依らない値（候補の時刻・層化の引き金の押下の時刻）にする。
//!   位相を [`TICK_PHASES_MS`] の 4 通りで回し、結果が割れた項目を `boundary_tick` に分ける。
//! - 記録に無いもの（時差・前日までの日の状態・スリープからの復帰・起動とローテートの別・同意の取り消し）は、
//!   照合できない項目を `unverified` に分ける。分かったふりをしない。
//!
//! ⚠️ OS API・ファイル IO を持たない（行の文字列を受け取る）。打鍵の本文は読まない（`key` 行は時刻と押下かだけ）。

use std::collections::{BTreeMap, HashMap, HashSet};

use serde::Serialize;
use serde_json::Value;

use crate::analysis::probe_arbiter::{
    Action, Arbiter, ArbiterConfig, DayClosedBy, DayQuestion, DayState, DayTrigger, OpenCard,
    Stratum, SuppressReason, TickInput, ARBITER_VERSION,
};
use crate::analysis::probe_scheduler::ProbeConfig;
use crate::s1_driver::{local_clock, GAP_AS_POWER_RESUME_MS, S1_TICK_LAG_MS};

/// 本モジュールの誤り（★ この repo は `anyhow` を依存に持たない・`redaction.rs` と同じ）。
pub type Result<T> = std::result::Result<T, String>;

/// 再生の版（出力の JSON に書く）。照合の規則を変えたら上げる。
pub const REPLAY_VERSION: &str = "s1-replay-1";

/// tick の位相（壁時計の 1 秒の中のずれ）。4 通りで回し、割れたものを境目に分ける。
pub const TICK_PHASES_MS: [u64; 4] = [0, 250, 500, 750];

/// 判断 2: 一時停止の行の時刻の前のこの幅にかかる不一致は `boundary_pause`。
pub const PAUSE_BOUNDARY_MS: u64 = 2_000;
/// tick が最大 1 秒遅れるので、実際に割れうるのは約 3 秒。判断 2 の窓の外の 1 秒を別に数える。
pub const NEAR_PAUSE_MS: u64 = 3_000;
/// 枠が動き出してからこの幅にかかる不一致は `boundary_activation`。
pub const ACTIVATION_BOUNDARY_MS: u64 = 3_000;
/// 日の問いの `shown_ts` と再生の tick の壁時計の差の許容（tick の位相の 1 秒）。
pub const DAY_SHOWN_TOLERANCE_MS: u64 = 1_000;
/// 前のファイルの終わりから次のファイルの始まりまでがこれより短ければローテート（同じ走行）とみなす。
pub const ROTATION_GAP_MS: u64 = 1_000;
/// 走行の始まりからこの幅の拾い直しの不一致は `unverified.app_start`（起動とローテートの別が推定のため）。
pub const APP_START_WINDOW_MS: u64 = 10_000;
/// ファイルの始まりより前に出てよい時刻の幅（書き込みの順の揺れ）。
pub const MAX_BEFORE_START_MS: u64 = 60_000;
/// 入力の全体の時間の幅の上限。
pub const MAX_TOTAL_SPAN_MS: u64 = 40 * 86_400_000;

// ---------------------------------------------------------------------------
// 行
// ---------------------------------------------------------------------------

/// 再生に使う行（それ以外の行種は読み飛ばす）。
#[derive(Debug, Clone)]
pub enum Row {
    MetaStart { t: u64 },
    MetaEnd { t: u64 },
    Key { t: u64 },
    Focus { t: u64 },
    Pause { t: u64, paused: bool },
    Frame(FrameRow),
    Assigned(AssignedRow),
    Suppressed(SuppressedRow),
    Label(LabelRow),
    Day(DayRow),
}

#[derive(Debug, Clone)]
pub struct FrameRow {
    pub t: u64,
    pub frame_seed: u64,
    pub anchor_ms: u64,
    pub config: ArbiterConfig,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AssignedRow {
    pub probe_id: String,
    pub scheduled_ts: u64,
    pub stratum: Stratum,
    pub debug: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct SuppressedRow {
    pub t: u64,
    pub candidate_ts: u64,
    pub stratum: Stratum,
    pub reason: SuppressReason,
}

/// `realtime_label`（段 1 のカードのラベル。`activity_label` は同じ時刻に対で出るので読まない）。
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LabelRow {
    pub t: u64,
    pub probe_id: String,
    pub answered: bool,
    pub skip_reason: String,
    pub debug: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct DayRow {
    pub t: u64,
    pub shown_ts: u64,
    pub target_day: i64,
    pub trigger: DayTrigger,
    pub delayed: bool,
    pub answered: bool,
    pub closed_by: DayClosedBy,
    pub debug: bool,
}

/// 1 本の記録のファイル。
#[derive(Debug, Clone)]
pub struct InputFile {
    pub name: String,
    pub rows: Vec<Row>,
    /// JSON として読めず飛ばした行の数（落ちた走行の書きかけの最後の行など・`--invitation` と同じ扱い）。
    pub skipped_lines: usize,
}

impl InputFile {
    pub fn session_start(&self) -> Option<u64> {
        self.rows.iter().find_map(|r| match r {
            Row::MetaStart { t } => Some(*t),
            _ => None,
        })
    }

    pub fn session_end(&self) -> Option<u64> {
        self.rows.iter().rev().find_map(|r| match r {
            Row::MetaEnd { t } => Some(*t),
            _ => None,
        })
    }

    /// 最後の時刻（`meta` の終わり、無ければ最後の時刻つきの行）。
    pub fn last_ms(&self) -> Option<u64> {
        self.session_end()
            .or_else(|| self.rows.iter().rev().find_map(row_time))
    }
}

fn row_time(r: &Row) -> Option<u64> {
    match r {
        Row::MetaStart { t } | Row::MetaEnd { t } | Row::Key { t } | Row::Focus { t } => Some(*t),
        Row::Pause { t, .. } => Some(*t),
        // ★ 枠の行の `t` は起点（同意の時刻を残さない・2 本目の判断 1）なので、置かれた位置の時刻にしない
        Row::Frame(_) | Row::Assigned(_) => None,
        Row::Suppressed(s) => Some(s.t),
        Row::Label(l) => Some(l.t),
        Row::Day(d) => Some(d.t),
    }
}

/// 行の時刻の欄すべて（入力の検査用・`row_time` に入らない欄も含む）。
fn all_times(r: &Row) -> Vec<u64> {
    match r {
        Row::Frame(f) => vec![f.t, f.anchor_ms],
        Row::Assigned(a) => vec![a.scheduled_ts],
        Row::Suppressed(x) => vec![x.t, x.candidate_ts],
        Row::Day(d) => vec![d.t, d.shown_ts],
        r => row_time(r).into_iter().collect(),
    }
}

fn stratum_parse(s: &str) -> Option<Stratum> {
    Some(match s {
        "random" => Stratum::Random,
        "low_operation_end" => Stratum::LowOperationEnd,
        "resumption" => Stratum::Resumption,
        _ => return None,
    })
}

/// 層の名（`probe_assignment.stratum` と同じ文字列）。
pub fn stratum_str(s: Stratum) -> &'static str {
    match s {
        Stratum::Random => "random",
        Stratum::LowOperationEnd => "low_operation_end",
        Stratum::Resumption => "resumption",
    }
}

fn u64_of(v: &Value, k: &str) -> Result<u64> {
    v.get(k)
        .and_then(Value::as_u64)
        .ok_or_else(|| format!("`{k}` が整数でない"))
}

fn bool_of(v: &Value, k: &str) -> Result<bool> {
    v.get(k)
        .and_then(Value::as_bool)
        .ok_or_else(|| format!("`{k}` が真偽でない"))
}

fn str_of<'a>(v: &'a Value, k: &str) -> Result<&'a str> {
    v.get(k)
        .and_then(Value::as_str)
        .ok_or_else(|| format!("`{k}` が文字列でない"))
}

fn debug_of(v: &Value) -> bool {
    v.get("debug").and_then(Value::as_bool).unwrap_or(false)
}

/// `probe_frame` の行から設定を戻す（`logger::format_probe_frame_line` の逆）。
fn frame_of(v: &Value) -> Result<FrameRow> {
    let version = str_of(v, "arbiter_version")?;
    if version != ARBITER_VERSION {
        return Err(format!(
            "arbiter_version が違う（記録 {version}・再生 {ARBITER_VERSION}）"
        ));
    }
    let lambda = v
        .get("lambda_per_ms")
        .and_then(Value::as_f64)
        .ok_or_else(|| "`lambda_per_ms` が数でない".to_string())?;
    let no_ask_fraction = v
        .get("no_ask_fraction")
        .and_then(Value::as_f64)
        .ok_or_else(|| "`no_ask_fraction` が数でない".to_string())?;
    let u32_of = |k: &str| -> Result<u32> {
        u32::try_from(u64_of(v, k)?).map_err(|_| format!("`{k}` が範囲の外"))
    };
    let usize_of = |k: &str| -> Result<usize> {
        usize::try_from(u64_of(v, k)?).map_err(|_| format!("`{k}` が範囲の外"))
    };
    let config = ArbiterConfig {
        random: ProbeConfig {
            lambda_per_ms: lambda,
            gap_min_ms: u64_of(v, "gap_min_ms")?,
            cap_window_ms: u64_of(v, "cap_window_ms")?,
            cap_count: usize_of("cap_count")?,
            max_gap_ms: u64_of(v, "max_gap_ms")?,
            away_idle_ms: u64_of(v, "away_idle_ms")?,
            min_session_elapsed_ms: u64_of(v, "warmup_ms")?,
        },
        strata_enabled: bool_of(v, "strata_enabled")?,
        strat_low_op_min_gap_ms: u64_of(v, "strat_low_op_min_gap_ms")?,
        strat_resume_min_gap_ms: u64_of(v, "strat_resume_min_gap_ms")?,
        strat_guard_after_any_ms: u64_of(v, "strat_guard_after_any_ms")?,
        strat_cap_count: usize_of("strat_cap_count")?,
        strat_cap_window_ms: u64_of(v, "strat_cap_window_ms")?,
        strat_yield_before_random_ms: u64_of(v, "strat_yield_before_random_ms")?,
        no_ask_enabled: bool_of(v, "no_ask_enabled")?,
        no_ask_block_ms: u64_of(v, "no_ask_block_ms")?,
        no_ask_fraction,
        eod_window_start_min: u32_of("eod_window_start_min")?,
        eod_window_end_min: u32_of("eod_window_end_min")?,
        eod_idle_ms: u64_of(v, "eod_idle_ms")?,
        eod_yield_before_random_ms: u64_of(v, "eod_yield_before_random_ms")?,
    };
    Ok(FrameRow {
        t: u64_of(v, "t")?,
        frame_seed: u64_of(v, "frame_seed")?,
        anchor_ms: u64_of(v, "anchor_ms")?,
        config,
    })
}

/// 1 行を読む。再生に使わない行種は `None`。壊れた行は `Err`（fail-closed）。
pub fn parse_line(line: &str) -> Result<Option<Row>> {
    let line = line.trim();
    if line.is_empty() {
        return Ok(None);
    }
    let Ok(v) = serde_json::from_str::<Value>(line) else {
        return Err(UNREADABLE.to_string());
    };
    let ty = v.get("type").and_then(Value::as_str).unwrap_or_default();
    Ok(Some(match ty {
        "meta" => {
            if let Some(t) = v.get("session_start").and_then(Value::as_u64) {
                Row::MetaStart { t }
            } else if let Some(t) = v.get("session_end").and_then(Value::as_u64) {
                Row::MetaEnd { t }
            } else {
                return Ok(None);
            }
        }
        "key" => {
            if !bool_of(&v, "press")? {
                return Ok(None);
            }
            Row::Key {
                t: u64_of(&v, "t")?,
            }
        }
        "focus_transition" => Row::Focus {
            t: u64_of(&v, "t")?,
        },
        "recording_pause" => Row::Pause {
            t: u64_of(&v, "t")?,
            paused: bool_of(&v, "paused")?,
        },
        "probe_frame" => Row::Frame(frame_of(&v)?),
        "probe_assignment" => {
            // ★ 段 1 より前の記録の `probe_assignment` は層を持たない（古いビルド）。再生の対象にしない
            let Some(stratum) = v
                .get("stratum")
                .and_then(Value::as_str)
                .and_then(stratum_parse)
            else {
                return Ok(None);
            };
            Row::Assigned(AssignedRow {
                probe_id: str_of(&v, "probe_id")?.to_string(),
                scheduled_ts: u64_of(&v, "scheduled_ts")?,
                stratum,
                debug: debug_of(&v),
            })
        }
        "probe_suppressed" => Row::Suppressed(SuppressedRow {
            t: u64_of(&v, "t")?,
            candidate_ts: u64_of(&v, "candidate_ts")?,
            stratum: stratum_parse(str_of(&v, "stratum")?)
                .ok_or_else(|| "知らない stratum".to_string())?,
            reason: SuppressReason::parse(str_of(&v, "reason")?)
                .ok_or_else(|| "知らない reason".to_string())?,
        }),
        "realtime_label" => {
            // ★ 自発の記録（`probe_id` が null）は段 1 のカードではない
            let Some(probe_id) = v.get("probe_id").and_then(Value::as_str) else {
                return Ok(None);
            };
            Row::Label(LabelRow {
                t: u64_of(&v, "ts")?,
                probe_id: probe_id.to_string(),
                answered: bool_of(&v, "answered")?,
                skip_reason: {
                    // ★ 既知の値だけ（出力の集計のキーになるので、検証していない文字列を通さない）
                    let r = str_of(&v, "skip_reason")?;
                    if !SKIP_REASONS.contains(&r) {
                        return Err(format!("知らない skip_reason: {r}"));
                    }
                    r.to_string()
                },
                debug: debug_of(&v),
            })
        }
        "day_question" => Row::Day(DayRow {
            t: u64_of(&v, "t")?,
            shown_ts: u64_of(&v, "shown_ts")?,
            target_day: v
                .get("target_day")
                .and_then(Value::as_i64)
                .ok_or_else(|| "`target_day` が整数でない".to_string())?,
            trigger: DayTrigger::parse(str_of(&v, "trigger")?)
                .ok_or_else(|| "知らない trigger".to_string())?,
            delayed: bool_of(&v, "delayed")?,
            answered: bool_of(&v, "answered")?,
            closed_by: DayClosedBy::parse(str_of(&v, "closed_by")?)
                .ok_or_else(|| "知らない closed_by".to_string())?,
            debug: debug_of(&v),
        }),
        _ => return Ok(None),
    }))
}

/// `realtime_label.skip_reason` の既知の値（`logger::SkipReason`）。
const SKIP_REASONS: [&str; 4] = ["none", "dont_remember", "dismissed", "superseded"];

/// JSON として読めない行の誤りの文（`parse_file` が数えて飛ばす）。
const UNREADABLE: &str = "JSON として読めない";

/// 1 本の記録の全体を読む。JSON として読めない行は数えて飛ばし、再生に使う行種の欄が壊れていれば
/// 行番号つきの誤りで止める（fail-closed）。
pub fn parse_file(name: &str, text: &str) -> Result<InputFile> {
    let mut rows = Vec::new();
    let mut skipped_lines = 0;
    for (i, line) in text.lines().enumerate() {
        match parse_line(line) {
            Ok(Some(r)) => rows.push(r),
            Ok(None) => {}
            Err(e) if e == UNREADABLE => skipped_lines += 1,
            Err(e) => return Err(format!("{name}:{}: {e}", i + 1)),
        }
    }
    Ok(InputFile {
        name: name.to_string(),
        rows,
        skipped_lines,
    })
}

/// ファイルを `meta.session_start` の順に並べる。始まりが無い・重なる記録は拒む。
pub fn order_inputs(mut files: Vec<InputFile>) -> Result<Vec<InputFile>> {
    for f in &files {
        if f.session_start().is_none() {
            return Err(format!("{}: meta.session_start が無い", f.name));
        }
    }
    // ★ 壊れた時刻（ビット化けなど）で再生の tick が止まらなくならないように、時刻の欄を全部縛る。
    //   ファイルの幅では縛らない（一時停止の間はローテートが回らないので、正しい記録でも 1 本が何日にもなる・
    //   /cross-review の security-checker MEDIUM）。上の端は入力の全体の幅（下の 40 日）で縛る。
    for f in &files {
        let start = f.session_start().unwrap_or(0);
        for t in f.rows.iter().flat_map(all_times) {
            if t.saturating_add(MAX_BEFORE_START_MS) < start
                || t > start.saturating_add(MAX_TOTAL_SPAN_MS)
            {
                return Err(format!(
                    "{}: 行の時刻 {t} が meta.session_start {start} から外れている",
                    f.name
                ));
            }
        }
    }
    files.sort_by_key(|f| f.session_start().unwrap_or(0));
    if let (Some(a), Some(b)) = (files.first(), files.last()) {
        let end = files
            .iter()
            .flat_map(|f| f.rows.iter().flat_map(all_times))
            .max()
            .unwrap_or(0)
            .max(b.last_ms().unwrap_or(0));
        let span = end.saturating_sub(a.session_start().unwrap_or(0));
        if span > MAX_TOTAL_SPAN_MS {
            return Err(format!("入力の時間の幅が長すぎる（{span} ms）"));
        }
    }
    for w in files.windows(2) {
        let (a, b) = (&w[0], &w[1]);
        let a_end = a.last_ms().unwrap_or(0);
        if b.session_start().unwrap_or(0) < a_end {
            return Err(format!("{} と {} の時間が重なる", a.name, b.name));
        }
    }
    Ok(files)
}

// ---------------------------------------------------------------------------
// 記録から作る時間の列
// ---------------------------------------------------------------------------

/// 開いていたカードの区間（記録から）。`from` は「この時刻より後の tick から開いている」。
#[derive(Debug, Clone)]
struct CardSpan {
    from: u64,
    to: u64,
    card: OpenCard,
    /// プローブなら `probe_id`（再生の発火と結んで `from` を直す）。
    probe: Option<(Stratum, u64)>,
    /// 確かめ用のカード（調停器の外で出す。再生は差し替えを出さない）。
    debug: bool,
}

/// 枠の動き出し。
#[derive(Debug, Clone)]
pub struct FrameSpan {
    pub file: String,
    pub frame: FrameRow,
    pub activation_lo: u64,
    pub activation_hi: u64,
    pub end_ms: u64,
    /// この枠で走行が始まった（ローテートでない）と推定したか。
    pub app_start: bool,
}

/// 記録の全体から作る、再生の入力と照合の相手。
#[derive(Debug, Clone, Default)]
struct Timeline {
    presses: Vec<u64>,
    focus: Vec<u64>,
    pauses: Vec<(u64, bool)>,
    frames: Vec<FrameSpan>,
    spans: Vec<CardSpan>,
    quits: Vec<u64>,
    /// 記録の日の問いの閉じ（`day_end` 以外）: (時刻, 対象の日, 答えたか, 確かめ用か)。
    day_closes: Vec<(u64, i64, bool, bool)>,
    power_resumes: Vec<u64>,
    assigned: Vec<AssignedRow>,
    suppressed: Vec<SuppressedRow>,
    labels: Vec<LabelRow>,
    days: Vec<DayRow>,
    /// 記録の段 1 の判定の行（割り当て・抑制）の位置の時刻（枠ごとの `tail` の判定に使う）。
    decision_times: Vec<u64>,
    /// 時刻つきの行が 30 秒以上途切れた後の最初の行の時刻（見えないスリープの候補・`warmup` の未照合に使う）。
    gap_ends: Vec<u64>,
    first_ms: u64,
    last_ms: u64,
}

/// 行の並びの中で、時刻を持たない行の位置の時刻（直前の時刻つきの行）を求める。
fn positions(rows: &[Row], start: u64) -> Vec<u64> {
    let mut cur = start;
    rows.iter()
        .map(|r| {
            if let Some(t) = row_time(r) {
                cur = cur.max(t);
            }
            cur
        })
        .collect()
}

fn build_timeline(files: &[InputFile]) -> Timeline {
    let mut tl = Timeline::default();
    let mut prev_end: Option<u64> = None;
    let mut open_probes: Vec<(String, u64, Stratum, u64, bool)> = Vec::new();
    for (fi, f) in files.iter().enumerate() {
        let start = f.session_start().unwrap_or(0);
        let end = f.last_ms().unwrap_or(start);
        if fi == 0 {
            tl.first_ms = start;
        }
        tl.last_ms = tl.last_ms.max(end);
        let app_start = match prev_end {
            None => true,
            Some(pe) => start.saturating_sub(pe) >= ROTATION_GAP_MS,
        };
        prev_end = Some(end);
        let pos = positions(&f.rows, start);
        let mut first_frame_in_file = true;
        for (i, r) in f.rows.iter().enumerate() {
            let at = pos[i];
            match r {
                Row::Key { t } => tl.presses.push(*t),
                Row::Focus { t } => tl.focus.push(*t),
                Row::Pause { t, paused } => {
                    tl.pauses.push((*t, *paused));
                    if *paused {
                        // ★ 一時停止で下ろしたカード（ラベルの行なし）はここで閉じる
                        for (_, from, st, sched, dbg) in open_probes.drain(..) {
                            tl.spans.push(probe_span(from, *t, st, sched, dbg));
                        }
                    }
                }
                Row::Frame(fr) => {
                    // 動き出しは、前の時刻つきの行と次の時刻つきの行の間
                    let lo = at.max(fr.anchor_ms);
                    let hi = f.rows[i + 1..]
                        .iter()
                        .find_map(row_time)
                        .unwrap_or(lo)
                        .max(lo);
                    // ★ 直後に溜まった候補の抑制の行があれば、その `t` が最初の tick の壁時計そのもの
                    let exact = f.rows[i + 1..].iter().find_map(|r| match r {
                        // ★ ふつうの抑制の行でも t − 候補 は 2〜3 秒（調停器の時計が 2 秒遅れ・tick は最大 1 秒遅れる）。
                        //   それを超えるものだけを溜まった候補と読む（/cross-review の code-reviewer MEDIUM）
                        Row::Suppressed(s)
                            if s.t > s.candidate_ts.saturating_add(S1_TICK_LAG_MS + 1_000) =>
                        {
                            Some(s.t)
                        }
                        _ => None,
                    });
                    let lo = exact.filter(|&t| t <= hi).unwrap_or(lo);
                    if let Some(prev) = tl.frames.last_mut() {
                        // ★ ローテートでは駆動役は調停器を持ち続ける（次の枠を作るまで前の枠で回す）。
                        //   走行が変わったときだけ、前の枠はファイルの終わりで止まる
                        if prev.end_ms > lo || (!app_start && first_frame_in_file) {
                            prev.end_ms = lo;
                        }
                    }
                    tl.frames.push(FrameSpan {
                        file: f.name.clone(),
                        frame: fr.clone(),
                        activation_lo: lo,
                        activation_hi: hi,
                        end_ms: end,
                        app_start: app_start && first_frame_in_file,
                    });
                    first_frame_in_file = false;
                }
                Row::Assigned(a) => {
                    open_probes.push((a.probe_id.clone(), at, a.stratum, a.scheduled_ts, a.debug));
                    tl.assigned.push(a.clone());
                    tl.decision_times.push(at);
                }
                Row::Suppressed(s) => {
                    tl.suppressed.push(*s);
                    tl.decision_times.push(s.t);
                }
                Row::Label(l) => {
                    if let Some(k) = open_probes.iter().position(|p| p.0 == l.probe_id) {
                        let (_, from, st, sched, dbg) = open_probes.remove(k);
                        tl.spans.push(probe_span(from, l.t, st, sched, dbg));
                    }
                    tl.labels.push(l.clone());
                }
                Row::Day(d) => {
                    tl.spans.push(CardSpan {
                        from: d.shown_ts,
                        to: d.t,
                        card: OpenCard::Day {
                            target_day: d.target_day,
                        },
                        probe: None,
                        debug: d.debug,
                    });
                    if d.trigger == DayTrigger::Quit {
                        tl.quits.push(d.shown_ts);
                    }
                    if d.closed_by != DayClosedBy::DayEnd {
                        tl.day_closes.push((d.t, d.target_day, d.answered, d.debug));
                    }
                    tl.days.push(*d);
                }
                Row::MetaStart { .. } | Row::MetaEnd { .. } => {}
            }
        }
        // ★ ファイルの終わりまで開いていたカード: 次のファイルでラベルが出ればそこで閉じる（ローテートまたぎ）。
        //   走行が終わったなら（次のファイルが走行の始まりなら）その時点で閉じる。
        let next_is_rotation = files
            .get(fi + 1)
            .and_then(InputFile::session_start)
            .is_some_and(|ns| ns.saturating_sub(end) < ROTATION_GAP_MS);
        if !next_is_rotation {
            for (_, from, st, sched, dbg) in open_probes.drain(..) {
                tl.spans.push(probe_span(from, end, st, sched, dbg));
            }
        }
    }
    for (_, from, st, sched, dbg) in open_probes.drain(..) {
        tl.spans.push(probe_span(from, tl.last_ms, st, sched, dbg));
    }
    // スリープからの復帰の推定: 溜まった候補の抑制の行（t − candidate_ts ≥ 30 秒）の t が復帰の tick
    for s in &tl.suppressed {
        if s.t.saturating_sub(s.candidate_ts) >= GAP_AS_POWER_RESUME_MS + S1_TICK_LAG_MS
            && !tl.frames.iter().any(|f| f.activation_lo == s.t)
        {
            tl.power_resumes.push(s.t);
        }
    }
    tl.power_resumes.sort_unstable();
    tl.power_resumes.dedup();
    let mut times: Vec<u64> = files
        .iter()
        .flat_map(|f| f.rows.iter().filter_map(row_time))
        .collect();
    times.sort_unstable();
    tl.gap_ends = times
        .windows(2)
        .filter(|w| w[1].saturating_sub(w[0]) >= GAP_AS_POWER_RESUME_MS)
        .map(|w| w[1])
        .collect();
    tl.presses.sort_unstable();
    tl.focus.sort_unstable();
    tl.decision_times.sort_unstable();
    tl
}

fn probe_span(from: u64, to: u64, stratum: Stratum, scheduled_ts: u64, debug: bool) -> CardSpan {
    // ★ 確かめ用のカードは押した tick の直後から開いている（割り当ての行の位置の時刻）
    if debug {
        return CardSpan {
            from,
            to,
            card: if stratum == Stratum::Random {
                OpenCard::Random
            } else {
                OpenCard::Strat
            },
            probe: Some((stratum, scheduled_ts)),
            debug,
        };
    }
    CardSpan {
        // ★ カードは候補（層化なら引き金の押下）の時刻 + 2 秒より前の tick には出ない（調停器の時計が 2 秒遅れ・
        //   tick は最大 1 秒遅れる）。割り当ての行の位置の時刻は発火の tick より前になりうるので、再生が自分で
        //   発火させていない間は「候補 + 3 秒」より後から開いているとみなす（再生が発火させれば `fired_at` で直す）。
        from: from.max(scheduled_ts.saturating_add(S1_TICK_LAG_MS + 1_000)),
        to,
        card: if stratum == Stratum::Random {
            OpenCard::Random
        } else {
            OpenCard::Strat
        },
        probe: Some((stratum, scheduled_ts)),
        debug,
    }
}

// ---------------------------------------------------------------------------
// 回す
// ---------------------------------------------------------------------------

/// 再生が出した判定。
#[derive(Debug, Clone, PartialEq, Eq)]
enum Replayed {
    Decision {
        stratum: Stratum,
        key_ms: u64,
        /// `None` = 発火、`Some` = 抑制の理由。
        suppressed: Option<SuppressReason>,
    },
    /// 差し替え（`probe_id` は記録の層化のカード）。
    Supersede {
        probe_id_key: (Stratum, u64),
        wall: u64,
    },
    DayShow {
        target_day: i64,
        trigger: DayTrigger,
        delayed: bool,
        wall: u64,
    },
    DayEnd {
        target_day: i64,
        wall: u64,
    },
}

/// 再生の設定（外から渡すもの）。
#[derive(Debug, Clone, Default)]
pub struct ReplayOptions {
    /// 時差（秒）。`None` なら日の問いと no_ask は照合しない。
    pub utc_offset_secs: Option<i32>,
    /// 前日までの日の状態（`--day-state`）。
    pub day_state: Option<DayState>,
}

fn code(s: Stratum) -> u8 {
    match s {
        Stratum::Random => 0,
        Stratum::LowOperationEnd => 1,
        Stratum::Resumption => 2,
    }
}

fn split_due(q: &mut Vec<u64>, now: u64, out: &mut Vec<u64>) {
    let k = q.partition_point(|&t| t <= now);
    out.extend(q.drain(..k));
}

/// 1 つの位相で回す。
fn run_phase(tl: &Timeline, opts: &ReplayOptions, phase_ms: u64) -> Vec<Replayed> {
    let offset = opts.utc_offset_secs.unwrap_or(0);
    let mut out = Vec::new();
    let Some(first) = tl.frames.first() else {
        return out;
    };
    let mut day = Some(DayQuestion::new(opts.day_state.clone().unwrap_or_default()));
    let mut arbiter: Option<Arbiter> = None;
    let mut frame_idx: usize = 0;
    let mut active_end: u64 = 0;
    let mut presses_q: Vec<u64> = Vec::new();
    let mut focus_q: Vec<u64> = Vec::new();
    let (mut pi, mut fi, mut pause_i, mut quit_i, mut close_i, mut power_i) = (0, 0, 0, 0, 0, 0);
    let mut paused = false;
    let mut epoch: u64 = 0;
    let mut started = false;
    // 記録の割り当て（層・時刻）→ 再生が発火させた壁時計（開いた区間の始まりを直す）
    let mut fired_at: HashMap<(u8, u64), u64> = HashMap::new();
    // 再生が出した日の問いの通し番号（対象の日 → card_id）
    let mut day_ids: HashMap<i64, u64> = HashMap::new();
    let mut wall = first
        .activation_lo
        .saturating_sub(first.activation_lo % 1_000)
        + phase_ms;
    if wall < first.activation_lo {
        wall += 1_000;
    }
    // ★ 最初の枠より前の一時停止の行は、駆動役では調停器の無い tick で縁が進んでいる（枠の最初の tick を
    //   再開として扱わない）。ループの前に状態だけ進める
    while pause_i < tl.pauses.len() && tl.pauses[pause_i].0 < wall.saturating_sub(1_000) {
        paused = tl.pauses[pause_i].1;
        epoch += 1;
        pause_i += 1;
    }
    let mut last_paused = paused;
    let mut last_epoch = epoch;
    let last = tl.last_ms;
    // 開いているカードの区間の索引（毎 tick に全部をなめない）
    let mut order: Vec<usize> = (0..tl.spans.len()).collect();
    order.sort_by_key(|&k| span_lower(&tl.spans[k]));
    let mut span_i = 0;
    let mut active: Vec<usize> = Vec::new();
    while wall <= last {
        // 一時停止の行（本物は止める側のコマンドが tick の前に `on_pause_requested` を呼ぶ）
        while pause_i < tl.pauses.len() && tl.pauses[pause_i].0 <= wall {
            let (t, p) = tl.pauses[pause_i];
            if p && !paused {
                let (d, m) = local_clock(t.saturating_sub(S1_TICK_LAG_MS), offset);
                if let Some(a) = arbiter.as_mut() {
                    let cfg = *a.config();
                    a.day_question_mut().on_pause(&cfg, d, m);
                }
            }
            paused = p;
            epoch += 1;
            pause_i += 1;
        }
        // 入力（行の時刻に届いたとみなす。調停器には 2 秒遅らせた時刻までしか渡らない）
        while pi < tl.presses.len() && tl.presses[pi] <= wall {
            presses_q.push(tl.presses[pi]);
            pi += 1;
        }
        while fi < tl.focus.len() && tl.focus[fi] <= wall {
            focus_q.push(tl.focus[fi]);
            fi += 1;
        }
        // 枠の始まりと終わり（★ 駆動役と同じく、入力を受けた後に枠を作り、起点より前の入力を捨てる）
        if arbiter.is_some() && wall > active_end {
            day = arbiter.take().map(Arbiter::into_day_question);
        }
        while frame_idx < tl.frames.len() && tl.frames[frame_idx].activation_lo <= wall {
            let f = &tl.frames[frame_idx];
            let d = arbiter
                .take()
                .map(Arbiter::into_day_question)
                .or_else(|| day.take())
                .unwrap_or_else(DayQuestion::disabled);
            if f.app_start {
                started = false;
            }
            arbiter = Some(Arbiter::new(
                f.frame.config,
                f.frame.frame_seed,
                f.frame.anchor_ms,
                d,
            ));
            active_end = f.end_ms;
            presses_q.retain(|&t| t >= f.frame.anchor_ms);
            focus_q.retain(|&t| t >= f.frame.anchor_ms);
            frame_idx += 1;
        }
        // 開いているカードの候補（始まりの下限の順に足し、閉じた後 1 秒で外す）
        while span_i < order.len() && span_lower(&tl.spans[order[span_i]]) <= wall {
            active.push(order[span_i]);
            span_i += 1;
        }
        active.retain(|&k| tl.spans[k].to.saturating_add(1_000) >= wall);
        let open = open_card_at(tl, &active, &fired_at, wall);
        // 終了の補助（本物はトレイのコマンドが tick の外で `on_quit` を呼ぶ）
        while quit_i < tl.quits.len() && tl.quits[quit_i] <= wall {
            let t = tl.quits[quit_i];
            quit_i += 1;
            if paused {
                continue;
            }
            let (d, m) = local_clock(t.saturating_sub(S1_TICK_LAG_MS), offset);
            if let Some(a) = arbiter.as_mut() {
                let cfg = *a.config();
                let before = open_card_at(tl, &active, &fired_at, t);
                if let Some(Action::ShowDayQuestion {
                    card_id,
                    target_day,
                    trigger,
                    delayed,
                    ..
                }) = a.day_question_mut().on_quit(&cfg, d, m, before)
                {
                    day_ids.insert(target_day, card_id);
                    out.push(Replayed::DayShow {
                        target_day,
                        trigger,
                        delayed,
                        wall: t,
                    });
                }
            }
        }
        // 記録の日の問いの閉じ（本人の操作）
        while close_i < tl.day_closes.len() && tl.day_closes[close_i].0 <= wall {
            let (_, target_day, answered, debug) = tl.day_closes[close_i];
            close_i += 1;
            if debug {
                continue;
            }
            if let (Some(a), Some(&id)) = (arbiter.as_mut(), day_ids.get(&target_day)) {
                a.day_question_mut().on_closed(id, target_day, answered);
            }
        }
        let mut power_resumed = false;
        while power_i < tl.power_resumes.len() && tl.power_resumes[power_i] <= wall {
            power_resumed = true;
            power_i += 1;
        }
        let epoch_changed = epoch != last_epoch;
        let resumed = !paused && (last_paused || epoch_changed);
        last_paused = paused;
        last_epoch = epoch;
        if let Some(a) = arbiter.as_mut() {
            let now = wall.saturating_sub(S1_TICK_LAG_MS);
            let mut presses = Vec::new();
            let mut focus = Vec::new();
            if paused {
                presses_q.clear();
                focus_q.clear();
            } else {
                split_due(&mut presses_q, now, &mut presses);
                split_due(&mut focus_q, now, &mut focus);
            }
            let (local_day, local_minute) = local_clock(now, offset);
            let input = TickInput {
                now_ms: now,
                key_presses_ms: &presses,
                focus_transitions_ms: &focus,
                paused,
                resumed,
                open_card: open,
                local_day,
                local_minute,
                app_started: !started,
                power_resumed,
            };
            started = true;
            for action in a.tick(&input) {
                match action {
                    Action::FireProbe {
                        stratum,
                        scheduled_ts,
                    } => {
                        fired_at
                            .entry((code(stratum), scheduled_ts))
                            .or_insert(wall);
                        out.push(Replayed::Decision {
                            stratum,
                            key_ms: scheduled_ts,
                            suppressed: None,
                        });
                    }
                    Action::Suppress {
                        stratum,
                        candidate_ts,
                        reason,
                    } => out.push(Replayed::Decision {
                        stratum,
                        key_ms: candidate_ts,
                        suppressed: Some(reason),
                    }),
                    Action::SupersedeOpenStrat => {
                        // ★ 確かめ用のカードの差し替えは記録の側でも照合の外（`debug` の行）
                        if let Some(key) = open_probe_at(tl, &active, &fired_at, wall)
                            .filter(|(s, _)| *s != Stratum::Random)
                        {
                            out.push(Replayed::Supersede {
                                probe_id_key: key,
                                wall,
                            });
                        }
                    }
                    Action::ShowDayQuestion {
                        card_id,
                        target_day,
                        trigger,
                        delayed,
                        ..
                    } => {
                        day_ids.insert(target_day, card_id);
                        out.push(Replayed::DayShow {
                            target_day,
                            trigger,
                            delayed,
                            wall,
                        });
                    }
                    Action::CloseDayQuestion {
                        target_day,
                        closed_by: DayClosedBy::DayEnd,
                        ..
                    } => out.push(Replayed::DayEnd { target_day, wall }),
                    Action::CloseDayQuestion { .. } => {}
                }
            }
        } else {
            // ★ 駆動役は調停器が無い tick で待ち行列を捨てる（`s1_driver.rs` の tick）
            presses_q.clear();
            focus_q.clear();
            // 次の枠まで何も判定しないので、次の枠の最初の tick の手前まで飛ばす（ファイルの間の空白を毎秒回さない）
            match tl.frames.get(frame_idx) {
                // ★ 次の枠の 1 つ前の tick（まだ調停器が無い）に着地させる。その tick で、飛ばした間の入力を
                //   捨て、一時停止の縁（`last_epoch`・`last_paused`）を進めてから枠を作る（駆動役は毎 tick そうする・
                //   /cross-review の security-checker と code-reviewer の MEDIUM）
                Some(next) if next.activation_lo > wall.saturating_add(2_000) => {
                    let k = (next.activation_lo - wall - 1) / 1_000;
                    wall = wall.saturating_add(k.saturating_sub(1) * 1_000);
                }
                Some(_) => {}
                None => break,
            }
        }
        wall = wall.saturating_add(1_000);
    }
    out
}

fn span_from(s: &CardSpan, fired_at: &HashMap<(u8, u64), u64>) -> u64 {
    match s.probe {
        Some((st, t)) if !s.debug => fired_at.get(&(code(st), t)).copied().unwrap_or(s.from),
        _ => s.from,
    }
}

/// 区間が開きうる最も早い時刻（索引の順）。★ 本物のプローブは候補 + 2 秒より前の tick には出ない。
fn span_lower(s: &CardSpan) -> u64 {
    match s.probe {
        Some((_, t)) if !s.debug => s.from.min(t.saturating_add(S1_TICK_LAG_MS)),
        _ => s.from,
    }
}

/// 壁時計 `wall` の tick の前に開いていたカード（★ プローブがあれば日の問いより優先・`s1_driver.rs`）。
/// `active` は開きうる区間の番号（`run_phase` の索引）。
fn open_card_at(
    tl: &Timeline,
    active: &[usize],
    fired_at: &HashMap<(u8, u64), u64>,
    wall: u64,
) -> Option<OpenCard> {
    let mut day = None;
    for &k in active {
        let s = &tl.spans[k];
        let from = span_from(s, fired_at);
        if wall > from && wall <= s.to {
            match s.card {
                OpenCard::Day { .. } => day = Some(s.card),
                c => return Some(c),
            }
        }
    }
    day
}

/// いま開いている本物のプローブのカード（確かめ用は除く）。
fn open_probe_at(
    tl: &Timeline,
    active: &[usize],
    fired_at: &HashMap<(u8, u64), u64>,
    wall: u64,
) -> Option<(Stratum, u64)> {
    active.iter().find_map(|&k| {
        let s = &tl.spans[k];
        let from = span_from(s, fired_at);
        (!s.debug && wall > from && wall <= s.to)
            .then_some(s.probe)
            .flatten()
    })
}

// ---------------------------------------------------------------------------
// 照合
// ---------------------------------------------------------------------------

/// 照合の分類（1 件にひとつ）。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum Class {
    Match,
    DebugCheck,
    BoundaryPause,
    NearPauseOutsideWindow,
    BoundaryTick,
    BoundaryActivation,
    UnverifiedOffsetUnknown,
    UnverifiedPriorDayState,
    UnverifiedPowerResume,
    UnverifiedAppStart,
    UnverifiedTail,
    /// 両方にあるが中身（発火と抑制・理由）が違う。
    Differ,
    /// 再生にあり記録に無い（記録の欠け）。
    Missing,
    /// 記録にあり再生に無い（記録の余り）。
    Extra,
}

/// 照合の種類。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum Kind {
    Random,
    LowOperationEnd,
    Resumption,
    Superseded,
    DayQuestion,
    DayEnd,
}

fn kind_of(s: Stratum) -> Kind {
    match s {
        Stratum::Random => Kind::Random,
        Stratum::LowOperationEnd => Kind::LowOperationEnd,
        Stratum::Resumption => Kind::Resumption,
    }
}

/// 照合の 1 件（`match` 以外を出力に並べる）。
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct Item {
    pub kind: Kind,
    pub key_ms: u64,
    pub class: Class,
    /// 記録の側（`fire`・抑制の理由・`shown`・`superseded`）。無ければ `None`。
    pub recorded: Option<String>,
    /// 再生の側。
    pub replayed: Option<String>,
    /// 4 つの位相で照合の結果（一致したか）が同じだったか。
    pub phase_stable: bool,
}

fn outcome_str(s: Option<SuppressReason>) -> String {
    match s {
        None => "fire".to_string(),
        Some(r) => r.as_str().to_string(),
    }
}

/// 照合の生の結果（分類の前）。
#[derive(Debug, Clone, PartialEq, Eq)]
struct Raw {
    kind: Kind,
    key_ms: u64,
    /// 位相をまたいで同じ項目を指す名（判定は鍵の時刻、日の問いは対象の日と契機）。
    /// ★ 再生にだけ出た日の問いの鍵は tick の壁時計で位相ごとに違うので、鍵では位相をまたいで結べない
    ///   （code-reviewer HIGH: 結べないと必ず `boundary_tick` になり、記録の欠けが赤にならない）。
    stab: String,
    recorded: Option<String>,
    replayed: Option<String>,
}

impl Raw {
    fn matched(&self) -> bool {
        self.recorded.is_some() && self.recorded == self.replayed
    }
    fn id(&self) -> (Kind, String) {
        (self.kind, self.stab.clone())
    }
}

/// 1 つの位相の再生と記録を突き合わせる（記録の確かめ用の行は除いてある）。
fn compare(tl: &Timeline, replayed: &[Replayed]) -> Vec<Raw> {
    let mut raws: BTreeMap<(Kind, u64), Raw> = BTreeMap::new();
    // ★ 記録に同じ鍵の行が 2 行以上あれば、2 行目以降を別の項目にする（二重に書く不具合を一致として潰さない）
    let mut dups: Vec<Raw> = Vec::new();
    let mut put = |kind: Kind, key: u64, stab: String, rec: Option<String>, rep: Option<String>| {
        let e = raws.entry((kind, key)).or_insert(Raw {
            kind,
            key_ms: key,
            stab: stab.clone(),
            recorded: None,
            replayed: None,
        });
        if rec.is_some() {
            if e.recorded.is_some() {
                let n = dups
                    .iter()
                    .filter(|d| d.kind == kind && d.key_ms == key)
                    .count();
                dups.push(Raw {
                    kind,
                    key_ms: key,
                    stab: format!("{stab}#dup{}", n + 1),
                    recorded: rec,
                    replayed: None,
                });
                return;
            }
            e.recorded = rec;
        }
        if rep.is_some() {
            e.replayed = rep;
        }
    };
    // 判定（発火・抑制）
    for a in tl.assigned.iter().filter(|a| !a.debug) {
        put(
            kind_of(a.stratum),
            a.scheduled_ts,
            a.scheduled_ts.to_string(),
            Some(outcome_str(None)),
            None,
        );
    }
    for s in &tl.suppressed {
        put(
            kind_of(s.stratum),
            s.candidate_ts,
            s.candidate_ts.to_string(),
            Some(outcome_str(Some(s.reason))),
            None,
        );
    }
    // 差し替え（記録は層化のカードの `superseded` のラベル。鍵は割り当ての時刻）
    let by_id: HashMap<&str, &AssignedRow> = tl
        .assigned
        .iter()
        .map(|a| (a.probe_id.as_str(), a))
        .collect();
    for l in tl
        .labels
        .iter()
        .filter(|l| !l.debug && l.skip_reason == "superseded")
    {
        if let Some(a) = by_id.get(l.probe_id.as_str()) {
            put(
                Kind::Superseded,
                a.scheduled_ts,
                a.scheduled_ts.to_string(),
                Some("superseded".into()),
                None,
            );
        }
    }
    // 日の問い（出した時刻は ±1 秒で寄せる）
    // ★ 位相をまたいで結ぶ名は「ラベル＋同じラベルの中の通し番号」（同じラベルが 2 件あっても潰さない・
    //   /cross-review の code-reviewer MEDIUM）。記録と寄せた再生は記録の名を使う
    let mut day_keys: Vec<(i64, DayTrigger, bool, u64, String)> = Vec::new();
    let mut seen: HashMap<String, usize> = HashMap::new();
    let mut ordinal = |label: &str| {
        let n = seen.entry(label.to_string()).or_default();
        *n += 1;
        format!("{label}#{n}")
    };
    for d in tl.days.iter().filter(|d| !d.debug) {
        let label = day_label(d.target_day, d.trigger, d.delayed);
        let stab = ordinal(&label);
        day_keys.push((d.target_day, d.trigger, d.delayed, d.shown_ts, stab.clone()));
        put(Kind::DayQuestion, d.shown_ts, stab, Some(label), None);
        if d.closed_by == DayClosedBy::DayEnd {
            let label = format!("day_end:{}", d.target_day);
            put(Kind::DayEnd, d.t, ordinal(&label), Some(label), None);
        }
    }
    let mut day_end_keys: Vec<(i64, u64)> = tl
        .days
        .iter()
        .filter(|d| !d.debug && d.closed_by == DayClosedBy::DayEnd)
        .map(|d| (d.target_day, d.t))
        .collect();
    let mut day_end_stabs: Vec<String> = Vec::new();
    {
        let mut n: HashMap<i64, usize> = HashMap::new();
        for &(day, _) in &day_end_keys {
            let k = n.entry(day).or_default();
            *k += 1;
            day_end_stabs.push(format!("day_end:{day}#{k}"));
        }
    }
    let mut replay_only: HashMap<String, usize> = HashMap::new();
    let mut replay_only_stab = |label: &str| {
        let n = replay_only.entry(label.to_string()).or_default();
        *n += 1;
        format!("{label}#r{n}")
    };
    for r in replayed {
        match r {
            Replayed::Decision {
                stratum,
                key_ms,
                suppressed,
            } => put(
                kind_of(*stratum),
                *key_ms,
                key_ms.to_string(),
                None,
                Some(outcome_str(*suppressed)),
            ),
            Replayed::Supersede { probe_id_key, .. } => put(
                Kind::Superseded,
                probe_id_key.1,
                probe_id_key.1.to_string(),
                None,
                Some("superseded".into()),
            ),
            Replayed::DayShow {
                target_day,
                trigger,
                delayed,
                wall,
            } => {
                let label = day_label(*target_day, *trigger, *delayed);
                // 記録の同じ鍵の日の問いのうち、出した時刻が近いものに寄せる
                let near = day_keys.iter().position(|k| {
                    k.0 == *target_day
                        && k.1 == *trigger
                        && k.2 == *delayed
                        && k.3.abs_diff(*wall) <= DAY_SHOWN_TOLERANCE_MS
                });
                let (key, stab) = match near {
                    Some(i) => {
                        let k = day_keys.remove(i);
                        (k.3, k.4)
                    }
                    None => (*wall, replay_only_stab(&label)),
                };
                put(Kind::DayQuestion, key, stab, None, Some(label));
            }
            Replayed::DayEnd { target_day, wall } => {
                let near = day_end_keys.iter().position(|k| {
                    k.0 == *target_day && k.1.abs_diff(*wall) <= DAY_SHOWN_TOLERANCE_MS
                });
                let (key, stab) = match near {
                    Some(i) => (day_end_keys.remove(i).1, day_end_stabs.remove(i)),
                    None => (*wall, replay_only_stab(&format!("day_end:{target_day}"))),
                };
                put(
                    Kind::DayEnd,
                    key,
                    stab,
                    None,
                    Some(format!("day_end:{target_day}")),
                );
            }
        }
    }
    let mut out: Vec<Raw> = raws.into_values().collect();
    out.extend(dups);
    out
}

fn day_label(target_day: i64, trigger: DayTrigger, delayed: bool) -> String {
    format!("{}:{}:{}", target_day, trigger.as_str(), delayed)
}

/// 一致しなかった 1 件を分類する（判断 2・design の順）。
fn classify(tl: &Timeline, opts: &ReplayOptions, raw: &Raw, phase_stable: bool) -> Class {
    let k = raw.key_ms;
    let is_day = matches!(raw.kind, Kind::DayQuestion | Kind::DayEnd);
    for &(p, paused) in &tl.pauses {
        if paused && k <= p && p - k <= PAUSE_BOUNDARY_MS {
            return Class::BoundaryPause;
        }
    }
    for &(p, paused) in &tl.pauses {
        if paused && k < p && p - k > PAUSE_BOUNDARY_MS && p - k <= NEAR_PAUSE_MS {
            return Class::NearPauseOutsideWindow;
        }
    }
    if !phase_stable {
        return Class::BoundaryTick;
    }
    if tl.frames.iter().any(|f| {
        k <= f.activation_hi + ACTIVATION_BOUNDARY_MS
            && k + ACTIVATION_BOUNDARY_MS >= f.activation_lo
    }) {
        return Class::BoundaryActivation;
    }
    // ★ no_ask は現地の時刻で決まる。時差が無いとき、no_ask の判定が絡む項目だけを未照合にする
    let no_ask =
        raw.recorded.as_deref() == Some("no_ask") || raw.replayed.as_deref() == Some("no_ask");
    if opts.utc_offset_secs.is_none() && (is_day || no_ask) {
        return Class::UnverifiedOffsetUnknown;
    }
    if is_day && opts.day_state.is_none() {
        let first_day = local_clock(tl.first_ms, opts.utc_offset_secs.unwrap_or(0)).0;
        let rec_day = raw
            .recorded
            .as_deref()
            .or(raw.replayed.as_deref())
            .and_then(|s| s.split(':').next())
            .and_then(|d| d.parse::<i64>().ok());
        if rec_day.is_some_and(|d| d < first_day) {
            return Class::UnverifiedPriorDayState;
        }
    }
    // ★ 記録だけがウォームアップで抑制したのは、記録に行の無いスリープからの復帰（調停器はウォームアップを
    //   やり直す）が見えないときだけ。行が 30 秒以上途切れた直後か、推定した復帰の直後に限る
    //   （限らないとウォームアップの判定の退行を見逃す・code-reviewer MEDIUM）。
    if raw.recorded.as_deref() == Some("warmup") {
        let warmup = tl
            .frames
            .iter()
            .map(|f| f.frame.config.random.min_session_elapsed_ms)
            .max()
            .unwrap_or(0)
            .saturating_add(S1_TICK_LAG_MS + 1_000);
        let after_gap = tl
            .gap_ends
            .iter()
            .chain(tl.power_resumes.iter())
            .any(|&g| k >= g.saturating_sub(S1_TICK_LAG_MS) && k <= g.saturating_add(warmup));
        if after_gap {
            return Class::UnverifiedPowerResume;
        }
    }
    if is_day
        && tl.frames.iter().any(|f| {
            f.app_start && k >= f.activation_lo && k - f.activation_lo <= APP_START_WINDOW_MS
        })
    {
        return Class::UnverifiedAppStart;
    }
    if raw.recorded.is_none() {
        // 枠の中の記録の最後の判定の行より後で、再生だけが判定した（同意の取り消しの後とみなす）。
        // ★ 取り消しの後は日の問いも出ないので、日の問いも同じ扱いにする
        let frame = tl
            .frames
            .iter()
            .find(|f| k.saturating_add(S1_TICK_LAG_MS) >= f.activation_lo && k <= f.end_ms);
        if let Some(f) = frame {
            let last_rec = tl
                .decision_times
                .iter()
                .copied()
                .filter(|&t| t >= f.activation_lo && t <= f.end_ms)
                .max();
            // ★ 枠に判定の行が 1 行も無いなら取り消しではなく全面的な欠けとして残す（code-reviewer MEDIUM）。
            //   取り消しの後も O1 の記録（押下）は続くので、鍵の後に押下が無ければ（記録の後ろが落ちた）欠けのまま
            let presses_after = tl
                .presses
                .get(tl.presses.partition_point(|&p| p <= k))
                .is_some_and(|&p| p <= f.end_ms);
            if last_rec.is_some_and(|t| k > t) && presses_after {
                return Class::UnverifiedTail;
            }
        }
    }
    match (&raw.recorded, &raw.replayed) {
        (Some(_), Some(_)) => Class::Differ,
        (None, Some(_)) => Class::Missing,
        _ => Class::Extra,
    }
}

// ---------------------------------------------------------------------------
// 出力
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize)]
pub struct Counts {
    #[serde(rename = "match")]
    pub matched: usize,
    /// `match` のうち、位相によって一致しない位相もあったもの（内訳・`match` に含まれる）。
    pub match_phase_sensitive: usize,
    pub differ: usize,
    pub missing: usize,
    pub extra: usize,
    pub boundary_pause: usize,
    pub near_pause_outside_window: usize,
    pub boundary_tick: usize,
    pub boundary_activation: usize,
    pub debug_check: usize,
    pub unverified: Unverified,
}

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize)]
pub struct Unverified {
    pub offset_unknown: usize,
    pub prior_day_state: usize,
    pub power_resume: usize,
    pub app_start: usize,
    pub tail: usize,
}

impl Counts {
    fn add(&mut self, c: Class) {
        match c {
            Class::Match => self.matched += 1,
            Class::Differ => self.differ += 1,
            Class::Missing => self.missing += 1,
            Class::Extra => self.extra += 1,
            Class::BoundaryPause => self.boundary_pause += 1,
            Class::NearPauseOutsideWindow => self.near_pause_outside_window += 1,
            Class::BoundaryTick => self.boundary_tick += 1,
            Class::BoundaryActivation => self.boundary_activation += 1,
            Class::DebugCheck => self.debug_check += 1,
            Class::UnverifiedOffsetUnknown => self.unverified.offset_unknown += 1,
            Class::UnverifiedPriorDayState => self.unverified.prior_day_state += 1,
            Class::UnverifiedPowerResume => self.unverified.power_resume += 1,
            Class::UnverifiedAppStart => self.unverified.app_start += 1,
            Class::UnverifiedTail => self.unverified.tail += 1,
        }
    }
}

/// カードの集計（回答率・S1-A4・A7）。記録だけから数える。
#[derive(Debug, Clone, Default, PartialEq, Serialize)]
pub struct Cards {
    pub total: usize,
    pub answered: usize,
    pub skipped_by_person: BTreeMap<String, usize>,
    /// 調停器が書いた差し替え（本人の未回答と分ける）。
    pub superseded: usize,
    pub dropped_by_pause: usize,
    pub dropped_at_quit: usize,
    pub carried_across_rotation: usize,
    pub open_at_input_end: usize,
    /// 割り当ての無いラベル。
    pub orphan: usize,
    /// 同じカードの 2 行目以降のラベル（数えない）。
    pub duplicate_labels: usize,
    pub debug: usize,
    /// 答えた数 ÷（本物のカード − 差し替え − 一時停止・終了・入力の終わりで下ろしたもの）。分母が 0 なら `None`。
    pub response_rate_excl_superseded: Option<f64>,
}

#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize)]
pub struct LagCheck {
    pub s1_tick_lag_ms: u64,
    /// 鍵の時刻の 2 秒前までに押下がある判定（押下が届き切っていたかに依る項目）。
    pub lag_sensitive_items: usize,
    pub lag_sensitive_matched: usize,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct FrameOut {
    pub file: String,
    pub anchor_ms: u64,
    pub activation_ms: Window,
    pub end_ms: u64,
    pub app_start: bool,
    /// この枠で最初に `differ`・`missing`・`extra` になった鍵の時刻。
    pub first_divergence_ms: Option<u64>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
pub struct Window {
    pub lo: u64,
    pub hi: u64,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct ProbesReport {
    pub mode: &'static str,
    pub replay_version: &'static str,
    pub arbiter_version: &'static str,
    pub utc_offset_secs: Option<i32>,
    pub day_state_given: bool,
    pub tick_phases_ms: Vec<u64>,
    pub inputs: Vec<String>,
    /// JSON として読めず飛ばした行の数（全ファイルの合計）。
    pub skipped_lines: usize,
    pub frames: Vec<FrameOut>,
    pub counts: Counts,
    pub by_kind: BTreeMap<Kind, Counts>,
    /// `match` 以外の項目（鍵の時刻の順）。
    pub items: Vec<Item>,
    pub cards: Cards,
    pub lag_check: LagCheck,
    /// 記録に無いので再生が推定したスリープからの復帰（溜まった候補の抑制の行から）。
    pub power_resumes_inferred: Vec<u64>,
    pub notes: Vec<&'static str>,
}

const NOTES: [&str; 3] = [
    "missing = 再生にあり記録に無い（記録の欠け）・extra = 記録にあり再生に無い（記録の余り）",
    "区間の削除は NDJSON に印を残さないので、削除した区間をまたぐ記録は一致しない",
    "一時停止の間に閉じた日の問いは行が無く、再生からは見えない",
];

/// `gse-replay --probes` の本体。`files` は `order_inputs` で並べたもの。
pub fn replay_probes(files: &[InputFile], opts: &ReplayOptions) -> ProbesReport {
    let tl = build_timeline(files);
    let runs: Vec<Vec<Raw>> = TICK_PHASES_MS
        .iter()
        .map(|&ph| compare(&tl, &run_phase(&tl, opts, ph)))
        .collect();
    // 位相ごとの一致の有無
    let mut matched_by_phase: HashMap<(Kind, String), Vec<bool>> = HashMap::new();
    for run in &runs {
        for r in run {
            matched_by_phase
                .entry(r.id())
                .or_default()
                .push(r.matched());
        }
    }
    let mut counts = Counts::default();
    let mut by_kind: BTreeMap<Kind, Counts> = BTreeMap::new();
    let mut items = Vec::new();
    for raw in &runs[0] {
        let flags = &matched_by_phase[&raw.id()];
        let stable = flags.len() == runs.len() && flags.iter().all(|&m| m == flags[0]);
        // ★ どれかの位相で一致すれば一致（記録の tick の位相は分からないので、説明できる位相があれば足りる）。
        //   位相に敏感な一致は別に数える（/cross-review の Codex P1: 位相 0 だけを見ると非対称になる）
        let any_match = flags.iter().any(|&m| m);
        if any_match && !stable {
            counts.match_phase_sensitive += 1;
        }
        let class = if any_match {
            Class::Match
        } else {
            classify(&tl, opts, raw, stable)
        };
        counts.add(class);
        by_kind.entry(raw.kind).or_default().add(class);
        if class != Class::Match {
            items.push(Item {
                kind: raw.kind,
                key_ms: raw.key_ms,
                class,
                recorded: raw.recorded.clone(),
                replayed: raw.replayed.clone(),
                phase_stable: stable,
            });
        }
    }
    // 確かめ用の行（照合の外・数だけ）
    let debug_rows =
        tl.assigned.iter().filter(|a| a.debug).count() + tl.days.iter().filter(|d| d.debug).count();
    for _ in 0..debug_rows {
        counts.add(Class::DebugCheck);
    }
    items.sort_by_key(|i| (i.key_ms, i.kind));
    let frames = tl
        .frames
        .iter()
        .map(|f| FrameOut {
            file: f.file.clone(),
            anchor_ms: f.frame.anchor_ms,
            activation_ms: Window {
                lo: f.activation_lo,
                hi: f.activation_hi,
            },
            end_ms: f.end_ms,
            app_start: f.app_start,
            first_divergence_ms: items
                .iter()
                .filter(|i| matches!(i.class, Class::Differ | Class::Missing | Class::Extra))
                .filter(|i| {
                    i.key_ms.saturating_add(S1_TICK_LAG_MS) >= f.activation_lo
                        && i.key_ms <= f.end_ms
                })
                .map(|i| i.key_ms)
                .min(),
        })
        .collect();
    let lag_check = lag_check(&tl, &runs[0]);
    ProbesReport {
        mode: "probes",
        replay_version: REPLAY_VERSION,
        arbiter_version: ARBITER_VERSION,
        utc_offset_secs: opts.utc_offset_secs,
        day_state_given: opts.day_state.is_some(),
        tick_phases_ms: TICK_PHASES_MS.to_vec(),
        inputs: files.iter().map(|f| f.name.clone()).collect(),
        skipped_lines: files.iter().map(|f| f.skipped_lines).sum(),
        frames,
        counts,
        by_kind,
        items,
        cards: cards(files),
        lag_check,
        power_resumes_inferred: tl.power_resumes.clone(),
        notes: NOTES.to_vec(),
    }
}

fn lag_check(tl: &Timeline, raws: &[Raw]) -> LagCheck {
    let mut out = LagCheck {
        s1_tick_lag_ms: S1_TICK_LAG_MS,
        ..LagCheck::default()
    };
    for r in raws.iter().filter(|r| {
        r.recorded.is_some()
            && matches!(
                r.kind,
                Kind::Random | Kind::LowOperationEnd | Kind::Resumption
            )
    }) {
        let lo = r.key_ms.saturating_sub(S1_TICK_LAG_MS);
        let k = tl.presses.partition_point(|&p| p < lo);
        if tl.presses.get(k).is_some_and(|&p| p <= r.key_ms) {
            out.lag_sensitive_items += 1;
            if r.matched() {
                out.lag_sensitive_matched += 1;
            }
        }
    }
    out
}

fn cards(files: &[InputFile]) -> Cards {
    let mut c = Cards::default();
    // probe_id → (ファイルの番号, 確かめ用か)
    let mut assigned: HashMap<&str, (usize, bool)> = HashMap::new();
    let mut labelled: HashSet<&str> = HashSet::new();
    // ★ 開いているカードはローテートをまたいで持つ（/cross-review の Codex・code-reviewer）
    let mut open: Vec<&str> = Vec::new();
    for (fi, f) in files.iter().enumerate() {
        let rotated_from_prev = fi > 0
            && f.session_start()
                .unwrap_or(0)
                .saturating_sub(files[fi - 1].last_ms().unwrap_or(0))
                < ROTATION_GAP_MS;
        if !rotated_from_prev {
            open.clear();
        }
        for r in &f.rows {
            match r {
                Row::Assigned(a) => {
                    assigned.insert(a.probe_id.as_str(), (fi, a.debug));
                    open.push(a.probe_id.as_str());
                }
                Row::Pause { paused: true, .. } => {
                    for id in open.drain(..) {
                        if assigned.get(id).is_some_and(|&(_, d)| !d) {
                            c.dropped_by_pause += 1;
                        }
                        labelled.insert(id);
                    }
                }
                Row::Label(l) => {
                    open.retain(|&id| id != l.probe_id);
                    let Some(&(afi, debug)) = assigned.get(l.probe_id.as_str()) else {
                        c.orphan += 1;
                        continue;
                    };
                    // ★ 同じカードに 2 行目のラベルが来たら数えず、二重として出す（回答率を 1 より大きくしない）
                    if !labelled.insert(l.probe_id.as_str()) {
                        c.duplicate_labels += 1;
                        continue;
                    }
                    if debug {
                        continue;
                    }
                    if afi != fi {
                        c.carried_across_rotation += 1;
                    }
                    if l.answered {
                        c.answered += 1;
                    } else if l.skip_reason == "superseded" {
                        c.superseded += 1;
                    } else {
                        *c.skipped_by_person
                            .entry(l.skip_reason.clone())
                            .or_default() += 1;
                    }
                }
                _ => {}
            }
        }
    }
    for (id, &(fi, debug)) in &assigned {
        if debug {
            c.debug += 1;
            continue;
        }
        c.total += 1;
        if labelled.contains(id) {
            continue;
        }
        // ★ ファイルが `meta` の終わりで閉じ、次がローテートでない（走行が終わった）なら終了で下ろした
        let rotated_into_next = files.get(fi + 1).is_some_and(|n| {
            n.session_start()
                .unwrap_or(0)
                .saturating_sub(files[fi].session_end().unwrap_or(0))
                < ROTATION_GAP_MS
        });
        if files[fi].session_end().is_some() && !rotated_into_next {
            c.dropped_at_quit += 1;
        } else {
            c.open_at_input_end += 1;
        }
    }
    let denom = c.total.saturating_sub(
        c.superseded + c.dropped_by_pause + c.dropped_at_quit + c.open_at_input_end,
    );
    c.response_rate_excl_superseded = (denom > 0).then(|| c.answered as f64 / denom as f64);
    c
}

// ---------------------------------------------------------------------------
// --day-questions
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct DayQuestionPresses {
    pub t: u64,
    pub target_day: i64,
    /// 回答の時刻から次の現地 4:00 までの押下の数。
    pub presses_until_cutoff: usize,
    pub cutoff_ms: u64,
    /// 記録が切れ目まで続いているか（続いていなければ数は途中まで）。
    pub input_covers_cutoff: bool,
    /// 数えた範囲の一時停止の長さ。
    pub paused_ms_in_span: u64,
}

/// 現地の日 `day`（4:00 区切り）が終わる時刻（UTC の ms）。
pub fn day_cutoff_ms(day: i64, utc_offset_secs: i32) -> u64 {
    let secs =
        (day + 1) * 86_400 + crate::eh3::DAY_CUTOFF_HOUR * 3_600 - i64::from(utc_offset_secs);
    u64::try_from(secs.max(0)).unwrap_or(0) * 1_000
}

/// `gse-replay --day-questions` の本体。
pub fn day_question_presses(files: &[InputFile], utc_offset_secs: i32) -> Vec<DayQuestionPresses> {
    let tl = build_timeline(files);
    let mut out = Vec::new();
    for d in tl.days.iter().filter(|d| d.answered && !d.debug) {
        let day = crate::eh3::local_day(d.t, utc_offset_secs);
        let cutoff = day_cutoff_ms(day, utc_offset_secs);
        let lo = tl.presses.partition_point(|&p| p < d.t);
        let hi = tl.presses.partition_point(|&p| p < cutoff);
        let mut paused_ms = 0;
        let mut since: Option<u64> = None;
        for &(t, p) in &tl.pauses {
            if p && since.is_none() {
                since = Some(t);
            } else if !p {
                if let Some(s) = since.take() {
                    paused_ms += overlap(s, t, d.t, cutoff);
                }
            }
        }
        if let Some(s) = since {
            paused_ms += overlap(s, tl.last_ms.max(s), d.t, cutoff);
        }
        out.push(DayQuestionPresses {
            t: d.t,
            target_day: d.target_day,
            presses_until_cutoff: hi.saturating_sub(lo),
            cutoff_ms: cutoff,
            input_covers_cutoff: covers(files, d.t, cutoff),
            paused_ms_in_span: paused_ms,
        });
    }
    out
}

/// 回答の時刻 `t` から `cutoff` まで、記録がローテートの鎖で途切れずに続いているか
/// （/cross-review の Codex P2: 最後の時刻だけを見ると、途中の空白を見逃す）。
fn covers(files: &[InputFile], t: u64, cutoff: u64) -> bool {
    let Some(mut i) = files
        .iter()
        .position(|f| f.session_start().unwrap_or(0) <= t && f.last_ms().unwrap_or(0) >= t)
    else {
        return false;
    };
    loop {
        let end = files[i].last_ms().unwrap_or(0);
        if end >= cutoff {
            return true;
        }
        match files.get(i + 1) {
            Some(n) if n.session_start().unwrap_or(0).saturating_sub(end) < ROTATION_GAP_MS => {
                i += 1
            }
            _ => return false,
        }
    }
}

fn overlap(a0: u64, a1: u64, b0: u64, b1: u64) -> u64 {
    a1.min(b1).saturating_sub(a0.max(b0))
}

#[cfg(test)]
mod tests {

    use super::*;
    use crate::analysis::probe_arbiter::RandomFrame;
    use crate::logger::{LogEntry, ProbeRef, SessionLogger, SkipReason};
    use crate::s1_driver::{Effect, S1Driver, TickEnv};
    use std::time::Duration;

    const JST: i32 = 9 * 3600;
    /// 2026-11-07 09:00 UTC（JST 18:00・日の問いの時間帯 17:00〜23:00 の中）。
    const T0: u64 = 1_794_042_000_000;
    const MIN: u64 = 60_000;

    /// 合成の 1 日（駆動役を回して本物のロガーで書く）。
    #[derive(Clone)]
    struct Scenario {
        anchor: u64,
        seed: u64,
        config: ArbiterConfig,
        end: u64,
        presses: Vec<u64>,
        focus: Vec<u64>,
        pauses: Vec<(u64, bool)>,
        /// 割り当てからこれだけ後に答える（`None` なら答えない）。
        answer_after_ms: Option<u64>,
        /// 押下が駆動役に届くまでの遅れ（陽性対照用）。
        press_delay_ms: u64,
        /// tick の無い区間（スリープ）。
        sleeps: Vec<(u64, u64)>,
        /// (時刻, 新しい seed): ローテート（新しいファイル・新しい枠）。
        rotations: Vec<(u64, u64)>,
        debug_probe_at: Option<u64>,
        day_answer_after_ms: u64,
        /// 駆動役の tick の位相。
        sim_phase_ms: u64,
    }

    /// 打鍵の塊（`from` から `to` まで `every` ごと）。
    fn burst(from: u64, to: u64, every: u64) -> Vec<u64> {
        (0..)
            .map(|k| from + k * every)
            .take_while(|&t| t < to)
            .collect()
    }

    fn base() -> Scenario {
        let anchor = T0;
        // 作業 → 長い途切れ（層化の低操作の終わり） → 作業 → 日の問いの途切れ（20 分）→ 作業
        let mut presses = burst(anchor + 5_000, anchor + 25 * MIN, 1_700);
        presses.extend(burst(anchor + 28 * MIN, anchor + 60 * MIN, 1_300));
        presses.extend(burst(anchor + 62 * MIN, anchor + 100 * MIN, 2_100));
        presses.extend(burst(anchor + 125 * MIN, anchor + 170 * MIN, 1_900));
        Scenario {
            anchor,
            seed: 7,
            config: ArbiterConfig::default(),
            end: anchor + 180 * MIN,
            presses,
            focus: vec![
                anchor + 61 * MIN,
                anchor + 61 * MIN + 30_000,
                anchor + 140 * MIN,
            ],
            pauses: Vec::new(),
            answer_after_ms: Some(6_000),
            press_delay_ms: 50,
            sleeps: Vec::new(),
            rotations: Vec::new(),
            debug_probe_at: None,
            day_answer_after_ms: 9_000,
            sim_phase_ms: 0,
        }
    }

    fn in_range(t: u64, spans: &[(u64, u64)]) -> bool {
        spans.iter().any(|&(a, b)| t >= a && t < b)
    }

    fn paused_at(t: u64, pauses: &[(u64, bool)]) -> bool {
        let mut p = false;
        for &(pt, v) in pauses {
            if pt <= t {
                p = v;
            }
        }
        p
    }

    /// 駆動役の出来事を行に写す（本物の写し `crate::s1_effect_row` と、差し替えのラベルの組み立て関数）。
    fn rows_of(fx: Vec<Effect>, out: &mut Vec<LogEntry>) {
        for e in fx {
            match e {
                Effect::Superseded { t, card } => {
                    let probe = ProbeRef::RandomProbe {
                        probe_id: card.probe_id.clone(),
                    };
                    out.push(
                        LogEntry::realtime_label_skipped(
                            t,
                            &probe,
                            SkipReason::Superseded,
                            0,
                            card.window_start_ms,
                            card.window_end_ms,
                        )
                        .with_s1_debug(card.debug),
                    );
                }
                e => {
                    if let Some(row) = crate::s1_effect_row(e) {
                        out.push(row);
                    }
                }
            }
        }
    }

    /// 回して、ファイルごとの行の列を返す（各ファイルの (始まり, 終わり, 行)）。
    fn simulate(sc: &Scenario) -> Vec<(u64, u64, Vec<LogEntry>)> {
        let mut files: Vec<(u64, u64, Vec<LogEntry>)> = vec![(sc.anchor, sc.end, Vec::new())];
        let env = |wall: u64, paused: bool, epoch: u64| TickEnv {
            wall_ms: wall,
            utc_offset_secs: JST,
            paused,
            pause_epoch: epoch,
            power_gen: 0,
        };
        let mut d = S1Driver::new(
            DayQuestion::new(DayState::default()),
            &env(sc.anchor, false, 0),
        );
        let mut n = 0u32;
        let mut ids = move || {
            n += 1;
            format!("ID{n:014}")
        };
        rows_of(
            d.start_frame(0, sc.anchor, sc.seed, sc.config),
            &mut files[0].2,
        );
        let (mut pi, mut pushed, mut fi, mut pause_i, mut rot_i) = (0, 0, 0, 0, 0);
        let mut paused = false;
        let mut epoch = 0;
        let mut opened_at: Option<(String, u64)> = None;
        let mut debug_done = false;
        let mut wall = sc.anchor + sc.sim_phase_ms;
        while wall <= sc.end {
            if in_range(wall, &sc.sleeps) {
                wall += 1_000;
                continue;
            }
            // ローテート
            while rot_i < sc.rotations.len() && sc.rotations[rot_i].0 <= wall {
                let (r, seed) = sc.rotations[rot_i];
                rot_i += 1;
                files.last_mut().unwrap().1 = r;
                files.push((r, sc.end, Vec::new()));
                rows_of(
                    d.start_frame(rot_i as u64, r, seed, sc.config),
                    &mut files.last_mut().unwrap().2,
                );
            }
            let out = &mut files.last_mut().unwrap().2;
            // 一時停止（止める側のコマンドが tick の前に伏せる）
            while pause_i < sc.pauses.len() && sc.pauses[pause_i].0 <= wall {
                let (t, p) = sc.pauses[pause_i];
                pause_i += 1;
                if p && !paused {
                    rows_of(d.on_pause_requested(t, JST), out);
                    opened_at = None;
                }
                out.push(LogEntry::RecordingPause {
                    timestamp: t,
                    paused: p,
                });
                paused = p;
                epoch += 1;
            }
            // 行（押した時刻に書く）と駆動役への到着（遅れつき）
            while pi < sc.presses.len() && sc.presses[pi] <= wall {
                let t = sc.presses[pi];
                pi += 1;
                if !paused_at(t, &sc.pauses) && !in_range(t, &sc.sleeps) {
                    out.push(LogEntry::Key {
                        vk_code: 0x41,
                        timestamp: t,
                        is_press: true,
                    });
                }
            }
            while pushed < sc.presses.len() && sc.presses[pushed] + sc.press_delay_ms <= wall {
                let t = sc.presses[pushed];
                pushed += 1;
                if !paused_at(t, &sc.pauses) && !in_range(t, &sc.sleeps) {
                    d.push_press(t);
                }
            }
            while fi < sc.focus.len() && sc.focus[fi] <= wall {
                let t = sc.focus[fi];
                fi += 1;
                if !paused_at(t, &sc.pauses) {
                    out.push(LogEntry::FocusTransition { timestamp: t });
                    d.push_focus(t);
                }
            }
            if let Some(t) = sc.debug_probe_at.filter(|&t| t <= wall && !debug_done) {
                debug_done = true;
                let fx = d.debug_show_probe(t, Stratum::Random, "DBG0000000000001".into());
                for e in &fx {
                    if let Effect::Assigned { probe_id, .. } = e {
                        opened_at = Some((probe_id.clone(), t));
                    }
                }
                rows_of(fx, out);
            }
            // 本人の回答（tick の間に届くコマンド）
            if let (Some(after), Some((id, at))) = (sc.answer_after_ms, opened_at.clone()) {
                let t = at + after;
                if t <= wall && !paused {
                    if let Some(card) = d.probe_card(&id).cloned() {
                        let probe = ProbeRef::RandomProbe {
                            probe_id: card.probe_id.clone(),
                        };
                        out.push(
                            LogEntry::realtime_label_answered(
                                t,
                                &probe,
                                3,
                                3,
                                after,
                                card.window_start_ms,
                                card.window_end_ms,
                            )
                            .with_s1_debug(card.debug),
                        );
                        d.close_probe(&id);
                    }
                    opened_at = None;
                }
            }
            if let Some(card) = d.day_card() {
                let t = card.shown_ts + sc.day_answer_after_ms;
                if t <= wall && !paused && d.probe_card("").is_none() {
                    if let Some(row) = d.day_row_for_close(
                        card.card_id,
                        t,
                        Some(4),
                        DayClosedBy::Answer,
                        Some(1_000),
                        Some(500),
                    ) {
                        rows_of(vec![Effect::DayRow(row)], out);
                        rows_of(d.commit_day_close(card.card_id, true), out);
                    }
                }
            }
            let fx = d.tick(&env(wall, paused, epoch), &mut ids);
            for e in &fx {
                if let Effect::Assigned { probe_id, .. } = e {
                    opened_at = Some((probe_id.clone(), wall));
                }
                if let Effect::Superseded { .. } = e {
                    opened_at = None;
                }
            }
            rows_of(fx, out);
            if paused {
                opened_at = None;
            }
            wall += 1_000;
        }
        files
    }

    static FILE_SEQ: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);

    /// 本物のロガーで書き、`meta` の時刻を合成の時刻に直して読む。
    fn write_and_parse(files: Vec<(u64, u64, Vec<LogEntry>)>) -> Vec<InputFile> {
        files
            .into_iter()
            .enumerate()
            .map(|(i, (start, end, rows))| {
                let seq = FILE_SEQ.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
                let path = std::env::temp_dir().join(format!(
                    "gse_s1_replay_{}_{}_{}.ndjson",
                    std::process::id(),
                    seq,
                    i
                ));
                let (logger, tx, shutdown_rx, _status) = SessionLogger::start(path.clone(), None);
                for r in rows {
                    tx.send(r).unwrap();
                }
                tx.send(LogEntry::End).unwrap();
                shutdown_rx
                    .recv_timeout(Duration::from_secs(10))
                    .expect("ロガーが止まらない");
                let text = std::fs::read_to_string(&logger.log_path).unwrap();
                let _ = std::fs::remove_file(&logger.log_path);
                let text: String = text
                    .lines()
                    .map(|l| {
                        if l.starts_with(r#"{"type":"meta","session_start""#) {
                            format!(r#"{{"type":"meta","session_start":{start}}}"#)
                        } else if l.starts_with(r#"{"type":"meta","session_end""#) {
                            format!(r#"{{"type":"meta","session_end":{end}}}"#)
                        } else {
                            l.to_string()
                        }
                    })
                    .collect::<Vec<_>>()
                    .join("\n");
                parse_file(&format!("f{i}"), &text).expect("読める")
            })
            .collect()
    }

    fn run(sc: &Scenario, opts: &ReplayOptions) -> (ProbesReport, Vec<InputFile>) {
        let files = order_inputs(write_and_parse(simulate(sc))).unwrap();
        (replay_probes(&files, opts), files)
    }

    fn jst() -> ReplayOptions {
        ReplayOptions {
            utc_offset_secs: Some(JST),
            day_state: None,
        }
    }

    fn bad(r: &ProbesReport) -> usize {
        r.counts.differ + r.counts.missing + r.counts.extra
    }

    // ---- 往復 ----

    #[test]
    fn round_trip_matches_every_row() {
        let (r, _) = run(&base(), &jst());
        assert_eq!(bad(&r), 0, "{:#?}", r.items);
        assert!(r.counts.matched >= 8, "一致が少なすぎる: {:?}", r.counts);
        assert!(
            r.by_kind.get(&Kind::Random).is_some_and(|c| c.matched >= 3),
            "{:?}",
            r.by_kind
        );
        assert!(
            r.by_kind
                .get(&Kind::DayQuestion)
                .is_some_and(|c| c.matched >= 1),
            "日の問いが一致していない: {:?}",
            r.by_kind
        );
        assert_eq!(
            r.cards.total,
            r.cards.answered
                + r.cards.superseded
                + r.cards.open_at_input_end
                + r.cards.dropped_at_quit
        );
    }

    #[test]
    fn round_trip_holds_for_every_driver_phase() {
        for ph in [0, 370, 999] {
            let mut sc = base();
            sc.sim_phase_ms = ph;
            let (r, _) = run(&sc, &jst());
            assert_eq!(bad(&r), 0, "位相 {ph}: {:#?}", r.items);
        }
    }

    /// v1 から: 押下の届く遅れが 2 秒未満なら一致し、遅れが tick の遅らせ（2 秒）と位相（1 秒）を越えると割れる。
    #[test]
    fn press_delay_beyond_the_tick_lag_breaks_the_match() {
        // 無作為だけにして、候補の直前に押下が 1 回だけある形を作る
        let cfg = ArbiterConfig {
            strata_enabled: false,
            ..ArbiterConfig::default()
        };
        let mut sc = base();
        sc.config = cfg;
        let c = (1..400)
            .map(|seed| {
                (
                    seed,
                    RandomFrame::new(seed, cfg.random, sc.anchor).next_candidate_ms(),
                )
            })
            .find(|&(_, c)| c > sc.anchor + 5 * MIN && c < sc.anchor + 20 * MIN)
            .expect("候補が見つかる");
        sc.seed = c.0;
        let c = c.1;
        // 候補の前は長く打っていない（離席の判定に入る）が、候補の 0.5 秒前に 1 回押す
        sc.presses = vec![sc.anchor + 1_000, c - 500];
        sc.presses
            .extend(burst(c + 10_000, sc.anchor + 40 * MIN, 1_500));
        sc.end = sc.anchor + 40 * MIN;
        sc.press_delay_ms = 1_900;
        let (ok, _) = run(&sc, &jst());
        assert_eq!(bad(&ok), 0, "1.9 秒の遅れは届き切る: {:#?}", ok.items);
        sc.press_delay_ms = 3_500;
        let (broken, _) = run(&sc, &jst());
        assert!(
            broken
                .items
                .iter()
                .any(|i| i.key_ms == c && i.class == Class::Differ),
            "3.5 秒の遅れでは候補 {c} の判定が割れるはず: {:#?}",
            broken.items
        );
    }

    // ---- 壊すと赤 ----

    fn drop_row(files: &mut [InputFile], pred: impl Fn(&Row) -> bool) -> bool {
        for f in files.iter_mut() {
            if let Some(k) = f.rows.iter().position(&pred) {
                f.rows.remove(k);
                return true;
            }
        }
        false
    }

    /// 一時停止・枠の動き出しから離れた判定（境目に入らない）。
    fn far_from_edges(r: &ProbesReport, key: u64) -> bool {
        r.frames.iter().all(|f| key > f.activation_ms.hi + 10_000)
    }

    #[test]
    fn deleting_an_assignment_is_missing() {
        let sc = base();
        let (r0, mut files) = run(&sc, &jst());
        assert_eq!(bad(&r0), 0);
        let target = files
            .iter()
            .flat_map(|f| f.rows.iter())
            .find_map(|r| match r {
                Row::Assigned(a)
                    if a.stratum == Stratum::Random && far_from_edges(&r0, a.scheduled_ts) =>
                {
                    Some(a.scheduled_ts)
                }
                _ => None,
            })
            .expect("無作為の割り当てがある");
        assert!(drop_row(
            &mut files,
            |r| matches!(r, Row::Assigned(a) if a.scheduled_ts == target)
        ));
        let r = replay_probes(&files, &jst());
        assert!(
            r.items
                .iter()
                .any(|i| i.key_ms == target && i.class == Class::Missing),
            "{:#?}",
            r.items
        );
    }

    #[test]
    fn adding_a_suppression_is_extra() {
        let (_, mut files) = run(&base(), &jst());
        let fake = T0 + 77 * MIN + 123;
        files[0].rows.push(Row::Suppressed(SuppressedRow {
            t: fake + 2_000,
            candidate_ts: fake,
            stratum: Stratum::Random,
            reason: SuppressReason::Away,
        }));
        let r = replay_probes(&files, &jst());
        assert!(
            r.items
                .iter()
                .any(|i| i.key_ms == fake && i.class == Class::Extra),
            "{:#?}",
            r.items
        );
    }

    #[test]
    fn a_wrong_seed_breaks_the_random_frame() {
        let (r0, mut files) = run(&base(), &jst());
        for f in files.iter_mut() {
            for row in f.rows.iter_mut() {
                if let Row::Frame(fr) = row {
                    fr.frame_seed += 1;
                }
            }
        }
        let r = replay_probes(&files, &jst());
        let random = |r: &ProbesReport| r.by_kind.get(&Kind::Random).map_or(0, |c| c.matched);
        assert!(random(&r0) >= 3);
        assert!(
            random(&r) <= 1,
            "seed を変えても無作為が一致した: {:?}",
            r.by_kind
        );
    }

    /// 判断 2: 一時停止の行の前 2 秒にかかる不一致は境目、2〜3 秒前は窓の外の近く、4 秒前なら余りのまま。
    ///
    /// ★ 一時停止の直前の候補は、記録でも再生でも判定されずに行が出ない（調停器の時計が 2 秒遅れるため）ことが多く、
    ///   回すだけでは境目の分類に届かない。記録に判定の行を注入して分類を直接確かめる。
    #[test]
    fn pause_boundary_is_counted_apart_from_extra() {
        let mut sc = base();
        let p = T0 + 47 * MIN + 300;
        sc.pauses = vec![(p, true), (p + 2 * MIN, false)];
        let (r0, files0) = run(&sc, &jst());
        assert_eq!(bad(&r0), 0, "{:#?}", r0.items);
        for (before, want) in [
            (1_000, Class::BoundaryPause),
            (2_500, Class::NearPauseOutsideWindow),
            (4_000, Class::Extra),
        ] {
            let mut files = files0.clone();
            let c = p - before;
            files[0].rows.push(Row::Suppressed(SuppressedRow {
                t: c + 2_000,
                candidate_ts: c,
                stratum: Stratum::Random,
                reason: SuppressReason::Away,
            }));
            let r = replay_probes(&files, &jst());
            let item = r
                .items
                .iter()
                .find(|i| i.key_ms == c)
                .unwrap_or_else(|| panic!("注入した行が照合に出ない: {before} ms 前"));
            assert_eq!(item.class, want, "止めた {before} ms 前");
        }
    }

    /// code-reviewer HIGH: 記録から日の問いの行が消えたら欠けになる（位相の境目に隠れない）。
    #[test]
    fn deleting_a_day_question_is_missing() {
        let (r0, mut files) = run(&base(), &jst());
        assert!(r0
            .by_kind
            .get(&Kind::DayQuestion)
            .is_some_and(|c| c.matched >= 1));
        assert!(drop_row(&mut files, |r| matches!(r, Row::Day(_))));
        let r = replay_probes(&files, &jst());
        assert!(
            r.items.iter().any(|i| i.kind == Kind::DayQuestion
                && i.class == Class::Missing
                && i.phase_stable),
            "{:#?}",
            r.items
        );
    }

    /// code-reviewer MEDIUM: 記録に同じ判定の行が 2 行あれば、2 行目は余り。
    #[test]
    fn a_duplicated_row_is_extra() {
        let (_, mut files) = run(&base(), &jst());
        let dup = files[0]
            .rows
            .iter()
            .find(|r| matches!(r, Row::Suppressed(_)))
            .cloned()
            .expect("抑制の行がある");
        let Row::Suppressed(sr) = dup else {
            unreachable!()
        };
        files[0].rows.push(Row::Suppressed(sr));
        let r = replay_probes(&files, &jst());
        assert!(
            r.items
                .iter()
                .any(|i| i.key_ms == sr.candidate_ts && i.class == Class::Extra),
            "{:#?}",
            r.items
        );
        assert!(r.counts.matched >= 1, "1 行目は一致のまま");
    }

    /// /cross-review の code-reviewer MEDIUM: 記録の後ろが落ちた（押下も続かない）なら、取り消しでなく欠け。
    #[test]
    fn a_truncated_tail_without_presses_is_missing() {
        let (_, mut files) = run(&base(), &jst());
        let cut = T0 + 120 * MIN;
        for f in files.iter_mut() {
            f.rows.retain(|r| match r {
                Row::Suppressed(s) => s.candidate_ts < cut,
                Row::Assigned(a) => a.scheduled_ts < cut,
                Row::Label(l) => l.t < cut,
                Row::Day(d) => d.t < cut,
                Row::Key { t } | Row::Focus { t } => *t < cut,
                _ => true,
            });
        }
        let r = replay_probes(&files, &jst());
        assert!(r.counts.missing >= 1, "{:?}", r.counts);
    }

    /// code-reviewer MEDIUM: 枠に判定の行が 1 行も無いなら、取り消し（tail）ではなく欠け。
    #[test]
    fn a_frame_without_any_decision_row_is_missing() {
        let (_, mut files) = run(&base(), &jst());
        for f in files.iter_mut() {
            f.rows
                .retain(|r| !matches!(r, Row::Suppressed(_) | Row::Assigned(_) | Row::Label(_)));
        }
        let r = replay_probes(&files, &jst());
        assert_eq!(r.counts.unverified.tail, 0, "{:?}", r.counts);
        assert!(r.counts.missing >= 3, "{:?}", r.counts);
    }

    /// code-reviewer MEDIUM: 記録だけのウォームアップの抑制は、行の途切れの直後だけ未照合にする。
    #[test]
    fn a_warmup_mismatch_is_unverified_only_after_a_gap() {
        let (_, files0) = run(&base(), &jst());
        // 押下が続いている時刻（途切れの直後でない）に記録だけのウォームアップの抑制
        let busy = T0 + 40 * MIN + 77;
        // 長い途切れ（100〜125 分）の直後
        let after_gap = T0 + 125 * MIN + 5_000;
        for (k, want) in [
            (busy, Class::Extra),
            (after_gap, Class::UnverifiedPowerResume),
        ] {
            let mut files = files0.clone();
            files[0].rows.push(Row::Suppressed(SuppressedRow {
                t: k + 2_000,
                candidate_ts: k,
                stratum: Stratum::Random,
                reason: SuppressReason::Warmup,
            }));
            let r = replay_probes(&files, &jst());
            let item = r
                .items
                .iter()
                .find(|i| i.key_ms == k)
                .expect("注入した行が照合に出る");
            assert_eq!(item.class, want, "{k}");
        }
    }

    /// code-reviewer MEDIUM: 枠の起点より前の押下（ファイルの始まりから同意までの間）を調停器に渡さない。
    #[test]
    fn presses_before_the_anchor_are_not_fed() {
        let cfg = ArbiterConfig {
            strata_enabled: false,
            ..ArbiterConfig::default()
        };
        let mut sc = base();
        sc.config = cfg;
        // 最初の候補がウォームアップの後・離席の判定の幅（180 秒）の中に落ちる seed
        let (seed, c) = (1..2_000)
            .map(|seed| {
                (
                    seed,
                    RandomFrame::new(seed, cfg.random, sc.anchor).next_candidate_ms(),
                )
            })
            .find(|&(_, c)| c > sc.anchor + 40_000 && c < sc.anchor + 150_000)
            .expect("候補が見つかる");
        sc.seed = seed;
        // 起点の後は候補より後から打つ（駆動役から見ると候補の時点で押下が無い）
        sc.presses = burst(c + 10_000, sc.anchor + 40 * MIN, 1_500);
        sc.end = sc.anchor + 40 * MIN;
        let (r0, mut files) = run(&sc, &jst());
        assert_eq!(bad(&r0), 0, "{:#?}", r0.items);
        // ファイルの始まりを 2 分前にずらし、起点の直前に押下の行を足す（同意の前の打鍵）
        let pre: Vec<Row> = (1..=20)
            .map(|k| Row::Key {
                t: sc.anchor - k * 1_000,
            })
            .collect();
        for r in files[0].rows.iter_mut() {
            if let Row::MetaStart { t } = r {
                *t = sc.anchor - 120_000;
            }
        }
        let at = files[0]
            .rows
            .iter()
            .position(|r| matches!(r, Row::Frame(_)))
            .unwrap();
        for (k, r) in pre.into_iter().rev().enumerate() {
            files[0].rows.insert(at + k, r);
        }
        let r = replay_probes(&files, &jst());
        assert!(
            !r.items.iter().any(|i| i.key_ms == c),
            "起点の前の押下が候補 {c} の判定に入った: {:#?}",
            r.items
        );
    }

    /// security-checker MEDIUM: 壊れた時刻の行・長すぎる入力は拒む（再生を止まらなくしない）。
    #[test]
    fn broken_times_and_too_long_inputs_are_refused() {
        let text = "{\"type\":\"meta\",\"session_start\":1000}\n{\"type\":\"key\",\"t\":1000000000000000,\"category\":\"a\",\"press\":true}\n";
        let f = parse_file("x", text).unwrap();
        assert!(order_inputs(vec![f]).is_err());
        let start = |t: u64| {
            parse_file(
                &format!("f{t}"),
                &format!("{{\"type\":\"meta\",\"session_start\":{t}}}\n"),
            )
            .unwrap()
        };
        assert!(order_inputs(vec![start(T0), start(T0 + 39 * 86_400_000)]).is_ok());
        assert!(order_inputs(vec![start(T0), start(T0 + 41 * 86_400_000)]).is_err());
        // 知らない skip_reason も拒む
        let bad_skip = "{\"type\":\"realtime_label\",\"probe_id\":\"A\",\"answered\":false,\"skip_reason\":\"<x>\",\"ts\":5}\n";
        assert!(parse_file("x", bad_skip).is_err());
    }

    // ---- 個別 ----

    /// 再生が自分で発火させたカードは、その tick の後から開いている（見積もりの「候補 + 3 秒」を待たない）。
    #[test]
    fn a_card_fired_by_the_replay_is_open_from_its_fire_tick() {
        let c = T0 + 10 * MIN;
        let tl = Timeline {
            spans: vec![probe_span(c, c + 20_000, Stratum::Random, c, false)],
            ..Timeline::default()
        };
        let none = HashMap::new();
        // 見積もりだけなら c + 3 秒までは閉じている
        assert_eq!(open_card_at(&tl, &[0], &none, c + 2_500), None);
        assert_eq!(
            open_card_at(&tl, &[0], &none, c + 3_500),
            Some(OpenCard::Random)
        );
        // c + 2.2 秒の tick で発火させたなら、次の tick から開いている
        let fired: HashMap<(u8, u64), u64> = [((code(Stratum::Random), c), c + 2_200)].into();
        assert_eq!(
            open_card_at(&tl, &[0], &fired, c + 2_200),
            None,
            "発火の tick の前は閉じている"
        );
        assert_eq!(
            open_card_at(&tl, &[0], &fired, c + 2_500),
            Some(OpenCard::Random)
        );
        // 閉じた時刻の後は閉じている
        assert_eq!(open_card_at(&tl, &[0], &fired, c + 20_001), None);
    }

    #[test]
    fn debug_cards_are_counted_apart() {
        let mut sc = base();
        sc.debug_probe_at = Some(T0 + 33 * MIN + 400);
        let (r, _) = run(&sc, &jst());
        assert!(r.counts.debug_check >= 1, "{:?}", r.counts);
        assert_eq!(bad(&r), 0, "確かめ用のカードが余りになった: {:#?}", r.items);
        assert_eq!(r.cards.debug, 1);
    }

    #[test]
    fn a_card_open_across_rotation_is_joined_by_probe_id() {
        let (r0, files0) = run(&base(), &jst());
        assert_eq!(bad(&r0), 0);
        // 最初の割り当ての 3 秒後にローテートし、回答は新しいファイルに入る
        let first = files0
            .iter()
            .flat_map(|f| f.rows.iter())
            .find_map(|r| match r {
                Row::Assigned(a) if a.scheduled_ts > T0 + 2 * MIN => Some(a.scheduled_ts),
                _ => None,
            })
            .unwrap();
        let mut sc = base();
        // 発火の tick は候補の 2〜3 秒後。回答は 6 秒後なので、発火の 3.5 秒後にローテートすれば間に入る
        sc.rotations = vec![(first + 2_000 + 3_500, 99)];
        let (r, files) = run(&sc, &jst());
        assert_eq!(files.len(), 2);
        assert_eq!(r.cards.carried_across_rotation, 1, "{:?}", r.cards);
        assert_eq!(bad(&r), 0, "{:#?}", r.items);
        assert_eq!(r.frames.len(), 2);
        assert!(!r.frames[1].app_start, "ローテートを走行の始まりとみなした");
    }

    #[test]
    fn a_card_dropped_by_pause_is_classified() {
        let (_, files0) = run(&base(), &jst());
        let first = files0
            .iter()
            .flat_map(|f| f.rows.iter())
            .find_map(|r| match r {
                Row::Assigned(a) if a.scheduled_ts > T0 + 2 * MIN => Some(a.scheduled_ts),
                _ => None,
            })
            .unwrap();
        let mut sc = base();
        sc.pauses = vec![(first + 4_000, true), (first + 4 * MIN, false)];
        let (r, _) = run(&sc, &jst());
        assert_eq!(r.cards.dropped_by_pause, 1, "{:?}", r.cards);
        assert_eq!(bad(&r), 0, "{:#?}", r.items);
    }

    #[test]
    fn rows_after_revocation_are_tail_not_missing() {
        // 取り消しの後も O1 の記録（押下）は続く
        let mut sc = base();
        sc.presses
            .extend(burst(T0 + 170 * MIN, T0 + 180 * MIN, 1_700));
        let (_, mut files) = run(&sc, &jst());
        // 120 分より後の判定の行を消す（同意の取り消しで枠が止まったのと同じ見え方）
        let cut = T0 + 120 * MIN;
        for f in files.iter_mut() {
            f.rows.retain(|r| match r {
                Row::Suppressed(s) => s.candidate_ts < cut,
                Row::Assigned(a) => a.scheduled_ts < cut,
                Row::Label(l) => l.t < cut,
                Row::Day(d) => d.t < cut,
                _ => true,
            });
        }
        let r = replay_probes(&files, &jst());
        assert!(r.counts.unverified.tail >= 1, "{:?}", r.counts);
        assert_eq!(r.counts.missing, 0, "{:#?}", r.items);
    }

    #[test]
    fn a_sleep_is_inferred_from_overdue_suppressions() {
        let mut sc = base();
        // 50〜58 分は tick が無い（スリープ）。押下もその間は無い
        sc.sleeps = vec![(T0 + 50 * MIN, T0 + 58 * MIN)];
        sc.presses.retain(|&t| !in_range(t, &sc.sleeps));
        let (r, _) = run(&sc, &jst());
        // ★ 8 分のスリープの間に落ちた候補は、復帰の tick で溜めて判定される（抑制の t − 候補 ≥ 30 秒）。
        //   再生はそれを手がかりに復帰を推定し、復帰の後のウォームアップを合わせる。
        assert_eq!(bad(&r), 0, "{:#?}", r.items);
        assert!(
            r.power_resumes_inferred
                .iter()
                .any(|&t| (T0 + 58 * MIN..T0 + 59 * MIN).contains(&t)),
            "復帰を推定していない（検査が空回り）: {:?}",
            r.power_resumes_inferred
        );
    }

    #[test]
    fn without_an_offset_day_questions_are_unverified() {
        let (r, _) = run(&base(), &ReplayOptions::default());
        // ★ 時差 0 で回すと日の問いは時間帯の外になり出ない。記録の日の問いは不一致でなく未照合に入る
        let day = r
            .by_kind
            .get(&Kind::DayQuestion)
            .expect("記録に日の問いがある");
        assert!(day.unverified.offset_unknown >= 1, "{day:?}");
        assert_eq!(day.differ + day.missing + day.extra, 0, "{day:?}");
        // 無作為は時差に依らない（no_ask は既定で無効）
        assert_eq!(
            r.by_kind
                .get(&Kind::Random)
                .map_or(0, |c| c.differ + c.missing + c.extra),
            0
        );
    }

    #[test]
    fn frame_rows_restore_the_config() {
        let cfg = ArbiterConfig::default();
        let line = crate::logger::format_probe_frame_line(1_000, 7, 1_000, &cfg);
        let Some(Row::Frame(fr)) = parse_line(&line).unwrap() else {
            panic!("枠の行として読めない: {line}");
        };
        assert_eq!(format!("{:?}", fr.config), format!("{cfg:?}"));
        assert_eq!(
            fr.config.random.lambda_per_ms.to_bits(),
            cfg.random.lambda_per_ms.to_bits()
        );
        let bad_version = line.replace(ARBITER_VERSION, "s1-arbiter-0");
        assert!(parse_line(&bad_version).is_err());
    }

    #[test]
    fn unreadable_lines_are_counted_and_broken_fields_stop() {
        let text = "{\"type\":\"meta\",\"session_start\":1}\n{\"type\":\"key\",\"t\":5,\"categ\n";
        let f = parse_file("x", text).unwrap();
        assert_eq!(f.skipped_lines, 1);
        let broken = "{\"type\":\"probe_suppressed\",\"t\":\"x\",\"candidate_ts\":1,\"stratum\":\"random\",\"reason\":\"away\"}\n";
        assert!(parse_file("x", broken).unwrap_err().starts_with("x:1:"));
    }

    #[test]
    fn overlapping_inputs_are_refused() {
        let a = parse_file("a", "{\"type\":\"meta\",\"session_start\":1000}\n{\"type\":\"key\",\"t\":5000,\"category\":\"a\",\"press\":true}\n").unwrap();
        let b = parse_file("b", "{\"type\":\"meta\",\"session_start\":3000}\n").unwrap();
        assert!(order_inputs(vec![b, a]).is_err());
    }

    #[test]
    fn cards_split_superseded_from_the_persons_skips() {
        let text = [
            r#"{"type":"meta","session_start":1000}"#,
            r#"{"type":"probe_assignment","probe_id":"A","scheduled_ts":2000,"session_elapsed_ms":1000,"stratum":"low_operation_end"}"#,
            r#"{"type":"realtime_label","probe_id":"A","source":"random_probe","q1_friction":null,"q2_progress":null,"answered":false,"skip_reason":"superseded","latency_ms":0,"analysis_window_start_ms":0,"analysis_window_end_ms":1,"ts":3000}"#,
            r#"{"type":"probe_assignment","probe_id":"B","scheduled_ts":3000,"session_elapsed_ms":2000,"stratum":"random"}"#,
            r#"{"type":"realtime_label","probe_id":"B","source":"random_probe","q1_friction":null,"q2_progress":null,"answered":false,"skip_reason":"dismissed","latency_ms":9,"analysis_window_start_ms":0,"analysis_window_end_ms":1,"ts":4000}"#,
            r#"{"type":"probe_assignment","probe_id":"C","scheduled_ts":5000,"session_elapsed_ms":4000,"stratum":"random"}"#,
            r#"{"type":"realtime_label","probe_id":"C","source":"random_probe","q1_friction":3,"q2_progress":3,"answered":true,"skip_reason":"none","latency_ms":9,"analysis_window_start_ms":0,"analysis_window_end_ms":1,"ts":6000}"#,
            r#"{"type":"meta","session_end":7000}"#,
        ]
        .join("\n");
        let files = vec![parse_file("x", &text).unwrap()];
        let c = cards(&files);
        assert_eq!((c.total, c.answered, c.superseded), (3, 1, 1));
        assert_eq!(c.skipped_by_person.get("dismissed"), Some(&1));
        // 分母は差し替えを外した 2
        assert_eq!(c.response_rate_excl_superseded, Some(0.5));
    }

    /// /cross-review の Codex P2・code-reviewer: 同じカードの 2 行目のラベルは数えない・ローテートの後の一時停止で下ろしたカード。
    #[test]
    fn cards_count_each_card_once_and_follow_rotation() {
        let f1 = [
            r#"{"type":"meta","session_start":1000}"#,
            r#"{"type":"probe_assignment","probe_id":"A","scheduled_ts":2000,"session_elapsed_ms":1000,"stratum":"random"}"#,
            r#"{"type":"realtime_label","probe_id":"A","source":"random_probe","q1_friction":3,"q2_progress":3,"answered":true,"skip_reason":"none","latency_ms":9,"analysis_window_start_ms":0,"analysis_window_end_ms":1,"ts":3000}"#,
            r#"{"type":"realtime_label","probe_id":"A","source":"random_probe","q1_friction":3,"q2_progress":3,"answered":true,"skip_reason":"none","latency_ms":9,"analysis_window_start_ms":0,"analysis_window_end_ms":1,"ts":3500}"#,
            r#"{"type":"probe_assignment","probe_id":"B","scheduled_ts":5000,"session_elapsed_ms":4000,"stratum":"random"}"#,
            r#"{"type":"meta","session_end":6000}"#,
        ]
        .join("\n");
        // ローテート（すぐ次のファイル）で、回答の前に一時停止
        let f2 = [
            r#"{"type":"meta","session_start":6100}"#,
            r#"{"type":"recording_pause","t":7000,"paused":true}"#,
            r#"{"type":"meta","session_end":9000}"#,
        ]
        .join("\n");
        let files = vec![parse_file("a", &f1).unwrap(), parse_file("b", &f2).unwrap()];
        let c = cards(&files);
        assert_eq!((c.total, c.answered, c.duplicate_labels), (2, 1, 1));
        assert_eq!(c.dropped_by_pause, 1, "{c:?}");
        assert_eq!(c.response_rate_excl_superseded, Some(1.0));
    }

    /// /cross-review の Codex P1・security-checker: 時刻の欄を全部縛る（桁あふれ）・何日も止めた記録は拒まない。
    #[test]
    fn every_time_field_is_bounded_but_long_pauses_are_accepted() {
        let overflow = format!(
            "{{\"type\":\"meta\",\"session_start\":{T0}}}\n{{\"type\":\"probe_assignment\",\"probe_id\":\"A\",\"scheduled_ts\":{},\"session_elapsed_ms\":0,\"stratum\":\"random\"}}\n",
            u64::MAX
        );
        assert!(order_inputs(vec![parse_file("x", &overflow).unwrap()]).is_err());
        // 5 日止めてから再開した 1 本のファイル（一時停止の間はローテートが回らない）
        let long = format!(
            "{{\"type\":\"meta\",\"session_start\":{T0}}}\n{{\"type\":\"recording_pause\",\"t\":{},\"paused\":true}}\n{{\"type\":\"recording_pause\",\"t\":{},\"paused\":false}}\n",
            T0 + MIN,
            T0 + 5 * 86_400_000
        );
        assert!(order_inputs(vec![parse_file("x", &long).unwrap()]).is_ok());
    }

    /// /cross-review の security-checker・code-reviewer MEDIUM: 枠の前（同意の前）の一時停止と再開を、枠の最初の
    /// tick の再開として扱わない（飛ばした区間の縁を、調停器の無い tick で進める）。
    #[test]
    fn a_pause_before_the_frame_is_not_a_resume_of_the_frame() {
        let (r0, mut files) = run(&base(), &jst());
        assert_eq!(bad(&r0), 0);
        // ファイルの始まりを 10 分前にし、同意の前に止めて再開した行を足す
        for r in files[0].rows.iter_mut() {
            if let Row::MetaStart { t } = r {
                *t = T0 - 10 * MIN;
            }
        }
        let at = files[0]
            .rows
            .iter()
            .position(|r| matches!(r, Row::Frame(_)))
            .unwrap();
        files[0].rows.insert(
            at,
            Row::Pause {
                t: T0 - 4 * MIN,
                paused: false,
            },
        );
        files[0].rows.insert(
            at,
            Row::Pause {
                t: T0 - 6 * MIN,
                paused: true,
            },
        );
        let r = replay_probes(&files, &jst());
        assert_eq!(bad(&r), 0, "{:#?}", r.items);
    }

    // ---- --day-questions ----

    #[test]
    fn day_question_presses_stop_at_the_local_4am() {
        // JST 2026-11-07 20:00 に答え、21:00 と翌 03:30 と 04:30 に押す
        let t = T0 + 2 * 60 * MIN;
        let text = [
            format!(r#"{{"type":"meta","session_start":{}}}"#, T0),
            format!(r#"{{"type":"day_question","t":{t},"shown_ts":{},"in_eod_window":true,"target_day":20764,"trigger":"evening_idle","delayed":false,"answered":true,"closed_by":"answer","items_version":"dq-draft-1","motivation":4,"latency_ms":1,"duration_ms":1}}"#, t - 5_000),
            format!(r#"{{"type":"key","t":{},"category":"a","press":true}}"#, t + 60 * MIN),
            format!(r#"{{"type":"key","t":{},"category":"a","press":true}}"#, t + 7 * 60 * MIN + 30 * MIN),
            format!(r#"{{"type":"key","t":{},"category":"a","press":true}}"#, t + 8 * 60 * MIN + 30 * MIN),
        ]
        .join("\n");
        let files = vec![parse_file("x", &text).unwrap()];
        let jst = day_question_presses(&files, JST);
        assert_eq!(jst.len(), 1);
        assert_eq!(jst[0].presses_until_cutoff, 2, "JST では 04:00 で切れる");
        assert!(jst[0].input_covers_cutoff);
        // UTC では同じ瞬間が 11:00 で、切れ目は翌 04:00 UTC（JST 13:00）まで延びる
        let utc = day_question_presses(&files, 0);
        assert_eq!(utc[0].presses_until_cutoff, 3);
        assert!(!utc[0].input_covers_cutoff);
    }

    /// /cross-review の Codex P2: 回答の日のファイルが途中で切れ、翌日の別の走行があっても「切れ目まで続いた」としない。
    #[test]
    fn coverage_requires_an_unbroken_chain_to_the_cutoff() {
        let t = T0 + 2 * 60 * MIN;
        let day_row = format!(
            r#"{{"type":"day_question","t":{t},"shown_ts":{},"in_eod_window":true,"target_day":20764,"trigger":"evening_idle","delayed":false,"answered":true,"closed_by":"answer","items_version":"dq-draft-1","motivation":4,"latency_ms":1,"duration_ms":1}}"#,
            t - 5_000
        );
        let a = format!("{{\"type\":\"meta\",\"session_start\":{T0}}}\n{day_row}\n{{\"type\":\"meta\",\"session_end\":{}}}\n", t + MIN);
        // 翌日の昼の別の走行（切れ目の後まで続くが、間が空いている）
        let b = format!("{{\"type\":\"meta\",\"session_start\":{}}}\n{{\"type\":\"meta\",\"session_end\":{}}}\n", t + 12 * 60 * MIN, t + 14 * 60 * MIN);
        let files = order_inputs(vec![
            parse_file("a", &a).unwrap(),
            parse_file("b", &b).unwrap(),
        ])
        .unwrap();
        let rows = day_question_presses(&files, JST);
        assert!(
            !rows[0].input_covers_cutoff,
            "間の空いた走行を連続とみなした"
        );
        // ローテートで続いていれば連続
        let c = format!("{{\"type\":\"meta\",\"session_start\":{}}}\n{{\"type\":\"meta\",\"session_end\":{}}}\n", t + MIN + 100, t + 14 * 60 * MIN);
        let files = order_inputs(vec![
            parse_file("a", &a).unwrap(),
            parse_file("c", &c).unwrap(),
        ])
        .unwrap();
        assert!(day_question_presses(&files, JST)[0].input_covers_cutoff);
    }
}
