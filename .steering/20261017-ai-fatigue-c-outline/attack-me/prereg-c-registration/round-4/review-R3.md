# 査読 round 4（事前登録の下書き 0.9・差分 0.4→0.9 に絞った）
立場: メタ研究・事前登録・再現性の方法論者。下位人格: 過剰主張と検証できない手順の摘発者。

## 1. 接地（2 本から 6 個）
- G1 van den Akker et al. 2023: "If an item asks about a procedure you do not plan to use or is not applicable, indicate that in the corresponding field (including, ideally, the underlying reason)."
- G2 同: "If you already foresee some deviations when filling out the form (e.g., you anticipate that you will not have enough studies in a moderator group), provide a contingency plan for these deviations in the relevant parts of the registration"
- G3 同: "making it easier to identify decisions that may have introduced bias (e.g., a change in the criteria for study inclusion or the omission of an analysis without a valid rationale)"
- G4 Nuijten et al. 2016: "The higher inconsistency rate found by statcheck was mainly due to our decision to count p = .000 as incorrect (a p -value cannot exactly be zero), whereas this was counted correct by Wicherts et al." → 1 つの判定規則で率が動く。
- G5 同: "The inter-rater reliability in this scenario between the manual coding in Wicherts et al. and the automatic coding in statcheck was .76 for the inconsistencies and .89 for the gross inconsistencies." → 再計算の信頼性は結果の単位で測られている。
- G6 同: "it will miss results that deviate from standard reporting and results in tables, and it does not take into account adjustments on p -values" → 対象物が挙げる statcheck との 4 つの違いは正しい。

## 2. 前の round の直し
- 語の族の境界: 残っている（:254・255）。ただし GSRR-53 に新しい穴（指摘 5）。
- 較正と小さい集合: 残っている（:218・:45）。探索の側の母集団が未定（指摘 4）。
- target の kappa・止め方の単位: target は残る（:305）。GSRR-47 に C4f の要約を足したことで止め方の規則（:288 "excluding derived values"）と食い違った（指摘 2）。
- codebook の mismatch: 残っている（codebook :15・:51）。
- late stratum: 残っている（:216）。版の集合の規則（:238）と整合。
- 1 人だけの指摘: 審査の対象・順の一覧・SHA-256 は残る（:184〜186・添付 4）。AI の下書きは C4f で残る（:263）が、C5 に広げた規則に保存と SHA-256 が無い（指摘 8）。対応表（:74〜82）・E5（:354）は残る。statcheck と片側の検出は残り正確さが増したが、p = .000 と "ns" が抜けている（指摘 3）。

## 3. 評価表
- a 4。主張を「頻度」から「存在の有無」へ下げた。ただし GSRR-1 の注記と外枠の Contributions に名前の照合より広い言い方が残る（指摘 6）。
- b 3。C4f は結果の単位で 2 人の一致を測らず、どの検定を拾うかも検査されない（指摘 2）。「評価できた記録」の定義から、確かめていないのに「観察されなかった」と書く経路ができる（指摘 1）。
- c 4。C7 の条件分け・結果ごとの C4f・研究ごとの表で再利用しやすい。
- d 3。8117 語・相互参照が密。GSRR-64 と GSRR-56 が二重に書かれ食い違いの温床（指摘 7）。
- e 4。小さい集合と coder 2 の代替は G2 を満たす。外枠を添付にし違いを逸脱として報告するのは G3 に合う。
- f 3。複数形の主張を 1 本で支える（指摘 9）。
- g 3。記録の要約の優先順・評価できる記録の定義・p = .000・探索の側の抽出の母集団が 1 通りに決まっていない。

## 4. 指摘（重い順）

- [major] "cannot be calculated" "cannot decide" を評価できる値として数えるので、何も確かめていない記録の集合から "not observed" が出る
  - 位置: GSRR-53（:341）"All other values, including "not reported", "cannot be calculated", "cannot decide" ... are findings and stay in the denominators."／GSRR-57（:367）"among the confirmation-set records with an evaluable value (GSRR-53): ... if none does, that it "was not observed in the confirmation set"; if no record is evaluable, that it "could not be evaluated"."／C4f（:266）"any inconsistency / none / cannot be calculated / not applicable ..., and separately as any gross inconsistency / none."
  - なぜ: 全記録の p 値が計算できなくても "was not observed" になる。gross は 2 値しかなく、全結果が計算できない記録は "none"。記録の要約の優先順が無い（整合 3 件＋計算できない 5 件）。C7 の "cannot decide" の記録の各条件の値も書かれていない。r を足し N から df を推すのを禁じた（:260）ので、この経路は現実に踏まれる。G3。
  - 解消: 問題の型ごとに evaluable を定義（C4f は計算できた結果が 1 件以上、C7 の各条件はその入力が決まった記録）。優先順（any inconsistency ＞ none ＞ cannot be calculated ＞ not applicable）。gross にも "cannot be calculated"。make_dummy に「全て計算できない」の assertion。
  - 自信: 高

