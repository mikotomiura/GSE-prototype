//! ADR-040 D3 の検査（手跡の背景の層の表現の入力が、記録・提出物・ファイル・ネットワーク・
//! 窓の保存と返送・他の窓・推定へ流れず、列を作らない）。テストだけのモジュール。
//!
//! `.steering/20261021-handmark-stage-pointer/design.md` §3 の表の行ごとに 1 つのテストを置き、
//! どれにも陽性対照を付ける。対照は、実際のファイルの本文の先頭に禁じる語を足した本文を実行時に組み立て、
//! 検査がそれを見つけることを確かめる（禁じる語を検査対象のファイルに書かない）。
//! 文字列の検査は別名の関数を経由した漏れを見つけられない（ADR-040 D3 の「止められないもの」）。

use crate::handmark_stage_pointer::{
    payload_type_name, Forwarder, PointerPayload, Switches, POINTER_EVENT,
};
use crate::input::handmark_pointer::{synthetic_sample, PointerSample, PointerUpdate};
use std::marker::PhantomData;
use std::path::{Path, PathBuf};

/// ポインタの値を扱う Rust のファイル。
const RUST: [(&str, &str); 3] = [
    (
        "input/handmark_pointer.rs",
        include_str!("input/handmark_pointer.rs"),
    ),
    (
        "input/handmark_pointer_macos.rs",
        include_str!("input/handmark_pointer_macos.rs"),
    ),
    (
        "handmark_stage_pointer.rs",
        include_str!("handmark_stage_pointer.rs"),
    ),
];

/// 背景の窓の側のファイル。
const WINDOW: [(&str, &str); 2] = [
    (
        "src/components/HandmarkStage.tsx",
        include_str!("../../src/components/HandmarkStage.tsx"),
    ),
    (
        "src/components/handmarkStageTrace.ts",
        include_str!("../../src/components/handmarkStageTrace.ts"),
    ),
];

/// テストの部分と、行の頭からのコメントを除いた本文。
fn body(src: &str) -> String {
    let head = src.split("#[cfg(test)]").next().unwrap_or(src);
    head.lines()
        .filter(|l| !l.trim_start().starts_with("//"))
        .collect::<Vec<_>>()
        .join("\n")
}

fn hits(src: &str, needles: &[&str]) -> Vec<String> {
    let b = body(src);
    needles
        .iter()
        .filter(|n| b.contains(**n))
        .map(|n| n.to_string())
        .collect()
}

/// どのファイルも語を含まないこと。陽性対照: 各ファイルの先頭に語を 1 つ足した本文では見つかる。
fn assert_clean(row: &str, files: &[(&str, &str)], needles: &[&str]) {
    for (name, src) in files {
        let found = hits(src, needles);
        assert!(found.is_empty(), "{row}: {name} が {found:?} を含む");
        for n in needles {
            let planted = format!("{n}\n{src}");
            assert_eq!(
                hits(&planted, &[n]),
                vec![n.to_string()],
                "{row}: 陽性対照が赤にならない（{name} に {n}）"
            );
        }
    }
}

fn short_name(full: &str) -> &str {
    full.rsplit("::").next().unwrap_or(full)
}

/// ポインタの値の型と payload の型の名前（実行時に得る）。
fn type_names() -> [String; 3] {
    [
        short_name(std::any::type_name::<PointerSample>()).to_string(),
        short_name(std::any::type_name::<PointerUpdate>()).to_string(),
        short_name(payload_type_name()).to_string(),
    ]
}

// ---- 型の層 ----

/// 型が trait を実装しているかを値で得る（実装していれば固有の定数、していなければ trait の定数に解決される）。
struct Probe<T>(PhantomData<T>);
trait Fallback {
    const DEBUG: bool = false;
    const DISPLAY: bool = false;
    const SERIALIZE: bool = false;
}
impl<T> Fallback for Probe<T> {}
impl<T: std::fmt::Debug> Probe<T> {
    const DEBUG: bool = true;
}
impl<T: std::fmt::Display> Probe<T> {
    const DISPLAY: bool = true;
}
impl<T: serde::Serialize> Probe<T> {
    const SERIALIZE: bool = true;
}

