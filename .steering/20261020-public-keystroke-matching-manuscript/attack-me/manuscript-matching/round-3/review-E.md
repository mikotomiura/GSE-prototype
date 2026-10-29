# 編集者 E の応答（round 3・commit c3f3f5b5）

判定: 直してから回す。致命的な欠陥なし。大きな指摘 4 件（書き換え・付録への移動・まとめで消せる）。

## 1. 接地
- E1（CfP）"The core contribution must be relevant to real-world privacy applications. The first page must clearly state how the work is relevant to real-world privacy applications."
- E2（CfP）"Papers that treat privacy as a superficial application domain (e.g., if the only relationship to privacy is a privacy-related dataset) do not demonstrate relevance to real-world privacy problems and are therefore out of scope."
- E3（規程）"appendices should only be used to provide supplementary information that falls outside of the stated contribution of the paper or to provide extended details that would not be of interest to most readers. The paper should be complete and self-contained without appendices."
- E4（規程）"The introduction should give some background and summarize the contributions of the paper at a level appropriate for a non-specialist reader."
- E5（Mensh & Kording 2017, Rule 4）"Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"
- E6（同 Rule 8・Table 1）"The discussion section explains how the results have filled the gap ... and describes how the paper advances the field by providing new opportunities"／"Readers are left with unanswered criticisms and/or questions on their mind."
- E7（同 Rule 7）"the title of the figure should communicate the conclusion of the analysis, and the legend should explain how it was done."
- 注: 投稿先の抜粋は round 1（2026-10-21）に照合済みのもの。この round では取り直せていない。

## 2. 最初の 2 頁から言える 1 文
「文字と数字を q に伏せた実在の公開ログ（Kaggle）は、候補の作文を持つ者に対して 1,000 本の中から全ログを本人の作文に結びつけさせてしまう（100%）。より多くを落とす処理も、照合をほぼ全長だけの水準まで下げたものは、執筆研究の標準の過程指標を相関の中央値 0.70 以下か計算不能にした。キーストロークログを公開する側は、作文そのものを補助情報として扱わなければならない。」
迷った点: 「誰の何のプライバシーが損なわれるか」が抄録に無く序論 4 段落目（introduction.tex:36-39）まで読んで分かる／C2 の言い方が事後の閾値に依る（指摘 2）。

## 3. 指摘
- [major] 1 頁目にプライバシーとの関係（誰が何を失うか）が無い
  - 位置: main.tex:40-51（抄録に privacy・harm・writer の損失の語が無い）・introduction.tex:36-39「The main harm we consider is the link between a processed log and its text for a party that holds the text ... we know of no release in which this has happened and state it only as a consequence」・threat-model.tex:145-146「it does not name the writers' privacy」
  - 理由: 害 (a) が書き手にとっての損失として書かれていない。E2 の「privacy-related dataset だけ」に見える恐れ。E1 は 1 頁目の明示を求める。
  - 解消: 抄録と序論第 1〜2 段落に「書き手が失うもの」を 1 文。ethics.tex:39「What the writers could lose is the link between their writing process, their scores and their texts」を前へ移すのが早い。
  - 自信: 高
- [major] C2 の見出しの主張がデータを見た後の切れ目（0.84）に依る
  - 位置: main.tex:48-50・introduction.tex:45「(a median correlation of 0.84 or more)」・results.tex:145-146・generated/main-1000.tex:14-15（R7(0.1) 70.2 / 0.85、R7(0.25) 14.3 / 0.81）
  - 理由: 0.84 は R7(0.1) と R7(0.25) の間に引いた値に見える。R7(0.25) は 0.81 で 14.3%。計算できない指標を 0 と数える中央値という合成指標にも依る（protocol.tex:116-117）。E6 の unanswered criticisms。
  - 解消: 閾値でなく図 1 の非支配の並びとして述べる、または 0.84 の根拠を書く。R7(0.25) の位置づけを考察で 1 文。
  - 自信: 中
