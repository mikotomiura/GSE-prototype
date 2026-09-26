//! 起票 P1-A: **凍結既定の config のまま** `restart.restop_ms` が非 null になることを測る。
//!
//! # ⚠️ なぜ要るか
//!
//! 旧 `.steering/20260914-mhd-feature-offline-tiers/issues/006-acceptance.sh` の AC6（`restop_ms` が
//! 1 つでも非 null）は、凍結既定（`warmup_count = 100`）では**原理的に成立しない**入力を使っていた
//! （θ の標本が 100 に届く頃には、残る onset が観測区間の右端で右側打ち切りになる）。
//! → その検査は呼び出しに `--set warmup_count=1` を足して旧前提を再現している。
//! ⚠️★ **副作用**: restart の非退化検査は、**凍結既定の config では 1 度も走っていなかった**。
//!
//! 本テストは `--set` / `--feature-config` を**渡さず**、凍結既定のまま
//! `gse-replay --features` を回して onset 行の `restop_ms` を測る。
//! ★ 入力は**テストが生成して一時ファイルに書く**（大きな fixture をコミットしない）。
//!
//! # 入力の時刻表（★ 凍結既定 `W = B = 30_000` / `q = 0.99` / `warmup_count = 100` から手で導いた）
//!
//! 時刻はセッション開始からの ms。条件 A は因果窓 `(t - W, t]` の純産出が `net_diff_min = 1` 未満。
//!
//! ```text
//!   1_000 ..= 150_000   feat 行を 1 Hz で敷く（観測区間 [a, b] = [1_000, 150_000]・穴なし）
//!   1_200 ..=  31_000   打鍵 150 回（200 ms 間隔）→ θ の標本 = 隣接対 149 個（>= warmup_count 100）
//!   31_000 + W = 61_000 s: 条件 A が true へ立ち上がる（最後の打鍵が窓から出る）
//!                       θ = 200（全対が 200 ms）→ t0 = s + θ = 61_200
//!   t0 + B     = 91_200 原点 o
//! 100_000 ..= 104_800   打鍵 25 回 → 再開 r_1 = 100_000（★ o より後）
//! 104_800 + W = 134_800 s'_1: 再停止（条件 A が再び true へ立ち上がる）
//!                       → restop_ms = s'_1 - o = 134_800 - 91_200 = 43_600
//! ```
//!
//! ★ `s'_1 = 134_800 <= b = 150_000` なので右側打ち切りにならない。
//! ⚠️ `s'_1` 自身も onset（`o_2 = 165_000 > b` なので**その行の `restop_ms` は打ち切りの `null`**）になる。
//! → 「onset 行がちょうど 1 本」を前提にしない。
//!
//! ★ 陰性対照は、**同じ入力から再停止の沈黙だけを消す**（2 つ目の打鍵の塊を観測区間の右端まで
//! 続ける）。再開はあるが再停止が観測されないので、`restop_ms` は全 onset 行で `null` になる。

use std::path::PathBuf;
use std::process::Command;

use serde_json::{json, Value};

/// ヘッダ行と `feat` 行の時刻の基準（`tests/fixtures/stall_onset_observed.ndjson` と同じ）。
const SESSION_START_MS: u64 = 1_700_000_000_000;
/// `feat` 行を敷く範囲（セッション開始からの ms・1 Hz）。
const FEAT_FIRST_OFFSET_MS: u64 = 1_000;
const FEAT_LAST_OFFSET_MS: u64 = 150_000;
const FEAT_STEP_MS: u64 = 1_000;
/// 打鍵の間隔と、press から release までの長さ。
const KEY_STEP_MS: u64 = 200;
const RELEASE_AFTER_PRESS_MS: u64 = 80;
/// 1 つ目の打鍵の塊（θ の標本を `warmup_count` 以上にするための長さ）。
const BURST1_FIRST_OFFSET_MS: u64 = 1_200;
const BURST1_PRESSES: u64 = 150;
/// 2 つ目の打鍵の塊（★ 原点 `o = 91_200` より後に始める）。
const BURST2_FIRST_OFFSET_MS: u64 = 100_000;
const BURST2_PRESSES: u64 = 25;
/// 上の時刻表から導いた `restop_ms`（`s'_1 - o`）。
const EXPECTED_RESTOP_MS: u64 = 43_600;

