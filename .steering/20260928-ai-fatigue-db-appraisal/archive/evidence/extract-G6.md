# 抽出結果 G6（AF025〜AF033）

共通メモ: 全 9 件について Crossref `update-to` / `relation` を確認したが、いずれも `null` / `{}` で、Crossref 経由では訂正・撤回・懸念表明の通知は見つからなかった（各レコード内でも個別に明記）。

---

## AF025
- アクセス範囲: 抄録のみ（OpenAlex 経由で復元した abstract_inverted_index）。使った URL: https://api.openalex.org/works/doi:10.1080/10494820.2019.1674887 、 https://api.crossref.org/works/10.1080/10494820.2019.1674887 。tandfonline 本文は WebFetch で HTTP 402 Payment Required、ERIC (https://eric.ed.gov/?id=EJ1345149) は接続失敗（Remote end closed connection）。未着手ではないが本文未取得。
- 書誌（一次で見えた値）: 著者（全員, Crossref）= Yu-Yin Wang, Yi-Shun Wang / 誌名 = Interactive Learning Environments / 巻 30 / 号 4 / 頁 619-634 / issued(Crossref) 2019-10-14 / published-online(Crossref date-parts) 2019-10-14 / published-print(Crossref) 2022-04-03 / DOI 10.1080/10494820.2019.1674887。★ input-G6.md には巻号年の指示があったが、Crossref の `published-online` フィールド自体は空(null)で、`issued`/`created` が 2019-10-14。オンライン公開年と巻号(印刷)年が異なる（2019 vs 2022）ことを確認: `issued: [[2019,10,14]]` / `published-print: [[2022,4,3]]`。
- 訂正・撤回・懸念表明: Crossref `update-to`=null, `relation`={}。出版社ページ（tandfonline）は本文にアクセスできず Correction/Retraction バナーの有無は確認できず（未確認）。
- 研究デザイン: 抄録の記述から尺度開発・検証研究（横断・多段階のバリデーション）。詳細は未確認（全文未取得）。
- 対象・国・募集方法・収集時期: 記載なし（抄録に明記なし）。未確認。
- N（募集・除外・解析の各段）: 抄録に "a sample of 301 respondents" とのみ。段階別の内訳は未確認。
- AI の種類・利用文脈: 抄録は AI 全般（generic AI anxiety）を対象。特定の AI 種類の記載なし。
- 疲労（または中心構成概念）の操作化: 構成概念名は "AI anxiety (AIA)"。尺度名 "AI Anxiety Scale (AIAS)"。項目数・因子数は抄録に数値なし（未確認）。逐語（抄録）: "no AI anxiety scale (AIAS) has been developed... this paper introduces and defines the construct of AIA, develops a generic AIAS". 疲労への言及なし（AIA ≠ fatigue）。「AI の利用・監督」への帰属は抄録からは Unclear。
- その他の主要変数: 抄録に "motivated learning behavior" が予測対象として言及。詳細未確認。
- 解析手法: 抄録に "reliability, criterion-related validity, content validity, discriminant validity, convergent validity, and nomological validity" を検討したと記載。具体的検定法（EFA/CFA 等）は未確認。
- 主要結果（報告された数値）: 抄録に数値なし（記述のみ）。未確認。
- 著者自身が述べる限界: 未確認（全文未取得）。
- 倫理承認・同意: 未確認（全文未取得）。
- 事前登録・データ/材料公開・資金・利益相反: 未確認（全文未取得）。
- 設計別チェック E（尺度開発・検証、簡略）:
  - 尺度名: AI Anxiety Scale (AIAS)
  - 項目数: 記載なし（未確認、抄録に数値なし）
  - 因子数: 記載なし（未確認）
  - 標本と N: N=301（抄録に明記の全体標本数のみ。段階別・下位標本は未確認）
  - 信頼性/妥当性の主な報告値: 抄録は種類の列挙のみ（信頼性・基準関連妥当性・内容妥当性・弁別妥当性・収束妥当性・法則的妥当性）で数値なし
  - 対象集団: 記載なし（未確認）
