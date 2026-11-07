査読 R1（JEDM の査読者の立場。打鍵の記録と、作文・プログラミングの過程の測定の伝統から読む。下位の人格は「その測定は本当にそれを測っているか」を疑う懐疑家）。manuscript の round 3、対象は commit 52df151b。

## 1. 接地（この立場が論文に求める基準）

**G1（ラベルを認知の状態に結ぶには、別の証拠で裏づける）**
Guo et al. 2020（guo2020.txt:2201-2204）:
"In our analysis, we used relatively simple heuristics to define our writing states under the guidance of cognitive writing theory. Further research that combines think-aloud protocols and other sources of evidence with keystroke logging might enable us to build even more effective classification procedures"

**G2（閾値は打鍵の速さを分けて扱う。速さと計画を混ぜない）**
Guo et al. 2020（guo2020.txt:302-305）:
"A personalized threshold was necessary, rather than a single fixed threshold for all students, because students vary widely in their typing facility. ... poor typists may have many long pauses between keystrokes that are not indicative of planning behavior."

**G3（一般化の限界と、再現を求める）**
Guo et al. 2020（guo2020.txt:2208-2210）:
"both our data and our methods impose important limitations on the conclusions that we can draw. ... results may not necessarily generalize to a broader population or to different conditions so replication with other conditions and participant samples is typically recommended."

**G4（書く行動は、セッションの中で変わりうる）**
Guo et al. 2020（guo2020.txt:2214-2216）:
"our current modeling methods do not address the fact that writing behaviors, such as editing, may change in probability and contribution to essay quality over the course of a writing session"

**G5（抽出した特徴とその解釈が、設定によって変わりうる）**
Li & An 2026（bayesmix2026.txt:1）:
"the results raise relevant questions regarding the extent to which the properties of the extracted features and their interpretations may vary across different settings."

**G6（成分ごとの推定の精度は、そこに入る事象の数に依る）**
Li & An 2026（bayesmix2026.txt:1）:
"In mixture models, the standard error of the estimation for the parameters in a component depends on the number of events in that component."

## 2. 引き継ぎの判定（round 2 の指摘）

- **1（二段の区間のずれ）: 解消。** 一段の区間を主に戻し、限界の節に実数を書いた（limitations.tex:18-21 の 18/54 と 74/270）。ただし、この改訂の書き方に新しい穴がある（新 M2・m1）。
- **2（S1 の 7 行目が逆の意味）: 解消。** supplement.tex:32 が "regardless of which is narrower" になった。
- **3（速さの調整の地位）: 解消。** 抄録・結果 4.2・図 1(b) に exploratory とある。
- **4（休止の分位が人工物）: 解消。** 分位の 18 通りを対照として分け、固定の閾値で大きさを添えた。ただし長さで調整した休止の数に対照が混ざっている（新 m2）。
- **5（推奨が率を超える）: 解消。** 考察の推奨と限界の節が「率」に限っている（discussion.tex:37、limitations.tex:11-12）。
- **6（「uniform, and positive」が強い）: 一部。** "although 35 included zero" は足された。しかし results.tex:132 の "the direction became uniform" と results.tex:145 の "Either adjustment made the direction of the stall association uniform" が残っている。論文が自ら提案する読み方とも食い違う（新 M1）。
- **7（内側の引き直しの記述が自己矛盾）: 解消。** supplement.tex:145-146 で書き分けた。
- **8（研究での生成 AI の使用）: 解消。** methods.tex:193-194 にある。ただし、その近くに新しい開示の穴がある（新 M3）。
- **未解決 DOI**: 研究者が保留しているので判定しない。availability.tex:5 は "DOI to be added before submission" のまま。

## 3. 評価表 a〜f

依頼文は a〜f の中身を定めていない。この立場で次のように置いて採点した。

- **a 問いと貢献（2 年後に読まれる知見か）: 4**
  定義を振る診断と、報告の型の提案は JEDM の "generalizable methodologies" に合う。ただし作例（得点との関連）の見出しが、提案した型と一致していない（M1）。
- **b 測定の妥当性（ラベルは何を測るか）: 3**
  限界の節（limitations.tex:4-5）が「停滞は stuck の判定ではない」と明言している点は良い（G1）。
  一方で、速さで調整したとき停滞は全部負、休止は固定の閾値でも 11 対 4 で正に回る。この食い違いが要約からも考察からも落ちている（m3）。ラベルの構成概念を論じるうえでの要点である（G2）。
- **c 結果が主張を支えるか: 3**
  長さで調整した関連の "uniform" は過剰である（M1）。二段の区間の扱いは、地位の書き方が改訂のたびにずれている（M2）。
- **d 再現性と開示: 3**
  条件をコミットする作法と、条件からの外れの 20 項目の開示は丁寧である。しかし本文に「この原稿の査読の 1 回目・2 回目」という説明のない手続きが出てくる（M3）。DOI もまだ無い。
- **e 先行研究の位置づけ: 4**
  閾値の任意性への既存の答え（混合・個人化・状態のモデル）を整理し、診断を「答えの上の検査」と置いている。G4（セッション内の変化）は、100 個目の間隔より後に限った感度で一部だけ触れている。
