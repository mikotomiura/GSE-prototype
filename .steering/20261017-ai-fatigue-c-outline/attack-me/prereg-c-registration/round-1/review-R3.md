# 査読報告（立場: メタ研究・事前登録・再現性の方法論者／下位人格: 過剰主張と検証できない手順の摘発者）

対象物: /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md（以下 REG）
添付: /Users/johnd/GSE-prototype-af-c/.steering/20261014-ai-fatigue-core1-item-analysis/codebook.md（以下 CB）
stage: prereg

## 1. 接地（この立場が登録に求める基準・逐語）

van den Akker et al. (2023)（gsrr.txt）
- S1（全項目に答える。使わない手順は理由を添えて書く）: "when you fill out the form on the Open Science Framework, all items are mandatory." / "If an item asks about a procedure you do not plan to use or is not applicable, indicate that in the corresponding field (including, ideally, the underlying reason)."
- S2（予見できる逸脱には代替の計画を置く）: "If you already foresee some deviations when filling out the form (e.g., you anticipate that you will not have enough studies in a moderator group), provide a contingency plan for these deviations in the relevant parts of the registration."
- S3（合成の手順は具体的に書き、実行できない場合も書く）: [GSRRF-56] "Describe the specific procedure you will apply to arrive at an answer to the research question(s). ... Also specify what you will do if parts of the plan can't be properly executed."
- S4（標本の大きさが足りない場合の扱い）: [GSRRF-39] "Finally, describe what you will do if a minimum required sample size or power is not reached (for your main analysis and any supplementary analyses)."
- S5（凍結の時点で決めておくことの目的）: "making it easier to identify decisions that may have introduced bias (e.g., a change in the criteria for study inclusion or the omission of an analysis without a valid rationale)."

Nuijten et al. (2016)（nuijten2016.txt。grep で抜いた範囲だけ読んだ）
- S6（「不一致」は再計算の規則が操作的に決まって初めて数えられる。片側検定・多重比較の補正・丸めといった決めごとで率が変わる）: "Whenever the reported p -value is inconsistent with the recalculated p -value, the result is marked as an inconsistency ." / "By default all tests are assumed to be two-tailed." / "statcheck does not take into account p -values that are adjusted for multiple testing (e.g., a Bonferroni correction). P -values adjusted for multiple comparisons that are higher than the recalculated p -value can therefore erroneously be marked as inconsistent." / "The correct rounding of test statistics is not incorporated in the automatic one-tailed test detection"
- S7（自動の抽出・判定は手作業と照合して妥当性を確かめる）: "we performed a validity study of statcheck, in which we compared statcheck's results with the results of Wicherts, Bakker, and Molenaar ( 2011 ), who performed a manual search for and verification of reporting errors" / "the results of statcheck should be interpreted with care."

