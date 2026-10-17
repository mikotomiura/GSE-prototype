# 査読の報告: 心理測定と構成概念の妥当性の立場の査読者（R1・prereg）

読んだファイル（依頼文と context-A の一覧にあるものだけ、すべて全文）:
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/attack-me/prereg-c-registration/round-1/brief-R1.md
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/attack-me/prereg-c-registration/round-1/context-A.md
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md（対象物・1〜198 行）
- /Users/johnd/GSE-prototype-af-c/.steering/20261014-ai-fatigue-core1-item-analysis/codebook.md（1〜54 行）
- 接地: .../round-1/tmp/sources/elson2023.txt と .../round-1/tmp/sources/lintner2024.txt（どちらも 1 行のテキスト。全文を読んだ）

## 1. 接地（この立場が論文に求める基準）

- **K1 名前と中身を混同しない**（Elson et al. 2023）: "They involve a nominal fallacy: that a measure’s name tells you about its contents or what it measures"
- **K2 同じ名前の道具でも中身が変わりうる**（Elson et al. 2023）: "Dropping, adding, and altering items in self-report scales, aggregating total scores in various ways in laboratory tasks, or varying stimuli and trial durations all occur while researchers not only refer to the same construct, but actually to the same nominal instrument"
- **K3 数え方を先に決め、できればコードで登録する**（Elson et al. 2023, Table 1）: "Determine procedural and scoring details ahead of time, reporting all deviations as they potentially weaken the strength of conclusions. Analytical and statistical decisions should be preregistered with code rather than a narrative description."
- **K4 尺度を変えたら、その変更を正当化する**（Elson et al. 2023, Table 1）: "Prove that any deviation or modification to an existing measure is either meaningful (e.g. to address non-invariance of a measure between samples) or irrelevant"
- **K5 内容的妥当性が中心にある**（Lintner 2024）: "Content validity refers to the degree to which the instrument measures the construct(s) it purports to measure" / "COSMIN considers content validity the most important measurement property of an instrument"
- **K6 構成概念の境界をどう決めたかを明かし、判定者の数による偏りを認める**（Lintner 2024）: "While self-efficacy is somewhat a distinct construct from self-reported AI literacy, the distinction between the two is heavily blurred. I therefore decided to adopt a more inclusive approach" / "It was performed by a single author, which might have caused some bias in the scales’ quality assessment"

## 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | GSRR-10 は「同じ問題が別の研究の集合でも現れるか」を問うと書くが、「現れた」と判定する基準が無い（GSRR-13 は仮説なし）。確認の形をとりながら、確認の基準が無い。 |
| b 方法の穴 | 2 | 組み入れの基準（「AI の利用との関係で」「動機の消耗」を疲労に含める）が、結果の C1・C2b と重なっている。そのため数の分布の一部は、組み入れの段階で決まってしまう。改変された既存の尺度の扱い（K2）と、AI の下書きの由来についても穴がある。 |
| c 持ち帰れるもの | 3 | 帰属の水準・項目の内容・報告の不整合を研究ごとに表にする設計は、読み手が使える。ただし、尺度ごとに報告された妥当性の証拠（信頼性・因子構造・内容的妥当性）をコードしないので、「尺度が妥当化されていない」という背景の主張（GSRR-10）を確かめる表にならない。 |
| d 簡潔さと構成 | 4 | 3,046 語で GSRR の項目に沿っており読みやすい。表 C1–C7 も整理されている。気になる点は、添付のコードブックが日本語で、版の表記と英訳が TBD であることだけ。 |
| e 規程への適合 | 3 | [GSRR-21]–[GSRR-32]・[GSRR-33]–[GSRR-42] のように項目を範囲でまとめていて、項目ごとに「該当しない・理由」が書かれていない（van den Akker 逐語 1）。確認の集合が小さすぎる場合の代替の計画が「表にできなければ報告する」だけで、閾値が無い（逐語 3）。 |
| f 先行研究の位置づけ | 3 | COSMIN を使う系統的レビューの存在には触れている（GSRR-10）。しかし、COSMIN の評価をしない理由と、それとどう補い合うかの説明が無い（GSRR-55 は「なし」とだけ書く）。参考文献は報告の手引きの 3 本だけ。 |
| g 固定の十分さ | 2 | C2b を何の単位で数えるか（項目・尺度・研究）が無い。C6a の一致の判定基準・「主な尺度」の定義・因果の語の一覧・較正が終わる条件も無い。経路の規則とコードブックの間にも矛盾がある（下記）。数え方のスクリプトは登録しない（K3）。 |

