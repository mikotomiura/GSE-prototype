//! 手跡（段 1 の後期・ADR-051）の IO 層: 割付の表・`.sha256`・日の状態ファイル・切った印の読み書きと、
//! 入口の門の評価。純粋な部分は `analysis::handmark`。1a では `lib.rs` の本体に配線しない。
//!
//! ## 切った状態の保ち方（判断 1-6）
//!
//! 切るときは状態ファイルに `off = true` を書き、失敗したら `~/.gse/handmark_off_<day>`（空）を作る。
//! 起動では、状態ファイルと今日の印を読んだ後に状態ファイルへの書き込みを試し、書けなければその日は出さない。
//!
//! ⚠️ 残る穴: 切るときに状態ファイルと印の**両方**の書き込みが一時的に失敗し、強制終了の後の起動では
//! 書ける、という並びでは、その日は出てしまう（テストで「望ましい振る舞い」として縛らない）。
//! 採らなかった案（既定を「出さない」にして許可を書く）も穴は同じ。記録は `decisions.md`。

use std::io;
use std::path::{Path, PathBuf};

use crate::analysis::handmark::assignment::{
    draw_seed, load_from_bytes, Assigned, Table, TableLoad,
};
use crate::analysis::handmark::day::DayRecord;
use crate::analysis::handmark::gate::{decide, Decision, StateStatus};
use crate::logger::HandmarkDayRow;

pub const TABLE_FILE_NAME: &str = "handmark_assignment.json";
pub const SHA_FILE_NAME: &str = "handmark_assignment.sha256";
pub const STATE_FILE_NAME: &str = "handmark_day_state.json";
pub const TABLE_ENV_VAR: &str = "GSE_HANDMARK_TABLE";

/// 読んだ結果。
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ReadResult {
    Missing,
    Bytes(Vec<u8>),
    Unreadable,
}

/// ファイルの口。テストで障害を注入できるように差し替えられる。
pub trait HandmarkFs {
    fn read_table(&self) -> ReadResult;
    fn read_sha(&self) -> ReadResult;
    fn read_state(&self) -> ReadResult;
    fn write_state(&self, bytes: &[u8]) -> io::Result<()>;
    fn mark_exists(&self, day: i64) -> bool;
    fn write_mark(&self, day: i64) -> io::Result<()>;
    fn remove_mark(&self, day: i64) -> io::Result<()>;
}

/// 表と `.sha256` の置き場（純関数）。`env` が空でなければそれ（SHA-256 は同じ名前で拡張子を替える）、
/// なければ `s1.mode` の印と同じフォルダ。
pub fn table_paths(env: Option<&str>, marker: Option<&Path>) -> Option<(PathBuf, PathBuf)> {
    if let Some(e) = env.filter(|e| !e.is_empty()) {
        let t = PathBuf::from(e);
        let sha = t.with_extension("sha256");
        return Some((t, sha));
    }
    let dir = marker?.parent()?.to_path_buf();
    Some((dir.join(TABLE_FILE_NAME), dir.join(SHA_FILE_NAME)))
}

/// 実ファイル。
pub struct DiskFs {
    pub table: PathBuf,
    pub sha: PathBuf,
    pub state: PathBuf,
    /// 印を置くフォルダ（`~/.gse`）。
    pub mark_dir: PathBuf,
}

impl DiskFs {
    /// 配布形（`exe` から `s1.mode` の隣）か環境変数の表で作る。ホームが分からなければ `None`。
    pub fn from_env(exe: &Path) -> Option<Self> {
        let marker = crate::s1::marker_path_for(exe, crate::g1::exe_to_folder_levels());
        let env = std::env::var(TABLE_ENV_VAR).ok();
        let (table, sha) = table_paths(env.as_deref(), marker.as_deref())?;
        let gse = crate::submission::home_dir()?.join(".gse");
        Some(Self {
            table,
            sha,
            state: gse.join(STATE_FILE_NAME),
            mark_dir: gse,
        })
    }

    fn mark_path(&self, day: i64) -> PathBuf {
        self.mark_dir.join(format!("handmark_off_{day}"))
    }
}

