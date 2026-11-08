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

/// 出力を書く。`force` でなければ、どちらかが既にあれば何も書かずに失敗する（`create_new`）。
fn write_outputs(out: &Path, bytes: &[u8], sha_text: &str, force: bool) -> Result<(), String> {
    let (t, s) = (out.join(TABLE_NAME), out.join(SHA_NAME));
    if !force {
        for p in [&t, &s] {
            if p.exists() {
                return Err(format!(
                    "{} already exists (use --force to overwrite)",
                    p.display()
                ));
            }
        }
    }
    std::fs::create_dir_all(out).map_err(|e| format!("create {}: {e}", out.display()))?;
    let write = |p: &Path, data: &[u8]| -> Result<(), String> {
        let mut o = std::fs::OpenOptions::new();
        o.write(true);
        if force {
            o.create(true).truncate(true);
        } else {
            o.create_new(true);
        }
        o.open(p)
            .and_then(|mut f| f.write_all(data))
            .map_err(|e| format!("write {}: {e}", p.display()))
    };
    write(&t, bytes)?;
    write(&s, sha_text.as_bytes())
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
