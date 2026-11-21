# review-R3 — paper-reviewer の応答（attack-me・stage manuscript・round 2・JSS）

> メインが応答の本文を写した。機械の検査（secrets-filter・一覧の外のパス）を通してから追跡されるファイルにした。

# R3（JSS・方法論と再現性の番人）round 2 の査読

## 0. 引き継ぎの判定（carryover-R3）

| # | 判定 | 理由（いまの原稿の位置と逐語） |
|---|---|---|
| major: DF3 と観察の終わりを未解決に数えている | **解消**（D2 側に新しい穴あり、新しい指摘 2） | §5.4（body.tex 156–158）で打ち切りとしての感度分析と区間 [A, U] を足した。RQ1（189）「Most of the difference rests on DF3: over all 89 episodes, the 8 unconsulted DF3 episodes contribute 9.0pp of the 11.2pp」。要旨は「it is the width of the range of unaided resolution, not a loss」。D1 の扱いは十分。 |
| major: 11・12 クラスタでのパーセンタイル区間と「0 を含まない」 | **部分的に解消** | 「0 を含まない」を検定として書くことはやめた（146「it is not evidence that the share is positive」、236）。k、開発者ごとの分布、CR2/BM、LODO も足した（160, 189）。ただし主の区間はパーセンタイルの pairs cluster bootstrap のままで、結論（390）は「(developer-level bootstrap interval [6.8, 15.7])」を但し書きなしで出している。MacKinnon et al. が主に勧める CV3 や WCR bootstrap は使っていない。区間の読み方も節ごとに違う（新しい指摘 5）。 |
| major: RQ4 の検証が足りない | **解消** | 表を構造の数値と相談の数値に分けた（Table 5）。算術（290「amounts to 22 of 89 episodes, or 24.7%, not 33%」）を足し、著者が PDF と照合した（150）。照会は「at the time of submission we had not received a reply」。言い切りは「under any of the four definitions we examined」（350）に絞った。alaboudi2021.txt で 21%・91%・2137 を確かめた。journal 版は一覧の外なので確かめていない。 |
| major: LLM の記録が Wagner et al. の最低線に届かない | **部分的に解消** | モデル・日付・役割は書いた（172–180）。残りは 4 つ。指示文は保存していない（172「The instructions given to each instance were not archived as a set」）。設定（温度など）を書いていない。解析コードを人が確かめていない（176「the author inspected the outputs but did not read the code」）。2 つ目の実装に渡した文に、合わせるべき値が入っていた（新しい指摘 1）。 |
| major: 誤読の実例が無く藁人形に近い | **解消**（構成上の依存は残る） | 序論 8「The paper is therefore not a correction of a published claim. Its aim is preventive」。要旨は「We found no published instance of the misreading」。この言明の根拠は対象外の §2.5 だけにある（新しい指摘 9）。 |
| major: D1 の入力がアーカイブに無い | **部分的に解消** | `results/d1_episodes.csv` と DATA.md の帰属表示は在る。ただし Data availability の DOI は旧版を指している（新しい指摘 3）。 |
| minor: 「結果の前に凍結」の記述が残る | **解消** | config.json の `_comment`、analyze.py の docstring（7–9 行「most point estimates were known earlier」）、NOTES.md の Freeze。 |
| minor: 合わせ込みの的を検査に数えている | **解消** | 115「These figures were targets as well as checks … not that it was tested independently of it」。 |
| minor: 二次データの倫理 | **部分的に解消** | §8（385）は 3 文だけ。元の被験者（配信者）の同意と研究利用の範囲は説明していない。§7.3 の「agreed to be observed」とも食い違う（新しい指摘 7）。 |
| minor: 声明の置き場所 | **解消** | declarations.tex は JSS の見出しの例どおり、文献表の前にある。 |
| minor: 先行研究の欠け | **解消** | §2.3 に Manski、ICH E9(R1)、打ち切りを足した。§5.4 で Imbens & Kolesár、MacKinnon を引いている。 |
| minor: 言い過ぎの細部 | **部分的に解消** | Highlight 4 が D1 に限ることを書いていない（新しい指摘 8）。MacKinnon の言い換えが強すぎる（新しい指摘 5）。 |
| nit: D2 の版 | **解消** | 125「transcribed from arXiv:2602.11435v3 … (Article FSE049)」。 |
| nit: 名前 | **解消** | U・A・A\|R。 |

