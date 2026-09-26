//! 提出の **収束器 (reconciler)** — `feature = "package"` 専用。
//!
//! ## ★ 設計の核 (`design.md` §1)
//!
//! 「いま何をすべきか」を**イベントから決めない**。毎回ディスクの状態を突き合わせ、
//! **足りない仕事だけ**をする。何度走らせても同じ状態に収束する (べき等)。
//!
//! ```text
//!   ① 閉じ終わった NDJSON   … session_end を持つ、いま書いていないファイル
//!   ② それに対応する .age    … 無ければ作る (匿名化 → age 暗号化)
//!   ③ それに対応する .sent   … 無ければ送る (成功したら .sent を置く)
//! ```
//!
//! ⚠️★★ **イベント駆動にしない理由**は `design.md` §0 にある。P-1 は 2 回とも
//! 「その瞬間に取るべき動作を取り損ねた」型で失敗しており、`preregistration.md §3.6` は
//! ブロックの事後除外を禁じているので ★ **1 ブロックの取りこぼしが回復不能な損失**になる。
//! 収束型なら、ブロック終了もアプリ起動も **ヒントにすぎない** (取りこぼしても次の機会に拾う)。
//!
//! ★ 「再送」という特別処理は無い。`.sent` が無ければ送る、それだけである。

use std::path::{Path, PathBuf};

use crate::packaging::{has_any_data_row, package_session_as, session_stem};
use crate::submission::{
    age_file_name, age_for_stem, parse_block_number, sent_marker_path, unsent_count,
    MANIFEST_FILE_NAME,
};

/// `.age` を送る先の抽象。★ **差し替え可能にしてある**ので、
/// テストは実エンドポイントに投げずに「失敗 → ローカル保持 → 再送」を実測できる。
pub trait Uploader {
    /// 1 本送る。`Ok(())` を返したときだけ `.sent` が置かれる。
    fn upload(&self, file_name: &str, bytes: &[u8]) -> Result<(), String>;
}

/// ⚠️★★★ **どの収集の提出物を収束させるか** (2026-08-27 / ADR-014 D8 の上書き)。
///
/// ★ G1 と O1 では **3 つの規則が違う**。⚠️ 混ぜると片方の契約が黙って壊れるので型で分ける。
///
/// | | **G1** (統制タスク) | **O1** (自然作業の常時収集) |
/// |---|---|---|
/// | 候補にする NDJSON | `meta` 行に `g1_mode` があるもの | ★ ファイル名が `gse_o1_*` のもの |
/// | 包むまでの猶予 | ★ **無し** (5 分ブロックが閉じたらすぐ) | ⚠️★★★ **48 時間** (`o1::SUBMIT_GRACE_MS`) |
/// | 送る条件 | ★ 被験者が「送信する」を押した (`.age.ok`) | ★ **自動** (同意文書 §5 の逐語) |
///
/// ⚠️ **既定は `G1`** —— ★ 呼び出し側が何も言わなければ従来と 1 バイトも変わらない。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum CollectionMode {
    /// G1 統制タスク実験 (★ 従来の挙動)。
    #[default]
    G1,
    /// ⚠️★★★ O1 (R3-a) 自然作業の常時収集。
    O1,
}

/// 収束器への入力。
pub struct ReconcileOptions {
    /// セッション NDJSON があるディレクトリ。
    pub session_dir: PathBuf,
    /// 提出物 (`.age` / `.sent` / `manifest.jsonl`) を置くディレクトリ。
    pub submission_dir: PathBuf,
    /// 研究者が割り当てた参加者 ID (ファイル名とブロック番号の名前空間)。
    pub participant: String,
    /// age 公開鍵 (`age1...` かファイルパス)。
    pub recipient: String,
    /// ★ どの収集の提出物か ([`CollectionMode`])。⚠️ **既定は `G1`** (従来の挙動)。
    pub mode: CollectionMode,
    /// ★ **いまの時刻** (epoch ms)。⚠️ O1 の 48 時間猶予を測るために要る。
    ///
    /// ★ 引数にしてあるのは **テストが時計を進められるようにする**ためである
    /// (⚠️ 「48 時間待たないと検証できない」テストは書かれないまま腐る)。
    pub now_ms: u64,
}

/// 収束の結果。★ **画面に出すためのもの**である (`design.md` §4: 送信先から成否を追えない)。
#[derive(Debug, Default, PartialEq, Eq)]
pub struct ReconcileReport {
    /// 新しく作った `.age` の本数。
    pub packaged: usize,
    /// 新しく送れた本数。
    pub sent: usize,
    /// 収束後に **まだ送れていない** 本数 (`.age` が在って `.sent` が無いもの)。
    pub unsent: usize,
    /// ★ 送信先が設定されていない (D-4 の研究者側スイッチが OFF)。`.age` はローカルに貯まる。
    pub upload_disabled: bool,
    /// ★ 別の収束器が走っていたので **何もしなかった**。⚠️ これは失敗ではない
    /// (ヒントは 2 本あり、次の機会に収束する)。
    pub skipped_busy: bool,
    /// ★ **被験者の確認待ち**の本数 (`.age` は在るが「送信する」がまだ押されていない)。
    /// ⚠️ これは失敗ではないが、★ **放置すると届かない**ので画面に出す。
    pub awaiting_approval: usize,
    /// ⚠️ 起きた問題。★ **握り潰さない**。呼び出し側が画面へ出す。
    pub errors: Vec<String>,
}

/// 収束器が同時に 2 つ走らないようにする排他ロック (提出物フォルダに 1 つ)。
///
/// ## ⚠️★ なぜ要るか — 「べき等だから二重起動を気にしなくてよい」は **言い過ぎだった**
///
/// 収束器の起点は 2 本ある (アプリ起動時 / ブロック終了時)。★ 送信が詰まると
/// 起動時の 1 回が **ブロック 1 本ぶん (5 分) より長く走りうる**
/// (⚠️ 送信のタイムアウトは 300 秒 × 未送信本数)。そこへブロック終了の 1 回が重なると:
///
/// - 2 つの収束器が **同じ `next_block_number` を読む** (読み取りと `.age` 作成の間に窓がある)
/// - → ★ **別々の NDJSON に同じブロック番号が付く** (`P012_block01_A.age` と
///   `P012_block01_B.age` が並ぶ)。⚠️ **どちらが 1 本目か研究者に分からなくなる**
///
/// ★ ファイルを失うわけではないが、**受け入れ条件「ファイル名にブロック番号が入る」が
/// 意味を失う**ので塞ぐ。塞ぎ方は「後から来たほうが何もせずに帰る」だけでよい
/// (★ 収束型なので、やらなかった仕事は次の機会に必ず拾われる)。
pub struct ReconcileLock {
    path: PathBuf,
    /// ★ このロックの**所有印** (取得時にファイルへ書く)。`refresh` / `Drop` は、ファイルの中身が
    /// これと一致するときだけ触る = **奪われた後に他人のロックを延命も削除もしない**
    /// (2026-09-27・code-reviewer / security-checker / Codex の 3 系統が一致して指摘)。
    token: String,
    /// ★ 所有を失ったと分かった (ロックが消えた / 別の収束器のものに替わった)。
    /// `reconcile()` は次の 1 本に進まず**中断する** (採番の衝突を広げない)。
    lost: std::sync::atomic::AtomicBool,
}

/// ロックを取ろうとした結果。
///
/// ⚠️★ **「他が走っている」と「そもそも作れない」を混ぜない** (code-review MEDIUM)。
/// 混ぜると、書けないフォルダで **永久に沈黙する**（毎回「busy なので何もしません」に見える）。
pub enum LockOutcome {
    /// 取れた。
    Acquired(ReconcileLock),
    /// 他の収束器が走っている。★ 失敗ではない (次の機会に収束する)。
    Busy,
    /// ⚠️ ロックファイルを作れない (権限・ディスク等)。★ **失敗として画面に出す。**
    Unavailable(String),
}

impl ReconcileLock {
    /// ロックを取る。
    ///
    /// `stale_after` より古いロックは **奪う**。⚠️ プロセスが強制終了されるとロックが
    /// 残るので、★ 残骸で永久に自動提出が止まるほうが害が大きい。
    pub fn acquire(dir: &Path, stale_after: std::time::Duration) -> LockOutcome {
        let path = dir.join("reconcile.lock");
        for attempt in 0..2 {
            match std::fs::OpenOptions::new()
                .write(true)
                .create_new(true)
                .open(&path)
            {
                Ok(mut f) => {
                    let token = new_lock_token();
                    // ⚠️ 所有印を書けないロックは `refresh` / `Drop` が自分のものと確認できない。
                    //   → 取れなかったものとして片付け、**失敗として出す** (Busy に倒さない)。
                    if let Err(e) = std::io::Write::write_all(&mut f, token.as_bytes()) {
                        drop(f);
                        let _ = std::fs::remove_file(&path);
                        return LockOutcome::Unavailable(format!(
                            "ロックファイルに書き込めません ({}): {e}",
                            path.display()
                        ));
                    }
                    return LockOutcome::Acquired(Self {
                        path,
                        token,
                        lost: std::sync::atomic::AtomicBool::new(false),
                    });
                }
                Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => {
                    if attempt > 0 {
                        return LockOutcome::Busy;
                    }
                    // ★ 古すぎるロックは残骸とみなして奪う。
                    let stale = std::fs::metadata(&path)
                        .and_then(|m| m.modified())
                        .map(|t| t.elapsed().map(|d| d > stale_after).unwrap_or(false))
                        .unwrap_or(false);
                    if !stale {
                        return LockOutcome::Busy;
                    }
                    tracing::warn!("reconcile: taking over a stale lock at {:?}", path);
                    let _ = std::fs::remove_file(&path);
                }
                // ⚠️ ★ ここを Busy に倒さない。書けないなら**毎回**失敗し続けるので、
                //   「次の機会に収束する」が成り立たない = 黙って止まる。
                Err(e) => {
                    return LockOutcome::Unavailable(format!(
                        "提出フォルダに書き込めません ({}): {e}",
                        path.display()
                    ))
                }
            }
        }
        LockOutcome::Busy
    }
}

#[cfg(test)]
thread_local! {
    /// テスト専用: このスレッドで `ReconcileLock::refresh` が呼ばれた回数。
    /// ⚠️ スレッドローカルなので、並列に走る他のテストの呼び出しは混ざらない。
    static REFRESH_CALLS: std::cell::Cell<usize> = const { std::cell::Cell::new(0) };
}

impl ReconcileLock {
    /// ★ **走っている間、ロックの mtime を「いま」へ進める** (heartbeat)。
    ///
    /// ⚠️★★★ 更新が無いと、`acquire` の stale 判定は「**取った時刻からの経過**」になり、
    /// 1 回の収束が `LOCK_STALE_AFTER` を超えて走ったとき**走っている最中のロックを奪われる**。
    /// O1 は 1 日 1 本なので、回線断が約 13 日続く (= 未送信 13 本 × 送信 timeout 300 秒 = 3900 秒 > 3600 秒。
    /// ⚠️ 12 本ちょうどは 3600 秒で `acquire` の `>` に当たらない。梱包の時間を足せばもっと早い) と
    /// 現に起きる (2026-09-27 に `impact-analyzer` が指摘・`reconcile.rs` 自身を読んで確認)。
    /// 奪われると 2 つの収束器が同じ番号を採る。
    ///
    /// ★ 1 本ごと (梱包 1 回・送信 1 回) の直前に呼ぶ。→ stale 判定は「**更新と更新の間 (1 本ぶん)** を
    /// 超えて更新が無い」だけになり、未送信の本数に依存しない。
    /// ⚠️★ **更新する前にファイルの中身が自分の所有印か確認する。** 奪われて別の収束器のロックに
    /// 替わっていたら、それを延命せず (`lost` を立てて) 呼び出し側に**中断させる**。
    /// 進められなかっただけ (I/O エラー) なら、黙らないが止めない (ロックは補助)。
    pub fn refresh(&self) {
        #[cfg(test)]
        REFRESH_CALLS.with(|c| c.set(c.get() + 1));
        match self.owned() {
            // ★ 自分のロックのときだけ進める。
            Some(true) => {
                let result = std::fs::OpenOptions::new()
                    .write(true)
                    .open(&self.path)
                    .and_then(|f| f.set_modified(std::time::SystemTime::now()));
                if let Err(e) = result {
                    // 進められなかっただけ (所有は失っていない)。黙らないが止めない。
                    tracing::warn!(
                        "reconcile: could not refresh the lock heartbeat at {:?}: {e}",
                        self.path
                    );
                }
            }
            // ⚠️ 消えた / 別の収束器のものに替わった = **奪われた**。作り直さず・触らず、印を立てる。
            Some(false) => {
                self.lost.store(true, std::sync::atomic::Ordering::SeqCst);
                tracing::warn!(
                    "reconcile: the lock was taken over or removed at {:?}; stopping this run",
                    self.path
                );
            }
            // 読めなかった (一時的な I/O エラー等)。所有は断定できないので中断はしない。
            None => tracing::warn!(
                "reconcile: could not read the lock to verify ownership at {:?}",
                self.path
            ),
        }
    }

