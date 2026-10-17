# 意図の監査役 round 2 の報告（stage: prereg）

対象物は `/Users/johnd/GSE-prototype-af-c/.steering/20261017-ai-fatigue-c-outline/registration-en.md`（草稿 0.2）と、添付の `codebook-c2b-en.md`（版 2）です。意図は context-B と、そこに挙がった `outline.md`・`decisions.md`・`overlap-narrative-review.md` から読みました。

結論を先に書きます。引き継ぎ 19 件のうち、15 件は解消しました。部分的に残るのが 3 件（2-3・3-B-1・3-B-3）、参照先の無い文が残るのが 1 件（3-B-4）です。新しい食い違いで重いのは、2-4 と 2-5 の 2 件です。

## 0. 引き継ぎの判定（1 件ずつ）

| 番号 | 判定 | 根拠（位置と逐語） |
|---|---|---|
| 1-1 | 解消 | GSRR-10「*Exploration done before registration (disclosed with dates).*」。2026-10-01・10-15・10-16・10-17 の 4 項目がある。ただし欠けが 1 つある（新しい 1-3） |
| 1-2 | 解消 | GSRR-34「Author 1 has screened the titles and abstracts of 71 additional candidates」、GSRR-65「Author 1 has seen the titles, abstracts and AI appraisals of 71 additional candidates.」。ただし 71 と他の数の関係が読めない（新しい 3-4） |
| 1-3 | 解消 | GSRR-10「These 10 studies and the four instruments form the exploration set」、GSRR-39 も同じ |
| 1-4 | 解消 | GSRR-6 段 5「The exploration set is re-coded under the same rules, also by two coders independently.」 |
| 1-5 | 解消 | コードブック 3 行目「Version 2 (2026-10-17). The English text is the authoritative version.」。Attachments 1 も同じ |
| 2-1 | 解消（事実として残した） | GSRR-10「both authors of this review are its authors」。ただし GSRR-46 と衝突する（新しい 2-4） |
| 2-2 | 解消 | GSRR-57「"was observed in the confirmation set", with its count and denominator」。ただし数える対象の中身に新しい問題がある（新しい 2-1・3-5） |
| 2-3 | 未解消のまま | context-B 持ち帰り 1「疲労を AI に結びつける段階・尺度の中身・報告の整合がばらばらで」は、まだデータの無い結果を主張として書いている。同じ文の「見ていない集合」は、対象物の言い方「records that neither coder has read in full before registration」（GSRR-10）より強い。GSRR-34 と GSRR-65 では、71 件の題名と抄録を見たと開示している。直すのは対象物でなくメインの文 |
| 2-4 | 解消 | GSRR-32「The review-aimed search produced a list of 46 records. 43 of them were unscreened on 2026-10-17.」 |
| 2-5 | 解消 | GSRR-4 の表「Drafts values for C4f and C5 only. ... The assistant is not a coder」 |
| 3-A-1 | 解消 | GSRR-11「RQ3 (reporting). How complete and how internally consistent is reporting?」 |
| 3-A-2〜5 | 解消 | C1 の L2・C7 の「it is the last sentence of the abstract」・C6b の日本語の語・GSRR-62 の 4 本。骨子との食い違いは、判断 8 の優先の規則で片づく。ただし、判断 8 が例に挙げていない差が 1 つある（新しい 3-6） |
| 3-B-1 | 部分的に解消 | 本文は C2b の行で「Target, assigned only when the type or secondary type is `MOT`, `AVO` or `FUT`」と明記した。しかし RQ2 の文と持ち帰り 3 は、苛立ち（IRR）にも対象が付くように読める（新しい 1-2） |
| 3-B-2 | 解消 | GSRR-44 の 4「its C2b values come from the re-coded exploration values, but only if the item wording is verbatim identical」 |
| 3-B-3 | 部分的に解消 | GSRR-50「The codebook quotes short phrases from items as anchors, with their sources.」と書いた。しかしコードブックの中身がこれに合っていない（新しい 3-3） |
| 3-B-4 | 解消。ただし参照先の無い文が残る | GSRR-48 は「Disagreements that remain are coded "unresolved".」に直った。一方 GSRR-19 の「the reconciliation rule in GSRR-48 applies with a single code」は、GSRR-48 に該当する規則が無いまま残っている（新しい 3-2） |
| 3-C-1 | 解消 | GSRR-6 段 3〜4、GSRR-39「Late stratum. Studies included after 2026-12-31 are reported as a separate stratum」 |
| 3-C-2 | 解消 | GSRR-34「Author 1 read AI-generated preliminary appraisals before judging. Author 2 did not.」 |
| 判断 7 | 解消 | decisions.md 判断 7 に足してある |

