# 抽出結果 G4 (AF015-AF020)

## AF015
- アクセス範囲: 書誌のみ（全文取得不可。使った URL: https://link.springer.com/article/10.1007/s44163-026-01855-3 (login gate に redirect / 303)、https://link.springer.com/content/pdf/10.1007/s44163-026-01855-3.pdf (curl で空ファイル)、OpenAlex/Semantic Scholar/Unpaywall/Crossref (書誌のみ、抄録・全文なし)）
- 書誌（一次で見えた値）:
  - 著者（全員）: Vaishali Wankhede, Komal Khandelwal（Crossref/OpenAlex/Unpaywall で一致）
  - 誌名: Discover Artificial Intelligence
  - 巻/号/頁: 記載なし（Crossref の volume/issue/page が全て null。論文番号形式の可能性あるが未確認）
  - 年・オンライン公開日: 2026-07-26（Crossref `published` / `published-online` 一致）
  - DOI: 10.1007/s44163-026-01855-3
  - 所属: Vaishali Wankhede = "Faculty of Management Symbiosis Law School, Symbiosis International (Deemed University), Pune, India"（Unpaywall raw_affiliation_strings）。Komal Khandelwal = corresponding author、同じく Symbiosis Law School
  - Funder（Crossref）: "Symbiosis International"
  - ライセンス: CC BY-NC-ND 4.0（Crossref license / OpenAlex license 一致）
- 訂正・撤回・懸念表明: Crossref `update-to` は null、`relation` は空 `{}`。訂正・撤回の兆候なし（ただし全文未取得のため出版社ページの Correction 表示欄は未確認）
- 研究デザイン: 未確認（全文未取得。タイトルから systematic review と推定されるが本文で確認できていない）
- 対象・国・募集方法・収集時期: 未確認
- N: 未確認
- AI の種類・利用文脈: 未確認
- 疲労（または中心構成概念）の操作化: 未確認
- その他の主要変数: 未確認
- 解析手法: 未確認
- 主要結果: 未確認
- 著者自身が述べる限界: 未確認
- 倫理承認・同意: 未確認
- 事前登録・データ/材料公開・資金・利益相反: 資金は Crossref funder フィールドに "Symbiosis International" とのみ記載（本文の Funding 節の逐語は未確認）
- 設計別チェック（D. システマティック／その他のレビュー）: 全項目 Unclear — 全文未取得のため判定不能
- 気づいた内部不整合: なし（書誌レベルの情報のみのため比較対象なし）
- 補足: OpenAlex は `is_oa: true, oa_status: gold` かつ `any_repository_has_fulltext: false` と記録しており、リポジトリ写しも存在しない。Springer の login-wall (idp.springer.com) が全文アクセスの障壁。Europe PMC は本レコードについては未照会（AF018 で照会した際は hitCount 0 だったが、それとは別件）

## AF016
- アクセス範囲: 全文（WebFetch 経由でページ本文を要約抽出。出版社ページ https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1921504/full ）
  - ⚠️ 注記: 本レコードは WebFetch（要約モデル経由）で取得した内容に基づく。逐語引用として示された文字列は WebFetch の出力をそのまま転記したものであり、抽出担当者自身が原文 HTML を直接目視した逐語照合はできていない（時間制約）。数値は再現性のため複数箇所で確認したが、完全な一次照合が必要な場合は再訪すること。
- 書誌（一次で見えた値）:
  - 著者（全員）: Weixu Qian, Feng Yang, Yaming Cao, Liangliang Yi, Run Gu, Zhuo Wang
  - 誌名: Frontiers in Psychology
  - 巻/論文番号: Volume 17, Article 1921504
  - オンライン公開日: 2026-08-27
  - DOI: 10.3389/fpsyg.2026.1921504
- 訂正・撤回・懸念表明: Crossref `update-to` null, `relation` 空。ページ内にも Correction/Retraction の表示なし（WebFetch 経由の確認）
- 研究デザイン: システマティックレビュー（PRISMA フロー図あり、narrative/descriptive evidence map、メタ分析なし）
- 対象・国・募集方法・収集時期: 対象は生成AI/教育AI利用に関する実証研究（高等教育の学生中心）。検索範囲は Web of Science Core Collection・SSCI・Education and Educational Research カテゴリ、英語論文限定。検索日: 2026年6月
- N（研究数）: 初期ヒット 139 件 → カテゴリフィルタ後 86 件 → タイトル/抄録スクリーニングで 30 件除外 → 全文評価 56 件 → 全文除外 19 件 → DB経路採択 37 件 + 後方引用 2 件追加 = 最終 39 件
- AI の種類・利用文脈: 生成AI・教育用AI/会話型AIシステム（GenAI, chatbot, LLM 等）、高等教育文脈
- 疲労（または中心構成概念）の操作化: 本レビューの中心構成概念は「認知負荷 (cognitive load)」（intrinsic/extraneous/germane の3成分）であり、fatigue/exhaustion/burnout は主構成概念ではない。疲労を測定した一次研究の特定: **特定できず**（レビュー本文中に fatigue/exhaustion/burnout の語が言及されている記述を確認できなかった。WebFetch 要約では「回答なし」との回答）
- その他の主要変数: cognitive offloading の枠組み採用の有無（39件中13件のみ明示採用）
- 解析手法: "narrative synthesis"「構造化記述的エビデンスマップ (structured descriptive evidence map)」。異質性のためメタ分析は実施せず
- 主要結果（WebFetch 経由の逐語）:
  - Extraneous load (n=16 distinct measures): Lower 7 / No difference 3 / Higher 1 / Curvilinear 1 / Non-directional 4
  - Overall/undifferentiated load (n=22): Lower 11 / No difference 5 / Higher 2 / Non-directional 4
  - Germane load subscale (n=11): Higher(directional) 4 / Curvilinear 1 / No directional comparison 6
  - "Cognitive Offloading Framing: Only 13 of 39 studies explicitly adopted this lens."
