//! 手跡の机上の道具（PR 4・ADR-051 D3）の純粋な部分。
//!
//! 記録の行から、30 秒の窓ごとに「許した情報の特徴（A）」「描き直した状態の特徴（B_state）」
//! 「当てる対象（T1・T2）」を作り、画素を描くためのコマを出す。統計は `experiments/` が行う。
//! 設計は `.steering/20261115-handmark-desk-tool/design.md`（v2）。
//!
//! ## 規則（テストで縛る）
//!
//! - 日は `eh3::local_day`（4:00 区切り）。オフセットは 1 つに固定する。
//! - 区間（状態を作り直す単位）: セッションと日の重なりを 1 片とし、その日の `handmark_day.stage_starts`
//!   のうち片の中にある時刻でさらに切る。区間の `t0` は片の始まりか stage の始まり。
//! - 種は全部の日で `assignment::draw_seed(表の SHA-256, 日)`（ライブと同じ式）。記録の `draw_seed` と
//!   違う日は使わず、日を報告する。
//! - 窓: UTC の 30 秒の格子にそろえ、区間の中に収まり、`t0 + 30 s` 以降に始まるものだけ。
//!   除く: (a) 一時停止に重なる (b) `feat` の行が 25 本未満 (c) 離席の候補。数えて報告する。
//! - T1 = 窓の `p_stuck` の平均 ≥ 0.60（`invitation::TRIGGER_P_STUCK`）。副に「全部の刻みで ≥ 0.60」。
//!   T2 = 窓の (`p_flow`, `p_inc`, `p_stuck`) の平均の最大（同点は後の方）。判断 3。
//! - 状態は `state::replay_live` の意味（`τ − LIVE_LAG_MS` まで進める）、場は `trace_replay::Synth` を
//!   `TraceField::step` に入れる（`replay_trace` と同じ）。区間ごとに 1 回だけ流す。
//! - 状態を特徴とコマにする前に、呼び出し側の変換を 1 回だけ通す（机上の対照のため。ここには中身を持たない）。
//!
//! ⚠️ OS API・ファイル IO を持たない（行の文字列を受け取る）。打鍵の本文は読まない（`key` 行は時刻と押下かだけ）。

use std::collections::BTreeMap;

use serde::Serialize;
use serde_json::Value;

use super::assignment::draw_seed;
use super::state::{Stage, StageState, LIVE_LAG_MS};
use super::trace::{Step, TraceField, CELLS};
use super::trace_replay::{Synth, REP_PT};
use crate::analysis::intervention::AWAY_IDLE_MS;
use crate::analysis::invitation::TRIGGER_P_STUCK;
use crate::analysis::pointer_bin::PointerBin;
use crate::eh3::{local_day, DAY_CUTOFF_HOUR};

/// 本モジュールの誤り（`s1_replay` と同じく文字列）。
pub type Result<T> = std::result::Result<T, String>;

/// 道具の版（表のヘッダに書く）。窓・特徴・対象の規則を変えたら上げる。
/// hm-desk-2（2026-11-16）: 感度分析の日（conditions.md C7）の印 `sens` と要約を足した。主の窓・特徴・対象は変えていない。
pub const DESK_VERSION: &str = "hm-desk-2";
/// 窓の長さ（ADR-051 D3）。
pub const WINDOW_MS: u64 = 30_000;
/// 区間の始まりから捨てる長さ（状態が 0 から立ち上がる間）。
pub const WARMUP_MS: u64 = 30_000;
/// 窓に要る `feat` の行の数（1 Hz で 30 本のうち）。
pub const MIN_FEATS: usize = 25;
/// T1 の閾値（招待の契機と同じ値）。
pub const T1_P_STUCK: f64 = TRIGGER_P_STUCK;
/// 画面の波紋が消えるまで（`HandmarkStage.tsx` の 1.6 秒）。
pub const RIPPLE_LIFE_MS: u64 = 1_600;
/// 動きを測る 2 枚目のずれ（画面の状態の寄せの幅）。
pub const PAIR_GAP_MS: u64 = 250;
/// 窓あたりの標本の数（既定）。30_000 を割り切る数だけを受ける。
pub const DEFAULT_SAMPLES: usize = 10;

const DAY_MS: i64 = 86_400_000;
/// 時刻として受ける範囲（2020-01-01 〜 2100-01-01・壊れた時刻で窓の列を際限なく作らない）。
pub const MIN_EPOCH_MS: u64 = 1_577_836_800_000;
pub const MAX_EPOCH_MS: u64 = 4_102_444_800_000;
/// 1 本の記録の幅の上限（一時停止の間はローテートしないので数日になりうる・`s1_replay` と同じ 40 日）。
pub const MAX_FILE_SPAN_MS: u64 = 40 * 86_400_000;
/// 画面の波紋の枠の数（`handmarkStageTrace.ts` の `RIPPLE_SLOTS`）。7 つ目は最も古い枠を上書きする。
pub const RIPPLE_SLOTS: usize = 6;

/// A の特徴の名前（表の列の順）。
pub const A_NAMES: [&str; 22] = [
    "n_press_10",
    "log_n_press_10",
    "n_press_30",
    "log_n_press_30",
    "n_press_60",
    "log_n_press_60",
    "iki_median_30",
    "iki_cv_30",
    "iki_p90_30",
    "max_gap_60",
    "since_last_press",
    "log_since_last_press",
    "pauses_2s_30",
    "bursts_30",
    "burst_len_30",
    "move_sum_10",
    "log_move_sum_10",
    "move_sum_30",
    "log_move_sum_30",
    "moved_secs_30",
    "buttons_30",
    "wheel_30",
];

/// B_state の特徴の名前（表の列の順）。
pub const B_STATE_NAMES: [&str; 13] = [
    "speed_mean",
    "speed_max",
    "speed_last",
    "speed_sd",
    "irreg_mean",
    "irreg_max",
    "irreg_last",
    "phase_delta",
    "bend_mean",
    "bend_max",
    "pull_mean",
    "field_nonzero",
    "ripples",
];

/// `feat` の行の確率（flow・inc・stuck の順）。
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Feat {
    pub t: u64,
    pub p: [f64; 3],
}

/// `handmark_day` の行のうち、道具が使う項目。
#[derive(Debug, Clone, PartialEq, Default)]
pub struct HmDay {
    /// 行を書いた時刻（同じ日の行は最後のものを採る）。
    pub t: u64,
    pub draw_seed: Option<u64>,
    pub stage_starts: Vec<u64>,
    /// 行に書かれた表の SHA-256（渡した表と違えば止める）。
    pub table_sha256: Option<String>,
    /// `stage_starts` が上限を超えて切れた日（区間を正しく切れないので使わない）。
    pub overflow: bool,
    /// 割付（`late_first`・`on` など）。古い行・前期の行には無い。
    pub assigned: Option<String>,
    /// その日に出ていた時間（ms・日の累計）。
    pub shown_ms: Option<u64>,
    /// 帯が見えていた時間（ms・日の累計）。記録が無ければ `None`。
    pub visible_ms: Option<u64>,
    /// 切った（`false`）／戻した（`true`）時刻。
    pub toggles: Vec<(u64, bool)>,
}

/// 1 本の記録から読んだもの。
#[derive(Debug, Clone, Default)]
pub struct DeskFile {
    pub name: String,
    pub session_start: u64,
    /// 記録の終わり（`meta.session_end` か、時刻を持つ行の最大）。
    pub end: u64,
    pub hmm_version: Option<String>,
    /// `key` 行で `press = true` の時刻（昇順）。
    pub presses: Vec<u64>,
    pub bins: Vec<PointerBin>,
    pub feats: Vec<Feat>,
    /// 一時停止の区間 `[from, to)`。
    pub pauses: Vec<(u64, u64)>,
    pub hm_days: BTreeMap<i64, HmDay>,
    /// `handmark_day` の全部の行に書かれた表の SHA-256（同じ日の古い行も含む。畳む前に照らすため）。
    pub table_shas: Vec<String>,
}

fn u64_of(v: &Value, key: &str) -> Result<u64> {
    v.get(key)
        .and_then(Value::as_u64)
        .ok_or_else(|| format!("{key} が無いか u64 でない"))
}

fn prob_of(v: &Value, key: &str) -> Result<f64> {
    v.get(key)
        .and_then(Value::as_f64)
        .filter(|x| (0.0..=1.0).contains(x))
        .ok_or_else(|| format!("{key} が無いか 0〜1 の数でない"))
}

fn u8_of(v: &Value, key: &str) -> Result<u8> {
    let x = u64_of(v, key)?;
    u8::try_from(x).map_err(|_| format!("{key} が u8 の範囲の外"))
}

