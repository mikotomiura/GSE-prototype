# review-R2 — paper-reviewer の応答（attack-me・stage manuscript・round 2・JSS）

> メインが応答の本文を写した。機械の検査（secrets-filter・一覧の外のパス）を通してから追跡されるファイルにした。

査読者 R2（JSS・プログラミングの人間の側〔HCI・計算機教育〕・下位人格は実務家／冗長さに厳しい読者）・round 2・stage manuscript

結論を先に書きます。推奨は minor revision です。round 1 の major 6 件のうち 5 件は解消し、1 件（#3 提言）は部分的な解消です。新しい指摘で最も重いのは §7.3 の Hellas et al. (2023) の算術の誤りで、元の論文の数値から計算すると逆の結論になります。

## 0. 引き継ぎ（carryover-R2）の判定

- **#1 major（動機にした誤読の実例が無い）: 解消。**
  - body.tex:8 「We did not find a publication that reads debugging data in this way … The paper is therefore not a correction of a published claim. Its aim is preventive」。§7.3 にも「We do not suggest that either study misreads its data」がある。
  - 構成の注記（§2.5 の中身には触れない）: 序論は 8 行と 10 行の 2 か所でこの節を頼りにしている（「within the literature search described in Sect.~\ref{sec:related}」）。要旨も「We found no published instance of the misreading.」と、同じ節を根拠に言い切っている。§2.5 の書き直しでは、序論と要旨のこの 2 か所を同時に確かめる必要がある。
- **#2 major（未解決で相談の無い 10 件が振る舞いとして何か）: 部分的に解消。**
  - DF3 の寄与（189 行「the 8 unconsulted DF3 episodes contribute 9.0pp of the 11.2pp」）、k と開発者ごとの分布（「2/17, 2/17, 2/12, …」。2 つ目の実装の output.txt と一致した）、所要時間（238 行）、セッションの最後かどうか（「4 were the last debugging episode of their session」）がそろった。
  - 残る穴: 最後ではない DF3 は 8 件、そのうち相談の無いものは 6 件ある。これらについて、同じセッションで同じ欠陥に戻ったかが書かれていない。一方で 187 行は「the coding does not link it to later work」と言っている。そうなると「最後かどうか」を示す意味が読者に伝わらない（新指摘 5）。
- **#3 major（提言が明日から使える形でない）: 部分的に解消。**
  - §7.4 は受け手別になり、2×2 表（Table 3）が置かれた。設計する人への提言は具体的になった。
  - ただし再利用する人については、公表値が相談率だけのとき（いちばん多い状況）に何ができるかが書かれていない（新指摘 3）。道具を評価する人への提言は 2 文しかない。
- **#4 major（指標の名前の負担）: 解消。** U・A・A|R に名前が替わり、「effect」は使われていない。ただし差の名前が 3 つ（unresolved-unconsulted share・denominator difference・conditioning difference）あり、ほかに b/(a+b)・u・q が加わる。要旨にも 11.2 points と 14.3% の 2 つが並ぶ。負担は軽くなったが、ゼロではない。
- **#5 major（debugging と助けの求め方の先行研究）: 部分的に解消。**
  - 助けの求め方の文献（Karabenick・Marwan・Almeda・Hellas）と、中断の文献（Ko 2007・Parnin 2011）が入った。
  - debugging の観察研究は、いまも D1・D2 の原典だけである。IDE のログで debugging を観察した研究（例えば接地に使った Beller et al. 2018）が refs.bib に無い（新指摘 6）。
