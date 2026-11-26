# 設計

- [2]: 選んだ段 1 のタグ（`s1_tag`）に `src-tauri/src/handmark_store.rs` と `handmark_driver.rs` があるかを `git cat-file -e` で見る。
  タグの選び方は変えない（手跡の無い段 1 のタグを飛ばして別のタグを選ぶと、配布物の `s1-release-tag.txt` との照合と食い違うため）。
- [4] 実体: `dist_facts_` の走査に手跡の 2 語を足し、段 1 の語とは別の行（`HM_LACKS`）で返す。
- [4] 表: 根の `handmark_assignment.json` と `.sha256` を読み、`.sha256` の最初の語が 64 桁の 16 進で、表の SHA-256 と合うか。
  表は JSON として読めるか。読み方はアプリ（`assignment.rs` の `parse_sha_file`）に合わせる（BOM を落とし最初の語・小文字）。
- 対照の語は門の本文に直書きしない形を保つ（selftest の対照は実行時に連結）。
- テスト戦略: selftest に対照を足す。実物の v0.1.41・v0.1.42 の .app で陽性対照。
