//! 手跡の記録の検査（ADR-050 D3 のうち打鍵だけの PR 1 に当たる行・試作 `handmark_stage_guard.rs` の考え方）。
//! テストだけのモジュール。
//!
//! 見るもの: (1) 打鍵の列を状態と日の累計に流しても、生じる `LogEntry` が `HandmarkDay` だけ、
//! (2) `handmark_day` の型に打鍵の時刻・キー・風の値の欄が無い、(3) 新しいファイルの本文に記録の口
//! （`LogEntry::` の `HandmarkDay` 以外の腕）が出ない。語の検査には陽性対照を付ける
//! （対照の文字列は実行時に連結して作る。禁じる語をこのファイルに書かない）。
//! 文字列の検査は別名の関数を経由した漏れを見つけられない。

use crate::analysis::handmark::state::replay;
use crate::handmark_store::testfs::with_table;
use crate::handmark_store::Evaluation;
use crate::logger::LogEntry;

/// 新しく足したファイルの本文（このファイル自身は含めない）。
const FILES: [(&str, &str); 13] = [
    (
        "analysis/handmark/mod.rs",
        include_str!("analysis/handmark/mod.rs"),
    ),
    (
        "analysis/handmark/state.rs",
        include_str!("analysis/handmark/state.rs"),
    ),
    (
        "analysis/handmark/assignment.rs",
        include_str!("analysis/handmark/assignment.rs"),
    ),
    (
        "analysis/handmark/day.rs",
        include_str!("analysis/handmark/day.rs"),
    ),
    (
        "analysis/handmark/gate.rs",
        include_str!("analysis/handmark/gate.rs"),
    ),
    ("handmark_store.rs", include_str!("handmark_store.rs")),
    ("handmark_driver.rs", include_str!("handmark_driver.rs")),
    ("handmark_stage.rs", include_str!("handmark_stage.rs")),
    // ★ 添字 0..=7 は上の検査（`FILES[5]`）が使うので、足すときは必ず末尾に足す。
    // ポインタ（PR 3・ADR-050 D3）。macOS の読み `input/handmark_pointer_macos.rs` は末尾（`pointer_files` の
    // 範囲に入る）。窓の TS は別の一覧（`WINDOW`）。
    (
        "analysis/handmark/trace.rs",
        include_str!("analysis/handmark/trace.rs"),
    ),
    (
        "analysis/handmark/trace_replay.rs",
        include_str!("analysis/handmark/trace_replay.rs"),
    ),
    (
        "input/handmark_pointer.rs",
        include_str!("input/handmark_pointer.rs"),
    ),
    (
        "handmark_pointer_thread.rs",
        include_str!("handmark_pointer_thread.rs"),
    ),
    (
        "input/handmark_pointer_macos.rs",
        include_str!("input/handmark_pointer_macos.rs"),
    ),
];

/// `FILES` のうちポインタの本文のファイル（末尾の 5 つ）。
fn pointer_files() -> &'static [(&'static str, &'static str)] {
    &FILES[8..]
}
const BIN: &str = include_str!("bin/gse-handmark-table.rs");

/// `LogEntry::` の後ろの名前が `HandmarkDay` 以外の出現を返す。
fn log_entry_violations(text: &str) -> Vec<String> {
    let needle = format!("{}{}", "LogEntry", "::");
    text.match_indices(&needle)
        .filter_map(|(i, _)| {
            let rest = &text[i + needle.len()..];
            let name: String = rest
                .chars()
                .take_while(|c| c.is_ascii_alphanumeric() || *c == '_')
                .collect();
            (name != "HandmarkDay").then_some(name)
        })
        .collect()
}

#[test]
fn new_files_open_no_recording_channel_but_handmark_day() {
    for (name, body) in FILES
        .iter()
        .copied()
        .chain([("bin/gse-handmark-table.rs", BIN)])
    {
        assert!(
            log_entry_violations(body).is_empty(),
            "{name}: {:?}",
            log_entry_violations(body)
        );
    }
}

#[test]
fn the_word_check_is_red_on_a_planted_word() {
    // 陽性対照: 実際のファイルの本文に、実行時に連結した禁じる語を足すと検査が赤になる
    let planted = format!(
        "{}\nfn x() {{ let _ = {}{}Key {{ }}; }}",
        FILES[5].1, "LogEntry", "::"
    );
    assert_eq!(log_entry_violations(&planted), vec!["Key".to_string()]);
    // 許す腕だけなら赤にならない
    let ok = format!("{}{}HandmarkDay(row)", "LogEntry", "::");
    assert!(log_entry_violations(&ok).is_empty());
}

/// 1 日分の打鍵を駆動役に流し(`new` → `tick` の列 → `turn_off` → `turn_on` → `on_quit`)、
/// 出た出来事のうち記録に向かうものが `Row`(= `handmark_day`)だけであることを、駆動役の出口で見る。
#[test]
fn a_day_of_typing_through_the_driver_produces_only_handmark_day_rows() {
    use crate::handmark_driver::{Destination, Effect, HandmarkDriver};
    let fs = with_table();
    let day = 20_411;
    let t0 = 1_800_000_000_000u64;
    let (mut d, mut all) = HandmarkDriver::new(&fs, true, t0, day);
    let mut moved = false;
    for i in 1..3_000u64 {
        d.on_press(t0 + i * 120);
        all.extend(d.tick(&fs, t0 + i * 250, day));
    }
    all.extend(d.turn_off(&fs, t0 + 800_000));
    all.extend(d.turn_on(&fs, t0 + 801_000));
    all.extend(d.on_quit(&fs, t0 + 802_000));
    for e in &all {
        if let Effect::State(s) = e {
            moved |= s.speed > 0.0;
        }
    }
    assert!(moved, "手跡が動いていない（検査が空回り）");
    let mut rows = 0;
    for e in &all {
        // 行き先の網羅は `destination()` の match が保つ。記録へ向かうのは Row だけ。
        if e.destination() == Destination::Log {
            let Effect::Row(r) = e else {
                panic!("記録へ向かうのが Row 以外: {e:?}");
            };
            let entry = LogEntry::HandmarkDay(r.clone());
            assert_eq!(entry.line_type(), Some("handmark_day"));
            rows += 1;
        }
    }
    assert!(rows >= 4, "{rows}");
    // 状態は打鍵の時刻だけの純関数(再生しても同じ)
    let times: Vec<u64> = (1..3_000u64).map(|i| t0 + i * 120).collect();
    assert_eq!(
        replay(&times, 5, t0, t0 + 300_000).bits(),
        replay(&times, 5, t0, t0 + 300_000).bits()
    );
}

/// `handmark_day` の型（スキーマ）の項目名が設計の一覧と一致し、打鍵・キー・風の欄が無い。
#[test]
fn the_handmark_day_schema_has_exactly_the_designed_fields() {
    let schema = schemars::schema_for!(crate::schema_dto::LogEntryDto);
    let v = serde_json::to_value(&schema).unwrap();
    let variants = v["oneOf"].as_array().expect("oneOf");
    let hm = variants
        .iter()
        .find(|e| e["properties"]["type"]["enum"][0] == "handmark_day")
        .expect("handmark_day variant");
    let mut got: Vec<&str> = hm["properties"]
        .as_object()
        .unwrap()
        .keys()
        .map(String::as_str)
        .collect();
    got.sort_unstable();
    let mut want = vec![
        "type",
        "t",
        "day",
        "assigned",
        "late_start_day",
        "first_shown_day",
        "shown_ms",
        "visible_ms",
        "toggles",
        "input_toggles",
        "stage_starts",
        "overflow",
        "table_sha256",
        "draw_seed",
        "reason",
    ];
    want.sort_unstable();
    assert_eq!(got, want);
    for banned in [
        "speed", "irreg", "phase", "drift", "key", "vk", "category", "press",
    ] {
        assert!(!got.contains(&banned), "{banned}");
    }
    // 実際に書く行のキーも同じ
    let row = with_table();
    let line = Evaluation::run(&row, true, 20_411, None).row(1).unwrap();
    let text = crate::logger::format_handmark_day_line_for_test(&line);
    let obj: serde_json::Value = serde_json::from_str(&text).unwrap();
    let mut keys: Vec<&str> = obj
        .as_object()
        .unwrap()
        .keys()
        .map(String::as_str)
        .collect();
    keys.sort_unstable();
    assert_eq!(keys, want);
}

/// スキーマの定義 `name` の中の `enum` の文字列をすべて集める。
fn schema_enum(name: &str) -> Vec<String> {
    let schema = schemars::schema_for!(crate::schema_dto::LogEntryDto);
    let v = serde_json::to_value(&schema).unwrap();
    fn walk(v: &serde_json::Value, out: &mut Vec<String>) {
        match v {
            serde_json::Value::Object(m) => {
                if let Some(a) = m.get("enum").and_then(|e| e.as_array()) {
                    out.extend(a.iter().filter_map(|x| x.as_str().map(String::from)));
                }
                m.values().for_each(|x| walk(x, out));
            }
            serde_json::Value::Array(a) => a.iter().for_each(|x| walk(x, out)),
            _ => {}
        }
    }
    let mut out = Vec::new();
    walk(&v["definitions"][name], &mut out);
    out.sort();
    out
}

/// 理由・割付の値の 3 つの真実源（Rust の列挙・logger の許す値・スキーマの enum）が一致する。
#[test]
fn reasons_and_assigned_values_agree_across_enum_logger_and_schema() {
    use crate::analysis::handmark::assignment::Assigned;
    use crate::analysis::handmark::gate::CloseReason;
    let mut reasons: Vec<String> = CloseReason::ALL
        .iter()
        .map(|r| r.as_str().to_string())
        .collect();
    reasons.sort();
    assert_eq!(reasons, schema_enum("HandmarkReasonDto"));
    let mut assigned: Vec<String> = Assigned::ALL
        .iter()
        .map(|a| a.as_str().to_string())
        .collect();
    assigned.push("unknown".into());
    assigned.sort();
    let mut logger: Vec<String> = crate::logger::HANDMARK_ASSIGNED_VALUES
        .iter()
        .map(|s| s.to_string())
        .collect();
    logger.sort();
    assert_eq!(assigned, logger);
    assert_eq!(assigned, schema_enum("HandmarkAssignedDto"));
}

