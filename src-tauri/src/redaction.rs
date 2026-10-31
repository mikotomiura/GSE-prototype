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
    if matches!(
        line_type,
        Some("meta") | Some("session_meta") | Some("invitation_condition")
    ) {
        return None;
    }
    // ★ 既定は `"t"`。⚠️ 別名を書く行種だけを**明示列挙**する（ADR-031 D6）。
    let key = match line_type {
        Some("realtime_label") | Some("vignette_response") => "ts",
        Some("probe_assignment") => "scheduled_ts",
        _ => "t",
    };
    obj.get(key).and_then(serde_json::Value::as_u64)
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
/// | それ以外 | 点（[`line_timestamp`]） |
/// | `meta` / `session_meta` | **`None`（常に残す）** |
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
pub fn redact_file(path: &Path, from_ms: u64, to_ms: u64) -> Result<usize> {
    let content = fs::read_to_string(path)
        .map_err(|e| format!("failed to read session log {}: {e}", path.display()))?;
    let (kept, removed) = retain_outside_range(content.lines(), from_ms, to_ms);
    if removed == 0 {
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
    Ok(removed)
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
        let removed = redact_file(&path, from_ms, to_ms)?;
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
            if matches!(line_type, "meta" | "session_meta" | "invitation_condition") {
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
            .filter(|t| !matches!(*t, "meta" | "session_meta" | "invitation_condition"))
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
        let removed = redact_file(&p, 40, 60).unwrap();
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

        assert_eq!(redact_file(&p, 40, 60).unwrap(), 1);

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
        redact_file(&q, 40, 60).unwrap();
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

        assert_eq!(redact_file(&p, 40, 60).unwrap(), 1);

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
        assert_eq!(redact_file(&p, 1000, 2000).unwrap(), 0);
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
        let s = redact_dir(&d, 100, 200, Some(&active)).unwrap();
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
        let s = redact_dir(&d, 0, u64::MAX, None).unwrap();
        assert_eq!(s, RedactionSummary::default());
    }

    /// ★ ディレクトリが無くても失敗しない (「消すものが無い」)。
    #[test]
    fn redact_dir_on_missing_directory_is_ok() {
        let d = std::env::temp_dir().join(format!("gse_redaction_absent_{}", std::process::id()));
        let _ = fs::remove_dir_all(&d);
        assert_eq!(
            redact_dir(&d, 0, 100, None).unwrap(),
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
}
