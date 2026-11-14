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
use crate::analysis::handmark::day::{DayRecord, PointerInput};
use crate::analysis::handmark::gate::{decide, CloseReason, Decision, StateStatus};
use crate::logger::HandmarkDayRow;
use crate::redaction::{handmark_subtractions, HandmarkSnap, HandmarkSubs};

pub const TABLE_FILE_NAME: &str = "handmark_assignment.json";
pub const SHA_FILE_NAME: &str = "handmark_assignment.sha256";
pub const STATE_FILE_NAME: &str = "handmark_day_state.json";
pub const TABLE_ENV_VAR: &str = "GSE_HANDMARK_TABLE";
/// 開発・検証の環境変数を読んでよいかを決める環境変数（`lib.rs` の `ensure_debug_enabled` と同じ値の見方）。
pub const DEBUG_ENV_VAR: &str = "GSE_DEBUG";
/// 読むファイルの大きさの上限（これを超えたら壊れている側に倒す）。
pub const MAX_FILE_BYTES: u64 = 64 * 1024;

/// `GSE_HANDMARK_TABLE` を読んでよいか（`GSE_DEBUG` が `"1"` のときだけ）。
pub fn table_env_allowed(gse_debug: Option<&str>) -> bool {
    gse_debug == Some("1")
}

/// 環境変数の表の指定のうち、読んでよいものだけを返す（純関数）。配布形は `s1.mode` の隣の表だけ。
pub fn effective_table_env(gse_debug: Option<&str>, table_env: Option<String>) -> Option<String> {
    if table_env_allowed(gse_debug) {
        table_env
    } else {
        None
    }
}

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
    /// 状態ファイルを消す(無ければ成功)。区間の削除で書き直せないときに使う。
    fn remove_state(&self) -> io::Result<()>;
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
        let env = effective_table_env(
            std::env::var(DEBUG_ENV_VAR).ok().as_deref(),
            std::env::var(TABLE_ENV_VAR).ok(),
        );
        let (table, sha) = table_paths(env.as_deref(), marker.as_deref())?;
        let gse = crate::submission::home_dir()?.join(".gse");
        Some(Self {
            table,
            sha,
            state: gse.join(STATE_FILE_NAME),
            mark_dir: gse,
        })
    }

    /// 表に依らず、状態ファイルと印の置き場だけを決める(駆動役がまだ無いときの区間の削除用)。
    pub fn state_only() -> Option<Self> {
        let gse = crate::submission::home_dir()?.join(".gse");
        Some(Self {
            table: PathBuf::new(),
            sha: PathBuf::new(),
            state: gse.join(STATE_FILE_NAME),
            mark_dir: gse,
        })
    }

    fn mark_path(&self, day: i64) -> PathBuf {
        self.mark_dir.join(format!("handmark_off_{day}"))
    }
}

fn read_file(p: &Path) -> ReadResult {
    use std::io::Read;
    let meta = match std::fs::metadata(p) {
        Ok(m) => m,
        Err(e) if e.kind() == io::ErrorKind::NotFound => return ReadResult::Missing,
        Err(_) => return ReadResult::Unreadable,
    };
    // 通常のファイルでなければ、大きすぎれば、壊れている側に倒す（読み込みで固まらない）
    if !meta.is_file() || meta.len() > MAX_FILE_BYTES {
        return ReadResult::Unreadable;
    }
    let mut buf = Vec::new();
    match std::fs::File::open(p).and_then(|f| f.take(MAX_FILE_BYTES + 1).read_to_end(&mut buf)) {
        Ok(_) if buf.len() as u64 <= MAX_FILE_BYTES => ReadResult::Bytes(buf),
        Ok(_) => ReadResult::Unreadable,
        Err(e) if e.kind() == io::ErrorKind::NotFound => ReadResult::Missing,
        Err(_) => ReadResult::Unreadable,
    }
}

/// 所有者だけが読み書きできる形で開く（unix は 0600。既存のファイルがあっても締める）。
fn create_private(path: &Path) -> io::Result<std::fs::File> {
    let mut o = std::fs::OpenOptions::new();
    o.write(true).create(true).truncate(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        o.mode(0o600);
    }
    let f = o.open(path)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        // `mode()` は新規作成のときにしか効かない（redaction.rs の作法）
        f.set_permissions(std::fs::Permissions::from_mode(0o600))?;
    }
    Ok(f)
}

/// ディレクトリを作り、unix では 0700 に締める。
fn ensure_private_dir(dir: &Path) -> io::Result<()> {
    std::fs::create_dir_all(dir)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(dir, std::fs::Permissions::from_mode(0o700))?;
    }
    Ok(())
}

