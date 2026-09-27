//! ⚠️★★★ **O1 自動起動**（G-1・2026-09-28・`.steering/20260928-o1-resilience-g1-g2-g5/`）。
//!
//! ★ O1 は「ふだんの作業のあいだ、ずっと動いている」ことで成り立つ。⚠️ 再起動のあとアプリを
//! 開き忘れると、**その日から何も記録されない**（受領台帳の「5 日途絶」で後から気づくだけだった）。
//! → ★ O1 の配布形で**初めて起動したときに 1 回だけ**、OS のログイン時起動に登録する。
//!
//! ## ★ 決めたこと（decisions.md 判断 1 / 2 / 9）
//! - ⚠️ **新しく作るのは 1 回だけ**。ホーム側（`~/.gse/`）に「一度登録した」記録
//!   [`HOME_RECORD_FILE_NAME`] を残し、以後は**新しく作らない**。★ 被験者が OS の設定で切ったり
//!   登録を消したりしたら**上書きしない**（やめる権利）。
//! - ★ 新しい版のフォルダを配り直したときは、**OS に登録が残っているときだけ**新しい exe へ
//!   **付け替える**（古いフォルダの exe を指したまま死なないように）。⚠️ 消されていたら作り直さない
//!   （security-checker MEDIUM-1・2026-09-28）。
//! - ★ 配布フォルダ（`o1.mode` の隣）の印 [`MARKER_FILE_NAME`] は「このフォルダでは処理済み」の印で、
//!   **中身は登録した exe のパス**（フォルダを移動・コピーしたら一致しなくなり、付け替えが起きる）。
//! - ★ 印と記録は **OS への登録が成功してから**書く（途中で落ちたら次の起動で再試行する）。
//! - ⚠️ Windows の自動起動は `GSE_起動.bat` を通らないので、`.bat` が付ける `GSE_DISABLE_PROBES=1`
//!   （多重防御）は**乗らない**。★ O1 でプローブが出ないのは `start_session` を拒む構造のガード
//!   （`lib.rs` の `start_session` 冒頭）によるもので、自動起動でも同じく効く（cross-review・2026-09-28）。
//! - ⚠️ **配布形（目印ファイル由来）の O1 だけ**。環境変数 `GSE_O1_MODE=1`（開発・検証）では登録しない
//!   —— さもないと**開発用バイナリがログイン項目に入る**。G1 / 通常運用でも登録しない。
//! - ★ `tauri-plugin-autostart` は使わない（tauri の版上げ・Windows の引用符なしパス・
//!   `StartupApproved` の書き戻し・未エスケープの plist。一次の根拠は design.md の表）。
//!
//! ## 登録の中身
//! - **macOS**: `~/Library/LaunchAgents/<LAUNCH_AGENT_LABEL>.plist`（`RunAtLoad`）。
//!   ★ 2026-09-28 の実機実験で、launchd から起動しても入力監視（TCC）が効き、
//!   `o1.mode` が見つかることを確かめた（`g1-mac-autostart-experiment.md`）。
//! - **Windows**: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` の値 [`RUN_VALUE_NAME`]
//!   に **引用符つき**の exe パス。⚠️ `StartupApproved` には**触らない**（タスクマネージャーでの
//!   無効化を尊重する）。
//!
//! ⚠️ ここは OS API を呼ぶので `analysis/` には置かない（`architecture-rules`）。
//! ★ 判定と文字列の組み立ては純関数にして、両 OS でテストする。

use std::path::{Path, PathBuf};

use crate::o1::O1Source;

/// ★ 「このフォルダでは処理済み」の印のファイル名（配布フォルダ・`o1.mode` の隣）。
pub const MARKER_FILE_NAME: &str = "o1.autostart";

/// ★ 「この利用者の端末で一度登録した」記録のファイル名（`~/.gse/`・同意の記録と同じ場所）。
pub const HOME_RECORD_FILE_NAME: &str = "o1_autostart_registered";

/// macOS の LaunchAgent の Label（= plist のファイル名）。
pub const LAUNCH_AGENT_LABEL: &str = "com.johnd.gse-next.o1";

/// Windows の Run キーの値の名前。
pub const RUN_VALUE_NAME: &str = "GSE-O1";

/// 自動起動をどうするか。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AutostartAction {
    /// ログイン時起動を新しく作る（この端末で初めて）。
    Register,
    /// ★ 既に OS に残っている登録を、いまの exe へ付け替える（新しい版のフォルダ）。
    Repoint,
    /// 何もしない。
    Skip,
}

