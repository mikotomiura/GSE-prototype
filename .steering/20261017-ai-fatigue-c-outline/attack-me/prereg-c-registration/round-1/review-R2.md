査読の報告: 方法論のレビューの事前登録の下書き（registration-en.md draft 0.1）
立場: HCI の測定の実務の側の査読者（UX と人と AI の相互作用の研究で質問紙を使う側）。下位の視点は「で、読者は何に使えるのか」と問う実務家、および冗長さに厳しい読者。

読んだファイル:
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/attack-me/prereg-c-registration/round-1/context-A.md
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md（全文）
- /Users/johnd/GSE-prototype-af-c/.steering/20261014-ai-fatigue-core1-item-analysis/codebook.md（全文）
- 接地の 2 本: perrig2024.txt は一部、bach2022.txt も一部（範囲は 5 に書く）

## 1. 接地（この立場が論文に求める基準）

- 基準 1: 項目の文言を開示すること（Perrig et al. 2024）
  - 引用: "When using scales, researchers should share the exact wording"（§2.1.2、236 行目）
  - 引用: "give precise detail on how the scale(s) were implemented, including exact wording for all items."（Step 6、1612–1613 行目）
- 基準 2: 尺度の品質の根拠を報告すること。尺度を引用しただけでは足りない（Perrig et al. 2024）
  - 引用: "such a citation alone is insufficient proof of a scale's quality, leaving UX research vulnerable to QMPs"（1212–1214 行目）
  - 引用: "At the very least, they need to search for and report on past evidence for the scale's psychometric quality."（1596–1597 行目）
- 基準 3: 改変を透明に報告し、改変の後に品質を確かめ直すこと（Perrig et al. 2024）
  - 引用: "they need to be transparently reported, so readers and reviewers can judge their legitimacy."（1233–1234 行目）
  - 引用: "the quality of survey scales needs to be re-investigated whenever they are adapted"（1235–1237 行目）
- 基準 4: 構成概念を定義し、尺度を選んだ理由を書くこと（Perrig et al. 2024）
  - 引用: "being transparent about the definitions of constructs and the rationale for why researchers selected specific measures is crucial"（1469–1472 行目）
- 基準 5: メタ研究の側では、コードの区分を明確に定義し、コーダー間の一致を報告すること（Perrig et al. 2024）
  - 引用: 定義の範囲を自ら限った例として "We did not opt for terms such as validated scale, as this would require us to investigate secondary sources of scale validity."（662–664 行目）
  - 引用: 一致を報告した例として "the overall average IRR (Cohen's Kappa: M = 0.803) was substantial"（650 行目）
- 基準 6: 自作の質問紙が多いと研究どうしを比べられない。定義を明示しているかを数えること（Bach et al. 2022）
  - 引用: "Of the 16 studies, 12 (75%) developed their own questionnaires"（1025–1026 行目）
  - 引用: "if user trust can be understood and measured in different ways, then being able to build upon the concept becomes challenging."（1471–1472 行目）
  - 引用: "Of 23 studies, only seven explicitly define trust, while eight conceptualize it and the remaining nine provide neither."（1054–1055 行目）

## 2. 評価表

- a 主張と根拠の一致: 3
  - 所見: 背景には "the scales are not validated" と書いてある（47 行目）。しかし、各研究が妥当性や信頼性の根拠を報告しているかを数えるコードが無い。C2c は改変の手続きだけを見ている。表題の "report it" は C4 の内部の整合に絞られている。問いの立て方と、数える中身がずれている。
- b 方法の穴: 3
  - 所見: 確認集合が人の目で不均等にふるい分けられていること、著者が独立でないこと、無料の情報源しか使っていないことは、正直に開示されている。
  - 一方で開示されていない穴がある。centre-A と centre-B の区分は C1 と循環している（SQ1）。C6b の因果語が SEM の統計の語彙と衝突する。探索集合の C2b は AI の予備判定である。
- c 持ち帰れるもの: 2
  - 所見: 出すものは記述の集計だけである。実務家が使える形、たとえば尺度の一覧に帰属の水準と品質の根拠を付けたものや、報告のチェックリストが、出すものとして約束されていない。
