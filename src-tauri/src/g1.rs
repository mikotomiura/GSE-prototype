//! G1 統制タスク実験の「G1 モード」判定 (OS API 非依存)。
//!
//! ## なぜこのモジュールがあるか
//!
//! G1 は `experiments/20260801-controlled-friction-task/protocol.md §1` (D-1) により
//! **1 ブロック = 1 セッション = NDJSON 1 ファイル**である。これを満たす手段が
//! 「ブロックごとにアプリを起動し直す」しか無く、被験者は 10 回再起動していた。
//! さらに `§4.4` は 5 分ブロックを凍結しているが、P-1 (2026-08-04) は
//! **被験者が自分では計らない**ことを実測で示した (11:37 / 4:04 / 7:14 / 9:57)。
//! `preregistration.md §3.6` がブロックの事後除外を禁じているので、
//! **止められるのは実施中だけ**である。
//!
//! → 本モジュールは「いま G1 の実施中か」だけを判定する。効果 (ローテート・5 分での
//! ブロック終了・プローブ停止・二重起動の fail-loud) は `lib.rs` が適用する。
//!
//! ## 引き金は 2 本ある (`preregistration.md §5.4` 第 10 版 / D-7)
//!
//! - **マーカー**: 実行ファイルを包むフォルダに `g1.mode` がある (配布形・既定の経路)
//! - **環境変数**: `GSE_G1_MODE=1` (開発・検証用の第 2 経路)
//!
//! ⚠️ ★ どちらも **起動時に 1 回だけ**読む。実行時トグルにしてはならない。
//! `lib.rs` のプローブスケジューラは「スレッドごと起こさない」ことで
//! 「発火はしたが黙殺した」状態を構造的に消しており、実行時に切り替えられると崩れる。
//!
//! ## ⚠️ マーカーをバンドルの中に置けない理由 (実測・D-7)
//!
//! `.app` の中にファイルを足すと `codesign --verify --strict` が
//! `a sealed resource is missing or invalid` で落ちる。★ **置き場所はバンドルの外しかない。**

use std::path::{Path, PathBuf};

/// 1 ブロックの長さ。`preregistration.md §2.3` が凍結した 5 分。
///
/// ⚠️ ★ この値は判定基準ではなく**実施手順**である (`§2.8` が「パイロットを見て変えてよい」と
/// している範囲)。★ **短くしても長くしても合格経路は 1 本も増えない**が、変えたら
/// `§2.3` と `writing-pad.html` の `BLOCK_MS` を**同時に**直すこと。
pub const BLOCK_DURATION_MS: u64 = 5 * 60 * 1000;

/// フォルダに置くマーカーのファイル名 (D-7)。
pub const MARKER_FILE_NAME: &str = "g1.mode";

/// G1 モードを立てた引き金。`meta` 行に記録して事後検証できるようにする
/// (⚠️ ★ マーカーが外れると黙って通常モードになるため・D-7)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum G1Source {
    /// 実行ファイルを包むフォルダに `g1.mode` があった (配布形)。
    Marker,
    /// 環境変数 `GSE_G1_MODE=1` が立っていた (開発・検証用)。
    Env,
}

impl G1Source {
    /// NDJSON `meta` 行に書く固定文字列。
    pub fn as_str(self) -> &'static str {
        match self {
            G1Source::Marker => "marker",
            G1Source::Env => "env",
        }
    }
}

/// 環境変数による G1 モード判定 (純関数)。
///
/// ★ `"1"` に**完全一致**したときだけ立てる。`analysis::probe_scheduler::probes_disabled_by_env`
/// と意図的に同じ厳しさにしてある: `"true"` / `"yes"` / `" 1"` を通すと
/// 「立てたつもり」が生まれ、⚠️ **`§3.6` が事後除外を禁じているので取り返せない**。
pub fn g1_enabled_by_env(value: Option<&str>) -> bool {
    matches!(value, Some("1"))
}

/// 実行ファイルからマーカーを置くフォルダまでの階層数。
///
/// - macOS: `…/G1-app/gse-next.app/Contents/MacOS/gse-next` → **4 階層上**が `G1-app`
/// - Windows: `…\G1-app\gse-next.exe` → **1 階層上**が `G1-app`
///
/// ★ `lib.rs` の `gse-submit` 解決 (同梱バイナリを `current_exe` の隣から探す) と
/// **同じプラットフォーム分岐**である。先例に倣っているだけで新しい仕組みではない。
pub const fn exe_to_folder_levels() -> usize {
    if cfg!(target_os = "macos") {
        4
    } else {
        1
    }
}

/// `exe` から `levels_up` 階層だけ上のディレクトリを返す (純関数・プラットフォーム非依存)。
///
/// ★ プラットフォーム分岐を引数に追い出してあるので、**両 OS の形を片方の OS 上で検証できる**。
pub fn folder_up(exe: &Path, levels_up: usize) -> Option<PathBuf> {
    let mut dir = exe;
    for _ in 0..levels_up {
        dir = dir.parent()?;
    }
    Some(dir.to_path_buf())
}

/// `exe` に対応するマーカーの想定パス (純関数)。
pub fn marker_path_for(exe: &Path, levels_up: usize) -> Option<PathBuf> {
    Some(folder_up(exe, levels_up)?.join(MARKER_FILE_NAME))
}

/// G1 モードの判定 (純関数)。IO は呼び出し側が行い、その結果だけを渡す。
///
/// ★ **マーカーを優先**する。配布形が既定の経路であり、`meta` 行に「どちらで立ったか」を
/// 残したいときに、より強い根拠 (物として残るもの) を書きたいため。
pub fn decide(marker_exists: bool, env_value: Option<&str>) -> Option<G1Source> {
    if marker_exists {
        Some(G1Source::Marker)
    } else if g1_enabled_by_env(env_value) {
        Some(G1Source::Env)
    } else {
        None
    }
}

/// 実行環境から G1 モードを判定する (IO あり)。`run()` から**起動時に 1 回だけ**呼ぶ。
///
/// マーカーの探索に失敗した場合 (`current_exe()` が取れない・階層が足りない) は
/// **マーカー無しとして扱う**。⚠️ ★ ここで落とさないのは、通常運用 (G1 でない) を
/// 壊さないためである。G1 実施時にマーカーが読めなければ、画面表示と `meta` 行が
/// 「G1 モードでない」と告げるので **fail-loud は UI 側が担う**。
pub fn detect_from_env() -> Option<G1Source> {
    let marker_exists = std::env::current_exe()
        .ok()
        .and_then(|exe| marker_path_for(&exe, exe_to_folder_levels()))
        .map(|p| p.is_file())
        .unwrap_or(false);
    let env_value = std::env::var("GSE_G1_MODE").ok();
    decide(marker_exists, env_value.as_deref())
}

/// 実行ファイル名（プロセス列挙の照合に使う）。
pub const PROCESS_NAME: &str = if cfg!(windows) {
    "gse-next.exe"
} else {
    "gse-next"
};