/// 判定に使う端末の状態（IO は呼び出し側が行う）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct AutostartState {
    /// このフォルダの印 [`MARKER_FILE_NAME`] がある。
    pub folder_marker: bool,
    /// ホーム側の記録 [`HOME_RECORD_FILE_NAME`] がある（= この端末で一度登録した）。
    pub ever_registered: bool,
    /// OS に登録が残っている（macOS: plist がある／Windows: Run の値がある）。
    pub entry_exists: bool,
}

/// ⚠️★★★ 対象になるか（純関数）: **目印ファイル由来の O1** かつ **G1 でない** かつ **O1 の同意確認済み**。
///
/// ⚠️ 同意確認（`submission::o1_consent_acknowledged`・R-7）を条件に入れるのは、
/// **同意の画面を押さずに閉じた人の端末で、ログインのたびに起動させない**ため
/// （code-reviewer HIGH・2026-09-28）。★ 同意した直後にも呼ぶので、初回に同意した人も取りこぼさない。
/// ⚠️ G1 は `o1::resolve` が既に O1 を落としているが、ここでも見る（二重の防御）。
pub fn eligible(o1: Option<O1Source>, g1_active: bool, consent_acknowledged: bool) -> bool {
    o1 == Some(O1Source::Marker) && !g1_active && consent_acknowledged
}

/// ⚠️★★★ どうするか（純関数）。
///
/// | 対象 | フォルダの印 | 一度登録した | OS に登録 | → |
/// |---|---|---|---|---|
/// | ✗ | * | * | * | Skip |
/// | ✓ | あり | * | * | Skip（このフォルダでは処理済み） |
/// | ✓ | なし | なし | * | **Register** |
/// | ✓ | なし | あり | あり | **Repoint**（新しいフォルダ・被験者は消していない） |
/// | ✓ | なし | あり | なし | Skip（⚠️ **被験者が消した**ので作り直さない） |
pub fn decide(eligible: bool, st: AutostartState) -> AutostartAction {
    if !eligible || st.folder_marker {
        AutostartAction::Skip
    } else if !st.ever_registered {
        AutostartAction::Register
    } else if st.entry_exists {
        AutostartAction::Repoint
    } else {
        AutostartAction::Skip
    }
}

/// 登録してよいパスか（純関数）。⚠️ 制御文字を含むパスは拒む。
///
/// ★ XML 1.0 は大半の制御文字を許さないので、plist が壊れて**黙って起動しなくなる**
/// （security-checker MEDIUM・2026-09-28）。Windows の Run 値でも意味が無い。
pub fn path_is_registrable(exe: &str) -> bool {
    !exe.is_empty() && !exe.chars().any(char::is_control)
}

/// `exe` に対応する印ファイルのパス（純関数）。★ 階層は `o1.mode` と同じ関数で決める。
pub fn marker_path_for(exe: &Path, levels_up: usize) -> Option<PathBuf> {
    Some(crate::g1::folder_up(exe, levels_up)?.join(MARKER_FILE_NAME))
}

/// XML の文字データとして安全な形にする（純関数）。
fn xml_escape(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for c in s.chars() {
        match c {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            '\'' => out.push_str("&apos;"),
            _ => out.push(c),
        }
    }
    out
}

/// macOS の LaunchAgent plist の本文（純関数）。
///
/// ★ キーはプラグイン（`auto-launch` 0.5）と同じ 3 つだけ（`Label` / `ProgramArguments` / `RunAtLoad`）。
/// ⚠️ `KeepAlive` は付けない —— 被験者がアプリを終了したら**終了したまま**にする（やめる権利）。
/// ⚠️ パスは XML エスケープする（`&` を含むフォルダで壊れた plist にしない）。
pub fn launch_agent_plist(exe: &str) -> String {
    format!(
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\
         <!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n\
         <plist version=\"1.0\">\n\
         <dict>\n\
         \t<key>Label</key>\n\
         \t<string>{label}</string>\n\
         \t<key>ProgramArguments</key>\n\
         \t<array>\n\
         \t\t<string>{exe}</string>\n\
         \t</array>\n\
         \t<key>RunAtLoad</key>\n\
         \t<true/>\n\
         </dict>\n\
         </plist>\n",
        label = LAUNCH_AGENT_LABEL,
        exe = xml_escape(exe),
    )
}

