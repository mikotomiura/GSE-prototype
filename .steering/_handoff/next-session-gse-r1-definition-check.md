# 引き継ぎ —— 予測の検査（R1）に定義の検査を当てる

> 作成: 2026-11-15（`.steering/20261115-gse-core-and-edge/` 判断 6・ADR-054 D4）。このメモは入口で一次ではない。一次は ADR-054・論文 1・論文 2 の原稿と実験の notes。
> 更新: 2026-11-16（`.steering/20261116-three-checks-tool-design/` 判断 7）。§0.5 の訂正を先に読む。§1 の「停滞の定義そのものは変えていない」は一部誤り。

## 0 入口の文

```
枝 docs/three-checks-tool-design の .steering/_handoff/next-session-gse-r1-definition-check.md（worktree /Users/johnd/GSE-prototype-three-checks にある）を読んで、予測の検査に定義の検査を当てる計算を /start-task から始めて。§0.5 の訂正を先に読む。
Skill: reproducibility-discipline・verify-before-claiming・subagent-delegation。返答は日本語、決めることは AskUserQuestion で推奨と理由をつけて 1 問ずつ、推奨は「研究として強いか」で決める。push と PR は研究者に確かめてから。
```

- ⚠️ 2026-11-16 の訂正は枝 `docs/three-checks-tool-design` にだけあり、main のこのファイルは古い（その枝の PR は R1 の後に出す・§6）。main や本線のチェックアウトの版を読まない。

- 新しい worktree を切る（本線のチェックアウトを共有しない）。論文 1 の枝 `docs/public-data-findings-paper` と論文 2 の枝 `docs/gse-paper2-stall-shape` のコードを使う。どちらを土台に切るかは grill で決める。
- 実験なので `reproducibility-discipline`（experiments/ の規約・seed・入力の固定）に従う。条件は値を見る前にコミットする（memory「必要な計算は行う」）。

## 0.5 2026-11-16 の訂正（先に読む）

- 論文 1 の確認は、補足で停滞の定義の 3 軸を holdout で振っている（枝 `docs/public-data-findings-paper` の `papers/public-data-findings/manuscript/appendix/supplement.tex:232-234`: 分位 q = 0.995・条件 A の窓 W = 15 s・W = 60 s。値は `experiments/20261105-findings-paper1-prefreeze/results_holdout/confirm_holdout.json` の `sensitivity.replay_q995`・`replay_w15`・`replay_w60`）。推定器の 2 信号（`d_p_stuck`・`d_ewma_x`）とも分岐 1（帯の内・equiv.）だった。
- したがって §1 の「論文 1 の感度解析は停滞の定義そのものは変えていない」は一部誤り（results.tex:137-152 の本文の節だけを見た記述）。ADR-054 Context 6 も同じ前提に立っているが、ADR は書き換えない（結果を見て必要なら別に扱う）。
- 新しく要るのは次の 2 つで、q・W を推定器の信号について振り直すことは要らない:
  1. **学習器の上限を定義で振ること**。論文 1 の学習器（logreg・勾配ブースティング・`confirm_p1.py` `models` :660）は定義を変えて回していない。道具の設計の判断 3（予測の面は学習器の族の上限で判定）と同じ物差しで、推定器（床）と並べる。
  2. **論文 1 が振っていない軸**: θ の固定値（10 s・30 s）・規則 ins・観測区間の扱い（g5・g30）。論文 2 の軸は `core.py:24-28`。
- データ: 論文 1 の CS1 の holdout は確認で 1 回開けたので開かない。見た書き手の側（CS1 2019 の見た 319 人・論文 1 の探索の基準 `d_p_stuck` 0.492（0.485〜0.499）・`experiments/20261106-findings-paper1-exploration/notes.md:39`・`:42`）と、他の公開データで、探索として行うのが既定の候補（grill で決める）。
- コードの所在: 論文 2 のコードは枝 `docs/gse-paper2-stall-shape` には無く、公開 repo の clone `/Users/johnd/stall-shape-multiverse`（1 コミット `8e4890b`）にある。論文 1 は枝 `docs/public-data-findings-paper` の `experiments/20261105-findings-paper1-prefreeze/scripts/confirm_p1.py`（1,509 行）。棚卸しは枝 `docs/three-checks-tool-design` の `.steering/20261116-three-checks-tool-design/inventory.md`。

