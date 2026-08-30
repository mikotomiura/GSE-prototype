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

/// NDJSON 1 行が「いつの記録か」を返す。⚠️ ★ **`meta` 行は常に `None`** である。
///
/// ★ 対象は `t` だけである（`key` / `feat` / `paste` / `pointer_bin` / …）。
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
    // ⚠️★★★ **`meta` 行は消さない**（上記 R-12）。★ 行種で弾くので、将来 `meta` に
    //   時刻フィールドが増えても**自動的に守られる**。
    if obj.get("type").and_then(serde_json::Value::as_str) == Some("meta") {
        return None;
    }
    obj.get("t").and_then(serde_json::Value::as_u64)
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
            if let Some(t) = line_timestamp(line) {
                if t >= from_ms && t <= to_ms {
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
    {
        // ⚠️★★★ 原本のパーミッションを**引き継いでから**書く（上の doc コメント参照）。
        //   ★ `rename` 後に締めるのでは**窓が開く**（0644 のファイルが一瞬でも原本の位置に立つ）。
        //   → ★ **作る時点で締める**。⚠️ 原本が読めない場合でも 0600 に倒す（fail-safe）。
        #[cfg(unix)]
        let mut f = {
            use std::os::unix::fs::{OpenOptionsExt, PermissionsExt};
            let mode = fs::metadata(path)
                .map(|m| m.permissions().mode() & 0o777)
                .unwrap_or(0o600);
            fs::OpenOptions::new()
                .write(true)
                .create(true)
                .truncate(true)
                .mode(mode)
                .open(&tmp)
                .map_err(|e| format!("failed to create temp file {}: {e}", tmp.display()))?
        };
        // Windows: NTFS の既定 ACL でユーザープロファイル配下は他ユーザーから読めない
        // (`logger::create_file_at` と同じ判断・同じ理由でここでも追加制限はしない)。
        #[cfg(not(unix))]
        let mut f = fs::File::create(&tmp)
            .map_err(|e| format!("failed to create temp file {}: {e}", tmp.display()))?;
        for line in &kept {
            writeln!(f, "{line}").map_err(|e| format!("failed to write {}: {e}", tmp.display()))?;
        }
        f.flush()
            .map_err(|e| format!("failed to flush {}: {e}", tmp.display()))?;
    }
    fs::rename(&tmp, path)
        .map_err(|e| format!("failed to replace session log {}: {e}", path.display()))?;
    Ok(removed)
}

/// セッションディレクトリ全体から区間内の行を落とす。
///
/// - `dir` …… セッション NDJSON が置かれたディレクトリ（`logger::session_log_dir()` の第 1 要素）
/// - `skip` …… ⚠️ **いま書いているファイル**（★ 呼び出し側が渡す。触らずに数えるだけ）
///
/// ★ 対象は `gse_*.ndjson` の通常ファイルのみ。⚠️ `.anon.ndjson` などの派生と、
/// 台帳 (`redaction_ledger.jsonl`) は**対象外**である。
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

        let mode = fs::metadata(&p).unwrap().permissions().mode() & 0o777;
        assert_ne!(
            mode, 0o600,
            "★ この環境では umask が厳しく、素朴な書き換えでも 0600 が保たれる。\
             ⚠️ その場合 redact_file_preserves_owner_only_permissions は空振りしうる"
        );
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
}