// ====================================================================================
// ポインタ（手跡の PR 3・ADR-050 D3 の 3 層）
//
// 試作 `handmark_stage_guard.rs` の考え方: 型で縛り・ソースの語で縛り・振る舞いで縛る。語の検査には
// 陽性対照（実際の本文に禁じる語を実行時に足すと赤になる）を付ける。この検査ファイル自身は走査の
// 対象でないので、禁じる語を検査の一覧に書いてよい。文字列の検査は別名の関数を経由した漏れを見つけられない。
// ====================================================================================

use crate::analysis::handmark::trace::{Point, RipplePoint, Step, TraceField, TraceState};
use crate::handmark_pointer_thread::{Gate, PointerDriver, PointerOut};
use crate::input::handmark_pointer::PointerSample;
use std::marker::PhantomData;

/// 識別子の字か。
fn ident(c: Option<&u8>) -> bool {
    c.is_some_and(|c| c.is_ascii_alphanumeric() || *c == b'_')
}

/// `i` からコメント・文字列・文字・raw 文字列が始まるなら、その後ろの位置を返す（閉じていなければ末尾）。
fn skip_lexeme(b: &[u8], i: usize) -> Option<usize> {
    let at = |k: usize| b.get(k).copied();
    match b[i] {
        b'/' if at(i + 1) == Some(b'/') => Some(
            b[i..]
                .iter()
                .position(|c| *c == b'\n')
                .map_or(b.len(), |k| i + k),
        ),
        b'/' if at(i + 1) == Some(b'*') => {
            let (mut depth, mut j) = (1usize, i + 2);
            while j < b.len() && depth > 0 {
                if b[j] == b'/' && at(j + 1) == Some(b'*') {
                    depth += 1;
                    j += 2;
                } else if b[j] == b'*' && at(j + 1) == Some(b'/') {
                    depth -= 1;
                    j += 2;
                } else {
                    j += 1;
                }
            }
            Some(j)
        }
        b'"' => {
            let mut j = i + 1;
            while j < b.len() {
                match b[j] {
                    b'\\' => j += 2,
                    b'"' => return Some(j + 1),
                    _ => j += 1,
                }
            }
            Some(b.len())
        }
        b'r' if !ident(i.checked_sub(1).and_then(|k| b.get(k)))
            || (i >= 1 && b[i - 1] == b'b' && !ident(i.checked_sub(2).and_then(|k| b.get(k)))) =>
        {
            let hashes = b[i + 1..].iter().take_while(|c| **c == b'#').count();
            if at(i + 1 + hashes) != Some(b'"') {
                return None;
            }
            let mut j = i + 2 + hashes;
            while j < b.len() {
                if b[j] == b'"'
                    && b[j + 1..]
                        .iter()
                        .take(hashes)
                        .filter(|c| **c == b'#')
                        .count()
                        == hashes
                {
                    return Some(j + 1 + hashes);
                }
                j += 1;
            }
            Some(b.len())
        }
        b'\'' if at(i + 1) == Some(b'\\') => Some(
            b[i + 2..]
                .iter()
                .position(|c| *c == b'\'')
                .map_or(b.len(), |k| i + 3 + k),
        ),
        // 1 バイトの文字（`'{'` など）。それ以外の `'` は寿命の印か多バイトの字で、括弧にならない。
        b'\'' if at(i + 2) == Some(b'\'') => Some(i + 3),
        _ => None,
    }
}

/// `j` から始まる項目の終わり（`;` か、対応する `}` の後ろ）。閉じていなければ `None`。
fn item_end(b: &[u8], mut j: usize) -> Option<usize> {
    let mut depth = 0usize;
    while j < b.len() {
        if let Some(n) = skip_lexeme(b, j) {
            j = n;
            continue;
        }
        match b[j] {
            b';' if depth == 0 => return Some(j + 1),
            b'{' | b'(' | b'[' => depth += 1,
            b'}' | b')' | b']' => {
                depth = depth.checked_sub(1)?;
                if depth == 0 && b[j] == b'}' {
                    return Some(j + 1);
                }
            }
            _ => {}
        }
        j += 1;
    }
    None
}

/// `#[cfg(test)]` の付いた項目だけを除く（後ろの本番のコードは残す）。コメント・文字列・文字の中の
/// 属性や括弧は数えない。閉じていない項目は外さない（外しすぎない）。
fn strip_test_items(src: &str) -> String {
    const ATTR: &str = "#[cfg(test)]";
    let b = src.as_bytes();
    let mut out = String::with_capacity(src.len());
    let (mut i, mut from) = (0usize, 0usize);
    while i < b.len() {
        if let Some(n) = skip_lexeme(b, i) {
            i = n;
            continue;
        }
        if b[i..].starts_with(ATTR.as_bytes()) {
            if let Some(e) = item_end(b, i + ATTR.len()) {
                out.push_str(&src[from..i]);
                i = e;
                from = e;
                continue;
            }
            i += ATTR.len();
            continue;
        }
        i += 1;
    }
    out.push_str(&src[from..]);
    out
}