- d 簡潔さと構成: 4
  - 所見: 3,046 語で、表とコードの対応が明快である（GSRR-49）。ただし GSRR の番号を範囲でまとめて書いたところでは、どの項目を「該当しない」としたかが見えない。
- e 規程への適合: 3
  - 所見: GSRR の逐語 1 は "indicate that in the corresponding field (including, ideally, the underlying reason)" と求める。下書きは [GSRR-21]–[GSRR-32]、[GSRR-33]–[GSRR-42] などをひとまとめにしている。
  - 逐語 3 の contingency plan は、コーダー 2 が見つからない場合と、確認集合が小さすぎる場合の閾値について欠けている。
- f 先行研究の位置づけ: 2
  - 所見: 報告の手引きは挙げてある。しかし HCI と UX の測定の実務についてのメタ研究（尺度が自作か引用か、項目を開示しているか、品質の根拠を報告しているかを数えた先例）を参照していない。そのため、コードがそれらの先例と比べられるように作られていない。参考文献は 3 本だけである。
- g 固定の十分さ: 2
  - 所見: 次の点が 1 通りに決まっていない。
    - C2b を研究単位にまとめる規則
    - C6a の「main instrument」
    - C7 (iii) の「its construct」
    - C4f で何を再計算するか
    - C6b の因果語の一覧（後で決める）
    - target の区分に「その他」が無いこと
    - C1 の順序と C7 (ii) の食い違い
    - 複数の値を付けるコードの kappa の計算法

## 3. 指摘の一覧（重い順）

- [severity: major] 確認集合の C2b に、AI の予備判定が人 1 人の確認だけで入る。独立した 2 人目のコーダーという主な安全策と矛盾する
  - 位置と引用:
    - registration-en.md 73 行目「If a confirmation study uses one of the four instruments already coded at item level, its C2b values come from the exploration coding.」
    - 137 行目「AI drafts are allowed only for C4f recalculation and C5 bibliographic matching.」
    - codebook.md 44 行目「`coder`: `claude-prelim`（Claude の予備判定）」
    - codebook.md 49 行目「判定者は Claude の予備判定とユーザーの確認だけで、独立した 2 人目はいない。一致は測っていない」
  - なぜ問題か: 再利用した値は、AI の下書きを C4f と C5 に限るという規則にも、2 人のコーダーが独立に付けるという規則（135 行目）にも外れる。再利用した値は副次の集計とされているが、感度分析 3 と探索集合の表に出る。基準 5（Perrig: 一致を報告する）にも届かない。
  - 解消の条件: 再利用する 4 つの尺度の C2b を、確認集合のコーディングの前に 2 人のコーダーが独立に付け直し、kappa を報告する、と書く。あるいは、再利用した値を確認集合のすべての集計から外す、と書く。
  - 自信: 高

- [severity: major] C1 の代表値の順序と C7 (ii) の規則が食い違い、質的研究が「beyond」に分類されない
  - 位置と引用: 120 行目の順序「… definition only / variable label only / interview-guide theme only / none」と、128 行目「(ii) it claims "AI fatigue" while the C1 representative value is variable label only or none」
  - なぜ問題か: interview-guide theme only は variable label only より弱い水準として並んでいる。それなのに C7 (ii) では「beyond」の条件に入っていない。順序に従えば、variable label only より弱い水準が「within」に分類される。これは意図していない分岐だと考える。
  - 解消の条件: C7 (ii) の条件を「variable label only, interview-guide theme only, or none」とする。あるいは、質的研究を順序の別の列に分ける理由を書く。
  - 自信: 高