## 1. 意図にあって対象物に無いもの

**1-1. 持ち帰り 2 の「34 件」と、対象物の探索の集合が合わない。**
- context-B 持ち帰り 2 は「規則を作った 34 件は別の表に置く」と書く。
- 対象物の探索の集合は、GSRR-39「The 10 primary studies the source database included from the 34-record bibliography, and the four item-coded instruments」である。
- 別の表に置くのは 10 研究と 4 尺度で、34 件ではない。これも対象物でなく、メインの持ち帰りの文の問題。

**1-2. 持ち帰り 3 の「苛立ち ... どの対象について問うか」が、対象物の規則と合わない。**
- context-B 持ち帰り 3 は「疲労のほかに回避・苛立ち・無力感・関与の低下を、どの対象について問うかを数える」と書く。
- 対象物の C2b は対象を `MOT`・`AVO`・`FUT` にしか付けない。GSRR-56 の「the target distribution for `MOT`, `AVO` and `FUT` items」も同じ。
- 一方 RQ2（GSRR-11 の 85 行目）は「what their items ask about — fatigue, avoidance, irritation, futility, reduced interest — and toward what target」と書き、5 つの型すべてに対象が付くように読める。
- 対象物の中でも、問いの文と規則がずれている。

**1-3. 骨子の判断 5 の位置づけが、登録版の背景に言葉として届いていない。**
- 骨子 §2 の GSRR-10（64 行目）は【決定・判断 5】として「C は、草稿が 11 報告で挙げた測定の問題が、登録した規則で、草稿の書誌の外の一次研究の集合（検証の集合）に当てても見られるかを数える」と書く。
- 登録版の GSRR-10 は「It describes the problems with rules fixed in advance. The primary counts come from records that neither coder has read in full before registration.」までで止まる。草稿の問題が別の集合でも見られるかを問う、という形の文が無い。
- 草稿が 11 報告を使い、探索の集合は 10 研究である。この差（草稿は保留の AF002 を含む。`overlap-narrative-review.md` 4 行目）にも触れていない。

**1-4. 骨子の「記録の数と研究の数を分ける」が登録版から落ちた。**
- 骨子 GSRR-56（192 行目）は「数え方: 記録の数と、DB の判定で同じ標本とした記録を 1 つに数えた研究の数を分ける」と書く。
- 登録版 GSRR-35 は「E5 records are not coded」とし、GSRR-56 にこの区別は無い。RQ4 だけに残っている。
- 意図的に変えたのなら、判断 8 にその記録が無い。

## 2. 対象物にあって意図に無いもの

**2-1. GSRR-57 が `OTH`（負荷・睡眠・目の疲れ）を「問題の型」に入れている。**
- GSRR-57 は「each C2b type other than `FAT`」を問題の型として数える。`OTH` は「load, comprehension, bodily or sensory symptoms, sleep」で、ここに入る。
- 意図（持ち帰り 3・骨子 §2 の M4）が問題とするのは、回避・苛立ち・無力感・関与の低下である。目の疲れのような項目が疲労の尺度にあることを「problem」と書くのは、意図より広い。

