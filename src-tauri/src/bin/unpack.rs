//! gse-unpack: 研究者端末で被験者から受領した `P###_<session>.age` を **age 復号** し、
//! 匿名化済み NDJSON (`gse-package` が VK→category 済) を取り出す自己完結 CLI
//! (pilot-pipeline-runbook D-PP1 / transfer-pipeline D1 の鏡像)。
//!
//! `gse-package` (暗号化側) と対称に age **crate** を使い、age CLI への依存を持たない。
//! 本機を含め age CLI 未導入の環境でも `cargo build --features package` だけで end-to-end
//! パイプラインが回る。鍵は `--identity <keyfile>` で **repo 外から**渡す (コミットしない)。
//!
//! 使い方:
//!   # 1) 研究者が鍵ペアを生成 (秘密鍵→ファイル[repo外]・公開鍵→stdout を被験者に配布)
//!   gse-unpack --keygen [--out <keyfile>]
//!   # 2) 受領した .age を復号 (出力は匿名化 NDJSON)
//!   gse-unpack --input <P###_x.age> --identity <keyfile> [--out <dir>]
//!
//! `cargo build --features package --bin gse-unpack` でビルドする (age 依存は default に載せない)。

use age::secrecy::ExposeSecret;
use std::io::{self, Read, Write};
use std::iter;
use std::path::{Path, PathBuf};
use std::process::ExitCode;
use std::str::FromStr;

fn usage() -> &'static str {
    "usage:\n  \
     gse-unpack --input <P###_x.age> --identity <keyfile> [--out <dir>]   (decrypt)\n  \
     gse-unpack --keygen [--out <keyfile>]                                (generate age keypair)"
}

/// 実行モード。decrypt が主、keygen は研究者の鍵ペア作成補助。
enum Mode {
    Decrypt {
        input: PathBuf,
        identity: PathBuf,
        out_dir: PathBuf,
    },
    Keygen {
        out: PathBuf,
    },
}

/// `--key value` 形式の素朴なパーサ (gse-package と同一様式・clap 非依存)。
fn parse_args() -> Result<Mode, String> {
    let mut input: Option<PathBuf> = None;
    let mut identity: Option<PathBuf> = None;
    let mut out: Option<PathBuf> = None;
    let mut keygen = false;
    let mut args = std::env::args().skip(1);
    while let Some(a) = args.next() {
        match a.as_str() {
            "--input" => {
                input = Some(PathBuf::from(
                    args.next().ok_or("--input requires a value")?,
                ))
            }
            "--identity" => {
                identity = Some(PathBuf::from(
                    args.next().ok_or("--identity requires a value")?,
                ))
            }
            "--out" => out = Some(PathBuf::from(args.next().ok_or("--out requires a value")?)),
            "--keygen" => keygen = true,
            "-h" | "--help" => return Err(usage().to_string()),
            other => return Err(format!("unknown arg: {other}\n{}", usage())),
        }
    }

    if keygen {
        if input.is_some() || identity.is_some() {
            return Err(format!(
                "--keygen takes only --out (got --input/--identity)\n{}",
                usage()
            ));
        }
        let out = out.unwrap_or_else(default_identity_path);
        return Ok(Mode::Keygen { out });
    }

    let input = input.ok_or_else(|| format!("missing --input\n{}", usage()))?;
    let identity = identity.ok_or_else(|| format!("missing --identity\n{}", usage()))?;
    // --out 省略時は入力 .age の親。入力がファイル名のみ (parent が "" や None) なら CWD "."
    // にフォールバックする (空 PathBuf だと create_dir_all が失敗するため)。
    let out_dir = out.unwrap_or_else(|| match input.parent() {
        Some(p) if !p.as_os_str().is_empty() => p.to_path_buf(),
        _ => PathBuf::from("."),
    });
    Ok(Mode::Decrypt {
        input,
        identity,
        out_dir,
    })
}

