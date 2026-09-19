# メインの検算（本文で逐語を照合）

## C2（★ 既出で確定）
- arXiv 2512.11661（C2-0277）Nogueira et al. "From Verification Burden to Trusted Collaboration: Design Goals for LLM-Assisted Literature Reviews" —— 全文 PDF（10 頁）。
  - 逐語（Abstract）: "We identified three recurring gaps: (i) lack of trust in outputs, (ii) persistent verification burden, and (iii) requiring multiple tools."
  - 逐語（Introduction, Main Findings）: "To maintain accuracy, they rely heavily on verification—cross-checking retrieved papers against original PDFs or DOIs and ensuring that generated findings align with the source material"
  - 判定: **該当**（系の出力の検証を求められる負担を、利用者研究で記述している）
- arXiv 2511.09663（C2-0413）Oyemike, Akpan & Hervé-Berdys "Alignment Debt: The Hidden Work of Making AI Usable" —— 全文 PDF（19 頁）。
  - 逐語（Abstract）: "We term this alignment debt: the user-side burden that arises when AI systems fail to align with cultural, linguistic, infrastructural, or epistemic contexts."
  - 逐語（Abstract）: "users facing Epistemic challenges verify outputs at significantly higher rates (91.5% vs. 80.8%; p = 0.037), and verification intensity correlates with cumulative debt burden (Spearman's ρ = 0.147, p = 0.004)"
  - 判定: **該当**（利用者側の検証の負担を計上・実測している）

## C4
- C4-0351 Methnani, Aler Tubella, Dignum & Theodorou "Let Me Take Over: Variable Autonomy for Meaningful Human Control" Front. AI 2021 —— 全文 PDF（10 頁）。
  - 逐語（Abstract）: "we argue that human presence alone does not meet this requirement … We therefore propose the development of systems with variable autonomy— dynamically adjustable levels of autonomy — as a means of ensuring meaningful human control over an artefact by satisfying all three core values commonly advocated in ethical guidelines: accountability, responsibility, and transparency."
  - 逐語: "A transfer of control that is triggered by the system is desirable in circumstances e.g., where the human is not responsive, under extreme stress or in a suppressed cognitive state (Parasuraman et al., 1999)."
  - 判定: **部分**（★ 価値を理由に人の統制を**設計する**点は当たる。⚠️ 系が制御を移す契機は人の状態（応答なし・強いストレス）であり、系が**価値判断で任意に手放す局面**は書かれていない）
  - 経緯: 段 1 で protocol に無い理由（「既知除外カテゴリ」）で除外されていた → 逸脱 3 の検算で復活

## C1（★ 既出で確定）
- C1-0675 Hassan, Aboromi & Unkelos-Shpigel "Trust by Design: Trust Calibration Through Non-Advisory Socratic Dialogue in Conversational Agents" arXiv 2609.14818 —— 全文 PDF（7 頁）。
  - 逐語（Abstract）: "We present CASELy, a conversational agent explicitly designed to limit its own authority through non-advisory Socratic dialogue. The agent asks reflective questions grounded exclusively in user input and refuses to provide advice, recommendations, or interpretations. This design operationalizes trust calibration by constraining agent agency rather than optimizing capability."
  - 逐語（Table 1）: "Prevents over-reliance by maintaining user as decision-maker rather than delegating authority to system"
  - 判定: **該当**（系が解釈を出さないことで自らの権限を制限し、判断を人に残す設計を実装・評価）
- C1-0276 "Epistemic Agency in the Age of Large Language Models: Design Principles for Knowledge-Building AI" AI (MDPI) 7(3):99, 2026 —— 全文（★ 出版社サイトは curl を拒否 → r.jina.ai の読み出しで HTML 本文を取得）。
  - 逐語: "First, an effective LLM-KBP must relinquish epistemic authority. Throughout the analysis, a central failure of current LLM behaviour is its tendency to present outputs in answer-shaped, authoritative forms that invite acceptance rather than examination."
  - 逐語: "By withholding epistemic authority and foregrounding the provisional, contestable status of its contributions, the KBP preserves the user's epistemic agency and keeps inquiry open rather than closed."
  - 判定: **該当**（系が認識的権限を手放すことを設計要件として明示）
