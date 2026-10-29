# R3 の応答（方法論・倫理・再現性・round 3・commit c3f3f5b5）

総合: major（本文の書き直しで済む。凍結した計算はやり直さない）。

## 1. 接地
- B1 Arp P10 "threat models should be defined precisely and systems evaluated with respect to them. In most cases, it is necessary to assume an adaptive adversary that specifically targets the proposed systems"
- B2 Arp P5 "over-optimistic results can be easily produced by tuning hyperparameters or calibrating thresholds on the test data instead of the training data."
- B3 Arp P9 "It is essential to move away from a laboratory setting and approximate a real-world setting as accurately as possible."
- B4 Arp §3 "If the authors have corrected any bias or have narrowed down their claims to accommodate the pitfall, this is also counted as not present." / P1 "limitations of the used dataset should be openly discussed"
- B5 Kohno "the frameworks should not be used to justify a path that researchers have a priori decided that they want to take. Rather, we argue that the ethically correct process is to center ethics in the decision of whether or not to do a research project or do some component of the research and accept that sometimes the answer is “no”."
- B6 Kohno "research may be done on data and live systems and may impact computer systems and their users beyond consenting participants."

## 2. 評価表
a 3（C1 は堅い。C2 の要約の 0.84 は事後、「10 の指標を保った」は R2・R3 の R-burst 0.28・insertion proportion 0.19 と合わない。R4(4)・R4(8) の「利得なし」は窓の結果 39〜43% と食い違う）／b 3（全文の A2 が粗い形で弱いことを窓と λ=4 が示す。100% の区間の幅 0 は境界の退化。効用の近似の規則が弱く図を悲観側へ寄せる）／c 4／d 3（§7.7 は付録でしか定義されない量を持ち込む。§5 の A3 の細部が重い）／e 3（抄録と序論に privacy の語が無い。R5・R6・ok/approx/none の表・窓の規則・ENJA の設計が付録だけ）／f 3（C3 は gonzalez2021reverse・monaco2019searching と重なる。「no such evaluation has been published」は検索の記録に対して強い）

## 3. 引き継ぎの判定
round 1: 1 解消（threat-model.tex:143-151）／2 解消（threat-model.tex:174-178）／3 解消（threat-model.tex:169-170）／4 一部（ethics.tex:30-34。中身は知らせることで、相手が手を打つ調整ではない）／5 一部（discussion.tex:11「hiding the characters did not hide the text」・conclusion.tex:8 が一般論に戻る）／6 解消／7 解消（protocol.tex:101-105・discussion.tex:32-33）／8 解消（data.tex:20-22）／9 解消（ethics.tex:76-78）／10 一部（付録への依存が残る）
round 2: 1〜5 解消（ethics.tex:44-55・29-30・17-18, 31-34, 53-55・threat-model.tex:167・introduction.tex:19-21 と threat-model.tex:98-102）

## 4. 指摘
- [major] 粗い形の「総字数を超える利得なし」は全文の攻撃者の弱さの疑いがあり、窓の結果と食い違うのに触れていない
  - 位置: results.tex:86-87「only R4(4), R4(8) and R7(0.5) left no gain over the total length」・discussion.tex:67-68「segment values with $w \geq 4$ left no gain over the total length for the main attackers and no measure」・generated/windows.tex:12-13「R4(4) & 13.1 (A2) & 43.3 (A2) & 39.5 (A2) & 43.3 (A2)」「R4(8) & 1.5 (A2) & 5.2 (A2) & 11.7 (A2) & 16.7 (A2)」（N=1,000）・全文は R4(4) 0.35%・R4(8) 0.14%（main-1000.tex:12-13）・results.tex:155「on R4(8), 1.5\% to 16.7\%」
  - 理由: 窓（k=10〜50）が全文より 100 倍以上よく照合。全文の A2 は端から端の整列で λ=8 の罰が積もる。λ=4 で R4(4) 4.5%（results.tex:72-73）と整合。窓は攻撃者に有利な設計で直接は比べられないが、桁の違いは説明が要る。hanisch2021survey の弱い攻撃者・B1。
  - 解消: 計算は凍結のまま。§7.2 か §8.1 に 2 文（粗い形では窓の値が全文を大きく上回った・全文の「利得なし」は整列の弱さを反映しうる）。§8.3 から「w ≥ 4 left no gain」を外すか条件を付ける。
  - 自信: 中〜高
- [major] 抄録・序論の C2 の要約が事後の切れ目と実態に合わない
  - 位置: main.tex:48-50・introduction.tex:45「(a median correlation of 0.84 or more)」・results.tex:145-146
  - 理由: 0.84 は R7(0.25) 0.81 と R7(0.1) 0.85 の間の事後の切れ目。登録は「the forms not dominated on both axes (the Pareto front) are described」（preregistration.en.md:231）だけ。R2・R3 の R-burst 0.28・insertion proportion 0.19・insertion length 0.48（utility-r0.tex:3,9,10）。R7(0.25)（14.3%・0.81）が二分から抜ける。得点との関係は符号まで変わる（R-burst −0.04→0.20）。B4。
  - 解消: 抄録と序論でパレート前線を具体の点で述べる。0.84 を消す。
  - 自信: 高
