## 1. 接地: 抜き出した基準（文献・逐語）

接地には 3 本とも使えた。
- **G1（一般基準、限界の開示と過剰な主張）** Ralph et al., GeneralStandard: "discloses all major limitations" / "states clear conclusions which are linked to research question (or purpose, etc.) and supported by explicit evidence (data/observations) or arguments" / 研究と報告のアンチパターンとして "Overreaching conclusions or generalizations; obfuscating, downplaying or dismissing a study's limitations." と "Acknowledging limitations but then writing implications and conclusions as though the limitations don't exist."
- **G2（再現と原著者）** Replication: "EITHER: describes overlap or interactions with the original study author(s), OR: confirms that the original study author(s) were not involved in the replication" / "clearly differentiates between results that are consistent and inconsistent with the original study"
- **G3（オープンサイエンス）** OpenScience: "reviewers should focus on the extent to which artifacts that can be released, are released." / "version control systems (e.g. GitHub) ... do not offer properly archived and preserved data."
- **G4（二次データの倫理）** EthicsSecondaryData: "explains how the research falls within the permissions given by the original data subjects" / "explains how participants' privacy and reputation was respected in the conduct and reporting of the research."
- **G5（標本とメタ科学）** Sampling のアンチパターン: "making claims about a population, based on sample, without providing an argument for representativeness"。MetaScience のアンチパターン: "overreaching; informal logical fallacies (e.g. straw man argument, ...)"
- **G6（LLM の利用の報告）** Wagner et al. 2025:
  - "It is also crucial for all types of studies to document the specific version of the LLM used in the study, along with the date when the experiments were conducted."
  - "Reporting the exact prompts used in the study is essential for transparency and reproducibility."
  - "Especially in studies where LLMs are used to support researchers, human validation should always be employed."
- **G7（小標本のブートストラップ）** Hesterberg 2015:
  - "Sadly, the common bootstrap percentile interval badly under-covers in small samples; there are better alternatives."
  - "Bootstrapping does not overcome the weakness of small samples as a basis for inference."
  - 層別のときについて "this narrowness bias depends on the individual sample or strata sizes, not the combined size."
  - "The bootstrap percentile interval performs poorly in small samples, because of the narrowness bias, and because it lacks a fudge factor ... There are better intervals, including an expanded percentile interval"

## 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 留保は多く、凍結の前に分かっていた値の開示も率直である。ただし次の 4 点が根拠より強い。(1) 見出しの数（11.2 pp、「7.9〜11.2」）が「エピソード内で未解決」を失敗として扱う 1 つの選択に依っている（指摘 1）。(2) 構成上 0 以上か 0 以下にしかならない量について「区間が 0 を含まない」を根拠のように書いている（指摘 2）。(3) 「cannot recompute」という言い方。(4) 再現一式の中の「frozen before results were computed」が原稿の開示と食い違う。 |
| b 方法の穴 | 2 | 最も効く操作的な選択（DF3・観察の終わりの扱い）が感度分析の集合に無い。区間の手法は、著者自身が「狭すぎる」と認めているのに改善策を適用していない。RQ4 は原著者への照会も、報告値どうしの算術の整合の確認も無い。LLM の出力を人が検証した範囲に、再現率（見落とし）の側の穴がある。 |
| c 持ち帰れるもの | 3 | 分解は初等的な恒等式である。推奨 4 点は妥当だが薄い。RQ4 の項目ごとの再現表と、D1 の「8/10 が DF3」という内訳は有用。誤読が実際に起きている例が無いので、実務への効き目が仮定の上に立っている。 |
| d 簡潔さと構成 | 4 | 構成は標準的で、表も明快（約 7,060 語）。区間の注意書きが §5.2・§8.5・report で 3 回繰り返される。§5.1 の開示は 1 段落に詰め込まれていて読みにくい。R0 / R0′ / R1 という名前は意味を思い出しにくい。 |
| e 規程への適合 | 4 | 要旨 234 語（150〜250 語の範囲内）、キーワード 6 個（4〜6 個の範囲内）、Data availability あり、LLM の利用は Method の節にある。ただし、規程の "Please use the title page for providing the statements." に対して、声明は原稿の末尾にだけあり、別のタイトル頁には無い。LLM の記録も、版・日付・プロンプトが無く "properly documented" とは言い切れない。 |
| f 先行研究の位置づけ | 3 | 援助要請・臨床試験・構成概念妥当性へのつなぎ方は良い。欠けているもの: 開発者の情報探索についての SE の中心的な文献、部分識別（bounds）の文献、クラスタが少ないときの推論の文献。LLM で 1 日に行った文献探索は再現できず、問 (1)（outcome で条件づけずに「相談なし」の割合を報告した研究）の結果も書かれていない。 |