fn read_file(p: &Path) -> ReadResult {
    match std::fs::read(p) {
        Ok(b) => ReadResult::Bytes(b),
        Err(e) if e.kind() == io::ErrorKind::NotFound => ReadResult::Missing,
        Err(_) => ReadResult::Unreadable,
    }
}

/// 一時ファイルに書いてから置き換える（`s1_day_state::save` と同じ作法）。
pub fn write_atomic(path: &Path, bytes: &[u8]) -> io::Result<()> {
    if let Some(dir) = path.parent() {
        std::fs::create_dir_all(dir)?;
    }
    let tmp = path.with_extension("json.tmp");
    {
        use std::io::Write;
        let mut f = std::fs::File::create(&tmp)?;
        f.write_all(bytes)?;
        f.sync_all()?;
    }
    if let Err(e) = std::fs::rename(&tmp, path) {
        let _ = std::fs::remove_file(&tmp);
        return Err(e);
    }
    Ok(())
}

impl HandmarkFs for DiskFs {
    fn read_table(&self) -> ReadResult {
        read_file(&self.table)
    }
    fn read_sha(&self) -> ReadResult {
        read_file(&self.sha)
    }
    fn read_state(&self) -> ReadResult {
        read_file(&self.state)
    }
    fn write_state(&self, bytes: &[u8]) -> io::Result<()> {
        write_atomic(&self.state, bytes)
    }
    fn mark_exists(&self, day: i64) -> bool {
        self.mark_path(day).exists()
    }
    fn write_mark(&self, day: i64) -> io::Result<()> {
        std::fs::create_dir_all(&self.mark_dir)?;
        std::fs::File::create(self.mark_path(day))?.sync_all()
    }
    fn remove_mark(&self, day: i64) -> io::Result<()> {
        match std::fs::remove_file(self.mark_path(day)) {
            Err(e) if e.kind() != io::ErrorKind::NotFound => Err(e),
            _ => Ok(()),
        }
    }
}

/// 状態ファイルを読んだ結果。
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DayLoad {
    Fresh,
    Loaded(DayRecord),
    Broken,
}

pub fn parse_state(r: &ReadResult) -> DayLoad {
    match r {
        ReadResult::Missing => DayLoad::Fresh,
        ReadResult::Unreadable => DayLoad::Broken,
        ReadResult::Bytes(b) => match serde_json::from_slice::<DayRecord>(b) {
            Ok(rec) if rec.is_valid() => DayLoad::Loaded(rec),
            _ => DayLoad::Broken,
        },
    }
}

fn load_table(fs: &dyn HandmarkFs) -> TableLoad {
    let table = match fs.read_table() {
        ReadResult::Missing => return TableLoad::Missing,
        ReadResult::Unreadable => return TableLoad::Broken,
        ReadResult::Bytes(b) => b,
    };
    let sha = match fs.read_sha() {
        ReadResult::Missing => None,
        // 読めない `.sha256` は照合できない（一致しない側に倒す）
        ReadResult::Unreadable => Some(String::from("unreadable")),
        ReadResult::Bytes(b) => Some(String::from_utf8_lossy(&b).into_owned()),
    };
    load_from_bytes(Some(&table), sha.as_deref())
}

/// 門の評価の結果と、その日の累計。
#[derive(Debug, Clone)]
pub struct Evaluation {
    pub decision: Decision,
    /// 状態ファイルが壊れているときは `None`（この走行では出さない）。
    pub record: Option<DayRecord>,
    pub table: Option<Table>,
    pub table_sha256: Option<String>,
    pub today: i64,
}

