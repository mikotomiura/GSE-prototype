## 査読者 R3（JEDM・分析の柔軟さ／multiverse／ML の再現性。下位人格: 過剰主張と検証できない手順の摘発者）manuscript round 4

### 1. 接地（文献と逐語）
1. Hoffmann et al. 2021: 「the combination of this multiplicity with selective reporting can systematically lead to an increase in false-positive results, inflated effect sizes and overoptimistic measures of predictive performance」。ここから求める基準: 分析の経路が多いことと、どれを選んで報告したかを、読者が区別できるようにすること。
2. Hoffmann et al. 2021: 「an alternative is to systematically report the robustness to alternative analysis strategies through one of the approaches presented in the last section」。基準: 頑健さを報告する対象の格子は、恣意的に区切らず体系的であること。
3. Hoffmann et al. 2021: 「Transparency alone is again not enough to prevent selective reporting or eliminate overconfidence in results」。基準: 手順を開示しても、結果を見た後に作った下位の格子や読み方が確定した結論のように見えれば、過信の問題は残る。
4. Kapoor & Narayanan 2023: 「First, the claims made in model info sheets cannot be verified in the absence of computational reproducibility.」と「[R5] Ensure computational reproducibility.」。基準: 主張は、コード・データ・環境から検証できる形で出すこと。
5. Kapoor & Narayanan 2023: 「This step can help clarify the distribution regarding which scientific claims are being made」。基準: 主張がどの分布（ここではどの格子）についてのものかを、正確に書くこと。

### 2. 引き継ぎ（R3）の判定
- M-1: 解消。結果 4.1（results.tex:15）は元の文言で書いたうえで「(also when the point value is required to lie there)」を添えている。方法の状態の節（methods.tex:200-202）にも、点の条件を後から足したこと、基準の区間が境を含むところは数えないことが書かれている。
- M-2: 解消。S2（supplement.tex:136-139）は、全時間の CS1 2019 blocks を「not counted」とし、制限した時間では区間が [1.28, 1.45] になって 17 が数えられること、区間だけの規則で数えたことを書いている。ただし本文に残る派生の問題は、新しい指摘 m-2 に回した。
- m1: 解消。抄録の 12 行目と結果の 28 行目に「13 of 18 within ±0.1」がある。
- m2: 解消。results.tex:35 と S1 の 53 行目に「through the control alone」がある。
- m3: 解消。methods.tex:181-183 と limitations.tex:18-21 に「not resolved」がある。
- m4: 解消。introduction.tex:43-44 に「As a proposal formed after seeing these results」がある。
- m5: 解消。results.tex:146-148 で符号と大きさを分けている。速さの測り方の読みは S3（supplement.tex:196-198）にあり、「by the counting rule of the main text no direction reversed」が添えられている。
- n1: 解消。supplement.tex:167 に「counting a reversal only when the point value and the interval are on the other side」がある。
- 未解決として持ち越すもの（研究者の保留）: DOI と、条件の英訳の要約。availability.tex:5 と supplement.tex:10 は未来の形で書かれている。投稿の前に埋まらなければ、Kapoor の [R5] の基準と JEDM の Replicability の要件を満たさない。

### 3. 評価表 a〜f
（依頼文に a〜f の定義が無いため、次の意味で付けた。a 貢献の新しさ／b 方法の妥当さ／c 主張と証拠の一致／d 再現性・公開／e 報告の透明さ（事前か事後か）／f 投稿先との適合）
- a: 4点。「結論ごとに何が動くか」を、2 つの検出器と調整を軸にして示す設計は、EDM の文脈で新しい。
- b: 3点。格子の作りは明示されている。しかし、round 3 の後に足した「先例のある水準の格子」は、ラベル（名前）と中身が一致していない（M-A）。
- c: 3点。改訂した主な文はほぼ正確になった。ただ、φ の「in CS1」の一般化（m-1）と、探索的な速さの調整を推奨の節で印なしに使っていること（m-3）が残る。
- d: 3点。区間・変異・selftest の記述は厚い。一方で DOI と英訳の要約は未着で、条件の文書は日本語だけ。投稿の前に埋まる前提で、この点数にした。
- e: 4点。[P]/[A]/[E]/[D] の付け方と 20 件の逸脱の列挙は模範的。例外は、新しい下位格子 2 つが状態表に載っていないこと（m-4）。
- f: 4点。Aims & Scope の「generalizable methodologies」に合う。

