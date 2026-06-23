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

use std::io::{self, Write};
use std::path::{Path, PathBuf};
use std::process::ExitCode;
use std::str::FromStr;

use gse_next_lib::analysis::anonymize::{anonymize_ndjson, find_session_start};

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

/// 参加者 ID の最小検証 (パストラバーサル防止)。英数字のみ・1..=16 文字。
fn is_valid_participant_id(id: &str) -> bool {
    !id.is_empty() && id.len() <= 16 && id.chars().all(|c| c.is_ascii_alphanumeric())
}

/// `--recipient` が `age1...` ならそのまま、そうでなければファイルとして読む。
fn resolve_recipient(arg: &str) -> Result<String, String> {
    let trimmed = arg.trim();
    if trimmed.starts_with("age1") {
        return Ok(trimmed.to_string());
    }
    let contents = std::fs::read_to_string(arg)
        .map_err(|e| format!("could not read recipient file {arg}: {e}"))?;
    let key = contents
        .lines()
        .map(str::trim)
        .find(|l| l.starts_with("age1"))
        .ok_or_else(|| format!("no 'age1...' public key found in {arg}"))?;
    Ok(key.to_string())
}

/// 平文を研究者の age 公開鍵 (X25519) 宛に暗号化する。
fn encrypt_to_recipient(plaintext: &[u8], recipient_str: &str) -> Result<Vec<u8>, String> {
    let recipient = age::x25519::Recipient::from_str(recipient_str)
        .map_err(|e| format!("invalid age recipient public key: {e}"))?;
    let encryptor = age::Encryptor::with_recipients(vec![Box::new(recipient)])
        .ok_or("no recipients provided")?;
    let mut encrypted = Vec::new();
    let mut writer = encryptor
        .wrap_output(&mut encrypted)
        .map_err(|e| format!("age wrap_output failed: {e}"))?;
    writer
        .write_all(plaintext)
        .map_err(|e| format!("age write failed: {e}"))?;
    writer
        .finish()
        .map_err(|e| format!("age finish failed: {e}"))?;
    Ok(encrypted)
}

/// 出力パスと匿名化の集計 (監査報告用)。
struct PackageReport {
    out_path: PathBuf,
    kept: usize,
    skipped: usize,
}

fn run() -> Result<PackageReport, String> {
    let (input, participant, recipient_arg, out_dir) = parse_args()?;
    let raw = std::fs::read_to_string(&input)
        .map_err(|e| format!("could not read input {}: {e}", input.display()))?;

    // 相対化基点。正規セッションは先頭に meta.session_start を持つ。無ければ破損入力として reject
    // (silent fallback=0 で絶対時刻が相対化漏れするのを防ぐ)。
    let session_start = find_session_start(&raw).ok_or(
        "input NDJSON has no meta.session_start (broken/truncated?) — refusing to package",
    )?;

    // 1) 匿名化 (VK→category・時刻相対化)。本文・VK 生値は残らない。
    let (anonymized, skipped) = anonymize_ndjson(&raw, session_start);
    let kept = anonymized.lines().count();

    // 2) age 暗号化 (研究者公開鍵宛)。
    let recipient = resolve_recipient(&recipient_arg)?;
    let encrypted = encrypt_to_recipient(anonymized.as_bytes(), &recipient)?;

    // 3) 出力 P###_<入力ステム>.age (セッション識別=入力ファイル名を踏襲)。
    let stem = input
        .file_stem()
        .and_then(|s| s.to_str())
        .filter(|s| !s.is_empty())
        .unwrap_or("session");
    let out_name = format!("{participant}_{stem}.age");
    let out_path = out_dir.join(out_name);
    std::fs::create_dir_all(&out_dir)
        .map_err(|e| format!("could not create out dir {}: {e}", out_dir.display()))?;
    std::fs::write(&out_path, &encrypted)
        .map_err(|e| format!("could not write {}: {e}", out_path.display()))?;
    Ok(PackageReport {
        out_path,
        kept,
        skipped,
    })
}

fn main() -> ExitCode {
    match run() {
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

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Read;

    #[test]
    fn participant_id_validation() {
        assert!(is_valid_participant_id("P003"));
        assert!(is_valid_participant_id("P000"));
        assert!(!is_valid_participant_id("../etc"));
        assert!(!is_valid_participant_id("P 3"));
        assert!(!is_valid_participant_id(""));
    }

    #[test]
    fn encrypt_decrypt_roundtrip_and_anonymized_payload() {
        // テスト用 age 鍵ペアを生成 (本番は研究者が生成・公開鍵のみ配布)。
        let id = age::x25519::Identity::generate();
        let pubkey = id.to_public().to_string();

        let raw = concat!(
            r#"{"type":"meta","session_start":1000000,"hmm_version":"0.3.0"}"#,
            "\n",
            r#"{"type":"key","t":1000200,"vk":74,"press":true}"#,
            "\n",
        );
        let ss = find_session_start(raw).expect("meta session_start");
        let (anonymized, _skipped) = anonymize_ndjson(raw, ss);
        // 暗号化前の匿名化ペイロードに VK 生値が無いこと。
        assert!(!anonymized.contains("\"vk\""), "vk leaked: {anonymized}");
        assert!(anonymized.contains("\"category\":\"alphabetic\""));

        let encrypted = encrypt_to_recipient(anonymized.as_bytes(), &pubkey).unwrap();
        // 暗号塊に平文 category 文字列が露出しないこと。
        assert!(!encrypted
            .windows(b"alphabetic".len())
            .any(|w| w == b"alphabetic"));

        // 研究者の秘密鍵でのみ復号でき、匿名化ペイロードに一致すること。
        let decryptor = age::Decryptor::new(&encrypted[..]).unwrap();
        let mut reader = match decryptor {
            age::Decryptor::Recipients(d) => d
                .decrypt(std::iter::once(&id as &dyn age::Identity))
                .unwrap(),
            _ => panic!("expected recipients decryptor"),
        };
        let mut decrypted = Vec::new();
        reader.read_to_end(&mut decrypted).unwrap();
        assert_eq!(String::from_utf8(decrypted).unwrap(), anonymized);
    }
}