## 1. 接地（逐語）

- Ralph et al., GeneralStandard:「describes in detail how the data were analyzed」「discloses all major limitations」「states clear conclusions which are linked to research question … and supported by explicit evidence」。
- Ralph et al., OpenScience:「archives supplementary materials on preserved digital repositories such as zenodo.org …」。
- Ralph et al., EthicsSecondaryData:「explains how the research falls within the permissions given by the original data subjects」「explains the provenance of the original data … (particularly in respect of consent for capture and future use)」。
- Wagner et al. 2025:
  - §IV-D「Reporting the exact prompts used in the study is essential for transparency and reproducibility.」
  - §IV-C「Detailed documentation of the conﬁguration and parameters used during any study is necessary for reproducibility.」
  - §IV-F「Especially in studies where LLMs are used to support researchers, human validation should always be employed.」
- MacKinnon, Nielsen & Webb 2023:
  - §7「Unless the number of clusters is fairly large and evidence demonstrates a convincing degree of homogeneity across clusters, results from at least one or two other methods should be reported. These might include tests and/or conﬁdence intervals based on CV3, P values and/or conﬁdence intervals based on one or more variants of the WCR bootstrap」
  - §6.1「Our recommendation is to use the methods discussed in this subsection primarily to conﬁrm (or perhaps cast doubt on) the results of the methods that we recommend」
  - §7「investigators should always report the median cluster size and the maximum cluster size, in addition to N and G」

## 2. 評価表

- **a 主張と根拠の一致: 4**。D1 の主張は DF3 と区間 [A, U] で正しく限定されている。弱い所が 2 つある。結論の「positive in both」は D2 で打ち切りを片側だけに当てた結果に依る（指摘 2）。Highlight 4 は D1 だけの話なのに限定が無い（指摘 8）。
- **b 方法の穴: 3**。凍結の守り（ハッシュで凍結した部分を検査する作りと Deviations 8〜11）は強い。一方、LLM が作った物を人が確かめていない（指摘 1・4）。D1 の時間の定義が曖昧（指摘 6）。D2 の打ち切りの選び方が非対称（指摘 2）。
- **c 持ち帰れるもの: 3**。2×2 の最小の報告と u·q の仕組みは使える。ただし核は恒等式で、大きさは「says nothing about its size elsewhere」（332）と著者自身が書いている。
- **d 簡潔さと構成: 3**。約 11,100 語。RQ1 の 189 行の 1 段落に k、CR2、LODO、DF3 の寄与、打ち切り、境界、最後の episode かどうかが詰め込まれている。§5.1 の凍結の開示も長い。
- **e 規程への適合: 4**。要旨 249 語（素朴な数えで 250 語、上限ちょうど）、Highlights 5 本（どれも 85 字以下）、キーワード 6 個、生成 AI の申告は文献表の前、どれも規程どおり。ただし「Provide a link to the dataset」に対して、示した DOI が別の版を指す（指摘 3）。
- **f 先行研究の位置づけ: 4**。部分識別、打ち切り、クラスタが少ないときの推論が入った。§2.5 は対象外。

## 3. 新しい指摘（重い順）

- [severity: major] 2 つ目の実装は、照合の的となる値を入力として受け取っていた
  - 位置と引用: body.tex 176「was given only the D1 coding, its codebook and the paragraphs of Sect.~\ref{sec:data} … without access to the analysis code or the results. It reproduced the numbers of episodes, activities, sessions and developers, the outcome codes, … the split by defect origin」。渡した §4.1 の本文そのもの（115「gives 89 episodes」「2,136」「11 developers and 15 sessions」、117「DF1 in 73, DF2 in 2, DF3 in 12 and DF5 in 2」、121「10 episodes are committed and 79 fresh」）にこれらの値が書いてある。audit/README.md 3 行目も「the paragraphs of the manuscript that describe episode extraction … (Sect. 4.1)」と書いている。
  - なぜ問題か: 「without access to … the results」は事実と違う。挙げた一致のうち前半は、入力に書かれた値の写しでありうる。独立した証拠になるのは 2×2 表、開発者ごとの分布、起源の中の 2×2 だけである。Wagner et al. §IV-F「human validation should always be employed」に照らすと、人による確かめも無い。指示文も保存していない（Wagner §IV-D）。この照合は 2026-11-21 に行ったもので、保存できたはずである。
  - 解消の条件: 渡した文に含まれていた数値を挙げ、一致の一覧を「入力に在った値」と「入力に無かった値」に分ける。この実装への指示文を逐語で再現一式に入れる。D1 の episode を数件（例えば unresolved かつ unconsulted の 10 件）、著者が codebook と元の動画やコード化データで確かめた記録を足す。
  - 自信: 高