- 著者自身が述べる限界（逐語、WebFetch 経由）:
  - "The search was restricted to English-language articles indexed in the SSCI within the Web of Science Core Collection and the Education and Educational Research category; studies indexed elsewhere may therefore be absent."
  - "The heterogeneity of instruments and study designs, together with the absence of a validated independent study-level risk-of-bias appraisal, precludes quality- or precision-weighted synthesis."
  - "Most studies relied on self-report and many used overall or undifferentiated load measures, so lower reported load cannot by itself be interpreted as lower extraneous load or improved learning."
- 倫理承認・同意: 本文中の方法節における IRB/倫理承認の記載は WebFetch 出力に含まれず（未確認。レビュー論文のため通常不要な可能性）
- 事前登録・データ/材料公開・資金・利益相反:
  - COI: "The author(s) declared that this work was conducted in the absence of any commercial or financial relationships that could be construed as a potential conflict of interest."
  - Funding: "This work was supported by the Shandong Provincial Department of Education under the 2025 Undergraduate Teaching Reform Research Project (Key Project; grant no. Z2025442)."
  - 生成AI利用開示: "The author(s) declared that Generative AI was used in the creation of this manuscript. DeepSeek and Kimi were used to translate from Chinese to English and to improve clarity and grammatical accuracy."
- 設計別チェック（D. システマティック／その他のレビュー）:
  1. 問いが明確か: Yes — RQ1-3 が明記されている
  2. 組入れ基準が問いに適切か: Yes — GenAI/教育AI + cognitive load 測定 + 実証データという組入れ基準が明記
  3. 検索戦略が適切か（式・日付・情報源）: Yes — WoS Core Collection・SSCI・Education カテゴリ、Topic式（3ブロックAND結合）、2026年6月検索、日付制限なし(データベース発足以降)
  4. 情報源が十分か: Unclear — 単一データベース(WoS)のみで、著者自身が限界として認めている
  5. 批判的吟味の基準が適切か: No/Unclear — "absence of a validated independent study-level risk-of-bias appraisal" と著者が明記。検証済みツールは不使用
  6. 吟味を2名以上が独立に行ったか: Yes（分類コーディングについて）— "Dual-coded across 14 dimensions" "Independent Dual Coding: Yes, explicitly stated"、Cohen's kappa報告（ただし個別studyのrisk-of-bias評価ではなくカテゴリ分類のコーディングに対する二重化）
  7. 抽出の誤りを減らす手順: Yes — カッパ係数算出、不一致の合意解決の記載
  8. 統合方法の適切さ: Yes（異質性を理由にメタ分析を回避しdescriptive mapを採用、という判断自体は方法論的に整合）
  9. 出版バイアスの評価: No — 実施されていないと明記
  10. 提言がデータに支持されているか: Unclear（要全文照合）
  11. 今後の研究への指示が適切か: Yes（germane load測定の不足等、具体的な今後の方向を提示）
  - 採択件数: 39（初期139件から）/ 検索日: 2026年6月 / PRISMA流れ図: あり（Figure 1）
- 気づいた内部不整合: なし（WebFetch要約の範囲内では検出せず。ただし一次照合未了のため断定不可）

