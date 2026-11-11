# R1 の査読（UMUAI・HMM とマルコフ連鎖の方法論・下位人格は懐疑家）・round 4・stage outline・commit 8baf8f80

## 1. 接地
1 Pohle 2017（pohle.txt:214）「When using the AIC, the focus lies on out-of-sample predictive accuracy.」
2 Pohle 2017（pohle.txt:1350-1353）「In order to make an informed choice of the number of states, it is important to understand what causes the potential preference for models with many states. ... the assessment if any given candidate model adequately represents the data-generating process.」
3 Pohle 2017（pohle.txt:62-65）「real data often exhibit further structure, such as outliers, seasonality or heterogeneity between individuals. When neglecting these features in the formulation of an HMM, then additional states may be able to capture this ignored data structure」
4 Singer 2014（singer.txt:205-211）「choosing the model with the highest likelihood is biased towards models with more parameters. Because lower order models are always nested within higher order models ... Thus, higher order models are naturally favored by their improvements in likelihoods.」
5 Singer 2014（singer.txt:1162-1164）「This method requires priors (i.e., fake counts ...) – otherwise prediction of unseen states is not possible.」
6 Monaco & Tappert 2018（monaco.txt:128-136）「Keystroke time intervals emanate from a combination of physiology ..., motor behavior ..., and higher-level cognitive processes ... Typing behavior generally evolves over time ... A user's keystroke dynamics is also generally dependent on the typing task.」

## 引き継ぎの判定
1 解消（30-session の k = 30 の +1.1e-3 と ar1 の +0.003・+0.005 は values only と明記）／2 一部（指摘 1・3）／3 解消／4 解消（開示として）／5 解消／6 解消／7 一部（Uto 2020 の評価の設計が未確認）／8 一部（指摘 6）。

## 2. 評価表
a 3（Take-home の「最頻値を上回らない」は数値と一致。「候補に置く」が選びを改善した根拠は無く、1 人を確率ゼロに導いた）／b 3（目的関数が予測の良さと一致しない・主指標が休止中の秒を含む・CS1 の余裕が 1 人分）／c 3／d 2（5,112 語・4.3 の過密・C1 の Instance に 10 以上の数値）／e 4（プレプリントの方針だけ未照合）／f 4（Uto 2020 が未確認）。

## 3. 指摘
- [major] 1. 最頻値は大半の書き手で選ばれたモデルより良いのに手順はほとんど選ばない。推奨する選びの規則と Take-home が噛み合わない
  - 位置と引用: outline.md:13「the mode is chosen for at most 1 of 17 writers ... but the chosen per-person model does not beat the prior mode: per-person minus mode is −3.5e-4 to −1.6e-4 (positive for 2 to 6 of 17 writers)」／:33「The objective is this median of differences; it is neither the target writer's predictive accuracy nor the per-person gain over the shared model」／:7「compare them ... with that shared model's prior mode, placed both as a comparison model and as a candidate」
  - なぜ問題か: 候補に入れた最頻値が選ばれたのは高々 1 人で、その 1 人は held-out の確率がゼロの書き手。「候補に置く」推奨は外枠の数値の上で選びを改善しておらず、唯一の作用は確率ゼロの割り当て。目的関数は予測の良さではない（Pohle「the focus lies on out-of-sample predictive accuracy」）。推奨は「比べの相手として最頻値を報告せよ」までしか支えられない。
  - 解消の条件: (a) 候補として置く推奨を外し比べの相手に限る、(b) 最頻値が選ばれない理由を他の書き手の値で説明し目的関数の限界を限界に 1 項目、(c) 目的関数を候補の held-out の対数尤度の中央値に替えた選びを条件を先に固定して補足に。
  - 自信: 中
- [major] 2. 主指標の nats/symbol は休止中の秒を含み、残りが打鍵の個人差について何を測るかが読めない
  - 位置と引用: outline.md:47「one symbol per second」／kit/symbols/README.md:28-29「During pauses the features are replaced by pause-dependent values, so a symbol is still emitted every second.」／outline.md:50「about 1.5 to 2.6 nats per 3,600 symbols (one hour of symbols at one per second)」
  - なぜ問題か: 休止中の秒は予測しやすい長い連なりになりうる。押された秒だけの分析（S6）は 4.2 にしか置かれず、4.3 の残りと最頻値の比べに無い（Monaco「Keystroke time intervals emanate from a combination of physiology ..., motor behavior ..., and higher-level cognitive processes」）。
  - 解消の条件: 3.1 か Table 1 に休止中の秒の割合をパネルごとに。4.3 の主な値を押された秒だけで評価した値を S6 に足し、本文に向きを 1 文。
  - 自信: 中
