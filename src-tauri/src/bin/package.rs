//! gse-package: 被験者端末で raw NDJSON を **匿名化 → age 暗号化** し、研究者に提出する
//! `P###_<session>.age` を生成する自己完結 CLI (D6 / WBS 0.15 / transfer-pipeline)。
//!
//! 被験者 (Mac/Win 混在・非技術者) は Python/age CLI 不要で、bundled exe を 1 コマンド実行するだけ。
//! 出力は研究者の age 公開鍵でのみ復号できる暗号塊なので、転送経路 (Dropbox File Request) は信用不要。
//!
//! 使い方:
//!   gse-package --input <raw.ndjson> --participant P003 --recipient <age1... or pubkey.txt> [--out <dir>]
//!
//! `--recipient` は研究者が生成・配布する age 公開鍵 (`age1...`) かそれを書いたファイル。
//! `cargo build --features package --bin gse-package` でビルドする (age 依存は default に載せない)。
//!
//! 匿名化 + age 暗号化ロジックは `gse_next_lib::packaging` に集約 (gse-submit と単一情報源)。
//! 本 CLI はパス指定の薄いラッパ。パス手打ちを避けたい被験者には `gse-submit` (最新セッション
//! 自動検出ダブルクリック) を推奨 (decisions D3)。

use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use gse_next_lib::packaging::{is_valid_participant_id, package_session};

fn usage() -> &'static str {
    "usage: gse-package --input <raw.ndjson> --participant <P###> --recipient <age1... | pubkey.txt> [--out <dir>]"
}

/// `--key value` 形式の素朴なパーサ。clap 非依存 (被験者配布バイナリの依存を最小化)。
fn parse_args() -> Result<(PathBuf, String, String, PathBuf), String> {
    let mut input: Option<PathBuf> = None;
    let mut participant: Option<String> = None;
    let mut recipient: Option<String> = None;
    let mut out: Option<PathBuf> = None;
    let mut args = std::env::args().skip(1);
    while let Some(a) = args.next() {
        match a.as_str() {
            "--input" => {
                input = Some(PathBuf::from(
                    args.next().ok_or("--input requires a value")?,
                ))
            }
            "--participant" => {
                participant = Some(args.next().ok_or("--participant requires a value")?)
            }
            "--recipient" => recipient = Some(args.next().ok_or("--recipient requires a value")?),
            "--out" => out = Some(PathBuf::from(args.next().ok_or("--out requires a value")?)),
            "-h" | "--help" => return Err(usage().to_string()),
            other => return Err(format!("unknown arg: {other}\n{}", usage())),
        }
    }
    let input = input.ok_or_else(|| format!("missing --input\n{}", usage()))?;
    let participant = participant.ok_or_else(|| format!("missing --participant\n{}", usage()))?;
    let recipient = recipient.ok_or_else(|| format!("missing --recipient\n{}", usage()))?;
    if !is_valid_participant_id(&participant) {
        return Err(format!(
            "invalid participant id (expect P### etc.): {participant}"
        ));
    }
    let out = out.unwrap_or_else(|| input.parent().map(Path::to_path_buf).unwrap_or_default());
    Ok((input, participant, recipient, out))
}

fn main() -> ExitCode {
    let result = parse_args().and_then(|(input, participant, recipient, out)| {
        package_session(&input, &participant, &recipient, &out)
    });
    match result {
        Ok(r) => {
            let mut o = io::stdout().lock();
            let _ = writeln!(
                o,
                "anonymized {} line(s){}, age-encrypted → {}",
                r.kept,
                if r.skipped > 0 {
                    format!(" ({} unparseable line(s) skipped)", r.skipped)
                } else {
                    String::new()
                },
                r.out_path.display()
            );
            let _ = writeln!(
                o,
                "→ この .age ファイルを研究者の Dropbox File Request に提出してください。"
            );
            ExitCode::SUCCESS
        }
        Err(e) => {
            let _ = writeln!(io::stderr(), "gse-package: {e}");
            ExitCode::from(1)
        }
    }
}