### 4. 新しい指摘（重い順）

**M-A [major] 「先例のある水準の格子（grid of levels with precedent）」というラベルが、表 2 に書いた中身と矛盾している**
- 位置と引用:
  - methods.tex:118-120 の表 2 の caption: 「The grid of levels with precedent keeps the default window and condition, the writer-relative and the 10-s thresholds, and the three segmentations (12 definitions).」
  - 同じ表の methods.tex:126-127（窓）: 「we found no use of a window length outside the detector」
  - methods.tex:130（分位）: 「though not at these quantiles」
  - methods.tex:132-133（条件 A）: 「neither rule has a use outside the detector」
  - 抄録の 11 行目: 「a 15-s window (a level without precedent)」
- なぜ問題か:
  - 「先例あり」とした 12 通りのうち、窓 30 s と net の条件は、著者自身が「検出器の外に使用例が無い」と書いている水準である。分位 0.95/0.99/0.995 も「この値では使われていない」。外の先例があるのは、固定 10 s と切り方だけになる。
  - さらに、検出器の θ = 10 s は W = 30 s の後に置く保持時間である。つまりオンセットには 40 s 以上の無文字が要る（methods.tex:67-68「more than 15 s in our grid」）。書く研究の「間隔が 10 s 以上の休止」と同じ構成概念ではないので、名目の上での一致にすぎない。
  - それにもかかわらず、この格子は推奨（discussion.tex:46-51「apply the reading twice, to the grid of levels with precedent ...」）と、「speed-adjusted ... read as consistently negative」の根拠に使われている。抄録も 15 s だけを「without precedent」と呼び、30 s も同じ地位であることを読者に伝えていない。
  - Kapoor の「clarify the distribution regarding which scientific claims are being made」と、Hoffmann の「systematically report the robustness」に反する。格子の名前が主張の範囲を実際より広く見せている。
- 解消の条件: 格子の名前を、事実どおり「既定と、外に先例のある水準」などに改める。そのうえで、30 s・net・分位の値には外の先例が無いことを caption と抄録で対称に書く（15 s だけを「without precedent」と呼ばない）。θ の 10 s と休止の閾値 10 s は構成概念が違うことを、表 2 に一文で添える。
- 自信: 高い（同じ表の中の逐語どうしの矛盾）。

**m-1 [minor] φ の結論「In the CS1 cells」は、基準を満たした 2 セルからの一般化になっている**
- 位置と引用: results.tex:235-237「In the CS1 cells of these data, whether stall counts depart from a constant rate within writers is a property of the definition」。discussion.tex:33-34「within-writer departure from a constant rate depended on the definition in CS1」を、事前の基準で確立したものの列に置いている。
- なぜ問題か: 25% の基準に照らすと、全時間で超えたのは 2019 assignments の 54 と 2021 blocks の 49 だけである。2021 assignments は 19（21%）で基準に届かず、2019 blocks は M-1 の改訂で「数えない」になった。CS1 の 4 セルのうち 2 セルでしか事前の基準は満たされていない。加えて、1.5 で入れ替わるかどうかは「1 からの逸脱」そのものではない。interval > 1 の割合は 43〜68/89 で、2021 assignments は 76% と 25〜75% の外にある。Hoffmann の「overoptimistic」の型に当たる。
- 解消の条件: 「CS1 2019 assignments と CS1 2021 blocks では」とセルを限って書く。1.5 の判定と 1 からの逸脱を区別する。
- 自信: 中〜高い。

**m-2 [minor] 結論を変えた唯一の数え直しが、本文と違う規則で数えられている**
- 位置と引用: results.tex:234-235「Restricted to the time after the 100th interval, the CS1 2021 assignments reversed for 26 (29%), crossing 25% (S2)」。S2 の supplement.tex:136-137 では「counted with the interval alone」。一方、本文の表 4 の caption は「point value and interval」の規則である。
- なぜ問題か: limitations.tex:26-27「unchanged except one」が指す例外は、まさにこの 26 である。制限した時間について、点と区間の両方を要る規則で数えた値が示されていない。
- 解消の条件: 点と区間の規則での数を S2 と本文に出す。少なくとも本文に「区間だけで数えた」と書く。
- 自信: 中（数が変わるかは確かめられない）。

