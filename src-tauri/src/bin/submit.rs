//! gse-submit: 被験者が **ダブルクリック 1 回** で最新セッションを匿名化 → age 暗号化し提出物を
//! 生成するゼロ引数ツール (M0 凍結 / decisions D3 / T2)。
//!
//! `gse-package` がパス・参加者 ID・公開鍵の手打ちを要求するのに対し、本ツールはそれらを
//! **自動解決**してパス手打ちミスを排除する (実データで提出が CLI 手打ちで参加者に不可能だった是正):
//!   - 入力: `~/Documents/GSE-sessions/`(または `$GSE_DATASET/raw/<pid>/`) の最新 `gse_*.ndjson`
//!   - 参加者 ID (ファイル名ラベル): 提出時に **対話入力** (研究者が割り当てた P006 等)。
//!     `GSE_PARTICIPANT_ID`/`GSE_PID` env があれば対話省略。デフォルトは `~/.gse/participant_id`
//!     だが、アプリ自動生成形式 (P+12桁 hex) は崩れたファイル名になるため採用せず強制入力。
//!   - 公開鍵: 同梱 `recipient.txt`(exe と同階層) / `$GSE_RECIPIENT` / `--recipient`
//!   - 出力: `~/Documents/GSE-submissions/<P###>_<session>.age`
//!
//! 匿名化 + 暗号化は `gse_next_lib::packaging` に集約 (gse-package と単一情報源)。匿名化保証
//! (VK→KeyCategory・本文非保存・時刻相対化) は両経路で不変。age 依存は `feature = "package"`
//! のみで、blind アプリ本体には載らない。
//! `cargo build --features package --bin gse-submit` でビルドする。

use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use gse_next_lib::packaging::{
    default_session_dir, default_submission_dir, find_latest_session_ndjson,
    is_valid_participant_id, package_session, read_persisted_participant_id,
};

/// コマンドラインの解釈結果。★ **ゼロ引数の既定挙動は不変**である
/// (被験者の手動提出経路の非回帰。`requirement.md` B)。
#[derive(Default)]
struct Args {
    recipient: Option<String>,
    out: Option<PathBuf>,
    /// 包む対象を明示する (既定は「最新 1 本」)。
    input: Option<PathBuf>,
    /// ★ 収束モード: ディスクの状態を突き合わせ、足りない `.age` を作り、未送信を送る。
    reconcile: bool,
    /// ⚠️★★★ **O1 (R3-a) の収束である** —— `gse_o1_*.ndjson` を対象にし、
    /// `session_end` から **48 時間**の猶予を置いてから包み、⚠️ **承認を求めずに送る**
    /// (研究者判断 O1-2 / 同意文書 §5)。★ 既定 (未指定) は従来どおり G1。
    o1: bool,
    help: bool,
}

fn parse_args() -> Result<Args, String> {
    parse_args_from(std::env::args().skip(1))
}

/// ★ 引数の解釈を **env から切り離す** (テストできるようにするため)。
fn parse_args_from<I: IntoIterator<Item = String>>(args: I) -> Result<Args, String> {
    let mut a = Args::default();
    let mut it = args.into_iter();
    while let Some(arg) = it.next() {
        match arg.as_str() {
            "--recipient" => a.recipient = Some(it.next().ok_or("--recipient requires a value")?),
            "--out" => a.out = Some(PathBuf::from(it.next().ok_or("--out requires a value")?)),
            "--input" => {
                a.input = Some(PathBuf::from(it.next().ok_or("--input requires a value")?))
            }
            "--reconcile" => a.reconcile = true,
            "--o1" => a.o1 = true,
            "-h" | "--help" => a.help = true,
            other => return Err(format!("unknown arg: {other}")),
        }
    }
    if a.reconcile && a.input.is_some() {
        return Err("--reconcile と --input は同時に使えません".to_string());
    }
    // ⚠️★ `--o1` は収束モード専用である。★ 黙って無視すると
    //   「O1 のつもりで指定したのに G1 の規則で包まれた」が静かに起こる。
    if a.o1 && !a.reconcile {
        return Err("--o1 は --reconcile と一緒にのみ使えます".to_string());
    }
    Ok(a)
}

