# 査読: *When "no help" is not "solved"*（EMSE・投稿済み原稿・round 1）

立場: IDE の中での debugging の実際の振る舞いと、プログラマーの助けの求め方を観察・記録して、道具の設計や教育に生かしてきた研究者（HCI・計算機教育を含む）。批判的な下位人格として、実務家と冗長さに厳しい読者を兼ねる。実在の個人は名乗らない。

## 1. 接地（この立場が論文に求める基準）

- **G1 知見を具体的な受け手の行動に結びつける**（Beller et al. 2018, beller2018.txt:119-122）: "Knowledge on how developers debug can help researchers to invent more practice-relevant techniques, educators to improve their debugging curricula, and tool builders to tailor debuggers to the actual needs of developers." 貢献にも同じことを求めている（:145-146）: "Improvement suggestions for current IDE debuggers that have in part already been implemented in practice."
- **G2 食い違いを報告するだけで終えず、説明しに行く**（Beller 2018, :156-160）: "We came up with a list of several, sometimes conﬂicting, observations that needed further explanation. 3⃝ To help us explain the ﬁndings in depth, we conducted interviews with developers"
- **G3 回数だけでなく時間でも測り、先行研究の主張と突き合わせる**（Beller 2018, :1124-1126）: "Developers spend surprisingly little time in the debugger; only 13% of their total development time on average, in stark contrast to previous ﬁndings claiming more than 50%."
- **H1 助けを求めない率を失敗という条件で読み直し、先行研究の読み方に含意を引く**（Hellas et al. 2023, hellas2023.txt:859-870）: "We checked whether this could be due to students’ mostly submitting correct sol utions, but that was not the case" ／ "the vast majority of prior r esearch has not explicitly collected information on whether studen ts want help"（抽出テキストの空白の乱れは原文のまま）
- **H2 求めないことの中身（他の情報源・断念・離脱）を書き分け、検出と支援の研究につなげる**（Hellas 2023, :880-891）: "Some stud ents will have needed help but decided not to ask for it." ／ "Instead of seeking help, students m ay also resort to plagiarism [26] or simply drop out [64]." ／ "Future research should seek to detect when students need hel p in order to provide timely feedback"
- **H3 含意を名指しした読者に向けて書く**（Hellas 2023, :56-58）: "Our study informs teach- ers interested in using LLMs as well as future eﬀorts to custo mize LLMs for the needs of programming education."

## 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 数値は表と本文で合っている（D1: 10/89、q=10/16、RQ3 の 7/10・12/79、p0=(10/12)^12 などを検算した）。慎重な留保も多い。ただし次の 4 点がずれている。(1) 題が R0 を "self-resolution measure" と呼ぶが、本文は誰もそう使っていないと認めている。(2) 要旨の結びの "both measures" が 3 指標のうちどれを指すか分からない。(3) 単位が違うので比べないと言った D1 と D2 を、条件づけの効果の範囲として 1 つにまとめている。(4) 「D1 は観察の終わりで切れない」という対比を、検証しないまま置いている |
| b 方法の穴 | 3 | 計算の再現性（ハッシュ・自己テスト・バイト一致）と、凍結の前に何を知っていたかの開示は、模範的と言ってよい。穴は振る舞いの側にある。未解決で相談なしの 10 件が配信の終わりと重なるか確かめていない。開発者ごとの偏り（k）を示していない。時間で重みをつけた版が無い。RQ4 について原著者に問い合わせたという記述が無い。LLM による文献探索は、探索語もデータベースも書かれていない |
| c 持ち帰れるもの | 2 | 中心の数値は 2×2 表の 1 つのセル（b/N）である。4 つの提言は「報告せよ」という一般論にとどまり、うち 1 つは D1 がすでに満たしている（l.327）。観察研究を設計する人、データを再利用する人、道具を評価する人のそれぞれが明日から何を変えるかが書かれていない（G1・H3 に届かない） |
| d 簡潔さと構成 | 2 | 4 つのセルに対して名前つきの量が 6 つある（R0・R0′・R1 と 3 つの効果）。2×2 の表そのものは載っていない。D2 の「観察の終わり」は 5 回、区間が狭すぎることと凍結の前に値を知っていたことはそれぞれ 2 回、臨床試験の類推は 3 回出てくる。Shepperd らの論争に触れる段落は、消しても主張が弱くならない |
| e 規程への適合 | 4 | 要旨は 234 語（150〜250 の範囲内）、キーワードは 6 個（4〜6）。LLM の利用は Methods の §5.5 にあり、Data availability もある。ただし規程は "Please use the title page for providing the statements." と言うのに、声明は原稿の末尾にしかない（context-A の補足の事実による）。D1 のデータへのリンクは figshare の `/s/` 形式である |
| f 先行研究の位置づけ | 2 | 参考文献 21 件のうち debugging は 3 件（D1 の 2 版と D2）。臨床と統計は 9 件。debugging の行動研究（Beller 2018 を含む）、プログラミングでの情報探索（information foraging）、中断からの再開、学習での助けの求め方の文献がほぼ無い |