- [major] 12 頁ちょうどの本文に、大半の読者が要らない細部が残る（付録へ移せる）
  - 位置: attackers.tex:29-35（規則の誤差・"Of the 2,381,444 segments ..."）／attackers.tex:48-49（同じコストの選び方）／attackers.tex:116-132（A3 の推定の細部）／attackers.tex:134-140・data.tex:41-44・results.tex:160-162・表の A4 の行（KeyTAR。results.tex:160 "stayed below A0 on every form and $N$"）／protocol.tex:101-105（Inputlog と照合できなかった・discussion.tex:32-33 と重なる）／protocol.tex:170-182（逸脱 4 件の詳細）／protocol.tex:184-188・results.tex:164-171（予測と結果・"a miss does not change the conclusions"）／protocol.tex:152-160・results.tex:186-193・discussion.tex:36-40（探索 5 件）／data.tex:46-51（取得後の点検）
  - 理由: 余白 0 で、指摘 1・2 を直す余地も考察を厚くする余地も無い。E3。
  - 解消: 移して約 1 頁を空け、1 頁目のプライバシーと考察に回す。
  - 自信: 高
- [major] 同じ但し書きと分析の地位の説明が何度も出る
  - 位置: 「上限ではない」main.tex:51・introduction.tex:48・threat-model.tex:191-192・protocol.tex:120-121・results.tex:83・discussion.tex:8・13-14・21・34・63・conclusion.tex:8-9（10 か所超）／「形の差は攻撃者の差も含む」threat-model.tex:174-177・protocol.tex:64-67・results.tex:87-88／「目的の読みは我々のもの」introduction.tex:24-25・threat-model.tex:147-150・results.tex:52／「KLiCKe から取られた」introduction.tex:19-21・threat-model.tex:98-109・discussion.tex:55-57・ethics.tex:25-27・45-55／「害 (b) は例を知らない」introduction.tex:38-39・threat-model.tex:152-153・discussion.tex:13／「KeyTAR は脅威モデルの外」threat-model.tex:139-140・data.tex:41-44・attackers.tex:67-68・137-139・protocol.tex:59・results.tex:19-20・160・discussion.tex:34／「開いた世界の AUC は誤一致率ではない」threat-model.tex:182-184・protocol.tex:137-138／「効用の軸は R0 との一致だけ」protocol.tex:117-120・results.tex:141-142・discussion.tex:33-34／「事前登録して変えていない」introduction.tex:34・protocol.tex:16-21・166-168・185-187／「探索的」protocol.tex:155-160・results.tex:189・discussion.tex:36-40
  - 理由: E5。主張が弱く見え紙面を食う。
  - 解消: §3.5 か §6 の 1 か所にまとめ他は参照。抄録・序論・結論では上限でないことを 1 回ずつ。
  - 自信: 高
- [minor] 考察が公開する側への含意を出し切っていない
  - 位置: discussion.tex:63「The results are material for three choices; each statement holds for the attackers tried, and none recommends a form.」・discussion.tex:52-54「These choices lie outside this evaluation.」
  - 解消: 推奨しないとしても結果から言える最低限の条件を 2〜3 文。差分プライバシー・合成データとの関係を 1 段落。
  - 自信: 中
- [minor] 動機の公開が 1 頁目で自ら弱められている
  - 位置: introduction.tex:19-21「The authors of a public corpus, KLiCKe, told us that the competition data were drawn from that corpus before it was released with its texts; we did not check ...」
  - 解消: 序論では一般の主張だけにし、出どころは §3.3 と ethics の 1 か所に。または 1 文の帰結として置く。
  - 自信: 中
- [minor] 日本語の翻訳ログが抄録の焦点をぼかす
  - 位置: main.tex:50-51・results.tex:173-184
  - 解消: 抄録に数字をつけて位置づける（51.6% 対 7.9%）。本文の節を短く。
  - 自信: 中
- [minor] §7.4 が雑多で、図 1 の caption が結論を言っていない
  - 位置: results.tex:148「\subsection{Windows, the open world and KeyTAR}」・results.tex:124「Matching against the process measures for the main forms ...」
  - 解消: 窓・開いた世界・KeyTAR を分け、図の caption の頭を結論文に。
  - 自信: 中
- [nit] 抄録の退化した区間 main.tex:46「(100.0\%, 95\% interval 100.0 to 100.0)」→ 外す。自信: 低

## 4. 判定: 直してから回す
中心の貢献は明確で範囲に入る。1 頁目に書き手が失うものが無く、C2 が事後の閾値に依る。細部・KeyTAR・予測・探索・繰り返しを移すかまとめれば直す紙面は作れる。

## 5. 読めなかった範囲・注入の疑い
references.bib は開いていない。補足は読んでいない（依頼どおり）。PDF の頁割りは確かめていない。注入の疑い: なし（tex のコメントは著者のメモ）。