## 3. 指摘の一覧（重い順）

- [severity: major] 組み入れの基準が結果の変数と重なっていて、C1 と C2b の分布の一部が組み入れの段階で決まる
  - 位置と引用: registration-en.md:100「fatigue (cognitive, emotional, physical, motivational or behavioural depletion, exhaustion or burnout-like depletion) is defined, measured or qualitatively analysed in relation to that AI use」、:104「no relation to AI use (E3)」、:50「... only as an interview theme, or not at all?」
  - なぜ問題か: (1) E3 は AI との関係が無い研究を除く。そうすると、C1 の「none」と「variable label only」の数は、組み入れる人が「in relation to」をどこまで緩く取るかで決まる。しかも組み入れを最終的に決める人の一人は、規則を書いた第 1 著者である（:22, :109）。(2) 疲労の定義に「motivational ... depletion」が入っているので、RQ2 が問う「項目が動機の低下を含むか」の一部も、組み入れの段階で保証されてしまう。(3) 組み入れが「fatigue」という名前によるのか、中身によるのかが書かれていない。名前によるなら、K1 の名目の誤り（jingle/jangle）を組み入れの段階で持ち込む。同じものを別の名前で測る研究（technostress の exhaustion、burnout の下位尺度など）を入れるのかも分からない。境界をどう決めたかを明かすという基準（K6, Lintner「the distinction between the two is heavily blurred. I therefore decided to adopt a more inclusive approach」）にも届いていない。
  - 解消の条件: 組み入れが名前によるのか、中身によるのかを 1 通りに書く（例: 「著者が fatigue・exhaustion・burnout の語で呼ぶ変数があること」を条件にし、中身は C2b で別に判定する）。E3 の「relation」の最低限を操作的に定義する。C1 の「none」が E3 によってどこまで切り落とされるかを限界に書く。動機の消耗を組み入れの定義から外すか、外さないなら、C2b の MOT の割合は組み入れの定義の影響を受けると明記する。
  - 自信: 高

- [severity: major] C2b の既存の尺度の値の由来が、AI の下書きを禁じる規則と矛盾する。改変された版も見分けない
  - 位置と引用: registration-en.md:73「If a confirmation study uses one of the four instruments already coded at item level, its C2b values come from the exploration coding.」、:137「AI drafts are allowed only for C4f recalculation and C5 bibliographic matching.」、:146「They become data only after being re-coded from the full text under these rules.」。codebook.md:44「`coder`: `claude-prelim`（Claude の予備判定）」、:49「判定者は Claude の予備判定とユーザーの確認だけで、独立した 2 人目はいない。一致は測っていない」
  - なぜ問題か: 探索の段階の 4 つの尺度の C2b は、Claude の予備判定と 1 人の確認でできている。それを確認の集合に流用すると、:137 と :146 に反する。2 人による独立のコード化（:136）と一致の測定（:138）も通らない（K6, Lintner「performed by a single author, which might have caused some bias」）。さらに、確認の集合の研究が同じ名前の尺度の項目を落としたり、言い換えたり、翻訳したりしていても、探索の段階の値がそのまま入る（K2「not only refer to the same construct, but actually to the same nominal instrument」）。
  - 解消の条件: 探索の段階の 4 つの尺度の C2b を、登録の後に 2 人の coder が独立にコードし直すと書く。流用は「その研究が載せた項目の文言が、コードした版と逐語で一致する場合だけ」に限る。一致しない場合は新しい版として C2b をコードし、C2a に改変の種類（項目の削除・追加・言い換え・教示文だけ AI に変えた・翻訳）を記録する。
  - 自信: 高