/// `pgrep` / `tasklist` の出力から **自分以外の同名プロセス** の PID を拾う (純関数)。
///
/// ⚠️ ★ なぜ `tauri-plugin-single-instance` だけでは足りないか（2026-08-05 実測）:
/// プラグインは **両方のビルドがプラグインを持っている**ときにしか効かない。
/// 実測では、**プラグインの無い旧ビルド**（被験者の `/Applications` にある Phase1 用）と
/// 新ビルドが **2 プロセス同時に走った**。★ これは `protocol.md §2-3` が言う
/// 「打鍵が 2 本の NDJSON に割れる」そのものである。
/// → G1 モードでは**プロセス名でも見る**。★ 二重化であって置き換えではない。
pub fn other_pids_from_pgrep(output: &str, self_pid: u32) -> Vec<u32> {
    output
        .lines()
        .filter_map(|l| l.trim().parse::<u32>().ok())
        .filter(|p| *p != self_pid)
        .collect()
}

/// Windows `tasklist /FO CSV /NH` の出力から自分以外の PID を拾う (純関数)。
///
/// 形式: `"gse-next.exe","17456","Console","3","47,644 K"`
///
/// ## ★ 2026-08-06 に Windows 実機で実出力を採取した
///
/// 採取記録は `.steering/20260806-g1-followups-and-windows-verification/windows-measurements.md`
/// (M-1 / M-2)。環境は `Windows 10.0.26200.8973` / ロケール `ja-JP` / コンソール CP `65001`。
/// 下の `tasklist_*` テストは **その生出力をそのまま**入力にしてある。
///
/// ★ 実測で分かったこと:
/// - 該当プロセスが無いとき `tasklist` は **`rc=0`** で
///   `INFO: No tasks are running which match the specified criteria.` を **stdout** に出す。
///   ★ 本関数は `o.stdout` を読むので、⚠️ **この行は確実にここへ渡る**。
/// - ⚠️★★ **同じ 1 台で文言が英語にも日本語にもなった** (M-1 / M-9)。
///   `cmd.exe` 直叩き = 英語 ／ PowerShell 経由 (`& cmd.exe /c …`) = 日本語
///   (`情報: 指定された条件に一致するタスクは実行されていません。`)。★ 条件の違いは**未特定**。
///   → ★ だからこそ本関数は **「数値に見える 2 列目」しか拾わない**設計を維持する
///   (何語でも安全側 = 検出なしに倒れる)。⚠️ **文言を列挙する実装にしてはならない。**
/// - `/FO CSV` を付けても **この INFO 行は CSV 化されない**（1 行そのまま出る）。
/// - メモリ列 `"47,644 K"` のカンマは、区切りが `","`(引用符込み) なので**影響しない**。
///
/// ## ✅ ★ 経路全体が Windows 実機で走ったことも実測した (M-8 / 陽性対照 E-1)
///
/// ⚠️ ★ **同名 exe の二重起動では 2 行を捕まえられない**（実測）。
/// `tauri-plugin-single-instance` が 2 個目を **14 ms** で終了させるので、`tasklist` 1 回
/// (≒57 ms) より短く、57 ms 間隔 209 サンプルでも **2 行は 1 度も観測されなかった**。
/// → ★ そのとき出る警告は `second-instance-blocked` 由来であって**本関数の経路ではない**。
///
/// ★ そこで **プラグインを持たない `gse-next.exe` という名前の別プロセス**を先に起こして
/// 「本当に 2 プロセス」を作り、**偽 `tasklist.exe` を配布フォルダに置いたまま**検査を走らせた。
/// ⚠️ これは `decisions.md` R-8 の「プラグインの無い旧ビルドと共存した」実測と**同じ形**である。
/// 結果、⚠️ **警告が出た**。→ ★ この 1 回で 3 つ同時に言える:
///
/// 1. `other_instance_running()` が Windows で **実際に走った**（空振り合格ではない）
/// 2. 使われたのは **System32 の本物**（絶対パス指定が効いている。偽 exe の痕跡ファイルは無し）
/// 3. **本関数が実機の CSV を実際にパースして PID を拾えた**
///
/// ## ⚠️ ★ それでも実測していないこと
///
/// ★ 2 行を作ったのは **代用プロセス**であって、**本物の GSE が 2 個並んだ状態ではない**。
/// 被験者の実環境（Phase1 の旧 `gse-next.exe` が残っている）そのものは再現していない。
pub fn other_pids_from_tasklist(output: &str, self_pid: u32) -> Vec<u32> {
    output
        .lines()
        .filter_map(|l| {
            let cols: Vec<&str> = l.split("\",\"").collect();
            if cols.len() < 2 {
                return None;
            }
            cols[1].trim_matches('"').trim().parse::<u32>().ok()
        })
        .filter(|p| *p != self_pid)
        .collect()
}

/// 自分以外に GSE が動いているかを OS に聞く (IO あり)。
///
/// ★ 判定できなかった場合は **`false`**（= 動いていない扱い）に倒す。
/// ⚠️ 列挙に失敗しただけで被験者の実施を止めるほうが害が大きいため。
/// ★ その代わり、**止めるのではなく画面に出す**設計にしてある（呼び出し側）。
pub fn other_instance_running() -> bool {
    let self_pid = std::process::id();
    let out = if cfg!(windows) {
        // ⚠️★ **絶対パスで叩く。** `Command::new("tasklist")` は PATH 探索になり、Windows の
        // 探索順は「子プロセス指定 PATH → **`current_exe()` のディレクトリ** → System32 → …」
        // である。★ **配布フォルダ (`G1-app`) は被験者が解凍する書き込み可能な場所**で、
        // アプリと同階層に `tasklist.exe` を置かれると **System32 の本物より先に**起動する。
        // ★ これは本タスクで記録した「zsh の `log` ビルトインで偽の緑を踏んだ」と**同型の罠**であり、
        // 同じ直し方 (絶対パス) で塞ぐ。`SystemRoot` が取れなければ**検査を諦める**。
        let system_root = match std::env::var("SystemRoot") {
            Ok(v) if !v.is_empty() => v,
            _ => {
                tracing::warn!("G1: SystemRoot not set; skipping duplicate-instance check");
                return false;
            }
        };
        let tasklist = std::path::Path::new(&system_root)
            .join("System32")
            .join("tasklist.exe");
        let mut cmd = std::process::Command::new(tasklist);
        cmd.args([
            "/FI",
            &format!("IMAGENAME eq {}", PROCESS_NAME),
            "/FO",
            "CSV",
            "/NH",
        ]);
        // ★ GUI アプリから起動するとコンソール窓が一瞬光り、被験者に見える。
        //   同 repo に先例あり (lib.rs の診断コマンド)。CREATE_NO_WINDOW = 0x0800_0000。
        #[cfg(windows)]
        {
            use std::os::windows::process::CommandExt;
            cmd.creation_flags(0x0800_0000);
        }
        cmd.output()
            .ok()
            .map(|o| (String::from_utf8_lossy(&o.stdout).to_string(), true))
    } else {
        // 同上。`pgrep` は PATH 依存にせず絶対パスで呼ぶ (macOS / Linux とも /usr/bin)。
        std::process::Command::new("/usr/bin/pgrep")
            .args(["-x", PROCESS_NAME])
            .output()
            .ok()
            .map(|o| (String::from_utf8_lossy(&o.stdout).to_string(), false))
    };
    match out {
        Some((text, true)) => !other_pids_from_tasklist(&text, self_pid).is_empty(),
        Some((text, false)) => !other_pids_from_pgrep(&text, self_pid).is_empty(),
        None => false,
    }
}