- **#6 major（RQ4 の位置と照会）: 解消。** Table 5 が「Structural figures」と「Consultation figures」に分かれた。報告値どうしの算術は 290 行にある（「22 of 89 episodes, or 24.7%, not 33%」）。照会の記述は 290 行「On 2026-11-21 we asked the original authors … at the time of submission we had not received a reply」。
- **minor（題）: 解消。** main-jss.tex:48 の題は「When ``no help'' is not ``solved'': unconsulted shares and unaided resolution …」。
- **minor（2 つのデータセットを 1 つの範囲にまとめていた）: 解消。** 236 行で D1 と D2 の範囲が分かれた。要旨の「by 7.9 to 11.2 points across eight definitions」も D1 だけの値である。
- **minor（「未解決」「解決」の中身が不均一）: 解消。** §5.4 に「Endings treated as censoring」と「P1TA in D2」が入り、結果は 189 行と 193 行にある。
- **minor（繰り返しと類推）: 未解消（むしろ悪化）。** 本文は約 11,100 語に増えた。次の 2 つの言い分が、それぞれ 5 か所ほどで繰り返されている（新指摘 2）。
  - 「区間は開発者のばらつきの記述で、符号の検定ではない」: 146・160・193・236・377 行
  - 「DF3 を打ち切りとみなす」: 156–158・189・324・365・390 行
- **minor（title page の声明と D1 のリンクの持続性）: 解消。** declarations.tex に JSS の形の声明が並び、Data availability に「the replication package also contains an episode-level table derived from that coding」とある。
- **nit（数値の桁）: 解消。** 260 行の脚注「These two values are given to two decimals so that they add up to the conditioning difference shown to one decimal.」

## 1. 接地（この立場が論文に求める基準）

- **G1 受け手ごとの持ち帰り。** Beller et al. 2018（§1）「Knowledge on how developers debug can help researchers to invent more practice-relevant techniques, educators to improve their debugging curricula, and tool builders to tailor debuggers to the actual needs of developers.」
- **G2 観察の単位の境界が、実際の作業と一致するかを問う。** Beller et al. 2018（§6 Construct Validity）「Debug sessions might not correspond to actual debug work, e.g. a user might have inadvertently left the debugger in the IDE running」
- **G3 一般化は、データが及ぶ範囲に留める。** Beller et al. 2018（§6 External Validity）「Other IDEs are not included in our analysis and the results with them might deviate.」。Hellas et al. 2023（§6）「The particular features of our context limit the generalizability of our findings.」
- **G4 記録の無い出来事は、その目的を知らなければ解釈できない。** Hellas et al. 2023（§5.5.1）「some earlier findings about student ‘failure’ may in fact be related to students employing the submission system as a feedback mechanism, not necessarily needing help but simply checking whether they are on the right path.」
- **G5 記録の外の助けの経路。** Hellas et al. 2023（§5.5.1）「Some students will have needed help but decided not to ask for it.」と「students may seek help from many sources, such as their peers or online services」

## 2. 評価表

- **a 主張と根拠の一致: 4。** 主張は全体に、観察された単位の中での話に絞られている（69 行・390 行）。崩れているのは 2 か所: §7.3 で Hellas の数値の読みを誤っていること（新指摘 1）と、2 つ目の実装が「results を見ていない」と書いていること（新指摘 4）。
- **b 方法の穴: 4。** 少数の開発者による限界は正直に書かれている（CR2・1 人ずつ外す計算・p0）。残る穴は 2 つ: 最後ではない DF3 の扱い（新指摘 5）と、block の順序が本文に書かれていないこと（新指摘 7）。
- **c 持ち帰れるもの: 3。** 2×2 表と [A, U] は実用になる。足りないのは 3 点: 公表値が相談率だけのときに何ができるか、道具を評価する人への具体性、26 頁に見合う持ち帰りの密度。
- **d 簡潔さと構成: 2。** 同じ但し書きが 4〜5 か所で繰り返される。§5.1 の凍結の開示（140 行）は 1 段落で約 400 語ある。結論（390 行）はほぼ RQ1 の再掲になっている。
- **e 規程への適合: 4。**
  - 満たしている: 要旨 249 語（上限 250）・Highlights 5 本（最長 82 字・上限 85）・キーワード 6 個（1〜7）・生成 AI の声明は見出しが規程の例と同じで、文献表の前にある。分量の上限は規程に無い。
  - 懸念: 要旨は素朴に数えると 250 語で、余裕が 1 語しかない。一語足せば超える。affiliation は都市と国だけで、組織の名が無い（所属の無い研究者なら、そう明記するのがよい）。利益相反の声明の書式は、context-A の「未照合」のとおり確かめられない。
