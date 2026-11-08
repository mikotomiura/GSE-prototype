//! gse-handmark-table: 手跡（段 1 の後期・ADR-051 D4）の割付の表と SHA-256 を、種から作る研究者の道具。
//!
//! 使い方:
//!   gse-handmark-table --seed <u64> --s1-start-day <i64> --early-min <u32> --early-max <u32> \
//!                      --late-days <u32> --out <dir> [--force]
//!
//! 出力: `<dir>/handmark_assignment.json`（改行で終わる・キーの順は固定）と
//! `<dir>/handmark_assignment.sha256`（`<hex>  handmark_assignment.json\n`）。標準出力に SHA-256 を出す。
//! 既存の表か `.sha256` があれば失敗する（研究の途中で配った表を上書きしない）。`--force` のときだけ上書きする。

use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use gse_next_lib::analysis::handmark::assignment::{generate, sha256_hex, Table};

const TABLE_NAME: &str = "handmark_assignment.json";
const SHA_NAME: &str = "handmark_assignment.sha256";

#[derive(Debug, PartialEq, Eq)]
struct Args {
    seed: u64,
    s1_start_day: i64,
    early_min: u32,
    early_max: u32,
    late_days: u32,
    out: PathBuf,
    force: bool,
}

fn parse_args<I: IntoIterator<Item = String>>(args: I) -> Result<Args, String> {
    let (mut seed, mut start, mut emin, mut emax, mut late, mut out) =
        (None, None, None, None, None, None);
    let mut force = false;
    let mut it = args.into_iter();
    while let Some(a) = it.next() {
        let mut val = |name: &str| it.next().ok_or(format!("{name} requires a value"));
        match a.as_str() {
            "--seed" => {
                seed = Some(
                    val("--seed")?
                        .parse::<u64>()
                        .map_err(|e| format!("--seed: {e}"))?,
                )
            }
            "--s1-start-day" => {
                start = Some(
                    val("--s1-start-day")?
                        .parse::<i64>()
                        .map_err(|e| format!("--s1-start-day: {e}"))?,
                )
            }
            "--early-min" => {
                emin = Some(
                    val("--early-min")?
                        .parse::<u32>()
                        .map_err(|e| format!("--early-min: {e}"))?,
                )
            }
            "--early-max" => {
                emax = Some(
                    val("--early-max")?
                        .parse::<u32>()
                        .map_err(|e| format!("--early-max: {e}"))?,
                )
            }
            "--late-days" => {
                late = Some(
                    val("--late-days")?
                        .parse::<u32>()
                        .map_err(|e| format!("--late-days: {e}"))?,
                )
            }
            "--out" => out = Some(PathBuf::from(val("--out")?)),
            "--force" => force = true,
            other => return Err(format!("unknown argument: {other}")),
        }
    }
    Ok(Args {
        seed: seed.ok_or("--seed is required")?,
        s1_start_day: start.ok_or("--s1-start-day is required")?,
        early_min: emin.ok_or("--early-min is required")?,
        early_max: emax.ok_or("--early-max is required")?,
        late_days: late.ok_or("--late-days is required")?,
        out: out.ok_or("--out is required")?,
        force,
    })
}

/// 表のバイト列と `.sha256` の本文を作る（IO なし）。
fn build(a: &Args) -> Result<(Table, Vec<u8>, String, String), String> {
    let table = generate(
        a.seed,
        a.s1_start_day,
        a.early_min,
        a.early_max,
        a.late_days,
    )?;
    let bytes = table.canonical_bytes();
    let hex = sha256_hex(&bytes);
    let sha_text = format!("{hex}  {TABLE_NAME}\n");
    Ok((table, bytes, hex, sha_text))
}

/// 一時ファイルを作って書き、`sync_all` する（本番の書き込み）。
/// `create_new` なので既存のファイルやリンクを辿らず、truncate もしない。unix では 0600。
fn write_synced(p: &Path, data: &[u8]) -> std::io::Result<()> {
    let mut o = std::fs::OpenOptions::new();
    o.write(true).create_new(true);
    #[cfg(unix)]
    {
        use std::os::unix::fs::OpenOptionsExt;
        o.mode(0o600);
    }
    let mut f = o.open(p)?;
    f.write_all(data)?;
    f.sync_all()
}

/// 一時ファイルを宛先に公開する（本番）。`force` なら `rename`（置き換える）。
/// そうでなければ `hard_link`（宛先がすでにあれば、壊れたリンクでも失敗し、置き換えない）で公開して一時ファイルを消す。
fn publish(tmp: &Path, dest: &Path, force: bool) -> std::io::Result<()> {
    if force {
        std::fs::rename(tmp, dest)
    } else {
        std::fs::hard_link(tmp, dest)?;
        let _ = std::fs::remove_file(tmp);
        Ok(())
    }
}

