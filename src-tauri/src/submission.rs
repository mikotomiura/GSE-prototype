//! 提出物 (`.age`) の **状態** を、アプリ本体 (default features) と提出ツール
//! (`feature = "package"`) の **両方から同じ規則で読む** ための単一情報源。
//!
//! ## なぜ feature gate の外に置くか
//!
//! `packaging.rs` は `age` を使うので `feature = "package"` の中にある。しかし
//! ★ **「未送信が何件あるか」を数えるのに暗号は要らない** (ファイルが在るか無いかだけ)。
//! 盲検アプリ本体は `age` を載せない (decisions D3) が、未送信件数はスタート画面に
//! 出さなければならない (`requirement.md` E)。→ ★ **状態の規則だけをここに置き、
//! 両側が同じ関数を呼ぶ**。さもないと「アプリが数えた件数」と「提出ツールが送る対象」が
//! 別々の規則で drift する。
//!
//! ## 状態はディスクだけが持つ (収束型・`design.md` §1)
//!
//! ```text
//!   ① 閉じ終わった NDJSON   … session_end を持つ、いま書いていないファイル
//!   ② それに対応する .age    … 無ければ作る
//!   ③ それに対応する .sent   … 無ければ送る
//!
//!   未送信 N 件 = ② が在って ③ が無いものの数   ← ★ 別カウンタを持たない
//! ```
//!
//! ⚠️ ★ **永続カウンタを作らない。** 実際 `lib.rs` の `G1_BLOCKS_STARTED` は
//! プロセス再起動でリセットされる。数えるのではなく **突き合わせる**。

use std::path::{Path, PathBuf};

/// 送信済みの印の拡張子。`<name>.age` に対して `<name>.age.sent` を置く。
///
/// ⚠️ ★ **`.age` は消さない**(`requirement.md` スコープ)。送信済みかどうかは
/// 別ファイルで表す。★ 送信先から成否を追えない (GAS の実行数ページはログ本文を
/// 出さず Cloud ログも開けない・`gas-measurements.md` M-5) ので、
/// ★ **端末側のこの印が唯一の真実源**である。
pub const SENT_SUFFIX: &str = "sent";

/// ★ **被験者が送信を確認した**印の拡張子。`<name>.age` に対して `<name>.age.ok`。
///
/// ## ⚠️★ なぜ「送る前の確認」を入れたか (研究者判断 2026-08-08・D-14)
///
/// 目的は **同意の担保**である。⚠️ 配布フォルダはコピーできるので、
/// ★ **同意手続きを経ていない人が G1 ビルドを起動する**経路が塞がっていなかった
/// (security-checker 指摘)。→ ★ **確認が無ければ送信経路が開かない**ようにする。
///
/// ## ★ 失っても大丈夫な形にしてある
///
/// ⚠️ ★ D-4 は「被験者側の停止スイッチ」を **却下していた** — 無人在宅で
/// 「止めたまま最後まで行く」と回収がゼロになるためである。★ 確認を毎回にすると
/// **その失敗様式が戻る**。そこで被害を最小化する:
///
/// - ★ **`.age` は確認の有無に関わらず必ず作る**。確認が要るのは ③ 送信だけである
///   → 最後の回収経路 (被験者のフォルダから研究者が受け取る) は**常に生きている**
/// - ★ 確認カードは **押されるまで消えない**。次の起動でも出る
/// - ★ 「あとで」を選んでも `.age` は残るので、後からまとめて確認できる
pub const APPROVED_SUFFIX: &str = "ok";

/// 提出物の来歴 (どの NDJSON が何ブロック目だったか) を残す append-only の台帳。
pub const MANIFEST_FILE_NAME: &str = "manifest.jsonl";

/// 送信先の設定ファイル名。配布フォルダ (`g1.mode` と同じ場所) に研究者が置く。
///
/// ★ D-4 (送信停止のスイッチは研究者側にだけ置く) の実体である。
/// ⚠️ **無ければ送信しない**(= `.age` をローカルに作るところで止まる)。再ビルドは要らない。
pub const SUBMIT_CONFIG_FILE_NAME: &str = "g1-submit.json";

