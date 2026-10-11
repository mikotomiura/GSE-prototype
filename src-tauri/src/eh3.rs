//! EH3（肖像と招待の参加者内比較）の「EH3 モード」判定と、日ごとの条件の割り当て（OS API 非依存）。
//!
//! ## なぜこのモジュールがあるか
//!
//! EH3 は参加者の PC で、空・D・A の 3 ブロック × 5 稼働日を順に回す
//! （`.steering/20261011-portrait-eh3-prereg/decisions.md` 判断 1・2）。
//! ★ 収集の器は **O1 をそのまま使う**（`.steering/20261011-portrait-eh3-impl/decisions.md` 判断 3 #1）。
//! → 本モジュールは O1 の上に載せる層で、**O1 でないときは EH3 を立てない**。
//!
//! ★ `o1.rs` と同じく **判定だけをここに置き、効果は `lib.rs` が適用する**。
//!
//! ## 割り当ての印
//!
//! 配布フォルダの `eh3.mode` の中身（1 行）が、その参加者の割り当てそのものである:
//!
//! ```text
//! order=E,D,A;a_first=seed;grammar=raw;drift=none
//! ```
//!
//! - `order`: 3 ブロックの順序（`E` = 空・`D` = 日替わりの地模様・`A` = その回の形）。3 つを 1 回ずつ。
//! - `a_first`: A ブロックの初日の終わりの扱い（`none` / `seed`）。以後、日ごとに交互にする。
//! - `grammar` / `drift`: 肖像の形の文法（F-1 で研究者が 1 つに選ぶ）。
//!
//! ⚠️ 中身が読めない・不正なら **EH3 を立てない**（既定の条件を勝手に選ばない）。
//!
//! ## 稼働日（判断 2 #2）
//!
//! 現地時刻で早朝 4:00 を区切りとし、その日に打鍵を 1 回でも観測したら 1 稼働日と数える。
//! 条件はその日を数えた時点で決まり、日中は変わらない。15 稼働日を超えた日は「期間の後」。
//! ⚠️ 曜日の判定は置かない（土日に使えばその日も数える）。

use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};

/// フォルダに置く印のファイル名。★ `o1.mode` の鏡像。
pub const MARKER_FILE_NAME: &str = "eh3.mode";

/// 開発・検証用の環境変数。中身は印と同じ書式。
pub const ENV_VAR: &str = "GSE_EH3_MODE";

/// 1 ブロックの稼働日の数（判断 2 #1）。
pub const BLOCK_DAYS: u32 = 5;

/// ブロックの数。
pub const BLOCKS: u32 = 3;

/// 期間全体の稼働日の数。
pub const PERIOD_DAYS: u32 = BLOCK_DAYS * BLOCKS;

/// 日付の区切り（現地時刻・時）。夜更けの作業を前の日に入れる（design §6）。
pub const DAY_CUTOFF_HOUR: i64 = 4;

const DAY_SECS: i64 = 24 * 60 * 60;

/// EH3 モードを立てた引き金。★ `O1Source` の鏡像。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Eh3Source {
    /// 実行ファイルを包むフォルダに `eh3.mode` があった (配布形)。
    Marker,
    /// 環境変数 `GSE_EH3_MODE` が立っていた (開発・検証用)。
    Env,
}

impl Eh3Source {
    /// `meta` 行の `eh3_mode` に書く固定文字列。
    pub fn as_str(self) -> &'static str {
        match self {
            Eh3Source::Marker => "marker",
            Eh3Source::Env => "env",
        }
    }
}

/// 肖像の条件のブロック。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Block {
    /// 空: 元の壁紙のまま。
    Blank,
    /// D: 日替わりの地模様（打鍵を材料にしない）。
    Decor,
    /// A: その回の形。
    Portrait,
}

/// A の終わりの扱い（E1-8）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Ending {
    /// 何もしない（次の始まりで地から）。
    None,
    /// 形を重心の小さな印へ畳む。
    Seed,
}

impl Ending {
    fn other(self) -> Ending {
        match self {
            Ending::None => Ending::Seed,
            Ending::Seed => Ending::None,
        }
    }
}

/// 肖像の形の文法（親の判断 13: `raw` と `lattice` が候補）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Grammar {
    Raw,
    Lattice,
}

/// 形の上書きの型（EH1 第 3〜5 回の `none` / `diffuse`）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Drift {
    None,
    Diffuse,
}

/// 1 人の参加者の割り当て。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Assignment {
    pub order: [Block; 3],
    pub a_first: Ending,
    pub grammar: Grammar,
    pub drift: Drift,
}

impl Assignment {
    /// 正規の書式（台帳と割り当てを結び付けるために使う）。
    pub fn canonical(&self) -> String {
        let b = |x: Block| match x {
            Block::Blank => "E",
            Block::Decor => "D",
            Block::Portrait => "A",
        };
        format!(
            "order={},{},{};a_first={};grammar={};drift={}",
            b(self.order[0]),
            b(self.order[1]),
            b(self.order[2]),
            match self.a_first {
                Ending::None => "none",
                Ending::Seed => "seed",
            },
            match self.grammar {
                Grammar::Raw => "raw",
                Grammar::Lattice => "lattice",
            },
            match self.drift {
                Drift::None => "none",
                Drift::Diffuse => "diffuse",
            },
        )
    }
}

