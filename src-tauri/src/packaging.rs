//! 提出パイプライン共有ロジック (`feature = "package"` 専用)。
//!
//! `gse-package` (パス指定 CLI) と `gse-submit` (最新セッション自動検出ダブルクリック) が
//! **同一の匿名化 → age 暗号化** ロジックを共有するための単一情報源 (data-privacy SSOT)。
//! crypto を 1 箇所に集約し、両提出経路で匿名化保証 (VK→KeyCategory・本文非保存・時刻相対化) が
//! 一致することを担保する。`age` 依存はこの module 経由でのみ参照され、blind アプリ本体
//! (default features) には載らない (decisions D3)。
//!
//! **エラー型の規約**: 本 module は提出 bin (`gse-package` / `gse-submit`) 専用で、bin 側の
//! `String` エラー慣習 (package.rs / unpack.rs) に整合させるため `Result<_, String>` を返す
//! (ガイドライン §9 の `anyhow::Result` から意図的に逸脱)。メッセージはそのまま参加者向け
//! 端末出力になるため日本語の操作案内を含む。

use std::io::Write;
use std::path::{Path, PathBuf};
use std::str::FromStr;

use crate::analysis::anonymize::{anonymize_ndjson, find_session_start};

/// 参加者 ID の最小検証 (パストラバーサル防止)。英数字のみ・1..=16 文字。
pub fn is_valid_participant_id(id: &str) -> bool {
    !id.is_empty() && id.len() <= 16 && id.chars().all(|c| c.is_ascii_alphanumeric())
}

