//! 段 1 の日の終わりの問いの状態ファイル（`~/.gse/s1_day_state.json`）の読み書き。
//!
//! ★ 中身は [`DayState`]（直近 7 日の「押下を観測したか・尋ねたか・答えたか」）だけで、
//!   NDJSON にも提出物にも入れない（計画の design §3）。再起動をまたいで「1 日の上限」と
//!   「翌日の拾い直し」を守るためだけに使う。
//!
//! ★ 書き方は `eh3::save_ledger` と同じ（一時ファイル → `sync_all` → 置き換え）。
//! ⚠️ 読めない・壊れているときは [`DayStateLoad::Broken`] を返し、呼び出し側はこの走行では
//!   日の問いを出さない（`DayQuestion::disabled()`）。空から数え直すと、同じ日に 2 度尋ねうる。
//!
//! IO を持つので `analysis/` の外に置く（agent-shared 技術制約 11・計画の design §6 の注）。

use std::path::{Path, PathBuf};

use crate::analysis::probe_arbiter::DayState;

/// 状態ファイルの名前。
pub const STATE_FILE_NAME: &str = "s1_day_state.json";

/// 状態ファイルの置き場（ホームが分からなければ `None`）。
pub fn state_path() -> Option<PathBuf> {
    crate::submission::home_dir().map(|h| h.join(".gse").join(STATE_FILE_NAME))
}

/// 状態ファイルを読んだ結果。
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DayStateLoad {
    /// ファイルが無い（初めての起動）。
    Fresh,
    /// 読めた。
    Loaded(DayState),
    /// ファイルはあるが読めない・壊れている。この走行では日の問いを出さない。
    Broken,
}

/// 状態ファイルを読む。
pub fn load(path: &Path) -> DayStateLoad {
    match std::fs::read_to_string(path) {
        Ok(text) => match serde_json::from_str::<DayState>(&text) {
            Ok(s) => DayStateLoad::Loaded(s),
            Err(_) => DayStateLoad::Broken,
        },
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => DayStateLoad::Fresh,
        Err(_) => DayStateLoad::Broken,
    }
}

/// 状態ファイルを書く。一時ファイルに書いてから置き換える（書きかけで落ちても壊れない）。
pub fn save(path: &Path, state: &DayState) -> std::io::Result<()> {
    if let Some(dir) = path.parent() {
        std::fs::create_dir_all(dir)?;
    }
    let tmp = path.with_extension("json.tmp");
    {
        use std::io::Write;
        let mut f = std::fs::File::create(&tmp)?;
        f.write_all(&serde_json::to_vec(state).map_err(std::io::Error::other)?)?;
        // 電源断で中身の空のファイルが残ると、以後ずっと `Broken` になり日の問いが止まる。
        f.sync_all()?;
    }
    if let Err(e) = std::fs::rename(&tmp, path) {
        let _ = std::fs::remove_file(&tmp);
        return Err(e);
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analysis::probe_arbiter::DayRecord;

    fn temp_dir(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!(
            "gse-s1-day-state-{tag}-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap_or_default()
                .as_nanos()
        ));
        std::fs::create_dir_all(&d).unwrap();
        d
    }

    #[test]
    fn missing_file_is_fresh() {
        let d = temp_dir("fresh");
        assert_eq!(load(&d.join(STATE_FILE_NAME)), DayStateLoad::Fresh);
        let _ = std::fs::remove_dir_all(&d);
    }

    #[test]
    fn round_trip_keeps_every_field() {
        let d = temp_dir("roundtrip");
        let path = d.join(".gse").join(STATE_FILE_NAME);
        let mut state = DayState::default();
        state.days.insert(
            20_400,
            DayRecord {
                seen_keys: true,
                asked_same_day: true,
                asked_pickup: false,
                answered: true,
            },
        );
        state.days.insert(
            20_401,
            DayRecord {
                seen_keys: true,
                asked_same_day: false,
                asked_pickup: true,
                answered: false,
            },
        );
        save(&path, &state).unwrap();
        assert_eq!(load(&path), DayStateLoad::Loaded(state));
        // ★ 書きかけの一時ファイルを残さない
        assert!(!path.with_extension("json.tmp").exists());
        let _ = std::fs::remove_dir_all(&d);
    }

    #[test]
    fn broken_file_is_broken_not_fresh() {
        let d = temp_dir("broken");
        let path = d.join(STATE_FILE_NAME);
        std::fs::write(&path, b"{not json").unwrap();
        assert_eq!(load(&path), DayStateLoad::Broken);
        // ★ 空のファイル（電源断の名残）も壊れている側に倒す
        std::fs::write(&path, b"").unwrap();
        assert_eq!(load(&path), DayStateLoad::Broken);
        let _ = std::fs::remove_dir_all(&d);
    }
}