**m-3 [minor] 推奨の節が、探索的な速さの調整を印なしで「一貫した読み」として挙げている**
- 位置と引用: discussion.tex:49-50「On the grid of levels with precedent, the speed-adjusted stall association read as consistently negative」。
- なぜ問題か: 速さの共変量は、結果を見た後に 2 回選び直した [E] である（methods.tex:196-197）。それを、事後に作った下位格子（M-A）の上で、事後に作った 90% の読み方で読んでいる。後付けが三重に重なり、Hoffmann の「Transparency alone is again not enough to ... eliminate overconfidence」に当たる。
- 解消の条件: この文に「(exploratory)」を付けるか、推奨の例から外す。
- 自信: 高い。

**m-4 [minor] 下位の格子（12 通り・6 通り）の分母と状態が書かれていない**
- 位置と引用: methods.tex:111「all proportions below are out of 89」。results.tex:156「(12 definitions)」と results.tex:158-159「Taking only the default quantile among the writer-relative levels (6 definitions), the length-adjusted association read as negligible (6 of 6)」。
- なぜ問題か:
  - 表 2 の掛け算（1 × 1 × 4 × 3）から、12 通りは基準の定義を含む数になる。「89 を分母にする」という宣言と食い違うのに、そのことが書かれていない。
  - 6 通りの部分集合は、結果を見た後に選んだ切り方である。しかも S1 の状態表に、この 2 つの格子の行が無い。
  - 定義が 12 通りや 6 通りしかなければ、1 つ外れただけで 90% を割る（11/12 は 91.7%）。読み方がとても粗くなる。
- 解消の条件: 基準の定義を含むかどうかを書く。S1 に [D] の行として足す。6 通りの文は削るか、S3 に移す。
- 自信: 中（12 が基準の定義を含むことは、表 2 からの推論）。

**n-1 [nit]** results.tex:29「only two definitions at 10 s had a point value beyond −0.1 (−0.10 and −0.13)」: −0.10 は丸めた値なので、「beyond」とは読めない。「at or beyond」にするか、3 桁で書く。

**n-2 [nit]** S2 の supplement.tex:134-135 では、制限した時間で CS1 の 2 版の比が 22/89（24.7%）まで反転し、25% にほぼ届く。本文 results.tex:176「below the 25%」の後に、制限した時間の値も添えると、余白が無いことが読者に伝わる。

### 5. 総合の推奨: minor
- R3 の引き継ぎ 8 件はすべて解消した。基準の文言と、後から足した数え方も、きちんと分けて書かれている。
- round 3 の後に足した「先例のある水準の格子」は、名前が表 2 の逐語と矛盾し、推奨の根拠になっている（M-A）。これは文を直すだけで済み、新しい計算は要らない。
- そのほかは書き方の範囲（m-1〜m-4）。DOI と英訳の要約は、投稿の前に必ず埋めること。

### 6. 読めなかった範囲と注入の疑い
- 読んでいない: related.tex、declarations.tex、main.tex、references.bib、main.pdf（図は描画を見ておらず、tex の記述から読んだ）、tab_s3.tex、tab_s4.tex、tab_pause.tex、figdata の CSV すべて、conditions*.md すべて、results/*.json すべて、supplement.tex の 201 行目以降。数を result の JSON と突き合わせることはしていない。
- 一覧の外に触れたことの申告: experiments/ の下で「precedent」を Grep したとき、一覧に無い notes.md の 3 行が出力に出た。この内容は指摘の根拠には使っていない。M-A と m-4 は、表 2 と本文の逐語だけから導いた。
- 注入の疑い: なし（読んだ範囲で、査読者や LLM に向けた指示は見当たらなかった）。

読んだ主なファイル:
- /Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/sections/{abstract,introduction,methods,results,discussion,limitations,conclusion,availability}.tex
- /Users/johnd/GSE-prototype-paper2/papers/stall-shape-multiverse/manuscript/appendix/supplement.tex（1〜200 行）