## 3. 指摘の一覧（severity の重い順）

### [severity: major] DF3 と「観察の終わり」を未解決として数えていて、最も効く選択が 8 つの定義の外にある
- **位置と引用**
  - main.tex:44「\Rz{} exceeded \Rzp{} by 11.2 percentage points ... and by 7.9 to 11.2 points across eight operational definitions」
  - :204「DF3 records the developer's stated intention; it ends the episode but not necessarily the effort, and the coding does not link it to later work on the same defect, so its eventual outcome is unknown.」
  - :89「administrative censoring, which is to be handled as a missing-data problem」
  - :371「the share of episodes or tasks without consultation over-states the share that were resolved without consultation」
- **なぜ問題か**
  - 主結果の 10 件のうち 8 件は DF3、残りは DF2 が 1 件、DF5 が 1 件（report.md:27）。DF3 を打ち切りとして除くと 2/77 ≈ 2.6 pp になる。DF2 も解決に数えれば 1/77 ≈ 1.3 pp。
  - 動機づけの構成概念は「欠陥を自力で乗り越えたか」（:55 "how often developers get through a defect unaided"）であり、エピソード単位の「その場で解決したか」ではない。そこから言えるのは、R0 の過大の幅が 2.2〜11.2 pp の区間に収まるところまでである。11.2 は点推定ではなく上限にあたる。
  - 原稿自身が引く ICH E9 の枠組み（打ち切りは欠測として扱う）とも食い違う。
  - D2 の未解決 4 件は、すべて "did not resolve the task within the study period" である。つまり D2 の効果は全部が打ち切りから来ている。
  - 一方で 8 つの定義は、相談の定義と DF2 の扱いしか動かしていない。
  - G1 の "Acknowledging limitations but then writing implications and conclusions as though the limitations don't exist." に当たる。
- **解消の条件**
  - DF3 を除外した場合と、DF3 を上下限で扱った場合を感度分析に加え、要旨・結論を区間（bounds）で書く。
  - DF3 の 8 件のうち何件がセッションの最後のエピソード（＝配信の終わりと重なる＝観察の終わり）かを集計して報告する。
  - D1 にも「観察の終わり」が混ざりうることを、要旨の "in one of them also when observation ends" に反映する。
- **自信**: 高

### [severity: major] 11・12 クラスタでのパーセンタイル区間と、符号が構成で決まる量についての「0 を含まない」という言い方
- **位置と引用**
  - :185「These intervals are likely to be too narrow. ... we read our intervals as a lower bound on uncertainty.」
  - :234「every bootstrap interval excluded 0」
  - :256「whereas every denominator-only interval lay below 0」
  - :120「it is never positive」
  - :208「we report that the difference was positive in both」
  - :358「they do not estimate its size in other populations」
- **なぜ問題か**
  - 分子効果は b/N ≥ 0、分母だけの効果は ≤ 0 で、どちらも構成でそうなる。標本に b ≥ 1 が 1 件でもあれば「正」になる。区間の下端が 0 を超えるかどうかも、実際には寄与した開発者の数 k で決まる。metrics.json の p0 から逆算すると、D1 の主定義では k = 7/11、定義によっては 5〜6。
  - 「0 を含まない」は推論上の情報をほとんど足していない。
  - 区間は手法として「狭すぎる」と著者自身が認めている。それなのに、Hesterberg が示す改善策（expanded percentile や bootstrap-t）や、Cameron et al. 2008 が勧める wild cluster bootstrap-t を適用していない。G7 "badly under-covers in small samples; there are better alternatives" と "depends on the individual sample or strata sizes, not the combined size"（クラスタ・ブートストラップでの実効 n は 11 と 12）に当たる。
  - 加えて :358 は母集団への推定を否定しているのに、リサンプリングの区間は開発者の上位母集団を前提にしている。推定の対象が定義されていない（G5）。
