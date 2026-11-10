//! 通常のモード（EH3・O1・G1 でない走行）の招待の契機の設定と、招待を許す条件（ADR-040 D4・タスク B）。
//!
//! 設計は `.steering/20261101-invitation-wiring/design.md` §2・§3。契機の種類と判定は
//! `analysis::invitation`（純ロジック）にあり、ここは設定ファイルの IO と「許すか」の純関数だけを持つ。
//!
//! - 設定ファイル: `~/.gse/invitation_trigger.json`（研究者が置く・本人の画面には出さない）。中身は
//!   [`TriggerKind`] の JSON 1 つ。
//!   - 無い → 推定器の既定（[`Trigger::MAIN`]・今の挙動）。
//!   - あるのに読めない・未知の欄・値の欠け・範囲外 → **通常のモードの招待を出さない**（fail-closed）。
//! - EH3 はこのファイルを読まない（`eh3::TriggerStage` のまま・EH3 の挙動は変わらない）。
//! - ⚠️ 値は applog に書かない（警告は「読めなかった」とだけ）。

use std::path::{Path, PathBuf};

use crate::analysis::invitation::TriggerKind;

/// 契機の設定のファイル名（`~/.gse/invitation_trigger.json`）。
pub const TRIGGER_FILE_NAME: &str = "invitation_trigger.json";

/// 契機の設定の置き場。
pub fn trigger_path() -> Option<PathBuf> {
    crate::submission::home_dir().map(|h| h.join(".gse").join(TRIGGER_FILE_NAME))
}

/// 設定ファイルを読んだ結果。
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum TriggerConfig {
    /// 使う契機（無いファイルは推定器の既定）。
    Kind(TriggerKind),
    /// 読めない・範囲外。通常のモードの招待を出さない。
    Invalid,
}

impl TriggerConfig {
    /// 招待を出してよい設定か。
    pub fn usable(self) -> Option<TriggerKind> {
        match self {
            TriggerConfig::Kind(k) => Some(k),
            TriggerConfig::Invalid => None,
        }
    }
}

/// 設定ファイルの大きさの上限（64 KiB）。
pub const MAX_CONFIG_BYTES: u64 = 64 * 1024;

/// 設定ファイルを安全に読む。無ければ `Ok(None)`。
///
/// 通常のファイルだけを受ける（symlink・ディレクトリ・特殊ファイルは `Err`）。上限を超えたら `Err`
/// （`take` で上限までしか読まない）。
pub fn read_config_text(path: &Path) -> std::io::Result<Option<String>> {
    use std::io::Read;
    let meta = match std::fs::symlink_metadata(path) {
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(None),
        Err(e) => return Err(e),
        Ok(m) => m,
    };
    if !meta.file_type().is_file() || meta.len() > MAX_CONFIG_BYTES {
        return Err(std::io::Error::other("not a regular file or too large"));
    }
    let file = std::fs::File::open(path)?;
    let mut text = String::new();
    file.take(MAX_CONFIG_BYTES + 1).read_to_string(&mut text)?;
    if text.len() as u64 > MAX_CONFIG_BYTES {
        return Err(std::io::Error::other("too large"));
    }
    Ok(Some(text))
}

/// 設定ファイルを読む。
pub fn load_trigger_config(path: &Path) -> TriggerConfig {
    match read_config_text(path) {
        Ok(None) => TriggerConfig::Kind(TriggerKind::default()),
        Ok(Some(t)) => match TriggerKind::from_json(&t) {
            Some(k) => TriggerConfig::Kind(k),
            None => {
                tracing::warn!("invitation trigger config is unreadable; invitations are off");
                TriggerConfig::Invalid
            }
        },
        Err(_) => {
            tracing::warn!("invitation trigger config is unreadable; invitations are off");
            TriggerConfig::Invalid
        }
    }
}