/// 公開鍵の解決順: `--recipient` > `$GSE_RECIPIENT` > exe と同階層の `recipient.txt`。
/// いずれも無ければ案内付きエラー (鍵未配置のまま暗号化しない)。
fn resolve_recipient_source(cli_recipient: Option<String>) -> Result<String, String> {
    if let Some(r) = cli_recipient {
        return Ok(r);
    }
    if let Ok(env) = std::env::var("GSE_RECIPIENT") {
        if !env.trim().is_empty() {
            return Ok(env);
        }
    }
    // exe と同階層の公開鍵ファイル (研究者が配布パッケージに同梱する)。既存配布の `pubkey.txt`
    // と新名 `recipient.txt` の両方を探す (配布物のリネームを強制しない)。
    if let Ok(exe) = std::env::current_exe() {
        if let Some(dir) = exe.parent() {
            for name in ["recipient.txt", "pubkey.txt"] {
                let path = dir.join(name);
                if path.is_file() {
                    return Ok(path.to_string_lossy().into_owned());
                }
            }
        }
    }
    Err("公開鍵が見つかりません。研究者から配布された pubkey.txt (または recipient.txt) を本ツールと\
         同じフォルダに置くか、--recipient <age1...> を指定してください。"
        .to_string())
}

const USAGE: &str =
    "usage: gse-submit [--recipient <age1...|file>] [--out <dir>] [--input <ndjson>]\n\
       gse-submit --reconcile [--o1] [--recipient <age1...|file>] [--out <dir>]\n\
     既定 (ゼロ引数): 最新セッションを自動検出して匿名化+暗号化し提出物 (.age) を生成します。\n\
     --input:     包む NDJSON を明示します (既定の「最新 1 本」を使いません)。\n\
     --reconcile: 閉じ終わった全セッションについて、足りない .age を作り、未送信を送ります\n\
                  (★ 何度実行しても同じ状態に収束します)。\n\
     --o1:        O1 (自然作業の常時収集) の収束を行います。gse_o1_*.ndjson を対象にし、\n\
                  session_end から 48 時間おいてから包み、承認を求めずに送ります。";

/// 生成した `.age` をファイルマネージャで **選択状態** で開く (best-effort)。
/// 被験者が「ファイルが見当たらない」事故 (OneDrive/iCloud の Documents リダイレクトで
/// Explorer/Finder の「ドキュメント」が別実体を指す) を防ぐため、実体の場所を直接見せる。
/// 失敗しても提出自体は成功しているので無視する (戻り値なし)。
fn reveal_in_file_manager(path: &Path) {
    #[cfg(target_os = "windows")]
    {
        // `explorer /select,"<file>"` でフォルダを開き当該ファイルを選択する。
        // 注意: 通常の `.arg()` は arg 全体を二重引用符で括るため `"/select,C:\...\田中 太郎\x.age"`
        // となり explorer が選択に失敗する (引用符が /select の前に来る形を解釈しない既知挙動)。
        // raw_arg で `/select,"<path>"` (引用符はパス側) を手組みし、スペースを含む実体ホームでも
        // 確実に選択させる。
        use std::os::windows::process::CommandExt;
        let _ = std::process::Command::new("explorer")
            .raw_arg(format!("/select,\"{}\"", path.display()))
            .spawn();
    }
    #[cfg(target_os = "macos")]
    {
        // `open -R <file>` で Finder に reveal (ファイル選択状態)。
        let _ = std::process::Command::new("open")
            .arg("-R")
            .arg(path)
            .spawn();
    }
    #[cfg(all(unix, not(target_os = "macos")))]
    {
        // Linux: ファイル選択 API は環境依存なので親フォルダを開く。
        if let Some(dir) = path.parent() {
            let _ = std::process::Command::new("xdg-open").arg(dir).spawn();
        }
    }
}