/// `--features` の入力を作る。`second_silence == false` なら 2 つ目の塊を観測区間の右端まで続ける
/// （★ 陰性対照: 再停止の沈黙だけが無い）。
fn build_session(second_silence: bool) -> String {
    let at = |offset_ms: u64| SESSION_START_MS + offset_ms;

    let mut events: Vec<(u64, String)> = Vec::new();
    let mut push_press = |offset_ms: u64, index: u64| {
        // ★ 文字キー (VK 'A'..='Z') だけ。条件 A の産出は挿入系 press の数で決まる。
        let vk = 0x41 + (index % 26);
        events.push((
            at(offset_ms),
            json!({"type": "key", "t": at(offset_ms), "vk": vk, "press": true}).to_string(),
        ));
        let release = offset_ms + RELEASE_AFTER_PRESS_MS;
        events.push((
            at(release),
            json!({"type": "key", "t": at(release), "vk": vk, "press": false}).to_string(),
        ));
    };

    for i in 0..BURST1_PRESSES {
        push_press(BURST1_FIRST_OFFSET_MS + i * KEY_STEP_MS, i);
    }
    let burst2_presses = if second_silence {
        BURST2_PRESSES
    } else {
        // 最後の打鍵が `feat` 行の右端に一致するまで続ける。
        (FEAT_LAST_OFFSET_MS - BURST2_FIRST_OFFSET_MS) / KEY_STEP_MS + 1
    };
    for i in 0..burst2_presses {
        push_press(BURST2_FIRST_OFFSET_MS + i * KEY_STEP_MS, BURST1_PRESSES + i);
    }

    for offset_ms in (FEAT_FIRST_OFFSET_MS..=FEAT_LAST_OFFSET_MS).step_by(FEAT_STEP_MS as usize) {
        events.push((
            at(offset_ms),
            json!({
                "type": "feat", "t": at(offset_ms),
                "f1": 0.0, "f3": 0.0, "f4": 0.0, "f5": 0.0, "f6": 0.0,
                "p_flow": 0.34, "p_inc": 0.33, "p_stuck": 0.33,
                "raw_x": 0.0, "raw_y": 0.0, "ewma_x": 0.0, "ewma_y": 0.0,
                "obs": 0, "alpha": 0.3,
            })
            .to_string(),
        ));
    }
    // ★ 実際のログと同じく時刻順にする（同時刻は挿入順のまま）。
    events.sort_by_key(|(t, _)| *t);

    let mut lines = vec![
        json!({"type": "meta", "session_start": SESSION_START_MS, "hmm_version": "0.5.0"})
            .to_string(),
        json!({"type": "session_start", "t": SESSION_START_MS}).to_string(),
        json!({
            "type": "session_meta", "track": "main", "task_kind": "argumentative",
            "monk_mode": false, "intervention_enabled": false, "condition": null,
            "label_pool": null, "head_id": "writing", "ts": SESSION_START_MS + 50,
        })
        .to_string(),
    ];
    lines.extend(events.into_iter().map(|(_, line)| line));
    let mut body = lines.join("\n");
    body.push('\n');
    body
}

/// `std::env::temp_dir()` 配下の一時 NDJSON。★ 破棄（テスト終了・失敗の unwind を含む）で消える。
struct TempSession {
    path: PathBuf,
}