/// Windows の Run キーに書く値（純関数）。
///
/// ⚠️★ **引用符で囲む。** 囲まないと、ユーザー名やフォルダ名にスペースがあるとき
/// `C:\Users\Taro Yamada\...` が `C:\Users\Taro` と引数に割れる（引用符なしパスの問題）。
pub fn run_value(exe: &str) -> String {
    format!("\"{exe}\"")
}

/// ★ 起動時と、O1 の同意確認を記録した直後に呼ぶ（IO あり）。
///
/// ⚠️ 失敗しても起動は止めない（ログに残す）。
/// ⚠️ ログにパスを出さない（ホームのパスにはユーザー名＝実名が入りうる・security-checker MEDIUM）。
pub fn register_if_needed(o1: Option<O1Source>, g1_active: bool, consent_acknowledged: bool) {
    // ⚠️ 対象でなければ exe も印も見ない（通常運用で IO を増やさない）。
    if !eligible(o1, g1_active, consent_acknowledged) {
        return;
    }
    let exe = match std::env::current_exe() {
        Ok(p) => p,
        Err(e) => {
            tracing::warn!("O1 autostart: cannot resolve the executable path: {e}");
            return;
        }
    };
    let Some(marker) = marker_path_for(&exe, crate::g1::exe_to_folder_levels()) else {
        tracing::warn!("O1 autostart: cannot resolve the distribution folder");
        return;
    };
    let Some(record) =
        crate::submission::home_dir().map(|h| h.join(".gse").join(HOME_RECORD_FILE_NAME))
    else {
        // ⚠️ 記録を残せないと「消した人に作り直さない」を守れない → 登録しない。
        tracing::warn!("O1 autostart: cannot resolve the home folder; NOT registering");
        return;
    };
    handle(&exe, &marker, &record, &OsRegistrar);
}

/// OS のログイン時起動への登録（テストで差し替えるための境目）。
pub trait Registrar {
    /// OS に登録が残っているか。
    fn entry_exists(&self) -> bool;
    /// `exe` を登録する（既にあれば上書き）。戻り値はログ用の場所の説明（⚠️ パスを含めない）。
    fn register(&self, exe: &Path) -> Result<String, String>;
}

/// 本物の OS に登録する。
struct OsRegistrar;

impl Registrar for OsRegistrar {
    fn entry_exists(&self) -> bool {
        platform::entry_exists()
    }
    fn register(&self, exe: &Path) -> Result<String, String> {
        platform::register(exe)
    }
}

/// ★ 判定して登録し、印と記録を書く（IO あり・OS への登録は `reg` に任せる）。戻り値はとった行動。
pub fn handle(exe: &Path, marker: &Path, record: &Path, reg: &dyn Registrar) -> AutostartAction {
    let here = exe.to_string_lossy().into_owned();
    // ★ 印の中身は「このフォルダで登録した exe のパス」。⚠️ フォルダを移動・コピーすると印も一緒に
    //   移るので、**いまの exe と一致するときだけ**処理済みとみなす（Codex P2・2026-09-28）。
    let folder_marker = marker_matches(std::fs::read_to_string(marker).ok().as_deref(), &here);
    if folder_marker {
        tracing::info!("O1 autostart: already handled for this folder (marker present)");
        return AutostartAction::Skip;
    }
    let st = AutostartState {
        folder_marker,
        ever_registered: record.is_file(),
        entry_exists: reg.entry_exists(),
    };
    let action = decide(true, st);
    if action == AutostartAction::Skip {
        // ★ 一度登録したのに OS に無い = 被験者が消した。⚠️ 作り直さない。印だけ置いて次から見ない。
        tracing::info!(
            "O1 autostart: the login entry was removed after registration; \
             respecting it (NOT re-creating)"
        );
        write_or_log(marker, &here, MARKER_FILE_NAME);
        return AutostartAction::Skip;
    }
    // ⚠️★ 登録の**前に**、印が書ける場所かだけを確かめる。★ 書けない場所で登録だけ成功すると、
    //   起動のたびに登録し直し、被験者が OS の設定で切っても戻してしまう（code-reviewer LOW）。
    //   ⚠️ 印そのものは**登録が成功してから**書く —— 先に書くと、書いた直後に落ちたとき
    //   二度と再試行しない（Codex P2・2026-09-28）。
    let Some(folder) = marker.parent() else {
        return AutostartAction::Skip;
    };
    if let Err(e) = probe_writable(folder) {
        tracing::error!(
            "O1 autostart: the distribution folder is not writable ({e}); \
             NOT registering (it would be re-registered on every launch)"
        );
        return AutostartAction::Skip;
    }
    // ⚠️★ ホーム側の記録も、登録の**前に**書ける場所かを確かめる（Codex P1・2026-09-28）。
    //   ★ 書けないまま登録すると、被験者が消したあと新しいフォルダで「初めて」と誤読して作り直す。
    if !st.ever_registered {
        let ready = match record.parent() {
            Some(d) => std::fs::create_dir_all(d).and_then(|()| probe_writable(d)),
            None => Err(std::io::Error::other("no parent")),
        };
        if let Err(e) = ready {
            tracing::error!(
                "O1 autostart: cannot write {HOME_RECORD_FILE_NAME} under ~/.gse ({e}); NOT registering"
            );
            return AutostartAction::Skip;
        }
    }
    match reg.register(exe) {
        Ok(where_) => {
            tracing::warn!(
                "O1 autostart: {} the login entry ({where_})",
                if action == AutostartAction::Repoint {
                    "re-pointed"
                } else {
                    "registered"
                }
            );
            // ★ 成功してから記録と印を書く。⚠️ ここで落ちても、次の起動は Register / Repoint を
            //   同じ exe でやり直すだけ（上書きなので登録は増えない）。
            if !st.ever_registered {
                write_or_log(record, "registered", HOME_RECORD_FILE_NAME);
            }
            write_or_log(marker, &here, MARKER_FILE_NAME);
            action
        }
        Err(e) => {
            tracing::warn!("O1 autostart: registration failed (will retry next launch): {e}");
            AutostartAction::Skip
        }
    }
}