/// アプリが自動生成した参加者 ID (`generate_participant_id` = `P{bits:012x}`、例 `P02165e17b7b1`)
/// かどうか。この形式はファイル名に入れても研究の参加者番号として意味をなさず「崩れた」ID に
/// 見えるため、対話入力のデフォルトには採用しない (研究者割当の P006 等を必ず入力させる)。
fn looks_autogenerated(id: &str) -> bool {
    // 生成器は `{:012x}` (小文字 hex) しか出さないので小文字 hex に限定し、
    // 13 文字・全小文字 hex のまれな割当 ID を過剰に自動生成扱いしないようにする。
    let mut chars = id.chars();
    id.len() == 13
        && chars.next() == Some('P')
        && chars.all(|c| c.is_ascii_digit() || ('a'..='f').contains(&c))
}

/// `GSE_PARTICIPANT_ID` / `GSE_PID` env から妥当な参加者 ID を取得 (自動化・研究者経路)。
fn env_participant_id() -> Option<String> {
    ["GSE_PARTICIPANT_ID", "GSE_PID"]
        .iter()
        .find_map(|k| std::env::var(k).ok())
        .map(|s| s.trim().to_string())
        .filter(|s| is_valid_participant_id(s))
}

/// ファイル名ラベル用の参加者 ID を確定する。
/// 優先: env (`GSE_PARTICIPANT_ID`/`GSE_PID`、対話省略) → 対話入力。
/// 対話のデフォルトは `stored_id` だが、自動生成形式 (または欠損) なら採用せず強制入力させる。
fn resolve_label_participant_id(stored_id: Option<&str>) -> Result<String, String> {
    if let Some(id) = env_participant_id() {
        return Ok(id);
    }
    let default = stored_id.filter(|s| !looks_autogenerated(s));
    prompt_participant_id(default)
}

/// 参加者 ID を対話入力させる (最大 3 回)。空入力は `default` を採用。入力は大文字化して検証。
/// EOF / 非対話 (stdin が読めない) は `default` にフォールバックする (headless・テスト互換)。
fn prompt_participant_id(default: Option<&str>) -> Result<String, String> {
    let mut out = io::stdout().lock();
    for _ in 0..3 {
        let _ = writeln!(
            out,
            "\n参加者 ID を入力してください (研究者が指定した P で始まる番号。例: P006)。"
        );
        match default {
            Some(d) => {
                let _ = write!(out, "  そのまま Enter で [{d}] を使用 > ");
            }
            None => {
                let _ = write!(out, "  ID > ");
            }
        }
        let _ = out.flush();

        let mut line = String::new();
        match io::stdin().read_line(&mut line) {
            Ok(0) | Err(_) => {
                // EOF / 非対話環境: default があれば使い、無ければ案内付きで失敗。
                if let Some(d) = default {
                    let _ = writeln!(out, "(対話入力なし: {d} を使用します)");
                    return Ok(d.to_string());
                }
                return Err("参加者 ID が未指定です (対話入力できない環境)。\
                     GSE_PARTICIPANT_ID を設定して再実行してください。"
                    .to_string());
            }
            Ok(_) => {}
        }

        let entered = line.trim();
        let chosen: Option<String> = if entered.is_empty() {
            default.map(|s| s.to_string())
        } else {
            Some(entered.to_ascii_uppercase())
        };
        match chosen {
            Some(id) if is_valid_participant_id(&id) => return Ok(id),
            Some(id) => {
                let _ = writeln!(
                    out,
                    "  「{id}」は使用できません (英数字のみ・16 文字以内。例: P006)。"
                );
            }
            None => {
                let _ = writeln!(out, "  未入力です。参加者 ID を入力してください。");
            }
        }
    }
    Err("参加者 ID を確定できませんでした (3 回とも無効な入力でした)。".to_string())
}