/// テストの項目と、行の頭からのコメントを除いた本文。
fn body(src: &str) -> String {
    strip_test_items(src)
        .lines()
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

/// どのファイルも語を含まないこと。陽性対照: 各ファイルの先頭に語を 1 つ足した本文（実行時に連結）では見つかる。
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

/// 記録の側が知ってはならないポインタの型の名前（型から実行時に得る・改名すれば検査が追従する）。
fn pointer_type_names() -> [String; 7] {
    [
        short_name(std::any::type_name::<PointerSample>()).to_string(),
        short_name(std::any::type_name::<TraceState>()).to_string(),
        short_name(std::any::type_name::<TraceField>()).to_string(),
        short_name(std::any::type_name::<RipplePoint>()).to_string(),
        short_name(std::any::type_name::<PointerOut>()).to_string(),
        short_name(std::any::type_name::<Point>()).to_string(),
        short_name(std::any::type_name::<Step>()).to_string(),
    ]
}

/// `src` の本文（コメント・テストを除く）が識別子 `name` を、識別子の単位で（`Point` が `PointerGate` や
/// `Points` に当たらないように）含むか。
fn contains_ident(src: &str, name: &str) -> bool {
    let b = body(src);
    let bytes = b.as_bytes();
    b.match_indices(name).any(|(i, _)| {
        let before = i.checked_sub(1).and_then(|k| bytes.get(k));
        !ident(before) && !ident(bytes.get(i + name.len()))
    })
}

/// どのファイルも識別子を（識別子の単位で）含まないこと。陽性対照: 先頭に識別子を足せば見つかり、
/// 識別子の一部（前後に字を付けた語）では見つからない。
fn assert_clean_idents(row: &str, files: &[(&str, &str)], names: &[&str]) {
    for (file, src) in files {
        for n in names {
            assert!(!contains_ident(src, n), "{row}: {file} が識別子 {n} を含む");
            assert!(
                contains_ident(&format!("let _ = {n};\n{src}"), n),
                "{row}: 陽性対照が赤にならない（{file} に {n}）"
            );
            assert!(
                !contains_ident(&format!("let _ = {n}s; let _ = x{n};\n{src}"), n)
                    || contains_ident(src, n),
                "{row}: 識別子の単位で見ていない（{n}）"
            );
        }
    }
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

/// 型が `Debug`・`Display`・`Serialize` を実装すると、テストのビルドが止まる。
macro_rules! assert_not_printable {
    ($($t:ty),+ $(,)?) => {$(
        const _: () = assert!(!Probe::<$t>::DEBUG);
        const _: () = assert!(!Probe::<$t>::DISPLAY);
        const _: () = assert!(!Probe::<$t>::SERIALIZE);
    )+};
}
assert_not_printable!(
    PointerSample,
    Point,
    Step,
    TraceState,
    TraceField,
    RipplePoint,
    PointerOut,
);
// 陽性対照: 実装している型では真になる（調べ方が空回りしていない）。
const _: () = assert!(Probe::<f64>::DEBUG && Probe::<f64>::DISPLAY && Probe::<f64>::SERIALIZE);
const _: () =
    assert!(Probe::<String>::DEBUG && Probe::<String>::DISPLAY && Probe::<String>::SERIALIZE);

// ---- ソースの層 ----

#[test]
fn pointer_files_do_not_touch_the_recorders_files_network_or_the_estimator() {
    let files = pointer_files();
    assert_eq!(files.len(), 5);
    // 記録・ログ・ファイル・ネットワーク・推定のどれも呼ばない。
    assert_clean(
        "ポインタの本文",
        files,
        &[
            "LogEntry",
            "log_tx",
            "tracing",
            "info!(",
            "warn!(",
            "debug!(",
            "error!(",
            "trace!(",
            "println",
            "eprintln",
            "dbg!",
            "std::fs",
            "fs::",
            "OpenOptions",
            "applog",
            "File",
            "std::net",
            "reqwest",
            "TcpStream",
            "crate::logger",
            "crate::analysis::engine",
            "features",
            "intervention",
            "invitation",
            "p_stuck",
        ],
    );
}

/// 逆向き: 記録の側（行・schema・提出・パッケージ）がポインタの値の型を知らない。
#[test]
fn the_record_side_does_not_know_the_pointer_types() {
    let record_side = [
        ("logger.rs", include_str!("logger.rs")),
        ("schema_dto.rs", include_str!("schema_dto.rs")),
        ("submission.rs", include_str!("submission.rs")),
        ("packaging.rs", include_str!("packaging.rs")),
        ("applog.rs", include_str!("applog.rs")),
        ("redaction.rs", include_str!("redaction.rs")),
        ("handmark_driver.rs", include_str!("handmark_driver.rs")),
        ("handmark_store.rs", include_str!("handmark_store.rs")),
        ("o1.rs", include_str!("o1.rs")),
    ];
    let names = pointer_type_names();
    let needles: Vec<&str> = names.iter().map(String::as_str).collect();
    assert_eq!(needles.len(), 7);
    assert_clean_idents("提出物", &record_side, &needles);
}

// ---- macOS の読みの境界 ----

/// `NSEvent::` の後ろの名前の一覧（本文のみ）。
fn nsevent_reads(src: &str) -> Vec<String> {
    let b = body(src);
    let needle = format!("{}{}", "NSEvent", "::");
    b.match_indices(&needle)
        .map(|(i, _)| {
            b[i + needle.len()..]
                .chars()
                .take_while(|c| c.is_ascii_alphanumeric() || *c == '_')
                .collect()
        })
        .collect()
}

/// macOS の読みは、いまの位置と押しているボタンだけを読む。キーボードの状態・フック・監視を持たない。
#[test]
fn the_macos_read_touches_only_the_pointer() {
    let mac = FILES[12];
    assert_eq!(mac.0, "input/handmark_pointer_macos.rs");
    assert_clean(
        "macOS の読み",
        &[mac],
        &[
            "modifierFlags",
            "keyCode",
            "keyState",
            "CGEventSource",
            "CGEvent",
            "addGlobalMonitor",
            "addLocalMonitor",
            "unsafe",
        ],
    );
    let reads = nsevent_reads(mac.1);
    assert!(
        reads.iter().any(|r| r == "mouseLocation")
            && reads.iter().any(|r| r == "pressedMouseButtons"),
        "読みが無い（検査が空回り）: {reads:?}"
    );
    for r in &reads {
        assert!(
            r == "mouseLocation" || r == "pressedMouseButtons",
            "NSEvent の読みが 2 つ以外: {r}"
        );
    }
    // 陽性対照: 本文の先頭に別の NSEvent の読みを実行時に足すと見つかる
    let planted = format!("let _ = {}{}{}();\n{}", "NSEvent", "::", "keyCode", mac.1);
    assert!(nsevent_reads(&planted).iter().any(|r| r == "keyCode"));
}

/// macOS の読み（`handmark_pointer_macos::read`）と箱への写し（`to_point`）を呼べるのは、`lib.rs`（スレッドの
/// 配線）・`handmark_pointer_thread.rs`・定義のファイルだけ。他のファイルがポインタを読み始めないことを保つ。
#[test]
fn only_lib_and_the_pointer_thread_read_the_pointer() {
    let files = rs_sources();
    let names = [
        "handmark_pointer_macos::",
        "handmark_pointer::to_point",
        "to_point(",
    ];
    let allowed = [
        "lib.rs",
        "handmark_pointer_thread.rs",
        "input/handmark_pointer.rs",
        "input/handmark_pointer_macos.rs",
    ];
    assert_eq!(
        rs_files_naming(&names, &allowed, &files),
        Vec::<String>::new()
    );
    // 許したファイルのうち lib.rs は本当に使っている（探し方が空回りしていない）。
    let lib = files.iter().find(|(n, _)| n == "lib.rs").expect("lib.rs");
    assert!(names.iter().any(|w| body(&lib.1).contains(w)));
    // 陽性対照: 他のファイルが書いたら見つかる（実行時に連結して作る）。
    for w in names {
        let mut planted = files.clone();
        planted.push((
            "planted.rs".to_string(),
            format!("fn f() {{ let _ = {w}; }}"),
        ));
        assert_eq!(
            rs_files_naming(&names, &allowed, &planted),
            vec!["planted.rs".to_string()],
            "対照が赤にならない（{w}）"
        );
    }
}

// ---- 窓の TS（PR 3・ADR-050 D3・D4） ----

/// 窓の側の本文（手跡の窓だけがポインタのイベントを受ける）。描画の純関数（`handmarkStageDraw.ts`・手跡の PR 4）も
/// 窓の側として同じ検査を受ける（机上の道具も同じ関数を呼ぶ）。
const WINDOW: [(&str, &str); 3] = [
    (
        "HandmarkStage.tsx",
        include_str!("../../src/components/HandmarkStage.tsx"),
    ),
    (
        "handmarkStageTrace.ts",
        include_str!("../../src/components/handmarkStageTrace.ts"),
    ),
    (
        "handmarkStageDraw.ts",
        include_str!("../../src/components/handmarkStageDraw.ts"),
    ),
];

/// 帯の窓の側の本文（ADR-051・手跡の下の縁の帯）。背景の窓と同じ検査を受ける。
/// 帯のイベント（`handmark-strip-near`・`handmark-strip-visible`）を知ってよい TS はこの 2 ファイルだけ。
const STRIP_WINDOW: [(&str, &str); 2] = [
    (
        "HandmarkEdgeStrip.tsx",
        include_str!("../../src/components/HandmarkEdgeStrip.tsx"),
    ),
    (
        "handmarkStripFrame.ts",
        include_str!("../../src/components/handmarkStripFrame.ts"),
    ),
];

/// 窓の TS に現れてはならない語（保存・送信・返送・ネットワーク）。
const WINDOW_BANNED: [&str; 14] = [
    "localStorage",
    "sessionStorage",
    "indexedDB",
    "invoke",
    "@tauri-apps/api/core",
    "fetch",
    "WebSocket",
    "XMLHttpRequest",
    "EventSource",
    "sendBeacon",
    "postMessage",
    "cookie",
    "caches",
    "console",
];

/// 窓は何も保存せず、何も返さず、外へ送らない。
#[test]
fn the_window_does_not_store_send_back_or_talk_to_the_network() {
    assert_clean("窓", &WINDOW, &WINDOW_BANNED);
}

/// 帯の窓も同じ（保存・返送・外への送りが無い。推定の語も受け取らない）。
#[test]
fn the_strip_window_does_not_store_send_back_or_talk_to_the_network() {
    assert_clean("帯の窓", &STRIP_WINDOW, &WINDOW_BANNED);
    // 推定（engine・invitation・p_stuck・level）の語を窓の TS に持ち込まない。
    assert_clean(
        "帯の窓の推定",
        &STRIP_WINDOW,
        &["p_stuck", "invitation", "pStuck", "engine"],
    );
}

/// 窓の側のコードとして走査する拡張子。
const TS_EXTS: [&str; 5] = ["ts", "tsx", "js", "jsx", "mjs"];

/// `src/` の `.ts`・`.tsx`・`.js`・`.jsx`・`.mjs` と、直下の `index.html`（名前, 本文）。
fn ts_sources() -> Vec<(String, String)> {
    fn walk_ts(dir: &std::path::Path, out: &mut Vec<(String, String)>) {
        let Ok(rd) = std::fs::read_dir(dir) else {
            return;
        };
        for e in rd.flatten() {
            let p = e.path();
            if p.is_dir() {
                walk_ts(&p, out);
            } else if p
                .extension()
                .and_then(|x| x.to_str())
                .is_some_and(|x| TS_EXTS.contains(&x))
            {
                if let Ok(text) = std::fs::read_to_string(&p) {
                    let name = p
                        .file_name()
                        .map(|f| f.to_string_lossy().to_string())
                        .unwrap_or_default();
                    out.push((name, text));
                }
            }
        }
    }
    let mut out = Vec::new();
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../src");
    walk_ts(&root, &mut out);
    let index = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../index.html");
    if let Ok(text) = std::fs::read_to_string(&index) {
        out.push(("index.html".to_string(), text));
    }
    out
}

/// イベント名を本文（コメントの行を除く）に含むファイルの名前（手跡の窓の 2 ファイルを除く）。
fn others_naming(name: &str, files: &[(String, String)]) -> Vec<String> {
    ts_files_naming_except(name, files, &WINDOW)
}

/// イベント名を本文に含むファイルの名前（`allowed` の窓のファイルを除く）。
fn ts_files_naming_except(
    name: &str,
    files: &[(String, String)],
    allowed: &[(&str, &str)],
) -> Vec<String> {
    files
        .iter()
        .filter(|(n, _)| !allowed.iter().any(|(w, _)| w == n))
        .filter(|(n, text)| {
            if n.ends_with(".html") {
                // HTML は Rust の字句の読みに通さない（アポストロフィで崩れる）。コメントも含めて見る。
                text.contains(name)
            } else {
                body(text).contains(name)
            }
        })
        .map(|(n, _)| n.clone())
        .collect()
}

/// 場と波紋のイベント名は手跡の窓だけが知る（`target` なしの `listen` で他の窓に届かないように）。
#[test]
fn only_the_stage_window_knows_the_trace_and_ripple_events() {
    let files = ts_sources();
    assert!(files.len() > 5, "src/ の走査が空回り: {}", files.len());
    // 走査の対象: index.html を読んでいる・拡張子の一覧に js 系を含む。
    assert!(
        files.iter().any(|(n, _)| n == "index.html"),
        "index.html を走査していない"
    );
    for ext in ["js", "jsx", "mjs"] {
        assert!(TS_EXTS.contains(&ext), "{ext} を走査しない");
    }
    for name in [stage_event("TRACE_EVENT"), stage_event("RIPPLE_EVENT")] {
        let name = name.as_str();
        assert!(
            others_naming(name, &files).is_empty(),
            "{name} を手跡の窓の外のコードが知っている: {:?}",
            others_naming(name, &files)
        );
        // 手跡の窓は実際に聞いている（探し方が空回りしていない）
        assert!(
            body(WINDOW[0].1).contains(name),
            "{name} を HandmarkStage.tsx が聞いていない"
        );
        // 陽性対照: 他のファイルが名前を書いたら見つかる（拡張子ごと・HTML も）
        for planted_name in [
            "Planted.tsx",
            "planted.js",
            "planted.jsx",
            "planted.mjs",
            "planted.html",
        ] {
            let mut planted = files.clone();
            planted.push((planted_name.to_string(), format!("listen('{name}')")));
            assert_eq!(
                others_naming(name, &planted),
                vec![planted_name.to_string()],
                "対照が赤にならない（{planted_name}）"
            );
        }
    }
}

/// `handmark_stage.rs` の `pub const <name>: &str = "...";` の値をソースから読む。
/// `handmark_stage` は macOS だけのモジュールなので、Windows でも走るこの検査は定数を参照せずにソースを読む
/// （2026-11-09 の CI で、定数を参照して Windows のビルドが止まった）。
fn stage_event(name: &str) -> String {
    let src = include_str!("handmark_stage.rs");
    let head = format!("pub const {name}: &str = \"");
    let line = src
        .lines()
        .find(|l| l.trim_start().starts_with(&head))
        .unwrap_or_else(|| panic!("{name} が handmark_stage.rs に無い"));
    let rest = &line.trim_start()[head.len()..];
    let v = &rest[..rest.find('"').expect("閉じない文字列")];
    assert!(v.starts_with("handmark-"), "{name} の値が想定外: {v}");
    v.to_string()
}

/// `src-tauri/src/` の Rust の本文（相対パス, 本文）。
fn rs_sources() -> Vec<(String, String)> {
    fn walk_rs(root: &std::path::Path, dir: &std::path::Path, out: &mut Vec<(String, String)>) {
        let Ok(rd) = std::fs::read_dir(dir) else {
            return;
        };
        for e in rd.flatten() {
            let p = e.path();
            if p.is_dir() {
                walk_rs(root, &p, out);
            } else if p.extension().and_then(|x| x.to_str()) == Some("rs") {
                if let Ok(text) = std::fs::read_to_string(&p) {
                    let rel = p
                        .strip_prefix(root)
                        // 区切りを `/` にそろえる（Windows では `\` になり、許可の一覧と合わない・2026-11-09 の CI）
                        .map(|r| r.to_string_lossy().replace('\\', "/"))
                        .unwrap_or_default();
                    out.push((rel, text));
                }
            }
        }
    }
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("src");
    let mut out = Vec::new();
    walk_rs(&root, &root, &mut out);
    out
}

/// `needles` のどれかを本文（コメント・テストを除く）に含む Rust のファイル（`allowed` と、この検査自身を除く）。
fn rs_files_naming(needles: &[&str], allowed: &[&str], files: &[(String, String)]) -> Vec<String> {
    files
        .iter()
        .filter(|(n, _)| n != "handmark_guard.rs" && !allowed.contains(&n.as_str()))
        .filter(|(_, text)| {
            let b = body(text);
            needles.iter().any(|w| b.contains(*w))
        })
        .map(|(n, _)| n.clone())
        .collect()
}

/// 場・波紋のイベント名（定数名と文字列）を参照するのは `handmark_stage.rs` だけ。全窓から聞く `listen_any` は使わない。
#[test]
fn only_the_stage_rs_names_the_events_and_nobody_uses_listen_any() {
    let files = rs_sources();
    assert!(
        files.len() > 30,
        "src-tauri/src の走査が空回り: {}",
        files.len()
    );
    assert!(files.iter().any(|(n, _)| n == "handmark_stage.rs"));
    let (trace, ripple) = (stage_event("TRACE_EVENT"), stage_event("RIPPLE_EVENT"));
    let events = [
        "TRACE_EVENT",
        "RIPPLE_EVENT",
        trace.as_str(),
        ripple.as_str(),
    ];
    assert_eq!(
        rs_files_naming(&events, &["handmark_stage.rs"], &files),
        Vec::<String>::new()
    );
    let listen_any = ["listen", "_any"].concat();
    assert_eq!(
        rs_files_naming(&[listen_any.as_str()], &[], &files),
        Vec::<String>::new()
    );
    // 陽性対照: 他のファイルが書いたら見つかる（実行時に連結して作り、この検査自身に語を残さない）。
    for w in events.iter().copied().chain([listen_any.as_str()]) {
        let mut planted = files.clone();
        planted.push((
            "planted.rs".to_string(),
            format!("fn f() {{ let _ = \"{w}\"; {w}; }}"),
        ));
        assert_eq!(
            rs_files_naming(&[w], &["handmark_stage.rs"], &planted),
            vec!["planted.rs".to_string()],
            "対照が赤にならない（{w}）"
        );
    }
    // 陽性対照 2: 許したファイル（handmark_stage.rs）は本当にその名前を使っている（探し方が空回りしていない）。
    let stage = files
        .iter()
        .find(|(n, _)| n == "handmark_stage.rs")
        .expect("stage");
    assert!(body(&stage.1).contains("TRACE_EVENT") && body(&stage.1).contains("RIPPLE_EVENT"));
}

/// 窓へ送る口（`emit_trace`・`emit_ripple`）と画面の大きさ（`screen_size_pt`）を呼べるのは `lib.rs`
/// （ポインタのスレッドの配線）と `handmark_stage.rs`（定義）だけ。
#[test]
fn only_lib_and_the_stage_call_the_emit_and_screen_size_functions() {
    let files = rs_sources();
    let names = ["emit_trace", "emit_ripple", "screen_size_pt"];
    assert_eq!(
        rs_files_naming(&names, &["lib.rs", "handmark_stage.rs"], &files),
        Vec::<String>::new()
    );
    // 許したファイルは本当に使っている（空回りしていない）。
    for allowed in ["lib.rs", "handmark_stage.rs"] {
        let f = files.iter().find(|(n, _)| n == allowed).expect(allowed);
        assert!(
            names.iter().any(|w| body(&f.1).contains(w)),
            "{allowed} が使っていない"
        );
    }
    // 陽性対照
    for w in names {
        let mut planted = files.clone();
        planted.push(("planted.rs".to_string(), format!("fn f() {{ {w}(); }}")));
        assert_eq!(
            rs_files_naming(&names, &["lib.rs", "handmark_stage.rs"], &planted),
            vec!["planted.rs".to_string()]
        );
    }
}

/// 送りは手跡の窓だけへ（`emit_to`）。全窓へ流す `emit` を使わない。
#[test]
fn the_stage_emits_only_to_its_own_window() {
    let src = FILES[7].1;
    assert_eq!(FILES[7].0, "handmark_stage.rs");
    let all = [".", "emit", "("].concat();
    assert!(hits(src, &[all.as_str()]).is_empty());
    assert!(body(src).contains("emit_to"));
    assert_eq!(hits(&format!("{all}\n{src}"), &[all.as_str()]).len(), 1);
}

/// 窓の側で配列・表を作ってよい名前（名前を決めた固定数の枠: 草・粒・波紋・場の 3 本の配列）。
const ALLOWED_LISTS: [&str; 6] = ["blades", "motes", "ripples", "bend", "pullX", "pullY"];
const LIST_MAKERS: [&str; 18] = [
    "[]",
    "Array.from",
    "Array(",
    "new Float32Array",
    "new Array",
    ".concat(",
    "[...",
    "new Map",
    "new Set",
    "new WeakMap",
    ".push(",
    ".unshift(",
    ".splice(",
    // 新しい列を返す書き方（写し・並べ替え・選び出し・生成）。
    ".map(",
    ".slice(",
    ".filter(",
    "Array.of",
    "structuredClone",
];
/// 値を持たない配列の書き方で、許す行（React の useEffect の依存の配列が空であること）。
const ALLOWED_LINES: [&str; 1] = ["}, []);"];

/// `new` の後ろが、大文字で始まり `Array` で終わる語（型付き配列の全部: `Int8Array`・`Uint8Array`・`Float64Array`・
/// `BigInt64Array` など）。一覧に 1 つずつ足すと漏れるので、形で拾う。
fn has_typed_array_ctor(line: &str) -> bool {
    line.match_indices("new ").any(|(i, _)| {
        let word: String = line[i + 4..]
            .trim_start()
            .chars()
            .take_while(|c| c.is_ascii_alphanumeric() || *c == '_')
            .collect();
        word.starts_with(|c: char| c.is_ascii_uppercase()) && word.ends_with("Array")
    })
}

/// 列・表を作る書き方を含む行。
fn makes_list(line: &str) -> bool {
    LIST_MAKERS.iter().any(|m| line.contains(m)) || has_typed_array_ctor(line)
}

/// 配列・表を作る行のうち、許す名前のどれにも当たらない行。
fn unnamed_lists(src: &str) -> Vec<String> {
    body(src)
        .lines()
        .filter(|l| !ALLOWED_LINES.contains(&l.trim()))
        .filter(|l| makes_list(l))
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

/// 窓の側の列は、名前を許した枠だけ（位置・押下の列を作らない）。
#[test]
fn the_window_lists_only_named_slots() {
    for (name, src) in WINDOW.into_iter().chain(STRIP_WINDOW) {
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
        // 陽性対照: 型付き配列は名前に依らず、形で拾う（一覧に無い型も）。
        for ctor in [
            "Int8Array",
            "Uint8Array",
            "Uint8ClampedArray",
            "Int16Array",
            "Uint16Array",
            "Int32Array",
            "Uint32Array",
            "Float64Array",
            "BigInt64Array",
            "BigUint64Array",
        ] {
            let planted = format!("const trail = new {ctor}(64);\n{src}");
            assert_eq!(
                unnamed_lists(&planted).len(),
                1,
                "列: 型付き配列の対照が赤にならない（{ctor}）"
            );
        }
        // 陽性対照 2: 許した名前の枠なら通る（探し方が過剰でない）
        let named = format!("const blades = x[];\n{src}");
        assert!(unnamed_lists(&named).is_empty());
    }
}

// ---- 列（D4） ----

/// `struct name { ... }` の定義の本文（波括弧の対応で切る）。タプル構造体・無い名前は `None`。
fn struct_def(src: &str, name: &str) -> Option<String> {
    let b = body(src);
    let head = format!("struct {name} {{");
    let start = b.find(&head)? + head.len() - 1;
    let end = item_end(b.as_bytes(), start)?;
    Some(b[start..end].to_string())
}

const COLUMN_TYPES: [&str; 4] = ["Vec", "VecDeque", "HashMap", "BTreeMap"];

fn column_hits(def: &str) -> Vec<&'static str> {
    // 識別子の単位で見る（`Vec` が `VecDeque` に当たらないように）。
    let words: Vec<&str> = def
        .split(|c: char| !(c.is_ascii_alphanumeric() || c == '_'))
        .collect();
    COLUMN_TYPES
        .iter()
        .copied()
        .filter(|t| words.contains(t))
        .collect()
}

/// 場・駆動役・（あれば）読みの構造体は、固定長の値だけを持ち、列を持たない。
#[test]
fn the_pointer_structs_hold_no_columns() {
    let owners: [(&str, &str, &str); 2] = [
        (
            "TraceField",
            "analysis/handmark/trace.rs",
            include_str!("analysis/handmark/trace.rs"),
        ),
        (
            "PointerDriver",
            "handmark_pointer_thread.rs",
            include_str!("handmark_pointer_thread.rs"),
        ),
    ];
    for (name, file, src) in owners {
        let def = struct_def(src, name).unwrap_or_else(|| panic!("{file} に struct {name} が無い"));
        assert!(
            def.contains("cells") || def.contains("field"),
            "{name}: 定義を取り違えた"
        );
        assert!(
            column_hits(&def).is_empty(),
            "{name} が列を持つ: {:?}",
            column_hits(&def)
        );
        // 陽性対照: 定義に列の欄を実行時に足すと見つかる。
        for t in COLUMN_TYPES {
            let planted = src.replacen(
                &format!("struct {name} {{"),
                &format!("struct {name} {{\n    trail: {t}<u8>,"),
                1,
            );
            let def = struct_def(&planted, name).expect("planted def");
            assert_eq!(
                column_hits(&def),
                vec![t],
                "{name}: 対照が赤にならない（{t}）"
            );
        }
    }
    // 読みの構造体（`PointerReader`）は、作ったときに列を持たないことを縛る（今は無い）。
    for (file, src) in pointer_files() {
        if let Some(def) = struct_def(src, "PointerReader") {
            assert!(
                column_hits(&def).is_empty(),
                "{file}: PointerReader が列を持つ"
            );
        }
    }
}

// ---- 振る舞いの層 ----

/// 記録へ向かう腕を持たないことを、網羅の match で縛る（`PointerOut` に腕を足すとここで必ず止まる）。
fn pointer_out_goes_to_the_log(o: &PointerOut) -> bool {
    match o {
        PointerOut::Trace(_) => false,
        PointerOut::Ripple(_) => false,
        PointerOut::StripNear(_) => false,
    }
}

/// 1 日分の打鍵と、ポインタの入れ切りを駆動役に通し、同じ時間に `PointerDriver` にも合成の一点を通す。
/// 記録へ向かう出来事は `HandmarkDay` の行だけ（駆動役の出口と `PointerOut` の両方）。
#[test]
fn a_day_of_typing_and_pointer_toggles_produces_only_handmark_day_rows() {
    use crate::analysis::handmark::day::PointerInput;
    use crate::analysis::handmark::trace_replay::synth_points;
    use crate::analysis::pointer_bin::PointerBin;
    use crate::handmark_driver::{Destination, Effect, HandmarkDriver};

    let fs = with_table();
    let day = 20_411;
    let t0 = 1_800_000_000_000u64;
    let bins: Vec<PointerBin> = (1..=900u64)
        .map(|k| PointerBin {
            timestamp: t0 + k * 1_000,
            moved: (k % 7) as u8 + 1,
            buttons: (k % 4) as u8,
            wheel: 0,
        })
        .collect();
    let mut pts = synth_points(&bins, 9, t0, t0 + 900_000).into_iter();

    let (mut d, mut fx_all) = HandmarkDriver::new(&fs, true, t0, day);
    let mut gate = Gate {
        open: false,
        cursor: true,
        click: true,
    };
    let absorb = |fx: &[Effect], gate: &mut Gate| {
        for e in fx {
            if let Effect::PointerGate {
                open,
                cursor,
                click,
            } = e
            {
                *gate = Gate {
                    open: *open,
                    cursor: *cursor,
                    click: *click,
                };
            }
        }
    };
    absorb(&fx_all, &mut gate);
    let mut p = PointerDriver::new();
    let (mut traces, mut ripples) = (0usize, 0usize);
    let (mut saw_cursor_off, mut saw_click_off, mut saw_closed_after_open) = (false, false, false);
    let mut was_open = false;
    let mut now = t0;
    let mut i = 0u64;
    while now < t0 + 600_000 {
        now += 16;
        i += 1;
        let mut read = || pts.next();
        for o in p.tick(now, gate, false, &mut read) {
            assert!(!pointer_out_goes_to_the_log(&o));
            match o {
                PointerOut::Trace(_) => traces += 1,
                PointerOut::Ripple(_) => ripples += 1,
                PointerOut::StripNear(_) => {}
            }
        }
        if i.is_multiple_of(16) {
            d.on_press(now - 40);
            let fx = d.tick(&fs, now, day);
            absorb(&fx, &mut gate);
            fx_all.extend(fx);
        }
        let fx = match i {
            6_000 => d.set_input(&fs, PointerInput::Cursor, false, now),
            9_000 => d.set_input(&fs, PointerInput::Cursor, true, now),
            12_000 => d.set_input(&fs, PointerInput::Click, false, now),
            15_000 => d.set_input(&fs, PointerInput::Click, true, now),
            20_000 => d.turn_off(&fs, now),
            22_000 => d.turn_on(&fs, now),
            _ => Vec::new(),
        };
        absorb(&fx, &mut gate);
        fx_all.extend(fx);
        saw_cursor_off |= gate.open && !gate.cursor;
        saw_click_off |= gate.open && !gate.click;
        saw_closed_after_open |= was_open && !gate.open;
        was_open |= gate.open;
    }
    fx_all.extend(d.on_quit(&fs, now));
    assert!(
        traces > 50 && ripples > 0,
        "合成の一点が通っていない（検査が空回り）: {traces} {ripples}"
    );
    assert!(saw_cursor_off && saw_click_off && saw_closed_after_open);
    let mut rows = 0;
    let mut gates = 0;
    for e in &fx_all {
        if matches!(e, Effect::PointerGate { .. }) {
            gates += 1;
            assert_eq!(e.destination(), Destination::Window);
        }
        if e.destination() == Destination::Log {
            let Effect::Row(r) = e else {
                panic!("記録へ向かうのが Row 以外: {e:?}");
            };
            let entry = LogEntry::HandmarkDay(r.clone());
            assert_eq!(entry.line_type(), Some("handmark_day"));
            rows += 1;
        }
    }
    assert!(rows >= 6 && gates >= 6, "rows={rows} gates={gates}");
}

/// 行に入る入れ切りの要素は時刻・入力の種類・入れたかの 3 つだけで、入力の種類は固定の 2 語。
#[test]
fn input_toggles_in_the_row_carry_only_time_kind_and_side() {
    use crate::analysis::handmark::day::PointerInput;
    use crate::handmark_store::{turn_input_off, turn_input_on};
    let fs = with_table();
    let mut ev = Evaluation::run(&fs, true, 20_411, None);
    turn_input_off(&fs, &mut ev, PointerInput::Cursor, 1_000);
    turn_input_off(&fs, &mut ev, PointerInput::Click, 2_000);
    assert!(turn_input_on(&fs, &mut ev, PointerInput::Cursor, 3_000).is_ok());
    let text = crate::logger::format_handmark_day_line_for_test(&ev.row(5).unwrap());
    let v: serde_json::Value = serde_json::from_str(&text).unwrap();
    let arr = v["input_toggles"].as_array().expect("input_toggles");
    assert_eq!(arr.len(), 3);
    for e in arr {
        let mut keys: Vec<&str> = e.as_object().unwrap().keys().map(String::as_str).collect();
        keys.sort_unstable();
        assert_eq!(keys, vec!["input", "on", "t"]);
        assert!(matches!(e["input"].as_str(), Some("cursor" | "click")));
    }
}

/// 入力の種類の値の 3 つの真実源（Rust の列挙・logger が許す値・スキーマの enum）が一致する。
#[test]
fn pointer_input_values_agree_across_enum_logger_and_schema() {
    use crate::analysis::handmark::day::PointerInput;
    let mut from_enum: Vec<String> = [PointerInput::Cursor, PointerInput::Click]
        .iter()
        .map(|i| i.as_str().to_string())
        .collect();
    from_enum.sort();
    assert_eq!(from_enum, schema_enum("HandmarkPointerInputDto"));
    // logger は固定の 2 語だけを書く（それ以外の語の要素は落とす）。
    let mut r = Evaluation::run(&with_table(), true, 20_411, None)
        .row(1)
        .unwrap();
    assert_eq!(from_enum, vec!["click".to_string(), "cursor".to_string()]);
    r.input_toggles = vec![(1, "cursor", true), (2, "click", true), (3, "wheel", true)];
    let text = crate::logger::format_handmark_day_line_for_test(&r);
    let v: serde_json::Value = serde_json::from_str(&text).unwrap();
    assert_eq!(v["input_toggles"].as_array().map(Vec::len), Some(2));
}

/// 窓の TS が `export const NAME = <数>;` で持つ値を読む（無ければ None）。
fn ts_const(src: &str, name: &str) -> Option<f64> {
    let head = format!("export const {name} = ");
    let line = src.lines().find(|l| l.trim_start().starts_with(&head))?;
    let rest = line.trim_start().strip_prefix(&head)?;
    rest.trim_end().trim_end_matches(';').trim().parse().ok()
}

/// Rust の場の定数と、窓の TS に手で写した値の食い違い（名前の一覧）。
fn trace_const_mismatches(ts: &str) -> Vec<&'static str> {
    use crate::analysis::handmark::trace::{BEND_MAX, BOX_W, GRID_H, GRID_W, MOTE_MAX};
    let want: [(&'static str, f64); 5] = [
        ("GRID_W", GRID_W as f64),
        ("GRID_H", GRID_H as f64),
        ("BOX_W", f64::from(BOX_W)),
        ("BEND_MAX", f64::from(BEND_MAX)),
        ("MOTE_MAX", f64::from(MOTE_MAX)),
    ];
    want.iter()
        .filter(|(n, v)| ts_const(ts, n).is_none_or(|t| (t - v).abs() > 1e-6))
        .map(|(n, _)| *n)
        .collect()
}

#[test]
fn the_window_copies_the_field_constants_exactly() {
    let ts = WINDOW[1].1;
    assert!(
        trace_const_mismatches(ts).is_empty(),
        "{:?}",
        trace_const_mismatches(ts)
    );
    // 陽性対照: 片方だけ値を変えると食い違いが出る。
    let changed = ts.replacen(
        "export const BEND_MAX = 0.9;",
        "export const BEND_MAX = 0.8;",
        1,
    );
    assert_ne!(changed, ts, "対照の置き換えが当たっていない");
    assert_eq!(trace_const_mismatches(&changed), vec!["BEND_MAX"]);
    // 陽性対照: 消すと食い違いが出る。
    let gone = ts.replacen("export const GRID_W = 16;", "", 1);
    assert_eq!(trace_const_mismatches(&gone), vec!["GRID_W"]);
}

/// 手跡の窓は WKWebView の既定（suspend）のままだと、数分でタイマーと描画が絞られて粗く遅くなる
/// （2026-11-09 の画面の確かめ）。窓の作りが絞りを切っていることを縛る。
fn stage_disables_throttling(src: &str) -> bool {
    let body = strip_test_items(src);
    body.contains(&["BackgroundThrottlingPolicy", "::Disabled"].concat())
        && body.contains(".background_throttling(")
}

#[test]
fn the_stage_window_is_not_throttled_when_covered() {
    let src = include_str!("handmark_stage.rs");
    assert!(stage_disables_throttling(src));
    // 陽性対照: 指定を外すと赤になる。
    let gone = src.replace(".background_throttling(", ".no_such_call(");
    assert_ne!(gone, src, "対照の置き換えが当たっていない");
    assert!(!stage_disables_throttling(&gone));
}

// ---- 帯の窓（PR 2・ADR-051・ADR-050 D3） ----

/// 帯の窓の層の本文。`handmark_edge_strip` は macOS だけのモジュールなので、Windows でも走るこの検査は
/// 定数を参照せずにソースを読む（2026-11-09 の CI で、macOS だけの定数を参照して Windows のビルドが止まった）。
const STRIP_RS: &str = include_str!("handmark_edge_strip.rs");

/// `src` の `[pub ]const <name>: &str = "...";` の値（行頭から探す）。
fn rs_str_const(src: &str, name: &str) -> String {
    let heads = [
        format!("pub const {name}: &str = \""),
        format!("const {name}: &str = \""),
    ];
    let line = src
        .lines()
        .map(str::trim_start)
        .find(|l| heads.iter().any(|h| l.starts_with(h.as_str())))
        .unwrap_or_else(|| panic!("{name} が見つからない"));
    let head = heads
        .iter()
        .find(|h| line.starts_with(h.as_str()))
        .expect("head");
    let rest = &line[head.len()..];
    rest[..rest.find('"').expect("閉じない文字列")].to_string()
}

/// TS の `const <name> = "...";` の値。
fn ts_str_const(src: &str, name: &str) -> Option<String> {
    let head = format!("const {name} = \"");
    let line = src.lines().find(|l| l.trim_start().starts_with(&head))?;
    let rest = &line.trim_start()[head.len()..];
    Some(rest[..rest.find('"')?].to_string())
}

/// 見張りは、窓の `occlusionState` をそのまま見えているかにせず、画面のロック・ユーザーの切り替え・主画面の
/// 眠りと合わせた `strip_seen` を通す（2026-11-12: ロック中も見えている扱いで、描画も止まらなかった・判断 11）。
/// 見張りは AppHandle を要りテストで走らないので、本文で縛る。
#[test]
fn the_strip_probe_judges_visibility_through_strip_seen() {
    // body() は行で読み直すので、Windows の CRLF のチェックアウトでも同じ本文になる（2026-11-12 の CI で赤）。
    let src = body(STRIP_RS);
    let probe = fn_body(&src, "fn probe_loop");
    // CRLF の本文でも同じ範囲を切り出せる（macOS でも Windows の形を確かめる）。
    let crlf = body(&STRIP_RS.replace("\r\n", "\n").replace('\n', "\r\n"));
    assert_eq!(fn_body(&crlf, "fn probe_loop"), probe);
    assert_eq!(
        probe
            .matches("let visible = strip_seen(occlusion_visible, session, asleep);")
            .count(),
        1,
        "見張りが strip_seen を通していない"
    );
    // 窓の読みの値は、受け取りと strip_seen の呼び出しの 2 か所でしか使わない（そのまま記録・送りに回さない）。
    assert_eq!(
        probe.matches("occlusion_visible").count(),
        2,
        "見張りが occlusion_visible を strip_seen の外で使っている"
    );
    // 判定した値が、印と窓への送りに使われている。
    assert_eq!(probe.matches("|| !set_seen_for(gen, visible)").count(), 1);
    assert_eq!(
        probe
            .matches("app.emit_to(LABEL, VISIBLE_EVENT, visible);")
            .count(),
        1
    );
    // 読めなかった刻み（メインスレッドへ投げられない・返事が来ない）は見えていない側に倒す（Codex の指摘・判断 14）。
    assert_eq!(probe.matches("set_seen_for(gen, false);").count(), 2);
    assert!(probe.contains("let session = read_session();"));
    assert!(probe.contains("let asleep = main_display.is_asleep();"));
}

/// `item` の宣言から、同じ字下げで閉じる `}` までの本文（`fn` の検査用）。
fn fn_body<'a>(src: &'a str, item: &str) -> &'a str {
    let from = src
        .find(item)
        .unwrap_or_else(|| panic!("{item} が見つからない"));
    let line_start = src[..from].rfind('\n').map_or(0, |i| i + 1);
    let indent = &src[line_start..from];
    let close = format!("\n{indent}}}\n");
    let to = src[from..]
        .find(&close)
        .unwrap_or_else(|| panic!("{item} の終わりが見つからない"));
    &src[from..from + to + close.len()]
}