/// 1 本の記録を読む。JSON として読めない行・使う行種の欄が壊れた行・範囲の外の時刻は、行番号つきの誤りで
/// 止める（fail-closed。同じファイルを読む `run_replay` も読めない行で止まるので、規則をそろえる）。
pub fn parse_file(name: &str, text: &str) -> Result<DeskFile> {
    let mut f = DeskFile {
        name: name.to_string(),
        ..DeskFile::default()
    };
    let mut start: Option<u64> = None;
    let mut session_end: Option<u64> = None;
    let mut max_t: u64 = 0;
    let mut pause_marks: Vec<(u64, bool)> = Vec::new();
    for (i, line) in text.lines().enumerate() {
        if line.trim().is_empty() {
            continue;
        }
        let at = |e: String| format!("{name}:{}: {e}", i + 1);
        let v = serde_json::from_str::<Value>(line)
            .map_err(|_| at("JSON として読めない".to_string()))?;
        let ty = v.get("type").and_then(Value::as_str);
        // 終わりの時刻は、この道具が使う行種の時刻だけで取る（知らない行種の壊れた時刻に引きずられない）
        if matches!(
            ty,
            Some("key" | "pointer_bin" | "feat" | "recording_pause" | "handmark_day")
        ) {
            let t = u64_of(&v, "t").map_err(at)?;
            if !(MIN_EPOCH_MS..=MAX_EPOCH_MS).contains(&t) {
                return Err(at(format!("時刻 {t} が範囲の外")));
            }
            max_t = max_t.max(t);
        }
        match ty {
            Some("meta") => {
                for k in ["session_start", "session_end"] {
                    match v.get(k) {
                        None | Some(Value::Null) => {}
                        Some(x) => {
                            let t = x.as_u64().ok_or_else(|| at(format!("{k} が u64 でない")))?;
                            if !(MIN_EPOCH_MS..=MAX_EPOCH_MS).contains(&t) {
                                return Err(at(format!("{k} {t} が範囲の外")));
                            }
                        }
                    }
                }
                if let Some(t) = v.get("session_start").and_then(Value::as_u64) {
                    start = Some(start.map_or(t, |s: u64| s.min(t)));
                    max_t = max_t.max(t);
                }
                if let Some(t) = v.get("session_end").and_then(Value::as_u64) {
                    session_end = Some(t);
                }
                if let Some(h) = v.get("hmm_version").and_then(Value::as_str) {
                    f.hmm_version = Some(h.to_string());
                }
            }
            Some("key") => {
                let t = u64_of(&v, "t").map_err(at)?;
                let press = v
                    .get("press")
                    .and_then(Value::as_bool)
                    .ok_or_else(|| at("press が無いか真偽でない".to_string()))?;
                if press {
                    f.presses.push(t);
                }
            }
            Some("pointer_bin") => {
                f.bins.push(PointerBin {
                    timestamp: u64_of(&v, "t").map_err(at)?,
                    moved: u8_of(&v, "moved").map_err(at)?,
                    buttons: u8_of(&v, "buttons").map_err(at)?,
                    wheel: u8_of(&v, "wheel").map_err(at)?,
                });
            }
            Some("feat") => {
                f.feats.push(Feat {
                    t: u64_of(&v, "t").map_err(at)?,
                    p: [
                        prob_of(&v, "p_flow").map_err(at)?,
                        prob_of(&v, "p_inc").map_err(at)?,
                        prob_of(&v, "p_stuck").map_err(at)?,
                    ],
                });
            }
            Some("recording_pause") => {
                let t = u64_of(&v, "t").map_err(at)?;
                let paused = v
                    .get("paused")
                    .and_then(Value::as_bool)
                    .ok_or_else(|| at("paused が無いか真偽でない".to_string()))?;
                pause_marks.push((t, paused));
            }
            Some("handmark_day") => {
                let t = u64_of(&v, "t").map_err(at)?;
                let day = v
                    .get("day")
                    .and_then(Value::as_i64)
                    .ok_or_else(|| at("day が無いか整数でない".to_string()))?;
                let seed = match v.get("draw_seed") {
                    None | Some(Value::Null) => None,
                    Some(Value::String(s)) => Some(
                        u64::from_str_radix(s, 16)
                            .map_err(|_| at("draw_seed が 16 進でない".to_string()))?,
                    ),
                    Some(_) => return Err(at("draw_seed が文字列でない".to_string())),
                };
                let mut starts = Vec::new();
                if let Some(a) = v.get("stage_starts") {
                    let a = a
                        .as_array()
                        .ok_or_else(|| at("stage_starts が配列でない".to_string()))?;
                    for x in a {
                        starts.push(
                            x.as_u64().ok_or_else(|| {
                                at("stage_starts の要素が u64 でない".to_string())
                            })?,
                        );
                    }
                }
                starts.sort_unstable();
                starts.dedup();
                let table_sha256 = match v.get("table_sha256") {
                    None | Some(Value::Null) => None,
                    Some(Value::String(s)) => Some(s.to_ascii_lowercase()),
                    Some(_) => return Err(at("table_sha256 が文字列でない".to_string())),
                };
                let overflow = match v.get("overflow") {
                    None | Some(Value::Null) => false,
                    Some(Value::Bool(b)) => *b,
                    Some(_) => return Err(at("overflow が真偽でない".to_string())),
                };
                let assigned = match v.get("assigned") {
                    None | Some(Value::Null) => None,
                    Some(Value::String(s)) => Some(s.clone()),
                    Some(_) => return Err(at("assigned が文字列でない".to_string())),
                };
                let opt_u64 = |key: &str| -> Result<Option<u64>> {
                    match v.get(key) {
                        None | Some(Value::Null) => Ok(None),
                        Some(x) => x
                            .as_u64()
                            .map(Some)
                            .ok_or_else(|| at(format!("{key} が u64 でない"))),
                    }
                };
                let shown_ms = opt_u64("shown_ms")?;
                let visible_ms = opt_u64("visible_ms")?;
                let mut toggles = Vec::new();
                if let Some(a) = v.get("toggles") {
                    let a = a
                        .as_array()
                        .ok_or_else(|| at("toggles が配列でない".to_string()))?;
                    for x in a {
                        let t = x.get("t").and_then(Value::as_u64);
                        let on = x.get("on").and_then(Value::as_bool);
                        match (t, on) {
                            (Some(t), Some(on)) => toggles.push((t, on)),
                            _ => return Err(at("toggles の要素が {t, on} でない".to_string())),
                        }
                    }
                }
                if let Some(sh) = &table_sha256 {
                    if !f.table_shas.contains(sh) {
                        f.table_shas.push(sh.clone());
                    }
                }
                let row = HmDay {
                    t,
                    draw_seed: seed,
                    stage_starts: starts,
                    table_sha256,
                    overflow,
                    assigned,
                    shown_ms,
                    visible_ms,
                    toggles,
                };
                match f.hm_days.get(&day) {
                    Some(prev) if prev.t > t => {}
                    _ => {
                        f.hm_days.insert(day, row);
                    }
                }
            }
            _ => {}
        }
    }
    f.session_start = start.ok_or_else(|| format!("{name}: meta.session_start が無い"))?;
    f.end = session_end.unwrap_or(max_t).max(f.session_start);
    if f.end - f.session_start > MAX_FILE_SPAN_MS {
        return Err(format!(
            "{name}: 記録の幅が {} 日を超える",
            MAX_FILE_SPAN_MS / 86_400_000
        ));
    }
    f.presses.sort_unstable();
    f.bins.sort_by_key(|b| b.timestamp);
    f.feats.sort_by_key(|x| x.t);
    pause_marks.sort_by_key(|m| m.0);
    let mut open: Option<u64> = None;
    for (t, paused) in pause_marks {
        match (open, paused) {
            (None, true) => open = Some(t),
            (Some(a), false) => {
                f.pauses.push((a, t));
                open = None;
            }
            _ => {}
        }
    }
    if let Some(a) = open {
        f.pauses.push((a, f.end.max(a)));
    }
    Ok(f)
}

/// 日 `day` の始まり（UTC の ms）。`local_day(day_start(d)) == d`。
pub fn day_start_ms(day: i64, utc_offset_secs: i32) -> u64 {
    let secs = day * (DAY_MS / 1000) + DAY_CUTOFF_HOUR * 3600 - i64::from(utc_offset_secs);
    u64::try_from(secs.saturating_mul(1000)).unwrap_or(0)
}

/// 状態を作り直す単位。
#[derive(Debug, Clone, PartialEq)]
pub struct Segment {
    pub file: usize,
    pub day: i64,
    pub t0: u64,
    pub end: u64,
    /// `t0` が記録の `stage_starts` から来たか（来なければ規則）。
    pub t0_recorded: bool,
    pub seed: u64,
}

/// 区間を切る。種が記録と食い違う日は使わず、`mismatched` に入れる。
pub fn segments(
    files: &[DeskFile],
    hm_days: &BTreeMap<i64, HmDay>,
    table_sha256_hex: &str,
    utc_offset_secs: i32,
    mismatched: &mut Vec<i64>,
    overflowed: &mut Vec<i64>,
) -> Vec<Segment> {
    let mut out = Vec::new();
    for (fi, f) in files.iter().enumerate() {
        let mut a = f.session_start;
        while a < f.end {
            let day = local_day(a, utc_offset_secs);
            let b = f.end.min(day_start_ms(day + 1, utc_offset_secs));
            let seed = draw_seed(table_sha256_hex, day);
            let rec = hm_days.get(&day);
            if rec.and_then(|r| r.draw_seed).is_some_and(|s| s != seed) {
                if !mismatched.contains(&day) {
                    mismatched.push(day);
                }
            } else if rec.is_some_and(|r| r.overflow) {
                if !overflowed.contains(&day) {
                    overflowed.push(day);
                }
            } else {
                let mut t0s: Vec<(u64, bool)> = vec![(a, false)];
                if let Some(r) = rec {
                    for &s in &r.stage_starts {
                        if s == a {
                            t0s[0].1 = true;
                        } else if s > a && s < b {
                            t0s.push((s, true));
                        }
                    }
                }
                for (i, &(t0, recd)) in t0s.iter().enumerate() {
                    let end = t0s.get(i + 1).map_or(b, |n| n.0);
                    out.push(Segment {
                        file: fi,
                        day,
                        t0,
                        end,
                        t0_recorded: recd,
                        seed,
                    });
                }
            }
            if b <= a {
                break;
            }
            a = b;
        }
    }
    mismatched.sort_unstable();
    overflowed.sort_unstable();
    out
}

/// 区間の中の窓の始まり（格子にそろえ、立ち上がりを捨てる）。
pub fn window_starts(seg: &Segment) -> Vec<u64> {
    let first = seg.t0.saturating_add(WARMUP_MS).div_ceil(WINDOW_MS) * WINDOW_MS;
    let mut out = Vec::new();
    let mut w = first;
    while w.saturating_add(WINDOW_MS) <= seg.end {
        out.push(w);
        w += WINDOW_MS;
    }
    out
}

