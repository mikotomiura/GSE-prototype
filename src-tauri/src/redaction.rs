//! 被験者による **区間指定削除**（「昨日の 14:00〜15:00 を消して」）の実装。
//!
//! ## ⚠️★★★ なぜこれが要るのか
//!
//! ADR-014 **判断 3** は O1 の倫理審査を不要と判断したが、★ その根拠 4 件のうち **根拠 3** は
//! 逐語「**被験者が停止・削除できる** —— 稼働中インジケータ / 即時の一時停止 /
//! **事後の区間指定削除**（D7）」であり、⚠️ 崩れる条件も逐語で書かれている ——
//! 「**削除 UI が実装されないまま収集を始めた時点で崩れる**」。
//! → ★ **本モジュールが無いまま O1 の収集を始めてはならない。**
//!
//! ★ 同意文書ドラフト `§4` は既に被験者へ「**時間帯を指定して削除できます。
//! ⚠️ 理由を説明する必要はありません**」と約束している。
//!
//! ## ★ 設計上の約束（★ 破ると約束違反になる）
//!
//! | # | 約束 | ★ 実装での担保 |
//! |---|---|---|
//! | 1 | ⚠️★★★ **理由を聞かない** | ★ 引数に理由が**無い**。UI にも入力欄を置かない |
//! | 2 | ★ **原本を壊さない** | ★ 一時ファイルへ書いて `rename`（途中で落ちても原本が残る） |
//! | 3 | ⚠️ **消した「事実」は残す** | ★ 台帳へ 1 行 append。⚠️ **何を消したかは書かない** |
//! | 4 | ⚠️ **書きかけのファイルを壊さない** | ★ 呼び出し側が現行セッションを `skip` に渡す |
//! | 5 | ⚠️★★★ **削除した位置に「元に無い onset」を立てない** | ★ 入口で最小幅まで**終端側へ広げる**（[`widen_to_minimum_width`]） |
//!
//! ## ⚠️ OS API を呼ばない
//!
//! `architecture-rules` ルール 2 / 4 に従い、本モジュールは **std のファイル操作のみ**で構成する
//! (`input/` にも `analysis/` にも属さない独立層)。

use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};

/// 本モジュールのエラー型。
///
/// ⚠️★ **`anyhow` は使わない。** ★ このリポジトリは `anyhow` を依存に持たず
/// `Result<_, String>` / `tauri::Result` で通している（`overlay_panel.rs` / `packaging.rs` に明記）。
/// ⚠️ `docs/agent-shared.md` の「`anyhow::Result` を使用」は**現行の依存関係と食い違っている**
/// (2026-08-23 実測: `src-tauri/Cargo.toml` に `anyhow` の行が無い)。→ ★ 実装に合わせる。
type Result<T> = std::result::Result<T, String>;

/// 台帳のファイル名。
///
/// ⚠️★★★ **拡張子を `.ndjson` にしない。**
/// `reconcile.rs` の収束器は `gse_*.ndjson` を提出候補として拾う。★ 接頭辞だけでも弾かれるが、
/// **拡張子でも外して二重に**する —— ⚠️ 台帳が提出物へ混ざると、**削除を要求した事実そのものが
/// 研究者へ渡る**ことになり、「理由を聞かない」の趣旨が裏から破れる。
pub const LEDGER_FILE_NAME: &str = "redaction_ledger.jsonl";

/// 1 回の削除要求の結果。
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct RedactionSummary {
    /// 実際に書き換えたファイル数（★ 1 行も落ちなかったファイルは数えない）。
    pub files_touched: usize,
    /// 落とした行数の合計。
    pub lines_removed: usize,
    /// ⚠️ 走査したが**書きかけなので飛ばした**ファイル数（★ 現行セッション）。
    pub files_skipped: usize,
}

/// ⚠️★★★ 区間指定削除の**最小幅**（ミリ秒）。★ これ未満の要求は [`widen_to_minimum_width`] が広げる。
///
/// ## なぜ要るのか（ADR-030 **D8 (b-2)** ／ 補訂 1 項目 5 ／ `blockers.md` **起票 15**）
///
/// 1Hz の `feat` 列に穴がある区間では、`stall onset` の条件 B の連続を切る。
/// ⚠️★★★ **ところが穴は `隣接差 > hole_gap_ms` で判定する**（`hole_gap_ms` の既定は 2 tick = 2,000 ms）。
/// → ★ **`feat` 行が 1 本だけ欠ける幅の削除は穴にならず**、
/// 1 秒おきの `feat` の中で `[30,900, 31,500]` を消すと**元に無い onset が削除区間の内側に立つ**
/// （★ 実測）。⚠️ 被験者が消すよう求めた位置に onset が出ては、削除の約束が裏から破れる。
///
/// ## ★ なぜ 60,000 か
///
/// 現行 UI の削除入力は `datetime-local`（**秒なし**）なので、UI が作りうる区間の幅は
/// 0 か **60,000 以上**になる。★ その最小の非 0 幅に揃える（＝ 現行 UI の被験者から見た挙動は
/// 「同じ分を両端に入れたときに 1 分消える」だけが変わる）。
///
/// ⚠️★★★ **`hole_gap_ms` より大きいことを保つ**（★ 大小の検査は `tests` にある）。
/// `hole_gap_ms` の値を変えるときは**この値も同時に見直す**（補訂 1 項目 5）。
pub const MIN_REDACTION_WIDTH_MS: u64 = 60_000;

/// 削除要求の区間 `[from_ms, to_ms]` を、[`MIN_REDACTION_WIDTH_MS`] を満たす形へ直す。
///
/// - ★ **広げる向きは終端側**（`to_ms = from_ms + MIN_REDACTION_WIDTH_MS`）。
///   `from_ms` は被験者が「**ここから**消したい」と言った点なので**動かさない**
///   （⚠️ 対称に広げると**指定していない過去**が消える）。
/// - ★ 幅が既に最小幅以上なら **1 ms も広げない**（過剰に消さない）。
/// - ⚠️★★★ **拒否しない。** 被験者が「消してくれ」と言ったのに消えないのは約束違反である
///   （補訂 1 項目 5 逐語「**削除は広げる側に倒す。被験者への約束は『その時間帯が消える』ことである**」）。
/// - ⚠️ `from_ms > to_ms` は**従来どおりエラー**（★ 空区間として黙って全消し／無視にしない）。
///
/// ★ 純関数。ファイル I/O を持たないので境界条件をテストで固定できる。
pub fn widen_to_minimum_width(from_ms: u64, to_ms: u64) -> Result<(u64, u64)> {
    if from_ms > to_ms {
        return Err("開始時刻が終了時刻より後になっています。".to_string());
    }
    // ⚠️ `saturating_add`: `from_ms` が `u64::MAX` 近傍でも桁あふれで**狭まらない**ようにする。
    let min_to_ms = from_ms.saturating_add(MIN_REDACTION_WIDTH_MS);
    Ok((from_ms, to_ms.max(min_to_ms)))
}

/// NDJSON 1 行が「いつの記録か」を返す。⚠️ ★ **`meta` 行は常に `None`** である。
///
/// ★ 主たる対象は `t` である（`key` / `feat` / `paste` / `pointer_bin` / `activity_label` / …）。
///
/// ## ⚠️★★★ 2026-09-14: **自己申告行が 1 行も消えていなかった**（ADR-031 **D6**）
///
/// ★ 旧実装は `"t"` **だけ**を読んでいた。⚠️ ところが `logger.rs` は
/// **`realtime_label` / `vignette_response` に `"ts"`**、**`probe_assignment` に
/// `"scheduled_ts"`** を書いている。→ ★ 本関数が `None` を返し、
/// [`retain_outside_range`] が**残していた**。
///
/// ⚠️★★★ **画面には「消しました（… 件）」と出るのに、被験者の自己申告は端末に残っていた。**
/// ★ 削除 UI は O1 以外でも出る（`src/components/RecordingControls.tsx` の `else` 枝）ので、
/// **通常運用（v0.3 較正）で live な欠陥**だった。
/// ⚠️ 既存テストは `key` と `pointer_bin`（どちらも `"t"`）しか見ておらず、素通りしていた。
///
/// ★ **直し方は「行種ごとの明示列挙」である**（⚠️ **「`t` が無ければ任意の `*_ts` を探す」
/// 汎用実装は採らない**）。理由は 2 つ:
/// 1. ⚠️ `session_meta` まで消える（下記）。
/// 2. ⚠️ **将来の行種が無言で削除対象に入る** —— ★ 明示列挙なら、足し忘れたときに
///    「**消えない**」側（＝ 安全側ではないが**気づける**側）に倒れ、テストが止める。
///
/// ## ⚠️★★★ `session_meta` は `meta` と同じく残す（ADR-031 D6 決定 3）
///
/// ⚠️★★★ **2026-09-14 に理由を実測で訂正した**（code-reviewer MEDIUM）。
/// ★ 初出は「`gse-replay` が 1 セッション 1 本を前提。**0 本の挙動は未検証**」と書いたが、
/// ⚠️ **実測すると 0 本は `Err` にならない** —— `bin/replay.rs` は
/// `track = TrackKind::Main` を既定にし、逐語 `"no session_meta found — assuming track=main"` と
/// **warn するだけ**である。
/// → ★★★ **実害は「落ちること」ではなく「O1 / exploratory が黙って `main` として読まれること」**である。
/// ⚠️ `Err` になるのは **2 本目以降で `task_kind` が割れたとき**（同ファイルの `bail!`）。
/// → ★ 結論（残す）は変わらないが、**根拠はこちらが正しい**。
/// ★ `session_meta` が持つのは `track` / `task_kind` / `condition` / `head_id` ——
/// **被験者の行動の中身ではなく、そのセッションの条件**である。
///
/// ## ⚠️★★★ 2026-08-26: **`meta` 行を削除対象から外した**（研究者判断 R-12）
///
/// > ⚠️ **旧実装は `session_start` / `session_end` も時刻として読み、`meta` 行を消していた。**
///
/// ★ security-checker が実測した壊れ方（LOW-2）:
/// **ローテート境界をまたぐ区間**を指定すると `meta`(session_end) が消え、
/// ⚠️★★★ `reconcile::closed_o1_session_end` が `None` を返して
/// **そのファイルが永久に提出されない**。★ 被験者にも研究者にも通知は出ない（静かな全損）。
///
/// ★ 外してよい理由: **`meta` 行は行動の中身を 1 バイトも持たない** ——
/// 持っているのは**セッションの境界時刻**と**版情報**（`hmm_version` / `app_version` /
/// `capabilities` / `keyboard_layout`）だけである。
/// → ★ 消しても被験者のプライバシーは 1 ミリも増えず、⚠️ **消すと
/// 「いつ・どの版で・何を記録できる計器で取ったか」が失われる** ——
/// ★ これは **ADR-013 D1**（「**信号が無い**」と「**計器が無い**」を分ける）が
/// 防ごうとしている状態そのものである。
///
/// ⚠️ **時刻を持たない行も `None`** を返す。→ [`retain_outside_range`] は **残す**。
pub fn line_timestamp(line: &str) -> Option<u64> {
    let v: serde_json::Value = serde_json::from_str(line).ok()?;
    let obj = v.as_object()?;
    // ⚠️★★★ **`meta` / `session_meta` 行は消さない**（上記 R-12 / ADR-031 D6 決定 3）。
    //   ★ 行種で弾くので、将来これらに時刻フィールドが増えても**自動的に守られる**。
    let line_type = obj.get("type").and_then(serde_json::Value::as_str);
    //   ★ `invitation_condition`（招待の契機の種類と値・推定器の版）も同じ側（セッションの条件の行）。
    //   消すとそのファイルの招待の条件が読めなくなる（ADR-040 D4・2026-11-01 研究者の決定）。
    //   ★ `probe_frame`（段 1 の問いの枠: seed・起点・調停器の定数）も同じ側。中身は系の設定だけで、
    //   行動も申告も含まない。削除した区間の候補の行（`probe_assignment`・`probe_suppressed`）は消える
    //   （`.steering/20261105-gse-m5-probe-wiring-plan/decisions.md` 判断 8）。
    //   ★ `handmark_day`（手跡のその日の累計の写し）は `t` で消える（判断 4: 区間の中の写しが残ると
    //   その時間帯にアプリが動いていたことと `shown_ms` の差が読める）。区間の外の行に残る `toggles` /
    //   `stage_starts` のうち区間に入る要素は [`scrub_handmark_day`] が消す。
    if line_type.is_some_and(|t| NEVER_REDACTED.contains(&t)) {
        return None;
    }
    // 行種の無い行（古い形）は `"t"` を読む（従来どおり）。
    obj.get(time_key(line_type.unwrap_or("")))
        .and_then(serde_json::Value::as_u64)
}

/// 区間の削除で消さない行種（セッションの境界・条件・系の設定の行。理由は [`line_timestamp`] の doc とコメント）。
/// ★ 全行種の鍵のテスト（`every_line_type_in_the_schema_has_a_redaction_key`）もこの表を読む。
pub const NEVER_REDACTED: &[&str] = &[
    "meta",
    "session_meta",
    "invitation_condition",
    "probe_frame",
];

/// 区間の削除で読む時刻の鍵。★ 既定は `"t"`。⚠️ 別名を書く行種だけを**明示列挙**する（ADR-031 D6）。
pub fn time_key(line_type: &str) -> &'static str {
    match line_type {
        "realtime_label" | "vignette_response" => "ts",
        "probe_assignment" => "scheduled_ts",
        _ => "t",
    }
}

