# 設計（GSE の全体の設計の整理）

## アプローチ

1. MhD の解剖: コード（`analysis/` の features・heads・engine・loop_step・key_gate）を一次で読み、空回し 2 本の notes と照らす。分布の形は CoAuthor の中間（空回しと同じ・取っておいた書き手を除く）で数え直す（`mhd-anatomy.md`）。
2. 決めることは研究者に 1 問ずつ聞き、`decisions.md` に問いと答えを残す。
3. 結果を SSOT へ落とす: 決定は ADR（ADR-044）、状態は地図（`docs/architecture/gse-design-map.md`）、事前登録の項目は草案（S1-E8）。

## 変更対象

- 新規: `docs/adr/ADR-044-hmm-frozen-through-stage1.md`・`docs/architecture/gse-design-map.md`
- 変更: `docs/adr/README.md`（ADR-044 の行）・`docs/preregistration-stage1.md`（S1-E8）・`docs/agent-shared.md`（リンクハブに地図・ADR の範囲を 044 へ）
- コードの変更は無い。

## テスト戦略

- 文書だけの変更。地図・ADR の各行の根拠（ファイルと行・ADR の番号）を一次で引けることを、レビューで確かめる（code-reviewer・/cross-review）。
- 解剖の数え（mhd-anatomy.md §3）は repo に出すのが集計値だけであることを確かめる。