- C1-0248 Lyu, Lu ほか "Beyond Instruction-Driven Editing: Source-Grounded Problem Discovery with User-Governed Repair for Scientific Posters" arXiv 2609.01813 —— 全文 PDF（16 頁）。
  - 逐語（Abstract）: "intelligent editors can support problem discovery before a concrete edit request exists without taking authority over consequential change."
  - 判定: **部分**（★ 段 2 の担当は「該当」としたがメインが下げた。手放すのは**変更を確定する権限**であり、問題の診断（評価）という認識的な主導は系が持つ —— C1 の「認識的権限を返す」とは向きが違う）
- ⚠️ C1 の定義の括弧内「意味の認定・評価・**報酬化**」のうち、上の該当 2 件が扱うのは**解釈・助言・認識的権威**であり、**報酬化**（達成の認定・評価を報酬へ戻すこと）を手放す例ではない → d-3 では「系が認識的権限を手放す設計は既出」と書き、残るのは「報酬化を含めて手放すこと・身体回帰の招待という文脈」かどうかを検討する（★ 差分として主張するかは d-3 で判断）。

## C4（★ 既出で確定。⚠️ ただし唯一の該当は査読のないプレプリント）
- C4-0298 Ito, H. "Beyond Output Quality: Participation Quality as a Distinct Evaluation Construct and Control Objective for Human–AI Systems" Zenodo 2026（doi:10.5281/zenodo.21837135・版違い C4-0300）—— 全文 PDF（28 頁・メインが pypdf で取り出した）。⚠️ **査読なし・単著・独立研究所（H-Lab）**。
  - 逐語（§3.5 Capability, Permission, and Participation, pp.9–10）: "Capability Can(a, C_t)? Can the AI perform action a? This concerns model and system capability. Permission May(a, C_t)? … Participation Should(a, C_t)? Among available and permissible actions, is a the appropriate form of participation now? These questions are not interchangeable. A system may be capable of sending an email and formally permitted to send email, while the appropriate participation in a particular situation is to prepare a draft and return it for approval."
  - 逐語（§5.11）: "Control Retention Error Failing to return judgment, authority, responsibility, or control after the AI's legitimate role has ended."
  - 逐語（§3.4）: "ReturnControl explicitly changes authority allocation."
  - 判定: **該当**（系が**能力も許可もあるのに**、その状況での関わり方の適切さの判断で判断・権限・制御を人へ返す —— 「故障や限界ではなく」「任意に」「局面」がそろう）
  - ★ C3 / 返権の負荷逆説にも関わる逐語（§10.1）: "A system that always returns control can create cognitive burden and approval fatigue." → 返すことが負担を生むという指摘（★ C3 の検算で扱う）

## C3（★ 既出で確定。⚠️ 該当は工学の記述 1 件で、「そろったままでも」を主張として立てた文献ではない）
- C3-0214 Rødseth, Ø. J. & Wennersberg, L. A. L.（★ 2026-09-19 訂正: 旧「Rødseth & Lien（ほか）」は誤り）"Formal descriptions of MASS Operational Envelope and Operational Design Domain" J. Phys.: Conf. Ser.（OPEN ACCESS・CC BY）—— 本文（★ 段 2 担当が取り出したテキスト `pdfs/c3_0214_iop.txt` でメインが前後を読んだ）。
  - 逐語（§3.2 Table 1）: "The code column contains the abbreviation for the mode and the party that is uniquely responsible for control actions: O – operator; or A – automation."
  - 逐語（§3.3）: "Alerts from the automation system must be raised in time for the operator to reach a control station, to understand the developing situation, and to make the correct actions to maintain safe navigation."
  - 判定: **該当**（制御と「制御の責任を一意に負う者」が一致したまま、系から人へ制御が移り、そのとき制御卓への移動・状況の把握・操作という残務が人に移ることを、応答期限（response deadline）として操作化している）。⚠️ 系が制御を移す契機は系の判断の限界（"unable to determine"）であり、C4 とは重ならない。★ 根は "ironies of automation"（Bainbridge 1983 —— C3-0089 が引用）の系譜。