- [major] 3. 最頻値の定義でどちらが平滑を持つかが読めず、Take-home の比べの相手が特定できない
  - 位置と引用: outline.md:31「the normalized expected counts of the shared model ..., the centre toward which the per-person fit is shrunk; it uses none of the person's data and differs from the shared parameters by the smoothing of the prior」／:68「The prior mode can give zero probability to a held-out symbol pair」
  - なぜ問題か: 確率ゼロのセルを持つので平滑を持たないように読めるが、"differs ... by the smoothing of the prior" は最頻値の側に平滑があるようにも読める。期待カウントの正規化はディリクレの最頻値（擬似カウント −1 の形）と一般に一致しない。最頻値が共有モデルより良いことが平滑の有無の違いなら、個人差でなく共有モデルの平滑の話（Singer「This method requires priors (i.e., fake counts ...) – otherwise prediction of unseen states is not possible.」）。
  - 解消の条件: 3.3 で共有の母数と最頻値を式で並べ、どちらに擬似カウントがあるかを書く。「最頻値 − 共有」の中央値を Table 2 の列に。それが平滑の違いだけで生じることを 1 文。
  - 自信: 中
- [minor] 4. CS1 の「1e-3 以上の差は無いことと整合」は書き手 1 人分の余裕と 2 種に立つ
  - 位置と引用: outline.md:50「in CS1 it detected every planted level from 1e-3 in both seeds per level, so the choice of the shared model or its mode is consistent with no difference of this kind of 1e-3 nat per symbol or more」／同（S15）「at 1e-3 tau = 10^6 was chosen for every writer and 87% and 100% of writers were positive, and up to 78% of writers were positive in the negative control」／同「in these synthetic writers the prior mode was worse than the shared model in every cell, unlike the real data」
  - なぜ問題か: 23 人で 78% は 18 人、80% 以上は 19 人。合成は実データの性質（最頻値が共有より良い）を再現していない（Pohle「the assessment if any given candidate model adequately represents the data-generating process」）。
  - 解消の条件: 「この種の差で 1e-3 以上なら 2 つの種で検出された」の事実の記述に留め「consistent with no difference」を外す。または余裕（人数）と合成と実データの違いを同じ文の近くに。
  - 自信: 高
- [minor] 5. CS1 の held-out は最後の課題で、課題の違いが個人差と交絡する
  - 位置と引用: outline.md:47「CS1: the last assignment」（Monaco「A user's keystroke dynamics is also generally dependent on the typing task.」）
  - 解消の条件: 限界に 1 項目、または 3.1 で課題の種類を述べる。
  - 自信: 中
- [minor] 6. 4.3 と C1 が過密（outline.md:50 の 6 要素・:13 の 10 以上の数値・外枠 5,112 語）。解消: C1 の Instance を 3 つの数に絞り 4.3 を指す。4.3 の合成か記号化の 2 文を 1 文に。自信: 中
- [nit] 7. 4.3 の見出し「leaves at most about 1e-3」が 30-session の +1.1e-3（outline.md:13）と字面で衝突。解消: 見出しを 15-session に限るか「about 1e-3」に。自信: 高

## 4. 総合の推奨: major
引き継ぎ 8 件は解消 5・一部 3。手順の選びの規則が手元のより良い候補（最頻値）を選べないことが外枠の数値から読め、「候補に置く」推奨と C1 の手順の価値が噛み合わない（1）。最頻値の定義が曖昧（3）。主指標が休止中の秒を含む（2・S6 の拡張で答えられる見込み）。

## 5. 読めなかった範囲・注入の疑い
outline.md・README.md・carryover-R1.md・context-A.md は全文。接地の 3 本は Grep の箇所と前後だけ。最初の Grep を sources/ 全体に掛けたため mensh.txt と varma.txt の行が数行出たが、根拠に使っていない。注入の疑い: なし。