/// 印の中身が「いまの exe」を指しているか（純関数）。
pub fn marker_matches(content: Option<&str>, exe: &str) -> bool {
    content.map(|c| c.trim_end_matches(['\r', '\n'])) == Some(exe)
}

/// 印と同じフォルダに書き込めるかを試す（試しに作って消す）。
///
/// ⚠️ 名前は毎回一意にし、**新規作成のみ**（`create_new`）で開く —— 固定名で `fs::write` すると、
/// 同名の既存ファイルを切り詰め、シンボリックリンクなら**リンク先を壊す**（Codex P2・2026-09-28）。
/// `create_new` は既存（リンクを含む）なら失敗し、辿らない。
fn probe_writable(dir: &Path) -> std::io::Result<()> {
    let nanos = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0);
    let probe = dir.join(format!(".gse-probe-{}-{nanos}", std::process::id()));
    std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&probe)?;
    std::fs::remove_file(&probe)
}

/// ⚠️ 書けなかったら黙らない（パスは出さない）。
fn write_or_log(path: &Path, content: &str, what: &str) {
    if let Err(e) = std::fs::write(path, format!("{content}\n")) {
        tracing::error!("O1 autostart: cannot write {what} ({e})");
    }
}

#[cfg(target_os = "macos")]
mod platform {
    use std::path::Path;

    /// LaunchAgent の plist を書く。戻り値はログ用の場所の説明（⚠️ パスを含めない）。
    pub fn register(exe: &Path) -> Result<String, String> {
        // ★ 実体パスにする（シンボリックリンク越しの起動でも同じ `.app` を指す）。
        let exe = exe
            .canonicalize()
            .map_err(|e| format!("canonicalize the executable: {e}"))?;
        let exe = exe
            .to_str()
            .ok_or_else(|| "the executable path is not valid UTF-8".to_string())?;
        if !super::path_is_registrable(exe) {
            return Err("the executable path contains control characters".to_string());
        }
        let home = std::env::var_os("HOME").ok_or_else(|| "HOME is not set".to_string())?;
        let dir = Path::new(&home).join("Library").join("LaunchAgents");
        // ⚠️ エラー文にパスを入れない（ホームにはユーザー名＝実名が入りうる）。
        std::fs::create_dir_all(&dir).map_err(|e| format!("create ~/Library/LaunchAgents: {e}"))?;
        let path = dir.join(format!("{}.plist", super::LAUNCH_AGENT_LABEL));
        std::fs::write(&path, super::launch_agent_plist(exe))
            .map_err(|e| format!("write the plist: {e}"))?;
        Ok(format!("LaunchAgent {}", super::LAUNCH_AGENT_LABEL))
    }

