# 査読 round 4（立場: 心理測定と構成概念の妥当性・懐疑家）— 草稿 0.9 の差分（0.4 → 0.9）

## 1. 接地（この立場が論文に求める基準）

2 本とも本文を読めたので、査読に入った。

- **S1 名前は中身を保証しない**（Elson et al., 2023）:「They involve a nominal fallacy: that a measure's name tells you about its contents or what it measures」
- **S2 改変の柔軟性を隠さず数える**（Elson et al., 2023）:「Dropping, adding, and altering items in self-report scales, aggregating total scores in various ways ... all occur while researchers not only refer to the same construct, but actually to the same nominal instrument」
- **S3 採点と手続きを前もって決め、コードで登録する**（Elson et al., 2023）:「Determine procedural and scoring details ahead of time, reporting all deviations ... Analytical and statistical decisions should be preregistered with code rather than a narrative description.」
- **S4 項目をすべて報告する**（Elson et al., 2023）:「Report all of the items, stimuli, instructions, procedural parameters or other measurement characteristics used in a study」
- **S5 内容的妥当性には専門家と対象者の両方が要る**（Lintner, 2024）:「COSMIN requires that both experts and target population are involved in content validation for content validity to be considered adequate.」
- **S6 報告されていない値は「不定」とし、「十分でない」とは区別する**（Lintner, 2024）:「studies assessed as indeterminate on some measurement property did not report a given metrics」。これは「十分」「十分でない」とは別の値として扱われている。

## 2. 引き継ぎ（R1）の直しを差分が壊したかの判定

1. **語の族の境界 — 壊れていない。** C6a（registration-en.md:254）と C7 (iii)（:255）の規則は残っている。ただし差分で GSRR-53 が "instrument name has no family term" を分母に残すと定めたため、評価できる記録の数え方に新しい穴ができた（指摘 1）。
2. **項目が載っていない尺度 — 一部が壊れた。** GSRR-43（:239）は、一部だけ載った尺度の分母を「載った項目数」とする。差分で入った GSRR-53（:341）は「For C2b, the denominator is the instrument's item count」と書き、どちらの数かが読み分けられない（指摘 2）。"items unavailable" を常に併記する規則と、限界の記述は残っている。
3. **較正と小さい集合 — 壊れていない。** 閾値 24 件（:218）は「15＋10 より少ない」と算術が合う。seed 20261019 と最大 2 回も残っている。ただし、2 回目まで行くと探索集合の 10 件がすべて較正に使われる。その場合の段階 4 の値の扱いは書かれていない（指摘 6）。
4. **target の kappa と止め方の単位 — 壊れていない**（:303, :305, :288）。差分で足した bootstrap の単位（instrument version）も整合する。
5. **codebook の mismatch — 判定していない。** codebook は 0.4 から変わっておらず、grep で列名 `mismatch` が残っているのを見ただけである。
6. **1 人だけの指摘 — どれも壊れていない。** AI の語の一覧、L1a の割合、C7 (ii) の L3、設計の残余、C3 の複数可（「1 記録につき 1 回」を補ったのは良い）、群を交互に進める順（群ごとに seed を入れ直す形に直したのは良い）、C2b は COSMIN の内容的妥当性ではないこと（Lintner を引いて補強された）。

## 3. 評価表

