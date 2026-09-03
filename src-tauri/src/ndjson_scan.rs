//! セッション NDJSON の **行の分類規則の単一真実源**（OS 非依存・依存ゼロの葉モジュール）。
//!
//! # ⚠️★★★ なぜこのモジュールがあるか (★ 2026-09-03 の cross-review で 3 か所の drift が出た)
//!
//! 同じ規則が **3 か所に手書きでコピーされていた**:
//!
//! | どこ | 何を判定していたか | ⚠️ 食い違い |
//! |---|---|---|
//! | `packaging::has_any_data_row` | 「中身のあるファイルか」 | ★ `hook_health` / `ime_state` を**データ行に数えない** |
//! | `reconcile::closed_o1_session_end` | 「閉じ終わった O1 か」 | ★ `session_end` は **`parse_meta_u64` で数値が取れること**を要求 |
//! | `o1::scan_session_shape` (新設) | 「開いたまま残った O1 か」 | ⚠️ **上の 2 つと両方ズレていた** |
//!
//! ★ 実測された帰結:
//! - ⚠️ `meta` ＋ `ime_state` だけのファイル (★ macOS 初回起動で**実際に出る**) を
//!   sweep が「中身あり」と見て閉じ、⚠️ **収束器は絶対に提出しない** ——
//!   ★ 「触ってはならないものに触っている」
//! - ⚠️★★★ 強制終了が `write_meta_end` の**途中**に当たり `{"type":"meta","session_end":` で
//!   切れた場合、sweep は文字列一致で「もう閉じている」と見て**永久に見送り**、
//!   収束器は数値が取れず `None` → ★ **そのファイルは恒久的に提出候補外**。
//!   ⚠️ これは**まさに本実装が塞ごうとしているクラッシュ経路**である。
//!
//! → ★ **規則を 1 か所に出し、3 者すべてがここを呼ぶ。**
//! ⚠️ memory `name-lookup-only-works-within-one-source`「名前で引く対策は 1 つの真実源の
//! 中でしか効かない」の型そのものだった。
//!
//! ⚠️ **`serde_json` を使わない。** ★ `reconcile` は逐語「1 行を丸ごとメモリに載せない走査で
//! 済ませている (★ 1 行は最大 `MAX_SESSION_BYTES` まで許容される)」ためであり、
//! `logger::write_meta_end` が**手書きの固定形**を出すので部分文字列で足りる。

/// `meta` 行の目印。
pub const NEEDLE_META: &str = r#""type":"meta""#;
/// 「開始する」を押した痕跡。★ ⚠️ `meta` 行の `session_start` **フィールド**とは別物。
pub const NEEDLE_SESSION_START: &str = r#""type":"session_start""#;
/// G1 のモードマーカー (`meta` 行)。
pub const NEEDLE_G1_MODE: &str = r#""g1_mode""#;
/// O1 のモードマーカー (`meta` 行)。
pub const NEEDLE_O1_MODE: &str = r#""o1_mode""#;