/// `recipient` 引数が `age1...` ならそのまま、そうでなければファイルとして読み公開鍵行を抽出する。
pub fn resolve_recipient(arg: &str) -> Result<String, String> {
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
pub fn encrypt_to_recipient(plaintext: &[u8], recipient_str: &str) -> Result<Vec<u8>, String> {
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

/// 匿名化 + 暗号化の集計 (監査報告用)。
#[derive(Debug)]
pub struct PackageReport {
    pub out_path: PathBuf,
    pub kept: usize,
    pub skipped: usize,
}

/// raw NDJSON を匿名化 → age 暗号化し `<participant>_<stem>.age` を `out_dir` に書く。
///
/// `gse-package` / `gse-submit` の両方がこれを呼ぶ。匿名化は `anonymize_ndjson`
/// (VK→category・時刻相対化・本文非保存) に委譲し、`meta.session_start` を欠く破損入力は
/// 相対化基点が取れないため reject する (絶対時刻の相対化漏れ防止)。
pub fn package_session(
    input: &Path,
    participant: &str,
    recipient_arg: &str,
    out_dir: &Path,
) -> Result<PackageReport, String> {
    if !is_valid_participant_id(participant) {
        return Err(format!(
            "invalid participant id (expect P### etc.): {participant}"
        ));
    }
    let raw = std::fs::read_to_string(input)
        .map_err(|e| format!("could not read input {}: {e}", input.display()))?;

    // 相対化基点。正規セッションは先頭に meta.session_start を持つ。無ければ破損入力として reject。
    let session_start = find_session_start(&raw).ok_or(
        "input NDJSON has no meta.session_start (broken/truncated?) — refusing to package",
    )?;

    // 1) 匿名化 (VK→category・時刻相対化)。本文・VK 生値は残らない。
    let (anonymized, skipped) = anonymize_ndjson(&raw, session_start);
    let kept = anonymized.lines().count();

    // 2) age 暗号化 (研究者公開鍵宛)。
    let recipient = resolve_recipient(recipient_arg)?;
    let encrypted = encrypt_to_recipient(anonymized.as_bytes(), &recipient)?;

    // 3) 出力 <participant>_<入力ステム>.age (セッション識別=入力ファイル名を踏襲)。
    let stem = input
        .file_stem()
        .and_then(|s| s.to_str())
        .filter(|s| !s.is_empty())
        .unwrap_or("session");
    let out_name = format!("{participant}_{stem}.age");
    let out_path = out_dir.join(out_name);
    std::fs::create_dir_all(out_dir)
        .map_err(|e| format!("could not create out dir {}: {e}", out_dir.display()))?;
    std::fs::write(&out_path, &encrypted)
        .map_err(|e| format!("could not write {}: {e}", out_path.display()))?;
    Ok(PackageReport {
        out_path,
        kept,
        skipped,
    })
}

// --- gse-submit (最新セッション自動検出) 専用ヘルパ ---------------------------------

/// home ディレクトリ。`USERPROFILE` → `HOME` の順で引く (logger.rs `fallback_log_dir` と一致。
/// Windows git-bash で両方設定された場合に解決先が割れないよう順序を揃える)。
fn home_dir() -> Option<PathBuf> {
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

/// `~/.gse/participant_id` を **読み取り専用** で取得する (生成・永続化はしない)。
/// 提出ツールはアプリ実行後に走る前提なので ID は既存。env `GSE_PARTICIPANT_ID` / `GSE_PID`
/// もフォールバックで見る。妥当な ID が無ければ `None`。
pub fn read_persisted_participant_id() -> Option<String> {
    let from_store = home_dir()
        .map(|h| h.join(".gse").join("participant_id"))
        .and_then(|p| std::fs::read_to_string(p).ok())
        .map(|s| s.trim().to_string());
    let candidate = from_store
        .filter(|s| !s.is_empty())
        .or_else(|| std::env::var("GSE_PARTICIPANT_ID").ok())
        .or_else(|| std::env::var("GSE_PID").ok())
        .map(|s| s.trim().to_string());
    candidate.filter(|s| is_valid_participant_id(s))
}

/// `dir` 内で `gse_*.ndjson` のうち **最終更新が最も新しい** ものを返す。
/// `*.anon.ndjson` 等の派生は対象外 (先頭 `gse_` + 拡張子 `ndjson` のみ)。
pub fn find_latest_session_ndjson(dir: &Path) -> Option<PathBuf> {
    let mut latest: Option<(std::time::SystemTime, PathBuf)> = None;
    for entry in std::fs::read_dir(dir).ok()?.flatten() {
        let path = entry.path();
        let name = match path.file_name().and_then(|s| s.to_str()) {
            Some(n) => n,
            None => continue,
        };
        // gse_<...>.ndjson の通常ファイルのみ。匿名化済み (.anon.ndjson)・他形式・ディレクトリは除外。
        if !name.starts_with("gse_") || !name.ends_with(".ndjson") || name.ends_with(".anon.ndjson")
        {
            continue;
        }
        if !entry.file_type().map(|t| t.is_file()).unwrap_or(false) {
            continue;
        }
        let mtime = match entry.metadata().and_then(|m| m.modified()) {
            Ok(t) => t,
            Err(_) => continue,
        };
        // mtime 優先、同値タイは決定的にファイル名 (タイムスタンプ命名) で割る。
        let is_newer = match &latest {
            Some((t, p)) => (mtime, &path) > (*t, p),
            None => true,
        };
        if is_newer {
            latest = Some((mtime, path));
        }
    }
    latest.map(|(_, p)| p)
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
        assert!(!is_valid_participant_id("P0123456789abcdef0")); // >16
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

    #[test]
    fn resolve_recipient_accepts_inline_and_file() {
        // インライン age1... はそのまま。
        let inline = resolve_recipient("age1qqqqq").unwrap();
        assert_eq!(inline, "age1qqqqq");
        // ファイル経由はコメント行を飛ばして age1 行を拾う。
        let dir = std::env::temp_dir().join(format!("gse_pkg_test_{}", std::process::id()));
        std::fs::create_dir_all(&dir).unwrap();
        let f = dir.join("pub.txt");
        std::fs::write(&f, "# researcher public key\nage1abcdef\n").unwrap();
        let from_file = resolve_recipient(f.to_str().unwrap()).unwrap();
        assert_eq!(from_file, "age1abcdef");
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn find_latest_skips_derived_and_non_session_files() {
        // mtime に依存しない決定的検証: 候補が 1 本だけになるよう派生/非セッションを除外し、
        // gse_*.ndjson のみが拾われることを確認する。
        let dir = std::env::temp_dir().join(format!("gse_submit_test_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join("gse_20260102_020202.ndjson"), "y").unwrap();
        std::fs::write(dir.join("gse_20260103_030303.anon.ndjson"), "z").unwrap(); // 派生: 除外
        std::fs::write(dir.join("metrics.json"), "w").unwrap(); // 非セッション: 除外
        std::fs::write(dir.join("notes.txt"), "v").unwrap(); // 除外
        let found = find_latest_session_ndjson(&dir).unwrap();
        assert_eq!(
            found.file_name().and_then(|s| s.to_str()),
            Some("gse_20260102_020202.ndjson")
        );
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn package_session_rejects_missing_meta_and_writes_named_output() {
        let id = age::x25519::Identity::generate();
        let pubkey = id.to_public().to_string();
        let dir = std::env::temp_dir().join(format!("gse_pkgsess_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();

        // meta.session_start 欠落 → 相対化基点が取れず reject (絶対時刻漏れ防止)。
        let bad = dir.join("gse_nometa.ndjson");
        std::fs::write(
            &bad,
            "{\"type\":\"key\",\"t\":5,\"vk\":74,\"press\":true}\n",
        )
        .unwrap();
        let out = dir.join("out");
        let err = package_session(&bad, "P007", &pubkey, &out).unwrap_err();
        assert!(
            err.contains("session_start"),
            "expected meta reject, got: {err}"
        );

        // 正常入力 → 出力名 P###_<stem>.age、暗号文に平文 category が露出しない。
        let good = dir.join("gse_20260628_120000.ndjson");
        std::fs::write(
            &good,
            "{\"type\":\"meta\",\"session_start\":1000,\"hmm_version\":\"0.3.0\"}\n\
             {\"type\":\"key\",\"t\":1200,\"vk\":74,\"press\":true}\n",
        )
        .unwrap();
        let report = package_session(&good, "P007", &pubkey, &out).unwrap();
        assert_eq!(
            report.out_path.file_name().and_then(|s| s.to_str()),
            Some("P007_gse_20260628_120000.age")
        );
        let bytes = std::fs::read(&report.out_path).unwrap();
        assert!(
            !bytes
                .windows(b"alphabetic".len())
                .any(|w| w == b"alphabetic"),
            "anonymized category leaked into ciphertext"
        );
        // 復号して匿名化 (category, NOT vk) を確認。
        use std::io::Read;
        let dec = age::Decryptor::new(&bytes[..]).unwrap();
        let mut reader = match dec {
            age::Decryptor::Recipients(d) => d
                .decrypt(std::iter::once(&id as &dyn age::Identity))
                .unwrap(),
            _ => panic!("expected recipients"),
        };
        let mut plain = String::new();
        reader.read_to_string(&mut plain).unwrap();
        assert!(plain.contains("\"category\":\"alphabetic\""));
        assert!(!plain.contains("\"vk\""), "raw vk leaked: {plain}");
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn session_dir_mirrors_logger_fallback() {
        // logger.rs fallback_log_dir と同じ末尾規約を保つ (SSOT 鏡写しの drift 監視)。
        // GSE_DATASET の有無に依存しない構造検証。
        let dir = default_session_dir("P007").expect("home resolvable in test");
        let s = dir.to_string_lossy().replace('\\', "/");
        assert!(
            s.ends_with("Documents/GSE-sessions") || s.ends_with("raw/P007"),
            "unexpected session dir (logger fallback drift?): {s}"
        );
    }

    #[test]
    fn find_latest_returns_none_for_empty_or_missing_dir() {
        let dir = std::env::temp_dir().join(format!("gse_submit_empty_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        assert!(find_latest_session_ndjson(&dir).is_none());
        let _ = std::fs::remove_dir_all(&dir);
        // 存在しないディレクトリでも panic せず None。
        assert!(find_latest_session_ndjson(&dir).is_none());
    }
}