/// 出力を書く。`force` でなければ、どちらかが既にあれば何も書かずに失敗する。
fn write_outputs(out: &Path, bytes: &[u8], sha_text: &str, force: bool) -> Result<(), String> {
    write_outputs_with(out, bytes, sha_text, force, &write_synced, &publish)
}

/// 実行ごとに一意な一時ファイルの名前（`<名前>.<pid>.<ナノ秒>.tmp`）。
fn unique_tmp(out: &Path, name: &str) -> PathBuf {
    let nanos = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_nanos();
    out.join(format!("{name}.{}.{nanos}.tmp", std::process::id()))
}

/// 両方を自分の一時ファイルに書いてから、表、`.sha256` の順に公開する。途中で失敗したら自分の一時ファイル
/// を消す。`write` と `publish` は差し替えて失敗を注入できる。
///
/// - `--force` なし: 公開は `hard_link`（既存の宛先を置き換えない）。`.sha256` の公開が失敗したら、
///   今回自分が公開した表を消して元に戻す（表も `.sha256` も残らない）。
/// - `--force`: 公開は `rename`。`.sha256` の `rename` だけが失敗すると、新しい表と古い `.sha256` が
///   残りうる。この組み合わせは SHA-256 が合わないので、アプリの門は `sha_mismatch` で閉じる
///   （出さない側に倒れる）。
fn write_outputs_with(
    out: &Path,
    bytes: &[u8],
    sha_text: &str,
    force: bool,
    write: &dyn Fn(&Path, &[u8]) -> std::io::Result<()>,
    publish: &dyn Fn(&Path, &Path, bool) -> std::io::Result<()>,
) -> Result<(), String> {
    let (t, s) = (out.join(TABLE_NAME), out.join(SHA_NAME));
    // 早い失敗のための確かめ（本番の門は hard_link）。壊れたリンクも「ある」とみなす。
    let exists_check = || -> Result<(), String> {
        if !force {
            for p in [&t, &s] {
                if std::fs::symlink_metadata(p).is_ok() {
                    return Err(format!(
                        "{} already exists (use --force to overwrite)",
                        p.display()
                    ));
                }
            }
        }
        Ok(())
    };
    exists_check()?;
    std::fs::create_dir_all(out).map_err(|e| format!("create {}: {e}", out.display()))?;
    let (t_tmp, s_tmp) = (unique_tmp(out, TABLE_NAME), unique_tmp(out, SHA_NAME));
    // 消すのは自分が作った一時ファイルだけ
    let cleanup = |created: &[&Path]| {
        for p in created {
            let _ = std::fs::remove_file(p);
        }
    };
    if let Err(e) = write(&t_tmp, bytes) {
        cleanup(&[&t_tmp]);
        return Err(format!("write {}: {e}", t_tmp.display()));
    }
    if let Err(e) = write(&s_tmp, sha_text.as_bytes()) {
        cleanup(&[&t_tmp, &s_tmp]);
        return Err(format!("write {}: {e}", s_tmp.display()));
    }
    if let Err(e) = publish(&t_tmp, &t, force) {
        cleanup(&[&t_tmp, &s_tmp]);
        return Err(format!("publish {}: {e}", t.display()));
    }
    if let Err(e) = publish(&s_tmp, &s, force) {
        if !force {
            // 今回自分が公開した表だけを消して元に戻す
            let _ = std::fs::remove_file(&t);
        }
        cleanup(&[&t_tmp, &s_tmp]);
        return Err(format!("publish {}: {e}", s.display()));
    }
    Ok(())
}

fn run() -> Result<String, String> {
    let a = parse_args(std::env::args().skip(1))?;
    let (_, bytes, hex, sha_text) = build(&a)?;
    write_outputs(&a.out, &bytes, &sha_text, a.force)?;
    Ok(hex)
}