impl TempSession {
    /// ⚠️ 同じプロセスで並列に走るテストと衝突しないよう、`tag` をファイル名に入れる。
    fn write(tag: &str, body: &str) -> Self {
        let path = std::env::temp_dir().join(format!(
            "gse-p1-restart-default-{}-{tag}.ndjson",
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

/// `gse-replay <session> --features` を**フラグ無しの設定**で回し、封筒（`{ provenance, config, rows }`）を返す。
/// ⚠️ `--set` / `--feature-config` / `--pole` を渡さない（★ 凍結既定・極は既定の baseline）。
fn replay_features(session: &TempSession) -> Value {
    let output = Command::new(env!("CARGO_BIN_EXE_gse-replay"))
        .arg(&session.path)
        .arg("--features")
        .output()
        .expect("spawn gse-replay");
    assert!(
        output.status.success(),
        "gse-replay --features が失敗した: {:?}\nstderr:\n{}",
        output.status,
        String::from_utf8_lossy(&output.stderr)
    );
    serde_json::from_slice(&output.stdout).expect("stdout is the feature envelope JSON")
}

/// 凍結既定のまま走ったこと、および入力の時刻表が前提にする値と入力の形を確かめる。
fn assert_frozen_defaults_and_input_shape(envelope: &Value) {
    let config = &envelope["config"];
    assert_eq!(
        config["config_source"], "frozen",
        "★ 凍結既定で走っていない: {config}"
    );
    assert_eq!(
        config["overrides"],
        json!([]),
        "★ 凍結値から外れたキーがある: {config}"
    );
    assert_eq!(config["pole"], "baseline", "極は既定の baseline: {config}");

    // ⚠️ 入力の時刻表はこの値から手で導いた。凍結値が変わったら、入力の側を導き直すこと
    // （★ 別の理由で「restop が測れない」ことに見えるのを、ここで名指しで止める）。
    assert_eq!(config["w_ms"], 30_000, "{config}");
    assert_eq!(config["b_ms"], 30_000, "{config}");
    assert_eq!(config["q"], 0.99, "{config}");
    assert_eq!(config["hole_gap_ms"], 2_000, "{config}");
    assert_eq!(config["warmup_count"], 100, "{config}");
    assert_eq!(config["net_diff_min"], 1, "{config}");

    // ★ `feat` 行に穴が 1 つも無い（観測区間が 1 本）。穴があると条件 A の連続が切れ、
    //   restop が測れない理由が入力の側に移る。
    assert_eq!(
        envelope["provenance"]["observed_intervals"],
        json!([{
            "a_ms": SESSION_START_MS + FEAT_FIRST_OFFSET_MS,
            "b_ms": SESSION_START_MS + FEAT_LAST_OFFSET_MS,
        }]),
        "観測区間が想定と違う（入力に穴がある）"
    );
}

/// onset が立った行（`stall_onset.is_onset == true`）だけを返す。
fn onset_rows(envelope: &Value) -> Vec<&Value> {
    envelope["rows"]
        .as_array()
        .expect("rows is an array")
        .iter()
        .filter(|row| row["stall_onset"]["is_onset"] == true)
        .collect()
}

/// AC1 / AC3: 凍結既定のまま、`restop_ms` が非 null の onset 行が 1 本以上ある。
#[test]
fn restop_is_measurable_under_frozen_defaults() {
    let session = TempSession::write("measurable", &build_session(true));
    let envelope = replay_features(&session);
    assert_frozen_defaults_and_input_shape(&envelope);

    let onsets = onset_rows(&envelope);
    assert!(
        !onsets.is_empty(),
        "onset 行が 1 本も無い（入力が onset を作れていない）"
    );

    // AC3: 凍結既定の下限（warmup_count = 100）を、onset 行が**実際に**満たしている。
    for row in &onsets {
        let n = row["stall_onset"]["theta_sample_n"]
            .as_u64()
            .unwrap_or_else(|| panic!("onset 行に theta_sample_n が無い: {row}"));
        assert!(n >= 100, "theta_sample_n = {n} < warmup_count 100: {row}");
    }

    // AC1: `restop_ms` が非 null の onset 行が 1 本以上。
    let measured: Vec<&&Value> = onsets
        .iter()
        .filter(|row| !row["restart"]["restop_ms"].is_null())
        .collect();
    assert!(
        !measured.is_empty(),
        "★ 凍結既定では restop_ms が全 onset 行で null（restart の非退化が測れていない）: {onsets:#?}"
    );
    // ★ 「非 null」だけでは、別の辺を拾った値でも通る。時刻表から導いた値まで固定する。
    assert_eq!(
        measured[0]["restart"]["restop_ms"], EXPECTED_RESTOP_MS,
        "restop_ms が時刻表（s'_1 - o = 43_600）と違う: {}",
        measured[0]
    );
}

/// AC2: 陰性対照。再停止の沈黙を消した版では `restop_ms` 非 null が 0 本（★ 検査が空振りしていない）。
#[test]
fn restop_absent_without_second_silence() {
    let session = TempSession::write("no-second-silence", &build_session(false));
    let envelope = replay_features(&session);
    assert_frozen_defaults_and_input_shape(&envelope);

    // ⚠️ onset 自体は立っている（1 つ目の沈黙は残してある）。0 本の理由が「onset が無い」ではないこと。
    let onsets = onset_rows(&envelope);
    assert!(
        !onsets.is_empty(),
        "onset 行が 1 本も無い（0 本の理由が onset の欠如になってしまい、対照にならない）"
    );

    let measured: Vec<&&Value> = onsets
        .iter()
        .filter(|row| !row["restart"]["restop_ms"].is_null())
        .collect();
    assert!(
        measured.is_empty(),
        "★ 再停止の沈黙が無いのに restop_ms が測れている（検査が空振りしている）: {measured:#?}"
    );
}