## 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 推論の範囲は抑えてある（REG:166「Descriptive only: no significance tests and no prevalence estimates」、REG:168）。ただ GSRR-10 は「whether these problems also appear」と追試として問いを立てているのに、「現れた」と言える基準が無い。また SQ2 の「supported by its own attribution level, instrument and design」は、C7 が実際に確かめる 3 条件より広い。 |
| b 方法の穴 | 3 | 確認集合が汚れていることは正直に開示してある（REG:74-78）。一方で、確認集合に何が入るかが、後から起きる出来事の時期に左右される（REG:97）。人が見ていない集団の記録が入るのかどうかも書かれていない（REG:77）。AI の下書きを使う C4f は手作業との照合の計画が無い（S7）。 |
| c 持ち帰れるもの | 4 | コード表・コードブック・集計のスクリプトを CC BY／MIT で公開する（REG:145）。探索集合と確認集合を分けて報告する設計（REG:66-70）は、他のレビューにも転用できる。 |
| d 簡潔さと構成 | 4 | 3,046 語で GSRR の順に沿っており、表もよく締まっている。ただ項目の番号の束ね方（GSRR-21–32、33–42、63–65）が様式と合わない箇所がある（e で扱う）。 |
| e 規程への適合 | 3 | S1 は「all items are mandatory」と求めるが、GSRR-28/29（著者への連絡）、GSRR-58（合成者の盲検）、GSRR-36/45（指示書）、GSRR-41（スクリーニングの判定の共有）に、個別の回答が無い。「[GSRR-63]–[GSRR-65] Amendments」（REG:180）は、様式の 63＝合成の手順の正当化、64＝合成のデータの共有、65＝その他、と中身が食い違う。GSRR-17 が求める版番号も無い。 |
| f 先行研究の位置づけ | 3 | 「we did not find a review」（REG:47）は、どこを探したか（検索の範囲）を示していない。COSMIN を使った既存のレビューに触れているのに、参考文献は 3 本だけで、比較の相手を引いていない。手順の面では Nuijten 系の不一致検出の伝統と比べられるのに、C4f はそれを参照していない。 |
| g 固定の十分さ | 2 | 主要な数え方のうち少なくとも 4 つ（C6b の因果語、C4f の再計算の規則、C2b の集計の単位、確認集合の構成）が、凍結の時点で 1 通りに決まっていない。添付のコードブックと REG の間に、AI の役割と探索のコードの扱いで矛盾がある。E5（同一標本の除外）と RQ4／C5 も噛み合っていない。 |

## 3. 指摘の一覧（重い順）

- [severity: major] C6b の因果語のリストが凍結の後に決まる
  - 位置と引用: REG:127「The list of causal terms will be fixed before calibration coding (examples: effect, impact, lead to, induce)」
  - なぜ問題か: C6b は RQ5 の主要な数え方であり、C7(i) を通じて SQ2 にも直接入る。登録の後に語のリストを決めると、確認集合のタイトルを見た人（第 1 著者はタイトルと要旨をスクリーニング済み・REG:76）が、数を動かせる余地が残る。S5「making it easier to identify decisions that may have introduced bias」。
  - 解消の条件: 語のリスト（語形の変化・否定の扱い・「association」「predict」の扱いを含む）を登録に書き切るか、凍結した添付にする。
  - 自信: 高

- [severity: major] C4f の再計算が操作的に定義されていない（しかも AI が下書きする）
  - 位置と引用: REG:125「(f) Recalculation from reported values: matches within rounding / does not match (which) / cannot be calculated」、REG:137「AI drafts are allowed only for C4f recalculation」
  - なぜ問題か: 何を再計算するのか（t・F・χ² からの p か、割合か、合計か、Cronbach の α か）、丸めの許容幅（報告の桁数に基づく上下限か）、片側検定と多重比較の補正をどう扱うか、記録の単位（結果の単位か記録の単位か）が、どれも決まっていない。Nuijten et al. (2016) は、こうした決めごとで不一致の判定が変わることを示している。「By default all tests are assumed to be two-tailed.」「P -values adjusted for multiple comparisons ... can therefore erroneously be marked as inconsistent.」AI の下書きを「A human checks every AI-drafted value」で済ませているが、照合の手順（独立に再計算するのか、見て確認するだけか）が無い。S7「we performed a validity study」。
  - 解消の条件: 対象にする統計量の一覧・許容幅の式・片側検定と補正の規則・記録の単位を明記する。人の確認は独立の再計算で行い、AI の下書きとの一致率を報告すると書く（statcheck のような既存の道具を使うなら、その版も書く）。
  - 自信: 高

