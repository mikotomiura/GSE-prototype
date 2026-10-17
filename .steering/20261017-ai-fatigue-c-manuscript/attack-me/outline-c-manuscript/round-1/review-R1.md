# 査読（心理測定・構成概念の妥当性の立場）—— outline-c-manuscript round-1

査読者の立場: 心理測定と構成概念の妥当性を専門とする査読者。下位人格は「その測定は本当にそれを測っているか」を疑う懐疑家。実在の個人ではない。

## 1. 接地: この立場が論文に求める基準

- **G1 名前と中身を混同しない（Elson et al., 2023）**: "They involve a nominal fallacy: that a measure's name tells you about its contents or what it measures"
- **G2 測定の柔軟性を明らかにするのは方法論のレビューである（Elson et al., 2023）**: "Dropping, adding, and altering items in self-report scales ... all occur while researchers not only refer to the same construct, but actually to the same nominal instrument" / "only a methodological literature review will reveal that many studies used, for instance, unique aggregation algorithms, scoring strategies, or items, often with unknown psychometric consequences."
- **G3 項目を全部報告し、改変を正当化する（Elson et al., 2023, SOBER Table 1）**: "Comprehensive Reporting Report all of the items, stimuli, instructions, procedural parameters" / "Justify Modifications Prove that any deviation or modification to an existing measure is either meaningful ... or irrelevant"
- **G4 新しく作った測定には妥当性の証拠を求める（Elson et al., 2023）**: "Reject studies that use novel/ad-hoc measures without providing validity evidence from independent data."
- **G5 内容的妥当性は、専門家と対象者の両方を関与させて確かめる性質である（Lintner, 2024）**: "Content validity refers to the degree to which the instrument measures the construct(s) it purports to measure" / "COSMIN requires that both experts and target population are involved in content validation for content validity to be considered adequate."
- **G6 評価者が 1 人であることの偏りを限界として述べる（Lintner, 2024）**: "It was performed by a single author, which might have caused some bias in the scales' quality assessment"

## 2. 評価表

観点 b と d は依頼文に定義がなかったため、b を「方法の妥当性」、d を「透明性・再現性」と仮に置いた。5 点満点。

| 観点 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | 主張・GSRR 番号・出力・表を 1 対 1 で結ぶ対応表はよくできている。ただし 3 点で、外枠の文が登録版を越える。(1) 序論が「項目内容が得点の中身を変える」と言い切っている（登録版は「Item content does not show what scores contain」）。(2) 新規性の主張が、登録版の探索範囲の非対称を落としている。(3) C7 の名前「beyond what was measured」が、条件 (iii) の中身（名前どうしの照合）より強い。 |
| b 方法の妥当性（仮定） | 3 | 登録版が優先するので軽く見た。C2b・C6a・C7 は研究者の分類であり、それ自体の妥当性の証拠は「同じ見方を共有する 2 人の一致」だけである。外枠はこの限定を運んでいない。 |
| c 持ち帰れるもの | 3 | 公開するコード表と 1 尺度ごとの要約表は再利用でき、価値が高い。一方、推奨（5.3）は自前のコード定義にしか結ばれていない。既存の報告基準（SOBER の項目・COSMIN の性質）との対応が無く、読者が自分の分野へ持ち帰る形になっていない。 |
| d 透明性・再現性（仮定） | 4 | 値をスクリプトから転記し、手で打たない・丸めない規則、表の入れ物、除いた値を全表に示す規則がある。Table 12 の入れ物は、自らの規則と小さく食い違っている（nit）。 |
| e 規程への適合 | 評価外 | 投稿先が未定のため。 |
| f 先行研究の位置づけ | 2 | 測定論の中心にある文献（jingle-jangle・測定の柔軟性・COSMIN の内容的妥当性）が背景の計画に無い。「COSMIN に基づくレビュー」（複数形）の根拠は結果の無い事前登録 1 本（Jonaid, 2026）だけである。抄録の「existing reviews point to unvalidated scales」には出典が無い。 |

## 3. 指摘（重い順）