// ---------------------------------------------------------------------------
// 「開始する」を押したときにログをどうするか (G-1・2026-08-19)
// ---------------------------------------------------------------------------

/// 「開始する」の押下に対して**ログファイルをどう扱うか**。
///
/// ★ 判定だけをここに置き、効果 (実際の送信・カウンタ操作) は `lib.rs` が適用する
/// (本モジュール冒頭の方針どおり)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StartAction {
    /// ★ **通常運用 (G1 でない)。** ローテートも計数もしない ＝ 挙動を 1 バイトも変えない。
    NotG1,
    /// G1 の**このプロセスで最初のブロック**。起動時に開いたファイルをそのまま使う
    /// (ローテートしない) が、★ `G1_BLOCKS_STARTED` は**増やす**。
    FirstBlock,
    /// 新しいブロックとしてローテートする。★ `G1_BLOCKS_STARTED` を**増やす**経路。
    RotateForNewBlock,
    /// ⚠️★★★ **セッション実行中に再び「開始する」が押された** (＝ G-1)。
    /// 前のセッションを閉じてから新しいファイルを開く。★ カウンタは**増やさない**。
    RotateForRestart,
    /// ⚠️★★★ **`record_session_meta` が失敗した直後の再押下**。
    /// ★ **ログを 1 行も書かない** (ローテートもしないし `session_start` も積まない)。
    ///
    /// ## なぜ独立の経路が要るか (code-reviewer HIGH・2026-08-19)
    ///
    /// `record_session_meta` が失敗すると、フロントは `isStarted` へ進まず
    /// **明示的に再押下を促す**。⚠️ このとき backend の `session_active` は**既に true**なので、
    /// 素朴に書くと [`StartAction::RotateForRestart`] に落ちて**ローテートしてしまう**。
    /// → ⚠️ **中身がほぼ空のファイルが 1 本増える**（旧 code-review HIGH が防いでいた「孤児」）。
    ///
    /// ⚠️★★★ **`packaging::has_any_data_row` は孤児を止められない。**（★ 2026-08-19 に実測）
    /// 同関数が読み飛ばすのは `meta` / `hook_health` / `ime_state` **だけ**で、
    /// **`session_start` 行があるファイルは `true` を返す** → `.age` に包まれ**提出され、
    /// ブロック番号を 1 つ消費する**。
    /// ★ したがって「提出側で二重化されている」という従来の説明は**成り立たない**。
    ///
    /// ★ **本経路の解**: 何も書かずに `Ok` を返す。
    /// → ファイルは `session_start` **1 本**のまま保たれ（`protocol.md §1` を満たす）、
    /// フロントは `record_session_meta` を natural に再試行できる。
    RetryAfterMetaFailure,
}

impl StartAction {
    /// ローテート (＝ 前を閉じて新ファイルを開く) が要るか。
    pub fn rotates(self) -> bool {
        matches!(
            self,
            StartAction::RotateForNewBlock | StartAction::RotateForRestart
        )
    }

    /// `G1_BLOCKS_STARTED` を増やす経路か。
    ///
    /// ⚠️★ **`RotateForRestart` は増やさない。** 二度押しは「新しい最初のブロック」ではなく、
    /// ★ 数えると code-review HIGH が指摘した「孤児ファイルを 1 本増やす」形に戻る。
    pub fn counts_block(self) -> bool {
        matches!(
            self,
            StartAction::FirstBlock | StartAction::RotateForNewBlock
        )
    }

    /// `session_start` 行を積むか。
    ///
    /// ⚠️★★★ [`StartAction::RetryAfterMetaFailure`] だけが **false** である。
    /// ★ 積むと**同じファイルに 2 本目の `session_start`** が入り、
    /// `protocol.md §1` の破れを `validate_blocks.py` が FAIL として検出する状態になる。
    pub fn writes_session_start(self) -> bool {
        !matches!(self, StartAction::RetryAfterMetaFailure)
    }
}

/// 「開始する」押下時の扱いを決める**純関数**。
///
/// ## ⚠️★★★ なぜ要るか (P010 block07 で実発生した破れ)
///
/// 従来は `if g1_mode().is_some() && !was_active` でしかローテートしなかったため、
/// **セッション実行中に「開始する」が押されると、ローテートせずに `SessionStart` だけが積まれた**。
/// → ⚠️ **1 ファイルに 2 セッション**となり、`protocol.md §1`「1 ブロック = 1 ファイル」が破れる。
///
/// ★ 実測 (`notes.md:1750-1800`): 第 1 セッションは 3 分 17 秒**打鍵ゼロ**、`starved_ms` が
/// 165,312 ms まで伸びて `HookHealth::Down` → トレイが「⚠ 計測できていません」に変わり、
/// **参加者が見て押し直した**と読むのが最も素直である
/// (⚠️ **推論であって観測ではない**)。`268.5s + 300s = 568.5s` に対し実際の `session_end` が
/// `569.05s` ＝ **2 回目の押下でタイマーが引き直された**。
///
/// ## ⚠️★★★ `!was_active` を単純に外してはならない
///
/// その条件が置かれた理由は「`record_session_meta` 失敗時の文言は**明示的に再押下を促す**ので、
/// 無条件に**数える**と孤児ファイルが 1 本増える」(code-review HIGH) である。
/// → ★ [`StartAction::RotateForRestart`] は**数えない** (カウンタを触らない) ので、
/// この指摘とは別の解になっている。
///
/// ## ★ カウンタを増やさなくてもファイルは 1 本ずつ増える (検算)
///
/// | 押下 | `was_active` | `blocks_started` | → | ファイル |
/// |---|---|---|---|---|
/// | block1 開始 | false | 0 | `FirstBlock` | file1 (起動時のもの) |
/// | 二度押し | **true** | 1 | `RotateForRestart` | file2 |
/// | block2 開始 | false | 1 (>0) | `RotateForNewBlock` | file3 |
///
/// → ★ **衝突も孤児も出ない。**
pub fn decide_start_action(
    g1_mode: bool,
    was_active: bool,
    blocks_started: u64,
    meta_recorded: bool,
) -> StartAction {
    if !g1_mode {
        // ⚠️★ 通常運用 (Phase1) では「戻る → 開始する」でファイルが分かれると困る。
        //   ★ 既定の挙動を 1 バイトも変えない (研究者決定 #2: リブートの範囲は G1 の計器＋運用)。
        return StartAction::NotG1;
    }
    if was_active {
        // ⚠️★★★ **「二度押し」と「meta 再送」を分ける。**
        //   ★ `record_session_meta` がまだ成功していないなら、そのブロックは
        //     **まだ始まっていない** —— フロントが明示的に再押下を促した結果である。
        //   → ログを 1 行も書かない (孤児ファイルを作らない)。
        if !meta_recorded {
            return StartAction::RetryAfterMetaFailure;
        }
        return StartAction::RotateForRestart;
    }
    if blocks_started > 0 {
        StartAction::RotateForNewBlock
    } else {
        StartAction::FirstBlock
    }
}

