//! O1 (R3-a・自然作業の常時収集) の「O1 モード」判定と、そのモードでだけ変わる方針
//! (OS API 非依存)。
//!
//! ## なぜこのモジュールがあるか
//!
//! O1 は `docs/adr/ADR-014` D5 の「在席の連続タイムライン」を取りに行く形成的トラックで、
//! ⚠️★★★ **研究者判断 O1-1 / ADR-016 判断 4b-0 が「(B) 常時収集」を確定させた** ——
//! 逐語「`session_active` の門を R3 で外し、**「開始する」の押下に依存せず記録を続ける**」。
//!
//! ⚠️ しかし 2026-08-25 の grep 時点で **R3/O1 用のモードマーカーは 1 つも存在しなかった**。
//! → ★ 本モジュールは `g1.rs` の 2 経路 (フォルダのマーカー ＋ 環境変数) を**そのまま写す**。
//!
//! ★ `g1.rs` と同じく **判定だけをここに置き、効果は `lib.rs` が適用する**。
//!
//! ## ⚠️★★★ なぜ「門を外す」実装が要るのか (★ 2026-08-25 に実測した非対称)
//!
//! | | ⚠️ 押し忘れの帰結 | ★ 判定量への波及 |
//! |---|---|---|
//! | (A) 押下あり | ⚠️★★★ **打鍵だけが静かに欠ける** (分析スレッドが `start_session` まで入力を捨てる)。★ ポインタ / フォーカスは**記録され続ける** (門を通っていない) | ⚠️★★★ その区間が事前登録 §2.2 の「打鍵ゼロ かつ ポインタ活動あり」＝ **非打鍵区間の定義に合致**し、**計器の欠損と非打鍵作業を事後に区別できない** |
//! | **(B) 常時収集** | ★ **ラベルだけが古くなる** (記録は欠けない) | ★ 事後層別の質が下がるのみ。**判定量は壊れない** |
//!
//! ## ⚠️ 起動時に 1 回だけ読む
//!
//! `g1.rs` と同じ理由で **実行時トグルにしてはならない**。O1 では「常時収集するかどうか」が
//! ロガーのファイル名 (`gse_o1_*`) と提出経路 (猶予つき自動提出) を決めるので、
//! ⚠️ 途中で切り替わると **同じ収集期間のファイルが 2 通りの規則で名付けられる**。

use std::path::{Path, PathBuf};

use crate::g1::G1Source;

/// フォルダに置くマーカーのファイル名。★ `g1.mode` の鏡像。
pub const MARKER_FILE_NAME: &str = "o1.mode";

/// ⚠️★★★ **日次ローテートの間隔** (判断 O1-2 の実施条件 1)。
///
/// ★ `write_meta_end` (`session_end`) は **Rotate / BlockEnd (G1 限定) / アプリ終了**でしか
/// 書かれない (`logger.rs`)。⚠️ O1 は「開始する」を押さないので、**アプリを終了しない被験者の
/// ファイルは何日も開いたままになり、提出候補にならない** (`reconcile` は `session_end` を持つ
/// ファイルしか触らない)。→ ★ **閉じるためにローテートする。**
///
/// ## ⚠️ なぜ「ローカル深夜 0 時」ではないのか
///
/// ★ ローカル時刻の取得は OS 呼び出しを要し (repo に `chrono` は無く、
/// `logger::chrono_like_filename` は **UTC 近似**である)、⚠️ **UTC の深夜は JST の 09:00** ——
/// ★ 就業時間の真ん中でローテート ＋ `engine.reset()` が走る。
/// → ★ 「**開いてから 24 時間**」なら「1 日 1 本」は同じく保証され、TZ の曖昧さが 1 つも無い。
pub const ROTATE_AFTER_MS: u64 = 24 * 60 * 60 * 1000;

/// ⚠️★★★ **自動提出までの猶予** (研究者判断 O1-2 / ADR-014 D8 の上書き)。
///
/// ★ **これは UX の都合ではなく「削除保証」を守るための機構である。**
/// `delete_time_range` → `redact_dir` は **ローカルの `gse_*.ndjson` だけ**を書き換え、
/// ⚠️ **`.age` (提出物) は対象外**である (`redaction.rs`)。→ ★ **包んだ時点で呼び戻せない。**
/// 猶予が無いと、ADR-014 **判断 3 の根拠 3**「被験者が停止・削除できる」が
/// 送信済み分について崩れる。
///
/// ⚠️★★★ **48 時間は repo に無い数字であり、恣意的である。**
/// (★ 7 日なら同意文書 §6-2 の既存値と揃った。) 研究者判断で 48 時間と決めた。
/// → ★ **恣意的であることを事前登録と同意文書に明記し、後から動かさない。**
/// ⚠️ **縮める / 外す変更は ADR-014 判断 3 の再検討を伴う** (`data-privacy` ルール 6)。
pub const SUBMIT_GRACE_MS: u64 = 48 * 60 * 60 * 1000;

/// O1 モードを立てた引き金。★ `G1Source` の鏡像。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum O1Source {
    /// 実行ファイルを包むフォルダに `o1.mode` があった (配布形)。
    Marker,
    /// 環境変数 `GSE_O1_MODE=1` が立っていた (開発・検証用)。
    Env,
}

impl O1Source {
    /// 診断ログに書く固定文字列。
    ///
    /// ⚠️★★★ **NDJSON の `meta` 行には出さない** (本セッションは schema を変えない)。
    /// ★ O1 かどうかは **ファイル名 (`gse_o1_*`)** が表す。理由は `design.md` D-1。
    pub fn as_str(self) -> &'static str {
        match self {
            O1Source::Marker => "marker",
            O1Source::Env => "env",
        }
    }
}

/// 環境変数による O1 モード判定 (純関数)。
///
/// ★ `"1"` に**完全一致**したときだけ立てる。⚠️ `g1::g1_enabled_by_env` と
/// **意図的に同じ厳しさ**にしてある: `"true"` / `"yes"` / `" 1"` を通すと
/// 「立てたつもり」が生まれ、★ O1 では**数日〜数週間ぶんの記録が丸ごと通常モードで取られる**。
pub fn o1_enabled_by_env(value: Option<&str>) -> bool {
    matches!(value, Some("1"))
}

/// `exe` に対応するマーカーの想定パス (純関数)。
///
/// ★ 階層数は **`g1::exe_to_folder_levels()` を再利用する**。
/// ⚠️ 複製すると macOS のバンドル階層が変わったとき片方だけ直り、**無音で失敗する**
/// (★ `g1` と `o1` は同層の純判定モジュールなので、`architecture-rules` ルール 1 が
/// 禁じている「層をまたぐ直接依存」には当たらない)。
pub fn marker_path_for(exe: &Path, levels_up: usize) -> Option<PathBuf> {
    Some(crate::g1::folder_up(exe, levels_up)?.join(MARKER_FILE_NAME))
}

/// O1 モードの判定 (純関数)。IO は呼び出し側が行い、その結果だけを渡す。
///
/// ★ **マーカーを優先**する (`g1::decide` と同じ理由: 配布形が既定の経路である)。
pub fn decide(marker_exists: bool, env_value: Option<&str>) -> Option<O1Source> {
    if marker_exists {
        Some(O1Source::Marker)
    } else if o1_enabled_by_env(env_value) {
        Some(O1Source::Env)
    } else {
        None
    }
}

/// ⚠️★★★ **G1 と O1 を同時に立てない** (純関数)。
///
/// ★ **G1 が勝つ。** 理由は選好ではなく**取り返しのつかなさの非対称**である:
///
/// - G1 は `preregistration.md §3.6` が **ブロックの事後除外を禁じている**ので、
///   1 ブロックの取りこぼしが**回復不能な損失**になる。
/// - ⚠️ 対して O1 は数日〜数週間の連続収集であり、1 日落ちても**次の日で埋まる**。
///
/// ★ **起動そのものは止めない。** ⚠️ 列挙の失敗や設定ミスで G1 の実施を潰すほうが害が大きい
/// (`g1::other_instance_running` が「止めるのではなく画面に出す」と決めたのと同じ倒し方)。
/// → ★ 呼び出し側が `tracing::error!` で必ず残す。
pub fn resolve(g1: Option<G1Source>, o1: Option<O1Source>) -> Option<O1Source> {
    if g1.is_some() {
        None
    } else {
        o1
    }
}

/// 両方のマーカーが立っていたか (★ 呼び出し側が **必ず** ログに残すための述語)。
pub fn modes_conflict(g1: Option<G1Source>, o1: Option<O1Source>) -> bool {
    g1.is_some() && o1.is_some()
}

// ---------------------------------------------------------------------------
// (B) 常時収集 — 門と稼働中インジケータ
// ---------------------------------------------------------------------------

/// ⚠️★★★ **分析スレッドが入力を処理してよいか** (純関数・判断 4b-0)。
///
/// ★ 現行の門は `lib.rs` の `if !session_active { while rx.try_recv().is_ok() {} ... }` であり、
/// **`LogEntry::Key` はこのループの中でしか出ない**。
/// → ⚠️ O1 で門を外さないと **打鍵チャネルが丸ごと空になる**。
///
/// ⚠️★ **非 O1 では `session_active` そのもの**である。
/// ★ G1 / Phase1 の観測可能な挙動は 1 バイトも変わらない。
pub fn analysis_gate_open(o1_mode: bool, session_active: bool) -> bool {
    o1_mode || session_active
}

/// ⚠️★★★ **自己ラベル (「今とても詰まっている」) を記録してよいか** (純関数)。
///
/// ★ O1 では **記録しない**。⚠️ 理由は `lib.rs` が O1 でグローバルショートカットを
/// 登録しない判断と**同一**である。起動ログ逐語:
///
/// > `global shortcuts are NOT registered (… could write user_label / review_marker rows
/// >  that **the consent form does not list**)`
///
/// ## ⚠️ なぜ純関数に切り出すか
///
/// ★ `O1_MODE` は `OnceLock` なので、テストから O1 / 非 O1 を切り替えられない。
/// → ⚠️ 判定を `is_o1()` の呼び出し地点に埋め込むと **両方の分岐を検査できない**
///   (★ `analysis_gate_open` / `decide_probe_init` と同じ理由・同じ形)。
///
/// ## ⚠️ 経緯 (2026-08-30)
///
/// ★ 旧実装は **ホットキーだけ**を塞ぎ、Dashboard のボタンは素通りだった。
/// ⚠️ 実機の画面を見るまで気づかず、**機械検査は 1 つも捕まえなかった**
/// (配布ゲート 19/19・`--selftest` 19/0 とも緑)。
pub fn self_marker_allowed(o1_mode: bool) -> bool {
    label_row_allowed(o1_mode)
}

/// ⚠️★★★ **被験者由来のラベル行を記録してよいか** (純関数・2026-08-31)。
///
/// ★ 対象は `user_label` / `realtime_label` / `review_marker` / `vignette_response` ——
/// ⚠️ **どれも O1 の同意文書が列挙していない行型**である。
///
/// ## ⚠️★★★ `activity_label` はここに**入れない**（2026-09-14・security-checker MEDIUM）
///
/// ★ 本関数は「**同意文書が列挙していないから O1 では通さない**」という門である。
/// ⚠️ ところが `activity_label`（6 択 ESM）は **O1 で取ると研究者が決めた**ものなので、
/// ★ 同じ門に入れると「通す」側へ倒すことになり、**門の意味が反転する**。
///
/// → ★★★ **代わりに [`activity_label_allowed`] を別に置く。**
/// ⚠️ そちらは `o1_mode` **だけでは通さない** —— ★ **同意の承認**と対にする
/// （`check-o1-release-readiness.sh` の承認マーカと 1 対 1）。
/// ★ いまは producer が無いので fail-closed だが、⚠️ **M5 で「O1 だから通す」と
/// 書かれると、同意承認と結びつかない穴になる。**
///
/// ## ⚠️ なぜ 1 つにまとめるのか
///
/// ★ 2026-08-30 に `record_self_marker` **だけ**に門を置いたが、
/// ⚠️ security-checker が「**兄弟コマンドが素通り**」であることを指摘した (2026-08-31)。
/// ★ 実測で確認（`#[tauri::command]` 直後の関数だけを数えた）:
///
/// ```text
/// record_user_label         ⚠️ 門なし
/// record_realtime_answer    ⚠️ 門なし
/// record_realtime_skip      ⚠️ 門なし
/// record_vignette_response  ⚠️ 門なし
/// record_self_marker        ✅ 門あり   ← ここだけ塞いだ
/// ```
///
/// → ⚠️ **1 つだけ塞ぐと「塞いだつもり」になる。** ★ 判定を 1 か所に集めて共有する。
///
/// ## ⚠️ 現時点の到達性（★ 正直に書く）
///
/// ★ O1 ではプローブが 1 件も出ない（`probe_assignment` を実機 3 セッションで **0 行**確認）ので、
/// `realtime_*` は UI からは呼ばれない。`record_user_label` は `src/` からの参照が **0 件**。
/// → ⚠️ **いま被験者に実害が出る経路は無い。**
///
/// ★ それでも門を置く理由は、この判断を最初に採ったときと**同じ**である ——
/// ⚠️ **UI 側だけの対処は、次に UI をいじった人が黙って穴を開け直す。**
/// ★ 実際に 2026-08-30 の事故がその形だった（ホットキーは塞いだのにボタンが残った）。
pub fn label_row_allowed(o1_mode: bool) -> bool {
    !o1_mode
}

