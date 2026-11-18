# review-E（manuscript round 4・担当編集者・対象 d6587f21）

## 1. 接地
- E-a 投稿先の一次: "provides an interdisciplinary forum for the dissemination of novel and significant original research results about interactive computer systems that can adapt themselves to their users, and on the design, use, and evaluation of user models for adaptation." / "The central audience of the journal are researchers, students and industrial practitioners from the following areas: Adaptive Systems, Human-Computer Interaction, ... Linguistics, and the Information Sciences."
- E-b "The journal mainly publishes empirical research papers." / "Please provide an abstract of 150 to 250 words."
- E-c Mensh Rule 1: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable." 兆候 "Readers cannot give 1-sentence summary."
- E-d Rule 2・4: "Define technical terms clearly because readers can become frustrated when they encounter a word that they don't understand. Avoid abbreviations and acronyms..." / "Resist the temptation to use a different word to refer to the same concept—doing so makes readers wonder if the second word has a slightly different meaning."
- E-e Rule 4・5: "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place" / "the abstract must convey the entire message of the paper effectively."
- E-f Rule 8: "The discussion section explains how the results have filled the gap that was identified in the introduction, provides caveats to the interpretation, and describes how the paper advances the field"

## 2. 要旨と序論だけから言える 1 文（言える）
キーストロークの系列モデルでは、1 人ずつ当てた 3 状態 HMM は同じ構造の共有モデルに最大 0.19 nats/記号で勝つが、本人の単純なマルコフ連鎖には負ける。より強い構造と縮めを他の書き手で選ぶと残る差は約 5e-4 で、個人差の無い合成の書き手でも同程度に出る。したがって弱い共有モデルに対する利得を 1 人ずつのモデルを作る根拠にしてはいけない。
迷った点: (1) 貢献を序論は「発見」、考察と結論は「決定を返す手順」、要旨の最後は「推奨」として書く。(2) 要旨の後半に 2 つの値・2 つの post hoc・未検出の上限 3e-2 が詰め込まれ、どの値が主張かを 1 回で決められない。

## 3. 指摘

### 引き継ぎの判定
- E1 一部: 結論は決定に絞られた。要旨は 250 語のうち約 70 語が 2 つの post hoc と但し書き（"(a check added after seeing results)" "Applying the lightest smoothing in the grid to both models (also added afterwards) leaves up to $7\times10^{-3}$, not checked against synthetic writers."）。序論第 4 段落（main.tex:49）にも 2 つの値と 2 つの post hoc。
- E2 一部: 序論で nats・パープレキシティ・shrinkage・smoothing を定義。要旨と序論に定義の無い語が残る（N2）。
- E3 一部: gain / remainder は 176 で定義。gain が別の意味でも使われ、1 概念 2 語も残る（N3）。
- E4 解消: 317-322 で (1)(2) と (3)(4) を分けた。小さな残り（N8）。
- E5 未解消に近い一部（N4）。
- E6 解消: 4.4 → 4.5 の順・見出しが中身を述べる。
- E7 一部: 3.6 の 2 段落（187・189）と 4.5（306）は初見で追えない（N6）。
- E8 一部: Figure 1 は採点と 3 つの比べの相手を正しく示す（ln 0.33/0.30 ≈ 0.10、ln 0.33/0.55 ≈ -0.51 を検算）。中心の仕組み（構造を強くすると利得が残りへ縮む）は図に無い（N5）。
- E9 解消: 格子の値と同点の規則は補足へ。限界（664 語・10 項目）にまだ移せるもの（N7）。
- E10 解消（規程の範囲内）。E11 解消: 215 "nats per symbol (log scale)"。