    /// ★ 所有を失ったか (`refresh` が奪取・消失を検知した)。呼び出し側は次の 1 本へ進まない。
    pub fn is_lost(&self) -> bool {
        self.lost.load(std::sync::atomic::Ordering::SeqCst)
    }

    /// ファイルの中身が自分の所有印か。`Some(true)`=自分 / `Some(false)`=無い・別物 / `None`=読めない。
    ///
    /// ⚠️★ **これは OS の排他ロックではない**。確認と操作 (`refresh` の更新・`Drop` の削除) の間には
    /// 競合窓が残る。⚠️ 窓の長さに上限は無い (確認の直後にスケジューラやスリープで止まりうる)。
    /// → 「奪われたら他人のロックを延命・削除し続ける」から「確認直後に止まった場合だけ」へ縮むだけで、
    /// 排他を**保証**するものではない。また処理の途中 (1 本の梱包・送信) で奪われても、その 1 本は
    /// 完了する (次の `refresh` で初めて検知する)。
    ///
    /// ★ 保証を失ったときの**最後の砦**は 2 つ: (1) 出力名が既にあれば包まない
    /// (`out_path.exists()`・「1 本も失わない」)、(2) 受け口が同名を**別名で足す**
    /// (`GSE_O1_Submit.gs` `saveWithoutOverwriting_`)。→ 最悪でも**重複・番号のずれ**であって、
    /// データの喪失ではない。
    fn owned(&self) -> Option<bool> {
        match std::fs::read_to_string(&self.path) {
            Ok(body) => Some(body == self.token),
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => Some(false),
            Err(_) => None,
        }
    }
}

/// ロックの所有印を作る (プロセス ID ＋ 時刻 ＋ プロセス内の連番)。秘密ではない・推測されても害は無い。
fn new_lock_token() -> String {
    static SEQ: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
    let nanos = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0);
    format!(
        "{}-{nanos}-{}",
        std::process::id(),
        SEQ.fetch_add(1, std::sync::atomic::Ordering::SeqCst)
    )
}

impl Drop for ReconcileLock {
    fn drop(&mut self) {
        // ★ **自分のロックだけ**消す。奪われた後に、後続の収束器のロックを消して
        //   3 つ目を通さない (旧実装は無条件に消していた)。読めないときは消さない
        //   (残しても 1 時間で stale として奪える・他人のを消すより害が小さい)。
        if self.owned() == Some(true) {
            let _ = std::fs::remove_file(&self.path);
        }
    }
}

/// ロックが残骸とみなされるまでの時間。
///
/// ★ 送信のタイムアウト (300 秒・2026-09-05 に実測して決定) を**十分に**上回る値にする
/// (余裕は × 10 = 3000 秒。テスト `the_stale_threshold_is_longer_than_a_worst_case_run`)。
/// ⚠️ 短すぎると、正常に走っている収束器のロックを奪って上の衝突を再現してしまう。
///
/// ★ **2026-09-27 の改訂**: 旧文は「× 想定される未送信の最大本数 (10 ブロック)」で、**取った時刻からの
/// 経過**で判定していた。G1 の 10 ブロックには足りたが、O1 の日単位の滞留 (13 本以上) には足りない。
/// → 収束器が `ReconcileLock::refresh` で 1 本ごとに mtime を進めるようにしたので、この値は
/// 「**1 本ぶんの所要を大きく超えて更新が無い = 死んだ**」の閾値になり、**本数に依存しない**。
/// 前提は「**更新と更新の間 (= 1 本の梱包、または 1 本の送信) が本値より十分に短いこと**」である。
/// ⚠️ 送信は timeout (300 秒) で抑えられるが、**梱包と読み込みは timeout で抑えられていない**。
/// 更新の間隔が本値を超えれば従来と同じ奪取が起きる — ただしその場合も、奪われた側は `refresh` で
/// 所有を確認して**中断し**、他人のロックを延命も削除もしない (`ReconcileLock::token`)。
pub const LOCK_STALE_AFTER: std::time::Duration = std::time::Duration::from_secs(60 * 60);

/// ★ **G1 で書かれ、かつ閉じ終わった**セッション NDJSON を、名前昇順 (= 時刻順) で列挙する。
///
/// 条件は 4 つ:
/// 1. `gse_*.ndjson` の通常ファイル (`.anon.ndjson` 等の派生は除く)
/// 2. ★ `meta.session_end` を持つ = **もう書かれない**
/// 3. `meta` 以外の行がある = 中身がある (`has_any_data_row`。2026-08-05 の空ファイル対策)
/// 4. ★★ `meta` 行に **`g1_mode` がある** = G1 の実施で書かれたものである
///
/// ⚠️ ★ 条件 2 が「いま書いているファイルを触らない」を **構造的に** 保証している。
/// 呼び出し側から「現在のパス」を渡してもらう設計にしなかったのは、
/// ★ 渡し忘れると黙って書きかけのファイルを包む形になるためである。
///
/// ## ⚠️★★ 条件 4 が要る理由 (code-review HIGH)
///
/// ★ `~/Documents/GSE-sessions` は **participant 非依存の共有ディレクトリ**である
/// (`logger.rs` の fallback)。Phase1 の較正セッションや P-1 の記録が **同じ端末に残る**。
/// 条件 4 が無いと、収束器はそれらも「閉じ終わった NDJSON」として拾い、
/// ⚠️ ★ **古いセッションにブロック番号 1〜4 を与えてから**、本物の G1 ブロックに 5 を振る。
/// → 受け入れ条件「ブロックの自動終了 1 回につき `.age` が 1 本・名前にブロック番号」が
/// **黙って意味を失う**。しかも古い記録が研究者へ送られる。
/// ★ 判定材料は `logger::write_meta_start` が既に書いている (`"g1_mode":"marker"|"env"`)。
pub fn closed_sessions(dir: &Path) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = match std::fs::read_dir(dir) {
        Ok(rd) => rd
            .flatten()
            .filter(|e| e.file_type().map(|t| t.is_file()).unwrap_or(false))
            .map(|e| e.path())
            .filter(|p| {
                let name = match p.file_name().and_then(|s| s.to_str()) {
                    Some(n) => n,
                    None => return false,
                };
                name.starts_with("gse_")
                    && name.ends_with(".ndjson")
                    && !name.ends_with(".anon.ndjson")
            })
            .filter(|p| is_closed_g1_session(p) && has_any_data_row(p))
            .collect(),
        Err(_) => Vec::new(),
    };
    out.sort();
    out
}

/// ⚠️★★★ **O1 で書かれ、閉じ終わり、猶予を過ぎた**セッション NDJSON を名前昇順で列挙する。
///
/// 条件は 5 つ (★ [`closed_sessions`] の 4 条件に **猶予**を足した形):
/// 1. ★ ファイル名が **`gse_o1_*.ndjson`** (`.anon.ndjson` 等の派生は除く)
/// 2. ★ `meta.session_end` を持つ = **もう書かれない**
/// 3. ⚠️ `meta` 行に **`g1_mode` が無い** (★ 万一 G1 の記録が同名で紛れても拾わない)
/// 4. `meta` 以外の行がある (`has_any_data_row`)
/// 5. ⚠️★★★ **`session_end` から `grace_ms` 以上が経っている**
///
/// ## ⚠️★★★ 猶予を「包む前」に効かせる理由 (★ ここを間違えると削除保証が崩れる)
///
/// `delete_time_range` → `redact_dir` は **ローカルの `gse_*.ndjson` だけ**を書き換え、
/// **`.age` は対象外**である (`redaction.rs`)。
/// → ★ **48 時間より前に `.age` を作ると、その後に被験者が消しても `.age` には残り、送られる。**
/// ⚠️ ADR-014 **判断 3 の根拠 3**「被験者が停止・削除できる」が崩れる。
/// ★ したがって猶予は **③ 送信ではなく ② 包む**ところに置く。
pub fn closed_o1_sessions(dir: &Path, now_ms: u64, grace_ms: u64) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = match std::fs::read_dir(dir) {
        Ok(rd) => rd
            .flatten()
            .filter(|e| e.file_type().map(|t| t.is_file()).unwrap_or(false))
            .map(|e| e.path())
            .filter(|p| {
                p.file_name()
                    .and_then(|s| s.to_str())
                    .map(crate::o1::is_o1_session_file_name)
                    .unwrap_or(false)
            })
            .filter(|p| match closed_o1_session_end(p) {
                Some(end) => crate::o1::grace_elapsed(end, now_ms, grace_ms),
                None => false,
            })
            .filter(|p| has_any_data_row(p))
            .collect(),
        Err(_) => Vec::new(),
    };
    out.sort();
    out
}

/// NDJSON が **O1 で閉じ終わっている**なら、その `session_end` (epoch ms) を返す。
///
/// ★ 読むのは **`meta` 行の形だけ**である (打鍵の内容も時刻も解釈しない・data-privacy)。
/// 読めないファイルは `None` (= 触らない) に倒す。
///
/// ⚠️ `g1_mode` を持つファイルは **`None`** を返す —— ★ G1 の提出経路 (承認つき・猶予なし) と
/// 二重に拾わないための構造的な排他である。
fn closed_o1_session_end(path: &Path) -> Option<u64> {
    use std::io::BufRead;
    let f = std::fs::File::open(path).ok()?;
    let mut session_end: Option<u64> = None;
    // ⚠️★★★ **`session_start` 行を 1 本でも持つファイルは O1 ではない**
    //   (cross-review / Codex HIGH・2026-08-27)。
    //
    // ★ Codex の指摘: O1 の識別が**ファイル名だけ**だと、⚠️ セッション置き場は
    //   **被験者が書き込めるフォルダ**なので、Phase1 の記録を `gse_o1_*` にリネームすると
    //   **承認なしで自動送信される**。
    // → ★ **構造的な弁別子を足す**: O1 は `start_session` を通らない
    //   (`lib.rs` が O1 で拒否する) ので **`{"type":"session_start"}` 行が 1 本も出ない**。
    //   ⚠️ 対して Phase1 / G1 の「中身のある」ファイルは**必ず 1 本以上持つ**
    //   (★ 押下しないと打鍵が記録されないので、押下の痕跡なしにデータ行は存在しえない)。
    //   ★ schema を 1 バイトも変えずに効く (⚠️ 完全ではない —— `decisions.md` R-1 参照)。
    let mut has_session_start = false;
    // ⚠️★★★ **`meta` 行の `o1_mode` を第 1 の根拠にする** (研究者判断 R-1・2026-08-26)。
    //   ★ ファイル名は被験者が書き換えられるが、⚠️ **`meta` 行は記録の中身**である。
    //   ★ `g1_mode` と同じ形。→ 2026-08-26 以降に O1 で書いたファイルは必ず持つ。
    let mut has_o1_mode = false;
    for line in std::io::BufReader::new(f).lines() {
        // ⚠️★★★ **1 行の読み取り失敗で関数ごと諦めない** (code-reviewer MEDIUM・2026-08-27)。
        //   ★ 以前は `line.ok()?` で、**UTF-8 として不正な 1 行があるだけで `None`** を返した。
        //   → ⚠️ そのファイルが **黙って提出候補から永久に外れる** (fail-silent)。
        //   ★ `meta` 行は ASCII の固定形なので、壊れた行を飛ばしても判定は成立する。
        let line = match line {
            Ok(l) => l,
            Err(_) => continue,
        };
        if crate::ndjson_scan::is_session_start_row(&line) {
            has_session_start = true;
        }
        if !crate::ndjson_scan::is_meta_row(&line) {
            continue;
        }
        if line.contains(crate::ndjson_scan::NEEDLE_G1_MODE) {
            // ⚠️ G1 の記録である。★ O1 の経路では 1 本も触らない。
            return None;
        }
        if line.contains(crate::ndjson_scan::NEEDLE_O1_MODE) {
            has_o1_mode = true;
        }
        // ⚠️ ★ **最後の `session_end` を採る。** 1 ファイルに 2 本入ることは無い設計だが、
        //   もし混ざったら「より新しい方」= 安全側 (猶予が長くなる) に倒れる。
        if let Some(v) = parse_meta_u64(&line, "session_end") {
            session_end = Some(v);
        }
    }
    if !has_o1_mode {
        // ⚠️★★★ **`o1_mode` を持たないファイルは O1 として提出しない** (R-1)。
        //   ★ 名前は書き換えられるが、`meta` 行の中身は記録そのものである。
        //   ⚠️ 2026-08-26 より前に O1 で書いたファイルはこれを持たないが、
        //   ★ **収集はまだ始まっていない**ので実データは存在しない (移行の心配は無い)。
        tracing::warn!(
            "reconcile: {:?} is named like an O1 session but its meta row has no o1_mode;              refusing to submit it as O1",
            path.file_name()
        );
        return None;
    }
    if has_session_start {
        // ⚠️★★★ **押下の痕跡があるファイルは O1 ではない。** ★ 名前だけを頼りにしない
        //   (★ セッション置き場は被験者が書き込めるフォルダである)。
        tracing::warn!(
            "reconcile: {:?} is named like an O1 session but carries session_start rows; \
             refusing to submit it as O1",
            path.file_name()
        );
        return None;
    }
    session_end
}