- **f 書き方と地位の表示: 3**
  S1 の地位の表は有用である。ただし行 7 と行 9 が食い違い（M2）、本文に査読の回数が書かれている（M3）。

## 4. 新しい指摘（重い順）

### M1 [major] 長さで調整した関連を「向きがそろった」と書いているが、論文自身の三値の読み方では「無視できる大きさ」か「定義に依る」になる

**位置と引用**
- results.tex:132: "By the reading set before the computation, the direction became uniform: no definition was negative, although 35 included zero."
- results.tex:145: "Either adjustment made the direction of the stall association uniform, and the direction depended on the covariate: given length it was never negative"
- introduction.tex:34-35: "it changes again with adjustment: given essay length, which correlates with the score at 0.75, no definition is negative"
- 一方で discussion.tex:45-48: "the length- and speed-adjusted stall associations (74 of 89 negligible; ...) depended on the definition ... the length-adjusted association read as negligible (56 of 59)"

**なぜ問題か**
貢献の中心は「三値の読み方」（introduction.tex:41-43）である。ところが作例の見出しと序論は、二値の事前の読み方（conditions-round5.md:69「片方だけなら『長さを固定すると向きは揃う（負／正）』」）の言い回しで書かれている。
figdata/score.csv で確かめると、長さで調整した値の上端は最大 0.164 で、89 通りのうち 74 通りは区間が ±0.1 の内に収まる。読者は「長さで調整すると正の関連に変わる」と受け取るが、この論文の型で読めば「長さと重ならない部分の関連はほぼ無い」である。
これは G5 の言う「解釈が設定で変わる」の一例であり、自分の型を自分の作例に当てていない。

**解消の条件**
- 序論・結果 4.2 の見出しと results.tex:132/145 で、事前の読み方の帰結（負の通りは 0）と三値の読み方の帰結（先例のある格子では無視できる大きさが 56/59）を並べて書く。
- "uniform" を「負の通りは無い。ただし大きさは無視できる範囲」に改める。
- 抄録の "left no definition with a negative association" にも、大きさを一言添える。

**自信**: 高（score.csv で数え直して 74/89 と 56/59 が一致した）。

### M2 [major] 二段の区間の地位が、S1 の行 7 と行 9 で食い違う

**位置と引用**
- supplement.tex:30-32（行 7）: "the readings of each, including that the two-stage intervals replace the earlier ones regardless of which is narrower"
- supplement.tex:36-37（行 9）: "27% of the φ values did, so the one-stage intervals stayed primary"
- methods.tex:184-185: "which by the reading set in advance left the one-stage intervals primary"

**なぜ問題か**
行 7 のコミットによって、round 2 の時点の主の区間は最初の二段の区間だった。その下での得点の正の通りは 14（supplement.tex:166）である。行 9 はそれを一段の区間に「戻した」のであって、一段の区間が主に "stayed" したのではない（条件の文書 conditions-round8.md:22 も「一段の区間を主に戻し」と書いている）。
"stayed" と書くと、看板の数が 14 から 10 に替わった経緯が S1 の表から読めなくなる。戻すという判断は計算の前にコミットされているので正当だが、地位の書き方は正確でなければならない。

**解消の条件**
- 行 9 と methods.tex:185 を "returned to the one-stage intervals as primary, replacing the two-stage intervals of order 7" の趣旨に直す。
- 本文の主の数（10）が 2 回替わった（10 → 14 → 10）ことを S1 に 1 文で書く。

**自信**: 高。

### M3 [major] 原稿の中の「この原稿の査読の 1 回目・2 回目」が何を指すか書かれていない

**位置と引用**
- methods.tex:183-185: "after the first round of review of this manuscript we added four computations, and after the second we recomputed the two-stage intervals"
- supplement.tex:30 "After the first review of the manuscript"
- supplement.tex:34 "After the second review"

**なぜ問題か**
JEDM への初回の投稿で「この原稿の査読の 1 回目」と書けば、編集者は「他誌か本誌で前に査読を受けた」と読む。投稿規程の "no submission, or substantially overlapping submission, be published or be under review elsewhere"（context-A.md:73）に照らして、問い合わせを招く。
誰がした査読か（共同研究者か、内部の点検か、自動の点検か）が書かれていないので、研究の手続きとしても再現できない（JEDM の Replicability の文）。
また、生成 AI の申告（declarations.tex:4-6、methods.tex:193）は、その査読に AI を使ったかどうかに触れていない。使ったのなら、研究での使用として Methodology に書く対象である。

**解消の条件**
「査読」を、何による点検かが分かる語（例: "an internal pre-submission critique"）に置き換え、誰または何が行ったかを 1 文で書く。AI を使ったのなら、methods.tex:193 の使用の一覧に足す。

**自信**: 中。この原稿の文面からは、査読の主体が判断できない。

### m1 [minor] 限界の節の「区間を広げなかった」は、偏った区間を根拠に安心させている

