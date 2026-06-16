//! gse-cohort — 被験者横断 (cohort) 較正判定 CLI (v0.3 較正スモーク Task E)
//!
//! `gse-replay --calibration ... --json` が出力した **per-被験者 calibration レポート JSON**
//! を gse-dataset ツリーから収集し、`analysis::cohort::cohort_verdict` でコホート全体の
//! Go/Kill/INCONCLUSIVE を判定して JSON を標準出力へ書く。
//!
//! # 使い方
//!
//! ```text
//! gse-cohort <dataset-root>                       # 既定 suffix ".calib.json" を走査
//! gse-cohort <dataset-root> --suffix .metrics.json
//! gse-cohort <dataset-root> --compact             # 1 行 JSON (既定は pretty)
//! ```
//!
//! 走査対象は `<root>/metrics/P*/**` (なければ `<root>/P*/**`)。被験者 ID = `P*` ディレクトリ名。
//! 各被験者ディレクトリ直下〜数階層 (`<os>/` 等) から suffix 一致ファイルを 1 件見つける。
//!
//! # 設計
//! - NDJSON 生ログは走査しない (プライバシー §10)。入力は集計済み calibration レポート JSON のみ。
//! - 凍結純関数 `model_gate`/`measurement_gate` を再利用する `cohort_verdict` を駆動するだけ。
//! - I/O 層 (本バイナリ) と純ロジック (`analysis::cohort`) を分離 (D の replay/calibration_eval と対称)。
//!
//! # 関連
//! - `docs/preregistration-v0.3.md` / `docs/development-guidelines.md` §10
//! - `.steering/20260617-probe-e2e/design.md`

use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use gse_next_lib::analysis::cohort::{cohort_verdict, CohortSubject, SubjectCalibrationView};

/// 走査する被験者数の上限 (リソース暴走防止)。実運用は n=3〜5。
const MAX_SUBJECTS: usize = 256;
/// 1 つの calibration レポート JSON の最大サイズ (集計値のみで小さい)。
const MAX_CALIB_BYTES: u64 = 16 * 1024 * 1024;
/// 被験者ディレクトリ配下を探索する最大深さ (`P*/<os>/file` を許容)。
const MAX_SCAN_DEPTH: usize = 3;
/// 既定の calibration レポートファイル接尾辞。
const DEFAULT_SUFFIX: &str = ".calib.json";

struct Args {
    root: PathBuf,
    suffix: String,
    pretty: bool,
}

fn usage() -> String {
    String::from(
        "gse-cohort — per-被験者 calibration レポートを集約しコホート判定を JSON 出力\n\n\
         USAGE:\n    \
         gse-cohort <dataset-root> [--suffix <s>] [--compact]\n\n\
         OPTIONS:\n    \
         --suffix <s>   収集する calibration レポートの接尾辞 (既定 \".calib.json\")\n    \
         --compact      1 行 JSON で出力 (既定は pretty)\n    \
         -h, --help     このヘルプを表示\n",
    )
}

fn parse_args() -> Result<Args, String> {
    let mut args: Vec<String> = std::env::args().skip(1).collect();
    if args.is_empty() || args.iter().any(|a| a == "-h" || a == "--help") {
        return Err(usage());
    }

    let suffix = if let Some(pos) = args.iter().position(|a| a == "--suffix") {
        if pos + 1 >= args.len() {
            return Err("--suffix requires an argument".to_string());
        }
        let s = args.remove(pos + 1);
        args.remove(pos);
        s
    } else {
        DEFAULT_SUFFIX.to_string()
    };

    let compact = if let Some(pos) = args.iter().position(|a| a == "--compact") {
        args.remove(pos);
        true
    } else {
        false
    };

    if args.len() != 1 {
        return Err(format!(
            "expected exactly 1 positional argument (dataset-root), got {}",
            args.len()
        ));
    }
    let root = PathBuf::from(args.remove(0));

    Ok(Args {
        root,
        suffix,
        pretty: !compact,
    })
}