/// G1 の参加者 ID (研究者が割り当てた `P012` 等) の保存先ファイル名。
///
/// ⚠️ ★ `~/.gse/participant_id` (logger が自動生成する `P{12桁hex}`) と **別のファイル**にする。
/// 自動生成 ID はセッション保存先のディレクトリ名に使われており、そこへ研究者割当の ID を
/// 上書きすると **保存先が変わる**。★ 用途が違うものを同じ場所に置かない。
pub const G1_ID_FILE_NAME: &str = "g1_participant_id";

/// home ディレクトリ。`USERPROFILE` → `HOME` の順で引く (logger.rs `fallback_log_dir` と一致。
/// Windows git-bash で両方設定された場合に解決先が割れないよう順序を揃える)。
pub fn home_dir() -> Option<PathBuf> {
    std::env::var_os("USERPROFILE")
        .or_else(|| std::env::var_os("HOME"))
        .map(PathBuf::from)
}

/// セッション NDJSON が書かれるディレクトリを解決する。
///
/// **SSOT 注記**: logger.rs `default_log_path` / `fallback_log_dir` の規則を提出側から鏡写しに
/// している (logger の `resolve_participant_id` は ID を新規生成・永続化する副作用があり、
/// 読み取り専用が要る提出ツールからは呼べないため意図的に複製)。logger 側のパス規約を変えたら
/// 本関数も追従すること (`session_dir_mirrors_logger_fallback` テストで一致を監視)。
/// `GSE_DATASET` 設定時は `<GSE_DATASET>/raw/<participant>`、無ければ
/// `~/Documents/GSE-sessions` (logger の fallback)。
pub fn default_session_dir(participant: &str) -> Option<PathBuf> {
    if let Some(dataset) = std::env::var_os("GSE_DATASET") {
        return Some(PathBuf::from(dataset).join("raw").join(participant));
    }
    home_dir().map(|h| h.join("Documents").join("GSE-sessions"))
}

/// 提出物 (`.age`) を置くディレクトリ。`~/Documents/GSE-submissions` (無ければ session dir)。
pub fn default_submission_dir() -> Option<PathBuf> {
    home_dir().map(|h| h.join("Documents").join("GSE-submissions"))
}

/// G1 参加者 ID の保存先 (`~/.gse/g1_participant_id`)。
pub fn g1_participant_id_path() -> Option<PathBuf> {
    home_dir().map(|h| h.join(".gse").join(G1_ID_FILE_NAME))
}

/// G1 参加者 ID を読む (妥当でなければ `None`)。env `GSE_G1_PARTICIPANT_ID` を優先する
/// (検証・テスト経路。★ 被験者運用ではファイルだけを使う)。
pub fn read_g1_participant_id() -> Option<String> {
    if let Ok(v) = std::env::var("GSE_G1_PARTICIPANT_ID") {
        let v = v.trim().to_string();
        if crate::participant_id::is_valid_participant_id(&v) {
            return Some(v);
        }
    }
    g1_participant_id_path()
        .and_then(|p| std::fs::read_to_string(p).ok())
        .map(|s| s.trim().to_string())
        .filter(|s| crate::participant_id::is_valid_participant_id(s))
}

/// G1 参加者 ID を保存する。妥当でない ID は **書かずに** `Err` を返す (fail-closed)。
pub fn write_g1_participant_id(id: &str) -> Result<(), String> {
    let id = id.trim();
    if !crate::participant_id::is_valid_participant_id(id) {
        return Err(
            "参加者 ID が正しくありません (英数字のみ・1〜16 文字。例: P012)。".to_string(),
        );
    }
    let path = g1_participant_id_path().ok_or("保存先 (~/.gse) を解決できませんでした。")?;
    if let Some(dir) = path.parent() {
        std::fs::create_dir_all(dir).map_err(|e| format!("保存先を作成できません: {e}"))?;
    }
    std::fs::write(&path, format!("{id}\n")).map_err(|e| format!("参加者 ID を保存できません: {e}"))
}