impl Evaluation {
    /// 評価する。`prior` は走行中の累計（検め直しで状態ファイルを読み直して量が戻らないようにする）。
    /// `prior` が無い（起動）か日が変わったときは、状態ファイルへの書き込みを試す。
    pub fn run(fs: &dyn HandmarkFs, s1_mode: bool, today: i64, prior: Option<DayRecord>) -> Self {
        let table_load = load_table(fs);
        let (table, sha) = match &table_load {
            TableLoad::Ok { table, sha256 } => (Some(table.clone()), Some(sha256.clone())),
            _ => (None, None),
        };
        let had_prior = prior.is_some();
        let mut record = match prior {
            Some(r) => Some(r),
            None => match parse_state(&fs.read_state()) {
                DayLoad::Fresh => Some(DayRecord::new(today)),
                DayLoad::Loaded(r) => Some(r),
                DayLoad::Broken => None,
            },
        };
        let mut state = StateStatus::Broken;
        let mut rolled = false;
        if let Some(r) = record.as_mut() {
            rolled = r.roll_to(today);
            state = StateStatus::Ok;
            if !had_prior || rolled {
                // 読んだ中身（日付を替えたもの）をそのまま書き直す
                if write_record(fs, r).is_err() {
                    state = StateStatus::Unwritable;
                }
            }
        }
        let _ = rolled;
        let off_today =
            fs.mark_exists(today) || record.as_ref().is_some_and(|r| r.off && r.day == today);
        let decision = decide(s1_mode, &table_load, today, state, off_today);
        Self {
            decision,
            record,
            table,
            table_sha256: sha,
            today,
        }
    }

    pub fn is_open(&self) -> bool {
        self.decision.is_open()
    }

    /// 出ていた時間を足す（開いているときだけ呼ぶ）。
    pub fn add_shown(&mut self, ms: u64) {
        if let Some(r) = self.record.as_mut() {
            r.add_shown(ms);
        }
    }

    /// 手跡を出し始めた時刻を足す。
    pub fn note_stage_start(&mut self, t: u64) {
        if let Some(r) = self.record.as_mut() {
            r.note_stage_start(t);
        }
    }

    /// 累計を状態ファイルに書く。
    pub fn save(&self, fs: &dyn HandmarkFs) -> io::Result<()> {
        match &self.record {
            Some(r) => write_record(fs, r),
            None => Err(io::Error::other("state is broken")),
        }
    }

    /// 描画の種（表が読めたときだけ）。
    pub fn draw_seed(&self) -> Option<u64> {
        self.table_sha256
            .as_deref()
            .map(|sha| draw_seed(sha, self.today))
    }

    /// `handmark_day` の行（段 1 のモードでなければ書かない）。
    pub fn row(&self, t_ms: u64) -> Option<HandmarkDayRow> {
        let (assigned, reason) = match self.decision {
            Decision::NotS1 => return None,
            Decision::Open { assigned } => (Some(assigned), None),
            Decision::Closed { reason, assigned } => (assigned, Some(reason.as_str())),
        };
        let assigned_str = assigned.map_or("unknown", Assigned::as_str);
        let rec = self.record.as_ref();
        Some(HandmarkDayRow {
            timestamp: t_ms,
            day: self.today,
            assigned: assigned_str,
            late_start_day: self.table.as_ref().map(|t| t.late_start_day),
            first_shown_day: rec.and_then(|r| r.first_shown_day),
            shown_ms: rec.map_or(0, |r| r.shown_ms),
            visible_ms: None,
            toggles: rec.map_or_else(Vec::new, |r| {
                r.toggles.iter().map(|t| (t.t, t.on)).collect()
            }),
            stage_starts: rec.map_or_else(Vec::new, |r| r.stage_starts.clone()),
            overflow: rec.is_some_and(|r| r.overflow),
            table_sha256: self.table_sha256.clone(),
            draw_seed: self.draw_seed(),
            reason,
        })
    }
}

fn write_record(fs: &dyn HandmarkFs, r: &DayRecord) -> io::Result<()> {
    let bytes = serde_json::to_vec(r).map_err(io::Error::other)?;
    fs.write_state(&bytes)
}

/// 切る／戻す操作の結果。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ToggleOutcome {
    /// 状態ファイルに書けた。
    State,
    /// 状態ファイルは失敗したが、印を作れた。
    MarkOnly,
    /// どちらも失敗した（この走行では出さない側に倒す）。
    NotPersisted,
}

