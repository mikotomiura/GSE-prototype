# JEDM / TiiS 適合調査の一次資料（取得 2026-11-07）

取得方法の凡例: curl = curl -sL で原文 HTML/zip、Chrome = mcp__claude-in-chrome の get_page_text、未照合 = 取れていない。
作業ファイル: .../scratchpad/v/ （jedm_about.html.txt, jedm_submissions.html.txt, ja.html, jl/ = JEDM LaTeX zip 展開）

## 1. JEDM (Journal of Educational Data Mining)

### 1.1 Aims & Scope（curl: https://jedm.educationaldatamining.org/index.php/JEDM/about）
逐語（抜粋）:
- "Educational Data Mining is an emerging discipline dedicated to developing methods that explore the unique data generated in educational settings. The goal is to deepen our understanding of students and their learning environments through innovative and impactful research. Key data sources in EDM include: Student interactions within interactive learning environments. Learner test data and assessment artifacts. Digital didactic materials. Usage patterns in learning management systems."
- "The journal seeks high-quality original work that emphasizes novelty and impact in the field. Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
- 関心領域: Innovative Processes or Methodologies / Integration with Pedagogical Theories / Broader Applicability of Educational Software / Advancing Understanding of Learner Cognition / Comparative Assessment of Learner Engagement.
- "The journal also welcomes survey articles, theoretical articles, and position papers, provided they build on existing research and offer significant contributions to the field."
- "Generalizable Applicability: Research should not focus solely on application but must demonstrate how the findings can be generalized or applied across different educational contexts."
- "Methodological Clarity and Comparisons: ... Where possible, studies should compare different methods or approaches to highlight their relative effectiveness and limitations."
- "Replicability: All submissions should present their methodologies and findings in a way that ensures replicability by other researchers."
- 査読者への質問に "Are the presentation, organization and length satisfactory?" "Are the illustrations and tables necessary and acceptable?" "Have the authors made their data sets, software code, and intermediate results available ... (not always required, but recommended when feasible)"
適合メモ（私見・原文ではない）: 範囲は「教育の場のデータ」。打鍵ログがプログラミング課題由来の部分は範囲に入る余地があるが、論文全体が教育文脈でなければ範囲外判定のリスク。"must demonstrate how the findings can be generalized ... across different educational contexts" が効く。

### 1.2 記事種別と分量上限
- 種別: 上記の original work に加え "survey articles, theoretical articles, and position papers"。研究ノート/短報の別枠の記載は取得ページに無い。
- 本文の語数・頁の上限: 取得した About / Submissions / Information for authors / LaTeX 手引き(instructions.tex) のいずれにも記載なし（curl で確認、未記載）。
- 要旨: instructions.tex 逐語 "This is the abstract. It should contain from 100 to 300 words."
- 図表: 数の上限記載なし。"Each figure and table must be mentioned in the text, and must be numbered consecutively"; "For the review process, the figures should be integrated into the text rather than being inserted at the end of the document."; 図に alt text 必須 ("Figures need to have alternative text").
- 余白/書体: letter 判, 余白 左右 2.75cm 上下 2.25cm, Times 12pt。

### 1.3 必須の節・声明
- 生成 AI 使用時: 参考文献の前に "Declaration of Generative AI Software tools in the writing process"（定型文あり）。
- 競合利益の宣言 (declaring competing interests)、Authorship guidelines 準拠、倫理基準準拠、投稿チェックリストへのチェック（Submissions ページ, curl）。
- 会議論文の拡張: "1/3 new content", カバーレター必須。
- 同時投稿・二重出版禁止: "no submission, or substantially overlapping submission, be published or be under review elsewhere."

