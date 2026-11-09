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
const FILES: [(&str, &str); 8] = [
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
];
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
