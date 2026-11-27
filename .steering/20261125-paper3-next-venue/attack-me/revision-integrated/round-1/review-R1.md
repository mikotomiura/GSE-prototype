# review-R1（行動の記号列の系列モデルの方法論・TMLR・round 1）

総合: major。読んだもの: brief-R1・context-A・一覧のファイル・monaco/pohle/singer。supplement の大半（1〜159・175〜289・324〜559 行）・figdata・kit README は読んでいない。references.bib は key の grep だけ。注入の疑い: なし。

## 1. 接地
- G1 Singer 2014（singer.txt:230-237）"we also allow k to be zero. In such a zero order Markov chain model the next state does not depend on any current or previous events, ... by how frequently it occurs in the navigational paths. This should serve as a baseline for our evaluations."
- G2 Singer 2014（295-297）"Using the log-likelihoods of the specific order models is not enough, as we will always get a better fit to our training data using higher order Markov chains."
- G3 Pohle 2017（870-872）"use model checking methods, in particular residual analyses, but potentially also simulation-based checks, to obtain a more detailed picture of the fitted models, and to validate or invalidate any given candidate model"
- G4 Pohle 2017（863-864, 880-882）"decide a priori on the candidate models" / "in cases where there seems to be no strong reason to prefer one particular model over another ... results for each of these models should be reported."
- G5 Pohle 2017（383-386）"additional states will be included as per recommendation of model selection criteria, in order to compensate for the inflexibility of the model to otherwise capture the additional structure."
- G6 Monaco & Tappert 2018（730-733, 808-813）"bias parameters that depend on event types with low frequency toward the marginals ... while parameters that depend on event types with high frequency will remain unchanged." / "Scenario 2 evaluates the POHMM implementation with parameter smoothing, whose effect diminishes as N increases."

## 2. 評価表
a 3（325 行が S14 の限定を落とす・題の "vanishes" と 3e-2 まで検出できないことの緊張）／b 3（残差・模擬・分割・入れ替えは基準を満たす。穴: 2 次のチェーンが無い・格子の端・S14 で頻度の基準線と同じ値・「検定を使わない」と S14 の p 値の食い違い）／c 3（0 次・1 次の基準線は系列モデルの標準の作法で ML の読者に新しい教訓として薄い。窓の重なりの仕組みは推測のまま〔307〕）／d 2（造語が多い・限界の第 1 項に 5 論点）／e 3（"generalizable insights" が弱い）／f 3（Singer 2014 の 0 次の基準線と次数の選択に触れない。「安い確かめ」が既存の作法そのものであることを率直に書くべき）

## 3. 指摘
- [major] 限界の第 1 項の末尾の 1 文が限定を落とし、安定した違いの手がかりとして読まれる
  - 位置と引用: main.tex:325（"In an exploratory check ... than other writers' training units did."）
  - なぜ問題か: 直前の "neither remainder was attributed to such differences" への反証として読まれる。S14 は supplement.tex:601 "These cells do not separate stable differences from closeness in time (drift)."・576（drift ρ=0.9 が 4 セルすべてで検出）・604 "device, keyboard and setting, the way of working ... It is not read as a person-specific typing difference." の限定を付けるが本文は落とす。"in the space of one-state transition tables" は遷移が識別を担ったと読ませるが、頻度の基準線は k=5 で 0.982 と同じ、k=1 で 0.941 対 0.912（585-587）。G1 の 0 次で同じ識別ができる。
  - 解消の条件: 例 "... did, as did symbol frequencies alone; the check separates neither stable differences from closeness in time nor the writer from device, setting or topic, and it is a ranking, not a predictive gain." または考察の 1 段に移して限定と一緒に置く。
  - 自信: 高
