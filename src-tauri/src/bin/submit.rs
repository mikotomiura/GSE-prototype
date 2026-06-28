//! gse-submit: 被験者が **ダブルクリック 1 回** で最新セッションを匿名化 → age 暗号化し提出物を
//! 生成するゼロ引数ツール (M0 凍結 / decisions D3 / T2)。
//!
//! `gse-package` がパス・参加者 ID・公開鍵の手打ちを要求するのに対し、本ツールはそれらを
//! **自動解決**してパス手打ちミスを排除する (実データで提出が CLI 手打ちで参加者に不可能だった是正):
//!   - 入力: `~/Documents/GSE-sessions/`(または `$GSE_DATASET/raw/<pid>/`) の最新 `gse_*.ndjson`
//!   - 参加者 ID: `~/.gse/participant_id` (アプリが記録した既存値・読み取り専用)
//!   - 公開鍵: 同梱 `recipient.txt`(exe と同階層) / `$GSE_RECIPIENT` / `--recipient`
//!   - 出力: `~/Documents/GSE-submissions/<P###>_<session>.age`
//!
//! 匿名化 + 暗号化は `gse_next_lib::packaging` に集約 (gse-package と単一情報源)。匿名化保証
//! (VK→KeyCategory・本文非保存・時刻相対化) は両経路で不変。age 依存は `feature = "package"`
//! のみで、blind アプリ本体には載らない。
//! `cargo build --features package --bin gse-submit` でビルドする。

use std::io::{self, Write};
use std::path::PathBuf;
use std::process::ExitCode;

use gse_next_lib::packaging::{
    default_session_dir, default_submission_dir, find_latest_session_ndjson, package_session,
    read_persisted_participant_id,
};

/// 任意の `--recipient <age1...|file>` / `--out <dir>` のみ受ける (基本はゼロ引数)。
fn parse_args() -> Result<(Option<String>, Option<PathBuf>, bool), String> {
    let mut recipient: Option<String> = None;
    let mut out: Option<PathBuf> = None;
    let mut help = false;
    let mut args = std::env::args().skip(1);
    while let Some(a) = args.next() {
        match a.as_str() {
            "--recipient" => recipient = Some(args.next().ok_or("--recipient requires a value")?),
            "--out" => out = Some(PathBuf::from(args.next().ok_or("--out requires a value")?)),
            "-h" | "--help" => help = true,
            other => return Err(format!("unknown arg: {other}")),
        }
    }
    Ok((recipient, out, help))
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

const USAGE: &str = "usage: gse-submit [--recipient <age1...|file>] [--out <dir>]\n\
     最新セッションを自動検出して匿名化+暗号化し提出物 (.age) を生成します。";

/// `Ok(None)` = --help を表示した (正常終了)。`Ok(Some(_))` = 提出物を生成した。
fn run() -> Result<Option<gse_next_lib::packaging::PackageReport>, String> {
    let (cli_recipient, cli_out, help) = parse_args()?;
    if help {
        return Ok(None);
    }

    // 1) 参加者 ID (アプリが記録した既存値)。
    let participant = read_persisted_participant_id().ok_or(
        "参加者 ID (~/.gse/participant_id) が見つかりません。先に GSE アプリでセッションを実行してください。",
    )?;

    // 2) 入力: セッションディレクトリの最新 gse_*.ndjson。
    let session_dir = default_session_dir(&participant)
        .ok_or("セッション保存先 (~/Documents/GSE-sessions) を解決できませんでした。")?;
    let input = find_latest_session_ndjson(&session_dir).ok_or_else(|| {
        format!(
            "提出できるセッション (gse_*.ndjson) が {} に見つかりません。",
            session_dir.display()
        )
    })?;

    // 3) 公開鍵。
    let recipient = resolve_recipient_source(cli_recipient)?;

    // 4) 出力先。
    let out_dir = cli_out
        .or_else(default_submission_dir)
        .unwrap_or_else(|| session_dir.clone());

    // 5) 匿名化 + 暗号化 (gse-package と同一ロジック)。
    package_session(&input, &participant, &recipient, &out_dir).map(Some)
}

fn main() -> ExitCode {
    match run() {
        Ok(None) => {
            // --help: 使い方を stdout に出して正常終了 (exit 0)。
            let _ = writeln!(io::stdout(), "{USAGE}");
            ExitCode::SUCCESS
        }
        Ok(Some(r)) => {
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
            let _ = writeln!(o, "  提出ファイル: {}", r.out_path.display());
            let _ = writeln!(
                o,
                "→ このファイルを研究者の Dropbox File Request に提出してください。\n\
                 (中身は匿名化済みで、研究者の鍵でしか開けません)"
            );
            ExitCode::SUCCESS
        }
        Err(e) => {
            let _ = writeln!(io::stderr(), "gse-submit: {e}");
            ExitCode::from(1)
        }
    }
}