/// 行が**占める時間の区間** `[start, end]`（★ 点しか持たない行は `start == end`）。
///
/// ## ⚠️★★★ なぜ「点」では足りないのか（2026-09-14・security-checker HIGH）
///
/// ★ 自己申告の行は **「答えた時刻」と「答えが指している時間帯」が違う**。
/// ⚠️ 点（＝ 答えた時刻）だけで削除判定すると、次が起きる:
///
/// > ★ 会話が **14:20–14:45**。復帰を引き金にプローブが **14:46** に出て、
/// > 被験者が「会話」と答える。⚠️ 第三者の求めで被験者が **14:20–14:45 を削除**しても、
/// > 回答の行（`t` ＝ 14:46）は**残る**。
/// > → ★★★ **削除した区間に第三者が同席していた事実が端末と提出物に残る。**
///
/// ⚠️ これは同意文書の逐語「★ **その時間帯のお答えは消えます**」を破る
/// （＝ ADR-031 **D5 保証 2** が実体として成立しない）。
///
/// ## ★ どの行が区間を持つか
///
/// | 行種 | 区間 |
/// |---|---|
/// | `activity_label` | `recall_window_start_ms` 〜 `recall_window_end_ms` ∪ `t` |
/// | `realtime_label` | `analysis_window_start_ms` 〜 `analysis_window_end_ms` ∪ `ts` |
/// | `day_question` | `shown_ts` 〜 `t`（表示から閉じるまで） |
/// | `probe_suppressed` | `candidate_ts` 〜 `t`（候補の時刻から判定まで） |
/// | それ以外 | 点（[`line_timestamp`]） |
/// | `meta` / `session_meta` / `invitation_condition` / `probe_frame` | **`None`（常に残す）** |
///
/// ⚠️★★★ **区間は「答えた時刻」も含める**（和集合）。★ 回答そのものの時刻を消す
/// 要求（「さっきの 5 分を消して」）でも落ちるようにするためである。
///
/// ⚠️ **`(0, 0)` の窓は「未設定」とみなして無視する** —— ★ skip 応答や旧ログで
/// 窓が 0 のことがあり、素直に和集合を取ると **epoch から回答時刻までの全区間**になって
/// **無関係な削除要求でも落ちてしまう**（★ 実測で踏んだ）。
pub fn line_interval(line: &str) -> Option<(u64, u64)> {
    let point = line_timestamp(line)?;
    let v: serde_json::Value = serde_json::from_str(line).ok()?;
    let obj = v.as_object()?;
    let num = |k: &str| obj.get(k).and_then(serde_json::Value::as_u64);
    let window = match obj.get("type").and_then(serde_json::Value::as_str) {
        Some("activity_label") => num("recall_window_start_ms").zip(num("recall_window_end_ms")),
        Some("realtime_label") => {
            num("analysis_window_start_ms").zip(num("analysis_window_end_ms"))
        }
        // ★ 段 1（2026-11-06・本タスクの判断 8）: 行が持つ 2 つ目の時刻も区間に入れる。
        //   点（`t`）だけで消すと、削除した区間の中の時刻が別の欄に残りうる（消す側に倒す）。
        // ⚠️ 2 つ目の時刻が 0（欠けた値）なら点に倒す（epoch からの全区間にしない・security-checker LOW）。
        Some("day_question") => num("shown_ts").filter(|&v| v > 0).zip(Some(point)),
        Some("probe_suppressed") => num("candidate_ts").filter(|&v| v > 0).zip(Some(point)),
        _ => None,
    };
    Some(match window {
        // ⚠️ 壊れた窓（start > end）と未設定の窓（0,0）は**点に倒す**（★ 黙って広げない）。
        Some((ws, we)) if ws <= we && we > 0 => (point.min(ws), point.max(we)),
        _ => (point, point),
    })
}

/// `[from_ms, to_ms]`（★ **両端を含む**）に入る行を落とし、残す行だけを返す。
///
/// ★ 純関数。⚠️ ファイル I/O を持たないので、境界条件をテストで固定できる。
///
/// - ⚠️ `from_ms > to_ms` の場合は**何も落とさない**（★ 空区間として扱い、黙って全消ししない）。
/// - ⚠️★★★ **`meta` 行は常に残す**（[`line_timestamp`] の doc・研究者判断 R-12）。
///   ★ 消すと `session_end` を失ったファイルが**永久に提出されなくなる**。
pub fn retain_outside_range<'a>(
    lines: impl IntoIterator<Item = &'a str>,
    from_ms: u64,
    to_ms: u64,
) -> (Vec<&'a str>, usize) {
    let mut kept = Vec::new();
    let mut removed = 0usize;
    for line in lines {
        if from_ms <= to_ms {
            // ★ **区間が交差したら落とす**（ADR-031 D6・2026-09-14）。
            //   ⚠️ 点の行は `start == end` なので、従来どおり「点が範囲内か」になる。
            if let Some((start, end)) = line_interval(line) {
                if start <= to_ms && end >= from_ms {
                    removed += 1;
                    continue;
                }
            }
        }
        kept.push(line);
    }
    (kept, removed)
}

/// `handmark_day` の行から、区間 `[from_ms, to_ms]`（両端を含む）に入る `toggles`・`input_toggles`・`stage_starts` の要素を消す。
///
/// `t` が区間に入る行は [`retain_outside_range`] が行ごと落とす。ここで扱うのは区間の外に残る行で、
/// 割付・SHA-256・種・出せなかった理由は残す。消すものが無い・`handmark_day` でない・
/// 区間が逆のときは `None`（行に触らない）。`shown_ms` は時刻ではなく量なので変えない。
pub fn scrub_handmark_day(line: &str, from_ms: u64, to_ms: u64) -> Option<String> {
    if from_ms > to_ms {
        return None;
    }
    let mut v: serde_json::Value = serde_json::from_str(line).ok()?;
    let obj = v.as_object_mut()?;
    if obj.get("type").and_then(serde_json::Value::as_str) != Some("handmark_day") {
        return None;
    }
    let inside = |t: u64| from_ms <= t && t <= to_ms;
    let mut changed = false;
    if let Some(arr) = obj
        .get_mut("toggles")
        .and_then(serde_json::Value::as_array_mut)
    {
        let before = arr.len();
        arr.retain(|e| {
            !e.get("t")
                .and_then(serde_json::Value::as_u64)
                .is_some_and(inside)
        });
        changed |= arr.len() != before;
    }
    if let Some(arr) = obj
        .get_mut("input_toggles")
        .and_then(serde_json::Value::as_array_mut)
    {
        let before = arr.len();
        arr.retain(|e| {
            !e.get("t")
                .and_then(serde_json::Value::as_u64)
                .is_some_and(inside)
        });
        changed |= arr.len() != before;
    }
    if let Some(arr) = obj
        .get_mut("stage_starts")
        .and_then(serde_json::Value::as_array_mut)
    {
        let before = arr.len();
        arr.retain(|e| !e.as_u64().is_some_and(inside));
        changed |= arr.len() != before;
    }
    if changed {
        serde_json::to_string(&v).ok()
    } else {
        None
    }
}

/// 手跡の日の累計の写し（`handmark_day` の行か走行中の累計）。削除で引く量を求める入力。
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub struct HandmarkSnap {
    pub day: i64,
    pub t: u64,
    pub shown_ms: u64,
    pub visible_ms: u64,
    /// いま書いているファイル（削除で書き換えないファイル）の行。
    pub skipped: bool,
}

/// ある日の累計から引く量。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct HandmarkSub {
    pub shown_ms: u64,
    pub visible_ms: u64,
    /// 当てる範囲の終わり（この時刻以降の行には当てない・走行中の累計にも当てない）。累計が日の途中で 0 から
    /// 始め直したとき、次の区切りの行を削らないため。`None` は終わりが無い（走行中の累計にも当てる）。
    pub until: Option<u64>,
}

impl HandmarkSub {
    /// 走行中の累計（状態ファイル）に当てるか。
    pub fn applies_to_live(&self) -> bool {
        self.until.is_none()
    }
}

/// 日（現地の日の番号）ごとの引く量。
pub type HandmarkSubs = std::collections::BTreeMap<i64, HandmarkSub>;

/// `handmark_day` の行から累計の写しを読む。`visible_ms` が数でない行（出せなかった理由の行・古い行）は
/// 累計を持たないので `None`。
pub fn handmark_snap(line: &str) -> Option<HandmarkSnap> {
    let v: serde_json::Value = serde_json::from_str(line).ok()?;
    let obj = v.as_object()?;
    if obj.get("type").and_then(serde_json::Value::as_str) != Some("handmark_day") {
        return None;
    }
    Some(HandmarkSnap {
        day: obj.get("day")?.as_i64()?,
        t: obj.get("t")?.as_u64()?,
        shown_ms: obj.get("shown_ms")?.as_u64()?,
        visible_ms: obj.get("visible_ms")?.as_u64()?,
        skipped: false,
    })
}

/// 削除の対象のディレクトリの全ファイルから累計の写しを集める。いま書いているファイル `skip` も読むだけ読み、
/// その行には `skipped` を立てる（[`handmark_subtractions`] がその日を引かない判断に使う）。
pub fn collect_handmark_snaps(dir: &Path, skip: Option<&Path>) -> Vec<HandmarkSnap> {
    let Ok(entries) = fs::read_dir(dir) else {
        return Vec::new();
    };
    let mut out = Vec::new();
    for entry in entries.flatten() {
        let path = entry.path();
        if !is_redactable_session_file(&path) {
            continue;
        }
        let skipped = skip.is_some_and(|s| same_file(s, &path));
        let Ok(content) = fs::read_to_string(&path) else {
            continue;
        };
        out.extend(
            content
                .lines()
                .filter(|l| l.contains("\"handmark_day\""))
                .filter_map(handmark_snap)
                .map(|s| HandmarkSnap { skipped, ..s }),
        );
    }
    out
}

/// 区間 `[from_ms, to_ms]` の手跡の量を、日ごとに求める（段 1 の同意の判断 13・本タスクの判断 1）。
///
/// 行はその日の累計（`shown_ms`・`visible_ms`）を持つので、区間の中の行を落としても、後の行の累計と
/// 前の行の差から区間の中の量が読める。日 d ごとに:
///
/// - next = d の写しで `t > to_ms` の最初のもの。無く、走行中の累計 `live` が d なら `live`。どちらも無ければ引かない。
/// - prev = d の写しで `t < from_ms` の最後のもの。無ければ 0（日の始まり）。累計が日の途中で 0 から始め直して
///   いれば（状態ファイルが消えた後の起動）、next と同じ区切りの中だけで探す（区切りの始まりは 0）。
/// - 引く量 = next − prev。区間の端の 5 分ほどまで（行の間隔）も含めて引く（消す側に倒す）。当てるのは next の
///   区切りの中だけ（[`HandmarkSub::until`]）。
/// - ⚠️ いま書いているファイル（`skipped`）に d の `t >= from_ms` の行（区間の中か後）があれば、d は引かない。その行は書き換えられず、
///   走行中の累計と他のファイルの行だけを引くと、その行との差で区間の量が読め、再開してから消し直すと二重に引く
///   （本タスクの判断 6）。消し残りは `files_skipped` で画面に出て、消し直しで 1 回だけ引かれる。
///
/// 区間が d より前に終わっていても、d の最初の行（日付の変わり目か起動の行）の累計は小さいので、
/// 引き過ぎは行の間隔ほどまで。`from_ms > to_ms` なら空。
pub fn handmark_subtractions(
    snaps: &[HandmarkSnap],
    live: Option<HandmarkSnap>,
    from_ms: u64,
    to_ms: u64,
) -> HandmarkSubs {
    let mut subs = HandmarkSubs::new();
    if from_ms > to_ms {
        return subs;
    }
    let mut days: Vec<i64> = snaps.iter().map(|s| s.day).collect();
    days.extend(live.map(|l| l.day));
    days.sort_unstable();
    days.dedup();
    for day in days {
        if snaps
            .iter()
            .any(|s| s.day == day && s.skipped && s.t >= from_ms)
        {
            continue;
        }
        // その日の写しを時刻の順に並べ、累計が減ったところで区切る（区切りの番号を付ける）
        let mut of_day: Vec<HandmarkSnap> =
            snaps.iter().filter(|s| s.day == day).copied().collect();
        of_day.sort_by_key(|s| s.t);
        let mut seg = Vec::with_capacity(of_day.len());
        let mut cur = 0usize;
        for (i, s) in of_day.iter().enumerate() {
            if i > 0 && s.shown_ms < of_day[i - 1].shown_ms {
                cur += 1;
            }
            seg.push(cur);
        }
        // 走行中の累計の区切り(最後の行より小さければ 0 から始め直した後)
        let live_seg = live.filter(|l| l.day == day).map(|l| match of_day.last() {
            Some(p) if l.shown_ms < p.shown_ms => cur + 1,
            _ => cur,
        });
        let next = match of_day.iter().position(|s| s.t > to_ms) {
            Some(i) => Some((of_day[i], seg[i])),
            None => live.filter(|l| l.day == day).zip(live_seg),
        };
        let Some((next, next_seg)) = next else {
            continue;
        };
        let (ps, pv) = of_day
            .iter()
            .zip(&seg)
            .rfind(|(s, g)| s.t < from_ms && **g == next_seg)
            .map_or((0, 0), |(p, _)| (p.shown_ms, p.visible_ms));
        // 当てる範囲: next の区切りの終わりまで(次の区切りの最初の行の時刻)。走行中の累計が別の区切りなら当てない
        let until = match of_day.iter().zip(&seg).find(|(_, g)| **g > next_seg) {
            Some((s, _)) => Some(s.t),
            None if live_seg.is_some_and(|g| g != next_seg) => Some(u64::MAX),
            None => None,
        };
        let sub = HandmarkSub {
            shown_ms: next.shown_ms.saturating_sub(ps),
            visible_ms: next.visible_ms.saturating_sub(pv),
            until,
        };
        if (sub.shown_ms, sub.visible_ms) != (0, 0) {
            subs.insert(day, sub);
        }
    }
    subs
}

/// 累計から引く（visible ≤ shown を保つ）。
pub fn subtract_handmark(shown_ms: u64, visible_ms: u64, sub: HandmarkSub) -> (u64, u64) {
    crate::analysis::handmark::day::subtract_totals(
        shown_ms,
        visible_ms,
        sub.shown_ms,
        sub.visible_ms,
    )
}