/// `read_session` が画面のセッションの辞書から読むのは、ロックの印と前に出ているかの 2 つの鍵だけ。
/// 利用者の名前などの他の鍵を読む・辞書を回す・値を Debug で出す道を作らない（security-checker L1・判断 13）。
#[test]
fn read_session_reads_only_the_two_session_keys() {
    let src = body(STRIP_RS);
    let f = fn_body(&src, "fn read_session");
    let keys: Vec<&str> = f
        .match_indices("truthy(\"")
        .map(|(i, _)| {
            let rest = &f[i + "truthy(\"".len()..];
            &rest[..rest.find('"').expect("閉じない鍵")]
        })
        .collect();
    assert_eq!(
        keys,
        ["CGSSessionScreenIsLocked", "kCGSSessionOnConsoleKey"]
    );
    // 辞書に触れるのは truthy の中の 1 か所だけ（find 以外の読み方・直の CF 呼び出しも数える）。
    assert_eq!(
        f.matches("dict.").count(),
        1,
        "辞書の読みは truthy の 1 か所だけ"
    );
    // 陽性対照の語は実行時に組み立てる（この検査の本文に検査対象の語を書かない）。
    let banned = [
        ["User", "Name"].concat(),
        ["get_keys", "_and_values"].concat(),
        [".it", "er("].concat(),
        ["{", ":?}"].concat(),
        ["tracing", "::"].concat(),
        ["Get", "Value"].concat(),
    ];
    for b in &banned {
        assert!(!f.contains(b.as_str()), "read_session に {b} がある");
    }
    // 陽性対照: 他の鍵を読む本文は赤になる。
    let planted = f.replace(
        "\"kCGSSessionOnConsoleKey\"",
        &format!("\"{}\"", ["kCGSSession", "User", "Name", "Key"].concat()),
    );
    assert!(planted.contains(&banned[0]));
    let planted_keys: Vec<&str> = planted
        .match_indices("truthy(\"")
        .map(|(i, _)| {
            let rest = &planted[i + "truthy(\"".len()..];
            &rest[..rest.find('"').expect("閉じない鍵")]
        })
        .collect();
    assert_ne!(
        planted_keys,
        ["CGSSessionScreenIsLocked", "kCGSSessionOnConsoleKey"]
    );
}