- [severity: major] C2b の集計の単位とまとめ方が決まっていない
  - 位置と引用: 158 行目「C2b type × target, per instrument」、122 行目「Item content (per item)」
  - なぜ問題か: コードは項目ごとに付ける。集計は尺度ごとである。項目の数を数えるのか、割合を出すのか、「MOT を 1 項目でも含む尺度」を数えるのかが決まっていない。どれを選ぶかで答えが変わる。
    - 加えて、codebook.md 28 行目は target を MOT・AVO・FUT にだけ付けると定めている。登録の本文はこれを書いていない。RQ2 の「Toward which target」は、IRR と OTH の項目について答えが空になる。
    - target の区分に「その他」が無い（codebook.md 30–36 行目）。たとえば "video conferencing" の場面を問う項目に付けられる値が無い。
  - 解消の条件:
    - 尺度ごとのまとめ方の規則を 1 つに決めて書く（例: 型ごとの項目数と割合、および「含む／含まない」の 2 値）。
    - target を付ける範囲を登録の本文に書く。
    - target に `OTHER` を加える。
  - 自信: 高

- [severity: major] C6a の「main instrument」と、C7 (iii) の「its construct」が定義されていない
  - 位置と引用: 127 行目「the name and item content of the main instrument」、128 行目「(iii) its construct is a C6a mismatch」
  - なぜ問題か: 尺度ごとに 1 行を立てるので（116 行目）、1 本の研究に疲労の尺度が複数ある場合がある。その場合に主な尺度を選ぶ規則が無い。また C6a は表題についてのコードであり、C7 は結論の文についてのコードである。「its construct」が結論の文の構成概念を指すのか、表題の構成概念を指すのかが分からない。
  - 解消の条件:
    - 主な尺度を選ぶ規則を書く（例: 抄録が結果として名指す最初の疲労の変数を測る尺度。決められなければ「cannot decide」）。
    - C7 (iii) を「結論の文が名指す構成概念が、主な尺度の名前と項目の中身に合わない」と書き直す。
  - 自信: 中

- [severity: major] C6b の因果語の一覧がまだ無い。SEM の統計の語彙と衝突し、数が膨らむ
  - 位置と引用: 127 行目「The list of causal terms will be fixed before calibration coding (examples: effect, impact, lead to, induce)」
  - なぜ問題か: 横断の SEM の研究は、"direct effect" や "indirect effect" を統計の用語として使うのが普通である。素朴に照合すると、ほとんどの横断研究が「mismatch」になる。そうなると C6b と C7 (i) が設計の分布を言い換えるだけになる。
    - 一覧を登録の後に決めることは、事前の固定にならない。
    - 比べる相手の「design」の値（横断・縦断・実験など）も定義されていない（62 行目では grouping の変数として名前が出るだけ）。
  - 解消の条件:
    - 因果語の一覧を登録に含める。
    - 統計の用語として使った場合（"indirect effect" など）を扱う規則を書く（除外する、または別に数える）。
    - design の値と、その判定の規則を書く。
  - 自信: 中

- [severity: major] 品質の根拠と項目の開示を数えるコードが無く、背景の主張と表題の "report it" に届かない
  - 位置と引用: 47 行目「Existing reviews note that the scales are not validated」、125 行目の C4 は内部の整合だけ、123 行目の C2c は改変の手続きだけ
  - なぜ問題か: この立場では、尺度を使う研究にまず求めるのは、項目の開示、信頼性の値、妥当性の根拠、尺度を選んだ理由である。
    - 接地: Perrig「At the very least, they need to search for and report on past evidence for the scale's psychometric quality.」
    - 接地: Perrig「including exact wording for all items」
    - この 2 つが無いと、実務家は「どの AI 疲労の尺度なら使えるのか」を持ち帰れない。
    - 「items unavailable」は C2b の欠測として扱われるだけで、報告の実務としては数えられていない。
  - 解消の条件: 尺度ごとのコードを加える。
    - 項目の全文を開示しているか（全部／一部／無し）
    - その標本での信頼性の値を報告しているか
    - 妥当性の根拠（因子分析、既存の文献の引用、無し）
    - 尺度を選んだ理由を書いているか
    - Perrig の区分（cited と self-developed）と比べられる形にする
    - 加えないなら、範囲から外した理由を登録に書く
  - 自信: 中（範囲を決めるのは著者だが、背景の文との食い違いは確か）