## 3. 指摘（重い順）

### [major] 動機にした誤読が、実際に起きている例として示されていない。中心の結果は 2×2 表の 1 セルである
- 位置と引用: main.tex:55「That reading is attractive whenever published observational data are reused as a reference point, for instance for how often developers get through a defect unaided.」／:57「The original debugging studies, moreover, report consultation descriptively and do not present its complement as a measure of self-resolution.」／:81「Neither study presents the share ... as a measure of self-resolution. Our concern is with how that share behaves when it is reused as one.」／:179「its numerator effect motivated this study」
- なぜ問題か: 「相談なしを自力で解決したと読む」誤りを犯した論文や評価が 1 本も挙がっていない。§2.5 の探索も、この批判の先例を探しただけで、誤用の実例は探していない。誤用の実例が無いと、R0−R0′ は定義からして b/N（未解決かつ相談なしの割合）に等しいので、主結果は「89 件のうち 10 件が未解決で相談なしに終わった」という 1 つの数に縮む。Hellas 2023 は低い依頼率を失敗という条件で読み直したうえで、"some earlier ﬁndings about student ‘failure’ may in fact be related to students employing the submission system as a f eedback mechanism"（:870-872）と、具体的な先行研究の読み方に含意を引いている（H1）。本稿にはこの「誰の、どの読み方が変わるか」が無い。加えて、著者自身の先の探索的分析が何の問いのために R0 を計算したのか（l.179）が読者に伝わらない。これこそが具体的な再利用の場面だったはずである。
- 解消の条件: 次のどちらかを満たすこと。(a) R0（または相談率の補数）を、道具や AI 支援の比較の基準、あるいは自力で解決する率として再利用した実例を 1 件以上引用し、本稿の補正でその数がどれだけ動くかを示す。(b) 実例が無いなら、題と序論を「結果の符号化を伴わない観察データを再利用するときの報告指針」へ位置づけ直し、主結果を「未解決かつ相談なしの割合（D1 で 10/89）」と平易に言い直す。いずれにしても、先の分析が何に使われたかを 1 文で書く。
- 自信: 高

### [major] 未解決かつ相談なしの 10 件が、振る舞いとして何なのかを調べていない（DF3 と配信の終わりの関係・時間・開発者ごとの偏り）
- 位置と引用: main.tex:204「8 ended with the developer going to return later (DF3) ... its eventual outcome is unknown.」／:44（要旨）「an episode ends when the defect is fixed or when the developer stops, and in one of them also when observation ends」
- なぜ問題か: 配信のセッションで「後で戻る」と言うのは、多くの場合は配信の終わりである。もし DF3 の 8 件が各セッションの最後の debugging ブロックで、配信の終わり近くに終わっているなら、D1 の「未解決」も実質的には観察の打ち切りになる。そうすると、要旨と §4.2 が D1 と D2 の間に引いた対比が崩れる。D1 の符号化にはブロックの時刻とセッションがあるので、これは確かめられるはずである（ただし私は生データを見ていない）。さらに、回数だけでは 2 分の修正と 2 時間の断念が同じ 1 件に数えられる。Beller 2018 は時間で測ることで先行研究の主張を覆した（G3）。また、p0=0.0% から k は 6 以上と逆算できるが、D1 の 10 件が何人の開発者から来ているかは本文に無い。Beller 2018 は食い違いを説明しに行った（G2）が、本稿は 10 件を量として報告するだけで、何が起きていたかを示さない。
- 解消の条件: DF3 の各件について、セッションの最後のブロックかどうかと、セッションの終わりまでの時間を表にする。10 件の継続時間と、debugging の総時間に占める割合（時間で重みをつけた numerator effect）を載せる。開発者ごとの件数（k と分布）を載せる。配信の終わりと重なるなら、D1 の「未解決」も打ち切りを含むと明記し、要旨の対比を直す。
- 自信: 中（データの中身を見ていないので、重なるかどうかは分からない。確かめられないままでいる点は確かである）