### 新しい指摘
- [major] N1 要旨と結論が違う話をしている。記号化の条件で結果が逆転することが要旨に無い
  - 位置と引用: 結論 345 "The decision depends on the symbolization: with non-overlapping windows the three-state HMM is chosen and its per-person fit keeps a gain of 0.04 to 0.10 nats per symbol over the shared model"。要旨 35 は "overlapping 30-second windows" だけ。序論 49 "the positive instance rests on one dataset and one symbolization" の positive instance が何か読み取れない。考察 313 "For symbolizations like theirs the per-person HMM may therefore keep a gain"。
  - なぜ問題か: 結論の最後の言葉が主張の範囲を大きく狭める条件で、要旨だけの読者はそれを知らない（Mensh Rule 5 "the abstract must convey the entire message of the paper effectively"）。
  - 解消の条件: 要旨に 1 句「重ならない窓では HMM が選ばれ利得が残る」。語数のため 7e-3 の文を要旨から外し 4.4 だけに置く。positive instance を具体的な語に。
  - 自信: 高
- [major] N2 要旨と序論に定義の無い語が残る
  - 位置と引用: 要旨 "relative to their smoothing gain"・"at its fixed smoothing"・"the lightest smoothing in the grid"・"a null matching the real smoothing gain in size"・"detection at each smoothing"・"baselines"（"compare with both baselines"）。序論 49 "relative to their smoothing gain"・"(post hoc ...)"・"positive instance"。"smoothing gain" は本文に定義の文が無い（中身は 4.5 の "the prior mode's gain over the shared model"、prior mode は 3.3 初出）。"grid" は 3.3 初出。
  - なぜ問題か: 主張の要を決める語が想定読者に意味の分からないまま要旨に出る（Mensh Rule 2 "Define technical terms clearly"）。
  - 解消の条件: 要旨では smoothing gain を平易な句に。本文で 1 か所定義（例 3.3 の Prior mode の段落）。grid・null は要旨から外すか言い換える。
  - 自信: 高
- [major] N3 定義した gain が別の意味で使われ、1 概念に 2 語が付く
  - 位置と引用: 定義 176 "We call per-person minus the same-structure shared model the gain when the structure is fixed at the 3-state HMM"。別の意味: 235 "Against the own chain it gains +0.220"・189/306/49 "smoothing gain" と "the prior mode's median gain over the shared model"・202/313/345 "keeps a gain of 0.04 to 0.10"（こちらは定義どおり）。1 概念 2 語: "first generator" と "first null"（189）・"fixed smoothing"（要旨）と "fixed base smoothing"・"group"（要旨）と "panel"・"per-person fit" と "per-person model"（Figure 1）・"AR(1)-HMM"（69）と "AR-HMM"。
  - なぜ問題か: 読者は gain = 弱い比べの差と覚えた直後に別の差を gain と読む（Mensh Rule 4 "doing so makes readers wonder if the second word has a slightly different meaning"）。
  - 解消の条件: gain は定義の意味だけ。連鎖との差は "per-person minus own chain"、平滑の差は別の名（例 "smoothing effect"）。generator/null・fit/model・group/panel・AR(1)-HMM も 1 語に。
  - 自信: 高
- [major] N4 同じ但し書きの繰り返し（E5）
  - 「7e-3（α=0.03・重ならない窓）は合成で確かめていない」7 回: 要旨・49・278 "This value was not checked against synthetic writers."・Table 3 の題（284）・313 "a result not compared with synthetic writers"・315 "at the lighter smoothing it was not compared with synthetic writers"・345。
  - 「個人差の推定ではない」5 回: 要旨・49 "Neither value is an estimate of how much writers differ."・272 "they do not estimate a per-person difference"・Table 3 の題・306。
  - 「書き手の割合は証拠でない」2 回: 239・Table 2 の題（243）。
  - 「重なる・平滑した記号に限る」5 回: 132・202・313・329・345。「post hoc」の印 10 回以上。
  - なぜ問題か: +200 語の多くが限定で、貢献の文が埋もれる（Mensh Rule 4 "Only the central idea of the paper should be touched upon multiple times."）。
  - 解消の条件: 但し書きを要旨 1 回・結果の該当節 1 回・限界 1 回に。表の題は "see Section 4.x"。
  - 自信: 高