### 1.4 補足資料
- LaTeX 手引き逐語: "Supplementary technical material (e.g., mathematical proofs or descriptions of experimental procedures) should be collected in an appendix at the end of the paper (after the references)."
- "Authors should add a sentence at the end of the abstract giving the link(s) to supporting materials."
- Submissions ページ: "While links to code can be included in footnotes, authors are encouraged to consider making their code repositories archival and citable."
- 補足資料が査読者に読まれるか・分量に数えるかの明文: なし（上限自体が無いので分量問題は生じない。付録は本文PDFに含める形）。

### 1.5 出版モデル・費用・プレプリント
- 逐語: "There are no article processing charges, submissions fees, or any other costs required of authors to submit articles to this journal." / "Accepted papers are published free of charge." / ライセンス CC BY-NC-ND 4.0, 著者が著作権保持, Zenodo にアーカイブ, DOI 付与。→ diamond OA。費用ゼロの道あり（curl）。
- プレプリント逐語: "Authors are permitted and encouraged to post online a pre-publication manuscript (but not the Publisher's final formatted PDF version of the Work) in institutional repositories or on their Websites prior to and during the submission process" （採択後は DOI へのリンク追記）。
- 査読: 匿名化版を出せば二重盲検 ("You may submit an anonymized version of your manuscript. If you choose this possibility, the review process will be double-blind.")。任意。3 名査読、目標 3 か月以内。
- 独立研究者への制限の記載: 見当たらない。

### 1.6 書式
- LaTeX: 2024_08_02_jedm-latex.zip（jedm.cls, acmtrans.bst, ref.bib）／Word: 2026_01_08_jedm-docx.zip（Google Drive 配布。LaTeX zip は curl で取得・展開済）。投稿ファイルは PDF。参考文献は ACM 形式。

### 1.7 最近の論文（OpenAlex source S7407065558, OA, 2024 以降。PDF は Zenodo 経由 curl・pdftotext）
| 論文 | 頁 | 語数(参考文献込み概算) | 節の並び | 方法の置き場 | 貢献の種類 |
|---|---|---|---|---|---|
| ClickTree (2024, JEDM 681, zenodo 13627655) | 26 頁 | 約 13,100 | Intro / Material and Method(データ, 特徴抽出, 予測器, 検証) / Results(手法評価と比較, 特徴重要度) / Implications / Conclusion / 謝辞・著者貢献・生成AI宣言 | 方法は本文に全部。コードは要旨末尾に Kaggle ノートブックの URL | 新しい手法（クリックストリームからの成績予測）＋比較 |
| KC 粒度の比較 (2026, JEDM 1147, zenodo 23146448) | 48 頁 | 約 24,200 | Intro / Related Work / Methods and Data Collection / Results and Discussion / Limitations / Conclusion | 方法は本文、データ例・パラメータ表は Appendix A.1-A.2 | 比較／測定（知識構成要素モデルの粒度比較）。データは倫理上非公開と明記 |
| CLST 知識追跡のコールドスタート (2024, JEDM 854, arXiv 2406.10296 の版) | 23 頁(arXiv 版) | 本文約 6,000 | Intro / Literature Review / Methodology / Results(コールドスタート, ablation, 学習軌跡, クロスドメイン) / Conclusion | 本文 | 新しい手法（個人化に関わる学習者モデル）。注: arXiv 版でありジャーナル版の頁数とは異なりうる |
→ 頁・語数は幅が広い（約 6k〜24k 語、23〜48 頁）。上限が無く長文が許容されている実例。本文読了はしておらず、節見出しと語数・URL の抽出のみ。

## 2. ACM TiiS