    /// OS に登録（plist）が残っているか。⚠️ 読めないときは「無い」に倒す（作り直さない側）。
    pub fn entry_exists() -> bool {
        std::env::var_os("HOME")
            .map(|h| {
                Path::new(&h)
                    .join("Library")
                    .join("LaunchAgents")
                    .join(format!("{}.plist", super::LAUNCH_AGENT_LABEL))
                    .is_file()
            })
            .unwrap_or(false)
    }
}

#[cfg(windows)]
mod platform {
    use std::path::Path;

    use windows::core::PCWSTR;
    use windows::Win32::Foundation::ERROR_SUCCESS;
    use windows::Win32::System::Registry::{
        RegGetValueW, RegSetKeyValueW, HKEY_CURRENT_USER, REG_SZ, RRF_RT_REG_SZ,
    };

    const RUN_SUBKEY: &str = r"Software\Microsoft\Windows\CurrentVersion\Run";

    fn wide(s: &str) -> Vec<u16> {
        s.encode_utf16().chain(std::iter::once(0)).collect()
    }

    /// HKCU の Run キーに引用符つきの exe パスを書く。戻り値はログ用の場所の説明。
    ///
    /// ⚠️ `canonicalize` しない（Windows では `\\?\` 付きの形になり、Run キーで起動できない）。
    pub fn register(exe: &Path) -> Result<String, String> {
        let exe = exe
            .to_str()
            .ok_or_else(|| "the executable path is not valid UTF-8".to_string())?;
        if !super::path_is_registrable(exe) {
            return Err("the executable path contains control characters".to_string());
        }
        let subkey = wide(RUN_SUBKEY);
        let name = wide(super::RUN_VALUE_NAME);
        let data = wide(&super::run_value(exe));
        let bytes = u32::try_from(data.len() * std::mem::size_of::<u16>())
            .map_err(|_| "the value is too long".to_string())?;
        // SAFETY: 3 つの UTF-16 バッファはすべて NUL 終端で、この呼び出しの間生きている。
        //   `cbdata` は NUL を含む `data` のバイト数（REG_SZ の要件）。
        let rc = unsafe {
            RegSetKeyValueW(
                HKEY_CURRENT_USER,
                PCWSTR(subkey.as_ptr()),
                PCWSTR(name.as_ptr()),
                REG_SZ.0,
                Some(data.as_ptr().cast()),
                bytes,
            )
        };
        if rc != ERROR_SUCCESS {
            return Err(format!("RegSetKeyValueW failed: {}", rc.0));
        }
        Ok(format!(r"HKCU\{RUN_SUBKEY}\{}", super::RUN_VALUE_NAME))
    }

    /// OS に登録（Run の値）が残っているか。⚠️ 読めないときは「無い」に倒す（作り直さない側）。
    pub fn entry_exists() -> bool {
        let subkey = wide(RUN_SUBKEY);
        let name = wide(super::RUN_VALUE_NAME);
        // SAFETY: 2 つの UTF-16 バッファは NUL 終端で、この呼び出しの間生きている。
        //   データを受け取らない（`pvdata` / `pcbdata` / `pdwtype` は None）＝値の有無だけを問う。
        let rc = unsafe {
            RegGetValueW(
                HKEY_CURRENT_USER,
                PCWSTR(subkey.as_ptr()),
                PCWSTR(name.as_ptr()),
                RRF_RT_REG_SZ,
                None,
                None,
                None,
            )
        };
        rc == ERROR_SUCCESS
    }
}

#[cfg(not(any(target_os = "macos", windows)))]
mod platform {
    pub fn register(_exe: &std::path::Path) -> Result<String, String> {
        Err("autostart is not supported on this OS".to_string())
    }

