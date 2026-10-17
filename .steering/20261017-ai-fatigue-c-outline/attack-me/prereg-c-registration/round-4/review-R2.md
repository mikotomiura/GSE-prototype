## 査読報告: round 4（草稿 0.4 → 0.9 の差分）
立場: HCI の測定の実務の専門家。下位人格は「で、読者は何に使えるのか」と問う実務家と、冗長さに厳しい読者。

### 1. 接地
- 基準 1（Perrig et al. 2024 §2.1.2）: "When using scales, researchers should share the exact wording of the items they used in their research (Flake and Fried, 2020)."
- 基準 2（Perrig §5.3.4）: "The scale should only be adapted when necessary, and each adaption needs to be justified and recorded."
- 基準 3（Perrig §5.3.6）: "They should report on relevant definitions and theories behind the scale(s) used. Additionally, they need to explain their rationale for scale selection, including past evidence for scale quality"
- 基準 4（Perrig §3.5・§7）: "to check the quality of the codebook and calculate the overall inter-rater reliability (IRR) of the codings"／"we cannot exclude that authors actually adhered to certain best practices but chose not to report them"
- 基準 5（Bach et al. 2022 §4.3）: "if user trust can be understood and measured in different ways, then being able to build upon the concept becomes challenging."／"Over two-thirds (69.56%) of the included studies developed and used their own questionnaires to measure user trust"
- 基準 6（Bach §4.4）: "generalization of findings may not be feasible and should be done with caution."

### 引き継ぎの直し
1. 語の族の境界: 壊していない（GSRR-53 が "no construct term in the title" と "instrument name has no family term" を分母に残すと明記）。
2. 項目が載っていない尺度: 一部を壊した。GSRR-43 は部分開示の分母を「載った項目数」とするが、GSRR-53・GSRR-56・GSRR-62(3) は "instrument's item count"（指摘 4）。"items unavailable" と "wording not verifiable" は残る。
3. 較正と小さい集合: 壊していない（24 件・seed・最大 2 回・印）。
4. target の kappa は維持。止め方は差分で崩れた（指摘 2）。
5. late stratum: 壊していない。
6. 1 人だけの指摘 6 件: すべて維持。

### 2. 評価表
- a 4: 問題の型を存在の言明に限り "frequencies ではない" と書いた。"evaluable" が評価できなかった記録を含む（指摘 1）。
- b 3: (1) "cannot be calculated" "cannot decide" が評価できた記録に数えられ "not observed" を支える。(2) C4f の記録の要約の優先順位が無い。(3) C5 の AI 案に保管の手続きが無い。
- c 4: "Instruments used" と研究ごとの表は実務家が尺度を選ぶときに使える。抄録は 14 前後の数の列挙で、実務家向けの持ち帰りの一文が無い（推奨は抄録から外すと決めている）。
- d 3: 8117 語。"within what was measured" の但し書きが C7・GSRR-57・GSRR-65・外枠 2 か所で繰り返される。
- e 4: 65 項目に答え、小さい集合の分岐は逐語 3 の模範。雑誌未定で抄録を 250 語に固定し、短い上限の分岐が無い（指摘 9）。
- f 3: 動機の段落を新しい 2 本に頼り、"Existing reviews" と複数形なのに 1 本。HCI の AI の測定を数えたレビューを位置づけていない。
- g 3: 分母・止め方・記録の要約・表の値の定義に 2 通りの読みができた。