/// 走査の基点を決める: `<root>/metrics` が **実体ディレクトリ**ならそれ、なければ `<root>`。
///
/// `metrics` が symlink の場合は採用しない (基点 symlink follow による意図しないツリー走査を防ぐ・
/// security MEDIUM)。判定は `symlink_metadata` (リンクを辿らない): symlink は `is_dir()==false` で
/// 既に弾かれるが、意図を明示するため `!is_symlink()` も併記する。
///
/// 限界: Windows の junction (reparse tag が symlink と異なる) は `is_symlink()==false` /
/// `is_dir()==true` となり本ガードでは弾けない。ただし `<root>` 自体はユーザーが明示指定する
/// 信頼ツリーであり (junction を仕込める攻撃者は root を直接渡せる)、本チェックは defense-in-depth。
/// junction の厳密検出 (FILE_ATTRIBUTE_REPARSE_POINT) は本ローカル研究 CLI のスコープ外とする。
fn scan_base(root: &Path) -> PathBuf {
    let metrics = root.join("metrics");
    match fs::symlink_metadata(&metrics) {
        Ok(m) if m.is_dir() && !m.file_type().is_symlink() => metrics,
        _ => root.to_path_buf(),
    }
}

/// 基点直下の被験者ディレクトリ (名前が 'P' で始まる dir) を ID 昇順で返す。シンボリックリンクは除外。
fn find_subject_dirs(base: &Path) -> Result<Vec<(String, PathBuf)>, String> {
    let mut out: Vec<(String, PathBuf)> = Vec::new();
    let entries = fs::read_dir(base).map_err(|e| format!("cannot read {}: {e}", base.display()))?;
    for entry in entries {
        let entry = entry.map_err(|e| format!("dir entry error: {e}"))?;
        let path = entry.path();
        // シンボリックリンクは辿らない (symlink_metadata で実体種別を確認)。
        let meta = fs::symlink_metadata(&path).map_err(|e| format!("stat error: {e}"))?;
        if !meta.is_dir() {
            continue;
        }
        if let Some(name) = path.file_name().and_then(|n| n.to_str()) {
            if name.starts_with('P') {
                out.push((name.to_string(), path));
                // 病理的に多い P* dir を全列挙し切る前に早期 bail (security LOW)。
                if out.len() > MAX_SUBJECTS {
                    return Err(format!("too many subject directories (> {MAX_SUBJECTS})"));
                }
            }
        }
    }
    out.sort_by(|a, b| a.0.cmp(&b.0));
    Ok(out)
}

/// 被験者ディレクトリ配下を深さ制限付きで走査し、suffix 一致ファイルを集める。symlink は辿らない。
fn find_calib_files(dir: &Path, suffix: &str, depth: usize, out: &mut Vec<PathBuf>) {
    if depth > MAX_SCAN_DEPTH {
        return;
    }
    let entries = match fs::read_dir(dir) {
        Ok(e) => e,
        Err(e) => {
            tracing::warn!("skip unreadable dir {}: {}", dir.display(), e);
            return;
        }
    };
    for entry in entries.flatten() {
        let path = entry.path();
        let meta = match fs::symlink_metadata(&path) {
            Ok(m) => m,
            Err(e) => {
                tracing::warn!("skip unstattable {}: {}", path.display(), e);
                continue;
            }
        };
        if meta.file_type().is_symlink() {
            continue;
        }
        if meta.is_dir() {
            find_calib_files(&path, suffix, depth + 1, out);
        } else if meta.is_file() {
            if let Some(name) = path.file_name().and_then(|n| n.to_str()) {
                if name.ends_with(suffix) {
                    out.push(path.clone());
                }
            }
        }
    }
}