/// ⚠️★ **データ行に数えない行種**（★ それ自体が被験者の作業を表さないもの）。
///
/// ★ 根拠は `packaging::has_any_data_row` にあった実測である (2026-08-10 macOS):
/// IME モニタは**アプリ起動直後**に `ime_state` を 2 行書くので、ブロックを一度も
/// 始めずに閉じただけの 261B のファイルが「中身あり」で通り、⚠️ `.age` に包まれて
/// **block01 を消費して送信された**（★ 本物の 1 本目が block02 になった）。
///
/// ⚠️ **ここに足す行種は「それ自体が被験者の作業を表さない」ものに限ること。**
const NON_DATA_ROW_TYPES: [&str; 2] = [r#""type":"hook_health""#, r#""type":"ime_state""#];

/// この行は `meta` 行か。
pub fn is_meta_row(line: &str) -> bool {
    line.contains(NEEDLE_META)
}

/// この行は **「中身」を表すデータ行**か。
///
/// ★ `meta` でも診断行でもなく、空でもない行。
pub fn is_data_row(line: &str) -> bool {
    let t = line.trim();
    if t.is_empty() || is_meta_row(t) {
        return false;
    }
    !NON_DATA_ROW_TYPES.iter().any(|n| t.contains(n))
}

/// この行は「開始する」の押下痕 (`session_start` 行) か。
pub fn is_session_start_row(line: &str) -> bool {
    line.contains(NEEDLE_SESSION_START)
}

/// `meta` 行から数値フィールドを 1 つ取り出す (★ 手書きパーサ)。
///
/// ⚠️★★★ **「文字列が在るか」ではなく「数値が取れるか」で判定すること。**
/// ★ 強制終了で `{"type":"meta","session_end":` の途中で切れた行は、
/// 文字列一致では「在る」、本関数では `None` になる。⚠️ 前者で判定すると
/// **そのファイルは恒久的に提出候補外のまま固定される**（★ 上の module doc 参照）。
pub fn parse_meta_u64(line: &str, key: &str) -> Option<u64> {
    let needle = format!("\"{key}\":");
    let start = line.find(&needle)? + needle.len();
    let digits: String = line[start..]
        .chars()
        .take_while(|c| c.is_ascii_digit())
        .collect();
    if digits.is_empty() {
        return None;
    }
    digits.parse::<u64>().ok()
}

#[cfg(test)]
mod tests {
    use super::*;

    /// ⚠️★★ **`meta` ＋ 診断行だけのファイルは「中身なし」**（★ 2026-08-10 の実害の対策）。
    #[test]
    fn diagnostic_rows_are_not_data_rows() {
        assert!(!is_data_row(r#"{"type":"meta","session_start":1}"#));
        assert!(!is_data_row(r#"{"type":"hook_health","t":1}"#));
        assert!(!is_data_row(r#"{"type":"ime_state","t":1,"open":true}"#));
        assert!(!is_data_row("   "));
        assert!(!is_data_row(""));
        // ★ 本物の作業を表す行は数える。
        assert!(is_data_row(r#"{"type":"feat","t":1,"ikiCv":0.1}"#));
        assert!(is_data_row(r#"{"type":"key","t":1}"#));
        assert!(is_data_row(r#"{"type":"session_start","t":1}"#));
    }

    /// ⚠️★★★ **`meta` 行の `session_start` *フィールド* を押下痕と誤認しない。**
    ///
    /// ★ 誤認すると O1 のファイルは**全部**「押下痕あり」になり、⚠️ 1 本も閉じない
    /// (★ 沈黙して直らない)。
    #[test]
    fn the_meta_session_start_field_is_not_a_press() {
        assert!(!is_session_start_row(
            r#"{"type":"meta","session_start":1788000000000,"o1_mode":"marker"}"#
        ));
        assert!(is_session_start_row(r#"{"type":"session_start","t":1}"#));
    }

    /// ⚠️★★★ **途中で切れた `session_end` は「閉じている」と読まない。**
    #[test]
    fn a_truncated_session_end_does_not_parse() {
        assert_eq!(
            parse_meta_u64(
                r#"{"type":"meta","session_end":1700000000000}"#,
                "session_end"
            ),
            Some(1_700_000_000_000)
        );
        // ⚠️ 強制終了で値の直前まで書かれて切れた形。
        assert_eq!(
            parse_meta_u64(r#"{"type":"meta","session_end":"#, "session_end"),
            None
        );
        assert_eq!(parse_meta_u64(r#"{"session_end":}"#, "session_end"), None);
        assert_eq!(
            parse_meta_u64(r#"{"session_end":"x"}"#, "session_end"),
            None
        );
        // ★ 別のキーを拾わない。
        assert_eq!(
            parse_meta_u64(r#"{"type":"meta","session_end":5}"#, "session_start"),
            None
        );
    }
}