/// 帯のイベント名（近さ・見えているか）を TS で知ってよいのは帯の 2 ファイルだけ（`target` なしの `listen` で
/// 他の窓に届かないように）。背景の窓の TS も知らない。帯の窓の TS は場・波紋のイベントを知らない。
#[test]
fn only_the_strip_window_knows_the_strip_events() {
    let files = ts_sources();
    assert!(files.len() > 5, "src/ の走査が空回り: {}", files.len());
    for name in [
        rs_str_const(STRIP_RS, "NEAR_EVENT"),
        rs_str_const(STRIP_RS, "VISIBLE_EVENT"),
    ] {
        let name = name.as_str();
        assert!(name.starts_with("handmark-strip-"), "想定外の値: {name}");
        assert!(
            ts_files_naming_except(name, &files, &STRIP_WINDOW).is_empty(),
            "{name} を帯の窓の外のコードが知っている: {:?}",
            ts_files_naming_except(name, &files, &STRIP_WINDOW)
        );
        // 帯の窓は実際に聞いている（探し方が空回りしていない）
        assert!(
            body(STRIP_WINDOW[0].1).contains(name),
            "{name} を HandmarkEdgeStrip.tsx が聞いていない"
        );
        // 陽性対照: 背景の窓のファイル・他のファイルが名前を書いたら見つかる（拡張子ごと・HTML も）
        for planted_name in [
            "HandmarkStage.tsx",
            "Planted.tsx",
            "planted.js",
            "planted.jsx",
            "planted.mjs",
            "planted.html",
        ] {
            let mut planted = files
                .iter()
                .filter(|(n, _)| n != planted_name)
                .cloned()
                .collect::<Vec<_>>();
            planted.push((planted_name.to_string(), format!("listen('{name}')")));
            assert_eq!(
                ts_files_naming_except(name, &planted, &STRIP_WINDOW),
                vec![planted_name.to_string()],
                "対照が赤にならない（{planted_name}）"
            );
        }
    }
    // 帯の窓の TS は、場・波紋のイベントを知らない（`others_naming` は帯のファイルを除かない）。
    for name in [stage_event("TRACE_EVENT"), stage_event("RIPPLE_EVENT")] {
        assert!(
            STRIP_WINDOW.iter().all(|(_, t)| !body(t).contains(&name)),
            "帯の窓が {name} を知っている"
        );
    }
}