/// 実行の結末。★ `--reconcile` は「1 本を包む」形に収まらないので別の腕にする。
enum Outcome {
    /// `--help` を表示した (正常終了)。
    Help,
    /// 提出物を 1 本生成した (既定 / `--input`)。
    Packaged(gse_next_lib::packaging::PackageReport),
    /// 収束を 1 回まわした。
    Reconciled(gse_next_lib::reconcile::ReconcileReport),
}

/// `--reconcile`: ディスクの状態を突き合わせ、足りない仕事だけをする。
///
/// ⚠️ ★ **ブロック中に呼ばれない**ことは呼び出し側 (`lib.rs`) が保証する。
/// 本関数は「閉じ終わった NDJSON」しか触らないので、万一ブロック中に走っても
/// 書きかけのファイルには手を出さない (二重の防御)。
fn run_reconcile(args: Args) -> Result<gse_next_lib::reconcile::ReconcileReport, String> {
    use gse_next_lib::reconcile::{reconcile, HttpUploader, ReconcileOptions, Uploader};
    use gse_next_lib::submission;

    // 1) 参加者 ID。★ env (アプリが渡す) → G1 の保存済み ID の順。
    //    ⚠️ ★ **対話入力にフォールバックしない。** 自動提出は誰も見ていない場所で走るので、
    //    プロンプトで止まると「起動したのに何もしていない」状態になる (fail-closed)。
    let participant = env_participant_id()
        .or_else(submission::read_g1_participant_id)
        .ok_or(
            "参加者 ID が登録されていないため自動提出できません。\
             アプリのスタート画面で ID を入力してください。",
        )?;

    // 2) 場所。
    //    ⚠️★ **セッション置き場の解決には logger と同じ ID を使う** (code-review MEDIUM)。
    //    `GSE_DATASET` があるとき logger は `raw/<自動生成 ID>` に書くのに対し、
    //    ここで研究者割当の ID (`P012`) を使うと `raw/P012` を見に行き、
    //    ★ **0 件・エラー無し・exit 0 の完全な空振り**になる (研究者端末で必ず踏む)。
    //    ★ 研究者割当の ID は **ファイル名ラベル専用**である (手動経路 `run_package_one` と同じ扱い)。
    let path_id = read_persisted_participant_id();
    let session_dir = submission::default_session_dir(path_id.as_deref().unwrap_or("P000"))
        .ok_or("セッション保存先 (~/Documents/GSE-sessions) を解決できませんでした。")?;
    if !session_dir.is_dir() {
        // ⚠️ ★ 黙って 0 件にしない。**探した場所が存在しない**ことを言う。
        return Err(format!(
            "セッション保存先が見つかりません: {}",
            session_dir.display()
        ));
    }
    let submission_dir = args
        .out
        .clone()
        .or_else(submission::default_submission_dir)
        .unwrap_or_else(|| session_dir.clone());

    // 3) 公開鍵。
    let recipient = resolve_recipient_source(args.recipient.clone())?;

    // 4) 送信先 (研究者が配布フォルダに置く g1-submit.json)。
    //    ★ 無ければ `.age` を作るところまでで止まる = D-4 の停止スイッチ。
    //    ⚠️ 壊れている場合は Err を返して **黙って「送らない」に倒さない**。
    let cfg = submission::load_submit_config(submission::distribution_folder().as_deref())?;
    let uploader = match cfg.as_ref() {
        Some(c) => Some(HttpUploader::new(c)?),
        None => None,
    };

    // 5) ⚠️★★★ どの収集か。★ **`--o1` はアプリ (`lib.rs`) が O1 モードのときだけ付ける。**
    //    ⚠️ ここで `o1::detect_from_env()` を呼んで自前判定しないのは、
    //    ★ `gse-submit` の `current_exe()` が **アプリ本体と同じ階層とは限らない**
    //    (macOS のバンドル内 sidecar) ためである。→ **判定はアプリが 1 か所で行い、渡す。**
    let mode = if args.o1 {
        gse_next_lib::reconcile::CollectionMode::O1
    } else {
        gse_next_lib::reconcile::CollectionMode::G1
    };
    let now_ms = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;

    let opts = ReconcileOptions {
        session_dir,
        submission_dir,
        participant,
        recipient,
        mode,
        now_ms,
    };
    Ok(reconcile(
        &opts,
        uploader.as_ref().map(|u| u as &dyn Uploader),
    ))
}

