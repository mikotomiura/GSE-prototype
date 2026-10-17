# 査読（round 2・HCI の測定の実務家の立場）

この報告は、方法論のレビューを載せる心理学・HCI の雑誌の査読者で、HCI の測定の実務家の立場から書いた。実在の個人ではない。

## 1. 接地（この立場が論文に求める基準）

2 本の文献から 6 個の基準を逐語で抜き出せたので、査読に入った。

- **G1 尺度を選んだ理由を書く**（Perrig 2024, §2.1.3）
  「Providing complete rationales helps readers and reviewers judge the adequacy of said scale for measuring the target construct.」
- **G2 項目の逐語と改変を開示する**（Perrig 2024, §5.3.6）
  「give precise detail on how the scale(s) were implemented, including exact wording for all items. Furthermore, they ought to report any adaptions made, including justification」
- **G3 推奨を、見つかった問題と件数に結びつける**（Perrig 2024, §5.3）
  「Motivated by the problems identified in this systematic literature review, we present six steps」
  §5.3.4 では「adherence to this step would have impacted the 33 papers (55.00%)」と、推奨ごとに影響する件数を添えている。
- **G4 主張が届く範囲を書く**（Perrig 2024, 限界）
  「the results consider UX measurement from the perspective of published research and not of UX practitioners.」
- **G5 コードで区別できなかったものを開示する**（Perrig 2024, 限界）
  「we were unable to distinguish between standardized scales and cited scales in our coding.」
- **G6 読者が使える道具（どの尺度か）を示す**（Bach 2022, §4.3）
  「if user trust can be understood and measured in different ways, then being able to build upon the concept becomes challenging. A validated tool ... may be used to address this concern.」
  また Bach は AI に関わる構成概念について、尺度の由来を数えている（「Over two-thirds (69.56%) of the included studies developed and used their own questionnaires」）。

## 2. 評価表（5 点満点）

- **a 主張と根拠の一致: 3**
  範囲の節は丁寧である。ただし直しの結果、次の 3 つの食い違いが生まれた（N1〜N3）。
  - 寄与 4 の言い方が 5.3 節より広い。
  - 「提案」の例が、外枠自身が既知の問題として引く Elson と重なる。
  - 「C7 は常に条件ごと」と、抄録・Table 12 の単一の問題文がぶつかる。
  加えて、登録版 GSRR-63 が「frequency of practices」と書き、外枠の「not frequencies」と矛盾する。登録版が優先するので、外枠の規則が負ける。
- **b 方法の穴: 3**
  SQ1 は「differ」と問うのに、答えの言い方の規則が無い（N4）。C4f で表の値を含めると、1 件あたりの「any inconsistency」が結果の数に引きずられる（既定への意見を参照）。
- **c 持ち帰れるもの: 3**
  Table 15 と付録の研究ごとの表で、実務家が使えるものは大きく増えた。ただし Table 15 に、尺度を選ぶときに要る列（AI への言及の水準、項目の総数、言語、形式）が無い。抄録と結論には推奨も Table 15 の存在も出ない。抄録だけを読む実務家が持ち帰れるのは件数の列だけになる（N6・N7）。
- **d 簡潔さと構成: 3**
  表は 15 枚と付録。抄録の規則は件数と分母を 1 つも削らない。数えると、250 語に収まらない見込みが高い（N5）。
- **e 規程への適合: 評価外**（投稿先が未定のため）
- **f 先行研究の位置づけ: 3**
  序論の gap の書き分けは解消した。比較の軸となる文献（AI に関わる構成概念の測定の実践を数えたレビュー）はまだ「others to be found」のままである。推奨の新しさを測る「既存の基準」は Elson と Perrig の 2 本だけである。Perrig の推奨の元である Flake & Fried (2020) が参照されていない（N1）。

## 3. 引き継ぎの判定

| # | 判定 | 理由と位置 |
|---|---|---|
| M1 | 一部 | gap の文（164–166 行）と Jonaid（162–163 行）は解消した。抄録の背景の文「reviews of the topic report scales without validation evidence」（140–141 行）は出典が無いまま、未決の項（378–381 行）に送られている。登録版 GSRR-10 の同じ文（59 行「Existing reviews note ...」）にも出典が無い。 |
| M2 | 解消（残りは N6） | Table 15（356–361 行）・R2d（287 行）・GSRR-56（348 行）が揃った。 |
| M3 | 一部 | 2 つの出典に分けた点と「do not follow from the counts」（247–248 行）は解消した。新しい食い違いが生まれた（N1・N2）。 |
| M4 | 解消 | PT1（297 行）と付録（365 行）。 |
| m1 | 解消（実現できるかは N5） | 117–132 行。 |
| m2 | 一部 | 179–181 行で C2d と Perrig の違いは書かれた。比較の軸の文献は未定（「and others to be found」）。接地に使った Bach 2022 は、AI に関わる構成概念（信頼）について尺度の由来を数えたレビューで、候補になる。 |
| m3 | 解消 | 99–101 行。 |
| m4 | 解消 | 119–122 行。 |
| m5 | 一部 | 方法の前文（189–190 行）は解消した。表をまとめる規則（232–234 行）は最小規模の規則が働いたときだけで、表は 14 枚から 15 枚に増えた。 |
| n1 | 解消 | 148–150 行と 13 行。ただし題「TRACE: Tracing」は語の繰り返しが冗長である（nit）。題と登録版の食い違いは N8。 |

