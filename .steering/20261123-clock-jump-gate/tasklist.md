# タスクリスト

- [x] 原因をコードと記録の行種・時刻で確かめる（requirement.md 背景）
- [x] 研究者に直す時期と直し方を確かめる（decisions 判断 1）
- [x] 回帰テストを先に書き、赤を見る（3 件が赤・範囲の内で待たない 1 件は stub でも緑）
- [x] `o1.rs` に判定と待ちを書く
- [x] `lib.rs::run()` から呼ぶ
- [x] cargo test（1388 件緑）/ clippy / replay（15 snapshots 一致）/ fmt
- [x] /cross-review（code-reviewer・security-checker・Codex）1 巡目（判断 3）
- [x] 高水位の待ち（判断 4）
- [ ] /cross-review 2 巡目
- [ ] コミット・push（PR は研究者に確かめる）