/// その日の条件。NDJSON の `eh3_day.condition` の値域そのもの。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Condition {
    Blank,
    Decor,
    PortraitNone,
    PortraitSeed,
}

impl Condition {
    /// `eh3_day.condition` に書く固定文字列（★ 値域を閉じる）。
    pub fn as_str(self) -> &'static str {
        match self {
            Condition::Blank => "blank",
            Condition::Decor => "decor",
            Condition::PortraitNone => "a_none",
            Condition::PortraitSeed => "a_seed",
        }
    }
}

/// 印の中身を割り当てに直す (純関数)。
///
/// ★ 4 つのキーがすべて 1 回ずつ揃い、値が値域の中にあるときだけ通す。
/// ⚠️ 欠け・重複・未知のキー・余分な空白以外の文字は拒む（立てたつもりを作らない）。
/// ⚠️ エラーの文に印の値を入れない（applog に割り当ての一部を平文で残さない）。
/// 先頭の BOM（メモ帳の UTF-8 保存）は読み飛ばす。
pub fn parse_assignment(text: &str) -> Result<Assignment, String> {
    let line = text.trim_start_matches('\u{feff}').trim();
    let mut order: Option<[Block; 3]> = None;
    let mut a_first: Option<Ending> = None;
    let mut grammar: Option<Grammar> = None;
    let mut drift: Option<Drift> = None;
    for part in line.split(';') {
        let (key, value) = part.split_once('=').ok_or("eh3.mode: a part has no '='")?;
        let (key, value) = (key.trim(), value.trim());
        match key {
            "order" => {
                if order.is_some() {
                    return Err("eh3.mode: order given twice".into());
                }
                order = Some(parse_order(value)?);
            }
            "a_first" => {
                if a_first.is_some() {
                    return Err("eh3.mode: a_first given twice".into());
                }
                a_first = Some(match value {
                    "none" => Ending::None,
                    "seed" => Ending::Seed,
                    _ => return Err("eh3.mode: bad a_first".into()),
                });
            }
            "grammar" => {
                if grammar.is_some() {
                    return Err("eh3.mode: grammar given twice".into());
                }
                grammar = Some(match value {
                    "raw" => Grammar::Raw,
                    "lattice" => Grammar::Lattice,
                    _ => return Err("eh3.mode: bad grammar".into()),
                });
            }
            "drift" => {
                if drift.is_some() {
                    return Err("eh3.mode: drift given twice".into());
                }
                drift = Some(match value {
                    "none" => Drift::None,
                    "diffuse" => Drift::Diffuse,
                    _ => return Err("eh3.mode: bad drift".into()),
                });
            }
            _ => return Err("eh3.mode: unknown key".into()),
        }
    }
    Ok(Assignment {
        order: order.ok_or("eh3.mode: order missing")?,
        a_first: a_first.ok_or("eh3.mode: a_first missing")?,
        grammar: grammar.ok_or("eh3.mode: grammar missing")?,
        drift: drift.ok_or("eh3.mode: drift missing")?,
    })
}

fn parse_order(value: &str) -> Result<[Block; 3], String> {
    let blocks: Vec<Block> = value
        .split(',')
        .map(|s| match s.trim() {
            "E" => Ok(Block::Blank),
            "D" => Ok(Block::Decor),
            "A" => Ok(Block::Portrait),
            _ => Err("eh3.mode: bad block".to_string()),
        })
        .collect::<Result<_, _>>()?;
    let [a, b, c] = blocks[..] else {
        return Err("eh3.mode: order needs 3 blocks".into());
    };
    if a == b || b == c || a == c {
        return Err("eh3.mode: order repeats a block".into());
    }
    Ok([a, b, c])
}

/// EH3 モードの判定 (純関数)。IO は呼び出し側が行い、その結果だけを渡す。
///
/// ★ 印を優先する（`o1::decide` と同じ）。⚠️ 印があって中身が不正なら、環境変数に落ちずに
/// `Err` を返す（配布の誤りを開発用の経路で隠さない）。
pub fn decide(
    marker: Option<&str>,
    env_value: Option<&str>,
) -> Result<Option<(Eh3Source, Assignment)>, String> {
    if let Some(text) = marker {
        return parse_assignment(text).map(|a| Some((Eh3Source::Marker, a)));
    }
    match env_value {
        Some(text) if !text.trim().is_empty() => {
            parse_assignment(text).map(|a| Some((Eh3Source::Env, a)))
        }
        _ => Ok(None),
    }
}

/// ⚠️★★★ **EH3 は O1 の上でだけ立てる** (純関数・判断 3 #1)。
///
/// O1 でない（通常運用・G1）なら EH3 を落とす。呼び出し側は落としたことを `tracing::warn!` で残す。
pub fn resolve(
    detected: Option<(Eh3Source, Assignment)>,
    o1_active: bool,
) -> Option<(Eh3Source, Assignment)> {
    if o1_active {
        detected
    } else {
        None
    }
}

/// `exe` に対応する印の想定パス (純関数)。★ 階層数は `g1` を再利用する（`o1::marker_path_for` と同じ）。
pub fn marker_path_for(exe: &Path, levels_up: usize) -> Option<PathBuf> {
    Some(crate::g1::folder_up(exe, levels_up)?.join(MARKER_FILE_NAME))
}