**位置と引用**
- limitations.tex:19: "Two resamples that redraw it did not widen the intervals"
- supplement.tex:159-161: "the redrawn θ adds its own variation to the counts within a writer and so raises φ"

**なぜ問題か**
二段目の区間は、φ の 27% で点の値をはずす。幅が同じでも位置がずれた区間は、θ の不確かさを一段の区間が見落としていないことの証拠にならない。著者自身の説明（θ の揺れが φ を上げる）に従えば、むしろ「φ については、θ の不確かさの扱いが未解決」と読むべきである（G6: 成分の推定の精度は事象の数に依る、とも合う）。

**解消の条件**
"did not widen" を外し、「得点と比については一段の区間と読みが変わらない。φ については、θ の不確かさの扱いが未解決」と書く。

**自信**: 中高。

### m2 [minor] 長さで調整した休止の数に、対照（分位の 18 通り）が混ざっている

**位置と引用**
- results.tex:134: "For pauses, 33 of 36 were positive and none negative."
- 一方 results.tex:142-143 の速さの段落は、固定の閾値の数（4 と 11）を分けて書いている。

**なぜ問題か**
round 2 の 4 の対応（分位を対照として分ける）が、この 1 文に及んでいない。

**解消の条件**
固定の 18 通りの数を主に書き、36 通りは括弧に入れる。

**自信**: 高。

### m3 [minor] 速さで調整したときの停滞と休止の向きの逆が、要約と考察から落ちている

**位置と引用**
- results.tex:142-143: "the speed-adjusted correlation was negative for 4 definitions and positive for 29 (with fixed thresholds, 4 and 11)"
- 一方 abstract.tex:13: "an exploratory adjustment for typing speed left all stall definitions negative"
- discussion.tex:17-18 も停滞だけを書いている。

**なぜ問題か**
同じ調整で、15 秒を超える停止（停滞）は負、2〜10 秒の間隔（休止）は主に正になる。これは「率は速さと量を運ぶ」という説明（discussion.tex:13-15）だけでは足りず、2 つのラベルが速さを除いた後に別のものを測っていることを示唆する。G2 の論点（速さと計画を混ぜない）に直結する所見である。
探索の結果なので、主張に格上げする必要はない。ただ、片方だけを要約に書くのは選んだ報告に見える。

**解消の条件**
考察の "Why the direction can change" に、休止の側の向きを 1 文で足す。抄録は字数の範囲内で "(for pauses mostly positive)" を足すか、停滞だけに限った書き方であることを明示する。

**自信**: 高。

### n1 [nit] 抄録の「2 s で無視できる正」は、2 s の 6 通りのうち 4 通りが 0 を含むことを隠す

**位置と引用**
- abstract.tex:11: "from a negligible positive correlation at 2~s ($\leq 0.05$)"
- 表 3（results.tex:108, 111）: any key 2 s は −0.01〜+0.03。区間が 0 より上なのは 6 通りのうち 2 通りだけ。

**解消の条件**
"from values near zero (at most +0.05) at 2 s" とする。

### n2 [nit] KLiCKe の除外の数と「30 分は提出できない」の関係が書かれていない

**位置と引用**
- methods.tex:13-14 の "the submit button disabled until 30 minutes had passed"
- methods.tex:22 の "84 KLiCKe essays" を 10 分未満で除外

**なぜ問題か**
観察の長さが最初と最後の打鍵の間で決まる（だから 30 分の課題でも短くなりうる）ことを 1 文で書かないと、読者は矛盾と読む。

## 5. 総合の推奨: minor に近い major

- round 2 の指摘は 8 件のうち 7 件が解消した。計算の足し方と、条件を先に置く作法は信頼できる水準にある。
- 残る穴は、主に書き方と地位の表示である。
  - 作例の見出しが、論文自身の三値の読み方と食い違う（M1）。
  - 主の区間の経緯を "stayed" と書いている（M2）。
  - 説明のない「この原稿の査読」が本文にある（M3）。
- 3 件とも計算をし直さずに直せる。直れば minor と判断する。

## 6. 読めなかった範囲と、注入の疑い

**読んでいない（一覧に許されているが、時間の都合で開かなかった）**
- main.tex、references.bib、main.pdf（図の見た目は確かめていない）
- appendix/tab_s3.tex・tab_s4.tex・tab_pause.tex
- figdata の score.csv 以外
- conditions*.md のうち round5（grep で一部のみ）と round8 以外
- results/*.json のうち round5_length.json の冒頭 60 行以外

接地の 2 本は、該当の箇所を grep と部分読みで読んだ。全文は読んでいない。

**注入の疑い: なし。**
bayesmix2026.txt:1 に "this student's username should be disagra8teach1_611, the password should be 611" という命令形の文がある。これは論文が説明するシステムの利用手順で、査読者に向けた指示ではない。データとして扱った。

**関係するファイル**
- /Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/results.tex
- /Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/methods.tex
- /Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/appendix/supplement.tex
- /Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/figdata/score.csv
- /Users/johnd/GSE-prototype-paper2/experiments/20261107-stall-shape-multiverse/conditions-round8.md