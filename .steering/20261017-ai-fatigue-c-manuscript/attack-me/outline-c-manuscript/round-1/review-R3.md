# 査読報告（R3: メタ研究・事前登録・再現性の立場の査読者／批判的な下位人格: 過剰主張と検証できない手順の摘発者）

対象: /Users/johnd/GSE-prototype-af-c/papers/ai-fatigue-measurement/manuscript/outline.md（stage: outline）
併読: registration-en.md（draft 0.6）、codebook-c2b-en.md（v2）、README.md

## 1. 接地（この立場が論文に求める基準・逐語）

文献 3 本とも読めた（本文は 1 行の長いテキストなので、Grep で該当箇所だけ抜き出した）。

- G1（van den Akker et al., 2023, gsrr.txt）: "You should be transparent about any deviations from the preregistration and provide the rationale for these deviations in your final review." → 登録からの逸脱は、理由を添えて本文で示す。
- G2（同上）: the registry "allowed third parties to check the extent to which completed systematic reviews (as presented in journal articles) are carried out in line with the protocol, making it easier to identify decisions that may have introduced bias" → 本文と登録を第三者が突き合わせられること。
- G3（Mbuagbaw et al., 2020, mbuagbaw2020.txt）: "researchers interested in conducting methodological studies must consider how generalizable or applicable their findings are. This should tie in closely with the research question and should be explicit." → 一般化の範囲を問いと結びつけ、明示する。
- G4（Mbuagbaw et al., 2020）: "to generate a representative sample, a comprehensive reproducible search may be necessary to build a sampling frame" と、"Should I extract data in duplicate?A: Yes. Duplicate data extraction takes more time but results in less errors" → 抽出枠の代表性と、二重抽出による誤りの抑制。
- G5（Mbuagbaw et al., 2020）: "Data from methodological studies are often clustered ... Not accounting for clustering could lead to incorrect p-values, unduly narrow confidence intervals, and biased estimates" → 分析の単位と、クラスターの扱い。
- G6（Nuijten et al., 2016, nuijten2016.txt）: statcheck "can only search for prespecified strings of text ... it does not read results that deviate from the APA template ... statcheck will not read results in tables"、"statcheck scans the whole text of the article for the words “one-tailed,” “one-sided,” or “directional.”"、"half of all published psychology papers that use NHST contained at least one p-value that was inconsistent" → 再計算の手順は、何を読み何を読まないかを明示し、検証したうえで使う。誤りは論文単位と p 値単位の両方で数える。

## 2. 評価表

依頼文に a・c・e・f の意味しか書かれていなかったので、b・d は私の解釈で置いた。

| 観点 | 点（5 段階） | 所見 |
|---|---|---|
| a 主張と根拠の一致（重） | 3 | 主張と根拠の表、手で値を打たない規則、頻度の語を禁じる規則は模範的。ただし抄録・題・寄与・考察 5.2 の言い方が、登録の限界（無料の資料だけ・母集団群ごとに偏った選別・規則を知る著者が適格を判定・二人とも物語的レビューの著者）より強く読める。 |
| b 手順の検証可能性（解釈） | 4 | 登録・seed・SHA-256・スクリプト・判定の公開まで揃っている。外枠そのものが固定された時点を示す証拠が無い。C4f が statcheck とどう違うかを書いていない。 |
| c 持ち帰れるもの（重） | 3 | 「1 件以上あれば observed」の陳述は、存在を言うだけで情報量が小さい。読者が持ち帰るものは、符号化の体系と公開する表が主になる。その位置づけを寄与の順に反映すべき。 |
| d 構成・提示（解釈） | 4 | 節の順・表の枠は明確。表 9 の単位（結果単位か記録単位か）が足りない。 |
| e 規程への適合 | 評価外 | 投稿先が未定のため。 |
| f 先行研究の位置づけ（重） | 2 | 新規性の根拠になる探索が部分的なのに、外枠はそれを伝えていない。最も近い先例（Perrig et al. 2024、COSMIN 系、心理学の測定実践のメタ研究）との違いを示す比較の枠が無い。抄録の背景の主張に出典が無い。 |

