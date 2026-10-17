# 査読の記録（round 3・立場: HCI の測定実務の専門家／下位人格: 「で、読者は何に使えるのか」と問う実務家・冗長さに厳しい読者）

読んだファイル: brief-R2.md、context-A.md、carryover-R2.md、registration-en.md（全文）、codebook-c2b-en.md（全文）、perrig2024.txt と bach2022.txt（grep で当たった箇所と、その前後だけ）。

## 1. 接地（この立場が論文に求める基準）

- **K1 項目の文言を開示すること**（Perrig 2024, l.236-240）: "When using scales, researchers should share the exact wording of the items they used in their research ... Sharing the items used allows readers to judge which version of a scale was employed, if or how items were adapted"
- **K2 尺度の改変は報告し、理由も添えること**（Perrig 2024, l.1232-1235）: "While some adaptions are justifiable (e.g., adapting the wording of items to the study context), they need to be transparently reported, so readers and reviewers can judge their legitimacy. This includes clear reasoning for those adaptions."
- **K3 信頼性はその標本で測り直すこと**（Perrig 2024, l.1324-1332）: "researchers should calculate and report evidence for a scale's reliability ... A scale's psychometric properties cannot be assumed equal across samples"
- **K4 定義は曖昧でなく、隣の構成概念と区別できること**（Perrig 2024, l.1477-1480・MacKenzie の引用）: "Good definitions should (a) specify the construct's conceptual theme, (b) in unambiguous terms, ... and that (d) clearly distinguishes it from related constructs."
- **K5 コーディングの信頼性を示すこと**（Perrig 2024, l.646-650）: "calculate the overall inter-rater reliability (IRR) of the codings ... (Cohen's Kappa: M = 0.803)"
- **K6 測り方がばらつけば知見を積み上げられないこと**（Bach 2022, l.1471-1472）: "if user trust can be understood and measured in different ways, then being able to build upon the concept becomes challenging."

## 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 4 | 結論の語は GSRR-57 で「observed / not observed」と、件数と分母に縛られている。集合どうしの比較もしないと明記している（l.340）。ただし後述の C1 の範囲の曖昧さが残ると、RQ1 の答えが意図と違う量になりうる。 |
| b 方法の穴 | 3 | 前の round の穴（登録の後の選別・較正）は手当てされた。新たな穴が 2 つある。小さい集合では較正が除く件数に上限が無い。探索の集合で較正すると、その記録の再コードが汚れる。 |
| c 持ち帰れるもの | 3 | 尺度ごとの一覧（GSRR-50）とコード表の公開は、尺度を選ぶ実務家に使える。一方、読者が自分の研究で使える形、たとえば問題の型 → 確かめ方の対応表になるかは、まだ見えない。ただし原稿が無い段階なので欠陥にはしない。 |
| d 簡潔さと構成 | 4 | 65 項目に 1 対 1 で、読みやすい。重複が少し残る（GSRR-47 の target の kappa が 2 回出る・GSRR-41 と GSRR-50）。 |
| e 規程への適合 | 4 | 該当しない項目には理由が付いている（GSRR-26・27・61。逐語 1 に適う）。予見できる逸脱には代替の計画がある（GSRR-39 の最小件数・GSRR-56 の末尾。逐語 3 に適う）。late stratum には期限が無く、これは逐語 3 の「代替の計画」が欠けた形に当たる。 |
| f 先行研究の位置づけ | 4 | Perrig 2024 と COSMIN 系の論文を GSRR-10 に置いた。先行研究の無さは 16 回の検索で確かめたと、範囲つきで書いてある。 |
| g 固定の十分さ | 3 | 規則の多くは 1 通りに決まった。ただし次の 4 か所に分岐が残る。C1 の対象（どの尺度か・主たる尺度か）、語の族に 2 つ当たる名前、項目が開示されない尺度の origin、較正を止める条件の「every code」。 |

## 3. 引き継ぎ（R2）の判定

| 指摘 | 判定 | 根拠 |
|---|---|---|
| M1 | 解消 | l.252 の除外の一覧と l.253 の affect の扱い |
| M2 | 解消 | l.233 の 3 つの族（族が重なるときの扱いは新しい指摘 N2 として別に挙げる） |
| M3 | 解消 | l.219 |
| M4 | おおむね解消 | l.199-201。ただし小さい集合の分岐に新しい穴がある（N3） |
| M5 | 解消 | l.168-171・l.65 の 3 項目 |
| m1 | 解消 | l.233「This is a name check only」 |
| m2 | 解消 | l.238・l.240 |
| m3 | 解消 | l.225 の L2・l.282 |
| m4 | 解消 | l.99 |
| m5 | 解消 | l.265・l.283・l.290 |
| m6 | 解消 | l.58 |
| n1 | 解消 | l.302 |
| n2 | 解消 | l.149 |

## 4. 指摘の一覧（重い順）