/// ★ G1 で「開始する」を押してよいかの判定 (純関数)。
///
/// ⚠️ ★ **通常運用 (G1 でない) は必ず通す。** ID 欄も自動送信も G1 モード限定であり、
/// マーカー無し起動の挙動を 1 バイトも変えない (`requirement.md` スコープ)。
///
/// G1 モードで ID が無いまま開始させてはならない理由: ★ ID が付かない `.age` は
/// **誰のものか分からないまま研究者に届く**。P-1 では ID が提出時の手打ちだったため、
/// 提出しない限り ID がどこにも付かなかった (`requirement.md` 原因 4)。
pub fn g1_start_gate(g1_mode: bool, participant_id: Option<&str>) -> Result<(), String> {
    if !g1_mode {
        return Ok(());
    }
    match participant_id {
        Some(id) if crate::participant_id::is_valid_participant_id(id) => Ok(()),
        _ => Err(
            "参加者 ID が登録されていません。研究者から渡された ID (例: P012) を\
             入力してから開始してください。"
                .to_string(),
        ),
    }
}

// --- 提出物のファイル名規約 -------------------------------------------------

/// 提出物のファイル名。`<participant>_block<NN>_<入力ステム>.age`。
///
/// ★ 受け入れ条件が「ファイル名に **ID とブロック番号**が入ること」を要求している。
/// ★ 入力ステムも残すのは、⚠️ **どの NDJSON から作られたかを名前だけで突き合わせる**ため
/// (`age_for_stem`)。台帳が消えても対応づけが復元できる。
pub fn age_file_name(participant: &str, block: u32, stem: &str) -> String {
    format!("{participant}_block{block:02}_{stem}.age")
}

/// 提出物のファイル名からブロック番号を読む。`participant` が一致しなければ `None`。
///
/// ⚠️ 旧形式 (`<participant>_<stem>.age`・手動提出が作る) は番号を持たないので `None`。
/// ★ 番号の採番はこれを **最大値の材料** にするので、`None` は「番号を消費していない」
/// を意味する。
pub fn parse_block_number(file_name: &str, participant: &str) -> Option<u32> {
    let prefix = format!("{participant}_block");
    let rest = file_name.strip_prefix(&prefix)?;
    let digits: String = rest.chars().take_while(|c| c.is_ascii_digit()).collect();
    if digits.is_empty() {
        return None;
    }
    // 番号の直後は必ず `_` (ステムが続く)。`P1_block1x.age` のような形を番号として読まない。
    if !rest[digits.len()..].starts_with('_') {
        return None;
    }
    digits.parse::<u32>().ok()
}

/// `dir` 内の `.age` を列挙する (`.sent` は含まない)。順序は名前昇順で決定的。
pub fn list_age_files(dir: &Path) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = match std::fs::read_dir(dir) {
        Ok(rd) => rd
            .flatten()
            .map(|e| e.path())
            .filter(|p| p.is_file())
            .filter(|p| {
                p.file_name()
                    .and_then(|s| s.to_str())
                    .map(|n| n.ends_with(".age"))
                    .unwrap_or(false)
            })
            .collect(),
        Err(_) => Vec::new(),
    };
    out.sort();
    out
}

/// `.age` に対する送信済みの印のパス (`<name>.age.sent`)。
pub fn sent_marker_path(age: &Path) -> PathBuf {
    let mut s = age.as_os_str().to_os_string();
    s.push(".");
    s.push(SENT_SUFFIX);
    PathBuf::from(s)
}

