# タスクリスト

- [x] issue #333・ADR-039・[V194] [V239] [V240] の登録状況を読む
- [x] 下位問い S1〜S4 を研究者と合意（2026-10-09）
- [x] 探索 4 本を並列で投げる（S1〜S4）
- [x] 一次の逐語をメインが確かめる（27 件・decisions.md 判断 2）
- [x] claim 抽出 → 3 票の検証（32 件）
- [x] カード（`docs/literature/20261009-keystroke-release-reidentification.md`・10 枚）
- [x] references.md に append（[V243]〜[V263]）＋ [V237] [V239] [V240] [P274] の注記を更新 → check_citations.py「違反なし」
- [x] _index.md に 1 行
- [x] research-positioning.md への還元（§4 を 1 か所精緻化・decisions.md 判断 4）
- [x] コミット（1 ラウンド = 1 コミット・cc2409e5）→ push（PR は出さない・判断 5）
- [x] issue #333 にコメント（https://github.com/mikotomiura/GSE-prototype/issues/333#issuecomment-6074912901）
- [x] レビュー（code-reviewer ∥ /cross-review の Codex 系統）→ 指摘を一次で確かめて反映（判断 6）

## 研究者が決めること（本タスクの外）

- [x] ADR-039 の訂正 4 件の扱い → 日付つきの注を足した（判断 7）
- [x] 【決 5】→ C を既定・関門後に A（判断 7）
- [x] 関門の攻撃を 3 つに・集計値も点検（判断 8）
- [x] 【決 5-b】【決 6】（形）【決 6-a】【決 9】と、実測の設計 4 点（判断 9）
- [x] 【決 6】を同等性の判定に・合格は測った条件に限る・実験の値は Claude が推奨・確定の Enter は先に確かめる・【決 9】は復元の分析と照合の試作を待つ（判断 10）
- [x] 関門の実測の最初の一歩 → 長さの並びの一意性（判断 7）
- [ ] 長さの並びの一意性の実測（別のタスク・研究者の決定で新しいセッションから。引き継ぎ: `.steering/_handoff/next-session-length-sequence-uniqueness.md`）
- [ ] 関門の細部 6 点（本番の関門の設計のタスクで・ADR-039 D6 の未決の論点・判断 11）
- [ ] 同意文 v2 の第 3 層の文面（別のタスク・研究者と詰める）
- [x] PR にする時期 → 研究者「計測は行っていないので通常通り」（2026-10-09）→ PR → CI → merge