- [major] "lack sufficient depth" への答えが仕組みでなく広さになっている
  - 位置と引用: main.tex:307 "The weak comparison is likely not specific to keystrokes: features computed over overlapping windows make consecutive inputs dependent, and a shared model whose structure misses that dependence makes a per-person fit look good. We have not checked this in other domains."／136 "consecutive windows share 29 of their 30 seconds and the values are smoothed, consecutive symbols are strongly dependent"／199 "with non-overlapping windows ... the \hmmthree{} beats the own chain in CoAuthor"
  - なぜ問題か: 中心の発見は記号化（29/30 の重なりと平滑）からほぼ予想がつき、重ならない窓で向きが逆になった。一般的な教訓になるはずの仕組み（入力の自己相関が強いほど同じ構造どうしの比べが利得を膨らませる）は推測のまま。S14 は仕組みを調べず違う問いと違う判定の確かめを足し、603 "Neither result is used to deny or support the other" で緊張を解かずに置く。G5 との関係も整理されていない。
  - 解消の条件: 窓の重なり（か平滑の強さ）を段階的に変えた用量反応の図 1 つ（新しい版として事前に凍結）、または自己相関を制御した合成の系列での比べ。無理なら 307 を仮説と明示し、寄与 (1) を CoAuthor の記号化に限った発見と書き直す。
  - 自信: 中
- [major] S14 の頻度の基準線を表に並べるだけでは足りない
  - 位置と引用: supplement.tex:574 "A frequency baseline collapses the rows ... it is descriptive and has no gate."／604 "no statement is made about the difference between it and the cross-likelihood."／表 585-589
  - なぜ問題か: 0 次の基準線に勝たない指標は遷移の寄与を示さない。差は最大 0.03 で k=1 では基準線が高い。節の見出し "Identification in one-state transition tables" と本文の "in the space of one-state transition tables" は表の数が支えない含みを持つ。
  - 解消の条件: 本文の文で「頻度だけでもほぼ同じに順位づいた」と記述として書く、または main.tex:343 の S14 の説明を "an exploratory ranking check in transition and frequency tables" に変える。
  - 自信: 高
- [minor] 「有意差の検定を使わない」と S14 の p 値・Holm が食い違う（main.tex:177 "All analyses are descriptive: we use no significance tests and no meaningful-difference threshold"／supplement.tex:578 "Nine cells, unadjusted $p$ (Holm-adjusted $p$ alongside, descriptive)"／603 "$p\le0.05$ here"）。解消: 177 を「S14 の探索の確かめを除き」と限る。自信: 高
- [minor] S14 の作り直しが「結果を見た後の 6 つの変更」に入っていない（supplement.tex:572 "The version reported here was designed after seeing that result."／main.tex:177 "Six changes were made after seeing results"）。解消: 「合成の門で止まった初版の作り直しは実データを読む前で 6 つに数えない」と 1 句。自信: 中
- [minor] 「30 倍」は違う共有モデルに対する差どうしの比（main.tex:52・表 2 の 0.188 と 5.5e-4）。解消: 共有 ar3 が共有 hmm3 に勝つ量を 1 つ添え、別の比べであることを 1 句。自信: 中
- [minor] 2 次のチェーンが無く、選んだ値が格子の端（main.tex:328 "Multilevel HMMs and second-order chains were not fitted"）。勧め (1)（316）が「1 次で十分」と読まれる。解消: 勧め (1) に「少なくとも 1 次の」と限定、または 2 次のチェーンを 1 セル報告。自信: 中
- [minor] 造語の密度（143-147, 175, 182, 186）。解消: 造語の小さな表か、本文で使う造語を半分に。自信: 中
- [nit] 題が context-A と原稿で違う。"what remains" の側を勧める。自信: 高
- [nit] CS1 の n_A=2 のセル（supplement.tex:592）は退化。表の注は既にある。本文で触れないままで足りる。自信: 低

## 4. 著者の問いへの答え
1. 足りない（本文の文で 1 句）。2. 確認の主張というより「書き手は安定して違う」手がかりとして読まれる。3. 弱く論点を増やす。深さは窓の重なりと利得の関係の側で出すのが筋。芽は S14 の中にある（弱い縮みで書き手は順位づくのに本人の表は共有の表に勝たない〔605〕）が、凍結した読みではないので使うなら "not prespecified" と明示した考察の 1 段に限る。

## 5. 推奨: major
数値の主張は正直に限られるが、足した 1 文が限定を落とす。深さへの答えが仕組みでなく探索の確かめの追加で、"generalizable insights" への答えが弱い。
