//! 段 1（ADR-043・本人の試しと確認の段）の「段 1 モード」判定（OS API 非依存の純ロジック ＋ `current_exe` のみ）。
//!
//! ★ O1 の収集の器の上に載せる層である（EH3 と同じ作り方・`.steering/20261105-gse-m5-probe-wiring-plan/design.md` §1）。
//! 提出・自動起動・導入 ID・区間の削除・ファイル名・`start_session` の拒否・介入の拒否は、
//! `o1::is_o1()` の分岐をそのまま共有する。段 1 で変わるのは、問い（C4 のプローブと日の終わりの問い）を
//! 出すことだけで、その効果は `lib.rs` の駆動役が適用する。
//!
//! ⚠️ 印 `s1.mode` が無い O1 の配布物は、本モジュールを足す前と 1 バイトも変わらない
//! （`logger::tests::o1_meta_unchanged_without_s1_marker`）。
//!
//! ## EH3 と同時に立てない（計画の判断 7）
//!
//! EH3 は招待を出す。段 1 は招待を出さない。両方の印があれば **両方を落として** 素の O1 として動かし、
//! 呼び出し側が `tracing::error!` で残す（`o1::resolve` が G1 との衝突で O1 を落とす作法と同じ倒し方）。
//! どちらかを勝たせると、配り間違いを静かに記録し続けるため。

use std::path::{Path, PathBuf};

/// フォルダに置く印のファイル名。★ `o1.mode` の鏡像。中身は読まない（有無だけ）。
pub const MARKER_FILE_NAME: &str = "s1.mode";

/// 開発・検証用の環境変数。★ 値が `"1"` に完全一致したときだけ立てる。
pub const ENV_VAR: &str = "GSE_S1_MODE";

/// 段 1 モードを立てた引き金。★ `O1Source` の鏡像。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum S1Source {
    /// 実行ファイルを包むフォルダに `s1.mode` があった（配布形）。
    Marker,
    /// 環境変数 `GSE_S1_MODE=1` が立っていた（開発・検証用）。
    Env,
}

impl S1Source {
    /// `meta` の `s1_mode` と診断ログに書く固定文字列。
    pub fn as_str(self) -> &'static str {
        match self {
            S1Source::Marker => "marker",
            S1Source::Env => "env",
        }
    }
}

/// 環境変数による判定（純関数）。★ `o1::o1_enabled_by_env` と同じ厳しさ（`"1"` に完全一致だけ）。
pub fn s1_enabled_by_env(value: Option<&str>) -> bool {
    matches!(value, Some("1"))
}

/// 段 1 モードの検出（純関数）。★ 印を優先する（`o1::decide` と同じ）。
pub fn decide(marker_exists: bool, env_value: Option<&str>) -> Option<S1Source> {
    if marker_exists {
        Some(S1Source::Marker)
    } else if s1_enabled_by_env(env_value) {
        Some(S1Source::Env)
    } else {
        None
    }
}

/// 段 1 と EH3 の両方が検出されたか（★ 呼び出し側が **必ず** ログに残すための述語）。
pub fn conflicts_with_eh3(detected: Option<S1Source>, eh3_detected: bool) -> bool {
    detected.is_some() && eh3_detected
}

/// ⚠️★★★ **段 1 は O1 の上でだけ立て、EH3 と同時には立てない**（純関数）。
///
/// - O1 でなければ落とす（通常運用・G1 では問いを出さない）。
/// - EH3 も検出されていれば落とす。⚠️ このとき EH3 も落とすのは呼び出し側の責務
///   （[`conflicts_with_eh3`] が真なら `eh3::resolve` に渡す前に EH3 の検出を捨てる）。
pub fn resolve(
    detected: Option<S1Source>,
    o1_active: bool,
    eh3_detected: bool,
) -> Option<S1Source> {
    if !o1_active || eh3_detected {
        None
    } else {
        detected
    }
}

/// 段 1 と EH3 の検出から、立てる段 1 と EH3 に渡す検出を決める（純関数・`lib.rs` が起動時に 1 回呼ぶ）。
///
/// ★ 両方が検出されたら、段 1 を落とし、**EH3 の検出も捨てて**返す（EH3 は `OnceLock` なので、
/// `eh3::resolve` に渡す前に決める・本タスクの判断 7）。EH3 の型には依存しない（`T` で受ける）。
pub fn resolve_with_eh3<T>(
    s1_detected: Option<S1Source>,
    o1_active: bool,
    eh3_detected: Option<T>,
) -> (Option<S1Source>, Option<T>) {
    if conflicts_with_eh3(s1_detected, eh3_detected.is_some()) {
        (None, None)
    } else {
        (
            resolve(s1_detected, o1_active, eh3_detected.is_some()),
            eh3_detected,
        )
    }
}