- [severity: major] D2 の打ち切りの感度分析が P4TA だけを外していて、原典の文や本文自身の読みと合わない
  - 位置と引用: body.tex 156「in D2, the task that ended with the study period (P4TA, a participant's task; for the streamers' tasks the paper does not say which ended with the stream)」。config.json 112「"study_period_end_ids": ["P4TA"]」。一方、body.tex 127 は原典の「participants did not resolve the task within the study period (P4TA, S3TA, S4TB, S5TA)」を引いて「In D2, ``unresolved'' therefore includes the end of observation」と読んでいる。li2026.txt 344 にも同じ文がある。NOTES.md 10 も「all four unresolved tasks, of participants and of streamers, are listed as not resolved within the study period」。
  - なぜ問題か: 凍結の後に足した解析で、打ち切りの集合を片側だけに選んでいる。4 件すべてを打ち切りにすると、D2 には unresolved の課題が残らず、差は 0 になる。結論と 195 行の「we report that the difference was positive in both」が成り立つかどうかは、この選び方で決まる。D1 では DF3 と DF5 をまとめて打ち切りとした。それに比べて基準が揃っていない。
  - 解消の条件: D2 で 4 件すべてを打ち切りにした値（差は 0）を並べて報告する。「positive in both」は観察の中の解決に限った言明だと明記する（D2 の [A, U] の幅が 11.8 で、すべて不明であることを要旨と結論でも示す）。P4TA だけを外す理由が原典の別の文にあるなら、その逐語を示す。
  - 自信: 中

