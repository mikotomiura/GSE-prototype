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
    !o1_mode
}

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
}