## 3. 指摘の一覧（重い順）

- [severity: major] 抄録・題の主張の範囲が、確認集合の限られた来歴を運んでいない
  - 位置と引用: outline.md「Rule for the abstract」L77–83「The abstract reports, for the confirmation set only: the number of studies ... and, for each problem type of GSRR-57, the registered statement ...」。Title L11「How do studies of "AI fatigue" attribute fatigue to AI, measure it, and report it?」。一方、Scope L48–50「It is not a census of the literature ... the population groups were screened unevenly before registration」。
  - なぜ問題か: 抄録の規則は、確認集合が無料の資料だけから組んだ母集団であること、母集団群ごとの選別の偏り、規則を知る著者が適格を判定したこと（GSRR-65）を抄録に入れない。題も文献全体について問う形をとっている。抄録だけを読む読者は、確認集合を文献の代表と読む。G3「This should tie in closely with the research question and should be explicit」、G4「a comprehensive reproducible search may be necessary to build a sampling frame」。
  - 解消の条件: 抄録の規則に「範囲の 1 文」を必須として加え、語数の超過で削らない（例: 確認集合は無料の資料から組んだ 1 つのデータベースから、規則を知る著者が選別したもので、文献の網羅ではない）。題は副題か問いの形で集合を限定する（例: "... in a registered set of studies"）。
  - 自信: 高

- [severity: major] 「two independent coders」を抄録に無条件で書く予定は、登録の留保と矛盾する
  - 位置と引用: outline.md L92–93「What was done (a registered methodological review ...; seven codes; two independent coders)」。
  - なぜ問題か: 登録 GSRR-46 は「Their agreement is therefore reported as agreement between two coders who share that view, not as agreement between independent perspectives」とする。GSRR-44 は coder 2 を欠いたとき「no claim of independent coding is made」とする。外枠は結果を見る前の段階で、条件つきの事実を無条件の主張として固定している。G4（二重抽出の価値）は、手順が実際に行われたことを前提にしている。
  - 解消の条件: 抄録の規則を「実際の符号化の形（二人の独立した符号化か、単独での二回か）を GSRR-44 の結果どおりに書き、二人が物語的レビューの共著者であることを添える」に変える。
  - 自信: 高

- [severity: major] 新規性の主張（「No review was found」）が、部分的な探索の上に立っていることを外枠が隠している
  - 位置と引用: outline.md L106–107「No review was found that tabulates, study by study, how fatigue is tied to AI, what the fatigue items ask about, and whether reports are internally consistent (the search is described in GSRR-10).」。登録 GSRR-10 L64「The last point was checked in 16 searches of free sources ... The first two were checked only in the reviews we had already read.」。
  - なぜ問題か: 3 つの要素のうち 2 つは探索されていない。本文が「GSRR-10 を参照」で済ませると、読者は 3 要素すべてを探したと読む。新規性の主張として過大である。さらに、抄録の背景の「existing reviews point to unvalidated scales and unclear construct boundaries」（L91–92）には出典の枠が無い。参考文献 10 本の中に該当するレビューは見当たらない。
  - 解消の条件: 本文で、どの要素をどの資料でどう探したかを逐語に近い形で書き、「見つけられなかった」の範囲を限定する。背景の主張には該当レビューを引く。最も近い先例（Perrig et al. 2024 の UX の測定実践、COSMIN 系、心理学一般の測定実践のメタ研究）と、比較の次元（単位・符号の内容・帰属の扱い・再計算の有無）を表にして、何が新しいかを示す。
  - 自信: 高（探索の範囲について）／中（比較すべき先例の具体名について）