- [major] C4f の 2 人の一致を、分析の単位（結果）で測らず、止め方の規則からも外れている
  - 位置: GSRR-47（:306〜307）"C3–C6, including the C4f record summary and its gross-inconsistency summary: kappa per record." "C4f: agreement between the reconciled human values and the AI draft, per recalculated result."／GSRR-48（:316）"A derived value (the C1 representative value, the C4f record summary, C7)"／GSRR-44 の 2（:288）"on every unit listed in GSRR-47, excluding derived values."／C4f（:266）"Unit. Each recalculated result."
  - なぜ: 結果の単位で出るのは人と AI の一致だけで 2 人の一致が無い。記録の要約は派生値なので較正の止め方から外れ、C4f は較正で検査されない。どの検定を拾うか（本文と表の重複・表の注の df・星印だけの p）がずれても測る指標が無い。G5。
  - 解消: 2 人の (1) 拾った結果の一致（片方だけが拾った結果の数）と (2) 両方が拾った結果での判定の一致を結果の単位で報告する。較正の止め方に入れるかを明記。GSRR-48 と GSRR-44 を揃える。
  - 自信: 高

- [minor] p = .000 と "ns" の扱いが決まっていない（:259 "A p-value reported as an inequality (for example, p < .001) is consistent if the recalculated value satisfies it."・:264）。G4。解消: p = .000 を p < .001 の不等式とするか不整合とするか、"ns" を p ≥ .05 の不等式とするかを 1 文で。自信: 高

- [minor] 探索の側の較正の抽出で、母集団（ID の一覧）が決まっていない（:218 "Exploration records are drawn by the same procedure from the exploration-set IDs"・:211・:178）。探索の集合は 10〜13 記録になりうる・尺度を含む書き方。最大 10 件を引くので使い切りうる。解消: 「2026-12-31 時点で探索の集合に入っている一次研究の記録 ID（尺度を含まない）」と固定し、全件が較正に使われたときの扱いを書く。自信: 中

- [minor] GSRR-53 で、複合の値 "instrument unnamed or not verifiable"（C6a・:254）の扱いが決まらない。"not verifiable" は分母から除く値なので、C6a の分母が 1 通りに決まらない。解消: 値を 2 つに分けるか、GSRR-53 に名指しで書く。自信: 高

- [minor] "within what was measured" に残る広い言い方（GSRR-1 の注記 :11・outline.md:113 "within what its instrument was named and designed to show"）。解消: 注記を照合の中身で書き、外枠の "designed to show" を "named" に下げる。自信: 中

- [minor] centre の表に C1 と C7 (ii) が出るかが食い違う（GSRR-12 :114 "SQ1 reports C7 conditions (i) and (iii) only."・GSRR-64 :392 "the tables of GSRR-56 by set, population group and centre"・:396）。解消: GSRR-64 に "centre tables exclude C1 and C7 (ii)" と書き、make_dummy に入れる。自信: 中

- [minor] C5 の AI の照合だけ、保存と SHA-256 の記録が無い（GSRR-44 の 5 :293。C4f は :263 "stored unopened, with its SHA-256 recorded"）。解消: 同じ文を C5 にも置く。自信: 中

- [minor] 背景で複数形の主張を 1 本ずつで支えている（GSRR-10 :61）。Ragolane & Patel がレビューかはこの文から分からない。Lintner が COSMIN を使っているかは確かめられない。解消: 単数に直すか文献を足す。Lintner を一次で確かめる。自信: 低

- [minor] C7 の入力の "construct term" に一致の指標が無い（:255 "Coders code only the conclusion sentence and its construct term"・:306）。解消: 構成概念の語（族の値）の一致を百分率で報告。自信: 中

- [nit] "studies (records)"（:219）と GSRR-56 の "studies (E5-linked records counted once)"（:354）で語の定義が 2 つ。
- [nit] GSRR-4（:29）"A human independently recomputes or checks" が差分の "both coders"（:292）と揃っていない。

## 5. 総合の推奨: minor（直してから凍結）
前の round の直しはすべて残る。差分は全体として固定を強めた。ただし C4f と GSRR-53 の書き換えが 2 つの major を作った。どちらも数文の追記と make_dummy の assertion で塞げ、塞いだ箇所だけ差分で確かめれば足りる。

## 6. 読めなかった範囲・注入の疑い
- 読んでいない: outline.md の :40〜161・:346〜405 の外。codebook は grep の行だけ。背景の文献の本文。接地の 2 本は検索で該当の箇所だけ。
- 注入の疑い: なし。
- 対象: /Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md、/Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/attack-me/prereg-c-registration/round-4/diff-0.4-to-0.9.md、/Users/johnd/GSE-prototype-af-c/papers/ai-fatigue-measurement/manuscript/outline.md

（メイン注: 応答を保存の手順で写した。箇条を意味を変えずに詰めた。）