/// ⚠️★★★ **6 択 ESM（`activity_label`）を記録してよいか**（純関数・2026-09-14）。
///
/// ★ ADR-031 **D1 / D5 保証 3**、ADR-043 D8。⚠️ 段 1 のモードだけでは通さない ——
/// **本人が問いに同意した印**を対にする。
///
/// ## ⚠️★★★ 2026-11-06 に引数の意味を変えた（M5 の 1 本目・`.steering/20261106-gse-m5-s1-core/`）
///
/// 旧版は `(o1_mode, consent_approved)` だった。M5 で 6 択を出すのは **段 1**（O1 の上に載る層・`s1.rs`）
/// だけであり、素の O1 では出さない（ADR-043 D8・O1 の同意文書は 6 択を列挙していない）。
/// → ★ 第 1 引数は `s1::is_s1()`、第 2 引数は `submission::s1_probe_consent_acknowledged()`
/// （登録の画面で本人が問いへの同意の項目を押したときだけ書かれる印・計画の判断 5）。
/// ⚠️ 式（`a && b`）は変えていない。**`o1::is_o1()` を渡すと O1 の全員で通ってしまう。**
///
/// ## ⚠️ なぜ `label_row_allowed` と分けるのか
///
/// ★ あちらは「**同意が列挙していないから O1 では通さない**」（`!o1_mode`）。
/// ⚠️ `activity_label` は **段 1 で取ると決めたもの**なので、同じ式に混ぜると
/// **門の意味が反転する**（★ 通す側へ倒れる）。
///
/// ## ⚠️★★★ 呼び出し側へ（★ ADR-031 M5）
///
/// ★ `consent_ack` は**ビルド時の定数や `true` 直書きにしない**（実行時の事実だけ）。
/// ★ 他の参加者向けの配布物では、段 1 の同意文書の承認の印を配布物のゲートが求める（M5 の 3 本目）。
pub fn activity_label_allowed(stage1_mode: bool, consent_ack: bool) -> Option<EsmConsent> {
    (stage1_mode && consent_ack).then_some(EsmConsent(()))
}

/// ⚠️★★★ **6 択 ESM を記録してよいことの「証拠」**（★ 2026-09-14・`/cross-review` HIGH-2）。
///
/// ## ★ なぜ `bool` ではなく型なのか
///
/// ⚠️ `bool` を返すだけだと、**門を通したことを誰も強制できない**。
/// ★ `/cross-review`（Codex）の逐語指摘:
///
/// > 「`grep -q 'activity_label_allowed('` は **『同じファイルに一度でも呼ばれている』ことしか見ません**。
/// > 実際の `activity_label_answered/skipped` の各送出経路が必ずその戻り値でガードされている
/// > 保証はありません。**無関係な場所に `activity_label_allowed(true, true);` があれば通ります。**」
///
/// → ★★★ **したがって「検査で守る」のをやめ、*型で守る*。**
/// ★ 本型は [`activity_label_allowed`] からしか作れず（⚠️ フィールドが private な unit struct）、
/// **`LogEntry::activity_label_*` が参照を要求する**ので、
/// ★ **門を通さずに 6 択 ESM の行を構築することはコンパイルできない。**
///
/// ⚠️ **残る抜け道**: `LogEntry::ActivityLabel { .. }` を直接構築する経路は Rust の
/// pub variant の性質上塞げない。→ ★ そちらは `capabilities` の
/// `activity_label_has_no_emitter_until_it_is_wired` と
/// `check-o1-release-readiness.sh` の送出元検査が二重に見る。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct EsmConsent(());

/// ⚠️★★★ **いま記録しているか** (純関数)。稼働中インジケータと `liveness` の両方が使う。
///
/// ## なぜ `session_active` と分けるのか
///
/// ★ O1 では `session_active` が **永久に false** である (「開始する」を押さないので)。
/// ⚠️ そのまま `tray::measure_state` に渡すと、逐語
/// 「**GSE — 停止中（記録していません）**」を出しながら**実際には記録し続ける**。
/// → ★ **同意文書 §4 の逐語「印が出ていないときは記録していません」と正面から矛盾する。**
///
/// ⚠️ 同じ理由で `liveness::step` にも渡す: そちらは `!session_active` で `starved_ms` を
/// **0 に落とす**ので、O1 では**フックの死が永久に検出されない**
/// (★ mac の `CGEventTap` 失効が無検出になる)。
///
/// ## ⚠️ 非 O1 で `paused` を見に行かない理由
///
/// ★ Phase1 / G1 の表示挙動を 1 バイトも変えないため。
/// (⚠️ 現行は一時停止中でも「計測中」と出る。★ 直す価値はあるが**本タスクの範囲外**である。)
pub fn recording_active(o1_mode: bool, session_active: bool, paused: bool) -> bool {
    if o1_mode {
        !paused
    } else {
        session_active
    }
}

// ---------------------------------------------------------------------------
// 宣言の変更 (判断 4b-1)
// ---------------------------------------------------------------------------

/// 宣言 (`task_kind`) が 1 回変わったときにログをどうするか。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DeclarationAction {
    /// ★ **O1 ではない。** 宣言 UI 自体が出ないので、ここへ来たら呼び出し側の誤りである。
    NotO1,
    /// ★ 前を閉じて新しいファイルを開き、そこへ宣言を書く。
    /// ⚠️ **G1 のブロック数 (`G1_BLOCKS_STARTED`) は数えない。**
    RotateAndDeclare,
}

/// 宣言変更 1 回の扱いを決める**純関数**。
///
/// ## ⚠️★★★ なぜローテートが要るのか (★ 2026-08-25 実測)
///
/// - `gse-replay` は **1 ファイルに相異なる `task_kind` が 2 つ以上あると `Err` で落ちる**
///   (`bin/replay.rs`)。⚠️ 非 G1 はローテートしないので、1 本のファイルに全部積まれる。
/// - ⚠️ `engine.reset()` をしないと **新ファイル先頭 30 秒の `feat` 行が前ファイルの状態に依存**し、
///   ★ **replay が本番を再現しない** (Replay-as-Truth の破れ)。
///
/// ## ⚠️ なぜ `g1::decide_start_action` に枝を足さないのか
///
/// ★ `decide_start_action` は **「開始する」押下 (`start_session`) 専用**の判定である。
/// ⚠️ O1 は `start_session` を通らない (通すと `SESSION_START_MS` が立ってプローブが動き、
/// `record_session_meta` が走って**未宣言を表せなくなる** = 判断 4b-3 の破れ)。
/// → ★ G1 の enum と関数に O1 の引数を通すと **G1 の分岐が O1 を知る**ことになる。
/// ⚠️ 「分岐はすべて O1 モードの中に閉じる」を守るため、**判定はこちらに置く**。
pub fn decide_declaration_action(o1_mode: bool, g1_mode: bool) -> DeclarationAction {
    // ⚠️ 二重の安全網。`resolve` が既に排他にしているが、呼び出し側が
    //   生の検出結果を渡してもここで落ちる。
    if !o1_mode || g1_mode {
        return DeclarationAction::NotO1;
    }
    DeclarationAction::RotateAndDeclare
}

// ---------------------------------------------------------------------------
// 日次ローテート
// ---------------------------------------------------------------------------

/// いまのファイルを閉じてローテートすべきか (純関数)。
///
/// ⚠️★ **時計の巻き戻しで発火させない。** NTP 補正・手動の時刻変更で `now_ms < opened_at_ms`
/// になりうるので `saturating_sub` を使う (★ 巻き戻ったときは「まだ経っていない」に倒れる)。
/// ★ `SystemTime` 由来の epoch ms を使うので、**スリープ / 休止も経過に含まれる**
/// (`Instant` だと OS によっては止まる)。
pub fn should_rotate_daily(opened_at_ms: u64, now_ms: u64, rotate_after_ms: u64) -> bool {
    now_ms.saturating_sub(opened_at_ms) >= rotate_after_ms
}

/// ⚠️★ **O1 定期再送の周期**（G-2・2026-09-28・研究者判断）: 6 時間。
///
/// ★ 送信は起動時と日次ローテート時にしか走らなかったので、回線断で失敗した `.age` が
/// 次のきっかけ（最長 24 時間）まで残っていた。⚠️ 1 時間にしなかったのは、送るものが無くても
/// 毎回 子プロセスの起動・NDJSON の読み込み・ロックの書き込みが走るため。
pub const PERIODIC_RECONCILE_MS: u64 = 6 * 60 * 60 * 1000;

/// 定期再送を回す時刻か (純関数・G-2)。
///
/// ★ `last_ms` は直近に収束器を回した時刻（起動時・ローテート時・定期のどれでも）。
/// ⚠️ **時計が巻き戻ったら（`now_ms < last_ms`）真を返す** —— 偽にすると、巻き戻った幅だけ
/// 再送が止まる。★ 収束器はべき等なので、余分に 1 回回っても害は無い（呼び出し側が基準を引き直す）。
pub fn periodic_reconcile_due(last_ms: u64, now_ms: u64) -> bool {
    now_ms < last_ms || now_ms - last_ms >= PERIODIC_RECONCILE_MS
}

/// 閉じたファイルを提出候補にしてよいか (純関数)。
///
/// ⚠️★★★ **`session_end` からの経過で測る** (ファイルの mtime ではない)。
/// ★ mtime は退避・コピー・ウイルス対策ソフトの走査で動きうるので、
/// **記録の中身に書かれた時刻**を真とする。
///
/// ⚠️ 巻き戻し時は `saturating_sub` で 0 になり、**まだ包まない**に倒れる
/// (★ 安全側 = 被験者が消せる時間を短くしない)。
pub fn grace_elapsed(session_end_ms: u64, now_ms: u64, grace_ms: u64) -> bool {
    now_ms.saturating_sub(session_end_ms) >= grace_ms
}

// ---------------------------------------------------------------------------
// セッションファイル名 (⚠️ schema を変えずに O1 を表す唯一の手段)
// ---------------------------------------------------------------------------

/// O1 で書いたセッション NDJSON のファイル名接頭辞。
///
/// ## ⚠️★★★ なぜ `meta` 行ではなくファイル名なのか
///
/// ★ **本来は `g1_mode` と同じく `meta` 行に刻むほうが強い** (事後検証ができる)。
/// ⚠️ しかしそれは `schema_dto.rs` → `schema/current.json` の変更を伴い、
/// **gse-dataset との parity 更新**が要る。本タスクは「schema を 1 バイトも変えない」制約下にある。
/// → ★ **研究者へ返す論点として `.steering/00000000-o1-collection-enablement/decisions.md` に残す。**
///
/// ★ 失敗様式は同じく fail-loud である: マーカーが外れれば `gse_<ts>.ndjson` になり、
/// ⚠️ **提出候補から外れて研究者に届かない** (無音で増えることはない)。
pub const SESSION_FILE_PREFIX: &str = "gse_o1_";

/// このファイル名が O1 のセッションか (純関数)。
///
/// ⚠️ 派生ファイル (`.anon.ndjson`) は除く —— `reconcile` / `redaction` の既存判定と揃える。
pub fn is_o1_session_file_name(name: &str) -> bool {
    name.starts_with(SESSION_FILE_PREFIX)
        && name.ends_with(".ndjson")
        && !name.ends_with(".anon.ndjson")
}

/// ⚠️★★★ **この提出物 (`.age`) が O1 のものか** (純関数)。
///
/// ## なぜ要るか (★ code-reviewer / security-checker が**一致して**指摘・2026-08-27)
///
/// `submission::unsent_age_files` は **ファイル名が `<participant>_block<NN>_….age` か**
/// だけで絞り、⚠️ **中身が G1 か O1 かを見ていない**。
/// ★ 提出物フォルダは participant 単位の**共有ディレクトリ**なので、
/// 同じ端末・同じ ID で **G1 を先にやった被験者が「送信する」を押さずに残した `.age`** が、
/// ⚠️★★★ **O1 の収束で承認なしに送られる** —— D-14 の承認ゲートが O1 経由で無効化され、
/// **別研究の同意範囲のデータが送られる**。
///
/// → ★ `closed_o1_sessions` が `g1_mode` を弾いているのと**対**になる排他を送信側にも置く。
///
/// ★ 判定材料は `submission::age_file_name` が名前に**元の stem を残している**ことである
/// (`<participant>_block<NN>_<stem>.age`・台帳が消えても対応づけを復元するための設計)。
pub fn is_o1_age_file_name(name: &str) -> bool {
    name.ends_with(".age") && name.contains(&format!("_{SESSION_FILE_PREFIX}"))
}