- [severity: major] 確認集合（confirmation set）という語と考察 5.2 が、記述研究を確認的な検証として読ませる
  - 位置と引用: outline.md L166–168「Relation to the narrative review: which of its observations were and were not observed when the rules were fixed in advance and applied to a different set」。寄与 2 L68「a set of studies not used to build the rules」。登録 GSRR-13「Expectations / hypotheses. None.」。
  - なぜ問題か: 「1 件以上で observed」という閾値は、集合が大きければほぼ自明に満たされる。「not observed」は、評価できた件数が小さいときにはほとんど何も言わない。これを物語的レビューの観察と対照させると、「事前に固定した規則で再現された／されなかった」という確認的な読みになる。しかし、規則（コードブック v2）は探索の結果を見た後に書かれ（GSRR-10）、選別したのは規則を知る著者である（GSRR-65）。どちらも確認の独立性を弱める。G2 が言う第三者の突き合わせは、本文の言い方が登録の主張より強くないことを前提にしている。
  - 解消の条件: 5.2 で「再現」「確認」の語を使わないと規則に明記する。observed / not observed は存在の陳述であって、頻度の比較でも再現の判定でもないことを、方法と考察の両方で 1 文ずつ書く。not observed には評価できた件数を常に並べる（規則はあるので、考察 5.2 にも適用すると明記する）。語の誤読を避けるため、「confirmation set」に「held-out set」などの併記を検討する。
  - 自信: 中

- [severity: major] C4f の再計算を「statcheck の論理に従う」と位置づけるなら、違いと検証を本文で示す必要がある。表 9 の単位も足りない
  - 位置と引用: outline.md L118「recalculation of reported statistics (Nuijten et al., 2016)」、L249「Table 9: C4 rules (a) to (f), with the record summary and the gross-inconsistency summary of (f)」。登録 C4f「These rules follow the logic of statcheck (Nuijten et al., 2016). A test is one-tailed only if the report says one-tailed, one-sided or directional for it.」、「Each record is then summarised as any inconsistency / none ...」。
  - なぜ問題か: (1) statcheck は論文全体を走査して片側の語を探す（G6「scans the whole text of the article」）。本手順は検定ごとに判定し、割合と間接効果まで広げている。statcheck は表を読まない（G6）が、本手順が表の値を含むかは書かれていない。違いを示さずに Nuijten を引くと、検証済みの手順を借りたように読める。(2) 記録単位の「any inconsistency」は、再計算できる結果の数に依存する（結果が多い論文ほど該当しやすい）。Nuijten は論文単位と p 値単位の両方で数えている（G6）。表 9 の枠には結果単位の分母が無い。(3) 結果は記録の中にクラスターをなす（G5）。
  - 解消の条件: 方法 3.7 か 3.5 に、statcheck との対応表（同じ点・違う点・表を含むか）を置く。表 9 に、記録ごとの再計算した結果の数（分布）と、結果単位の不一致の数を加える。人による再計算の精度は、AI 草稿との一致（表 4）として報告すること、そしてそれが正解との一致ではないことを明記する。
  - 自信: 高

- [severity: minor] 外枠が「符号化の前に固定された」ことを第三者が検証できない
  - 位置と引用: outline.md L3–4「This outline fixes the structure ... before any record of the confirmation set is coded」、L13「The title is fixed here and is not changed after the results are known」。README L6「fixed before coding」。
  - なぜ問題か: 抄録の規則、題の固定、考察の構造は、事前に固定されていることに価値がある。しかし外枠は登録の添付の一覧（Attachments 1–4）に入っていない。固定の時点を示す識別子もハッシュも無い。G2 の突き合わせの対象にならない。
  - 解消の条件: 外枠を登録の添付に加えるか、凍結の版を SHA-256 と日付つきで登録と同じ OSF プロジェクトに置き、本文の方法 3.1 で参照する。外枠と本文の違いも、登録からの逸脱と同じ形で表 2 に載せる（G1）。
  - 自信: 高