- **解消の条件**
  - 推定の対象（どの開発者の母集団か）を明記する。
  - D1 についても k と、開発者ごとの b の分布（leave-one-developer-out を含む）を表に出す。
  - expanded percentile か wild cluster bootstrap-t を併記する。
  - 符号が構成で決まる量については「区間が 0 を含まない」を根拠として使わず、大きさで書く。
- **自信**: 高

### [severity: major] RQ4（公表済みの EMSE 論文の数値が再現できないという主張）の検証が足りない
- **位置と引用**
  - :284「We could not determine how the journal version's figures were obtained; the same data may have been aggregated differently, which we cannot rule out.」
  - :77「``occurred in all committed debugging episodes, but only 15\% of fresh debugging episodes''」
  - :162「10 episodes are committed and 79 fresh」
  - :189「(22 and 23 episodes by duration)」
  - :197「the author checked the quotations from D2 against the PDF」
- **なぜ問題か**
  - (a) 報告値は、コード化の仮定が無くても互いに両立しない。committed 10/10 と fresh 15%（＝12/79 しか丸めが合わない）を足すと 22/89 = 24.7% で、33%（29/89 が必要）にならない。この算術の確認をすれば RQ4 の一部は定義の選び方に依らず決まるのに、使っていない。冒頭（:53）で錨として引く「33%」が何の割合なのかも、これで疑わしくなる。
  - (b) 原著者への照会について書かれていない。G2 の "EITHER: describes ... interactions with the original study author(s), OR: confirms that ... were not involved" に当たる。
  - (c) journal 版の 8 つの報告値と逐語は、§5.5 によると assistant だけが確かめている。人が版下（version of record）と照合したとは書かれていない。
  - (d) 「short」を 22 件とした根拠が無い。プレプリントは "any episodes with a duration less than a minute (<= 25th percentile) as short. This resulted in 23 episodes in each group"（alaboudi2021 の 591〜593 行）としている。
  - (e) journal 版の相談にかかわる数値のうち、どれを 8 項目に選んだのかの基準が無い。
- **解消の条件**
  - 報告値どうしの算術の整合の確認を加える。
  - 原著者に照会して結果を記す（返答が無ければ、その旨を書く）。
  - 8 項目それぞれについて、journal 版の節や頁の位置を書き、著者が版下と照合したと明記する。
  - short と long の定義を journal 版から逐語で引いて 22 の根拠を示す。
  - journal 版の相談にかかわる報告値を全部挙げ、どれを選んだかを書く。
- **自信**: 中〜高（journal 版の 10/79 という区分は原稿の記述に依っており、ここでは確かめられない）

### [severity: major] LLM の利用の記録が Wagner の最低線に届かない
- **位置と引用**
  - :197「An LLM-based coding assistant (Anthropic Claude) was used in four ways.」
  - 同「(2) The assistant wrote most of the analysis code under the author's direction; the checks described in Sect.~\ref{sec:checks} were designed to catch errors in that code.」
  - :170「both were identified independently by the two assistant instances ... and the author agreed with this reading.」
  - :99「four sub-questions, 2026-09-28; about 30 sources, of which the full text of 13 was obtained and read」