// ---------------------------------------------------------------------------
// ⚠️★★★ 孤児セッションの回収 (2026-09-03・引き継ぎ ④)
// ---------------------------------------------------------------------------

/// ⚠️★★★ **これより古い「現在時刻」は壊れているとみなす** (2020-01-01T00:00:00Z)。
///
/// ★ 孤児回収は `session_end` に現在時刻を書く。⚠️ 時計が壊れて `0` / `1` が来ると
/// **猶予が最初から経過済み**になり、削除保証がゼロになる。→ ★ 閉じずに見送る。
/// ⚠️ O1 の収集は 2026 年に始まるので、この境界が正当な値を弾くことはない。
pub const MIN_PLAUSIBLE_EPOCH_MS: u64 = 1_577_836_800_000;

/// ⚠️★★★ **これより新しい「現在時刻」も壊れているとみなす** (2040-01-01T00:00:00Z)。
///
/// ★ 時計が未来にずれた状態で 1 回でも閉じると、⚠️ **未来の `session_end`** が書かれ、
/// 以後 sweep は「閉じている」と見送り (べき等)、`grace_elapsed` も永久に偽になる ——
/// ★ **静かに提出されないまま固定する** (⚠️ fail-silent。cross-review MEDIUM)。
/// → ★ 閉じずに **fail-loud** で見送る (⚠️ 閉じないのは「今までどおり」なので後退しない)。
///
/// ⚠️ 固定値なので 2040 年以降は常に赤になるが、★ O1 の収集は 2026 年の研究であり、
/// **そのころには本コードは無い**。⚠️ 万一残っていたら `tracing::error!` で必ず目に付く。
pub const MAX_PLAUSIBLE_EPOCH_MS: u64 = 2_208_988_800_000;

/// ⚠️★★★ **時計の高水位マーク**を置くファイル名（★ セッション置き場に置く）。
///
/// ★ `gse_` で始まらないので、`reconcile` / `packaging` / `redaction` の走査
/// (`name.starts_with("gse_")`) には**構造的に掛からない**。
/// ⚠️ 中身は epoch ms が 1 行だけ。★ 被験者を特定できるものは 1 バイトも書かない。
pub const CLOCK_HWM_FILE_NAME: &str = ".o1_clock_hwm";

/// 今の時計が O1 の記録に使える範囲（[`MIN_PLAUSIBLE_EPOCH_MS`]〜[`MAX_PLAUSIBLE_EPOCH_MS`]）にあるか（純関数）。
pub fn clock_is_plausible(now_ms: u64) -> bool {
    (MIN_PLAUSIBLE_EPOCH_MS..=MAX_PLAUSIBLE_EPOCH_MS).contains(&now_ms)
}

/// 高水位（[`CLOCK_HWM_FILE_NAME`]）より古い時計を待つ回数の上限（1 秒に 1 回で 10 分）。
///
/// 高水位は前にしか動かないので、一度でも未来へずれた時計で書かれると、上限なしでは
/// その時刻まで起動しなくなる（判断 4）。範囲の外の待ちには上限を置かない（判断 2）。
pub const HWM_WAIT_MAX_SLEEPS: u64 = 600;

/// [`wait_for_plausible_clock`] の結果。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ClockWait {
    /// 眠った回数（範囲の外の待ちと高水位の待ちの合計）。
    pub slept: u64,
    /// 高水位の待ちを上限で打ち切り、高水位より古い時計のまま始めた。
    pub gave_up_below_hwm: bool,
}

/// 時計が範囲に入り、前回の高水位にも追いつくまで待つ（高水位の待ちは [`HWM_WAIT_MAX_SLEEPS`] まで）。
///
/// 2026-11-22、この Mac の起動直後の数分、時計が 1976 年になっていた。O1 はその時刻で記録を開き、
/// 段 1 の無作為の枠の起点も 1976 年になった。時計が合った最初の 1 秒で、調停器が 50 年分の候補を
/// 1 つずつ離席として抑え、1,907,310 行の `probe_suppressed` を書いた（208 MB）。
/// → 記録のファイル名・起点・`meta` を決める前に、ここで待つ（`.steering/20261123-clock-jump-gate/`）。
///
/// 範囲の内でも、前回の起動の高水位より古い時計（ファームウェアの既定日など）は同じ追いかけを起こすので待つ。
/// `on_wait` は眠り終えるたびに、眠った回数と眠る前に読んだ時刻を受ける（警告の間引きは呼び出し側）。
pub fn wait_for_plausible_clock(
    hwm: Option<u64>,
    mut now_ms: impl FnMut() -> u64,
    mut sleep: impl FnMut(),
    mut on_wait: impl FnMut(u64, u64),
) -> ClockWait {
    let mut slept = 0u64;
    let mut hwm_sleeps = 0u64;
    loop {
        let now = now_ms();
        let below_hwm = hwm.is_some_and(|h| now < h);
        if clock_is_plausible(now) {
            if !below_hwm || hwm_sleeps >= HWM_WAIT_MAX_SLEEPS {
                return ClockWait {
                    slept,
                    gave_up_below_hwm: below_hwm,
                };
            }
            hwm_sleeps += 1;
        }
        sleep();
        slept += 1;
        on_wait(slept, now);
    }
}

/// セッション置き場 `dir` の時計の高水位を読む（無い・壊れていれば `None`）。
pub fn clock_hwm_in(dir: &Path) -> Option<u64> {
    read_clock_hwm(&dir.join(CLOCK_HWM_FILE_NAME))
}

/// 高水位の待ちを打ち切ったときの、その高水位の値を置くファイル名（セッション置き場に置く）。
///
/// 高水位は孤児の回収が書き、時計がそれより古いと書き直さない。一度未来の値が書かれると下がらず、
/// 起動のたびに 10 分待つことになる。→ 打ち切った値を覚え、高水位が同じ値の間は待たない（判断 5）。
/// `gse_` で始まらないので、提出・削除の走査には掛からない。中身は epoch ms が 1 行だけ。
pub const CLOCK_HWM_GAVE_UP_FILE_NAME: &str = ".o1_clock_hwm_gave_up";

/// 打ち切りを覚えた高水位の値を読む（無い・壊れていれば `None`）。
pub fn clock_hwm_gave_up_in(dir: &Path) -> Option<u64> {
    read_clock_hwm(&dir.join(CLOCK_HWM_GAVE_UP_FILE_NAME))
}

/// 高水位の待ちを打ち切ったことを覚える。
pub fn record_clock_hwm_gave_up(dir: &Path, hwm: u64) -> std::io::Result<()> {
    std::fs::write(dir.join(CLOCK_HWM_GAVE_UP_FILE_NAME), format!("{hwm}\n"))
}

/// 待つべき高水位（純関数）。前に打ち切った値と同じなら待たない（`None`）。
pub fn hwm_to_wait_for(hwm: Option<u64>, gave_up: Option<u64>) -> Option<u64> {
    match (hwm, gave_up) {
        (Some(h), Some(g)) if h == g => None,
        _ => hwm,
    }
}

/// ⚠️★★★ 行の分類規則は **`crate::ndjson_scan` が単一真実源**である。
///
/// ★ 2026-09-03 の cross-review で、同じ規則が `packaging` / `reconcile` / ここの
/// **3 か所に手書きコピーされていて食い違っていた**ことが実測された（詳細は
/// `ndjson_scan` の module doc）。→ ⚠️ **ここで判定を書き直さないこと。**
use crate::ndjson_scan;

/// NDJSON 1 本の「形」。★ `meta` 行の形と「データ行があるか」だけを見る。
///
/// ⚠️ **打鍵の内容も時刻も解釈しない** (`data-privacy`)。★ `reconcile::closed_o1_session_end`
/// と**同じ弁別子**を持つ (⚠️ 片方だけ緩めると「収束器は O1 と認めないのに、こちらは閉じる」
/// という食い違いが静かに生まれる)。
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub struct O1SessionShape {
    /// `meta` 行に `o1_mode` がある = **記録の中身が O1 だと言っている** (R-1)。
    pub has_o1_mode: bool,
    /// `meta` 行に `g1_mode` がある = G1 の記録である。
    pub has_g1_mode: bool,
    /// `session_start` 行がある = **「開始する」を押した記録** = O1 ではない。
    pub has_session_start: bool,
    /// `meta.session_end` がある = **もう閉じている**。
    pub has_session_end: bool,
    /// `meta` 以外の行がある = 中身がある。
    pub has_data_row: bool,
}

/// ★ この形のファイルを「開いたまま残った O1 セッション」として閉じてよいか (純関数)。
///
/// ⚠️ **5 つ全部**が要る。★ どれを外しても、他の研究の記録・空ファイル・二重クローズの
/// いずれかを踏む。
pub fn is_closable_orphan(shape: &O1SessionShape) -> bool {
    shape.has_o1_mode
        && !shape.has_g1_mode
        && !shape.has_session_start
        && !shape.has_session_end
        && shape.has_data_row
}

/// NDJSON を 1 パス走査して [`O1SessionShape`] を得る。
///
/// ⚠️ **1 行の読み取り失敗で諦めない** (`reconcile.rs:294` と同じ倒し方)。★ 強制終了だと
/// 最終行が途中で切れていることがあり、そこで諦めると**回収したいファイルほど回収できない**。
fn scan_session_shape(path: &Path) -> Option<O1SessionShape> {
    use std::io::BufRead;
    let f = std::fs::File::open(path).ok()?;
    let mut shape = O1SessionShape::default();
    for line in std::io::BufReader::new(f).lines() {
        let line = match line {
            Ok(l) => l,
            Err(_) => continue,
        };
        if line.trim().is_empty() {
            continue;
        }
        if ndjson_scan::is_session_start_row(&line) {
            shape.has_session_start = true;
        }
        // ⚠️★★★ **`packaging::has_any_data_row` と同じ規則**でなければならない
        //   (★ `hook_health` / `ime_state` はデータ行に数えない)。
        //   ⚠️ ここが緩いと、**収束器が絶対に提出しないファイル**に `session_end` を書く
        //   ことになる（★ 2026-09-03 の code-reviewer が実測で見つけた HIGH）。
        if ndjson_scan::is_data_row(&line) {
            shape.has_data_row = true;
        }
        if !ndjson_scan::is_meta_row(&line) {
            continue;
        }
        if line.contains(ndjson_scan::NEEDLE_G1_MODE) {
            shape.has_g1_mode = true;
        }
        if line.contains(ndjson_scan::NEEDLE_O1_MODE) {
            shape.has_o1_mode = true;
        }
        // ⚠️★★★ **「文字列が在るか」ではなく「数値が取れるか」で見る**
        //   (★ `reconcile::closed_o1_session_end` と同じ規則)。
        //   ⚠️ 強制終了が `write_meta_end` の途中に当たり `…"session_end":` で切れた行を
        //   「閉じている」と読むと、★ sweep は永久に見送り・収束器は数値を取れず、
        //   **そのファイルは恒久的に提出候補外**になる —— ⚠️ 本実装が塞ごうとしている
        //   クラッシュ経路そのものである（★ 2026-09-03 の code-reviewer MEDIUM）。
        if ndjson_scan::parse_meta_u64(&line, "session_end").is_some() {
            shape.has_session_end = true;
        }
    }
    Some(shape)
}

/// 回収の結果。★ 呼び出し側がログに出すためだけの値。
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub struct OrphanSweep {
    /// ★ 閉じたファイルの本数。
    pub closed: usize,
    /// ⚠️ 閉じようとして**書けなかった**本数 (★ 権限・ディスク)。
    pub failed: usize,
}