- [severity: major] 添付のコードブックと REG の間に、AI の役割と探索のコードの扱いで矛盾がある
  - 位置と引用: CB:44「`coder`: `claude-prelim`（Claude の予備判定）」、CB:49「判定者は Claude の予備判定とユーザーの確認だけで、独立した 2 人目はいない」。これに対し REG:137「AI drafts are allowed only for C4f recalculation and C5 bibliographic matching」、REG:73「its C2b values come from the exploration coding」、REG:146「They become data only after being re-coded from the full text under these rules」
  - なぜ問題か: (1) 添付として凍結するコードブックが、C2b に AI の予備判定の列を定義している。これは REG の「AI は C4f と C5 だけ」と食い違う。(2) 使い回す尺度の C2b 値を「exploration coding」からそのまま取る（REG:73）のは、「re-coded ... become data only after」（REG:146）と矛盾する。しかも探索のコードは 2 人目がいない AI＋1 人のコードである。(3) 探索集合の一致の報告（REG:138「Reported separately for the exploration and the confirmation sets」）には、探索集合を 2 人で再コードすることが前提になるが、誰がいつ行うのかが無い。
  - 解消の条件: 探索集合を、確認集合と同じ手順（2 人が独立に・AI の下書きなし）で再コードすると決めて明記する。そのうえで、使い回す尺度の C2b はその再コードの値を使う。コードブックは、登録用の版で `coder` の値・限界の節・「研究者の決定待ち」の文を REG と揃えてから添付する。
  - 自信: 高

- [severity: major] 確認集合の構成が、後から起きる出来事の時期で分岐し、最小数の扱いも無い
  - 位置と引用: REG:97「If it is run and its eligibility decisions are finalised before stage 5, its newly included primary studies join the confirmation set. If not, the confirmation set consists of the additional candidates only. If it is too small for a table, we will report that and give the reason.」、REG:95「43 of them have not been screened.」
  - なぜ問題か: 主要な数の分母が、本検索がいつ終わるかで変わる。stage 5 の開始の時期は著者が決められるので、集合の大きさを見ながら時期を選ぶ自由度が残る。「too small for a table」の閾値も無い。S2・S4「describe what you will do if a minimum required sample size ... is not reached」。
  - 解消の条件: 確認集合を締める日付か出来事を固定する（例: 「YYYY-MM-DD の時点で source database が最終判定した記録」）。本検索で後から入る研究は、別の層として報告すると決める。表に出す最小の件数と、それを下回ったときの扱い（例: 件数だけ示して比率は出さない）を数で書く。
  - 自信: 高

- [severity: major] E5 で同一標本を除外する規則と、RQ4／C5 の「統合した単位」が噛み合わない
  - 位置と引用: REG:106「duplicate report or same sample (E5)」（除外）、REG:53「how many units remain after merging records the source database confirmed as the same sample?」、REG:126「Category: confirmed same sample by the source database (E5)」、REG:175-176「2. Same-sample records merged.」
  - なぜ問題か: source database が E5 で除外した記録は確認集合に入らないので、C5 の「confirmed same sample (E5)」の区分も、統合の後の単位の数も、定義の上で空になる。そうでなければ、E5 の記録を除外せずに残すという別の規則が隠れていることになる。どちらなのかで、RQ4 と感度分析 2 の意味が変わる。
  - 解消の条件: E5 の記録を「除外せず、親の記録に紐づけて保持する」のか、「除外する（その場合、RQ4 は E5 の件数を source database の判定から数えるだけ）」のかを、1 通りに決めて書く。
  - 自信: 中（source database の内部の扱いは、REG 以外に読んでいない）

- [severity: major] C2b の主要な集計の単位が決まっていない
  - 位置と引用: REG:158「C2b type × target, per instrument」、REG:73「The primary C2b count uses only the instruments first seen.」、REG:177「C2b counted with secondary type `MOT` included (a lenient count)」
  - なぜ問題か: 「per instrument」が何を数えるのか読み取れない。項目の数の度数なのか、尺度ごとの割合なのか、「その型の項目を 1 つ以上含む尺度の数」なのか。一つの尺度が複数の研究で使われたとき、尺度を 1 回と数えるのか、使用の回ごとに数えるのか。さらに CB:28 によれば、target は MOT・AVO・FUT（またはその副型）にしか付かない。ところが REG:122 と REG:51 は、すべての項目に target があるかのように書いている。この状態では type × target の表の形が決まらない。
  - 解消の条件: 主要な数を 1 文で定義する（例: 「確認集合で初めて見た尺度ごとに、主型の項目の数と全項目の数」）。尺度の重複の数え方と、target が空の項目の扱いを明記する。
  - 自信: 高

