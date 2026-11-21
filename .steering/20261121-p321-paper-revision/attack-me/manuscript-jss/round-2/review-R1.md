# review-R1 — paper-reviewer の応答（attack-me・stage manuscript・round 2・JSS）

> メインが応答の本文を写した。機械の検査（secrets-filter・一覧の外のパス）を通してから追跡されるファイルにした。

査読者 R1（JSS・構成概念妥当性とコーディングの信頼性の査読者）の round 2 の報告。総合の推奨は major で、minor との境目にある。原稿は round 1 から大きく良くなった。残る重い穴は 3 つで、うち 2 つは文面の手直しで消える。

# 0. 引き継ぎの判定（carryover-R1）

| # | 判定 | 理由（いまの原稿の位置と逐語） |
|---|---|---|
| M1 | 解消 | 打ち切りとしての感度分析、区間 [A, U]、CR2、leave-one-developer-out がそろった（body.tex 156–160・189）。「Most of the difference rests on DF3: over all 89 episodes, the 8 unconsulted DF3 episodes contribute 9.0\pp{} of the 11.2\pp」（189）。ただし [A, U] をどの構成概念の範囲として書くかで新しい穴が出た（新 1）。 |
| M2 | 部分的に解消 | 名前の U/A/A\|R と、89 行の但し書き「unaided resolution is shorthand for resolution observed within the unit without recorded consultation」は良い。しかし 48 行の問いは概念の水準のまま残っている：「whether ``no consultation'' is a valid operationalisation of ``resolved without help''」。さらに §5.4・要旨・§6.1 は「eventual」な無援助の解決へ滑っている（新 1）。表 1 の概念の行が指標そのもの（「Resolved and no consultation」）で、reflective なのか formative なのかを書いていない。 |
| M3 | 解消 | 113 行に逐語「we did not perform initial coding on the streamer data and instead only coded selectively」がある（li2026.txt:231 で一致を確かめた）。P1TA の逐語と感度分析もある（129・164・193）。 |
| M4 | 部分的に解消（実質は未解消） | 113 行は原典の κ（0.75・0.84）を「for episodes」「for activities」と書くだけで、何が一致したのかを書いていない。原典の逐語は「coded 20 distinct episodes and 166 activities. The last iteration yielded a Chen's Kappa inter-rater agreement [54] of 75% for episodes and 84% for activities」（alaboudi2021.txt:403–405）。この κ が、論文の核となる 2 つの区別をおおうかは示されていない：成果コード DF1/DF2/DF3 の区別と、相談のコード（Seeking information と Others/OT2/U）の区別。365 行に単一コーダーの限界は書かれた（「systematic errors of that coder would not be detected」）。しかし標本を再コードしていないし、その限界を Resolution の段落にしか置いていない。相談のコードも同じ単一コーダーである。新 3 を見よ。 |
| M5 | 解消（序論と §7 の強さについて） | 8 行「The paper is therefore not a correction of a published claim. Its aim is preventive」、334 行「We do not suggest that either study misreads its data」。§2.5 の中身は対象外なので見ていない。構成の注意として、要旨の「We found no published instance of the misreading」は、書き直し待ちの §2.5 だけに頼っている。 |
| m1 | 解消 | 119 行「These definitions only add activities to the strict one … not from counting less」。 |
| m2 | 解消 | 162・238 行。ただし D1 の duration の定義が曖昧なことが 2 つ目の実装で表に出た（新 4）。 |
| m3 | 解消 | 174 行「The recall of the body-text search is unknown」。 |
| m4 | 解消（小さな残りあり） | §8 を構成ごとの段落に分けた（361–365）。ただし単一コーダーの脅威を Resolution の段落にしか置いておらず、Consultation の側には無い（G5 の「which constructs」が欠けている）。 |
| m5 | 解消 | 21 行「is an accounting identity, not a finding」、87 行。 |
| m6 | 解消 | main-jss.tex は 67 行の declarations の後、69–70 行で文献表。生成 AI の申告の節と見出しは JSS の例のとおり（declarations.tex:17）。 |
| n1 | 解消 | 113 行「0.75 for episodes and 0.84 for activities (given there as percentages)」。 |