/// ⚠️★★★ **起動時に「開いたまま」残った O1 セッションを閉じる。**
///
/// # なぜ要るか (★ 2026-09-03 にコードで確認した欠陥)
///
/// `meta.session_end` を書くのは `lib.rs` の `shutdown()` だけで、そこへ入るのは
/// **トレイの終了 / main 窓の × / `quit_app`** の 3 経路しか無い。
/// ⚠️ `ExitRequested` / `SIGTERM` / `WM_ENDSESSION` のハンドラは repo に **1 つも無い**。
/// → ★ **GSE をトレイから終了せずに PC を再起動するだけ**で、その日のファイルは
/// `session_end` を持たないまま残り、⚠️ `reconcile` は `session_end` を持つファイルしか
/// 触らないので **永久に提出候補にならない**。
/// ★ 日次ローテートも救わない —— 起点 `O1_LOG_OPENED_MS` は**メモリ上の Atomic** で、
/// 次の起動では**新しいファイル**が開かれるだけである。
///
/// ⚠️ データが消えるわけではない (★ ローカルには残る) が、研究者から見ると
/// 「**記録は取れているのに送られてこない**」、被験者から見ると**何も起きていないように見える**。
/// ★ 強制終了が習慣の人ほど丸ごと欠測するので、⚠️ **母集団に偏りが入る**。
///
/// # ⚠️★★★ なぜ `session_end` に **`now_ms` (検出時刻)** を書くのか
///
/// ★ 「最終データ行の時刻」を書くほうが意味的には正しい。⚠️ **しかしそれは削除保証を壊す。**
/// 猶予は `session_end + SUBMIT_GRACE_MS` で効く (`grace_elapsed`) ので、
/// 3 日前に落ちたファイルに 3 日前の時刻を書くと ★ **次の起動でいきなり包まれて送られ**、
/// 被験者に消す窓が 1 秒も残らない —— ⚠️ ADR-014 **判断 3 の根拠 3** が崩れる。
///
/// → ★ **検出時刻なら、猶予の起点は「被験者が次にアプリを立ち上げた瞬間」**であり、
/// ⚠️ **窓は絶対に短くならない** (★ 常に丸 48 時間ある)。
/// `data-privacy` ルール 6 が禁じているのは「猶予を**縮める / 外す**」変更なので、
/// ★ 伸ばす向きにしか動かない本実装は ADR-014 判断 3 の再検討を要しない。
///
/// ⚠️★★ **代償**: `session_end` が「最後に記録した時刻」ではなくなるので、
/// `session_start`〜`session_end` を観測窓とみなす下流は**実在しない沈黙区間を数える**
/// (★ 実例: `experiments/20260819-silence-presence-decomposition/scripts/extract.py:314`)。
/// ★ 回収されたファイルは `session_end - (最終データ行の t)` が異常に大きいことで**判別できる**。
/// ⚠️ schema には**フィールドを足さない** (`schema_dto.rs` ＋ `schema/current.json` ＋
/// gse-dataset の 3 者同期が要り、配布直前に cross-repo の drift を作るほうが危ない)。
///
/// # 引数
///
/// - `dir` … セッション置き場
/// - `current` … ⚠️ **いま開いているファイル** (★ 絶対に触らない)
/// - `now_ms` … 書き込む `session_end` の値 (= 検出時刻)
///
/// ★ 同時起動は `tauri-plugin-single-instance` が `Builder::build()` の中で殺す
/// (`lib.rs:3731`)。⚠️ プラグインを持たない**旧ビルド**は同時に走りうるが、旧ビルドは
/// O1 ではないので `gse_o1_*` を書かず、`has_o1_mode` で構造的に外れる。
pub fn close_orphaned_sessions(dir: &Path, current: Option<&Path>, now_ms: u64) -> OrphanSweep {
    let mut sweep = OrphanSweep::default();
    // ⚠️★★★ **システム時計が壊れているときは 1 本も閉じない** (fail-closed)。
    //
    // ★ `lib.rs` の `now_epoch_ms()` は失敗時に **`1`** を返し (`epoch_ms()` は `0`)、
    //   ⚠️ そのまま `session_end` に書くと `grace_elapsed(1, now, 48h)` が**必ず真**になり、
    //   ★ **次の収束で即座に包まれて送られる** —— 被験者に消す窓が 1 秒も残らない。
    //   → ⚠️ ADR-014 判断 3 の根拠 3 を、まさに守ろうとしている実装が壊すことになる。
    // ★ 閉じないほうは損失にならない (次の正常な起動で拾われる)。
    if !(MIN_PLAUSIBLE_EPOCH_MS..=MAX_PLAUSIBLE_EPOCH_MS).contains(&now_ms) {
        tracing::error!(
            "O1 orphan sweep: refusing to run; the system clock looks wrong (now_ms={})",
            now_ms
        );
        return sweep;
    }
    // ⚠️★★★ **時計が後ろに飛んだ起動では 1 本も閉じない** (security-checker HIGH・2026-09-03)。
    //
    // ★ 床 (`MIN_PLAUSIBLE_EPOCH_MS`) だけでは **2020 年以降の任意の過去時刻**が通る。
    //   ⚠️ 実際に起きる筋: ノート PC の CMOS 電池が切れ、BIOS 既定日 (2020〜2023) で起動
    //   → sweep が `session_end = 数年前` を書く → NTP が時刻を補正 →
    //   ★ 次の収束で `grace_elapsed` が**真**になり、⚠️ **被験者に消す窓が 1 秒も残らないまま**
    //   `.age` が作られ承認なしに送られる。→ ⚠️ 守ろうとしている当の根拠 3 が破れる。
    //
    // ★ 高水位マークは**前にしか動かさない**。⚠️ 下回る起動では sweep 全体を見送る
    //   (★ 見送りは損失にならない —— 時計が直った次の起動で拾われる)。
    let hwm_path = dir.join(CLOCK_HWM_FILE_NAME);
    if let Some(hwm) = read_clock_hwm(&hwm_path) {
        if now_ms < hwm {
            tracing::error!(
                "O1 orphan sweep: refusing to run; the clock went backwards \
                 (now_ms={} < last seen {}). Nothing was closed.",
                now_ms,
                hwm
            );
            return sweep;
        }
    }
    if let Err(e) = std::fs::write(&hwm_path, format!("{now_ms}\n")) {
        // ⚠️ ★ **書けなくても止めない。** ★ 書けないのは異常だが、
        //   ここで止めると「回収されないまま」が続き、本来の欠陥が残る。
        tracing::warn!(
            "O1 orphan sweep: cannot update the clock high-water mark: {}",
            e
        );
    }
    // ⚠️ ★ 現在パスは**正規化して**比べる。相対 / シンボリックリンクで
    //   すり抜けると、書きかけのファイルに `session_end` を書くことになる。
    let current_canonical = current.and_then(|p| std::fs::canonicalize(p).ok());
    let entries = match std::fs::read_dir(dir) {
        Ok(rd) => rd,
        // ⚠️ 置き場が読めないのは異常だが、★ ここで落ちても記録は続く。次の起動で拾う。
        Err(e) => {
            tracing::warn!("O1 orphan sweep: cannot read {:?}: {}", dir, e);
            return sweep;
        }
    };
    let mut paths: Vec<PathBuf> = entries
        .flatten()
        .filter(|e| e.file_type().map(|t| t.is_file()).unwrap_or(false))
        .map(|e| e.path())
        .filter(|p| {
            p.file_name()
                .and_then(|s| s.to_str())
                .map(is_o1_session_file_name)
                .unwrap_or(false)
        })
        .collect();
    paths.sort();
    for path in paths {
        // ★ 条件 2: いま開いているファイルは触らない。
        if let (Some(cur), Ok(here)) = (current_canonical.as_ref(), std::fs::canonicalize(&path)) {
            if *cur == here {
                continue;
            }
        }
        // ⚠️ ★ canonicalize が使えない環境でも**名前だけでもう一度**弾く (二重の門)。
        if let (Some(cur), Some(here)) = (current.and_then(|p| p.file_name()), path.file_name()) {
            if cur == here {
                continue;
            }
        }
        let shape = match scan_session_shape(&path) {
            Some(s) => s,
            None => continue,
        };
        if !is_closable_orphan(&shape) {
            continue;
        }
        match append_session_end(&path, now_ms) {
            Ok(()) => {
                sweep.closed += 1;
                // ⚠️★ **回収した事実をログに残す** (★ schema を変えない代わりの記録)。
                //   ローカルの `gse-app.log` だけに出る (提出物には載らない)。
                tracing::warn!(
                    "O1 orphan sweep: closed {:?} with session_end={} \
                     (the app did not shut down cleanly last time; \
                      the 48h deletion window starts now)",
                    path.file_name(),
                    now_ms
                );
            }
            Err(e) => {
                sweep.failed += 1;
                tracing::error!(
                    "O1 orphan sweep: cannot close {:?}: {}",
                    path.file_name(),
                    e
                );
            }
        }
    }
    sweep
}

/// 時計の高水位マークを読む。⚠️ 読めない / 壊れているときは `None` (= 検査しない)。
///
/// ★ `None` に倒すのは、⚠️ **初回起動ではマークが存在しない**からである
/// (★ そこで止めると、本欠陥がいつまでも直らない)。
fn read_clock_hwm(path: &Path) -> Option<u64> {
    std::fs::read_to_string(path)
        .ok()?
        .trim()
        .parse::<u64>()
        .ok()
}

/// `{"type":"meta","session_end":<ms>}` を 1 行 append する。
///
/// ⚠️★★ **最終行が改行で終わっていないことがある** (★ 強制終了で書き込みが途中で切れた場合)。
/// そのまま append すると ⚠️ **壊れた行と `meta` 行が 1 行に融合し、`meta` 行が読めなくなる**
/// (= 回収したはずのファイルがまた提出候補から外れる)。→ ★ 先に `\n` を補う。
/// 断片は 1 行のゴミとして残るが、`reconcile` の行読みは 1 行の失敗で諦めない。
fn append_session_end(path: &Path, now_ms: u64) -> std::io::Result<()> {
    use std::io::{Read, Seek, SeekFrom, Write};
    let mut f = std::fs::OpenOptions::new()
        .read(true)
        .append(true)
        .open(path)?;
    let len = f.metadata()?.len();
    let mut needs_newline = false;
    if len > 0 {
        f.seek(SeekFrom::End(-1))?;
        let mut last = [0u8; 1];
        f.read_exact(&mut last)?;
        needs_newline = last[0] != b'\n';
    }
    if needs_newline {
        f.write_all(b"\n")?;
    }
    // ⚠️★★★ **形を手で 2 回書かない。** ★ `logger::write_meta_end` を直接呼ぶ
    //   (2026-09-03 の cross-review MEDIUM: 同じリテラルが 2 か所にあると、
    //   ⚠️ `logger` 側だけ変えたときに **両方緑のまま黙って drift する**)。
    crate::logger::write_meta_end(&mut f, now_ms);
    f.flush()
}

// ---------------------------------------------------------------------------
// 起動時に 1 回だけ確定するモード
// ---------------------------------------------------------------------------

/// O1 モードの引き金。`run()` が起動時に 1 回だけ書き、以後は読み取り専用。
///
/// ⚠️ ★ `g1.rs` と違って **`lib.rs` ではなくここに置く**のは、
/// `logger::default_log_path()` がファイル名を決めるときに読むためである
/// (★ `logger` → `lib` の逆依存を作らない)。
static O1_MODE: std::sync::OnceLock<Option<O1Source>> = std::sync::OnceLock::new();

/// 起動時に 1 回だけモードを確定させる。★ 2 回目以降は**黙って無視する**
/// (⚠️ テストが同一プロセスで複数回呼びうるため `expect` にしない)。
pub fn set_mode(source: Option<O1Source>) {
    let _ = O1_MODE.set(source);
}

/// O1 モードか (引き金つき)。`None` なら通常運用。
pub fn mode() -> Option<O1Source> {
    *O1_MODE.get().unwrap_or(&None)
}

/// O1 モードか (真偽値の近道)。
pub fn is_o1() -> bool {
    mode().is_some()
}

/// ⚠️★★★ **導入ごとの識別子** (`meta` 行の `o1_install_id`・2026-10-07・研究者判断)。
///
/// ★ 目的: 1 人が複数端末で O1 を走らせても、**解析で端末を分けられる**ようにする
/// (端末 A を離れて B で作業した時間を「離脱」と混ぜない・G2 の入力を汚さない)。
///
/// ⚠️★★★ **ハードウェア・MAC・ホスト名・ユーザー名・OS の機械 ID は一切使わない**
/// (ADR-013 D6 は「マシン GUID はフィンガープリントになる」として禁じている)。
/// ★ **導入時に乱数で作った 16 桁の hex** であり、`~/.gse` を消せば別の値になる。
/// ⚠️ 値域を `[0-9a-f]{16}` に閉じるので、**手書き JSON を壊す経路が無い**
/// (`g1_mode` が security review MEDIUM で採った作法と同じ)。
pub const INSTALL_ID_LEN: usize = 16;

/// `s` が導入識別子として妥当か (純関数)。16 桁の小文字 hex だけを通す。
pub fn is_valid_install_id(s: &str) -> bool {
    s.len() == INSTALL_ID_LEN && s.bytes().all(|b| matches!(b, b'0'..=b'9' | b'a'..=b'f'))
}

/// 8 バイトの乱数から導入識別子を作る (純関数。乱数の取得は呼び出し側)。
pub fn install_id_from_bytes(bytes: [u8; 8]) -> String {
    bytes.iter().map(|b| format!("{b:02x}")).collect()
}