/// 一時ファイルに書いてから置き換える（`s1_day_state::save` と同じ作法）。unix では 0600 で作り、
/// 一時ファイルの残骸は先に消す。
pub fn write_atomic(path: &Path, bytes: &[u8]) -> io::Result<()> {
    if let Some(dir) = path.parent() {
        ensure_private_dir(dir)?;
    }
    let tmp = path.with_extension("json.tmp");
    // 残骸（古い権限のもの）を引き継がない
    let _ = std::fs::remove_file(&tmp);
    {
        use std::io::Write;
        let mut f = create_private(&tmp)?;
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
    fn remove_state(&self) -> io::Result<()> {
        match std::fs::remove_file(&self.state) {
            Err(e) if e.kind() != io::ErrorKind::NotFound => Err(e),
            _ => Ok(()),
        }
    }
    fn mark_exists(&self, day: i64) -> bool {
        self.mark_path(day).exists()
    }
    fn write_mark(&self, day: i64) -> io::Result<()> {
        ensure_private_dir(&self.mark_dir)?;
        create_private(&self.mark_path(day))?.sync_all()
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
    s1_mode: bool,
    table_load: TableLoad,
    state: StateStatus,
    off_today: bool,
    /// 窓の層が失敗を知らせた(`window_unavailable` で閉じる)。
    window_unavailable: bool,
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
        let mut record = match prior {
            Some(r) => Some(r),
            None => match parse_state(&fs.read_state()) {
                DayLoad::Fresh => Some(DayRecord::new(today)),
                DayLoad::Loaded(r) => Some(r),
                DayLoad::Broken => None,
            },
        };
        let mut state = StateStatus::Broken;
        if let Some(r) = record.as_mut() {
            r.roll_to(today);
            state = StateStatus::Ok;
            // 起動でも検め直しでも毎回、読んだ（走行中の）中身をそのまま書き直して試す
            if write_record(fs, r).is_err() {
                state = StateStatus::Unwritable;
            }
        }
        let off_today =
            fs.mark_exists(today) || record.as_ref().is_some_and(|r| r.off && r.day == today);
        let decision = decide(s1_mode, &table_load, today, state, off_today);
        Self {
            decision,
            record,
            table,
            table_sha256: sha,
            today,
            s1_mode,
            table_load,
            state,
            off_today,
            window_unavailable: false,
        }
    }

    fn redecide(&mut self) {
        self.decision = decide(
            self.s1_mode,
            &self.table_load,
            self.today,
            self.state,
            self.off_today,
        );
        // 開いているはずなのに窓が出せていないときは、窓の失敗で閉じる
        if self.window_unavailable {
            if let Decision::Open { assigned } = self.decision {
                self.decision = Decision::Closed {
                    reason: CloseReason::WindowUnavailable,
                    assigned: Some(assigned),
                };
            }
        }
    }

    /// 窓の層の失敗の印を門に反映する(`true` で閉じ、`false` で戻す)。
    pub fn set_window_unavailable(&mut self, failed: bool) {
        self.window_unavailable = failed;
        self.redecide();
    }

    /// 5 分の保存などの書き込みが失敗したことを門に戻す（この走行では出さない・次の検め直しで書けたら戻る）。
    pub fn note_save_failed(&mut self) {
        self.state = StateStatus::Unwritable;
        self.redecide();
    }

    /// 区間の削除: 走行中の累計から区間内の切った／戻した時刻と起点を消し、状態ファイルへ書く。
    /// 書けなかったら `Err`（累計は消えた後の形でメモリに残る）。lib.rs の削除の経路への配線は 1b。
    /// `subs` の今日の記録の日の分を累計から引く（判断 13・[`crate::redaction::handmark_subtractions`]）。
    pub fn scrub_state(
        &mut self,
        fs: &dyn HandmarkFs,
        from_ms: u64,
        to_ms: u64,
        subs: &HandmarkSubs,
    ) -> io::Result<()> {
        let Some(r) = self.record.as_mut() else {
            return Ok(());
        };
        scrub_record(r, from_ms, to_ms, subs);
        write_record(fs, r)
    }

    /// 走行中の累計の写し（削除で引く量を求める入力・`t` は今）。
    pub fn live_snap(&self, now: u64) -> Option<HandmarkSnap> {
        self.record.as_ref().map(|r| snap_of(r, now))
    }

    pub fn is_open(&self) -> bool {
        self.decision.is_open()
    }

    /// 入力ごとの入れ切り `(カーソルが入っている, クリックが入っている)`。累計が無い（状態ファイルが
    /// 壊れている）ときは窓が開かないので値に意味はなく、両方入っているとして返す。
    pub fn inputs_on(&self) -> (bool, bool) {
        self.record
            .as_ref()
            .map_or((true, true), |r| (!r.cursor_off, !r.click_off))
    }

    /// 出ていた時間を足す（開いているときだけ呼ぶ）。
    pub fn add_shown(&mut self, ms: u64) {
        let today = self.today;
        // 時計が巻き戻って今日と記録の日が違う間は足さない
        if let Some(r) = self.record.as_mut().filter(|r| r.day == today) {
            r.add_shown(ms);
        }
    }

    /// 帯が見えていた時間を足す（`add_shown` と同じ条件のときだけ呼ぶ）。
    pub fn add_visible(&mut self, ms: u64) {
        let today = self.today;
        if let Some(r) = self.record.as_mut().filter(|r| r.day == today) {
            r.add_visible(ms);
        }
    }

    /// 手跡を出し始めた時刻を足す。
    pub fn note_stage_start(&mut self, t: u64) {
        let today = self.today;
        if let Some(r) = self.record.as_mut().filter(|r| r.day == today) {
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
            visible_ms: rec.map(|r| r.visible_ms),
            toggles: rec.map_or_else(Vec::new, |r| {
                r.toggles.iter().map(|t| (t.t, t.on)).collect()
            }),
            input_toggles: rec.map_or_else(Vec::new, |r| {
                r.input_toggles
                    .iter()
                    .map(|t| (t.t, t.input.as_str(), t.on))
                    .collect()
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

/// 区間の削除で状態ファイルを直せなかった。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ScrubFailed;

/// 区間の削除: 状態ファイルを直接読み、区間内の切った／戻した時刻と起点を消して書き直す。
/// 書き直せない・壊れているときは、状態ファイルを消す(消す前に、切っていたなら印を残す)。
/// 消せなければ `Err`。ファイルが無ければ何もしない。駆動役がまだ無いときの区間の削除にも使う。
///
/// 消した後の起動は 1a の `Fresh`(その日の累計 0・切っていない・`first_shown_day` 無し)になり、
/// 日の割付は表だけから決まるので、翌日以降の割付どおりの動きは変わらない。
///
/// 累計からも区間の中の量を引く（判断 13）。引く量は `snaps`（ファイルの行）と状態ファイルの累計から求め、
/// ファイルの行に当てるためにそのまま返す。
pub fn scrub_state_file(
    fs: &dyn HandmarkFs,
    from_ms: u64,
    to_ms: u64,
    snaps: &[HandmarkSnap],
    now: u64,
) -> (Result<(), ScrubFailed>, HandmarkSubs) {
    let remove = |fs: &dyn HandmarkFs| fs.remove_state().map_err(|_| ScrubFailed);
    let rows_only = || handmark_subtractions(snaps, None, from_ms, to_ms);
    match parse_state(&fs.read_state()) {
        DayLoad::Fresh => (Ok(()), rows_only()),
        DayLoad::Broken => (remove(fs), rows_only()),
        DayLoad::Loaded(mut r) => {
            let subs = handmark_subtractions(snaps, Some(snap_of(&r, now)), from_ms, to_ms);
            scrub_record(&mut r, from_ms, to_ms, &subs);
            if write_record(fs, &r).is_ok() {
                return (Ok(()), subs);
            }
            (rewrite_or_remove(fs, &r), subs)
        }
    }
}

/// 区間の削除を累計に当てる: 区間の時刻の要素を消し、記録の日の分の量を引く。
pub(crate) fn scrub_record(r: &mut DayRecord, from_ms: u64, to_ms: u64, subs: &HandmarkSubs) {
    r.scrub_range(from_ms, to_ms);
    if let Some(sub) = subs.get(&r.day) {
        r.subtract(sub.shown_ms, sub.visible_ms);
    }
}

fn snap_of(r: &DayRecord, now: u64) -> HandmarkSnap {
    HandmarkSnap {
        day: r.day,
        t: now,
        shown_ms: r.shown_ms,
        visible_ms: r.visible_ms,
    }
}

/// 区間を落とした累計が書き直せなかった後の始末（`scrub_state_file` と駆動役の `on_redact` で共通）。
///
/// - 何も切っていない: 状態ファイルを消す。
/// - 入力ごとにだけ切っていた（`off` は偽で `cursor_off`/`click_off` が真）: 消す前に、時刻を全部落とし
///   入力ごとの切りを保つ最小の形（`minimal_keeping_off`）で書き直す。それも書けなければ、切りが再起動で
///   戻らないよう全体の「やめる」の印を試してから（書けなくても）消す（時刻を残さないことを優先する）。
/// - 全体を切っていた: 印を書けたときだけ消す。印を書けなければ消さず（停止が失われる）、`off` を保つ最小の形を
///   書き直す。それも駄目なら失敗。
pub(crate) fn rewrite_or_remove(
    fs: &dyn HandmarkFs,
    r: &crate::analysis::handmark::day::DayRecord,
) -> Result<(), ScrubFailed> {
    let remove = |fs: &dyn HandmarkFs| fs.remove_state().map_err(|_| ScrubFailed);
    if !r.off {
        if r.cursor_off || r.click_off {
            if write_record(fs, &r.minimal_keeping_off()).is_ok() {
                return Ok(());
            }
            let _ = fs.write_mark(r.day);
        }
        return remove(fs);
    }
    // 切っていた日: 切ったことが失われないよう、印を書けたときだけ状態ファイルを消す。
    if fs.write_mark(r.day).is_ok() {
        return remove(fs);
    }
    // 印を書けない: 消さない(消すと停止が失われる)。区間の時刻を落とし、`off` を保つ最小の形で
    // 書き直すことを試す。それも駄目なら消さずに失敗として返す(区間の時刻が残りうる)。
    let mut min = r.minimal_keeping_off();
    min.off = true;
    write_record(fs, &min).map_err(|_| ScrubFailed)
}

/// 駆動役が起きない閉じた日の行(ホームが分からない等)。割付も表も分からない。
pub fn unavailable_row(t_ms: u64, day: i64, reason: CloseReason) -> HandmarkDayRow {
    HandmarkDayRow {
        timestamp: t_ms,
        day,
        assigned: "unknown",
        late_start_day: None,
        first_shown_day: None,
        shown_ms: 0,
        visible_ms: None,
        toggles: Vec::new(),
        input_toggles: Vec::new(),
        stage_starts: Vec::new(),
        overflow: false,
        table_sha256: None,
        draw_seed: None,
        reason: Some(reason.as_str()),
    }
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

/// 切る。走行中は必ず出さない側に倒す（開いていれば `Closed{OffToday}` にする）。
pub fn turn_off(fs: &dyn HandmarkFs, ev: &mut Evaluation, now_ms: u64) -> ToggleOutcome {
    let today = ev.today;
    let outcome = match ev.record.as_mut() {
        None => {
            // 状態ファイルが壊れていて累計が無い: 印だけ試す
            if fs.write_mark(ev.today).is_ok() {
                ToggleOutcome::MarkOnly
            } else {
                ToggleOutcome::NotPersisted
            }
        }
        Some(r) => {
            // 記録の日が今日と違う間（時計の巻き戻り）は記録に足さない。印だけ試す
            if r.day == today {
                r.set_off(now_ms, true);
            }
            if r.day == today && write_record(fs, r).is_ok() {
                ToggleOutcome::State
            } else if fs.write_mark(ev.today).is_ok() {
                ToggleOutcome::MarkOnly
            } else {
                ToggleOutcome::NotPersisted
            }
        }
    };
    ev.off_today = true;
    ev.redecide();
    outcome
}

/// 戻せなかった（出さないまま）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RestoreFailed;

/// 戻す。状態ファイルに書けて、印があれば消せたときだけ戻り、門を判定し直す。失敗したら出さないまま（`Err`）。
pub fn turn_on(fs: &dyn HandmarkFs, ev: &mut Evaluation, now_ms: u64) -> Result<(), RestoreFailed> {
    let today = ev.today;
    let Some(r) = ev.record.as_mut().filter(|r| r.day == today) else {
        return Err(RestoreFailed);
    };
    let prev = r.clone();
    r.set_off(now_ms, false);
    if write_record(fs, r).is_err() || fs.remove_mark(ev.today).is_err() {
        *r = prev;
        r.off = true;
        return Err(RestoreFailed);
    }
    ev.off_today = false;
    ev.redecide();
    Ok(())
}

/// 入力ごとに切る。走行の中では、書けなくても必ず切った状態にする（切った側に倒す）。
/// 結果は状態ファイルに書けたか（`State`）・書けず、全体の「やめる」と同じ日付つきの印（`handmark_off_<日>`）を
/// 書けたか（`MarkOnly`）・どちらも書けなかったか（`NotPersisted`・この走行の中だけ切る）。
///
/// ★ 状態ファイルに書けなかったとき（ADR-051 D2「書き残せなかったときは、切った側に倒す（出さない）」）:
/// 再起動で入力が黙って戻らないよう、その日は手跡全体を出さない側に倒す。印を書けたら全体を切った扱いにして
/// （`turn_off` と同じ・窓は閉じる）、印も書けなければ今のとおりこの走行の中だけ切る。
/// 累計が無い（状態ファイルが壊れている）ときは何も持てず `NotPersisted`（そのとき窓は開かない）。
/// 記録の日が今日と違う間（時計の巻き戻り）は状態だけ切り、記録には足さない（書き込みを試みないので印も作らない）。
pub fn turn_input_off(
    fs: &dyn HandmarkFs,
    ev: &mut Evaluation,
    input: PointerInput,
    now_ms: u64,
) -> ToggleOutcome {
    let today = ev.today;
    let Some(r) = ev.record.as_mut() else {
        return ToggleOutcome::NotPersisted;
    };
    if r.day != today {
        match input {
            PointerInput::Cursor => r.cursor_off = true,
            PointerInput::Click => r.click_off = true,
        }
        return ToggleOutcome::NotPersisted;
    }
    r.set_input(now_ms, input, false);
    if write_record(fs, r).is_ok() {
        return ToggleOutcome::State;
    }
    // 書けなかった: 再起動で戻らないよう、その日は全体を出さない側に倒す（印を試す）。
    if fs.write_mark(today).is_ok() {
        r.set_off(now_ms, true);
        ev.off_today = true;
        ev.redecide();
        ToggleOutcome::MarkOnly
    } else {
        ToggleOutcome::NotPersisted
    }
}

/// 入力ごとに戻す。状態ファイルに書けたときだけ戻り、書けなければ切ったまま（`Err`）。
pub fn turn_input_on(
    fs: &dyn HandmarkFs,
    ev: &mut Evaluation,
    input: PointerInput,
    now_ms: u64,
) -> Result<(), RestoreFailed> {
    let today = ev.today;
    let Some(r) = ev.record.as_mut().filter(|r| r.day == today) else {
        return Err(RestoreFailed);
    };
    let prev = r.clone();
    r.set_input(now_ms, input, true);
    if write_record(fs, r).is_err() {
        *r = prev;
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
        /// 次の `n` 回の状態の書き込みだけ失敗させる（その後は成功）。
        pub fail_state_writes_left: Cell<u32>,
        pub fail_mark_write: Cell<bool>,
        pub fail_mark_remove: Cell<bool>,
        pub fail_state_remove: Cell<bool>,
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
            let left = self.fail_state_writes_left.get();
            if left > 0 {
                self.fail_state_writes_left.set(left - 1);
                return Err(io::Error::other("injected"));
            }
            *self.state.borrow_mut() = Some(bytes.to_vec());
            Ok(())
        }
        fn remove_state(&self) -> io::Result<()> {
            if self.fail_state_remove.get() {
                return Err(io::Error::other("injected"));
            }
            *self.state.borrow_mut() = None;
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
        // この走行では出さない側（門が閉じ、行の理由も off_today）
        assert!(!ev.is_open());
        assert_eq!(ev.row(1).unwrap().reason, Some("off_today"));
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
        assert!(!ev.is_open());
        assert_eq!(reason(&ev), Some(CloseReason::OffToday));
        assert_eq!(ev.row(1).unwrap().assigned, "on");
        assert_eq!(
            reason(&Evaluation::run(&fs, true, ON_DAY, None)),
            Some(CloseReason::OffToday)
        );
        // 戻す操作が失敗したら出さないまま
        fs.fail_state_write.set(true);
        assert!(turn_on(&fs, &mut ev, 2).is_err());
        assert!(!ev.is_open());
        fs.fail_state_write.set(false);
        assert!(turn_on(&fs, &mut ev, 3).is_ok());
        assert!(ev.is_open());
        assert_eq!(ev.row(3).unwrap().reason, None);
        assert!(Evaluation::run(&fs, true, ON_DAY, None).is_open());
        // 印があって消せないときも戻らない
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        fs.fail_state_write.set(true);
        turn_off(&fs, &mut ev, 4);
        fs.fail_state_write.set(false);
        fs.fail_mark_remove.set(true);
        assert!(turn_on(&fs, &mut ev, 5).is_err());
        assert!(!ev.is_open());
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
        // 累計(記録)があれば Some(累計)。この日は一度も出ていないので 0。
        assert_eq!(row.visible_ms, Some(0));
        let fs = MemFs::default();
        let row = Evaluation::run(&fs, true, ON_DAY, None).row(9).unwrap();
        assert_eq!(row.assigned, "unknown");
        assert_eq!(row.reason, Some("table_missing"));
        assert!(row.table_sha256.is_none() && row.draw_seed.is_none());
        // 累計が無いとき(状態ファイルが壊れている)は null
        let fs = with_table();
        *fs.state.borrow_mut() = Some(b"{broken".to_vec());
        let ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert!(ev.record.is_none());
        assert_eq!(ev.row(9).unwrap().visible_ms, None);
        // 足すと行に載り、状態ファイルの往復で残る
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        ev.add_shown(900);
        ev.add_visible(400);
        assert_eq!(ev.row(9).unwrap().visible_ms, Some(400));
        ev.save(&fs).unwrap();
        let back = Evaluation::run(&fs, true, ON_DAY, None);
        assert_eq!(back.row(9).unwrap().visible_ms, Some(400));
        assert_eq!(back.row(9).unwrap().shown_ms, 900);
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
        // visible_ms が shown_ms を超える状態ファイルも壊れている側(評価は閉じたまま)
        let mut bad = DayRecord::new(ON_DAY);
        bad.add_shown(10);
        bad.add_visible(11);
        std::fs::write(&fs.state, serde_json::to_vec(&bad).unwrap()).unwrap();
        assert_eq!(parse_state(&fs.read_state()), DayLoad::Broken);
        assert!(Evaluation::run(&fs, true, ON_DAY, None).record.is_none());
        let _ = std::fs::remove_dir_all(&d);
    }

    /// 書けない → 同じ日の検め直しでも閉じたまま（検め直しのたびに書き込みを試す）。
    #[test]
    fn an_unwritable_state_stays_closed_at_every_recheck() {
        let fs = with_table();
        let ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert!(ev.is_open());
        fs.fail_state_write.set(true);
        let ev2 = Evaluation::run(&fs, true, ON_DAY, ev.record.clone());
        assert_eq!(reason(&ev2), Some(CloseReason::StateUnwritable));
        let ev3 = Evaluation::run(&fs, true, ON_DAY, ev2.record.clone());
        assert_eq!(reason(&ev3), Some(CloseReason::StateUnwritable));
        // 書けるようになれば次の検め直しで戻る
        fs.fail_state_write.set(false);
        assert!(Evaluation::run(&fs, true, ON_DAY, ev3.record.clone()).is_open());
    }

    /// 5 分の保存の失敗は門に戻る。
    #[test]
    fn a_failed_periodic_save_closes_the_gate() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        ev.add_shown(10);
        fs.fail_state_write.set(true);
        assert!(ev.save(&fs).is_err());
        ev.note_save_failed();
        assert!(!ev.is_open());
        assert_eq!(ev.row(1).unwrap().reason, Some("state_unwritable"));
        // 次の検め直しでも書けなければ閉じたまま
        let ev2 = Evaluation::run(&fs, true, ON_DAY, ev.record.clone());
        assert_eq!(reason(&ev2), Some(CloseReason::StateUnwritable));
    }

    /// 今日の区間を消す → row() を作り直しても、状態ファイルを読み直しても時刻が無い。
    #[test]
    fn scrub_state_removes_the_times_from_memory_and_from_the_state_file() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        ev.note_stage_start(1_000);
        ev.note_stage_start(5_000);
        turn_off(&fs, &mut ev, 2_000);
        assert!(turn_on(&fs, &mut ev, 3_000).is_ok());
        ev.add_shown(77);
        ev.save(&fs).unwrap();
        ev.scrub_state(&fs, 900, 3_500, &crate::redaction::HandmarkSubs::new())
            .unwrap();
        let row = ev.row(9).unwrap();
        assert_eq!(row.stage_starts, vec![5_000]);
        assert!(row.toggles.is_empty());
        assert_eq!(row.shown_ms, 77);
        let DayLoad::Loaded(disk) = parse_state(&fs.read_state()) else {
            panic!("state must load");
        };
        assert!(disk.toggles.is_empty());
        assert_eq!(disk.stage_starts, vec![5_000]);
        // 起動し直しても戻らない
        let again = Evaluation::run(&fs, true, ON_DAY, None);
        assert_eq!(again.row(10).unwrap().stage_starts, vec![5_000]);
        assert!(again.row(10).unwrap().toggles.is_empty());
        // 書けないときは Err
        fs.fail_state_write.set(true);
        assert!(ev
            .scrub_state(&fs, 0, u64::MAX, &crate::redaction::HandmarkSubs::new())
            .is_err());
    }

    /// 日 D に切って保存 → 時計が D-1 に戻って検め直し → D に戻って検め直し → 切ったまま。
    #[test]
    fn a_clock_that_goes_back_does_not_forget_that_it_was_turned_off() {
        let fs = with_table();
        let d = ON_DAY;
        let mut ev = Evaluation::run(&fs, true, d, None);
        assert_eq!(turn_off(&fs, &mut ev, 1_000), ToggleOutcome::State);
        let saved = ev.record.clone();
        // D-1 に戻る: 記録は変えず、足さない
        let mut back = Evaluation::run(&fs, true, d - 1, saved.clone());
        back.add_shown(5_000);
        back.note_stage_start(2_000);
        turn_off(&fs, &mut back, 3_000);
        assert_eq!(back.record, saved);
        // D に戻る
        let ev2 = Evaluation::run(&fs, true, d, back.record.clone());
        assert!(!ev2.is_open());
        assert_eq!(ev2.row(9).unwrap().reason, Some("off_today"));
        assert!(ev2.record.as_ref().unwrap().off);
        assert_eq!(ev2.record.as_ref().unwrap().shown_ms, 0);
        // 起動し直しても切ったまま（巻き戻りの間に状態ファイルが別の日で上書きされていない）
        assert_eq!(
            reason(&Evaluation::run(&fs, true, d, None)),
            Some(CloseReason::OffToday)
        );
    }

    #[test]
    fn the_env_table_is_read_only_when_gse_debug_is_one() {
        assert!(table_env_allowed(Some("1")));
        for v in [
            None,
            Some(""),
            Some("0"),
            Some("true"),
            Some("11"),
            Some(" 1"),
        ] {
            assert!(!table_env_allowed(v), "{v:?}");
        }
        let t = Some("/x/t.json".to_string());
        assert_eq!(effective_table_env(Some("1"), t.clone()), t);
        assert_eq!(effective_table_env(None, t.clone()), None);
        assert_eq!(effective_table_env(Some("0"), t), None);
    }

    fn temp_dir(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!(
            "gse-handmark-{tag}-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_nanos()
        ));
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    #[test]
    fn read_file_treats_non_files_and_big_files_as_unreadable() {
        let d = temp_dir("read");
        assert_eq!(read_file(&d.join("none")), ReadResult::Missing);
        // ディレクトリ
        assert_eq!(read_file(&d), ReadResult::Unreadable);
        // 上限ちょうどは読める・1 バイト超えは読まない
        let ok = d.join("ok");
        std::fs::write(&ok, vec![b'a'; MAX_FILE_BYTES as usize]).unwrap();
        assert!(matches!(read_file(&ok), ReadResult::Bytes(b) if b.len() as u64 == MAX_FILE_BYTES));
        let big = d.join("big");
        std::fs::write(&big, vec![b'a'; MAX_FILE_BYTES as usize + 1]).unwrap();
        assert_eq!(read_file(&big), ReadResult::Unreadable);
        // 状態ファイルとしては壊れている側
        assert_eq!(parse_state(&read_file(&big)), DayLoad::Broken);
        let _ = std::fs::remove_dir_all(&d);
    }

    #[cfg(unix)]
    #[test]
    fn state_tmp_marks_and_dir_are_owner_only_on_unix() {
        use std::os::unix::fs::PermissionsExt;
        let mode = |p: &Path| std::fs::metadata(p).unwrap().permissions().mode() & 0o777;
        let d = temp_dir("perm");
        let gse = d.join("gse");
        let fs = DiskFs {
            table: d.join("t.json"),
            sha: d.join("t.sha256"),
            state: gse.join(STATE_FILE_NAME),
            mark_dir: gse.clone(),
        };
        // 古い権限の一時ファイルの残骸と、緩い権限の既存の状態ファイルがあっても締める
        std::fs::create_dir_all(&gse).unwrap();
        std::fs::set_permissions(&gse, std::fs::Permissions::from_mode(0o755)).unwrap();
        let tmp = fs.state.with_extension("json.tmp");
        std::fs::write(&tmp, b"stale").unwrap();
        std::fs::set_permissions(&tmp, std::fs::Permissions::from_mode(0o644)).unwrap();
        std::fs::write(&fs.state, b"{}").unwrap();
        std::fs::set_permissions(&fs.state, std::fs::Permissions::from_mode(0o644)).unwrap();
        fs.write_state(b"{}").unwrap();
        assert_eq!(mode(&fs.state), 0o600);
        assert!(!tmp.exists());
        assert_eq!(mode(&gse), 0o700);
        // 印: 既存の緩い印も締める
        std::fs::write(gse.join("handmark_off_5"), b"").unwrap();
        std::fs::set_permissions(
            gse.join("handmark_off_5"),
            std::fs::Permissions::from_mode(0o644),
        )
        .unwrap();
        fs.write_mark(5).unwrap();
        assert_eq!(mode(&gse.join("handmark_off_5")), 0o600);
        fs.write_mark(6).unwrap();
        assert_eq!(mode(&gse.join("handmark_off_6")), 0o600);
        let _ = std::fs::remove_dir_all(&d);
    }

    /// 区間の削除で状態ファイルを直せないとき(書けない・壊れている)は消す。消した後は 1a の Fresh で、
    /// 翌日の割付どおりに戻り、切っていた日の印は残る。
    #[test]
    fn scrub_state_file_removes_what_it_cannot_rewrite_and_fresh_is_harmless() {
        // 書き直せる: 時刻だけ消えて残る
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        ev.note_stage_start(1_000);
        ev.save(&fs).unwrap();
        scrub_state_file(&fs, 0, 2_000, &[], 0).0.unwrap();
        let DayLoad::Loaded(r) = parse_state(&fs.read_state()) else {
            panic!("loaded");
        };
        assert!(r.stage_starts.is_empty());
        // 書けない: 消す(切っていたので印は残る)
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert_eq!(turn_off(&fs, &mut ev, 5), ToggleOutcome::State);
        fs.fail_state_write.set(true);
        scrub_state_file(&fs, 0, 10, &[], 0).0.unwrap();
        fs.fail_state_write.set(false);
        assert_eq!(fs.read_state(), ReadResult::Missing);
        assert!(fs.mark_exists(ON_DAY));
        // Fresh の起動: 切った日はそのまま閉じ、翌日は割付どおりに開く
        assert_eq!(
            reason(&Evaluation::run(&fs, true, ON_DAY, None)),
            Some(CloseReason::OffToday)
        );
        assert!(Evaluation::run(&fs, true, 20_414, None).is_open());
        // 壊れている: 消す・消せなければ Err
        *fs.state.borrow_mut() = Some(b"{broken".to_vec());
        fs.fail_state_remove.set(true);
        assert_eq!(scrub_state_file(&fs, 0, 10, &[], 0).0, Err(ScrubFailed));
        fs.fail_state_remove.set(false);
        scrub_state_file(&fs, 0, 10, &[], 0).0.unwrap();
        assert_eq!(fs.read_state(), ReadResult::Missing);
        // 無ければ何もしない
        scrub_state_file(&fs, 0, 10, &[], 0).0.unwrap();
        // 切っていなかった日は Fresh で、割付どおり開く(累計は 0 に戻る)
        let fs2 = with_table();
        let mut ev2 = Evaluation::run(&fs2, true, ON_DAY, None);
        ev2.add_shown(5_000);
        ev2.save(&fs2).unwrap();
        fs2.fail_state_write.set(true);
        scrub_state_file(&fs2, 0, u64::MAX, &[], 0).0.unwrap();
        fs2.fail_state_write.set(false);
        let again = Evaluation::run(&fs2, true, ON_DAY, None);
        assert!(again.is_open());
        assert_eq!(again.row(1).unwrap().shown_ms, 0);
    }

    /// 状態ファイルと印の書き込みが同時に失敗する → 失敗を返し、状態ファイルを消さず、再起動で切ったまま。
    #[test]
    fn scrub_keeps_the_off_state_when_neither_the_state_nor_the_mark_can_be_written() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        ev.note_stage_start(1_000);
        assert_eq!(turn_off(&fs, &mut ev, 5), ToggleOutcome::State);
        fs.fail_state_write.set(true);
        fs.fail_mark_write.set(true);
        assert_eq!(scrub_state_file(&fs, 0, 10_000, &[], 0).0, Err(ScrubFailed));
        fs.fail_state_write.set(false);
        fs.fail_mark_write.set(false);
        // 状態ファイルは消されず、off を保っている(区間の時刻は残りうる)
        let DayLoad::Loaded(r) = parse_state(&fs.read_state()) else {
            panic!("state must stay");
        };
        assert!(r.off);
        assert_eq!(
            reason(&Evaluation::run(&fs, true, ON_DAY, None)),
            Some(CloseReason::OffToday)
        );
    }

    #[test]
    fn a_window_failure_closes_with_its_reason_and_can_be_cleared() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert!(ev.is_open());
        ev.set_window_unavailable(true);
        assert!(!ev.is_open());
        assert_eq!(ev.row(1).unwrap().reason, Some("window_unavailable"));
        assert_eq!(ev.row(1).unwrap().assigned, "on");
        ev.set_window_unavailable(false);
        assert!(ev.is_open());
        // 他の理由で閉じているときは、その理由を残す
        let fs = MemFs::default();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        ev.set_window_unavailable(true);
        assert_eq!(ev.row(1).unwrap().reason, Some("table_missing"));
    }

    #[test]
    fn unavailable_row_has_the_reason_and_no_other_attributes() {
        let r = unavailable_row(5, 20_411, CloseReason::PathsUnavailable);
        assert_eq!(r.reason, Some("paths_unavailable"));
        assert_eq!((r.assigned, r.shown_ms), ("unknown", 0));
        assert!(r.table_sha256.is_none() && r.draw_seed.is_none() && r.toggles.is_empty());
    }
    use crate::analysis::handmark::day::PointerInput as PI;

    #[test]
    fn an_input_toggle_goes_to_the_row_and_the_state_file() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert_eq!(ev.inputs_on(), (true, true));
        assert_eq!(
            turn_input_off(&fs, &mut ev, PI::Cursor, 1_000),
            ToggleOutcome::State
        );
        assert_eq!(ev.inputs_on(), (false, true));
        assert!(turn_input_on(&fs, &mut ev, PI::Cursor, 2_000).is_ok());
        assert_eq!(
            turn_input_off(&fs, &mut ev, PI::Click, 3_000),
            ToggleOutcome::State
        );
        assert_eq!(ev.inputs_on(), (true, false));
        let row = ev.row(9).unwrap();
        assert_eq!(
            row.input_toggles,
            vec![
                (1_000, "cursor", false),
                (2_000, "cursor", true),
                (3_000, "click", false)
            ]
        );
        // 全体の「やめる」は入力ごとの状態に触れない
        turn_off(&fs, &mut ev, 4_000);
        assert_eq!(ev.inputs_on(), (true, false));
        // 起動で状態ファイルから戻る
        let again = Evaluation::run(&fs, true, ON_DAY, None);
        assert_eq!(again.inputs_on(), (true, false));
        assert_eq!(again.row(10).unwrap().input_toggles.len(), 3);
        // 翌日は両方入った状態に戻り、記録は空
        let next = Evaluation::run(&fs, true, ON_DAY + 3, again.record.clone());
        assert_eq!(next.inputs_on(), (true, true));
        assert!(next.row(11).unwrap().input_toggles.is_empty());
        let boot = Evaluation::run(&fs, true, ON_DAY + 3, None);
        assert_eq!(boot.inputs_on(), (true, true));
    }

    #[test]
    fn a_failed_write_keeps_the_input_off_and_cannot_turn_it_on() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        fs.fail_state_write.set(true);
        // 印も書けない（書けるときは全体を出さない側に倒れる・下の別のテスト）
        fs.fail_mark_write.set(true);
        // 切るのは書けなくても切った状態にする
        assert_eq!(
            turn_input_off(&fs, &mut ev, PI::Click, 1_000),
            ToggleOutcome::NotPersisted
        );
        assert_eq!(ev.inputs_on(), (true, false));
        // 入れるのは書けなければ切ったまま
        assert!(turn_input_on(&fs, &mut ev, PI::Click, 2_000).is_err());
        assert_eq!(ev.inputs_on(), (true, false));
        assert_eq!(
            ev.row(1).unwrap().input_toggles.len(),
            1,
            "the failed on is not recorded"
        );
        // 書けるようになれば入れられる
        fs.fail_state_write.set(false);
        assert!(turn_input_on(&fs, &mut ev, PI::Click, 3_000).is_ok());
        assert_eq!(ev.inputs_on(), (true, true));
        // 状態が壊れている（累計が無い）ときは何も持たず、入れられもしない
        let fs = with_table();
        *fs.state.borrow_mut() = Some(b"{broken".to_vec());
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert!(ev.record.is_none());
        assert_eq!(
            turn_input_off(&fs, &mut ev, PI::Cursor, 1),
            ToggleOutcome::NotPersisted
        );
        assert!(turn_input_on(&fs, &mut ev, PI::Cursor, 2).is_err());
    }

    #[test]
    fn a_failed_input_cut_with_a_mark_leaves_the_whole_day_off_after_a_restart() {
        // 状態ファイルに書けなかったら、その日は手跡全体を出さない側に倒す（ADR-051 D2）。
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert!(ev.is_open());
        fs.fail_state_write.set(true);
        assert_eq!(
            turn_input_off(&fs, &mut ev, PI::Cursor, 1_000),
            ToggleOutcome::MarkOnly
        );
        assert!(!ev.is_open(), "この走行でも全体を出さない");
        assert!(
            fs.marks.borrow().contains(&ON_DAY),
            "全体のやめると同じ日付つきの印"
        );
        // 起動し直す（状態ファイルは古いまま = カーソルは入ったまま）。その日は出ない。
        fs.fail_state_write.set(false);
        let ev2 = Evaluation::run(&fs, true, ON_DAY, None);
        assert!(!ev2.is_open());
        assert_eq!(reason(&ev2), Some(CloseReason::OffToday));
        // 陽性対照: 書けたときは印を作らず、全体も切らない。
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert_eq!(
            turn_input_off(&fs, &mut ev, PI::Cursor, 1_000),
            ToggleOutcome::State
        );
        assert!(ev.is_open() && fs.marks.borrow().is_empty());
        // 印も書けなければ、この走行の中だけ切る（再起動では戻る）。
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        fs.fail_state_write.set(true);
        fs.fail_mark_write.set(true);
        assert_eq!(
            turn_input_off(&fs, &mut ev, PI::Click, 1_000),
            ToggleOutcome::NotPersisted
        );
        assert!(ev.is_open() && ev.inputs_on() == (true, false));
        fs.fail_state_write.set(false);
        fs.fail_mark_write.set(false);
        assert_eq!(
            Evaluation::run(&fs, true, ON_DAY, None).inputs_on(),
            (true, true)
        );
    }

    /// 区間の削除の書き直しに失敗しても、入力ごとの切りは保たれる（時刻だけが落ちる）。
    #[test]
    fn a_failed_redact_rewrite_keeps_an_input_cut() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert_eq!(
            turn_input_off(&fs, &mut ev, PI::Cursor, 1_000),
            ToggleOutcome::State
        );
        // 最初の書き込み（区間を落とした全体）だけ失敗し、最小の形は書ける。
        fs.fail_state_writes_left.set(1);
        assert!(scrub_state_file(&fs, 0, 10_000, &[], 0).0.is_ok());
        let ev2 = Evaluation::run(&fs, true, ON_DAY, None);
        assert_eq!(ev2.inputs_on(), (false, true), "カーソルは切れたまま");
        assert!(
            ev2.row(1).unwrap().input_toggles.is_empty(),
            "時刻は落ちている"
        );
        // 最小の形も書けないときは、全体の印を試して状態ファイルを消す（時刻を残さない）。
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        let _ = turn_input_off(&fs, &mut ev, PI::Click, 1_000);
        fs.fail_state_write.set(true);
        assert!(scrub_state_file(&fs, 0, 10_000, &[], 0).0.is_ok());
        assert!(fs.state.borrow().is_none());
        assert!(
            fs.marks.borrow().contains(&ON_DAY),
            "切りが戻らないよう全体を出さない側へ"
        );
        // 何も切っていなければ、今までどおり消すだけ（印は作らない）。
        let fs = with_table();
        let ev = Evaluation::run(&fs, true, ON_DAY, None);
        let _ = ev.save(&fs);
        fs.fail_state_write.set(true);
        assert!(scrub_state_file(&fs, 0, 10_000, &[], 0).0.is_ok());
        assert!(fs.marks.borrow().is_empty());
    }

    #[test]
    fn input_toggles_overflow_uses_the_existing_flag() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        for i in 0..70u64 {
            let _ = turn_input_off(&fs, &mut ev, PI::Cursor, i);
        }
        let row = ev.row(1).unwrap();
        assert_eq!(
            row.input_toggles.len(),
            crate::analysis::handmark::day::MAX_PER_DAY
        );
        assert!(row.overflow);
        assert_eq!(ev.inputs_on(), (false, true));
    }

    #[test]
    fn scrub_removes_input_toggles_from_the_row_the_state_file_and_the_running_total() {
        let fs = with_table();
        let mut ev = Evaluation::run(&fs, true, ON_DAY, None);
        turn_input_off(&fs, &mut ev, PI::Cursor, 1_000);
        turn_input_off(&fs, &mut ev, PI::Click, 2_000);
        assert!(turn_input_on(&fs, &mut ev, PI::Cursor, 3_000).is_ok());
        // 走行中の累計（と、そこから作る行）
        ev.scrub_state(&fs, 1_500, 2_500, &crate::redaction::HandmarkSubs::new())
            .unwrap();
        let row = ev.row(9).unwrap();
        assert_eq!(
            row.input_toggles,
            vec![(1_000, "cursor", false), (3_000, "cursor", true)]
        );
        // 状態（切った）は時刻でないので残る
        assert_eq!(ev.inputs_on(), (true, false));
        // 状態ファイル
        let DayLoad::Loaded(disk) = parse_state(&fs.read_state()) else {
            panic!("state must load");
        };
        assert_eq!(disk.input_toggles.len(), 2);
        // 駆動役が無いときの状態ファイルの直接の削除
        scrub_state_file(&fs, 0, 1_000, &[], 0).0.unwrap();
        let DayLoad::Loaded(disk) = parse_state(&fs.read_state()) else {
            panic!("state must load");
        };
        assert_eq!(disk.input_toggles.len(), 1);
        assert_eq!(disk.input_toggles[0].t, 3_000);
        assert!(!disk.cursor_off && disk.click_off);
        // 起動し直しても戻らない
        let again = Evaluation::run(&fs, true, ON_DAY, None);
        assert_eq!(
            again.row(10).unwrap().input_toggles,
            vec![(3_000, "cursor", true)]
        );
    }

    #[test]
    fn an_old_state_file_without_input_fields_loads_with_both_inputs_on() {
        let fs = with_table();
        let old = r#"{"version":1,"day":20411,"shown_ms":5,"toggles":[],"off":false,"first_shown_day":20411,"stage_starts":[],"overflow":false}"#;
        *fs.state.borrow_mut() = Some(old.as_bytes().to_vec());
        let ev = Evaluation::run(&fs, true, ON_DAY, None);
        assert!(ev.record.is_some());
        assert_eq!(ev.inputs_on(), (true, true));
        assert_eq!(ev.row(1).unwrap().shown_ms, 5);
    }

    /// 駆動役が無いときの状態ファイルの直接の削除でも、累計から区間の量を引き、同じ量をファイル用に返す
    /// （段 1 の同意の判断 13）。
    #[test]
    fn state_file_redact_subtracts_the_interval_and_returns_the_amount() {
        use crate::redaction::{HandmarkSnap, HandmarkSub};
        let fs = with_table();
        let st = r#"{"version":1,"day":20411,"shown_ms":500,"visible_ms":400,"toggles":[],"off":false,"first_shown_day":20411,"stage_starts":[],"overflow":false}"#;
        *fs.state.borrow_mut() = Some(st.as_bytes().to_vec());
        let snaps = [HandmarkSnap {
            day: ON_DAY,
            t: 1_000,
            shown_ms: 100,
            visible_ms: 90,
        }];
        let (r, subs) = scrub_state_file(&fs, 1_500, 2_500, &snaps, 9_000);
        r.unwrap();
        assert_eq!(
            subs.get(&ON_DAY),
            Some(&HandmarkSub {
                shown_ms: 400,
                visible_ms: 310
            })
        );
        let DayLoad::Loaded(disk) = parse_state(&fs.read_state()) else {
            panic!("state must load");
        };
        assert_eq!((disk.shown_ms, disk.visible_ms), (100, 90));
        // 状態ファイルが無ければ、ファイルの行だけから求める(後の行が無いので引かない)
        *fs.state.borrow_mut() = None;
        let (r, subs) = scrub_state_file(&fs, 1_500, 2_500, &snaps, 9_000);
        r.unwrap();
        assert!(subs.is_empty());
    }
}