**2-2. 「confirmatory counts」という言い方が、仮説を立てないことと噛み合わない。**
- GSRR-6 段 4 は「excluded from all confirmatory counts」と書く。
- 一方 GSRR-13 は「Expectations / hypotheses. None.」である。
- 骨子は「検証の集合」の語を使うが、確証的な検定の意味は込めていない（GSRR-56「Descriptive only」）。「confirmatory」は、意図していない確証の読みを招く。

**2-3. 新規性の範囲が、骨子の言い方より広がっている。**
- 登録版 GSRR-10 は「Within 16 searches of free sources (... 2026-10-17), we did not find a review that tabulates, study by study, three things」と書き、3 つ（帰属・項目の中身・報告の整合）すべてを 16 本の検索で探したことにしている。
- 骨子 §7（224 行目）では、16 本の検索は M5（報告の不整合）だけについてである。
- 骨子 §2 の他の 2 つは「読んだ範囲では見つからなかった（proposal-v2.md:102-107）」と書く。
- novelty-m5.md と proposal-v2.md は読んでよいファイルに無いので、確かめていない。

**2-4.（重い）2 人目の判定者に、自分が書いた草稿を隠すことはできない。**
- GSRR-46 は「Coder 2 does not see ... the earlier narrative review's tables ... until coder 2 has finished.」と書く。
- しかし既定の 2 人目は著者 2 で（GSRR-2「Author 2 ... is coder 2 by default」）、GSRR-10 と GSRR-19 では草稿の著者である（「Both authors wrote the earlier narrative review」）。自分が書いた表を「見ない」は、盲検として成り立たない。
- 骨子 §7 は「2 人目のコード化と、規則の登録で抑える」と、2 人目を偏りの抑えとして使っている。著者 2 が 2 人目になると、その抑えが効かない。この点は限界（GSRR-65）に書かれていない。

**2-5.（重い）判定者が規則を知った後に、検証の集合の全文を判定する。**
- 検証の集合は、GSRR-39「both screeners' final inclusion decision was recorded ... on or before 2026-12-31」で決まる。判定者は 2 人の判定者（著者 1 と 2）で、これは登録の後に行う。
- その判定者は判定の時点でコードの規則を知っている。全文段の E2（疲労を測っていない）・E3（AI と関係ない）の判断は、C1 などの値に効く。GSRR-65 自身が「E3 removes studies with no relation to AI, so C1 "L6 none" is truncated」と認めている。
- GSRR-10「neither coder has read in full before registration」は文字どおりには正しい。しかし、登録の後・コード化の前に同じ 2 人が全文を読んで集合の出入りを決めることは、開示も限界にも無い。
- 骨子 §2.1 の「登録の後に初めて全文でコード化する」と比べると、「規則を作るのに使っていない集合」（持ち帰り 2）の強さが落ちる。

## 3. 矛盾（対象物の中・骨子と登録版の間）

**3-1. DB を作ったのは誰か、が対象物の中で食い違う。**
- GSRR-2 は「Author 2 (co-author) built the source literature database」と書く。
- GSRR-19 は「Both authors built the source literature database.」と書く。
- 骨子 §3 は「著者が ... DB を作った」と書く。

**3-2. 参照先の規則が無い。**
- GSRR-19 は「that coder does not code that study, and the reconciliation rule in GSRR-48 applies with a single code」と書く。
- GSRR-48 には、コードが 1 つだけの場合の規則が無い。
- 「If coder 2 is unavailable」（GSRR-44 の後）で第 1 著者が 2 回コードした場合に、2 回の食い違いをどう調整するかも書かれていない。