// ---------------------------------------------------------------------------
// ブロックの自動終了 — D-1 (自動終了スレッド × 「開始する」押下の競合)
// ---------------------------------------------------------------------------

/// ブロック自動終了スレッドが、いま何をすべきか。
///
/// ★ 判定だけをここに置き、効果 (`session_active` の停止・`BlockEnd` の送信) は
/// `lib.rs` が適用する ([`decide_start_action`] と同じ流儀)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BlockEndAction {
    /// ブロックが始まっていない (`SESSION_START_MS == 0`)。★ 何もしない。
    NotStarted,
    /// まだ [`BLOCK_DURATION_MS`] に達していない。★ 回り続ける。
    KeepRunning,
    /// ★ 閉じてよい。
    EndBlock,
    /// ⚠️★★★ **観測した時点とは別のブロックになっている** → **中止する**。
    ///
    /// ★ 「開始する」が押されて新しいブロックが始まった (通常のブロック開始でも、
    /// 実行中の再押下 [`StartAction::RotateForRestart`] でも起きる)。
    /// ⚠️ ここで進むと **始まったばかりのブロックへ `session_end` を書く**。
    Superseded,
}

/// ブロックを自動終了してよいかを決める**純関数**。
///
/// ## ⚠️★★★ なぜ「観測した時点」と「いまの時点」を分けて渡すのか (D-1)
///
/// 自動終了スレッドは 500 ms ごとに `SESSION_START_MS` を読み、5 分を越えていたら
/// ブロックを閉じる。⚠️ **その判断と実際に閉じる操作の間には窓がある** ——
/// その窓で「開始する」が押されると、次の 2 通りに壊れる:
///
/// | 交錯 | ⚠️ 何が起きるか |
/// |---|---|
/// | **押下が後** | 自動終了が `session_active=false` にした後で押されるので `was_active == false` → [`StartAction::RotateForNewBlock`] → **`Rotate` が先に届く** → 直後の `BlockEnd` が**新しいファイルへ `session_end` を書く** (`logger.rs` の `Rotate` が `block_closed` を `false` に戻すため) |
/// | **押下が先** | 自動終了の `SESSION_START_MS.store(0)` が**始まったばかりのブロックの開始時刻を消す** → ★ 分析が止まり、`start == 0` で `continue` するので**自動終了も二度と来ない** |
///
/// ★ **pre-existing** だが、⚠️ G-1 修正で「実行中の押下」が**想定内の操作**になったぶん
/// 確率が上がった。⚠️★★★ **これはリブートの原因と同じ失敗クラス (ブロック境界の破れ) である。**
/// `preregistration.md §3.6` がブロックの事後除外を禁じているので、走り出したら**回復不能**。
///
/// → ★ **「押下が後」は排他 (`lib.rs` の `BLOCK_TRANSITION`) が順序を作って閉じる。**
/// → ★ **「押下が先」は本関数が [`BlockEndAction::Superseded`] として閉じる。**
///
/// ⚠️ **排他だけでは足りない**: 先に排他を取った自動終了が、
/// 既に交代済みのブロックを閉じてしまう。★ だから**照合**が要る。
/// ⚠️ **照合だけでも足りない**: `start_session` は `Rotate` を**ログのロックの中**で送り、
/// `SESSION_START_MS` を**ロックを抜けた後**で書くので、
/// ★ 「`Rotate` は送られたが `SESSION_START_MS` はまだ 0」という窓が実在する。
/// → ⚠️★★★ **排他と照合の両方が要る。**
///
/// ## 引数
///
/// - `observed_start_ms`: ★ ポーリング時に観測した `SESSION_START_MS`。
/// - `current_start_ms`: ⚠️★ **排他を取った後**に読み直した `SESSION_START_MS`。
///   ポーリング時点の判定では `observed_start_ms` と同じ値を渡す
///   (＝ そこでは交代を判定しない)。
/// - `now_ms`: いまの epoch ms。
/// - `limit_ms`: 1 ブロックの長さ ([`BLOCK_DURATION_MS`])。
///
/// ⚠️ ★ `now_ms < observed_start_ms` (時計の巻き戻し) は `saturating_sub` で 0 になり、
/// [`BlockEndAction::KeepRunning`] に倒れる。★ **勝手に閉じないほうが安全側**である
/// (閉じ損ねは次のポーリングで拾えるが、誤って閉じたブロックは `§3.6` により戻せない)。
pub fn decide_block_end(
    observed_start_ms: u64,
    current_start_ms: u64,
    now_ms: u64,
    limit_ms: u64,
) -> BlockEndAction {
    if observed_start_ms == 0 {
        return BlockEndAction::NotStarted;
    }
    // ⚠️★★★ **経過時間より先に照合する。** 逆にすると、交代後の (まだ 5 分に達していない)
    //   ブロックに対して `KeepRunning` を返してしまい、★ 呼び出し側が
    //   「まだ時間じゃないだけ」と読んで**同じブロックをもう一度閉じようとする**。
    if current_start_ms != observed_start_ms {
        return BlockEndAction::Superseded;
    }
    if now_ms.saturating_sub(observed_start_ms) < limit_ms {
        return BlockEndAction::KeepRunning;
    }
    BlockEndAction::EndBlock
}

#[cfg(test)]
mod tests {
    use super::*;

    /// ★ 未設定で G1 モードになってはならない (通常運用の非回帰)。
    #[test]
    fn env_unset_does_not_enable() {
        assert!(!g1_enabled_by_env(None));
        assert!(!g1_enabled_by_env(Some("")));
        assert!(!g1_enabled_by_env(Some("0")));
    }

    /// ⚠️ ★ 「立てたつもり」を生む綴りを通さない (probes_disabled_by_env と同じ厳しさ)。
    #[test]
    fn env_near_misses_do_not_enable() {
        assert!(!g1_enabled_by_env(Some("true")));
        assert!(!g1_enabled_by_env(Some("yes")));
        assert!(!g1_enabled_by_env(Some(" 1")));
        assert!(!g1_enabled_by_env(Some("1 ")));
        assert!(!g1_enabled_by_env(Some("11")));
    }