/// 切る。走行中は必ず出さない側（メモリの `off`）に倒す。
pub fn turn_off(fs: &dyn HandmarkFs, ev: &mut Evaluation, now_ms: u64) -> ToggleOutcome {
    let Some(r) = ev.record.as_mut() else {
        // 状態ファイルが壊れていて累計が無い: 印だけ試す
        return if fs.write_mark(ev.today).is_ok() {
            ToggleOutcome::MarkOnly
        } else {
            ToggleOutcome::NotPersisted
        };
    };
    r.set_off(now_ms, true);
    if write_record(fs, r).is_ok() {
        return ToggleOutcome::State;
    }
    if fs.write_mark(ev.today).is_ok() {
        ToggleOutcome::MarkOnly
    } else {
        ToggleOutcome::NotPersisted
    }
}

/// 戻せなかった（出さないまま）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RestoreFailed;

/// 戻す。状態ファイルに書けて、印があれば消せたときだけ戻る。失敗したら出さないまま（`Err`）。
pub fn turn_on(fs: &dyn HandmarkFs, ev: &mut Evaluation, now_ms: u64) -> Result<(), RestoreFailed> {
    let Some(r) = ev.record.as_mut() else {
        return Err(RestoreFailed);
    };
    let prev = r.clone();
    r.set_off(now_ms, false);
    if write_record(fs, r).is_err() || fs.remove_mark(ev.today).is_err() {
        *r = prev;
        r.off = true;
        return Err(RestoreFailed);
    }
    Ok(())
}

// 記録の検査（テストだけ・ADR-050 D3 のうち PR 1 の行）。
#[cfg(test)]
#[path = "handmark_guard.rs"]
mod guard;

#[cfg(test)]
pub(crate) mod testfs {
    use super::*;
    use std::cell::{Cell, RefCell};

    /// メモリ上のファイル。書き込みの失敗を注入できる。
    #[derive(Default)]
    pub struct MemFs {
        pub table: RefCell<Option<Vec<u8>>>,
        pub sha: RefCell<Option<Vec<u8>>>,
        pub state: RefCell<Option<Vec<u8>>>,
        pub marks: RefCell<Vec<i64>>,
        pub fail_state_write: Cell<bool>,
        pub fail_mark_write: Cell<bool>,
        pub fail_mark_remove: Cell<bool>,
    }

    fn rr(v: &RefCell<Option<Vec<u8>>>) -> ReadResult {
        v.borrow()
            .clone()
            .map_or(ReadResult::Missing, ReadResult::Bytes)
    }

    impl HandmarkFs for MemFs {
        fn read_table(&self) -> ReadResult {
            rr(&self.table)
        }
        fn read_sha(&self) -> ReadResult {
            rr(&self.sha)
        }
        fn read_state(&self) -> ReadResult {
            rr(&self.state)
        }
        fn write_state(&self, bytes: &[u8]) -> io::Result<()> {
            if self.fail_state_write.get() {
                return Err(io::Error::other("injected"));
            }
            *self.state.borrow_mut() = Some(bytes.to_vec());
            Ok(())
        }
        fn mark_exists(&self, day: i64) -> bool {
            self.marks.borrow().contains(&day)
        }
        fn write_mark(&self, day: i64) -> io::Result<()> {
            if self.fail_mark_write.get() {
                return Err(io::Error::other("injected"));
            }
            self.marks.borrow_mut().push(day);
            Ok(())
        }
        fn remove_mark(&self, day: i64) -> io::Result<()> {
            if self.fail_mark_remove.get() {
                return Err(io::Error::other("injected"));
            }
            self.marks.borrow_mut().retain(|d| *d != day);
            Ok(())
        }
    }

    /// 後期の初日が 20410、続く日が [on, off, off, on] の表を置く。
    pub fn with_table() -> MemFs {
        let t = Table {
            version: 1,
            s1_start_day: 20_400,
            early_days: 10,
            late_start_day: 20_410,
            days: vec![true, false, false, true],
        };
        let bytes = t.canonical_bytes();
        let fs = MemFs::default();
        *fs.sha.borrow_mut() = Some(
            format!(
                "{}  {TABLE_FILE_NAME}\n",
                crate::analysis::handmark::assignment::sha256_hex(&bytes)
            )
            .into_bytes(),
        );
        *fs.table.borrow_mut() = Some(bytes);
        fs
    }
}

