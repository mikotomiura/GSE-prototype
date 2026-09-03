//! **このビルドが何を記録できるか**を宣言するための単一情報源 (ADR-013 D1 / D2)。
//!
//! ## なぜ要るか
//!
//! ⚠️★★★ 「計器がコホートを跨げなかった」失敗が **2 件**起きている (ADR-013 §Context-1):
//!
//! 1. `keys` / `bs_keys` の配線は 2026-08-16。Phase1 ログはそれ以前なので**存在しない**。
//! 2. `hook_health` / `starved_ms` は Phase1 コホート (63 ファイル) に **1 行も無い**
//!    (記録期間 2026-07-04〜07-24 に対し `liveness.rs` の追加は 2026-08-09 = **収集の 16 日後**)。
//!
//! → ★ 教訓の逐語: **「既存ログにある」は *現行コードが出す* の意味であって、
//! *対象コホートにある* の意味ではない。**
//!
//! ⚠️ これは「規約が無かった」失敗ではない。★ **規約は書いてあったのに適用しなかった**のである。
//! → 人が適用し忘れられる形のままでは 3 件目が起きるので、**ログ自身に刻む**。
//!
//! ## 解析側の機械判定 (ADR-013 D1)
//!
//! | `capabilities` | 該当行の数 | 結論 |
//! |---|---|---|
//! | `unconditional` に有 | 0 行 | ★ **信号が無かった** (測れて、無かった) |
//! | `threshold_gated` に有 | 0 行 | ⚠️★★★ **判定不能** (閾値未達と区別できない) |
//! | 無 | 0 行 | ⚠️ **計器が無かった** (測っていない) ← ★ 2 件の失敗はここ |
//! | 無 | ≥1 行 | ⚠️ **宣言のバグ** → `app_version` で追跡する |
//!
//! ⚠️ **`hmm_version` では代用できない** —— HMM の版であって「何を記録できるか」ではない。
//!
//! ## ⚠️★★★ 導出元は「送出元があるか」であって writer ではない (D2)
//!
//! `LogEntry` の variant / `logger.rs` が書ける行種から導出すると、
//! **macOS で `ime_shadow` を過大申告する** —— variant は両 OS でコンパイルされるが、
//! 送出元は `lib.rs` の `#[cfg(target_os = "windows")] fn emit_ime_shadow` **だけ**である
//! (macOS の `input/ime_macos.rs` は `ImeState` しか送らない)。
//!
//! ⚠️ **過大申告は「計器が無い」を「信号が無い」に化けさせる** ——
//! 本 ADR が防ごうとしている取り違えの、ちょうど裏返しである。
//! → ★ 本モジュールは `#[cfg]` を**反映した**表を持ち、腐りを [`tests`] が機械的に止める。
//!
//! ## ⚠️ 名前が紛らわしいので注意 (★ 2 つの「capabilities」がある)
//!
//! | 何 | 場所 | 意味 |
//! |---|---|---|
//! | **本モジュール** | `src-tauri/src/capabilities.rs` | ★ **収集仕様の自己記述** (`meta.capabilities`)。ADR-013 |
//! | Tauri の権限定義 | `src-tauri/capabilities/` (**ディレクトリ**) | ⚠️ Tauri 2.0 の permission 設定。**無関係** |
//!
//! ★ JSON のフィールド名 `capabilities` は **ADR-013 D1 が凍結している**ので変えない。
//! ⚠️ grep するときは**パスまで見る**こと (`src/capabilities.rs` か `capabilities/` か)。
//!
//! ## ★ OS API は呼ばない
//!
//! `#[cfg]` を見るだけの純粋な宣言表である (先例: `g1.rs`)。
//! `architecture-rules` の「OS 依存は `input/` に閉じる」に抵触しない。