- [severity: major] Data availability の DOI は旧版を指していて、本文が在ると言う派生表や凍結の後の解析が入っていない
  - 位置と引用: declarations.tex 15「the replication package also contains an episode-level table derived from that coding … archived at \url{https://doi.org/10.5281/zenodo.23029603}」。README.md 75「An archived copy of version `submission-2026-09-29` is on Zenodo: <https://doi.org/10.5281/zenodo.23029603>」。NOTES.md の Deviations 8–11 の派生表、post_review、audit は、どれもこのタグの後に足したものである。
  - なぜ問題か: 査読者がこの DOI を開いても、本文が述べる派生表、LODO、CR2、2 つ目の実装は無い。Ralph et al. OpenScience「archives supplementary materials on preserved digital repositories」の要件を、いまの版については満たしていない。JSS の「Provide a link to the dataset during the submission process」にも、実質で合わない。
  - 解消の条件: 改訂版（`revision-jss` のコミット）を Zenodo の新しい版として出し、その版の DOI（concept DOI でなく、版の DOI）を Data availability と README に書く。旧版の DOI は前の版のために残す。
  - 自信: 高（新しい版を出すつもりかどうかは、この版では確かめられない）

- [severity: major] 解析コードと D2 の本文中の相談を、人が確かめていない。安く確かめられる所が残っている
  - 位置と引用: body.tex 176「the author inspected the outputs but did not read the code」。174「The recall of the body-text search is unknown」。381「The D2 counts have no second implementation; with 17 tasks they can be recounted by hand from the transcriptions」。declarations.tex 18「the author did not read the analysis code」。
  - なぜ問題か: Wagner et al. §IV-F「human validation should always be employed」。D2 は 17 課題で、本文中の相談の拾い出しは、著者が原典の結果の節を読めば数時間で再現率を確かめられる。手で数え直せると書きながら、数え直していない。JSS の申告の文「reflects their own analysis」に照らしても、編集者は解析を人が確かめていないことを問題にしうる。
  - 解消の条件: 著者が D2 の 17 課題を手で数え直し、本文中の相談を自分で拾い出して、結果を書く（「the author recounted …; found …」）。D1 は、少なくとも数え方の中心（d1.py の結合の規則と相談の規則、stats.py の数え方）を著者が読んだか、上の数件の手での確かめを足す。
  - 自信: 高

- [severity: minor] 区間を何として読むかが節ごとに違い、MacKinnon et al. の言い換えが原文より強い
  - 位置と引用: 146「we read our intervals as a lower bound on uncertainty」。160「we read this interval, like the bootstrap interval, as a description of the variation across developers. Neither interval rests on random sampling of developers from a defined population」。377「no method is known to be reliable with so few clusters of such unequal size \citep{mackinnon2023}」。結論 390「(developer-level bootstrap interval [6.8, 15.7])」。
  - なぜ問題か: 「不確かさの下限」と「開発者の間のばらつきの記述」は別の読み方で、母集団が無いならどちらの意味も定まらない。開発者の間のばらつきは、LODO と開発者ごとの表がすでに記述している。MacKinnon et al. は §7 で CV3 や WCR を主に勧め、BM 系は「primarily to conﬁrm (or perhaps cast doubt on) the results of the methods that we recommend」と位置づけている。「no method is known to be reliable」とまでは書いていない。この言い換えが、勧められた方法を使わない理由のように読める。
  - 解消の条件: 区間の読み方を 1 つにそろえる。結論から区間を外すか、但し書きを付ける。MacKinnon の言い換えを原文の強さに合わせる（例: 「cases with few clusters of unequal size are ones in which even the recommended methods may be unreliable」）。CV3 か WCR を足すか、足さない理由（上限と下限に制約のある割合の平均に回帰の方法を当てることの限界）を書く。D2 のクラスタの大きさの分布（中央値と最大）も書く（MacKinnon §7）。
  - 自信: 中

- [severity: minor] D1 の時間の定義が曖昧で、2 つ目の実装では読みによって中央値が分かれたことを伏せている
  - 位置と引用: body.tex 162「D1: seconds of the episode」。176「It reproduced … the median durations」。audit/output.txt 21「dur unresolved unconsulted 10 median span 363.0 median sum 290.5」。README「The analysis sums the block durations of a merged episode, which is the script's "sum" column」。
  - なぜ問題か: 「seconds of the episode」は、中断を挟んだ episode の始まりから終わりまで（span）と自然に読める。2 つ目の実装は 2 つの読みを出し、合ったのは sum の方だけだった。それを「reproduced」とだけ書くのは、一致を後から選んだことになる。時間で重みを付けた 19.1pp もこの選び方に依る。
  - 解消の条件: §5.4 で「中断を除いた各 block の時間の和」と定義する。span で数えた値（重みを付けた差を含む）も添えるか、span で数えると中央値が違うことを書く。
  - 自信: 高

- [severity: minor] 「agreed to be observed」と二次データの倫理の記述が不十分
  - 位置と引用: body.tex 334「in our data they rest on 11 and 12 developers who agreed to be observed」。385「D1's coding, however, refers to public videos and repositories of identifiable developers」。
  - なぜ問題か: D1 の配信者は公開の配信をしただけで、研究に同意したとは原稿のどこにも書いていない。Ralph et al. EthicsSecondaryData「explains the provenance of the original data … (particularly in respect of consent for capture and future use)」「explains how the research falls within the permissions given by the original data subjects」に、§8 は答えていない。
  - 解消の条件: 334 行を「who streamed publicly (D1) or took part in a study (D2)」のように直す。§8 に、D1 と D2 の配信者が研究利用について何を同意し、または同意していないか（原典の記述で）と、派生表を再配布してよい根拠（CC BY 4.0 と、新しい開示が無いこと）を 2〜3 文で足す。
  - 自信: 中

- [severity: minor] Highlight 4 が D1 に限ることを書いていない
  - 位置と引用: highlights.tex 8「Restricting to resolved episodes hides the gap because two differences cancel.」。本文 260「The two differences do not always cancel: in D2 under the table+text definition, the denominator difference … is more than twice as large」。
  - なぜ問題か: 本文が限定した主張を、Highlights が一般化している。
  - 解消の条件: 「In one dataset, restricting …」のように限定を付ける（85 字以内に収める）。
  - 自信: 高

- [severity: minor] 最後の episode かどうかの理屈が §3.1 と食い違う
  - 位置と引用: 189「4 were the last debugging episode of their session, so for them the coding could not have recorded a return」。69「Neither dataset links a unit to later work on the same defect」。
  - なぜ問題か: コード化データが後の作業と結び付かないなら、最後の episode でなくても戻ったことは記録されない。開発者が複数の動画を持つ場合、別のセッションで戻ることもある。この量は 2 つ目の実装と一致しなかった唯一の数（3 か 4 か）でもあり、定義（始まりの時刻で並べること）を本文が書いていない。
  - 解消の条件: この数を外すか、「the session contains no later debugging episode at all」という記述にとどめ、戻ったかどうかとの関係を言わない。並べ方を本文に書く。
  - 自信: 中

- [severity: minor] 派生表から計算し直せると言うが、それを読むスクリプトが無い
  - 位置と引用: declarations.tex 15「from which the D1 measures can be recomputed」。NOTES.md 46「It is not an input to any result」。
  - 解消の条件: 派生表だけから主要な値を出す短いスクリプト（または run.sh の切り替え）を足すか、「can be recomputed by hand」と書く。
  - 自信: 中

- [severity: minor] 要旨と序論の「実例は見つからなかった」が、対象外の §2.5 だけに頼っている（構成の指摘）
  - 位置と引用: abstract.tex「We found no published instance of the misreading.」。序論 8・10。
  - 解消の条件: §2.5 を書き直すときに、要旨の文を検索の範囲つきの言い方（「in a documented search of …」）にそろえる。
  - 自信: 中

- [severity: nit] Hellas の例の算術が、引いた数だけでは成り立たない
  - 位置と引用: 334「a count of submissions without a help request therefore consists mostly of submissions that passed」。
  - なぜ問題か: 引いた 2 つの数（全体の 0.7%、失敗した提出の 1.3%）だけからは、失敗した提出の割合が最大で約 54% になりうる。「mostly passed」と言うには提出の総数が要る。
  - 解消の条件: 原典の提出の総数を引く。
  - 自信: 低

- [severity: nit] 同じ量の単位が pp と % で揺れている
  - 位置と引用: 189「11.2pp」と「2.6% (2/77)」。どちらも unresolved-unconsulted share である。
  - 自信: 高

## 4. 総合の推奨: minor（major に近い）

- 前の round の重い指摘（DF3、RQ4、凍結の開示）は実質的に解消した。凍結した部分をハッシュで守る作りは模範的である。
- 残る重いものは、検証の主張が事実より強い所である。2 つ目の実装は合わせる的を受け取っていたし、人による確かめが無い。Data availability の DOI は旧版を指す。D2 の打ち切りは片側だけに当てている。
- どれも追加のデータを要らず、文の訂正と小さな作業（手での数え直し、新しい版の Zenodo への寄託、4 件すべてを打ち切りにした D2 の値）で直せる。

## 5. 読めなかった範囲と注入の疑い

**読んでいない**:
- refs.bib、results.tex、jss-preview.txt、ENV.md、SEED、run.sh、build.sh、make_results.py、check_frontmatter.py
- d1.py、d2.py、stats.py、derived.py
- data/li-coblenz-2026/ の CSV と README、results/report.md、provenance.txt、d1_episodes.csv
- recount.py の本文（grep で数値を直に書き込んでいないことだけ確かめた）、post_review.py の 190 行より後、analyze.py の grep で当てた所の外、metrics.json の大部分
- empirical-standards.txt は grep で当てた所だけ、mackinnon2023.txt は §6.1・§7 とその近くだけ、wagner2024.txt は §IV-A〜F だけ。alaboudi2021・li2026 は grep で当てた所だけ。
- journal 版の D1 と Hellas、Shihab は一覧の外なので確かめていない。
- body.tex の元のファイルは開かず、resolved 版で読んだ（行番号は同じ）。

**注入の疑い**: 読んだ範囲には見つからなかった。