/// 窓を除く理由（最初に当たったもの）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Exclude {
    Pause,
    FewFeats,
    Away,
}

fn in_range<T>(v: &[T], key: impl Fn(&T) -> u64, from: u64, to: u64) -> &[T] {
    let a = v.partition_point(|x| key(x) < from);
    let b = v.partition_point(|x| key(x) < to);
    &v[a..b]
}

/// 窓 `[w, w + 30 s)` を除くか。
pub fn exclusion(f: &DeskFile, w: u64) -> Option<Exclude> {
    let e = w + WINDOW_MS;
    if f.pauses.iter().any(|&(a, b)| a < e && b > w) {
        return Some(Exclude::Pause);
    }
    if in_range(&f.feats, |x| x.t, w, e).len() < MIN_FEATS {
        return Some(Exclude::FewFeats);
    }
    let pressed = !in_range(&f.presses, |&t| t, w, e).is_empty();
    // pointer_bin の時刻はビンの終端なので (w, e] を見る
    let moved = !in_range(&f.bins, |b| b.timestamp, w + 1, e + 1).is_empty();
    if !pressed && !moved {
        let before = &f.presses[..f.presses.partition_point(|&t| t < w)];
        let away = before.last().is_none_or(|&t| w - t >= AWAY_IDLE_MS);
        if away {
            return Some(Exclude::Away);
        }
    }
    None
}

/// 窓の対象。
#[derive(Debug, Clone, Copy, PartialEq, Serialize)]
pub struct Targets {
    /// 平均の確率（flow・inc・stuck）。
    pub p_mean: [f64; 3],
    pub t1: u8,
    pub t1_all: u8,
    pub t2: u8,
}

/// 窓の `feat` から T1・T2 を作る（空なら `None`）。
pub fn targets(feats: &[Feat]) -> Option<Targets> {
    if feats.is_empty() {
        return None;
    }
    let n = feats.len() as f64;
    let mut m = [0.0f64; 3];
    for x in feats {
        for (k, v) in m.iter_mut().enumerate() {
            *v += x.p[k];
        }
    }
    for v in &mut m {
        *v /= n;
    }
    let mut t2 = 0usize;
    for k in 1..3 {
        if m[k] >= m[t2] {
            t2 = k;
        }
    }
    Some(Targets {
        p_mean: m,
        t1: u8::from(m[2] >= T1_P_STUCK),
        t1_all: u8::from(feats.iter().all(|x| x.p[2] >= T1_P_STUCK)),
        t2: t2 as u8,
    })
}

fn quantile(sorted: &[f64], q: f64) -> f64 {
    if sorted.is_empty() {
        return 0.0;
    }
    let pos = q * (sorted.len() - 1) as f64;
    let lo = pos.floor() as usize;
    let hi = pos.ceil() as usize;
    sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo as f64)
}

/// A の特徴（窓の終わり `e` で、許した情報だけから）。[`A_NAMES`] の順。
///
/// 振り返りは区間の始まり `from` より前を見ない（手跡の状態も `t0` より前を知らない。stage の始まりで切った
/// 区間とセッションの再起動の直後で、規則をそろえる・/cross-review の指摘）。
pub fn a_features(presses: &[u64], bins: &[PointerBin], e: u64, from: u64) -> [f64; 22] {
    let lo = |l: u64| e.saturating_sub(l).max(from);
    let count = |l: u64| in_range(presses, |&t| t, lo(l), e).len() as f64;
    let (n10, n30, n60) = (count(10_000), count(30_000), count(60_000));
    let p30 = in_range(presses, |&t| t, lo(30_000), e);
    let gaps: Vec<f64> = p30.windows(2).map(|w| (w[1] - w[0]) as f64).collect();
    let mut sorted = gaps.clone();
    sorted.sort_by(f64::total_cmp);
    let (median, p90) = (quantile(&sorted, 0.5), quantile(&sorted, 0.9));
    let cv = if gaps.len() >= 2 {
        let mean = gaps.iter().sum::<f64>() / gaps.len() as f64;
        let var = gaps.iter().map(|g| (g - mean).powi(2)).sum::<f64>() / gaps.len() as f64;
        if mean > 0.0 {
            var.sqrt() / mean
        } else {
            0.0
        }
    } else {
        0.0
    };
    // 60 秒の中の最長の間隔（窓の端も区切りに含める・上限 60 秒）
    let s60 = lo(60_000);
    let p60 = in_range(presses, |&t| t, s60, e);
    let mut edges: Vec<u64> = Vec::with_capacity(p60.len() + 2);
    edges.push(s60);
    edges.extend_from_slice(p60);
    edges.push(e);
    let max_gap = edges.windows(2).map(|w| w[1] - w[0]).max().unwrap_or(0) as f64;
    let last = presses[..presses.partition_point(|&t| t < e)]
        .last()
        .filter(|&&t| t >= from);
    let since = last.map_or(e - from.min(e), |&t| e - t).min(600_000) as f64;
    let pauses = gaps.iter().filter(|&&g| g >= 2_000.0).count() as f64;
    // 200 ms 未満で続く打鍵の列（2 打以上）の数と平均の長さ
    let (mut runs, mut run_total, mut cur) = (0usize, 0usize, 1usize);
    for &g in &gaps {
        if g < 200.0 {
            cur += 1;
        } else {
            if cur >= 2 {
                runs += 1;
                run_total += cur;
            }
            cur = 1;
        }
    }
    if cur >= 2 {
        runs += 1;
        run_total += cur;
    }
    let burst_len = if runs > 0 {
        run_total as f64 / runs as f64
    } else {
        0.0
    };
    let bins_in = |l: u64| in_range(bins, |b| b.timestamp, lo(l) + 1, e + 1);
    let move_sum = |l: u64| {
        bins_in(l)
            .iter()
            .map(|b| REP_PT[usize::from(b.moved).min(REP_PT.len() - 1)])
            .sum::<f64>()
    };
    let (m10, m30) = (move_sum(10_000), move_sum(30_000));
    let b30 = bins_in(30_000);
    let moved_secs = b30.iter().filter(|b| b.moved > 0).count() as f64;
    let buttons = b30.iter().map(|b| f64::from(b.buttons)).sum::<f64>();
    let wheel = b30.iter().map(|b| f64::from(b.wheel)).sum::<f64>();
    [
        n10,
        n10.ln_1p(),
        n30,
        n30.ln_1p(),
        n60,
        n60.ln_1p(),
        median,
        cv,
        p90,
        max_gap,
        since,
        since.ln_1p(),
        pauses,
        runs as f64,
        burst_len,
        m10,
        m10.ln_1p(),
        m30,
        m30.ln_1p(),
        moved_secs,
        buttons,
        wheel,
    ]
}

/// 1 時点の描き直し（変換の後）。
#[derive(Debug, Clone, PartialEq)]
pub struct Sample {
    pub t: u64,
    pub state: StageState,
    /// 場（全部が 0 なら `None`）。
    pub field: Option<[[f32; 3]; CELLS]>,
    /// 生きている波紋（x・y・始まりからの ms）。
    pub ripples: Vec<(f32, f32, u16)>,
}

/// 区間を流した結果。
#[derive(Debug, Clone, PartialEq)]
pub struct Stream {
    /// `qs` の順の標本。
    pub samples: Vec<Sample>,
    /// 波紋の始まりの時刻（昇順・最後の `q` まで）。
    pub ripple_starts: Vec<u64>,
}

/// 区間を 1 回だけ流して、昇順の時刻 `qs` での状態と場を出す。
///
/// 状態は `replay_live(presses, seed, t0, q)`、場は `replay_trace(bins, seed, t0, q)` とビット単位で同じ。
/// `transform` は状態に 1 回だけ当てる（`q` までの最後の `p_stuck` を渡す）。
pub fn stream_samples(
    seg: &Segment,
    f: &DeskFile,
    qs: &[u64],
    transform: &dyn Fn(StageState, Option<f64>) -> StageState,
) -> Stream {
    let mut stage = Stage::new(seg.seed, seg.t0);
    let mut field = TraceField::new(seg.t0);
    let q_last = qs.last().copied().unwrap_or(seg.t0);
    let mut synth = Synth::new(&f.bins, seg.seed, seg.t0, q_last);
    let g0 = seg.t0 / super::trace::STEP_MS * super::trace::STEP_MS;
    let mut k: u64 = 0;
    // 画面と同じ 6 枠の輪（`addRipple`: 次の枠を順に上書きする）
    let mut ripples: [Option<(f32, f32, u64)>; RIPPLE_SLOTS] = [None; RIPPLE_SLOTS];
    let mut ring_next = 0usize;
    let mut ripple_starts: Vec<u64> = Vec::new();
    let presses = &f.presses[f.presses.partition_point(|&t| t < seg.t0)..];
    let mut pi = 0usize;
    let mut out = Vec::with_capacity(qs.len());
    for &q in qs {
        // 状態（replay の流れ: 押下の時刻まで進めてから押す・最後に q − 遅れまで進める）
        let target = q.saturating_sub(LIVE_LAG_MS);
        while pi < presses.len() && presses[pi] <= target {
            stage.advance_to(presses[pi]);
            stage.press(presses[pi]);
            pi += 1;
        }
        stage.advance_to(target);
        // 場（刻み k の時刻は g0 + 16 k）
        while g0 + super::trace::STEP_MS * (k + 1) <= q {
            let Some(p) = synth.next() else { break };
            k += 1;
            if let Some(r) = field.step(Step {
                sample: Some(p),
                cursor_on: true,
                click_on: true,
                lost: false,
            }) {
                let at = g0 + super::trace::STEP_MS * k;
                ripples[ring_next] = Some((r.x, r.y, at));
                ring_next = (ring_next + 1) % RIPPLE_SLOTS;
                ripple_starts.push(at);
            }
        }
        for slot in &mut ripples {
            if slot.is_some_and(|r| r.2 + RIPPLE_LIFE_MS <= q) {
                *slot = None;
            }
        }
        let last_p = f.feats[..f.feats.partition_point(|x| x.t <= q)]
            .last()
            .map(|x| x.p[2]);
        let st = field.state();
        out.push(Sample {
            t: q,
            state: transform(stage.state(), last_p),
            field: if st.is_zero() { None } else { Some(st.cells) },
            ripples: ripples
                .iter()
                .flatten()
                .map(|r| (r.0, r.1, (q - r.2).min(u64::from(u16::MAX)) as u16))
                .collect(),
        });
    }
    Stream {
        samples: out,
        ripple_starts,
    }
}

