# tasklist

## 場面ごとの道具（完了前に照合）

- 文献の探索 → /literature-review・Sonnet のサブエージェント 4 本の並列（メインは検索を叩かない）
- 逐語の照合 → メインが一次（pypdf・抄録）で。取れない一次は Chrome
- 出典の登録 → citation-ssot（メインが直列で append）
- 完了時のレビュー → code-reviewer ＋ /cross-review（Codex に O1・段 1 の記録は渡さない。docs の diff だけ）

## タスク

- [x] worktree を origin/main から切る（`/Users/johnd/GSE-prototype-daily-scale`・枝 `docs/gse-daily-item-scale-literature`）
- [x] 下位の問いの合意（判断 1）
- [x] サブエージェント 4 本を並列で投げる
- [x] 戻りの逐語・書誌をメインが照合する
- [x] claim 台帳・3 票・温度
- [x] カードを書く
- [x] references.md に append（V386〜）
- [x] _index.md に 1 行
- [x] research-positioning.md への還元の判断
- [x] check_citations.py 違反なし
- [x] code-reviewer ＋ /cross-review（1 巡目・判断 6）
- [ ] /cross-review 2 巡目（修正の差分）
- [x] 単独コミット（d2f71bfe・push は研究者）
