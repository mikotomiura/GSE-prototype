//! 通常のモード（EH3・O1・G1 でない走行）の招待の契機の設定と、招待を許す条件（ADR-040 D4・タスク B）。
//!
//! 設計は `.steering/20261101-invitation-wiring/design.md` §2・§3。契機の種類と判定は
//! `analysis::invitation`（純ロジック）にあり、ここは設定ファイルの IO と「許すか」の純関数だけを持つ。
//!
//! - 設定ファイル: `~/.gse/invitation_trigger.json`（研究者が置く・本人の画面には出さない）。中身は
//!   [`TriggerKind`] の JSON 1 つ。
//!   - 無い → 推定器の既定（[`Trigger::MAIN`]・今の挙動）。
//!   - あるのに読めない・未知の欄・値の欠け・範囲外 → **通常のモードの招待を出さない**（fail-closed）。
//! - EH3 はこのファイルを読まない（`eh3::TriggerStage` のまま・EH3 の挙動は変わらない）。
//! - ⚠️ 値は applog に書かない（警告は「読めなかった」とだけ）。

use std::path::{Path, PathBuf};

use crate::analysis::invitation::TriggerKind;

/// 契機の設定のファイル名（`~/.gse/invitation_trigger.json`）。
pub const TRIGGER_FILE_NAME: &str = "invitation_trigger.json";

/// 契機の設定の置き場。
pub fn trigger_path() -> Option<PathBuf> {
    crate::submission::home_dir().map(|h| h.join(".gse").join(TRIGGER_FILE_NAME))
}

/// 設定ファイルを読んだ結果。
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum TriggerConfig {
    /// 使う契機（無いファイルは推定器の既定）。
    Kind(TriggerKind),
    /// 読めない・範囲外。通常のモードの招待を出さない。
    Invalid,
}

impl TriggerConfig {
    /// 招待を出してよい設定か。
    pub fn usable(self) -> Option<TriggerKind> {
        match self {
            TriggerConfig::Kind(k) => Some(k),
            TriggerConfig::Invalid => None,
        }
    }
}

/// 設定ファイルを読む。
pub fn load_trigger_config(path: &Path) -> TriggerConfig {
    match std::fs::read_to_string(path) {
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => {
            TriggerConfig::Kind(TriggerKind::default())
        }
        Ok(t) => match TriggerKind::from_json(&t) {
            Some(k) => TriggerConfig::Kind(k),
            None => {
                tracing::warn!("invitation trigger config is unreadable; invitations are off");
                TriggerConfig::Invalid
            }
        },
        Err(_) => {
            tracing::warn!("invitation trigger config is unreadable; invitations are off");
            TriggerConfig::Invalid
        }
    }
}

/// 起動後に 1 回だけ読む（セッションの宣言の行と状態機械が同じ値を使う）。
///
/// ホームが解決できないときは `Invalid`（無いのか読めないのか分からないので出さない側）。
pub fn process_config() -> TriggerConfig {
    static CONFIG: std::sync::OnceLock<TriggerConfig> = std::sync::OnceLock::new();
    *CONFIG.get_or_init(|| match trigger_path() {
        Some(p) => load_trigger_config(&p),
        None => {
            tracing::warn!("invitation trigger config path is unavailable; invitations are off");
            TriggerConfig::Invalid
        }
    })
}

/// 通常のモードで招待を許すか（純関数）。
///
/// 真になるのは、セッションの宣言が真で、O1・G1・EH3 のどれでもなく、設定ファイルが読めたときだけ。
/// 第 1 週（宣言が偽）・O1・G1 では偽。EH3 は別の経路（`eh3::assignment`）なので、ここでは常に偽。
pub fn normal_invitation_allowed(
    declared: bool,
    o1: bool,
    g1: bool,
    eh3: bool,
    config: TriggerConfig,
) -> bool {
    declared && !o1 && !g1 && !eh3 && config.usable().is_some()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analysis::invitation::Trigger;

    fn write(dir: &Path, text: &str) -> PathBuf {
        let p = dir.join(TRIGGER_FILE_NAME);
        std::fs::write(&p, text).unwrap();
        p
    }

    fn tmp(name: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("gse-inv-trigger-{name}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&d);
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    #[test]
    fn missing_file_is_the_estimator_default() {
        let d = tmp("missing");
        assert_eq!(
            load_trigger_config(&d.join(TRIGGER_FILE_NAME)),
            TriggerConfig::Kind(Trigger::MAIN.into())
        );
    }

    #[test]
    fn valid_file_is_read() {
        let d = tmp("valid");
        let p = write(&d, r#"{"kind":"random","per_active_hour":3,"seed":9}"#);
        assert_eq!(
            load_trigger_config(&p),
            TriggerConfig::Kind(TriggerKind::Random {
                per_active_hour: 3.0,
                seed: 9
            })
        );
        let p = write(&d, r#"{"kind":"none"}"#);
        assert_eq!(
            load_trigger_config(&p),
            TriggerConfig::Kind(TriggerKind::Off {})
        );
    }

    #[test]
    fn broken_unknown_missing_or_out_of_range_files_fail_closed() {
        let d = tmp("bad");
        for bad in [
            "",
            "{",
            r#"{"kind":"rising"}"#,
            r#"{"kind":"rising","delta":0.2}"#,
            r#"{"kind":"random","seed":1}"#,
            r#"{"kind":"random","per_active_hour":6}"#,
            r#"{"kind":"none","x":1}"#,
            r#"{"kind":"rising","delta":-1,"window_ms":10}"#,
            r#"{"kind":"random","per_active_hour":100,"seed":1}"#,
        ] {
            let p = write(&d, bad);
            assert_eq!(load_trigger_config(&p), TriggerConfig::Invalid, "{bad:?}");
        }
        // 読めない（ファイルでなくディレクトリ）
        let sub = d.join("dir");
        std::fs::create_dir_all(&sub).unwrap();
        assert_eq!(load_trigger_config(&sub), TriggerConfig::Invalid);
    }

    #[test]
    fn normal_invitation_gate() {
        let ok = TriggerConfig::Kind(TriggerKind::default());
        assert!(normal_invitation_allowed(true, false, false, false, ok));
        // 第 1 週（宣言が偽）
        assert!(!normal_invitation_allowed(false, false, false, false, ok));
        // O1・G1・EH3 では偽
        assert!(!normal_invitation_allowed(true, true, false, false, ok));
        assert!(!normal_invitation_allowed(true, false, true, false, ok));
        assert!(!normal_invitation_allowed(true, false, false, true, ok));
        // 設定が読めない
        assert!(!normal_invitation_allowed(
            true,
            false,
            false,
            false,
            TriggerConfig::Invalid
        ));
        // 「なし」は読めた設定なので許す（統制の条件。契機が立たないだけ）
        assert!(normal_invitation_allowed(
            true,
            false,
            false,
            false,
            TriggerConfig::Kind(TriggerKind::Off {})
        ));
    }
}