/// `meta` 行から数値フィールドを 1 つ取り出す (★ 手書きパーサ)。
///
/// ⚠️ ★ `serde_json` を使わないのは、`reconcile` が **1 行を丸ごとメモリに載せない**
/// 走査で済ませているためである (★ 1 行は最大 `MAX_SESSION_BYTES` まで許容される)。
/// ★ `meta` 行は `logger::write_meta_end` が**手書きで固定形**に出しているので、
/// `"<key>":<digits>` を探せば足りる。
fn parse_meta_u64(line: &str, key: &str) -> Option<u64> {
    // ⚠️★★★ **実装は `crate::ndjson_scan` が単一真実源**である (2026-09-03)。
    //   ★ `o1::scan_session_shape` が「文字列が在るか」で見ていて食い違ったため、
    //   ⚠️ **同じ関数を呼ぶ形に寄せた**。★ ここの薄いラッパは既存の呼び出し / テストのため。
    crate::ndjson_scan::parse_meta_u64(line, key)
}

/// NDJSON が **G1 で書かれ、かつ `session_end` を持つ**か (1 パスで両方見る)。
///
/// ★ 読むのは **`meta` 行の形だけ**である (打鍵の内容も時刻も解釈しない・data-privacy)。
/// 読めないファイルは `false` (= 触らない) に倒す。⚠️ 書きかけを包むより、
/// 次の機会に持ち越すほうが安全だからである (収束型なので持ち越しは損失にならない)。
pub fn is_closed_g1_session(path: &Path) -> bool {
    use std::io::BufRead;
    let f = match std::fs::File::open(path) {
        Ok(f) => f,
        Err(_) => return false,
    };
    let mut closed = false;
    let mut is_g1 = false;
    for line in std::io::BufReader::new(f).lines() {
        let line = match line {
            Ok(l) => l,
            Err(_) => return false,
        };
        if !crate::ndjson_scan::is_meta_row(&line) {
            continue;
        }
        if line.contains(r#""session_end""#) {
            closed = true;
        }
        if line.contains(crate::ndjson_scan::NEEDLE_G1_MODE) {
            is_g1 = true;
        }
    }
    closed && is_g1
}

/// 台帳 (`manifest.jsonl`) と既存 `.age` から、次に使うブロック番号を決める。
///
/// ★ **両方の最大値 + 1** を採る。⚠️ 台帳が消えても `.age` の名前から復元でき、
/// `.age` を研究者が手で退避しても台帳から復元できる (どちらか片方が欠けても番号が戻らない)。
/// ★ アプリのメモリ上のカウンタは使わない (再起動で 0 に戻るため・`design.md` §3)。
pub fn next_block_number(submission_dir: &Path, participant: &str) -> u32 {
    let from_files = crate::submission::list_age_files(submission_dir)
        .iter()
        .filter_map(|p| p.file_name().and_then(|s| s.to_str()))
        .filter_map(|n| parse_block_number(n, participant))
        .max()
        .unwrap_or(0);
    let from_manifest = read_manifest_blocks(submission_dir, participant)
        .into_iter()
        .max()
        .unwrap_or(0);
    from_files.max(from_manifest) + 1
}

/// ⚠️★★★ **O1 の次の日番号**を決める (R-13)。★ `next_block_number` の鏡像。
///
/// ★ `.age` の名前と台帳の**両方の最大値 + 1** を採る (⚠️ 片方が欠けても番号が戻らない)。
pub fn next_o1_day_number(submission_dir: &Path, participant: &str) -> u32 {
    let from_files = crate::submission::list_age_files(submission_dir)
        .iter()
        .filter_map(|p| p.file_name().and_then(|s| s.to_str()))
        .filter_map(|n| crate::submission::parse_o1_day_number(n, participant))
        .max()
        .unwrap_or(0);
    let from_manifest = read_manifest_days(submission_dir, participant)
        .into_iter()
        .max()
        .unwrap_or(0);
    from_files.max(from_manifest) + 1
}

/// 台帳から、その参加者の **O1 日番号**を読む。
///
/// ⚠️ ★ 台帳の `block` 欄は G1 と共有だが、`age` の名前で**どちらの名前空間か**が分かる。
fn read_manifest_days(submission_dir: &Path, participant: &str) -> Vec<u32> {
    let path = submission_dir.join(MANIFEST_FILE_NAME);
    let text = match std::fs::read_to_string(path) {
        Ok(t) => t,
        Err(_) => return Vec::new(),
    };
    text.lines()
        .filter_map(|l| serde_json::from_str::<serde_json::Value>(l.trim()).ok())
        .filter(|v| v.get("participant").and_then(|x| x.as_str()) == Some(participant))
        // ⚠️★ **`age` の名前で名前空間を判定する。** ★ `block` 欄だけを見ると
        //   G1 の番号を O1 の最大値として拾い、⚠️ **番号が飛ぶ**。
        .filter(|v| {
            v.get("age")
                .and_then(|x| x.as_str())
                .map(|n| crate::submission::parse_o1_day_number(n, participant).is_some())
                .unwrap_or(false)
        })
        .filter_map(|v| v.get("block").and_then(|x| x.as_u64()))
        .map(|n| n as u32)
        .collect()
}

/// 台帳から、その参加者のブロック番号を読む。壊れた行は飛ばす (★ 台帳は append-only で、
/// 壊れた 1 行のために全体を捨てない)。
fn read_manifest_blocks(submission_dir: &Path, participant: &str) -> Vec<u32> {
    let path = submission_dir.join(MANIFEST_FILE_NAME);
    let text = match std::fs::read_to_string(path) {
        Ok(t) => t,
        Err(_) => return Vec::new(),
    };
    text.lines()
        .filter_map(|l| serde_json::from_str::<serde_json::Value>(l.trim()).ok())
        .filter(|v| v.get("participant").and_then(|x| x.as_str()) == Some(participant))
        .filter_map(|v| v.get("block").and_then(|x| x.as_u64()))
        .map(|n| n as u32)
        .collect()
}

/// 台帳に 1 行 **追記** する。⚠️ ★ 既存の行は書き換えない (`design.md` §3)。
fn append_manifest(
    submission_dir: &Path,
    participant: &str,
    block: u32,
    age_name: &str,
    source_stem: &str,
) -> Result<(), String> {
    use std::io::Write;
    let path = submission_dir.join(MANIFEST_FILE_NAME);
    let line = serde_json::json!({
        "participant": participant,
        "block": block,
        "age": age_name,
        "source_stem": source_stem,
    });
    let mut f = std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&path)
        .map_err(|e| format!("台帳を開けません ({}): {e}", MANIFEST_FILE_NAME))?;
    writeln!(f, "{line}").map_err(|e| format!("台帳に追記できません: {e}"))
}

/// ★ 収束を 1 回まわす。**何度呼んでも安全** (べき等)。
///
/// `uploader` が `None` のとき ② まで行って止まる (= 送信オフ・D-4)。
pub fn reconcile(opts: &ReconcileOptions, uploader: Option<&dyn Uploader>) -> ReconcileReport {
    let mut report = ReconcileReport {
        upload_disabled: uploader.is_none(),
        ..Default::default()
    };

    if let Err(e) = std::fs::create_dir_all(&opts.submission_dir) {
        report.errors.push(format!(
            "提出物フォルダを作成できません ({}): {e}",
            opts.submission_dir.display()
        ));
        return report;
    }

    // ★ 同時に 2 つ走らせない (ブロック番号の衝突を防ぐ・`ReconcileLock` のコメント参照)。
    //   ⚠️ 取れなかったのは **失敗ではない**。何もせずに帰る。
    let lock = match ReconcileLock::acquire(&opts.submission_dir, LOCK_STALE_AFTER) {
        LockOutcome::Acquired(l) => l,
        LockOutcome::Busy => {
            report.skipped_busy = true;
            report.unsent = unsent_count(&opts.submission_dir, &opts.participant);
            return report;
        }
        LockOutcome::Unavailable(e) => {
            // ⚠️ ★ 黙らない。書けないフォルダは毎回失敗するので、次の機会にも収束しない。
            report.errors.push(e);
            report.unsent = unsent_count(&opts.submission_dir, &opts.participant);
            return report;
        }
    };

    // --- ② 閉じ終わった NDJSON に .age が無ければ作る --------------------------
    // ⚠️★★★ O1 は **48 時間の猶予**を過ぎたものだけを候補にする。
    //   ★ 猶予は「包む前」に効かせる —— `.age` にしてしまうと `delete_time_range` が
    //   届かなくなり (`redaction.rs` は `.age` を触らない)、判断 3 の根拠 3 が崩れる。
    let candidates = match opts.mode {
        CollectionMode::G1 => closed_sessions(&opts.session_dir),
        CollectionMode::O1 => {
            closed_o1_sessions(&opts.session_dir, opts.now_ms, crate::o1::SUBMIT_GRACE_MS)
        }
    };
    // ★ ロックを奪われたと分かったら、次の 1 本へ進まず**中断する** (採番の衝突を広げない)。
    let mut lost = false;
    for input in candidates {
        let stem = session_stem(&input);
        if age_for_stem(&opts.submission_dir, &stem).is_some() {
            continue; // 既に包んである (手動提出で作った旧形式も含む)
        }
        // ★ 1 本ごとに heartbeat (`ReconcileLock::refresh` のコメント参照)。
        lock.refresh();
        if lock.is_lost() {
            lost = true;
            break;
        }
        // ⚠️★★★ **O1 は G1 と別の名前空間で採番する** (研究者判断 R-13)。
        //   ★ 共有すると番号を食い合い、⚠️ 研究者から見て「何ブロック目か」が意味を失う。
        //   ★ O1 の単位は**ブロック (5 分) ではなく日**なので `block` の語自体が嘘になる。
        let (block, out_name) = match opts.mode {
            CollectionMode::G1 => {
                let n = next_block_number(&opts.submission_dir, &opts.participant);
                (n, age_file_name(&opts.participant, n, &stem))
            }
            CollectionMode::O1 => {
                let n = next_o1_day_number(&opts.submission_dir, &opts.participant);
                (
                    n,
                    crate::submission::o1_age_file_name(&opts.participant, n, &stem),
                )
            }
        };
        let out_path = opts.submission_dir.join(&out_name);
        if out_path.exists() {
            // ⚠️ ★ **黙って上書きしない。** 1 本も失えない (`design.md` §3)。
            report.errors.push(format!(
                "提出物 {out_name} が既にあるため、このブロックを包めませんでした。研究者に連絡してください。"
            ));
            continue;
        }
        match package_session_as(
            &input,
            &opts.participant,
            &opts.recipient,
            &opts.submission_dir,
            &out_name,
        ) {
            Ok(_) => {
                report.packaged += 1;
                if let Err(e) = append_manifest(
                    &opts.submission_dir,
                    &opts.participant,
                    block,
                    &out_name,
                    &stem,
                ) {
                    // ★ `.age` は既にできている。台帳が書けなくても提出物は失われない。
                    //   ⚠️ ただし黙らない (次回の採番が `.age` の名前だけに頼ることになる)。
                    report.errors.push(e);
                }
            }
            Err(e) => report
                .errors
                .push(format!("提出物を作成できませんでした: {e}")),
        }
    }

    // --- ③ 確認済みで .sent が無い .age を送る -----------------------------------
    // ⚠️★ **被験者が「送信する」を押した分だけ**送る (D-14: 同意の担保)。
    //   ★ 確認が無いものも ② で `.age` にはなっている = **データは失われない**。
    //   送られないだけであり、後から確認すればそのまま送られる (収束型のまま)。
    // ⚠️★★★ **O1 は承認を求めない** (研究者判断 O1-2 / 同意文書 §5)。
    //   ★ 逐語「1 日ごとにひとまとまりにした記録を、48 時間おいてから暗号化して
    //   **自動的に**研究者へ送ります」。⚠️ 毎日「送信する」を押させると**その逐語が嘘になる**。
    //   ★ `.age.ok` が担っていた「同意手続きを経ていない人が起動する経路を塞ぐ」役割は、
    //   O1 では **配布フォルダのマーカー (`o1.mode`)** が担う (G1 の `g1.mode` と同じ形)。
    //   ⚠️ G1 は `approved_unsent_age_files` のまま —— 1 バイトも変えない。
    if let Some(up) = uploader.filter(|_| !lost) {
        let to_send = match opts.mode {
            CollectionMode::G1 => crate::submission::approved_unsent_age_files(
                &opts.submission_dir,
                &opts.participant,
            ),
            // ⚠️★★★ **O1 の提出物だけを送る** (code-reviewer / security-checker が一致して指摘)。
            //   ★ 絞らないと **同じ端末に残っている G1 の未承認 `.age`** が
            //   **承認なしに送られる** = D-14 の承認ゲートが O1 経由で無効化される。
            //   ★ R-13 で名前空間を分けたので、**`o1day<NN>` の形かどうか**で構造的に切れる
            //   (⚠️ `closed_o1_sessions` が `g1_mode` を弾いているのと対の排他)。
            CollectionMode::O1 => {
                crate::submission::unsent_o1_age_files(&opts.submission_dir, &opts.participant)
            }
        };
        for age in to_send {
            let name = match age.file_name().and_then(|s| s.to_str()) {
                Some(n) => n.to_string(),
                None => continue,
            };
            let bytes = match std::fs::read(&age) {
                Ok(b) => b,
                Err(e) => {
                    report.errors.push(format!("{name} を読めません: {e}"));
                    continue;
                }
            };
            // ★ 1 本ごとに heartbeat (最大 300 秒の送信の**前**に進める)。
            lock.refresh();
            if lock.is_lost() {
                lost = true;
                break;
            }
            match up.upload(&name, &bytes) {
                Ok(()) => {
                    // ★ 送れたときだけ印を置く。⚠️ `.age` には触らない。
                    match std::fs::write(sent_marker_path(&age), b"sent\n") {
                        Ok(()) => report.sent += 1,
                        Err(e) => {
                            // ⚠️ ★ 送れたのに印が置けない = **次回もう一度送る**。
                            //   二重に届くほうが、届かないより害が小さい (研究者が重複を捨てられる)。
                            report
                                .errors
                                .push(format!("{name} の送信済みマークを保存できません: {e}"));
                        }
                    }
                }
                Err(e) => report.errors.push(format!("{name} を送信できません: {e}")),
            }
        }
    }

    if lost {
        // ⚠️ 黙らない。やらなかった仕事は次の機会に収束する (収束型)。
        report.errors.push(
            "収束の途中でロックを失いました (別の収束器に奪われた可能性)。残りは次の機会に収束します。"
                .to_string(),
        );
    }

    // ⚠️★ **数える対象と送る対象を同じ規則にする** (`submission.rs` の drift 防止の趣旨)。
    //   ★ O1 で全部数えると、**送らない G1 の `.age`** まで「まだ届いていない」に出る。
    report.unsent = match opts.mode {
        CollectionMode::G1 => unsent_count(&opts.submission_dir, &opts.participant),
        CollectionMode::O1 => {
            crate::submission::unsent_o1_age_files(&opts.submission_dir, &opts.participant).len()
        }
    };
    // ⚠️★ **O1 に「確認待ち」は無い** (承認ゲートを通らないので、数えると画面に嘘が出る)。
    report.awaiting_approval = match opts.mode {
        CollectionMode::G1 => {
            crate::submission::awaiting_approval_count(&opts.submission_dir, &opts.participant)
        }
        CollectionMode::O1 => 0,
    };
    report
}