/// 現地時刻の「日」（4:00 区切り）を、1970-01-01 からの日数で返す (純関数)。
///
/// `utc_offset_secs` は呼び出し側が OS から取る（`analysis/` と同じく、ここでは時刻帯を引かない）。
pub fn local_day(ts_ms: u64, utc_offset_secs: i32) -> i64 {
    let local_secs = (ts_ms / 1000) as i64 + i64::from(utc_offset_secs);
    (local_secs - DAY_CUTOFF_HOUR * 3600).div_euclid(DAY_SECS)
}

/// 現地時刻の「その日の 0:00 からの分」(純関数)。時間帯の判定に使う（4:00 区切りではない暦の時刻）。
pub fn local_minute_of_day(ts_ms: u64, utc_offset_secs: i32) -> u32 {
    let local_secs = (ts_ms / 1000) as i64 + i64::from(utc_offset_secs);
    (local_secs.rem_euclid(DAY_SECS) / 60) as u32
}

/// `day_index`（1 始まり）の条件 (純関数)。期間の後（16 日目以降）は `None`。
pub fn condition_for(a: &Assignment, day_index: u32) -> Option<Condition> {
    if day_index == 0 || day_index > PERIOD_DAYS {
        return None;
    }
    let block = a.order[((day_index - 1) / BLOCK_DAYS) as usize];
    let k = (day_index - 1) % BLOCK_DAYS; // ブロックの中の 0 始まりの日
    Some(match block {
        Block::Blank => Condition::Blank,
        Block::Decor => Condition::Decor,
        Block::Portrait => {
            let ending = if k.is_multiple_of(2) {
                a.a_first
            } else {
                a.a_first.other()
            };
            match ending {
                Ending::None => Condition::PortraitNone,
                Ending::Seed => Condition::PortraitSeed,
            }
        }
    })
}

/// 数えた稼働日の台帳（端末の中だけ・`~/.gse/eh3_state.json`）。
///
/// ⚠️ NDJSON にも提出物にも入れない。稼働日の日付は打鍵の記録からも分かるので、新しい情報を作らない。
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct DayLedger {
    /// 数えた日（`local_day` の値）。昇順・重複なし。
    pub days: Vec<i64>,
    /// この台帳を作った割り当て（`Assignment::canonical`）。割り当てが替わったら台帳を使わない
    /// （研究者が同じ PC で試してから配った・印を差し替えた、で途中の日から始まらないように）。
    #[serde(default)]
    pub assignment: Option<String>,
}

/// その日の割り当ての結果。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct DayAssignment {
    /// 1 始まりの稼働日の番号。
    pub day_index: u32,
    /// その日の条件。期間の後なら `None`。
    pub condition: Option<Condition>,
}

impl DayLedger {
    /// 台帳を検める（昇順・重複なしに直す）。手で壊されたファイルを読んだ後に呼ぶ。
    pub fn normalized(mut self) -> Self {
        self.days.sort_unstable();
        self.days.dedup();
        self
    }

    /// `day` に打鍵を観測した (純関数的な更新)。
    ///
    /// 戻り値は割り当て（無ければ `None`）と「この呼び出しで新しく数えた」か。
    ///
    /// ⚠️ 時計が戻って、最後に数えた日より前の・まだ数えていない日が来たときは、**数えず割り当てもしない**
    /// （途中に挿し込むと後の日の番号が繰り下がり、すでに書いた `eh3_day` 行とブロックの境界がずれる）。
    pub fn observe(&mut self, day: i64, a: &Assignment) -> (Option<DayAssignment>, bool) {
        if let Some(found) = self.lookup(day, a) {
            return (Some(found), false);
        }
        if self.days.last().is_some_and(|last| day < *last) {
            return (None, false);
        }
        self.days.push(day);
        let day_index = self.days.len() as u32;
        (
            Some(DayAssignment {
                day_index,
                condition: condition_for(a, day_index),
            }),
            true,
        )
    }

    /// `day` がすでに数えた日なら、その日の割り当てを返す（打鍵を観測する前の起動で使う）。
    pub fn lookup(&self, day: i64, a: &Assignment) -> Option<DayAssignment> {
        let pos = self.days.binary_search(&day).ok()?;
        let day_index = pos as u32 + 1;
        Some(DayAssignment {
            day_index,
            condition: condition_for(a, day_index),
        })
    }

    /// 期間を終えたか（15 稼働日を数え、`day` がそれより後の日）。
    pub fn period_over(&self, day: i64) -> bool {
        // 15 日目（台帳の 15 番目）より後の日。16 日目を数えた後でも同じ答えになる。
        self.days
            .get(PERIOD_DAYS as usize - 1)
            .is_some_and(|fifteenth| day > *fifteenth)
    }
}

/// 稼働日の台帳のファイル名（`~/.gse/eh3_state.json`）。
pub const STATE_FILE_NAME: &str = "eh3_state.json";

/// 稼働日の台帳の置き場。
pub fn state_path() -> Option<PathBuf> {
    crate::submission::home_dir().map(|h| h.join(".gse").join(STATE_FILE_NAME))
}