/// 起動後に 1 回だけ読む（セッションの宣言の行と状態機械が同じ値を使う）。
///
/// ホームが解決できないときは `Invalid`（無いのか読めないのか分からないので出さない側）。
pub fn process_config() -> TriggerConfig {
    static CONFIG: std::sync::OnceLock<TriggerConfig> = std::sync::OnceLock::new();
    *CONFIG.get_or_init(|| match trigger_path() {
        Some(p) => load_trigger_config(&p),
        None => {
            tracing::warn!("invitation trigger config path is unavailable; invitations are off");
            TriggerConfig::Invalid
        }
    })
}

/// 通常のモードで招待を許すか（純関数）。
///
/// 真になるのは、セッションの宣言が真で、O1・G1・EH3 のどれでもなく、設定ファイルが読めたときだけ。
/// 第 1 週（宣言が偽）・O1・G1 では偽。EH3 は別の経路（`eh3::assignment`）なので、ここでは常に偽。
pub fn normal_invitation_allowed(
    declared: bool,
    o1: bool,
    g1: bool,
    eh3: bool,
    config: TriggerConfig,
) -> bool {
    declared && !o1 && !g1 && !eh3 && config.usable().is_some()
}

/// 記録から組んだ 1 tick（`feat` 行 1 行 = 1 tick）。
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct RecordedTick {
    /// `feat` 行の時刻（epoch ms）。
    pub t: u64,
    pub p_stuck: f64,
    /// この時刻までの最後の打鍵（押下）の時刻。
    pub last_press: Option<u64>,
}

/// 記録から契機を再現した結果（時刻は epoch ms）。
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct RecordedRun {
    /// 契機が立った時刻（出したかどうかに依らない）。
    pub triggered: Vec<u64>,
    /// 出した時刻（本人の設定の既定・終日・上限 2）。
    pub presented: Vec<u64>,
}

/// `feat` 行の列（時刻の狭義単調）と打鍵の押下の時刻から tick を組む。
///
/// 打鍵は時刻だけを使う（本文は読まない）。組み方は `examples/invitation_trigger_sweep.rs` と同じ。
pub fn build_recorded_ticks(feats: &[(u64, f64)], presses: &[u64]) -> Vec<RecordedTick> {
    let mut presses = presses.to_vec();
    presses.sort_unstable();
    let mut k = 0;
    let mut last_press = None;
    feats
        .iter()
        .map(|&(t, p_stuck)| {
            while k < presses.len() && presses[k] <= t {
                last_press = Some(presses[k]);
                k += 1;
            }
            RecordedTick {
                t,
                p_stuck,
                last_press,
            }
        })
        .collect()
}