/// 鍵を repo 外に置く既定パス (`~/.gse/age-identity.txt`)。HOME/USERPROFILE が無ければ CWD。
fn default_identity_path() -> PathBuf {
    let base = std::env::var_os("USERPROFILE").or_else(|| std::env::var_os("HOME"));
    match base {
        Some(b) => PathBuf::from(b).join(".gse").join("age-identity.txt"),
        None => PathBuf::from("age-identity.txt"),
    }
}

/// identity ファイルから age 秘密鍵 (`AGE-SECRET-KEY-1...`) 行を 1 本読み出す。
/// age-keygen 形式のコメント行 (`# ...`) は無視する。
fn load_identity(path: &Path) -> Result<age::x25519::Identity, String> {
    let contents = std::fs::read_to_string(path)
        .map_err(|e| format!("could not read identity file {}: {e}", path.display()))?;
    let line = contents
        .lines()
        .map(str::trim)
        .find(|l| l.starts_with("AGE-SECRET-KEY-1"))
        .ok_or_else(|| {
            format!(
                "no 'AGE-SECRET-KEY-1...' line found in identity file {} (is this an age secret key?)",
                path.display()
            )
        })?;
    age::x25519::Identity::from_str(line)
        .map_err(|e| format!("invalid age identity in {}: {e}", path.display()))
}

/// age 暗号塊を研究者の秘密鍵で復号する。passphrase 形式 (Recipients でない) は非対応。
fn decrypt_with_identity(
    encrypted: &[u8],
    identity: &age::x25519::Identity,
) -> Result<Vec<u8>, String> {
    let decryptor =
        age::Decryptor::new(encrypted).map_err(|e| format!("not a valid age file: {e}"))?;
    let mut reader = match decryptor {
        age::Decryptor::Recipients(d) => d
            .decrypt(iter::once(identity as &dyn age::Identity))
            .map_err(|e| format!("age decrypt failed (wrong key?): {e}"))?,
        age::Decryptor::Passphrase(_) => {
            return Err(
                "file is passphrase-encrypted; gse-package produces recipient-encrypted files"
                    .into(),
            )
        }
    };
    let mut out = Vec::new();
    reader
        .read_to_end(&mut out)
        .map_err(|e| format!("age read failed: {e}"))?;
    Ok(out)
}

/// 匿名化後に残ってはならない生フィールド名 (data-privacy ルール1 の禁止集合 + vk)。
/// 匿名化済み NDJSON は `category` のみを持ち、これらは現れない。`"name":` 形式 (フィールド名 +
/// コロン) で照合し、category 値文字列等への誤検知を避ける。
const FORBIDDEN_RAW_FIELDS: &[&str] = &[
    "\"vk\":",
    "\"vk_code\":",
    "\"scan_code\":",
    "\"unicode\":",
    "\"unicode_char\":",
    "\"char\":",
    "\"window_title\":",
];

/// 1 行 (NDJSON) に禁止生フィールドが含まれるか。空白揺れ (`"vk" :`) も拾うため
/// コロン前の空白を除去して照合する。
fn line_has_raw_field(line: &str) -> bool {
    let compact: String = line.chars().filter(|c| !c.is_whitespace()).collect();
    FORBIDDEN_RAW_FIELDS.iter().any(|f| compact.contains(f))
}

/// 復号レポート (監査報告用)。
struct UnpackReport {
    out_path: PathBuf,
    lines: usize,
    vk_leak_lines: usize,
}