- [severity: major] 追試の問いに判定の基準が無い／SQ2 の言い方が C7 の中身より広い
  - 位置と引用: REG:47「The present review asks whether these problems also appear when the rules are fixed in advance」、REG:58「Is each study's main conclusion supported by its own attribution level, instrument and design?」、REG:128 の C7 の 3 条件
  - なぜ問題か: 記述にとどめる方針（REG:166）と、「also appear」という肯定か否定かの問いが、結びついていない。どの数なら「現れた」と書くのかが無いので、結果を見てから言い方を選べる（下位人格の言う過剰主張の余地）。C7 は C6a・C6b・C1 から機械的に導かれるだけで、尺度の質も設計の残りも見ていない。「supported by ... instrument and design」は、それより広いことを約束している。
  - 解消の条件: GSRR-57 に「現れた」と書く条件を置く（例: 確認集合で 1 件以上あれば「現れた」とし、比率の比較はしない）。あるいは問いを「確認集合でそれぞれの型が何件あるか」に言い換える。SQ2 は「C7 の 3 条件に照らして測ったものの範囲を超えているか」と書き直す。
  - 自信: 中

- [severity: minor] 人が見ていない集団の記録が確認集合に入るかどうか不明
  - 位置と引用: REG:77「Some groups (for example, health professionals) are therefore unscreened by a human.」、REG:99「We use the source database's final eligibility decisions without re-screening.」、REG:109「Screening in the source database is done independently by two screeners」
  - なぜ問題か: 2 人が独立にスクリーニングするという記述と、人が見ていない群があるという記述が並んでいる。見ていない群は、2 人のスクリーニングが済むまで待つのか、AI の判定だけで入るのか、入らないのか。どれなのかで、集団ごとの表の分母が変わる。
  - 解消の条件: 確認集合に入る条件を、「2 人が独立にスクリーニングして包含と判定したもの」に限ると明記する。
  - 自信: 中

- [severity: minor] C4 の (a)〜(c) と C7 で、判定の対象の選び方が決まっていない
  - 位置と引用: REG:125「(b) Direction of the main relation」、REG:128「it claims "AI fatigue"」「If no decision is possible, it is coded "cannot decide"」
  - なぜ問題か: 「main relation」をどう特定するのかが無い。仮説 1 か、要旨で最初に出る関係か。(c) で複数の基準があるときも同じ。C7(ii) の「claims "AI fatigue"」は語の一致で判定するのか、意味で判定するのか。「cannot decide」になる条件も無い。この状態では 2 人の一致が規則によるものか解釈によるものか区別できない。
  - 解消の条件: それぞれに選び方の規則を 1 文ずつ足す（例: 「要旨の結果の節で最初に報告された、AI 側の変数と疲労の関係」）。
  - 自信: 中

- [severity: minor] 較正の 5 件の抽出と、較正の後に変えてよいことの範囲が決まっていない
  - 位置と引用: REG:35「5 records drawn at random ... Any change to the definitions is registered as an amendment」
  - なぜ問題か: 乱数の作り方（seed・道具）が無い。較正を誰がどう行うのかも無い。2 人で話し合うなら、それ以降 coder 2 は「coder 1 の考え」を知った状態でコードすることになる（REG:136 の盲検とどう関係するのかが無い）。較正の後に変えてよい範囲（定義の文言だけか、区分の追加までか）も無い。
  - 解消の条件: seed と抽出の手順・較正の進め方・変えてよい範囲を書く。
  - 自信: 中

- [severity: minor] 一致の統計が、複数選択の項目と項目単位の項目で定義されていない
  - 位置と引用: REG:138「Cohen's kappa with 95% CI for categorical items」、REG:120「(all that apply)」
  - なぜ問題か: C1 は複数選択で、C2b は項目の単位、C1 と C4 は記録の単位である。どの単位で κ を計算するのか（水準ごとの二値か、代表値か）と、CI の求め方が無い。
  - 解消の条件: 項目ごとに一致を計算する単位と、CI の方法を書く。
  - 自信: 中

