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
//! 150_000               閉じの打鍵 1 回（★ 最後の入力 = 最後の feat 行。事前宣言 v1.2 の前処理で
//!                       ファイルの最後が削られないようにする）
//! ```
//!
//! ★ `s'_1 = 134_800 <= b = 150_000` なので右側打ち切りにならない。
//!
//! ⚠️ **閉じの打鍵が無いと**（2026-10-08・事前宣言 v1.2 §6.1）: ファイルの最後で、最後の入力
//! （2 つ目の塊の最後の release `104_880`）を含む秒の `feat` 行（`105_000`）より後が落ち、観測区間は `[1_000, 105_000]` に縮む。
//! → `s'_1 = 134_800 > b` で再停止は右側打ち切りになる。これを `frozen_defaults_trim_an_idle_tail` が固定する
//! （前処理が既定で効いていることの、実バイナリでの確かめ）。
//! ★ 閉じの打鍵は 1 つ目の onset の `θ`（`s` より前の対だけを使う）にも、再停止 `s'_1` にも触れない。
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
/// 閉じの打鍵が無いとき、前処理の後に残る最後の `feat` 行（2 つ目の塊の最後の release `104_880` 以上で最初の `feat` 行）。
const TRIMMED_LAST_FEAT_OFFSET_MS: u64 = 105_000;