/// ★ **この収束器が、この参加者のために作った** `.age` だけを返す。
///
/// ⚠️★★ **「フォルダにある `.age` 全部」ではない** (code-review / security-checker とも HIGH)。
/// `~/Documents/GSE-submissions` には **Phase1 の手動提出物** (`P007_gse_….age`) や
/// **P-1 の残骸** が同じ端末に残る (`notes.md §7-5`: P-1 実機に 4 本ある)。
/// 全部を対象にすると:
/// - ⚠️ ★ **同意の範囲外の記録が G1 のエンドポイントへ送られる**
///   (Phase1 は手動 Dropbox 提出に同意しており、この経路には同意していない)
/// - ⚠️ ★ スタート画面にいきなり「未送信 4 件」が出て、被験者が混乱する
///
/// ★ 判定は **ファイル名がこの参加者のブロック形式か** で行う
/// (`<participant>_block<NN>_….age`)。⚠️ 旧形式 (`<participant>_<stem>.age`) は
/// **対象外**である — ★ 「二重に包まない」(`age_for_stem`) と「送る」は別の話であり、
/// 手動提出した分をこの経路で送り直さない。
pub fn owned_age_files(dir: &Path, participant: &str) -> Vec<PathBuf> {
    list_age_files(dir)
        .into_iter()
        .filter(|p| {
            p.file_name()
                .and_then(|s| s.to_str())
                .and_then(|n| parse_block_number(n, participant))
                .is_some()
        })
        .collect()
}

/// `.age` に対する **送信確認済み**の印のパス (`<name>.age.ok`)。
pub fn approval_marker_path(age: &Path) -> PathBuf {
    let mut s = age.as_os_str().to_os_string();
    s.push(".");
    s.push(APPROVED_SUFFIX);
    PathBuf::from(s)
}

/// まだ送っていない `.age` (= 自分の分で `.sent` が無いもの)。
/// ★ **確認の有無は問わない** (画面の「まだ届いていない」件数はこれで数える)。
pub fn unsent_age_files(dir: &Path, participant: &str) -> Vec<PathBuf> {
    owned_age_files(dir, participant)
        .into_iter()
        .filter(|p| !sent_marker_path(p).exists())
        .collect()
}

/// 未送信の件数。★ **カウンタではなく突き合わせ**なのでズレようがない。
/// ★ 画面に出す件数と、実際に送る対象を **同じ規則**で数える (drift させない)。
pub fn unsent_count(dir: &Path, participant: &str) -> usize {
    unsent_age_files(dir, participant).len()
}

/// ★ **送ってよい** `.age` (= 未送信で、被験者の確認が済んでいるもの)。
///
/// ⚠️ ★ 送信層はこれ**だけ**を送る。確認が無いものは `.age` として残るが送られない。
pub fn approved_unsent_age_files(dir: &Path, participant: &str) -> Vec<PathBuf> {
    unsent_age_files(dir, participant)
        .into_iter()
        .filter(|p| approval_marker_path(p).exists())
        .collect()
}

/// ★ **被験者の確認待ち** の `.age` (= 未送信で、確認の印が無いもの)。
/// 画面はこの件数だけ「送信しますか？」を出す。
pub fn awaiting_approval_age_files(dir: &Path, participant: &str) -> Vec<PathBuf> {
    unsent_age_files(dir, participant)
        .into_iter()
        .filter(|p| !approval_marker_path(p).exists())
        .collect()
}

/// 確認待ちの件数。
pub fn awaiting_approval_count(dir: &Path, participant: &str) -> usize {
    awaiting_approval_age_files(dir, participant).len()
}

/// ★ 確認待ちの `.age` **すべて**に確認の印を付ける (被験者が「送信する」を押したとき)。
///
/// 付けた本数を返す。⚠️ 1 本でも書けなければ `Err`。★ 「押したのに付いていない」を作らない。
pub fn approve_pending(dir: &Path, participant: &str) -> Result<usize, String> {
    let pending = awaiting_approval_age_files(dir, participant);
    let mut n = 0;
    for age in &pending {
        std::fs::write(approval_marker_path(age), b"approved\n")
            .map_err(|e| format!("送信の確認を保存できませんでした: {e}"))?;
        n += 1;
    }
    Ok(n)
}