### [major] 提言が、名指しした 3 種類の読者にとって明日から使える形になっていない
- 位置と引用: main.tex:322-329「For studies whose units can end without resolution, and for reanalyses that reuse such data, we recommend: ... Report the outcome-agnostic share ... together with the outcome-requiring share」／:327「D1's codebook already records most of these distinctions」
- なぜ問題か: 4 項目とも「報告せよ」で終わっていて、本質は「結果×相談の 2×2 表を、結果を細かく分けて載せよ」の 1 項目に畳める。しかも提言 3 は D1 がすでに満たしている。観察研究を設計する人に向けた具体策が無い。たとえば、エピソードが終わった理由を研究者が記録する、配信や観察の終わりを独立のコードにする、DF3 の件を後のセッションの同じ欠陥に結びつける、画面上の相談も（発話だけでなく）符号化する、といったことである。データを再利用する人には、D1 と D2 がそれぞれ何に使えて何に使えないかの判断表が無い。道具を評価する人（いま最もありそうな再利用は AI 支援の基準値）には、IDE の中の AI 支援を「開発環境の外の相談」（D1 strict、l.160）の定義にどう入れるかの指針が無い。D2 では "web sources" に AI が入っている（l.346）にもかかわらずである。G1・H3 の水準では、受け手ごとの含意が求められる。
- 解消の条件: 提言を受け手別に書き直す（設計する人／再利用する人／評価する人）。各項目に、D1 と D2 で何を変えればよかったかを 1 例ずつ添える。2×2 の表（4 つのセルと、結果のコードごとの内訳）を、報告の最小形式として本文の表に載せる。IDE の中の AI 支援の扱いを 1 項目に加える。
- 自信: 高

### [major] 3 つの指標と 3 つの効果の名前が、読者に負担をかける
- 位置と引用: main.tex:108「\Rz = \frac{a+b}{N}, \qquad \Rzp = \frac{a}{N}, \qquad \Ro = \frac{a}{S}」／:116-118「conditioning effect ... numerator effect ... denominator-only effect」／:44「We recommend reporting both measures and the unresolved, unconsulted share separately.」
- なぜ問題か:
  - R0′ はプライムのせいで R0 の変種に見える。だが実際に分子を共有しているのは R1 である。再現一式の README:9-11 では R1 が R0′ より先に並んでおり、記号の順序が自然でないことを示している。
  - "numerator effect" は "the unresolved, unconsulted share"（要旨と提言 2）と同じ量で、名前が 2 つある。
  - "denominator-only effect" は、R1≈R0 となる理由を説明するためだけにある量で、報告を勧められてもいない。
  - "effect" という語は因果を連想させる。
  - 4 つのセルに 6 つの名前があり、要旨で 3 指標を定義しておきながら結びでは "both measures" と書いている。
- 解消の条件: 記号より内容を表す名前を主にする（例: unconsulted share / unaided-resolution share / unaided-resolution rate among resolved / unresolved-unconsulted share）。"effect" は "difference" か "gap" に替える。denominator-only の行は表から外し、l.256 の q と R1 の比較（37.5% 対 17.8%）で説明する。要旨の "both measures" を具体名に直す。
- 自信: 高

