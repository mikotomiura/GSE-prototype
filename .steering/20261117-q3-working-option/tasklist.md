# タスクリスト

- [x] 一次の確認（ADR-031 D3・判断 5・消費者・同意の版・事前登録の状態）
- [x] 研究者と 5 点を決める（decisions 判断 1〜5）
- [x] ADR-055 と README
- [x] logger・schema_dto・submission（版）・テスト
- [x] emit_schema で current.json
- [x] probeTypes・S1ProbeCard
- [x] 画面で確かめる
- [x] 同意文書をその場で直し印を外す・フォームのビルダーとテスト（判断 7）
- [x] 事前登録の草案
- [x] data-privacy ルール 7・glossary・設計地図
- [x] cargo test・clippy・tsc・gse-replay の golden
- [x] gse-dataset との parity（gse-dataset の枝 chore/schema-q3-working で OK・gse-dataset PR #10）
- [x] /cross-review 1 巡目（Codex を含む・判断 10）
- [x] /cross-review 2 巡目（判断 11・12）
- [x] push と PR（研究者に確かめた・GSE-prototype PR #426）
- [ ] CI を見て merge（研究者に確かめてから・gse-dataset #10 と並べて）
- [ ] 研究者が同意文書を承認して印を入れ直し、ADR-055 を Accepted にする

## 場面ごとの対応

| 場面 | 使うもの |
|---|---|
| Rust | rust-standards・architecture-rules |
| TS | typescript-standards |
| 自己申告の選択肢 | data-privacy |
| ADR の引用 | citation-ssot（既存の番号だけを使う） |
| 画面 | shim で実マウント（memory ui-changes-need-eyes） |
| 完了 | /finish-task（code-reviewer＋/cross-review） |
