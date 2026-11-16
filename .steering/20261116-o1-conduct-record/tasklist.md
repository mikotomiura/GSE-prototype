# タスクリスト

## 場面ごとの道具（完了前に照合する）
- 条件の文とコード → code-reviewer・security-checker・/cross-review（Codex には条件の文とコードだけ）
- 設計の分岐 → grill で閉じた（判断 0〜3）。条件の文で迷ったら codex-consult
- 実験の規約 → reproducibility-discipline（SEED・lockfile・gse-replay の SHA-256・p1-episode の版）

## 手順
- [x] grill（判断 0〜3）・worktree `docs/o1-conduct-record`
- [x] O1 の終了を記録する（判断 5・入力は条件の digest で固定）。受領台帳の「O1 終了判定」タブは研究者が更新
- [x] zip の新しい 43 本を受け取りフォルダへ足す（`cp -n`・既存 99 本は zip とバイト一致・足した後に 142 本すべて一致・2026-11-16）
- [ ] 削除の求めが 0 件であることを確かめる（run.sh の門で計算の直前に）
- [x] n4・stall-decomposition・c1c2c6・論文 1 の学習器のコードを読み、使い回せる所を決める（design.md）
- [x] 条件の文（conditions.md）・コード・陽性対照・通しの検査・変異（20 種すべて赤）
- [x] /cross-review と security-checker 1 巡目 → 直し（判断 8）
- [x] /cross-review 2 巡目 → 直し（判断 9・変異 39 種すべて赤）→ コミット（記録を開く前）
- [ ] 別の PR: 削除台帳 A-7 に今回の派生物の名前を足す（研究者に確かめてから・判断 8）
- [ ] 復号（repo の外）→ `run.sh` を 1 回
- [ ] notes.md（実施の記録・記述・探索の AUC・言える範囲）
- [ ] code-reviewer・security-checker・/cross-review
- [ ] push（PR は研究者に確かめてから）