/// 帯のイベント名（定数名と文字列）を Rust で参照してよいのは `handmark_edge_strip.rs` だけ。近さを送る
/// 関数 `emit_near` を呼べるのは `lib.rs`（ポインタのスレッドの配線）と定義のファイルだけ。
#[test]
fn only_the_strip_rs_names_the_strip_events_and_only_lib_calls_emit_near() {
    let files = rs_sources();
    assert!(files.len() > 30, "走査が空回り: {}", files.len());
    let (near, visible) = (
        rs_str_const(STRIP_RS, "NEAR_EVENT"),
        rs_str_const(STRIP_RS, "VISIBLE_EVENT"),
    );
    let events = [
        "NEAR_EVENT",
        "VISIBLE_EVENT",
        near.as_str(),
        visible.as_str(),
    ];
    assert!(files.iter().any(|(n, _)| n == "handmark_edge_strip.rs"));
    assert_eq!(
        rs_files_naming(&events, &["handmark_edge_strip.rs"], &files),
        Vec::<String>::new()
    );
    let names = ["emit_near"];
    assert_eq!(
        rs_files_naming(&names, &["lib.rs", "handmark_edge_strip.rs"], &files),
        Vec::<String>::new()
    );
    // 許したファイルは本当に使っている（探し方が空回りしていない）。
    let strip = files
        .iter()
        .find(|(n, _)| n == "handmark_edge_strip.rs")
        .expect("strip");
    assert!(events.iter().all(|w| body(&strip.1).contains(w)));
    let lib = files.iter().find(|(n, _)| n == "lib.rs").expect("lib.rs");
    assert!(body(&lib.1).contains("emit_near"));
    // 陽性対照: 他のファイル（背景の窓の層を含む）が書いたら見つかる（拡張子の違う別名も同じ）。
    for planted_name in ["planted.rs", "handmark_stage.rs"] {
        for w in events {
            let mut planted: Vec<_> = files
                .iter()
                .filter(|(n, _)| n != planted_name)
                .cloned()
                .collect();
            planted.push((
                planted_name.to_string(),
                format!("fn f() {{ let _ = \"{w}\"; {w}; }}"),
            ));
            assert_eq!(
                rs_files_naming(&events, &["handmark_edge_strip.rs"], &planted),
                vec![planted_name.to_string()],
                "対照が赤にならない（{planted_name}・{w}）"
            );
        }
        let mut planted: Vec<_> = files
            .iter()
            .filter(|(n, _)| n != planted_name)
            .cloned()
            .collect();
        planted.push((
            planted_name.to_string(),
            "fn f() { emit_near(); }".to_string(),
        ));
        assert_eq!(
            rs_files_naming(&names, &["lib.rs", "handmark_edge_strip.rs"], &planted),
            vec![planted_name.to_string()]
        );
    }
}

