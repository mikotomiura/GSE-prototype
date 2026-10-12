//! EH3 の招待の契機の値を、手元の記録で比べる道具（配布ビルドには入らない）。
//!
//! `cargo run --example` でしか動かず、`cargo build --release` にも tauri のバンドルにも含まれない。
//! 計器ではない（`.steering/20261012-eh3-trigger-values/`）。
//!
//! ## 何を数えるか
//!
//! NDJSON の `feat` 行（`t`・`p_stuck`・`p_flow`・`p_inc`）と `key` 行（`t`・`press`）だけを読み、
//! 閾値 × 継続の格子ごとに、本番と同じ状態機械（`analysis::invitation::InvitationMachine`）を
//! `feat` 行 1 行を 1 tick として回す。判定の規則は書き直さない（1 区間 1 回・60 秒で区間を閉じる・
//! 離席候補 180 秒の除外は状態機械がそのまま持つ）。
//!
//! - 契機: `TickOutput::triggered`（出したかどうかに依らない）。作業時間 1 時間あたりで出す。
//! - 提示: 本人の設定の既定（終日・上限 2）での `presented`。
//! - 作業時間: 最後の打鍵から 180 秒未満の `feat` 行の時間（次の行までの間・1 行 1 秒まで）。
//! - 停滞らしさ: 契機の直前の継続の窓で、`p_stuck` が 3 状態の最大だった行の割合と、窓の中の `p_stuck` の最大値。
//!
//! 各ファイルの `feat` 行は時刻が狭義単調でなければならず、ファイルどうしで同じ時刻の行があってもいけない
//! （どちらも並べ替えると実際と違う時系列になるので、黙って直さずに止める）。
//! 渡したファイルはすべて 1 本の時系列に並べて 1 つの状態機械で回す（O1 は起動したまま日次でファイルを
//! 替えるので、ファイルの境目で上限や間隔を数え直さない）。殻（`lib.rs` の `InvitationRunner`）と同じく、
//! `feat` 行が 30 秒以上空いたらセッションの区切りとし、現地の日（4:00 区切り）が変わったら区切る。
//!
//! 殻と違うところ（数の読み方に関わる）:
//! - 記録の一時停止は再現しない（O1 の記録には一時停止の区間が残らず、止めていた区間は `feat` 行の欠けと
//!   して区切りになる）。再開の後 30 秒の停滞の無効化も再現しない。
//! - 割り当て済みの日かどうか（期間の中か・台帳）は見ない（`research_enabled` は常に真）。提示の数は上限め。
//! - 記録の `p_stuck` は小数 4 桁に丸めてある（`logger.rs`）。閾値ちょうどの比較（`≥`）では、丸める前に
//!   閾値をわずかに下回った値（例: 0.49996）を道具だけが届いたと数える。向きは多め側だけで、量は小さい。
//!
//! ⚠️ 打鍵の内容は読まない（`key` 行は時刻と押下だけを使う）。結果は集計の数だけを stdout に出す。
//! NDJSON の生ログと出力の行ごとの値を外部の LLM に送らない（`data-privacy`）。
//!
//! ## 使い方
//!
//! ```text
//! cd src-tauri
//! cargo run --example invitation_trigger_sweep -- [--utc-offset-secs 32400] <a.ndjson> [b.ndjson ...]
//! ```

use std::fs::File;
use std::io::{BufRead, BufReader, Write};

type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;

use gse_next_lib::analysis::intervention::AWAY_IDLE_MS;
use gse_next_lib::analysis::invitation::{InvitationMachine, Settings, TickInput, Trigger};
use gse_next_lib::eh3::{local_day, local_minute_of_day};

const THRESHOLDS: [f64; 3] = [0.50, 0.55, 0.60];
const HOLDS_SEC: [u64; 4] = [10, 15, 20, 30];
/// 殻の `InvitationRunner::GAP_AS_BOUNDARY_MS` と同じ。
const GAP_AS_BOUNDARY_MS: u64 = 30_000;
/// 停滞らしさの目安（本番の閾値）。
const MAIN_P: f64 = 0.60;

