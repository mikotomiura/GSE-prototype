//! ⚠️★★★ **O1 自動起動**（G-1・2026-09-28・`.steering/20260928-o1-resilience-g1-g2-g5/`）。
//!
//! ★ O1 は「ふだんの作業のあいだ、ずっと動いている」ことで成り立つ。⚠️ 再起動のあとアプリを
//! 開き忘れると、**その日から何も記録されない**（受領台帳の「5 日途絶」で後から気づくだけだった）。
//! → ★ O1 の配布形で**初めて起動したときに 1 回だけ**、OS のログイン時起動に登録する。
//!
//! ## ★ 決めたこと（decisions.md 判断 1 / 2 / 9）
//! - ⚠️ **1 回だけ**。配布フォルダ（`o1.mode` の隣）に印 [`MARKER_FILE_NAME`] を置き、印があれば何もしない。
//!   ★ 被験者が OS の設定で切ったら**上書きしない**（やめる権利）。
//!   ★ 印を配布フォルダに置くのは、新しい版のフォルダを配り直したときに
//!   **古いフォルダの exe を指したまま**にならないようにするため。
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

/// ★ 「登録を済ませた」印のファイル名（配布フォルダ・`o1.mode` の隣）。
pub const MARKER_FILE_NAME: &str = "o1.autostart";

/// macOS の LaunchAgent の Label（= plist のファイル名）。
pub const LAUNCH_AGENT_LABEL: &str = "com.johnd.gse-next.o1";

/// Windows の Run キーの値の名前。
pub const RUN_VALUE_NAME: &str = "GSE-O1";

/// 自動起動をどうするか。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AutostartAction {
    /// ログイン時起動に登録する（初回）。
    Register,
    /// 何もしない。
    Skip,
}

/// ⚠️★★★ 登録してよいか（純関数）。
///
/// ★ **目印ファイル由来の O1** かつ **G1 でない** かつ **O1 の同意確認が済んでいる** かつ
/// **印が無い** ときだけ登録する。
/// ⚠️ 同意確認（`submission::o1_consent_acknowledged`・R-7）を条件に入れるのは、
/// **同意の画面を押さずに閉じた人の端末で、ログインのたびに起動させない**ため
/// （code-reviewer HIGH・2026-09-28）。★ 同意した直後にも呼ぶので、初回に同意した人も取りこぼさない。
/// ⚠️ G1 は `o1::resolve` が既に O1 を落としているが、ここでも見る（二重の防御）。
pub fn decide(
    o1: Option<O1Source>,
    g1_active: bool,
    consent_acknowledged: bool,
    marker_exists: bool,
) -> AutostartAction {
    match (o1, g1_active, consent_acknowledged, marker_exists) {
        (Some(O1Source::Marker), false, true, false) => AutostartAction::Register,
        _ => AutostartAction::Skip,
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
    // ⚠️ 判定の前に絞る: 対象でなければ exe も印も見ない（通常運用で IO を増やさない）。
    if decide(o1, g1_active, consent_acknowledged, false) == AutostartAction::Skip {
        return;
    }
    let exe = match std::env::current_exe() {
        Ok(p) => p,
        Err(e) => {
            tracing::warn!("O1 autostart: cannot resolve the executable path: {e}");
            return;
        }
    };
    let marker = match marker_path_for(&exe, crate::g1::exe_to_folder_levels()) {
        Some(p) => p,
        None => {
            tracing::warn!("O1 autostart: cannot resolve the distribution folder");
            return;
        }
    };
    if decide(o1, g1_active, consent_acknowledged, marker.is_file()) == AutostartAction::Skip {
        tracing::info!(
            "O1 autostart: already registered once for this folder (marker present); \
             not touching the OS setting (the participant may have turned it off)"
        );
        return;
    }
    // ⚠️★ **印を先に書く。** 書けない場所（読み取り専用の置き場）で登録だけ成功すると、
    //   起動のたびに登録し直し、被験者が OS の設定で切っても戻してしまう（code-reviewer LOW）。
    //   → ★ 印が書けないなら登録しない。
    if let Err(e) = std::fs::write(&marker, b"registered\n") {
        tracing::error!(
            "O1 autostart: cannot write the marker {MARKER_FILE_NAME} in the distribution folder \
             ({e}); NOT registering (it would be re-registered on every launch)"
        );
        return;
    }
    match platform::register(&exe) {
        Ok(where_) => tracing::warn!("O1 autostart: registered to start at login ({where_})"),
        Err(e) => {
            // ★ 印を戻して次の起動で再試行する。
            let _ = std::fs::remove_file(&marker);
            tracing::warn!("O1 autostart: registration failed (will retry next launch): {e}");
        }
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
}

#[cfg(windows)]
mod platform {
    use std::path::Path;

    use windows::core::PCWSTR;
    use windows::Win32::Foundation::ERROR_SUCCESS;
    use windows::Win32::System::Registry::{RegSetKeyValueW, HKEY_CURRENT_USER, REG_SZ};

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
}

#[cfg(not(any(target_os = "macos", windows)))]
mod platform {
    pub fn register(_exe: &std::path::Path) -> Result<String, String> {
        Err("autostart is not supported on this OS".to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// ⚠️★★★ 登録するのは「目印由来の O1・G1 でない・同意確認済み・印が無い」の 1 通りだけ（全 24 通りを見る）。
    #[test]
    fn registers_only_for_a_consented_first_launch_of_the_o1_distribution() {
        for o1 in [None, Some(O1Source::Env), Some(O1Source::Marker)] {
            for g1 in [false, true] {
                for consent in [false, true] {
                    for marker in [false, true] {
                        let want = if o1 == Some(O1Source::Marker) && !g1 && consent && !marker {
                            AutostartAction::Register
                        } else {
                            AutostartAction::Skip
                        };
                        assert_eq!(
                            decide(o1, g1, consent, marker),
                            want,
                            "o1={o1:?} g1={g1} consent={consent} marker={marker}"
                        );
                    }
                }
            }
        }
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
}