/// 入力 NDJSON のステム (`gse_20260807_101112`) に対応する `.age` が既に在るか。
///
/// ★ 名前が `..._<stem>.age` で終わるものを探す。⚠️ 旧形式 (`<pid>_<stem>.age`) も
/// 一致するので、**手動提出で作った分を二重に作らない**。
pub fn age_for_stem(dir: &Path, stem: &str) -> Option<PathBuf> {
    let needle = format!("_{stem}.age");
    list_age_files(dir).into_iter().find(|p| {
        p.file_name()
            .and_then(|s| s.to_str())
            .map(|n| n.ends_with(&needle))
            .unwrap_or(false)
    })
}

// --- 送信先の設定 -----------------------------------------------------------

/// 送信先の設定 (研究者が配布フォルダに置く `g1-submit.json`)。
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SubmitConfig {
    /// GAS Web App の `/exec` URL。
    pub endpoint: String,
    /// 共有シークレット。⚠️ ★ **本文に入れる** (GAS の `e` にヘッダが無い・実測 M-3)。
    /// ★ クエリには置かない (URL に残るため)。
    pub secret: String,
}

/// `g1-submit.json` の本文を解釈する (純関数・IO なし)。
///
/// ★ 「壊れている」と「そもそも送信しない設定」を **区別する**:
/// - `Ok(None)`  … endpoint が空 = ★ **意図的に送信を止めている** (D-4)。`.age` はローカルに貯まる
/// - `Ok(Some)`  … 送る
/// - `Err(_)`    … ⚠️ 壊れている。★ **黙って「送らない」に倒さない** (fail-loud)
pub fn parse_submit_config(text: &str) -> Result<Option<SubmitConfig>, String> {
    let v: serde_json::Value = serde_json::from_str(text)
        .map_err(|e| format!("{SUBMIT_CONFIG_FILE_NAME} が JSON として壊れています: {e}"))?;
    let endpoint = v
        .get("endpoint")
        .and_then(|x| x.as_str())
        .unwrap_or("")
        .trim()
        .to_string();
    let secret = v
        .get("secret")
        .and_then(|x| x.as_str())
        .unwrap_or("")
        .trim()
        .to_string();
    if endpoint.is_empty() {
        return Ok(None);
    }
    if !endpoint.starts_with("https://") {
        // ⚠️ ★ 平文 HTTP を許さない。中身は `.age` で読めないが、経路の取り違えを黙認しない。
        return Err(format!(
            "{SUBMIT_CONFIG_FILE_NAME} の endpoint が https:// で始まっていません。"
        ));
    }
    if secret.is_empty() {
        return Err(format!(
            "{SUBMIT_CONFIG_FILE_NAME} に secret がありません (endpoint だけでは送信しません)。"
        ));
    }
    Ok(Some(SubmitConfig { endpoint, secret }))
}

/// 配布フォルダから `g1-submit.json` を読む。ファイルが無ければ `Ok(None)` (= 送信しない)。
/// env `GSE_G1_SUBMIT_CONFIG` があればそのパスを優先する (検証経路)。
pub fn load_submit_config(folder: Option<&Path>) -> Result<Option<SubmitConfig>, String> {
    let path = match std::env::var_os("GSE_G1_SUBMIT_CONFIG") {
        Some(p) => PathBuf::from(p),
        None => match folder {
            Some(f) => f.join(SUBMIT_CONFIG_FILE_NAME),
            None => return Ok(None),
        },
    };
    if !path.is_file() {
        return Ok(None);
    }
    let text = std::fs::read_to_string(&path)
        .map_err(|e| format!("{} を読めません: {e}", path.display()))?;
    parse_submit_config(&text)
}