### [severity: major] 序論が「項目内容が得点の中身を変える」と言い切り、登録版と自らのスコープ節に反する
- **位置と引用**: outline.md 101–103 行「items that ask about avoidance, irritation or disengagement change what a "fatigue" score contains」。照合先は以下のとおり。
  - 登録版 GSRR-65（400 行）「Item content does not show what scores contain.」
  - コードブック「Limitation」節「Item wording does not show what scores contain. ... Testing that requires correlational or factor-analytic data.」
  - outline.md 44 行「The item-content types (C2b) are described and are not called problems」
- **なぜ問題か**: 得点が何を含むかは、項目の字面からは分からない。構造的妥当性（因子分析・IRT）の問いである。この文は登録版が自ら否定した推論を、序論の動機として置いている。さらに「avoidance, irritation or disengagement」を「fatigue」の外にあるものとして扱っている。しかし適格基準（GSRR-24）は motivational / behavioural depletion を疲労に含め、C2b の型を問題と呼ばないと決めている。序論が型を問題として描けば、結果節の中立な記述が読者には問題の報告として読まれる。
  - 接地: G5 Lintner「Structural validity refers to the degree to which the instrument scores are an adequate reflection of the dimensionality of the construct」
- **解消の条件**: 序論の文を「項目の文言は、疲労と呼ばれる尺度が何を尋ねているかを示す。得点が何を含むかは示さない」という水準へ下げる。避ける・苛立ち・関心の低下を「疲労でないもの」として書かない。疲労の定義の幅（GSRR-24）を序論の同じ段落で示す。
- **自信**: 高

### [severity: major] C7「beyond what was measured」の名前が、条件 (i)(iii) の中身より強い（このレビュー自身が名目の誤謬を負う）
- **位置と引用**: outline.md 205 行 S2「Conclusions within or beyond what was measured, by condition.」、46–47 行「C7 says how far a conclusion is supported by what was measured」。登録版 C7 の条件は 3 つある。
  - (i)「C6b is a mismatch」
  - (ii)「AI-fatigue term ... while the main instrument's C1 representative value is L3, L4, L5 or L6」
  - (iii)「The construct term in the conclusion is in a different term family from the name of the main instrument」
- **なぜ問題か**: 3 条件のうち「測ったもの」に触れるのは (ii) だけである（AI への言及が項目・教示にあるか）。(i) は因果の語と研究デザインの照合であって、測定ではない。(iii) は結論の語と**尺度の名前**の照合である。Elson の言う名目の誤謬そのものを判定基準に組み込んでいる。尺度名の語族が結論の語と違っても、測った中身が結論と違うとは限らない。逆に語族が同じでも、中身が違うことはある。(iii) を満たすことを「測ったものを越えた」と呼べば、レビュー自身が名前から中身を推している。C6a「different family」を問題型としていることにも同じ構造がある。
  - 接地: G1 Elson「a nominal fallacy: that a measure's name tells you about its contents or what it measures」
- **解消の条件**: 登録したコード名は変えなくてよい。原稿では次のどちらかをする。
  - 条件ごとに何を照合したかを言い換えて報告する（(i) 因果の語とデザイン、(ii) AI 疲労の語と帰属の水準、(iii) 結論の語と尺度名）。Table 11 と抄録で条件別の数を必ず並べる。
  - 「(iii) と C6a は名前の一致を見ており、構成概念の一致を見ていない」と方法節とスコープ節に明記する。

  いずれの場合も、Discussion 5.1 で「beyond what was measured」を単一の量として語らない。
- **自信**: 高