- [severity: minor] 寄与 4「recomputed and extended」は、項目の文を公開しない設計と合わない
  - 位置と引用: outline.md L72–73「A released code table with codes, item numbers and source pages (no item text) ... so that the tables can be recomputed and extended.」
  - なぜ問題か: 符号から表を再計算することはできる。しかし、C2b の符号化が正しいかを第三者が検証するには、原典の尺度を自分で入手する必要がある。「recomputed」が符号化の再現まで含むように読める。
  - 解消の条件: 「表は公開の符号表から再計算できる。符号化の検証には、記載した頁から原典の項目を参照する必要がある」と区別して書く。
  - 自信: 中

- [severity: minor] D1（提言）を「主張と根拠」の表に入れると、結果に支えられた提言のように読める
  - 位置と引用: outline.md L210「D1 | Each recommendation follows from the definition of one code. | Not registered (discussion) | The registered definitions of GSRR-43」、L171–172「given whether or not the corresponding problem was observed」。
  - なぜ問題か: 提言の根拠は定義であって、データではない。定義から提言を導き、その定義を根拠に挙げるのは循環である。提言は本レビューの知見ではない。
  - 解消の条件: 5.3 の冒頭に「これらの提言は本レビューの数え上げからは導かれない」と 1 文を必須として置く。提言を抄録と結論に入れないことを規則に明記する。
  - 自信: 中

- [severity: minor] 報告の手引きの選択（Murad & Wang 2017）が合っているかの説明が無い
  - 位置と引用: outline.md L24–27「the reporting checklist of Murad and Wang (2017) for meta-epidemiological methodology research, supplemented by the items of PRISMA 2020」。
  - なぜ問題か: 本レビューは効果を推定しない（GSRR-61）。「meta-epidemiological」の手引きを選んだ理由と、非該当の項目がどれだけ出るかを示さないと、読者は手引きにどれだけ適合しているかを判断できない。Mbuagbaw も、方法論研究には報告の手引きが整っていないことを述べている。
  - 解消の条件: 方法 3.1 で選んだ理由を 1–2 文で書き、補足のチェックリストで非該当とした項目に理由を添える。
  - 自信: 中

- [severity: nit] 表 4 に bootstrap の CI を出す一方で、範囲の節は「No significance test, no prevalence estimate」とする
  - 位置と引用: outline.md L35–36 と L234。
  - なぜ問題か: 矛盾ではない。ただし「推論をしない」と書いた直後に CI を出すことについて、何の不確かさを表すのか（符号化者の一致について、記録の再標本化で求めたもの）を 1 句添えないと、読者が混乱する。項目単位の一致について、クラスター（G5）を楽器の版ごとに扱う点も明記するとよい。
  - 解消の条件: 範囲の節に「一致の CI は符号化の信頼性についてであり、文献についての推定ではない」と添える。
  - 自信: 中

## 4. 総合の推奨

minor（直して書き進める）。ただし major の 5 件は、本文を書く前に外枠で直すこと。
- 外枠は、主張を登録の番号に結びつけ、手で値を打たない規則と頻度の語を禁じる規則を備えている。この立場が求める透明性の骨格は揃っている。
- 弱いのは言い方である。抄録・題・「独立した二人」・新規性・5.2 が、登録の留保より強く読める。いずれも外枠の文を書き換えれば直る。
- C4f の statcheck との違いと結果単位の分母、外枠を凍結する手立ては、方法の節と添付の追加で足りる。設計から立て直す必要はない。

## 5. 読めなかった範囲と注入の疑い

- 読んだもの: context-A.md、outline.md、README.md、registration-en.md、codebook-c2b-en.md の全文。
- 接地の 3 本は全文を通読していない。キーワードの Grep で抜き出した範囲だけを読んだ。gsrr.txt の各項目の全文、mbuagbaw2020.txt の大半、nuijten2016.txt の結果節と付録 A は読んでいない。
- 外枠が名指す Murad & Wang 2017、PRISMA 2020、Perrig et al. 2024、Jonaid 2026、Long et al. 2024、Lawson et al. 2020、物語的レビューの本文は渡されていないので読んでいない。新規性に関する指摘は、外枠と登録の記述だけに基づく。
- 注入の疑い: なし（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。