/// 区間より後（`t > to_ms`）の `handmark_day` の行の累計から、その日の引く量を引く。変えたら新しい行。
pub fn subtract_handmark_day(line: &str, to_ms: u64, subs: &HandmarkSubs) -> Option<String> {
    let snap = handmark_snap(line)?;
    if snap.t <= to_ms {
        return None;
    }
    let sub = subs.get(&snap.day)?;
    if sub.until.is_some_and(|u| snap.t >= u) {
        return None;
    }
    let (shown, visible) = subtract_handmark(snap.shown_ms, snap.visible_ms, *sub);
    if (shown, visible) == (snap.shown_ms, snap.visible_ms) {
        return None;
    }
    let mut v: serde_json::Value = serde_json::from_str(line).ok()?;
    let obj = v.as_object_mut()?;
    obj.insert("shown_ms".into(), shown.into());
    obj.insert("visible_ms".into(), visible.into());
    serde_json::to_string(&v).ok()
}

/// 1 ファイルから区間内の行を落とす。★ 落ちた行数を返す。
///
/// ⚠️ **書き換えは一時ファイル → `rename`** で行う。★ 途中で電源が落ちても原本が残る。
/// ★ 1 行も落ちないときは**ファイルに触らない**（mtime を動かさない）。
///
/// ## ⚠️★★★ パーミッションを引き継ぐ (2026-08-30 の実機で踏んだ)
///
/// ★ `logger::create_file_at` はセッション NDJSON を **0600** で作る。逐語:
/// 「他ユーザーが打鍵ログの**内容**を読めない (data-privacy ルール 2)」。
///
/// ⚠️ 旧実装は `fs::File::create(&tmp)` で一時ファイルを作っていた。★ これは既定
/// パーミッション (umask 適用で通常 **0644**) で作られ、`rename` で原本を置き換えるので、
/// → ⚠️★★★ **削除を実行したファイルだけが世界読み取り可になっていた。**
///
/// ★ 2026-08-30 に macOS 実機で実測（★ 同じディレクトリの他ファイルとの対照）:
///
/// ```text
/// -rw-------  gse_o1_20260830_061725.ndjson   ← 触っていない
/// -rw-r--r--  gse_o1_20260830_062005.ndjson   ← ⚠️ 削除を適用した
/// -rw-------  gse_o1_20260830_074040.ndjson   ← 触っていない
/// ```
///
/// ⚠️ **プライバシー機能そのものがプライバシーを緩めていた。**
/// ★ 同意文書 §7（削除の申し出）に応じる経路が、応じるたびに保護を落としていたことになる。
///
/// 戻り値は、落とした行と、区間の中の時刻を消した・累計から区間の量を引いた `handmark_day` の行の数の和。
/// `subs` は [`handmark_subtractions`] で、削除の前に全ファイルと走行中の累計から求めたもの。
pub fn redact_file(path: &Path, from_ms: u64, to_ms: u64, subs: &HandmarkSubs) -> Result<usize> {
    let content = fs::read_to_string(path)
        .map_err(|e| format!("failed to read session log {}: {e}", path.display()))?;
    let (kept, removed) = retain_outside_range(content.lines(), from_ms, to_ms);
    // ★ `handmark_day` の行は残し、削除区間に入る要素だけを消し、後の行の累計から区間の量を引く。
    let mut scrubbed = 0usize;
    let kept: Vec<std::borrow::Cow<str>> = kept
        .into_iter()
        .map(|l| {
            let line = match scrub_handmark_day(l, from_ms, to_ms) {
                Some(new) => std::borrow::Cow::Owned(new),
                None => std::borrow::Cow::Borrowed(l),
            };
            // 区間より後の行の累計から、区間の中の量を引く（判断 13）
            let line = match subtract_handmark_day(&line, to_ms, subs) {
                Some(new) => std::borrow::Cow::Owned(new),
                None => line,
            };
            if matches!(line, std::borrow::Cow::Owned(_)) {
                scrubbed += 1;
            }
            line
        })
        .collect();
    if removed == 0 && scrubbed == 0 {
        return Ok(0);
    }

    let tmp = path.with_extension("ndjson.redact-tmp");

    // ⚠️★★★ **残骸を必ず消してから開く** (2026-08-31・code-reviewer / security-checker が一致して指摘)。
    //   ★ `OpenOptions::mode()` は **新規作成時にしか効かない**（実測で確認: 0644 の既存ファイルを
    //     `O_CREAT|O_TRUNC` ＋ mode 0600 で開き直しても **0644 のまま**）。
    //   ⚠️ 旧実装が失敗して残した `*.redact-tmp` は **0644** なので、
    //     → ★ **修正後の初回削除で、その 0644 が原本の位置へ rename される**。
    //     ＝ ⚠️ **直したはずの欠陥が黙って再現し、しかも回帰テストは緑のまま**だった。
    let _ = fs::remove_file(&tmp);

    // ★ 書き込みに失敗したら **残骸を残さない**（次回の再現源にしない）。
    let write_result = (|| -> Result<()> {
        let mut f = fs::File::create(&tmp)
            .map_err(|e| format!("failed to create temp file {}: {e}", tmp.display()))?;

        // ⚠️★★★ 原本のパーミッションを引き継ぐ（上の doc コメント参照）。
        //   ★ `rename` 後に締めるのでは**窓が開く**（0644 のファイルが一瞬でも原本の位置に立つ）。
        //   → ★ **rename の前に**、開いたハンドル経由で締める。
        //   ⚠️ `set_permissions` は **umask に削られない**ので、`OpenOptions::mode()` より確実。
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            // ★ 原本が読めなければ 0600 に倒す（fail-safe。緩い側に倒さない）。
            // ⚠️ `& 0o700` で **group/other を必ず落とす** —— ★ 原本が何らかの理由で 0644 でも
            //   それを引き継がない。`logger::create_file_at` は常に 0600 で作るので実運用コストは 0。
            let mode = fs::metadata(path)
                .map(|m| m.permissions().mode())
                .unwrap_or(0o600)
                & 0o700;
            f.set_permissions(fs::Permissions::from_mode(mode))
                .map_err(|e| format!("failed to secure temp file {}: {e}", tmp.display()))?;
        }
        // Windows: NTFS の既定 ACL でユーザープロファイル配下は他ユーザーから読めない
        // (`logger::create_file_at` と同じ判断・同じ理由でここでも追加制限はしない)。

        for line in &kept {
            writeln!(f, "{line}").map_err(|e| format!("failed to write {}: {e}", tmp.display()))?;
        }
        f.flush()
            .map_err(|e| format!("failed to flush {}: {e}", tmp.display()))?;
        // ★ rename の前に **fsync** する。⚠️ doc は「途中で電源が落ちても原本が残る」と主張して
        //   いるが、flush だけでは**残す側 (kept 行) が失われうる**（code-reviewer LOW）。
        //   ★ 削除経路は頻度が低いのでコストは無視できる。
        f.sync_all()
            .map_err(|e| format!("failed to sync {}: {e}", tmp.display()))?;
        Ok(())
    })();
    if let Err(e) = write_result {
        let _ = fs::remove_file(&tmp);
        return Err(e);
    }

    fs::rename(&tmp, path).map_err(|e| {
        let _ = fs::remove_file(&tmp);
        format!("failed to replace session log {}: {e}", path.display())
    })?;
    // ★ 時刻だけを消した `handmark_day` の行も 1 件と数える（画面が「0 件」と言わないため・判断 3）。
    Ok(removed + scrubbed)
}

/// ⚠️★★★ **既に世界読み取り可になったファイルを締め直す**（自己修復・2026-08-31）。
///
/// ## なぜ要るのか
///
/// ★ [`redact_file`] の修正は**再発を止めるだけ**である。
/// ⚠️ 2026-08-30 以前に削除を実行した端末には、**0644 のセッションログが残ったまま**になる。
/// ★ 実機で確認した実例（`~/Documents/GSE-sessions/`）:
///
/// ```text
/// -rw-r--r--  gse_o1_20260830_062005.ndjson   ← ⚠️ 削除を適用した回の残骸
/// -rw-r--r--  redaction_ledger.jsonl          ← ⚠️ 台帳は最初から 0644 だった
/// ```
///
/// ⚠️★★ **被験者の端末は研究者が触れない。** → ★ アプリ自身が直すしかない。
///
/// ## ★ どこから呼ぶか
///
/// `logger::default_log_path()`（★ 保存先が確定する**唯一の場所**・起動ごとに 1 回）。
/// ⚠️ 同じ場所に `warn_if_cloud_synced` があり、**同種の「起動時の点検」**として揃う。
///
/// ## ⚠️ 何をしないか
///
/// - ⚠️ **緩めない。** 既に 0600 のものには触らない（mtime を動かさない）。
/// - ⚠️ 失敗しても**起動を止めない**（★ 権限が無い / 別ユーザー所有などで落とさない）。
/// - ★ 対象は `gse_*.ndjson` と台帳のみ（⚠️ ディレクトリの権限は変えない ——
///   `logger::create_file_at` の逐語「親ディレクトリの権限は変更しない」と同じ判断）。
///
/// 締め直した件数を返す（★ 0 なら何も直す物が無かった）。
#[cfg(unix)]
pub fn secure_existing_files(dir: &Path) -> usize {
    use std::os::unix::fs::PermissionsExt;
    let Ok(entries) = fs::read_dir(dir) else {
        return 0;
    };
    let mut fixed = 0usize;
    for entry in entries.flatten() {
        let path = entry.path();
        let is_target = is_redactable_session_file(&path)
            || path.file_name().and_then(|n| n.to_str()) == Some(LEDGER_FILE_NAME);
        if !is_target {
            continue;
        }
        let Ok(meta) = fs::metadata(&path) else {
            continue;
        };
        let mode = meta.permissions().mode();
        // ★ group/other にビットが立っているものだけを締める。
        if mode & 0o077 == 0 {
            continue;
        }
        if fs::set_permissions(&path, fs::Permissions::from_mode(mode & 0o700)).is_ok() {
            fixed += 1;
        }
    }
    fixed
}

/// Windows: NTFS の既定 ACL でユーザープロファイル配下は他ユーザーから読めない
/// （`logger::create_file_at` と同じ判断）。★ 何もしない。
#[cfg(not(unix))]
pub fn secure_existing_files(_dir: &Path) -> usize {
    0
}

/// セッションディレクトリ全体から区間内の行を落とす。
///
/// - `dir` …… セッション NDJSON が置かれたディレクトリ（`logger::session_log_dir()` の第 1 要素）
/// - `skip` …… ⚠️ **いま書いているファイル**（★ 呼び出し側が渡す。触らずに数えるだけ）
///
/// ★ 対象は `gse_*.ndjson` の通常ファイルのみ。⚠️ `.anon.ndjson` などの派生と、
/// 台帳 (`redaction_ledger.jsonl`) は**対象外**である。
///
/// ⚠️★★★ 本関数は**最小幅を保証しない**。★ 呼ぶ前に必ず [`widen_to_minimum_width`] を通すこと
/// （★ 本番の呼び出しは `lib.rs` の `delete_time_range` だけで、そこが通している・2026-09-25 code-reviewer LOW）。
pub fn redact_dir(
    dir: &Path,
    from_ms: u64,
    to_ms: u64,
    skip: Option<&Path>,
    subs: &HandmarkSubs,
) -> Result<RedactionSummary> {
    let mut summary = RedactionSummary::default();
    let entries = match fs::read_dir(dir) {
        Ok(e) => e,
        // ★ まだ 1 本も書いていない端末では、ディレクトリ自体が無い。
        //   ⚠️ それは失敗ではなく「消すものが無い」である。
        Err(_) => return Ok(summary),
    };
    for entry in entries.flatten() {
        let path = entry.path();
        if !is_redactable_session_file(&path) {
            continue;
        }
        if skip.is_some_and(|s| same_file(s, &path)) {
            summary.files_skipped += 1;
            continue;
        }
        let removed = redact_file(&path, from_ms, to_ms, subs)?;
        if removed > 0 {
            summary.files_touched += 1;
            summary.lines_removed += removed;
        }
    }
    Ok(summary)
}

/// 削除対象にしてよいファイルか。
///
/// ★ `reconcile.rs` の候補判定と**同じ形**にそろえる（`gse_` 接頭辞 + `.ndjson`・派生は除く）。
pub fn is_redactable_session_file(path: &Path) -> bool {
    if !path.is_file() {
        return false;
    }
    let Some(name) = path.file_name().and_then(|n| n.to_str()) else {
        return false;
    };
    name.starts_with("gse_") && name.ends_with(".ndjson") && !name.ends_with(".anon.ndjson")
}

/// 2 つのパスが同じファイルを指すか。
///
/// ⚠️ Windows では大文字小文字を区別しないので、単純な `==` では取りこぼす。
/// ★ 正規化に失敗したら**元のパスで比較**する（★ 比較できないことを理由に消しに行かない）。
fn same_file(a: &Path, b: &Path) -> bool {
    match (fs::canonicalize(a), fs::canonicalize(b)) {
        (Ok(x), Ok(y)) => x == y,
        _ => a == b,
    }
}

