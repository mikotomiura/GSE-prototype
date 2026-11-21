//! `gse-replay --features` の `context`（文脈の量）を実バイナリで確かめる統合テスト
//! (`.steering/20261121-auto-context-segmentation/`)。
//!
//! 欠測の 3 状態（宣言なし / 宣言ありで 0 行 / 宣言ありで行あり）と、tick への帰属を見る。

use std::path::PathBuf;
use std::process::Command;

use serde_json::{json, Value};

const T0: u64 = 1_700_000_000_000;

fn caps() -> Value {
    json!({
        "unconditional": ["feat", "ime_state", "key", "paste", "session_meta", "session_start"],
        "threshold_gated": ["hook_health", "starve_window"],
        "config_gated": ["focus_transition", "pointer_bin", "ime_shadow"]
    })
}

/// 10 秒の打鍵（毎秒 1 回）と feat 行。`extra` は追加の行。
fn session(meta_caps: Option<Value>, extra: Vec<Value>) -> String {
    let mut meta = json!({"type": "meta", "session_start": T0, "hmm_version": "0.5.0"});
    if let Some(c) = meta_caps {
        meta["capabilities"] = c;
    }
    let mut lines = vec![
        meta,
        json!({"type": "session_start", "t": T0}),
        json!({"type": "session_meta", "track": "main", "task_kind": "argumentative",
               "monk_mode": false, "intervention_enabled": false, "condition": null,
               "label_pool": null, "head_id": "writing", "ts": T0}),
    ];
    let mut events: Vec<Value> = Vec::new();
    for s in 0..10u64 {
        let t = T0 + s * 1000 + 100;
        events.push(json!({"type": "key", "t": t, "vk": 0x41, "press": true}));
        events.push(json!({"type": "key", "t": t + 40, "vk": 0x41, "press": false}));
        events.push(json!({"type": "feat", "t": T0 + s * 1000 + 999, "f1": 0, "f3": 0, "f4": 0,
                           "f5": 0, "f6": 0, "p_flow": 0.34, "p_inc": 0.33, "p_stuck": 0.33,
                           "raw_x": 0, "raw_y": 0, "ewma_x": 0, "ewma_y": 0, "obs": 0, "alpha": 0.3}));
    }
    events.extend(extra);
    events.sort_by_key(|v| v["t"].as_u64().unwrap_or(0));
    lines.extend(events);
    let mut body = lines
        .iter()
        .map(Value::to_string)
        .collect::<Vec<_>>()
        .join("\n");
    body.push('\n');
    body
}

struct TempSession {
    path: PathBuf,
}

impl TempSession {
    fn write(tag: &str, body: &str) -> Self {
        let path = std::env::temp_dir().join(format!(
            "gse-context-features-{}-{tag}.ndjson",
            std::process::id()
        ));
        std::fs::write(&path, body).expect("write the temporary session NDJSON");
        Self { path }
    }
}

impl Drop for TempSession {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.path);
    }
}

fn rows(body: &str, tag: &str) -> Vec<Value> {
    let s = TempSession::write(tag, body);
    let out = Command::new(env!("CARGO_BIN_EXE_gse-replay"))
        .arg(&s.path)
        .arg("--features")
        .output()
        .expect("spawn gse-replay");
    assert!(
        out.status.success(),
        "gse-replay --features が失敗した: {:?}\n{}",
        out.status,
        String::from_utf8_lossy(&out.stderr)
    );
    let env: Value = serde_json::from_slice(&out.stdout).expect("envelope JSON");
    env["rows"].as_array().expect("rows").clone()
}

fn extra_rows() -> Vec<Value> {
    vec![
        json!({"type": "focus_transition", "t": T0 + 3_500}),
        json!({"type": "pointer_bin", "t": T0 + 6_000, "moved": 4, "buttons": 1, "wheel": 0}),
        json!({"type": "ime_state", "t": T0 + 2_200, "on": true, "active": false}),
    ]
}

#[test]
fn declared_rows_are_counted_per_tick() {
    let r = rows(&session(Some(caps()), extra_rows()), "declared");
    assert_eq!(r.len(), 10);
    // 原点は最初の打鍵 (T0 + 100)。tick i は [T0 + 100 + 1000 i, T0 + 100 + 1000 (i + 1))。
    let ctx = |i: usize| &r[i]["context"];
    // focus T0 + 3500 → tick 3。
    assert_eq!(ctx(3)["focus_transitions"], 1);
    assert_eq!(ctx(2)["focus_transitions"], 0);
    assert_eq!(ctx(4)["focus_transitions"], 0);
    // pointer_bin の終端 T0 + 6000 → tick 5。
    assert_eq!(ctx(5)["pointer_active"], true);
    assert_eq!(ctx(5)["pointer_moved"], 4);
    assert_eq!(ctx(6)["pointer_active"], false);
    // ime_state T0 + 2200 (on) → tick 2 の終端から on。それより前は分からない。
    assert_eq!(ctx(1)["ime_on"], Value::Null);
    assert_eq!(ctx(2)["ime_on"], true);
    assert_eq!(ctx(9)["ime_on"], true);
    // キーの種類の構成の合計は activity.keys と一致する。
    for row in &r {
        let sum: u64 = row["context"]["cat_counts"]
            .as_object()
            .expect("cat_counts")
            .values()
            .map(|v| v.as_u64().expect("count"))
            .sum();
        assert_eq!(sum, row["activity"]["keys"].as_u64().expect("keys"));
    }
}

#[test]
fn declared_but_no_rows_is_null_not_zero() {
    let r = rows(&session(Some(caps()), vec![]), "declared-empty");
    for row in &r {
        assert_eq!(row["context"]["focus_transitions"], Value::Null);
        assert_eq!(row["context"]["pointer_active"], Value::Null);
        assert_eq!(row["context"]["ime_on"], Value::Null);
    }
}

#[test]
fn old_log_without_capabilities_is_null_even_with_rows() {
    let r = rows(&session(None, extra_rows()), "undeclared");
    for row in &r {
        assert_eq!(row["context"]["focus_transitions"], Value::Null);
        assert_eq!(row["context"]["pointer_active"], Value::Null);
        assert_eq!(row["context"]["pointer_moved"], Value::Null);
        assert_eq!(row["context"]["ime_on"], Value::Null);
    }
    // 打鍵の構成は計器の宣言に依らず出る。
    assert_eq!(r[0]["context"]["cat_counts"]["alphabetic"], 1);
}