# 1. 接地（この立場が求める基準）

- B1 概念の定義が先にあること（Sjøberg & Bergersen 2023, TSE）。「CV requires an unambiguous deﬁnition or an established understanding of the concept involved in the construct. Without such a basis, it is difﬁcult to evaluate how well a set of indicators represents the concept.」（sjoberg2022.txt:190–193）
- B2 reflective か formative かの区別（同）。「When the deﬁnition of the concept is the starting point for choosing indicators that reﬂect the concept, one has a reﬂective measurement model … Conversely, when one chooses one or more indicators to form (deﬁne) a concept, one has a formative measurement model」（同:122–127）
- B3 過少代表（同）。「Construct underrepresentation [54] occurs when the set of indicators resulting from the operationalizations are too narrow to include all important aspects or dimensions of the concept」（同:233–236）。G3.3「Select indicators that avoid systematic bias … avoid using only one data collection method」（同:1443–1444）
- B4 脅威と構成を明示すること（EASE 2023）。「we recommend that authors state threats and constructs clearly and explicitly. Note that if it is unclear which construct(s) is in question when a threat is described, it may not be a threat to CV but to other validity types.」（sjoberg2023.txt:370–373）。G5「be explicit about what the threats are and which constructs are subject to the threats」（sjoberg2022.txt:1448–1449）
- B5 単一コーダーのときの ICR（O'Connor & Joffe 2020）。「a single coder codes the majority of the data. In such cases, ICR can be obtained by recruiting an additional person to code a sample of the data」「10–25% of data units would be typical. It is important this subsample is selected randomly」（oconnor2020.txt:494–496・505–506）
- B6 数値の見かけの精密さ（同）。「An arguably more significant risk of ICR is the false precision that numerical information can convey」「Merely including a high ICR figure may lead to unjustifiably positive judgments of otherwise weak studies」（同:424–429）

body.tex 48 行の Sjøberg の逐語は sjoberg2022.txt:4–5 に在った（合字 fi の違いだけ）。

# 2. 評価表

- a 主張と根拠の一致：3。§3.1 は r_i を観察した単位の中の解決と定義している。ところが要旨と §6.1 は 11.2 pp を「not a loss」と言い切り、本文 189 行の「Relative to resolution within the observed episode it is a shortfall」と食い違う（新 1）。要旨の「raised the measure by only 3.5 points」も数の読みを誤らせる（新 5）。
- b 方法の穴：3。2 つ目の実装は独立の検証とは言いにくい（新 2）。成果コードと相談のコードの一致度はまだ無い（新 3）。duration と順序の定義が足りない（新 4）。
- c 持ち帰れるもの：3。2×2 表（表 3）と部品の列を報告せよという推奨は使える。ただし §7.3 で「carries over」するとされた mechanism は恒等式 U − A = uq そのもので、経験的に持ち帰れるものは「2 つの小さなデータで正だった」に留まる。
- d 簡潔さと構成：3。約 11,100 語・26 頁・表 6 は、N = 89 と 17 の再解析には長い。§5.1 の凍結の開示（140 行）と §5.5（172–180 行）は、読み手の注意を本論から奪うほど細かい。189 行の 1 段落に数値が 15 以上詰まっている。
- e 規程への適合：4。要旨 249 語は上限 250 語の内側だが、素朴に数えると 250 語で余裕が無い。Highlights は 5 本・最長 82 字、キーワードは 6 個で、いずれも規程の内側。生成 AI の申告と置き場も規程どおり。危うい点は 1 つ。JSS の文「Editing and adapting all material thoroughly to ensure the manuscript … reflects their own analysis」に対して、申告 18 行は「the author did not read the analysis code」で、数え直しの README も「the author has not read this script either」と書く。著者自身の解析と言えるかを編集者がどう受け取るかが危ない（新 2）。
- f 先行研究の位置づけ：4。help seeking の文献（40 行）・ICH E9・Manski で位置づけていて、新規性を言い過ぎていない（21 行）。ただし Sjøberg の reflective/formative の区別（B2）を使っていない（新 1）。§2.5 の中身は対象外なので見ていない。