/// NDJSON に現れうる**全**行種 (OS を問わない候補集合)。
///
/// ⚠️ ★ **これは宣言ではない。** 「宣言し忘れ」を検出するための参照点である
/// (実際に宣言するのは [`unconditional`] と [`THRESHOLD_GATED`])。
///
/// ★ `logger.rs` の `"type":"<x>"` リテラルと突き合わせる網羅テストがあるので、
/// 新しい行種を足して**ここへの追加を忘れると赤くなる**。
pub const KNOWN_LINE_TYPES: &[&str] = &[
    "meta",
    "session_start",
    "key",
    "paste",
    "feat",
    "ime_state",
    "ime_shadow",
    "hook_health",
    "starve_window",
    "user_label",
    "review_marker",
    "session_meta",
    "probe_assignment",
    "realtime_label",
    "vignette_response",
    "intervention_decision",
    "intervention_response",
    // ⚠️★★★ O1 (R3): 被験者が記録を止めた / 再開した遷移 (ADR-014 D7-ii)。
    "recording_pause",
    // ⚠️★★★ O1 (R3-a): 非打鍵チャネル (ADR-014 D4 の段 1)。
    //   ★ `secure_input` は **macOS 専用**。⚠️★★★ **2026-09-03 訂正: 旧コメント
    //   「まだ送出元が無い (`observe_macos.rs` はスタブ)」は失効している。**
    //   ★ 送出元は 2026-08-24 に実装済み (`observe_macos.rs` の 1Hz ポーリング。下記
    //   `SECURE_INPUT_AVAILABLE` 分岐と同ファイル L211 のコメントが正)。
    //   ⚠️ Windows は相当 API が無く計器を持てない (`observe_windows.rs` の
    //   `SECURE_INPUT_AVAILABLE = false`)。→ ★ **0 行の意味が OS で違う**。
    //   ⚠️ 陳腐化したまま残ると、提出文書の「macOS は実装済み」と食い違って見える
    //   (★ security-checker L-3 で顕在化した)。
    "focus_transition",
    "pointer_bin",
    "secure_input",
];

/// **閾値ゲート付き**の行種 (ADR-013 D1)。
///
/// ⚠️★★★ この群では **0 行は「信号が無かった」を意味しない**。
/// `hook_health` は状態変化時にしか出ず (`lib.rs`)、`starve_window` は
/// `n_lt30 == 0` の窓を出さないので、★ **閾値未達と信号皆無を区別できない**。
///
/// ⚠️ `unconditional` と同じ集合に混ぜてはならない ——
/// **本 ADR が防ごうとした取り違えを、判定表が再導入する** (code-reviewer HIGH)。
pub const THRESHOLD_GATED: &[&str] = &["hook_health", "starve_window"];

