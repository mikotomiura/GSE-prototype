# 判断の記録

研究者の決定は `.steering/20261012-eh3-windows-device-rest/decisions.md` 判断 3 #2（直す）。実装の判断（問いにしない）:

- 「この層が書いたことがあるか（`last_set`）」でなく、読み戻しで「いま元の壁紙を出しているか」で決める。記録を失った異常終了の後でも、肖像が残るモニタは元と違うパスなので書き戻す。

## レビューの記録（2026-10-12・`57efc90a..227992cf`）

- code-reviewer（Sonnet）: HIGH なし。
  - MEDIUM: 外れたモニタも「書くモニタ」に数えるので、つながったモニタがすべて元でも位置を書く → 採用。つながっていて元でないモニタだけで決めた。テスト `a_disconnected_portrait_monitor_does_not_rewrite_the_position`。
  - LOW: 元のファイルが変わったときの `ok` の検査が無い → 採用。テスト `an_edited_original_already_shown_is_not_reported_as_restored`。コメントの参照先 → 判断は device-rest にあるのでそのまま。本人のモニタとの混在 → 既存の `only_the_monitor_the_person_changed_is_left_alone` が覆う。
  - 位置について確かめたこと: `show_image` は `set_position` を呼ばない（`wallpaper_windows.rs`・`wallpaper_macos.rs` の `set` は画像だけ・macOS の `set_position` は no-op）。
- security-checker（Sonnet）: CRITICAL・HIGH・MEDIUM なし。LOW 2 件。
  - `same_path` が正規化しない → 一致しなければ書く側に倒れる（安全側）ので対応不要。
  - `detect_user_change` の `starts_with(work_dir)` が大文字小文字を区別する → 以前からある・範囲外。記録だけ。
- /cross-review の Codex 系統 1 巡目（`wallpaper.rs` だけ）:
  1. [P1・要確認] この層が位置を替えた後、パスだけ元へ戻ると位置が戻らない → 対応不要。この層は肖像を書くときに位置を替えない（上の確認）。
  2. [P2] 外れたモニタだけでも位置を書く → 採用（code-reviewer の MEDIUM と同じ）。
  3. [P2・要確認] 同じパスで中身が変わったとき、書かないと OS の古い表示が残りうる → 対応不要。元のファイルは本人のファイルで、変わった中身を書き直すのは本人の壁紙に触れること。今までも「戻った」とは報告しない（`ok` 偽）。テストで固定した。
- 変異: 外れたモニタを数える（1 件落ちる）・ハッシュの検査を外す（1 件落ちる）。`cargo test --lib` 923 passed・clippy 緑。