fn main() -> ExitCode {
    match run() {
        Ok(hex) => {
            let _ = writeln!(std::io::stdout(), "{hex}");
            ExitCode::SUCCESS
        }
        Err(msg) => {
            let _ = writeln!(std::io::stderr(), "gse-handmark-table: {msg}");
            ExitCode::from(1)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use gse_next_lib::analysis::handmark::assignment::{load_from_bytes, TableLoad};

    fn args(seed: u64) -> Args {
        parse_args(
            [
                "--seed",
                &seed.to_string(),
                "--s1-start-day",
                "20400",
                "--early-min",
                "7",
                "--early-max",
                "12",
                "--late-days",
                "15",
                "--out",
                "/tmp/x",
            ]
            .map(String::from),
        )
        .unwrap()
    }

    #[test]
    fn same_args_give_the_same_bytes_and_pass_the_loader() {
        let (_, b1, h1, s1) = build(&args(42)).unwrap();
        let (_, b2, h2, _) = build(&args(42)).unwrap();
        assert_eq!((&b1, &h1), (&b2, &h2));
        assert!(b1.ends_with(b"\n"));
        assert!(s1.ends_with("  handmark_assignment.json\n"));
        assert!(matches!(
            load_from_bytes(Some(&b1), Some(&s1)),
            TableLoad::Ok { .. }
        ));
    }

    #[test]
    fn a_different_seed_changes_the_output() {
        let (_, b1, ..) = build(&args(42)).unwrap();
        assert!((0..20u64).any(|s| build(&args(s)).unwrap().1 != b1));
    }

    #[test]
    fn existing_outputs_are_not_overwritten_without_force() {
        let d = std::env::temp_dir().join(format!("gse-hm-table-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        let (_, b1, _, s1) = build(&args(1)).unwrap();
        let (_, b2, _, s2) = build(&args(2)).unwrap();
        write_outputs(&d, &b1, &s1, false).unwrap();
        // 2 回目は失敗し、中身は 1 回目のまま
        assert!(write_outputs(&d, &b2, &s2, false).is_err());
        assert_eq!(std::fs::read(d.join(TABLE_NAME)).unwrap(), b1);
        // 片方だけ残っていても失敗し、もう片方を作らない
        std::fs::remove_file(d.join(TABLE_NAME)).unwrap();
        assert!(write_outputs(&d, &b2, &s2, false).is_err());
        assert!(!d.join(TABLE_NAME).exists());
        // --force は上書きする
        write_outputs(&d, &b2, &s2, true).unwrap();
        assert_eq!(std::fs::read(d.join(TABLE_NAME)).unwrap(), b2);
        assert_eq!(std::fs::read_to_string(d.join(SHA_NAME)).unwrap(), s2);
        assert!(parse_args(["--force"].map(String::from)).is_err());
        let _ = std::fs::remove_dir_all(&d);
    }

    /// 2 つ目の一時ファイルの書き込みに失敗しても、既存の 2 つのファイルは元のまま・一時ファイルは残らない。
    #[test]
    fn a_failed_second_temp_write_leaves_the_existing_pair_untouched() {
        let d = std::env::temp_dir().join(format!("gse-hm-table-atomic-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        let (_, b1, _, s1) = build(&args(1)).unwrap();
        let (_, b2, _, s2) = build(&args(2)).unwrap();
        write_outputs(&d, &b1, &s1, false).unwrap();
        let calls = std::cell::Cell::new(0);
        let failing = |p: &Path, data: &[u8]| -> std::io::Result<()> {
            calls.set(calls.get() + 1);
            if calls.get() == 2 {
                // 2 つ目で失敗する（途中まで書いた一時ファイルを残す失敗）
                std::fs::write(p, b"partial")?;
                return Err(std::io::Error::other("injected"));
            }
            write_synced(p, data)
        };
        assert!(write_outputs_with(&d, &b2, &s2, true, &failing, &publish).is_err());
        assert_eq!(std::fs::read(d.join(TABLE_NAME)).unwrap(), b1);
        assert_eq!(std::fs::read_to_string(d.join(SHA_NAME)).unwrap(), s1);
        let names: Vec<String> = std::fs::read_dir(&d)
            .unwrap()
            .map(|e| e.unwrap().file_name().to_string_lossy().into_owned())
            .collect();
        assert!(names.iter().all(|n| !n.ends_with(".tmp")), "{names:?}");
        // 1 つ目で失敗しても同じ
        calls.set(1);
        let first_fails =
            |_: &Path, _: &[u8]| -> std::io::Result<()> { Err(std::io::Error::other("injected")) };
        assert!(write_outputs_with(&d, &b2, &s2, true, &first_fails, &publish).is_err());
        assert_eq!(std::fs::read(d.join(TABLE_NAME)).unwrap(), b1);
        let _ = std::fs::remove_dir_all(&d);
    }

    fn tmp_dir(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("gse-hm-table-{tag}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        d
    }

    fn names(d: &Path) -> Vec<String> {
        std::fs::read_dir(d)
            .map(|r| {
                r.map(|e| e.unwrap().file_name().to_string_lossy().into_owned())
                    .collect()
            })
            .unwrap_or_default()
    }

    /// 2 つ目の公開だけを失敗させる（1 つ目は本番の公開）。
    fn sha_publish_fails(tmp: &Path, dest: &Path, force: bool) -> std::io::Result<()> {
        if dest.file_name().is_some_and(|n| n == SHA_NAME) {
            return Err(std::io::Error::other("injected"));
        }
        publish(tmp, dest, force)
    }

    #[test]
    fn without_force_a_failed_second_publish_leaves_neither_file() {
        let d = tmp_dir("pub-noforce");
        let (_, b, _, sha) = build(&args(1)).unwrap();
        let r = write_outputs_with(&d, &b, &sha, false, &write_synced, &sha_publish_fails);
        assert!(r.is_err());
        assert!(names(&d).is_empty(), "{:?}", names(&d));
        let _ = std::fs::remove_dir_all(&d);
    }

    #[test]
    fn with_force_a_failed_second_rename_leaves_a_pair_the_app_rejects() {
        use gse_next_lib::analysis::handmark::assignment::{load_from_bytes, TableLoad};
        let d = tmp_dir("pub-force");
        let (_, b1, _, s1) = build(&args(1)).unwrap();
        let (_, b2, _, s2) = build(&args(2)).unwrap();
        assert_ne!(b1, b2);
        write_outputs(&d, &b1, &s1, false).unwrap();
        let r = write_outputs_with(&d, &b2, &s2, true, &write_synced, &sha_publish_fails);
        assert!(r.is_err());
        // 新しい表と古い .sha256 が残る。門の検めは sha_mismatch（出さない側）
        let t = std::fs::read(d.join(TABLE_NAME)).unwrap();
        let s = std::fs::read_to_string(d.join(SHA_NAME)).unwrap();
        assert_eq!((&t, &s), (&b2, &s1));
        assert_eq!(load_from_bytes(Some(&t), Some(&s)), TableLoad::ShaMismatch);
        assert!(
            names(&d).iter().all(|n| !n.ends_with(".tmp")),
            "{:?}",
            names(&d)
        );
        let _ = std::fs::remove_dir_all(&d);
    }

    #[test]
    fn temp_names_are_unique_per_call_and_never_follow_existing_files() {
        let d = tmp_dir("uniq");
        std::fs::create_dir_all(&d).unwrap();
        let a = unique_tmp(&d, TABLE_NAME);
        std::thread::sleep(std::time::Duration::from_millis(1));
        let b = unique_tmp(&d, TABLE_NAME);
        assert_ne!(a, b);
        assert!(a.to_string_lossy().ends_with(".tmp"));
        // create_new: 既にあれば失敗し、中身を変えない
        std::fs::write(&a, b"keep").unwrap();
        assert!(write_synced(&a, b"x").is_err());
        assert_eq!(std::fs::read(&a).unwrap(), b"keep");
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            write_synced(&b, b"x").unwrap();
            assert_eq!(
                std::fs::metadata(&b).unwrap().permissions().mode() & 0o777,
                0o600
            );
        }
        let _ = std::fs::remove_dir_all(&d);
    }

    /// 宛先に壊れたシンボリックリンクがあれば、`--force` なしでは失敗して何も書かない。
    #[cfg(unix)]
    #[test]
    fn a_dangling_symlink_at_the_destination_blocks_without_force() {
        let (_, b, _, sha) = build(&args(1)).unwrap();
        for victim in [TABLE_NAME, SHA_NAME] {
            let d = tmp_dir("dangling");
            std::fs::create_dir_all(&d).unwrap();
            let target = d.join("elsewhere");
            std::os::unix::fs::symlink(&target, d.join(victim)).unwrap();
            assert!(write_outputs(&d, &b, &sha, false).is_err(), "{victim}");
            assert!(!target.exists(), "リンク先を作ってはいけない");
            assert!(names(&d).iter().all(|n| !n.ends_with(".tmp")));
            let other = if victim == TABLE_NAME {
                SHA_NAME
            } else {
                TABLE_NAME
            };
            assert!(std::fs::symlink_metadata(d.join(other)).is_err());
            let _ = std::fs::remove_dir_all(&d);
        }
        // 事前の確かめを通り抜けても、本番の公開（hard_link）が置き換えない
        let d = tmp_dir("dangling-link");
        std::fs::create_dir_all(&d).unwrap();
        let tmp = d.join("src.tmp");
        std::fs::write(&tmp, b"x").unwrap();
        let dest = d.join("dest");
        let target = d.join("elsewhere");
        std::os::unix::fs::symlink(&target, &dest).unwrap();
        assert!(publish(&tmp, &dest, false).is_err());
        assert!(!target.exists());
        let _ = std::fs::remove_dir_all(&d);
    }

    #[test]
    fn bad_args_are_rejected() {
        assert!(parse_args(["--seed", "x"].map(String::from)).is_err());
        assert!(parse_args(["--bogus"].map(String::from)).is_err());
        assert!(parse_args(Vec::<String>::new()).is_err());
        let mut a = args(1);
        a.early_min = 9;
        a.early_max = 3;
        assert!(build(&a).is_err());
    }
}