### [major] debugging と助けの求め方の先行研究がほとんど無い
- 位置と引用: §2（main.tex:73-99）。refs.bib のうち debugging の文献は alaboudi2021・alaboudi2023・li2026 だけ。:99「Within that search we found no study that applied the critique ...」
- なぜ問題か: 本稿が想定する読者（debugging の行動研究）に向けて位置づけるには、少なくとも次の系統が要る。私の知識による挙示なので、書誌は著者が確かめること。
  - IDE での debugging の振る舞いの現場研究: Beller et al. 2018, ICSE。debugging の区間を測るが、欠陥が直ったかは符号化していない（本文に結果の符号化の記述は見当たらない）。つまり R0′ が計算できないデータの例で、提言 3 が最も効く場所である。
  - debugging を情報探索として見る研究: Lawrance et al. 2013, TSE "How programmers debug, revisited"。プログラミング中の web 探索: Brandt et al. 2009, CHI。開発者の web 探索: Xia et al. 2017, EMSE。チームの中の情報の必要と同僚への相談: Ko, DeLine & Venolia 2007, ICSE。
  - 中断と再開（DF3 の解釈に直結する）: Parnin & Rugaber 2011／Parnin & DeLine 2010。
  - 学習での助けの求め方と回避: Aleven et al. 2003, RER。プログラミングでの要因: Price et al. 2017, ICER。助けを求めないまま進めない状態（wheel-spinning）: Beck & Gong 2013, AIED。
  - 実務家に debugging を課して成否と時間を測った研究: Böhme et al. 2017, FSE（DBGBench）。

  LLM による探索が約 30 件で、これらに当たっていない。このことは、新規性の主張（l.99）の重みを下げる。
- 解消の条件: 上の系統を §2 に入れる。「相談」を、助けの求め方（社会的な援助）と情報探索のどちらの概念として扱うかを明記する。DF3 と未解決かつ相談なしの件を、再開の研究と wheel-spinning の研究に照らして 1 段落で解釈する（H2）。探索の語・データベース・日付・採否の基準を付録に載せる。
- 自信: 中（個々の文献の存在と内容は私の記憶による。欠けていること自体は refs.bib で確かめた）

### [major] RQ4（他の EMSE 論文の数値を再現する監査）が主題から外れており、原著者との照会も書かれていない
- 位置と引用: main.tex:284「We could not determine how the journal version's figures were obtained; the same data may have been aggregated differently, which we cannot rule out.」／:335「we hope that publishing the reproduction table item by item, rather than a single verdict, keeps the discussion about the figures.」
- なぜ問題か: numerator effect は 4 つの定義のどれでも 7.9〜11.2 に収まる（l.234）。したがって RQ4 の結果は主題の結論を動かさない。それでいて、紙幅（表 5・§6.4・§2.4 の論争の段落）と、要旨の 1 文を占めている。再現の報告では、原著者に問い合わせてその返答を載せるのが通例である。single-blind で原著者が査読者になりうるだけに、「照会したかどうか」が書かれていないのは突かれる。
- 解消の条件: 原著者への照会とその結果（返答が無かったことを含む）を書く。RQ4 を付録か短い節に移し、§2.4 の Shepperd の段落と §6.4 の後半を 2 文に縮める。
- 自信: 中

### [minor] 題が R0 を「self-resolution measure」と呼ぶが、本文はそう使われていないと認めている
- 位置と引用: main.tex:34「outcome-agnostic self-resolution measures in two public debugging datasets」と :81「Neither study presents ... as a measure of self-resolution.」
- なぜ問題か: 2 つのデータセットに自力で解決した率の指標があるように読める。
- 解消の条件: 題を、相談の割合と、相談なしで解決した割合の違いを述べる形に直す。
- 自信: 高

### [minor] 比べないと言った 2 つのデータセットを、1 つの範囲にまとめている
- 位置と引用: main.tex:256「Across all 10 combinations of definitions in both datasets, the conditioning effect ranged from −8.6pp to −2.5pp」と :208「The two datasets differ in unit, size and the meaning of "unresolved" ... we do not claim that D2 replicates D1」
- なぜ問題か: 「未解決」の意味が違う 2 つのデータセットを 1 つの範囲で語っている。
- 解消の条件: D1 と D2 の範囲を分けて書く。
- 自信: 高