/// 1 tick の材料。
#[derive(Clone, Copy)]
struct Row {
    t: u64,
    p_stuck: f64,
    stuck_is_max: bool,
    /// 最後の打鍵（押下）の時刻。
    last_press: Option<u64>,
    /// 前の行から 30 秒以上空いた（または時計が戻った）。最初の行は偽。
    after_gap: bool,
}

/// 1 本のファイルから `feat` 行（時刻・確率）と打鍵の押下の時刻を読む。
fn load(path: &str, feats: &mut Vec<(u64, f64, bool)>, presses: &mut Vec<u64>) -> Result<()> {
    let reader = BufReader::new(File::open(path)?);
    let mut prev_feat: Option<u64> = None;
    for line in reader.lines() {
        let line = line?;
        let Ok(v) = serde_json::from_str::<serde_json::Value>(&line) else {
            continue;
        };
        let Some(t) = v.get("t").and_then(|x| x.as_u64()) else {
            continue;
        };
        match v.get("type").and_then(|x| x.as_str()) {
            Some("key") => {
                if v.get("press").and_then(|x| x.as_bool()) == Some(true) {
                    presses.push(t);
                }
            }
            Some("feat") => {
                let f = |k: &str| v.get(k).and_then(|x| x.as_f64()).unwrap_or(0.0);
                let (ps, pf, pi) = (f("p_stuck"), f("p_flow"), f("p_inc"));
                // 時計の戻り・同じ時刻の行は、並べ替えると実際と違う時系列になるので受け付けない
                if prev_feat.is_some_and(|q| t <= q) {
                    return Err(
                        format!("{path}: feat rows are not strictly increasing in t").into(),
                    );
                }
                prev_feat = Some(t);
                feats.push((t, ps, ps >= pf && ps >= pi));
            }
            _ => {}
        }
    }
    Ok(())
}

/// すべてのファイルを 1 本の時系列に並べる。O1 は起動したまま日次でファイルを替えるので、
/// ファイルの境目では状態機械を作り直さない（区切りは殻と同じく `feat` の欠けと日の変わり目だけ）。
fn timeline(paths: &[String]) -> Result<Vec<Row>> {
    let (mut feats, mut presses) = (Vec::new(), Vec::new());
    for p in paths {
        load(p, &mut feats, &mut presses)?;
    }
    // ファイルどうしは並べ替えて繋ぐ（各ファイルの中は狭義単調を確かめてある）。
    // 重なるファイル（同じ時刻の行が 2 本ある）は、どちらを採るかで数が変わるので受け付けない。
    feats.sort_by_key(|f| f.0);
    if feats.windows(2).any(|w| w[0].0 == w[1].0) {
        return Err("input files overlap (same feat timestamp in two files)".into());
    }
    presses.sort_unstable();
    let mut rows = Vec::with_capacity(feats.len());
    let mut k = 0;
    let mut last_press = None;
    let mut prev: Option<u64> = None;
    for (t, ps, is_max) in feats {
        while k < presses.len() && presses[k] <= t {
            last_press = Some(presses[k]);
            k += 1;
        }
        let after_gap = prev.is_some_and(|q| t - q >= GAP_AS_BOUNDARY_MS);
        prev = Some(t);
        rows.push(Row {
            t,
            p_stuck: ps,
            stuck_is_max: is_max,
            last_press,
            after_gap,
        });
    }
    Ok(rows)
}

#[derive(Default)]
struct Tally {
    work_ms: u64,
    triggers: u64,
    presented: u64,
    /// 契機の窓で `p_stuck` が 3 状態の最大だった行の割合の和（契機ごと）。
    stuck_max_share_sum: f64,
    /// 契機の窓の `p_stuck` の最大値が本番の閾値に届かなかった契機。
    below_main: u64,
    days_with_work: std::collections::BTreeSet<i64>,
    days_presented: std::collections::BTreeSet<i64>,
}

