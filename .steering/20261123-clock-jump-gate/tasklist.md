# タスクリスト

- [x] 原因をコードと記録の行種・時刻で確かめる（requirement.md 背景）
- [x] 研究者に直す時期と直し方を確かめる（decisions 判断 1）
- [x] 回帰テストを先に書き、赤を見る（3 件が赤・範囲の内で待たない 1 件は stub でも緑）
- [x] `o1.rs` に判定と待ちを書く
- [x] `lib.rs::run()` から呼ぶ
- [x] cargo test（1388 件緑）/ clippy / replay（15 snapshots 一致）/ fmt
- [x] /cross-review（code-reviewer・security-checker・Codex）1 巡目（判断 3）
- [x] 高水位の待ち（判断 4）
- [x] /cross-review 2 巡目（判断 5）
- [x] /cross-review 3 巡目（判断 6・新しい問題なし）
- [x] コミット・push（PR は研究者に確かめる）
- [x] PR #435 を出した（研究者の選択: PR まで。マージと版上げは研究者が確かめてから）
  - CI（run 45128616213）: check (mac self-hosted) 緑。check (win self-hosted) は `link.exe not found` でコンパイル前に赤 —— 同じ日の他の 2 本の枝（45102450969・45097217086）も同じ赤で、11-19 までは緑。G-GEAR のランナーの環境の問題で、この変更とは関係ない。frontend-check は 1 歩も走らず（11 月の Actions の無料分の枯渇）。
- [ ] Windows でのコンパイルの確かめ（G-GEAR のランナーが直った後に re-run）
- [ ] マージ → 版上げ（v0.1.43）→ 配り直し（研究者が確かめてから）