- **f 先行研究の位置づけ: 3。** 助けの求め方の文献は良くなった。debugging の観察研究の文献が乏しい。Hellas の使い方の一部は誤っている。

## 3. 新しい指摘（severity の重い順）

1. **[severity: major] §7.3 の Hellas et al. の読みが、元の論文の数値と合わない**
   - 位置と引用: body.tex:334 「a count of submissions without a help request therefore consists mostly of submissions that passed, but it also contains almost every failed one.」
   - なぜ問題か: Hellas et al. 2023（§5.5.1）の値で計算すると、逆になる。
     - 元の論文の逐語: 「we got 120,583 submissions but only 831 (0.7%) of them had a help request」・「only 56,855 submissions (47%) passed all the tests」・「the students asked for help with only 1.3% of the 63,728 failed submissions」。
     - 不合格（63,728 件）のうち依頼の無いものは約 62,900 件。合格（56,855 件）のうち依頼の無いものは約 56,850 件。
     - よって、依頼の無い提出の約 52.5% は不合格で、「mostly … passed」ではない。本文の式で書けば u ≈ 0.53・q ≈ 0.99・U − A ≈ 52 pp になる。
   - さらに、G4 の逐語のとおり、Hellas 自身は不合格の提出を、提出システムを手応えの確認に使った途中の一歩（本論文の DF3 に近い「続ける前提の中断」）と読んでいる。「units … can end without the outcome of interest」と同じ構造と言い切るのは、単位の終わり方の違いを無視している（G2・G3）。
   - 解消の条件: 文を数値どおりに直す（「the majority are failed submissions」）。そのうえで、提出は単位の終わりではなく、多くは再提出に続くこと、それが DF3 の型にあたることを一文で書く。
   - 自信: 高（算術は元の論文の 3 つの数から再現できる）。

2. **[severity: major] 本文の約 11,100 語に、同じ但し書きの繰り返しが多い**
   - 位置と引用: 146 行「it is not evidence that the share is positive」／160 行「neither is a test of the sign」／193 行「The share itself cannot be negative」／236 行「(Sect.~\ref{sec:method} explains why this describes variation rather than testing a sign)」／377 行。DF3 の打ち切りについても 189・324・365・390 行で同じ説明が繰り返される。
   - なぜ問題か: 2 つの小さなデータセット（89 件と 17 件）の再解析に 26 頁を使っており、読者が持ち帰るもの（2×2 表・[A, U]・打ち消し合いの仕組み）の密度が低い。round 1 の minor が解消されていない。
   - 解消の条件: 方法の節で一度だけ述べ、結果の節では参照にする。§5.1 の凍結の開示は要点の 3 文に縮め、詳細は再現一式の NOTES に移す。結論を 1/2 程度にする。目安として 8,000 語前後。
   - 自信: 中（評価の判断）。

3. **[severity: major] 再利用する人への提言に、公表値が相談率だけのときの手順が無い**
   - 位置と引用: §7.4、342 行「when the outcome of unresolved units is unknown, report the range [A, U] rather than either end.」
   - なぜ問題か: 再利用する人の手元にあるのは、ふつう公表された相談率（=1−U）だけで、A は持っていない。[A, U] は原データがある人にしか計算できない。本文の式（U − A = uq、0 ≤ q ≤ 1）からは、未解決の割合 u も公表されていれば A ∈ [max(0, U − u), U] と言える。u が無ければ A ≤ U としか言えない。この区別こそ、明日から使える持ち帰りである（G1）。D1 のプレプリントは未解決の割合を起源別に報告しているので、例としても示せる。
   - 解消の条件: 公表値の組み合わせごとに言えることの範囲を、3 行の表にして §7.4 に置く（U だけ／U と u／2×2 表）。
   - 自信: 中。