    #[test]
    fn env_exact_one_enables() {
        assert!(g1_enabled_by_env(Some("1")));
    }

    /// ★ macOS の形: `.app` の 4 階層上がフォルダ。
    #[test]
    fn marker_path_macos_shape() {
        let exe = Path::new("/Users/x/G1-app/gse-next.app/Contents/MacOS/gse-next");
        assert_eq!(
            marker_path_for(exe, 4).unwrap(),
            Path::new("/Users/x/G1-app/g1.mode")
        );
    }

    /// ★ Windows の形: `.exe` の 1 階層上がフォルダ。
    #[test]
    fn marker_path_windows_shape() {
        let exe = Path::new("/c/G1-app/gse-next.exe");
        assert_eq!(
            marker_path_for(exe, 1).unwrap(),
            Path::new("/c/G1-app/g1.mode")
        );
    }

    /// ⚠️ 階層が足りない (ルート直下等) なら None。落とさずマーカー無し扱いにする。
    #[test]
    fn marker_path_returns_none_when_too_shallow() {
        assert!(marker_path_for(Path::new("/gse-next"), 4).is_none());
    }

    /// ★ マーカーが env より優先される。
    #[test]
    fn marker_wins_over_env() {
        assert_eq!(decide(true, Some("1")), Some(G1Source::Marker));
        assert_eq!(decide(true, None), Some(G1Source::Marker));
    }

    #[test]
    fn env_used_when_no_marker() {
        assert_eq!(decide(false, Some("1")), Some(G1Source::Env));
    }

    /// ★ どちらも無ければ通常モード (既定の非回帰)。
    #[test]
    fn neither_means_normal_mode() {
        assert_eq!(decide(false, None), None);
        assert_eq!(decide(false, Some("0")), None);
    }

    /// ★ `meta` 行に書く文字列を固定する (解析側が読む値なので変えたら分析が壊れる)。
    #[test]
    fn source_strings_are_stable() {
        assert_eq!(G1Source::Marker.as_str(), "marker");
        assert_eq!(G1Source::Env.as_str(), "env");
    }

    /// ★ 自分の PID は「他のインスタンス」に数えない（さもないと常に警告が出る）。
    #[test]
    fn pgrep_excludes_self() {
        assert_eq!(other_pids_from_pgrep("4242\n", 4242), Vec::<u32>::new());
        assert_eq!(other_pids_from_pgrep("4242\n999\n", 4242), vec![999]);
        assert_eq!(other_pids_from_pgrep("", 4242), Vec::<u32>::new());
    }

    /// ⚠️ 数字でない行 (エラーメッセージ等) を PID と誤読しない。
    #[test]
    fn pgrep_ignores_non_numeric_lines() {
        assert_eq!(
            other_pids_from_pgrep("pgrep: illegal option\n", 4242),
            Vec::<u32>::new()
        );
    }

    /// ★★ **Windows 実機の生出力**（2026-08-06 採取・`windows-measurements.md` M-2）。
    /// `tasklist /FI "IMAGENAME eq gse-next.exe" /FO CSV /NH` の 1 行をそのまま入力にしてある。
    /// ★ この行を書き換えるときは**実機で採り直す**こと（想像で直さない）。
    #[test]
    fn tasklist_csv_extracts_pid_column() {
        let out = "\"gse-next.exe\",\"17456\",\"Console\",\"3\",\"47,644 K\"\r\n";
        assert_eq!(other_pids_from_tasklist(out, 999), vec![17456]);
        // ★ 自分自身は「他のインスタンス」に数えない（さもないと常に警告が出る）。
        assert_eq!(other_pids_from_tasklist(out, 17456), Vec::<u32>::new());
    }

    /// ★ 区切りが **`","`(引用符込み) であること**を固定する。
    ///
    /// ⚠️ ★ **わざと壊して分かったこと**: 区切りを素の `,` に変えても、実機で採れた行
    /// （`"explorer.exe","2084","Console","3","386,368 K"`）では **2 列目が変わらない**ので
    /// テストが赤にならない。★ メモリ列のカンマは**最終列**にしか出ず、PID 列より後ろだからである。
    /// → ★ **「実測行を置いただけでは区切りの選択を守れない」**。そこで、素のカンマ分割だと
    /// 2 列目がずれる行（**イメージ名にカンマを含む**形）を構成して赤を出せるようにする。
    /// ★ この行は **実測ではない**（Windows のファイル名にカンマは使えるが、実機では見ていない）。
    #[test]
    fn tasklist_splits_on_quoted_comma_not_bare_comma() {
        // ★ 素の `,` で割ると cols[1] = `app.exe"` になり数値化に失敗 → PID を取りこぼす。
        let out = "\"my,app.exe\",\"2084\",\"Console\",\"3\",\"386,368 K\"\r\n";
        assert_eq!(
            other_pids_from_tasklist(out, 999),
            vec![2084],
            "区切りは `\",\"` である必要がある（素の `,` だと 2 列目がずれる）"
        );
        // 実測行（M-2）でも同じ結果になること。
        let real = "\"explorer.exe\",\"2084\",\"Console\",\"3\",\"386,368 K\"\r\n";
        assert_eq!(other_pids_from_tasklist(real, 999), vec![2084]);
    }

    /// ★★ **Windows 実機の生出力**（2026-08-06 採取・`windows-measurements.md` M-1）。
    ///
    /// ⚠️ ★ 実測で分かった重要な点: **`ja-JP` 環境でも文言は英語**で、**`rc=0`** かつ
    /// **stdout** に出た。`/FO CSV` を付けても CSV 化されない。
    /// ★ ただし **1 台の実測**にすぎないので、「日本語 Windows なら常に英語」とは書かない。
    /// → 下の `tasklist_non_csv_lines_are_dropped_whatever_the_language` が本命の防御である。
    #[test]
    fn tasklist_ignores_no_task_message() {
        let out = "INFO: No tasks are running which match the specified criteria.\r\n";
        assert_eq!(other_pids_from_tasklist(out, 999), Vec::<u32>::new());
    }

    /// ★★ **文言が何語でも安全側（= 検出なし）に倒れる**ことを固定する。
    ///
    /// ⚠️★★ **日本語文言は「起こりうる」ではなく実際に起きた**（`windows-measurements.md` **M-9**）。
    /// **同じ 1 台**で、`cmd.exe` 直叩きだと**英語**、PowerShell 経由 (`& cmd.exe /c …`) だと
    /// **日本語**が返った。★ 条件の違いは特定できていない。
    /// → ⚠️ ★ **文言をテストで列挙する方針だったら破綻していた。**
    /// 本関数は「`","` で 2 列以上に割れ、2 列目が数値」の行しか拾わないので、
    /// ★ **文言ではなくその性質をテストで固定する。**
    #[test]
    fn tasklist_non_csv_lines_are_dropped_whatever_the_language() {
        // ★ 実測された日本語文言 (M-9)。
        let ja = "情報: 指定された条件に一致するタスクは実行されていません。\r\n";
        assert_eq!(other_pids_from_tasklist(ja, 999), Vec::<u32>::new());
        // 数字を含む非 CSV 行も PID と誤読しない。
        let noisy = "エラー: 無効な引数またはオプションです - '/FO CSV 1234'\r\n";
        assert_eq!(other_pids_from_tasklist(noisy, 999), Vec::<u32>::new());
        assert_eq!(other_pids_from_tasklist("", 999), Vec::<u32>::new());
    }