### [severity: major] C2b を COSMIN の内容的妥当性と区別する断り書きが、外枠に運ばれていない
- **位置と引用**: outline.md 70–71 行 Contribution 3「Item-level content of the fatigue instruments first seen in the confirmation set」、104–105 行「the COSMIN-based reviews of AI-related instruments evaluate measurement properties (Jonaid, 2026)」。照合先は登録版 GSRR-10「The item-content coding in this review (C2b) is a researcher classification of item wording. It is not a COSMIN content-validity assessment, which requires experts and the target population.」
- **なぜ問題か**: 測定論の読者は「item-level content」を内容的妥当性の証拠と読む。登録版にある断り書きが外枠のスコープ節・寄与・序論のどこにも無いので、原稿でも落ちる恐れがある。同じことが C2d にも言える。C2d は報告の有無（項目の開示・この標本での信頼性・因子分析・選んだ理由）しか見ておらず、COSMIN の性質のごく一部である。さらに C2b は項目が印刷された尺度に限られ、登録版は「the instruments with printed items may differ systematically from the others」と認めている。Contribution 3 にこの限定が無い。
  - 接地: G5 Lintner「COSMIN requires that both experts and target population are involved in content validation」
- **解消の条件**: Scope of the claims 節に 1 項を足す。中身は「C2b is a researcher classification of item wording, not a content-validity assessment; C2d records disclosure, not measurement properties」。Contribution 3 には「印刷された項目に限る」「items unavailable の数を併記」を入れる。
- **自信**: 高

### [severity: major] 新規性の主張（「No review was found」）が、登録版の探索範囲の非対称を落としている
- **位置と引用**: outline.md 106–107 行「No review was found that tabulates, study by study, how fatigue is tied to AI, what the fatigue items ask about, and whether reports are internally consistent (the search is described in GSRR-10).」。照合先は登録版 GSRR-10「The last point was checked in 16 searches of free sources ... The first two were checked only in the reviews we had already read.」
- **なぜ問題か**: 3 点のうち 2 点（帰属と項目内容）は、既に読んだレビューの中で確かめただけである。外枠の文は 3 点が同じ強さで探索されたように読める。これは寄与の中心にある主張なので、根拠の範囲を越えている。
- **解消の条件**: 序論の文を、点ごとの探索範囲が分かる形に書き換える。例:「For internal consistency, 16 searches ...; for attribution and item content, only the reviews we had read」。
- **自信**: 高

### [severity: major] 背景に測定論の中心の文献が無い。COSMIN 側の根拠は結果の無い事前登録 1 本だけ
- **位置と引用**: outline.md 111–120 行（2. Background の 4 項目。測定論は Mbuagbaw・Murad & Wang・Long・Nuijten のみ）、104–105 行「the COSMIN-based reviews ... (Jonaid, 2026)」、91–92 行（抄録の Background）「existing reviews point to unvalidated scales and unclear construct boundaries」（参考文献一覧に該当する出典が無い）
- **なぜ問題か**: このレビューの問いの多くは、測定論で名前の付いた問題である。
  - C6a・C7 (iii) は jingle-jangle にあたる。
  - C2a の modification は undisclosed flexibility にあたる。
  - C2d は SOBER の Comprehensive Reporting にあたる。

  背景がこの系譜に触れないと、新しさ（AI 疲労の領域への適用、事前の規則化）と既知のもの（問題の型そのもの）の境が読者に見えない。Elson は、方法論のレビューこそが測定の柔軟性を明らかにすると書いており、本レビューの存在理由を直接支える文献でもある。「COSMIN-based reviews」（複数形）を事前登録 1 本で支えるのも弱い。AI 関連の尺度を COSMIN で評価した、結果のある系統的レビューは存在する（例: 本査読の接地に使った Lintner 2024 の AI literacy scales）。
  - 接地: G2 Elson「only a methodological literature review will reveal ...」、G3（SOBER の表）
- **解消の条件**: Background に「測定の柔軟性と jingle-jangle」の項を立てる。寄与の言い方を「既知の問題型を、AI 疲労の研究に事前に固定した規則で当てた」と位置づける。COSMIN 側には結果のあるレビューを最低 1 本引く。抄録の「existing reviews」には出典を付ける。
- **自信**: 中（どの文献を引くかは著者の判断）

