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
}