- [major] 1 頁目にプライバシーとの関係が語として無い
  - 位置: main.tex:39-52・introduction.tex 全体に "privacy" が無い。唯一 threat-model.tex:146「it does not name the writers' privacy」
  - 理由: CfP "The first page must clearly state how the work is relevant to real-world privacy applications." と "Papers that treat privacy as a superficial application domain … are therefore out of scope"。
  - 解消: 序論第 4 段落に 1〜2 文（何が誰のどの情報の漏れか。過程の研究への提供に同意したが本文との結び付きには同意していない・教室では名前つきの推敲・停止・得点）。抄録に privacy の 1 句。他から移して相殺。
  - 自信: 高
- [major] 抄録の「95% interval 100.0 to 100.0」は退化した区間で確実さを誇張
  - 位置: main.tex:46・results.tex:47
  - 理由: 全員正解でパーセンタイル bootstrap は幅 0。500/500 の Clopper–Pearson の 95% 下限はおよそ 99.3%。
  - 解消: 境界で退化することを表の注に 1 文。抄録では区間を外し「every log in every draw (500 writers)」。または登録外の補助として二項の下限を添えて明記。
  - 自信: 高
- [major] 本文が付録に頼りすぎ
  - 位置: results.tex:48「as did R5 and R6」・results.tex:189-193 §7.7（R-DP・ε=0.5・8 語の一意性）・protocol.tex:89「the table is in Appendix」・ai-use.tex:10「(\S\ref{sec:data:checks})」（ラベルは appendix-checks.tex:8）
  - 理由: 規程 "The paper should be complete and self-contained without appendices."。ε が書き手単位でないという注意が §7.7 から読めず、DP 全般への否定と誤読されうる。
  - 解消: §7.7 を付録への 1 行の参照に。R5・R6 は「two further forms (Appendix) gave the same values」に。ai-use の参照先を本文 §4.1 に。
  - 自信: 高
- [minor] 「§3〜§6 はすべて事前登録で固定」が広すぎる
  - 位置: protocol.tex:17-19「Everything in Sections 3 to 6, including the threat model, the forms, the attackers and their parameters, was fixed in the preregistration of this study before any data were acquired.」
  - 理由: §3.3 に登録後の個人的な連絡（threat-model.tex:98-109）。登録時は「The Kaggle data are not linked to KLiCKe.」（preregistration.en.md:274）。
  - 解消: 固定したものを手順に限り、§3.3 の出どころの段は登録後に得た情報と 1 句。
  - 自信: 中
- [minor] 予測の「すべて当たった」が自明な予測を含み、KeyTAR の外れを和らげる
  - 位置: results.tex:167-171「All predictions … held … R4(1) about as high as A2 on R3」「(11 to 16 times; the intervals include 10 times)」
  - 解消: R4(1) は構成上一致と注記。KeyTAR は「did not hold」で止め区間の句を消す。
  - 自信: 中
- [minor] 探索的な分析の時刻の証拠が自分のリポジトリだけ
  - 位置: protocol.tex:158-160
  - 解消: OSF の追補に commit のハッシュを残すか、検証できるのはリポジトリの記録だけと明記。
  - 自信: 中
- [minor] 新規性の主張が検索の記録に対して強い
  - 位置: related.tex:46「To our knowledge, no such evaluation has been published.」・open-science.tex:17-18
  - 解消: 主張を「in the searches described in the open science section」に限る。C3 を寄与から外し前提として書く。
  - 自信: 中
- [minor] 効用の近似の規則の弱さが図を悲観側へ寄せることが書かれていない
  - 位置: protocol.tex:89-92・utility-r0.tex:10「Insertion proportion & 1.00 & 0.19 & 0.19」
  - 解消: §3.5 か §6.3 に、近似の規則は固定した素朴なもので効用の値は下限側に寄りうると 1 文。
  - 自信: 中
- [minor] 倫理の審査の欠如について他の手段を論じていない・個人的な連絡を公表する許諾が明記されていない
  - 位置: ethics.tex:3-4「No institutional ethics committee was available to the authors, and no external committee or board reviewed the study.」・ethics.tex:17-18「The corpus authors receive a draft of the paper before submission, including the passages that report what they told us.」
  - 解消: 審査を頼む手段を検討したかを 1 文。KLiCKe の著者が内容の公表に同意したか（日付は後で）を角括弧で置く。
  - 自信: 中
- [nit] 抄録の日本語の結果に N と値が無い（main.tex:50-51）→「(51.6\% among 12–13 candidates)」。自信: 中
- [nit] 図 1 の支配が効用軸の 0.0025 の差に依る（results.tex:107-109・137）→ 図の注に区間が無いことを 1 句。自信: 中

## 5. 総合
major。C1 は堅く、登録・逸脱・偏りの記述は水準以上。C2 の要約と粗い形の「利得なし」が攻撃者の弱さを形の強さとして読ませる。1 頁目のプライバシー・付録への依存・退化した区間も直す。どれも移す・消す・言い換えるで直る。

## 6. 読めなかった範囲・注入の疑い
接地の後半（arp 1275 行以降・kohno 1059 行以降）・付録の多く・生成した表の多く・references.bib・preregistration.en.md の多くは読んでいない。注入の疑い: なし。