- 気づいた内部不整合: Crossref の `issued`（オンライン公開扱い, 2019-10-14）と `published-print`（2022-04-03、巻30号4）の間に約2年半のギャップがある。抄録先行公開から巻号確定までの一般的な遅延と考えられるが、事実として記録。

---

## AF026
- アクセス範囲: 全文（PDF, 10ページ, Stanford VHIL 著者版）。使った URL: https://vhil.stanford.edu/sites/g/files/sbiybj29011/files/media/file/fauville-zef-chbr_2021.pdf （OpenAlex `best_oa_location` は ScienceDirect gold OA も指す）。
- 書誌（一次で見えた値）: 著者（全員, Crossref）= G. Fauville, M. Luo, A.C.M. Queiroz, J.N. Bailenson, J. Hancock / 誌名 Computers in Human Behavior Reports / 巻4 / 号 なし(null) / 頁(論文番号) 100119 / issued 2021-08 / created 2021-07-06 / DOI 10.1016/j.chbr.2021.100119。
- 訂正・撤回・懸念表明: Crossref `update-to`=null, `relation`={}。本文中に訂正表示なし（確認範囲内）。
- 研究デザイン: 横断的な尺度開発・検証（複数段階: インタビュー→サーベイ→EFA→CFA→妥当性検証）。
- 対象・国・募集方法・収集時期: Study 3(サーベイ): Amazon Mechanical Turk で募集した N=395。Study 4: Lucid 経由 + 学生, N=130（学生73名＋Lucid経由57名）。Study 5（大規模妥当性検証）: 2021年2月22日〜26日にオンラインで convenience sample を募集, N=2724。米国中心と推定されるが国の明記は確認範囲内で見当たらず（未確認）。
- N（募集・除外・解析の各段。単位=人）: フェーズIII(尺度作成) N=395（MTurk）／フェーズIV N=130（学生73＋Lucid57）／妥当性検証フェーズ N=2724（"Participants who failed the two attention check questions were removed" — 除外後の最終解析Nは本文表記のまま2724人として記述されており、除外前後の内訳数値は本文から特定できず未確認）。
- AI の種類・利用文脈: 該当なし（Zoom/ビデオ会議ツールの利用文脈。AI固有の話題ではない）。
- 疲労（または中心構成概念）の操作化: 構成概念名 "Zoom fatigue" を General/Social/Emotional/Visual/Motivational Fatigue の5下位尺度で測定。尺度名 Zoom Exhaustion & Fatigue (ZEF) Scale。項目数 15項目(5因子×3項目)。出典: 本論文自体が原著。項目例（逐語、Table 3 由来の因子ラベルのみ確認、個別項目文の逐語は未確認）。★ 疲労が「ツール利用」に帰属して測られているか: 逐語 "revealing five dimensions of fatigue: general, social, emotional, visual, and motivational fatigue" — Zoom/ビデオ会議の利用文脈に特化した尺度であり、AIへの帰属ではない。
- その他の主要変数: 動画会議の頻度・時間・バースト性 (frequency, duration, burstiness)、ビデオ会議への態度（3項目 Likert）。
- 解析手法: 探索的因子分析→確認的因子分析（second-order CFA）。適合度指標あり。
- 主要結果（報告された数値、逐語）: "the five-factor model fits the data well: CFI = 0.944, TLI = 0.930, RMSEA = 0.086 and SRMR = 0.060, X2 (85) = 116.21." および "Cronbach's alphas were above 0.8 for each of the five constructs (general fatigue: ɑ = 0.89, visual fatigue: ɑ = 0.88, social fatigue: ɑ = 0.84, motivational fatigue: ɑ = 0.83, emotional fatigue: ɑ = 0.83)" 、総合スコアは "ZEF Score... showed high reliability (ɑ = 0.95)"。
- 著者自身が述べる限界: 未確認（該当箇所を時間内に特定できず、途中）。
- 倫理承認・同意: 本文方法節の逐語 "university Administrative Panel on Human Subjects in Research (IRB-57116)"（インタビュー段階のIRB番号）。妥当性検証フェーズは "individuals could elect to participate in our study after providing informed consent." 末尾宣言欄は未確認（時間内未到達）。
- 事前登録・データ/材料公開・資金・利益相反: 未確認（時間内未到達）。
- 設計別チェック E（尺度開発・検証、簡略）:
  - 尺度名: Zoom Exhaustion & Fatigue (ZEF) Scale
  - 項目数: 15項目（49項目から因子分析で絞り込み）
  - 因子数: 5因子（general, social, emotional, visual, motivational fatigue）
  - 標本と N: 開発時395人(MTurk, CFA)／追加検証130人(学生+Lucid)／大規模妥当性検証2724人(convenience sample, オンライン募集)
  - 信頼性/妥当性の主な報告値: 各下位尺度 α=0.83〜0.89、総合スコア α=0.95、CFA適合度 CFI=0.944/TLI=0.930/RMSEA=0.086/SRMR=0.060
  - 対象集団: 一般成人のビデオ会議利用者（学生含む convenience sample、MTurk/Lucid/SNS経由）