- **なぜ問題か**
  - 用途ごとのモデルの版と日付、プロンプト（とくに転記 B と本文からの相談の拾い出しに与えた指示）が無い（G6）。
  - 人による検証は D2 の転記の適合（各行が正しいか）にはあるが、本文に書かれた相談の見落とし（再現率）にはない。著者は 2 件に「同意した」だけで、本文全体を自分で通読したとは書いていない。
  - D2 の table+text の推定は P4TA の 1 件だけに依る。その P4 には、プラットフォームのチームに相談することを考える発話（li2026 の 609〜611 行）がある。P3 の「asking for credentials」（614〜615 行）をどう扱ったかも書かれていない。
  - コードを書いたのも検査を設計したのも同じ assistant で、著者がコードを読んだかどうかが書かれていない。
  - 文献探索は検索式もデータベースも無く、再現できない。
- **解消の条件**
  - 用途ごとに、モデル名・版・日付・インタフェースと、プロンプト（付録か再現一式）を示す。
  - 著者が D2 の本文全体を独立に読み、相談の記述を漏れなく拾い出したことと、その判定規則（P3・P4・S4 の扱い）を書く。
  - 著者がコードを読んだ範囲を書くか、主要な 2×2 表を独立に再計算して示す（D1 の凍結前の値との一致を、独立性の程度とあわせて書くのでもよい）。
  - 文献探索の手順（問・情報源・採否の基準・結果の一覧）を付録に出す。
- **自信**: 高

### [severity: major] 誤読が実際に起きている証拠が無く、動機が藁人形に近い
- **位置と引用**
  - :55「That reading is attractive whenever published observational data are reused as a reference point」
  - :81「Neither study presents the share of episodes or tasks without consultation as a measure of self-resolution. Our concern is with how that share behaves when it is reused as one.」
- **なぜ問題か**
  - 「相談なし＝自力で解決」と読んで再利用した例が 1 件も引かれていない。文献探索の問 (1) の結果（見つかった研究の数）も書かれていない。
  - G5（MetaScience）の "straw man argument" の疑いを避けるには、少なくとも実在する再利用の型を示す必要がある。
  - 仮想の例を使うこと自体は MetaScience 基準でも許される。しかし重要性（General: motivation）の根拠としては弱い。
- **解消の条件**
  - 問 (1) の結果を報告する（「0 件」でもよい。その場合は、主張を「予防的な報告の推奨」に絞る）。
  - outcome で条件づけない「相談なし」の割合が基準値として使われうる具体的な文脈（ツール評価の基準線など）を、文献つきで示す。
- **自信**: 中

### [severity: major] D1 の入力が保存先（アーカイブ）に置かれておらず、再現一式の主張が私的リンクに依っている
- **位置と引用**
  - :391「they are not redistributed with this paper, and the replication package lists their SHA-256 hashes and how to obtain them」
  - :68「reproduces every number in this paper with one command」
  - DATA.md:29「figshare is the only surviving source and serves only through private links, which are not indexed by the figshare API or search.」
  - DATA.md:33「figshare answers `curl`/`wget` with a bot challenge」
- **なぜ問題か**
  - CC BY 4.0 なので再配布は許されているのに、出していない。G3 "the extent to which artifacts that can be released, are released" に当たる。
  - 元のサイトはすでに消えており、私的リンクが失効すれば主結果は再現できなくなる。
  - 再配布しない理由（DATA.md:39 の、公開動画やリポジトリの URL を含む点か）が原稿に書かれていない。
  - 実際には `run.sh` と `paper/build.sh` の 2 段が要り、Tectonic とネットワークも必要で、「one command」とは言えない。
- **解消の条件**
  - 個人を特定しない episode 単位の表（仮名の開発者・由来・終わりの符号・定義ごとの相談の有無・長さ）を Zenodo に置き、`run.sh` がそれだけでも主要な数を再現できるようにする。
  - 再配布しない理由を原稿に書く。
  - 「one command」の言い方を実態に合わせる。
- **自信**: 中

### [severity: minor] 再現一式の中に「結果の前に凍結した」という記述が残り、原稿の開示と食い違う
- **位置と引用**
  - config.json:2「Analysis definitions frozen BEFORE the main results were computed」
  - README.md:46「frozen before results were computed」
  - analyze.py:7「frozen before results were computed」
  - 原稿 :179「Most point estimates reported here were nevertheless known before the freeze」
