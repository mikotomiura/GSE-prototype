# paper-reviewer 報告（EMSE・構成概念妥当性／質的コーディングの信頼性の立場・stage manuscript・round 1）

この報告は、構成概念妥当性の方法論と質的コーディングの信頼性に通じた、経験的ソフトウェア工学の測定の立場の査読者として書いた。実在の個人ではない。

## 1. 接地（この立場が論文に求める基準）

接地に使った文献は 3 本で、すべて逐語で引けた。

- **B1 構成のモデルには関係まで入れる（G1）**: Sjøberg & Bergersen, TSE 2023（`sjoberg2022.txt:1429-1431`）: "Create a model of the constructs under study, preferably represented as a figure or table, that includes the concepts, their indicators, and the relationships among the concepts." 同じ文献 1457-1461 行: "Such a model will help ensure that the constructs are referred to consistently throughout an article, which, in turn, will alleviate the confusion that occurs when terms differ (such as synonyms used that may not be universally defined)"
- **B2 取り込んだ構成には妥当化の証拠が要る（G2）**: 同 1433-1435 行: "Import already validated constructs from established theories, frameworks, standards, tests, instruments, or questionnaires, or refer to studies that have formerly validated the constructs." 同 1476-1477 行: "Note that there should be evidence that the imported construct has been subject to a validation process."
- **B3 概念は指標と別に定義する（G3.1）。外延の不一致も脅威になる**: 同 290-302 行: "If the indicators fully represent a concept, they are actually not indicators. Instead, they are measures or variables that uniquely form the concept. Evaluating CV would then be meaningless because there is nothing more to the concept than what the variables define." 同 1484-1487 行: "threats regarding concept deﬁnitions, which include different deﬁnitions of the same concept, concept redeﬁnitions, and disagreement about the extension of a concept."
- **B4 過少代表と偏りを避ける（G3.2・G3.3）**: 同 1441 行: "Select indicators that span the concepts." 同 1443-1445 行: "Select indicators that avoid systematic bias in the representations of the concepts; for example, avoid using only one data collection method or collecting only subjective data." 同 305-308 行: "the indicator does not follow “naturally” from the deﬁnition of the concept. The indicator may only indirectly represent the concept and may be a better indicator of another concept." 同 1604-1605 行（単一の二値指標の例）: "frequency relative to the length of the document, i.e., not only a binary indicator"
- **B5 脅威と構成を明示する（G5・G4）**: 同 1448-1449 行: "When reporting threats to CV in a paper, be explicit about what the threats are and which constructs are subject to the threats." Sjøberg & Bergersen, EASE 2023（`sjoberg2023.txt:371-373`）: "Note that if it is unclear which construct(s) is in question when a threat is described, it may not be a threat to CV but to other validity types." 同 283-284 行: "If a definition is introduced in a paper, it should be followed."
- **B6 コーディングの信頼性（ICR）**: O'Connor & Joffe 2020（`oconnor2020.txt:483-484`）: "A minimum of two independent coders is necessary to establish ICR." 同 531-533 行: "It is generally accepted that the physical double-coding should be performed independently without conferral between coders." 同 443-446 行（行末のハイフンをつないだ）: "If researchers intend to include numerical information in the analytic results, validating that through initial ICR assessment is good practice." 同 790-792 行: "pooling all codes’ reliability figures means codes with poor reliability can be “hidden” or canceled out by codes that perform very well"