/// `exe` に対応する印の想定パス（純関数）。★ 階層数は `g1` を再利用する（`o1::marker_path_for` と同じ）。
pub fn marker_path_for(exe: &Path, levels_up: usize) -> Option<PathBuf> {
    Some(crate::g1::folder_up(exe, levels_up)?.join(MARKER_FILE_NAME))
}

static S1: std::sync::OnceLock<Option<S1Source>> = std::sync::OnceLock::new();

/// 起動時に 1 回だけモードを確定させる。★ 2 回目以降は黙って無視する（`o1::set_mode` と同じ）。
pub fn set_mode(mode: Option<S1Source>) {
    let _ = S1.set(mode);
}

/// 段 1 モードの引き金。`None` なら段 1 ではない。
pub fn mode() -> Option<S1Source> {
    S1.get().copied().flatten()
}

/// 段 1 モードか。
pub fn is_s1() -> bool {
    mode().is_some()
}

/// 実行環境から段 1 モードを検出する（IO あり）。★ `run()` から起動時に 1 回だけ呼ぶ。
///
/// 印の探索に失敗した場合は印無しとして扱う（`o1::detect_from_env` と同じ）。
pub fn detect_from_env() -> Option<S1Source> {
    let marker_exists = std::env::current_exe()
        .ok()
        .and_then(|exe| marker_path_for(&exe, crate::g1::exe_to_folder_levels()))
        .is_some_and(|p| p.is_file());
    let env_value = std::env::var(ENV_VAR).ok();
    decide(marker_exists, env_value.as_deref())
}

#[cfg(test)]
mod tests {
    use super::*;

    /// 段 1 は O1 の上でだけ立つ（4 通り）。
    #[test]
    fn s1_requires_o1() {
        for src in [S1Source::Marker, S1Source::Env] {
            assert_eq!(resolve(Some(src), true, false), Some(src));
            assert_eq!(
                resolve(Some(src), false, false),
                None,
                "O1 でなければ落とす"
            );
        }
        assert_eq!(resolve(None, true, false), None);
        assert_eq!(resolve(None, false, false), None);
    }

    /// ⚠️ 段 1 と EH3 の印が両方あれば段 1 を落とし、衝突を述語で知らせる（EH3 を落とすのは呼び出し側）。
    #[test]
    fn s1_and_eh3_both_dropped() {
        assert_eq!(resolve(Some(S1Source::Marker), true, true), None);
        assert!(conflicts_with_eh3(Some(S1Source::Marker), true));
        assert!(
            !conflicts_with_eh3(None, true),
            "段 1 が無ければ衝突ではない"
        );
        assert!(!conflicts_with_eh3(Some(S1Source::Env), false));
        // ★ EH3 に渡す検出も落とす（2026-11-06 code-reviewer MEDIUM: 旧版は述語を呼ぶことしか見ていなかった）
        let eh3 = Some("eh3-assignment");
        assert_eq!(
            resolve_with_eh3(Some(S1Source::Marker), true, eh3),
            (None, None)
        );
        assert_eq!(
            resolve_with_eh3(None, true, eh3),
            (None, eh3),
            "段 1 が無ければ EH3 はそのまま"
        );
        assert_eq!(
            resolve_with_eh3(Some(S1Source::Env), true, None::<&str>),
            (Some(S1Source::Env), None)
        );
        assert_eq!(
            resolve_with_eh3(Some(S1Source::Env), false, None::<&str>),
            (None, None),
            "O1 でなければ段 1 は立たない"
        );
        // ★ 呼び出し側（`lib.rs`）がこの関数の戻り値を EH3 に渡していることを、本文で確かめる。
        const LIB: &str = include_str!("lib.rs");
        assert!(
            LIB.contains("crate::s1::resolve_with_eh3(")
                && LIB.contains("crate::eh3::resolve(eh3_kept,"),
            "lib.rs が段 1 と EH3 の決め方を通していない"
        );
    }

    /// 印が env より優先される。
    #[test]
    fn s1_marker_beats_env() {
        assert_eq!(decide(true, None), Some(S1Source::Marker));
        assert_eq!(decide(true, Some("1")), Some(S1Source::Marker));
        assert_eq!(decide(false, Some("1")), Some(S1Source::Env));
        assert_eq!(decide(false, None), None);
    }

    /// env は `"1"` の完全一致だけ。
    #[test]
    fn env_value_exactly_1() {
        assert!(s1_enabled_by_env(Some("1")));
        for v in ["0", "true", "yes", " 1", "1 ", "", "01"] {
            assert!(!s1_enabled_by_env(Some(v)), "{v:?} を通してはならない");
        }
        assert!(!s1_enabled_by_env(None));
    }

    #[test]
    fn as_str_is_fixed() {
        assert_eq!(S1Source::Marker.as_str(), "marker");
        assert_eq!(S1Source::Env.as_str(), "env");
    }
}