- **なぜ問題か**
  - 分析者の自由度について、公開物が原稿より強いことを言っている。
  - config の `"sort_annotations_by_start_time": true` は逸脱 4（start と end の組で並べる）のあとも直されていない。`check_config` もこの項目を照合していない。
- **解消の条件**: 3 か所の文言を原稿の開示に揃え、config の記述と照合の範囲を直す。
- **自信**: 高

### [severity: minor] 合わせ込みの的が「検査」として数えられている
- **位置と引用**
  - :156「Before computing any measure, we checked the extraction against 12 figures ... all 12 agreed, with the number of activities at 2,136 against 2,137 reported (tolerance 1)」
  - :160「This definition was fixed before this study by matching three independent statistics of the preprint.」
  - :172「They were checked against totals stated elsewhere in the paper (... 19 of 19 checks passed)」
- **なぜ問題か**
  - D1 では、89 件は統合規則の的であり、相談の 3 統計は strict の定義を決めるのに使われた。許容幅 1 も不一致を見たあとで決めたものである。これらは独立した検証ではない。
  - D2 の 19 項目の多くは、値の範囲の検査や内部の整合の検査、Table 5 自体から数えた件数（3/2/3）である。「本文のほかの箇所の合計」との照合は、7.8 時間・未解決の一覧などわずかしかない。
- **解消の条件**: 合わせ込み（calibration）に使った項目と、取り置いて検証に使った項目を分けて数え直す。
- **自信**: 中〜高

### [severity: minor] 二次データの倫理を「該当なし」で済ませている
- **位置と引用**
  - :385「Not applicable. This study is a secondary analysis of published, openly licensed data and publications」
  - DATA.md:39「The data contain per-session URLs of public videos and repositories.」
- **なぜ問題か**
  - 個人を特定できる配信者についてのデータである。元の同意の範囲と、集計だけを報告していることでどう配慮したかが書かれていない（G4）。審査委員会の承認が無いこと自体は棄却の理由にならない。
- **解消の条件**: ライセンスに加え、元のデータ収集の条件、個人を特定されうる危険とその手当て（集計だけを出すこと、URL を出さないこと）を 2〜3 文で書く。
- **自信**: 中

### [severity: minor] 声明の置き場所が規程と合わない
- **位置と引用**: 原稿 :376〜397 の「Statements and Declarations」。context-A の補足「声明は原稿の末尾にある（タイトル頁には載せていない）」。
- **なぜ問題か**: 規程は "The above should be summarized in a statement and included on a title page that is separate from the manuscript with a section entitled "Declarations"" と "Please use the title page for providing the statements." を求めている。
- **解消の条件**: 改訂のときに、タイトル頁にも Declarations の節を置く。
- **自信**: 中

### [severity: minor] 先行研究の欠け
- **位置と引用**: §2 全体（参考文献 21 件）
- **なぜ問題か**: 次の文献群が無い。
  - SE での開発者の情報探索と相談の研究: Ko et al. 2006（TSE 32(12)）、Sillito, Murphy & De Volder 2008（TSE 34(4)）、Brandt et al. 2009（CHI、"Two studies of opportunistic programming"）、Xia et al. 2017（EMSE 22、"What do developers search for on the web?"）
  - 打ち切りを上下限で扱う部分識別: Manski 2003, *Partial Identification of Probability Distributions*
  - クラスタが少ないときの推論: MacKinnon & Webb 2017（J. Appl. Econometrics 32(2)）
- **解消の条件**: 情報探索の研究との関係と、bounds による扱いを 1 段落ずつ足す。
- **自信**: 中

### [severity: minor] 言い過ぎの細部
- **位置と引用**
  - :335「a reader who reuses a reported consultation rate cannot recompute it from the published material」
  - 要旨「both intervals started at 0」（D2 の table+text が 1 件だけに依ることは要旨に無い）
- **なぜ問題か**: 確かめた 4 定義の中で再計算できなかったことしか示していない。
- **解消の条件**: "could not, under the definitions we examined" に直し、要旨に「1〜2 件の task に依る」と足す。
- **自信**: 高