// --- HTTP 送信層 -------------------------------------------------------------

/// GAS Web App へ POST する送信層。
///
/// ★ 実測に基づく制約 (`gas-measurements.md`):
/// - **M-1**: POST は **302 を返す**。⚠️ リダイレクトを追う必要があり、
///   ★ メソッドを POST に強制すると **405** になる。`reqwest` の既定のリダイレクト方針は
///   302 で POST → GET に変える (curl の既定と同じ) ので、実測が通った形と一致する。
/// - **M-2**: 300 KB が 1.45 s で通る → **分割アップロードは不要**。
/// - **M-3**: GAS の `e` に **ヘッダが無い** → ★ 認証は **本文** に入れる
///   (⚠️ クエリに置くと URL に残る)。
#[cfg(feature = "package")]
pub struct HttpUploader {
    endpoint: String,
    secret: String,
    /// ★ クライアントは **1 回だけ** 作る。⚠️ 送信のたびに build すると、
    /// 10 本再送で TLS/プロキシの初期化を 10 回やることになる (code-review LOW)。
    client: reqwest::blocking::Client,
}

#[cfg(feature = "package")]
impl HttpUploader {
    pub fn new(cfg: &crate::submission::SubmitConfig) -> Result<Self, String> {
        let client = reqwest::blocking::Client::builder()
            // ★ 2026-09-05 に**実測して決めた** (`experiments/20260801-controlled-friction-task/
            // o1-upload-timeout-measurement.md`)。⚠️ それまでは「Drive 保存を含む所要時間が
            // 未実測」のまま 180 秒を置いていた。
            //
            // ★ 実測 (Drive 保存を含む・合成ランダムバイト・端末 → 本番の受け口):
            //   | raw    | 本文    | client   | server  |
            //   |  1 MB  |  1.4 MB |   7.9 s  |  3.5 s  |
            //   | 12 MB  | 16.0 MB |  37.5 s  | 17.0 s  |
            //   | 28 MB  | 37.3 MB |  54.5 s  | 28.1 s  |
            //   | 36 MB  | 48.0 MB |  97.3 s  | 55.9 s  |  ← ★ **通る最大**
            //   | 40 MB  | 53.3 MB | ⚠️ HTTP 400 (★ Google が doPost の手前で弾く) |
            //
            // ⚠️★★★ **`MAX_BYTES = 48 MB` は到達できない。** ★ Apps Script Web App の
            // HTTP 本文の上限 (実測で 48.0 MB は通り 53.3 MB は 400) が先に効くので、
            // 送れる `.age` は **約 37 MB まで**である。→ ★ 受け口側の上限を下げる話は別件
            // (`o1-upload-timeout-measurement.md` の「⚠️ 併せて見つかった欠陥」)。
            //
            // ★ 採用: **300 秒固定**。⚠️ 理由は 2 つ:
            //   1. ★ 通る最大 (36 MB) の実測が 97.3 s なので **約 3 倍**の余裕になる。
            //      ⚠️ これ以上長くしても、37 MB 超は timeout ではなく **400 で落ちる**ので
            //      何も買えない (★ 長い timeout が助けるのは「遅い回線」だけ)。
            //   2. ⚠️ `LOCK_STALE_AFTER >= timeout * 10` の不変条件 (下のテスト) がある。
            //      ★ 2026-09-27 以降は heartbeat (`ReconcileLock::refresh`) があるので**未送信の本数には
            //      依存しない**が、1 本ぶんの所要が `LOCK_STALE_AFTER` に近づかない余裕は要る
            //      (300 s なら 3000 s ≤ 3600 s。⚠️ 600 秒にするとテストが赤になる = 余裕の見直しを促す)。
            .timeout(std::time::Duration::from_secs(300))
            .build()
            .map_err(|e| format!("HTTP クライアントを初期化できません: {e}"))?;
        Ok(Self {
            endpoint: cfg.endpoint.clone(),
            secret: cfg.secret.clone(),
            client,
        })
    }
}

#[cfg(feature = "package")]
impl Uploader for HttpUploader {
    fn upload(&self, file_name: &str, bytes: &[u8]) -> Result<(), String> {
        use base64::Engine as _;
        let body = serde_json::json!({
            "secret": self.secret,
            "name": file_name,
            "b64": base64::engine::general_purpose::STANDARD.encode(bytes),
        })
        .to_string();

        let resp = self
            .client
            .post(&self.endpoint)
            .header("Content-Type", "application/json")
            .body(body)
            .send()
            .map_err(|e| format!("送信に失敗しました (通信): {e}"))?;

        let status = resp.status();
        let text = resp.text().unwrap_or_default();
        if !status.is_success() {
            return Err(format!("送信に失敗しました (HTTP {})", status.as_u16()));
        }
        // ⚠️★ **HTTP 200 を成功と読まない。** GAS は例外時も 200 で本文にエラーを返す。
        //   ★ アプリ層の応答 (`"ok":true`) を要求する。さもないと「送ったつもり」が
        //   `.sent` になって回収不能になる (送信先から成否を追えない・M-5)。
        if !response_is_ok(&text) {
            return Err(format!(
                "送信先が受領を確認しませんでした: {}",
                truncate_for_display(&text)
            ));
        }
        Ok(())
    }
}

/// 送信先の応答が「受領した」と言っているか (純関数)。
///
/// ⚠️ ★ **本文の部分一致で判定しない** (code-review LOW)。
/// 部分一致だと `{"echo":"\"ok\":true"}` のような**別の意味の本文**まで成功と読む。
/// ★ GAS 側は必ず JSON を返す (`json_()`) ので、**構造として読む**。
/// ⚠️ 読めない本文 (HTML のエラーページ等) は当然 `false`。
pub fn response_is_ok(body: &str) -> bool {
    serde_json::from_str::<serde_json::Value>(body)
        .ok()
        .and_then(|v| v.get("ok").and_then(|x| x.as_bool()))
        .unwrap_or(false)
}