/// **設定で丸ごと止まる**行種 (⚠️ 2026-08-19 追加・code-reviewer HIGH)。
///
/// ⚠️★★★ **これを `unconditional` に入れてはならない。**
/// `unconditional` は「0 行 ＝ **信号が無かった**（測れて、無かった）」と読まれる群である。
/// ★ ところが次の 2 つは**設定で送出元ごと止まる**:
///
/// | 行種 | 止まる条件 | 実測 |
/// |---|---|---|
/// | `probe_assignment` / `realtime_label` | ⚠️ **G1 実施中は常に止まる** | `lib.rs`: `probes_disabled = disabled_by_env \|\| disabled_by_g1.is_some()` |
/// | `intervention_decision` / `intervention_response` | ⚠️ **盲検較正 (`intervention_enabled=false`) では常に止まる** | `lib.rs`: `if !INTERVENTION_ENABLED { return safe_default(); }` |
///
/// → ⚠️★★★ **G1 ログを D1 の判定表に掛けると `probe_assignment` 0 行が
/// 「信号が無かった」という *偽の結論* になる。** ★ しかもこれは「計器が無い」より質が悪い
/// —— **測ったふりをする**からである。
///
/// ★ `threshold_gated` を分けた理屈（「0 行は判定不能」）は、閾値だけでなく
/// **設定ゲート**にもそのまま当てはまる。→ **第 3 群として分ける。**
///
/// ⚠️★★★ **2026-08-22 追加: `ime_shadow` もここに入る**（★ 実測で判明）。
///
/// ★ `ime_shadow` は `IME_ACTIVE` が `true` になったときにだけ出る。
/// ⚠️★ **2026-08-23 訂正**: 旧文は「その `true` を書くのは
/// **`hook_windows.rs` の WinEvent コールバック 1 か所だけ**である」と書いていたが、
/// ★ 現在は **2 か所**ある —— 文書化された `EVENT_OBJECT_IME_*` 経路と、
/// **cloak/uncloak 経路** (`input/ime_cloak.rs` + `ime_windows.rs::spawn_cloak_resolver_thread`)。
/// ⚠️ 2 つは `hook.rs::LEGACY_IME_EVENT_MS` で**排他**にしてある (同時には駆動しない)。
/// ⚠️★★★ ところが実機計測（2026-08-22・`examples/ime_winevent_probe.rs`）で
/// **`EVENT_OBJECT_IME_SHOW/HIDE/CHANGE`(0x8027-0x8029) が 60 秒間 1 件も飛ばない**ことが分かった
/// —— 同じ時間に `TEXTSELECTIONCHANGED` 298 件・`VALUECHANGE` 246 件・
/// `CREATE`/`DESTROY` 各 680 件が飛んでおり、**日本語入力は確かに行われていた**。
/// ★ この Windows 11 の IME は候補 UI を**汎用イベント**で表現し、MSAA の IME イベントを上げない。
///
/// → ⚠️ **`ime_shadow` は「環境（IME / アプリ）によって丸ごと出ない」**。
/// ★ `unconditional`（0 行 ＝ 信号が無かった）に置くと **「測れて、無かった」という偽の結論**になる。
/// ⚠️ これは ADR-013 が防ごうとした**過大申告**そのものである。
///
/// ⚠️ **「原理的に不可能」ではない**（別の IME / アプリなら上がりうる）ので、
/// ★ `config_gated`（**0 行は判定不能**）が正しい群である。
///
/// ⚠️★★★ **2026-08-22 追試: 「WinEvent の代わりに EnumWindows で駆動する」案は潰れた。**
/// ★ `ime_windows.rs` には検出の第 2 経路 (`is_ime_candidate_window_visible`) があり、
/// これは生きているので **`IME_ACTIVE` の駆動源をそちらへ移せば `ime_shadow` が復活する**
/// ように見える。⚠️ **実機で測ったら 0 だった。**
///
/// ★ **実測 (60 秒 × 2 回・2 回目の値)**:
/// **検出 0 / 2400 回 (0.0%)・立ち上がり 0**、本番相当の 100ms 間引きでも **0 / 600**。
/// ★ 同時に取った可視トップレベル窓のセンサスに **`Candidate` を含むクラス名は 1 件も無い**。
///
/// ⚠️★★★ **「候補 UI がトップレベル窓に無い」とまでは実測できていない。**
/// ★ 対立仮説がある —— `Windows.UI.Core.CoreWindow` が **600/600 で常時可視**かつ
/// 窓レベル `SHOW` 20 件 / `HIDE` 0 件であり、これは
/// 「候補 UI は**常駐トップレベル窓**で、表示/非表示ではなく **DWM の cloak/uncloak** で
/// 出入りしている」とも整合する（⚠️ `IsWindowVisible` は cloaked な窓に **TRUE** を返す）。
///
/// ★ **ただし結論は対立仮説のどちらでも変わらない**:
/// - 仮説 A（トップレベル窓に無い）→ `EnumWindows` は列挙対象外なので**見えない**。
/// - 仮説 B（常駐窓を cloak している）→ **常時可視なので可視性が信号を運ばない。**
///   ⚠️ そのクラス名を網に入れると**常時 true** になり、
///   `excludes_language_bar_and_imm32_system_window` が固定した
///   **「分析が永久停止する」事故を再発させる。**
///
/// → ★ **どちらにせよ `IsWindowVisible` ＋ クラス名では変換中と非変換中を分離できない。**
/// ★ つまり第 2 経路は「まだ試していない当て」ではなく、**試して外れた当て**である。
///
/// # ⚠️★★★ 2026-08-23: cloak 経路を入れた。**それでも `config_gated` は据え置く**
///
/// ★ 上の「仮説 B（常駐窓を cloak している）」が **実測で確定した**
/// (`findings-enumwindows-probe.md` §15-16)。→ ★ `IME_ACTIVE` を
/// `EVENT_OBJECT_CLOAKED`/`UNCLOAKED` ＋ クラス完全一致 `IME` で駆動し直し、
/// **`ime_shadow` は実際に出るようになった**。
///
/// ⚠️★★★ **それでも `unconditional` へは戻さない。** 理由:
///
/// | # | ⚠️ 未解決 |
/// |---|---|
/// | 1 | ★ **1 台・1 アプリでしか確認していない。** 被験者環境で再現するかは未検証 |
/// | 2 | ⚠️ cloak が飛ぶのは**候補ウィンドウが出るとき**であって、ローマ字入力中ではない —— ★ 「変換しない打ち方」の被験者では 0 行になりうる |
/// | 3 | ⚠️ macOS には送出元が構造的に無い (`emit_ime_shadow` が Windows 限定) |
///
/// → ★ **0 行は依然「判定不能」であって「信号が無かった」ではない。**
/// ⚠️ 複数台で再現を確認するまで `config_gated` のまま据え置く。
///
/// ★ 詳細: `.steering/20260821-workspace-behavior-triage/findings-instrument-defects.md`
/// ★ EnumWindows 追試: `.steering/20260822-ime-active-rewiring/findings-enumwindows-probe.md`
/// ★ cloak 経路の復旧: `.steering/20260823-ime-active-cloak-rewiring/`
pub fn config_gated() -> Vec<&'static str> {
    let mut v = vec![
        "probe_assignment",
        "realtime_label",
        "intervention_decision",
        "intervention_response",
    ];
    // ⚠️ ★ 送出元 (`emit_ime_shadow`) が Windows 限定なので、宣言も Windows 限定にする (D2)。
    #[cfg(target_os = "windows")]
    v.push("ime_shadow");

    // ⚠️★★★ **O1 (R3-a) の非打鍵チャネルは `config_gated` に置く。**
    //
    // ★ なぜ `unconditional` ではないのか:
    // - ⚠️ 計器の設置は**実行時に失敗しうる** (`SetWinEventHook` / `RegisterRawInputDevices`)。
    //   → ★ `unconditional` に置くと、設置に失敗した端末の 0 行が
    //   **「測れて、無かった」という偽の結論**になる (`ime_shadow` を移した理由と同型)。
    // - ⚠️ `pointer_bin` は**ゼロ抑制**されるので、そもそも「無活動 = 0 行」である。
    // → ★ **0 行は判定不能**、が正しい読みである。
    //
    // ⚠️ 宣言は **`observe` 側の実装有無と 1 対 1** にする (★ 過大申告を作らない)。
    if crate::input::observe::FOCUS_AVAILABLE {
        v.push("focus_transition");
    }
    if crate::input::observe::POINTER_AVAILABLE {
        v.push("pointer_bin");
    }
    // ⚠️★★★ 2026-08-24: macOS 側の送出元を実装したので `SECURE_INPUT_AVAILABLE` を見て push する。
    if crate::input::observe::SECURE_INPUT_AVAILABLE {
        v.push("secure_input");
    }

    v.sort_unstable();
    v
}

