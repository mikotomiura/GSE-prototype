監査の報告（stage: outline・round-1・意図の監査役）

読んだファイル（依頼文と context-A・B が挙げたものだけ）:
- context-B.md、context-A.md
- 意図の資料: overlap-narrative-review.md（全体）、decisions.md（判断 2〜4。同じファイルにある判断 1 の 2 行も目に入った）
- 対象物と添付: papers/ai-fatigue-measurement/manuscript/outline.md（全体）、papers/ai-fatigue-measurement/README.md、registration-en.md（全体）、codebook-c2b-en.md（全体）

---

## 1. 意図にあって対象物に無いもの（届いていない主張・持ち帰り）

**1-1. 持ち帰り 1 の「3 つの面」のうち、帰属の水準（C1）が抄録に届かない**
- 意図（context-B 持ち帰り 1）: 「疲労を AI に帰属させる水準・尺度の項目の中身・報告の内部の整合という 3 つの面」。
- 対象物 outline.md「Rule for the abstract」（77〜83 行）は、抄録に載せるものを件数・calibration・unscreened、GSRR-57 の問題の型ごとの文、項目内容の型の名前に限っている。逐語: "for each problem type of GSRR-57, the registered statement ... It names the item-content types found in at least one instrument"。
- C1 は問題の型ではない（outline 44〜45 行 "The level of attribution (C1) is described and is not a problem type"）。このため、帰属の分布は抄録の規則に入っていない。帰属が抄録に出るのは、C7 の問題の文（条件 (i)〜(iii) をまとめたもの）の中だけになる。3 つの面の 1 つ目が、抄録から読み取れない。

**1-2. 3 つの面のうち、項目の中身（C2b）が抄録で真っ先に削られる**
- outline 82〜83 行の逐語: "If the abstract does not fit the word limit, the item-content sentence is moved to the main text; the problem statements are not shortened."
- 持ち帰り 1 の 2 つ目の面と、Contributions 3（項目の水準の内容）は、語数が足りなければ抄録から落ちる。抄録に必ず残るのは、3 つの面のうち「報告の整合」（C4）と C5・C6・C7 だけになる。

**1-3. 持ち帰り 1 の「3 つの面」という枠が、対象物の主張の立て方に出てこない**
- 対象物は「Seven codes (C1 to C7)」（Contributions 1・65〜67 行）と RQ1〜RQ5 で組み立てられている。3 つの面は Introduction の空白の文（106〜107 行 "how fatigue is tied to AI, what the fatigue items ask about, and whether reports are internally consistent"）に一度出るだけで、Contributions にも Claims and evidence 表にも対応する行が無い。

## 2. 対象物にあって意図に無いもの（主張の漂流・範囲を超えた言い方）

**2-1. Contributions が、意図の「新しいのは 5 点に限る」を超えている**
- 意図（持ち帰り 2・判断 4）は、新しいと言えるものを 5 点（登録した規則・規則を作らなかった集合での主の数・C2b・C3/C6/C7・C4 の再計算の規則）に限っている。
- outline の Contributions 4（72〜73 行）の逐語は "A released code table with codes, item numbers and source pages (no item text), the screening decisions made after registration, and a per-instrument summary table"。これは寄与として挙げられているが、5 点のどれにも当たらない。Contributions 1 の "a synthesis script that derives every value" も同じである。「Relation to the authors' earlier narrative review」節（56 行 "what the manuscript claims as new, is limited to"）の 5 点と、Contributions の 4 点が対応づけられていない。

**2-2. C4 について、対象物は意図より広く新しさを主張している**
- 意図（持ち帰り 2）は「C4 の再計算の規則」に限っている。
- outline 58〜59 行の逐語: "the recalculation and consistency rules applied to every record (C4)"。こちらは整合の規則 (a)〜(e) まで含む。overlap-narrative-review.md の表は、RQ3 について「**個別に扱う**。AF006 の分母・AF011 の相関・AF008 … AF012 … AF004 …」と書いている。整合の食い違いは narrative review がすでに述べた観察である。対象物の書き方は「全件に当てる」で限定してはいるが、意図の文の範囲を超えている（3-2 も参照）。