## 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 慎重に限定している箇所は多い（D2 が再現したとは言わない・因果を主張しない、など）。ただし結論（main.tex:371）の "over-states the share that were resolved without consultation" と貢献 (ii)（:68）の "estimates ... in two independent public datasets" は、指標が支えられる範囲を超えている。D1 の差の 8/10 は帰結が不明な DF3 であり、D2 の指標は grounded theory のコードを転用したものである（M1・M3） |
| b 方法の穴 | 2 | 解決の側の操作化を変えていない（DF3・DF5・観察の終わりを打ち切りとして扱う定義が無い）。成果コードについて、コードごとの一致度が無い。D2 では、表と「解決」列の原典での意味を検討していない。二値の「1 回でも参照した」はエピソードの長さ（曝露）に依存する（M1・M3・M4・m2） |
| c 持ち帰れるもの | 3 | 推奨 3（終わり方の内訳を分けて数える）は有用である。一方、R0 を自己解決として読む誤用が実際にあることを一件も示していない（M5）。加えて、貢献 (i) の分解は会計上の恒等式である（m5） |
| d 簡潔さと構成 | 4 | 節の立て方・表・数値の出どころは明快である。用語が揺れていること（self-resolution／unaided resolution／resolved without help／solved）は G1 の趣旨に反する（M2） |
| e 規程への適合 | 4 | 照らし合わせた結果は次のとおり。要旨 234 語（規程は 150〜250 語）、キーワード 6 個（規程は 4〜6 個）、LLM の利用は Method 節（Sect. 5.5）に記載、Data availability statement あり、single-blind なので氏名の記載は可。外れているのは声明の置き場所だけである。規程は "Please use the title page for providing the statements." だが、声明は本文の末尾にあり、タイトル頁には無い（m6） |
| f 先行研究の位置づけ | 3 | Sjøberg・Ralph & Tempero・援助要請研究・ICH E9 は引いている。足りないのは 3 点。他人が別の目的で付けた質的コードを数値の指標として二次利用することの妥当性の議論、打ち切りや部分識別の扱い（ICH E9 を引きながら適用していない）、そして R0 の実際の再利用例である |

## 3. 指摘の一覧（重い順）