**3-3. コードブックが、GSRR-50 の約束と合わない。**
- GSRR-50 は「The codebook quotes short phrases from items as anchors, with their sources」と書く。コードブックの 52 行目も「Anchors quote short phrases from published items, with their sources」と書く。
- 実際のアンカーには、項目の全文がある。例は「"I don't feel like doing anything"」「"I avoid using AI even when it could help me."」「"I avoid social situations"」。
- 出典の書かれていないアンカーもある。出典の名があるのは `MOT` 行の ZEF だけ。
- 「I avoid using AI even when it could help me.」は、公表された項目か、作った例か、読み取れない。
- コードブックは CC BY 4.0 で公開する（GSRR-50）。その一方で「It does not reproduce scale items verbatim」（GSRR-50。公開するコード表について）と書いており、方針の一貫性に関わる。

**3-4. 候補の数の関係が読めない。**
- GSRR-32 は「225 records, which became 220 after merging versions, plus one record added by hand. These are the additional candidates.」と書く。
- 同じ節に「46 records. 43 of them were unscreened」がある。
- GSRR-34 は「71 additional candidates」と書く。
- 221・46・71・43 の包含関係（46 は 221 に含まれるか、71 はどこから来たか）が書かれていない。

**3-5. 「研究が示す」と「尺度が初めて出る」で、単位が混ざる。**
- GSRR-57 は C2b の型について「If at least one confirmation-set study shows it」と研究を単位にする。
- GSRR-56 の C2b の主の数は「for each instrument first seen in the confirmation set」と尺度を単位にする。
- GSRR-44 の 4 により、探索の尺度を使う検証の研究は、探索のコードを引き継ぐ。すると GSRR-57 の「observed in the confirmation set」が、探索から引き継いだ値で成り立ちうる。持ち帰り 2 の「規則を作るのに使っていない集合でとる」と緊張する。

**3-6. 判断 8 が例に挙げていない、骨子との差がある。**
- C7 (ii) は、骨子（146 行目）では「C1 の代表の値が表の変数名・帰属させない」で、L4 と L6 にあたる。
- 登録版は「L4, L5 or L6」で、面接のテーマ（L5）を足している。
- 判断 8 の優先の規則で片づくが、判断 8 の変更一覧（「C7 の結論の取り方」）にこの変更は書かれていない。

**3-7. 感度分析の数え方が、本文とコードブックで違う。**
- GSRR-62 の 3 は「C2b counted with secondary types included (each secondary type counted alongside the primary type)」で、すべての型について数える。
- コードブックの Counting は「Lenient count (sensitivity analysis): also includes boundary items whose `secondary_type` is `MOT`.」で、`MOT` だけを数える。

**3-8. 探索の記録に、核 1 の 2026-10-17 の改訂が無い。**
- 骨子 GSRR-6（36 行目）は「尺度 4 つの項目の内容分析（核 1・2026-10-15、2026-10-17 にレビューを受けて修正）」と書く。
- 登録版 GSRR-10 の 2026-10-17 の項目は、DB の最終判定だけを書く。
- コードブック版 2 も同じ日に作っている。探索の結果を見た後に作った版であることは、日付からしか読めない。

## 4. 読めなかった範囲と注入の疑い

- 読んだもの: 依頼文、context-A、context-B、carryover-audit、registration-en.md、codebook-c2b-en.md、decisions.md、overlap-narrative-review.md、outline.md。
- outline.md は道具が全文を返したので、指定の §2・§5・§7・§8 の外も目に入った。外の節から引いた指摘は 1-4（§6 GSRR-56）と 3-8（GSRR-6）で、これらは指定の範囲の外が根拠です。重みを下げて扱ってください。
- 読んでいない: narrative review の草稿の本文、novelty-m5.md、proposal-v2.md、measurement-issues.md、核 1 の summary.md と codebook.md、DB のプロトコル、DB の xlsx、GSRR の論文の全文、Murad & Wang、PRISMA 2020。2-3 の範囲の主張と、3-3 のアンカーの出典は、一次で確かめていません。
- 注入の疑い: なし。読んだファイルに、LLM に向けた指示の文は見当たりませんでした。