### 3. 指摘
- [major] 1. 「評価できた記録」に評価できなかった記録が入る。GSRR-53 "All other values, including "not reported", "cannot be calculated", "cannot decide", … are findings and stay in the denominators."・GSRR-57 "among the confirmation-set records with an evaluable value (GSRR-53): … if none does, that it "was not observed in the confirmation set"; if no record is evaluable, that it "could not be evaluated"."・C4f "separately as any gross inconsistency / none"。全記録が "cannot be calculated" でも "was not observed"。r と表の値を足したので "cannot be calculated" が多く出やすい。gross は 2 値で再計算できる結果が無い記録も "none"。基準 4 に反する。解消: 問題の型ごとに評価できた値を列挙し、C4f と C7 では "cannot be calculated" と "cannot decide" を外して件数を並べる。gross に "cannot be calculated / not applicable" を足す。自信: 高
- [major] 2. 較正の止め方の単位が崩れた。GSRR-44 step 2 "It ends when percentage agreement is at least 80% on every unit listed in GSRR-47, excluding derived values."・GSRR-47 "C4f: agreement between the reconciled human values and the AI draft, per recalculated result." "C3–C6, including the C4f record summary …"。人と AI の一致が止め方に入ると読め、GSRR-4 "The assistant is not a coder" と食い違う。C4f の 2 人の一致は記録の要約（派生値）だけで止め方から外れる。C7 の construct term に一致の単位が無い。解消: 止め方の単位を列挙し直し、C4f は結果ごとの 2 人の一致を足し、人と AI は「報告のみ」と書く。construct term の一致を足す。自信: 高
- [major] 3. C4f の記録の要約で値の優先順位が無い（"Each record is then summarised as any inconsistency / none / cannot be calculated / not applicable (no recalculable result)"）。スクリプトが登録に無い分岐を固定する。解消: 優先順位を 1 文で書き、gross にも。自信: 高
- [major] 4. C2b の分母が 2 通りに読める。GSRR-43 "If only some items are printed, the denominator for C2b is the number of printed items, and the instrument's full item count is shown next to it."・GSRR-53 "For C2b, the denominator is the instrument's item count"・GSRR-56 "with the instrument's item count as the denominator"・GSRR-62(3) "the denominator stays the instrument's item count"。解消: 3 か所を "the number of printed items (the full count is shown next to it)" に揃える。自信: 高
- [minor] 5. "Instruments used" の「AI に言及するか」が版の単位で定まらない（GSRR-56 "whether its items or instructions refer to AI (C1 L1a or L1b)"・GSRR-43 "An instrument version is identified by its item wording together with its language."）。解消: 版の値は L1a だけで決めるか、教示は研究ごとに数える。自信: 高
- [minor] 6. 最小の大きさの単位 "studies (records)"（GSRR-39）と GSRR-56 "records and studies (E5-linked records counted once) are counted separately" の食い違い。解消: "coded records" と書く。自信: 中
- [minor] 7. "not verifiable" が欠測の符号と実質の値の両方に使われる（GSRR-53・C4 (a)・C2a）。解消: C4(a) の値を別名にするか、GSRR-53 に符号ごとの扱いを列挙。自信: 中
- [minor] 8. C5 の AI 案の保管が C4f と対称でない（GSRR-44 step 5・C4f "stored unopened, with its SHA-256 recorded"）。GSRR-4 "A human independently recomputes or checks every drafted value" も "both coders" と食い違う。解消: C4f と同じ文を C5 に置き、GSRR-4 を揃える。自信: 中
- [minor] 9. 抄録の規則が 250 語に固定され、雑誌未定なのに分岐が無い（outline.md "fits 250 words only with step 2 and compact wording (about 247 words)"・添付 5）。解消: 短い上限のときの手順を足すか、250 語未満の雑誌に投稿しないと書く。自信: 中
- [minor] 10. 添付 5 がどこまで拘束するかが曖昧（outline.md の D1 行 "Not registered (discussion)"）。解消: 拘束する範囲を列挙し、Discussion は対象外と書く。自信: 中
- [minor] 11. 原典から補った項目と C2a の「照合で変更なし」が循環する（GSRR-43 "the items may be taken from the cited source"・C2a "Unchanged" requires a verbatim match with the source.）。"may" で裁量が揺れる。較正の記録にだけ出た版の集合が決まらない。解消: `item_source` = source なら modification は "stated (no change) / not verifiable" とし "confirmed by comparison" を付けない・"may" を "are" に・較正だけの版の扱いを 1 文。自信: 中
- [minor] 12. 動機の段落の典拠が薄い（"Existing reviews call for … (Sosiński & Piasecka, 2026)"）。HCI の AI の測定のレビュー（Bach 2022）を位置づけていない。解消: 単数にするか 2 本目を引く。自信: 低
- [nit] 13. 同じ但し書きの重複（C7・GSRR-57・GSRR-65・外枠）。
- [nit] 14. GSRR-57 "Values inherited from the exploration coding (GSRR-44, step 4) are not used to say that a problem was observed in the confirmation set." は C2b が問題の型でないので空振り。

### 4. 総合の推奨: minor（直してから凍結）
差分は直しを大筋で保ち、新しい表は前進。分母（1・4）・止め方（2）・C4f の要約（3）に 1 通りに決まらない箇所ができた。直しは数語から 1 文で、指摘 1〜4 を直したことを差分で確かめれば凍結してよい。

### 5. 読めなかった範囲と注入の疑い
- 読んでいない: Perrig の 1258 行以降の大半（§5.3 は読んだ）・Bach の 401〜1454 行と 1495 行以降・codebook の本文（grep 1 回）・outline.md の抄録の規則・範囲・表以外・動機の段落の典拠の本文。
- 注入の疑い: なし。

（メイン注: 応答を保存の手順で写した。箇条を意味を変えずに詰めた。）