- **[severity: major] N1 C1 の各水準がどの尺度を指すのかが書かれていない。主たる尺度との関係も決まっていない**
  - 位置と引用: registration-en.md:225「L1a: the item wording of a multi-item scale mentions AI」。同:216「C1 and C3–C7 are coded per record」。同:234 の (ii)「while the C1 representative value is L4, L5 or L6」
  - なぜ問題か: L1a の定義には「fatigue」の語が無い。字義どおりに読むと、C3 の AI 側の尺度（依存の尺度など。項目に AI が必ず出る）だけで、ほぼ全件が L1a になる。また C1 は記録ごとで、代表値は「first applicable level」である。このため、副次の疲労尺度が L1a なら、主たる尺度が L4 の研究でも C7 (ii) が発火しない。C6a と C7 (iii) は主たる尺度に依るので、C7 の 3 条件が別々の対象を見ることになる。K4 の「unambiguous terms」に反する。
  - 解消の条件: L1a〜L6 の主語を「the fatigue instrument(s)」と明記する。そのうえで、C7 (ii) が使うのを記録の代表値にするか、主たる尺度の水準にするかを 1 つに決めて書く（たとえば C1 に「main-instrument level」の欄を足す）。
  - 自信: 中（コーダーは RQ1 の文から「fatigue」を補って読むだろう。ただ、登録の文として 1 通りにはなっていない）

- **[severity: major] N2 語の族に 2 つ当たる名前、どの族にも当たらない語、語形の扱いが決まっていない**
  - 位置と引用: registration-en.md:233「Term families: {fatigue, tiredness, 疲労, 疲れ}; {exhaustion, depletion, 消耗, 枯渇}; ... Values: same family / different family / ...」。同:234 の (iii)「in a different term family (C6a) from the name of the main instrument」
  - なぜ問題か: 探索の集合に入っている Zoom Exhaustion & Fatigue Scale（codebook l.68）は、1 つの名前が 2 つの族にまたがる。この場合に same と different のどちらを付けるかが決まっていない。次に、結論の語が族の外にある場合（technostress・digital fatigue の扱い）、また結論に構成概念の語が無い場合の値も無い。さらに、語形（tired・fatigued・exhausted）や複合語（techno-exhaustion）を族に含めるのかも書かれていない。いずれも C6a と C7 にそのまま効く。
  - 解消の条件: 3 点を規則として書く。(1) 名前が複数の族に当たるときは「1 つでも共有すれば same」とするか、別の値を立てる。(2) 族の外の語と、語が無い場合の値を足す（C7 (iii) ではその場合を「not applicable」にする、など）。(3) 語形と複合語を含めるかを書く（C6b の「inflected forms」と同じ書き方でよい）。
  - 自信: 高

- **[severity: minor] N3 小さい集合で較正を探索の記録に移す規則に、どの記録を使うか（seed）が無い。較正に使った記録をその後どう扱うかも無い**
  - 位置と引用: registration-en.md:200「If the pool has 20 studies or fewer, calibration is done on exploration-set records instead」。同:45「The exploration set is re-coded under the same rules」
  - なぜ問題か: 2 つある。第 1 に、引き方と seed が書かれていない。第 2 に、較正で定義を練るのに使った探索の記録が、主たるコーディングで「独立に」再コードされ、別の表に載る。較正と本番が同じ記録になり、その表の一致率が上に偏る。
  - 解消の条件: 探索の 10 件から引く方法（seed）を書く。較正に使った探索の記録は、探索の表から除くか、印を付けて分けて示す。
  - 自信: 高

- **[severity: minor] N4 較正で除く件数に上限が無い**
  - 位置と引用: registration-en.md:265「five more records are drawn ... up to two further rounds」。同:200「20 studies or fewer」
  - なぜ問題か: 候補が 21〜30 件だと、3 回の較正で最大 15 件が除かれる。21 件なら確証の集合は 6 件になり、GSRR-39 の「件数だけ」の分岐に落ちる。前もって決めた基準によって、主たる集合の大半を失いうる。b（妥当性への脅威）に当たる。
  - 解消の条件: 除く件数の上限を決める（たとえば候補の 25% まで）。上限を超えるときは、探索の記録で較正を続ける規則を書く。
  - 自信: 中

- **[severity: minor] N5 較正を止める条件「every code」の単位が決まっていない**
  - 位置と引用: registration-en.md:265「It ends when percentage agreement is at least 80% on every code」
  - なぜ問題か: C2a の modification は 7 つの下位欄を持ち、C4 は (a)〜(f) の 6 つの規則を持つ。C1 は水準ごとの二値である。どの単位で 80% を測るのかで、止まるかどうかが変わる。C7 のように導出される値を含めるかも書かれていない。「not applicable」が多い欄は一致率が水増しされる点も同じ単位の問題に含まれる。
  - 解消の条件: 測る単位を、GSRR-47 の kappa の単位と同じ一覧で固定する。導出値は除くと書く。
  - 自信: 中

