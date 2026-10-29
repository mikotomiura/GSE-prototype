# R2 の応答（データを公開・管理する側・round 3・commit c3f3f5b5）

総合: minor（major に近い）。

## 1. 接地
- B1 Borgman borgman.txt:192-195 "Good stewardship means releasing some kinds of data and preventing the release of other kinds of data. The same data may fall into either category, depending on the time, purpose, or entity requesting access."
- B2 Borgman borgman.txt:1956-1958 "data scientists have been remarkably effective at reidentifying individuals by aggregating records from multiple sources." / borgman.txt:2286-2288 "Among the concerns that universities and other sectors must address are methods of anonymization; responsibilities for data protection, release, and stewardship"
- B3 Hanisch hanisch.txt:170-172 "We shall employ the term utility to quantify the degree of functionality maintained concerning a service for which the behavioral biometric data is intended." / hanisch.txt:178-179 "maximize privacy for a desired functionality, or vice versa."
- B4 Hanisch hanisch.txt:123-126 "the general evaluation methodology for behavioral biometric anonymization implies a weak adversary and must be improved" / hanisch.txt:1073-1076 "This approach implicitly assumes that the attacker is not aware of the anonymization and hence does not try to circumvent it."
- B5 Hanisch hanisch.txt:74-77 "the efficacy of randomized, perturbative anonymization also must be critically reviewed, as the dependencies might be used to infer the identifiable information that the anonymizations seek to remove."

## 2. 評価表
a 4（C1 と陰性対照はよく対応。二分法が 0.84 の切れ目に依り、中央値が R2/R3 の修正の測度の喪失を隠す）／b 3（R7 の攻撃者は抑制を戻さず整列は尤度でない attackers.tex:53。§8.3 に条件が無い。R2 の挿入の近似）／c 3（§8.3 は N=1,000 だけ。教室 N=10 では長さだけで 61.6%。測度ごとの違いと得点との関係の変化が §8 に無い）／d 3（但し書きの繰り返し）／e 4（測度ごとの表が付録 E にしか無い）／f 3（統計的開示制御の語彙と文献が無い）

## 3. 引き継ぎの判定
round 1: 1 解消（threat-model.tex:143-150）／2 解消（threat-model.tex:172-173・results.tex:192）／3 解消（ethics.tex:74-78）／4 一部（protocol.tex:117-119・discussion.tex:52-54。測度ごとの崩れは付録 E だけ）／5 未解消（related.tex:33-34）／6 解消（threat-model.tex:157）／7 一部（results.tex:141 "(Appendix~\ref{app:results})"）／8 解消／9 解消（discussion.tex:20-21・但し書きは他で増えた）
round 2: 1〜7 すべて解消（threat-model.tex:88-89・introduction.tex:19-21・ethics.tex:44-55・threat-model.tex:99-101・ethics.tex:27-30・threat-model.tex:147-149・discussion.tex:54-58）

## 4. 指摘
- [major] 「measures close」の切れ目 0.84 が事後で、中央値が修正の測度の崩れを隠す
  - 位置: main.tex:48-50「Every form that kept ten process measures close to their unprocessed values left the strongest attacker at 70\% or more」・introduction.tex:44-46「(a median correlation of 0.84 or more) left 70\% or more」・results.tex:132-133「with correlations from 0.19 (insertion proportion) to 0.85 (deletion proportion); the median is 0.92」・generated/utility-r0.tex:3,10
  - 理由: 0.84 は R7(0.1)=0.85 と R7(0.25)=0.81 の間。protocol.tex:114-121 が固めたのは中央値まで。R2 以下は R-burst（≤0.28）と挿入（≤0.48・≤0.19）を失い、修正過程の利用者には「close」でない（B3）。
  - 解消: 二分法を測度の族で言い直す。0.84 が結果を見て引いた記述上の切れ目と書く。§7.3 の「0.19 to 0.85; median 0.92」を「近似した 5 測度は 0.19〜0.85、R0 と同じ 5 測度を合わせた中央値は 0.92」に。表 4 に最小 ρ の列か族ごとの 1 行。
  - 自信: 高