- [severity: major] RQ2 は「疲労」を問うのに、コードブックには疲労のコードが無い。疲労は OTH に混ざっている
  - 位置と引用: registration-en.md:51「What do the items ask about: fatigue, avoidance, irritation, futility, or reduced interest and engagement?」、:122「`OTH` other, including fatigue proper」。codebook.md:22「`OTH` | その他 | 疲れ・消耗・認知の負荷・理解の困難・身体と感覚の症状・睡眠」
  - なぜ問題か: 内容的妥当性の問い（K5「measures the construct(s) it purports to measure」）に答えるには、「疲労そのものを問う項目」の割合が中心の量になる。いまの設計では、疲労・認知の負荷・理解の困難・睡眠・身体の症状が 1 つのコードに入る。そのため「疲労尺度の項目のうち疲労を問うものはいくつか」が数えられず、RQ2 の文言にも答えられない。また target は MOT/AVO/FUT にしか付かない（codebook.md:28）。だから疲労の項目が AI の利用に向いているのかも記録されない。これは C1（帰属の水準）と照らすうえで欠かせない情報である。
  - 解消の条件: OTH を少なくとも「FAT 疲労・消耗」と「その他（負荷・理解・身体・睡眠）」に分ける。登録の後で変えるなら、改訂として版を上げる。そうしないなら RQ2 の文言から「fatigue」を外す。target を全部の型に付けるか、付けない理由を書く。登録の表（:122）にも「target は MOT/AVO/FUT のときだけ付ける」と明記する。
  - 自信: 高

- [severity: major] C2b の主要な数え方の単位と量が決まっていない
  - 位置と引用: registration-en.md:73「The primary C2b count uses only the instruments first seen.」、:158「C2b type × target, per instrument」、:177「C2b counted with secondary type `MOT` included (a lenient count).」
  - なぜ問題か: 「count」が何を数えるのかが 1 通りに決まらない。項目の数か、尺度の中の割合か、MOT を 1 つ以上含む尺度の数か、研究の数か。同じ尺度を使う研究が多いときの重みも決まっていない。boundary の項目を主の型で数えるという点も、感度分析（:177）から推すしかない。分析を先にコードで決めるという基準（K3「preregistered with code rather than a narrative description」）にも届いていない。
  - 解消の条件: 主要な量を 1 つ定義する（例: 「確認の集合で初めて見た尺度ごとに、型 × target の項目の数と割合。研究の数ではなく、尺度の版を 1 単位とする」）。数え方のスクリプト（ダミーデータで動くもの）を登録に添付する。
  - 自信: 高

- [severity: major] C2a・C2c が、既存の尺度の改変の種類と、その報告を記録しない
  - 位置と引用: registration-en.md:121「Origin: new in this study / existing AI-specific scale (name) / adapted general scale (source) / unchanged general scale.」、:123「back-translation / content validity / pilot / factor check — each reported or not」
  - なぜ問題か: 「adapted」と「unchanged」を分ける判定の規則が無い。教示文に「AI」を足しただけの場合、項目を落とした場合、尺度の段階の数を変えた場合、得点の出し方を変えた場合が、どれに入るか分からない。既存の AI 特有の尺度を一部だけ使った場合や改変した場合のコードも無い。こうした改変は、測定の柔軟性の中心にあたる（K2, K4）。C1 の「scale item or instruction」も、項目に AI が入る場合と教示文だけに入る場合を 1 つにまとめている。後者は、一般の尺度の名前と中身のまま AI に帰属させる典型（K1）であり、分けて数えるべきである。
  - 解消の条件: C2a に「改変の種類」の列を足す（項目の削除・追加・言い換え・教示文だけ・段階の変更・得点化の変更・翻訳。それぞれ「あり / 報告なし / 確かめられない」）。「unchanged」は、原典と項目の逐語を照合できた場合だけにする。C1 の最初の水準を「項目の文言に AI」と「教示文だけに AI」に分ける。
  - 自信: 高