fn run() -> Result<Outcome, String> {
    let args = parse_args()?;
    if args.help {
        return Ok(Outcome::Help);
    }
    if args.reconcile {
        return run_reconcile(args).map(Outcome::Reconciled);
    }
    run_package_one(args).map(Outcome::Packaged)
}

/// 包む対象の NDJSON を決める。
///
/// ★ `--input` があればそれ。⚠️ **無ければ従来どおり「最新 1 本」**である
/// (ゼロ引数の既定挙動の非回帰)。指定されたパスが無ければ **黙って最新へ落ちない**
/// — 落とすと「別のセッションを提出したのに気づかない」形になる (fail-closed)。
fn resolve_input(cli_input: Option<PathBuf>, session_dir: &Path) -> Result<PathBuf, String> {
    match cli_input {
        Some(p) => {
            if !p.is_file() {
                return Err(format!(
                    "指定された NDJSON が見つかりません: {}",
                    p.display()
                ));
            }
            Ok(p)
        }
        None => find_latest_session_ndjson(session_dir).ok_or_else(|| {
            format!(
                "提出できるセッション (gse_*.ndjson) が {} に見つかりません。",
                session_dir.display()
            )
        }),
    }
}

/// 既定 (ゼロ引数) と `--input` の経路。★ **ゼロ引数の挙動は従来と 1 バイトも変えない。**
fn run_package_one(args: Args) -> Result<gse_next_lib::packaging::PackageReport, String> {
    let Args {
        recipient: cli_recipient,
        out: cli_out,
        input: cli_input,
        ..
    } = args;

    // 1) セッション探索用 ID (アプリが記録した既存値)。入力 NDJSON の場所特定にのみ使う。
    //    研究者の GSE_DATASET 経路は `raw/<id>` を辿るため ID 必須。被験者の非 dataset 経路は
    //    `~/Documents/GSE-sessions` で participant 非依存なので、ID 欠損・破損でも探索を続行し
    //    (ファイル名は後段の対話入力で確定する)、提出不能に陥らせない。
    let dataset_mode = std::env::var_os("GSE_DATASET").is_some();
    let stored_id = read_persisted_participant_id();

    // 2) 入力: セッションディレクトリの最新 gse_*.ndjson。
    let session_dir = if dataset_mode {
        let id = stored_id.as_deref().ok_or(
            "参加者 ID (~/.gse/participant_id) が見つかりません。先に GSE アプリでセッションを実行してください。",
        )?;
        default_session_dir(id)
    } else {
        // 非 dataset 経路: 戻り値は participant 非依存。欠損時は形式上のプレースホルダを渡す。
        default_session_dir(stored_id.as_deref().unwrap_or("P000"))
    }
    .ok_or("セッション保存先 (~/Documents/GSE-sessions) を解決できませんでした。")?;
    let input = resolve_input(cli_input, &session_dir)?;

    // 3) ファイル名ラベル用の参加者 ID を確定 (研究者割当の P006 等を対話で入力)。
    let label_id = resolve_label_participant_id(stored_id.as_deref())?;

    // 4) 公開鍵。
    let recipient = resolve_recipient_source(cli_recipient)?;

    // 5) 出力先。
    let out_dir = cli_out
        .or_else(default_submission_dir)
        .unwrap_or_else(|| session_dir.clone());

    // 6) 匿名化 + 暗号化 (gse-package と同一ロジック)。ファイル名は label_id を使う。
    package_session(&input, &label_id, &recipient, &out_dir)
}