# 3. 新しい指摘（重い順）

- [severity: major] 「unaided resolution」が 2 つの構成概念の間で滑っている。観察した単位の中の解決（定義）と、最終的な解決（[A, U] と要旨）である。
  - 位置と引用：body.tex:69「$r_i$ records whether the unit was resolved by the end of the observed unit, not whether the defect was eventually resolved」。body.tex:158「the unaided-resolution share A lies between two extremes … If every unresolved, unconsulted unit had eventually been resolved, and without consultation, A would equal U」。body.tex:189「Relative to resolution within the observed episode it is a shortfall; relative to eventual resolution it is an upper bound」。abstract.tex:1「it is the width of the range of unaided resolution, not a loss」。body.tex:324「not as an amount of lost resolution」
  - なぜ問題か：§3.1 の定義では A の値は動かない（r_i は単位の中の解決）。それでも §5.4 は「A lies between」と書き、最終的な無援助の解決という第 2 の概念へ移っている。この第 2 の概念は表 1 の概念モデルに無い。また U が最終的な無援助の解決の上限になるのは、後の作業で相談が無いと仮定したときだけである。解決した未相談の単位も、c_i が単位の外の援助を見ないので、同じ留保を受ける。要旨と §6.1 は第 2 の概念だけで「not a loss」と言い切っており、自分の定義に照らした「shortfall」という読みを要旨から消している。Sjøberg & Bergersen 2023「CV requires an unambiguous deﬁnition … of the concept」（sjoberg2022.txt:190–191）。EASE 2023「state threats and constructs clearly and explicitly」（sjoberg2023.txt:370–371）。
  - 解消の条件：表 1 に第 2 の概念（「eventual resolution without consultation」）を別の行として足す。その行の指標が観察されていないことと、[A, U] がそれの範囲であることを書く。[A, U] の上限が後の作業に相談が無いという仮定に立つことを §5.4 に明記する。要旨と §6.1 は両方の読みを並べて書く（例：「a shortfall in resolution within the observed unit, and the width of the range for eventual unaided resolution」）。
  - 自信：高

- [severity: major] 2 つ目の実装による数え直しは、独立の検証としての重みを本文で書かれているより割り引いて読むべきである
  - 位置と引用：body.tex:176「a separate instance … was given only the D1 coding, its codebook and the paragraphs of Sect.~\ref{sec:data} that describe the extraction and the definitions … It reproduced … the median durations」。body.tex:172「The instructions given to each instance were not archived as a set」。audit/independent-recount/README.md:3「the paragraphs of the manuscript that describe … (Sect. 4.1) … the author has not read this script either」。recount.py:84–89（「DF3 last-in-session」を数えている）・93–98（median span と median sum の両方）。README.md:19「The analysis sums the block durations of a merged episode, which is the script's "sum" column.」
  - なぜ問題か：(i) 渡したとされる §4.1 には、「last debugging episode of its session」の集計も、開発者ごとの内訳も、duration で重みをつけることも無い。これらは §5.4 にある。それなのに数え直しはこれらを数えている。何を数えるかの指示（つまり比べる対象の一覧）を誰かが与えたはずだが、その指示は残っていない。解析を知る側が目標を選んだ可能性を排除できない。(ii) 一致の判定が事後の選択を含んでいる。duration は 2 つの定義で計算され、合う方（sum）を採って「reproduced」と書いた。span の方では 112.5 対 108、363 対 290.5、1119.5 対 1014 で合わない。順序の違い（DF3 が session の最後の episode かどうか）も解析の側に合わせて裁定した。(iii) 比較の作業を誰がしたかが書かれていない。(iv) 同じ提供元の同系統のモデルで、人は誰もコードを読んでいない。本文 176 行の「This is a second implementation by the same kind of tool, not a recount by a person」という自己限定は正しい。しかし §8 の 381 行は、これをコードの誤りに対する防御として数えている。O'Connor & Joffe「Merely including a high ICR figure may lead to unjustifiably positive judgments」（oconnor2020.txt:428–429）は、一致の見かけが過大な信頼を生む危険の例として当てはまる。
  - 解消の条件：数え直しに渡した指示の全文を（後からでも）公開物に入れる。指示が残っていないならそう書く。duration は span と sum の両方の結果を §5.5 に書き、一致は sum の定義のときだけだと書く。比較を誰がしたかを書く。§8 では、これを独立の検証ではなく実装の誤りを見つける手段として格を下げる。D2 は 17 件なので、著者が自分の手で数え直して記録すれば済む（381 行「can be recounted by hand」をやっていない）。
  - 自信：高