    pub fn entry_exists() -> bool {
        false
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// ⚠️★★★ 対象は「目印由来の O1・G1 でない・同意確認済み」の 1 通りだけ（全 12 通りを見る）。
    #[test]
    fn eligible_only_for_a_consented_o1_distribution() {
        for o1 in [None, Some(O1Source::Env), Some(O1Source::Marker)] {
            for g1 in [false, true] {
                for consent in [false, true] {
                    let want = o1 == Some(O1Source::Marker) && !g1 && consent;
                    assert_eq!(
                        eligible(o1, g1, consent),
                        want,
                        "o1={o1:?} g1={g1} consent={consent}"
                    );
                }
            }
        }
    }

    /// ⚠️★★★ 表のとおり（全 16 通り）。★ 被験者が消した登録は作り直さない・新しいフォルダでは付け替える。
    #[test]
    fn decide_follows_the_table() {
        use AutostartAction::*;
        for el in [false, true] {
            for folder_marker in [false, true] {
                for ever_registered in [false, true] {
                    for entry_exists in [false, true] {
                        let st = AutostartState {
                            folder_marker,
                            ever_registered,
                            entry_exists,
                        };
                        let want = match (el, folder_marker, ever_registered, entry_exists) {
                            (false, ..) | (true, true, ..) => Skip,
                            (true, false, false, _) => Register,
                            (true, false, true, true) => Repoint,
                            (true, false, true, false) => Skip,
                        };
                        assert_eq!(decide(el, st), want, "{el} {st:?}");
                    }
                }
            }
        }
        // ★ 名指しで 2 つ（表の読み違いを防ぐ）
        let removed = AutostartState {
            folder_marker: false,
            ever_registered: true,
            entry_exists: false,
        };
        assert_eq!(
            decide(true, removed),
            Skip,
            "⚠️ 被験者が消した登録を作り直さない"
        );
        let moved = AutostartState {
            folder_marker: false,
            ever_registered: true,
            entry_exists: true,
        };
        assert_eq!(
            decide(true, moved),
            Repoint,
            "★ 新しい版のフォルダへ付け替える"
        );
    }

    /// ⚠️ 制御文字を含むパスは登録しない（plist が壊れて黙って起動しなくなる）。
    #[test]
    fn paths_with_control_characters_are_not_registrable() {
        assert!(path_is_registrable(
            "/Users/p/O1_実施用_macOS/gse-next.app/Contents/MacOS/gse-next"
        ));
        assert!(path_is_registrable(r"C:\Users\Taro Yamada\O1\gse-next.exe"));
        assert!(!path_is_registrable("/Users/p/a\u{1}b/gse-next"));
        assert!(!path_is_registrable("/Users/p/a\nb/gse-next"));
        assert!(!path_is_registrable(""));
    }

    /// ★ 印は `o1.mode` と同じフォルダに置く（両 OS の配布形）。
    #[test]
    fn marker_sits_next_to_the_o1_mode_marker_on_both_os() {
        let mac = Path::new("/Users/p/O1/gse-next.app/Contents/MacOS/gse-next");
        assert_eq!(
            marker_path_for(mac, 4),
            Some(PathBuf::from("/Users/p/O1/o1.autostart"))
        );
        assert_eq!(
            marker_path_for(mac, 4).map(|p| p.with_file_name(crate::o1::MARKER_FILE_NAME)),
            crate::o1::marker_path_for(mac, 4)
        );
        let win = Path::new("/c/Users/p/O1/gse-next.exe");
        assert_eq!(
            marker_path_for(win, 1),
            Some(PathBuf::from("/c/Users/p/O1/o1.autostart"))
        );
        assert_ne!(MARKER_FILE_NAME, crate::o1::MARKER_FILE_NAME);
    }

    /// ★ plist はプラグインと同じ 3 キー・`KeepAlive` なし・パスは XML エスケープ。
    #[test]
    fn launch_agent_plist_escapes_the_path_and_has_no_keepalive() {
        let p = launch_agent_plist("/Users/p/R&D <x>/gse-next.app/Contents/MacOS/gse-next");
        assert!(p.contains("<string>com.johnd.gse-next.o1</string>"));
        assert!(p.contains(
            "<string>/Users/p/R&amp;D &lt;x&gt;/gse-next.app/Contents/MacOS/gse-next</string>"
        ));
        assert!(!p.contains("R&D"), "⚠️ 生の & を残さない");
        assert!(p.contains("<key>RunAtLoad</key>\n\t<true/>"));
        assert!(!p.contains("KeepAlive"), "⚠️ 終了したら終了したままにする");
        // ★ 非 ASCII のフォルダ名（配布フォルダは「O1_実施用_macOS」）はそのまま
        let j = launch_agent_plist("/Users/p/O1_実施用_macOS/gse-next.app/Contents/MacOS/gse-next");
        assert!(j.contains("O1_実施用_macOS"));
    }

    /// ⚠️★ Run の値は引用符で囲む（スペースを含むユーザー名で割れない）。
    #[test]
    fn run_value_is_quoted() {
        assert_eq!(
            run_value(r"C:\Users\Taro Yamada\Downloads\O1_実施用_Windows\gse-next.exe"),
            r#""C:\Users\Taro Yamada\Downloads\O1_実施用_Windows\gse-next.exe""#
        );
    }

    /// ★ 印は「いまの exe」を指しているときだけ処理済み（移動・コピーに追随する）。
    #[test]
    fn marker_must_point_at_the_current_executable() {
        let here = "/Users/p/O1/gse-next.app/Contents/MacOS/gse-next";
        assert!(marker_matches(Some(&format!("{here}\n")), here));
        assert!(marker_matches(Some(&format!("{here}\r\n")), here));
        assert!(
            !marker_matches(
                Some("/Users/p/OLD/gse-next.app/Contents/MacOS/gse-next\n"),
                here
            ),
            "⚠️ 移動・コピーされた印"
        );
        assert!(!marker_matches(Some("registered\n"), here));
        assert!(!marker_matches(Some(""), here));
        assert!(!marker_matches(None, here));
    }

    // --- 流れ全体（偽の登録先・一時フォルダ）---------------------------------------------

    use std::cell::{Cell, RefCell};

    /// 偽の登録先。`register` の呼ばれ方を記録し、失敗させることもできる。
    struct FakeReg {
        entry: Cell<bool>,
        fail: Cell<bool>,
        calls: RefCell<Vec<PathBuf>>,
    }
    impl FakeReg {
        fn new() -> Self {
            FakeReg {
                entry: Cell::new(false),
                fail: Cell::new(false),
                calls: RefCell::new(Vec::new()),
            }
        }
    }
    impl Registrar for FakeReg {
        fn entry_exists(&self) -> bool {
            self.entry.get()
        }
        fn register(&self, exe: &Path) -> Result<String, String> {
            self.calls.borrow_mut().push(exe.to_path_buf());
            if self.fail.get() {
                return Err("boom (test)".to_string());
            }
            self.entry.set(true);
            Ok("fake".to_string())
        }
    }

    fn tmp(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!(
            "gse_autostart_{tag}_{}_{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    /// 配布フォルダ 1 つ分（exe と印の場所）を作る。
    fn folder(root: &Path, name: &str) -> (PathBuf, PathBuf) {
        let f = root.join(name);
        std::fs::create_dir_all(&f).unwrap();
        (f.join("gse-next.exe"), f.join(MARKER_FILE_NAME))
    }

    /// ★ 初回は登録し、同じフォルダの 2 回目は OS に触らない。
    #[test]
    fn first_launch_registers_once_then_leaves_the_os_alone() {
        let root = tmp("once");
        let (exe, marker) = folder(&root, "O1");
        let record = root.join("home").join(".gse").join(HOME_RECORD_FILE_NAME);
        let reg = FakeReg::new();
        assert_eq!(
            handle(&exe, &marker, &record, &reg),
            AutostartAction::Register
        );
        assert!(record.is_file() && marker.is_file());
        assert_eq!(handle(&exe, &marker, &record, &reg), AutostartAction::Skip);
        assert_eq!(reg.calls.borrow().len(), 1, "★ 2 回目は登録を呼ばない");
        let _ = std::fs::remove_dir_all(&root);
    }

    /// ⚠️★★★ 被験者が登録を消したら、同じフォルダでも新しいフォルダでも作り直さない。
    #[test]
    fn a_removed_entry_is_never_recreated() {
        let root = tmp("removed");
        let (exe, marker) = folder(&root, "O1");
        let record = root.join(HOME_RECORD_FILE_NAME);
        let reg = FakeReg::new();
        handle(&exe, &marker, &record, &reg);
        reg.entry.set(false); // 被験者が消した
        let (exe2, marker2) = folder(&root, "O1_new");
        assert_eq!(
            handle(&exe2, &marker2, &record, &reg),
            AutostartAction::Skip
        );
        assert_eq!(reg.calls.borrow().len(), 1, "⚠️ 作り直さない");
        let _ = std::fs::remove_dir_all(&root);
    }

    /// ★ 新しい版のフォルダ・移動したフォルダでは、登録が残っていれば付け替える（印が移ってきても）。
    #[test]
    fn a_new_or_moved_folder_repoints_a_live_entry() {
        let root = tmp("moved");
        let (exe, marker) = folder(&root, "O1");
        let record = root.join(HOME_RECORD_FILE_NAME);
        let reg = FakeReg::new();
        handle(&exe, &marker, &record, &reg);
        // フォルダごと移動した = 印の中身は古い exe のまま
        let (exe2, marker2) = folder(&root, "O1_moved");
        std::fs::copy(&marker, &marker2).unwrap();
        assert_eq!(
            handle(&exe2, &marker2, &record, &reg),
            AutostartAction::Repoint
        );
        assert_eq!(reg.calls.borrow().last().unwrap(), &exe2);
        let _ = std::fs::remove_dir_all(&root);
    }

    /// ⚠️★ 登録に失敗したら印も記録も残さない → 次の起動で再試行する（「消した」と誤読しない）。
    #[test]
    fn a_failed_registration_is_retried_next_launch() {
        let root = tmp("fail");
        let (exe, marker) = folder(&root, "O1");
        let record = root.join(HOME_RECORD_FILE_NAME);
        let reg = FakeReg::new();
        reg.fail.set(true);
        assert_eq!(handle(&exe, &marker, &record, &reg), AutostartAction::Skip);
        assert!(!marker.exists() && !record.exists());
        reg.fail.set(false);
        assert_eq!(
            handle(&exe, &marker, &record, &reg),
            AutostartAction::Register
        );
        assert_eq!(reg.calls.borrow().len(), 2);
        let _ = std::fs::remove_dir_all(&root);
    }

    /// ⚠️ 印を書けない配布フォルダでは登録しない（起動のたびに登録し直さないため）。
    #[cfg(unix)]
    #[test]
    fn an_unwritable_folder_is_not_registered() {
        use std::os::unix::fs::PermissionsExt;
        let root = tmp("ro");
        let (exe, marker) = folder(&root, "O1");
        let dir = marker.parent().unwrap().to_path_buf();
        std::fs::set_permissions(&dir, std::fs::Permissions::from_mode(0o555)).unwrap();
        let record = root.join(HOME_RECORD_FILE_NAME);
        let reg = FakeReg::new();
        let got = handle(&exe, &marker, &record, &reg);
        std::fs::set_permissions(&dir, std::fs::Permissions::from_mode(0o755)).unwrap();
        assert_eq!(got, AutostartAction::Skip);
        assert!(
            reg.calls.borrow().is_empty(),
            "⚠️ 書けない場所では登録しない"
        );
        let _ = std::fs::remove_dir_all(&root);
    }

    /// ⚠️ ホーム側（`~/.gse`）に書けないなら登録しない（消した人に作り直さない、を守れないため）。
    #[cfg(unix)]
    #[test]
    fn an_unwritable_home_is_not_registered() {
        use std::os::unix::fs::PermissionsExt;
        let root = tmp("rohome");
        let (exe, marker) = folder(&root, "O1");
        let gse = root.join("home").join(".gse");
        std::fs::create_dir_all(&gse).unwrap();
        std::fs::set_permissions(&gse, std::fs::Permissions::from_mode(0o555)).unwrap();
        let reg = FakeReg::new();
        let got = handle(&exe, &marker, &gse.join(HOME_RECORD_FILE_NAME), &reg);
        std::fs::set_permissions(&gse, std::fs::Permissions::from_mode(0o755)).unwrap();
        assert_eq!(got, AutostartAction::Skip);
        assert!(reg.calls.borrow().is_empty());
        assert!(!marker.exists());
        let _ = std::fs::remove_dir_all(&root);
    }

    /// ⚠️ 書き込みの試しは、既存のファイルやリンクを辿って壊さない。
    #[cfg(unix)]
    #[test]
    fn the_writability_probe_never_touches_existing_files() {
        let root = tmp("probe");
        let victim = root.join("victim.txt");
        std::fs::write(&victim, b"keep").unwrap();
        // 旧実装の固定名と、それらしい名前のリンクを置いても
        std::os::unix::fs::symlink(&victim, root.join(".o1.autostart.probe")).unwrap();
        probe_writable(&root).unwrap();
        assert_eq!(std::fs::read(&victim).unwrap(), b"keep");
        let left: Vec<_> = std::fs::read_dir(&root)
            .unwrap()
            .filter_map(|e| e.ok())
            .filter(|e| e.file_name().to_string_lossy().starts_with(".gse-probe-"))
            .collect();
        assert!(left.is_empty(), "★ 試しのファイルは残さない");
        let _ = std::fs::remove_dir_all(&root);
    }
}