fn run_decrypt(input: &Path, identity_path: &Path, out_dir: &Path) -> Result<UnpackReport, String> {
    let identity = load_identity(identity_path)?;
    let encrypted = std::fs::read(input)
        .map_err(|e| format!("could not read input {}: {e}", input.display()))?;
    let plaintext = decrypt_with_identity(&encrypted, &identity)?;

    // 出力は匿名化 NDJSON (gse-package が VK→category 済)。万一の生キー由来フィールド漏れを
    // 件数で監査 (data-privacy ルール1: 平文に raw 値が残らないことの多層防御。内容は出さない)。
    // 単一パスで非空行数と漏れ行数を集計する。
    let text = String::from_utf8(plaintext)
        .map_err(|e| format!("decrypted payload is not valid UTF-8: {e}"))?;
    let mut lines = 0usize;
    let mut vk_leak_lines = 0usize;
    for l in text.lines() {
        if l.trim().is_empty() {
            continue;
        }
        lines += 1;
        if line_has_raw_field(l) {
            vk_leak_lines += 1;
        }
    }

    // 出力名: 入力ステム (.age を剥がす) + .ndjson。セッション識別を踏襲。
    let stem = input
        .file_stem()
        .and_then(|s| s.to_str())
        .filter(|s| !s.is_empty())
        .unwrap_or("session");
    let out_path = out_dir.join(format!("{stem}.ndjson"));
    std::fs::create_dir_all(out_dir)
        .map_err(|e| format!("could not create out dir {}: {e}", out_dir.display()))?;
    std::fs::write(&out_path, text.as_bytes())
        .map_err(|e| format!("could not write {}: {e}", out_path.display()))?;
    Ok(UnpackReport {
        out_path,
        lines,
        vk_leak_lines,
    })
}

fn run_keygen(out: &Path) -> Result<(PathBuf, String), String> {
    if out.exists() {
        return Err(format!(
            "refusing to overwrite existing key file {} (delete it first if intended)",
            out.display()
        ));
    }
    let identity = age::x25519::Identity::generate();
    let pubkey = identity.to_public().to_string();
    // 秘密鍵は **ファイルにのみ** 書き、stdout には出さない。公開鍵のみ stdout に出す。
    let secret = identity.to_string();
    let contents = format!(
        "# age identity for GSE pilot decrypt — KEEP SECRET, do NOT commit to any repo.\n\
         # public key (distribute this to participants as --recipient): {pubkey}\n\
         {}\n",
        secret.expose_secret()
    );
    if let Some(parent) = out.parent() {
        if !parent.as_os_str().is_empty() {
            std::fs::create_dir_all(parent)
                .map_err(|e| format!("could not create key dir {}: {e}", parent.display()))?;
        }
    }
    std::fs::write(out, contents.as_bytes())
        .map_err(|e| format!("could not write key file {}: {e}", out.display()))?;
    restrict_permissions(out);
    Ok((out.to_path_buf(), pubkey))
}

/// 秘密鍵ファイルを所有者のみ読み書き可 (0600) にする (Unix のみ・best effort)。
#[cfg(unix)]
fn restrict_permissions(path: &Path) {
    use std::os::unix::fs::PermissionsExt;
    let _ = std::fs::set_permissions(path, std::fs::Permissions::from_mode(0o600));
}

#[cfg(not(unix))]
fn restrict_permissions(path: &Path) {
    // Windows: ACL の自動設定は行わない。所有者限定アクセスはユーザに委ねる旨を警告する
    // (runbook §2 でも「共有/同期フォルダに置かない」を明記)。
    let _ = writeln!(
        io::stderr(),
        "gse-unpack: NOTE: on Windows the key file's ACL is left at default — restrict it to your \
         user (e.g. icacls \"{}\" /inheritance:r /grant:r \"%USERNAME%:R\") and keep it out of any \
         shared/synced folder.",
        path.display()
    );
}