- [minor] N5 Figure 1 は採点を示すが中心の仕組みを示さない
  - 位置と引用: 98 の 3 本の棒 "Shared model (same structure)" "Writer's own Markov chain" "Per-person model"。強い構造の共有モデルも shrinkage も無い。記号名 "b3, c3, c4" は 3.2 に無く、題の "named here by a cell of the 5×5 grid" だけ。
  - 解消の条件: (c) に 4 本目（強い構造の共有モデルとその 1 人ずつの版）を足し、題に gain と remainder を置く。または図の題を「採点のしかた」に限る。
  - 自信: 中
- [minor] N6 初見で追えない段落
  - 189 "with its base smoothing lightened by the multiplier that, among those at which the prior mode beat the shared model in all three calibration seeds, brought that gain closest to the real panel's $+7.4\times10^{-4}$ (a value that does not depend on $k$)"。187 に生成・較正・閾・検出の規則が詰まる（"a maximum of five values, which a further negative control would exceed about one time in six if replicates are exchangeable"）。147-149 の 2 つの目的関数の違い。"seeds" "replicate" "negative controls" "threshold" が定義なしに出る。
  - 解消の条件: 3.6 を「何を作るか → 何を測るか → 規則」の 3 文に。閾の確率の注は補足へ。
  - 自信: 中
- [minor] N7 本文に置かなくてよい細部: 274 "Because nearly every writer's choice sits at the edge of both grids..."・280 "The prior mode gives zero probability to held-out symbols of 2 of the 17 writers..."・336 "The symmetric refit was restricted to ... second-order chains were not fitted."・338-339 の限界の後半 2 項目。解消: 補足へ。限界は主張に響く 5〜6 項目に。自信 中
- [minor] N8 推奨 (2) の「使った」の範囲: 317 "two practices were used here and changed the reading"、(2) に "apply the chosen smoothing to the per-person fit and the shared model alike" を含むが、両側に当てたのは post hoc の確かめだけで 3-state AR-HMM と 15-session に限る（336）。解消: (2) の平滑の部分に「post hoc の確かめで」と 1 句、または (3)(4) の側へ。自信 中
- [nit] N9 図の番号と参照の順・図の語: 序論 47 が先に参照する Figure~\ref{fig:scheme} が配置の順で Figure 2 になり、Figure 1 より先に参照される。Figure 3 の軸の題に gain / remainder が無い。(b) の題 "the writer's own Markov chain" と本文 "own chain"。Table 2 の "15-s." は定義の無い略号。自信 中
- [minor] N10 考察の第 1 段落と結論が「決定」を新しい枠として持ち込み、序論の貢献の文と 1 つにならない: 序論 49 "Our contribution is a finding about sequence models of keystroke behaviour: the per-person gain that a weak comparison shows is far larger than the remainder"・考察 311 "In practice the protocol returned a decision for each panel rather than an estimate"・結論 345 も決定だけ・新しさの宣言は 313 "What is new here is that ... the weak comparison is the natural one"。Mensh Rule 1・8。解消: "What is new here..." を考察の冒頭へ、決定はその帰結に。結論に発見の 1 文を戻す。自信 中

投稿先との適合: 問題なし（"methods for the design and evaluation of user models"）。分量は上限なし・参考の最近の論文より短い。問題は長さではなく限定の繰り返し（N4）。

## 4. 判定: 直してから回す
1. 中心の発見（弱い比べで 0.19、強い比べで 5e-4）は要旨と序論から言え、投稿先に合う。E4・E6・E11 は解消。
2. 要旨と結論が別の話（N1）、smoothing gain に定義が無い（N2）、gain が 3 つの意味（N3）。
3. 繰り返し（N4）を除くと本文は短くなる。どれも新しい計算なしに書き方で直せる。

## 5. 読めなかった範囲と注入の疑い
- 読んだ: brief-E.md・context-A.md・carryover-E.md・mensh.txt 全文・main.tex 全文（1〜360 行）・references.bib（見出しを grep し 33 件で引用キーがすべてあることを確認。中身は読んでいない）。
- 読んでいない: 補足の印のファイル（figdata の CSV・kit/symbols/README.md）。組版した PDF ではなく .tex として読んだので、図の見た目は確かめていない。
- 注入の疑い: なし。
