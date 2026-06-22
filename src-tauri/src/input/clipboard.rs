//! クリップボード文字数の取得 (capture-schema-freeze CD1)。
//!
//! ペーストイベント時に **クリップボードのテキスト長 (文字数) のみ** を取得し、
//! `external_paste_chars` として記録するためのモジュール。(b) 自力解決率
//! (`manual_contribution_ratio = manual_insert_chars / (manual_insert_chars + external_paste_chars)`,
//! v0.4 §4.2) の分母に使う。
//!
//! **プライバシー (data-privacy CD1)**: 取得するのは文字数 (整数) のみ。クリップボードの
//! **中身 (テキスト) は数えた直後に破棄**し、保存・ログ出力・外部送信を一切行わない。
//! 「長さ」は「内容」ではないため data-privacy ルール1 (Unicode 文字内容を記録しない) と整合する。
//!
//! **レイヤー (architecture-rules)**: OS 固有のクリップボード API (`arboard` 経由で Win32 /
//! NSPasteboard) はこの `input/` モジュールに隔離する。`analysis/` からは呼ばない。
//!
//! **スレッド (hook-constraints)**: 本関数はフックコールバックからは呼ばない。`arboard` は
//! クリップボードを open/close するため、ブロッキング禁止のコールバック内では使用しない。
//! 呼び出しは lib.rs の analysis ループスレッド (フック外) から行う。

/// クリップボードのテキスト文字数 (Unicode スカラ値の数) を返す。
///
/// 画像のみ等でテキストが取れない場合・クリップボードアクセスに失敗した場合は `None`。
/// 取得したテキストは文字数を数えた後この関数内で破棄され、外部へは出ない。
pub fn clipboard_char_count() -> Option<u64> {
    // クリップボードの初期化失敗 (権限・OS リソース等) は本来あってはならない運用事故。
    // 毎回 None になり external_paste_chars が無音で欠落するのを避けるため warn を残す
    // (中身は出さない。エラー内容のみ)。get_text の失敗 (画像のみ等) は正常系なので静か。
    let mut clipboard = match arboard::Clipboard::new() {
        Ok(c) => c,
        Err(e) => {
            tracing::warn!("clipboard init failed; external_paste_chars=null: {e}");
            return None;
        }
    };
    let text = clipboard.get_text().ok()?;
    // `text` はこのスコープを抜けると drop される。文字数のみ持ち出す。
    Some(text.chars().count() as u64)
}