static O1_INSTALL_ID: std::sync::OnceLock<Option<String>> = std::sync::OnceLock::new();

/// 起動時に 1 回だけ導入識別子を確定させる。★ 2 回目以降は黙って無視する (`set_mode` と同じ)。
/// ⚠️ 妥当でない値は**保持しない** (`None` にする)。
pub fn set_install_id(id: Option<String>) {
    let _ = O1_INSTALL_ID.set(id.filter(|s| is_valid_install_id(s)));
}

/// 確定済みの導入識別子。O1 でなければ・未確定なら `None`。
pub fn install_id() -> Option<String> {
    O1_INSTALL_ID.get().cloned().flatten()
}

/// 実行環境から O1 モードを検出する (IO あり)。★ `run()` から**起動時に 1 回だけ**呼ぶ。
///
/// マーカーの探索に失敗した場合 (`current_exe()` が取れない・階層が足りない) は
/// **マーカー無しとして扱う** (`g1::detect_from_env` と同じ倒し方)。
pub fn detect_from_env() -> Option<O1Source> {
    let marker_exists = std::env::current_exe()
        .ok()
        .and_then(|exe| marker_path_for(&exe, crate::g1::exe_to_folder_levels()))
        .map(|p| p.is_file())
        .unwrap_or(false);
    let env_value = std::env::var("GSE_O1_MODE").ok();
    decide(marker_exists, env_value.as_deref())
}

#[cfg(test)]
mod tests {
    use super::*;

    /// ⚠️★★★ **6 択 ESM は段 1 かつ本人の同意の印があるときだけ通る**（ADR-031 D1 / D5 保証 3・ADR-043 D8）。
    ///
    /// ★ 2026-11-06 に旧 `activity_label_needs_both_o1_and_consent` を書き換えた（第 1 引数の意味が
    /// O1 から段 1 に変わった）。★ 4 通りすべてを見る（⚠️ 片側だけ見ると「常に false」でも緑になる）。
    #[test]
    fn activity_label_some_only_for_s1_with_ack() {
        assert!(
            activity_label_allowed(true, true).is_some(),
            "★ 段 1 かつ同意の印ありなら通る"
        );
        assert!(
            activity_label_allowed(true, false).is_none(),
            "⚠️★★★ 同意の印が無ければ通さない（★ 被験者向け文書は契約）"
        );
        assert!(
            activity_label_allowed(false, true).is_none(),
            "⚠️ 段 1 でなければ通さない"
        );
        assert!(activity_label_allowed(false, false).is_none());
    }

    /// ⚠️★★★ 素の O1 は、同意の印があっても 6 択を通さない（ADR-043 D8）。
    ///
    /// 第 1 引数に `is_o1()` を渡す書き方を防ぐため、O1 だが段 1 ではない組を名指しで見る。
    /// 呼び出し側が段 1 の判定を渡していることは、送出元を作る M5 の 2 本目で本文の検査に置く。
    #[test]
    fn activity_label_none_for_o1_even_with_consent() {
        let o1_active = true;
        let s1_active = crate::s1::resolve(None, o1_active, false).is_some();
        assert!(!s1_active, "印の無い O1 は段 1 ではない");
        assert!(activity_label_allowed(s1_active, true).is_none());
    }

    use std::path::PathBuf;

    // --- A: 引き金 ---------------------------------------------------------

    /// ⚠️★ `g1_enabled_by_env` と**同じ厳しさ**であること。
    /// ★ 緩めると「立てたつもり」で数週間ぶんが通常モードで取られる。
    #[test]
    fn env_trigger_accepts_only_exact_one() {
        assert!(o1_enabled_by_env(Some("1")));
        for v in ["0", "true", "yes", " 1", "1 ", "", "01"] {
            assert!(!o1_enabled_by_env(Some(v)), "{v:?} を通してはならない");
        }
        assert!(!o1_enabled_by_env(None));
    }

    #[test]
    fn marker_wins_over_env() {
        assert_eq!(decide(true, None), Some(O1Source::Marker));
        assert_eq!(decide(true, Some("1")), Some(O1Source::Marker));
        assert_eq!(decide(false, Some("1")), Some(O1Source::Env));
        assert_eq!(decide(false, Some("0")), None);
        assert_eq!(decide(false, None), None);
    }

    /// ⚠️★★★ **本モジュールの核心の 1 つ: G1 と同時に立たない。**
    ///
    /// ★ 両方のマーカーが置かれた配布フォルダは事故だが、**起きたときに静かに壊れない**
    /// ことが要る。G1 が勝つのは事後除外が禁じられていて取り返しがつかないためである。
    #[test]
    fn g1_and_o1_are_mutually_exclusive() {
        // 両方立っている → O1 を落とす
        assert_eq!(
            resolve(Some(G1Source::Marker), Some(O1Source::Marker)),
            None
        );
        assert_eq!(resolve(Some(G1Source::Env), Some(O1Source::Env)), None);
        assert!(modes_conflict(Some(G1Source::Marker), Some(O1Source::Env)));

        // 片方だけ → そのまま通る
        assert_eq!(
            resolve(None, Some(O1Source::Marker)),
            Some(O1Source::Marker)
        );
        assert_eq!(resolve(Some(G1Source::Marker), None), None);
        assert_eq!(resolve(None, None), None);

        // ★ 衝突していないときに衝突と言わない
        assert!(!modes_conflict(None, Some(O1Source::Marker)));
        assert!(!modes_conflict(Some(G1Source::Marker), None));
        assert!(!modes_conflict(None, None));
    }

    /// ⚠️★★ **両 OS の形を片方の OS 上で検算する**
    /// (★ macOS では `hook_windows.rs` が 1 行もコンパイルされないので、
    /// `#[cfg]` に頼るテストは相手側の OS で走らない)。
    ///
    /// ## ⚠️★★★ **区切りは必ず `/` で書く**（★ 2026-08-27 に macOS CI で実際に落ちた）
    ///
    /// ★ 本テストが見ているのは **階層数**（mac は 4 つ上・Windows は 1 つ上）であって、
    /// 区切り文字ではない。⚠️ ところが初版は Windows 形を `C:\dist\O1-app\gse-next.exe` と
    /// **バックスラッシュ**で書いていた ——
    /// ★ **Unix では `\` は区切りではない**ので、この文字列は**丸ごと 1 コンポーネント**になり、
    /// `parent()` が空を返して `marker_path_for` が `"o1.mode"` を返す。
    /// → ⚠️★★★ **「両 OS で検算する」ための テストが、片方の OS でしか通らなかった。**
    ///
    /// ★ `g1.rs` の同種テストは最初から `/c/G1-app/gse-next.exe` と**スラッシュ**で書いてある。
    /// ⚠️ **その先例に揃えること。** ★ `/` は Windows でも区切りとして解釈されるので、
    /// **両 OS で同じコンポーネント列**になる = これが「両 OS で検算する」の実体である。
    #[test]
    fn marker_path_matches_the_distribution_layout_on_both_os() {
        // macOS: …/O1-app/gse-next.app/Contents/MacOS/gse-next → 4 階層上が O1-app
        let mac_exe = PathBuf::from("/Users/x/O1-app/gse-next.app/Contents/MacOS/gse-next");
        assert_eq!(
            marker_path_for(&mac_exe, 4),
            Some(PathBuf::from("/Users/x/O1-app").join(MARKER_FILE_NAME))
        );
        // Windows: …/O1-app/gse-next.exe → 1 階層上が O1-app
        // ⚠️ **`\` で書かない**（上記）。★ `g1.rs` と同じ `/c/...` の形に揃える。
        let win_exe = PathBuf::from("/c/O1-app/gse-next.exe");
        assert_eq!(
            marker_path_for(&win_exe, 1),
            Some(PathBuf::from("/c/O1-app").join(MARKER_FILE_NAME))
        );
        // ★ 階層が足りなければ None (落とさない)
        assert_eq!(marker_path_for(Path::new("gse-next"), 4), None);
    }

    /// ⚠️ `g1.mode` と `o1.mode` が同じ名前になっていないこと (★ 取り違えの構造的防止)。
    #[test]
    fn marker_file_names_do_not_collide() {
        assert_ne!(MARKER_FILE_NAME, crate::g1::MARKER_FILE_NAME);
    }

    // --- B: 門と稼働中インジケータ -----------------------------------------

    /// ⚠️★★★ 非 O1 では `session_active` と**完全に同値**である
    /// (＝ G1 / Phase1 の挙動が 1 バイトも変わらない)。
    #[test]
    fn analysis_gate_is_identical_to_session_active_when_not_o1() {
        for active in [false, true] {
            assert_eq!(analysis_gate_open(false, active), active);
        }
    }

    /// ★ O1 では押下に依存せず常に通る (判断 4b-0)。
    #[test]
    fn analysis_gate_is_always_open_in_o1() {
        assert!(analysis_gate_open(true, false));
        assert!(analysis_gate_open(true, true));
    }

    /// ⚠️★★★ **O1 では自己ラベルを記録しない** (2026-08-30 の実機発見の掛け金)。
    ///
    /// ★ ホットキーだけを塞いでボタンが素通りしていた事故を再発させないための門。
    /// ⚠️ **UI 側の `{!o1Mode && …}` だけに頼らない** —— 隠し忘れ / 将来の UI 変更 /
    /// IPC の直叩きでも、backend のここが最後の門になる。
    #[test]
    fn self_marker_is_blocked_in_o1() {
        assert!(!self_marker_allowed(true));
    }

    /// ⚠️★★ **陰性対照**: 非 O1 (Phase1 / G1) の挙動を 1 バイトも変えていないこと。
    ///
    /// ★ これが無いと「全部 false を返す」実装でも上のテストだけは緑になる
    /// (memory `silent-failure-in-guard-scripts`: 門は広げすぎると誤爆する)。
    #[test]
    fn self_marker_is_allowed_when_not_o1() {
        assert!(self_marker_allowed(false));
    }

    /// ★ 共有の門も両分岐を見る（⚠️ 陰性対照つき）。
    #[test]
    fn label_rows_are_blocked_in_o1_and_allowed_elsewhere() {
        assert!(!label_row_allowed(true));
        assert!(label_row_allowed(false));
    }

    /// ⚠️★★★ **ラベル系コマンドの門の掛け忘れを検出する** (2026-08-31)。
    ///
    /// ## なぜソースを読むテストにするのか
    ///
    /// ★ 2026-08-30 に `record_self_marker` **だけ**へ門を置き、⚠️ 兄弟 4 つを見落とした。
    /// ⚠️ **その状態でテストは全部緑だった** —— 純関数のテストは「門があるか」を見ないからである。
    /// → ★ **「配線されているか」を機械で見る**しかない。
    ///
    /// ⚠️ 6 個目のラベル系コマンドを足した人が門を忘れたら、**このテストが赤になる**。
    ///
    /// ⚠️★ 対照も置く: 検査対象のコマンドが 1 つも見つからなければ**赤にする**
    /// (★ 「関数名を変えたら 0 件マッチで黙って緑」を防ぐ。
    ///  memory `silent-failure-in-guard-scripts` の「0 件マッチ」型)。
    #[test]
    fn every_label_command_has_an_o1_gate() {
        // ★ `include_str!` はコンパイル時に埋め込むので、実行時のパス解決に依存しない。
        let src = include_str!("lib.rs");
        let commands = [
            "record_user_label",
            "record_realtime_answer",
            "record_realtime_skip",
            "record_vignette_response",
            "record_self_marker",
        ];
        let mut checked = 0usize;
        for name in commands {
            // ★ `#[tauri::command]` が付いた定義だけを対象にする（`_inner` を拾わない）。
            let needle = format!("\nfn {name}(");
            let Some(pos) = src.find(&needle) else {
                continue;
            };
            checked += 1;
            let body: String = src[pos..].chars().take(1600).collect();
            assert!(
                body.contains("label_row_allowed") || body.contains("self_marker_allowed"),
                "⚠️ {name} に O1 の門が無い。\
                 ★ `crate::o1::label_row_allowed(crate::o1::is_o1())` を先頭に足すこと \
                 (同意文書が列挙していない行型を書かせないため)"
            );
        }
        // ⚠️★★ **対照**: 1 つも見つからなければ検査が空回りしている。
        assert_eq!(
            checked,
            commands.len(),
            "⚠️ ラベル系コマンドの一部が見つからない（改名？）。\
             ★ 本テストが空回りしている可能性があるので、名前を更新すること"
        );
    }