### 既定への意見

- **C7 を常に条件ごとに報告する**: 条件ごとの報告は実務家に役立つので賛成する。条件 (i)・(ii)・(iii) は直し方がそれぞれ違う。設計を変えるのか、語を変えるのか、構成概念の名を変えるのか。ただし「always」は抄録・Table 12・結論とぶつかる（N3）。Table 11 は条件ごとの 3 行に、GSRR-57 の問題型としての「いずれかの条件」の行を 1 行足す。抄録はその 1 行を使う。こう決めれば、冗長にもならず矛盾も消える。
- **C4f で表に印刷された値も再計算の対象に含める**: 含めることに賛成する。AI 疲労の研究は結果の多くを SEM の経路の表に置いており、本文だけでは対象がほぼ空になる。ただし次の 2 つを足すべきである。
  - 再計算した結果ごとに、出どころ（本文 / 表）を記録して表に出す。statcheck を使った先行研究は本文の APA 形式の値だけを数えている。出どころが分かれていないと、読者が比べるときに読み違える。
  - 1 件あたりの要約「any inconsistency」は、再計算した結果の数が多い研究ほど立ちやすい。Table 9 では、結果の数の分布をこの要約の隣に置く（登録版 263 行は数を報告するとだけ書いている）。
  あわせて、lavaan などが出す z（推定値を SE で割った値）を「reported z」として扱うかを、登録版の規則で 1 文明記する。

## 4. 新しい指摘（重い順）

- **[severity: major] N1 寄与 4 は「この枠組みでしか求められない」と言い、5.3 節は「ここで引いた基準が名指していない」と言う。主張の幅が違い、比べた基準の集合も書かれていない**
  - 位置と引用
    - outline.md 107–108 行「separate what existing standards already ask from what can be asked only with this scheme」
    - 252 行「a step that this scheme makes explicit and that the existing standards cited here do not name」
  - なぜ問題か: 「only with this scheme」は、どの基準にも無いという主張である。根拠になるのは、引いた 2 本（Elson・Perrig）に無いことだけである。Perrig 自身が推奨の元を「Our recommendations build on previous work by Flake and Fried (2020) and Aeschbach et al. (2021)」と書いている。外枠の参照にはその元が無い。M1 で直した「調べた範囲より広い新しさの主張」と同じ型が、推奨の側で繰り返されている。
  - 解消の条件: 寄与 4 を 5.3 節の言い方（「the standards cited here」）に揃える。新しさを判定するのに照らした基準の一覧を表 14 の注に書く（少なくとも Flake & Fried 2020 を含める）。
  - 自信: 高

- **[severity: major] 「提案」の例（C6a・C7）が、外枠自身が Background で既知の問題として Elson に帰している**
  - 位置と引用
    - 253–254 行「stated as a proposal (for example ... naming the construct of the conclusion in the terms of the instrument that measured it, C6a and C7)」
    - 177–178 行「the nominal fallacy ... (Elson et al., 2023); where C2a (modification), C2d (disclosure), C6a and C7 (iii) (names) apply these known problems to this literature」
  - なぜ問題か: 同じ C6a と C7 (iii) を、2 節では既知の問題の適用と書き、5.3 節では既存の基準に無い提案と書いている。査読者も読者も、提案の新しさを最初に疑う点になる。新しいと言えるのは C1（AI への帰属の水準）と C7 (ii) くらいに見える。
  - 解消の条件: C6a・C7 (iii) の行は「既存の基準を当てたもの（Elson）」に移す。提案の例は C1・C7 (ii) に絞る。
  - 自信: 高