### [severity: minor] 推奨（5.3）が自前のコード定義にしか結ばれておらず、持ち帰りにくい
- **位置と引用**: outline.md 169–172 行「Each recommendation is tied to one code and to the registered definition of that code (for example, printing the items administered; stating the level of attribution; reporting adaptation procedures)」、210 行 D1
- **なぜ問題か**: 例に挙がった推奨のうち 2 つ（項目を印刷する・改変の手続きを報告する）は、既存の基準（SOBER の Comprehensive Reporting / Justify Modifications）と重なる。対応を示さないと、読者には新しい規範に見えて採用されにくく、既存基準の何を AI 疲労へ具体化したのかも見えない。
  - 接地: G3 Elson「Report all of the items ...」「Justify Modifications ...」
- **解消の条件**: 推奨ごとに「対応するコード」と「対応する既存の報告基準（あれば）」の 2 列を持つ表（Table 14 など）を、外枠の時点で入れ物として置く。
- **自信**: 中

### [severity: minor] コード体系そのものが「新しく作った測定」であり、寄与 1 の言い方に妥当性の限定が無い
- **位置と引用**: outline.md 65–67 行 Contribution 1「A registered coding scheme for measurement and reporting ...」、197 行 AG1「Agreement between coders per code and set」、93 行（抄録）「two independent coders」
- **なぜ問題か**: C1〜C7 は本レビューが作った分類の道具である。その証拠は、規則を作った 2 人（同じ物語的レビューの著者）の一致だけである。登録版 GSRR-46 は「agreement between two coders who share that view, not as agreement between independent perspectives」と限定し、coder 2 が欠けた場合は単独コーダーになるとも定めている。外枠の AG1・Table 4・抄録はこの限定を運んでいない。抄録の「two independent coders」は、結果より前に固定される文として強すぎる。
  - 接地: G4 Elson「novel/ad-hoc measures without providing validity evidence from independent data」（類推として）、G6 Lintner「performed by a single author, which might have caused some bias」
- **解消の条件**: AG1 と Table 4 の見出しに GSRR-46 の限定を入れる。抄録の規則に「coder 2 が欠けた場合は single-coder と書く」の分岐を入れる。Contribution 1 には「一致は規則を作った者どうしのもの」を添える。
- **自信**: 中

### [severity: nit] Table 12 の入れ物に、除外した値の列が無い
- **位置と引用**: outline.md 216–217 行「Values excluded from denominators ("not verifiable", "not applicable", "unresolved") are shown in every table.」に対し、254 行の列は「Count | Evaluable records | Unresolved」だけで、「not verifiable」「not applicable」の列が無い。
- **なぜ問題か**: 自らの規則と食い違っている。問題の記述では分母が読みの要になる。
- **解消の条件**: Table 12 に 2 列を足すか、Evaluable の注で内訳を示す。
- **自信**: 高

## 4. 総合の推奨: major（直して再査読）

- 外枠の骨格（主張・GSRR・出力・表の対応、頻度語の禁止、確認集合だけで主張する規則）は、結果を知る前に主張の範囲を縛る道具として優れている。
- ただし、序論の動機の文と C7・C2b の扱いが、登録版自身の測定上の限定（項目の文言は得点の中身を示さない／名前の照合は中身の照合ではない／C2b は内容的妥当性ではない）を原稿へ運んでおらず、読者に構成概念の主張として読まれる。
- 先行研究の位置づけが測定論の系譜を欠いており、寄与の新しさの境が見えない。上の major の 5 件は、どれも外枠の文の追加と書き換えで消える。

## 5. 読めなかった範囲と注入の疑い

- 読んだもの: 依頼文、context-A.md、outline.md、README.md、registration-en.md、codebook-c2b-en.md（いずれも全文）、接地の elson2023.txt と lintner2024.txt（全文）。
- 読んでいないもの: tmp/sources/ にある perrig2024.txt・bach2022.txt・nuijten2016.txt・gsrr.txt・mbuagbaw2020.txt（この立場の接地に指定されていないため）。Murad & Wang 2017・PRISMA 2020 の本文（渡されていない）。outline が引く Jonaid 2026・Perrig 2024 の本文。したがって、外枠がこれらを正しく要約しているかは確かめていない。
- 注入の疑い: なし（読んだ範囲に、査読者や LLM へ向けた指示は見当たらなかった）。
