//! 提出ファイル名ラベル用 participant_id の検証 (単一情報源)。
//!
//! `<participant>_<stem>.age` のファイル名に使う ID は **英数字のみ・1..=16 文字**に限る
//! (パストラバーサル防止 + 提出物名が崩れないため)。この述語を `packaging` (feature = "package"
//! の提出 CLI 経路) と `lib.rs` の `submit_latest_session` (アプリ内提出・default ビルド) の
//! **双方が参照**する。feature gate を跨いで規則がサイレントに drift しないよう、ここを唯一の
//! 定義とし、`packaging::is_valid_participant_id` は本関数を re-export する。
//!
//! 注意: `logger::is_valid_participant_id` は**別規則**(セッションディレクトリ用・最大 64 文字・
//! `-_` 許可) で意図的に異なる。本モジュールは提出ラベル専用の厳格規則だけを扱う。

/// 提出ラベル用 participant_id が妥当か (英数字のみ・1..=16 文字)。
pub fn is_valid_participant_id(id: &str) -> bool {
    !id.is_empty() && id.len() <= 16 && id.chars().all(|c| c.is_ascii_alphanumeric())
}

#[cfg(test)]
mod tests {
    use super::is_valid_participant_id;

    #[test]
    fn accepts_assigned_ids_rejects_junk() {
        assert!(is_valid_participant_id("P006"));
        assert!(is_valid_participant_id("P000"));
        assert!(is_valid_participant_id("abc123"));
        assert!(!is_valid_participant_id("")); // 空
        assert!(!is_valid_participant_id("../etc")); // パストラバーサル
        assert!(!is_valid_participant_id("P 3")); // 空白
        assert!(!is_valid_participant_id("P006\n")); // 改行
        assert!(!is_valid_participant_id("P0123456789abcdef0")); // >16
    }
}