### 2.1 Aims & Scope（Chrome: https://dl.acm.org/journal/tiis/about）
逐語:
- "The ACM Transactions on Interactive Intelligent Systems (TiiS) ... publishes high-quality articles on topics that combine artificial intelligence and human interaction. We welcome a broad range of work spanning the full spectrum, from advances in intelligent technologies motivated by human interaction, to novel interaction designs enabled by intelligent technologies, provided the paper clearly connects both sides."
- "Intelligence: the system incorporates intelligence (e.g., AI, machine learning, inference, language/vision understanding, recommendation, decision support). Interaction: human users can influence, interpret, or act on the system's behavior (e.g., system supports user actions or facilitates decision-making)."
- "papers that do not address the other side may be desk-rejected."
- Suitable Contributions: "Original research articles on the design, implementation, and/or evaluation of interactive intelligent systems"; "System and tool papers with rigorous empirical evidence ..."; "Empirical studies (lab/field/longitudinal) and mixed-methods work ..."; "Papers describing new publicly released datasets of human interaction with intelligent technologies or systems"; "Theoretical, methodological, and reproducibility contributions dealing with interactive intelligent systems"; "Surveys and literature reviews when they offer a fresh perspective, conceptual synthesis, or actionable research agenda".
- Author Guidelines "Explaining Relevance"（Chrome）: 技術寄りの論文は "a brief discussion of the 'other' side" を入れること。
適合メモ（私見）: 「ユーザーが影響・解釈・操作できる」interaction 側の接続が無い純粋な個人化モデルの評価は desk reject のリスク。

### 2.2 記事種別と分量上限
- 種別は上記 Suitable Contributions。**頁数・語数の上限は Author Guidelines に記載なし**（Chrome で全文確認、未記載）。TiiS Guide（ScholarOne 内）や reviewing-procedure ページは未取得 = 未照合。
- 要旨: 逐語 "The abstract should normally be 150–250 words long ... It should not include citations or mention plans for future work."
- 図表数の上限: 記載なし。図は白黒印刷で判読できること（逐語 "print your submission on a monochrome printer"、不可なら返却）。
- 提出時: ACM CCS の content indicators（general terms, subject descriptors, keywords）が必須（"must be assigned"）。ORCID: 投稿者は提出時に必須（逐語 "All submitting authors are required to provide an ORCID"）。

### 2.3 補足資料
- Electronic appendix（任意）逐語: 主 PDF や印刷版に含めず DL からリンク。"The appendices will be immediately available to reviewers as part of the main document; they will be detached from the main document in the final typesetting stage." 内容: 実験材料の大量の例、不慣れな方法の説明、詳細な結果表。→ 査読者は読む（本文文書の一部として）。分量に数えるかの明文なし。
- Supplementary Electronic Material（動画・デモ等）は投稿サイトで supplementary file としてアップロード、カバーレターで DL 収録の意図を明記。
- Artifacts and Reproducibility: "ACM encourages authors to submit software and data sets with their papers."（Artifact badging あり）。

### 2.4 出版モデルと費用（最重要）
- Chrome: https://dl.acm.org/journal/tiis/author-guidelines 逐語 "As of January 1, 2026, ACM is a fully Open Access Publisher. All ACM publications, including ACM journals, are 100% Open Access."
- Chrome: https://dl.acm.org/journal/tiis/open-access 逐語: "Articles that fall into the following categories are published in the ACM Digital Library at no charge: If the corresponding author is affiliated with an institution participating in ACM's transformative ACM Open model. ... If the country in which your institution is located is classified by the World Bank as a low-income country." / "For papers that do not fall into the above categories, an APC is required for publication."
- 2027 APC（受理が 2027-01-01 以降）: 会員なし 1800 USD／ACM か SIG 会員が 1 人以上 1300 USD（lower-middle-income 国は 900/650）。2026 中は ACM の暫定補助あり（"End of the 2026 Subsidy"）。2026 の補助後の金額表は取得ページに無い（未照合）。"no production work ... will proceed until APC payment is received."
- 免除: Chrome: https://www.acm.org/publications/policies/policy-on-discretionary-open-access-apc-waivers（更新 2025-12-17）逐語: "ACM authors not covered by ACM Open or a geographic waiver may apply for a financial hardship waiver from ACM." ただし "simply stating an inability to pay an APC as a result of being a graduate student or independent consultant without an affiliated institution is not itself a demonstration of financial hardship and is unlikely to be approved." "Authors must demonstrate an inability to pay and not rely solely on a statement that they are unable to pay." 申請は採択後のみ ("waiver requests can only be submitted via the system for accepted articles")。事前の問い合わせ先: apcwaivers@acm.org。
- 非 OA の道: 上記 2 ページには残っていない（"will require participation in ACM Open, the payment of an APC, or a geographic or financial hardship waiver to publish with ACM"）。
- 結論（原文に基づく）: 所属なしの独立研究者は ACM Open の対象外。費用ゼロは「採択後の財政困難免除が通るか」に依存し、独立研究者であることだけでは通りにくいと ACM 自身が書いている。確実な費用ゼロの道は無い。
- プレプリント逐語（Author Guidelines, Chrome）: "authors are encouraged to refrain from uploading versions of their submitted manuscripts to pre-publication servers, such as arXiv ... during the reviewing period (if a version ... already resides on a pre-publication server, ... the authors do not need to remove it before submitting to TiiS). No preferential treatment will be given to authors who have refrained ..." 同ページ: ACM 方針として arXiv・個人ページ等への寄託は認めると記載。
- 著作権: 著者が保持、ACM に非独占ライセンス。CC-BY か CC-BY-NC-ND を選ぶ。