/// 台帳を読んだ結果。
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum LedgerLoad {
    /// ファイルが無い（初めての起動）。
    Fresh,
    /// 読めた。
    Loaded(DayLedger),
    /// ⚠️ ファイルはあるが読めない・壊れている。
    ///
    /// 空の台帳から数え直すと、条件が 1 日目からやり直しになり、同じブロックを 2 度回してしまう。
    /// → この起動では日の割り当てをしない（`eh3_day` 行が出ないので、研究者が事後に気づける）。
    Broken,
}

/// 台帳を読む (IO あり)。
pub fn load_ledger(path: &Path) -> LedgerLoad {
    match std::fs::read_to_string(path) {
        Ok(text) => match serde_json::from_str::<DayLedger>(&text) {
            Ok(l) => LedgerLoad::Loaded(l.normalized()),
            Err(_) => LedgerLoad::Broken,
        },
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => LedgerLoad::Fresh,
        Err(_) => LedgerLoad::Broken,
    }
}

/// 台帳を書く (IO あり)。一時ファイルに書いてから置き換える（書きかけで落ちても壊れない）。
///
/// ★ repo は `anyhow` に依存していないので、`std::io::Result` で返す（`submission.rs` と同じ）。
pub fn save_ledger(path: &Path, ledger: &DayLedger) -> std::io::Result<()> {
    if let Some(dir) = path.parent() {
        std::fs::create_dir_all(dir)?;
    }
    let tmp = path.with_extension("json.tmp");
    {
        use std::io::Write;
        let mut f = std::fs::File::create(&tmp)?;
        f.write_all(&serde_json::to_vec(ledger).map_err(std::io::Error::other)?)?;
        // 電源断で中身の空の台帳が残ると、以後ずっと `Broken` になって研究が止まる。
        f.sync_all()?;
    }
    std::fs::rename(&tmp, path)?;
    Ok(())
}

/// 打鍵と起動から、その日の割り当てを 1 日 1 回だけ出す。
///
/// 状態は台帳と「この走行で行を出した日」だけ。台帳の保存の失敗は呼び出し側へ返さず、
/// 次の打鍵（60 秒おき）でもう一度書く（数えた日は台帳の中身なので、書けなかった日を取りこぼさない）。
#[derive(Debug)]
pub struct DayTracker {
    ledger: Option<DayLedger>,
    path: Option<PathBuf>,
    emitted_day: Option<i64>,
    /// 台帳の保存に失敗した（次の打鍵でもう一度書く。書けないまま終了すると、再起動の後にその日が
    /// 数え直しになるので、書けるまで試す。打鍵のたびに試さないよう 60 秒おきに間引く）。
    unsaved: bool,
    last_save_try_ms: u64,
}

impl DayTracker {
    /// `load` が `Broken` か、台帳が別の割り当てで作られていたら、この走行では何も割り当てない。
    pub fn new(load: LedgerLoad, path: Option<PathBuf>, a: &Assignment) -> Self {
        let canonical = a.canonical();
        let ledger = match load {
            LedgerLoad::Fresh => Some(DayLedger {
                days: Vec::new(),
                assignment: Some(canonical),
            }),
            LedgerLoad::Loaded(l) if l.assignment.as_deref() == Some(canonical.as_str()) => Some(l),
            LedgerLoad::Loaded(_) => {
                tracing::error!(
                    "EH3 day ledger was made for another assignment; no daily condition this run"
                );
                None
            }
            LedgerLoad::Broken => None,
        };
        Self {
            ledger,
            path,
            emitted_day: None,
            unsaved: false,
            last_save_try_ms: 0,
        }
    }

    /// 保存の再試行の間隔。
    const SAVE_RETRY_MS: u64 = 60_000;

    fn save(&mut self, now_ms: u64) {
        self.last_save_try_ms = now_ms;
        if let (Some(p), Some(ledger)) = (&self.path, &self.ledger) {
            match save_ledger(p, ledger) {
                Ok(()) => self.unsaved = false,
                Err(e) => {
                    // ⚠️ 日付も条件も出さない。失敗が続く間は最初の 1 回だけ残す。
                    if !self.unsaved {
                        tracing::warn!("EH3 day ledger could not be saved: {e}");
                    }
                    self.unsaved = true;
                }
            }
        }
    }

    /// 起動時: その日をすでに数えていれば、その日の割り当てを返す（行を出すため）。
    pub fn on_start(
        &mut self,
        now_ms: u64,
        utc_offset_secs: i32,
        a: &Assignment,
    ) -> Option<DayAssignment> {
        let day = local_day(now_ms, utc_offset_secs);
        let got = self.ledger.as_ref()?.lookup(day, a)?;
        self.emitted_day = Some(day);
        got.condition.map(|_| got)
    }

    /// 打鍵を観測した: その日を初めて扱うなら、数えて割り当てを返す。期間の後なら `None`。
    pub fn on_press(
        &mut self,
        ts_ms: u64,
        utc_offset_secs: i32,
        a: &Assignment,
    ) -> Option<DayAssignment> {
        let day = local_day(ts_ms, utc_offset_secs);
        if self.unsaved && ts_ms.saturating_sub(self.last_save_try_ms) >= Self::SAVE_RETRY_MS {
            self.save(ts_ms);
        }
        if self.emitted_day == Some(day) {
            return None;
        }
        let ledger = self.ledger.as_mut()?;
        if ledger.period_over(day) {
            // 期間の後は台帳を伸ばさない（書き込みも行も要らない）。
            self.emitted_day = Some(day);
            return None;
        }
        let (got, newly) = ledger.observe(day, a);
        self.emitted_day = Some(day);
        let got = got?;
        if newly {
            self.save(ts_ms);
        }
        got.condition.map(|_| got)
    }