#[cfg(test)]
mod tests {
    use super::testfs::*;
    use super::*;
    use crate::analysis::handmark::gate::{needs_recheck, CloseReason, RECHECK_MS};

    const LATE_FIRST: i64 = 20_410;
    const ON_DAY: i64 = 20_411;

    fn reason(ev: &Evaluation) -> Option<CloseReason> {
        match ev.decision {
            Decision::Closed { reason, .. } => Some(reason),
            _ => None,
        }
    }

    #[test]
    fn table_paths_prefers_env_and_falls_back_to_the_marker_folder() {
        let (t, s) = table_paths(Some("/x/y/t.json"), None).unwrap();
        assert_eq!(t, PathBuf::from("/x/y/t.json"));
        assert_eq!(s, PathBuf::from("/x/y/t.sha256"));
        let (t, s) = table_paths(None, Some(Path::new("/dist/s1.mode"))).unwrap();
        assert_eq!(t, PathBuf::from("/dist/handmark_assignment.json"));
        assert_eq!(s, PathBuf::from("/dist/handmark_assignment.sha256"));
        assert!(table_paths(Some(""), None).is_none());
        assert!(table_paths(None, None).is_none());
    }

    #[test]
    fn closed_reasons_are_recorded_for_each_failure() {
        let fs = MemFs::default();
        assert_eq!(
            reason(&Evaluation::run(&fs, true, ON_DAY, None)),
            Some(CloseReason::TableMissing)
        );
        let fs = with_table();
        *fs.table.borrow_mut() = Some(b"{broken".to_vec());
        assert_eq!(
            reason(&Evaluation::run(&fs, true, ON_DAY, None)),
            Some(CloseReason::TableBroken)
        );
        let fs = with_table();
        *fs.sha.borrow_mut() = None;
        assert_eq!(
            reason(&Evaluation::run(&fs, true, ON_DAY, None)),
            Some(CloseReason::ShaMissing)
        );
        let fs = with_table();
        *fs.sha.borrow_mut() = Some(format!("{}\n", "0".repeat(64)).into_bytes());
        assert_eq!(
            reason(&Evaluation::run(&fs, true, ON_DAY, None)),
            Some(CloseReason::ShaMismatch)
        );
        let fs = with_table();
        *fs.state.borrow_mut() = Some(b"{not json".to_vec());
        assert_eq!(
            reason(&Evaluation::run(&fs, true, ON_DAY, None)),
            Some(CloseReason::StateBroken)
        );
        let fs = with_table();
        fs.fail_state_write.set(true);
        assert_eq!(
            reason(&Evaluation::run(&fs, true, ON_DAY, None)),
            Some(CloseReason::StateUnwritable)
        );
        // 段 1 でなければ門は NotS1 で行も無い
        let fs = with_table();
        let ev = Evaluation::run(&fs, false, ON_DAY, None);
        assert_eq!(ev.decision, Decision::NotS1);
        assert!(ev.row(1).is_none());
        // 開く
        let fs = with_table();
        assert!(Evaluation::run(&fs, true, LATE_FIRST, None).is_open());
        assert!(Evaluation::run(&fs, true, ON_DAY, None).is_open());
        assert_eq!(
            reason(&Evaluation::run(&fs, true, ON_DAY + 1, None)),
            Some(CloseReason::AssignedOff)
        );
        assert_eq!(
            reason(&Evaluation::run(&fs, true, LATE_FIRST - 1, None)),
            Some(CloseReason::BeforeLate)
        );
        assert_eq!(
            reason(&Evaluation::run(&fs, true, LATE_FIRST + 9, None)),
            Some(CloseReason::AfterTable)
        );
    }

