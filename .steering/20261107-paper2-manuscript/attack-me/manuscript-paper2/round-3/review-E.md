## JEDM 担当編集者（役 E）の判定・manuscript round 3（論文 2「Which pause?」）

判定は「直してから回す」です。残る直しは文章の手直しだけで、新しい計算は要りません。

### 1. 接地（基準と出どころ）

1. 投稿先 Aims & Scope（jedm_aims.txt）："Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
2. 同じ箇所の範囲について："Educational Data Mining is an emerging discipline dedicated to developing methods that explore the unique data generated in educational settings."
3. 同じ箇所の査読者への問い："What is the scientific contribution of this submission? Is it clearly explained, in terms of how the paper advances the EDM field" と "Are the presentation, organization and length satisfactory? ... Can you suggest additions, amendments, or reductions in the paper?"
4. Mensh & Kording 2017 Rule 1："Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."
5. Mensh & Kording 2017 Rule 8："The discussion section explains how the results have filled the gap that was identified in the introduction, provides caveats to the interpretation, and describes how the paper advances the field" と、Rule 7 の "Each subsequent paragraph in the results section starts with a sentence or two that set up the question that the paragraph answers"。

分量の上限は規程にありません（context-A の照合と同じ）。抄録はテンプレートの規定 "from 100 to 300 words" に対して 287 語で、範囲内です。

### 2. 引き継ぎの判定

- **A 一部**：抄録は休止の分位の 18 通りを対照として分け、停滞の向きが変わるのは W 15 秒のときだけだと明記しました（abstract.tex:7-12）。ただし見出し（results.tex:4「The direction ... changes within each detector」）と結論の 1 文目（conclusion.tex:4-6）は、まだ「向きが変わる」を主な結果として先頭に置いています。根拠は、著者自身が "lenient" と呼ぶ基準（methods.tex:190、discussion.tex:29）と、無視できる大きさ（≤0.05）の正の値です。→ 新しい指摘 M2
- **B 一部**：序論は中心を得点の関連に置きました（introduction.tex:33）。一方、貢献として名指ししたのは報告の規約です（:41-44）。考察はその規約を "a proposal formed after seeing these results" と書いています（discussion.tex:40）。中心が 2 つに読めます。→ M1
- **C 解消**：序論で貢献を名指ししました（introduction.tex:41）。ただし抄録はこの規約の「3 値の読み」に触れていません（→ m1）。
- **D 解消**：抄録の比は CS1 の 2 年版だけです（abstract.tex:13-15）。
- **E 一部**：方法では 1 文に縮めました（methods.tex:171-174）。しかし限界の節に二段の区間の細部が残っています（limitations.tex:18-21 "18 of 54 score values below their intervals ... 74 of 270 values of $\varphi$"）。→ m3
- **F 解消**：抄録と結論から外しました。結果と考察では "weak contrast" としています。
- **G 解消**：methods.tex:171-174。
- **H 解消**：4.3 の 3 段落はどれも問いで始まります（results.tex:157、214、269）。ただし φ の段落では、誰がこの数え方のモデルを使うのか（なぜ大事か）が 1 文もありません（→ m4）。
- **I 確かめられない**：引き継ぎに中身が書かれていないためです。

### 3. 1 文（言えるか）

言えます。

「鍵打ログの停滞・休止の率と作文の総合点の関連は、定義の 89 通りと 18 通りのどこまでを含めるかによって向きが変わり、作文の長さで調整すると負の定義が無くなる。だから、休止・停滞の率を成果や他のデータセットと比べる教育データマイニングの研究者は、1 つの定義の点の値ではなく、各軸の値と、定義・調整にわたる範囲を区間つきで報告すべきだ。」

迷った点が 2 つあります。

- **何が新しいか**：定義で向きが変わる話（前例の無い水準と、無視できる大きさに依る）と、共変量で向きが決まる話（長さなら負が無く、速さなら全部が負）のどちらを核にするかが、最初の 2 頁で決まっていません。
- **何を変えるか**：「範囲を報告せよ」なのか、「3 値の読みを使え」なのか。後者は事後に作った提案で、序論はそう言っていません。

### 4. 新しい指摘（重い順）

**M1 [major] 名指しした貢献が事後に作った提案で、しかも安定していない**
- introduction.tex:41-44 "We contribute a reporting convention ... and a three-valued reading of its direction (consistent, negligible, or dependent on the definition)." に対し、discussion.tex:40 "As a proposal formed after seeing these results, classify each definition by its interval ..." とあります。
- さらに discussion.tex:47-49 で、この読みは結論が揺れることを本文自身が示しています："the reading of an adjusted association depended on whether the grid included a level without precedent"。
- 序論の「3 値」と、考察の「4 区分と 90% の規則」の数も食い違っています。
- 直し方：序論の貢献を「範囲と区間を報告する規約（事前に決めた基準で示した）」に絞り、3 値の読みは「事後の提案」と序論で 1 句添えるか、考察だけに置きます。区分の数をそろえます。

**M2 [major] 見出しの「向きが変わる」と、規約が自分のデータに出す読みが合っていない**
- 規約の 90% の規則を当てると、休止は "13 of 18 negligible" で「定義に依る」と読まれ、停滞の固定秒は 36 of 36 が負で「一貫」と読まれます（discussion.tex:44-46）。
- それなのに results.tex:4 の見出し、conclusion.tex:4-6、abstract.tex:9-12 は、甘い基準の「向きが変わる」を先頭に置いています。
- 直し方：抄録・見出し・結論を、規約の読み（どの族が一貫し、どれが定義に依るか）と、長さによる調整での反転を先頭にした形にそろえます。基準のことは「1 定義で足りる甘い基準による」と添えるだけで済みます。