/// ⚠️ ★ **`meta` 行自身**。[`unconditional`] に載せない (その行がこの `meta` なので)。
/// ★ production では参照しない (載せない、という**不在**の宣言なので) — テストだけが使う。
#[cfg(test)]
const SELF_LINE_TYPE: &str = "meta";

/// このビルドで**送出元が実在し、閾値ゲートが無い**行種。
///
/// ⚠️★★★ **`ime_shadow` はここに入らない** —— [`config_gated`] へ移した (2026-08-22)。
pub fn unconditional() -> Vec<&'static str> {
    let mut v = vec![
        "key",
        "feat",
        "paste",
        "ime_state",
        "session_start",
        "session_meta",
        "user_label",
        "review_marker",
        "vignette_response",
        // ⚠️★★★ O1 (R3): `recording_pause` は **`unconditional`** である。
        //   ★ 0 行 = 「**一度も止めなかった**」と読んでよい (`paste` と同じ形)。
        //   ⚠️ `config_gated` に置くと「止めたかどうか判定不能」になり、
        //   ★ **被験者が消した区間と信号が無い区間の区別**という本行の存在理由が消える。
        "recording_pause",
    ];
    // ⚠️★★★ **2026-08-22: `ime_shadow` はここから [`config_gated`] へ移した。**
    //   ★ 実機計測で「環境によって丸ごと出ない」ことが分かったため
    //   (0 行を「信号が無かった」と読ませてはならない)。
    v.sort_unstable();
    v
}