## AF017
- アクセス範囲: 全文（PDF を取得し pypdf でテキスト抽出。https://ceur-ws.org/Vol-4134/paper2.pdf 、25頁、104,571文字）
- 書誌（一次で見えた値）:
  - 著者（全員）: Pratik Sapkota (Tampere University), Markus Makkonen (Tampere University), Henri Pirkkalainen (Tampere University), Markus Salo (University of Jyväskylä)
  - 会議: The 11th International Workshop on Socio-Technical Perspectives in IS (STPIS'25), September 17-18 2025, Skopje, North Macedonia. CEUR Workshop Proceedings, Vol-4134, paper 2
  - ISSN: 1613-0073
  - 出版日: "published 2025-12-20"（本文フッターの逐語）
  - DOI: 記載なし（URN のみ。input-G4.md 記載通り "DOI未確認"）
  - ライセンス: "© 2025 Copyright for this paper by its authors. Use permitted under Creative Commons License Attribution 4.0 International (CC BY 4.0)."
- 訂正・撤回・懸念表明: 本文中に記載なし。Crossref 照合は DOI 不明のため未実施
- 研究デザイン: システマティックリテラチャーレビュー（Okoli (2015) の8段階法 + PRISMA 2020 ガイドライン準拠）
- 対象・国・募集方法・収集時期: 対象は「AIが職場でストレスを誘発する要因」を扱う査読済み英語ジャーナル論文。単一データベース Scopus を 2025年3月7日に検索
- N（各段）:
  - 検索ヒット: 1,333 件（重複2件除去後の unique records）
  - 第1段階（タイトル/抄録）除外: 1,210 件除外 → 123 件残存
  - 第2段階（全文評価）除外: 57 件除外 → **最終採択 66 件**（quantitative 40 / qualitative 9 / mixed-methods 6 / conceptual 11）
- AI の種類・利用文脈: 職場文脈のAIシステム全般（customer-facing service AI 13件・algorithmic management/surveillance 11件・clinical AI 11件・generative AI 5件・industrial automation 4件・transport AI 3件・finance AI 1件・STARA全般18件）
- 疲労（または中心構成概念）の操作化: 中心構成概念は「AI-stressors」（techno-overload等の既存6 technostressor + 新規5 AI-stressor）。burnout/exhaustion は「ストレスの帰結(strain)」として言及されるが、レビュー自体の主要構成概念ではない。★疲労が「AIの利用・監督」に帰属して測られているかは各一次研究依存（下記参照）
  - 一次研究のうち fatigue/exhaustion/burnout を実際に測定したと本文で確認できたもの（最大10件。本文の記述に基づく判断であり、各一次研究への遡及照合はしていない。「特定できず」ではなく「本文の記述から推定できる」レベル）:
    1. Kim, B.-J. & Lee, J. (2024). "The mental health implications of artificial intelligence adoption: the crucial role of self-efficacy." Humanit Soc Sci Commun 11:1561. DOI: 10.1057/s41599-024-04018-w — 本文: "Survey studies reinforce the pattern: STARA awareness or bossware oversight consistently predicts lower perceived job autonomy, which in turn drives reduced engagement and higher burnout [48,50]."（[48]=本文献）
    2. Hur, W.-M. & Shin, Y. (2024). "Service employees' STARA awareness and proactive service performance." JSM 38:426–442. DOI: 10.1108/JSM-03-2023-0115 — 同上引用 [50]
    3. Chuang, Y.-T., Chiang, H.-L., Lin, A.-P. (2025). "Insights from the Job Demands–Resources Model: AI's dual impact on employees' work and life well-being." International Journal of Information Management 83:102887. DOI: 10.1016/j.ijinfomgt.2025.102887（★このレビューの参考文献[68]=本レコード群の AF019 と同一論文。本文: "Where measured quantitatively, techno-uncertainty correlates with technostress, emotional exhaustion, burnout, reduced productivity, lower self-efficacy, and diminished AI adoption intentions [48,68,70]."）
    4. Meduri, K. et al. (2024). "Human-centered AI for personalized workload management: A multimodal approach to preventing employee burnout." J. Infras. Policy. Dev. 8:6918. DOI: 10.24294/jipd.v8i9.6918 — 本文: "Mixed-methods and longitudinal studies further link perceived AI complexity to burnout [48,72]"
    5. Jeong, J., Kim, B.-J., Lee, J. (2024). "Navigating AI transitions: how coaching leadership buffers against job stress and protects employee physical health." Front. Public Health 12:1343932. DOI: 10.3389/fpubh.2024.1343932 — 本文: "Longitudinal evidence indicates that any short-term motivational lift from challenge-appraised overload...quickly flips to hindrance, manifesting as burnout and reduced engagement [44]."
  - 上記は narrative synthesis の記述からの推定であり、各一次研究の burnout/exhaustion の操作化（尺度名等）はこのレビュー本文からは確認できていない（未確認）
- その他の主要変数: 既存6 technostressor（techno-overload/invasion/complexity/insecurity/uncertainty/unreliability）+ 新規5 AI-stressor（techno-unpredictability, loss of autonomy, ethical/moral conflict, social erosion, career disruption）の出現頻度（該当研究数・%）
- 解析手法: narrative synthesis（inductive coding によるテーマ抽出）。メタ分析なし（"no quantitative meta-analysis was performed"）
- 主要結果（逐語）: "Screening 1,333 records yielded 66 eligible articles (40 quantitative, 9 qualitative, 6 mixed-methods, and 11 conceptual)"／"22 studies (about 33%)" が loss of autonomy を報告／"46 studies (about 70%)" が techno-insecurity を報告／"49 studies (about 74%)" が techno-uncertainty を報告
- 著者自身が述べる限界（逐語）:
  - "our inclusion was restricted to studies that explicitly examined stress related to AI, which may introduce a bias"
  - "most empirical evidence is cross-sectional...limiting causal inference...Only a few longitudinal studies [49,57,61,68,79,86] exist"
  - "we did not formally weight studies by quality. We included conceptual studies on equal footing with empirical ones"
  - "our search strategy, confined to one database (Scopus) and specific keywords might have missed relevant works that discuss similar phenomena under different terms (e.g., 'strain' or 'burnout' instead of stress)"
- 倫理承認・同意: 記載なし（システマティックレビューのため方法節に被験者倫理承認の言及なし。本文全体を確認したが該当箇所なし）
- 事前登録・データ/材料公開・資金・利益相反:
  - 事前登録: プロトコルは「事前に策定 (established a structured review protocol)」と記載されるが、PROSPERO等への公式事前登録の言及はなし（未確認/記載なし）
  - COI: "Competing Interests: The authors declare no competing interests or conflicts of interest relevant to this work."
  - データ公開: "Data Availability: The full list of the 66 included studies can be accessed here."（リンク先はPDF内ハイパーリンクのためテキスト抽出では確認できず、未確認）
  - 資金: 本文中に Funding 節の記載を発見できず（未確認）
  - 生成AI利用: "Declaration on Generative AI: The author(s) have not employed any generative AI tools in the development of this manuscript, aside from standard grammar-checking tools (e.g., Grammarly)."
- 設計別チェック（D. システマティック／その他のレビュー）:
  1. 問いが明確か: Yes — "RQ1: What kinds of emerging AI-stressors have been identified...RQ2: How do these AI-stressors differ..."
  2. 組入れ基準が問いに適切か: Yes — 3条件（英語・最終出版段階の査読論文／職場でのAI由来ネガティブストレスを明示的に扱う／ストレスとAIの直接的リンクを報告 or 理論化）を明記
  3. 検索戦略が適切か（式・日付・情報源）: Yes — 完全な Scopus 検索式を逐語で報告: "TITLE-ABS-KEY (stress* OR *stress) AND TITLE-ABS-KEY (\"AI\" OR \"Artificial Intelligence\") AND TITLE-ABS-KEY (work* OR organization*)..."。検索日 2025-03-07 を明記
  4. 情報源が十分か: No — 著者自身が単一データベース(Scopus)のみを限界として認めている。"No other databases were searched...no manual search of references was conducted"
  5. 批判的吟味の基準が適切か: No — 正式なrisk-of-biasツールは不使用。"We did not perform a formal risk of bias assessment for each study" strong/moderate/weakの非公式格付けのみ
  6. 吟味を2名以上が独立に行ったか: No — "one author performed the primary extraction for all studies"（単一抽出者）。第1段階スクリーニングも "reviewed against the inclusion criteria by the first author"（単一）。"No disagreements arose in the screening process among the authors as the criteria were clear-cut" とあるが、実質は単一レビュアーによる一次スクリーニング
  7. 抽出の誤りを減らす手順: Unclear — 抽出フォームのパイロットテストは実施("pilot tested on a few studies and refined")したが、独立2名照合の記載はない
  8. 統合方法の適切さ: Yes — 異質なデータ(定量/定性/概念研究混在)に対してnarrative synthesisを採用した判断は妥当と評価できる
  9. 出版バイアスの評価: 部分的 — 正式な統計的出版バイアス検定はないが、"we acknowledge potential biases in the literature, such as a publication bias favoring studies that report negative outcomes" と限界節で言及
  10. 提言がデータに支持されているか: Yes（記述された知見の範囲内）
  11. 今後の研究への指示が適切か: Yes — 縦断研究・介入研究・異文化比較等、具体的方向性を提示
  - 採択件数: 66（1,333件から）/ 検索日: 2025-03-07 / PRISMA流れ図: あり(Figure 1、"PRISMA 2020 flow diagram")
- 気づいた内部不整合: 本文冒頭Abstractでは "no formal risk-of-bias tools were applied" と明記される一方、2.5節では "we did appraise the strength of evidence for the claims of each empirical study. Each empirical study was categorized as providing strong, moderate, or weak evidence" とあり、非公式ながら一種の質評価を行っている旨が併記されている（矛盾ではなく非公式評価の存在を示すが、Abstractの言い切り方とはニュアンスが異なる）。出所: 本文 15行目付近（Abstract）と 199-201行目付近（2.5節）

## AF018
- アクセス範囲: 全文（curl で PDF 直接取得に成功。https://slejournal.springeropen.com/counter/pdf/10.1186/s40561-024-00316-7.pdf 、37頁、140,804文字。オープンアクセス CC BY 4.0）
- 書誌（一次で見えた値）:
  - 著者（全員）: Chunpeng Zhai, Santoso Wibowo, Lily D. Li（全員 School of Engineering & Technology/Tertiary Education Division, CQUniversity, Rockhampton, Australia）
  - 誌名: Smart Learning Environments
  - 巻・論文番号: (2024) 11:28
  - DOI: 10.1186/s40561-024-00316-7
  - ライセンス: CC BY 4.0（"© The Author(s) 2024. Open Access..."）
- 訂正・撤回・懸念表明: Crossref `update-to` null, `relation` 空。本文中にも訂正表示なし
- 研究デザイン: システマティックリテラチャーレビュー（Macdonald et al. (2023) の5段階法 + PRISMA + Kools et al. (1996) の次元分析法を併用）
- 対象・国・募集方法・収集時期: 対象は「生成モジュールを組み込んだAI対話システム」を扱う研究・教育文脈の論文（英語、2017-2023年発行）。データベース: ProQuest, IEEE Xplore, ScienceDirect, Web of Science
- N（各段、PRISMA flow より逐語の数値）:
  - Records identified from databases (n=70): ProQuest(n=18), IEEE(n=22), ScienceDirect(n=16), WoS(n=14)
  - スクリーニング前除去: 重複(n=7) + 自動化ツールでの不適格判定(n=8) + その他理由(n=2)
  - Records screened (n=55) → Records excluded (n=15)
  - Reports sought for retrieval (n=40) → Reports not retrieved (n=5)
  - Reports assessed for eligibility (n=35) → 除外: Not AI dialogue systems(6)／Not for research and education(5)／No generative modules(5)／Thesis writing(4)／Editorial(1) = 21件除外
  - **Studies included in review (n=9)** + Reports of included studies (n=5) = 本文で言及される「14 studies」「14 articles」相当
- AI の種類・利用文脈: AI対話システム（生成モジュール搭載の会話エージェント、研究・高等教育での利用）
- 疲労（または中心構成概念）の操作化: 全文中に fatigue / exhaustion / burnout の語は一切出現しない（grep で0件、全文読了済み）。中心構成概念は「over-reliance（過信）」とその帰結としての認知能力(critical thinking / decision-making / analytical thinking)の低下。疲労を測定した一次研究: **特定できず**（本文に fatigue/exhaustion/burnout への言及なし）
- その他の主要変数: 5つの倫理的問題（AI hallucination, algorithmic bias, plagiarism, privacy concerns, transparency concerns）
- 解析手法: 六段階のテーマ分析（thematic analysis → コーディング → サブ次元識別 → レビュー → 統合 → 分析）+ Kools et al. (1996) の3段階次元分析法
- 主要結果（逐語の一部）: Abstract より "Our findings indicate that over-reliance stemming from ethical issues of AI impacts cognitive abilities, as individuals increasingly favor fast and optimal solutions over slow ones constrained by practicality."（数値的効果量やp値は narrative review のため報告されていない = 記載なし）
- 著者自身が述べる限界（逐語）:
  - "One of the primary limitations of this study is its narrow scope, focusing predominantly on the negative effects of over-reliance on AI dialogue systems in research and education without equally examining the potential benefits"
  - "the study is based on a review of literature from only 14 databases"（★内部不整合。下記参照）
  - "The second limitation is that the study is primarily focused on higher education. It does not consider the cognitive developmental differences across various age groups"
- 倫理承認・同意（逐語）:
  - "Ethics approval and consent to participate: The author intends to submit a comprehensive application for ethical clearance concerning both the research instrument and the data collection process to the CQUniversity Human Research Ethics Committee (CQUHREC). Given that this project constitutes a systematic review, it does not require an ethics approval number."
  - "Consent for publication: The author(s) hereby grant the publisher the irrevocable, perpetual, and unrestricted right to publish..."
- 事前登録・データ/材料公開・資金・利益相反:
  - 事前登録: 記載なし（PROSPERO等の言及なし）
  - データ/材料公開: "Availability of data and materials: Not applicable."
  - 資金: "Funding: Funding was provided by Central Queensland University Australia."
  - COI（逐語）: "Competing interests: The author(s) of the manuscript...hereby declare that there are no non-competing interests related to this publication."（★二重否定の文言。下記内部不整合参照）
- 設計別チェック（D. システマティック／その他のレビュー）:
  1. 問いが明確か: Yes — 2つのRQ（"How does over-reliance...affect critical and analytical thinking abilities..." / "What are the primary ethical concerns causing over-reliance..."）を明記
  2. 組入れ基準が問いに適切か: Yes — Table 1 に inclusion/exclusion 基準を明記（4条件+3除外条件）
  3. 検索戦略が適切か（式・日付・情報源）: Unclear寄りYes — 4つのデータベース、期間2017-2023、検索語（"AI chatbot with a generative module"等）は本文に列挙されているが、正式なブーリアン検索式（AND/OR演算子つき）としては提示されていない
  4. 情報源が十分か: Unclear — 4データベースのみ。著者自身は「14 databases」と（誤記と思われるが）限界節で記載
  5. 批判的吟味の基準が適切か: No — 正式な risk-of-bias/critical appraisal ツール（JBI・CASP等）の使用は本文に記載なし。PRISMAの27項目チェックリストへの言及はあるがこれは報告ガイドラインであり研究の質評価ツールではない
  6. 吟味を2名以上が独立に行ったか: No/Unclear — "C.Zhai was responsible for the overall conceptualization, research, and writing"、共著者は "contributed to the proofreading and editing"／"contributed to the proofreading" のみと明記。実質的に単著者によるスクリーニング・抽出と読める。本文には "dual screening process in accordance with the PRISMA guidelines" との記述もあるが、これが2名の独立レビューを意味するか、2段階のスクリーニングプロセスを意味するかは本文から判別不能（Unclear）
  7. 抽出の誤りを減らす手順: 記載なし
  8. 統合方法の適切さ: Unclear — 六段階のテーマ分析法自体は提示されているが、質的レビューとしての厳密な適切性は本文だけでは判定困難
  9. 出版バイアスの評価: No — 言及なし
  10. 提言がデータに支持されているか: Unclear
  11. 今後の研究への指示が適切か: Yes — "Future studies should measure the cognitive impacts of using AI dialogue systems in educational settings."等の具体的提言あり
  - 採択件数: 9（+ Reports of included studies 5 = 本文表記の14）/ 検索日: 記載なし（期間2017-2023のみで検索実行日は不明）/ PRISMA流れ図: あり（Fig.1、Fig.2表記が本文中で交錯 — 下記内部不整合参照）
- 気づいた内部不整合（事実のみ、出所つき）:
  1. Limitations節: "the study is based on a review of literature from only 14 databases" — しかし本文の Methods 節で明記されているデータベースは ProQuest, IEEE Xplore, ScienceDirect, Web of Science の **4件のみ**。「14」は最終採択論文数（14 articles/studies）との混同とみられる。出所: 本文1448行目付近(Limitations) vs 349-351行目付近(Conducting a literature search)
  2. Competing interests節の文言: "hereby declare that there are no **non**-competing interests related to this publication."（二重否定。文意上は「competing interestsがない」と言いたいと解されるが、逐語では逆の意味になっている）。出所: 本文1500-1501行目付近
  3. PRISMA flow 図の数値とAbstract/本文の記述の対応: Abstract および本文には「14 articles/studies が最終分析対象」と繰り返し書かれる一方、Fig.1 (PRISMA flow) 内の "Included" 欄には "Studies included in review (n=9)" と "Reports of included studies (n=5)" が別項目として並記されている（9+5=14で数値自体は整合するが、「14」という一つの数字として本文で言及される箇所が多く、実際には9件+付随報告5件という内訳であることが分かりにくい）。出所: 本文392行目付近 vs 440-463行目付近(Fig.1テキスト)
  4. Ethics approval節の文言が未来形: "The author intends to submit a comprehensive application for ethical clearance..." — 出版済み論文の Declarations 節に「今後提出する意向である」という将来時制の記載がある。出所: 本文1478-1481行目付近

## AF019
- アクセス範囲: 抄録のみ（全文取得不可。使った URL: https://doi.org/10.1016/j.ijinfomgt.2025.102887 → https://linkinghub.elsevier.com/retrieve/pii/S0268401225000192（"Redirecting" のみで本文なし、ScienceDirect ブロック）／OpenAlex（abstract_inverted_index 空）／Semantic Scholar（abstract: null）／Unpaywall（`url_for_pdf: null`、`best_oa_location.url` は結局 doi.org へのリンクのみで実PDFなし）／機関リポジトリ https://scholar.lib.ntnu.edu.tw/en/publications/insights-from-the-job-demandsresources-model-ais-dual-impact-on-e/ で英語抄録全文を取得（WebFetch 経由）
- 書誌（一次で見えた値）:
  - 著者（全員）: Ya-Ting Chuang, Hua-Ling Chiang, An-Pan Lin（NTNU機関リポジトリ表記。Semantic Scholarでは3人目が "An-Min Lin" と表記され、AF017参考文献[68]では "A.-P. Lin" — 下記内部不整合参照）
  - 誌名: International Journal of Information Management
  - 巻・頁: Volume 83, Article 102887（OpenAlex biblio: volume=83, first_page=last_page=102887）
  - オンライン公開日: OpenAlex/Crossref/Unpaywall とも 2025-02-22。NTNUリポジトリページは "2025年8月" と表示（★下記内部不整合参照）
  - DOI: 10.1016/j.ijinfomgt.2025.102887
  - ライセンス: CC BY-NC-ND（Semantic Scholar/Unpaywall 一致、"HYBRID" OA ステータス）
- 訂正・撤回・懸念表明: Crossref `update-to` null, `relation` 空。訂正・撤回の兆候なし（書誌照合のみ）
- 研究デザイン: 3時点（three-wave）調査（縦断デザイン）。詳細な各波の実施間隔・調査手法（オンラインパネル等）は未確認（抄録に記載なし）
- 対象・国・募集方法・収集時期: 抄録より「AIと共に働く、多様な業種の、男女比が均衡した参加者」。国・募集方法（パネル会社等）・具体的収集時期は未確認
- N: 抄録に "600 gender-balanced participants" と明記。各波ごとの回収数・脱落率（attrition）は未確認（全文が必要）
- AI の種類・利用文脈: 職場でのAI利用全般（"working with AI across diverse industries"）。生成AIも独立変数として扱われている（"generative AI" を AI efficacy とは別の資源(resource)として測定）
- 疲労（または中心構成概念）の操作化: 構成概念名は "exhaustion"（燃え尽き/消耗）。JD-Rモデルにおいて engagement と並ぶ媒介変数(mediator)として位置づけられている。抄録の逐語: "with engagement and exhaustion as mediating factors" および "AI technostress increases exhaustion, exacerbates work–family conflict, and lowers job satisfaction"。★疲労(exhaustion)は明確に「AI technostress」に帰属する形で測定されている（抄録レベルで確認）。使用尺度名・項目数・出典・項目例は未確認（全文未取得のため）
- その他の主要変数: AI demands = AI technostress／AI resources = AI efficacy, generative AI／アウトカム = productivity, job satisfaction, work–family conflict／媒介変数 = engagement, exhaustion
- 解析手法: Bayesian SEM（構造方程式モデリング）
- 主要結果（逐語、抄録より）: "Bayesian SEM results indicate that both AI efficacy and generative AI positively impact productivity, with AI efficacy also enhancing engagement and job satisfaction. In contrast, AI technostress increases exhaustion, exacerbates work–family conflict, and lowers job satisfaction, even though it may still contribute to productivity."／"generative AI mitigates the negative effects of technostress, a benefit not observed for AI efficacy as measured in this study."（係数・CI・p値等の数値は抄録に含まれず、未確認）
- 著者自身が述べる限界: 未確認（全文未取得）
- 倫理承認・同意: 未確認
- 事前登録・データ/材料公開・資金・利益相反: 未確認
- 設計別チェック（A. 横断研究 — ただし本研究は3時点縦断調査であり、横断研究チェックリストの直接適用は不適切。参考までに全項目 Unclear とし「全文未取得」と明記）:
  1〜8: すべて Unclear（全文未取得のため）
- 気づいた内部不整合:
  1. 公開日: OpenAlex/Crossref/Unpaywall は一致して "2025-02-22"（Crossref `published`/`published-online`）だが、NTNU機関リポジトリのページ表示は「2025年8月」（WebFetch要約による）。出所: OpenAlex `af019_openalex.json` の `publication_date` フィールド vs NTNUリポジトリページ（WebFetch出力）
  2. 第3著者名の表記ゆれ: NTNUリポジトリ="An-Pan Lin"、Semantic Scholar="An-Min Lin"、AF017 (STPIS'25 レビュー) の参考文献[68]="A.-P. Lin"。3者で "An-Pan" と "An-Min" の不一致がある。出所: `af019_s2.json`（Semantic Scholar）の authors 配列 vs NTNUリポジトリページ vs `af017_fulltext.txt` 1104-1106行目付近

## AF020
- アクセス範囲: 全文（arXiv PDF を取得し pypdf でテキスト抽出。https://arxiv.org/pdf/2102.09692 、21頁、80,139文字。arXiv プレプリント版=CSCW発表版と同一と明記されている：DOI 10.1145/3449287, Proc. ACM Hum.-Comput. Interact. 5, CSCW1, Article 188 (April 2021)）
  - ⚠️注記: 取得したのは arXiv プレプリント版(v1, 2021-02-19投稿)。ACM 公式出版版とテキストが完全一致するかは未確認（通常はcamera-ready相当だが、倫理/資金記載など出版時に追加される節が本PDFには存在しない可能性がある）
- 書誌（一次で見えた値）:
  - 著者（全員）: Zana Buçinca (Harvard University), Maja Barbara Malaya (Lodz University of Technology), Krzysztof Z. Gajos (Harvard University)
  - 誌名: Proceedings of the ACM on Human-Computer Interaction
  - 巻・号・論文番号: Vol. 5, No. CSCW1, Article 188
  - 頁数: 21 pages
  - 発行日: April 2021
  - DOI: 10.1145/3449287
  - arXiv投稿日: 2021-02-19
- 訂正・撤回・懸念表明: Crossref `update-to` null, `relation` 空。訂正・撤回の兆候なし
- 研究デザイン: 実験（オンライン、Amazon Mechanical Turk）。混合計画（between-subject + within-subject、両因子とも "condition"）
- 対象・国・募集方法・収集時期: 米国在住成人限定、Amazon Mechanical Turk 経由で3バッチに分けて募集。収集時期は記載なし（未確認）
- N（募集・除外・解析）:
  - 募集: 260名（3バッチ）
  - 除外: プレート上にない食材を55%超の設問で選択した49名を除外（これらは課題正答率も0だったと記載）＋ 分析対象外の探索的条件のみに割り当てられた12名を除外
  - 解析対象: **199名**（うち191名が任意の人口統計調査に回答。Mage=37.09, SD=10.74。65.44%が男性と自己申告）
  - 報酬: 1人$2.50（時給換算約$10）、各バッチのトップパフォーマーに$3ボーナス
- AI の種類・利用文脈: シミュレートされたAI決定支援システム（食事画像から炭水化物源を検出し代替食材を提案するタスク）。9条件中6条件が本論文で報告（No AI / Explanation / Uncertainty / On demand / Update / Wait の6条件 + 本論文非報告の探索的3条件）
- 実験条件・N・主要アウトカム（過信・主観評価など）:
  - 条件: No AI（AIなし基準群）／Explanation（説明付きAI提案）／Uncertainty（AI確信度表示）／On demand（クリックでAI提案を表示）／Wait（処理待ち演出後に提案表示）／Update（初回判断後にAI提案を見て更新可能） — これら6条件（cognitive forcing functions群=Update/Wait/On demand相当の3種 vs simple explainable AI群=Explanation/Uncertainty の2種 vs No AI基準）
  - 客観的アウトカム: Overall performance／Carb source detection performance／Carb reduction／Flavor similarity／**Overreliance**（AIが誤った予測をした際にAIに同意した割合）／Human error（AI誤予測時の誤判断割合）
  - 主観的アウトカム（5件法リッカート、各1項目）: Preference（"I would like to use this system frequently."）／Trust（"I trust this AI's suggestions for optimal replacement."）／**Mental demand**（"I found this task difficult."）／System complexity（"The system was complex."）
  - 主要結果（逐語・数値、Table 3より）: Mental Demand の post-hoc: "{SXAI, CFF} < {no AI}" で Marginal Means (SE) = no AI 3.66(0.16), SXAI 2.86(0.12), CFF 2.84(0.11), "F(2,183.4) = 11.70, p ≪ .0001"。本文: "They found the no AI condition to be significantly more mentally demanding than cognitive forcing functions and simple explainable AI conditions."
  - Overreliance関連: "cognitive forcing significantly reduced overreliance compared to the simple explainable AI approaches"（Table 2相当の数値は本文中に F値・p値・効果量dで報告されているが今回は Mental Demand の表を優先的に転記。Overreliance側の具体数値は時間の都合で全数値の書き写しは省略——必要なら追加照合可）
- 疲労/負担に関する測定があるかどうか: **単項目の "Mental demand"（"I found this task difficult." 5件法リッカート、単一項目・各ブロック後に測定）が唯一の負担関連測定**。これは検証済みの疲労・workload尺度（NASA-TLX等）ではなく、単一項目の主観評価。fatigue/exhaustion/burnout という語、NASA-TLX、standardized workload scaleへの言及は本文に一切なし（grep で0件、全文読了済み＝「記載なし」）
- 著者自身が述べる限界（逐語）:
  - "A key limitation of our work is that it was conducted in the context of a single non-critical decision-making task. Additional work is needed to examine if the effects we observe generalize across domains and settings."
  - "Another limitation is that cognitive forcing functions improved the performance of the human+AI teams at the cost of reducing the perceived usability. Consequently, systems that employ cognitive forcing functions may find less adoption than those that use simple explainable AI techniques because users will resist using them."
- 倫理承認・同意: 本文3.4節に "Participants were first presented with a consent form and instructions." と記載（インフォームドコンセントの実施に言及）。ただし IRB/倫理審査委員会名や承認番号の明記は本文中に見当たらず（grep で "IRB" "institutional review" 該当なし＝記載なし。ACM出版版では別途Ethics節がある可能性があるが本PDFでは未確認）
- 事前登録・データ/材料公開・資金・利益相反: 本PDF中に Funding/Acknowledgments 節はあるが謝辞のみで資金情報の記載なし（逐語: "We thank Isaac Lage, Andrzej Romanowski, Ofra Amir, Zilin Ma, and Vineet Pandey for helpful suggestions and discussions."）。grant/NSF/funding等の語は grep で本文中に該当なし＝記載なし。事前登録(OSF等)・データ材料公開への言及も本文中に見当たらず（記載なし）
- 設計別チェック（C. ランダム化比較試験、条件へのランダム割付を伴う実験のため準用）:
  1. 真のランダム化: Yes — "participants were randomly shown a different condition in each block"（条件へのランダム割当が明記）
  2. 割付の隠蔽: Unclear（オンライン自動割当のため通常は問題にならないが、明記した記述はなし）
  3. ベースラインの群間類似: Yes寄り — 人口統計(年齢・性別・学歴)は全体でのみ報告され、条件別の比較は記載なし（Unclear寄りYes）
  4. 参加者の盲検: NA/Unclear — 条件の性質上（AIの提示方法が異なる）完全盲検は構造的に不可能。言及なし
  5. 介入実施者の盲検: NA（オンライン自動実験のため実施者介在なし）
  6. 評価者の盲検: NA（客観的アウトカムはシステムログから自動記録されるため評価者バイアスのリスクは低いと考えられるが明記はなし）
  7. 介入以外の扱いが同一: Yes — タスク構造(26問・2ブロック)は全条件で共通
  8. 追跡の完全性: Yes — 除外の内訳と理由（49名+12名）が明記されている
  9. 割付どおりの解析: Yes（除外後の199名で条件別に分析。ITT的な逸脱の記載はなし）
  10. 群間で同じ方法でアウトカム測定: Yes — 全条件で同一の質問セット・リッカート項目
  11. アウトカム測定の信頼性: Unclear — 主観指標は単一項目のリッカートで、信頼性係数（α等）の報告なし
  12. 統計解析の適切さ: Yes — mixed-effects model（参加者をランダム効果、条件を固定効果）を用いた理由を明記し、多重測定の非独立性を考慮
  13. 試験デザインの適切さ: Yes — 混合計画の設計意図が明記されている
- 気づいた内部不整合: 見当たらず（全文読了の範囲内）

---
時間配分の記録: 全6件について全文または抄録レベルまで到達。AF015のみ書誌レベルに留まった（Springerの login-wall のため）。締切（起動から25分）の直前まで作業したため、AF019 の全文再照合・AF017の burnout関連一次研究の遡及検証（各研究の実際の尺度確認）等、追加の深掘りは行っていない。