    /// ★★ **2 プロセス同時のときの Windows 実機の生出力**
    /// （2026-08-06 採取・`windows-measurements.md` **M-8**）。
    ///
    /// ⚠️ ★ この 2 行は **代用プロセス**（`gse-next.exe` という名前で眠るだけの別プロセス）を
    /// 使って作った。★ **同名 exe の二重起動では原理的に 2 行にならない**ためである
    /// (`tauri-plugin-single-instance` が 2 個目を 14 ms で終了させ、`tasklist` 1 回 ≒57 ms より短い)。
    /// ★ 代用は「ごまかし」ではなく、⚠️ `decisions.md` R-8 の
    /// **「プラグインを持たない旧ビルドと共存する」**という**本命の脅威モデルの再現**である。
    #[test]
    fn tasklist_two_rows_yield_the_other_pid_only() {
        let out = "\"gse-next.exe\",\"13864\",\"Console\",\"4\",\"4,212 K\"\r\n\
                   \"gse-next.exe\",\"13696\",\"Console\",\"4\",\"37,164 K\"\r\n";
        // ★ 実機ではこの状態で「2 つ動いている」警告に到達した (M-8)。
        assert_eq!(other_pids_from_tasklist(out, 13696), vec![13864]);
        assert_eq!(other_pids_from_tasklist(out, 13864), vec![13696]);
        assert_eq!(other_pids_from_tasklist(out, 999), vec![13864, 13696]);
    }

    /// ★ ブロック長は `preregistration.md §2.3` の 5 分と `writing-pad.html` の
    /// `BLOCK_MS` に一致していなければならない。⚠️ 片方だけ変えると、ページが
    /// 打鍵を止める時刻とログを閉じる時刻がずれる。
    #[test]
    fn block_duration_is_five_minutes() {
        assert_eq!(BLOCK_DURATION_MS, 300_000);
    }

    // -----------------------------------------------------------------------
    // G-1: 「開始する」押下時の扱い (2026-08-19)
    // -----------------------------------------------------------------------

    /// ⚠️★★★ **通常運用 (G1 でない) の挙動を 1 バイトも変えない。**
    ///
    /// ★ `was_active` にも `blocks_started` にも一切依存せず、常に `NotG1` であること。
    /// ⚠️ ここが崩れると Phase1 の「戻る → 開始する」でファイルが分かれ、
    /// **前半が提出されなくなる**。
    #[test]
    fn normal_mode_never_rotates_or_counts() {
        for was_active in [false, true] {
            for blocks in [0u64, 1, 9] {
                let a = decide_start_action(false, was_active, blocks, true);
                assert_eq!(
                    a,
                    StartAction::NotG1,
                    "was_active={was_active} blocks={blocks}"
                );
                assert!(!a.rotates());
                assert!(!a.counts_block());
            }
        }
    }

    /// ★ G1 の 1 ブロック目は**ローテートしない**が**数える** (起動時のファイルを使う)。
    #[test]
    fn g1_first_block_counts_without_rotating() {
        let a = decide_start_action(true, false, 0, true);
        assert_eq!(a, StartAction::FirstBlock);
        assert!(!a.rotates());
        assert!(a.counts_block());
    }

    /// ★ G1 の 2 ブロック目以降はローテートして数える (従来どおり)。
    #[test]
    fn g1_later_blocks_rotate_and_count() {
        for blocks in [1u64, 2, 9] {
            let a = decide_start_action(true, false, blocks, true);
            assert_eq!(a, StartAction::RotateForNewBlock, "blocks={blocks}");
            assert!(a.rotates());
            assert!(a.counts_block());
        }
    }

    /// ⚠️★★★ **G-1 の本命**: セッション実行中の再押下は
    /// **ローテートするが数えない**。
    ///
    /// ★ 数えないことが重要である —— 数えると code-review HIGH が指摘した
    /// 「`record_session_meta` 失敗後の再押下で孤児ファイルが 1 本増える」形に戻る。
    #[test]
    fn g1_restart_while_active_rotates_without_counting() {
        for blocks in [0u64, 1, 9] {
            let a = decide_start_action(true, true, blocks, true);
            assert_eq!(a, StartAction::RotateForRestart, "blocks={blocks}");
            assert!(
                a.rotates(),
                "★ ここが false だと 1 ファイルに 2 セッションが入る (P010 block07)"
            );
            assert!(!a.counts_block());
        }
    }

    /// ⚠️★★★ **`record_session_meta` 失敗後の再押下では、ログを 1 行も書かない**
    /// (code-reviewer HIGH・2026-08-19)。
    ///
    /// ★ フロントは失敗時に `isStarted` へ進まず**再押下を促す**が、backend の
    /// `session_active` は既に true なので、素朴に書くと `RotateForRestart` に落ちて
    /// ⚠️ **中身がほぼ空の孤児ファイルが 1 本増える**。
    /// ⚠️ **`packaging::has_any_data_row` はこれを止められない**
    /// (`session_start` 行があるファイルは通る・2026-08-19 実測)。
    #[test]
    fn retry_after_meta_failure_writes_nothing() {
        for blocks in [0u64, 1, 9] {
            let a = decide_start_action(true, true, blocks, false);
            assert_eq!(a, StartAction::RetryAfterMetaFailure, "blocks={blocks}");
            assert!(!a.rotates(), "★ ローテートすると孤児ファイルが 1 本増える");
            assert!(!a.counts_block());
            assert!(
                !a.writes_session_start(),
                "★ 積むと同じファイルに 2 本目の session_start が入る"
            );
        }
    }

    /// ★ 対照: **握手が済んでいれば**同じ `was_active == true` でも本物の二度押しである。
    #[test]
    fn restart_is_distinguished_from_meta_retry_by_the_handshake() {
        assert_eq!(
            decide_start_action(true, true, 1, true),
            StartAction::RotateForRestart
        );
        assert_eq!(
            decide_start_action(true, true, 1, false),
            StartAction::RetryAfterMetaFailure
        );
    }

    /// ★ 新規ブロックの経路は握手の有無に**依存しない** (⚠️ was_active=false なら常に新規)。
    #[test]
    fn new_block_paths_do_not_depend_on_the_handshake() {
        for meta in [true, false] {
            assert_eq!(
                decide_start_action(true, false, 0, meta),
                StartAction::FirstBlock
            );
            assert_eq!(
                decide_start_action(true, false, 3, meta),
                StartAction::RotateForNewBlock
            );
            assert_eq!(
                decide_start_action(false, true, 3, meta),
                StartAction::NotG1
            );
        }
    }