/// アプリの版。
///
/// ⚠️★★★ **粗い semver のみ**を刻む (ADR-013 D6 / security-checker LOW)。
/// ★ git SHA / ビルドホスト名 / ビルド時刻 / マシン GUID / OS ビルド番号は
/// **フィンガープリントになる**ので入れない。
///
/// ## ★ なぜ要るか (本 ADR の発案ではない)
///
/// `experiments/20260801-controlled-friction-task/notes.md:1865` 逐語:
/// 「`hook_health` 行の存在は **v0.1.25 以降**を意味するだけで、v0.1.25 と v0.1.26 を分けない
/// (`liveness.rs` の導入コミットは**両方のタグに含まれる**)。…
/// **アプリ版を `meta` に刻んでいれば機械的に答えが出た。**」
/// → ★ G1 では「版の特定はできなかった」という**回復不能な情報損失**として現れた。
pub fn app_version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

/// `meta`(session_start) 行に埋め込む `capabilities` オブジェクトの JSON 断片。
///
/// ★ `logger.rs` は float 桁固定のため手書き `writeln!` で NDJSON を組む。
/// ここも同じ流儀で文字列を返す (serde を通さない)。
///
/// ⚠️ 要素は `&'static str` の固定語彙だけなので、**エスケープが要る文字は入りえない**
/// (外部由来の文字列がここへ来る経路を作らないこと)。
pub fn capabilities_json() -> String {
    let quoted = |xs: &[&str]| {
        xs.iter()
            .map(|s| format!("\"{s}\""))
            .collect::<Vec<_>>()
            .join(",")
    };
    format!(
        r#"{{"unconditional":[{}],"threshold_gated":[{}],"config_gated":[{}]}}"#,
        quoted(&unconditional()),
        quoted(THRESHOLD_GATED),
        quoted(&config_gated())
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::BTreeSet;

    /// `logger.rs` のソースに現れる `"type":"<x>"` リテラルを全部拾う。
    ///
    /// ⚠️ ★ **既知の限界**: テスト用フィクスチャ内のリテラルも拾うため**過大側に振れる**。
    /// ★ それは「落ちすぎる」方向であり、**見落とす方向ではない**ので受け入れる (ADR-013 D3-1)。
    fn line_types_in_logger_source() -> BTreeSet<String> {
        const NEEDLE: &str = r#""type":""#;
        // ⚠️★★ **NDJSON の行を書くのは `logger.rs` だけ**という不変条件に依存している
        //   (code-reviewer LOW・2026-08-19)。★ 他のファイルが行を書き始めると
        //   本テストの網から**素通り**するので、その不変条件を下の
        //   [`ndjson_rows_are_written_only_by_logger`] で明示的に固定してある。
        let src = include_str!("logger.rs");
        let mut found = BTreeSet::new();
        let mut rest = src;
        while let Some(i) = rest.find(NEEDLE) {
            rest = &rest[i + NEEDLE.len()..];
            if let Some(end) = rest.find('"') {
                found.insert(rest[..end].to_string());
            }
        }
        found
    }

    fn declared() -> BTreeSet<&'static str> {
        unconditional()
            .into_iter()
            .chain(THRESHOLD_GATED.iter().copied())
            .chain(config_gated())
            .collect()
    }

    /// ★ ADR-013 D3-1 (網羅): `logger.rs` が書ける行種が `KNOWN_LINE_TYPES` から漏れていたら落ちる。
    ///
    /// ⚠️ **これが今回の失敗 (「新しい行種を足したのに宣言を更新し忘れる」) を止める仕掛けである。**
    #[test]
    fn capabilities_covers_every_line_type() {
        let known: BTreeSet<&str> = KNOWN_LINE_TYPES.iter().copied().collect();
        let missing: Vec<_> = line_types_in_logger_source()
            .into_iter()
            .filter(|t| !known.contains(t.as_str()))
            .collect();
        assert!(
            missing.is_empty(),
            "logger.rs が書く行種が KNOWN_LINE_TYPES に無い: {missing:?}\n\
             ★ 行種を足したら capabilities.rs の表も更新すること (ADR-013 D3-1)。"
        );
    }

    /// ⚠️★★★ **NDJSON の行を組み立てるのは `logger.rs` だけ**であることを固定する
    /// (code-reviewer LOW・2026-08-19)。
    ///
    /// ★ [`capabilities_covers_every_line_type`] は `logger.rs` しか走査しない。
    /// → ⚠️ 他のファイルが `{"type":"…"}` を書き始めると、**網羅テストの網から素通り**し、
    /// 「宣言し忘れ」を止められなくなる (＝ 本 ADR の失敗様式が戻る)。
    /// ★ そこで**不変条件そのものをテストにする**。
    ///
    /// ⚠️ 破るときは、走査対象を配列にして両方を見るように直してから破ること。
    #[test]
    fn ndjson_rows_are_written_only_by_logger() {
        // ★ **書き手**の目印は `format!` のエスケープ `{{` である
        //   (`writeln!(w, r#"{{"type":"key",…"#)`)。
        //   ⚠️ **読み手**と混同しないこと —— `packaging.rs` / `reconcile.rs` は
        //   `contains(r#""type":"meta""#)` のように**単一の `{`** で照合しており、
        //   それは行を書いていない (★ 一度これで誤検出した)。
        const NEEDLE: &str = r#"{{"type":""#;
        for (name, src) in [
            ("lib.rs", include_str!("lib.rs")),
            ("submission.rs", include_str!("submission.rs")),
            ("reconcile.rs", include_str!("reconcile.rs")),
            ("packaging.rs", include_str!("packaging.rs")),
        ] {
            assert!(
                !src.contains(NEEDLE),
                "{name} が NDJSON の行種リテラルを持っている。\
                 ★ 行を書くのは logger.rs だけ、という前提が壊れた \
                 (capabilities の網羅テストが素通りする)。"
            );
        }
    }

    /// ★ ADR-013 D3-3b (過大申告の逆アサート): 宣言した行種には**必ず writer がある**。
    ///
    /// ⚠️ **既知の限界**: これは「writer がある」ことしか言わない。
    /// ★ **OS ごとの送出元の有無**は下の対のテスト
    /// ([`ime_shadow_is_declared_only_where_its_emitter_is_compiled`]) が固定する。
    /// ⚠️ さらに「送出元が実在してもバグで一度も呼ばれない」可能性は残る
    /// (ADR-013 Consequences 逐語) → ★ だから `app_version` を併記する。
    #[test]
    fn every_capability_has_a_reachable_emitter() {
        let in_source = line_types_in_logger_source();
        for t in declared() {
            assert!(
                in_source.contains(t),
                "capabilities に {t:?} を宣言しているが logger.rs に writer が無い \
                 (＝過大申告・ADR-013 D3-3b)"
            );
        }
    }

    /// ⚠️★★★ 宣言集合が `KNOWN_LINE_TYPES` を**過不足なく**割ることを固定する。
    ///
    /// ★ `KNOWN = unconditional ∪ threshold_gated ∪ {meta} ∪ (このビルドで送出元が無いもの)`。
    /// ⚠️ 右辺の最後の集合を `#[cfg]` で書き下すので、**OS ごとの過大/過小申告が両方向で落ちる**。
    #[test]
    fn declaration_partitions_known_line_types() {
        // ⚠️★★★ `secure_input` は **Windows には送出元が無い** (Windows に
        //   `EnableSecureEventInput` 相当の API が存在しない・`observe_windows.rs` は常に `None`)。
        #[cfg(target_os = "windows")]
        let emitterless: &[&str] = &["secure_input"];
        // ⚠️ macOS には `emit_ime_shadow` (Windows 限定) が無い。`ime_macos.rs` は `ImeState` だけを送る。
        //   ★ 2026-08-24: O1 の非打鍵チャネル (`focus_transition`/`pointer_bin`/`secure_input`) は
        //   macOS 側の送出元を実装したので、この行から外した (`observe_macos.rs`)。
        #[cfg(not(target_os = "windows"))]
        let emitterless: &[&str] = &["ime_shadow"];

        let mut lhs: BTreeSet<&str> = declared();
        lhs.insert(SELF_LINE_TYPE);
        lhs.extend(emitterless.iter().copied());

        let known: BTreeSet<&str> = KNOWN_LINE_TYPES.iter().copied().collect();
        assert_eq!(lhs, known, "宣言集合が KNOWN_LINE_TYPES を割り切っていない");
    }

    /// ★ ADR-013 D3-2 (OS 対): `ime_shadow` は **Windows でのみ**宣言される。
    ///
    /// ⚠️ 根拠は `docs/agent-shared.md` 逐語「**OS ごとに規則が違うロジックは両 OS に対のテストを置く**」
    /// (★ 2026-08-10 に macOS 前提のテストが Windows CI で赤になった実績がある)。
    ///
    /// ★ 併せて **送出元の `#[cfg]` そのもの**をソースで確かめる ——
    /// 宣言と実装が別々に動いて食い違う経路を塞ぐ (ADR-013 §Context-4)。
    #[test]
    fn ime_shadow_is_declared_only_where_its_emitter_is_compiled() {
        // ⚠️★★★ 2026-08-22: 宣言先を `unconditional` から `config_gated` へ移した
        //   (実機計測で「環境によって丸ごと出ない」ことが判明したため)。
        //   ★ このテストが見るのは **OS との整合**であって群ではないので、
        //   `declared()`（3 群の合併）で判定する。
        let declared_here = declared().contains("ime_shadow");
        assert_eq!(
            declared_here,
            cfg!(target_os = "windows"),
            "ime_shadow の宣言が OS と食い違っている (ADR-013 D2/D3-2)"
        );

        // ★ 送出元が本当に Windows 限定で書かれていることを、ソースの実物で確かめる。
        // ⚠️ 改行コードに依存しないよう、直前の数十文字を見る形にしてある。
        let lib_src = include_str!("lib.rs");
        let at = lib_src
            .find("fn emit_ime_shadow(")
            .expect("emit_ime_shadow が lib.rs に無い");
        // ⚠️ ★ **バイト数で切らない** —— 直前は日本語コメントなので、
        //   `at - 48` が文字境界に落ちず panic する (2026-08-19 に実際に踏んだ)。
        let head = &lib_src[..at];
        let start = head
            .char_indices()
            .rev()
            .take(48)
            .last()
            .map(|(i, _)| i)
            .unwrap_or(0);
        let preceding = &head[start..];
        assert!(
            preceding.contains(r#"#[cfg(target_os = "windows")]"#),
            "emit_ime_shadow の直前から #[cfg(target_os = \"windows\")] が消えた。\
             ★ capabilities の宣言も見直すこと (ADR-013 D2)。直前の文字列: {preceding:?}"
        );
    }

    /// ⚠️ 3 群は互いに素であること (混ぜると判定表が壊れる・ADR-013 D1)。
    #[test]
    fn capability_groups_are_disjoint() {
        let u: BTreeSet<&str> = unconditional().into_iter().collect();
        for t in THRESHOLD_GATED.iter().copied().chain(config_gated()) {
            assert!(!u.contains(&t), "{t:?} が unconditional と重複している");
        }
        for t in config_gated() {
            assert!(
                !THRESHOLD_GATED.contains(&t),
                "{t:?} が threshold_gated と重複している"
            );
        }
        assert_eq!(u.len(), unconditional().len(), "unconditional に重複がある");
        assert!(
            !u.contains(SELF_LINE_TYPE),
            "meta 行自身を capabilities に載せてはならない (ADR-013 D1)"
        );
    }

    /// ⚠️★★★ **設定で止まる行種を `unconditional` に置かない** (code-reviewer HIGH・2026-08-19)。
    ///
    /// ★ `unconditional` は「0 行 ＝ **信号が無かった**」と読まれる群である。
    /// ⚠️ G1 では probe 系が、盲検較正では intervention 系が **設定で丸ごと止まる**ので、
    /// そこに置くと **G1 ログが「測れて、無かった」という偽の結論**を機械的に出す。
    /// → ★ **「計器が無い」より質が悪い** (測ったふりをする)。
    #[test]
    fn config_gated_line_types_are_not_declared_unconditional() {
        let u: BTreeSet<&str> = unconditional().into_iter().collect();
        for t in [
            "probe_assignment",      // ⚠️ G1 実施中は probes_disabled で常に 0 行
            "realtime_label",        // ⚠️ 同上
            "intervention_decision", // ⚠️ intervention_enabled=false で常に 0 行
            "intervention_response", // ⚠️ 同上
        ] {
            assert!(
                !u.contains(t),
                "{t:?} は設定で止まるので unconditional に置いてはならない"
            );
            assert!(config_gated().contains(&t), "{t:?} が config_gated に無い");
        }
    }

    /// ⚠️★★★ **`ime_shadow` を `unconditional` に戻させない** (2026-08-22)。
    ///
    /// ★ 実機計測（`examples/ime_winevent_probe.rs`）で、この Windows 11 の IME が
    /// **`EVENT_OBJECT_IME_SHOW/HIDE/CHANGE` を 1 件も上げない**ことが分かった
    /// （⚠️ 同じ 60 秒に `TEXTSELECTIONCHANGED` 298 件・`VALUECHANGE` 246 件が飛んでおり、
    /// **日本語入力は確かに行われていた**）。
    /// → ⚠️ `IME_ACTIVE` が `true` にならず `ime_shadow` は **0 行**になる。
    ///
    /// ★ `unconditional` に置くと「**測れて、無かった**」という**偽の結論**を機械的に出す。
    /// ⚠️ ADR-013 が防ごうとした**過大申告**そのものである。
    #[test]
    #[cfg(target_os = "windows")]
    fn ime_shadow_is_config_gated_not_unconditional() {
        let u: BTreeSet<&str> = unconditional().into_iter().collect();
        assert!(
            !u.contains("ime_shadow"),
            "ime_shadow を unconditional に戻してはならない (0 行が「信号が無かった」と誤読される)"
        );
        assert!(
            config_gated().contains(&"ime_shadow"),
            "ime_shadow が config_gated に無い (0 行は判定不能でなければならない)"
        );
    }

    /// ⚠️ macOS には `emit_ime_shadow` が無いので、**どの群にも宣言しない**。
    #[test]
    #[cfg(not(target_os = "windows"))]
    fn ime_shadow_is_not_declared_on_non_windows() {
        assert!(
            !declared().contains("ime_shadow"),
            "macOS に送出元が無い ime_shadow を宣言してはならない (ADR-013 D2)"
        );
    }

    /// ★ `app_version` は**粗い semver** であること (D6)。
    ///
    /// ⚠️ git SHA / ホスト名 / GUID が紛れ込む改変を落とす。
    #[test]
    fn app_version_is_a_coarse_semver() {
        let v = app_version();
        let parts: Vec<_> = v.split('.').collect();
        assert_eq!(parts.len(), 3, "app_version は x.y.z 形式であること: {v}");
        for p in parts {
            assert!(
                !p.is_empty() && p.chars().all(|c| c.is_ascii_digit()),
                "app_version に数字以外が入っている (フィンガープリント禁止・D6): {v}"
            );
        }
    }

    /// ★ JSON 断片の形を固定する (キー順を含む)。
    #[test]
    fn capabilities_json_shape_is_stable() {
        let j = capabilities_json();
        assert!(j.starts_with(r#"{"unconditional":["#), "{j}");
        assert!(
            j.contains(r#""threshold_gated":["hook_health","starve_window"],"config_gated":["#),
            "{j}"
        );
        assert!(j.contains(r#""feat""#) && j.contains(r#""key""#), "{j}");
        // ⚠️ エスケープが要る文字が語彙に入っていないこと。
        assert!(
            !j.contains('\\'),
            "capabilities に要エスケープ文字が入った: {j}"
        );
    }
}
