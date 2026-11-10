//! 記録の **即時一時停止 / 再開** (ADR-014 **D7-ii**)。
//!
//! ## ⚠️★★★ なぜ独立モジュールなのか
//!
//! ★ フラグを読むのは **`logger`** で、書くのは **`lib.rs` の IPC**、表示するのは
//! **Frontend** である。⚠️ どれか 1 つの中に置くと、他の 2 つがそのモジュールへ
//! 依存することになり `architecture-rules` ルール 1（依存は一方向）に触れる。
//! → ★ **依存を 1 つも持たない葉モジュール**にして、誰からも読めるようにする。
//!
//! ## ★★★ どこで止めるか — **ロガーの書き出し点**である
//!
//! ⚠️ フックの送信点では止めない。★ 理由:
//!
//! | 案 | ⚠️ 問題 |
//! |---|---|
//! | フックの送信を止める | ⚠️ 分析スレッドから見ると**沈黙**と区別が付かず、`starved_ms` / 介入判定が
//!   「離席した」と誤解する。★ 再開時に特徴量バッファを捨てる後始末も要る |
//! | ★ **ロガーの書き出しを止める**（採用） | ★ 被験者への約束は逐語「**すぐ止める**（記録を止める）」であり、
//!   **ファイルに 1 バイトも書かない**ことがその約束の実体である |
//!
//! → ★ 一時停止中も画面の表示（いまの状態）は動く。⚠️ **ディスクには何も残らない。**
//!
//! ## ⚠️★★★ 「止めた」と「信号が無かった」を混同させない
//!
//! ★ ADR-013 **D1** の原則（「**信号が無い**」と「**計器が無い**」を分ける）と同じ理屈で、
//! **遷移のたびに `recording_pause` 行を書く**。⚠️ 書かないと、解析側は
//! 「被験者が止めた 3 時間」と「本当に何も起きなかった 3 時間」を**永久に区別できない**。
//!
//! ★ `recording_pause` 行は**一時停止中でも書く**（★ そうしないと「再開した」が記録できない）。

use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};

/// 記録を一時停止しているか。
///
/// ⚠️ ★ 既定は `false`（＝ 記録する）。★ アプリを起動し直すと **必ず記録側に戻る** ——
/// ⚠️ 「止めたつもりが次回も止まったままで、何も取れていなかった」を作らないため。
/// ★ 被験者は稼働中インジケータで現在値を常に確認できる（D7-i）。
static RECORDING_PAUSED: AtomicBool = AtomicBool::new(false);

/// いま一時停止中か。
pub fn is_paused() -> bool {
    RECORDING_PAUSED.load(Ordering::Acquire)
}

/// 一時停止 / 再開を設定し、**直前の値**を返す。
///
/// ★ 呼び出し側は「値が変わったときだけ `recording_pause` 行を書く」ために直前値を使う。
pub fn set_paused(paused: bool) -> bool {
    let prev = RECORDING_PAUSED.swap(paused, Ordering::AcqRel);
    if prev != paused {
        PAUSE_EPOCH.fetch_add(1, Ordering::AcqRel);
    }
    prev
}

/// 一時停止と再開の切り替えの回数（値が変わったときだけ進む）。
///
/// ★ 段 1 の駆動役（1 秒に 1 回 `is_paused` を読む）が、1 秒の中の「止めてすぐ再開」を
///   取りこぼさないために見る。止めていない走行では誰も読まない。
static PAUSE_EPOCH: AtomicU64 = AtomicU64::new(0);

/// 一時停止と再開の切り替えの回数。
pub fn pause_epoch() -> u64 {
    PAUSE_EPOCH.load(Ordering::Acquire)
}

/// 一時停止中に**それでも書いてよい**行種か。
///
/// ★ 純関数にして、判断を 1 か所に閉じる（⚠️ ロガーの match 腕に条件を散らさない）。
///
/// | 通すもの | ★ 理由 |
/// |---|---|
/// | `recording_pause` | ⚠️ **再開したことを記録できなくなる** |
/// | `meta` | ★ `session_end` / `capabilities` はファイルの**整合性**そのもの。
///   ⚠️ 落とすと「閉じていないファイル」が残り `reconcile` が提出候補から外す |
///
/// ⚠️★★★ **それ以外は 1 行も書かない。** ★ `key` / `feat` / `paste` / `pointer_bin` /
/// `focus_transition` はすべて落ちる（＝ 被験者への約束「すぐ止める」の実体）。
pub fn is_writable_while_paused(line_type: &str) -> bool {
    matches!(line_type, "recording_pause" | "meta")
}

#[cfg(test)]
mod tests {
    use super::*;

    /// ⚠️★★★ 記録される側の行は 1 つも通さない。
    ///
    /// ## ⚠️★★★ 2026-09-14: **ハードコード列挙をやめた** (ADR-031 D4-3)
    ///
    /// ★ 旧実装は行種名を**手で並べていた**ので、⚠️ **新しい行種を足しても
    /// このテストは何も言わなかった**（★ 列に足し忘れれば、ただ検査されないだけ）。
    /// → ★ **宣言（`capabilities::KNOWN_LINE_TYPES`）から導出する。**
    /// ⚠️ こうすると「行種を足して `KNOWN_LINE_TYPES` に載せた瞬間」から
    /// **自動的に一時停止ゲートの検査対象に入る**。
    #[test]
    fn paused_blocks_every_data_line_type() {
        // ★ 通してよい 2 つ（⚠️ [`paused_still_allows_the_marker_and_meta`] が対で固定する）。
        const ALLOWED: [&str; 2] = ["meta", "recording_pause"];
        let mut checked = 0usize;
        for t in crate::capabilities::KNOWN_LINE_TYPES {
            if ALLOWED.contains(t) {
                continue;
            }
            assert!(
                !is_writable_while_paused(t),
                "{t:?} が一時停止中に書けてしまう"
            );
            checked += 1;
        }
        // ⚠️★★★ **検査が空回りしていないこと**（★ `verify-before-claiming` ルール 6）。
        //   ★ `KNOWN_LINE_TYPES` が壊れて空になっても緑にならないようにする。
        // ⚠️★★★ **魔法数を置かない**（2026-09-14・code-reviewer LOW）。
        //   ★ `>= 19` だと 1 件消えても緑のままだった。→ **宣言から導いて厳密に一致させる。**
        assert_eq!(
            checked,
            crate::capabilities::KNOWN_LINE_TYPES.len() - ALLOWED.len(),
            "検査した行種の数が宣言と合わない。★ KNOWN_LINE_TYPES か ALLOWED が壊れていないか見ること"
        );
    }

    /// ★ 「再開した」を書けること / ファイルを閉じられること。
    #[test]
    fn paused_still_allows_the_marker_and_meta() {
        assert!(is_writable_while_paused("recording_pause"));
        assert!(is_writable_while_paused("meta"));
    }

    /// ★ `swap` が直前値を返すこと（★ 遷移したときだけ行を書くために要る）。
    ///
    /// ⚠️ グローバルな Atomic を触る唯一のテストである（★ 他のテストは純関数のみ）。
    #[test]
    fn set_paused_returns_the_previous_value() {
        set_paused(false);
        assert!(!set_paused(true), "false → true の直前値は false");
        assert!(is_paused());
        assert!(
            set_paused(true),
            "true → true の直前値は true (遷移していない)"
        );
        assert!(set_paused(false), "true → false の直前値は true");
        assert!(!is_paused());
    }
}