// 表現の入力の型が Debug・Display・Serialize を実装すると、コンパイルが通らない。
const _: () = assert!(!Probe::<PointerSample>::DEBUG);
const _: () = assert!(!Probe::<PointerSample>::DISPLAY);
const _: () = assert!(!Probe::<PointerSample>::SERIALIZE);
const _: () = assert!(!Probe::<PointerUpdate>::DEBUG);
const _: () = assert!(!Probe::<PointerUpdate>::DISPLAY);
const _: () = assert!(!Probe::<PointerUpdate>::SERIALIZE);
// 陽性対照: 実装している型では真になる（調べ方が空回りしていない）。
const _: () = assert!(Probe::<f64>::DEBUG && Probe::<f64>::DISPLAY && Probe::<f64>::SERIALIZE);

// ---- NDJSON・applog・tracing ----

#[test]
fn d3_records_the_pointer_files_do_not_touch_the_recorders() {
    assert_clean(
        "記録",
        &RUST,
        &[
            "LogEntry",
            "tracing",
            "log_tx",
            "POINTER_TX",
            "println",
            "eprintln",
            "dbg!",
        ],
    );
    assert_clean("記録", &WINDOW, &["console"]);
}

/// 数を数えるだけの tracing の層。
struct CountLayer(std::sync::Arc<std::sync::atomic::AtomicUsize>);
impl<S: tracing::Subscriber> tracing_subscriber::Layer<S> for CountLayer {
    fn on_event(&self, _e: &tracing::Event<'_>, _c: tracing_subscriber::layer::Context<'_, S>) {
        self.0.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
    }
}

fn spike_dir() -> PathBuf {
    std::env::temp_dir().join("gse-handmark-spike")
}

fn entries(dir: &Path) -> usize {
    std::fs::read_dir(dir).map(|d| d.count()).unwrap_or(0)
}

/// 合成のポインタで配送を 4 秒ぶん回す（送り先は窓へ送るときと同じく JSON にするだけ）。
/// `leak` は陽性対照: 送るたびに applog へ出す・ファイルへ書く偽の実装。
fn run_forwarding(leak_log: bool, leak_file: Option<&Path>) -> (usize, usize) {
    use tracing_subscriber::layer::SubscriberExt;
    let count = std::sync::Arc::new(std::sync::atomic::AtomicUsize::new(0));
    let sub = tracing_subscriber::registry().with(CountLayer(count.clone()));
    let mut sent = 0;
    tracing::subscriber::with_default(sub, || {
        let sw = Switches::new();
        let mut fw = Forwarder::new();
        for k in 0..250u64 {
            if k == 100 {
                sw.set_cursor(false);
            }
            if k == 150 {
                sw.set_cursor(true);
            }
            let mut read = || synthetic_sample(k * 16);
            let mut send = |p: PointerPayload| {
                let json = serde_json::to_string(&p).unwrap_or_default();
                sent += 1;
                if leak_log {
                    tracing::info!("{}", json);
                }
                if let Some(path) = leak_file {
                    let _ = std::fs::write(path.join(format!("leak-{k}")), json);
                }
            };
            fw.tick(&sw, (k * 16) as f64, &mut read, &mut send);
        }
    });
    (count.load(std::sync::atomic::Ordering::Relaxed), sent)
}

#[test]
fn d3_records_forwarding_leaves_no_line_and_no_file() {
    let dir = spike_dir();
    let before = entries(&dir);
    let (lines, sent) = run_forwarding(false, None);
    assert!(sent > 200, "配送が回っていない（{sent}）");
    assert_eq!(lines, 0, "配送で applog の行が出た");
    assert_eq!(entries(&dir), before, "配送で計測のファイルが増えた");
    // 陽性対照: 送るたびに出す・書く偽の実装なら増える
    assert!(run_forwarding(true, None).0 > 0);
    let control = std::env::temp_dir().join(format!("gse-handmark-guard-{}", std::process::id()));
    std::fs::create_dir_all(&control).unwrap();
    run_forwarding(false, Some(&control));
    let written = entries(&control);
    let _ = std::fs::remove_dir_all(&control);
    assert!(written > 0);
}