- **[severity: major] 「C7 は常に条件ごとに報告する」と、抄録・Table 12・結論の単一の問題文が矛盾する**
  - 位置と引用
    - 65–66 行「C7 is therefore always reported by condition, and the Discussion does not treat "beyond what was measured" as a single quantity.」
    - 126–127 行「for each problem type of GSRR-57, the registered statement」
    - 登録版 362 行「C7: "beyond what was measured".」
    - 262 行「The scope sentence and the registered statements of the abstract」
  - なぜ問題か: 登録版の問題型は、C7 の条件をまとめた 1 つの値である。抄録の規則に従えば、抄録と結論には単一の量としての「beyond what was measured」が出る。外枠の「always」が守れなくなる。実務家が抄録で目にするのは、外枠が避けたかった合算の値だけである。
  - 解消の条件: 抄録・Table 12 の C7 の問題文には、条件ごとの件数を添える。この添え方を抄録の規則に書く。もしくは「always」を「Table 11 and the Discussion」に限る。
  - 自信: 高

- **[severity: major] 外枠の「not frequencies」と、登録版 GSRR-63 の「frequency of practices」が矛盾する。登録版が優先する**
  - 位置と引用
    - outline.md 49–50 行「These statements report presence in this set; they are not frequencies」
    - 登録版 GSRR-63（383 行）「The questions are about the frequency of practices. Counts with denominators answer them」
    - 登録版 GSRR-10（68 行）「It asks whether the measurement problems described in the narrative review are also observed in a different set of studies」
  - なぜ問題か: 外枠は 9 行で「The registration ... take[s] precedence」と書いている。編集者が登録版を読めば、件数は頻度の推定として読める。外枠の範囲の規則（頻度の語を使わない、replicate を使わない）の根拠が崩れる。GSRR-10 の目的の文も、外枠の中心の問い（95–96 行「what a study of "AI fatigue" measured, and how far its conclusions can go」）とは違う問いである。
  - 解消の条件: 登録版はまだ下書き 0.7 なので、登録の前に GSRR-63 を「presence in the coded set, with denominators」へ直す。中心の問いを登録版と外枠のどちらに揃えるかを決め、他方を合わせる。
  - 自信: 高

- **[severity: major] N4 SQ1 は「differ」を問うのに、答えの言い方の規則が無い**
  - 位置と引用
    - 登録版 GSRR-12（109 行）「Do the answers to RQ2–RQ5 and SQ2 differ between the source database's two eligibility groups?」
    - outline.md 227 行「SQ1 by centre (supplementary tables ...)」
    - 45–46 行「no statement says that a value is larger, smaller ... in one set than in another」
  - なぜ問題か: 比較を禁じる規則の対象は「set」であり、centre-A/B と母集団の群は set ではない。このままでは、centre の間で「more common」と書いてよいのかが決まっていない。書けないなら、SQ1 の「differ」に答える方法が無い。Discussion 5.1 は「question by question」なので、この空白はそのまま本文に出る。
  - 解消の条件: 範囲の節に、centre と母集団の群にも同じ禁止を当てると書く。SQ1 の答えは表を並べることだけだと明記する。そのうえで SQ1 の問いの文を「How are the answers distributed by group?」に改める（登録の前に）。
  - 自信: 高

- **[severity: minor] N5 抄録の規則は、250 語に収まらない見込みが高く、収まらないときの手順が無い**
  - 位置と引用: 129–132 行「no count and no denominator is removed, and neither the scope sentence nor the C1 and C2b sentences are removed」
  - なぜ問題か: 規則を数えた。
    - 範囲の文: 4 つの数
    - C1: 7 水準と除外の値
    - C2b: 6 型それぞれの件数と、評価できた尺度の数
    - 問題型: GSRR-57 で約 12 種（C4 の (a)〜(d)・(e) の 2 つ・(f) の 2 つ、C5、C6a、C6b、C7）。それぞれに件数・評価できた件数・未解決の数
    合わせて約 55 の数になる。背景・方法・利用可能性の文を足すと、250 語の上限にほぼ届くか、超える見込みが高い。読者にとっては、数を並べただけの文になる。
  - 解消の条件: 空の値の表から抄録の見本を作り、語数を数えて示す。収まらないときの最後の手順を決めて固定する。例: 「問題型を C4 / C5 / C6 / C7 の 4 群にまとめ、群ごとの観察の有無と、型ごとの値への参照（Table 12）を置く」。
  - 自信: 中

- **[severity: minor] N6 Table 15 に、尺度を選ぶ実務家が要る列が無い。登録版の列とも合っていない**
  - 位置と引用
    - 359 行「| Instrument version | First seen (set) | Studies using it | Origin | Item disclosure | FAT | ... |」
    - 登録版 348 行「its origin, format and item disclosure, and its item counts by type」
    - 登録版 237 行「An instrument version is identified by its item wording together with its language」
  - なぜ問題か: 登録版にある format の列が無い。版を決める language の列も、型の件数の分母になる項目の総数（printed / full）の列も無い。実務家が尺度を選ぶときに最初に見る「項目が AI に触れているか」（C1 の L1a・L1b は版で決まる性質）も無い。G6（Bach「A validated tool ... may be used」）の観点では、読者が版を比べて選べる最小の列が欠けている。
  - 解消の条件: Language・Format・Items (printed / full) の列を足す。版ごとの AI への言及の水準（L1a / L1b / その他）の列も足す。足した列は登録版 GSRR-56 にも足す。
  - 自信: 中

