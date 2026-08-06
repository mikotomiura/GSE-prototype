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
/// (⚠️ 送信のタイムアウトは 180 秒 × 未送信本数)。そこへブロック終了の 1 回が重なると:
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
                Ok(_) => return LockOutcome::Acquired(Self { path }),
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

impl Drop for ReconcileLock {
    fn drop(&mut self) {
        let _ = std::fs::remove_file(&self.path);
    }
}

/// ロックが残骸とみなされるまでの時間。
///
/// ★ 送信のタイムアウト (180 秒) × 想定される未送信の最大本数 (10 ブロック) を超える値にする。
/// ⚠️ 短すぎると、正常に走っている収束器のロックを奪って上の衝突を再現してしまう。
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
        if !line.contains(r#""type":"meta""#) {
            continue;
        }
        if line.contains(r#""session_end""#) {
            closed = true;
        }
        if line.contains(r#""g1_mode""#) {
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
    let _lock = match ReconcileLock::acquire(&opts.submission_dir, LOCK_STALE_AFTER) {
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
    for input in closed_sessions(&opts.session_dir) {
        let stem = session_stem(&input);
        if age_for_stem(&opts.submission_dir, &stem).is_some() {
            continue; // 既に包んである (手動提出で作った旧形式も含む)
        }
        let block = next_block_number(&opts.submission_dir, &opts.participant);
        let out_name = age_file_name(&opts.participant, block, &stem);
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
    if let Some(up) = uploader {
        for age in
            crate::submission::approved_unsent_age_files(&opts.submission_dir, &opts.participant)
        {
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

    report.unsent = unsent_count(&opts.submission_dir, &opts.participant);
    report.awaiting_approval =
        crate::submission::awaiting_approval_count(&opts.submission_dir, &opts.participant);
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
            // 実測は 300 KB で 1.45 s。⚠️ ★ Drive 保存を含む本番 doPost の所要時間は **未実測**
            // なので、余裕を大きく取る (`gas-measurements.md` §3)。
            .timeout(std::time::Duration::from_secs(180))
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

    /// ⚠️ ★ 猶予を短くすると、走っている収束器のロックを奪って番号衝突を再現してしまう。
    /// ★ 送信のタイムアウト (180 秒) × 10 ブロックより十分に長いことを固定する。
    #[test]
    fn the_stale_threshold_is_longer_than_a_worst_case_run() {
        assert!(
            LOCK_STALE_AFTER >= std::time::Duration::from_secs(180 * 10),
            "LOCK_STALE_AFTER が短すぎる (送信タイムアウト 180s × 10 ブロックを超えること)"
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
}