- 気づいた内部不整合: 特になし（確認した範囲内）。

---

## AF027
- アクセス範囲: 抄録のみ（OpenAlex 経由）。使った URL: https://api.openalex.org/works/doi:10.1287/isre.1070.0165 。本文 pubsonline.informs.org は WebFetch で HTTP 403 Forbidden。OpenAlex open_access.oa_status = "closed"（OAコピーなし）。
- 書誌（一次で見えた値）: 著者（全員, Crossref）= T. S. Ragu-Nathan, Monideepa Tarafdar, Bhanu S. Ragu-Nathan, Qiang Tu / 誌名 Information Systems Research / 巻19 / 号4 / 頁417-433 / issued/published-print 2008-12 / DOI 10.1287/isre.1070.0165。
- 訂正・撤回・懸念表明: Crossref `update-to`=null, `relation`={}。出版社ページは本文未取得のためバナー表示は未確認。
- 研究デザイン: 横断的サーベイによる尺度開発・構造方程式モデリング（SEM）検証。
- 対象・国・募集方法・収集時期: 抄録に "608 end users of ICTs from multiple organizations" とのみ。国・収集時期は記載なし（未確認）。
- N（募集・除外・解析の各段）: N=608（抄録に明記の解析対象のみ。募集・除外段階は未確認）。
- AI の種類・利用文脈: 該当なし（ICT全般に対するテクノストレス。AI固有ではない）。
- 疲労（または中心構成概念）の操作化: 構成概念名 "technostress"。下位構成として technostress creators（ストレス要因）／technostress inhibitors（組織的抑制要因）の二次因子モデル。項目数・出典は抄録に記載なし（未確認）。★「AIの利用・監督」への帰属ではなく、ICT利用一般に帰属。逐語: "stress experienced by end users of Information and Communication Technologies (ICTs)"。
- その他の主要変数: job satisfaction, organizational commitment, continuance commitment, intention to stay, age, gender, education, computer confidence。
- 解析手法: 構造方程式モデリング（SEM）。
- 主要結果（報告された数値、逐語）: 抄録に数値なし。逐語 "technostress creators decrease job satisfaction, leading to decreased organizational and continuance commitment, while Technostress inhibitors increase job satisfaction and organizational and continuance commitment."
- 著者自身が述べる限界: 未確認（全文未取得）。
- 倫理承認・同意: 未確認（全文未取得）。
- 事前登録・データ/材料公開・資金・利益相反: 未確認（全文未取得）。
- 設計別チェック E: 全文未取得のため主要数値は記載なし。尺度名は "Technostress Creators" / "Technostress Inhibitors" 尺度（本論文が原著）。項目数・因子数・信頼性係数は未確認。対象集団: 複数組織のICTエンドユーザー(N=608)。
- 気づいた内部不整合: 特になし（確認できた範囲内。全文未取得のため限定的）。

---