    /// ★ `decide_start_action` の検算表 (doc コメント) をそのまま実行する。
    ///
    /// ⚠️ 「カウンタを増やさなくてもファイルが 1 本ずつ増える」ことを、
    /// **押下の並び**に対して確かめる (ここが崩れると衝突か孤児が出る)。
    #[test]
    fn g1_press_sequence_yields_one_file_per_press() {
        let mut blocks: u64 = 0;
        let mut files: u64 = 1; // ★ 起動時に 1 本開いている。

        // ① block1 開始 (was_active=false)
        let a = decide_start_action(true, false, blocks, true);
        assert_eq!(a, StartAction::FirstBlock);
        if a.counts_block() {
            blocks += 1;
        }
        if a.rotates() {
            files += 1;
        }
        assert_eq!((blocks, files), (1, 1));

        // ② 二度押し (was_active=true)
        let a = decide_start_action(true, true, blocks, true);
        assert_eq!(a, StartAction::RotateForRestart);
        if a.counts_block() {
            blocks += 1;
        }
        if a.rotates() {
            files += 1;
        }
        assert_eq!((blocks, files), (1, 2), "★ 数えずにファイルだけ増える");

        // ③ block2 開始 (停止後なので was_active=false)
        let a = decide_start_action(true, false, blocks, true);
        assert_eq!(a, StartAction::RotateForNewBlock);
        if a.counts_block() {
            blocks += 1;
        }
        if a.rotates() {
            files += 1;
        }
        assert_eq!((blocks, files), (2, 3), "★ 衝突も孤児も出ない");
    }

    // -----------------------------------------------------------------------
    // ブロックの自動終了 (D-1) — ⚠️★★★ 交錯の 2 方向をそれぞれ固定する
    // -----------------------------------------------------------------------

    /// 5 分ぴったりの開始時刻。★ 値そのものに意味は無い (非ゼロであることだけ)。
    const T1: u64 = 1_700_000_000_000;
    /// ★ 交代後のブロックの開始時刻 (T1 とは別の値)。
    const T2: u64 = 1_700_000_268_500;

    /// ⚠️★★★ **交錯 ①「押下が先」**: 観測してから排他を取るまでに新しいブロックが始まった
    /// → **中止する** (`Superseded`)。
    ///
    /// ★ ここで進むと `SESSION_START_MS.store(0)` が**始まったばかりのブロックを殺し**、
    /// ⚠️ `start == 0` で `continue` するので**自動終了も二度と来ない**。
    #[test]
    fn block_end_is_aborted_when_a_new_block_started() {
        // 通常のブロック開始で交代した (前が閉じてから押された)。
        assert_eq!(
            decide_block_end(T1, T2, T1 + BLOCK_DURATION_MS, BLOCK_DURATION_MS),
            BlockEndAction::Superseded,
        );
        // ⚠️★ 実行中の再押下 (`RotateForRestart`) でも交代する。
        //   ★ この経路は `session_active` を true のまま維持するので、
        //   `session_active` を見ていると気づけない (Codex HIGH・2026-08-19 と同じ罠)。
        assert_eq!(
            decide_block_end(T1, T2, T1 + BLOCK_DURATION_MS * 3, BLOCK_DURATION_MS),
            BlockEndAction::Superseded,
        );
        // ⚠️★★★ **経過時間より照合が先**であること。交代後のブロックがまだ 5 分に
        //   達していなくても `KeepRunning` ではなく `Superseded` を返す
        //   (★ `KeepRunning` だと呼び出し側が「まだ時間じゃないだけ」と読んで再挑戦する)。
        assert_eq!(
            decide_block_end(T1, T2, T2 + 1_000, BLOCK_DURATION_MS),
            BlockEndAction::Superseded,
            "★ 交代の判定は経過時間より先"
        );
    }

    /// ⚠️★★★ **交錯 ②「押下が後」**: 排他を取った時点で**まだ同じブロック**なら
    /// **閉じてよい** (`EndBlock`)。
    ///
    /// ★ この後に押される分は `lib.rs` の `BLOCK_TRANSITION` が待たせるので、
    /// `Rotate` は必ず `BlockEnd` の**後ろ**に回る。
    /// ⚠️ 純関数はここまでしか言えない —— **順序を作るのは排他の仕事**である。
    #[test]
    fn block_end_proceeds_for_the_same_block() {
        assert_eq!(
            decide_block_end(T1, T1, T1 + BLOCK_DURATION_MS, BLOCK_DURATION_MS),
            BlockEndAction::EndBlock,
            "★ 5 分ちょうどで閉じる (>= 境界)"
        );
        assert_eq!(
            decide_block_end(T1, T1, T1 + BLOCK_DURATION_MS * 2, BLOCK_DURATION_MS),
            BlockEndAction::EndBlock,
        );
    }

    /// まだ 5 分に達していないブロックは閉じない。
    #[test]
    fn block_end_waits_until_the_limit() {
        assert_eq!(
            decide_block_end(T1, T1, T1 + BLOCK_DURATION_MS - 1, BLOCK_DURATION_MS),
            BlockEndAction::KeepRunning,
            "★ 1 ms 手前ではまだ閉じない"
        );
        assert_eq!(
            decide_block_end(T1, T1, T1, BLOCK_DURATION_MS),
            BlockEndAction::KeepRunning,
        );
    }

    /// ブロックが始まっていなければ何もしない。
    #[test]
    fn block_end_ignores_an_unstarted_block() {
        assert_eq!(
            decide_block_end(0, 0, T1, BLOCK_DURATION_MS),
            BlockEndAction::NotStarted,
        );
        // ⚠️ 観測が 0 なら、いま非ゼロでも「未開始」として扱う
        //   (★ そのブロックは次のポーリングが観測する)。
        assert_eq!(
            decide_block_end(0, T2, T1, BLOCK_DURATION_MS),
            BlockEndAction::NotStarted,
        );
    }

    /// ⚠️★ **時計が巻き戻っても勝手に閉じない** (安全側)。
    ///
    /// ★ 閉じ損ねは次のポーリングで拾えるが、⚠️ 誤って閉じたブロックは
    /// `preregistration.md §3.6` (事後除外の禁止) により**戻せない**。
    #[test]
    fn block_end_does_not_fire_when_the_clock_goes_backwards() {
        assert_eq!(
            decide_block_end(T1, T1, T1 - 60_000, BLOCK_DURATION_MS),
            BlockEndAction::KeepRunning,
        );
    }