    /// 行を出し直す: その日をすでに数えていれば、その日の割り当てを返す（再開・日次の切り替えの後に使う）。
    /// 条件は日中に変わらないので、出し直しても別の日の条件にはならない。
    pub fn reemit_today(
        &mut self,
        now_ms: u64,
        utc_offset_secs: i32,
        a: &Assignment,
    ) -> Option<DayAssignment> {
        self.on_start(now_ms, utc_offset_secs, a)
    }

    /// 行を送れなかった（チャネルが満杯）: 次の打鍵でもう一度出す。
    pub fn forget_emitted(&mut self) {
        self.emitted_day = None;
    }

    /// その日の条件（割り当て済みなら）。肖像・招待の層が読む。
    pub fn today(&self, now_ms: u64, utc_offset_secs: i32, a: &Assignment) -> Option<Condition> {
        let day = local_day(now_ms, utc_offset_secs);
        self.ledger.as_ref()?.lookup(day, a)?.condition
    }

    /// 期間を終えたか。台帳が壊れているときは `false`（何もしない側）。
    pub fn period_over(&self, now_ms: u64, utc_offset_secs: i32) -> bool {
        let day = local_day(now_ms, utc_offset_secs);
        self.ledger.as_ref().is_some_and(|l| l.period_over(day))
    }
}

/// 招待の設定のファイル名（`~/.gse/eh3_invitation.json`・端末の中だけ）。
///
/// ⚠️ 設定の値は NDJSON・applog・提出物に出さない（時間帯は生活時間の代理になりうる・ADR-035 D4・
/// `.steering/20261011-portrait-eh3-impl/design.md` §2.3）。
pub const INVITATION_SETTINGS_FILE_NAME: &str = "eh3_invitation.json";

/// 招待の設定の置き場。
pub fn invitation_settings_path() -> Option<PathBuf> {
    crate::submission::home_dir().map(|h| h.join(".gse").join(INVITATION_SETTINGS_FILE_NAME))
}

/// 招待の設定を読む。
///
/// - 無い（初めての起動）: 既定値（ADR-035 D2: 出す・時期と上限は狭い側）。
/// - あるのに読めない・壊れている: **出さない**・狭い側（本人が「出さない」を選んだ後にファイルが壊れても、
///   黙って提示を再開しない）。applog には中身を含めずに 1 行だけ残す。
pub fn load_invitation_settings(path: &Path) -> crate::analysis::invitation::Settings {
    use crate::analysis::invitation::Settings;
    match std::fs::read_to_string(path) {
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Settings::default(),
        Ok(t) => match serde_json::from_str(&t) {
            Ok(s) => s,
            Err(_) => {
                tracing::warn!("EH3 invitation settings file is unreadable; invitations are off");
                Settings {
                    enabled: false,
                    ..Settings::default()
                }
            }
        },
        Err(_) => {
            tracing::warn!("EH3 invitation settings file is unreadable; invitations are off");
            Settings {
                enabled: false,
                ..Settings::default()
            }
        }
    }
}

/// 招待の設定を書く（一時ファイル → 同期 → 置き換え）。
pub fn save_invitation_settings(
    path: &Path,
    settings: &crate::analysis::invitation::Settings,
) -> std::io::Result<()> {
    if let Some(dir) = path.parent() {
        std::fs::create_dir_all(dir)?;
    }
    let tmp = path.with_extension("json.tmp");
    {
        use std::io::Write;
        let mut f = std::fs::File::create(&tmp)?;
        f.write_all(&serde_json::to_vec(settings).map_err(std::io::Error::other)?)?;
        f.sync_all()?;
    }
    std::fs::rename(&tmp, path)
}

/// フォーカス遷移の行を出すか (純関数)。
///
/// EH3 では、GSE 自身の窓へ移る遷移（`own`）と、GSE の窓から戻る遷移（直前が `own`）を記録しない。
/// 招待の図像を押して説明と設定の窓を開いた・閉じたことが時刻の列から読めないようにする
/// （`.steering/20261011-portrait-eh3-impl/decisions.md` 判断 6 #3・台帳 肖13 の横の経路）。
/// 代償: A → GSE → B と移ったときの A→B の 1 本も落ちる。EH3 でなければ常に出す（O1 の記録は変えない）。
pub fn focus_row_allowed(eh3: bool, own: bool, last_own: bool) -> bool {
    !(eh3 && (own || last_own))
}

static EH3: std::sync::OnceLock<Option<(Eh3Source, Assignment)>> = std::sync::OnceLock::new();

/// 起動時に 1 回だけモードを確定させる。★ 2 回目以降は黙って無視する（`o1::set_mode` と同じ）。
pub fn set_mode(mode: Option<(Eh3Source, Assignment)>) {
    let _ = EH3.set(mode);
}

/// EH3 モードの引き金。`None` なら EH3 ではない。
pub fn mode() -> Option<Eh3Source> {
    EH3.get().copied().flatten().map(|(s, _)| s)
}

/// EH3 の割り当て。`None` なら EH3 ではない。
pub fn assignment() -> Option<Assignment> {
    EH3.get().copied().flatten().map(|(_, a)| a)
}

