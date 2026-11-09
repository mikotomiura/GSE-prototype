# 引き継ぎ —— 構造の足りなさの試験の notes が済んだ後、論文 3 の外枠の C2 を直し、attack-me round 2 を 1 回回す（Mac）

> 作成: 2026-11-09（Mac）。このメモを一次資料にしない。一次は次のとおり。
> - 論文 3 の判断: `.steering/20261107-gse-paper3-per-person-learning/decisions.md`（判断 1〜16）と `.steering/20261107-gse-paper3-unsmoothed-residual-check/decisions.md`（判断 12〜14）
> - 構造の試験: `/Users/johnd/GSE-prototype-structure-deficit/experiments/20261107-structure-deficit-test/conditions.md`（D5 が読みの形）と、同じ worktree の `.steering/_handoff/next-session-gse-structure-deficit-after-run.md`
> - attack-me round 1: `.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1/`

## 0 入口の文（前の段が済んでから、Mac の新しいセッションで打ち込む）

前の段は次の 2 つ。どちらかが済んでいなければ、このメモに進まない。
1. HP Z2 で構造の試験の本計算が終わり、結果が `origin/exp/gse-structure-deficit-test` に上がっている。
2. 別のセッションで、構造の試験の notes.md が書かれ、レビューを通っている（`next-session-gse-structure-deficit-after-run.md` の入口の文で始める）。

```
/Users/johnd/GSE-prototype-paper3/.steering/_handoff/next-session-gse-paper3-after-structure-deficit.md を読み、§2 の確かめをしてから §3 のとおり論文 3 の外枠を直し、§4 のとおり attack-me round 2 を 1 回回してください（Codex も加える）。push と PR は私が確かめてから。
```

作業は worktree `/Users/johnd/GSE-prototype-paper3`（枝 `docs/gse-paper3-per-person-learning`）。

## 1 ここまでに済んだこと（2026-11-09 の時点）

- 平滑の無い記号（u・n）と擬似残差の試験は終わった。notes は `experiments/20261107-unsmoothed-residual-check/notes.md`。C1・C2 は、元の記号化の上の測定に限った（判断 12）。モデル検査は 4.2 の 1 文・補足の表 S13・限界の 1 文（判断 13）。
- 外枠の C2 の Strength の最後の一文は、構造の試験の結果を待つために残してある:
  "The reading that the per-person HMM was compensating for missing short-range dependence is consistent with C1 and C2 but was not tested (two structure families, one quantization); the pseudo-residual autocorrelations are not a test of this reading."
- 文献番号は [V497]〜[V534] に付け替えた（判断 15）。次に番号を足すときは、fetch してから origin の全枝の最大の次から採る（2026-11-09 の時点では [V535]）。[V496]（Dunn & Smyth 1996）は provisional のままで、本文は未照合。
- attack-me round 2 は、構造の試験の結果で C2 を直した後に 1 回だけ回すと研究者が決めた（判断 16）。

## 2 始める前の確かめ

- 構造の試験の notes.md が `origin/exp/gse-structure-deficit-test` にあり、「実行と門」がすべて通っている。V1（repro_check）が外れていたら、結果を外枠に持ち込まずに止める。
- 構造の試験の条件の「読まないこと」には「結果は論文 3 に入れない（論文 3 の範囲は凍結）」とある。一方、論文 3 の判断 11（2026-11-07）は凍結を解き、「結果を論文 3 に入れる」と改めた。
  - 構造の試験の notes の「結果の後に変えたこと」か「条件の後の変更」に、この改めが記録されているかを見る。
  - 記録が無ければ、外枠に持ち込む前に研究者に AskUserQuestion で聞く。推奨は、判断 11 は結果より前の決定なので持ち込むこと。その上で、構造の試験の notes に 1 行足すのを、あちらの枝で頼む。
  - こちらの枝から構造の試験の条件・コード・notes を変えない（判断 11 の「守ること」）。
- 論文 3 の枝が `origin/docs/gse-paper3-per-person-learning` と同じか（push 済みか）を見る。2026-11-09 の時点では `04714753`・`d253e270` が未 push だった。