fn sweep(rows: &[Row], trigger: Trigger, offset: i32) -> Tally {
    let mut tally = Tally::default();
    let mut m = InvitationMachine::with_trigger(trigger);
    let mut last_day: Option<i64> = None;
    let mut seg_start = 0;
    for (i, r) in rows.iter().enumerate() {
        let day = local_day(r.t, offset);
        let idle_ms = r.last_press.map_or(u64::MAX, |p| r.t.saturating_sub(p));
        if idle_ms < AWAY_IDLE_MS {
            // 作業時間は時刻で数える（次の行までの間、ただし 1 行 1 秒まで）
            let dt = rows.get(i + 1).map_or(1000, |n| (n.t - r.t).min(1000));
            tally.work_ms += dt;
            tally.days_with_work.insert(day);
        }
        let boundary = r.after_gap || last_day.is_some_and(|d| d != day);
        if boundary {
            seg_start = i;
        }
        last_day = Some(day);
        let out = m.tick(&TickInput {
            now_ms: r.t,
            local_day: day,
            minute_of_day: local_minute_of_day(r.t, offset),
            p_stuck: r.p_stuck,
            idle_ms,
            research_enabled: true,
            recording_active: true,
            settings: Settings::default(),
            session_boundary: boundary,
        });
        if out.triggered {
            tally.triggers += 1;
            // 契機の直前の継続の窓（時刻で切り、区切りの前の行を入れない）
            let from = r.t.saturating_sub(trigger.hold_ms);
            let window: Vec<&Row> = rows[seg_start..=i].iter().filter(|w| w.t >= from).collect();
            let share =
                window.iter().filter(|w| w.stuck_is_max).count() as f64 / window.len() as f64;
            tally.stuck_max_share_sum += share;
            let peak = window.iter().map(|w| w.p_stuck).fold(0.0, f64::max);
            if peak < MAIN_P {
                tally.below_main += 1;
            }
        }
        if out.presented {
            tally.presented += 1;
            tally.days_presented.insert(day);
        }
    }
    tally
}

fn main() -> Result<()> {
    let mut offset: i32 = 9 * 3600;
    let mut paths = Vec::new();
    let mut args = std::env::args().skip(1);
    while let Some(a) = args.next() {
        if a == "--utc-offset-secs" {
            offset = args
                .next()
                .ok_or("--utc-offset-secs needs a value")?
                .parse()?;
        } else {
            paths.push(a);
        }
    }
    if paths.is_empty() {
        return Err("usage: invitation_trigger_sweep [--utc-offset-secs N] <a.ndjson> ...".into());
    }
    let rows = timeline(&paths)?;

    let stdout = std::io::stdout();
    let mut out = stdout.lock();
    writeln!(
        out,
        "threshold\thold_s\twork_h\ttriggers\ttriggers_per_work_h\tpresented_default\twork_days\tdays_presented\tstuck_max_share\tpeak_below_0.60"
    )?;
    for &p in &THRESHOLDS {
        for &h in &HOLDS_SEC {
            let t = sweep(
                &rows,
                Trigger {
                    p_stuck: p,
                    hold_ms: h * 1000,
                },
                offset,
            );
            let work_h = t.work_ms as f64 / 3_600_000.0;
            let per_h = if work_h > 0.0 {
                t.triggers as f64 / work_h
            } else {
                0.0
            };
            let share = if t.triggers > 0 {
                t.stuck_max_share_sum / t.triggers as f64
            } else {
                0.0
            };
            writeln!(
                out,
                "{p:.2}\t{h}\t{work_h:.2}\t{}\t{per_h:.2}\t{}\t{}\t{}\t{share:.2}\t{}",
                t.triggers,
                t.presented,
                t.days_with_work.len(),
                t.days_presented.len(),
                t.below_main
            )?;
        }
    }
    Ok(())
}