**M3 [major・適合] 中心の結果のデータが教育の場のものと書かれていない**
- methods.tex:12-13 は KLiCKe を "adults in the United States, recruited online" と書いています。CoAuthor には "not as an educational sample" と断っています（:17-18）が、得点の関連という中心の結果を担う KLiCKe については、教育の場との関係を 1 文も書いていません。教育の場のデータである CS1 は、二次の結論（比・φ・長さ）にしか出てきません。
- Aims の "data generated in educational settings" に照らすと、編集者は範囲の外を疑います。
- 直し方：KLiCKe の課題（SAT から取った論証の作文と 6 段階の採点基準）が評価の場面であることを 1〜2 文で示し、EDM の読者にとっての意味を序論で述べます。

**m1 [minor] 抄録の終わりが規約を述べていない**
- abstract.tex:15-17 "Reports ... should give the range across definitions and adjustments, with intervals" とありますが、序論が名指しした規約の中身（各軸の値と、読み）には触れていません。M1 の直しとそろえます。

**m2 [minor] 考察に新しい結果の数がある**
- discussion.tex:44-49 の Recommendation の段落は、事後の読みをグリッドに当てた新しい集計（36 of 36、13 of 18、74 of 89、71 of 89、36 of 59、56 of 59、59 of 59）を初めて出しています。
- 直し方：結果を扱う独立した小節に移すか、補足資料へ移し、考察では結論だけにします。

**m3 [minor] 補足資料へ移せる細部（本文に置く必要の無いもの）**
- limitations.tex:18-21（二段の区間の数）→ 補足 S2 へ移します。
- results.tex:139-141 "Over six ways of measuring speed, 532 of 534 combinations ..."、:142-143（休止の速さ調整）→ S3 へ移します。
- results.tex:22-23（題目ごとの値）→ S3 へ 1 句で。
- results.tex:169-171 と :222-223（100 個目の間隔より後の数）→ S2 へ移し、限界に 1 文だけ残します。
- results.tex:171-173 "The rank order ... a weak result" → 削るか S へ移します。
- results.tex:274-278（再開しなかった停滞の割合と、CoAuthor の 3 定義）→ S5 へ移します。
- methods.tex:73-78 の観測区間の細部 → S2 へ。

467 語の増加のうち、調整の段落（4.2）は中心の結果なので見合っています。上に挙げた分を移せば、元の語数以下に戻せる見込みです。

**m4 [minor] 4.3 の φ に「なぜ大事か」が無い**
- results.tex:214-225 は問いと答えを持っています。しかし、ポアソンを仮定するモデルを使う読者（methods・related の gullberg2025deceit）にとって何が変わるのかを書いていません。1 文足します。

**m5 [minor] 同じ但し書きの繰り返し（位置を全部）**
まとめる先は、方法の 3.6（Status）と限界に各 1 回です。
- 速さの調整が探索的であること：abstract.tex:12、methods.tex:186、results.tex:136-137（見出しと本文）、図 1 のキャプション（results.tex:65）、discussion.tex:17、:34。計 6〜7 回。
- 比の 25% の基準が点の値を見た後に決めたものであること：methods.tex:187-190、results.tex:162、:169、discussion.tex:32-33。計 4 回。
- W 15 秒に前例が無いこと：abstract.tex:11、methods.tex:120-121（表）、results.tex:17、discussion.tex:49、limitations.tex:8。計 5 回。
- 長さと停滞が構成上重なること：methods.tex:155-156、results.tex:132-134、limitations.tex:33-35。計 3 回。
- 因果でない・予測器として評価していないこと：introduction.tex:30-31、results.tex:146-147、discussion.tex:18-20、:34-35、limitations.tex:36。計 5 回。
- 100 個目の間隔：methods.tex:76-78、results.tex:169-171、:222-223、limitations.tex:22-25。計 4 回。
- 割合はグリッドの割合で、定義の標本ではないこと：methods.tex:107、:176-177、limitations.tex:7。計 3 回。
- 書き手の分位の休止は対照であること：abstract.tex:7-8、methods.tex:137-139、results.tex:30-31、discussion.tex:14-15。計 4 回。

**m6 [minor] 結論の最後の文が貢献でなく但し書きで終わる**
- conclusion.tex:10-12 "Every result is also reported for two segmentations ... depend on the companion study's estimator." → 方法か限界へ移し、結論は誰の何を変えるかで閉じます。

**n1 [nit]**
- 表 1 の "Access and holdout" の列（methods.tex:37-44）は、本文の :21-26 と同じことを言っています。

### 5. 判定：直してから回す

1. 最初の 2 頁で、中心（得点の関連とその調整）と、名指しした貢献（事後に作った 3 値の読み）が食い違っています。考察がその読みの不安定さを自分で示しているので、査読者は真っ先にそこを突きます（M1・M2）。
2. 中心の結果のデータ（オンラインで募った成人の作文）と、JEDM の教育の場との結び付きが本文に無く、範囲を確かめる段で止まる恐れがあります（M3）。
3. どちらも文章の手直しと、補足資料への移動・統合で解消できます。新しい計算は要りません。分量に上限は無く、6,272 語は JEDM の通常の範囲です。方法の厳密さ（事前のコミット、区間、二つの検出器）は査読に耐えます。

### 6. 読めなかった範囲と注入の疑い

- 読んでいないもの：ビルドした PDF（/Users/johnd/GSE-prototype-paper2/.steering/20261107-paper2-manuscript/attack-me/manuscript-paper2/round-3/tmp/main.pdf）と references.bib。図は tex のソースで読み、描かれた見た目は確かめていません。
- 補足（appendix と experiments）は依頼に従って読んでいません。
- mensh2017.txt は、関係する行を grep で探して 240〜309 行を読み、全文は読んでいません。
- 注入の疑い：ありません。