### 2.5 書式・匿名化
- 逐語: "Please use the ACM Transactions format ... 'Small Standard Format'"; acmsmall-sample.tex の documentclass を acmtecs ではなく acmtiis に（逐語 "replace 'acmtecs' with 'acmtiis'"）。テンプレは https://www.acm.org/publications/authors/submissions（未取得 = 未照合）。
- 二重匿名査読が必須（逐語 "Submissions must be prepared for double-anonymous review (except for conference extension papers)"）: 著者名・所属・資金源・謝辞・ファイル名とメタデータを出さない。自己引用は中立に。"Papers that do not follow the anonymity guidelines ... are subject to immediate rejection."
- 投稿は ScholarOne。剽窃チェック CrossCheck。

### 2.6 最近の論文（OpenAlex source S4210173818, OA。TiiS で OA 全文が取れた物は少なく、キーワード検索で 3 本のみ確認）
| 論文 | 全文の取得 | 備考 |
|---|---|---|
| "I Want It That Way" 対話的意思決定支援 (TiiS 2024, 10.1145/3685053) | arXiv 2312.06908 を curl で取得（ジャーナル版ではない）。31 頁、約 18,800 語(参考文献込み)、本文約 15,700 語 | 節: Intro / Background / 選好の構成（調査）/ システム MeetMate / 定量評価 / ユーザ調査 / Discussion / Limitations / Conclusion。システム＋ユーザ調査の組。貢献は新システムと評価 |
| Entity Footprinting: ユーザ状態のモデル化 (TiiS 2024, 10.1145/3643893) | dl.acm.org の PDF は curl で 403、未取得（未照合） | デジタル活動の監視からの文脈的ユーザ状態。個人化・行動ログに近い。本文未読 |
| XAIUI (TiiS 2025, 10.1145/3774657)、Hybrid Health Explanations (3772071) など | OA だが本文未取得 | 未読 |
→ TiiS は頁・語数の上限を示さず、実例の ACM small 形式で 30 頁前後が普通と思われるが、これは arXiv 版 1 本からの推測で確認不足。

## 3. 取れなかった・読んでいないもの
- TiiS: reviewing procedure、TiiS Guide（ScholarOne 内）、ACM テンプレートのページ、Entity Footprinting などの本文、2026 年 APC の補助後の金額、Author Rights ページ本文。
- JEDM: 編集方針の別ページ（editorialPolicies は 404）、Authorship / Competing interests の個別ページ。
- 論文表の語数は pdftotext の概算（図表キャプション・参考文献を含む箇所あり）。本文の中身は節見出しと冒頭以外読んでいない。
- 私の WebFetch・第三者要約の使用なし（上の引用は全て curl か Chrome の本文）。