    /// ⚠️★★★ 「記録しているのに『記録していません』と出る」を消す。
    #[test]
    fn recording_active_follows_pause_in_o1_and_session_elsewhere() {
        // O1: session_active は永久に false だが、止めていない限り記録している
        assert!(recording_active(true, false, false));
        assert!(!recording_active(true, false, true));
        // ★ 一時停止が最優先 (押下があっても止めていれば「記録していません」)
        assert!(!recording_active(true, true, true));

        // 非 O1: session_active そのもの (⚠️ paused を見ない = 既存挙動を変えない)
        assert!(!recording_active(false, false, false));
        assert!(!recording_active(false, false, true));
        assert!(recording_active(false, true, false));
        assert!(recording_active(false, true, true));
    }

    /// ⚠️★★★ **事前登録 §7 E1 の実装 acceptance**:
    /// O1 でも `starved_ms` が進む (＝ フックの死を検出できる)。
    ///
    /// ★ `liveness::step` は第 2 引数が false のとき `starved_ms` を **0 に落とす**ので、
    /// `session_active` をそのまま渡すと O1 では永久に 0 になる。
    #[test]
    fn starvation_accumulates_in_o1_even_without_session_active() {
        use crate::input::liveness::{step, Starvation};

        let o1 = true;
        let session_active = false; // ★ O1 では永久にこれ
        let paused = false;

        let mut s = Starvation::default();
        for _ in 0..3 {
            s = step(
                s,
                recording_active(o1, session_active, paused),
                /* system_input_seen */ true,
                /* hook_event_seen  */ false,
                1_000,
            );
        }
        assert_eq!(
            s.starved_ms, 3_000,
            "★ O1 でフックが死んでも starved_ms が進まないと、永久に検出できない"
        );

        // ⚠️ 対照: 素の session_active を渡すと 0 のまま = 直す前の壊れ方
        let mut broken = Starvation::default();
        for _ in 0..3 {
            broken = step(broken, session_active, true, false, 1_000);
        }
        assert_eq!(broken.starved_ms, 0);

        // ★ 一時停止中は数えない (打鍵が無くて当たり前)
        let paused_s = step(
            Starvation { starved_ms: 5_000 },
            recording_active(o1, session_active, /* paused */ true),
            true,
            false,
            1_000,
        );
        assert_eq!(paused_s.starved_ms, 0);
    }

    // --- C: 宣言 -----------------------------------------------------------

    #[test]
    fn declaration_rotates_only_in_o1() {
        assert_eq!(
            decide_declaration_action(true, false),
            DeclarationAction::RotateAndDeclare
        );
        assert_eq!(
            decide_declaration_action(false, false),
            DeclarationAction::NotO1
        );
        // ⚠️★ 二重の安全網: G1 が立っていたら O1 の枝へ入らない
        assert_eq!(
            decide_declaration_action(true, true),
            DeclarationAction::NotO1
        );
        assert_eq!(
            decide_declaration_action(false, true),
            DeclarationAction::NotO1
        );
    }

    // --- D: ローテートと猶予 -----------------------------------------------

    #[test]
    fn daily_rotate_fires_at_the_boundary_and_not_before() {
        let opened = 1_000_000_u64;
        assert!(!should_rotate_daily(opened, opened, ROTATE_AFTER_MS));
        assert!(!should_rotate_daily(
            opened,
            opened + ROTATE_AFTER_MS - 1,
            ROTATE_AFTER_MS
        ));
        assert!(should_rotate_daily(
            opened,
            opened + ROTATE_AFTER_MS,
            ROTATE_AFTER_MS
        ));
        assert!(should_rotate_daily(
            opened,
            opened + ROTATE_AFTER_MS * 3,
            ROTATE_AFTER_MS
        ));
    }

    /// ⚠️★ 時計が巻き戻っても発火しない (NTP 補正 / 手動の時刻変更)。
    #[test]
    fn daily_rotate_survives_a_clock_going_backwards() {
        let opened = 10_000_000_u64;
        assert!(!should_rotate_daily(opened, opened - 1, ROTATE_AFTER_MS));
        assert!(!should_rotate_daily(opened, 0, ROTATE_AFTER_MS));
    }

    /// ⚠️★★★ 猶予は **`session_end` からの経過**で測る。
    #[test]
    fn grace_is_measured_from_session_end() {
        let end = 1_700_000_000_000_u64;
        assert!(!grace_elapsed(end, end, SUBMIT_GRACE_MS));
        assert!(!grace_elapsed(
            end,
            end + SUBMIT_GRACE_MS - 1,
            SUBMIT_GRACE_MS
        ));
        assert!(grace_elapsed(end, end + SUBMIT_GRACE_MS, SUBMIT_GRACE_MS));
        // ⚠️ 巻き戻しは「まだ包まない」に倒れる (安全側)
        assert!(!grace_elapsed(end, end - 1, SUBMIT_GRACE_MS));
    }

    /// ⚠️ 48 時間という値そのものを固定する (★ 恣意的だからこそ動かさない)。
    #[test]
    fn grace_is_exactly_48_hours() {
        assert_eq!(SUBMIT_GRACE_MS, 172_800_000);
        assert_eq!(ROTATE_AFTER_MS, 86_400_000);
    }

    // --- D: ファイル名 -----------------------------------------------------

    #[test]
    fn o1_session_file_names_are_distinguishable() {
        assert!(is_o1_session_file_name("gse_o1_00000000_101112.ndjson"));
        assert!(is_o1_session_file_name("gse_o1_00000000_101112_2.ndjson"));
        // ⚠️ 通常運用 / G1 のファイルは拾わない
        assert!(!is_o1_session_file_name("gse_00000000_101112.ndjson"));
        // ⚠️ 派生ファイルは拾わない
        assert!(!is_o1_session_file_name(
            "gse_o1_00000000_101112.anon.ndjson"
        ));
        assert!(!is_o1_session_file_name("gse_o1_00000000_101112.age"));
        assert!(!is_o1_session_file_name("gse-app.log"));
    }

    /// ★ `reconcile` / `redaction` の既存フィルタ (`gse_` 接頭辞) を**通り抜ける**こと。
    /// ⚠️ 通らないと、O1 のファイルが区間指定削除の対象から外れる = 削除保証が崩れる。
    #[test]
    fn o1_files_still_match_the_generic_session_prefix() {
        assert!(SESSION_FILE_PREFIX.starts_with("gse_"));
    }

    /// ⚠️★★★ **O1 の送信対象に G1 の提出物が 1 本も混ざらない。**
    ///
    /// ★ 提出物フォルダは participant 単位の共有ディレクトリなので、同じ端末に
    /// G1 の未承認 `.age` が残りうる。⚠️ 混ざると **D-14 の承認ゲートが O1 経由で無効化される**。
    #[test]
    fn o1_age_files_are_distinguishable_from_g1_ones() {
        // O1 (stem が gse_o1_*)
        assert!(is_o1_age_file_name(
            "P012_block01_gse_o1_00000000_101112.age"
        ));
        assert!(is_o1_age_file_name(
            "P012_block07_gse_o1_00000000_101112_2.age"
        ));
        // ⚠️ G1 / Phase1 (stem が gse_*)
        assert!(!is_o1_age_file_name("P012_block01_gse_00000000_101112.age"));
        // ⚠️ 旧形式 (手動提出・ブロック番号なし)
        assert!(!is_o1_age_file_name("P012_gse_00000000_101112.age"));
        // ⚠️ 送信済みの印・その他
        assert!(!is_o1_age_file_name(
            "P012_block01_gse_o1_00000000_101112.age.sent"
        ));
        assert!(!is_o1_age_file_name("manifest.jsonl"));
        // ⚠️★ 参加者 ID そのものが `gse_o1_` を含んでも誤判定しない
        //   (★ ID は `^[A-Za-z0-9]{1,16}$` なので `_` を含めない = 構造的に起きない)
        assert!(!is_o1_age_file_name("gseo1_block01_gse_00000000.age"));
    }

    // --- G: 孤児セッションの回収 (2026-09-03・引き継ぎ ④) ------------------