/// `--features` の入力を作る。`second_silence == false` なら 2 つ目の塊を観測区間の右端まで続ける
/// （★ 陰性対照: 再停止の沈黙だけが無い）。`closing_press` なら `feat` 行の右端に打鍵を 1 回置く
/// （`second_silence == false` では最後の打鍵が既に右端にあるので置かない）。
fn build_session(second_silence: bool, closing_press: bool) -> String {
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
    if second_silence && closing_press {
        push_press(FEAT_LAST_OFFSET_MS, BURST1_PRESSES + burst2_presses);
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
    assert_eq!(config["idle_trim_min_gap_ms"], 60_000, "{config}");
    assert_eq!(config["idle_trim_max_ms"], 1_800_000, "{config}");

    // ★ 前処理で落ちた `feat` 行が無い（最後の入力が `feat` 行の右端にある）。
    assert_eq!(
        envelope["provenance"]["idle_trim"],
        json!({"dropped_feat_rows": 0, "spans": []}),
        "前処理で行が落ちている（閉じの打鍵が効いていない）"
    );

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
    let session = TempSession::write("measurable", &build_session(true, true));
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
    let session = TempSession::write("no-second-silence", &build_session(false, true));
    let envelope = replay_features(&session);
    assert_frozen_defaults_and_input_shape(&envelope);

    // ⚠️ onset 自体は立っている（1 つ目の沈黙は残してある）。0 本の理由が「onset が無い」ではないこと。
    let onsets = onset_rows(&envelope);
    assert!(
        !onsets.is_empty(),
        "onset 行が 1 本も無い（0 本の理由が onset の欠如になってしまい、対照にならない）"
    );

    // ⚠️ 「明示的な null」と「キーが無い」を区別する。serde_json の添字は欠落キーを `Null` として返すので、
    //   `row["restart"]["restop_ms"].is_null()` だけでは、出力からキー自体が消える退行を「正常な null」として受理してしまう。
    // ★ あわせて、θ の標本数が凍結既定の下限を満たしていること（0 本の理由が「θ が育っていない」ではないこと）。
    for row in &onsets {
        let restop = row
            .get("restart")
            .and_then(|restart| restart.get("restop_ms"));
        assert_eq!(
            restop,
            Some(&Value::Null),
            "onset 行の restart.restop_ms が明示的な null でない（キーの欠落かもしれない）: {row}"
        );
        let n = row["stall_onset"]["theta_sample_n"]
            .as_u64()
            .unwrap_or_else(|| panic!("onset 行に theta_sample_n が無い: {row}"));
        assert!(n >= 100, "theta_sample_n = {n} < warmup_count 100: {row}");
    }

    let measured: Vec<&&Value> = onsets
        .iter()
        .filter(|row| !row["restart"]["restop_ms"].is_null())
        .collect();
    assert!(
        measured.is_empty(),
        "★ 再停止の沈黙が無いのに restop_ms が測れている（検査が空振りしている）: {measured:#?}"
    );
}

/// `gse-replay <session> --features <extra...>` を回し、封筒を返す。
fn replay_features_with(session: &TempSession, extra: &[&str]) -> Value {
    let output = Command::new(env!("CARGO_BIN_EXE_gse-replay"))
        .arg(&session.path)
        .arg("--features")
        .args(extra)
        .output()
        .expect("spawn gse-replay");
    assert!(
        output.status.success(),
        "gse-replay --features {extra:?} が失敗した: {:?}\nstderr:\n{}",
        output.status,
        String::from_utf8_lossy(&output.stderr)
    );
    serde_json::from_slice(&output.stdout).expect("stdout is the feature envelope JSON")
}

/// 事前宣言 v1.2 §6.1: 閉じの打鍵が無いと、凍結既定のままファイルの最後の無入力の `feat` 行が落ち、
/// 観測区間が最後の入力で終わる。★ 前処理が既定で効いていることを、実バイナリで確かめる。
/// ★ 同じ入力に `--set idle_trim_max_ms=0` を渡すと、前処理なし（観測区間は `feat` 行の右端まで）に戻る（対照）。
#[test]
fn frozen_defaults_trim_an_idle_tail() {
    let session = TempSession::write("idle-tail", &build_session(true, false));

    let trimmed = replay_features(&session);
    assert_eq!(trimmed["config"]["overrides"], json!([]));
    assert_eq!(
        trimmed["provenance"]["observed_intervals"],
        json!([{
            "a_ms": SESSION_START_MS + FEAT_FIRST_OFFSET_MS,
            "b_ms": SESSION_START_MS + TRIMMED_LAST_FEAT_OFFSET_MS,
        }]),
        "ファイルの最後の無入力の feat 行が落ちていない"
    );
    let dropped = (FEAT_LAST_OFFSET_MS - TRIMMED_LAST_FEAT_OFFSET_MS) / FEAT_STEP_MS;
    assert_eq!(
        trimmed["provenance"]["idle_trim"],
        json!({
            "dropped_feat_rows": dropped,
            "spans": [{
                "a_ms": SESSION_START_MS + TRIMMED_LAST_FEAT_OFFSET_MS + FEAT_STEP_MS,
                "b_ms": SESSION_START_MS + FEAT_LAST_OFFSET_MS,
            }],
        })
    );
    // ★ 再停止 `s'_1 = 134_800` は区間の右端より後なので、restop は全 onset 行で打ち切りの null になる。
    //   ⚠️ onset が 0 本だと下のループは空振りで通るので、先に 1 本以上あることを確かめる (Codex 指摘 2026-10-09)。
    let trimmed_onsets = onset_rows(&trimmed);
    assert!(
        !trimmed_onsets.is_empty(),
        "前処理ありで onset が 1 本も無い（1 つ目の沈黙の onset は区間の内側に残るはず）"
    );
    for row in trimmed_onsets {
        assert_eq!(
            row.get("restart").and_then(|r| r.get("restop_ms")),
            Some(&Value::Null),
            "区間を縮めたのに restop_ms が測れている: {row}"
        );
    }

    let untrimmed = replay_features_with(&session, &["--set", "idle_trim_max_ms=0"]);
    assert_eq!(
        untrimmed["config"]["overrides"],
        json!([{"key": "idle_trim_max_ms", "frozen": 1_800_000, "value": 0}])
    );
    assert_eq!(
        untrimmed["provenance"]["observed_intervals"],
        json!([{
            "a_ms": SESSION_START_MS + FEAT_FIRST_OFFSET_MS,
            "b_ms": SESSION_START_MS + FEAT_LAST_OFFSET_MS,
        }]),
        "idle_trim_max_ms=0 で前処理なしに戻っていない"
    );
    assert_eq!(
        untrimmed["provenance"]["idle_trim"],
        json!({"dropped_feat_rows": 0, "spans": []})
    );
    let measured: Vec<&Value> = onset_rows(&untrimmed)
        .into_iter()
        .filter(|row| !row["restart"]["restop_ms"].is_null())
        .collect();
    assert_eq!(
        measured.first().map(|row| &row["restart"]["restop_ms"]),
        Some(&json!(EXPECTED_RESTOP_MS)),
        "前処理なしでは時刻表どおりに restop が測れる"
    );
}

/// 事前宣言 v1.3 §7.1: `feat` 行が途切れずに続いても、入力の間が 30 分以上空いた区間の行は凍結既定のまま落ち、
/// 観測区間が 2 本に割れる。★ 同じ入力に `--set idle_trim_input_gap_ms=0` を渡すと、1 本に戻る（対照）。
///
/// 時刻表（セッション開始からの ms）: `feat` 行は 1_000..=2_000_000（1 Hz・穴なし）。打鍵は 1_200（release 1_280）・
/// 1_900_000・2_000_000。1_280 → 1_900_000 の無入力（1_898_720 ms）が 30 分以上なので、1_280 を含む秒の行 2_000 は残し、
/// 3_000..=1_899_000 の 1897 行を落とす。1_900_000 の行（次の打鍵を含む秒）は残る。
/// 長い無入力の前処理の結合テスト用の入力。`feat` 行は `1_000..=feat_last_offset_ms`（1 Hz・穴なし）、
/// 打鍵は `press_offsets_ms`（それぞれ `RELEASE_AFTER_PRESS_MS` 後に release）。
fn build_input_gap_session(feat_last_offset_ms: u64, press_offsets_ms: &[u64]) -> String {
    let at = |offset_ms: u64| SESSION_START_MS + offset_ms;
    let mut events: Vec<(u64, String)> = Vec::new();
    for (i, &offset_ms) in press_offsets_ms.iter().enumerate() {
        let vk = 0x41 + i as u64;
        events.push((
            at(offset_ms),
            json!({"type": "key", "t": at(offset_ms), "vk": vk, "press": true}).to_string(),
        ));
        let release = offset_ms + RELEASE_AFTER_PRESS_MS;
        events.push((
            at(release),
            json!({"type": "key", "t": at(release), "vk": vk, "press": false}).to_string(),
        ));
    }
    for offset_ms in (1_000..=feat_last_offset_ms).step_by(FEAT_STEP_MS as usize) {
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
    events.sort_by_key(|(t, _)| *t);
    let mut lines = vec![
        json!({"type": "meta", "session_start": SESSION_START_MS, "hmm_version": "0.5.0"})
            .to_string(),
        json!({"type": "session_start", "t": SESSION_START_MS}).to_string(),
    ];
    lines.extend(events.into_iter().map(|(_, line)| line));
    let mut body = lines.join("\n");
    body.push('\n');
    body
}

#[test]
fn frozen_defaults_drop_a_long_input_gap_without_a_feat_hole() {
    let at = |offset_ms: u64| SESSION_START_MS + offset_ms;
    let body = build_input_gap_session(2_000_000, &[1_200, 1_900_000, 2_000_000]);
    let session = TempSession::write("input-gap", &body);

    let trimmed = replay_features(&session);
    assert_eq!(trimmed["config"]["overrides"], json!([]));
    assert_eq!(trimmed["config"]["idle_trim_input_gap_ms"], 1_800_000);
    assert_eq!(trimmed["config"]["prereg_version"], "1.2.0");
    assert_eq!(
        trimmed["provenance"]["idle_trim"],
        json!({"dropped_feat_rows": 0, "spans": []}),
        "穴もファイルの最後の無入力も無いので、無入力の末尾の前処理は何も落とさない"
    );
    assert_eq!(
        trimmed["provenance"]["input_gap_trim"],
        json!({
            "dropped_feat_rows": 1897,
            "spans": [{"a_ms": at(3_000), "b_ms": at(1_899_000)}],
        })
    );
    assert_eq!(
        trimmed["provenance"]["observed_intervals"],
        json!([
            {"a_ms": at(1_000), "b_ms": at(2_000)},
            {"a_ms": at(1_900_000), "b_ms": at(2_000_000)},
        ]),
        "長い無入力の区間が観測区間から外れていない"
    );

    let untrimmed = replay_features_with(&session, &["--set", "idle_trim_input_gap_ms=0"]);
    assert_eq!(
        untrimmed["config"]["overrides"],
        json!([{"key": "idle_trim_input_gap_ms", "frozen": 1_800_000, "value": 0}])
    );
    assert_eq!(
        untrimmed["provenance"]["input_gap_trim"],
        json!({"dropped_feat_rows": 0, "spans": []})
    );
    assert_eq!(
        untrimmed["provenance"]["observed_intervals"],
        json!([{"a_ms": at(1_000), "b_ms": at(2_000_000)}]),
        "idle_trim_input_gap_ms=0 で前処理なしに戻っていない"
    );
}

/// 事前宣言 v1.3 §7.1: 無入力の長さは idle trim の**前の**列の境で測る（code-reviewer M-1・2026-10-11）。
///
/// 時刻表: `feat` 行は 1_000..=2_401_000（40 分・穴なし）、打鍵は 1_200（release 1_280）だけ。
/// idle trim はファイルの最後から 30 分（602_000..=2_401_000 の 1800 行）を落とす。後の列の最後は 601_000 になるが、
/// 元の列で測った無入力（1_280 → 2_401_000）は 30 分以上なので、残る 3_000..=601_000（599 行）も本前処理が落とす。
/// ⚠️ 後の列の境で測る誤った配線では、無入力が 10 分に縮んで何も落ちない。
#[test]
fn input_gap_trim_measures_the_tail_against_the_untrimmed_file() {
    let at = |offset_ms: u64| SESSION_START_MS + offset_ms;
    let session = TempSession::write(
        "input-gap-tail",
        &build_input_gap_session(2_401_000, &[1_200]),
    );
    let envelope = replay_features(&session);
    assert_eq!(
        envelope["provenance"]["idle_trim"],
        json!({
            "dropped_feat_rows": 1800,
            "spans": [{"a_ms": at(602_000), "b_ms": at(2_401_000)}],
        })
    );
    assert_eq!(
        envelope["provenance"]["input_gap_trim"],
        json!({
            "dropped_feat_rows": 599,
            "spans": [{"a_ms": at(3_000), "b_ms": at(601_000)}],
        }),
        "境を idle trim の後の列から取っている"
    );
    assert_eq!(
        envelope["provenance"]["observed_intervals"],
        json!([{"a_ms": at(1_000), "b_ms": at(2_000)}])
    );
}
