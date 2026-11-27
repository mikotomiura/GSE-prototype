# 論文 3 の深さを仕組みで示す: 窓の重なりの用量反応

## 背景

論文 3（per-person-learning）の S14 を入れた版の attack-me（revision-integrated round 1）は major だった。4 人が一致した点の 1 つは、深さが仕組みで示されていないこと。本文 307 行の「重なる窓が入力を従属させ、弱い構造の共有モデルが個人化を良く見せる」は推測のままで、支えは補足の S12（構造の埋め合わせ）と S13（重ならない窓で向きが戻る・記号の数が約 1/30 に減る）だけである。研究者は、書き方で閉じずに仕組みの計算（窓の重なりの用量反応）を足すと選んだ（論文 3 の判断 6 の (1)）。

引き継ぎ: `.steering/20261125-paper3-next-venue/handoff-mechanism-dose-response.md`（枝 docs/gse-paper3-per-person-learning）。

## ゴール

窓の歩み（重なりの強さ）を段階的に変え、記号の数をそろえる比べを足して、得（per-person hmm3 − 共有 hmm3）・本人の連鎖への差・ジョイントの選びの残りが重なりに沿うかを、条件を先に凍結して測る。結果を論文 3 の本文の仕組みの節と図 1 つにし、S12・S13 の結論を本文に上げる。

## スコープ

### 含むもの
- 条件 `experiments/20261127-window-overlap-dose/conditions.md` を、データを見る前にコミットする
- 条件の attack-me（stage prereg・Codex を加える・minor が 2 回続いたら閉じる）と凍結
- コード・陽性対照・変異・端の再現の門、本計算、notes
- 論文の枝へ結果の要約を持ち込み、本文に仕組みの節と図 1 つ、S12・S13 の結論（数 1 つと読み 1 文）を足す（移す・まとめるで埋め合わせる）
- attack-me round 2（revision-integrated・carryover）と venue-fit の当て直し（handoff の手順 6・7）

### 含まないもの
- 自己相関を制御した合成の系列での比べ・取り置いた 30% での確認（研究者が選んでいない。広げるなら問う）
- CS1 での用量反応（広げるなら研究者に問う）
- S14 の数と読みの文を変えること
- 実データの書き手ごとの値と打鍵の中身を外部の LLM に送ること

## 受け入れ条件

- [ ] conditions.md がコード・結果より前の commit にある
- [ ] 条件の attack-me で minor が 2 回続いた（記録は `attack-me/prereg/round-N/`）
- [ ] 端の再現の門（歩み 1 = S13 の u・歩み 30 の位相 0 = S13 の n）が相対 1e-9 で通る
- [ ] 陽性対照と名指しの変異がすべて期待どおり
- [ ] notes に凍結した読みの語と、論文への持ち込みの文の型が当たっている
- [ ] 論文 3 の本文に仕組みの節と図 1 つが入り、本文の語数を length-log に書いた

## 関連ドキュメント

- 論文 3 の判断 6: `.steering/20261125-paper3-next-venue/decisions.md`
- round 1 の判定: `.steering/20261125-paper3-next-venue/attack-me/revision-integrated/round-1/verdict.md`
- S13 の条件と notes: `experiments/20261107-unsmoothed-residual-check/`
- `docs/experiment-tracking.md`