- [severity: major] SQ1 の centre-A と centre-B の区分が C1 と循環している。区分の定義も登録に無い
  - 位置と引用: 57 行目「studies that attribute fatigue to AI in their measurement ("centre-A" in the source database)」
  - なぜ問題か: centre-A は「測定のところで AI に帰属させる」研究と定義されている。これは C1 の上位の水準とほぼ同じである。そのため、RQ1 を centre ごとに比べても、区分の定義をなぞるだけになる。
    - 区分は外の文献データベースが決める。判定の規則と、誰が判定するか（AI の予備判定を読んだ人を含むか）が書かれていない。
  - 解消の条件:
    - centre-A と centre-B の判定の規則を逐語で載せる。
    - C1 を区分ごとに比べることは、区分の定義上は情報にならないと明記する。または、SQ1 から C1 を外す。
  - 自信: 中

- [severity: major] 予見できる逸脱に contingency plan が無い（GSRR の逐語 3）
  - 位置と引用:
    - 13 行目「Coder 2: **[TBD]**」
    - 97 行目「If it is too small for a table, we will report that and give the reason.」
  - なぜ問題か: 2 人目のコーダーは「the main safeguard」とされている（78 行目）。それなのに、見つからない場合の手当てが書かれていない。また「too small」の閾値が無いので、事後に決めることになる。規程の逐語 3 は "provide a contingency plan for these deviations in the relevant parts of the registration" と求めている。
  - 解消の条件:
    - コーダー 2 を確保できない場合に何をするかを書く（例: 確認の主張を立てず、探索の研究と表記する）。
    - 表を出す最小の件数（例: 確認集合が 10 件未満なら集計を記述に限る）を数で書く。
  - 自信: 高

- [severity: minor] C4f で何を再計算するかが決まっていない
  - 位置と引用: 125 行目「(f) Recalculation from reported values: matches within rounding / does not match (which) / cannot be calculated」
  - なぜ問題か: 再計算の対象（たとえば負荷量からの AVE と CR、β と SE からの t、自由度と統計量からの p、表の合計）を列挙していない。対象をどこまで広げるかで不一致の数が変わる。AI の下書きもここに使う。
  - 解消の条件: 再計算の対象と、丸めの許容幅を列挙して固定する。
  - 自信: 中

- [severity: minor] 複数の値を付けるコードと境界の項目について、一致の計算法が決まっていない
  - 位置と引用:
    - 138 行目「Cohen's kappa with 95% CI for categorical items」
    - 120 行目の C1 は「all that apply」
    - 122 行目「Boundary items carry a secondary type」
  - なぜ問題か: 複数の値を付けるコードに Cohen の kappa はそのまま使えない。値ごとの 2 値の kappa にするのか、代表値で計算するのかによって、報告する一致の値が変わる。探索集合の一致を報告するとあるが（138 行目）、探索集合を誰が独立にコード化するのかも書かれていない。
  - 解消の条件:
    - C1 は値ごとの 2 値の kappa と代表値の kappa、C2b は主の型の kappa、のように計算の単位を書く。
    - 探索集合を付け直す人を書く。
  - 自信: 中

- [severity: minor] GSRR の番号を範囲でまとめているため、該当しない項目とその理由が見えない
  - 位置と引用: 92 行目「**[GSRR-21]–[GSRR-32] Search.**」、99 行目「**[GSRR-33]–[GSRR-42] Eligibility.**」、150 行目「**[GSRR-52]–[GSRR-54].**」
  - なぜ問題か: 規程の逐語 1 は、該当しない項目をそれぞれの欄で示し、できれば理由を添えるよう求めている。OSF の様式では欄ごとに入力するので、登録の時に詰まる。
  - 解消の条件: 番号ごとに 1 行を立て、「Not applicable: no own search (records from the source database)」のように書く。
  - 自信: 中

