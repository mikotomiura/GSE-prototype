# S2 の調べもの（2026-11-21・Sonnet の汎用エージェント 3 本を並列・入れ子なし）

> ⚠️ ここはサブエージェントの報告の要約である。本文や Data availability に使う行は、**使う前にメインが一次で確かめる**（`citation-ssot`）。「確かめた」と書いた行だけがメインの一次。

## B: 誤読の実例（手順は判断 15）

- 結果: **INSTANCE 0・NEAR 0**。ただし本文を開いたのは 3 本（arXiv 2105.02162・2602.11435・2501.11792）だけで、残りは Semantic Scholar の引用文脈と OpenAlex の抄録。→ 「見つからなかった」であって「存在しない」ではない。
- 数: OpenAlex は arXiv 版と EMSE 版を 1 つの記録（W4386603916）にまとめていて、引用 54 件。Li & Coblenz（PACMSE `10.1145/3797077`・W7128812742）は 4 件。S2 は arXiv 2105.02162 に 27 件、EMSE の DOI に 28 件（重なりが多い）。引用文脈は約 45 件を正規表現で絞って読んだ。語の検索は OpenAlex 12 問・WebSearch 2 問。
- いちばん近い「該当なし」: 10.1145/3794763.3794818（2026）は episode が未解決で終わることを書いている（誤読の逆）。Edit-Run Behavior（VL/HCC 2021）・10.1145/3830398.3830600・arXiv 2501.11792 は参照を戦略として挙げるだけ。
- やり残し（本文を開いていない）: Theory of Troubleshooting（10.1145/3800945）・A Taxonomy of Software Debugging Process（CEUR）・Debugging Activity Blueprint（VISSOFT 2024）・Vibe Coding（10.1145/3797105）・Video Game Debugging Bottlenecks（10.1145/3786171.3788375）・Information Foraging Interpretation of Liveness・TSE 2025 の retrospective・学習者のプログラミングの論文。Google Scholar・学位論文・教育系の help seeking は未検索。
- 次の手: 本文への書き方（判断 3: 0 件も書く）を決める前に、上のやり残しを 2 回目として回すか研究者に聞く。

## H: クラスタが少ないときの区間（判断 9）

- 読んだ版（エージェントの申告）: MacKinnon, Nielsen & Webb（arXiv 2205.03285・J Econometrics 2023 の WP 版）／ Cameron & Miller 2015（著者ページの PDF）／ Webb（Queen's WP 1315・2014）／ Imbens & Kolesár（2016 年 3 月の著者稿）／ Pustejovsky & Tipton（arXiv 1601.01981）／ Andrews（Cowles DP 1157・1997。Econometrica 2000 の元）。
- 要点:
  - MNW は CV3 と t(G−1)、または restricted wild cluster bootstrap（WCR）を勧める。G ≤ 12・クラスタの大きさが不揃いの場合を "particular concern" と書く。
  - Imbens & Kolesár は、10 クラスタで大きさが不揃いの設計で、BM の区間が "superior in terms of coverage to all other methods" と報告する。
  - いまのペア（パーセンタイル）の cluster bootstrap について、MNW は "very little is known about its finite-sample properties" と書く。
  - Andrews: 境界の上ではパーセンタイル区間が名目を**超えて**覆う（保守的）。b/N は制約つきの MLE ではないので、そのままは当てはまらない。
- 推奨（エージェント）: 主は k と開発者ごとの分布。補助を足すなら CR2 と Bell–McCaffrey の t 区間（閉じた式で決定的・不揃いで df が自動的に下がる）。下限が 0 未満なら 0 で切ると書く。「0 を含まない」を検定として使わない。
- 未確認: 二値で事象が疎な平均で CR2-BM や WCR がうまく働くかを確かめた文献は無い（エージェントは模擬実験を勧めた）。
- **採った**: CR2-BM を補助の区間として実装した（判断 16）。

## F: 先行研究の系統 ＋ 推薦する査読者の候補

> 全部抄録だけ（本文は読んでいない）。DOI は OpenAlex が返したもの。