- **[severity: minor] N6 項目が開示されない尺度の origin の値が無い**
  - 位置と引用: registration-en.md:226「"Unchanged" requires a verbatim match with the source.」。同:229「Item disclosure: all / some / none」
  - なぜ問題か: 項目を開示する報告は少ない（Perrig 2024, l.252「reporting items is uncommon in scale-based UX research」）。開示が無いと、verbatim の照合ができない。その場合、origin の adapted / unchanged が決められないが、それに当たる値が無い。実務上いちばん多い型になりうる。
  - 解消の条件: origin に「general scale, modification not verifiable」を足す。または、modification を全部 not verifiable にしたうえで、origin を報告の記述どおりに付けると書く。
  - 自信: 高

- **[severity: minor] N7 探索の段で保留になった 3 件と、late stratum の境界が決まっていない**
  - 位置と引用: registration-en.md:81「3 pending for unavailable full text」。同:195「the exploration records, even if found again」。同:198「Studies included after 2026-12-31 are reported as a separate stratum」
  - なぜ問題か: 保留の 3 件は、探索の集合（10 件）にも追加の候補（221 件）にも入らない。全文が手に入った場合の行き先が無い。また late stratum には締切が無い。二重コードするかも書かれていない。
  - 解消の条件: 3 件の行き先を 1 つに決める（たとえば探索の集合に入れる）。late stratum の締切（stage 5 の開始の日など）と、コードの手順を書く。
  - 自信: 高

- **[severity: minor] N8 C6b の「manipulation」の判定が、純粋なデザインと混合のデザインで基準が違う**
  - 位置と引用: registration-en.md:258「manipulation: quasi-experimental or pre–post with an intervention」。同:259「mixed: manipulation if any component manipulates the AI-side variable」
  - なぜ問題か: 混合のデザインでは AI 側の変数を操作したかを問う。一方、純粋な準実験では、AI と無関係な介入（休憩の訓練など）でも manipulation になる。その結果、「AI use affects fatigue」は match になってしまう。加えて、因果の語が数えられるのは「a claim about a relation」だが、どの変数間の関係かが書かれていない。
  - 解消の条件: 3 つのデザイン全部に「AI 側の変数を操作したか」の基準を揃える。数える関係を、AI 側の変数と疲労の関係に限るかどうかを書く。
  - 自信: 中

- **[severity: minor] N9 「abstract's results」が無い場合の判定が曖昧である**
  - 位置と引用: registration-en.md:220「If the abstract has no results, it is the instrument described first in the methods.」
  - なぜ問題か: 構造化されていない抄録で、どこまでを「results」と読むかが決まっていない。結果の文はあるが見出しが無い、という場合である。主たる尺度と主たる関係は C4b・C6a・C7 の入口なので、ここが分かれるとそれらが全部ずれる。
  - 解消の条件: 「results」を「a sentence reporting a finding」のように文の単位で定義する。
  - 自信: 中

- **[severity: minor] N10 C2b の副次の型と boundary の信頼性が報告されない。項目を入手できない尺度の数え方も無い**
  - 位置と引用: registration-en.md:280「kappa for the primary type and, separately, for the target」。同:354 の感度分析 3。同:227「Items that cannot be obtained are coded "items unavailable"」
  - なぜ問題か: 感度分析 3 は副次の型を使うのに、その一致は示されない（K5）。また「items unavailable」の尺度が、GSRR-39 の「fewer than 3 instruments」の数に入るのかが決まっていない。
  - 解消の条件: boundary と secondary_type の kappa を足す。最小件数を数えるのは、項目を入手できた尺度だけと書く。
  - 自信: 中

- **[severity: nit] N11 重複**
  - 位置と引用: registration-en.md:280 と :282（target の kappa が 2 回出る）。GSRR-41 と GSRR-50（公開物）。
  - 解消の条件: 1 か所にまとめる。
  - 自信: 高

- **[severity: nit] N12 C2d の「Reason for choosing the instrument: given」に基準が無い**
  - 位置と引用: registration-en.md:229
  - なぜ問題か: 先行研究で使われたと引くだけで理由に数えるのかが決まっていない（K2「clear reasoning」）。
  - 解消の条件: 1 文で基準を書く。
  - 自信: 中

## 5. 総合の推奨

**minor（直してから凍結）**
- 引き継ぎの 13 件は、実質すべて解消した。設計の骨格（集合の分け方・順の固定・結論の語）は凍結に耐える。
- 残る major の 2 件（N1・N2）は、どちらも主要な数え方の入口（C1・C6a・C7）にある分岐である。ただ、解消の書き方は 1 通りに決まっていて、規則を数行足せば消える。
- minor は境界の件（N3〜N10）で、再査読は要らない。ただし N1・N2 は、直した文をメインが目で確かめてから凍結すること。

## 6. 読めなかった範囲と注入の疑い

- **読んでいない**: perrig2024.txt と bach2022.txt の全文。grep で当たった箇所と前後（Perrig l.230-259・646-650・1225-1236・1320-1333・1465-1489、Bach l.1458-1489 ほか）だけを読んだ。Murad & Wang 2017・PRISMA 2020・GSRR の原文は渡されていないので、読んでいない。
- **注入の疑い**: 無し（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。