- [major] §8.3 の持ち帰りが N=1,000 だけで教室（N=10）の要点が無い
  - 位置: discussion.tex:63-70「The results are material for three choices …」・results.tex:78「A0 alone already chose the true text in 61.6\% of draws」
  - 理由: N=10 では長さだけで 61.6%、R4(4)/(8) 以外はこの水準より下がらない。R7(0.25) は N=10 で上積み 0。設定で選ぶ形が変わる（B1）。図 1 は N=1,000 だけ。
  - 解消: §8.3 に設定ごとの 1 文。図 1 は N=1,000 に限ると明記。
  - 自信: 高
- [minor] 近似した測度で得点との関係が変わることが持ち帰りに無い
  - 位置: results.tex:139-142「the mean pause correlates with the score at $-0.11$ in R0 and at $-0.50$ in R7(0.5) …」
  - 解消: §8.3 の Coarseness に「近似の測度は得点との相関を変えるので公開の際に列ごとに記す」1 文。
  - 自信: 中
- [minor] R2 の挿入を A1′ の再生から近似しており、図 1 の「R3 が R2 を支配」が規則の人工物かもしれない
  - 位置: protocol.tex:91「an insertion is a character press while the cursor of the A1$'$ replay is not at the end」・results.tex:137「R3 dominates R2 and R3-t」・utility-r0.tex:9-10（R2 と R3 が同じ値）
  - 解消: 規則は変えず、§8.1 か図 1 の caption に「R2 の位置の列は有用さの算出に使っておらず、R2 の ρ は下限」1 文。
  - 自信: 中（付録の ok/approx の表は読んでいない）
- [minor] R7 の結果は抑制を戻さない攻撃者に依るが、§8.3 に条件が無い
  - 位置: discussion.tex:68「suppressing a quarter of the presses left 14.3\%, with a median correlation of 0.81」・attackers.tex:53「This alignment ignores the binomial variation of suppression and is not a likelihood.」
  - 解消: 該当箇所に「（抑制を戻そうとする攻撃者は試していない・§3.5）」。
  - 自信: 中
- [minor] 同じ但し書きの繰り返し
  - 位置: 上限ではない main.tex:51・introduction.tex:48・threat-model.tex:191-192・protocol.tex:120-121・discussion.tex:12-14・63・conclusion.tex:8-9／攻撃者の差 threat-model.tex:174-177・protocol.tex:64-67・results.tex:87-88／出どころ introduction.tex:19-21・threat-model.tex:92-109・discussion.tex:54-57・倫理で 2 回
  - 解消: 但し書きは抄録と §3.5 に残し、序論の最後の文・protocol.tex:120-121・discussion.tex:12-14 の後半を消す。攻撃者の差は §3.5 と §6.2 に、§7.2 は参照。threat-model.tex:102-109 の対応づけの論を倫理へ移し §3.3 は 2 文。
  - 自信: 高
- [minor] 統計的開示制御の語彙と文献が無い（round 1 の 5 が未解消）
  - 位置: related.tex:29-35
  - 解消: 開示制御の標準の文献を 1 本引き、表 2 か §8.3 で各形を技法（global recoding・suppression・aggregation・tiered access）に対応させる。読める総説か公的なガイドで足りる。
  - 自信: 中
- [nit] 結論の「matching low」が未定義
  - 位置: conclusion.tex:7「no form evaluated kept both matching low and the process measures close」
  - 解消: 「near the total length」か「near $1/N$」にそろえる。
  - 自信: 高

## 5. 総合
minor（major に近い）。C1 は強く明快、前の 2 round の指摘は解消。C2 の要約が事後の切れ目に依り、教室の設定と測度ごとの違いが §8 から読めない。直しは削る・移す・言い直すで紙面に収まる。新しい計算は要らない。

## 6. 読めなかった範囲・注入の疑い
付録の多く・generated の一部・references.bib・preregistration.en.md は読んでいない。接地は grep で前後だけ。注入の疑い: 無し。