/// 窓の標本（`τ` の側だけ）から B_state を作る。[`B_STATE_NAMES`] の順。
/// `ripple_starts` は窓の中で始まった波紋の数。
pub fn b_state_features(samples: &[&Sample], ripple_starts: usize) -> [f64; 13] {
    let n = samples.len().max(1) as f64;
    let speed: Vec<f64> = samples.iter().map(|s| s.state.speed).collect();
    let irreg: Vec<f64> = samples.iter().map(|s| s.state.irreg).collect();
    let mean = |v: &[f64]| v.iter().sum::<f64>() / n;
    let max = |v: &[f64]| v.iter().copied().fold(0.0f64, f64::max);
    let sm = mean(&speed);
    let sd = (speed.iter().map(|x| (x - sm).powi(2)).sum::<f64>() / n).sqrt();
    let phase_delta = match (samples.first(), samples.last()) {
        (Some(a), Some(b)) => b.state.phase - a.state.phase,
        _ => 0.0,
    };
    let (mut bend_sum, mut bend_max, mut pull_sum, mut nonzero) = (0.0f64, 0.0f64, 0.0f64, 0.0f64);
    for s in samples {
        if let Some(cells) = &s.field {
            for c in cells {
                let b = f64::from(c[0].abs());
                bend_sum += b;
                bend_max = bend_max.max(b);
                pull_sum += f64::from(c[1]).hypot(f64::from(c[2]));
                if c.iter().any(|v| *v != 0.0) {
                    nonzero += 1.0;
                }
            }
        }
    }
    let cells = n * CELLS as f64;
    [
        sm,
        max(&speed),
        speed.last().copied().unwrap_or(0.0),
        sd,
        mean(&irreg),
        max(&irreg),
        irreg.last().copied().unwrap_or(0.0),
        phase_delta,
        bend_sum / cells,
        bend_max,
        pull_sum / cells,
        nonzero / cells,
        ripple_starts as f64,
    ]
}

/// 表の 1 行。
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct WindowRow {
    pub id: u32,
    pub day: i64,
    pub file: usize,
    pub t_start: u64,
    /// 区間の始まりからの時間（ms・経過時間の診断に使う。判定の特徴には入れない）。
    pub t_since_t0: u64,
    pub t0_recorded: bool,
    pub hmm_version: Option<String>,
    pub n_feats: usize,
    pub p_mean: [f64; 3],
    pub t1: u8,
    pub t1_all: u8,
    pub t2: u8,
    pub a: Vec<f64>,
    pub b_state: Vec<f64>,
    /// 感度分析に使う窓（conditions.md C7: 使う日で、切っていた区間に重ならない）。
    pub sens: bool,
}

/// 除いた窓の数。
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize)]
pub struct Excluded {
    pub pause: usize,
    pub few_feats: usize,
    pub away: usize,
}

/// 道具の設定。
#[derive(Debug, Clone)]
pub struct DeskConfig {
    pub utc_offset_secs: i32,
    pub table_sha256_hex: String,
    /// 窓あたりの標本の数（30_000 を割り切る）。
    pub samples: usize,
    /// 区間指定削除の区間 `[from, to)`（台帳から）。重なる日は感度分析に使わない（C7）。
    pub redactions: Vec<(u64, u64)>,
}

/// 感度分析の日の、帯が見えていた割合の下限（C7）。
pub const SENS_MIN_VISIBLE: f64 = 0.5;
/// 感度分析の日の、切っていない窓の割合の下限（C7）。
pub const SENS_MIN_ON_SHARE: f64 = 0.5;

/// 感度分析の日の数え（日は数だけを出す。日の番号は暦に戻せるので書かない）。
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize)]
pub struct SensSummary {
    /// 割付が `late_first` か `on` の日。
    pub late_days: usize,
    /// 使う日。
    pub days: usize,
    /// 除いた日: `overflow`。
    pub overflow: usize,
    /// 除いた日: 区間指定削除に重なる。
    pub redacted: usize,
    /// 除いた日: `visible_ms / shown_ms` が下限未満か、量が無い。
    pub not_visible: usize,
    /// 除いた日: 切っていない窓がその日の有効な窓の下限未満（窓が無い日を含む）。
    pub few_on_windows: usize,
    /// 使う窓。
    pub windows: usize,
    /// 使う日のうち、切っていた区間に重なって除いた窓。
    pub windows_off: usize,
}

/// `toggles` から切っていた区間 `[from, to)` を作る。始めは出ている。切ったまま日が終われば `day_end` まで。
/// 同じ時刻の要素は記録の並び（操作の順）のまま扱う（安定な並べ替え）。長さ 0 の区間は捨てる。
pub fn off_intervals(toggles: &[(u64, bool)], day_end: u64) -> Vec<(u64, u64)> {
    let mut t = toggles.to_vec();
    t.sort_by_key(|x| x.0);
    let mut out = Vec::new();
    let mut open: Option<u64> = None;
    for (ti, on) in t {
        match (open, on) {
            (None, false) => open = Some(ti),
            (Some(a), true) => {
                if ti > a {
                    out.push((a, ti));
                }
                open = None;
            }
            _ => {}
        }
    }
    if let Some(a) = open {
        if day_end > a {
            out.push((a, day_end));
        }
    }
    out
}

/// 切っていない窓の割合が下限以上か（C7: 「その日の有効な窓の 50% 以上」・ちょうど半分は使う）。窓が 0 なら偽。
pub fn on_share_ok(on: usize, valid: usize) -> bool {
    valid > 0 && on as f64 >= SENS_MIN_ON_SHARE * valid as f64
}

/// 感度分析の日を選び、使う窓に印を付ける（C7）。
fn mark_sensitivity(hm_days: &BTreeMap<i64, HmDay>, cfg: &DeskConfig, out: &mut DeskOut) {
    let mut s = SensSummary::default();
    for (&day, r) in hm_days {
        if !matches!(r.assigned.as_deref(), Some("late_first" | "on")) {
            continue;
        }
        s.late_days += 1;
        let ds = day_start_ms(day, cfg.utc_offset_secs);
        let de = day_start_ms(day + 1, cfg.utc_offset_secs);
        if r.overflow {
            s.overflow += 1;
            continue;
        }
        // 台帳の区間は両端を含む（`redaction.rs` は `[from, to]` を消す）
        if cfg.redactions.iter().any(|&(a, b)| a < de && b >= ds) {
            s.redacted += 1;
            continue;
        }
        let visible = match (r.visible_ms, r.shown_ms) {
            (Some(v), Some(sh)) if sh > 0 => v as f64 >= SENS_MIN_VISIBLE * sh as f64,
            _ => false,
        };
        if !visible {
            s.not_visible += 1;
            continue;
        }
        let offs = off_intervals(&r.toggles, de);
        let idx: Vec<usize> = (0..out.windows.len())
            .filter(|&i| out.windows[i].day == day)
            .collect();
        let on: Vec<usize> = idx
            .iter()
            .copied()
            .filter(|&i| {
                let w = out.windows[i].t_start;
                let e = w + WINDOW_MS;
                !offs.iter().any(|&(a, b)| a < e && b > w)
            })
            .collect();
        if !on_share_ok(on.len(), idx.len()) {
            s.few_on_windows += 1;
            continue;
        }
        s.days += 1;
        s.windows += on.len();
        s.windows_off += idx.len() - on.len();
        for i in on {
            out.windows[i].sens = true;
        }
    }
    out.sens = s;
}

/// 道具の出力（コマは呼び出し側へ流す）。
#[derive(Debug, Clone, Default)]
pub struct DeskOut {
    pub windows: Vec<WindowRow>,
    pub excluded: Excluded,
    pub seed_mismatch_days: Vec<i64>,
    /// `stage_starts` が切れていて使わなかった日。
    pub overflow_days: Vec<i64>,
    pub segments: usize,
    pub segments_recorded_t0: usize,
    /// 感度分析の日の数え（C7）。
    pub sens: SensSummary,
}