/// 帯の窓の層は、記録・ログの口・ファイル・ネットワーク・推定を呼ばない。送りは帯の窓だけへ（`emit_to`）。
#[test]
fn the_strip_rs_touches_no_recorder_file_network_estimator_and_emits_only_to_its_window() {
    assert_clean(
        "帯の窓の層",
        &[("handmark_edge_strip.rs", STRIP_RS)],
        &[
            "LogEntry",
            "log_tx",
            "crate::logger",
            "std::fs",
            "OpenOptions",
            "applog",
            "std::net",
            "reqwest",
            "TcpStream",
            "crate::analysis::engine",
            "features",
            "intervention",
            "invitation",
            "p_stuck",
            "handmark_pointer::",
            "handmark_pointer_macos",
            // 宛先の絞りを迂回する口(`emit_to` の第 1 引数の検査と対にする)
            "emit_filter",
            "EventTarget",
            "Emitter::emit",
        ],
    );
    let all = [".", "emit", "("].concat();
    assert!(hits(STRIP_RS, &[all.as_str()]).is_empty());
    assert!(body(STRIP_RS).contains("emit_to"));
    assert_eq!(
        hits(&format!("{all}\n{STRIP_RS}"), &[all.as_str()]).len(),
        1
    );
    // 全窓から聞く口を使わない
    let listen_any = ["listen", "_any"].concat();
    assert!(hits(STRIP_RS, &[listen_any.as_str()]).is_empty());
    // 窓の様子の口（`status`）は背景の窓のもの。帯の窓の層は背景の窓を開け閉めしない。
    assert!(hits(STRIP_RS, &["handmark_stage::open", "handmark_stage::close"]).is_empty());
}

/// 帯の窓も、覆われたときに WKWebView の既定（suspend）で絞られない。
#[test]
fn the_strip_window_is_not_throttled_when_covered() {
    assert!(stage_disables_throttling(STRIP_RS));
    // 陽性対照: 指定を外すと赤になる。
    let gone = STRIP_RS.replace(".background_throttling(", ".no_such_call(");
    assert_ne!(gone, STRIP_RS, "対照の置き換えが当たっていない");
    assert!(!stage_disables_throttling(&gone));
}

/// 帯の窓の label が Rust・capabilities・`main.tsx` の分岐で食い違わない（食い違うと窓が空のまま・権限が無い）。
fn label_mismatches(rs: &str, caps: &str, main_tsx: &str) -> Vec<&'static str> {
    let label = rs_str_const(rs, "LABEL");
    let mut out = Vec::new();
    let caps_json: serde_json::Value = serde_json::from_str(caps).expect("capabilities の JSON");
    let in_caps = caps_json["windows"]
        .as_array()
        .is_some_and(|w| w.iter().any(|v| v.as_str() == Some(label.as_str())));
    if !in_caps {
        out.push("capabilities");
    }
    if !main_tsx.contains(&format!("windowLabel === \"{label}\"")) {
        out.push("main.tsx");
    }
    out
}

#[test]
fn the_strip_label_agrees_across_rust_capabilities_and_main_tsx() {
    let caps = include_str!("../capabilities/handmark-stage.json");
    let main_tsx = include_str!("../../src/main.tsx");
    assert_eq!(rs_str_const(STRIP_RS, "LABEL"), "handmark-edge-strip");
    assert!(label_mismatches(STRIP_RS, caps, main_tsx).is_empty());
    // 陽性対照: 片方を変えると食い違いが出る。
    let caps_changed = caps.replace("handmark-edge-strip", "handmark-edge-stripe");
    assert_ne!(caps_changed, caps);
    assert_eq!(
        label_mismatches(STRIP_RS, &caps_changed, main_tsx),
        vec!["capabilities"]
    );
    let main_changed = main_tsx.replace("handmark-edge-strip", "handmark-edge-stripe");
    assert_ne!(main_changed, main_tsx);
    assert_eq!(
        label_mismatches(STRIP_RS, caps, &main_changed),
        vec!["main.tsx"]
    );
}

/// 窓の TS に手で写した値（イベント名・状態の間隔・近さの上限）と Rust の食い違い。
fn strip_const_mismatches(tsx: &str, frame_ts: &str) -> Vec<&'static str> {
    let mut out = Vec::new();
    if ts_str_const(tsx, "STATE_EVENT").as_deref() != Some(stage_event("STATE_EVENT").as_str()) {
        out.push("STATE_EVENT");
    }
    if ts_str_const(tsx, "NEAR_EVENT").as_deref()
        != Some(rs_str_const(STRIP_RS, "NEAR_EVENT").as_str())
    {
        out.push("NEAR_EVENT");
    }
    if ts_str_const(tsx, "VISIBLE_EVENT").as_deref()
        != Some(rs_str_const(STRIP_RS, "VISIBLE_EVENT").as_str())
    {
        out.push("VISIBLE_EVENT");
    }
    let tick = crate::analysis::handmark::state::TICK_MS as f64;
    if ts_const(frame_ts, "STATE_TICK_MS").is_none_or(|t| (t - tick).abs() > 1e-6) {
        out.push("STATE_TICK_MS");
    }
    // 近さの上限は、帯の上にいるときの `strip_near` の値
    let top = f64::from(crate::handmark_pointer_thread::strip_near(true, 5.0, 0.0));
    if ts_const(frame_ts, "NEAR_MAX").is_none_or(|t| (t - top).abs() > 1e-6) {
        out.push("NEAR_MAX");
    }
    out
}