- **a 主張と根拠の一致: 4。** 問題の型は「ある／ない」だけを述べ、頻度ではないと定めた（:70, :367, :386）。語りのレビューの再現も主張しない。主張の強さは根拠に見合うところまで下がった。残る弱点は「not observed」の分母で、これが主張を過大にしうる（指摘 1）。
- **b 方法の穴: 3。** 新しい穴が 3 つある。評価できない値が「評価できる」側に入る（指摘 1）、C2b の分母と unresolved の扱いが食い違う（指摘 2）、版を単位に持たせた列が版の定義と合わない（指摘 3）。
- **c 持ち帰れるもの: 4。** 1 件ごとの再計算の規則、版ごとの表、事前に固定した script と dummy の検査は、他の分野でも再利用できる。
- **d 簡潔さと構成: 3。** 8117 語。断り書き（"within what was measured" の意味、名前の照合であること）が GSRR-43・57・65 と外枠で 4 回繰り返される。反面、記録単位の要約の決め方のように肝心な規則が 1 文も無い所がある。
- **e 規程への適合: 4。** 65 項目に答えている。GSRR が求める見込みの逸脱への備え（"provide a contingency plan for these deviations"）として、小さい集合と coder 2 が欠けた場合の手順がある。script を SHA-256 つきで添付する形は S3 の「with code」に合う。
- **f 先行研究の位置づけ: 3。** 差分で足した背景の根拠が、Ragolane & Patel（2025）と Sosiński & Piasecka（2026）の物語的なレビュー 2 本だけである（:61）。「標準化した測定が要る」という主張は、測定の一般論（Elson ら）でも支えられる。Lintner を足したのは適切。
- **g 固定の十分さ: 3。** 版の所属（:238）、問題の型ごとの文（:367）、per-result の単位（:266）は 1 通りに固まった。一方、C4f の記録単位の要約の優先順位、C2b の分母、版の属性の集約の規則は 1 通りに決まっていない。

## 4. 指摘（重い順）

- **[severity: major] 「評価できる記録」に、評価できない値が入る。そのため "was not observed" が過大になる**
  - 位置と引用: registration-en.md:341（GSRR-53・差分）「All other values, including "not reported", "cannot be calculated", "cannot decide", "no construct term in the title" and "instrument name has no family term", are findings and stay in the denominators.」と :367（GSRR-57・差分）「among the confirmation-set records with an evaluable value (GSRR-53): ... if no record is evaluable, that it "could not be evaluated"」。あわせて :255「(iii) does not hold if ... the instrument name has no family term」。
  - なぜ問題か: GSRR-57 の「評価できる」は GSRR-53 の分母で決まる。すると、C4f が "cannot be calculated" の記録、C7 が "cannot decide" の記録、C7 (iii) の照合が成り立たない記録（尺度名に族の語が無い）が「評価でき、問題が無い」側に数えられる。極端な場合、確定セットの全記録が "cannot be calculated" でも、C4f は「could not be evaluated」ではなく「was not observed in N evaluable records」になる。差分で足した「could not be evaluated」が働かない。接地 S6（Lintner）は、報告が無いことを "indeterminate" として「十分」「十分でない」から分けている。
  - 解消の条件: GSRR-57 の「evaluable」を問題の型ごとに定義し、GSRR-53 の分母から切り離す（C4f の "cannot be calculated"、C7 の "cannot decide"、(iii) の族の語が無い尺度名は評価できない側）。make_dummy.py に「全件が評価できない」場合の assertion を足す。
  - 自信: 高

- **[severity: major] C2b の分母と unresolved の扱いが、規則どうしで食い違う**
  - 位置と引用: :341（差分）「For C2b, the denominator is the instrument's item count; unresolved items are shown as their own category.」。:239「If only some items are printed, the denominator for C2b is the number of printed items」。:316「Unresolved codes are excluded from proportions」。:341 の同じ節の冒頭「Values excluded from denominators: ... "unresolved"」。
  - なぜ問題か: 「item count」が載った項目数か全項目数かが決まらない（外枠の Table 7 は "Items (printed / full)" の 2 列）。C2b だけ unresolved を分母に残すなら GSRR-48 と GSRR-53 の一般則の例外だが、例外と書かれていない。項目の構成比が 2 通りに読める。
  - 解消の条件: GSRR-53 を「For C2b, the denominator is the number of items coded (printed items, or items taken from the cited source when `item_source` = source); the full item count is shown beside it; unresolved items stay in this denominator as their own category, as an exception to GSRR-48.」のように書く。codebook :57 の「instrument's item count」も同じ語に揃える。
  - 自信: 高