/// EH3 モードか。
pub fn is_eh3() -> bool {
    mode().is_some()
}

/// 実行環境から EH3 モードを検出する (IO あり)。★ `run()` から起動時に 1 回だけ呼ぶ。
///
/// 印の探索に失敗した場合は印無しとして扱う（`o1::detect_from_env` と同じ）。
/// ⚠️ 印が読めて中身が不正なときは `Err`（呼び出し側が EH3 を立てずに `tracing::error!` で残す）。
pub fn detect_from_env() -> Result<Option<(Eh3Source, Assignment)>, String> {
    let marker = std::env::current_exe()
        .ok()
        .and_then(|exe| marker_path_for(&exe, crate::g1::exe_to_folder_levels()))
        .filter(|p| p.is_file())
        .map(|p| std::fs::read_to_string(&p).map_err(|e| format!("eh3.mode: cannot read: {e}")))
        .transpose()?;
    let env_value = std::env::var(ENV_VAR).ok();
    decide(marker.as_deref(), env_value.as_deref())
}

#[cfg(test)]
mod tests {
    use super::*;

    const OK: &str = "order=E,D,A;a_first=seed;grammar=raw;drift=none";

    fn assign() -> Assignment {
        parse_assignment(OK).expect("valid")
    }

    #[test]
    fn parses_a_full_assignment() {
        let a = assign();
        assert_eq!(a.order, [Block::Blank, Block::Decor, Block::Portrait]);
        assert_eq!(a.a_first, Ending::Seed);
        assert_eq!(a.grammar, Grammar::Raw);
        assert_eq!(a.drift, Drift::None);
        // 空白と改行は許す
        assert_eq!(
            parse_assignment(" order = A,E,D ; a_first=none;grammar=lattice;drift=diffuse\n")
                .expect("valid")
                .order,
            [Block::Portrait, Block::Blank, Block::Decor]
        );
    }

    #[test]
    fn rejects_broken_assignments() {
        for bad in [
            "",
            "order=E,D,A;a_first=seed;grammar=raw", // 欠け
            "order=E,D,A;a_first=seed;grammar=raw;drift=none;x=1", // 未知のキー
            "order=E,D,A;a_first=seed;a_first=none;grammar=raw;drift=none", // 重複
            "order=E,E,A;a_first=seed;grammar=raw;drift=none", // ブロックの重複
            "order=E,D;a_first=seed;grammar=raw;drift=none", // 2 つだけ
            "order=E,D,A,A;a_first=seed;grammar=raw;drift=none", // 4 つ
            "order=E,D,X;a_first=seed;grammar=raw;drift=none", // 未知のブロック
            "order=E,D,A;a_first=yes;grammar=raw;drift=none",
            "order=E,D,A;a_first=seed;grammar=ordinal;drift=none", // 外した文法
            "order=E,D,A;a_first=seed;grammar=raw;drift=fade",
        ] {
            assert!(parse_assignment(bad).is_err(), "should reject {bad:?}");
        }
    }

    #[test]
    fn marker_wins_and_a_bad_marker_is_an_error() {
        let env = "order=A,D,E;a_first=none;grammar=lattice;drift=none";
        let (src, a) = decide(Some(OK), Some(env)).unwrap().unwrap();
        assert_eq!(src, Eh3Source::Marker);
        assert_eq!(a, assign());
        // ⚠️ 印が不正なら環境変数に落ちない
        assert!(decide(Some("garbage"), Some(env)).is_err());
        assert_eq!(decide(None, Some(env)).unwrap().unwrap().0, Eh3Source::Env);
        assert_eq!(decide(None, None).unwrap(), None);
        assert_eq!(decide(None, Some("  ")).unwrap(), None);
    }

    #[test]
    fn eh3_needs_o1() {
        let d = Some((Eh3Source::Marker, assign()));
        assert!(resolve(d, true).is_some());
        assert!(resolve(d, false).is_none(), "O1 でなければ EH3 を立てない");
        assert!(resolve(None, true).is_none());
    }

    #[test]
    fn local_day_cuts_at_four_in_the_morning() {
        // 2026-10-12 00:00:00 UTC = 1_760_227_200 s
        let midnight_utc = 1_760_227_200_000u64;
        let jst = 9 * 3600;
        // JST 2026-10-12 03:59 と 04:00
        let t0359 = midnight_utc - 9 * 3_600_000 + (3 * 60 + 59) * 60_000;
        let t0400 = midnight_utc - 9 * 3_600_000 + 4 * 3_600_000;
        assert_eq!(local_day(t0359, jst) + 1, local_day(t0400, jst));
        // 前日の 23:00 と 03:59 は同じ日
        let t2300_prev = t0400 - 5 * 3_600_000;
        assert_eq!(local_day(t2300_prev, jst), local_day(t0359, jst));
        assert_eq!(local_minute_of_day(t0400, jst), 240);
        // 負の時差でも壊れない
        // JST 04:00 = UTC 19:00 = UTC-5 の 14:00
        assert_eq!(local_minute_of_day(t0400, -5 * 3600), 14 * 60);
    }