## AF028
- アクセス範囲: 抄録のみ（PubMed/NCBI eutils）。使った URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=12670612&rettype=abstract&retmode=text 。ScienceDirect本文・Tilburg大学リポジトリPDF (https://research.tilburguniversity.edu/files/510406/psychometric.pdf) はいずれも HTTP 403 Forbidden で取得不可。
- 書誌（一次で見えた値）: 著者（全員, PubMed/Crossref）= Helen J. Michielsen, Jolanda De Vries, Guus L. Van Heck / 誌名 Journal of Psychosomatic Research / 巻54 / 号4 / 頁345-352 / issued/published-print 2003-04 / DOI 10.1016/S0022-3999(02)00392-6。著者所属（逐語）: "Department of Clinical Health Psychology, Tilburg University, PO Box 90153, The Netherlands."
- 訂正・撤回・懸念表明: Crossref `update-to`=null, `relation`={}。本文未取得のため出版社ページのバナー表示は未確認。
- 研究デザイン: 縦断研究の一部としての横断的尺度検証（"As part of a longitudinal study"）。
- 対象・国・募集方法・収集時期: 逐語 "the respondents, all workers with at least 20 working hours per week, completed the FAS..." オランダ（著者所属Tilburg大学から推定、本文に明記の国名は未確認）。収集時期の記載なし（未確認）。
- N（募集・除外・解析の各段）: 抄録に具体的なN数値の記載なし（未確認）。
- AI の種類・利用文脈: 該当なし。
- 疲労（または中心構成概念）の操作化: 構成概念名 "fatigue"。尺度名 Fatigue Assessment Scale (FAS)、項目数10項目（逐語 "a new 10-item fatigue measure, the Fatigue Assessment Scale (FAS)"）。因子構造は抄録に "a clear one-factor solution" と一因子であることが示唆。★ AIの利用・監督への帰属ではなく、労働者の一般的疲労を測定する尺度（"all workers with at least 20 working hours per week"）。
- その他の主要変数: 他の疲労尺度4種、抑うつ質問紙、情緒安定性尺度。ジェンダーバイアス分析（DIF）。
- 解析手法: 内的一貫性分析、相関分析、因子分析（複数疲労尺度の合同因子分析）、項目バイアス(gender)分析。
- 主要結果（報告された数値、逐語）: "The FAS had a high internal consistency."／"8 out of the 10 FAS items were unbiased concerning gender; two had a uniform bias."　具体的なα係数の数値は抄録に記載なし（未確認、全文アクセス不可のため）。
- 著者自身が述べる限界: 未確認（全文未取得）。
- 倫理承認・同意: 未確認（全文未取得）。
- 事前登録・データ/材料公開・資金・利益相反: 未確認（全文未取得。2003年発表のため事前登録は制度的に存在しない可能性が高いが、これは推測であり明記していない）。
- 設計別チェック E（尺度開発・検証、簡略）:
  - 尺度名: Fatigue Assessment Scale (FAS)
  - 項目数: 10項目
  - 因子数: 一因子（"a clear one-factor solution"、抄録の記述）
  - 標本と N: 記載なし（未確認、抄録に数値なし）
  - 信頼性/妥当性の主な報告値: 「高い内的一貫性」「良好な収束的・弁別的妥当性」との定性的記述のみ、数値は未確認
  - 対象集団: 週20時間以上勤務する労働者（"all workers with at least 20 working hours per week"）
- 気づいた内部不整合: 特になし（抄録レベルのため限定的）。

---

## AF029
- アクセス範囲: 全文（PDF, 15ページ, Springer著者版）。使った URL: https://link.springer.com/content/pdf/10.3758/s13428-013-0334-1.pdf 。
- 書誌（一次で見えた値）: 著者（全員, Crossref）= Jimmie Leppink, Fred Paas, Cees P. M. Van der Vleuten, Tamara Van Gog, Jeroen J. G. Van Merriënboer / 誌名 Behavior Research Methods / 巻45 / 号4 / 頁1058-1072 / issued/published-online 2013-04-10 / published-print 2013-12 / DOI 10.3758/s13428-013-0334-1。
- 訂正・撤回・懸念表明: Crossref `update-to`=null, `relation`={}。本文中に訂正表示なし。
- 研究デザイン: 尺度開発（PCA→CFA）の複数スタディ構成 + ランダム化実験による追加検証。
- 対象・国・募集方法・収集時期: Study I: "a lecture in statistics for PhD students... in psychology and health sciences" (n=56)。Study II: "lectures in statistics for different cohorts of bachelor students in the social and health sciences" (ns=171, 136, 148)。Study III(実験): "a randomized experiment with university freshmen in the health sciences" (n=58)。国名の明記は未確認（大学名等の記載なし、欧州の大学と推測されるが明記は無いため記載しない）。
- N（募集・除外・解析の各段。単位=人）: Study I n=56（PCA）／Study II（CFA）ns=171, 136, 148（3コホート）／Study III（実験, ランダム化）n=58、うち "unfamiliar format (formula; n=29)" と "familiar format (textual explanation; n=29)" に2群分割。
- AI の種類・利用文脈: 該当なし（認知負荷理論・統計学講義の文脈、AIとは無関係）。
- 疲労（または中心構成概念）の操作化: 構成概念名 "cognitive load"（intrinsic load, extraneous load, germane load の3種）。尺度名なし（本論文が原著の10項目尺度）。項目数10項目、3因子（IL=Items1-3, EL=Items4-6, GL=Items7-10）。★ 疲労ではなく認知負荷であり、AIの利用・監督への帰属ではなく、あらゆる学習指導形式に対する一般的測定尺度。
- その他の主要変数: 記載なし特筆（比較対象研究として位置づけ）。
- 解析手法: 主成分分析(PCA)→確認的因子分析(CFA)→信頼性分析(Cronbach's α)。
- 主要結果（報告された数値、逐語）: "Cronbach's alpha values of .81 for Items 1, 2, and 3 (expected to measure IL); .75 for Items 4, 5, and 6 (expected to measure EL); and .82 for Items 7, 8, 9, and 10 (expected to measure GL)."
- 著者自身が述べる限界: 未確認（時間内未到達、途中）。
- 倫理承認・同意: 未確認（時間内未到達）。
- 事前登録・データ/材料公開・資金・利益相反: 未確認（時間内未到達）。
- 設計別チェック E（尺度開発・検証、簡略）:
  - 尺度名: 10-item cognitive load instrument（Leppink et al.、固有の尺度名なし）
  - 項目数: 10項目
  - 因子数: 3因子（IL 3項目・EL 3項目・GL 4項目）
  - 標本と N: Study I n=56（PhD学生, PCA）／Study II ns=171,136,148（学士課程, CFA）／Study III n=58（新入生, ランダム化実験）
  - 信頼性/妥当性の主な報告値: α=.81(IL), .75(EL), .82(GL)。CFAによる3因子構造の確認、ランダム化実験による further support。
  - 対象集団: 大学生（心理学・保健科学系, PhD〜学部新入生）
- 気づいた内部不整合: 特になし（確認できた範囲内）。

---

## AF030
- アクセス範囲: 全文（PDF, 29ページ, White Rose Research Online 著者受理版 "Version: Accepted Version"）。使った URL: https://eprints.whiterose.ac.uk/id/eprint/136633/1/PRISMA_ScR_Manuscript_July6th_clean_1_.pdf 。
- 書誌（一次で見えた値）: 著者（全員, Crossref）= Andrea C. Tricco, Erin Lillie, Wasifa Zarin, Kelly K. O'Brien, Heather Colquhoun, Danielle Levac, David Moher, Micah D.J. Peters, Tanya Horsley, Laura Weeks, Susanne Hempel, Elie A. Akl, Christine Chang, Jessie McGowan, Lesley Stewart, Lisa Hartling, Adrian Aldcroft, Michael G. Wilson, Chantelle Garritty, Simon Lewin, Christina M. Godfrey, Marilyn T. Macdonald, Etienne V. Langlois, Karla Soares-Weiser, Jo Moriarty, Tammy Clifford, Özge Tunçalp, Sharon E. Straus / 誌名 Annals of Internal Medicine / 巻169 / 号7 / 頁467-473 / issued/published-print 2018-10-02 / DOI 10.7326/M18-0850。
- 訂正・撤回・懸念表明: Crossref `update-to`=null, `relation`={}。本文（著者受理版）に訂正表示なし。
- 何を定めたか（要約）: PRISMA (Systematic reviews) の scoping review 拡張版チェックリストと解説。20コア項目＋2つの任意項目からなるチェックリスト。逐語: "The final checklist, with 20 items plus two optional items, is presented in Table 1."
- 開発方法の主要数値: 修正Delphi法（85%合意基準）。逐語 "An 85% consensus rule was selected a priori to signify agreement amongst the expert" 。ラウンド3には27名招待、24名が完了（逐語 "A total of 27 people were invited to participate in round 3 of the Delphi... Overall, 24 out of 27 completed"）。
- 資金: 逐語 "of Health Research (CIHR) [grant # KRS 144046]. This funding body had no role in"（Canadian Institutes of Health Research）。
- 版・後継版の有無: 本論文自体が2018年の初版。★ 別途 AF033（2026年 J Clin Epidemiol）が改訂に向けた scoping review であることを確認済み（下記AF033参照）。2026-09-28時点で PRISMA-ScR 2.0 等の正式改訂版は未公表であることを PRISMA公式サイト・EQUATOR Networkで確認（下記参照）。
- 設計別チェック: 不要（方法論文献のため対象外、brief指示通り）。
- 気づいた内部不整合: 特になし。

【付帯確認: PRISMA-ScR 正式改訂版の有無（2026-09-28時点）】
- EQUATOR Network (https://www.equator-network.org/reporting-guidelines/prisma-scr/): WebFetch要約によれば「PRISMA-ScR 2.0などの改訂版についての記載はない」。原論文は2018年発表、ページの最終更新日は2025年2月6日と表示。改訂版・準備中の言及は無し。
- PRISMA公式サイト (https://www.prisma-statement.org/scoping): WebFetch要約によれば「The PRISMA extension for scoping reviews (PRISMA-ScR) was published in 2018」とのみ記載され、改訂版の言及なし。
- ★ いずれも WebFetch（AIによる要約経由）での確認であり、私自身がページ全文を直接読んだわけではない点に注意（要約の忠実性は未検証）。ただし AF033 本文（一次資料、直接全文読了）は「PRISMA-ScRの更新はまだ完了しておらず、AF033のScRはその更新を情報提供する段階」と明記しており（後述）、独立に整合する。

---

## AF031
- アクセス範囲: 抄録のみ（Europe PMC REST）。使った URL: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.11124/JBIES-20-00167&format=json&resultType=core 。無料全文リンクとして Europe PMC が "https://journals.lww.com/jbisrir/Fulltext/2020/10000/..." を提示したが WebFetch で HTTP 403 Forbidden。リポジトリ https://rgu-repository.worktribe.com/output/979072 も HTTP 403 Forbidden で本文取得不可。
- 書誌（一次で見えた値）: 著者（全員, Crossref）= Micah D.J. Peters, Casey Marnie, Andrea C. Tricco, Danielle Pollock, Zachary Munn, Lyndsay Alexander, Patricia McInerney, Christina M. Godfrey, Hanan Khalil / 誌名 JBI Evidence Synthesis / 巻18 / 号10 / 頁2119-2126 / issued 2020-09-22 / published-online(Crossref) 2020-10 / DOI 10.11124/JBIES-20-00167。
- 訂正・撤回・懸念表明: Crossref `update-to`=null, `relation`={}。本文未取得のためページ上のバナー表示は未確認。
- 何を定めたか（要約、抄録より）: JBI scoping review 方法論ガイダンスの更新（2014年初版→2017年軽微更新→2020年最新更新）。PRISMA-ScRとの整合を確保。逐語: "In 2014, the JBI Scoping Review Methodology Group developed guidance for scoping reviews that received minor updates in 2017 and was most recently updated in 2020."／"Furthermore, it is aligned with the PRISMA-ScR to ensure consistent reporting."
- 主要数値: 抄録に開発期間の記載あり: "Between 2015 and 2020, the JBI Scoping Review Methodology Group expanded its membership..."。項目数など具体的なチェックリスト数値の記載は抄録になし（未確認、全文未取得）。
- 版・後継版の有無: JBI Manual for Evidence Synthesis に掲載され、2020年にJBI International Scientific Committeeが承認（逐語 "The updated chapter was endorsed by JBI's International Scientific Committee in 2020."）。★ AF033本文の逐語（後述）によれば「the JBI guide to ScRs is also currently in the process of being updated (personal communication with Pollock)」とあり、2026年時点でさらなる改訂が進行中との言及がある（AF033側の一次情報）。
- 設計別チェック: 不要（方法論文献のため対象外）。
- 気づいた内部不整合: 特になし（抄録レベルのため限定的）。

---

## AF032
- アクセス範囲: 全文（PDF, 11ページ, Springer, オープンアクセス "© The Author(s) 2018. This article is an open access publication"）。使った URL: https://link.springer.com/content/pdf/10.1007%2Fs11136-018-1798-3.pdf 。
- 書誌（一次で見えた値）: 著者（全員, Crossref）= C. A. C. Prinsen, L. B. Mokkink, L. M. Bouter, J. Alonso, D. L. Patrick, H. C. W. de Vet, C. B. Terwee / 誌名 Quality of Life Research / 巻27 / 号5 / 頁1147-1157 / issued/published-online 2018-02-12 / published-print 2018-05 / DOI 10.1007/s11136-018-1798-3。
- 訂正・撤回・懸念表明: Crossref `update-to`=null, `relation`={}。本文に訂正表示なし。
- 何を定めたか（要約）: PROM（patient-reported outcome measures）の測定特性に関する系統的レビューを行うための10ステップの手順を提案。逐語: "A consecutive ten-step procedure for conducting a systematic review of PROMs is proposed. Steps 1–4 concern preparing and performing the literature search, and selecting relevant studies. Steps 5–8 concern the evaluation of the quality of the eligible studies, the measurement …"
- 主要数値: 10ステップ（Fig. 1「Ten steps for conducting a systematic review of PROMs」）。COSMIN Risk of Bias checklist と修正GRADEアプローチを用いる。
- 資金: 逐語 "Funding CP has received funding from the European Union's Seventh"（文が途中で改頁により切れている。全文中に続きの記載があるはずだが時間内に該当箇所を追えず、詳細は途中）。
- 版・後継版の有無: 本論文が2018年のCOSMINガイドライン本体。後継版・改訂版の言及は本文中に確認できず（未確認、探索範囲内）。
- 設計別チェック: 不要（方法論文献のため対象外）。
- 気づいた内部不整合: 特になし。

---

## AF033
- アクセス範囲: 全文（PDF, 15ページ, Amsterdam UMC機関リポジトリ経由）。使った URL: https://pure.amsterdamumc.nl/ws/files/217632679/Updating-the-prisma-reporting-guideline-for-scoping-reviews.pdf 。
- 書誌（一次で見えた値）: 著者（全員, Crossref, 37名）= Andrea C. Tricco, Emily Robinson, Sharon E. Straus, Heather Colquhoun, Christina M. Godfrey, David Moher, Zachary Munn, Danielle Pollock, Sherrie Logan, Ellen B.M. Elsman, Sabira Hasanoff, Yonda Lai, James McMahon, Jasmeen Dourka, Dipika Neupane, Hanan Khalil, Micah D.J. Peters, Lyndsay Alexander, Romy M. Jia, Ashrita Saran, Catrin Evans, Dawid Pieper, Érica Brandão de Moraes, Fiona Campbell, Lisa Hartling, Michael G. Wilson, Vivian Welch, Tanya Horsley, Chantelle Garritty, Laura Weeks, Adrian Aldcroft, Etienne V. Langlois, Jessie McGowan, Adrienne Stevens, Brian Hutton, Martin Offringa, Areti Angeliki Veroniki / 誌名 Journal of Clinical Epidemiology / 巻196 / 号 なし(null) / 頁(論文番号) 112314 / issued/published-print 2026-08 / created(Crossref) 2026-05-09 / DOI 10.1016/j.jclinepi.2026.112314。本文表記: "Accepted 1 May 2026; Published online 8 May 2026"。
- 訂正・撤回・懸念表明: Crossref `update-to`=null, `relation`={}。本文に訂正表示なし。
- 何を定めたか（要約）: PRISMA-ScR（2018）の改訂に向けた scoping review。新しい報告項目候補を特定し、今後のDelphi調査でPRISMA-ScR更新に反映する位置づけ。逐語: "this ScR underpins the update by identifying potential new reporting items for consideration"。
- 主要数値（構造化抄録, Results節, 逐語）: "Of the 8265 records screened, 43 unique documents (13 overviews of ScRs and 30 guidance documents) were included and extracted. Thirty-seven potential reporting items for ScRs were identified."
- ★★ 採択資料数の表記の食い違い（構造化抄録 vs Plain Language Summary, 逐語）:
  - 構造化抄録(Results): "Of the 8265 records screened, 43 unique documents (13 overviews of ScRs and 30 guidance documents) were included and extracted."
  - Plain Language Summary: "They found 47 research papers that suggested 37 new reporting items."
  - → 採択件数が **43（構造化抄録）vs 47（平易な要約）** で異なる。新規報告項目候補数「37」は両節で一致（抄録: "Thirty-seven potential reporting items"／平易要約: "suggested 37 new reporting items"）。43と47の差の理由（丸め・誤記・異なる集計単位か）は本文中に説明を見つけられず、事実として記録するのみ（判定はしない）。
- 事前登録: 逐語 "The protocol for this review was published and registered with the Open Science Framework and in a peer-reviewed journal."／"Study registration: Open Science Framework: https://osf.io/mta4p"。
- 資金: 逐語 "Funding: Funding for this research was provided by the Canadian Insti-"（改頁で切れており全文は時間内に追えず、Canadian Institutes of Health Research と推測されるが逐語確定は途中）。
- 著者自身が述べる限界（逐語、抜粋）: "This review also had some limitations, including the potential for missed studies... A highly experienced team conducted data extraction with one extractor and one verifier, rather than in duplicate. Our database searches, conducted more than 20 months ago, were …"
- PRISMA-ScR改訂の進行状況（逐語, Introduction）: "the JBI guide to ScRs is also currently in the process of being updated (personal communication with Pollock)."／本論文はDelphi調査に先立つ scoping review の段階であり、"PRISMA-ScR 2.0" 等の正式版が本論文時点（2026年）で存在するとは書かれていない。
- 設計別チェック: 不要（方法論文献/scoping reviewだが、brief指示によりG6は簡略F扱い）。ただし D（システマティック/その他レビュー）に近い性質のため参考までに: 検索日・情報源は報告あり（MEDLINE, Embase, Cochrane Methodology Register + gray literature）。PRISMA準拠のフロー図の有無は本文に "Fig 2" として記載を確認（"8265 titles and abstracts were screened (Fig 2)"）。
- 気づいた内部不整合: 上記の 43 vs 47 の採択件数の食い違い（★最重要）。

---

## 作業状況サマリ
- 全9レコード完了（AF025〜AF033）。ただし AF025/AF027/AF028/AF031 は抄録レベル止まり（本文はペイウォール/403で取得不可）。AF026/AF029/AF030/AF032/AF033 は全文取得・読了。
- AF032 の資金節・AF033 の資金節はページ境界で文が切れており、続きを時間内に追いきれず「途中」。
- AF026 の「著者自身が述べる限界」「事前登録・資金・利益相反」は時間内未到達（該当節を特定できず）で「未確認」扱い。