fn main() -> ExitCode {
    let mode = match parse_args() {
        Ok(m) => m,
        Err(e) => {
            let _ = writeln!(io::stderr(), "gse-unpack: {e}");
            return ExitCode::from(1);
        }
    };
    match mode {
        Mode::Decrypt {
            input,
            identity,
            out_dir,
        } => match run_decrypt(&input, &identity, &out_dir) {
            Ok(r) => {
                let mut o = io::stdout().lock();
                let _ = writeln!(
                    o,
                    "age-decrypted {} line(s) → {}",
                    r.lines,
                    r.out_path.display()
                );
                if r.vk_leak_lines > 0 {
                    // 想定外: 匿名化前の生ログが暗号化されていた可能性。件数のみ警告。
                    let _ = writeln!(
                        io::stderr(),
                        "gse-unpack: WARNING: {} line(s) contain a raw key field (vk/scan_code/\
                         unicode/window_title) — input may not have been anonymized by gse-package. \
                         Do NOT share this NDJSON.",
                        r.vk_leak_lines
                    );
                }
                let _ = writeln!(
                    o,
                    "→ 匿名化 NDJSON です。gse-dataset / repo にコミットせず、sync-session で metrics 化してください。"
                );
                ExitCode::SUCCESS
            }
            Err(e) => {
                let _ = writeln!(io::stderr(), "gse-unpack: {e}");
                ExitCode::from(1)
            }
        },
        Mode::Keygen { out } => match run_keygen(&out) {
            Ok((path, pubkey)) => {
                let mut o = io::stdout().lock();
                let _ = writeln!(o, "age public key (give to participants as --recipient):");
                let _ = writeln!(o, "{pubkey}");
                let _ = writeln!(
                    o,
                    "secret key written to: {} (KEEP SECRET, not in repo)",
                    path.display()
                );
                ExitCode::SUCCESS
            }
            Err(e) => {
                let _ = writeln!(io::stderr(), "gse-unpack: {e}");
                ExitCode::from(1)
            }
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use gse_next_lib::analysis::anonymize::{anonymize_ndjson, find_session_start};

    /// 同梱 gse-package と同じ暗号化ロジック (テスト内に閉じる)。
    fn encrypt_to_recipient(plaintext: &[u8], recipient: &age::x25519::Recipient) -> Vec<u8> {
        let encryptor = age::Encryptor::with_recipients(vec![Box::new(recipient.clone())]).unwrap();
        let mut encrypted = Vec::new();
        let mut writer = encryptor.wrap_output(&mut encrypted).unwrap();
        writer.write_all(plaintext).unwrap();
        writer.finish().unwrap();
        encrypted
    }

    #[test]
    fn keygen_encrypt_decrypt_roundtrip() {
        // keygen で作る形式の identity 文字列を decrypt 側が読み戻せること。
        let id = age::x25519::Identity::generate();
        let pubkey = id.to_public();
        let secret_line = id.to_string();

        let raw = concat!(
            r#"{"type":"meta","session_start":1000000,"hmm_version":"0.3.0"}"#,
            "\n",
            r#"{"type":"key","t":1000200,"vk":74,"press":true}"#,
            "\n",
        );
        let ss = find_session_start(raw).expect("meta session_start");
        let (anonymized, _skipped) = anonymize_ndjson(raw, ss);
        assert!(!anonymized.contains("\"vk\""), "vk leaked pre-encrypt");

        let encrypted = encrypt_to_recipient(anonymized.as_bytes(), &pubkey);

        // identity ファイル形式 (コメント行 + 秘密鍵行) からの読み戻し。
        let id_file = format!(
            "# public key: {}\n{}\n",
            pubkey,
            secret_line.expose_secret()
        );
        let parsed = id_file
            .lines()
            .map(str::trim)
            .find(|l| l.starts_with("AGE-SECRET-KEY-1"))
            .and_then(|l| age::x25519::Identity::from_str(l).ok())
            .expect("identity parse");

        let decrypted = decrypt_with_identity(&encrypted, &parsed).unwrap();
        assert_eq!(String::from_utf8(decrypted).unwrap(), anonymized);
    }

    #[test]
    fn decrypt_with_wrong_key_fails() {
        let right = age::x25519::Identity::generate();
        let wrong = age::x25519::Identity::generate();
        let encrypted = encrypt_to_recipient(b"hello", &right.to_public());
        assert!(decrypt_with_identity(&encrypted, &wrong).is_err());
    }
}