- [severity: minor] GSRR の必須項目に回答が無い・番号が食い違う
  - 位置と引用: REG:180「**[GSRR-63]–[GSRR-65] Amendments.**」、REG:92「**[GSRR-21]–[GSRR-32] Search.**」、REG:82「Python scripts ...」
  - なぜ問題か: S1「all items are mandatory」「indicate that in the corresponding field (including, ideally, the underlying reason)」。著者への連絡（28/29）・盲検（58）・指示書（36/45）・スクリーニングの判定の共有（41）・合成の手順の正当化（63）に、個別の回答が無い。63〜65 は様式の中身と違う。ソフトの版も無い。OSF の様式に入れるときに、そのままでは貼れない。
  - 解消の条件: 様式の 65 項目に 1 対 1 で答える。使わない手順は「Not applicable: 理由」と書く。検索のログを添付する（GSRR-25 の代わり）。
  - 自信: 高

- [severity: minor] 群分けの変数の定義が無い
  - 位置と引用: REG:57「("centre-A" in the source database) ... ("centre-B")」、REG:175「Peer-reviewed records only.」、REG:178「by population group」
  - なぜ問題か: centre-A／B の判定規則・誰が判定するか・プレプリントや会議録を「peer-reviewed」に入れるか・集団の区分の一覧が、REG の中に無い。どれも SQ1 と感度分析の分母を決める。
  - 解消の条件: それぞれの定義と区分の一覧を書くか、凍結した添付にする。
  - 自信: 中

- [severity: minor] コードブックが日本語で、翻訳が未定
  - 位置と引用: REG:197「to be translated into English before registration) **[TBD]**」
  - なぜ問題か: 登録の時に埋める予定の欄だが、凍結する規則の中身そのものなので、埋めないと登録できない。翻訳と原文の照合の手順（どちらを正とするか）も決まっていない。
  - 解消の条件: 英訳を添付し、日本語の版を正とするのか英語の版を正とするのかを書く。
  - 自信: 高

- [severity: nit] 撤回された記録を含めるのか除くのかが無い
  - 位置と引用: REG:150「Retractions and corrections are checked and linked to the original.」
  - 解消の条件: 撤回された記録を含めるのか除くのか、訂正の後の版でコードするのかを書く。
  - 自信: 中

- [severity: nit] 和解の規則に、効いていない条件がある
  - 位置と引用: REG:139「provided the co-author was not a coder for that record」
  - なぜ問題か: 役割の表（REG:23）では、共著者は coder ではない。条件が効く場面が無く、どの場面を想定しているのか読めない。
  - 解消の条件: 削るか、想定している場面を書く。
  - 自信: 低

## 4. 総合の推奨

major（直して再査読）
- 重く見る g で、主要な数え方のうち 4 つ（C6b の語のリスト・C4f の再計算の規則・C2b の集計の単位・確認集合の締め方）が、凍結の時点で 1 通りに決まっていない。
- 添付のコードブックと REG が、AI の役割と探索のコードの扱いで矛盾している。E5 と RQ4 も噛み合っていない。どれも、結果を見た後に選べる余地を残している（S5）。
- 開示と、探索集合／確認集合の分離の設計はよい。上の指摘は書き足しで直せるので、計画を立て直す必要は無い。

## 5. 読めなかった範囲・注入の疑い

- 読めなかった範囲: nuijten2016.txt は全文を読んでいない。Grep の抜き出し（statcheck の手順の Step 3・4、片側検定・多重比較・丸めの扱い、validity study、sloppiness の節の周辺）だけを読んだ。gsrr.txt・REG・CB・context-A.md は全文を読んだ。REG が参照する source database の内部の規則（E5 の扱い・centre-A／B の判定）、Murad & Wang 2017、PRISMA 2020、提案書 v2、decisions.md は、一覧の外なので読んでいない。
- 注入の疑い: 読んだ範囲には無い。nuijten2016.txt の読んでいない部分は確かめていない。