/// 記録の tick を、実機と同じ状態機械（`InvitationMachine`）で回して契機と提示の時刻を返す。
///
/// 殻（`lib.rs` の `InvitationRunner`）と同じく、`feat` 行が 30 秒以上空いたらセッションの区切りとし、
/// 現地の日（4:00 区切り）が変わったら区切る。記録の一時停止・割り当て済みの日の判定は再現しない
/// （研究の条件は常に真）。
///
/// 実機と一致しうる範囲（/cross-review 2 巡目）:
/// - 1 本の状態機械で記録の全期間を回す。実機は宣言（`record_session_meta`）のたびに状態機械を
///   作り直すので、一致するのは最初の宣言以降で、再宣言による数え直し（保持・上限）は再現しない。
///   記録の `invitation_condition` 行（`seed_effective`）で照合する。
/// - `random` の秒の引き直しは `feat` 行の tick でだけ起きる。実機は毎秒 tick し、離席候補の tick で
///   遡りの起点を捨てる。30 秒未満の `feat` 行の欠けが離席候補からの再開をまたぐと、引く秒の数が
///   実機と違いうる。
/// - 1 回の tick で遡った区間に当たりの秒が複数あっても、立つのは最初の 1 つだけ（実機も同じ）。
pub fn replay_recorded(
    ticks: &[RecordedTick],
    kind: TriggerKind,
    session_start_ms: u64,
    utc_offset_secs: i32,
) -> RecordedRun {
    use crate::analysis::invitation::{InvitationMachine, Settings, TickInput};
    // 殻の `InvitationRunner::GAP_AS_BOUNDARY_MS` と同じ。
    const GAP_AS_BOUNDARY_MS: u64 = 30_000;
    let mut m = InvitationMachine::with_kind_session(kind, session_start_ms);
    let mut run = RecordedRun::default();
    let mut prev: Option<u64> = None;
    let mut last_day: Option<i64> = None;
    for r in ticks {
        let day = crate::eh3::local_day(r.t, utc_offset_secs);
        let boundary = prev.is_some_and(|q| r.t.saturating_sub(q) >= GAP_AS_BOUNDARY_MS)
            || last_day.is_some_and(|d| d != day);
        prev = Some(r.t);
        last_day = Some(day);
        let out = m.tick(&TickInput {
            now_ms: r.t,
            local_day: day,
            minute_of_day: crate::eh3::local_minute_of_day(r.t, utc_offset_secs),
            p_stuck: r.p_stuck,
            idle_ms: r.last_press.map_or(u64::MAX, |p| r.t.saturating_sub(p)),
            research_enabled: true,
            recording_active: true,
            settings: Settings::default(),
            session_boundary: boundary,
        });
        if out.triggered {
            // 無作為で tick が欠けて複数の秒をまとめて引いたときは、立った秒を報告する
            // （毎秒 tick の実機と同じ時刻になる）
            let at = match m.random_fired_ms() {
                Some(ms) if ms / 1000 != r.t / 1000 => ms,
                _ => r.t,
            };
            run.triggered.push(at);
        }
        if out.presented {
            run.presented.push(r.t);
        }
    }
    run
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analysis::invitation::Trigger;

    fn write(dir: &Path, text: &str) -> PathBuf {
        let p = dir.join(TRIGGER_FILE_NAME);
        std::fs::write(&p, text).unwrap();
        p
    }

    fn tmp(name: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("gse-inv-trigger-{name}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    #[test]
    fn missing_file_is_the_estimator_default() {
        let d = tmp("missing");
        assert_eq!(
            load_trigger_config(&d.join(TRIGGER_FILE_NAME)),
            TriggerConfig::Kind(Trigger::MAIN.into())
        );
    }

    #[test]
    fn valid_file_is_read() {
        let d = tmp("valid");
        let p = write(&d, r#"{"kind":"random","per_active_hour":3,"seed":9}"#);
        assert_eq!(
            load_trigger_config(&p),
            TriggerConfig::Kind(TriggerKind::Random {
                per_active_hour: 3.0,
                seed: 9
            })
        );
        let p = write(&d, r#"{"kind":"none"}"#);
        assert_eq!(
            load_trigger_config(&p),
            TriggerConfig::Kind(TriggerKind::Off {})
        );
    }

    #[test]
    fn broken_unknown_missing_or_out_of_range_files_fail_closed() {
        let d = tmp("bad");
        for bad in [
            "",
            "{",
            r#"{"kind":"rising"}"#,
            r#"{"kind":"rising","delta":0.2}"#,
            r#"{"kind":"random","seed":1}"#,
            r#"{"kind":"random","per_active_hour":6}"#,
            r#"{"kind":"none","x":1}"#,
            r#"{"kind":"rising","delta":-1,"window_ms":10}"#,
            r#"{"kind":"random","per_active_hour":100,"seed":1}"#,
        ] {
            let p = write(&d, bad);
            assert_eq!(load_trigger_config(&p), TriggerConfig::Invalid, "{bad:?}");
        }
        // 読めない（ファイルでなくディレクトリ）
        let sub = d.join("dir");
        std::fs::create_dir_all(&sub).unwrap();
        assert_eq!(load_trigger_config(&sub), TriggerConfig::Invalid);
    }

    #[test]
    fn normal_invitation_gate() {
        let ok = TriggerConfig::Kind(TriggerKind::default());
        assert!(normal_invitation_allowed(true, false, false, false, ok));
        // 第 1 週（宣言が偽）
        assert!(!normal_invitation_allowed(false, false, false, false, ok));
        // O1・G1・EH3 では偽
        assert!(!normal_invitation_allowed(true, true, false, false, ok));
        assert!(!normal_invitation_allowed(true, false, true, false, ok));
        assert!(!normal_invitation_allowed(true, false, false, true, ok));
        // 設定が読めない
        assert!(!normal_invitation_allowed(
            true,
            false,
            false,
            false,
            TriggerConfig::Invalid
        ));
        // 「なし」は読めた設定なので許す（統制の条件。契機が立たないだけ）
        assert!(normal_invitation_allowed(
            true,
            false,
            false,
            false,
            TriggerConfig::Kind(TriggerKind::Off {})
        ));
    }

    const T0: u64 = 1_760_000_000_000;

    /// 1 秒 1 行の記録。`p` は経過秒 → p_stuck。打鍵は毎秒（離席候補にならない）。
    fn recorded(secs: u64, p: &dyn Fn(u64) -> f64) -> Vec<RecordedTick> {
        let feats: Vec<(u64, f64)> = (0..secs).map(|s| (T0 + s * 1000, p(s))).collect();
        let presses: Vec<u64> = (0..secs).map(|s| T0 + s * 1000).collect();
        build_recorded_ticks(&feats, &presses)
    }

    #[test]
    fn replay_estimator_matches_the_machine() {
        let ticks = recorded(120, &|s| if s >= 10 { 0.9 } else { 0.1 });
        let run = replay_recorded(&ticks, TriggerKind::default(), 0, 0);
        assert_eq!(run.triggered, vec![T0 + 40_000]);
        assert_eq!(run.presented, vec![T0 + 40_000]);
    }

    #[test]
    fn replay_off_and_random_and_rising() {
        let ticks = recorded(7200, &|s| if (s / 600) % 2 == 1 { 0.9 } else { 0.1 });
        assert!(replay_recorded(&ticks, TriggerKind::Off {}, 0, 0)
            .triggered
            .is_empty());
        let r = TriggerKind::Random {
            per_active_hour: 30.0,
            seed: 5,
        };
        let a = replay_recorded(&ticks, r, 0, 0);
        let b = replay_recorded(&ticks, r, 0, 0);
        assert_eq!(a, b, "seed から再現する");
        assert!(!a.triggered.is_empty());
        assert!(a.presented.len() <= 2, "既定の上限 2");
        let rising = TriggerKind::Rising {
            delta: 0.5,
            window_ms: 10_000,
        };
        let c = replay_recorded(&ticks, rising, 0, 0);
        // 600 秒ごとの 0.1 → 0.9 の立ち上がりで 1 回ずつ（窓 10 秒の中に収まる急な上がりは 1 つの立ち上がり）
        assert_eq!(c.triggered.len(), 6, "{:?}", c.triggered);
    }

    #[test]
    fn replay_gap_and_missing_press_block_triggers() {
        // 打鍵が無い記録は離席候補で、どの契機も立たない
        let feats: Vec<(u64, f64)> = (0..300).map(|s| (T0 + s * 1000, 0.9)).collect();
        let ticks = build_recorded_ticks(&feats, &[]);
        assert!(replay_recorded(&ticks, TriggerKind::default(), 0, 0)
            .triggered
            .is_empty());
        // 30 秒以上の欠けは区切り（区間が貯まらない）
        let feats: Vec<(u64, f64)> = (0..25)
            .map(|s| (T0 + s * 1000, 0.9))
            .chain((0..25).map(|s| (T0 + 100_000 + s * 1000, 0.9)))
            .collect();
        let presses: Vec<u64> = feats.iter().map(|f| f.0).collect();
        let ticks = build_recorded_ticks(&feats, &presses);
        assert!(replay_recorded(&ticks, TriggerKind::default(), 0, 0)
            .triggered
            .is_empty());
    }

    /// 実機を模した毎秒 tick(殻と同じ区切り: tick の間隔が 30 秒以上なら区切り)と、feat 行だけの replay が、
    /// feat 行の欠けを挟んでも同じ時刻で契機が立つ(無作為・離席候補の外)。
    #[test]
    fn random_replay_matches_a_per_second_live_simulation_across_feat_holes() {
        use crate::analysis::invitation::{InvitationMachine, Settings, TickInput};
        let kind = TriggerKind::Random {
            per_active_hour: 60.0,
            seed: 20261101,
        };
        let session_start = T0 + 5_000;
        // 打鍵は全期間で毎秒。feat 行は 600..606(短い欠け)と 1500..1560(30 秒以上の欠け)で欠ける
        let all: Vec<u64> = (0..3600).collect();
        let presses: Vec<u64> = all.iter().map(|s| T0 + s * 1000).collect();
        let feat_secs: Vec<u64> = all
            .iter()
            .copied()
            .filter(|s| !(600..606).contains(s) && !(1500..1560).contains(s))
            .collect();
        let feats: Vec<(u64, f64)> = feat_secs.iter().map(|s| (T0 + s * 1000, 0.1)).collect();
        let replayed = replay_recorded(
            &build_recorded_ticks(&feats, &presses),
            kind,
            session_start,
            0,
        );
        assert!(
            replayed.triggered.len() > 20,
            "{}",
            replayed.triggered.len()
        );

        // 実機: 短い欠け(600..606)は tick が続く。長い欠け(1500..1560)は分析が止まって tick が無い
        let mut m = InvitationMachine::with_kind_session(kind, session_start);
        let mut live = Vec::new();
        let mut prev: Option<u64> = None;
        for s in all.iter().copied().filter(|s| !(1500..1560).contains(s)) {
            let t = T0 + s * 1000;
            let boundary = prev.is_some_and(|q| t - q >= 30_000);
            prev = Some(t);
            let out = m.tick(&TickInput {
                now_ms: t,
                local_day: crate::eh3::local_day(t, 0),
                minute_of_day: crate::eh3::local_minute_of_day(t, 0),
                p_stuck: 0.1,
                idle_ms: 0,
                research_enabled: true,
                recording_active: true,
                settings: Settings::default(),
                session_boundary: boundary,
            });
            if out.triggered {
                live.push(t);
            }
        }
        assert_eq!(replayed.triggered, live);
    }

    #[test]
    fn config_reader_rejects_symlinks_and_oversize_files() {
        let d = tmp("limits");
        let big = d.join("big.json");
        std::fs::write(&big, vec![b' '; MAX_CONFIG_BYTES as usize + 1]).unwrap();
        assert_eq!(load_trigger_config(&big), TriggerConfig::Invalid);
        // 上限ちょうどの空白 + JSON は読める大きさ(中身が JSON として正しければ受ける)
        let ok = d.join("ok.json");
        let mut body = br#"{"kind":"none"}"#.to_vec();
        body.resize(MAX_CONFIG_BYTES as usize, b' ');
        std::fs::write(&ok, body).unwrap();
        assert_eq!(
            load_trigger_config(&ok),
            TriggerConfig::Kind(TriggerKind::Off {})
        );
        #[cfg(unix)]
        {
            let link = d.join("link.json");
            std::os::unix::fs::symlink(&ok, &link).unwrap();
            assert_eq!(load_trigger_config(&link), TriggerConfig::Invalid);
        }
        assert!(read_config_text(&d.join("none.json")).unwrap().is_none());
    }
}