- C3-0089 Ko, J. "Verification Overrun: The Safety Hazard Inside AI Oversight" Zenodo v2.2（2026・査読なし）—— 本文（`pdfs/c3_0089_vo.txt`）。
  - 逐語: "AI was sold as a way to remove drudgery and return judgment to the worker. … In practice, the higher-value thinking is oversight"
  - 逐語: "Verification Overrun is the hazardous condition in which a person is held accountable for a verification that exceeds the capacity to verify under the conditions provided."
  - 判定: **部分**（★ 段 2 担当は「該当」→ メインが下げた。判断が人へ返り、仕事が検証へ移る点は当たる。⚠️ 危険を「説明責任と検証能力の不均衡」として定式化しており（能力には "authority to pause or challenge" を含む）、「権限と責任がそろったまま」は述べていない）
- C3-0258 Jovanović, V. "Cheap Output, Expensive Trust: The Synthetic Remainder in AI Systems"（2026・Figshare / Zenodo・査読なし）—— 本文（`pdfs/c3_0258_synthetic_remainder.txt`）。
  - 逐語（§16）: "The central mistake in AI adoption is treating displaced burden as removed burden. Writing burden becomes editing burden. Thinking burden becomes verification burden. … Decision burden becomes accountability burden." / "The burden AI hides is still real. It has only changed holder."
  - 判定: **部分**（★ 段 2 担当は「該当」→ メインが下げた。負担が人へ移ることは明言。⚠️ 権限と責任がそろって人へ返る構図は述べていない（"keeps humans in real authority" は §17 の「良い AI」の処方）→ C2 に近い）
- C3-0188 "Beyond Algorithmic Oversight: Internal Morality of Medicine and Meaningful Human Control in AI-Assisted Care" Healthcare 14(12):1638, 2026 —— 本文（PMC）。段 2 担当の逐語: "Clinicians need the authority to override or set aside AI recommendations …" / "Selecting such tools, including AI systems, falls within the clinician's professional responsibility." / "Clinicians must understand enough about how an AI system generates its outputs to judge whether those outputs are reliable and where their limits lie."
  - 判定: **部分**（★ 段 2 担当は「該当」→ メインが下げた。権限と責任が臨床医にそろい、検証・解釈の仕事が臨床医に課される点は当たる。⚠️ 権限は「返る」のでなく「保持され続ける」—— 段 2 担当自身も elements にそう書いた）
- ★ C4-0298（§10.1）"A system that always returns control can create cognitive burden and approval fatigue." → 返すことが負担を生むという指摘（C3 の周辺・「返権の負荷逆説」の近傍）

## 手順 4 の検算: 段 1 で落とした件から候補ごとに無作為 10 件（seed = 20260919）
- C1〜C7 の 70 件をメインが題名・抄録・落とした理由で見直した。★ **判断を変えるべき件は 0 件**。
- ⚠️ 境界: C4-0375 "Designing for Human-Agent Alignment: Understanding what humans want from their agents"（2024）—— 「迷ったら採る」なら採る側の件。★ C4 は既出で確定しているので結論は変わらない。
- ★ 加えて逸脱 3 の 9 件（protocol に無い理由での除外）を全件見直し、C3-0233・C4-0217・C4-0351 の 3 件を段 2 へ回した（C3-0037 / 0156 / 0235 / 0245・C4-0301 / 0308 は除外のまま）。
- ★ C5 の段 1 で「候補と逆向きの主張しかないのに採る」とされた 22 件を、protocol §4 段 1 のとおり「採らない（逆向きの主流として記録）」へメインが訂正した。