## 1 なぜやるか

ADR-054 は一言を「本文を保存しない打鍵の観測から、作業の停滞についてどこまで言えるかを、予測・定義・漏れの 3 つの検査で確かめる」にした。予測の検査の材料（R1）は論文 1 の否定の結果（手で決めた推定器の 30 秒の上がりは、停滞の手前を同じ書き手の短い休止の手前から分けない）。論文 1 の感度解析（`papers/public-data-findings/manuscript/sections/results.tex:137-152`）は床・対照・層の 4 種で、停滞の定義そのものは変えていない。Codex（2026-11-15 の codex-consult）が「R3（定義しだい）は R1 にも返る」と指摘した。手順を自分の結果に当て切るのがこのタスク。

## 2 確かめる問い（grill で詰める）

- 代表的な停滞の定義（論文 2 の multiverse の中から、事前に決めた少数）で、推定器の 30 秒の上がりの AUC と、前の打鍵の単純な量の学習器の AUC の順位と差が保たれるか。
- 論文 1 の停滞の定義: 条件 A（直前 30 秒の挿入から削除を引いた押下が 1 未満）が立ち上がって θ（書き手のそれまでの打鍵間隔の 0.99 分位）続いた時点を始まりとし、始まりの手前の最後の文字の入力 u から次の文字の入力まで 30 秒以上（`papers/public-data-findings/manuscript/sections/data.tex:26-40`）。
- 論文 2 の定義の空間: `experiments/20261107-stall-shape-multiverse/`（枝 `docs/gse-paper2-stall-shape`）。

## 3 先に決めること（値を見る前にコミット）

1. 選ぶ定義の数と選び方（multiverse の軸の端と中央など）。選ぶ理由は R1 の値を見ずに書く。
2. データ。CS1 の holdout は論文 1 の確認に使ったので、新しい定義での読みは探索になる。探索と書くか、別の分け方をするか。
3. 何をもって「保たれる」とするか（順位・差の符号・帯の内外）。
4. 結果の置き場（新しい experiments/ のフォルダ）と、論文 1・2 のどちらに還元するか（還元しない選択も含む）。

## 4 既知の制約

- NDJSON・O1 の記録は外部の LLM に送らない（集計値だけ）。
- 投稿先と状態は公開物と docs に書かない。
- 結果は ADR-054 D4 の「これから」を埋めるもので、一言を変える判断は結果を見て別に行う。

## 5 結果を道具の設計に返す（2026-11-16 追記）

R1 の結果は、枝 `docs/three-checks-tool-design` の `.steering/20261116-three-checks-tool-design/design.md` の次の 3 か所に返す（判断 7: 道具の前に今のコードで出した結果を、道具の計算を外から照らす相手にする）。
- §4 の層 ② `test_replay_r1_definition_check` の入力と期待値（R1 の集計の置き場と、判定の値）。
- §7 の「道具の前」の項（済んだこと・振った軸）。
- §8 の未決のうち、R1 で答えが出たもの（例: 学習器の族の初版を 2 つに留めるか）。
R1 の experiments/ の本体は R1 の枝に置き、設計の枝には上の 3 か所の追記だけを入れる（PR を論理の単位ごとに分ける）。

## 6 設計の枝の PR（R1 の後）

1. 枝 `docs/three-checks-tool-design`（worktree `/Users/johnd/GSE-prototype-three-checks`）に §5 の追記を 1 コミット足す。`git -C <worktree> branch --show-current` で枝を確かめてからコミットする。
2. origin/main との両方向の差を見る（`git log HEAD..origin/main`・`git log origin/main..HEAD`）。
3. 研究者に確かめてから push と PR。docs だけなので `[skip ci]`（空コミット＋マージの subject・memory feedback-push-only-no-pr-during-runs）。PR が main に入ると、この引き継ぎの訂正も main に入る。