- **[severity: major] M1. 分子効果の大半は「帰結が不明」の単位なのに、全定義でそれを「未解決」と数えている。見出しの "over-states" は確立していない**
  - 位置と引用:
    - main.tex:204「DF3 records the developer's stated intention; it ends the episode but not necessarily the effort, and the coding does not link it to later work on the same defect, so its eventual outcome is unknown.」
    - :204「8 ended with the developer going to return later (DF3), 1 with the defect mostly fixed (DF2) and 1 with the defect not reproducible (DF5)」
    - :371「the share of episodes or tasks without consultation over-states the share that were resolved without consultation」
    - :44「by 7.9 to 11.2 points across eight operational definitions」
    - :89「administrative censoring, which is to be handled as a missing-data problem」
    - :168「In D2, ``unresolved'' therefore includes the end of observation」
  - なぜ問題か:
    - 解決の定義は 2 通り（DF1、DF1 または DF2）しかなく、どちらも DF3 と DF5 を「未解決」に入れている。DF3 と DF5 を打ち切りとして除くと、D1 の分子効果は概算で DF1 なら 1/75、DF1 または DF2 なら 0 になる（本文の内訳から計算した）。
    - したがって 11.2pp は主に「解決が観察されなかった」幅である。「解決しなかった」量ではない。真の「援助なしで解決した割合」に対しては、R0' が下限、R0 が上限の区間を与えるにすぎない。
    - 本文は ICH E9 を引いて、事象と打ち切りの区別を導入している。それなのに D2 の研究期間終了（まさに administrative censoring）を失敗側に入れており、自ら導入した区別に従っていない（B5「If a definition is introduced in a paper, it should be followed.」）。
    - 「解決」の外延（DF3 を含むか）はまさに B3 の "disagreement about the extension of a concept" にあたる。また、「未解決」の指標は「観察窓内で未解決」という別の概念をよりよく表している（B4 "may be a better indicator of another concept"）。
  - 解消の条件:
    - (1) DF3（と DF5）、および D2 の研究期間終了の 4 課題を打ち切りとして分母から除く定義を、感度分析に加える。
    - (2) 結果を部分識別の区間 [R0', R0] として提示し、要旨と結論を "over-states" から「解決が観察されていない単位を含む」へ書き直す。
    - (3) D1 は動画が公開されている（原典 `alaboudi2021.txt:408-409`「The entire dataset, including the videos and codes, is publicly available」）。DF3 の 8 件について、同じセッション内でその欠陥に戻ったかを確かめて報告する。
  - 自信: 高

- **[severity: major] M2. 吟味する概念「unaided resolution」を、指標そのもので定義している。概念と指標が一致するので、構成概念妥当性を論じる意味が無くなる。表 1 は G1 の要件（関係）を満たさない**
  - 位置と引用:
    - main.tex:132「The concept whose operationalisation this paper examines is \emph{unaided resolution}: a unit that was resolved without consultation.」
    - :342「Table~\ref{tab:constructs} is the model of constructs that their guideline G1 asks for」
    - :93「whether ``no consultation'' is a valid operationalisation of ``resolved without help''」
    - 題「self-resolution measures」
  - なぜ問題か:
    - B3 のとおり、指標で尽くされる概念には評価すべき妥当性が無い。問われているのは「援助なしで解決した」という概念で、それは「参照の記録が無い」より広い。たとえば次のものを含む。
      - 求めずに受けた援助（配信者の両データで、視聴者がチャットで出す案。原典 `li2026.txt:595-597`「some streamers engaged directly with chat participants to brainstorm solutions with viewers in real time (S3, S5)」）
      - 開発環境の内側の資源（`li2026.txt:620-621`「referring to syntax documentation within the IDE (S1)」、:576「P7 used IDE-embedded AI」）
    - 表 1 は概念と指標を並べるだけで、G1 が求める "the relationships among the concepts" が無い。RQ3 で使う欠陥の出自（DF8）、効いている可能性のあるエピソードの長さも、モデルに無い。
    - 同じ概念を少なくとも 5 つの名で呼んでいる（self-resolution／unaided resolution／resolved without help／solved／unaided）。B1 が避けよと言う同義語の混乱そのものである。
  - 解消の条件:
    - (1) 概念を指標から独立に定義する（例: 開発者が外部の知識源や他者に依らずに欠陥を修正した状態に至ること）。
    - (2) 「参照」の指標がその概念のどの側面を覆い、どれを覆わないか（求めない援助・環境内の資源・観察されない援助）を表に明記する。
    - (3) 表 1 に概念間の関係（単位の終わり→観察された解決、援助の必要→参照、出自・長さ→両者）を加える。
    - (4) 用語を 1 つに統一する。
  - 自信: 高

- **[severity: major] M3. D2 の「参照」と「解決」の指標は、原典のコーディングの意味から見て正当に転用されていない**
  - 位置と引用:
    - main.tex:166「We count a task as consulted if Table~5 lists it under documentation, social-technical sources or web sources」
    - :142「\emph{Resolved} = Y in Table 4 of the paper」
    - :170「The authors ``prioritized coding the verbal transcripts''」
    - :68「(ii) estimates of the difference \Rz{}~$-$~\Rzp{} in two independent public datasets」
  - なぜ問題か:
    - (a) 原典は、配信者のデータを網羅的にコード化していない（`li2026.txt:230-231`「With the categories emerging, we did not perform initial coding on the streamer data and instead only coded selectively.」）。原稿はこの一文を引いていない。未解決の 4 課題のうち 3 つは配信者の課題で、表のみの定義で分子に入る 2 課題の一方（S5TA）も配信者の課題である。表 5 に載っていないことは、参照が無かった証拠として弱い。
    - (b) 表 5 は grounded theory の技法のコードブックである（`li2026.txt:667-668`「Backed by the grounded theory framework, we categorize debugging techniques based on actions and associate actions with the intentions」）。課題ごとの網羅的な出現記録として設計されたものではない。
    - (c) 「Resolved = Y」の P1TA は、開発者が直した課題ではない（`li2026.txt:342-343`「P1TA discovered that the bug had already been fixed in the latest patch, skipping the fix construction step」、:600「redirected the issue to those best equipped to resolve it」）。表のみの定義では、P1TA が「援助なしで解決」の分子に入る。これは指標が概念から "naturally" に従わない典型である（B4）。
    - B2 の "evidence that the imported construct has been subject to a validation process" も、B6 の「数値に使うなら ICR で確かめる」も、D2 には無い。
  - 解消の条件:
    - (1) 選択的コーディングの一文を引用し、その影響を「参照」の過少代表として論じる。
    - (2) P1TA の解決の扱いを明記し、「開発者が解決したのではない」または除外とする感度分析を加える。
    - (3) D2 は「推定」ではなく例示と位置づける。貢献 (ii) の "estimates in two independent public datasets" も弱める。
  - 自信: 事実の確認は高、severity の判断は中

- **[severity: major] M4. 指標の根拠となる成果コード（DF1〜DF5）と参照コード（U・OT2）に、コードごとの信頼性の証拠が無い**
  - 位置と引用:
    - main.tex:154「the journal version reports Cohen's kappa of 75\% for episodes and 84\% for activities」
    - :350「In both datasets one author coded the whole dataset ... so systematic errors of that coder would not be detected by inter-rater agreement.」
  - なぜ問題か:
    - 原典（`alaboudi2021.txt:404-407`）の κ は、20 エピソードと 166 活動の「episodes」と「activities」についての値である。分子効果を決める DF3 と DF1 の区別（発話に基づく判断）や U コードについては、一致度が示されていない。B6 は、プールした値に弱いコードが隠れると警告している（"codes with poor reliability can be “hidden”"）。
    - D2 は ICR を取っていない（`li2026.txt:173-174`「The first author then performed initial coding on the transcripts and discussed the codes with the second author」）。B6「A minimum of two independent coders is necessary to establish ICR.」
    - 本文 :350 の記述は向きが正確でない。較正のあとに 1 名だけで全体を付けたので、ずれが検出されない、と書くのが正しい。
  - 解消の条件:
    - (1) 「成果コードと参照の有無については、コードごとの一致度が報告されていない」と明記する。
    - (2) D1 は動画が公開されているので、別の人間のコーダーが参照の有無を知らない状態で、89 エピソードの終わり方を再コード化する。少なくとも未解決の 16 件と、無作為に選んだ解決のエピソード（O'Connor のいう 10〜25%）で行う。そのうえで DF コードごとの κ を報告する。
  - 自信: 中〜高（journal 版は一覧に無く読めないが、原稿が引く値は preprint と同じ 2 つである）

- **[severity: major] M5. R0 を「自己解決」として読む誤用が、実際にあると示されていない（藁人形の危険）**
  - 位置と引用:
    - main.tex:55「That reading is attractive whenever published observational data are reused as a reference point」（引用なし）
    - :57「The original debugging studies ... do not present its complement as a measure of self-resolution.」
    - :81「Neither study presents the share ... as a measure of self-resolution.」
  - なぜ問題か: 構成概念妥当性は "whether one can justifiably make claims at the conceptual level that are supported by results at the operational level"（`sjoberg2022.txt:4-5`。原稿 :93 も同じ定義を引く）を問う。概念の水準でその主張をしている文献が 1 つも示されなければ、脅威は仮想のものにとどまり、持ち帰れるものが弱まる。
  - 解消の条件: R0（または 1 − 参照率）を、援助なしでの解決・自力での解決の指標として再利用している実例を 1 件以上引く。それができなければ、主張を「報告の推奨」に縮め、D1 と D2 の数値は例示と位置づける。
  - 自信: 中

- **[severity: minor] m1. D1 の 4 つの参照の定義は入れ子で、一方向（広げる方向）にしか動いていない。これを書いていない**
  - 位置と引用: main.tex:160「\emph{+U} ..., \emph{+OT2} ... and \emph{+OT2+U}」、:234「every bootstrap interval excluded 0」
  - なぜ問題か: strict ⊂ +U、+OT2 ⊂ +OT2+U であり（`analysis/d1.py:109-118` の `is_consult` で確認）、どれも参照を広げる側の感度である。分子効果に対して保守側に動くこと自体は妥当だが、要旨の「8 定義にわたって 7.9〜11.2」は、解決の側の不確かさ（M1）を覆っていない。
  - 解消の条件: 4 定義が入れ子であることと、分子効果への向きを明記する。8 定義の範囲は「参照の範囲を広げた場合」と限定して述べる。
  - 自信: 高

- **[severity: minor] m2. 二値の参照指標は単位の長さ（曝露）に依存する。この偏りを論じていない**
  - 位置と引用: main.tex:298「Short episodes consulted & 0\% & 0/22」、:299「Long episodes consulted & 74\% & 11/23」、:260「Part of the pooled association therefore reflects which defects the developers were working on」
  - なぜ問題か: 「1 回でも参照したか」は長い単位ほど 1 になりやすい。DF3 で早く切り上げたエピソードは、参照の機会が無かっただけかもしれない。RQ3 の解釈は長さという代替説明に触れていない。B4 の例（"not only a binary indicator"）がまさにこの点である。
  - 解消の条件: 分子に入る 10 エピソードと他のエピソードの長さの分布を示す。時間あたりの参照、または長さで層別した表を加え、RQ3 の解釈に長さを併記する。
  - 自信: 中

- **[severity: minor] m3. D2 の本文中の参照を拾う作業が網羅的に記録されておらず、独立なコーディングでもない**
  - 位置と引用:
    - main.tex:170「both were identified independently by the two assistant instances ... and the author agreed with this reading」
    - `data/li-coblenz-2026/text_external.csv` は 3 つの引用だけを載せる
  - なぜ問題か:
    - 原典には、候補になり得る文が他にもあり、扱いが書かれていない（`li2026.txt:601-602` P5 のコミットの閲覧、:615 P3 の資格情報の依頼、:620-621 S1 の IDE 内の文書、:609-610 P4 が「platform team」に話す可能性に触れた発言）。S4 を除外したことは本文にしか書かれていない。
    - 同じモデルの 2 インスタンスが付けた判断に著者が同意する形は、B6 の "independently without conferral between coders" にあたらない。
    - 分子効果は動かないもの（P5・P3 は解決済み）が多いが、S1 の IDE 内の文書は D1 の strict（環境の外）と定義が揃っていないことを示す。
  - 解消の条件: 原典の全文から候補文を規則で拾い、文ごとの判定と理由を表にする（補遺または再現一式）。少なくとも配信者の課題については、人間の第二コーダーが分析の目的を知らない状態で判定する。
  - 自信: 中

- **[severity: minor] m4. 脅威の節は G1〜G5 の形をなぞっているが、構成ごとの脅威の向きが無く、置き場所の誤りもある**
  - 位置と引用:
    - main.tex:342「guideline G2 (import validated constructs) applies only in part」
    - :358（External validity）「streamers may consult or narrate differently because they are watched」
    - :350 の単一コーダーの記述が「Resolution」の段落にだけある
  - なぜ問題か:
    - G2 の要件は「妥当化の証拠」である（B2）。「部分的に当てはまる」で済ませると、取り込んだコードを評価していないことが見えなくなる。
    - 発話の仕方が変われば、指標が何を捉えるかが変わる。これは構成概念妥当性の問題で、外的妥当性の節に置くのは G4 の趣旨に反する（B5）。
    - 単一コーダーの問題は「参照」にも同じく当てはまる。
  - 解消の条件: 構成（参照・解決・単位の終わり・援助なしの解決）× 脅威の型（定義・過少代表・偏り）× R0・R0'・分子効果への向き、の表を置く。発話の点は構成概念妥当性の節へ移す。
  - 自信: 中

- **[severity: minor] m5. 貢献 (i) の「厳密な分解」は会計上の恒等式である**
  - 位置と引用: main.tex:68「(i) an exact decomposition that states what each of the three measures counts」、:128「Equation~\eqref{eq:reading} is an identity about the three measures, not an additional analysis」
  - なぜ問題か: R0 − R0' = b/N は定義からそのまま出る。本文 :128 自身が「追加の分析ではない」と認めているのに、貢献に数えるのは過大である。
  - 解消の条件: 貢献から外して「読み方の道具」とするか、相殺の条件（q と R1 の大小）を一般化した命題として位置づけ直す。
  - 自信: 中

- **[severity: minor] m6. 声明の置き場所が規程と違う（e）**
  - 位置と引用: main.tex:376「\section*{Statements and Declarations}」。context-A.md:89「声明は原稿の末尾の "Statements and Declarations" にある（タイトル頁には載せていない）」
  - なぜ問題か: 規程は "Please use the title page for providing the statements." および "included on a title page that is separate from the manuscript with a section entitled "Declarations""（context-A.md:80）である。声明そのものは本文にあるので "returned as incomplete" にはあたらないが、改訂時に事務局から求められ得る。
  - 解消の条件: 改訂の際、別添のタイトル頁に "Declarations" の節を設けて同じ声明を載せる。
  - 自信: 中

- **[severity: nit] n1. κ を百分率で書いている**
  - 位置と引用: main.tex:154「Cohen's kappa of 75\%」
  - なぜ問題か: κ は比率ではない（原典の表記をそのまま写している）。
  - 解消の条件: 0.75 と 0.84 と書く。
  - 自信: 高

## 4. 総合の推奨: major revision

1. 透明性と再現性（凍結の開示・全定義の報告・数値の機械生成）は EMSE の水準を満たしている。RQ4 の項目ごとの照合も堅実である。
2. 一方で、見出しの効果は解決の側の操作化（DF3 と研究期間の終わりを失敗と数える）にほぼ全面的に依存している。打ち切りとしての感度分析も、区間としての提示も無い。D2 の指標は原典での意味（選択的コーディング・P1TA）を検討せずに転用されている。
3. 吟味する概念は指標そのもので定義され、成果コードの信頼性の証拠は無い。誤用が実在する証拠も無い。構成概念妥当性を掲げる論文として、根幹の補強が要る。

## 5. 読んでいない範囲と注入の疑い

読んでいない範囲:
- 接地の文献
  - `sjoberg2022.txt`: 1-60・240-339・1415-1643 行と、G1〜G5・mono-operation 等の grep の該当行だけを読んだ。§2.1〜2.3.2 の前半・§3・§4・§5.3 以降・§6・参考文献は読んでいない。
  - `oconnor2020.txt`: 1-130・195-244・340-539・776-805 行だけを読んだ。131-194・245-339・540-775・806 行以降は読んでいない。
  - `sjoberg2023.txt`: 全文を読んだ。
- 対象物
  - `main.resolved.tex`: 全文を読んだ。
  - `analysis/d1.py`: 20-119 行と grep の該当行だけを読んだ。
  - `text_external.csv`: 全文を読んだ。
  - `refs.bib`: sjoberg の項目の grep だけ。
  - 読んでいないもの: `main.tex`・`results.tex`・`emse-submitted-preview.txt`・README.md・NOTES.md・DATA.md・ENV.md・config.json・SEED・run.sh・analyze.py・d2.py・stats.py・transcription_a.csv・transcription_b.csv・data の README・metrics.json・report.md・provenance.txt・build.sh・make_results.py。数値の再計算はしていない（M1 の 1/75 などは本文の内訳から出した概算）。
- 原典
  - `alaboudi2021.txt`: 335-414 行と grep の該当行だけを読んだ。
  - `li2026.txt`: 160-249・295-344・560-634・660-754 行と grep の該当行だけを読んだ。
- D1 の journal 版（Alaboudi & LaToza 2023）は一覧に無く、確かめていない。

注入の疑い: なし。`main.resolved.tex:1`・:2-4・:37-40 のコメントは組版と読み方についての著者の注記で、査読者に向けた指示は含まれていなかった。