- [severity: major] 確認の形をとるのに「現れた」と判定する基準が無い
  - 位置と引用: registration-en.md:47「The present review asks whether these problems also appear when the rules are fixed in advance and applied to a different set of studies.」、:60「We state no hypotheses.」
  - なぜ問題か: 探索の集合と確認の集合を分けた目的は、確認だと考えられる。しかし基準が無いと、確認の集合で何件見つかっても「現れた」と書けてしまう。結論の強さを事前に縛れない（K3「reporting all deviations as they potentially weaken the strength of conclusions」）。
  - 解消の条件: 仮説の検定をしないなら、GSRR-10 の「asks whether ... also appear」を記述の問いに書き直す。または、記述だけの判定の規則を先に書く（例: 「各 C4 の規則で、確認の集合に 1 件以上あれば『現れた』、0 件なら『見つからなかった』。割合は探索の集合の値と並べて示すが、比べた結論は書かない」）。
  - 自信: 中

- [severity: major] C6a・C4b・C7 の判定に、主観の残る語が定義されないまま入っている
  - 位置と引用: registration-en.md:127「Construct named in the title vs. the name and item content of the main instrument: match / mismatch」、:127「The list of causal terms will be fixed before calibration coding」、:125「Direction of the main relation」、:128「(ii) it claims "AI fatigue"」
  - なぜ問題か: 「main instrument」「main relation」が、尺度や関係が複数ある研究でどれを指すのか分からない。「match」を名前の一致で決めるのか、項目の中身で決めるのか（C2b のどの値なら mismatch なのか）も無い。因果の語の一覧が登録の後に決まる。C7(ii) の「claims 'AI fatigue'」が逐語の語の一致なのか、意味の一致なのかも不明である。こうした語は 2 人の coder の一致を下げ、規則が登録の後に動く余地を残す（K3）。
  - 解消の条件: 「main instrument」を規則で決める（例: 結論の文の構成概念を測る尺度。複数あれば最初に記述されたもの）。C6a の一致を C2b の値から機械的に決める規則にする（例: 名前が fatigue・exhaustion で、OTH(疲労) の項目が半数未満なら mismatch）。因果の語の一覧は登録に入れる。C7(ii) は語の一覧（AI fatigue・AI-induced fatigue など）で判定する。
  - 自信: 高

- [severity: minor] 較正と一致の測定に、終わりの条件と、数えにくい項目の扱いが無い
  - 位置と引用: registration-en.md:35「5 records drawn at random ... used only to refine the definitions」、:138「Cohen's kappa with 95% CI for categorical items」、:120「(all that apply)」
  - なぜ問題か: 5 件では、C2b の境界の項目や質的研究が出ないこともある。較正を終える基準（一致の値・追加の較正）が無い。C1 は複数を選べるコードなので、Cohen's kappa をそのままでは定義できない。C2b の一致を項目の単位で測るのか尺度の単位で測るのかも決まっていない。一致が低いときに何をするか（定義を改訂して再コードするか）も無い。
  - 解消の条件: C1 は水準ごとに二値の kappa にする。C2b は項目の単位で type と target に分けて測る。較正を終える条件（例: 全項目の一致率が一定以上、届かなければさらに 5 件）と、届かないときの改訂の手続きを書く。
  - 自信: 中

- [severity: minor] 尺度の妥当性の証拠をコードせず、COSMIN を使わない理由も書いていない
  - 位置と引用: registration-en.md:47「Existing reviews note that the scales are not validated」、:155「Quality appraisal. None.」
  - なぜ問題か: 背景で「妥当化されていない」と書きながら、尺度ごとに報告された内容的妥当性・構造的妥当性・信頼性の有無をコードしない。そのため、その主張を確かめる表が残らない（K5「COSMIN considers content validity the most important measurement property」）。C2c は改変の手続きだけを見ていて、新しく作った尺度の証拠は見ない。
  - 解消の条件: C2 に「報告された測定の性質」の列を足す（内容的妥当性・因子分析・内的一貫性・弁別的妥当性。それぞれ報告あり / なし。COSMIN の評価はしないと明記する）。または、COSMIN を使うレビューとの役割の分担を GSRR-55 に 2 文で書く。
  - 自信: 中