/// 窓の表を作る。コマ（`τ − 250` と `τ` の 2 枚ずつ）は `on_frame(window_id, sample)` に流す。
pub fn build(
    files: &[DeskFile],
    cfg: &DeskConfig,
    transform: &dyn Fn(StageState, Option<f64>) -> StageState,
    on_frame: &mut dyn FnMut(u32, &Sample),
) -> Result<DeskOut> {
    if cfg.samples == 0 || !WINDOW_MS.is_multiple_of(cfg.samples as u64) {
        return Err(format!("標本の数 {} は 30000 を割り切らない", cfg.samples));
    }
    let step = WINDOW_MS / cfg.samples as u64;
    if step <= PAIR_GAP_MS {
        return Err(format!("標本の間隔 {step} ms が {PAIR_GAP_MS} ms 以下"));
    }
    let mut hm_days: BTreeMap<i64, HmDay> = BTreeMap::new();
    for f in files {
        for (d, r) in &f.hm_days {
            match hm_days.get(d) {
                Some(prev) if prev.t > r.t => {}
                _ => {
                    hm_days.insert(*d, r.clone());
                }
            }
        }
    }
    // 記録に書かれた表が、渡した表と違えば止める（別の人の表で黙って描き直さない）。同じ日の古い行も含めて
    // 全部の行を、畳む前に照らす。
    if let Some(sh) = files
        .iter()
        .flat_map(|f| {
            f.table_shas
                .iter()
                .chain(f.hm_days.values().filter_map(|r| r.table_sha256.as_ref()))
        })
        .find(|s| s.as_str() != cfg.table_sha256_hex)
    {
        return Err(format!(
            "handmark_day の行の表の SHA-256 が渡した表と違う（{sh}）"
        ));
    }
    let mut out = DeskOut::default();
    let segs = segments(
        files,
        &hm_days,
        &cfg.table_sha256_hex,
        cfg.utc_offset_secs,
        &mut out.seed_mismatch_days,
        &mut out.overflow_days,
    );
    out.segments = segs.len();
    out.segments_recorded_t0 = segs.iter().filter(|s| s.t0_recorded).count();
    let mut id: u32 = 0;
    for seg in &segs {
        let f = &files[seg.file];
        let mut kept: Vec<(u64, Targets, usize)> = Vec::new();
        for w in window_starts(seg) {
            match exclusion(f, w) {
                Some(Exclude::Pause) => out.excluded.pause += 1,
                Some(Exclude::FewFeats) => out.excluded.few_feats += 1,
                Some(Exclude::Away) => out.excluded.away += 1,
                None => {
                    let fs = in_range(&f.feats, |x| x.t, w, w + WINDOW_MS);
                    if let Some(tg) = targets(fs) {
                        kept.push((w, tg, fs.len()));
                    }
                }
            }
        }
        if kept.is_empty() {
            continue;
        }
        let mut qs = Vec::with_capacity(kept.len() * cfg.samples * 2);
        for (w, _, _) in &kept {
            for s in 1..=cfg.samples as u64 {
                let tau = w + step * s;
                qs.push(tau - PAIR_GAP_MS);
                qs.push(tau);
            }
        }
        let stream = stream_samples(seg, f, &qs, transform);
        let samples = &stream.samples;
        for (wi, (w, tg, n_feats)) in kept.iter().enumerate() {
            let chunk = &samples[wi * cfg.samples * 2..(wi + 1) * cfg.samples * 2];
            for s in chunk {
                on_frame(id, s);
            }
            let taus: Vec<&Sample> = chunk.iter().skip(1).step_by(2).collect();
            let ripple_starts = in_range(&stream.ripple_starts, |&t| t, *w, w + WINDOW_MS).len();
            out.windows.push(WindowRow {
                id,
                day: seg.day,
                file: seg.file,
                t_start: *w,
                t_since_t0: *w - seg.t0,
                t0_recorded: seg.t0_recorded,
                hmm_version: f.hmm_version.clone(),
                n_feats: *n_feats,
                p_mean: tg.p_mean,
                t1: tg.t1,
                t1_all: tg.t1_all,
                t2: tg.t2,
                a: a_features(&f.presses, &f.bins, w + WINDOW_MS, seg.t0).to_vec(),
                b_state: b_state_features(&taus, ripple_starts).to_vec(),
                sens: false,
            });
            id = id
                .checked_add(1)
                .ok_or_else(|| "窓の数が u32 を超えた".to_string())?;
        }
    }
    mark_sensitivity(&hm_days, cfg, &mut out);
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analysis::handmark::state::{replay_live, SplitMix64};
    use crate::analysis::handmark::trace_replay::replay_trace;

    const OFF: i32 = 9 * 3600;
    const SHA: &str = "ab";

    fn ident(s: StageState, _: Option<f64>) -> StageState {
        s
    }

    /// 日 `day` の 10:00（現地）。
    fn at10(day: i64) -> u64 {
        day_start_ms(day, OFF) + 6 * 3_600_000
    }

    fn feats_every_second(from: u64, to: u64, p_stuck: f64) -> Vec<Feat> {
        (from / 1000..to / 1000)
            .map(|s| Feat {
                t: s * 1000 + 300,
                p: [1.0 - p_stuck, 0.0, p_stuck],
            })
            .collect()
    }

    fn file(start: u64, end: u64) -> DeskFile {
        DeskFile {
            name: "f".into(),
            session_start: start,
            end,
            ..DeskFile::default()
        }
    }

    fn cfg() -> DeskConfig {
        DeskConfig {
            utc_offset_secs: OFF,
            table_sha256_hex: SHA.into(),
            samples: DEFAULT_SAMPLES,
            redactions: Vec::new(),
        }
    }

    #[test]
    fn day_start_is_the_first_ms_of_the_local_day() {
        for d in [20_000i64, 20_407, 20_800] {
            let s = day_start_ms(d, OFF);
            assert_eq!(local_day(s, OFF), d);
            assert_eq!(local_day(s - 1, OFF), d - 1);
        }
    }

    #[test]
    fn parse_reads_the_rows_and_fails_closed_on_broken_fields() {
        // 時刻は T を基準にした相対で書いて置き換える
        let t = |x: u64| (T + x).to_string();
        let text = [
            r#"{"type":"meta","session_start":@1000,"hmm_version":"0.5.0"}"#,
            r#"{"type":"key","t":@2000,"press":true,"category":"letter"}"#,
            r#"{"type":"key","t":@2050,"press":false,"category":"letter"}"#,
            r#"{"type":"pointer_bin","t":@3000,"moved":2,"buttons":1,"wheel":0}"#,
            r#"{"type":"feat","t":@3100,"p_flow":0.2,"p_inc":0.3,"p_stuck":0.5}"#,
            r#"{"type":"recording_pause","t":@4000,"paused":true}"#,
            r#"{"type":"recording_pause","t":@5000,"paused":false}"#,
            r#"{"type":"handmark_day","t":@6000,"day":7,"draw_seed":"00000000000000ff","stage_starts":[@5500,@5400],"table_sha256":"AB","overflow":true,"assigned":"on","shown_ms":900,"visible_ms":800,"toggles":[{"t":@5600,"on":false},{"t":@5700,"on":true}]}"#,
            r#"{"type":"handmark_day","t":@5900,"day":7,"draw_seed":null,"stage_starts":[]}"#,
            r#"{"type":"focus_transition","t":@9000}"#,
            r#"{"type":"unknown_kind","t":99999999999999}"#,
        ]
        .join("\n");
        let text = rel(&text, &t);
        let f = parse_file("a", &text).unwrap();
        assert_eq!(f.session_start, T + 1000);
        // 知らない行種の時刻（focus_transition・壊れた時刻）は終わりに使わない
        assert_eq!(f.end, T + 6000);
        assert_eq!(f.presses, vec![T + 2000]);
        assert_eq!(f.bins.len(), 1);
        assert_eq!(f.feats[0].p, [0.2, 0.3, 0.5]);
        assert_eq!(f.pauses, vec![(T + 4000, T + 5000)]);
        let d = &f.hm_days[&7];
        assert_eq!(d.draw_seed, Some(0xff));
        assert_eq!(d.stage_starts, vec![T + 5400, T + 5500]);
        assert_eq!(d.table_sha256.as_deref(), Some("ab"));
        assert!(d.overflow);
        assert_eq!(d.assigned.as_deref(), Some("on"));
        assert_eq!((d.shown_ms, d.visible_ms), (Some(900), Some(800)));
        assert_eq!(d.toggles, vec![(T + 5600, false), (T + 5700, true)]);

        for bad in [
            r#"{"type":"handmark_day","t":@1,"day":1,"assigned":3}"#,
            r#"{"type":"handmark_day","t":@1,"day":1,"shown_ms":-1}"#,
            r#"{"type":"handmark_day","t":@1,"day":1,"visible_ms":"x"}"#,
            r#"{"type":"handmark_day","t":@1,"day":1,"toggles":{}}"#,
            r#"{"type":"handmark_day","t":@1,"day":1,"toggles":[{"t":@1}]}"#,
            r#"{"type":"key","t":"x","press":true}"#,
            r#"{"type":"key","t":@1,"press":"yes"}"#,
            r#"{"type":"feat","t":@1,"p_flow":0.1,"p_inc":0.1}"#,
            r#"{"type":"pointer_bin","t":@1,"moved":300,"buttons":0,"wheel":0}"#,
            r#"{"type":"handmark_day","t":@1,"day":1,"draw_seed":"zz"}"#,
            r#"{"type":"handmark_day","t":@1,"day":1,"table_sha256":3}"#,
            r#"{"type":"key","t":5,"press":true}"#,
            r#"{"type":"key","t":@1,"press":true"#,
            "not json",
        ] {
            let text = rel(
                &format!("{{\"type\":\"meta\",\"session_start\":@0}}\n{bad}"),
                &t,
            );
            assert!(parse_file("b", &text).is_err(), "{bad}");
        }
        assert!(parse_file("c", &rel(r#"{"type":"key","t":@1,"press":true}"#, &t)).is_err());
        // 幅が 40 日を超える記録は止める
        let long = rel(
            &format!(
                "{{\"type\":\"meta\",\"session_start\":@0}}\n{{\"type\":\"key\",\"t\":@{},\"press\":true}}",
                MAX_FILE_SPAN_MS + 1
            ),
            &t,
        );
        assert!(parse_file("d", &long).is_err());
    }

    /// `@123` を `t(123)` に置き換える。
    fn rel(text: &str, t: &dyn Fn(u64) -> String) -> String {
        let mut out = String::new();
        let mut rest = text;
        while let Some(i) = rest.find('@') {
            out.push_str(&rest[..i]);
            let tail = &rest[i + 1..];
            let n = tail
                .find(|c: char| !c.is_ascii_digit())
                .unwrap_or(tail.len());
            out.push_str(&t(tail[..n].parse().unwrap()));
            rest = &tail[n..];
        }
        out.push_str(rest);
        out
    }

    const T: u64 = 1_700_000_000_000;

    #[test]
    fn an_open_pause_runs_to_the_end_of_the_file() {
        let text = format!(
            "{{\"type\":\"meta\",\"session_start\":{}}}\n{{\"type\":\"recording_pause\",\"t\":{},\"paused\":true}}\n{{\"type\":\"meta\",\"session_end\":{}}}",
            T,
            T + 10,
            T + 99
        );
        assert_eq!(
            parse_file("p", &text).unwrap().pauses,
            vec![(T + 10, T + 99)]
        );
    }

    #[test]
    fn segments_cut_at_the_day_boundary_and_at_stage_starts() {
        let d = 20_400;
        let start = day_start_ms(d + 1, OFF) - 3_600_000; // 前の日の 3:00
        let f = file(start, day_start_ms(d + 1, OFF) + 7_200_000);
        let s1 = day_start_ms(d + 1, OFF) + 1_800_000;
        let mut hm = BTreeMap::new();
        hm.insert(
            d + 1,
            HmDay {
                t: 1,
                draw_seed: Some(draw_seed(SHA, d + 1)),
                stage_starts: vec![s1, day_start_ms(d + 3, OFF)],
                ..HmDay::default()
            },
        );
        let mut mis = Vec::new();
        let segs = segments(&[f], &hm, SHA, OFF, &mut mis, &mut Vec::new());
        assert!(mis.is_empty());
        let got: Vec<(i64, u64, u64, bool)> = segs
            .iter()
            .map(|s| (s.day, s.t0, s.end, s.t0_recorded))
            .collect();
        let b = day_start_ms(d + 1, OFF);
        assert_eq!(
            got,
            vec![
                (d, start, b, false),
                (d + 1, b, s1, false),
                (d + 1, s1, b + 7_200_000, true),
            ]
        );
        assert_eq!(segs[0].seed, draw_seed(SHA, d));
        assert_eq!(segs[2].seed, draw_seed(SHA, d + 1));
    }

    #[test]
    fn a_day_whose_recorded_seed_differs_is_left_out_and_reported() {
        let d = 20_400;
        let f = file(at10(d), at10(d) + 3_600_000);
        let mut hm = BTreeMap::new();
        hm.insert(
            d,
            HmDay {
                t: 1,
                draw_seed: Some(draw_seed(SHA, d) ^ 1),
                stage_starts: vec![],
                ..HmDay::default()
            },
        );
        let mut mis = Vec::new();
        assert!(segments(&[f], &hm, SHA, OFF, &mut mis, &mut Vec::new()).is_empty());
        assert_eq!(mis, vec![d]);
    }

    #[test]
    fn windows_sit_on_the_grid_after_the_warmup_and_inside_the_segment() {
        let seg = Segment {
            file: 0,
            day: 0,
            t0: 1_000_010,
            end: 1_150_000,
            t0_recorded: false,
            seed: 1,
        };
        // t0 + 30 s = 1_030_010 → 次の格子は 1_050_000。最後は 1_120_000（終わり 1_150_000 に収まる）
        assert_eq!(window_starts(&seg), vec![1_050_000, 1_080_000, 1_110_000]);
        let exact = Segment {
            t0: 1_020_000,
            end: 1_080_000,
            ..seg
        };
        assert_eq!(window_starts(&exact), vec![1_050_000]);
    }

    #[test]
    fn exclusions_are_checked_in_order() {
        let w = 3_000_000;
        let mut f = file(0, 4_000_000);
        f.feats = feats_every_second(w, w + WINDOW_MS, 0.1);
        f.presses = vec![w - AWAY_IDLE_MS];
        assert_eq!(exclusion(&f, w), Some(Exclude::Away));
        f.presses = vec![w - AWAY_IDLE_MS + 1];
        assert_eq!(exclusion(&f, w), None);
        f.presses = vec![w - AWAY_IDLE_MS];
        f.bins = vec![PointerBin {
            timestamp: w + WINDOW_MS,
            moved: 1,
            buttons: 0,
            wheel: 0,
        }];
        assert_eq!(exclusion(&f, w), None, "ビンの終端が窓の終わりなら窓に入る");
        f.bins[0].timestamp = w;
        assert_eq!(
            exclusion(&f, w),
            Some(Exclude::Away),
            "始まりの時刻の終端は前の秒"
        );
        f.feats.truncate(MIN_FEATS - 1);
        assert_eq!(exclusion(&f, w), Some(Exclude::FewFeats));
        f.pauses = vec![(w + WINDOW_MS - 1, w + WINDOW_MS + 10)];
        assert_eq!(exclusion(&f, w), Some(Exclude::Pause));
        f.pauses = vec![(w + WINDOW_MS, w + WINDOW_MS + 10)];
        assert_eq!(exclusion(&f, w), Some(Exclude::FewFeats));
    }

    #[test]
    fn t1_uses_the_mean_and_t2_breaks_ties_to_the_later_class() {
        let mk = |ps: &[[f64; 3]]| -> Vec<Feat> {
            ps.iter()
                .enumerate()
                .map(|(i, p)| Feat { t: i as u64, p: *p })
                .collect()
        };
        let t = targets(&mk(&[[0.4, 0.0, 0.6], [0.4, 0.0, 0.6]])).unwrap();
        assert_eq!((t.t1, t.t1_all, t.t2), (1, 1, 2));
        let t = targets(&mk(&[[0.0, 0.1, 0.9], [0.5, 0.0, 0.5]])).unwrap();
        assert_eq!((t.t1, t.t1_all), (1, 0));
        let t = targets(&mk(&[[0.41, 0.0, 0.59]])).unwrap();
        assert_eq!(t.t1, 0);
        let t = targets(&mk(&[[0.5, 0.5, 0.0]])).unwrap();
        assert_eq!(t.t2, 1);
        let t = targets(&mk(&[[0.4, 0.2, 0.4]])).unwrap();
        assert_eq!(t.t2, 2);
        assert!(targets(&[]).is_none());
    }

    #[test]
    fn a_features_follow_their_definitions() {
        let e = 100_000;
        let presses = vec![
            e - 50_000,
            e - 9_000,
            e - 8_900,
            e - 8_800,
            e - 5_000,
            e - 100,
        ];
        let bins = vec![
            PointerBin {
                timestamp: e - 20_000,
                moved: 3,
                buttons: 2,
                wheel: 1,
            },
            PointerBin {
                timestamp: e,
                moved: 1,
                buttons: 0,
                wheel: 0,
            },
            PointerBin {
                timestamp: e - 10_000,
                moved: 2,
                buttons: 0,
                wheel: 0,
            },
        ];
        let mut sorted = bins.clone();
        sorted.sort_by_key(|b| b.timestamp);
        let a = a_features(&presses, &sorted, e, 0);
        let get = |n: &str| a[A_NAMES.iter().position(|x| *x == n).unwrap()];
        assert_eq!(get("n_press_10"), 5.0);
        assert_eq!(get("n_press_30"), 5.0);
        assert_eq!(get("n_press_60"), 6.0);
        // 30 秒の間隔: 100, 100, 3800, 4900
        assert_eq!(get("iki_median_30"), 1_950.0);
        assert_eq!(get("pauses_2s_30"), 2.0);
        assert_eq!(get("bursts_30"), 1.0);
        assert_eq!(get("burst_len_30"), 3.0);
        // 60 秒: 端 e-60000 → e-50000 は 10000、e-50000 → e-9000 は 41000
        assert_eq!(get("max_gap_60"), 41_000.0);
        assert_eq!(get("since_last_press"), 100.0);
        // 10 秒は (e-10000, e]: e-10000 のビンは入らない
        assert_eq!(get("move_sum_10"), REP_PT[1]);
        assert_eq!(get("move_sum_30"), REP_PT[1] + REP_PT[2] + REP_PT[3]);
        assert_eq!(get("moved_secs_30"), 3.0);
        assert_eq!(get("buttons_30"), 2.0);
        assert_eq!(get("wheel_30"), 1.0);
        // 打鍵が無ければ、最後の打鍵からの時間は区間の始まり（ここでは 0）からの時間（上限 600 秒）
        let none = a_features(&[], &[], e, 0);
        assert!(none.iter().all(|v| v.is_finite()));
        assert_eq!(
            none[A_NAMES
                .iter()
                .position(|x| *x == "since_last_press")
                .unwrap()],
            100_000.0
        );
    }

    #[test]
    fn a_features_do_not_look_before_the_segment_start() {
        let e = 1_000_000;
        let from = e - 40_000;
        let presses = vec![e - 55_000, e - 45_000, e - 20_000, e - 1_000];
        let bins = vec![
            PointerBin {
                timestamp: e - 50_000,
                moved: 3,
                buttons: 1,
                wheel: 0,
            },
            PointerBin {
                timestamp: e - 5_000,
                moved: 2,
                buttons: 0,
                wheel: 0,
            },
        ];
        let a = a_features(&presses, &bins, e, from);
        let get = |n: &str| a[A_NAMES.iter().position(|x| *x == n).unwrap()];
        assert_eq!(get("n_press_60"), 2.0, "t0 より前の 2 打は数えない");
        // 60 秒の最長の間隔は from から測る: from → e-20000 は 20000
        assert_eq!(get("max_gap_60"), 20_000.0);
        assert_eq!(get("buttons_30"), 0.0);
        // t0 の後に打鍵が無ければ、最後の打鍵からの時間は t0 からの時間
        let a = a_features(&presses, &bins, from + 10_000, from + 5_000);
        assert_eq!(
            a[A_NAMES
                .iter()
                .position(|x| *x == "since_last_press")
                .unwrap()],
            5_000.0
        );
    }

    fn random_file(seed: u64, t0: u64, span: u64) -> DeskFile {
        let mut r = SplitMix64::new(seed);
        let mut f = file(t0, t0 + span);
        let mut t = t0 + 500;
        while t < t0 + span {
            let span_ms = if r.below(10) == 0 { 8_000 } else { 400 };
            t += 40 + r.below(span_ms);
            f.presses.push(t);
        }
        let mut s = t0 / 1000 * 1000 + 1000;
        while s < t0 + span {
            if r.below(3) == 0 {
                f.bins.push(PointerBin {
                    timestamp: s,
                    moved: r.below(8) as u8,
                    buttons: r.below(3) as u8,
                    wheel: 0,
                });
            }
            s += 1000;
        }
        f.feats = feats_every_second(t0, t0 + span, 0.3);
        f
    }

    #[test]
    fn streamed_samples_match_replay_live_and_replay_trace_bit_for_bit() {
        for case in 0..12u64 {
            let t0 = 1_700_000_000_123 + case * 7;
            let f = random_file(case, t0, 120_000);
            let seg = Segment {
                file: 0,
                day: 0,
                t0,
                end: t0 + 120_000,
                t0_recorded: false,
                seed: 0x1234 ^ case,
            };
            let mut r = SplitMix64::new(case + 99);
            let mut qs: Vec<u64> = (0..40).map(|_| t0 + 1 + r.below(119_000)).collect();
            qs.sort_unstable();
            qs.dedup();
            let got = stream_samples(&seg, &f, &qs, &ident).samples;
            for (q, s) in qs.iter().zip(&got) {
                let want = replay_live(&f.presses, seg.seed, t0, *q);
                assert_eq!(s.state.bits(), want.bits(), "case {case} q {q}");
                let tr = replay_trace(&f.bins, seg.seed, t0, *q);
                let cells = s.field.unwrap_or([[0.0; 3]; CELLS]);
                let mut a = vec![tr.epoch];
                a.extend(tr.cells.iter().flat_map(|c| c.iter().map(|v| v.to_bits())));
                let mut b = vec![tr.epoch];
                b.extend(cells.iter().flat_map(|c| c.iter().map(|v| v.to_bits())));
                assert_eq!(a, b, "case {case} q {q}");
            }
        }
    }

    #[test]
    fn the_transform_sees_the_last_p_stuck_and_touches_only_the_output() {
        let t0 = 1_700_000_000_000;
        let mut f = random_file(3, t0, 60_000);
        f.feats = vec![
            Feat {
                t: t0 + 10_000,
                p: [0.0, 0.0, 0.25],
            },
            Feat {
                t: t0 + 20_000,
                p: [0.0, 0.0, 0.75],
            },
        ];
        let seg = Segment {
            file: 0,
            day: 0,
            t0,
            end: t0 + 60_000,
            t0_recorded: false,
            seed: 5,
        };
        let qs = [t0 + 5_000, t0 + 15_000, t0 + 20_000, t0 + 50_000];
        let plain = stream_samples(&seg, &f, &qs, &ident).samples;
        let bump = |s: StageState, p: Option<f64>| StageState {
            speed: s.speed + p.unwrap_or(-1.0),
            ..s
        };
        let bumped = stream_samples(&seg, &f, &qs, &bump).samples;
        let adds: Vec<f64> = plain
            .iter()
            .zip(&bumped)
            .map(|(a, b)| b.state.speed - a.state.speed)
            .collect();
        assert_eq!(adds, vec![-1.0, 0.25, 0.75, 0.75]);
        for (a, b) in plain.iter().zip(&bumped) {
            assert_eq!(a.state.phase.to_bits(), b.state.phase.to_bits());
        }
    }

    #[test]
    fn ripples_live_for_their_lifetime() {
        let t0 = 1_700_000_000_000;
        let mut f = file(t0, t0 + 20_000);
        f.bins = vec![PointerBin {
            timestamp: t0 + 3_000,
            moved: 2,
            buttons: 1,
            wheel: 0,
        }];
        let seg = Segment {
            file: 0,
            day: 0,
            t0,
            end: t0 + 20_000,
            t0_recorded: false,
            seed: 9,
        };
        // 押下はビンの区間 [t0+2000, t0+3000) の真ん中 t0+2500 を含む刻み
        let qs: Vec<u64> = (0..40).map(|i| t0 + 2_000 + i * 100).collect();
        let st = stream_samples(&seg, &f, &qs, &ident);
        // 押下は t0 + 2500 を含む 16 ms の刻み（終わりの時刻 t0 + 2512）
        assert_eq!(st.ripple_starts, vec![t0 + 2_512]);
        let s = st.samples;
        let alive: Vec<u64> = s
            .iter()
            .filter(|x| !x.ripples.is_empty())
            .map(|x| x.t)
            .collect();
        assert!(!alive.is_empty());
        let first = alive[0];
        let last = *alive.last().unwrap();
        assert_eq!(first, t0 + 2_600);
        assert!(
            last - first < RIPPLE_LIFE_MS && last - first >= RIPPLE_LIFE_MS - 200,
            "{}",
            last - first
        );
    }

    #[test]
    fn ripples_use_six_slots_like_the_screen() {
        let t0 = 1_700_000_000_000;
        let mut f = file(t0, t0 + 20_000);
        // 1 秒に 15 回の押下（画面は最新の 6 つしか持たない）
        f.bins = vec![PointerBin {
            timestamp: t0 + 3_000,
            moved: 0,
            buttons: 15,
            wheel: 0,
        }];
        let seg = Segment {
            file: 0,
            day: 0,
            t0,
            end: t0 + 20_000,
            t0_recorded: false,
            seed: 9,
        };
        let qs: Vec<u64> = (0..30).map(|i| t0 + 2_000 + i * 100).collect();
        let st = stream_samples(&seg, &f, &qs, &ident);
        assert_eq!(st.ripple_starts.len(), 15, "始まりは全部数える");
        assert!(st.samples.iter().all(|x| x.ripples.len() <= RIPPLE_SLOTS));
        let at_end = st.samples.iter().find(|x| x.t == t0 + 3_000).unwrap();
        assert_eq!(at_end.ripples.len(), RIPPLE_SLOTS);
        // 残るのは最新の 6 つ（経過が短い順に 6 つ）
        let newest: Vec<u64> = st
            .ripple_starts
            .iter()
            .rev()
            .take(RIPPLE_SLOTS)
            .copied()
            .collect();
        let mut ages: Vec<u16> = at_end.ripples.iter().map(|r| r.2).collect();
        ages.sort_unstable();
        let mut want: Vec<u16> = newest.iter().map(|&s| (t0 + 3_000 - s) as u16).collect();
        want.sort_unstable();
        assert_eq!(ages, want);
    }

    #[test]
    fn a_second_segment_with_earlier_presses_still_matches_the_replay() {
        // 区間の t0 より前にも打鍵とビンがある（日の 2 つ目の区間・stage の始まりの後）
        for case in 0..6u64 {
            let start = 1_700_000_000_000 + case * 13;
            let f = random_file(case + 40, start, 180_000);
            let t0 = start + 61_237;
            let seg = Segment {
                file: 0,
                day: 0,
                t0,
                end: start + 180_000,
                t0_recorded: true,
                seed: 77 ^ case,
            };
            let qs: Vec<u64> = (1..40).map(|i| t0 + i * 2_900).collect();
            let got = stream_samples(&seg, &f, &qs, &ident).samples;
            for (q, s) in qs.iter().zip(&got) {
                assert_eq!(
                    s.state.bits(),
                    replay_live(&f.presses, seg.seed, t0, *q).bits()
                );
                let tr = replay_trace(&f.bins, seg.seed, t0, *q);
                let cells = s.field.unwrap_or([[0.0; 3]; CELLS]);
                assert_eq!(
                    tr.cells
                        .iter()
                        .flatten()
                        .map(|v| v.to_bits())
                        .collect::<Vec<_>>(),
                    cells
                        .iter()
                        .flatten()
                        .map(|v| v.to_bits())
                        .collect::<Vec<_>>(),
                    "case {case} q {q}"
                );
            }
        }
    }

    #[test]
    fn a_recorded_table_other_than_the_given_one_stops_and_overflow_days_are_left_out() {
        let d = 20_400;
        let mut f = day_file(d, 0.3, 5);
        f.hm_days.insert(
            d,
            HmDay {
                t: 1,
                table_sha256: Some("cd".into()),
                ..HmDay::default()
            },
        );
        assert!(build(&[f.clone()], &cfg(), &ident, &mut |_, _| {}).is_err());
        f.hm_days.insert(
            d,
            HmDay {
                t: 1,
                table_sha256: Some(SHA.into()),
                overflow: true,
                ..HmDay::default()
            },
        );
        let out = build(&[f], &cfg(), &ident, &mut |_, _| {}).unwrap();
        assert_eq!(out.overflow_days, vec![d]);
        assert!(out.windows.is_empty());
    }

    fn day_file(day: i64, p_stuck: f64, seed: u64) -> DeskFile {
        let t0 = at10(day);
        let mut f = random_file(seed, t0, 600_000);
        f.feats = feats_every_second(t0, t0 + 600_000, p_stuck);
        f
    }

    #[test]
    fn off_intervals_start_shown_and_close_at_the_day_end() {
        assert!(off_intervals(&[], 100).is_empty());
        assert_eq!(
            off_intervals(&[(50, true), (10, false), (20, true), (30, false)], 100),
            vec![(10, 20), (30, 50)]
        );
        // 切ったまま日が終われば日の終わりまで
        assert_eq!(
            off_intervals(&[(10, false), (20, true), (30, false)], 100),
            vec![(10, 20), (30, 100)]
        );
        // 同じ時刻の要素は記録の順のまま: 切ってすぐ戻せば長さ 0 で捨て、戻してすぐ切れば切ったまま
        assert!(off_intervals(&[(10, false), (10, true)], 100).is_empty());
        assert_eq!(
            off_intervals(&[(10, true), (10, false)], 100),
            vec![(10, 100)]
        );
        // 5 で切る・10 で戻す・10 で切る・20 で戻す（/cross-review 2 巡目の例）
        assert_eq!(
            off_intervals(&[(5, false), (10, true), (10, false), (20, true)], 100),
            vec![(5, 10), (10, 20)]
        );
        assert!(off_intervals(&[(100, false)], 100).is_empty());
        // 続けて切る・続けて戻すは 1 つにまとめる
        assert_eq!(
            off_intervals(&[(10, false), (15, false), (20, true), (25, true)], 100),
            vec![(10, 20)]
        );
    }

    #[test]
    fn on_share_boundary_is_inclusive_at_half() {
        assert!(on_share_ok(10, 20));
        assert!(!on_share_ok(9, 20));
        assert!(on_share_ok(1, 1));
        assert!(!on_share_ok(0, 0));
        assert!(on_share_ok(2, 3) && !on_share_ok(1, 3));
    }

    #[test]
    fn a_redaction_ending_at_the_day_start_touches_that_day() {
        let d = 20_400;
        let mut f = day_file(d, 0.3, 3);
        f.hm_days.insert(
            d,
            HmDay {
                t: 1,
                assigned: Some("on".into()),
                shown_ms: Some(1000),
                visible_ms: Some(1000),
                ..HmDay::default()
            },
        );
        let ds = day_start_ms(d, OFF);
        let mut c = cfg();
        c.redactions = vec![(ds - 60_000, ds - 1)];
        let out = build(&[f.clone()], &c, &ident, &mut |_, _| {}).unwrap();
        assert_eq!((out.sens.days, out.sens.redacted), (1, 0));
        c.redactions = vec![(ds - 60_000, ds)];
        let out = build(&[f], &c, &ident, &mut |_, _| {}).unwrap();
        assert_eq!((out.sens.days, out.sens.redacted), (0, 1));
    }

    /// 感度分析の日（C7）: 割付・overflow・削除・見えていた割合・切っていない窓の割合の各分岐。
    #[test]
    fn sensitivity_days_follow_c7() {
        let base = 20_400;
        // 日ごとに (割付, 見えていた/出ていた, 切った区間の長さの割合, overflow, 削除)
        /// (割付, (見えていた, 出ていた), 切った割合, overflow, 削除)
        type Case<'a> = (Option<&'a str>, (u64, u64), f64, bool, bool);
        let cases: [Case; 8] = [
            (Some("on"), (900, 1000), 0.0, false, false), // 使う
            (Some("late_first"), (500, 1000), 0.4, false, false), // 使う（境界ちょうど・切った窓は除く）
            (Some("off"), (900, 1000), 0.0, false, false),        // 割付の外
            (None, (900, 1000), 0.0, false, false),               // 前期の行
            (Some("on"), (499, 1000), 0.0, false, false),         // 見えていない
            (Some("on"), (900, 1000), 0.7, false, false),         // 切っていた窓が多い
            (Some("on"), (900, 1000), 0.0, true, false),          // overflow
            (Some("on"), (900, 1000), 0.0, false, true),          // 削除に重なる
        ];
        let mut files = Vec::new();
        let mut redactions = Vec::new();
        for (i, (asg, (vis, shown), off_share, overflow, redacted)) in cases.iter().enumerate() {
            let d = base + i as i64;
            let mut f = day_file(d, 0.3, 10 + i as u64);
            let t0 = at10(d);
            let toggles = if *off_share > 0.0 {
                // 窓の格子の始まり（t0 + 30 s の後）から切る
                let a = t0 + 30_000;
                vec![(a, false), (a + (600_000.0 * off_share) as u64, true)]
            } else {
                Vec::new()
            };
            f.hm_days.insert(
                d,
                HmDay {
                    t: 1,
                    assigned: asg.map(str::to_string),
                    shown_ms: Some(*shown),
                    visible_ms: Some(*vis),
                    toggles,
                    overflow: *overflow,
                    ..HmDay::default()
                },
            );
            if *redacted {
                redactions.push((t0 + 100_000, t0 + 160_000));
            }
            files.push(f);
        }
        let mut c = cfg();
        c.redactions = redactions;
        let out = build(&files, &c, &ident, &mut |_, _| {}).unwrap();
        let s = out.sens;
        assert_eq!(s.late_days, 6);
        assert_eq!(s.days, 2);
        assert_eq!(
            (s.not_visible, s.few_on_windows, s.overflow, s.redacted),
            (1, 1, 1, 1)
        );
        let used: Vec<i64> = out
            .windows
            .iter()
            .filter(|w| w.sens)
            .map(|w| w.day)
            .collect();
        assert!(used.iter().all(|&d| d == base || d == base + 1));
        let day1 = out.windows.iter().filter(|w| w.day == base + 1).count();
        let day1_used = out
            .windows
            .iter()
            .filter(|w| w.day == base + 1 && w.sens)
            .count();
        assert!(
            day1_used < day1 && day1_used * 2 >= day1,
            "{day1_used}/{day1}"
        );
        assert_eq!(s.windows, used.len());
        assert_eq!(s.windows_off, day1 - day1_used);
        // 切っていた区間に重なる窓は使わない
        let off_end = at10(base + 1) + 30_000 + 240_000;
        assert!(out
            .windows
            .iter()
            .filter(|w| w.day == base + 1 && w.sens)
            .all(|w| w.t_start >= off_end));
        // 主の窓の表は変えない（感度の印のほかは、割付の行が無い場合と同じ）
        let plain: Vec<DeskFile> = files
            .iter()
            .map(|f| {
                let mut g = f.clone();
                for r in g.hm_days.values_mut() {
                    *r = HmDay {
                        t: r.t,
                        overflow: r.overflow,
                        ..HmDay::default()
                    };
                }
                g
            })
            .collect();
        let out0 = build(&plain, &cfg(), &ident, &mut |_, _| {}).unwrap();
        let strip = |o: &DeskOut| -> Vec<WindowRow> {
            o.windows
                .iter()
                .cloned()
                .map(|mut w| {
                    w.sens = false;
                    w
                })
                .collect()
        };
        assert_eq!(strip(&out), strip(&out0));
        assert_eq!(out0.sens.late_days, 0);
    }

    #[test]
    fn build_is_deterministic_and_counts_windows_and_frames() {
        let files = vec![day_file(20_400, 0.7, 1), day_file(20_401, 0.2, 2)];
        let run = || {
            let mut frames: Vec<(u32, u64)> = Vec::new();
            let out = build(&files, &cfg(), &ident, &mut |id, s| frames.push((id, s.t))).unwrap();
            let rows = serde_json::to_string(&out.windows).unwrap();
            (out, rows, frames)
        };
        let (a, rows_a, frames_a) = run();
        let (_, rows_b, frames_b) = run();
        assert_eq!(rows_a, rows_b);
        assert_eq!(frames_a, frames_b);
        assert!(!a.windows.is_empty());
        assert_eq!(frames_a.len(), a.windows.len() * DEFAULT_SAMPLES * 2);
        assert!(a
            .windows
            .iter()
            .all(|w| w.a.len() == 22 && w.b_state.len() == 13));
        assert!(a
            .windows
            .iter()
            .all(|w| w.a.iter().chain(&w.b_state).all(|v| v.is_finite())));
        let t1: Vec<(i64, u8)> = a.windows.iter().map(|w| (w.day, w.t1)).collect();
        assert!(t1.iter().all(|&(d, t)| (d == 20_400) == (t == 1)));
        // 窓の始まりは格子の上・区間の t0 + 30 s 以降
        assert!(a
            .windows
            .iter()
            .all(|w| w.t_start % WINDOW_MS == 0 && w.t_start >= at10(w.day) + WARMUP_MS));
        let ids: Vec<u32> = a.windows.iter().map(|w| w.id).collect();
        assert_eq!(ids, (0..ids.len() as u32).collect::<Vec<_>>());
    }

    #[test]
    fn build_rejects_sample_counts_that_do_not_divide_the_window() {
        let mut c = cfg();
        for bad in [0usize, 7, 200] {
            c.samples = bad;
            assert!(build(&[], &c, &ident, &mut |_, _| {}).is_err(), "{bad}");
        }
        c.samples = 6;
        assert!(build(&[], &c, &ident, &mut |_, _| {}).is_ok());
    }

    #[test]
    fn the_identity_transform_leaves_the_table_unchanged_and_a_leak_changes_only_b() {
        let files = vec![day_file(20_400, 0.7, 4)];
        let plain = build(&files, &cfg(), &ident, &mut |_, _| {}).unwrap();
        let leak = |s: StageState, p: Option<f64>| StageState {
            speed: s.speed + p.unwrap_or(0.0),
            ..s
        };
        let leaked = build(&files, &cfg(), &leak, &mut |_, _| {}).unwrap();
        assert_eq!(plain.windows.len(), leaked.windows.len());
        for (a, b) in plain.windows.iter().zip(&leaked.windows) {
            assert_eq!(a.a, b.a);
            assert_eq!((a.t1, a.t2), (b.t1, b.t2));
            assert_ne!(a.b_state[0], b.b_state[0]);
        }
    }
}
