# タスクリスト

- [x] 調査・研究者の判断（判断 1・2）
- [x] 行種の削除の鍵のテスト（設計 3）: `every_line_type_in_the_schema_has_a_redaction_key`・除外の表を `NEVER_REDACTED` に 1 か所へ
- [x] 削除の引く量の純関数と `redact_file` への適用（設計 1）
- [x] 走行中の累計と状態ファイルへの適用・`delete_time_range` の順序
- [x] 一時停止の扱い（設計 2・判断 4）
- [x] schema の doc（`HandmarkDay`）と `emit_schema` の一致（説明の文だけ）
- [x] gse-dataset の schema の同期のコミット（`/Users/johnd/gse-dataset-hm-predist`・枝 `chore/schema-handmark-redaction`・a19cbf2・push 前）
- [x] 同意の md・フォームの §4 の 2 番・受付メール・`participant-setup-guide.md`・承認の印を外す・`docs/o1-deletion-ledger.md`
- [x] 変異で赤を見る（8 件すべて赤・ファイルは元どおり）
- [x] `cargo test --workspace`・clippy・fmt・フォームのテスト 358 件・変異 119 件・readiness の selftest 85 件
- [x] code-reviewer・security-checker（処理は decisions.md の表・判断 6・7）
- [ ] /cross-review（Codex 込み）
- [ ] 研究者の承認の取り直し → push・PR（研究者に確かめる）