    #[test]
    fn conditions_follow_the_order_and_alternate_inside_a() {
        let a = parse_assignment("order=A,E,D;a_first=seed;grammar=raw;drift=none").unwrap();
        let got: Vec<&str> = (1..=PERIOD_DAYS)
            .map(|d| condition_for(&a, d).unwrap().as_str())
            .collect();
        assert_eq!(
            got,
            [
                "a_seed", "a_none", "a_seed", "a_none", "a_seed", //
                "blank", "blank", "blank", "blank", "blank", //
                "decor", "decor", "decor", "decor", "decor",
            ]
        );
        let b = parse_assignment("order=E,D,A;a_first=none;grammar=raw;drift=none").unwrap();
        assert_eq!(condition_for(&b, 11), Some(Condition::PortraitNone));
        assert_eq!(condition_for(&b, 12), Some(Condition::PortraitSeed));
        assert_eq!(condition_for(&b, 0), None);
        assert_eq!(condition_for(&b, 16), None, "期間の後");
    }

    #[test]
    fn ledger_counts_each_day_once_and_skips_unused_days() {
        let a = assign();
        let mut l = DayLedger::default();
        let (d1, new1) = l.observe(100, &a);
        assert!(new1);
        assert_eq!(d1.unwrap().day_index, 1);
        let (again, new_again) = l.observe(100, &a);
        assert!(!new_again, "同じ日は数え直さない");
        assert_eq!(again.unwrap().day_index, 1);
        // 3 日あけて使っても次の稼働日は 2
        let (d2, _) = l.observe(104, &a);
        assert_eq!(d2.unwrap().day_index, 2);
        assert_eq!(l.lookup(104, &a).unwrap().day_index, 2);
        assert_eq!(l.lookup(103, &a), None, "使っていない日は数えない");
    }

    #[test]
    fn ledger_ignores_a_day_earlier_than_the_last_counted() {
        // 時計が戻った: [100, 104] に 102 が来ても挿し込まず、104 は 2 日目のまま。
        let a = assign();
        let mut l = DayLedger::default();
        l.observe(100, &a);
        l.observe(104, &a);
        let (got, newly) = l.observe(102, &a);
        assert_eq!(got, None);
        assert!(!newly);
        assert_eq!(l.days, vec![100, 104]);
        assert_eq!(l.lookup(104, &a).unwrap().day_index, 2);
        // 戻った先が数えた日なら、その日の割り当てを返す
        assert_eq!(l.observe(100, &a).0.unwrap().day_index, 1);
    }

    #[test]
    fn ledger_period_is_over_after_fifteen_days() {
        let a = assign();
        let mut l = DayLedger::default();
        for d in 0..PERIOD_DAYS as i64 {
            l.observe(d, &a);
        }
        assert!(
            !l.period_over(PERIOD_DAYS as i64 - 1),
            "15 日目の当日はまだ期間の中"
        );
        assert!(l.period_over(PERIOD_DAYS as i64));
        let (d16, _) = l.observe(PERIOD_DAYS as i64, &a);
        assert_eq!(d16.unwrap().condition, None, "16 日目は期間の後");
        assert!(
            l.period_over(PERIOD_DAYS as i64),
            "16 日目を数えた後も同じ答え"
        );
    }

    const DAY_MS: u64 = 86_400_000;
    // 2026-10-12 12:00 JST
    const NOON_JST: u64 = 1_760_227_200_000 + 3 * 3_600_000;
    const JST: i32 = 9 * 3600;