- [severity: minor] 添付のコードブックが、登録の外の文書を基準の根拠にしている。固定の後の追記もある
  - 位置と引用:
    - codebook.md 3 行目「区分はユーザーが決めた（decisions.md 判断 2）」
    - codebook.md 14 行目「提案書 v2 §6.1 の M4」
    - codebook.md 51–53 行目「追記（2026-10-17・基準は変えない）」
  - なぜ問題か: 登録の読者は decisions.md や提案書を読めない。追記は、固定の後に境界の例を足している。「基準は変えない」と書いてあるが、例は判定に効く。英訳もまだである（197 行目）。訳すときに定義がずれるおそれがある。
  - 解消の条件:
    - 英訳した版で、外の文書への参照を自己完結した説明に置き換える。
    - 版の番号と固定の日付を付ける。
    - 日本語版と英語版のどちらが正本かを書く。
  - 自信: 高

- [severity: minor] 背景の「先行研究と違う点」の主張が、検索の範囲の書き方として弱い
  - 位置と引用: 47 行目「Within our searches, we did not find a review that tabulates, study by study, …」
  - なぜ問題か: 無料の情報源しか使っておらず、検索の文字列も残っていない（93 行目）。そのため「見つからなかった」を確かめられない。COSMIN を使ったレビューの名前も挙げていない。
  - 解消の条件: 比べた既存のレビューを参考文献に挙げ、それぞれと何が違うかを 1 行ずつ書く。
  - 自信: 中

- [severity: minor] peer-reviewed の定義が無い
  - 位置と引用: 62 行目「peer-reviewed or not」、175 行目「Peer-reviewed records only.」
  - なぜ問題か: プレプリント、会議録、学位論文の扱いが決まっていない。感度分析 1 の分岐になる。
  - 解消の条件: どの種類を peer-reviewed とみなすかを列挙する。
  - 自信: 中

- [severity: nit] 解消の手続きの但し書きが、役割の表と噛み合わない
  - 位置と引用: 139 行目「provided the co-author was not a coder for that record」
  - なぜ問題か: 役割の表（23 行目）では、コーダーは第一著者とコーダー 2（規則を書いていない人、13 行目）である。共著者がコーダーになる経路は無いように読める。
  - 解消の条件: 共著者がコーダー 2 になりうるのかを明記する。
  - 自信: 低

- [severity: nit] 感度分析 3 で、副の型を数えに入れるのが MOT だけである
  - 位置と引用: 177 行目「C2b counted with secondary type `MOT` included (a lenient count).」
  - なぜ問題か: AVO、IRR、FUT の副の型を数えない理由が書かれていない。
  - 解消の条件: 理由を 1 文書く。または、すべての副の型について数える。
  - 自信: 低

## 4. 総合の推奨

推奨: minor と major の境目。判断としては major（直してから再査読）とする。

理由:
1. 開示と工程の設計は誠実である。ただし、主な安全策である独立した 2 人目のコーダーに、2 つの穴がある。AI の予備判定の C2b を再利用すること、およびコーダー 2 が見つからない場合の手当てが無いことである。
2. 数え方が 1 通りに決まっていないところが複数ある。C2b のまとめ方、main instrument、C1 と C7 (ii) の食い違い、因果語の一覧、C4f の範囲、複数の値を付けるコードの kappa である。凍結しても、事後に分岐が残る。
3. 実務家が持ち帰れるもの（尺度ごとの品質の根拠と項目の開示）を数えておらず、背景の主張とずれている。範囲を決め直すかどうかは著者の判断だが、決めた結果を登録に書く必要がある。

## 5. 読めなかった範囲と、注入の疑い

読んでいない範囲:
- perrig2024.txt は、Grep で当たった行の周辺（640–699、1200–1279、1440–1639 行目）だけを読んだ。方法の節の前半（検索、適格の基準）、結果の大部分、参考文献は読んでいない。
- bach2022.txt は、1015–1094 行目と 1455–1519 行目だけを読んだ。方法の節、表の全体、参考文献は読んでいない。
- 登録が名指す Murad & Wang 2017、PRISMA 2020、MISTIC の本文は渡されていないので読んでいない。それらへの適合は評価していない。
- 外の文献データベースの centre の定義、decisions.md、提案書 v2 は、一覧の外なので読んでいない。

注入の疑い: 読んだ範囲には無い。