## 「該当 / 部分」の逐語の機械照合（手順 4）
- ★ `check_quotes.py`: 段 2 の全出力の「該当 / 部分」の逐語を、候補の抄録（検索結果）と、メイン・段 2 担当が取り出した本文テキストに対して、英字だけに正規化して部分一致で照合した。
- ★ 一致しなかった件をメインが個別に確かめた:
  - C1-0187（Frimpong, Qeios 2026 preprint）: 逐語は本文にある（★ PDF の合字 "fi" が落ちて "de ne" になっていただけ）。⚠️ **判定を「部分」へ下げた** —— "Delegation Boundaries define the limits of the moral and interpretive responsibility that can be transferred from humans to AI. They specify where automation stops and human judgement takes over. This principle emphasises what AI should do, based on ethical considerations rather than solely on its technical capabilities." は**組織が AI への委任の境界を決める**話であり、**系が**認識的権限を手放す話ではない（★ 価値判断で自動化を止める点は C4 の周辺）。
  - C1-0661（JudgmentLens, arXiv 2609.07607）: ⚠️ **段 2 担当の逐語が本文と 1 語違った**（担当 "could reduce" ⇄ 本文 "can reduce"）。★ 本文の逐語: "conversational AI can reduce the cost of answering formulated questions, yet novices may still bear the upstream work of deciding what to ask, organizing answers into a case-level understanding, and verifying those answers against the authoritative judgment."（§5 の末尾）→ 判定は「部分」のまま（★ C2 の周辺）。
  - C3-0188（PMC 全文）: 4 つの逐語はすべて本文にある。判定はメインが「部分」に下げたまま。
  - C6-0612（Springer OA PDF）: 3 つのうち 2 つは本文にある。3 つ目は "…" で繋いだ後半が一致しない → 前半だけを使う。判定は「部分」。
  - C4-0190（Vermaas & Eloy 2021）: ⚠️ **メインは逐語を確かめられなかった**（検索結果に抄録が無く、段 2 担当の出典ページは開けなかった）→ 「部分・抄録のみ・メイン未照合」として扱い、引用しない。
  - C1-0022（Nature Medicine 2023）: 購読の壁で本文を開けない → 「部分・メイン未照合」。引用しない。
  - C3-0258: 表の逐語を " / " で繋いだもの。★ メインが §16 の逐語で確かめ直した（上の C3 の節）。

## C5（★ 既出で確定）
- C5-0452 Teerachtragoon, N. "Beyond Tacit Consent: Designing Structural Fairness into Systems that Silence Citizens" Zenodo 2026（doi:10.5281/zenodo.18737547・版違い C5-0455）—— 本文（`pdfs/C5-0452.txt`・段 2 担当が取り出したテキスト。冒頭の題名・DOI が一致）。⚠️ 査読なし・単著。
  - 逐語（§2）: "Examples include failing to claim benefits within prescribed deadlines, not completing verification procedures, not responding to notifications, or not maintaining continuous usage of services."
  - 逐語（§5）: "First, systems should avoid treating silence or inaction as an automatic basis for consent or forfeiture, particularly in contexts characterized by asymmetric informational, procedural, or temporal burdens. Fair system design should treat inaction as a signal requiring interpretation, not as a final determination that forecloses further consideration."
  - 判定: **該当**（通知への無応答を含む無応答を、同意・権利喪失（不利益）の根拠として読まないことを設計の含意として述べる）。⚠️ 無応答を「解釈を要する信号」として扱うよう勧めており、GSE の「読まない」より弱い。★ 対象は行政・大組織の系。