- [severity: minor] AI の役割の書き方が、表と本文で一致しない
  - 位置と引用: registration-en.md:24「Drafting support, cross-checking of counts, recalculation (C4f), bibliographic matching (C5)」、:137「AI drafts are allowed only for C4f recalculation and C5 bibliographic matching.」、:170「One person builds the tables, and the other checks every number against the code table.」
  - なぜ問題か: 「Drafting support」と「cross-checking of counts」が何を指すのかが、本文の制限（C4f・C5 だけ）と合わない。
  - 解消の条件: 表を本文の制限に合わせる。数の照合を AI が補助するなら、その結果を人が確かめると書く。
  - 自信: 高

- [severity: minor] 添付するコードブックの版と中身が、登録の手続きと合っていない
  - 位置と引用: codebook.md:3「固定: 2026-10-15。」、:51「追記（2026-10-17・基準は変えない）」、:49「独立した 2 人目はいない」。registration-en.md:197「Codebook for C2b (fixed version; to be translated into English before registration) **[TBD]**」
  - なぜ問題か: 「fixed version」がどの版か（追記を含むのか）が特定できない。コードブックの限界の節が、探索の段階の手続き（Claude の予備判定と 1 人の確認）を書いたままなので、確認の段階の手続きと矛盾する。英訳が無ければ登録の添付にならない。
  - 解消の条件: 版の番号と日付を付けた英訳を添付する。確認の段階の coder 列の値（coder1 / coder2）と手続きを書き足し、探索の段階の記述と分ける。
  - 自信: 高

- [severity: minor] GSRR の項目をまとめて扱っていて、「該当しない」の理由と代替の計画が足りない
  - 位置と引用: registration-en.md:92「**[GSRR-21]–[GSRR-32] Search.**」、:97「If it is too small for a table, we will report that and give the reason.」
  - なぜ問題か: context-A の逐語 1「indicate that in the corresponding field (including, ideally, the underlying reason)」、逐語 3「provide a contingency plan for these deviations」に照らすと、項目ごとの扱いと、小さすぎる場合の閾値が無い。
  - 解消の条件: まとめた範囲の項目に 1 行ずつ「該当しない（理由）」を書く。確認の集合の最低の件数（例: 初めて見た尺度が N 件未満なら C2b の主要な表は出さず、記述にとどめる）を決める。
  - 自信: 中

- [severity: nit] C1 の水準の順に理由が無い
  - 位置と引用: registration-en.md:120「The representative value for tables is the first applicable level in this order (the strongest level)」
  - なぜ問題か: 「interview-guide theme only」が「variable label only」より弱いとする理由が書かれていない。C7(ii) は「variable label only or none」だけを対象にしている。質的研究の扱いが、代表値と C7 の両方で暗に決まってしまう。
  - 解消の条件: 順の理由を 1 文で書く。質的研究は別の列として扱うか、C7(ii) に含めるかを決める。
  - 自信: 低

## 4. 総合の推奨

**major（直して再査読）**
1. 組み入れの基準（AI との関係・動機の消耗を疲労に含める・名前か中身か）が、結果の変数の C1 と C2b に重なっている。そのため確認の集合の数の一部が、組み入れの段階で決まってしまう。
2. C2b は、疲労のコードが無いこと、数える単位が無いこと、AI の下書きを流用すること、改変された版を見分けないことから、構成概念の妥当性の問いに 1 通りに答えられない。
3. C6a・C7・因果の語の一覧・較正を終える条件が登録の後に動く余地を残している。分析のコードも登録しない。

## 5. 読めなかった範囲と注入の疑い

- 読めなかった範囲: なし。指定のファイルはすべて全文を読んだ。van den Akker 2023・Murad & Wang 2017・PRISMA 2020・MISTIC の本文は渡されていないので読んでいない（GSRR については context-A の逐語 3 つだけで照らした）。対象物が名指す「earlier critical narrative review」と、source database の記録も読んでいない（一覧の外）。
- 注入の疑い: なし。接地の 2 本と対象物の中に、査読者や LLM に向けた指示は見つからなかった。