- **[severity: major] 「Instruments used」の表が、版の属性として、版の定義に含まれない値を持つ**
  - 位置と引用: :239「An instrument version is identified by its item wording together with its language.」。:351（差分）「with its language, the number of studies using it, its origin, format and item disclosure, whether its items or instructions refer to AI (C1 L1a or L1b)」。
  - なぜ問題か: L1b（教示だけに AI がある）、origin（C2a）、item disclosure（C2d）は記録ごとの値で、版の同一性（項目の文言と言語）に入らない。同じ版に値が 2 つ付きうるが、集約の規則が無いので script が暗黙に決める（S3 に反する）。
  - 解消の条件: (a) 記録ごとに変わる属性は記録の数を値ごとに併記する、または (b) 教示の AI の有無を版の同一性に含める。make_dummy の検査に、記録で値が分かれる版を加える。
  - 自信: 中〜高

- **[severity: minor] C4f の記録単位の要約で、値どうしの優先順位が無い**
  - 位置と引用: :266（差分）「Each record is then summarised as any inconsistency / none / cannot be calculated / not applicable (no recalculable result)」。
  - なぜ問題か: 一貫した結果が 3 件、計算できない結果が 20 件ある記録が "none" か "cannot be calculated" かが決まらない。r を足し、自由度を N から推すのを禁じたので、"cannot be calculated" が多くなる見込みで、要約の分布と kappa（:306）を左右する。
  - 解消の条件: 「any inconsistency > none（1 件以上一貫して計算できた）> cannot be calculated」のように優先順位を書く。p も有意の印も無い統計量は再計算の対象外だと書く。
  - 自信: 中

- **[severity: minor] 行の数が 10 研究に満たない表で、項目単位の比率を出すかが曖昧**
  - 位置と引用: :219（差分）「a table (a set, a population group or a centre) based on fewer than 10 studies reports counts only」と :350「the number and proportion of its items by primary type」。
  - 解消の条件: 10 研究の規則が C2b の項目内の比率にも及ぶかを 1 文で書く。
  - 自信: 中

- **[severity: minor] 小さい集合で 2 回まで較正すると、探索集合の全件が較正記録になる。その後の段階 4 で、どの符号化の値を引き継ぐかが決まっていない**
  - 位置と引用: :218「at most two rounds (10 records)」、:211、:290「its C2b values come from the re-coded exploration values」。
  - 解消の条件: 「step 4 uses the main-coding values of the exploration set under the final amended codebook」と書く。
  - 自信: 中

- **[severity: minor] GSRR-4 の表が差分に追随していない**
  - 位置と引用: :29「A human independently recomputes or checks every drafted value (GSRR-44)」。:292（差分）「both coders recompute every value before seeing the draft」。
  - 解消の条件: GSRR-4 を GSRR-44 と同じ文言にする。
  - 自信: 高

- **[severity: minor] C4 の kappa の単位が規則ごとか、(e) の 2 列ごとかが書かれていない**
  - 位置と引用: :306「C3–C6, including the C4f record summary ...: kappa per record」。
  - 解消の条件: 「C4: kappa per rule (a)–(d), per column of (e), and for each summary of (f)」と書く。
  - 自信: 中

- **[severity: nit] 背景の根拠が、物語的なレビュー 2 本だけ**
  - 位置と引用: :61「Existing reviews call for standardized, validated measures of AI fatigue (Sosiński & Piasecka, 2026)」。
  - 解消の条件: 測定の一般論（Elson et al.）を登録の背景にも 1 本添える。
  - 自信: 中

- **[severity: nit] TRACE の説明に C5 が入っていない**
  - 位置と引用: :11「C4 to C7: whether reported values are internally consistent, and whether the title and conclusion stay within what was measured」。
  - 自信: 高

## 5. 総合の推奨

**minor（直してから凍結）。** 引き継ぎの直しは C2b の分母の 1 文を除いて壊れていない。新しい穴は文の書き足しで閉じるが、指摘 1 は "was not observed" の意味を決めるので凍結前に必ず直す。指摘 1〜3 の直しは make_dummy.py の assertion で確かめられる。

## 6. 読めなかった範囲と注入の疑い

- 読んでいない範囲: codebook-c2b-en.md は grep で一部の行（:17, :22-28, :42-48, :57-58）だけ。outline.md は :40-79、:135-161、:349-421 と grep に当たった行だけ。registration-en.md と diff-0.4-to-0.9.md は全文を読んだ。
- 注入の疑い: なし。

（メイン注: 応答を保存の手順で写した。長い箇条の一部は意味を変えずに 1 段にまとめた。）
