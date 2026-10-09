# タスクリスト

## 準備
- [x] 議論と決定を `.idea/` に記録する
- [x] Step 0・1: 下位問い・予算・名前空間・還元先・attack-me の要否を研究者が承認（`decisions.md` 判断 1）
- [x] 前提 Skill を読む（literature-card / citation-ssot / subagent-delegation）
- [x] worktree を origin/main から切る

## サーヴェイ
- [x] Step 2: 5 angle を Sonnet で並列に探索（5 本とも 2.5〜3.6 分で完走・入れ子なし）
- [x] 断定に使う一次をメインが開いて確かめる（逐語は正規化してから照合・保存されていなかった 3 本は自分で取得）
- [x] Step 3: claim 抽出（22 件）
- [x] Step 4: 3 票の検証・エビデンス温度（confirmed 17・判定不能 5・否決 6）
- [x] Step 5: カードを書く（動機・検証状態・gate の要点・否決リスト・登録しなかったもの）
- [x] Step 6: references.md に append（直前に全ブランチの末尾番号を測り直した。AF001 の重複は判断 2）
- [x] Step 7: _index.md に 1 行
- [x] Step 8: RP は還元不要と明記（カードの「GSE への還元」）
- [x] Step 9: 自己点検（下）
- [x] check_citations.py が `=== 違反なし ===`（1 回目は違反 1 件 → 是正 → 再実行で違反なし）

### Step 9 自己点検
- [x] 反証 angle を含めた（A4・ほかの angle でも反証を落とさない指示）
- [x] 下位問いごとに温度を分けた（SQ1 は a/b/c で別・SQ3 は反証を別行）
- [x] 判定不能を弱い支持に丸めていない（SQ2・SQ3・SQ4 の直接の問いは判定不能と書いた）
- [x] 否決リストを残した（6 件）
- [x] 全カードの [n] が references.md に実在する（check_citations）
- [x] provisional と active を取り違えていない（全件 Crossref で確認したので active。[P453] は一次全文未取得と明記）
- [x] _index.md の「やり残し」が次ラウンドの入口になっている（6 項目）

## 具体化
- [x] `.idea/` §7 に結果を書く
- [x] 設計案を具体化する（§8: 面・時・造形・本人の操作・プライバシー・評価の段・棄却線・研究者が決めること）

## 閉じる
- [x] 単独でコミット・push（PR は出さない）（`cac7327c`）
- [x] /cross-review 1 巡目（Claude 19 件・Codex 5 件・すべて採用 → 判断 4）。Codex は 44,395 トークン（worktree の台帳に記帳・コミットに含める）
- [x] /cross-review 2 巡目（足した主張・留保の境界条件）。Claude 13 件・Codex 3 件・すべて採用 → 判断 5
- [x] `.idea/` に 2 巡の訂正を反映する（版管理外）
- [ ] 研究者への報告（[P362] の項目の確認結果・用語の訂正・PR は計測の run が終わってから）