### [minor] 「未解決」と「解決」の中身がそれぞれ不均一なのに、感度分析に入っていない
- 位置と引用: main.tex:158「DF5 (the developer cannot reproduce the issue)」が主定義で未解決に入っている。:327「D2's tables record only resolved or not」
- なぜ問題か: debugging の実務では、再現できない欠陥は「再現できない」として閉じることがあり、失敗と同じに扱うのは疑わしい。D2 の P1TA は、li2026.txt:342 によれば "discovered that the bug had already been fixed in the latest patch, skipping the fix construction step" で、それでも Resolved=Y である。D2 の「解決」にも中身の違いがあるが、本稿は触れていない。
- 解消の条件: DF5 を除外する感度分析を 1 行加える。P1TA のような件を提言 3 の例に挙げる。
- 自信: 中

### [minor] 繰り返しと類推が多く、消しても主張が弱くならない段落がある
- 位置と引用:
  - D2 の観察の終わり: l.168、206、314、350、371
  - 区間が狭すぎること: l.185 と 362
  - 凍結の前に値を知っていたこと: l.179 と 362
  - 臨床の類推: l.89、314、331
  - Shepperd の論争: l.95 と 335-337
- なぜ問題か: 中心が 1 つのセルの論文としては、通常の組版で 21 頁は長い。
- 解消の条件: 各論点を 1 か所にまとめ、他の場所は参照で済ませる。§2.3 を 2 文にする。
- 自信: 高

### [minor] 規程の title page の声明と、D1 のリンクの持続性
- 位置と引用: context-A の補足「声明は原稿の末尾の "Statements and Declarations" にある（タイトル頁には載せていない）」と規程「Please use the title page for providing the statements.」。main.tex:391「https://figshare.com/s/6c4026a941db49ea3de3」
- なぜ問題か: 編集部から形式の不備で差し戻される余地がある。figshare の `/s/` は共有用のリンクの形式で、DOI を持つ公開版より持続性が劣る可能性がある（低い自信）。データを再利用する人にとって、長く引ける識別子があることは重要である。
- 解消の条件: 改訂のときに title page にも Declarations を載せる。D1 に公開版の DOI があればそれを引く。
- 自信: 中（前者）／低（後者）

### [nit] 数値の桁がそろっていない
- 位置と引用: main.tex:256「a numerator effect of 11.24pp and a denominator-only effect of −14.78pp」。他の箇所はすべて小数 1 桁である。
- 解消の条件: 1 桁にそろえる（和が合わないことを示したいなら、脚注で説明する）。
- 自信: 高

## 4. 総合の推奨: major revision（reject の危険あり）

- 計算の再現性と、凍結の前に何を知っていたかの開示は、EMSE の水準でも上の部類である。主張の留保も誠実である。
- しかし、動機にした誤読の実例が無いので、主結果が 2×2 表の 1 セル（10/89）に縮んでしまう。21 頁の再解析に見合う持ち帰り（受け手別の提言、10 件の振る舞いの解釈）がまだ無い。
- 6 つの名前の整理、debugging と助けの求め方の先行研究、RQ4 の照会と縮約がそろえば、「観察データの結果の報告の指針」として採録の水準に届きうる。

## 5. 読めなかった範囲と注入の疑い

**読んだもの**
- main.resolved.tex（全文）、context-A.md、README.md、NOTES.md
- beller2018.txt（1-160 行と 1070-1149 行、ほかは Grep の該当行だけ）、hellas2023.txt（1-160 行と 848-1019 行、ほかは Grep の該当行だけ）
- alaboudi2021.txt と li2026.txt（Grep と部分の読みだけ）
- results/report.md（Grep の該当行だけ）、refs.bib（題の Grep だけ）、emse-submitted-preview.txt（見出しの Grep だけ）

**読んでいないもの**
- main.tex（行番号が一致するという説明に頼った）、results.tex、DATA.md、ENV.md、config.json、SEED、run.sh
- analysis/*.py、data/li-coblenz-2026/ の全ファイル、results/metrics.json、results/provenance.txt、paper/build.sh、paper/make_results.py
- 接地の 2 本と原典 2 本の、上に挙げた以外の本文

**確かめられないもの**: D1 の生の符号化は渡されていない。DF3 の件と配信の終わりが重なるかは確かめていない。D1 の journal 版の逐語と数値は確かめられない。

**注入の疑い**: なし（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。