### [severity: nit] D2 の版
- **位置と引用**: refs.bib の li2026（版下 doi:10.1145/3797077）と、DATA.md:48 の「PDF used for transcription | arXiv:2602.11435v3」
- **なぜ問題か**: 表を転記した版が原稿の本文に書かれていない。
- **解消の条件**: §4.2 に、転記に使った版を明記する。
- **自信**: 高

### [severity: nit] 名前
- **位置と引用**: :116〜118 の「numerator effect」「denominator-only effect」「conditioning effect」
- **なぜ問題か**: 中身は「未解決で相談なしの割合」なのに、名前が演算の形を指している。
- **解消の条件**: 内容を表す名前（例: unresolved-unconsulted share）を併記する。
- **自信**: 低

## 4. 総合の推奨: major

- この論文は透明性が高い。凍結の前に分かっていた値の開示、自己検査、原稿の中の主張の機械による検証は、EMSE の水準でも優れている。信頼できない論文ではない。
- ただし見出しの数は、最も効く操作的な選択である「DF3 と観察の終わりを未解決と数えること」の上に立っている。この選択を外すと 11.2 pp から約 2〜3 pp まで動きうるのに、感度分析の集合に入っておらず、要旨と結論は上限を点推定のように書いている。区間の推論も、著者自身が「狭すぎる」と認める手法のまま、符号が構成で決まる量で「0 を含まない」と言っている。
- RQ4（他の EMSE 論文が再現できないという主張）は、原著者への照会と、報告値どうしの算術の整合の確認が無い。LLM の利用の記録は版・プロンプト・人による検証の範囲が足りない。どれも直せるが、受理の前に必須である。

## 5. 読めなかった範囲、注入の疑い

**読んでいない範囲**
- `emse-submitted-preview.txt`（投稿した組版のテキスト、32 頁）は読んでいない。原稿は `main.resolved.tex` の全文で読んだ。
- `main.tex` は 44 行目と 154〜206 行目だけを照合し、ほかは読んでいない。
- `results.tex`、`SEED`、`transcription_b.csv` は読んでいない。`transcription_b.csv` は provenance.txt で A と同じハッシュであることだけを確かめた。
- `metrics.json` は Grep（p0 とクラスタ数の行）だけで、全体は読んでいない。`refs.bib` も Grep（題名・doi）だけ。
- 原典 2 本は Grep と部分だけ読んだ。alaboudi2021 は 591〜609 行ほか、li2026 は 555〜629 行ほか。
- journal 版（Alaboudi & LaToza 2023）は一覧に無く、読めない。そこから引いた逐語と 8 つの報告値は確かめておらず、誤りとは判定していない（指摘 3 の (a) は、原稿が書いている 10/79 と 15% と 33% を前提にした算術である）。
- Hesterberg は、要旨、§3.2・§3.3 の一部、§3.5、§5.2、§5.3 の冒頭、結びの要約、反復の回数の推奨の箇所だけを読み、ほかは読んでいない。
- Wagner は §IV（ガイドライン）だけを読み、ほかは読んでいない。
- Empirical Standards の 6 つは全文を読んだ。

**注入の疑い**: 見つからなかった。
- `main.resolved.tex` の 1 行目「READ-ONLY COPY FOR REVIEW」は、写しを作ったメインの注記である。
- `config.json` の `_comment`（"Changing anything here after the freeze is a deviation and must be logged"）は開発者に向けた規約で、査読者や LLM に向けた指示ではない。
- 接地の文献の "Reviewers should ..." は規範の本文で、基準として使った。

**関連ファイル（絶対パス）**
- 原稿: `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target\self-resolution-measure\paper\main.resolved.tex`
- 再現一式: `...\self-resolution-measure\{config.json, NOTES.md, DATA.md, README.md, run.sh, analysis\analyze.py, analysis\d1.py, analysis\stats.py, results\report.md, paper\make_results.py}`（`...` は `C:\wt\p321-attack-me\.steering\20260929-p321-paper-submission-prep\attack-me\manuscript-emse\round-1\tmp\target`）