/// 1 件の calibration レポート JSON を読み、read-model にパースして `CohortSubject` を作る。
///
/// stat と read を分離すると TOCTOU でサイズ上限を回避されうるため、単一ハンドルから
/// `take(MAX_CALIB_BYTES)` で読み取り量を物理的に上限化する (security MEDIUM)。
/// 上限ちょうど読めた場合は「超過の可能性」としてエラーにする。
fn load_subject(subject_id: &str, path: &Path) -> Result<CohortSubject, String> {
    let file = File::open(path).map_err(|e| format!("cannot open {}: {e}", path.display()))?;
    // +1 まで読もうとし、MAX を超えた分があれば上限超過として弾く。
    let mut reader = file.take(MAX_CALIB_BYTES + 1);
    let mut buf: Vec<u8> = Vec::new();
    reader
        .read_to_end(&mut buf)
        .map_err(|e| format!("cannot read {}: {e}", path.display()))?;
    if buf.len() as u64 > MAX_CALIB_BYTES {
        return Err(format!(
            "{} exceeds size limit ({} bytes)",
            path.display(),
            MAX_CALIB_BYTES
        ));
    }
    let view: SubjectCalibrationView = serde_json::from_slice(&buf)
        .map_err(|e| format!("invalid calibration JSON {}: {e}", path.display()))?;
    Ok(CohortSubject {
        subject_id: subject_id.to_string(),
        view,
    })
}

fn main() -> ExitCode {
    let _ = tracing_subscriber::fmt()
        .with_writer(std::io::stderr)
        .with_max_level(tracing::Level::INFO)
        .try_init();

    let args = match parse_args() {
        Ok(a) => a,
        Err(msg) => {
            let _ = writeln!(std::io::stderr(), "{msg}");
            return ExitCode::from(2);
        }
    };

    if !args.root.is_dir() {
        let _ = writeln!(
            std::io::stderr(),
            "dataset root is not a directory: {}",
            args.root.display()
        );
        return ExitCode::from(2);
    }

    let base = scan_base(&args.root);
    let subject_dirs = match find_subject_dirs(&base) {
        Ok(v) => v,
        Err(e) => {
            let _ = writeln!(std::io::stderr(), "{e}");
            return ExitCode::from(1);
        }
    };

    if subject_dirs.is_empty() {
        let _ = writeln!(
            std::io::stderr(),
            "no subject directories (P*) found under {}",
            base.display()
        );
        return ExitCode::from(1);
    }
    if subject_dirs.len() > MAX_SUBJECTS {
        let _ = writeln!(
            std::io::stderr(),
            "too many subject directories ({} > {})",
            subject_dirs.len(),
            MAX_SUBJECTS
        );
        return ExitCode::from(1);
    }

    let mut subjects: Vec<CohortSubject> = Vec::with_capacity(subject_dirs.len());
    for (id, dir) in &subject_dirs {
        let mut files: Vec<PathBuf> = Vec::new();
        find_calib_files(dir, &args.suffix, 0, &mut files);
        files.sort();
        match files.len() {
            0 => {
                tracing::warn!(
                    "subject {}: no '{}' file under {} → skipped",
                    id,
                    args.suffix,
                    dir.display()
                );
            }
            1 => match load_subject(id, &files[0]) {
                Ok(s) => subjects.push(s),
                Err(e) => {
                    let _ = writeln!(std::io::stderr(), "{e}");
                    return ExitCode::from(1);
                }
            },
            n => {
                tracing::warn!(
                    "subject {}: {} '{}' files found (ambiguous) → skipped",
                    id,
                    n,
                    args.suffix
                );
            }
        }
    }

    if subjects.is_empty() {
        let _ = writeln!(
            std::io::stderr(),
            "no calibration reports ('{}') found under {}",
            args.suffix,
            base.display()
        );
        return ExitCode::from(1);
    }

    tracing::info!("aggregating {} subject report(s)", subjects.len());
    let report = cohort_verdict(&subjects);

    let json = if args.pretty {
        serde_json::to_string_pretty(&report)
    } else {
        serde_json::to_string(&report)
    };
    let json = match json {
        Ok(s) => s,
        Err(e) => {
            let _ = writeln!(std::io::stderr(), "serialization error: {e}");
            return ExitCode::from(1);
        }
    };

    let stdout = std::io::stdout();
    let mut lock = stdout.lock();
    let _ = writeln!(lock, "{json}");
    ExitCode::SUCCESS
}