fn main() -> ExitCode {
    match run() {
        Ok(Outcome::Help) => {
            // --help: 使い方を stdout に出して正常終了 (exit 0)。
            let _ = writeln!(io::stdout(), "{USAGE}");
            ExitCode::SUCCESS
        }
        Ok(Outcome::Reconciled(r)) => {
            let mut o = io::stdout().lock();
            // ★ 呼び出し元 (アプリ) が読む 1 行。⚠️ ファイル名も参加者 ID も出さない
            //   (画面・ログに載るため・data-privacy)。**件数だけ**を出す。
            let _ = writeln!(
                o,
                "GSE_RECONCILE {}",
                serde_json::json!({
                    "packaged": r.packaged,
                    "sent": r.sent,
                    "unsent": r.unsent,
                    "upload_disabled": r.upload_disabled,
                    "skipped_busy": r.skipped_busy,
                    "awaiting_approval": r.awaiting_approval,
                    // ★ G-5: 受け口の上限を超えて送らずに `oversize/` へ移した本数（O1 のみ）。
                    "quarantined": r.quarantined,
                    "errors": r.errors.len(),
                })
            );
            for e in &r.errors {
                let _ = writeln!(io::stderr(), "gse-submit: {e}");
            }
            // ⚠️ ★ 問題があったら **非ゼロで返す**。呼び出し元が「起動したが動いていない」と
            //   「動いたが失敗した」を区別できないと fail-loud にならない。
            if r.errors.is_empty() {
                ExitCode::SUCCESS
            } else {
                ExitCode::from(1)
            }
        }
        Ok(Outcome::Packaged(r)) => {
            let mut o = io::stdout().lock();
            let _ = writeln!(
                o,
                "✓ 最新セッションを匿名化 ({} 行{}) → age 暗号化しました。",
                r.kept,
                if r.skipped > 0 {
                    format!(" / 解析不能 {} 行スキップ", r.skipped)
                } else {
                    String::new()
                },
            );
            let _ = writeln!(o, "\n  提出ファイルの場所:\n    {}\n", r.out_path.display());
            let _ = writeln!(
                o,
                "  ※ 上の場所が「ドキュメント」フォルダに見当たらない場合、OneDrive(Windows) / \n\
                 iCloud(mac) でドキュメントの保存先が変更されている可能性があります。\n\
                 上の絶対パスを直接たどってください。フォルダを自動で開きます。"
            );
            let _ = writeln!(
                o,
                "→ このファイルを研究者の Dropbox File Request に提出してください。\n\
                 (中身は匿名化済みで、研究者の鍵でしか開けません)"
            );
            // 生成物をファイルマネージャで選択状態にして「見当たらない」を防ぐ (best-effort)。
            reveal_in_file_manager(&r.out_path);
            ExitCode::SUCCESS
        }
        Err(e) => {
            let _ = writeln!(io::stderr(), "gse-submit: {e}");
            ExitCode::from(1)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{looks_autogenerated, parse_args_from, resolve_input};
    use std::path::{Path, PathBuf};

    fn args(v: &[&str]) -> Vec<String> {
        v.iter().map(|s| s.to_string()).collect()
    }

    /// ★★ **ゼロ引数の既定は不変**。何も指定しなければ従来と同じ経路に入る。
    #[test]
    fn zero_args_keeps_the_legacy_behaviour() {
        let a = parse_args_from(args(&[])).unwrap();
        assert!(a.input.is_none(), "★ 既定は「最新 1 本」のまま");
        assert!(!a.reconcile);
        assert!(!a.help);
        assert!(a.recipient.is_none());
        assert!(a.out.is_none());
    }

    #[test]
    fn input_and_reconcile_are_parsed() {
        let a = parse_args_from(args(&["--input", "/tmp/x.ndjson"])).unwrap();
        assert_eq!(a.input, Some(PathBuf::from("/tmp/x.ndjson")));
        let a = parse_args_from(args(&["--reconcile"])).unwrap();
        assert!(a.reconcile);
        // 既存フラグと併用できる。
        let a = parse_args_from(args(&["--reconcile", "--out", "/tmp/o"])).unwrap();
        assert!(a.reconcile);
        assert_eq!(a.out, Some(PathBuf::from("/tmp/o")));
    }

    /// ⚠️ 値の無いフラグ / 相互排他 / 未知の引数は **黙って通さない**。
    #[test]
    fn malformed_args_are_rejected() {
        assert!(parse_args_from(args(&["--input"])).is_err());
        assert!(parse_args_from(args(&["--reconcile", "--input", "/tmp/x"])).is_err());
        assert!(parse_args_from(args(&["--nope"])).is_err());
    }

    /// ★ `--input` は **別ディレクトリのファイル**でも受ける (セッションフォルダに縛らない)。
    /// ⚠️ 存在しないパスは **最新 1 本へ黙って落ちない**。
    #[test]
    fn resolve_input_prefers_explicit_path_and_fails_loudly() {
        let dir = std::env::temp_dir().join(format!("gse_submit_input_{}", std::process::id()));
        let elsewhere = dir.join("elsewhere");
        let session = dir.join("sessions");
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&elsewhere).unwrap();
        std::fs::create_dir_all(&session).unwrap();
        // セッションフォルダには「最新 1 本」候補がある。
        std::fs::write(
            session.join("gse_20260101_010101.ndjson"),
            "{\"type\":\"meta\",\"session_start\":1}\n{\"type\":\"key\",\"t\":2,\"vk\":65,\"press\":true}\n",
        )
        .unwrap();
        // 別ディレクトリの明示指定が優先される。
        let explicit = elsewhere.join("gse_20260202_020202.ndjson");
        std::fs::write(&explicit, "{\"type\":\"meta\",\"session_start\":1}\n").unwrap();
        assert_eq!(
            resolve_input(Some(explicit.clone()), &session).unwrap(),
            explicit
        );
        // 指定なしなら従来どおり最新 1 本。
        assert_eq!(
            resolve_input(None, &session)
                .unwrap()
                .file_name()
                .unwrap()
                .to_str()
                .unwrap(),
            "gse_20260101_010101.ndjson"
        );
        // ⚠️ 存在しない指定 → エラー (最新へフォールバックしない)。
        let missing = elsewhere.join("does_not_exist.ndjson");
        assert!(resolve_input(Some(missing), &session).is_err());
        // ディレクトリを渡しても通さない。
        assert!(resolve_input(Some(elsewhere.clone()), &session).is_err());
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// 候補が 1 本も無ければ (指定なし) エラー。★ Path 引数の形も固定する。
    #[test]
    fn resolve_input_errors_when_nothing_to_submit() {
        let dir = std::env::temp_dir().join(format!("gse_submit_empty_in_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        assert!(resolve_input(None, Path::new(&dir)).is_err());
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn autogenerated_ids_are_not_offered_as_default() {
        // generate_participant_id() = format!("P{bits:012x}") = P + 12 桁 hex。
        assert!(looks_autogenerated("P02165e17b7b1"));
        assert!(looks_autogenerated("Pffffffffffff"));
    }

    #[test]
    fn assigned_ids_are_treated_as_meaningful() {
        // 研究者割当のスタディ ID はデフォルトに採用される (= 自動生成形式ではない)。
        assert!(!looks_autogenerated("P006"));
        assert!(!looks_autogenerated("P007"));
        assert!(!looks_autogenerated("P000"));
        // 長さ 13 でも hex 以外を含めば自動生成扱いしない。
        assert!(!looks_autogenerated("P02165e17b7bZ"));
        // P 始まりでない / 空。
        assert!(!looks_autogenerated("X02165e17b7b1"));
        assert!(!looks_autogenerated(""));
    }
}