#[test]
fn the_strip_window_copies_the_constants_exactly() {
    let (tsx, frame_ts) = (STRIP_WINDOW[0].1, STRIP_WINDOW[1].1);
    assert!(
        strip_const_mismatches(tsx, frame_ts).is_empty(),
        "{:?}",
        strip_const_mismatches(tsx, frame_ts)
    );
    // 陽性対照: 片方だけ値を変えると食い違いが出る。
    let changed = frame_ts.replacen(
        "export const STATE_TICK_MS = 250;",
        "export const STATE_TICK_MS = 200;",
        1,
    );
    assert_ne!(changed, frame_ts, "対照の置き換えが当たっていない");
    assert_eq!(strip_const_mismatches(tsx, &changed), vec!["STATE_TICK_MS"]);
    let changed = frame_ts.replacen(
        "export const NEAR_MAX = 10;",
        "export const NEAR_MAX = 1;",
        1,
    );
    assert_ne!(changed, frame_ts);
    assert_eq!(strip_const_mismatches(tsx, &changed), vec!["NEAR_MAX"]);
    let changed = tsx.replacen(
        "const NEAR_EVENT = \"handmark-strip-near\";",
        "const NEAR_EVENT = \"handmark-strip-nearby\";",
        1,
    );
    assert_ne!(changed, tsx);
    assert_eq!(
        strip_const_mismatches(&changed, frame_ts),
        vec!["NEAR_EVENT"]
    );
    let changed = tsx.replacen("const STATE_EVENT = \"handmark-state\";", "", 1);
    assert_ne!(changed, tsx);
    assert_eq!(
        strip_const_mismatches(&changed, frame_ts),
        vec!["STATE_EVENT"]
    );
}

/// `emit_to(` の呼び出しごとの第 1 引数（空白を除いた文字列）。本文（コメント・テストを除く）から読む。
fn emit_to_targets(src: &str) -> Vec<String> {
    let b = body(src);
    let mut out = Vec::new();
    let mut rest = b.as_str();
    let head = ["emit", "_to("].concat();
    while let Some(i) = rest.find(&head) {
        let after = &rest[i + head.len()..];
        let end = after.find(',').unwrap_or(after.len());
        out.push(after[..end].split_whitespace().collect::<String>());
        rest = after;
    }
    out
}

/// 帯の層の送りは、宛先がすべて帯の窓の `LABEL`（宛先を変数・別の窓・全窓にすると赤）。
#[test]
fn every_emit_to_in_the_strip_rs_targets_label() {
    let targets = emit_to_targets(STRIP_RS);
    assert!(
        targets.len() >= 4,
        "送りの数が想定より少ない（空回り）: {targets:?}"
    );
    assert!(
        targets.iter().all(|t| t == "LABEL"),
        "emit_to の第 1 引数が LABEL でない: {targets:?}"
    );
    // 陽性対照: 別の宛先（文字列・別の定数・改行を挟む形）を足すと見つかる。
    for planted_target in ["\"main\"", "OTHER", "self.target"] {
        for call in [
            format!("fn f() {{ app.emit_to({planted_target}, X, 1); }}"),
            format!("fn f() {{ app.emit_to(\n    {planted_target},\n    X, 1); }}"),
        ] {
            let planted = format!("{call}\n{STRIP_RS}");
            let t = emit_to_targets(&planted);
            assert_eq!(t.len(), targets.len() + 1);
            assert!(
                t.iter().any(|x| x != "LABEL"),
                "対照が赤にならない: {planted_target}"
            );
        }
    }
}

/// 帯の層の `tracing` は `warn_once` の 1 か所だけ（値・状態をログに出さない）。
#[test]
fn the_strip_rs_has_exactly_one_tracing_call_in_warn_once() {
    let needle = ["tracing", "::"].concat();
    let count = |src: &str| body(src).matches(needle.as_str()).count();
    assert_eq!(count(STRIP_RS), 1, "tracing:: は warn_once の 1 か所だけ");
    let b = body(STRIP_RS);
    let from = b.find("fn warn_once").expect("warn_once");
    let end = b[from..].find("\n    }\n").expect("warn_once の終わり");
    assert!(
        b[from..from + end].contains(needle.as_str()),
        "tracing:: が warn_once の外にある"
    );
    // 陽性対照: 1 行足すと数が増える。
    let planted = format!("{STRIP_RS}\nfn x() {{ {needle}debug!(\"x\"); }}");
    assert_eq!(count(&planted), 2);
}

/// `emit_near` を `lib.rs` が呼ぶのは 1 か所だけ（ポインタのスレッドの配線）。
#[test]
fn lib_rs_calls_emit_near_exactly_once() {
    let files = rs_sources();
    let lib = files.iter().find(|(n, _)| n == "lib.rs").expect("lib.rs");
    let count = |src: &str| body(src).matches("emit_near").count();
    assert_eq!(count(&lib.1), 1, "lib.rs の emit_near は 1 か所だけ");
    let planted = format!("{}\nfn x() {{ emit_near(); }}", lib.1);
    assert_eq!(count(&planted), 2, "対照が赤にならない");
}

const CONF: &str = include_str!("../tauri.conf.json");

/// CSP の指令ごとの値（文字列でもオブジェクトでも読む）。
fn csp_directives(conf: &str) -> Vec<(String, Vec<String>)> {
    let v: serde_json::Value = serde_json::from_str(conf).expect("tauri.conf.json");
    let csp = &v["app"]["security"]["csp"];
    match csp {
        serde_json::Value::String(s) => s
            .split(';')
            .filter_map(|d| {
                let mut it = d.split_whitespace();
                let name = it.next()?.to_string();
                Some((name, it.map(str::to_string).collect()))
            })
            .collect(),
        serde_json::Value::Object(m) => m
            .iter()
            .map(|(k, val)| {
                let toks = match val {
                    serde_json::Value::String(s) => {
                        s.split_whitespace().map(str::to_string).collect()
                    }
                    serde_json::Value::Array(a) => a
                        .iter()
                        .filter_map(|x| x.as_str().map(str::to_string))
                        .collect(),
                    _ => Vec::new(),
                };
                (k.clone(), toks)
            })
            .collect(),
        _ => Vec::new(),
    }
}

/// 外の宛先を許す指令(`connect-src`・`img-src`・`default-src`)の値。
fn csp_external(conf: &str) -> Vec<String> {
    // 許す source expression の一覧（これ以外は外の宛先になりうるとみなす。スキームを省いたホスト名も赤）。
    let allowed = ["'self'", "data:", "'none'"];
    csp_directives(conf)
        .into_iter()
        .filter(|(n, _)| ["connect-src", "img-src", "default-src"].contains(&n.as_str()))
        .flat_map(|(n, toks)| toks.into_iter().map(move |t| (n.clone(), t)))
        .filter(|(_, t)| !allowed.contains(&t.as_str()))
        .map(|(n, t)| format!("{n} {t}"))
        .collect()
}

/// CSP に外の宛先が無い(窓が外へ送れない)。`default-src` が `connect-src` の既定になるので、これも要る。
#[test]
fn the_csp_names_no_external_destination() {
    let dirs = csp_directives(CONF);
    assert!(
        dirs.iter()
            .any(|(n, t)| n == "default-src" && t.iter().any(|x| x == "'self'")),
        "default-src 'self' が無い: {dirs:?}"
    );
    assert_eq!(csp_external(CONF), Vec::<String>::new());
    // 陽性対照: 外の宛先を足すと赤になる(文字列の形・オブジェクトの形、どちらの指令でも)。
    for (find, put) in [
        (
            "default-src 'self'",
            "default-src 'self' https://example.invalid",
        ),
        (
            "img-src 'self' data:",
            "img-src 'self' data: http://example.invalid",
        ),
        ("default-src 'self'", "default-src *"),
        (
            "default-src 'self'",
            "default-src 'self'; connect-src ws://example.invalid",
        ),
        (
            "default-src 'self'",
            "default-src 'self'; connect-src wss://example.invalid",
        ),
        // スキームを省いたホスト名（2026-11-12 の Codex の指摘・旧い検査は通していた）。
        (
            "default-src 'self'",
            "default-src 'self'; connect-src example.invalid",
        ),
    ] {
        let planted = CONF.replacen(find, put, 1);
        assert_ne!(planted, CONF, "対照の置き換えが当たっていない: {find}");
        assert!(
            !csp_external(&planted).is_empty(),
            "対照が赤にならない: {put}"
        );
    }
    let object_form = r#"{"app":{"security":{"csp":{"default-src":"'self'","connect-src":["'self'","https://example.invalid"]}}}}"#;
    assert_eq!(csp_external(object_form).len(), 1);
}

/// 帯のイベント名の接頭辞(連結の片割れ: `"handmark-strip-" + x`)も、帯の 2 ファイルの外に現れない。
#[test]
fn the_strip_event_prefix_appears_only_in_the_strip_window() {
    let files = ts_sources();
    assert!(files.len() > 5, "src/ の走査が空回り: {}", files.len());
    let prefix = ["handmark", "-strip-"].concat();
    assert_eq!(
        ts_files_naming_except(&prefix, &files, &STRIP_WINDOW),
        Vec::<String>::new(),
        "帯の窓の外のコードが接頭辞を書いている"
    );
    // 帯の窓は実際に書いている(探し方が空回りしていない)
    assert!(body(STRIP_WINDOW[0].1).contains(prefix.as_str()));
    // 陽性対照: 連結の片割れだけでも、拡張子ごと・HTML も見つかる。
    for planted_name in [
        "Planted.tsx",
        "planted.ts",
        "planted.js",
        "planted.mjs",
        "planted.html",
    ] {
        let mut planted = files.clone();
        planted.push((
            planted_name.to_string(),
            format!("const n = \"{prefix}\" + kind;"),
        ));
        assert_eq!(
            ts_files_naming_except(&prefix, &planted, &STRIP_WINDOW),
            vec![planted_name.to_string()],
            "対照が赤にならない（{planted_name}）"
        );
    }
}