/// 実行ファイルから見た配布フォルダ (`g1.mode` / `g1-submit.json` を置く場所)。
///
/// ★ `g1.rs` のマーカー探索と **同じ階層規則** を使う。別々に持つと片方だけ直したときに
/// 「マーカーは見えるのに設定は見えない」が起きる。
pub fn distribution_folder() -> Option<PathBuf> {
    let exe = std::env::current_exe().ok()?;
    crate::g1::folder_up(&exe, crate::g1::exe_to_folder_levels())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tmp(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("gse_subm_{}_{}", tag, std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    /// ★ 通常運用 (マーカー無し) は ID が無くても必ず開始できる (非回帰)。
    #[test]
    fn start_gate_never_blocks_normal_mode() {
        assert!(g1_start_gate(false, None).is_ok());
        assert!(g1_start_gate(false, Some("")).is_ok());
    }

    /// ★ G1 で ID が無い / 壊れているときは開始させない (fail-closed)。
    #[test]
    fn start_gate_blocks_g1_without_valid_id() {
        assert!(g1_start_gate(true, None).is_err());
        assert!(g1_start_gate(true, Some("")).is_err());
        assert!(g1_start_gate(true, Some("  ")).is_err());
        assert!(g1_start_gate(true, Some("../etc")).is_err());
        assert!(g1_start_gate(true, Some("P 12")).is_err());
        assert!(g1_start_gate(true, Some("P012")).is_ok());
    }

    #[test]
    fn age_file_name_carries_id_and_block() {
        assert_eq!(
            age_file_name("P012", 3, "gse_20260807_101112"),
            "P012_block03_gse_20260807_101112.age"
        );
        // 2 桁を超えても壊れない (10 ブロックの実施なので 10 まで出る)。
        assert_eq!(age_file_name("P012", 10, "gse_x"), "P012_block10_gse_x.age");
    }

    #[test]
    fn parse_block_number_reads_own_files_only() {
        assert_eq!(
            parse_block_number("P012_block03_gse_x.age", "P012"),
            Some(3)
        );
        assert_eq!(
            parse_block_number("P012_block10_gse_x.age", "P012"),
            Some(10)
        );
        // 別の参加者の分は数えない。
        assert_eq!(parse_block_number("P013_block03_gse_x.age", "P012"), None);
        // 旧形式 (番号なし) は番号を消費していない。
        assert_eq!(parse_block_number("P012_gse_x.age", "P012"), None);
        // 番号の直後が `_` でない形を番号として読まない。
        assert_eq!(parse_block_number("P012_block3x_gse.age", "P012"), None);
    }

    /// ★ 未送信は **`.age` が在って `.sent` が無いもの**。カウンタを持たない。
    #[test]
    fn unsent_is_a_diff_between_two_kinds_of_files() {
        let d = tmp("unsent");
        std::fs::write(d.join("P012_block01_gse_a.age"), b"x").unwrap();
        std::fs::write(d.join("P012_block02_gse_b.age"), b"x").unwrap();
        std::fs::write(d.join("P012_block02_gse_b.age.sent"), b"ok").unwrap();
        // `.age` でないものは数えない。
        std::fs::write(d.join("notes.txt"), b"x").unwrap();
        assert_eq!(unsent_count(&d, "P012"), 1);
        assert_eq!(
            unsent_age_files(&d, "P012")[0].file_name().unwrap(),
            "P012_block01_gse_a.age"
        );
        // ★ 印を足せば 0 になる (= 何度走らせても同じ状態に収束する)。
        std::fs::write(d.join("P012_block01_gse_a.age.sent"), b"ok").unwrap();
        assert_eq!(unsent_count(&d, "P012"), 0);
        let _ = std::fs::remove_dir_all(&d);
    }

    /// ⚠️★★ **他人の分・Phase1 の手動提出物・旧形式を「未送信」に数えない。**
    ///
    /// `~/Documents/GSE-submissions` は使い回されるフォルダで、P-1 の実機には
    /// 旧形式の `.age` が 4 本残っている (`notes.md §7-5`)。★ これを数えると
    /// 被験者のスタート画面にいきなり「未送信 4 件」が出て、⚠️ **同意していない経路で
    /// 送られる**ことにもなる。
    #[test]
    fn foreign_and_legacy_submissions_are_not_ours() {
        let d = tmp("owned");
        std::fs::write(d.join("P012_block01_gse_a.age"), b"x").unwrap(); // ★ 自分の分
        std::fs::write(d.join("P007_block01_gse_b.age"), b"x").unwrap(); // 他人の分
        std::fs::write(d.join("P012_gse_c.age"), b"x").unwrap(); // 旧形式 (手動提出)
        std::fs::write(d.join("P007_gse_d.age"), b"x").unwrap(); // 他人の旧形式
        assert_eq!(unsent_count(&d, "P012"), 1);
        assert_eq!(
            owned_age_files(&d, "P012")[0].file_name().unwrap(),
            "P012_block01_gse_a.age"
        );
        // ★ ただし旧形式でも「もう包んである」判定には使う (二重に包まないため)。
        assert!(age_for_stem(&d, "gse_c").is_some());
        let _ = std::fs::remove_dir_all(&d);
    }

    #[test]
    fn unsent_count_is_zero_for_missing_dir() {
        let d = std::env::temp_dir().join(format!("gse_subm_missing_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        assert_eq!(unsent_count(&d, "P012"), 0);
    }

    /// ★ 既に `.age` がある NDJSON は二度と包まない (べき等)。旧形式も一致させる。
    #[test]
    fn age_for_stem_matches_new_and_legacy_names() {
        let d = tmp("stem");
        std::fs::write(d.join("P012_block01_gse_20260807_101112.age"), b"x").unwrap();
        std::fs::write(d.join("P012_gse_20260807_222222.age"), b"x").unwrap();
        assert!(age_for_stem(&d, "gse_20260807_101112").is_some());
        assert!(age_for_stem(&d, "gse_20260807_222222").is_some()); // 手動提出の分
        assert!(age_for_stem(&d, "gse_20260807_999999").is_none());
        let _ = std::fs::remove_dir_all(&d);
    }

    /// ⚠️ ★ 「送信を止めている」と「設定が壊れている」を混ぜない。
    #[test]
    fn submit_config_distinguishes_off_from_broken() {
        // 送信オフ (D-4 の研究者側スイッチ)。
        assert_eq!(
            parse_submit_config(r#"{"endpoint":"","secret":"s"}"#),
            Ok(None)
        );
        assert_eq!(parse_submit_config("{}"), Ok(None));
        // 正常。
        assert_eq!(
            parse_submit_config(r#"{"endpoint":"https://example.test/exec","secret":"s"}"#),
            Ok(Some(SubmitConfig {
                endpoint: "https://example.test/exec".to_string(),
                secret: "s".to_string(),
            }))
        );
        // ⚠️ 壊れている: JSON でない / http:// / secret 欠落 → **黙って「送らない」に倒さない**。
        assert!(parse_submit_config("not json").is_err());
        assert!(
            parse_submit_config(r#"{"endpoint":"http://example.test/exec","secret":"s"}"#).is_err()
        );
        assert!(parse_submit_config(r#"{"endpoint":"https://example.test/exec"}"#).is_err());
    }

    /// logger.rs fallback_log_dir と同じ末尾規約を保つ (SSOT 鏡写しの drift 監視)。
    #[test]
    fn session_dir_mirrors_logger_fallback() {
        let dir = default_session_dir("P007").expect("home resolvable in test");
        let s = dir.to_string_lossy().replace('\\', "/");
        assert!(
            s.ends_with("Documents/GSE-sessions") || s.ends_with("raw/P007"),
            "unexpected session dir (logger fallback drift?): {s}"
        );
    }

    #[test]
    fn sent_marker_is_a_sibling_not_a_rename() {
        let p = Path::new("/tmp/x/P012_block01_gse_a.age");
        assert_eq!(
            sent_marker_path(p),
            Path::new("/tmp/x/P012_block01_gse_a.age.sent")
        );
    }
}