// ---- 提出物（逆向き） ----

#[test]
fn d3_submission_the_record_side_does_not_know_the_input() {
    let record_side = [
        ("logger.rs", include_str!("logger.rs")),
        ("schema_dto.rs", include_str!("schema_dto.rs")),
        ("submission.rs", include_str!("submission.rs")),
        ("packaging.rs", include_str!("packaging.rs")),
    ];
    let [a, b, c] = type_names();
    let needles = [
        a.as_str(),
        b.as_str(),
        c.as_str(),
        POINTER_EVENT,
        "handmark_pointer",
        "handmark_stage_pointer",
    ];
    assert_clean("提出物", &record_side, &needles);
}

// ---- 計測のファイル・ネットワーク ----

#[test]
fn d3_files_and_network_none_in_the_pointer_files() {
    assert_clean(
        "計測のファイル",
        &RUST,
        &["std::fs", "fs::", "File", "OpenOptions"],
    );
    assert_clean(
        "ネットワーク",
        &RUST,
        &[
            "TcpStream",
            "UdpSocket",
            "std::net",
            "reqwest",
            "ureq",
            "hyper",
        ],
    );
    assert_clean(
        "ネットワーク",
        &WINDOW,
        &[
            "fetch",
            "XMLHttpRequest",
            "WebSocket",
            "EventSource",
            "sendBeacon",
        ],
    );
}

// ---- 窓の保存と返送 ----

#[test]
fn d3_window_does_not_store_or_send_back() {
    assert_clean(
        "窓の保存と返送",
        &WINDOW,
        &[
            "invoke",
            "@tauri-apps/api/core",
            "localStorage",
            "sessionStorage",
            "indexedDB",
            "caches",
            "cookie",
            "postMessage",
            "emit",
        ],
    );
}

// ---- 他の窓への配送 ----

fn walk(dir: &Path, exts: &[&str], out: &mut Vec<PathBuf>) {
    let Ok(rd) = std::fs::read_dir(dir) else {
        return;
    };
    for e in rd.flatten() {
        let p = e.path();
        if p.is_dir() {
            walk(&p, exts, out);
        } else if p
            .extension()
            .and_then(|x| x.to_str())
            .is_some_and(|x| exts.contains(&x))
        {
            out.push(p);
        }
    }
}

/// イベント名を本文（コメントの行を除く）に含む Rust・TS のファイル（この検査のファイルを除く）。
fn files_naming(name: &str) -> Vec<String> {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"));
    let mut files = Vec::new();
    walk(&root.join("src"), &["rs"], &mut files);
    walk(&root.join("../src"), &["ts", "tsx"], &mut files);
    let mut found: Vec<String> = files
        .iter()
        .filter(|p| !p.ends_with("handmark_stage_guard.rs"))
        .filter(|p| {
            std::fs::read_to_string(p)
                .map(|s| body(&s).contains(name))
                .unwrap_or(false)
        })
        .map(|p| {
            p.file_name()
                .map(|f| f.to_string_lossy().to_string())
                .unwrap_or_default()
        })
        .collect();
    found.sort();
    found
}

#[test]
fn d3_delivery_only_the_stage_window_knows_the_event() {
    assert_eq!(
        files_naming(POINTER_EVENT),
        vec![
            "HandmarkStage.tsx".to_string(),
            "handmark_stage_pointer.rs".to_string()
        ],
        "ポインタのイベント名を背景の窓の外のコードが知っている（target なしの listen で届く）"
    );
    // 陽性対照: 探し方が空回りしていない（既にある別の名前なら、それを使うファイルが見つかる）
    assert!(files_naming("handmark-stage-key").len() >= 2);
    // 全部の窓へ流す emit を使わず、背景の窓だけへ送る
    let src = include_str!("handmark_stage_pointer.rs");
    let needle = [".", "emit", "("].concat();
    assert!(hits(src, &[needle.as_str()]).is_empty());
    assert!(body(src).contains("emit_to"));
    assert_eq!(
        hits(&format!("{needle}\n{src}"), &[needle.as_str()]).len(),
        1
    );
}