/// エラー表示用に応答本文を切り詰める (画面・ログを汚さない)。
fn truncate_for_display(s: &str) -> String {
    let one_line: String = s.chars().map(|c| if c == '\n' { ' ' } else { c }).collect();
    let trimmed = one_line.trim();
    if trimmed.chars().count() <= 200 {
        trimmed.to_string()
    } else {
        trimmed.chars().take(200).collect::<String>() + "…"
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Mutex;

    fn tmpdir(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("gse_rec_{}_{}", tag, std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    fn test_recipient() -> String {
        age::x25519::Identity::generate().to_public().to_string()
    }

    /// ★ **G1 で** 閉じたセッション (g1_mode + session_end + 打鍵) を 1 本書く。
    /// ⚠️ `g1_mode` は `logger::write_meta_start` が G1 実施時にだけ刻む値である。
    fn write_closed(dir: &Path, name: &str) {
        std::fs::write(
            dir.join(name),
            "{\"type\":\"meta\",\"session_start\":1000,\"hmm_version\":\"0.3.0\",\"g1_mode\":\"marker\"}\n\
             {\"type\":\"key\",\"t\":1200,\"vk\":74,\"press\":true}\n\
             {\"type\":\"meta\",\"session_end\":9000}\n",
        )
        .unwrap();
    }

    /// ⚠️ **Phase1 相当** (G1 ではない) の閉じたセッション。★ 触ってはならない。
    fn write_closed_non_g1(dir: &Path, name: &str) {
        std::fs::write(
            dir.join(name),
            "{\"type\":\"meta\",\"session_start\":1000,\"hmm_version\":\"0.3.0\"}\n\
             {\"type\":\"key\",\"t\":1200,\"vk\":74,\"press\":true}\n\
             {\"type\":\"meta\",\"session_end\":9000}\n",
        )
        .unwrap();
    }

    /// ⚠️★★★ **O1 で** 閉じたセッションを 1 本書く。
    /// ★ O1 は `meta` 行に `g1_mode` を刻まない (schema を変えないため) ので、
    /// **ファイル名 (`gse_o1_*`)** が O1 であることの根拠になる。
    fn write_closed_o1(dir: &Path, name: &str, session_end_ms: u64) {
        std::fs::write(
            dir.join(name),
            format!(
                "{{\"type\":\"meta\",\"session_start\":1000,\"hmm_version\":\"0.5.0\",\"o1_mode\":\"marker\"}}\n\
                 {{\"type\":\"key\",\"t\":1200,\"vk\":74,\"press\":true}}\n\
                 {{\"type\":\"key\",\"t\":5000,\"vk\":75,\"press\":true}}\n\
                 {{\"type\":\"meta\",\"session_end\":{session_end_ms}}}\n"
            ),
        )
        .unwrap();
    }

    /// 書きかけのセッション (session_end 無し)。
    fn write_open(dir: &Path, name: &str) {
        std::fs::write(
            dir.join(name),
            "{\"type\":\"meta\",\"session_start\":1000}\n\
             {\"type\":\"key\",\"t\":1200,\"vk\":74,\"press\":true}\n",
        )
        .unwrap();
    }

    /// 常に成功する送信層。送ったファイル名を記録する。
    struct OkUploader(Mutex<Vec<String>>);
    impl Uploader for OkUploader {
        fn upload(&self, file_name: &str, _bytes: &[u8]) -> Result<(), String> {
            self.0.lock().unwrap().push(file_name.to_string());
            Ok(())
        }
    }

    /// 常に失敗する送信層 (★ 実エンドポイントに投げずに「落ちている」を作る)。
    struct FailUploader;
    impl Uploader for FailUploader {
        fn upload(&self, _file_name: &str, _bytes: &[u8]) -> Result<(), String> {
            Err("connection refused (test)".to_string())
        }
    }

    /// 被験者が「送信する」を押した状態にする (確認の印を付ける)。
    fn approve(subm: &Path) -> usize {
        crate::submission::approve_pending(subm, "P012").unwrap()
    }

    fn opts(sess: &Path, subm: &Path, recipient: &str) -> ReconcileOptions {
        ReconcileOptions {
            session_dir: sess.to_path_buf(),
            submission_dir: subm.to_path_buf(),
            participant: "P012".to_string(),
            recipient: recipient.to_string(),
            // ★ 既定は G1 = 従来の挙動。⚠️ 既存のテストは 1 本も意味が変わらない。
            mode: CollectionMode::G1,
            now_ms: 0,
        }
    }

    /// ⚠️★★★ O1 用の入力。★ **時計を引数で渡す**ので、48 時間を待たずに検証できる。
    fn o1_opts(sess: &Path, subm: &Path, recipient: &str, now_ms: u64) -> ReconcileOptions {
        ReconcileOptions {
            mode: CollectionMode::O1,
            now_ms,
            ..opts(sess, subm, recipient)
        }
    }

    /// ⚠️★ **書きかけのファイルを包まない。** 閉じたものだけを拾う。
    #[test]
    fn closed_sessions_ignores_open_and_derived_files() {
        let d = tmpdir("closed");
        write_closed(&d, "gse_20260807_010101.ndjson");
        write_open(&d, "gse_20260807_020202.ndjson"); // 書きかけ: 除外
        std::fs::write(
            d.join("gse_20260807_030303.ndjson"),
            "{\"type\":\"meta\",\"session_start\":1}\n{\"type\":\"meta\",\"session_end\":2}\n",
        )
        .unwrap(); // meta しか無い: 除外
        std::fs::write(d.join("gse_20260807_040404.anon.ndjson"), "x").unwrap(); // 派生: 除外
        std::fs::write(d.join("notes.txt"), "x").unwrap();

        let found = closed_sessions(&d);
        assert_eq!(found.len(), 1, "found = {found:?}");
        assert_eq!(found[0].file_name().unwrap(), "gse_20260807_010101.ndjson");
        let _ = std::fs::remove_dir_all(&d);
    }

    /// ★★ **収束する** — 途中で止めて再実行しても同じ状態になる (べき等)。
    #[test]
    fn reconcile_is_idempotent() {
        let s = tmpdir("idem_s");
        let o = tmpdir("idem_o");
        let r = test_recipient();
        write_closed(&s, "gse_20260807_010101.ndjson");
        write_closed(&s, "gse_20260807_020202.ndjson");

        let up = OkUploader(Mutex::new(Vec::new()));
        // 1 回目: `.age` はできるが、★ **確認前なので送らない**。
        let first = reconcile(&opts(&s, &o, &r), Some(&up));
        assert_eq!(first.packaged, 2);
        assert_eq!(first.sent, 0, "★ 確認前に送ってはならない");
        assert_eq!(first.awaiting_approval, 2);
        assert!(first.errors.is_empty(), "{:?}", first.errors);

        // 被験者が「送信する」を押す。
        assert_eq!(approve(&o), 2);
        let sent = reconcile(&opts(&s, &o, &r), Some(&up));
        assert_eq!(sent.packaged, 0);
        assert_eq!(sent.sent, 2);
        assert_eq!(sent.unsent, 0);
        assert_eq!(sent.awaiting_approval, 0);

        // ★ もう一度走らせても **何も増えない**。
        let second = reconcile(&opts(&s, &o, &r), Some(&up));
        assert_eq!(second.packaged, 0);
        assert_eq!(second.sent, 0);
        assert_eq!(second.unsent, 0);
        assert_eq!(
            up.0.lock().unwrap().len(),
            2,
            "同じ .age を二度送ってはならない"
        );

        let _ = std::fs::remove_dir_all(&s);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ★★ **取りこぼしても次の機会に拾う** — `.age` の無い NDJSON を置けば拾われる。
    #[test]
    fn reconcile_picks_up_a_missed_block() {
        let s = tmpdir("miss_s");
        let o = tmpdir("miss_o");
        let r = test_recipient();
        write_closed(&s, "gse_20260807_010101.ndjson");
        let up = OkUploader(Mutex::new(Vec::new()));
        reconcile(&opts(&s, &o, &r), Some(&up));
        approve(&o);
        reconcile(&opts(&s, &o, &r), Some(&up));

        // ★ ここで「ブロック終了イベントを取りこぼした」状況を作る = 送信処理を呼ばずに
        //   NDJSON だけが増える。
        write_closed(&s, "gse_20260807_020202.ndjson");
        let rep = reconcile(&opts(&s, &o, &r), Some(&up));
        assert_eq!(rep.packaged, 1, "取りこぼしたブロックが拾われていない");
        assert_eq!(rep.awaiting_approval, 1);
        approve(&o);
        let rep = reconcile(&opts(&s, &o, &r), Some(&up));
        assert_eq!(rep.sent, 1);
        assert_eq!(rep.unsent, 0);
        // ブロック番号は 1 → 2 と続く。
        assert!(o.join("P012_block01_gse_20260807_010101.age").is_file());
        assert!(o.join("P012_block02_gse_20260807_020202.age").is_file());
        let _ = std::fs::remove_dir_all(&s);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ★★ **送信失敗 → ローカル保持 → 再送** の一巡 (⚠️ 実エンドポイントには投げない)。
    #[test]
    fn failed_upload_keeps_age_and_is_retried_next_time() {
        let s = tmpdir("retry_s");
        let o = tmpdir("retry_o");
        let r = test_recipient();
        write_closed(&s, "gse_20260807_010101.ndjson");

        // 0) `.age` を作り、被験者が「送信する」を押した状態にする。
        reconcile(&opts(&s, &o, &r), Some(&FailUploader));
        assert_eq!(approve(&o), 1);

        // 1) 送信先が落ちている。
        let down = reconcile(&opts(&s, &o, &r), Some(&FailUploader));
        assert_eq!(down.packaged, 0);
        assert_eq!(down.sent, 0);
        assert_eq!(down.unsent, 1, "★ 未送信が見えていなければ回収できない");
        assert!(
            !down.errors.is_empty(),
            "★ 失敗を黙って飲み込んではならない"
        );
        let age = o.join("P012_block01_gse_20260807_010101.age");
        assert!(age.is_file(), "★ .age はローカルに残らなければならない");
        assert!(!sent_marker_path(&age).exists());

        // 2) 復旧したら **再送という特別処理なしに** 送られる。
        let up = OkUploader(Mutex::new(Vec::new()));
        let back = reconcile(&opts(&s, &o, &r), Some(&up));
        assert_eq!(back.packaged, 0, "包み直してはならない");
        assert_eq!(back.sent, 1);
        assert_eq!(back.unsent, 0);
        assert!(sent_marker_path(&age).exists());
        assert!(age.is_file(), "★ 送信後も .age を消さない");
        let _ = std::fs::remove_dir_all(&s);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ★ 送信オフ (D-4 の研究者側スイッチ) では ② まで進んで止まる。
    #[test]
    fn upload_disabled_still_produces_local_age() {
        let s = tmpdir("off_s");
        let o = tmpdir("off_o");
        let r = test_recipient();
        write_closed(&s, "gse_20260807_010101.ndjson");
        let rep = reconcile(&opts(&s, &o, &r), None);
        assert!(rep.upload_disabled);
        assert_eq!(rep.packaged, 1);
        assert_eq!(rep.sent, 0);
        assert_eq!(rep.unsent, 1);
        assert!(o.join("P012_block01_gse_20260807_010101.age").is_file());
        let _ = std::fs::remove_dir_all(&s);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ★★ **匿名化が新しい経路でも効いている**ことを、生成物を復号して実測する。
    /// (受け入れ条件: `vk` が `category` に置き換わっている)
    #[test]
    fn generated_age_is_anonymized() {
        use std::io::Read;
        let s = tmpdir("anon_s");
        let o = tmpdir("anon_o");
        let id = age::x25519::Identity::generate();
        let pubkey = id.to_public().to_string();
        write_closed(&s, "gse_20260807_010101.ndjson");
        reconcile(&opts(&s, &o, &pubkey), None);

        let age_path = o.join("P012_block01_gse_20260807_010101.age");
        let bytes = std::fs::read(&age_path).unwrap();
        let dec = age::Decryptor::new(&bytes[..]).unwrap();
        let mut reader = match dec {
            age::Decryptor::Recipients(d) => d
                .decrypt(std::iter::once(&id as &dyn age::Identity))
                .unwrap(),
            _ => panic!("expected recipients"),
        };
        let mut plain = String::new();
        reader.read_to_string(&mut plain).unwrap();
        assert!(!plain.contains("\"vk\""), "★ vk が漏れている: {plain}");
        assert!(plain.contains("\"category\":\"alphabetic\""));
        let _ = std::fs::remove_dir_all(&s);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ★ ブロック番号は台帳と `.age` の **両方** から復元できる。
    #[test]
    fn next_block_number_recovers_from_either_source() {
        let o = tmpdir("num");
        assert_eq!(next_block_number(&o, "P012"), 1);

        // `.age` だけがある (台帳を失った)。
        std::fs::write(o.join("P012_block03_gse_a.age"), b"x").unwrap();
        assert_eq!(next_block_number(&o, "P012"), 4);

        // 台帳だけがある (研究者が `.age` を退避した)。
        let o2 = tmpdir("num2");
        std::fs::write(
            o2.join(MANIFEST_FILE_NAME),
            "{\"participant\":\"P012\",\"block\":5}\nbroken line\n{\"participant\":\"P013\",\"block\":9}\n",
        )
        .unwrap();
        assert_eq!(
            next_block_number(&o2, "P012"),
            6,
            "★ 壊れた行で全体を捨てない"
        );
        assert_eq!(next_block_number(&o2, "P013"), 10);
        assert_eq!(next_block_number(&o2, "P099"), 1, "他人の番号を継がない");
        let _ = std::fs::remove_dir_all(&o);
        let _ = std::fs::remove_dir_all(&o2);
    }

    /// ⚠️★★ **G1 以外の記録に手を出さない** (code-review / security-checker とも HIGH)。
    ///
    /// `~/Documents/GSE-sessions` と `~/Documents/GSE-submissions` は **使い回される**。
    /// Phase1 の較正セッションや P-1 の残骸が同じ端末に在り、実際に P-1 実機には
    /// 旧形式の `.age` が 4 本残っている (`notes.md §7-5`)。
    ///
    /// ★ 絞りが無いと:
    /// - ⚠️ **Phase1 の記録が、同意していない経路 (G1 のエンドポイント) へ送られる**
    /// - ⚠️ 古いセッションがブロック番号 1〜4 を食い潰し、**本物の G1 ブロック 1 が block05 になる**
    /// - ⚠️ 初回起動でいきなり「未送信 4 件」が出て被験者が混乱する
    #[test]
    fn nothing_outside_g1_is_packaged_counted_or_sent() {
        let s = tmpdir("scope_s");
        let o = tmpdir("scope_o");
        let r = test_recipient();

        // Phase1 相当 (g1_mode 無し) の閉じたセッション。★ 触ってはならない。
        write_closed_non_g1(&s, "gse_20260701_010101.ndjson");
        // 手動提出で作られた旧形式の `.age` (P-1 の残骸)。★ 送ってはならない。
        std::fs::write(o.join("P012_gse_20260701_010101.age"), b"old").unwrap();
        // 別参加者の提出物。★ 送ってはならない。
        std::fs::write(o.join("P007_block01_gse_x.age"), b"other").unwrap();

        let up = OkUploader(Mutex::new(Vec::new()));
        let rep = reconcile(&opts(&s, &o, &r), Some(&up));
        assert_eq!(rep.packaged, 0, "★ G1 でないセッションを包んではならない");
        assert_eq!(rep.sent, 0, "★ 自分の分でない .age を送ってはならない");
        assert_eq!(rep.unsent, 0, "★ 他人・旧形式を未送信に数えてはならない");
        assert!(up.0.lock().unwrap().is_empty(), "1 本も送ってはならない");

        // ★ 陽性対照: G1 のセッションを 1 本足せば、ちゃんと block01 から始まる。
        write_closed(&s, "gse_20260808_010101.ndjson");
        let rep2 = reconcile(&opts(&s, &o, &r), Some(&up));
        assert_eq!(rep2.packaged, 1);
        approve(&o);
        let rep2 = reconcile(&opts(&s, &o, &r), Some(&up));
        assert_eq!(rep2.sent, 1);
        assert!(
            o.join("P012_block01_gse_20260808_010101.age").is_file(),
            "★ 古い記録に番号を食われて block01 でなくなってはならない"
        );
        let _ = std::fs::remove_dir_all(&s);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ★★ **確認していないブロックは送らない。ただし `.age` は必ず作る。**
    ///
    /// ⚠️ ★ ここが D-14 の核心である。同意の担保のために送信を止めるが、
    /// **記録そのものは止めない** — さもないと D-4 が却下した
    /// 「止めたまま最後まで行って回収ゼロ」が本当に起きる。
    /// ★ `.age` がローカルに在る限り、研究者が端末から受け取る最後の経路は生きている。
    #[test]
    fn unapproved_blocks_are_packaged_but_never_sent() {
        let s = tmpdir("appr_s");
        let o = tmpdir("appr_o");
        let r = test_recipient();
        write_closed(&s, "gse_20260808_010101.ndjson");

        let up = OkUploader(Mutex::new(Vec::new()));
        let rep = reconcile(&opts(&s, &o, &r), Some(&up));
        assert_eq!(
            rep.packaged, 1,
            "★ 確認前でも .age は作る (データを失わない)"
        );
        assert_eq!(rep.sent, 0, "★ 確認前に送ってはならない");
        assert_eq!(rep.awaiting_approval, 1);
        assert!(up.0.lock().unwrap().is_empty());
        let age = o.join("P012_block01_gse_20260808_010101.age");
        assert!(age.is_file(), "★ .age はローカルに残る");

        // ★ 何度走らせても、確認しない限り送られない (「あとで」を押し続けた状態)。
        for _ in 0..3 {
            let again = reconcile(&opts(&s, &o, &r), Some(&up));
            assert_eq!(again.sent, 0);
            assert_eq!(again.awaiting_approval, 1);
        }
        assert!(up.0.lock().unwrap().is_empty());

        // 被験者が「送信する」を押したら送られる。
        assert_eq!(approve(&o), 1);
        let after = reconcile(&opts(&s, &o, &r), Some(&up));
        assert_eq!(after.sent, 1);
        assert_eq!(after.awaiting_approval, 0);
        assert_eq!(after.unsent, 0);
        let _ = std::fs::remove_dir_all(&s);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ⚠️ ロックが作れない (書けないフォルダ) を「busy」と混ぜない。
    /// ★ 混ぜると、書けない環境で**毎回何もせず・エラーも出さず**に沈黙する。
    #[test]
    fn an_unwritable_folder_is_an_error_not_busy() {
        // ⚠️ ★ 「ロックのパスにディレクトリを置く」では **赤にならなかった** (実測):
        //   `O_CREAT|O_EXCL` は既存ディレクトリにも `AlreadyExists` を返すので busy 扱いになる。
        //   → ★ **存在しないフォルダ**で試す (どのプラットフォームでも `NotFound` になる)。
        let o = std::env::temp_dir().join(format!("gse_rec_nodir_{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&o);
        assert!(
            matches!(
                ReconcileLock::acquire(&o, LOCK_STALE_AFTER),
                LockOutcome::Unavailable(_)
            ),
            "★ 書けない状態を busy に倒してはならない"
        );
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ★★ **収束器が 2 つ同時に走らない。** 走っている間は後から来たほうが何もせずに帰る。
    ///
    /// ⚠️ ★ これが無いと、2 つの収束器が同じ `next_block_number` を読み、
    /// **別々の NDJSON に同じブロック番号が付く**（どちらが 1 本目か分からなくなる）。
    /// ★ 何もせずに帰るのは損失にならない（収束型なので次の機会に必ず拾われる）。
    #[test]
    fn a_second_reconciler_does_nothing_while_one_is_running() {
        let s = tmpdir("busy_s");
        let o = tmpdir("busy_o");
        let r = test_recipient();
        write_closed(&s, "gse_20260807_010101.ndjson");

        // 1 つ目が走っている状態を作る。
        let held = match ReconcileLock::acquire(&o, LOCK_STALE_AFTER) {
            LockOutcome::Acquired(l) => l,
            _ => panic!("first lock must be acquired"),
        };
        let rep = reconcile(&opts(&s, &o, &r), None);
        assert!(rep.skipped_busy, "★ 走っている間は何もしないこと");
        assert_eq!(rep.packaged, 0, "★ 番号を採ってはならない");
        assert!(rep.errors.is_empty(), "★ 失敗ではない: {:?}", rep.errors);

        // 1 つ目が終われば、次の機会にちゃんと拾われる。
        drop(held);
        let rep2 = reconcile(&opts(&s, &o, &r), None);
        assert!(!rep2.skipped_busy);
        assert_eq!(rep2.packaged, 1);
        assert!(o.join("P012_block01_gse_20260807_010101.age").is_file());
        let _ = std::fs::remove_dir_all(&s);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ⚠️ ★ プロセスが強制終了してロックが残っても、**永久に止まらない**。
    #[test]
    fn a_stale_lock_is_taken_over() {
        let o = tmpdir("stale");
        // 残骸のロック（誰も持っていない）。
        std::fs::write(o.join("reconcile.lock"), b"").unwrap();
        // 猶予 0 なら「古い」とみなして奪う。
        let taken = ReconcileLock::acquire(&o, std::time::Duration::from_secs(0));
        assert!(
            matches!(taken, LockOutcome::Acquired(_)),
            "★ 残骸で永久に止まってはならない"
        );
        drop(taken);

        // ⚠️ ★ 逆に、**いま取ったばかりのロックは奪えない**。
        //   (猶予 0 で試すと自分で置いたロックまで古い扱いになる — 実測して分かった。
        //    ★ だから `LOCK_STALE_AFTER` を短くしてはならない。)
        let held = match ReconcileLock::acquire(&o, LOCK_STALE_AFTER) {
            LockOutcome::Acquired(l) => l,
            _ => panic!("fresh lock must be acquired"),
        };
        assert!(
            matches!(
                ReconcileLock::acquire(&o, LOCK_STALE_AFTER),
                LockOutcome::Busy
            ),
            "★ 走っている収束器のロックを奪ってはならない"
        );
        drop(held);
        assert!(matches!(
            ReconcileLock::acquire(&o, LOCK_STALE_AFTER),
            LockOutcome::Acquired(_)
        ));
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ロックファイルの mtime を `age` だけ過去へ動かす (テスト用)。
    fn backdate_lock(dir: &Path, age: std::time::Duration) {
        let f = std::fs::OpenOptions::new()
            .write(true)
            .open(dir.join("reconcile.lock"))
            .expect("backdate_lock: reconcile.lock を開けない");
        f.set_modified(std::time::SystemTime::now() - age)
            .expect("backdate_lock: mtime を動かせない");
    }

    /// ⚠️★★★ **長く走っている収束器のロックを奪わせない** (heartbeat)。
    ///
    /// O1 で未送信が 12 本以上溜まると 1 回の収束が 3600 秒を超える。更新が無いと、
    /// 走っている最中のロックが「古い」と判定されて奪われ、番号衝突と二重送信が起きる。
    #[test]
    fn a_refreshed_lock_is_not_taken_over_but_an_unrefreshed_one_is() {
        let two_hours = std::time::Duration::from_secs(2 * 60 * 60);

        // 対照: 更新が無いまま 2 時間経ったロックは奪われる (= 旧実装の壊れ方)。
        let a = tmpdir("hb_control");
        let held_a = match ReconcileLock::acquire(&a, LOCK_STALE_AFTER) {
            LockOutcome::Acquired(l) => l,
            _ => panic!("first lock must be acquired"),
        };
        backdate_lock(&a, two_hours);
        let stolen = ReconcileLock::acquire(&a, LOCK_STALE_AFTER);
        assert!(
            matches!(stolen, LockOutcome::Acquired(_)),
            "対照: 更新の無い古いロックは奪われる (このテストの前提)"
        );
        // ⚠️ 奪われた側の Drop が後続のロックを消す = 実害の再現 (ここでは片付けのため forget)。
        std::mem::forget(held_a);
        drop(stolen);
        let _ = std::fs::remove_dir_all(&a);

        // 本体: 走りながら refresh していれば、同じ 2 時間の遅れでも奪われない。
        let b = tmpdir("hb_refreshed");
        let held_b = match ReconcileLock::acquire(&b, LOCK_STALE_AFTER) {
            LockOutcome::Acquired(l) => l,
            _ => panic!("first lock must be acquired"),
        };
        backdate_lock(&b, two_hours);
        held_b.refresh();
        assert!(
            matches!(
                ReconcileLock::acquire(&b, LOCK_STALE_AFTER),
                LockOutcome::Busy
            ),
            "★ refresh したロックは奪われない"
        );
        drop(held_b);
        let _ = std::fs::remove_dir_all(&b);
    }

    /// 送信のたびにロックの mtime を確かめ、確かめたあと 2 時間前へ戻す送信層。
    /// ⚠️ `reconcile()` が 1 本ごとに `refresh` を呼んでいなければ、**2 本目**で赤くなる。
    struct LockProbeUploader {
        submission_dir: PathBuf,
        seen_fresh: Mutex<Vec<bool>>,
    }
    impl Uploader for LockProbeUploader {
        fn upload(&self, _file_name: &str, _bytes: &[u8]) -> Result<(), String> {
            let lock = self.submission_dir.join("reconcile.lock");
            let age = std::fs::metadata(&lock)
                .and_then(|m| m.modified())
                .map(|t| t.elapsed().unwrap_or_default())
                .unwrap_or(std::time::Duration::MAX);
            self.seen_fresh
                .lock()
                .unwrap()
                .push(age < std::time::Duration::from_secs(60));
            backdate_lock(
                &self.submission_dir,
                std::time::Duration::from_secs(2 * 60 * 60),
            );
            Ok(())
        }
    }

    /// ★ 未送信が複数あるとき、`reconcile()` が**送信の直前ごとに**ロックを更新している。
    #[test]
    fn reconcile_refreshes_the_lock_before_every_upload() {
        let d = tmpdir("hb_wire");
        let o = tmpdir("hb_wire_out");
        let end = 1_000_000_000_000_u64;
        write_closed_o1(&d, "gse_o1_00000000_090909.ndjson", end);
        write_closed_o1(&d, "gse_o1_00000000_100909.ndjson", end);
        write_closed_o1(&d, "gse_o1_00000000_110909.ndjson", end);
        let r = test_recipient();

        let up = LockProbeUploader {
            submission_dir: o.clone(),
            seen_fresh: Mutex::new(Vec::new()),
        };
        let rep = reconcile(&o1_opts(&d, &o, &r, end + GRACE), Some(&up));
        assert_eq!(rep.sent, 3, "{:?}", rep.errors);
        assert_eq!(
            *up.seen_fresh.lock().unwrap(),
            vec![true, true, true],
            "★ 2 本目以降の送信の前にもロックが更新されていること"
        );
        let _ = std::fs::remove_dir_all(&d);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ★ **梱包側と送信側の両方**で 1 本ごとに `refresh` が呼ばれる (N 本包む + M 本送る = N + M 回)。
    ///
    /// ⚠️ 上の `LockProbeUploader` は**送信側だけ**しか観測できない (梱包は uploader が最初に
    /// backdate する前に全部終わる)。→ 梱包側の呼び出しを消しても緑のままだった
    /// (code-reviewer HIGH・2026-09-27・変異で実測)。呼び出し回数で両方を固定する。
    #[test]
    fn refresh_is_called_once_per_package_and_once_per_upload() {
        let d = tmpdir("hb_count");
        let o = tmpdir("hb_count_out");
        let end = 1_000_000_000_000_u64;
        write_closed_o1(&d, "gse_o1_00000000_090909.ndjson", end);
        write_closed_o1(&d, "gse_o1_00000000_100909.ndjson", end);
        let r = test_recipient();

        REFRESH_CALLS.with(|c| c.set(0));
        let up = OkUploader(Mutex::new(Vec::new()));
        let rep = reconcile(&o1_opts(&d, &o, &r, end + GRACE), Some(&up));
        assert_eq!((rep.packaged, rep.sent), (2, 2), "{:?}", rep.errors);
        assert_eq!(
            REFRESH_CALLS.with(|c| c.get()),
            4,
            "★ 梱包 2 回 + 送信 2 回 = 4 回 (梱包側か送信側のどちらかを消すと減る)"
        );
        let _ = std::fs::remove_dir_all(&d);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ⚠️★★★ **奪われた側は、他人のロックを延命も削除もせず、中断する** (所有印)。
    ///
    /// A が走行中に更新が途切れて stale と判定され、B が奪った、という状況を作る。
    /// 旧実装は A の `refresh` が B のロックを延命し、A の `Drop` が B のロックを消した
    /// (code-reviewer / security-checker / Codex の 3 系統が一致して指摘)。
    #[test]
    fn a_run_that_lost_its_lock_neither_extends_nor_deletes_the_new_owners_lock() {
        let o = tmpdir("own");
        let a = match ReconcileLock::acquire(&o, LOCK_STALE_AFTER) {
            LockOutcome::Acquired(l) => l,
            _ => panic!("first lock must be acquired"),
        };
        // A の更新が途切れて 2 時間経った → B が奪う。
        backdate_lock(&o, std::time::Duration::from_secs(2 * 60 * 60));
        let b = match ReconcileLock::acquire(&o, LOCK_STALE_AFTER) {
            LockOutcome::Acquired(l) => l,
            _ => panic!("stale lock must be taken over by B"),
        };
        let b_body = std::fs::read_to_string(o.join("reconcile.lock")).unwrap();
        assert_ne!(b_body, a.token, "★ 所有印が A と B で別であること (前提)");
        // B のロックを 2 時間前へ戻しておく = A が延命したら分かる。
        backdate_lock(&o, std::time::Duration::from_secs(2 * 60 * 60));

        a.refresh();
        assert!(a.is_lost(), "★ 奪われたことを検知する");
        assert!(!b.is_lost());
        let mtime_age = std::fs::metadata(o.join("reconcile.lock"))
            .and_then(|m| m.modified())
            .unwrap()
            .elapsed()
            .unwrap();
        assert!(
            mtime_age > std::time::Duration::from_secs(60 * 60),
            "★ A の refresh が B のロックを延命してはならない"
        );

        drop(a);
        assert!(
            o.join("reconcile.lock").is_file(),
            "★ A の Drop が B のロックを消してはならない"
        );
        assert_eq!(
            std::fs::read_to_string(o.join("reconcile.lock")).unwrap(),
            b_body
        );
        drop(b);
        assert!(
            !o.join("reconcile.lock").exists(),
            "自分のロックは Drop で消える"
        );
        let _ = std::fs::remove_dir_all(&o);
    }

    /// 送信中にロックを奪われた (と分かった) 収束は、次の 1 本に進まず中断し、失敗として出す。
    struct StealLockUploader {
        submission_dir: PathBuf,
        calls: Mutex<usize>,
    }
    impl Uploader for StealLockUploader {
        fn upload(&self, _file_name: &str, _bytes: &[u8]) -> Result<(), String> {
            let mut n = self.calls.lock().unwrap();
            *n += 1;
            if *n == 1 {
                // 1 本目の送信中に、別の収束器がロックを奪った状況を再現する。
                let lock = self.submission_dir.join("reconcile.lock");
                std::fs::remove_file(&lock).unwrap();
                std::fs::write(&lock, "someone-else").unwrap();
            }
            Ok(())
        }
    }

    #[test]
    fn reconcile_stops_when_it_loses_the_lock_and_leaves_the_new_owners_lock() {
        let d = tmpdir("lost_run");
        let o = tmpdir("lost_run_out");
        let end = 1_000_000_000_000_u64;
        write_closed_o1(&d, "gse_o1_00000000_090909.ndjson", end);
        write_closed_o1(&d, "gse_o1_00000000_100909.ndjson", end);
        write_closed_o1(&d, "gse_o1_00000000_110909.ndjson", end);
        let r = test_recipient();

        let up = StealLockUploader {
            submission_dir: o.clone(),
            calls: Mutex::new(0),
        };
        let rep = reconcile(&o1_opts(&d, &o, &r, end + GRACE), Some(&up));
        assert_eq!(
            *up.calls.lock().unwrap(),
            1,
            "★ 奪われたら次の 1 本へ進まない"
        );
        assert_eq!(rep.sent, 1, "{:?}", rep.errors);
        assert_eq!(rep.unsent, 2, "★ 残りは次の機会に収束する (失われない)");
        assert!(
            rep.errors.iter().any(|e| e.contains("ロックを失いました")),
            "★ 黙って止めない: {:?}",
            rep.errors
        );
        assert_eq!(
            std::fs::read_to_string(o.join("reconcile.lock")).unwrap(),
            "someone-else",
            "★ 他の収束器のロックを消さない"
        );
        let _ = std::fs::remove_dir_all(&d);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ⚠️ ★ 猶予を短くすると、走っている収束器のロックを奪って番号衝突を再現してしまう。
    /// ★ 送信のタイムアウト (300 秒) × 10 ブロックより十分に長いことを固定する。
    #[test]
    fn the_stale_threshold_is_longer_than_a_worst_case_run() {
        assert!(
            LOCK_STALE_AFTER >= std::time::Duration::from_secs(300 * 10),
            "LOCK_STALE_AFTER が短すぎる (送信タイムアウト 300s × 10 ブロックを超えること)"
        );
    }

    /// ★ ロックファイルを未送信として数えない（`.age` ではないので）。
    #[test]
    fn the_lock_file_is_not_counted_as_a_submission() {
        let o = tmpdir("lockcount");
        let _l = ReconcileLock::acquire(&o, LOCK_STALE_AFTER);
        assert_eq!(crate::submission::unsent_count(&o, "P012"), 0);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ⚠️★ **HTTP 200 だけを成功と読まない。** GAS は例外でも 200 を返す。
    #[test]
    fn only_an_explicit_ack_counts_as_success() {
        assert!(response_is_ok(r#"{"ok":true,"saved":"P012_block01.age"}"#));
        assert!(response_is_ok("{ \"ok\" : true }"));
        assert!(!response_is_ok(r#"{"ok":false,"error":"bad secret"}"#));
        assert!(!response_is_ok("<html>Google Apps Script error</html>"));
        assert!(!response_is_ok(""));
        // ⚠️ ★ **本文に文字列として現れるだけの `"ok":true` を成功と読まない。**
        //   部分一致で判定していたときはこれを通していた。
        assert!(!response_is_ok(r#"{"echo":"\"ok\":true"}"#));
        assert!(
            !response_is_ok(r#"{"ok":"true"}"#),
            "文字列の \"true\" は真ではない"
        );
    }

    // -----------------------------------------------------------------------
    // ⚠️★★★ O1 (R3-a): 48 時間の猶予つき自動提出 (研究者判断 O1-2)
    // -----------------------------------------------------------------------

    const GRACE: u64 = crate::o1::SUBMIT_GRACE_MS;

    /// ⚠️★★★ **猶予の中にあるファイルは候補にならない。**
    ///
    /// ★ これが本機能の値打ちである: 包んでしまうと `delete_time_range` が
    /// `.age` に届かないので (`redaction.rs` は `.age` を触らない)、
    /// ⚠️ **ADR-014 判断 3 の根拠 3「被験者が消せる」が崩れる。**
    #[test]
    fn o1_candidates_appear_only_after_the_grace_window() {
        let d = tmpdir("o1grace");
        let end = 1_000_000_000_000_u64;
        write_closed_o1(&d, "gse_o1_00000000_010101.ndjson", end);

        // 閉じた直後: まだ候補にならない
        assert!(closed_o1_sessions(&d, end, GRACE).is_empty());
        // 47 時間 59 分 59.999 秒: まだ
        assert!(closed_o1_sessions(&d, end + GRACE - 1, GRACE).is_empty());
        // ちょうど 48 時間: 候補になる
        assert_eq!(closed_o1_sessions(&d, end + GRACE, GRACE).len(), 1);

        let _ = std::fs::remove_dir_all(&d);
    }

    /// ⚠️★★★ **猶予の中なら、被験者が消したものは送られない** (削除保証の実体)。
    ///
    /// ★ 「閉じた → 被験者が区間指定削除 → 猶予が明ける」の順で走らせ、
    /// **包まれた `.age` に消した行が入っていないこと**を、
    /// ⚠️ **`.age` が作られる前に消せること**として固定する。
    #[test]
    fn o1_deletion_during_the_grace_window_removes_the_data_before_packaging() {
        let d = tmpdir("o1delete");
        let end = 1_000_000_000_000_u64;
        let name = "gse_o1_00000000_020202.ndjson";
        write_closed_o1(&d, name, end);

        // ① 猶予の中なので、まだ `.age` は作られていない
        assert!(closed_o1_sessions(&d, end + 1000, GRACE).is_empty());

        // ② 被験者が「この時間帯を消して」を実行する (★ `key` 行の t=1200 を含む区間)
        let outcome = crate::redaction::redact_dir(&d, 1_100, 1_300, None).unwrap();
        assert_eq!(
            outcome.lines_removed, 1,
            "★ 区間指定削除が O1 のファイルに効かなければ削除保証が崩れる"
        );

        // ③ 猶予が明けた。★ ファイルは候補になるが、消した行はもう無い
        let found = closed_o1_sessions(&d, end + GRACE, GRACE);
        assert_eq!(found.len(), 1);
        let text = std::fs::read_to_string(&found[0]).unwrap();
        assert!(
            !text.contains("\"t\":1200"),
            "⚠️ 消したはずの行が提出候補に残っている: {text}"
        );
        // ★ 消していない行は残る (⚠️ 削除が「全消し」に化けていないこと)
        assert!(text.contains("\"t\":5000"), "{text}");

        let _ = std::fs::remove_dir_all(&d);
    }

    /// ⚠️★★★ **G1 と O1 が互いのファイルを拾わない。**
    ///
    /// ★ `~/Documents/GSE-sessions` は participant 非依存の共有ディレクトリなので、
    /// 同じ端末に Phase1 / G1 / O1 の記録が同居しうる。
    #[test]
    fn o1_and_g1_candidate_sets_do_not_overlap() {
        let d = tmpdir("o1mix");
        let end = 1_000_000_000_000_u64;
        write_closed(&d, "gse_00000000_030303.ndjson"); // G1
        write_closed_non_g1(&d, "gse_00000000_040404.ndjson"); // Phase1
        write_closed_o1(&d, "gse_o1_00000000_050505.ndjson", end); // O1
        write_open(&d, "gse_o1_00000000_060606.ndjson"); // O1 書きかけ

        let g1 = closed_sessions(&d);
        assert_eq!(g1.len(), 1);
        assert!(g1[0].to_string_lossy().contains("gse_00000000_030303"));

        let o1 = closed_o1_sessions(&d, end + GRACE, GRACE);
        assert_eq!(o1.len(), 1, "★ 書きかけ / G1 / Phase1 を拾ってはならない");
        assert!(o1[0].to_string_lossy().contains("gse_o1_00000000_050505"));

        let _ = std::fs::remove_dir_all(&d);
    }

    /// ⚠️★ **`g1_mode` を持つファイルは、名前が `gse_o1_*` でも O1 では拾わない。**
    /// ★ 二重に提出される経路を構造的に消す。
    #[test]
    fn o1_never_picks_up_a_file_marked_as_g1() {
        let d = tmpdir("o1g1mark");
        write_closed(&d, "gse_o1_00000000_070707.ndjson"); // 名前は O1・中身は G1
        assert!(closed_o1_sessions(&d, u64::MAX / 2, GRACE).is_empty());
        let _ = std::fs::remove_dir_all(&d);
    }

    /// ⚠️★★★ **O1 は承認を求めずに送る** (同意文書 §5 の逐語「自動的に…送ります」)。
    ///
    /// ★ 対照として、同じ状態を G1 モードで回すと **1 本も送られない** ことも見る。
    #[test]
    fn o1_sends_without_the_approval_marker_while_g1_still_requires_it() {
        let d = tmpdir("o1auto");
        let o = tmpdir("o1auto_out");
        let end = 1_000_000_000_000_u64;
        write_closed_o1(&d, "gse_o1_00000000_080808.ndjson", end);
        let r = test_recipient();

        // ★ G1 モードでは O1 のファイルを 1 本も見ない (包みもしない)
        let g1_report = reconcile(&opts(&d, &o, &r), None);
        assert_eq!(g1_report.packaged, 0);

        // ★ O1 モード: 猶予明けに包み、⚠️ `.age.ok` が無くても送る
        let up = OkUploader(Mutex::new(Vec::new()));
        let report = reconcile(&o1_opts(&d, &o, &r, end + GRACE), Some(&up));
        assert_eq!(report.packaged, 1, "{:?}", report.errors);
        assert_eq!(report.sent, 1, "{:?}", report.errors);
        assert_eq!(report.unsent, 0);
        // ⚠️ O1 に「確認待ち」は無い (画面に嘘を出さない)
        assert_eq!(report.awaiting_approval, 0);

        // ★ 対照: 同じ `.age` を G1 の規則で送ろうとすると、承認が無いので送らない
        let up2 = OkUploader(Mutex::new(Vec::new()));
        let g1_again = reconcile(&opts(&d, &o, &r), Some(&up2));
        assert_eq!(g1_again.sent, 0);

        let _ = std::fs::remove_dir_all(&d);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ★ 何度回しても同じ状態に収束する (べき等) —— O1 でも壊れない。
    #[test]
    fn o1_reconcile_is_idempotent() {
        let d = tmpdir("o1idem");
        let o = tmpdir("o1idem_out");
        let end = 1_000_000_000_000_u64;
        write_closed_o1(&d, "gse_o1_00000000_090909.ndjson", end);
        let r = test_recipient();
        let now = end + GRACE;

        let up = OkUploader(Mutex::new(Vec::new()));
        let first = reconcile(&o1_opts(&d, &o, &r, now), Some(&up));
        assert_eq!((first.packaged, first.sent), (1, 1), "{:?}", first.errors);
        let second = reconcile(&o1_opts(&d, &o, &r, now), Some(&up));
        assert_eq!(
            (second.packaged, second.sent),
            (0, 0),
            "{:?}",
            second.errors
        );
        assert_eq!(up.0.lock().unwrap().len(), 1, "★ 二重送信しない");

        let _ = std::fs::remove_dir_all(&d);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ⚠️★★★ **O1 の収束が、承認していない G1 の提出物を送らない。**
    ///
    /// ★ 提出物フォルダは participant 単位の**共有ディレクトリ**なので、
    /// 同じ端末・同じ ID で G1 を先にやった被験者の未承認 `.age` が残りうる。
    /// ⚠️ 送ってしまうと **D-14 の承認ゲートが O1 経由で無効化され、
    /// 別研究の同意範囲のデータが送られる** (code-reviewer / security-checker が一致して指摘)。
    #[test]
    fn o1_never_sends_an_unapproved_g1_submission() {
        let d = tmpdir("o1notg1");
        let o = tmpdir("o1notg1_out");
        let end = 1_000_000_000_000_u64;
        let r = test_recipient();

        // ① G1 のブロックを 1 本包む (⚠️ 承認しない = `.age.ok` を置かない)
        write_closed(&d, "gse_00000000_010101.ndjson");
        let g1 = reconcile(&opts(&d, &o, &r), None);
        assert_eq!(g1.packaged, 1, "{:?}", g1.errors);

        // ② O1 のファイルを 1 本置き、猶予明けに O1 モードで回す
        write_closed_o1(&d, "gse_o1_00000000_020202.ndjson", end);
        let up = OkUploader(Mutex::new(Vec::new()));
        let report = reconcile(&o1_opts(&d, &o, &r, end + GRACE), Some(&up));

        assert_eq!(report.packaged, 1, "{:?}", report.errors);
        let sent = up.0.lock().unwrap().clone();
        assert_eq!(sent.len(), 1, "★ 送ってよいのは O1 の 1 本だけ: {sent:?}");
        assert!(
            sent[0].contains("gse_o1_"),
            "⚠️★★★ 未承認の G1 提出物が O1 経由で送られた: {sent:?}"
        );
        // ⚠️ 画面に出る件数も O1 のものだけを数える (送る対象と同じ規則)
        assert_eq!(report.unsent, 0, "★ O1 の未送信は 0 のはず");

        // ★ G1 の `.age` は**残っている** (失われていない・承認すれば送られる)
        assert_eq!(
            crate::submission::unsent_count(&o, "P012"),
            1,
            "★ G1 の未承認分はローカルに残るだけで、失われてはならない"
        );

        let _ = std::fs::remove_dir_all(&d);
        let _ = std::fs::remove_dir_all(&o);
    }

    /// ⚠️★★★ **名前だけを頼りにしない** —— リネームした Phase1 の記録を O1 として送らない
    /// (cross-review / Codex HIGH・2026-08-27)。
    ///
    /// ★ セッション置き場は**被験者が書き込めるフォルダ**なので、`gse_o1_*` へのリネームは
    /// 事故でも故意でも起こりうる。⚠️ 通すと **承認を経ていない別研究の記録が自動送信される**。
    /// → ★ O1 は `start_session` を通らないので **`session_start` 行を 1 本も持たない**。
    #[test]
    fn a_renamed_phase1_session_is_not_submitted_as_o1() {
        let d = tmpdir("o1renamed");
        // ⚠️ Phase1 相当 (`g1_mode` は無いが `session_start` 行を持つ) を O1 の名前で置く
        std::fs::write(
            d.join("gse_o1_00000000_101112.ndjson"),
            "{\"type\":\"meta\",\"session_start\":1000,\"hmm_version\":\"0.5.0\"}\n\
             {\"type\":\"session_start\",\"t\":1000}\n\
             {\"type\":\"key\",\"t\":1200,\"vk\":74,\"press\":true}\n\
             {\"type\":\"meta\",\"session_end\":9000}\n",
        )
        .unwrap();
        assert!(
            closed_o1_sessions(&d, u64::MAX / 2, GRACE).is_empty(),
            "⚠️★★★ リネームだけで O1 の自動提出に載せられてはならない"
        );

        // ★ 対照: 本物の O1 (押下の痕跡が無い) は拾われる
        write_closed_o1(&d, "gse_o1_00000000_202020.ndjson", 9000);
        let found = closed_o1_sessions(&d, u64::MAX / 2, GRACE);
        assert_eq!(found.len(), 1);
        assert!(found[0].to_string_lossy().contains("202020"));

        let _ = std::fs::remove_dir_all(&d);
    }

    /// ⚠️★ **UTF-8 として不正な 1 行があっても、そのファイルを黙って捨てない。**
    ///
    /// ★ 以前は `line.ok()?` で `None` を返し、**提出候補から永久に外れた** (fail-silent)。
    #[test]
    fn a_single_invalid_utf8_line_does_not_hide_the_whole_file() {
        use std::io::Write;
        let d = tmpdir("o1badutf8");
        let end = 1_000_000_000_000_u64;
        let path = d.join("gse_o1_00000000_030303.ndjson");
        {
            let mut f = std::fs::File::create(&path).unwrap();
            f.write_all(
                b"{\"type\":\"meta\",\"session_start\":1000,\"hmm_version\":\"0.5.0\",\"o1_mode\":\"marker\"}\n",
            )
            .unwrap();
            // ⚠️ 不正な UTF-8 を 1 行混ぜる
            f.write_all(&[0xff, 0xfe, 0x00, b'\n']).unwrap();
            f.write_all(b"{\"type\":\"key\",\"t\":1200,\"vk\":74,\"press\":true}\n")
                .unwrap();
            f.write_all(format!("{{\"type\":\"meta\",\"session_end\":{end}}}\n").as_bytes())
                .unwrap();
        }
        let found = closed_o1_sessions(&d, end + GRACE, GRACE);
        assert_eq!(
            found.len(),
            1,
            "⚠️ 壊れた 1 行でファイルごと提出候補から外れている (fail-silent)"
        );
        let _ = std::fs::remove_dir_all(&d);
    }

    /// `meta` 行から `session_end` を読む手書きパーサの健全性。
    #[test]
    fn meta_u64_parser_reads_only_the_named_key() {
        let line = r#"{"type":"meta","session_end":1700000000000}"#;
        assert_eq!(parse_meta_u64(line, "session_end"), Some(1_700_000_000_000));
        assert_eq!(parse_meta_u64(line, "session_start"), None);
        // ⚠️ 数字が無い / 壊れている行では None (★ 0 に倒さない = 猶予を勝手に満了させない)
        assert_eq!(parse_meta_u64(r#"{"session_end":}"#, "session_end"), None);
        assert_eq!(
            parse_meta_u64(r#"{"session_end":"x"}"#, "session_end"),
            None
        );
    }

    /// ⚠️★★★ **孤児回収 → 収束器 の結合テスト**（★ cross-review で「無い」と指摘された穴）。
    ///
    /// ★ 単体テストは「`session_end` が書かれたか」しか見ない。⚠️ 本当に確かめたいのは
    /// **「閉じたファイルが *実際に* 提出候補になり、しかも *即座には* ならない」**である
    /// （★ 48 時間の猶予＝削除保証が生きていること）。
    #[test]
    fn a_recovered_orphan_becomes_a_candidate_only_after_the_grace_window() {
        let d = tmpdir("o1_orphan_e2e");
        // ★ O1 の「開いたまま」のファイル（⚠️ `session_end` が無い）。
        std::fs::write(
            d.join("gse_o1_20260901_101112.ndjson"),
            "{\"type\":\"meta\",\"session_start\":1000,\"hmm_version\":\"0.3.0\",\"o1_mode\":\"marker\"}\n\
             {\"type\":\"key\",\"t\":1200,\"vk\":74,\"press\":true}\n",
        )
        .unwrap();

        let now = 1_788_000_000_000u64;
        let grace = crate::o1::SUBMIT_GRACE_MS;

        // ⚠️ 回収する前は候補にならない（★ これが今回塞いだ欠陥そのもの）。
        assert!(
            closed_o1_sessions(&d, now + grace * 10, grace).is_empty(),
            "★ 回収前に候補になってはならない"
        );

        // ★ 回収する。
        assert_eq!(crate::o1::close_orphaned_sessions(&d, None, now).closed, 1);

        // ⚠️★★★ **直後は候補にならない**（★ 被験者が消せる 48 時間）。
        assert!(
            closed_o1_sessions(&d, now, grace).is_empty(),
            "⚠️ 閉じた直後に提出候補になっている = 削除保証が消えている"
        );
        assert!(
            closed_o1_sessions(&d, now + grace - 1, grace).is_empty(),
            "⚠️ 猶予が 48 時間より短い"
        );

        // ★ 48 時間ちょうどで候補になる。
        let ready = closed_o1_sessions(&d, now + grace, grace);
        assert_eq!(ready.len(), 1, "★ 猶予を過ぎたら候補になるべき");
        assert_eq!(
            ready[0].file_name().and_then(|s| s.to_str()),
            Some("gse_o1_20260901_101112.ndjson")
        );
    }

    /// ⚠️★★ **診断行だけのファイルは回収もされないし候補にもならない**（★ 両側で一致すること）。
    #[test]
    fn a_diagnostic_only_orphan_is_ignored_by_both_sides() {
        let d = tmpdir("o1_orphan_diag");
        let p = d.join("gse_o1_20260901_101112.ndjson");
        let body = "{\"type\":\"meta\",\"session_start\":1000,\"o1_mode\":\"marker\"}\n\
                    {\"type\":\"ime_state\",\"t\":1200,\"open\":false}\n";
        std::fs::write(&p, body).unwrap();
        let now = 1_788_000_000_000u64;
        assert_eq!(
            crate::o1::close_orphaned_sessions(&d, None, now),
            crate::o1::OrphanSweep::default()
        );
        assert_eq!(std::fs::read_to_string(&p).unwrap(), body);
        assert!(!has_any_data_row(&p), "★ 収束器側も「中身なし」と見ること");
    }
}