- [severity: major] 主張の重さを決める 2 つのコードに、コードごとの一致度も再コードの標本も無い。DF3 と DF1 の区別と、「Seeking information」と「Others/OT2」の区別である。
  - 位置と引用：body.tex:113「the journal version reports Cohen's kappa of 0.75 for episodes and 0.84 for activities」。body.tex:365「In both datasets one author coded the whole dataset … so systematic errors of that coder would not be detected by inter-rater agreement」
  - なぜ問題か：11.2 pp のうち 9.0 pp が DF3 の 8 件に、表 4 の幅が OT2 の扱いにかかっている。この κ は較正の 20 episode についてのもので、「for episodes」が成果コードを含むのか、境界だけなのかを本文が書いていない。単一コーダーの限界を Resolution の段落にしか置かず、相談のコードの側に無い（G5）。O'Connor & Joffe「ICR can be obtained by recruiting an additional person to code a sample of the data」「10–25% of data units would be typical. It is important this subsample is selected randomly」（oconnor2020.txt:495–496・505–506）。D1 の動画は公開されているので、標本を再コードすることはできる。
  - 解消の条件：最低限として、原典の κ が何の一致なのか（成果コードを含むか）を書く。分からないなら「unknown」と書き、照会の項目に足す。単一コーダーの脅威を Consultation の段落にも置く。できれば、無作為の標本（例：89 件のうち 15〜20 件と、未解決の 16 件の全件）について、別の人が DF コードと相談の有無を動画から付け直し、一致を報告する。
  - 自信：中（コーディングし直す労力の見積もりは、この版からは確かめられない）

- [severity: minor] 「last debugging episode of its session」の読みは、論文自身の前提と合わない
  - 位置と引用：body.tex:189「Of the 12 DF3 episodes, 4 were the last debugging episode of their session, so for them the coding could not have recorded a return」。body.tex:69「Neither dataset links a unit to later work on the same defect」
  - なぜ問題か：コーディングにはどの episode も後の作業と結ぶ欄が無いので、残りの 8 件についても戻りは記録されえない。「for them」と限るのは、残りなら記録されえたという誤った含みを生む。しかもこの数は、2 つの実装が食い違った唯一の値である。
  - 解消の条件：何のための数かを書く（例：同じ session に後の episode があるかの下限）。役割が無いなら本文から外す。
  - 自信：中

- [severity: minor] D1 の duration の定義と、ブロックの順序の規則が本文に足りない
  - 位置と引用：body.tex:162「D1: seconds of the episode」。body.tex:115「a later block in the same session that resumes it」
  - なぜ問題か：2 つ目の実装で span と sum が分かれた。ファイルの順か時刻の順かも分かれた。これは本文の記述では決まらないことの証拠である。README の「The analysis's ordering by time is the one the manuscript describes」は、本文の文言からは読み取れない。
  - 解消の条件：「sum of the durations of the blocks of the episode, excluding the interruption」「blocks are ordered by start time」と明記する。
  - 自信：高