## 3 外枠の直し（papers/per-person-learning/manuscript/outline.md）

構造の試験の notes の語（形 A・A'・B・C、部分 1 の「消える・沿わない・割れる」、部分 2 の「他の人でも勝つ・本人に固有・割れる」）を言い換えずに使う。値は notes の集計値（中央値）だけを使う。

1. C2 の Strength の最後の一文を、形ごとに次の向きで書き換える。どれも外枠の英語で書き、notes の値を添える。
   - 形 A: 「並べ替えで前の記号への依存を消すと上積みも消え、他の人の当てはめでも共通に勝った」。ただし、並べ替えはゆっくりした頻度の変化も消す。また「共通の EM が悪い局所解にある」という説明が残る（gap12 を添える）。だから "was not tested" を "was tested in one way (permutation) and is consistent with it" の程度に改めるだけにし、「確かめた」と書かない。
   - 形 A': 足りなさは効くが、人ごとの違いもある。C1 の take-home（同じ構造と比べると上積みは小さい）の書き方を見直す候補として、研究者に聞く。
   - 形 B: 対抗の説明（母数が多い構造ほど本人の記録で推せない）と合う。補償の読みは Discussion から下げ、限界に移す。C1 の Evidence の読みも見直す候補として研究者に聞く。
   - 形 C（割れた）: 値を並べ、分けられなかったと書く。"was not tested" を「1 つの対照で確かめたが分けられなかった」に改める。
   - 主のセル 3 つがすべて同じ形のときだけ、その形と書く。CS1 C5 k = 5 は別に読む（もともと力が弱い）。
2. Discussion（§5 の行）の "structure-compensation hypothesis: same direction, two families and one quantization" を、構造の試験の量子化 3 通り（記号 10・26・50）・構造 6 つ・並べ替えの対照に合わせて直す。
3. 置き場所: 本文は C2 の一文と Discussion の 1〜2 文まで。表は補足に置く（論文の本文は簡潔に、細部は補足へ）。補足の表の番号は、S13 の次（S14〜）から採る。
4. 構造の試験の結果も、段 1 の候補の採否や ADR-047 の根拠にしない。EM の状態に名前を付けない。CS1 を日本語・IME・GSE の参加者へ広げない。
5. papers/ に GSE の名前・内部のパス・ADR や判断や条件の番号を書かない。
6. 直しは判断（per-person-learning の decisions.md の判断 17〜）に記録し、code-reviewer と /cross-review（Codex も加える・`scripts/run-codex-review.sh` を通して記帳する）を通す。

## 4 attack-me round 2（1 回だけ）

- Skill `attack-me` に従う。round 1 と同じ立場・同じ接地の文献で回し、役ごとに round 1 の指摘と、その指摘への対応（carryover）を渡す。
- Codex も加える。保留済みの論点（既知の未決）の一覧を添え、判定に数えないよう頼む。一覧の候補は次の 3 つ。
  - 一般性は論じただけで試していない（C3）。
  - 記号化は 1 通り（元の 26 記号）を主に置き、平滑の無い記号は補足の確かめ。
  - CS1 の力の弱さ。
- 本文の照合は件数だけを出す（round 1 で本文の 1 行が文脈に印字された逸脱があった）。
- 判定が minor なら閉じ、原稿の本文（Step 2）を勧める。major なら直す順を研究者に聞いてから直す。round 3 は研究者が求めたときだけ回す。

## 5 守ること

- push と PR は研究者が確かめてから。
- 決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて日本語で聞く。報告を地の文の問いで終えない。
- 書き手ごとの値・npz を開かない。キーストロークの内容・NDJSON・書き手ごとの値を外部の LLM（Codex を含む）に送らない。Codex に送るのは外枠と記録の diff だけ。
- `.codex/budget.json` はコミットしない。2026-11-07 の /cross-review の 26,322 tokens は記帳されていない（研究者が知っている）。
- 返答は日本語。記号を多用しない。