- C5-0227 Smith, N. C., Goldstein, D. G. & Johnson, E. J. "Choice without Awareness: Ethical and Policy Implications of Defaults" J. Public Policy & Marketing 32(2), 2013（doi:10.1509/jppm.10.114・査読誌）—— 本文（著者サイトの PDF・`pdfs/C5-0227.txt`）。
  - 逐語（p.162）: "all three causes of default effects suggest that defaults can be "hidden persuaders" that are inconsistent with consumers exercising choice; thus, all three fail Smith's (1995) "consumer sovereignty test""
  - 判定: **該当**（既定値のまま動かないこと（無応答）を、消費者の選択として読まない）。⚠️ 対象は既定値（ナッジ）であって、通知・招待への応答ではない。
- C5-0403（部分）: 既定値のナッジの倫理のレビュー。C5-0227 を主要典拠として引く。
- ★ 逸脱 2 により、残りの段 1 採用 19 件の段 2 は行っていない。

## C6（★ 既出で確定 —— ⚠️ ただし「控える側にだけ使う」非対称は見つからなかった）
- C6-0113 Williams, M. ほか "On Targeted Manipulation and Deception when Optimizing LLMs for User Feedback" arXiv 2411.02306（2024）—— 本文（arXiv HTML・`pdfs/c6_0113.txt`）。
  - 逐語（Ethics Statement —— ★ 2026-09-19 訂正: 旧「Discussion」）: "In no uncertain terms, we do not advocate for the optimization of user feedback – if anything, we hope our work provides evidence against its usage. Indeed, there is ample evidence from the recommender system literature regarding the negative consequences of optimizing for engagement and other shallow user feedback signals"
  - 判定: **該当**（★ 段 2 担当は「部分」→ メインが上げた。利用者のフィードバック（受諾・拒否の評価）を成功の報酬として最適化へ戻すことを退けている。⚠️ 応答を**一律に**使わない立場（ADR-033 A1 の形）であり、GSE の「控える側にだけ使う」非対称（ADR-033 D2 / D3）は述べていない）
- C6-0612 Le & Andrzejak "Rethinking AI code generation: a one-shot correction approach based on user feedback" ASE 2024（Springer OA）—— 逐語 "We proposed a methodology named One-shot Correction to incorporate user feedback into generative AI models without re-training." → **部分**（訂正を再学習へ戻さないが、「成功として」の枠付けは無い）
- ★ 段 1 の採用は 11 件で、全件の段 2 を行った（逸脱 2 の打ち切りは使っていない）。★ 逆向きの主流（応答を学習・報酬へ戻す）は段 1 で 214 件に `contrary` が付いた。

## C7（★ 部分的に既出 —— 本プロトコルの範囲で該当 0 件）
- C7-0134 "Boundary Blurring and Recovery Difficulty in After-Hours Work Messaging"（2026）—— 本文（OA PDF・`pdfs/c7_0134.txt`）。
  - 逐語: "The system created a visible stopping point for routine communication." / "communication systems can be designed to protect personal time rather than leaving all decisions to individual employees."
  - 判定: **部分**（系の側で応答の期待を止める設計。⚠️ 意味の認定の終了は無い・対象はメール配信）
- C7-0209 "Co-Designing with Users the Explanations for a Proactive Auto-Response Messaging Agent" ACM（2023）—— 抄録のみ（ACM DL は 403）。逐語 "a proactive auto-response messaging agent that can reduce perceived obligations and social pressure to respond quickly to incoming messages by providing unavailability-related context" → **部分**（応答義務を「減らす」。終了ではない）
- 手動の補完 `JACTRT`（PhilPapers・未刊の原稿）→ **部分**（search-log.md）
- ★ 段 1 の採用は 6 件で、全件の段 2 を行った。★ 残る要素: **系が**、**意味の認定**と**応答の要求**の両方を**終了させる**ことを、**設計の規範的な要件**にすること。