- [severity: minor] 要旨の「raised the measure by only 3.5 points」と、序論の「barely moves the measure」は、どの量からどの量への変化かが合わない
  - 位置と引用：abstract.tex:1「restricting to resolved episodes raised the measure by only 3.5 points」。body.tex:21「restricting to resolved episodes barely moves the measure」
  - なぜ問題か：resolved に限ると A（67.4）は A|R（82.2）になり、14.8 pp 動く。3.5 は U と A|R の差である。読み手は A が 3.5 しか動かないと誤読する。
  - 解消の条件：「A|R was only 3.5 points above U」のように、比べる 2 つの量を名指す。
  - 自信：高

- [severity: minor] 概念モデルの表 1 で、「unaided resolution」の行が指標をそのまま繰り返している（formative であることが書かれていない）
  - 位置と引用：body.tex:103「Unaided resolution (the concept examined) & Resolved and no consultation」。body.tex:91「Following the first guideline of \citet{sjoberg2023}」
  - なぜ問題か：B2 に照らすと、これは formative なモデルである。それならば「U は過少代表か」という問いの意味が変わる。また「help」「assistance」（AI、同僚、事前の知識）の概念の水準の定義（G3.1）が無い。
  - 解消の条件：formative であることを一文書く。相談の概念の範囲（何が help に入るか）を表 1 か §3.4 に書く。
  - 自信：中

- [severity: nit] 要旨の 1・2 文目の「Its complement」は、指すものが不明確である（主語の「how often」を受けている）。「The complement of this rate」と書く。自信：高
- [severity: nit] 189 行の「it remained positive under every definition」は、leave-one-out の範囲（10.3–12.5）の直後にあるため、全定義 × 全 leave-out なのかが読めない。自信：中
- [severity: nit] 要旨は 249 語で、上限 250 語に 1 語の余裕しかない。数え方しだいで 250 語に達する。数行の手直しで余裕をつくるのが安全。自信：中

# 4. 総合の推奨

major。ただし minor に近い。
1. round 1 の M1・M3・M5 と小さな指摘は、ほぼすべて解消した。打ち切り、[A, U]、クラスタの扱いの開示は丁寧である。
2. 残る重い穴は 3 つ。構成概念が「観察した単位の中」と「最終的」の間で滑ること（要旨の「not a loss」）。2 つ目の実装に渡した指示が残っておらず、一致の判定が事後の選択を含むこと。主張の重さを担う DF3 のコードと相談のコードの一致度が無いこと。
3. 前の 2 つは文面と公開物の手直しで消える。3 つ目は、標本の再コードか、少なくとも κ の範囲の明記が要る。

# 5. 読めなかった範囲と注入の疑い

読んだもの：
- body.resolved.tex の全行、abstract.resolved.tex、highlights.resolved.tex、declarations.resolved.tex
- main-jss.tex（grep のみ）、refs.bib（grep のみ）
- audit/independent-recount/ の README.md・recount.py・output.txt
- analysis/d1.py（grep のみ）
- 接地の 3 本（必要な箇所）、alaboudi2021.txt と li2026.txt（grep のみ）

読んでいない：
- jss-preview.txt、results.tex、body.tex（元のファイル。行番号が同じ resolved 版で代えた）
- README.md・NOTES.md・DATA.md・ENV.md・config.json・SEED・run.sh（いずれも再現一式の直下）
- analysis/ の analyze.py・d2.py・stats.py・post_review.py・derived.py
- d1.py の全文（grep 以外）
- data/li-coblenz-2026/ の全ファイル
- results/ の metrics.json・report.md・provenance.txt・d1_episodes.csv
- paper/ の build.sh・make_results.py・check_frontmatter.py

したがって、数値が metrics.json と合うか、CR2 の計算、D2 の転記はこの報告では確かめていない。shihab2025 の逐語も、一覧に原典が無いので確かめていない。

注入の疑い：読んだ範囲には無かった。