    /// ★ ポーリング時点の呼び出し (`observed == current`) では `Superseded` になりえない。
    /// ⚠️ ここが崩れると、排他の外で中止判定が起き**ブロックが閉じなくなる**。
    #[test]
    fn polling_call_never_reports_superseded() {
        for now in [0u64, T1, T1 + BLOCK_DURATION_MS, u64::MAX] {
            let a = decide_block_end(T1, T1, now, BLOCK_DURATION_MS);
            assert_ne!(a, BlockEndAction::Superseded, "now={now}");
        }
    }

    /// ⚠️★★★ **配線の不変条件を固定する** (D-1)。
    ///
    /// [`decide_block_end`] は「押下が**先**」の交錯しか閉じられない。
    /// ★ 「押下が**後**」を閉じるのは `lib.rs` の `BLOCK_TRANSITION` が作る**順序**であり、
    /// それは純関数テストでは表現できない。→ ⚠️ **ソース走査で位置関係を固定する。**
    ///
    /// 固定する不変条件は 2 つ:
    ///
    /// 1. `start_session` が、`Rotate` を送る**前**に排他を取り、
    ///    `SESSION_START_MS.store(now)` の**後**に離す
    ///    (★ 「`Rotate` は送られたが `SESSION_START_MS` はまだ 0」の窓を消すため)
    /// 2. 自動終了スレッドが、`BlockEnd` を送る**前**に排他を取り、**後**に離す
    ///
    /// ⚠️★ **本テストは回帰検知であって設計保証ではない** (Codex 指摘 3・2026-08-21)。
    /// ★ 位置関係しか見ていないので、「同じ guard が本当に保持されている」ことは証明しないし、
    /// ⚠️ ヘルパ関数化やログ文の変更で**壊れる**。
    /// → ★ 壊れたときは「テストが古い」と断じる前に、
    ///   **上の 2 つの不変条件がまだ成り立っているか**を目で確かめること。
    ///
    /// ⚠️ ★ **バイト数でスライスしない** —— 日本語コメントで文字境界 panic する
    /// (`.steering/20260819-g1-reboot-and-instrument-fix/blockers.md` B-4 で実際に踏んだ)。
    /// → `match_indices` が返す位置を**比較するだけ**にする。
    #[test]
    fn block_transition_is_held_across_the_whole_block_boundary() {
        const SRC: &str = include_str!("lib.rs");
        let pos =
            |needle: &str| -> Vec<usize> { SRC.match_indices(needle).map(|(i, _)| i).collect() };

        // ⚠️★ **呼び出し回数で数える** (code-reviewer LOW・2026-08-21)。
        //   ★ binding 名 (`let block_transition = ...`) で数えると、
        //   `let _g = lock_block_transition();` のような別名追加が**素通りする**。
        let acquire = pos("lock_block_transition();");
        let release = pos("drop(block_transition);");
        assert_eq!(
            acquire.len(),
            2,
            "★ 排他を取るのは start_session と自動終了スレッドの 2 箇所だけ"
        );
        assert_eq!(release.len(), 2, "★ 明示的に離すのも 2 箇所");

        // ⚠️★★★ **照合も固定する** (code-reviewer MEDIUM・2026-08-21)。
        //   ★ 変異テストで実測: ロック配置を壊す 5 変異はすべて赤になったが、
        //     **再照合を潰す変異は緑のまま**だった。
        //   → 設計は「排他と照合の**両方**が要る」と言っているのに、
        //     ⚠️ 固定されていたのは排他だけだった。
        let recheck = pos("let current_start_ms = SESSION_START_MS.load(Ordering::Acquire);");
        let start_ms = pos("SESSION_START_MS.store(now, Ordering::Release);");
        let block_end = pos("block_log_tx.try_send(LogEntry::BlockEnd)");
        assert_eq!(start_ms.len(), 1);
        assert_eq!(block_end.len(), 1);

        // ⚠️★★★ **`Rotate` の送信点は 2 つある** (2026-08-27 に O1 が増えた)。
        //   ① `start_session` …… G1 のブロック境界 (★ 本テストが守っている当のもの)
        //   ② `o1_rotate` ……… O1 の宣言変更 / 日次ローテート
        //       ★ O1 は `start_session` を通らず、`g1_mode` とは**排他**である
        //       (`o1::resolve` が G1 を勝たせる) ので、⚠️ ブロック境界とは競合しない。
        //   → ★ 「1 個しか無い」ではなく「**排他区間の中に 1 個ある**」で固定する
        //     (⚠️ こちらのほうが強い: 位置関係そのものを見ている)。
        let rotate = pos("LogEntry::Rotate { new_path }");
        assert!(
            !rotate.is_empty(),
            "★ start_session の Rotate 送信が見つからない"
        );
        let rotate_in_block: Vec<usize> = rotate
            .iter()
            .copied()
            .filter(|p| *p > acquire[0] && *p < release[0])
            .collect();
        assert_eq!(
            rotate_in_block.len(),
            1,
            "⚠️ start_session の排他区間 (取る → 離す) の中にある Rotate が 1 個ではない \
             (★ 区間の外に出ると Rotate と SESSION_START_MS の間に窓が残る)"
        );
        let rotate0 = rotate_in_block[0];

        // ① start_session: 取る → Rotate → SESSION_START_MS → 離す
        assert!(
            acquire[0] < rotate0,
            "⚠️ start_session が Rotate を送った後で排他を取っている              (★ Rotate と SESSION_START_MS の間に窓が残る)"
        );
        assert!(
            start_ms[0] < release[0],
            "⚠️ SESSION_START_MS.store(now) の前に排他を離している              (★ 自動終了が「まだ 0」を見て新しいファイルへ session_end を書く)"
        );
        assert!(rotate0 < start_ms[0], "★ 送信は SESSION_START_MS より前");

        // ② 自動終了スレッド: 取る → BlockEnd → 離す
        assert!(
            acquire[1] < block_end[0],
            "⚠️ BlockEnd を送った後で排他を取っている (★ 順序を作れていない)"
        );
        assert!(
            block_end[0] < release[1],
            "⚠️ BlockEnd を送る前に排他を離している              (★ その隙に Rotate が割り込むと session_end が新しいファイルへ行く)"
        );

        // ③ ⚠️★★★ 照合は**排他の中**で、かつ `BlockEnd` より**前**に行う。
        assert_eq!(
            recheck.len(),
            1,
            "★ 排他を取った後の再照合が見つからない (「押下が先」の交錯が閉じない)"
        );
        assert!(
            acquire[1] < recheck[0] && recheck[0] < block_end[0],
            "⚠️★★★ 再照合が排他の外にあるか、BlockEnd より後にある。             ★ 排他だけでは『先に排他を取った自動終了が、既に交代済みのブロックを閉じる』             を防げない —— 照合が要る"
        );

        // ④ ⚠️ 2 箇所が入れ子になっていないこと (★ start_session が先・自動終了が後)。
        assert!(
            release[0] < acquire[1],
            "⚠️ 2 つの臨界区間がソース上で入れ子に見える。★ 位置関係の前提が崩れた"
        );
    }
}