    #[test]
    fn tracker_emits_once_per_day_and_persists() {
        let dir = std::env::temp_dir().join(format!("gse_eh3_tracker_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        let path = dir.join(STATE_FILE_NAME);
        let a = assign();
        let mut t = DayTracker::new(load_ledger(&path), Some(path.clone()), &a);
        assert_eq!(
            t.on_start(NOON_JST, JST, &a),
            None,
            "数える前の起動では出さない"
        );
        let d1 = t.on_press(NOON_JST, JST, &a).expect("1 日目を数える");
        assert_eq!(d1.day_index, 1);
        assert_eq!(
            t.on_press(NOON_JST + 1000, JST, &a),
            None,
            "同じ日に 2 回出さない"
        );
        assert_eq!(t.today(NOON_JST, JST, &a), Some(Condition::Blank));
        // 送れなかったら、次の打鍵で出し直す
        t.forget_emitted();
        assert_eq!(t.on_press(NOON_JST + 2000, JST, &a).unwrap().day_index, 1);
        // 再開・切り替えの後の出し直し
        assert_eq!(
            t.reemit_today(NOON_JST + 3000, JST, &a).unwrap().day_index,
            1
        );
        // 再起動しても同じ日は数え直さず、起動時に 1 回だけ出す
        let mut t2 = DayTracker::new(load_ledger(&path), Some(path.clone()), &a);
        assert_eq!(t2.on_start(NOON_JST + 5000, JST, &a).unwrap().day_index, 1);
        assert_eq!(t2.on_press(NOON_JST + 6000, JST, &a), None);
        // 翌日は 2 日目
        assert_eq!(
            t2.on_press(NOON_JST + DAY_MS, JST, &a).unwrap().day_index,
            2
        );
        // 別の割り当てで読むと、何も割り当てない（途中の日から始めない）
        let other = parse_assignment("order=A,D,E;a_first=none;grammar=raw;drift=none").unwrap();
        let mut t3 = DayTracker::new(load_ledger(&path), Some(path.clone()), &other);
        assert_eq!(t3.on_press(NOON_JST + 2 * DAY_MS, JST, &other), None);
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn a_failed_save_is_retried_on_the_next_press() {
        // 保存先を「ファイルの下」にして書けなくする → 書ける場所に直すと次の打鍵で保存される
        let dir = std::env::temp_dir().join(format!("gse_eh3_unsaved_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let blocker = dir.join("blocker");
        std::fs::write(&blocker, b"x").unwrap();
        let a = assign();
        let mut t = DayTracker::new(LedgerLoad::Fresh, Some(blocker.join(STATE_FILE_NAME)), &a);
        assert!(t.on_press(NOON_JST, JST, &a).is_some());
        assert!(t.unsaved, "書けなかったことを覚える");
        let good = dir.join(STATE_FILE_NAME);
        t.path = Some(good.clone());
        assert_eq!(
            t.on_press(NOON_JST + 1000, JST, &a),
            None,
            "同じ日の行は出し直さない"
        );
        assert!(t.unsaved, "60 秒たつまでは試さない");
        assert_eq!(t.on_press(NOON_JST + 61_000, JST, &a), None);
        assert!(!t.unsaved);
        assert!(matches!(load_ledger(&good), LedgerLoad::Loaded(l) if l.days.len() == 1));
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn a_broken_ledger_assigns_nothing() {
        let a = assign();
        let mut t = DayTracker::new(LedgerLoad::Broken, None, &a);
        assert_eq!(t.on_press(NOON_JST, JST, &a), None);
        assert_eq!(t.on_start(NOON_JST, JST, &a), None);
        assert_eq!(t.today(NOON_JST, JST, &a), None);
        assert!(!t.period_over(NOON_JST, JST));
        // 壊れたファイルを Broken と読む
        let dir = std::env::temp_dir().join(format!("gse_eh3_broken_{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let p = dir.join(STATE_FILE_NAME);
        std::fs::write(&p, b"{not json").unwrap();
        assert_eq!(load_ledger(&p), LedgerLoad::Broken);
        assert_eq!(load_ledger(&dir.join("absent.json")), LedgerLoad::Fresh);
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn tracker_stops_assigning_after_the_period() {
        let a = assign();
        let mut t = DayTracker::new(LedgerLoad::Fresh, None, &a);
        for k in 0..u64::from(PERIOD_DAYS) {
            assert!(t.on_press(NOON_JST + k * DAY_MS, JST, &a).is_some());
        }
        let after = NOON_JST + u64::from(PERIOD_DAYS) * DAY_MS;
        assert_eq!(t.on_press(after, JST, &a), None, "16 日目は行を出さない");
        assert!(t.period_over(after, JST));
        assert_eq!(t.today(after, JST, &a), None);
    }

    #[test]
    fn ledger_normalizes_a_hand_edited_file() {
        let l = DayLedger {
            days: vec![5, 3, 5, 1],
            assignment: None,
        }
        .normalized();
        assert_eq!(l.days, vec![1, 3, 5]);
    }

    #[test]
    fn invitation_settings_round_trip_and_fall_back_to_the_narrow_default() {
        use crate::analysis::invitation::{DailyCap, Settings, TimeWindow};
        let dir = std::env::temp_dir().join(format!("gse_eh3_inv_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        let p = dir.join(INVITATION_SETTINGS_FILE_NAME);
        assert_eq!(
            load_invitation_settings(&p),
            Settings::default(),
            "無ければ既定"
        );
        let s = Settings {
            enabled: false,
            window: TimeWindow::Wide,
            cap: DailyCap::Four,
        };
        save_invitation_settings(&p, &s).unwrap();
        assert_eq!(load_invitation_settings(&p), s);
        // 自由な値・未知の欄・壊れたファイルは読まず、「出さない」・狭い側に倒れる
        let off = Settings {
            enabled: false,
            ..Settings::default()
        };
        for bad in [
            r#"{"enabled":true,"window":"all_day","cap":"four"}"#,
            r#"{"enabled":true,"window":"wide","cap":"four","threshold":0.1}"#,
            "{",
        ] {
            std::fs::write(&p, bad).unwrap();
            assert_eq!(load_invitation_settings(&p), off, "{bad}");
        }
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn focus_rows_into_and_out_of_gse_are_dropped_only_in_eh3() {
        // O1（EH3 でない）は従来どおり全部出す
        for own in [false, true] {
            for last in [false, true] {
                assert!(focus_row_allowed(false, own, last));
            }
        }
        // EH3: 他のアプリどうしは出す・GSE へ移る / GSE から戻るは出さない
        assert!(focus_row_allowed(true, false, false));
        assert!(!focus_row_allowed(true, true, false));
        assert!(!focus_row_allowed(true, false, true));
        assert!(!focus_row_allowed(true, true, true));
    }

    #[test]
    fn a_bom_is_skipped_and_errors_do_not_echo_the_marker() {
        let with_bom = format!("\u{feff}{OK}");
        assert_eq!(parse_assignment(&with_bom).unwrap(), assign());
        let e = parse_assignment("order=E,E,A;a_first=seed;grammar=raw;drift=none").unwrap_err();
        assert!(!e.contains("E,E,A"), "エラーに印の値を入れない: {e}");
        assert_eq!(assign().canonical(), OK);
    }
}