    #[test]
    fn deleting_the_table_after_opening_closes_at_the_next_recheck() {
        let fs = with_table();
        let t0 = 1_000_000u64;
        let ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert!(ev.is_open());
        *fs.table.borrow_mut() = None;
        // 60 秒たたないうちは検め直さない
        assert!(!needs_recheck(t0, ON_DAY, t0 + RECHECK_MS - 1, ON_DAY));
        assert!(needs_recheck(t0, ON_DAY, t0 + RECHECK_MS, ON_DAY));
        let ev2 = Evaluation::run(&fs, true, ON_DAY, ev.record.clone());
        assert_eq!(reason(&ev2), Some(CloseReason::TableMissing));
    }

    #[test]
    fn rewriting_the_sha_file_closes_the_gate() {
        let fs = with_table();
        let ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert!(ev.is_open());
        *fs.sha.borrow_mut() = Some(format!("{}\n", "f".repeat(64)).into_bytes());
        let ev2 = Evaluation::run(&fs, true, ON_DAY, ev.record.clone());
        assert_eq!(reason(&ev2), Some(CloseReason::ShaMismatch));
    }

    /// 1: 出している → 切る（状態ファイルは失敗・印は成功）→ 落ちる → 同じ日に起動 → 出さない。
    #[test]
    fn off_survives_a_crash_when_only_the_mark_was_written() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert!(ev.is_open());
        fs.fail_state_write.set(true);
        assert_eq!(turn_off(&fs, &mut ev, 5_000), ToggleOutcome::MarkOnly);
        fs.fail_state_write.set(false);
        drop(ev); // 強制終了
        let ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert_eq!(reason(&ev), Some(CloseReason::OffToday));
    }

    /// 2: 両方失敗 → 落ちる → 同じ日に起動（まだ書けない）→ 出さない。
    #[test]
    fn off_with_both_writes_failing_still_stays_closed_while_unwritable() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        fs.fail_state_write.set(true);
        fs.fail_mark_write.set(true);
        assert_eq!(turn_off(&fs, &mut ev, 5_000), ToggleOutcome::NotPersisted);
        // この走行ではメモリの off が真（出さない側）
        assert!(ev.record.as_ref().unwrap().off);
        drop(ev);
        let ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert_eq!(reason(&ev), Some(CloseReason::StateUnwritable));
    }

    /// 3: 翌日に起動すると、割付どおりに戻る（前日の印は見ない）。
    #[test]
    fn next_day_returns_to_the_assignment() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        fs.fail_state_write.set(true);
        turn_off(&fs, &mut ev, 5_000);
        fs.fail_state_write.set(false);
        drop(ev);
        // 20413 は割付 on（days = [on, off, off, on] の 4 番目）
        let ev = Evaluation::run(&fs, true, 20_414, None);
        assert_eq!(
            ev.decision,
            Decision::Open {
                assigned: Assigned::On
            }
        );
        assert!(!ev.record.as_ref().unwrap().off);
    }

    #[test]
    fn turning_off_and_on_round_trips_and_a_failed_restore_stays_off() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert_eq!(turn_off(&fs, &mut ev, 1), ToggleOutcome::State);
        assert_eq!(
            reason(&Evaluation::run(&fs, true, ON_DAY, None)),
            Some(CloseReason::OffToday)
        );
        // 戻す操作が失敗したら出さないまま
        fs.fail_state_write.set(true);
        assert!(turn_on(&fs, &mut ev, 2).is_err());
        assert!(ev.record.as_ref().unwrap().off);
        fs.fail_state_write.set(false);
        assert!(turn_on(&fs, &mut ev, 3).is_ok());
        assert!(Evaluation::run(&fs, true, ON_DAY, None).is_open());
        // 印があって消せないときも戻らない
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        fs.fail_state_write.set(true);
        turn_off(&fs, &mut ev, 4);
        fs.fail_state_write.set(false);
        fs.fail_mark_remove.set(true);
        assert!(turn_on(&fs, &mut ev, 5).is_err());
        assert!(ev.record.as_ref().unwrap().off);
    }

    /// 同じ日の途中で 2 回起動しても、表示の量が 0 に戻らず、最後の行を採れば二重に数えない。
    #[test]
    fn restart_in_the_same_day_does_not_reset_shown_ms() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        ev.add_shown(60_000);
        ev.note_stage_start(1_000);
        ev.save(&fs).unwrap();
        let row1 = ev.row(2_000).unwrap();
        drop(ev);
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        let row2 = ev.row(3_000).unwrap();
        assert_eq!(row2.shown_ms, 60_000, "再起動の直後の行");
        ev.add_shown(30_000);
        let row3 = ev.row(4_000).unwrap();
        assert!(row2.shown_ms >= row1.shown_ms && row3.shown_ms >= row2.shown_ms);
        // 机上では日ごとに最後の行を採る: 足し合わせると二重に数える
        let rows = [&row1, &row2, &row3];
        let last = rows.iter().max_by_key(|r| r.timestamp).unwrap();
        assert_eq!(last.shown_ms, 90_000);
        assert_ne!(rows.iter().map(|r| r.shown_ms).sum::<u64>(), last.shown_ms);
        assert_eq!(row3.stage_starts, vec![1_000]);
        assert_eq!(row3.first_shown_day, Some(ON_DAY));
    }

    #[test]
    fn row_carries_the_day_attributes_even_when_closed() {
        let fs = with_table();
        let ev = Evaluation::run(&fs, true, ON_DAY + 1, None);
        let row = ev.row(9).unwrap();
        assert_eq!(row.assigned, "off");
        assert_eq!(row.reason, Some("assigned_off"));
        assert_eq!(row.late_start_day, Some(LATE_FIRST));
        assert!(row.table_sha256.is_some() && row.draw_seed.is_some());
        assert_eq!(row.visible_ms, None);
        let fs = MemFs::default();
        let row = Evaluation::run(&fs, true, ON_DAY, None).row(9).unwrap();
        assert_eq!(row.assigned, "unknown");
        assert_eq!(row.reason, Some("table_missing"));
        assert!(row.table_sha256.is_none() && row.draw_seed.is_none());
    }

    #[test]
    fn day_change_writes_a_new_day_and_keeps_first_shown_day() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        ev.add_shown(1_000);
        let old_row = ev.row(10).unwrap();
        let ev2 = Evaluation::run(&fs, true, 20_414, ev.record.clone());
        let new_row = ev2.row(11).unwrap();
        assert_eq!((old_row.day, new_row.day), (ON_DAY, 20_414));
        assert_eq!(new_row.shown_ms, 0);
        assert_eq!(new_row.first_shown_day, Some(ON_DAY));
    }

    #[test]
    fn disk_fs_round_trip_in_a_temp_dir() {
        let d = std::env::temp_dir().join(format!(
            "gse-handmark-store-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_nanos()
        ));
        std::fs::create_dir_all(&d).unwrap();
        let mem = with_table();
        let fs = DiskFs {
            table: d.join(TABLE_FILE_NAME),
            sha: d.join(SHA_FILE_NAME),
            state: d.join("gse").join(STATE_FILE_NAME),
            mark_dir: d.join("gse"),
        };
        std::fs::write(&fs.table, mem.table.borrow().clone().unwrap()).unwrap();
        std::fs::write(&fs.sha, mem.sha.borrow().clone().unwrap()).unwrap();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert!(ev.is_open());
        ev.add_shown(5);
        ev.save(&fs).unwrap();
        assert!(!fs.state.with_extension("json.tmp").exists());
        assert_eq!(
            parse_state(&fs.read_state()),
            DayLoad::Loaded(ev.record.clone().unwrap())
        );
        assert!(!fs.mark_exists(ON_DAY));
        fs.write_mark(ON_DAY).unwrap();
        assert!(fs.mark_exists(ON_DAY));
        fs.remove_mark(ON_DAY).unwrap();
        fs.remove_mark(ON_DAY).unwrap();
        assert!(!fs.mark_exists(ON_DAY));
        // 空の状態ファイルは壊れている側
        std::fs::write(&fs.state, b"").unwrap();
        assert_eq!(parse_state(&fs.read_state()), DayLoad::Broken);
        let _ = std::fs::remove_dir_all(&d);
    }
}