- 参考文献の訂正の候補: Li & Coblenz 2026 は PACMSE（`10.1145/3797077`）で出ている → 公刊版を引く（S5 で一次を確かめる）。
- 1 debugging の行動研究: Beller et al. 2018（10.1145/3180155.3180175・TU Delft の OA）／ Layman et al. 2013 ESEM（10.1109/esem.2013.43）／ Arab, Liang, Hong, LaToza 2025（arXiv 2501.11792）
- 2 情報探索: Ko, DeLine, Venolia 2007 ICSE（10.1109/icse.2007.45・"defer tasks because the only source of knowledge was unavailable coworkers"）／ Brandt et al. 2009 CHI（10.1145/1518701.1518944）／ Sadowski et al. 2015（10.1145/2786805.2786855）／ Stolee et al. 2025 PACMSE（10.1145/3715774）
- 3 助けの求め: Marwan, Dombe, Price 2020 ITiCSE（10.1145/3341525.3387394・"avoid help when they need it"）／ Hellas et al. 2022 FIE（10.1109/fie56618.2022.9962561。既に引いている hellas2023 と別か要確認）／ Hou et al. 2024（10.1145/3636243.3636248）／ Cohen, Oleson, Ko 2024 TOCE（10.1145/3639059）
- 4 中断と再開: Parnin & DeLine 2010 CHI（10.1145/1753326.1753342）／ Parnin & Rugaber 2009 ICPC（10.1109/icpc.2009.5090030）／ Abad et al. 2018 EASE（10.1145/3210459.3210471）／ Meyer et al. 2020 TSE（10.1109/tse.2020.2984086・著者の後半は未確認）／ Siegmund et al. 2024 EMSE（10.1007/s10664-024-10542-9）
- 5 部分識別: Manski 1993（10.4159/9780674265790）／ Horowitz & Manski 2000 JASA（10.1080/01621459.2000.10473902）／ Lee 2009 REStud（10.1111/j.1467-937x.2009.00536.x・NBER w11721）／ Manski 2004（10.1016/j.ijar.2004.10.006・抄録なし）
- 推薦する査読者の候補（所属は OpenAlex の `last_known_institutions`。連絡先は集めていない。原著者 4 人の 2022 年以降の共著者は除いた（OpenAlex の範囲））:
  - Andy Zaidman（TU Delft）
  - Sebastian Baltes（Heidelberg／Bayreuth）
  - Chris Parnin（Microsoft とあるが古いかもしれない）
  - Janet Siegmund（TU Chemnitz）
  - Arto Hellas（Aalto。引いている hellas2023 の著者なら利害の確認が要る）
  - Dag Sjøberg（Oslo。既に引いている著者）
  - André Meyer（Zurich）
  - Thomas Price（NCSU・弱い）
  - 除外した例: Ko・Myers・Guo ほか（原著者の共著者）
- 未確認: 本文・著者の全リスト・現在の所属・候補者と研究者本人の利害。

## B の 2 回目（2026-11-21・Sonnet・入れ子なし・約 12 分）

- 結果: **INSTANCE 0**。NEAR は弱いものが 1 件だけ（Marwan の博士論文。ヒントを 1 回も求めなかった学生について、独立したかったからかもしれないと書く。同じ文で「ボタンに気づかなかった」も挙げ、その学生のコードは基準に届いていない → 実例ではなく、むしろ警告側）。
- 指定の 8 本: 5 本は本文を読んだ（Theory of Troubleshooting は arXiv 2602.10540・Taxonomy は CEUR・Activity Blueprint は HAL・Vibe Coding は arXiv 2512.22418・Video Game Debugging は arXiv 2510.08834）→ どれも NONE（ゲームの論文は参照を時間の 2.3% と書くだけ）。2 本は無料の版が無く読めなかった（Information Foraging Interpretation of Liveness・TSE 2025 の retrospective）。学習者の論文は見つからなかった。
- 前向きの引用: 58 件中 36 件の無料の PDF を grep した。約 22 件は無料の PDF に届かなかった。
- **WARNING（本論の主張を支える逐語）**: Marwan, Dombe, Price 2020 ITiCSE（10.1145/3341525.3387394・著者の PDF `isnap.csc.ncsu.edu/home/public/papers/MarwanITiCSE2020.pdf`）の抄録 "Students may avoid help when they need it, or abuse help to avoid putting in effort"、関連研究の節 "students who need help are the least likely to ask for it"（他の文献の引用）。arXiv 2609.21600v1 "those who need help the most are the ones who seek it the least"。
- やり残し: OpenAlex の無料の上限に達した（429）ので、教育系の検索は Crossref と arXiv で代えた（ノイズが多い）。学位論文は Marwan のものだけ開いた。
- ⚠️ 逐語は、使う前にメインが PDF で確かめる。