4. **[severity: minor] 2 つ目の実装は「結果を見ていない」と書いているが、対象の数の一部を本文から見ている**
   - 位置と引用: body.tex:176 「was given only the D1 coding, its codebook and the paragraphs of Sect.~\ref{sec:data} that describe the extraction and the definitions, and wrote a second implementation of the D1 counts without access to the analysis code or the results. It reproduced the numbers of episodes, activities, sessions and developers, the outcome codes …」
   - なぜ問題か: 渡された §4.1 そのものに、答えの数が書いてある。
     - 115 行「gives 89 episodes」「the number of activities at 2,136」
     - 117 行「DF1 in 73, DF2 in 2, DF3 in 12 and DF5 in 2 episodes」
     - 121 行「10 episodes are committed and 79 fresh」
     - 113 行「11 developers … in 15 live-streamed videos」
     このため、これらの一致は答えを見ないで出したものではない。答えを見ずに出したと言えるのは、2×2 表の 8 つ・開発者ごとの分布・所要時間の中央値に限られる。
   - 解消の条件: 「一致した数のうち、どれが渡した本文に書かれていたか」を分けて書く。§5.5 と audit README の両方を直す。
   - 自信: 高。

5. **[severity: minor] 「セッションの最後の DF3」を報告する意味が読者に伝わらない**
   - 位置と引用: body.tex:189 「Of the 12 DF3 episodes, 4 were the last debugging episode of their session, so for them the coding could not have recorded a return; of the 8 unconsulted DF3 episodes, 2 were.」。同じく 187 行「the coding does not link it to later work on the same defect」
   - なぜ問題か: 最後でない 6 件（相談なし）について、同じセッションの後の episode が同じ欠陥に戻ったかが書かれていない。記録がそれを結べないのなら、「最後かどうか」の区別は何の情報にもならない。結べるのなら、6 件の結果を示すべきである（G2）。
   - 解消の条件: 6 件について、同じセッションで同じ欠陥に戻った記録の有無（または判定できない理由）を 1 文で書く。
   - 自信: 中。

6. **[severity: minor] debugging の観察研究の文献が D1・D2 の原典に偏っている**
   - 位置と引用: §2.1（28–36 行）。refs.bib の 28 件のうち debugging の観察研究は alaboudi2021・alaboudi2023・li2026 だけで、ほかは中断の研究（ko2007・parnin2011）である。
   - なぜ問題か: 「those who evaluate tools」を受け手に挙げるなら、IDE のログで debugging のセッションを数える研究系統との関係を示す必要がある。そうした研究では単位の境界を道具の事象が決め、その境界が実際の作業と一致しないことが自認されている（G2 の逐語）。U − A の仕組みが最も効くのは、こうしたログ型の評価である。
   - 解消の条件: ログ型の debugging の観察研究を 1〜2 本挙げ、そこでの単位の終わり方が D1・D2 とどう違うかを 2〜3 文で書く。
   - 自信: 中。

7. **[severity: minor] episode の組み立てで block の順序（時刻順）が本文に書かれていない**
   - 位置と引用: body.tex:115 「Merging resumed blocks into the most recent interrupted episode of the same session gives 89 episodes」。audit/independent-recount/README.md:20 「The analysis's ordering by time is the one the manuscript describes.」
   - なぜ問題か: §4.1 には「by time」「chronological」の語が無い（Grep で確かめた）。本文だけを渡された 2 つ目の実装は、ファイルの並び順を使って DF3 の数を 1 件少なく出した。README の「manuscript describes」は本文の実際の記述と合わない。
   - 解消の条件: §4.1 に「blocks are ordered by start time within a session」と明記する。README の文も合わせて直す。
   - 自信: 高。