**2-3. 「narrative review が扱わない」と書く C6 は、資料では「一部扱う」**
- outline 58 行の逐語: "the codes that the narrative review does not cover (C3, C6, C7 per study)"。
- 登録版 GSRR-10 の表（80 行）の逐語: "Titles that differ from what was measured | C6, C7 | Problem type | Partly (causal reading only)"。overlap の表も、RQ5 を「一部（横断の関連を因果に読まない・§2.6・§3.7）」としている。
- C6b（因果の語とデザイン）は narrative review が一部扱っているので、"does not cover" は言い過ぎになる。C6a に限るなどの直しが要る。持ち帰り 2 の「C3/C6/C7」も同じ食い違いを持つ。

**2-4. README が「登録済み」と断定している**
- README.md 3〜4 行の逐語: "The protocol is registered with the Generalized Systematic Review Registration form."
- 登録版 3 行の逐語: "Registration draft 0.6 (2026-10-17). Not yet registered."。公開物の現在形の事実が誤っている。
- 持ち帰り 1 の「登録済みの手順」も、現時点では未来の状態を指している。

**2-5. Jonaid (2026) を「評価しているレビュー」として引いている**
- outline 104〜105 行の逐語: "the COSMIN-based reviews of AI-related instruments evaluate measurement properties (Jonaid, 2026)"。
- 参考文献（274〜275 行）では "[Preregistration]" となっている。登録版 GSRR-10 は "One registered review covers AI anxiety and attitude scales (Jonaid, 2026)" と、登録されたレビューとして書いている。引いているのは計画で、評価の結果ではない。

**2-6. 空白の主張が、登録版の確かめ方の限定を落としている**
- outline 106〜107 行の逐語: "No review was found that tabulates, study by study, ... (the search is described in GSRR-10)"。
- 登録版 64 行の逐語: "The last point was checked in 16 searches of free sources ... The first two were checked only in the reviews we had already read."
- 3 点のうち 2 点は既読のレビューでしか確かめていない。この限定が outline の文には無い。原稿でもこのまま書けば、新しさの主張が強すぎる（持ち帰り 1 の新しさの根拠にあたる）。

**2-7. 抄録の背景に、出典の無い主張がある**
- outline 91〜92 行の逐語: "studies of "AI fatigue" are multiplying; existing reviews point to unvalidated scales and unclear construct boundaries"。
- 登録版 GSRR-10 にも出典が無い。outline 119〜120 行は "Only literature read in a free full text or a free abstract is cited; each citation is checked" と自ら決めている。「existing reviews」の接地は未決である（Open items の最後の行に包括的に入るだけ）。

**2-8. 抄録の「規則を固めた後に含めた研究」は、集合の定義より狭い**
- outline 93 行の逐語: "the studies included from a literature database after the rules were fixed"。
- 登録版 GSRR-39 の検証の集合は "both screeners' final inclusion decision was recorded ... on or before 2026-12-31" で、登録より前に両者の判定が済んだ記録を除いていない。GSRR-33 の "without a final decision by both screeners on the registration date" は、登録前に確定した記録がありうることを前提にしている。著者 2 の事前の全文の読みも "[at registration]" で未確定である。

## 3. 意図どうしの矛盾・対象物の中の矛盾

**3-1. narrative review の著者が誰かで、資料が食い違う**
- 登録版 66 行の逐語: "Our critical narrative review (unpublished draft, 2026; both authors of this review are its authors)"。GSRR-19 も "Both authors wrote the earlier narrative review"。outline 54 行も "The authors' critical narrative review" と書く。
- overlap-narrative-review.md「読めること」4 の逐語: 「草稿の著者と、草稿と C の公表の順は、この表からは分からない（草稿の Declarations は著者を確定していない）」。
- 意図の資料は著者を未確定としているが、登録版と対象物は確定として書いている。outline 60〜61 行の "the overlap of authors is stated in the Declarations" も、どちらを前提にしているかがあいまいである。