/// ⚠️★★★ **「消した」という事実だけ**を台帳へ 1 行 append する。
///
/// ★ 書くのは 5 つの数だけである:
/// `requested_at` / `from` / `to` / `files_touched` / `lines_removed`。
///
/// ⚠️★★★ **何を消したかは書かない。** 行種の内訳も、打鍵数も、アプリも書かない ——
/// ★ それを書いた瞬間、**削除した区間の内容が台帳に復活する**（削除の意味が消える）。
///
/// ★ なぜ「事実」だけは残すのか: ⚠️ 解析側が「**この区間は信号が無かった**」と
/// 「**被験者が消した**」を取り違えると、`left_observation` の内訳を割るという O1 の目的が壊れる
/// （ADR-013 D1 の「信号が無い」と「計器が無い」の分離と同じ理屈）。
pub fn append_ledger(
    dir: &Path,
    requested_at: u64,
    from_ms: u64,
    to_ms: u64,
    summary: &RedactionSummary,
) -> Result<PathBuf> {
    fs::create_dir_all(dir)
        .map_err(|e| format!("failed to create session dir {}: {e}", dir.display()))?;
    let path = dir.join(LEDGER_FILE_NAME);
    let mut f = fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&path)
        .map_err(|e| format!("failed to open redaction ledger {}: {e}", path.display()))?;
    // ⚠️★★★ 台帳も **0600** で保つ (2026-08-31・security-checker が実機で 0644 を確認)。
    //   ★ `logger::create_file_at` (`:1162`) と `applog` はどちらも `.mode(0o600)` を付けており、
    //     ⚠️ **ここだけ外れていた**（＝ 2026-08-30 に直した欠陥と**同一ファイル内の同一クラス**）。
    //   ★ 中身は数値 5 つだけだが、⚠️ **「被験者がいつ・どの区間の削除を要求したか」**という
    //     行動メタデータである（`redaction.rs` 冒頭 / `data-privacy` ルール 6）。
    //   ⚠️ `.mode()` ではなく `set_permissions` を使う —— ★ append なので
    //     **既存の台帳（既に 0644 のもの）にも効かせる**必要がある（作成時のみでは直らない）。
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let _ = f.set_permissions(fs::Permissions::from_mode(0o600));
    }
    writeln!(
        f,
        r#"{{"requested_at":{},"from":{},"to":{},"files_touched":{},"lines_removed":{}}}"#,
        requested_at, from_ms, to_ms, summary.files_touched, summary.lines_removed
    )
    .map_err(|e| format!("failed to append redaction ledger {}: {e}", path.display()))?;
    Ok(path)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tmp_dir(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("gse_redaction_{}_{}", tag, std::process::id()));
        let _ = fs::remove_dir_all(&d);
        fs::create_dir_all(&d).unwrap();
        d
    }

    #[test]
    fn line_timestamp_reads_t_on_data_rows() {
        assert_eq!(
            line_timestamp(r#"{"type":"key","t":1000,"category":"alphabetic","press":true}"#),
            Some(1000)
        );
        assert_eq!(
            line_timestamp(r#"{"type":"pointer_bin","t":2000,"moved":3,"buttons":0,"wheel":0}"#),
            Some(2000)
        );
    }

    /// ⚠️★★★ **`meta` 行は時刻を持っていても削除対象にしない**（研究者判断 R-12）。
    ///
    /// ★ 消すと `reconcile::closed_o1_session_end` が `session_end` を見つけられず、
    /// ⚠️ **そのファイルが永久に提出されない**（★ 被験者にも研究者にも通知が出ない）。
    /// ★ `meta` 行は行動の中身を 1 バイトも持たず、⚠️ 失うのは
    /// 「いつ・どの版で・何を記録できる計器で取ったか」だけである（ADR-013 D1）。
    #[test]
    fn meta_rows_are_never_redacted_even_though_they_carry_a_time() {
        assert_eq!(
            line_timestamp(r#"{"type":"meta","session_start":500,"hmm_version":"0.5.0"}"#),
            None
        );
        assert_eq!(
            line_timestamp(r#"{"type":"meta","session_end":9000}"#),
            None
        );
    }

    /// ⚠️★★★ **ローテート境界をまたぐ削除でも `session_end` が残る**（★ 通しの回帰）。
    ///
    /// ★ これが崩れると、提出候補の述語が「閉じていない」と読んで
    /// **そのファイルを永久に拾わなくなる**。
    #[test]
    fn a_range_spanning_the_whole_file_still_leaves_the_session_boundary() {
        let (kept, removed) = retain_outside_range(
            [
                r#"{"type":"meta","session_start":1000,"hmm_version":"0.5.0"}"#,
                r#"{"type":"key","t":1200,"category":"alphabetic","press":true}"#,
                r#"{"type":"key","t":5000,"category":"alphabetic","press":true}"#,
                r#"{"type":"meta","session_end":9000}"#,
            ],
            0,
            u64::MAX,
        );
        assert_eq!(removed, 2, "★ データ行は 2 本とも消える");
        assert_eq!(kept.len(), 2);
        assert!(kept[0].contains("session_start"), "{kept:?}");
        assert!(kept[1].contains("session_end"), "{kept:?}");
    }

    /// ⚠️★★★ **`line_timestamp` の行種列挙が `logger.rs` の書式と一致していること**
    /// (ADR-031 **D6 決定 4** / `verify-before-claiming` ルール 6)。
    ///
    /// ## ★ なぜ要るのか
    ///
    /// ★ ADR-031 §Alternatives **A8** は「汎用実装は採らず明示列挙にする。
    /// **足し忘れれば『消えない』側に倒れるが、それは検査で止める**」と書いた。
    /// ⚠️ **その「検査」が無かった** (2026-09-14・code-reviewer HIGH)。
    ///
    /// ## ★ 何を突き合わせるか
    ///
    /// `logger.rs` の書式文字列を行単位で走査し、**その行が書く時刻キー**を
    /// [`line_timestamp`] が実際に拾えることを 1 行通して確かめる。
    /// ⚠️ 拾えない行種は**区間指定削除で永久に消えない** (= 同意文書 §4-3 の約束が破れる)。
    #[test]
    fn every_logger_line_type_uses_the_time_key_that_redaction_looks_for() {
        const LOGGER: &str = include_str!("logger.rs");
        const NEEDLE: &str = "{{\"type\":\"";
        let mut checked: std::collections::BTreeSet<&str> = std::collections::BTreeSet::new();
        let mut problems: Vec<String> = Vec::new();

        for src_line in LOGGER.lines() {
            let Some(i) = src_line.find(NEEDLE) else {
                continue;
            };
            let rest = &src_line[i + NEEDLE.len()..];
            let Some(q) = rest.find('"') else { continue };
            let line_type = &rest[..q];

            // ★ `meta` / `session_meta` は**常に残す**側である (D6 決定 3)。
            if NEVER_REDACTED.contains(&line_type) {
                continue;
            }

            // ★ この行が実際に書いている時刻キーを拾う (★ 走査は 1 行に閉じる)。
            let key = if src_line.contains("\"scheduled_ts\":") {
                "scheduled_ts"
            } else if src_line.contains("\"t\":") {
                "t"
            } else if src_line.contains("\"ts\":") {
                "ts"
            } else {
                continue; // ★ 時刻を持たない行は対象外。
            };

            checked.insert(line_type);
            let probe = format!("{{\"type\":\"{line_type}\",\"{key}\":4242}}");
            if line_timestamp(&probe) != Some(4242) {
                problems.push(format!(
                    "{line_type}: logger は {key} を書くのに line_timestamp が拾わない"
                ));
            }
        }

        assert!(
            problems.is_empty(),
            "⚠️★★★ 区間指定削除で消えない行種がある (同意文書 §4-3 が破れる):
{}",
            problems.join(
                "
"
            )
        );
        // ⚠️★★★ **検査が空回りしていないこと** —— ★ 魔法数ではなく**宣言と一致**させる
        //   (2026-09-14・`/cross-review` MEDIUM「フォーマット文字列走査は脆い」への対処)。
        //   ★ `logger.rs` の書式が複数行化・serde 化して走査が空振りしたら、
        //   **ここで検出される**（★ 見逃しではなく赤になる）。
        //
        // ⚠️★★★ **循環していないことの確認**（2026-09-14・`/cross-review` 2 巡目 MEDIUM-2）:
        //   ★ Codex は「`KNOWN_LINE_TYPES` を基準にすると *logger に足したのに KNOWN を
        //   更新し忘れた* ケースを検出できない」と指摘した。
        //   → ★ **それは別のテストが既に見ている** ——
        //   `capabilities::tests::capabilities_covers_every_line_type` が
        //   **`logger.rs` のリテラルを走査して KNOWN に在ることを要求する**。
        //   ⚠️ したがって「logger にあって KNOWN に無い」は**そちらで赤になる**。
        //   ★ 本テストが見るのは「KNOWN にあって redaction が拾えない」側である。
        let expected: std::collections::BTreeSet<&str> = crate::capabilities::KNOWN_LINE_TYPES
            .iter()
            .copied()
            .filter(|t| {
                !matches!(
                    *t,
                    "meta" | "session_meta" | "invitation_condition" | "probe_frame"
                )
            })
            .collect();
        assert_eq!(
            checked, expected,
            "★ 走査できた行種が宣言と一致しない。
             ⚠️ `logger.rs` の書式文字列の形が変わって走査が空振りしている可能性がある 
             (★ そのときは *見逃し* ではなく本アサートで止まる)。"
        );
    }

    /// ⚠️★★★ **自己申告行も区間指定削除の対象である** (ADR-031 **D6** 決定 2 / 4)。
    ///
    /// ★ 2026-09-14 まで、これらは `"t"` を持たないので **1 行も消えていなかった**。
    /// ⚠️ 画面には「消しました（… 件）」と出るのに端末に残る、という状態だった。
    #[test]
    fn self_reported_rows_are_redactable_even_though_they_use_another_time_key() {
        // ★ `realtime_label` / `vignette_response` は `"ts"`。
        assert_eq!(
            line_timestamp(
                r#"{"type":"realtime_label","probe_id":"p-1","source":"random_probe","q1_friction":3,"q2_progress":4,"answered":true,"skip_reason":"none","latency_ms":1,"analysis_window_start_ms":0,"analysis_window_end_ms":0,"ts":3000}"#
            ),
            Some(3000)
        );
        assert_eq!(
            line_timestamp(
                r#"{"type":"vignette_response","vignette_id":"v1","expected_quadrant":"flow","q1_friction":3,"q2_progress":4,"elapsed_ms":1,"changes":0,"ts":4000}"#
            ),
            Some(4000)
        );
        // ⚠️ `probe_assignment` は `"t"` を**持たない**。時刻は `"scheduled_ts"` である。
        assert_eq!(
            line_timestamp(
                r#"{"type":"probe_assignment","probe_id":"p-1","scheduled_ts":2000,"session_elapsed_ms":1000,"stratum":"random"}"#
            ),
            Some(2000)
        );
        // ★ 新しい監査 criterion は `"t"` を使う (ADR-031 D6 決定 1)。
        assert_eq!(
            line_timestamp(
                r#"{"type":"activity_label","t":5000,"probe_id":"p-1","category":"conversation","answered":true,"latency_ms":120,"recall_window_start_ms":4700,"recall_window_end_ms":5000}"#
            ),
            Some(5000)
        );
    }

    /// ⚠️★★★ **「会話の *区間* を消せば、その申告も消える」** (ADR-031 **D5 保証 2**)。
    ///
    /// ## ★ これは同意文書の逐語に対応する回帰である
    ///
    /// 逐語（`consent-draft-o1.md` §4 追補）: 「★ **お答えも上の 3 番（時間帯を指定して消す）の
    /// 対象です。★ その時間帯のお答えは消えます。**」
    ///
    /// ⚠️★★★ **2026-09-14 まで、これは実装で保証されていなかった**（security-checker HIGH）。
    /// ★ `activity_label` の `t` は**回答した時刻**なので、会話が 14:20–14:45 で回答が 14:46 だと、
    /// **14:20–14:45 を削除しても行が残った**。
    #[test]
    fn deleting_the_conversation_window_also_removes_the_self_report_about_it() {
        // ★ 会話は 14:20–14:45、プローブは復帰後の 14:46 に発火して回答された、という配置。
        const CONV_START: u64 = 1_700_000_000_000; // 14:20 相当
        const CONV_END: u64 = CONV_START + 25 * 60_000; // 14:45
        const ANSWERED_AT: u64 = CONV_END + 60_000; // 14:46

        let label = format!(
            r#"{{"type":"activity_label","t":{ANSWERED_AT},"probe_id":"p-1","category":"conversation","answered":true,"latency_ms":900,"recall_window_start_ms":{CONV_START},"recall_window_end_ms":{CONV_END}}}"#
        );
        let unrelated =
            format!(r#"{{"type":"key","t":{ANSWERED_AT},"category":"alphabetic","press":true}}"#);

        // ★ 被験者は **会話の時間帯だけ**を指定する（⚠️ 回答時刻は範囲の外である）。
        let (kept, removed) =
            retain_outside_range([label.as_str(), unrelated.as_str()], CONV_START, CONV_END);
        assert_eq!(removed, 1, "★ 会話の申告が落ちていない: {kept:?}");
        assert!(
            !kept.iter().any(|l| l.contains("conversation")),
            "⚠️★★★ 第三者の在席を示す申告が端末に残った: {kept:?}"
        );
        // ⚠️★★★ **対照**: 同じ範囲でも、範囲外の打鍵行は残る（★ 過剰削除をしていない）。
        assert_eq!(kept.len(), 1, "{kept:?}");
        assert!(kept[0].contains(r#""type":"key""#), "{kept:?}");

        // ★ 逆向き: **回答時刻だけ**を指定しても落ちる（★ 和集合であること）。
        let (kept2, removed2) =
            retain_outside_range([label.as_str()], ANSWERED_AT - 1_000, ANSWERED_AT + 1_000);
        assert_eq!(removed2, 1, "回答時刻を指定しても落ちること: {kept2:?}");

        // ⚠️★★★ **無関係な時間帯では落ちない**（★ 検査が「常に落ちる」空回りでないこと）。
        let (kept3, removed3) =
            retain_outside_range([label.as_str()], CONV_START - 600_000, CONV_START - 60_000);
        assert_eq!(removed3, 0, "無関係な範囲で落ちてはならない: {kept3:?}");
    }

    /// ★ `realtime_label` も**分析窓**で落ちる（★ 同じ穴が主データ側にもあった）。
    #[test]
    fn realtime_label_is_removed_when_its_analysis_window_is_deleted() {
        let line = r#"{"type":"realtime_label","probe_id":"p-1","source":"random_probe","q1_friction":3,"q2_progress":4,"answered":true,"skip_reason":"none","latency_ms":500,"analysis_window_start_ms":1700000000000,"analysis_window_end_ms":1700000030000,"ts":1700000090000}"#;
        // ★ 分析窓だけを指定する（⚠️ `ts` は範囲外）。
        let (kept, removed) = retain_outside_range([line], 1_700_000_000_000, 1_700_000_030_000);
        assert_eq!(removed, 1, "分析窓で落ちない: {kept:?}");
        // ⚠️ 無関係な範囲では落ちないこと（★ 空回り防止）。
        let (kept2, removed2) = retain_outside_range([line], 1, 2);
        assert_eq!(removed2, 0, "{kept2:?}");
    }

    /// ⚠️★★★ **`session_meta` は消さない** (ADR-031 D6 決定 3)。
    ///
    /// ★ `gse-replay` は 1 セッション 1 本の `session_meta` を前提にしており、
    /// ⚠️ **0 本になったときの挙動は未検証**である。→ ★ 触らない側に倒す。
    /// ⚠️ `meta` と対で固定する —— ★ 片方だけ直すと、もう片方が無言で消える。
    #[test]
    fn session_meta_is_never_redacted_like_meta() {
        assert_eq!(
            line_timestamp(
                r#"{"type":"session_meta","track":"o1","task_kind":"writing","intervention_enabled":false,"condition":null,"label_pool":null,"head_id":"writing","ts":1000}"#
            ),
            None
        );
        assert_eq!(
            line_timestamp(r#"{"type":"meta","session_start":500,"hmm_version":"0.5.0"}"#),
            None
        );
    }

    /// `invitation_condition` も `session_meta` と同じく区間削除で消さない（ADR-040 D4）。
    /// 時刻キーが `t` でも行種で弾く（`session_meta_is_never_redacted_like_meta` と対）。
    #[test]
    fn invitation_condition_is_never_redacted() {
        let line = r#"{"type":"invitation_condition","t":1000,"condition":"estimator","p_stuck":0.6,"hold_ms":30000,"hmm_version":"0.5.0"}"#;
        assert_eq!(line_timestamp(line), None);
        // 対照: 同じ時刻の招待の提示は時刻を持つ（消える側）
        assert_eq!(
            line_timestamp(r#"{"type":"invitation_present","t":1000}"#),
            Some(1000)
        );
        let (kept, removed) = retain_outside_range([line], 500, 5000);
        assert_eq!(removed, 0);
        assert_eq!(kept.len(), 1);
    }

    /// `probe_frame` は区間の削除で消さない（系の設定だけ・計画の判断 8）。対照の候補の行は消える。
    #[test]
    fn probe_frame_survives_redaction() {
        let frame = r#"{"type":"probe_frame","t":1000,"frame_seed":42,"anchor_ms":900,"arbiter_version":"s1-arbiter-1"}"#;
        assert_eq!(line_timestamp(frame), None);
        let assignment = r#"{"type":"probe_assignment","probe_id":"p-1","scheduled_ts":2000,"session_elapsed_ms":1000,"stratum":"random"}"#;
        let (kept, removed) = retain_outside_range([frame, assignment], 500, 5000);
        assert_eq!(removed, 1);
        assert_eq!(kept, vec![frame]);
    }

    fn handmark_row() -> &'static str {
        r#"{"type":"handmark_day","t":9000,"day":20411,"assigned":"on","late_start_day":20410,"first_shown_day":20410,"shown_ms":600000,"visible_ms":null,"toggles":[{"t":1000,"on":false},{"t":3000,"on":true},{"t":8000,"on":false}],"stage_starts":[500,2500,7000],"overflow":false,"table_sha256":null,"draw_seed":"0123456789abcdef","reason":"off_today"}"#
    }

    /// `t` が区間に入る `handmark_day` の行は行ごと消える。区間の外なら残り、要素だけが消える。
    #[test]
    fn handmark_day_row_is_dropped_when_t_is_inside_and_scrubbed_otherwise() {
        let row = handmark_row(); // t = 9000
        assert_eq!(line_timestamp(row), Some(9_000));
        let (kept, removed) = retain_outside_range([row], 9_000, 9_000);
        assert_eq!((kept.len(), removed), (0, 1));
        let (kept, removed) = retain_outside_range([row], 0, u64::MAX);
        assert_eq!((kept.len(), removed), (0, 1));
        let (kept, removed) = retain_outside_range([row], 2_000, 5_000);
        assert_eq!((kept.len(), removed), (1, 0));
        let out = scrub_handmark_day(row, 2_000, 5_000).expect("changed");
        let v: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(
            v["toggles"],
            serde_json::json!([{"t":1000,"on":false},{"t":8000,"on":false}])
        );
        assert_eq!(v["stage_starts"], serde_json::json!([500, 7000]));
        // 日の属性・量は変わらない
        for k in [
            "day",
            "assigned",
            "shown_ms",
            "draw_seed",
            "reason",
            "t",
            "late_start_day",
        ] {
            let orig: serde_json::Value = serde_json::from_str(row).unwrap();
            assert_eq!(v[k], orig[k], "{k}");
        }
        // 両端を含む
        let out = scrub_handmark_day(row, 1_000, 1_000).expect("changed");
        let v: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(v["toggles"].as_array().unwrap().len(), 2);
        // 全部を覆えば空の配列で行は残る
        let out = scrub_handmark_day(row, 0, 10_000).expect("changed");
        let v: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(v["toggles"], serde_json::json!([]));
        assert_eq!(v["stage_starts"], serde_json::json!([]));
        // 区間の外・逆の区間・別の行種は触らない
        assert_eq!(scrub_handmark_day(row, 20_000, 30_000), None);
        assert_eq!(scrub_handmark_day(row, 5_000, 2_000), None);
        let key = r#"{"type":"key","t":3000,"category":"alphabetic","press":true}"#;
        assert_eq!(scrub_handmark_day(key, 0, 10_000), None);
    }

    /// `input_toggles`（入力ごとの入れ切り）も区間に入る要素だけが消え、それしか消えないときも 1 件と数える。
    #[test]
    fn handmark_day_input_toggles_are_scrubbed_like_toggles() {
        let row = r#"{"type":"handmark_day","t":9000,"day":20411,"assigned":"on","late_start_day":20410,"first_shown_day":20410,"shown_ms":600000,"visible_ms":null,"toggles":[],"input_toggles":[{"t":1000,"input":"cursor","on":false},{"t":3000,"input":"click","on":false},{"t":8000,"input":"cursor","on":true}],"stage_starts":[],"overflow":false,"table_sha256":null,"draw_seed":"0123456789abcdef","reason":null}"#;
        let out = scrub_handmark_day(row, 2_000, 5_000).expect("changed");
        let v: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(
            v["input_toggles"],
            serde_json::json!([{"t":1000,"input":"cursor","on":false},{"t":8000,"input":"cursor","on":true}])
        );
        // 両端を含む・全部覆えば空で行は残る・外は触らない
        let out = scrub_handmark_day(row, 3_000, 3_000).expect("changed");
        let v: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(v["input_toggles"].as_array().unwrap().len(), 2);
        let out = scrub_handmark_day(row, 0, 10_000).expect("changed");
        let v: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(v["input_toggles"], serde_json::json!([]));
        assert_eq!(scrub_handmark_day(row, 20_000, 30_000), None);
        // 古い行（`input_toggles` が無い）はそのまま扱える
        assert_eq!(scrub_handmark_day(handmark_row(), 20_000, 30_000), None);
        // 数え方: `input_toggles` だけが消える行も 1 件
        let (kept, removed) = retain_outside_range([row], 2_000, 5_000);
        assert_eq!((kept.len(), removed), (1, 0), "retain は行を落とさない側");
        let d = tmp_dir("handmark-input-scrub");
        let path = d.join("gse_20261109_000000.ndjson");
        std::fs::write(&path, format!("{row}\n")).unwrap();
        assert_eq!(
            redact_file(&path, 2_000, 5_000, &HandmarkSubs::new()).unwrap(),
            1
        );
        let text = std::fs::read_to_string(&path).unwrap();
        assert!(!text.contains(r#""t":3000"#) && text.contains(r#""t":1000"#));
        assert_eq!(
            redact_file(&path, 200_000, 300_000, &HandmarkSubs::new()).unwrap(),
            0
        );
        let _ = std::fs::remove_dir_all(&d);
    }

    /// ファイルを通しても、行は残って要素だけが消える（消すものが他に無くてもファイルを書き換える）。
    #[test]
    fn redact_file_scrubs_handmark_day_without_dropping_the_row() {
        let d = tmp_dir("handmark-scrub");
        let path = d.join("gse_20261108_000000.ndjson");
        let key = r#"{"type":"key","t":99000,"category":"alphabetic","press":true}"#;
        std::fs::write(&path, format!("{}\n{key}\n", handmark_row())).unwrap();
        let removed = redact_file(&path, 2_000, 5_000, &HandmarkSubs::new()).unwrap();
        assert_eq!(
            removed, 1,
            "落ちた行は無いが、書き換えた行を 1 件と数える（画面に 0 件と出さない）"
        );
        let text = std::fs::read_to_string(&path).unwrap();
        let lines: Vec<&str> = text.lines().collect();
        assert_eq!(lines.len(), 2);
        assert!(
            lines[0].contains(r#""stage_starts":[500,7000]"#),
            "{}",
            lines[0]
        );
        assert_eq!(lines[1], key);
        // 当たらない区間なら触らない
        let before = std::fs::read(&path).unwrap();
        assert_eq!(
            redact_file(&path, 200_000, 300_000, &HandmarkSubs::new()).unwrap(),
            0
        );
        assert_eq!(std::fs::read(&path).unwrap(), before);
        // t（9000）が区間に入れば行ごと消える
        assert_eq!(
            redact_file(&path, 8_000, 10_000, &HandmarkSubs::new()).unwrap(),
            1
        );
        let text = std::fs::read_to_string(&path).unwrap();
        assert_eq!(text.lines().collect::<Vec<_>>(), vec![key]);
        let _ = std::fs::remove_dir_all(&d);
    }

    /// 段 1 の申告と候補の行は `"t"` で消える。2 つ目の時刻（表示・候補）が区間に入っても消える。
    #[test]
    fn new_s1_rows_are_deleted_by_t() {
        let dq = r#"{"type":"day_question","t":3000,"shown_ts":2000,"in_eod_window":true,"target_day":20000,"trigger":"evening_idle","delayed":false,"answered":true,"closed_by":"answer","items_version":"dq-draft-1","motivation":4,"latency_ms":10,"duration_ms":10}"#;
        let sup = r#"{"type":"probe_suppressed","t":3000,"candidate_ts":2999,"stratum":"random","reason":"away"}"#;
        assert_eq!(line_timestamp(dq), Some(3000));
        assert_eq!(line_timestamp(sup), Some(3000));
        // 閉じた時刻を含む削除
        let (_, removed) = retain_outside_range([dq, sup], 2500, 3500);
        assert_eq!(removed, 2);
        // 表示した時刻だけを含む削除でも、日の問いは消える
        let (kept, removed) = retain_outside_range([dq, sup], 1500, 2500);
        assert_eq!(removed, 1);
        assert_eq!(kept, vec![sup]);
        assert_eq!(line_interval(dq), Some((2000, 3000)));
        assert_eq!(line_interval(sup), Some((2999, 3000)));
        // 2 つ目の時刻が 0 なら点に倒す（epoch から消さない）
        let zero = r#"{"type":"probe_suppressed","t":3000,"candidate_ts":0,"stratum":"random","reason":"away"}"#;
        assert_eq!(line_interval(zero), Some((3000, 3000)));
    }

    /// ★ 通しの回帰: **自己申告行が実際に落ちて、`session_meta` と `meta` は残る**。
    #[test]
    fn a_range_drops_self_reports_and_keeps_both_meta_kinds() {
        let (kept, removed) = retain_outside_range(
            [
                r#"{"type":"meta","session_start":1000,"hmm_version":"0.5.0"}"#,
                r#"{"type":"session_meta","track":"o1","task_kind":"writing","intervention_enabled":false,"condition":null,"label_pool":null,"head_id":"writing","ts":1100}"#,
                r#"{"type":"probe_assignment","probe_id":"p-1","scheduled_ts":2000,"session_elapsed_ms":1000,"stratum":"random"}"#,
                r#"{"type":"realtime_label","probe_id":"p-1","source":"random_probe","q1_friction":3,"q2_progress":4,"answered":true,"skip_reason":"none","latency_ms":1,"analysis_window_start_ms":0,"analysis_window_end_ms":0,"ts":3000}"#,
                r#"{"type":"activity_label","t":3100,"probe_id":"p-1","category":"conversation","answered":true,"latency_ms":120,"recall_window_start_ms":2800,"recall_window_end_ms":3100}"#,
                r#"{"type":"key","t":8000,"category":"alphabetic","press":true}"#,
                r#"{"type":"meta","session_end":9000}"#,
            ],
            1500,
            5000,
        );
        assert_eq!(removed, 3, "★ 自己申告 3 行が落ちる: {kept:?}");
        assert_eq!(kept.len(), 4);
        assert!(kept[0].contains("session_start"), "{kept:?}");
        assert!(kept[1].contains("session_meta"), "{kept:?}");
        assert!(kept[2].contains(r#""t":8000"#), "{kept:?}");
        assert!(kept[3].contains("session_end"), "{kept:?}");
        // ⚠️★★★ **会話の申告が端末に残っていないこと** (ADR-031 D5 保証 2)。
        assert!(
            !kept.iter().any(|l| l.contains("conversation")),
            "第三者の在席を示す申告が残っている: {kept:?}"
        );
    }

    /// ⚠️ 時刻の無い行・壊れた行は `None` → **残す**。
    #[test]
    fn line_timestamp_is_none_without_a_time() {
        assert_eq!(
            line_timestamp(r#"{"type":"meta","hmm_version":"0.5.0"}"#),
            None
        );
        assert_eq!(line_timestamp("not json"), None);
        assert_eq!(line_timestamp(""), None);
    }

    /// ★ 両端を含む。
    #[test]
    fn retain_outside_range_is_inclusive_on_both_ends() {
        let lines = vec![
            r#"{"t":99}"#,
            r#"{"t":100}"#,
            r#"{"t":150}"#,
            r#"{"t":200}"#,
            r#"{"t":201}"#,
        ];
        let (kept, removed) = retain_outside_range(lines, 100, 200);
        assert_eq!(removed, 3);
        assert_eq!(kept, vec![r#"{"t":99}"#, r#"{"t":201}"#]);
    }

    /// ⚠️★★★ 逆転区間で**全消ししない**。
    #[test]
    fn retain_outside_range_drops_nothing_when_range_is_inverted() {
        let lines = vec![r#"{"t":1}"#, r#"{"t":2}"#];
        let (kept, removed) = retain_outside_range(lines.clone(), 200, 100);
        assert_eq!(removed, 0);
        assert_eq!(kept, lines);
    }

    /// ⚠️ 時刻を持たない行は残す (`meta` の版情報を落とさない)。
    #[test]
    fn retain_outside_range_keeps_timeless_lines() {
        let lines = vec![r#"{"type":"meta","hmm_version":"0.5.0"}"#, r#"{"t":150}"#];
        let (kept, removed) = retain_outside_range(lines, 100, 200);
        assert_eq!(removed, 1);
        assert_eq!(kept, vec![r#"{"type":"meta","hmm_version":"0.5.0"}"#]);
    }

    #[test]
    fn redact_file_rewrites_atomically_and_leaves_no_temp() {
        let d = tmp_dir("file");
        let p = d.join("gse_20260823_120000.ndjson");
        fs::write(&p, "{\"t\":1}\n{\"t\":50}\n{\"t\":100}\n").unwrap();
        let removed = redact_file(&p, 40, 60, &HandmarkSubs::new()).unwrap();
        assert_eq!(removed, 1);
        assert_eq!(fs::read_to_string(&p).unwrap(), "{\"t\":1}\n{\"t\":100}\n");
        assert!(!d.join("gse_20260823_120000.ndjson.redact-tmp").exists());
    }

    /// ⚠️★★★ **削除しても 0600 が落ちない**（2026-08-30 の実機で踏んだ欠陥の掛け金）。
    ///
    /// ★ 旧実装は `fs::File::create` で一時ファイルを作っていたので、`rename` 後の原本が
    /// umask 既定（通常 0644）になり、⚠️ **削除を実行したファイルだけ世界読み取り可**になった。
    #[cfg(unix)]
    #[test]
    fn redact_file_preserves_owner_only_permissions() {
        use std::os::unix::fs::PermissionsExt;
        let d = tmp_dir("perm");
        let p = d.join("gse_20260830_120000.ndjson");
        fs::write(&p, "{\"t\":1}\n{\"t\":50}\n{\"t\":100}\n").unwrap();
        fs::set_permissions(&p, fs::Permissions::from_mode(0o600)).unwrap();

        // ★ 前提の確認: 書き換え**前**は 0600 である（⚠️ ここが崩れたらテストが無意味）。
        assert_eq!(
            fs::metadata(&p).unwrap().permissions().mode() & 0o777,
            0o600,
            "前提が崩れている: 書き換え前から 0600 ではない"
        );

        assert_eq!(redact_file(&p, 40, 60, &HandmarkSubs::new()).unwrap(), 1);

        let mode = fs::metadata(&p).unwrap().permissions().mode() & 0o777;
        assert_eq!(
            mode, 0o600,
            "⚠️ 削除後に 0600 が失われた (mode={mode:o})。\
             ★ redact_file の一時ファイルが既定パーミッションで作られていないか確認すること"
        );
        // ⚠️ 他ユーザーから読めないことを**明示的に**も見る（★ 0640 等を見逃さないため）。
        assert_eq!(mode & 0o077, 0, "⚠️ group/other にビットが立っている");
    }

    /// ⚠️★★ **陽性対照**: 上のテストが「実在の欠陥」を本当に捕まえることを確かめる。
    ///
    /// ★ 旧実装と同じ作り方（`File::create` → `rename`）を再現し、
    /// ⚠️ **0600 が失われること**を assert する。→ ★ 失われないなら、上のテストは
    /// 「何も検査していない」ことになる（memory `measurement-instrument-false-positives`）。
    #[cfg(unix)]
    #[test]
    fn naive_rewrite_would_drop_permissions_positive_control() {
        use std::os::unix::fs::PermissionsExt;
        let d = tmp_dir("perm-control");
        let p = d.join("gse_20260830_130000.ndjson");
        fs::write(&p, "{\"t\":1}\n").unwrap();
        fs::set_permissions(&p, fs::Permissions::from_mode(0o600)).unwrap();

        // ★ 旧実装の作り方をそのまま再現する。
        let tmp = p.with_extension("ndjson.naive-tmp");
        {
            let mut f = fs::File::create(&tmp).unwrap();
            writeln!(f, "{{\"t\":1}}").unwrap();
        }
        fs::rename(&tmp, &p).unwrap();
        let naive = fs::metadata(&p).unwrap().permissions().mode() & 0o777;

        // ★ 同じ入口を `redact_file` に通す。
        let q = d.join("gse_20260830_140000.ndjson");
        fs::write(&q, "{\"t\":1}\n{\"t\":50}\n").unwrap();
        fs::set_permissions(&q, fs::Permissions::from_mode(0o600)).unwrap();
        redact_file(&q, 40, 60, &HandmarkSubs::new()).unwrap();
        let fixed = fs::metadata(&q).unwrap().permissions().mode() & 0o777;

        // ⚠️★★ **環境依存で赤にしない** (2026-08-31・code-reviewer MEDIUM)。
        //   ★ 旧版は `assert_ne!(naive, 0o600)` だったので、⚠️ umask 077 のマシンでは
        //     `File::create` が 0600 を作り、**欠陥が無いのにテストが落ちた**。
        //   → ★ 環境によらず成り立つ不変条件を**無条件に**見る。
        assert_eq!(fixed, 0o600, "★ redact_file 側は必ず 0600 を保つこと");
        // ★ umask が緩い環境（＝欠陥が観測できる環境）でだけ、**差が出ること**を要求する。
        //   ⚠️ 厳しい環境では対照が成立しないが、上の無条件 assert が本体を守っている。
        //   ★ 環境非依存の対照は `stale_temp_file_does_not_defeat_permission_inheritance`
        //     が担う（そちらは 0644 を**明示的に作る**ので umask に依存しない）。
        if naive != 0o600 {
            assert_ne!(
                fixed, naive,
                "⚠️ redact_file が素朴な書き換えと同じ結果になっている（mode={fixed:o}）"
            );
        }
    }

    /// ⚠️★★★ **残骸の一時ファイルが 0600 引き継ぎを無効化しない** (2026-08-31)。
    ///
    /// ★ `OpenOptions::mode()` は**新規作成時にしか効かない**（★ 実測で確認）。
    /// ⚠️ 旧実装が失敗して残した `*.redact-tmp`（0644）があると、
    /// **直したはずの欠陥がそのまま再現し、しかも他のテストは緑のまま**だった。
    /// ★ code-reviewer (HIGH) と security-checker (MEDIUM) が**独立に**指摘した経路。
    ///
    /// ★ 本テストは 0644 を**明示的に作る**ので **umask に依存しない対照**である。
    #[cfg(unix)]
    #[test]
    fn stale_temp_file_does_not_defeat_permission_inheritance() {
        use std::os::unix::fs::PermissionsExt;
        let d = tmp_dir("perm-stale");
        let p = d.join("gse_20260831_120000.ndjson");
        fs::write(&p, "{\"t\":1}\n{\"t\":50}\n{\"t\":100}\n").unwrap();
        fs::set_permissions(&p, fs::Permissions::from_mode(0o600)).unwrap();

        // ⚠️ **旧実装が残した 0644 の残骸**を置く（★ これが再現の種である）。
        let tmp = p.with_extension("ndjson.redact-tmp");
        fs::write(&tmp, "stale\n").unwrap();
        fs::set_permissions(&tmp, fs::Permissions::from_mode(0o644)).unwrap();

        assert_eq!(redact_file(&p, 40, 60, &HandmarkSubs::new()).unwrap(), 1);

        let mode = fs::metadata(&p).unwrap().permissions().mode() & 0o777;
        assert_eq!(
            mode, 0o600,
            "⚠️ 残骸の 0644 が原本の位置へ rename された（mode={mode:o}）"
        );
        assert!(!tmp.exists(), "★ 残骸が消えていない");
        // ★ 残骸の中身が混ざっていないことも見る。
        let body = fs::read_to_string(&p).unwrap();
        assert!(!body.contains("stale"), "⚠️ 残骸の中身が混入した");
    }

    /// ⚠️★★★ 自己修復が **既に劣化したファイルを締め直す**（2026-08-31）。
    ///
    /// ★ 修正は再発を止めるだけで、⚠️ **配布済みの被験者端末に残った 0644 は直らない**。
    #[cfg(unix)]
    #[test]
    fn secure_existing_files_tightens_world_readable_logs_and_ledger() {
        use std::os::unix::fs::PermissionsExt;
        let d = tmp_dir("self-heal");
        let mode_of = |p: &Path| fs::metadata(p).unwrap().permissions().mode() & 0o777;

        let bad_log = d.join("gse_20260830_120000.ndjson");
        let bad_ledger = d.join(LEDGER_FILE_NAME);
        let good_log = d.join("gse_20260830_130000.ndjson");
        // ⚠️ 対象外のものが巻き込まれないことも見る（★ 範囲を広げすぎない）。
        let unrelated = d.join("notes.txt");
        let derived = d.join("gse_20260830_140000.anon.ndjson");

        for p in [&bad_log, &bad_ledger, &unrelated, &derived] {
            fs::write(p, "{}\n").unwrap();
            fs::set_permissions(p, fs::Permissions::from_mode(0o644)).unwrap();
        }
        fs::write(&good_log, "{}\n").unwrap();
        fs::set_permissions(&good_log, fs::Permissions::from_mode(0o600)).unwrap();

        assert_eq!(
            secure_existing_files(&d),
            2,
            "★ 直すのはログと台帳の 2 件だけ"
        );

        assert_eq!(
            mode_of(&bad_log),
            0o600,
            "⚠️ セッションログが締まっていない"
        );
        assert_eq!(mode_of(&bad_ledger), 0o600, "⚠️ 台帳が締まっていない");
        assert_eq!(
            mode_of(&good_log),
            0o600,
            "★ もともと 0600 のものは変わらない"
        );
        // ⚠️★★ **範囲を広げすぎない**（memory: ゲートは広げすぎると誤爆する）。
        assert_eq!(mode_of(&unrelated), 0o644, "⚠️ 無関係なファイルに触れた");
        assert_eq!(mode_of(&derived), 0o644, "⚠️ 派生ファイル (.anon) に触れた");

        // ★ 2 回目は何も直さない（★ mtime を動かさない・冪等）。
        assert_eq!(secure_existing_files(&d), 0);
    }

    /// ⚠️★★ **陰性対照**: 自己修復が**緩める方向に動かない**。
    ///
    /// ★ これが無いと「全部 0600 にする」実装でも上のテストは緑になるが、
    /// ⚠️ 実運用では「0400 のものを 0600 に**緩める**」事故がありうる。
    #[cfg(unix)]
    #[test]
    fn secure_existing_files_never_loosens() {
        use std::os::unix::fs::PermissionsExt;
        let d = tmp_dir("self-heal-tight");
        let p = d.join("gse_20260830_150000.ndjson");
        fs::write(&p, "{}\n").unwrap();
        // ★ owner の read だけ（★ 0600 より厳しい）。
        fs::set_permissions(&p, fs::Permissions::from_mode(0o400)).unwrap();

        assert_eq!(secure_existing_files(&d), 0, "★ 締まっているものは数えない");
        assert_eq!(
            fs::metadata(&p).unwrap().permissions().mode() & 0o777,
            0o400,
            "⚠️ 0400 を 0600 へ緩めた"
        );
    }

    /// ★ 台帳も 0600 で保つ（⚠️ 既に 0644 で存在していても締め直す）。
    ///
    /// ⚠️ security-checker が**実機で 0644 を確認**した（`~/Documents/GSE-sessions/`）。
    /// ★ 2026-08-30 に直した欠陥と**同一ファイル内の同一クラス**が残っていた。
    #[cfg(unix)]
    #[test]
    fn ledger_is_owner_only_even_if_it_already_exists_world_readable() {
        use std::os::unix::fs::PermissionsExt;
        let d = tmp_dir("ledger-perm");
        let ledger = d.join(LEDGER_FILE_NAME);
        fs::write(&ledger, "{}\n").unwrap();
        fs::set_permissions(&ledger, fs::Permissions::from_mode(0o644)).unwrap();

        let s = RedactionSummary {
            files_touched: 1,
            lines_removed: 2,
            ..Default::default()
        };
        append_ledger(&d, 1, 2, 3, &s).unwrap();

        let mode = fs::metadata(&ledger).unwrap().permissions().mode() & 0o777;
        assert_eq!(mode, 0o600, "⚠️ 台帳が 0600 でない（mode={mode:o}）");
    }

    /// ★ 1 行も落ちないならファイルに触らない。
    #[test]
    fn redact_file_is_a_noop_when_nothing_matches() {
        let d = tmp_dir("noop");
        let p = d.join("gse_20260823_130000.ndjson");
        let original = "{\"t\":1}\n{\"t\":2}\n";
        fs::write(&p, original).unwrap();
        assert_eq!(
            redact_file(&p, 1000, 2000, &HandmarkSubs::new()).unwrap(),
            0
        );
        assert_eq!(fs::read_to_string(&p).unwrap(), original);
    }

    /// ⚠️★★★ 書きかけの現行セッションは触らない。
    #[test]
    fn redact_dir_skips_the_active_session_file() {
        let d = tmp_dir("skip");
        let active = d.join("gse_20260823_140000.ndjson");
        let closed = d.join("gse_20260823_130000.ndjson");
        fs::write(&active, "{\"t\":150}\n").unwrap();
        fs::write(&closed, "{\"t\":150}\n").unwrap();
        let s = redact_dir(&d, 100, 200, Some(&active), &HandmarkSubs::new()).unwrap();
        assert_eq!(s.files_skipped, 1);
        assert_eq!(s.files_touched, 1);
        assert_eq!(s.lines_removed, 1);
        assert_eq!(fs::read_to_string(&active).unwrap(), "{\"t\":150}\n");
    }

    /// ⚠️ 派生ファイルと台帳を巻き込まない。
    #[test]
    fn redact_dir_ignores_derived_files_and_the_ledger() {
        let d = tmp_dir("ignore");
        fs::write(d.join("gse_20260823_150000.anon.ndjson"), "{\"t\":150}\n").unwrap();
        fs::write(d.join(LEDGER_FILE_NAME), "{\"from\":1}\n").unwrap();
        fs::write(d.join("gse-app.log"), "log\n").unwrap();
        let s = redact_dir(&d, 0, u64::MAX, None, &HandmarkSubs::new()).unwrap();
        assert_eq!(s, RedactionSummary::default());
    }

    /// ★ ディレクトリが無くても失敗しない (「消すものが無い」)。
    #[test]
    fn redact_dir_on_missing_directory_is_ok() {
        let d = std::env::temp_dir().join(format!("gse_redaction_absent_{}", std::process::id()));
        let _ = fs::remove_dir_all(&d);
        assert_eq!(
            redact_dir(&d, 0, 100, None, &HandmarkSubs::new()).unwrap(),
            RedactionSummary::default()
        );
    }

    /// ⚠️★★★ 台帳には **5 つの数しか出ない**。
    #[test]
    fn ledger_records_only_the_fact_of_deletion() {
        let d = tmp_dir("ledger");
        let s = RedactionSummary {
            files_touched: 2,
            lines_removed: 37,
            files_skipped: 1,
        };
        let p = append_ledger(&d, 1_700_000_000_000, 100, 200, &s).unwrap();
        let body = fs::read_to_string(&p).unwrap();
        assert_eq!(
            body,
            "{\"requested_at\":1700000000000,\"from\":100,\"to\":200,\"files_touched\":2,\"lines_removed\":37}\n"
        );
        // ⚠️ 「何を消したか」に繋がる語が 1 つも無いこと。
        for forbidden in ["category", "vk", "app", "window", "skipped"] {
            assert!(
                !body.contains(forbidden),
                "台帳に {forbidden:?} が漏れている"
            );
        }
    }

    /// ★ append であること (2 回目が 1 回目を消さない)。
    #[test]
    fn ledger_appends() {
        let d = tmp_dir("ledger_append");
        let s = RedactionSummary::default();
        append_ledger(&d, 1, 0, 1, &s).unwrap();
        let p = append_ledger(&d, 2, 0, 1, &s).unwrap();
        assert_eq!(fs::read_to_string(&p).unwrap().lines().count(), 2);
    }

    // ── 削除の最小幅（ADR-030 D8 (b-2) ／ 補訂 1 項目 5 ／ issue 002）──────────────

    /// 最小幅が穴の閾値を**超える**か（★ 定数を直接比べず、**引数を取る**判定にしてある）。
    ///
    /// ⚠️★★★ 引数化の理由: 定数どうしを直接 `assert!(A > B)` で比べると、
    /// 「**今たまたま大小を満たしている**」ことしか言えず、判定が働いていること
    /// （＝ 崩れたら赤になること）は示せない。★ 真になる組と偽になる組の両方を踏めるようにする。
    fn min_width_exceeds_hole_gap(min_width_ms: u64, hole_gap_ms: u64) -> bool {
        min_width_ms > hole_gap_ms
    }

    /// AC1: 60,000 = 現行 UI（`datetime-local`・秒なし）が作りうる**最小の非 0 幅**。
    #[test]
    fn min_redaction_width_matches_the_ui_granularity() {
        assert_eq!(
            MIN_REDACTION_WIDTH_MS, 60_000,
            "★ `RecordingControls.tsx` の削除入力は分単位。値を変えるなら UI の文言（「1 分」）も同時に直す"
        );
    }

    /// AC2: ⚠️★★★ 最小幅 > `hole_gap_ms`（凍結済みの既定）。
    ///
    /// ★ この test が赤になる場面は 2 つ: `hole_gap_ms` の既定が最小幅以上へ上がったとき、
    /// 最小幅が `hole_gap_ms` 以下へ下がったとき。⚠️ どちらも**削除区間の内側に onset が立つ穴**が開く
    /// （補訂 1 項目 5 が「値を変えるときは最小幅も同時に見直す」と書いた理由）。
    ///
    /// ⚠️ `analysis/` への参照は**この test だけ**（★ 非 test の `redaction.rs` は `analysis/` を
    /// 1 行も import しない。`analysis/` 側も `redaction` を参照しない → 循環しない）。
    #[test]
    fn min_redaction_width_exceeds_hole_gap() {
        let hole_gap_ms = crate::analysis::feat_offline::StallOnsetConfig::default().hole_gap_ms;
        assert!(
            min_width_exceeds_hole_gap(MIN_REDACTION_WIDTH_MS, hole_gap_ms),
            "⚠️★★★ 最小幅 {MIN_REDACTION_WIDTH_MS} ms が hole_gap_ms {hole_gap_ms} ms を超えていない \
             → 削除区間の内側に元に無い onset が立つ穴が開く"
        );
    }

    /// ⚠️ 既定値だけでなく、**P1 事前宣言の探索空間にある `hole_gap_ms` のすべて**でも最小幅が上回ること
    /// （★ `gse-replay --set hole_gap_ms=…` で探索範囲を振ったときに穴が再び開かないため・2026-09-25 security-checker LOW）。
    #[test]
    fn min_redaction_width_exceeds_every_declared_hole_gap() {
        let prereg: serde_json::Value =
            serde_json::from_str(include_str!("../prereg/p1-episode.json")).expect("prereg JSON");
        let declared = prereg["search_space"]["hole_gap_ms"]
            .as_array()
            .expect("search_space.hole_gap_ms は配列");
        assert!(!declared.is_empty(), "探索空間が空だと検査が空振りする");
        for v in declared {
            let hole_gap_ms = v.as_u64().expect("hole_gap_ms は整数");
            assert!(
                min_width_exceeds_hole_gap(MIN_REDACTION_WIDTH_MS, hole_gap_ms),
                "最小幅 {MIN_REDACTION_WIDTH_MS} ms が宣言済みの hole_gap_ms {hole_gap_ms} ms を超えていない"
            );
        }
    }

    /// AC3: ⚠️★★★ **陽性対照** —— 上の判定は**違反した組で `false` を返す**。
    ///
    /// ★ これが無いと、判定が常に真でも AC2 は緑のままである（検査の検査）。
    #[test]
    fn min_redaction_width_check_rejects_a_violating_pair() {
        let hole_gap_ms = crate::analysis::feat_offline::StallOnsetConfig::default().hole_gap_ms;
        // 真になる組（現行値）。
        assert!(min_width_exceeds_hole_gap(
            MIN_REDACTION_WIDTH_MS,
            hole_gap_ms
        ));
        // ⚠️ 現行値を**逆転**させた組は偽。
        assert!(
            !min_width_exceeds_hole_gap(hole_gap_ms, MIN_REDACTION_WIDTH_MS),
            "逆転させた組で判定が真を返している（判定が働いていない）"
        );
        // ⚠️ 境界: **等しい**組も偽（★ 厳密な不等式であること）。
        assert!(!min_width_exceeds_hole_gap(2_000, 2_000));
        assert!(!min_width_exceeds_hole_gap(1_999, 2_000));
        assert!(min_width_exceeds_hole_gap(2_001, 2_000));
    }

    /// AC4: 最小幅未満は **終端側へ**最小幅まで広げる（★ `from` は動かさない）。
    #[test]
    fn narrow_range_is_widened_to_the_minimum() {
        let from = 1_700_000_000_000_u64;
        // ★ 幅 0 も含める: `datetime-local` は秒が無いので、同じ分を両端に入れると幅 0 になる。
        for width in [0, 1, 600, 30_000, MIN_REDACTION_WIDTH_MS - 1] {
            let (f, t) = widen_to_minimum_width(from, from + width).unwrap();
            assert_eq!(f, from, "⚠️ from は動かさない（幅 {width}）");
            assert_eq!(
                t,
                from + MIN_REDACTION_WIDTH_MS,
                "幅 {width} は from + 最小幅まで広がるはず"
            );
        }
        // ⚠️ 桁あふれで**狭まらない**（`u64::MAX` 近傍）。
        let (f, t) = widen_to_minimum_width(u64::MAX - 5, u64::MAX - 1).unwrap();
        assert_eq!((f, t), (u64::MAX - 5, u64::MAX));
        assert!(t >= u64::MAX - 1, "広げる操作が要求より狭めてはならない");
    }

    /// AC5: ⚠️ **陰性対照** —— 幅が既に最小幅以上なら **1 ms も広げない**（過剰に消さない）。
    #[test]
    fn wide_enough_range_is_not_widened() {
        let from = 1_700_000_000_000_u64;
        for width in [
            MIN_REDACTION_WIDTH_MS, // ★ 境界（ちょうど最小幅）
            MIN_REDACTION_WIDTH_MS + 1,
            3_600_000,
            86_400_000,
        ] {
            assert_eq!(
                widen_to_minimum_width(from, from + width).unwrap(),
                (from, from + width),
                "幅 {width} は最小幅以上なので変えてはならない"
            );
        }
        // 全期間（参加の取りやめ）も変えない。
        assert_eq!(widen_to_minimum_width(0, u64::MAX).unwrap(), (0, u64::MAX));
    }

    /// AC6: ⚠️ `from_ms > to_ms` は**従来どおりエラー**（★ 最小幅で救わない・文言も変えない）。
    #[test]
    fn reversed_range_is_still_rejected() {
        let err = widen_to_minimum_width(2_000, 1_000).unwrap_err();
        assert_eq!(
            err, "開始時刻が終了時刻より後になっています。",
            "★ UI がそのまま被験者に見せる文言。変えると従来の振る舞いを壊す"
        );
        // ⚠️ 1 ms だけ逆でも拒否する（★ 「ほぼ同じ」を広げて通さない）。
        assert!(widen_to_minimum_width(1_001, 1_000).is_err());
    }

    /// ⚠️★★★ 起票 15 の欠陥を**再現してから**直ったことを通しで固める（★ AC1〜6 は部品の検査）。
    ///
    /// 1 秒おきの `feat` 行の中で `[30,900, 31,500]` を消すと**消えるのは 1 本だけ**で、
    /// 隣接差がちょうど 2,000 ms（＝ `hole_gap_ms`。**超えない**）なので区間が切れず、
    /// 元に無い onset が削除区間の内側に立った。→ 広げたあとは穴が区間を切ること。
    #[test]
    fn widening_makes_a_narrow_deletion_split_the_observed_intervals() {
        use crate::analysis::feat_offline::stall_onset::observed_intervals;
        let hole_gap_ms = crate::analysis::feat_offline::StallOnsetConfig::default().hole_gap_ms;
        let rows: Vec<String> = (0..=120_u64)
            .map(|k| format!(r#"{{"type":"feat","t":{}}}"#, k * 1000))
            .collect();
        let feat_ts_after = |from: u64, to: u64| -> Vec<u64> {
            let (kept, _) = retain_outside_range(rows.iter().map(String::as_str), from, to);
            kept.iter().filter_map(|l| line_timestamp(l)).collect()
        };

        // ★ 陽性対照（欠陥の再現）: 広げないと 1 本だけ消え、区間は切れない。
        let unwidened = feat_ts_after(30_900, 31_500);
        assert_eq!(unwidened.len(), rows.len() - 1, "消えるのは feat 1 本だけ");
        assert_eq!(
            observed_intervals(&unwidened, hole_gap_ms).len(),
            1,
            "⚠️ 欠陥の再現に失敗した（前提が変わった: 広げなくても穴が切れるなら本 test を見直す）"
        );

        // ★ 直った: 最小幅まで広げると、消えた区間が穴として観測区間を 2 つに割る。
        let (from, to) = widen_to_minimum_width(30_900, 31_500).unwrap();
        let widened = feat_ts_after(from, to);
        assert_eq!(
            observed_intervals(&widened, hole_gap_ms),
            vec![(0, 30_000), (91_000, 120_000)],
            "広げた区間 [{from}, {to}] が穴として区間を切っていない"
        );
    }

    /// 全行種が区間の削除の鍵を持つ（ADR-052 D2・段 1 の同意の配る前の条件 5）。
    ///
    /// 行種と必須の欄を `schema/current.json`（`schema_dto.rs` から機械生成）から読むので、行種を足すと
    /// 自動でこの検査に入る。除外は [`NEVER_REDACTED`] の 4 行種だけ。
    #[test]
    fn every_line_type_in_the_schema_has_a_redaction_key() {
        let schema: serde_json::Value =
            serde_json::from_str(include_str!("../schema/current.json")).unwrap();
        let variants = schema["oneOf"].as_array().expect("oneOf");
        let mut seen = std::collections::BTreeSet::new();
        let mut checked = 0usize;
        for v in variants {
            let ty = v["properties"]["type"]["enum"][0]
                .as_str()
                .or_else(|| v["properties"]["type"]["const"].as_str())
                .expect("type");
            seen.insert(ty);
            if NEVER_REDACTED.contains(&ty) {
                continue;
            }
            let key = time_key(ty);
            let required: Vec<&str> = v["required"]
                .as_array()
                .expect("required")
                .iter()
                .filter_map(serde_json::Value::as_str)
                .collect();
            assert!(
                required.contains(&key),
                "{ty:?} は削除の鍵 {key:?} を必須の欄に持たない（別名なら time_key に足す）"
            );
            let line = format!(r#"{{"type":"{ty}","{key}":1500}}"#);
            let (kept, removed) = retain_outside_range([line.as_str()], 1_000, 2_000);
            assert_eq!((kept.len(), removed), (0, 1), "{ty:?} が区間で消えない");
            checked += 1;
        }
        let known: std::collections::BTreeSet<&str> = crate::capabilities::KNOWN_LINE_TYPES
            .iter()
            .copied()
            .collect();
        assert_eq!(seen, known, "schema の行種と KNOWN_LINE_TYPES が食い違う");
        assert_eq!(checked, known.len() - NEVER_REDACTED.len());
        // 除外の行種は区間の中でも残る
        for ty in NEVER_REDACTED {
            let line = format!(r#"{{"type":"{ty}","t":1500}}"#);
            assert_eq!(retain_outside_range([line.as_str()], 1_000, 2_000).1, 0);
        }
    }

    // ---- 手跡の累計から区間の量を引く（段 1 の同意の判断 13・本タスクの判断 1）----

    const D: i64 = 20_411;

    fn hm_line(day: i64, t: u64, shown: u64, visible: Option<u64>) -> String {
        let v = visible.map_or("null".to_string(), |v| v.to_string());
        format!(
            r#"{{"type":"handmark_day","t":{t},"day":{day},"assigned":"on","late_start_day":20410,"first_shown_day":20410,"shown_ms":{shown},"visible_ms":{v},"toggles":[],"input_toggles":[],"stage_starts":[],"overflow":false,"table_sha256":null,"draw_seed":null,"reason":null}}"#
        )
    }

    fn snap(day: i64, t: u64, s: u64, v: u64) -> HandmarkSnap {
        HandmarkSnap {
            day,
            t,
            shown_ms: s,
            visible_ms: v,
            skipped: false,
        }
    }

    fn sub(s: u64, v: u64) -> HandmarkSub {
        HandmarkSub {
            shown_ms: s,
            visible_ms: v,
            until: None,
        }
    }

    fn sub_until(s: u64, v: u64, until: u64) -> HandmarkSub {
        HandmarkSub {
            until: Some(until),
            ..sub(s, v)
        }
    }

    fn day_snaps() -> Vec<HandmarkSnap> {
        vec![
            snap(D, 1_000, 100, 80),
            snap(D, 2_000, 200, 150),
            snap(D, 3_000, 300, 250),
            snap(D, 4_000, 400, 300),
        ]
    }

    #[test]
    fn the_subtraction_is_the_next_row_minus_the_previous_row() {
        let subs = handmark_subtractions(&day_snaps(), None, 1_500, 2_500);
        assert_eq!(subs.get(&D), Some(&sub(200, 170)));
        // 区間の端が行の時刻ちょうど(両端を含む)なら、その行は区間の中で、前後は外の行
        let subs = handmark_subtractions(&day_snaps(), None, 2_000, 3_000);
        assert_eq!(subs.get(&D), Some(&sub(300, 220)));
    }

    #[test]
    fn without_a_later_row_the_running_total_is_the_next() {
        let live = snap(D, 9_999, 500, 400);
        let subs = handmark_subtractions(&day_snaps(), Some(live), 3_500, 5_000);
        assert_eq!(subs.get(&D), Some(&sub(200, 150)));
        // 走行中の累計も無ければ、後の行が無いので引かない(区間の中の行は消える)
        assert!(handmark_subtractions(&day_snaps(), None, 3_500, 5_000).is_empty());
    }

    #[test]
    fn without_an_earlier_row_the_day_starts_at_zero() {
        let subs = handmark_subtractions(&day_snaps(), None, 0, 1_500);
        assert_eq!(subs.get(&D), Some(&sub(200, 150)));
    }

    #[test]
    fn only_the_days_that_have_a_later_row_are_subtracted() {
        // 前の日の行は区間より前にしか無い → 前の日は引かない。今日は最初の行(小さい累計)を引く
        let snaps = vec![
            snap(D - 1, 500, 50, 40),
            snap(D - 1, 900, 90, 80),
            snap(D, 3_000, 30, 20),
            snap(D, 4_000, 130, 120),
        ];
        let subs = handmark_subtractions(&snaps, None, 950, 2_000);
        assert_eq!(subs.get(&(D - 1)), None);
        assert_eq!(subs.get(&D), Some(&sub(30, 20)));
        // 区間が 2 日にまたがる: 両方の日を引く
        let subs = handmark_subtractions(&snaps, None, 600, 3_500);
        assert_eq!(subs.get(&(D - 1)), None, "前の日は区間より後の行が無い");
        assert_eq!(subs.get(&D), Some(&sub(130, 120)));
        let subs = handmark_subtractions(&snaps, Some(snap(D - 1, 0, 95, 85)), 600, 3_500);
        assert_eq!(subs.get(&(D - 1)), Some(&sub(45, 45)));
    }

    #[test]
    fn a_reversed_range_subtracts_nothing() {
        assert!(handmark_subtractions(&day_snaps(), None, 2_500, 1_500).is_empty());
    }

    #[test]
    fn rows_without_a_visible_total_are_not_snapshots() {
        assert_eq!(handmark_snap(&hm_line(D, 1_000, 0, None)), None);
        assert_eq!(
            handmark_snap(&hm_line(D, 1_000, 5, Some(4))),
            Some(snap(D, 1_000, 5, 4))
        );
        assert_eq!(handmark_snap(r#"{"type":"key","t":1}"#), None);
    }

    #[test]
    fn subtracting_keeps_visible_within_shown_and_never_goes_below_zero() {
        assert_eq!(subtract_handmark(100, 90, sub(30, 10)), (70, 70));
        assert_eq!(subtract_handmark(10, 5, sub(30, 30)), (0, 0));
    }

    /// 区間の量が、区間の前後の行の差からも、後の行の累計からも読めない（ファイルをまたいでも）。
    #[test]
    fn after_redaction_the_deleted_amount_cannot_be_read_from_any_row() {
        let d = tmp_dir("handmark-sub");
        // 再起動をまたぐ: 前のファイルと後のファイル
        let a = d.join("gse_o1_a.ndjson");
        let b = d.join("gse_o1_b.ndjson");
        std::fs::write(
            &a,
            format!(
                "{}\n{}\n",
                hm_line(D, 1_000, 100, Some(80)),
                hm_line(D, 2_000, 200, Some(150))
            ),
        )
        .unwrap();
        std::fs::write(
            &b,
            format!(
                "{}\n{}\n{}\n",
                hm_line(D, 3_000, 300, Some(250)),
                hm_line(D, 4_000, 400, Some(300)),
                hm_line(D, 4_500, 0, None)
            ),
        )
        .unwrap();
        let snaps = collect_handmark_snaps(&d, None);
        assert_eq!(snaps.len(), 4, "累計の無い行は写しにしない");
        let subs = handmark_subtractions(&snaps, None, 1_500, 2_500);
        let s = redact_dir(&d, 1_500, 2_500, None, &subs).unwrap();
        assert_eq!(s.lines_removed, 3, "区間の中の 1 行 + 引いた 2 行");
        let rows: Vec<HandmarkSnap> = collect_handmark_snaps(&d, None)
            .into_iter()
            .collect::<std::collections::BTreeSet<_>>()
            .into_iter()
            .collect();
        let got: Vec<(u64, u64, u64)> = rows
            .iter()
            .map(|r| (r.t, r.shown_ms, r.visible_ms))
            .collect();
        assert_eq!(
            got,
            vec![(1_000, 100, 80), (3_000, 100, 80), (4_000, 200, 130)]
        );
        // 区間の前後の行の差が 0（区間の中の量が読めない）
        assert_eq!((got[1].1 - got[0].1, got[1].2 - got[0].2), (0, 0));
        // 累計の無い行には触らない
        assert!(std::fs::read_to_string(&b)
            .unwrap()
            .contains(&hm_line(D, 4_500, 0, None)));
        // 引く量の無い削除では書き換えない(対照)
        let none = handmark_subtractions(&collect_handmark_snaps(&d, None), None, 10_000, 20_000);
        assert_eq!(
            redact_dir(&d, 10_000, 20_000, None, &none)
                .unwrap()
                .lines_removed,
            0
        );
        let _ = std::fs::remove_dir_all(&d);
    }

    /// いま書いているファイル（書き換えない）に区間より後の行がある日は引かない。再開の後の消し直しで 1 回だけ引く
    /// （本タスクの判断 6・レビューの H1）。
    #[test]
    fn a_day_with_later_rows_in_the_skipped_file_is_not_subtracted_and_a_retry_subtracts_once() {
        let d = tmp_dir("handmark-skip");
        let closed = d.join("gse_o1_a.ndjson");
        let cur = d.join("gse_o1_b.ndjson");
        std::fs::write(
            &closed,
            format!(
                "{}\n{}\n",
                hm_line(D, 1_000, 100, Some(100)),
                hm_line(D, 2_000, 120, Some(120))
            ),
        )
        .unwrap();
        std::fs::write(&cur, format!("{}\n", hm_line(D, 3_000, 130, Some(130)))).unwrap();
        // 一時停止中の削除: いま書いているファイルに区間より後の行がある → 引かない(走行中の累計からも)
        let snaps = collect_handmark_snaps(&d, Some(&cur));
        let live = snap(D, 9_000, 131, 131);
        let subs = handmark_subtractions(&snaps, Some(live), 1_500, 2_500);
        assert!(subs.is_empty(), "{subs:?}");
        redact_dir(&d, 1_500, 2_500, Some(&cur), &subs).unwrap();
        // 対照: 飛ばさなければ引く
        assert_eq!(
            handmark_subtractions(&collect_handmark_snaps(&d, None), Some(live), 1_500, 2_500)
                .get(&D),
            Some(&sub(30, 30))
        );
        // 再開して消し直す(いまのファイルは閉じた): 1 回だけ引く
        let snaps = collect_handmark_snaps(&d, None);
        let subs = handmark_subtractions(&snaps, Some(live), 1_500, 2_500);
        assert_eq!(subs.get(&D), Some(&sub(30, 30)));
        redact_dir(&d, 1_500, 2_500, None, &subs).unwrap();
        let got: Vec<u64> = {
            let mut v = collect_handmark_snaps(&d, None);
            v.sort();
            v.iter().map(|s| s.shown_ms).collect()
        };
        assert_eq!(got, vec![100, 100]);
        // 3 回目: 何も引かない(冪等)
        let subs = handmark_subtractions(
            &collect_handmark_snaps(&d, None),
            Some(snap(D, 9_000, 101, 101)),
            1_500,
            2_500,
        );
        assert!(subs.is_empty(), "{subs:?}");
        let _ = std::fs::remove_dir_all(&d);
    }

    /// 累計が日の途中で 0 から始め直していれば（状態ファイルが消えた後の起動）、next と同じ区切りの中で prev を探す。
    #[test]
    fn a_running_total_that_restarts_from_zero_is_split() {
        let snaps = vec![
            snap(D, 1_000, 500, 500),
            snap(D, 2_000, 600, 600),
            // ここで状態ファイルが消えて 0 から
            snap(D, 3_000, 10, 10),
            snap(D, 4_000, 70, 60),
        ];
        // 区間 [2_500, 3_500]: next = 4_000 の行(70)、prev は同じ区切りに区間の前の行が無いので 0
        let subs = handmark_subtractions(&snaps, None, 2_500, 3_500);
        assert_eq!(subs.get(&D), Some(&sub(70, 60)));
        // 区間 [1_500, 1_800]: next = 2_000(600)、prev = 1_000(500)。当てるのは 0 から始め直す前(3_000 より前)まで
        let subs = handmark_subtractions(&snaps, None, 1_500, 1_800);
        assert_eq!(subs.get(&D), Some(&sub_until(100, 100, 3_000)));
        // 当てた後: 始め直した後の行(10・70)は削られない(Codex P2)
        let line = |t, s, v| hm_line(D, t, s, Some(v));
        assert!(subtract_handmark_day(&line(2_000, 600, 600), 1_800, &subs).is_some());
        assert_eq!(
            subtract_handmark_day(&line(3_000, 10, 10), 1_800, &subs),
            None
        );
        assert_eq!(
            subtract_handmark_day(&line(4_000, 70, 60), 1_800, &subs),
            None
        );
        assert!(!subs[&D].applies_to_live());
        // 走行中の累計が最後の行より小さい(0 から始め直した)なら、走行中の累計そのものを引く
        let subs = handmark_subtractions(&snaps, Some(snap(D, 9_000, 5, 5)), 4_500, 5_000);
        assert_eq!(subs.get(&D), Some(&sub(5, 5)));
        assert!(subs[&D].applies_to_live());
        // 区間の後の行が始め直す前の区切りで、走行中の累計が始め直した後なら、走行中の累計には当てない
        let two = vec![snap(D, 1_000, 500, 500), snap(D, 2_000, 600, 600)];
        let subs = handmark_subtractions(&two, Some(snap(D, 9_000, 5, 5)), 1_200, 1_500);
        assert_eq!(subs.get(&D), Some(&sub_until(100, 100, u64::MAX)));
        assert!(!subs[&D].applies_to_live());
    }

    /// 一時停止中に、いま書いているファイルの区間の中にだけ行がある削除でも引かない。再開して消し直すと 1 回だけ
    /// 引き、その後の別の区間の削除で累計が 0 に崩れない（/cross-review の Claude H1）。
    #[test]
    fn rows_inside_the_range_in_the_skipped_file_also_defer_the_day() {
        let d = tmp_dir("handmark-skip-inside");
        let cur = d.join("gse_o1_a.ndjson");
        std::fs::write(
            &cur,
            format!(
                "{}\n{}\n",
                hm_line(D, 1_000, 100, Some(100)),
                hm_line(D, 2_000, 120, Some(120))
            ),
        )
        .unwrap();
        // 一時停止中の削除: 区間 [1_500, 3_000] の後の行は無いが、中の行がいまのファイルにある → 引かない
        let subs = handmark_subtractions(
            &collect_handmark_snaps(&d, Some(&cur)),
            Some(snap(D, 9_000, 125, 125)),
            1_500,
            3_000,
        );
        assert!(subs.is_empty(), "{subs:?}");
        // 対照: 旧い条件(区間より後の行だけ)なら走行中の累計から 25 引いていた
        assert_eq!(
            handmark_subtractions(
                &collect_handmark_snaps(&d, None),
                Some(snap(D, 9_000, 125, 125)),
                1_500,
                3_000
            )
            .get(&D),
            Some(&sub(25, 25))
        );
        // 再開して行が増え(130)、ローテートの後に消し直す: 1 回だけ引く
        std::fs::write(
            &cur,
            format!(
                "{}\n{}\n{}\n",
                hm_line(D, 1_000, 100, Some(100)),
                hm_line(D, 2_000, 120, Some(120)),
                hm_line(D, 5_000, 130, Some(130))
            ),
        )
        .unwrap();
        let subs = handmark_subtractions(
            &collect_handmark_snaps(&d, None),
            Some(snap(D, 9_000, 135, 135)),
            1_500,
            3_000,
        );
        assert_eq!(subs.get(&D), Some(&sub(30, 30)));
        redact_dir(&d, 1_500, 3_000, None, &subs).unwrap();
        let mut rows = collect_handmark_snaps(&d, None);
        rows.sort();
        assert_eq!(
            rows.iter().map(|r| r.shown_ms).collect::<Vec<_>>(),
            vec![100, 100]
        );
        // その後の別の区間の削除: 累計は崩れない(引くのは差の 0)
        let subs = handmark_subtractions(&rows, Some(snap(D, 9_500, 105, 105)), 4_000, 4_500);
        assert!(subs.is_empty(), "{subs:?}");
        let _ = std::fs::remove_dir_all(&d);
    }
}