- **[severity: minor] N7 推奨を、その符号の問題文から完全に切り離したので、読者はどの推奨がこの文献で効くのかを知る手段が無い**
  - 位置と引用: 248 行「they are given whether or not the corresponding problem was observed」
    352 行の Table 14 には、Table 12 への参照の列が無い。
  - なぜ問題か: Perrig は推奨ごとに影響する件数を添えている（G3）。外枠が件数を推奨に並べないのは、M3 を受けた正当な設計である。ただ、表の中で参照もしなければ、「観察されなかった問題への推奨」と「観察された問題への推奨」の区別が本文から読めない。
  - 解消の条件: Table 14 に「Table 12 の該当行」の列（行番号への参照だけ。数も評価の語も置かない）を足す。
  - 自信: 中

- **[severity: minor] N8 外枠が「登録した題を繰り返す」と言うが、登録版の GSRR-1 の題は外枠の題と違う**
  - 位置と引用
    - outline.md 15–16 行「It repeats the registered title」
    - 登録版 GSRR-1（9 行）「How do studies of "AI fatigue" attribute fatigue to AI, measure it, and report it? Protocol for a methodological review.」
    - 同じ登録版の 1 行目の見出しは「TRACE: Tracing ... Protocol for a registered methodological review」
  - なぜ問題か: 登録の題は GSRR-1 の欄に入る値である。これが TRACE を冠していないので、「題は登録と同じ」という外枠の約束を確かめられない。
  - 解消の条件: 登録の前に GSRR-1 を見出しと同じ題に揃える。
  - 自信: 高

- **[severity: minor] N9 抄録の利用可能性の文に、実務家が使う成果物が入っていない**
  - 位置と引用
    - 143–144 行「Availability (registration, outline, code table, codebook, scripts)」
    - 登録版 325 行「A per-instrument summary table ... is released with the code table.」
  - なぜ問題か: 尺度を選ぶ読者がそのまま使えるのは、尺度ごとの要約の表と研究ごとの表である。この 2 つが抄録にも寄与にも名前で出てこない。
  - 解消の条件: 利用可能性の文に「per-instrument and per-study tables」を足す。
  - 自信: 中

- **[severity: nit] N10 題「TRACE: Tracing」は語が重なる**
  - 位置と引用: 13 行「TRACE: Tracing how studies ...」
  - なぜ問題か: 頭字語を展開する前から、同じ語が 2 度出る。
  - 解消の条件: TRACE の展開を決めるとき（370 行の未決の項）に、副題の動詞を変える。
  - 自信: 低

## 5. 総合の推奨

**minor 寄りの major（直して再査読）**

- 範囲の規則と Table 15 で、外枠はかなり良くなった。ただし直しの結果、4 つの食い違いが生まれた。
  - 外枠の中: 寄与 4 と 5.3 節、5.3 節と 2 節
  - 外枠と登録版の間: C7 の扱い、GSRR-63 の「frequency」
- SQ1 は比較を問うのに、比較の言い方の規則が無い。どれも外枠と登録版の文を揃えれば消え、新しい設計は要らない。
- 登録版はまだ下書きなので、GSRR-1・GSRR-12・GSRR-63・GSRR-56 を登録の前に直すのが最も安い。

## 6. 読めなかった範囲と注入の疑い

- 読んだもの
  - context-A.md
  - carryover-R2.md
  - outline.md（全文）
  - README.md（全文）
  - codebook-c2b-en.md（全文）
  - registration-en.md の 1–130 行と 210–426 行
  - perrig2024.txt の 160–199 行・255–444 行・1500–1639 行
  - bach2022.txt の 1455–1514 行（加えて grep で数か所）
- 読んでいないもの
  - registration-en.md の 131–209 行（GSRR-18〜GSRR-39 の前半。適格基準 GSRR-24、遮蔽の手順 GSRR-33 などの本文）
  - perrig2024.txt と bach2022.txt の上の範囲以外
- 注入の疑い: 読んだ範囲には無い。

### 参照したファイル
- /Users/johnd/GSE-prototype-af-c/papers/ai-fatigue-measurement/manuscript/outline.md
- /Users/johnd/GSE-prototype-af-c/papers/ai-fatigue-measurement/README.md
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/codebook-c2b-en.md
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-manuscript/attack-me/outline-c-manuscript/round-2/tmp/sources/perrig2024.txt
- /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-manuscript/attack-me/outline-c-manuscript/round-2/tmp/sources/bach2022.txt