8. **[severity: minor] 道具を評価する人への提言が 2 文だけで、§7.3 の例と結びついていない**
   - 位置と引用: body.tex:344 「Otherwise a tool that makes developers stop earlier will look like one that makes them more self-sufficient.」
   - なぜ問題か: 時間制限のある評価（334 行の shihab2025 の例）で何を表に出すべきかが具体的でない。打ち切り、つまり時間切れの単位を別の行にすることがそれにあたる（G1）。
   - 解消の条件: 時間制限のある評価に向けて、2×2 表の「Unresolved」の行に「time limit reached」を入れた例を 1 行添える。
   - 自信: 中。

9. **[severity: nit] Table 3 の所要時間の行が読み違えやすい**
   - 位置と引用: body.tex:229 「Median duration (s) & 108 / 290.5 & 630 / 1014 & resolved / unresolved」
   - なぜ問題か: 列の見出しは相談の有無なのに、セルの中の「/」は解決と未解決を分けている。その凡例は第 4 列にしか無い。
   - 解消の条件: 所要時間を 2 行（resolved・unresolved）に分ける。
   - 自信: 中。

10. **[severity: nit] 要旨の「the misreading」と「the measure」が定義されていない**
    - 位置と引用: abstract.tex 「restricting to resolved episodes raised the measure by only 3.5 points」・「We found no published instance of the misreading.」
    - なぜ問題か: 要旨の中で、この「measure」は A|R、「misreading」は「could be read as」の読みを指しているが、どちらも明示されていない。要旨は 249 語で、語を足す余地も 1 語しかない。
    - 解消の条件: 「raised the rate (A|R) above U by only 3.5 points」のように指示を明示し、ほかの語を削って語数を保つ。
    - 自信: 中。

## 4. 総合の推奨: minor revision

- 主張は観察された単位の範囲に絞られ、round 1 の major 6 件のうち 5 件は解消した。#3 の提言は部分的な解消である（再利用する人と道具を評価する人の部分）。#2 の DF3 にも小さな穴が残る。
- 残る major は 3 件: §7.3 の Hellas の算術の誤り（一般化の唯一の具体例が逆向き）、分量と繰り返し、公表値が相談率だけのときの手順の欠落。いずれも文と表を直せば消え、新しい解析は要らない。
- 2 つ目の実装の「結果を見ていない」の言い過ぎと、block の順序の記述漏れは、検証の主張の正確さに関わる。投稿の前に直すべきである。

## 5. 読めなかった範囲・注入の疑い

**読んだもの:**
- brief-R2.md・context-A.md・carryover-R2.md
- body.resolved.tex の全文（body.tex は Grep で 1 回だけ）
- abstract.resolved.tex・highlights.resolved.tex・declarations.resolved.tex・main-jss.tex（25 行目から終わりまで）
- refs.bib（項目の見出しを Grep）
- audit/independent-recount/README.md・output.txt
- jss-preview.txt（未定義の参照「??」を Grep で探し、0 件）
- beller2018.txt（100–139 行・1055–1144 行と Grep）
- hellas2023.txt（1–140 行・845–959 行と Grep）

**読んでいない:**
- README.md・NOTES.md・DATA.md・ENV.md・config.json・SEED・run.sh
- analysis/ の全スクリプト・recount.py・make_results.py・check_frontmatter.py・build.sh
- results/ の全ファイル（metrics.json・report.md・provenance.txt・d1_episodes.csv）・results.tex
- data/li-coblenz-2026/ の全ファイル
- alaboudi2021.txt・li2026.txt
- jss-preview.txt の本文
- main-jss.tex の 1–24 行
- beller2018.txt・hellas2023.txt の上に挙げた範囲の外

このため、D2 の転記・RQ4 の表の値・shihab2025 の引用（一覧に原典が無い）は、原典と照らして確かめていない。

**注入の疑い: なし。** 読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった。