    /// ★ テスト用の一時フォルダ。⚠️ 既存のテスト (reconcile / redaction) と同じ流儀。
    fn sweep_dir(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("gse_o1_sweep_{}_{}", tag, std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    /// ★ 現実的な「いま」。⚠️ `MIN_PLAUSIBLE_EPOCH_MS` を超えている必要がある。
    const NOW: u64 = 1_788_000_000_000;

    fn write(dir: &Path, name: &str, body: &str) -> PathBuf {
        let p = dir.join(name);
        std::fs::write(&p, body).unwrap();
        p
    }

    /// O1 の「開いたまま」= `o1_mode` あり / `session_end` なし / データ行あり。
    const OPEN_O1: &str = concat!(
        r#"{"type":"meta","session_start":1788000000000,"hmm_version":"0.3.0","o1_mode":"marker"}"#,
        "\n",
        r#"{"type":"feat","t":1788000001000,"ikiCv":0.1}"#,
        "\n"
    );

    // ★ 正常: 孤児が閉じ、`session_end` が **検出時刻**になる。
    #[test]
    fn orphan_is_closed_with_the_detection_time() {
        let d = sweep_dir("normal");
        let p = write(&d, "gse_o1_20260901_101112.ndjson", OPEN_O1);
        let sweep = close_orphaned_sessions(&d, None, NOW);
        assert_eq!(
            sweep,
            OrphanSweep {
                closed: 1,
                failed: 0
            }
        );
        let body = std::fs::read_to_string(&p).unwrap();
        assert!(
            body.contains(&format!(r#"{{"type":"meta","session_end":{NOW}}}"#)),
            "★ logger::write_meta_end と 1 バイトも違わない形で書かれていない:\n{body}"
        );
        // ⚠️★★★ 猶予の起点が **今** になっている = 窓は必ず丸 48 時間ある。
        assert!(
            !grace_elapsed(NOW, NOW, SUBMIT_GRACE_MS),
            "★ 閉じた直後に猶予が経過していてはならない (削除保証が消える)"
        );
        assert!(grace_elapsed(NOW, NOW + SUBMIT_GRACE_MS, SUBMIT_GRACE_MS));
    }

    /// ⚠️★★★ **陰性対照**: 触ってはならない 5 種が **1 バイトも変わらない**。
    #[test]
    fn sweep_never_touches_anything_it_should_not() {
        let d = sweep_dir("negative");
        // ① Phase1 (名前が gse_o1_ ではない)
        let phase1 = write(&d, "gse_20260901_101112.ndjson", OPEN_O1);
        // ② G1 (meta に g1_mode)
        let g1 = write(
            &d,
            "gse_o1_20260901_101113.ndjson",
            concat!(
                r#"{"type":"meta","session_start":1,"g1_mode":"marker","o1_mode":"marker"}"#,
                "\n",
                r#"{"type":"feat","t":2}"#,
                "\n"
            ),
        );
        // ③ 押下の痕跡がある (session_start 行) = O1 ではない
        let pressed = write(
            &d,
            "gse_o1_20260901_101114.ndjson",
            concat!(
                r#"{"type":"meta","session_start":1,"o1_mode":"marker"}"#,
                "\n",
                r#"{"type":"session_start","t":2}"#,
                "\n",
                r#"{"type":"feat","t":3}"#,
                "\n"
            ),
        );
        // ④ 既に閉じている O1 (二重クローズしない)
        let closed = write(
            &d,
            "gse_o1_20260901_101115.ndjson",
            concat!(
                r#"{"type":"meta","session_start":1,"o1_mode":"marker"}"#,
                "\n",
                r#"{"type":"feat","t":2}"#,
                "\n",
                r#"{"type":"meta","session_end":3}"#,
                "\n"
            ),
        );
        // ⑤ 中身が無い O1 (meta だけ)
        let empty = write(
            &d,
            "gse_o1_20260901_101116.ndjson",
            concat!(
                r#"{"type":"meta","session_start":1,"o1_mode":"marker"}"#,
                "\n"
            ),
        );
        // ⑥ o1_mode を持たない (名前だけ O1) = R-1 の弁別子
        let renamed = write(
            &d,
            "gse_o1_20260901_101117.ndjson",
            concat!(
                r#"{"type":"meta","session_start":1,"hmm_version":"0.3.0"}"#,
                "\n",
                r#"{"type":"feat","t":2}"#,
                "\n"
            ),
        );
        let before: Vec<String> = [&phase1, &g1, &pressed, &closed, &empty, &renamed]
            .iter()
            .map(|p| std::fs::read_to_string(p).unwrap())
            .collect();
        let sweep = close_orphaned_sessions(&d, None, NOW);
        assert_eq!(
            sweep,
            OrphanSweep::default(),
            "★ 触ってはならないものを閉じた"
        );
        for (p, was) in [&phase1, &g1, &pressed, &closed, &empty, &renamed]
            .iter()
            .zip(before)
        {
            assert_eq!(
                std::fs::read_to_string(p).unwrap(),
                was,
                "⚠️ {:?} が変わっている",
                p.file_name()
            );
        }
    }

    /// ⚠️★★★ **いま開いているファイルには絶対に書かない**。
    #[test]
    fn sweep_never_closes_the_file_that_is_open_right_now() {
        let d = sweep_dir("current");
        let current = write(&d, "gse_o1_20260903_090000.ndjson", OPEN_O1);
        let old = write(&d, "gse_o1_20260901_101112.ndjson", OPEN_O1);
        let sweep = close_orphaned_sessions(&d, Some(current.as_path()), NOW);
        assert_eq!(
            sweep,
            OrphanSweep {
                closed: 1,
                failed: 0
            }
        );
        assert!(
            !std::fs::read_to_string(&current)
                .unwrap()
                .contains("session_end"),
            "★ 書きかけのファイルを閉じてはならない"
        );
        assert!(std::fs::read_to_string(&old)
            .unwrap()
            .contains("session_end"));
    }

    /// ★ 壊れ: **最終行が改行なしで切れている** (強制終了の実際の姿)。
    ///
    /// ⚠️ そのまま append すると壊れた行と `meta` 行が融合し、★ 回収したはずのファイルが
    /// また提出候補から外れる。
    #[test]
    fn truncated_last_line_does_not_swallow_the_meta_row() {
        let d = sweep_dir("truncated");
        let p = write(
            &d,
            "gse_o1_20260901_101112.ndjson",
            concat!(
                r#"{"type":"meta","session_start":1,"o1_mode":"marker"}"#,
                "\n",
                r#"{"type":"feat","t":2}"#,
                "\n",
                r#"{"type":"feat","t":3,"iki"#, // ⚠️ ここで電源が落ちた
            ),
        );
        assert_eq!(close_orphaned_sessions(&d, None, NOW).closed, 1);
        let body = std::fs::read_to_string(&p).unwrap();
        let meta_line = body
            .lines()
            .find(|l| l.contains(r#""session_end""#))
            .expect("★ session_end の行が見つからない");
        assert_eq!(
            meta_line,
            format!(r#"{{"type":"meta","session_end":{NOW}}}"#),
            "⚠️ 壊れた断片と融合している: {body:?}"
        );
    }

    /// ★ 不在: フォルダごと無い / 空のフォルダ。⚠️ 落ちず、何もしない。
    #[test]
    fn missing_or_empty_dir_is_a_no_op() {
        let missing =
            std::env::temp_dir().join(format!("gse_o1_sweep_none_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&missing);
        assert_eq!(
            close_orphaned_sessions(&missing, None, NOW),
            OrphanSweep::default()
        );
        let d = sweep_dir("empty");
        assert_eq!(
            close_orphaned_sessions(&d, None, NOW),
            OrphanSweep::default()
        );
    }

    /// ⚠️★★★ **時計が壊れているときは 1 本も閉じない** (fail-closed)。
    ///
    /// ★ `now_epoch_ms()` の失敗値 `1` / `epoch_ms()` の `0` をそのまま書くと、
    /// 猶予が最初から経過済みになり **削除保証がゼロになる**。
    #[test]
    fn a_broken_clock_closes_nothing() {
        for bad in [0u64, 1, MIN_PLAUSIBLE_EPOCH_MS - 1] {
            let d = sweep_dir(&format!("clock{bad}"));
            let p = write(&d, "gse_o1_20260901_101112.ndjson", OPEN_O1);
            assert_eq!(
                close_orphaned_sessions(&d, None, bad),
                OrphanSweep::default(),
                "★ now_ms={bad} で閉じてしまった"
            );
            assert_eq!(std::fs::read_to_string(&p).unwrap(), OPEN_O1);
        }
    }

    /// ★ 純関数 `is_closable_orphan` を 5 条件ぶん個別に落とす (⚠️ どれを外しても閉じない)。
    #[test]
    fn every_one_of_the_five_conditions_is_required() {
        let ok = O1SessionShape {
            has_o1_mode: true,
            has_g1_mode: false,
            has_session_start: false,
            has_session_end: false,
            has_data_row: true,
        };
        assert!(is_closable_orphan(&ok));
        let mutants = [
            (
                "o1_mode が無い",
                O1SessionShape {
                    has_o1_mode: false,
                    ..ok
                },
            ),
            (
                "g1_mode がある",
                O1SessionShape {
                    has_g1_mode: true,
                    ..ok
                },
            ),
            (
                "押下の痕跡がある",
                O1SessionShape {
                    has_session_start: true,
                    ..ok
                },
            ),
            (
                "既に閉じている",
                O1SessionShape {
                    has_session_end: true,
                    ..ok
                },
            ),
            (
                "中身が無い",
                O1SessionShape {
                    has_data_row: false,
                    ..ok
                },
            ),
        ];
        for (why, m) in mutants {
            assert!(!is_closable_orphan(&m), "⚠️ {why} のに閉じようとした");
        }
    }

    /// ⚠️★★ **べき等**: 2 回走らせても `session_end` は 1 行だけ。
    #[test]
    fn sweeping_twice_writes_session_end_only_once() {
        let d = sweep_dir("idempotent");
        let p = write(&d, "gse_o1_20260901_101112.ndjson", OPEN_O1);
        assert_eq!(close_orphaned_sessions(&d, None, NOW).closed, 1);
        let after_first = std::fs::read_to_string(&p).unwrap();
        assert_eq!(close_orphaned_sessions(&d, None, NOW + 1000).closed, 0);
        assert_eq!(std::fs::read_to_string(&p).unwrap(), after_first);
        assert_eq!(after_first.matches(r#""session_end""#).count(), 1);
    }

    /// ⚠️★ 回収したファイルが **`reconcile` の弁別子を満たす**こと
    /// (★ 「閉じたのに収束器が O1 と認めない」食い違いを固定する)。
    #[test]
    fn a_recovered_file_satisfies_the_reconciler_discriminators() {
        let d = sweep_dir("shape");
        let p = write(&d, "gse_o1_20260901_101112.ndjson", OPEN_O1);
        assert_eq!(close_orphaned_sessions(&d, None, NOW).closed, 1);
        let shape = scan_session_shape(&p).unwrap();
        assert!(shape.has_o1_mode && shape.has_session_end && shape.has_data_row);
        assert!(!shape.has_g1_mode && !shape.has_session_start);
    }

    /// ⚠️★★ **`meta` 行の `session_start` *フィールド* を `session_start` *行* と誤認しない**
    /// (Codex cross-review MEDIUM)。
    ///
    /// ★ O1 の meta 開始行は `{"type":"meta","session_start":<ms>,…}` であり、
    /// ⚠️ 誤認すると **すべての O1 ファイルが「押下の痕跡あり」になって 1 本も閉じない**
    /// (★ 沈黙して直らない)。
    #[test]
    fn the_meta_session_start_field_is_not_a_session_start_row() {
        let d = sweep_dir("metafield");
        let p = write(&d, "gse_o1_20260901_101112.ndjson", OPEN_O1);
        let shape = scan_session_shape(&p).unwrap();
        assert!(
            !shape.has_session_start,
            "⚠️ meta の session_start フィールドを行と誤認している"
        );
        assert_eq!(close_orphaned_sessions(&d, None, NOW).closed, 1);
    }

    /// ⚠️ **書き込めないファイルは `failed` に数え、`closed` に数えない**
    /// (Codex cross-review LOW)。★ 「閉じたつもり」を作らない。
    #[cfg(unix)]
    #[test]
    fn an_unwritable_file_is_counted_as_a_failure() {
        use std::os::unix::fs::PermissionsExt;
        let d = sweep_dir("readonly");
        let p = write(&d, "gse_o1_20260901_101112.ndjson", OPEN_O1);
        std::fs::set_permissions(&p, std::fs::Permissions::from_mode(0o444)).unwrap();
        let sweep = close_orphaned_sessions(&d, None, NOW);
        // ⚠️ root で走ると書けてしまうので、★ **どちらでも「嘘をつかない」ことだけ**を固定する。
        let body = std::fs::read_to_string(&p).unwrap();
        if body.contains("session_end") {
            assert_eq!(
                sweep,
                OrphanSweep {
                    closed: 1,
                    failed: 0
                }
            );
        } else {
            assert_eq!(
                sweep,
                OrphanSweep {
                    closed: 0,
                    failed: 1
                }
            );
        }
        let _ = std::fs::set_permissions(&p, std::fs::Permissions::from_mode(0o644));
    }

    /// ⚠️★★★ **`meta` ＋ 診断行だけのファイルを閉じない**（★ code-reviewer HIGH・実測で発見）。
    ///
    /// ★ macOS の初回起動では IME モニタが `ime_state` を 2 行書くので、
    /// **ブロックを一度も始めずに閉じただけのファイル**が現実に出る。
    /// ⚠️ 旧実装は `meta` 以外を無条件にデータ行と数えたので、
    /// **収束器 (`packaging::has_any_data_row`) が絶対に提出しないファイル**に
    /// `session_end` を書いていた（★ 「触ってはならないものに触っている」）。
    #[test]
    fn a_file_with_only_diagnostic_rows_is_not_closed() {
        let d = sweep_dir("diagnostic");
        let p = write(
            &d,
            "gse_o1_20260901_101112.ndjson",
            concat!(
                r#"{"type":"meta","session_start":1,"o1_mode":"marker"}"#,
                "\n",
                r#"{"type":"ime_state","t":2,"open":false}"#,
                "\n",
                r#"{"type":"ime_state","t":3,"open":true}"#,
                "\n",
                r#"{"type":"hook_health","t":4}"#,
                "\n"
            ),
        );
        let before = std::fs::read_to_string(&p).unwrap();
        assert_eq!(
            close_orphaned_sessions(&d, None, NOW),
            OrphanSweep::default(),
            "⚠️ 収束器が提出しないファイルを閉じてはならない"
        );
        assert_eq!(std::fs::read_to_string(&p).unwrap(), before);
        // ★ 陰性対照: 本物のデータ行が 1 行でもあれば閉じる。
        let q = write(
            &d,
            "gse_o1_20260901_101113.ndjson",
            concat!(
                r#"{"type":"meta","session_start":1,"o1_mode":"marker"}"#,
                "\n",
                r#"{"type":"ime_state","t":2,"open":false}"#,
                "\n",
                r#"{"type":"feat","t":3,"ikiCv":0.1}"#,
                "\n"
            ),
        );
        assert_eq!(close_orphaned_sessions(&d, None, NOW).closed, 1);
        assert!(std::fs::read_to_string(&q).unwrap().contains("session_end"));
    }

    /// ⚠️★★★ **`session_end` が途中で切れた行は「閉じている」と読まない**
    /// （★ code-reviewer MEDIUM・**本実装が塞ごうとしているクラッシュ経路そのもの**）。
    ///
    /// ★ 強制終了が `write_meta_end` の途中に当たると `…"session_end":` で切れる。
    /// ⚠️ 文字列一致で「閉じている」と読むと、sweep は永久に見送り・収束器は数値を取れず、
    /// **そのファイルは恒久的に提出候補外**になる。
    #[test]
    fn a_truncated_session_end_is_not_treated_as_closed() {
        let d = sweep_dir("truncmeta");
        let p = write(
            &d,
            "gse_o1_20260901_101112.ndjson",
            concat!(
                r#"{"type":"meta","session_start":1,"o1_mode":"marker"}"#,
                "\n",
                r#"{"type":"feat","t":2,"ikiCv":0.1}"#,
                "\n",
                r#"{"type":"meta","session_end":"#, // ⚠️ ここで電源が落ちた
            ),
        );
        assert_eq!(close_orphaned_sessions(&d, None, NOW).closed, 1);
        let body = std::fs::read_to_string(&p).unwrap();
        assert!(
            body.lines()
                .any(|l| ndjson_scan::parse_meta_u64(l, "session_end") == Some(NOW)),
            "★ 数値として読める session_end が無い:\n{body}"
        );
    }

    /// ⚠️★★★ **時計が後ろに飛んだ起動では 1 本も閉じない**（★ security-checker HIGH）。
    ///
    /// ★ CMOS 電池切れ → BIOS 既定日 (2020〜2023) で起動、という現実の筋。
    /// ⚠️ 過去の時刻を書くと NTP 補正後に猶予が経過済みになり、削除保証がゼロになる。
    #[test]
    fn a_clock_that_went_backwards_closes_nothing() {
        let d = sweep_dir("backwards");
        // ★ 1 回目 (正常な時計) — 高水位マークが置かれる。
        let first = write(&d, "gse_o1_20260901_101112.ndjson", OPEN_O1);
        assert_eq!(close_orphaned_sessions(&d, None, NOW).closed, 1);
        assert!(std::fs::read_to_string(&first)
            .unwrap()
            .contains("session_end"));
        assert!(d.join(CLOCK_HWM_FILE_NAME).is_file());

        // ⚠️ 2 回目 (時計が 3 年戻った) — **床は通るが高水位で止まる**。
        let past = NOW - 3 * 365 * 24 * 3600 * 1000;
        assert!(
            past > MIN_PLAUSIBLE_EPOCH_MS,
            "★ 床では止まらない値であること"
        );
        let second = write(&d, "gse_o1_20260902_101112.ndjson", OPEN_O1);
        assert_eq!(
            close_orphaned_sessions(&d, None, past),
            OrphanSweep::default(),
            "⚠️ 時計が戻っているのに閉じた"
        );
        assert_eq!(std::fs::read_to_string(&second).unwrap(), OPEN_O1);

        // ★ 時計が直れば拾われる。
        assert_eq!(close_orphaned_sessions(&d, None, NOW + 1000).closed, 1);
    }

    /// ⚠️★★ **時計が未来に飛んだ起動でも閉じない**（★ cross-review MEDIUM の fail-silent 対策）。
    ///
    /// ★ 未来の `session_end` を書くと `grace_elapsed` が永久に偽になり、
    /// ⚠️ **静かに提出されないまま固定**する。→ ★ 閉じずに fail-loud で見送る。
    #[test]
    fn a_clock_in_the_far_future_closes_nothing() {
        let d = sweep_dir("future");
        let p = write(&d, "gse_o1_20260901_101112.ndjson", OPEN_O1);
        assert_eq!(
            close_orphaned_sessions(&d, None, MAX_PLAUSIBLE_EPOCH_MS + 1),
            OrphanSweep::default()
        );
        assert_eq!(std::fs::read_to_string(&p).unwrap(), OPEN_O1);
    }

    /// ⚠️★ **高水位マークは提出経路の走査に掛からない**（★ `gse_` で始まらない）。
    #[test]
    fn the_clock_mark_is_never_mistaken_for_a_session() {
        assert!(!CLOCK_HWM_FILE_NAME.starts_with("gse_"));
        assert!(!is_o1_session_file_name(CLOCK_HWM_FILE_NAME));
        assert!(!is_o1_age_file_name(CLOCK_HWM_FILE_NAME));
    }

    /// ★ G-2: 6 時間ちょうどで回し、1 ms 手前では回さない。⚠️ 巻き戻りでは止めない。
    #[test]
    fn periodic_reconcile_is_due_every_six_hours() {
        assert_eq!(PERIODIC_RECONCILE_MS, 6 * 60 * 60 * 1000);
        let last = 1_790_000_000_000_u64;
        assert!(!periodic_reconcile_due(last, last));
        assert!(!periodic_reconcile_due(
            last,
            last + PERIODIC_RECONCILE_MS - 1
        ));
        assert!(periodic_reconcile_due(last, last + PERIODIC_RECONCILE_MS));
        assert!(
            periodic_reconcile_due(last, last + 3 * PERIODIC_RECONCILE_MS),
            "★ 寝ていたぶんも経過に入る"
        );
        assert!(
            periodic_reconcile_due(last, last - 1),
            "⚠️ 時計が巻き戻ったら基準を引き直させる"
        );
    }

    #[test]
    fn install_id_accepts_only_16_lowercase_hex() {
        assert!(is_valid_install_id("0123456789abcdef"));
        assert!(!is_valid_install_id("0123456789ABCDEF"), "大文字は不可");
        assert!(!is_valid_install_id("0123456789abcde"), "15 桁は不可");
        assert!(!is_valid_install_id("0123456789abcdef0"), "17 桁は不可");
        assert!(!is_valid_install_id("0123456789abcdeg"), "hex 以外は不可");
        assert!(!is_valid_install_id(""));
        assert!(
            !is_valid_install_id("0123456789abcd\"\""),
            "JSON を壊す文字は不可"
        );
    }

    #[test]
    fn install_id_from_bytes_is_valid_and_deterministic() {
        let id = install_id_from_bytes([0, 1, 0xab, 0xcd, 0xef, 0x10, 0x20, 0xff]);
        assert_eq!(id, "0001abcdef1020ff");
        assert!(is_valid_install_id(&id));
    }

    #[test]
    fn plausible_clock_bounds() {
        assert!(!clock_is_plausible(0));
        assert!(!clock_is_plausible(197_132_474_227), "1976 年は範囲の外");
        assert!(!clock_is_plausible(MIN_PLAUSIBLE_EPOCH_MS - 1));
        assert!(clock_is_plausible(MIN_PLAUSIBLE_EPOCH_MS));
        assert!(
            clock_is_plausible(1_795_335_817_091),
            "2026-11-22 は範囲の内"
        );
        assert!(clock_is_plausible(MAX_PLAUSIBLE_EPOCH_MS));
        assert!(!clock_is_plausible(MAX_PLAUSIBLE_EPOCH_MS + 1));
    }

    #[test]
    fn wait_returns_at_once_when_the_clock_is_plausible() {
        let mut slept = 0u64;
        let mut waits = Vec::new();
        let w = wait_for_plausible_clock(
            None,
            || 1_795_335_817_091,
            || slept += 1,
            |k, t| waits.push((k, t)),
        );
        assert_eq!((w.slept, slept, w.gave_up_below_hwm), (0, 0, false));
        assert!(waits.is_empty());
    }

    /// 2026-11-22 の形: 1976 年で起動し、数回後に 2026 年へ合う。合うまで眠り、合ったら抜ける。
    #[test]
    fn wait_sleeps_until_the_clock_becomes_plausible() {
        let clock = std::cell::Cell::new(0usize);
        let seq = [
            197_132_424_000u64,
            197_132_425_000,
            197_132_426_000,
            1_795_335_817_091,
        ];
        let mut slept = 0u64;
        let mut waits = Vec::new();
        let w = wait_for_plausible_clock(
            None,
            || seq[clock.get().min(seq.len() - 1)],
            || {
                slept += 1;
                clock.set(clock.get() + 1);
            },
            |k, t| waits.push((k, t)),
        );
        assert_eq!((w.slept, slept), (3, 3));
        assert_eq!(waits.len(), 3);
        assert_eq!(waits[0], (1, 197_132_424_000));
    }

    /// `on_wait` は眠り終えてから呼ぶ（「n 秒待った」の n が実際に眠った回数と合う）。
    #[test]
    fn on_wait_is_called_after_each_sleep() {
        let clock = std::cell::Cell::new(0usize);
        let seq = [0u64, 0, 1_795_335_817_091];
        let log = std::cell::RefCell::new(Vec::new());
        wait_for_plausible_clock(
            None,
            || seq[clock.get().min(seq.len() - 1)],
            || {
                log.borrow_mut().push("sleep");
                clock.set(clock.get() + 1);
            },
            |_, _| log.borrow_mut().push("on_wait"),
        );
        assert_eq!(*log.borrow(), ["sleep", "on_wait", "sleep", "on_wait"]);
    }

    /// 未来側にずれた時計（2040 年より後）も待つ。
    #[test]
    fn wait_also_waits_for_a_clock_in_the_far_future() {
        let clock = std::cell::Cell::new(0usize);
        let seq = [MAX_PLAUSIBLE_EPOCH_MS + 1, 1_795_335_817_091];
        let mut slept = 0u64;
        let w = wait_for_plausible_clock(
            None,
            || seq[clock.get().min(seq.len() - 1)],
            || {
                slept += 1;
                clock.set(clock.get() + 1);
            },
            |_, _| {},
        );
        assert_eq!((w.slept, slept), (1, 1));
    }

    /// 偽の時計: 呼ぶたびに `seq` を 1 つ進める（最後の値に留まる）。
    /// 眠りが 10,000 回を超えたら落とす（待ちが終わらない誤りを、止まりではなく赤にする）。
    fn run_wait(hwm: Option<u64>, seq: &[u64]) -> ClockWait {
        let i = std::cell::Cell::new(0usize);
        wait_for_plausible_clock(
            hwm,
            || seq[i.get().min(seq.len() - 1)],
            || {
                i.set(i.get() + 1);
                assert!(i.get() <= 10_000, "待ちが終わらない");
            },
            |_, _| {},
        )
    }

    const NOW_2026: u64 = 1_795_335_817_091;
    const BIOS_2024: u64 = 1_704_067_200_000;

    /// ファームウェアの既定日（範囲の内・前回の高水位より古い）で起動し、数秒後に合う形。
    #[test]
    fn wait_for_the_clock_to_pass_the_high_water_mark() {
        let w = run_wait(Some(NOW_2026 - 60_000), &[BIOS_2024, BIOS_2024, NOW_2026]);
        assert_eq!(
            w,
            ClockWait {
                slept: 2,
                gave_up_below_hwm: false
            }
        );
    }

    /// 高水位ちょうどは待たない（前にしか動かない印と同じ時刻は「古い」ではない）。
    #[test]
    fn a_clock_equal_to_the_high_water_mark_does_not_wait() {
        let w = run_wait(Some(NOW_2026), &[NOW_2026]);
        assert_eq!(
            w,
            ClockWait {
                slept: 0,
                gave_up_below_hwm: false
            }
        );
    }

    /// 未来の高水位（一度ずれた時計で書かれた）には追いつけない。上限で打ち切って始める。
    #[test]
    fn a_future_high_water_mark_is_given_up_after_the_limit() {
        let w = run_wait(Some(2_051_222_400_000), &[NOW_2026]);
        assert_eq!(
            w,
            ClockWait {
                slept: HWM_WAIT_MAX_SLEEPS,
                gave_up_below_hwm: true
            }
        );
    }

    /// 範囲の外の待ちは上限に数えない（1976 年の間に高水位の 10 分を使い切らない）。
    #[test]
    fn out_of_range_sleeps_do_not_use_the_high_water_budget() {
        let mut seq = vec![197_132_424_000u64; HWM_WAIT_MAX_SLEEPS as usize + 5];
        seq.push(BIOS_2024);
        seq.push(NOW_2026);
        let w = run_wait(Some(NOW_2026 - 60_000), &seq);
        assert_eq!(
            w,
            ClockWait {
                slept: HWM_WAIT_MAX_SLEEPS + 6, // 範囲の外 605 回＋既定日 1 回
                gave_up_below_hwm: false
            }
        );
    }

    /// 600 回目の眠りの後の読みで高水位に届けば、打ち切りではない（上限の境界の内側）。
    #[test]
    fn reaching_the_high_water_mark_on_the_last_allowed_read_is_not_a_give_up() {
        let mut seq = vec![BIOS_2024; HWM_WAIT_MAX_SLEEPS as usize];
        seq.push(NOW_2026);
        let w = run_wait(Some(NOW_2026 - 60_000), &seq);
        assert_eq!(
            w,
            ClockWait {
                slept: HWM_WAIT_MAX_SLEEPS,
                gave_up_below_hwm: false
            }
        );
    }

    /// 前に打ち切った高水位と同じなら待たない。高水位が動いたら（別の値なら）また待つ。
    #[test]
    fn a_high_water_mark_given_up_once_is_not_waited_for_again() {
        assert_eq!(hwm_to_wait_for(None, None), None);
        assert_eq!(hwm_to_wait_for(Some(NOW_2026), None), Some(NOW_2026));
        assert_eq!(hwm_to_wait_for(Some(NOW_2026), Some(NOW_2026)), None);
        assert_eq!(
            hwm_to_wait_for(Some(NOW_2026 + 1), Some(NOW_2026)),
            Some(NOW_2026 + 1)
        );
        assert_eq!(hwm_to_wait_for(None, Some(NOW_2026)), None);
    }

    #[test]
    fn gave_up_mark_round_trips_and_stays_out_of_session_scans() {
        assert!(!CLOCK_HWM_GAVE_UP_FILE_NAME.starts_with("gse_"));
        assert!(!is_o1_session_file_name(CLOCK_HWM_GAVE_UP_FILE_NAME));
        assert!(!is_o1_age_file_name(CLOCK_HWM_GAVE_UP_FILE_NAME));
        let dir = sweep_dir("clock_hwm_gave_up");
        assert_eq!(clock_hwm_gave_up_in(&dir), None);
        record_clock_hwm_gave_up(&dir, NOW_2026).unwrap();
        assert_eq!(clock_hwm_gave_up_in(&dir), Some(NOW_2026));
        // 高水位そのものには触れない
        assert_eq!(clock_hwm_in(&dir), None);
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn clock_hwm_in_reads_the_mark_and_tolerates_absence() {
        let dir = sweep_dir("clock_hwm_in");
        assert_eq!(clock_hwm_in(&dir), None);
        std::fs::write(dir.join(CLOCK_HWM_FILE_NAME), "1795335817091\n").unwrap();
        assert_eq!(clock_hwm_in(&dir), Some(NOW_2026));
        std::fs::write(dir.join(CLOCK_HWM_FILE_NAME), "garbage").unwrap();
        assert_eq!(clock_hwm_in(&dir), None);
        let _ = std::fs::remove_dir_all(&dir);
    }
}