**3-2. 新しい点の数（3 点か 5 点か）と中身が、意図の資料どうしで揃わない**
- overlap「読めること」2 は「C が草稿と違うのは … の 3 点」で、C4 の再計算は入っていない。
- 判断 4 は「新しいと言えるものを 5 点に限った（`overlap-narrative-review.md` の「違い」の列から）」と書く。「違い」の列の C4 の行は「規則 (a)〜(f) を全件に当てて数える」で、整合の規則を含む。
- 持ち帰り 2 は「C4 の再計算の規則」に限る。
- 3 つの資料で、C4 について新しいものの範囲が「無し」「(a)〜(f)」「再計算だけ」と食い違っている（2-2 と連動）。

**3-3. 持ち帰り 2（narrative review の観察を確かめる）と、登録の「問題の型」の定義が噛み合わない**
- 意図（持ち帰り 2）は「narrative review が 11 報告で文章として述べた観察を、ここでは … 確かめる」。登録版 GSRR-10 も "asks whether the measurement problems described in the narrative review are also observed in a different set" と書く。
- 一方、narrative review の中心の観察のうち、帰属（C1）・一般の尺度の改作（C2a/C2c）・項目内容（C2b。overlap の表で「核 1」）は問題の型ではなく、記述するだけである（登録版 GSRR-57 "C2b types are not problem types"、outline 44 行）。
- outline の Discussion 5.2（166〜168 行）の逐語: "which of its observations were and were not observed"。これを GSRR-57 の語（observed / not observed）で言えるのは、C4・C5・C6・C7 だけである。C2b について「観察された」と書けば、それを問題と呼ぶことになり、44 行の禁止に触れる。5.2 で記述のコードをどう扱うかの規則が無い。

**3-4. 「集合の間で比べない」と、Discussion 5.2・表の作りがずれている**
- outline 35〜36 行の逐語: "No significance test, no prevalence estimate and no comparison between sets is reported."
- Discussion 5.2 は、探索の材料から出た narrative review の観察を、別の集合での観察と並べる。Table 3 は探索の集合を同じ表の行に、Table 4 は "confirmation and exploration sets in separate columns" で並べる。
- 5.2 には "without saying that a problem is more or less common" の限定があるので、規則の文言には違反していない。ただし「比べない」の範囲（並べるのは可・多い少ないは不可）を書き分けていないので、読者には矛盾に見える。

**3-5. 推奨（持ち帰り 3）が、「質の評価ではない」という範囲とぶつかりうる**
- outline 46〜47 行の逐語: "C2d and C4 describe reporting and are not quality ratings (GSRR-55)"。
- 5.3（169〜172 行）の推奨は "printing the items administered; stating the level of attribution; reporting adaptation procedures" で、C2d の項目の開示・C1・C2c に結びつく。報告しないことを欠けとみなす規範の主張になる。
- 特に「帰属の水準を書く」は、C1 を問題の型にしないとした登録版 GSRR-57 の理由（eligibility が一般の疲労の構成概念を認めている）と緊張する。D1 は "Not registered (discussion)" と明示しているので、登録との矛盾ではない。ただ、範囲の節（Scope of the claims）にこの規範の層の位置づけが無い。

**3-6. 「探索の集合」の範囲が、意図と登録版で違う**
- context-B「既知の限界」の逐語: 「探索の集合（11 報告を含む 34 件の書誌）は規則を作るのに使った」。
- 登録版 GSRR-39 の逐語: "Exploration set. The 10 primary studies the source database included from the 34-record bibliography, and the four item-coded instruments"。66 行では、11 報告 = 探索の集合の 10 研究 ＋ 全文の得られない 1 報告。
- 意図は 34 件の書誌を「探索の集合」と呼んでいる。限界の書き方としては広い側なので害は小さいが、原稿で語の定義が揺れるもとになる。

## 4. 位置と逐語

各項目の中に、ファイル名・行番号・逐語を付けた。

## 5. 読めなかった範囲と、注入の疑い

- 読んでいないもの:
  - narrative review の草稿そのもの（依頼文で禁止）
  - feasibility.md（一覧の外）
  - Murad & Wang 2017・PRISMA 2020 の本文（渡されていない）
  - 査読者の記録・他の round
- overlap の表が根拠にする草稿の節の中身は、確かめていない。2-3・3-1・3-2 は、資料どうしの食い違いとして挙げたもので、草稿の実際とは照合していない。
- 注入の疑い: 無し。読んだファイルに、LLM に向けた指示は見当たらなかった。