// ---- 推定 ----

#[test]
fn d3_inference_nothing_reaches_the_estimator() {
    let needles = ["analysis", "engine", "invitation", "p_stuck"];
    assert_clean("推定", &RUST, &needles);
    assert_clean("推定", &WINDOW, &needles);
}

// ---- 列（D4） ----

/// 窓の側で配列・表を作ってよい名前（名前を決めた固定数の枠と、打鍵の時刻・草・粒の決まった数）。
const ALLOWED_LISTS: [&str; 4] = ["presses", "blades", "motes", "ripples"];
const LIST_MAKERS: [&str; 9] = [
    "[]",
    "Array.from",
    "Array(",
    "new Map",
    "new Set",
    "new WeakMap",
    ".push(",
    ".unshift(",
    ".splice(",
];

/// 値を持たない配列の書き方で、許す行（React の useEffect の依存の配列が空であること）。
const ALLOWED_LINES: [&str; 1] = ["}, []);"];

/// 配列・表を作る行のうち、許す名前のどれにも当たらない行。
fn unnamed_lists(src: &str) -> Vec<String> {
    body(src)
        .lines()
        .filter(|l| !ALLOWED_LINES.contains(&l.trim()))
        .filter(|l| LIST_MAKERS.iter().any(|m| l.contains(m)))
        .filter(|l| {
            !ALLOWED_LISTS.iter().any(|a| {
                [" =", ".push(", ": "]
                    .iter()
                    .any(|t| l.contains(&format!("{a}{t}")))
            })
        })
        .map(|l| l.trim().to_string())
        .collect()
}

#[test]
fn d4_lists_only_named_slots() {
    assert_clean(
        "列",
        &RUST,
        &[
            "Vec",
            "VecDeque",
            "HashMap",
            "BTreeMap",
            "HashSet",
            "LinkedList",
            "BinaryHeap",
        ],
    );
    for (name, src) in WINDOW {
        let bad = unnamed_lists(src);
        assert!(
            bad.is_empty(),
            "列: {name} に名前の一覧の外の配列・表: {bad:?}"
        );
        // 陽性対照: 一覧に無い名前で作る行を足すと見つかる
        for maker in LIST_MAKERS {
            let planted = format!("const trail = x{maker}y;\n{src}");
            assert_eq!(
                unnamed_lists(&planted).len(),
                1,
                "列: 対照が赤にならない（{maker}）"
            );
        }
    }
}

// ---- 境界 ----

#[test]
fn d3_boundary_macos_reads_only_the_pointer() {
    let mac = [RUST[1]];
    assert_clean(
        "境界",
        &mac,
        &[
            "modifierFlags",
            "keyCode",
            "CGEvent",
            "addGlobalMonitor",
            "addLocalMonitor",
            "unsafe",
        ],
    );
    let b = body(RUST[1].1);
    assert!(b.contains("mouseLocation") && b.contains("pressedMouseButtons"));
    // 窓の用意・トレイの側はポインタの値の型を知らない
    let [a, b2, c] = type_names();
    assert_clean(
        "境界",
        &[(
            "handmark_stage_spike.rs",
            include_str!("handmark_stage_spike.rs"),
        )],
        &[a.as_str(), b2.as_str(), c.as_str()],
    );
    // O1 の記録の側は表現の入力を知らない
    assert_clean(
        "境界",
        &[
            ("input/observe.rs", include_str!("input/observe.rs")),
            (
                "input/observe_macos.rs",
                include_str!("input/observe_macos.rs"),
            ),
            (
                "analysis/pointer_bin.rs",
                include_str!("analysis/pointer_bin.rs"),
            ),
        ],
        &["handmark_pointer", a.as_str(), b2.as_str()],
    );
}
